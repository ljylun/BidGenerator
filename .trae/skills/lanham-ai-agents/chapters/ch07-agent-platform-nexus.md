# Chapter 7: Assembling and using an agent platform

## Core Idea
Nexus is an open-source teaching platform developed with this book to demonstrate core agent concepts. It integrates personas/profiles, actions/tools, knowledge/memory, and planning/feedback into a unified Streamlit-based chat application. This chapter shows how to use and extend Nexus.

## Frameworks Introduced
- **Nexus Architecture**: A four-component agent platform — Personas/Profiles (who the agent is), Actions/Tools (what the agent can do), Knowledge/Memory (what the agent knows), Planning/Feedback (how the agent plans and adapts).
  - When to use: As a learning platform for understanding agent architecture or as a foundation for building custom agent systems.
  - How: Install from GitHub → configure API keys → select persona, actions, knowledge, and planning options → run and interact through the Streamlit UI.

- **Semantic + Native Functions in Nexus**: Nexus supports both semantic (prompt-based) and native (code-based) functions as agent tools, managed through a plugin-style interface.
  - When to use: When building custom tools for agents within the Nexus platform.
  - How: Define functions as semantic prompts or native Python code → register as plugins → agents can discover and invoke them.

## Key Concepts
- **Persona/Profile**: The personality and primary motivator for an agent. Defines how the agent communicates and approaches tasks.
- **Actions/Tools**: Both semantic (prompt-driven) and native (code-driven) functions available to the agent.
- **Knowledge/Memory**: Additional context sources — from short-term conversation history to long-term semantic memory.
- **Planning/Feedback**: Configurable planning strategies and feedback mechanisms for agent behavior.
- **Streamlit Interface**: The web-based UI for Nexus, providing a ChatGPT-like experience with additional agent configuration options.

## Mental Models
- **Nexus = agent configuration dashboard**: Think of Nexus as a control panel where you configure all four dimensions of an agent (persona, actions, knowledge, planning) and observe how they interact.
- **Platform as teaching tool**: Nexus is designed to make agent concepts tangible and experimentable.

## Anti-patterns
- **Too many actions without focus**: Giving an agent too many tools can confuse it — provide only the actions needed for the goal.
- **Ignoring planning configuration**: The planning/feedback component is what transforms a chatbot into an agent — don't leave it as default.

## Worked Example
Running Nexus:
1. Create Python 3.10 virtual environment
2. `pip install git+https://github.com/cxbxmxcx/Nexus.git`
3. Set `OPENAI_API_KEY` environment variable
4. `nexus run` → launches Streamlit web interface
5. Create a new user → start a chat thread
6. Configure agent: select model (OpenAI/Gemini/Claude), persona, actions, and planning options
7. Interact with the configured agent through the chat interface

## Key Takeaways
1. Nexus demonstrates the four core components of an agent platform: personas, actions, knowledge, and planning.
2. The platform supports both semantic (prompt) and native (code) functions as agent tools.
3. Nexus uses Streamlit for the UI, making it accessible and easy to extend.
4. The platform is designed as a teaching tool — it evolves with each chapter of the book.
5. Agent configuration (persona + actions + knowledge + planning) is as important as the underlying LLM.

## Connects To
- **Ch 5**: Semantic and native functions from SK are implemented as Nexus plugins.
- **Ch 8**: Knowledge and memory features in Nexus build on RAG concepts.
- **Ch 11**: Planning and feedback in Nexus demonstrate the concepts from that chapter.
