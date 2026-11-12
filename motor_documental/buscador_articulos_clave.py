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
    "y", "o", "se", "su", "al"
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

        palabras_titulo = set(re.findall(r"\b\w+\b", titulo))
        palabras_titulo -= PALABRAS_COMUNES

        coincidencias = palabras_pregunta & palabras_titulo

        puntuacion = len(coincidencias) * 3

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
