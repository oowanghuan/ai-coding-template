# /project-pm - 项目级 PM Driver 编排命令

你是一个 AI 协作开发助手。Project PM Driver 是项目级编排层工具，用于协调多个 Feature 的并行开发。

## 核心原则

**Project PM Driver 是项目级协调者（Mayor），Feature AI PM (`/ai-pm`) 是执行者（Polecat）。**

- Project PM 负责 Ready Set 计算、任务分配、进度汇总
- Feature AI PM 负责单个 feature 的 Phase 1-7 执行
- Human 作为命令分发者，将 assign 生成的命令分发给各 Dev Agent

## 参数

- `$ARGUMENTS`：子命令和参数

## 子命令总览

| 子命令 | 说明 | 前置条件 |
|--------|------|----------|
| `init` | 初始化 PROJECT_TRACKER | Foundation Gate passed |
| `status` | 查看项目整体状态 | PROJECT_TRACKER 存在 |
| `ready` | 获取 Ready Set | PROJECT_TRACKER 存在 |
| `assign` | 生成 dev agent 命令 | Ready Set 非空 |
| `check` | 检查并更新进度 | PROJECT_TRACKER 存在 |
| `sync` | 同步 ROADMAP 变更 | PROJECT_TRACKER 存在 |
| `logs` | 查看项目活动日志 | PROJECT_ACTIVITY_LOG 存在 |

---

## 执行步骤

### 1. 解析参数

```
解析 $ARGUMENTS：
  - 第一个词为子命令（init, status, ready, assign, check, sync）
  - 后续为选项参数

如果 $ARGUMENTS 为空，默认执行 status 子命令

有效子命令：
  - init
  - status
  - ready
  - assign [--max=N]
  - check
  - sync
  - logs [--tail=N] [--type=TYPE]
```

### 2. 定位项目文件

```yaml
paths:
  # 数据文件（运行时）
  foundation_dir: "docs/_foundation"
  planning_dir: "docs/_foundation/_planning"
  module_decomposition: "docs/_foundation/_planning/03_MODULE_DECOMPOSITION.md"
  roadmap: "docs/_foundation/_planning/04_ROADMAP.md"
  foundation_gate_status: "docs/_foundation/FOUNDATION_GATE_STATUS.yaml"
  project_tracker: "docs/_foundation/PROJECT_TRACKER.yaml"
  project_pm_state: "docs/_foundation/PROJECT_PM_STATE.yaml"
  project_activity_log: "docs/_foundation/PROJECT_ACTIVITY_LOG.yaml"

  # 模板文件（初始化时使用）
  templates:
    project_tracker: "CC_COLLABORATION/03_templates/00_foundation/PROJECT_TRACKER_TEMPLATE.yaml"
    project_pm_state: "CC_COLLABORATION/03_templates/00_foundation/PROJECT_PM_STATE_TEMPLATE.yaml"
    project_activity_log: "CC_COLLABORATION/03_templates/00_foundation/PROJECT_ACTIVITY_LOG_TEMPLATE.yaml"
```

---

## 子命令详细规格

### `/project-pm init`

**功能**：从 MODULE_DECOMPOSITION 和 ROADMAP 初始化 PROJECT_TRACKER

**前置条件**：
- Foundation Gate (Phase 0) 已通过
- `03_MODULE_DECOMPOSITION.md` 已填写 feature 列表
- `04_ROADMAP.md` 已定义里程碑

**执行逻辑**：

