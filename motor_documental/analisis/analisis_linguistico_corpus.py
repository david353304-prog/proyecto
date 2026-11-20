"""Análisis lingüístico académico de la Ley 1801 de 2016."""

import argparse
import json
import hashlib
import math
import re
import unicodedata
from collections import Counter
from pathlib import Path

import spacy

BASE = Path(__file__).resolve().parent.parent
CORPUS = BASE / "corpus" / "articulos_ley_1801.json"
SALIDA = BASE / "analisis" / "resultados_linguisticos.json"

TERMINOS = [
    "multa",
    "comparendo",
    "medida correctiva",
    "espacio público",
]

EXPRESIONES_JURIDICAS = [
    "medida correctiva",
    "multa general",
    "autoridad de policía",
    "espacio público",
    "orden de comparendo",
    "comportamientos contrarios a la convivencia",
]

GLOSARIO = {
    "comparendo": {
        "explicacion": "Orden relacionada con un procedimiento de policía.",
        "consulta_coloquial": "Me pusieron un comparendo, ¿qué hago?"
    },
    "multa": {
        "explicacion": "Medida correctiva de carácter económico.",
        "consulta_coloquial": "¿Cuánto tengo que pagar?"
    },
    "medida correctiva": {
        "explicacion": "Medida contemplada por el Código Nacional de Seguridad y Convivencia Ciudadana.",
        "consulta_coloquial": "¿Qué me puede pasar si incumplo una norma?"
    },
    "espacio público": {
        "explicacion": "Espacios destinados al uso y disfrute colectivo.",
        "consulta_coloquial": "¿Puedo hacer esto en la calle o en un parque?"
    },
    "autoridad de policía": {
        "explicacion": "Autoridad con competencias establecidas en el Código.",
        "consulta_coloquial": "¿Quién puede intervenir o imponer una medida?"
    },
}

PATRONES_ENTIDADES = {
    "AUTORIDAD": r"\b(?:Policía Nacional|Corte Constitucional|Ministerio del Interior|"
                 r"Instituto Colombiano de Bienestar Familiar|Ministerio Público|"
                 r"inspector(?:es)? de Policía|alcald(?:e|es|ía|ías)|corregidor(?:es)?)\b",
    "LUGAR": r"\b(?:Colombia|Bogotá|espacio público|territorio nacional)\b",
    "MONTO": r"\b\d+(?:[.,]\d+)?\s*(?:%|pesos\b|(?:sml[dv]v|uvb|uvt)\b)|"
             r"\b(?:\d+|\(\d+\))\s*salarios mínimos(?: legales)?\b",
    "PLAZO": r"\b(?:\d+|(?:treinta|cuarenta|cincuenta|sesenta|setenta|ochenta|noventa)\s+y\s+"
             r"(?:un[oa]?|dos|tres|cuatro|cinco|seis|siete|ocho|nueve)\s+\(\d+\)|"
             r"[a-záéíóú]+\s+\(\d+\))\s+"
             r"(?:horas?|días?|mes(?:es)?|años?)(?:\s+hábiles)?\b",
}


