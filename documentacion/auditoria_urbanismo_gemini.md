# Auditoría técnica de urbanismo y Gemini

## Punto de partida verificado

El 18 de noviembre de 2026 la rama local y remota coincidían en
`263e554cbc38a3f4249e3a4f9293c4645b7b1244`. El remoto de `main`
seguía en `726828d809dca0f68138b47d65dec8c8b1dd4807`. El alcance público
tenía 18 artículos, 33 fragmentos y 39 bloques de ampliación. El
banco de 50 registraba 14 aciertos documentales y 36 abstenciones.
La brecha principal era la cobertura por apartado, seguida de la
fidelidad de la salida y la falta de una evaluación real atribuible
a la versión local.

## Matriz de esta fase

| Requisito | Resultado y evidencia | Siguiente acción |
|---|---|---|
| Corpus, procedencia y vigencia | Se reprodujo byte a byte el expediente de 159 diferencias. Los 39 bloques anteriores se conservaron y se añadieron tres del art. 135. [Selección](../motor_documental/corpus/ampliacion_publicable.json) · [Cotejo](../motor_documental/corpus/evidencia_ampliacion.json) | Revisar los demás numerales y medidas, los plazos de reconocimiento y ejecución, y el régimen aplicable a predios no aptos o protegidos. Mantener separados corpus histórico, referencia oficial y alcance público. |
| Análisis lingüístico | Se reprodujeron 249 artículos, 53.943 tokens y 5.059 tipos en spaCy. El conjunto público dio 19 artículos con apartados seleccionados, 1.677 tokens, 557 tipos, TTR 0,3321 y media 88,26 tokens. [Histórico](../motor_documental/analisis/resultados_linguisticos.json) · [Público](../motor_documental/analisis/resultados_linguisticos_publicables.json) | Afinar detección de cantidades y plazos y medir exactitud de entidades sobre una muestra mayor anotada. |
| Recuperación | Regeneración del índice público de 34 fragmentos, 384 dimensiones, con revisión del modelo fijada. Sobre 50 preguntas, P@5 0,056, Recall@5 0,28 y MRR 0,28. Hubo 14 aciertos y 36 abstenciones. [Medición](../motor_documental/pruebas/recuperacion_publica_urbanismo.json) | Afinar el enrutamiento de consultas ambiguas y ampliar apartados cotejados. El banco pregunta por temas más amplios que el extracto de urbanismo. |
| Interfaz, fuentes y API | Chrome verificó una consulta libre real de urbanismo, texto y enlace de la fuente, abstención ante una descripción genérica del art. 77, historial, reinicio y aviso. Otra prueba pulsó una sugerencia y comprobó la interfaz ante un HTTP 503 con una captura local reutilizada. CORS devolvió 204 al origen admitido y 403 al otro. Node verificó PDF válido, inválido y sin texto, además de `indexado: false`. [Navegador real](../motor_documental/pruebas/verificacion_navegador_urbanismo.json) · [Sugerencia y error reproducidos](../motor_documental/pruebas/verificacion_navegador_reproduccion.json) | Probar en Linux y repetir el recorrido de sugerencias con Gemini si se cambian las preguntas. |
| Evaluación real | 26/26 trampas rechazadas. De 50 consultas, Gemini intervino en 14: 13 respuestas visibles y una retenida. Hubo 36 abstenciones previas a Gemini y cero errores HTTP. [Corrida identificada](../motor_documental/pruebas/evaluacion_api_gemini_extractiva.json) | Ampliar el conjunto de respuestas sustentables, revisar jurídicamente las referencias del banco y repetir la medición en un entorno independiente. |

## Artículo 135

