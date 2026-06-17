# Chapter 10: Agent reasoning and evaluation

## Core Idea
Agents need reasoning capabilities to solve complex problems and evaluation mechanisms to ensure quality. This chapter covers a spectrum of reasoning techniques from simple question-answering to advanced methods like self-consistency and Tree of Thought (ToT) prompting, all implemented using Prompt Flow.

## Frameworks Introduced
- **Reasoning Spectrum**: A progression of reasoning techniques from simple to complex:
  - **Question-Answer Prompting**: Basic context + question → answer.
  - **Few-Shot Prompting**: Provide examples to guide the LLM's behavior, even to use made-up words correctly.
  - **Zero-Shot Prompting**: Guide the LLM with rules/guidelines without examples.
  - **Chain of Thought (CoT)**: Encourage the LLM to show its reasoning step by step.
  - **Self-Consistency Prompting**: Generate multiple reasoning paths and select the most consistent answer.
  - **Tree of Thought (ToT)**: Explore multiple reasoning branches, evaluate them, and select the best path.
  - **Automatic Reasoning with Tools (ART)**: Combine reasoning with tool use for complex problem-solving.

- **Planning vs Reasoning Axes**: The book maps techniques on two axes — Thought (y-axis: how the LLM reasons) and Planning (x-axis: how the LLM organizes solutions).
  - When to use: When selecting the right reasoning technique for a given problem complexity.
  - How: Simple problems → direct/few-shot. Complex reasoning → CoT/ToT. Tool-dependent → ART.

## Key Concepts
- **Few-Shot Learning**: Providing 1-3 examples in the prompt to guide the LLM's behavior.
- **Zero-Shot Learning**: Using only rules/guidelines, no examples.
- **Chain of Thought**: Prompting the LLM to "think step by step" before giving the final answer.
- **Self-Consistency**: Running the same prompt multiple times and taking the majority vote.
- **Tree of Thought**: Generating multiple reasoning paths (branches), evaluating each, and selecting the best.
- **Embedding-Based Evaluation**: Using embedding similarity to automatically evaluate LLM outputs against expected answers.

## Mental Models
- **Reasoning depth scales with problem complexity**: Simple questions need simple prompts; complex problems need CoT/ToT.
- **Multiple reasoning paths > single path**: Self-consistency and ToT are more reliable because they explore multiple possibilities.

## Anti-patterns
- **Using complex reasoning for simple tasks**: Don't use ToT for basic question-answering — it wastes tokens and time.
- **Skipping evaluation**: Always evaluate reasoning outputs — even advanced techniques can produce incorrect results.

## Worked Example
Few-shot prompting to teach a made-up word:
1. System prompt: "You are an eccentric word dictionary maker..."
2. Provide examples: "whatpu" → example sentence, "farduddle" → example sentence
3. User input: "A sunner is a meal we eat in Canada at sunset, please use the word in a sentence"
4. LLM correctly uses "sunner" in context: "After a long hike, we sat by the lake and enjoyed a peaceful sunner..."

## Key Takeaways
1. Reasoning techniques exist on a spectrum from simple (direct) to complex (ToT).
2. Chain of Thought prompting is the most practical technique for improving reasoning quality.
3. Self-consistency and ToT provide higher reliability at the cost of more LLM calls.
4. Evaluation through embedding similarity enables automated quality assessment.
5. The Thought/Planning axes help select the right technique for the problem.

## Connects To
- **Ch 9**: Prompt engineering strategies are the foundation for reasoning techniques.
- **Ch 11**: Planning and feedback build on these reasoning capabilities.
