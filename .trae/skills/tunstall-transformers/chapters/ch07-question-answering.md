# Chapter 7: Question Answering

## Core Idea
Modern QA systems use a retriever-reader architecture: a retriever fetches relevant documents from a corpus, and a reader extracts answer spans from those documents. The chapter shows how to build, evaluate, and improve such a system using Haystack and Hugging Face transformers, with practical techniques for domain adaptation when pretrained models fail on specialized data.

## Frameworks Introduced
- **Retriever-Reader Architecture**: Split QA into two stages—retrieve relevant documents, then extract answers. Use when building production QA over large corpora; the retriever sets the upper bound on system performance.
- **Span Classification**: Frame answer extraction as predicting start and end token indices. Use for extractive QA where answers are contiguous text spans.
- **Dense Passage Retrieval (DPR)**: Use two BERT encoders (one for questions, one for passages) to create dense embeddings, then retrieve via nearest-neighbor search. Use when BM25 struggles with vocabulary mismatch or semantic nuance.
- **RAG (Retrieval-Augmented Generation)**: Combine a retriever (DPR) with a generator (BART) to produce free-form answers instead of extracting spans. Use when answers need to be synthesized from multiple documents or rephrased.
- **Domain Adaptation for QA**: Fine-tune a SQuAD-pretrained reader on target-domain data. Use when your domain (reviews, legal, medical) differs significantly from Wikipedia and EM/F1 drop by 50%+.
- **Haystack Pipeline Abstraction**: Combine retrievers, readers, and document stores into graph-based query flows. Use for rapid prototyping and custom evaluation flows.

## Key Concepts
- **Closed-domain vs Open-domain QA**: Closed-domain restricts search to a narrow topic (single product); open-domain searches a broad corpus (all products).
- **Sparse vs Dense Retrievers**: Sparse (BM25, TF-IDF) uses term frequencies; dense (DPR, embeddings) uses contextualized vectors. Sparse is fast and interpretable; dense handles synonyms and paraphrases better.
- **Exact Match (EM)**: Strict metric—prediction must match ground truth character-for-character after normalization. Use as the primary quality gate.
- **F1-score**: Harmonic mean of precision and recall at token level. Use alongside EM because EM is overly strict (one extra token drops score to zero).
- **Recall@k**: Fraction of questions where the correct answer appears in the top-k retrieved documents. Use to measure retriever coverage.
- **Mean Average Precision (mAP)**: Rewards retrievers that rank correct answers higher. Use when answer ranking matters, not just recall.
- **Sliding Window**: Split long contexts into overlapping chunks (controlled by `max_seq_length` and `doc_stride`). Use when documents exceed the model's context window.
- **SubjQA Dataset**: 10,000+ customer reviews with subjective questions/answers across 6 domains. Use for benchmarking review-based QA.

## Mental Models
- **Retriever sets the ceiling**: Even a perfect reader cannot extract answers the retriever failed to fetch. Evaluate and optimize the retriever first.
- **Start with SQuAD pretraining, then adapt**: Fine-tuning on SQuAD gives strong reading comprehension; further fine-tuning on domain data adapts the language. Two-stage fine-tuning beats single-stage on small datasets.
- **Small data ≠ naive fine-tuning**: With only 1,295 training examples (SubjQA), naive fine-tuning from scratch overfits. Start from SQuAD pretraining, then do a second fine-tuning step.
- **Filter aggressively in production**: Always filter retrievers by product ID or category; without filtering, queries return irrelevant documents and latency balloons.

## Anti-patterns
- **Concatenating all reviews into one giant context**: This creates unacceptable latency (~3 seconds per query). Use a retriever to select only relevant passages.
- **Truncating long contexts**: Unlike text classification, QA cannot simply truncate—the answer may be at the end. Use sliding windows instead.
- **Comparing answer scores across passages**: The Transformers QA pipeline normalizes start/end logits with softmax per passage, so a 0.9 score in passage A is not comparable to 0.8 in passage B. Use FARMReader if cross-passage comparison is needed.
- **Ignoring unanswerable questions**: SQuAD 2.0 and SubjQA contain unanswerable questions. Models that always predict an answer will learn to hallucinate. Always set `return_no_answer=True`.
- **Evaluating reader in isolation**: SQuAD-style evaluation feeds ground-truth context to the reader. In production, the retriever may miss the context. Evaluate the full pipeline, not just components.

## Code Examples
```python
# Retriever-Reader pipeline with Haystack
from haystack.pipeline import ExtractiveQAPipeline
pipe = ExtractiveQAPipeline(reader, es_retriever)
preds = pipe.run(query=query, top_k_retriever=3, top_k_reader=4,
                 filters={"item_id": [item_id], "split": ["train"]})

# DPR retriever initialization
from haystack.retriever.dense import DensePassageRetriever
dpr_retriever = DensePassageRetriever(
    document_store=document_store,
    query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
    passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base",
    embed_title=False
)

# Domain adaptation: convert to SQuAD format and fine-tune
reader.train(data_dir=".", use_gpu=True, n_epochs=1, batch_size=16,
             train_filename="electronics-train.json",
             dev_filename="electronics-validation.json")
```
- **What it demonstrates**: Building an end-to-end QA pipeline, initializing a dense retriever, and fine-tuning a reader on domain data.

## Worked Example
**Building a review-based QA system for Amazon electronics:**
1. **Dataset**: Load SubjQA electronics subset (1,295 train, 358 test questions).
2. **Baseline**: Use MiniLM fine-tuned on SQuAD 2.0 via FARMReader. Result: EM=0.06, F1=0.20 on SubjQA.
3. **Retriever**: Initialize Elasticsearch document store with product reviews. Evaluate BM25 (Recall@3=0.95) vs DPR (no improvement over BM25 on this small dataset).
4. **Reader evaluation**: Learn that EM is strict (one extra token = 0) while F1 is lenient ("6000 dollars" gets F1=0.4). Always track both.
5. **Domain adaptation**: Fine-tune MiniLM on SubjQA training data (converted to SQuAD JSON format). Result: EM increases by 6×, F1 more than doubles.
6. **Lesson**: Two-stage fine-tuning (SQuAD → domain) beats single-stage (domain only) because the model retains general reading comprehension while adapting to domain language.

## Key Takeaways
1. Always filter retrievers by product/category ID in production to avoid irrelevant results and high latency.
2. Use sliding windows (`return_overflowing_tokens=True`, `stride=128`) for long documents—never truncate.
3. Track both EM and F1; EM catches hallucinations, F1 catches partial matches.
4. Start with SQuAD-pretrained models, then fine-tune on domain data. Two-stage training beats one-stage on small datasets.
5. Evaluate the full retriever-reader pipeline, not just the reader in isolation.
6. DPR requires domain fine-tuning to beat BM25; without it, BM25 is often sufficient and faster.

## Connects To
- **Ch 3**: QA readers are typically BERT-like encoders fine-tuned with a span classification head.
- **Ch 11**: RAG and generative QA represent the future of QA beyond extractive methods.
- **Hugging Face Hub**: Use `deepset/minilm-uncased-squad2` as a strong, fast baseline for extractive QA.
