import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from motor_documental import ejecutar_extraccion_pdf as modulo


class TestEjecutorExtraccionPDF(unittest.TestCase):

    def test_establece_limites_de_recursos(self):
        with patch.object(modulo.resource, "setrlimit") as limite:
            modulo.establecer_limites()

        self.assertEqual(limite.call_count, 3)

        limite.assert_any_call(
            modulo.resource.RLIMIT_AS,
            (
                modulo.LIMITE_MEMORIA_BYTES,
                modulo.LIMITE_MEMORIA_BYTES
            )
        )

        limite.assert_any_call(
            modulo.resource.RLIMIT_CPU,
            (
                modulo.LIMITE_CPU_SEGUNDOS,
                modulo.LIMITE_CPU_SEGUNDOS
            )
        )

        limite.assert_any_call(
            modulo.resource.RLIMIT_FSIZE,
            (
                modulo.LIMITE_ARCHIVO_BYTES,
                modulo.LIMITE_ARCHIVO_BYTES
            )
        )

    def test_rechaza_argumentos_invalidos(self):
        with patch.object(sys, "argv", ["ejecutor.py"]):
            resultado = modulo.main()

        self.assertEqual(resultado, 2)

    def test_rechaza_documento_inexistente(self):
        nombre = "123e4567-e89b-42d3-a456-426614174000.pdf"

        with patch.object(
            sys,
            "argv",
            ["ejecutor.py", nombre]
        ), patch.object(
            modulo,
            "establecer_limites"
        ):
            resultado = modulo.main()

        self.assertEqual(resultado, 1)

    def test_proceso_rechaza_argumentos_invalidos(self):
        script = (
            Path(__file__).resolve().parents[1]
            / "motor_documental"
            / "ejecutar_extraccion_pdf.py"
        )

        resultado = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True,
            text=True,
            timeout=10
        )

        self.assertEqual(resultado.returncode, 2)

        datos = json.loads(resultado.stdout)

        self.assertEqual(datos["estado"], "error")
        self.assertEqual(
            datos["codigo"],
            "ARGUMENTOS_INVALIDOS"
        )


if __name__ == "__main__":
    unittest.main()
