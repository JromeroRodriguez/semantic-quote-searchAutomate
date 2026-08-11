# Motor de Búsqueda Semántica de Frases

Una aplicación web que devuelve las **3 frases semánticamente más relevantes** a partir de una descripción en texto libre de una situación, emoción o pensamiento. El sistema **no depende de coincidencia de palabras clave** — utiliza comprensión semántica profunda a través de embeddings y reranking.

## Arquitectura

```mermaid
graph LR
    A[Consulta del Usuario] --> B[FastAPI]
    B --> C[MiniLM Embeddings]
    C --> D[Índice FAISS]
    D --> E[Top 15 Candidatos]
    E --> F[Cross-Encoder ms-marco-MiniLM-L-6-v2]
    F --> G[Top 3 Frases]
    G --> H[Frontend]
```

Dos procesos separados:

1. **Preparación de Datos** (se ejecuta manualmente cuando se necesita):
   - `scripts/scrape_quotes.py` → `data/quotes.json`
   - `scripts/build_index.py` → `data/quotes.index` + `data/metadata.json`

2. **Búsqueda en Tiempo Real** (atiende peticiones del usuario):
   - FastAPI carga los modelos una sola vez al inicio
   - Genera embedding de la consulta → Recuperación de candidatos con FAISS → Reranking con BGE → Top 3

## Stack Tecnológico

| Componente | Tecnología |
|-----------|-----------|
| Backend | Python, FastAPI |
| Scraping | Playwright |
| Embeddings | `sentence-transformers/paraphrase-multilingual-MiniLM-L-12-v2` |
| Búsqueda Vectorial | FAISS (IndexFlatIP) |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| Frontend | CSS editorial personalizado, JavaScript vanilla |
| Dataset | JSON |

## Instalación

### 1. Clonar y configurar entorno

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
playwright install chromium
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env si es necesario
```

### 3. Extraer frases (scraping)

```bash
python scripts/scrape_quotes.py
```

Esto crea `data/quotes.json` con todas las frases de [quotes.toscrape.com](https://quotes.toscrape.com/).

### 4. Construir el índice FAISS

```bash
python scripts/build_index.py
```

Descarga el modelo MiniLM (~470MB) y genera los embeddings de todas las frases (~0.7s). Genera `data/quotes.index` y `data/metadata.json`.

### 5. Iniciar la aplicación

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

Abrir [http://localhost:8000](http://localhost:8000) en el navegador.

## Docker (Recomendado para Portabilidad)

### Inicio rápido

```bash
docker compose up --build
```

Abrir [http://localhost:8002](http://localhost:8002).

### Ejecutar en segundo plano

```bash
docker compose up -d
docker compose logs -f   # ver logs en tiempo real
docker compose down      # detener
```

### Prerrequisitos

- Docker Engine 20.10+ o Docker Desktop
- El usuario debe estar en el grupo `docker`: `sudo usermod -aG docker $USER` (luego cerrar y abrir sesión)
- Docker Desktop debe tener al menos **4GB de memoria** asignada (Settings → Resources)

## Variables de Entorno

| Variable | Valor por defecto | Descripción |
|----------|---------|-------------|
| `EMBEDDING_MODEL` | `sentence-transformers/paraphrase-multilingual-MiniLM-L-12-v2` | Modelo de embeddings |
| `RERANKER_MODEL` | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Modelo reranker |
| `TOP_K` | `15` | Candidatos recuperados de FAISS |
| `FINAL_RESULTS` | `3` | Resultados finales devueltos |
| `MAX_QUERY_LENGTH` | `500` | Longitud máxima de la consulta en caracteres |
| `QUOTES_PATH` | `data/quotes.json` | Ruta al dataset de frases |
| `FAISS_INDEX_PATH` | `data/quotes.index` | Ruta al índice FAISS |
| `METADATA_PATH` | `data/metadata.json` | Ruta al mapping de metadatos |
| `DEVICE` | automático | `cpu` o `cuda` |
| `MODEL_DTYPE` | `float32` | `float32`, `float16` o `bfloat16` |

## API

### Búsqueda

```
POST /api/v1/search
Content-Type: application/json

{"query": "Siento que todos avanzan mientras yo sigo estancado."}
```

Respuesta:

```json
{
  "results": [
    {"id": 1, "quote": "...", "author": "..."},
    {"id": 2, "quote": "...", "author": "..."},
    {"id": 3, "quote": "...", "author": "..."}
  ]
}
```

### Salud

```
GET /health
```

## Cómo Ejecutar el Scraper

```bash
python scripts/scrape_quotes.py                    # Sin ventana (por defecto)
python scripts/scrape_quotes.py --headed           # Mostrar ventana del navegador
python scripts/scrape_quotes.py -v                 # Logging detallado
python scripts/scrape_quotes.py -o custom.json     # Ruta de salida personalizada
```

## Cómo Construir el Índice FAISS

```bash
python scripts/build_index.py                      # Configuración por defecto
python scripts/build_index.py --batch-size 16      # Ajustar tamaño de lote
python scripts/build_index.py -v                   # Logging detallado
```

## Pruebas

```bash
python -m pytest tests/ -v                    # Ejecutar todas las pruebas
python -m pytest tests/test_api.py -v         # Solo pruebas de API
python -m pytest tests/test_integration.py -v # Solo pruebas de integración
```

## Benchmarking

```bash
python benchmarks/evaluate.py
```

Ejecuta 10 consultas representativas en diferentes categorías emocionales y mide la latencia y la calidad de recuperación.

## Rendimiento

| Métrica | Valor |
|---------|-------|
| Carga del modelo | ~3s |
| Embedding por query | ~0.016s |
| Búsqueda total | ~5s |
| Tamaño del modelo | 470MB |

## Estructura del Proyecto

```
├── backend/
│   └── app/
│       ├── main.py              # Punto de entrada FastAPI + lifespan
│       ├── api/routes/search.py # POST /api/v1/search
│       ├── core/
│       │   ├── config.py        # Configuración desde .env
│       │   └── logging.py       # Configuración de logging
│       ├── models/quote.py      # Modelo de dominio Quote
│       ├── schemas/search.py    # Schemas de request/response
│       ├── services/
│       │   ├── embeddings/jina_service.py
│       │   ├── search/faiss_service.py
│       │   ├── search/semantic_search_service.py
│       │   └── reranker/bge_service.py
│       ├── repositories/quote_repository.py
│       └── utils/text.py        # Normalización de texto compartida
├── scripts/
│   ├── scrape_quotes.py         # Preparación de datos: scraping
│   └── build_index.py           # Preparación de datos: indexación
├── frontend/
│   ├── index.html               # Interfaz editorial
│   └── src/
│       ├── main.js              # Lógica de la aplicación
│       ├── services/api.js      # Cliente API
│       └── styles/main.css      # Estilos editorial
├── data/
│   ├── quotes.json              # Dataset extraído
│   ├── quotes.index             # Índice FAISS
│   └── metadata.json            # Mapping frase ↔ índice
├── tests/                       # Suite de pruebas pytest
├── benchmarks/                  # Evaluación semántica
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## Limitaciones Conocidas

- **Inferencia solo en CPU**: La latencia promedio de búsqueda es ~5s en CPU. Con GPU se reduciría a <1s.
- **Recuperación multilingüe**: MiniLM soporta español nativamente. Los resultados son consistentes para consultas en español.
- **Tamaño del dataset**: 100 frases de quotes.toscrape.com. La arquitectura escala a datasets más grandes sin cambios.
- **Sin panel de administración**: Las actualizaciones del dataset requieren ejecutar los scripts manualmente.

