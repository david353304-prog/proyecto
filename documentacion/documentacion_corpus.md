# Documentación del corpus jurídico del chatbot RAG

## Contraste con fuente oficial del 18 de noviembre de 2026

La [compilación de Cancillería](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm)
identifica como publicación original el Diario Oficial 49.949 del 29 de
julio de 2016. Se descargó su HTML y se cotejó automáticamente con el
JSON extraído del PDF EVA. El archivo
[`referencia_normativa.json`](../motor_documental/corpus/referencia_normativa.json)
registra la URL, los enlaces por artículo cuando existen, la fecha, la
huella SHA-256 del HTML y el resultado por artículo. Los dos insumos
cubren los mismos **249** identificadores. Coinciden **90** tras comparar
tokens sin distinguir mayúsculas ni puntuación. Los **159** restantes
requieren conciliación. Una diferencia puede deberse a una reforma, una
nota de edición, una tabla o un error de extracción.

La referencia conserva la jerarquía de libro, título y capítulo que
publica el HTML. Reconoce artículos por encabezado, parágrafos y
numerales por inicio de bloque, y literales mediante sus letras
de lista. El epígrafe se toma del encabezado y el tema del nivel
jerárquico más específico disponible. Se compactan blancos y se
suprimen guiones blandos, elementos HTML y firmas al final de la ley.
Las notas angulares del editor se guardan aparte. Las filas de tabla
se mantienen como bloques de texto. Las subdivisiones ambiguas
requieren cotejo manual. Los rótulos de los literales en Cancillería
pueden diferir de los rótulos de trabajo del índice existente, como
ocurre en el artículo 223A.

### Cambios con impacto en las respuestas

| Disposición | Hallazgo verificable |
|---|---|
| 8 y 10 | La compilación registra reforma de los principios y de los deberes de las autoridades por los arts. 2 y 3 de la Ley 2318 de 2023. [Compilación oficial](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#8) |
| 33 y 92 | La Ley 2450 de 2025 reformó el art. 33 y añadió disposiciones sobre ruido al art. 92. Las respuestas del banco sobre ruido requieren cotejarse con la nueva redacción. [Art. 33](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#33) · [Art. 92](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#92) |
| 33.2.c y 140.7 | C-253/19 declaró inexequibles expresiones sobre bebidas alcohólicas y sustancias psicoactivas del texto entonces examinado. El alcance de la decisión debe distinguirse de las redacciones posteriores. [Corte Constitucional](https://www.corteconstitucional.gov.co/comunicados/no.%2018%20comunicado%2006%20de%20junio%20de%202019.pdf) |
| 47 a 75 | C-223/17 declaró inexequibles los artículos del Título VI sujetos a reserva de ley estatutaria y difirió los efectos hasta antes del 20 de junio de 2019. [Parte resolutiva](https://www.corteconstitucional.gov.co/secretaria/edictos/EDICTOS%20OCTUBRE%202017.php) |
| 88 | La compilación registra la modificación del servicio de baño por el art. 2 de la Ley 2633 de 2026. [Art. 88](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#88) |
| 117, 119 y 126–134 | La Ley 2054 de 2020 modificó las disposiciones sobre animales y la terminología de los caninos de manejo especial. [Compilación oficial](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#126) |
| 155 | C-281/17 examinó el texto original. El art. 40 de la Ley 2197 de 2022 lo reformó y C-081/23 examinó el nuevo parágrafo 5 y sus condicionamientos. [C-281/17](https://www.corteconstitucional.gov.co/relatoria/2017/C-281-17.htm) · [C-380/23, síntesis de C-081/23](https://www.corteconstitucional.gov.co/relatoria/2023/c-380-23) |
| 223A | El art. 47 de la Ley 2197 de 2022 adicionó el procedimiento, con corrección del art. 25 del Decreto 207 de 2022. [Art. 223A](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#223A) |

El estado verificable registrado para los artículos 47 a 75 se refiere
al texto original y enlaza la sentencia. Para las demás entradas el
campo queda en `pendiente_revision_juridica`, incluso cuando coincide el
texto. La referencia es un insumo de auditoría. El chatbot sigue
usando el corpus y el índice históricos durante la revisión del grupo.

El [artículo 41 de la Ley 23 de 1982](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=3431)
prevé la reproducción de leyes y decisiones judiciales conforme a la
edición oficial y salvo prohibición. La exportación identifica la
compilación y conserva las notas como material editorial identificado.
La licencia específica del PDF EVA y de los elementos editoriales
queda pendiente de verificar antes de redistribuirlos.

Para reproducir el contraste, descarga el HTML de Cancillería y ejecuta
`python -m motor_documental.corpus.contrastar_corpus ley1801.html --fecha-consulta AAAA-MM-DD --salida referencia.json`.
Compara la huella del HTML si repites la corrida con una descarga nueva.

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
