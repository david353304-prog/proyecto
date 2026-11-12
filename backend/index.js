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

    const temporizador = setTimeout(() => {
        proceso.kill();
    }, 120000);

    proceso.stdout.on("data", (datos) => {
        salida += datos.toString();
    });

    proceso.stderr.on("data", (datos) => {
        errores += datos.toString();
    });

    proceso.on("error", () => {
        clearTimeout(temporizador);
        if (!finalizado) {
            finalizado = true;
            res.status(500).json({
                error: "No fue posible iniciar el motor documental."
            });
        }
    });

    proceso.on("close", (codigo) => {
        clearTimeout(temporizador);

        if (finalizado) return;
        finalizado = true;

        if (codigo !== 0) {
            return res.status(500).json({
                error: "No fue posible procesar la consulta."
            });
        }

        try {
            const respuesta = JSON.parse(salida);
            return res.json(respuesta);
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
