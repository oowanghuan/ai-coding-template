# 04_AI_WORKFLOW.md
# AI 协作工作流总纲

> 版本：v1.4
> 最后更新：2025-01-02
> 状态：框架定稿，工具已实现

---

## 概述

本文档定义了 AI 协作开发的 **8 阶段工作流**，每个阶段包含：
- **环节目标**：这个阶段要达成什么
- **标准文档**：这个阶段要产出/更新什么文档
- **环节工具**：可用的 Skills / Subagents / Slash Commands
- **完成标准**：怎样算完成这个阶段

### 模板状态说明

| 图标 | 含义 |
|------|------|
| ✅ | 有标准模板，位于 `CC_COLLABORATION/03_templates/{phase}/` 目录 |
| 📄 | 有模板，位于 `CC_COLLABORATION/03_templates/_foundation/` 目录 |
| 📝 | 文件名固定，内容自由编写（无模板） |

---

## Phase 0: Foundation（基础建设）

### 环节目标
建立项目级的系统规范，为所有功能模块提供统一的约束和参考。

### 标准文档

| 文档 | 用途 | 模板/参考 | 状态 |
|------|------|----------|------|
| `_foundation/01_USER_JOURNEY.md` | **需求起源层** - 用户流程、系统责任、模块映射 | `01_USER_JOURNEY_TEMPLATE.md` | ✅ 有模板 |
| `_foundation/00_PROJECT_CONTEXT.md` | 项目背景、团队、领域知识 | `03_templates/01_kickoff/10_CONTEXT_TEMPLATE.md` | ✅ 有模板 |
| `_foundation/01_PROJECT_PROFILE.yaml` | 技术栈配置、工作流开关 | `03_templates/_common/01_PROJECT_PROFILE_TEMPLATE.yaml` | ✅ 有模板 |
| `_foundation/_api_system/*` | API 规则体系（4 层） | `03_templates/_foundation/_api_system_template/` | 📄 有模板 |
| `_foundation/03_DB_CONVENTIONS.md` | 数据库命名、索引策略 | `03_templates/_foundation/03_DB_CONVENTIONS_TEMPLATE.md` | 📄 有模板 |
| `_foundation/_ui_system/*` | UI 规则体系（6 层） | `03_templates/_foundation/_ui_system_template/` | 📄 有模板 |

> **说明**：`/init-project` 命令会根据 `CC_COLLABORATION/03_templates/_foundation/` 中的模板生成 `docs/_foundation/` 目录下的项目基础文件。

### 环节工具

| 类型 | 名称 | 用途 | 状态 |
|------|------|------|------|
| Slash Command | `/init-project` | 初始化 _foundation 目录和基础文档 | ✅ 已实现 |
| Skill | `system_scaffolder` | 根据 Profile 生成目录结构 | ✅ 已实现 |

### 完成标准
- [ ] `_foundation/` 目录结构完整
- [ ] `01_PROJECT_PROFILE.yaml` 配置正确
- [ ] 所有系统级文档已创建

### 负责角色
System Architect

---

## Phase 0.5: Foundation Gate（需求验证）

> **v1.4 新增**：在 Phase 0 与 Phase 1 之间引入 Foundation Gate 机制，确保需求起源层完整。

### 环节目标
验证 Foundation 文档的完整性，确保所有 P0 模块都可追溯到用户步骤，通过设计验证后才能进入功能开发。

### 核心理念

```
User Journey → System Responsibility → Module Mapping → Design Validation → Foundation Gate
     ↑                                                                              │
     └────────────────────────── 可追溯 ◀───────────────────────────────────────────┘
```

### 标准文档

| 文档 | 用途 | 模板/参考 | 状态 |
|------|------|----------|------|
| `_foundation/01_USER_JOURNEY.md` | 用户流程（U1→U2→...）、失败路径（F1, F2...）、系统责任、模块映射 | `01_USER_JOURNEY_TEMPLATE.md` | ✅ 有模板 |
| `_foundation/00_FOUNDATION_GATE.md` | Gate 规则定义、MVS 标准、检查项 | `00_FOUNDATION_GATE.md` | ✅ 有模板 |
| `_foundation/DESIGN_VALIDATION_RESULT.yaml` | 设计验证结果 | 自动生成 | 📝 运行时产物 |

### 环节工具

