"""
Controlador de extracción PDF mediante un proceso independiente.

Aplica límites de tiempo real y salida.
No modifica el corpus jurídico ni los índices FAISS.
"""

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_EJECUTOR = (
    Path(__file__).resolve().parent
    / "ejecutar_extraccion_pdf.py"
)

TIEMPO_MAXIMO_SEGUNDOS = 30
LIMITE_SALIDA_BYTES = 4096


def controlar_extraccion_pdf(nombre_archivo):
    """Ejecuta la extracción con un tiempo máximo."""

    if (
        not isinstance(nombre_archivo, str)
        or re.fullmatch(
            r"[0-9a-f]{8}-[0-9a-f]{4}-"
            r"[0-9a-f]{4}-[0-9a-f]{4}-"
            r"[0-9a-f]{12}\.pdf",
            nombre_archivo
        ) is None
    ):
        return {
            "estado": "error",
            "codigo": "ARGUMENTOS_INVALIDOS"
        }

    try:
        with tempfile.TemporaryFile() as salida:
            with tempfile.TemporaryFile() as errores:
                try:
                    resultado = subprocess.run(
                        [
                            sys.executable,
                            str(SCRIPT_EJECUTOR),
                            nombre_archivo
                        ],
                        stdout=salida,
                        stderr=errores,
                        timeout=TIEMPO_MAXIMO_SEGUNDOS,
                        check=False
                    )

                except subprocess.TimeoutExpired:
                    return {
                        "estado": "error",
                        "codigo": "TIEMPO_AGOTADO"
                    }

                salida.seek(0)
                errores.seek(0)

                stdout = salida.read(LIMITE_SALIDA_BYTES + 1)
                stderr = errores.read(LIMITE_SALIDA_BYTES + 1)

    except OSError:
        return {
            "estado": "error",
            "codigo": "ERROR_EJECUCION"
        }

    if (
        len(stdout) > LIMITE_SALIDA_BYTES
        or len(stderr) > LIMITE_SALIDA_BYTES
    ):
        return {
            "estado": "error",
            "codigo": "SALIDA_EXCESIVA"
        }

    try:
        datos = json.loads(stdout)
    except (ValueError, UnicodeDecodeError):
        return {
            "estado": "error",
            "codigo": "RESPUESTA_INVALIDA"
        }

    if not isinstance(datos, dict):
        return {
            "estado": "error",
            "codigo": "RESPUESTA_INVALIDA"
        }

    if resultado.returncode != 0:
        codigos_permitidos = {
            "ARGUMENTOS_INVALIDOS",
            "EXTRACCION_RECHAZADA",
            "ERROR_RECURSOS"
        }

        codigo = datos.get("codigo")

        if (
            datos.get("estado") != "error"
            or not isinstance(codigo, str)
            or codigo not in codigos_permitidos
        ):
            codigo = "EXTRACCION_FALLIDA"

        return {
            "estado": "error",
            "codigo": codigo
        }

    documento = datos.get("documento")
    paginas = datos.get("total_paginas_con_texto")
    caracteres = datos.get("total_caracteres")

    respuesta_valida = (
        datos.get("estado") == "correcto"
        and documento == nombre_archivo
        and type(paginas) is int
        and 1 <= paginas <= 200
        and type(caracteres) is int
        and 1 <= caracteres <= 1000000
    )

    if not respuesta_valida:
        return {
            "estado": "error",
            "codigo": "RESPUESTA_INVALIDA"
        }

    return {
        "estado": "correcto",
        "documento": documento,
        "total_paginas_con_texto": paginas,
        "total_caracteres": caracteres
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(json.dumps({
            "estado": "error",
            "codigo": "ARGUMENTOS_INVALIDOS"
        }))
        sys.exit(2)

    respuesta = controlar_extraccion_pdf(sys.argv[1])
    print(json.dumps(respuesta))

    sys.exit(
        0 if respuesta["estado"] == "correcto" else 1
    )
