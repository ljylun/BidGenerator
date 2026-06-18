---
name: lanham-ai-agents
description: "Knowledge base from \"AI Agents in Action\" by Micheal Lanham (Manning, 2025). Use when applying agent frameworks (AutoGen, CrewAI, Semantic Kernel, Behavior Trees), building autonomous assistants, implementing prompt engineering strategies (CoT, ToT, RAG), or referencing AI agent architecture patterns."
---

<!-- argument-hint: [topic, framework name, or chapter number] -->

# AI Agents in Action
**Author**: Micheal Lanham | **Pages**: ~346 | **Chapters**: 11 | **Generated**: 2026-06-16

## How to Use This Skill

- **Without arguments** — load core frameworks for reference
- **With a topic** — ask about `behavior trees`, `RAG`, `multi-agent`, `prompt engineering`, or another indexed topic; I find and read the relevant chapter
- **With chapter** — ask for `ch05`; I load that specific chapter
- **Browse** — ask "what chapters do you have?" to see the full index

When you ask about a topic not covered in Core Frameworks below, I will read
the relevant chapter file before answering.

---

## Core Frameworks & Mental Models

### Agent Interaction Spectrum (Ch 1)
Use this spectrum to select the right autonomy level for any use case:
- **Direct** → simple QA, no tools needed
- **Proxy** → LLM reformulates prompts for another model (e.g., ChatGPT → DALL-E)
- **Agent + Confirmation** → tool use with user approval step
- **Autonomous** → independent planning, decision-making, execution

Think of agent autonomy as a **spectrum, not a binary**. Match the level to the risk/reward profile of the task.

### Multi-Agent Systems (Ch 4)
Use **AutoGen** for conversational, exploratory multi-agent systems (group chat, proxy patterns). Use **CrewAI** when you need structured, role-based enterprise workflows (sequential/hierarchical task management). Think of multi-agent systems as **teams of specialists** — a coordinator delegates to experts.

### Empowering Agents with Actions (Ch 5)
**OpenAI Function Calling** is the standard pattern for LLM-tool integration. Define functions with name + description + parameters → LLM decides when to call → execute → return results. **Semantic Kernel (SK)** adds structure: semantic functions (prompt templates) for "what" and "why", native functions (code) for "how". Use the **semantic service layer** pattern to cleanly separate LLMs from external APIs.

### Behavior Trees for Agent Control (Ch 6)
Use **behavior trees** when you need structured, reusable control over agent decision-making. Five primary nodes cover most patterns: **Selector** (try until one succeeds), **Sequence** (run all, fail on any failure), **Action** (execute), **Condition** (check), **Decorator** (control/block). **Agentic Behavior Trees (ABTs)** use LLMs to dynamically construct and modify the tree. Always implement **Control Barrier Functions** as safety guardrails.

### RAG and Memory (Ch 8)
Use **Retrieval Augmented Generation (RAG)** whenever agents need external knowledge. Two phases: **Index** (load → chunk → embed → store) and **Query** (embed query → similarity search → augment prompt). **Knowledge** is document-based (external); **memory** is experience-based (from interactions). Both augment prompts through retrieval.

### Prompt Engineering Strategies (Ch 9)
Six OpenAI strategies map to agent components: **Write Clear Instructions** → persona/behavior, **Provide Reference Text** → knowledge/RAG, **Split Complex Tasks** → subtask decomposition, **Give Models Time to "Think"** → reasoning/planning, **Use External Tools** → function calling, **Test Changes Systematically** → evaluation. Always iterate — prompt engineering is never one-shot.

### Reasoning Techniques (Ch 10)
Scale reasoning depth to problem complexity: **Direct/Few-Shot** for simple tasks, **Chain of Thought (CoT)** for multi-step reasoning, **Self-Consistency** for high-reliability needs (multiple paths, majority vote), **Tree of Thought (ToT)** for complex exploration. Multiple reasoning paths always beat a single path.

