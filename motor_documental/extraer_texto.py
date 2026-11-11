from pathlib import Path
from collections import Counter
import re
import pymupdf
import json

# Ruta del documento
ruta_pdf = Path(__file__).parent / "corpus" / "Ley_1801_de_2016.pdf"

# Buscar encabezados de artículos al inicio de una línea
patron_articulo = r"(?im)^[ \t]*ARTÍCULO[ \t]+(\d+[A-Z]?)[ \t]*[.º°]"

articulos = []

with pymupdf.open(ruta_pdf) as documento:

	print("Total de páginas:", len(documento))

	for numero_pagina, pagina in enumerate(documento, start=1):

		texto = pagina.get_text()

		coincidencias = re.findall(
			patron_articulo,
			texto
		)

		for numero in coincidencias:
			articulos.append(numero.upper())

# Contar encabezados
conteo = Counter(articulos)

# Identificar números repetidos
repetidos = {
	numero: cantidad
	for numero, cantidad in conteo.items()
	if cantidad > 1
}

print("\nTotal de encabezados encontrados:", len(articulos))
print("Números de artículo diferentes:", len(conteo))

print("\nPrimeros 20 artículos:")
print(articulos[:20])

print("\nÚltimos 20 artículos:")
print(articulos[-20:])

print("\nNúmeros repetidos:")
print(repetidos)

# Verificar números faltantes en la secuencia principal
numeros_encontrados = {
    int(re.match(r"\d+", numero).group())
    for numero in articulos
}

numeros_esperados = set(range(1, 244))

faltantes = sorted(numeros_esperados - numeros_encontrados)

# Identificar artículos con letras adicionales
articulos_adicionados = [
    numero for numero in articulos
    if re.search(r"[A-Z]$", numero)
]

print("\nNúmeros faltantes entre 1 y 243:")
print(faltantes)

print("\nArtículos con letras adicionales:")
print(articulos_adicionados)


# Unir el texto de todas las páginas
with pymupdf.open(ruta_pdf) as documento:
    texto_completo = "\n".join(
        pagina.get_text() for pagina in documento
    )

# Buscar las posiciones de los encabezados
coincidencias = list(
    re.finditer(patron_articulo, texto_completo)
)

# Extraer el primer artículo como prueba
inicio = coincidencias[0].start()
fin = coincidencias[1].start()

texto_articulo_1 = texto_completo[inicio:fin]
# Eliminar encabezados repetitivos del PDF
texto_articulo_1 = re.sub(
    r"Departamento Administrativo de la Función Pública\s+"
    r"Ley 1801 de 2016\s+"
    r"\d+\s+"
    r"EVA - Gestor Normativo\s*",
    "",
    texto_articulo_1
)
texto_articulo_1 = re.sub(r"\s+", " ", texto_articulo_1).strip()
print("\n--- CONTENIDO DEL ARTÍCULO 1 ---")
print(texto_articulo_1)
print("--- FIN DEL ARTÍCULO 1 ---")


# Comparar el texto original y el texto limpio
print("\n--- COMPARACIÓN DE TEXTOS ---")

print("Caracteres del texto original:",
      len(texto_completo[inicio:fin]))

print("Caracteres del texto limpio:",
      len(texto_articulo_1))

print("\n¿El texto limpio contiene 'de las personas'?")
print("de las personas" in texto_articulo_1)

print("\n¿El texto limpio contiene 'delas personas'?")
print("delas personas" in texto_articulo_1)


# Comprobar cómo aparece la expresión en el PDF original
print("\n--- VERIFICACIÓN DEL TEXTO ORIGINAL ---")

texto_original = texto_completo[inicio:fin]

print("¿Original contiene 'de las personas'?")
print("de las personas" in texto_original)

print("¿Original contiene 'delas personas'?")
print("delas personas" in texto_original)



# Identificar la página donde comienza cada artículo
print("\n--- UBICACIÓN DE LOS PRIMEROS 10 ARTÍCULOS ---")

with pymupdf.open(ruta_pdf) as documento:

    for numero_pagina, pagina in enumerate(documento, start=1):

        texto_pagina = pagina.get_text()

        encontrados = re.findall(
            patron_articulo,
            texto_pagina
        )

        for numero_articulo in encontrados:

            if numero_articulo in [str(n) for n in range(1, 11)]:

                print(
                    f"Artículo {numero_articulo}: "
                    f"página {numero_pagina}"
                )



