"""Servicio FastAPI para el chatbot jurídico RAG."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from motor_documental.generador_respuestas_rag import GeneradorRespuestasRAG
from motor_documental.salida_segura_rag import preparar_salida_publica


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
    return {"estado": "activo"}


@app.post("/consultar")
async def consultar(datos: Consulta):
    if not datos.pregunta.strip():
        raise HTTPException(
            status_code=400,
            detail="La pregunta no puede estar vacía."
        )

    try:
        resultado = await run_in_threadpool(
            generador.responder,
            datos.pregunta.strip()
        )
        return preparar_salida_publica(resultado)

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="No fue posible procesar la consulta."
        )
