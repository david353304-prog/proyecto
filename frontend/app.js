"use strict";

// Elementos de la interfaz.
const conversacion = document.getElementById("conversacion");
const bienvenida = document.getElementById("bienvenida");
const formulario = document.getElementById("formulario-chat");
const campoPregunta = document.getElementById("pregunta");
const botonEnviar = document.getElementById("enviar");
const botonNuevo = document.getElementById("nuevo-chat");
const indicador = document.getElementById("indicador-procesamiento");
const estadoServidor = document.getElementById("estado-servidor");

let procesando = false;
let controladorSolicitud = null;
let identificadorConversacion = 0;


// Convierte Markdown básico en elementos seguros del navegador.
function formatearRespuesta(texto) {
    const contenedor = document.createElement("div");
    const lineas = String(texto).split(/\r?\n/);

    let lista = null;

    // Comprueba que la dirección utilice un protocolo web permitido.
    function obtenerURLSegura(direccion) {
        try {
            const url = new URL(direccion);

            if (url.protocol !== "https:" && url.protocol !== "http:") {
                return null;
            }

            return url.href;
        } catch {
            return null;
        }
    }

    // Convierte direcciones web en enlaces sin ejecutar HTML.
    function agregarEnlaces(destino, contenido) {
        const patron = /https?:\/\/[^\s<>"\]]+/g;
        let posicion = 0;

        for (const coincidencia of contenido.matchAll(patron)) {
            const indice = coincidencia.index;
            const direccionOriginal = coincidencia[0];
            const direccion = direccionOriginal.replace(/[.,;!?]+$/, "");
            const sobrante = direccionOriginal.slice(direccion.length);

            destino.appendChild(
                document.createTextNode(contenido.slice(posicion, indice))
            );

            const urlSegura = obtenerURLSegura(direccion);

            if (urlSegura) {
                const enlace = document.createElement("a");
                enlace.href = urlSegura;
                enlace.textContent = direccion;
                enlace.target = "_blank";
                enlace.rel = "noopener noreferrer";
                destino.appendChild(enlace);
            } else {
                destino.appendChild(document.createTextNode(direccion));
            }

            if (sobrante) {
                destino.appendChild(document.createTextNode(sobrante));
            }

            posicion = indice + direccionOriginal.length;
        }

        destino.appendChild(
            document.createTextNode(contenido.slice(posicion))
        );
    }

    // Reconoce negritas y enlaces Markdown sencillos.
    function agregarTextoFormateado(destino, contenido) {
        // Normaliza enlaces con un par adicional de corchetes.
        contenido = contenido.replace(
            /\[\[(https?:\/\/[^\]\s]+)\]\((https?:\/\/[^)\s]+)\)\]/g,
            (coincidencia, etiqueta, direccion) => {
                const urlEtiqueta = obtenerURLSegura(etiqueta);
                const urlDestino = obtenerURLSegura(direccion);

                if (urlEtiqueta && urlDestino && urlEtiqueta === urlDestino) {
                    return `[${etiqueta}](${direccion})`;
                }

                return coincidencia;
            }
        );
        const patron = /(\*\*[^*]+\*\*|\[[^\]]+\]\(https?:\/\/[^)\s]+\))/g;
        let posicion = 0;

        for (const coincidencia of contenido.matchAll(patron)) {
            agregarEnlaces(
                destino,
                contenido.slice(posicion, coincidencia.index)
            );

            const fragmento = coincidencia[0];

            if (fragmento.startsWith("**")) {
                const negrita = document.createElement("strong");

                agregarEnlaces(
                    negrita,
                    fragmento.slice(2, -2)
                );

                destino.appendChild(negrita);
            } else {
                const enlaceMarkdown = fragmento.match(
                    /^\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)$/
                );

                if (enlaceMarkdown) {
                    const urlSegura = obtenerURLSegura(enlaceMarkdown[2]);

                    if (urlSegura) {
                        const enlace = document.createElement("a");
                        enlace.href = urlSegura;
                        enlace.textContent = enlaceMarkdown[1];
                        enlace.target = "_blank";
                        enlace.rel = "noopener noreferrer";
                        destino.appendChild(enlace);
                    } else {
                        destino.appendChild(
                            document.createTextNode(fragmento)
                        );
                    }
                }
            }

            posicion = coincidencia.index + fragmento.length;
        }

        agregarEnlaces(destino, contenido.slice(posicion));
    }

    for (const linea of lineas) {
        const limpia = linea.trim();

        if (!limpia) {
            lista = null;
            continue;
        }

        if (/^(?:-{3,}|\*{3,}|(?:\\\*){3,})$/.test(limpia)) {
            lista = null;
            contenedor.appendChild(document.createElement("hr"));
            continue;
        }

        const encabezado = limpia.match(/^(#{1,4})\s+(.+)$/);

        if (encabezado) {
            lista = null;

            const nivel = Math.min(encabezado[1].length + 2, 6);
            const titulo = document.createElement(`h${nivel}`);

            agregarTextoFormateado(titulo, encabezado[2]);
            contenedor.appendChild(titulo);
            continue;
        }

        const elementoLista = limpia.match(/^[-*]\s+(.+)$/);

        if (elementoLista) {
            if (!lista) {
                lista = document.createElement("ul");
                contenedor.appendChild(lista);
            }

            const elemento = document.createElement("li");

            agregarTextoFormateado(elemento, elementoLista[1]);
            lista.appendChild(elemento);
            continue;
        }

        lista = null;

        const parrafo = document.createElement("p");
        agregarTextoFormateado(parrafo, limpia);
        contenedor.appendChild(parrafo);
    }

    return contenedor;
}

// Crea mensajes usando texto seguro, sin interpretar HTML.
function agregarMensaje(texto, tipo, validacion = null) {
    const mensaje = document.createElement("div");

    mensaje.classList.add("mensaje", `mensaje-${tipo}`);
    if (tipo === "asistente") {
        mensaje.appendChild(formatearRespuesta(texto));
    } else {
        mensaje.textContent = String(texto);
    }

    if (tipo === "asistente" && validacion) {
        const metadatos = document.createElement("div");
        metadatos.className = "metadatos-respuesta";

        const estado = validacion.estado || "NO DISPONIBLE";

        const nombresEstados = {
            PENDIENTE_VALIDACION: "Pendiente de revisión jurídica",
            REQUIERE_REVISION: "Requiere revisión jurídica",
            "NO DISPONIBLE": "Estado de revisión no disponible"
        };

        const estadoVisible = Object.prototype.hasOwnProperty.call(
            nombresEstados,
            estado
        )
            ? nombresEstados[estado]
            : `Estado no reconocido (${String(estado)})`;

        metadatos.textContent = `Validación documental: ${estadoVisible}`;

        const advertencias = Array.isArray(validacion.advertencias)
            ? validacion.advertencias
            : [];

        if (advertencias.length > 0) {
            const lista = document.createElement("div");
            lista.className = "lista-advertencias";

            const encabezado = document.createElement("p");
            encabezado.textContent =
                "Advertencias de la validación documental:";

            lista.appendChild(encabezado);

            advertencias.forEach((alerta) => {
                if (
                    !alerta ||
                    typeof alerta !== "object" ||
                    Array.isArray(alerta)
                ) {
                    return;
                }

                const elemento = document.createElement("div");
                elemento.className = "advertencia-individual";

                const tipo = document.createElement("strong");
                tipo.textContent =
                    alerta.tipo || "Advertencia documental";

                elemento.appendChild(tipo);

                if (alerta.detalle) {
                    const detalle = document.createElement("p");
                    detalle.textContent = alerta.detalle;
                    elemento.appendChild(detalle);
                }

                if (
                    typeof alerta.fragmento === "string" &&
                    alerta.fragmento.trim()
                ) {
                    const etiqueta = document.createElement("p");
                    etiqueta.textContent = "Fragmento detectado:";

                    const fragmento = document.createElement("blockquote");
                    fragmento.textContent = alerta.fragmento;

                    elemento.appendChild(etiqueta);
                    elemento.appendChild(fragmento);
                }

                lista.appendChild(elemento);
            });

            metadatos.appendChild(lista);
        }
        mensaje.appendChild(metadatos);
    }

    conversacion.appendChild(mensaje);
    conversacion.scrollTop = conversacion.scrollHeight;
}

// Activa o desactiva el indicador de procesamiento.
function establecerProcesamiento(valor) {
    procesando = valor;

    botonEnviar.disabled = valor;
    campoPregunta.disabled = valor;
    indicador.hidden = !valor;

    botonEnviar.textContent = valor ? "Procesando..." : "Enviar";
}

// Consulta el estado del backend.
async function verificarServidor() {
    try {
        const respuesta = await fetch("/api/estado");

        if (!respuesta.ok) {
            throw new Error("Servidor no disponible");
        }

        const datos = await respuesta.json();

        if (datos.estado !== "activo") {
            throw new Error("Servidor no activo");
        }

        estadoServidor.textContent = "Servidor conectado";
        estadoServidor.className = "estado activo";
    } catch {
        estadoServidor.textContent = "Servidor desconectado";
        estadoServidor.className = "estado error";
    }
}

// Envía una pregunta al motor RAG.
async function enviarPregunta(pregunta) {
    const texto = String(pregunta).trim();

    if (!texto || procesando) {
        return;
    }

    if (texto.length > 2000) {
        agregarMensaje(
            "La pregunta supera el límite de 2000 caracteres.",
            "error"
        );
        return;
    }

    if (bienvenida && bienvenida.isConnected) {
        bienvenida.remove();
    }

    agregarMensaje(texto, "usuario");
    campoPregunta.value = "";

    establecerProcesamiento(true);

    const conversacionActual = identificadorConversacion;
    const controlador = new AbortController();
    controladorSolicitud = controlador;

    try {
        const respuesta = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                pregunta: texto
            }),
            signal: controlador.signal
        });

        const datos = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(
                datos.error || "No fue posible procesar la pregunta."
            );
        }

        if (conversacionActual !== identificadorConversacion) {
            return;
        }

        if (typeof datos.respuesta !== "string") {
            throw new Error("El servidor devolvió una respuesta inválida.");
        }

        agregarMensaje(
            datos.respuesta,
            "asistente",
            datos.validacion_documental
        );
    } catch (error) {
        if (
            error.name !== "AbortError" &&
            conversacionActual === identificadorConversacion
        ) {
            agregarMensaje(
                error.message || "Ocurrió un error inesperado.",
                "error"
            );
        }
    } finally {
        if (controladorSolicitud === controlador) {
            controladorSolicitud = null;
        }

        if (conversacionActual === identificadorConversacion) {
            establecerProcesamiento(false);
            campoPregunta.focus();
        }
    }
}

