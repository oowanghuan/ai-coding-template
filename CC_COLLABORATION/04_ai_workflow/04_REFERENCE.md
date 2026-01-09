# AI 协作开发框架 - 完整参考手册

> 适用于：按需查阅详细规范

---

## 一、全部 24 个 Slash Commands

### 1.1 按类别分类

```
项目初始化（5 个）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
/init-project                     创建 Foundation 目录结构
/doc-design-validation            执行设计验证
/check-foundation-gate            检查 Foundation Gate
/approve-foundation --role=XX     审批 Foundation
/plan-features                    生成功能开发清单

功能开发（4 个）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
/new-feature {name}               创建新功能模块 (Phase 1)
/gen-demo {feature}               生成 Demo (Phase 3)
/run-tests {feature}              执行测试 (Phase 6)
/release {feature} {version}      发布上线 (Phase 7)

每日工作（5 个）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
/start-day                        每日开始（同步代码、恢复上下文）
/iresume {feature}                断点恢复（最重要！）
/check-progress {feature}         查看进度
/daily-summary                    生成每日总结
/end-day                          每日结束（提交代码）

Phase Gate（3 个）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
/check-gate {feature} --phase=N   检查 Gate 状态
/approve-gate {feature} --phase=N --role=XX  审批通过
/next-phase {feature}             进入下一阶段

老项目整合（4 个）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
/scan-project {path}              扫描项目（技术栈、模块）
/integrate-project {path} --level=N  整合到框架
/reverse-api {path}               逆向生成 API 文档
/reverse-schema {path}            逆向生成数据模型

辅助工具（3 个）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
/expert-review {path}             OpenAI 独立评审
/sync-docs                        检查文档与代码一致性
/gui-connect                      连接 GUI 控制台
```

### 1.2 命令详解

| # | 命令 | 用途 | 阶段 | 示例 |
|---|------|------|------|------|
| 1 | `/init-project` | 初始化项目 Foundation 目录 | Phase 0 | `/init-project` |
| 2 | `/doc-design-validation` | 执行设计验证 | Phase 0.5 | `/doc-design-validation --verbose` |
| 3 | `/check-foundation-gate` | 检查 Foundation Gate | Phase 0.5 | `/check-foundation-gate` |
| 4 | `/approve-foundation` | 审批 Foundation | Phase 0.5 | `/approve-foundation --role=PM` |
| 5 | `/plan-features` | 生成功能开发清单 | Phase 0.5 | `/plan-features` |
| 6 | `/new-feature` | 创建新功能模块 | Phase 1 | `/new-feature user-auth` |
| 7 | `/gen-demo` | 生成 Demo | Phase 3 | `/gen-demo user-auth` |
| 8 | `/run-tests` | 执行测试 | Phase 6 | `/run-tests user-auth` |
| 9 | `/release` | 发布上线 | Phase 7 | `/release user-auth v1.0.0` |
| 10 | `/start-day` | 每日开始 | 每日 | `/start-day` |
| 11 | `/iresume` | 断点恢复 | 每日 | `/iresume user-auth` |
| 12 | `/check-progress` | 查看进度 | 每日 | `/check-progress user-auth` |
| 13 | `/daily-summary` | 生成每日总结 | 每日 | `/daily-summary` |
| 14 | `/end-day` | 每日结束 | 每日 | `/end-day` |
| 15 | `/check-gate` | 检查 Gate 状态 | 任意 | `/check-gate user-auth --phase=2` |
| 16 | `/approve-gate` | 审批 Gate | 任意 | `/approve-gate user-auth --phase=2 --role=PM` |
| 17 | `/next-phase` | 进入下一阶段 | 任意 | `/next-phase user-auth` |
| 18 | `/scan-project` | 扫描项目 | 整合 | `/scan-project ./my-project` |
| 19 | `/integrate-project` | 整合现有项目 | 整合 | `/integrate-project ./my-project --level=1` |
| 20 | `/reverse-api` | 逆向生成 API 文档 | 整合 | `/reverse-api ./my-project` |
| 21 | `/reverse-schema` | 逆向生成数据模型 | 整合 | `/reverse-schema ./my-project` |
| 22 | `/sync-docs` | 检查文档一致性 | 辅助 | `/sync-docs` |
| 23 | `/expert-review` | OpenAI 独立评审 | 辅助 | `/expert-review docs/user-auth --phase=4` |
| 24 | `/gui-connect` | 连接 GUI 控制台 | GUI | `/gui-connect` |

