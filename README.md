
# AI FinTech Risk Intelligence Platform

**Portfolio-grade, production-style ML system demonstrating how a real FinTech / RegTech platform detects, explains, audits, and monitors risk in production.**

This repository intentionally avoids:
- tutorials
- demo shortcuts
- UI-first thinking
- “basic now, improve later” design

Everything here is designed **as if it will be reviewed by regulators, ML platform teams, and senior engineers**.

---

## What this system demonstrates

This platform shows **how I design real ML systems**, not models in isolation.

### Core capabilities
- Fraud & anomaly detection on structured transaction data
- Conduct & compliance risk detection on unstructured text
- Unified risk decisioning with explanations and evidence
- Centralized model registry, embeddings, and LLM usage
- Production-grade observability (metrics, traces, drift)
- Cloud-native deployment on AWS (ECS Fargate)

This is **not a SaaS product**.  
It is an **engineering demonstration**.

---

## Core ML use-cases (locked)

### 1. Fraud / Anomaly Detection (Structured)

**Data**
- Transactions
- Customer metadata
- Events
- Velocity & aggregation features

**Approach**
- Unsupervised / semi-supervised anomaly detection
- Feature contribution–based explanations
- Threshold calibration per environment

**Outputs**
- Fraud risk score
- Reason codes
- Model version
- Timestamped audit record

---

### 2. Conduct & Compliance Risk (Text + Hybrid)

**Data**
- Customer complaints
- Support messages
- Free-text notes

**Approach**
- TCF-style taxonomy
- Hybrid scoring:
  - deterministic rules (policy alignment)
  - ML classifier (generalization)
- Evidence spans and retrieval-backed explanations

**Outputs**
- Conduct risk score
- Risk category
- Evidence references
- Prompt + model versioning

---

## Unified Risk Intelligence Layer

Both ML pillars feed into a **single decisioning layer** producing an auditable, explainable outcome:


## RiskDecision:
- risk_score
- risk_category
- reason_codes
- evidence
- model_versions
- prompt_version
- timestamps
- trace_id

This object is the system of record.

⸻

# Architecture overview (high level)

           ┌───────────────┐
           │ API Gateway   │
           └───────┬───────┘
                   │
            ┌──────▼──────┐
            │ Risk API     │  (FastAPI, thin HTTP layer)
            └──────┬──────┘
                   │
      ┌────────────┼────────────┐
      │                            │
┌─────▼─────┐              ┌──────▼──────┐
│ Fraud ML  │              │ Conduct ML  │
│ (struct)  │              │ (text/hyb)  │
└─────┬─────┘              └──────┬──────┘
      │                            │
      └────────────┬───────────────┘
                   │
          ┌────────▼────────┐
          │ Decisioning     │
          │ + Audit Layer   │
          └────────┬────────┘
                   │
     ┌─────────────┼─────────────┐
     │                             │
┌────▼────┐              ┌────────▼────────┐
│ RDS     │              │ OpenSearch       │
│ (audit) │              │ (evidence)       │
└─────────┘              └─────────────────┘


⸻

# Repository structure (why it looks this way)

services/        → HTTP + worker entrypoints (thin, no ML logic)
libs/            → ALL shared ML, NLP, observability, decisioning logic
model_training/  → reproducible training pipelines
configs/         → locked taxonomy, thresholds, observability config
infra/           → AWS deployment mapping (IaC mindset)

Design rule:
If logic is shared between training and inference → it lives in libs/.

⸻

# LLM & NLP usage (strictly controlled)

This system does not scatter LLM calls.

Central rules
	•	One LLM Gateway
	•	Versioned prompts
	•	Logged inputs/outputs
	•	Retry + timeout policies
	•	No direct provider calls in APIs

LLMs are used only where justified, e.g.:
	•	structured extraction (when rules/ML are insufficient)
	•	explanation normalization (not decision-making)

Embeddings are single-implementation, reusable, cached.

⸻

# Observability (mandatory, first-class)

This platform treats observability as a core feature, not tooling glue.

Included
	•	Structured JSON logging
	•	Request IDs + trace IDs
	•	OpenTelemetry tracing
	•	Prometheus metrics
	•	Grafana dashboards
	•	Drift detection:
	•	structured feature drift (PSI)
	•	embedding distribution drift

Examples of tracked metrics
	•	Inference latency (p50 / p95 / p99)
	•	Error rate per model version
	•	Drift score over time
	•	Risk volume by category
	•	Flag precision (offline eval)

⸻

# Auditability & explainability

## Every decision is:
	•	reproducible
	•	attributable
	•	explainable

## Audit record includes
	•	input hashes
	•	feature snapshot references
	•	model + prompt versions
	•	reason codes
	•	evidence pointers
	•	timestamps
	•	trace IDs

## This design supports:
	•	internal reviews
	•	regulator discussions
	•	incident post-mortems

⸻

# AWS deployment model

Target environment: AWS ECS Fargate

Mapped services
	•	API Gateway → Risk API
	•	ECS Fargate → API + worker
	•	RDS Postgres → audit & decisions
	•	S3 → data, artifacts, evaluations
	•	OpenSearch → text evidence & retrieval
	•	AMP + AMG → metrics & dashboards
	•	CloudWatch → structured logs

Local Docker exists only to validate parity with cloud.

--- 
Final note

This repository represents how I think as an ML engineer, not how fast I can build demos.

If you are reviewing this:
	•	start with docs/architecture.md
	•	then inspect libs/
	•	then look at observability and decisioning

