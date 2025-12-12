# 05_TOOLS - Claude Code 工具库

> 版本：v2.2
> 最后更新：2024-12-12

---

## 概述

本目录包含 AI 协作开发框架的所有预置工具，用户可以直接复制到自己的项目中使用。

工具库包含三类工具：
- **Slash Commands (10 个)**：用户直接调用的命令
- **Skills (13 个)**：可复用的能力模块
- **Subagents (4 个)**：处理复杂多步骤任务的子代理

## 目录结构

```
05_TOOLS/
├── README.md              # 本文件
├── slash-commands/        # Slash Commands（10 个）
│   ├── init-project.md    # P3 - 初始化项目系统目录
│   ├── new-feature.md     # P0 - 创建新功能模块
│   ├── start-day.md       # P0 - 每日开始工作（git pull + resume）
│   ├── end-day.md         # P0 - 每日结束工作（更新进度 + commit + push）
│   ├── gen-demo.md        # P2 - 生成 Demo + Mock API
│   ├── check-progress.md  # P1 - 查看进度状态
│   ├── resume.md          # P0 - 断点恢复
│   ├── daily-summary.md   # P0 - 生成每日总结
│   ├── run-tests.md       # P2 - 执行测试
│   └── release.md         # P2 - 生成发布说明
├── skills/                # Skills（13 个）
│   ├── README.md
│   ├── progress_updater.md     # P0 - 更新 PROGRESS_LOG
│   ├── review_alignment.md     # P1 - 检查代码与设计一致性
│   ├── ui_demo.md              # P1 - 生成 UI Demo
│   ├── mock_api_generator.md   # P1 - 生成 Mock API
│   ├── doc_generator.md        # P1 - 根据模板生成文档
│   ├── context_writer.md       # P2 - 生成 CONTEXT 文档
│   ├── spec_validator.md       # P2 - 检查 SPEC 完整性
│   ├── design_from_demo.md     # P2 - 从 Demo 反推 API 契约
│   ├── test_runner.md          # P2 - 执行测试
│   ├── test_report_generator.md # P2 - 生成测试报告
│   ├── changelog_updater.md    # P2 - 更新 CHANGELOG
│   ├── system_scaffolder.md    # P3 - 生成目录结构
│   └── schema_generator.md     # P3 - 生成 DB Schema
└── subagents/             # Subagents（4 个）
    ├── README.md
    ├── spec_writer.md          # P1 - 生成 SPEC 文档
    ├── progress_tracker.md     # P1 - 生成 DAILY_SUMMARY
    ├── test_plan_writer.md     # P2 - 生成测试计划
    └── release_summarizer.md   # P2 - 生成 RELEASE_NOTE
```

## 安装方式

### 方式 1：手动复制

将 `slash-commands/` 目录下的所有 `.md` 文件复制到你的项目的 `.claude/commands/` 目录：

```bash
# 在你的项目根目录执行
mkdir -p .claude/commands

# 复制所有 slash commands
cp /path/to/ai-coding-org/docs/_system/CC_COLLABORATION/05_TOOLS/slash-commands/*.md \
   .claude/commands/
```

### 方式 2：使用安装脚本

```bash
# 在 ai-coding-org 项目根目录执行
./scripts/init-claude-tools.sh --target=/path/to/your-project
```

## 工具列表

### Slash Commands

| 命令 | 优先级 | 阶段 | 用途 |
|------|--------|------|------|
| `/init-project` | P3 | Phase 0 | 初始化 _system 目录和基础文档 |
| `/new-feature <name>` | P0 | Phase 1 | 创建功能模块目录和初始文档 |
| `/start-day [feature]` | P0 | 跨阶段 | 每日开始：git pull + 恢复上下文 |
| `/end-day [feature]` | P0 | 跨阶段 | 每日结束：更新进度 + commit + push |
| `/gen-demo <feature>` | P2 | Phase 3 | 生成 Demo.vue + Mock API |
| `/check-progress <feature>` | P1 | Phase 5 | 查看当前进度状态 |
| `/resume <feature>` | P0 | Phase 5 | 断点恢复，读取 checkpoint 继续 |
| `/daily-summary` | P0 | Phase 5 | 从 PROGRESS_LOG 生成今日总结 |
| `/run-tests <feature>` | P2 | Phase 6 | 执行测试并生成报告 |
| `/release <feature> <version>` | P2 | Phase 7 | 生成 RELEASE_NOTE 并打 tag |

