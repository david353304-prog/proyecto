import unittest
from motor_documental.salida_segura_rag import preparar_salida_publica


class FuentesPublicasTests(unittest.TestCase):
    def test_fragmentos_limitados_y_sin_campos_internos(self):
        resultado = {
            "pregunta": "¿Qué es una orden?", "respuesta": "Respuesta",
            "respuesta_original": "NO PUBLICAR",
            "resultados_recuperados": {
                "resultados_generales": [{
                    "articulo": "1", "texto": "Texto normativo",
                    "url_fuente": "https://ejemplo.org/norma", "interno": "SECRETO"
                }],
                "resultados_estructurados_135": []
            }
        }
        salida = preparar_salida_publica(resultado)
        self.assertEqual(salida["fuentes_recuperadas"][0]["articulo"], "1")
        self.assertNotIn("respuesta_original", salida)
        self.assertNotIn("interno", salida["fuentes_recuperadas"][0])

    def test_fuentes_vacias_y_url_no_segura(self):
        salida = preparar_salida_publica({"resultados_recuperados": {
            "resultados_generales": [{"articulo": "2", "texto": "Texto", "url_fuente": "javascript:alert(1)"}]
        }})
        self.assertEqual(salida["fuentes_recuperadas"][0]["url_fuente"], "")
        self.assertEqual(preparar_salida_publica({})["fuentes_recuperadas"], [])


if __name__ == "__main__":
    unittest.main()
