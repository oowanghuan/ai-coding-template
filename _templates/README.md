# _templates - 系统模板库

> 版本：v1.1
> 最后更新：2025-12-11

---

## 概述

本目录包含 AI 协作开发框架的所有**模板定义**。用户 clone 仓库后可以：

1. **直接使用**：按默认模板初始化项目
2. **自定义模板**：修改模板内容后再初始化

模板内容可自定义，但**流程、命令、生成的文件名保持一致**。

---

## 目录结构

```
_templates/
│
├── README.md                              # 本文件
│
├── CC_COLLABORATION/                      # Claude Code 协作框架
│   ├── 00_OVERVIEW.md                     # 框架总览
│   ├── 01_COMMIT_RULES.md                 # Git 提交规范
│   ├── 04_AI_WORKFLOW.md                  # 8 阶段工作流定义
│   ├── 05_TOOL_DEFINITIONS.md             # 工具定义说明
│   │
│   ├── 02_WORKFLOWS/                      # 工作流脚本（5 个）
│   │
│   ├── 03_TEMPLATES/                      # 文档模板（按编号）
│   │   ├── 00_CONTEXT_TEMPLATE.md         # 功能上下文
│   │   ├── 01_PROJECT_PROFILE_TEMPLATE.yaml
│   │   ├── 10_DESIGN_TEMPLATE.md          # 详细设计
│   │   ├── 11_UI_FLOW_SPEC_TEMPLATE.md    # UI 流程规格
│   │   ├── 11_API_SPEC_TEMPLATE.md        # API 规格
│   │   ├── 12_DEMO_REVIEW_TEMPLATE.md     # Demo 评审
│   │   ├── 20_DEV_PLAN_TEMPLATE.md        # 开发计划
│   │   ├── 30_PROGRESS_LOG_TEMPLATE.yaml  # 进度日志
│   │   ├── 31_DAILY_SUMMARY_TEMPLATE.md   # 每日总结
│   │   ├── 40_TEST_PLAN_TEMPLATE.md       # 测试计划
│   │   ├── 41_TEST_REPORT_TEMPLATE.md     # 测试报告
│   │   ├── 50_RELEASE_NOTE_TEMPLATE.md    # 发布说明
│   │   └── 51_CHANGELOG_TEMPLATE.md       # 变更日志
│   │
│   └── 05_TOOLS/                          # 工具库
│       ├── slash-commands/                # 10 个 Slash Commands
│       ├── skills/                        # 13 个 Skills
│       └── subagents/                     # 4 个 Subagents
│
└── _foundation_templates/                 # Foundation 层模板
    ├── 02_API_CONVENTIONS_TEMPLATE.md     # API 规范模板
    ├── 03_DB_CONVENTIONS_TEMPLATE.md      # DB 规范模板
    └── _ui_system_template/               # UI 系统模板
        ├── 00_UI_TOKENS_TEMPLATE.md
        ├── 01_COMPONENT_LIBRARY_TEMPLATE.md
        ├── 02_LAYOUT_RULES_TEMPLATE.md
        ├── 03_INTERACTION_RULES_TEMPLATE.md
        ├── 04_PAGE_TEMPLATES_TEMPLATE.md
        └── 05_WORKFLOW_TEMPLATES_TEMPLATE.md
```

---

## 使用方式

### 方式 1：默认模板初始化

```bash
# 在 Claude Code 中
/init-project

# 会根据 _templates 中的模板
# 在 docs/_foundation/ 目录生成项目基础文件
```

### 方式 2：自定义模板后初始化

```bash
# 1. 先修改模板（如调整 API 规范）
# 编辑 _templates/_foundation_templates/02_API_CONVENTIONS_TEMPLATE.md

# 2. 再执行初始化
/init-project
```

---

## 模板与生成文件的对应关系

| 模板 | 生成位置 |
|------|----------|
| `CC_COLLABORATION/03_TEMPLATES/00_CONTEXT_TEMPLATE.md` | `docs/{feature}/00_CONTEXT.md` |
| `CC_COLLABORATION/03_TEMPLATES/30_PROGRESS_LOG_TEMPLATE.yaml` | `docs/{feature}/30_PROGRESS_LOG.yaml` |
| `_foundation_templates/02_API_CONVENTIONS_TEMPLATE.md` | `docs/_foundation/02_API_CONVENTIONS.md` |
| `_foundation_templates/_ui_system_template/*` | `docs/_foundation/_ui_system/*` |

---

## 编号规则

模板文件名的数字前缀对应工作流阶段：

| 前缀 | 阶段 | 文档类型 |
|------|------|----------|
| 00 | Phase 0/1 | 上下文 (Context) |
| 01 | Phase 0 | 项目配置 (Profile) |
| 10 | Phase 4 | 详细设计 (Design) |
| 11 | Phase 2 | 规格定义 (Spec) |
| 12 | Phase 3 | Demo 评审 |
| 20 | Phase 5 | 开发计划 (Dev Plan) |
| 30 | Phase 5 | 进度日志 |
| 31 | Phase 5 | 每日总结 |
| 40 | Phase 6 | 测试计划 |
| 41 | Phase 6 | 测试报告 |
| 50 | Phase 7 | 发布说明 |

---

## 注意事项

1. **不要直接修改 CC_COLLABORATION 的结构**，这是框架核心
2. **可以修改模板内容**，以适应你的项目需求
3. **工具库（05_TOOLS）需要安装到 .claude/commands/**：
   ```bash
   ./scripts/init-claude-tools.sh --target=.
   ```

---

_由 Claude Code 生成_
