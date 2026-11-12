# Documentación del corpus jurídico del chatbot RAG

## 1. Objetivo

Documentar el origen, procesamiento, limpieza y segmentación
del corpus de la Ley 1801 de 2016 utilizado por el chatbot
jurídico desarrollado como proyecto académico.

## 2. Fuente del corpus

El corpus corresponde a la Ley 1801 de 2016 de Colombia,
Código Nacional de Seguridad y Convivencia Ciudadana.

Fuente registrada:
- Entidad: Departamento Administrativo de la Función Pública.
- Plataforma: EVA - Gestor Normativo.
- URL: https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=80538

PDF utilizado:
`motor_documental/corpus/Ley_1801_de_2016.pdf`

La fecha original de consulta no está documentada.
La vigencia de todas las disposiciones requiere verificación.

## 3. Extracción

El archivo `motor_documental/extraer_texto.py` utiliza
PyMuPDF para extraer el texto del PDF.

Los artículos se identifican mediante expresiones regulares
que reconocen su numeración, incluidas letras adicionales.

Cada artículo se delimita utilizando el inicio del
artículo siguiente.

## 4. Limpieza del texto

Se realizan las siguientes operaciones:

- Eliminación de encabezados repetidos.
- Normalización de espacios y saltos de línea.
- Corrección de ligaduras tipográficas.
- Sustitución de palabras específicas verificadas.
- Extracción del título cuando está disponible.

## 5. Corpus estructurado

Archivo:
`motor_documental/corpus/articulos_ley_1801.json`

Contiene 249 artículos identificados de forma única.

Metadatos:
- numero
- titulo
- pagina_inicio
- pagina_fin
- fuente
- entidad_fuente
- url_fuente
- texto

No incluye campos independientes de libro, capítulo,
estado de vigencia o clasificación temática.

## 6. Fragmentación para el chatbot

Archivo de generación:
`motor_documental/generar_fragmentos.py`

Función:
`dividir_en_fragmentos_por_tokens`

Modelo de tokenización:
`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

Configuración:
- Tamaño máximo: 120 tokens, incluidos tokens especiales.
- Solapamiento aproximado: 20 tokens.
- Se respetan palabras completas.
- Cada artículo se fragmenta independientemente.

El solapamiento no es necesariamente de 20 tokens exactos,
porque se calcula retrocediendo por palabras completas.

## 7. Fragmentos generados

Archivo:
`motor_documental/fragmentos/fragmentos_ley_1801.json`

Resultados:
- Artículos: 249.
- Fragmentos: 866.
- Artículos con fragmentos: 249.
- Artículos sin fragmentos: 0.
- Mínimo por artículo: 1 fragmento.
- Máximo por artículo: 21 fragmentos.

Cada fragmento conserva su identificador, número de
artículo, título, páginas, fuente, URL y texto.

## 8. Utilización en el chatbot RAG

Los fragmentos constituyen unidades de recuperación
de información jurídica.

El sistema utiliza los fragmentos recuperados como
contexto para generar respuestas sobre la Ley 1801.

Los metadatos permiten identificar los artículos
relacionados con la respuesta y mostrar referencias
a las fuentes utilizadas.

## 9. Condiciones de uso

El corpus procede de un documento normativo colombiano
atribuido al Departamento Administrativo de la Función Pública.

No se ha verificado una licencia específica aplicable
al archivo PDF utilizado.

Las condiciones de reutilización deben comprobarse
antes de la entrega definitiva.

## 10. Limitaciones

- No se conoce la fecha original de consulta.
- No se ha verificado integralmente la vigencia normativa.
- No se documentan todas las modificaciones posteriores.
- No existen metadatos explícitos de jerarquía normativa.
- La extracción automática puede presentar errores.
- La fragmentación puede separar información relacionada.

## 11. Alcance académico

El chatbot es un prototipo académico de consulta
informativa sobre la Ley 1801 de 2016.

No reemplaza la consulta de fuentes normativas
actualizadas ni el asesoramiento jurídico profesional.

## 12. Archivos relacionados

- `motor_documental/corpus/Ley_1801_de_2016.pdf`
- `motor_documental/corpus/articulos_ley_1801.json`
- `motor_documental/fragmentos/fragmentos_ley_1801.json`
- `motor_documental/extraer_texto.py`
- `motor_documental/generar_fragmentos.py`
- `motor_documental/utilidades_texto.py`
