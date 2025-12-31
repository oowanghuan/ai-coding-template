# CLAUDE_INIT.md
# AI 初始化指南 - 本文档供 Claude Code 读取并执行

> **读者**：Claude Code (AI)
> **目的**：读取本文档后，自动完成项目初始化
> **触发方式**：用户说「初始化项目」「按照模板设置」「帮我配置好这个框架」等

---

## 场景判断

首先判断用户的场景：

```
场景 A：全新项目
  - 用户还没有克隆模板
  - 需要从 Step 0 开始

场景 B：已克隆，需要初始化
  - 用户已经克隆了模板到本地
  - 从 Step 1 开始

场景 C：已初始化，添加新功能
  - docs/ 目录下已有功能模块
  - 直接执行 /new-feature {功能名}
```

---

## 完整初始化流程

### Step 0: 克隆模板仓库（场景 A）

如果用户还没有克隆模板，指导执行：

```bash
# 克隆模板仓库
git clone https://github.com/oowanghuan/ai-coding-template.git {项目名}
cd {项目名}

# 重置 Git 历史，作为自己的新项目
rm -rf .git
git init
```

**检查点**：执行后应该能看到以下目录结构：
```
{项目名}/
├── .claude/              # Claude Code 配置
├── CC_COLLABORATION/     # 协作框架
├── docs/                 # 功能文档目录
└── scripts/              # 工具脚本
```

### Step 1: 安装 Claude Code 工具

执行安装脚本，将 Slash Commands 和 Skills 安装到项目：

```bash
./scripts/init-claude-tools.sh --target=.
```

**安装内容**：
- `.claude/commands/` - Slash Commands（如 /new-feature, /check-gate）
- `.claude/settings.json` - Claude Code 项目配置

**验证安装**：安装完成后，在 Claude Code 中输入 `/` 应该能看到可用命令列表。

### Step 2: 确认项目信息

向用户询问以下信息（如果用户没有主动提供）：

```
必需信息：
  - 项目名称（用于显示）
  - 第一个要开发的功能名称（kebab-case，如 user-auth）

可选信息：
  - 项目简述（一句话描述）
  - 技术栈（前端/后端/全栈）
  - 是否需要 UI（影响 Phase 3 Demo 是否跳过）
```

### Step 3: 初始化 Git 仓库

```bash
# 如果还没有初始化 Git
if [ ! -d ".git" ]; then
  git init
fi

# 提交初始代码
git add .
git commit -m "init: 基于 ai-coding-template 初始化项目"
```

### Step 4: 创建第一个功能模块

执行 `/new-feature {功能名称}` 命令，这会自动创建：

```
docs/{功能名称}/
├── 10_CONTEXT.md           # 功能上下文
├── 90_PROGRESS_LOG.yaml    # 进度日志
├── PHASE_GATE.yaml         # Gate 规则
├── PHASE_GATE_STATUS.yaml  # Gate 状态
└── _demos/                 # Demo 文件目录
```

### Step 5: 引导用户填写 Context

打开 `docs/{功能名称}/10_CONTEXT.md`，引导用户填写：

```markdown
需要用户提供的信息：
1. 功能背景 - 为什么要做这个功能？
2. 目标 - 至少 2 条明确目标
3. 非目标 - 明确不做什么
4. 核心场景 - 至少 1 个用户场景
```

**AI 行为**：
- 如果用户已经描述了需求，帮助整理成标准格式写入
- 如果用户没有描述，通过提问引导用户补充

### Step 6: 检查 Phase 1 Gate

```bash
/check-gate {功能名称} --phase=1
```

确保 Context 文档满足 Gate 要求：
- 目标至少 2 条
- 有明确的非目标
- 验收标准至少 50 字符

### Step 7: 输出初始化完成摘要

```
✅ 项目初始化完成！

项目：{项目名称}
功能：{功能名称}
当前阶段：Phase 1 Kickoff

📁 已创建文件：
  - docs/{功能名称}/10_CONTEXT.md
  - docs/{功能名称}/90_PROGRESS_LOG.yaml
  - docs/{功能名称}/PHASE_GATE.yaml
  - docs/{功能名称}/PHASE_GATE_STATUS.yaml

📝 下一步：
  1. 完善 10_CONTEXT.md 中的功能描述
  2. 执行 /check-gate {功能名称} --phase=1 检查
  3. 请 PM 审批后进入 Phase 2 Spec

💡 常用命令：
  /check-progress     - 查看整体进度
  /start-day          - 每日开始
  /end-day            - 每日结束
```

---

## 日常开发工作流

初始化完成后，每天的工作流程：

### 每日开始

```bash
/start-day
```

这会：
- 读取 `90_PROGRESS_LOG.yaml` 恢复上下文
- 显示昨天的进度和今天的待办
- 让 AI 快速「记起」之前的工作

### 断点恢复

如果 Claude Code 发生 compact（上下文压缩）或重启：

```bash
/iresume
```

这会从 `90_PROGRESS_LOG.yaml` 中读取：
- 当前进行的任务
- 上次编辑的文件
- 下一步操作

### 检查进度

```bash
/check-progress {功能名称}
```

### 每日结束

```bash
/end-day
```

这会：
- 总结今天完成的工作
- 更新进度日志
- 生成 Daily Standup 数据

---

## 8 阶段工作流

初始化完成后，按照 8 阶段工作流推进：

| Phase | 名称 | 核心产出 | 说明 |
|-------|------|----------|------|
| 0 | Foundation | 项目配置 | 项目级基础设施（通常跳过） |
| 1 | Kickoff | 10_CONTEXT.md | 明确目标和范围 |
| 2 | Spec | 21_UI_FLOW_SPEC.md | 精确可执行的规格 |
| 3 | Demo | 交互原型 | 用户体验验证 |
| 4 | Design | 40_DESIGN_FINAL.md | 技术方案设计 |
| 5 | Code | 功能代码 | AI 按设计实现 |
| 6 | Test | 测试报告 | 质量验证 |
| 7 | Deploy | 发布说明 | 上线交付 |

### Phase Gate 工作流

每个阶段完成后：

```bash
# 1. 检查 Gate 状态
/check-gate {功能名称} --phase=N

# 2. 审批通过（需要对应角色）
/approve-gate {功能名称} --phase=N --role=ROLE

# 3. 进入下一阶段
/next-phase {功能名称}
```

### 关键阶段使用 Expert Review

对于重要的设计文档，可以调用独立 AI 评审：

```bash
/expert-review docs/{功能名称} --phase=4
```

这会使用 OpenAI GPT-4 作为独立评审方，避免「自己审自己」。

---

## 错误处理

### 如果用户在非模板项目中执行

```
检测到当前目录不是 ai-coding-template 项目。

请先克隆模板：
git clone https://github.com/oowanghuan/ai-coding-template.git {项目名}
cd {项目名}

然后重新执行初始化。
```

### 如果功能名称格式不对

```
功能名称应使用 kebab-case 格式：
  ✅ user-auth
  ✅ payment-system
  ❌ userAuth
  ❌ UserAuth
  ❌ user_auth
```

### 如果 Gate 检查失败

引导用户补充缺失的内容，而不是直接跳过。

---

## 元信息

```yaml
文档版本: v1.1
最后更新: 2025-12-31
适用于: ai-coding-template v2.0+
```
