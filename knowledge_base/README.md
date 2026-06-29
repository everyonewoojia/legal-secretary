# 法务小秘 — 知识库 (knowledge_base)

## 目录作用

本目录为法务小秘系统的**领域知识库**，为 AI Agent 层提供合同起草、谈判分析、风险审查所需的领域知识。所有知识文件以结构化 JSON 格式存储，后续可接入 FAISS 向量索引实现语义检索（RAG）。

## 目录结构

```
knowledge_base/
├── README.md                          # 本文件
├── index.json                         # 知识库索引清单（各知识源元信息）[TODO]
├── templates/                         # 合同结构化模板（5 类）
│   ├── technical_service_contract.json  # 技术服务合同
│   ├── purchase_contract.json           # 采购合同
│   ├── labor_contract.json              # 劳动合同
│   ├── cooperation_agreement.json       # 合作协议
│   └── nda_contract.json                # 保密协议
├── clauses/                           # 条款级知识
│   └── bottom_line_rules.json          # 底线策略规则库（6 类风险）
└── legal_docs/                        # 法律知识库（Markdown 摘要）
    ├── 民法典合同编摘要.json            # 民法典合同编核心条文（JSON 格式）
    ├── contract_law_summary.md         # 合同法通用规则知识摘要
    ├── labor_contract_law_summary.md   # 劳动法/劳动合同知识摘要
    ├── confidentiality_summary.md      # 商业秘密与保密义务知识摘要
    ├── dispute_resolution_summary.md   # 争议解决（管辖/仲裁/诉讼）知识摘要
    └── risk_review_rules.md            # 谈判风险审查规则库（9 类核心风险）
```

## 5 类合同模板说明

模板采用统一 JSON Schema，每类模板包含以下字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `contract_type` | string | 类型标识（如 `technical_service`） |
| `display_name` | string | 中文展示名称 |
| `description` | string | 模板适用场景与范围说明 |
| `required_fields` | array | 必填要素列表 |
| `sections` | array | 合同条款模板数组，每条含 `title`（条款标题）和 `content_template`（内容模板，占位符用 `[____]` 标记） |
| `clauses` | array | 结构化条款数组（用于RAG/合同生成），每条含 `id`、`title`、`content`（使用 `{{变量名}}` 占位符）、`variables`（占位变量列表）、`risk_tips`（该条款的常见风险提示） |
| `risk_points` | array | 该类合同的常见法律风险点，每条含：`risk_type`（类型）、`risk_description`（风险描述）、`suggestion`（防范建议） |
| `generation_notes` | string | AI 生成时的额外注意事项 |

### 现有模板（为旧版合同生成流程使用）

`agent/contract_agent.py` 加载的模板文件位于 `knowledge_base/templates/` 下，共用以下 5 个旧版文件名：`tech_service.json`、`procurement.json`、`employment.json`、`cooperation.json`、`non_disclosure.json`。新版模板文件名（带 `_contract` 后缀）为中期汇报展示用途，结构更完整，后续可将旧版模板逐步迁移对齐。

## `clauses/` 底线策略规则库

`clauses/bottom_line_rules.json` 是结构化底线策略规则库，覆盖 **10 类核心风险**：管辖法院变更、违约金比例过高、付款节点不明确、验收标准模糊、保密期限过短、单方解除权过宽、责任限制不合理、不可抗力范围异常、知识产权归属不清、交付义务过重。

### JSON 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 规则唯一标识（如 `jurisdiction_change`） |
| `name` | string | 规则中文名称 |
| `description` | string | 风险描述 |
| `applicable_contract_types` | array | 适用合同类型列表 |
| `trigger_keywords` | array | 触发关键词，用于 Agent 文本匹配 |
| `risk_level` | string | 风险等级：`high` / `medium` / `low` |
| `review_points` | array | 审查要点列表 |
| `bottom_line` | string | 底线断言——不可退让的条件 |
| `recommended_response` | string | 推荐应对策略（简短） |
| `negotiation_strategy` | object | 三档谈判话术：`firm_position` / `compromise_position` / `fallback_position` |
| `demo_disclaimer` | string | 每条款均标注实训 Demo 声明 |

