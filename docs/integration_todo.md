# 联调前待办清单

> 日期：2026-06-29
> 维护人：张怀月
> 说明：按模块列出前后端联调前需要完成的准备工作，供组员分工执行。

---

## 一、认证登录

### 当前状态
- 后端: `POST /api/v1/auth/login`（接受 `phone`, `password`）返回 `{access_token, token_type}`
- 后端: `POST /api/v1/auth/register`（接受 `phone`, `password`, `nickname`, `company_name`）返回 `{user_id, token}`
- 前端 store: 全部使用 `authMock.js`，但 `api/index.js` 已预定义 `auth.login()` 和 `auth.register()` 的 HTTP 路径

### 阻塞问题
- [ ] H5: 注册字段名 `username` vs `nickname` 不一致

### 前端待改
- [ ] `stores/user.js:` `login()` 改为调用 `api/index.js` 的 `auth.login()` 而非 `mockLogin()`
- [ ] `stores/user.js:` `register()` 改为调用 `api/index.js` 的 `auth.register()` 而非 `mockRegister()`
- [ ] 传入参数从 `{phone, password, username}` 改为 `{phone, password, nickname, company_name?}`
- [ ] 对接后端响应：后端 `login` 返回 `data.access_token`，前端需提取 `res.data.access_token` 而非 `res.data.token`

### 后端待改
- 后端接口已就绪，无需改动

### 文档待改
- 无

### 验收标准
1. 输入正确手机号密码 → 登录成功，跳转首页
2. 输入错误密码 → 显示"密码错误"提示
3. 注册新账号 → 注册成功并跳转首页
4. 手机号已注册 → 提示"该手机号已注册"

---

## 二、用户管理

### 当前状态
- 后端: `GET /api/v1/users/me` 返回 `{id, phone, nickname, avatar, gender, company_name, role, is_active}`
- 后端: `PUT /api/v1/users/me` 支持更新 `nickname`, `avatar`, `gender`, `company_name`
- 后端: `POST /api/v1/users/me/change-password` 接受 `{old_password, new_password}`
- 前端: 全部使用 `authMock.js` 的 `mockUpdateProfile` / `mockChangePassword`

### 阻塞问题
- [ ] M1: 用户信息字段 `username` vs `nickname`、`status` vs `is_active`
- [ ] M4: 两个 `/change-password` 端点，需确认前端使用哪个

### 前端待改
- [ ] `stores/user.js:` `updateProfile()` 改为 HTTP 调用 `PUT /api/v1/users/me`
- [ ] `stores/user.js:` `changePassword()` 改为 HTTP 调用 `POST /api/v1/users/me/change-password`
- [ ] 字段映射：`username` → `nickname`、`avatar` → `avatar`
- [ ] Profile.vue 所有 `userInfo.username` → `userInfo.nickname`

### 后端待改
- [ ] M4: 删除 `auth/change-password` 无认证版本（可选），保留 `users/me/change-password`

### 文档待改
- 无

### 验收标准
1. 进入个人中心 → 显示当前用户信息（昵称、脱敏手机号、角色、注册时间）
2. 修改昵称 → 保存成功，页面刷新显示新昵称
3. 修改密码 → 正确旧密码可改，错误旧密码提示
4. JWT token 过期 → 自动跳转登录页

---

## 三、合同起草

### 当前状态
- 后端: 无 session 机制，采用 `type_id` + `collected_fields` 的 RESTful 设计
- 后端流程: 获取类型（GET）→ SSE 对话（POST）→ 生成合同（POST）
- 前端: 完整 session 驱动的三栏页面，全部走 Mock

### 阻塞问题
- [ ] **H2**: 整个 `contractStore` 的 session 模型与后端不兼容（最高优先级）
- [ ] H3: 生成合同入参 `sessionId` vs `type_id` + `collected_fields`
- [ ] H4: 下载响应格式不匹配

### 前端待改
- [ ] **重写 `stores/contract.js`**：
  - 删除 `sessionId` 概念
  - `startSession(type)` → 调用 `GET /api/v1/contracts/types` + 初始化对话状态
  - `sendMessage(msg)` → 改为 `POST /api/v1/contracts/chat/{type_id}`（SSE 流式消费）
  - `generateContract()` → 改为 `POST /api/v1/contracts/generate/{type_id}` 或 `generate-stream/{type_id}`
- [ ] **重写 `api/contract.js`**：
  - 删除 `mockCreateSession` / `mockGenerateContract` / `mockExportDraft`
  - 新增 `http.get('/contracts/types')`
  - 新增 `http.post('/contracts/chat/' + typeId, {message, history})`（SSE）
  - 新增 `http.post('/contracts/generate/' + typeId, {collected_fields, title})`
- [ ] 修改 `api/index.js` 中的 `chatStream()`：从 `mockChatStream` 切换为真实 SSE 消费（后端已有 `/contracts/chat/{type_id}` 和 `/contracts/generate-stream/{type_id}`）
- [ ] 合同下载：需和后端确认方案后再修改

### 后端待改
- [ ] H4: 确认下载方案（`/contracts/{id}/download` 返回文件流还是文本）

### 文档待改
- [ ] 更新 AGENTS.md 中 `/api/v1/contract/session` 的记录（此端点不存在）