| 类型 | 名称 | 用途 | 状态 |
|------|------|------|------|
| Slash Command | `/doc-design-validation` | 执行设计验证，输出 PASS/FAIL | ✅ 已实现 |
| Slash Command | `/check-foundation-gate` | 检查 Foundation Gate 状态 | ✅ 已实现 |
| Slash Command | `/plan-features` | 生成功能开发清单（需先通过 Gate） | ✅ 已实现 |

### User Journey MVS（最小可通过要求）

| 必填区块 | 最小要求 |
|----------|----------|
| 用户画像 | ≥ 1 个主要用户 |
| 主成功路径 | ≥ 3 个用户步骤（U1, U2, U3...） |
| 失败路径 | ≥ 2 个失败场景（F1, F2...） |
| 系统责任声明 | 每个用户步骤都有「系统必须做」 |
| 模块映射表 | 所有 P0 模块都有对应的用户步骤 |

### 完成标准
- [ ] `01_USER_JOURNEY.md` 满足 MVS 要求
- [ ] `/doc-design-validation` 结果为 PASS
- [ ] Foundation Gate 检查通过
- [ ] PM / Architect 审批完成

### 负责角色
PM / Product + Architect

---

## Phase 1: Kickoff（功能启动）

### 环节目标
为新功能模块建立上下文，明确边界、目标、约束。

### 标准文档

| 文档 | 用途 | 模板/参考 | 状态 |
|------|------|----------|------|
| `{feature}/10_CONTEXT.md` | 功能背景、边界、用户故事 | `10_CONTEXT_TEMPLATE.md` | ✅ 有模板 |
| `{feature}/10_CONTEXT_CHANGELOG.md` | 变更记录 | `CHANGELOG_TEMPLATE.md` | ✅ 有模板 |

### 环节工具

| 类型 | 名称 | 用途 | 状态 |
|------|------|------|------|
| Slash Command | `/new-feature <name>` | 创建功能模块目录和初始文档 | ✅ 已实现 |
| Skill | `context_writer` | 根据需求描述生成 10_CONTEXT.md | ✅ 已实现 |

### 完成标准
- [ ] `{feature}/` 目录已创建
- [ ] `10_CONTEXT.md` 已填写完整
- [ ] 功能边界已明确，无歧义

### 负责角色
Architect / PM

---

## Phase 2: Spec（规格定义）

### 环节目标
将功能需求转化为可执行的规格说明（UI 流程或 API 规范）。

### 标准文档

| 文档 | 用途 | 模板/参考 | 状态 | 适用场景 |
|------|------|----------|------|----------|
| `{feature}/21_UI_FLOW_SPEC.md` | UI 流程、交互规则、边界条件 | `21_UI_FLOW_SPEC_TEMPLATE.md` | ✅ 有模板 | has_ui=true |
| `{feature}/20_API_SPEC.md` | API 端点、请求响应、错误码 | `20_API_SPEC_TEMPLATE.md` | ✅ 有模板 | has_ui=false |
| `{feature}/11_SPEC_CHANGELOG.md` | 变更记录 | `CHANGELOG_TEMPLATE.md` | ✅ 有模板 | - |

### 环节工具

| 类型 | 名称 | 用途 | 状态 |
|------|------|------|------|
| Subagent | `spec_writer` | 根据 CONTEXT 生成 SPEC 文档 | ✅ 已实现 |
| Skill | `spec_validator` | 检查 SPEC 完整性和一致性 | ✅ 已实现 |

### 完成标准
- [ ] SPEC 文档已生成
- [ ] 所有页面/API 已列出
- [ ] 交互规则/错误处理已定义
- [ ] 已通过人工评审

### 负责角色
AI Product Engineer

---

## Phase 3: Demo（原型验证）

### 环节目标
生成可运行的 UI 原型 + Mock API，验证设计可行性。

> **注意**：此阶段仅当 `ui.demo_policy.required_before_implementation = true` 时启用

### 标准文档/产物

| 产物 | 位置 | 模板/参考 | 状态 |
|------|------|----------|------|
| UI Demo | `playgrounds/{feature}/Demo.vue` | 工具自动生成 | 📝 代码产物 |
| Mock API | `playgrounds/{feature}/mock/api.js` | 工具自动生成 | 📝 代码产物 |
| Demo 评审记录 | `{feature}/30_DEMO_REVIEW.md` | `30_DEMO_REVIEW_TEMPLATE.md` | ✅ 有模板 |

### 环节工具

