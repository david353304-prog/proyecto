"""
Prepara la sustitución de fragmentos FAISS del artículo 223A
por numerales jurídicos completos.

Conserva la procedencia y las posiciones originales de FAISS.
No modifica los resultados originales ni verifica vigencia.
"""

from motor_documental.deduplicar_contexto_rag import (
    preparar_fragmentos_unicos
)

from motor_documental.recuperar_numerales_223a import (
    recuperar_numerales_223a
)


def sustituir_fragmentos_223a(resultados_generales):
    if not isinstance(resultados_generales, list):
        raise TypeError(
            "Los resultados generales deben ser una lista."
        )

    fragmentos_conservados = []
    fragmentos_sustituidos = []

    # 1. Separar resultados directos de FAISS.
    for posicion, resultado in enumerate(
        resultados_generales, 1
    ):
        if str(resultado.get("articulo", "")).upper() == "223A":
            copia = dict(resultado)
            copia["posicion_faiss_original"] = posicion
            fragmentos_sustituidos.append(copia)
        else:
            fragmentos_conservados.append(resultado)

    # 2. Expandir los fragmentos del artículo 223A.
    if fragmentos_sustituidos:
        posiciones_directas = {
            registro["id"]: registro["posicion_faiss_original"]
            for registro in fragmentos_sustituidos
        }

        fragmentos_expandidos = preparar_fragmentos_unicos(
            fragmentos_sustituidos,
            vecinos=8
        )

        # 3. Asignar procedencia sin inventar posiciones FAISS.
        for fragmento in fragmentos_expandidos:
            identificador = fragmento["id"]

            posicion_original = posiciones_directas.get(
                identificador
            )

            fragmento["posicion_faiss_original"] = (
                posicion_original
            )

            fragmento["tipo_recuperacion"] = (
                "FAISS"
                if posicion_original is not None
                else "VECINO"
            )

    else:
        fragmentos_expandidos = []

    # 4. Recuperar los numerales completos.
    numerales = recuperar_numerales_223a(
        fragmentos_expandidos
    )

    if fragmentos_sustituidos and not numerales:
        raise ValueError(
            "Se encontraron fragmentos del artículo 223A, "
            "pero no fue posible recuperar sus numerales."
        )

    # 5. Clasificar la procedencia de cada numeral.
    for registro in numerales:
        origen = registro["fragmento_origen"]

        registro["tipo_recuperacion"] = (
            "FAISS"
            if origen in posiciones_directas
            else "VECINO"
        )

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
