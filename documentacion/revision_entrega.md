# Revisión del prototipo académico

Rama local `fix/extraccion-pdf-multiplataforma`. Verificación del
18 de noviembre de 2026 en Windows, Python 3.12, Node 26 y FAISS en CPU.
La matriz sigue los cinco requisitos escritos en el encargo. El PDF
definitivo de la consigna y la rúbrica del docente queda pendiente de
incorporar a la revisión. El único PDF localizado en el repositorio
es el texto normativo del grupo.

Regresión en Windows con Python 3.12.10 y Node 26.13.1.
`pip check` pasó. La suite principal de Python aprobó 79 pruebas
y omitió una por falta del permiso de Windows para crear enlaces
simbólicos. El selector documental aprobó 5 pruebas y Node aprobó
25. El contraste se reprodujo byte a byte con la misma descarga.

En la fase de conciliación, la suite principal de Python ejecutó
81 pruebas, con 80 aprobadas y la misma omisión de Windows.
La prueba del corpus verificó cobertura exacta de las 159 diferencias,
reproducción del expediente y ausencia de aprobaciones para el índice.
En esta fase no se midió generación con Gemini ni latencia completa.

En la revisión siguiente, el clasificador aplica las señales externas
específicas incluso cuando la consulta menciona la Ley 1801. Las preguntas
mixtas con esas señales se rechazan como una sola consulta. La salvaguarda
de C-223/17 muestra un aviso para consultas explícitas, excluye los textos
originales del contexto y bloquea citas generadas hacia esos artículos.
Las pruebas de generación usan un cliente simulado y el aviso también
se probó por FastAPI sin credencial.
En Windows se ejecutaron 87 pruebas de Python, con 86 aprobadas y
una omitida por permisos de enlaces simbólicos. Node aprobó 25
pruebas. El expediente original se reprodujo byte a byte. Una
prueba del comando de conciliación con otro insumo generó un
expediente de un solo caso.

| Requisito | Estado | Evidencia, pruebas y resultado | Pendiente |
|---|---|---|---|
| Corpus jurídico | Parcial, con 18 artículos total o parcialmente habilitados | [Selección](../motor_documental/corpus/ampliacion_publicable.json), [cotejo por bloque](../motor_documental/corpus/evidencia_ampliacion.json), [expediente](../motor_documental/corpus/conciliacion_diferencias.json). Se habilitaron 39 bloques adicionales y se conservaron los originales de archivo. | Cerrar diferencias sustantivas, revisar reformas y fallos aplicables a los apartados pendientes y validar tablas y notas editoriales. |
| Análisis lingüístico | Ejecutado sobre el corpus histórico | [Informe](informe_analisis_linguistico.md), [resultados reproducibles](../motor_documental/analisis/resultados_linguisticos.json). spaCy en español procesó 249 artículos, 53.943 tokens y 5.059 tipos. Relación tipo/token 0,0938 y media 216,64. Se generaron entidades, colocaciones PMI, KWIC, glosario y frecuencias. | Validar una muestra etiquetada a mano para estimar la calidad de las entidades y repetir sobre el corpus conciliado. |
| Recuperación y RAG | Medido en el índice público de 33 fragmentos | [Medición pública actual](../motor_documental/pruebas/recuperacion_publica_ampliada.json). El servicio recuperó el artículo esperado en 14 de 50 preguntas y se abstuvo en 36. La Precisión@5 fue 0,056, el Recall@5 0,28 y el MRR 0,28. | Ampliar los apartados revisados y verificar fidelidad de la generación real. |
| Interfaz y API | Verificado en Windows | [README y API](../README.md), [pruebas Node](../backend/tests). Chrome sin ventana verificó pregunta sugerida, pregunta libre, historial de la sesión, reinicio, aviso y panel de fuentes con una respuesta de prueba. CORS devolvió 204 al origen permitido y 403 al no permitido. Las pruebas de carga verificaron PDF válido, inválido y sin texto, y `indexado: false`. | Verificar instalación y suite de PDF en Linux y hacer una prueba de navegador con generación real. El historial del prototipo vive en la conversación abierta. |
| Evaluación y rendimiento | Parcial, sin Gemini | [Banco de 50](../motor_documental/pruebas/banco_evaluacion_50.json), [corrida HTTP actual](../motor_documental/pruebas/evaluacion_api_ampliada.json). Express → FastAPI rechazó 26/26 trampas sin citas. Entre las 50 preguntas hubo 36 abstenciones HTTP 200 y 14 respuestas HTTP 503. Hubo cero respuestas generadas. | Con credencial, calificar exactitud, fidelidad y citas frente al contexto y medir el umbral de 10 s con consultas que invoquen Gemini. |

