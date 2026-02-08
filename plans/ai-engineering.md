# Learning Plan: AI Engineering (Chip Huyen)

**Start date:** 2026-02-09
**Target completion:** 2026-03-15
**Schedule:** Daily, 1 hour each
**Status:** in-progress

---

## Day 1: The Rise of AI Engineering & Use Cases (1 hour)
**Objective:** Understand how foundation models emerged and what people build with them
- [ ] Read Ch1 pp.1–28: LLMs → foundation models → AI engineering (20 min)
- [ ] Read Ch1 pp.16–28: Use cases — coding, image/video, writing, education, bots, data org, automation (25 min)
- [ ] Write notes: which use cases are most relevant to you, key distinctions between LLMs and foundation models (15 min)
**Key concepts:** Foundation models, AI engineering vs traditional ML, use case landscape
**Resources:** Chapter 1 (first half)

## Day 2: Planning AI Apps & The AI Stack (1 hour)
**Objective:** Learn how to scope an AI project and understand the engineering stack
- [ ] Read Ch1 pp.28–35: Use case evaluation, expectations, milestone planning, maintenance (20 min)
- [ ] Read Ch1 pp.35–47: Three layers of the AI stack, AI eng vs ML eng vs full-stack eng (25 min)
- [ ] Write notes: sketch the three-layer stack from memory, list differences between AI eng and ML eng (15 min)
**Key concepts:** Project planning framework, AI stack layers, role distinctions
**Resources:** Chapter 1 (second half)

## Day 3: Training Data & Model Architecture (1 hour)
**Objective:** Understand what foundation models are trained on and how they're built
- [ ] Read Ch2 pp.49–58: Training data, multilingual models, domain-specific models (20 min)
- [ ] Read Ch2 pp.58–67: Model architecture (transformer details) (25 min)
- [ ] Write notes: summarize architecture choices and their tradeoffs (15 min)
**Key concepts:** Training data composition, multilingual/domain-specific tradeoffs, transformer architecture
**Resources:** Chapter 2 (first third)

## Day 4: Model Size & Post-Training (1 hour)
**Objective:** Understand scaling laws, SFT, and preference finetuning (RLHF)
- [ ] Read Ch2 pp.67–78: Model size, scaling laws (20 min)
- [ ] Read Ch2 pp.78–88: Supervised finetuning, preference finetuning (RLHF/DPO) (25 min)
- [ ] Write notes: diagram the post-training pipeline (pretrain → SFT → RLHF) (15 min)
**Key concepts:** Scaling laws, SFT, RLHF, DPO, post-training pipeline
**Resources:** Chapter 2 (middle third)

## Day 5: Sampling & Structured Outputs (1 hour)
**Objective:** Understand how models generate text and how to control their output
- [ ] Read Ch2 pp.88–99: Sampling fundamentals, strategies (temperature, top-k, top-p), test-time compute (25 min)
- [ ] Read Ch2 pp.99–111: Structured outputs, probabilistic nature of AI (20 min)
- [ ] Write notes: when to use which sampling strategy, structured output patterns (15 min)
**Key concepts:** Temperature, top-k, top-p, test-time compute, structured outputs, non-determinism
**Resources:** Chapter 2 (final third)

## Day 6: Evaluation Metrics & Exact Evaluation (1 hour)
**Objective:** Learn the mathematical foundations of model evaluation
- [ ] Read Ch3 pp.113–125: Evaluation challenges, entropy, cross entropy, perplexity (25 min)
- [ ] Read Ch3 pp.125–136: Functional correctness, similarity metrics, embeddings intro (20 min)
- [ ] Write notes: define perplexity in your own words, list similarity metrics and when to use each (15 min)
**Key concepts:** Entropy, perplexity, BLEU, ROUGE, BERTScore, embeddings
**Resources:** Chapter 3 (first half)

## Day 7: AI as a Judge & Comparative Evaluation (1 hour)
**Objective:** Learn modern evaluation approaches using AI models as evaluators
- [ ] Read Ch3 pp.136–148: Why AI as judge, how to use it, limitations (20 min)
- [ ] Read Ch3 pp.148–156: Ranking models with comparative evaluation, challenges (25 min)
- [ ] Write notes: when to use AI-as-judge vs exact metrics, comparative eval pitfalls (15 min)
**Key concepts:** AI-as-judge, pairwise comparison, ELO ratings, evaluation biases
**Resources:** Chapter 3 (second half)