### 1.3 命令依赖关系

```
/init-project
    │
    ▼
/doc-design-validation ──▶ /check-foundation-gate ──▶ /plan-features
                                                           │
                                                           ▼
                                                    /new-feature
                                                           │
    ┌──────────────────────────────────────────────────────┘
    │
    ▼
/iresume ──▶ [编码] ──▶ /check-gate ──▶ /approve-gate ──▶ /next-phase
    ▲                                                          │
    │                                                          │
    └──────────────────────────────────────────────────────────┘
                          （循环 Phase 1-7）
```

---

## 二、Skills 清单（20 个）

### 2.1 按阶段分类

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

### 2.2 整合相关 Skills

| Skill | 用途 |
|-------|------|
| `project_scanner` | 扫描项目结构和技术栈 |
| `api_reverser` | 从代码逆向生成 API 文档 |
| `schema_reverser` | 从 ORM 逆向生成数据模型 |
| `doc_sync_checker` | 检查文档与代码一致性 |
| `contract_resolver` | 接口契约解析 |

---

## 三、Subagents 清单（5 个）

| Subagent | 阶段 | 用途 | 位置 |
|----------|------|------|------|
| `spec_writer` | Phase 2 | 生成 SPEC 文档 | `.claude/subagents/spec_writer.md` |
| `progress_tracker` | Phase 5 | 生成 DAILY_SUMMARY | `.claude/subagents/progress_tracker.md` |
| `test_plan_writer` | Phase 6 | 生成测试计划 | `.claude/subagents/test_plan_writer.md` |
| `release_summarizer` | Phase 7 | 生成 RELEASE_NOTE | `.claude/subagents/release_summarizer.md` |
| `expert_reviewer` | 评审 | 独立技术评审 | `.claude/subagents/expert_reviewer.md` |

---

## 四、阶段裁剪指南

### 4.1 预设裁剪模式

| 模式 | 适用场景 | 阶段流程 |
|------|---------|---------|
| **Full** | 大型功能、新模块 | 0 → 0.5 → 1 → 2 → 3 → 4 → 5 → 6 → 7 |
| **Standard** | 中型功能 | 1 → 2 → 3 → 4 → 5 → 6 → 7 |
| **Lean** | 小型功能、UI 改动 | 1 → 2 → 5 → 6 → 7 |
| **API-Only** | 纯后端、无 UI | 1 → 2(API) → 4 → 5 → 6 → 7 |
| **Hotfix** | 紧急修复 | 1 → 5 → 6 → 7 |

### 4.2 使用方法

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

### 4.3 裁剪决策矩阵

| 功能特征 | 推荐模式 | 跳过阶段 |
|---------|---------|---------|
| 新项目/新模块 | Full | 无 |
| 已有项目的新功能 | Standard | Phase 0 |
| 小型 UI 改动 | Lean | Phase 0, 3, 4 |
| 纯 API 开发 | API-Only | Phase 0, 3 |
| 紧急修复 | Hotfix | Phase 0, 2, 3, 4 |

---

## 五、老项目整合

### 5.1 整合级别

| 级别 | 名称 | 产出物 | 耗时 | 适用场景 |
|------|------|--------|------|----------|
| **Level 0** | 最小登记 | 10_CONTEXT.md（极简） | 5-10分钟 | 很少改动 |
| **Level 1** | AI可协作 | +技术栈+模块划分 | 30分钟-1小时 | 日常维护 |
| **Level 2** | 深度协作 | +API文档+数据模型 | 1-3天 | 核心项目 |
| **Level 3** | 完全规范 | 全套Foundation | 按需 | 对标新项目 |

