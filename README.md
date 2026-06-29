# 法务小秘

面向中小企业的 AI 智能体合同起草与谈判辅助系统。

## 项目简介

法务小秘是一款利用大语言模型与 AI 智能体技术，面向中小企业的合同起草与谈判辅助 Web 系统。系统提供**对话式合同起草**与**智能风险审查**两大核心能力，帮助企业在没有专职法务的情况下高效完成合同拟定与谈判分析。

### 核心模块

| 模块 | 说明 |
|------|------|
| 合同智能起草 | 多轮对话引导 + 大模型自动生成标准化合同初稿，支持双栏预览与 docx/pdf 导出 |
| 谈判风险审查 | 上传对方修改稿，自动差异比对 + AI 风险识别 + 反驳话术生成 |
| 本地法务知识库 | 5类合同模板库 + 法律法规摘要库 + RAG 检索增强 |
| 后台管理 | 用户审核、LLM API Key 配置、系统日志监控 |

### 技术栈

- **前端**: Vue 3 + Vite + Element Plus + Pinia
- **后端**: Python FastAPI + SQLAlchemy + SQLite
- **AI**: OpenAI-compatible LLM API (通义千问/智谱GLM) + 流式 SSE
- **检索**: FAISS 向量库 + RAG 检索增强生成

## 快速开始

### 环境要求

- Node.js >= 18
- Python >= 3.10
- Git

### 安装

```bash
# 1. 克隆仓库
git clone <repo-url>
cd legal-secretary

# 2. 安装前端依赖
cd frontend
npm install
cd ..

# 3. 安装后端依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 填入 LLM_API_KEY（阿里云 DashScope）
# 警告：.env 只允许本地修改，不要修改 .env.example
# 警告：.env 包含敏感信息，不要提交到 Git
```

### 运行

```bash
# 终端1：启动后端（必须在项目根目录，否则路径错误）
PYTHONPATH=backend python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 终端2：启动前端
cd frontend
npm run dev -- --host 0.0.0.0
```

打开浏览器访问 `http://localhost:5173`

### 初始化知识库（首次使用）

```bash
# 首次启动后，需导入知识库数据到 LawArticle 表
PYTHONPATH=backend python scripts/ingest_knowledge_base.py
```

> 知识库导入不是每次启动都需要，只在**首次初始化**、**重置数据库**、**修改 knowledge_base 目录内容**或**更新 ingest 逻辑**后执行。

### 构建 FAISS 向量索引（可选）

```bash
# 构建 FAISS 语义搜索索引（需下载约 500MB 模型）
python scripts/build_vector_index.py

# 搜索演示
python scripts/search_knowledge_base.py "违约金过高怎么办"
```

## 项目结构

```
legal-secretary/
├── frontend/                 # 前端 Vue3 项目
│   └── src/
│       ├── api/              # API 封装
│       ├── router/           # 路由配置
│       ├── stores/           # Pinia 状态管理
│       └── views/            # 页面组件
├── backend/                  # 后端 FastAPI 项目
│   └── app/
│       ├── routers/          # REST API 路由
│       ├── services/         # 业务逻辑
│       ├── models/           # 数据库模型
│       ├── schemas/          # 请求/响应 DTO
│       └── core/             # 配置与工具
├── agent/                    # AI Agent 层
│   ├── orchestrator.py       # 主控 Agent
│   ├── dialogue_agent.py     # 对话引导 Agent
│   ├── contract_agent.py     # 合同生成 Agent
│   ├── risk_agent.py         # 风险分析 Agent
│   └── prompts/              # System Prompt
├── knowledge_base/           # 知识库
│   ├── templates/            # 5类合同结构化模板
│   ├── clauses/              # 底线策略规则库
│   └── legal_docs/           # 法规摘要
├── scripts/                  # 工具脚本
├── tests/                    # 测试
└── docs/                     # 文档
```

## API 接口一览

所有接口前缀 `/api/v1`，统一响应格式 `{code: 0, message: "ok", data: {...}}`。

### 认证 Auth

| 方法 | 路由 | 说明 | 认证 |
|------|------|------|------|
| POST | `/auth/login` | 登录，返回 JWT token | ❌ |
| POST | `/auth/register` | 注册 | ❌ |
| POST | `/auth/sms-code` | 发送验证码（演示模式返回 123456）| ❌ |

