# Changelog

All notable changes to ai-coding-template will be documented in this file.

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
