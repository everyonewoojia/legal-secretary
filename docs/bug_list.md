# Bug 记录表

> 维护人：张怀月
> 创建日期：2026-06-29
> 说明：记录联调和开发过程中发现的 Bug，供团队跟踪修复进度。

---

## 模板

```markdown
| 编号 | 模块 | 问题描述 | 优先级 | 负责人 | 状态 | 备注 |
|------|------|---------|--------|--------|------|------|
| B-001 | 认证 | ... | P0 | 待定 | 待修复 | ... |
```

**优先级定义**:
- **P0**: 阻断性，功能不可用，必须修复才能联调
- **P1**: 重要，功能可用但行为错误
- **P2**: 次要，UI/UX 细节或非关键路径
- **P3**: 建议，未来优化

**状态定义**:
- `待修复`: 已确认，未开始
- `修复中`: 正在处理
- `已修复`: 已提交修复
- `已验证`: QA 确认通过
- `暂缓`: 当前版本不处理
- `非 Bug`: 确认不是 Bug

---

## Bug 列表

| 编号 | 模块 | 问题描述 | 复现步骤 | 实际结果 | 预期结果 | 优先级 | 负责人 | 状态 | 备注 |
|------|------|---------|---------|---------|---------|--------|--------|------|------|
| B-001 | RAG | 前端 `POST /api/v1/rag/search` 路径后端不存在 | 前端调用 `rag.search()` | 404 Not Found | 返回搜索结果 | P0 | 待定 | 待修复 | 需确认使用 GET /rag/laws 还是新增 POST /rag/search |
| B-002 | 合同 | 前端 `chatStream()` 全部用 Mock，未对接真实 SSE 端点 | 在合同起草页面发送消息 | 使用 Mock 数据回复 | 从后端 `POST /contracts/chat/{type_id}` 流式获取回复 | P0 | 待定 | 待修复 | 需同时改 api/contract.js 和 stores/contract.js |
| B-003 | 合同 | 前端 `generateContract(sessionId)` 后端无对应端点 | 点击"生成合同"按钮 | 调用 Mock | 调用 `POST /contracts/generate/{type_id}` 生成合同 | P0 | 待定 | 待修复 | 后端用 type_id + collected_fields，前端需适配 |
| B-004 | 用户 | 前端注册传入 `username`，后端需要 `nickname` | 填写注册表单提交 | `username` 被忽略，`nickname` 留空 | 填写的昵称正确保存到后端 | P0 | 待定 | 待修复 | 前端表单字段名改为 nickname |
| B-005 | 合同 | 合同下载前端期望 download_url，后端返回 content/title/format | 点击"下载"按钮 | `window.open('#')` 打开空白标签 | 成功下载合同文件 | P0 | 待定 | 待修复 | 需前后端确认方案 |
| B-006 | 用户 | 用户列表前端用纯数组，后端返回 `{items, total}` | Admin.vue 调用 `fetchUserList()` | 类型错误或 undefined | 正确填充用户列表 | P1 | 待定 | 待修复 | 前端 store 需要取 `res.data.items` |
| B-007 | 用户 | 用户状态字段 `status` vs `is_active` | Admin.vue 显示用户状态 | 状态显示错误或不对应 | 正确显示"正常"/"禁用" | P1 | 待定 | 待修复 | 前端改为判断 `row.is_active` |
| B-008 | 认证 | 用户信息字段 `username` vs `nickname` | Profile.vue 显示用户昵称 | 昵称字段为空或 undefined | 正确显示用户昵称 | P1 | 待定 | 待修复 | 前端 `userInfo.username` 改为 `userInfo.nickname` |
| B-009 | 谈判 | 谈判分析需要多步流程（upload/diff/analyze/risks），前端期望一步完成 | 上传文件点击"开始分析" | 调用 Mock 返回模拟数据 | 调用后端 API 完成分析 | P1 | 待定 | 待修复 | 需确认：前端适配多步 or 后端新增合并端点 |
| B-010 | 认证 | 后端有两个 `/change-password` 端点（auth 无认证 + users 有认证） | — | 功能重复，可能存在安全风险 | 只保留一个有认证的端点 | P2 | 待定 | 待修复 | 建议删除 `auth/change-password`（无认证版本）|
| B-011 | 文档 | AGENTS.md 记录的 `/api/v1/contract/session` 端点不存在 | — | 文档与实际不符 | 更新文档 | P3 | 待定 | 待修复 | 后端合同路由为 `/contracts`（复数），无 session 端点 |

---

## 变更记录

| 日期 | 操作 | 描述 |
|------|------|------|
| 2026-06-29 | 初始化 | 基于联调前接口一致性检查结果创建初始 Bug 列表 |