# Identificar las páginas de inicio y fin de cada artículo
print("\n--- RANGO DE PÁGINAS DE LOS PRIMEROS 10 ARTÍCULOS ---")

with pymupdf.open(ruta_pdf) as documento:

    posiciones_paginas = []
    texto_paginas = []

    for pagina in documento:
        posiciones_paginas.append(
            sum(len(texto) + 1 for texto in texto_paginas)
        )
        texto_paginas.append(pagina.get_text())

    texto_unido = "\n".join(texto_paginas)

    encabezados = list(
        re.finditer(patron_articulo, texto_unido)
    )

    for indice in range(min(10, len(encabezados))):

        encabezado = encabezados[indice]
        numero_articulo = encabezado.group(1)

        inicio_articulo = encabezado.start()

        if indice + 1 < len(encabezados):
            fin_articulo = encabezados[indice + 1].start()
        else:
            fin_articulo = len(texto_unido)

        pagina_inicio = sum(
            posicion <= inicio_articulo
            for posicion in posiciones_paginas
        )

        pagina_fin = sum(
            posicion < fin_articulo
            for posicion in posiciones_paginas
        )

        print(
            f"Artículo {numero_articulo}: "
            f"página {pagina_inicio} a {pagina_fin}"
        )

# Revisar el contenido del artículo 7
print("\n--- CONTENIDO DEL ARTÍCULO 7 ---")

for indice, encabezado in enumerate(encabezados):

    if encabezado.group(1) == "7":

        inicio_articulo_7 = encabezado.start()
        fin_articulo_7 = encabezados[indice + 1].start()

        texto_articulo_7 = texto_unido[
            inicio_articulo_7:fin_articulo_7
        ]

        # Comprobar el texto antes de limpiarlo
        posicion_social = texto_articulo_7.find("social")

        print("\n--- ANTES DE LIMPIAR ---")
        print(repr(texto_articulo_7[posicion_social:posicion_social + 45]))


        # Eliminar encabezados repetitivos
        texto_articulo_7 = re.sub(
            r"Departamento Administrativo de la Función Pública\s+"
            r"Ley 1801 de 2016\s+"
            r"\d+\s+"
r"EVA - Gestor Normativo[ \t]*\n?",
                " ",
            texto_articulo_7
        )

        # Comprobar el texto después de eliminar encabezados
        posicion_social = texto_articulo_7.find("social")

        print("\n--- DESPUÉS DE ELIMINAR ENCABEZADOS ---")
        print(repr(texto_articulo_7[posicion_social:posicion_social + 45]))

        # Normalizar espacios
        texto_articulo_7 = re.sub(
            r"\s+",
            " ",
            texto_articulo_7
        ).strip()

        # Comprobar el resultado de normalizar espacios
        posicion_social = texto_articulo_7.find("social")

        print("\n--- DESPUÉS DE NORMALIZAR ESPACIOS ---")
        print(repr(texto_articulo_7[posicion_social:posicion_social + 45]))

        # Normalizar ligaduras tipográficas

        texto_articulo_7 = texto_articulo_7.replace("ﬁ", "fi")
        texto_articulo_7 = texto_articulo_7.replace("ﬂ", "fl")

        # Verificar el texto final
        print("\n--- VERIFICACIÓN FINAL ---")
        print("¿Contiene 'social previstas'?",
              "social previstas" in texto_articulo_7)
        print("¿Contiene 'socialprevistas'?",
              "socialprevistas" in texto_articulo_7)

        posicion_social = texto_articulo_7.find("social")
        print(repr(texto_articulo_7[posicion_social:posicion_social + 45]))

        print("\n--- TEXTO FINAL DEL ARTÍCULO 7 ---")
        print(texto_articulo_7)

        break

print("--- FIN DEL ARTÍCULO 7 ---")

# Revisar posibles errores de extracción
print("\n--- REVISIÓN DE PALABRAS ---")

texto_original_7 = texto_unido[
    inicio_articulo_7:fin_articulo_7
]

