"""Compara ambas unidades de recuperación sin regenerar el índice publicado."""

import argparse
import hashlib
import json
from pathlib import Path
from time import perf_counter

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from motor_documental.buscador_general_1801 import BuscadorGeneral1801
from motor_documental.clasificador_tematico import clasificar_pregunta
from motor_documental.pruebas.evaluar_recuperacion_50 import (
    RUTA_BANCO, calcular_metricas, cargar_banco, normalizar_articulo,
)
from motor_documental.recuperador_combinado_1801 import RecuperadorCombinado1801
from motor_documental.vigencia_rag import (
    IDENTIFICADORES_INEXEQUIBLES, SIMILITUD_MINIMA_DEFINICION,
    alcance_semantico_documental, articulos_para_consulta, corpus_publicable,
)
from motor_documental.indice_publicable import RecuperadorPublicable, huella_corpus


CARPETA = Path(__file__).resolve().parent
MODELO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def evaluar_publicable(banco):
    recuperador = RecuperadorPublicable()
    textos = {n: a["texto"] for n, a in corpus_publicable().items()}
    numeros = list(textos)
    modelo = recuperador.modelo
    vectores = modelo.encode(list(textos.values()), normalize_embeddings=True)
    indice_completo = faiss.IndexFlatIP(recuperador.indice.d)
    indice_completo.add(np.ascontiguousarray(vectores, dtype=np.float32))
    consultas = modelo.encode([c["pregunta"] for c in banco], normalize_embeddings=True)
    consultas = np.ascontiguousarray(consultas, dtype=np.float32)
    diagnostico = {}
    for nombre, indice, metadatos in (
        ("articulo_completo", indice_completo, numeros),
        ("fragmentos", recuperador.indice, recuperador.articulos),
    ):
        _, rankings = indice.search(consultas, indice.ntotal)
        diagnostico[nombre] = calcular_metricas([
            {
                "esperados": list(map(normalizar_articulo, caso["articulos_esperados"])),
                "recuperados": list(dict.fromkeys(metadatos[i] for i in ranking if i >= 0)),
            }
            for caso, ranking in zip(banco, rankings)
        ])
    filas = []
    for caso in banco:
        inicio = perf_counter()
        pregunta = caso["pregunta"]
        consulta_busqueda = pregunta
        permitidos, opciones = set(), {}
        if not clasificar_pregunta(pregunta)["fuera_de_dominio"]:
            permitidos = articulos_para_consulta(pregunta)
            if not permitidos:
                alcance = alcance_semantico_documental(pregunta)
                permitidos = set(alcance)
                consulta_busqueda = next(iter(alcance.values()), pregunta)
                opciones["similitud_minima"] = SIMILITUD_MINIMA_DEFINICION
        recuperados = []
        if permitidos:
            resultado = recuperador.buscar(
                consulta_busqueda, cantidad_general=5, articulos_permitidos=permitidos, **opciones
            )
            recuperados = [a["articulo"] for a in resultado["resultados_generales"]]
        filas.append({
            "id": caso["id"], "esperados": sorted(map(normalizar_articulo, caso["articulos_esperados"])),
            "recuperados": recuperados, "abstencion_documental": not recuperados,
            "recuperacion_ms": round((perf_counter() - inicio) * 1000, 3),
        })
    return {
        "modo": "indice_publico_y_enrutamiento_de_produccion",
        "sha256_corpus_publicable": huella_corpus(),
        "sha256_banco": hashlib.sha256(RUTA_BANCO.read_bytes()).hexdigest(),
        "total_preguntas": len(filas),
        "articulos_publicables": sorted(corpus_publicable(), key=int),
        "fragmentos_indizados": recuperador.indice.ntotal,
        "preguntas_con_referencia_publicable": sum(
            bool(corpus_publicable().keys() & set(f["esperados"])) for f in filas
        ),
        "abstenciones_documentales": sum(f["abstencion_documental"] for f in filas),
        "metricas": calcular_metricas(filas),
        "diagnostico_sin_enrutamiento": {
            "max_tokens_modelo": modelo.max_seq_length,
            "articulos_truncados": sum(
                len(ids) > modelo.max_seq_length for ids in modelo.tokenizer(
                    list(textos.values()), truncation=False, verbose=False
                )["input_ids"]
            ),
            "metricas": diagnostico,
        },
        "resultados": filas,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, required=True)
    parser.add_argument("--publicable", action="store_true", help="Aplica el alcance del servicio público.")
    args = parser.parse_args()
    banco = cargar_banco()
    if args.publicable:
        args.salida.write_text(
            json.dumps(evaluar_publicable(banco), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return
    ruta = CARPETA.parent / "corpus" / "articulos_ley_1801.json"
    datos = ruta.read_bytes()
    articulos = json.loads(datos)
    modelo = SentenceTransformer(MODELO)
    fragmentos = BuscadorGeneral1801(modelo=modelo)
    if {a["numero"] for a in articulos} != {
        str(f["numero_articulo"]) for f in fragmentos.metadatos
    } or fragmentos.indice.metric_type != faiss.METRIC_INNER_PRODUCT:
        raise ValueError("Los índices deben cubrir los mismos artículos y usar producto interno")

    def codificar(textos):
        return np.ascontiguousarray(
            modelo.encode(textos, normalize_embeddings=True), dtype=np.float32
        )

    indice_articulos = faiss.IndexFlatIP(fragmentos.indice.d)
    textos = [a["texto"] for a in articulos]
    indice_articulos.add(codificar(textos))
    estrategias = {
        "articulo_completo": (indice_articulos, [a["numero"] for a in articulos]),
        "fragmentos_faiss": (
            fragmentos.indice, [str(f["numero_articulo"]) for f in fragmentos.metadatos]
        ),
    }
    hibrido = RecuperadorCombinado1801(modelo=modelo)
    registros = {nombre: [] for nombre in (*estrategias, "hibrido_prototipo")}
    for caso in banco:
        esperados = sorted({normalizar_articulo(a) for a in caso["articulos_esperados"]})
        inicio = perf_counter()
        vector = codificar([caso["pregunta"]])
        codificacion_ms = (perf_counter() - inicio) * 1000
        for nombre, (indice, numeros) in estrategias.items():
            inicio = perf_counter()
            _, posiciones = indice.search(vector, indice.ntotal)
            recuperados = list(dict.fromkeys(
                numeros[i] for i in posiciones[0]
                if i >= 0 and numeros[i] not in IDENTIFICADORES_INEXEQUIBLES
            ))[:50]
            registros[nombre].append({
                "id": caso["id"], "esperados": esperados, "recuperados": recuperados,
                "recuperacion_ms": round(codificacion_ms + (perf_counter() - inicio) * 1000, 3),
            })
        inicio = perf_counter()
        resultado = hibrido.buscar(
            caso["pregunta"], cantidad_general=5, cantidad_estructurada=5,
        )
        recuperados = list(dict.fromkeys(
            normalizar_articulo(r["articulo"])
            for r in resultado["resultados_generales"] + resultado["resultados_estructurados_135"]
        ))
        registros["hibrido_prototipo"].append({
            "id": caso["id"], "esperados": esperados, "recuperados": recuperados,
            "recuperacion_ms": round((perf_counter() - inicio) * 1000, 3),
        })

    trampas = json.loads((CARPETA / "banco_preguntas_fuera_dominio.json").read_text(encoding="utf-8"))
    resultado = {
        "modelo": MODELO,
        "sha256_corpus": hashlib.sha256(datos).hexdigest(),
        "banco": RUTA_BANCO.name,
        "sha256_banco": hashlib.sha256(RUTA_BANCO.read_bytes()).hexdigest(),
        "articulos_excluidos": sorted(IDENTIFICADORES_INEXEQUIBLES, key=int),
        "max_tokens_modelo": modelo.max_seq_length,
        "articulos_que_superan_max_tokens": sum(
            len(tokens) > modelo.max_seq_length for tokens in
            modelo.tokenizer(textos, truncation=False, verbose=False)["input_ids"]
        ),
        "total_preguntas": len(banco),
        "evaluacion": {
            nombre: {
                "metricas": calcular_metricas(filas),
                "p50_recuperacion_ms": round(float(np.median([f["recuperacion_ms"] for f in filas])), 3),
                "p95_recuperacion_ms": round(float(np.percentile([f["recuperacion_ms"] for f in filas], 95)), 3),
                "resultados": filas,
            }
            for nombre, filas in registros.items()
        },
        "clasificador": [
            {"id": c["id"], "esperado": c["debe_ser_fuera_de_dominio"],
             "obtenido": clasificar_pregunta(c["pregunta"])["fuera_de_dominio"]}
            for c in trampas
        ],
    }
    args.salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