| 类型 | 名称 | 用途 | 状态 |
|------|------|------|------|
| Skill | `ui_demo` | 根据 SPEC + UI System 生成 Demo | ✅ 已实现 |
| Skill | `mock_api_generator` | 根据 SPEC 生成 Mock API | ✅ 已实现 |
| Slash Command | `/gen-demo <feature>` | 一键生成 Demo + Mock API | ✅ 已实现 |

### 完成标准
- [ ] Demo.vue 可正常运行
- [ ] Mock API 覆盖所有预期接口
- [ ] Demo 已通过人工评审
- [ ] 评审意见已记录

### 负责角色
AI Product Engineer

---

## Phase 4: Design（详细设计）

### 环节目标
基于 SPEC 和 Demo 反馈，完成技术设计，确定 API 契约和数据模型。

### 标准文档

| 文档 | 用途 | 模板/参考 | 状态 |
|------|------|----------|------|
| `{feature}/40_DESIGN_FINAL.md` | 技术架构、API 契约、数据模型 | `40_DESIGN_TEMPLATE.md` | ✅ 有模板 |
| `{feature}/40_DESIGN_CHANGELOG.md` | 变更记录 | `CHANGELOG_TEMPLATE.md` | ✅ 有模板 |

### 环节工具

| 类型 | 名称 | 用途 | 状态 |
|------|------|------|------|
| Skill | `design_from_demo` | 从 Demo Mock API 反推正式 API 契约 | ✅ 已实现 |
| Skill | `schema_generator` | 根据 DESIGN 生成数据库 Schema | ✅ 已实现 |

### 完成标准
- [ ] API 契约已确定（路径、参数、响应）
- [ ] 数据模型已定义
- [ ] 与 Demo Mock API 一致性已验证
- [ ] 已通过架构评审

### 负责角色
Architect

---

## Phase 5: Code（开发实现）

### 环节目标
按照 DESIGN 和 DEV_PLAN 进行开发，持续追踪进度。

### 标准文档

| 文档 | 用途 | 模板/参考 | 状态 |
|------|------|----------|------|
| `{feature}/50_DEV_PLAN.md` | 任务拆解、验证方式、依赖关系 | `50_DEV_PLAN_TEMPLATE.md` | ✅ 有模板 |
| `{feature}/90_PROGRESS_LOG.yaml` | 执行进度、断点信息 | `90_PROGRESS_LOG_TEMPLATE.yaml` | ✅ 有模板 |
| `{feature}/91_DAILY_SUMMARY/{date}.md` | 每日总结 | `91_DAILY_SUMMARY_TEMPLATE.md` | ✅ 有模板 |

### 环节工具

| 类型 | 名称 | 用途 | 状态 |
|------|------|------|------|
| Slash Command | `/check-progress <feature>` | 查看当前进度状态 | ✅ 已实现 |
| Slash Command | `/iresume <feature>` | 断点恢复，读取 checkpoint 继续 | ✅ 已实现 |
| Slash Command | `/daily-summary` | 从 PROGRESS_LOG 生成今日总结 | ✅ 已实现 |
| Skill | `review_alignment` | 检查代码与 DESIGN 一致性 | ✅ 已实现 |
| Skill | `progress_updater` | 自动更新 PROGRESS_LOG | ✅ 已实现 |
| Subagent | `progress_tracker` | 解析 PROGRESS_LOG 生成 DAILY_SUMMARY | ✅ 已实现 |

### 完成标准
- [ ] 所有 DEV_PLAN 任务完成
- [ ] PROGRESS_LOG 状态为 done
- [ ] 代码已提交并通过 CI

### 负责角色
Developer / Claude Code

---

## Phase 6: Test（测试验证）

### 环节目标
根据 SPEC 编写测试计划，执行测试，生成报告。

### 标准文档

| 文档 | 用途 | 模板/参考 | 状态 |
|------|------|----------|------|
| `{feature}/60_TEST_PLAN.md` | 测试用例、预期结果、工具 | `60_TEST_PLAN_TEMPLATE.md` | ✅ 有模板 |
| `{feature}/61_TEST_REPORT.md` | 测试执行结果、Bug 列表 | `61_TEST_REPORT_TEMPLATE.md` | ✅ 有模板 |

### 环节工具

