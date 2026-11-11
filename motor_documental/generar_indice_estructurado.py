import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# 1. Definir las rutas
carpeta_motor = Path(__file__).resolve().parent
carpeta_fragmentos = carpeta_motor / "fragmentos"
carpeta_embeddings = carpeta_motor / "embeddings"

ruta_datos = carpeta_fragmentos / "articulo_135_rag.json"
ruta_indice = carpeta_embeddings / "indice_estructurado_135.faiss"
ruta_metadatos = carpeta_embeddings / "metadatos_estructurados_135.json"

# 2. Cargar los registros jurídicos
print("\n--- CARGA DE REGISTROS ESTRUCTURADOS ---")

with open(ruta_datos, "r", encoding="utf-8") as archivo:
	registros = json.load(archivo)

if not isinstance(registros, list) or not registros:
	raise ValueError("No se encontraron registros válidos.")

textos = [registro["texto_rag"] for registro in registros]

print("Registros disponibles:", len(registros))

# 3. Cargar el mismo modelo utilizado en el índice general
print("\n--- CARGA DEL MODELO ---")

modelo = SentenceTransformer(
	"sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# 4. Generar embeddings normalizados
print("\n--- GENERACIÓN DE EMBEDDINGS ---")

vectores = modelo.encode(
	textos,
	batch_size=16,
	show_progress_bar=True,
	convert_to_numpy=True,
	normalize_embeddings=True
)

vectores = np.ascontiguousarray(
	vectores,
	dtype=np.float32
)

print("Dimensiones de los vectores:", vectores.shape)

# 5. Crear el índice FAISS
print("\n--- CREACIÓN DEL ÍNDICE ---")

dimension = vectores.shape[1]

indice = faiss.IndexFlatIP(dimension)
indice.add(vectores)

# 6. Guardar el índice y los metadatos
carpeta_embeddings.mkdir(parents=True, exist_ok=True)

faiss.write_index(indice, str(ruta_indice))

with open(ruta_metadatos, "w", encoding="utf-8") as archivo:
	json.dump(
		registros,
		archivo,
		ensure_ascii=False,
		indent=2
	)

# 7. Verificar los archivos generados
indice_verificado = faiss.read_index(str(ruta_indice))

if indice_verificado.ntotal != len(registros):
	raise ValueError(
		"La cantidad de vectores no coincide con los registros."
	)

print("\n--- RESULTADO FINAL ---")
print("Vectores indexados:", indice_verificado.ntotal)
print("Dimensión:", indice_verificado.d)
print("Índice guardado en:", ruta_indice)
print("Metadatos guardados en:", ruta_metadatos)
print("\nÍNDICE ESTRUCTURADO CREADO CORRECTAMENTE")
