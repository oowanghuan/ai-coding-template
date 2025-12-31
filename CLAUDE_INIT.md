# CLAUDE_INIT.md
# AI 初始化指南 - 本文档供 Claude Code 读取并执行

> **读者**：Claude Code (AI)
> **目的**：读取本文档后，自动完成项目初始化
> **触发方式**：用户说「初始化项目」「按照模板设置」「帮我配置好这个框架」等

---

## 执行前检查

在执行初始化之前，请先确认：

```
检查项 1：当前目录是否是项目根目录？
  - 应该能看到 CC_COLLABORATION/ 目录
  - 应该能看到 .claude/ 目录
  - 如果不存在，提示用户先克隆模板仓库

检查项 2：是否已经初始化过？
  - 检查 docs/ 目录下是否已有功能模块
  - 如果有，询问用户是否要继续添加新功能，而不是重新初始化
```

---

## 初始化步骤

### Step 1: 确认项目信息

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

### Step 2: 初始化 Git（如果需要）

```bash
# 检查是否已有 .git 目录
if [ ! -d ".git" ]; then
  # 如果是从模板克隆的，需要重新初始化
  rm -rf .git
  git init
  git add .
  git commit -m "init: 基于 ai-coding-template 初始化项目"
fi
```

### Step 3: 创建第一个功能模块

执行 `/new-feature {功能名称}` 命令，这会自动创建：

```
docs/{功能名称}/
├── 10_CONTEXT.md           # 功能上下文
├── 90_PROGRESS_LOG.yaml    # 进度日志
├── PHASE_GATE.yaml         # Gate 规则
├── PHASE_GATE_STATUS.yaml  # Gate 状态
└── _demos/                 # Demo 文件目录
```

### Step 4: 引导用户填写 Context

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

### Step 5: 检查 Phase 1 Gate

```bash
/check-gate {功能名称} --phase=1
```

确保 Context 文档满足 Gate 要求：
- 目标至少 2 条
- 有明确的非目标
- 验收标准至少 50 字符

### Step 6: 输出初始化完成摘要

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

## 后续工作流提示

初始化完成后，按照 8 阶段工作流推进：

```
Phase 0: Foundation  → 项目级配置（通常跳过）
Phase 1: Kickoff     → 当前阶段，完善 Context
Phase 2: Spec        → 编写 UI/API 规格
Phase 3: Demo        → 生成交互原型
Phase 4: Design      → 技术方案设计
Phase 5: Code        → 编码实现
Phase 6: Test        → 测试验证
Phase 7: Deploy      → 发布上线
```

每个阶段完成后：
1. `/check-gate {功能名称}` - 检查 Gate 状态
2. `/approve-gate {功能名称} --phase=N --role=ROLE` - 审批
3. `/next-phase {功能名称}` - 进入下一阶段

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
文档版本: v1.0
最后更新: 2025-12-31
适用于: ai-coding-template v2.0+
```
