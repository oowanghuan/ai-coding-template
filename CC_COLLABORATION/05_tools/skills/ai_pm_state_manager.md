# ai_pm_state_manager - AI PM Driver 状态管理器

## 能力描述

管理 AI PM Driver 的状态文件 `AI_PM_ORCHESTRATION_STATE.yaml`，提供读取、写入、验证等操作。

**核心职责**：
- 读取状态文件
- 写入状态更新（带备份）
- 验证状态一致性
- 状态恢复

**设计原则**：
- **禁止存储执行事实**：状态文件不存储 current_phase / step_status / completed / gate_result
- **控制态分离**：只存储 intent / policy / runtime 控制态
- **备份优先**：每次写入前自动备份

## 输入

### 读取操作

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| action | string | 是 | 固定为 `read` |
| feature | string | 是 | 功能模块名称 |

### 写入操作

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| action | string | 是 | 固定为 `write` |
| feature | string | 是 | 功能模块名称 |
| updates | object | 是 | 要更新的字段（深度合并） |

### 验证操作

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| action | string | 是 | 固定为 `validate` |
| feature | string | 是 | 功能模块名称 |

### 恢复操作

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| action | string | 是 | 固定为 `restore` |
| feature | string | 是 | 功能模块名称 |
| backup_index | number | 否 | 备份索引（默认最新） |

## 输出

### 读取结果

```yaml
read_result:
  success: true | false
  state: { ... }  # 完整状态对象
  exists: true | false
  error: null | "错误信息"
```

### 写入结果

```yaml
write_result:
  success: true | false
  backup_path: "docs/{feature}/.ai_pm_backups/{timestamp}.yaml"
  error: null | "错误信息"
```

### 验证结果

```yaml
validate_result:
  success: true | false
  valid: true | false
  issues:
    - field: "runtime.current_phase"
      type: "forbidden_field"
      message: "禁止存储执行事实字段"
    - field: "runtime.status"
      type: "invalid_value"
      message: "无效的状态值"
  consistency:
    phase_gate_sync: true | false
    progress_sync: true | false
```

## 执行步骤

### 1. 读取操作 (action = "read")

```python
def read_state(feature):
    state_file = f"docs/{feature}/AI_PM_ORCHESTRATION_STATE.yaml"

    if not exists(state_file):
        return {
            "success": True,
            "state": None,
            "exists": False,
            "error": None
        }

    try:
        state = load_yaml(state_file)
        return {
            "success": True,
            "state": state,
            "exists": True,
            "error": None
        }
    except Exception as e:
        return {
            "success": False,
            "state": None,
            "exists": True,
            "error": str(e)
        }
```

### 2. 写入操作 (action = "write")

```python
def write_state(feature, updates):
    state_file = f"docs/{feature}/AI_PM_ORCHESTRATION_STATE.yaml"
    backup_dir = f"docs/{feature}/.ai_pm_backups"

    # 1. 验证更新不包含禁止字段
    forbidden_fields = ["current_phase", "step_status", "completed", "gate_result"]
    for field in forbidden_fields:
        if field_exists_in_updates(updates, field):
            return {
                "success": False,
                "error": f"禁止写入字段: {field}"
            }

    # 2. 读取现有状态
    if exists(state_file):
        existing_state = load_yaml(state_file)

        # 3. 创建备份
        ensure_dir(backup_dir)
        backup_path = f"{backup_dir}/{current_timestamp}.yaml"
        save_yaml(existing_state, backup_path)

        # 4. 清理旧备份（保留最近 10 个）
        cleanup_old_backups(backup_dir, keep=10)

        # 5. 深度合并更新
        new_state = deep_merge(existing_state, updates)
    else:
        # 首次创建，updates 就是完整状态
        new_state = updates
        backup_path = None

    # 6. 保存新状态
    save_yaml(new_state, state_file)

    return {
        "success": True,
        "backup_path": backup_path,
        "error": None
    }
```

### 3. 验证操作 (action = "validate")

