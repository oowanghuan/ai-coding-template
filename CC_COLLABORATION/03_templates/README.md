# 03_templates - 文档模板

本目录包含 8 阶段工作流中各阶段的文档模板。

## 目录结构

```
03_templates/
├── 00_foundation/    # Phase 0: 项目基础设施模板
├── 01_kickoff/       # Phase 1: Kickoff 模板
├── 02_spec/          # Phase 2: Spec 模板
├── 03_demo/          # Phase 3: Demo 模板
├── 04_design/        # Phase 4: Design 模板
├── 05_code/          # Phase 5: Code 模板
├── 06_test/          # Phase 6: Test 模板
├── 07_deploy/        # Phase 7: Deploy 模板
└── _shared/          # 跨阶段共享模板
```

## 各阶段模板

### Phase 0: Foundation（项目基础设施）

| 模板 | 用途 |
|------|------|
| `00_FOUNDATION_GATE.md` | Foundation Gate 说明 |
| `01_USER_JOURNEY_TEMPLATE.md` | 用户旅程模板 |
| `02_ARCHITECTURE_TEMPLATE.md` | 架构模板 |
| `03_MODULE_DECOMPOSITION_TEMPLATE.md` | 模块分解模板 |
| `04_ROADMAP_TEMPLATE.md` | 路线图模板 |
| `05_TECH_DECISIONS_TEMPLATE.md` | 技术决策模板 |

### Phase 1-7: 功能开发阶段

| Phase | 模板 | 用途 |
|-------|------|------|
| 1 Kickoff | `10_CONTEXT_TEMPLATE.md` | 功能上下文 |
| 2 Spec | `20_API_SPEC_TEMPLATE.md` | API 规格 |
| 2 Spec | `21_UI_FLOW_SPEC_TEMPLATE.md` | UI 流程规格 |
| 3 Demo | `30_DEMO_REVIEW_TEMPLATE.md` | Demo 评审记录 |
| 4 Design | `40_DESIGN_TEMPLATE.md` | 技术设计 |
| 5 Code | `50_DEV_PLAN_TEMPLATE.md` | 开发计划 |
| 6 Test | `60_TEST_PLAN_TEMPLATE.md` | 测试计划 |
| 6 Test | `61_TEST_REPORT_TEMPLATE.md` | 测试报告 |
| 7 Deploy | `70_RELEASE_NOTE_TEMPLATE.md` | 发布说明 |
| 7 Deploy | `71_CHANGELOG_TEMPLATE.md` | 变更日志 |

### 跨阶段共享模板 (_shared/)

| 模板 | 用途 |
|------|------|
| `90_PROGRESS_LOG_TEMPLATE.yaml` | 进度日志 |
| `91_DAILY_SUMMARY_TEMPLATE.md` | 每日总结 |
| `PHASE_GATE_TEMPLATE.yaml` | Phase Gate 规则 |
| `PHASE_GATE_STATUS_TEMPLATE.yaml` | Phase Gate 状态 |
| `REVIEW_ACTIONS_TEMPLATE.yaml` | 评审行动项 |
| `REVIEW_REPORT_TEMPLATE.md` | 评审报告 |

## 使用方式

1. **手动使用**：复制模板到 `docs/{feature}/` 目录，修改文件名去掉 `_TEMPLATE` 后缀
2. **命令使用**：通过 `/new-feature` 等命令自动生成

## 相关目录

- `04_ai_workflow/` - 8 阶段工作流说明
- `07_phase_gate/` - Phase Gate 机制定义

---

_CC_COLLABORATION Framework_
