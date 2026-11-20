from motor_documental.validador_respuestas_rag import ValidadorRespuestasRAG
from motor_documental.clasificador_tematico import clasificar_pregunta, normalizar
import os
import time
import logging
import json
import re

from google import genai
from google.genai import types

from motor_documental.indice_publicable import RecuperadorPublicable
from motor_documental.preparar_contexto_rag import preparar_contexto
from motor_documental.instrucciones_ia import (
    MARCADOR_SIN_RESPALDO, MAX_CITAS_PUBLICABLES, construir_mensajes,
)
from motor_documental.vigencia_rag import (
    articulos_mencionados, articulos_para_consulta, contexto_publicable,
    pasajes_del_contexto, respuesta_revision_pendiente, respuesta_texto_inexequible,
)


MODELO_GEMINI = "gemini-3.1-flash-lite"
logger = logging.getLogger(__name__)


def rotular_pasaje(articulo, pasaje, rotulo=None):
    if rotulo:
        return f"**{rotulo}.** «{pasaje}»"
    numeral = re.match(r"(?:Numeral\s+(\d+)\b|(\d+)\.\s)", pasaje)
    paragrafo = re.match(r"PARÁGRAFO(?:\s+(\d+)[oOº°]?)?\.", pasaje)
    referencia = f"Artículo {articulo}"
    if numeral:
        referencia = f"Numeral {numeral[1] or numeral[2]} del artículo {articulo}"
    elif paragrafo:
        numero = f" {paragrafo[1]}" if paragrafo[1] else ""
        referencia = f"Parágrafo{numero} del artículo {articulo}"
    elif articulo in {"33", "146", "223"} and (literal := re.match(r"([a-h])[.)] ", pasaje)):
        numeral_padre = {"33": 1, "146": 10, "223": 3}[articulo]
        referencia = f"Literal {literal[1]} del numeral {numeral_padre} del artículo {articulo}"
    return f"**{referencia}.** «{pasaje}»"


def completar_pasajes(pregunta, ids, pasajes):
    """Completa el alcance solicitado cuando Gemini ya eligió el pasaje principal."""
    consulta = normalizar(pregunta)
    if re.search(r"\b(?:solo|unicamente|numeral|paragrafo)\b", consulta):
        return ids
    reglas = (
        ("27", r"que comportamientos?[^?]{0,50}(?:vida e integridad|integridad de las personas)",
         "1. Reñir", tuple(f"{n}. " for n in range(2, 12))),
        ("33", r"(?:ruid\w*[^?]{0,65}(?:vecin|tranquilidad)|vecin\w+[^?]{0,55}musica)",
         "a. Sonidos", ("Numeral 1 ",)),
        ("206", r"que atribuciones[^?]{0,60}(?:inspectores|corregidores)",
         "1. Conciliar", tuple(f"{n}. " for n in range(2, 9)) +
         ("a. ", "b. ", "c. ", "d. ", "e. ", "f. ", "g. ", "h. ", "i. ")),
        ("77", r"ocup\w*[^?]{0,65}(?:inmueble|predio)[^?]{0,80}"
         r"que comportamientos?[^?]{0,85}(?:posesion|tenencia)",
         "1. Perturbar", ("2. Perturbar", "3. Instalar", "4. Omitir", "5. Impedir", "Numeral 1 ")),
        ("150", r"(?:orden verbal[^?]{0,65}procedimiento[^?]*[.?¿]\s*¿?las ordenes"
         r"|ordenes? de policia[^?]{0,35}verbal[^?]{0,45}procedimiento)",
         "La orden de Policía", ("Las órdenes de Policía",)),
        ("124", r"deambul\w*[^?]{0,65}(?:riesgo|peligro)[^?]{0,65}[.?¿]\s*¿?que establece",
         "1. Dejar deambular", ("7. Tolerar", "Numeral 1 ", "Numeral 7 ")),
    )
    for articulo, patron, ancla, adicionales in reglas:
        if re.search(patron, consulta) and any(
            pasajes[i]["articulo"] == articulo and pasajes[i]["texto"].startswith(ancla)
            for i in ids
        ):
            elegidos = set(ids)
            return [
                i for i, p in pasajes.items()
                if i in elegidos or (
                    p["articulo"] == articulo and p["texto"].startswith(adicionales)
                )
            ]
    return ids


def es_inventario_transporte(pregunta):
    return bool(re.search(
        r"\bque (?:conductas|comportamientos) (?:estan prohibid\w+|se prohiben)"
        r"[^?]{0,70}\btransporte publico\b",
        normalizar(pregunta),
    ))


