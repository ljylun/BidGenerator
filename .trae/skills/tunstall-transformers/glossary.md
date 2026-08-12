# Glossary

**Attention Head** — A single scaled dot-product attention unit with its own Q/K/V projections. Multiple heads compose multi-head attention. (Ch 3)

**Backpropagation** — The algorithm for computing gradients in neural networks by applying the chain rule layer-by-layer from output to input. (Ch 3)

**BM25** — A sparse retrieval algorithm that improves on TF-IDF by saturating term frequency and normalizing for document length. Default retriever in Haystack's ElasticsearchRetriever. (Ch 7)

**BPE (Byte-Pair Encoding)** — A subword tokenization algorithm that iteratively merges the most frequent character pairs. Used by GPT-2 and many transformer models. (Ch 3, implied)

**CLS Token** — A special `[CLS]` token prepended to BERT inputs; its final hidden state is used for classification tasks. (Ch 3, Ch 7)

**Contrastive Learning** — A pretraining objective that trains a model to maximize similarity of matched pairs (image-caption) while minimizing similarity of mismatched pairs. Used by CLIP. (Ch 11)

**Cross-Entropy Loss** — The standard loss function for language modeling and classification; measures the difference between predicted probability distributions and true labels. (Ch 11)

**Dense Passage Retrieval (DPR)** — A bi-encoder architecture using two BERT models (question encoder + passage encoder) to create dense embeddings for retrieval. (Ch 7)

**Domain Adaptation** — Fine-tuning a pretrained model on target-domain data to improve performance when the domain differs from the pretraining corpus. (Ch 7)

**EM (Exact Match)** — A binary QA metric: EM = 1 if the predicted answer matches the ground truth exactly after normalization, else 0. (Ch 7)

**Encoder-Decoder Attention** — Attention layer in the decoder where queries come from the decoder and keys/values come from the encoder. Allows the decoder to "look at" the input sequence. (Ch 3)

**F1-score** — Harmonic mean of precision and recall for QA; more lenient than EM because it rewards partial token overlap. (Ch 7)

**FAISS** — Facebook AI Similarity Search library for efficient similarity search and clustering of dense vectors. Used to speed up DPR retrieval. (Ch 7)

**Feed-Forward Layer** — A position-wise two-layer neural network (linear → GELU → linear → dropout) applied independently to each token position in transformer layers. (Ch 3)

**GELU (Gaussian Error Linear Unit)** — Activation function `x * Φ(x)` where Φ is the standard normal CDF. Commonly used in transformer feed-forward layers (BERT, GPT-2). (Ch 3)

**GPT (Generative Pretrained Transformer)** — Decoder-only transformer pretrained on autoregressive language modeling. Good for text generation. (Ch 3)

**Haystack** — An open-source NLP framework by deepset for building QA and search systems with retrievers, readers, and pipelines. (Ch 7)

**Hidden State** — The sequence of embedding vectors output by a transformer layer; also called "context" or "encoder output." (Ch 3)

**iGPT** — Applies GPT-style autoregressive pretraining to image pixels for image generation and classification. (Ch 11)

**Knowledge Distillation** — Technique to compress a large teacher model into a smaller student model by training the student to match the teacher's soft predictions. Used in DistilBERT. (Ch 3)

**Layer Normalization** — Normalizes activations across the feature dimension. In transformers, applied before attention and feed-forward sublayers (Pre-LN) or after (Post-LN). (Ch 3)

**Linearized Attention** — Reformulates attention as a kernel function to reduce complexity from O(n²) to O(n). Implemented in Linear Transformer and Performer. (Ch 11)

**Longformer** — Transformer with sparse attention combining global tokens, local band attention, and dilated windows. Supports 4,096 tokens. (Ch 11)

**Masked Language Modeling (MLM)** — Pretraining objective where random tokens are masked and the model predicts them. Used by BERT. (Ch 3)

**mAP (mean Average Precision)** — Retrieval metric that rewards correct documents appearing higher in the ranked list. (Ch 7)

**MiniLM** — Distilled version of BERT-base that preserves 99% performance while being 2× faster (66M parameters). Good baseline for QA. (Ch 7)

**Multimodal Transformer** — A transformer that processes multiple modalities (text + image, text + audio, text + table) in a single architecture. (Ch 11)

**Next Sentence Prediction (NSP)** — BERT pretraining task: predict whether two sentences follow each other in a document. (Ch 3)

**Performer** — Transformer with linearized attention using orthogonal random features. Reduces memory and compute to O(n). (Ch 11)

**Position Embeddings** — Vectors added to token embeddings to encode token position. Variants: learnable (BERT), relative (T5), rotary (GPT-Neo). (Ch 3)

**RAG (Retrieval-Augmented Generation)** — Combines a dense retriever (DPR) with a seq2seq generator (BART) to produce parametric and non-parametric memory. (Ch 7)

**Recall@k** — Fraction of questions where the ground-truth answer appears in the top-k retrieved documents. (Ch 7)

**Retriever-Reader Architecture** — Two-stage QA: retriever fetches candidate documents, reader extracts answer spans. The retriever sets the system's performance ceiling. (Ch 7)

**RoBERTa** — Robustly optimized BERT pretraining: longer training, larger batches, more data, no NSP task. (Ch 3)

**Rotary Position Embeddings (RoPE)** — Position encoding that rotates query/key vectors by position-dependent angles. Used in GPT-Neo. (Ch 3)

**Scaling Laws** — Empirical power-law relationships: loss L ∝ N^(-α_N) ∝ C^(-α_C) ∝ D^(-α_D) for autoregressive models. (Ch 11)

**SEP Token** — Special `[SEP]` token used in BERT to separate segments (e.g., question and context in QA). (Ch 3, Ch 7)

**SQuAD** — Stanford Question Answering Dataset: 100k+ Wikipedia paragraphs with crowd-sourced questions/answers. Benchmark for extractive QA. (Ch 7)

**SubjQA** — Dataset of 10k+ customer reviews with subjective questions/answers across 6 domains. Used for benchmarking review-based QA. (Ch 7)

**TAPAS** — Table Parser: transformer that flattens table cells as tokens and learns aggregation operations (SUM, AVERAGE, COUNT) for table QA. (Ch 11)

**Token Type IDs** — Segment embeddings in BERT indicating whether a token belongs to segment A (0) or segment B (1). Used in QA to distinguish question from context. (Ch 7)

**Transformer Encoder** — Stack of encoder layers that converts input tokens into contextualized hidden states. Used in BERT, RoBERTa, DistilBERT. (Ch 3)

**Transformer Decoder** — Stack of decoder layers with masked self-attention and encoder-decoder attention. Used in GPT family for autoregressive generation. (Ch 3)

**ViT (Vision Transformer)** — Splits images into fixed-size patches, embeds them, and processes with a standard transformer encoder. Scales better than CNNs on large image datasets. (Ch 11)

**wav2vec 2.0** — Self-supervised speech representation model combining CNN feature extractor with transformer layers. Pretrained on 960 hours of unlabeled audio for ASR. (Ch 11)

**Zero-shot Classification** — Classifying inputs without task-specific fine-tuning by comparing input embeddings to class name embeddings. CLIP enables zero-shot image classification. (Ch 11)
