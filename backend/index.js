const { spawn } = require("node:child_process");
const path = require("node:path");
const crypto = require("node:crypto");
const fs = require("node:fs/promises");

const express = require("express");
const multer = require("multer");

const {
    ejecutarExtraccionPDF
} = require("./ejecutar_extraccion_pdf.js");

const app = express();
const PORT = process.env.PORT || 3000;

// Carpeta independiente para los PDF cargados por usuarios.
const carpetaDocumentosSubidos = (
    process.env.NODE_ENV === "test" &&
    process.env.DIRECTORIO_PDF_PRUEBAS
)
    ? path.resolve(process.env.DIRECTORIO_PDF_PRUEBAS)
    : path.resolve(
        __dirname,
        "../motor_documental/documentos_subidos"
    );

// Almacenamiento independiente para los PDF cargados.
const almacenamientoPDF = multer.diskStorage({
    destination: (req, archivo, callback) => {
        fs.mkdir(carpetaDocumentosSubidos, {
            recursive: true,
            mode: 0o700
        })
            .then(() => fs.chmod(carpetaDocumentosSubidos, 0o700))
            .then(() => callback(null, carpetaDocumentosSubidos))
            .catch(error => callback(error));
    },
    filename: (req, archivo, callback) => {
        callback(null, `${crypto.randomUUID()}.pdf`);
    }
});

const LIMITE_PDF_BYTES = 10 * 1024 * 1024;

// Rutas para ejecutar el validador PDF con el entorno virtual.
const pythonValidadorPDF = path.resolve(
    __dirname,
    "../.venv/bin/python"
);

const scriptValidadorPDF = path.resolve(
    __dirname,
    "validar_pdf.py"
);

// Tiempo máximo permitido para validar un documento PDF.
const TIEMPO_MAXIMO_VALIDACION_PDF_MS = 15000;

// Tamaño máximo permitido para la salida del validador Python.
const LIMITE_SALIDA_VALIDADOR_PDF_BYTES = 4096;


// Configuración inicial para recibir un PDF con tamaño limitado.
const cargarPDF = multer({
    storage: almacenamientoPDF,
    limits: {
        fileSize: LIMITE_PDF_BYTES,
        files: 1
    },
    fileFilter: (req, archivo, callback) => {
        const extensionValida =
            path.extname(archivo.originalname).toLowerCase() === ".pdf";

        const tipoValido = archivo.mimetype === "application/pdf";

        if (!extensionValida || !tipoValido) {
            return callback(new Error("TIPO_PDF_INVALIDO"));
        }

        callback(null, true);
    }
});



// Comprueba la cabecera inicial de un archivo PDF.
async function tieneCabeceraPDF(rutaArchivo) {
    const manejador = await fs.open(rutaArchivo, "r");

    try {
        const cabecera = Buffer.alloc(5);
        const { bytesRead } = await manejador.read(
            cabecera, 0, cabecera.length, 0
        );

        return bytesRead === 5 &&
            cabecera.toString("ascii") === "%PDF-";
    } finally {
        await manejador.close();
    }
}

// Ejecuta la validación estructural del PDF mediante Python.
function ejecutarValidadorPDF(rutaArchivo) {
    return new Promise((resolve, reject) => {
        const proceso = spawn(
            pythonValidadorPDF,
            [scriptValidadorPDF, rutaArchivo],
            {
                stdio: ["ignore", "pipe", "pipe"],
                timeout: TIEMPO_MAXIMO_VALIDACION_PDF_MS
            }
        );

        let salida = "";
        let errorProceso = "";
        let finalizado = false;
        let limiteSalidaSuperado = false;

        proceso.stdout.on("data", datos => {
            if (limiteSalidaSuperado) return;

            const tamanoActual = Buffer.byteLength(salida, "utf8");

            if (
                tamanoActual + datos.length >
                LIMITE_SALIDA_VALIDADOR_PDF_BYTES
            ) {
                limiteSalidaSuperado = true;
                proceso.kill();
                return;
            }

            salida += datos.toString();
        });

        proceso.stderr.on("data", datos => {
            if (limiteSalidaSuperado) return;

            const tamanoActual = Buffer.byteLength(errorProceso, "utf8");

            if (
                tamanoActual + datos.length >
                LIMITE_SALIDA_VALIDADOR_PDF_BYTES
            ) {
                limiteSalidaSuperado = true;
                proceso.kill();
                return;
            }

            errorProceso += datos.toString();
        });

        proceso.on("error", error => {
            if (finalizado) return;
            finalizado = true;
            reject(error);
        });

        proceso.on("close", (codigo, senal) => {
            if (finalizado) return;
            finalizado = true;

            if (limiteSalidaSuperado) {
                return reject(new Error("LIMITE_SALIDA_PDF_SUPERADO"));
            }

            if (senal) {
                return reject(new Error("VALIDACION_PDF_INTERRUMPIDA"));
            }

            if (codigo === 0 && salida.trim() === "PDF_VALIDO") {
                return resolve(true);
            }

            if (codigo === 1 && salida.trim() === "PDF_INVALIDO") {
                return resolve(false);
            }

            reject(new Error("ERROR_VALIDACION_PDF"));
        });
    });
}

