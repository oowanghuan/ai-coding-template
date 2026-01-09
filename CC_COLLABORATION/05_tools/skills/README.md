# Skills - 技能模块

> 版本：v2.0
> 最后更新：2026-01-09
> 状态：已实现

---

## 概述

Skills 是 Claude Code 的技能模块，每个 Skill 定义一个专注的能力，可以被 Slash Commands 或 Subagents 调用。

**与其他工具的区别**：
- **Slash Commands**：用户直接调用的命令，如 `/new-feature`
- **Skills**：可复用的能力模块，被其他工具调用或在特定条件下自动触发
- **Subagents**：复杂的工作流，编排多个 Skills 完成复杂任务

**Skills 的特点**：
- 专注单一职责
- 可被多个 Commands/Subagents 复用
- 部分 Skills 在特定条件下自动触发

## 目录

```
skills/
├── README.md                  # 本文件
│
├── # 进度管理（2 个）
├── progress_updater.md        # 更新 PROGRESS_LOG
├── gate_checker.md            # 检查 Phase Gate 条件
│
├── # 文档生成（4 个）
├── context_writer.md          # 生成 CONTEXT 文档
├── doc_generator.md           # 根据模板生成文档
├── changelog_updater.md       # 更新 CHANGELOG
├── schema_generator.md        # 生成 DB Schema
│
├── # Demo & Mock（3 个）
├── ui_demo.md                 # 生成 UI Demo
├── mock_api_generator.md      # 生成 Mock API
├── design_from_demo.md        # 从 Demo 反推 API 契约
│
├── # 验证 & 评审（4 个）
├── spec_validator.md          # 检查 SPEC 完整性
├── review_alignment.md        # 检查代码与设计一致性
├── openai_expert_review.md    # 调用 OpenAI 独立评审
│
├── # 测试（2 个）
├── test_runner.md             # 执行测试
├── test_report_generator.md   # 生成测试报告
│
└── # 初始化
    └── system_scaffolder.md   # 生成目录结构
```

## Skills 列表（15 个）

### 进度管理

| Skill | Phase | 触发条件 | 用途 | 状态 |
|-------|-------|----------|------|------|
| `progress_updater` | Phase 5 | 任务状态变更 | 自动更新 PROGRESS_LOG | ✅ 已实现 |
| `gate_checker` | 跨阶段 | Phase 切换前 | 检查 Gate 条件是否满足 | ✅ 已实现 |

### 文档生成

| Skill | Phase | 触发条件 | 用途 | 状态 |
|-------|-------|----------|------|------|
| `context_writer` | Phase 1 | 创建新功能时 | 生成 10_CONTEXT.md | ✅ 已实现 |
| `doc_generator` | 跨阶段 | 需要生成文档时 | 根据模板生成任意文档 | ✅ 已实现 |
| `changelog_updater` | 跨阶段 | 文档变更时 | 更新 CHANGELOG | ✅ 已实现 |
| `schema_generator` | Phase 4 | 需要数据模型时 | 生成数据库 Schema 定义 | ✅ 已实现 |

### Demo & Mock

| Skill | Phase | 触发条件 | 用途 | 状态 |
|-------|-------|----------|------|------|
| `ui_demo` | Phase 3 | Demo 阶段 | 根据 SPEC + UI System 生成 Demo | ✅ 已实现 |
| `mock_api_generator` | Phase 3 | Demo 阶段 | 根据 SPEC 生成 Mock API | ✅ 已实现 |
| `design_from_demo` | Phase 4 | Demo 评审后 | 从 Demo Mock API 反推正式 API 契约 | ✅ 已实现 |

### 验证 & 评审

| Skill | Phase | 触发条件 | 用途 | 状态 |
|-------|-------|----------|------|------|
| `spec_validator` | Phase 2 | Spec 完成时 | 检查 SPEC 完整性和一致性 | ✅ 已实现 |
| `review_alignment` | Phase 5 | 任务完成后 | 检查代码与 DESIGN 一致性 | ✅ 已实现 |
| `openai_expert_review` | Phase 4-6 | 专家评审时 | 调用 OpenAI GPT-4 独立评审 | ✅ 已实现 |

### 测试

| Skill | Phase | 触发条件 | 用途 | 状态 |
|-------|-------|----------|------|------|
| `test_runner` | Phase 6 | Test 阶段 | 执行测试计划（Chrome MCP / API 测试） | ✅ 已实现 |
| `test_report_generator` | Phase 6 | 测试完成后 | 汇总测试结果生成报告 | ✅ 已实现 |

### 初始化

| Skill | Phase | 触发条件 | 用途 | 状态 |
|-------|-------|----------|------|------|
| `system_scaffolder` | Phase 0 | 初始化项目时 | 根据 Profile 生成目录结构 | ✅ 已实现 |

## 使用方式

### 1. 被 Slash Command 自动调用

大多数 Skills 被 Slash Commands 内部调用，用户无需显式操作：

```
/check-gate user-auth --phase=2
→ 内部调用 gate_checker skill

/new-feature user-auth
→ 内部调用 context_writer skill
```

### 2. 条件触发（自动）

部分 Skills 在特定条件下自动触发：

```
任务状态变更 → progress_updater 自动更新 PROGRESS_LOG
Phase 切换前 → gate_checker 自动检查条件
Spec 完成时 → spec_validator 自动验证
```

### 3. 直接调用

```
请使用 progress_updater skill 更新 docs/user-auth/90_PROGRESS_LOG.yaml，
将任务 CODE-003 标记为 done。
```

### 4. 被 Subagent 编排

Subagent 在执行复杂任务时会自动调用相关 Skills：

```
spec_writer (Subagent)
├── 调用 doc_generator skill (生成 SPEC 框架)
├── 调用 spec_validator skill (验证完整性)
└── 调用 changelog_updater skill (更新 CHANGELOG)
```

## Skill 文件格式

每个 Skill 文件遵循统一格式：

```markdown
# {skill_name} - {简短描述}

## 元信息
- 类型: Skill
- Phase: 适用阶段
- 触发条件: 何时触发
- 优先级: P0 / P1 / P2

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

## 与工作流的关系

```
Phase 0 Foundation    → system_scaffolder
Phase 1 Kickoff       → context_writer
Phase 2 Spec          → spec_validator
Phase 3 Demo          → ui_demo, mock_api_generator
Phase 4 Design        → design_from_demo, schema_generator
Phase 5 Code          → progress_updater, review_alignment
Phase 6 Test          → test_runner, test_report_generator

跨阶段通用            → gate_checker, doc_generator, changelog_updater, openai_expert_review
```

## 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| v2.0 | 2026-01-09 | 更新至 15 个 Skills，添加 gate_checker 和 openai_expert_review |
| v1.0 | 2024-12-11 | 初始版本，实现 13 个 Skills |

---

_CC_COLLABORATION Framework v3.1_
