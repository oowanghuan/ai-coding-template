# AI Coding Template

> AI 协作开发框架模板 - 让 AI 成为你的开发伙伴

## 1. 这是什么？

一套经过实战验证的 **AI 协作开发框架**，包含：

- **7 阶段工作流** - 可裁剪，按需选用
- **标准化模板** - Context、Spec、Design、Test 等文档模板
- **Claude Code 工具库** - Slash Commands + Skills + Subagents
- **Phase Gate 机制** - 质量门禁，确保每个阶段的交付质量

## 2. 核心理念

```
Human-AI Loop = 人类决策 + AI 执行 + 质量把控
```

- **人类负责**：目标定义、架构决策、质量审批
- **AI 负责**：代码生成、文档编写、任务执行
- **流程保障**：Phase Gate 机制确保每个阶段的质量

## 3. 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/oowanghuan/ai-coding-template.git my-project
cd my-project
rm -rf .git && git init  # 初始化为自己的仓库
```

### 2. 安装 Claude Code 工具

```bash
./scripts/init-claude-tools.sh --target=.
```

### 3. 创建第一个功能

在 Claude Code 中执行：

```
/new-feature user-login
```

这会自动生成功能文档目录：

```
docs/user-login/
├── 10_CONTEXT.md           # 待填写：功能背景和目标
├── 90_PROGRESS_LOG.yaml    # 自动更新：进度日志
├── PHASE_GATE.yaml         # 质量关卡配置
└── PHASE_GATE_STATUS.yaml  # 关卡状态
```

### 4. 开始开发

```bash
# 每天开始时
/start-day

# 恢复之前的工作
/iresume

# 检查 Phase Gate 状态
/check-gate user-login

# 每天结束时
/end-day
```

## 4. 目录结构

```
my-project/
├── .claude/                  # Claude Code 配置
│   ├── commands/             # Slash 命令
│   ├── hooks/                # Hook 脚本
│   └── settings.json         # 项目设置
│
├── CC_COLLABORATION/         # 协作框架（核心）
│   ├── 00_overview/          # 框架概述
│   ├── 01_commit_rules/      # 提交规范
│   ├── 02_workflows/         # 工作流定义
│   ├── 03_templates/         # 文档模板
│   │   ├── 01_kickoff/       # Phase 1 模板
│   │   ├── 02_spec/          # Phase 2 模板
│   │   └── ...               # Phase 3-7 模板
│   ├── 04_ai_workflow/       # 7 阶段工作流说明
│   ├── 05_tools/             # 工具定义
│   ├── 06_roles_guide/       # 角色指南
│   └── 07_phase_gate/        # Phase Gate 定义
│
├── docs/                     # 功能文档（按功能组织）
│   └── {feature}/            # 功能模块文档
│
└── scripts/                  # 工具脚本
```

## 5. 7 阶段工作流

| Phase | 名称 | 核心产出 | 价值 |
|-------|------|----------|------|
| 1 | **Kickoff** | 10_CONTEXT.md | 明确目标和范围 |
| 2 | **Spec** | 21_UI_FLOW_SPEC.md | 精确可执行的规格 |
| 3 | **Demo** | 交互原型 | 用户体验验证 |
| 4 | **Design** | 40_DESIGN_FINAL.md | 技术方案设计 |
| 5 | **Code** | 功能代码 | AI 按设计实现 |
| 6 | **Test** | 测试报告 | 质量验证 |
| 7 | **Deploy** | 发布说明 | 上线交付 |

> 详细说明见 `CC_COLLABORATION/04_ai_workflow/`

## 6. 工具列表

### Slash Commands

| 命令 | 用途 |
|------|------|
| `/new-feature` | 创建新功能目录 |
| `/start-day` | 每日开始，同步上下文 |
| `/end-day` | 每日结束，生成总结 |
| `/iresume` | 恢复上次工作 |
| `/check-progress` | 检查进度状态 |
| `/check-gate` | 检查 Phase Gate 状态 |
| `/approve-gate` | 审批 Phase Gate |
| `/next-phase` | 进入下一阶段 |
| `/expert-review` | 调用 OpenAI 独立专家评审 |
| `/run-tests` | 执行测试 |
| `/release` | 发布流程 |

完整列表见 `CC_COLLABORATION/05_tools/`

## 7. 可视化工作台

如果你需要**可视化的项目管理界面**，推荐使用 [HA Loop Desk](https://github.com/oowanghuan/ha-loop-desk)：

- 📊 **甘特图视图** - 追踪多功能模块进度
- 🔄 **Daily Standup** - 每日站会面板
- 🚦 **Phase Gate 状态** - 可视化质量关卡

HA Loop Desk 是本框架的**可视化伴侣工具**，读取 `docs/` 目录下的 YAML 文件，提供图形化的项目状态视图。

```bash
# 下载 HA Loop Desk
# https://github.com/oowanghuan/ha-loop-desk/releases

# 打开后选择你的项目目录即可
```

## 8. Phase Gate 机制

每个阶段都有质量关卡，确保交付质量：

```bash
# 检查当前阶段的 Gate 状态
/check-gate user-login --phase=2

# 审批通过 Gate
/approve-gate user-login --phase=2 --role=PM

# 进入下一阶段
/next-phase user-login
```

Gate 检查包括：
- **必需产出物**：文档是否齐全
- **质量检查**：内容是否符合要求
- **审批状态**：相关角色是否已审批

## 9. Expert Review（独立专家评审）

解决 AI 协作开发中的核心问题：**AI 自己审自己，没有真正的质量门禁**。

```bash
# 使用 OpenAI GPT-4 作为独立评审方
/expert-review docs/my-feature --phase=4

# 评审结果：
# - GO: 无问题，可继续
# - REVISE: 有建议，可选修复
# - BLOCK: 有严重问题，必须修复
```

需要配置 OpenAI API Key：
```bash
export OPENAI_API_KEY="sk-your-api-key"
```

## 10. 核心机制：上下文恢复

**问题**：Claude Code 的 context window 有限，长对话会被压缩，之前讨论的细节会丢失。

**解决方案**：将关键信息持久化到文件系统，需要时重新加载。

```
对话中产生的信息 → 写入标准化文档 → compact 后从文档恢复
```

| 文档 | 恢复的信息 |
|------|------------|
| `10_CONTEXT.md` | 功能背景、目标、范围 |
| `40_DESIGN_FINAL.md` | 技术方案、架构决策 |
| `90_PROGRESS_LOG.yaml` | 已完成任务、当前进度 |

## 11. 最佳实践

1. **每天开始执行 `/start-day`** - 让 AI 快速恢复上下文
2. **每天结束执行 `/end-day`** - 自动生成进度总结
3. **保持文档更新** - Context 和 Spec 是 AI 理解需求的关键
4. **先 Spec 后 Code** - 先定义清楚再动手
5. **关键阶段使用 Expert Review** - 让独立 AI 评审你的设计

## 12. 相关项目

| 项目 | 说明 |
|------|------|
| [HA Loop Desk](https://github.com/oowanghuan/ha-loop-desk) | 可视化工作台（桌面应用） |

## 13. License

MIT

---

_让 AI 成为你的编程伙伴，而不是替代品_
