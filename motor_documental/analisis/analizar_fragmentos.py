import json
from pathlib import Path
from collections import Counter

# Localizar el archivo JSON de fragmentos
carpeta_motor = Path(__file__).resolve().parent.parent

ruta_fragmentos = (
	carpeta_motor
	/ "fragmentos"
	/ "fragmentos_ley_1801.json"
)

# Leer los fragmentos guardados
with open(ruta_fragmentos, "r", encoding="utf-8") as archivo:
	fragmentos_guardados = json.load(archivo)

# Analizar los límites de los fragmentos del artículo 135
print("\n--- REVISIÓN DE LÍMITES DEL ARTÍCULO 135 ---")

fragmentos_135 = [
	fragmento
	for fragmento in fragmentos_guardados
	if fragmento["numero_articulo"] == "135"
]

for indice, fragmento in enumerate(fragmentos_135, start=1):
	palabras = fragmento["texto"].split()

	print(f"\nFragmento {indice}")
	print("Inicio:", " ".join(palabras[:20]))
	print("Final:", " ".join(palabras[-20:]))

# Contar los fragmentos de cada artículo
print("\n--- ARTÍCULOS CON VARIOS FRAGMENTOS ---")

conteo_fragmentos = Counter(
	fragmento["numero_articulo"]
	for fragmento in fragmentos_guardados
)

articulos_divididos = {
	numero: cantidad
	for numero, cantidad in conteo_fragmentos.items()
	if cantidad > 1
}

print("Total de artículos:", len(conteo_fragmentos))

print(
	"Artículos con un solo fragmento:",
	sum(
		1
		for cantidad in conteo_fragmentos.values()
		if cantidad == 1
	)
)

print("Artículos con varios fragmentos:", len(articulos_divididos))

print("\nArtículos divididos:")

for numero, cantidad in articulos_divididos.items():
	print(f"Artículo {numero}: {cantidad} fragmentos")
