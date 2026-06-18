# Chapter 9: Mastering agent prompts with prompt flow

## Core Idea
Systematic prompt engineering — iterating, evaluating, and refining prompts — is essential for building effective agents. This chapter covers OpenAI's prompt engineering strategies, agent profiles/personas, and using Microsoft's Prompt Flow tool for iterative prompt development and evaluation.

## Frameworks Introduced
- **OpenAI's Six Prompt Engineering Strategies**: (1) Write Clear Instructions, (2) Provide Reference Text, (3) Split Complex Tasks into Simpler Subtasks, (4) Give Models Time to "Think", (5) Use External Tools, (6) Test Changes Systematically.
  - When to use: Always — these are the foundational tactics for any agent prompt.
  - How: Map each strategy to the relevant agent component (Actions, Memory, Planning, Evaluation) and apply iteratively.

- **Agent Profile**: An encapsulation of component prompts that describe an agent — persona, special instructions, and strategies mapped to prompt engineering categories.
  - When to use: When designing any agent system, from simple assistants to complex multi-agent systems.
  - How: Define persona → map to Write Clear Instructions → add actions (External Tools) → add knowledge (Reference Text) → add planning (Give Time to Think) → add evaluation (Test Systematically).

- **Prompt Flow (Microsoft)**: A visual tool for building, testing, and evaluating prompt flows using a DAG (Directed Acyclic Graph) of components.
  - When to use: When you need to systematically iterate on prompts and evaluate their effectiveness.
  - How: Create a flow.dag.yaml → define LLM/Embedding/Python components → connect them visually → test and evaluate outputs.

## Key Concepts
- **System Prompt**: Defines the agent's role, rules, and behavior across the entire conversation.
- **Iterative Refinement**: The process of starting with a basic prompt, evaluating results, and incrementally improving.
- **Evaluation via Embedding Similarity**: Using embedding models to compare predicted vs. expected outputs for automated evaluation.
- **Agent Profile Components**: Persona (who), Instructions (what), Actions/Tools (how), Knowledge (context), Planning (strategy), Evaluation (quality).

## Mental Models
- **Prompt engineering is iterative, not one-shot**: Every prompt benefits from systematic testing and refinement.
- **Agent profile = complete prompt architecture**: A well-designed agent profile addresses all six prompt engineering strategies.

## Anti-patterns
- **Skipping evaluation**: Without systematic testing (Test Changes Systematically), you can't know if prompt changes actually improve results.
- **Mixing planning and action prompts**: Keep "thinking" prompts separate from "action" prompts for better reasoning quality.

## Worked Example
Building a Question-Answer prompt flow:
1. Create a flow with: Question-Answer LLM → Embedding (predicted) + Embedding (expected) → Python evaluation
2. Input: context + question + expected answer
3. LLM generates an answer based on context
4. Embed both predicted and expected answers
5. Calculate cosine similarity between embeddings
6. Output: evaluation score (0-1) measuring answer quality
7. Iterate on the prompt template to improve the evaluation score

## Key Takeaways
1. Systematic prompt engineering (build → test → evaluate → refine) is essential for agent quality.
2. The six OpenAI prompt engineering strategies map to agent components (Actions, Memory, Planning, Evaluation).
3. Agent profiles encapsulate all the prompts that define an agent's behavior.
4. Prompt Flow (DAG-based visual tool) enables systematic iteration and evaluation.
5. Embedding-based similarity scoring provides automated evaluation of prompt outputs.

## Connects To
- **Ch 2**: Prompt engineering builds on the basic LLM message structure.
- **Ch 10**: Reasoning and evaluation techniques extend these prompt engineering strategies.
