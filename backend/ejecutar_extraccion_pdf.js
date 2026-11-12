"use strict";

const { spawn } = require("node:child_process");
const path = require("node:path");

const PYTHON = path.resolve(
    __dirname,
    "../.venv/bin/python"
);

const CONTROLADOR = path.resolve(
    __dirname,
    "../motor_documental/controlar_extraccion_pdf.py"
);

const TIMEOUT_NORMAL_MS = 35000;

const timeoutPruebas = Number(
    process.env.TIMEOUT_EXTRACCION_PDF_PRUEBAS
);

const TIEMPO_MAXIMO_MS = (
    process.env.NODE_ENV === "test" &&
    Number.isInteger(timeoutPruebas) &&
    timeoutPruebas >= 100 &&
    timeoutPruebas <= TIMEOUT_NORMAL_MS
)
    ? timeoutPruebas
    : TIMEOUT_NORMAL_MS;

const LIMITE_SALIDA_BYTES = 4096;

const PATRON_UUID_PDF =
    /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.pdf$/;

function ejecutarExtraccionPDF(nombreArchivo) {
    if (
        typeof nombreArchivo !== "string" ||
        !PATRON_UUID_PDF.test(nombreArchivo)
    ) {
        return Promise.resolve({
            estado: "error",
            codigo: "ARGUMENTOS_INVALIDOS"
        });
    }

    return new Promise((resolve) => {
        let proceso;

        try {
            proceso = spawn(
                PYTHON,
                [CONTROLADOR, nombreArchivo],
                {
                    stdio: ["ignore", "pipe", "pipe"],
                    detached: process.platform !== "win32",
                    env: process.env
                }
            );
        } catch {
            resolve({
                estado: "error",
                codigo: "ERROR_EJECUCION"
            });
            return;
        }

        const salida = [];
        let bytesSalida = 0;
        let bytesError = 0;
        let finalizado = false;
        let salidaExcesiva = false;
        let errorInicio = false;
        let tiempoAgotado = false;
        let temporizador = null;

        function detenerProcesos() {
            if (!proceso.pid) return;

            try {
                if (process.platform !== "win32") {
                    process.kill(-proceso.pid, "SIGKILL");
                } else {
                    proceso.kill("SIGKILL");
                }
            } catch (error) {
                if (error.code !== "ESRCH") {
                    // No exponer detalles internos del proceso.
                }
            }
        }

        temporizador = setTimeout(() => {
            tiempoAgotado = true;
            detenerProcesos();
        }, TIEMPO_MAXIMO_MS);

        function finalizar(respuesta) {
            if (finalizado) return;
            finalizado = true;
            clearTimeout(temporizador);
            resolve(respuesta);
        }

        proceso.stdout.on("data", fragmento => {
            bytesSalida += fragmento.length;

            if (bytesSalida > LIMITE_SALIDA_BYTES) {
                salidaExcesiva = true;
                detenerProcesos();
                return;
            }

            if (!salidaExcesiva) {
                salida.push(fragmento);
            }
        });

        proceso.stderr.on("data", fragmento => {
            bytesError += fragmento.length;

            if (bytesError > LIMITE_SALIDA_BYTES) {
                salidaExcesiva = true;
                detenerProcesos();
            }
        });

        proceso.on("error", () => {
            errorInicio = true;
            finalizar({
                estado: "error",
                codigo: "ERROR_EJECUCION"
            });
        });

        proceso.on("close", (codigo, senal) => {
            if (finalizado) return;

            if (tiempoAgotado) {
                finalizar({
                    estado: "error",
                    codigo: "TIEMPO_AGOTADO"
                });
                return;
            }

            if (salidaExcesiva) {
                finalizar({
                    estado: "error",
                    codigo: "SALIDA_EXCESIVA"
                });
                return;
            }

            if (errorInicio) {
                finalizar({
                    estado: "error",
                    codigo: "ERROR_EJECUCION"
                });
                return;
            }

            if (senal) {
                finalizar({
                    estado: "error",
                    codigo: "PROCESO_INTERRUMPIDO"
                });
                return;
            }

            let datos;

            try {
                datos = JSON.parse(
                    Buffer.concat(salida).toString("utf8")
                );
            } catch {
                finalizar({
                    estado: "error",
                    codigo: "RESPUESTA_INVALIDA"
                });
                return;
            }

            if (
                !datos ||
                typeof datos !== "object" ||
                Array.isArray(datos)
            ) {
                finalizar({
                    estado: "error",
                    codigo: "RESPUESTA_INVALIDA"
                });
                return;
            }

            if (
                codigo === 0 &&
                datos.estado === "correcto" &&
                datos.documento === nombreArchivo &&
                Number.isInteger(datos.total_paginas_con_texto) &&
                datos.total_paginas_con_texto > 0 &&
                datos.total_paginas_con_texto <= 200 &&
                Number.isInteger(datos.total_caracteres) &&
                datos.total_caracteres > 0 &&
                datos.total_caracteres <= 1000000
            ) {
                finalizar({
                    estado: "correcto",
                    documento: datos.documento,
                    total_paginas_con_texto:
                        datos.total_paginas_con_texto,
                    total_caracteres:
                        datos.total_caracteres
                });
                return;
            }

            const codigosPermitidos = new Set([
                "ARGUMENTOS_INVALIDOS",
                "EXTRACCION_RECHAZADA",
                "ERROR_RECURSOS",
                "TIEMPO_AGOTADO",
                "ERROR_EJECUCION",
                "SALIDA_EXCESIVA",
                "RESPUESTA_INVALIDA",
                "EXTRACCION_FALLIDA"
            ]);

            if (
                codigo !== 0 &&
                datos.estado === "error" &&
                codigosPermitidos.has(datos.codigo)
            ) {
                finalizar({
                    estado: "error",
                    codigo: datos.codigo
                });
                return;
            }

            finalizar({
                estado: "error",
                codigo: "RESPUESTA_INVALIDA"
            });
        });
    });
}

module.exports = {
    ejecutarExtraccionPDF
};