## Day 8: Evaluation Criteria for AI Systems (1 hour)
**Objective:** Define what "good" means for an AI application
- [ ] Read Ch4 pp.159–172: Domain-specific capability, generation capability (hallucination, toxicity, coherence) (25 min)
- [ ] Read Ch4 pp.172–179: Instruction-following capability, cost and latency (20 min)
- [ ] Write notes: build a checklist of evaluation criteria you'd use for a real project (15 min)
**Key concepts:** Hallucination detection, toxicity, faithfulness, instruction following, cost/latency tradeoffs
**Resources:** Chapter 4 (first half)

## Day 9: Model Selection & Evaluation Pipeline Design (1 hour)
**Objective:** Learn how to pick the right model and set up systematic evaluation
- [ ] Read Ch4 pp.179–200: Selection workflow, build vs buy, navigating public benchmarks (25 min)
- [ ] Read Ch4 pp.200–208: Evaluate all components, create guidelines, define methods & data (20 min)
- [ ] Write notes: outline a model selection process for a hypothetical project (15 min)
**Key concepts:** Model selection workflow, build vs buy, benchmark interpretation, eval pipeline design
**Resources:** Chapter 4 (second half)

## Day 10: Prompting Fundamentals & Best Practices (1 hour)
**Objective:** Master prompt engineering techniques
- [ ] Read Ch5 pp.211–220: Zero-shot, few-shot, system vs user prompt, context length (20 min)
- [ ] Read Ch5 pp.220–234: Clear instructions, context, task decomposition, chain-of-thought, tools (25 min)
- [ ] Write notes: create a prompt engineering checklist from the best practices (15 min)
**Key concepts:** Zero/few-shot learning, system prompts, chain-of-thought, prompt iteration
**Resources:** Chapter 5 (first half)

## Day 11: Defensive Prompt Engineering (1 hour)
**Objective:** Understand prompt security — attacks and defenses
- [ ] Read Ch5 pp.235–248: Proprietary prompts, jailbreaking, prompt injection, information extraction (25 min)
- [ ] Read Ch5 pp.248–251: Defenses against prompt attacks (20 min)
- [ ] Write notes: catalog attack types and corresponding defenses (15 min)
**Key concepts:** Jailbreaking, prompt injection, data exfiltration, defense strategies
**Resources:** Chapter 5 (second half)

## Day 12: RAG Architecture & Retrieval (1 hour)
**Objective:** Understand retrieval-augmented generation end to end
- [ ] Read Ch6 pp.253–268: RAG architecture, retrieval algorithms (vector search, keyword, hybrid) (25 min)
- [ ] Read Ch6 pp.268–274: Retrieval optimization, RAG beyond text (20 min)
- [ ] Write notes: diagram a RAG pipeline, list retrieval optimization techniques (15 min)
**Key concepts:** RAG architecture, vector search, hybrid retrieval, chunking, reranking
**Resources:** Chapter 6 (first half)

## Day 13: Agents & Memory (1 hour)
**Objective:** Understand agentic AI patterns — tools, planning, and memory
- [ ] Read Ch6 pp.275–298: Agent overview, tools, planning strategies (ReAct, function calling) (25 min)
- [ ] Read Ch6 pp.298–305: Agent failure modes, evaluation, memory patterns (20 min)
- [ ] Write notes: compare agent planning approaches, list common failure modes (15 min)
**Key concepts:** Tool use, ReAct, function calling, agent evaluation, short/long-term memory
**Resources:** Chapter 6 (second half)

## Day 14: Finetuning — When and Why (1 hour)
**Objective:** Decide when finetuning is the right approach
- [ ] Read Ch7 pp.307–316: Finetuning overview, reasons to finetune, reasons not to (25 min)
- [ ] Read Ch7 pp.316–319: Finetuning vs RAG — when to use which (20 min)
- [ ] Write notes: decision tree for "should I finetune?" (15 min)
**Key concepts:** Finetuning tradeoffs, finetuning vs RAG vs prompt engineering decision framework
**Resources:** Chapter 7 (first third)

