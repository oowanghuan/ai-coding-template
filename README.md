# AI Coding Template

AI 协作开发框架模板 - 让 Claude Code 成为你的得力助手。

## 这是什么？

一套经过实战验证的 **AI 协作开发框架**，包含：

- **8 阶段工作流** - 从需求到上线的完整流程定义
- **标准化模板** - Context、Spec、Design、Test 等文档模板
- **Claude Code 工具库** - 10 个 Slash Commands + 13 个 Skills + 4 个 Subagents
- **项目看板**（可选）- 可视化进度追踪

## 解决什么问题？

使用 AI 写代码时常见的痛点：

| 痛点 | 解决方案 |
|------|----------|
| 上下文丢失 | 标准化文档结构，AI 可快速恢复上下文 |
| 进度不可见 | 自动更新的进度日志 + 可视化看板 |
| 协作混乱 | 明确的人机分工 + 交接清单 |
| 质量失控 | 内置评审和测试流程 |

## 核心机制：上下文恢复

**问题**：Claude Code 的 context window 有限，长对话会被 compact（压缩），之前讨论的细节会丢失。

**解决方案**：将关键信息持久化到文件系统，需要时重新加载。

```
对话中产生的信息 → 写入标准化文档 → compact 后从文档恢复
```

### 工作原理

1. **开发过程中**：进度、决策、问题自动记录到 `30_PROGRESS_LOG.yaml`
2. **每天结束时**：`/end-day` 生成当日总结到 `31_DAILY_SUMMARY/`
3. **恢复上下文时**：`/resume` 或 `/start-day` 读取这些文件，重建上下文

### 恢复的内容

| 文档 | 恢复的信息 |
|------|------------|
| `00_CONTEXT.md` | 功能背景、目标、范围 |
| `10_DESIGN.md` | 技术方案、架构决策 |
| `30_PROGRESS_LOG.yaml` | 已完成任务、当前进度、阻塞问题 |
| `31_DAILY_SUMMARY/` | 历史工作记录 |

### 为什么有效

- **结构化**：不是随意的笔记，而是 AI 可解析的标准格式
- **增量更新**：每次操作自动更新，不需要手动维护
- **按需加载**：只加载当前功能相关的文档，不浪费 context

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/oowanghuan/ai-coding-template.git my-project
cd my-project
```

### 2. 安装 Claude Code 工具

```bash
./scripts/init-claude-tools.sh --target=.
```

这会将 Slash Commands 和 Skills 安装到 `.claude/commands/` 目录。

### 3. 创建第一个功能

在 Claude Code 中执行：

```
/new-feature user-login
```

这会自动生成功能文档目录：

```
docs/user-login/
├── 00_CONTEXT.md        # 待填写：功能背景和目标
├── 30_PROGRESS_LOG.yaml # 自动更新：进度日志
└── ...
```

### 4. 开始开发

```
# 每天开始时
/start-day

# 恢复之前的工作
/resume

# 每天结束时
/end-day
```

## 目录结构

```
my-project/
├── _templates/           # 模板库（核心，勿删）
│   ├── CC_COLLABORATION/ # 协作框架定义
│   │   ├── 04_AI_WORKFLOW.md      # 8 阶段工作流
│   │   ├── 03_TEMPLATES/          # 文档模板
│   │   └── 05_TOOLS/              # 工具定义
│   └── _foundation_templates/     # 基础配置模板
│
├── docs/                 # 功能文档（按功能组织）
│   ├── _foundation/      # 项目级配置
│   └── {feature}/        # 功能模块文档
│
├── _backup/              # 临时备份（定期清理）
├── scripts/              # 工具脚本
└── vue-app/              # 项目看板（可选）
```

## 8 阶段工作流

| 阶段 | 名称 | 目标 |
|------|------|------|
| 0 | Foundation | 建立项目级规范（API/DB/UI） |
| 1 | Kickoff | 初始化功能，填写 Context |
| 2 | Spec | 定义 UI 流程和 API 规格 |
| 3 | Demo | 快速原型验证 |
| 4 | Design | 技术方案设计 |
| 5 | Code | 功能实现 |
| 6 | Test | 测试与质量验证 |
| 7 | Deploy | 发布上线 |

详细说明见 `_templates/CC_COLLABORATION/04_AI_WORKFLOW.md`

## 工具列表

### Slash Commands

| 命令 | 用途 |
|------|------|
| `/new-feature` | 创建新功能目录 |
| `/start-day` | 每日开始，同步上下文 |
| `/end-day` | 每日结束，生成总结 |
| `/resume` | 恢复上次工作 |
| `/check-progress` | 检查进度状态 |
| `/run-tests` | 执行测试 |
| `/release` | 发布流程 |
| `/init-project` | 初始化项目配置 |

### Skills

| 技能 | 用途 |
|------|------|
| `context_loader` | 加载功能上下文 |
| `spec_writer` | 生成规格文档 |
| `progress_tracker` | 更新进度日志 |
| `code_reviewer` | 代码评审 |
| `test_generator` | 生成测试用例 |

完整列表见 `_templates/CC_COLLABORATION/05_TOOLS/`

## 项目看板（可选）

如需使用可视化看板：

```bash
cd vue-app
npm install
npm run dev
```

看板功能：
- 甘特图式进度展示
- GitHub Issue/PR 同步
- 文档在线查看
- 每日进度摘要

> 看板需要配置 Supabase，详见 `vue-app/README.md`

## 自定义模板

所有模板都可以根据项目需求修改：

1. 编辑 `_templates/` 下的模板文件
2. 模板会在下次创建功能时生效
3. 保持文件名和结构不变，只修改内容

## 最佳实践

1. **每天开始执行 `/start-day`** - 让 AI 快速恢复上下文
2. **每天结束执行 `/end-day`** - 自动生成进度总结
3. **保持文档更新** - Context 和 Spec 是 AI 理解需求的关键
4. **定期清理 `_backup/`** - 避免历史文件堆积
5. **先 Spec 后 Code** - 先定义清楚再动手

## 相关资源

- [AI 协作开发框架文档](https://ai-coding-org.vercel.app)
- [Claude Code 官方文档](https://docs.anthropic.com/claude-code)

## License

MIT

---

_让 AI 成为你的编程伙伴，而不是替代品_
