import unittest

from motor_documental.validador_respuestas_rag import ValidadorRespuestasRAG


CONTEXTO = """
CONTEXTO JURÍDICO RECUPERADO
[GENERAL 1]
Artículo: 218
Texto: Fragmento documental de prueba.
[GENERAL 2]
Artículo: 219
Texto: Fragmento documental de prueba.
FIN DEL CONTEXTO JURÍDICO RECUPERADO
"""

CONTEXTO_223A = """
CONTEXTO JURÍDICO RECUPERADO
=== ARTÍCULO 223A ===
[223A NUMERAL 2]
Texto completo: Fragmento documental de prueba.
FIN DEL CONTEXTO JURÍDICO RECUPERADO
"""


class TestValidadorRespuestasRAG(unittest.TestCase):

    def setUp(self):
        self.validador = ValidadorRespuestasRAG()

    def verificar(self, respuesta, contexto, esperadas):
        resultado = self.validador.validar(respuesta, contexto)
        obtenidas = [
            alerta["tipo"]
            for alerta in resultado["advertencias"]
        ]

        self.assertEqual(sorted(obtenidas), sorted(esperadas))

        estado_esperado = (
            "REQUIERE_REVISION"
            if esperadas
            else "PENDIENTE_VALIDACION"
        )
        self.assertEqual(resultado["estado"], estado_esperado)

    def test_articulo_presente(self):
        self.verificar("Según el artículo 218, existe una disposición.", CONTEXTO, [])

    def test_articulo_ausente(self):
        self.verificar("Según el artículo 250, existe una disposición.", CONTEXTO,
                       ["ARTICULO_NO_EN_CONTEXTO"])

    def test_dos_articulos_presentes(self):
        self.verificar("Los artículos 218 y 219 regulan estas materias.", CONTEXTO, [])

    def test_segundo_articulo_ausente(self):
        self.verificar("Los artículos 218 y 250 regulan estas materias.", CONTEXTO,
                       ["ARTICULO_NO_EN_CONTEXTO"])

    def test_enumeracion_con_comas(self):
        self.verificar("Los artículos 218, 219 y 250 regulan estas materias.", CONTEXTO,
                       ["ARTICULO_NO_EN_CONTEXTO"])

    def test_enumeracion_abreviada(self):
        self.verificar("Los arts. 218, 219 y 250 regulan estas materias.", CONTEXTO,
                       ["ARTICULO_NO_EN_CONTEXTO"])

    def test_223a_presente(self):
        self.verificar("El artículo 223A contiene disposiciones.", CONTEXTO_223A, [])

    def test_223a_ausente(self):
        self.verificar("El artículo 223A contiene disposiciones.", CONTEXTO,
                       ["ARTICULO_NO_EN_CONTEXTO"])

    def test_223_distinto_de_223a(self):
        self.verificar("El artículo 223 contiene disposiciones.", CONTEXTO_223A,
                       ["ARTICULO_NO_EN_CONTEXTO"])

    def test_generalizacion_223a(self):
        self.verificar("El artículo 223A aplica a todas las medidas correctivas.",
                       CONTEXTO_223A,
                       ["POSIBLE_GENERALIZACION_ARTICULO_223A"])

    def test_confusion_plazo(self):
        self.verificar(
            "La aceptación de responsabilidad ocurre en tres días hábiles.",
            CONTEXTO,
            ["POSIBLE_CONFUSION_PLAZO_223A"],
        )

    def test_plazo_despues_articulo(self):
        self.verificar(
            "Según el artículo 218, y 3 días después se realiza el trámite.",
            CONTEXTO, [],
        )

    def test_cantidad_dias(self):
        self.verificar(
            "El artículo 218 establece un procedimiento de 5 días.",
            CONTEXTO, [],
        )

    def test_cantidad_multas(self):
        self.verificar(
            "El artículo 218 contempla 4 multas en este ejemplo.",
            CONTEXTO, [],
        )

    def test_articulos_separados(self):
        self.verificar(
            "El artículo 218 es relevante. También se cita el artículo 250.",
            CONTEXTO,
            ["ARTICULO_NO_EN_CONTEXTO"],
        )




class TestNumeralesRAG(unittest.TestCase):

    def setUp(self):
        self.validador = ValidadorRespuestasRAG()

    def comprobar(self, respuesta, contexto, esperadas):
        resultado = self.validador.validar(respuesta, contexto)
        obtenidas = sorted(
            advertencia["tipo"]
            for advertencia in resultado["advertencias"]
        )
        self.assertEqual(obtenidas, sorted(esperadas))

    def test_numeral_135_presente(self):
        contexto = """
        === REGISTROS ESTRUCTURADOS ===
        [ESTRUCTURADO 1]
        Artículo: 135
        Numeral: 2
        """
        self.comprobar(
            "Numeral 2 del artículo 135.",
            contexto,
            [],
        )

    def test_numeral_135_ausente(self):
        contexto = """
        === REGISTROS ESTRUCTURADOS ===
        [ESTRUCTURADO 1]
        Artículo: 135
        Numeral: 2
        """
        self.comprobar(
            "Numeral 5 del artículo 135.",
            contexto,
            ["NUMERAL_NO_EN_CONTEXTO"],
        )

    def test_numeral_223a_formato_directo(self):
        contexto = """
        === ARTÍCULO 223A ===
        [223A NUMERAL 2]
        Texto completo: Fragmento de prueba.
        """
        self.comprobar(
            "Numeral 2 del artículo 223A.",
            contexto,
            [],
        )

    def test_223a_posicion_distinta_del_numeral(self):
        contexto = """
        === NUMERALES COMPLETOS DEL ARTÍCULO 223A ===
        [223A NUMERAL 1]
        Artículo: 223A
        Numeral: 3
        """
        self.comprobar(
            "Numeral 1 del artículo 223A.",
            contexto,
            ["NUMERAL_NO_EN_CONTEXTO"],
        )
        self.comprobar(
            "Numeral 3 del artículo 223A.",
            contexto,
            [],
        )

    def test_223a_varios_registros(self):
        contexto = """
        === NUMERALES COMPLETOS DEL ARTÍCULO 223A ===
        [223A NUMERAL 1]
        Artículo: 223A
        Numeral: 3
        [223A NUMERAL 2]
        Artículo: 223A
        Numeral: 5
        """
        self.comprobar(
            "Numeral 5 del artículo 223A.",
            contexto,
            [],
        )
        self.comprobar(
            "Numeral 2 del artículo 223A.",
            contexto,
            ["NUMERAL_NO_EN_CONTEXTO"],
        )

    def test_numeral_de_articulo_diferente(self):
        contexto = """
        === ARTÍCULO 223A ===
        [223A NUMERAL 2]
        """
        self.comprobar(
            "Numeral 2 del artículo 135.",
            contexto,
            ["ARTICULO_NO_EN_CONTEXTO"],
        )

if __name__ == "__main__":
    unittest.main()
