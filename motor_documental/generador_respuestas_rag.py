from motor_documental.validador_respuestas_rag import ValidadorRespuestasRAG
import os

from google import genai
from google.genai import types

from motor_documental.recuperador_combinado_1801 import RecuperadorCombinado1801
from motor_documental.preparar_contexto_rag import preparar_contexto
from motor_documental.instrucciones_ia import construir_mensajes


MODELO_GEMINI = "gemini-3.1-flash-lite"


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
                timeout=20000,
                retry_options=types.HttpRetryOptions(attempts=1)
            )
        )

    def responder(self, pregunta):
        if not isinstance(pregunta, str) or not pregunta.strip():
            raise ValueError("La pregunta no puede estar vacía.")

        pregunta = pregunta.strip()

        resultados = self.recuperador.buscar(
            pregunta,
            cantidad_general=5,
            cantidad_estructurada=5
        )

        contexto = preparar_contexto(
            resultados,
            modo_sustitucion_223a=True
        )
        mensajes = construir_mensajes(pregunta, contexto)

        respuesta = self.cliente.models.generate_content(
            model=MODELO_GEMINI,
            contents=mensajes[1]["content"],
            config=types.GenerateContentConfig(
                system_instruction=mensajes[0]["content"],
                temperature=0.1,
                max_output_tokens=1200
            )
        )

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
