# Learning Plan: Building AI Applications

**Start date:** 2026-02-15
**Target completion:** 2026-04-30
**Schedule:** 2-3 sessions/week, ~2 hours each
**Status:** in-progress

---

## Phase 1: Foundations & Prompt Engineering (Sessions 1-4)

### Session 1: LLM APIs & Prompt Engineering Fundamentals (2 hours)
**Objective:** Get hands-on with LLM APIs and master core prompting techniques
- [x] Set up dev environment: Python, OpenAI SDK, Anthropic SDK, API keys (20 min)
- [x] Call Claude and GPT-4 APIs programmatically — completions, chat, streaming (30 min)
- [x] Practice prompting techniques: zero-shot, few-shot, role-based, chain-of-thought (40 min)
- [x] Build a small CLI tool that takes a prompt template and runs it against multiple models (30 min)
**Key concepts:** API structure, tokens, temperature, system vs user prompts, CoT, few-shot learning
**Resources:** Anthropic docs, OpenAI Cookbook, promptingguide.ai

### Session 2: Structured Outputs & Tool Use (2 hours)
**Objective:** Control LLM outputs and enable function calling
- [x] Force structured JSON/XML outputs with schema validation (Pydantic) (30 min)
- [x] Implement OpenAI function calling / Anthropic tool use patterns (40 min)
- [x] Build a tool-using assistant: calculator, web search, file reader (30 min)
- [x] Experiment with self-consistency and tree-of-thought prompting on a reasoning task (20 min)
**Key concepts:** Structured outputs, function calling, tool use, Pydantic validation, ToT
**Resources:** Anthropic tool use docs, OpenAI function calling guide

### Session 3: Model Context Protocol (MCP) (2 hours)
**Objective:** Understand and build with Anthropic's MCP standard for tool integration
- [x] Read MCP specification: architecture, core primitives (tools, resources, prompts) (30 min)
- [x] Set up an MCP server locally — expose a simple tool (40 min)
- [x] Connect your MCP server to Claude Code or Claude Desktop (20 min)
- [x] Build a useful MCP server: e.g., query a database, read from a file system, or call an internal API (30 min)
**Key concepts:** MCP architecture, tools/resources/prompts primitives, MCP servers, stdio/SSE transport
**Resources:** modelcontextprotocol.io, Anthropic MCP course (Skilljar), github.com/modelcontextprotocol

### Session 4: Advanced Prompt Engineering & Security (2 hours)
**Objective:** Master defensive prompting and production prompt patterns
- [x] Study prompt injection attacks: direct injection, indirect injection, jailbreaking (30 min)
- [x] Implement defenses: input validation, output filtering, sandboxing (30 min)
- [x] Build a prompt template library for common tasks (code review, summarisation, extraction) (30 min)
- [x] Evaluate prompt quality: build a small eval harness that scores outputs against criteria (30 min)
**Key concepts:** Prompt injection, jailbreaking, defense strategies, prompt templating, eval basics
**Resources:** OWASP LLM Top 10, Anthropic prompt engineering guide

---

## Phase 2: RAG — Retrieval Augmented Generation (Sessions 5-8)

### Session 5: Embeddings & Vector Search Fundamentals (2 hours)
**Objective:** Understand how semantic search works under the hood
- [x] Learn embedding models: what they are, how they encode meaning (20 min)
- [x] Set up Chroma locally, index a set of documents (markdown, PDF, code) (40 min)
- [x] Implement basic vector similarity search and compare results (30 min)
- [x] Compare embedding models: OpenAI ada-002/3-small, Cohere embed, open-source alternatives (30 min)
**Key concepts:** Embeddings, cosine similarity, vector databases, indexing, Chroma
**Resources:** Chroma docs, OpenAI embeddings guide

### Session 6: Building a RAG Pipeline (2 hours)
**Objective:** Build an end-to-end RAG system from scratch
- [x] Implement document loading and chunking strategies (fixed-size, sentence-aware, semantic) (30 min)
- [x] Build a complete RAG pipeline: load → chunk → embed → store → retrieve → generate (40 min)
- [x] Add metadata filtering and compare retrieval quality (20 min)
- [x] Test your RAG against a set of questions and manually evaluate answers (30 min)
**Key concepts:** Chunking strategies, retrieval pipeline, metadata filtering, context window management
**Resources:** LangChain RAG tutorial, LlamaIndex getting started

