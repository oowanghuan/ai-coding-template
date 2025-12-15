# 02_YAML_SCHEMA_CONVENTIONS.md
# YAML Schema 设计规范

> 版本：v1.0
> 最后更新：{timestamp}
> 适用范围：所有 YAML 配置文件和数据契约

---

## 1. 概述

本文档定义项目中所有 YAML 文件的设计规范，确保：
- 文件结构一致性
- 字段命名标准化
- Schema 可验证
- 便于 Claude Code 理解和生成

---

## 2. 文件类型分类

### 2.1 配置文件（Configuration）

```yaml
# 特征：定义系统行为，较少变更
# 示例：PHASE_GATE.yaml, feature_profile.yaml

# 命名规范
文件名: UPPER_SNAKE_CASE.yaml
用途: 定义规则、配置、模板
```

### 2.2 状态文件（State/Status）

```yaml
# 特征：记录运行时状态，频繁变更
# 示例：PHASE_GATE_STATUS.yaml, 30_PROGRESS_LOG.yaml

# 命名规范
文件名: UPPER_SNAKE_CASE_STATUS.yaml 或 NN_SNAKE_CASE.yaml
用途: 记录当前状态、历史、检查结果
```

### 2.3 输出文件（Output/Report）

```yaml
# 特征：由工具生成，记录结果
# 示例：REVIEW_ACTIONS.yaml

# 命名规范
文件名: ACTION_TYPE.yaml
用途: 工具输出、评审结果、执行报告
```

---

## 3. 字段命名规范

### 3.1 命名风格

```yaml
# 使用 snake_case（全小写 + 下划线）
user_id: 123
created_at: "2024-12-15T10:00:00Z"
is_active: true

# 避免
userId: 123          # 不要用驼峰
user-id: 123         # 不要用连字符
USER_ID: 123         # 不要用全大写（除非是常量）
```

### 3.2 布尔字段

```yaml
# 使用 is_、has_、can_、should_ 前缀
is_enabled: true
is_required: false
has_permission: true
can_override: false
should_notify: true
```

### 3.3 日期时间字段

```yaml
# 使用 _at 后缀，ISO 8601 格式
created_at: "2024-12-15T10:00:00Z"
updated_at: "2024-12-15T10:30:00+08:00"
started_at: "2024-12-15"
completed_at: null  # 未完成时为 null

# 使用 _date 后缀表示仅日期
start_date: "2024-12-15"
end_date: "2024-12-20"
```

### 3.4 枚举字段

```yaml
# 使用小写 + 下划线
status: pending        # pending | in_progress | done | blocked
severity: block        # block | warn | info
gate_state: passed     # pending | passed | blocked | skipped
```

### 3.5 ID 字段

```yaml
# 主键
id: "ER-001"

# 外键/引用
feature_id: "expert-reviewer"
phase_id: 2
user_id: "@huan"

# 复合 ID
session_id: "cc-2024-12-15-expert-reviewer"
```

---

## 4. 文件结构规范

### 4.1 标准头部

```yaml
# {文件名}
# {一句话描述}
# 功能模块：{feature-name}
# 版本：{version}

# ============================================================
# 元信息
# ============================================================
meta:
  feature: "feature-name"
  version: "1.0"
  last_updated: "2024-12-15T10:00:00Z"
```

### 4.2 章节分隔

```yaml
# ============================================================
# 章节名称
# ============================================================
section_name:
  field1: value1
  field2: value2
```

### 4.3 注释规范

```yaml
# 章节注释（在章节分隔线下方）
# ============================================================
# Phase 1: Kickoff Gate - 配置
# ============================================================

# 字段注释（在字段上方）
# 当前阶段 (1-7)
current_phase: 2

# 行内注释（简短说明）
status: wip  # done | wip | blocked | pending
```

---

## 5. 常用 Schema 模式

### 5.1 元信息块（Meta Block）

```yaml
meta:
  feature: string           # 功能 ID
  feature_name: string      # 功能显示名称
  version: string           # 版本号
  created_at: datetime      # 创建时间
  last_updated: datetime    # 最后更新时间
  owner: string             # 负责人
```

### 5.2 状态块（Status Block）

```yaml
status_block:
  status: enum              # pending | in_progress | done | blocked | skipped
  start_date: date          # 开始日期
  end_date: date | null     # 结束日期
  completion_pct: integer   # 完成百分比 0-100
```

### 5.3 任务列表（Task List）

```yaml
tasks:
  - id: string              # 任务 ID，如 "ER-001"
    task: string            # 任务描述
    status: enum            # pending | in_progress | done | blocked | skipped
    priority: enum          # P0 | P1 | P2
    owner: string           # 负责人（可选）
    verification: string    # 验证条件（可选）
    completed_at: datetime  # 完成时间（可选）
    notes: string           # 备注（可选）
```

### 5.4 审批记录（Approval Record）

```yaml
approvals:
  - role: enum              # PM | Architect | Developer | QA
    user: string            # 用户标识
    approved_at: datetime   # 审批时间
    comment: string         # 审批意见（可选）
```

### 5.5 检查结果（Check Result）

