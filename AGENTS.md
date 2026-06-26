# 法务小秘 — AI 合同起草与谈判辅助系统

## 项目概况
面向中小企业的 AI 智能体合同起草与谈判辅助系统。前端已搭建完成，可对接后端 API 进行联调。

## 技术栈
- **前端**: Vue 3 + Vite 8 + Vue Router 4 + Pinia 3 + Element Plus + Axios + marked
- **后端**: FastAPI (Python) — 已实现全部 API
- **AI 层**: Python Agent 体系（orchestrator / dialogue / contract / risk / negotiation）
- **数据库**: SQLite (开发) / MySQL (生产)
- **大模型**: 阿里云 DashScope (通义千问)，通过 OpenAI 兼容 SDK 调用

## 📌 各分支并行开发状态

| 分支 | 状态 | 说明 |
|------|------|------|
| `master` | 已整合 | 合并 feat-wlf（前端完整实现）+ feat-agent（AI Agent 层 + API 契约定义），当前 HEAD 包含对契约 JSON 的语法修复 |
| `feat-wlf` (前端) | 已完成 | 完整前端 8 个页面、3 个 Pinia store、路由守卫、模拟数据层，已合入 master |
| `feat-agent` | 开发中 | Agent 层实现与契约定义，后端 API 路由已接入 Agent 调用 |
| `feat-zhy` (知识库) | 开发中 | 模板/知识库/RAG/测试/文档方向。当前 HEAD：合同模板初始化与 clauses 填充 |

## 目录结构
```
legal-secretary/
├── frontend/                     # Vue 3 前端项目
│   ├── src/
│   │   ├── api/                  # axios 实例 + 模块化 API 封装 + 模拟接口
│   │   │   ├── index.js          # axios 实例 + SSE 流式聊天 (chatStream)，默认导出 http
│   │   │   ├── contract.js       # 合同 API：createSession / generateContract / exportDraft / analyze
│   │   │   ├── negotiation.js    # 谈判 API：analyzeNegotiation / exportReport
│   │   │   └── mock/
│   │   │       └── authMock.js   # 登录/注册/用户管理的模拟接口
│   │   ├── components/           # 公共组件
│   │   ├── views/
│   │   │   ├── Home.vue          # 首页（功能入口卡片）
│   │   │   ├── Login.vue         # 登录页面（手机号+密码）
│   │   │   ├── Register.vue      # 注册页面（手机号+验证码）
│   │   │   ├── ContractDraft.vue # 合同起草（三栏布局：类型选择 + SSE 对话 + 预览）
│   │   │   ├── NegotiationAnalyze.vue # 谈判分析（两栏：差异列表 + 风险详情）
│   │   │   ├── Negotiate.vue     # 旧版谈判分析（已废弃）
│   │   │   ├── Profile.vue       # 个人中心（信息编辑/修改密码）
│   │   │   └── Admin.vue         # 后台管理（用户列表/禁用/改角色）
│   │   ├── stores/
│   │   │   ├── user.js           # 用户认证状态（login/register/logout/权限检查）
│   │   │   ├── contract.js       # 合同会话/消息/slots/起草状态
│   │   │   └── negotiation.js    # 谈判分析状态（diffList / caseId / selectedRisk）
│   │   ├── router/index.js       # 7 条路由 + beforeEach 守卫（auth/role 检查）
│   │   ├── App.vue               # 根组件（认证后显示顶部导航栏 + 头像下拉菜单）
│   │   ├── main.js               # 入口（注册 Pinia/Router/ElementPlus）
│   │   └── style.css
│   ├── index.html
│   ├── vite.config.js            # 代理 /api → localhost:8000
│   └── package.json
├── backend/                      # FastAPI 后端项目
│   └── app/
│       ├── main.py               # FastAPI 入口，注册 4 个路由模块
│       ├── api/                   # REST API 路由
│       │   ├── auth.py           # /api/v1/auth/* 登录/注册
│       │   ├── contract.py       # /api/v1/contract/* 会话/对话/生成/导出/谈判分析
│       │   ├── admin.py          # /api/v1/admin/* 用户管理/日志/LLM 配置（stub）
│       │   └── rag.py            # /api/v1/rag/search 知识库检索
│       ├── core/                 # 配置与基础设施
│       │   ├── config.py         # pydantic-settings 读取 .env
│       │   ├── database.py       # SQLAlchemy async engine + session
│       │   ├── llm.py            # OpenAI 兼容 SDK 封装（流式/非流式）
│       │   └── response.py       # 统一响应格式 {code, message, data}
│       ├── models/               # SQLAlchemy ORM 模型
│       │   ├── user.py           # User 模型（含角色/状态）
│       │   └── contract.py       # ContractSession / ChatMessage / ContractDraft / NegotiationCase / RiskItem
│       ├── schemas/              # Pydantic 请求/响应 DTO
│       │   ├── common.py         # 通用分页等
│       │   └── contract.py       # CreateSession / Chat / Generate / Export / Negotiate 请求
│       └── services/             # 业务逻辑层
│           ├── contract_generator.py  # 调用 LLM 生成合同初稿
│           ├── diff_service.py        # diff-match-patch 文本差异比对
│           ├── risk_service.py        # LLM 风险分析 + 入库
│           ├── export_service.py      # DOCX/PDF 导出
│           └── rag_service.py         # FAISS 向量检索（stub）
├── agent/                        # AI Agent 层（进程内调用）
│   ├── orchestrator.py           # 主控 Agent：意图识别、槽位追踪、任务路由
│   ├── dialogue_agent.py         # 多轮对话引导：槽位抽取、校验与追问
│   ├── contract_agent.py         # 合同初稿生成：模板匹配 + LLM 填充
│   ├── risk_agent.py             # 风险分析：差异比对 + AI 识别 + 分类
│   ├── negotiation_agent.py      # 谈判话术生成：强硬/折中两套方案
│   └── prompts/                  # System Prompt 模板
│       ├── dialogue_system.txt
│       ├── contract_generation.txt
│       └── risk_analysis.txt
├── api-contracts/                # Agent ↔ Backend API 契约（JSON Schema）
│   ├── index.json                # 契约索引，定义 6 个接口的元信息
│   ├── chat/dialogue.json        # 对话接口契约
│   ├── generation/contract_generation.json  # 合同生成接口契约
│   ├── risk/risk_analysis.json   # 风险分析接口契约
│   ├── risk/negotiation_reply.json          # 批量话术生成接口契约
│   ├── risk/single_reply.json               # 单条话术生成接口契约
│   └── rag/rag_search.json       # 知识库检索接口契约（stub）
├── knowledge_base/               # 领域知识库
│   ├── templates/                # 5 类合同结构化模板（JSON 条款数组）
│   │   ├── tech_service.json              # (旧版 stub)
│   │   ├── procurement.json               # (旧版 stub)
│   │   ├── employment.json                # (旧版 stub)
│   │   ├── cooperation.json               # (旧版 stub)
│   │   ├── non_disclosure.json            # (旧版 stub)
│   │   ├── technical_service_contract.json # 技术服务合同（完整模板，含 clauses）
│   │   ├── purchase_contract.json          # 采购合同（完整模板，含 clauses）
│   │   ├── labor_contract.json             # 劳动合同（完整模板，含 clauses）
│   │   ├── cooperation_agreement.json      # 合作协议（完整模板，含 clauses）
│   │   └── nda_contract.json               # 保密协议（完整模板，含 clauses）
│   ├── clauses/
│   │   └── bottom_line_rules.json  # 底线策略规则库
│   └── legal_docs/
│       └── 民法典合同编摘要.json     # 法规摘要
├── tests/                        # 测试（空）
├── docs/                         # 文档（空）
└── requirements.txt              # Python 依赖（FastAPI / SQLAlchemy / openai / ...）
```