### Skills（13 个）

| Skill | 优先级 | 阶段 | 用途 |
|-------|--------|------|------|
| `progress_updater` | P0 | Phase 5 | 自动更新 PROGRESS_LOG |
| `review_alignment` | P1 | Phase 5 | 检查代码与 DESIGN 一致性 |
| `ui_demo` | P1 | Phase 3 | 根据 SPEC + UI System 生成 Demo |
| `mock_api_generator` | P1 | Phase 3 | 根据 SPEC 生成 Mock API |
| `doc_generator` | P1 | 跨阶段 | 根据模板生成任意标准文档 |
| `context_writer` | P2 | Phase 1 | 根据需求描述生成 CONTEXT |
| `spec_validator` | P2 | Phase 2 | 检查 SPEC 完整性和一致性 |
| `design_from_demo` | P2 | Phase 4 | 从 Demo Mock API 反推 API 契约 |
| `test_runner` | P2 | Phase 6 | 执行测试（Chrome MCP / API） |
| `test_report_generator` | P2 | Phase 6 | 汇总测试结果生成报告 |
| `changelog_updater` | P2 | 跨阶段 | 更新文档的 CHANGELOG |
| `system_scaffolder` | P3 | Phase 0 | 根据 Profile 生成目录结构 |
| `schema_generator` | P3 | Phase 4 | 根据 DESIGN 生成 DB Schema |

### Subagents（4 个）

| Subagent | 优先级 | 阶段 | 用途 |
|----------|--------|------|------|
| `spec_writer` | P1 | Phase 2 | 根据 CONTEXT 生成 SPEC 文档 |
| `progress_tracker` | P1 | Phase 5 | 解析 PROGRESS_LOG 生成 DAILY_SUMMARY |
| `test_plan_writer` | P2 | Phase 6 | 根据 SPEC 生成测试计划 |
| `release_summarizer` | P2 | Phase 7 | 汇总信息生成 RELEASE_NOTE |

## 使用示例

### 1. 创建新功能

```
你：/new-feature user-auth

CC：好的，我来为你创建 user-auth 功能模块...
    ✓ 创建目录 docs/user-auth/
    ✓ 生成 00_CONTEXT.md 框架
    ✓ 生成 30_PROGRESS_LOG.yaml

    请补充 00_CONTEXT.md 中的功能描述和目标。
```

### 2. 恢复工作

```
你：/resume user-auth

CC：正在读取 user-auth 的断点信息...

    📍 上次状态：
    - Session: cc-2024-12-11-001
    - 最后编辑: src/auth/login.vue
    - 最后操作: 完成登录表单 UI
    - 下一步: 实现登录 API 调用

    📂 相关文件：
    - docs/user-auth/10_DESIGN_FINAL.md
    - docs/user-auth/30_PROGRESS_LOG.yaml

    是否继续上次的工作？
```

### 3. 每日总结

```
你：/daily-summary

CC：正在生成今日工作总结...

    📅 2024-12-11 工作总结

    ✅ 已完成：
    - [user-auth] 完成登录表单 UI (CODE-003)
    - [user-auth] 完成密码验证逻辑 (CODE-004)

    🔄 进行中：
    - [user-auth] 登录 API 调用 (CODE-005)

    📝 已生成: docs/user-auth/31_DAILY_SUMMARY/2024-12-11.md
```

## 注意事项

1. **依赖项目结构**：这些工具假设项目遵循 `04_AI_WORKFLOW.md` 定义的目录结构
2. **文档模板**：部分命令会引用 `03_TEMPLATES/` 下的模板
3. **YAML 解析**：`/resume` 和 `/check-progress` 需要读取 YAML 文件

## 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| v2.2 | 2024-12-12 | 新增 /start-day 和 /end-day 每日工作流命令，完成测试验证 |
| v2.1 | 2024-12-12 | 更新命令数量为 10 个 |
| v2.0 | 2024-12-11 | 完整版本，新增 13 个 Skills 和 4 个 Subagents |
| v1.0 | 2024-12-11 | 初始版本，包含 8 个 Slash Commands |
