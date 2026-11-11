import json
from pathlib import Path

# Localizar el archivo JSON
carpeta_motor = Path(__file__).resolve().parent.parent

ruta_fragmentos = (
	carpeta_motor
	/ "fragmentos"
	/ "fragmentos_ley_1801.json"
)

# Leer los fragmentos guardados
with open(ruta_fragmentos, "r", encoding="utf-8") as archivo:
	fragmentos = json.load(archivo)

# Definir los campos obligatorios
campos_obligatorios = [
	"id",
	"numero_articulo",
	"titulo",
	"pagina_inicio",
	"pagina_fin",
	"fuente",
	"url_fuente",
	"texto",
]

# Buscar registros con campos faltantes
fragmentos_incompletos = [
	fragmento.get("id", "Sin ID")
	for fragmento in fragmentos
	if any(campo not in fragmento for campo in campos_obligatorios)
]

# Obtener los identificadores
identificadores = [
	fragmento["id"]
	for fragmento in fragmentos
	if "id" in fragmento
]

# Buscar textos vacíos
fragmentos_vacios = [
	fragmento.get("id", "Sin ID")
	for fragmento in fragmentos
	if not fragmento.get("texto", "").strip()
]

# Mostrar los resultados
print("\n--- VERIFICACIÓN INDEPENDIENTE DE FRAGMENTOS ---")
print("Fragmentos recuperados:", len(fragmentos))
print("Fragmentos con campos faltantes:", len(fragmentos_incompletos))
print("Identificadores únicos:", len(set(identificadores)))
print("Fragmentos vacíos:", len(fragmentos_vacios))

# Comprobar los resultados
assert len(fragmentos) == 866
assert len(fragmentos_incompletos) == 0
assert len(set(identificadores)) == len(fragmentos)
assert len(fragmentos_vacios) == 0

print("Todas las verificaciones fueron superadas.")
