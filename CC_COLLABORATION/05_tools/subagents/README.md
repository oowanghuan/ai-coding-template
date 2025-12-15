# Subagents - 子代理模块

> 版本：v1.0
> 最后更新：2024-12-11

---

## 概述

Subagents 是 Claude Code 的子代理模块，用于处理复杂的多步骤任务。每个 Subagent 定义一个完整的工作流程，可以调用多个 Skills 来完成任务。

Subagents 与 Skills 的区别：
- **Skills**：单一、专注的能力，如"更新 PROGRESS_LOG"
- **Subagents**：复杂的工作流，编排多个 Skills 完成复杂任务

## 目录

```
subagents/
├── README.md               # 本文件
├── spec_writer.md          # P1 - 生成 SPEC 文档
├── progress_tracker.md     # P1 - 生成 DAILY_SUMMARY
├── test_plan_writer.md     # P2 - 生成测试计划
└── release_summarizer.md   # P2 - 生成 RELEASE_NOTE
```

## Subagents 列表

| Subagent | 阶段 | 优先级 | 用途 | 状态 |
|----------|------|--------|------|------|
| `spec_writer` | Phase 2 | P1 | 根据 CONTEXT 生成 SPEC 文档 | ✅ 已实现 |
| `progress_tracker` | Phase 5 | P1 | 解析 PROGRESS_LOG 生成 DAILY_SUMMARY | ✅ 已实现 |
| `test_plan_writer` | Phase 6 | P2 | 根据 SPEC 生成测试计划 | ✅ 已实现 |
| `release_summarizer` | Phase 7 | P2 | 汇总 PROGRESS_LOG + TEST_REPORT 生成 RELEASE_NOTE | ✅ 已实现 |

## 使用方式

Subagents 通常由 Slash Commands 调用，也可以直接请求使用：

### 1. 通过 Slash Command 调用

```
/daily-summary
→ 内部调用 progress_tracker subagent
```

### 2. 直接调用

```
请使用 spec_writer subagent 为 user-auth 功能生成 UI_FLOW_SPEC。

输入信息：
- 功能名称：user-auth
- CONTEXT 位置：docs/user-auth/10_CONTEXT.md
- SPEC 类型：ui（前端功能）
```

## Subagent 文件格式

每个 Subagent 文件遵循统一格式：

```markdown
# {subagent_name} - {简短描述}

## 能力描述
{详细说明这个 subagent 能做什么}

## 输入
{需要什么输入参数}

## 输出
{会产出什么结果}

## 工作流程
{分步骤说明执行流程，包括调用的 Skills}

## 调用的 Skills
{列出会调用的 Skills}

## 示例
{使用示例}

## 注意事项
{使用时的注意点}
```

## 与 Skills 的协作

Subagents 通过编排 Skills 来完成复杂任务：

```
spec_writer (Subagent)
├── 调用 doc_generator skill (生成 SPEC 框架)
├── 调用 spec_validator skill (验证完整性)
└── 调用 changelog_updater skill (更新 CHANGELOG)
```

## 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2024-12-11 | 初始版本，实现 4 个 Subagents |
