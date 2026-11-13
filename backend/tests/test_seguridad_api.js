"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const http = require("node:http");
const path = require("node:path");

const archivoBackend = path.resolve(__dirname, "../index.js");
const URL_FASTAPI = "http://127.0.0.1:8000/consultar";
const LIMITE = 1024 * 1024;

async function probarAPI(simulacion, pregunta = "Consulta de prueba") {
    const fetchOriginal = global.fetch;
    const listenOriginal = http.Server.prototype.listen;
    let servidor = null;

    global.fetch = async (url, opciones) => {
        if (url === URL_FASTAPI) {
            return simulacion(url, opciones);
        }
        return fetchOriginal(url, opciones);
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

        const respuesta = await fetchOriginal(
            `http://127.0.0.1:${servidor.address().port}/api/chat`,
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ pregunta }),
                signal: AbortSignal.timeout(10000)
            }
        );

        return {
            estado: respuesta.status,
            datos: await respuesta.json()
        };
    } finally {
        global.fetch = fetchOriginal;
        http.Server.prototype.listen = listenOriginal;

        if (servidor) {
            await new Promise(resolve => servidor.close(resolve));
        }

        delete require.cache[require.resolve(archivoBackend)];
    }
}

function respuestaSimulada(datos, estado = 200) {
    return new Response(JSON.stringify(datos), {
        status: estado,
        headers: { "Content-Type": "application/json" }
    });
}

