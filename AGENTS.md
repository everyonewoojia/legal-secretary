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
| `master` | 已整合 | 合并 feat-wlf（前端完整实现）+ feat-agent（AI Agent 层 + API 契约定义），当前 HEAD 包含对契约 JSON 的语法修复+ RAG 检索与 Agent 集成调用链 |
| `feat-wlf` (前端) | 调试完成 | 前端 8 页面 + Pinia store + 路由守卫 + 真实后端对接；增强后端 mock（字段驱动对话/合同模板 slots 填充/风险分析/话术），全端点手动测试通过 |
| `feat-agent` | 开发中 | Agent 层实现与契约定义，后端 API 路由已接入 Agent 调用 |
| `feat-jzx` (后端集成) | 开发中 | 后端 FastAPI 完整实现（37+ API/9 ORM/10 Services/6 Routers）+ 全栈联调。当前 HEAD：合并 feat-agent + 项目结构优化 |
| `feat-zhy` (知识库) | 开发中 | 模板/知识库/RAG/测试/文档方向。当前 HEAD：联调前接口一致性分析完成，产出 check/todo/bug 三份文档 |

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
│       ├── main.py               # FastAPI 入口，注册 6 个路由模块
│       ├── routers/               # REST API 路由
│       │   ├── api.py            # 路由聚合器，挂载 6 个子路由
│       │   ├── auth.py           # /api/v1/auth/* 登录/注册/改密
│       │   ├── users.py          # /api/v1/users/* 个人信息/头像
│       │   ├── contracts.py      # /api/v1/contracts/* 会话/对话/生成/版本/风险
│       │   ├── negotiation.py    # /api/v1/negotiation/* 文件上传/差异比对/AI分析/话术
│       │   ├── rag.py            # /api/v1/rag/* 法律法规/合同模板 CRUD
│       │   └── admin.py          # /api/v1/admin/* 用户管理/API密钥/日志/统计
│       ├── core/                 # 配置与基础设施
│       │   ├── config.py         # pydantic-settings 读取 .env
│       │   ├── database.py       # SQLAlchemy engine + session
│       │   ├── security.py       # JWT 创建/验证 + bcrypt 密码哈希
│       │   └── deps.py           # get_current_user 依赖注入
│       ├── models/               # SQLAlchemy ORM 模型（9 张表）
│       │   ├── base.py           # TimestampMixin 基类
│       │   ├── user.py           # User 模型
│       │   ├── contract.py       # Contract / ContractVersion / RiskAssessment
│       │   ├── contract_type.py  # ContractType
│       │   ├── template.py       # ContractTemplate
│       │   ├── knowledge_base.py # LawArticle（含 embedding 字段）
│       │   ├── risk.py           # (保留)
│       │   ├── audit.py          # AuditLog
│       │   └── api_key.py        # ApiKeyConfig
│       ├── schemas/              # Pydantic 请求/响应 DTO（6 文件）
│       │   ├── common.py         # 统一响应 {code, message, data} + 分页
│       │   ├── user.py           # 登录/注册/个人信息/改密
│       │   ├── contract.py       # 会话/对话/生成/合同 CRUD
│       │   ├── negotiation.py    # 差异项/风险项/话术请求
│       │   ├── rag.py            # 法律法规/模板 CRUD
│       │   └── admin.py          # 用户管理/API密钥/审计日志
│       ├── services/             # 业务逻辑层（10 个 Service）
│       │   ├── ai_service.py     # OpenAI SDK 封装 + mock 回退（流式/非流式）
│       │   ├── auth_service.py   # 注册/登录
│       │   ├── user_service.py   # 用户信息 CRUD
│       │   ├── contract_service.py  # 合同 CRUD + AI 对话/生成
│       │   ├── dialogue_service.py  # 5 类合同 System Prompt + 槽位提取
│       │   ├── negotiation_service.py  # 风险分析 + 话术生成
│       │   ├── admin_service.py  # 用户管理/API密钥/日志/统计
│       │   ├── rag_service.py    # 法律法规/模板 CRUD
│       │   ├── rag_engine.py     # ChromaDB 向量检索 + SQL 回退
│       │   └── file_service.py   # 文件上传/文本提取
│       └── utils/                # 工具函数
│           ├── file_parser.py    # DOCX 解析（PDF stub）
│           ├── text_diff.py      # difflib 文本差异比对
│           └── sse.py            # SSE 格式化辅助
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

