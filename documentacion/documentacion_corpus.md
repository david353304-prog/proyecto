# Documentación del corpus jurídico del chatbot RAG

## Ampliación de medidas correctivas del 20 de noviembre de 2026

La selección pública pasó de 31 a 33 artículos y de 127 a 132
ventanas de dimensión 384. El cotejo usa las capturas documentadas del
18 de noviembre y la revisión oficial del 20. La evidencia por bloque
conserva ambas fechas, las huellas y las fuentes.

- **Artículo 172, inciso principal.** Incluye definición y finalidad.
  Se excluyen los parágrafos sobre naturaleza y registro. T-234/21
  recoge la definición y C-349/17 distingue el alcance de las medidas
  en el procedimiento policial. [Ley 1801, art. 172](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#172)
  · [T-234/21](https://www.corteconstitucional.gov.co/relatoria/2021/t-234-21.htm)
  · [C-349/17](https://www.corteconstitucional.gov.co/relatoria/2017/c-349-17.htm)
- **Artículo 173, encabezado y numerales 1 a 20.** Se incorpora
  el catálogo según el artículo 12 del Decreto 555 de 2017, incluida
  la denominación corregida de la última medida. Una enumeración
  general no determina qué medida procede en un caso concreto.
  [Ley 1801, art. 173](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#173)
  · [Decreto 555 de 2017](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=80775)

[Cotejo por bloque](../motor_documental/corpus/evidencia_ampliacion.json)
· [Auditoría del índice](../motor_documental/pruebas/auditoria_medidas_publicables.json)

## Alcance de la entrega según la guía del docente

La p. 3 exige texto oficial vigente, fecha de consulta, identificación de
reformas y fallos pertinentes, limpieza y segmentación hasta parágrafo y
numeral. Cada fragmento requiere identificador, jerarquía, epígrafe,
estado de vigencia y tema. La p. 6 exige el corpus en JSON y documentación
de origen, fecha, segmentación, metadatos y licencia de uso. La p. 7 exige
verificar vigencia y modificaciones antes de incluir cada artículo.

La entrega para consulta corresponde a la selección pública de 31 artículos.
Los JSON de referencia y selección identifican las unidades habilitadas.
Los metadatos y la auditoría por bloque vinculan cada ventana con esas
unidades. El estado de cotejo se interpreta junto con el alcance y las
exclusiones de cada artículo. De los 159 artículos del expediente,
22 tienen algún apartado en la selección pública. El cotejo de esos
apartados deja abiertas las diferencias que afectan al resto del artículo.

La guía no fija un mínimo de artículos ni exige entregar el PDF histórico.
Las condiciones de uso documentan la base de reproducción del texto
normativo y el tratamiento de los elementos editoriales.

## Auditoría del corpus público de 28 artículos (evidencia histórica)

La selección de cierre reúne 28 artículos, 128 bloques aprobados y 63 ventanas. La auditoría reconstruye cada artículo desde su encabezado y los bloques seleccionados de la referencia. Verifica el texto y los caracteres de inicio y fin de cada ventana, y recalcula sus IDs de apartado por intersección con los bloques. Excluye los textos históricos bloqueados y comprueba que el material público carezca de marcas de notas editoriales. El registro indica entidad, URL, captura, revisión disponible, huella o posición del bloque y enlaces de cotejo. [Auditoría por bloque](../motor_documental/pruebas/auditoria_corpus_cierre.json)

El expediente conserva 159 diferencias. La clasificación de 48 como extracción o formato indica candidatas a revisión. El cotejo estricto de los textos completos ignorando solo espacios no cerró ningún caso. Las 27 reformas, 77 diferencias vinculadas a decisiones judiciales y 7 de revisión jurídica siguen en el expediente histórico. Algunas selecciones tienen evidencia puntual para sus propios bloques. La aprobación de un bloque no cierra automáticamente el expediente del artículo.

La procedencia identifica textos legales y compilaciones oficiales, así como el PDF histórico y la edición empleada. Falta acreditar una licencia específica del PDF EVA, las notas editoriales y los elementos de las compilaciones. El expediente preserva su atribución y el índice público excluye las notas. La revisión de condiciones de redistribución del PDF y de los contenidos editoriales permanece pendiente.


## Control reproducido sobre el corpus público v2

La auditoría del 19 de noviembre verificó 248 bloques de 31 artículos,
127 ventanas y dimensión 384. Reconstruyó los textos y sus intervalos,
verificó la procedencia de los bloques y la exclusión de textos
inexequibles y comprobó la normalización de los vectores. La evaluación
HTTP v2 corresponde a la huella actual. El pasaje histórico de RAG-031
se conserva como prueba separada del rótulo del parágrafo 2.

- Corpus: `e1095acca700aa3c8d84b62e411c45f32a55c9bdf49ccbb6c46f6132d7459b55`.
- FAISS: `6ea62b8b5a1bfd00ae04bf487f5c2c46dea9b98e445f9d14d49bf535d7bf5eb7`.
- Metadatos: `dc7e02316f4ed234b46f14d103dacf2d6f256c1c10caec4ddadf09265d9b0073`.

[Auditoría actual por apartado](../motor_documental/pruebas/auditoria_corpus_pendientes_v2.json)

El artículo 93 se publica con el numeral 1 y su fila de medida.
La Ley 2450 de 2025 modificó el tratamiento del ruido, incluida la
fila del numeral 3 en el parágrafo 2, y añadió el numeral 15 y
disposiciones asociadas. Esos apartados quedan fuera de esta selección.
[Ley 2450 de 2025](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=259638)

## Fecha de captura y fecha de revisión

| Fuente | Evidencia de fecha |
| --- | --- |
| Compilación de Cancillería de la Ley 1801 | Captura HTML documentada el 18 de noviembre de 2026 en `referencia_normativa.json`. La huella de la copia local coincide. El 19 se revisaron los apartados 93.1 y 111.1 y 111.3, con consulta de sus pasajes en la compilación oficial. |
| Compilación de Jurinfo de la Ley 1801 | Captura HTML documentada el 18 de noviembre en `contraste_jep.json`. La huella de la copia local coincide. El cotejo de los bloques revisados el 19 utilizó esa captura. |
| Ley 2450 de 2025 en Jurinfo | El registro de revisión del 19 documenta la consulta de los artículos 21 y 22. No se dispone de una captura local con huella para esta fuente complementaria. |
| Función Pública y PDF de Cancillería | La revisión del 19 conserva enlaces, referencias y extractos de búsqueda. Eso no acredita una descarga completa fechada. El PDF se usó para localizar la nota editorial que relaciona los numerales 3 y 8 del artículo 111. |

`fecha_consulta` en los metadatos se refiere a la captura base del 18, y `fecha_revision_documental` al cotejo posterior del apartado. El valor nulo indica que no se añadió una fecha de revisión específica en este ajuste. La verificación regenerada compara las huellas de las capturas archivadas. La coincidencia de texto respalda la transcripción y no determina por sí sola la vigencia o aplicabilidad.

## Selección pública revisada el 19 de noviembre de 2026

Se seleccionaron los numerales 1 a 5 del artículo 27 y el numeral 2
del artículo 35. Los textos se compararon por bloque con las
compilaciones oficiales archivadas el 18 de noviembre y se cotejaron
con el artículo 39 de la Ley 2197 de 2022 y el alcance de C-600/19 y
C-223/25, según corresponda. Se excluyen las multas, los cuadros de
medidas y los demás numerales. El inciso segundo del artículo 150 y
el parágrafo 1 del artículo 222 siguen fuera del alcance público.
[Selección](../motor_documental/corpus/ampliacion_publicable.json) ·
[Huellas y fuentes por bloque](../motor_documental/corpus/evidencia_ampliacion.json)

El expediente conserva 159 diferencias. Su clasificación preliminar
contiene 48 de extracción o formato, 27 de reforma o corrección
normativa, 77 con señales de decisiones judiciales y 7 de revisión
jurídica. La clasificación orienta la verificación y las coincidencias
entre compilaciones dan evidencia de transcripción. Se requiere revisión
de efectos, redacciones aplicables y fechas antes de ampliar el alcance.

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
| 33 y 93 | La Ley 2450 de 2025 reformó el art. 33 y añadió disposiciones sobre ruido al art. 93. Las respuestas del banco sobre ruido requieren cotejarse con la nueva redacción. [Art. 33](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#33) · [Art. 93](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#93) |
| 33.2.c y 140.7 | C-253/19 declaró inexequibles expresiones sobre bebidas alcohólicas y sustancias psicoactivas del texto entonces examinado. El alcance de la decisión debe distinguirse de las redacciones posteriores. [Corte Constitucional](https://www.corteconstitucional.gov.co/comunicados/no.%2018%20comunicado%2006%20de%20junio%20de%202019.pdf) |
| 47 a 75 | C-223/17 declaró inexequibles los artículos del Título VI sujetos a reserva de ley estatutaria y difirió los efectos hasta antes del 20 de junio de 2019. [Parte resolutiva](https://www.corteconstitucional.gov.co/secretaria/edictos/EDICTOS%20OCTUBRE%202017.php) |
| 88 | La compilación registra la modificación del servicio de baño por el art. 2 de la Ley 2633 de 2026. [Art. 88](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#88) |
| 117, 119 y 126–134 | La Ley 2054 de 2020 modificó las disposiciones sobre animales y la terminología de los caninos de manejo especial. [Compilación oficial](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#126) |
| 155 | C-281/17 examinó el texto original. El art. 40 de la Ley 2197 de 2022 lo reformó y C-081/23 examinó el nuevo parágrafo 5 y sus condicionamientos. [C-281/17](https://www.corteconstitucional.gov.co/relatoria/2017/C-281-17.htm) · [C-380/23, síntesis de C-081/23](https://www.corteconstitucional.gov.co/relatoria/2023/c-380-23) |
| 162 | El resolutivo segundo de C-223/17 declaró inexequible el artículo completo. El histórico conserva su texto y la compilación lo señala como inexequible. [C-223/17](https://www.corteconstitucional.gov.co/relatoria/2017/C-223-17.htm) |
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

## Hoja de conciliación para revisión

[`conciliacion_diferencias.json`](../motor_documental/corpus/conciliacion_diferencias.json)
conserva los 159 artículos marcados en el contraste inicial. Por artículo
incluye los dos textos completos, la URL de cada fuente, las páginas del
PDF, los bloques divergentes, las notas de la compilación y una decisión
propuesta. Los índices de cada bloque se cuentan desde cero sobre tokens
de palabra y el extremo final es exclusivo.

Las categorías pueden coexistir. La clasificación principal prioriza
las señales judiciales, luego las reformas o correcciones normativas,
luego las diferencias atribuibles a formato mediante equivalencias
tipográficas acotadas o límites de extracción. Los casos restantes
requieren revisión jurídica específica. Una nota de reforma puede
referirse a un cambio ya incorporado en el histórico. Las menciones a
sentencias son pistas para comprobar partes resolutivas. La hoja
identifica por separado el alcance cotejado de C-223/17.

| Clasificación principal | Casos |
|---|---:|
| Extracción o formato | 48 |
| Reforma o corrección normativa | 27 |
| Decisión judicial | 77 |
| Revisión jurídica específica | 7 |
| Total | 159 |

Los 159 casos siguen abiertos para revisión del grupo. Cada propuesta
mantiene `aprobado_para_indice: false`. El cotejo legal debe fijar texto,
apartado, fecha de efectos y fuente antes de incorporar una disposición.
El corpus histórico y el índice operativo conservan su estado previo.

Para reproducir el expediente desde la raíz con `.venv` activo:

```bash
python -m motor_documental.corpus.conciliar_diferencias --salida conciliacion_revision.json
python -m unittest discover -s tests -p "test_conciliacion_corpus.py"
```

El generador toma la cobertura de las marcas `diferencias_por_revisar`
de la referencia. Para una descarga futura usa `--referencia` y
`--salida` con rutas distintas. `--historico` permite elegir el
corpus con el que se hizo el contraste. La prueba histórica comprueba
por separado los 159 casos y las huellas SHA-256 del expediente
del 18 de noviembre de 2026.

Mientras se usa el índice histórico, las consultas explícitas sobre
el artículo 162 o los textos originales de los artículos 47 a 75
reciben un aviso con enlace a C-223/17. Los candidatos de esos artículos
se excluyen del contexto generativo y de los fragmentos públicos.
La salvaguarda se aplica a esos textos históricos y la revisión del resto
del corpus sigue abierta.

## Alcance público y evidencia por apartado

El expediente contiene 650 bloques de contraste en 159 artículos. Cada
bloque ubica el epígrafe, cuerpo, numeral, literal o parágrafo de la
referencia, y conserva su URL y fecha. En una eliminación se indica
una ubicación adyacente, que no prueba que el texto eliminado formara
parte de ese apartado. Para los artículos 8, 10, 33, 88, 93, 166, 167,
180, 181 y 206 se añadió el enlace oficial de la reforma y su apartado.
La ficha de cada artículo distingue esas fuentes de las notas
editoriales de la compilación. El cotejo oficial de una reforma y la
revisión de su aplicabilidad son pasos distintos.

El [contraste con Jurinfo de la JEP](../motor_documental/corpus/contraste_jep.json)
procesó los mismos 159 artículos. Coincidieron 156 al comparar tokens.
Las tres diferencias restantes son la separación de ordinales en 84 y
242, y la mención de una directriz COPNIA que aparece en la extracción
de Cancillería para el art. 92 y no en la de Jurinfo. La mención queda
pendiente de revisión editorial. La concordancia de dos compilaciones
no prueba vigencia ni sustituye el cotejo del acto modificatorio o de
la parte resolutiva.

```bash
python -m motor_documental.corpus.contraste_jep ley1801-jep.html --fecha-consulta 2026-11-18
```

El [registro de alcance público](../motor_documental/corpus/alcance_publicable.json)
incluye los artículos 1, 2, 5, 6 y 7, tras comparar el texto y las
anotaciones visibles de las compilaciones oficiales. El servicio usa
la redacción de Cancillería para contexto y fuentes. Los vectores
históricos solo ordenan resultados del subconjunto. La auditoría comprueba
que sus nueve fragmentos sean subsecuencias contiguas del texto
cotejado tras normalizar la puntuación. El cotejo habilita una descripción
documental acotada. No certifica aplicación jurídica a casos concretos.

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

Consulta documental del 19 de noviembre de 2026. El artículo 41 de la
Ley 23 de 1982 permite reproducir normas y decisiones judiciales cuando
la reproducción se ajusta a la edición oficial y no existe prohibición.
La Ley 1801 se publicó en el Diario Oficial 49.949 del 29 de julio de 2016.
[Ley 23 de 1982, art. 41](https://www.cancilleria.gov.co/normograma/compilacion/docs/ley_0023_1982.htm)

Función Pública remite a las reglas de propiedad intelectual en sus
condiciones generales del portal. La consulta del PDF EVA devolvió HTTP 502.
La copia histórica carece de fecha original de descarga acreditada.
Sigue pendiente acreditar autorización específica para redistribuir la
edición PDF y sus elementos editoriales. Las notas quedan fuera del
texto del índice público.
[Condiciones del portal](https://www1.funcionpublica.gov.co/politica-de-privacidad-y-condiciones-de-uso)
· [PDF EVA](https://www.funcionpublica.gov.co/eva/gestornormativo/norma_pdf.php?i=80538)

La entrega actual retira el archivo PDF histórico del árbol publicado.
La copia local se conserva en su ruta original para reproducir la extracción
histórica cuando se disponga del archivo. El historial de Git conserva
la versión anteriormente publicada. El chatbot usa los apartados
cotejados y funciona con el corpus y el índice públicos existentes.

## 10. Alcance documental y verificaciones pendientes

- El índice público v2 contiene 31 artículos y 127 ventanas. El manifiesto
  registra jerarquía, título, tema, fecha, fuente y apartados. El cotejo
  se aplica por apartado. El expediente distingue captura y revisión.
- El edicto de la Corte confirma los resolutivos de C-223/17 sobre los
  textos originales de los artículos 47 a 75 y el artículo 162. Esos
  textos quedan excluidos del índice público.
  [Edicto de la Corte Constitucional](https://www.corteconstitucional.gov.co/secretaria/edictos/EDICTOS%20OCTUBRE%202017.php)
- El expediente preserva las 159 diferencias y sus insumos. Los 48
  candidatos de formato requieren verificar equivalencia, las 27
  reformas requieren cotejar acto modificatorio y alcance, los 77
  casos asociados a fallos requieren verificar resolutivos y efectos y
  los 7 restantes requieren revisión jurídica individual. La publicación
  de apartados cotejados no resuelve el expediente del artículo entero.

## 11. Alcance académico

El chatbot es un prototipo académico de consulta
informativa sobre la Ley 1801 de 2016.

No reemplaza la consulta de fuentes normativas
actualizadas ni el asesoramiento jurídico profesional.

## 12. Archivos relacionados

- `motor_documental/corpus/Ley_1801_de_2016.pdf` (copia histórica local)
- `motor_documental/corpus/articulos_ley_1801.json`
- `motor_documental/fragmentos/fragmentos_ley_1801.json`
- `motor_documental/extraer_texto.py`
- `motor_documental/generar_fragmentos.py`
- `motor_documental/utilidades_texto.py`
