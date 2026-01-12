# Subagents - 子代理模块

> 版本：v2.0
> 最后更新：2026-01-09
> 状态：已实现

---

## 概述

Subagents 是 Claude Code 的子代理模块，用于处理复杂的多步骤任务。每个 Subagent 定义一个完整的工作流程，可以调用多个 Skills 来完成任务。

**与其他工具的区别**：
- **Slash Commands**：用户直接调用的命令，触发单个操作
- **Skills**：单一、专注的能力，如"更新 PROGRESS_LOG"
- **Subagents**：复杂的工作流，编排多个 Skills 完成复杂任务，有自己的执行上下文

**Subagents 的特点**：
- 独立执行上下文
- 编排多个 Skills
- 产出完整的文档或报告

## 目录

```
subagents/
├── README.md               # 本文件
├── spec_writer.md          # 生成 SPEC 文档
├── progress_tracker.md     # 生成 DAILY_SUMMARY
├── test_plan_writer.md     # 生成测试计划
├── expert_reviewer.md      # 独立评审设计和代码
└── release_summarizer.md   # 生成 RELEASE_NOTE
```

## Subagents 列表（5 个）

| Subagent | Phase | 用途 | 依赖能力 | 状态 |
|----------|-------|------|----------|------|
| `spec_writer` | Phase 2 | 根据 CONTEXT 生成 SPEC 文档 | doc_generator + 内置验证逻辑 | ✅ 已实现 |
| `progress_tracker` | Phase 5 | 解析 PROGRESS_LOG 生成 DAILY_SUMMARY | doc_generator + 内置进度解析 | ✅ 已实现 |
| `test_plan_writer` | Phase 6 | 根据 SPEC 生成测试计划 | doc_generator | ✅ 已实现 |
| `expert_reviewer` | Phase 4-6 | 独立评审设计和代码 | 内置评审逻辑 | ✅ 已实现 |
| `release_summarizer` | Phase 7 | 汇总生成发布说明 | doc_generator + 内置汇总逻辑 | ✅ 已实现 |

## 各 Subagent 详细说明

### `spec_writer`

**阶段**：Phase 2 Spec

**功能**：根据 10_CONTEXT.md 生成完整的 SPEC 文档（API_SPEC 或 UI_FLOW_SPEC）

**工作流程**：
```
1. 读取 10_CONTEXT.md
2. 分析功能类型（前端/后端/全栈）
3. 调用 doc_generator 生成 SPEC 框架
4. 执行内置验证逻辑检查完整性
5. 更新 DOC_CHANGELOG.md 记录变更
```

### `progress_tracker`

**阶段**：Phase 5 Code

**功能**：解析 PROGRESS_LOG，生成 DAILY_SUMMARY

**工作流程**：
```
1. 读取 90_PROGRESS_LOG.yaml
2. 提取今日完成的任务
3. 统计进度百分比
4. 调用 doc_generator 生成每日总结
```

### `test_plan_writer`

**阶段**：Phase 6 Test

**功能**：根据 SPEC 生成测试计划

**工作流程**：
```
1. 读取 21_UI_FLOW_SPEC.md 或 20_API_SPEC.md
2. 提取测试场景
3. 生成测试用例
4. 调用 doc_generator 生成 60_TEST_PLAN.md
```

### `expert_reviewer`

**阶段**：Phase 4-6

**功能**：调用外部 AI（OpenAI GPT-4）进行独立评审，避免「自己审自己」

**工作流程**：
```
1. 收集待评审材料（DESIGN/代码）
2. 执行内置评审逻辑（多维度分析）
3. 解析评审结果（GO/REVISE/BLOCK）
4. 生成 REVIEW_REPORT.md
5. 记录 REVIEW_ACTIONS.yaml
```

### `release_summarizer`

**阶段**：Phase 7 Deploy

**功能**：汇总 PROGRESS_LOG + TEST_REPORT 生成 RELEASE_NOTE

**工作流程**：
```
1. 读取 90_PROGRESS_LOG.yaml
2. 读取 61_TEST_REPORT.md
3. 汇总功能变更
4. 调用 doc_generator 生成 70_RELEASE_NOTE.md
5. 更新项目 CHANGELOG.md
```

## 使用方式

### 1. 通过 Slash Command 调用

```
/daily-summary
→ 内部调用 progress_tracker subagent

/expert-review docs/user-auth --phase=4
→ 内部调用 expert_reviewer subagent

/release user-auth
→ 内部调用 release_summarizer subagent
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

## 元信息
- 类型: Subagent
- Phase: 适用阶段
- 优先级: P0 / P1 / P2

## 能力描述
{详细说明这个 subagent 能做什么}

## 输入
{需要什么输入参数}

## 输出
{会产出什么结果}

## 工作流程
{分步骤说明执行流程}

## 调用的 Skills
{列出会调用的 Skills}

## 示例
{使用示例}

## 注意事项
{使用时的注意点}
```

## 与 Skills 的协作关系

```
┌─────────────────────────────────────────────────────────┐
│                    Slash Command                        │
│                    (用户调用)                            │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                     Subagent                            │
│                  (编排执行流程)                           │
└─────────────────────┬───────────────────────────────────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
     ┌─────────┐ ┌─────────┐ ┌─────────┐
     │ Skill 1 │ │ Skill 2 │ │ Skill 3 │
     └─────────┘ └─────────┘ └─────────┘
```

**示例**：
```
/expert-review docs/user-auth --phase=4
    │
    └── expert_reviewer (Subagent)
            │
            ├── openai_expert_review (Skill) - 调用 GPT-4 评审
            └── doc_generator (Skill) - 生成报告
```

## 与工作流的关系

```
Phase 2 Spec    → spec_writer
Phase 4-6       → expert_reviewer（可在设计、编码、测试阶段使用）
Phase 5 Code    → progress_tracker
Phase 6 Test    → test_plan_writer
Phase 7 Deploy  → release_summarizer
```

## 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| v2.0 | 2026-01-09 | 更新至 5 个 Subagents，添加 expert_reviewer |
| v1.0 | 2024-12-11 | 初始版本，实现 4 个 Subagents |

---

_CC_COLLABORATION Framework v3.1_
