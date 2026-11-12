# Chatbot jurídico RAG — Ley 1801 de 2016

Proyecto de asistente jurídico basado en la Ley 1801 de 2016
(Código Nacional de Seguridad y Convivencia Ciudadana de Colombia).

El sistema utiliza recuperación de información documental (RAG)
para apoyar la generación de respuestas relacionadas con la norma.

> **Advertencia:** Este proyecto está en desarrollo. Sus respuestas
> deben contrastarse con el texto legal vigente y no sustituyen
> el asesoramiento de un profesional del derecho.

## 1. Arquitectura

El sistema está compuesto por:

- **Frontend:** interfaz web desarrollada con HTML, CSS y JavaScript.
- **Backend:** servidor Node.js con Express.
- **Puente Python:** comunicación entre la API y el motor documental.
- **Motor RAG:** recuperación documental y generación de respuestas.
- **FAISS:** búsqueda vectorial.
- **Sentence Transformers:** generación de representaciones semánticas.
- **Gemini:** modelo de lenguaje utilizado para generar respuestas.
- **Validación documental:** controles sobre la información recuperada.

Flujo general:

```text
Usuario
   |
Frontend
   |
POST /api/chat
   |
Backend Node.js
   |
Puente Python
   |
Motor documental RAG
   |
Respuesta pública
   |
Frontend
```

## 2. Requisitos

Entorno de referencia utilizado durante el desarrollo:

- Python 3.12.3.
- Node.js.
- npm.
- Acceso a las dependencias indicadas en `requirements.txt`.
- Credencial válida de Gemini para consultas reales al modelo.

El backend utiliza actualmente el intérprete Python ubicado en
`.venv/bin/python`. Por tanto, se debe crear el entorno virtual
con ese nombre en la raíz del repositorio.

## 3. Instalación de Python

Desde la raíz del proyecto:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Las versiones de `requirements.txt` corresponden al entorno
de desarrollo inspeccionado. La instalación desde cero
todavía requiere una prueba independiente.

## 4. Instalación de Node.js

Desde la raíz del proyecto:

```bash
cd backend
npm ci
```

El backend utiliza Express y cuenta con `package-lock.json`.

## 5. Configuración

El archivo `.env.example` documenta las variables utilizadas:

- `GEMINI_API_KEY`: credencial para acceder a Gemini.
- `PORT`: puerto del servidor; por defecto, `3000`.

La clave real debe configurarse como variable de entorno
o mediante los secretos de GitHub Codespaces.

No se deben publicar claves API ni credenciales reales.

**Nota:** `.env.example` es una referencia de configuración;
su presencia no implica que el servidor cargue automáticamente
un archivo `.env`.

## 6. Ejecución del chatbot

Desde la raíz del proyecto:

```bash
node backend/index.js
```

El servidor utiliza el puerto `3000` de forma predeterminada,
salvo que se configure otro mediante `PORT`.

En un entorno local, la interfaz puede abrirse en:

```text
http://localhost:3000
```

En GitHub Codespaces, utilizar la URL correspondiente
al puerto reenviado.

### Rutas de la API

- `GET /api/estado`: consulta del estado del servidor.
- `POST /api/chat`: envío de preguntas al motor documental.

El frontend se sirve desde la carpeta `frontend/`.

## 7. Pruebas automatizadas

### Validador jurídico

Desde la raíz del proyecto:

```bash
.venv/bin/python -m unittest discover -s tests -p "test_*.py" -q
```

### Selector documental

```bash
.venv/bin/python -m unittest discover -s motor_documental/pruebas -p "test_*.py" -q
```

### Seguridad HTTP

```bash
cd backend
npm test
```

En la última regresión completa registrada durante
el desarrollo aprobaron 55 pruebas:

- 38 del validador jurídico.
- 5 del selector documental.
- 12 de seguridad HTTP.

Estas pruebas no sustituyen una evaluación integral
con consultas reales a Gemini.

## 8. Estado y limitaciones

El proyecto continúa en desarrollo.

Pendiente de verificar o completar:

- Instalación reproducible en un entorno limpio.
- Integración completa entre frontend, backend y motor RAG.
- Pruebas reales de generación con Gemini.
- Evaluación de precisión jurídica y citas normativas.
- Revisión final de la experiencia de usuario.
- Preparación para despliegue y operación.

## 9. Seguridad

El backend incorpora controles sobre las solicitudes,
el procesamiento del motor Python y la respuesta pública.

Las pruebas HTTP incluyen escenarios de error,
tiempo de espera y límites de salida del proceso Python.

No se deben almacenar credenciales reales en Git.
