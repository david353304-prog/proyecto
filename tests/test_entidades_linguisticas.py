import unittest

from motor_documental.analisis.analisis_linguistico_corpus import (
    PATRONES_ENTIDADES, entidades_por_reglas,
)


class TestPlazos(unittest.TestCase):
    def test_duracion_compuesta_y_edad(self):
        texto = ("Para los mayores de 18 años y las personas de 17 años de edad, "
                 "la diligencia se hará dentro de cuarenta y ocho (48) horas.")
        self.assertEqual(
            list(entidades_por_reglas("PLAZO", PATRONES_ENTIDADES["PLAZO"], texto)),
            ["cuarenta y ocho (48) horas"],
        )
