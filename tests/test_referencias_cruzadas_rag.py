import unittest

from motor_documental.validador_respuestas_rag import (
    ValidadorRespuestasRAG,
)


class TestReferenciasCruzadasRAG(unittest.TestCase):

    def setUp(self):
        self.validador = ValidadorRespuestasRAG()

    def tipos_advertencia(self, respuesta, contexto):
        resultado = self.validador.validar(
            respuesta=respuesta,
            contexto=contexto,
        )
        return {
            advertencia["tipo"]
            for advertencia in resultado["advertencias"]
        }

    def test_referencia_ley_599(self):
        contexto = """
[GENERAL CONSERVADO 1]
Artículo: 150
Texto: ARTÍCULO 150. Orden de Policía.
El incumplimiento configura el tipo penal
establecido en el artículo 454 de la Ley 599 de 2000.
"""
        respuesta = (
            "El artículo 150 de la Ley 1801 remite "
            "al artículo 454 de la Ley 599 de 2000."
        )

        self.assertNotIn(
            "ARTICULO_NO_EN_CONTEXTO",
            self.tipos_advertencia(respuesta, contexto),
        )

    def test_referencia_codigo_general_proceso(self):
        contexto = """
[GENERAL CONSERVADO 1]
Artículo: 206
Texto: ARTÍCULO 206. Atribuciones.
Ejecutar las comisiones que trata el artículo 38
del Código General del Proceso.
"""
        respuesta = (
            "El artículo 206 menciona el artículo 38 "
            "del Código General del Proceso."
        )

        self.assertNotIn(
            "ARTICULO_NO_EN_CONTEXTO",
            self.tipos_advertencia(respuesta, contexto),
        )

    def test_referencia_numeral_articulo_205(self):
        contexto = """
[GENERAL CONSERVADO 1]
Artículo: 206
Texto: ARTÍCULO 206. Atribuciones.
Restitución y protección de bienes inmuebles,
diferentes a los descritos en el numeral 17
del artículo 205.
"""
        respuesta = (
            "El artículo 206 excluye los bienes "
            "descritos en el numeral 17 del artículo 205."
        )

        tipos = self.tipos_advertencia(respuesta, contexto)

        self.assertNotIn("ARTICULO_NO_EN_CONTEXTO", tipos)
        self.assertNotIn("NUMERAL_NO_EN_CONTEXTO", tipos)

    def test_referencia_ley_1453(self):
        contexto = """
[GENERAL CONSERVADO 1]
Artículo: 95
Texto: ARTÍCULO 95. Equipos terminales móviles.
Base de datos negativa de que trata el artículo 106
de la Ley 1453 de 2011.
"""
        respuesta = (
            "El artículo 95 remite al artículo 106 "
            "de la Ley 1453 de 2011."
        )

        self.assertNotIn(
            "ARTICULO_NO_EN_CONTEXTO",
            self.tipos_advertencia(respuesta, contexto),
        )

    def test_articulo_inventado_sigue_bloqueado(self):
        contexto = """
[GENERAL CONSERVADO 1]
Artículo: 150
Texto: ARTÍCULO 150. Orden de Policía.
"""
        respuesta = (
            "Según el artículo 454 de la Ley 599 de 2000, "
            "se establece esta obligación."
        )

        self.assertIn(
            "ARTICULO_NO_EN_CONTEXTO",
            self.tipos_advertencia(respuesta, contexto),
        )


if __name__ == "__main__":
    unittest.main()
