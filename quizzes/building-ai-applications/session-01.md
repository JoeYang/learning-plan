# Quiz: Session 1 — LLM APIs & Prompt Engineering Fundamentals

**Instructions:** Choose the best answer(s) for each question. Answers at the bottom.

---

### Q1. What is the minimum required to make an Anthropic Claude API call?

A) model, messages
B) model, max_tokens, messages
C) model, max_tokens, messages, system
D) model, max_tokens, messages, temperature

---

### Q2. In the messages array, why do you include messages with `role: "assistant"`?

A) The API requires alternating user/assistant messages or it throws an error
B) The model is stateless — you replay conversation history so it has context for follow-up questions
C) Assistant messages are used to fine-tune the model in real time
D) They're optional metadata for logging purposes

---

### Q3. What does `temperature=0` do?

A) The model refuses to answer
B) The model produces the most random, creative output
C) The model deterministically picks the most likely token at each step
D) The model uses fewer tokens to save cost

---

### Q4. You need the model to classify support tickets into exactly 5 categories using a consistent JSON format. Which prompting technique is MOST important to include?

A) Zero-shot — just describe the categories
B) Few-shot — provide example tickets with their correct JSON classification
C) Chain-of-thought — ask it to reason step by step
D) High temperature — to encourage diverse classifications

---

### Q5. What is the key difference between a `system` prompt and a `user` prompt?

A) System prompts are cheaper (fewer tokens billed)
B) System prompts set persistent instructions/persona; user prompts are the actual requests
C) System prompts are only used for safety filtering
D) There is no practical difference — they're interchangeable

---

### Q6. When would chain-of-thought prompting be MOST valuable? (Select all that apply)

A) Generating a creative marketing tagline
B) Deciding whether a trading alert is critical or a false alarm based on multiple signals
C) Translating a sentence from English to French
D) Analysing a log file to determine the root cause of a latency spike

---

### Q7. You're building a production system that classifies 10,000 log messages per day. Each API call costs money. Which is the best strategy?

A) Always use the largest model (Opus) for best accuracy
B) Start with the cheapest model (Haiku) with few-shot prompting, evaluate accuracy, only upgrade if needed
C) Use zero-shot with Sonnet to save on prompt tokens
D) Fine-tune a model immediately

---

### Q8. What happens if you send a multi-turn conversation but OMIT the assistant message from a previous turn?

```python
messages = [
    {"role": "user", "content": "What is RAG?"},
    # assistant response omitted
    {"role": "user", "content": "How do I build one?"},
]
```

A) The API throws an error because messages must alternate
B) The model treats it as two unrelated questions and doesn't know what "one" refers to
C) The model automatically remembers its previous response
D) The model answers both questions together

---

### Q9. Streaming responses are useful because:

A) They reduce the total number of output tokens
B) They reduce perceived latency — the user sees tokens as they're generated instead of waiting
C) They make the model produce better quality responses
D) They reduce API cost

---

### Q10. You ran the same prompt through claude-haiku and claude-sonnet. Haiku was 3x faster and 4x cheaper, but its answer was slightly less nuanced. When would you pick Haiku over Sonnet in production?

A) Never — always use the best model
B) When the task is straightforward classification/extraction and few-shot examples ensure accuracy
C) Only for internal testing, never for production
D) When you need the most creative output

---

## Answer Key

**Q1: B** — `model`, `max_tokens`, and `messages` are required. System prompt and temperature are optional.

**Q2: B** — LLMs are stateless. Each API call is independent. You include assistant messages to give the model conversation context so it can handle follow-up questions coherently.

**Q3: C** — Temperature 0 makes the model deterministic — it always selects the highest-probability token. Good for factual/consistent tasks.

**Q4: B** — Few-shot is the best technique when you need consistent output format. The examples teach the model exactly what structure you expect. CoT helps reasoning but doesn't guarantee format.

**Q5: B** — The system prompt sets the overall instructions, persona, and rules. The user prompt contains the actual request. They serve fundamentally different purposes.

**Q6: B, D** — CoT is most valuable when the task requires multi-step reasoning or weighing multiple factors. Classifying alerts from multiple signals and root-cause analysis both benefit from explicit reasoning. Translation and creative taglines don't need step-by-step logic.

**Q7: B** — Start cheap, measure, upgrade only if needed. Few-shot prompting on a cheaper model often matches the quality of zero-shot on an expensive model, at a fraction of the cost. This is a core production AI pattern.

**Q8: B** — The model has no memory. Without the assistant message providing context, it doesn't know what "one" refers to. It would likely answer "How do I build one?" as a standalone question.

**Q9: B** — Streaming doesn't change cost, token count, or quality. It reduces *perceived* latency by showing tokens as they're generated, which is critical for user-facing applications.

**Q10: B** — Smaller, cheaper models are ideal for well-defined tasks where few-shot examples can guide accuracy. Save expensive models for tasks requiring deeper reasoning. This cost/quality tradeoff is a key production decision.