### Planning and Feedback (Ch 11)
**Planning** separates agents from chatbots. Use **sequential planning** when tasks have dependencies (output feeds next step). Build **custom JSON planners** using prompt engineering to generate step-by-step plans from available functions. Implement **feedback mechanisms** (corrective, suggestive, epistemic) for continuous improvement. Always set **safety guardrails** — agents with autonomous actions can go rogue.

---

## Chapter Index

| # | Title | Key Frameworks |
|---|-------|----------------|
| [ch01](chapters/ch01-introduction-to-agents.md) | Introduction to agents and their world | Agent Interaction Spectrum, Multi-Agent Pattern |
| [ch02](chapters/ch02-harnessing-llms.md) | Harnessing the power of large language models | OpenAI API, Message Roles, Temperature |
| [ch03](chapters/ch03-engaging-gpt-assistants.md) | Engaging GPT assistants | GPT Builder, Custom Actions, Persona/Rules |
| [ch04](chapters/ch04-multi-agent-systems.md) | Exploring multi-agent systems | AutoGen Studio, CrewAI, Group Chat, AgentOps |
| [ch05](chapters/ch05-empowering-agents-actions.md) | Empowering agents with actions | OpenAI Functions, Semantic Kernel, Semantic Service Layer |
| [ch06](chapters/ch06-autonomous-assistants.md) | Building autonomous assistants | Behavior Trees, ABTs, Control Barrier Functions |
| [ch07](chapters/ch07-agent-platform-nexus.md) | Assembling and using an agent platform | Nexus Architecture, Personas, Semantic+Native Functions |
| [ch08](chapters/ch08-agent-memory-knowledge.md) | Understanding agent memory and knowledge | RAG, Vector DB, Memory Systems |
| [ch09](chapters/ch09-prompt-engineering-prompt-flow.md) | Mastering agent prompts with prompt flow | 6 Strategies, Agent Profile, Prompt Flow DAG |
| [ch10](chapters/ch10-reasoning-evaluation.md) | Agent reasoning and evaluation | CoT, Self-Consistency, ToT, Evaluation |
| [ch11](chapters/ch11-planning-feedback.md) | Agent planning and feedback | Sequential Planning, JSON Planners, Feedback |

## Topic Index

- **AgentOps** → ch04
- **AutoGen / AutoGen Studio** → ch04
- **Behavior Trees** → ch06
- **Chain of Thought (CoT)** → ch10
- **Control Barrier Functions** → ch06
- **CrewAI** → ch04
- **Custom Actions / Functions** → ch03, ch05
- **Few-Shot Prompting** → ch10
- **Function Calling** → ch05
- **GPT Assistants / GPT Store** → ch03
- **Memory (short-term, long-term, semantic)** → ch08
- **Multi-Agent Systems** → ch04
- **Native Functions** → ch05
- **Nexus** → ch07
- **OpenAI API / Chat Completions** → ch02
- **Planning / Sequential Planning** → ch11
- **Prompt Engineering (6 strategies)** → ch09
- **Prompt Flow** → ch09
- **RAG (Retrieval Augmented Generation)** → ch08
- **Reasoning Spectrum** → ch10
- **Self-Consistency Prompting** → ch10
- **Semantic Functions / Semantic Kernel** → ch05
- **Temperature** → ch02
- **Tokens / Token Counting** → ch02
- **Tree of Thought (ToT)** → ch10
- **Vector Database** → ch08

## Supporting Files

- [glossary.md](glossary.md) — all key terms with definitions
- [patterns.md](patterns.md) — all techniques and design patterns
- [cheatsheet.md](cheatsheet.md) — quick reference tables and decision guides

---

## Scope & Limits

This skill covers the book content only. For hands-on implementation in your codebase,
combine with project-specific tools. For topics beyond this book, check related skills
or ask the agent directly.
