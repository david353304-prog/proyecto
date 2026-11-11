
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

# Verificar el archivo JSON de fragmentos

# Cargar los fragmentos guardados para análisis posteriores
with open(ruta_fragmentos, "r", encoding="utf-8") as archivo:
    fragmentos_guardados = json.load(archivo)

# Revisar los límites de los fragmentos del artículo 135
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

# Identificar artículos divididos en varios fragmentos
print("\n--- ARTÍCULOS CON VARIOS FRAGMENTOS ---")

from collections import Counter

conteo_fragmentos = Counter(
    fragmento["numero_articulo"]
    for fragmento in fragmentos_guardados
)

articulos_divididos = {
    numero: cantidad
    for numero, cantidad in conteo_fragmentos.items()
    if cantidad > 1
}

print("Total de artículos:", len(corpus_articulos))
print("Artículos con un solo fragmento:",
      sum(1 for cantidad in conteo_fragmentos.values() if cantidad == 1))

print("Artículos con varios fragmentos:", len(articulos_divididos))

print("\nArtículos divididos:")

for numero, cantidad in articulos_divididos.items():
    print(f"Artículo {numero}: {cantidad} fragmentos")

# Examinar la estructura del artículo 135
print("\n--- ESTRUCTURA DEL ARTÍCULO 135 ---")

import re

articulo_135 = next(
    articulo
    for articulo in corpus_articulos
    if articulo["numero"] == "135"
)

texto_135 = articulo_135["texto"]

patron_estructura = re.compile(
    r"\bPARÁGRAFO\s+\d+[A-Z]?\b"
    r"|\bNumeral\s+\d+\b"
    r"|\b\d+\.\s+(?=[A-ZÁÉÍÓÚÑ])",
    re.IGNORECASE
)

coincidencias = list(patron_estructura.finditer(texto_135))

print("Posibles marcadores encontrados:", len(coincidencias))

for coincidencia in coincidencias:
    inicio = coincidencia.start()
    fin = coincidencia.end()

    contexto = texto_135[fin:fin + 75]

    print(
        f"{coincidencia.group()} "
        f"→ {contexto.strip()}"
    )

# Extraer las medidas correctivas del artículo 135
print("\n--- MEDIDAS CORRECTIVAS DEL ARTÍCULO 135 ---")

patron_medidas = re.compile(
    r"\bNumeral\s+(\d+)\b",
    re.IGNORECASE
)

coincidencias_medidas = list(
    patron_medidas.finditer(texto_135)
)

medidas_correctivas = []

for indice, coincidencia in enumerate(coincidencias_medidas):

    numero = coincidencia.group(1)

    inicio = coincidencia.end()

    if indice + 1 < len(coincidencias_medidas):
        fin = coincidencias_medidas[indice + 1].start()
    else:
        fin = len(texto_135)

    medida = texto_135[inicio:fin].strip()

    medidas_correctivas.append({
        "numeral": numero,
        "medida": medida
    })

print("Medidas encontradas:", len(medidas_correctivas))

for registro in medidas_correctivas:
    print(
        f'Numeral {registro["numeral"]}: '
        f'{registro["medida"]}'
    )

# Separar notas normativas de las medidas correctivas
print("\n--- SEPARACIÓN DE NOTAS NORMATIVAS ---")

for registro in medidas_correctivas:

    registro["nota_normativa"] = None

    patron_nota = re.search(
        r"\(Corregido por el Art\.[^)]+\)",
        registro["medida"],
        re.IGNORECASE
    )

    if patron_nota:

        registro["nota_normativa"] = patron_nota.group()

        registro["medida"] = (
            registro["medida"][:patron_nota.start()]
            + registro["medida"][patron_nota.end():]
        ).strip()

# Mostrar el resultado del numeral 24
for registro in medidas_correctivas:

    if registro["numeral"] == "24":

        print("Numeral:", registro["numeral"])
        print("Medida:", registro["medida"])
        print("Nota normativa:", registro["nota_normativa"])

# Extraer los comportamientos del artículo 135
print("\n--- COMPORTAMIENTOS DEL ARTÍCULO 135 ---")

# Tomar el texto anterior al primer parágrafo
coincidencia_paragrafo = re.search(
    r"\bPARÁGRAFO\s+1\b",
    texto_135,
    re.IGNORECASE
)

texto_comportamientos = texto_135[:coincidencia_paragrafo.start()]

# Buscar los numerales del 1 al 24
patron_comportamientos = re.compile(
    r"\b(\d{1,2})\.\s+(?=[A-ZÁÉÍÓÚÑ])"
)