// Procesa el formulario.
formulario.addEventListener("submit", (evento) => {
    evento.preventDefault();
    enviarPregunta(campoPregunta.value);
});

// Enter envía; Shift + Enter permite un salto de línea.
campoPregunta.addEventListener("keydown", (evento) => {
    if (evento.key === "Enter" && !evento.shiftKey) {
        evento.preventDefault();

        if (!procesando) {
            formulario.requestSubmit();
        }
    }
});

// Permite usar las preguntas sugeridas.
document.querySelectorAll(".pregunta-sugerida").forEach((boton) => {
    boton.addEventListener("click", () => {
        enviarPregunta(boton.dataset.pregunta || "");
    });
});

// Inicia una nueva conversación visual.
botonNuevo.addEventListener("click", () => {
    identificadorConversacion += 1;

    if (controladorSolicitud) {
        controladorSolicitud.abort();
        controladorSolicitud = null;
    }

    establecerProcesamiento(false);

    conversacion.replaceChildren();

    const inicio = document.createElement("div");
    inicio.className = "bienvenida";

    const titulo = document.createElement("h2");
    titulo.textContent = "Nueva conversación";

    const descripcion = document.createElement("p");
    descripcion.textContent =
        "Escribe una pregunta sobre la Ley 1801 de 2016 para comenzar.";

    inicio.append(titulo, descripcion);
    conversacion.appendChild(inicio);

    campoPregunta.value = "";
    campoPregunta.focus();
});

// Comprueba la conexión cuando carga la página.
verificarServidor();
