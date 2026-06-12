# PRD-008：AI 直播与数字人互动系统

> **文档版本**：v3.0  
> **优先级**：P2（探索）  
> **负责部门**：市场部 / 运营部  
> **创建日期**：2026-06-12  
> **最后更新**：2026-06-12  
> **状态**：草稿

---

## 1. 产品概述

### 1.1 背景与问题

| 维度 | 现状 |
|------|------|
| **痛点来源** | 市场部、运营部 |
| **当前方式** | 真人直播成本高、时长有限、无法 24 小时覆盖 |
| **核心问题** | 直播人力成本高、内容无法沉淀、用户互动体验单一 |
| **业务影响** | 直播转化率低、用户粘性不足 |
| **量化损失** | 真人直播单场成本 5000-20000 元；非直播时段流量浪费 |

### 1.2 产品定义

**一句话描述**：利用 AI 数字人技术，实现 24 小时不间断直播，自动介绍产品、回答用户问题、引导下单，降低直播成本、提升覆盖时长。

**产品愿景**：构建 AI 驱动的直播带货体系，实现"全天候、低成本、高转化"的直播运营。

**产品载体**：本产品为运行在钉钉平台上的**钉钉AI表格应用**，利用钉钉AI表格的多维表格能力、自动化流程、AI字段识别、权限管理等原生功能，实现直播数据的管理、分析与协作。

### 1.3 目标用户

| 角色 | 用户画像 | 使用场景 | 核心诉求 | 使用频率 |
|------|----------|----------|----------|----------|
| 直播运营 | 25-35 岁，直播管理 | 直播内容策划 | 降低直播成本 | 每日 |
| 市场人员 | 28-40 岁，营销策划 | 品牌推广 | 扩大品牌曝光 | 每周 |
| 客服人员 | 22-35 岁，客户服务 | 直播互动 | 自动回答用户问题 | 每日 |

---

## 2. 业务流程

### 2.1 AI 直播主流程

```
直播前准备
  ├─ 配置数字人形象
  ├─ 准备商品脚本
  └─ 设置直播场景
        │
        ▼
AI 数字人直播
  ├─ 自动介绍商品
  ├─ 实时回答用户问题
  ├─ 引导用户下单
  └─ 定时推送优惠信息
        │
        ▼
直播数据记录（钉钉AI表格）
  ├─ 观看人数
  ├─ 互动数据
  ├─ 转化数据
  └─ 用户问题汇总
        │
        ▼
直播后分析
  ├─ 生成直播报告
  ├─ 优化话术脚本
  └─ 用户问题知识库更新
```

### 2.2 数字人互动流程

```
用户发送问题
        │
        ▼
NLP 理解用户意图
  ├─ 商品咨询
  ├─ 价格咨询
  ├─ 活动咨询
  └─ 其他问题
        │
        ▼
知识库匹配
  ├─ 匹配成功 → 生成回答
  └─ 匹配失败 → 转人工客服
        │
        ▼
数字人呈现回答
  ├─ 语音播报
  ├─ 文字展示
  └─ 商品卡片推送
        │
        ▼
用户反馈
  ├─ 满意 → 继续互动
  └─ 不满意 → 优化知识库
```

---

## 3. 功能需求

### 3.1 功能清单

| 功能ID | 功能名称 | 优先级 | 描述 | 开发人日 |
|--------|----------|--------|------|----------|
| F-001 | 数字人形象 | P0 | 配置和管理数字人形象 | 5 |
| F-002 | 脚本管理 | P0 | 创建和管理直播脚本 | 3 |
| F-003 | 实时互动 | P0 | 自动回答用户问题 | 10 |
| F-004 | 商品推荐 | P0 | 智能推荐相关商品 | 5 |
| F-005 | 直播推流 | P0 | 推流到直播平台 | 5 |
| F-006 | 数据统计 | P1 | 直播数据统计 | 3 |
| F-007 | 知识库管理 | P1 | 管理问答知识库 | 3 |
| F-008 | 多平台支持 | P2 | 支持多个直播平台 | 5 |

### 3.2 用户故事

#### Epic 1：数字人直播

| 故事ID | 用户故事 | 验收标准 | 优先级 |
|--------|----------|----------|--------|
| US-001 | 作为运营，我希望配置数字人形象 | 支持多种形象选择 | P0 |
| US-002 | 作为运营，我希望创建直播脚本 | 支持模板和自定义 | P0 |
| US-003 | 作为运营，我希望数字人自动介绍商品 | 语音自然流畅 | P0 |

#### Epic 2：实时互动

| 故事ID | 用户故事 | 验收标准 | 优先级 |
|--------|----------|----------|--------|
| US-004 | 作为用户，我希望在直播中提问并获得回答 | 回答准确率 ≥ 80% | P0 |
| US-005 | 作为用户，我希望看到商品推荐 | 推荐相关性高 | P0 |
| US-006 | 作为运营，我希望查看互动数据 | 实时统计 | P1 |

