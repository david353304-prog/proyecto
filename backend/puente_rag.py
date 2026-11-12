"""Puente entre el backend Node.js y el motor documental Python."""

import json
import sys
from pathlib import Path

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ_PROYECTO))

from motor_documental.salida_segura_rag import preparar_salida_publica


def procesar_pregunta(pregunta):
    """Procesa una pregunta utilizando el motor RAG."""

    if not isinstance(pregunta, str) or not pregunta.strip():
        raise ValueError("La pregunta debe ser un texto no vacío.")

    from motor_documental.generador_respuestas_rag import GeneradorRespuestasRAG

    generador = GeneradorRespuestasRAG()
    resultado_interno = generador.responder(pregunta.strip())

    return preparar_salida_publica(resultado_interno)


if __name__ == "__main__":
    try:
        datos = json.load(sys.stdin)
        respuesta = procesar_pregunta(datos.get("pregunta"))

        print(json.dumps(respuesta, ensure_ascii=False))

    except Exception:
        print(
            json.dumps(
                {
                    "error": "No fue posible procesar la consulta."
                },
                ensure_ascii=False
            )
        )
        sys.exit(1)
