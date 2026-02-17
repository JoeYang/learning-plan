# Quiz: Session 5 — Embeddings & Vector Search Fundamentals

**Instructions:** Choose the best answer for each question. Answers at the bottom.

---

### Q1. What does an embedding model produce?

A) A text summary of the input
B) A fixed-length vector of numbers representing the meaning of the input text
C) A probability distribution over possible next words
D) A JSON object with extracted entities

### Q2. Two texts have cosine similarity of 0.95. What does this mean?

A) They share 95% of the same words
B) Their meaning vectors point in nearly the same direction — they are semantically very similar
C) One text is 95% as long as the other
D) They were written by the same author

### Q3. Why can't you use a chat model (like Claude) as an embedding model?

A) Chat models are too expensive
B) Chat models generate text output, not fixed-length numerical vectors — they're different architectures trained for different tasks
C) Chat models can't process short text
D) Chat models don't understand meaning

### Q4. What is the main advantage of semantic search over keyword (BM25) search?

A) It's faster
B) It finds documents with the same MEANING even when the WORDS are completely different
C) It requires less storage
D) It doesn't need a database

### Q5. You have 1 million documents to search. Why not just use a cross-encoder for every query?

A) Cross-encoders are less accurate
B) Cross-encoders require feeding (query + document) together into the model for EACH document — 1M model calls per query is far too slow
C) Cross-encoders don't work with text
D) Cross-encoders need GPUs

### Q6. What is the "Matryoshka" trick in OpenAI's text-embedding-3 models?

A) Nesting multiple models inside each other
B) The model is trained so you can truncate the vector to fewer dimensions and it still works, trading quality for speed/storage
C) Running the same text through the model multiple times
D) Compressing the model weights

### Q7. The typical dimension sweet spot for embedding models is around 768-1536. Why not always use the maximum (e.g., 3072)?

A) Higher dimensions are always worse
B) Diminishing quality returns, but storage and search costs scale linearly — double the dims means double the compute per search
C) The API doesn't support higher dimensions
D) Higher dimensions cause more errors

### Q8. What is hybrid search?

A) Using two different LLMs and picking the best answer
B) Combining keyword search (BM25) with semantic search (embeddings) to get both exact matches and meaning-based matches
C) Searching across two different databases
D) Using both CPU and GPU for search

### Q9. In a production RAG pipeline, what role does a cross-encoder typically play?

A) It replaces the embedding model entirely
B) It reranks the top N candidates from initial retrieval, providing more accurate relevance scores
C) It generates the final answer
D) It indexes documents

### Q10. You indexed trading documents and searched for "billing mistake with wrong amount charged". It found the fee error postmortem even though those exact words don't appear. Why?

A) The database did a fuzzy string match
B) The embedding model encoded the MEANING — "billing mistake" and "fee error" have similar semantic representations because the model learned from training data that these concepts are related
C) Chroma has a built-in synonym dictionary
D) The query was automatically rewritten by the API

---

## Answer Key

**Q1: B** — Embedding models convert text into fixed-length vectors. These are numerical representations of meaning, not text generation. The vector captures semantic content in a way that allows mathematical comparison.

**Q2: B** — Cosine similarity measures the angle between two vectors. 0.95 means they point in nearly the same direction in the embedding space — the texts have very similar meaning. This has nothing to do with shared words or text length.

**Q3: B** — Chat models (Claude, GPT-4) are decoder transformers that generate text token by token. Embedding models are encoder-only transformers that produce a single fixed vector. Different architecture, different training objective, different output type.

**Q4: B** — Keyword search requires exact word overlap. Semantic search finds "orders getting rejected a lot" when the document says "order rejection spike" because the embedding model learned these mean the same thing. This is the core value proposition of embeddings.

**Q5: B** — A cross-encoder must process (query, document) as a pair through the full model. With 1M documents, that's 1M inference calls per query — far too slow for real-time search. Embeddings pre-compute document vectors, so search is just vector math (milliseconds).

**Q6: B** — Matryoshka representation learning trains the model so that the first N dimensions of the vector are a valid (slightly lower quality) embedding on their own. You can truncate 3072 → 1024 → 256 at query time, trading quality for speed/storage without re-embedding.

**Q7: B** — Going from 1024 → 3072 dimensions gives marginal quality improvement but 3x storage and 3x compute per similarity calculation. The quality-vs-cost curve flattens around 768-1536 for most use cases.

**Q8: B** — Hybrid search combines BM25 (exact keyword matching, great for error codes and IDs) with embeddings (semantic matching, great for paraphrased queries). Together they cover both cases: exact terms AND meaning-based retrieval.

**Q9: B** — Cross-encoders are too slow for initial retrieval but very accurate. The pattern is: embeddings find top 50 candidates fast, then cross-encoder reranks those 50 with higher precision. Best of both worlds.

**Q10: B** — The embedding model was trained on billions of text examples and learned that "billing mistake" and "fee error", "wrong amount" and "decimal point error" are semantically related concepts. The vectors for these phrases point in similar directions, so cosine similarity is high.
