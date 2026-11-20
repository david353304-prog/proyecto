# Chatbot jurídico RAG de la Ley 1801 de 2016

Prototipo académico de consulta documental sobre el Código Nacional de Seguridad y Convivencia Ciudadana de Colombia. La interfaz presenta el historial de la conversación actual y permite desplegar fragmentos y fuentes. Las respuestas requieren verificación normativa y revisión jurídica.

En respuestas largas, el chat muestra el comienzo de la respuesta y
separa las conductas de las medidas correctivas cuando ambas aparecen.
Despliega **Ver fragmentos recuperados** para revisar el texto de respaldo
y abrir la fuente normativa en otra pestaña.

El índice público reúne apartados cotejados de 33 artículos y 132 vectores
de dimensión 384. Los 249 artículos del corpus histórico se conservan
como antecedente documental. El [alcance público actual y su auditoría](documentacion/documentacion_corpus.md#ampliación-de-medidas-correctivas-del-20-de-noviembre-de-2026)
documentan los apartados habilitados y sus exclusiones.
El [informe técnico final](output/pdf/informe_tecnico_final.pdf) resume
las comprobaciones obligatorias y el resultado de latencia.

```text
Navegador → Express → FastAPI → FAISS → Gemini → validación documental
              ↳ carga de PDFs → validación y extracción aisladas
```

## Instalación y ejecución

Usa Python 3.12 y Node.js 22 o posterior. Ejecuta desde la raíz del repositorio.

**Linux**

```bash
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
npm --prefix backend ci
```

**Windows PowerShell**

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
npm.cmd --prefix backend ci
```

Los comandos Python siguientes suponen el entorno virtual activo. En PowerShell puedes reemplazar `python` por `.\.venv\Scripts\python.exe`. La primera carga del modelo multilingüe requiere acceso a Hugging Face o una caché precargada.

Configura `GEMINI_API_KEY` en el entorno de FastAPI o en el `.env`
local a partir de `.env.example`. `PORT` cambia el puerto de Node,
que por defecto es 3000. `CORS_ORIGINS` admite orígenes exactos
separados por comas. Con el valor vacío, la interfaz funciona
desde el mismo origen.

En dos terminales, desde la raíz:

```bash
python -m uvicorn backend.servicio_rag:app --host 127.0.0.1 --port 8000
node backend/index.js
```

Abre `http://127.0.0.1:3000`. El servicio público consulta los
apartados cotejados del índice público. El alcance parcial por artículo
está documentado en la matriz de cobertura. El corpus histórico
permanece disponible para experimentos locales. Sin credencial, FastAPI
responde a los rechazos deterministas y devuelve HTTP 503 para consultas
que requieren generación. El servicio interno documenta sus
rutas en `http://127.0.0.1:8000/docs`.

Para aislar una corrida, fija `FASTAPI_PORT` en el entorno de Node
y usa el mismo número en `--port` al iniciar FastAPI. Node solo se
conecta a la dirección local. `GET /estado` de FastAPI indica el modo
documental y si la generación fue configurada.

## API pública

| Ruta | Solicitud | Respuesta |
|---|---|---|
| `GET /api/estado` | Sin cuerpo | HTTP 200 con estado del servidor Node. |
| `GET /estado` en FastAPI | Sin cuerpo | HTTP 200 con modo, disponibilidad de generación y SHA-256 del corpus público. |
| `POST /consultar` en FastAPI | JSON con `pregunta` de 1 a 2000 caracteres. | HTTP 200 con respuesta, validación y fuentes públicas. HTTP 400 si solo contiene espacios, 422 para JSON o campos inválidos, 503 si requiere generación y esta no está configurada, o 500 ante un fallo interno. |
| `POST /api/chat` | JSON con `pregunta` de 1 a 2000 caracteres tras recortar blancos. | HTTP 200 con `respuesta`, `fuentes_recuperadas` y, cuando corresponde, `validacion_documental`. HTTP 400 para pregunta inválida, 502 para error del motor, 503 para generación indisponible y 504 para tiempo agotado. |
| `POST /upload_pdf/` | Multipart con un archivo en el campo `documento`. Límite de 10 MiB. | HTTP 201 con nombre, tamaño, conteo de páginas con texto, caracteres e `indexado: false`. HTTP 400 para carga inválida, 413 para tamaño excedido y 422 si la validación o la extracción rechazan el PDF. |

```bash
curl -H 'Content-Type: application/json' -d '{"pregunta":"¿Qué es un comparendo?"}' http://127.0.0.1:3000/api/chat
curl -F 'documento=@documento.pdf' http://127.0.0.1:3000/upload_pdf/
```

La carga de PDF tiene un directorio independiente y realiza validación y extracción local. El índice de recuperación se prepara de forma independiente y conserva el corpus de la Ley 1801.

## Pruebas y evaluación

```bash
python -m unittest discover -s tests
python -m unittest discover -s motor_documental/pruebas -p "test_*.py"
npm --prefix backend test
python -m motor_documental.analisis.analisis_linguistico_corpus
python -m motor_documental.analisis.analisis_linguistico_corpus --publicable --salida linguistica_publica.json
python -m motor_documental.corpus.conciliar_diferencias --salida conciliacion.json
python -m motor_documental.corpus.verificar_ampliacion ley1801-jep.html --salida evidencia_ampliacion.json
python -m motor_documental.pruebas.auditar_evidencia
python -m motor_documental.pruebas.comparar_recuperacion --salida comparacion.json
python -m motor_documental.indice_publicable
python -m motor_documental.pruebas.comparar_recuperacion --publicable --salida comparacion_publicable.json
python -m motor_documental.pruebas.cobertura_banco_final
python -m motor_documental.pruebas.evaluar_api --salida evaluacion_http.json
```

Ejecuta la evaluación HTTP con ambos servidores activos. Con credencial, conserva las respuestas observadas, los tiempos y los artículos esperados para revisión con la escala de `motor_documental/pruebas/rubrica_evaluacion_respuestas.json`. El indicador de diez segundos se mide en consultas exitosas del banco que invocaron Gemini. Los rechazos deterministas y fuera de dominio se reportan por separado.

El índice público se distribuye en `motor_documental/embeddings/`
y se regenera con el comando anterior si cambia el corpus cotejado.
El servicio valida las huellas del corpus y del índice antes de cargar
el modelo. La opción `--publicable` usa el índice y el enrutamiento
del servicio. El comparador sin esa opción se reserva al experimento
histórico.

Consulta la [matriz de revisión](documentacion/revision_entrega.md), el
[contraste normativo](documentacion/documentacion_corpus.md) y el
[informe lingüístico](documentacion/informe_analisis_linguistico.md).

La [matriz de entrega](documentacion/revision_entrega.md) documenta el
alcance público ensayado y separa las métricas históricas. Para medir
HTTP con Gemini, ejecuta FastAPI y Node como se indica arriba y usa
`python -m motor_documental.pruebas.evaluar_api --estado-motor http://127.0.0.1:8000/estado --salida evaluacion_http.json`.
Indica `--url` si Node usa otro puerto y ajusta `FASTAPI_PORT` para
que Node apunte al mismo motor que verifica el evaluador. La consulta
de estado compara la huella del corpus y comprueba si la generación
está configurada antes de evaluar el banco.

### Verificar la entrega

```powershell
$py = ".venv/Scripts/python.exe"
& $py -m motor_documental.pruebas.auditar_cierre --salida auditoria.json
& $py -m motor_documental.pruebas.comparar_recuperacion --publicable --salida recuperacion.json
& $py -m motor_documental.analisis.evaluar_muestra_entidades --salida entidades.json
& $py -m motor_documental.analisis.analisis_linguistico_corpus --publicable --salida linguistica.json
& $py -m unittest discover -s tests
npm.cmd --prefix backend test
```

El control de navegador usa Chromium local y respuestas simuladas.
`node motor_documental/pruebas/verificar_interfaz_cierre.cjs RUTA_CHROME interfaz.json`.
El informe separa la última corrida real de Gemini de las comprobaciones
deterministas posteriores. [Evaluación de cierre](documentacion/evaluacion_cierre.md)
La [auditoría de urbanismo y Gemini](documentacion/auditoria_urbanismo_gemini.md)
registra la cobertura, la evaluación por respuesta y los resultados de
la última medición HTTP.
