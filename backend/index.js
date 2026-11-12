const { spawn } = require("node:child_process");
const path = require("node:path");

const express = require("express");

const app = express();
const PORT = process.env.PORT || 3000;

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
                                detalle: alerta.detalle
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


// Sirve los archivos HTML, CSS y JavaScript del frontend.
const carpetaFrontend = path.resolve(__dirname, "../frontend");
app.use(express.static(carpetaFrontend));

// Inicia el servidor.
app.listen(PORT, () => {
    console.log(`Servidor iniciado en el puerto ${PORT}`);
});
