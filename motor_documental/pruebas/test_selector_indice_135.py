import unittest

from motor_documental.recuperador_combinado_1801 import (
    RecuperadorCombinado1801,
)


class PruebasSelectorIndice135(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.original = RecuperadorCombinado1801()

        cls.experimental = RecuperadorCombinado1801(
            modelo=cls.original.modelo,
            modo_135="experimental",
        )

    def test_modo_predeterminado(self):
        self.assertEqual(
            self.original.estructurado.modo,
            "original",
        )

    def test_modo_experimental(self):
        self.assertEqual(
            self.experimental.estructurado.modo,
            "experimental",
        )

    def test_modelo_compartido(self):
        self.assertIs(
            self.original.modelo,
            self.original.estructurado.modelo,
        )
        self.assertIs(
            self.experimental.modelo,
            self.experimental.estructurado.modelo,
        )

    def test_modo_invalido(self):
        with self.assertRaises(ValueError):
            RecuperadorCombinado1801(
                modelo=self.original.modelo,
                modo_135="inexistente",
            )

    def test_indices_independientes(self):
        self.assertEqual(
            self.original.estructurado.indice.ntotal,
            26,
        )
        self.assertEqual(
            self.experimental.estructurado.indice.ntotal,
            28,
        )


if __name__ == "__main__":
    unittest.main()