### 与 `risk_review_rules.md` 的关系

- `legal_docs/risk_review_rules.md`（Markdown 格式）用于**人工阅读和展示**，覆盖 9 类规则
- `clauses/bottom_line_rules.json`（JSON 格式）用于**程序化读取**，被 RiskAgent / NegotiationAgent 加载使用，覆盖 10 类规则
- `templates/*.json` 中的 `risk_points` 字段扩展至合同类型维度的风险描述，三者配合使用——`bottom_line_rules` 提供底线断言，`risk_review_rules.md` 提供审查上下文，`risk_points` 提供场景化背景
- 后续可作为 FAISS 向量化素材：每条规则的 `description`、`review_points`、`bottom_line` 字段均可作为 embedding 分块输入

## FAISS 向量索引构建

当前版本：通过 `scripts/build_vector_index.py` 实现完整的 Embedding + FAISS 索引构建流程。

### 向量化素材来源

| 来源 | 格式 | 内容 | 分块策略 |
|------|------|------|----------|
| `templates/*.json` 的 `clauses[]` | JSON | 结构化条款含 risk_tips | 每条 clause 为一个分块 |
| `templates/*.json` 的 `risk_points[]` | JSON | 合同类型维度风险点 | 每条 risk_point 为一个分块 |
| `templates/*.json` 的 `generation_notes` | JSON | 生成注意事项 | 每文件一个文本块 |
| `clauses/bottom_line_rules.json` | JSON | 底线策略断言 | 每条规则为一个分块 |
| `legal_docs/*.md` | Markdown | 法律知识摘要和审查规则 | 按二级标题（##）分块 |

### 构建步骤

```bash
# 1. 安装依赖
pip install sentence-transformers faiss-cpu

# 2. 构建向量索引
python3 scripts/build_vector_index.py
```

输出文件：
- `knowledge_base/faiss_index.bin` — FAISS 向量索引（IndexFlatIP，384 维）
- `knowledge_base/index_metadata.json` — 索引元信息（来源文件、块类型、标题、预览）

### 搜索演示

```bash
# 搜索 top 5 相似知识块
python3 scripts/search_knowledge_base.py "违约金过高怎么办"
python3 scripts/search_knowledge_base.py "管辖法院可以在哪里约定"
python3 scripts/search_knowledge_base.py "试用期最长多久"
```

搜索结果包含：`score`（相似度）、`source_file`（来源文件）、`chunk_type`（块类型）、`title`（块标题）、`text_preview`（内容预览）。

### 索引元信息（index.json）

`knowledge_base/index.json` 描述了所有知识源文件清单、类型、用途和向量化状态，可配合 FAISS 索引进行可视化展示。

### 技术细节

- Embedding 模型：`paraphrase-multilingual-MiniLM-L12-v2`（支持中文，384 维）
- FAISS 索引：`IndexFlatIP`（内积索引，等价于余弦相似度）
- Embedding 归一化：构建时已对向量进行 L2 归一化
- 块类型：`template_clause` / `template_risk_point` / `template_generation_note` / `bottom_line_rule` / `legal_doc_section`

## 当前版本限制

- **实训 Demo 用途**：本知识库所有模板、规则、法律摘要**仅作为实训 Demo 模板，不替代专业律师意见**。实际使用中须由执业律师审核。
- 法律条文摘要仅覆盖民法典合同编、劳动法、商业秘密保护、争议解决等基础领域，未覆盖全部法律法规。
- 底线策略规则库和风险审查规则库仅覆盖常见风险场景，不能替代针对具体合同的全面审查。
- **索引结果仅供辅助检索**，不构成法律意见，实际合同审查须由执业律师完成。
- 模板中的 `content_template` 使用 `[____]` 占位符，AI 生成时需替换为实际内容。
- `legal_docs/` 下的 Markdown 文件通过本地检索使用，暂未接入后端 RAG 接口。
