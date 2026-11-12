"""Análisis lingüístico académico de la Ley 1801 de 2016."""

import json
import re
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


def main():
    articulos = json.loads(CORPUS.read_text(encoding="utf-8"))
    nlp = spacy.load("es_core_news_sm")

    textos = [
        str(articulo.get("texto", "")).strip()
        for articulo in articulos
    ]

    textos = [texto for texto in textos if texto]

    frecuencias = Counter()
    lemas = Counter()
    categorias = Counter()
    entidades = Counter()
    bigramas = Counter()
    longitudes = []
    concordancias = {termino: [] for termino in TERMINOS}

    total_tokens = 0
    tipos = set()

    for doc in nlp.pipe(textos, batch_size=16):
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

        texto = doc.text

        for termino in TERMINOS:
            if len(concordancias[termino]) >= 5:
                continue

            patron = re.compile(
                re.escape(termino),
                re.IGNORECASE
            )

            for coincidencia in patron.finditer(texto):
                inicio = max(0, coincidencia.start() - 65)
                fin = min(len(texto), coincidencia.end() + 65)

                concordancias[termino].append(
                    texto[inicio:fin].replace("\n", " ")
                )

                if len(concordancias[termino]) >= 5:
                    break

    corpus_normalizado = [
        re.sub(r"\\s+", " ", texto.lower())
        for texto in textos
    ]

    colocaciones = {
        expresion: sum(
            len(re.findall(
                r"(?<!\\w)" + re.escape(expresion) + r"(?!\\w)",
                texto
            ))
            for texto in corpus_normalizado
        )
        for expresion in EXPRESIONES_JURIDICAS
    }

    resultados = {
        "corpus": "Ley 1801 de 2016",
        "modelo": "es_core_news_sm",
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