### 用户管理 Users

| 方法 | 路由 | 说明 | 认证 |
|------|------|------|------|
| GET | `/users/me` | 获取个人信息 | ✅ |
| PUT | `/users/me` | 更新个人信息 | ✅ |
| POST | `/users/me/change-password` | 修改密码 | ✅ |
| POST | `/users/me/avatar` | 上传头像 | ✅ |

### 合同起草 Contracts

| 方法 | 路由 | 说明 | 认证 |
|------|------|------|------|
| GET | `/contracts/types` | 合同类型列表 | ❌ |
| POST | `/contracts/chat/{type_id}` | SSE 流式对话引导 | ❌ |
| POST | `/contracts/generate/{type_id}` | 生成合同初稿（非流式） | ✅ |
| POST | `/contracts/generate-stream/{type_id}` | SSE 流式生成合同 | ✅ |
| POST | `/contracts/` | 创建合同 | ✅ |
| GET | `/contracts/` | 合同列表 | ✅ |
| GET | `/contracts/{id}` | 合同详情 | ✅ |
| DELETE | `/contracts/{id}` | 删除合同 | ✅ |
| GET | `/contracts/{id}/download` | 下载合同（返回文本） | ✅ |
| GET | `/contracts/{id}/versions` | 版本列表 | ✅ |
| GET | `/contracts/{id}/risks` | 风险列表 | ✅ |

### 谈判审查 Negotiation

| 方法 | 路由 | 说明 | 认证 |
|------|------|------|------|
| POST | `/negotiation/upload/{contract_id}` | 上传对方修改稿 | ✅ |
| GET | `/negotiation/diff/{contract_id}` | 文本差异比对 | ✅ |
| POST | `/negotiation/ai-analyze/{contract_id}` | AI 风险分析 | ✅ |
| GET | `/negotiation/risks/{contract_id}` | 风险列表 | ✅ |
| POST | `/negotiation/counter-argument` | 生成谈判话术 | ✅ |

### RAG 知识库

| 方法 | 路由 | 说明 | 认证 |
|------|------|------|------|
| GET | `/rag/laws` | 搜索法律法规（query: q, category, page） | ✅ |
| POST | `/rag/laws` | 新增法条 | ✅ |
| GET/PUT/DELETE | `/rag/laws/{id}` | 单条法条 CRUD | ✅ |
| GET | `/rag/templates` | 合同模板列表 | ✅ |
| POST | `/rag/templates` | 新增合同模板 | ✅ |
| GET/PUT/DELETE | `/rag/templates/{id}` | 单条模板 CRUD | ✅ |

### 后台管理 Admin

| 方法 | 路由 | 说明 | 认证 |
|------|------|------|------|
| GET | `/admin/users` | 用户列表（分页） | admin |
| PUT | `/admin/users/{id}/toggle-active` | 启用/禁用用户 | admin |
| PUT | `/admin/users/{id}/role` | 修改用户角色 | admin |
| GET | `/admin/api-keys` | API Key 列表 | admin |
| PUT | `/admin/api-keys/{id}` | 更新 API Key | admin |
| GET | `/admin/logs` | 审计日志 | admin |
| GET | `/admin/stats` | 系统统计 | admin |

## 安全注意事项

- `.env` 文件包含 `LLM_API_KEY` 和 `SECRET_KEY`，**不要提交到 Git**
- 默认 `SECRET_KEY=your-secret-key` **仅用于开发**，生产部署必须修改
- `*.db` 文件为本地开发数据库，**不要提交到 Git**
- `.env.example` 是模板文件，不要写入真实密钥

## 开发团队

| 角色 | 姓名 | 职责 |
|------|------|------|
| 项目总监 | 黄嘉儿 | AI 智能体开发、Prompt 工程 |
| 项目经理 | 姬卓希 | 后端 API、数据库设计 |
| 开发人员 | 魏麟凤 | 前端开发、交互设计 |
| 开发人员 | 张怀月 | 合同模板、测试、文档 |

> 本项目为教学实训 Demo 系统，生成内容仅供学习参考，不替代专业律师出具的法律意见。
