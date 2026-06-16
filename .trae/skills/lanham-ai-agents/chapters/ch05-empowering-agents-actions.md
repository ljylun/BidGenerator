# Chapter 5: Empowering agents with actions

## Core Idea
Agents need to act beyond generating text. This chapter covers how agents use tools/actions through OpenAI function calling and Microsoft's Semantic Kernel (SK), which provides a structured way to define semantic functions (prompt-based) and native functions (code-based) that agents can invoke.

## Frameworks Introduced
- **OpenAI Function Calling**: Define functions with names, descriptions, and parameters in the API call. The LLM identifies when to call a function and provides the arguments.
  - When to use: When an agent needs to interact with external APIs or perform actions beyond text generation.
  - How: Add a `functions` array to the API call with function definitions → LLM returns function calls in the response → execute the function → pass results back to the LLM.

- **Semantic Kernel (SK)**: Microsoft's open-source SDK for building AI applications. Distinguishes between semantic functions (prompt templates that engage an LLM) and native functions (code that performs actions).
  - When to use: When building agent systems that need a structured way to manage prompts, functions, and context.
  - How: Create semantic functions from prompts → register native functions as plugins → combine them into skills → expose through a semantic service layer.

- **Semantic + Native Function Synergy**: Native functions can be embedded within semantic functions, creating layered execution where prompts guide code execution.
  - When to use: When you need the flexibility of LLM reasoning combined with the reliability of code execution.
  - How: Define a semantic function that references native functions → the LLM determines when to invoke native code → results feed back into the prompt context.

## Key Concepts
- **Semantic Function**: A prompt template that defines how to engage an LLM for a specific task. The "what" and "why" of an action.
- **Native Function**: Code that performs an action (API call, database query, file operation). The "how" of an action.
- **Plugin/Skill**: A collection of related semantic and native functions registered as a unit.
- **Context Variables**: Shared state passed between semantic and native functions in SK.
- **Semantic Service Layer**: An architecture where SK sits between the LLM and external APIs, managing the flow of prompts, function calls, and results.

## Mental Models
- **Semantic functions = LLM instructions, Native functions = code execution**: The LLM decides what to do (semantic), and code actually does it (native).
- **SK as middleware**: Semantic Kernel acts as the orchestration layer between LLMs and the outside world.

## Anti-patterns
- **Returning too little from functions**: Return as much information as possible — the LLM can filter and transform data better than pre-processing it.
- **Overly complex function descriptions**: Function descriptions should be clear and concise. The LLM uses them to decide when to call the function.

## Code Examples *(technical)*

```python
# OpenAI Function Calling example
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What's the weather in Calgary?"}],
    functions=[
        {
            "name": "get_weather",
            "description": "Get the current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "The city name"}
                },
                "required": ["city"]
            }
        }
    ]
)
```

## Worked Example
Building a semantic service agent with SK:
1. Install Semantic Kernel: `pip install semantic-kernel`
2. Create a semantic function (prompt template) for a movie recommender
3. Register a native function that scrapes a movie website
4. Combine them into a skill/plugin
5. Create a semantic service layer that exposes the skill through a chat interface
6. Test by asking for movie recommendations — the LLM uses the semantic function to understand the request, calls the native function to get data, and formats the response

## Key Takeaways
1. Actions extend agents from text generation to real-world interaction.
2. OpenAI function calling is the standard pattern for LLM-tool integration.
3. Semantic Kernel provides a structured framework for managing semantic and native functions.
4. Semantic functions (prompts) and native functions (code) work together — the LLM decides, code executes.
5. The semantic service layer pattern creates a clean architecture for agent systems.

## Connects To
- **Ch 2**: Function calling builds on the basic LLM API patterns.
- **Ch 6**: Actions are used by autonomous assistants and behavior trees.
- **Ch 7**: Nexus implements semantic and native functions as core features.