for palabra in ["social", "pro-mover", "promover"]:

    posicion = texto_original_7.find(palabra)

    if posicion != -1:
        inicio_fragmento = max(0, posicion - 40)
        fin_fragmento = posicion + len(palabra) + 40

        fragmento = texto_original_7[
            inicio_fragmento:fin_fragmento
        ]

        print(f"\nExpresión buscada: {palabra}")
        print(repr(fragmento))

    else:
        print(f"\nNo se encontró: {palabra}")


# Correcciones específicas de errores de extracción
CORRECCIONES_VERIFICAR = {
    "ordena-miento": "ordenamiento",
    "pro-mover": "promover",
    "departa-mentales": "departamentales",
    "re-conocimientos": "reconocimientos",
    "con-vivencia": "convivencia",
    "per-turbación": "perturbación",
    "re-unión": "reunión"
}

def limpiar_texto_articulo(texto):
    # Eliminar encabezados repetitivos del PDF
    texto = re.sub(
        r"Departamento Administrativo de la Función Pública\s+"
        r"Ley 1801 de 2016\s+"
        r"\d+\s+"
        r"EVA - Gestor Normativo[ \t]*\n?",
        " ",
        texto
    )

    # Normalizar espacios y saltos de línea
    texto = re.sub(r"\s+", " ", texto).strip()

    # Normalizar ligaduras tipográficas

    texto = texto.replace("ﬁ", "fi")
    texto = texto.replace("ﬂ", "fl")

    # Corregir las siete palabras verificadas
    for palabra_original, palabra_corregida in CORRECCIONES_VERIFICAR.items():
        texto = texto.replace(palabra_original, palabra_corregida)

    return texto


# Probar la función reutilizable
print("\n--- PRUEBA DE FUNCIÓN DE LIMPIEZA ---")

texto_prueba = texto_unido[
    inicio_articulo_7:fin_articulo_7
]

resultado_prueba = limpiar_texto_articulo(texto_prueba)

print("¿Contiene 'social previstas'?",
      "social previstas" in resultado_prueba)

print("¿Contiene 'socialprevistas'?",
      "socialprevistas" in resultado_prueba)

print("¿Contiene 'fines'?",
      "fines" in resultado_prueba)

print("¿Contiene 'pacífica'?",
      "pacífica" in resultado_prueba)
 
# Crear una lista con todos los artículos
corpus_articulos = []

for indice, encabezado in enumerate(encabezados):
    numero_articulo = encabezado.group(1)
    inicio_articulo = encabezado.start()

    if indice + 1 < len(encabezados):
        fin_articulo = encabezados[indice + 1].start()
    else:
        fin_articulo = len(texto_unido)

    # Extraer el contenido original del artículo
    texto_original_articulo = texto_unido[
        inicio_articulo:fin_articulo
    ]

    # Limpiar el contenido
    texto_limpio = limpiar_texto_articulo(
        texto_original_articulo
    )

    # Calcular las páginas donde se encuentra el artículo
    pagina_inicio = sum(
        posicion <= inicio_articulo
        for posicion in posiciones_paginas
    )

    pagina_fin = sum(
        posicion < fin_articulo
        for posicion in posiciones_paginas
    )

    # Extraer el título del artículo
    coincidencia_titulo = re.match(
        r"^ARTÍCULO\s+\d+[A-Z]?\s*[.º°]\s*([^.\n]+)\.",
        texto_limpio,
        re.IGNORECASE
    )

    if coincidencia_titulo:
        titulo_articulo = coincidencia_titulo.group(1).strip()
    else:
        titulo_articulo = None

    # El artículo 223A no tiene título independiente
    # en el PDF utilizado para construir el corpus
    if numero_articulo == "223A":
        titulo_articulo = None

   
    # Organizar los datos y metadatos del artículo
    articulo = {
        "numero": numero_articulo,
        "titulo": titulo_articulo,
        "pagina_inicio": pagina_inicio,
        "pagina_fin": pagina_fin,
        "fuente": "Ley 1801 de 2016",
        "entidad_fuente": "Departamento Administrativo de la Función Pública",
        "url_fuente": "https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=80538",
        "texto": texto_limpio
    }


    # Agregar el artículo a la lista
    corpus_articulos.append(articulo)

# Verificar el corpus
print("\n--- CORPUS DE ARTÍCULOS ---")
print("Total de artículos procesados:", len(corpus_articulos))

print("\nPrimer artículo:")
print(corpus_articulos[0])

