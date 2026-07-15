---
AIGC:
    Label: "1"
    ContentProducer: 001191110102MACQD9K64018705
    ProduceID: 7626417217399357722-data_volume/files/所有对话/主对话/项目规划/林润鲜境_企业AI系统_技术落地方案_v3.md
    ReservedCode1: ""
    ContentPropagator: 001191110102MACQD9K64028705
    PropagateID: 3440784236359376#1783586552040
    ReservedCode2: ""
---
# 林润鲜境 - 企业AI系统技术落地方案 v3.0

> **版本**：v3.0（技术落地版）
> **日期**：2026-07-10
> **输入依据**：需求调研文档v2.0 + 架构设计文档v1.0
> **适用范围**：林润鲜境全公司（20-50人），以抖音生鲜电商为核心业务
> **核心定位**：不是"各部门各自用AI"，而是**跨部门实时协作的AI中枢**

---

## 一、项目概述

### 1.1 项目目标

| 目标 | 量化指标 | 达成时间 |
|------|---------|---------|
| 老板决策效率提升 | 每天节省1-2h数据汇总时间 | 第4周 |
| 客服人效提升 | 减少80%重复性问答 | 第4周 |
| 投放异常响应 | 从"事后发现"到"分钟级预警" | 第4周 |
| 跨部门协作提速 | 选品定价从1-2天→1小时 | 第8周 |
| 断货损失降低 | 库存预警准确率≥90% | 第8周 |
| 财务对账提效 | 月结对账从数天→数小时 | 第8周 |

### 1.2 项目范围

**覆盖部门**：总经办、人力资源部、财务部、采购部、仓配部、客服部、业务部（直播组/货架组/商务组/渠道组/私域组）

**功能范围**：20个AI应用场景（P0×6 + P1×8 + P2×6），2大核心协作流程，3大财务预警体系

**不在范围**：不涉及现有ERP/WMS系统替换，不涉及生产端（产地）数字化改造

### 1.3 核心原则

| 原则 | 说明 |
|------|------|
| **够用就好** | 不搞重型架构，PostgreSQL+ChromaDB够用，不上Kafka/ES |
| **全部开源** | Ollama+Dify+PostgreSQL+ChromaDB+One API，软件零成本 |
| **先跑通再买** | 先现有电脑部署验证→确认效果→再采购Mac Mini独立主机 |
| **数据本地** | 所有数据本地部署，不依赖云端API，数据安全可控 |
| **飞书为枢纽** | 飞书作为主要通知和协作渠道，不额外开发独立APP |
| **API优先** | 已有抖店430个API文档+千川OAuth，优先自动拉取数据 |

---

## 二、技术架构设计

基于v1架构文档的5层架构（L0-L4 + 治理层），逐层细化技术方案。

### 2.1 L0 基础设施层

#### 2.1.1 硬件配置方案

| 方案 | 硬件 | 算力 | 可跑模型 | 适用阶段 | 成本 |
|------|------|------|---------|---------|------|
| **过渡方案** | 现有办公电脑 | CPU/8-16GB内存 | qwen2.5-7B-Q4（CPU推理，慢） | 第1-2周验证 | 0元 |
| **推荐方案** | Mac Mini M4 24GB | 10核GPU/24GB统一内存 | qwen2.5-14B-Q4、deepseek-coder-6.7B | 日常运行 | ~5,500元 |
| **进阶方案** | Mac Mini M4 48GB | 10核GPU/48GB统一内存 | qwen2.5-32B-Q4、多模型并行 | 并发增加 | ~11,000元 |
| **旗舰方案** | Mac Mini M4 Pro 64GB | 14核GPU/64GB统一内存 | qwen2.5-72B-Q4、全模型并行 | 全功能运行 | ~18,000元 |

**推荐采购路径**：
- 第1阶段：用现有电脑部署验证（0元）
- 第2阶段：购买 Mac Mini M4 24GB（~5,500元），独立部署
- 第3阶段（按需）：升级至 M4 48GB 或追加一台 M4 Pro 64GB

#### 2.1.2 网络方案

```
公司局域网
├── Mac Mini（AI服务器）── 固定IP 192.168.1.100
│   ├── Dify Web UI ──── http://192.168.1.100:3000
│   ├── Ollama API ──── http://192.168.1.100:11434
│   ├── One API ─────── http://192.168.1.100:3001
│   └── PostgreSQL ──── 192.168.1.100:5432
│
├── 办公区终端 ──── 192.168.1.x（通过局域网访问）
└── 飞书机器人 ──── Webhook回调（需内网穿透或公网IP）

网络安全：
├── Mac Mini 仅限局域网访问，不暴露公网（除飞书Webhook）
├── PostgreSQL 仅内网访问
├── 飞书Webhook通过Nginx反向代理+IP白名单保护
└── 定期备份数据到外接硬盘
```

#### 2.1.3 存储方案

| 存储内容 | 存储位置 | 预估容量 |
|---------|---------|---------|
| 操作系统+软件 | Mac Mini SSD | ~50GB |
| PostgreSQL数据库 | Mac Mini SSD | ~20GB/年 |
| 向量数据库 | Mac Mini SSD | ~10GB/年 |
| 知识库源文件 | Mac Mini SSD | ~5GB |
| 数据备份 | 外接USB硬盘（2TB） | 滚动保留30天 |

### 2.2 L1 数据层

#### 2.2.1 PostgreSQL 数据库设计

**Schema隔离方案**（对应v1架构中的部门隔离）：

```sql
-- 公共Schema
CREATE SCHEMA public;          -- 用户/权限/系统配置
CREATE SCHEMA shared_data;     -- 跨部门共享数据（商品/订单/库存汇总）

-- 部门Schema（按v2需求文档中的部门划分）
CREATE SCHEMA workspace_boss;        -- 总经办：经营简报、预警记录、决策日志
CREATE SCHEMA workspace_hr;          -- 人力资源：薪酬、考勤、人效
CREATE SCHEMA workspace_finance;     -- 财务：对账、盈亏、税务、合规
CREATE SCHEMA workspace_procurement; -- 采购：供应商、行情、采购单
CREATE SCHEMA workspace_warehouse;   -- 仓配：库存、发货、损耗、品控
CREATE SCHEMA workspace_cs;          -- 客服：工单、差评、赔付、话术
CREATE SCHEMA workspace_ops;         -- 业务-直播：直播数据、投放、排品
CREATE SCHEMA workspace_shelf;       -- 业务-货架：店铺运营、商品管理
CREATE SCHEMA workspace_biz_dev;     -- 业务-商务：达人管理、佣金
CREATE SCHEMA workspace_channel;     -- 业务-渠道：线下渠道数据
CREATE SCHEMA workspace_private;     -- 业务-私域：社群、复购

-- 权限控制：老板workspace可只读访问所有schema
```

**核心表结构大纲**（按业务模块）：

