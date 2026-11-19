"""Mide el recorrido HTTP de Node a FastAPI con el banco del proyecto."""

import argparse
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
    return {
        "id": caso["id"], "pregunta": caso["pregunta"], "http": estado_http,
        "segundos": segundos, "respuesta": datos,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:3000/api/chat")
    parser.add_argument("--salida", type=Path, required=True)
    parser.add_argument("--solo-trampas", action="store_true")
    args = parser.parse_args()
    banco = json.loads((CARPETA / "banco_evaluacion_50.json").read_text(encoding="utf-8"))
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
    tiempos = [f["segundos"] for f in mediciones if f["http"] == 200]
    resultado = {
        "url": args.url,
        "trampas": consultas,
        "trampas_rechazadas": sum(caso["rechazo_sin_fuentes"] for caso in consultas),
        "consultas_banco": mediciones,
        "consultas_banco_http_200": len(tiempos),
        "p50_banco_s": median(tiempos) if tiempos else None,
        "p95_banco_s": quantiles(tiempos, n=100, method="inclusive")[94] if len(tiempos) >= 2 else None,
        "banco_menos_de_10_s": sum(valor < 10 for valor in tiempos),
    }
    args.salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
