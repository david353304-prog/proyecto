import sys
from pathlib import Path

# Permitir importar funciones desde motor_documental.
carpeta_motor = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(carpeta_motor))

from utilidades_texto import dividir_en_fragmentos

# Crear un texto de prueba de 700 palabras.
texto_prueba = " ".join(str(i) for i in range(1, 701))

# Dividir el texto en fragmentos.
fragmentos = dividir_en_fragmentos(
	texto_prueba,
	tamano=300,
	solapamiento=50,
)

# Mostrar resultados.
print("\n--- PRUEBA INDEPENDIENTE DE FRAGMENTACIÓN ---")
print("Fragmentos generados:", len(fragmentos))
print("Palabras por fragmento:", [len(fragmento.split()) for fragmento in fragmentos])

# Verificar los resultados.
assert len(fragmentos) == 3
assert [len(fragmento.split()) for fragmento in fragmentos] == [300, 300, 200]

print("Prueba superada correctamente.")
