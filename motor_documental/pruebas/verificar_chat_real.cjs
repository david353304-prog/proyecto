"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const { spawn } = require("node:child_process");
const { setTimeout: pausa } = require("node:timers/promises");

async function esperar(operacion, segundos = 20) {
    const fin = Date.now() + segundos * 1000;
    while (Date.now() < fin) {
        try {
            const resultado = await operacion();
            if (resultado) return resultado;
        } catch {
            // El navegador puede estar arrancando.
        }
        await pausa(100);
    }
    throw new Error("El navegador no alcanzó el estado esperado.");
}

async function main() {
    const [chrome, salida, url = "http://127.0.0.1:3000/", ...idsSolicitados] = process.argv.slice(2);
    assert.ok(chrome && salida);
    const banco = JSON.parse(await fs.readFile(path.join(__dirname, "banco_evaluacion_50.json"), "utf8"));
    const carpeta = path.dirname(salida);
    const perfil = await fs.mkdtemp(path.join(os.tmpdir(), "ley1801-chat-"));
    const browser = spawn(chrome, [
        "--headless", "--disable-gpu", "--no-first-run", "--disable-background-networking",
        "--remote-debugging-port=0", `--user-data-dir=${perfil}`, "about:blank",
    ], { windowsHide: true, stdio: "ignore" });
    let socket;
    try {
        const puerto = (await esperar(() => fs.readFile(path.join(perfil, "DevToolsActivePort"), "utf8"))).split("\n")[0];
        const [pagina] = await (await fetch(`http://127.0.0.1:${puerto}/json/list`)).json();
        socket = new WebSocket(pagina.webSocketDebuggerUrl);
        await new Promise((resolve, reject) => {
            socket.addEventListener("open", resolve, { once: true });
            socket.addEventListener("error", reject, { once: true });
        });
        let siguiente = 0;
        const pendientes = new Map();
        socket.addEventListener("message", ({ data }) => {
            const mensaje = JSON.parse(data);
            if (!pendientes.has(mensaje.id)) return;
            const { resolve, reject } = pendientes.get(mensaje.id);
            pendientes.delete(mensaje.id);
            if (mensaje.error) reject(new Error(mensaje.error.message));
            else resolve(mensaje.result);
        });
        const cdp = (method, params = {}) => new Promise((resolve, reject) => {
            const id = ++siguiente;
            pendientes.set(id, { resolve, reject });
            socket.send(JSON.stringify({ id, method, params }));
        });
        const evaluar = async expression => {
            const resultado = await cdp("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true });
            if (resultado.exceptionDetails) throw new Error("Error al ejecutar el control DOM.");
            return resultado.result.value;
        };
        await cdp("Page.enable");
        await cdp("Emulation.setDeviceMetricsOverride", {
            width: 1280, height: 900, deviceScaleFactor: 1, mobile: false,
        });
        await cdp("Page.navigate", { url });
        await esperar(() => evaluar('document.querySelector("#estado-servidor")?.classList.contains("activo")'));
        const ids = idsSolicitados.length ? idsSolicitados : ["RAG-051", "RAG-044", "RAG-004", "RAG-026", "RAG-029"];
        const casos = ids.map(id => {
            const fila = banco.find(r => r.id === id);
            assert.ok(fila, id);
            return { id, pregunta: fila.pregunta };
        });
        casos.push({ id: "IMPUESTOS", pregunta: "¿Cuál es la multa por declarar renta tarde?" });
        const controles = [];
        for (const caso of casos) {
            const resultado = await evaluar(`(async () => {
                const selector = ".mensaje-asistente";
                const antes = document.querySelectorAll(selector).length;
                const errores = document.querySelectorAll(".mensaje-error").length;
                document.querySelector("#pregunta").value = ${JSON.stringify(caso.pregunta)};
                document.querySelector("#formulario-chat").requestSubmit();
                for (let i = 0; i < 1000; i++) {
                    const mensajes = document.querySelectorAll(selector);
                    const fallos = document.querySelectorAll(".mensaje-error");
                    if (fallos.length > errores) return {
                        respuesta: fallos[fallos.length - 1].textContent, error: true, citas: [], fuentes: [],
                    };
                    if (mensajes.length > antes) {
                        const actual = mensajes[mensajes.length - 1];
                        return {
                            respuesta: actual.querySelector("div")?.textContent || actual.textContent,
                            citas: [...actual.querySelectorAll("p strong")].map(e => e.textContent),
                            fuentes: [...actual.querySelectorAll("details section")].map(e => ({
                                fragmento: e.querySelector("blockquote")?.textContent,
                                url: e.querySelector("a")?.href,
                            })),
                            evidenciaPlegada: actual.querySelector("details")?.open === false,
                            anchoSinDesbordamiento: document.documentElement.scrollWidth <= innerWidth,
                            grupos: [...actual.querySelectorAll(".grupo-citas")].map(e => e.textContent),
                            inicioVisible: Math.abs(actual.getBoundingClientRect().top -
                                document.querySelector("#conversacion").getBoundingClientRect().top) < 32,
                        };
                    }
                    await new Promise(resolve => setTimeout(resolve, 100));
                }
                throw new Error("Consulta sin respuesta en navegador.");
            })()`);
            controles.push({ ...caso, ...resultado });
            if (caso.id === "RAG-044") {
                await evaluar(`(() => {
                    const resultado = [...document.querySelectorAll(".mensaje-asistente")].at(-1);
                    resultado.scrollIntoView({block: "start"});
                })()`);
                const captura = await cdp("Page.captureScreenshot", { format: "png" });
                await fs.writeFile(path.join(carpeta, path.basename(salida, ".json") + "_rag044.png"), Buffer.from(captura.data, "base64"), { flag: "wx" });
            }
        }
        const errorSimulado = await evaluar(`(async () => {
            const anterior = window.fetch;
            try {
                window.fetch = (ruta, ...args) => ruta === "/api/chat"
                    ? Promise.resolve(new Response(JSON.stringify({ error: "El motor documental no está disponible." }),
                        { status: 502, headers: { "Content-Type": "application/json" } }))
                    : anterior(ruta, ...args);
                await enviarPregunta(${JSON.stringify(banco.find(r => r.id === "RAG-025").pregunta)});
                const ultimo = document.querySelector("#conversacion").lastElementChild;
                return { mensaje: ultimo.textContent, clase: ultimo.className,
                    sinFuentes: !ultimo.querySelector("details, a, blockquote") };
            } finally {
                window.fetch = anterior;
            }
        })()`);
        const interfaz = await evaluar(`(() => {
            const conversacion = document.querySelector("#conversacion");
            const historial = conversacion.textContent.includes(${JSON.stringify(casos[0].pregunta)});
            const aviso = document.body.textContent.includes("Este asistente es informativo");
            const fuente = conversacion.querySelector(".fuentes-recuperadas");
            fuente?.querySelector("summary").click();
            const fragmentoVisible = Boolean(fuente?.open && fuente.querySelector("blockquote")?.checkVisibility());
            document.querySelector("#nuevo-chat").click();
            const reinicio = !conversacion.querySelector(".fuentes-recuperadas")
                && !conversacion.textContent.includes(${JSON.stringify(casos[0].pregunta)});
            const htmlSeguro = formatearRespuesta("<img src=x onerror=alert(1)>");
            return { historial, aviso, fragmentoVisible, reinicio,
                htmlSeguro: !htmlSeguro.querySelector("img") && htmlSeguro.textContent.includes("<img") };
        })()`);
        await fs.writeFile(salida, JSON.stringify({ url, controles, interfaz, errorSimulado }, null, 2) + "\n", { flag: "wx" });
    } finally {
        socket?.close();
        browser.kill();
    }
}

main().catch(error => {
    console.error(error.message);
    process.exitCode = 1;
});
