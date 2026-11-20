# Informe de análisis lingüístico

## Reproducción y resultados ampliados

Desde la raíz, con el entorno virtual activo, ejecuta
`python -m motor_documental.analisis.analisis_linguistico_corpus`.
Se usó spaCy 3.8.18 con `es_core_news_sm` 3.8.0. El
[`resultados_linguisticos.json`](../motor_documental/analisis/resultados_linguisticos.json)
registra las versiones y el SHA-256 del corpus realmente procesado.
El análisis usa los 249 artículos del corpus histórico del chatbot
para conservar comparabilidad con el informe del grupo.

El JSON incluye bigramas y trigramas de formas en minúscula, frecuencias
de formas y lemas, distribución POS, entidades del modelo general y
un conjunto de patrones explícitos para autoridades, lugares, montos
y plazos. Los patrones tienen cobertura parcial. Los recuentos son
ocurrencias textuales y pueden incluir notas editoriales del PDF.

Las colocaciones se calculan como PMI sobre pares de tokens consecutivos
dentro de cada artículo, después de excluir espacios y puntuación.
Se incluyen pares con al menos cinco ocurrencias y con una de las
formas `multa`, `comparendo`, `medida` o `espacio`. La PMI mide
asociación en el corpus y favorece pares menos frecuentes.

Las concordancias KWIC incluyen hasta cinco coincidencias por término,
con artículo, contexto izquierdo, término central y contexto derecho.
La detección exige límites de palabra. El JSON es la evidencia
reproducible más reciente. Las tablas y ejemplos de las secciones
siguientes corresponden al informe original.

## 1. Objetivo

Caracterizar lingüísticamente el corpus utilizado por el chatbot jurídico RAG basado en la Ley 1801 de 2016.

## 2. Corpus analizado

- Artículos registrados: 249.
- Artículos con texto: 249.
- Archivo: `motor_documental/corpus/articulos_ley_1801.json`.
- Idioma: español.

## 3. Metodología

Se utilizó Python y spaCy con el modelo `es_core_news_sm` para tokenización, lematización, etiquetado gramatical (POS) y reconocimiento de entidades (NER).

Las frecuencias se calcularon sobre los textos de los artículos. Se aplicó conversión a minúsculas para el conteo de palabras y expresiones.

Se excluyeron espacios y signos de puntuación del conteo principal de tokens. Para las frecuencias de lemas se excluyeron palabras vacías.

## 4. Estadísticas generales

| Indicador | Resultado |
|---|---:|
| Artículos | 249 |
| Tokens | 53943 |
| Tipos léxicos | 5059 |
| Relación tipo/token | 0.0938 |
| Longitud media por artículo | 216.64 tokens |

La relación tipo/token representa la proporción de formas diferentes respecto al total de tokens. Su interpretación depende del tamaño del corpus.

## 5. Frecuencias léxicas

| Lema | Frecuencia |
|---|---:|
| actividad | 490 |
| público | 448 |
| policía | 389 |
| artículo | 377 |
| numeral | 361 |
| multa | 353 |
| autoridad | 301 |
| medida | 296 |
| comportamiento | 288 |
| general | 284 |
| parágrafo | 280 |
| tipo | 264 |
| 2 | 250 |
| 4 | 246 |
| 1 | 231 |

## 6. Categorías gramaticales (POS)

| Categoría | Frecuencia |
|---|---:|
| NOUN | 13258 |
| ADP | 9995 |
| DET | 6973 |
| ADJ | 5592 |
| PROPN | 4733 |
| VERB | 3686 |
| CCONJ | 3004 |
| NUM | 2392 |
| PRON | 1940 |
| ADV | 929 |
| AUX | 852 |
| SCONJ | 535 |
| SYM | 44 |
| PUNCT | 8 |
| INTJ | 1 |
| PART | 1 |

## 7. Reconocimiento de entidades (NER)

Se presentan las entidades más frecuentes detectadas automáticamente por el modelo.

| Entidad | Etiqueta | Frecuencia |
|---|---|---:|
| Policía | PER | 220 |
| la Ley | LOC | 89 |
| Suspensión | LOC | 66 |
| Código | MISC | 61 |
| PARÁGRAFO 1 | MISC | 61 |
| Sentencia de la Corte Constitucional | MISC | 58 |
| PARÁGRAFO 2 | MISC | 50 |
| PARÁGRAFO | ORG | 46 |
| Suspensión | PER | 43 |
| Policía Nacional | MISC | 40 |