Se habilitó el encabezado del literal A, su numeral 4 y la fila
correspondiente del parágrafo 7. La conducta cotejada está limitada
a terrenos aptos sin licencia o con licencia caducada. La fila
prevé multa especial por infracción urbanística, demolición de obra,
construcción, cerramiento, reparación o mantenimiento de inmueble y
remoción de bienes. La lista describe medidas, cuya aplicación
requiere el procedimiento y la evaluación del caso. El extracto
excluye cálculos, plazos, reconocimiento de obras y otras filas.
[Compilación de Cancillería](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#135) ·
[Decreto 555 de 2017, art. 10](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=80775) ·
[Sentencia T-535/24](https://www.corteconstitucional.gov.co/relatoria/2024/t-535-24.htm)

La revisión del banco conservó RAG-019 y RAG-042 con sus referencias
históricas. RAG-019 pide el catálogo de infracciones y RAG-042
incluye en la referencia apartados y plazos fuera de la selección.
Ambos quedaron entre las abstenciones de la corrida del banco.
La consulta acotada de construcción sin permisos se comprobó por
separado en el navegador. La coincidencia entre compilaciones es
evidencia de cotejo textual. La revisión jurídica de los apartados
excluidos sigue pendiente. Las condiciones de reutilización se
describen en la [documentación del corpus](documentacion_corpus.md).

## Comparación de recuperación

| Modo sobre el mismo corpus público de 19 artículos | P@5 | Recall@5 | MRR |
|---|---:|---:|---:|
| Un vector por artículo, diagnóstico sin enrutamiento | 0,072 | 0,36 | 0,2597 |
| Fragmentos solapados, diagnóstico sin enrutamiento | 0,068 | 0,34 | 0,2822 |
| Índice de fragmentos y filtro del servicio | 0,056 | 0,28 | 0,2800 |

Se usó el mismo banco, el modelo multilingüe MiniLM y producto
interno con vectores normalizados. La longitud máxima del modelo
fue 128 tokens. Seis artículos excedieron el límite en la estrategia
de artículo completo. Los fragmentos de hasta 100 tokens con
solapamiento de 20 preservan más texto. Las dos primeras filas
son diagnósticos y la última representa el servicio. El filtro
prioriza evitar atribuciones sin respaldo ante un tema no cubierto.

## Muestra manual de entidades

| Patrón | Caso histórico | Revisión de la etiqueta |
|---|---|---|
| Autoridad | Policía Nacional, art. 20 | Referencia a la institución, aunque el NER general la clasifica como MISC en parte del corpus |
| Autoridad | Corte Constitucional, art. 27 | Institución correcta, localizada dentro de una nota jurisprudencial del histórico |
| Lugar | Bogotá, art. 12 | Topónimo dentro de la denominación del Concejo Distrital |
| Lugar | Espacio público, art. 2 | Categoría espacial, no un topónimo |
| Monto | 50 %, art. 180 | Proporción del descuento en el histórico, no importe en moneda |
| Monto | 75 %, art. 212 | Proporción de incremento, no un valor en moneda |
| Plazo | 18 años, art. 38 | Falso positivo de plazo, expresa una edad |
| Plazo | ocho (48) horas, art. 63 | El patrón omitió «cuarenta y» de un plazo compuesto |
| Plazo | tres (3) días hábiles, art. 180 | Plazo con unidad y calificador detectados en el histórico |

## Evaluación técnica de respuestas

La corrida aislada verificó antes de consultar que FastAPI anunciara
`citas_extractivas` con generación habilitada. En una primera
medición se observó salida de formato anterior. Esa evidencia se
[conservó aparte](../motor_documental/pruebas/evaluacion_api_gemini_version_anterior.json)
y no se usa para medir esta versión. Las 14 consultas exitosas que
invocaron Gemini tardaron **1,106 s mínimo, 1,576 s mediana, 5,665 s
p95 y 7,883 s máximo**. **14 de 14** estuvieron por debajo de 10 s
en esta muestra secuencial, incluida la respuesta retenida.

La siguiente evaluación es técnica, realizada por el asistente
con la [rúbrica interna](../motor_documental/pruebas/rubrica_evaluacion_respuestas.json)
de 0 a 2. La [captura HTTP](../motor_documental/pruebas/evaluacion_api_gemini_extractiva.json)
conserva cada respuesta y la fuente completa que sustentó las
respuestas visibles. Para RAG-003 el ranking identifica el artículo
8 como contexto. La salida rechazada queda oculta y, por ello,
fidelidad y citas reciben «—». Se valoró la exactitud contra la
referencia del banco y se anotó explícitamente cuándo esta incluye
apartados sin revisión jurídica suficiente.

| Caso | Exactitud | Fidelidad | Citas | Motivo |
|---|---:|---:|---:|---|
| RAG-001 | 2 | 2 | 2 | El art. 1 respalda el objeto preventivo y sus dos finalidades mencionadas. |
| RAG-002 | 2 | 2 | 1 | Se reproducen los seis objetivos. Los rótulos de la corrida solo identifican el primer numeral de cada grupo citado. |
| RAG-003 | 0 | — | — | El control retuvo la salida sobre principios. No se publicó texto ni fuente. |
| RAG-051 | 2 | 2 | 2 | La definición del art. 5 incluye personas, bienes, ambiente y ordenamiento jurídico. |
| RAG-022 | 1 | 2 | 2 | El primer inciso del art. 150 cubre la definición. La referencia añade incumplimiento y plazos, fuera del alcance cotejado. |
| RAG-025 | 1 | 2 | 2 | Se muestran definición y clasificación general. La referencia añade tipos, montos y objeción, pendientes de cotejo tras la reforma de 2025. |
| RAG-026 | 1 | 2 | 2 | Se citan correctamente los numerales 1 y 2 del art. 206 reformado. Las instancias, comisiones y demás competencias quedan fuera. |
| RAG-027 | 1 | 2 | 1 | Incluye las cuatro etapas sin la apelación de la referencia. El rótulo 3 agrupa también el numeral 4. |
| RAG-028 | 1 | 2 | 2 | Los numerales 1 y 2 respaldan inicio y citación. Faltan audiencia, recursos y ejecución de la referencia. |
| RAG-035 | 1 | 2 | 2 | El numeral 1 responde por la ocupación ilegal. La referencia enumera otras conductas y medidas que quedaron fuera. |
| RAG-038 | 1 | 2 | 2 | Se identifica la infracción sanitaria. La medida mencionada por la referencia queda fuera del extracto. |
| RAG-045 | 2 | 2 | 2 | El primer inciso responde a la pregunta puntual sobre la posibilidad de una orden verbal. |
| RAG-049 | 1 | 2 | 1 | Se describen las cuatro etapas, sin la apelación. El numeral 4 quedó bajo el rótulo del 3. |
| RAG-050 | 1 | 2 | 2 | Los numerales 1 y 2 respaldan las etapas iniciales. La referencia también pide audiencia, recursos y cumplimiento. |

Resultado de exactitud contra el banco, **4 completas, 9 parciales
y 1 retenida** entre las 14 llamadas. La fidelidad técnica de las 13
respuestas visibles corresponde a pasajes comprobados contra su
fuente; la selección de pasajes aún puede resultar parcial. Los
rótulos incompletos observados en RAG-002, RAG-027 y RAG-049 motivaron
la separación de numerales contiguos en la salida. El cambio pasó
una prueba local con el artículo 2. La tabla conserva las calificaciones
de lo realmente observado, previas a ese ajuste. La revisión jurídica
humana y una corrida representativa a escala del corpus completo
siguen pendientes.
