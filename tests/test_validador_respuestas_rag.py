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


class TestCorrespondenciaMedidas135(unittest.TestCase):

    CONTEXTO_135 = """
    === REGISTROS ESTRUCTURADOS ===

    [ESTRUCTURADO 1]
    Artículo: 135
    Numeral: 11
    Sección: C
    Comportamiento: Contravenir los usos específicos del suelo.
    Medidas correctivas registradas: Multa especial por infracción urbanística; Suspensión definitiva de la actividad.

    [ESTRUCTURADO 2]
    Artículo: 135
    Numeral: 12
    Sección: C
    Comportamiento: Facilitar usos del suelo no autorizados.
    Medidas correctivas registradas: Multa especial por infracción urbanística; Demolición de obra; Construcción, cerramiento, reparación o mantenimiento de inmueble.
    """

    def setUp(self):
        self.validador = ValidadorRespuestasRAG()

    def comprobar(self, respuesta, esperadas):
        resultado = self.validador.validar(
            respuesta=respuesta,
            contexto=self.CONTEXTO_135,
        )

        obtenidas = sorted(
            advertencia["tipo"]
            for advertencia in resultado["advertencias"]
        )

        self.assertEqual(obtenidas, sorted(esperadas))

        estado_esperado = (
            "REQUIERE_REVISION"
            if esperadas
            else "PENDIENTE_VALIDACION"
        )

        self.assertEqual(
            resultado["estado"],
            estado_esperado,
        )

    def test_numeral_11_suspension_correcta(self):
        self.comprobar(
            "El numeral 11 del artículo 135 contempla "
            "la suspensión definitiva de la actividad.",
            [],
        )

    def test_numeral_12_demolicion_correcta(self):
        self.comprobar(
            "El numeral 12 del artículo 135 contempla "
            "la demolición de obra.",
            [],
        )

    def test_numeral_11_demolicion_incorrecta(self):
        self.comprobar(
            "El numeral 11 del artículo 135 contempla "
            "la demolición de obra.",
            ["MEDIDA_NO_CORRESPONDE_NUMERAL"],
        )

    def test_numeral_12_suspension_incorrecta(self):
        self.comprobar(
            "El numeral 12 del artículo 135 contempla "
            "la suspensión definitiva de la actividad.",
            ["MEDIDA_NO_CORRESPONDE_NUMERAL"],
        )

    def test_negacion_correcta(self):
        self.comprobar(
            "El numeral 11 del artículo 135 no contempla "
            "la demolición de obra.",
            [],
        )

    def test_comparacion_correcta(self):
        self.comprobar(
            "El numeral 11 del artículo 135 contempla "
            "la suspensión definitiva de la actividad, "
            "mientras que el numeral 12 del artículo 135 "
            "contempla la demolición de obra.",
            [],
        )

    def test_respuesta_sin_medida(self):
        self.comprobar(
            "El numeral 11 del artículo 135 se refiere "
            "a contravenir los usos específicos del suelo.",
            [],
        )


    def test_verbo_permite_medida_incorrecta(self):
        self.comprobar(
            "El numeral 11 del artículo 135 permite "
            "la demolición de obra.",
            ["MEDIDA_NO_CORRESPONDE_NUMERAL"],
        )

    def test_dos_medidas_segunda_incorrecta(self):
        self.comprobar(
            "El numeral 11 del artículo 135 contempla "
            "la multa especial por infracción urbanística "
            "y la demolición de obra.",
            ["MEDIDA_NO_CORRESPONDE_NUMERAL"],
        )


    def test_medida_negada_despues_de_correcta(self):
        self.comprobar(
            "El numeral 11 del artículo 135 contempla "
            "la multa especial por infracción urbanística, "
            "pero no la demolición de obra.",
            [],
        )

    def test_medida_mencionada_como_diferencia(self):
        self.comprobar(
            "El numeral 11 del artículo 135 contempla "
            "la suspensión definitiva de la actividad, "
            "a diferencia de la demolición de obra.",
            [],
        )


    def test_negacion_con_adverbio(self):
        self.comprobar(
            "El numeral 11 del artículo 135 contempla "
            "la multa especial por infracción urbanística, "
            "pero no necesariamente la demolición de obra.",
            [],
        )

    def test_negacion_sin_articulo(self):
        self.comprobar(
            "El numeral 11 del artículo 135 contempla "
            "la multa especial por infracción urbanística, "
            "pero no demolición de obra.",
            [],
        )

    def test_comparacion_sin_articulo(self):
        self.comprobar(
            "El numeral 11 del artículo 135 contempla "
            "la suspensión definitiva de la actividad, "
            "a diferencia de demolición de obra.",
            [],
        )






    def test_atribucion_con_corresponde(self):
        self.comprobar(
            "Según el numeral 11 del artículo 135, "
            "corresponde la demolición de obra.",
            ["MEDIDA_NO_CORRESPONDE_NUMERAL"],
        )

    def test_atribucion_con_dispone(self):
        self.comprobar(
            "El numeral 11 del artículo 135 dispone "
            "la demolición de obra.",
            ["MEDIDA_NO_CORRESPONDE_NUMERAL"],
        )

    def test_negacion_con_tampoco(self):
        self.comprobar(
            "El numeral 11 del artículo 135 contempla "
            "la multa especial por infracción urbanística, "
            "pero tampoco la demolición de obra.",
            [],
        )


if __name__ == "__main__":
    unittest.main()
