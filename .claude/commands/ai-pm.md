# /ai-pm - AI PM Driver 编排命令

你是一个 AI 协作开发助手。AI PM Driver 是一个编排层工具，用于自动化功能开发流程。

## 核心原则

**AI PM Driver 是编排层（Orchestration Layer），不是执行引擎（Execution Engine）。**

- Driver 只做决策（何时做什么、是否继续）
- 所有执行动作委托给现有 Skill（/check-gate, /next-phase, /expert-review 等）
- Driver 不存储执行事实（phase 完成状态从 progress check 实时获取）

## 参数

- `$ARGUMENTS`：子命令和参数

## 子命令总览

| 子命令 | 说明 | 前置状态 |
|--------|------|----------|
| `start` | 启动驱动器 | `idle` |
| `status` | 查看状态 | any |
| `pause` | 暂停执行 | `running` |
| `resume` | 恢复执行 | `paused`, `stuck` |
| `stop` | 停止执行 | any except `idle` |
| `confirm` | 确认继续 | `waiting_human` |
| `reject` | 拒绝继续 | `waiting_human` |
| `skip` | 跳过当前阶段 | `stuck` only |
| `compare` | 对比分析 | any |
| `logs` | 查看日志 | any |
| `restart` | 重新开始 | `failed` |

## 执行步骤

### 1. 解析参数

```
解析 $ARGUMENTS：
  - 第一个词为子命令（start, status, pause 等）
  - 第二个词为功能名称（feature）
  - 后续为选项参数（--mode, --from-phase 等）

如果 $ARGUMENTS 为空或只有功能名称，默认执行 status 子命令
```

### 2. 验证功能模块存在

```
检查目录是否存在：docs/{feature}/
检查文件是否存在：
  - docs/{feature}/90_PROGRESS_LOG.yaml
  - docs/{feature}/PHASE_GATE_STATUS.yaml

如果不存在，提示：
  ❌ 功能模块 "{feature}" 不存在或未启用 Gate 机制

  请先创建功能模块：
  /new-feature {feature}
```

### 3. 读取或创建状态文件

```yaml
state_file = "docs/{feature}/AI_PM_ORCHESTRATION_STATE.yaml"

如果文件存在：
  state = 读取 state_file
否则：
  state = null  # 尚未启动
```

---

## 子命令详细规格

### `/ai-pm start {feature} --mode={mode} [--from-phase=N]`

启动 AI PM Driver 编排。

**参数**：
- `feature`：功能名称（必需）
- `--mode`：运行模式（必需，`full_auto` 或 `human_confirm`）
- `--from-phase`：起始阶段（可选，默认 3）

**前置条件**：
- 功能目录存在
- 不存在正在运行的 Driver（状态为 idle 或无状态文件）
- 指定的起始阶段前置 Gate 已通过（实时查询 PHASE_GATE_STATUS.yaml）

**执行逻辑**：

```yaml
# 1. 验证前置条件
如果 state 存在且 state.runtime.status 不是 "idle"：
  ❌ Driver 已在运行中

  当前状态：{state.runtime.status}
  如需重新开始，请先执行：/ai-pm stop {feature}

# 2. 验证起始阶段前置 Gate
gate_status = 读取 PHASE_GATE_STATUS.yaml
from_phase = --from-phase 或 3
prev_phase = from_phase - 1

如果 prev_phase >= 1：
  prev_gate = gate_status["phase_{prev_phase}_*"].gate_state
  如果 prev_gate 不是 "passed" 且不是 "skipped"：
    ❌ 无法启动：Phase {prev_phase} 的 Gate 未通过

    请先完成 Phase {prev_phase} 的 Gate 审批：
    /check-gate {feature} --phase={prev_phase}
    /approve-gate {feature} --phase={prev_phase} --role={required_role}

# 3. 创建初始状态文件
state = {
  meta: {
    feature: "{feature}",
    schema_version: "1.1",
    created_at: current_datetime,
    created_by: "@human"
  },
  intent: {
    mode: "{mode}",
    start_phase: from_phase,
    target_phase: 7,
    allow_auto_fix: true,
    allow_skip: false
  },
  policy: {
    auto_fix: {
      max_attempts_per_issue: 2,
      max_attempts_per_phase: 5,
      max_total_attempts: 10
    },
    api_retry: {
      max_retries: 3,
      retry_delay_seconds: 5
    },
    circuit_breaker: {
      stuck_timeout_minutes: 30,
      total_timeout_minutes: 480,
      no_progress_threshold: 3
    },
    expert_review: {
      enabled: true,
      threshold: 7,
      required_phases: [4, 5, 6]
    },
    notification: {
      on_phase_complete: true,
      on_stuck: true,
      on_error: true
    }
  },
  runtime: {
    status: "running",
    last_action: "start",
    last_decision: "continue",
    last_decision_reason: "Driver 启动",
    last_decision_at: current_datetime,
    human_context: null,
    stuck_context: null
  },
  counters: {
    total_fix_attempts: 0,
    current_phase_fix_attempts: 0,
    per_issue_fix_attempts: {},
    consecutive_no_progress: 0,
    api_retry_count: 0,
    phase_events: [
      { phase: from_phase, event: "started", at: current_datetime }
    ]
  },
  timeline: {
    started_at: current_datetime,
    last_progress_at: current_datetime
  }
}

保存 state 到 state_file

# 4. 委托执行第一个检查
执行 /check-gate {feature} --phase={from_phase}
```

