# 法务小秘 API 接口文档

**基础地址:** `/api/v1`  
**统一响应格式:**
```json
{
  "code": 0,
  "message": "ok",
  "data": { ... }
}
```
**认证方式:** `Authorization: Bearer <token>`（除 auth 接口外都需要）

---

## 一、认证 Auth

### 1.1 注册
`POST /auth/register`
```json
// Request
{"phone": "13912345678", "password": "Test1234", "nickname": "用户昵称", "company_name": "公司名"}
// Response 200
{"code":0, "message":"ok", "data":{"user_id":1, "token":{"access_token":"xxx", "token_type":"bearer"}}}
```

### 1.2 登录
`POST /auth/login`
```json
// Request
{"phone": "13800000000", "password": "admin123"}
// Response 200
{"code":0, "message":"ok", "data":{"access_token":"xxx", "token_type":"bearer"}}
```

### 1.3 发送短信验证码（演示模式）
`POST /auth/sms-code`
```json
// Request
{"phone": "13912345678"}
// Response 200
{"code":0, "message":"ok", "data":{"message":"验证码已发送（演示模式），验证码：123456"}}
```

### 1.4 修改密码（需认证）
`POST /auth/change-password`
```json
// Request
{"old_password": "old123", "new_password": "new456"}
```

---

## 二、用户管理 Users

### 2.1 获取个人信息
`GET /users/me`  
Response `data`:
```json
{"id":1, "phone":"13912345678", "nickname":"用户昵称", "avatar":"", "gender":0, "company_name":"公司名", "role":"user", "is_active":true}
```

### 2.2 修改个人信息
`PUT /users/me`
```json
// Request（可选字段，至少传一个）
{"nickname":"新昵称", "avatar":"url", "gender":1, "company_name":"新公司"}
```

### 2.3 上传头像
`POST /users/me/avatar`  
- 类型: `multipart/form-data`  
- 字段: `file`（JPG/PNG, ≤2MB）

### 2.4 修改密码
`POST /users/me/change-password`
```json
{"old_password": "old123", "new_password": "new456"}
```

---

## 三、合同起草 Contracts

### 3.1 合同类型列表
`GET /contracts/types`
```json
// Response data:
[{"id":1, "name":"技术服务合同", "code":"tech_service", "description":"适用于软件开发、技术咨询等服务场景", "sort_order":1},
 {"id":2, "name":"采购合同", ...},
 {"id":3, "name":"劳动合同", ...},
 {"id":4, "name":"合作协议", ...},
 {"id":5, "name":"保密协议", ...}]
```

### 3.2 AI 对话（SSE 流式）
`POST /contracts/chat/{type_id}`  
- 返回: `text/event-stream`（SSE 流式响应）
```json
// Request
{"message": "我需要起草一份技术服务合同", "history": []}
// SSE events:
data: {"content": "您好！我是法务小秘的AI助手..."}
data: {"content": "请问甲方公司的全称是什么？"}
data: [DONE]
```

### 3.3 AI 生成合同（同步）
`POST /contracts/generate/{type_id}`  
```json
// Request
{"collected_fields": {"甲方":"A公司", "乙方":"B公司", "服务内容":"软件开发", "金额":"100万"}, "title":"技术服务合同"}
```

### 3.4 AI 生成合同（SSE 流式）
`POST /contracts/generate-stream/{type_id}`  
- 返回: `text/event-stream`，逐字输出合同全文
- 最后一条 event 包含 `contract_id`

### 3.5 创建合同（手动）
`POST /contracts/`
```json
{"type_id":1, "title":"技术服务合同", "content":"合同内容..."}
```

### 3.6 合同列表
`GET /contracts?status=draft`  
- 参数: `status` 可选（draft / completed / archived）

### 3.4 合同详情
`GET /contracts/{contract_id}`

### 3.5 删除合同
`DELETE /contracts/{contract_id}`

### 3.6 合同版本列表
`GET /contracts/{contract_id}/versions`