```yaml
步骤:
  1_check_foundation_gate:
    read: "docs/_foundation/FOUNDATION_GATE_STATUS.yaml"
    validate:
      - field: "summary.gate_state"
        expected: "passed"
    on_fail: |
      ❌ Foundation Gate 未通过

      请先完成 Foundation 文档并通过 Gate 检查：
      1. 填写 docs/_foundation/_planning/ 下的规划文档
      2. 执行 /check-gate --phase=0
      3. 执行 /approve-gate --phase=0 --role=PM
      4. 执行 /approve-gate --phase=0 --role=Architect

  2_check_existing:
    check: "docs/_foundation/PROJECT_TRACKER.yaml 是否存在"
    if_exists: |
      ⚠️ PROJECT_TRACKER 已存在

      已存在的跟踪文件：
        • docs/_foundation/PROJECT_TRACKER.yaml
        • docs/_foundation/PROJECT_PM_STATE.yaml
        • docs/_foundation/PROJECT_ACTIVITY_LOG.yaml

      是否要重新初始化？这将覆盖现有数据。[y/N]

  3_parse_module_decomposition:
    read: "docs/_foundation/_planning/03_MODULE_DECOMPOSITION.md"
    parse:
      - format: "markdown_table"
        fields: [module_id, feature_name, milestone, priority, blocked_by, description]
      - format: "yaml_block"
        fallback: true
    extract: "features 列表"

  4_parse_roadmap:
    read: "docs/_foundation/_planning/04_ROADMAP.md"
    extract: "milestones 定义"

  5_detect_cycles:
    algorithm: "DFS 循环依赖检测"
    on_cycle: |
      ❌ 检测到循环依赖，无法初始化

      以下 feature 之间存在循环依赖：
      {列出循环路径}

      请修改 03_MODULE_DECOMPOSITION.md 解除循环依赖后重试。

  6_validate_feature_directories:
    for_each: feature in features
    check: "docs/{feature}/ 目录是否存在"
    status_if_missing: "pending"
    warn_missing: true

  7_build_tracker:
    construct: PROJECT_TRACKER.yaml
    fields:
      - meta (project, schema_version, timestamps)
      - milestones (从 ROADMAP)
      - features (从 MODULE_DECOMPOSITION)
      - ready_set (计算)
      - stats (统计)

  8_build_state:
    construct: PROJECT_PM_STATE.yaml
    fields:
      - meta
      - intent (默认 human_confirm 模式)
      - policy
      - runtime (idle)
      - counters
      - timeline

  9_build_activity_log:
    construct: PROJECT_ACTIVITY_LOG.yaml
    initial_entry:
      - timestamp: current_datetime
        type: "project_initialized"
        description: "项目跟踪系统初始化"
        by: "@human"
        details:
          command: "/project-pm init"
          features_count: features.length

  10_save:
    write:
      - "docs/_foundation/PROJECT_TRACKER.yaml"
      - "docs/_foundation/PROJECT_PM_STATE.yaml"
      - "docs/_foundation/PROJECT_ACTIVITY_LOG.yaml"
```

**输出**：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 Project PM 初始化
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

从以下文档读取配置：
  • docs/_foundation/_planning/03_MODULE_DECOMPOSITION.md
  • docs/_foundation/_planning/04_ROADMAP.md

已创建：
  ✅ docs/_foundation/PROJECT_TRACKER.yaml
  ✅ docs/_foundation/PROJECT_PM_STATE.yaml
  ✅ docs/_foundation/PROJECT_ACTIVITY_LOG.yaml

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 检测到的功能模块
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

里程碑 M1 ({milestone_name}):
  • {feature} (priority: {N})
  • {feature} (priority: {N}, blocked_by: {deps})

里程碑 M2 ({milestone_name}):
  • {feature} (priority: {N}, blocked_by: {deps})

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Ready Set（可立即开始）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  • {feature}

{如果有缺失目录}
⚠️ 以下 feature 目录尚未创建：
  • {feature} → /new-feature {feature}

执行 /project-pm assign 生成 dev agent 命令
```

---

### `/project-pm status`

**功能**：显示项目整体状态

**执行逻辑**：

```yaml
步骤:
  1_read_tracker:
    read: "docs/_foundation/PROJECT_TRACKER.yaml"
    on_missing: |
      ❌ PROJECT_TRACKER 不存在

      请先执行 /project-pm init 初始化项目追踪器

  2_read_state:
    read: "docs/_foundation/PROJECT_PM_STATE.yaml"

  3_compute_milestone_progress:
    for_each: milestone in tracker.milestones
    compute: "completion_rate = done_count / total_count * 100"

  4_build_feature_matrix:
    for_each: feature in tracker.features
    read: "docs/{feature}/90_PROGRESS_LOG.yaml"
    extract: "current_phase, status"

  5_output: "状态概览"
