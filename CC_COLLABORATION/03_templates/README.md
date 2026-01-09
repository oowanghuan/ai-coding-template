# 03_templates - 文档模板

本目录包含 8 阶段工作流中各阶段的文档模板。

## 目录结构

```
03_templates/
├── 00_foundation/    # Phase 0: 项目基础设施模板（项目级，只用一次）
├── 01_kickoff/       # Phase 1: Kickoff 模板
├── 02_spec/          # Phase 2: Spec 模板
├── 03_demo/          # Phase 3: Demo 模板
├── 04_design/        # Phase 4: Design 模板
├── 05_code/          # Phase 5: Code 模板
├── 06_test/          # Phase 6: Test 模板
├── 07_deploy/        # Phase 7: Deploy 模板
└── _shared/          # 跨阶段共享模板（每个功能都用）
```

---

## 两类模板的区别

### `00_foundation/` - 项目级模板

**特点**：
- 整个项目只使用**一次**
- 在项目初始化（Phase 0）时创建
- 产出物放在 `docs/_foundation/` 目录

**用途**：定义项目的基础架构、用户旅程、模块划分等全局性文档。

| 模板 | 产出位置 | 用途 |
|------|----------|------|
| `01_USER_JOURNEY_TEMPLATE.md` | `docs/_foundation/01_USER_JOURNEY.md` | 用户旅程与系统责任 |
| `02_ARCHITECTURE_TEMPLATE.md` | `docs/_foundation/02_ARCHITECTURE.md` | 系统架构设计 |
| `03_MODULE_DECOMPOSITION_TEMPLATE.md` | `docs/_foundation/03_MODULE_DECOMPOSITION.md` | 模块分解与依赖 |
| `04_ROADMAP_TEMPLATE.md` | `docs/_foundation/04_ROADMAP.md` | 开发路线图 |
| `05_TECH_DECISIONS_TEMPLATE.md` | `docs/_foundation/05_TECH_DECISIONS.md` | 技术决策记录 |
| `_api_system_template/` | `docs/_foundation/_api_system/` | API 规范体系 |
| `_ui_system_template/` | `docs/_foundation/_ui_system/` | UI 规范体系 |

### `_shared/` - 功能级共享模板

**特点**：
- 每个功能模块**都会使用**
- 在创建新功能（`/new-feature`）时复制
- 产出物放在 `docs/{feature}/` 目录

**用途**：进度跟踪、Phase Gate 管理、评审记录等贯穿整个功能开发周期的文档。

| 模板 | 产出位置 | 用途 |
|------|----------|------|
| `90_PROGRESS_LOG_TEMPLATE.yaml` | `docs/{feature}/90_PROGRESS_LOG.yaml` | 进度日志（CC 断点恢复依赖） |
| `91_DAILY_SUMMARY_TEMPLATE.md` | `docs/{feature}/91_DAILY_SUMMARY/` | 每日总结 |
| `PHASE_GATE_TEMPLATE.yaml` | `docs/{feature}/PHASE_GATE.yaml` | Phase Gate 规则定义 |
| `PHASE_GATE_STATUS_TEMPLATE.yaml` | `docs/{feature}/PHASE_GATE_STATUS.yaml` | Gate 状态追踪 |
| `REVIEW_ACTIONS_TEMPLATE.yaml` | `docs/{feature}/REVIEW_ACTIONS.yaml` | 评审行动项 |
| `REVIEW_REPORT_TEMPLATE.md` | `docs/{feature}/REVIEW_REPORT.md` | 评审报告 |
| `01_PROJECT_PROFILE_TEMPLATE.yaml` | `docs/{feature}/PROJECT_PROFILE.yaml` | 功能配置 |

---

## Phase 1-7: 功能开发阶段模板

每个功能在对应阶段使用的模板：

| Phase | 模板 | 产出位置 | 用途 |
|-------|------|----------|------|
| 1 Kickoff | `10_CONTEXT_TEMPLATE.md` | `docs/{feature}/10_CONTEXT.md` | 功能上下文 |
| 2 Spec | `20_API_SPEC_TEMPLATE.md` | `docs/{feature}/20_API_SPEC.md` | API 规格 |
| 2 Spec | `21_UI_FLOW_SPEC_TEMPLATE.md` | `docs/{feature}/21_UI_FLOW_SPEC.md` | UI 流程规格 |
| 3 Demo | `30_DEMO_REVIEW_TEMPLATE.md` | `docs/{feature}/30_DEMO_REVIEW.md` | Demo 评审记录 |
| 4 Design | `40_DESIGN_TEMPLATE.md` | `docs/{feature}/40_DESIGN_FINAL.md` | 技术设计 |
| 5 Code | `50_DEV_PLAN_TEMPLATE.md` | `docs/{feature}/50_DEV_PLAN.md` | 开发计划 |
| 6 Test | `60_TEST_PLAN_TEMPLATE.md` | `docs/{feature}/60_TEST_PLAN.md` | 测试计划 |
| 6 Test | `61_TEST_REPORT_TEMPLATE.md` | `docs/{feature}/61_TEST_REPORT.md` | 测试报告 |
| 7 Deploy | `70_RELEASE_NOTE_TEMPLATE.md` | `docs/{feature}/70_RELEASE_NOTE.md` | 发布说明 |
| 7 Deploy | `71_CHANGELOG_TEMPLATE.md` | `docs/{feature}/71_CHANGELOG.md` | 变更日志 |

---

## 使用方式

### 自动使用（推荐）

```bash
# 初始化项目 - 自动使用 00_foundation/ 模板
/init-project

# 创建新功能 - 自动使用 _shared/ + 对应 Phase 模板
/new-feature user-auth
```

### 手动使用

1. 复制模板到目标目录
2. 修改文件名，去掉 `_TEMPLATE` 后缀
3. 填写模板内容

---

## 相关目录

- `01_workflow/` - 工作流说明
- `07_phase_gate/` - Phase Gate 机制定义

---

_CC_COLLABORATION Framework v3.1_
