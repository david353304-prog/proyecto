import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class BuscadorGeneral1801:
    """Búsqueda semántica en los fragmentos de la Ley 1801."""

    def __init__(self, modelo=None):
        base = Path(__file__).resolve().parent

        ruta_indice = base / "embeddings/indice_ley_1801.faiss"
        ruta_metadatos = base / "embeddings/metadatos_ley_1801.json"

        self.indice = faiss.read_index(str(ruta_indice))

        with ruta_metadatos.open(encoding="utf-8") as archivo:
            self.metadatos = json.load(archivo)

        if self.indice.ntotal != len(self.metadatos):
            raise ValueError(
                "La cantidad de vectores no coincide "
                "con los metadatos."
            )

        self.modelo = modelo if modelo is not None else SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )

        if self.indice.d != self.modelo.get_embedding_dimension():
            raise ValueError(
                "Las dimensiones del modelo y FAISS "
                "no coinciden."
            )

    def buscar(self, pregunta, cantidad=5, articulos_excluidos=()):
        """Devuelve hasta la cantidad pedida de fragmentos aptos por similitud."""

        if not isinstance(pregunta, str) or not pregunta.strip():
            raise ValueError(
                "La pregunta debe contener texto."
            )

        if (
            not isinstance(cantidad, int)
            or isinstance(cantidad, bool)
            or cantidad < 1
        ):
            raise ValueError(
                "La cantidad debe ser un entero positivo."
            )

        cantidad = min(cantidad, self.indice.ntotal)
        excluidos = set(articulos_excluidos)
        # Cada fragmento excluido puede ocupar un puesto en la búsqueda FAISS.
        reserva = sum(str(f["numero_articulo"]) in excluidos for f in self.metadatos)

        vector = self.modelo.encode(
            [pregunta],
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        vector = np.ascontiguousarray(
            vector,
            dtype=np.float32
        )

        similitudes, posiciones = self.indice.search(
            vector,
            min(cantidad + reserva, self.indice.ntotal)
        )

        resultados = []

        for posicion, similitud in zip(
            posiciones[0], similitudes[0]
        ):
            if posicion < 0:
                continue

            fragmento = self.metadatos[int(posicion)]
            if str(fragmento["numero_articulo"]) in excluidos:
                continue

            resultados.append({
                "id": fragmento["id"],
                "articulo": fragmento["numero_articulo"],
                "titulo": fragmento["titulo"],
                "texto": fragmento["texto"],
                "fuente": fragmento["fuente"],
                "url_fuente": fragmento["url_fuente"],
                "similitud": float(similitud),
                "posicion_faiss": int(posicion)
            })
            if len(resultados) == cantidad:
                break

        return resultados
