"""Mide coincidencias exactas de menciones en una muestra anotada fija."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from motor_documental.analisis.analisis_linguistico_corpus import (
    PATRONES_ENTIDADES, entidades_por_reglas,
)


def evaluar(muestra):
    filas = []
    conteo = {tipo: Counter(aciertos=0, falsos_positivos=0, omisiones=0)
              for tipo in PATRONES_ENTIDADES}
    for caso in muestra:
        diferencias = {}
        for tipo, patron in PATRONES_ENTIDADES.items():
            esperadas = Counter(caso["esperadas"].get(tipo, []))
            obtenidas = Counter(entidades_por_reglas(tipo, patron, caso["texto"]))
            falsos = list((obtenidas - esperadas).elements())
            omitidos = list((esperadas - obtenidas).elements())
            conteo[tipo].update(aciertos=sum((obtenidas & esperadas).values()),
                                falsos_positivos=len(falsos), omisiones=len(omitidos))
            diferencias[tipo] = {"esperadas": list(esperadas.elements()),
                                 "obtenidas": list(obtenidas.elements()),
                                 "falsos_positivos": falsos, "omisiones": omitidos}
        filas.append({"id": caso["id"], "entidades": diferencias})
    metricas = {}
    for tipo, valores in conteo.items():
        aciertos, falsos, omitidos = (valores[k] for k in ("aciertos", "falsos_positivos", "omisiones"))
        metricas[tipo] = {**valores,
                          "precision": aciertos / (aciertos + falsos) if aciertos + falsos else None,
                          "recall": aciertos / (aciertos + omitidos) if aciertos + omitidos else None}
    return {"metricas_por_entidad": metricas, "casos": filas}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, required=True)
    args = parser.parse_args()
    datos = Path(__file__).with_name("muestra_entidades.json").read_bytes()
    resultado = {"sha256_muestra": hashlib.sha256(datos).hexdigest(), **evaluar(json.loads(datos))}
    args.salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
