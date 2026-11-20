"""Motor de evaluación con telemetría HTTP de Gemini sin contenido de solicitudes."""

import itertools
import hashlib
import json
import os
import re
from contextvars import ContextVar
from contextlib import ExitStack
from functools import wraps
from time import perf_counter
from unittest.mock import patch

import httpx
import uvicorn
from google.genai import errors, models
from google.genai._api_client import BaseApiClient
from motor_documental import generador_respuestas_rag as rag


CONSULTA = ContextVar("consulta_diagnostico", default=None)


def registrar(**datos):
    print("DIAGNOSTICO_GEMINI " + json.dumps({"consulta": CONSULTA.get(), **datos}), flush=True)


def clasificar_error(error):
    if isinstance(error, httpx.TimeoutException):
        return "timeout"
    if isinstance(error, httpx.TransportError):
        return "transporte"
    if isinstance(error, errors.APIError):
        return "limite_o_cuota" if error.code == 429 else "http_proveedor"
    if isinstance(error, (ValueError, UnicodeError)):
        return "datos_invalidos"
    return "otra_excepcion"


def medir_etapa(nombre, funcion, resumen=None):
    @wraps(funcion)
    def medida(*args, **kwargs):
        inicio = perf_counter()
        try:
            resultado = funcion(*args, **kwargs)
        except Exception as error:
            codigo = getattr(error, "code", None)
            registrar(evento=nombre, segundos=round(perf_counter() - inicio, 6),
                      error=type(error).__name__, categoria=clasificar_error(error),
                      http_proveedor=codigo if isinstance(codigo, int) else None)
            raise
        registrar(evento=nombre, segundos=round(perf_counter() - inicio, 6),
                  **(resumen(resultado) if resumen else {}))
        return resultado
    return medida


def medir_seleccion(funcion):
    @wraps(funcion)
    def seleccion(texto_modelo, registros, *args, **kwargs):
        inicio = perf_counter()
        resultado = funcion(texto_modelo, registros, *args, **kwargs)
        datos = {}
        if resultado is None or args:
            try:
                seleccion = json.loads(texto_modelo)
                if "pasajes" in seleccion:
                    ids = seleccion["pasajes"]
                    catalogo = args[0] if args else {}
                    datos = {"seleccion_por_id": True, "cantidad": len(ids),
                             "todos_en_catalogo": all(isinstance(i, str) and i in catalogo for i in ids),
                             "catalogo": list(catalogo),
                             "ids": [i if isinstance(i, str) and re.fullmatch(r"P?\d{1,4}", i)
                                     else "<formato inválido>" for i in ids]}
                else:
                    citas = seleccion["citas"]
                    fuentes = {a["articulo"]: " ".join(a["texto"].split()) for a in registros}
                    datos = {"cantidad": len(citas), "citas": [
                        {"articulo_en_contexto": c.get("articulo") in fuentes,
                         "caracteres": len(c.get("texto", "")),
                         "literal": bool(c.get("texto")) and " ".join(c["texto"].split())
                         in fuentes.get(c.get("articulo"), "")}
                        for c in citas
                    ]}
            except (KeyError, TypeError, ValueError, AttributeError):
                datos = {"seleccion_malformada_o_sin_citas_literales": True}
        registrar(evento="seleccion_citas", segundos=round(perf_counter() - inicio, 6),
                  aceptada=resultado is not None, **datos)
        return resultado
    return seleccion


def main():
    ids = itertools.count(1)

    from backend.servicio_rag import app

    @app.middleware("http")
    async def medir_consulta(solicitud, continuar):
        if solicitud.url.path != "/consultar":
            return await continuar(solicitud)
        token = CONSULTA.set(next(ids))
        try:
            registrar(evento="inicio")
            respuesta = await continuar(solicitud)
            registrar(evento="fin", http=respuesta.status_code)
            return respuesta
        finally:
            CONSULTA.reset(token)

    etapas = (
        (BaseApiClient, "_request_once", "intento", None),
        (models.Models, "generate_content", "generacion", None),
        (rag.RecuperadorPublicable, "buscar", "recuperacion", None),
        (rag, "preparar_contexto", "contexto",
         lambda texto: {"sha256": hashlib.sha256(texto.encode("utf-8")).hexdigest()}),
        (rag.ValidadorRespuestasRAG, "validar", "validacion",
         lambda resultado: {"estado": resultado["estado"]}),
    )
    with ExitStack() as stack:
        stack.enter_context(patch.object(rag, "presentar_citas", medir_seleccion(rag.presentar_citas)))
        for objeto, atributo, evento, resumen in etapas:
            stack.enter_context(patch.object(objeto, atributo, medir_etapa(
                evento, getattr(objeto, atributo), resumen,
            )))
        uvicorn.run(app, host="127.0.0.1",
                    port=int(os.environ.get("FASTAPI_PORT", "8598")), access_log=False)


if __name__ == "__main__":
    main()
