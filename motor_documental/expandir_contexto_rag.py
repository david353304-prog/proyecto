import json
from pathlib import Path


RUTA_FRAGMENTOS = (
    Path(__file__).resolve().parent
    / "fragmentos"
    / "fragmentos_ley_1801.json"
)


def unir_fragmentos(fragmentos):
    """Une fragmentos consecutivos eliminando solapamientos exactos."""
    if not fragmentos:
        return ""

    palabras = fragmentos[0]["texto"].split()

    for fragmento in fragmentos[1:]:
        siguientes = fragmento["texto"].split()
        solapamiento = 0

        for cantidad in range(
            min(len(palabras), len(siguientes)),
            0,
            -1
        ):
            if palabras[-cantidad:] == siguientes[:cantidad]:
                solapamiento = cantidad
                break

        palabras.extend(siguientes[solapamiento:])

    return " ".join(palabras)


def expandir_contexto(id_fragmento, vecinos=1):
    """Recupera un fragmento y sus vecinos del mismo artículo."""
    if not isinstance(vecinos, int) or vecinos < 0:
        raise ValueError("vecinos debe ser un entero no negativo.")

    with RUTA_FRAGMENTOS.open("r", encoding="utf-8") as archivo:
        datos = json.load(archivo)

    posicion_central = next(
        (
            i for i, item in enumerate(datos)
            if item.get("id") == id_fragmento
        ),
        None
    )

    if posicion_central is None:
        raise ValueError(f"Fragmento no encontrado: {id_fragmento}")

    central = datos[posicion_central]
    articulo = str(central["numero_articulo"])

    fragmentos_articulo = [
        item for item in datos
        if str(item.get("numero_articulo")) == articulo
    ]

    indice = next(
        i for i, item in enumerate(fragmentos_articulo)
        if item["id"] == id_fragmento
    )

    inicio = max(0, indice - vecinos)
    fin = min(len(fragmentos_articulo), indice + vecinos + 1)

    seleccionados = fragmentos_articulo[inicio:fin]

    return {
        "articulo": articulo,
        "fragmento_central": id_fragmento,
        "fragmentos_incluidos": [
            item["id"] for item in seleccionados
        ],
        "texto_ampliado": unir_fragmentos(seleccionados)
    }
