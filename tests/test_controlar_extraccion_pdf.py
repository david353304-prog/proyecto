import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from motor_documental import controlar_extraccion_pdf as modulo


class TestControladorExtraccionPDF(unittest.TestCase):

    def test_rechaza_nombre_no_valido(self):
        resultado = modulo.controlar_extraccion_pdf(None)

        self.assertEqual(resultado["estado"], "error")
        self.assertEqual(
            resultado["codigo"],
            "ARGUMENTOS_INVALIDOS"
        )

    def test_controla_tiempo_agotado(self):
        with patch.object(
            modulo.subprocess,
            "run",
            side_effect=subprocess.TimeoutExpired(
                cmd=["python"],
                timeout=30
            )
        ):
            resultado = modulo.controlar_extraccion_pdf(
                "123e4567-e89b-42d3-a456-426614174001.pdf"
            )

        self.assertEqual(
            resultado["codigo"],
            "TIEMPO_AGOTADO"
        )

    def test_rechaza_salida_excesiva(self):

        def simular_proceso(*args, **kwargs):
            kwargs["stdout"].write(b"x" * 5000)

            return subprocess.CompletedProcess(
                args=args[0],
                returncode=0
            )

        with patch.object(
            modulo.subprocess,
            "run",
            side_effect=simular_proceso
        ):
            resultado = modulo.controlar_extraccion_pdf(
                "123e4567-e89b-42d3-a456-426614174001.pdf"
            )

        self.assertEqual(
            resultado["codigo"],
            "SALIDA_EXCESIVA"
        )

    def test_acepta_resumen_correcto(self):
        respuesta = {
            "estado": "correcto",
            "documento": "123e4567-e89b-42d3-a456-426614174001.pdf",
            "total_paginas_con_texto": 2,
            "total_caracteres": 150
        }

        def simular_proceso(*args, **kwargs):
            kwargs["stdout"].write(
                json.dumps(respuesta).encode()
            )

            return subprocess.CompletedProcess(
                args=args[0],
                returncode=0
            )

        with patch.object(
            modulo.subprocess,
            "run",
            side_effect=simular_proceso
        ):
            resultado = modulo.controlar_extraccion_pdf(
                "123e4567-e89b-42d3-a456-426614174001.pdf"
            )

        self.assertEqual(resultado["estado"], "correcto")
        self.assertEqual(
            resultado["total_paginas_con_texto"],
            2
        )
        self.assertEqual(
            resultado["total_caracteres"],
            150
        )

    def test_proceso_real_rechaza_pdf_inexistente(self):
        nombre = "123e4567-e89b-42d3-a456-426614174000.pdf"

        resultado = modulo.controlar_extraccion_pdf(nombre)

        self.assertEqual(resultado["estado"], "error")
        self.assertEqual(
            resultado["codigo"],
            "EXTRACCION_RECHAZADA"
        )


    def test_rechaza_respuestas_invalidas(self):
        respuestas = [
            {
                "estado": "correcto",
                "documento": "otro_123e4567-e89b-42d3-a456-426614174001.pdf",
                "total_paginas_con_texto": 1,
                "total_caracteres": 100
            },
            {
                "estado": "correcto",
                "documento": "123e4567-e89b-42d3-a456-426614174001.pdf",
                "total_paginas_con_texto": -1,
                "total_caracteres": 100
            },
            {
                "estado": "correcto",
                "documento": "123e4567-e89b-42d3-a456-426614174001.pdf",
                "total_paginas_con_texto": 201,
                "total_caracteres": 100
            },
            {
                "estado": "correcto",
                "documento": "123e4567-e89b-42d3-a456-426614174001.pdf",
                "total_paginas_con_texto": True,
                "total_caracteres": 100
            },
            {
                "estado": "correcto",
                "documento": "123e4567-e89b-42d3-a456-426614174001.pdf",
                "total_paginas_con_texto": 1,
                "total_caracteres": -1
            },
            {
                "estado": "correcto",
                "documento": "123e4567-e89b-42d3-a456-426614174001.pdf",
                "total_paginas_con_texto": 1,
                "total_caracteres": 1000001
            },
            {
                "estado": "correcto",
                "documento": "123e4567-e89b-42d3-a456-426614174001.pdf",
                "total_paginas_con_texto": 1,
                "total_caracteres": "100"
            }
        ]

        for respuesta in respuestas:
            with self.subTest(respuesta=respuesta):

                def simular_proceso(*args, **kwargs):
                    kwargs["stdout"].write(
                        json.dumps(respuesta).encode()
                    )

                    return subprocess.CompletedProcess(
                        args=args[0],
                        returncode=0
                    )

                with patch.object(
                    modulo.subprocess,
                    "run",
                    side_effect=simular_proceso
                ):
                    resultado = modulo.controlar_extraccion_pdf(
                        "123e4567-e89b-42d3-a456-426614174001.pdf"
                    )

                self.assertEqual(
                    resultado["codigo"],
                    "RESPUESTA_INVALIDA"
                )

    def test_rechaza_codigo_error_desconocido(self):
        respuesta = {
            "estado": "error",
            "codigo": "CODIGO_NO_PERMITIDO"
        }

        def simular_proceso(*args, **kwargs):
            kwargs["stdout"].write(
                json.dumps(respuesta).encode()
            )

            return subprocess.CompletedProcess(
                args=args[0],
                returncode=1
            )

        with patch.object(
            modulo.subprocess,
            "run",
            side_effect=simular_proceso
        ):
            resultado = modulo.controlar_extraccion_pdf(
                "123e4567-e89b-42d3-a456-426614174001.pdf"
            )

        self.assertEqual(resultado["estado"], "error")
        self.assertEqual(
            resultado["codigo"],
            "EXTRACCION_FALLIDA"
        )


    def test_rechaza_codigos_error_malformados(self):
        codigos_invalidos = [
            [],
            {},
            None,
            123
        ]

        nombre = (
            "123e4567-e89b-42d3-a456-426614174001.pdf"
        )

        for codigo in codigos_invalidos:
            with self.subTest(codigo=codigo):
                respuesta = {
                    "estado": "error",
                    "codigo": codigo
                }

                def simular_proceso(*args, **kwargs):
                    kwargs["stdout"].write(
                        json.dumps(respuesta).encode("utf-8")
                    )

                    return subprocess.CompletedProcess(
                        args=args[0],
                        returncode=1
                    )

                with patch.object(
                    modulo.subprocess,
                    "run",
                    side_effect=simular_proceso
                ):
                    resultado = (
                        modulo.controlar_extraccion_pdf(nombre)
                    )

                self.assertEqual(
                    resultado,
                    {
                        "estado": "error",
                        "codigo": "EXTRACCION_FALLIDA"
                    }
                )


