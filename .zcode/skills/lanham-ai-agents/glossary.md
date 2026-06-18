# Glossary

**Agent** — An entity that acts on behalf of a user, ranging from simple proxies to fully autonomous systems (Ch 1)

**Agent Profile** — An encapsulation of component prompts (persona, instructions, strategies) that define an agent's behavior (Ch 9)

**Agentic Behavior Tree (ABT)** — A behavior tree where an LLM constructs and modifies the tree at runtime (Ch 6)

**AgentOps** — An observability platform for monitoring agent performance, cost, and output accuracy (Ch 4)

**Assistant** — Synonym with "agent" in this book's context; specifically refers to agents that act on behalf of users (Ch 1)

**Assistant Role** — A message role in the OpenAI API that captures message history or injects previous responses (Ch 2)

**Autonomous Agent** — An agent that interprets requests, constructs plans, and executes decisions independently (Ch 1)

**AutoGen** — Microsoft's open-source multi-agent platform supporting conversational agent interactions (Ch 4)

**AutoGen Studio** — Visual development environment for creating and managing multi-agent systems (Ch 4)

**Back Chaining** — A method for building behavior trees by starting from the goal and working backward (Ch 6)

**Behavior Tree** — A hierarchical control structure using selector, sequence, condition, action, and decorator nodes (Ch 6)

**Chain of Thought (CoT)** — A prompting technique that encourages the LLM to show its reasoning step by step (Ch 10)

**Chat Completions Model** — The standard LLM interface pattern: model + messages + temperature (Ch 2)

**Condition Node** — A behavior tree node that returns success/failure based on a condition check (Ch 6)

**Context Variables** — Shared state passed between semantic and native functions in Semantic Kernel (Ch 5)

**Control Barrier Function (CBF)** — A decorator node in behavior trees that blocks or prevents unwanted behaviors (Ch 6)

**CrewAI** — A structured, role-based multi-agent framework for enterprise applications (Ch 4)

**Custom Action** — An external API (typically FastAPI) connected to a GPT assistant via OpenAPI spec (Ch 3)

**Decorator Node** — A behavior tree node that controls execution of child nodes, often as a safety guard (Ch 6)

**Direct Solution Prompting** — The simplest form of prompt engineering — direct question/answer (Ch 10)

**Embedding Model** — Converts text into vector representations that capture semantic meaning (Ch 8)

**Few-Shot Prompting** — Providing 1-3 examples in a prompt to guide the LLM's behavior (Ch 10)

**Function Calling** — OpenAI API feature for defining functions that the LLM can invoke (Ch 5)

**GPT Assistant** — OpenAI's no-code platform for building and publishing AI assistants (Ch 3)

**GPT Builder** — Chat-based interface for creating GPT assistants through conversation (Ch 3)

**GPT Store** — Marketplace for publishing and discovering GPT assistants (Ch 3)

**Group Chat Pattern** — Multiple agents communicating in a shared conversation (Ch 4)

**Iterative Execution** — Default LLM behavior: execute one action, show result, ask to continue (Ch 11)

**Knowledge** — External, document-based context provided to agents via retrieval (Ch 8)

**Memory** — Interaction-based, experiential context that agents retain across conversations (Ch 8)

**Multi-Agent System** — Multiple agent profiles working together under a coordinating controller (Ch 1)

**Native Function** — Code that performs an action (API call, database query) (Ch 5)

**Nexus** — Open-source teaching platform developed with this book for building AI agents (Ch 7)

**Parallel Actions** — Standalone actions that can be executed simultaneously (Ch 11)

**Persona** — The personality and primary motivator for an agent (Ch 3, Ch 7)

**Planner** — A component that breaks goals into executable steps (Ch 11)

**Planning** — The process of breaking a goal into subtasks and sequencing them for execution (Ch 11)

**Prompt Flow** — Microsoft's visual tool for building, testing, and evaluating prompt flows (Ch 9)

**Prompt Engineering** — The iterative process of refining prompts to improve LLM outputs (Ch 9)

**Proxy Agent** — An LLM that interjects and reformulates user requests for a specific model/task (Ch 1)

**RAG (Retrieval Augmented Generation)** — Two-phase pattern: index documents → query with retrieval + generation (Ch 8)

**Rules** — Explicit constraints that ensure consistent agent output (Ch 3)

**Selector Node** — A behavior tree node that executes children until one succeeds (Ch 6)

**Self-Consistency Prompting** — Generating multiple reasoning paths and selecting the most consistent answer (Ch 10)

**Semantic Function** — A prompt template that defines how to engage an LLM for a specific task (Ch 5)

**Semantic Kernel (SK)** — Microsoft's open-source SDK for building AI applications with semantic and native functions (Ch 5)

**Semantic Service Layer** — Architecture where SK sits between the LLM and external APIs (Ch 5)

**Sequence Node** — A behavior tree node that executes children in sequence, failing on first failure (Ch 6)

**Sequential Planning** — Actions executing in order, with each step depending on the previous one (Ch 11)

**Speaker Selection** — Strategy for determining which agent speaks next in a group chat (Ch 4)

**System Prompt** — Defines the agent's role, rules, and behavior across the entire conversation (Ch 9)

**System Role** — A message role that defines the rules and guidelines for an LLM request (Ch 2)

**Temperature** — Controls output variability in LLM requests: 0=consistent, higher=variable (Ch 2)

**Token** — The basic unit of text processing in LLMs, used for cost estimation and context management (Ch 2)

**Tree of Thought (ToT)** — Exploring multiple reasoning branches, evaluating them, and selecting the best path (Ch 10)

**User Proxy Agent** — An agent that represents the human user, coordinating between other agents (Ch 4)

**User Role** — A message role representing the message from the user (Ch 2)

**Vector Database** — Stores document chunks as embeddings for similarity search (Ch 8)

**Zero-Shot Prompting** — Guiding the LLM with rules/guidelines without providing examples (Ch 10)
