# docs 目录 - 功能文档中心

此目录存放所有功能模块的文档，按照 8 阶段工作流组织。

## 目录结构

```
docs/
├── _foundation/                     # 项目级基础配置
│   ├── _planning/                   # 规划文档
│   │   ├── 01_USER_JOURNEY.md       # 用户旅程
│   │   ├── 02_ARCHITECTURE.md       # 系统架构
│   │   ├── 03_MODULE_DECOMPOSITION.md # 模块分解
│   │   ├── 04_ROADMAP.md            # 路线图
│   │   └── 05_TECH_DECISIONS.md     # 技术决策
│   ├── _api_system/                 # API 规范
│   ├── _db_system/                  # DB 规范
│   ├── _ui_system/                  # UI 设计系统
│   ├── FOUNDATION_GATE_STATUS.yaml  # Foundation Gate 状态
│   └── PROJECT_TRACKER.yaml         # 项目跟踪（可选）
│
├── {feature-name}/                  # 功能模块文档
│   ├── 10_CONTEXT.md                # 功能上下文 (Phase 1)
│   ├── 20_API_SPEC.md               # API 规格 (Phase 2)
│   ├── 21_UI_FLOW_SPEC.md           # UI 流程规格 (Phase 2)
│   ├── 30_DEMO_REVIEW.md            # Demo 评审 (Phase 3)
│   ├── 40_DESIGN_FINAL.md           # 技术设计 (Phase 4)
│   ├── 50_DEV_PLAN.md               # 开发计划 (Phase 5)
│   ├── 60_TEST_PLAN.md              # 测试计划 (Phase 6)
│   ├── 61_TEST_REPORT.md            # 测试报告 (Phase 6)
│   ├── 70_RELEASE_NOTE.md           # 发布说明 (Phase 7)
│   ├── 90_PROGRESS_LOG.yaml         # 进度日志
│   ├── PHASE_GATE.yaml              # Phase Gate 规则
│   ├── PHASE_GATE_STATUS.yaml       # Phase Gate 状态
│   ├── DOC_CHANGELOG.md             # 文档变更日志
│   └── _demos/                      # Demo 文件目录
│
└── README.md                        # 本文件
```

## 文档编号规则

| 前缀 | 阶段 | 文档类型 |
|------|------|----------|
| 10 | Phase 1 Kickoff | 功能上下文 (Context) |
| 20 | Phase 2 Spec | API 规格 (API Spec) |
| 21 | Phase 2 Spec | UI 流程规格 (UI Flow Spec) |
| 30 | Phase 3 Demo | Demo 评审 (Demo Review) |
| 40 | Phase 4 Design | 技术设计 (Design Final) |
| 50 | Phase 5 Code | 开发计划 (Dev Plan) |
| 60 | Phase 6 Test | 测试计划 (Test Plan) |
| 61 | Phase 6 Test | 测试报告 (Test Report) |
| 70 | Phase 7 Deploy | 发布说明 (Release Note) |
| 71 | Phase 7 Deploy | 变更日志 (Changelog) |
| 90 | 通用 | 进度日志 (Progress Log) |

## 创建新功能

使用 Claude Code 命令快速创建功能目录：

```bash
# 在 Claude Code 中执行
/new-feature my-feature-name
```

这会自动生成包含所有模板的功能目录，包括：
- 10_CONTEXT.md（功能上下文）
- 90_PROGRESS_LOG.yaml（进度日志）
- PHASE_GATE.yaml（Gate 规则）
- PHASE_GATE_STATUS.yaml（Gate 状态）
- DOC_CHANGELOG.md（文档变更日志）
- _demos/（Demo 目录）

## 文档模板位置

所有模板定义在 `CC_COLLABORATION/03_templates/` 目录中。

---

_由 AI 协作开发框架生成_
