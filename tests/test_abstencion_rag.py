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
            "resultados_generales": [{"articulo": "1"}],
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

    def test_consultas_explicitas_responden_con_el_fallo_sin_texto_historico(self):
        preguntas = [f"¿Está vigente el artículo {n}?" for n in (*range(47, 76), 162)]
        preguntas.extend((
            "¿Qué disponían los artículos 47 a 75?",
            "¿Qué dicen los artículos 46 y 162?",
            "¿Qué establecían los artículos 46 hasta 76?",
            "¿Está vigente el art. 162?",
        ))
        for pregunta in preguntas:
            with self.subTest(pregunta=pregunta):
                resultado = preparar_salida_publica(self.generador.responder(pregunta))
                self.assertEqual(resultado["validacion_documental"]["estado"], "TEXTO_INEXEQUIBLE")
                self.assertIn("C-223/17", resultado["respuesta"])
                self.assertEqual(resultado["fuentes_recuperadas"], [])
        self.generador.recuperador.buscar.assert_not_called()
        self.generador.cliente.models.generate_content.assert_not_called()

    def test_filtra_candidatos_historicos_del_contexto_y_fuentes(self):
        def candidato(articulo, texto):
            return {"articulo": articulo, "texto": texto, "id": f"art-{articulo}"}

        self.generador.recuperador.buscar.return_value = {
            "resultados_generales": [
                candidato("162", "TEXTO HISTÓRICO A"),
                candidato("47", "TEXTO HISTÓRICO B"),
                candidato("1", "El Código busca establecer condiciones de convivencia."),
            ],
            "resultados_estructurados_135": [],
            "total_generales": 3,
            "total_estructurados": 0,
        }
        generar = self.generador.cliente.models.generate_content
        generar.return_value = SimpleNamespace(text="El artículo 1 establece el objeto del Código.")
        resultado = preparar_salida_publica(self.generador.responder("¿Cuál es el objeto del Código?"))
        self.assertNotIn("TEXTO HISTÓRICO", generar.call_args.kwargs["contents"])
        self.assertEqual(resultado["total_generales"], 1)
        self.assertEqual([f["articulo"] for f in resultado["fuentes_recuperadas"]], ["1"])

        for articulo in ("162", "73", "93", "223A"):
            with self.subTest(articulo=articulo):
                generar.return_value = SimpleNamespace(text=f"El artículo {articulo} permite el ingreso.")
                resultado = preparar_salida_publica(self.generador.responder("¿Cuál es el objeto del Código?"))
                self.assertEqual(resultado["validacion_documental"]["estado"], "SIN_RESPALDO")
                self.assertEqual(resultado["fuentes_recuperadas"], [])
                self.assertNotIn("permite el ingreso", resultado["respuesta"])

    def test_articulo_sin_cotejo_pendiente_no_llega_al_modelo(self):
        resultado = preparar_salida_publica(self.generador.responder("¿Qué dice el artículo 93?"))
        self.assertEqual(resultado["validacion_documental"]["estado"], "SIN_RESPALDO")
        self.assertEqual(resultado["fuentes_recuperadas"], [])
        self.generador.recuperador.buscar.assert_not_called()
        self.generador.cliente.models.generate_content.assert_not_called()

    def test_solo_candidatos_inexequibles_no_llaman_al_modelo(self):
        self.generador.recuperador.buscar.return_value = {
            "resultados_generales": [{"articulo": "75", "texto": "TEXTO HISTÓRICO"}],
            "resultados_estructurados_135": [],
            "total_generales": 1,
            "total_estructurados": 0,
        }
        resultado = preparar_salida_publica(self.generador.responder("¿Qué regula el Código?"))
        self.assertEqual(resultado["validacion_documental"]["estado"], "SIN_RESPALDO")
        self.assertEqual(resultado["total_generales"], 0)
        self.assertEqual(resultado["fuentes_recuperadas"], [])
        self.generador.cliente.models.generate_content.assert_not_called()

    def test_api_sin_gemini_entrega_el_aviso(self):
        from fastapi.testclient import TestClient
        from backend import servicio_rag

        with patch.object(servicio_rag, "generador", None):
            respuesta = TestClient(servicio_rag.app).post(
                "/consultar", json={"pregunta": "¿Qué permite el artículo 162?"}
            )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["validacion_documental"]["estado"], "TEXTO_INEXEQUIBLE")
        self.assertEqual(respuesta.json()["fuentes_recuperadas"], [])
