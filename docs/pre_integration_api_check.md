# 联调前接口一致性检查报告

> 日期：2026-06-29
> 检查人：张怀月
> 目标：确认后端实际路由、前端预期 API、api-contracts 契约三方之间的一致性，为团队联调提供参考。

---

## 一、当前启动状态

| 项目 | 状态 | 命令 |
|------|------|------|
| 后端 FastAPI | ✅ 可启动 | `cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` |
| Swagger 文档 | ✅ 可访问 | `http://172.21.193.99:8000/docs` |
| 前端 Vite | ✅ 可启动 | `cd frontend && npm run dev -- --host 0.0.0.0` |
| 基础测试 | ✅ 54 passed | `python -m pytest tests/ -v` |
| 前后端联调 | ❌ 尚未开始 | 前端当前全部使用 Mock 数据，无真实 HTTP 调用 |

---

## 二、后端实际路由概览

路由前缀：`/api/v1`（定义于 `backend/app/core/config.py:7`，`API_V1_STR = "/api/v1"`）

### 认证 Auth

| 方法 | 路由 | 认证 | 请求体关键字段 |
|------|------|------|---------------|
| POST | `/auth/login` | ❌ | `phone`, `password` |
| POST | `/auth/register` | ❌ | `phone`, `password`, `nickname`, `company_name` |
| POST | `/auth/sms-code` | ❌ | `phone` |
| POST | `/auth/change-password` | ❌ | `old_password`, `new_password` |

### 用户管理 Users

| 方法 | 路由 | 认证 | 说明 |
|------|------|------|------|
| GET | `/users/me` | ✅ | 返回 `UserInfo`（含 `id, phone, nickname, avatar, gender, company_name, role, is_active`）|
| PUT | `/users/me` | ✅ | body: `nickname?`, `avatar?`, `gender?`, `company_name?` |
| POST | `/users/me/avatar` | ✅ | UploadFile |
| POST | `/users/me/change-password` | ✅ | body: `old_password`, `new_password` |

### 合同起草 Contracts

| 方法 | 路由 | 认证 | 说明 |
|------|------|------|------|
| GET | `/contracts/types` | ❌ | 返回合同类型列表 `[{id, name, code, description, sort_order}]` |
| POST | `/contracts/chat/{type_id}` | ❌ | SSE 流式对话，body: `{message, history}` |
| POST | `/contracts/generate/{type_id}` | ✅ | 非流式生成，body: `{collected_fields, title}` |
| POST | `/contracts/generate-stream/{type_id}` | ✅ | SSE 流式生成 |
| POST | `/contracts/` | ✅ | 创建合同，body: `{type_id, title, content}` |
| GET | `/contracts/` | ✅ | 列表，query: `status?` |
| GET | `/contracts/{id}` | ✅ | 详情 |
| DELETE | `/contracts/{id}` | ✅ | 删除 |
| GET | `/contracts/{id}/download` | ✅ | 下载（返回 `{content, title, format}`）|
| GET | `/contracts/{id}/versions` | ✅ | 版本列表 |
| GET | `/contracts/{id}/risks` | ✅ | 风险列表 |

### 谈判风险审查 Negotiation

| 方法 | 路由 | 认证 | 说明 |
|------|------|------|------|
| POST | `/negotiation/upload/{contract_id}` | ✅ | 上传对方修改稿 |
| GET | `/negotiation/diff/{contract_id}` | ✅ | 文本差异比对 |
| POST | `/negotiation/ai-analyze/{contract_id}` | ✅ | AI 风险分析 |
| GET | `/negotiation/risks/{contract_id}` | ✅ | 风险列表 |
| POST | `/negotiation/counter-argument` | ✅ | 生成话术，body: `{risk_id, negotiation_style}` |

### RAG 知识库

后端均为 `contract_type` 表 / `law_article` 表 / `contract_template` 表的 CRUD，**无 `/rag/search` 端点**。

| 方法 | 路由 | 说明 |
|------|------|------|
| POST/GET | `/rag/laws` | 法条 CRUD |
| GET/PUT/DELETE | `/rag/laws/{id}` | 单条法条 |
| POST/GET | `/rag/templates` | 合同模板 CRUD |
| GET/PUT/DELETE | `/rag/templates/{id}` | 单个模板 |

### 后台管理 Admin

| 方法 | 路由 | 说明 |
|------|------|------|
| GET | `/admin/users` | 用户列表（分页）`{items, total}` |
| PUT | `/admin/users/{id}/toggle-active` | 切换启用/禁用 |
| PUT | `/admin/users/{id}/role` | 修改角色 |
| GET | `/admin/api-keys` | API Key 列表 |
| PUT | `/admin/api-keys/{id}` | 更新 API Key |
| GET | `/admin/logs` | 审计日志 |
| GET | `/admin/stats` | 统计信息 |