### Session 7: Advanced RAG Patterns (2 hours)
**Objective:** Go beyond naive RAG with production-grade retrieval
- [x] Implement hybrid search: combine vector search with BM25/keyword search (30 min)
- [x] Add a reranking step (Cohere reranker or cross-encoder) and measure improvement (30 min)
- [x] Implement query transformation: HyDE (hypothetical document embeddings), multi-query (20 min)
- [x] Study advanced patterns: corrective RAG, adaptive RAG, parent-document retrieval (20 min)
- [x] Compare Chroma vs pgvector vs Qdrant — set up at least one alternative (20 min)
**Key concepts:** Hybrid search, reranking, HyDE, corrective RAG, multi-query retrieval
**Resources:** LangChain advanced RAG docs, LlamaIndex advanced patterns

### Session 8: RAG Evaluation & Production Readiness (2 hours)
**Objective:** Systematically evaluate and improve your RAG system
- [x] Set up RAGAS: measure faithfulness, answer relevancy, context precision, context recall (40 min)
- [x] Build an evaluation dataset: 20+ question-answer pairs for your document set (30 min)
- [x] Iterate: tune chunk size, overlap, retrieval k, reranking — track metrics (30 min)
- [x] Study Graph RAG and agentic RAG patterns (when the agent decides how to retrieve) (20 min)
**Key concepts:** RAGAS metrics, evaluation datasets, ablation testing, Graph RAG, agentic RAG
**Resources:** RAGAS docs, LangSmith evaluation guides

---

## Phase 3: AI Agents (Sessions 9-13)

### Session 9: Agent Fundamentals — ReAct & Tool Use (2 hours)
**Objective:** Build your first autonomous agent from scratch
- [x] Study the ReAct pattern: Reason → Act → Observe loop (20 min)
- [x] Build a ReAct agent from scratch (no framework) using Claude or GPT-4 (40 min)
- [x] Add tools: web search, calculator, code execution, file I/O (30 min)
- [x] Observe failure modes: looping, hallucinated actions, tool misuse (30 min)
**Key concepts:** ReAct, agent loop, tool calling, observation parsing, failure modes
**Resources:** ReAct paper, Anthropic agent patterns doc

### Session 10: LangChain & LangGraph for Agents (2 hours)
**Objective:** Build production agents with the dominant orchestration framework
- [x] LangChain basics: chains, agents, memory, callbacks (30 min)
- [x] Build a LangGraph agent: define nodes, edges, state, conditional routing (40 min)
- [x] Add persistence (checkpointing) and human-in-the-loop approval steps (30 min)
- [x] Compare LangGraph's graph-based approach vs simple chain-based agents (20 min)
**Key concepts:** LangChain, LangGraph, state graphs, checkpointing, human-in-the-loop
**Resources:** LangGraph docs, LangChain tutorials

### Session 11: Multi-Agent Systems (2 hours)
**Objective:** Coordinate multiple specialised agents working together
- [x] Study multi-agent patterns: supervisor, hierarchical, collaborative, debate (20 min)
- [x] Build a multi-agent system with LangGraph: researcher + writer + reviewer (40 min)
- [x] Try CrewAI or OpenAI Agents SDK for comparison: role-based multi-agent setup (30 min)
- [x] Evaluate: when do multi-agent systems outperform single agents? (30 min)
**Key concepts:** Agent handoffs, supervisor pattern, role specialisation, OpenAI Agents SDK, CrewAI
**Resources:** OpenAI Agents SDK docs, CrewAI docs, LangGraph multi-agent tutorial

### Session 12: Claude Agent SDK & Anthropic Patterns (2 hours)
**Objective:** Build agents using Anthropic's native SDK and patterns
- [ ] Set up Claude Agent SDK: agents, tools, sessions, error handling (30 min)
- [ ] Build a coding agent that can read files, run commands, and iterate on code (40 min)
- [ ] Study Claude Code's architecture: how it uses agents internally (20 min)
- [ ] Compare Claude Agent SDK vs LangGraph vs OpenAI Agents SDK on the same task (30 min)
**Key concepts:** Claude Agent SDK, agent sessions, tool orchestration, agentic coding
**Resources:** Anthropic Agent SDK docs, "Building agents with Claude Agent SDK" blog post