**输出**：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 AI PM Driver 已启动
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

功能：{feature}
模式：{mode}
起始阶段：Phase {from_phase}
目标阶段：Phase 7 (Deploy)

状态文件：docs/{feature}/AI_PM_ORCHESTRATION_STATE.yaml

开始执行 Gate 检查...
```

---

### `/ai-pm status {feature}`

查看 Driver 当前状态。

**执行逻辑**：

```yaml
如果 state 不存在：
  输出：
    ℹ️ AI PM Driver 未启动

    功能：{feature}
    状态：未初始化

    使用以下命令启动：
    /ai-pm start {feature} --mode=full_auto
    /ai-pm start {feature} --mode=human_confirm

否则：
  # 实时查询执行状态
  progress_log = 读取 90_PROGRESS_LOG.yaml
  gate_status = 读取 PHASE_GATE_STATUS.yaml
  current_phase = progress_log.meta.current_phase

  输出状态详情
```

**输出**：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 AI PM Driver 状态
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

功能：{feature}
模式：{state.intent.mode}
状态：{status_icon} {state.runtime.status}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 当前进度（实时查询）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

当前阶段：Phase {current_phase} {phase_name}
Gate 状态：{gate_state}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 编排计数器
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

总修复尝试：{state.counters.total_fix_attempts} / {state.policy.auto_fix.max_total_attempts}
当前阶段修复：{state.counters.current_phase_fix_attempts} / {state.policy.auto_fix.max_attempts_per_phase}
连续无进展：{state.counters.consecutive_no_progress} / {state.policy.circuit_breaker.no_progress_threshold}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕐 时间线
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

启动时间：{state.timeline.started_at}
最后进展：{state.timeline.last_progress_at}
运行时长：{duration}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 最后决策
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

动作：{state.runtime.last_action}
决策：{state.runtime.last_decision}
原因：{state.runtime.last_decision_reason}
时间：{state.runtime.last_decision_at}
```

---

### `/ai-pm confirm {feature}`

确认继续执行（仅在 `waiting_human` 状态有效）。

**语义约束**：
- `confirm` = 批准最后的 AI PM 决策
- **不会**修改 intent 或 policy
- **不会**重新评估
- 只是从暂停点恢复编排

**前置条件**：
- `state.runtime.status == "waiting_human"`

**执行逻辑**：

```yaml
如果 state.runtime.status != "waiting_human"：
  ❌ 当前状态不是 waiting_human

  当前状态：{state.runtime.status}
  confirm 命令只能在等待人工确认时使用。

# 更新状态
state.runtime.status = "running"
state.runtime.last_action = "confirm"
state.runtime.last_decision = "continue"
state.runtime.last_decision_reason = "人工确认继续"
state.runtime.last_decision_at = current_datetime
state.runtime.human_context = null

保存 state

# 恢复编排（不重新评估）
根据 human_context.waiting_for 执行相应动作：
  confirm_phase_transition → 执行 /next-phase {feature}
  clarify_requirement → 继续当前阶段
  其他 → 恢复执行
```

**输出**：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 确认成功
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

功能：{feature}
确认动作：{previous_human_context.waiting_for}
确认时间：{datetime}

恢复编排...（从暂停点继续，不重新评估）
```

---

### `/ai-pm reject {feature} --reason="xxx"`

拒绝当前动作（仅在 `waiting_human` 状态有效）。

**参数**：
- `--reason`：拒绝原因（必需）

**前置条件**：
- `state.runtime.status == "waiting_human"`

**执行逻辑**：

```yaml
如果 state.runtime.status != "waiting_human"：
  ❌ 当前状态不是 waiting_human