---

## 三、前端当前 Mock 状态

前端全部关键 API 目前均使用 Mock 数据，真实 HTTP 调用极少：

| 文件 | Mock 函数 | 是否使用 HTTP |
|------|----------|-------------|
| `frontend/src/api/index.js` | `auth.login()` → `http.post('/auth/login')` | ✅ 部分有 HTTP |
| `frontend/src/api/index.js` | `auth.register()` → `http.post('/auth/register')` | ✅ 部分有 HTTP |
| `frontend/src/api/index.js` | `rag.search()` → `http.post('/rag/search')` | ✅ HTTP（但路径不存在）|
| `frontend/src/api/index.js` | `chatStream()` → `mockChatStream()` | ❌ 全 Mock |
| `frontend/src/api/contract.js` | `createSession()` → `mockCreateSession()` | ❌ 全 Mock |
| `frontend/src/api/contract.js` | `generateContract()` → `mockGenerateContract()` | ❌ 全 Mock |
| `frontend/src/api/contract.js` | `exportDraft()` → `mockExportDraft()` | ❌ 全 Mock |
| `frontend/src/api/negotiation.js` | `analyzeNegotiation()` → `mockAnalyzeNegotiation()` | ❌ 全 Mock |
| `frontend/src/api/negotiation.js` | `exportReport()` → `mockExportReport()` | ❌ 全 Mock |
| `frontend/src/stores/user.js` | 全部 → `authMock.js` 函数 | ❌ 全 Mock |

---

## 四、高优先级问题

### H1. RAG `/rag/search` 路径不存在

- **描述**: 前端 `api/index.js:28-30` 调用 `POST /api/v1/rag/search`，后端无此路由
- **后端实有**: `GET /api/v1/rag/laws?q=...`（RESTful 查询法条）
- **影响**: RAG 搜索功能完全不可用
- **文件**: `frontend/src/api/index.js`
- **建议修复方向**: 前端改为 `http.get('/rag/laws', { params: { q: query } })`
- **归属**: 前端修改

### H2. 合同对话模型不一致（session vs. type_id + collected_fields）

- **描述**: 前端 store 基于 `sessionId` 管理多轮对话，后端基于 `contracts/chat/{type_id}` 直接对话
- **前端流程**: `createSession(type)` → `sessionId` → `chatStream(sessionId, msg)` → `generateContract(sessionId)`
- **后端流程**: `GET /contracts/types` → `POST /contracts/chat/{type_id}` → `POST /contracts/generate/{type_id}`
- **影响**: 整个 `contractStore` 需要重写
- **文件**: `frontend/src/stores/contract.js`、`frontend/src/api/contract.js`、`frontend/src/api/index.js`
- **建议修复方向**: 前端的 `startSession` 改为调用 `GET /contracts/types` 获取类型 + 初始化对话状态；`sendMessage` 改为 `POST /contracts/chat/{type_id}` SSE 消费；`generateContract` 改为 `POST /contracts/generate/{type_id}`
- **归属**: 前端重构

### H3. 合同生成入参不匹配

- **描述**: 前端 `generateContract(sessionId)` 传 sessionId，后端需要 `type_id` + `collected_fields`
- **影响**: 生成合同无法正常工作
- **文件**: `frontend/src/stores/contract.js:80-93`
- **建议修复方向**: 前端 store 需要跟踪 `contractTypeId`（int）和 `collectedFields`（dict），调用时传递
- **归属**: 前端修改

### H4. 合同下载响应格式完全不匹配

- **前端期望**: `mockExportDraft` 返回 `{download_url: '#'}`，前端用 `window.open(download_url)`
- **后端实际**: `GET /contracts/{id}/download` 返回 `{content, title, format}`（纯文本内容）
- **影响**: 下载功能不可用
- **文件**: `frontend/src/views/ContractDraft.vue:227-239`
- **建议修复方向**: 需要前后端双方确认方案——后端改为返回文件流（真正的 DOCX 下载），或前端改为下载返回的 content 文本作为文件
- **归属**: 待前后端讨论

### H5. 注册字段名不匹配

- **前端 Mock**: `mockRegister({phone, password, username})` 使用 `username`
- **后端 Schema**: `RegisterRequest` 使用 `nickname` 和 `company_name`
- **影响**: 注册时字段名对不上，传入 `username` 会被后端忽略
- **文件**: `frontend/src/api/mock/authMock.js:67`、`frontend/src/stores/user.js:41`
- **建议修复方向**: 前端将 `username` 改为 `nickname`，并决定是否传 `company_name`
- **归属**: 前端修改

