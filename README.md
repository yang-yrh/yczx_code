# YCZX Code

YCZX Code（命令名 `yczx`）是一个面向代码阅读与项目理解的轻量级终端 Coding Agent。项目以清晰、可测试、可替换的分层 Agent 架构为目标，交互参考 Claude Code，但不复刻其全部能力。

它是燕中生态的本地 Agent 客户端：官方配置通过燕中统一 API 网关调用模型，独立开源使用可通过 Provider 适配器连接兼容端点。模型供应商、额度和账单不会进入 Agent 核心。

> 当前状态：预览纵向切片可运行。CLI `run` 命令通过 FakeProvider + 计算器工具走通一次有界 ReAct 循环（模型→工具→回填→最终回答），事件流全程记录并渲染。公共契约、模型适配端口、工具、安全策略、Agent 各层已就位；真实 Provider、文件只读工具、内存、MCP、插件与复杂 TUI 仍以占位或待实现形式存在，未将计划中的能力写成已实现功能。

## 目标

用户在本地代码库中启动会话后，Agent 调用工具查找证据、修改代码并运行验证：

```bash
yczx [WORKSPACE]
```

省略 `WORKSPACE` 时使用当前目录。

初期目标是：

- 单 Agent、单一有界 ReAct 循环与连续终端会话；
- 一个 OpenAI-compatible Provider 与测试用 FakeProvider；
- `list_dir`、`read_file`、`search_files`、`get_project_rules` 等只读工具；
- 工作区隔离、敏感文件拒绝与资源限制；
- 确定性测试、GitHub Actions 与最小项目文档。

## 开发环境

项目要求 Python 3.12，使用 uv 管理仓库内的 `.venv`：

```bash
uv sync --dev
uv run yczx --help
uv run yczx run --task "2 * 8"
uv run pytest
```

增加运行依赖使用 `uv add <package>`，增加开发依赖使用 `uv add --dev <package>`。不得使用全局 `pip` 安装项目依赖。

`yczx run` 使用 FakeProvider 离线演示工具调用与 ReAct 循环，无需 API Key。接通真实模型后，将 Provider 替换为网关或兼容端点适配器即可。

## 目录结构（分层）

框架按分层组织，便于分工与逐步实现：

```text
src/yczx_code/
├─ core/          # 平台层：契约、配置、Agent 基类、会话、上下文、事件流
├─ providers/     # 模型层：网关、OpenAI-compatible、Ollama、测试替身
├─ tools/         # 工具层：基类、注册、流水线、只读/写入/Shell
├─ safety/        # 安全层：统一工具策略、沙箱边界
├─ agents/        # Agent 实现：CodingAgent、子 Agent 编排
├─ memory/        # 记忆层：持久化、摘要、召回（占位）
├─ mcp/           # MCP 扩展（占位）
├─ plugins/       # 插件层（占位）
├─ ui/            # 终端层：CLI、渲染、确认、TUI（占位）
├─ application.py # 组合根：装配各层
└─ __main__.py    # 包入口
```

建议分工：

- `core/` + `agents/`：Agent 循环、会话与上下文；
- `providers/` + `tools/` + `safety/`：模型接入、工具与安全策略；
- `ui/` + `memory/` + `mcp/` + `plugins/`：终端、记忆与生态扩展。

## 架构

```text
CLI -> Application -> Agent -> Provider 端口
                             +-> Context
                             +-> Tool Registry -> ToolPolicy -> Tool
                             +-> AgentEvent -> 渲染 / 观测
```

CLI 只负责输入输出；Agent、Provider、工具、上下文、事件与安全策略通过公共对象连接。详见 [AGENTS.md](AGENTS.md)。

## 文档

- [Agent 协作约定](AGENTS.md)
- [来源说明](NOTICE)
- [许可证](LICENSE)

## 提交前检查

```bash
uv lock --check
uv run ruff check .
uv run pytest
git diff --check
```

所有变更通过符合命名规则的短分支和 Pull Request 合入 `main`，具体规则见 [AGENTS.md](AGENTS.md)。

除单独标注的第三方内容外，本仓库自主代码与文档采用 [GNU Affero General Public License v3.0](LICENSE)。