```sql
-- ============ public: 用户与权限 ============
CREATE TABLE public.users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    department VARCHAR(50),       -- 部门编码
    role VARCHAR(20),             -- boss/manager/staff
    feishu_id VARCHAR(50),        -- 飞书用户ID
    api_key VARCHAR(64),          -- 个人API Key
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE public.agent_access_log (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES public.users(id),
    agent_name VARCHAR(50),
    action VARCHAR(50),           -- query/create/export
    input_summary TEXT,           -- 输入摘要（脱敏）
    output_summary TEXT,          -- 输出摘要
    token_used INT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============ shared_data: 跨部门共享数据 ============
CREATE TABLE shared_data.products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    category VARCHAR(50),         -- 品类
    supplier_id INT,              -- 供应商
    purchase_price DECIMAL(10,2), -- 采购价
    selling_price DECIMAL(10,2),  -- 售价
    cost_logistics DECIMAL(10,2), -- 物流成本
    cost_packaging DECIMAL(10,2), -- 包材成本
    status VARCHAR(20),           -- active/inactive
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE shared_data.orders_daily (
    id SERIAL PRIMARY KEY,
    date DATE,
    channel VARCHAR(20),          -- douyin/pinduoduo/taobao/offline
    product_id INT REFERENCES shared_data.products(id),
    order_count INT,
    gmv DECIMAL(12,2),
    refund_amount DECIMAL(12,2),
    refund_rate DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE shared_data.inventory (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES shared_data.products(id),
    quantity INT,
    safety_stock INT,             -- 动态安全库存（AI计算）
    warehouse_location VARCHAR(50),
    last_inbound_date DATE,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE shared_data.suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    contact VARCHAR(50),
    category VARCHAR(50),
    rating DECIMAL(3,2),          -- 综合评分
    delivery_rate DECIMAL(5,4),   -- 交期达成率
    quality_rate DECIMAL(5,4),    -- 品质合格率
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============ workspace_finance: 财务 ============
CREATE TABLE workspace_finance.profit_daily (
    id SERIAL PRIMARY KEY,
    date DATE,
    channel VARCHAR(20),
    gmv DECIMAL(12,2),
    cost_purchase DECIMAL(12,2),  -- 采购成本
    cost_logistics DECIMAL(12,2), -- 物流成本
    cost_packaging DECIMAL(12,2), -- 包材成本
    cost_ads DECIMAL(12,2),       -- 投流成本
    cost_commission DECIMAL(12,2),-- 平台佣金
    cost_refund DECIMAL(12,2),    -- 售后赔付
    profit DECIMAL(12,2),         -- 净利润
    profit_rate DECIMAL(5,4),     -- 利润率
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE workspace_finance.alert_records (
    id SERIAL PRIMARY KEY,
    alert_type VARCHAR(50),       -- cost/roi/compliance
    severity VARCHAR(20),         -- critical/warning/info
    title VARCHAR(200),
    detail JSONB,                 -- 告警详情
    status VARCHAR(20),           -- open/acknowledged/resolved
    notified_to VARCHAR(200),     -- 通知对象
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============ workspace_ops: 直播投放 ============
CREATE TABLE workspace_ops.ad_plans (
    id SERIAL PRIMARY KEY,
    plan_id VARCHAR(100),         -- 千川计划ID
    product_id INT,
    date DATE,
    cost DECIMAL(12,2),           -- 消耗
    gmv DECIMAL(12,2),
    roi DECIMAL(5,2),
    impressions INT,
    clicks INT,
    conversions INT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE workspace_ops.live_sessions (
    id SERIAL PRIMARY KEY,
    date DATE,
    duration_minutes INT,
    gmv DECIMAL(12,2),
    viewers INT,
    avg_online INT,
    conversion_rate DECIMAL(5,4),
    refund_rate DECIMAL(5,4),
    ad_cost DECIMAL(12,2),
    roi DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============ workspace_cs: 客服 ============
CREATE TABLE workspace_cs.complaints (
    id SERIAL PRIMARY KEY,
    date DATE,
    product_id INT,
    channel VARCHAR(20),
    complaint_type VARCHAR(50),   -- quality/logistics/description/other
    refund_amount DECIMAL(10,2),
    ai_attribution VARCHAR(100),  -- AI归因：采购/仓配/运营
    resolved BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============ workspace_procurement: 采购 ============
CREATE TABLE workspace_procurement.market_prices (
    id SERIAL PRIMARY KEY,
    date DATE,
    category VARCHAR(50),
    origin VARCHAR(50),           -- 产地
    price_low DECIMAL(10,2),
    price_high DECIMAL(10,2),
    price_avg DECIMAL(10,2),
    supply_status VARCHAR(20),    -- sufficient/tight/shortage
    source VARCHAR(100),          -- 数据来源
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============ workspace_warehouse: 仓配 ============
CREATE TABLE workspace_warehouse.shipping_daily (
    id SERIAL PRIMARY KEY,
    date DATE,
    total_orders INT,
    shipped INT,
    pending INT,
    exception_count INT,
    avg_delivery_hours DECIMAL(5,2),
    damage_rate DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============ workspace_boss: 老板全局 ============
CREATE TABLE workspace_boss.daily_briefing (
    id SERIAL PRIMARY KEY,
    date DATE,
    gmv_total DECIMAL(12,2),
    profit_total DECIMAL(12,2),
    order_count INT,
    avg_roi DECIMAL(5,2),
    refund_rate DECIMAL(5,4),
    stock_alert_count INT,
    compliance_alert_count INT,
    briefing_content TEXT,        -- AI生成的简报内容
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 2.2.2 向量数据库选型（ChromaDB）

| 配置项 | 值 |
|--------|-----|
| 部署方式 | Docker容器，与PostgreSQL同一台机器 |
| 端口 | 8000 |
| 存储后端 | 本地持久化（SQLite + 文件） |
| Embedding模型 | bge-m3（Ollama本地部署，中文效果好） |
| 向量维度 | 1024 |
| 数据组织 | 按部门分Collection |

**向量数据库Collection规划**：

```
chromadb_collections:
├── kb_sop              # 全公司SOP文档（公共知识库）
├── kb_product          # 产品手册、FAQ
├── kb_platform_rules   # 抖店/拼多多平台规则
├── kb_cs_scripts       # 客服话术库
├── kb_training         # 培训资料（新人入职/技能培训）
├── kb_finance_policy   # 财务制度、税务政策
├── kb_market           # 市场行情分析报告
└── kb_history_chat     # 历史高质量对话（用于few-shot）
```

#### 2.2.3 共享数据层设计

```
共享数据层架构：

┌─────────────────────────────────────────────┐
│           shared_data (PostgreSQL Schema)     │
├─────────────────────────────────────────────┤
│                                             │
│  商品主数据 (products)                       │
│  ├── 采购写入：采购价、供应商                 │
│  ├── 业务写入：售价、渠道信息                 │
│  ├── 仓配写入：库存量、库位                   │
│  ├── 客服写入：售后率、投诉分类               │
│  └── 财务写入：成本明细、利润                 │
│                                             │
│  订单汇总 (orders_daily)                     │
│  ├── API自动写入：各渠道订单/GMV/退货         │
│  └── 各部门Agent只读查询                     │
│                                             │
│  事件总线表 (event_bus)                      │
│  ├── 事件产生者写入                          │
│  ├── 事件消费者读取+确认                     │
│  └── 过期事件自动清理（保留7天）              │
│                                             │
└─────────────────────────────────────────────┘

数据访问控制（通过PostgreSQL RLS实现）：
├── 采购部 → 读写 products/procurement，只读 orders_daily
├── 业务部 → 读写 orders_daily（本渠道），只读 products
├── 仓配部 → 读写 inventory/shipping，只读 orders_daily
├── 客服部 → 读写 complaints，只读 products/orders_daily
├── 财务部 → 读写 finance，只读全公司数据
└── 老板   → 只读所有schema
```

### 2.3 L2 平台层

#### 2.3.1 Ollama 模型服务

| 模型 | 用途 | 参数规模 | 显存需求 | 部署优先级 |
|------|------|---------|---------|-----------|
| qwen2.5:14b (Q4) | 通用对话、数据分析、报告生成 | 14B | ~9GB | P0 |
| deepseek-coder-v2:lite | 代码辅助、数据处理脚本 | 16B | ~10GB | P1 |
| bge-m3 | 文本Embedding（知识库向量化） | 0.5B | ~1GB | P0 |
| qwen2.5:7b (Q4) | 轻量级任务（分类、提取、简单问答） | 7B | ~5GB | P0 |
| qwen2.5:32b (Q4) | 复杂推理（仅48GB+机型） | 32B | ~20GB | P2 |

**模型加载策略**（适配24GB Mac Mini）：
```
常驻内存：qwen2.5:14b + bge-m3（~10GB）
按需加载：qwen2.5:7b（简单任务时切换，~5GB）
Ollama配置：OLLAMA_MAX_LOADED_MODELS=2
```

#### 2.3.2 Dify 平台配置

**工作空间划分**（对应v1架构）：

| 工作空间 | 成员 | 可用Agent | 可用知识库 |
|---------|------|----------|-----------|
| 总经办 | 伟壕 | 老板全局Agent | 全部只读 |
| 人力资源部 | HR负责人+专员 | 薪酬核算Agent、培训问答Agent、人力看板Agent | kb_training, kb_sop |
| 财务部 | 财务负责人 | 对账Agent、盈亏看板Agent、合规预警Agent | kb_finance_policy |
| 采购部 | 采购负责人 | 库存预警Agent、供应商管理Agent、行情追踪Agent | kb_market |
| 仓配部 | 仓配负责人 | 发货看板Agent、库存可视化Agent、损耗分析Agent | kb_sop |
| 客服部 | 客服负责人+组员 | 自动回复Agent、差评预警Agent、归因分析Agent | kb_cs_scripts, kb_product, kb_platform_rules |
| 业务-直播 | 直播团队 | 直播复盘Agent、ROI看板Agent、话术生成Agent | kb_product, kb_market |
| 业务-货架 | 货架运营 | 商品优化Agent、店铺数据Agent | kb_product, kb_platform_rules |
| 业务-商务 | 商务团队 | 达人筛选Agent、效果追踪Agent | kb_market |
| 业务-渠道 | 渠道团队 | 渠道数据Agent、订单管理Agent | kb_product |
| 业务-私域 | 私域团队 | 文案生成Agent、客户标签Agent | kb_product, kb_cs_scripts |

**Dify核心配置**：
```yaml
# docker-compose中的Dify环境变量
SECRET_KEY: <随机生成>
DB_HOST: postgresql
DB_PORT: 5432
DB_USERNAME: dify
DB_PASSWORD: <强密码>
REDIS_HOST: redis
FILE_MAX_SIZE: 50MB          # 单文件上传限制
PLUGIN_MAX_PACKAGE_SIZE: 50MB
```

#### 2.3.3 One API 网关

```
One API 配置：
├── 后端模型：Ollama本地模型（统一接入）
├── 渠道管理：
│   ├── Channel 1: Ollama本地 → qwen2.5:14b, qwen2.5:7b, bge-m3
│   ├── Channel 2: (可选) 通义千问API → 备用/高峰期分流
│   └── Channel 3: (可选) DeepSeek API → 代码任务
├── 令牌管理：
│   ├── 每个部门分配独立Token
│   ├── Token限额：按部门设定月度Token上限
│   └── Token监控：超额自动降级到小模型
└── 日志审计：所有API调用记录保存30天
```

### 2.4 L3 应用层：各部门Agent清单

按v2需求文档中的P0/P1/P2整理，共20个Agent场景：

#### P0 - 第1-4周上线（6个核心Agent）

| 序号 | Agent名称 | 归属部门 | 核心能力 | 数据依赖 | 技术实现 |
|------|----------|---------|---------|---------|---------|
| A1 | 老板全局Agent | 总经办 | 经营简报推送、自然语言查数据、异常预警 | 全公司数据 | Dify Workflow + 定时触发 + 飞书Webhook |
| A2 | 直播复盘Agent | 业务-直播 | 每场直播数据自动汇总、生成复盘报告 | 抖店直播API + 千川API | Dify Workflow + API数据拉取 |
| A3 | 千川ROI看板Agent | 业务-直播 | ROI实时监控、消耗异常预警、素材效果分析 | 千川API | Dify Workflow + 规则引擎 + 飞书告警 |
| A4 | 客服自动回复Agent | 客服部 | 常见问题自动回复、差评实时预警 | 知识库(RAG) + 抖店消息API | Dify Chatflow + RAG |
| A5 | 库存预警Agent | 采购+仓配 | 断货预警、安全库存计算、补货建议 | 库存数据 + 销量数据 | Dify Workflow + 定时检测 |
| A6 | 薪酬核算Agent | 人力+财务 | 底薪+绩效+提成+主播分成自动计算 | HR薪酬数据 | Dify Workflow + PostgreSQL |

#### P1 - 第5-8周扩展（8个重要Agent）

| 序号 | Agent名称 | 归属部门 | 核心能力 |
|------|----------|---------|---------|
| A7 | 财务对账Agent | 财务部 | 平台结算 vs 订单 vs 银行流水三方核对 |
| A8 | 实时盈亏Agent | 财务部 | 日/周/月盈亏实时更新，老板随时查 |
| A9 | 直播话术Agent | 业务-直播 | 基于产品+客群+热点生成话术/脚本 |
| A10 | 达人筛选Agent | 业务-商务 | 粉丝画像/ROI/品类匹配度分析 |
| A11 | 供应商管理Agent | 采购部 | 供应商评级、交期跟踪、比价分析 |
| A12 | 商品优化Agent | 业务-货架 | 标题/详情页AI优化、竞品价格监控 |
| A13 | 私域文案Agent | 业务-私域 | 朋友圈/社群营销文案批量生成 |
| A14 | 培训问答Agent | 人力+客服 | 新人入职/制度/SOP一问就答 |

#### P2 - 第9-12周深化（6个进阶Agent）

| 序号 | Agent名称 | 归属部门 | 核心能力 |
|------|----------|---------|---------|
| A15 | 销量预测Agent | 采购+业务 | 基于历史+季节+市场预测需求量 |
| A16 | 竞品监控Agent | 业务-直播 | 竞品直播间/价格/评价变化追踪 |
| A17 | 财务风险雷达Agent | 财务部 | 资金链/应收/税务综合风险评估 |
| A18 | 离职预警Agent | 人力部 | 基于出勤/绩效/沟通信号预测 |
| A19 | 选品定价Agent | 跨部门 | 选品定价建议书自动生成 |
| A20 | 采销配协同Agent | 跨部门 | 实时联动事件分发与通知 |

### 2.5 L4 决策+治理层

#### 2.5.1 老板全局Agent设计

```
老板全局Agent 架构：

