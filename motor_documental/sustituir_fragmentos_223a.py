"""
Prepara la sustitución de fragmentos del artículo 223A
por numerales jurídicos completos.

Conserva la procedencia documental y las posiciones FAISS
cuando estas se encuentran disponibles.
"""

import json

from motor_documental.deduplicar_contexto_rag import (
    preparar_fragmentos_unicos
)

from motor_documental.expandir_contexto_rag import RUTA_FRAGMENTOS

from motor_documental.recuperar_numerales_223a import (
    recuperar_numerales_223a
)


def sustituir_fragmentos_223a(resultados_generales):

    if not isinstance(resultados_generales, list):
        raise TypeError(
            "Los resultados generales deben ser una lista."
        )

    with RUTA_FRAGMENTOS.open(encoding="utf-8") as archivo:
        corpus = json.load(archivo)

    fragmentos_articulo = [
        registro for registro in corpus
        if str(registro.get("numero_articulo", "")).upper() == "223A"
    ]

    por_id = {
        registro["id"]: registro
        for registro in fragmentos_articulo
    }

    fragmentos_conservados = []
    fragmentos_sustituidos = []
    semillas = []
    procedencias_directas = {}

    for resultado in resultados_generales:

        if str(resultado.get("articulo", "")).upper() != "223A":
            fragmentos_conservados.append(resultado)
            continue

        original = dict(resultado)
        fragmentos_sustituidos.append(original)

        identificador = original.get("id")
        origen = original.get("origen_recuperacion")

        # Resultado obtenido por título o número:
        # el ID general no corresponde a un fragmento FAISS.
        if (
            identificador not in por_id
            and origen == "titulo_numero"
        ):
            candidatos = fragmentos_articulo
            tipo = "TITULO_NUMERO"

        elif identificador in por_id:
            candidatos = [por_id[identificador]]
            tipo = (
                "TITULO_NUMERO"
                if origen == "titulo_numero"
                else "FAISS"
            )

        else:
            raise ValueError(
                f"Identificador 223A no reconocido: {identificador}"
            )

        for fragmento in candidatos:

            id_fragmento = fragmento["id"]

            if id_fragmento in procedencias_directas:
                continue

            semilla = dict(fragmento)

            posicion = original.get(
                "posicion_faiss"
            )

            semilla["posicion_faiss_original"] = (
                posicion if tipo == "FAISS" else None
            )

            semillas.append(semilla)

            procedencias_directas[id_fragmento] = {
                "tipo": tipo,
                "posicion": (
                    posicion if tipo == "FAISS" else None
                )
            }

    if semillas:

        fragmentos_expandidos = preparar_fragmentos_unicos(
            semillas,
            vecinos=8
        )

        for fragmento in fragmentos_expandidos:

            identificador = fragmento["id"]
            procedencia = procedencias_directas.get(
                identificador
            )

            if procedencia is not None:
                fragmento["tipo_recuperacion"] = (
                    procedencia["tipo"]
                )
                fragmento["posicion_faiss_original"] = (
                    procedencia["posicion"]
                )
            else:
                fragmento["tipo_recuperacion"] = "VECINO"
                fragmento["posicion_faiss_original"] = None

    else:
        fragmentos_expandidos = []

    numerales = recuperar_numerales_223a(
        fragmentos_expandidos
    )

    if semillas and not numerales:
        raise ValueError(
            "Se encontraron fragmentos del artículo 223A, "
            "pero no fue posible recuperar sus numerales."
        )

    for registro in numerales:

        origen = registro["fragmento_origen"]

        procedencia = procedencias_directas.get(origen)

        if procedencia is not None:
            registro["tipo_recuperacion"] = (
                procedencia["tipo"]
            )
            registro["posicion_faiss"] = (
                procedencia["posicion"]
            )
        else:
            registro["tipo_recuperacion"] = "VECINO"
            registro["posicion_faiss"] = None

    introduccion = (
        numerales[0]["introduccion"]
        if numerales
        else ""
    )

    return {
        "fragmentos_conservados": fragmentos_conservados,
        "fragmentos_sustituidos": fragmentos_sustituidos,
        "fragmentos_expandidos": fragmentos_expandidos,
        "numerales_223a": numerales,
        "introduccion_223a": introduccion
    }
