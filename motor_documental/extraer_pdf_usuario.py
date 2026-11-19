"""
Extracción limitada de texto de PDF cargados por usuarios.

No modifica el corpus jurídico ni genera índices FAISS.
"""

from pathlib import Path
import os
import re
import stat

import pymupdf


CARPETA_DOCUMENTOS = (
    Path(os.environ["DIRECTORIO_PDF_PRUEBAS"]).resolve()
    if (
        os.environ.get("NODE_ENV") == "test"
        and os.environ.get("DIRECTORIO_PDF_PRUEBAS")
    )
    else Path(__file__).resolve().parent / "documentos_subidos"
)

LIMITE_PDF_BYTES = 10 * 1024 * 1024
LIMITE_PAGINAS = 200
LIMITE_CARACTERES = 1_000_000

PATRON_NOMBRE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
    r"[0-9a-f]{4}-[0-9a-f]{12}\.pdf$"
)


class ErrorExtraccionPDF(ValueError):
    """Error controlado durante la extracción."""


def _abrir_pdf(ruta):
    if os.name != "nt":
        return os.open(ruta, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)

    import ctypes
    import msvcrt
    from ctypes import wintypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    crear_archivo = kernel32.CreateFileW
    crear_archivo.argtypes = (
        wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
        wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE
    )
    crear_archivo.restype = wintypes.HANDLE

    acceso_lectura = 0x80000000
    compartir_lectura_y_borrado = 0x01 | 0x04
    abrir_existente = 3
    abrir_punto_reanalisis = 0x00200000
    handle = crear_archivo(
        str(ruta), acceso_lectura, compartir_lectura_y_borrado, None,
        abrir_existente, abrir_punto_reanalisis, None
    )
    if handle == wintypes.HANDLE(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())

    try:
        # Consulta los atributos del objeto abierto, incluso si se reemplaza la ruta.
        consultar = kernel32.GetFileInformationByHandleEx
        consultar.argtypes = (
            wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD
        )
        consultar.restype = wintypes.BOOL
        atributos_y_etiqueta = (wintypes.DWORD * 2)()
        clase_atributos_y_etiqueta = 9
        if not consultar(
            handle, clase_atributos_y_etiqueta, atributos_y_etiqueta,
            ctypes.sizeof(atributos_y_etiqueta)
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        if atributos_y_etiqueta[0] & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise ErrorExtraccionPDF("El documento es un punto de reanálisis.")

        return msvcrt.open_osfhandle(handle, os.O_RDONLY | os.O_BINARY)
    except BaseException:
        kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
        kernel32.CloseHandle(handle)
        raise


def extraer_pdf_usuario(nombre_archivo):
    """Extrae texto por página de un PDF previamente recibido."""

    if not isinstance(nombre_archivo, str):
        raise ErrorExtraccionPDF("Nombre de archivo inválido.")

    if not PATRON_NOMBRE.fullmatch(nombre_archivo):
        raise ErrorExtraccionPDF("Nombre de archivo no permitido.")

    ruta = CARPETA_DOCUMENTOS / nombre_archivo

    paginas = []
    caracteres_totales = 0

    try:
        descriptor = _abrir_pdf(ruta)

        try:
            informacion = os.fstat(descriptor)

            if not stat.S_ISREG(informacion.st_mode):
                raise ErrorExtraccionPDF(
                    "El documento no es un archivo regular."
                )

            if informacion.st_size > LIMITE_PDF_BYTES:
                raise ErrorExtraccionPDF(
                    "El PDF supera el tamaño permitido."
                )

            with os.fdopen(descriptor, "rb", closefd=False) as archivo:
                datos = archivo.read(LIMITE_PDF_BYTES + 1)

            if len(datos) > LIMITE_PDF_BYTES:
                raise ErrorExtraccionPDF(
                    "El PDF supera el tamaño permitido."
                )

        finally:
            os.close(descriptor)

        with pymupdf.open(
            stream=datos,
            filetype="pdf"
        ) as documento:

            if not documento.is_pdf or documento.needs_pass:
                raise ErrorExtraccionPDF("PDF no permitido.")

            if not 1 <= documento.page_count <= LIMITE_PAGINAS:
                raise ErrorExtraccionPDF(
                    "Cantidad de páginas no permitida."
                )

            for numero, pagina in enumerate(documento, start=1):
                texto = pagina.get_text("text").strip()

                if not texto:
                    continue

                caracteres_totales += len(texto)

                if caracteres_totales > LIMITE_CARACTERES:
                    raise ErrorExtraccionPDF(
                        "El documento supera el límite de texto."
                    )

                paginas.append({
                    "pagina": numero,
                    "texto": texto
                })

    except (
        pymupdf.FileDataError,
        pymupdf.EmptyFileError,
        pymupdf.FileNotFoundError,
        OSError
    ) as error:
        raise ErrorExtraccionPDF(
            "No fue posible procesar el documento PDF."
        ) from error

    if not paginas:
        raise ErrorExtraccionPDF(
            "El PDF no contiene texto extraíble."
        )

    return {
        "documento": nombre_archivo,
        "total_paginas_con_texto": len(paginas),
        "total_caracteres": caracteres_totales,
        "paginas": paginas
    }
