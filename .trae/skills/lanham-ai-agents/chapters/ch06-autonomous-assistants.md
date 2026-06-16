# Chapter 6: Building autonomous assistants

## Core Idea
Autonomous agents require structured control mechanisms. This chapter introduces behavior trees (from robotics and game AI) as a pattern for controlling agent behavior, explores the GPT Assistants Playground for building autonomous agents, and covers agentic behavior trees (ABTs) that combine LLMs with behavior tree control.

## Frameworks Introduced
- **Behavior Trees (BTs)**: A hierarchical control structure using selector, sequence, condition, action, and decorator nodes. Originally from robotics (Brooks 1986), now standard in game AI and increasingly used for agentic control.
  - When to use: When you need structured, reusable control over agent decision-making at task or planning level.
  - How: Define a tree with a root composite node → add selector/sequence nodes for branching → add condition nodes for checks → add action nodes for execution.

- **Agentic Behavior Trees (ABTs)**: Extend traditional BTs by using LLMs to construct and modify the tree at runtime. The LLM can reason about which actions to take and adapt the tree.
  - When to use: When agents need to dynamically plan and adapt their behavior based on context.
  - How: Use an LLM to generate BT nodes → execute the tree → use results to modify the tree → repeat.

- **Control Barrier Functions (CBFs)**: Decorator nodes in behavior trees that block or prevent unwanted behaviors. They act as safety guardrails.
  - When to use: When autonomous agents need safety constraints to prevent harmful actions.
  - How: Add decorator nodes that evaluate safety conditions before allowing action execution.

## Key Concepts
- **Selector (Fallback) Node**: Executes children in sequence until one succeeds. Returns success if any child succeeds.
- **Sequence Node**: Executes children in sequence. Returns success only if ALL children succeed. Fails on first child failure.
- **Condition Node**: Returns success/failure based on a condition check. No side effects.
- **Action Node**: Executes a specific action and returns success/failure.
- **Decorator Node**: Controls execution of child nodes. Can act as a guard/blocker (control barrier function).
- **Parallel Node**: Executes all children simultaneously. Success determined by threshold.
- **Back Chaining**: A method for building behavior trees by starting from the goal and working backward to define required conditions and actions.
- **GPT Assistants Playground**: OpenAI's development environment for building and testing assistants with custom actions.

## Mental Models
- **Behavior trees = flowcharts with success/failure**: Unlike traditional flowcharts, BTs use success/failure as the control flow mechanism, making them naturally resilient to failure.
- **ABTs = LLM as brain, BT as nervous system**: The LLM reasons about what to do, the BT structure controls how actions are sequenced and selected.

## Anti-patterns
- **Using FSMs for complex agents**: Finite State Machines become unwieldy with complexity — behavior trees scale much better.
- **Ignoring safety guardrails**: Autonomous agents without control barrier functions can take unintended actions.

## Reference Table
**Comparison of AI Control Systems**:
| Control System | Description | Shortcomings | Good for Agents? |
|---|---|---|---|
| Finite State Machine | States + transitions triggered by events | Becomes unwieldy with complexity | No — doesn't scale |
| Decision Tree | Tree-like model of decisions and consequences | Overfitting, lacks generalization | Can be adapted with BT |
| Utility-based System | Utility functions evaluate and select best action | Requires careful function design | Can be adopted within BT |
| Rule-based System | If-then rules define behavior | Cumbersome with many rules, conflicts | Limited |
| Behavior Tree | Hierarchical success/failure control | Initial learning curve | Yes — best option |

## Key Takeaways
1. Behavior trees provide a scalable, hierarchical control structure for autonomous agents.
2. The five primary node types (selector, sequence, condition, action, decorator) cover most control patterns.
3. Agentic behavior trees use LLMs to dynamically construct and modify the tree.
4. Control barrier functions are essential safety guardrails for autonomous agents.
5. Back chaining is a powerful technique for building BTs from complex goals.

## Connects To
- **Ch 1**: Autonomous agents are the highest level of the agent spectrum.
- **Ch 5**: Actions in BTs are the same functions defined through OpenAI/SK.
- **Ch 11**: Planning and feedback connect to how BTs select and sequence actions.
