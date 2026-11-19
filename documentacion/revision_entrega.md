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

| Requisito | Estado | Evidencia, pruebas y resultado | Pendiente |
|---|---|---|---|
| Corpus jurídico | Parcial | [Contraste y fuentes](documentacion_corpus.md), [JSON segmentado](../motor_documental/corpus/referencia_normativa.json). Corrida sobre 249 artículos, con 90 coincidencias normalizadas y 159 diferencias por revisar. Se identificaron 267 parágrafos, 627 numerales y 88 literales según los encabezados del HTML. Se registró C-223/17 en los 29 textos originales afectados. | Conciliar diferencias y tablas, verificar la vigencia disposición por disposición, revisar licencia específica del material editorial y aprobar la migración del corpus utilizado por el RAG. |
| Análisis lingüístico | Ejecutado sobre el corpus histórico | [Informe](informe_analisis_linguistico.md), [resultados reproducibles](../motor_documental/analisis/resultados_linguisticos.json). spaCy en español procesó 249 artículos, 53.943 tokens y 5.059 tipos. Relación tipo/token 0,0938 y media 216,64. Se generaron entidades, colocaciones PMI, KWIC, glosario y frecuencias. | Validar una muestra etiquetada a mano para estimar la calidad de las entidades y repetir sobre el corpus conciliado. |
| Recuperación y RAG | Recuperación medida, generación actual pendiente | [Comparación FAISS](../motor_documental/pruebas/comparacion_recuperacion_resultados.json), [pruebas de abstención](../tests/test_abstencion_rag.py). Orientación suave por libro en candidatos semánticos y preservación de referencias cruzadas. En HTTP, 13/13 trampas se rechazaron con el clasificador y sin fuentes. | Repetir con corpus conciliado y consultas nuevas. Revisar las respuestas reales y las citas de parágrafo, numeral y literal con una credencial de Gemini. |
| Interfaz y API | Verificado en Windows | [README y API](../README.md), [pruebas Node](../backend/tests). Chrome sin ventana verificó pregunta sugerida, pregunta libre, historial de la sesión, reinicio, aviso y panel de fuentes con una respuesta de prueba. CORS devolvió 204 al origen permitido y 403 al no permitido. Las pruebas de carga verificaron PDF válido, inválido y sin texto, y `indexado: false`. | Verificar instalación y suite de PDF en Linux y hacer una prueba de navegador con generación real. El historial del prototipo vive en la conversación abierta. |
| Evaluación y rendimiento | Parcial | [Banco de 50](../motor_documental/pruebas/banco_evaluacion_50.json), [capturas históricas](../motor_documental/pruebas/evaluacion_respuestas_50.json), [corrida HTTP](../motor_documental/pruebas/evaluacion_api_sin_credencial.json). El recorrido real Express → FastAPI respondió HTTP 503 a las 50 preguntas que requerían generación. El mayor tiempo observado en los 13 rechazos fuera de dominio fue 0,0813 s. | Medir la consulta completa con Gemini para comprobar el límite de 10 s. Evaluar exactitud, fidelidad y citas sobre las respuestas actuales y completar la revisión jurídica del banco y del corpus. |

## Recuperación documental

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

## Revisión técnica de respuestas históricas

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
