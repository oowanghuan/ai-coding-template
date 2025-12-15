# /init-project - 初始化项目系统目录

你是一个 AI 协作开发助手。用户请求为项目初始化 AI 协作开发框架的系统目录。

## 参数

- `$ARGUMENTS`：无需参数，在当前项目根目录执行

## 执行步骤

### 1. 检查项目根目录

确认当前目录是项目根目录（存在 `package.json` 或 `.git` 目录）。

如果不是，提示：
```
⚠️ 请在项目根目录执行此命令

检测条件：
• 存在 package.json 文件
• 或存在 .git 目录

当前目录：{current_dir}
```

### 2. 检查是否已初始化

检查 `docs/_system/` 目录是否已存在。

如果已存在，提示：
```
⚠️ 项目已初始化 AI 协作框架

现有目录结构：
docs/_system/
├── CC_COLLABORATION/
│   ├── ...
│   └── ...

是否要重新初始化？这将覆盖现有配置。[y/N]
```

### 3. 创建目录结构

创建以下目录结构：

```
docs/
├── _system/
│   └── CC_COLLABORATION/
│       ├── 01_OVERVIEW.md           # 框架概述
│       ├── 02_ROLES.md              # 角色定义
│       ├── 03_templates/            # 文档模板
│       │   ├── 10_CONTEXT.md
│       │   ├── 40_DESIGN_FINAL.md
│       │   ├── 20_UI_FLOW_SPEC.md
│       │   └── 90_PROGRESS_LOG.yaml
│       ├── 04_AI_WORKFLOW.md        # 工作流定义
│       └── 05_TOOLS/                # 工具库
│           ├── README.md
│           └── slash-commands/
│               ├── new-feature.md
│               ├── resume.md
│               ├── daily-summary.md
│               ├── check-progress.md
│               ├── gen-demo.md
│               ├── run-tests.md
│               ├── release.md
│               └── init-project.md
└── .gitkeep
```

### 4. 生成核心文档

#### 4.1 01_OVERVIEW.md

```markdown
# AI 协作开发框架

> 版本：v1.0
> 初始化日期：{current_date}

---

## 简介

本项目采用 AI 协作开发框架，通过标准化的流程和工具，实现人类与 AI（Claude Code）的高效协作。

## 核心概念

### 8 阶段工作流

1. **Phase 0 - Foundation**：基础设施准备
2. **Phase 1 - Kickoff**：功能启动
3. **Phase 2 - Spec**：需求规格
4. **Phase 3 - UI Flow**：界面流程
5. **Phase 4 - Review**：方案评审
6. **Phase 5 - Code**：开发实现
7. **Phase 6 - Test**：测试验证
8. **Phase 7 - Deploy**：发布部署

### 角色分工

- **System Architect**：系统架构，负责 Phase 0
- **Product Manager**：产品需求，负责 Phase 1
- **AI PE**：AI 提示工程，负责 Phase 2-4
- **Developer / Claude Code**：开发实现，负责 Phase 5-7

### 文档体系

每个功能模块在 `docs/{feature-name}/` 下维护独立文档：
- `10_CONTEXT.md` - 功能上下文
- `40_DESIGN_FINAL.md` - 设计文档
- `20_UI_FLOW_SPEC.md` - UI 流程规格
- `90_PROGRESS_LOG.yaml` - 进度日志
- `40_TEST_REPORT.md` - 测试报告
- `70_RELEASE_NOTES/` - 发布说明

## 快速开始

1. 使用 `/new-feature <name>` 创建功能模块
2. 按照工作流推进各阶段
3. 使用 `/check-progress` 查看进度
4. 使用 `/iresume` 恢复工作上下文

## 相关文档

- 角色定义：`02_ROLES.md`
- 工作流详情：`04_AI_WORKFLOW.md`
- 工具使用：`05_TOOLS/README.md`
```

#### 4.2 02_ROLES.md

```markdown
# 角色定义

> 版本：v1.0
> 最后更新：{current_date}

---

## 角色概览

| 角色 | 主要职责 | 负责阶段 |
|------|----------|----------|
| System Architect | 技术架构 | Phase 0 |
| Product Manager | 产品定义 | Phase 1 |
| AI PE | 规格设计 | Phase 2-4 |
| Developer / Claude Code | 开发测试 | Phase 5-7 |

## 角色详情

### System Architect

**职责**：
- 制定技术架构
- 建立项目结构
- 配置开发环境
- 定义技术标准

**交付物**：
- 技术架构文档
- 项目初始化配置
- 开发规范

### Product Manager

**职责**：
- 定义产品需求
- 确定功能范围
- 设定优先级
- 协调资源

**交付物**：
- 功能上下文（10_CONTEXT.md）
- 需求清单
- 优先级排序

### AI PE (AI Prompt Engineer)

**职责**：
- 编写详细规格
- 设计 UI 流程
- 准备 AI 开发上下文
- 主持方案评审

**交付物**：
- 设计文档（40_DESIGN_FINAL.md）
- UI 流程规格（20_UI_FLOW_SPEC.md）
- 评审记录

### Developer / Claude Code

**职责**：
- 实现功能代码
- 编写测试
- 修复问题
- 发布部署

**交付物**：
- 功能代码
- 测试报告（40_TEST_REPORT.md）
- 发布说明（70_RELEASE_NOTES/）

## 协作流程

各角色按阶段接力，上一阶段的交付物是下一阶段的输入。
详见 `04_AI_WORKFLOW.md`。
```

### 5. 安装 Slash Commands

复制 `05_TOOLS/slash-commands/` 下的所有文件到 `.claude/commands/`：

```bash
mkdir -p .claude/commands
cp docs/_system/CC_COLLABORATION/05_TOOLS/slash-commands/*.md .claude/commands/
```

### 6. 输出结果

```
✅ 项目初始化成功！

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 创建的目录结构
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
docs/
├── _system/
│   └── CC_COLLABORATION/
│       ├── 01_OVERVIEW.md
│       ├── 02_ROLES.md
│       ├── 03_templates/
│       ├── 04_AI_WORKFLOW.md
│       └── 05_TOOLS/

.claude/
└── commands/
    ├── new-feature.md
    ├── resume.md
    ├── daily-summary.md
    └── ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 可用命令
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• /new-feature <name>   创建新功能模块
• /iresume <feature>     恢复工作上下文
• /daily-summary        生成每日总结
• /check-progress       查看进度状态
• /gen-demo <feature>   生成 Demo
• /run-tests <feature>  执行测试
• /release <f> <v>      生成发布说明

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 下一步:
1. 阅读 docs/_system/CC_COLLABORATION/01_OVERVIEW.md 了解框架
2. 使用 /new-feature <name> 创建第一个功能模块
3. 按照 04_AI_WORKFLOW.md 定义的流程推进开发

祝开发顺利！🚀
```

## 注意事项

- 此命令只在项目根目录执行
- 不会覆盖已存在的 `docs/` 下的功能文档
- 会覆盖 `_system/` 目录（如果确认重新初始化）
- Slash Commands 会复制到 `.claude/commands/`
- 建议将生成的文件提交到版本控制