print("\nÚltimo artículo:")
print("Número:", corpus_articulos[-1]["numero"])
print("Caracteres:", len(corpus_articulos[-1]["texto"]))

# Guardar el corpus en formato JSON
ruta_json = Path(__file__).parent / "corpus" / "articulos_ley_1801.json"

print("\n--- ARCHIVO JSON ---")
print("Archivo guardado en:", ruta_json)
print("Total de artículos:", len(corpus_articulos))

# Verificar los títulos extraídos
articulos_sin_titulo = [
    articulo["numero"]
    for articulo in corpus_articulos
    if articulo["titulo"] is None
]

print("\n--- VERIFICACIÓN DE TÍTULOS ---")
print("Total de artículos:", len(corpus_articulos))
print("Artículos sin título:", len(articulos_sin_titulo))
print("Números sin título:", articulos_sin_titulo)

# Revisar una muestra de títulos del corpus
print("\n--- MUESTRA DE TÍTULOS ---")

numeros_muestra = [
    "1", "7", "25", "50", "75",
    "100", "125", "150", "175",
    "185A", "200", "223A", "234A", "243"
]

for articulo in corpus_articulos:
    if articulo["numero"] in numeros_muestra:
        print(
            f'Artículo {articulo["numero"]}: '
            f'{articulo["titulo"]}'
        )

# Revisar el encabezado original del artículo 223A
print("\n--- REVISIÓN DEL ARTÍCULO 223A ---")

for encabezado in encabezados:
    if encabezado.group(1) == "223A":

        inicio = encabezado.start()
        fragmento = texto_unido[inicio:inicio + 700]

        print(repr(fragmento))
        break

# Comprobar artículos vacíos o demasiado cortos
print("\n--- CONTROL DE CALIDAD DEL CORPUS ---")

articulos_vacios = [
    articulo["numero"]
    for articulo in corpus_articulos
    if not articulo["texto"].strip()
]

articulos_cortos = [
    (articulo["numero"], len(articulo["texto"]))
    for articulo in corpus_articulos
    if len(articulo["texto"]) < 100
]

print("Total de artículos:", len(corpus_articulos))
print("Artículos vacíos:", articulos_vacios)
print("Artículos con menos de 100 caracteres:", articulos_cortos)

# Buscar posibles palabras divididas por guiones
print("\n--- REVISIÓN DE GUIONES ---")

posibles_errores = []

for articulo in corpus_articulos:

    coincidencias_guion = re.findall(
        r"\b[a-záéíóúñ]+-[a-záéíóúñ]+\b",
        articulo["texto"],
        re.IGNORECASE
    )

    for palabra in coincidencias_guion:
        posibles_errores.append(
            (articulo["numero"], palabra)
        )

print("Total de coincidencias:", len(posibles_errores))
print("Primeras 30 coincidencias:")

for numero, palabra in posibles_errores[:30]:
    print(f"Artículo {numero}: {palabra}")

# Revisar el contexto de las expresiones con guiones
print("\n--- CONTEXTO DE GUIONES ---")

for articulo in corpus_articulos:

    for coincidencia in re.finditer(
        r"\b[a-záéíóúñ]+-[a-záéíóúñ]+\b",
        articulo["texto"],
        re.IGNORECASE
    ):

        inicio = max(0, coincidencia.start() - 60)
        fin = min(
            len(articulo["texto"]),
            coincidencia.end() + 60
        )

        fragmento = articulo["texto"][inicio:fin]

        print(f'\nArtículo {articulo["numero"]}')
        print("Expresión:", coincidencia.group())
        print("Contexto:", fragmento)

# Comprobar guiones en el texto original del PDF
print("\n--- GUIONES EN EL TEXTO ORIGINAL ---")

palabras_revisar = [
    "ordena-miento",
    "pro-mover",
    "departa-mentales",
    "re-conocimientos",
    "con-vivencia",
    "per-turbación",
    "COMPOR-TAMIENTOS",
    "re-unión"
]

for palabra in palabras_revisar:
    posicion = texto_unido.find(palabra)

    print(f"\nExpresión: {palabra}")

    if posicion != -1:
        inicio = max(0, posicion - 35)
        fin = min(len(texto_unido), posicion + len(palabra) + 35)

        print(repr(texto_unido[inicio:fin]))
    else:
        print("No encontrada exactamente en el texto original")

