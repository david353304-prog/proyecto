"""
Extrae los numerales del artículo 223A del corpus local.

Conserva el texto original sin corregir errores de extracción.
No verifica la vigencia normativa.
"""

import json
import re
from pathlib import Path


RUTA_ARTICULOS = (
    Path(__file__).resolve().parent
    / "corpus"
    / "articulos_ley_1801.json"
)


def extraer_numerales_223a():
    datos = json.loads(
        RUTA_ARTICULOS.read_text(encoding="utf-8")
    )

    articulos = (
        datos.get("articulos", [])
        if isinstance(datos, dict)
        else datos
    )

    coincidencias_articulo = [
        item
        for item in articulos
        if str(item.get("numero", "")).strip().upper() == "223A"
    ]

    if len(coincidencias_articulo) != 1:
        raise ValueError(
            "Se esperaba exactamente un artículo 223A."
        )

    articulo = coincidencias_articulo[0]
    texto = articulo["texto"]

    patron = re.compile(
        r"(?<!\d)(10|[1-9])\.\s*(?=[A-ZÁÉÍÓÚÑ])"
    )

    coincidencias = list(patron.finditer(texto))

    numeros = [
        int(coincidencia.group(1))
        for coincidencia in coincidencias
    ]

    if numeros != list(range(1, 11)):
        raise ValueError(
            f"Numeración inesperada: {numeros}"
        )

    introduccion = texto[:coincidencias[0].start()]
    numerales = []
    segmentos_originales = []

    for indice, coincidencia in enumerate(coincidencias):
        inicio = coincidencia.start()

        fin = (
            coincidencias[indice + 1].start()
            if indice + 1 < len(coincidencias)
            else len(texto)
        )

        segmento = texto[inicio:fin]
        segmentos_originales.append(segmento)

        numerales.append({
            "id": f"articulo_223A_numeral_{numeros[indice]}",
            "articulo": "223A",
            "numeral": numeros[indice],
            "introduccion": introduccion.strip(),
            "texto": segmento.strip(),
            "fuente": articulo.get("fuente"),
            "url_fuente": articulo.get("url_fuente"),
            "pagina_inicio": articulo.get("pagina_inicio"),
            "pagina_fin": articulo.get("pagina_fin")
        })

    reconstruido = introduccion + "".join(segmentos_originales)

    if reconstruido != texto:
        raise ValueError(
            "La separación modificó el texto original."
        )

    return numerales
