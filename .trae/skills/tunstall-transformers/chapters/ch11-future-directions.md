# Chapter 11: Future Directions

## Core Idea
Scaling transformers to larger sizes reveals both empirical regularities (scaling laws) and practical bottlenecks (infrastructure, cost, evaluation). Simultaneously, researchers are pushing transformers beyond text into vision, audio, tables, and multimodal settings. This chapter maps the frontier: what we know about scaling, how to make attention efficient, and where transformers are heading next.

## Frameworks Introduced
- **Scaling Laws**: Power-law relationships between cross-entropy loss and compute budget (C), dataset size (D), and model size (N). Use to predict model performance before training; focus on scaling all three in tandem rather than optimizing architecture.
- **Sparse Attention Patterns**: Limit query-key pairs using atomic patterns—global, band, dilated, random, block local. Use when processing sequences longer than 2k tokens; Longformer and BigBird combine patterns to reach 4,096 tokens.
- **Linearized Attention**: Express attention as kernel function to reduce complexity from O(n²) to O(n). Use when you need long sequences but cannot afford sparse attention overhead; Linear Transformer and Performer are popular implementations.
- **Multimodal Transformers**: Combine modalities (text + vision, text + audio, text + tables) in a single architecture. Use when your task requires understanding across modalities.
- **TAPAS (Table Parser)**: Apply transformers to tables by flattening cells as tokens and learning to aggregate answers (SUM, AVERAGE, COUNT). Use for natural language querying of structured data.
- **wav2vec 2.0**: Self-supervised speech representation learning using transformer layers + CNN, trained on 960 hours of unlabeled audio. Use for ASR with limited labeled data.
- **CLIP (Contrastive Language-Image Pretraining)**: Jointly train text and image encoders with contrastive learning on 400M image-caption pairs. Use for zero-shot image classification without task-specific training.

## Key Concepts
- **Scaling Exponent (α)**: Typical values 0.05–0.095; determines how fast loss decreases with scale. Larger α means more gain from scaling.
- **Sample Efficiency**: Larger models reach the same loss with fewer training steps than smaller models. Counterintuitively, big models are more data-efficient.
- **Infrastructure Bottleneck**: Training GPT-3 costs millions of dollars and requires hundreds of GPUs. Most companies should use hosted APIs (OpenAI, Hugging Face Accelerated Inference) instead.
- **Human Reporting Bias**: Text frequencies don't reflect real-world frequencies. Models trained on web text have distorted world models.
- **iGPT**: Applies GPT-style autoregressive pretraining to pixels. Demonstrates transformers generalize beyond language.
- **ViT (Vision Transformer)**: Splits images into patches, embeds them like tokens, and processes with a standard transformer encoder. Scales better than CNNs on large datasets.
- **LayoutLM**: Multimodal model for scanned documents combining text, image, and layout embeddings. State-of-the-art for receipt/invoice understanding.
- **wav2vec-U**: Unsupervised speech recognition using clustering + GANs, no aligned speech-text data required. Enables ASR for low-resource languages.
- **VQA (Visual Question Answering)**: Answer natural language questions about images. Models like LXMERT and VisualBERT combine ResNet features with transformer encoders.
- **Contrastive Learning**: Training objective that maximizes similarity of matched image-text pairs while minimizing similarity of mismatched pairs. Used in CLIP.

## Mental Models
- **Bigger models learn faster (sample efficiency)**: A 10× larger model may need only 1/10 the training steps to reach the same loss. Don't compare models by training time alone.
- **Scaling laws let you extrapolate**: Train small models, measure loss curves, then extrapolate to predict what a 100× larger model would achieve.
- **Attention is the bottleneck, not the layers**: O(n²) self-attention limits sequence length. When you hit memory walls, optimize attention before adding more layers.
- **Modality gaps are semantic, not just signal-based**: Combining vision and text isn't just about concatenating features—you need pretraining objectives that align the modalities (contrastive learning for CLIP, masked modeling for LayoutLM).
- **Zero-shot is the new fine-tuning**: CLIP shows that large-scale pretraining + contrastive learning can eliminate the need for task-specific classification heads.

## Anti-patterns
- **Scaling without data**: A larger model on a low-quality dataset will amplify biases and produce worse results. Prioritize dataset curation before model scaling.
- **Ignoring evaluation at scale**: Evaluating a 100B-parameter model on downstream tasks requires massive compute. Budget evaluation resources alongside training.
- **Deploying raw large models**: A 100GB model cannot run on a single GPU. Use distillation, pruning, quantization, or hosted APIs.
- **Treating tables as plain text**: TAPAS works because it preserves table structure and learns aggregation operations. Don't flatten tables into text for QA.
- **Assuming vision transformers beat CNNs everywhere**: ViT needs large datasets to shine; on small datasets, ResNet often outperforms ViT. Match model capacity to data size.
- **Forgetting multimodal alignment**: Simply concatenating image and text features without joint pretraining yields poor results. Use contrastive or masked pretraining objectives.

## Code Examples
```python
# TAPAS table question answering
from transformers import pipeline
table_qa = pipeline("table-question-answering")
table = pd.DataFrame(book_data).astype(str)
queries = ["What's the topic in chapter 4?", "How many chapters have >20 pages?"]
preds = table_qa(table, queries)
# preds[0]["aggregator"] == "NONE", preds[1]["aggregator"] == "COUNT"

# CLIP zero-shot image classification
from transformers import CLIPProcessor, CLIPModel
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
texts = ["a photo of a transformer", "a photo of a robot", "a photo of agi"]
inputs = processor(text=texts, images=image, return_tensors="pt", padding=True)
outputs = model(**inputs)
probs = outputs.logits_per_image.softmax(dim=1)
```
- **What it demonstrates**: Querying structured data with natural language via TAPAS, and zero-shot image classification with CLIP.

## Worked Example
**Choosing a transformer for a new domain:**
- **Task**: Classify support tickets (text) and attach relevant screenshots (vision).
- **Text backbone**: Start with DistilBERT for latency. If accuracy is insufficient, upgrade to RoBERTa-base. Only consider larger models if compute budget allows.
- **Vision backbone**: If you have >100k labeled images, use ViT. Otherwise, use a pretrained ResNet or CLIP image encoder.
- **Multimodal fusion**: Use CLIP if you need zero-shot flexibility (define classes via text). Use LayoutLM if documents have rich layout (receipts, forms). Use cross-attention transformers (LXMERT) if you need deep interaction between modalities.
- **Long documents**: If tickets exceed 512 tokens, use Longformer with sliding local + global attention.

## Key Takeaways
1. Scaling laws predict that loss improves as power law of N, C, D. Scale all three together.
2. Larger models are more sample-efficient—they reach target performance with fewer training steps.
3. For sequences >2k tokens, switch from full attention to sparse (Longformer, BigBird) or linearized (Performer) attention.
4. TAPAS enables natural language querying of tables without writing SQL/Pandas.
5. wav2vec 2.0 achieves competitive ASR with only minutes of labeled data via self-supervised pretraining.
6. CLIP enables zero-shot image classification by aligning text and image embeddings via contrastive learning.
7. Most companies should use hosted APIs for large models instead of training from scratch.

## Connects To
- **Ch 3**: Efficient attention patterns (sparse, linearized) are modifications of the basic self-attention mechanism.
- **Ch 7**: RAG (retriever + generator) is the generative extension of the retriever-reader pattern.
- **Hugging Face Transformers**: ViT, TAPAS, wav2vec 2.0, and CLIP are all one-line pipeline instantiations in the library.