```yaml
check_results:
  - id: string              # 检查项 ID
    status: enum            # passed | failed | skipped | not_applicable
    details: string         # 详细信息
    evidence: string        # 证据（可选）
```

### 5.6 历史记录（History Log）

```yaml
history:
  - timestamp: datetime     # 事件时间
    action: string          # 动作描述
    actor: string           # 执行者
    result: string          # 结果
    details: object         # 详细信息（可选）
```

---

## 6. 数据类型定义

### 6.1 基础类型

| 类型 | YAML 表示 | 示例 |
|------|-----------|------|
| string | 字符串 | `"hello"` 或 `hello` |
| integer | 整数 | `42` |
| float | 浮点数 | `3.14` |
| boolean | 布尔值 | `true` / `false` |
| null | 空值 | `null` 或 `~` |

### 6.2 复合类型

| 类型 | YAML 表示 | 示例 |
|------|-----------|------|
| date | ISO 日期 | `"2024-12-15"` |
| datetime | ISO 时间 | `"2024-12-15T10:00:00Z"` |
| enum | 枚举值 | `pending` \| `done` |
| array | 列表 | `[a, b, c]` 或多行 `- item` |
| object | 映射 | `key: value` |

### 6.3 可空字段

```yaml
# 可空字段使用 null 或不存在
end_date: null           # 显式 null
# 或省略字段

# 不要使用空字符串表示空值
end_date: ""             # 错误：应该用 null
```

---

## 7. 版本控制

### 7.1 Schema 版本

```yaml
meta:
  schema_version: "1.0"    # Schema 版本

# 版本升级规则
# 1.0 → 1.1：向后兼容的新增字段
# 1.x → 2.0：破坏性变更
```

### 7.2 向后兼容规则

**兼容变更**（小版本）：
- 添加新的可选字段
- 添加新的枚举值
- 放宽字段验证

**破坏性变更**（大版本）：
- 删除或重命名字段
- 改变字段类型
- 改变必填/可选状态
- 移除枚举值

---

## 8. 验证规范

### 8.1 必填字段

```yaml
# 在 Schema 中标注必填
# required: true

meta:
  feature: string         # required
  last_updated: datetime  # required
  version: string         # optional, default: "1.0"
```

### 8.2 字段约束

```yaml
# 数值范围
completion_pct:
  type: integer
  minimum: 0
  maximum: 100

# 字符串格式
email:
  type: string
  format: email

# 枚举限制
status:
  type: string
  enum: [pending, in_progress, done, blocked]
```

---

## 9. 工具生成规范

### 9.1 自动生成标记

```yaml
# ============================================================
# 统计信息（由工具自动更新）
# ============================================================
stats:
  # AUTO-GENERATED: Do not edit manually
  total_tasks: 15
  done: 3
  pending: 12
```

### 9.2 人工编辑区域

```yaml
# ============================================================
# 任务列表（人工维护）
# ============================================================
tasks:
  # MANUAL: Edit tasks below as needed
  - id: "TASK-001"
    task: "实现功能 A"
```

---

## 10. Claude Code 使用指南

### 10.1 生成 YAML 时的检查清单

- [ ] 文件头是否包含必要注释
- [ ] meta 块是否完整
- [ ] 字段名是否使用 snake_case
- [ ] 日期时间是否使用 ISO 8601
- [ ] 枚举值是否使用小写
- [ ] 可空字段是否使用 null

### 10.2 读取 YAML 时的检查清单

- [ ] 验证 meta.schema_version 兼容性
- [ ] 检查必填字段是否存在
- [ ] 处理 null 值
- [ ] 处理缺失的可选字段

---

## 附录：常用 Schema 示例

### A. 进度日志 Schema

```yaml
meta:
  feature: string
  current_phase: integer    # 1-7
  status: enum              # done | wip | blocked | pending

phase_N_name:
  status: enum
  start_date: date
  end_date: date | null
  completion_pct: integer
  tasks: TaskList[]

stats:
  total_tasks: integer
  done: integer
  pending: integer
```

### B. Gate 状态 Schema

```yaml
meta:
  feature: string
  last_updated: datetime

phase_N_name:
  gate_state: enum          # pending | passed | blocked | skipped
  gate_state_meta:
    last_updated_at: datetime
    last_updated_by_command: string
  approvals: ApprovalRecord[]
  last_check:
    checked_at: datetime
    check_results: CheckResult[]
  check_history: HistoryLog[]
```

### C. 评审结果 Schema

```yaml
meta:
  feature: string
  phase: integer
  reviewed_at: datetime
  reviewer: string

verdict: enum               # GO | REVISE | BLOCK
summary:
  total_issues: integer
  block_count: integer
  warn_count: integer

actions:
  - id: string
    severity: enum          # block | warn
    issue: string
    fix: string
    owner_role: enum
```

---

## 模板使用说明

1. 复制此文件到 `docs/_foundation/_api_system/02_YAML_SCHEMA_CONVENTIONS.md`
2. 替换 `{timestamp}` 为当前日期
3. 根据项目实际情况调整 Schema 示例
4. 删除此"模板使用说明"段落
