# YCZX Code 开发约定

工作区总约束见 `../AGENTS.md`，生态架构与跨系统契约见 `../docs/`。本仓自主代码采用 AGPL-3.0；参考实现、SDK 和其他依赖保留各自许可证与署名。

## 产品与生态职责

YCZX Code（命令 `yczx`）是燕中生态的本地 Coding Agent。它负责在用户指定的代码库中组织模型、上下文、工具、权限确认和终端交互，不负责成员身份、模型额度或供应商路由。

- 燕中官方服务默认通过 `api_yanchuaner` 统一 API 网关调用模型，使用网关颁发的主体凭据和稳定错误契约。
- CLI 核心只依赖 `Provider` 契约，不依赖 New API、LiteLLM 或任何供应商 SDK 的领域对象。
- 开源独立使用允许配置其他兼容端点，但必须通过 Provider 适配器，不能让供应商字段进入 Agent、工具或上下文模块。
- 主站身份由 `web_yanchuaner` 管理；CLI 不保存主站密码，不复制用户表。
- `yczx_code_lab` 是学习与实验仓，代码不能直接复制进入正式主线；采用时需在本仓重新设计、测试、评审并登记来源。

当前实现状态以 `README.md` 为准；边界约定见本文件。计划中的 ReAct、工具或插件不得写成已实现能力。

## 核心架构

```text
CLI -> Application -> Agent -> Provider 端口
                             +-> Context
                             +-> Tool Registry -> ToolPolicy -> Tool
                             +-> AgentEvent -> 渲染 / 观测
```

- CLI 只解析参数、收集确认并渲染事件，不调用模型 SDK 或直接操作项目文件。
- Application 是组合根，负责创建配置、Provider、Agent、工具、策略和会话。
- Agent 只处理公共消息、结构化工具调用、停止条件和事件，不执行 Shell 或文件系统操作。
- Provider 负责燕中网关或兼容端点的协议转换、超时、重试和错误映射。
- Tool Registry 负责名称、schema 和分发；每个工具仍须经过统一 Policy。
- Context 负责项目规则、消息、结果裁剪和 token 预算，不持有终端 UI。
- Event 是 CLI、日志和后续可观测性唯一输出边界，不暴露隐藏推理。

扩展必须进入明确端口。新增 Provider、工具或渲染器不应修改 Agent 循环；新增 Agent 策略不应绕过同一工具策略与事件协议。

代码按分层组织为 `core/`、`providers/`、`tools/`、`safety/`、`agents/`、`memory/`、`mcp/`、`plugins/`、`ui/` 等包，`application.py` 为组合根。当前只实现 CLI 与只读能力，其余层以接口或占位形式给出。

## 当前 Preview 边界

- 正式主线使用单 Agent、单个有界 ReAct 循环。
- 当前实现只读能力：`list_dir`、`read_file`、`search_files`、`get_project_rules`。
- `memory/`、`mcp/`、`plugins/`、子 Agent 与 TUI 等层作为接口/占位搭好，对应能力尚未实现，不得写成已实现功能。
- 会话在进程内存中，不提供长期记忆或云端同步。
- 文件写入、任意 Shell、MCP、多 Agent、插件与复杂 TUI 需先具备操作预览、显式确认、最小权限、审计与恢复契约，完成前保持关闭。
- Plan-and-Solve、Reflection 等实验只在 Lab 或独立分支验证，不并列复制公共消息、工具、Provider 和 Policy。

## 公共契约

跨模块对象使用标准库 `dataclass`、`Enum` 和 `Protocol` 等清楚类型，至少区分：

- `Message`：可提交给模型的公开角色与内容；
- `ToolCall`：调用 ID、工具名和已解析参数；
- `ToolResult`：状态、结构化结果、摘要、错误与截断游标；
- `AgentEvent`：模型请求、工具请求、确认、结果、失败和最终回答事件；
- `AgentResult`：停止原因、最终回答与公开用量；
- `Provider`：公共请求到公共响应的转换；
- `Tool`：名称、说明、参数 schema 与执行入口；
- `PolicyDecision`：允许、拒绝或需要用户确认，以及稳定原因码。

供应商请求 ID、错误字段和计费信息只在 Provider 适配器解析，再映射为生态通用字段。跨生态追踪使用 `request_id`、`trace_id` 与网关 `upstream_request_id`，不把终端会话 ID 当账单编号。

## 安全红线

- 所有路径先基于解析后的 `workspace_root` 规范化、解析符号链接并验证仍在根目录内。
- `.env*`、私钥、证书、凭据、`.git/` 对象、数据库和其他敏感或二进制文件默认拒绝读取。
- 模型输出、仓库内容和工具参数均视为不可信输入。模型不能自行提高权限或改变资源限制。
- 不打印完整 API Key、Authorization 头、系统提示、敏感文件内容或未裁剪的工具结果。
- 每轮限制 Agent 步数、重复调用、文件字节、目录项、搜索结果、上下文长度、超时和重试。
- 写入与 Shell 能力必须先具备操作预览、显式确认、最小权限、审计、超时、输出限制和恢复测试；不得通过一个布尔开关整体放行。
- 插件与 MCP 将来进入时按不可信代码和不可信网络服务处理，声明权限、来源、版本、数据出口和禁用方式。

安全约束见上文「安全红线」。

## 模块化与插件

