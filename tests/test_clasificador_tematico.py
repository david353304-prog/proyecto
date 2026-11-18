import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from motor_documental.clasificador_tematico import (
    clasificar_pregunta,
    libro_de_articulo,
    orientar_por_libro,
)


class PruebasClasificadorTematico(unittest.TestCase):
    def test_banco_fuera_de_dominio(self):
        ruta = RAIZ / "motor_documental/pruebas/banco_preguntas_fuera_dominio.json"
        for caso in json.loads(ruta.read_text(encoding="utf-8")):
            with self.subTest(caso["id"]):
                resultado = clasificar_pregunta(caso["pregunta"])
                self.assertEqual(
                    resultado["fuera_de_dominio"],
                    caso["debe_ser_fuera_de_dominio"],
                )

    def test_libros_por_articulo(self):
        self.assertEqual(libro_de_articulo("1"), "PRIMERO")
        self.assertEqual(libro_de_articulo("135"), "SEGUNDO")
        self.assertEqual(libro_de_articulo("223A"), "TERCERO")

    def test_orientar_por_libro_conserva_articulos_clave(self):
        resultados = [
            {"articulo": "5"},
            {"articulo": "200"},
            {"articulo": "135", "origen_recuperacion": "titulo_numero"},
        ]
        orden = [r["articulo"] for r in orientar_por_libro(resultados, "TERCERO")]
        self.assertEqual(orden, ["135", "200", "5"])

    def test_pregunta_vacia(self):
        with self.assertRaises(ValueError):
            clasificar_pregunta("  ")


if __name__ == "__main__":
    unittest.main()