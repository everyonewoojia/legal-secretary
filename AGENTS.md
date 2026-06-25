# 法务小秘 — AI 合同起草与谈判辅助系统

## 项目概况
面向中小企业的 AI 智能体合同起草与谈判辅助系统。前端已搭建完成，可对接后端 API 进行联调。

## 技术栈
- **前端**: Vue 3 + Vite 8 + Vue Router 4 + Pinia 3 + Element Plus + Axios + marked
- **后端**: FastAPI (Python) — 已实现全部 API
- **AI 层**: Python Agent 体系（orchestrator / dialogue / contract / risk）
- **数据库**: SQLite (开发) / MySQL (生产)
- **大模型**: 阿里云 DashScope (通义千问)，通过 OpenAI 兼容 SDK 调用

## 目录结构 (前端)
```
frontend/
├── src/
│   ├── api/
│   │   ├── index.js          # axios 实例 + SSE 流式聊天 (chatStream)，默认导出 http
│   │   ├── contract.js       # 合同 API：createSession / generateContract / exportDraft / analyze
│   │   ├── negotiation.js    # 谈判 API：analyzeNegotiation / exportReport
│   │   └── mock/
│   │       └── authMock.js   # 登录/注册/用户管理的模拟接口
│   ├── components/           # 公共组件
│   ├── views/
│   │   ├── Home.vue          # 首页（功能入口卡片）
│   │   ├── Login.vue         # 登录页面（手机号+密码）
│   │   ├── Register.vue      # 注册页面（手机号+验证码）
│   │   ├── ContractDraft.vue # 合同起草（三栏布局：类型选择 + SSE 对话 + 预览）
│   │   ├── NegotiationAnalyze.vue # 谈判分析（两栏：差异列表 + 风险详情）
│   │   ├── Negotiate.vue     # 旧版谈判分析（已废弃）
│   │   ├── Profile.vue       # 个人中心（信息编辑/修改密码）
│   │   └── Admin.vue         # 后台管理（用户列表/禁用/改角色）
│   ├── stores/
│   │   ├── user.js           # 用户认证状态（login/register/logout/权限检查）
│   │   ├── contract.js       # 合同会话/消息/slots/起草状态
│   │   └── negotiation.js    # 谈判分析状态（diffList / caseId / selectedRisk）
│   ├── router/index.js       # 7 条路由 + beforeEach 守卫（auth/role 检查）
│   ├── App.vue               # 根组件（认证后显示顶部导航栏）
│   ├── main.js               # 入口（注册 Pinia/Router/ElementPlus）
│   └── style.css
├── index.html
├── vite.config.js            # 代理 /api → localhost:8000
└── package.json
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
| `/api/v1/negotiation/analyze` | POST | 谈判风险分析（支持文件上传）|
| `/api/v1/negotiation/{id}/export` | GET | 导出分析报告 |
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
- 当前开发分支: `feat-wlf`

## 待办/后续可做
- [ ] 完善登录流程（当前 Login 页面已存在，且 Api 层已配置 JWT 拦截器）
- [ ] 增强合同预览的 Markdown 渲染样式
- [ ] 移动端适配
- [ ] 合同保存/历史记录管理
- [ ] 多轮对话上下文优化
