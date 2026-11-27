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
├── PHASE_GATE.yaml            # Phase Gate 规则配置（必需）
├── PHASE_GATE_STATUS.yaml     # Phase Gate 运行状态（必需）
├── DOC_CHANGELOG.md           # 文档变更日志（必需）
└── _demos/                    # Demo 文件目录
    └── .gitkeep               # 保持目录存在
```

创建 `_demos/` 目录用于存放该功能的 Demo 文件（由 `/gen-demo` 命令生成）。
创建 `DOC_CHANGELOG.md` 用于记录该功能模块下所有文档的修改历史。
创建 `PHASE_GATE.yaml` 和 `PHASE_GATE_STATUS.yaml` 用于 Phase Gate 机制（由 `/check-gate` 和 `/ai-pm` 命令使用）。

### 3. 生成 10_CONTEXT.md（智能模式 vs 模板模式）

根据用户是否提供功能描述，选择不同的生成模式：

#### 3.1 智能生成模式（用户提供了功能描述）

如果用户提供了功能描述（如 `/new-feature user-auth "用户登录注册模块，支持邮箱验证"`），则：

**步骤 A：解析需求描述**

从用户描述中自动提取：
- **核心功能点**：登录、注册、邮箱验证...
- **目标用户**：普通用户、管理员...
- **业务价值**：提高安全性、改善用户体验...
- **关键约束**：密码加密、Token 有效期...

**步骤 B：自动生成用户故事**

根据提取的信息，生成 User Story 格式：

```markdown
### US-001: 用户登录
**作为** 注册用户
**我想要** 使用邮箱和密码登录系统
**以便于** 访问我的个人数据和功能

**验收标准**：
- [ ] 支持邮箱+密码登录
- [ ] 登录失败显示错误提示
- [ ] 登录成功跳转到首页
```

**步骤 C：自动定义功能边界**

```markdown
### 包含（In Scope）
- 邮箱密码登录
- 用户注册
- 邮箱验证

### 不包含（Out of Scope）
- 第三方登录（OAuth）
- 多因素认证（MFA）
```

**步骤 D：自动识别约束条件**

```markdown
### 技术约束
- 密码必须加密存储（bcrypt）
- Token 有效期 24 小时

### 业务约束
- 邮箱必须唯一
- 密码至少 8 位
```

#### 3.2 模板模式（用户未提供描述）

如果用户只提供了功能名称，则使用以下模板生成 `10_CONTEXT.md`：

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

- 工作流文档：`CC_COLLABORATION/01_workflow/README.md`
- 进度日志：`docs/{feature-name}/90_PROGRESS_LOG.yaml`
- Gate 状态：`docs/{feature-name}/PHASE_GATE_STATUS.yaml`

---

## CHANGELOG

| 版本 | 日期 | 作者 | 变更内容 |
|------|------|------|----------|
| v0.1 | {current_date} | {作者} | 初始版本 |
```

### 4. 生成 DOC_CHANGELOG.md

使用下方内置模板生成文档变更日志（没有独立的 DOC_CHANGELOG 模板文件）：

```markdown
# 文档变更日志

> 功能模块：{feature-name}
> 创建时间：{current_datetime}

---

本文件记录该功能模块下所有文档的修改历史。文档本身只保留最新版本，历史变更记录于此。

## 变更记录

### {current_datetime} - Phase 1 初始化

| 文档 | 操作 | 说明 |
|------|------|------|
| `10_CONTEXT.md` | 创建 | 功能上下文初始化 |
| `90_PROGRESS_LOG.yaml` | 创建 | 进度日志初始化 |
| `PHASE_GATE.yaml` | 创建 | Phase Gate 规则配置初始化 |
| `PHASE_GATE_STATUS.yaml` | 创建 | Phase Gate 运行状态初始化 |
| `DOC_CHANGELOG.md` | 创建 | 文档变更日志初始化 |

---

<!--
变更记录格式：

### YYYY-MM-DD HH:MM - {变更标题}

| 文档 | 操作 | 说明 |
|------|------|------|
| `{文件名}` | 创建/修改/删除 | {变更说明} |

操作类型：
- 创建：新建文档
- 修改：更新现有文档内容
- 重构：文档结构调整
- 删除：移除文档

变更说明应简要描述：
- 修改了什么章节
- 为什么修改
- 主要变化点
-->
```

### 5. 生成 90_PROGRESS_LOG.yaml

从模板 `CC_COLLABORATION/03_templates/_shared/90_PROGRESS_LOG_TEMPLATE.yaml` 生成，并替换占位符。

生成后的文件结构示例：

