# Topic: FDE Production AI Systems — Closing the Demo-to-Production Gap

## Why I Want to Learn This
Track 3 of the FDE (Forward Deployed Engineer) path, finance-vertical profile. The prototyping track (TypeScript) proves I can build a client-facing demo fast; this track proves I can take that demo and make it something a client would trust in production — retrieval that's actually grounded, agents that fail gracefully instead of hallucinating a tool call, and evals that catch regressions before a client does. FDE postings in finance consistently list SQL fluency, messy-data ingestion, eval harnesses, and guardrails as baseline expectations, not nice-to-haves — this course exists to make sure none of those are gaps when I'm in front of a client.

## Current Knowledge Level
intermediate — completed Claude Code Mastery and Building AI Applications (RAG basics, agents, tool use, MCP, Claude Agent SDK). Strong Python and low-latency C++ background gives me the engineering discipline; what's missing is production-grade rigor on retrieval quality, agent reliability under failure, and systematic evaluation — the parts that separate a demo from something a client deploys.

## Goal
Be able to:
1. Design and tune a retrieval pipeline (chunking, embeddings, hybrid search, reranking) against messy real-world finance documents, and defend chunking/retrieval choices with evaluation numbers, not intuition
2. Write production-quality SQL against relational schemas and stand up ingestion pipelines for the mix of sources a client actually hands over (databases, CSVs, REST APIs, PDFs)
3. Build multi-step agents with reliable tool-use using both LangGraph (explicit graphs, state, checkpointing) and the Claude Agent SDK/MCP, and know which tool fits which failure mode
4. Build eval harnesses — golden sets, LLM-as-judge with judge validation, CI regression gates — that catch retrieval and generation regressions automatically
5. Harden a system against prompt injection, add tracing/observability, and reason explicitly about cost and latency trade-offs
6. Ship a finance-vertical RAG + agent system end to end, with a published eval report and a written trade-off memo a client stakeholder could read

## Capstone: what artefact proves mastery?
Per-phase artefacts under `artefacts/fde-production-ai-systems/phase-N/`, each a working piece of the same finance-vertical system:

- **Phase 1** — `artefacts/fde-production-ai-systems/phase-1/retrieval-eval-report.md` — a retrieval pipeline over public financial documents (SEC filings, earnings-call transcripts) with a chunking/embedding/hybrid-search/reranking comparison table and retrieval-quality metrics (recall@k, MRR) across configurations
- **Phase 2** — `artefacts/fde-production-ai-systems/phase-2/ingestion-pipeline/` — a working ingestion pipeline that pulls from at least three source types (SQL DB, CSV, REST API or unstructured filing) into a unified store, with incremental sync and a data-quality checklist
- **Phase 3** — `artefacts/fde-production-ai-systems/phase-3/agent-reliability-report.md` — the same agent task implemented once in LangGraph and once on the Claude Agent SDK/MCP, with a side-by-side reliability comparison (retry behavior, state recovery, structured-output adherence) under injected tool failures
- **Phase 4** — `artefacts/fde-production-ai-systems/phase-4/eval-harness/` — a golden-set eval harness with LLM-as-judge scoring (judge validated against human-labeled examples), wired into a CI regression gate that fails the build on a retrieval or generation quality drop
- **Phase 5 (course capstone)** — `artefacts/fde-production-ai-systems/phase-5/capstone/` — the finance-vertical RAG + agent system (querying public SEC filings and earnings-call transcripts) fully assembled: hardened against prompt injection, instrumented with tracing and cost/latency dashboards, with a **published eval report** (`eval-report.md`) and a **written trade-off memo** (`trade-off-memo.md`) covering the retrieval, orchestration, and cost/latency decisions made across the course — the artefact I'd walk a client technical lead through.

## Resources (optional)
- Anthropic docs: contextual retrieval, tool use, MCP specification
- LangGraph docs (graphs, state, checkpointing, human-in-the-loop)
- RAGAS and TruLens for retrieval/generation evaluation
- LlamaIndex and LangChain retrieval modules for hybrid search/reranking reference implementations
- SEC EDGAR full-text search API and financial-statement datasets for source documents
- Cohere Rerank / cross-encoder rerankers for the reranking sessions
- OpenTelemetry + Langfuse or Arize Phoenix for tracing/observability
- Builds on `topics/claude-certified-architect.md` (agent/MCP patterns) and sits downstream of `topics/typescript-crash-course.md` (the prototype front-end this system will eventually serve)

## Time Estimate
18 sessions, ~1.5 hrs each, 4 sessions/week — about 5 weeks (2026-09-14 to 2026-11-13)

## Priority
high