### 3.3 数字人能力要求

| 能力 | 要求 | 说明 |
|------|------|------|
| 语音合成 | 自然度 ≥ 90% | 接近真人语音 |
| 口型同步 | 延迟 ≤ 200ms | 口型与语音同步 |
| 表情动作 | 支持 20+ 种 | 丰富表情和手势 |
| 实时渲染 | 帧率 ≥ 30fps | 流畅画面 |

### 3.4 Prompt 设计（问答生成）

```
系统提示词：
你是一个专业的直播带货助手。请根据用户问题，生成简洁、有吸引力的回答。

商品信息：{product_info}
促销活动：{promotion_info}
用户问题：{user_question}

请生成：
1. 简洁回答（≤ 50 字）
2. 商品卖点（≤ 3 个）
3. 引导下单话术

输出格式：
{
  "answer": "...",
  "highlights": ["...", "...", "..."],
  "cta": "..."
}
```

---

## 4. 技术方案

### 4.1 技术选型

| 组件 | 技术方案 | 说明 |
|------|----------|------|
| 数字人引擎 | 硅基智能 / 腾讯智影 | 成熟的数字人技术 |
| 语音合成 | 阿里云 TTS / 讯飞 | 高质量语音合成 |
| 推流服务 | OBS / FFmpeg | 推流到直播平台 |
| 数据存储 | 钉钉AI表格 | 业务数据存储 |
| 知识库 | Elasticsearch | 快速问答检索 |

### 4.2 数据模型

#### 钉钉AI表格表结构设计

**表1：数字人形象表**
| 字段名 | 字段类型 | 说明 |
|--------|----------|------|
| 形象编号 | 文本 | 自动生成 |
| 形象名称 | 文本 | 形象名称 |
| 形象类型 | 单选 | 真人/卡通/虚拟 |
| 预览图 | 附件 | 形象预览 |
| 状态 | 单选 | 启用/禁用 |
| 创建时间 | 系统字段 | 自动记录 |

**表2：直播脚本表**
| 字段名 | 字段类型 | 说明 |
|--------|----------|------|
| 脚本编号 | 文本 | 自动生成 |
| 脚本名称 | 文本 | 脚本名称 |
| 商品 | 关联 | 关联商品表 |
| 脚本内容 | 多行文本 | 详细内容 |
| 话术要点 | 多行文本 | 关键话术 |
| 时长 | 数字 | 预计时长（秒） |
| 状态 | 单选 | 启用/禁用 |
| 创建人 | 人员 | 钉钉用户 |
| 创建时间 | 系统字段 | 自动记录 |

**表3：直播记录表**
| 字段名 | 字段类型 | 说明 |
|--------|----------|------|
| 直播编号 | 文本 | 自动生成 |
| 直播标题 | 文本 | 直播标题 |
| 数字人形象 | 关联 | 关联数字人形象表 |
| 直播平台 | 单选 | 抖音/快手/视频号/其他 |
| 开始时间 | 日期时间 | 开始时间 |
| 结束时间 | 日期时间 | 结束时间 |
| 观看人数 | 数字 | 峰值观看人数 |
| 互动次数 | 数字 | 互动总次数 |
| 转化订单数 | 数字 | 转化订单数 |
| 转化金额 | 数字 | 转化金额 |
| 状态 | 单选 | 待直播/直播中/已结束 |
| 创建时间 | 系统字段 | 自动记录 |

**表4：互动记录表**
| 字段名 | 字段类型 | 说明 |
|--------|----------|------|
| 直播 | 关联 | 关联直播记录表 |
| 用户ID | 文本 | 用户标识 |
| 问题内容 | 文本 | 用户问题 |
| 回答内容 | 文本 | 数字人回答 |
| 问题类型 | 单选 | 商品/价格/活动/其他 |
| 回答来源 | 单选 | 知识库/AI生成/人工 |
| 用户反馈 | 单选 | 满意/一般/不满意 |
| 互动时间 | 日期时间 | 互动时间 |
| 创建时间 | 系统字段 | 自动记录 |

**表5：知识库表**
| 字段名 | 字段类型 | 说明 |
|--------|----------|------|
| 问题 | 文本 | 用户问题 |
| 标准问题 | 文本 | 标准化问题 |
| 回答 | 文本 | 标准回答 |
| 关联商品 | 关联 | 关联商品表 |
| 标签 | 多选 | 问题标签 |
| 使用次数 | 数字 | 累计使用次数 |
| 满意度 | 数字 | 平均满意度 |
| 状态 | 单选 | 启用/禁用 |
| 创建时间 | 系统字段 | 自动记录 |