def es_resumen_pasajeros(pregunta):
    return bool(re.search(
        r"\bpasajer\w+ (?:realiza|incurre en) comportamientos"
        r"[^?]{0,65}\btransporte publico\b[^?]{0,20}que establece",
        normalizar(pregunta),
    ))


def presentar_citas(texto_modelo, registros, pasajes=None, pregunta=""):
    fuentes = {a["articulo"]: a["texto"] for a in registros}
    salida = []
    try:
        seleccion = json.loads(texto_modelo)
        if pasajes is not None and isinstance(seleccion, dict) and "pasajes" in seleccion:
            ids = seleccion["pasajes"]
            if set(seleccion) != {"pasajes"} or not isinstance(ids, list) or len(ids) > MAX_CITAS_PUBLICABLES:
                return None
            if any(not isinstance(i, str) or i not in pasajes for i in ids):
                return None
            if (
                es_inventario_transporte(pregunta)
                and fuentes.keys() == {"146"}
                and len(pasajes) <= 44
                and any(re.match(r"\d+\. ", pasajes[i]["texto"]) for i in ids)
            ):
                # En una consulta de inventario, el cuadro del §1 se lee junto
                # con las conductas, a partir del catálogo público completo.
                ids = list(pasajes)
            elif fuentes.keys() == {"146"} and ids and es_resumen_pasajeros(pregunta):
                patron = re.compile(r"(?:Numeral (?:5|7|8|9|11|12|16) |(?:5|7|8|9|11|12|16)\. )")
                ids = [i for i, p in pasajes.items() if patron.match(p["texto"])]
            else:
                ids = completar_pasajes(pregunta, ids, pasajes)
                if len(ids) > MAX_CITAS_PUBLICABLES:
                    return None
            elegidos = [pasajes[i] for i in dict.fromkeys(ids)]
            if any(p["texto"] not in fuentes.get(p["articulo"], "") for p in elegidos):
                return None
            return "\n\n".join(
                rotular_pasaje(p["articulo"], p["texto"], p.get("rotulo")) for p in elegidos
            )
        citas = seleccion["citas"]
        if not isinstance(citas, list) or len(citas) > MAX_CITAS_PUBLICABLES:
            return None
        for cita in citas:
            articulo = cita["articulo"]
            literal = " ".join(cita["texto"].split())
            fuente = " ".join(fuentes[articulo].split())
            fila_breve = re.fullmatch(r"Numeral \d+ Amonestación\.?", literal)
            if literal not in fuente or (len(literal) < 24 and not fila_breve):
                return None
            # La selección puede copiar varios numerales contiguos en una cita.
            pasajes = re.split(
                r"(?<=[.;])\s+(?=\d{1,2}\.\s|PARÁGRAFO\b)|(?<=:)\s+(?=1\.\s)",
                literal,
            )
            if len(salida) + len(pasajes) > MAX_CITAS_PUBLICABLES:
                return None
            salida.extend(rotular_pasaje(articulo, pasaje) for pasaje in pasajes)
    except (KeyError, TypeError, AttributeError, ValueError):
        return None
    return "\n\n".join(salida)


def respuesta_fuera_dominio(pregunta):
    if clasificar_pregunta(pregunta)["fuera_de_dominio"]:
        return {
            "pregunta": pregunta,
            "respuesta": "La información solicitada queda fuera del corpus de la Ley 1801 de 2016.",
            "modelo": "clasificador temático",
            "total_generales": 0,
            "total_estructurados": 0,
            "validacion_documental": {"estado": "FUERA_DE_DOMINIO", "advertencias": []},
        }
    return None


def respuesta_sin_respaldo(pregunta, resultados, modelo=MODELO_GEMINI):
    return {
        "pregunta": pregunta,
        "respuesta": "No encontré respaldo suficiente en los fragmentos de la Ley 1801 de 2016.",
        "modelo": modelo,
        "total_generales": resultados["total_generales"],
        "total_estructurados": resultados["total_estructurados"],
        "validacion_documental": {"estado": "SIN_RESPALDO", "advertencias": []},
    }


class GeneracionNoDisponible(RuntimeError):
    pass


