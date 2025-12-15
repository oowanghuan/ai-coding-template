# Changelog

All notable changes to ai-coding-template will be documented in this file.

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

- [AI 协作开发框架文档](https://ai-coding-org.vercel.app)
- [Claude Code 官方文档](https://docs.anthropic.com/claude-code)

---

_🤖 Generated with Claude Code_
