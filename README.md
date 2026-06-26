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
# 编辑 .env 填入 LLM_API_KEY
```

### 运行

```bash
# 终端1：启动后端
uvicorn backend.app.main:app --reload --port 8000

# 终端2：启动前端
cd frontend
npm run dev
```

打开浏览器访问 `http://localhost:5173`

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
│       ├── api/              # REST API 路由
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
├── tests/                    # 测试
└── docs/                     # 文档
```

## API 接口一览

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/auth/login` | POST | 用户登录 |
| `/api/v1/auth/register` | POST | 用户注册 |
| `/api/v1/contract/session` | POST | 创建合同会话 |
| `/api/v1/contract/chat/stream` | POST | 对话引导（SSE 流式） |
| `/api/v1/contract/generate` | POST | 生成合同初稿 |
| `/api/v1/contract/{id}/export` | GET | 导出合同文档 |
| `/api/v1/contract/negotiate/analyze` | POST | 风险分析 |
| `/api/v1/rag/search` | POST | 知识库检索 |

## 开发团队

| 角色 | 姓名 | 职责 |
|------|------|------|
| 项目总监 | 黄嘉儿 | AI 智能体开发、Prompt 工程 |
| 项目经理 | 姬卓希 | 后端 API、数据库设计 |
| 开发人员 | 魏麟凤 | 前端开发、交互设计 |
| 开发人员 | 张怀月 | 合同模板、测试、文档 |

> 本项目为教学实训 Demo 系统，生成内容仅供学习参考，不替代专业律师出具的法律意见。