```

**输出**：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 项目整体状态
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

项目: {project_name}
更新时间: {datetime}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏁 里程碑进度
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

M0 Foundation     ████████████████████ 100% ✅
M1 {name}         ████████████░░░░░░░░  {rate}% 🔄 (target: {date})
M2 {name}         ██░░░░░░░░░░░░░░░░░░  {rate}% 🔄 (target: {date})

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Feature 概览
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────┬────┬────┬────┬────┬────┬────┬────┬─────────┐
│ Feature         │ P1 │ P2 │ P3 │ P4 │ P5 │ P6 │ P7 │ Status  │
├─────────────────┼────┼────┼────┼────┼────┼────┼────┼─────────┤
│ {feature}       │ ✅ │ ✅ │ ✅ │ ✅ │ ✅ │ ✅ │ ✅ │ done    │
│ {feature}       │ ✅ │ 🔄 │ ⏳ │ ⏳ │ ⏳ │ ⏳ │ ⏳ │ Phase 2 │
│ {feature}       │ 🔒 │ 🔒 │ 🔒 │ 🔒 │ 🔒 │ 🔒 │ 🔒 │ blocked │
└─────────────────┴────┴────┴────┴────┴────┴────┴────┴─────────┘

图例: ✅ done | 🔄 wip | ⏳ pending | 🔒 blocked

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 统计
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Features: {N}
  ✅ Done:        {N}
  🔄 In Progress: {N}
  ⏳ Pending:     {N}
  🔒 Blocked:     {N}

Ready Set: {N} features can proceed in parallel
```

---

### `/project-pm ready`

**功能**：计算并显示 Ready Set

**Ready Set 计算规则**：

```python
def compute_ready_set(features):
    """
    Ready Set = 所有满足以下条件的 feature：
    1. status 不是 done
    2. status 不是 blocked
    3. 所有 blocked_by 依赖的 feature 状态都是 done
    """
    ready = []
    for feature_id, feature in features.items():
        if feature.status == "done":
            continue
        if feature.status == "blocked":
            continue

        # 检查所有依赖是否完成
        all_deps_done = all(
            features.get(dep, {}).get("status") == "done"
            for dep in feature.get("blocked_by", [])
        )

        # 检查目录是否存在
        dir_exists = directory_exists(f"docs/{feature_id}/")

        if all_deps_done and dir_exists:
            ready.append(feature_id)

    # 按优先级排序
    return sorted(ready, key=lambda f: features[f].get("priority", 99))
```

**输出**：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Ready Set - 可执行任务
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

计算时间: {datetime}

可立即执行（无阻塞依赖）：
┌─────────────────┬──────────┬──────────┬─────────────────────┐
│ Feature         │ Milestone│ Priority │ Status              │
├─────────────────┼──────────┼──────────┼─────────────────────┤
│ {feature}       │ {M1}     │ {1}      │ {ready}             │
│ {feature}       │ {M1}     │ {2}      │ {in_progress (P3)}  │
└─────────────────┴──────────┴──────────┴─────────────────────┘

被阻塞（等待依赖完成）：
┌─────────────────┬──────────┬─────────────────────┐
│ Feature         │ Milestone│ Blocked By          │
├─────────────────┼──────────┼─────────────────────┤
│ {feature}       │ {M1}     │ {blocked_by}        │
└─────────────────┴──────────┴─────────────────────┘

{如果 Ready Set 为空}
ℹ️ Ready Set 为空

可能原因：
  • 所有 feature 都已完成
  • 所有未完成的 feature 都被依赖阻塞
  • feature 目录尚未创建

检查方法：
  • 执行 /project-pm status 查看详细状态
  • 执行 /project-pm check 刷新进度

