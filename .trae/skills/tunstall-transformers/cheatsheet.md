# Cheatsheet

## Model Selection Decision Tree

```
What task are you solving?
├── Text understanding (classification, NER, QA)
│   ├── Need maximum accuracy, latency is secondary
│   │   └── RoBERTa-large or DeBERTa-v3
│   ├── Need speed + good accuracy
│   │   └── MiniLM or DistilBERT (2× faster than BERT-base)
│   └── Need multilingual support
│       └── XLM-RoBERTa-large
├── Text generation (summarization, translation, dialogue)
│   ├── Open-ended generation
│   │   └── GPT-2, GPT-Neo, or BART
│   └── Controlled generation
│       └── CTRL (add control tokens at start)
└── Sequence-to-sequence (translation, summarization, QA generation)
    ├── Best quality
    │   └── BART-large or T5-11B
    └── Best speed
        └── DistilBART or T5-small
```

## Retriever Selection

| Scenario | Choice | Rationale |
|----------|--------|-----------|
| Corpus < 10k docs, low latency requirement | BM25 (Elasticsearch) | No training, sub-10ms latency |
| Semantic search with synonyms | DPR + FAISS | Dense embeddings capture meaning |
| Multilingual corpus | XLM-R-based dense retriever | Multilingual pretraining |
| Domain-specific jargon | DPR fine-tuned on domain | BM25 fails on vocabulary mismatch |
| Constrained hardware | BM25 or sparse embedding | DPR needs GPU for reasonable latency |

## QA System Design

| Decision | Rule of Thumb |
|----------|---------------|
| `top_k_retriever` | Start with 3–5. Increase until recall plateaus (usually k=10). |
| `top_k_reader` | 3–5 answers. More increases latency linearly. |
| `max_seq_length` | Model max (e.g., 512 for BERT). |
| `doc_stride` | 128 (25% of max_seq_length). Smaller = more overlap, more windows. |
| Retriever type | Start with BM25. Switch to DPR only if recall@3 < 0.9. |
| Reader base | MiniLM for prototyping; RoBERTa-base for production. |

## Evaluation Thresholds

| Metric | Good | Acceptable | Poor |
|--------|------|------------|------|
| Retriever Recall@3 | > 0.95 | 0.80–0.95 | < 0.80 |
| Reader EM (SQuAD 2.0) | > 70 | 50–70 | < 50 |
| Reader F1 (SQuAD 2.0) | > 75 | 60–75 | < 60 |
| End-to-end EM (domain) | > 0.5× SQuAD baseline | 0.2–0.5× | < 0.2× |

## Transformer Architecture Quick Reference

| Architecture | Pretraining | Strengths | Weaknesses | Examples |
|--------------|-------------|-----------|------------|----------|
| Encoder-only | MLM (+ NSP) | Understanding, feature extraction | Cannot generate | BERT, RoBERTa, DistilBERT |
| Decoder-only | Causal LM | Generation, in-context learning | No bidirectional context | GPT-2, GPT-Neo, CTRL |
| Encoder-Decoder | MLM + LM | Seq2seq, generation with context | Larger, slower | BART, T5, BigBird |

## Scaling Decision Rules

- **Dataset < 10k examples**: Start from SQuAD-pretrained model; fine-tune on domain. Do not train from scratch.
- **Dataset 10k–100k examples**: Can fine-tune from generic pretrained checkpoint (BERT-base).
- **Dataset > 100k examples**: Consider training from scratch or continued pretraining on domain corpus.
- **Latency < 100ms**: Use DistilBERT or MiniLM; avoid models > 200M parameters.
- **Latency < 1s**: RoBERTa-base or ALBERT are feasible on CPU with batching.
- **Throughput > 100 QPS**: Use batching + quantization + ONNX Runtime.

## Attention Efficiency Rules

| Sequence Length | Recommended Attention |
|-----------------|----------------------|
| < 512 tokens | Full self-attention (BERT, RoBERTa) |
| 512–2k tokens | Full attention with gradient checkpointing |
| 2k–4k tokens | Sparse attention (Longformer, BigBird) |
| 4k–16k tokens | Sparse + linearized (Longformer-Ensemble) |
| > 16k tokens | Linearized attention (Performer) or chunking |

## Domain Adaptation Checklist

- [ ] Start with SQuAD-pretrained reader (MiniLM or RoBERTa)
- [ ] Convert domain data to SQuAD JSON format
- [ ] Fine-tune for 1–3 epochs, batch size 8–16
- [ ] Evaluate with both EM and F1 on held-out test set
- [ ] If EM improves < 2×, try data augmentation (paraphrasing, back-translation)
- [ ] If still poor, inspect error cases for annotation quality issues

## Multimodal Model Selection

| Modalities | Model | Use Case |
|------------|-------|----------|
| Text + Vision (zero-shot) | CLIP | Image classification without labeled data |
| Text + Vision (VQA) | LXMERT, VisualBERT | Answering questions about images |
| Text + Layout (documents) | LayoutLMv2/v3 | Receipt, invoice, form understanding |
| Text + Table | TAPAS | Natural language querying of tables |
| Text + Audio (ASR) | wav2vec 2.0 | Speech-to-text with limited labeled data |
| Text + Audio (unsupervised) | wav2vec-U | ASR for low-resource languages, no aligned data |
| Image generation | DALL·E, iGPT | Text-to-image synthesis |

## Common Pitfalls

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| EM=0, F1 low | Answer span off by one token or punctuation | Normalize predictions (lowercase, strip punctuation) before scoring |
| High retriever recall, low reader EM | Reader not trained on domain | Fine-tune reader on domain data |
| Low retriever recall | BM25 vocabulary mismatch | Switch to DPR or expand query with synonyms |
| Slow inference (>1s) | Model too large, no batching | Distill to smaller model; enable batching; use ONNX |
| Answers across windows | `doc_stride` too small | Increase `doc_stride` to reduce overlap; deduplicate answers |
| Hallucinated answers | Reader predicts text not in context | Enable `return_no_answer=True`; set confidence threshold |
