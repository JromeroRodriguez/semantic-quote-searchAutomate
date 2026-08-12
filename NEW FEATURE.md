# Feature Implementation: Budget Optimizer & Batch Packaging

## Context

You are working on an existing Python/FastAPI application called **Semantic Quote Search Automate**.

Repository:
`JromeroRodriguez/semantic-quote-searchAutomate`

The application currently includes:

- Quote scraping from `quotes.toscrape.com`
- Quote storage in `data/quotes.json`
- Semantic search using embeddings + FAISS
- Cross-encoder reranking
- Debate mode using a local Ollama LLM
- Frontend built with vanilla JavaScript and custom CSS
- Ollama configured with the local model `qwen2.5:0.5b`

The existing functionality is working and **must not be broken or unnecessarily refactored**.

---

# New Feature

Implement a new independent feature called:

**Budget Optimizer & Batch Packaging**

The purpose of this feature is to efficiently package scraped quotes into batches before sending them to an LLM.

The system must:

1. Load quotes from the existing `data/quotes.json`.
2. Calculate the token size of the text before sending it to the LLM.
3. Dynamically group quotes into batches.
4. Never exceed the configured maximum token budget per request.
5. Maximize the amount of content packed into each batch.
6. Process all quotes.
7. Track actual input/output token consumption.
8. Track the total number of LLM requests.
9. Generate a final usage receipt.

This feature should be implemented as a **new module**, not as a replacement for the current search or debate pipeline.

---

# Existing Architecture

Preserve the current architecture.

Relevant existing components include:

```text
scripts/
    scrape_quotes.py

data/
    quotes.json

backend/app/
    services/
        search/
        debate/
        embeddings/
        reranker/

frontend/
    index.html
    src/
        main.js
        services/api.js
        styles/main.css
```

The existing scraper already produces records similar to:

```json
{
    "id": 1,
    "author": "Albert Einstein",
    "quote": "The world as we have created it is a process of our thinking...",
    "source": "quotes.toscrape.com"
}
```

Do NOT create another scraper.

Reuse the existing dataset.

---

# LLM

The current local LLM is:

```text
Provider: Ollama
Model: qwen2.5:0.5b
```

The existing Ollama configuration must be reused.

Do not introduce another LLM provider unless absolutely necessary.

Do not hardcode the model name if the project already exposes it through configuration.

---

# Token Counting

Token counting is a critical requirement.

Do NOT use character count as a substitute for tokens.

Do NOT assume:

```text
1 word = 1 token
```

The implementation must use a tokenizer compatible with the selected model whenever possible.

Investigate the current project dependencies and Ollama capabilities before adding a new dependency.

Prefer the simplest reliable solution compatible with:

```text
qwen2.5:0.5b
```

If an exact tokenizer cannot reasonably be used locally, implement a clearly documented fallback estimator and isolate it behind a tokenizer abstraction so it can later be replaced without changing the batching logic.

The token-counting component must be independently testable.

---

# Batch Algorithm

Implement a greedy packing algorithm.

Given:

```text
maximum_tokens_per_request = X
```

and quotes with calculated token sizes:

```text
Quote A = 120 tokens
Quote B = 250 tokens
Quote C = 180 tokens
Quote D = 300 tokens
```

with:

```text
X = 500
```

the result should be:

```text
Batch 1:
A + B = 370 tokens

C cannot fit:
370 + 180 = 550

Batch 2:
C + D = 480 tokens
```

The algorithm must:

- Preserve quote order.
- Never exceed the configured token limit.
- Add as many quotes as possible to the current batch.
- Start a new batch when the next quote would exceed the limit.
- Detect a single quote that is larger than the configured limit.
- Handle empty datasets.
- Handle malformed records gracefully.

Do not silently truncate quotes unless an explicit truncation strategy is implemented and documented.

---

# Important: Prompt Overhead

The token budget must account for the complete request, not only the raw quote text.

For example, if the LLM prompt looks like:

```text
Translate these quotes into Japanese and explain their historical context:

1. ...
2. ...
3. ...
```

the following contribute to the request token count:

- System prompt
- Instructions
- Formatting
- Quote text
- Author information
- Any additional context

Design the batching system so prompt overhead can be measured or configured.