# 更新状态
state.runtime.status = "stuck"
state.runtime.last_action = "reject"
state.runtime.last_decision = "ask_human"
state.runtime.last_decision_reason = "人工拒绝: {reason}"
state.runtime.last_decision_at = current_datetime
state.runtime.human_context = null
state.runtime.stuck_context = {
  stuck_since: current_datetime,
  stuck_reason: "review_rejection",
  blocked_issue: reason,
  suggested_actions: [
    "检查拒绝原因并修复",
    "执行 /ai-pm resume {feature} 恢复"
  ]
}

保存 state
```

**输出**：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ 已拒绝
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

功能：{feature}
拒绝原因：{reason}
时间：{datetime}

Driver 已进入 STUCK 状态。

📝 下一步操作：
1. 检查拒绝原因并修复相关问题
2. 执行 /ai-pm resume {feature} 恢复
```

---

### `/ai-pm pause {feature}`

暂停执行（仅在 `running` 状态有效）。

**前置条件**：
- `state.runtime.status == "running"`

**执行逻辑**：

```yaml
如果 state.runtime.status != "running"：
  ❌ 当前状态不是 running

state.runtime.status = "paused"
state.runtime.last_action = "pause"
state.runtime.last_decision = "ask_human"
state.runtime.last_decision_reason = "人工暂停"
state.runtime.last_decision_at = current_datetime

保存 state
```

**输出**：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏸️ 已暂停
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

功能：{feature}
暂停时间：{datetime}

使用以下命令恢复：
/ai-pm resume {feature}
```

---

### `/ai-pm resume {feature}`

恢复执行（在 `paused` 或 `stuck` 状态有效）。

**前置条件**：
- `state.runtime.status` 为 `paused` 或 `stuck`

**执行逻辑**：

```yaml
如果 state.runtime.status 不是 "paused" 也不是 "stuck"：
  ❌ 当前状态不支持 resume

  当前状态：{state.runtime.status}
  resume 命令只能在 paused 或 stuck 状态使用。

prev_status = state.runtime.status

state.runtime.status = "running"
state.runtime.last_action = "resume"
state.runtime.last_decision = "continue"
state.runtime.last_decision_reason = "从 {prev_status} 恢复"
state.runtime.last_decision_at = current_datetime
state.runtime.stuck_context = null
state.timeline.last_progress_at = current_datetime

保存 state

# 重新进入编排循环
执行 orchestration_loop
```

**输出**：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶️ 已恢复
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

功能：{feature}
前一状态：{prev_status}
恢复时间：{datetime}

继续执行编排...
```

---

### `/ai-pm stop {feature}`

停止执行（需要确认）。

**前置条件**：
- `state.runtime.status` 不是 `idle`

**执行逻辑**：

```yaml
如果 state 不存在或 state.runtime.status == "idle"：
  ❌ Driver 未在运行

# 提示确认
输出：
  ⚠️ 确认停止 AI PM Driver？

  功能：{feature}
  当前状态：{state.runtime.status}
  运行时长：{duration}

  停止后状态文件将被重置。

  确认请输入：/ai-pm stop {feature} --confirm

如果有 --confirm：
  state.runtime.status = "idle"
  state.runtime.last_action = "stop"
  state.runtime.last_decision = "abort"
  state.runtime.last_decision_reason = "人工停止"
  state.runtime.last_decision_at = current_datetime

  保存 state
```

**输出**：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏹️ 已停止
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

功能：{feature}
停止时间：{datetime}

Driver 已停止。使用以下命令重新启动：
/ai-pm start {feature} --mode={mode}
```

---

### `/ai-pm skip {feature} --reason="xxx" --approver="@xxx"`

跳过当前阶段（仅在 `stuck` 状态有效，需要审批记录）。

**参数**：
- `--reason`：跳过原因（必需）
- `--approver`：审批人（必需）

**前置条件**：
- `state.runtime.status == "stuck"`

**硬规则**：
- 必须记录 reason 和 approver
- 写入审计日志
- 不能连续跳过超过 2 个阶段

**执行逻辑**：

```yaml
如果 state.runtime.status != "stuck"：
  ❌ skip 命令只能在 STUCK 状态使用

  当前状态：{state.runtime.status}
  只有在 STUCK 状态下才能跳过阶段。