---

## 五、中优先级问题

### M1. 用户信息字段名不一致

- **前端 Mock**: `{id, phone, username, role, status, created_at}`
- **后端返回**: `{id, phone, nickname, avatar, gender, company_name, role, is_active, created_at}`
- **具体差异**:
  - `username` → `nickname`
  - `status`（'active'/'disabled'）→ `is_active`（true/false）
  - 后端额外有 `avatar`、`gender`、`company_name`
- **影响**: Profile.vue、Admin.vue 多处使用 `row.username`、`row.status`
- **文件**: `frontend/src/views/Profile.vue`、`frontend/src/views/Admin.vue`
- **建议修复方向**: 前端将所有 `row.username` 改为 `row.nickname`，`row.status === 'active'` 改为 `row.is_active === true`
- **归属**: 前端修改

### M2. 用户列表响应结构不一致

- **前端 Mock 返回**: 纯数组 `[{...}, {...}]`
- **后端实际**: `{items: [{...}, {...}], total: N}`
- **影响**: `Admin.vue` 的 `userList.value = await store.fetchUserList()` 不能直接得到数组
- **文件**: `frontend/src/views/Admin.vue:80-88`、`frontend/src/stores/user.js:58-60`
- **建议修复方向**: store 内改为获取 `res.data.items`
- **归属**: 前端修改

### M3. 用户状态切换机制不一致

- **前端 Mock**: `toggleUserStatus(userId)` → 本地切换 `status` 字段
- **后端**: `PUT /admin/users/{id}/toggle-active` → 切换 `is_active`
- **影响**: 切换后前端无法正确反映状态
- **文件**: `frontend/src/views/Admin.vue`（第 36-43、48-52、92-94 行）
- **建议修复方向**: 前端改为调用 `PUT /admin/users/{id}/toggle-active` 后刷新列表
- **归属**: 前端修改

### M4. 两个 `/change-password` 端点冗余

- **描述**: 后端 auth 模块和 users 模块都有一个改密码端点，前者无认证，后者有认证
- **无认证**: `POST /auth/change-password`（`backend/app/routers/auth.py:38-41`）
- **有认证**: `POST /users/me/change-password`（`backend/app/routers/users.py:44-54`）
- **建议**: 前端应使用带认证的 `POST /users/me/change-password`，后端可考虑删除无认证版本
- **归属**: 待后端确认

### M5. 谈判风险分析流程不匹配

- **前端 Mock**: 一次 `analyzeNegotiation(FormData)` 调用返回全部结果（`diff_list`）
- **后端流程**:
  1. `POST /negotiation/upload/{contract_id}`（上传文件）
  2. `GET /negotiation/diff/{contract_id}`（获取差异）
  3. `POST /negotiation/ai-analyze/{contract_id}`（AI 分析）
  4. `GET /negotiation/risks/{contract_id}`（获取风险）
- **影响**: 前端无法一步完成分析
- **文件**: `frontend/src/stores/negotiation.js:23-48`
- **建议修复方向**: 前端适配三步流程；或后端新增一个合并端点将 upload+analyze+return 一步完成
- **归属**: 待前后端讨论

### M6. 合同类型编码可能不匹配

- **前端 hardcode**: `tech_service` / `procurement` / `employment` / `cooperation` / `non_disclosure`
- **后端 `ContractType` 模型**: 有 `code` 字段（实际值需经 Swagger 确认）
- **风险**: 如果后端 `code` 使用的是 `technical_service` 等新命名，则前端匹配不上
- **归属**: 需确认后端数据库 seed 数据后再决定（待讨论）

---

## 六、低优先级问题

### L1. 文档中 `/api/v1/contract/session` 端点不存在

- AGENTS.md 和 README 中提到有 `/api/v1/contract/session` 端点，但后端没有
- 后端合同路由前缀是 `/contracts`（复数），不是 `/contract`（单数）
- **建议**: 更新文档

### L2. 前端路由 `/negotiate` 与后端 API 路径 `/negotiation` 命名不统一

- 不直接影响功能，但增加认知成本

### L3. `api-contracts/` 目录定位不清晰

- 当前 `api-contracts/` 描述的是 Agent 进程内 Python 方法调用契约，不是前端 HTTP API 契约
- 容易被误解为 HTTP API 契约

---

## 七、总体统计

| 问题级别 | 数量 | 前端改 | 后端改 | 待讨论 | Docs 改 |
|---------|------|--------|--------|--------|---------|
| 高 | 5 | H1,H2,H3,H5 | H4 | H4 | — |
| 中 | 6 | M1,M2,M3,M5 | M4, M6(待确认) | M5,M6 | — |
| 低 | 3 | — | — | — | L1,L2,L3 |