The goal is to avoid producing a batch that appears to be under the limit when the complete prompt actually exceeds it.

---

# LLM Processing

Create a dedicated service responsible for processing batches through Ollama.

Conceptually:

```text
Quote Dataset
      ↓
Token Counter
      ↓
Batch Optimizer
      ↓
Batch 1
Batch 2
Batch 3
...
      ↓
Ollama
      ↓
Usage Tracker
      ↓
Final Receipt
```

Each batch should contain enough structured information to know:

```text
batch_id
quote_ids
quote_count
estimated_input_tokens
actual_input_tokens
actual_output_tokens
total_tokens
```

Use the existing Ollama integration patterns where appropriate.

Do not duplicate unnecessary HTTP/client configuration.

---

# Actual Token Usage

The system must distinguish between:

### Estimated usage

Calculated before the request:

```text
estimated_input_tokens
```

### Actual usage

Returned by Ollama after generation:

```text
actual_input_tokens
actual_output_tokens
total_tokens
```

Use Ollama's response metadata whenever available.

Do not fabricate usage numbers.

If the Ollama response does not provide a field required by the receipt, represent it explicitly as unavailable instead of inventing a value.

---

# Usage Receipt

Create a structured final receipt.

Example:

```json
{
    "quotes_processed": 100,
    "batches_created": 8,
    "requests_completed": 8,
    "estimated_input_tokens": 4820,
    "actual_input_tokens": 4912,
    "actual_output_tokens": 1830,
    "total_tokens": 6742,
    "token_limit_per_request": 1000
}
```

The exact schema can be improved if necessary, but it must clearly communicate:

- Number of quotes processed
- Number of batches
- Number of requests
- Estimated input consumption
- Actual input consumption
- Actual output consumption
- Total consumption
- Configured token limit

---

# API

Add a dedicated API endpoint for the new feature.

For example:

```http
POST /api/v1/optimizer/run
```

The endpoint should allow configuration of the batch budget.

Example request:

```json
{
    "max_tokens": 1000
}
```

If useful, allow optional parameters such as:

```json
{
    "max_tokens": 1000,
    "process_with_llm": true
}
```

The endpoint should return:

```json
{
    "success": true,
    "receipt": {
        ...
    },
    "batches": [
        {
            "batch_id": 1,
            "quote_ids": [1, 2, 3],
            "quote_count": 3,
            "estimated_input_tokens": 940,
            "actual_input_tokens": 951,
            "actual_output_tokens": 310,
            "total_tokens": 1261
        }
    ]
}
```

Use proper Pydantic schemas following the existing project's conventions.

---

# Frontend

Add a new section/mode to the existing frontend:

**Budget Optimizer**

Do not redesign the entire application.

Reuse the existing visual language and CSS architecture.

The UI should allow the user to:

1. Enter the maximum token budget.
2. Start the optimization.
3. See how many quotes were processed.
4. See how many batches were created.
5. See how many requests were made.
6. See estimated vs actual token usage.
7. See the final total consumption.
8. Inspect the generated batches if practical.

Example UI:

```text
┌─────────────────────────────────────────────┐
│ Budget Optimizer                            │
│                                             │
│ Maximum tokens per request                  │
│ [ 1000 ]                                    │
│                                             │
│ [ Run Optimizer ]                           │
│                                             │
│ Quotes processed        100                 │
│ Batches                 8                   │
│ Requests                8                   │
│                                             │
│ Estimated input        4,820 tokens         │
│ Actual input           4,912 tokens         │
│ Output                 1,830 tokens         │
│ Total                  6,742 tokens         │
└─────────────────────────────────────────────┘
```

Keep the existing Search and Debate modes functional.

---

# Configuration

If appropriate, add a configuration value for the default budget.

For example:

```env
OPTIMIZER_MAX_TOKENS=1000
```

However, the API should still allow the user to provide a custom limit.

Do not hardcode the budget throughout the codebase.

---

# Suggested Backend Structure

Follow the project's existing architecture.

A possible structure is:

```text
backend/app/
├── api/
│   └── routes/
│       └── optimizer.py
│
├── schemas/
│   └── optimizer.py
│
└── services/
    └── optimizer/
        ├── __init__.py
        ├── tokenizer.py
        ├── batch_optimizer.py
        ├── ollama_processor.py
        └── usage_tracker.py
```

