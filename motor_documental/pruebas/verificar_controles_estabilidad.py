"""Comprueba los pasajes necesarios en los dos controles HTTP de estabilidad."""

import argparse
import json
import re
from pathlib import Path

from motor_documental.vigencia_rag import corpus_publicable


CARPETA = Path(__file__).parent
CITAS = re.compile(r"\*\*(.+?)\.\*\* «([^»]+)»")
CASOS = {
    "RAG-035": ("77", ("1. ", "2. ", "5. ", "Numeral 1 ")),
    "RAG-041": ("124", ("1. ", "7. ", "Numeral 1 ", "Numeral 7 ")),
    "RAG-045": ("150", ("La orden de Policía", "Las órdenes de Policía")),
}
OPCIONALES = {
    "RAG-002": ("Con el fin",),
    "RAG-003": ("Son principios",),
    "RAG-009": ("Además",),
    "RAG-012": ("Son aquellos", "Numeral 4 ", "Numeral 5 "),
    "RAG-015": ("Los siguientes",),
    "RAG-016": ("PARÁGRAFO 2o.",),
    "RAG-031": ("Los siguientes",),
    "RAG-038": ("Los siguientes",),
    "RAG-040": ("3. ", "Numeral 3 "),
}


def verificar(primero, segundo, conservacion):
    base = json.loads((CARPETA / "comparacion_50_catalogo_final.json").read_bytes())
    corpus = corpus_publicable()
    completas = {
        fila["id"]: fila for fila in base["filas"]
        if fila["despues"]["calidad"] == "completa"
    }
    controles = []
    rondas = ((primero, set(CASOS)), (segundo, set(CASOS)), (conservacion, set(CASOS) | completas.keys()))
    for ronda, (control, esperados) in enumerate(rondas, 1):
        assert control["estado_motor"]["sha256_corpus_publicable"] == base["resumen"]["sha256_corpus"]
        assert {fila["id"] for fila in control["filas"]} == esperados
        for fila in control["filas"]:
            identificador = fila["id"]
            if ronda == 3 and identificador in CASOS:
                continue
            resultado = fila["respuesta"]
            visibles = resultado.get("fuentes_recuperadas", [])
            citas = CITAS.findall(resultado.get("respuesta", ""))
            if identificador in CASOS:
                articulo, prefijos = CASOS[identificador]
                faltantes = [
                    prefijo for prefijo in prefijos
                    if not any(texto.startswith(prefijo) for _, texto in citas)
                ]
            else:
                original = completas[identificador]
                articulo = original["articulo_esperado"]
                faltantes = [
                    cita["texto"] for cita in original["despues"]["citas"]
                    if not cita["texto"].startswith(OPCIONALES.get(identificador, ()))
                    and (cita["rotulo"], cita["texto"]) not in citas
                ]
            literal = bool(citas) and all(
                rotulo.endswith(f"rtículo {articulo}")
                and texto in corpus[articulo]["texto"]
                and any(f.get("articulo") == articulo and texto in f.get("texto", "")
                        for f in visibles)
                for rotulo, texto in citas
            )
            controles.append({
                "ronda": ronda,
                "id": identificador, "http": fila["http"], "segundos": fila["segundos"],
                "faltantes": faltantes, "citas_literales_y_visibles": literal,
                "pasa": fila["http"] == 200 and literal and not faltantes,
            })
    return {"controles": controles, "pasan": all(f["pasa"] for f in controles)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("primero", type=Path)
    parser.add_argument("segundo", type=Path)
    parser.add_argument("conservacion", type=Path)
    parser.add_argument("salida", type=Path)
    args = parser.parse_args()
    informe = verificar(*(json.loads(ruta.read_bytes()) for ruta in (
        args.primero, args.segundo, args.conservacion,
    )))
    with args.salida.open("x", encoding="utf-8") as archivo:
        json.dump(informe, archivo, ensure_ascii=False, indent=2)
        archivo.write("\n")
    raise SystemExit(0 if informe["pasan"] else 1)


if __name__ == "__main__":
    main()
