# Kohler AI Bathroom Designer

Research/demo POC for an interactive AI bathroom design assistant. The implementation follows `IMPLEMENTATION_SPEC.md` incrementally, with LLMs proposing and deterministic software enforcing hard product/spatial constraints.

## Implementation status

- Phase 1 — Foundation: **complete**
- Phase 2 — Synthetic catalog/evaluation data: **complete**
- Phase 3 — Neo4j knowledge graph/rules: **complete**
- Phase 4 — Hybrid semantic + KG recommendation: **complete**
- Phase 5 — PuLP bundle optimization: **complete**
- Phase 6 — Multimodal spatial extraction: **complete**
- Phase 7 — Deterministic geometry validation: **complete**
- Phase 8 — Layout generation/refinement: **complete**
- Phase 9 — Deterministic SVG rendering: **complete**
- Phase 10 — Flask API + interactive frontend: **complete**
- Phase 11 — End-to-end evaluation framework: **complete**
- Phase 12 — Testing/demo polish: **complete**

## Architecture

```text
Bathroom image + requirements
          ↓
Spatial extraction / structured input
          ↓
Neo4j KG + semantic retrieval
          ↓
Hybrid recommendation
          ↓
PuLP Top-3 bundle optimization
          ↓
3–5 layout candidates
          ↓
Deterministic geometry validation + refinement
          ↓
Best valid layout
          ↓
Deterministic SVG
          ↓
Flask interactive UI
```

The central engineering boundary is: **the LLM proposes; structured product rules, mathematical optimization, and deterministic geometry validation enforce hard constraints.**

## Local setup

From the repository root:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\\Scripts\\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and configure services as needed.

Run the environment check:

```bash
python scripts/preflight.py
```

Run tests:

```bash
python -m pytest -q
```

Start Flask:

```bash
python -m app.main
```

Then open `http://127.0.0.1:5000/`.

## Offline/demo path

The frontend accepts a structured `SpatialPlan`, so the deterministic pipeline can be exercised without a live bathroom image. A command-line demo is also provided:

```bash
python scripts/demo_offline.py
```

The demo uses a synthetic bathroom plan and does not make a multimodal API call. The complete demo still requires the Python dependencies in `requirements.txt`, and bundle optimization requires PuLP.

## Optional services

- `OPENAI_API_KEY` — required for live image/spatial extraction and optional LLM explanation/refinement.
- `OPENAI_MODEL` — configurable multimodal model; defaults to the implementation's configured model.
- `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD` — enable Neo4j-backed product relationships.
- `PRODUCT_CATALOG_MODE=synthetic` — default development/evaluation catalog mode.

The system must not claim that the synthetic catalog is the complete Kohler catalog. Real/curated catalog mode is intended for explicitly sourced official product data.

## API

- `GET /` — interactive designer
- `GET /health` — health check
- `POST /api/design` — full pipeline; accepts multipart `requirements` + optional `image`, or structured `spatial_plan`
- `POST /api/recommend` — product recommendation only
- `POST /api/layout` — return layout/SVG information from a result payload
- `POST /api/validate` — return validation information from a result payload
- `POST /api/replace` — replace a selected product category and regenerate the affected bundle/layout
- `GET /api/result` — latest result held by the running Flask process

## Evaluation

Run:

```bash
python scripts/run_evaluation.py
```

Benchmark outputs are stored under `evaluation/benchmark_results/`.

The evaluation framework covers spatial extraction errors, recommendation compatibility, optimization/budget/accessory constraints, geometry violations, repair success, and fully-valid design rate.

## Failure handling

The application explicitly reports missing dependencies, missing API keys, unavailable Neo4j, malformed spatial data, missing room dimensions, unavailable compatible bundles, budget shortfalls, and layouts with no valid candidate. It does not silently fabricate missing measurements or professional code compliance.

See `IMPLEMENTATION_SPEC.md` for the complete requirements and definition of done.
