# Patterns

## Agent Interaction Spectrum
**When to use**: Always — foundational mental model for choosing the right agent architecture.
**How**: Identify the required autonomy level:
- Direct LLM interaction (simple QA)
- Agent proxy (prompt reformulation for specific models)
- Agent with confirmation (tool use with user approval)
- Autonomous agent (independent planning and execution)

## Multi-Agent Collaboration
**When to use**: When a problem decomposes into specialized subtasks requiring different expertise.
**How**: Define agent profiles with specific roles, tools, and knowledge → assign a controller/proxy → agents communicate through group chat, proxy, or hierarchical patterns.
**Trade-offs**: More agents = more complexity but better specialization. Use observability tools (AgentOps) to monitor.

## OpenAI Function Calling
**When to use**: When an agent needs to interact with external APIs or perform actions beyond text generation.
**How**: Define functions with name, description, and parameters → add to API call → LLM returns function calls → execute → pass results back.
**Trade-offs**: Requires careful function description design. Too many functions can confuse the LLM.

## Semantic Kernel (SK) Architecture
**When to use**: When building agent systems that need structured management of prompts, functions, and context.
**How**: Create semantic functions (prompt templates) → register native functions (code actions) → combine into plugins/skills → expose through semantic service layer.
**Trade-offs**: Adds architectural complexity but provides clean separation of concerns.

## Behavior Tree Control
**When to use**: When you need structured, reusable control over agent decision-making.
**How**: Define tree with root composite node → add selector/sequence nodes for branching → add condition nodes for checks → add action nodes for execution.
**Trade-offs**: Learning curve for BT concepts, but scales much better than FSMs for complex control.

## Agentic Behavior Trees (ABTs)
**When to use**: When agents need to dynamically plan and adapt behavior based on context.
**How**: Use LLM to generate BT nodes → execute tree → use results to modify tree → repeat. Combine with back chaining for complex goals.
**Trade-offs**: More flexible than static BTs but requires more LLM calls.

## RAG (Retrieval Augmented Generation)
**When to use**: Whenever an agent needs external knowledge beyond its training data.
**How**: Phase 1 — Load documents → chunk → embed → store in vector DB. Phase 2 — Embed query → similarity search → augment prompt with retrieved chunks.
**Trade-offs**: Chunking strategy significantly impacts quality. Too many retrieved chunks can confuse the LLM.

## Sequential Planning
**When to use**: When tasks have dependencies (output of one step feeds into the next).
**How**: Define goal → planner breaks into sequential steps → execute each step → pass results to next step.
**Trade-offs**: More reliable than parallel-only execution but slower. Not all LLMs support sequential planning natively.

## Custom JSON Planners
**When to use**: When you need control over how plans are generated from available functions.
**How**: Define available functions → create planner prompt that generates JSON plans → execute step by step → incorporate feedback.
**Trade-offs**: More flexible than built-in planners but requires prompt engineering expertise.

## Prompt Engineering Iteration
**When to use**: Always — for any agent prompt.
**How**: Build prompt → test with sample inputs → evaluate outputs (embedding similarity) → refine prompt → repeat.
**Trade-offs**: Time-intensive but essential for quality. Automated evaluation (embedding similarity) enables faster iteration.

## Chain of Thought (CoT) Prompting
**When to use**: When the LLM needs to reason through multi-step problems.
**How**: Add "think step by step" or similar instruction to the prompt → LLM shows reasoning → final answer.
**Trade-offs**: Significantly improves reasoning quality. Costs more tokens due to longer outputs.

## Self-Consistency Prompting
**When to use**: When you need higher reliability for complex reasoning tasks.
**How**: Run the same prompt multiple times → collect answers → take majority vote or most consistent answer.
**Trade-offs**: Higher reliability but costs N times more LLM calls.

## Tree of Thought (ToT) Prompting
**When to use**: For complex problems where exploring multiple reasoning paths is beneficial.
**How**: Generate multiple reasoning branches → evaluate each → select best path → continue reasoning.
**Trade-offs**: Highest reasoning quality but most expensive in tokens and computation.

## Agent Profile Construction
**When to use**: When designing any agent system.
**How**: Define persona → map to Write Clear Instructions → add actions (External Tools) → add knowledge (Reference Text) → add planning (Give Time to Think) → add evaluation (Test Systematically).
**Trade-offs**: Comprehensive profiles require more upfront design but produce more consistent agents.

## Few-Shot Prompting for Behavior Modification
**When to use**: When you need the LLM to adopt new patterns or use unfamiliar terms.
**How**: Provide 1-3 examples demonstrating the desired behavior → LLM generalizes from examples.
**Trade-offs**: Powerful for behavior modification but examples must be carefully chosen.

## Agent Safety with Control Barrier Functions
**When to use**: When autonomous agents have access to actions with real-world consequences.
**How**: Add decorator nodes in behavior trees that evaluate safety conditions → block unsafe actions.
**Trade-offs**: May prevent some legitimate actions. Balance safety with capability.
