"""Evaluación documental del recuperador combinado de la Ley 1801."""

import json
from pathlib import Path
from collections import Counter

from motor_documental.recuperador_combinado_1801 import (
    RecuperadorCombinado1801,
)

BASE = Path(__file__).resolve().parents[2]

RUTA_BANCO = (
    BASE / "motor_documental/pruebas/banco_evaluacion_50.json"
)

RUTA_SALIDA = (
    BASE
    / "motor_documental/pruebas/evaluacion_recuperacion_50_resultados.json"
)

K_VALORES = (1, 3, 5, 10, 20, 50)


def normalizar_articulo(valor):
    return str(valor).strip().upper()


def cargar_banco():
    banco = json.loads(
        RUTA_BANCO.read_text(encoding="utf-8")
    )

    if not isinstance(banco, list) or len(banco) != 50:
        raise ValueError("El banco debe contener 50 preguntas.")

    ids = [p["id"] for p in banco]

    if len(set(ids)) != len(ids):
        raise ValueError("Hay identificadores duplicados.")

    for p in banco:
        if not p.get("pregunta", "").strip():
            raise ValueError(f"Pregunta vacía: {p['id']}")

        if not p.get("articulos_esperados"):
            raise ValueError(f"Sin artículos esperados: {p['id']}")

        if not p.get("respuesta_referencia", "").strip():
            raise ValueError(f"Sin respuesta de referencia: {p['id']}")

    return banco


def extraer_articulos(resultados):
    """Obtiene artículos únicos respetando el orden de recuperación."""

    articulos = []

    for resultado in resultados:
        numero = resultado.get(
            "articulo",
            resultado.get("numero_articulo")
        )

        if numero is None:
            continue

        numero = normalizar_articulo(numero)

        if numero not in articulos:
            articulos.append(numero)

    return articulos


def calcular_metricas(registros):
    total = len(registros)
    metricas = {}

    for k in K_VALORES:
        aciertos = 0
        recall_acumulado = 0.0
        precision_acumulada = 0.0

        for registro in registros:
            esperados = set(registro["esperados"])
            recuperados = set(registro["recuperados"][:k])

            interseccion = esperados & recuperados

            if interseccion:
                aciertos += 1

            recall_acumulado += (
                len(interseccion) / len(esperados)
            )

            precision_acumulada += (
                len(interseccion) / k
            )

        metricas[f"precision_at_{k}"] = round(
            precision_acumulada / total, 4
        )

        metricas[f"hit_at_{k}"] = round(
            aciertos / total, 4
        )

        metricas[f"recall_at_{k}"] = round(
            recall_acumulado / total, 4
        )

    suma_rr = 0.0

    for registro in registros:
        esperados = set(registro["esperados"])

        posicion = next(
            (
                i
                for i, articulo in enumerate(
                    registro["recuperados"], start=1
                )
                if articulo in esperados
            ),
            None
        )

        registro["primera_posicion_relevante"] = posicion

        if posicion is not None:
            suma_rr += 1 / posicion

    metricas["mrr"] = round(suma_rr / total, 4)

    return metricas


def main():
    print("=== EVALUACION DEL RECUPERADOR RAG ===")

    banco = cargar_banco()

    print("Preguntas:", len(banco))
    print("Inicializando recuperador combinado...")

    recuperador = RecuperadorCombinado1801(
        modo_135="original"
    )

    registros = []

    for indice, prueba in enumerate(banco, start=1):
        resultados = recuperador.buscar(
            prueba["pregunta"],
            cantidad_general=50,
            cantidad_estructurada=10,
        )

        esperados = sorted({
            normalizar_articulo(a)
            for a in prueba["articulos_esperados"]
        })

        recuperados = extraer_articulos(
            resultados["resultados_generales"]
        )

        estructurados = resultados[
            "resultados_estructurados_135"
        ]

        registro = {
            "id": prueba["id"],
            "pregunta": prueba["pregunta"],
            "articulos_esperados": esperados,
            "articulos_recuperados": recuperados,
            "numerales_estructurados_135": [
                str(r.get("numeral"))
                for r in estructurados
            ],
        }

        registro["esperados"] = esperados
        registro["recuperados"] = recuperados

        registros.append(registro)

        encontrados = set(esperados) & set(recuperados)

        print(
            f"[{indice:02d}/50] {prueba['id']} | "
            f"Esperados: {esperados} | "
            f"Encontrados: {sorted(encontrados)}"
        )

    metricas = calcular_metricas(registros)

    print("\n=== METRICAS GENERALES ===")

    for nombre, valor in metricas.items():
        print(f"{nombre}: {valor:.4f}")

    print("\n=== RESULTADOS DE COBERTURA ===")

    total_aciertos = sum(
        bool(set(r["esperados"]) & set(r["recuperados"]))
        for r in registros
    )

    print(f"Preguntas con algún artículo correcto: {total_aciertos}/50")
    print(f"Preguntas sin coincidencias: {50-total_aciertos}/50")

    errores = [
        r for r in registros
        if not set(r["esperados"]) & set(r["recuperados"])
    ]

    print("\n=== PREGUNTAS SIN COINCIDENCIA ===")

    for registro in errores:
        print(
            registro["id"],
            "| Esperados:",
            registro["articulos_esperados"]
        )

    resultado_final = {
        "descripcion": (
            "Evaluación de recuperación documental del chatbot "
            "jurídico RAG sobre la Ley 1801 de 2016."
        ),
        "total_preguntas": len(banco),
        "modo_indice_135": "original",
        "cantidad_general_solicitada": 50,
        "metricas": metricas,
        "preguntas_con_coincidencia": total_aciertos,
        "preguntas_sin_coincidencia": len(errores),
        "resultados": [
            {
                "id": r["id"],
                "pregunta": r["pregunta"],
                "articulos_esperados": r["articulos_esperados"],
                "articulos_recuperados": r["articulos_recuperados"],
                "primera_posicion_relevante": (
                    r["primera_posicion_relevante"]
                ),
                "numerales_estructurados_135": (
                    r["numerales_estructurados_135"]
                ),
            }
            for r in registros
        ],
    }

    RUTA_SALIDA.write_text(
        json.dumps(
            resultado_final,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print("\nArchivo generado:")
    print(RUTA_SALIDA)

    print("\nPASO 1.370: EVALUACION COMPLETADA")


if __name__ == "__main__":
    main()