Las etiquetas son resultados automáticos y no constituyen una validación jurídica de las entidades.

## 8. Expresiones jurídicas frecuentes

| Expresión | Apariciones |
|---|---:|
| medida correctiva | 68 |
| multa general | 235 |
| autoridad de policía | 50 |
| espacio público | 62 |
| orden de comparendo | 13 |
| comportamientos contrarios a la convivencia | 22 |

Estas cifras corresponden a ocurrencias textuales de expresiones seleccionadas, no a una medida estadística de asociación entre palabras.

## 9. Concordancias

Se obtuvieron ejemplos de contexto para los siguientes términos:

### multa

Ejemplos encontrados: 5.

- «rrectivas: COMPORTAMIENTOS MEDIDA CORRECTIVA A APLICAR Numeral 1 Multa General tipo 2 Numeral 2 Amonestación; Participación en programa»
- «ama comunitario o actividad pedagógica de convivencia. Numeral 3 Multa General tipo 3. Numeral 4 Participación en programa comunitario»
- «n en programa comunitario o actividad pedagógica de convivencia; Multa General tipo 2. Numeral 5 Construcción, cerramiento, reparación»

### comparendo

Ejemplos encontrados: 5.

- «ención al motivo de policía in situ quedará plasmado en orden de comparendo o en sala de mediación policial, se dejará constancia de todo lo»
- «o, que admita la imposición de multa general, impondrán orden de comparendo al infractor, evidenciando el hecho. Es deber de toda persona na»
- «urante los cinco (5) días hábiles siguientes a la expedición del comparendo, se le disminuirá el valor de la multa en un cincuenta (50%) por»

### medida correctiva

Ejemplos encontrados: 5.

- «ambién constituya una conducta tipificada en el Código Penal, la medida correctiva a imponer no podrá tener la misma naturaleza que la sanción prev»
- «plicación de las siguientes medidas correctivas: COMPORTAMIENTOS MEDIDA CORRECTIVA A APLICAR Numeral 1 Multa General tipo 2 Numeral 2 Amonestación;»
- «aplicación de las siguientes medidas correctivas: COMPORTAMIENTOSMEDIDA CORRECTIVA A APLICAR Numeral 1 Multa General tipo 3; Remoción de bienes, De»

### espacio público

Ejemplos encontrados: 5.

- «la comunidad comportamientos que favorezcan la convivencia en el espacio público, áreas comunes, lugares abiertos al público o que siendo privado»
- «gente. 2. Salvo actos circenses, prender o manipular fuego en el espacio público, lugar abierto al público, sin contar con la autorización del al»
- «privados: 1. Bienes muebles o inmuebles que se encuentran en el espacio público, en lugar privado abierto al público o utilizados para fines soc»

## 10. Glosario jurídico orientativo

| Término | Explicación | Consulta coloquial |
|---|---|---|
| comparendo | Orden relacionada con un procedimiento de policía. | Me pusieron un comparendo, ¿qué hago? |
| multa | Medida correctiva de carácter económico. | ¿Cuánto tengo que pagar? |
| medida correctiva | Medida contemplada por el Código Nacional de Seguridad y Convivencia Ciudadana. | ¿Qué me puede pasar si incumplo una norma? |
| espacio público | Espacios destinados al uso y disfrute colectivo. | ¿Puedo hacer esto en la calle o en un parque? |
| autoridad de policía | Autoridad con competencias establecidas en el Código. | ¿Quién puede intervenir o imponer una medida? |

Las explicaciones son orientativas y requieren contraste con los artículos correspondientes antes de considerarse definiciones jurídicas verificadas.

## 11. Limitaciones

- El modelo de español es general y puede clasificar incorrectamente entidades jurídicas.
- El análisis depende del contenido y la cobertura del corpus JSON disponible.
- Las expresiones seleccionadas no representan un análisis estadístico de colocaciones.
- Las concordancias son muestras limitadas.
- El glosario no sustituye las definiciones legales.

## 12. Conclusiones

El análisis permitió cuantificar las características léxicas y gramaticales del corpus, identificar términos recurrentes y documentar expresiones relacionadas con consultas de convivencia ciudadana.

