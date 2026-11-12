"""Búsqueda complementaria por número y título de artículos."""

import json
import re
import unicodedata
from pathlib import Path


RUTA_CORPUS = (
    Path(__file__).resolve().parent
    / "corpus"
    / "articulos_ley_1801.json"
)

PALABRAS_COMUNES = {
    "que", "como", "cual", "cuales", "cuando",
    "donde", "para", "por", "con", "una", "uno",
    "unos", "unas", "del", "las", "los", "segun",
    "ley", "articulo", "articulos", "2016", "1801",
    "definicion", "define", "significa", "consiste",
    "es", "son", "un", "de", "la", "el", "en", "a",
    "y", "o", "se", "su", "al",
    "persona", "personas"
}

# Equivalencias para consultas coloquiales sobre convivencia.
# Los términos de destino se contrastan con el texto del corpus.
EXPANSIONES_JURIDICAS = {
    "pelea": (
        "renir",
        "confrontaciones violentas",
        "agresiones fisicas",
    ),
    "pelear": (
        "renir",
        "confrontaciones violentas",
        "agresiones fisicas",
    ),
    "rina": (
        "renir",
        "confrontaciones violentas",
    ),
    "rinas": (
        "renir",
        "confrontaciones violentas",
    ),
    "rinendo": (
        "renir",
        "confrontaciones violentas",
    ),
    "confrontacion": (
        "confrontaciones violentas",
        "renir",
    ),
    "confrontaciones": (
        "confrontaciones violentas",
        "renir",
    ),
    "agrede": (
        "agredir fisicamente",
        "agresiones fisicas",
    ),
    "agredir": (
        "agredir fisicamente",
        "agresiones fisicas",
    ),
    "agresion": (
        "agredir fisicamente",
        "agresiones fisicas",
    ),
    "agresiones": (
        "agredir fisicamente",
        "agresiones fisicas",
    ),
}



def normalizar(texto):
    texto = unicodedata.normalize("NFD", str(texto).lower())
    texto = "".join(
        caracter for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )
    return texto


def buscar_articulos_clave(pregunta, limite=5):
    if not isinstance(pregunta, str) or not pregunta.strip():
        raise ValueError("La pregunta debe ser un texto no vacío.")

    if not isinstance(limite, int) or limite < 1:
        raise ValueError("El límite debe ser un entero positivo.")

    with RUTA_CORPUS.open(encoding="utf-8") as archivo:
        articulos = json.load(archivo)

    pregunta_normalizada = normalizar(pregunta)

    palabras_pregunta = {
        palabra
        for palabra in re.findall(r"\b\w+\b", pregunta_normalizada)
        if palabra not in PALABRAS_COMUNES and len(palabra) > 2
    }

    numeros_mencionados = set(
        re.findall(
            r"\barticulo\s+(\d+[a-z]?)\b",
            pregunta_normalizada
        )
    )

    resultados = []

    for articulo in articulos:
        numero = str(articulo.get("numero", "")).strip()
        titulo = normalizar(articulo.get("titulo") or "")
        texto_articulo = normalizar(articulo.get("texto") or "")

        palabras_titulo = set(re.findall(r"\b\w+\b", titulo))
        palabras_titulo -= PALABRAS_COMUNES

        coincidencias_titulo = (
            palabras_pregunta & palabras_titulo
        )

        coincidencias_contenido = set()

        for palabra in palabras_pregunta:
            equivalencias = EXPANSIONES_JURIDICAS.get(
                palabra, ()
            )

            for expresion in equivalencias:
                if expresion in texto_articulo:
                    coincidencias_contenido.add(expresion)

        coincidencias = (
            coincidencias_titulo | coincidencias_contenido
        )

        puntuacion = (
            len(coincidencias_titulo) * 3
            + len(coincidencias_contenido) * 5
        )

        if normalizar(numero) in numeros_mencionados:
            puntuacion += 100

        if puntuacion > 0:
            resultados.append({
                "articulo": numero,
                "titulo": articulo.get("titulo"),
                "texto": articulo.get("texto"),
                "fuente": articulo.get("fuente"),
                "url_fuente": articulo.get("url_fuente"),
                "puntuacion": puntuacion,
                "coincidencias": sorted(coincidencias)
            })

    resultados.sort(
        key=lambda item: item["puntuacion"],
        reverse=True
    )

    return resultados[:limite]



def buscar_referencias_cruzadas(articulos_iniciales, limite=10):
    """
    Recupera referencias cruzadas pertenecientes a la misma ley
    del documento de origen.

    Excluye referencias identificadas expresamente como pertenecientes
    a otras leyes.
    """
    if not isinstance(articulos_iniciales, list):
        raise TypeError("Los artículos iniciales deben ser una lista.")

    if not isinstance(limite, int) or isinstance(limite, bool) or limite < 1:
        raise ValueError("El límite debe ser un entero positivo.")

    with RUTA_CORPUS.open(encoding="utf-8") as archivo:
        articulos_corpus = json.load(archivo)

    por_numero = {
        str(articulo.get("numero", "")).strip().upper(): articulo
        for articulo in articulos_corpus
    }

    iniciales = {
        str(articulo.get("articulo", "")).strip().upper()
        for articulo in articulos_iniciales
    }

    referencias = {}

    patron_articulo = re.compile(
        r"\barticulos?\s+(\d{1,3}[a-z]?)\b",
        re.I
    )

    patron_ley = re.compile(
        r"\bley\s+(\d+)\s+de\s+(\d{4})\b",
        re.I
    )

    patron_esta_ley = re.compile(
        r"\bde\s+(?:la\s+)?(?:esta|presente)\s+ley\b",
        re.I
    )

    for inicial in articulos_iniciales:

        numero_origen = str(
            inicial.get("articulo", "")
        ).strip().upper()

        texto = normalizar(inicial.get("texto", ""))

        fuente = normalizar(inicial.get("fuente", ""))

        ley_origen_match = patron_ley.search(fuente)

        if not ley_origen_match:
            continue

        ley_origen = (
            ley_origen_match.group(1),
            ley_origen_match.group(2)
        )

        for coincidencia in patron_articulo.finditer(texto):

            numero_referencia = coincidencia.group(1).upper()

            if numero_referencia in iniciales:
                continue

            if numero_referencia not in por_numero:
                continue

            # Examinar únicamente el texto inmediato de la referencia.
            cola = texto[coincidencia.end():]
            cola = re.split(r"[,.;:]", cola, maxsplit=1)[0]

            ley_explicita = patron_ley.search(cola)

            if ley_explicita:
                ley_referencia = (
                    ley_explicita.group(1),
                    ley_explicita.group(2)
                )

            elif patron_esta_ley.search(cola):
                ley_referencia = ley_origen

            else:
                # No asumir la pertenencia a una ley sin evidencia.
                continue

            if ley_referencia != ley_origen:
                continue

            if numero_referencia in referencias:
                continue

            documento = por_numero[numero_referencia]

            referencias[numero_referencia] = {
                "articulo": numero_referencia,
                "titulo": documento.get("titulo"),
                "texto": documento.get("texto"),
                "fuente": documento.get("fuente"),
                "url_fuente": documento.get("url_fuente"),
                "puntuacion": 0,
                "coincidencias": [],
                "origen_recuperacion": "referencia_cruzada",
                "referenciado_por": numero_origen,
                "ley_referencia": (
                    f"Ley {ley_referencia[0]} de "
                    f"{ley_referencia[1]}"
                )
            }

            if len(referencias) >= limite:
                return list(referencias.values())

    return list(referencias.values())