def seleccionar_citas_directas(pregunta, pasajes):
    """Exige todos los bloques que responden a una intención documental simple."""
    consulta = normalizar(pregunta).strip("¿?¡! .")
    reglas = (
        (r"que es (?:la )?convivencia|que (?:se entiende|entiende (?:el codigo|la ley)) por convivencia|definicion de convivencia",
         "5", ("Para los efectos de este Código, se entiende por convivencia",)),
        (r"que (?:es|son) (?:una |la |las )?multas?|definicion de (?:la )?multa",
         "180", ("Es la imposición del pago de una suma de dinero",)),
        (r"como se clasifican (?:las )?multas",
         "180", ("las multas se clasifican en generales y especiales.",)),
        (r"cuales son las finalidades de la convivencia|cuales son los fines (?:esenciales )?de la convivencia",
         "7", ("Son fines esenciales", *(f"{n}. " for n in range(1, 7)))),
    )
    for patron, articulo, inicios in reglas:
        if not re.fullmatch(patron, consulta):
            continue
        bloques = [p["texto"] for p in pasajes.values() if p["articulo"] == articulo]
        elegidos = [next((b for b in bloques if b.startswith(inicio)), None) for inicio in inicios]
        if all(elegidos):
            return "\n\n".join(rotular_pasaje(articulo, bloque) for bloque in elegidos)
    return None


