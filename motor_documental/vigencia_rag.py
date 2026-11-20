"""Salvaguarda del índice histórico para la sentencia C-223/17."""

import json
import re
from functools import lru_cache
from pathlib import Path

from motor_documental.clasificador_tematico import normalizar


FUENTE_CORTE = "https://www.corteconstitucional.gov.co/relatoria/2017/C-223-17.htm"
ARTICULOS_INEXEQUIBLES = frozenset({*range(47, 76), 162})
IDENTIFICADORES_INEXEQUIBLES = frozenset(map(str, ARTICULOS_INEXEQUIBLES))
# El alcance temático restringe primero el artículo. Este umbral solo
# descarta similitudes bajas dentro de las definiciones autorizadas.
SIMILITUD_MINIMA_DEFINICION = 0.35
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
def referencia_publicable():
    ruta = Path(__file__).resolve().parent / "corpus" / "referencia_normativa.json"
    return json.loads(ruta.read_bytes())


@lru_cache(maxsize=1)
def corpus_publicable():
    carpeta = Path(__file__).resolve().parent / "corpus"
    alcance = json.loads((carpeta / "alcance_publicable.json").read_bytes())
    referencia = referencia_publicable()
    ampliacion = json.loads((carpeta / "ampliacion_publicable.json").read_bytes())
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
    oficiales = {a["articulo"]: a for a in referencia["articulos"]}
    for numero, ficha in ampliacion["articulos"].items():
        a = oficiales[numero]
        if numero in IDENTIFICADORES_INEXEQUIBLES or numero in registros or a["fecha_consulta"] != ampliacion["fecha_consulta"]:
            raise ValueError(f"Selección pública inválida para el artículo {numero}.")
        unidades = {u["id"].removeprefix(a["id"] + "-"): u for u in a["unidades"]}
        bloques = [
            unidades[unidad]["bloques"][i]
            for unidad, indices in ficha["seleccion"].items() for i in indices
        ]
        registros[numero] = {
            "articulo": numero, "id": a["id"], "titulo": a["epigrafe"],
            "texto": " ".join([f"ARTÍCULO {numero}. {a['epigrafe']}.", *bloques]),
            "fuente": "Ley 1801 de 2016, apartados cotejados en Cancillería",
            "url_fuente": a["fuente"],
            "alcance": ficha["alcance"],
            "consulta": ficha["consulta"],
            "exclusiones_consulta": ficha.get("exclusiones_consulta", r"(?!)"),
            "numerales": [
                unidades[unidad]["etiqueta"] for unidad in ficha["seleccion"]
                if unidades[unidad]["tipo"] == "numeral"
            ],
        }
    for numero, registro in registros.items():
        oficial = oficiales[numero]
        ficha = ampliacion["articulos"].get(numero)
        registro.update(
            jerarquia=oficial["jerarquia"], tema=oficial["tema"],
            fecha_consulta=oficial["fecha_consulta"],
            estado_documental="apartados_cotejados" if ficha else "articulo_cotejado",
            evidencia_adicional=ficha["evidencia"] if ficha else [],
            apartados=[
                {"id": unidad["id"], "tipo": unidad["tipo"],
                 "etiqueta": unidad.get("etiqueta"), "bloques": indices}
                for unidad in oficial["unidades"]
                if (indices := (
                    ficha["seleccion"].get(unidad["id"].removeprefix(oficial["id"] + "-"))
                    if ficha else list(range(len(unidad["bloques"])))
                ))
            ],
        )
    return registros