输入渠道：
├── 飞书私聊 → 自然语言查询（"这周利润多少"）
├── 定时推送 → 每日经营简报（飞书群，早9:00）
└── Web Dashboard → 全局数据看板（Dify内置或简易前端）

核心能力：
├── 经营简报生成
│   ├── 每日自动从 shared_data 拉取前一日数据
│   ├── AI生成简报文本（包含：GMV/利润/退货率/库存/投放ROI）
│   ├── 异常项标红提醒
│   └── 通过飞书Webhook推送到老板专属群
│
├── 自然语言查询
│   ├── "这周利润多少" → SQL查询 → 格式化输出
│   ├── "哪个渠道ROI最高" → 多表JOIN → 排序输出
│   ├── "蜂糖李还能卖几天" → 库存/日均销量 → 天数计算
│   └── Text-to-SQL（基于PostgreSQL，qwen2.5:14b驱动）
│
├── 异常预警（被动接收各部门Agent告警）
│   ├── ROI暴跌 → 千川Agent上报
│   ├── 库存断货 → 库存预警Agent上报
│   ├── 合规风险 → 财务合规Agent上报
│   └── 统一汇总 → 飞书消息 + Dashboard标记
│
└── 决策辅助
    ├── "要不要开新渠道" → 拉取现有渠道ROI → 对比分析 → 给出建议
    └── "这个品要不要加大投入" → 利润/库存/趋势综合分析
```

#### 2.5.2 权限体系（RBAC三级）

| 角色 | 数据范围 | Agent范围 | 管理权限 |
|------|---------|----------|---------|
| **老板**（伟壕） | 全公司所有数据（只读） | 所有Agent | 全部配置 |
| **部门负责人** | 本部门全部 + 共享数据（读写） + 其他部门（只读摘要） | 本部门Agent + 公共Agent | 本部门Agent配置 |
| **普通员工** | 本部门授权数据（读写） | 本部门授权Agent | 无 |

#### 2.5.3 审计日志

```sql
-- 所有Agent操作留痕
CREATE TABLE public.audit_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    user_id INT,
    user_name VARCHAR(50),
    department VARCHAR(50),
    agent_name VARCHAR(50),
    action_type VARCHAR(50),       -- query/create/export/delete/approve
    target_table VARCHAR(100),     -- 操作的数据表
    input_text TEXT,               -- 用户输入（保留原文）
    output_text TEXT,              -- Agent输出（保留原文）
    data_changed JSONB,            -- 数据变更详情（如果有）
    ip_address VARCHAR(50),
    token_used INT,
    duration_ms INT
);

-- 敏感操作告警规则
-- 导出超过1000条数据 → 通知部门负责人
-- 删除任何数据 → 通知老板
-- 非工作时间访问财务数据 → 通知老板+财务负责人
```

---

## 三、两大核心协作场景技术方案

### 3.1 选品定价协作流程

#### 3.1.1 数据流设计

```
选品定价数据流：

                    ┌──────────────┐
                    │   触发入口    │
                    │ 采购/业务发起  │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────────┐
              ▼            ▼                ▼
     ┌──────────────┐ ┌──────────┐ ┌──────────────┐
     │ 采购数据拉取  │ │ 销售数据  │ │ 市场数据拉取  │
     │              │ │ 拉取     │ │              │
     │·供应商报价    │ │·历史销量  │ │·竞品价格      │
     │·产地行情     │ │·退货率   │ │·市场热度      │
     │·历史采购价    │ │·售后投诉  │ │·季节性系数    │
     └──────┬───────┘ │·渠道表现  │ └──────┬───────┘
            │         └──────┬───┘        │
            │                │            │
            └────────┬───────┘────────────┘
                     ▼
          ┌──────────────────┐
          │  仓配+财务数据    │
          │                  │
          │·当前库存/库容     │
          │·仓储成本/包材成本 │
          │·快递费率          │
          │·目标毛利率        │
          │·平台佣金率        │
          └────────┬─────────┘
                   ▼
          ┌──────────────────┐
          │ AI 定价引擎       │
          │ (Dify Workflow)  │
          │                  │
          │ Step1: 数据汇聚   │
          │ Step2: 成本计算   │
          │ Step3: 定价建议   │
          │ Step4: 风险评估   │
          │ Step5: 生成报告   │
          └────────┬─────────┘
                   ▼
          ┌──────────────────┐
          │ 《选品定价建议书》 │
          │                  │
          │·建议采购价区间    │
          │·建议售价区间      │
          │·预估月销量        │
          │·预估售后率        │
          │·预估净利润        │
          │·风险提示          │
          └────────┬─────────┘
                   ▼
          ┌──────────────────┐
          │ 各部门在线评审    │
          │ (飞书群讨论)      │
          │                  │
          │ AI实时调取数据    │
          │ 回答各方疑问      │
          └────────┬─────────┘
                   ▼
          ┌──────────────────┐
          │ 最终定价确认      │
          │ 老板审批          │
          │ → 自动同步各部门  │
          └──────────────────┘
```

#### 3.1.2 AI处理逻辑

```
AI定价引擎 Workflow 步骤（Dify实现）：

Step 1 - 数据汇聚节点：
  输入：product_id（待选品ID）
  动作：
    - 查询 shared_data.products 获取基础信息
    - 查询 workspace_procurement.market_prices 获取行情
    - 查询 shared_data.orders_daily 获取历史销量（如有同类品）
    - 查询 workspace_cs.complaints 获取同类品售后率
    - 查询 shared_data.inventory 获取库存/仓配成本
  输出：结构化数据包

Step 2 - 成本计算节点（规则引擎，非AI）：
  总成本 = 采购成本 + 物流成本 + 包材成本 + 平台佣金 + 投流预估 + 售后预估
  其中：
    物流成本 = 快递费 + 仓配操作费
    平台佣金 = 售价 × 佣金率（按渠道）
    投流预估 = 目标GMV × 投流占比（行业均值或历史值）
    售后预估 = 售价 × 预估售后率 × 赔付比例

