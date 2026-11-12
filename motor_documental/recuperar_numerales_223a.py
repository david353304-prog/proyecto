"""
Recupera numerales completos del artículo 223A a partir de
fragmentos encontrados por FAISS.

No verifica la vigencia normativa ni determina pertinencia jurídica.
"""

import json
from pathlib import Path


DIRECTORIO = Path(__file__).resolve().parent / "fragmentos"

RUTA_MAPA = DIRECTORIO / "mapa_fragmentos_numerales_223a.json"
RUTA_NUMERALES = DIRECTORIO / "articulo_223a_rag.json"


def recuperar_numerales_223a(resultados_generales):
    if not isinstance(resultados_generales, list):
        raise TypeError(
            "Los resultados generales deben ser una lista."
        )

    mapa = json.loads(
        RUTA_MAPA.read_text(encoding="utf-8")
    )

    registros = json.loads(
        RUTA_NUMERALES.read_text(encoding="utf-8")
    )

    por_numero = {
        registro["numeral"]: registro
        for registro in registros
    }

    recuperados = []
    numeros_vistos = set()

    for posicion, resultado in enumerate(resultados_generales, 1):
        identificador = resultado.get("id")

        if identificador not in mapa:
            continue

        for numero in mapa[identificador]:
            if numero in numeros_vistos:
                continue

            if numero not in por_numero:
                raise ValueError(
                    f"No existe el numeral {numero} en el JSON."
                )

            registro = dict(por_numero[numero])
            posicion_original = resultado.get(
                "posicion_faiss_original",
                posicion
            )

            registro["posicion_faiss"] = posicion_original
            registro["fragmento_origen"] = identificador

            recuperados.append(registro)
            numeros_vistos.add(numero)

    return recuperados
