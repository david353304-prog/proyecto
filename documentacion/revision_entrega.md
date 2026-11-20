# Revisión del prototipo académico

## Cierre técnico del corpus de 28 artículos

| Requisito | Estado | Evidencia y prueba | Resultado observado | Pendiente y siguiente acción |
| --- | --- | --- | --- | --- |
| Corpus, procedencia y vigencia | Parcial | Reconstrucción independiente del corpus y chequeo de bloques, intervalos, metadatos y huellas. [Auditoría](../motor_documental/pruebas/auditoria_corpus_cierre.json) · [Procedencia](documentacion_corpus.md) | 128 bloques públicos, 63 ventanas, dimensión 384. De 159 diferencias históricas, 48 clasificadas preliminarmente como extracción o formato. Cero diferencias cerradas por equivalencia de espacios. | Cotejo jurídico y edición oficial de los casos pendientes. Acreditar los términos de redistribución del PDF y notas editoriales. |
| Lingüística | Cumplido | Nueva ejecución de spaCy sobre ambos corpus y muestra anotada fija. [Informe](informe_analisis_linguistico.md#análisis-del-corpus-entregado) | Público: 2.975 tokens, 844 tipos y TTR 0,2837. Muestra: 13/15 menciones antes y 15/15 después, sin falsos positivos. | Una muestra independiente y mayor permitiría estimar el rendimiento general de las reglas. |
| RAG y citas | Parcial | Reproducción de rankings y pruebas de corpus, ventanas y cotas de tokenización. Reproducción de RAG-031 con su pasaje registrado y pruebas de parágrafos. [Evaluación](evaluacion_cierre.md) | 27/50 aciertos, 23 sin candidatos. Se corrige el rótulo de parágrafo 2. MRR diagnóstico de ventanas 0,5312 frente a 0,4987 por artículo. | RAG-003 quedó retenida en la última corrida. Su salida original no está disponible para determinar la causa exacta. |
| Interfaz, API y PDF | Cumplido en Windows | Chromium real con respuestas simuladas y suite Node para HTTP, errores, fuentes y PDF. [Interfaz](../motor_documental/pruebas/verificacion_interfaz_cierre.json) · [Contratos](../README.md) | Pasaron siete comprobaciones de navegador. Las tres sugerencias tienen respaldo. Node 26/26, con carga PDF `indexado: false`. | La prueba de Linux queda pendiente. `wsl.exe --list --quiet` informó que WSL no está instalado. |
| Evaluación y rendimiento | Parcial | Revisión por ID, corpus y banco vinculados a la corrida HTTP guardada. [Informe](evaluacion_cierre.md) | 7 completas, 18 parciales, 1 retenida, 23 abstenciones, 1 error y 26/26 trampas. Doce de 26 llamadas con HTTP 200 superaron 10 s. | Verificar RAG-003 y RAG-043 en una corrida dirigida si existe una hipótesis concreta. Validar jurídicamente las referencias. |
| Documentación y reproducción | Cumplido para el entorno probado | Guía, comandos, huellas, evidencias y paquete de cierre. [README](../README.md) | Git, sintaxis y pruebas verificadas. Se reutilizó la corrida de Gemini correspondiente al índice. | Contrastar el cierre con la rúbrica definitiva del docente cuando esté disponible. |

Python en el entorno del proyecto: 104 aprobadas y 1 omitida por permisos de enlaces simbólicos de Windows. Node: 26 aprobadas. El cambio de RAG-031 afecta a la presentación de la cita y conserva el texto literal, la recuperación y el índice.

Se verificó la instalación de `requirements.txt` en un entorno temporal nuevo con Python 3.12.10. `pip check` pasó, se cargó `es_core_news_sm` 3.8.0 y la suite volvió a registrar 104 aprobadas y 1 omitida. También se instaló el backend con `npm ci --offline --no-audit --no-fund` en un directorio temporal usando Node 26.13.1 y el lockfile del repositorio. La verificación pendiente en Linux consiste en instalar ambos manifiestos y ejecutar `.venv/bin/python -m unittest discover -s tests` y `npm --prefix backend test` desde la raíz.

## Cobertura en tres lotes sucesivos

La línea base de movilidad reproducía 25 artículos, 47 fragmentos y 20 aciertos en el banco de 50. La [revisión por ID](../motor_documental/pruebas/auditoria_50_lotes_sucesivos.json) registra apartados, referencias originales, selección y pendientes. Se mantuvo separado el expediente histórico de 159 diferencias.

| Lote | Selección y decisión documental | IDs recuperados adicionales |
| --- | --- | --- |
| Órdenes y convivencia | Artículo 27, fila del numeral 1 y mediación del parágrafo 2, contrastadas con Decreto 555 y Ley 2197. Artículo 36, inciso y parágrafo sobre acompañamiento. Artículo 150, inciso segundo, con la decisión de C-391/17 sobre el plazo. Se reconoció «sin contar con la licencia» en el alcance ya aprobado del artículo 135. | RAG-007, RAG-031, RAG-042 |
| Protección | Artículo 39, inciso y numeral 1. C-281/17 se inhibió sobre ese numeral y condicionó el parágrafo 3, excluido. Artículo 124, numerales 1 y 7 y sus filas. La Ley 2054 y C-048/20 afectan otros apartados excluidos. | RAG-009, RAG-041 |
| Posesión y salud pública | Artículo 77, numerales 1 a 5 y filas. T-391/22 y T-533/24 delimitan casos y procedimiento ajenos al alcance del extracto. Artículo 94, numerales 1 a 9 y filas del primer parágrafo, con contraste de Cancillería, Jurinfo y el PDF oficial consultado. | RAG-012, RAG-015 |

Las capturas base son del 18 de noviembre de 2026 y la consulta normativa y revisión de este lote se registraron el 19. El [manifiesto de selección](../motor_documental/corpus/ampliacion_publicable.json) identifica los apartados, las URLs y la fecha. La [evidencia por bloque](../motor_documental/corpus/evidencia_ampliacion.json) registra la posición, la huella y el contraste con la captura de Jurinfo. El alcance es documental.

| Recuperación pública | Artículos / fragmentos | Aciertos / sin candidatos | Precisión@5 | Recall@5 | MRR |
| --- | ---: | ---: | ---: | ---: | ---: |
| Movilidad, línea base | 25 / 47 | 20 / 30 | 0,080 | 0,40 | 0,40 |
| Órdenes | 26 / 52 | 23 / 27 | 0,092 | 0,46 | 0,46 |
| Protección | 28 / 56 | 25 / 25 | 0,100 | 0,50 | 0,50 |
| Convivencia | 28 / 63 | 27 / 23 | 0,108 | 0,54 | 0,54 |

El banco y los artículos esperados conservaron la misma huella. Cada lote se volvió a medir y se registraron los cambios de ranking en los 50 IDs. El FAISS público final tiene dimensión 384, SHA-256 `4b479fd101e854c52c6c12ffcc6488541e64fe01c777e78ad95beb93ab887cc1` y corpus SHA-256 `3bd9a032cef749c47e1319f29bdf08ad3c02087fffbab00ddcfd63c0f5b7d40c`. [Comparación por ID](../motor_documental/pruebas/comparacion_recuperacion_lotes_sucesivos.json)

En el [control diagnóstico real de RAG-044](../motor_documental/pruebas/diagnostico_rag044_lotes.json), Gemini terminó con `STOP` y entregó siete objetos bien formados. Los siete fallaron el cotejo literal. Sus longitudes son compatibles con haber añadido medidas a las conductas. La traza conserva la huella y las longitudes de la salida, y el control directo tardó 107,598 s. El prompt ahora pide un objeto separado por cada fila de medidas. La regresión cubre la fila breve y literal del numeral 11 del artículo 146, numerales inventados y la unión de una conducta con una medida de otra parte del contexto. En el control anterior de RAG-043 las filas estaban en contexto y Gemini omitió seleccionarlas.

Para los 23 casos sin candidatos, el siguiente cotejo se concentra en los pares que comparten artículo. En el 33 queda pendiente integrar la Ley 2450 con el condicionamiento de C-308/19. En el 163 falta representar las garantías de C-212/17 junto con el texto reformado, y en el 155 las de C-281/17 con la Ley 2197. Los arts. 92 y 95 requieren cotejar sus remisiones y distinguir las reglas sectoriales. En el 124 quedan fuera los numerales sujetos a terminología actualizada o interpretación judicial y en 135, 140 y 146 los inventarios amplios. Los plazos de 223A y las restricciones de acceso a datos de 237 siguen pendientes. El inventario por ID conserva también las brechas de los casos cuya respuesta puede ser parcial aun con recuperación correcta.

El parágrafo 7 del art. 92 remite al 87 y el numeral 1 del art. 95 remite al art. 106 de la Ley 1453. El generador actual reconoce referencias a otros artículos también dentro de la cita literal y las contrasta con los artículos recuperados de la Ley 1801. Queda pendiente distinguir en el validador las remisiones internas de una atribución hecha por el modelo, además de verificar los requisitos y las medidas concretas. La C-094/20 fue inhibitoria respecto del numeral 8 del art. 95 y no resolvió el numeral 1. [Compilación de Cancillería, art. 92](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#92) · [Art. 95](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#95) · [C-094/20](https://www.corteconstitucional.gov.co/relatoria/2020/C-094-20.htm)

### Evaluación HTTP

| Resultado frente al banco | Últimas observaciones por ID antes de los lotes | Corrida final |
| --- | ---: | ---: |
| Completas | 3 | 7 |
| Parciales | 15 | 18 |
| Retenidas | 1 | 1 |
| Abstenciones | 30 | 23 |
| Errores HTTP | 1 | 1 |

La columna anterior combina la última corrida completa de 23 artículos con los controles del lote de movilidad. La nueva corrida es una sola evaluación HTTP de 50 preguntas y 26 trampas. Se rechazaron las 26 trampas y 49 preguntas del banco respondieron HTTP 200. La revisión técnica cotejó los elementos de referencia, el texto literal y los rótulos. Las 80 citas visibles coincidieron con el corpus y la fuente mostrada y señalaron el artículo esperado. La cita de mediación de RAG-031 incluyó el texto del parágrafo 2, pero el rótulo visible solo identificó el artículo 27. [Resultado HTTP](../motor_documental/pruebas/evaluacion_api_gemini_lotes_sucesivos.json) · [Evaluación por ID](../motor_documental/pruebas/auditoria_50_lotes_sucesivos.json)

RAG-044 pasó de retenida a completa frente al banco, con siete conductas y siete filas de medidas separadas, en 6,327 s. RAG-043 devolvió 502 en 11,735 s tras tres HTTP 503 del proveedor. Su control previo sigue siendo la evidencia de que Gemini llegó a citar las conductas sin seleccionar las medidas. RAG-003 quedó retenida en la selección extractiva en 1,232 s. [Traza por intento](../motor_documental/pruebas/traza_api_gemini_lotes_sucesivos.jsonl)

De las 26 consultas con llamada confirmada y HTTP 200, incluida la retenida, 14 quedaron por debajo de 10 s y 12 superaron el umbral. Mínimo 0,931 s, mediana 8,912 s, p95 66,802 s y máximo 71,974 s. El error HTTP de RAG-043 queda fuera de esos percentiles y también superó 10 s. La traza registra cinco respuestas 503 y dos 504 del proveedor, incluidas las recuperadas por reintento. La medición fue secuencial.

Python: 101 aprobadas y 1 omitida por permisos de enlaces simbólicos en Windows. Node: 26 aprobadas. La suite comprobó que las 63 ventanas cubren el texto aprobado, conservan solapamiento y límites de palabra, respetan el límite del tokenizador y excluyen apartados no aprobados. La huella de metadatos públicos es `7338700c61d34315f4a013e54d8671126418a751636df9a454b05f67dbef235e`.

### Reproducción

```powershell
$py = ".venv/Scripts/python.exe"
& $py -m motor_documental.corpus.verificar_ampliacion ruta-a-la-captura-jurinfo.html
& $py -m motor_documental.indice_publicable
& $py -m motor_documental.pruebas.comparar_recuperacion --publicable --salida recuperacion.json
& $py -m unittest discover -s tests
npm.cmd --prefix backend test
```

Para medir HTTP, arranca FastAPI y Express con la configuración local del README. Usa `python -m motor_documental.pruebas.evaluar_api --estado-motor http://127.0.0.1:8000/estado --salida evaluacion.json`. Para reproducir los lotes en una copia de trabajo aislada, usa la selección de cada lote y repite el cotejo, la generación del índice y la recuperación. Las cuatro selecciones reconstruidas se verificaron contra las huellas de los informes. [Selecciones por lote](../motor_documental/pruebas/selecciones_lotes_sucesivos.json)

## Lote de espacio público y transporte

Se revisaron las 32 consultas sin candidatos en la corrida anterior. La dificultad refleja si el banco pide una conducta delimitada, tablas de medidas o la interpretación conjunta de reformas y decisiones judiciales. [Auditoría por ID](../motor_documental/pruebas/auditoria_abstenciones_lote_movilidad.json)

| Artículo | Preguntas y apartados necesarios | Cotejo pendiente o decisión | Dificultad |
| --- | --- | --- | --- |
| 124 | RAG-018: numerales 1–9 y cuadro. RAG-041: numerales 1 y 7 y sus medidas. | Contrastar terminología de manejo especial y reformas de protección animal, incluidas las referencias del capítulo a la Ley 2054. | Media |
| 135 | RAG-019: literales y cuadro en conjunto. RAG-042: literal A n. 4, parágrafos 1 y 2 y sus condiciones. | Decreto 555 art. 10 y alcance de T-535/24. Los plazos y condiciones siguen fuera. | Alta |
| 140 | RAG-020: numerales 1–14 y condicionamientos. RAG-043: numerales 3 y 5 y filas del parágrafo 2. | Se incorporó el alcance de RAG-043. Para RAG-020 siguen pendientes Ley 2000 de 2019, C-211/17, C-253/19 y C-127/23. | Media para 043, alta para 020 |
| 146 | RAG-021: numerales 1–16, incluido el contenido asociado al 10, y cuadro completo. RAG-044: numerales 5, 7, 8, 9, 11, 12 y 16 y sus filas. | Se incorporó el alcance de RAG-044. C-094/20 examinó el primer inciso del parágrafo 2 sobre cámaras, excluido. | Media |
| 155 | RAG-023 y RAG-046: inciso inicial, literales del traslado, excepciones de mediación, plazo y garantías. | Contrastar la reforma de Ley 2197/22 y C-281/17 con el texto aplicable, incluido el alcance de los condicionamientos. | Alta |
| 163 | RAG-024: inciso general, siete causales y parágrafos. RAG-047: inciso, numeral 1 e informe del parágrafo 1. | Pendiente integrar C-212/17, cosa juzgada en C-334/17 y la adición posterior de la causal de maltrato animal. | Alta |
| 33 | RAG-005: numeral 1 y medidas. RAG-032: numeral 1 literal a y medidas pertinentes. | Ley 2450 art. 18, C-308/19 y alcance de C-253/19 en el numeral 2. | Alta |
| 35 | RAG-006: lista completa. RAG-033: numerales 1 y 2. | El numeral 2 ya está cotejado con C-600/19. Pendiente delimitar el numeral 1 tras el fallo inhibitorio C-223/25. | Alta |
| 38 | RAG-008: enumeración y literales. RAG-034: acceso, material inapropiado, sustancias y conductas de riesgo. | Verificar cada remisión, reforma y nota jurisprudencial del bloque sobre protección de menores. | Alta |
| 92 | RAG-013: enumeración y cuadro. RAG-036: numeral 16 y parágrafo 7 con remisión al 87. | Decreto 555 art. 8 y relación de la remisión con C-054/19. | Alta |
| 95 | RAG-016: numeral 1 y fila. RAG-039: numeral 1, parágrafo 2 y fila. | Pendiente verificar redacción, remisiones a bases de datos y reglas de registro. | Alta |

### Lote cotejado

| Selección pública | Captura, consulta y revisión | Alcance documental |
| --- | --- | --- |
| Art. 140, numerales 3 y 5 y filas correspondientes del parágrafo 2 | Capturas Cancillería/Jurinfo del 18 de noviembre de 2026. Consulta y revisión del 19. El art. 11 del Decreto 555 de 2017 permite verificar la redacción de las conductas y la corrección de la fila 3. [Cancillería](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#140) · [Decreto 555](https://www.alcaldiabogota.gov.co/sisjur/normas/Norma1.jsp?i=68690) | Apartados cotejados. Quedan fuera ocupación, sustancias y las restantes medidas. |
| Art. 146, numerales 5, 7, 8, 9, 11, 12 y 16 y filas correspondientes del parágrafo 1 | Capturas Cancillería/Jurinfo del 18 de noviembre. Consulta y revisión del 19. Se contrastaron numerales y filas con la compilación oficial y se delimitó C-094/20 al inciso examinado del parágrafo 2. [Cancillería](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#146) · [C-094/20](https://www.corteconstitucional.gov.co/relatoria/2020/C-094-20.htm) | Apartados cotejados. Quedan fuera las demás conductas, filas y parágrafos. |

Las referencias de reforma y jurisprudencia se guardan como procedencia. El texto indexado para responder proviene de la Ley 1801. [Cotejo y huellas por bloque](../motor_documental/corpus/evidencia_ampliacion.json)

Sobre los mismos 50 IDs, solo cambiaron RAG-043 y RAG-044. Con 25 artículos y 47 fragmentos, el índice público obtuvo **20 aciertos y 30 consultas sin candidatos**, frente a 18 y 32. Precisión@5 pasó de 0,072 a 0,080, Recall@5 de 0,36 a 0,40 y MRR de 0,36 a 0,40. [Rankings](../motor_documental/pruebas/recuperacion_publica_lote_movilidad.json) · [Comparación por ID](../motor_documental/pruebas/comparacion_recuperacion_lote_movilidad.json)

Las 47 ventanas se verificaron con el tokenizador del modelo. Cubren el texto aprobado completo y conservan el solapamiento y los límites de palabra. Las pruebas excluyen expresamente el numeral 7 del artículo 140 y el parágrafo 2 del 146. El cotejo total de ampliación registra 70 bloques.

| SHA-256 | Antes | Después |
| --- | --- | --- |
| Corpus público | `a2b92ae92020791edb8c31005a375bd2744ed3e1d41fac76c46f9235a3be60e6` | `f7e45f8839a96721dde450c1d8076c88d355d0c02bcb49f4a83becbef16f0a3a` |
| FAISS público | `6ce9bcb79bae46b38b732c5af633d247270b94be705353f97ecc202ab4815cb1` | `084c04fe2fa2dbe33e80c6f9d272f467934fd05220f6e43e4a2a162d81c636c8` |
| Metadatos públicos | `4c0b74b64014100243965f7ae4854f072e7ff085917560b6cae098a3a9665429` | `b5bc3f4274eb9bafcede9197fe085777ac32c20195de8772bd1a27bdb7ec1b0d` |

| Control inicial | HTTP | Tiempo | Evaluación frente al banco |
| --- | ---: | ---: | --- |
| RAG-020 | 200 | 0,251 s | Abstención esperada por inventario general. |
| RAG-021 | 200 | 0,027 s | Abstención esperada por inventario general. |
| RAG-043 | 200 | 7,271 s | Parcial. Citó literalmente las dos conductas y omitió las medidas, aunque estaban en el contexto. |
| RAG-044 | 200 | 68,405 s | Respuesta retenida en revisión documental, sin citas públicas. |

Las 26 trampas se rechazaron sin fuentes. El fallo de RAG-044 detuvo la primera evaluación completa. [Control inicial](../motor_documental/pruebas/control_api_gemini_lote_movilidad.json)

La repetición diagnóstica de RAG-044 recuperó el artículo 146 en 0,066 s. El intento del SDK tomó 6,111 s, la generación 6,193 s y el HTTP total 6,408 s. La selección extractiva volvió a rechazarse antes de la validación de citas y se devolvió `REQUIERE_REVISION` sin fuentes. La traza identifica la etapa del rechazo. Falta distinguir si la selección incumplió el formato, el límite o la literalidad. La corrida completa queda pendiente porque el control volvió a fallar. [Segundo control](../motor_documental/pruebas/control_api_gemini_lote_movilidad_reintento.json) · [Traza](../motor_documental/pruebas/traza_lote_movilidad.jsonl)

Python: 100 aprobadas y 1 omitida por permisos de enlaces simbólicos en Windows. Node: 26 aprobadas.

## Procedencia y límites de las ventanas públicas

Las huellas de las copias HTML de Cancillería y Jurinfo coinciden con las capturas documentadas el **18 de noviembre de 2026**. El **19 de noviembre** corresponde a la revisión de los apartados 93.1, 111.1 y 111.3. La evidencia de ampliación y el manifiesto separan la procedencia de las capturas de la revisión de esos apartados. El [registro de procedencia](documentacion_corpus.md#fecha-de-captura-y-fecha-de-revisión) distingue también las fuentes complementarias para las que no existe una descarga fechada con huella.

El índice anterior tenía seis límites de ventana que no coincidían con palabras completas, en los artículos 2, 6, 7, 111, 206 y 222. Se alinearon los límites a espacios y se añadieron intervalos en el texto aprobado. Se comprobaron las 40 ventanas de 23 artículos, desde el primer hasta el último carácter de cada texto, con 17 solapamientos de 20 a 22 tokens y un máximo de 102 tokens con especiales frente al límite de 128. El segundo fragmento del artículo 111 empieza por «Arrojar». El tercer fragmento del 222 empieza por «convivencia.». Cada ventana es una porción literal de los apartados aprobados y el índice conserva las exclusiones.

| Huella SHA-256 | Valor |
| --- | --- |
| Corpus público, igual a la corrida de 23 artículos | `a2b92ae92020791edb8c31005a375bd2744ed3e1d41fac76c46f9235a3be60e6` |
| FAISS público anterior | `fd3053e26db17c4d00aa62448f34c6e82d717bbc8230841bf760d1187f87f6de` |
| FAISS público regenerado | `6ce9bcb79bae46b38b732c5af633d247270b94be705353f97ecc202ab4815cb1` |
| Metadatos públicos regenerados | `4c0b74b64014100243965f7ae4854f072e7ff085917560b6cae098a3a9665429` |

La recuperación operativa quedó idéntica en los 50 IDs: 18 aciertos, 32 sin candidatos, Precisión@5 de 0,072, Recall@5 de 0,36 y MRR de 0,36. El diagnóstico por fragmentos sin enrutamiento conservó P@5 de 0,10, Recall@5 de 0,50 y MRR de 0,4022. [Corrida](../motor_documental/pruebas/recuperacion_publica_limites.json) · [Comparación exacta por ID](../motor_documental/pruebas/comparacion_recuperacion_limites.json)

| Control dirigido | HTTP | Citas literales en fuente visible | Tiempo HTTP |
| --- | ---: | --- | ---: |
| RAG-002 | 200 | Art. 2, numerales 1 a 6 | 13,110 s |
| RAG-017 | 200 | Art. 111, numeral 1 | 10,305 s |
| RAG-037 | 200 | Art. 93, numeral 1 | 18,062 s |
| RAG-040 | 200 | Art. 111, numerales 1 y 3 | 3,005 s |

Las 26 trampas se rechazaron sin fuentes. Los controles ejecutaron el FAISS regenerado y confirmaron las diez citas. Tres controles generativos superaron 10 s. Se omitió una corrida completa adicional porque los rankings por ID y el texto normativo que recibe Gemini permanecen idénticos, y los controles confirmaron las fuentes de los apartados afectados. Los resultados HTTP completos anteriores se conservan como evidencia histórica. [Controles nuevos](../motor_documental/pruebas/control_api_gemini_limites.json)

Python: 99 aprobadas y 1 omitida por permisos de enlaces simbólicos en Windows. Node: 26 aprobadas. Solo se regeneró el índice público.

## Auditoría por ID y controles dirigidos

Se compararon las mismas 50 preguntas y rankings operativos de 21 y 23 artículos. El banco conserva su huella. Los otros 46 textos visibles son idénticos. RAG-002 explica por sí sola la disminución de 4 a 3 respuestas completas. Los tres nuevos aciertos entregaron respuestas. El error ocurrió en RAG-002, cuyo artículo ya se recuperaba en ambas versiones. [Comparación de los 50 IDs](../motor_documental/pruebas/comparacion_regresion_cobertura.json)

| ID | Causa comprobada y evidencia | Estado del control dirigido |
| --- | --- | --- |
| RAG-002 | El ranking mantuvo el artículo 2 y sus tres fragmentos son idénticos en los manifiestos. La fuente pública anterior coincide con el registro actual. El contexto reconstruido coincide con la huella del control, pero la solicitud histórica a Gemini no se capturó. Node recibió HTTP 500 de FastAPI y devolvió 502. El último log histórico fue la preparación del contexto, antes de obtener respuesta generativa o validar citas. | HTTP 200, los seis numerales, 11,979 s. El 502 no se reprodujo. Sigue sin conocerse la excepción o código que causó el 500 histórico. |
| RAG-017 | Acierto nuevo, artículo 111 numeral 1. Cita la conducta sobre horarios. La revisión frente al banco es parcial porque su referencia incluye la medida correctiva, excluida del contexto. | HTTP 200, cita literal, 1,298 s. |
| RAG-037 | Acierto nuevo, artículo 93 numeral 1. Cita el deber de informar sobre evacuación. La referencia también incluye la medida correctiva, excluida del contexto. | HTTP 200, cita literal, 2,302 s. |
| RAG-040 | Acierto nuevo, artículo 111 numerales 1 y 3. Cita el horario y la disposición en lugares públicos no autorizados. La referencia espera numeral 8 y medidas, fuera de la selección. | HTTP 200, ambas citas literales, 1,658 s. |

El artículo 21 de la Ley 2450 de 2025 añadió el numeral 15, modificó el parágrafo 2 y añadió reglas sobre ruido en parágrafos del artículo 93. El artículo 22 modificó la fila del numeral 3 del cuadro del parágrafo 2. El corpus público conserva exclusivamente el numeral 1 sobre protocolos de seguridad y evacuación. Las demás conductas, los parágrafos y el cuadro de medidas permanecen fuera de la selección. El cotejo de los controles confirmó los numerales públicos del artículo 111 con su fuente literal. [Art. 93 en Cancillería](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#93) · [Arts. 21 y 22 en Jurinfo](https://jurinfo.jep.gov.co/Normograma/compilacion/docs/ley_2450_2025.htm) · [Art. 111 en Cancillería](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#111)

### Rendimiento observado por etapa

| ID | Recuperación (s) | Intento SDK (s) | Generación total (s) | Validación (s) | HTTP total (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| RAG-002 | 0,098 | 11,391 | 11,531 | 0,015 | 11,979 |
| RAG-017 | 0,078 | 1,195 | 1,200 | 0,001 | 1,298 |
| RAG-037 | 0,053 | 2,223 | 2,228 | 0,001 | 2,302 |
| RAG-040 | 0,050 | 1,569 | 1,574 | 0,001 | 1,658 |

El intento SDK es parte de la generación total. Los cuatro controles terminaron con un intento exitoso por ID. Las 26 trampas devolvieron HTTP 200, `FUERA_DE_DOMINIO`, sin fuentes ni intentos de generación. El control se ejecutó en 3698/8698 y no constituye una nueva evaluación completa. En la última corrida completa, 7 de 17 generaciones quedaron por debajo de 10 s. [Resultados dirigidos](../motor_documental/pruebas/control_regresion_cobertura.json) · [Traza sin solicitudes ni cabeceras](../motor_documental/pruebas/traza_regresion_cobertura.jsonl)

El trazador de pruebas identifica timeout, errores de transporte, HTTP del proveedor, HTTP 429 compatible con límite o cuota y excepciones de datos. Registra separadamente si se aceptaron las citas y el estado de validación documental. Se probaron las categorías mediante cuatro excepciones simuladas y se comprobó que el mensaje se omite de la traza. Los controles reales carecen de excepciones y por ello no permiten atribuir el 502 histórico a una categoría. Se mantuvo el manejo seguro de errores, los tiempos de espera y los reintentos de producción.

Python: 98 aprobadas y 1 omitida por permisos de enlaces simbólicos en Windows. Node: 26 aprobadas. El corpus, los índices y las corridas anteriores quedaron intactos.

## Ampliación de cobertura y diagnóstico de Gemini

Las 35 abstenciones de la [línea base HTTP](../motor_documental/pruebas/evaluacion_api_gemini_enumeraciones_ajustadas.json) se clasificaron por pregunta. En 27 faltaba el artículo esperado, 7 excedían el apartado aprobado y RAG-031 quedó sin candidatos por su formulación coloquial. En los 35 casos el selector devolvió un conjunto vacío, por lo que no se confirmó un fallo de FAISS. [Auditoría](../motor_documental/pruebas/auditoria_35_abstenciones.json)

| Apartados | Cotejo del 19 de noviembre de 2026 y decisión |
| --- | --- |
| Art. 93 n. 1 | Protocolos de evacuación. Concordancia con Cancillería y con la captura Jurinfo del 18 de noviembre. Los arts. 21 y 22 de la Ley 2450 de 2025 modifican otros apartados. No se halló modificación directa ni fallo sobre el numeral seleccionado en las fuentes consultadas. Se mantuvieron excluidas las medidas y la pregunta general RAG-014. [Cancillería](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#93) · [Texto de la reforma](https://jurinfo.jep.gov.co/Normograma/compilacion/docs/ley_2450_2025.htm) |
| Art. 111 nn. 1 y 3 | Horarios de disposición y residuos en sitios públicos no autorizados. Coincidencia exacta normalizada con la captura Jurinfo. No se halló modificación directa ni fallo sobre esos numerales en las fuentes consultadas. La nota editorial relaciona el numeral 3 con el 8. Se conserva la redacción literal del numeral 3 y se dejan fuera la aplicación de medidas y la distinción entre ambas consecuencias. [Cancillería](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#111) · [Notas del PDF oficial](https://cancilleria.gov.co/sites/default/files/Normograma/docs/pdf/ley_1801_2016.pdf) |

El estado de los tres bloques es `apartados_cotejados`. Quedan pendientes, entre otros, el ruido del artículo 33 (RAG-005 y RAG-032) por verificar juntos la reforma de la Ley 2450 y los efectos de C-308/19 sobre la disposición original. Para los pares de preguntas sobre los artículos 38, 92, 95, 124, 140, 146, 155 y 163 falta aprobar sus apartados concretos. [Selección y huellas por bloque](../motor_documental/corpus/evidencia_ampliacion.json)

| Recuperación operativa sobre las mismas 50 preguntas | Antes | Ahora |
| --- | ---: | ---: |
| Artículos / fragmentos públicos | 21 / 37 | 23 / 40 |
| Preguntas cuyo artículo esperado existe total o parcialmente | 23 | 27 |
| Preguntas con acierto / sin candidatos | 15 / 35 | 18 / 32 |
| Precisión@5 | 0,060 | 0,072 |
| Recall@5 | 0,30 | 0,36 |
| MRR | 0,30 | 0,36 |

La recuperación adicional corresponde a RAG-017, RAG-037 y RAG-040. Se regeneró solo FAISS público. [Rankings nuevos](../motor_documental/pruebas/recuperacion_publica_cobertura.json)

| Corrida HTTP de 50 preguntas y 26 trampas | Antes | Ahora |
| --- | ---: | ---: |
| HTTP 200 del banco / trampas rechazadas sin fuentes | 50 / 26 | 49 / 26 |
| Respuestas completas / parciales frente a la referencia | 4 / 11 | 3 / 14 |
| Abstenciones documentales / errores HTTP | 35 / 0 | 32 / 1 |
| Citas literales, artículo esperado y rótulo concordante | 46/46 | 44/44 |
| Generaciones entregadas en menos de 10 s | 15/15 | 7/17 |
| Mediana / p95 / máximo de generaciones entregadas | 2,013 / 6,174 / 9,437 s | 10,385 / 20,059 / 23,559 s |

La revisión técnica conserva la clasificación anterior de los textos idénticos. RAG-017 y RAG-037 cubrieron la conducta y dejaron fuera la medida que espera el banco. RAG-040 citó los numerales 1 y 3 del artículo 111. La referencia espera los numerales 1 y 8 y las medidas, así que se calificó parcial. RAG-002 quedó como error HTTP en la corrida completa. Las dos repeticiones separadas de RAG-002 devolvieron HTTP 200 y seis numerales. Estas repeticiones permanecen fuera de la tabla. [Corrida HTTP](../motor_documental/pruebas/evaluacion_api_gemini_cobertura.json) · [Cotejo por consulta](../motor_documental/pruebas/verificacion_gemini_cobertura.json)

El HTTP 502 de RAG-002, en 72,131 s, fue la respuesta de Node al HTTP 500 del motor. El último registro del motor correspondió al contexto preparado y el primer trazador omitió los intentos del SDK. Los tres 502 de la [prueba de arranque anterior](../motor_documental/pruebas/latencia_arranques_antes.json) también quedaron después de preparar el contexto, a los 68,218 s, 25,692 s y 78,071 s. Los registros de esas cuatro solicitudes no permiten asignar una excepción del proveedor o un reintento concreto.

El trazador de diagnóstico se movió al límite de cada intento del SDK. En cinco controles registró un intento aceptado por consulta, de 4,779 a 13,986 s, y ningún fallo. Registra duración, tipo de excepción y código del SDK si está disponible. Los cinco controles no reprodujeron el 502. Se conservan la traza de la corrida completa y la de los controles. No se cambiaron los tiempos de espera ni la política de reintentos de producción. [Traza de la corrida](../motor_documental/pruebas/intentos_gemini_cobertura.jsonl) · [Controles HTTP](../motor_documental/pruebas/control_sdk_gemini_cobertura.json) · [Traza por intento](../motor_documental/pruebas/intentos_sdk_gemini_cobertura.jsonl)

Python: 98 aprobadas y 1 omitida por permisos de enlaces simbólicos en Windows. Selector documental: 5 aprobadas. Node: 26 aprobadas.

## Matriz anterior a la ampliación de los artículos 93 y 111

Rama local `fix/extraccion-pdf-multiplataforma`, base `263e554cbc38a3f4249e3a4f9293c4645b7b1244`. El PDF definitivo de la consigna no apareció en el repositorio. La evaluación usa los requisitos escritos. La línea base local ya incluía la auditoría de urbanismo y Gemini, con cambios sin commit y sus capturas. Antes de editar pasaron 93 pruebas Python de 94 ejecutadas y las 26 de Node.

| Requisito y peso | Estado actual y evidencia | Pendiente |
| --- | --- | --- |
| Corpus · 20 % | 21 artículos con alcance público y 49 bloques de ampliación comparados entre Cancillería y Jurinfo. [Selección](../motor_documental/corpus/ampliacion_publicable.json), [bloques](../motor_documental/corpus/evidencia_ampliacion.json), [expediente de 159 diferencias](../motor_documental/corpus/conciliacion_diferencias.json). | Revisión jurídica sustantiva del expediente, cuadros de multas, más cobertura en procedimientos y confirmación de reutilización. |
| Análisis lingüístico · 15 % | spaCy en español. Subconjunto público: 1.800 tokens, 589 tipos, TTR 0,3272 y media de 54,97 tokens por fragmento. [Informe](informe_analisis_linguistico.md). | Muestra anotada de entidades para cuantificar precisión y exhaustividad. PMI se queda sin pares que superen el umbral en el subconjunto. |
| RAG · 20 % | FAISS público separado, 37 vectores de dimensión 384, hashes y metadatos por apartado. En el servicio, 15/50 casos con un acierto y 35 abstenciones documentales. [Rankings](../motor_documental/pruebas/recuperacion_publica_final.json). | Mayor cobertura, separar mejor las peticiones mixtas y completar selección de citables cuando una respuesta necesita varios incisos. |
| Integración · 15 % | Node/FastAPI en HTTP local, fuentes y respuestas públicas, CORS, PDF con `indexado: false`, 26 pruebas Node. Las capturas previas verificaron preguntas libres y sugeridas, historial, fuentes, enlace y error visible. [Auditoría de interfaz](auditoria_urbanismo_gemini.md). | Instalación limpia y ejecución en Linux. WSL no está instalado en el equipo de pruebas. |
| Evaluación · 15 % | 50 preguntas activas, RAG-011 archivada y RAG-051 activa. Corrida con las enumeraciones ajustadas: 26/26 trampas rechazadas sin fuentes, 35 abstenciones sin fuentes y 15 respuestas visibles de Gemini, 4 completas y 11 parciales según el banco. [HTTP](../motor_documental/pruebas/evaluacion_api_gemini_enumeraciones_ajustadas.json), [alcance del banco](../motor_documental/pruebas/cobertura_banco_final.json). | Cotejo humano del banco y sus apartados, carga concurrente y una muestra real con mayor cobertura. |
| Documentación · 15 % | [README](../README.md), origen y segmentación del [corpus](documentacion_corpus.md), comandos y resultados locales, diff y manifiesto de la entrega. | Comparación con el PDF definitivo del docente. |

### Métricas, pruebas y límites

| Ejecución pública | Artículos / fragmentos | Aciertos / abstenciones | P@5 | Recall@5 | MRR |
| --- | ---: | ---: | ---: | ---: | ---: |
| Auditoría previa de urbanismo | 19 / 34 | 14 / 36 | 0,056 | 0,28 | 0,28 |
| 19 de noviembre, servicio operativo | 21 / 37 | 15 / 35 | 0,060 | 0,30 | 0,30 |

Sobre las 50 consultas, Precisión@k es la media de aciertos divididos por k, incluso cuando la lista tiene menos de k candidatos. Recall@k divide el número de artículos esperados hallados entre los artículos esperados. MRR promedia el inverso de la posición del primer esperado, con cero cuando no figura. Se cuentan identificadores de artículo únicos. En 23/50 preguntas al menos un artículo esperado figura en el corpus público. Eso no garantiza que el apartado pedido esté seleccionado.

El diagnóstico sin enrutamiento y con el mismo banco, corpus y modelo dio P@5/Recall@5/MRR de 0,088/0,44/0,3025 por artículo y 0,084/0,42/0,3355 por fragmento. Siete artículos excedieron el límite de 128 tokens del modelo y se truncaron en el experimento por artículo. El índice público usa ventanas de hasta 100 tokens del modelo con 20 de solapamiento. Las cifras del índice histórico se conservan más abajo.

### Corrida HTTP con el índice entregado

FastAPI en 8298 y Node en 3298 arrancaron desde el estado local final. `/estado` anunció el SHA-256 del corpus `f776b4d07089828860b0e76f219ce229ef69e5bd43720064df6303b598833075`, idéntico al de los metadatos públicos. Se verificó el binario FAISS con SHA-256 `f72b4021f9acdb43c5d99dafba77bd46895fe13c32978b5f0cd29867052c922c`. El evaluador recibió `--estado-motor` y registró el SHA-256 del banco activo `dbeab26c86e8cebc541e301b673347584214630b447af06343e3c311c20beaa9`.

Las 50 consultas devolvieron HTTP 200. Las 42 citas de las 15 respuestas visibles coincidieron literalmente con el corpus público y las fuentes visibles, con artículos esperados y rótulos de numeral concordantes. Ningún artículo excluido apareció en las citas ni en las fuentes. Las 35 consultas `SIN_RESPALDO` y las 26 trampas quedaron sin fuentes. RAG-003 mostró el numeral 1 bajo su propio rótulo y los demás numerales del 2 al 14 por separado. RAG-002 mostró solo los primeros tres de los seis objetivos del banco. RAG-027 y RAG-049 conservaron sus cuatro rótulos separados.

Desde `POST /api/chat`, las **15 de 15** consultas con Gemini quedaron por debajo de 10 s: mínimo 0,899 s, mediana 1,140 s, p95 1,555 s y máximo 1,657 s. La muestra fue secuencial y las 35 abstenciones se excluyeron de esos tiempos.

### Corridas HTTP anteriores

En la corrida de 3198/8198, Gemini intervino en 15 consultas con mínimo 0,952 s, mediana 2,476 s, p95 4,987 s y máximo 6,150 s. La revisión de ese lote registró 4 respuestas completas y 11 parciales. [Revisión anterior](../motor_documental/pruebas/revision_respuestas_final.json)

Verificación local de esta fase: 96 pruebas Python aprobadas de 97 ejecutadas, una omitida por permisos de enlaces simbólicos de Windows. Node: 26 de 26.

La regresión determinista confirmó que el encabezado del artículo 8 se separa del primer numeral. Una consulta real de control a RAG-003 en 3199/8199 terminó en 2,610 s y quedó retenida por la validación documental.

**Corrección de la auditoría anterior.** La corrida HTTP anterior usó el corpus con SHA-256 `08173e8fa006cc6b48f14582c6a41f6b9f3d29339d8928b0fb7bef67c615a1b9`. El manifiesto del índice entregado registra `f776b4d07089828860b0e76f219ce229ef69e5bd43720064df6303b598833075`. En aquella corrida, RAG-003 rotuló incorrectamente el numeral 1 del artículo 8 como parte de la cita general del artículo. El control posterior quedó retenido. [Corrida anterior](../motor_documental/pruebas/evaluacion_api_gemini_final.json) · [Control anterior](../motor_documental/pruebas/repeticion_gemini_rag_003.json) · [Metadatos entregados](../motor_documental/embeddings/metadatos_publicables.json)

### Ajuste de enumeraciones y control dirigido

El selector de Gemini y el validador comparten un máximo de 16 citas. La instrucción pide un pasaje literal por numeral pertinente para las preguntas que requieren enumerar. El validador mantiene el cotejo literal con el texto del artículo recuperado y limita también el total de pasajes después de separar una cita agrupada.

| Caso | Corrida anterior con el índice entregado | Control dirigido tras el ajuste |
| --- | --- | --- |
| RAG-002 | Numerales 1–3 de 6, 1,129 s | Numerales 1–6, 13,955 s, fuente visible del artículo 2 |
| RAG-004 | Numerales 1–3 de 5 disponibles, 1,090 s | Numerales 1–5, 1,795 s, fuente visible del artículo 27 |

El control usó Node en 3398 y FastAPI en 8398 con el mismo corpus público. El primer control del proceso recién iniciado, RAG-002, excedió 10 s. [Respuestas del control dirigido](../motor_documental/pruebas/control_api_gemini_enumeraciones.json)

La primera corrida completa con el límite ampliado conservó 50 HTTP 200 y 26 rechazos fuera de dominio. RAG-002 y RAG-004 cubrieron los numerales disponibles. RAG-003 se retuvo, por lo que se amplió el presupuesto de salida a 2048 tokens y se permitió agrupar numerales consecutivos en listas de más de diez, siempre como un extracto continuo. El validador separa los rótulos y coteja los pasajes con la fuente recuperada. [Primera corrida con el ajuste](../motor_documental/pruebas/evaluacion_api_gemini_enumeraciones.json)

El segundo control dirigido, en 3498/8498, verificó los seis numerales de RAG-002 en 5,086 s, los cinco disponibles de RAG-004 en 1,225 s y los catorce de RAG-003 en 2,026 s. Cada pasaje coincidió con su fuente pública visible. [Segundo control dirigido](../motor_documental/pruebas/control_api_gemini_enumeraciones_ajustadas.json)

La corrida completa posterior, con los mismos hashes de corpus y banco que la línea base, obtuvo 50 HTTP 200 y 26/26 trampas rechazadas sin fuentes. Hubo 35 abstenciones documentales sin fuentes y 15 respuestas visibles. Las 46 citas fueron literales, con artículo esperado, fuente pública visible y rótulo de numeral concordante cuando correspondía. Frente a la línea base, RAG-002 pasó de parcial a completa, RAG-003 conservó sus catorce numerales y RAG-004 pasó de tres a cinco numerales disponibles. Los otros 47 textos públicos fueron idénticos. La latencia de las 15 consultas con Gemini fue de 1,261 s como mínimo, 2,013 s de mediana, 6,174 s en p95 y 9,437 s como máximo. Las 15 quedaron por debajo de 10 s en esta corrida secuencial. [Corrida completa con el ajuste final](../motor_documental/pruebas/evaluacion_api_gemini_enumeraciones_ajustadas.json)

### Latencia de RAG-002 al reiniciar el servicio

Se lanzaron procesos nuevos de Node y FastAPI en puertos locales aislados. Por arranque se midió desde el lanzamiento hasta que ambos servicios respondieron a sus rutas de estado y después se enviaron tres consultas RAG-002 secuenciales por `POST /api/chat`. Se registraron los tiempos HTTP y las etapas emitidas por FastAPI. El modelo y FAISS se cargan antes de que FastAPI responda a `/estado`. La medición de inicio incluye el intervalo de sondeo y usa la caché local del modelo. La primera medición de inicio coincidió parcialmente con un ensayo de disponibilidad descartado por usar una ruta de Node incorrecta.

La captura histórica de 13,955 s solo conserva el tiempo HTTP completo y corresponde a la primera versión del ajuste de enumeraciones. Los arranques nuevos usaron el ajuste final. El primer arranque nuevo reprodujo una demora en la primera consulta: 42,727 s, con 42,380 s dentro de la llamada a Gemini y 0,140 s en la recuperación. También se observaron demoras en consultas posteriores. Los datos localizan la demora reproducida en la etapa del proveedor. El registro histórico carece del desglose necesario para atribuir sus 13,955 s a un reintento, a la conexión o al procesamiento del proveedor.

Se conservó el código de producción. Anticipar una llamada a Gemini al iniciar añadiría una solicitud y trasladaría parte de la espera a la disponibilidad del servicio. La carga local observada dentro de la consulta resulta demasiado pequeña frente a la variación de la llamada externa para esperar una reducción útil por ese camino. [Mediciones por arranque](../motor_documental/pruebas/latencia_arranques_antes.json)

| Arranque | Servicios listos (s) | Primera consulta (s) | Segunda (s) | Tercera (s) |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 71,692 | 42,727 | 2,541 | 68,218 (502) |
| 2 | 24,498 | 1,994 | 3,070 | 3,039 |
| 3 | 23,259 | 7,116 | 4,767 | 25,692 (502) |
| 4 | 28,857 | 78,071 (502) | 30,835 | 22,698 |
| 5 | 28,805 | 20,148 | 29,236 | 48,695 |

Superaron 10 s 3 de 5 primeras consultas y 6 de 10 posteriores, contando los errores HTTP. Las medianas respectivas fueron 20,148 s y 24,195 s. Las 12 respuestas HTTP 200 mostraron los seis numerales. En las tres respuestas HTTP 502, el último registro del motor corresponde a la preparación del contexto, justo antes de invocar Gemini. El servicio no registró el detalle del error externo y el código HTTP público no permite identificarlo. En las respuestas lentas con HTTP 200, la etapa Gemini tomó de 19,930 a 48,640 s. La recuperación local de toda la muestra tomó de 0,020 a 0,140 s.

### Alcance de las preguntas y referencias del banco

| Caso | Alcance de la pregunta y de la referencia |
| --- | --- |
| RAG-002 | La pregunta plural requiere los seis objetivos del artículo 2, todos presentes en la fuente recuperada. Tres objetivos constituyen una respuesta parcial. |
| RAG-004 | La pregunta amplia abarca los comportamientos del artículo 27. El subconjunto cotejado permite citar los numerales 1 a 5. La referencia también cubre porte de armas y dispositivos menos letales, fuera de la selección pública. Una respuesta con los cinco numerales sigue parcial frente a esa referencia. |
| RAG-025 | Definición y clasificación responden al núcleo de la pregunta. La referencia también espera cuantías, descuento y objeción. Estos extremos requieren revisión frente a la reforma y quedan fuera del contexto aprobado. |
| RAG-032 | La pregunta pide identificar la norma del ruido. La referencia añade multas y facultades para disolver la reunión o desactivar la fuente. |
| RAG-035 | La pregunta pide comportamientos relacionados con la posesión. La referencia añade la medida de restitución. Otros comportamientos y la medida quedan fuera del alcance público del artículo 77. |
| RAG-037 y RAG-042 | La pregunta pide identificar el comportamiento. Las referencias también añaden una multa para el primer caso y, para el segundo, plazos, reconocimiento y consecuencias de la obra. |
| RAG-045 | La pregunta pide confirmar si las órdenes pueden ser verbales. El primer inciso responde ese punto. La referencia añade obligatoriedad y consecuencias del incumplimiento, que exceden la pregunta y el alcance público. |

La evaluación conserva intactas las referencias. La cobertura de la pregunta y la completitud frente a la referencia pueden producir valoraciones distintas.

### Estimación técnica interna de cumplimiento

Cada componente tiene cinco comprobaciones de igual valor dentro de su peso. Se puntúan únicamente las marcadas como comprobadas en este entorno. El resultado es **72 %** con los pesos del encargo, a falta de la rúbrica original.

| Peso | Comprobaciones que puntúan | Comprobaciones pendientes | Puntos |
| --- | --- | --- | ---: |
| Corpus 20 | Procedencia y segmentación, expediente reproducible, ampliación con evidencia por bloque | Resolución sustantiva, cobertura y reutilización jurídica | 12 |
| Lingüística 15 | Reproducibilidad, tokens/lemas/POS/estadísticas, entidades por reglas con regresión, KWIC/glosario/n-gramas | Validación anotada de entidades y colocaciones públicas suficientes | 12 |
| RAG 20 | Índice trazable, comparación controlada, abstenciones y citas extractivas verificadas | Cobertura amplia, respuestas completas y desambiguación de peticiones con varios apartados | 12 |
| Integración 15 | HTTP, rutas y PDF, entorno/CORS, interfaz en capturas | Instalación limpia y Linux | 12 |
| Evaluación 15 | Banco activo y trampas, rankings y fórmulas, HTTP/latencia, revisión técnica de calidad | Validación jurídica de referencias y pruebas bajo carga | 12 |
| Documentación 15 | Guía de ejecución, corpus e informe lingüístico, matriz/reproducción, paquete trazable | Cotejo con PDF definitivo del docente | 12 |

## Historial de verificaciones

La actualización posterior amplió el alcance público a 19 artículos
y ejecutó la evaluación real de Gemini. Consulta la
[matriz y resultados de la fase de urbanismo](auditoria_urbanismo_gemini.md).
Las mediciones que siguen documentan fases anteriores.

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
## Seguimiento de las respuestas parciales del banco de 50

La línea base verificada tiene 28 artículos, 63 fragmentos y 27/50 aciertos.
La revisión HTTP registró 7 respuestas completas, 18 parciales, una retenida,
23 abstenciones y un error HTTP. Se conservan el
[informe por ID](../motor_documental/pruebas/auditoria_50_lotes_sucesivos.json)
y la [corrida HTTP](../motor_documental/pruebas/evaluacion_api_gemini_lotes_sucesivos.json).

| Requisito | Comprobación y evidencia | Pendiente |
| --- | --- | --- |
| Corpus público | Se añadió la fila del numeral 1 del artículo 93 y el numeral 8 y las filas 1, 3 y 8 del artículo 111. Las capturas del 18 de noviembre de 2026 se revisaron el 19. El [cotejo por bloque](../motor_documental/corpus/evidencia_ampliacion.json) registra fuente y SHA-256. | Siguen excluidas la fila 3 del artículo 93 modificada por la Ley 2450 de 2025, las demás filas, las cuantías y la aplicación acumulada de medidas. |
| Recuperación | Las [50 preguntas](../motor_documental/pruebas/recuperacion_mejora_residuos.json) conservaron los mismos ordenamientos en producción, 27 aciertos, P@5 de 0,108, Recall@5 de 0,54 y MRR de 0,54. El índice mantiene 63 fragmentos. | El texto nuevo amplía las citas posibles para artículos ya recuperados. Aún quedan preguntas sin alcance aprobado. |
| Selección y citas | Se amplió el máximo a 24 citas y a 3.072 tokens de salida. El [diagnóstico previo](../motor_documental/pruebas/diagnostico_18_parciales.json) registra el faltante de cada parcial. Los controles de [selección](../motor_documental/pruebas/control_mejora_seleccion.json) y [cobertura](../motor_documental/pruebas/control_mejora_residuos.json) mostraron los elementos faltantes de RAG-007, RAG-017 y RAG-037. | RAG-012 y RAG-015 omitieron las filas de medidas en el control. RAG-040 omitió el numeral 8 y su fila a pesar de estar disponibles. RAG-035 incorporó restitución, pero la referencia también menciona otras conductas. |
| RAG-003 | La [reproducción](../motor_documental/pruebas/diagnostico_rag003_mejora.json) retornó JSON válido con una cita de 823 caracteres que no figuraba literalmente en el contexto. En el [control posterior](../motor_documental/pruebas/traza_mejora_seleccion.jsonl) volvió a fallar en selección de citas, antes de validación documental. | La salida original de la línea base no está disponible. Se conserva el rechazo de citas inexistentes. |
| RAG-043 y tiempo | En la línea base hubo HTTP 502 con tres intentos HTTP 503 del proveedor. En el control hubo HTTP 200 en 2,529 s, con 0,02 s de recuperación y 2,47 s de generación. | El control aislado no establece el cumplimiento del umbral de 10 s. |
| Abstenciones | La [priorización por ID](../motor_documental/pruebas/diagnostico_23_abstenciones_mejora.json) identifica el alcance necesario en las 23 abstenciones iniciales. | Se mantienen fuera los bloques sin cotejo suficiente, incluidos los que necesitan condiciones judiciales o remisiones. |

Huella del corpus público `13d9f322bc8d85fbca763e0264838f6b984ff786f5bef132349d2c1eade58f0e`.
Huella del FAISS público `34da15d8b4da1df0b6d1741afdbda5238eb7dded3b946cd8f6d7aca280a298ee`.

La [corrida HTTP final](../motor_documental/pruebas/evaluacion_api_gemini_mejora.json)
anuncia esa huella de corpus en `/estado`. El
[comparativo por ID](../motor_documental/pruebas/comparacion_50_mejora.json)
conserva las respuestas, citas, fuentes, rankings, tiempos y trazas.

| Resultado frente al mismo banco | Línea base | Final |
| --- | ---: | ---: |
| Recuperación | 27/50 | 27/50 |
| Completas | 7 | 10 |
| Parciales | 18 | 14 |
| Retenidas | 1 | 2 |
| Abstenciones | 23 | 23 |
| Error HTTP | 1 | 1 |
| Consultas con Gemini, HTTP 200 y menos de 10 s | 14/26 | 25/26 |

Las cuatro altas de completitud fueron RAG-007, RAG-017, RAG-037 y RAG-043.
RAG-038 pasó de completa a HTTP 502. FastAPI devolvió 500 después de tres
respuestas HTTP 429 de Gemini y Node devolvió 502 en 7,536 s. El código 429
acredita un límite o cuota, sin identificar por sí solo cuál. RAG-022 pasó
de parcial a retenida en selección de citas. RAG-003 volvió a quedar retenida.
Las 80 citas de la corrida final fueron literales en el corpus y en la fuente
visible y correspondieron al artículo esperado. Se rechazaron las 26 trampas.
RAG-031 mostró explícitamente el parágrafo 2.

RAG-040 fue la única generación HTTP 200 por encima de 10 s, con 44,009 s
totales. La recuperación tomó 0,099 s, la generación 43,871 s y la validación
0,001 s. Hubo dos intentos con HTTP 429 de 0,265 y 0,294 s y un tercero
exitoso de 36,971 s. La diferencia de cerca de 6,34 s entre la generación
y la suma de los intentos incluye esperas entre los reintentos. RAG-043
respondió en 1,734 s en el barrido final con un intento de 1,621 s.
La [traza](../motor_documental/pruebas/traza_api_gemini_mejora.jsonl)
permite separar esos casos. El requisito de rendimiento general sigue pendiente.

Las pruebas finales ejecutaron 107 casos de Python (106 aprobados y uno
omitido) y 26 de Node (todos aprobados). Comandos desde la raíz del repositorio:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
npm.cmd --prefix backend test
.\.venv\Scripts\python.exe -m motor_documental.pruebas.comparar_recuperacion --publicable --salida motor_documental/pruebas/recuperacion_reproduccion.json
.\.venv\Scripts\python.exe -m motor_documental.pruebas.evaluar_api --url http://127.0.0.1:4098/api/chat --estado-motor http://127.0.0.1:9098/estado --salida motor_documental/pruebas/evaluacion_api_reproduccion.json
git diff --check
```
## Selección por apartados recuperados

La [línea base HTTP](../motor_documental/pruebas/evaluacion_api_gemini_mejora.json)
y su comparativo coinciden con el banco, el corpus y el índice públicos.
La línea base tenía 27/50 aciertos, 10 completas, 14 parciales, dos retenidas,
23 abstenciones y un HTTP 502. El
[diagnóstico de las 14 parciales](../motor_documental/pruebas/diagnostico_14_parciales_apartados.json)
distingue textos ya disponibles y pendientes de corpus. En esta fase se
conservaron el índice, el corpus y el banco.

Las salidas originales de RAG-003 y RAG-022 no están en la corrida HTTP.
En la [reproducción previa](../motor_documental/pruebas/traza_antes_apartados.jsonl),
RAG-003 generó catorce citas literales, dos de 21 y 19 caracteres, por debajo
del mínimo de 24 en la selección anterior. RAG-022 generó cuatro citas y
una no estaba literalmente en la fuente. Ambas se retuvieron antes de
invocar el validador documental. Otra reproducción de RAG-003, de la fase
previa, detectó una cita no literal, por lo que la causa puede variar por intento.

Gemini selecciona ahora identificadores locales de bloques cotejados que
pertenecen al material recuperado. El servidor vuelve a comprobar los
bloques contra el contexto y se encarga de transcribirlos y rotularlos. Los
identificadores ajenos al catálogo y las afirmaciones adicionales no son
válidos en la respuesta estructurada. El validador documental se mantiene.

En los [controles posteriores](../motor_documental/pruebas/control_despues_apartados.json),
RAG-003 mostró los catorce principios, RAG-022 mostró ambos incisos, y
RAG-040 incluyó los numerales 1 y 8 y sus dos medidas. También presentó el
numeral 3 como regla separada. RAG-012 y RAG-015 mostraron las filas de medidas,
y RAG-035 y RAG-045 recuperaron los elementos faltantes de sus referencias.
RAG-041 quedó retenida en el control. Las 26 trampas se rechazaron.

RAG-038 y RAG-043 obtuvieron HTTP 200 en 3,947 y 3,912 s en los controles.
La prueba simulada del SDK comprobó tres intentos por HTTP 429 o 503, un
HTTP 500 seguro en FastAPI y ausencia de detalles sensibles. Las pruebas
Node comprueban la comunicación del error al cliente como HTTP 502.

El [comparativo final por ID](../motor_documental/pruebas/comparacion_50_apartados.json)
cruza la [única corrida HTTP completa de la fase](../motor_documental/pruebas/evaluacion_api_gemini_apartados.json)
con la línea base. El aumento neto fue de ocho completas.

| Indicador | Antes | Después |
| --- | ---: | ---: |
| Aciertos de recuperación | 27/50 | 27/50 |
| Completas | 10 | 18 |
| Parciales | 14 | 8 |
| Retenidas | 2 | 1 |
| Abstenciones | 23 | 23 |
| Errores HTTP | 1 | 0 |
| Trampas rechazadas | 26/26 | 26/26 |
| Generaciones HTTP 200 inferiores a 10 s | 25/26 | 27/27 |

RAG-003, RAG-012, RAG-015, RAG-022, RAG-035, RAG-040 y RAG-045
completaron sus referencias en los controles y en la corrida final.
RAG-038 volvió a completa en una generación exitosa, sin repetir los
429 de la línea base. RAG-043 siguió completa. Ninguna de las diez
completas iniciales perdió esa clasificación. Las 138 citas finales fueron
literales, visibles en la fuente y del artículo esperado.

RAG-041 pasó de parcial a retenida. La
[traza final](../motor_documental/pruebas/traza_api_gemini_apartados.jsonl)
identifica dos identificadores solicitados por Gemini, con al menos uno fuera
del catálogo. La protección descartó la selección antes del validador
documental. Las ocho parciales conservan pendientes de corpus detallados en
el comparativo. Para RAG-027 y RAG-049 ya aparece la competencia; la
apelación sigue excluida.

Los tiempos finales de generación HTTP 200, medidos de extremo a extremo,
tuvieron mediana de 1,299 s, p95 de 4,224 s y máximo de 5,064 s.
Este resultado describe la corrida observada. Los 44,009 s de RAG-040
en la línea base y la exposición a límites del proveedor mantienen pendiente
demostrar un rendimiento sostenido.

Python ejecutó 109 casos (108 aprobados y uno omitido); Node aprobó los 26.
Para reproducir las pruebas y la evaluación, usar los comandos de la sección
anterior cambiando el nombre del JSON de salida para conservar esta corrida.
## Catálogo restringido y ampliaciones urbanística y de equipos móviles

La línea base de esta fase fue de 27/50 aciertos, 18 completas, ocho
parciales, una retenida, 23 abstenciones y ningún error HTTP. Se rechazaron
26/26 trampas. El [diagnóstico por ID](../motor_documental/pruebas/diagnostico_8_parciales_23_abstenciones_catalogo.json)
conserva pregunta, referencia, contexto usado y faltantes de las ocho
parciales, y registra las 23 abstenciones a partir de la corrida anterior.

### RAG-041

La traza anterior solo indicaba que al menos un ID no pertenecía al
catálogo. Los valores exactos históricos no fueron guardados. La
[reproducción previa](../motor_documental/pruebas/traza_041_antes_catalogo.jsonl)
dio dos valores de formato inválido con el catálogo P1–P4. La traza conserva
marcadores en vez de cadenas arbitrarias del proveedor. P1 y P2 corresponden
a los numerales 1 y 7 del artículo 124 y P3 y P4 a sus respectivas filas.
Al enumerar los IDs válidos en el esquema de Gemini, el
[control](../motor_documental/pruebas/traza_lote_urbanistico_catalogo.jsonl)
seleccionó P1 y P3 y publicó ambas citas literales. Las pruebas rechazan
identificadores inventados y números sin prefijo. El ataque y su multa,
condicionales en la referencia, siguen sin darse por respondidos si se omiten.

### Lotes cotejados

| Lote | Pasajes y alcance | Evidencia y medición |
| --- | --- | --- |
| Urbanismo | Art. 135, parágrafos 1 y 2. Se conservan literal A, numeral 4 y su fila del parágrafo 7. El Decreto 555 corrigió la fila y T-535/24 exige considerar garantías al aplicar la medida. El reconocimiento tiene condiciones y no es automático. | [Cancillería](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#135), [Decreto 555](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=80775), [T-535/24](https://www.corteconstitucional.gov.co/relatoria/2024/t-535-24.htm). [Recuperación](../motor_documental/pruebas/recuperacion_lote_urbanistico_catalogo.json), 27/50 y 66 fragmentos. RAG-042 mostró ambos parágrafos en el control. |
| Equipos móviles | Art. 95, numeral 1, parágrafo 2 y fila 1 del parágrafo 3. La referencia a la Ley 1453 identifica la base de datos y permanece dentro de la cita literal. Esa ley no se recupera ni se presenta como fuente independiente. C-094/20 se inhibió sobre el numeral 8, excluido. | [Cancillería](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#95), [Decreto 1078](https://www1.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=77888), [C-094/20](https://www.corteconstitucional.gov.co/relatoria/2020/C-094-20.htm). [Recuperación](../motor_documental/pruebas/recuperacion_lote_celulares_catalogo.json), 29/50 y 70 fragmentos de dimensión 384. RAG-016 y RAG-039 mostraron la conducta, la verificación y las medidas en los controles. |

El [expediente por bloque](../motor_documental/corpus/evidencia_ampliacion.json)
mantiene la procedencia de las capturas del 18 de noviembre de 2026 y la
fecha de revisión del 19. El SHA de corpus final es
`41507d4d7e91d7527baffade9379c670a10cb42cc3b89f1cdb06e9da7d953324`.
P@5 pasó de 0,108 a 0,116; Recall@5 y MRR pasaron de 0,54 a 0,58.
El SHA-256 del FAISS final es
`dc6e9b6af3d41c73f244a9ff8c8a5bd01766be441029fda9c5c494ce42dba667`.
El SHA-256 de sus metadatos es
`235a9120ab94807e230f9c02ef9c098cd993172891f36f3266778e0ae05a3e2d`.
Los dos nuevos aciertos fueron RAG-016 y RAG-039, ambos en primer lugar.

### Evaluación HTTP final

La [corrida final](../motor_documental/pruebas/evaluacion_api_gemini_catalogo_final.json)
anunció en `/estado` el mismo SHA de corpus que el índice público.
El [comparativo de los 50 IDs](../motor_documental/pruebas/comparacion_50_catalogo_final.json)
contiene rankings, respuestas, citas, fuentes, latencias y trazas por etapa.

| Indicador | Base | Final |
| --- | ---: | ---: |
| Recuperación | 27/50 | 29/50 |
| Completas | 18 | 19 |
| Parciales | 8 | 10 |
| Retenidas | 1 | 0 |
| Abstenciones | 23 | 21 |
| Errores HTTP | 0 | 0 |
| Trampas rechazadas | 26/26 | 26/26 |
| Generaciones HTTP 200 superiores a 10 s | 0/27 | 3/29 |

El saldo de completitud fue **+1**. RAG-016, RAG-039 y RAG-042
pasaron a completas en el control y en el barrido. RAG-035 y RAG-045
pasaron a parciales por omisiones de selección con texto disponible.
RAG-035 tuvo además un primer intento HTTP 503 y terminó con HTTP 200;
el estado HTTP no explica por sí mismo la omisión. RAG-045 no tuvo
fallo del proveedor. RAG-041 pasó de retenida a parcial y citó de nuevo
el numeral 1 y su fila; omitió el supuesto condicional del numeral 7.
Las 139 citas finales fueron literales en el corpus y en su fuente visible
y correspondieron al artículo esperado.

RAG-012 tardó 13,890 s, RAG-016 14,285 s y RAG-028 39,253 s.
Cada una tuvo un intento exitoso sin reintentos. La recuperación quedó
por debajo de 0,09 s en esos casos; la espera se concentró en Gemini.
El p95 del tiempo HTTP de las 29 consultas con Gemini fue 14,127 s y
la mediana 1,455 s. El requisito de rendimiento sigue pendiente.

Se ejecutaron 112 pruebas Python (111 aprobadas y una omitida), 26
pruebas Node aprobadas y `git diff --check` sin errores.

### Pendientes jurídicos

- **RAG-004 y RAG-025.** Cerrar la versión operativa de los numerales sobre
  armas y las filas del artículo 27 con Ley 2197 y Decreto 207. En multas,
  contrastar los tipos y valores con los efectos de Ley 2450, incluidas las
  referencias a objeción y descuentos que exceden la pregunta.
- **RAG-026.** La Ley 2492 reformó el artículo 206. La compilación mantiene
  una redacción anómala en el literal c del numeral 5. Quedan pendientes el
  texto aplicable de la medida, las instancias y el régimen de remisiones a
  los artículos 205 del Código y 38 del CGP.
- **RAG-027 y RAG-049.** C-282/17 declaró exequible el efecto devolutivo
  por el cargo examinado. La copia conserva la denominación anterior del
  destinatario. El artículo 10 de la Ley 2492 exige reflejar la denominación
  actual al mostrar el parágrafo completo, que permanece excluido.
- **RAG-028 y RAG-050.** Falta el bloque integrado de autoridad, audiencia,
  pruebas, recursos y cumplimiento. Se requiere reflejar Ley 2492 y Decreto
  768 y conciliar la inasistencia con C-349/17. El expediente D-14308
  también requiere cierre documental para los literales acusados.
- **Abstenciones de mayor impacto.** Art. 33 requiere conciliar Ley 2450 y
  C-308/19 antes de publicar medidas por ruido. Art. 35.1 sigue fuera por
  el alcance en libertad de expresión, sin decisión de fondo en C-223/25.
  Arts. 155 y 163 necesitan incorporar sus condiciones judiciales sobre el
  informe, posibilidad de cesación y control posterior. Art. 237 requiere
  representar el condicionamiento de datos de C-094/20 junto al texto.
- **Demás abstenciones.** Las referencias generales de los artículos 38,
  40, 92, 93, 124, 135, 140 y 146 requieren cubrir bloques más amplios que
  los extractos. El detalle por pregunta está en el diagnóstico. El
  procedimiento 223A requiere distinguir los plazos de objeción y
  aceptación y revisar su concordancia con la redacción del artículo 180.

### Reproducción

Desde la raíz, con la caché del modelo de embeddings disponible y la clave
configurada localmente para HTTP:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
npm.cmd --prefix backend test
git diff --check
.\.venv\Scripts\python.exe -m motor_documental.pruebas.comparar_recuperacion --publicable --salida motor_documental/pruebas/recuperacion_catalogo_reproduccion.json
.\.venv\Scripts\python.exe -m motor_documental.pruebas.evaluar_api --url http://127.0.0.1:4096/api/chat --estado-motor http://127.0.0.1:9096/estado --salida motor_documental/pruebas/evaluacion_catalogo_reproduccion.json
```

La prueba HTTP usó Node en 4096 y FastAPI con
`python -m motor_documental.pruebas.motor_diagnostico_gemini` en 9096.
El verificador de ampliación usó las capturas documentadas antes de generar
FAISS con `python -m motor_documental.indice_publicable`.
## Estabilidad de la selección sobre el corpus aprobado

La base de esta fase fue de 29/50 aciertos de recuperación, 19 completas,
diez parciales, ninguna retenida, 21 abstenciones y ningún error HTTP.
También rechazó las 26 trampas. Se mantuvieron el banco y el índice
público de 29 artículos, 70 fragmentos y dimensión 384. El FAISS conserva
la huella `dc6e9b6af3d41c73f244a9ff8c8a5bd01766be441029fda9c5c494ce42dba667`.

El [diagnóstico por ID](../motor_documental/pruebas/diagnostico_estabilidad_parciales.json)
conserva preguntas, referencias, catálogos reconstruidos, respuestas y
trazas de las dos corridas anteriores. Los IDs exactos de la primera no
quedaron registrados; los IDs indicados para ella se infieren de las citas
literales publicadas, sin afirmar su orden original.

| Caso | Evidencia y corrección |
| --- | --- |
| RAG-035 | El mismo contexto y catálogo produjo antes los cinco numerales y sus filas. En la línea base Gemini eligió P1, P2 y P7, correspondientes al cuerpo, numeral 1 y su medida. Cuando hay un supuesto de ocupación y una pregunta amplia sobre posesión o tenencia, la regla completa el listado de conductas y la fila del supuesto descrito, si Gemini ya eligió la conducta base. |
| RAG-045 | Con igual contexto, Gemini pasó de citar ambos incisos a elegir solo P1. La forma verbal quedó contestada, pero la referencia también pide obligatoriedad e incumplimiento. La regla agrega ese inciso al hablar de la forma verbal de una orden en un procedimiento. |
| RAG-041 | P1 y P3 eran válidos. Responden a deambular sin medidas y su multa. P2 y P4, aprobados y recuperados, corresponden a permitir o tolerar un ataque y su medida. La regla los añade como supuesto separado con su condición literal si se describe deambulación, riesgo y una pregunta abierta sobre lo que prevé el Código. |
| RAG-004, 025, 026, 027, 028, 049 y 050 | El cierre frente a la referencia depende de los apartados jurídicos que se detallan en el diagnóstico. No se encontró en ellas un cierre completo con pasajes aprobados que hubieran dejado de recuperarse. |

La selección se comprueba antes de añadir pasajes. Una lista vacía sigue
vacía, cualquier ID inventado invalida la selección y el texto resultante
se verifica de nuevo contra la fuente. Las consultas explícitamente
limitadas a un numeral o parágrafo conservan ese alcance.

Las 21 abstenciones de la base que requieren cotejo son RAG-005 y 032
(art. 33), RAG-006 y 033 (art. 35), RAG-008 y 034 (art. 38), RAG-010
(art. 40), RAG-013 y 036 (art. 92), RAG-014 (art. 93), RAG-018 (art. 124),
RAG-019 (art. 135), RAG-020 (art. 140), RAG-021 (art. 146), RAG-023 y
046 (art. 155), RAG-024 y 047 (art. 163), RAG-029 (art. 223A), RAG-030
(art. 237) y RAG-048 (art. 180). Los apartados pendientes están en el
[diagnóstico del corpus](../motor_documental/pruebas/diagnostico_8_parciales_23_abstenciones_catalogo.json).

### Controles y reproducción

El [informe automático](../motor_documental/pruebas/verificacion_estabilidad_http.json)
confirmó los tres casos dirigidos en dos rondas y los pasajes requeridos
de las otras 19 respuestas completas. El primer intento de la regla de
RAG-041 buscaba un inicio incorrecto del numeral 7. La prueba determinista
detectó que se mostraba la fila sin el numeral; se corrigió el prefijo y
se repitieron los tres casos dos veces antes de habilitar el barrido.
El control de las otras 19 no dependía de esa regla del artículo 124.

En las dos rondas corregidas Gemini siguió seleccionando P1/P2/P7
para RAG-035, P1 para RAG-045 y P1/P3 para RAG-041. La
[traza de ambos controles](../motor_documental/pruebas/traza_estabilidad_validada.jsonl)
atribuye la presencia de los pasajes adicionales a la regla del servidor.
RAG-041 recibió un 429 en la primera ronda y completó la respuesta tras
reintentar. Los tiempos HTTP de las dos rondas fueron 2,284 y 1,788 s
para RAG-035, 1,755 y 4,381 s para RAG-045 y 6,058 y 5,360 s para RAG-041.
En el control de conservación superaron 10 s RAG-038 (13,921 s),
RAG-039 (24,837 s) y RAG-042 (10,299 s).

Desde la raíz del repositorio:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
npm.cmd --prefix backend test
git diff --check
$p = 'motor_documental/pruebas'
.\.venv\Scripts\python.exe -m motor_documental.pruebas.verificar_controles_estabilidad "$p/control_estabilidad_validado_1.json" "$p/control_estabilidad_validado_2.json" "$p/control_estabilidad_segundo.json" "$p/verificacion_estabilidad_reproducida.json"
.\.venv\Scripts\python.exe -m motor_documental.pruebas.evaluar_api --url http://127.0.0.1:4098/api/chat --estado-motor http://127.0.0.1:9098/estado --salida "$p/evaluacion_estabilidad_reproducida.json"
```

Se ejecutaron 113 pruebas de Python, con 112 aprobadas y una omitida,
y 26 pruebas de Node aprobadas. La suite Python comprobó dimensión,
metadatos, texto de los fragmentos, exclusiones y compatibilidad de
las huellas del índice público.

### Barrido HTTP final

La [corrida de 50 preguntas y 26 trampas](../motor_documental/pruebas/evaluacion_api_gemini_estabilidad.json)
y el [comparativo por ID](../motor_documental/pruebas/comparacion_50_estabilidad.json)
registran un aumento neto de tres completas. RAG-035, RAG-041 y RAG-045
pasaron a completas en ambos controles y en el barrido. Las 19 completas
previas conservaron sus pasajes requeridos. Las 146 citas finales fueron
literales, visibles en la fuente y del artículo esperado.

| Indicador | Base | Final |
| --- | ---: | ---: |
| Recuperación | 29/50 | 29/50 |
| Completas | 19 | 22 |
| Parciales | 10 | 7 |
| Retenidas | 0 | 0 |
| Abstenciones | 21 | 21 |
| HTTP con error | 0 | 0 |
| Trampas rechazadas | 26/26 | 26/26 |
| Generaciones HTTP 200 por encima de 10 s | 3/29 | 0/29 |

La mediana de tiempo HTTP con Gemini fue 2,476 s, el p95 fue 6,026 s
y el máximo 6,236 s en RAG-051, con un único intento exitoso de 6,167 s.
En la [traza final](../motor_documental/pruebas/traza_api_gemini_estabilidad.jsonl)
se observó un 503 en RAG-002 y un 429 en RAG-025 y RAG-043. Cada
consulta se recuperó con un reintento. El resultado de 0/29 no elimina
los excesos de 10 s del control de conservación y de las corridas previas.
## Cotejo de procedimientos y transporte

Se verificó la línea base de 29/50 aciertos, 22 completas, siete parciales,
21 abstenciones, cero errores y 26/26 trampas rechazadas. El
[inventario por ID](../motor_documental/pruebas/inventario_cotejo_28.json)
registra los 28 casos pendientes, con su referencia, las medidas y el
bloqueo documental. La [auditoría de pertinencia](../motor_documental/pruebas/auditoria_pertinencia_pasajes.json)
revisó las citas y condiciones de RAG-035, RAG-041 y RAG-045. La muestra
no mostró regresiones. Las reglas de esos casos se conservaron.

### Apartados cotejados y habilitados

La fuente textual de los bloques fue la compilación jurídica de la
Cancillería de Colombia, contrastada con Jurinfo de la JEP. Se conservaron
las huellas de las capturas del 18 de noviembre de 2026. La revisión de
los bloques y la consulta web de las fuentes que se citan abajo se hicieron
el 19 de noviembre de 2026. El
[expediente por apartado](../motor_documental/corpus/evidencia_ampliacion.json)
identifica unidad, bloque, fecha, URL, alcance y SHA-256 del texto. El cotejo
documental automatizado y la revisión de fuentes sustentan la selección del
prototipo. La validación jurídica humana permanece pendiente.

| Lote | Alcance y decisiones | Recuperación y control |
| --- | --- | --- |
| Artículo 222 | Parágrafo 1, apelación y efecto devolutivo. La Corte Constitucional examinó el efecto en C-282/17 y lo declaró exequible por el cargo analizado. La nota visible explica que la Ley 2492 de 2025, art. 10, actualizó la denominación de la autoridad. Quedaron fuera los §§2 y 3. | 29/50, 71 vectores. RAG-027 y RAG-049 incluyeron competencia, cuatro etapas y §1. [Cancillería](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#222), [Corte Constitucional](https://www.corteconstitucional.gov.co/relatoria/2017/C-282-17.htm), [Ley 2492, Presidencia](https://dapre.presidencia.gov.co/normativa/normativa/LEY%20No%202492%20DEL%2023%20DE%20JULIO%20DE%202025.pdf), [control](../motor_documental/pruebas/control_cotejo_proceso_inmediato.json). |
| Artículo 223 | Inciso de competencia, numerales 1 a 5, literales a–d del 3 y §§1–4. El Auto 579/21 rechazó la súplica D-14308 sin decisión de fondo. El texto del §1 se acompaña del condicionamiento de C-349/17 sobre inasistencia con justa causa. Se mantiene la nota de denominación y se cotejó el reglamento del Decreto 768. El §5 se conservó fuera. | 29/50, 86 vectores. RAG-028 y RAG-050 incluyeron etapas, recursos, plazo de cumplimiento y nota judicial. [Cancillería](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#223), [C-349/17](https://www.corteconstitucional.gov.co/relatoria/2017/C-349-17.htm), [A-579/21](https://www.corteconstitucional.gov.co/relatoria/autos/2021/a579-21.htm), [Decreto 768, Presidencia](https://dapre.presidencia.gov.co/normativa/normativa/DECRETO%200768%20DEL%2007%20DE%20JULIO%20DE%202025.pdf), [control](../motor_documental/pruebas/control_cotejo_proceso_abreviado.json). |
| Artículo 146 | Numerales 1 a 16, literales a–h del 10 y filas 1 a 16 del §1. Los cuadros incluyen amonestaciones, multas y reparación para el numeral 13. El §2 sobre cámaras, examinado en C-094/20, queda fuera. | 30/50, 96 vectores. RAG-021 mostró 41 bloques con dos extractos visibles. El primer control de RAG-044 omitió siete filas y el numeral 16. Tras preservar el alcance de pasajeros mediante las 7 conductas pertinentes con sus medidas, el [recontrol](../motor_documental/pruebas/control_cotejo_transporte_acotado.json) mostró los 14 bloques esperados. [Cancillería](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#146), [C-094/20](https://www.corteconstitucional.gov.co/relatoria/2020/C-094-20.htm). |

P@5 aumentó de 0,116 a 0,120. Recall@5 y MRR aumentaron de 0,58 a 0,60.
El [índice público](../motor_documental/embeddings/metadatos_publicables.json)
tiene 29 artículos y 96 vectores de dimensión 384. Las comprobaciones
revisaron jerarquía, apartados, continuidad, límites por ventana, huellas y
exclusión de los bloques pendientes. SHA-256 del corpus
`84c2842d557359483bb8ed8079930fbfe354a45d9156ea364ec90fabd0dd4e07`.
SHA-256 del FAISS
`1cae242aa759feac7180b277184ddce91b0a319b6936dd401895e336f8f0d322`.
SHA-256 de metadatos
`f25295fa98b737ec7e76fdfa03e5ed2a28505d38397e386cbb63cd616ebf1852`.

### Preparados para revisión y fuera del alcance público

Los extractos restantes del artículo 27 deben cotejar la Ley 2197 y el
Decreto 207. Los tipos, cuantías y descuentos del artículo 180 requieren
conciliar la Ley 2450 y las referencias del banco. La competencia del
artículo 206, reformada por la Ley 2492, requiere verificar el texto del
literal c del numeral 5, las remisiones y las comisiones. Los artículos
33, 35, 155, 163 y 237 requieren resolver el alcance de las reformas y
condiciones judiciales antes de entregar medidas, acceso o facultades.
Las demás preguntas con alcance insuficiente están en el inventario por
ID. El banco y los índices históricos se conservaron.

### Evaluación HTTP final y pruebas

| Resultado | Base | Final |
| --- | ---: | ---: |
| Aciertos de recuperación | 29/50 | 30/50 |
| Completas | 22 | 27 |
| Parciales | 7 | 2 |
| Retenidas | 0 | 0 |
| Abstenciones | 21 | 20 |
| Errores HTTP | 0 | 1 |
| Trampas rechazadas | 26/26 | 26/26 |

RAG-021, RAG-027, RAG-028, RAG-049 y RAG-050 pasaron a completas tanto
en sus controles como en el barrido. Las 22 completas anteriores
conservaron todos los pasajes de la línea base. RAG-004 y RAG-026
quedaron parciales. RAG-025, antes parcial por alcance del artículo 180,
dio HTTP 502 en 6,960 s después de tres 429 de Gemini. RAG-026 y RAG-035
se recuperaron de un 429. Se verificaron 221 citas literales en su fuente
visible y del artículo esperado. El
[comparativo por ID](../motor_documental/pruebas/comparacion_50_cotejo_final.json)
incluye tiempos HTTP, trazas y fuentes.

Las 29 consultas con Gemini y HTTP 200 tuvieron mediana de 1,246 s, p95
de 3,034 s y máximo de 5,009 s. Ninguna de las 50 consultas de esta
corrida superó 10 s, incluido el error, que se contabiliza aparte.
El resultado no acredita el cumplimiento sostenido del umbral.

Python ejecutó 115 pruebas con 114 aprobadas y una omitida. Node pasó
26 de 26. `git diff --check` pasó. Para repetir la recuperación y HTTP,
desde la raíz, con Node en 4096 y el motor de diagnóstico en 9096:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
npm.cmd --prefix backend test
git diff --check
.\.venv\Scripts\python.exe -m motor_documental.pruebas.comparar_recuperacion --publicable --salida motor_documental/pruebas/recuperacion_cotejo_reproducida.json
.\.venv\Scripts\python.exe -m motor_documental.pruebas.evaluar_api --url http://127.0.0.1:4096/api/chat --estado-motor http://127.0.0.1:9096/estado --salida motor_documental/pruebas/evaluacion_cotejo_reproducida.json
```
## Chat real y cotejo de conductas, competencias y ruido

La línea base verificada fue de 30/50 aciertos, 27 completas, dos
parciales, 20 abstenciones, ninguna retenida y un error HTTP.
Se rechazaron las 26 trampas. El banco conserva su huella original.

### Comprobación de navegador

Chrome de escritorio cargó [el chat en localhost:3000](http://127.0.0.1:3000)
y ejecutó las seis preguntas solicitadas. Ese puerto ya estaba ocupado
y el FastAPI preexistente respondía sin la huella de corpus exigida para
atribuirle resultados de esta rama. Se preservaron ambos servicios.
La [evidencia de ese acceso](../motor_documental/pruebas/chat_navegador_real.json)
se conserva por separado.

Arranqué Node y FastAPI en 4098 y 9098 con la configuración local y
verifiqué la huella por `/estado`. En [el control previo de la rama](../motor_documental/pruebas/chat_navegador_indice_actual.json)
Chrome mostró RAG-051 con artículo 5, RAG-044 con 14 citas y dos extractos,
RAG-004 y RAG-026 parciales, RAG-029 sin respaldo y la trampa de renta
fuera de alcance, sin fuentes en los dos últimos casos.

La [captura anterior](../motor_documental/pruebas/chat_navegador_indice_actual_rag044.png)
mostró que los numerales de conductas y las filas de medidas se veían
iguales. El chat ahora muestra encabezados para ambos grupos y desplaza
al comienzo de una respuesta cuando excede el alto de la conversación.
Los textos originales, los enlaces y las evidencias plegables se conservan.
En [el control posterior](../motor_documental/pruebas/chat_navegador_final.json)
verifiqué las 14 citas, evidencia separada, rótulos de grupos, historial,
nueva conversación, aviso informativo, enlaces HTTPS visibles y que un
fragmento HTML se renderizara como texto. También inspeccioné la
[captura posterior](../motor_documental/pruebas/chat_navegador_final_rag044.png)
de la lista de conductas y el comienzo del grupo de medidas.

No se comprobó el diseño móvil ni se abrió un sitio normativo desde el
navegador de prueba. Para comprobarlos manualmente, ajuste la ventana a
un ancho móvil, envíe RAG-044, desplácese hasta «Ver fragmentos recuperados»
y abra el enlace de Cancillería. Debe abrirse en otra pestaña y la
conversación debe seguir visible. En una sesión propia, compare
`http://127.0.0.1:8000/estado` con la huella registrada aquí antes
de medir el chat del puerto 3000.

### Cotejo e índice público

| Caso | Decisión documental |
| --- | --- |
| RAG-004 | Se incorporaron los numerales 6–11 para contestar las conductas. Ley 2197 art. 39 incorporó los numerales 8–11 y Decreto 207 art. 19 corrigió la transcripción. C-051/20 se inhibió sobre parte del 7; C-014/23 resolvió otras previsiones de Ley 2197. Se excluyeron las filas nuevas, incluida la duplicación de rótulo 8 donde corresponde verificar la fila 9. La pregunta solicita conductas. [Cancillería](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#27), [Decreto 207](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=177086), [C-051/20](https://www.corteconstitucional.gov.co/relatoria/2020/C-051-20.htm). |
| RAG-026 | Se incorporaron restitución de tierras comunales, instancias, medidas, comisiones y demás atribuciones pertinentes del artículo 206 reformado por Ley 2492 art. 6. Las remisiones se mantienen en su cita literal y no se convierten en nuevas fuentes abiertas del chatbot. Se excluyó el literal c del numeral 5 por la redacción anómala incluso en el texto oficial. [Cancillería](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#206), [Ley 2492, Presidencia](https://dapre.presidencia.gov.co/normativa/normativa/LEY%20No%202492%20DEL%2023%20DE%20JULIO%20DE%202025.pdf). |
| RAG-005 y RAG-032 | Se incorporó ruido del numeral 1, literales a–c, fila 1 y §§3–7 reformados por Ley 2450 art. 18. La referencia del banco dice tipo 3; la fuente cotejada dice tipo 4. Se conserva el banco y se evalúa el desacuerdo de manera explícita. C-308/19 limita la desactivación a los supuestos comprobados y no autoriza ingreso a domicilio. §6 incluye una remisión a la ley modificatoria, con su aclaración documental. El numeral 2 sigue excluido. [JEP, Ley 2450](https://jurinfo.jep.gov.co/Normograma/compilacion/docs/ley_2450_2025.htm), [C-308/19](https://www.corteconstitucional.gov.co/relatoria/2019/C-308-19.htm). |
| RAG-025 | El 502 base tardó 6,960 s tras tres 429 de Gemini. En el control dirigido hubo HTTP 200 en 1,128 s, lo cual no acredita disponibilidad estable. El 502 simulado en Chrome se mostró como error comprensible sin fuentes ni citas. Los montos, tipos especiales y descuentos del art. 180 siguen condicionados al cotejo con Ley 2450, art. 223A y la regla de conversión UVB de Ley 2294 art. 313. [Ley 2294](https://www.cancilleria.gov.co/normograma/compilacion/docs/ley_2294_2023.htm). |

Las compilaciones contrastadas conservan capturas del 18 de noviembre
de 2026 y el expediente registra revisión del 19 y las fuentes oficiales
consultadas durante el cotejo. El
[inventario de las 20 abstenciones de partida](../motor_documental/pruebas/inventario_chat_20_abstenciones.json)
conserva el bloqueo y alcance por pregunta. Fuera de los lotes anteriores
siguen pendientes las reformas y decisiones allí registradas. No se
presenta el contraste automático como validación jurídica humana.

El lote de conductas y atribuciones tuvo 104 vectores y 30/50 aciertos.
El lote de ruido dejó 117 vectores de dimensión 384 y 32/50 aciertos.
P@5 pasó de 0,120 a 0,128; Recall@5 y MRR de 0,60 a 0,64. Las huellas
de corpus, FAISS y metadatos son respectivamente
`f3153f86278f97bce99f39e490a36103b8e36a37059af45b7d6a9464a5b69d54`,
`1ca5bb84eca52f405cbf31ffe92e93880059bb98db4fe57b16d2cfa63af8285c` y
`e057f9d2b0c19131b0ceba44eea40b36af3102330214fbe6f5aa1131e285f500`.

### Medición final

| Indicador | Base | Final |
| --- | ---: | ---: |
| Recuperación | 30/50 | 32/50 |
| Completas | 27 | 29 |
| Parciales | 2 | 3 |
| Abstenciones | 20 | 18 |
| Retenidas | 0 | 0 |
| Errores HTTP | 1 | 0 |
| Trampas rechazadas | 26/26 | 26/26 |

RAG-004 y RAG-026 fueron completas en controles y barrido. Las 27 previas
conservaron sus pasajes. RAG-005 y RAG-032 son parciales frente a la
referencia intacta por el tipo de multa. RAG-025 pasó a parcial al
volver a responder en 1,649 s, con el mismo alcance de multas. Hubo 271
citas literales en las fuentes visibles y del artículo esperado. El
[comparativo por ID](../motor_documental/pruebas/comparacion_50_chat_final.json)
conserva citas, recuperación, resultado y traza de cada caso.

Cuatro de 32 consultas con Gemini superaron 10 s. RAG-051 (15,082 s) y
RAG-032 (18,082 s) tuvieron un único intento exitoso. RAG-038 (15,364 s)
y RAG-041 (12,554 s) reintentaron después de HTTP 503 y 429,
respectivamente. La mediana fue 1,668 s y el p95 fue 15,209 s.
El umbral de 10 s no se cumplió en esta corrida.

Python ejecutó 117 pruebas (116 aprobadas y una omitida), incluidas las
de jerarquía, exclusiones, huellas, dimensión y ventanas completas del
índice. Node aprobó 26 de 26. Las comprobaciones de sintaxis de los
scripts JavaScript y `git diff --check` pasaron. Para reproducir:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -q
npm.cmd --prefix backend test
.\.venv\Scripts\python.exe -m motor_documental.pruebas.comparar_recuperacion --publicable --salida motor_documental/pruebas/recuperacion_chat_reproducida.json
.\.venv\Scripts\python.exe -m motor_documental.pruebas.evaluar_api --url http://127.0.0.1:4098/api/chat --estado-motor http://127.0.0.1:9098/estado --salida motor_documental/pruebas/evaluacion_chat_reproducida.json
node motor_documental/pruebas/verificar_chat_real.cjs "$env:ProgramFiles\Google\Chrome\Application\chrome.exe" motor_documental/pruebas/chat_reproducido.json http://127.0.0.1:4098/
git diff --check
```
## Hitos de revisión y publicación

La [evidencia de los hitos](hitos_publicacion.md) registra el cotejo de los
artículos 35 y 38, los controles de recuperación y la verificación en
Chrome. Los primeros dos commits se publicaron en
`trabajo/ley1801-hitos-verificables`. La consolidación de esa rama reúne
el corpus, la integración y sus pruebas. Los ZIP de revisión se
conservan en el espacio de trabajo.