| 类型 | 名称 | 用途 | 状态 |
|------|------|------|------|
| Subagent | `test_plan_writer` | 根据 SPEC 生成测试计划 | ✅ 已实现 |
| Skill | `test_runner` | 执行测试计划（Chrome MCP / API 测试） | ✅ 已实现 |
| Skill | `test_report_generator` | 汇总测试结果生成报告 | ✅ 已实现 |
| Slash Command | `/run-tests <feature>` | 执行测试并生成报告 | ✅ 已实现 |

### 完成标准
- [ ] 测试计划覆盖所有关键路径
- [ ] 所有测试用例执行完毕
- [ ] 测试报告已生成
- [ ] 无 P0/P1 级 Bug

### 负责角色
QA / Claude Code

---

## Phase 7: Deploy（发布上线）

### 环节目标
汇总所有变更，生成发布说明，完成上线。

### 标准文档

| 文档 | 用途 | 模板/参考 | 状态 |
|------|------|----------|------|
| `{feature}/70_RELEASE_NOTE.md` | 版本、特性、修复、已知问题 | `70_RELEASE_NOTE_TEMPLATE.md` | ✅ 有模板 |

### 环节工具

| 类型 | 名称 | 用途 | 状态 |
|------|------|------|------|
| Subagent | `release_summarizer` | 汇总 PROGRESS_LOG + TEST_REPORT 生成 RELEASE_NOTE | ✅ 已实现 |
| Slash Command | `/release <feature> <version>` | 生成 RELEASE_NOTE 并打 tag | ✅ 已实现 |

### 完成标准
- [ ] RELEASE_NOTE 已生成
- [ ] 所有文档已更新到最终状态
- [ ] 代码已合并到主分支
- [ ] 已部署到生产环境

### 负责角色
PM

---

## 跨阶段工具

以下工具不属于特定阶段，在整个工作流中通用：

| 类型 | 名称 | 用途 | 触发场景 | 状态 |
|------|------|------|----------|------|
| Slash Command | `/compact-recovery` | 上下文压缩后恢复 | 模型提示 compact | ✅ 已实现 |
| Skill | `doc_generator` | 根据模板生成任意标准文档 | 任意阶段 | ✅ 已实现 |
| Skill | `changelog_updater` | 更新文档的 CHANGELOG | 文档变更时 | ✅ 已实现 |

---

## 工具实现优先级

### P0 - 必须先实现（影响基本流程）

| 工具 | 类型 | 阶段 | 说明 |
|------|------|------|------|
| `/new-feature` | Slash Command | Phase 1 | 新功能的入口 |
| `/iresume` | Slash Command | Phase 5 | 断点恢复，解决 compact 问题 |
| `/daily-summary` | Slash Command | Phase 5 | 每日必用 |
| `progress_updater` | Skill | Phase 5 | 进度追踪核心 |

### P1 - 高优先级（提升效率）

| 工具 | 类型 | 阶段 | 说明 |
|------|------|------|------|
| `spec_writer` | Subagent | Phase 2 | 减少手工编写 SPEC |
| `ui_demo` | Skill | Phase 3 | 快速生成 Demo |
| `/check-progress` | Slash Command | Phase 5 | 随时查看状态 |
| `progress_tracker` | Subagent | Phase 5 | 自动生成 DAILY_SUMMARY |

### P2 - 标准优先级（完善体验）

| 工具 | 类型 | 阶段 | 说明 |
|------|------|------|------|
| `/gen-demo` | Slash Command | Phase 3 | 一键生成 Demo |
| `test_runner` | Skill | Phase 6 | 自动化测试 |
| `release_summarizer` | Subagent | Phase 7 | 自动生成 RELEASE_NOTE |

### P3 - 低优先级（锦上添花）

| 工具 | 类型 | 阶段 | 说明 |
|------|------|------|------|
| `/init-project` | Slash Command | Phase 0 | 新项目初始化 |
| `schema_generator` | Skill | Phase 4 | 自动生成 DB Schema |

---

## 工具汇总表

### Slash Commands (11 个)

