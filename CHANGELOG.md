# Changelog

All notable changes to ai-coding-template will be documented in this file.

---

## [v2.0.0] - 2025-12-31

### 🎉 Major Release: 可视化工作台独立

重大架构调整：将可视化工作台独立为 [HA Loop Desk](https://github.com/oowanghuan/ha-loop-desk) 项目。

### Added

- **HA Loop Desk** - 独立的可视化工作台应用
  - 甘特图进度视图
  - Daily Standup 面板
  - Phase Gate 状态显示
  - 实时文件监控

### Changed

- **项目定位明确** - 本仓库专注于框架模板，可视化由 HA Loop Desk 提供

### 项目关系

```
ai-coding-template          HA Loop Desk
═══════════════════         ═══════════════
方法论 + 模板               可视化工作台

- SDLC 阶段定义      ──→    - 甘特图进度视图
- 文档模板                  - Daily Standup 面板
- Phase Gate 机制           - Phase Gate 状态显示
- 进度日志 (YAML)           - 实时文件监控
```

---

## [v1.4.0] - 2025-12-19

### Added

- **Expert Review** - 外部专家评审集成（支持 OpenAI API）
- **Dashboard View** - 多功能模块甘特图视图
- **Daily Standup** - `/end-day` 生成每日站会数据

### Changed

- **Phase Gate 增强** - 支持 External Gate 和 Override 机制
- **Schema Discovery** - 自动识别项目配置和功能模块

---

## [v1.3.0] - 2024-12-15

### 🔧 Breaking Change: 文件编号规范化

**修复文件编号约定**：将所有模板文件编号调整为按 Phase 顺序排列。

#### 编号变更

| Phase | 旧编号 | 新编号 | 文件 |
|-------|--------|--------|------|
| 1 Kickoff | 00_ | 10_ | 10_CONTEXT |
| 2 Spec | 11_ | 20_/21_ | 20_API_SPEC, 21_UI_FLOW_SPEC |
| 3 Demo | 12_ | 30_ | 30_DEMO_REVIEW |
| 4 Design | 10_ | 40_ | 40_DESIGN_FINAL |
| 5 Code | 20_ | 50_ | 50_DEV_PLAN |
| 6 Test | 40_/41_ | 60_/61_ | 60_TEST_PLAN, 61_TEST_REPORT |
| 7 Deploy | 50_/51_ | 70_/71_ | 70_RELEASE_NOTE, 71_CHANGELOG |
| 通用 | 30_/31_ | 90_/91_ | 90_PROGRESS_LOG, 91_DAILY_SUMMARY |

#### 迁移指南

如果项目中已有旧编号的文件，需要重命名：
```bash
mv 00_CONTEXT.md 10_CONTEXT.md
mv 11_API_SPEC.md 20_API_SPEC.md
mv 10_DESIGN_FINAL.md 40_DESIGN_FINAL.md
mv 30_PROGRESS_LOG.yaml 90_PROGRESS_LOG.yaml
```

---

## [v1.2.0] - 2024-12-15

### 🚀 New Feature: Phase Gate System

新增 **Phase Gate 质量门禁系统**，确保每个阶段的交付物质量。

#### 新增模板
- `PHASE_GATE_TEMPLATE.yaml` - Phase Gate 检查项定义
- `PHASE_GATE_STATUS_TEMPLATE.yaml` - Gate 状态追踪

#### 新增工具
- **Skill**: `gate_checker` - 自动检查 Gate 条件
- **Slash Commands**:
  - `/check-gate` - 检查当前阶段 Gate 状态
  - `/approve-gate` - 审批通过 Gate
  - `/next-phase` - 进入下一阶段

#### 新增文档
- `07_phase_gate/README.md` - Phase Gate 完整指南

---

## [v1.1.0] - 2024-12-15

### 🔧 Major Refactoring

**目录结构大重组**：简化并优化了模板库的目录结构，使其更加清晰和易于使用。

### Breaking Changes

- **CC_COLLABORATION 提升为一级目录**：原 `_templates/CC_COLLABORATION/` 现直接位于根目录
- **Foundation 模板整合**：原 `_templates/_foundation_templates/` 移入 `CC_COLLABORATION/03_templates/_foundation/`
- **删除 _templates 目录**：不再使用中间层目录

### 新的目录结构

```
CC_COLLABORATION/
├── 00_overview/README.md
├── 01_commit_rules/README.md
├── 02_workflows/
├── 03_templates/
│   ├── _common/              # 通用模板
│   ├── _foundation/          # Foundation 级模板
│   │   ├── _api_system_template/
│   │   ├── _ui_system_template/
│   │   └── 03_DB_CONVENTIONS_TEMPLATE.md
│   ├── 01_kickoff/
│   ├── 02_spec/
│   ├── 03_demo/
│   ├── 04_design/
│   ├── 05_code/
│   ├── 06_test/
│   └── 07_deploy/
├── 04_ai_workflow/README.md
├── 05_tools/
└── 06_roles_guide/README.md
```

### New Features

- **API System 模板扩展**：新增 4 个 API 规范模板
  - `00_REST_CONVENTIONS_TEMPLATE.md` - HTTP REST API 设计标准
  - `01_COMMAND_CONVENTIONS_TEMPLATE.md` - Slash Command 设计标准
  - `02_YAML_SCHEMA_CONVENTIONS_TEMPLATE.md` - YAML 文件结构标准
  - `03_EXTERNAL_API_CONVENTIONS_TEMPLATE.md` - 外部 API 调用标准

### Documentation Updates

- 更新 `04_ai_workflow/README.md` 版本至 v1.3
- 更新所有模板路径引用
- 更新工具文档中的路径引用（doc_generator, system_scaffolder, init-project）

### Migration Guide

如果你正在使用旧版本，请按以下步骤迁移：

1. 删除旧的 `_templates/` 目录
2. 复制新的 `CC_COLLABORATION/` 目录到项目中
3. 更新项目中的模板路径引用

---

## [v1.0.0] - 2024-12-12

### 🎉 Initial Release

这是 ai-coding-template 的首个正式发布版本。

### Features

- **8 阶段工作流** - 可裁剪的完整开发流程（Phase 0-7）
- **10 个 Slash Commands** - 完整的 Claude Code 命令库
- **标准化模板** - Context、Spec、Design、Test 等文档模板
- **安装脚本** - 一键安装工具到项目
- **项目看板**（可选）- Vue 3 + Element Plus 可视化看板

### Slash Commands

| 命令 | 用途 |
|------|------|
| `/new-feature` | 创建新功能目录 |
| `/start-day` | 每日开始，恢复上下文 |
| `/end-day` | 每日结束，生成总结 |
| `/iresume` | 断点恢复 |
| `/check-progress` | 检查进度状态 |
| `/daily-summary` | 生成每日总结 |
| `/gen-demo` | 生成 Demo |
| `/run-tests` | 执行测试 |
| `/release` | 发布流程 |
| `/init-project` | 初始化项目配置 |

### Documentation

- 完整的 README 使用指南
- 8 阶段工作流详细说明
- 「真实工作流：从定义到现场交付」章节
- 核心机制：上下文恢复原理说明

### Quick Start

```bash
git clone https://github.com/oowanghuan/ai-coding-template.git my-project
cd my-project
./scripts/init-claude-tools.sh --target=.
# 在 Claude Code 中执行：/new-feature my-first-feature
```

---

## 相关链接

- [HA Loop Desk](https://github.com/oowanghuan/ha-loop-desk) - 可视化工作台
- [Claude Code 官方文档](https://docs.anthropic.com/claude-code)

---

_🤖 Generated with Claude Code_