Step 3 - 定价建议节点（AI推理）：
  Prompt = """
  基于以下数据，给出建议售价区间：
  - 总成本：{total_cost}
  - 目标毛利率：{target_margin}（财务要求）
  - 同类竞品价格：{competitor_prices}
  - 历史同类品售价与销量关系：{history_data}
  - 当前市场热度：{market_heat}
  
  请给出：
  1. 建议售价区间（最低价/建议价/最高价）
  2. 预估月销量（乐观/中性/悲观）
  3. 理由
  """
  
Step 4 - 风险评估节点（AI推理）：
  评估维度：
  - 供应稳定性（供应商交期达成率、产地天气）
  - 季节性（是否应季、距旺季/淡季天数）
  - 竞争烈度（竞品数量、价格战程度）
  - 品质风险（同类品历史售后率）

Step 5 - 报告生成节点（AI生成）：
  将上述结果组装为《选品定价建议书》，格式化为飞书卡片消息
```

#### 3.1.3 输出产物

| 产物 | 格式 | 接收方 | 用途 |
|------|------|--------|------|
| 《选品定价建议书》 | 飞书卡片消息 + PDF存档 | 所有参与部门 + 老板 | 评审依据 |
| 评审意见汇总 | 飞书群消息 | 老板 | 最终决策参考 |
| 定价执行通知 | 飞书消息（分部门） | 各部门 | 各部门执行动作 |
| 数据存档 | PostgreSQL记录 | 系统 | 后续复盘对比 |

#### 3.1.4 技术实现要点

| 要点 | 方案 |
|------|------|
| 数据实时性 | 行情数据每日更新（API自动拉取），成本数据录入即更新 |
| AI准确性 | 定价建议基于公式计算+AI推理双重校验，AI建议仅供参考 |
| 流程效率 | 从发起→出建议书≤30分钟，评审→最终定价≤1小时 |
| 历史追溯 | 每次选品定价全过程存档，可对比"预测vs实际" |
| 权限控制 | 采购价/利润率仅参与部门和老板可见 |

### 3.2 采销配客服实时协作

#### 3.2.1 事件驱动架构设计

```
事件驱动架构（轻量级实现，不用Kafka）：

┌─────────────────────────────────────────────────────────┐
│                  事件驱动引擎                              │
│              (Python + PostgreSQL event_bus表)            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  事件生产者（数据源）                                     │
│  ├── 抖店API轮询（5min） → 订单事件/销量事件             │
│  ├── 千川API轮询（10min） → 投放事件/消耗事件            │
│  ├── 仓配录入（实时） → 库存事件/品控事件/发货事件       │
│  ├── 客服录入（实时） → 售后事件/差评事件/投诉事件       │
│  └── 采购录入（异常实时） → 供应事件/行情事件            │
│                                                          │
│  事件总线（event_bus表）                                  │
│  ┌──────────────────────────────────────────────────┐    │
│  │ id | event_type | severity | payload | status    │    │
│  │    | created_at | source   | consumers | ack_at  │    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
│  事件消费者                                              │
│  ├── 规则引擎（Python定时任务，每5min执行）               │
│  │   → 扫描未处理事件 → 匹配规则 → 触发联动              │
│  ├── AI研判器（复杂事件）                                 │
│  │   → 规则引擎无法处理 → 交给AI分析 → 生成建议          │
│  └── 通知分发器                                          │
│      → 飞书Webhook → 各部门协作群                        │
│      → 老板看板更新                                      │
│      → 紧急事项 → 飞书电话                               │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**event_bus 表结构**：

```sql
CREATE TABLE shared_data.event_bus (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50),       -- sales_surge/supply_disruption/quality_issue/stock_alert/roi_drop/compliance_alert
    severity VARCHAR(20),         -- critical/warning/info
    source VARCHAR(50),           -- douyin_api/qianchuan_api/warehouse_input/cs_input/procurement_input
    payload JSONB,                -- 事件详情
    affected_products INT[],      -- 涉及商品ID列表
    affected_departments VARCHAR(50)[], -- 需要通知的部门
    status VARCHAR(20) DEFAULT 'pending', -- pending/processing/resolved/ignored
    ai_analysis TEXT,             -- AI分析结果
    notifications_sent JSONB,     -- 已发送的通知记录
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    resolved_at TIMESTAMP
);

-- 索引：按status+created_at查询未处理事件
CREATE INDEX idx_event_pending ON shared_data.event_bus(status, created_at) WHERE status = 'pending';
```

#### 3.2.2 规则引擎设计

**阈值规则**（可配置，存储在配置表中）：

```sql
CREATE TABLE shared_data.alert_rules (
    id SERIAL PRIMARY KEY,
    rule_name VARCHAR(100),
    rule_type VARCHAR(50),        -- threshold/trend/combination
    metric VARCHAR(50),           -- 监控指标
    condition VARCHAR(200),       -- 条件表达式
    threshold_value DECIMAL(10,2),
    comparison VARCHAR(10),       -- gt/lt/gte/lte/between
    time_window_minutes INT,      -- 时间窗口
    severity VARCHAR(20),         -- 触发后的严重级别
    notify_departments VARCHAR(50)[], -- 通知部门
    notify_channels VARCHAR(50)[], -- feishu_message/feishu_call/dashboard
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**预置规则清单**：

| 规则名称 | 指标 | 条件 | 严重级别 | 通知部门 |
|---------|------|------|---------|---------|
| 销量暴涨 | 小时销量 | > 日均3倍 | warning | 仓配+采购+客服 |
| ROI暴跌 | 千川ROI | < 1.5 持续1小时 | critical | 业务+老板 |
| 库存断货 | 可售天数 | < 1天 | critical | 采购+业务+老板 |
| 库存偏低 | 可售天数 | < 3天 | warning | 采购+仓配 |
| 品质异常 | 入库不合格率 | > 3% | warning | 采购+业务+客服 |
| 售后超标 | 品售后率 | > 行业均值×1.5 | warning | 客服+采购+仓配 |
| 体验分下降 | 店铺体验分 | < 4.5 | critical | 客服+业务+老板 |
| 消耗异常 | 小时消耗 | > 日预算50% | critical | 业务+老板 |
| 发货延迟 | 待发货积压 | > 500单 且 超承诺时效 | warning | 仓配+客服+业务 |
| 赔付超标 | 日赔付金额 | > 日GMV×5% | warning | 财务+客服+老板 |

**联动规则**（A变化 → 通知B/C/D）：

```yaml
联动规则矩阵：
  销量暴涨:
    → 仓配: "备货建议 + 人力需求"
    → 采购: "补货建议 + 供应商确认"
    → 客服: "应急话术 + 预期售后率"
    → 财务: "GMV/利润预估更新"
    
  供应中断:
    → 业务: "提价/限量/切换替代品建议"
    → 仓配: "库存分配优先级建议"
    → 客服: "延迟发货话术 + 补偿方案"
    → 财务: "成本影响评估"
    
  品质异常:
    → 采购: "供应商扣款/整改/备选建议"
    → 业务: "暂停推广/调整详情页建议"
    → 客服: "主动联系/赔付方案"
    → 财务: "赔付预估 + 损耗统计"
    
  评分下降:
    → 客服: "紧急干预方案"
    → 业务: "降低推广/优化详情页"
    → 采购: "品质溯源"
    → 仓配: "打包/物流改进"
```

#### 3.2.3 AI研判逻辑

```
AI研判触发条件：
├── 多指标同时异常（规则引擎无法覆盖的组合情况）
├── 趋势持续恶化（连续N小时/天指标变差）
└── 事件影响范围大（涉及多个品/多个渠道）

AI研判流程：
1. 收集相关数据（近7天指标趋势 + 历史相似事件）
2. 调用 qwen2.5:14b 进行分析：
   Prompt = """
   当前异常事件：{event_detail}
   相关指标趋势（近7天）：{metrics_trend}
   历史相似事件及处理结果：{similar_history}
   
   请分析：
   1. 最可能的根因（1-3个）
   2. 对各业务线的影响评估
   3. 建议的应对措施（按优先级排序）
   4. 是否需要升级处理（通知老板）
   """
3. 输出结构化分析报告
4. 附加在飞书通知中推送
```

#### 3.2.4 告警分级与通知渠道

| 告警级别 | 触发条件 | 通知方式 | 响应时效 |
|---------|---------|---------|---------|
| **紧急（Critical）** | ROI<1.5、断货、体验分<4.5、大额亏损 | 飞书电话+消息+Dashboard弹窗 | 15分钟内响应 |
| **重要（Warning）** | 指标偏离阈值、趋势恶化、品质异常 | 飞书群消息+Dashboard标记 | 1小时内响应 |
| **关注（Info）** | 指标波动但未达阈值、信息通知 | 飞书消息（非@） | 下一工作日处理 |

**飞书通知格式**（卡片消息）：

```
🚨 【紧急预警】XX品库存即将断货
━━━━━━━━━━━━━━━━━━━━
📦 商品：蜂糖李 5斤装
📊 当前库存：120件
📈 日均销量：85件
⏰ 预计断货时间：1.4天后
━━━━━━━━━━━━━━━━━━━━
🔔 建议动作：
  → 采购：立即联系供应商补货，预计需XX件
  → 业务：考虑限量销售或暂停推广
  → 仓配：优先保障该品打包发货
