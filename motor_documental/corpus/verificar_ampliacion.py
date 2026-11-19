"""Verifica por apartado la ampliación contra la extracción de Jurinfo."""

import argparse
import hashlib
import json
from pathlib import Path

from .contrastar_corpus import CARPETA, clave_textual, segmentar


def verificar(html):
    alcance = json.loads((CARPETA / "ampliacion_publicable.json").read_bytes())
    referencia = json.loads((CARPETA / "referencia_normativa.json").read_bytes())
    principales = {a["articulo"]: a for a in referencia["articulos"]}
    secundarios = segmentar(html.decode("utf-8-sig"), alcance["fecha_consulta"], {})
    filas = []
    for numero, seleccion in alcance["articulos"].items():
        principal, secundario = principales[numero], secundarios[numero]
        unidades = [
            {u["id"].removeprefix(a["id"] + "-"): u["bloques"] for u in a["unidades"]}
            for a in (principal, secundario)
        ]
        for unidad, posiciones in seleccion["seleccion"].items():
            for i in posiciones:
                a, b = (bloques[unidad][i] for bloques in unidades)
                if clave_textual(a) != clave_textual(b):
                    raise ValueError(f"Texto distinto para {numero}, {unidad}, bloque {i}.")
                filas.append({
                    "articulo": numero, "unidad": unidad, "bloque": i,
                    "cancilleria": principal["fuente"],
                    "jurinfo": alcance["fuente_secundaria"] + f"#{numero}",
                    "fuentes_adicionales": seleccion["evidencia"],
                    "sha256_texto_cancilleria": hashlib.sha256(a.encode()).hexdigest(),
                    "alcance": seleccion["alcance"],
                })
    return {
        "fecha_consulta": alcance["fecha_consulta"], "total_bloques": len(filas),
        "sha256_html_jep": hashlib.sha256(html).hexdigest(), "bloques": filas,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    parser.add_argument("--salida", type=Path, default=CARPETA / "evidencia_ampliacion.json")
    args = parser.parse_args()
    args.salida.write_text(json.dumps(verificar(args.html.read_bytes()), ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