// Elimina un documento PDF rechazado o que no deba conservarse.
async function eliminarArchivoPDF(rutaArchivo) {
    if (!rutaArchivo) return;

    try {
        await fs.unlink(rutaArchivo);
    } catch (error) {
        if (error.code !== "ENOENT") {
            throw error;
        }
    }
}

// Permite recibir información en formato JSON.
app.use(express.json());

// Ruta para comprobar que el servidor funciona.
app.get("/api/estado", (req, res) => {
    res.json({
        estado: "activo",
        mensaje: "Backend del chatbot jurídico funcionando",
        proyecto: "Chatbot RAG - Ley 1801 de 2016"
    });
});


// Recibe preguntas y las envía al motor RAG de Python.
app.post("/api/chat", (req, res) => {
    const pregunta = req.body?.pregunta;

    if (typeof pregunta !== "string" || !pregunta.trim()) {
        return res.status(400).json({
            error: "Debes enviar una pregunta válida."
        });
    }

    if (pregunta.length > 2000) {
        return res.status(400).json({
            error: "La pregunta supera el límite de 2000 caracteres."
        });
    }

    const python = path.resolve(__dirname, "../.venv/bin/python");
    const puente = path.resolve(__dirname, "puente_rag.py");

    const proceso = spawn(python, [puente], {
        cwd: path.resolve(__dirname, ".."),
        env: process.env
    });

    let salida = "";
    let errores = "";
    let finalizado = false;
    let tiempoAgotado = false;
    let salidaExcesiva = false;

    const LIMITE_SALIDA_BYTES = 1024 * 1024;
    let bytesSalida = 0;
    let bytesErrores = 0;

    const temporizador = setTimeout(() => {
        tiempoAgotado = true;
        proceso.kill();
    }, 120000);

    function controlarSalida(datos, tipo) {
        if (salidaExcesiva || finalizado) return;

        const bytes = Buffer.byteLength(datos);

        if (tipo === "stdout") {
            bytesSalida += bytes;
        } else {
            bytesErrores += bytes;
        }

        if (
            bytesSalida > LIMITE_SALIDA_BYTES ||
            bytesErrores > LIMITE_SALIDA_BYTES
        ) {
            salidaExcesiva = true;
            proceso.kill();
            return;
        }

        if (tipo === "stdout") {
            salida += datos.toString();
        } else {
            errores += datos.toString();
        }
    }

    proceso.stdout.on("data", (datos) => {
        controlarSalida(datos, "stdout");
    });

    proceso.stderr.on("data", (datos) => {
        controlarSalida(datos, "stderr");
    });

    proceso.on("error", () => {
        clearTimeout(temporizador);
        if (!finalizado) {
            finalizado = true;
            if (salidaExcesiva) {
                return res.status(502).json({
                    error: "El motor documental superó el tamaño máximo de salida."
                });
            }
            if (tiempoAgotado) {
                return res.status(504).json({
                    error: "La consulta superó el tiempo máximo de procesamiento."
                });
            }
            return res.status(500).json({
                error: "No fue posible iniciar el motor documental."
            });
        }
    });

    proceso.on("close", (codigo) => {
        clearTimeout(temporizador);

        if (finalizado) return;
        finalizado = true;

        if (salidaExcesiva) {
            return res.status(502).json({
                error: "El motor documental superó el tamaño máximo de salida."
            });
        }

        if (tiempoAgotado) {
            return res.status(504).json({
                error: "La consulta superó el tiempo máximo de procesamiento."
            });
        }

        if (codigo !== 0) {
            return res.status(500).json({
                error: "No fue posible procesar la consulta."
            });
        }

        try {
            const respuesta = JSON.parse(salida);

            if (
                !respuesta ||
                typeof respuesta !== "object" ||
                Array.isArray(respuesta) ||
                typeof respuesta.respuesta !== "string" ||
                !respuesta.respuesta.trim()
            ) {
                return res.status(500).json({
                    error: "El motor documental devolvió una respuesta inválida."
                });
            }

            const camposPublicos = [
                "pregunta",
                "respuesta",
                "modelo",
                "total_generales",
                "total_estructurados"
            ];

            const salidaPublica = {};

            for (const campo of camposPublicos) {
                if (Object.prototype.hasOwnProperty.call(respuesta, campo)) {
                    salidaPublica[campo] = respuesta[campo];
                }
            }

            const validacion = respuesta.validacion_documental;

            if (
                validacion &&
                typeof validacion === "object" &&
                !Array.isArray(validacion)
            ) {
                salidaPublica.validacion_documental = {
                    estado: validacion.estado,
                    advertencias: Array.isArray(validacion.advertencias)
                        ? validacion.advertencias
                            .filter(alerta =>
                                alerta &&
                                typeof alerta === "object" &&
                                !Array.isArray(alerta)
                            )
                            .map(alerta => ({
                                tipo: alerta.tipo,
                                detalle: alerta.detalle,
                                fragmento: alerta.fragmento
                            }))
                        : []
                };
            }

            return res.json(salidaPublica);
        } catch {
            return res.status(500).json({
                error: "El motor documental devolvió una respuesta inválida."
            });
        }
    });

    proceso.stdin.on("error", () => {});

    proceso.stdin.end(JSON.stringify({
        pregunta: pregunta.trim()
    }));
});


