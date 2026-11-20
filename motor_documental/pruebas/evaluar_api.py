"""Mide el recorrido HTTP de Node a FastAPI con el banco del proyecto."""

import argparse
import hashlib
import json
from pathlib import Path
from statistics import median, quantiles
from time import perf_counter
from urllib.error import HTTPError
from urllib.request import Request, urlopen


CARPETA = Path(__file__).resolve().parent


def consultar(url, caso):
    solicitud = Request(
        url, data=json.dumps({"pregunta": caso["pregunta"]}).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    inicio = perf_counter()
    try:
        respuesta = urlopen(solicitud, timeout=125)
    except HTTPError as error:
        respuesta = error
    with respuesta:
        estado_http = respuesta.status
        datos = json.load(respuesta)
    segundos = round(perf_counter() - inicio, 6)
    estado = datos.get("validacion_documental", {}).get("estado")
    modelo = str(datos.get("modelo", ""))
    return {
        "id": caso["id"], "pregunta": caso["pregunta"], "http": estado_http,
        "segundos": segundos, "respuesta": datos,
        "llamada_gemini_confirmada": estado_http == 200 and modelo.startswith("gemini-"),
        "estado_documental": estado,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:3000/api/chat")
    parser.add_argument("--salida", type=Path, required=True)
    parser.add_argument("--solo-trampas", action="store_true")
    parser.add_argument("--estado-motor", help="URL de /estado del motor usado por Node")
    args = parser.parse_args()
    bytes_banco = (CARPETA / "banco_evaluacion_50.json").read_bytes()
    banco = json.loads(bytes_banco)
    estado_motor = None
    if args.estado_motor:
        from motor_documental.indice_publicable import huella_corpus

        with urlopen(args.estado_motor, timeout=15) as respuesta:
            estado_motor = json.load(respuesta)
        if estado_motor.get("sha256_corpus_publicable") != huella_corpus():
            parser.error("El motor HTTP no sirve el corpus público de este checkout.")
        if not estado_motor.get("generacion_configurada") and not args.solo_trampas:
            parser.error("El motor HTTP está activo pero Gemini no está configurado.")
    externo = json.loads((CARPETA / "banco_preguntas_fuera_dominio.json").read_text(encoding="utf-8"))
    trampas = [caso for caso in externo if caso["debe_ser_fuera_de_dominio"]]
    consultas = [consultar(args.url, caso) for caso in trampas]
    for fila in consultas:
        cuerpo = fila["respuesta"]
        fila["rechazo_sin_fuentes"] = (
            fila["http"] == 200
            and cuerpo.get("validacion_documental", {}).get("estado") == "FUERA_DE_DOMINIO"
            and cuerpo.get("fuentes_recuperadas") == []
        )

    mediciones = []
    if not args.solo_trampas:
        for caso in banco:
            fila = consultar(args.url, caso)
            fila["respuesta_referencia"] = caso["respuesta_referencia"]
            fila["articulos_esperados"] = caso["articulos_esperados"]
            mediciones.append(fila)
    exitosas = [f for f in mediciones if f["http"] == 200]
    # Un rechazo documental inmediato no mide el tiempo de generación.
    tiempos = [
        f["segundos"] for f in exitosas
        if f["llamada_gemini_confirmada"]
    ]
    resultado = {
        "url": args.url,
        "estado_motor": estado_motor,
        "sha256_banco": hashlib.sha256(bytes_banco).hexdigest(),
        "trampas": consultas,
        "trampas_rechazadas": sum(caso["rechazo_sin_fuentes"] for caso in consultas),
        "consultas_banco": mediciones,
        "consultas_banco_http_200": len(exitosas),
        "consultas_banco_generadas": len(tiempos),
        "min_banco_s": min(tiempos) if tiempos else None,
        "p50_banco_s": median(tiempos) if tiempos else None,
        "p95_banco_s": quantiles(tiempos, n=100, method="inclusive")[94] if len(tiempos) >= 2 else None,
        "banco_menos_de_10_s": sum(valor < 10 for valor in tiempos),
        "max_banco_s": max(tiempos) if tiempos else None,
    }
    args.salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
