# Cheatsheet

## Agent Architecture Decision Matrix

| Need | Solution | Key Tool |
|---|---|---|
| Simple QA, no tools | Direct LLM | OpenAI API |
| Prompt reformulation | Agent Proxy | ChatGPT + DALL-E |
| Tool use with approval | Agent + Functions | OpenAI Function Calling |
| Independent execution | Autonomous Agent | Behavior Trees + LLM |
| Multiple specialists | Multi-Agent System | AutoGen / CrewAI |
| External knowledge | RAG | Vector DB + Embeddings |
| Structured control | Behavior Trees | py_trees / Custom |
| Complex reasoning | CoT / ToT | Prompt engineering |

## Prompt Engineering Quick Reference

| Strategy | Tactic | Example |
|---|---|---|
| Write Clear Instructions | Be specific, use delimiters, specify steps | "Answer in 3 bullet points:" |
| Provide Reference Text | Add context to reduce hallucinations | "Based on the following text: {context}" |
| Split Complex Tasks | Intent classification, summarization | "First, classify the intent. Then..." |
| Give Time to Think | "Think step by step", inner monologue | "Let's work through this problem..." |
| Use External Tools | Function calling, code execution | Define functions array |
| Test Changes | A/B test prompts, evaluate with embeddings | Use Prompt Flow DAG |

## LLM Connection Essentials

```
Messages = [
  {"role": "system", "content": "Rules and behavior"},
  {"role": "user", "content": "User input"},
  {"role": "assistant", "content": "Previous response"}  // optional
]
Temperature: 0 = deterministic, 1 = creative
```

## Behavior Tree Node Quick Reference

| Node | Logic | Use When |
|---|---|---|
| Selector | Try children until one succeeds | Fallback options |
| Sequence | Run all children, fail on any failure | Dependent steps |
| Action | Execute and return success/failure | Actual work |
| Condition | Check condition, return success/failure | Guard checks |
| Decorator | Control child execution (can block) | Safety/thresholds |

## Reasoning Technique Selection

**Simple factual question** → Direct prompting
**Pattern following** → Few-shot prompting
**Multi-step reasoning** → Chain of Thought
**High-stakes decision** → Self-Consistency or ToT
**Tool-dependent task** → Automatic Reasoning with Tools (ART)

## RAG Pipeline Checklist

1. Load documents (PDF, TXT, MD)
2. Split into chunks (500 words, 50-word overlap)
3. Embed chunks (text-embedding-ada-002 or similar)
4. Store in vector DB (Chroma, Pinecone, FAISS)
5. At query: embed query → similarity search (top-k=3)
6. Augment prompt with retrieved chunks
7. Generate response grounded in context

## Agent Platform Comparison

| Feature | GPT Assistants | AutoGen | CrewAI | Nexus |
|---|---|---|---|---|
| Interface | No-code (ChatGPT UI) | Visual Studio | Code-first | Streamlit |
| Multi-agent | No | Yes (group chat) | Yes (role-based) | Configurable |
| Custom actions | OpenAPI/FastAPI | Skills | Tools | Semantic + Native |
| Planning | Built-in | Via agents | Via tasks | Configurable |
| Knowledge | File uploads | Via skills | Via memory | RAG |
| Best For | Rapid prototyping | Research/exploration | Enterprise | Learning |

## Safety Rules for Autonomous Agents

1. **Always implement control barrier functions** — decorator nodes that block unsafe actions
2. **Limit available tools** — provide only the actions the agent needs
3. **Require confirmation for destructive actions** — don't let agents delete/modify without approval
4. **Monitor agent behavior** — use observability tools (AgentOps) to track actions
5. **Set iteration limits** — prevent agents from looping indefinitely
6. **Test with safe defaults** — start with read-only actions, expand gradually

## Key Temperature Settings

| Task | Temperature | Why |
|---|---|---|
| Factual QA | 0 | Consistent, deterministic answers |
| Code generation | 0-0.2 | Reliable, correct code |
| Data analysis | 0.3-0.5 | Balance consistency with flexibility |
| Creative writing | 0.7-1.0 | More varied, creative output |
| Brainstorming | 0.8-1.0 | Maximum diversity of ideas