// Recibe y valida documentos PDF cargados por los usuarios.
app.post("/upload_pdf/", (req, res) => {
    cargarPDF.single("documento")(req, res, async error => {

        if (error) {
            if (req.file?.path) {
                try {
                    await eliminarArchivoPDF(req.file.path);
                } catch (errorLimpieza) {
                    console.error("Error al eliminar PDF:", errorLimpieza);
                }
            }

            if (error instanceof multer.MulterError) {
                if (error.code === "LIMIT_FILE_SIZE") {
                    return res.status(413).json({
                        error: "El PDF supera el límite permitido de 10 MB."
                    });
                }

                return res.status(400).json({
                    error: "No fue posible recibir el documento PDF."
                });
            }

            if (error.message === "TIPO_PDF_INVALIDO") {
                return res.status(400).json({
                    error: "El archivo debe tener extensión PDF y tipo MIME application/pdf."
                });
            }

            console.error("Error al recibir PDF:", error);

            return res.status(500).json({
                error: "No fue posible recibir el documento."
            });
        }

        if (!req.file) {
            return res.status(400).json({
                error: "Debes seleccionar un documento PDF."
            });
        }

        try {
            // Restringe el acceso al PDF antes de validarlo.
            await fs.chmod(req.file.path, 0o600);

            const cabeceraValida = await tieneCabeceraPDF(req.file.path);

            if (!cabeceraValida) {
                await eliminarArchivoPDF(req.file.path);

                return res.status(400).json({
                    error: "El archivo no contiene una cabecera PDF válida."
                });
            }

            const pdfValido = await ejecutarValidadorPDF(req.file.path);

            if (!pdfValido) {
                await eliminarArchivoPDF(req.file.path);

                return res.status(422).json({
                    error: "El documento PDF no superó la validación estructural."
                });
            }

            // Extrae metadatos del PDF mediante el controlador Python.
            const extraccion = await ejecutarExtraccionPDF(
                req.file.filename
            );

            if (extraccion.estado !== "correcto") {
                await eliminarArchivoPDF(req.file.path);

                if (extraccion.codigo === "TIEMPO_AGOTADO") {
                    return res.status(504).json({
                        error: "La extracción del PDF superó el tiempo permitido."
                    });
                }

                if (extraccion.codigo === "EXTRACCION_RECHAZADA") {
                    return res.status(422).json({
                        error: "El PDF no contiene texto extraíble válido o fue rechazado."
                    });
                }

                return res.status(502).json({
                    error: "No fue posible extraer el contenido del PDF."
                });
            }

            return res.status(201).json({
                estado: "aceptado",
                mensaje: "Documento PDF recibido, validado y procesado correctamente.",
                documento: {
                    nombre: req.file.filename,
                    tamano_bytes: req.file.size,
                    indexado: false,
                    extraccion: {
                        estado: "correcto",
                        total_paginas_con_texto:
                            extraccion.total_paginas_con_texto,
                        total_caracteres:
                            extraccion.total_caracteres
                    }
                }
            });

        } catch (errorValidacion) {
            try {
                await eliminarArchivoPDF(req.file.path);
            } catch (errorLimpieza) {
                console.error("Error al eliminar PDF rechazado:", errorLimpieza);
            }

            if (errorValidacion.message === "LIMITE_SALIDA_PDF_SUPERADO") {
                return res.status(502).json({
                    error: "El validador PDF superó el límite máximo de salida."
                });
            }

            if (errorValidacion.message === "VALIDACION_PDF_INTERRUMPIDA") {
                return res.status(504).json({
                    error: "La validación del documento superó el tiempo permitido o fue interrumpida."
                });
            }

            console.error("Error en validación PDF:", errorValidacion);

            return res.status(500).json({
                error: "No fue posible completar la validación del documento."
            });
        }
    });
});

// Sirve los archivos HTML, CSS y JavaScript del frontend.
const carpetaFrontend = path.resolve(__dirname, "../frontend");
app.use(express.static(carpetaFrontend));

// Inicia el servidor.
app.listen(PORT, () => {
    console.log(`Servidor iniciado en el puerto ${PORT}`);
});