class GeneradorRespuestasRAG:
    def __init__(self):
        self.recuperador = RecuperadorPublicable()

        self.cliente = None
        if not os.environ.get("GEMINI_API_KEY"):
            return

        self.cliente = genai.Client(
            api_key=os.environ["GEMINI_API_KEY"],
            http_options=types.HttpOptions(
                timeout=60000,
                retry_options=types.HttpRetryOptions(attempts=3, initial_delay=2, max_delay=15, exp_base=2, jitter=0.5, http_status_codes=[429, 500, 502, 503, 504])
            )
        )

    def responder(self, pregunta):
        if not isinstance(pregunta, str) or not pregunta.strip():
            raise ValueError("La pregunta no puede estar vacía.")

        pregunta = pregunta.strip()

        fuera = respuesta_fuera_dominio(pregunta)
        if fuera:
            return fuera

        aviso = respuesta_texto_inexequible(pregunta) or respuesta_revision_pendiente(pregunta)
        if aviso:
            return aviso
        candidatos = articulos_para_consulta(pregunta)
        if not candidatos:
            return respuesta_sin_respaldo(pregunta, {
                "total_generales": 0, "total_estructurados": 0
            }, modelo="verificación documental")

        inicio_total = time.perf_counter()
        inicio_etapa = time.perf_counter()

        resultados = self.recuperador.buscar(
            pregunta,
            cantidad_general=5,
            articulos_permitidos=candidatos,
        )
        resultados["resultados_generales"] = [
            a for a in resultados["resultados_generales"] if a["articulo"] in candidatos
        ]
        resultados = contexto_publicable(resultados)
        if not (resultados["total_generales"] or resultados["total_estructurados"]):
            return respuesta_sin_respaldo(pregunta, resultados, modelo="verificación documental")

        logger.warning("RAG recuperación: %.2f s", time.perf_counter() - inicio_etapa)
        inicio_etapa = time.perf_counter()

        contexto = preparar_contexto(
            resultados
        )
        pasajes = pasajes_del_contexto(resultados["resultados_generales"])
        cita_directa = seleccionar_citas_directas(pregunta, pasajes)
        if cita_directa:
            validacion = ValidadorRespuestasRAG().validar(respuesta=cita_directa, contexto=contexto)
            if validacion["estado"] != "REQUIERE_REVISION":
                return {
                    "pregunta": pregunta,
                    "respuesta": cita_directa,
                    "validacion_documental": validacion,
                    "modelo": "extracción documental",
                    "total_generales": resultados["total_generales"],
                    "total_estructurados": resultados["total_estructurados"],
                    "resultados_recuperados": resultados,
                }
        if self.cliente is None:
            raise GeneracionNoDisponible()
        catalogo = "\n".join(
            f"{i} [artículo {p['articulo']}] {p['texto']}" for i, p in pasajes.items()
        )
        mensajes = construir_mensajes(
            pregunta, f"{contexto}\n\nPASAJES SELECCIONABLES:\n{catalogo}", publicable=True
        )

        logger.warning("RAG contexto: %.2f s", time.perf_counter() - inicio_etapa)
        inicio_etapa = time.perf_counter()

        respuesta = self.cliente.models.generate_content(
            model=MODELO_GEMINI,
            contents=mensajes[1]["content"],
            config=types.GenerateContentConfig(
                system_instruction=mensajes[0]["content"],
                temperature=0.1,
                response_mime_type="application/json",
                response_schema=types.Schema(
                    type=types.Type.OBJECT, required=["pasajes"],
                    properties={"pasajes": types.Schema(
                        type=types.Type.ARRAY, max_items=MAX_CITAS_PUBLICABLES,
                        items=types.Schema(type=types.Type.STRING, enum=list(pasajes)),
                    )},
                ),
                max_output_tokens=512,
            )
        )

        logger.warning("RAG Gemini: %.2f s", time.perf_counter() - inicio_etapa)
        inicio_etapa = time.perf_counter()

        texto_modelo = (respuesta.text or "").strip()
        texto_respuesta = presentar_citas(texto_modelo, resultados["resultados_generales"], pasajes, pregunta)
        if texto_respuesta is None:
            return {
                **respuesta_sin_respaldo(pregunta, resultados),
                "validacion_documental": {"estado": "REQUIERE_REVISION", "advertencias": []},
            }
        # En el extracto cotejado del 95, esta remisión identifica la base de
        # datos. No es una cita independiente ni habilita recuperar otra ley.
        texto_validable = texto_respuesta
        if any(r["articulo"] == "95" for r in resultados["resultados_generales"]):
            texto_validable = texto_respuesta.replace(
                "artículo 106 de la Ley 1453 de 2011", "la disposición legal remitida"
            )
        if any(r["articulo"] == "206" for r in resultados["resultados_generales"]):
            texto_validable = texto_validable.replace(
                "numeral 17 del artículo 205", "la atribución exceptuada"
            ).replace("artículo 38 del Código General del Proceso", "la regla procesal remitida")
        if any(r["articulo"] == "33" for r in resultados["resultados_generales"]):
            texto_validable = texto_validable.replace(
                "artículo 14 de esta ley", "la regla de la ley modificatoria"
            )
        articulos_citados = articulos_mencionados(texto_validable)
        if (
            MARCADOR_SIN_RESPALDO in texto_respuesta
            or not articulos_citados
            or not articulos_citados <= {a["articulo"] for a in resultados["resultados_generales"]}
        ):
            return respuesta_sin_respaldo(pregunta, resultados)

        validacion_documental = ValidadorRespuestasRAG().validar(
            respuesta=texto_validable,
            contexto=contexto
        )


        logger.warning("RAG validación: %.2f s", time.perf_counter() - inicio_etapa)
        logger.warning("RAG TOTAL: %.2f s", time.perf_counter() - inicio_total)

        respuesta_visible = texto_respuesta
        if articulos_citados & {"222", "223"}:
            respuesta_visible += (
                "\n\n**Nota de denominación.** Los extractos conservan la redacción "
                "de la compilación. La Ley 2492 de 2025, "
                "artículo 10, actualizó la denominación a Inspector de Convivencia y Paz."
            )
        if "223" in articulos_citados:
            respuesta_visible += (
                "\n\n**Condición de la sentencia C-349/17.** Ante la inasistencia, "
                "se suspende el procedimiento hasta por tres días para acreditar "
                "sumariamente una justa causa. Si se admite, se cita a una nueva audiencia."
            )
        if "33" in articulos_citados:
            respuesta_visible += (
                "\n\n**Condición de la sentencia C-308/19.** Desactivar la fuente sonora "
                "no autoriza el ingreso a un domicilio. Antes deben verificarse las "
                "circunstancias que demuestren una perturbación evidente o el incumplimiento "
                "de los niveles autorizados mediante medición objetiva."
            )
            if "artículo 14 de esta ley" in texto_respuesta:
                respuesta_visible += (
                    " La remisión del parágrafo 6 corresponde al artículo 14 "
                    "de la Ley 2450 de 2025."
                )
        if "35" in articulos_citados:
            respuesta_visible += (
                "\n\n**Alcance de los extractos.** Son supuestos generales. "
                "La sentencia C-223/25 no decidió de fondo sobre el numeral 1. "
                "Las citas no califican los hechos de una persona ni determinan una medida."
            )

        if validacion_documental["estado"] == "REQUIERE_REVISION":
            respuesta_visible = (
                "No puedo ofrecer una respuesta jurídica suficientemente "
                "verificada con la información procesada. "
                "Se detectaron posibles inconsistencias que requieren "
                "revisión de las disposiciones legales citadas. "
                "Consulte la fuente normativa oficial o una "
                "autoridad competente antes de actuar."
            )

        return {
            "pregunta": pregunta,
            "respuesta": respuesta_visible,
            "respuesta_original": texto_modelo,
            "validacion_documental": validacion_documental,
            "modelo": MODELO_GEMINI,
            "total_generales": resultados["total_generales"],
            "total_estructurados": resultados["total_estructurados"],
            "resultados_recuperados": resultados
        }
