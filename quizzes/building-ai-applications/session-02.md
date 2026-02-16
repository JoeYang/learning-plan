# Quiz: Session 2 — Structured Outputs & Tool Use

**Instructions:** Choose the best answer(s) for each question. Answers at the bottom.

---

### Q1. You ask an LLM to return JSON, but it wraps the response in ```json markdown fences. What is the BEST long-term fix?

A) Strip the fences with string manipulation every time
B) Add "DO NOT use markdown fences" to every prompt
C) Use a Pydantic model to define the schema and validate the response automatically
D) Switch to a different model that doesn't add fences

---

### Q2. In Anthropic's tool use flow, who actually executes the tool function?

A) The LLM executes it on Anthropic's servers
B) The LLM generates code that runs in a sandbox
C) You (the developer) execute it locally and return the result to the LLM
D) The tool runs automatically when the model outputs the tool_use block

---

### Q3. The model returns `stop_reason = "tool_use"`. What does this mean?

A) The model encountered an error and stopped
B) The model wants to call a tool — you should execute it and send the result back
C) The model finished its response and used a tool during generation
D) The model is waiting for the user to provide a tool

---

### Q4. You define a tool with this description: "Do math". The model rarely uses it. Why?

A) The model doesn't support math tools
B) Tool descriptions are like API docs — vague descriptions make it hard for the model to know when to use the tool
C) You need to explicitly tell the model to use the tool in every prompt
D) The tool name must contain "calculator" for the model to recognise it

---

### Q5. What is the purpose of `tool_use_id` in the tool result message?

A) It's used for billing — each tool call has a cost
B) It matches the result back to the specific tool call, so the model knows which request this answers
C) It's a security token that authorises the tool execution
D) It's optional metadata for logging

---

### Q6. Your Pydantic model has `confidence: float = Field(ge=0.0, le=1.0)`. The LLM returns `"confidence": 1.5`. What happens?

A) Pydantic silently clamps it to 1.0
B) Pydantic raises a ValidationError — the value violates the constraint
C) The value is accepted since 1.5 is a valid float
D) The API call fails before Pydantic sees it

---

### Q7. In the retry pattern, when validation fails you send the error back to the model. Why does this work?

A) The model has been fine-tuned on Pydantic errors specifically
B) The model sees its previous output + the specific error, giving it enough context to self-correct
C) The Anthropic API automatically retries on validation errors
D) It doesn't work reliably — you should just retry with the same prompt

---

### Q8. Self-consistency prompting runs the same question 5 times and takes the majority answer. When is this NOT worth the cost?

A) Classifying the severity of a production incident that may require paging on-call
B) Generating a commit message for a code change
C) Determining the root cause of a trading system outage
D) Deciding whether to escalate a margin breach to the risk committee

---

### Q9. How does Tree-of-Thought differ from basic Chain-of-Thought?

A) ToT uses a different model; CoT works with any model
B) ToT generates multiple hypotheses and evaluates them before committing; CoT follows a single reasoning path
C) ToT is cheaper because it uses fewer tokens
D) There is no practical difference — they produce the same results

---

### Q10. You're building a production alert classifier. It needs to output structured JSON, use a calculator for threshold comparisons, and search logs for context. Which combination of Session 2 concepts would you use?

A) Pydantic for output schema + tool use for calculator and log search + retry pattern for reliability
B) Zero-shot prompting + manual JSON parsing
C) Tree-of-thought for every alert + self-consistency with 10 samples
D) Fine-tune a model specifically for this task

---

## Answer Key

**Q1: C** — Pydantic is the production solution. It defines the schema once, validates automatically, and gives you typed Python objects. String manipulation and prompt tricks are fragile workarounds.

**Q2: C** — The model never executes anything. It generates a structured request (tool name + arguments). You run the function locally and send the result back. This is a fundamental safety property of tool use.

**Q3: B** — `stop_reason = "tool_use"` means the model paused to request a tool call. You execute the tool, send the result as a `tool_result` message, and call the API again so the model can continue.

**Q4: B** — Tool descriptions are the model's only way to understand what a tool does and when to use it. "Do math" is too vague. "Evaluate mathematical expressions including arithmetic, percentages, and functions like sqrt" is much better. Think of descriptions as API documentation for the model.

**Q5: B** — When the model calls multiple tools, each gets a unique ID. The `tool_use_id` in your result tells the model "this is the answer to that specific tool call." Without it, the model wouldn't know which result corresponds to which request.

**Q6: B** — Pydantic enforces constraints. `ge=0.0, le=1.0` means the value must be between 0 and 1. A value of 1.5 raises a ValidationError. This is exactly why Pydantic is better than manual validation — constraints are declared once and enforced automatically.

**Q7: B** — The model sees: "I generated this JSON → it failed with this error → I need to fix this specific issue." This is the same pattern as a developer reading a compiler error and fixing their code. It works because the error message gives precise feedback about what went wrong.

**Q8: B** — A commit message is low-stakes and straightforward. Self-consistency is for high-stakes decisions where a wrong answer has serious consequences (production incidents, risk decisions, escalations). Don't spend 5x the cost on a task where one attempt is good enough.

**Q9: B** — CoT follows one linear path: "First... then... therefore..." If it starts down the wrong path, it's stuck. ToT generates multiple candidate paths, evaluates each against the evidence, and picks the best-supported one. It's more thorough but costs more (multiple API calls).

**Q10: A** — This combines all three key patterns from Session 2: Pydantic for reliable structured output, tool use for external data (calculator + log search), and the retry pattern to handle occasional failures. This is a realistic production architecture.
