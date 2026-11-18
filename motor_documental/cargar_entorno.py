"""Carga sencilla de un archivo .env sin dependencias externas.

No sobrescribe variables que ya existan en el entorno del sistema.
"""

import os
from pathlib import Path

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent


def cargar_entorno(ruta=None):
    """Lee KEY=VALOR desde .env (raíz del proyecto por defecto)."""
    archivo = Path(ruta) if ruta else RAIZ_PROYECTO / ".env"
    if not archivo.is_file():
        return False

    for linea in archivo.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        clave = clave.strip()
        valor = valor.strip().strip('"').strip("'")
        if clave and valor and clave not in os.environ:
            os.environ[clave] = valor
    return True