### Session 13: Agent Memory, Planning & Reliability (2 hours)
**Objective:** Make agents that remember, plan ahead, and recover from errors
- [ ] Implement short-term memory (conversation buffer) and long-term memory (vector store) (30 min)
- [ ] Add planning capabilities: task decomposition, subgoal generation (30 min)
- [ ] Implement retry logic, fallback strategies, and self-correction patterns (30 min)
- [ ] Build a mini project: an agent that can research a topic and produce a structured report (30 min)
**Key concepts:** Agent memory types, planning strategies, error recovery, self-reflection
**Resources:** LangGraph memory docs, Anthropic agent patterns

---

## Phase 4: AI for Software Engineering (Sessions 14-17)

### Session 14: AI-Assisted Code Review & Testing (2 hours)
**Objective:** Use AI to improve code quality systematically
- [ ] Study how AI code review tools work: CodeRabbit, Qodo, Claude Code /review (20 min)
- [ ] Build a custom AI code reviewer: takes a diff, produces structured feedback (40 min)
- [ ] Build an AI test generator: given a function, generate unit tests with edge cases (40 min)
- [ ] Integrate with a GitHub PR workflow (webhook or GitHub Action) (20 min)
**Key concepts:** Diff analysis, structured review output, test generation, CI/CD integration
**Resources:** CodeRabbit docs, GitHub Actions docs, Qodo docs

### Session 15: AI in CI/CD & Development Workflows (2 hours)
**Objective:** Embed AI into your team's development pipeline
- [ ] Build a GitHub Action that runs AI review on every PR (30 min)
- [ ] Create an AI-powered commit message generator and PR description writer (20 min)
- [ ] Build an AI documentation generator: reads code changes, updates docs (30 min)
- [ ] Study AI pair programming patterns: when AI helps vs hurts productivity (20 min)
- [ ] Design an "AI adoption playbook" for your organisation: which workflows benefit most (20 min)
**Key concepts:** GitHub Actions, automated review, documentation generation, AI adoption strategy
**Resources:** GitHub Actions docs, CodeRabbit integration guide

### Session 16: AI for Monitoring & Troubleshooting — Fundamentals (2 hours)
**Objective:** Use AI agents for production support of trading systems
- [ ] Study AIOps concepts: anomaly detection, log analysis, incident response (20 min)
- [ ] Build a log analysis agent: ingest logs, detect patterns, surface anomalies (40 min)
- [ ] Create an AI-powered runbook agent: given an alert, suggest diagnosis and remediation steps (40 min)
- [ ] Design an architecture for AI-assisted incident response for trading systems (20 min)
**Key concepts:** AIOps, log pattern detection, anomaly detection, intelligent runbooks, alert triage
**Resources:** Datadog AIOps docs, Splunk AI docs

### Session 17: AI for Trading System Operations (2 hours)
**Objective:** Build AI tools specifically for trading system support
- [ ] Build a latency analysis agent: parses timing logs, identifies bottlenecks, suggests fixes (40 min)
- [ ] Create an order flow analysis tool: detects rejection patterns, unusual trading activity (30 min)
- [ ] Build a system health dashboard agent: summarises system state from multiple data sources (30 min)
- [ ] Design an AI-powered alerting system: reduces noise, prioritises by business impact (20 min)
**Key concepts:** Latency analysis, order flow anomalies, system health summarisation, alert prioritisation
**Resources:** Internal trading system docs, AIOps best practices

---

## Phase 5: Fine-Tuning & Model Customisation (Sessions 18-20)

### Session 18: When and How to Fine-Tune (2 hours)
**Objective:** Understand the fine-tuning decision framework
- [ ] Study the decision tree: prompt engineering vs RAG vs fine-tuning (20 min)
- [ ] Fine-tune a small model using OpenAI's fine-tuning API on a classification task (40 min)
- [ ] Prepare a fine-tuning dataset: format, quality checks, train/val split (30 min)
- [ ] Compare fine-tuned model vs few-shot prompting on the same task (30 min)
**Key concepts:** Fine-tuning decision framework, data preparation, JSONL format, evaluation
**Resources:** OpenAI fine-tuning guide, Chip Huyen Ch7