# 检查连续跳过次数
consecutive_skips = 计算最近连续跳过的阶段数
如果 consecutive_skips >= 2：
  ❌ 不能连续跳过超过 2 个阶段

  已跳过阶段：{list}
  请手动处理当前阻塞问题。

# 实时查询当前阶段
progress_log = 读取 90_PROGRESS_LOG.yaml
current_phase = progress_log.meta.current_phase

# 更新 Gate 状态为 skipped
gate_status = 读取 PHASE_GATE_STATUS.yaml
gate_status["phase_{current_phase}_*"].gate_state = "skipped"
gate_status["phase_{current_phase}_*"].gate_state_meta = {
  last_updated_at: current_datetime,
  last_updated_by_command: "/ai-pm skip",
  last_updated_by_user: approver
}
保存 gate_status

# 更新 Driver 状态
state.runtime.status = "running"
state.runtime.last_action = "skip"
state.runtime.last_decision = "continue"
state.runtime.last_decision_reason = "跳过 Phase {current_phase}: {reason}"
state.runtime.last_decision_at = current_datetime
state.runtime.stuck_context = null
state.counters.phase_events.append({
  phase: current_phase,
  event: "skipped",
  at: current_datetime,
  reason: reason,
  approver: approver
})

保存 state

# 执行 next-phase
执行 /next-phase {feature}
```

**输出**：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏭️ 阶段已跳过
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

功能：{feature}
跳过阶段：Phase {current_phase}
跳过原因：{reason}
审批人：{approver}
审批时间：{datetime}

⚠️ 警告：跳过阶段可能影响最终质量

继续执行...
```

---

### `/ai-pm compare {feature_a} {feature_b}`

对比两个功能模块的编排效率。

**执行逻辑**：

```yaml
# 读取两个功能的状态
state_a = 读取 docs/{feature_a}/AI_PM_ORCHESTRATION_STATE.yaml
state_b = 读取 docs/{feature_b}/AI_PM_ORCHESTRATION_STATE.yaml

# 计算效率指标
total_time_a = 计算总耗时(state_a)
total_time_b = 计算总耗时(state_b)
human_wait_a = 计算人工等待时间(state_a)
human_wait_b = 计算人工等待时间(state_b)

# 计算迭代指标
fix_attempts_a = state_a.counters.total_fix_attempts
fix_attempts_b = state_b.counters.total_fix_attempts

# 生成对比报表
```

**输出**：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 AI PM Driver 模式对比报表
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

对比对象：
• Feature A: {feature_a} ({mode_a})
• Feature B: {feature_b} ({mode_b})

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️ 效率指标
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    Feature A    Feature B    差异
总耗时               {time_a}     {time_b}    {diff}%
人工等待时间          {wait_a}     {wait_b}    {diff}%
实际执行时间         {exec_a}     {exec_b}    {diff}%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 迭代指标
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    Feature A    Feature B    差异
Gate 检查次数        {gate_a}     {gate_b}    {diff}
自动修复次数         {fix_a}      {fix_b}     {diff}
人工介入次数         {human_a}    {human_b}   {diff}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 结论
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{自动生成的对比结论}
```

---

### `/ai-pm logs {feature} [--tail=N]`

查看编排日志。

**参数**：
- `--tail`：显示最后 N 条记录（默认 20）

**执行逻辑**：

```yaml
state = 读取 AI_PM_ORCHESTRATION_STATE.yaml

# 输出 phase_events
for event in state.counters.phase_events[-N:]:
  输出：{event.at} | Phase {event.phase} | {event.event}
```

**输出**：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📜 AI PM Driver 日志
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

功能：{feature}
显示最后 {N} 条记录

时间                    | 阶段     | 事件
------------------------|----------|------------------
{datetime}              | Phase 3  | started
{datetime}              | Phase 3  | gate_passed
{datetime}              | Phase 4  | started
...
```

---

### `/ai-pm restart {feature}`

重新开始（仅在 `failed` 状态有效）。

**前置条件**：
- `state.runtime.status == "failed"`

**执行逻辑**：

```yaml
如果 state.runtime.status != "failed"：
  ❌ restart 命令只能在 FAILED 状态使用

  当前状态：{state.runtime.status}
  如需重新开始，请先 stop 再 start。

# 重置状态为 idle
state.runtime.status = "idle"
state.runtime.last_action = "restart"
state.runtime.last_decision = "continue"
state.runtime.last_decision_reason = "从 failed 状态重新开始"
state.runtime.last_decision_at = current_datetime
# 保留 counters 和 timeline 用于审计

保存 state
```