━━━━━━━━━━━━━━━━━━━━
💡 AI分析：近3天销量呈上升趋势（+25%），
叠加周末效应，实际断货可能在明天下午。
建议补货量≥200件。
```

#### 3.2.5 安全库存动态调整算法

```
动态安全库存计算公式：

SS = Z × σ_d × √(LT + RT)

其中：
  SS  = 安全库存
  Z   = 服务水平系数（默认1.65 = 95%服务水平）
  σ_d = 需求标准差（近30天日销量标准差）
  LT  = 供应商交货周期（天）
  RT  = 评审周期（天，默认7天）

动态调整因子（每日更新）：

  LT_adjusted = LT_base × (1 + delivery_delay_rate)
    delivery_delay_rate = 近30天实际交期 / 承诺交期 - 1
  
  σ_d_adjusted = σ_d_base × season_factor × event_factor
    season_factor:
      应季品 = 1.3（需求波动大）
      淡季品 = 0.8（需求稳定）
      节日品 = 1.5（临近节日时）
    event_factor:
      未来7天有直播计划 = 1.5
      有平台大促 = 2.0
      正常 = 1.0
  
  Z_adjusted = f(supplier_reliability)
    供应商交期达成率 > 95% → Z = 1.28（90%服务水平即可）
    供应商交期达成率 < 80% → Z = 2.05（需98%服务水平）

实现方式：
  Python定时任务，每日凌晨计算 → 更新 shared_data.inventory.safety_stock
  → 如有大幅调整（>20%），通知采购+仓配确认
```

---

## 四、财务三大预警技术方案

### 4.1 成本异常预警

#### 4.1.1 监控指标清单

| 指标分类 | 具体指标 | 数据来源 | 监控频率 |
|---------|---------|---------|---------|
| **采购成本** | 单品采购价环比变化率 | 采购录入 + shared_data.products | 每笔采购 |
| | 同品不同供应商价差 | workspace_procurement | 每笔采购 |
| | 采购总量周环比 | workspace_procurement | 每周 |
| **物流成本** | 单均快递费 | 快递对账单 + shared_data.orders_daily | 每日 |
| | 快递线路费用变化 | 快递对账单 | 每周 |
| | 包材成本占GMV比 | 仓配录入 | 每周 |
| **售后成本** | 单品赔付金额/比例 | workspace_cs.complaints | 每日 |
| | 整体售后成本占GMV比 | workspace_finance | 每日 |
| | 品类售后成本周环比 | workspace_finance | 每周 |
| **人力成本** | 部门人力成本 vs 预算 | workspace_hr | 每月 |
| | 人均产出趋势 | workspace_hr + shared_data.orders_daily | 每月 |

#### 4.1.2 阈值设定规则

```yaml
成本异常阈值配置：

采购成本:
  单品采购价环比上涨: 
    warning: ">10%"
    critical: ">20%"
  同品供应商价差:
    warning: ">15%"
    critical: ">30%"
  采购总量周环比:
    warning: "±30%"
    critical: "±50%"

物流成本:
  单均快递费超预算:
    warning: ">10%"
    critical: ">20%"
  包材成本占GMV比:
    warning: ">历史均值×1.2"
    critical: ">历史均值×1.5"

售后成本:
  单品赔付比例:
    warning: ">5%"
    critical: ">10%"
  整体售后占GMV:
    warning: ">历史均值×1.3"
    critical: ">历史均值×1.5"

人力成本:
  部门超预算:
    warning: ">110%"
    critical: ">130%"
```

#### 4.1.3 告警逻辑

```
成本异常告警处理流程：

1. 数据采集：
   - 每笔采购入库时 → 自动对比历史价格
   - 每日凌晨 → 汇总前一日各项成本指标
   - 每周一 → 生成周度成本对比报告

2. 规则匹配：
   - 指标值 vs 阈值 → 判定warning/critical
   - 连续N次超标 → 升级为critical
   - 多指标同时超标 → 升级为critical

3. AI分析增强：
   - 不是简单超阈值告警，AI会分析原因
   - 例如：采购价上涨10% → AI查行情 → 
     "市场整体涨价15%，当前供应商价格仍低于市场均价，属合理波动"
   - 避免无效告警，只在真正异常时通知

4. 告警输出：
   - 飞书消息 → 财务负责人 + 老板
   - 内容：异常指标 + 偏离幅度 + AI分析原因 + 建议动作
   - 示例："⚠️ 采购成本预警：芒果采购价本周环比上涨18%。
     AI分析：产地云南受暴雨影响，市场均价上涨22%，
     当前供应商报价仍低于市场均价。建议维持现有供应商，
     关注天气变化，准备备选产地（广西）。"
```

### 4.2 投产异常预警

#### 4.2.1 ROI监控体系

```
千川ROI监控层级：

┌──────────────────────────────────────────┐
│ 整体层面                                  │
│ · 全账户ROI → 低于2.0 → warning          │
│ · 全账户ROI → 低于1.5 → critical         │
│ · 日消耗 vs 日预算 → 超支50% → critical   │
├──────────────────────────────────────────┤
│ 计划层面                                  │
│ · 单计划ROI → 连续2小时低于均值50% → critical│
│ · 单计划消耗速度 → 1小时超日预算30% → warning│
│ · 单计划ROI → 连续3天为负 → warning       │
├──────────────────────────────────────────┤
│ 素材层面                                  │
│ · 素材A/B测试 → ROI差距>100% → info       │
│ · 素材消耗占比 → 单素材>50%总消耗 → warning │
├──────────────────────────────────────────┤
│ 达人层面                                  │
│ · 达人带货ROI → 低于1.0 → warning         │
│ · 达人服务费新规 → D级达人ROI持续为负 → critical│
└──────────────────────────────────────────┘

数据拉取频率：
├── 千川API → 投放数据（10分钟一次）
├── 抖店API → 订单/成交数据（10分钟一次）
└── ROI计算 → 消耗/成交GMV → 实时更新
```

#### 4.2.2 单品亏损检测

```
单品利润计算模型：

单品净利润 = GMV - 采购成本 - 物流成本 - 包材成本 
            - 平台佣金 - 投流成本 - 售后赔付 - 其他分摊

实时监控：
  每笔订单成交后 → 计算该品当日累计利润
  当日累计利润 < 0 → 触发"单品亏损预警"

亏损分级：
  轻微亏损（利润率 -5% ~ 0%）→ info，日报体现
  明显亏损（利润率 -10% ~ -5%）→ warning，通知业务+财务
  严重亏损（利润率 < -10%）→ critical，通知老板+业务+财务

AI分析附加：
  "XX品今日GMV 5000元，总成本 6200元，亏损1200元（-24%）。
   亏损原因：投流成本占比42%（正常20%），售后赔付占比12%（正常5%）。
   建议：① 降低投流预算 ② 排查售后问题根因 ③ 评估是否继续推广"
```

#### 4.2.3 渠道投产失衡检测

```
渠道ROI监控：

  渠道健康度评分 = f(ROI趋势, ROI稳定性, GMV增长, 退货率)

  检测规则：
  ├── 某渠道ROI连续7天低于均值 → 渠道效率下降预警
  ├── 某渠道投入增加但GMV不增长（连续14天）→ 投产失衡预警
  ├── 某渠道退货率异常上升（周环比>50%）→ 渠道风险预警
  └── 活动期间ROI vs 日常ROI → 活动投产评估报告

  AI建议：
  "拼多多渠道近14天投入增加20%但GMV仅增长3%，ROI从2.5降至1.8。
   原因分析：竞品降价导致流量成本上升，且退货率从8%升至15%。
   建议：① 暂停增加投入 ② 优化商品详情页减少退货 ③ 评估是否调整价格策略"
```

### 4.3 合规预警

#### 4.3.1 税务合规监控

```
税务合规模块：

监控项：
├── 进销项发票匹配
│   ├── 每月自动统计进项/销项金额
│   ├── 进项不足预警（进项/销项 < 80%）→ warning
│   ├── 提前提醒：距离申报截止日7天 → info
│   └── 税负率监控（增值税税负率偏离行业均值±30%）→ warning
│
├── 税务申报日历
│   ├── 增值税（月度）→ 每月15日前
│   ├── 企业所得税（季度）→ 季后15日内
│   ├── 个税（月度）→ 每月15日前
│   └── 自动提前提醒 + 飞书日程创建
│
├── 税收优惠政策追踪
│   ├── 农产品流通免税政策 → 持续适用
│   ├── 小微企业优惠 → 监控是否仍符合标准
│   └── 政策变更 → 影响评估 + 应对建议
│
└── 大额交易监控
    ├── 单笔>5万 → 记录备查
    ├── 月度累计异常 → AI分析合理性
    └── 关联交易 → 价格合理性检查
```

#### 4.3.2 平台合规模块

```
平台合规模块：

监控来源：
├── 抖店API → 店铺违规/处罚通知（实时Webhook）
├── 拼多多API → 店铺违规通知
└── 人工录入 → 平台规则变更公告

