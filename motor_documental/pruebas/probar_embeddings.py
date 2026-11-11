from sentence_transformers import SentenceTransformer, util


# 1. Cargar el modelo de embeddings
print("Cargando modelo...")

modelo = SentenceTransformer(
	"sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# 2. Crear tres textos de ejemplo
textos = [
	"Una persona hace demasiado ruido y molesta a sus vecinos.",
	"Los comportamientos que afectan la tranquilidad y las relaciones respetuosas entre las personas.",
	"Una persona estaciona su vehículo en un lugar prohibido.",
]

# 3. Convertir los textos en vectores numéricos
embeddings = modelo.encode(textos, convert_to_tensor=True)

# 4. Mostrar las dimensiones de los vectores
print("\n--- RESULTADOS DE EMBEDDINGS ---")
print("Cantidad de textos:", len(textos))
print("Dimensiones de los embeddings:", embeddings.shape)

# 5. Comparar el primer texto con los demás
similitudes = util.cos_sim(embeddings[0], embeddings)[0]

print("\n--- SIMILITUD SEMÁNTICA ---")

for indice, similitud in enumerate(similitudes):
	print(f"Texto {indice + 1}: {similitud.item():.4f}")
	print(textos[indice])
	print()
