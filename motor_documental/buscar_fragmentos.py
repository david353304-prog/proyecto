import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# 1. Definir las rutas
carpeta_motor = Path(__file__).resolve().parent
carpeta_embeddings = carpeta_motor / "embeddings"

ruta_indice = carpeta_embeddings / "indice_ley_1801.faiss"
ruta_metadatos = carpeta_embeddings / "metadatos_ley_1801.json"

# 2. Cargar el índice FAISS
print("\n--- CARGA DEL ÍNDICE FAISS ---")

indice = faiss.read_index(str(ruta_indice))

print("Vectores disponibles:", indice.ntotal)

# 3. Cargar los metadatos
with open(ruta_metadatos, "r", encoding="utf-8") as archivo:
	metadatos = json.load(archivo)

print("Fragmentos disponibles:", len(metadatos))

if indice.ntotal != len(metadatos):
	raise ValueError(
		"La cantidad de vectores no coincide con los metadatos."
	)

# 4. Cargar el mismo modelo utilizado para los documentos
print("\n--- CARGA DEL MODELO ---")

modelo = SentenceTransformer(
	"sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

if modelo.get_embedding_dimension() != indice.d:
	raise ValueError(
		"Las dimensiones del modelo no coinciden con el índice."
	)

# 5. Permitir varias preguntas
while True:

    pregunta = input(
        "\nEscribe tu pregunta sobre la Ley 1801 "
        "(o 'salir' para terminar): "
    ).strip()

    if pregunta.lower() == "salir":
        print("\nBúsqueda finalizada.")
        break

    if not pregunta:
        print("Debes escribir una pregunta.")
        continue

    print("\n--- PREGUNTA DEL USUARIO ---")
    print(pregunta)

    # 6. Convertir la pregunta en un embedding
    vector_pregunta = modelo.encode(
        [pregunta],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    vector_pregunta = np.ascontiguousarray(
        vector_pregunta,
        dtype=np.float32
    )

    # 7. Buscar los cinco fragmentos más similares
    cantidad_resultados = min(5, indice.ntotal)

    similitudes, posiciones = indice.search(
        vector_pregunta,
        cantidad_resultados
    )

    # 8. Mostrar los resultados
    print("\n--- RESULTADOS DE BÚSQUEDA ---")

    for numero, (posicion, similitud) in enumerate(
        zip(posiciones[0], similitudes[0]),
        start=1
    ):
        if posicion < 0:
            continue

        fragmento = metadatos[int(posicion)]

        print(f"\nRESULTADO {numero}")
        print("Similitud:", round(float(similitud), 4))
        print("ID:", fragmento["id"])
        print("Artículo:", fragmento["numero_articulo"])
        print("Título:", fragmento["titulo"])
        print("Fuente:", fragmento["fuente"])
        print("URL:", fragmento["url_fuente"])

        print("\nTexto recuperado:")
        print(fragmento["texto"][:700])

        print("-" * 60)

   
    # 9. Identificar artículos candidatos entre los resultados de FAISS
    print("\n--- ARTÍCULOS CANDIDATOS ---")

    articulos_candidatos = {}

    for posicion, similitud in zip(
        posiciones[0], similitudes[0]
    ):
        if posicion < 0:
            continue

        fragmento = metadatos[int(posicion)]
        numero_articulo = str(fragmento["numero_articulo"])

        if numero_articulo not in articulos_candidatos:
            articulos_candidatos[numero_articulo] = {
                "titulo": fragmento["titulo"],
                "similitud": float(similitud),
                "fragmentos": []
            }

        articulos_candidatos[numero_articulo]["fragmentos"].append(
            fragmento["id"]
        )

    for numero_articulo, informacion in articulos_candidatos.items():

        fragmentos_articulo = [
            fragmento
            for fragmento in metadatos
            if str(fragmento["numero_articulo"]) == numero_articulo
        ]

        print("\n" + "=" * 60)
        print("Artículo:", numero_articulo)
        print("Título:", informacion["titulo"])
        print("Mayor similitud:", round(informacion["similitud"], 4))
        print("Fragmentos encontrados por FAISS:",
              informacion["fragmentos"])
        print("Total de fragmentos del artículo:",
              len(fragmentos_articulo))
