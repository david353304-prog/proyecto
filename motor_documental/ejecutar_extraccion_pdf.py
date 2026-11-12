"""
Ejecutor independiente para extraer texto de PDF.

Aplica límites de recursos al proceso de extracción.
No genera embeddings ni modifica índices FAISS.
"""

import json
import resource
import sys

if __package__:
    from .extraer_pdf_usuario import (
        ErrorExtraccionPDF,
        extraer_pdf_usuario,
    )
else:
    from extraer_pdf_usuario import (
        ErrorExtraccionPDF,
        extraer_pdf_usuario,
    )


LIMITE_MEMORIA_BYTES = 512 * 1024 * 1024
LIMITE_CPU_SEGUNDOS = 20
LIMITE_ARCHIVO_BYTES = 4096


def establecer_limites():
    """Establece límites de recursos para este proceso."""

    resource.setrlimit(
        resource.RLIMIT_AS,
        (LIMITE_MEMORIA_BYTES, LIMITE_MEMORIA_BYTES)
    )

    resource.setrlimit(
        resource.RLIMIT_CPU,
        (LIMITE_CPU_SEGUNDOS, LIMITE_CPU_SEGUNDOS)
    )

    resource.setrlimit(
        resource.RLIMIT_FSIZE,
        (LIMITE_ARCHIVO_BYTES, LIMITE_ARCHIVO_BYTES)
    )


def main():
    if len(sys.argv) != 2:
        print(json.dumps({
            "estado": "error",
            "codigo": "ARGUMENTOS_INVALIDOS"
        }))
        return 2

    try:
        establecer_limites()

        resultado = extraer_pdf_usuario(sys.argv[1])

        print(json.dumps({
            "estado": "correcto",
            "documento": resultado["documento"],
            "total_paginas_con_texto":
                resultado["total_paginas_con_texto"],
            "total_caracteres":
                resultado["total_caracteres"]
        }))

        return 0

    except ErrorExtraccionPDF:
        print(json.dumps({
            "estado": "error",
            "codigo": "EXTRACCION_RECHAZADA"
        }))
        return 1

    except (OSError, ValueError, MemoryError):
        print(json.dumps({
            "estado": "error",
            "codigo": "ERROR_RECURSOS"
        }))
        return 1


if __name__ == "__main__":
    sys.exit(main())