# Verificar las correcciones aplicadas
print("\n--- VERIFICACIÓN DE CORRECCIONES ---")

for original, corregida in CORRECCIONES_VERIFICAR.items():

    apariciones_original = sum(
        articulo["texto"].count(original)
        for articulo in corpus_articulos
    )

    apariciones_corregida = sum(
        articulo["texto"].count(corregida)
        for articulo in corpus_articulos
    )

    print(
        f"{original} -> {corregida} | "
        f"Original restante: {apariciones_original} | "
        f"Forma corregida: {apariciones_corregida}"
    )

print("\n--- EXPRESIONES QUE DEBEN CONSERVARSE ---")

for expresion in ["minero-ambiental", "buque-puerto", "Decreto-ley"]:

    cantidad = sum(
        articulo["texto"].count(expresion)
        for articulo in corpus_articulos
    )

    print(f"{expresion}: {cantidad} apariciones")

# Revisar el texto extraído del artículo 100
print("\n--- REVISIÓN DEL ARTÍCULO 100 ---")

for articulo in corpus_articulos:
    if articulo["numero"] == "100":

        posicion = articulo["texto"].find("COMPOR-TAMIENTOS")

        if posicion != -1:
            print(articulo["texto"][posicion:])
        else:
            print("No se encontró el encabezado de la tabla.")

# Identificar los numerales de la tabla del artículo 100
print("\n--- NUMERALES DE LA TABLA DEL ARTÍCULO 100 ---")

for articulo in corpus_articulos:
    if articulo["numero"] == "100":

        posicion = articulo["texto"].find("COMPOR-TAMIENTOS")

        if posicion != -1:
            texto_tabla = articulo["texto"][posicion:]

            numerales = re.findall(
                r"Numeral\s+(\d+)",
                texto_tabla,
                re.IGNORECASE
            )

            print("Numerales encontrados:", numerales)
            print("Cantidad:", len(numerales))
        else:
            print("No se encontró el encabezado de la tabla.")

# Separar las filas de la tabla del artículo 100
print("\n--- FILAS DE LA TABLA DEL ARTÍCULO 100 ---")

for articulo in corpus_articulos:
    if articulo["numero"] == "100":

        posicion = articulo["texto"].find("COMPOR-TAMIENTOS")

        if posicion != -1:
            texto_tabla = articulo["texto"][posicion:]

            filas = re.findall(
                r"Numeral\s+(\d+)\s+(.*?)(?=Numeral\s+\d+|$)",
                texto_tabla,
                re.IGNORECASE
            )


            tabla_estructurada = []

            for numero, medidas in filas:
                fila = {
                    "numeral": int(numero),
                    "medidas_correctivas": [
                        medida.strip()
                        for medida in medidas.split(";")
                    ]
                }

                tabla_estructurada.append(fila)

            print(json.dumps(
                tabla_estructurada,
                ensure_ascii=False,
                indent=4
            ))

            articulo["tabla_medidas_correctivas"] = tabla_estructurada

        else:
            print("No se encontró la tabla.")

# Guardar el corpus completo después de procesar los artículos
with open(ruta_json, "w", encoding="utf-8") as archivo:
    json.dump(
        corpus_articulos,
        archivo,
        ensure_ascii=False,
        indent=4
    )

print("\n--- GUARDADO FINAL DEL CORPUS ---")
print("Archivo guardado correctamente:", ruta_json)
print("Total de artículos guardados:", len(corpus_articulos))

# Verificar el contenido del archivo JSON guardado
print("\n--- VERIFICACIÓN DEL JSON GUARDADO ---")

with open(ruta_json, "r", encoding="utf-8") as archivo:
    corpus_guardado = json.load(archivo)

print("Artículos recuperados:", len(corpus_guardado))

articulo_100 = next(
    (articulo for articulo in corpus_guardado
     if articulo["numero"] == "100"),
    None
)

if articulo_100 is not None:
    print("Artículo 100 encontrado: Sí")

    tabla = articulo_100.get("tabla_medidas_correctivas", [])

    print("Filas de la tabla:", len(tabla))
    print("Numerales:", [fila["numeral"] for fila in tabla])
else:
    print("Artículo 100 encontrado: No")
