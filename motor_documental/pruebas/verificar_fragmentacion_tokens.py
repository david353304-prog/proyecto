
import json
from pathlib import Path

from sentence_transformers import SentenceTransformer
from motor_documental.utilidades_texto import (
    dividir_en_fragmentos_por_tokens
)

# 1. Localizar el corpus
carpeta_motor = Path(__file__).resolve().parents[1]
ruta_corpus = carpeta_motor / "corpus" / "articulos_ley_1801.json"

with open(ruta_corpus, "r", encoding="utf-8") as archivo:
    articulos = json.load(archivo)

# 2. Cargar el modelo
modelo = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

tokenizer = modelo.tokenizer
limite = modelo.max_seq_length

total_fragmentos = 0
fragmentos_fuera_limite = 0
articulos_con_errores = []
maximo_tokens = 0

# 3. Analizar cada artículo
for articulo in articulos:

    fragmentos = dividir_en_fragmentos_por_tokens(
        articulo["texto"],
        tokenizer,
        tamano=120,
        solapamiento=20
    )

    total_fragmentos += len(fragmentos)

    for fragmento in fragmentos:
        cantidad_tokens = len(
            tokenizer.encode(
                fragmento,
                add_special_tokens=True,
                truncation=False
            )
        )

        maximo_tokens = max(
            maximo_tokens,
            cantidad_tokens
        )

        if cantidad_tokens > limite:
            fragmentos_fuera_limite += 1

    # 4. Reconstruir el texto eliminando solapamientos
    if not fragmentos:
        articulos_con_errores.append(articulo["numero"])
        continue

    palabras_recuperadas = fragmentos[0].split()

    for fragmento in fragmentos[1:]:
        palabras = fragmento.split()
        coincidencia = 0

        maximo = min(
            len(palabras_recuperadas),
            len(palabras)
        )

        for cantidad in range(maximo, 0, -1):
            if (
                palabras_recuperadas[-cantidad:]
                == palabras[:cantidad]
            ):
                coincidencia = cantidad
                break

        palabras_recuperadas.extend(
            palabras[coincidencia:]
        )

    if palabras_recuperadas != articulo["texto"].split():
        articulos_con_errores.append(articulo["numero"])

# 5. Mostrar resultados
print("\n--- VERIFICACIÓN COMPLETA DEL CORPUS ---")
print("Artículos analizados:", len(articulos))
print("Fragmentos generados:", total_fragmentos)
print("Límite del modelo:", limite)
print("Máximo de tokens:", maximo_tokens)
print("Fragmentos fuera del límite:", fragmentos_fuera_limite)
print("Artículos con diferencias:", len(articulos_con_errores))

if articulos_con_errores:
    print("Artículos que requieren revisión:")
    print(articulos_con_errores)
else:
    print("Conservación de palabras: CORRECTA")
