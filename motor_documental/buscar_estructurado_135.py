import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class BuscadorEstructurado135:
    """Búsqueda semántica de registros estructurados del artículo 135."""

    def __init__(self, modelo=None, modo="original"):
        base = Path(__file__).resolve().parent

        archivos = {
            "original": (
                "indice_representaciones_135.faiss",
                "metadatos_representaciones_135.json",
            ),
            "experimental": (
                "indice_representaciones_135_experimental.faiss",
                "metadatos_representaciones_135_experimental.json",
            ),
        }

        if modo not in archivos:
            raise ValueError(
                "Modo de índice no válido. "
                "Utilice 'original' o 'experimental'."
            )

        self.modo = modo
        nombre_indice, nombre_metadatos = archivos[modo]
        carpeta = base / "embeddings"

        self.indice = faiss.read_index(
            str(carpeta / nombre_indice)
        )

        with (
            carpeta / nombre_metadatos
        ).open(encoding="utf-8") as archivo:
            self.metadatos = json.load(archivo)

        with (
            base / "fragmentos/articulo_135_rag.json"
        ).open(encoding="utf-8") as archivo:
            registros = json.load(archivo)

        self.juridicos = {
            registro["id"]: registro
            for registro in registros
        }

        if self.indice.ntotal != len(self.metadatos):
            raise ValueError(
                "El índice FAISS y los metadatos no coinciden."
            )

        if not all(
            metadata["id"] in self.juridicos
            for metadata in self.metadatos
        ):
            raise ValueError(
                "Existen representaciones sin registro jurídico."
            )

        self.modelo = modelo if modelo is not None else SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )

        if self.indice.d != self.modelo.get_embedding_dimension():
            raise ValueError(
                "Las dimensiones del modelo y del índice no coinciden."
            )

    def buscar(self, pregunta, cantidad=5):
        """Devuelve registros jurídicos únicos ordenados por similitud."""

        if not isinstance(pregunta, str) or not pregunta.strip():
            raise ValueError("La pregunta no puede estar vacía.")

        if (
            not isinstance(cantidad, int)
            or isinstance(cantidad, bool)
            or cantidad < 1
        ):
            raise ValueError(
                "La cantidad debe ser un entero positivo."
            )

        cantidad = min(cantidad, len(self.juridicos))

        consulta = self.modelo.encode(
            [pregunta],
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        consulta = np.ascontiguousarray(
            consulta,
            dtype=np.float32
        )

        k = min(cantidad, self.indice.ntotal)

        while True:
            puntajes, posiciones = self.indice.search(consulta, k)
            mejores = {}

            for puntaje, posicion in zip(
                puntajes[0], posiciones[0]
            ):
                if posicion < 0:
                    continue

                metadata = self.metadatos[int(posicion)]
                identificador = metadata["id"]
                similitud = float(puntaje)

                if (
                    identificador not in mejores
                    or similitud > mejores[identificador]["similitud"]
                ):
                    mejores[identificador] = {
                        "similitud": similitud,
                        "tipo_representacion": metadata["tipo"]
                    }

            if len(mejores) >= cantidad or k == self.indice.ntotal:
                break

            k = min(k * 2, self.indice.ntotal)

        ordenados = sorted(
            mejores.items(),
            key=lambda elemento: elemento[1]["similitud"],
            reverse=True
        )

        resultados = []

        for identificador, coincidencia in ordenados[:cantidad]:
            juridico = self.juridicos[identificador]

            resultados.append({
                "id": identificador,
                "articulo": juridico["articulo"],
                "numeral": juridico["numeral"],
                "seccion": juridico["seccion"],
                "comportamiento": juridico["comportamiento"],
                "medida_correctiva": juridico["medida_correctiva"],
                "nota_normativa": juridico["nota_normativa"],
                "fuente": juridico["fuente"],
                "url_fuente": juridico["url_fuente"],
                "similitud": coincidencia["similitud"],
                "tipo_representacion": coincidencia[
                    "tipo_representacion"
                ]
            })

        return resultados
