# Chapter 4: Exploring multi-agent systems

## Core Idea
Multi-agent systems use multiple specialized agents working together to solve complex problems. This chapter covers two major platforms — AutoGen (Microsoft's conversational multi-agent framework) and CrewAI (an enterprise-focused role-based agent system) — showing how to build collaborative agent systems.

## Frameworks Introduced
- **AutoGen Studio**: A visual development environment for creating, testing, and managing multi-agent systems. Supports multiple agent types (user proxies, assistant agents) and communication patterns (group chat, hierarchical, proxy).
  - When to use: For rapid prototyping of multi-agent systems with a visual interface.
  - How: Install AutoGen Studio → create agents with specific skills → configure communication patterns → run multi-agent conversations.

- **CrewAI**: A structured, role-based multi-agent framework that emphasizes enterprise applications. Agents have defined roles and tasks execute sequentially or hierarchically.
  - When to use: When you need precise control over agent behavior and task flow in production systems.
  - How: Define agents with roles → assign tasks with descriptions → configure crew (sequential/hierarchical) → execute and observe.

- **Group Chat Pattern**: Multiple agents communicate in a shared conversation, sharing information and collaborating on solutions.
  - When to use: When agents need to share context and build on each other's outputs.
  - How: Set up a group chat with a speaker selection strategy → agents take turns contributing → conversation converges on a solution.

## Key Concepts
- **User Proxy Agent**: An agent that represents the human user, coordinating between other agents.
- **Assistant Agent**: An LLM-powered agent with specific capabilities and tools.
- **Agent Communication Patterns**: Proxy (primary agent interfaces between user and workers), Group Chat (agents share a conversation), Hierarchical (chain of command).
- **AgentOps**: An observability platform for monitoring agent performance, cost, and output accuracy.
- **Speaker Selection**: The strategy for determining which agent speaks next in a group chat (round-robin, manual, auto).

## Mental Models
- **Multi-agent = team of specialists**: Like a human organization, each agent has a role, expertise, and tools. The coordinator (proxy) delegates and synthesizes.
- **CrewAI is more structured, AutoGen is more flexible**: Choose CrewAI for rigid enterprise workflows; AutoGen for exploratory, conversational agent interactions.

## Anti-patterns
- **Too many agents without clear roles**: Agents without well-defined responsibilities will produce redundant or conflicting work.
- **Ignoring observability**: Multi-agent systems are complex — use tools like AgentOps to monitor interactions and costs.

## Worked Example
Building a CrewAI jokester crew:
1. Define a `Joker` role agent with the task of generating jokes
2. Define a `Critic` role agent that evaluates and refines jokes
3. Set up a sequential crew: Joker creates → Critic refines → output
4. Execute with a topic and observe the collaborative output
5. Add AgentOps to monitor the interaction flow and token usage

## Key Takeaways
1. AutoGen Studio provides a visual, conversational approach to building multi-agent systems.
2. CrewAI offers a more structured, role-based approach suitable for enterprise applications.
3. Group chat patterns enable agents to collaborate through shared conversation.
4. Agent communication patterns (proxy, group chat, hierarchical) determine how agents interact.
5. Observability tools like AgentOps are essential for monitoring complex multi-agent interactions.

## Connects To
- **Ch 1**: Multi-agent systems are a natural extension of the agent concept.
- **Ch 7**: Nexus provides a platform for configuring multi-agent interactions.
- **Ch 11**: Planning and feedback mechanisms apply to multi-agent coordination.
