# /new-feature - 创建新功能模块

你是一个 AI 协作开发助手。用户请求创建一个新的功能模块。

## 参数

- `$ARGUMENTS`：功能模块名称（如 `user-auth`、`payment-system`）

## 执行步骤

### 1. 验证参数

如果 `$ARGUMENTS` 为空，请提示用户：
```
请提供功能名称，例如：/new-feature user-auth
```

### 2. 创建功能目录

在 `docs/` 下创建功能目录：

```
docs/{feature-name}/
├── 10_CONTEXT.md              # 功能上下文（必需）
├── 90_PROGRESS_LOG.yaml       # 进度日志（必需）
├── PHASE_GATE.yaml            # Gate 规则配置（必需，v1.2 新增）
├── PHASE_GATE_STATUS.yaml     # Gate 运行状态（必需，v1.2 新增）
└── _demos/                    # Demo 文件目录
    └── .gitkeep               # 保持目录存在
```

创建 `_demos/` 目录用于存放该功能的 Demo 文件（由 `/gen-demo` 命令生成）。

### 3. 生成 10_CONTEXT.md

使用以下模板生成 `10_CONTEXT.md`：

```markdown
# 10_CONTEXT.md
# {Feature Name} - 功能上下文

> 版本：v0.1
> 最后更新：{current_date}
> 状态：Draft
> 负责人：{请补充}

---

## 1. 功能概述

### 1.1 背景

{请描述功能背景和解决的问题}

### 1.2 目标

- **目标 1**：{请补充}
- **目标 2**：{请补充}
- **目标 3**：{请补充}

### 1.3 预期价值

| 价值点 | 衡量指标 | 目标值 |
|--------|----------|--------|
| {价值1} | {指标} | {目标} |

---

## 2. 功能范围

### 2.1 包含内容（In Scope）

- {请列举}

### 2.2 不包含内容（Out of Scope）

- {请列举}

### 2.3 未来规划（Future Scope）

- {请列举}

---

## 3. 用户与场景

### 3.1 目标用户

| 用户类型 | 描述 | 核心诉求 |
|----------|------|----------|
| {用户1} | {描述} | {诉求} |

### 3.2 核心场景

#### 场景 1：{场景名称}

```
角色：{角色}
目的：{目的}
前置条件：{条件}
步骤：
  1. {步骤1}
  2. {步骤2}
预期结果：{结果}
```

---

## 4. 技术方案

{请在 Spec 阶段补充}

---

## 5. 依赖与集成

### 5.1 内部依赖

| 依赖模块 | 依赖内容 | 状态 |
|----------|----------|------|
| {模块} | {内容} | {状态} |

### 5.2 外部依赖

| 外部系统 | 集成方式 | 状态 |
|----------|----------|------|
| {系统} | {方式} | {状态} |

---

## 6. 里程碑

| 阶段 | 交付物 | 状态 |
|------|--------|------|
| Kickoff | 10_CONTEXT.md | Draft |
| Spec | 40_DESIGN_FINAL.md | 待开始 |
| Code | 功能实现 | 待开始 |
| Test | 测试报告 | 待开始 |
| Deploy | 上线 | 待开始 |

---

## 7. 相关文档

- 工作流总纲：`docs/_system/CC_COLLABORATION/04_AI_WORKFLOW.md`
- 进度日志：`docs/{feature-name}/90_PROGRESS_LOG.yaml`

---

## CHANGELOG

| 版本 | 日期 | 作者 | 变更内容 |
|------|------|------|----------|
| v0.1 | {current_date} | {作者} | 初始版本 |
```

### 4. 生成 90_PROGRESS_LOG.yaml

使用以下模板生成 `90_PROGRESS_LOG.yaml`：