- 只有存在第二个真实实现、测试替身或稳定替换需求时才抽象接口，不创建空插件目录。
- 插件只能通过版本化 SDK 使用公开契约，不导入 CLI 内部模块或修改全局注册表。
- 清单至少声明插件 ID、版本、兼容 API、入口、能力、权限、网络与数据访问、许可证。
- 能力默认关闭，由用户或管理员显式启用；冲突的工具名、未知权限和不兼容版本直接拒绝加载。
- 内置能力与外部插件走同一 Registry、Policy、Event 和审计路径，不能保留特权旁路。

插件协议落地前先以架构决策记录（ADR）定义兼容与撤销策略，不以加载任意 Python 包作为插件系统。

### 扩展点（新增组件在哪里接）

- 新增 Provider：实现 `core.contracts.Provider` 端口，置于 `providers/`，由 `application.py` 装配。
- 新增工具：继承 `tools/base.Tool`（声明 `name`、`description`、`parameters`、`read_only`、`concurrency_safe`），在 `ToolRegistry` 注册，必须经 `ToolPolicy`。
- 新增渲染：实现 `ui/render.Renderer` 端口；UI 不进入 Agent 核心。
- 新增记忆：实现 `memory/store.MemoryStore` 端口。
- 新增会话存储：实现 `core/session.SessionStore` 端口。
- 新增插件：按 `plugins/loader.PluginManifest` 声明，经 `PluginRegistry` 注册，与内置能力同走策略与审计。
- 新增 Agent：继承 `core/agent.Agent`，在 `agents/` 提供实现。

统一原则：新增组件不应修改 Agent 循环；不绕过统一工具策略与事件协议；不在注册表之外另开特权通道。

## 环境与代码

- 使用 Python 3.12、uv 和仓库内 `.venv`；通过 `uv sync --dev` 同步，不使用全局 `pip`。
- 新运行依赖使用 `uv add`，开发依赖使用 `uv add --dev`，同时维护 `pyproject.toml` 与 `uv.lock`。
- 产品代码位于 `src/yczx_code/`，测试位于 `tests/`。标识符使用英文，中文文档与必要注释说明设计意图。
- 不捕获宽泛异常后静默继续；错误在模块边界映射为稳定类型，并保留可排查但已脱敏的原因。
- FakeProvider、临时目录和确定性 fixture 是核心测试设施，单元测试不得依赖真实付费模型。

## 代码与命名约定

- 语言与风格：Python 3.12；`ruff` 为 lint 标准（line-length=100，选中 E/F/I/UP/B/SIM），格式化用 `ruff format`。
- 命名：模块、变量、函数用 `snake_case`；公开契约类用 `PascalCase`；常量用 `UPPER_SNAKE_CASE`。模块用名词（如 `context`、`provider`），函数用动词短语（如 `resolve_workspace`、`register_tool`）。
- 类型：公共对象使用 `dataclass`、`StrEnum`、`Protocol`；跨模块接口给出明确类型标注，并保留 `from __future__ import annotations`。
- 错误：在模块边界映射为稳定类型（如 `ProviderError`、`ToolError`），不静默吞掉宽泛异常，错误信息保留可定位但已脱敏的原因。
- 导入：使用相对导入，顺序由 ruff/isort 管理；避免循环依赖，跨层契约集中在 `core/contracts.py`。
- 注释：中文注释说明必要设计意图与边界条件，不重复代码本身；模块需有 docstring 说明职责。
- 测试：单元测试使用 FakeProvider、临时目录与确定性 fixture，不调用真实付费模型。
- 命名一致性：包名（import）＝ 产品名，命令名＝ 短别名，发布名＝ 连字符版。产品名暂定 `yczx_code`（命令 `yczx`、发布名 `yczx-code`）；定稿后需整体同步修正：包目录 `src/<new>/`、import 名、`pyproject.toml` 的 `name` 与入口、`__main__` 脚本，以及 `AGENTS.md`/`README.md` 中的命令名。

## 提交与 Pull Request

- 分支：`main` 为长期分支；开发分支匹配 `^(feat|fix|docs|test|refactor|chore|ci|revert)/[a-z0-9]+(-[a-z0-9]+)*$`。
- 提交与标题：采用 Conventional Commits `type(scope): subject`，type 为 feat/fix/docs/test/refactor/chore/ci/revert，subject 不超过 72 字符；标题 type 需与分支 type 一致。
- 一个 PR 只处理一个主题；不直接推送、不强制更新、不删除 `main`，main 通过 CI 与至少一位评审者后合并。
- PR 说明须写出：目的、实际改动、亲自运行的验证命令与结果、来源与许可、已知限制。
- 公共 Message/Provider/Tool/Policy/Event/配置/错误语义变化需受影响模块维护者与至少一名非作者复核。

## 文档

- `README.md`：项目介绍、开发环境与提交检查
- `NOTICE`：来源与许可说明

行为、配置、公共对象、权限或命令变化时，在同一改动中更新文档。个人实验结论留在 Lab，正式架构只保留已选择的设计与代价。

## 验证与完成条件

至少运行：

```bash
uv lock --check
uv run ruff check .
uv run pytest
git diff --check
```

涉及 CLI 时运行 `uv run yczx --help`；涉及 Provider 时使用 FakeProvider 与假网关响应覆盖成功、限流、认证失败、超时、取消和流式中断；涉及工具时覆盖路径逃逸、符号链接、敏感文件、超限与确认拒绝。

保留用户已有改动，不直接推送 `main`，不代替维护者合并。分支使用工作区约定前缀，不使用 `codex/*`。完成时必须能说明当前行为、尚未实现能力、验证结果和安全边界。
