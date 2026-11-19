"""Salvaguarda del índice histórico para la sentencia C-223/17."""

import json
import re
from functools import lru_cache
from pathlib import Path

from motor_documental.clasificador_tematico import normalizar


FUENTE_CORTE = "https://www.corteconstitucional.gov.co/relatoria/2017/C-223-17.htm"
ARTICULOS_INEXEQUIBLES = frozenset({*range(47, 76), 162})
IDENTIFICADORES_INEXEQUIBLES = frozenset(map(str, ARTICULOS_INEXEQUIBLES))
REFERENCIAS = re.compile(
    r"\b(?:articulos?|arts?\.)\s*\**\s*:?\s*(\d{1,3}[a-z]?\b"
    r"(?:\s*(?:,|y|e|o|a|al|hasta|[-–])\s*\d{1,3}[a-z]?\b)*)"
)


def articulos_mencionados(texto):
    articulos = set()
    for lista in REFERENCIAS.findall(normalizar(texto)):
        articulos.update(n.upper() for n in re.findall(r"\d+[a-z]?", lista))
        for inicio, fin in re.findall(r"(\d+)\s*(?:a|al|hasta|[-–])\s*(\d+)\b", lista):
            articulos.update(map(str, range(int(inicio), int(fin) + 1)))
    return articulos


def menciona_texto_inexequible(texto):
    return bool(articulos_mencionados(texto) & IDENTIFICADORES_INEXEQUIBLES)


@lru_cache(maxsize=1)
def corpus_publicable():
    carpeta = Path(__file__).resolve().parent / "corpus"
    alcance = json.loads((carpeta / "alcance_publicable.json").read_bytes())
    referencia = json.loads((carpeta / "referencia_normativa.json").read_bytes())
    registros = {
        a["articulo"]: {
            "articulo": a["articulo"],
            "id": a["id"],
            "titulo": a["epigrafe"],
            "texto": " ".join(
                [f"ARTÍCULO {a['articulo']}. {a['epigrafe']}."]
                + [bloque for unidad in a["unidades"] for bloque in unidad["bloques"]]
            ),
            "fuente": "Ley 1801 de 2016, compilación de Cancillería",
            "url_fuente": a["fuente"],
        }
        for a in referencia["articulos"]
        if a["articulo"] in alcance["articulos"]
        and a["articulo"] not in IDENTIFICADORES_INEXEQUIBLES
        and not a["notas_editoriales"]
        and a["fecha_consulta"] == alcance["fecha_consulta"]
    }
    if registros.keys() != alcance["articulos"].keys():
        raise ValueError("El alcance documental no coincide con los artículos cotejados.")
    return registros


def respuesta_revision_pendiente(pregunta):
    if articulos_mencionados(pregunta) - corpus_publicable().keys():
        return {
            "pregunta": pregunta,
            "respuesta": "La disposición solicitada está fuera del alcance documental verificado del prototipo y requiere revisión antes de presentarse como aplicable.",
            "modelo": "verificación documental",
            "total_generales": 0,
            "total_estructurados": 0,
            "validacion_documental": {"estado": "SIN_RESPALDO", "advertencias": []},
        }
    return None


def contexto_publicable(resultados):
    corpus = corpus_publicable()
    numeros = dict.fromkeys(
        str(registro["articulo"]) for registro in resultados.get("resultados_generales", [])
        if str(registro["articulo"]) in corpus
    )
    generales = [corpus[numero].copy() for numero in numeros]
    return {
        **resultados,
        "resultados_generales": generales,
        "total_generales": len(generales),
        "resultados_estructurados_135": [],
        "total_estructurados": 0,
    }


def respuesta_texto_inexequible(pregunta):
    if menciona_texto_inexequible(pregunta):
        return {
            "pregunta": pregunta,
            "respuesta": (
                "La Corte Constitucional declaró inexequibles el artículo 162 "
                "y los textos originales de los artículos 47 a 75 de la Ley 1801 "
                "en la sentencia C-223/17. Para los artículos 47 a 75, la Corte difirió "
                "los efectos hasta antes del 20 de junio de 2019. "
                "La situación de cualquier regulación posterior requiere un cotejo separado. "
                f"[Consultar la sentencia C-223/17]({FUENTE_CORTE})"
            ),
            "modelo": "verificación documental",
            "total_generales": 0,
            "total_estructurados": 0,
            "validacion_documental": {"estado": "TEXTO_INEXEQUIBLE", "advertencias": []},
        }
    return None
