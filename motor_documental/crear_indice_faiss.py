from pathlib import Path

import faiss
import numpy as np

# 1. Definir las rutas
carpeta_motor = Path(__file__).resolve().parent
carpeta_embeddings = carpeta_motor / "embeddings"

ruta_vectores = carpeta_embeddings / "vectores_ley_1801.npy"
ruta_indice = carpeta_embeddings / "indice_ley_1801.faiss"

# 2. Cargar los embeddings
print("\n--- CARGA DE EMBEDDINGS ---")

vectores = np.load(ruta_vectores)
vectores = np.ascontiguousarray(vectores, dtype=np.float32)

print("Dimensiones de la matriz:", vectores.shape)

# 3. Verificar los vectores
if vectores.ndim != 2 or vectores.shape[0] == 0:
	raise ValueError("La matriz de embeddings no es válida.")

if not np.isfinite(vectores).all():
	raise ValueError("Los embeddings contienen valores no válidos.")

normas = np.linalg.norm(vectores, axis=1)

if not np.allclose(normas, 1.0, atol=1e-4):
	raise ValueError("Los embeddings no están normalizados.")

# 4. Obtener las dimensiones
cantidad_vectores, dimensiones = vectores.shape

print("Cantidad de vectores:", cantidad_vectores)
print("Dimensiones por vector:", dimensiones)

# 5. Crear el índice FAISS
print("\n--- CREACIÓN DEL ÍNDICE FAISS ---")

indice = faiss.IndexFlatIP(dimensiones)

# 6. Agregar los vectores
indice.add(vectores)

print("Vectores incorporados al índice:", indice.ntotal)

# 7. Verificar el índice
if indice.ntotal != cantidad_vectores:
	raise ValueError("No se incorporaron todos los vectores.")

# 8. Guardar el índice
faiss.write_index(indice, str(ruta_indice))

print("\n--- GUARDADO DEL ÍNDICE ---")
print("Archivo:", ruta_indice)

# 9. Verificar que se puede volver a cargar
indice_recuperado = faiss.read_index(str(ruta_indice))

print("\n--- VERIFICACIÓN FINAL ---")
print("Vectores recuperados:", indice_recuperado.ntotal)
print("Dimensiones:", indice_recuperado.d)

if indice_recuperado.ntotal != cantidad_vectores:
	raise ValueError("El índice guardado no coincide con el original.")

print("Índice FAISS creado correctamente.")