```python
def validate_state(feature):
    state_file = f"docs/{feature}/AI_PM_ORCHESTRATION_STATE.yaml"
    issues = []

    if not exists(state_file):
        return {
            "success": True,
            "valid": True,
            "issues": [],
            "consistency": {}
        }

    state = load_yaml(state_file)

    # 1. 检查禁止字段
    forbidden_fields = ["current_phase", "step_status", "completed", "gate_result"]
    for field in forbidden_fields:
        if field_exists_in_state(state, field):
            issues.append({
                "field": field,
                "type": "forbidden_field",
                "message": f"禁止存储执行事实字段: {field}"
            })

    # 2. 检查必需字段
    required_fields = [
        "meta.feature",
        "intent.mode",
        "runtime.status"
    ]
    for field in required_fields:
        if not field_exists_in_state(state, field):
            issues.append({
                "field": field,
                "type": "missing_field",
                "message": f"缺少必需字段: {field}"
            })

    # 3. 检查枚举值
    valid_statuses = ["idle", "running", "waiting_human", "stuck", "paused", "completed", "failed"]
    if state.get("runtime", {}).get("status") not in valid_statuses:
        issues.append({
            "field": "runtime.status",
            "type": "invalid_value",
            "message": f"无效的状态值: {state['runtime']['status']}"
        })

    valid_modes = ["full_auto", "human_confirm"]
    if state.get("intent", {}).get("mode") not in valid_modes:
        issues.append({
            "field": "intent.mode",
            "type": "invalid_value",
            "message": f"无效的模式: {state['intent']['mode']}"
        })

    # 4. 检查状态一致性
    consistency = check_consistency(feature, state)

    return {
        "success": True,
        "valid": len(issues) == 0,
        "issues": issues,
        "consistency": consistency
    }

def check_consistency(feature, state):
    """检查 Driver 状态与下游文件的一致性"""
    gate_status = load_yaml(f"docs/{feature}/PHASE_GATE_STATUS.yaml")
    progress_log = load_yaml(f"docs/{feature}/90_PROGRESS_LOG.yaml")

    result = {
        "phase_gate_sync": True,
        "progress_sync": True
    }

    # 检查 phase_events 与 PHASE_GATE_STATUS 是否一致
    for event in state.get("counters", {}).get("phase_events", []):
        phase = event["phase"]
        phase_key = f"phase_{phase}_*"
        # 如果 event 记录 gate_passed，检查 gate_status 是否确实 passed
        if event["event"] == "gate_passed":
            if gate_status.get(phase_key, {}).get("gate_state") != "passed":
                result["phase_gate_sync"] = False
                break

    return result
```

### 4. 恢复操作 (action = "restore")

```python
def restore_state(feature, backup_index=0):
    backup_dir = f"docs/{feature}/.ai_pm_backups"
    state_file = f"docs/{feature}/AI_PM_ORCHESTRATION_STATE.yaml"

    if not exists(backup_dir):
        return {
            "success": False,
            "error": "没有可用的备份"
        }

    # 获取备份列表（按时间倒序）
    backups = sorted(list_files(backup_dir), reverse=True)

    if backup_index >= len(backups):
        return {
            "success": False,
            "error": f"备份索引超出范围: {backup_index} >= {len(backups)}"
        }

    backup_path = backups[backup_index]
    backup_state = load_yaml(backup_path)

    # 恢复
    save_yaml(backup_state, state_file)

    return {
        "success": True,
        "restored_from": backup_path,
        "error": None
    }
```

## 状态 Schema

