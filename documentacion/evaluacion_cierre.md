# Evaluación del corpus público entregado

Corpus SHA-256 `3bd9a032cef749c47e1319f29bdf08ad3c02087fffbab00ddcfd63c0f5b7d40c`. FAISS SHA-256 `4b479fd101e854c52c6c12ffcc6488541e64fe01c777e78ad95beb93ab887cc1`. Banco SHA-256 `dbeab26c86e8cebc541e301b673347584214630b447af06343e3c311c20beaa9`. El índice y sus 63 vectores de dimensión 384 se conservaron.

| Medición con 50 preguntas | P@5 | Recall@5 | MRR |
| --- | ---: | ---: | ---: |
| Operativa con enrutamiento | 0,108 | 0,54 | 0,54 |
| Artículo completo, sin enrutamiento | 0,128 | 0,64 | 0,4987 |
| Ventanas con solapamiento, sin enrutamiento | 0,124 | 0,62 | 0,5312 |

En las dos variantes diagnósticas se usaron los mismos artículos públicos, banco, modelo multilingüe, similitud y k. Se eliminaron las repeticiones de artículo del ranking conservando el orden. El modelo trunca 14 de los 28 artículos al codificarlos completos por su límite de 128 tokens. Las ventanas dispuestas con solapamiento muestran mejor MRR y menor Recall@5 en esta muestra. La medición operativa aplica las restricciones documentales. Reprodujo por ID los 27 aciertos y las 23 consultas sin candidatos. [Rankings y métricas](../motor_documental/pruebas/recuperacion_publica_cierre.json)

La última corrida HTTP completa en Node y FastAPI se vincula a las mismas huellas de banco y corpus. Registró 7 completas, 18 parciales, 1 retenida, 23 abstenciones y 1 error. Se rechazaron 26/26 trampas. Las 80 citas públicas coincidieron literalmente con el texto y la fuente visible. Una de ellas llevó un rótulo general al citar el parágrafo 2 del artículo 27. El pasaje guardado de RAG-031 se reprodujo y el rótulo quedó corregido. Se añadió regresión para el parágrafo inexistente y el parágrafo sin numerar. Los conteos HTTP se mantienen como medición del lote observado. [Corrida completa](../motor_documental/pruebas/evaluacion_api_gemini_lotes_sucesivos.json) · [Revisión por ID](../motor_documental/pruebas/auditoria_50_lotes_sucesivos.json) · [Reproducción determinista](../motor_documental/pruebas/auditoria_corpus_cierre.json)

Las 26 consultas con Gemini y HTTP 200, incluida la retenida, tardaron en total entre 0,931 y 71,974 s, con mediana de 8,912 s y p95 de 66,802 s. Doce superaron 10 s. Las latencias individuales se preservan en la corrida. RAG-043 devolvió 502 aparte en 11,735 s después de tres 503 del proveedor. La traza separa recuperación, selección, validación, generación e intentos. En una prueba anterior con cinco reinicios, la disponibilidad de los procesos y las primeras consultas se midieron por separado. Tres de cinco primeras consultas y seis de diez posteriores superaron 10 s, incluidos los errores HTTP. Esa prueba precedió al índice actual. Los datos de arranque y el tiempo de la API representan mediciones distintas. [Traza por etapa](../motor_documental/pruebas/traza_api_gemini_lotes_sucesivos.jsonl) · [Prueba de arranque](../motor_documental/pruebas/latencia_arranques_antes.json)

- **RAG-003.** El último HTTP quedó retenido en la selección. La traza no conserva el contenido original, por lo que falta identificar qué cláusula falló. La regresión determinista del encabezado y primer numeral del artículo 8 sigue pasando.
- **RAG-043.** Queda pendiente observar una generación exitosa bajo la configuración actual. El control anterior omitió medidas y el último error se produjo antes de una respuesta visible.
- **RAG-040 y preguntas amplias.** La fuente solo incluye apartados aprobados. Revisar los apartados adicionales y la adecuación de las referencias antes de ampliar respuestas.
- **Latencia.** Conservar mediciones por intento y separar resultados con proveedor indisponible. La evidencia no acredita el umbral de 10 s.

