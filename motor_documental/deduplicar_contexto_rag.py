import json

from motor_documental.expandir_contexto_rag import RUTA_FRAGMENTOS


def preparar_fragmentos_unicos(resultados_generales, vecinos=1, max_resultados_expandir=None):
    """
    Expande y deduplica resultados generales de FAISS.

    Conserva la procedencia de cada fragmento y ordena
    los fragmentos según su posición en el corpus original.
    """
    if not isinstance(vecinos, int) or vecinos < 0:
        raise ValueError("vecinos debe ser un entero no negativo.")

    if max_resultados_expandir is not None:
        if (
            not isinstance(max_resultados_expandir, int)
            or max_resultados_expandir < 0
        ):
            raise ValueError(
                "max_resultados_expandir debe ser un entero no negativo o None."
            )

    with RUTA_FRAGMENTOS.open("r", encoding="utf-8") as archivo:
        corpus = json.load(archivo)

    por_id = {registro["id"]: registro for registro in corpus}
    posiciones = {
        registro["id"]: posicion
        for posicion, registro in enumerate(corpus)
    }

    unicos = {}

    for posicion_resultado, resultado in enumerate(
        resultados_generales, 1
    ):
        identificador = resultado.get("id")

        if identificador not in por_id:
            raise ValueError(
                f"Fragmento no encontrado: {identificador}"
            )

        central = por_id[identificador]
        articulo = str(central["numero_articulo"])

        fragmentos_articulo = [
            registro for registro in corpus
            if str(registro.get("numero_articulo")) == articulo
        ]

        indice = next(
            i for i, registro in enumerate(fragmentos_articulo)
            if registro["id"] == identificador
        )

        ampliar = (
            max_resultados_expandir is None
            or posicion_resultado <= max_resultados_expandir
        )

        vecinos_actuales = vecinos if ampliar else 0

        inicio = max(0, indice - vecinos_actuales)
        fin = min(
            len(fragmentos_articulo),
            indice + vecinos_actuales + 1
        )

        for fragmento in fragmentos_articulo[inicio:fin]:
            id_actual = fragmento["id"]

            if id_actual not in unicos:
                unicos[id_actual] = {
                    **fragmento,
                    "resultado_directo": False,
                    "recuperado_por": []
                }

            if posicion_resultado not in unicos[id_actual]["recuperado_por"]:
                unicos[id_actual]["recuperado_por"].append(
                    posicion_resultado
                )

            if id_actual == identificador:
                unicos[id_actual]["resultado_directo"] = True

    prioridad_articulos = {}

    for registro in unicos.values():
        articulo = str(registro["numero_articulo"])
        mejor_posicion = min(registro["recuperado_por"])

        if articulo not in prioridad_articulos:
            prioridad_articulos[articulo] = mejor_posicion
        else:
            prioridad_articulos[articulo] = min(
                prioridad_articulos[articulo],
                mejor_posicion
            )

    return sorted(
        unicos.values(),
        key=lambda registro: (
            prioridad_articulos[str(registro["numero_articulo"])],
            posiciones[registro["id"]]
        )
    )
