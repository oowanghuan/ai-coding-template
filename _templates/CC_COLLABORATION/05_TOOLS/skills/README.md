# Skills - 技能模块

> 版本：v1.0
> 最后更新：2024-12-11

---

## 概述

Skills 是 Claude Code 的技能模块，每个 Skill 定义一个专注的能力，可以被 Slash Commands 或 Subagents 调用。

Skills 与 Slash Commands 的区别：
- **Slash Commands**：用户直接调用的命令，如 `/new-feature`
- **Skills**：可复用的能力模块，被其他工具调用

## 目录

```
skills/
├── README.md                  # 本文件
├── progress_updater.md        # P0 - 更新 PROGRESS_LOG
├── review_alignment.md        # P1 - 检查代码与设计一致性
├── ui_demo.md                 # P1 - 生成 UI Demo
├── mock_api_generator.md      # P1 - 生成 Mock API
├── doc_generator.md           # P1 - 根据模板生成文档
├── context_writer.md          # P2 - 生成 CONTEXT 文档
├── spec_validator.md          # P2 - 检查 SPEC 完整性
├── design_from_demo.md        # P2 - 从 Demo 反推 API 契约
├── test_runner.md             # P2 - 执行测试
├── test_report_generator.md   # P2 - 生成测试报告
├── changelog_updater.md       # P2 - 更新 CHANGELOG
├── system_scaffolder.md       # P3 - 生成目录结构
└── schema_generator.md        # P3 - 生成 DB Schema
```

## Skills 列表

| Skill | 阶段 | 优先级 | 用途 | 状态 |
|-------|------|--------|------|------|
| `progress_updater` | Phase 5 | P0 | 自动更新 PROGRESS_LOG | ✅ 已实现 |
| `review_alignment` | Phase 5 | P1 | 检查代码与 DESIGN 一致性 | ✅ 已实现 |
| `ui_demo` | Phase 3 | P1 | 根据 SPEC + UI System 生成 Demo | ✅ 已实现 |
| `mock_api_generator` | Phase 3 | P1 | 根据 SPEC 生成 Mock API | ✅ 已实现 |
| `doc_generator` | 跨阶段 | P1 | 根据模板生成任意标准文档 | ✅ 已实现 |
| `context_writer` | Phase 1 | P2 | 根据需求描述生成 00_CONTEXT.md | ✅ 已实现 |
| `spec_validator` | Phase 2 | P2 | 检查 SPEC 完整性和一致性 | ✅ 已实现 |
| `design_from_demo` | Phase 4 | P2 | 从 Demo Mock API 反推正式 API 契约 | ✅ 已实现 |
| `test_runner` | Phase 6 | P2 | 执行测试计划（Chrome MCP / API 测试） | ✅ 已实现 |
| `test_report_generator` | Phase 6 | P2 | 汇总测试结果生成报告 | ✅ 已实现 |
| `changelog_updater` | 跨阶段 | P2 | 更新文档的 CHANGELOG | ✅ 已实现 |
| `system_scaffolder` | Phase 0 | P3 | 根据 Profile 生成目录结构 | ✅ 已实现 |
| `schema_generator` | Phase 4 | P3 | 根据 DESIGN 生成数据库 Schema | ✅ 已实现 |

## 使用方式

Skills 可以通过以下方式调用：

### 1. 在 Slash Command 中引用

```markdown
## 依赖 Skills
- `progress_updater` - 用于更新进度日志
- `doc_generator` - 用于生成文档
```

### 2. 直接调用

```
请使用 progress_updater skill 更新 docs/user-auth/30_PROGRESS_LOG.yaml，
将任务 CODE-003 标记为 done。
```

### 3. 被 Subagent 调用

Subagent 在执行复杂任务时会自动调用相关 Skills。

## Skill 文件格式

每个 Skill 文件遵循统一格式：

```markdown
# {skill_name} - {简短描述}

## 能力描述
{详细说明这个 skill 能做什么}

## 输入
{需要什么输入参数}

## 输出
{会产出什么结果}

## 执行步骤
{分步骤说明如何执行}

## 示例
{使用示例}

## 注意事项
{使用时的注意点}
```

## 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2024-12-11 | 初始版本，实现 13 个 Skills |
