# YCZX Code 团队分工说明

本文基于仓库现有 `README.md` 与 `AGENTS.md` 的分层边界，明确前期交接和后续并行开发时的角色职责。若团队任务发布者提供了更细的任务编号或验收标准，应以任务单为准，并同步更新本文。

## 阶段说明

### 前期：交接为主

角色 A 先完成平台层基础能力，并以合并的 PR 和公共契约为交接边界。其他角色在角色 A 的 PR 合入 `main` 前，可以阅读代码、准备依赖和设计测试，但不应依赖尚未合入的新接口。

### 后期：并行开发

角色 A、B、C 分别在各自边界内并行开发。任何涉及公共契约、权限、事件、配置或跨层依赖的变化，必须先同步相关角色，并在同一 PR 中更新测试、文档和本说明。

## 角色与职责

### 角色 A：平台与核心

负责层：`core/`、`agents/`、`application.py`。

主要职责：

- 维护 `core/contracts.py` 等公共契约，保证跨模块对象和端口稳定；
- 维护 `core/context.py`，负责消息、上下文裁剪和 token 预算；
- 维护 `core/session.py` 和会话存储端口；
- 维护 `core/agent.py`、`agents/coding_agent.py` 及 Agent 循环；
- 维护 `application.py` 组合根，装配 Provider、Agent、工具、策略和会话；
- 为公共契约、上下文、会话和组合根补充确定性测试。

当前已完成：

- 冻结公共契约测试；
- 实现 `Context.trim()`；
- 实现 `FileSessionStore` 的保存、读取与分叉；
- 在 `Application` 中暴露 `session_store()`；
- `CodingAgent.run()` 在每次 Provider 请求前自动调用 `Context.trim()`；
- CLI 已通过 `Application.run()` 使用本地会话存储，默认保存在工作区 `.yczx/sessions`。

边界：

- 不直接实现 Provider 网络协议和供应商字段映射；
- 不实现工具内部的 Shell、文件系统操作或安全策略细节；
- 不实现复杂终端 UI、用户确认交互、memory、MCP 和插件；
- 不将模型供应商字段、API Key 或账单信息写入核心对象。

### 角色 B：模型、工具与安全

负责层：`providers/`、`tools/`、`safety/`。

主要职责：

- 实现和接入 Provider 适配器，包括网关、OpenAI-compatible 端点、Ollama 和测试替身；
- 完成 Provider 协议转换、超时、重试、取消、限流和错误映射；
- 实现工具注册表、工具基类、只读工具、写入与 Shell 工具的权限契约；
- 完善 `ToolPolicy`、`ToolPipeline` 和沙箱边界；
- 落实路径规范化、符号链接校验、敏感文件拒绝、超时和资源上限；
- 覆盖 Provider 与工具的路径逃逸、认证失败、限流、超时、取消和确认拒绝等测试。

边界：

- 供应商字段只在 Provider 适配器内解析，不进入 Agent、Context 或事件；
- 新增工具必须经过统一 `ToolPolicy`，不能绕过注册表或策略；
- 不得在核心层写入任何 Provider SDK 依赖；
- 不得把 API Key、敏感文件内容或未裁剪的工具结果写入日志和事件。

### 角色 C：终端、记忆与生态扩展

负责层：`ui/`、`memory/`、`mcp/`、`plugins/`，以及后续需要接入的生态能力。

主要职责：

- 完善 CLI 会话流程，基于 `Application.run()` 和 `session_store()` 支持会话列表、恢复和切换；
- 完善事件渲染、用户确认、诊断输出和复杂 TUI；
- 实现 memory 的持久化、摘要和召回；
- 实现 MCP 客户端和服务器适配，管理工具定义与权限声明；
- 实现插件清单、加载、注册、冲突检测和禁用策略；
- 保证所有外部能力默认关闭，并按最小权限、显式确认、审计和恢复契约接入。

边界：

- 不修改 Agent 循环或绕过统一工具策略；
- 不在 UI 中直接调用模型 SDK 或操作项目文件；
- 不把插件和 MCP 当作可信代码或可信网络服务；
- 不将终端会话 ID 当作账单编号或上游追踪 ID。

## 共享契约

以下对象和端口是团队并行开发的公共边界：

- `Message`、`ToolCall`、`ToolResult`、`AgentEvent`、`AgentResult`、`ProviderResponse`；
- `Provider`、`Tool`、`ToolRegistry`、`ToolPolicy`、`SessionStore`、`Context`；
- `Application` 的 `agent()`、`run()`、`session_id()`、`registry()`、`events()` 和 `session_store()`；
- `AppConfig`、`ProviderConfig`、`SandboxMode`、`ApprovalPolicy`。

公共契约变更必须：

- 先说明目的、影响范围和兼容策略；
- 同步更新对应测试和管理文档；
- 通知受影响角色，并由至少一名非作者复核；
- 在同一 PR 中完成代码、测试、文档和本说明的更新。

## 交接流程

1. 角色 A 提交并推送平台核心改动，PR 合入 `main`；
2. 角色 B、C 基于最新 `main` 创建各自短分支；
3. 开始前确认 `TEAM_DIVISION.md`、README 和 AGENTS 中的边界一致；
4. 每个 PR 只处理一个主题，分支命名遵循项目约定，不使用 `codex/*`；
5. 合并前至少完成项目规定的验证命令，并注明实际运行结果；
6. 涉及公共契约、权限、配置、事件或错误语义变化时，补充说明并请求交叉评审。

## 并行开发约定

- 角色之间优先通过 Git 分支、PR 和文档交接，不直接修改对方当前未提交的文件；
- 遇到未覆盖的跨层需求，先更新本文或提出 ADR，再进入实现；
- 不通过临时代码绕过统一策略、事件协议或会话存储端口；
- 不要为了实验能力而复制公共消息、Provider、工具和 Policy；
- 每个阶段结束后检查工作区，清理临时文件、日志、缓存和不再需要的产物。

## 当前状态

| 角色 | 当前状态 | 待办 |
| --- | --- | --- |
| A | 平台核心初始任务已完成，PR #4 待合并 | 等待评审结果；后续维护核心接口 |
| B | 尚未开始正式实现 | 真实 Provider、工具、安全策略与安全测试 |
| C | CLI 基础会话已由 A 接通 | 完整会话列表与恢复 UI、用户确认、memory、MCP、插件 |

## 文档维护

本文件由角色 A 创建并维护初次版本；后续角色边界、任务编号或验收标准变化时，由提出变更的角色在同一 PR 中更新本文件。文档中的能力描述必须与 `README.md` 和 `AGENTS.md` 保持一致，不得把计划中的能力写成已实现功能。