if __name__ == "__main__":
    unittest.main()


class TestMetadatosVaciosPDF(unittest.TestCase):
    """Verifica que una extracción exitosa no tenga metadatos vacíos."""

    def test_rechaza_paginas_o_caracteres_en_cero(self):
        import io
        import json
        import tempfile
        from unittest.mock import patch

        from motor_documental.controlar_extraccion_pdf import (
            controlar_extraccion_pdf,
        )

        nombre = "12345678-1234-1234-1234-123456789abc.pdf"

        casos = [
            (0, 100),
            (1, 0),
            (0, 0),
            (-1, 100),
            (1, -1),
            (201, 100),
            (1, 1000001),
            (1.5, 100),
            (1, 10.5),
            (True, 100),
            (1, False),
            ("1", 100),
            (1, "100"),
            (None, 100),
            (1, None),
        ]

        for paginas, caracteres in casos:
            with self.subTest(
                paginas=paginas,
                caracteres=caracteres,
            ):
                respuesta_python = {
                    "estado": "correcto",
                    "documento": nombre,
                    "total_paginas_con_texto": paginas,
                    "total_caracteres": caracteres,
                }

                class ProcesoSimulado:
                    returncode = 0

                def ejecutar_simulado(*args, **kwargs):
                    salida = kwargs["stdout"]
                    salida.write(
                        json.dumps(respuesta_python).encode("utf-8")
                    )
                    return ProcesoSimulado()

                with patch(
                    "motor_documental.controlar_extraccion_pdf.subprocess.run",
                    side_effect=ejecutar_simulado,
                ):
                    resultado = controlar_extraccion_pdf(nombre)

                self.assertEqual(
                    resultado,
                    {
                        "estado": "error",
                        "codigo": "RESPUESTA_INVALIDA",
                    },
                )
