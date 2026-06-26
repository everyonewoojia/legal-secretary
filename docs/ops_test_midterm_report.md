# 法务小秘 — 中期汇报工作说明

> 作者：张怀月（zhy2006）
> 分支：feat-zhy
> 方向：ops-test / 模板 / RAG 知识库 / 测试 / 文档
> 日期：2026-06-26

---

## 一、成员身份与负责范围

| 项目 | 说明 |
|------|------|
| 成员 | 张怀月 |
| 开发分支 | `feat-zhy` |
| 负责方向 | 合同模板初始化、RAG 知识库搭建、法律文档整理、测试与文档 |
| 协作方式 | 独立开发，不与 `backend/`、`frontend/`、`agent/` 目录重叠 |

---

## 二、已完成工作

### 2.1 合同模板初始化与 clauses 填充

在 `knowledge_base/templates/` 下新建 5 个完整的合同模板 JSON 文件，保留旧版 stub 文件不做删除：

| 模板文件 | 合同类型 | clauses 数 | 核心覆盖 |
|----------|---------|-----------|---------|
| `technical_service_contract.json` | 技术服务合同 | 10 条 | 服务内容、验收、知识产权 |
| `purchase_contract.json` | 采购合同 | 11 条 | 采购标的、质量、质保售后 |
| `labor_contract.json` | 劳动合同 | 12 条 | 工时、报酬、社保、竞业限制 |
| `cooperation_agreement.json` | 合作协议 | 13 条 | 投入、收益分配、退出机制 |
| `nda_contract.json` | 保密协议 | 10 条 | 保密范围、例外情形、信息归还 |

每个 clause 包含：
- `id` — 条款唯一标识
- `title` — 条款中文标题
- `content` — 条款原文模板，使用 `{{变量名}}` 占位符
- `variables` — 占位变量列表
- `risk_tips` — 该条款的常见风险提示

所有模板 JSON 格式已通过验证。

### 2.2 法律知识库搭建

在 `knowledge_base/legal_docs/` 下新建 5 个法律知识库 Markdown 文件：

| 文件 | 领域 | 内容结构 |
|------|------|----------|
| `contract_law_summary.md` | 合同法通用规则 | 适用场景 → 核心法律要点（订立/效力/履行/违约/解除）→ 6 类风险表 → RAG 摘要文本 |
| `labor_contract_law_summary.md` | 劳动合同法 | 适用场景 → 核心要点（试用期/工资/社保/解除/竞业限制）→ 5 类风险表 → RAG 摘要文本 |
| `confidentiality_summary.md` | 商业秘密与保密义务 | 适用场景 → 核心要点（构成要件/义务来源/违约竞合/例外情形）→ 6 类风险表 → RAG 摘要文本 |
| `dispute_resolution_summary.md` | 争议解决 | 适用场景 → 核心要点（管辖/仲裁/劳动争议/时效/送达）→ 7 类风险表 → RAG 摘要文本 |
| `risk_review_rules.md` | 谈判风险审查规则 | 9 类核心风险，每条含风险描述、审查标准、强硬/折中/底线三档话术 |

每份文件均标注"仅作为实训 Demo 知识库素材，不替代专业律师意见"。

### 2.3 文档更新

- 更新 `knowledge_base/README.md` — 补充 `clauses` 字段说明、legal_docs 目录说明、向量化素材来源表、RAG 分块策略
- 更新 `AGENTS.md` — 新增分支状态表 `feat-zhy` 行、目录结构中的新模板和 legal_docs 文件、两轮工作记录

---

## 三、当前成果如何支撑项目

### 3.1 支撑合同智能起草
- 模板中的 `required_fields` 与 `agent/dialogue_agent.py` 的槽位定义对齐
- `clauses` 的结构化条款可作为合同初稿生成的输出范本
- 每个风险点（`risk_points`）可直接用于生成环节的风险预警

### 3.2 支撑谈判风险审查
- `risk_review_rules.md` 提供 9 类核心风险的审查标准和三档话术
- `clauses` 中的 `risk_tips` 为每一条款提供针对性的风险提示
- `legal_docs/` 下的法律摘要可为 Agent 提供法律依据引用

### 3.3 支撑后续 FAISS 向量化和 RAG 检索
- 各文件已按统一格式组织，便于按二级标题分块
- JSON 模板可直接解析为 embedding 输入
- Markdown 知识库可切分为语义块后索引

### 3.4 支撑中期汇报展示
- 5 个完整模板 + 5 个知识库文件可组合成演示链路
- 模板中的 `display_name`、`description` 字段可用于 UI 展示
- `risk_points` 和 `risk_tips` 可用于风险分析的界面呈现

---

## 四、可展示文件清单

```
knowledge_base/
├── README.md                              # 知识库说明文档（已更新）
├── templates/
│   ├── technical_service_contract.json     # 技术服务合同模板（10 clauses）
│   ├── purchase_contract.json              # 采购合同模板（11 clauses）
│   ├── labor_contract.json                 # 劳动合同模板（12 clauses）
│   ├── cooperation_agreement.json          # 合作协议模板（13 clauses）
│   └── nda_contract.json                   # 保密协议模板（10 clauses）
├── clauses/
│   └── bottom_line_rules.json              # 底线策略规则库
├── legal_docs/
│   ├── contract_law_summary.md             # 合同法知识摘要
│   ├── labor_contract_law_summary.md       # 劳动法知识摘要
│   ├── confidentiality_summary.md          # 保密法律知识摘要
│   ├── dispute_resolution_summary.md       # 争议解决知识摘要
│   └── risk_review_rules.md                # 谈判风险审查规则库
├── faiss_index.bin                         # [待生成] FAISS 向量索引
└── index.json                              # [待创建] 知识库索引清单
```

---

## 五、后续计划

| 序号 | 计划事项 | 优先级 | 依赖 |
|------|---------|--------|------|
| 1 | 继续标准化模板字段，与 agent/ 层 slot 定义对齐 | 高 | 与后端团队确认字段映射 |
| 2 | 配合后端接入 RAG 检索（`backend/app/services/rag_service.py`）| 高 | FAISS 构建脚本就绪 |
| 3 | 配合前端展示模板选择列表和风险提示面板 | 中 | 前端 UI 组件就绪 |
| 4 | 编写测试用例和测试报告（`tests/` 目录）| 中 | 后端 API 稳定 |
| 5 | 参与全栈联调与验收 | 中 | 前后端对接完成 |

---

## 六、风险与限制

1. **实训 Demo 属性**：所有模板、规则、法律摘要**仅作为实训 Demo 素材，不替代专业律师意见**。实际使用中须由执业律师审核。
2. **法律知识库覆盖有限**：当前仅覆盖合同法、劳动法、保密法律、争议解决等基础领域，未覆盖公司法、知识产权法、税法等其他相关法律法规。
3. **知识准确性**：法律条文摘要已尽力确保准确，但可能因法律法规更新、地方性差异等原因存在偏差，需定期校对和更新。
4. **向量检索尚未就绪**：FAISS 索引尚未构建，当前 RAG 接口仅支持文件级直接读取，语义检索能力待接入。
5. **联调进度**：当前 `feat-zhy` 分支独立开发，尚未与 `master` 分支或 `backend`、`frontend` 进行集成联调。
6. **模板格式兼容**：新模板与旧版 stub 文件（`tech_service.json` 等）格式不同，后续需确认过渡方案。

---

## 七、版本记录

| 版本 | 日期 | 内容 | 作者 |
|------|------|------|------|
| v1.0 | 2026-06-26 | 初始版本，记录合同模板初始化和 legal_docs 知识库搭建成果 | 张怀月 |
