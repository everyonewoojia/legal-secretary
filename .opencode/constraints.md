# AI 开发约束规则

## 1. 会话前必读
每次对话开始（或上下文重置后），必须先完整阅读根目录 `AGENTS.md`，确认当前分支状态、已完成工作和目录结构后再操作。

## 2. 全栈联调契约
- 编写 Python Agent（`agent/` 下的类）时，输入输出格式必须严格匹配 `api-contracts/` 下对应的 JSON Schema 契约文件，不可自行增减字段。
- 前端对接必须遵守 `frontend/src/api/index.js` 定义的 Axios 实例规范：自动注入 JWT token、统一错误拦截、响应格式 `{code, message, data}`。
- 流式对话必须使用 `chatStream()`（基于 fetch + ReadableStream 消费 SSE），禁止用其他方式轮询或模拟。

## 3. 每日进度同步钩子
在当前分支的工作结束或准备 commit 前，必须由 AI 自动在 `AGENTS.md` 中：
- `📌 各分支并行开发状态` 表格中更新当前分支状态与说明。
- `已完成的工作` 区域追加最新进度日志（按日期或迭代分段）。
- 严禁覆盖、删除或修改其他分支的日志内容。

## 4. 垃圾文件防护
- 禁止在项目根目录或各代码目录（`frontend/`、`backend/`、`agent/` 等）下生成临时的 `.txt`、`.log`、未归类的备份文件（如 `test_copy.py`、`temp.json`）或任何不属该目录产物的文件。
- 所有测试代码必须放入 `tests/` 目录。
- 所有文档、数据、知识库文件必须归入 `docs/`、`knowledge_base/` 等对应目录。
- 若需临时调试输出，使用完后立即清理，不得提交。