def entidades_por_reglas(tipo, patron, texto):
    for coincidencia in re.finditer(patron, texto, re.I):
        if tipo == "PLAZO":
            antes = texto[max(0, coincidencia.start() - 40):coincidencia.start()]
            despues = texto[coincidencia.end():coincidencia.end() + 12]
            if ("año" in coincidencia[0].casefold() and (
                re.search(r"\b(?:edades?|mayor(?:es)?|menor(?:es)?)\s+de\s*$", antes, re.I)
                or re.match(r"\s+de edad\b", despues, re.I)
            )):
                continue
        yield coincidencia[0].casefold()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publicable", action="store_true")
    parser.add_argument("--salida", type=Path)
    args = parser.parse_args()
    if args.publicable and not args.salida:
        parser.error("--publicable requiere una salida separada")
    salida = args.salida or SALIDA
    if args.publicable:
        from motor_documental.vigencia_rag import corpus_publicable

        articulos = [
            {"numero": numero, "texto": registro["texto"]}
            for numero, registro in corpus_publicable().items()
        ]
        datos = json.dumps(articulos, ensure_ascii=False, sort_keys=True).encode("utf-8")
    else:
        datos = CORPUS.read_bytes()
        articulos = json.loads(datos)
    nlp = spacy.load("es_core_news_sm")

    textos = [
        (" ".join(unicodedata.normalize("NFC", articulo["texto"]).split()), articulo["numero"])
        for articulo in articulos
        if articulo.get("texto", "").strip()
    ]

    frecuencias = Counter()
    lemas = Counter()
    categorias = Counter()
    entidades = Counter()
    entidades_juridicas = {tipo: Counter() for tipo in PATRONES_ENTIDADES}
    bigramas = Counter()
    trigramas = Counter()
    longitudes = []
    concordancias = {termino: [] for termino in TERMINOS}

    total_tokens = 0
    tipos = set()

    for doc, articulo in nlp.pipe(textos, as_tuples=True, batch_size=16):
        palabras = [
            token for token in doc
            if not token.is_space and not token.is_punct
        ]

        total_tokens += len(palabras)
        longitudes.append(len(palabras))

        normalizadas = [
            token.text.lower()
            for token in palabras
        ]

        frecuencias.update(normalizadas)
        tipos.update(normalizadas)

        lemas.update(
            token.lemma_.lower()
            for token in palabras
            if not token.is_stop
        )

        categorias.update(
            token.pos_ for token in palabras
        )

        entidades.update(
            (ent.text, ent.label_)
            for ent in doc.ents
        )

        bigramas.update(
            zip(normalizadas, normalizadas[1:])
        )
        trigramas.update(zip(normalizadas, normalizadas[1:], normalizadas[2:]))

        texto = doc.text
        for tipo, patron in PATRONES_ENTIDADES.items():
            entidades_juridicas[tipo].update(
                entidades_por_reglas(tipo, patron, texto)
            )

        for termino in TERMINOS:
            if len(concordancias[termino]) >= 5:
                continue

            patron = re.compile(
                r"\b" + re.escape(termino) + r"\b",
                re.IGNORECASE
            )

            for coincidencia in patron.finditer(texto):
                inicio = max(0, coincidencia.start() - 65)
                fin = min(len(texto), coincidencia.end() + 65)

                concordancias[termino].append(
                    {
                        "articulo": articulo,
                        "izquierda": texto[inicio:coincidencia.start()],
                        "termino": coincidencia[0],
                        "derecha": texto[coincidencia.end():fin],
                    }
                )

                if len(concordancias[termino]) >= 5:
                    break

    corpus_normalizado = [
        texto.casefold() for texto, _ in textos
    ]

    colocaciones = {
        expresion: sum(
            len(re.findall(
                r"(?<!\w)" + re.escape(expresion) + r"(?!\w)",
                texto
            ))
            for texto in corpus_normalizado
        )
        for expresion in EXPRESIONES_JURIDICAS
    }

    pares = sum(bigramas.values())
    izquierdas, derechas = Counter(), Counter()
    for (a, b), frecuencia in bigramas.items():
        izquierdas[a] += frecuencia
        derechas[b] += frecuencia
    asociaciones = []
    for (a, b), frecuencia in bigramas.items():
        if frecuencia >= 5 and {a, b} & {"multa", "comparendo", "medida", "espacio"}:
            pmi = math.log2(frecuencia * pares / (izquierdas[a] * derechas[b]))
            asociaciones.append({"terminos": [a, b], "frecuencia": frecuencia, "pmi": round(pmi, 4)})
    asociaciones.sort(key=lambda fila: (-fila["pmi"], fila["terminos"]))

    resultados = {
        "corpus": "Ley 1801 de 2016, apartados públicos" if args.publicable else "Ley 1801 de 2016",
        "sha256_corpus": hashlib.sha256(datos).hexdigest(),
        "modelo": "es_core_news_sm",
        "version_modelo": nlp.meta["version"],
        "version_spacy": spacy.__version__,
        "total_articulos": len(articulos),
        "articulos_con_texto": len(textos),
        "total_tokens": total_tokens,
        "total_tipos": len(tipos),
        "relacion_tipo_token": round(
            len(tipos) / total_tokens, 4
        ) if total_tokens else 0,
        "longitud_media_articulo_tokens": round(
            sum(longitudes) / len(longitudes), 2
        ) if longitudes else 0,
        "frecuencias": frecuencias.most_common(30),
        "lemas_frecuentes": lemas.most_common(30),
        "categorias_pos": dict(categorias),
        "entidades_frecuentes": [
            {"texto": texto, "tipo": tipo, "frecuencia": cantidad}
            for (texto, tipo), cantidad
            in entidades.most_common(30)
        ],
        "bigramas_frecuentes": [
            {"terminos": list(par), "frecuencia": cantidad}
            for par, cantidad in bigramas.most_common(30)
        ],
        "trigramas_frecuentes": [
            {"terminos": list(terna), "frecuencia": cantidad}
            for terna, cantidad in trigramas.most_common(30)
        ],
        "entidades_por_patrones": {
            tipo: conteo.most_common(30) for tipo, conteo in entidades_juridicas.items()
        },
        "colocaciones_pmi": asociaciones,
        "concordancias_kwic": concordancias,
        "colocaciones_juridicas": colocaciones,
        "glosario": GLOSARIO,
        "limitaciones_ner": (
            "El modelo general de español puede clasificar "
            "incorrectamente entidades jurídicas. "
            "Sus etiquetas requieren interpretación humana."
        ),
    }

    if args.publicable:
        manifiesto = CORPUS.parent.parent / "embeddings" / "metadatos_publicables.json"
        fragmentos = json.loads(manifiesto.read_bytes())["fragmentos"]
        longitudes_fragmento = [
            sum(not token.is_space and not token.is_punct for token in nlp.make_doc(f["texto"]))
            for f in fragmentos
        ]
        resultados["fragmentos"] = len(fragmentos)
        resultados["longitud_media_fragmento_tokens"] = round(
            sum(longitudes_fragmento) / len(longitudes_fragmento), 2
        )
    salida.write_text(
        json.dumps(
            resultados,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print("Artículos:", len(articulos))
    print("Tokens:", total_tokens)
    print("Tipos:", len(tipos))
    print("Relación tipo/token:", resultados["relacion_tipo_token"])
    print("Longitud media:", resultados["longitud_media_articulo_tokens"])
    print("Archivo generado:", salida)
    print("ANALISIS LINGUISTICO: COMPLETADO")


if __name__ == "__main__":
    main()