```yaml
# AI_PM_ORCHESTRATION_STATE.yaml
# 完整 Schema 定义

meta:
  feature: string           # 功能名称
  schema_version: "1.1"     # Schema 版本
  created_at: datetime      # 创建时间
  created_by: string        # 创建者

intent:
  mode: enum                # "full_auto" | "human_confirm"
  start_phase: number       # 起始阶段
  target_phase: number      # 目标阶段
  allow_auto_fix: boolean   # 允许自动修复
  allow_skip: boolean       # 允许跳过阶段

policy:
  auto_fix:
    max_attempts_per_issue: number
    max_attempts_per_phase: number
    max_total_attempts: number
  api_retry:
    max_retries: number
    retry_delay_seconds: number
  circuit_breaker:
    stuck_timeout_minutes: number
    total_timeout_minutes: number
    no_progress_threshold: number
  expert_review:
    enabled: boolean
    threshold: number
    required_phases: number[]
  notification:
    on_phase_complete: boolean
    on_stuck: boolean
    on_error: boolean

runtime:
  status: enum              # "idle" | "running" | "waiting_human" | "stuck" | "paused" | "completed" | "failed"
  last_action: string       # 最后执行的动作
  last_decision: enum       # "continue" | "retry" | "ask_human" | "abort"
  last_decision_reason: string
  last_decision_at: datetime
  human_context: object | null
  stuck_context: object | null

counters:
  total_fix_attempts: number
  current_phase_fix_attempts: number
  per_issue_fix_attempts: object
  consecutive_no_progress: number
  api_retry_count: number
  phase_events: array

timeline:
  started_at: datetime
  last_progress_at: datetime
```

## 禁止字段清单

以下字段**禁止**出现在状态文件中：

| 字段 | 原因 | 正确获取方式 |
|------|------|-------------|
| `current_phase` | 执行事实 | 从 90_PROGRESS_LOG.yaml 实时查询 |
| `step_status` | 执行事实 | 从 90_PROGRESS_LOG.yaml 实时查询 |
| `completed` | 执行事实 | 从 PHASE_GATE_STATUS.yaml 实时查询 |
| `gate_result` | 执行事实 | 从 PHASE_GATE_STATUS.yaml 实时查询 |

## 备份策略

```yaml
backup_policy:
  trigger: "before_each_write"
  location: "docs/{feature}/.ai_pm_backups/"
  naming: "{timestamp}.yaml"  # 如 20260110_143000.yaml
  retention: 10               # 保留最近 10 个版本
  cleanup: "automatic"        # 写入时自动清理旧备份
```

## 使用示例

### 示例 1：读取状态

```yaml
# 输入
action: read
feature: ai-pm-driver

# 输出
read_result:
  success: true
  exists: true
  state:
    meta:
      feature: "ai-pm-driver"
      ...
    runtime:
      status: "running"
      ...
```

### 示例 2：更新运行时状态

```yaml
# 输入
action: write
feature: ai-pm-driver
updates:
  runtime:
    status: "waiting_human"
    human_context:
      waiting_since: "2026-01-10T14:30:00+08:00"
      waiting_for: "confirm_phase_transition"
      summary: "Phase 4 Gate 通过，等待确认"

# 输出
write_result:
  success: true
  backup_path: "docs/ai-pm-driver/.ai_pm_backups/20260110_143000.yaml"
```

### 示例 3：验证状态

```yaml
# 输入
action: validate
feature: ai-pm-driver

# 输出
validate_result:
  success: true
  valid: true
  issues: []
  consistency:
    phase_gate_sync: true
    progress_sync: true
```

### 示例 4：从备份恢复

```yaml
# 输入
action: restore
feature: ai-pm-driver
backup_index: 0  # 最新备份

# 输出
restore_result:
  success: true
  restored_from: "docs/ai-pm-driver/.ai_pm_backups/20260110_140000.yaml"
```

## 注意事项

1. **写入前验证**：每次写入都会验证不包含禁止字段
2. **自动备份**：每次写入前自动创建备份
3. **深度合并**：updates 使用深度合并，不会覆盖未指定的字段
4. **一致性检查**：validate 操作会检查与下游文件的一致性
5. **幂等读取**：read 操作是幂等的，不会修改任何文件

## 关联工具

- `/ai-pm` - 使用此 skill 管理状态
- `gate_checker` - 读取 Gate 状态
- `progress_updater` - 更新进度信息