| 命令 | 阶段 | 用途 | 优先级 |
|------|------|------|--------|
| `/init-project` | Phase 0 | 初始化 _foundation 目录 | P3 |
| `/doc-design-validation` | Phase 0.5 | 执行设计验证 PASS/FAIL（v1.4 新增） | P0 |
| `/check-foundation-gate` | Phase 0.5 | 检查 Foundation Gate 状态（v1.4 新增） | P0 |
| `/plan-features` | Phase 0.5 | 生成功能开发清单（v1.4 新增） | P1 |
| `/new-feature <name>` | Phase 1 | 创建功能模块 | P0 |
| `/gen-demo <feature>` | Phase 3 | 生成 Demo + Mock API | P2 |
| `/check-progress <feature>` | Phase 5 | 查看进度状态 | P1 |
| `/iresume <feature>` | Phase 5 | 断点恢复 | P0 |
| `/daily-summary` | Phase 5 | 生成今日总结 | P0 |
| `/run-tests <feature>` | Phase 6 | 执行测试 | P2 |
| `/release <feature> <version>` | Phase 7 | 生成 RELEASE_NOTE | P2 |

### Skills (10 个)

| Skill | 阶段 | 用途 | 优先级 |
|-------|------|------|--------|
| `system_scaffolder` | Phase 0 | 生成目录结构 | P3 |
| `context_writer` | Phase 1 | 生成 CONTEXT 文档 | P2 |
| `spec_validator` | Phase 2 | 检查 SPEC 完整性 | P2 |
| `ui_demo` | Phase 3 | 生成 UI Demo | P1 |
| `mock_api_generator` | Phase 3 | 生成 Mock API | P1 |
| `design_from_demo` | Phase 4 | 从 Demo 反推 API 契约 | P2 |
| `schema_generator` | Phase 4 | 生成 DB Schema | P3 |
| `review_alignment` | Phase 5 | 检查代码与设计一致性 | P1 |
| `progress_updater` | Phase 5 | 更新 PROGRESS_LOG | P0 |
| `test_runner` | Phase 6 | 执行测试 | P2 |
| `test_report_generator` | Phase 6 | 生成测试报告 | P2 |
| `doc_generator` | 跨阶段 | 根据模板生成文档 | P1 |
| `changelog_updater` | 跨阶段 | 更新 CHANGELOG | P2 |

### Subagents (4 个)

| Subagent | 阶段 | 用途 | 优先级 |
|----------|------|------|--------|
| `spec_writer` | Phase 2 | 生成 SPEC 文档 | P1 |
| `progress_tracker` | Phase 5 | 生成 DAILY_SUMMARY | P1 |
| `test_plan_writer` | Phase 6 | 生成测试计划 | P2 |
| `release_summarizer` | Phase 7 | 生成 RELEASE_NOTE | P2 |

---

## 附录 A：阶段与文档/工具速查表

```
Phase 0: Foundation
├── 文档: 01_USER_JOURNEY ✅, 00_PROJECT_CONTEXT ✅, 01_PROJECT_PROFILE ✅, 02_API_CONVENTIONS 📄, 03_DB_CONVENTIONS 📄, _ui_system/* 📄
└── 工具: /init-project, system_scaffolder

Phase 0.5: Foundation Gate (v1.4 新增)
├── 文档: 01_USER_JOURNEY ✅, 00_FOUNDATION_GATE ✅, DESIGN_VALIDATION_RESULT 📝
└── 工具: /doc-design-validation, /check-foundation-gate, /plan-features

Phase 1: Kickoff
├── 文档: 10_CONTEXT ✅, 10_CONTEXT_CHANGELOG ✅
└── 工具: /new-feature, context_writer

Phase 2: Spec
├── 文档: 21_UI_FLOW_SPEC ✅ 或 20_API_SPEC ✅, 11_SPEC_CHANGELOG ✅
└── 工具: spec_writer (subagent), spec_validator

Phase 3: Demo
├── 产物: playgrounds/{feature}/Demo.vue 📝, mock/api.js 📝, 30_DEMO_REVIEW ✅
└── 工具: /gen-demo, ui_demo, mock_api_generator

Phase 4: Design
├── 文档: 40_DESIGN_FINAL ✅, 40_DESIGN_CHANGELOG ✅
└── 工具: design_from_demo, schema_generator

Phase 5: Code
├── 文档: 50_DEV_PLAN ✅, 90_PROGRESS_LOG ✅, 91_DAILY_SUMMARY/* ✅
└── 工具: /check-progress, /iresume, /daily-summary, review_alignment, progress_updater, progress_tracker (subagent)

Phase 6: Test
├── 文档: 60_TEST_PLAN ✅, 61_TEST_REPORT ✅
└── 工具: /run-tests, test_plan_writer (subagent), test_runner, test_report_generator

Phase 7: Deploy
├── 文档: 70_RELEASE_NOTE ✅
└── 工具: /release, release_summarizer (subagent)

跨阶段
└── 工具: /compact-recovery, doc_generator, changelog_updater

图例: ✅ 有模板 | 📄 有示例 | 📝 代码产物
```

