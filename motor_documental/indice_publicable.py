"""Construye y consulta el índice separado del corpus público cotejado."""

import hashlib
import json
import re
from bisect import bisect_left, bisect_right
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
TOKENS_VENTANA = 100
TOKENS_SOLAPAMIENTO = 20


def huella_corpus():
    canonico = json.dumps(corpus_publicable(), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonico.encode("utf-8")).hexdigest()


def ventanas_por_palabra(texto, tokenizer, max_tokens):
    """Conserva palabras completas y verifica cada ventana con tokens especiales."""
    palabras = list(re.finditer(r"\S+", texto))
    inicios = [p.start() for p in palabras]
    finales = [p.end() for p in palabras]
    offsets = tokenizer(
        texto, add_special_tokens=False, truncation=False,
        return_offsets_mapping=True, verbose=False,
    )["offset_mapping"]
    inicios_token = [ini for ini, _ in offsets]
    inicio = 0
    while inicio < len(palabras):
        a = inicios[inicio]
        primer_token = bisect_left(inicios_token, a)
        ultimo_token = min(primer_token + TOKENS_VENTANA, len(offsets)) - 1
        limite = offsets[ultimo_token][1] if ultimo_token >= primer_token else finales[-1]
        fin = max(inicio, bisect_right(finales, limite) - 1)
        while fin >= inicio:
            b = finales[fin]
            cantidad = len(tokenizer(texto[a:b], truncation=False, verbose=False)["input_ids"])
            if cantidad <= max_tokens:
                break
            fin -= 1
        if fin < inicio:
            raise ValueError("Una palabra completa excede el límite de tokens del modelo.")
        yield a, b
        if fin == len(palabras) - 1:
            break
        siguiente = bisect_left(inicios_token, b)
        objetivo = inicios_token[max(primer_token, siguiente - TOKENS_SOLAPAMIENTO)]
        inicio = max(inicio + 1, bisect_right(inicios, objetivo) - 1)


def construir():
    modelo = SentenceTransformer(MODELO, revision=REVISION)
    referencia = json.loads((CARPETA.parent / "corpus" / "referencia_normativa.json").read_bytes())
    ampliacion = json.loads((CARPETA.parent / "corpus" / "ampliacion_publicable.json").read_bytes())
    unidades = {u["id"]: u["bloques"] for a in referencia["articulos"] for u in a["unidades"]}
    fragmentos = []
    for a in corpus_publicable().values():
        texto = a["texto"]
        tramos = []
        cursor = len(f"ARTÍCULO {a['articulo']}. {a['titulo']}.")
        for apartado in a["apartados"]:
            for posicion in apartado["bloques"]:
                bloque = unidades[apartado["id"]][posicion]
                inicio_bloque = cursor + 1
                cursor = inicio_bloque + len(bloque)
                if texto[inicio_bloque:cursor] != bloque:
                    raise ValueError(f"Apartado desalineado: {apartado['id']}.")
                tramos.append((inicio_bloque, cursor, apartado["id"]))
        for comienzo, termino in ventanas_por_palabra(texto, modelo.tokenizer, modelo.max_seq_length):
            fragmento = texto[comienzo:termino]
            fragmentos.append({
                **{clave: a[clave] for clave in (
                    "articulo", "id", "titulo", "tema", "jerarquia", "fuente",
                    "url_fuente", "fecha_consulta", "estado_documental",
                )},
                "apartados": list(dict.fromkeys(
                    unidad for izq, der, unidad in tramos if izq < termino and comienzo < der
                )),
                "intervalo_texto": [comienzo, termino],
                "fecha_revision_documental": ampliacion["articulos"].get(
                    a["articulo"], {}
                ).get("fecha_revision_documental"),
                "texto": fragmento,
            })
    vectores = modelo.encode([f["texto"] for f in fragmentos], normalize_embeddings=True)
    indice = faiss.IndexFlatIP(vectores.shape[1])
    indice.add(np.ascontiguousarray(vectores, dtype=np.float32))
    datos = faiss.serialize_index(indice).tobytes()
    INDICE.write_bytes(datos)
    MANIFIESTO.write_text(json.dumps({
        "modelo": MODELO, "revision_modelo": REVISION,
        "sha256_corpus": huella_corpus(), "sha256_indice": hashlib.sha256(datos).hexdigest(),
        "dimension": indice.d, "fragmentos": fragmentos,
        "procedencia_insumos": ampliacion["procedencia_insumos"],
        "segmentacion": {
            "unidad_limite": "palabra_delimitada_por_espacios",
            "objetivo_tokens": TOKENS_VENTANA,
            "objetivo_solapamiento_tokens": TOKENS_SOLAPAMIENTO,
            "limite_tokens_modelo_con_especiales": modelo.max_seq_length,
        },
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

    def buscar(self, pregunta, cantidad_general=5, articulos_permitidos=None, similitud_minima=None):
        vector = self.modelo.encode([pregunta], normalize_embeddings=True)
        similitudes, posiciones = self.indice.search(np.ascontiguousarray(vector, dtype=np.float32), self.indice.ntotal)
        orden = dict.fromkeys(
            self.articulos[i] for i, similitud in zip(posiciones[0], similitudes[0])
            if i >= 0 and (articulos_permitidos is None or self.articulos[i] in articulos_permitidos)
            and (similitud_minima is None or similitud >= similitud_minima)
        )
        return {"resultados_generales": [{"articulo": a} for a in list(orden)[:cantidad_general]]}


if __name__ == "__main__":
    construir()
