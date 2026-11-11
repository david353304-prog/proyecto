import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

# 1. Definir las rutas del proyecto
carpeta_motor = Path(__file__).resolve().parent

ruta_fragmentos = (
	carpeta_motor / "fragmentos" / "fragmentos_ley_1801.json"
)

carpeta_embeddings = carpeta_motor / "embeddings"
carpeta_embeddings.mkdir(parents=True, exist_ok=True)

ruta_vectores = carpeta_embeddings / "vectores_ley_1801.npy"
ruta_metadatos = carpeta_embeddings / "metadatos_ley_1801.json"

# 2. Cargar los fragmentos
print("\n--- CARGA DE FRAGMENTOS ---")

with open(ruta_fragmentos, "r", encoding="utf-8") as archivo:
	fragmentos = json.load(archivo)

print("Fragmentos cargados:", len(fragmentos))

if not fragmentos:
	raise ValueError("El archivo no contiene fragmentos.")

# 3. Preparar los textos
textos = []

for fragmento in fragmentos:
	texto = fragmento["texto"].strip()

	if not texto:
		raise ValueError(
			f"Fragmento vacío: {fragmento['id']}"
		)

	textos.append(texto)

# 4. Cargar el modelo de embeddings
print("\n--- CARGA DEL MODELO ---")

nombre_modelo = (
	"sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

modelo = SentenceTransformer(nombre_modelo)

# 5. Generar los embeddings
print("\n--- GENERACIÓN DE EMBEDDINGS ---")

vectores = modelo.encode(
	textos,
	batch_size=16,
	show_progress_bar=True,
	convert_to_numpy=True,
	normalize_embeddings=True
)

vectores = np.asarray(vectores, dtype=np.float32)

print("Dimensiones de la matriz:", vectores.shape)

# 6. Verificar los resultados
if vectores.shape[0] != len(fragmentos):
	raise ValueError(
		"La cantidad de vectores no coincide con los fragmentos."
	)

if not np.isfinite(vectores).all():
	raise ValueError(
		"Se encontraron valores numéricos no válidos."
	)

# 7. Guardar los vectores
np.save(ruta_vectores, vectores)

print("\n--- GUARDADO DE VECTORES ---")
print("Archivo:", ruta_vectores)

# 8. Guardar los metadatos en el mismo orden
with open(ruta_metadatos, "w", encoding="utf-8") as archivo:
	json.dump(
		fragmentos,
		archivo,
		ensure_ascii=False,
		indent=2
	)

print("\n--- GUARDADO DE METADATOS ---")
print("Archivo:", ruta_metadatos)

# 9. Mostrar el resumen final
print("\n--- RESUMEN FINAL ---")
print("Fragmentos procesados:", len(fragmentos))
print("Vectores generados:", len(vectores))
print("Dimensiones por vector:", vectores.shape[1])
print("Proceso completado correctamente.")
