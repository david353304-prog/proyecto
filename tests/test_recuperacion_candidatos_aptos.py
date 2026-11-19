import unittest
from unittest.mock import Mock, patch

import faiss
import numpy as np

from motor_documental.buscador_general_1801 import BuscadorGeneral1801
from motor_documental import recuperador_combinado_1801 as modulo


class TestRecuperacionCandidatosAptos(unittest.TestCase):
    def test_omite_inexequibles_y_completa_k_con_resultados_posteriores(self):
        recuperador = modulo.RecuperadorCombinado1801.__new__(modulo.RecuperadorCombinado1801)
        general = BuscadorGeneral1801.__new__(BuscadorGeneral1801)
        general.indice = faiss.IndexFlatIP(1)
        general.indice.add(np.array([[6], [5], [4], [3], [2], [1]], dtype=np.float32))
        general.modelo = Mock()
        general.modelo.encode.return_value = np.array([[1]], dtype=np.float32)
        general.metadatos = [
            {"id": str(i), "numero_articulo": numero, "titulo": "", "texto": numero,
             "fuente": "", "url_fuente": ""}
            for i, numero in enumerate(("47", "73", "162", "73", "5", "6"))
        ]
        recuperador.general = general
        recuperador.estructurado = Mock()
        recuperador.estructurado.buscar.return_value = []

        with patch.object(modulo, "buscar_articulos_clave", return_value=[{"articulo": "47"}]), patch.object(
            modulo, "buscar_referencias_cruzadas", return_value=[{"articulo": "162"}]
        ):
            resultado = recuperador.buscar("¿Cuál es la definición de convivencia?", cantidad_general=2)

        self.assertEqual([a["articulo"] for a in resultado["resultados_generales"]], ["5", "6"])
        self.assertEqual(resultado["total_generales"], 2)
        general.modelo.encode.assert_called_once()
