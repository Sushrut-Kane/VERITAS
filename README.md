# VERITAS — AI Product Data Firewall

**UniHack 2026 Submission** · Challenge: *AI-Powered Product Intelligence for Industrial Commerce*

> Instead of asking AI to generate more product data, VERITAS makes AI-generated product data trustworthy before it reaches the catalog.

---

## 1. The Problem

Industrial companies pull product information from scattered, messy sources — spec-sheet PDFs, catalog scans, technical drawings, vendor websites. Using an LLM/VLM to turn that mess into structured catalog data is easy to demo and dangerous to ship: every generated field is a potential hallucination, a misread unit, a fact lifted out of context, or a contradiction between two source documents that nobody caught. Most "AI enrichment" tools optimize for **coverage** (fill every field) with no systematic way to say *how sure are we, and why*.

## 2. The Idea

VERITAS is not another extraction pipeline — it's a **firewall** that sits between AI-generated product attributes and the live catalog. Every attribute VERITAS emits is treated as a **claim**, and a claim only reaches the catalog after it survives:

1. **Evidence linking** — every claim is tied to the exact document, page/region, and source text it came from.
2. **Cross-document verification** — claims are checked against every other source that mentions the same attribute, using a GraphRAG-style traversal of an evidence knowledge graph.
3. **Adversarial red-teaming** — a dedicated LangGraph agent actively tries to break each claim: hunting for hallucination, unit/format errors, lost context ("high temperature" relative to what?), and unsupported inference.
4. **Classification** — each attribute is labeled **Verified / Derived / Inferred / Conflicting / Unsupported**, with a confidence score and a human-readable justification.
5. **Policy decision** — a policy engine routes each attribute to **Publish**, **Send to Human Review**, or **Block**, based on classification, confidence, and business rules (e.g. safety-critical fields always route to review).

The output is not just "structured product data" — it's structured product data with a **receipt**: what it says, where it came from, how confident VERITAS is, and why.

## 3. Core Differentiator (why this wins on the rubric)

| Judging Criteria | How VERITAS addresses it |
|---|---|
| **Accuracy & Consistency** | Cross-document verification + red-team agent actively hunts inconsistencies before publish, not after. |
| **AI Validation & Enrichment** | Validation *is* the product — every enrichment ships with evidence, confidence, and reasoning. |
| **Structured Data Generation** | LangGraph extraction pipeline emits a typed, schema-conformant attribute graph, not free text. |
| **Scalable Catalog Engine** | Neo4j evidence graph + Postgres attribute store + async FastAPI pipeline designed for batch catalog ingestion, not single-SKU demos. |
| **Explainability** (implicit ask: "reliable, explainable outputs") | Classification + reasoning + policy decision are first-class, user-facing outputs, not debug logs. |

## 4. System Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              INGESTION LAYER                             │
│   PDFs · Spec sheets · Catalog images · Technical docs · Website scrapes │
└───────────────────────────────────┬────────────────────────────────────-┘
                                     ▼
                     ┌───────────────────────────────┐
                     │   EXTRACTION AGENT (LLM/VLM)   │   → raw claims + bbox/source span
                     └───────────────┬───────────────-┘
                                     ▼
                     ┌───────────────────────────────┐
                     │   EVIDENCE GRAPH BUILDER       │   → Neo4j: Attribute─EVIDENCED_BY─Source
                     └───────────────┬───────────────-┘
                                     ▼
                     ┌───────────────────────────────┐
                     │  CROSS-DOC VERIFIER (GraphRAG) │   → agrees / conflicts / no corroboration
                     └───────────────┬───────────────-┘
                                     ▼
                     ┌───────────────────────────────┐
                     │   RED-TEAM AGENT (LangGraph)   │   → adversarial probes: hallucination,
                     │                                 │      unit errors, context loss, unsupported
                     └───────────────┬───────────────-┘
                                     ▼
                     ┌───────────────────────────────┐
                     │   CLASSIFICATION ENGINE        │   → Verified/Derived/Inferred/
                     │                                 │      Conflicting/Unsupported + confidence
                     └───────────────┬───────────────-┘
                                     ▼
                     ┌───────────────────────────────┐
                     │   POLICY ENGINE                │   → Publish / Human Review / Block
                     └───────────────┬───────────────-┘
                                     ▼
        ┌────────────────────────────┴────────────────────────────┐
        ▼                                                          ▼
┌───────────────────┐                                  ┌───────────────────────┐
│  CATALOG (Postgres)│                                  │  REVIEW DASHBOARD      │
│  published attrs   │                                  │  (Next.js/React)       │
└───────────────────┘                                  └───────────────────────┘
```

## 5. Tech Stack

| Layer | Technology |
|---|---|
| Extraction & agents | Python, LangGraph, LLM (Claude) + VLM for image/PDF understanding |
| Knowledge graph | Neo4j (evidence graph), GraphRAG-style retrieval |
| Structured storage | PostgreSQL (attributes, audit trail, policy decisions) |
| Embeddings | For semantic cross-document matching & retrieval |
| Backend API | FastAPI (async), Pydantic schemas |
| Frontend | Next.js / React, Tailwind |
| Auth / infra | JWT auth, Docker Compose for local dev |

See `IMPLEMENTATION_PLAN.md` for the build sequence and `INTEGRATION.md` for API contracts and how the pieces wire together.

## 6. Repository Structure

```
veritas/
├── backend/
│   ├── app/
│   │   ├── api/                  # FastAPI routers
│   │   ├── agents/                # LangGraph graphs: extraction, red-team, verifier
│   │   ├── graph/                 # Neo4j client + Cypher queries
│   │   ├── db/                    # Postgres models (SQLAlchemy) + migrations (Alembic)
│   │   ├── policy/                # Policy engine rules
│   │   ├── schemas/                # Pydantic models (Attribute, Evidence, Verdict, PolicyDecision)
│   │   └── core/                   # config, logging, security
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── app/                        # Next.js app router
│   │   ├── upload/                 # document ingestion UI
│   │   ├── catalog/                # published attribute browser
│   │   ├── review/                 # human-in-the-loop review queue
│   │   └── attribute/[id]/         # evidence + reasoning drill-down
│   └── components/
├── docs/
│   ├── IMPLEMENTATION_PLAN.md
│   └── INTEGRATION.md
├── docker-compose.yml
└── README.md
```

## 7. Quick Start (local dev)

```bash
# 1. Clone and start infra (Postgres + Neo4j)
docker compose up -d db neo4j

# 2. Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# 3. Frontend
cd frontend
npm install
npm run dev
```

Environment variables required (see `.env.example`): `DATABASE_URL`, `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `ANTHROPIC_API_KEY`, `JWT_SECRET`.

## 8. Demo Script (for judging)

1. Upload two conflicting spec sheets for the same SKU (e.g. one lists "Max Temp: 80°C", another "176°F" that's actually 80°F — an intentional error).
2. Show the extraction pipeline pull both claims with evidence spans.
3. Show the red-team agent flag the unit conversion mismatch as **Conflicting**.
4. Show the policy engine block that attribute and route it to the human review queue with a plain-English explanation.
5. Show a clean, corroborated attribute pass through as **Verified** and auto-publish to the catalog.
6. Drill into an attribute's detail page to show the full evidence graph and reasoning trail.

## 9. Team

Built for **UniHack 2026** (Hack2skill × Unilog). Registrations open through 23 Aug 2026; evaluations 24 Aug – 1 Sep; finale 4 Sep 2026.

## 10. License

TBD — note UniHack's terms transfer IP rights for winning solutions to the organizers upon award confirmation; keep this repo private until that's resolved if it matters to your team.
