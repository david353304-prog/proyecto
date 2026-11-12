import json
from pathlib import Path

import faiss

from motor_documental.buscar_estructurado_135 import (
    BuscadorEstructurado135,
)


RAIZ = Path(__file__).resolve().parents[2]

PRUEBAS = [
    RAIZ / "motor_documental/pruebas/evaluacion_independiente_135.json",
    RAIZ / "motor_documental/pruebas/evaluacion_contraste_135.json",
]

EMBEDDINGS = RAIZ / "motor_documental/embeddings"


def cargar_preguntas():
    preguntas = []
    identificadores = set()

    for ruta in PRUEBAS:
        datos = json.loads(
            ruta.read_text(encoding="utf-8")
        )

        if not isinstance(datos, list):
            raise ValueError(
                f"El archivo debe contener una lista: {ruta}"
            )

        for prueba in datos:
            identificador = str(prueba["id"])

            if identificador in identificadores:
                raise ValueError(
                    f"Identificador duplicado: {identificador}"
                )

            identificadores.add(identificador)
            preguntas.append(prueba)

    return preguntas


def validar_indice(buscador, nombre):
    if buscador.indice.ntotal != len(buscador.metadatos):
        raise ValueError(
            f"{nombre}: índice y metadatos no coinciden"
        )

    if buscador.indice.d != buscador.modelo.get_embedding_dimension():
        raise ValueError(
            f"{nombre}: dimensión de embeddings incorrecta"
        )

    for metadata in buscador.metadatos:
        if metadata["id"] not in buscador.juridicos:
            raise ValueError(
                f"{nombre}: ID jurídico inexistente: {metadata['id']}"
            )


def evaluar(buscador, preguntas):
    resultados = {}
    metricas = {
        "top1": 0,
        "top3": 0,
        "top10": 0,
    }

    for prueba in preguntas:
        identificador = str(prueba["id"])
        esperado = str(prueba["numeral_esperado"])
        pregunta = prueba["pregunta"]

        encontrados = buscador.buscar(
            pregunta,
            cantidad=24,
        )

        numerales = [
            str(resultado["numeral"])
            for resultado in encontrados
        ]

        posicion = (
            numerales.index(esperado) + 1
            if esperado in numerales
            else None
        )

        if posicion is not None:
            if posicion <= 1:
                metricas["top1"] += 1
            if posicion <= 3:
                metricas["top3"] += 1
            if posicion <= 10:
                metricas["top10"] += 1

        resultados[identificador] = {
            "esperado": esperado,
            "posicion": posicion,
            "top3": numerales[:3],
        }

    return resultados, metricas


def imprimir_metricas(nombre, metricas, total):
    print(f"\n{nombre}")
    for clave in ("top1", "top3", "top10"):
        cantidad = metricas[clave]
        porcentaje = 100 * cantidad / total if total else 0
        print(
            f"  {clave.upper()}: "
            f"{cantidad}/{total} ({porcentaje:.1f}%)"
        )


def main():
    preguntas = cargar_preguntas()

    if not preguntas:
        raise ValueError("No hay preguntas de evaluación.")

    print("=== EVALUACIÓN AUTOMÁTICA ARTÍCULO 135 ===")
    print("Preguntas cargadas:", len(preguntas))

    original = BuscadorEstructurado135(
        modo="original"
    )

    experimental = BuscadorEstructurado135(
        modelo=original.modelo,
        modo="experimental",
    )

    validar_indice(original, "ORIGINAL")
    validar_indice(experimental, "EXPERIMENTAL")

    resultados_original, metricas_original = evaluar(
        original, preguntas
    )

    resultados_experimental, metricas_experimental = evaluar(
        experimental, preguntas
    )

    print("\n=== RESULTADOS POR PREGUNTA ===")

    mejoras = []
    regresiones = []
    iguales = []

    for prueba in preguntas:
        identificador = str(prueba["id"])

        anterior = resultados_original[identificador]
        nuevo = resultados_experimental[identificador]

        posicion_anterior = anterior["posicion"]
        posicion_nueva = nuevo["posicion"]

        print(
            f"{identificador} | "
            f"Numeral: {anterior['esperado']} | "
            f"Original: {posicion_anterior} | "
            f"Experimental: {posicion_nueva}"
        )

        rango_anterior = (
            posicion_anterior
            if posicion_anterior is not None
            else float("inf")
        )

        rango_nuevo = (
            posicion_nueva
            if posicion_nueva is not None
            else float("inf")
        )

        if rango_nuevo < rango_anterior:
            mejoras.append(identificador)
        elif rango_nuevo > rango_anterior:
            regresiones.append(identificador)
        else:
            iguales.append(identificador)

    total = len(preguntas)

    print("\n=== MÉTRICAS GENERALES ===")
    imprimir_metricas(
        "ORIGINAL", metricas_original, total
    )
    imprimir_metricas(
        "EXPERIMENTAL", metricas_experimental, total
    )

    print("\n=== COMPARACIÓN ===")
    print("Mejoras:", mejoras)
    print("Regresiones:", regresiones)
    print("Sin cambios:", len(iguales))

    print("\n=== CRITERIOS DE ACEPTACIÓN ===")

    condiciones = {
        "18 preguntas evaluadas": total == 18,
        "Sin regresiones": len(regresiones) == 0,
        "Top 1 experimental >= 15": (
            metricas_experimental["top1"] >= 15
        ),
        "Top 3 experimental = 18": (
            metricas_experimental["top3"] == 18
        ),
        "Top 10 experimental = 18": (
            metricas_experimental["top10"] == 18
        ),
    }

    for descripcion, cumplida in condiciones.items():
        estado = "CORRECTO" if cumplida else "FALLO"
        print(f"{descripcion}: {estado}")

    print("\n=== RESULTADO ===")

    if not all(condiciones.values()):
        print("EVALUACIÓN RECHAZADA")
        print("Se detectaron condiciones incumplidas.")
        raise SystemExit(1)

    print("EVALUACIÓN APROBADA")
    print("Todos los criterios de aceptación se cumplen.")
    print("Índices modificados: NO")
    print("Gemini utilizado: NO")
    print("Validación jurídica externa: PENDIENTE")


if __name__ == "__main__":
    main()