coincidencias_comportamientos = [
    coincidencia
    for coincidencia in patron_comportamientos.finditer(texto_comportamientos)
    if 1 <= int(coincidencia.group(1)) <= 24
]

comportamientos = []

for indice, coincidencia in enumerate(coincidencias_comportamientos):

    numero = coincidencia.group(1)
    inicio = coincidencia.end()

    if indice + 1 < len(coincidencias_comportamientos):
        fin = coincidencias_comportamientos[indice + 1].start()
    else:
        fin = len(texto_comportamientos)

    descripcion = texto_comportamientos[inicio:fin].strip()

    comportamientos.append({
        "numeral": numero,
        "comportamiento": descripcion
    })

print("Comportamientos encontrados:", len(comportamientos))

for registro in comportamientos:
    print(
        f'Numeral {registro["numeral"]}: '
        f'{registro["comportamiento"][:100]}'
    )

# Revisar comportamientos que requieren verificación
print("\n--- REVISIÓN DE COMPORTAMIENTOS ---")

numerales_revisar = ["4", "6", "18"]

for registro in comportamientos:

    if registro["numeral"] in numerales_revisar:

        print("\n" + "=" * 50)
        print("NUMERAL:", registro["numeral"])
        print("=" * 50)

        print(registro["comportamiento"])

# Separar el encabezado B) del comportamiento 4
print("\n--- CORRECCIÓN ESTRUCTURAL DEL NUMERAL 4 ---")

encabezado_b = None

for registro in comportamientos:

    if registro["numeral"] == "4":

        texto_original = registro["comportamiento"]

        partes = re.split(
            r"(?=\bB\)\s*Actuaciones\b)",
            texto_original,
            maxsplit=1,
            flags=re.IGNORECASE
        )

        if len(partes) == 2:

            registro["comportamiento"] = partes[0].strip()

            encabezado_b = partes[1].strip()

        print("Numeral:", registro["numeral"])
        print("Comportamiento:", registro["comportamiento"])
        print("Encabezado separado:", encabezado_b)

        break

# Relacionar comportamientos con medidas correctivas
print("\n--- RELACIÓN DE COMPORTAMIENTOS Y MEDIDAS ---")

medidas_por_numeral = {
    registro["numeral"]: registro
    for registro in medidas_correctivas
}

registros_relacionados = []

for comportamiento in comportamientos:

    numero = comportamiento["numeral"]

    medida = medidas_por_numeral.get(numero)

    if medida is not None:

        registro_completo = {
            "articulo": "135",
            "numeral": numero,
            "comportamiento": comportamiento["comportamiento"],
            "medida_correctiva": medida["medida"],
            "nota_normativa": medida["nota_normativa"]
        }

        registros_relacionados.append(registro_completo)

print("Comportamientos encontrados:", len(comportamientos))
print("Medidas encontradas:", len(medidas_correctivas))
print("Relaciones creadas:", len(registros_relacionados))

print("\n--- EJEMPLO: NUMERAL 5 ---")

for registro in registros_relacionados:

    if registro["numeral"] == "5":

        print("Artículo:", registro["articulo"])
        print("Numeral:", registro["numeral"])
        print("Comportamiento:", registro["comportamiento"])
        print("Medida correctiva:", registro["medida_correctiva"])
        print("Nota normativa:", registro["nota_normativa"])

        break

# Identificar encabezados de las secciones del artículo 135
print("\n--- ENCABEZADOS DEL ARTÍCULO 135 ---")

patron_encabezados = re.compile(
    r"(?<![A-Za-zÁÉÍÓÚÑáéíóúñ])([A-Z])\)\s*"
)

encabezados_encontrados = list(
    patron_encabezados.finditer(texto_comportamientos)
)

print("Posibles encabezados encontrados:", len(encabezados_encontrados))

for coincidencia in encabezados_encontrados:

    letra = coincidencia.group(1)

    inicio = coincidencia.start()
    fin = min(inicio + 180, len(texto_comportamientos))

    contexto = texto_comportamientos[inicio:fin]

    print("\nSección:", letra)
    print("Texto:", contexto)

# Asignar secciones a los comportamientos del artículo 135
print("\n--- ASIGNACIÓN DE SECCIONES ---")

