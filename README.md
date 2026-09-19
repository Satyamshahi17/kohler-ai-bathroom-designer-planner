# Kohler AI Bathroom Planner and Designer

> An AI-assisted bathroom planning and product recommendation POC that
> combines multimodal spatial understanding, structured product
> knowledge, semantic retrieval, mathematical bundle optimization,
> deterministic geometry validation, layout refinement, and SVG-based 2D
> visualization.

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-2.x-E92063?style=flat-square)](https://docs.pydantic.dev/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.x-008CC1?style=flat-square&logo=neo4j&logoColor=white)](https://neo4j.com/)
[![PuLP](https://img.shields.io/badge/PuLP-ILP%20Optimization-3776AB?style=flat-square)](https://coin-or.github.io/pulp/)
[![Sentence
Transformers](https://img.shields.io/badge/Sentence--Transformers-Embeddings-FF6F00?style=flat-square)](https://www.sbert.net/)
[![OpenAI](https://img.shields.io/badge/OpenAI-Multimodal%20LLM-412991?style=flat-square&logo=openai&logoColor=white)](https://platform.openai.com/)
[![Jinja2](https://img.shields.io/badge/Jinja2-Templates-B41717?style=flat-square)](https://jinja.palletsprojects.com/)
[![JavaScript](https://img.shields.io/badge/JavaScript-Vanilla-F7DF1E?style=flat-square&logo=javascript&logoColor=111111)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![SVG](https://img.shields.io/badge/SVG-Deterministic%202D%20Rendering-FFB13B?style=flat-square)](https://www.w3.org/Graphics/SVG/)

**Core technologies:** Python, Flask, Pydantic, Neo4j, Cypher, PuLP,
sentence-transformers, OpenAI multimodal API, Jinja2, HTML/CSS, Vanilla
JavaScript, deterministic SVG rendering, pytest.

Note: The system uses a provider-agnostic LLM abstraction. The recorded demonstration uses Groq-hosted Qwen 3.8 27B, while an OpenAI multimodal provider is retained as an alternative implementation.

**Data modes:** synthetic catalog for development/evaluation, with
architecture prepared for a separate curated real-product mode.

### 📁 Submission Files & Project Demo Video

* **Drive Folder:** [View Project Files & Demo Video](https://drive.google.com/drive/folders/1oph_SpDNb00vcEXeRS-ZYYc-RcGB6yxC?usp=sharing)
* **YouTube Demo link:** [View Demo Video on YouTube](https://youtu.be/IQe2SfiU8cE)
------------------------------------------------------------------------

## Problem Statement

Bathroom product selection and bathroom layout planning are usually
treated as separate problems.

A customer may know:

-   the approximate bathroom dimensions,
-   their budget,
-   the required fixtures,
-   a preferred design theme,
-   and a bathroom plan or image,

but still has to manually answer several difficult questions:

1.  Which products fit the desired aesthetic?
2.  Which products are mutually compatible?
3.  Which accessories are required for the selected products?
4.  Does the complete bundle remain within budget?
5.  Will the selected fixtures physically fit in the room?
6.  Will clearances, circulation, windows, and door swing remain usable?
7.  If a product is replaced, what else needs to change?
8.  Can the resulting design be communicated visually and explained
    clearly?

A purely semantic recommendation system can produce aesthetically
attractive combinations that violate hard product or spatial
constraints. A purely rule-based system can be consistent but weak at
understanding natural-language preferences and design intent.

The project therefore treats bathroom planning as a **hybrid AI +
optimization + deterministic geometry problem**.

------------------------------------------------------------------------

## Solution

The Kohler AI Bathroom Planner and Designer combines six complementary
capabilities:

### 1. Multimodal spatial understanding

A bathroom plan/image and user requirements are converted into
structured representations.

The spatial extractor produces a `SpatialPlan` containing room
dimensions, doors, windows, fixed obstacles, existing infrastructure,
and proposed infrastructure.

Every extracted measurement can carry:

-   value
-   unit
-   source/provenance
-   confidence

The system explicitly avoids silently inventing missing dimensions or
precise door-swing measurements.

### 2. Product intelligence with Knowledge Graph + semantic retrieval

The product catalog is represented through:

-   structured product attributes,
-   Neo4j relationships,
-   explicit compatibility/incompatibility rules,
-   theme relationships,
-   infrastructure requirements,
-   accessory dependencies.

Semantic embeddings provide fuzzy matching for preferences such as:

> "warm, minimalist, spa-like, natural"

while the Knowledge Graph remains authoritative for explicit
relationships.

### 3. Hybrid recommendation

Candidate products are ranked using:

-   semantic similarity,
-   KG/theme evidence,
-   user preference fit.

Explicit incompatibilities are never overridden by semantic similarity.

If a category has no explicit KG theme match, the system falls back to
semantic ranking rather than incorrectly eliminating the entire
category.

### 4. PuLP bundle optimization

The optimizer selects complete product bundles under hard constraints.

It handles:

-   one product per required category,
-   budget,
-   product incompatibilities,
-   required accessories,
-   accessory cost,
-   bundle ranking.

If no budget-feasible bundle exists, the system can identify the best
fallback bundle and report the actual budget shortfall instead of
pretending the bundle fits.

### 5. Deterministic spatial validation + layout refinement

The LLM/layout generator proposes candidate fixture arrangements.

A deterministic geometry engine then checks:

-   room bounds,
-   fixture collisions,
-   required clearances,
-   door swing,
-   windows,
-   fixed obstacles,
-   circulation,
-   infrastructure requirements.

Invalid layouts are passed through a bounded refinement loop and
revalidated.

Only layouts that pass hard spatial validation are eligible to become
the final design.

### 6. Deterministic SVG visualization

The final validated layout is rendered using a deterministic Python SVG
renderer.

The renderer draws:

-   room boundaries,
-   fixtures,
-   doors,
-   door swing,
-   windows,
-   dimensions,
-   labels,
-   legend.

The same validated layout produces the same SVG representation.

------------------------------------------------------------------------

# Salient Features and Constraints Considered

## Product intelligence

-   Product categories: vanity, faucet, toilet, shower, accessory
-   Product dimensions
-   Price
-   Finish
-   Style tags
-   Installation type
-   Faucet configuration
-   Required accessories
-   Compatibility
-   Infrastructure requirements
-   Clearance requirements

## User constraints

-   Budget
-   Design theme
-   Required fixture categories
-   Natural-language preferences
-   Installation preferences where available

## Spatial constraints

-   Room width/depth
-   Walls
-   Doors
-   Door width and offset
-   Hinge position
-   Opening direction
-   Door swing angle/radius when confidently available
-   Windows
-   Ventilation
-   Fixed obstacles
-   Existing plumbing
-   Existing electrical
-   Proposed plumbing
-   Proposed electrical

## Hard validation rules

-   Fixture must remain inside room bounds
-   Fixtures cannot overlap
-   Required clearances must be satisfied
-   Door swing cannot intersect protected fixture space
-   Windows can have protected zones
-   Fixed architecture is immovable
-   Infrastructure requirements must be satisfied when represented
-   Circulation constraints are checked deterministically
-   Invalid layouts cannot win through aesthetic scoring

## Important uncertainty rules

The system does **not** silently fabricate:

-   missing room dimensions,
-   exact door-swing measurements,
-   precise product specifications for real products.

Unknown spatial information is represented as uncertain/provisional and
can prevent the system from claiming an exact layout.

> **POC limitation:** this is a research/demo system and is not
> professional architectural, plumbing, electrical, structural, or
> building-code software.

------------------------------------------------------------------------

# System Architecture

``` mermaid
flowchart TD
    U["User<br/>Bathroom Image / Plan<br/>Budget + Theme + Requirements"] --> R["Requirements Parser"]
    U --> V["Multimodal Spatial Extractor"]

    R --> UC["UserConstraints"]
    V --> SP["SpatialPlan"]

    UC --> HR["Hybrid Product Recommendation"]
    KG["Neo4j Product Knowledge Graph"] --> HR
    EMB["Semantic Embedding Index"] --> HR
    CAT["Synthetic / Curated Product Catalog"] --> HR

    HR --> C["Ranked Product Candidates"]

    C --> OPT["PuLP Bundle Optimizer"]
    KG --> OPT
    OPT --> B["Top 3 Product Bundles"]

    B --> LG["Layout Candidate Generator"]
    SP --> LG
    KG --> LG

    LG --> LV["Deterministic Geometry Validator"]

    LV -->|Invalid| RF["Layout Refinement"]
    RF --> LV

    LV -->|Valid| LS["Layout Scoring + Selection"]

    LS --> SVG["Deterministic SVG Renderer"]
    LS --> EX["Explanation + Trace"]

    SVG --> API["Flask API"]
    EX --> API
    B --> API
    SP --> API

    API --> UI["Interactive Flask / Jinja / Vanilla JS Frontend"]

    UI -->|Replace Product| RP["Replacement Flow"]
    RP --> HR
    RP --> OPT
    RP --> LG
```

### Architectural authority

The project intentionally separates responsibilities:


| Layer | Primary responsibility | Authority |
| --- | --- | --- |
| Multimodal LLM | Interpret image and design intent | Proposal / extraction |
| Semantic embeddings | Fuzzy aesthetic matching | Ranking signal |
| Neo4j KG | Explicit product relationships | Hard product rules |
| PuLP | Discrete bundle selection | Hard optimization constraints |
| Geometry engine | Physical feasibility | Hard spatial authority |
| SVG renderer | Visual representation | Deterministic output |
| Flask | Application/API/UI integration | Orchestration/interface |
  -------------------------------------------------------------------------

The central engineering principle is:

> **AI proposes personalized product and spatial designs; structured
> product knowledge, mathematical optimization, and deterministic
> geometry validation enforce consistency and physical feasibility.**

------------------------------------------------------------------------

# Module-by-Module Architecture

## Module 1 --- Configuration and Data Models

``` text
Environment variables
       │
       ▼
   Settings
       │
       ├──────────────┐
       ▼              ▼
UserConstraints    SpatialPlan
       │              │
       └──────┬───────┘
              ▼
          Pipeline
```

**Purpose:** establish typed contracts between pipeline stages.

Key models:

-   `Product`
-   `UserConstraints`
-   `SourcedValue`
-   `Door`
-   `SpatialPlan`
-   `FixturePlacement`
-   `Layout`
-   `DesignResult`

------------------------------------------------------------------------

## Module 2 --- Multimodal LLM + Requirements

``` text
Bathroom image ──► Vision Provider ──► SpatialPlan
                                      │
                                      ├─ confidence
                                      ├─ source
                                      └─ provisional state

User text ───────► Requirements Parser ──► UserConstraints
```

**Purpose:** convert unstructured user input into validated structured
data.

The provider abstraction keeps the application independent from one
specific LLM vendor.

------------------------------------------------------------------------

## Module 3 --- Product Catalog

``` text
synthetic_products.json
          │
          ▼
     Catalog Loader
          │
          ▼
 Product model validation
          │
          ▼
    Catalog in memory
```

**Purpose:** provide normalized product records to the KG, embedding
index, recommendation system, optimizer, and renderer.

The synthetic catalog is intended for POC development and evaluation.

------------------------------------------------------------------------

## Module 4 --- Knowledge Graph

``` text
Product ──STYLED_AS────────► DesignTheme
   │
   ├──HAS_FINISH───────────► Finish
   │
   ├──COMPATIBLE_WITH──────► Product
   │
   ├──INCOMPATIBLE_WITH────► Product
   │
   ├──REQUIRES_ACCESSORY───► Accessory
   │
   └──REQUIRES_ELECTRICAL──► InfrastructureRequirement
```

**Purpose:** encode relationships that should not be inferred from
semantic similarity.

Neo4j/Cypher provides deterministic relationship queries.

------------------------------------------------------------------------

## Module 5 --- Semantic Embeddings + Hybrid Recommendation

``` text
User theme/preferences
          │
          ▼
   Semantic embedding
          │
          ▼
 Product embedding search
          │
          ├───────────────┐
          ▼               ▼
 Semantic score       Neo4j evidence
          │               │
          └───────┬───────┘
                  ▼
           Hybrid Ranker
                  │
                  ▼
        Ranked candidates/category
```

**Purpose:** combine flexible semantic personalization with explicit
product rules.

Current scoring components include:

``` text
55% semantic similarity
30% KG/theme evidence
15% preference fit
```

These are ranking signals; explicit incompatibility remains a hard
constraint.

------------------------------------------------------------------------

## Module 6 --- Bundle Optimization

``` text
Ranked candidates
       │
       ▼
   Binary product variables
       +
   Binary accessory variables
       │
       ▼
       PuLP / ILP
       │
       ├── exactly one/category
       ├── budget
       ├── incompatibilities
       └── required accessories
       │
       ▼
     Top 3 Bundles
```

**Purpose:** transform individually relevant products into complete
feasible bundles.

Accessory costs are included in the total budget.

------------------------------------------------------------------------

## Module 7 --- Deterministic Geometry

``` text
SpatialPlan + Layout
        │
        ▼
 ┌─────────────────────┐
 │ Room bounds         │
 │ Collision           │
 │ Clearance           │
 │ Door swing          │
 │ Windows             │
 │ Obstacles           │
 │ Circulation         │
 │ Infrastructure      │
 └──────────┬──────────┘
            ▼
       ValidationResult
```

**Purpose:** serve as the final authority for physical feasibility.

This layer does not depend on an LLM's statement that a layout "looks
valid."

------------------------------------------------------------------------

## Module 8 --- Layout Generation + Refinement

``` text
SpatialPlan + Bundle
          │
          ▼
 Candidate Generator
          │
          ▼
      3–5 candidates
          │
          ▼
 Geometry Validator
      │          │
   invalid      valid
      │          │
      ▼          ▼
 Refinement    Scoring
      │          │
      └──►Revalidate
                 │
                 ▼
          Best valid layout
```

**Purpose:** explore multiple spatial arrangements while ensuring that
only valid candidates can win.

------------------------------------------------------------------------

## Module 9 --- Deterministic SVG Rendering

``` text
Validated Layout
      +
SpatialPlan
      +
Product dimensions
      │
      ▼
 SVG Renderer
      │
      ├── walls
      ├── doors
      ├── swing arc
      ├── windows
      ├── fixtures
      ├── dimensions
      └── legend
      │
      ▼
 Deterministic SVG
```

**Purpose:** convert validated geometry into a stable, scaled 2D
representation.

SVG generation is programmatic rather than LLM-generated.

------------------------------------------------------------------------

## Module 10 --- Flask API + Frontend

``` text
Browser
   │
   ▼
Flask / Jinja
   │
   ├── /api/design
   ├── /api/recommend
   ├── /api/layout
   ├── /api/validate
   ├── /api/replace
   └── /api/result
   │
   ▼
DesignPipeline
   │
   ▼
JSON + SVG + trace
   │
   ▼
Interactive UI
```

The frontend provides:

-   image upload,
-   requirement entry,
-   bundle display,
-   product details,
-   SVG design canvas,
-   validation results,
-   explanations,
-   product replacement.

------------------------------------------------------------------------

## Module 11 --- Evaluation

``` text
Synthetic Plans + Gold Outputs
              │
              ▼
          Evaluator
              │
     ┌────────┼────────┐
     ▼        ▼        ▼
 Spatial   Product   Layout
 Metrics   Metrics   Metrics
     │        │        │
     └────────┼────────┘
              ▼
       Aggregate Metrics
              │
              ▼
    Benchmark Results JSON
```

**Purpose:** quantify system quality rather than relying only on visual
inspection.

Metrics include extraction errors, recommendation violations, budget
violations, spatial violations, repair success, and fully valid design
rate.

------------------------------------------------------------------------

# Repository Structure

``` text
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

------------------------------------------------------------------------

# Setup

## 1. Clone the repository

``` bash
git clone <your-github-repository-url>
cd kohler-ai-bathroom-designer
```

## 2. Create a virtual environment

### Windows

``` powershell
python -m venv .venv
.venv\Scripts\activate
```

### macOS/Linux

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

``` bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Copy:

``` text
.env.example
```

to:

``` text
.env
```

Example:

``` env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-5.6-luna

FLASK_ENV=development
FLASK_DEBUG=1

PRODUCT_CATALOG_MODE=synthetic

NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password
```

> Keep `.env` private. Never commit API keys or database passwords to
> GitHub.

The application is designed around an LLM provider abstraction, so
another compatible multimodal provider can be integrated without
changing the downstream recommendation, optimization, geometry, and
rendering layers.

------------------------------------------------------------------------

# Neo4j Setup

Install and start a local Neo4j 5.x database.

The default configuration expects:

``` text
bolt://localhost:7687
```

with:

``` text
username = neo4j
password = your configured password
```

Then seed the synthetic product Knowledge Graph:

``` bash
python scripts/seed_neo4j.py
```

If your local setup does not expose that script in the current checkout,
seed through the KG module/API according to the project version you are
using.

The graph represents product relationships such as:

``` text
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

------------------------------------------------------------------------

# Usage

## Run environment checks

``` bash
python scripts/preflight.py
```

## Run tests

``` bash
python -m pytest -q
```

## Run the offline/demo pipeline

The structured spatial-plan path can be used for deterministic
development and testing without requiring image-based LLM extraction.

``` bash
python scripts/demo_offline.py
```

## Run the Flask application

``` bash
python -m app.main
```

Then open:

``` text
http://127.0.0.1:5000
```

The frontend accepts:

-   bathroom image/plan,
-   budget,
-   theme,
-   required fixtures,
-   preferences.

The main design request follows:

``` text
POST /api/design
```

Additional endpoints include:

``` text
POST /api/recommend
POST /api/layout
POST /api/validate
POST /api/replace
GET  /api/result
```

------------------------------------------------------------------------

# End-to-End Design Flow

A complete design request follows:

``` text
Bathroom image + user requirements
                │
                ▼
       Requirements Parser
                │
                ▼
       Multimodal Spatial Extraction
                │
                ▼
            SpatialPlan
                │
                ▼
     Product Candidate Generation
                │
          ┌─────┴─────┐
          ▼           ▼
     Semantic      Neo4j KG
     Retrieval      Rules
          │           │
          └─────┬─────┘
                ▼
          Hybrid Ranking
                │
                ▼
         PuLP Optimization
                │
                ▼
            Top 3 Bundles
                │
                ▼
       3–5 Layout Candidates
                │
                ▼
     Deterministic Validation
                │
        ┌───────┴────────┐
        ▼                ▼
     Invalid            Valid
        │                │
        ▼                ▼
     Refinement        Scoring
        │                │
        └── Revalidate ──┘
                         │
                         ▼
                  Best Valid Layout
                         │
                         ▼
                Deterministic SVG
                         │
                         ▼
                  Flask Frontend
```

------------------------------------------------------------------------

# Product Replacement Flow

The system also supports follow-up changes such as:

> Replace the vanity.

The replacement flow is:

``` text
Selected product
      │
      ▼
Identify category
      │
      ▼
Retrieve alternative candidates
      │
      ▼
Apply KG compatibility
      │
      ▼
Recalculate accessories
      │
      ▼
Recalculate bundle cost
      │
      ▼
Re-check budget
      │
      ▼
Re-check infrastructure
      │
      ▼
Regenerate layout
      │
      ▼
Deterministic validation
      │
      ▼
Updated SVG
```

The goal is to avoid blindly rebuilding unrelated input while still
rerunning the stages whose outputs can change because of the
replacement.

------------------------------------------------------------------------

# Evaluation

The project includes synthetic evaluation scenarios covering:

-   small bathrooms,
-   medium bathrooms,
-   large bathrooms,
-   different door positions,
-   different door widths,
-   different door swing directions,
-   windows,
-   ventilation,
-   fixed obstacles,
-   infrastructure requirements,
-   infeasible rooms,
-   missing room dimensions,
-   unknown door swing.

Run:

``` bash
python scripts/run_evaluation.py
```

The evaluation framework measures:

### Spatial extraction

-   room dimension error,
-   door position error,
-   door width error,
-   door categorical accuracy,
-   window detection accuracy.

### Recommendation

-   required-category coverage,
-   missing categories,
-   duplicate categories,
-   compatibility violations.

### Optimization

-   budget violation,
-   budget shortfall,
-   accessory omission,
-   infeasible bundle detection.

### Layout

-   fixture overlap,
-   room-boundary violations,
-   door-swing violations,
-   clearance violations,
-   circulation violations,
-   infrastructure violations,
-   repair attempts,
-   repair success.

### Overall

-   fully valid design rate,
-   average layout validity,
-   recommendation violation rate,
-   optimization violation rate,
-   repair success rate.

------------------------------------------------------------------------

# Research / Engineering Design Principles

### Deterministic hard constraints

Hard constraints should not be delegated to an LLM when deterministic
validation is possible.

### Structured intermediate representations

Pipeline stages communicate through typed models rather than loosely
formatted strings.

### Explicit product relationships

Known incompatibilities and requirements are represented explicitly in
the Knowledge Graph.

### Semantic personalization

Embeddings handle fuzzy design language and aesthetic intent.

### Mathematical optimization

PuLP selects combinations under discrete constraints rather than relying
on an LLM to perform combinatorial optimization.

### Deterministic rendering

The final SVG is generated programmatically from validated geometry.

### Explainability

Pipeline decisions and rejection reasons are preserved in the result
trace so the system can explain why a product or layout was selected.

------------------------------------------------------------------------

# Limitations

This project is a **research/demo POC**, not professional architectural
software.

It should not be used as authoritative guidance for:

-   building-code compliance,
-   structural engineering,
-   plumbing design,
-   electrical design,
-   accessibility certification,
-   construction documentation,
-   professional architectural approval.

Real-product mode should only contain specifications that have actually
been sourced and verified from appropriate official product/technical
documentation.

The synthetic catalog is intentionally used for development and
evaluation so that the system does not make unsupported claims about
real Kohler product specifications.

------------------------------------------------------------------------

# Author

**Satyam Kumar**

B.Tech Computer Science & Engineering

Interests: Artificial Intelligence, Machine Learning, Computer Vision,
NLP, Generative AI, Knowledge Graphs, Recommendation Systems, and
AI-assisted spatial planning.

------------------------------------------------------------------------

## Project Thesis

> **AI proposes personalized product and spatial designs, while
> structured product knowledge, mathematical optimization, and
> deterministic geometric validation ensure that recommendations remain
> consistent with user requirements and physical constraints.**
