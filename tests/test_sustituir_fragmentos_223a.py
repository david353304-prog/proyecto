import json

from motor_documental.expandir_contexto_rag import RUTA_FRAGMENTOS
from motor_documental.sustituir_fragmentos_223a import (
    sustituir_fragmentos_223a
)


def cargar_fragmentos_223a():
    with RUTA_FRAGMENTOS.open(encoding="utf-8") as archivo:
        corpus = json.load(archivo)

    return [
        f for f in corpus
        if str(f.get("numero_articulo", "")).upper() == "223A"
    ]


def test_recuperacion_por_titulo_numero():
    resultado = {
        "id": "articulo_223A",
        "articulo": "223A",
        "origen_recuperacion": "titulo_numero",
        "similitud": 1.0
    }

    salida = sustituir_fragmentos_223a([resultado])
    numerales = salida["numerales_223a"]

    assert len(numerales) == 10
    assert [n["numeral"] for n in numerales] == list(range(1, 11))

    assert all(
        n["tipo_recuperacion"] == "TITULO_NUMERO"
        for n in numerales
    )

    assert all(
        n["posicion_faiss"] is None
        for n in numerales
    )


def test_recuperacion_faiss_conserva_posicion():
    fragmentos = cargar_fragmentos_223a()
    primero = fragmentos[0]

    resultado = {
        "id": primero["id"],
        "articulo": "223A",
        "posicion_faiss": 818,
        "similitud": 0.95
    }

    salida = sustituir_fragmentos_223a([resultado])
    numerales = salida["numerales_223a"]

    assert len(numerales) == 10

    numeral_1 = next(
        n for n in numerales if n["numeral"] == 1
    )

    assert numeral_1["tipo_recuperacion"] == "FAISS"
    assert numeral_1["posicion_faiss"] == 818

    vecinos = [
        n for n in numerales
        if n["tipo_recuperacion"] == "VECINO"
    ]

    assert vecinos
    assert all(n["posicion_faiss"] is None for n in vecinos)


def test_multiples_fragmentos_faiss_conservan_posiciones():
    fragmentos = cargar_fragmentos_223a()

    seleccionados = [
        (fragmentos[0], 818),
        (fragmentos[2], 820),
        (fragmentos[6], 824)
    ]

    resultados = [
        {
            "id": fragmento["id"],
            "articulo": "223A",
            "posicion_faiss": posicion,
            "similitud": 0.95
        }
        for fragmento, posicion in seleccionados
    ]

    salida = sustituir_fragmentos_223a(resultados)
    numerales = salida["numerales_223a"]

    assert len(numerales) == 10

    esperados = {
        1: 818,
        3: 820,
        4: 820,
        9: 824
    }

    for numero, posicion in esperados.items():
        registro = next(
            n for n in numerales
            if n["numeral"] == numero
        )

        assert registro["tipo_recuperacion"] == "FAISS"
        assert registro["posicion_faiss"] == posicion


def test_no_se_pierden_numerales():
    fragmentos = cargar_fragmentos_223a()

    resultado = {
        "id": fragmentos[0]["id"],
        "articulo": "223A",
        "posicion_faiss": 818
    }

    salida = sustituir_fragmentos_223a([resultado])

    obtenidos = {
        n["numeral"]
        for n in salida["numerales_223a"]
    }

    assert obtenidos == set(range(1, 11))
