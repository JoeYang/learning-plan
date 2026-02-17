# Quiz: Session 6 — Building a RAG Pipeline

**Instructions:** Choose the best answer for each question. Answers at the bottom.

---

### Q1. Fixed-size chunking splits text every N characters. What is its main problem?

A) It produces too few chunks
B) It can split mid-sentence or mid-word, breaking context
C) It requires an LLM to run
D) It only works with markdown files

### Q2. Why is semantic/section-aware chunking best for structured documents like incident reports and runbooks?

A) It produces the smallest chunks
B) It preserves the document's logical structure — an incident's root cause stays in one chunk instead of being split across two
C) It's the fastest chunking method
D) It doesn't require any configuration

### Q3. In a RAG pipeline, what is the purpose of the system prompt "Answer based ONLY on the provided documents"?

A) It makes the LLM respond faster
B) It prevents hallucination — the LLM should only use retrieved context, not its training knowledge
C) It reduces API costs
D) It improves retrieval quality

### Q4. What does metadata filtering do in vector search?

A) It improves the embedding quality
B) It narrows the search space to a specific document type or category BEFORE vector similarity is computed
C) It changes the embedding model
D) It sorts results alphabetically

### Q5. Why might unfiltered search be BETTER than filtered search for the query "What incidents affected HEDGE_FUND_A?"

A) Unfiltered search is always faster
B) Information about HEDGE_FUND_A is scattered across multiple document types (incidents, configs, runbooks) — filtering to one type misses the rest
C) Filtered search returns fewer results
D) Unfiltered search uses a better algorithm

### Q6. In the RAG eval, what does the "chocolate cake recipe" test verify?

A) That the LLM can follow recipes
B) That the LLM says "I don't have that information" instead of hallucinating an answer from its training data
C) That the retrieval works correctly
D) That the chunks are the right size

### Q7. You change your chunking strategy and the RAG eval score drops from 90% to 70%. What should you do?

A) Keep the new strategy — chunking doesn't matter much
B) Investigate which test cases failed, understand how the chunking change affected retrieval, and iterate
C) Switch to a bigger LLM
D) Remove the failing test cases

### Q8. In production RAG, who should decide which metadata filter to apply?

A) The user types the filter manually
B) The LLM decides — it classifies the query intent and selects appropriate filters via tool use
C) Filters are hardcoded per page
D) No filters should ever be used

### Q9. Chunk overlap (e.g., 50-100 tokens between chunks) exists to solve what problem?

A) It makes embeddings more accurate
B) It prevents important information from being split at a chunk boundary — the overlapping text appears in both chunks
C) It reduces storage costs
D) It speeds up vector search

### Q10. A RAG system retrieves 5 chunks but the answer is wrong. What are the two possible failure modes?

A) The LLM is too slow and the chunks are too big
B) RETRIEVAL failure (wrong chunks found) or GENERATION failure (right chunks found but LLM answered incorrectly)
C) The embedding model is broken and the database is corrupt
D) The query was too long and the answer was too short

---

## Answer Key

**Q1: B** — Fixed-size chunking blindly splits at character boundaries. "The connection pool had a hard lim" / "it of 200 connections" — the meaning is broken across two chunks, and neither chunk makes full sense on its own.

**Q2: B** — Semantic chunking uses document headings (##, ###) as split points. An incident's "Root Cause" section stays as one chunk instead of being arbitrarily split. This means when you search for "what caused the outage," you get the complete root cause, not half of it.

**Q3: B** — Without this constraint, the LLM might answer from its training data instead of the retrieved documents. For a trading system, this is dangerous — you want answers from YOUR incident reports, not generic knowledge. The chocolate cake test verified this works.

**Q4: B** — Metadata filtering is a pre-filter: "only search within runbooks" or "only search P1 incidents." It narrows the candidate set before vector similarity runs. This ensures all your top-K slots are filled with the right document type.

**Q5: B** — HEDGE_FUND_A appears in incident reports (affected client), system config (custom risk limits), and potentially runbooks. Filtering to just one doc type means you miss information from the others. Some queries genuinely need cross-document retrieval.

**Q6: B** — The chocolate cake question has nothing to do with trading. A well-behaved RAG system should say "I don't have that information" rather than hallucinating a recipe from Claude's training data. This tests that the "answer ONLY from documents" constraint works.

**Q7: B** — Same principle as Session 4's eval-driven approach. A score drop is a regression. Investigate which specific criteria failed, understand whether the new chunking split critical information across chunks, and fix it. The eval suite is your regression test.

**Q8: B** — Users shouldn't need to know internal metadata tags. The LLM classifies query intent ("troubleshooting" → runbooks, "what happened" → incidents) and applies the appropriate filter via tool use. This is the query routing pattern we discussed.

**Q9: B** — Without overlap, a sentence at a chunk boundary gets split in half. With 50-token overlap, the end of chunk N and the start of chunk N+1 share text, so the complete sentence appears in at least one chunk. This prevents information loss at boundaries.

**Q10: B** — RAG has two failure modes: (1) Retrieval failure — the vector search returned irrelevant chunks, so the LLM didn't have the right information. (2) Generation failure — the right chunks were retrieved but the LLM misinterpreted them or missed key details. The eval harness helps distinguish which one failed.