执行 /project-pm assign 生成开发命令
```

---

### `/project-pm assign [--max=N]`

**功能**：为 Ready Set 中的 feature 生成 dev agent 命令

**参数**：
- `--max=N`：最多生成 N 条命令（默认 5）

**执行逻辑**：

```yaml
步骤:
  1_compute_ready_set:
    call: compute_ready_set()

  2_check_empty:
    if: ready_set 为空
    output: |
      ℹ️ Ready Set 为空，无可分配任务

      执行 /project-pm check 检查进度更新

  3_get_feature_phase:
    for_each: feature in ready_set[:max]
    read: "docs/{feature}/90_PROGRESS_LOG.yaml"
    extract: current_phase

  4_generate_commands:
    for_each: feature
    command: "/ai-pm start {feature} --mode=full_auto --from-phase={current_phase}"

  5_output: "dev agent 命令列表"
```

**输出**：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 Dev Agent 命令生成
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

基于 Ready Set，生成以下命令：

┌─────────────────────────────────────────────────────────────┐
│ Agent 1: {feature}                                          │
├─────────────────────────────────────────────────────────────┤
│ /ai-pm start {feature} --mode=full_auto --from-phase={N}    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ Agent 2: {feature}                                          │
├─────────────────────────────────────────────────────────────┤
│ /ai-pm start {feature} --mode=full_auto --from-phase={N}    │
└─────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 操作步骤
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 打开新的 Claude Code CLI 终端
2. 复制上述命令执行
3. 完成后执行 /project-pm check 检查进度

⚠️ 注意：每个命令应在独立的 CLI 会话中执行
```

---

### `/project-pm check`

**功能**：检查各 feature 进度，更新 PROJECT_TRACKER

**执行逻辑**：

```yaml
步骤:
  1_read_tracker:
    read: "docs/_foundation/PROJECT_TRACKER.yaml"

  2_scan_features:
    for_each: feature_id in tracker.features
    actions:
      - check_directory:
          path: "docs/{feature_id}/"
          on_missing:
            set: status = "pending"
            warn: true

      - read_progress:
          file: "docs/{feature_id}/90_PROGRESS_LOG.yaml"
          extract: [current_phase, status]

      - read_gate:
          file: "docs/{feature_id}/PHASE_GATE_STATUS.yaml"
          extract: [current_gate_state]

      - update_tracker:
          fields:
            - current_phase
            - gate_state
            - status (如果 Phase 7 passed → done)

  3_recompute_ready_set:
    call: compute_ready_set(updated_features)

  4_recompute_stats:
    call: compute_stats(features, milestones)

  5_append_activities:
    for_each: feature in changed_features
    actions:
      - if_phase_changed:
          append_to: "docs/_foundation/PROJECT_ACTIVITY_LOG.yaml"
          activity:
            timestamp: current_datetime
            type: "phase_completed"
            feature: feature_id
            phase: previous_phase
            phase_name: phase_names[previous_phase]
            description: "{feature} 完成 Phase {previous_phase}"
            by: "/project-pm check"
            details:
              new_phase: current_phase
              gate_state: gate_state

      - if_feature_completed:
          append_to: "docs/_foundation/PROJECT_ACTIVITY_LOG.yaml"
          activity:
            timestamp: current_datetime
            type: "feature_completed"
            feature: feature_id
            description: "{feature} 功能开发完成"
            by: "/project-pm check"
            details:
              total_phases: 7
              mode: "N/A"

      - if_milestone_completed:
          append_to: "docs/_foundation/PROJECT_ACTIVITY_LOG.yaml"
          activity:
            timestamp: current_datetime
            type: "milestone_completed"
            milestone: milestone_id
            milestone_name: milestone_name
            description: "里程碑 {milestone_id} 完成"
            by: "/project-pm check"
            details:
              features_completed: completed_features_list

  6_save_tracker:
    write: "docs/_foundation/PROJECT_TRACKER.yaml"

  7_update_activity_summary:
    update: "docs/_foundation/PROJECT_ACTIVITY_LOG.yaml"
    fields:
      - summary.total_activities
      - summary.features_completed
      - summary.phases_completed
      - summary.milestones_completed
      - summary.last_activity_at

  8_output: "进度变化摘要"
```

**输出**：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 进度检查
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

正在扫描各 feature 进度...

