[![Portfolio](https://img.shields.io/badge/Portfolio-dmiruke.dev-6aa7ff?style=for-the-badge&logo=github)](https://dmiruke-ai.github.io/dmiruke.github.io/)
[![Source Code](https://img.shields.io/badge/Source%20Code-AgenticDevops-b48cff?style=for-the-badge&logo=github)](https://github.com/dmiruke-ai/AgenticDevops)
[![Demo](https://img.shields.io/badge/Live%20Demo-agenticdevops--demo-5fc77a?style=for-the-badge)](https://github.com/dmiruke-ai/agenticdevops-demo)
[![Tests](https://img.shields.io/badge/Tests-426%20passing-brightgreen?style=for-the-badge)]()

# AgenticDevops — AI DevOps Agent Platform

> Portfolio showcase for **AgenticDevops** — an AI-powered multi-agent platform that converts conversational intent into production-ready cloud infrastructure.  
> Source code: **[dmiruke-ai/AgenticDevops](https://github.com/dmiruke-ai/AgenticDevops)**

---

## What This Platform Demonstrates

**Not** "call an LLM and hope for the best." This is a full agentic control plane with deterministic safety gates, confidence-tracked intent, and smart error recovery — the complete picture of what a production-grade AI DevOps agent actually needs:

### Intent Engine
- **4-band confidence system** — `stated` · `confirmed` · `inferred` · `speculative` — prevents execution on uncertain intent
- **IntentSpec** — canonical intermediate representation capturing cloud provider, compute platform, region, constraints, with per-field confidence
- **Conflict detection** — identifies contradictory constraints before generation begins
- **Session isolation** — multi-tenant, Tenant A cannot read or affect Tenant B

### Security (OPA Intent Gate)
- **Wildcard IAM** (`*`) — blocked at intent layer before any generation
- **Open security groups** (`0.0.0.0/0`) — blocked except explicit 80/443
- **Prompt injection** — 15 patterns detected and blocked
- **Confidence gate** — `confirmed` required to generate Terraform; `confirmed + approval` required to apply or delete

### Generation
- **Terraform generator** — VPC, EKS, IAM, security groups, from IntentSpec
- **CI/CD generator** — GitHub Actions workflows keyed to the generated infrastructure
- **IAM policy generator** — least-privilege policies derived from intent constraints

### Validation & Smart Replanning
- **15 error classifiers** — `INVALID_REFERENCE`, `MISSING_REQUIRED`, `CIRCULAR_DEPENDENCY`, `SECURITY_VIOLATION`, and 11 more
- **Targeted fix strategies** — each error type has a specific replan action, not naive retry
- **Chain-of-Thought planner** — reasoning trace preserved for audit

### FinOps (Tree-of-Thought)
- **Multi-option evaluation** — Lambda vs ECS vs EKS vs EC2 scored against budget and requirements
- **Cost delta calculation** — monthly cost impact surfaced before approval
- **Blast radius** — count of creates, updates, and deletes surfaced to the approver

### Human-in-the-Loop
- **Approval gate** — blast radius + cost delta shown before destructive operations
- **5-minute timeout** — auto-reject on operator inaction
- **Audit trail** — every approval/rejection recorded with timestamp

### Observability
- **30+ Prometheus metrics** — intent parse latency, generation time, replan count, approval decisions, OPA gate outcomes
- **Jaeger traces** — distributed trace per agent pipeline execution
- **Grafana dashboards** — per-tenant throughput, error rates, cost trends

---

## Architecture

```
 Natural Language Input
         │
         ▼
 ┌──────────────────┐     ┌──────────────────┐
 │  Intent Parser   │────▶│ Conflict Detector │
 │  (LangGraph)     │     └──────────────────┘
 └──────────────────┘              │
         │                         ▼
         │              ┌──────────────────┐
         │              │   OPA Security   │  ← blocks wildcard IAM,
         │              │   Intent Gate    │    open SGs, injection
         │              └──────────────────┘
         │                         │
         ▼                         ▼
 ┌────────────────────────────────────────┐
 │          IntentSpec (canonical)        │
 │  confidence: stated│confirmed│inferred │
 └────────────────────────────────────────┘
         │
   ┌─────┼──────┬───────────────┐
   ▼     ▼      ▼               ▼
 TF    CI/CD   IAM          FinOps Scorer
 Gen   Gen     Gen          (Tree-of-Thought)
         │
         ▼
 ┌──────────────────────────────────────────┐
 │  Validation Loop                         │
 │  Error → Classify (15 types) → Targeted  │
 │  Fix → Regenerate                        │
 └──────────────────────────────────────────┘
         │
         ▼
 ┌──────────────────────────────────────────┐
 │  Approval Gate                           │
 │  Blast Radius · Cost Delta · Human HITL  │
 └──────────────────────────────────────────┘
         │
         ▼
  [Terraform Apply]
```

---

## Key Metrics

| Metric | Value |
|--------|-------|
| **Tests passing** | 426 |
| **OPA policies** | 4 active (IAM, SG, injection, structure) |
| **Error classifiers** | 15 types with targeted fix strategies |
| **Confidence bands** | 4 (stated · confirmed · inferred · speculative) |
| **Prometheus series** | 30+ custom metrics |
| **Sprints completed** | 5 (Foundation → Intent → DAG+FinOps → Validation+Security → Observability+HITL) |

---

## Sprint Story

| Sprint | Focus | Outcome |
|--------|-------|---------|
| Sprint 0 | Foundation — FastAPI skeleton, LangGraph wiring, project structure | Running agent pipeline |
| Sprint 1 | Intent Engine — IntentSpec schema, 4-band confidence, session manager | Natural language → structured intent |
| Sprint 2 | DAG + FinOps + Generators — Tree-of-Thought FinOps, Terraform/CI/CD gen | End-to-end: intent → infrastructure files |
| Sprint 3 | Validation + Security — 15-type error classifier, OPA gate, smart replan | Deterministic safety + self-healing |
| Sprint 4 | Observability + HITL — 30+ Prom metrics, Jaeger, Grafana, approval gate | Production-observable + human control |

---

## Quick Demo

```bash
git clone https://github.com/dmiruke-ai/AgenticDevops.git
cd AgenticDevops
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
make demo-quick   # < 2 minutes, no Docker required
```

Three scenarios in under 2 minutes:
1. **Intent → Infrastructure** — "Deploy a scalable web app on AWS with EKS and CI/CD" → `main.tf` + `deploy.yml`
2. **Error handling** — INVALID_REFERENCE → classify → smart replan → fixed in 1 attempt
3. **FinOps** — $100/month budget → Lambda recommended at $11.50/mo (88% under budget)

---

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](https://github.com/dmiruke-ai/AgenticDevops/blob/main/architecture/ARCHITECTURE.md) | System design, data flow, component responsibilities |
| [FinOps Analysis](https://github.com/dmiruke-ai/AgenticDevops/blob/main/docs/FINOPS_ANALYSIS.md) | Tree-of-Thought cost scoring methodology |
| [Sprint 3 Summary](https://github.com/dmiruke-ai/AgenticDevops/blob/main/docs/SPRINT_3_SUMMARY.md) | Validation + Security implementation |
| [Sprint 4 Summary](https://github.com/dmiruke-ai/AgenticDevops/blob/main/docs/SPRINT_4_SUMMARY.md) | Observability + HITL implementation |
| [Demo Preview](https://github.com/dmiruke-ai/AgenticDevops/blob/main/docs/DEMO_PREVIEW.md) | Screenshots and full output preview |

---

## Stack

**LangGraph** · **FastAPI** · **Terraform** · **OPA (Rego)** · **OpenTelemetry** · **Prometheus** · **Grafana** · **Jaeger** · **Redis** · **Python 3.11+**

---

## Author

**Dattaram Miruke** — Principal AI Platform Architect · DevOps · Kubernetes · AWS  
[dmiruke@gmail.com](mailto:dmiruke@gmail.com) · [github.com/dmiruke-ai](https://github.com/dmiruke-ai) · [dmiruke.dev](https://dmiruke.dev)