### 3.9 合同风险列表
`GET /contracts/{contract_id}/risks`
```json
// Response data:
[{"id":1, "clause_location":"第七条 违约责任", "risk_type":"违约金", "risk_level":"high", "description":"违约金比例由0.05%上调至0.1%", "suggestion":"建议恢复原比例", "legal_basis":"《民法典》第585条"}]
```

### 3.8 合同下载
`GET /contracts/{contract_id}/download?fmt=docx`  
- 参数: `fmt` 可选 `docx` / `pdf`

---

## 四、谈判审查 Negotiation

### 4.1 上传对方修改稿
`POST /negotiation/upload/{contract_id}`  
- 类型: `multipart/form-data`  
- 字段: `file`（仅支持 .docx 格式）

### 4.2 AI 风险分析
`POST /negotiation/ai-analyze/{contract_id}`  
- 自动对比最新两个版本，调用大模型识别风险条款
```json
// Response data:
[{"clause_location":"第七条 违约责任", "risk_type":"违约金比例上调", "risk_level":"high", "description":"...", "suggestion":"...", "legal_basis":"..."}]
```

### 4.3 文本差异对比
`GET /negotiation/diff/{contract_id}?version_a=1&version_b=2`
```json
// Response data:
{"original_text":"原合同内容...", "modified_text":"修改后内容...", "changes":[{"type":"addition", "content":"新增内容", "line_number":10}, {"type":"deletion", "content":"删除内容", "line_number":15}]}
```

### 4.4 风险列表
`GET /negotiation/risks/{contract_id}`  
（同 3.9）

### 4.5 生成反驳话术
`POST /negotiation/counter-argument`
```json
// Request
{"risk_id":1, "negotiation_style":"balanced"}
// Response data:
{"plan_a":"【强硬方案】根据《民法典》第xxx条...", "plan_b":"【折中方案】考虑到双方合作意愿..."}
```

---

## 五、知识库 RAG

### 5.1 添加法条
`POST /rag/laws`
```json
{"title":"民法典第585条", "source":"《民法典》", "content":"当事人可以约定一方违约时应当根据违约情况向对方支付一定数额的违约金...", "category":"合同编"}
```

### 5.2 搜索法条
`GET /rag/laws?q=违约金&category=合同编&page=1&page_size=20`

### 5.3 法条详情
`GET /rag/laws/{law_id}`

### 5.4 更新法条
`PUT /rag/laws/{law_id}`
```json
{"title":"新标题", "source":"新来源", "content":"新内容", "category":"新分类"}
```

### 5.5 删除法条
`DELETE /rag/laws/{law_id}`

### 5.6 添加模板
`POST /rag/templates`
```json
{"name":"技术服务合同标准模板", "type_id":1, "description":"标准模板", "structure":"{...}"}
```

### 5.7 模板列表
`GET /rag/templates?type_id=1`

### 5.8 模板详情
`GET /rag/templates/{template_id}`

### 5.9 更新模板
`PUT /rag/templates/{template_id}`
```json
{"name":"新名称", "description":"新描述", "structure":"新结构", "is_active":true}
```

### 5.10 删除模板
`DELETE /rag/templates/{template_id}`

---

## 六、后台管理 Admin

### 6.1 用户列表
`GET /admin/users?page=1&page_size=20`

### 6.2 启用/停用用户
`PUT /admin/users/{user_id}/toggle-active`

### 6.3 修改用户角色
`PUT /admin/users/{user_id}/role?role=admin`

### 6.4 API Key 列表
`GET /admin/api-keys`

### 6.5 更新 API Key
`PUT /admin/api-keys/{key_id}?api_key=sk-xxx&base_url=https://...&model_name=qwen-max&is_active=true`

### 6.6 操作日志
`GET /admin/logs?action=login&page=1&page_size=50`

### 6.7 系统统计
`GET /admin/stats`
```json
// Response data:
{"users":10, "contracts":25, "laws":1420}
```

---

## 附录：通用错误码

| code | 含义 |
|------|------|
| 0    | 成功 |
| 400  | 请求参数错误 |
| 401  | 未认证 / Token 无效 |
| 403  | 无权限 |
| 404  | 资源不存在 |
| 409  | 资源冲突（如手机号已注册） |
| 500  | 服务器内部错误 |
