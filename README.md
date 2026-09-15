# Kohler AI Bathroom Planner and Designer

> An AI-assisted bathroom planning and product recommendation POC that combines multimodal spatial understanding, structured product knowledge, semantic retrieval, mathematical bundle optimization, deterministic geometry validation, layout refinement, and SVG-based 2D visualization.

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.x-E92063?style=flat-square)](https://docs.pydantic.dev/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.x-008CC1?style=flat-square&logo=neo4j&logoColor=white)](https://neo4j.com/)
[![PuLP](https://img.shields.io/badge/PuLP-ILP%20Optimization-3776AB?style=flat-square)](https://coin-or.github.io/pulp/)
[![Sentence Transformers](https://img.shields.io/badge/Sentence--Transformers-Embeddings-FF6F00?style=flat-square)](https://www.sbert.net/)
[![OpenAI](https://img.shields.io/badge/OpenAI-Multimodal%20LLM-412991?style=flat-square&logo=openai&logoColor=white)](https://platform.openai.com/)
[![Jinja2](https://img.shields.io/badge/Jinja2-Templates-B41717?style=flat-square)](https://jinja.palletsprojects.com/)
[![JavaScript](https://img.shields.io/badge/JavaScript-Vanilla-F7DF1E?style=flat-square&logo=javascript&logoColor=111111)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![SVG](https://img.shields.io/badge/SVG-Deterministic%202D%20Rendering-FFB13B?style=flat-square)](https://www.w3.org/Graphics/SVG/)

**Core technologies:** Python, Flask, Pydantic, Neo4j, Cypher, PuLP, sentence-transformers, OpenAI multimodal API, Jinja2, HTML/CSS, Vanilla JavaScript, deterministic SVG rendering, pytest.

**Data modes:** synthetic catalog for development/evaluation, with architecture prepared for a separate curated real-product mode.

---

## Problem Statement

Bathroom product selection and bathroom layout planning are usually treated as separate problems.

A customer may know:

- the approximate bathroom dimensions,
- their budget,
- the required fixtures,
- a preferred design theme,
- and a bathroom plan or image,

but still has to manually answer several difficult questions:

1. Which products fit the desired aesthetic?
2. Which products are mutually compatible?
3. Which accessories are required for the selected products?
4. Does the complete bundle remain within budget?
5. Will the selected fixtures physically fit in the room?
6. Will clearances, circulation, windows, and door swing remain usable?
7. If a product is replaced, what else needs to change?
8. Can the resulting design be communicated visually and explained clearly?

A purely semantic recommendation system can produce aesthetically attractive combinations that violate hard product or spatial constraints. A purely rule-based system can be consistent but weak at understanding natural-language preferences and design intent.

The project therefore treats bathroom planning as a **hybrid AI + optimization + deterministic geometry problem**.

---

## Solution

The Kohler AI Bathroom Planner and Designer combines six complementary capabilities:

### 1. Multimodal spatial understanding

A bathroom plan/image and user requirements are converted into structured representations.

The spatial extractor produces a `SpatialPlan` containing room dimensions, doors, windows, fixed obstacles, existing infrastructure, and proposed infrastructure.

Every extracted measurement can carry:

- value
- unit
- source/provenance
- confidence

The system explicitly avoids silently inventing missing dimensions or precise door-swing measurements.

### 2. Product intelligence with Knowledge Graph + semantic retrieval

The product catalog is represented through:

- structured product attributes,
- Neo4j relationships,
- explicit compatibility/incompatibility rules,
- theme relationships,
- infrastructure requirements,
- accessory dependencies.

Semantic embeddings provide fuzzy matching for preferences such as:

> "warm, minimalist, spa-like, natural"

while the Knowledge Graph remains authoritative for explicit relationships.

### 3. Hybrid recommendation

Candidate products are ranked using:

- semantic similarity,
- KG/theme evidence,
- user preference fit.

Explicit incompatibilities are never overridden by semantic similarity.

If a category has no explicit KG theme match, the system falls back to semantic ranking rather than incorrectly eliminating the entire category.

### 4. PuLP bundle optimization

The optimizer selects complete product bundles under hard constraints.

It handles:

- one product per required category,
- budget,
- product incompatibilities,
- required accessories,
- accessory cost,
- bundle ranking.

If no budget-feasible bundle exists, the system can identify the best fallback bundle and report the actual budget shortfall instead of pretending the bundle fits.

### 5. Deterministic spatial validation + layout refinement

The LLM/layout generator proposes candidate fixture arrangements.

A deterministic geometry engine then checks:

- room bounds,
- fixture collisions,
- required clearances,
- door swing,
- windows,
- fixed obstacles,
- circulation,
- infrastructure requirements.

Invalid layouts are passed through a bounded refinement loop and revalidated.

Only layouts that pass hard spatial validation are eligible to become the final design.

### 6. Deterministic SVG visualization

The final validated layout is rendered using a deterministic Python SVG renderer.

The renderer draws:

- room boundaries,
- fixtures,
- doors,
- door swing,
- windows,
- dimensions,
- labels,
- legend.

The same validated layout produces the same SVG representation.

---

# Business Impact

## 1. AI in manufacturing and product ecosystems

The project demonstrates how generative AI can move beyond text and image generation into a **constraint-aware product configuration workflow**.

For a manufacturer such as Kohler, the same architecture can support:

- guided product discovery,
- product configuration,
- compatibility-aware cross-selling,
- accessory attachment,
- design assistance,
- spatial planning,
- customer-specific recommendations.

The Knowledge Graph creates a machine-readable layer over product relationships, while the optimization layer converts recommendations into complete, constraint-aware bundles.

This creates a bridge between **AI personalization and structured manufacturing/product knowledge**.

## 2. Recommendation engine

Traditional recommendation systems often optimize relevance or similarity.

This project adds hard product logic:

```text
semantic relevance
        +
explicit compatibility
        +
accessories
        +
budget
        =
feasible product bundle
```

---

## System Architecture
```
                         USER
              Image + Requirements + Budget
                           │
                           ▼
                ┌─────────────────────┐
                │ Multimodal LLM      │
                │                     │
                │ • Requirement parse │
                │ • Spatial extraction│
                └──────────┬──────────┘
                           │
                 ┌─────────┴─────────┐
                 ▼                   ▼
        User Constraints       Spatial Plan
                 │                   │
                 └─────────┬─────────┘
                           ▼
              ┌───────────────────────┐
              │ Product Intelligence  │
              │                       │
              │ Neo4j KG              │
              │ +                     │
              │ Semantic Embeddings   │
              └───────────┬───────────┘
                          ▼
                  Candidate Products
                          │
                          ▼
                ┌───────────────────┐
                │ Hybrid Ranker     │
                └─────────┬─────────┘
                          ▼
                Ranked Product Pool
                          │
                          ▼
                ┌───────────────────┐
                │ PuLP Optimizer    │
                │                   │
                │ Budget            │
                │ Compatibility     │
                │ Accessories       │
                │ Preferences       │
                └─────────┬─────────┘
                          ▼
                    Top 3 Bundles
                          │
                          ▼
              ┌─────────────────────┐
              │ Layout Planner      │
              │ LLM + KG rules     │
              └──────────┬──────────┘
                         ▼
                  3–5 Candidates
                         │
                         ▼
              ┌─────────────────────┐
              │ Geometry Engine     │
              │                     │
              │ Bounds              │
              │ Collision           │
              │ Clearance           │
              │ Door Swing          │
              │ Circulation         │
              │ Infrastructure      │
              └──────────┬──────────┘
                         │
                  invalid │ valid
                         ▼
                 Refinement Loop
                         │
                         ▼
                 Best Valid Layout
                         │
                         ▼
              ┌─────────────────────┐
              │ Deterministic SVG   │
              └──────────┬──────────┘
                         ▼
                 Flask Frontend
                         │
                         ▼
                       USER
```
---

### Architectural Authority

The project intentionally separates responsibilities:

| Layer | Primary responsibility | Authority |
|---|---|---|
| Multimodal LLM | Interpret image and design intent | Proposal / extraction |
| Semantic embeddings | Fuzzy aesthetic matching | Ranking signal |
| Neo4j KG | Explicit product relationships | Hard product rules |
| PuLP | Discrete bundle selection | Hard optimization constraints |
| Geometry engine | Physical feasibility | Hard spatial authority |
| SVG renderer | Visual representation | Deterministic output |
| Flask | Application/API/UI integration | Orchestration/interface |

---

## Repository Structure

```
kohler-ai-bathroom-designer/
│
├── README.md                         # Project README / general documentation
├── README_GITHUB.md                  # GitHub-focused project README
├── .env.example                      # Example environment configuration
├── requirements.txt                  # Python dependencies
│
├── app/
│   ├── __init__.py                   # Python package initialization
│   ├── main.py                       # Flask application entry point
│   │
│   ├── config/
│   │   ├── __init__.py               # Configuration package
│   │   ├── constants.py              # Shared application constants
│   │   └── settings.py               # Environment-backed settings
│   │
│   ├── models/
│   │   ├── __init__.py               # Model package
│   │   ├── product.py                # Product data contract
│   │   ├── user_constraints.py       # User requirement model
│   │   ├── spatial_plan.py           # Spatial geometry/provenance model
│   │   ├── layout.py                 # Layout and fixture placement models
│   │   └── result.py                 # End-to-end result contract
│   │
│   ├── llm/
│   │   ├── __init__.py               # LLM package
│   │   ├── client.py                 # Provider abstraction + OpenAI adapter
│   │   ├── vision.py                 # Multimodal spatial extraction
│   │   ├── requirements.py           # Natural-language requirements parser
│   │   ├── explainer.py              # Design explanation generation
│   │   └── prompts/
│   │       ├── requirements.txt      # Requirements parsing prompt
│   │       └── spatial_extraction.txt# Spatial extraction prompt
│   │
│   ├── knowledge_graph/
│   │   ├── __init__.py               # KG package
│   │   ├── connection.py             # Neo4j driver/connection handling
│   │   ├── schema.py                 # Neo4j constraints and schema
│   │   ├── queries.py                # Cypher query definitions
│   │   ├── rules_engine.py            # Deterministic KG rule interface
│   │   └── seed.py                   # Synthetic catalog → Neo4j seeding
│   │
│   ├── products/
│   │   ├── __init__.py               # Product package
│   │   ├── catalog.py                # Catalog loading and normalization
│   │   ├── embeddings.py             # Product semantic embedding index
│   │   ├── validator.py              # Catalog integrity validation
│   │   └── data/
│   │       └── synthetic_products.json# Synthetic product catalog
│   │
│   ├── recommendation/
│   │   ├── __init__.py               # Recommendation package
│   │   ├── candidate_generation.py   # Per-category candidate generation
│   │   ├── scoring.py                # Semantic/KG/preference scoring
│   │   └── hybrid_ranker.py          # Hybrid recommendation ranking
│   │
│   ├── optimization/
│   │   ├── __init__.py               # Optimization package
│   │   ├── optimizer.py              # PuLP bundle optimization
│   │   ├── constraints.py            # Optimization hard constraints
│   │   └── accessories.py            # Accessory dependency/cost logic
│   │
│   ├── geometry/
│   │   ├── __init__.py               # Geometry package
│   │   ├── spatial_engine.py         # Coordinate/fixture geometry primitives
│   │   ├── collision.py              # Fixture collision detection
│   │   ├── clearance.py              # Required clearance validation
│   │   ├── door.py                   # Door swing geometry
│   │   ├── circulation.py             # Circulation checks
│   │   ├── infrastructure.py         # Plumbing/electrical checks
│   │   └── validator.py              # Unified geometry validator
│   │
│   ├── layout/
│   │   ├── __init__.py               # Layout package
│   │   ├── candidate_generator.py    # Multi-strategy layout generation
│   │   ├── refinement.py             # Invalid-layout repair loop
│   │   ├── scorer.py                 # Valid-layout scoring
│   │   └── selector.py               # Best-valid-layout selection
│   │
│   ├── rendering/
│   │   ├── __init__.py               # Rendering package
│   │   ├── svg_renderer.py           # Deterministic SVG generation
│   │   ├── dimensions.py             # SVG dimension annotations
│   │   ├── symbols.py                # Door/window/fixture SVG symbols
│   │   └── legend.py                 # SVG legend rendering
│   │
│   ├── evaluation/
│   │   ├── __init__.py               # Evaluation package
│   │   ├── evaluator.py              # Benchmark runner
│   │   ├── metrics.py                # Evaluation metric calculations
│   │   └── scenarios.py              # Synthetic benchmark scenarios
│   │
│   ├── pipeline/
│   │   ├── __init__.py               # Pipeline package
│   │   └── orchestrator.py           # End-to-end pipeline orchestration
│   │
│   └── api/
│       ├── __init__.py               # API package
│       ├── routes.py                 # Flask API routes
│       └── schemas.py                # API request/response schemas
│
├── frontend/
│   ├── templates/
│   │   └── index.html                # Main interactive designer page
│   │
│   └── static/
│       ├── css/
│       │   └── style.css             # Frontend styling
│       └── js/
│           └── app.js                # Browser-side API/UI logic
│
├── evaluation/
│   ├── bathroom_plans/               # Synthetic benchmark spatial plans
│   └── expected_outputs/             # Gold spatial extraction outputs
│
├── tests/
│   ├── test_foundation.py            # Foundation/model tests
│   ├── test_catalog.py               # Catalog validation tests
│   ├── test_synthetic_plans.py       # Synthetic-plan tests
│   ├── test_kg.py                    # Knowledge Graph tests
│   ├── test_recommendation.py        # Recommendation tests
│   ├── test_optimizer.py             # PuLP optimization tests
│   ├── test_requirements.py          # Requirements parser tests
│   ├── test_vision.py                # Spatial extraction tests
│   ├── test_geometry.py              # Geometry validation tests
│   ├── test_layout.py                # Layout generation/refinement tests
│   ├── test_rendering.py             # SVG renderer tests
│   ├── test_evaluation.py            # Evaluation framework tests
│   ├── test_pipeline.py              # Pipeline integration tests
│   └── test_api.py                   # Flask API tests
│
└── scripts/
    ├── generate_synthetic_catalog.py # Generate synthetic products
    ├── generate_test_plans.py        # Generate synthetic bathroom plans
    ├── preflight.py                  # Environment/dependency checks
    ├── demo_offline.py               # Structured-input offline demo
    └── run_evaluation.py             # Run evaluation benchmarks
```

---

# Setup

---

## 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd kohler-ai-bathroom-designer
```

---

## 2. Create a virtual environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure environment variables

Copy:

```text
.env.example
```

to:

```text
.env
```

Example:

```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-5.6-luna

FLASK_ENV=development
FLASK_DEBUG=1

PRODUCT_CATALOG_MODE=synthetic

NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password
```

> **Security:** Keep `.env` private. Never commit API keys or database passwords to GitHub.

The application is designed around an LLM provider abstraction, so another compatible multimodal provider can be integrated without changing the downstream recommendation, optimization, geometry, and rendering layers.

---

# Neo4j Setup

---

## 1. Install and start Neo4j

Install and start a local **Neo4j 5.x** database.

The default configuration expects:

```text
bolt://localhost:7687
```

with:

```text
username = neo4j
password = your configured password
```

---

## 2. Seed the synthetic product Knowledge Graph

If the checkout contains the seeding script:

```bash
python scripts/seed_neo4j.py
```

If your local checkout does not expose that script, use the KG seeding module/API provided by the project version you are running.

The graph represents product relationships such as:

```text
COMPATIBLE_WITH
INCOMPATIBLE_WITH
STYLED_AS
HAS_FINISH
REQUIRES_ACCESSORY
REQUIRES_PLUMBING
REQUIRES_DRAIN
REQUIRES_WATER_SUPPLY
REQUIRES_ELECTRICAL
REQUIRES_INSTALLATION_ZONE
```

---

# Usage

---

## 1. Run environment checks

```bash
python scripts/preflight.py
```

This checks whether the local environment has the dependencies and configuration required by the project.

---

## 2. Run tests

```bash
python -m pytest -q
```

Run the test suite before starting the full demo to catch configuration or dependency issues early.

---

## 3. Run the offline/demo pipeline

The structured spatial-plan path can be used for deterministic development and testing without requiring image-based LLM extraction.

```bash
python scripts/demo_offline.py
```

This is useful for validating the recommendation, optimization, layout, geometry-validation, and SVG-rendering pipeline independently of multimodal image extraction.

---

## 4. Run the Flask application

```bash
python -m app.main
```

Then open:

```text
http://127.0.0.1:5000
```

The frontend accepts:

- Bathroom image/plan
- Budget
- Theme
- Required fixtures
- User preferences

The main design request uses:

```http
POST /api/design
```

Additional endpoints include:

```http
POST /api/recommend
POST /api/layout
POST /api/validate
POST /api/replace
GET  /api/result
```

---

# Recommended Local Run Order

---

```text
1. Create and activate .venv
        ↓
2. Install requirements.txt
        ↓
3. Configure .env
        ↓
4. Start Neo4j
        ↓
5. Seed the Knowledge Graph
        ↓
6. Run preflight checks
        ↓
7. Run tests
        ↓
8. Run offline demo
        ↓
9. Start Flask
        ↓
10. Open http://127.0.0.1:5000
        ↓
11. Upload bathroom image/plan
        ↓
12. Enter budget, theme, fixtures and preferences
        ↓
13. Generate the design
```

---

# End-to-End Design Flow

---

The complete application is intended to follow this pipeline:

```text
Bathroom Image + User Requirements
                ↓
       Multimodal Spatial Extraction
                ↓
          User Constraints
                ↓
       Product Catalog + Neo4j KG
                +
       Semantic Product Retrieval
                ↓
        Hybrid Recommendation
                ↓
          PuLP Optimization
                ↓
            Top 3 Bundles
                ↓
       3–5 Layout Candidates
                ↓
      Deterministic Geometry Validation
                ↓
        Refinement of Invalid Layouts
                ↓
          Best Valid Layout
                ↓
        Deterministic SVG Renderer
                ↓
          Flask Interactive UI
```

---

# Author

Satyam Kumar

B.Tech — Computer Science & Engineering

Interests: Artificial Intelligence, Machine Learning, NLP, Generative AI, Knowledge Graphs, Recommendation Systems.