Los resultados sirven como evidencia del procesamiento lingüístico realizado para el prototipo académico. Las etiquetas automáticas y las explicaciones jurídicas deben interpretarse considerando las limitaciones documentadas.
# Resultados del 19 de noviembre de 2026

spaCy 3.8.18 con `es_core_news_sm` 3.8.0 procesó 21 artículos públicos
total o parcialmente seleccionados, 1.800 tokens y 589 tipos.
TTR 0,3272. La media es de 85,71 tokens por artículo y 54,97 por
fragmento FAISS, contando tokens spaCy sin espacios ni signos de
puntuación. El histórico reanalizado conserva 249 artículos, 53.943
tokens, 5.059 tipos, TTR 0,0938 y 216,64 tokens por artículo.

Las reglas conservan «cuarenta y ocho (48) horas» como una unidad y
excluyen edades señaladas por «menor/mayor de» o «años de edad».
Las reglas son heurísticas. Falta medir la precisión de las entidades
con una muestra anotada. El subconjunto público no produjo
pares PMI por encima del umbral de frecuencia del script.

```bash
python -m motor_documental.analisis.analisis_linguistico_corpus --publicable --salida linguistica_publica.json
python -m motor_documental.analisis.analisis_linguistico_corpus --salida linguistica_historica.json
```

[JSON público](../motor_documental/analisis/resultados_linguisticos_final.json) ·
[JSON histórico reanalizado](../motor_documental/analisis/resultados_linguisticos_historico_reanalizado.json)
# Análisis del corpus entregado

La nueva ejecución usó spaCy 3.8.18 y `es_core_news_sm` 3.8.0. El público comprende 28 artículos y 63 ventanas. Los 2.975 tokens, 844 tipos y TTR de 0,2837 se calcularon por artículo sin contar el solapamiento de las ventanas. La media es de 106,25 tokens por artículo y 55,30 por ventana. El histórico se midió por separado con 249 artículos, 53.943 tokens, 5.059 tipos, TTR de 0,0938 y media de 216,64 tokens por artículo. [Estadísticas públicas](../motor_documental/analisis/resultados_linguisticos_cierre_publico.json) · [Estadísticas históricas](../motor_documental/analisis/resultados_linguisticos_cierre_historico.json)

La muestra anotada incluye 11 ejemplos redactados para cubrir un pasaje basado en el artículo 36 y casos contrastivos de lugares, autoridades, montos, plazos y edades. Se compara cada mención exacta, con minúsculas y conservando el número de ocurrencias. Antes se hallaron 13 de 15 menciones y quedaron fuera Instituto Colombiano de Bienestar Familiar y Ministerio Público. Tras añadir sus nombres, se hallaron 15 de 15 con cero falsos positivos. La exhaustividad de autoridades subió de 3/5 a 5/5. La muestra comprueba regresiones puntuales y su tamaño no permite estimar la calidad global del NER. [Muestra y etiquetas](../motor_documental/analisis/muestra_entidades.json) · [Antes](../motor_documental/analisis/evaluacion_entidades_antes.json) · [Después](../motor_documental/analisis/evaluacion_entidades_despues.json)

Los JSON incluyen frecuencias, lemas, POS, entidades, n-gramas, colocaciones y KWIC de multa, comparendo, medida correctiva y espacio público. Los valores vacíos de KWIC o de colocaciones indican falta de ocurrencias o de frecuencia suficiente en el texto analizado. El glosario recoge formulaciones orientadas a búsqueda a partir de los términos del Código. Por ejemplo, una consulta coloquial sobre «una multa» puede referirse a una orden de comparendo o a una medida. La aplicación conserva esa diferencia documental.

```powershell
$py = ".venv/Scripts/python.exe"
& $py -m motor_documental.analisis.evaluar_muestra_entidades --salida entidades.json
& $py -m motor_documental.analisis.analisis_linguistico_corpus --publicable --salida publico.json
& $py -m motor_documental.analisis.analisis_linguistico_corpus --salida historico.json
```
## Corpus público de la revisión por hitos

El [análisis de esta revisión](../motor_documental/analisis/resultados_linguisticos_hitos_publicacion.json)
se ejecutó sobre 31 artículos del corpus público con 6.453 tokens y 1.499 tipos.
La relación tipo/token fue 0,2323 y la longitud media fue de 208,16 tokens.