### 5.2 整合命令流程

```bash
# Step 1: 扫描项目
/scan-project ./my-project
# → 输出：技术栈、模块数、推荐级别

# Step 2: 执行整合
/integrate-project ./my-project --level=1 --name=legacy-dashboard
# → 生成：docs/legacy-dashboard/ 目录和基础文档

# Step 3: 逆向生成文档（可选）
/reverse-api ./my-project      # 生成 API 文档
/reverse-schema ./my-project   # 生成数据模型文档
```

### 5.3 标记系统

| 标记 | 含义 | 示例 |
|------|------|------|
| `[legacy]` | 历史功能 | `## 用户管理 [legacy]` |
| `[逆向]` | 从代码生成 | `### GET /api/users [逆向]` |
| `[推断]` | AI 推断 | `page: number [推断]` |
| `[已验证]` | 人工确认 | `### 数据模型 [已验证]` |

---

## 六、文件结构参考

### 6.1 项目级文档（Foundation）

```
docs/_foundation/
├── 00_PROJECT_CONTEXT.md       # 项目背景
├── 01_USER_JOURNEY.md          # 需求起源（Phase 0.5 核心）
├── 01_PROJECT_PROFILE.yaml     # 技术栈配置
├── 02_ARCHITECTURE.md          # 架构设计
├── 03_MODULE_DECOMPOSITION.md  # 模块划分
├── 04_ROADMAP.md               # 里程碑规划
├── FEATURE_CHECKLIST.md        # 功能开发清单（自动生成）
├── FOUNDATION_GATE_STATUS.yaml # Gate 状态（自动生成）
├── _api_system/                # API 规则体系
│   ├── 00_REST_CONVENTIONS.md
│   ├── 01_COMMAND_CONVENTIONS.md
│   ├── 02_YAML_SCHEMA_CONVENTIONS.md
│   └── 03_EXTERNAL_API_CONVENTIONS.md
├── _ui_system/                 # UI 规则体系
└── 03_DB_CONVENTIONS.md        # 数据库规范
```

### 6.2 功能级文档（每个 Feature）

```
docs/{feature-name}/
├── 10_CONTEXT.md              # Phase 1: 功能上下文
├── 20_API_SPEC.md             # Phase 2: API 规格（无 UI 时）
├── 21_UI_FLOW_SPEC.md         # Phase 2: UI 流程规格（有 UI 时）
├── 30_DEMO_REVIEW.md          # Phase 3: Demo 评审记录
├── 40_DESIGN_FINAL.md         # Phase 4: 详细设计
├── 50_DEV_PLAN.md             # Phase 5: 开发计划（可选）
├── 60_TEST_PLAN.md            # Phase 6: 测试计划
├── 61_TEST_REPORT.md          # Phase 6: 测试报告
├── 70_RELEASE_NOTE.md         # Phase 7: 发布说明
├── 90_PROGRESS_LOG.yaml       # 进度日志（含 cc_checkpoint）
├── 91_DAILY_SUMMARY/          # 每日总结目录
├── PHASE_GATE.yaml            # Gate 规则配置
├── PHASE_GATE_STATUS.yaml     # Gate 运行状态
├── REVIEW_ACTIONS.yaml        # 专家评审结果
├── REVIEW_REPORT.md           # 专家评审报告
└── _demos/                    # Demo 文件目录
```

---

## 七、模板文件清单

所有模板位于 `CC_COLLABORATION/03_templates/` 目录：