test("La API acepta una respuesta pública válida", async () => {
    const resultado = await probarAPI(() => respuestaSimulada({
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
    const resultado = await probarAPI(() => respuestaSimulada({
        pregunta: "Consulta de prueba"
    }));

    assert.equal(resultado.estado, 500);
    assert.equal(Object.hasOwn(resultado.datos, "respuesta"), false);
});

test("La API no expone respuesta_original", async () => {
    const resultado = await probarAPI(() => respuestaSimulada({
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
    const resultado = await probarAPI(() => new Response(
        "ESTO NO ES JSON",
        { status: 200 }
    ));

    assert.equal(resultado.estado, 500);
    assert.equal(typeof resultado.datos.error, "string");
});

test("La API rechaza errores HTTP de FastAPI", async () => {
    const resultado = await probarAPI(() => respuestaSimulada({
        detail: "Error interno"
    }, 500));

    assert.equal(resultado.estado, 502);
});

test("La API maneja fallos de conexión con FastAPI", async () => {
    const resultado = await probarAPI(() => {
        throw new Error("ECONNREFUSED simulado");
    });

    assert.equal(resultado.estado, 502);
});

test("La API acepta una respuesta HTTP normal", async () => {
    const resultado = await probarAPI(() => respuestaSimulada({
        respuesta: "Respuesta válida"
    }));

    assert.equal(resultado.estado, 200);
    assert.equal(resultado.datos.respuesta, "Respuesta válida");
});

test("La API rechaza respuestas superiores a 1 MiB", async () => {
    const resultado = await probarAPI(() => new Response(
        "A".repeat(LIMITE + 1),
        { status: 200 }
    ));

    assert.equal(resultado.estado, 502);
});

test("La API acepta una respuesta exactamente de 1 MiB", async () => {
    const base = JSON.stringify({
        respuesta: "Respuesta válida",
        relleno: ""
    });

    const salida = JSON.stringify({
        respuesta: "Respuesta válida",
        relleno: "X".repeat(
            LIMITE - Buffer.byteLength(base)
        )
    });

    assert.equal(Buffer.byteLength(salida), LIMITE);

    const resultado = await probarAPI(() => new Response(salida, {
        status: 200
    }));

    assert.equal(resultado.estado, 200);
    assert.equal(resultado.datos.respuesta, "Respuesta válida");
});

test("La API conserva correctamente caracteres UTF-8", async () => {
    const resultado = await probarAPI(() => respuestaSimulada({
        respuesta: "Artículo 27: protección y convivencia ciudadana."
    }));

    assert.equal(resultado.estado, 200);
    assert.equal(
        resultado.datos.respuesta,
        "Artículo 27: protección y convivencia ciudadana."
    );
});

test("La API rechaza preguntas vacías", async () => {
    const resultado = await probarAPI(
        () => {
            throw new Error("No debería llamar a FastAPI");
        },
        " "
    );

    assert.equal(resultado.estado, 400);
});

test("La API rechaza preguntas superiores a 2000 caracteres", async () => {
    const resultado = await probarAPI(
        () => {
            throw new Error("No debería llamar a FastAPI");
        },
        "A".repeat(2001)
    );

    assert.equal(resultado.estado, 400);
});

test("La API devuelve HTTP 504 cuando FastAPI agota el tiempo", async () => {
    const fetchOriginal = global.fetch;
    const setTimeoutOriginal = global.setTimeout;
    const clearTimeoutOriginal = global.clearTimeout;
    const listenOriginal = http.Server.prototype.listen;

    let servidor = null;
    let temporizador = null;
    let llamadaInterrumpida = false;

    try {
        global.fetch = (url, opciones) => {
            if (url !== URL_FASTAPI) {
                return fetchOriginal(url, opciones);
            }

            return new Promise((resolve, reject) => {
                opciones.signal.addEventListener("abort", () => {
                    llamadaInterrumpida = true;
                    const error = new Error("Solicitud interrumpida");
                    error.name = "AbortError";
                    reject(error);
                }, { once: true });
            });
        };

        global.setTimeout = (funcion, tiempo, ...argumentos) => {
            if (tiempo === 120000) {
                temporizador = funcion;
                return { simulado: true };
            }

            return setTimeoutOriginal(funcion, tiempo, ...argumentos);
        };

        global.clearTimeout = identificador => {
            if (identificador?.simulado) return;
            return clearTimeoutOriginal(identificador);
        };

        http.Server.prototype.listen = function () {
            servidor = this;
            return listenOriginal.call(this, 0, "127.0.0.1");
        };

        delete require.cache[require.resolve(archivoBackend)];
        require(archivoBackend);

        await new Promise((resolve, reject) => {
            if (servidor.listening) return resolve();
            servidor.once("listening", resolve);
            servidor.once("error", reject);
        });

        const solicitud = fetchOriginal(
            `http://127.0.0.1:${servidor.address().port}/api/chat`,
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    pregunta: "Prueba de timeout HTTP"
                }),
                signal: AbortSignal.timeout(10000)
            }
        );

        for (let intento = 0; intento < 100; intento++) {
            if (temporizador) break;
            await new Promise(resolve => setTimeoutOriginal(resolve, 10));
        }

        assert.equal(typeof temporizador, "function");

        temporizador();

        const respuesta = await solicitud;
        const datos = await respuesta.json();

        assert.equal(llamadaInterrumpida, true);
        assert.equal(respuesta.status, 504);
        assert.equal(
            datos.error,
            "La consulta superó el tiempo máximo de procesamiento."
        );
    } finally {
        global.fetch = fetchOriginal;
        global.setTimeout = setTimeoutOriginal;
        global.clearTimeout = clearTimeoutOriginal;
        http.Server.prototype.listen = listenOriginal;

        if (servidor) {
            await new Promise(resolve => servidor.close(resolve));
        }

        delete require.cache[require.resolve(archivoBackend)];
    }
});

test("La API reconstruye caracteres UTF-8 divididos entre fragmentos", async () => {
    const texto = "¿Qué señala el artículo 27 sobre la convivencia?";
    const contenido = Buffer.from(
        JSON.stringify({ respuesta: texto }),
        "utf8"
    );

    const posicion = contenido.indexOf(Buffer.from("ñ", "utf8"));

    assert.notEqual(posicion, -1);

    const fragmentos = [
        contenido.subarray(0, posicion + 1),
        contenido.subarray(posicion + 1)
    ];

    const resultado = await probarAPI(() => {
        const cuerpo = new ReadableStream({
            start(controlador) {
                for (const fragmento of fragmentos) {
                    controlador.enqueue(fragmento);
                }
                controlador.close();
            }
        });

        return new Response(cuerpo, {
            status: 200,
            headers: {
                "Content-Type": "application/json"
            }
        });
    });

    assert.equal(resultado.estado, 200);
    assert.equal(resultado.datos.respuesta, texto);
});

test("La API maneja una conexión HTTP interrumpida", async () => {
    const resultado = await probarAPI(() => {
        const cuerpo = new ReadableStream({
            start(controlador) {
                controlador.enqueue(
                    Buffer.from('{"respuesta":"Respuesta incompleta')
                );

                controlador.error(
                    new Error("Conexión interrumpida simulada")
                );
            }
        });

        return new Response(cuerpo, {
            status: 200,
            headers: {
                "Content-Type": "application/json"
            }
        });
    });

    assert.equal(resultado.estado, 502);
    assert.equal(typeof resultado.datos.error, "string");
    assert.equal(
        Object.hasOwn(resultado.datos, "respuesta"),
        false
    );
});
