# progress_updater - 更新 PROGRESS_LOG

## 能力描述

自动更新功能模块的 `90_PROGRESS_LOG.yaml` 文件，包括：
- 更新任务状态（pending → wip → done）
- 更新 cc_checkpoint 断点信息
- 更新统计信息
- 维护时间戳

## 输入

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| feature | string | 是 | 功能模块名称 |
| action | string | 是 | 操作类型：`update_task`, `update_checkpoint`, `update_stats` |
| task_id | string | 否 | 任务 ID（action=update_task 时必需） |
| new_status | string | 否 | 新状态：`pending`, `wip`, `done`（action=update_task 时必需） |
| checkpoint_data | object | 否 | 断点数据（action=update_checkpoint 时使用） |

## 输出

- 更新后的 `90_PROGRESS_LOG.yaml` 文件
- 变更摘要

## 执行步骤

### 1. 读取 PROGRESS_LOG

```yaml
# 读取 docs/{feature}/90_PROGRESS_LOG.yaml
```

### 2. 根据 action 执行操作

#### action = update_task

```yaml
# 找到对应的 task_id
# 更新 status 字段
# 如果 new_status = done，添加 completed_at 时间戳
# 如果 new_status = wip，确保只有一个任务是 wip
```

#### action = update_checkpoint

```yaml
# 更新 cc_checkpoint 部分
cc_checkpoint:
  session_id: "{new_session_id}"
  last_file_edited: "{last_file}"
  last_action: "{action_description}"
  next_step: "{next_step}"
  context_files:
    - "{file_1}"
    - "{file_2}"
```

#### action = update_stats

```yaml
# 重新计算统计信息
stats:
  total_tasks: {count_all_tasks}
  done: {count_done}
  wip: {count_wip}
  pending: {count_pending}
  completion_rate: "{percentage}%"
```

### 3. 更新时间戳

```yaml
meta:
  last_updated: "{current_datetime}"
```

### 4. 写回文件

保存更新后的 YAML 文件。

### 5. 输出变更摘要

```
✓ 更新 PROGRESS_LOG

变更内容：
• 任务 {task_id}: {old_status} → {new_status}
• 完成率: {old_rate}% → {new_rate}%
• 更新时间: {current_datetime}
```

## 示例

### 示例 1：更新任务状态

**输入**：
```
请使用 progress_updater skill：
- feature: user-auth
- action: update_task
- task_id: CODE-003
- new_status: done
```

**输出**：
```
✓ 更新 PROGRESS_LOG

变更内容：
• 任务 CODE-003: wip → done
• 完成率: 50% → 60%
• 更新时间: 2024-12-11T15:30:00+08:00

下一步建议：
继续处理 CODE-004: 实现密码验证逻辑
```

### 示例 2：更新断点信息

**输入**：
```
请使用 progress_updater skill：
- feature: user-auth
- action: update_checkpoint
- checkpoint_data:
    session_id: cc-2024-12-11-002
    last_file_edited: src/auth/login.vue
    last_action: 完成登录表单 UI
    next_step: 实现登录 API 调用
```

**输出**：
```
✓ 更新断点信息

Session: cc-2024-12-11-002
最后编辑: src/auth/login.vue
下一步: 实现登录 API 调用
```

## 注意事项

1. **YAML 格式**：确保输出的 YAML 格式正确，缩进为 2 空格
2. **时间戳格式**：使用 ISO 8601 格式，带时区（如 `2024-12-11T15:30:00+08:00`）
3. **任务状态互斥**：同一时间只能有一个任务处于 `wip` 状态
4. **统计同步**：更新任务状态后自动同步统计信息
5. **备份**：在修改前建议保留原文件内容以便回滚

## 关联工具

- `/check-progress` - 调用此 skill 显示进度
- `/daily-summary` - 读取此 skill 更新的数据
- `/iresume` - 依赖 cc_checkpoint 数据