```yaml
# 90_PROGRESS_LOG.yaml
# 功能模块：{Feature Name}
# 最后更新：{current_datetime}

meta:
  feature: "{feature-name}"
  feature_name: "{Feature Name}"
  current_phase: 1
  status: wip
  owner: "@{请补充}"
  started_at: "{current_date}"
  last_updated: "{current_datetime}"
  target_date: "{target_date}"

# Phase 1-7 各阶段任务（完整结构见模板）
phase_1_kickoff:
  status: wip
  start_date: "{current_date}"
  end_date: null
  completion_pct: 50
  tasks:
    - id: "{PREFIX}-KICK-001"
      task: "创建功能目录 docs/{feature-name}/"
      status: done
      priority: P0
      completed_at: "{current_date}"

    - id: "{PREFIX}-KICK-002"
      task: "编写 10_CONTEXT.md 功能背景文档"
      status: wip
      priority: P0
      verification: "包含功能概述、边界定义、用户故事、约束条件"
      completed_at: null

# Phase 2-7 使用模板默认值（pending 状态）
# ...

# Claude Code 断点恢复信息
cc_checkpoint:
  session_id: "cc-{current_date}-{feature-name}"
  last_file_edited: "docs/{feature-name}/10_CONTEXT.md"
  last_action: "创建功能目录和初始文档"
  next_step: "补充 10_CONTEXT.md 中的功能描述和目标"
  context_files:
    - "docs/{feature-name}/10_CONTEXT.md"
    - "docs/{feature-name}/90_PROGRESS_LOG.yaml"
  implementation_summary: []

# 统计信息（由工具自动更新）
stats:
  by_phase:
    phase_1_kickoff:
      total: 2
      done: 1
      pending: 1
      status: "wip"
    # ... 其他阶段
  summary:
    total_tasks: 12
    done: 1
    wip: 1
    pending: 10
    blocked: 0
    completion_rate: "8%"
  next_milestone: "完成 Phase 1 Kickoff"
```

**注意**：实际生成时应使用完整模板，包含 Phase 1-7 所有阶段的任务定义。

### 6. 生成 Phase Gate 文件

从模板生成 Phase Gate 配置和状态文件：

**6.1 生成 PHASE_GATE.yaml**

从 `CC_COLLABORATION/03_templates/_shared/PHASE_GATE_TEMPLATE.yaml` 复制模板，并替换占位符：
- `{feature-name}` → 功能名称
- `{date}` → 当前日期

此文件定义该功能的 Phase 1-7 Gate 规则（必需产出物、质量检查、审批角色）。

**6.2 生成 PHASE_GATE_STATUS.yaml**

从 `CC_COLLABORATION/03_templates/_shared/PHASE_GATE_STATUS_TEMPLATE.yaml` 复制模板，并替换占位符：
- `{feature-name}` → 功能名称
- `{datetime}` → 当前时间戳

此文件记录该功能的 Phase 1-7 Gate 运行状态（gate_state、approvals、check_history）。

### 7. 追加项目活动日志（如果存在）

如果存在 `docs/_foundation/PROJECT_ACTIVITY_LOG.yaml`，追加活动记录：

```yaml
追加活动：
  timestamp: current_datetime
  type: "feature_created"
  feature: "{feature-name}"
  description: "创建 {feature-name} 功能模块"
  by: "@human"
  details:
    command: "/new-feature {feature-name}"
    initial_phase: 1
```

### 8. 输出结果

创建完成后，输出以下信息：

```
✅ 功能模块 "{feature-name}" 创建成功！

📁 目录结构：
docs/{feature-name}/
├── 10_CONTEXT.md              # 功能上下文
├── 90_PROGRESS_LOG.yaml       # 进度日志
├── PHASE_GATE.yaml            # Phase Gate 规则配置
├── PHASE_GATE_STATUS.yaml     # Phase Gate 运行状态
├── DOC_CHANGELOG.md           # 文档变更日志
└── _demos/                    # Demo 文件目录

📝 下一步操作：
1. 补充 10_CONTEXT.md 中的功能描述、目标和范围
2. 与团队确认功能上下文后，将状态改为 Approved
3. 执行 /check-gate {feature-name} --phase=1 检查 Kickoff Gate
4. 进入 Spec 阶段，编写 20_API_SPEC.md 或 21_UI_FLOW_SPEC.md

💡 提示：
- 使用 /check-progress {feature-name} 查看进度
- 使用 /check-gate {feature-name} 查看 Gate 状态
- 使用 /iresume {feature-name} 恢复工作上下文
```

## 注意事项

- 功能名称使用 kebab-case（如 `user-auth`，不是 `userAuth`）
- 自动生成的文档是框架，需要人工补充内容
- 10_CONTEXT.md 状态默认为 Draft，确认后改为 Approved