```
03_templates/
├── _common/                              # 通用模板
│   ├── 01_PROJECT_PROFILE_TEMPLATE.yaml
│   ├── 90_PROGRESS_LOG_TEMPLATE.yaml
│   └── 91_DAILY_SUMMARY_TEMPLATE.md
├── _foundation/                          # Foundation 级模板
│   ├── 00_FOUNDATION_GATE.md
│   ├── 01_USER_JOURNEY_TEMPLATE.md
│   ├── 03_DB_CONVENTIONS_TEMPLATE.md
│   ├── _api_system_template/
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

### 模板对应关系

| 模板文件 | 对应产出 | 阶段 |
|---------|---------|------|
| `01_kickoff/10_CONTEXT_TEMPLATE.md` | `10_CONTEXT.md` | Phase 1 |
| `02_spec/21_UI_FLOW_SPEC_TEMPLATE.md` | `21_UI_FLOW_SPEC.md` | Phase 2 |
| `02_spec/20_API_SPEC_TEMPLATE.md` | `20_API_SPEC.md` | Phase 2 |
| `03_demo/30_DEMO_REVIEW_TEMPLATE.md` | `30_DEMO_REVIEW.md` | Phase 3 |
| `04_design/40_DESIGN_TEMPLATE.md` | `40_DESIGN_FINAL.md` | Phase 4 |
| `05_code/50_DEV_PLAN_TEMPLATE.md` | `50_DEV_PLAN.md` | Phase 5 |
| `_common/90_PROGRESS_LOG_TEMPLATE.yaml` | `90_PROGRESS_LOG.yaml` | Phase 5 |
| `06_test/60_TEST_PLAN_TEMPLATE.md` | `60_TEST_PLAN.md` | Phase 6 |
| `06_test/61_TEST_REPORT_TEMPLATE.md` | `61_TEST_REPORT.md` | Phase 6 |
| `07_deploy/70_RELEASE_NOTE_TEMPLATE.md` | `70_RELEASE_NOTE.md` | Phase 7 |

---

## 八、阶段与工具速查表

```
Phase 0: Foundation
├── 文档: 01_USER_JOURNEY ✅, 00_PROJECT_CONTEXT ✅, 01_PROJECT_PROFILE ✅
├── 工具: /init-project, system_scaffolder
└── Gate: PM + Architect 审批

Phase 0.5: Foundation Gate
├── 文档: 01_USER_JOURNEY ✅, 00_FOUNDATION_GATE ✅
├── 工具: /doc-design-validation, /check-foundation-gate, /plan-features
└── Gate: 设计验证 PASS + 审批

Phase 1: Kickoff
├── 文档: 10_CONTEXT ✅
├── 工具: /new-feature, context_writer
└── Gate: PM 审批

Phase 2: Spec
├── 文档: 21_UI_FLOW_SPEC ✅ 或 20_API_SPEC ✅
├── 工具: spec_writer (subagent), spec_validator
└── Gate: Architect 审批

Phase 3: Demo
├── 产物: Demo.vue, mock/api.js, 30_DEMO_REVIEW ✅
├── 工具: /gen-demo, ui_demo, mock_api_generator
└── Gate: PM 审批

Phase 4: Design
├── 文档: 40_DESIGN_FINAL ✅
├── 工具: design_from_demo, schema_generator
└── Gate: Architect 审批

Phase 5: Code
├── 文档: 50_DEV_PLAN ✅, 90_PROGRESS_LOG ✅
├── 工具: /start-day, /iresume, /end-day, progress_updater
└── Gate: Developer 审批

Phase 6: Test
├── 文档: 60_TEST_PLAN ✅, 61_TEST_REPORT ✅
├── 工具: /run-tests, test_plan_writer (subagent)
└── Gate: QA 审批（无 P0/P1 Bug）

Phase 7: Deploy
├── 文档: 70_RELEASE_NOTE ✅
├── 工具: /release, release_summarizer (subagent)
└── Gate: PM 审批

图例: ✅ 有模板
```

---

## 下一步

- 想快速上手？→ [01_QUICKSTART.md](./01_QUICKSTART.md)
- 想了解框架体系？→ [02_FRAMEWORK_OVERVIEW.md](./02_FRAMEWORK_OVERVIEW.md)
- 想了解每日操作？→ [03_DAILY_OPERATIONS.md](./03_DAILY_OPERATIONS.md)

---

_文档版本：v1.5 | 最后更新：2026-01-09_
