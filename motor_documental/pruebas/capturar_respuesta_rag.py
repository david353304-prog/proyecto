"""Captura reproducible de respuestas del chatbot RAG."""

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from motor_documental.generador_respuestas_rag import (
    GeneradorRespuestasRAG,
)
from motor_documental.preparar_contexto_rag import (
    preparar_contexto,
)


CARPETA = Path(__file__).resolve().parent
RUTA_EVALUACION = CARPETA / "evaluacion_respuestas_50.json"


def capturar(identificador):
    if not os.environ.get("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY no configurada.")

    documento = json.loads(
        RUTA_EVALUACION.read_text(encoding="utf-8")
    )

    casos = [
        caso for caso in documento["resultados"]
        if caso["id"] == identificador
    ]

    if len(casos) != 1:
        raise ValueError("Identificador inexistente o duplicado.")

    caso = casos[0]

    if caso["respuesta_generada"] is not None:
        raise RuntimeError(
            "El caso ya tiene una respuesta registrada. "
            "No se sobrescribirá."
        )

    generador = GeneradorRespuestasRAG()

    # Se utiliza el método real del chatbot.
    resultado = generador.responder(caso["pregunta"])

    # La recuperación incluida en el resultado corresponde
    # a la misma ejecución que produjo la respuesta.
    recuperados = resultado["resultados_recuperados"]

    contexto = preparar_contexto(
        recuperados,
        modo_sustitucion_223a=True
    )

    validacion = resultado["validacion_documental"]

    caso["respuesta_generada"] = resultado["respuesta_original"]
    caso["respuesta_visible"] = resultado["respuesta"]
    caso["modelo"] = resultado["modelo"]
    caso["estado_validacion_documental"] = validacion["estado"]
    caso["advertencias_documentales"] = validacion.get(
        "advertencias", []
    )

    caso["contexto_utilizado"] = contexto
    caso["resultados_recuperados"] = recuperados
    caso["fecha_captura_utc"] = datetime.now(
        timezone.utc
    ).isoformat()

    caso["estado_evaluacion"] = "pendiente_revision_humana"

    # No se asignan calificaciones automáticamente.
    caso["exactitud"] = None
    caso["fidelidad_contexto"] = None
    caso["correccion_citas"] = None

    temporal = RUTA_EVALUACION.with_suffix(".json.tmp")

    temporal.write_text(
        json.dumps(
            documento,
            ensure_ascii=False,
            indent=2
        ) + "\n",
        encoding="utf-8"
    )

    temporal.replace(RUTA_EVALUACION)

    print("Caso capturado:", identificador)
    print("Modelo:", caso["modelo"])
    print("Validación:", caso["estado_validacion_documental"])
    print("Advertencias:", len(caso["advertencias_documentales"]))
    print("Evaluación humana: PENDIENTE")
    print("Respuesta y contexto guardados en la misma ejecución.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--id",
        required=True,
        help="Identificador de la pregunta, por ejemplo RAG-031"
    )

    argumentos = parser.parse_args()
    capturar(argumentos.id)
