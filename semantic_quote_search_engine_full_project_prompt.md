# Semantic Quote Search Engine — Full Project Implementation Prompt

## Role

Act as a **Senior Python Full-Stack AI/ML Engineer and Software Architect**.

You must develop a modular web application that implements a semantic quote search engine.

The project already contains a prototype scraper based on **Python + Playwright** that extracts quotes and authors from:

```text
https://quotes.toscrape.com/
```

Before changing anything, inspect the existing project and reuse/refactor the current scraper where appropriate. Do not discard working functionality without a technical reason.

---

# 1. Project Objective

Build a web application where the user can describe:

- A personal situation
- An emotion
- A feeling
- An abstract thought
- A problem
- A moment of reflection

Examples:

```text
I feel like time is moving too fast and I am not achieving my goals.

The feeling of peace I get when I watch the rain.

I feel like everyone is moving forward while I remain stuck.

Sometimes I wonder if the life I built is really the life I wanted.
```

The system must return the **3 quotes from the quote dataset that are most semantically relevant** to the user's situation.

The most important requirement is:

> The system must NOT depend on keyword matching.

A quote can be considered highly relevant even when the user's query and the quote do not share any significant words.

---

# 2. Important Architectural Decision

There is **NO LLM in the final architecture**.

Do NOT use:

```text
Llama
Qwen
GPT
Claude
Gemini
OpenAI API
Any cloud LLM
```

The previous LLM experimentation was only a benchmark and is no longer part of the project.

The semantic understanding must be achieved through:

```text
Jina Embeddings v3
+
FAISS
+
BGE Reranker v2-m3
```

---

# 3. Final Technology Stack

Use:

```text
Backend:
Python
FastAPI

Scraping:
Playwright

Dataset:
JSON

Semantic Embeddings:
jinaai/jina-embeddings-v3

Vector Search:
FAISS

Reranker:
BAAI/bge-reranker-v2-m3

Frontend:
Tailwind CSS — current stable version
JavaScript or TypeScript as appropriate

API:
REST / JSON
```

Do not introduce unnecessary frameworks or services.

---

# 4. High-Level Architecture

The system must have two clearly separated processes.

## Process A — Dataset Preparation

This process is NOT executed for every user search.

```text
quotes.toscrape.com
        │
        ▼
     Playwright
        │
        ▼
Extract quotes + authors
        │
        ▼
Validation / Cleaning
        │
        ▼
Deduplication
        │
        ▼
quotes.json
        │
        ▼
Jina Embeddings v3
        │
        ▼
FAISS index
```

The scraper is a data preparation process.

It should NOT run every time a user enters a query.

---

# 5. Runtime Search Process

When the user performs a search:

```text
User
 │
 ▼
Web Interface
 │
 ▼
FastAPI
 │
 ▼
Jina Embeddings v3
 │
 ▼
FAISS
 │
 ▼
Top N semantic candidates
 │
 ▼
BGE Reranker v2-m3
 │
 ▼
Top 3 quotes
 │
 ▼
FastAPI
 │
 ▼
Frontend
```

The scraper must NOT execute during this process.

The system must NOT regenerate embeddings for all quotes during a search.

---

# 6. Existing Scraper

The current project already contains a Playwright-based scraper.

Inspect the existing implementation first.

The current scraper extracts data conceptually equivalent to:

```python
{
    "author": "...",
    "phrase": "..."
}
```

Reuse the existing extraction logic where possible.

Refactor it into a dedicated modular service/script instead of keeping the entire implementation inside a notebook.

The scraper must support:

- Pagination
- Quote extraction
- Author extraction
- Basic validation
- Duplicate detection
- JSON export
- Logging
- Error handling

The output should be:

```text
data/quotes.json
```

Example:

```json
[
  {
    "id": 1,
    "author": "Albert Einstein",
    "quote": "..."
  },
  {
    "id": 2,
    "author": "J.K. Rowling",
    "quote": "..."
  }
]
```

Keep the original source information when useful.

---

# 7. Dataset Preparation

Create a separate indexing process.

Example:

```text
scripts/
    scrape_quotes.py
    build_index.py
```

The indexing process should:

1. Read `quotes.json`.
2. Validate records.
3. Normalize text for embedding.
4. Detect duplicates.
5. Generate embeddings using Jina Embeddings v3.
6. Build a FAISS index.
7. Save the index to disk.
8. Save metadata needed to map FAISS results back to quotes.

Example:

```text
data/
├── quotes.json
├── quotes.index
└── metadata.json
```

Do not regenerate the index during every API request.

---

# 8. Embedding Strategy

Use:

```text
jinaai/jina-embeddings-v3
```

Use the appropriate retrieval task configuration.

For quote documents/passages:

```text
retrieval.passage
```

For user queries:

```text
retrieval.query
```

The embedding model must represent semantic meaning rather than keywords.

Example:

```text
Query:
I feel like everyone is moving forward while I remain stuck.

Potential relevant quote:
Do not compare the pace of your journey with someone walking a different path.
```

The system should be capable of recognizing this relationship even with low lexical overlap.

---

# 9. FAISS Vector Search

Use FAISS for the first implementation.

Do not introduce Qdrant unless the project requirements later justify it.

FAISS should retrieve an initial candidate set.

Recommended initial configuration:

```text
TOP_K = 20 or 30
FINAL_RESULTS = 3
```

Make these values configurable.

The initial vector search is not the final ranking.

Its purpose is candidate retrieval.

---

# 10. Reranking

Use:

```text
BAAI/bge-reranker-v2-m3
```

The reranker receives:

```text
User query
+
Top 20/30 FAISS candidates
```

It evaluates the relevance of each candidate.

Then select:

```text
TOP 3
```

The final ranking should consider semantic and contextual relevance.

Do not return the raw FAISS ranking directly.

---

# 11. No Keyword Search

This is a strict project requirement.

Do NOT implement:

```text
Keyword search
LIKE
ILIKE
contains()
TF-IDF
BM25
Regex-based retrieval
Keyword fallback
Exact text matching as the retrieval mechanism
```

The retrieval pipeline must remain:

```text
Embedding
→ Vector similarity
→ Reranking
→ Top 3
```

---

# 12. Frontend

Build a clean, modern and responsive web interface using:

```text
Tailwind CSS
```

Do not create an admin panel.

The application is focused on the end-user search experience.

The main page should contain:

### Hero / Search Area

A clear title explaining the purpose of the application.

Example:

```text
Find the words that fit what you're feeling.
```

A large textarea:

```text
What are you feeling or thinking?
```

Example placeholder:

```text
Describe a situation, emotion, or thought...
```

A primary button:

```text
Find quotes
```

The UI should clearly communicate that the user can write naturally and does not need to enter keywords.

---

# 13. Results Interface

Display exactly 3 quote cards when sufficient results exist.

Each card should contain:

```text
Quote
Author
```

Optionally display a subtle relevance indicator if appropriate.

Do not expose internal model scores directly unless there is a clear UX reason.

The results should feel like recommendations rather than raw search-engine results.

---

# 14. UX States

The frontend must handle:

### Empty state

Before searching:

```text
Describe what you're feeling, thinking, or experiencing.
```

### Loading state

While processing:

```text
Finding the quotes that best connect with your thought...
```

Use an elegant loading animation.

### Success state

Display the 3 recommended quotes.

### No results

Show a friendly message explaining that no sufficiently relevant quotes were found.

### Error state

Show a clear user-friendly message without exposing stack traces.

---

# 15. Frontend Architecture

Keep frontend code modular.

Do not put the entire application in one HTML file if the implementation becomes complex.

Suggested structure:

```text
frontend/
├── src/
│   ├── components/
│   ├── services/
│   ├── utils/
│   ├── styles/
│   └── main.*
├── public/
└── package.json
```

If a lightweight vanilla JavaScript implementation is technically more appropriate, maintain the same separation of concerns.

Do not introduce React solely for the sake of using React.

Choose the simplest frontend architecture that provides a professional UX.

---

# 16. FastAPI Architecture

Use a modular backend.

Suggested structure:

```text
backend/
└── app/
    ├── main.py
    │
    ├── api/
    │   └── routes/
    │       └── search.py
    │
    ├── core/
    │   ├── config.py
    │   └── logging.py
    │
    ├── models/
    │   └── quote.py
    │
    ├── schemas/
    │   └── search.py
    │
    ├── services/
    │   ├── embeddings/
    │   │   └── jina_service.py
    │   │
    │   ├── search/
    │   │   └── faiss_service.py
    │   │
    │   └── reranker/
    │       └── bge_service.py
    │
    └── repositories/
        └── quote_repository.py
```

Maintain clear separation of concerns.

Do not create a monolithic `main.py`.

---

# 17. API Endpoint

Create:

```http
POST /api/v1/search
```

Request:

```json
{
  "query": "I feel like everyone is moving forward while I remain stuck."
}
```

Response:

```json
{
  "results": [
    {
      "id": 1,
      "quote": "...",
      "author": "..."
    },
    {
      "id": 2,
      "quote": "...",
      "author": "..."
    },
    {
      "id": 3,
      "quote": "...",
      "author": "..."
    }
  ]
}
```

The backend must never invent quote content or authors.

Every result must originate from `quotes.json`.

---

# 18. Configuration

Use environment variables.

Create:

```text
.env.example
```

Possible configuration:

```env
EMBEDDING_MODEL=jinaai/jina-embeddings-v3
RERANKER_MODEL=BAAI/bge-reranker-v2-m3

TOP_K=30
FINAL_RESULTS=3

FAISS_INDEX_PATH=data/quotes.index
QUOTES_PATH=data/quotes.json
METADATA_PATH=data/metadata.json
```

Do not hardcode configurable paths or model settings.

---

# 19. Performance

The runtime search must NOT perform unnecessary work.

During a user search:

```text
DO:
✓ Embed one query
✓ Search existing FAISS index
✓ Rerank retrieved candidates
✓ Return 3 results
```

DO NOT:

```text
✗ Scrape the website
✗ Rebuild the FAISS index
✗ Re-embed all quotes
✗ Re-download the dataset
```

Load the embedding model, reranker and FAISS index once during application startup where practical.

Do not instantiate expensive ML models for every request.

---

# 20. Performance Instrumentation

Measure:

```text
query_embedding_time
faiss_search_time
reranking_time
total_search_time
```

Log structured performance information.

Example:

```text
[PERF]
embedding: 0.080s
faiss: 0.010s
reranker: 0.220s
total: 0.310s
```

The exact numbers are not predetermined.

Benchmark the actual implementation.

---

# 21. Deduplication

During dataset preparation:

- Trim whitespace.
- Normalize repeated whitespace.
- Normalize Unicode where appropriate.
- Normalize quotation marks where appropriate.
- Detect duplicate quote text.
- Preserve the original display text.

Do not duplicate the same quote in the vector index.

---

# 22. Error Handling

Handle:

- Invalid query
- Empty query
- Missing dataset
- Missing FAISS index
- Model loading errors
- Embedding errors
- Reranker errors
- Corrupted index
- Invalid JSON
- API errors
- Scraping failures
- Network failures

Return appropriate HTTP status codes.

Do not expose internal stack traces to users.

---

# 23. Logging

Use Python logging with structured and useful messages.

Log:

```text
Application startup
Model loading
Index loading
Search request
Search latency
Number of retrieved candidates
Number of final results
Scraping progress
Indexing progress
Errors
```

Avoid unnecessarily logging the complete user query.

---

# 24. Testing

Create tests for:

### Scraper

- Quote extraction
- Author extraction
- Pagination
- Deduplication

### Dataset

- Valid JSON
- Required fields
- Duplicate handling

### Embeddings

- Query embedding generation
- Passage embedding generation

### FAISS

- Index creation
- Index loading
- Candidate retrieval

### Reranker

- Candidate ranking
- Top 3 selection

### API

- Valid request
- Empty request
- Invalid request
- Successful response
- Error handling

### Integration

Test the complete flow:

```text
User Query
→ Embedding
→ FAISS
→ Reranker
→ Top 3
```

---

# 25. Benchmark Dataset

Create a small test set containing different types of user input:

```text
1. Personal frustration
2. Lack of motivation
3. Feeling stuck
4. Existential doubt
5. Anxiety about the future
6. Loneliness
7. Failure
8. Personal growth
9. Peace and tranquility
10. Reflection
```

Use this dataset to evaluate whether the returned quotes actually match the meaning of the query.

The central metric is not keyword overlap.

Evaluate:

```text
Semantic relevance
Emotional relevance
Contextual relevance
Ranking quality
Latency
```

---

# 26. Important Cross-Language Consideration

The scraped quotes from `quotes.toscrape.com` are primarily in English, while users may enter queries in Spanish.

Do NOT assume cross-language retrieval works perfectly.

Explicitly test cases such as:

```text
Spanish query:
"Siento que todos avanzan mientras yo sigo estancado."

English quote:
"Do not compare the pace of your journey with someone walking a different path."
```

Validate the actual behavior of:

```text
Jina Embeddings v3
+
BGE Reranker v2-m3
```

If cross-language relevance is weak, document the problem and propose a solution before replacing the selected models.

Do not silently introduce a translation LLM.

---

# 27. Data Source

The primary data source for the challenge is the scraped quote dataset.

The application must use the generated dataset as its source of truth.

Do not fetch quotes from external APIs during runtime.

Do not generate quotes using AI.

Do not fabricate authors.

---

# 28. Scraping Frequency

Scraping is a separate preparation task.

The user search flow must NEVER trigger scraping.

For the current version:

```text
scrape_quotes.py
        ↓
quotes.json
        ↓
build_index.py
        ↓
FAISS index
        ↓
FastAPI application
```

If the dataset needs updating, run the scraping/indexing process manually.

Do NOT create an admin panel at this stage.

---

# 29. Dependency Management

Use a clean Python environment.

