# Kohler AI Bathroom Planner and Designer

> An AI-assisted bathroom planning and product recommendation POC that combines multimodal spatial understanding, structured product knowledge, semantic retrieval, mathematical bundle optimization, deterministic geometry validation, layout refinement, and SVG-based 2D visualization.

---

## Tech Stack

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

The project demonstrates how generative AI can move beyond text generation into a **constraint-aware product configuration workflow**.

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