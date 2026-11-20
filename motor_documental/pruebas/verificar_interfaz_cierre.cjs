"use strict";

const assert = require("node:assert/strict");
const http = require("node:http");
const fs = require("node:fs/promises");
const os = require("node:os");
const path = require("node:path");
const { spawn } = require("node:child_process");

const frontend = path.resolve(__dirname, "../../frontend");
const fuente = "https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#5";
const guion = `
async function probar() {
    const pausa = () => new Promise(resolve => setTimeout(resolve, 25));
    async function espera(condicion) {
        for (let i = 0; i < 80; i++) {
            if (condicion()) return;
            await pausa();
        }
        throw new Error("La condición de interfaz no se cumplió.");
    }
    const conversacion = document.querySelector("#conversacion");
    await espera(() => document.querySelector("#estado-servidor").classList.contains("activo"));
    const sugerida = document.querySelector(".pregunta-sugerida");
    sugerida.click();
    await espera(() => conversacion.querySelector(".fuentes-recuperadas"));
    const respuestaSugerida = conversacion.textContent.includes(sugerida.dataset.pregunta);
    const campo = document.querySelector("#pregunta");
    campo.value = "Consulta libre de verificación";
    document.querySelector("#formulario-chat").requestSubmit();
    await espera(() => conversacion.querySelectorAll(".fuentes-recuperadas").length === 2);
    const libre = conversacion.textContent.includes("Consulta libre de verificación");
    const historial = conversacion.textContent.includes(sugerida.dataset.pregunta);
    const detalles = [...conversacion.querySelectorAll(".fuentes-recuperadas")];
    detalles.forEach(d => { d.open = true; });
    const fragmento = detalles.every(d => d.textContent.includes("interacción pacífica"));
    const enlace = detalles.every(d => [...d.querySelectorAll("a")].some(a => a.href === "${fuente}"));
    const aviso = document.body.textContent.includes("Este asistente es informativo");
    document.querySelector("#nuevo-chat").click();
    const reinicio = conversacion.textContent.includes("Nueva conversación")
        && !conversacion.querySelector(".fuentes-recuperadas") && campo.value === "";
    return { respuestaSugerida, libre, historial, fragmento, enlace, aviso, reinicio };
}
probar().then(resultado => {
    const marca = document.createElement("pre");
    marca.id = "resultado-auditoria";
    marca.textContent = JSON.stringify(resultado);
    document.body.appendChild(marca);
});
`;

async function main() {
    const [chrome, salida] = process.argv.slice(2);
    assert.ok(chrome && salida, "Uso: node verificar_interfaz_cierre.cjs CHROME SALIDA");
    const html = await fs.readFile(path.join(frontend, "index.html"), "utf8");
    const preguntas = [];
    const servidor = http.createServer(async (req, res) => {
        if (req.url === "/") {
            res.setHeader("Content-Type", "text/html; charset=utf-8");
            res.end(html.replace("</body>", '<script src="/prueba.js"></script></body>'));
            return;
        }
        if (req.url === "/api/estado" || req.url === "/api/chat") {
            res.setHeader("Content-Type", "application/json");
            if (req.url === "/api/estado") {
                res.end('{"estado":"activo"}');
                return;
            }
            let cuerpo = "";
            for await (const fragmento of req) cuerpo += fragmento;
            preguntas.push(JSON.parse(cuerpo).pregunta);
            res.end(JSON.stringify({
                respuesta: "**Artículo 5.** «La convivencia es la interacción pacífica.»",
                fuentes_recuperadas: [{
                    articulo: "5", titulo: "Definición", texto: "interacción pacífica",
                    url_fuente: fuente,
                }],
                validacion_documental: { estado: "PENDIENTE_VALIDACION" },
            }));
            return;
        }
        const recursos = {
            "/app.js": ["app.js", "text/javascript"], "/styles.css": ["styles.css", "text/css"],
        };
        if (req.url === "/prueba.js") {
            res.setHeader("Content-Type", "text/javascript; charset=utf-8");
            res.end(guion);
        } else if (recursos[req.url]) {
            const [archivo, tipo] = recursos[req.url];
            res.setHeader("Content-Type", tipo + "; charset=utf-8");
            res.end(await fs.readFile(path.join(frontend, archivo)));
        } else {
            res.writeHead(404).end();
        }
    });
    const perfil = await fs.mkdtemp(path.join(os.tmpdir(), "ley1801-navegador-"));
    try {
        await new Promise(resolve => servidor.listen(0, "127.0.0.1", resolve));
        const { port } = servidor.address();
        const browser = spawn(chrome, ["--headless", "--disable-gpu", "--disable-background-networking",
            "--no-first-run", "--dump-dom", "--virtual-time-budget=6000", `--user-data-dir=${perfil}`,
            `http://127.0.0.1:${port}/`], { windowsHide: true });
        let dom = "";
        browser.stdout.setEncoding("utf8").on("data", data => { dom += data; });
        browser.stderr.resume();
        const codigo = await new Promise((resolve, reject) => {
            browser.once("close", resolve);
            browser.once("error", reject);
        });
        assert.equal(codigo, 0);
        const resultado = JSON.parse(dom.match(/<pre id="resultado-auditoria">([^<]+)<\/pre>/)?.[1] || "{}");
        assert.equal(Object.keys(resultado).length, 7);
        assert.ok(Object.values(resultado).every(Boolean), JSON.stringify(resultado));
        assert.equal(preguntas.length, 2);
        await fs.writeFile(salida, JSON.stringify({
            metodo: "Chromium real, HTML y JavaScript del proyecto, respuestas HTTP simuladas",
            ...resultado,
        }, null, 2) + "\n");
    } finally {
        servidor.close();
    }
}

main().catch(error => {
    process.exitCode = 1;
    console.error(error.message);
});
