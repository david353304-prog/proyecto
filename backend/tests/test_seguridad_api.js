"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const http = require("node:http");
const { EventEmitter } = require("node:events");
const { PassThrough } = require("node:stream");
const cp = require("node:child_process");
const path = require("node:path");

const archivoBackend = path.resolve(__dirname, "../index.js");

async function probarRespuesta(salidaSimulada) {
    const spawnOriginal = cp.spawn;
    const listenOriginal = http.Server.prototype.listen;

    let servidor = null;

    cp.spawn = function () {
        const proceso = new EventEmitter();

        proceso.stdout = new PassThrough();
        proceso.stderr = new PassThrough();
        proceso.stdin = new PassThrough();

        proceso.kill = () => true;

        proceso.stdin.on("finish", () => {
            setImmediate(() => {
                proceso.stdout.end(salidaSimulada);
                proceso.stderr.end();
                proceso.emit("close", 0);
            });
        });

        return proceso;
    };

    http.Server.prototype.listen = function () {
        servidor = this;
        return listenOriginal.call(this, 0, "127.0.0.1");
    };

    try {
        delete require.cache[require.resolve(archivoBackend)];
        require(archivoBackend);

        await new Promise((resolve, reject) => {
            if (servidor.listening) return resolve();
            servidor.once("listening", resolve);
            servidor.once("error", reject);
        });

        const puerto = servidor.address().port;

        const respuesta = await fetch(
            `http://127.0.0.1:${puerto}/api/chat`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    pregunta: "Consulta de prueba"
                }),
                signal: AbortSignal.timeout(10000)
            }
        );

        return {
            estado: respuesta.status,
            datos: await respuesta.json()
        };
    } finally {
        cp.spawn = spawnOriginal;
        http.Server.prototype.listen = listenOriginal;

        if (servidor) {
            await new Promise(resolve => servidor.close(resolve));
        }

        delete require.cache[require.resolve(archivoBackend)];
    }
}

test("La API acepta una respuesta pública válida", async () => {
    const resultado = await probarRespuesta(JSON.stringify({
        pregunta: "Consulta de prueba",
        respuesta: "Respuesta pública",
        validacion_documental: {
            estado: "PENDIENTE_VALIDACION",
            advertencias: []
        }
    }));

    assert.equal(resultado.estado, 200);
    assert.equal(resultado.datos.respuesta, "Respuesta pública");
});

test("La API rechaza respuestas sin texto público", async () => {
    const resultado = await probarRespuesta(JSON.stringify({
        pregunta: "Consulta de prueba",
        validacion_documental: {
            estado: "PENDIENTE_VALIDACION",
            advertencias: []
        }
    }));

    assert.equal(resultado.estado, 500);
    assert.equal(
        Object.hasOwn(resultado.datos, "respuesta"),
        false
    );
});

test("La API no expone respuesta_original", async () => {
    const resultado = await probarRespuesta(JSON.stringify({
        pregunta: "Consulta de prueba",
        respuesta: "Respuesta pública",
        respuesta_original: "CONTENIDO INTERNO",
        validacion_documental: {
            estado: "REQUIERE_REVISION",
            advertencias: []
        }
    }));

    assert.equal(resultado.estado, 200);
    assert.equal(
        Object.hasOwn(resultado.datos, "respuesta_original"),
        false
    );
});

test("La API rechaza JSON inválido", async () => {
    const resultado = await probarRespuesta("ESTO NO ES JSON");

    assert.equal(resultado.estado, 500);
    assert.equal(typeof resultado.datos.error, "string");
});


test("La API devuelve HTTP 504 cuando se agota el tiempo", async () => {
    const spawnOriginal = cp.spawn;
    const listenOriginal = http.Server.prototype.listen;
    const timeoutOriginal = global.setTimeout;
    const clearOriginal = global.clearTimeout;

    let servidor = null;
    let temporizadorSimulado = null;
    let procesoDetenido = false;

    try {
        cp.spawn = () => {
            const proceso = new EventEmitter();

            proceso.stdout = new PassThrough();
            proceso.stderr = new PassThrough();
            proceso.stdin = new PassThrough();

            proceso.kill = () => {
                procesoDetenido = true;
                setImmediate(() => proceso.emit("close", null));
                return true;
            };

            return proceso;
        };

        http.Server.prototype.listen = function () {
            servidor = this;
            return listenOriginal.call(this, 0, "127.0.0.1");
        };

        global.setTimeout = (funcion, tiempo) => {
            if (tiempo === 120000) {
                temporizadorSimulado = funcion;
                return { simulado: true };
            }

            return timeoutOriginal(funcion, tiempo);
        };

        global.clearTimeout = identificador => {
            if (identificador?.simulado) return;
            return clearOriginal(identificador);
        };

        delete require.cache[require.resolve(archivoBackend)];
        require(archivoBackend);

        await new Promise((resolve, reject) => {
            if (servidor.listening) return resolve();
            servidor.once("listening", resolve);
            servidor.once("error", reject);
        });

        const puerto = servidor.address().port;

        const solicitud = fetch(
            `http://127.0.0.1:${puerto}/api/chat`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    pregunta: "Prueba automatizada de timeout"
                }),
                signal: AbortSignal.timeout(10000)
            }
        );

        for (let intento = 0; intento < 100; intento++) {
            if (temporizadorSimulado) break;

            await new Promise(resolve =>
                timeoutOriginal(resolve, 10)
            );
        }

        assert.equal(typeof temporizadorSimulado, "function");

        temporizadorSimulado();

        const respuesta = await solicitud;
        const datos = await respuesta.json();

        assert.equal(procesoDetenido, true);
        assert.equal(respuesta.status, 504);
        assert.equal(
            datos.error,
            "La consulta superó el tiempo máximo de procesamiento."
        );

    } finally {
        cp.spawn = spawnOriginal;
        http.Server.prototype.listen = listenOriginal;
        global.setTimeout = timeoutOriginal;
        global.clearTimeout = clearOriginal;

        if (servidor) {
            await new Promise(resolve => servidor.close(resolve));
        }

        delete require.cache[require.resolve(archivoBackend)];
    }
});