### Session 19: LoRA, QLoRA & Parameter-Efficient Fine-Tuning (2 hours)
**Objective:** Fine-tune open-source models efficiently
- [ ] Set up Hugging Face Transformers + PEFT library (20 min)
- [ ] Fine-tune a 7-8B model with LoRA on a domain-specific dataset (40 min)
- [ ] Try QLoRA with Unsloth for faster, memory-efficient training (30 min)
- [ ] Evaluate: compare base model, LoRA-tuned, and QLoRA-tuned on your task (30 min)
**Key concepts:** LoRA, QLoRA, PEFT, Unsloth, rank selection, learning rate tuning
**Resources:** Hugging Face PEFT docs, Unsloth docs, Sebastian Raschka's LoRA tips

### Session 20: Alignment & Reinforcement Learning (2 hours)
**Objective:** Understand RLHF, DPO, and model alignment
- [ ] Study the alignment pipeline: pretraining → SFT → RLHF/DPO (20 min)
- [ ] Implement DPO training on a small model using TRL library (40 min)
- [ ] Create a preference dataset: chosen vs rejected responses for your domain (30 min)
- [ ] Compare DPO vs standard SFT on response quality (30 min)
**Key concepts:** RLHF, DPO, reward models, preference data, alignment
**Resources:** TRL docs, Hugging Face alignment handbook

---

## Phase 6: Production, Safety & Organisational Impact (Sessions 21-24)

### Session 21: Evaluation & Observability in Production (2 hours)
**Objective:** Monitor and evaluate AI systems systematically
- [ ] Set up LangSmith or Arize Phoenix for tracing and monitoring (30 min)
- [ ] Implement LLM-as-judge evaluation: define criteria, build scoring rubrics (30 min)
- [ ] Build a dashboard: track latency, cost, quality scores, error rates over time (30 min)
- [ ] Design an A/B testing framework for AI features (30 min)
**Key concepts:** LLM observability, tracing, LLM-as-judge, cost tracking, A/B testing
**Resources:** LangSmith docs, Arize Phoenix docs, Weights & Biases LLM docs

### Session 22: Guardrails, Safety & Responsible AI (2 hours)
**Objective:** Ship AI features safely with proper guardrails
- [ ] Set up Guardrails AI: input/output validation, PII detection, toxicity filtering (30 min)
- [ ] Try NeMo Guardrails: topical rails, safety rails, jailbreak detection (30 min)
- [ ] Build a safety pipeline: input guard → LLM → output guard → response (30 min)
- [ ] Study regulatory considerations for AI in financial services / trading (30 min)
**Key concepts:** Input/output guards, PII detection, content safety, regulatory compliance, Colang
**Resources:** Guardrails AI docs, NeMo Guardrails docs, OWASP LLM Top 10

### Session 23: Architecture & Deployment Patterns (2 hours)
**Objective:** Design production-grade AI application architectures
- [ ] Study LLM gateway patterns: routing, failover, cost optimisation, rate limiting (30 min)
- [ ] Design a complete AI application architecture: API → gateway → guardrails → LLM → eval (30 min)
- [ ] Implement streaming responses with guardrail validation (20 min)
- [ ] Study caching strategies: semantic caching, prompt caching (20 min)
- [ ] Build a deployment checklist for AI features at your organisation (20 min)
**Key concepts:** LLM gateways, model routing, semantic caching, streaming, deployment patterns
**Resources:** LiteLLM docs, AI gateway comparison guides

### Session 24: Capstone — AI Adoption Strategy & Demo (2 hours)
**Objective:** Synthesise everything into an organisational AI adoption plan
- [ ] Build a capstone demo: an AI agent for your organisation (e.g., internal docs Q&A, production support agent, or code review bot) (60 min)
- [ ] Write an AI adoption proposal: top 5 use cases, effort vs impact matrix, risks, timeline (30 min)
- [ ] Prepare a presentation: demo the agent, show evaluation results, present the adoption roadmap (30 min)
**Key concepts:** AI adoption strategy, use case prioritisation, ROI analysis, stakeholder communication
**Resources:** Everything from this course, your organisation's specific needs
