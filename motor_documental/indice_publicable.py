"""Construye y consulta el índice separado del corpus público cotejado."""

import hashlib
import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from motor_documental.vigencia_rag import corpus_publicable


CARPETA = Path(__file__).resolve().parent / "embeddings"
INDICE = CARPETA / "indice_publicable.faiss"
MANIFIESTO = CARPETA / "metadatos_publicables.json"
MODELO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
REVISION = "e8f8c211226b894fcb81acc59f3b34ba3efd5f42"


def huella_corpus():
    canonico = json.dumps(corpus_publicable(), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonico.encode("utf-8")).hexdigest()


def construir():
    modelo = SentenceTransformer(MODELO, revision=REVISION)
    fragmentos = []
    for a in corpus_publicable().values():
        texto = a["texto"]
        offsets = modelo.tokenizer(
            texto, add_special_tokens=False, truncation=False,
            return_offsets_mapping=True, verbose=False,
        )["offset_mapping"]
        for inicio in range(0, len(offsets), 80):
            fin = min(inicio + 100, len(offsets))
            fragmento = texto[offsets[inicio][0]:offsets[fin - 1][1]]
            if len(modelo.tokenizer(fragmento)["input_ids"]) > modelo.max_seq_length:
                raise ValueError(f"El fragmento excede el límite del modelo: {a['id']}.")
            fragmentos.append({"articulo": a["articulo"], "texto": fragmento})
            if fin == len(offsets):
                break
    vectores = modelo.encode([f["texto"] for f in fragmentos], normalize_embeddings=True)
    indice = faiss.IndexFlatIP(vectores.shape[1])
    indice.add(np.ascontiguousarray(vectores, dtype=np.float32))
    datos = faiss.serialize_index(indice).tobytes()
    INDICE.write_bytes(datos)
    MANIFIESTO.write_text(json.dumps({
        "modelo": MODELO, "revision_modelo": REVISION,
        "sha256_corpus": huella_corpus(), "sha256_indice": hashlib.sha256(datos).hexdigest(),
        "dimension": indice.d, "fragmentos": fragmentos,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(fragmentos)} fragmentos públicos, dimensión {indice.d}")


class RecuperadorPublicable:
    def __init__(self):
        manifiesto = json.loads(MANIFIESTO.read_bytes())
        datos = INDICE.read_bytes()
        if (
            manifiesto["sha256_corpus"] != huella_corpus()
            or manifiesto["sha256_indice"] != hashlib.sha256(datos).hexdigest()
            or (manifiesto["modelo"], manifiesto["revision_modelo"]) != (MODELO, REVISION)
        ):
            raise ValueError("El índice público requiere regeneración con el corpus cotejado.")
        self.indice = faiss.deserialize_index(np.frombuffer(datos, dtype=np.uint8))
        self.articulos = [f["articulo"] for f in manifiesto["fragmentos"]]
        self.modelo = SentenceTransformer(MODELO, revision=REVISION)
        if (
            self.indice.ntotal != len(self.articulos)
            or set(self.articulos) != corpus_publicable().keys()
            or self.indice.d != self.modelo.get_embedding_dimension()
            or self.indice.metric_type != faiss.METRIC_INNER_PRODUCT
        ):
            raise ValueError("Dimensiones o metadatos del índice público desalineados.")

    def buscar(self, pregunta, cantidad_general=5, articulos_permitidos=None):
        vector = self.modelo.encode([pregunta], normalize_embeddings=True)
        _, posiciones = self.indice.search(np.ascontiguousarray(vector, dtype=np.float32), self.indice.ntotal)
        orden = dict.fromkeys(
            self.articulos[i] for i in posiciones[0]
            if i >= 0 and (articulos_permitidos is None or self.articulos[i] in articulos_permitidos)
        )
        return {"resultados_generales": [{"articulo": a} for a in list(orden)[:cantidad_general]]}


if __name__ == "__main__":
    construir()
