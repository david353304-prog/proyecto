from motor_documental.validador_respuestas_rag import ValidadorRespuestasRAG
from motor_documental.clasificador_tematico import clasificar_pregunta
import os
import time
import logging

from google import genai
from google.genai import types

from motor_documental.indice_publicable import RecuperadorPublicable
from motor_documental.preparar_contexto_rag import preparar_contexto
from motor_documental.instrucciones_ia import MARCADOR_SIN_RESPALDO, construir_mensajes
from motor_documental.vigencia_rag import (
    articulos_mencionados, articulos_para_consulta, contexto_publicable,
    respuesta_revision_pendiente, respuesta_texto_inexequible,
)


MODELO_GEMINI = "gemini-3.1-flash-lite"
logger = logging.getLogger(__name__)


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


class GeneradorRespuestasRAG:
    def __init__(self):
        if not os.environ.get("GEMINI_API_KEY"):
            raise RuntimeError(
                "No se encontró GEMINI_API_KEY en el entorno."
            )

        self.recuperador = RecuperadorPublicable()

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
        mensajes = construir_mensajes(pregunta, contexto, publicable=True)

        logger.warning("RAG contexto: %.2f s", time.perf_counter() - inicio_etapa)
        inicio_etapa = time.perf_counter()

        respuesta = self.cliente.models.generate_content(
            model=MODELO_GEMINI,
            contents=mensajes[1]["content"],
            config=types.GenerateContentConfig(
                system_instruction=mensajes[0]["content"],
                temperature=0.1,
                max_output_tokens=1200
            )
        )

        logger.warning("RAG Gemini: %.2f s", time.perf_counter() - inicio_etapa)
        inicio_etapa = time.perf_counter()

        texto_respuesta = (respuesta.text or "").strip()
        articulos_citados = articulos_mencionados(texto_respuesta)
        if (
            MARCADOR_SIN_RESPALDO in texto_respuesta
            or not articulos_citados
            or not articulos_citados <= {a["articulo"] for a in resultados["resultados_generales"]}
        ):
            return respuesta_sin_respaldo(pregunta, resultados)

        validacion_documental = ValidadorRespuestasRAG().validar(
            respuesta=texto_respuesta,
            contexto=contexto
        )


        logger.warning("RAG validación: %.2f s", time.perf_counter() - inicio_etapa)
        logger.warning("RAG TOTAL: %.2f s", time.perf_counter() - inicio_total)

        respuesta_visible = texto_respuesta

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
            "respuesta_original": texto_respuesta,
            "validacion_documental": validacion_documental,
            "modelo": MODELO_GEMINI,
            "total_generales": resultados["total_generales"],
            "total_estructurados": resultados["total_estructurados"],
            "resultados_recuperados": resultados
        }
