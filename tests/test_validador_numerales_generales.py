import unittest

from motor_documental.validador_respuestas_rag import (
    ValidadorRespuestasRAG,
)


class TestNumeralesArticulosGenerales(unittest.TestCase):

    def setUp(self):
        self.validador = ValidadorRespuestasRAG()
        self.contexto = (
            "CONTEXTO JURIDICO RECUPERADO\n"
            "[GENERAL CONSERVADO 1]\n"
            "Artículo: 33\n"
            "Texto: ARTÍCULO 33. Comportamientos que afectan "
            "la tranquilidad. 1. En el vecindario se prohíben "
            "los ruidos que afecten la convivencia. "
            "2. En espacio público se regulan otros "
            "comportamientos. PARÁGRAFO 1. Medidas correctivas.\n"
            "Fuente: Ley 1801 de 2016\n"
        )

    def test_numeral_1_presente(self):
        resultado = self.validador.validar(
            "El numeral 1 del artículo 33 regula "
            "comportamientos en el vecindario.",
            self.contexto,
        )
        self.assertFalse(
            any(
                a["tipo"] == "NUMERAL_NO_EN_CONTEXTO"
                for a in resultado["advertencias"]
            )
        )

    def test_numeral_2_presente(self):
        resultado = self.validador.validar(
            "El numeral 2 del artículo 33 regula "
            "comportamientos en espacio público.",
            self.contexto,
        )
        self.assertFalse(
            any(
                a["tipo"] == "NUMERAL_NO_EN_CONTEXTO"
                for a in resultado["advertencias"]
            )
        )

    def test_numeral_99_inexistente(self):
        resultado = self.validador.validar(
            "El numeral 99 del artículo 33 establece "
            "una medida correctiva.",
            self.contexto,
        )
        self.assertTrue(
            any(
                a["tipo"] == "NUMERAL_NO_EN_CONTEXTO"
                for a in resultado["advertencias"]
            )
        )

    def test_numeral_de_otro_articulo_no_se_confunde(self):
        resultado = self.validador.validar(
            "El numeral 1 del artículo 93 regula "
            "este comportamiento.",
            self.contexto,
        )
        self.assertTrue(
            any(
                a["tipo"] == "ARTICULO_NO_EN_CONTEXTO"
                for a in resultado["advertencias"]
            )
        )


if __name__ == "__main__":
    unittest.main()