This structure is only a recommendation.

Adapt it to the project's existing conventions rather than blindly creating files.

Responsibilities should remain separated:

### tokenizer.py

Responsible only for token counting.

### batch_optimizer.py

Responsible only for batch construction.

### ollama_processor.py

Responsible for sending batches to Ollama.

### usage_tracker.py

Responsible for accumulating estimated and actual usage.

### optimizer.py / orchestration service

Responsible for coordinating the complete workflow.

---

# Error Handling

Handle at least:

- Empty `quotes.json`
- Missing dataset
- Invalid JSON
- Invalid quote records
- Empty quote text
- Invalid token budget
- Token budget <= 0
- Quote larger than maximum token budget
- Ollama unavailable
- Ollama timeout
- Invalid Ollama response
- Partial batch processing failures

Do not allow one failed batch to silently corrupt the final receipt.

Clearly report failed requests.

---

# Tests

Add unit and integration tests.

At minimum test:

### Tokenizer

- Empty string
- Short quote
- Long quote
- Unicode/Japanese text if applicable

### Batch optimizer

```text
Quotes fit exactly
Quotes exceed limit
Multiple batches
Single quote larger than limit
Empty dataset
One quote
Many small quotes
```

Example:

```text
Limit = 100

Quote sizes:

40
30
20
50
```

Expected:

```text
Batch 1 = 40 + 30 + 20 = 90
Batch 2 = 50
```

Also test that:

```text
sum(batch.tokens) <= max_tokens
```

for every batch.

### Usage tracking

Verify that:

```text
total = input + output
```

and that multiple batches accumulate correctly.

### API

Test the new endpoint using the project's existing FastAPI testing approach.

---

# Performance

The dataset currently comes from `quotes.toscrape.com`.

Do not perform unnecessary repeated tokenization.

Tokenize each quote once and cache/reuse the result during batch creation.

Avoid loading the entire LLM model repeatedly.

Reuse the existing Ollama configuration.

The optimizer should be efficient enough to process the complete dataset without unnecessary API requests.

---

# Compatibility

Do not break:

```text
POST /api/v1/search
POST /api/v1/debate
GET /health
```

Do not modify the semantic search pipeline unless absolutely necessary.

Do not modify the scraper unless absolutely necessary.

Do not replace FAISS.

Do not replace the embedding model.

Do not replace the reranker.

Do not replace Ollama.

Do not introduce unnecessary frameworks.

---

# Implementation Process

Before changing code:

1. Inspect the repository structure.
2. Inspect the current configuration.
3. Inspect the existing Ollama integration.
4. Inspect existing Pydantic schemas.
5. Inspect existing API routing conventions.
6. Inspect frontend architecture.
7. Inspect existing tests.

Then:

1. Design the optimizer architecture.
2. Implement token counting.
3. Implement batch packing.
4. Implement usage tracking.
5. Implement Ollama batch processing.
6. Implement the API endpoint.
7. Implement frontend integration.
8. Add tests.
9. Run the existing test suite.
10. Run the new tests.
11. Verify that Search and Debate still work.

---

# Important Constraints

Do NOT simply create a demonstration script disconnected from the application.

This must be a real application feature integrated into the existing architecture.

Do NOT create fake token usage.

Do NOT assume character count equals token count.

Do NOT hardcode `qwen2.5:0.5b` if the project already provides an environment-based model configuration.

Do NOT break existing features.

Do NOT duplicate the scraping pipeline.

Do NOT send all 100 quotes in one request.

The primary objective is:

> Efficiently maximize the amount of quote content sent in each LLM request while never exceeding the configured token budget, then report the actual consumption and number of requests.

---

# Final Deliverables

When implementation is complete, provide:

1. Files created.
2. Files modified.
3. Explanation of the batching algorithm.
4. Explanation of the token-counting strategy.
5. Explanation of how Ollama usage is measured.
6. API endpoint and request/response examples.
7. Frontend changes.
8. Tests added.
9. Test results.
10. Any limitations or assumptions.

Do not modify unrelated parts of the application.
