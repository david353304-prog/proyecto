# Hitos de publicación de la rama de trabajo

La evaluación de partida registró 32/50 aciertos, 29 completas, tres
parciales, 18 abstenciones y 26/26 trampas rechazadas. La huella de la
medición corresponde a 117 vectores públicos, no a los 96 del índice
anterior. La [auditoría de calidad](../motor_documental/pruebas/auditoria_hito_calidad_publicacion.json)
conserva las huellas y revisa una muestra de siete respuestas sobre los
29 casos sometidos a comprobación de citas.

La [propuesta versionada](../motor_documental/pruebas/propuesta_referencias_v1.json)
documenta que el art. 18 de la Ley 2450 establece multa tipo 4 para el
numeral 1 del art. 33 y conserva la condición de C-308/19. Los dos casos
se siguen puntuando contra el banco original. RAG-025 queda parcial
mientras no se concilien el artículo 180, el procedimiento 223A y UVB.

## Lote de relaciones con las autoridades

Se cotejaron los numerales 1, 2, 3 y 5 a 7 del artículo 35 contra las
capturas de Cancillería y Jurinfo del 18 de noviembre de 2026 y las
fuentes oficiales consultadas el 19. C-223/25 se inhibió respecto del
numeral 1. C-600/19 resolvió los cargos estudiados del numeral 2. Se
excluyó el numeral 4 porque D-16628 registra una inadmisión y falta
verificar su desenlace. Tampoco se incorporaron las filas de sanciones,
que estas dos preguntas no piden. Las citas no califican el hecho ni
el alcance de una crítica a la autoridad.

La [recuperación](../motor_documental/pruebas/recuperacion_hito_autoridades.json)
subió de 32 a 34 aciertos con 118 vectores de dimensión 384. P@5 pasó
de 0,128 a 0,136; Recall@5 y MRR de 0,64 a 0,68. En el
[control](../motor_documental/pruebas/control_hito_autoridades.json),
RAG-033 incluyó los numerales 1 y 2 y RAG-006 quedó parcial por el
numeral 4 excluido. Pasaron 116 pruebas Python y una quedó omitida.

[Compilación institucional](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#35)
· [C-223/25](https://www.corteconstitucional.gov.co/relatoria/2025/C-223-25.htm)
· [C-600/19](https://www.corteconstitucional.gov.co/relatoria/2019/C-600-19.htm)
· [Estado de D-16628](https://www.corteconstitucional.gov.co/secretaria/estados/estado-no.-110-10-de-julio-de-2025.pdf).

## Lote de integridad de niñas, niños y adolescentes

Se contrastaron los numerales 1–3, 5–6 y 8–11 del artículo 38 y sus
literales seleccionados, con la corrección del Decreto 555 de 2017,
artículo 4. El Auto 533/22 cita el numeral 5.b al tratar otro artículo.
Quedan excluidos los numerales 4 y 7, los parágrafos y las sanciones.
Las preguntas evaluadas describen conductas en abstracto. [Cancillería](https://cancilleria.gov.co/normograma/compilacion/docs/ley_1801_2016.htm#38)
· [Decreto 555](https://www.funcionpublica.gov.co/eva/gestornormativo/norma.php?i=80775)
· [Auto 533/22](https://www.corteconstitucional.gov.co/relatoria/autos/2022/a533-22.htm).

La recuperación llegó a 36/50. Precisión@5 fue 0,144. Recall@5 y MRR
fueron 0,72. El índice tiene 31 artículos y 127 vectores de dimensión 384.
RAG-008 y RAG-034 devolvieron 23 citas con fuente visible en los controles.
El expediente de ampliación conserva fecha, URL y SHA de cada bloque.

- Corpus `e1095acca700aa3c8d84b62e411c45f32a55c9bdf49ccbb6c46f6132d7459b55`
- FAISS `6ea62b8b5a1bfd00ae04bf487f5c2c46dea9b98e445f9d14d49bf535d7bf5eb7`
- Metadatos `dc7e02316f4ed234b46f14d103dacf2d6f256c1c10caec4ddadf09265d9b0073`

## Integración

Chrome comprobó las preguntas ampliadas, RAG-044 con 14 citas y dos
extractos, la abstención, la trampa tributaria, enlaces, historial,
reinicio, aviso y tratamiento de HTML no confiable. Los controles
HTTP y las pruebas Node conservaron la carga PDF sin reindexación.
Python ejecutó 118 pruebas con 117 aprobadas y una omitida. Node aprobó
26 de 26. El análisis lingüístico del corpus público arrojó 6.453
tokens, 1.499 tipos y relación de 0,2323. Las fuentes normativas
y la aprobación jurídica humana siguen siendo distintas del cotejo
automático de huellas y del resultado del chatbot.

## Evaluación final local

| Indicador | Inicial | Final |
| --- | ---: | ---: |
| Recuperación | 32/50 | 36/50 |
| Precisión@5 | 0,128 | 0,144 |
| Recall@5 y MRR | 0,64 | 0,72 |
| Completas | 29 | 32 |
| Parciales | 3 | 4 |
| Abstenciones | 18 | 14 |
| Retenidas y errores HTTP | 0 | 0 |
| Trampas rechazadas | 26/26 | 26/26 |

RAG-008, RAG-033 y RAG-034 fueron las tres completas adicionales.
Se comprobaron 325 citas literales que aparecen en las fuentes visibles
y corresponden al artículo esperado. RAG-006, RAG-005, RAG-025 y RAG-032
siguen parciales. El [comparativo](../motor_documental/pruebas/comparacion_50_hitos_publicacion.json)
registra los 50 IDs. El [inventario](../motor_documental/pruebas/pendientes_hitos_publicacion.json)
registra los bloqueos documentales de las 14 abstenciones restantes.

Cuatro de 36 consultas con Gemini superaron 10 s. RAG-007 tardó 10,781 s
tras un 503, RAG-008 tardó 41,892 s y RAG-009 22,452 s con un único
intento exitoso, y RAG-016 tardó 63,477 s tras un 504. La traza permite
separar recuperación, intentos, validación y HTTP total. El p95 HTTP fue
27,312 s. No quedó demostrado un defecto local que explique esas demoras.

La auditoría y la propuesta versionada se publicaron primero en los
commits `6755f78` y `0f8fbbb` de `trabajo/ley1801-hitos-verificables`.
La consolidación reúne en la misma rama el código, el corpus público,
el índice FAISS y la evidencia reproducible de los avances.