#### 核心表结构（备用关系型数据库方案）

```sql
-- 数字人形象表
CREATE TABLE avatar (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    avatar_no       VARCHAR(50) UNIQUE NOT NULL COMMENT '形象编号',
    avatar_name     VARCHAR(100) NOT NULL COMMENT '形象名称',
    avatar_type     VARCHAR(50) COMMENT 'REAL/CARTOON/VIRTUAL',
    preview_url     VARCHAR(500) COMMENT '预览图URL',
    status          TINYINT DEFAULT 1,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 直播脚本表
CREATE TABLE live_script (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    script_no       VARCHAR(50) UNIQUE NOT NULL COMMENT '脚本编号',
    script_name     VARCHAR(200) NOT NULL COMMENT '脚本名称',
    product_id      BIGINT COMMENT '关联商品ID',
    content         TEXT COMMENT '脚本内容',
    key_points      JSON COMMENT '话术要点',
    duration        INT COMMENT '预计时长(秒)',
    status          TINYINT DEFAULT 1,
    creator         VARCHAR(50) COMMENT '创建人',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 直播记录表
CREATE TABLE live_record (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    live_no         VARCHAR(50) UNIQUE NOT NULL COMMENT '直播编号',
    live_title      VARCHAR(200) NOT NULL COMMENT '直播标题',
    avatar_id       BIGINT COMMENT '数字人形象ID',
    platform        VARCHAR(50) COMMENT 'DOUYIN/KUAISHOU/VIDEO_ACCOUNT',
    start_time      DATETIME COMMENT '开始时间',
    end_time        DATETIME COMMENT '结束时间',
    viewers         INT DEFAULT 0 COMMENT '观看人数',
    interactions    INT DEFAULT 0 COMMENT '互动次数',
    order_count     INT DEFAULT 0 COMMENT '转化订单数',
    order_amount    DECIMAL(10, 2) DEFAULT 0 COMMENT '转化金额',
    status          VARCHAR(20) DEFAULT 'SCHEDULED' COMMENT 'SCHEDULED/LIVE/ENDED',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_time (start_time, end_time)
);

-- 互动记录表
CREATE TABLE interaction_log (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    live_id         BIGINT NOT NULL COMMENT '直播ID',
    user_id         VARCHAR(50) COMMENT '用户ID',
    question        TEXT COMMENT '问题内容',
    answer          TEXT COMMENT '回答内容',
    question_type   VARCHAR(50) COMMENT 'PRODUCT/PRICE/PROMOTION/OTHER',
    answer_source   VARCHAR(50) COMMENT 'KB/AI/MANUAL',
    satisfaction    VARCHAR(20) COMMENT 'SATISFIED/NEUTRAL/UNSATISFIED',
    interact_time   DATETIME COMMENT '互动时间',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_live (live_id),
    INDEX idx_user (user_id)
);

-- 知识库表
CREATE TABLE knowledge_base (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    question        TEXT NOT NULL COMMENT '问题',
    standard_question TEXT COMMENT '标准化问题',
    answer          TEXT NOT NULL COMMENT '回答',
    product_id      BIGINT COMMENT '关联商品ID',
    tags            JSON COMMENT '标签',
    use_count       INT DEFAULT 0 COMMENT '使用次数',
    avg_satisfaction DECIMAL(5, 4) COMMENT '平均满意度',
    status          TINYINT DEFAULT 1,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FULLTEXT INDEX ft_question (question, standard_question)
);
```

### 4.3 API 规格

#### 创建直播 API

```
POST /api/v1/live/create
Content-Type: application/json

请求参数：
{
  "live_title": "周末水果特惠直播",
  "avatar_no": "A001",
  "platform": "DOUYIN",
  "start_time": "2026-06-14 10:00:00",
  "script_no": "S001"
}

响应：
{
  "code": 200,
  "data": {
    "live_no": "L20260612001",
    "status": "SCHEDULED",
    "stream_url": "rtmp://xxx",
    "message": "直播已创建"
  }
}
```

#### 互动问答 API

```
POST /api/v1/live/interact
Content-Type: application/json

请求参数：
{
  "live_no": "L20260612001",
  "user_id": "user123",
  "question": "这个草莓多少钱？"
}

响应：
{
  "code": 200,
  "data": {
    "answer": "红颜草莓 300g 只要 29.9 元，新鲜直达，现在下单还包邮哦！",
    "highlights": ["当季新鲜", "产地直发", "坏果包赔"],
    "cta": "点击下方购物车，立即抢购！",
    "product_card": {
      "product_id": 2001,
      "product_name": "红颜草莓 300g/盒",
      "price": 29.9,
      "image_url": "https://xxx/strawberry.jpg"
    }
  }
}
```

#### 直播统计 API

