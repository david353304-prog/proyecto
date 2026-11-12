"""
Validador estructural de documentos PDF cargados por usuarios.

Utiliza PyMuPDF para comprobar que un documento
pueda abrirse como PDF.

No modifica el corpus original ni los embeddings.
"""

import pymupdf

def validar_pdf(ruta_archivo):
    """Comprueba que un documento PDF pueda abrirse y leerse."""

    try:
        with pymupdf.open(ruta_archivo) as documento:
            if not documento.is_pdf:
                return False

            if documento.needs_pass:
                return False

            if documento.page_count == 0:
                return False

            for numero_pagina in range(documento.page_count):
                pagina = documento.load_page(numero_pagina)
                pagina.get_text()

            return True

    except (
        pymupdf.FileDataError,
        pymupdf.EmptyFileError,
        pymupdf.FileNotFoundError,
        ValueError,
        OSError
    ):
        return False

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("ERROR_ARGUMENTOS")
        sys.exit(2)

    if validar_pdf(sys.argv[1]):
        print("PDF_VALIDO")
        sys.exit(0)

    print("PDF_INVALIDO")
    sys.exit(1)
