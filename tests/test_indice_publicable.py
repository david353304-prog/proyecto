import hashlib
import json
import unittest

import faiss
import numpy as np

from motor_documental.indice_publicable import INDICE, MANIFIESTO, huella_corpus
from motor_documental.vigencia_rag import corpus_publicable


class TestIndicePublicable(unittest.TestCase):
    def test_indice_real_corresponde_a_la_ampliacion(self):
        corpus = corpus_publicable()
        metadatos = json.loads(MANIFIESTO.read_bytes())
        datos = INDICE.read_bytes()
        indice = faiss.deserialize_index(np.frombuffer(datos, dtype=np.uint8))
        self.assertEqual(metadatos["sha256_corpus"], huella_corpus())
        self.assertEqual(metadatos["sha256_indice"], hashlib.sha256(datos).hexdigest())
        self.assertEqual(indice.metric_type, faiss.METRIC_INNER_PRODUCT)
        self.assertEqual(indice.ntotal, len(metadatos["fragmentos"]))
        self.assertEqual(indice.d, metadatos["dimension"])
        self.assertEqual({f["articulo"] for f in metadatos["fragmentos"]}, corpus.keys())
        self.assertTrue(all(
            f["texto"] in corpus[f["articulo"]]["texto"] for f in metadatos["fragmentos"]
        ))
        self.assertTrue(np.allclose(np.linalg.norm(indice.reconstruct_n(), axis=1), 1, atol=1e-5))