## 后端 API（当前重构后）
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/auth/login` | POST | 登录，返回 JWT token |
| `/api/v1/auth/register` | POST | 注册 |
| `/api/v1/auth/sms-code` | POST | 发送验证码（演示模式返回 123456）|
| `/api/v1/users/me` | GET/PUT | 获取/更新个人信息 |
| `/api/v1/contracts/types` | GET | 合同类型列表 |
| `/api/v1/contracts/chat/{type_id}` | POST | SSE 流式多轮对话 |
| `/api/v1/contracts/generate/{type_id}` | POST | 生成合同初稿（非流式）|
| `/api/v1/contracts/generate-stream/{type_id}` | POST | SSE 流式生成合同 |
| `/api/v1/contracts/` | GET/POST | 合同列表 / 创建合同 |
| `/api/v1/contracts/{id}` | GET/DELETE | 合同详情 / 删除 |
| `/api/v1/contracts/{id}/download` | GET | 下载合同 |
| `/api/v1/contracts/{id}/versions` | GET | 合同版本列表 |
| `/api/v1/negotiation/upload/{contract_id}` | POST | 上传对方修改稿 |
| `/api/v1/negotiation/diff/{contract_id}` | GET | 文本差异比对 |
| `/api/v1/negotiation/ai-analyze/{contract_id}` | POST | AI 风险分析 |
| `/api/v1/negotiation/risks/{contract_id}` | GET | 风险列表 |
| `/api/v1/negotiation/counter-argument` | POST | 生成谈判话术 |
| `/api/v1/admin/users` | GET | 用户列表（分页）|
| `/api/v1/admin/users/{id}/toggle-active` | PUT | 禁用/启用用户 |
| `/api/v1/admin/users/{id}/role` | PUT | 修改用户角色 |
| `/api/v1/admin/api-keys` | GET/PUT | API Key 管理 |
| `/api/v1/admin/logs` | GET | 系统日志 |
| `/api/v1/admin/stats` | GET | 系统统计 |

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

## 已完成的工作 (2025-06-27)
1. API 层全面切换：新建 `api/auth.js`（认证 + 用户管理 + 管理员 API），重写 `api/contract.js`（合同 types / chat / generate-stream / CRUD / download），重写 `api/negotiation.js`（upload / diff / ai-analyze / counter-argument）
2. SSE 流式重写：`api/index.js` 移除 mockChatStream，改用 `fetch` + `ReadableStream` 消费真实后端 SSE（`chatStream` + `generateStream` 两个函数）
3. `stores/user.js`：移除全部 mock 引入，调用真实 HTTP API；登录后自动 `getProfile()` 获取用户信息；映射 `nickname` → `username` 兼容现有视图；admin 用户列表适配后端分页格式
4. `stores/contract.js`：移除 sessionId 概念，改用 typeId（后端 integer）；`startSession` 从后端拉取合同类型列表；`sendMessage` 使用真实 SSE；`generateContract` 使用 generate-stream SSE
5. `stores/negotiation.js`：适配新后端流程（创建合同 → 上传文件 → 对比差异 → AI 分析 → 获取风险 → 加载话术），`loadCounterArgument` 选中风险时异步加载话术
6. `ContractDraft.vue`：`store.sessionId` → `store.typeId`，`store.contractType` → `store.contractCode`，下载改用 `contractApi.download` 支持文件下载回退
7. `NegotiationAnalyze.vue`：导入 `contractApi` 替代 mock，选中风险时调用 `loadCounterArgument` 获取话术，导出报告改用文本文件下载

## 已完成的工作 (2025-06-27 / 第二轮 / 后端 mock 增强 & Bug 修复)
1. 后端 mock (`backend/app/services/ai_service.py`) 丰富至与前前端 mock 等质：新增 5 类合同模板（CONTRACT_TEMPLATES）、5 类合同多轮对话流（CHAT_FLOWS）+ 默认流、slots 抽取正则（SLOT_EXTRACTION_MAP）、5 条详细风险项（MOCK_RISK_ITEMS，含 clause_location / risk_level / description / suggestion / legal_basis）、话术生成 mock（返回 JSON 格式 plan_a/plan_b）
2. `_mock_chat` 流程重写：根据 system prompt 中【合同类型】自动匹配对话流；根据 `ai_turns` 自动推进对话轮次；`generate` / `risk` / `counter-argument` / `dialogue` 四路分支智能路由；`_mock_generate_contract` 按合同类型返回对应模板；`_mock_risk_analysis` 返回 5 条 Mock 风险项；`_mock_counter_argument` 返回 JSON 格式话术
3. 修复 `generate_stream` 路径：`_mock_chat` 关键字检测补充 `合同生成专家` 和 `输出合同全文`，使合同生成 mock 模式返回合同模板而非对话文本
4. 修复 counter-argument mock 返回非 JSON 导致 500：`_mock_chat` 检测 `plan_a` / `plan_b` 关键词后返回 `_mock_counter_argument()`（JSON 格式）
5. 修复 negotiation store 文本上传路径：当无文件上传时，将 `modifiedText` 转换为 Blob/File 通过 upload 端点上载为版本 2，解决"版本数不足"错误
6. 修复 `UserInfo` 无 `username` 字段兼容：`normalizeUser(data)` 映射 `nickname` → `username`
7. 修复 `persist()` 空 userInfo 覆盖 token 问题：分开检查 token 和 userInfo 后再存入 localStorage
8. 修复 axios 拦截器响应 400+ 时 `detail` 字段未捕获：error 拦截器补充 `body?.detail`
9. build 通过（仅 @vueuse/core PURE 注释警告，非阻塞）

## 已完成的工作 (2025-06-27 / 第三轮 / 全流程修复 & TXT 上传支持)
1. 后端 mock 增强补全：`ai_service.py` 追加 5 类合同完整模板（CONTRACT_TEMPLATES）、5 类合同多轮对话流（CHAT_FLOWS）、slots 抽取正则、5 条详细风险项、话术 JSON 格式返回
2. 修复 `_mock_chat` 关键检测缺失：补充 `合同生成专家` / `输出合同全文` 匹配 `generate` 路径；追加 `plan_a` / `plan_b` 匹配 `counter-argument` 路径
3. 修复 `chat_stream` mock 模式下 `_mock_stream` 为 async generator 但被 `for` 迭代的 TypeError：改为 `async for`
4. 修复前端 negotiation store 文本模式无文件上传时"版本数不足"：pasted text 转为 Blob/File 通过 upload 上传为 version 2
5. 后端 `FileService` / `file_parser.py` 增加 `.txt` 文件上传解析支持（parse_txt + ext check）
6. 后端 `seed_data` 启动时自动初始化演示账号 + 5 类合同类型
7. 后端 `law_secretary.db` 清理后自动重建（删旧库重启即可）
8. 所有 API 端点手动测试通过：login / types / chat SSE / generate-stream / create / upload / diff / ai-analyze / risks / counter-argument

## 已完成的工作 (2025-06-27 / 第四轮 / Mock 智能对话增强 & 修复)
1. **Mock 多轮对话升级为字段驱动**：`_mock_chat` 改为提取全量 user 消息的 slots → 按 FIELD_LIST 检测缺失字段 → 仅问缺失项 + 确认已填内容；去掉旧固定回复，改为动态追问
2. **合同生成填充 slots**：`_mock_generate_contract` 从 generation prompt JSON 提取 `collected_fields` → `_fill_placeholders` 替换占位符（甲方/乙方/金额/交付物/付款节点/验收标准 → 模板中对应位置）
3. **修复 `ack` 覆盖 Bug**：`last_slots` 循环改为 `ack_parts` 列表累积 + `"，"` join，支持多字段同时提取（如"乙方是XX，合同金额是50万"）
4. **修复对话 JSON 与 SSE 不兼容**：移除 `_mock_chat` 的 JSON 返回格式（含 slots），改为纯文本对话，避免 SSE 字符流渲染原始 JSON 字符串
5. **清理冗余代码**：移除 `_all_slots_from_messages` 重复定义、`_extract_slots_from_json` 未使用函数；仅从 user 消息提取 slots（不再解析 system prompt 的模板占位符）
6. **修复生成时 slots 获取失败**：`_all_slots_from_messages` 恢复对 system 消息的 JSON 提取（`from_system=True` 参数），保障 `generate-stream` 端点正确填充 collected_fields 到合同
7. **扩展正则匹配**：甲方 regex 增加 `采购方` 关键词，覆盖采购合同场景
8. **清理 `FIELD_QUESTIONS` 硬编码前缀**：去掉各问题的"已了解"/"已记录"/"好的/"明白了"等前缀，避免与动态 `ack` 重复
9. **build 通过**，全流程手动测试通过

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

## 已完成的工作 (2026-06-27) — RAG 检索与 Agent 集成调用链
1. **知识库向量化导入脚本** (`scripts/ingest_knowledge_base.py`)：遍历 `knowledge_base/` 下 5 个模板 JSON + 5 个法律文档 MD，按策略分块（clauses/sections/risk_points/## 标题），写入 SQLite `LawArticle` 表（180 条记录）+ ChromaDB 同步
2. **RAG 搜索 API 端点** (`POST /api/v1/rag/search`)：新增 `schemas/rag.py` 中 `RagSearchRequest/Response`，`routers/rag.py` 中 `/search` 端点，`RagService.search_all()` 三层搜索链（ChromaDB 向量 → SQLite keyword → 知识库磁盘文件 fallback）
3. **Agent 层 LLM 入口桥接**：新建 `backend/app/core/llm.py` 代理 `ai_service.py`，修复 `agent/` 层对 `backend.app.core.llm` 的 5 处引用
4. **Agent RAG 客户端**：新建 `agent/rag_client.py`，提供 `search()` / `search_legal_basis()` / `search_clause_template()` / `search_risk_rules()`，支持有 DB 和无 DB 两种模式
5. **RAG 注入 Agent 调用链**：
   - `AgentOrchestrator.process()` — 在 dialogue/generate 分流前执行 RAG 检索，填充 `session["rag_context"]`
   - `AgentOrchestrator.process_risk_negotiation()` — 注入法律知识到 RiskAgent+NegotiationAgent 上下文
   - `DialogueAgent.run()` — 在 LLM prompt 中加入法律知识，提升追问质量
   - `ContractAgent.run()` — 主动 RAG 查询增强合同模板填充
   - `RiskAgent.run()` — 注入法条依据提升风险识别准确率
   - `NegotiationAgent._generate_single()` — 注入底线规则和法律依据到话术生成 prompt
6. **后端服务层 RAG 增强**：
   - `ContractService.ai_generate_contract()` — 改用 `search_all()` 做多字段语义检索
   - `DialogueService.generate_contract()` — 接受并传递 RAG `law_context`
   - `NegotiationService.ai_analyze_risks()` — 获取合同类型后执行 RAG 搜索，注入风险分析 prompt
7. **前端 API 层改造**：`api/index.js` 中 `chatStream()` 尝试真实 SSE 端点 + mock fallback，`api/contract.js`/`api/negotiation.js` 所有函数 try real API + mock fallback，Store 层 (`contract.js`/`negotiation.js`) 异步调用 `ragSearch()` 获取法律上下文

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

## 已完成的工作 (feat-zhy / 第四轮 / 底线策略规则库)
1. 新建 `knowledge_base/clauses/bottom_line_rules.json` — 结构化底线策略规则库，定义 10 类核心风险：管辖法院变更、违约金比例过高、付款节点不明确、验收标准模糊、保密期限过短、单方解除权过宽、责任限制不合理、不可抗力范围异常、知识产权归属不清、交付义务过重
2. 每条规则包含 11 个字段：id / name / description / applicable_contract_types / trigger_keywords / risk_level / review_points / bottom_line / recommended_response / negotiation_strategy（三档话术：强硬/折中/底线）/ demo_disclaimer
3. 规则风险等级分布：high 6 条（管辖/违约金/付款/解除/责任限制/知识产权），medium 4 条（验收/保密/不可抗力/交付）
4. 更新 `legal_docs/risk_review_rules.md` — 增加与 `bottom_line_rules.json` 的对应关系表
5. 更新 `knowledge_base/README.md` — 增加 `clauses/` 目录说明、`bottom_line_rules.json` 字段说明
6. 更新 `docs/ops_test_midterm_report.md` — 增加 2.4 节（底线策略规则库）和 2.5 节（配套文档更新）
7. 所有修改未涉及 backend、frontend、agent 目录

## 已完成的工作 (feat-zhy / 第五轮 / FAISS 向量索引构建)
1. 新建 `scripts/build_vector_index.py` — 遍历 knowledge_base/ 下全部 JSON 和 Markdown 文件，提取文本块，使用 sentence-transformers 生成 384 维 embedding，构建 FAISS IndexFlatIP 索引
2. 新建 `scripts/search_knowledge_base.py` — 加载 FAISS 索引，支持命令行查询，返回 Top 5 相似知识块
3. 新建 `knowledge_base/index.json` — 知识库源文件清单，描述 11 个源文件的类型、用途和向量化状态
4. 更新 `.gitignore` — 忽略 `knowledge_base/faiss_index.bin` 等可重新生成的二进制产物
5. 更新 `knowledge_base/README.md` — 替换 FAISS 接入计划为实际构建步骤和搜索演示用法
6. 更新 `docs/ops_test_midterm_report.md` — 增加 2.6 节（FAISS 向量索引构建）
7. 所有修改未涉及 backend、frontend、agent 目录

## 已完成的工作 (feat-zhy / 第六轮 / 基础测试体系)
1. 新建 `tests/` 目录及其 6 个测试文件，覆盖我负责模块的关键文件结构验证：
   - `tests/conftest.py` — pytest 共享 fixture（project_root / knowledge_base_dir / templates_dir / legal_docs_dir / clauses_dir / scripts_dir + load_json 辅助函数）
   - `tests/test_templates_schema.py` — 5 个模板 JSON 的结构字段完整性校验（字段存在性、clauses 非空、clause 字段完整、variables 为数组、risk_tips 非空），使用 @pytest.mark.parametrize 参数化
   - `tests/test_bottom_line_rules.py` — 底线策略规则库验证（规则数量 >= 10、11 个必填字段、risk_level 枚举约束、negotiation_strategy 三档话术结构、demo_disclaimer 含实训字样）
   - `tests/test_index_manifest.py` — index.json 源文件存在性验证（自动兼容 sources/files/items 等不同顶层字段名、path 文件真实存在、vectorized 为布尔值）
   - `tests/test_vector_scripts.py` — 脚本存在性和基础结构验证（main 入口、faiss/sentence_transformers 引用），不下载 Hugging Face 模型，不重构索引
   - `tests/test_metadata_basic.py` — index_metadata.json 元数据格式验证（顶层兼容 list/dict、可追溯字段、合法 chunk_type）
2. 新建 `pyproject.toml` — 配置 pytest 发现规则（`testpaths = ["tests"]`, `python_files = ["test_*.py"]`, `addopts = "-q"`）
3. 修改 `requirements.txt` — 追加 `pytest>=8.0.0`、`pytest-cov>=5.0.0`，未删除已有依赖
4. 更新 `docs/ops_test_midterm_report.md` — 新增 2.7 节（基础测试体系）和 v4.0 版本记录
5. 所有修改未涉及 backend、frontend、agent 目录，未修改知识库正文和模板内容，未执行 git 操作

## 已完成的工作 (feat-zhy / 第七轮 / 联调前接口一致性分析)
1. 完成全链路接口一致性分析，检查后端实际路由（`backend/app/routers/*.py`、`backend/app/main.py`、`backend/app/routers/api.py`）、前端 API 调用（`frontend/src/api/`、`frontend/src/stores/`、`frontend/src/views/`）、api-contracts 契约三方之间的一致性
2. 发现 **5 个高优先级问题**（RAG 搜索路径不存在、合同 session 模型不兼容、生成入参不匹配、下载格式不匹配、注册字段名不一致）、**6 个中优先级问题**、**3 个低优先级问题**
3. 新增 `docs/pre_integration_api_check.md` — 联调前接口一致性检查报告，含后端路由表、前端 Mock 状态、分级问题清单、建议修复方向和归属
4. 新增 `docs/integration_todo.md` — 按 6 个模块（认证/用户/合同/谈判/RAG/管理）列出联调前待办，含当前状态、阻塞问题、前端/后端/文档待改、验收标准
5. 新增 `docs/bug_list.md` — Bug 记录表模板和初始 11 条 Bug（B-001 ~ B-011），含编号/模块/复现步骤/优先级/负责人/状态
6. 确认以下事实：
   - 前端当前全部使用 Mock数据，无真实 HTTP 调用
   - api-contracts 是 Agent 进程内调用契约，不是前端 HTTP API 契约
   - 合同起草前后端模型差异最大，需要前端 store 重写
7. 所有修改未涉及 backend、frontend、agent 业务代码，未执行 git 操作

## 已完成的工作 (feat-jzx / 后端集成 & 结构优化 · 2026-06-26)
1. **后端 FastAPI 完整实现** — 37+ API 端点，覆盖 6 组路由（auth/users/contracts/negotiation/rag/admin），含 JWT 认证、请求校验、统一响应格式
2. **9 个 ORM 模型** — User / Contract / ContractVersion / ContractType / ContractTemplate / RiskAssessment / LawArticle / AuditLog / ApiKeyConfig，含完整关系映射与索引
3. **10 个 Service 层** — ai_service（OpenAI SDK + mock 回退）/ auth_service / user_service / contract_service / dialogue_service（5 类合同 Prompt + 槽位抽取）/ negotiation_service / admin_service / rag_service / rag_engine（ChromaDB + SQL 回退）/ file_service
4. **项目结构重构** — 统一调整为 `backend/app/` 结构，整理 agents、contracts、knowledge_base 目录
5. **合并 feat-agent** — 将 AI Agent 层（5 个 Agent + 3 套 Prompt）和后端路由代码纳入 feat-jzx
6. **AI 开发规范** — 新增 `.opencode/constraints.md`，定义全栈联调契约、进度同步、垃圾文件防护规则
7. **AGENTS.md 同步改版** — 项目概况、完整目录树、API 端点表、路由表、分支状态看板、多人工作日志

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

## 待办/后续可做
- [ ] 填写 `.env` 中的 `LLM_API_KEY`（阿里云 DashScope），AI 层才能跑通
- [ ] 修复 `agent/contract_agent.py` 模板文件名不匹配（代码读 `tech_service.json`，实际文件名为 `technical_service_contract.json`）
- [ ] 前端从 Mock 切换为调用真实后端 API（`api/contract.js`、`api/negotiation.js`、`chatStream()`）
- [ ] 实现真正的 DOCX/PDF 导出（当前 download 端点仅返回 JSON）
- [ ] 实现 `utils/file_parser.py` 的 PDF 解析（当前抛 NotImplementedError）
- [x] 补全基础测试（`tests/` 目录 — 模板结构、底线规则、索引清单、元数据、脚本基础结构验证已覆盖）
- [ ] 补全后端 Service 层和 API 层测试（需等 backend 模块稳定后补充）
- [ ] 补全前端组件测试（需等 frontend 模块稳定后补充）
- [x] 构建 FAISS 向量索引（`knowledge_base/faiss_index.bin` 已构建）
- [ ] 增强合同预览的 Markdown 渲染样式
- [ ] 移动端适配
- [ ] 前端从 Mock 切换为真实 HTTP 调用（见 `docs/integration_todo.md` 按模块推进）
- [ ] 合同起草 store 重写（适配后端 type_id + collected_fields 模型）
- [ ] 谈判分析流程确认（多步流程 vs. 合并端点）
- [ ] 合同下载方案确认（文件流 vs. 文本下载）
- [ ] api-contracts 目录定位说明更新
