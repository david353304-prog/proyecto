import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from motor_documental import generador_respuestas_rag as rag
from motor_documental.salida_segura_rag import preparar_salida_publica


class TestAbstencionRAG(unittest.TestCase):
    def setUp(self):
        self.generador = rag.GeneradorRespuestasRAG.__new__(rag.GeneradorRespuestasRAG)
        self.generador.recuperador = Mock()
        self.generador.recuperador.buscar.return_value = {
            "total_generales": 1,
            "total_estructurados": 0,
        }
        self.generador.cliente = Mock()

    def test_consulta_fuera_de_dominio_no_llega_a_gemini(self):
        resultado = preparar_salida_publica(
            self.generador.responder("¿Cómo impugno un comparendo de tránsito?")
        )
        self.generador.recuperador.buscar.assert_not_called()
        self.generador.cliente.models.generate_content.assert_not_called()
        self.assertEqual(resultado["validacion_documental"]["estado"], "FUERA_DE_DOMINIO")
        self.assertEqual(resultado["fuentes_recuperadas"], [])

    def test_abstencion_y_respuesta_sin_cita_ocultan_afirmaciones(self):
        for texto in (
            f"{rag.MARCADOR_SIN_RESPALDO} Artículo 999.",
            "Puede proceder al pago inmediato.",
        ):
            with self.subTest(texto=texto), patch.object(
                rag, "preparar_contexto", return_value="Artículo: 1\nTexto: Objeto del Código."
            ):
                self.generador.cliente.models.generate_content.return_value = SimpleNamespace(text=texto)
                resultado = preparar_salida_publica(
                    self.generador.responder("¿Cuál es el objeto del Código?")
                )
                self.assertEqual(resultado["validacion_documental"]["estado"], "SIN_RESPALDO")
                self.assertEqual(resultado["fuentes_recuperadas"], [])
                self.assertNotIn(texto, resultado["respuesta"])