secciones_articulo_135 = {
    "A": {
        "numerales": range(1, 5),
        "titulo": "Parcelar, urbanizar, demoler, intervenir o construir"
    },
    "B": {
        "numerales": range(5, 9),
        "titulo": (
            "Actuaciones en los inmuebles declarados de "
            "conservación e interés cultural, histórico, "
            "urbanístico, paisajístico y arquitectónico"
        )
    },
    "C": {
        "numerales": range(9, 13),
        "titulo": "Usar o destinar un inmueble a"
    },
    "D": {
        "numerales": range(13, 25),
        "titulo": "Incumplir cualquiera de las siguientes obligaciones"
    }
}

for registro in registros_relacionados:

    numero = int(registro["numeral"])

    registro["seccion"] = None
    registro["titulo_seccion"] = None

    for letra, datos in secciones_articulo_135.items():

        if numero in datos["numerales"]:

            registro["seccion"] = letra
            registro["titulo_seccion"] = datos["titulo"]

            break

for letra in secciones_articulo_135:

    cantidad = sum(
        1
        for registro in registros_relacionados
        if registro["seccion"] == letra
    )

    print(f"Sección {letra}: {cantidad} comportamientos")

sin_seccion = [
    registro["numeral"]
    for registro in registros_relacionados
    if registro["seccion"] is None
]

print("Comportamientos sin sección:", len(sin_seccion))

# Revisar un registro jurídico completo
print("\n--- REGISTRO COMPLETO DEL NUMERAL 5 ---")

for registro in registros_relacionados:

    if registro["numeral"] == "5":

        print(
            json.dumps(
                registro,
                ensure_ascii=False,
                indent=4
            )
        )

        break

# Guardar los registros estructurados del artículo 135
print("\n--- GUARDADO DEL ARTÍCULO 135 ESTRUCTURADO ---")

ruta_articulo_135 = (
    Path(__file__).parent
    / "fragmentos"
    / "articulo_135_estructurado.json"
)

with open(ruta_articulo_135, "w", encoding="utf-8") as archivo:
    json.dump(
        registros_relacionados,
        archivo,
        ensure_ascii=False,
        indent=4
    )

print("Archivo guardado en:", ruta_articulo_135)
print("Registros guardados:", len(registros_relacionados))

# Agregar información de la fuente a los registros
print("\n--- METADATOS DEL ARTÍCULO 135 ---")

for registro in registros_relacionados:

    registro["fuente"] = articulo_135["fuente"]

    registro["entidad_fuente"] = articulo_135["entidad_fuente"]

    registro["url_fuente"] = articulo_135["url_fuente"]

    registro["pagina_inicio"] = articulo_135["pagina_inicio"]

    registro["pagina_fin"] = articulo_135["pagina_fin"]

print("Registros actualizados:", len(registros_relacionados))

# Mostrar los metadatos del primer registro
primer_registro = registros_relacionados[0]

print("Artículo:", primer_registro["articulo"])
print("Fuente:", primer_registro["fuente"])
print("Entidad:", primer_registro["entidad_fuente"])
print("URL:", primer_registro["url_fuente"])
print("Página inicial:", primer_registro["pagina_inicio"])
print("Página final:", primer_registro["pagina_fin"])

# Actualizar el JSON con los metadatos de la fuente
print("\n--- ACTUALIZACIÓN DEL JSON ESTRUCTURADO ---")

with open(ruta_articulo_135, "w", encoding="utf-8") as archivo:
    json.dump(
        registros_relacionados,
        archivo,
        ensure_ascii=False,
        indent=4
    )

# Leer nuevamente el archivo para verificarlo
with open(ruta_articulo_135, "r", encoding="utf-8") as archivo:
    registros_verificados = json.load(archivo)

print("Registros guardados:", len(registros_verificados))

campos_fuente = [
    "fuente",
    "entidad_fuente",
    "url_fuente",
    "pagina_inicio",
    "pagina_fin"
]

registros_con_metadatos = sum(
    all(
        campo in registro and registro[campo] is not None
        for campo in campos_fuente
    )
    for registro in registros_verificados
)

print("Registros con metadatos completos:", registros_con_metadatos)
print("Archivo actualizado:", ruta_articulo_135)

# Preparar un registro estructurado para búsqueda RAG
print("\n--- TEXTO PARA RECUPERACIÓN RAG ---")

registro_ejemplo = next(
    registro
    for registro in registros_verificados
    if registro["numeral"] == "5"
)

texto_rag = (
    f'Ley 1801 de 2016. '
    f'Artículo {registro_ejemplo["articulo"]}. '
    f'Sección {registro_ejemplo["seccion"]}: '
    f'{registro_ejemplo["titulo_seccion"]}. '
    f'Numeral {registro_ejemplo["numeral"]}. '
    f'Comportamiento: {registro_ejemplo["comportamiento"]} '
    f'Medida correctiva: {registro_ejemplo["medida_correctiva"]}'
)

