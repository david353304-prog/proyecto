"""Construye una referencia segmentada a partir del HTML de Cancillería."""

import argparse
import hashlib
import json
import re
import unicodedata
from html import unescape
from pathlib import Path


CARPETA = Path(__file__).resolve().parent
FUENTE = "https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm"
JERARQUIA = ("libro", "título", "capítulo")
ENCABEZADO = re.compile(r"^(LIBRO|TÍTULO|CAPÍTULO) ([IVXLCDM]+|PRIMERO|SEGUNDO|TERCERO|ÚNICO)\.?$", re.I)
ARTICULO = re.compile(r"^ARTÍCULO\s+(\d+(?:\s*(?-i:[A-Z]))?)[oº°]?\s*\.\s*(.*)$", re.I)
UNIDAD = re.compile(
    r"^(?:PARÁGRAFO(?:\s+(\d+|TRANSITORIO|ÚNICO)[oº°]?)?\s*\.|(\d+)[.)]\s|([a-z])[.)]\s)",
    re.I,
)


def texto_html(html):
    return " ".join(unicodedata.normalize(
        "NFC", unescape(re.sub(r"<[^>]+>", " ", html))
    ).replace("\u00ad", "").split())


def clave_textual(texto):
    return re.findall(r"\w+", texto.casefold())


def segmentar(html, fecha, local):
    # Las tablas vacías del sitio se rellenan con notas editoriales vía JavaScript.
    marca = re.search(r'name="LIBRO I"', html, re.I)
    html = html[html.rfind("<p", 0, marca.start()):]
    bloques = re.finditer(
        r"<(p|tr)\b([^>]*)>(.*?)</\1\s*>", html, re.I | re.S
    )
    jerarquia = dict.fromkeys(JERARQUIA)
    registros = {}
    articulo = unidad = None
    esperando_nombre = None
    paragrafo = None
    for bloque in bloques:
        etiqueta, atributos, contenido = bloque.groups()
        texto = texto_html(contenido)
        if not texto:
            continue
        nombre = ENCABEZADO.fullmatch(texto)
        if nombre:
            nivel = nombre[1].lower()
            for inferior in JERARQUIA[JERARQUIA.index(nivel):]:
                jerarquia[inferior] = None
            jerarquia[nivel] = texto.rstrip(".")
            esperando_nombre = nivel
            articulo = None
            continue

        ancla = re.search(
            r'<a\b[^>]*\bname="([^"]+)"[^>]*>(.*?)</a\s*>',
            contenido, re.I | re.S
        )
        negrita = re.match(r"\s*<b>(.*?)</b>", contenido, re.I | re.S)
        encabezado = texto_html(ancla[2] if ancla else negrita[1] if negrita else "")
        cabecera = ARTICULO.match(encabezado)
        if cabecera and (not ancla or re.fullmatch(r"\d+[a-z]?", ancla[1], re.I)):
            numero = (ancla[1] if ancla else cabecera[1]).replace(" ", "").upper()
            if numero in registros:
                raise ValueError(f"Artículo duplicado en la fuente: {numero}")
            epigrafe = cabecera[2].strip(" .") or None
            articulo = {
                "id": f"ley-1801-2016-art-{numero}", "articulo": numero,
                "jerarquia": jerarquia.copy(), "epigrafe": epigrafe,
                "tema": next((jerarquia[n] for n in reversed(JERARQUIA) if jerarquia[n]), epigrafe),
                "fuente": f"{FUENTE}#{ancla[1]}" if ancla else FUENTE, "fecha_consulta": fecha,
                "estado_vigencia": "pendiente_revision_juridica",
                "notas_editoriales": [], "unidades": [],
            }
            registros[numero] = articulo
            paragrafo = None
            esperando_nombre = None
            unidad = {"id": articulo["id"] + "-cuerpo", "tipo": "cuerpo", "bloques": []}
            articulo["unidades"].append(unidad)
            texto = texto[len(encabezado):].strip()
        elif esperando_nombre and "centrado" in atributos:
            jerarquia[esperando_nombre] += " " + texto
            esperando_nombre = None
            continue

        if articulo is None or not texto:
            continue
        if articulo["articulo"] == "243" and texto.startswith("El Presidente"):
            break
        notas = re.findall(r"<([^<>]+)>", texto)
        articulo["notas_editoriales"].extend(notas)
        texto = " ".join(re.sub(r"<[^<>]+>", "", texto).split())
        unidad_detectada = UNIDAD.match(texto) if etiqueta.lower() == "p" else None
        if unidad_detectada:
            if unidad_detectada[2]:
                tipo, etiqueta_unidad = "numeral", unidad_detectada[2]
            elif unidad_detectada[3]:
                tipo, etiqueta_unidad = "literal", unidad_detectada[3].lower()
            else:
                tipo, etiqueta_unidad = "paragrafo", unidad_detectada[1] or "sin-numero"
                paragrafo = etiqueta_unidad
            unidad = {
                "id": f"{articulo['id']}-{tipo}-{len(articulo['unidades'])}",
                "tipo": tipo, "etiqueta": etiqueta_unidad,
                "paragrafo": paragrafo, "bloques": [],
            }
            articulo["unidades"].append(unidad)
        if texto:
            unidad["bloques"].append(texto)

    for numero, articulo in registros.items():
        anterior = local.get(numero)
        texto = " ".join(
            bloque for unidad in articulo["unidades"] for bloque in unidad["bloques"]
        )
        prefijo = clave_textual(f"ARTÍCULO {numero}. {articulo['epigrafe'] or ''}")
        tokens_locales = clave_textual(anterior["texto"]) if anterior else []
        articulo["contraste_local"] = (
            "sin_articulo_local" if not anterior else
            "coincide_normalizado" if tokens_locales == prefijo + clave_textual(texto) else
            "diferencias_por_revisar"
        )
        if anterior:
            articulo["paginas_pdf_local"] = [anterior["pagina_inicio"], anterior["pagina_fin"]]
        if numero.isdecimal() and 47 <= int(numero) <= 75:
            articulo["estado_vigencia"] = "inexequible_texto_original"
            articulo["evidencia_vigencia"] = {
                "decision": "C-223/17",
                "efectos_diferidos_hasta": "2019-06-20",
                "fuente": "https://www.corteconstitucional.gov.co/relatoria/2017/C-223-17.htm",
            }
    return registros


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    parser.add_argument("--fecha-consulta", required=True)
    parser.add_argument("--salida", type=Path, default=CARPETA / "referencia_normativa.json")
    args = parser.parse_args()
    datos = args.html.read_bytes()
    html = datos.decode("utf-8-sig", errors="strict")
    local = {a["numero"]: a for a in json.loads(
        (CARPETA / "articulos_ley_1801.json").read_text(encoding="utf-8")
    )}
    registros = segmentar(html, args.fecha_consulta, local)
    if not {"1", "33", "135", "140", "155", "243"} <= registros.keys():
        raise ValueError("La compilación no contiene los artículos de control")
    resultado = {
        "fuente": FUENTE, "fecha_consulta": args.fecha_consulta,
        "sha256_html": hashlib.sha256(datos).hexdigest(),
        "solo_en_pdf_local": sorted(local.keys() - registros.keys()),
        "articulos": list(registros.values()),
    }
    args.salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