Para reproducir recuperación y diagnóstico, usa `.venv/Scripts/python.exe -m motor_documental.pruebas.comparar_recuperacion --publicable --salida recuperacion.json`. Para una corrida HTTP futura, arranca el motor y Node según el README y ejecuta `.venv/Scripts/python.exe -m motor_documental.pruebas.evaluar_api --estado-motor http://127.0.0.1:8000/estado --salida evaluacion.json`.
## Actualización con el cotejo de los artículos 222, 223 y 146

Esta medición usó el mismo banco de 50 preguntas y el índice público de
96 vectores de dimensión 384. La sección anterior conserva la medición
de la versión indicada en su encabezado.

| Medida operativa | Base de esta fase | Índice final |
| --- | ---: | ---: |
| Aciertos | 29/50 | 30/50 |
| Precisión@5 | 0,116 | 0,120 |
| Recall@5 | 0,58 | 0,60 |
| MRR | 0,58 | 0,60 |
| Respuestas completas | 22 | 27 |
| Trampas rechazadas | 26/26 | 26/26 |

Las cinco completas nuevas fueron RAG-021, RAG-027, RAG-028, RAG-049 y
RAG-050. Las 22 completas previas conservaron sus pasajes necesarios.
Hubo 20 abstenciones, dos parciales, ninguna retención y un error HTTP.
El error fue RAG-025, con tres respuestas 429 del proveedor y un 502
público. Las 29 consultas generadas con HTTP 200 tuvieron p95 de 3,034 s,
máximo de 5,009 s y ningún exceso de 10 s. Los resultados de disponibilidad
o latencia de esta corrida no cierran el requisito sostenido.