监控项：
├── 店铺违规
│   ├── 收到处罚通知 → 即时告警（critical）
│   ├── 处罚类型分类：虚假宣传/资质缺失/延迟发货/售后不当
│   ├── 自动评估影响：扣分→预估对体验分的影响
│   └── AI建议：整改措施 + 申诉策略
│
├── 商品合规
│   ├── 定期扫描商品标题/详情 → 是否含违禁词
│   ├── 资质到期提醒（食品经营许可证等）
│   └── 广告法合规检查（极限词/虚假宣传）
│
├── 达人服务费新规（2026.7.8生效）
│   ├── A级达人：0费率 → 优先合作
│   ├── B+级：20% → 正常合作
│   ├── B级：30% → 评估ROI
│   ├── C级：35% → 谨慎合作
│   └── D级：40% → 建议替换
│   系统自动标记达人等级，筛选时优先推荐A/B+级
│
└── 规则变更追踪
    ├── 人工/自动采集平台规则更新
    ├── AI评估影响范围（涉及哪些商品/流程）
    └── 生成应对建议 → 通知相关部门
```

#### 4.3.3 发票合规模块

```
发票合规模块：

监控项：
├── 发票真伪验证
│   ├── 新录入发票 → 调用税务局验证接口（或人工复核标记）
│   ├── 验证失败 → 即时告警（critical）
│
├── 发票-合同匹配
│   ├── 发票金额 vs 合同金额 → 偏差>5% → warning
│   ├── 发票日期 vs 合同日期 → 逻辑异常检查
│
├── 发票认证期限
│   ├── 未认证发票 → 距截止日30天 → warning
│   ├── 距截止日7天 → critical
│
├── 供应商开票信息
│   ├── 供应商开票信息变更 → 自动比对
│   └── 变更未确认 → 暂停开票提醒
│
└── 资金合规
    ├── 大额资金进出（单笔>10万）→ 记录+AI分析
    ├── 公私混用检测 → 非常规转账告警
    └── 合同付款 vs 发票 → 不匹配告警
```

---

## 五、数据接入方案

### 5.1 抖店开放平台API对接

**已有资源**：430个API文档（已下载整理）

**优先对接API清单**：

| 模块 | API | 用途 | 调用频率 | 优先级 |
|------|-----|------|---------|--------|
| 订单 | `/order/searchList` | 订单查询/汇总 | 10min | P0 |
| 订单 | `/order/orderDetail` | 订单详情 | 按需 | P0 |
| 商品 | `/product/listV2` | 商品列表 | 1h | P0 |
| 售后 | `/afterSale/orderList` | 售后单查询 | 30min | P0 |
| 物流 | `/logistics/list` | 物流信息 | 1h | P1 |
| 评价 | `/comment/list` | 评价/差评 | 30min | P0 |
| 直播 | `/live/roomList` | 直播间数据 | 30min | P0 |
| 店铺 | `/shop/score` | 体验分 | 1h | P0 |
| 财务 | `/settlement/billDetail` | 结算账单 | 1天 | P1 |
| 达人 | `/buyin/authorList` | 达人带货数据 | 1天 | P1 |

**对接方案**：

```python
# 抖店API对接架构（Python脚本，Dify Workflow调用）

抖店开放平台 → OAuth2.0认证 → API调用 → 数据清洗 → PostgreSQL

数据同步服务（Python，部署在Mac Mini）：
├── douyin_sync.py       # 抖店数据同步主程序
│   ├── 定时任务（APScheduler）
│   ├── API调用封装（requests + 签名计算）
│   ├── 数据清洗 & 标准化
│   └── 写入PostgreSQL（shared_data / workspace_ops）
│
├── config.yaml          # API密钥、店铺ID、同步频率配置
└── logs/                # 同步日志

注意事项：
├── 抖店API有频率限制 → 需要限流（令牌桶算法）
├── 数据需要去重 → 基于订单ID/商品ID去重
├── 签名计算 → 按照抖店文档实现HMAC签名
└── 异常处理 → API调用失败 → 重试3次 → 失败告警
```

### 5.2 千川API对接

**已有资源**：OAuth已申请

**对接API清单**：

| API | 用途 | 调用频率 | 优先级 |
|-----|------|---------|--------|
| 广告计划列表 | 计划状态/消耗/ROI | 10min | P0 |
| 广告素材数据 | 素材效果分析 | 1h | P1 |
| 账户消耗汇总 | 整体投放数据 | 10min | P0 |
| 达人合作数据 | 达人带货效果 | 1天 | P1 |

**对接方案**：

```python
# 千川API数据同步
qianchuan_sync.py:
├── OAuth2.0 认证刷新
├── 投放数据拉取 → workspace_ops.ad_plans
├── ROI实时计算 → 写入shared_data供其他Agent查询
├── 异常检测 → 消耗/ROI超阈值 → 写入event_bus
└── 飞书通知 → 投放异常即时推送
```

### 5.3 拼多多API对接

| API | 用途 | 调用频率 | 优先级 |
|-----|------|---------|--------|
| 订单列表 | 订单数据同步 | 30min | P1 |
| 售后列表 | 售后数据同步 | 1h | P1 |
| 商品列表 | 商品信息同步 | 1天 | P1 |
| 店铺数据 | 店铺评分/违规 | 1h | P1 |
| 结算账单 | 财务对账 | 1天 | P1 |

**对接计划**：第3阶段（5-8周）实施，优先完成抖店和千川

### 5.4 飞书集成方案

```
飞书集成架构：

┌──────────────────────────────────────────────┐
│              飞书集成方案                       │
├──────────────────────────────────────────────┤
│                                              │
│  1. 飞书机器人（通知推送）                      │
│     ├── 方式：飞书自定义机器人（Webhook）        │
│     ├── 部署：Dify Workflow → HTTP请求节点      │
│     ├── 推送内容：                              │
│     │   ├── 每日经营简报（老板群，9:00）        │
│     │   ├── 异常预警（各部门协作群，实时）       │
│     │   ├── 日报/周报（部门群，定时）            │
│     │   └── 合规提醒（财务群，定时）             │
│     └── 消息格式：飞书卡片消息（Interactive Card）│
│                                              │
│  2. 飞书应用（双向交互，P2阶段实现）             │
│     ├── 方式：飞书应用 → 消息回调               │
│     ├── 功能：在飞书聊天中直接@AI查询数据        │
│     └── 前提：需要飞书开放平台应用审核           │
│                                              │
│  3. 飞书文档（知识库同步）                      │
│     ├── 现有SOP/制度文档 → 导入Dify知识库       │
│     ├── 会议纪要 → 定期同步                     │
│     └── 方式：飞书开放API读取文档内容            │
│                                              │
│  4. 飞书日程（提醒与计划）                      │
│     ├── 税务申报提醒 → 创建飞书日程             │
│     ├── 会议安排 → 自动创建                     │
│     └── 方式：飞书日历API                       │
│                                              │
└──────────────────────────────────────────────┘

飞书Webhook配置：
├── 老板群 Webhook URL → 经营简报 + 全局预警
├── 直播组群 Webhook URL → 直播数据 + 投放预警
├── 客服群 Webhook URL → 差评预警 + 售后通知
├── 采购仓配群 Webhook URL → 库存预警 + 协同通知
├── 财务群 Webhook URL → 合规预警 + 成本预警
└── 全员群 Webhook URL → 重要公告
```

### 5.5 数据同步频率设计

```
数据同步时间表：

┌────────────────┬──────────┬───────────┬──────────────────┐
│ 数据源          │ 同步频率  │ 同步方式   │ 说明             │
├────────────────┼──────────┼───────────┼──────────────────┤
│ 抖店订单        │ 10分钟    │ API拉取   │ P0，核心数据      │
│ 抖店售后        │ 30分钟    │ API拉取   │ P0              │
│ 抖店评价        │ 30分钟    │ API拉取   │ P0，差评即时      │
│ 抖店直播数据    │ 30分钟    │ API拉取   │ P0              │
│ 抖店体验分      │ 1小时     │ API拉取   │ P0              │
│ 千川投放数据    │ 10分钟    │ API拉取   │ P0，ROI核心      │
│ 拼多多订单      │ 30分钟    │ API拉取   │ P1              │
│ 拼多多售后      │ 1小时     │ API拉取   │ P1              │
│ 库存数据        │ 实时      │ 手动录入   │ P0，扫码/录入    │
│ 采购行情        │ 每日      │ 手动录入   │ P0              │
│ 财务数据        │ 每日      │ 手动+自动  │ P1              │
│ 人力数据        │ 每周      │ 手动录入   │ P1              │
│ 结算账单        │ 每日      │ API拉取   │ P1              │
└────────────────┴──────────┴───────────┴──────────────────┘

