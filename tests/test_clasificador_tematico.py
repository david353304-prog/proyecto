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

    def test_materias_externas_con_contexto(self):
        for pregunta in (
            "¿Cuánto cuesta renovar el pasaporte colombiano?",
            "¿Cómo puedo tramitar una visa para Estados Unidos?",
            "¿Cuánto me corresponde de liquidación al renunciar a mi empleo?",
            "¿Qué documentos necesito para registrar una empresa?",
            "¿Cómo puedo solicitar una pensión de vejez?",
            "¿Qué sanción tributaria se aplica por no declarar ingresos?",
            "¿Cuántos días de vacaciones debe pagarme mi empleador?",
        ):
            with self.subTest(pregunta=pregunta):
                self.assertTrue(clasificar_pregunta(pregunta)["fuera_de_dominio"])
        for pregunta in (
            "¿Qué regula la Ley 1801 sobre el ruido de una empresa?",
            "¿Puede la Policía suspender una actividad económica sin licencia?",
            "¿Qué regula el artículo 150 sobre las órdenes de Policía?",
            "¿Qué es el registro de medidas correctivas?",
            "¿Qué dice el Código de Policía sobre los documentos de una actividad económica?",
        ):
            with self.subTest(pregunta=pregunta):
                self.assertFalse(clasificar_pregunta(pregunta)["fuera_de_dominio"])

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
