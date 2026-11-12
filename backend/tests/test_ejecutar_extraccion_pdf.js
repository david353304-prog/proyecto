"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const crypto = require("node:crypto");
const { spawnSync } = require("node:child_process");

const {
    ejecutarExtraccionPDF
} = require("../ejecutar_extraccion_pdf.js");

const PYTHON = path.resolve(
    __dirname,
    "../../.venv/bin/python"
);

test("El puente rechaza nombres PDF inválidos", async () => {
    const resultado = await ejecutarExtraccionPDF(
        "../documento.pdf"
    );

    assert.deepEqual(resultado, {
        estado: "error",
        codigo: "ARGUMENTOS_INVALIDOS"
    });
});

test("El puente extrae metadatos de un PDF válido", async () => {
    const carpeta = await fs.mkdtemp(
        path.join(os.tmpdir(), "chatbot-puente-pdf-")
    );

    const entornoAnterior = process.env.NODE_ENV;
    const directorioAnterior =
        process.env.DIRECTORIO_PDF_PRUEBAS;

    try {
        process.env.NODE_ENV = "test";
        process.env.DIRECTORIO_PDF_PRUEBAS = carpeta;

        const nombre = `${crypto.randomUUID()}.pdf`;
        const ruta = path.join(carpeta, nombre);

        const generador = spawnSync(
            PYTHON,
            [
                "-c",
                [
                    "import pymupdf",
                    "import sys",
                    "doc = pymupdf.open()",
                    "pagina = doc.new_page()",
                    "pagina.insert_text((72, 72), 'Prueba automatizada PDF')",
                    "doc.save(sys.argv[1])",
                    "doc.close()"
                ].join("\n"),
                ruta
            ],
            {
                encoding: "utf8",
                timeout: 10000
            }
        );

        assert.equal(generador.status, 0);

        const resultado = await ejecutarExtraccionPDF(
            nombre
        );

        assert.equal(resultado.estado, "correcto");
        assert.equal(resultado.documento, nombre);
        assert.equal(resultado.total_paginas_con_texto, 1);
        assert.ok(resultado.total_caracteres > 0);

    } finally {
        if (entornoAnterior === undefined) {
            delete process.env.NODE_ENV;
        } else {
            process.env.NODE_ENV = entornoAnterior;
        }

        if (directorioAnterior === undefined) {
            delete process.env.DIRECTORIO_PDF_PRUEBAS;
        } else {
            process.env.DIRECTORIO_PDF_PRUEBAS =
                directorioAnterior;
        }

        await fs.rm(carpeta, {
            recursive: true,
            force: true
        });
    }
});

test("El puente rechaza un PDF inexistente", async () => {
    const carpeta = await fs.mkdtemp(
        path.join(os.tmpdir(), "chatbot-puente-pdf-")
    );

    const entornoAnterior = process.env.NODE_ENV;
    const directorioAnterior =
        process.env.DIRECTORIO_PDF_PRUEBAS;

    try {
        process.env.NODE_ENV = "test";
        process.env.DIRECTORIO_PDF_PRUEBAS = carpeta;

        const resultado = await ejecutarExtraccionPDF(
            `${crypto.randomUUID()}.pdf`
        );

        assert.deepEqual(resultado, {
            estado: "error",
            codigo: "EXTRACCION_RECHAZADA"
        });

    } finally {
        if (entornoAnterior === undefined) {
            delete process.env.NODE_ENV;
        } else {
            process.env.NODE_ENV = entornoAnterior;
        }

        if (directorioAnterior === undefined) {
            delete process.env.DIRECTORIO_PDF_PRUEBAS;
        } else {
            process.env.DIRECTORIO_PDF_PRUEBAS =
                directorioAnterior;
        }

        await fs.rm(carpeta, {
            recursive: true,
            force: true
        });
    }
});

test("El puente rechaza un PDF sin texto", async () => {
    const carpeta = await fs.mkdtemp(
        path.join(os.tmpdir(), "chatbot-puente-pdf-")
    );

    const entornoAnterior = process.env.NODE_ENV;
    const directorioAnterior =
        process.env.DIRECTORIO_PDF_PRUEBAS;

    try {
        process.env.NODE_ENV = "test";
        process.env.DIRECTORIO_PDF_PRUEBAS = carpeta;

        const nombre = `${crypto.randomUUID()}.pdf`;
        const ruta = path.join(carpeta, nombre);

        const generador = spawnSync(
            PYTHON,
            [
                "-c",
                [
                    "import pymupdf",
                    "import sys",
                    "doc = pymupdf.open()",
                    "doc.new_page()",
                    "doc.save(sys.argv[1])",
                    "doc.close()"
                ].join("\n"),
                ruta
            ],
            {
                encoding: "utf8",
                timeout: 10000
            }
        );

        assert.equal(generador.status, 0);

        const resultado = await ejecutarExtraccionPDF(
            nombre
        );

        assert.deepEqual(resultado, {
            estado: "error",
            codigo: "EXTRACCION_RECHAZADA"
        });

    } finally {
        if (entornoAnterior === undefined) {
            delete process.env.NODE_ENV;
        } else {
            process.env.NODE_ENV = entornoAnterior;
        }

        if (directorioAnterior === undefined) {
            delete process.env.DIRECTORIO_PDF_PRUEBAS;
        } else {
            process.env.DIRECTORIO_PDF_PRUEBAS =
                directorioAnterior;
        }

        await fs.rm(carpeta, {
            recursive: true,
            force: true
        });
    }
});


test("El puente rechaza metadatos inválidos de Python", async () => {
    const { EventEmitter } = require("node:events");
    const { PassThrough } = require("node:stream");
    const childProcess = require("node:child_process");

    const nombre = `${crypto.randomUUID()}.pdf`;

    const casos = [
        [0, 100],
        [1, 0],
        [0, 0],
        [-1, 100],
        [1, -1],
        [201, 100],
        [1, 1000001],
        [1.5, 100],
        [1, 10.5],
        [true, 100],
        [1, false],
        ["1", 100],
        [1, "100"],
        [null, 100],
        [1, null]
    ];

    const rutaPuente = require.resolve(
        "../ejecutar_extraccion_pdf.js"
    );

    const moduloChildProcess = require.resolve(
        "node:child_process"
    );

    const spawnOriginal = childProcess.spawn;
    const moduloAnterior = require.cache[rutaPuente];

    try {
        for (const [paginas, caracteres] of casos) {
            const proceso = new EventEmitter();

            proceso.pid = undefined;
            proceso.stdout = new PassThrough();
            proceso.stderr = new PassThrough();

            childProcess.spawn = () => {
                process.nextTick(() => {
                    proceso.stdout.end(
                        JSON.stringify({
                            estado: "correcto",
                            documento: nombre,
                            total_paginas_con_texto: paginas,
                            total_caracteres: caracteres
                        })
                    );

                    proceso.stderr.end();

                    proceso.emit("close", 0, null);
                });

                return proceso;
            };

            delete require.cache[rutaPuente];

            const puente = require(rutaPuente);

            const resultado = await puente.ejecutarExtraccionPDF(
                nombre
            );

            assert.deepEqual(
                resultado,
                {
                    estado: "error",
                    codigo: "RESPUESTA_INVALIDA"
                },
                `Debe rechazar páginas=${JSON.stringify(paginas)}, caracteres=${JSON.stringify(caracteres)}`
            );
        }
    } finally {
        childProcess.spawn = spawnOriginal;

        delete require.cache[rutaPuente];

        if (moduloAnterior) {
            require.cache[rutaPuente] = moduloAnterior;
        }
    }
});
