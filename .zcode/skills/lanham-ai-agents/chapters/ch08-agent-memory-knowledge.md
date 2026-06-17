# Chapter 8: Understanding agent memory and knowledge

## Core Idea
Agents need memory and knowledge to be effective beyond single interactions. This chapter covers Retrieval Augmented Generation (RAG) as the standard mechanism for providing external context to prompts, and explores different forms of agent memory (short-term, long-term, semantic) and knowledge systems.

## Frameworks Introduced
- **Retrieval Augmented Generation (RAG)**: A two-phase pattern — (1) Index documents by loading, chunking, embedding into vectors, and storing in a vector database; (2) Query by embedding the query, retrieving similar chunks, and augmenting the prompt with context.
  - When to use: Whenever an agent needs to reference external documents or knowledge beyond its training data.
  - How: Load documents → split into chunks → embed with an embedding model → store in vector DB → at query time, embed query → similarity search → augment prompt with retrieved chunks.

- **Memory Systems**: Short-term (conversation history), long-term (persistent facts/preferences), and semantic (embedding-based retrieval of relevant memories).
  - When to use: When agents need to remember user preferences, previous tasks, or contextual information across interactions.
  - How: Store memories as structured data or embeddings → retrieve relevant memories based on current context → augment prompts with retrieved memories.

## Key Concepts
- **Vector Database**: Stores document chunks as embeddings for similarity search (e.g., Chroma, Pinecone, FAISS).
- **Embedding Model**: Converts text into vector representations that capture semantic meaning.
- **Contextual Retrieval**: Retrieving relevant information based on semantic similarity rather than exact keyword matching.
- **Prompt Augmentation**: Adding retrieved knowledge/memory to the prompt to provide the LLM with relevant context.
- **Knowledge vs Memory**: Knowledge is external, document-based context. Memory is interaction-based, experiential context.

## Mental Models
- **RAG = giving the LLM a reference library**: Instead of expecting the LLM to know everything, RAG provides relevant documents at query time.
- **Memory = agent's personal experience**: While knowledge is external (documents), memory is internal (previous interactions, preferences).

## Anti-patterns
- **Ignoring chunking strategy**: Poor chunking leads to irrelevant retrievals — chunk size and overlap matter significantly.
- **Retrieving too many chunks**: Too much context can confuse the LLM — retrieve only what's most relevant.

## Worked Example
Building a knowledge assistant with RAG:
1. Load a PDF document (e.g., a technical manual)
2. Split into 500-word chunks with 50-word overlap
3. Embed chunks using OpenAI's text-embedding-ada-002
4. Store embeddings in a vector database
5. User asks: "How do I configure the agent's temperature?"
6. Embed the query → find the 3 most similar chunks → augment the prompt
7. LLM generates an answer grounded in the document content

## Key Takeaways
1. RAG is the standard mechanism for providing external knowledge to agents.
2. The two phases of RAG are indexing (load → chunk → embed → store) and querying (embed query → retrieve → augment prompt).
3. Memory systems (short-term, long-term, semantic) give agents continuity across interactions.
4. Knowledge is document-based; memory is experience-based — both augment prompts.
5. Vector databases and embedding models are the technical foundation for retrieval.

## Connects To
- **Ch 7**: Nexus implements knowledge and memory features.
- **Ch 9**: Prompt engineering strategies (Provide Reference Text) directly use RAG outputs.