### 验收标准
1. 选择合同类型（5 种）→ 启动对话
2. 输入合同要素 → AI 流式回复
3. 点击生成合同 → 右侧预览区显示合同文本
4. 点击下载 → 下载文件（DOCX 或文本）
5. SSE 流式打字效果正常

---

## 四、谈判风险审查

### 当前状态
- 后端: 四步流程（upload → diff → ai-analyze → risks）
- 前端: 一步 `analyzeNegotiation(FormData)` Mock，返回模拟 diff_list

### 阻塞问题
- [ ] **M5**: 前端期望一次调用，后端需要多步流程

### 前端待改
- [ ] `stores/negotiation.js:` `submitAnalysis()` 改为多步流程：
  1. 若用户已上传文件，调用 `POST /negotiation/upload/{contract_id}`（需先有 contract_id）
  2. 调用 `GET /negotiation/diff/{contract_id}` 获取差异
  3. 调用 `POST /negotiation/ai-analyze/{contract_id}` 获取 AI 分析
  4. 调用 `GET /negotiation/risks/{contract_id}` 获取风险列表
- [ ] 或等待后端新增合并端点 `POST /negotiation/analyze` 接受文件 + 文本一步完成
- [ ] `api/negotiation.js`: 需要对接真实 HTTP 端点

### 后端待改
- [ ] M5: 创建合并端点 `POST /negotiation/analyze`（接收 UploadFile 或 body），内部执行 upload+diff+analyze，返回完整的 diff_list + risks — 或前端直接适配多步流程

### 文档待改
- 无

### 验收标准
1. 上传对方合同文件或粘贴修改文本
2. 点击分析 → 显示差异列表（红/橙/蓝风险标签）
3. 选择差异项 → 右侧显示风险详情、法律依据、底线话术
4. 点击复制话术 → 可用
5. 导出报告 → 可下载

---

## 五、RAG 知识库

### 当前状态
- 后端: `GET /api/v1/rag/laws?q=...` 支持 RESTful 查询，不支持 `POST /rag/search`
- 后端: 完整的法条和模板 CRUD
- 前端: `api/index.js` 中定义了 `rag.search()` 但调用路径不存在
- FAISS 索引: 已构建，但尚未接入后端

### 阻塞问题
- [ ] **H1**: 前端 `POST /api/v1/rag/search` 后端没有

### 前端待改
- [ ] `api/index.js:28-30` 中的 `rag.search()` 改为 `http.get('/rag/laws', { params: { q: query } })`
- [ ] 完善前端展示（搜索结果列表）

### 后端待改
- [ ] 如果需要 `POST /rag/search` 风格，可以新增该端点；否则前端适配 GET 风格即可
- [ ] 如果需要 FAISS 语义搜索，需将 `scripts/build_vector_index.py` 产出的索引接入 `rag_engine.py` 或 `rag_service.py`

### 文档待改
- [ ] 更新 api-contracts 中 `rag_search.json` 的接入状态

### 验收标准
1. 输入查询关键词 → 返回匹配的法条/知识块
2. 搜索结果包含来源文件、内容预览

---

## 六、后台管理

### 当前状态
- 后端: 完整的 admin 路由（用户列表/切换状态/修改角色/API Keys/日志/统计）
- 前端: 全部使用 Mock (`mockGetUserList` / `mockToggleUserStatus` / `mockChangeUserRole`)

### 阻塞问题
- [ ] M2: 用户列表响应结构 `纯数组` vs `{items, total}`
- [ ] M3: 用户状态字段 `status` vs `is_active`

### 前端待改
- [ ] `stores/user.js:` `fetchUserList()` 改为 HTTP 调用 `GET /api/v1/admin/users?page=1`
- [ ] `stores/user.js:` `toggleUserStatus()` 改为 HTTP 调用 `PUT /api/v1/admin/users/{id}/toggle-active`
- [ ] `stores/user.js:` `changeUserRole()` 改为 HTTP 调用 `PUT /api/v1/admin/users/{id}/role?role=admin`
- [ ] Admin.vue 中 `row.status === 'active'` → `row.is_active === true`
- [ ] Admin.vue 中 `row.password` 敏感字段：后端不返回 password，没问题

### 后端待改
- 后端接口已就绪，无需改动

### 文档待改
- 无

### 验收标准
1. 管理员登录 → 可访问 `/admin`
2. 用户列表分页展示（头像/用户名/手机号/角色/状态/注册时间）
3. 禁用/启用用户 → 确认弹窗 → 操作成功
4. 修改角色 → 确认弹窗 → 操作成功
5. 普通用户访问 `/admin` → 无权限提示，跳转首页

---

## 总体依赖关系

```
认证登录 ───→ 用户管理 ───→ 后台管理
     │                     （需要 token）
     ├──→ 合同起草（需要 token + 类型选择）
     └──→ 谈判风险审查（需要 token + contract_id）
     └──→ RAG 知识库（需要 token）
```

**建议联调顺序**:
1. **认证登录**（最简单，后端已就绪，前端调整最小）
2. **用户管理/个人中心**（依赖 token）
3. **后台管理**（依赖 admin 角色）
4. **合同起草**（最复杂，前后端模型差异最大）
5. **RAG 知识库**（路径调整即可）
6. **谈判风险审查**（流程差异大，需确认方案后执行）