---

## 附录 B：模板文件清单

所有模板位于 `CC_COLLABORATION/03_templates/` 目录：

```
03_templates/
├── _common/                              # 通用模板
│   ├── 01_PROJECT_PROFILE_TEMPLATE.yaml
│   ├── 90_PROGRESS_LOG_TEMPLATE.yaml
│   └── 91_DAILY_SUMMARY_TEMPLATE.md
├── _foundation/                          # Foundation 级模板
│   ├── 00_FOUNDATION_GATE.md             # Gate 规则（v1.4 新增）
│   ├── 01_USER_JOURNEY_TEMPLATE.md       # 需求起源层（v1.4 新增）
│   ├── 03_DB_CONVENTIONS_TEMPLATE.md
│   ├── _api_system_template/
│   │   ├── 00_REST_CONVENTIONS_TEMPLATE.md
│   │   ├── 01_COMMAND_CONVENTIONS_TEMPLATE.md
│   │   ├── 02_YAML_SCHEMA_CONVENTIONS_TEMPLATE.md
│   │   └── 03_EXTERNAL_API_CONVENTIONS_TEMPLATE.md
│   └── _ui_system_template/
├── 01_kickoff/
│   └── 10_CONTEXT_TEMPLATE.md
├── 02_spec/
│   ├── 20_API_SPEC_TEMPLATE.md
│   └── 21_UI_FLOW_SPEC_TEMPLATE.md
├── 03_demo/
│   └── 30_DEMO_REVIEW_TEMPLATE.md
├── 04_design/
│   └── 40_DESIGN_TEMPLATE.md
├── 05_code/
│   └── 50_DEV_PLAN_TEMPLATE.md
├── 06_test/
│   ├── 60_TEST_PLAN_TEMPLATE.md
│   └── 61_TEST_REPORT_TEMPLATE.md
└── 07_deploy/
    ├── 70_RELEASE_NOTE_TEMPLATE.md
    └── 71_CHANGELOG_TEMPLATE.md
```

| 模板文件 | 对应文档 | 阶段 |
|---------|---------|------|
| `01_kickoff/10_CONTEXT_TEMPLATE.md` | `10_CONTEXT.md` | Phase 1 |
| `_common/01_PROJECT_PROFILE_TEMPLATE.yaml` | `01_PROJECT_PROFILE.yaml` | Phase 0 |
| `02_spec/21_UI_FLOW_SPEC_TEMPLATE.md` | `21_UI_FLOW_SPEC.md` | Phase 2 |
| `02_spec/20_API_SPEC_TEMPLATE.md` | `20_API_SPEC.md` | Phase 2 |
| `03_demo/30_DEMO_REVIEW_TEMPLATE.md` | `30_DEMO_REVIEW.md` | Phase 3 |
| `04_design/40_DESIGN_TEMPLATE.md` | `40_DESIGN_FINAL.md` | Phase 4 |
| `05_code/50_DEV_PLAN_TEMPLATE.md` | `50_DEV_PLAN.md` | Phase 5 |
| `_common/90_PROGRESS_LOG_TEMPLATE.yaml` | `90_PROGRESS_LOG.yaml` | Phase 5 |
| `_common/91_DAILY_SUMMARY_TEMPLATE.md` | `91_DAILY_SUMMARY/{date}.md` | Phase 5 |
| `06_test/60_TEST_PLAN_TEMPLATE.md` | `60_TEST_PLAN.md` | Phase 6 |
| `06_test/61_TEST_REPORT_TEMPLATE.md` | `61_TEST_REPORT.md` | Phase 6 |
| `07_deploy/70_RELEASE_NOTE_TEMPLATE.md` | `70_RELEASE_NOTE.md` | Phase 7 |
| `07_deploy/71_CHANGELOG_TEMPLATE.md` | `*_CHANGELOG.md` | 通用 |

### Foundation 模板

Foundation 级别的规范模板位于 `03_templates/_foundation/`：

| 模板目录/文件 | 说明 |
|--------------|------|
| `01_USER_JOURNEY_TEMPLATE.md` | **需求起源层** - 用户流程、系统责任、模块映射（v1.4 新增） |
| `00_FOUNDATION_GATE.md` | Foundation Gate 规则、MVS 标准（v1.4 新增） |
| `_api_system_template/` | API 规则体系（REST、Command、YAML、External API） |
| `_ui_system_template/` | UI 设计系统（6 层） |
| `03_DB_CONVENTIONS_TEMPLATE.md` | 数据库设计规范 |

