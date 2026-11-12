"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const http = require("node:http");
const path = require("node:path");
const fs = require("node:fs/promises");
const os = require("node:os");

const archivoBackend = path.resolve(
    __dirname,
    "../index.js"
);

async function probarCargaPDF(prepararSolicitud) {
    const listenOriginal = http.Server.prototype.listen;
    const entornoAnterior = process.env.NODE_ENV;
    const directorioAnterior = process.env.DIRECTORIO_PDF_PRUEBAS;

    const directorioTemporal = await fs.mkdtemp(
        path.join(os.tmpdir(), "chatbot-pdf-test-")
    );

    process.env.NODE_ENV = "test";
    process.env.DIRECTORIO_PDF_PRUEBAS = directorioTemporal;

    let servidor = null;

    http.Server.prototype.listen = function () {
        servidor = this;

        return listenOriginal.call(
            this,
            0,
            "127.0.0.1"
        );
    };

    try {
        delete require.cache[
            require.resolve(archivoBackend)
        ];

        require(archivoBackend);

        await new Promise((resolve, reject) => {
            if (servidor.listening) {
                return resolve();
            }

            servidor.once("listening", resolve);
            servidor.once("error", reject);
        });

        const url = (
            `http://127.0.0.1:${servidor.address().port}` +
            "/upload_pdf/"
        );

        const opciones = prepararSolicitud();

        const respuesta = await fetch(url, {
            method: "POST",
            body: opciones.body,
            signal: AbortSignal.timeout(10000)
        });

        const datos = await respuesta.json();

        const archivosRestantes = await fs.readdir(
            directorioTemporal
        );

        return {
            estado: respuesta.status,
            datos,
            archivosRestantes
        };

    } finally {
        http.Server.prototype.listen = listenOriginal;

        try {
            if (servidor) {
                await new Promise(resolve => {
                    servidor.close(resolve);
                });
            }
        } finally {
            delete require.cache[
                require.resolve(archivoBackend)
            ];

            if (entornoAnterior === undefined) {
                delete process.env.NODE_ENV;
            } else {
                process.env.NODE_ENV = entornoAnterior;
            }

            if (directorioAnterior === undefined) {
                delete process.env.DIRECTORIO_PDF_PRUEBAS;
            } else {
                process.env.DIRECTORIO_PDF_PRUEBAS = directorioAnterior;
            }

            await fs.rm(directorioTemporal, {
                recursive: true,
                force: true
            });
        }
    }
}

test("La carga PDF rechaza solicitudes sin documento", async () => {
    const resultado = await probarCargaPDF(() => ({
        body: new FormData()
    }));

    assert.equal(resultado.estado, 400);
    assert.equal(
        resultado.datos.error,
        "Debes seleccionar un documento PDF."
    );
});

test("La carga PDF rechaza archivos que no son PDF", async () => {
    const resultado = await probarCargaPDF(() => {
        const formulario = new FormData();

        formulario.append(
            "documento",
            new Blob(
                ["Contenido de prueba"],
                { type: "text/plain" }
            ),
            "archivo.txt"
        );

        return {
            body: formulario
        };
    });

    assert.equal(resultado.estado, 400);

    assert.equal(
        resultado.datos.error,
        "El archivo debe tener extensión PDF y tipo MIME application/pdf."
    );
});


test("La carga PDF acepta un documento válido", async () => {
    const { spawnSync } = require("node:child_process");

    const python = path.resolve(
        __dirname,
        "../../.venv/bin/python"
    );

    const generador = spawnSync(
        python,
        [
            "-c",
            [
                "import pymupdf",
                "import sys",
                "doc = pymupdf.open()",
                "pagina = doc.new_page()",
                "pagina.insert_text((72, 72), 'PDF de prueba')",
                "sys.stdout.buffer.write(doc.tobytes())",
                "doc.close()"
            ].join("\n")
        ],
        {
            encoding: null,
            maxBuffer: 1024 * 1024,
            timeout: 10000
        }
    );

    assert.equal(
        generador.status,
        0,
        "No fue posible generar el PDF de prueba."
    );

    const contenidoPDF = generador.stdout;

    assert.ok(contenidoPDF.length > 0);

    const resultado = await probarCargaPDF(() => {
        const formulario = new FormData();

        formulario.append(
            "documento",
            new Blob(
                [contenidoPDF],
                { type: "application/pdf" }
            ),
            "prueba.pdf"
        );

        return {
            body: formulario
        };
    });

    assert.equal(resultado.estado, 201);
    assert.equal(resultado.datos.estado, "aceptado");

    assert.deepEqual(
        resultado.archivosRestantes,
        [resultado.datos.documento.nombre],
        "El PDF válido debe permanecer almacenado."
    );
    assert.equal(resultado.datos.documento.indexado, false);

    assert.match(
        resultado.datos.documento.nombre,
        /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.pdf$/
    );

    assert.equal(
        resultado.datos.documento.tamano_bytes,
        contenidoPDF.length
    );

    assert.deepEqual(
        resultado.datos.documento.extraccion,
        {
            estado: "correcto",
            total_paginas_con_texto: 1,
            total_caracteres: "PDF de prueba".length
        }
    );
});


test("La carga PDF rechaza documentos sin texto", async () => {
    const { spawnSync } = require("node:child_process");

    const python = path.resolve(
        __dirname,
        "../../.venv/bin/python"
    );

    const generador = spawnSync(
        python,
        [
            "-c",
            [
                "import pymupdf",
                "import sys",
                "doc = pymupdf.open()",
                "doc.new_page()",
                "sys.stdout.buffer.write(doc.tobytes())",
                "doc.close()"
            ].join("\n")
        ],
        {
            encoding: null,
            maxBuffer: 1024 * 1024,
            timeout: 10000
        }
    );

    assert.equal(
        generador.status,
        0,
        "No fue posible generar el PDF sin texto."
    );

    const resultado = await probarCargaPDF(() => {
        const formulario = new FormData();

        formulario.append(
            "documento",
            new Blob(
                [generador.stdout],
                { type: "application/pdf" }
            ),
            "sin_texto.pdf"
        );

        return { body: formulario };
    });

    assert.equal(resultado.estado, 422);

    assert.deepEqual(
        resultado.archivosRestantes,
        [],
        "El PDF rechazado no debe permanecer almacenado."
    );

    assert.equal(
        resultado.datos.error,
        "El PDF no contiene texto extraíble válido o fue rechazado."
    );
});