## Day 15: Memory Bottlenecks & Quantization (1 hour)
**Objective:** Understand the computational constraints of finetuning
- [ ] Read Ch7 pp.319–328: Backpropagation refresher, trainable params, memory math (25 min)
- [ ] Read Ch7 pp.328–332: Numerical representations, quantization (INT8, INT4, mixed precision) (20 min)
- [ ] Write notes: calculate memory requirements for a sample model (15 min)
**Key concepts:** GPU memory math, FP16/BF16/INT8/INT4, quantization methods
**Resources:** Chapter 7 (middle third)

## Day 16: Finetuning Techniques (1 hour)
**Objective:** Learn practical finetuning methods — LoRA, merging, and tactics
- [ ] Read Ch7 pp.332–347: Parameter-efficient finetuning (LoRA, QLoRA, adapters) (25 min)
- [ ] Read Ch7 pp.347–361: Model merging, multi-task finetuning, finetuning tactics (20 min)
- [ ] Write notes: compare PEFT methods, when to use model merging (15 min)
**Key concepts:** LoRA, QLoRA, adapters, model merging, multi-task finetuning
**Resources:** Chapter 7 (final third)

## Day 17: Data Curation & Synthesis (1 hour)
**Objective:** Learn how to build and augment datasets for AI
- [ ] Read Ch8 pp.363–380: Data quality, coverage, quantity, acquisition, annotation (25 min)
- [ ] Read Ch8 pp.380–396: Data augmentation, AI-powered synthesis, model distillation (20 min)
- [ ] Write notes: list data quality checks, when to use synthetic data (15 min)
**Key concepts:** Data quality dimensions, annotation strategies, synthetic data, distillation
**Resources:** Chapter 8 (first two-thirds)

## Day 18: Data Processing & Inference Fundamentals (1 hour)
**Objective:** Finish dataset engineering, start understanding inference
- [ ] Read Ch8 pp.396–403: Inspect, deduplicate, clean, filter, format data (15 min)
- [ ] Read Ch9 pp.405–419: Inference overview, performance metrics (latency, throughput, TTFT) (25 min)
- [ ] Read Ch9 pp.419–425: AI accelerators (GPUs, TPUs) (20 min)
**Key concepts:** Data deduplication, inference metrics (TTFT, TPS, TPOT), GPU/TPU landscape
**Resources:** Chapter 8 (end) + Chapter 9 (first half)

## Day 19: Inference Optimization Techniques (1 hour)
**Objective:** Learn how to make models faster and cheaper in production
- [ ] Read Ch9 pp.426–440: Model optimization (pruning, distillation, compilation) (25 min)
- [ ] Read Ch9 pp.440–447: Inference service optimization (batching, KV cache, speculative decoding) (20 min)
- [ ] Write notes: rank optimization techniques by impact and implementation effort (15 min)
**Key concepts:** Pruning, distillation, continuous batching, KV cache, speculative decoding, PagedAttention
**Resources:** Chapter 9 (second half)

## Day 20: AI Engineering Architecture (1 hour)
**Objective:** Understand the full production architecture for AI applications
- [ ] Read Ch10 pp.449–465: Context enhancement, guardrails, model router/gateway, caching, agent patterns (25 min)
- [ ] Read Ch10 pp.465–473: Monitoring, observability, pipeline orchestration (20 min)
- [ ] Write notes: draw the full architecture diagram from memory (15 min)
**Key concepts:** Guardrails, model routing, semantic caching, observability, orchestration
**Resources:** Chapter 10 (first half)

## Day 21: User Feedback & Book Wrap-Up (1 hour)
**Objective:** Learn feedback loops and consolidate everything
- [ ] Read Ch10 pp.474–492: Conversational feedback, feedback design, limitations (25 min)
- [ ] Read Epilogue pp.495–496 (5 min)
- [ ] Final review: write a 1-page summary of the book's key frameworks and your top takeaways (30 min)
**Key concepts:** Implicit/explicit feedback, feedback flywheel, continuous improvement
**Resources:** Chapter 10 (second half) + Epilogue