El [contraste con Jurinfo de la JEP](../motor_documental/corpus/contraste_jep.json)
dio 156 coincidencias normalizadas de los 159 artículos del
expediente. Las diferencias 84, 92 y 242 quedan identificadas por
bloque. Este cotejo textual no cierra la revisión jurídica.

## Banco revisado y selección de candidatos

### Ampliación del alcance público

El servicio consulta 18 artículos, 13 de ellos incorporados por
apartado. Se verificaron **39 bloques** de ampliación contra
Cancillería y Jurinfo. El manifiesto enlaza los actos modificatorios
y fallos consultados cuando corresponden. Las selecciones acotadas
no abarcan la totalidad del artículo.

| Tema | Apartados habilitados | Pendiente de cotejo antes de habilitarlo |
|---|---|---|
| Bases y derechos | Arts. 1, 2, 5, 6, 7, incisos del 3 e introducción y principios 1–14 del 8 según la compilación | Parágrafo del art. 8 y reglas específicas sobre derechos de menores, movilidad, reunión y espacio público |
| Comportamientos | Arts. 24 y 26, cuerpo del 25, introducción y numeral 1 de 77 y 94 | Medidas, demás numerales y reglas sectoriales; ruido, convivencia con animales, urbanismo y establecimientos |
| Multas y comparendo | Dos primeros bloques del cuerpo del 180 y definición del 218 | Cuantías, tipos específicos, descuentos, cobro, requisitos y objeción |
| Autoridades y órdenes | Primer inciso del 150 y cuerpo más numerales 1 y 2 del 206 | Régimen de incumplimiento, comisiones, instancias y otras competencias |
| Procedimiento | Cuerpo y numerales 1–4 del 222 y numerales 1–2 del 223 | Apelación, sanciones y actas del 222, audiencia, recursos, decisión y ejecución del 223, y régimen especial del 223A |

[Selección, límites y fuentes](../motor_documental/corpus/ampliacion_publicable.json) ·
[Cotejo por bloque](../motor_documental/corpus/evidencia_ampliacion.json)

La ampliación usa 33 fragmentos de hasta 100 tokens, más los tokens
especiales, con solapamiento de 20 y vectores normalizados de 384
dimensiones. Se fijó la revisión del modelo y se generó un índice
FAISS público separado del histórico. El texto entregado al generador
es el extracto oficial y la nota de alcance va en un campo separado.
Las reglas de enrutamiento son conservadoras y se abstienen si la
pregunta no coincide con un tema habilitado. Tratándose del artículo
150, el extracto respalda tanto la definición como el carácter verbal
de una orden.

La validación reconoce `[GENERAL n]`. Una prueba con el texto real
del art. 2 mantiene la respuesta que cita su numeral 1 y rechaza la
del numeral 99, también en la forma «artículo 2, numeral 99». La API
oculta la afirmación, fuentes y detalles de la cita rechazada.

Aunque 17 preguntas del banco remiten a un número de artículo presente,
solo 14 recuperaron el artículo esperado. RAG-012 y RAG-015 piden listas
más amplias que los numerales cotejados. RAG-048 plantea una multa ya
impuesta y el alcance habilitado es definitorio. Esas tres preguntas
quedaron sin recuperación. Las otras 33 abstenciones remiten a artículos
fuera del subconjunto. En Windows pasaron 92 pruebas de Python y una
se omitió por permisos de enlaces simbólicos. Node aprobó 25.

