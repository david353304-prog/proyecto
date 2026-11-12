import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pymupdf

from motor_documental import extraer_pdf_usuario as modulo


NOMBRE = "123e4567-e89b-42d3-a456-426614174000.pdf"


class TestExtraerPDFUsuario(unittest.TestCase):

    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)

        self.carpeta = Path(self.temporal.name)

        parche = patch.object(
            modulo,
            "CARPETA_DOCUMENTOS",
            self.carpeta
        )
        parche.start()
        self.addCleanup(parche.stop)

    def crear_pdf(self, textos):
        ruta = self.carpeta / NOMBRE

        with pymupdf.open() as documento:
            for texto in textos:
                pagina = documento.new_page()

                if texto:
                    pagina.insert_text((72, 72), texto)

            documento.save(ruta)

        return ruta

    def test_extrae_texto_y_paginas(self):
        self.crear_pdf(["Primera pagina", "Segunda pagina"])

        resultado = modulo.extraer_pdf_usuario(NOMBRE)

        self.assertEqual(resultado["total_paginas_con_texto"], 2)
        self.assertEqual(resultado["paginas"][0]["pagina"], 1)
        self.assertIn(
            "Primera pagina",
            resultado["paginas"][0]["texto"]
        )

    def test_rechaza_pdf_sin_texto(self):
        self.crear_pdf([""])

        with self.assertRaises(modulo.ErrorExtraccionPDF):
            modulo.extraer_pdf_usuario(NOMBRE)

    def test_rechaza_nombre_no_permitido(self):
        with self.assertRaises(modulo.ErrorExtraccionPDF):
            modulo.extraer_pdf_usuario("../archivo.pdf")

    def test_rechaza_enlace_simbolico(self):
        destino = self.carpeta / "destino.pdf"
        destino.write_bytes(b"contenido")

        (self.carpeta / NOMBRE).symlink_to(destino)

        with self.assertRaises(modulo.ErrorExtraccionPDF):
            modulo.extraer_pdf_usuario(NOMBRE)

    def test_limite_paginas(self):
        self.crear_pdf(["Pagina uno", "Pagina dos"])

        with patch.object(modulo, "LIMITE_PAGINAS", 1):
            with self.assertRaises(modulo.ErrorExtraccionPDF):
                modulo.extraer_pdf_usuario(NOMBRE)

    def test_limite_caracteres(self):
        self.crear_pdf(["Texto suficientemente largo"])

        with patch.object(modulo, "LIMITE_CARACTERES", 5):
            with self.assertRaises(modulo.ErrorExtraccionPDF):
                modulo.extraer_pdf_usuario(NOMBRE)


    def test_rechaza_pdf_malformado(self):
        ruta = self.carpeta / NOMBRE
        ruta.write_bytes(b"%PDF-archivo-invalido")

        with self.assertRaises(modulo.ErrorExtraccionPDF):
            modulo.extraer_pdf_usuario(NOMBRE)

    def test_rechaza_archivo_demasiado_grande(self):
        ruta = self.carpeta / NOMBRE
        ruta.write_bytes(b"contenido")

        with patch.object(modulo, "LIMITE_PDF_BYTES", 3):
            with self.assertRaises(modulo.ErrorExtraccionPDF):
                modulo.extraer_pdf_usuario(NOMBRE)

    def test_conserva_numero_pagina_original(self):
        self.crear_pdf(["", "Texto en pagina dos", ""])

        resultado = modulo.extraer_pdf_usuario(NOMBRE)

        self.assertEqual(resultado["total_paginas_con_texto"], 1)
        self.assertEqual(resultado["paginas"][0]["pagina"], 2)

    def test_rechaza_archivo_inexistente(self):
        with self.assertRaises(modulo.ErrorExtraccionPDF):
            modulo.extraer_pdf_usuario(NOMBRE)


    def test_rechaza_directorio(self):
        (self.carpeta / NOMBRE).mkdir()

        with self.assertRaises(modulo.ErrorExtraccionPDF):
            modulo.extraer_pdf_usuario(NOMBRE)

    def test_lee_descriptor_abierto_ante_cambio_de_ruta(self):
        import os

        self.crear_pdf(["Documento original"])

        ruta = self.carpeta / NOMBRE
        ruta_movida = self.carpeta / "original_guardado.pdf"

        apertura_original = modulo.os.open

        def abrir_y_cambiar_ruta(*args, **kwargs):
            descriptor = apertura_original(*args, **kwargs)

            os.rename(ruta, ruta_movida)
            ruta.write_bytes(b"archivo sustituido")

            return descriptor

        with patch.object(
            modulo.os,
            "open",
            side_effect=abrir_y_cambiar_ruta
        ):
            resultado = modulo.extraer_pdf_usuario(NOMBRE)

        self.assertIn(
            "Documento original",
            resultado["paginas"][0]["texto"]
        )


if __name__ == "__main__":
    unittest.main()
