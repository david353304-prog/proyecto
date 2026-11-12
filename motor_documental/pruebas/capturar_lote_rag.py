"""Ejecuta capturas pendientes del banco de evaluacion."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
ARCHIVO = CARPETA / "evaluacion_respuestas_50.json"
CAPTURADOR = CARPETA / "capturar_respuesta_rag.py"


def ejecutar(limite, confirmar):
    datos = json.loads(ARCHIVO.read_text(encoding="utf-8"))

    pendientes = [
        caso["id"]
        for caso in datos["resultados"]
        if not caso.get("respuesta_generada")
    ]

    seleccionados = pendientes[:limite]

    print("Preguntas totales:", len(datos["resultados"]))
    print("Pendientes:", len(pendientes))
    print("Seleccionadas:", seleccionados, flush=True)

    if not confirmar:
        print("SIMULACION: no se consulto Gemini.")
        return 0

    completadas = 0

    for identificador in seleccionados:
        print("Capturando:", identificador, flush=True)

        resultado = subprocess.run(
            [
                sys.executable,
                str(CAPTURADOR),
                "--id",
                identificador,
            ],
            cwd=CARPETA.parent.parent,
            check=False,
        )

        if resultado.returncode != 0:
            print(
                "CAPTURA DETENIDA EN:",
                identificador,
                flush=True,
            )
            print(
                "Las capturas anteriores permanecen guardadas.",
                flush=True,
            )
            return resultado.returncode

        completadas += 1

    print("CAPTURAS COMPLETADAS:", completadas)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--limite", type=int, default=1
    )
    parser.add_argument(
        "--confirmar", action="store_true"
    )
    args = parser.parse_args()

    if args.limite < 1:
        parser.error("--limite debe ser mayor que cero")

    sys.exit(ejecutar(args.limite, args.confirmar))
