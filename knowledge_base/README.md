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

## 风险点体系

`clauses/bottom_line_rules.json` 覆盖 6 类核心风险：管辖法院、违约金比例、保密期限、责任限制、付款条件、不可抗力。`templates/*.json` 中的 `risk_points` 字段扩展至合同类型维度的风险描述，两者配合使用——`bottom_line_rules` 提供底线断言，`risk_points` 提供场景化背景。

## RAG / FAISS 接入

当前版本：`backend/app/services/rag_service.py` 通过文件系统遍历直接读取 JSON 模板文件，无向量检索。

### 向量化素材来源

| 来源 | 格式 | 内容 | 分块策略 |
|------|------|------|----------|
| `templates/*.json` 的 `sections[].content_template` | JSON | 各类合同模板条款 | 每条 sections 为一个分块 |
| `templates/*.json` 的 `clauses[]` | JSON | 结构化条款含 risk_tips | 每条 clause 为一个分块 |
| `templates/*.json` 的 `risk_points[]` | JSON | 合同类型维度风险点 | 每条 risk_point 为一个分块 |
| `legal_docs/*.md` | Markdown | 法律知识摘要和审查规则 | 按二级标题（##）分块 |
| `clauses/bottom_line_rules.json` | JSON | 底线策略断言 | 每条规则为一个分块 |
| `legal_docs/民法典合同编摘要.json` | JSON | 合同法条文摘要 | 每条条文为一个分块 |

### 后续接入计划（见 `scripts/build_vector_index.py`）

1. 遍历 `knowledge_base/` 下所有 JSON 和 Markdown 文件，识别各文件格式按上述策略分块
2. 使用 `sentence-transformers`（`paraphrase-multilingual-MiniLM-L12-v2`）生成 768 维 embedding
3. 写入 FAISS `IndexFlatIP`（内积索引），保存到 `knowledge_base/faiss_index.bin`
4. 查询时：query → embedding → FAISS 搜索 → 返回 top_k 片段（含来源文件路径和 chunk 类型）

## 当前版本限制

- **实训 Demo 用途**：本知识库所有模板、规则、法律摘要**仅作为实训 Demo 模板，不替代专业律师意见**。实际使用中须由执业律师审核。
- 法律条文摘要仅覆盖民法典合同编、劳动法、商业秘密保护、争议解决等基础领域，未覆盖全部法律法规。
- 底线策略规则库和风险审查规则库仅覆盖常见风险场景，不能替代针对具体合同的全面审查。
- 尚未接入向量检索（FAISS），当前为文件级直接读取。
- 模板中的 `content_template` 使用 `[____]` 占位符，AI 生成时需替换为实际内容。
- `legal_docs/` 下的 Markdown 文件暂未接入 Agent 调用，后续可通过 RAG 实现语义检索增强。
