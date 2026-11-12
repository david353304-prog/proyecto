# Informe de análisis lingüístico

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
