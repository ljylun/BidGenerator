# Patterns

## Scaled Dot-Product Attention

**When to use**: Building any attention mechanism, from simple self-attention to cross-attention in encoder-decoder models.

**How**: Project inputs into query (Q), key (K), and value (V) matrices. Compute attention scores as `softmax(QK^T / sqrt(d_k))`. Multiply scores by V to get weighted outputs. The scaling factor `1/sqrt(d_k)` prevents softmax from saturating when dot products grow large for high-dimensional embeddings.

**Trade-offs**: Full attention is O(n²) in sequence length. For n > 2k, consider sparse or linearized attention. Multi-head attention adds parameter overhead but lets the model attend to different subspaces.

---

## Multi-Head Attention

**When to use**: When you need the model to jointly attend to information from different representation subspaces at different positions. Standard in all transformer architectures.

**How**: Run h independent scaled dot-product attention heads in parallel, each with learned linear projections. Concatenate the outputs and apply a final linear projection. Each head operates on `d_k = d_model / h` dimensions.

**Trade-offs**: More heads increase capacity but also parameter count and compute. BERT-base uses 12 heads with 64-dimensional each. Rule of thumb: `head_dim` should divide `embed_dim` evenly.

---

## Transformer Encoder Layer

**When to use**: Building encoder-only models for understanding tasks (classification, NER, QA, sentence embeddings).

**How**: 
1. Layer norm on input → Multi-head attention → Residual connection (`x + attention`)
2. Layer norm on result → Position-wise feed-forward → Residual connection (`x + ff`)

**Feed-forward layer: linear (d_model → 4×d_model) → GELU → linear (4×d_model → d_model) → dropout.

**Trade-offs**: Post-LN (attention/FFN before norm) is the original design but can cause training instability. Pre-LN (norm before sublayer) trains more stably. Encoder-only models cannot generate sequences autoregressively.

---

## Transformer Decoder Layer

**When to use**: Autoregressive text generation (GPT family), where each token can only attend to previous tokens.

**How**: Similar to encoder layer but with two attention sublayers:
1. Masked self-attention (queries attend only to current and previous positions)
2. Encoder-decoder attention (queries from decoder, keys/values from encoder)
3. Position-wise feed-forward

**Trade-offs**: Masked attention ensures autoregressive property but prevents parallel training over the full sequence. Must use causal masking during training and inference.

---

## Position Embeddings

**When to use**: Always. Attention is permutation-invariant, so the model needs explicit position information to understand token order.

**How**:
- **Learnable**: A lookup table of position indices added to token embeddings. Used in BERT.
- **Relative**: Encode distances between tokens rather than absolute positions. Used in T5.
- **Rotary (RoPE)**: Rotate query/key vectors by angles proportional to token position. Used in GPT-Neo, PaLM.

**Trade-offs**: Learnable positions are simple but limited to training sequence length. Relative and RoPE generalize better to longer sequences at inference.

---

## Retriever-Reader Pipeline

**When to use**: Production QA over corpora larger than a few thousand documents. The retriever reduces the search space, and the reader extracts precise answers.

**How**:
1. **Retriever**: Fetch top-k relevant documents using sparse (BM25) or dense (DPR) retrieval.
2. **Reader**: Run a span classification model on retrieved documents to predict answer start/end positions.
3. **Post-processing**: Apply answer deduplication, confidence thresholding, and reranking.

**Trade-offs**: BM25 is fast, interpretable, and requires no training. DPR handles synonyms better but needs embedding index updates and GPU for latency. The retriever's recall@k sets the ceiling for the whole system.

---

## Sparse Retrieval (BM25)

**When to use**: Baseline retriever when you need fast, interpretable search without training embedding models. Works well for keyword-heavy queries.

**How**: Represent documents and queries as bag-of-words vectors weighted by TF-IDF with saturation and document length normalization. Score by inner product. In Haystack: `ElasticsearchRetriever` with BM25.