**输出**：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 已重置
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

功能：{feature}
前一状态：failed
重置时间：{datetime}

Driver 已重置为 idle 状态。

使用以下命令重新启动：
/ai-pm start {feature} --mode={mode}
```

---

## 编排循环逻辑

当 Driver 处于 `running` 状态时，执行以下编排循环：

```yaml
orchestration_loop:
  # 1. 实时查询当前状态（不从 Driver 状态读取）
  progress_log = 读取 90_PROGRESS_LOG.yaml
  gate_status = 读取 PHASE_GATE_STATUS.yaml
  current_phase = progress_log.meta.current_phase

  # 2. 检查是否已完成
  如果 current_phase > state.intent.target_phase：
    state.runtime.status = "completed"
    生成完成报告
    返回

  # 3. 检查熔断条件
  如果 check_circuit_breaker() 触发：
    state.runtime.status = "stuck"
    state.runtime.stuck_context = { ... }
    返回

  # 4. 执行 Gate 检查
  gate_result = 执行 /check-gate {feature} --phase={current_phase}

  # 5. 根据 Gate 结果决策
  如果 gate_result.passed：
    如果 state.intent.mode == "full_auto"：
      # 自动执行 next-phase
      state.runtime.last_action = "delegate_next_phase"
      执行 /next-phase {feature}
      # 循环继续
    否则：  # human_confirm 模式
      # 等待人工确认
      state.runtime.status = "waiting_human"
      state.runtime.human_context = {
        waiting_since: current_datetime,
        waiting_for: "confirm_phase_transition",
        summary: "Phase {current_phase} Gate 通过，等待确认进入 Phase {current_phase+1}",
        suggested_command: "/ai-pm confirm {feature}",
        confirm_action: "resume_orchestration"
      }
      返回

  否则：  # Gate 失败
    如果 gate_result.auto_fixable 且未达熔断：
      # 委托修复
      state.runtime.last_action = "delegate_auto_fix"
      state.counters.total_fix_attempts += 1
      state.counters.current_phase_fix_attempts += 1
      # 委托 progress check / expert review 执行修复
      # 等待下一次循环评估
    否则：
      # 不可修复，进入 stuck
      state.runtime.status = "stuck"
      state.runtime.stuck_context = {
        stuck_since: current_datetime,
        stuck_reason: "fundamental",
        blocked_issue: gate_result.blocked_reasons[0],
        suggested_actions: [...]
      }
      返回

# 熔断检查
check_circuit_breaker():
  # 检查各类熔断条件
  如果 state.counters.total_fix_attempts >= state.policy.auto_fix.max_total_attempts：
    返回 { triggered: true, reason: "max_retry" }

  如果 state.counters.current_phase_fix_attempts >= state.policy.auto_fix.max_attempts_per_phase：
    返回 { triggered: true, reason: "max_retry" }

  如果 state.counters.consecutive_no_progress >= state.policy.circuit_breaker.no_progress_threshold：
    返回 { triggered: true, reason: "no_progress" }

  如果 当前时间 - state.timeline.started_at > state.policy.circuit_breaker.total_timeout_minutes：
    返回 { triggered: true, reason: "timeout" }

  返回 { triggered: false }
```

---

## 状态图标说明

| 状态 | 图标 | 说明 |
|------|------|------|
| `idle` | ⚪ | 未启动 |
| `running` | 🟢 | 运行中 |
| `waiting_human` | 🟡 | 等待人工 |
| `stuck` | 🔴 | 卡住 |
| `paused` | ⏸️ | 已暂停 |
| `completed` | ✅ | 已完成 |
| `failed` | ❌ | 失败 |

---

## 注意事项

1. **编排层原则**：Driver 只做决策，不做执行
2. **实时查询**：当前 phase 从 progress_log 实时获取，不从 Driver 状态读取
3. **禁止字段**：Driver 状态中禁止存储 current_phase / step_status / completed / gate_result
4. **委托执行**：所有执行动作通过已有 Skill 完成
5. **无内部循环**：Driver 中没有 while/for 执行循环

## 关联工具

- `/check-gate` - Gate 检查
- `/approve-gate` - Gate 审批
- `/next-phase` - 进入下一阶段
- `/expert-review` - 专家评审
- `/check-progress` - 查看进度
- `/iresume` - 恢复上下文