AT系统已有能力：
├── 部分电商数据已在AT系统中有存储 → 评估是否可直接读取
├── 避免重复拉取 → 优先从AT系统获取已有数据
└── AT系统数据同步到PostgreSQL → 作为补充数据源
```

---

## 六、硬件采购清单与成本估算

### 6.1 推荐配置

| 阶段 | 硬件 | 数量 | 单价 | 小计 | 说明 |
|------|------|------|------|------|------|
| **阶段1** | 现有办公电脑 | 1 | 0元 | 0元 | 开发验证用 |
| **阶段2** | Mac Mini M4 24GB | 1 | ~5,500元 | 5,500元 | 日常生产环境 |
| **阶段3**（可选） | Mac Mini M4 48GB | 1 | ~11,000元 | 11,000元 | 替代24GB，跑更大模型 |
| **阶段3**（可选） | Mac Mini M4 Pro 64GB | 1 | ~18,000元 | 18,000元 | 与48GB二选一 |

### 6.2 外设与网络

| 物品 | 数量 | 单价 | 小计 | 说明 |
|------|------|------|------|------|
| 外接USB硬盘 2TB | 1 | ~400元 | 400元 | 数据备份 |
| UPS不间断电源 | 1 | ~500元 | 500元 | 防止断电数据丢失 |
| 千兆交换机（如需） | 1 | ~100元 | 100元 | 网络扩展 |
| 网线 Cat6 | 若干 | ~50元 | 50元 | Mac Mini有线连接 |
| **外设小计** | | | **~1,050元** | |

### 6.3 总成本估算

| 方案 | 硬件总成本 | 适用场景 |
|------|-----------|---------|
| **最小方案** | ~6,550元 | Mac Mini M4 24GB + 备份硬盘 + UPS + 网络 |
| **推荐方案** | ~12,550元 | Mac Mini M4 48GB + 备份硬盘 + UPS + 网络 |
| **旗舰方案** | ~19,550元 | Mac Mini M4 Pro 64GB + 备份硬盘 + UPS + 网络 |

> 建议：先用最小方案（~6,550元）跑通全部功能，确认效果后再决定是否升级。

---

## 七、软件栈与部署方案

### 7.1 软件清单+版本号

| 软件 | 版本 | 用途 | 费用 |
|------|------|------|------|
| macOS | Sonoma 14.x+ | 操作系统（Mac Mini） | 0元 |
| Docker Desktop | 最新稳定版 | 容器化部署 | 0元（个人免费） |
| Ollama | 最新稳定版 | 本地模型服务 | 0元 |
| Dify | v0.8+ (CE) | Agent编排平台 | 0元（开源版） |
| PostgreSQL | 16.x | 业务数据库 | 0元 |
| ChromaDB | 最新稳定版 | 向量数据库 | 0元 |
| Redis | 7.x | 缓存+消息队列 | 0元 |
| One API | 最新稳定版 | 模型API网关 | 0元 |
| Nginx | 最新稳定版 | 反向代理（飞书Webhook） | 0元 |
| Python | 3.11+ | 数据同步脚本 | 0元 |
| Node.js | 20 LTS | Dify依赖 | 0元 |
| **合计** | | | **0元** |

### 7.2 Docker Compose 部署架构

```yaml
# docker-compose.yml 架构概览

version: '3.8'

services:
  # === L2 平台层 ===
  dify-api:
    image: langgenius/dify-api:latest
    ports: ["5001:5001"]
    depends_on: [postgresql, redis]
    environment:
      - SECRET_KEY=${DIFY_SECRET_KEY}
      - DB_HOST=postgresql
      - REDIS_HOST=redis
    
  dify-web:
    image: langgenius/dify-web:latest
    ports: ["3000:3000"]
    depends_on: [dify-api]
  
  # === L1 数据层 ===
  postgresql:
    image: postgres:16-alpine
    ports: ["5432:5432"]
    volumes:
      - pg_data:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    environment:
      - POSTGRES_USER=dify
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    # 创建多个schema（init-db.sql中实现）
  
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    volumes:
      - redis_data:/data
  
  chromadb:
    image: chromadb/chroma:latest
    ports: ["8000:8000"]
    volumes:
      - chroma_data:/chroma/chroma
  
  # === L2 API网关 ===
  one-api:
    image: justsong/one-api:latest
    ports: ["3001:3000"]
    depends_on: [postgresql]
  
  # === 反向代理 ===
  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf

volumes:
  pg_data:
  redis_data:
  chroma_data:
```

**端口规划**：

| 服务 | 端口 | 访问方式 |
|------|------|---------|
| Dify Web UI | 3000 | http://192.168.1.100:3000 |
| One API | 3001 | http://192.168.1.100:3001 |
| PostgreSQL | 5432 | 仅内网 |
| Redis | 6379 | 仅内网 |
| ChromaDB | 8000 | 仅内网 |
| Nginx | 80 | 飞书Webhook入口 |
| Ollama | 11434 | http://192.168.1.100:11434 |

### 7.3 分步部署计划

```
部署路径：现有电脑跑通 → 迁移Mac Mini

第1步：现有电脑部署（第1周）
├── 安装 Docker Desktop
├── 安装 Ollama + 下载 qwen2.5:7b
├── docker-compose up → 启动 Dify + PostgreSQL + Redis
├── 验证：在Dify中创建一个简单Agent，测试对话
└── 目的：验证整体流程可行，团队熟悉工具

第2步：现有电脑完善（第2-3周）
├── 下载更多模型（qwen2.5:14b, bge-m3）
├── 搭建第一批P0 Agent（老板Agent + 直播复盘Agent）
├── 导入第一批知识库（SOP/产品手册/FAQ）
├── 手动导入一些数据验证数据流
└── 目的：核心功能在现有电脑上跑通

第3步：Mac Mini部署（第3-4周，硬件到货后）
├── Mac Mini初始化 + Docker Desktop安装
├── docker-compose up → 全量服务启动
├── 从现有电脑迁移数据：
│   ├── PostgreSQL: pg_dump → pg_restore
│   ├── ChromaDB: 复制数据目录
│   ├── 知识库文件: rsync
│   └── 配置文件: 复制
├── 验证所有Agent在新环境正常运行
├── 现有电脑回归办公用途
└── 目的：独立生产环境上线

第4步：优化完善（第5周+）
├── 配置Nginx反向代理（飞书Webhook）
├── 设置自动备份脚本（每日凌晨pg_dump → 外接硬盘）
├── 配置UPS通讯（优雅关机）
├── 设置开机自启动（launchd）
└── 压力测试（模拟多用户并发）
```

---

## 八、分阶段实施计划

### 第1阶段（第1-2周）：基础设施搭建 + 试点

**目标**：在现有电脑上跑通基础环境，1个部门试点验证

| 任务 | 负责人 | 交付物 | 验收标准 |
|------|--------|--------|---------|
| 安装Docker Desktop + Ollama | 口袋/顶全 | 运行中的容器环境 | docker ps显示所有服务正常 |
| 部署Dify + PostgreSQL + Redis | 口袋/顶全 | Dify Web UI可访问 | http://localhost:3000 可登录 |
| 下载并部署模型（qwen2.5:7b/14b + bge-m3） | 口袋/顶全 | Ollama API可用 | curl测试模型响应正常 |
| 创建客服部/运营部试点Agent | 小全 | 1-2个可用Agent | 能正常对话，能查知识库 |
| 导入第一批知识库 | 小全+试点部门 | 知识库RAG可用 | 问答准确率>80% |
| 培训试点部门使用 | 小全 | 培训文档+录屏 | 试点部门能独立使用 |

**里程碑**：试点部门能用AI回答常见问题，团队认可"这条路能走通"

### 第2阶段（第3-4周）：核心P0功能上线

**目标**：6个P0 Agent全部上线，老板每日收到经营简报

| 任务 | 负责人 | 交付物 | 验收标准 |
|------|--------|--------|---------|
| Mac Mini到货 → 部署迁移 | 口袋/顶全 | Mac Mini生产环境 | 所有服务正常运行 |
| 老板全局Agent上线 | 小全+口袋 | 经营简报每日推送 | 9:00飞书准时推送 |
| 直播复盘Agent上线 | 小全+口袋 | 自动复盘报告 | 每场直播后30min内出报告 |
| 千川ROI看板Agent上线 | 口袋/顶全 | ROI实时监控+预警 | 异常15分钟内告警 |
| 客服自动回复Agent上线 | 小全+口袋 | 常见问题AI回复 | 覆盖80%常见问题 |
| 库存预警Agent上线 | 口袋/顶全 | 断货预警推送 | 库存低于阈值即时通知 |
| 薪酬核算Agent上线 | 小全+口袋 | 薪酬自动计算 | 计算结果与人工核对一致 |
| 飞书Webhook配置 | 口袋/顶全 | 通知渠道打通 | 飞书群能收到AI推送 |

**里程碑**：老板每天收到经营简报，投放异常秒级发现，客服工作量明显下降

### 第3阶段（第5-8周）：P1功能扩展 + API对接

**目标**：P1 Agent上线，电商API全面打通，跨部门协作流程跑通

| 任务 | 负责人 | 交付物 | 验收标准 |
|------|--------|--------|---------|
| 抖店API对接（订单/商品/售后/评价） | 口袋/顶全 | 数据自动同步 | 数据延迟≤15min |
| 千川API对接（投放/素材/账户） | 口袋/顶全 | 投放数据自动同步 | 数据延迟≤15min |
| 拼多多API对接 | 口袋/顶全 | 数据自动同步 | 数据延迟≤30min |
| 财务对账Agent + 实时盈亏Agent | 小全+口袋 | 自动对账+盈亏看板 | 月对账时间缩短80% |
| 直播话术Agent + 达人筛选Agent | 小全 | 话术生成+达人评估 | 话术可用率>70% |
| 供应商管理Agent + 商品优化Agent | 小全+口袋 | 供应商看板+商品优化 | 供应商评分准确 |
| 私域文案Agent + 培训问答Agent | 小全 | 文案生成+培训问答 | 文案可直接使用 |
| 选品定价协作流程上线 | 小全+口袋 | 端到端协作流程 | 30min出建议书 |
| 采销配协同通知机制上线 | 口袋/顶全 | 实时联动通知 | 事件触发→5min内通知到位 |
| 财务三大预警体系上线 | 小全+口袋 | 成本/投产/合规预警 | 告警准确率>85% |

**里程碑**：选品定价从1-2天→1小时，采销配实时联动，财务三大预警全覆盖

### 第4阶段（第9-12周）：P2深度应用 + 全局看板

**目标**：P2 Agent上线，全局看板完善，系统稳定运行

| 任务 | 负责人 | 交付物 | 验收标准 |
|------|--------|--------|---------|
| 销量预测Agent | 口袋/顶全 | 需求预测 | 预测偏差<20% |
| 竞品监控Agent | 小全 | 竞品变化追踪 | 竞品调价1h内通知 |
| 财务风险雷达Agent | 小全+口袋 | 综合风险评估 | 风险预警覆盖率>90% |
| 离职预警Agent | 小全 | 离职风险预测 | 模型初步可用 |
| 全局Dashboard | 口袋/顶全 | Web看板 | 老板可实时查看全数据 |
| 系统优化 & 稳定性加固 | 口袋/顶全 | 稳定运行环境 | 7×24无故障运行 |
| 全公司推广 & 培训 | 小全 | 全员培训完成 | 所有部门都在使用 |
| 效果评估 & v4.0规划 | 小全+伟壕 | 效果评估报告 | 量化ROI |

**里程碑**：全公司各部门都在使用AI系统，老板对全局经营状况实时掌控

---

## 九、团队与分工

### 9.1 角色定义

| 角色 | 人员 | 职责 | 投入时间 |
|------|------|------|---------|
| **项目经理/AI Agent** | 小全 | 需求拆解、方案设计、Agent配置、验收协调、项目管理、知识库整理、培训 | 全职 |
| **后端开发** | 口袋/顶全 | API对接开发、数据同步脚本、规则引擎、部署运维、前端看板 | 全职 |
| **决策审批** | 伟壕（老板） | 需求确认、方案审批、资源协调、验收确认、飞书群配置 | 兼职 |
| **部门配合** | 各部门负责人 | 提供业务需求、参与测试、反馈优化意见 | 兼职 |

### 9.2 协作方式

```
协作流程：

