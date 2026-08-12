---
name: tunstall-transformers
description: "Knowledge base from \"Natural Language Processing with Transformers\" by Tunstall, von Werra & Wolf. Use when applying transformer architectures for NLP tasks, building QA systems with Haystack, selecting models from the Hugging Face Hub, or understanding transformer internals (attention, encoder/decoder, scaling laws)."
---

<!-- argument-hint: [topic, framework name, or chapter number] -->

# Natural Language Processing with Transformers
**Author**: Lewis Tunstall, Leandro von Werra, Thomas Wolf | **Pages**: ~107 (excerpt) | **Chapters**: 3 | **Generated**: 2026-08-12

## How to Use This Skill

- **Without arguments** — load core frameworks for reference
- **With a topic** — ask about `retriever-reader`, `scaled attention`, `DPR`, `RAG`, or another indexed topic; I find and read the relevant chapter
- **With chapter** — ask for `ch03`, `ch07`, or `ch11`; I load that specific chapter
- **Browse** — ask "what chapters do you have?" to see the full index

When you ask about a topic not covered in Core Frameworks below, I will read the relevant chapter file before answering.

---

## Core Frameworks & Mental Models

### Transformer Architecture
Transformers stack three components: self-attention, position-wise feed-forward networks, and layer normalization. **Use scaled dot-product attention** (`softmax(QK^T / sqrt(d_k))V`) for any attention mechanism—the scaling prevents softmax saturation in high dimensions. **Use multi-head attention** when you need the model to attend to different representation subspaces simultaneously. **Use encoder layers** for understanding tasks (BERT family) and **decoder layers** for generation (GPT family).

### Model Selection by Task
- **Encoder-only** (BERT, RoBERTa, DistilBERT): Classification, NER, QA, embeddings. Bidirectional context.
- **Decoder-only** (GPT-2, GPT-Neo, CTRL): Text generation, in-context learning. Autoregressive.
- **Encoder-Decoder** (BART, T5): Summarization, translation, generative QA. Best of both worlds.

Rule: For QA readers, start with MiniLM (66M params, 2× faster than BERT-base) or RoBERTa-base. Upgrade to larger models only if accuracy is insufficient and latency budget allows.

### Retriever-Reader QA Pipeline
Production QA uses two stages: **retriever** fetches candidate documents, **reader** extracts answer spans. The retriever sets the system's performance ceiling—optimize it first.

- **BM25**: Fast, interpretable, no training. Use as default. Recall@3 typically >0.95.
- **DPR**: Dense embeddings via two BERT encoders. Better for semantic/vocabulary mismatch but needs GPU and domain fine-tuning.
- **RAG**: Extends retriever-reader with a generator (BART) for free-form answers. Use when answers must be synthesized from multiple documents.

### Scaling Laws
Loss follows power-law relationships with model size (N), compute (C), and dataset size (D): `L ∝ N^(-α)`. Larger models are more sample-efficient—they reach target loss with fewer steps. **Scale N, C, and D in tandem** rather than optimizing architecture on a fixed budget.

### Efficient Attention
Standard self-attention is O(n²). For sequences >2k tokens, switch to:
- **Sparse attention** (Longformer, BigBird): Global + band + dilated patterns. Reaches 4,096 tokens.
- **Linearized attention** (Performer, Linear Transformer): Kernel trick reduces to O(n).

### Multimodal Frontiers
- **TAPAS**: Natural language querying of tables. Flattens cells as tokens, learns SUM/AVERAGE/COUNT aggregations.
- **CLIP**: Zero-shot image classification via contrastive learning on 400M image-text pairs. No task-specific training needed.
- **wav2vec 2.0**: Self-supervised ASR. Competitive results with only minutes of labeled speech.

---

## Chapter Index

| # | Title | Key Frameworks |
|---|-------|----------------|
| [ch03](chapters/ch03-transformer-anatomy.md) | Transformer Anatomy | Scaled dot-product attention, Multi-head attention, Encoder/Decoder layers, Position embeddings, Transformer taxonomy |
| [ch07](chapters/ch07-question-answering.md) | Question Answering | Retriever-Reader architecture, Span classification, BM25, DPR, RAG, Domain adaptation, Haystack pipelines |
| [ch11](chapters/ch11-future-directions.md) | Future Directions | Scaling laws, Sparse attention, Linearized attention, TAPAS, CLIP, wav2vec 2.0, Multimodal transformers |

## Topic Index

- **Attention** → ch03
- **BM25** → ch07
- **BART** → ch03
- **BERT** → ch03
- **BigBird** → ch03, ch11
- **CLIP** → ch11
- **Contrastive learning** → ch11
- **DPR** → ch07
- **Domain adaptation** → ch07
- **Encoder-Decoder** → ch03
- **Encoder-only** → ch03
- **Exact Match (EM)** → ch07
- **F1-score** → ch07
- **FAISS** → ch07
- **GPT** → ch03
- **Haystack** → ch07
- **Layer normalization** → ch03
- **Linearized attention** → ch11
- **Longformer** → ch11
- **MiniLM** → ch07
- **Multimodal** → ch11
- **Performer** → ch11
- **Position embeddings** → ch03
- **QA pipeline** → ch07
- **RAG** → ch07
- **Recall@k** → ch07
- **Retriever-Reader** → ch07
- **RoBERTa** → ch03
- **Scaling laws** → ch11
- **Sparse attention** → ch11
- **Span classification** → ch07
- **TAPAS** → ch11
- **ViT** → ch11
- **wav2vec 2.0** → ch11
- **Zero-shot classification** → ch11

## Supporting Files

- [glossary.md](glossary.md) — all key terms with definitions
- [patterns.md](patterns.md) — all techniques and design patterns
- [cheatsheet.md](cheatsheet.md) — quick reference tables and decision guides

---

## Scope & Limits

This skill covers the book content only. For hands-on implementation in your codebase, combine with project-specific tools. For topics beyond this book, check related skills or ask the agent directly.