## 后端 API（已完成，可直接对接）
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/auth/login` | POST | 登录，返回 JWT token |
| `/api/v1/auth/register` | POST | 注册 |
| `/api/v1/contract/session` | POST | 创建合同会话 |
| `/api/v1/contract/chat/stream` | POST | SSE 流式多轮对话 |
| `/api/v1/contract/generate` | POST | 生成合同初稿 |
| `/api/v1/contract/{id}/export` | GET | 导出 DOCX |
| `/api/v1/contract/negotiate/analyze` | POST | 谈判风险分析（支持文件上传）|
| `/api/v1/rag/search` | POST | RAG 知识库检索 |
| `/api/v1/admin/*` | GET/POST | 后台管理 |

**响应格式**: `{code: 0, message: "success", data: {...}}`

## 已完成的工作 (2025-06-23)
1. 前端脚手架搭建：Vue 3 + Vite + Router + Pinia + Axios + Element Plus
2. API 层重构：axios 实例 + 拦截器（自动注入 JWT token），`chatStream()` 用 fetch + ReadableStream 消费 SSE
3. 合同 Pinia store (`src/stores/contract.js`)：管理 sessionId / messages / draftId / contractText / slots
4. 合同起草页面 (`ContractDraft.vue`)：三栏布局（类型选择 + SSE 流式对话 + 合同预览/下载）
5. 谈判分析旧版 (`Negotiate.vue`)：粘贴文本 → AI 分析差异比对 → 风险列表展开详情

## 已完成的工作 (2025-06-24)
1. API 层拆分：新建 `api/contract.js`，`api/negotiation.js`，`api/index.js` 保持重导出兼容
2. 合同起草页面重写 (`ContractDraft.vue`)：完整三栏布局（左侧类型选择/已采集要素，中间 SSE 对话，右侧合同预览），支持格式切换、loading 状态、错误提示
3. 新建谈判分析页面 (`NegotiationAnalyze.vue`)：两栏布局，文件上传 + 文本输入 + 差异列表（红/橙/蓝风险标签）→ 右侧风险详情（依据/底线/话术）+ 复制话术 + 导出报告
4. 新建谈判 Pinia store (`stores/negotiation.js`)：管理 caseId / diffList / selectedRisk / fileList 等状态
5. 所有页面构建通过 (vite build)

## 已完成的工作 (2025-06-25)
1. 登录/注册流程：新建 `Login.vue`（手机号+密码，表单校验，错误提示，演示账号提示），新建 `Register.vue`（手机号+验证码+密码+确认密码，模拟验证码倒计时，注册后跳转登录）
2. 后台管理页面重写 (`Admin.vue`)：用户列表表格（头像/用户名/手机号/角色/状态/注册时间），禁用/启用用户、修改角色操作（带确认弹窗），不可操作自己
3. 用户 Pinia store (`stores/user.js`)：isLoggedIn / userInfo / token 状态，login / register / logout / checkPermission 方法，localStorage 持久化
4. 模拟接口 (`api/mock/authMock.js`)：预设管理员(13800000000/admin123)和普通用户(13800000001/user123)，注册用户默认 user 角色，所有数据 localStorage 持久化
5. 路由守卫 (`router/index.js`)：beforeEach 守卫 — 未登录跳转 /login，已登录访问登录页跳转首页，/admin 需 admin 角色
6. App.vue 重写：登录后显示深色顶部导航栏（法务小秘 Logo + 合同起草/谈判分析/后台管理），右侧显示用户头像+用户名+退出登录
7. 所有页面构建通过 (vite build)

## 已完成的工作 (2025-06-26)
1. 新建个人中心页面 (`Profile.vue`)：左右布局（侧边导航 + 内容区），个人信息编辑（昵称/头像/脱敏手机号/角色/注册时间）、修改密码（当前密码/新密码/确认密码校验）
2. 头像下拉菜单：App.vue 导航栏右侧头像改为 el-dropdown，包含个人中心/后台管理(admin)/退出登录
3. 用户 store (`stores/user.js`) 新增 `updateProfile()` 和 `changePassword()` 方法
4. 模拟接口 (`authMock.js`) 新增 `mockUpdateProfile()` 和 `mockChangePassword()`
5. 路由新增 `/profile`，配置 requiresAuth 守卫
6. 所有页面构建通过 (vite build)

## 已完成的工作 (AI Agent 层 & 后端集成)
1. AI Agent 体系搭建：`AgentOrchestrator`（意图识别/槽位追踪/任务路由）+ `DialogueAgent`（5 类合同槽位抽取）+ `ContractAgent`（模板匹配 + LLM 填充）+ `RiskAgent`（差异分析 + 风险分类）+ `NegotiationAgent`（强硬/折中两套话术生成）
2. Prompt 工程：3 个 system prompt 模板（对话引导/合同生成/风险分析），覆盖 5 类合同（技术服务/采购/劳动/合作/保密）的必填槽位定义与追问映射
3. API 路由实现：`/auth/*`（JWT 登录/注册）、`/contract/*`（会话创建/SSE 流式对话/合同生成/DOCX 导出/谈判分析）、`/rag/search`（知识库检索）、`/admin/*`（用户管理/日志/LLM 配置）
4. 后端基础设施：SQLAlchemy async ORM（5 张表）、pydantic-settings 配置管理、统一响应格式 `{code, message, data}`、CORS 中间件
5. API 契约定义：`api-contracts/index.json` 维护 6 个 Agent ↔ Backend 接口的 JSON Schema 契约（dialogue / generation / risk_analysis / negotiation_reply / single_reply / rag_search），含优先级与状态标注
6. 谈判话术生成重构：话术生成统一收拢至 `NegotiationAgent`，由 `AgentOrchestrator.process_risk_negotiation()` 编排 RiskAgent + NegotiationAgent 的串联调用
7. 视图层知识库：5 类合同 JSON 结构化模板、底线策略规则库、民法典合同编摘要
8. 代码合并与修复：手动合并 feat-agent 分支，修复契约 JSON 文件中的尾部逗号等语法错误，放宽 faiss-cpu 版本约束

## 已完成的工作 (feat-zhy / 张怀月 / ops-test)
1. 合同模板初始化与 clauses 填充：在 `knowledge_base/templates/` 下新建 5 个完整合同模板 JSON 文件，保留旧版 stub 文件不做删除
2. `technical_service_contract.json` — 技术服务合同，10 条 clauses，覆盖服务内容、验收、知识产权等核心条款
3. `purchase_contract.json` — 采购合同，11 条 clauses，覆盖采购标的、质量、质保售后等条款
4. `labor_contract.json` — 劳动合同，12 条 clauses，覆盖工时、报酬、社保、竞业限制等法定必备条款
5. `cooperation_agreement.json` — 合作协议，13 条 clauses，覆盖投入、收益分配、退出机制等条款
6. `nda_contract.json` — 保密协议，10 条 clauses，覆盖保密范围、例外情形、信息归还等条款
7. 每个 clause 包含 `id` / `title` / `content`（`{{变量名}}` 占位符）/ `variables` / `risk_tips`，用于中期汇报展示和后续 RAG/合同生成
8. 所有模板文件 JSON 格式验证通过，未改动 backend、frontend、agent 目录
9. `knowledge_base/README.md` 同步更新，补充 `clauses` 字段说明

## 已完成的工作 (feat-zhy / 第二轮 / legal_docs 法律知识库)
1. 在 `knowledge_base/legal_docs/` 下新增 5 个 Markdown 法律知识库文件，覆盖合同法通用规则、劳动法、保密法律、争议解决、风险审查规则五大领域
2. `contract_law_summary.md` — 合同法通用规则摘要（合同订立/效力/履行/违约/解除 + 6 类风险）
3. `labor_contract_law_summary.md` — 劳动合同知识摘要（试用期/工资/社保/解除/竞业限制 + 5 类风险）
4. `confidentiality_summary.md` — 商业秘密与保密义务知识摘要（构成要件/义务来源/违约竞合/例外情形 + 6 类风险）
5. `dispute_resolution_summary.md` — 争议解决知识摘要（诉讼管辖/仲裁/劳动争议/诉讼时效/送达 + 7 类风险）
6. `risk_review_rules.md` — 谈判风险审查规则库（9 类核心风险：管辖/违约金/付款/验收/保密/解约/责任限制/不可抗力/知识产权，每条含风险描述、审查标准、强硬/折中/底线三档谈判话术）
7. 每个 Markdown 文件采用统一结构：适用场景 > 核心法律要点 > 常见风险表 > RAG 摘要文本 > 注意事项，均标注"仅作为实训 Demo 知识库素材"声明
8. `knowledge_base/README.md` 同步更新：legal_docs 目录说明、向量化素材来源表、RAG 分块策略、版本限制补充
9. 所有修改未涉及 backend、frontend、agent 目录

## 已完成的工作 (feat-zhy / 第三轮 / 中期汇报文档)
1. 新建 `docs/ops_test_midterm_report.md` — 中期汇报工作说明文档，包含成员身份、已完成工作、成果支撑说明、可展示文件清单、后续计划、风险与限制、版本记录
2. 文档结构清晰，适合中期汇报时照着讲解，未夸大项目完成度，未声称提供正式法律意见

## 路由表
| 路径 | 页面 | 访问权限 |
|------|------|---------|
| `/login` | 登录 | 游客（已登录则跳转首页）|
| `/register` | 注册 | 游客 |
| `/` | 首页 | 需登录 |
| `/draft` | 合同起草 | 需登录 |
| `/negotiate` | 谈判分析 | 需登录 |
| `/profile` | 个人中心 | 需登录 |
| `/admin` | 后台管理 | 需 admin 角色 |

## 环境注意事项
- 项目在 WSL (Ubuntu) 下开发，Node.js 需用 **Linux 版**（Windows 版会因 UNC 路径问题导致 Vite 报错）
- Linux Node.js 安装在 `~/.local/node/bin`，已加入 `.bashrc` 的 PATH
- 启动前端: `cd ~/projects/legal-secretary/frontend && npm run dev`
- 启动后端: `cd ~/projects/legal-secretary && uvicorn backend.app.main:app --reload --port 8000`
- 前端代理配置：`vite.config.js` 中 `/api` → `http://localhost:8000`
- 需配置 `.env` 文件（参考 `.env.example`），填入 `LLM_API_KEY`（阿里云 DashScope）
- 当前分支: `feat-zhy`

## 待办/后续可做
- [ ] 完善登录流程（当前 Login 页面已存在，且 Api 层已配置 JWT 拦截器）
- [ ] 增强合同预览的 Markdown 渲染样式
- [ ] 移动端适配
- [ ] 合同保存/历史记录管理
- [ ] 多轮对话上下文优化