1. 需求确认：
   伟壕口述需求 → 小全整理为结构化需求文档 → 伟壕确认 → 口袋/顶全执行

2. 开发执行：
   小全拆解为技术任务 → 分配给口袋/顶全 → 每日站会同步进度 → 小全验收

3. 测试验收：
   小全初验 → 部门试用 → 反馈修改 → 伟壕最终确认

4. 沟通机制：
   ├── 飞书项目群：每日进度同步
   ├── 飞书文档：技术文档+会议纪要
   └── 每周复盘：伟壕+小全+口袋/顶全，30分钟
```

---

## 十、风险与应对

### 10.1 技术风险

| 风险 | 概率 | 影响 | 应对策略 |
|------|------|------|---------|
| Mac Mini M4 24GB算力不足，并发请求响应慢 | 高 | 中 | 限制并发数（排队机制）；简单任务用7b模型；按需升级48GB |
| 本地模型回答质量不达预期 | 中 | 高 | 持续优化Prompt；知识库质量把关；必要时接入云端API补充 |
| Dify开源版功能限制 | 中 | 中 | 评估社区版vs商业版；部分功能用Python脚本补充 |
| 电商API对接遇到技术障碍（签名/权限/限流） | 中 | 高 | 提前研究API文档；准备手动导入作为备用方案 |
| Docker容器服务不稳定 | 低 | 高 | 配置容器自动重启（restart: always）；设置健康检查；配置监控告警 |
| 数据同步延迟超出预期 | 中 | 中 | 优化同步脚本；关键数据提高频率；增加异常告警 |

### 10.2 数据风险

| 风险 | 概率 | 影响 | 应对策略 |
|------|------|------|---------|
| 数据丢失（硬件故障/误操作） | 低 | 极高 | 每日自动备份到外接硬盘；PostgreSQL开启WAL日志；保留30天备份 |
| 敏感数据泄露 | 低 | 极高 | 严格RBAC权限；调用审计日志；内网部署不暴露公网 |
| 数据不一致（多系统数据冲突） | 中 | 中 | 统一数据源（以电商平台API为准）；手动录入增加校验 |
| 知识库内容过时/错误 | 中 | 中 | 定期审核知识库；建立知识更新流程；版本管理 |

### 10.3 人员风险

| 风险 | 概率 | 影响 | 应对策略 |
|------|------|------|---------|
| 各部门配合度低，Agent没人用 | 高 | 高 | 先做1个部门出效果 → 效果带动推广 → 老板背书要求使用 |
| 关键开发人员（口袋/顶全）离职 | 低 | 高 | 完善技术文档；代码规范；Dify低代码降低开发依赖 |
| 业务部门提需求模糊/频繁变更 | 中 | 中 | 小全做需求把关；每个阶段锁定需求范围；变更走评审流程 |
| 伟壕时间不够，审批/决策延迟 | 中 | 中 | 明确哪些需要伟壕决策，哪些小全可自主决定；减少伟壕审批负担 |

### 10.4 整体应对策略

```
核心原则：
1. 先跑通最小闭环 → 验证价值 → 再扩展
2. 用效果说话 → 一个部门成功 → 带动其他部门
3. 文档驱动 → 所有技术方案/配置/操作都有文档 → 降低人员依赖
4. 开源兜底 → 全栈开源 → 不受厂商锁定，随时可换
5. 渐进式投入 → 先花~6500元验证 → 确认有效再追加投入
```

---

## 十一、预算总表

### 11.1 硬件成本

| 项目 | 最小方案 | 推荐方案 | 旗舰方案 |
|------|---------|---------|---------|
| Mac Mini M4 24GB | 5,500元 | - | - |
| Mac Mini M4 48GB | - | 11,000元 | - |
| Mac Mini M4 Pro 64GB | - | - | 18,000元 |
| 外接硬盘 2TB | 400元 | 400元 | 400元 |
| UPS电源 | 500元 | 500元 | 500元 |
| 网络设备 | 150元 | 150元 | 150元 |
| **硬件总计** | **~6,550元** | **~12,050元** | **~19,050元** |

### 11.2 软件成本

| 项目 | 费用 |
|------|------|
| Ollama | 0元（开源） |
| Dify CE | 0元（开源） |
| PostgreSQL | 0元（开源） |
| ChromaDB | 0元（开源） |
| Redis | 0元（开源） |
| One API | 0元（开源） |
| Nginx | 0元（开源） |
| Python/Node.js | 0元（开源） |
| **软件总计** | **0元** |

### 11.3 运营成本（月）

| 项目 | 月费用 | 说明 |
|------|--------|------|
| 电费 | ~30元 | Mac Mini功耗约30W，24h运行 |
| 网络 | ~20元 | 局域网运行，增量很小 |
| 域名（如需公网访问） | ~5元 | 可选，年费约60元 |
| **月运营总计** | **~55元** | |

### 11.4 人力成本

| 角色 | 人员 | 成本 | 说明 |
|------|------|------|------|
| 项目经理/AI Agent | 小全 | 内部人力 | 现有团队，无额外招聘 |
| 后端开发 | 口袋/顶全 | 内部人力 | 现有团队，无额外招聘 |
| 决策审批 | 伟壕 | 内部人力 | 兼职参与 |
| **人力总计** | | **0元额外成本** | 全部内部调配 |

### 11.5 预算汇总

| 方案 | 一次性投入 | 月运营成本 | 3个月总成本 | 对比SaaS方案 |
|------|-----------|-----------|------------|-------------|
| **最小方案** | ~6,550元 | ~55元 | ~6,715元 | SaaS方案20人团队月费3000-8000元，3个月9000-24000元 |
| **推荐方案** | ~12,050元 | ~55元 | ~12,215元 | |
| **旗舰方案** | ~19,050元 | ~55元 | ~19,215元 | |

> **对比结论**：本地部署方案即使选择旗舰配置（~19,050元），3个月总成本也低于SaaS方案最低档（~9,000元/3月）。且本地部署数据完全自主可控，长期使用边际成本趋近于零。

---

> **文档版本**：v3.0（技术落地版）
> **创建日期**：2026-07-10
> **下一步**：伟壕审批 → 启动第1阶段实施
> **文档依据**：需求调研文档v2.0 + 架构设计文档v1.0

---

> 本内容由 Coze AI 生成，请遵循相关法律法规及《人工智能生成合成内容标识办法》使用与传播。
