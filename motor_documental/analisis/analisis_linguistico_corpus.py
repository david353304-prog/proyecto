"""Análisis lingüístico académico de la Ley 1801 de 2016."""

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
                 r"inspector(?:es)? de Policía|alcald(?:e|es|ía|ías)|corregidor(?:es)?)\b",
    "LUGAR": r"\b(?:Colombia|Bogotá|espacio público|territorio nacional)\b",
    "MONTO": r"\b\d+(?:[.,]\d+)?\s*(?:%|pesos\b|(?:sml[dv]v|uvb|uvt)\b)|"
             r"\b(?:\d+|\(\d+\))\s*salarios mínimos(?: legales)?\b",
    "PLAZO": r"\b(?:\d+|[a-záéíóú]+\s+\(\d+\))\s+"
             r"(?:horas?|días?|mes(?:es)?|años?)(?:\s+hábiles)?\b",
}


def main():
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
                m[0].casefold() for m in re.finditer(patron, texto, re.I)
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
        "corpus": "Ley 1801 de 2016",
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

    SALIDA.write_text(
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
    print("Archivo generado:", SALIDA)
    print("ANALISIS LINGUISTICO: COMPLETADO")


if __name__ == "__main__":
    main()