El [JSON de evaluación](../motor_documental/pruebas/evaluacion_api_gemini_cotejo_final.json)
conserva las respuestas originales del barrido. El
[comparativo de los 50 IDs](../motor_documental/pruebas/comparacion_50_cotejo_final.json)
registra cambios, citas, fuentes y latencias. Las 221 citas se comprobaron
en el texto literal y la fuente visible. La
[matriz de revisión](revision_entrega.md#cotejo-de-procedimientos-y-transporte)
recoge las decisiones, las fuentes y los pendientes de validación jurídica.
## Evaluación de la fase del chat real

El índice público final tiene 117 vectores de dimensión 384. Los aciertos
pasaron de 30/50 a 32/50, con P@5 de 0,128, Recall@5 de 0,64 y MRR de
0,64. Se obtuvieron 29 completas (+2), tres parciales, 18 abstenciones,
cero retenidas y cero errores HTTP. Se rechazaron las 26 trampas.
RAG-004 y RAG-026 aportaron las nuevas completas. RAG-005 y RAG-032
dejaron de abstenerse, pero sus referencias dicen tipo 3 y el texto
cotejado del artículo 33 dice tipo 4, por lo que figuran como parciales.

RAG-025 recuperó HTTP 200 con el alcance anterior. El 502 de la línea
base fue posterior a tres 429 del proveedor. La [evaluación](../motor_documental/pruebas/evaluacion_api_gemini_chat_final.json)
y su [traza](../motor_documental/pruebas/traza_api_gemini_chat_final.jsonl)
registraron cuatro excesos de 10 s, con máximo de 18,082 s. Dos fueron
intentos únicos exitosos y dos incluyeron un reintento.
El [comparativo de los 50 IDs](../motor_documental/pruebas/comparacion_50_chat_final.json)
incluye 271 citas corroboradas en el texto y en fuentes visibles.
La [matriz](revision_entrega.md#chat-real-y-cotejo-de-conductas-competencias-y-ruido)
incluye el control del navegador y los límites documentales.
## Evaluación local de la revisión por hitos

El índice evaluado tiene 31 artículos, 127 vectores de dimensión 384 y
huella de corpus `e1095acca700aa3c8d84b62e411c45f32a55c9bdf49ccbb6c46f6132d7459b55`.
La recuperación pasó de 32 a 36 aciertos y las completas de 29 a 32.
Hubo cuatro parciales, 14 abstenciones y ningún error HTTP ni retención.
Las 26 trampas fueron rechazadas. Cuatro consultas superaron 10 s.
Los [resultados por ID](../motor_documental/pruebas/comparacion_50_hitos_publicacion.json)
y los [hitos](hitos_publicacion.md) identifican citas, cobertura y demoras.
## Cierre del plan mínimo funcional v2

Se reevaluó el banco original de 50 preguntas y 26 trampas con el
corpus `e1095acca700aa3c8d84b62e411c45f32a55c9bdf49ccbb6c46f6132d7459b55`
y FAISS de 127 vectores de dimensión 384. No hubo cambio de corpus,
modelo, enrutamiento ni banco. El SHA del análisis lingüístico se
validó sobre su proyección de pares número y texto, que usa una
serialización distinta de la huella del índice.

| Comprobación | Resultado |
| --- | --- |
| Arranque real | Frontend HTTP 200, consulta a Gemini con artículo 5 visible. |
| Corpus | 31 artículos públicos con jerarquía, epígrafe, tema, apartados y evidencia. Sigue pendiente la licencia específica del PDF histórico y las notas editoriales, además de la revisión jurídica de las diferencias documentadas. |
| Análisis | SpaCy reproducible, 6.453 tokens, 1.499 tipos y 61,78 tokens de media por fragmento. |
| Recuperación operativa | 36/50. Precisión@5 0,144, Recall@5 0,72 y MRR 0,72. |
| Comparación controlada sin enrutamiento | Artículo completo: P@5 0,140, Recall@5 0,70, MRR 0,6054. Ventanas solapadas: P@5 0,140, Recall@5 0,70, MRR 0,5948. |
| Interfaz y PDF | Chrome verificó consultas, citas, fuentes, historial y reinicio. POST /upload_pdf/ pasó con indexado falso y huellas del índice y metadatos intactas. |
| Exactitud frente al banco | 30 completas, 4 parciales, 14 abstenciones, 0 retenidas, 2 errores HTTP. Se rechazaron 26/26 trampas. |
| Fidelidad y citas | 316 citas literales, del artículo esperado y verificables en la fuente visible. Se conserva la propuesta versionada de corrección del artículo 33 para las referencias históricas de RAG-005 y RAG-032. |
| Pruebas | Python 117 aprobadas y una omitida. Node 26 aprobadas. |
| Menos de 10 s | **Incumplido**. Seis consultas de 50 alcanzaron o excedieron 10 s, incluida una con error. Mediana de las 34 generaciones HTTP 200: 1,828 s, p95: 44,511 s y máximo: 70,816 s. |

RAG-035 y RAG-037 pasaron de completas a HTTP 502. La traza registró
429/503 en RAG-035 y tres 429 en RAG-037. RAG-051 tardó 70,816 s tras
503 y 504, mientras que RAG-050 tardó 17,306 s con un único intento
exitoso. La recuperación y la validación de esos casos tomaron menos
de 0,04 s cada una. No se identificó un cuello de botella local que
justificara modificar la arquitectura o recortar el tiempo de espera.

[Recuperación](../motor_documental/pruebas/recuperacion_cierre_plan_v2.json)
· [HTTP](../motor_documental/pruebas/evaluacion_cierre_plan_v2.json)
· [Comparación por ID](../motor_documental/pruebas/comparacion_cierre_plan_v2.json)
· [Traza por etapa](../motor_documental/pruebas/traza_cierre_plan_v2.jsonl)
· [Chrome](../motor_documental/pruebas/chat_cierre_plan_v2.json)
· [Informe técnico de dos páginas](../output/pdf/informe_tecnico_final.pdf).
