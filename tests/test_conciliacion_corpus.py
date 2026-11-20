import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from motor_documental.corpus.conciliar_diferencias import CARPETA, conciliar, main


class TestConciliacionCorpus(unittest.TestCase):
    def test_cubre_diferencias_y_reproduce_evidencia(self):
        historico = json.loads((CARPETA / "articulos_ley_1801.json").read_bytes())
        referencia = json.loads((CARPETA / "referencia_normativa.json").read_bytes())
        evidencia = json.loads((CARPETA / "conciliacion_diferencias.json").read_bytes())
        filas = conciliar(historico, referencia)
        esperados = {
            a["articulo"] for a in referencia["articulos"]
            if a["contraste_local"] == "diferencias_por_revisar"
        }
        self.assertEqual(len(filas), len(esperados))
        self.assertEqual({f["articulo"] for f in filas}, esperados)
        self.assertEqual(filas, evidencia["casos"])
        self.assertTrue(all(
            f["historico"]["texto"] and f["historico"]["fuente"]
            and f["referencia_oficial"]["texto"] and f["referencia_oficial"]["fuente"]
            and f["diferencias"] and f["decision_propuesta"]
            and not f["aprobado_para_indice"]
            for f in filas
        ))
        self.assertTrue(all(
            cambio["apartados"] and cambio["fuente_oficial"] and cambio["fecha_consulta"]
            for fila in filas for cambio in fila["diferencias"]
        ))

        por_articulo = {f["articulo"]: f for f in filas}
        self.assertEqual(por_articulo["15"]["clasificacion_principal"], "extraccion_o_formato")
        self.assertEqual(por_articulo["93"]["clasificacion_principal"], "reforma_o_correccion_normativa")
        self.assertEqual(por_articulo["162"]["evidencia"]["fallo_cotejado"]["decision"], "C-223/17")
        self.assertEqual(por_articulo["242"]["clasificacion_principal"], "revision_juridica")

    def test_expediente_del_18_de_noviembre_de_2026(self):
        expediente = json.loads((CARPETA / "conciliacion_diferencias.json").read_bytes())
        huellas = {
            "articulos_ley_1801.json": "80b7731924bab0a1ae2a70acea60629db380f106c234474dfc37eca9c195336f",
            "referencia_normativa.json": "2890099753124d46ff96c79d1d7e38b9dd4f5e0b8cb5f779cd38c479f11b0500",
        }
        self.assertEqual(expediente["total"], 159)
        self.assertEqual(len(expediente["casos"]), 159)
        self.assertEqual(expediente["insumos_sha256"], huellas)
        for nombre, huella in huellas.items():
            with self.subTest(nombre=nombre):
                # El expediente se generó en Windows con los insumos en CRLF.
                datos = (CARPETA / nombre).read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
                self.assertEqual(hashlib.sha256(datos).hexdigest(), huella)
        self.assertEqual({
            caso["referencia_oficial"]["fecha_consulta"] for caso in expediente["casos"]
        }, {"2026-11-18"})

    def test_programa_admite_un_expediente_con_otro_total(self):
        referencia = json.loads((CARPETA / "referencia_normativa.json").read_bytes())
        referencia["articulos"] = [
            a for a in referencia["articulos"] if a["articulo"] in {"1", "15"}
        ]
        with tempfile.TemporaryDirectory() as directorio:
            insumo = Path(directorio) / "referencia.json"
            salida = Path(directorio) / "revision.json"
            insumo.write_text(json.dumps(referencia), encoding="utf-8")
            with patch("sys.argv", ["conciliar", "--referencia", str(insumo), "--salida", str(salida)]):
                main()
            resultado = json.loads(salida.read_bytes())
        self.assertEqual(resultado["total"], 1)
        self.assertEqual([caso["articulo"] for caso in resultado["casos"]], ["15"])

    def test_segunda_fuente_cubre_expediente_sin_aprobar_vigencia(self):
        expediente = json.loads((CARPETA / "conciliacion_diferencias.json").read_bytes())
        jep = json.loads((CARPETA / "contraste_jep.json").read_bytes())
        self.assertEqual(
            [fila["articulo"] for fila in jep["casos"]],
            [fila["articulo"] for fila in expediente["casos"]],
        )
        self.assertTrue(all(not fila["cierra_revision_juridica"] for fila in jep["casos"]))
        self.assertEqual(
            {fila["articulo"] for fila in jep["casos"] if fila["bloques"]},
            {"84", "92", "242"},
        )
