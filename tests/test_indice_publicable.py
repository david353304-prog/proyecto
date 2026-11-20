import hashlib
import json
import unittest
from collections import defaultdict

import faiss
import numpy as np

from motor_documental.indice_publicable import INDICE, MANIFIESTO, huella_corpus
from motor_documental.vigencia_rag import corpus_publicable
from motor_documental.indice_publicable import MODELO, REVISION, ventanas_por_palabra
from transformers import AutoTokenizer


class TestIndicePublicable(unittest.TestCase):
    def test_lotes_sociales_excluyen_disposiciones_fuera_del_cotejo(self):
        corpus = corpus_publicable()
        self.assertIn("1. Irrespetar a las autoridades", corpus["35"]["texto"])
        self.assertNotIn("4. Negarse a dar", corpus["35"]["texto"])
        self.assertIn("d) La explotación laboral.", corpus["38"]["texto"])
        self.assertNotIn("7. Permitir que los niños", corpus["38"]["texto"])
        self.assertNotIn("PARÁGRAFO 6o.", corpus["38"]["texto"])

    def test_lotes_conservan_unicamente_paragrafos_y_filas_aprobados(self):
        corpus = corpus_publicable()
        urbanismo = corpus["135"]["texto"]
        self.assertIn("PARÁGRAFO 1o. Cuando se trate de construcciones", urbanismo)
        self.assertIn("PARÁGRAFO 2o. Cuando se realice actuación urbanística", urbanismo)
        self.assertNotIn("PARÁGRAFO 3o.", urbanismo)
        celulares = corpus["95"]["texto"]
        self.assertIn("1. Comprar, alquilar o usar equipo terminal", celulares)
        self.assertIn("Numeral 1 Multa General tipo 2", celulares)
        self.assertNotIn("Numeral 2 Multa General", celulares)
        self.assertNotIn("8. No solicitar", celulares)

    def test_filas_cotejadas_de_evacuacion_y_residuos(self):
        corpus = corpus_publicable()
        self.assertIn("Numeral 1 Multa General Tipo 1", corpus["93"]["texto"])
        self.assertNotIn("Multa especial por ruido", corpus["93"]["texto"])
        residuos = corpus["111"]["texto"]
        self.assertIn("8. Arrojar basura, llantas, residuos o escombros", residuos)
        for numeral in (1, 3):
            self.assertIn(
                f"Numeral {numeral} Participación en programa comunitario", residuos
            )
        self.assertIn("Numeral 8 Multa General tipo 4.", residuos)
        self.assertNotIn("Numeral 2 Participación", residuos)

    def test_ventanas_reales_cubren_texto_sin_cortar_palabras(self):
        corpus = corpus_publicable()
        metadatos = json.loads(MANIFIESTO.read_bytes())
        tokenizer = AutoTokenizer.from_pretrained(MODELO, revision=REVISION)
        limite = metadatos["segmentacion"]["limite_tokens_modelo_con_especiales"]
        por_articulo = defaultdict(list)
        for frag in metadatos["fragmentos"]:
            por_articulo[frag["articulo"]].append(frag)
        for numero, registro in corpus.items():
            with self.subTest(articulo=numero):
                texto = registro["texto"]
                fragmentos = por_articulo[numero]
                intervalos = [tuple(f["intervalo_texto"]) for f in fragmentos]
                self.assertEqual(intervalos, list(ventanas_por_palabra(texto, tokenizer, limite)))
                self.assertEqual(intervalos[0][0], 0)
                self.assertEqual(intervalos[-1][1], len(texto))
                for (inicio, fin), f in zip(intervalos, fragmentos):
                    self.assertTrue(inicio == 0 or texto[inicio - 1].isspace())
                    self.assertTrue(fin == len(texto) or texto[fin].isspace())
                    self.assertEqual(f["texto"], texto[inicio:fin])
                    self.assertLessEqual(len(tokenizer(f["texto"])["input_ids"]), limite)
                for (anterior, fin), (siguiente, nuevo_fin) in zip(intervalos, intervalos[1:]):
                    self.assertLess(anterior, siguiente)
                    self.assertLess(siguiente, fin)
                    self.assertLess(fin, nuevo_fin)
        for numero, excluido in (
            ("111", "numeral-2"), ("222", "paragrafo-6"),
            ("140", "numeral-7"), ("146", "paragrafo-26"),
        ):
            self.assertFalse(any(
                unidad.endswith(f"-{excluido}")
                for f in por_articulo[numero] for unidad in f["apartados"]
            ))

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
        for fragmento in metadatos["fragmentos"]:
            articulo = corpus[fragmento["articulo"]]
            self.assertEqual(fragmento["url_fuente"], articulo["url_fuente"])
            self.assertEqual(fragmento["jerarquia"], articulo["jerarquia"])
            self.assertTrue(fragmento["apartados"])
            self.assertLessEqual(
                set(fragmento["apartados"]), {u["id"] for u in articulo["apartados"]},
            )
        self.assertTrue(np.allclose(np.linalg.norm(indice.reconstruct_n(), axis=1), 1, atol=1e-5))