if registro_ejemplo["nota_normativa"]:
    texto_rag += (
        f' Nota normativa: '
        f'{registro_ejemplo["nota_normativa"]}'
    )

print(texto_rag)
print("\nCantidad de palabras:", len(texto_rag.split()))

# Generar textos RAG para los 24 numerales del artículo 135
print("\n--- GENERACIÓN DE TEXTOS RAG DEL ARTÍCULO 135 ---")

registros_rag = []

for registro in registros_verificados:

    texto = (
        f'Ley 1801 de 2016. '
        f'Artículo {registro["articulo"]}. '
        f'Sección {registro["seccion"]}: '
        f'{registro["titulo_seccion"]}. '
        f'Numeral {registro["numeral"]}. '
        f'Comportamiento: {registro["comportamiento"]} '
        f'Medida correctiva: {registro["medida_correctiva"]}'
    )

    if registro["nota_normativa"]:
        texto += (
            f' Nota normativa: {registro["nota_normativa"]}'
        )

    registro_rag = {
        **registro,
        "id": (
            f'articulo_{registro["articulo"]}'
            f'_numeral_{registro["numeral"]}'
        ),
        "texto_rag": texto
    }

    registros_rag.append(registro_rag)

print("Registros procesados:", len(registros_verificados))
print("Textos RAG generados:", len(registros_rag))

textos_vacios = sum(
    not registro["texto_rag"].strip()
    for registro in registros_rag
)

print("Textos RAG vacíos:", textos_vacios)

print("\nPrimer identificador:", registros_rag[0]["id"])
print("Último identificador:", registros_rag[-1]["id"])

# Guardar los registros RAG del artículo 135
print("\n--- GUARDADO DE REGISTROS RAG ---")

ruta_rag_135 = (
    Path(__file__).parent
    / "fragmentos"
    / "articulo_135_rag.json"
)

with open(ruta_rag_135, "w", encoding="utf-8") as archivo:
    json.dump(
        registros_rag,
        archivo,
        ensure_ascii=False,
        indent=4
    )

# Verificar que el archivo se pueda leer
with open(ruta_rag_135, "r", encoding="utf-8") as archivo:
    registros_rag_guardados = json.load(archivo)

print("Archivo:", ruta_rag_135)
print("Registros guardados:", len(registros_rag_guardados))

identificadores = [
    registro["id"]
    for registro in registros_rag_guardados
]

print("Identificadores únicos:", len(set(identificadores)))

registros_incompletos = sum(
    not registro.get("texto_rag", "").strip()
    or not registro.get("url_fuente")
    for registro in registros_rag_guardados
)

print("Registros incompletos:", registros_incompletos)

# Verificar la integridad de los textos RAG
print("\n--- INTEGRIDAD DE LOS TEXTOS RAG ---")

registros_con_errores = []

for registro in registros_rag_guardados:

    texto = registro["texto_rag"]

    comportamiento = registro["comportamiento"]
    medida = registro["medida_correctiva"]
    seccion = registro["titulo_seccion"]

    if (
        comportamiento not in texto
        or medida not in texto
        or seccion not in texto
    ):
        registros_con_errores.append(registro["id"])

print("Registros revisados:", len(registros_rag_guardados))
print("Registros con errores:", len(registros_con_errores))

if registros_con_errores:
    print("Identificadores con errores:", registros_con_errores)
else:
    print("Todos los textos contienen su comportamiento, medida y sección.")

# Verificar la cobertura de los numerales del artículo 135
print("\n--- COBERTURA DE NUMERALES DEL ARTÍCULO 135 ---")

numerales_esperados = set(range(1, 25))

numerales_encontrados = [
    int(registro["numeral"])
    for registro in registros_rag_guardados
]

numerales_unicos = set(numerales_encontrados)

numerales_faltantes = sorted(
    numerales_esperados - numerales_unicos
)

numerales_inesperados = sorted(
    numerales_unicos - numerales_esperados
)

numerales_repetidos = sorted({
    numero
    for numero in numerales_encontrados
    if numerales_encontrados.count(numero) > 1
})

print("Numerales esperados:", len(numerales_esperados))
print("Numerales encontrados:", len(numerales_encontrados))
print("Numerales únicos:", len(numerales_unicos))
print("Numerales faltantes:", numerales_faltantes)
print("Numerales inesperados:", numerales_inesperados)
print("Numerales repetidos:", numerales_repetidos)
