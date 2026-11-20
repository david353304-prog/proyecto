"""Servicio FastAPI para el chatbot jurídico RAG."""

from contextlib import asynccontextmanager
import logging

from motor_documental.cargar_entorno import cargar_entorno

cargar_entorno()

from fastapi import FastAPI, HTTPException
from google.genai.errors import APIError
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from motor_documental.generador_respuestas_rag import (
    GeneracionNoDisponible, GeneradorRespuestasRAG, respuesta_fuera_dominio, respuesta_sin_respaldo,
)
from motor_documental.salida_segura_rag import preparar_salida_publica
from motor_documental.indice_publicable import huella_corpus
from motor_documental.vigencia_rag import (
    articulos_para_consulta, respuesta_revision_pendiente, respuesta_texto_inexequible,
)


generador = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global generador
    generador = GeneradorRespuestasRAG()
    yield
    generador = None


app = FastAPI(
    title="Chatbot jurídico Ley 1801",
    lifespan=lifespan
)


class Consulta(BaseModel):
    pregunta: str = Field(min_length=1, max_length=2000)


@app.get("/estado")
def estado():
    return {
        "estado": "activo",
        "modo_respuesta": "citas_extractivas",
        "generacion_configurada": generador is not None and generador.cliente is not None,
        "sha256_corpus_publicable": huella_corpus(),
    }


@app.post("/consultar")
async def consultar(datos: Consulta):
    if not datos.pregunta.strip():
        raise HTTPException(
            status_code=400,
            detail="La pregunta no puede estar vacía."
        )

    if generador is None:
        pregunta = datos.pregunta.strip()
        respuesta = (
            respuesta_fuera_dominio(pregunta) or respuesta_texto_inexequible(pregunta)
            or respuesta_revision_pendiente(pregunta)
        )
        if respuesta:
            return preparar_salida_publica(respuesta)
        if not articulos_para_consulta(pregunta):
            return preparar_salida_publica(respuesta_sin_respaldo(
                pregunta, {"total_generales": 0, "total_estructurados": 0},
                modelo="verificación documental",
            ))
        raise HTTPException(status_code=503, detail="Generación sin configurar.")

    try:
        resultado = await run_in_threadpool(
            generador.responder,
            datos.pregunta.strip()
        )
        return preparar_salida_publica(resultado)

    except GeneracionNoDisponible:
        raise HTTPException(status_code=503, detail="Generación sin configurar.") from None
    except APIError as error:
        if error.code in {429, 503, 504}:
            logging.getLogger(__name__).warning("Generación externa indisponible: HTTP %s", error.code)
            raise HTTPException(status_code=503, detail="Servicio de generación temporalmente limitado o no disponible.") from None
        raise HTTPException(status_code=500, detail="No fue posible procesar la consulta.") from None
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="No fue posible procesar la consulta."
        )