Feature 状态更新：
┌─────────────────┬────────────┬────────────┬─────────────────┐
│ Feature         │ 上次状态   │ 当前状态   │ 变化            │
├─────────────────┼────────────┼────────────┼─────────────────┤
│ {feature}       │ Phase 4    │ Phase 7 ✅ │ COMPLETED       │
│ {feature}       │ Phase 1    │ Phase 3    │ +2 phases       │
└─────────────────┴────────────┴────────────┴─────────────────┘

{如果有 feature 完成}
🎉 Feature 完成：{feature}

{如果有新解锁}
新增 Ready（依赖解除）：
  ✅ {feature} ({blocker} 完成后解锁)
  ✅ {feature} ({blocker} 完成后解锁)

{如果有缺失目录}
⚠️ 以下 feature 目录不存在：
┌─────────────────┬─────────────────────┬────────────────────────────┐
│ Feature         │ 预期目录            │ 建议操作                   │
├─────────────────┼─────────────────────┼────────────────────────────┤
│ {feature}       │ docs/{feature}/     │ /new-feature {feature}     │
└─────────────────┴─────────────────────┴────────────────────────────┘

里程碑进度：
  M1: ████████████░░░░░░░░ {rate}% ({diff})
  M2: ██░░░░░░░░░░░░░░░░░░ {rate}% ({diff})

📝 下一步：
  执行 /project-pm assign 获取新的开发命令
```

---

### `/project-pm sync`

**功能**：同步 ROADMAP 变更到 PROJECT_TRACKER

**执行逻辑**：

```yaml
步骤:
  1_read_current:
    read: "docs/_foundation/PROJECT_TRACKER.yaml"

  2_parse_roadmap:
    read: "docs/_foundation/_planning/04_ROADMAP.md"
    extract: milestones

  3_detect_changes:
    compare: tracker.milestones vs parsed_milestones
    detect:
      - added_milestones
      - removed_milestones
      - renamed_milestones
      - date_changes

  4_parse_modules:
    read: "docs/_foundation/_planning/03_MODULE_DECOMPOSITION.md"
    compare: tracker.features vs parsed_features
    detect:
      - added_features
      - removed_features
      - dependency_changes

  5_confirm_sync:
    if: changes detected
    ask: |
      检测到以下变更：

      里程碑变更：
        {列出变更}

      功能变更：
        {列出变更}

      是否同步到 PROJECT_TRACKER？[y/N]

  6_apply_changes:
    update: tracker with changes
    recompute: ready_set, stats

  7_save:
    write: "docs/_foundation/PROJECT_TRACKER.yaml"
```

**输出**：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 同步 ROADMAP 变更
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

正在比对源文档与 PROJECT_TRACKER...

检测到以下变更：

里程碑变更：
  + 新增：M3 ({name})
  ~ 修改：M2 目标日期 {old} → {new}

功能变更：
  + 新增：{feature} (M3)
  ~ 修改：{feature} blocked_by 变更

是否同步到 PROJECT_TRACKER？[y/N]

{确认后}

✅ 同步完成

已更新：
  • 里程碑定义
  • 功能依赖关系
  • Ready Set（重新计算）

📝 下一步：
  执行 /project-pm ready 查看更新后的可执行任务
```

---

### `/project-pm logs [--tail=N] [--type=TYPE]`

**功能**：查看项目活动日志

**参数**：
- `--tail=N`：显示最近 N 条记录（默认 20）
- `--type=TYPE`：筛选活动类型（可选）
  - `feature_created` - 功能创建
  - `feature_started` - 功能开始
  - `phase_completed` - 阶段完成
  - `feature_completed` - 功能完成
  - `feature_blocked` - 功能阻塞
  - `milestone_completed` - 里程碑完成

**执行逻辑**：

```yaml
步骤:
  1_read_activity_log:
    read: "docs/_foundation/PROJECT_ACTIVITY_LOG.yaml"
    on_missing: |
      ❌ PROJECT_ACTIVITY_LOG 不存在

      请先执行 /project-pm init 初始化项目追踪器

  2_filter_activities:
    if: --type 指定
    filter: activities where type == TYPE

  3_limit_results:
    take: last N activities (default 20)

  4_format_output: "活动日志表格"
```