**Trade-offs**: Fails on vocabulary mismatch (e.g., "smartphone" vs "cell phone"). No semantic understanding. Strengths: no training needed, extremely fast, explainable scores.

---

## Dense Passage Retrieval (DPR)

**When to use**: When BM25 recall is insufficient due to synonymy, paraphrasing, or semantic mismatch. Requires GPU for low-latency inference.

**How**: 
1. Encode all passages offline with a passage encoder (BERT).
2. At query time, encode the question with a question encoder (BERT).
3. Retrieve top-k passages by maximum inner product (or FAISS for speed).

**Trade-offs**: 2–5× slower than BM25. Needs domain fine-tuning to beat BM25 on small datasets. Embeddings must be updated when documents change. Best paired with FAISS for large corpora.

---

## Span Classification Head

**When to use**: Extractive QA where the answer is a contiguous span of text in a context passage.

**How**: Add a linear layer on top of the transformer's final hidden states to produce start logits and end logits. Train with cross-entropy loss on start and end positions. At inference, take argmax of start and end logits (constrained to valid spans).

**Trade-offs**: Cannot generate answers not present in the context. Sliding windows needed for long contexts. Duplicate answers across overlapping windows must be post-processed.

---

## Domain Adaptation for QA

**When to use**: When a SQuAD-pretrained model performs poorly on your domain (e.g., customer reviews, legal contracts, medical records).

**How**: 
1. Start with a model fine-tuned on SQuAD 2.0 (strong reading comprehension baseline).
2. Convert your domain data to SQuAD JSON format.
3. Fine-tune for 1–3 epochs with small batch size (8–16).

**Trade-offs**: Two-stage fine-tuning (SQuAD → domain) beats single-stage (domain only) when domain data is small (<5k examples). Risk of catastrophic forgetting is low because the second stage is brief.

---

## Sliding Window for Long Contexts

**When to use**: When question-context pairs exceed the model's maximum sequence length (e.g., 512 for BERT).

**How**: Set `return_overflowing_tokens=True` in the tokenizer with `max_length` and `stride` parameters. This creates overlapping windows. Each window is processed independently, and answers are deduplicated by span.

**Trade-offs**: Larger stride → fewer windows, faster inference, but risk of splitting answer spans. Smaller stride → more coverage, slower inference. Rule of thumb: `stride = max_length / 4`.

---

## RAG (Retrieval-Augmented Generation)

**When to use**: When answers need to be synthesized from multiple documents or rephrased, not just extracted as spans.

**How**: 
1. Encode question with DPR question encoder → retrieve top-k passages.
2. Feed retrieved passages + question to a seq2seq generator (BART).
3. Generator produces free-form answer conditioned on retrieved context.

**Trade-offs**: Generates fluent, composed answers. Higher latency than extractive QA (generation is slower than span selection). Risk of hallucination if retrieved passages are irrelevant.

---

## TAPAS Table Question Answering

**When to use**: Natural language querying of structured tabular data without writing SQL or Pandas code.

**How**: Flatten table cells into token sequences. TAPAS learns to predict cell selection plus aggregation operators (NONE, SUM, AVERAGE, COUNT, MIN, MAX).

**Trade-offs**: Requires all columns to be strings. Works best on tables with <50 rows and <20 columns. Slower than raw SQL but accessible to non-technical users.

---

## CLIP Zero-Shot Classification

**When to use**: Image classification when you lack labeled training data or need flexible class definitions that change frequently.

**How**: 
1. Encode candidate class names with CLIP text encoder.
2. Encode image with CLIP image encoder.
3. Compute cosine similarity between image embedding and all class embeddings.
4. Predict class with highest similarity.

**Trade-offs**: No task-specific training needed. Performance approaches fully supervised models on common categories but may lag on fine-grained or niche classes. Inference requires both text and image encoders.