```yaml
# 90_PROGRESS_LOG.yaml
# 功能模块：{Feature Name}
# 最后更新：{current_datetime}

meta:
  feature: {feature-name}
  feature_name: "{Feature Name}"
  current_phase: 1  # Kickoff
  status: wip
  owner: "{请补充}"
  started_at: {current_date}
  last_updated: {current_datetime}

# ============================================================
# Phase 1: Kickoff（功能启动）- 进行中
# ============================================================
phase_1_kickoff:
  status: wip
  tasks:
    - id: KICK-001
      task: "创建功能目录 docs/{feature-name}/"
      status: done
      completed_at: {current_date}

    - id: KICK-002
      task: "编写 10_CONTEXT.md 功能上下文"
      status: wip
      notes: "需要补充功能描述和目标"

    - id: KICK-003
      task: "创建 90_PROGRESS_LOG.yaml"
      status: done
      completed_at: {current_date}

# ============================================================
# Phase 2: Spec（需求规格）- 待开始
# ============================================================
phase_2_spec:
  status: pending
  tasks:
    - id: SPEC-001
      task: "编写 40_DESIGN_FINAL.md"
      status: pending

# ============================================================
# Phase 5: Code（开发实现）- 待开始
# ============================================================
phase_5_code:
  status: pending
  tasks: []

# ============================================================
# Claude Code 断点恢复信息
# ============================================================
cc_checkpoint:
  session_id: "cc-{current_date}-{feature-name}"
  last_file_edited: "docs/{feature-name}/10_CONTEXT.md"
  last_action: "创建功能目录和初始文档"
  next_step: "补充 10_CONTEXT.md 中的功能描述和目标"
  context_files:
    - "docs/{feature-name}/10_CONTEXT.md"
    - "docs/{feature-name}/90_PROGRESS_LOG.yaml"

# ============================================================
# 统计信息
# ============================================================
stats:
  total_tasks: 4
  done: 2
  wip: 1
  pending: 1
  completion_rate: "50%"
  next_milestone: "完成 Kickoff 阶段，进入 Spec"
```

### 5. 生成 PHASE_GATE.yaml（v1.2 新增）

从模板 `_templates/CC_COLLABORATION/03_TEMPLATES/PHASE_GATE_TEMPLATE.yaml` 生成，替换变量：

```yaml
# PHASE_GATE.yaml
# Phase Gate 规则配置文件
# 功能模块：{feature-name}

meta:
  feature: "{feature-name}"
  schema_version: "1.2"
  created_at: "{current_date}"

feature_profile:
  has_ui: true                    # 根据功能类型调整
  demo_required: true             # 根据功能类型调整

# Phase 1-7 的 Gate 规则（从模板复制完整内容）
# ...
```

### 6. 生成 PHASE_GATE_STATUS.yaml（v1.2 新增）

从模板 `_templates/CC_COLLABORATION/03_TEMPLATES/PHASE_GATE_STATUS_TEMPLATE.yaml` 生成，替换变量：

```yaml
# PHASE_GATE_STATUS.yaml
# Phase Gate 运行态文件
# 功能模块：{feature-name}

meta:
  feature: "{feature-name}"
  last_updated: "{current_datetime}"

# Phase 1-7 的 Gate 状态（从模板复制完整内容）
# 所有 gate_state 初始为 pending
# ...
```

### 7. 输出结果

创建完成后，输出以下信息：

```
✅ 功能模块 "{feature-name}" 创建成功！

📁 目录结构：
docs/{feature-name}/
├── 10_CONTEXT.md              # 功能上下文
├── 90_PROGRESS_LOG.yaml       # 进度日志
├── PHASE_GATE.yaml            # Gate 规则配置
├── PHASE_GATE_STATUS.yaml     # Gate 运行状态
└── _demos/                    # Demo 文件目录

🚦 Phase Gate 已启用！
  - 每个阶段必须通过 Gate 检查才能进入下一阶段
  - 使用 /check-gate {feature-name} 查看 Gate 状态
  - 使用 /approve-gate {feature-name} --phase=N --role=ROLE 审批

📝 下一步操作：
1. 补充 10_CONTEXT.md 中的功能描述、目标和范围
   - 至少 2 条目标
   - 至少 1 条 Non-Goals
   - 验收标准（至少 50 字符）
2. 执行 /check-gate {feature-name} --phase=1 检查 Gate
3. 请 PM 审批后进入 Spec 阶段

💡 提示：
- 使用 /check-progress {feature-name} 查看进度
- 使用 /iresume {feature-name} 恢复工作上下文
- 使用 /next-phase {feature-name} 进入下一阶段（需先通过 Gate）
```

## 注意事项

- 功能名称使用 kebab-case（如 `user-auth`，不是 `userAuth`）
- 自动生成的文档是框架，需要人工补充内容
- 10_CONTEXT.md 状态默认为 Draft，确认后改为 Approved
- **Phase Gate 机制**（v1.2 新增）：
  - `PHASE_GATE.yaml` 定义各阶段的 Gate 规则，一般不需要修改
  - `PHASE_GATE_STATUS.yaml` 记录运行时状态，由系统自动更新
  - 每个阶段必须通过 Gate 检查和审批才能进入下一阶段
  - 可以修改 `feature_profile` 来调整功能类型（如 `has_ui: false`）

## 关联工具

- `/check-gate` - 检查 Gate 状态
- `/approve-gate` - 审批 Gate
- `/next-phase` - 进入下一阶段
- `/check-progress` - 查看进度
- `/iresume` - 恢复工作上下文
