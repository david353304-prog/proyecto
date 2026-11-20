"""Comprueba identidad del banco, rankings y procedencia del índice histórico."""

import hashlib
import json
from pathlib import Path

import faiss
import numpy as np

from motor_documental.corpus.contrastar_corpus import clave_textual
from motor_documental.pruebas.evaluar_recuperacion_50 import (
    RUTA_BANCO, calcular_metricas, cargar_banco, normalizar_articulo,
)
from motor_documental.vigencia_rag import IDENTIFICADORES_INEXEQUIBLES, corpus_publicable


MOTOR = Path(__file__).resolve().parents[1]


def huellas_del_json(ruta):
    # Git puede convertir los finales de línea durante el checkout.
    lf = ruta.read_bytes().replace(b"\r\n", b"\n")
    return {hashlib.sha256(datos).hexdigest() for datos in (lf, lf.replace(b"\n", b"\r\n"))}


def auditar(ruta_metricas):
    banco = cargar_banco()
    esperados = [
        (p["id"], sorted({normalizar_articulo(a) for a in p["articulos_esperados"]}))
        for p in banco
    ]
    medicion = json.loads(ruta_metricas.read_bytes())
    if medicion["sha256_banco"] not in huellas_del_json(RUTA_BANCO) or medicion["total_preguntas"] != len(banco):
        raise ValueError("La medición no pertenece al banco activo.")
    for nombre, estrategia in medicion["evaluacion"].items():
        filas = estrategia["resultados"]
        if [(f["id"], f["esperados"]) for f in filas] != esperados:
            raise ValueError(f"Casos desalineados: {nombre}.")
        if any(IDENTIFICADORES_INEXEQUIBLES.intersection(f["recuperados"]) for f in filas):
            raise ValueError(f"El ranking contiene artículos excluidos: {nombre}.")
        if calcular_metricas(filas) != estrategia["metricas"]:
            raise ValueError(f"Métricas no reproducibles desde el ranking: {nombre}.")

    ruta_historico = MOTOR / "corpus" / "articulos_ley_1801.json"
    historico = {a["numero"]: a["texto"] for a in json.loads(ruta_historico.read_bytes())}
    if medicion["sha256_corpus"] not in huellas_del_json(ruta_historico):
        raise ValueError("El corpus de la medición no coincide con el histórico.")
    # Esta auditoría histórica comprueba únicamente el subconjunto original.
    numeros_originales = json.loads((MOTOR / "corpus" / "alcance_publicable.json").read_bytes())["articulos"]
    publicable = {n: corpus_publicable()[n] for n in numeros_originales}
    for numero, registro in publicable.items():
        if clave_textual(registro["texto"]) != clave_textual(historico[numero]):
            raise ValueError(f"Texto cotejado sin equivalente histórico: {numero}.")

    carpeta = MOTOR / "embeddings"
    indice = faiss.read_index(str(carpeta / "indice_ley_1801.faiss"))
    vectores = np.load(carpeta / "vectores_ley_1801.npy", allow_pickle=False)
    metadatos = json.loads((carpeta / "metadatos_ley_1801.json").read_bytes())
    fragmentos = json.loads((MOTOR / "fragmentos" / "fragmentos_ley_1801.json").read_bytes())
    if (
        indice.metric_type != faiss.METRIC_INNER_PRODUCT
        or vectores.shape != (indice.ntotal, indice.d)
        or not np.array_equal(indice.reconstruct_n(0, indice.ntotal), vectores)
        or not np.allclose(np.linalg.norm(vectores, axis=1), 1, atol=1e-5)
        or [(f["id"], f["texto"]) for f in metadatos] != [(f["id"], f["texto"]) for f in fragmentos]
    ):
        raise ValueError("FAISS, vectores y textos de los fragmentos están desalineados.")
    aptos = [f for f in metadatos if str(f["numero_articulo"]) in publicable]
    for f in aptos:
        texto = " ".join(clave_textual(f["texto"]))
        canonico = " ".join(clave_textual(publicable[str(f["numero_articulo"])]["texto"]))
        if f" {texto} " not in f" {canonico} ":
            raise ValueError(f"El fragmento apto no figura en el texto cotejado: {f['id']}.")
    if {str(f["numero_articulo"]) for f in aptos} != publicable.keys():
        raise ValueError("Faltan vectores de artículos publicables.")
    return {
        "preguntas": len(banco),
        "estrategias_auditadas": list(medicion["evaluacion"]),
        "sha256_banco": medicion["sha256_banco"],
        "articulos_publicables": list(publicable),
        "vectores_totales": indice.ntotal,
        "vectores_publicables": len(aptos),
        "dimension": indice.d,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "metricas", type=Path, nargs="?",
        default=Path(__file__).with_name("comparacion_recuperacion_banco_revisado.json"),
    )
    print(json.dumps(auditar(parser.parse_args().metricas), ensure_ascii=False, indent=2))