```bash
python -m motor_documental.corpus.verificar_ampliacion ley1801-jep.html
python -m motor_documental.indice_publicable
python -m motor_documental.pruebas.comparar_recuperacion --publicable --salida recuperacion_publica.json
```

El caso RAG-011 sobre aglomeraciones complejas se conserva con su
procedencia y texto original en [el archivo histórico](../motor_documental/pruebas/rag_011_historico.json).
El artículo 73 original quedó comprendido en el resolutivo primero
de [C-223/17](https://www.corteconstitucional.gov.co/relatoria/2017/C-223-17.htm).
El [banco activo](../motor_documental/pruebas/banco_evaluacion_50.json)
mantiene 50 preguntas mediante RAG-051. Su referencia es la definición
de convivencia del artículo 5, cotejada el 18 de noviembre de 2026.
Las otras 49 respuestas de referencia conservan su estado de revisión
previo. [Compilación de Cancillería](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm)

La búsqueda combina los artículos completos seleccionados por título
o referencia con hasta `k` fragmentos semánticos adicionales. Reserva
espacio en el ranking para los fragmentos de artículos excluidos y los
ya cubiertos por un artículo completo. Calcula el embedding de la
pregunta una sola vez en esa búsqueda FAISS. La regresión con un índice
en memoria confirmó que recupera los dos fragmentos aptos aun con cuatro
resultados excluidos por delante. El índice histórico en disco y las
capturas de generación previas se conservaron.

## Recuperación documental histórica

Se conservó `paraphrase-multilingual-MiniLM-L12-v2` porque soporta
español, se ejecuta en CPU, coincide con los 384 componentes del
índice FAISS existente y permite comparar unidades con el mismo
modelo. Se comprobó que el índice y sus metadatos coinciden en
cardinalidad, cubren los mismos identificadores que el corpus del
experimento y usan producto interno sobre vectores normalizados.

Las dos estrategias comparables usan el mismo corpus histórico,
modelo, preguntas, vector de consulta y ordenación FAISS. La primera
envía cada artículo completo al codificador. La segunda usa los
fragmentos existentes de hasta 120 tokens con solapamiento aproximado
de 20. El modelo limita la entrada a 128 tokens y 167 de los 249
artículos exceden ese límite. La primera estrategia trunca esos
artículos. Los resultados se deduplican por artículo conservando su
primera aparición. Se calcula la precisión con denominador fijo
`k`, recall respecto a los artículos esperados y MRR sobre el
ranking registrado. El híbrido se mide aparte porque incorpora títulos,
referencias cruzadas, orientación por libro y el índice del art. 135.

| Estrategia | Precisión@5 | Recall@5 | MRR | P50 recuperación | P95 recuperación |
|---|---:|---:|---:|---:|---:|
| Un vector por artículo | 0,168 | 0,84 | 0,6875 | 11,439 ms | 13,673 ms |
| Fragmentos FAISS | 0,172 | 0,86 | 0,7450 | 11,646 ms | 13,873 ms |
| Híbrido del prototipo | 0,180 | 0,90 | 0,7157 | 66,010 ms | 78,127 ms |

Los tiempos excluyen la carga del modelo, Gemini, HTTP y navegador.
La prueba usó cuatro hilos de OpenMP y MKL. El híbrido recuperó un
artículo esperado entre los cinco primeros en 45/50 casos. Falló
dos veces para el art. 180 en preguntas genéricas sobre multas
(RAG-025 y RAG-048), y una vez para cada uno de los arts. 35, 93 y
94 (RAG-033, RAG-037, RAG-038). Conviene evaluar un sinónimo de
búsqueda para la definición de multa y variantes independientes
sobre desobediencia, protocolos de evacuación y condiciones
sanitarias. El MRR más bajo del híbrido frente a fragmentos indica
que conviene medir también cuándo sus candidatos adicionales
desplazan al resultado pertinente.

## Recuperación con el banco revisado

Se ejecutó el mismo comparador con RAG-051 en el banco y con los
artículos bloqueados por C-223/17 excluidos del ranking de las tres
estrategias. Se registraron las métricas para k de 1, 3, 5, 10, 20 y 50,
además de MRR. Las diferencias frente a la corrida histórica reflejan
el cambio de banco y el filtro, además del ajuste del recuperador.

| Estrategia | Precisión@5 | Recall@5 | MRR | Posición del art. 5 para RAG-051 |
|---|---:|---:|---:|---:|
| Un vector por artículo | 0,168 | 0,84 | 0,7012 | 1 |
| Fragmentos FAISS | 0,180 | 0,90 | 0,7623 | 1 |
| Híbrido del prototipo | 0,180 | 0,90 | 0,7177 | 4 |

La [medición nueva](../motor_documental/pruebas/comparacion_recuperacion_banco_revisado.json)
registra los rankings y las huellas del corpus y del banco. Los
[resultados históricos](../motor_documental/pruebas/comparacion_recuperacion_resultados.json)
permanecen separados. La medida se refiere a recuperación documental.
Sigue pendiente revisar la vigencia y el alcance de las referencias
restantes, incluidas las que se basan en disposiciones reformadas,
y evaluar respuestas, citas y latencia completa con Gemini.

## Revisión técnica de respuestas históricas

### Cobertura de la API pública anterior a la ampliación

Solo tres de las 50 preguntas tienen un artículo esperado dentro
del alcance público. Sobre las 50, el híbrido acotado obtuvo
Precisión@5 de 0,012, Recall@5 de 0,06 y MRR de 0,04. Las dos
estrategias semánticas acotadas obtuvieron 0,012, 0,06 y 0,05,
respectivamente. La principal causa de pérdida de cobertura son
las 47 referencias fuera del subconjunto cotejado. Antes de
interpretar estas cifras como calidad de generación, hay que
revisar por separado la cobertura normativa y la fidelidad de
las respuestas sobre la cobertura disponible.

Las 50 capturas del grupo contienen respuesta y contexto de una
versión anterior. El archivo original marca 49 pendientes de
revisión humana y una evaluación preliminar del corpus (RAG-031).
La siguiente muestra se cotejó con las referencias y fragmentos
guardados. Se usa la escala 0–2 de la rúbrica interna del expediente.
Las puntuaciones describen la muestra histórica.

| Caso | Exactitud | Fidelidad | Citas | Observación |
|---|---:|---:|---:|---|
| RAG-001 | 2 | 2 | 2 | El art. 1 respalda el objeto. Los arts. 2 y 7 recuperados respaldan el contexto adicional y los tres numerales citados. |
| RAG-002 | 2 | 2 | 2 | La respuesta recoge los seis objetivos del art. 2 y los enumera en su orden. |
| RAG-003 | 2 | 2 | 1 | El art. 8 recuperado respalda la lista y el parágrafo. Faltan los numerales de los criterios concretos. La mención del parágrafo corresponde al texto histórico de la captura y requiere cotejo con la reforma de 2023. |

Para la revisión del grupo, califica cada respuesta visible con la
[rúbrica interna](../motor_documental/pruebas/rubrica_evaluacion_respuestas.json)
conforme a la referencia y al contexto utilizado. Registra por
separado si la aseveración está respaldada, si la cita identifica la
subdivisión correcta y si la disposición sigue siendo aplicable.
Conserva el texto de la respuesta y la evidencia al corregir una
referencia del banco.

## Reproducción

Sigue la instalación y ejecuta los comandos de pruebas del
[README](../README.md). Para repetir los experimentos sin tocar los
informes del grupo, usa archivos de salida distintos.

```bash
python -m motor_documental.pruebas.comparar_recuperacion --salida comparacion_nueva.json
python -m motor_documental.pruebas.evaluar_api --salida evaluacion_nueva.json
```

Para repetir la verificación visual, abre el servidor Node en
Chrome, envía una pregunta sugerida y otra libre, confirma que
ambas permanezcan en la conversación, abre el panel de fuentes
y usa «Nueva conversación». Sin Gemini, una respuesta de prueba de
`POST /api/chat` con `fuentes_recuperadas` permite verificar el
renderizado. La corrida HTTP de las trampas y el banco se ejecuta
contra los servicios reales.