Separate runtime dependencies from development dependencies if appropriate.

Document installation commands.

The project should be reproducible from a clean environment.

---

# 30. Documentation

Create a complete `README.md` containing:

1. Project description
2. Architecture
3. Technology stack
4. Installation
5. Environment variables
6. How to scrape quotes
7. How to build the FAISS index
8. How to start FastAPI
9. How to start the frontend
10. API documentation
11. Testing
12. Benchmarking
13. Project structure
14. Known limitations

Include architecture diagrams using Mermaid where useful.

---

# 31. Modular Design Requirement

This is a strict engineering requirement.

The application must be modular.

Avoid:

```text
One giant Python file
One giant frontend file
Duplicated logic
Global mutable state
Hardcoded configuration
Tightly coupled services
```

Each component should have one clear responsibility.

For example:

```text
Scraper
    → only collects data

Dataset service
    → validates and normalizes data

Embedding service
    → generates embeddings

FAISS service
    → performs vector retrieval

Reranker service
    → ranks candidates

Search service
    → orchestrates the complete search pipeline

API route
    → handles HTTP requests

Frontend
    → handles presentation and user interaction
```

Use dependency injection or clean service composition where appropriate.

---

# 32. Startup Behavior

On application startup:

1. Load configuration.
2. Load required models.
3. Load FAISS index.
4. Load quote metadata.
5. Validate that all required resources exist.
6. Fail clearly if required resources are missing.

Do not rebuild the index automatically during normal API startup unless explicitly configured.

---

# 33. Search Service

Create a dedicated orchestration service.

Conceptually:

```python
class SemanticSearchService:

    def search(self, query: str):
        query_embedding = self.embedding_service.embed_query(query)

        candidates = self.faiss_service.search(
            query_embedding,
            top_k=self.top_k
        )

        ranked = self.reranker_service.rerank(
            query,
            candidates
        )

        return ranked[:3]
```

This is an architectural example, not a requirement to use this exact implementation.

The important requirement is separation of responsibilities.

---

# 34. Security and Validation

Validate user input.

Apply reasonable:

- Maximum query length
- Empty input validation
- Request validation
- Error handling

Do not unnecessarily store user queries.

Do not expose model internals.

---

# 35. Development Order

Implement in this order:

## Phase 1 — Inspect Existing Project

- Inspect current repository.
- Inspect the existing scraper.
- Identify reusable code.
- Identify technical debt.
- Do not rewrite working code unnecessarily.

## Phase 2 — Refactor Scraper

Extract the notebook logic into a modular Python scraper.

Generate:

```text
data/quotes.json
```

## Phase 3 — Build Embedding Pipeline

Implement Jina Embeddings v3.

Create:

```text
scripts/build_index.py
```

Generate the FAISS index.

## Phase 4 — Implement Semantic Search

Implement:

```text
Jina
→ FAISS
→ BGE Reranker
→ Top 3
```

Test it from Python before adding the web interface.

## Phase 5 — FastAPI

Expose the search engine through:

```text
POST /api/v1/search
```

## Phase 6 — Frontend

Implement the Tailwind interface.

Connect it to FastAPI.

## Phase 7 — Testing and Benchmarking

Test the complete application.

Measure latency.

Evaluate semantic relevance.

## Phase 8 — Documentation and Cleanup

Finish README, tests, configuration and project cleanup.

---

# 36. Critical Success Criterion

The application is successful only if it demonstrates semantic retrieval beyond lexical overlap.

Example:

### User:

```text
I feel like everyone is moving forward while I remain stuck.
```

### Relevant quote:

```text
Do not compare the pace of your journey with someone walking a different path.
```

Even if the two texts do not share meaningful words, the system should recognize their semantic relationship.

This is the central requirement of the entire project.

---

# 37. Final Instructions to the AI Agent

Before implementing:

1. Inspect the existing project.
2. Inspect the current Playwright scraper.
3. Identify reusable code.
4. Identify necessary refactoring.
5. Propose the final folder structure.
6. Verify that the architecture is modular.
7. Verify that no LLM is included.
8. Verify that no keyword search is included.
9. Verify that scraping is separated from runtime search.
10. Verify that embeddings are precomputed for quotes.
11. Verify that the FAISS index is persisted.
12. Verify that expensive models are loaded once.
13. Verify that the frontend uses Tailwind CSS.
14. Verify that there is no admin section.

Then proceed with implementation.

Do not create unnecessary abstractions or over-engineer the system.

Prioritize:

```text
Correctness
Modularity
Semantic relevance
Performance
Maintainability
Clean UX
```

The final application should be a complete, runnable web application where a user can naturally describe what they are feeling or thinking and receive the **3 most semantically relevant quotes** from the scraped dataset.
