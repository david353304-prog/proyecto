from motor_documental.validador_respuestas_rag import ValidadorRespuestasRAG
import os
import time
import logging

from google import genai
from google.genai import types

from motor_documental.recuperador_combinado_1801 import RecuperadorCombinado1801
from motor_documental.preparar_contexto_rag import preparar_contexto
from motor_documental.instrucciones_ia import construir_mensajes


MODELO_GEMINI = "gemini-3.1-flash-lite"
logger = logging.getLogger(__name__)


class GeneradorRespuestasRAG:
    def __init__(self):
        if not os.environ.get("GEMINI_API_KEY"):
            raise RuntimeError(
                "No se encontró GEMINI_API_KEY en el entorno."
            )

        self.recuperador = RecuperadorCombinado1801()

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

        inicio_total = time.perf_counter()
        inicio_etapa = time.perf_counter()

        resultados = self.recuperador.buscar(
            pregunta,
            cantidad_general=5,
            cantidad_estructurada=5
        )

        logger.warning("RAG recuperación: %.2f s", time.perf_counter() - inicio_etapa)
        inicio_etapa = time.perf_counter()

        contexto = preparar_contexto(
            resultados,
            modo_sustitucion_223a=True
        )
        mensajes = construir_mensajes(pregunta, contexto)

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

        texto_respuesta = respuesta.text

        if not texto_respuesta:
            texto_respuesta = (
                "No fue posible generar una respuesta "
                "con la información disponible."
            )

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