def articulos_para_consulta(pregunta):
    corpus = corpus_publicable()
    texto = normalizar(pregunta)
    # En consultas urbanísticas, «sin autorización» expresa la falta de licencia.
    texto_urbanistico = re.sub(r"\bsin autorizacion\b", "sin licencia", texto)
    texto_urbanistico = re.sub(
        r"\bcuanto (?:debo|tengo que|hay que) pagar\b", "cuantia", texto_urbanistico
    )
    explicitos = articulos_mencionados(pregunta)
    if explicitos:
        if explicitos - corpus.keys():
            return set()
        solicitados = set(re.findall(r"\bnumeral\s+(\d+)\b", texto))
        consulta_multiple = re.search(r"\bnumerales\b|\bnumeral\s+\d+\s*(?:,|y|o|a|al|hasta|[-–])\s*\d", texto)
        numeral_sin_identificar = re.search(r"\bnumeral\b", texto) and not solicitados
        paragrafo = re.search(r"\bparagrafos?\b", texto)
        return {
            numero for numero in explicitos
            if "consulta" not in corpus[numero]
            or (
                not consulta_multiple and not numeral_sin_identificar
                and len(solicitados) <= 1 and not paragrafo
                and not re.search(
                    corpus[numero]["exclusiones_consulta"], texto_urbanistico if numero == "135" else texto
                )
                and solicitados <= set(corpus[numero]["numerales"])
                and (solicitados or re.search(
                    corpus[numero]["consulta"], texto_urbanistico if numero == "135" else texto
                ))
            )
        }
    patrones = {
        "1": r"objetivo general|objeto del codigo|para que (?:sirve|existe) el codigo",
        "2": r"objetivos? especific|objetivos? del codigo",
        "5": r"definicion de convivencia|que (?:es|entiende).{0,30}(?:por )?convivencia",
        "6": r"categorias (?:juridicas|de convivencia)",
        "7": r"finalidades? de la convivencia|fines? (?:esenciales )?de la convivencia",
    }
    return {
        numero for numero, registro in corpus.items()
        if re.search(
            registro.get("consulta", patrones.get(numero, r"(?!)")),
            texto_urbanistico if numero == "135" else texto,
        )
        and not re.search(
            registro.get("exclusiones_consulta", r"(?!)"),
            texto_urbanistico if numero == "135" else texto,
        )
    }


def alcance_semantico_documental(pregunta):
    """Admite paráfrasis de definiciones con un tema documental aprobado."""
    texto = normalizar(pregunta).strip("¿?¡! .")
    if articulos_mencionados(pregunta):
        return {}
    intencion = re.fullmatch(
        r"(?:como define (?:el codigo|la ley)(?: a)?|"
        r"a que se refiere (?:el codigo|la ley) (?:con|cuando habla de)|"
        r"que quiere decir (?:el codigo|la ley) (?:con|cuando habla de)) (.+)", texto
    )
    if not intencion:
        return {}
    temas = {
        "5": r"(?:la )?convivencia",
        "172": r"(?:(?:una|la|las) )?medidas? correctivas?",
        "218": r"(?:(?:una|un|el|la) )?(?:orden de )?comparendo",
    }
    return {n: intencion[1] for n, tema in temas.items() if n in corpus_publicable()
            and re.fullmatch(tema, intencion[1])}


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


def pasajes_del_contexto(registros):
    """Da identificadores locales a bloques aprobados de los artículos recuperados."""
    oficiales = {a["articulo"]: a for a in referencia_publicable()["articulos"]}
    pasajes = {}
    for registro in registros:
        numero = registro["articulo"]
        oficial = oficiales[numero]
        unidades = {unidad["id"]: unidad["bloques"] for unidad in oficial["unidades"]}
        for apartado in registro["apartados"]:
            for posicion in apartado["bloques"]:
                texto = unidades[apartado["id"]][posicion]
                if texto in registro["texto"]:
                    pasaje = {"articulo": numero, "texto": texto}
                    if posicion and numero == "223" and apartado["tipo"] in {"numeral", "paragrafo"}:
                        clase = "Numeral" if apartado["tipo"] == "numeral" else "Parágrafo"
                        pasaje["rotulo"] = f"{clase} {apartado['etiqueta']} del artículo {numero}"
                    if numero == "206" and apartado["tipo"] == "literal":
                        orden = int(apartado["id"].rsplit("-", 1)[1])
                        padre = 4 if orden <= 8 else 5
                        pasaje["rotulo"] = f"Literal {apartado['etiqueta']} del numeral {padre} del artículo {numero}"
                    if numero == "38" and apartado["tipo"] == "literal":
                        orden = int(apartado["id"].rsplit("-", 1)[1])
                        padre = 1 if orden < 8 else 5 if orden < 16 else 6
                        pasaje["rotulo"] = f"Literal {apartado['etiqueta']} del numeral {padre} del artículo {numero}"
                    pasajes[f"P{len(pasajes) + 1}"] = pasaje
    return pasajes


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