---

## 附录 C：阶段裁剪指南

### 概述

8 阶段工作流是完整框架，但并非所有功能都需要经过全部阶段。根据功能的规模和类型，可以灵活裁剪。

### 裁剪原则

1. **保留核心阶段**：Phase 1 (Kickoff) 和 Phase 7 (Deploy) 始终保留
2. **按需跳过**：根据功能特点跳过不适用的阶段
3. **文档记录**：在 `10_CONTEXT.md` 中记录裁剪决策和原因

### 预设裁剪模式

#### 1. 完整模式（Full）- 默认

适用于：大型功能、新模块、涉及 UI + API + DB 的完整功能

```
Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7
Foundation → Kickoff → Spec → Demo → Design → Code → Test → Deploy
```

#### 2. 标准模式（Standard）

适用于：中型功能、已有架构基础、标准 CRUD 功能

跳过：Phase 0 (Foundation) - 复用现有基础设施

```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7
Kickoff → Spec → Demo → Design → Code → Test → Deploy
```

#### 3. 精简模式（Lean）

适用于：小型功能、UI 改动、简单的 bug 修复

跳过：Phase 0, Phase 3 (Demo), Phase 4 (Design)

```
Phase 1 → Phase 2 → Phase 5 → Phase 6 → Phase 7
Kickoff → Spec → Code → Test → Deploy
```

#### 4. API-Only 模式

适用于：纯后端功能、API 开发、无 UI 的服务

跳过：Phase 0, Phase 3 (Demo)

```
Phase 1 → Phase 2 (API Spec) → Phase 4 → Phase 5 → Phase 6 → Phase 7
Kickoff → API Spec → Design → Code → Test → Deploy
```

#### 5. 热修复模式（Hotfix）

适用于：紧急 bug 修复、生产问题

跳过：Phase 0, Phase 2, Phase 3, Phase 4

```
Phase 1 → Phase 5 → Phase 6 → Phase 7
Kickoff → Code → Test → Deploy
```

### `/new-feature` 命令裁剪参数

创建新功能时，可通过参数指定裁剪模式：

```bash
# 完整模式（默认）
/new-feature my-feature

# 标准模式
/new-feature my-feature --mode=standard

# 精简模式
/new-feature my-feature --mode=lean

# API-Only 模式
/new-feature my-feature --mode=api-only

# 热修复模式
/new-feature my-feature --mode=hotfix

# 自定义跳过阶段
/new-feature my-feature --skip=demo,design

# 无 UI 功能
/new-feature my-feature --no-ui
```

### 裁剪决策矩阵

| 功能特征 | 推荐模式 | 跳过阶段 |
|---------|---------|---------|
| 新项目/新模块 | Full | 无 |
| 已有项目的新功能 | Standard | Phase 0 |
| 小型 UI 改动 | Lean | Phase 0, 3, 4 |
| 纯 API 开发 | API-Only | Phase 0, 3 |
| 紧急修复 | Hotfix | Phase 0, 2, 3, 4 |
| 配置变更 | Hotfix | Phase 0, 2, 3, 4 |
| 文档更新 | Hotfix | Phase 0, 2, 3, 4, 6 |

### 裁剪后的文档要求

即使跳过某些阶段，仍需保留必要文档：

| 模式 | 必需文档 |
|------|---------|
| Full | 所有文档 |
| Standard | 10_CONTEXT, 11_SPEC, 30_DEMO_REVIEW, 40_DESIGN, 50_DEV_PLAN, 40_TEST, 70_RELEASE |
| Lean | 10_CONTEXT, 11_SPEC, 50_DEV_PLAN, 40_TEST, 70_RELEASE |
| API-Only | 10_CONTEXT, 20_API_SPEC, 40_DESIGN, 50_DEV_PLAN, 40_TEST, 70_RELEASE |
| Hotfix | 10_CONTEXT (简化), 70_RELEASE |

### 最佳实践

1. **宁多勿少**：不确定时选择更完整的模式
2. **记录决策**：在 CONTEXT 中说明为什么选择该模式
3. **灵活调整**：开发过程中可以补充之前跳过的阶段
4. **团队共识**：裁剪决策需要团队确认