**输出**：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📜 项目活动日志
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

项目: {project_name}
显示最近 {N} 条记录

时间                    | 类型              | 描述
------------------------|-------------------|----------------------------------
2026-01-11 18:00        | feature_completed | user-auth 功能开发完成
2026-01-11 16:30        | phase_completed   | user-auth 完成 Phase 6 Test
2026-01-11 14:00        | phase_completed   | user-auth 完成 Phase 5 Code
2026-01-11 10:30        | feature_started   | 开始开发 user-auth
2026-01-11 10:00        | feature_created   | 创建 user-auth 功能模块
2026-01-11 09:00        | project_init      | 项目跟踪系统初始化

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 活动统计
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

总活动数: {N}
功能完成: {N}
阶段完成: {N}
里程碑完成: {N}

最后活动: {datetime}
```

---

## 状态图标说明

| 状态 | 图标 | 说明 |
|------|------|------|
| `done` | ✅ | 已完成（Phase 7 Gate passed） |
| `in_progress` | 🔄 | 执行中（Phase 1-7） |
| `ready` | ⬜ | 可执行（依赖满足） |
| `pending` | ⏳ | 待开始（目录不存在或依赖未满足） |
| `blocked` | 🔒 | 被阻塞（依赖的 feature 回退） |

## Feature 状态机

```
                              /project-pm init
                                    │
                                    ▼
                ┌───────────────────────────────────────────┐
                │                 pending                   │
                │    (目录不存在，或依赖未满足)               │
                └─────────────────────┬─────────────────────┘
                                      │
                     目录已创建 且 所有依赖 done
                                      │
                                      ▼
                ┌───────────────────────────────────────────┐
                │                  ready                    │
                │    (可执行：目录存在，依赖已满足)           │
                └─────────────────────┬─────────────────────┘
                                      │
                           /ai-pm start 或 Human 分配
                                      │
                                      ▼
                ┌───────────────────────────────────────────┐
    ┌───────────│              in_progress                  │
    │           │    (执行中：Phase 1-7 进行中)              │
    │           └─────────────────────┬─────────────────────┘
    │                                 │
    │                Phase 7 Gate passed
    │                                 │
    │                                 ▼
    │           ┌───────────────────────────────────────────┐
    │           │                  done                     │
    │           │    (已完成：所有 Phase Gate 通过)          │
    │           └───────────────────────────────────────────┘
    │
    │  依赖方状态回退
    │
    ▼
┌───────────────────────────────────────────────────────────┐
│                        blocked                             │
│    (阻塞：依赖的 feature 状态回退)                          │
└───────────────────────────────────────────────────────────┘
    │
    │  阻塞条件解除
    │
    └──────────────────────────────▶ ready
```

## 注意事项

1. **前置条件**：`init` 要求 Foundation Gate 已通过
2. **Human 分发**：`assign` 生成的命令需要 Human 手动分发到各 CLI 会话
3. **实时计算**：Ready Set 和进度在每次执行时实时计算
4. **不自动执行**：Project PM 只做协调，不直接执行 Feature AI PM 命令
5. **目录验证**：feature 目录必须存在才能进入 ready 状态

## 关联工具

- `/ai-pm` - Feature 级 AI PM Driver
- `/check-gate` - Gate 状态检查
- `/new-feature` - 创建功能模块
- `/check-gate --phase=0` - Foundation Gate 检查
- `/check-progress` - 查看功能进度

## 典型工作流

```bash
# 1. Foundation 完成后，初始化 Project PM
/project-pm init

# 2. 查看可执行任务
/project-pm ready

# 3. 生成 dev agent 命令
/project-pm assign

# 4. Human 在多个 CLI 窗口分别执行生成的命令
# (CLI 1) /ai-pm start feature-a --mode=full_auto
# (CLI 2) /ai-pm start feature-b --mode=full_auto

# 5. 定期检查进度
/project-pm check

# 6. 查看整体状态
/project-pm status

# 7. 继续分配新解锁的任务
/project-pm assign
```