```
GET /api/v1/live/statistics?live_no=L20260612001

响应：
{
  "code": 200,
  "data": {
    "live_no": "L20260612001",
    "duration": 7200,
    "viewers": 1500,
    "interactions": 320,
    "order_count": 45,
    "order_amount": 2680.00,
    "avg_watch_time": 180,
    "top_questions": [
      {"question": "草莓多少钱", "count": 28},
      {"question": "包邮吗", "count": 22}
    ]
  }
}
```

### 4.4 钉钉AI表格集成方案

#### 4.4.1 钉钉AI表格应用架构

本产品作为钉钉AI表格应用运行，利用钉钉开放平台提供的以下核心能力：

| 能力模块 | 用途 | 实现方式 |
|----------|------|----------|
| 多维表格 | 数据存储与管理 | 使用钉钉AI表格作为主数据存储 |
| 自动化流程 | 业务逻辑触发 | 配置自动化规则，实现直播任务调度 |
| 权限管理 | 数据访问控制 | 配置表格级、行级、列级权限 |
| 消息通知 | 推送提醒 | 通过钉钉机器人推送直播状态 |
| 连接器 | 外部系统集成 | 通过连接器调用数字人服务 |

#### 4.4.2 钉钉开放平台集成

**钉钉应用配置**：
- 应用类型：企业内部应用
- 运行平台：钉钉AI表格
- 权限范围：
  - `dingtalk:app:table:read` - 表格读取
  - `dingtalk:app:table:write` - 表格写入
  - `dingtalk:user:readonly` - 用户基本信息读取
  - `dingtalk:message:send_as_bot` - 消息发送

#### 4.4.3 前端技术适配

**运行环境要求**：
- 运行平台：钉钉客户端（iOS/Android）内置浏览器
- 技术框架：钉钉AI表格小程序框架（基于钉钉小程序技术栈）
- 兼容性要求：
  - iOS 13.0+
  - Android 8.0+
  - 钉钉客户端版本 6.5.0+

---

## 5. 测试方案

| 用例ID | 测试场景 | 预期结果 |
|--------|----------|----------|
| TC-001 | 数字人形象配置 | 形象加载正常 |
| TC-002 | 脚本管理 | 脚本创建和编辑正常 |
| TC-003 | 实时互动 | 回答准确率 ≥ 80% |
| TC-004 | 商品推荐 | 推荐相关性高 |
| TC-005 | 直播推流 | 推流稳定，延迟 ≤ 3 秒 |
| TC-006 | 数据统计 | 统计数据准确 |
| TC-007 | 知识库管理 | 问答匹配准确 |
| TC-008 | 钉钉AI表格集成 | 数据正确写入并可查询 |

---

## 6. 实施计划

| 阶段 | 时间 | 目标 |
|------|------|------|
| **阶段一：核心功能** | 第 1-6 周 | 数字人形象、脚本管理、推流 |
| **阶段二：互动功能** | 第 7-10 周 | 实时互动、商品推荐 |
| **阶段三：数据分析** | 第 11-12 周 | 数据统计、直播报告 |
| **阶段四：优化推广** | 第 13-16 周 | 性能优化、全面推广 |

---

## 7. 价值量化

| 维度 | 预期效果 |
|------|----------|
| **成本降低** | 直播成本降低 80%（从万元级降至千元级） |
| **覆盖时长** | 从每天 4-6 小时提升至 24 小时 |
| **转化率** | 预计提升至 3-5% |
| **用户互动** | 自动回答覆盖率 ≥ 80% |

---

## 8. 验收标准

| 验收项 | 指标 | 验收方法 |
|--------|------|----------|
| 数字人形象 | 自然度 ≥ 90% | 用户调研 |
| 语音合成 | MOS ≥ 4.0 | 语音质量评估 |
| 回答准确率 | ≥ 80% | 100 条测试集 |
| 推流稳定性 | 中断率 ≤ 1% | 压力测试 |
| 钉钉AI表格集成 | 数据正确读写 | 集成测试 |

---

## 9. 术语表

| 术语 | 说明 |
|------|------|
| 数字人 | 利用计算机图形学技术创建的虚拟人物形象 |
| TTS | Text-To-Speech，文本转语音 |
| RTMP | Real-Time Messaging Protocol，实时消息传输协议 |
| 知识库 | 存储问答对的数据结构 |
| 钉钉AI表格 | 钉钉平台提供的多维表格应用，支持AI字段、自动化流程等能力 |
| 钉钉开放平台 | 钉钉提供的应用开发平台，提供API和SDK |

---

## 10. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-06-12 | 初始版本 |
| v2.0 | 2026-06-12 | 扩写数字人能力、数据模型、API 规格、用户故事 |
| v3.0 | 2026-06-12 | 修正产品载体定位为钉钉AI表格应用，更新技术方案、运行环境、集成方案 |
