from sentence_transformers import SentenceTransformer

try:
    from .buscador_general_1801 import BuscadorGeneral1801
    from .buscar_estructurado_135 import BuscadorEstructurado135
    from .buscador_articulos_clave import buscar_articulos_clave
except ImportError:
    from buscador_general_1801 import BuscadorGeneral1801
    from buscar_estructurado_135 import BuscadorEstructurado135
    from buscador_articulos_clave import buscar_articulos_clave


class RecuperadorCombinado1801:
    """Recupera candidatos jurídicos desde dos índices FAISS."""

    def __init__(self, modelo=None):
        self.modelo = (
            modelo
            if modelo is not None
            else SentenceTransformer(
                "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            )
        )

        self.general = BuscadorGeneral1801(
            modelo=self.modelo
        )

        self.estructurado = BuscadorEstructurado135(
            modelo=self.modelo
        )

    def buscar(
        self,
        pregunta,
        cantidad_general=5,
        cantidad_estructurada=10
    ):
        """Devuelve los dos grupos de resultados sin mezclarlos."""

        resultados_generales = self.general.buscar(
            pregunta,
            cantidad=cantidad_general
        )

        # Recuperación complementaria por título y número de artículo.
        articulos_clave = buscar_articulos_clave(
            pregunta,
            limite=3
        )

        # Los artículos clave se incorporan antes de los fragmentos FAISS.
        # Se conservan las claves y el formato que espera el contexto RAG.
        identificadores = set()
        resultados_hibridos = []

        for articulo in articulos_clave:
            identificador = "articulo_" + str(articulo["articulo"])

            if identificador in identificadores:
                continue

            identificadores.add(identificador)

            resultados_hibridos.append({
                "id": identificador,
                "articulo": articulo["articulo"],
                "titulo": articulo["titulo"],
                "texto": articulo["texto"],
                "fuente": articulo["fuente"],
                "url_fuente": articulo["url_fuente"],
                "similitud": 1.0,
                "origen_recuperacion": "titulo_numero"
            })

        for resultado in resultados_generales:
            identificador = "articulo_" + str(
                resultado.get("articulo", "")
            )

            if identificador in identificadores:
                continue

            resultados_hibridos.append(resultado)

        resultados_generales = resultados_hibridos

        resultados_estructurados = self.estructurado.buscar(
            pregunta,
            cantidad=cantidad_estructurada
        )

        return {
            "pregunta": pregunta,
            "resultados_generales": resultados_generales,
            "resultados_estructurados_135": resultados_estructurados,
            "total_generales": len(resultados_generales),
            "total_estructurados": len(resultados_estructurados)
        }
