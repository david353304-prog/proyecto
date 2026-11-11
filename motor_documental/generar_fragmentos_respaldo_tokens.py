
from pathlib import Path
import json
from utilidades_texto import dividir_en_fragmentos

# Ubicar el archivo JSON que contiene los artículos
ruta_json = Path(__file__).parent / "corpus" / "articulos_ley_1801.json"

# Leer el corpus documental
with open(ruta_json, "r", encoding="utf-8") as archivo:
    corpus_articulos = json.load(archivo)

# Comprobar que los artículos se cargaron
print("\n--- CARGA DEL CORPUS ---")
print("Artículos cargados:", len(corpus_articulos))
print("Primer artículo:", corpus_articulos[0]["numero"])
print("Último artículo:", corpus_articulos[-1]["numero"])

# Analizar la longitud de los artículos
print("\n--- LONGITUD DE LOS ARTÍCULOS ---")

longitudes = []

for articulo in corpus_articulos:
    cantidad_palabras = len(articulo["texto"].split())

    longitudes.append({
        "numero": articulo["numero"],
        "palabras": cantidad_palabras
    })

# Ordenar los artículos desde el más largo
longitudes_ordenadas = sorted(
    longitudes,
    key=lambda articulo: articulo["palabras"],
    reverse=True
)

print("Artículo más corto:", min(
    longitudes,
    key=lambda articulo: articulo["palabras"]
))

print("Artículo más largo:", longitudes_ordenadas[0])

print("\nLos 10 artículos más largos:")

for articulo in longitudes_ordenadas[:10]:
    print(
        f'Artículo {articulo["numero"]}: '
        f'{articulo["palabras"]} palabras'
    )

# Configuración inicial de los fragmentos para RAG
TAMANO_FRAGMENTO = 300
SOLAPAMIENTO = 50

print("\n--- CONFIGURACIÓN DE FRAGMENTOS ---")
print("Tamaño máximo:", TAMANO_FRAGMENTO, "palabras")
print("Solapamiento:", SOLAPAMIENTO, "palabras")
print(
    "Avance entre fragmentos:",
    TAMANO_FRAGMENTO - SOLAPAMIENTO,
    "palabras"
)

# Generar fragmentos para todos los artículos
print("\n--- FRAGMENTACIÓN DEL CORPUS COMPLETO ---")

todos_los_fragmentos = []

for articulo in corpus_articulos:

    fragmentos_articulo = dividir_en_fragmentos(
        articulo["texto"],
        TAMANO_FRAGMENTO,
        SOLAPAMIENTO
    )

    for indice, texto_fragmento in enumerate(fragmentos_articulo, start=1):

        fragmento = {
            "id": f'articulo_{articulo["numero"]}_fragmento_{indice}',
            "numero_articulo": articulo["numero"],
            "titulo": articulo["titulo"],
            "pagina_inicio": articulo["pagina_inicio"],
            "pagina_fin": articulo["pagina_fin"],
            "fuente": articulo["fuente"],
            "url_fuente": articulo["url_fuente"],
            "texto": texto_fragmento
        }

        todos_los_fragmentos.append(fragmento)

print("Artículos procesados:", len(corpus_articulos))
print("Fragmentos generados:", len(todos_los_fragmentos))

fragmentos_vacios = [
    fragmento["id"]
    for fragmento in todos_los_fragmentos
    if not fragmento["texto"].strip()
]

print("Fragmentos vacíos:", len(fragmentos_vacios))

# Guardar los fragmentos generados en formato JSON
ruta_fragmentos = (
    Path(__file__).parent
    / "fragmentos"
    / "fragmentos_ley_1801.json"
)

with open(ruta_fragmentos, "w", encoding="utf-8") as archivo:
    json.dump(
        todos_los_fragmentos,
        archivo,
        ensure_ascii=False,
        indent=4
    )

print("\n--- GUARDADO DE FRAGMENTOS ---")
print("Archivo guardado en:", ruta_fragmentos)
print("Total de fragmentos guardados:", len(todos_los_fragmentos))
