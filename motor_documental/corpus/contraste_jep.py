"""Contrasta contra Jurinfo los artículos del expediente de conciliación."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from .conciliar_diferencias import bloques_diferentes, localizar_en_referencia
from .contrastar_corpus import CARPETA, segmentar


FUENTE = "https://jurinfo.jep.gov.co/normograma/compilacion/docs/ley_1801_2016.htm"


def texto(articulo):
    encabezado = f"ARTÍCULO {articulo['articulo']}. {articulo['epigrafe'] or ''}".rstrip()
    bloques = [b for u in articulo["unidades"] for b in u["bloques"]]
    return encabezado, "\n".join([encabezado, *bloques])


def contrastar(html, fecha, referencia):
    jep = segmentar(html, fecha, {})
    casos = []
    for oficial in referencia["articulos"]:
        if oficial["contraste_local"] != "diferencias_por_revisar":
            continue
        numero = oficial["articulo"]
        segunda = jep.get(numero)
        fuente_jep = FUENTE
        bloques = []
        estado = "articulo_no_localizado"
        if segunda:
            sufijo = segunda["fuente"].partition("#")[2]
            fuente_jep = f"{FUENTE}#{sufijo}" if sufijo else FUENTE
            segunda = {**segunda, "fuente": fuente_jep}
            encabezado, segunda_version = texto(segunda)
            bloques = bloques_diferentes(texto(oficial)[1], segunda_version)
            localizar_en_referencia(bloques, segunda, encabezado)
            for bloque in bloques:
                bloque["cancilleria"] = bloque.pop("historico")
                bloque["cancilleria_tokens"] = bloque.pop("historico_tokens")
                bloque["jep"] = bloque.pop("referencia")
                bloque["jep_tokens"] = bloque.pop("referencia_tokens")
            estado = "diferencia_entre_compilaciones" if bloques else "coincidencia_textual"
        casos.append({
            "articulo": numero,
            "cancilleria": oficial["fuente"],
            "jurinfo_jep": fuente_jep,
            "estado_textual": estado,
            "bloques": bloques,
            "cierra_revision_juridica": False,
        })
    return casos


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    parser.add_argument("--fecha-consulta", required=True)
    parser.add_argument("--salida", type=Path, default=CARPETA / "contraste_jep.json")
    args = parser.parse_args()
    datos = args.html.read_bytes()
    referencia = json.loads((CARPETA / "referencia_normativa.json").read_bytes())
    casos = contrastar(datos.decode("utf-8-sig"), args.fecha_consulta, referencia)
    resultado = {
        "fuente": FUENTE,
        "fecha_consulta": args.fecha_consulta,
        "sha256_html": hashlib.sha256(datos).hexdigest(),
        "total": len(casos),
        "estados": dict(Counter(caso["estado_textual"] for caso in casos)),
        "casos": casos,
    }
    args.salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
