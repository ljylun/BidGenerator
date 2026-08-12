# 07-RAG：让AI查资料再回答

## 开篇除恐

前面几章，我们的客服机器人有个大问题：**它只能回答通用问题**。

你问："你们的退货政策是什么？" 它可能回答："一般7天无理由退货。" 但实际上你们公司的政策是**15天无理由，且需要保留包装**。它不知道，因为它训练数据里没有这些信息。

怎么办？**教它翻书**。

这一章介绍的RAG（Retrieval-Augmented Generation，检索增强生成），就是让AI**先查资料，再回答问题**的技术。

**就这么简单。**

---

## 白话化：把术语扒光了看

### RAG

**大白话**：RAG就是**AI版的"开卷考试"**。

传统AI是闭卷考试：只靠训练时学过的知识答题。
RAG是开卷考试：允许AI考前翻书（查资料），然后结合书本内容答题。

**原书说明**：RAG结合了信息检索（retrieval）和文本生成（generation），让LLM能访问外部知识库。

### 检索器（Retriever）

**大白话**：Retriever就是AI的**图书管理员**。你问问题，它去图书馆帮你找最相关的几页书。

**原书说明**：Retriever从知识库中检索与用户查询最相关的文档片段。

### 生成器（Generator）

**大白话**：Generator就是AI的**答题者**。它拿到检索器找来的资料，结合问题，生成答案。

**原书说明**：Generator通常是LLM，它根据检索到的上下文生成回答。

### 向量数据库（Vector Database）

**大白话**：向量数据库就是**一本能按"意思"查的书**。

传统数据库按关键词匹配：你搜"苹果"，它找含"苹果"的文档。
向量数据库按语义相似度匹配：你搜"手机品牌"，它能找出含"苹果公司"的文档，即使没有"手机品牌"这四个字。

**原书说明**：向量数据库存储文本的embedding向量，支持高效的相似度搜索。

### Chunking（分块）

**大白话**：Chunking就是把大文档**切成小块**，方便AI消化。

你不可能把一整本《红楼梦》塞给AI，它记不住。你要把它切成：
- 第1-5回
- 第6-10回
- ...

每块大小适中，AI一次能处理。

**原书说明**：Chunking是将文档分割成适合LLM上下文窗口的片段的过程。

### Embedding

**大白话**：见第2章。在RAG中，我们把每个chunk转换成embedding向量，存入向量数据库。

### 相似度搜索

**大白话**：相似度搜索就是**找最像的**。用户问问题，把问题转成向量，然后在向量数据库里找最相似的chunk。

**原书说明**：常用相似度度量包括余弦相似度、欧氏距离、点积等。

---

## 直觉先行：用"查字典+写答案"理解RAG

想象你要回答一个问题："什么是光合作用？"

**没有RAG的AI**（闭卷考试）：
> 它靠训练记忆回答，可能记错、可能过时、可能瞎编。

**有RAG的AI**（开卷考试）：
> 1. **检索**：去图书馆（向量数据库）找"光合作用"相关的段落
> 2. **阅读**：找到3段最相关的教材内容
> 3. **答题**：结合这3段内容，组织语言回答你的问题
> 4. **引用**：告诉你答案来自哪几页

**核心优势**：
- 答案基于**真实资料**，不是AI"编"的
- 可以**引用来源**，用户可以验证
- 资料**实时更新**，不需要 retrain 模型

---

## 例子贴身

### ☼ 热身：最简单的RAG实现

**自编** 用Python实现一个迷你RAG系统：

```python
from openai import OpenAI
import numpy as np

client = OpenAI(api_key="YOUR_API_KEY")

# 1. 准备知识库（小公司客服FAQ）
knowledge_base = [
    "退货政策：15天无理由退货，需保留原包装和配件。",
    "运费：订单满99元免运费，不满99元收10元运费。",
    "VIP会员：享受9折优惠、优先发货、专属客服。",
    "发货时间：下单后24小时内发货，节假日顺延。"
]

# 2. 把知识库转成embedding
def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

# 预计算知识库embedding
kb_embeddings = [get_embedding(doc) for doc in knowledge_base]

# 3. 检索函数：找最相关的1个chunk
def retrieve(query, top_k=1):
    query_emb = get_embedding(query)
    
    # 计算余弦相似度
    similarities = []
    for kb_emb in kb_embeddings:
        sim = np.dot(query_emb, kb_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(kb_emb))
        similarities.append(sim)
    
    # 取最相关的top_k个
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    return [knowledge_base[i] for i in top_indices]

# 4. 生成答案
def rag_qa(question):
    # 检索相关文档
    relevant_docs = retrieve(question)
    context = "\n".join(relevant_docs)
    
    # 生成回答
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0.3,
        messages=[
            {"role": "system", "content": f"你是客服代表。根据以下资料回答用户问题，不要编造。\n\n资料：\n{context}"},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content

# 测试
print(rag_qa("退货需要什么条件？"))
print(rag_qa("VIP会员有什么好处？"))
```

**输出示例**：
> 退货需要什么条件？
> "根据我们的退货政策，您可以在15天内无理由退货，但需要保留原包装和配件。"

### ☼☼ 正经：给客服机器人接入企业知识库（贯穿例子·第7章）

**场景**：你的电商客服需要回答大量专业问题，如：
- 各种商品的详细参数
- 复杂的促销规则
- 物流合作方的具体信息
- 售后维修流程

**原书** 展示了RAG架构、chunking策略、向量数据库的选择。

**自编** 你搭建了一个完整的RAG系统：

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ 用户问题    │────▶│ 检索器       │────▶│ 向量数据库  │
│ "如何办理  │     │ (Embedding  │     │ (FAISS /    │
│  退换货？" │     │  + 相似度搜索)│     │  Pinecone)  │
└─────────────┘     └──────────────┘     └─────────────┘
                           │                     │
                           ▼                     │
                    ┌──────────────┐             │
                    │ 相关文档片段 │◀────────────┘
                    │ (Chunks)    │
                    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ 生成器       │
                    │ (LLM + 上下文)│
                    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ 最终回答     │
                    │ + 引用来源   │
                    └──────────────┘
```

**实现步骤**：

1. **文档准备**：收集公司内部文档（PDF、Word、Excel）
2. **Chunking**：用LangChain或LlamaIndex切分成512token的块
3. **Embedding**：用OpenAI text-embedding-3-small生成向量
4. **存入向量数据库**：用Pinecone或FAISS存储
5. **检索+生成**：用户提问时，先检索相关chunk，再让LLM生成答案

**效果**：

| 指标 | 无RAG | 有RAG |
|------|-------|-------|
| 答案准确率 | 62% | 94% |
| 幻觉率 | 28% | 3% |
| 用户满意度 | 3.1/5 | 4.6/5 |

**原书** 还提到了RAG的挑战：
- Chunking策略影响检索质量
- 向量数据库需要维护和更新
- 检索质量决定最终答案质量（garbage in, garbage out）

---

## 这一章要带走的东西

- RAG = 检索 + 生成，让AI"开卷考试"。
- Retriever是图书管理员，Generator是答题者。
- 向量数据库按语义搜索，不是关键词匹配。
- Chunking把大文档切成小块，方便AI消化。
- Embedding把文字变成向量，用于相似度计算。
- RAG的核心优势：答案基于真实资料、可引用来源、可实时更新。
- 我们的客服机器人接入了企业知识库，准确率大幅提升。

**就这样。**
