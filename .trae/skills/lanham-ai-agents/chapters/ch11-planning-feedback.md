# Chapter 11: Agent planning and feedback

## Core Idea
Planning is what separates agents from chatbots. This chapter covers the agent planning process (goal → plan → execute → results), sequential planning (where steps depend on previous results), building custom planners, and feedback mechanisms that allow agents to adapt and improve.

## Frameworks Introduced
- **Agent Planning Process**: Goal submission → Plan construction → Execution → Results presentation. The agent breaks the goal into tasks, sequences them, and executes each step.
  - When to use: Always — planning is the essential capability that makes an agent autonomous.
  - How: User submits goal → LLM/agent constructs a plan (identifies subtasks and dependencies) → executes tasks → presents results.

- **Sequential Planning**: Actions execute in order, with each step depending on the previous one. Supported natively by Claude and OpenAI Assistants.
  - When to use: When tasks have dependencies (e.g., search → download → save).
  - How: Define the goal → the planner breaks it into sequential steps → each step's output feeds the next step.

- **Custom Planners**: JSON-based planners that use prompt engineering to generate step-by-step plans from available functions.
  - When to use: When you need more control over how plans are generated and executed.
  - How: Define available functions → create a planner prompt that generates JSON plans → execute the plan step by step.

- **Feedback Mechanisms**: Corrective (fix errors), suggestive (propose improvements), epistemic (share knowledge) feedback that helps agents adapt plans.
  - When to use: When agents need to improve over time or adapt to changing requirements.
  - How: Collect feedback → incorporate into planner prompt → generate improved plans.

## Key Concepts
- **Planner**: A component (prompt-based or code-based) that breaks goals into executable steps.
- **Parallel Actions**: Standalone actions that can be executed simultaneously (supported by OpenAI, Groq, Azure).
- **Sequential Actions**: Actions that depend on previous results — require a planner.
- **Iterative Execution**: Default LLM behavior — execute one action, show result, ask to continue.
- **JSON Plan Format**: Plans expressed as structured JSON with steps, functions, and arguments.
- **Control Barrier Functions**: Safety checks that prevent agents from taking unintended actions.

## Mental Models
- **Planning = breaking goals into steps**: The core insight is that complex goals become achievable when decomposed into sequential, dependent tasks.
- **Planner as translator**: The planner translates a natural language goal into a structured sequence of function calls.

## Anti-patterns
- **Too many actions without a planner**: Without planning, agents can only execute parallel (independent) actions.
- **Ignoring safety**: Agents with actions can go rogue — always implement guardrails and confirmations.

## Worked Example
Building a sequential planner for Wikipedia search:
1. Goal: "Search Wikipedia for pages on {topic} and download each page and save to a file"
2. Without planner: Agent can only execute search_wikipedia (parallel action) — cannot chain to download and save.
3. With sequential planner:
   - Step 1: search_wikipedia(topic) → returns page IDs
   - Step 2: get_wikipedia_page(page_id) → for each page
   - Step 3: save_file(content) → saves to Wikipedia_{topic}.txt
4. The planner prompt generates JSON: `{"steps": [{"function": "search_wikipedia", "args": {"topic": "..."}}, ...]}`
5. Execute step by step, passing results between steps

## Key Takeaways
1. Planning is the essential capability that distinguishes agents from chatbots.
2. Sequential planning enables agents to execute dependent actions in the correct order.
3. Custom planners can be built using prompt engineering (JSON-based plans from available functions).
4. Feedback mechanisms (corrective, suggestive, epistemic) enable agents to adapt and improve.
5. Safety guardrails are critical — agents with autonomous actions can produce unintended consequences.

## Connects To
- **Ch 6**: Behavior trees provide an alternative planning/control mechanism.
- **Ch 7**: Nexus implements configurable planners.
- **Ch 10**: Reasoning techniques (CoT, ToT) are used within planning.
