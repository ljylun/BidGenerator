# Chapter 3: Transformer Anatomy

## Core Idea
Transformers are built from three core components—self-attention, feed-forward networks, and layer normalization—stacked into encoder/decoder layers. Understanding these building blocks lets you implement transformers from scratch, choose the right architecture for your task, and navigate the rapidly expanding model zoo.

## Frameworks Introduced
- **Scaled Dot-Product Attention**: Compute attention scores as `softmax(QK^T / sqrt(d_k))V`. Use when building any attention mechanism; the scaling prevents softmax saturation for large embedding dimensions.
- **Multi-Head Attention**: Run multiple scaled dot-product attention heads in parallel, each with different learned projections, then concatenate outputs. Use when you need the model to attend to information from different representation subspaces at different positions.
- **Transformer Encoder Layer**: Combine multi-head attention + residual connection + layer norm + position-wise feed-forward + residual connection + layer norm. Use as the basic building block for encoder-only models.
- **Transformer Decoder Layer**: Similar to encoder but with masked self-attention (prevents looking ahead) and encoder-decoder attention. Use for autoregressive text generation.
- **Position Embeddings**: Inject token position information since attention is permutation-invariant. Options include learnable embeddings, relative embeddings, and rotary position embeddings (RoPE).
- **The Transformer Tree of Life**: A taxonomy dividing models into Encoder-only (BERT family), Decoder-only (GPT family), and Encoder-Decoder (BART, T5) branches.

## Key Concepts
- **Self-Attention**: Mechanism where each token attends to all other tokens in the sequence, producing context-aware representations.
- **Query/Key/Value (Q/K/V)**: The three vectors derived from input embeddings; attention computes weighted sums of values using query-key similarity.
- **Hidden State / Context**: The sequence of embedding vectors output by the encoder, serving as memory for the decoder.
- **Token Type IDs**: In BERT-like models, segment embeddings distinguishing question tokens (0) from context tokens (1).
- **Knowledge Distillation**: Technique used in DistilBERT to compress a large teacher model into a smaller student model while preserving most of the performance.
- **Span Classification**: Framing QA as predicting start and end token indices of the answer span.

## Mental Models
- **Attention as a differentiable dictionary lookup**: The query looks up keys, and the values are returned as a weighted sum. Think of it as a soft, content-based addressing mechanism.
- **Encoder = understanding, Decoder = generation**: Encoders create rich contextual representations; decoders use those representations to generate output sequences token-by-token.
- **Larger models need more data, not just more layers**: Scaling laws show that increasing model size (N), compute (C), and dataset size (D) together yields better results than architectural tweaks alone.
- **Choose architecture by task**: Encoders for understanding (classification, NER, QA), Decoders for generation (summarization, translation), Encoder-Decoder for sequence-to-sequence tasks.

## Anti-patterns
- **Ignoring position information**: Never feed raw token embeddings without positional signals; the model cannot distinguish "cat sat mat" from "mat sat cat".
- **Using full attention for very long sequences**: Standard self-attention scales O(n²); for documents longer than ~2k tokens, use sparse attention (Longformer, BigBird) or linearized attention.
- **Assuming bigger is always better**: DistilBERT achieves 97% of BERT's performance with 40% less memory and 60% faster inference. Profile latency and memory before defaulting to the largest model.
- **Treating all models as interchangeable**: BERT-base and RoBERTa-base have different pretraining schemes; a model fine-tuned on SQuAD may catastrophically fail on subjective review data without domain adaptation.

## Code Examples
```python
import torch
import torch.nn.functional as F
from math import sqrt

# Scaled dot-product attention
def scaled_dot_product_attention(query, key, value):
    dim_k = key.size(-1)
    scores = torch.bmm(query, key.transpose(1, 2)) / sqrt(dim_k)
    weights = F.softmax(scores, dim=-1)
    return torch.bmm(weights, value)

# Multi-head attention
class MultiHeadAttention(nn.Module):
    def __init__(self, config):
        super().__init__()
        embed_dim = config.hidden_size
        num_heads = config.num_attention_heads
        head_dim = embed_dim // num_heads
        self.heads = nn.ModuleList(
            [AttentionHead(embed_dim, head_dim) for _ in range(num_heads)]
        )
        self.output_linear = nn.Linear(embed_dim, embed_dim)

    def forward(self, hidden_state):
        attn_outputs = torch.cat([head(hidden_state) for head in self.heads], dim=-1)
        return self.output_linear(attn_outputs)

# Transformer encoder layer
class TransformerEncoderLayer(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.layer_norm_1 = nn.LayerNorm(config.hidden_size)
        self.layer_norm_2 = nn.LayerNorm(config.hidden_size)
        self.attention = MultiHeadAttention(config)
        self.feed_forward = FeedForward(config)

    def forward(self, x):
        hidden_state = self.layer_norm_1(x)
        x = x + self.attention(hidden_state)
        x = x + self.feed_forward(self.layer_norm_2(x))
        return x
```
- **What it demonstrates**: Building a transformer encoder from scratch in PyTorch, showing how attention, normalization, and skip connections compose.

## Worked Example
**Implementing a complete transformer encoder from scratch:**
1. Define token embeddings + positional embeddings
2. Create scaled dot-product attention with Q/K/V projections
3. Wrap in MultiHeadAttention with multiple heads
4. Add position-wise feed-forward network (hidden size = 4× embed_dim, GELU activation)
5. Stack encoder layers with residual connections and layer norm
6. Add a task-specific classification head

The key insight is that each component is simple in isolation, but the residual connections and layer normalization are critical for training deep stacks. Without them, gradients vanish or explode.

## Key Takeaways
1. Self-attention computes weighted sums of value vectors using query-key similarity; scaling by `sqrt(d_k)` prevents softmax saturation.
2. Multi-head attention lets the model jointly attend to information from different representation subspaces.
3. Encoder-only models (BERT) excel at understanding tasks; decoder-only (GPT) excel at generation; encoder-decoder (BART) excel at sequence-to-sequence.
4. Position embeddings are mandatory because attention is permutation-invariant.
5. When scaling to long sequences, switch from full O(n²) attention to sparse or linearized variants.

## Connects To
- **Ch 7**: Uses transformer encoders (BERT, MiniLM) as the backbone for extractive QA readers.
- **Ch 11**: Discusses scaling these architectures to larger sizes and making attention more efficient.
- **Hugging Face Transformers**: All these components are pre-implemented in the library; understanding them helps with debugging and architecture selection.
