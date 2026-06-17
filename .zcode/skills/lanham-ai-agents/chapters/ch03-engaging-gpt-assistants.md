# Chapter 3: Engaging GPT assistants

## Core Idea
OpenAI's GPT Assistants platform provides a no-code/low-code way to build, customize, and publish AI agents. This chapter explores building assistants through the ChatGPT UI, creating custom actions with FastAPI, extending knowledge with file uploads, and publishing to the GPT Store.

## Frameworks Introduced
- **GPT Assistant Construction**: Name + description + instructions + conversation starters + rules = a functional assistant.
  - When to use: For rapid prototyping of agent/assistant concepts without writing code.
  - How: Use the GPT Builder chat interface for initial creation, then manually configure instructions and rules for precision.

- **Custom Actions via OpenAPI/FastAPI**: Extend assistants with external API calls by creating a FastAPI service and connecting it through OpenAPI specifications.
  - When to use: When the assistant needs to interact with external services (databases, APIs, custom logic).
  - How: Build a FastAPI service → generate OpenAPI spec → deploy locally with ngrok → connect to GPT assistant.

## Key Concepts
- **GPT Builder**: Chat-based interface for creating GPT assistants through conversation.
- **Instructions**: The system-level prompt that defines the assistant's behavior, rules, and output format.
- **Rules**: Explicit constraints that ensure consistent agent output (e.g., "always include nutritional information").
- **Persona**: Giving the assistant a specific personality (e.g., speaking as Julia Child) that shapes tone and references.
- **GPT Store**: Marketplace for publishing and discovering GPT assistants.
- **Code Interpretation**: Built-in capability for assistants to run Python code on uploaded files (CSV analysis, etc.).
- **File Upload Knowledge**: Uploading documents to give assistants specialized knowledge.

## Mental Models
- **Instructions + Rules = Agent Behavior**: The combination of high-level instructions and specific rules is what transforms a generic LLM into a specialized agent.
- **Custom actions = plugins**: FastAPI services connected via OpenAPI are the programmatic equivalent of ChatGPT plugins.

## Anti-patterns
- **Vague instructions**: Without specific rules, assistant output will be inconsistent and may not match expectations.
- **Ignoring economics**: GPT assistants consume tokens — always consider the cost of running an assistant at scale.

## Worked Example
Building a "Culinary Companion" GPT assistant:
1. Click "Create" in the GPT Store → interact with the GPT Builder chat
2. Define instructions: "Culinary Companion assists users with a friendly, engaging tone, reminiscent of Julia Child"
3. Add rules: always generate recipe images, estimate calories, provide shopping lists with prices, estimate cost per serving
4. Test by asking: "I have a bag of prepared frozen chicken strips and I want to make a romantic dinner for two"
5. The assistant generates a complete recipe with image, nutritional info, shopping list, and cost breakdown

## Key Takeaways
1. The GPT Assistants platform enables rapid prototyping of agent concepts through a no-code interface.
2. Rules and personas are essential for shaping consistent agent behavior.
3. Custom actions (via FastAPI + OpenAPI) extend assistants to interact with external services.
4. Knowledge assistants can be created by uploading documents for the LLM to reference.
5. Publishing to the GPT Store requires careful consideration of resource usage and user experience.

## Connects To
- **Ch 1**: GPT Assistants are one implementation of the agent spectrum.
- **Ch 5**: Custom actions here (OpenAI functions) connect to the broader function-calling patterns.
- **Ch 7**: The Nexus platform provides a programmatic alternative to GPT Assistants.
