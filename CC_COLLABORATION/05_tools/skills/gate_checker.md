# gate_checker - Phase Gate 检查器

## 能力描述

检查指定功能模块的 Phase Gate 状态，验证是否满足进入下一阶段的条件。

**核心职责**：
- 检查 `required_outputs` 是否存在
- 执行 `quality_checks` 验证
- 检查 `approvals` 审批状态
- 更新 `PHASE_GATE_STATUS.yaml` 的检查结果

**设计原则**：
- Gate 状态只能由此 skill 和 `/approve-gate` 命令写入
- 禁止手动修改 `gate_state` 字段

## 输入

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| feature | string | 是 | 功能模块名称（如 `user-auth`） |
| phase | number/string | 是 | Phase 编号或名称（如 `1` 或 `kickoff`） |

## 输出

```yaml
gate_check_result:
  feature: "{feature-name}"
  phase: "phase_{n}_{name}"
  timestamp: "{datetime}"

  overall_state: pending | passed | blocked | skipped

  required_outputs:
    - path: "{file_path}"
      exists: true | false
      status: "✅ 存在" | "❌ 缺失" | "⏭️ 跳过（条件不满足）"

  quality_checks:
    - id: "{check_id}"
      passed: true | false
      severity: block | warn
      message: "✅ 通过" | "❌ 失败: {reason}" | "⚠️ 警告: {reason}"
      evidence:
        location: "{file}:{line}" | null
        matched: "{matched_content}" | null
        searched: ["{pattern1}", "{pattern2}"]  # 搜索失败时列出

  warnings:
    - id: "{check_id}"
      message: "⚠️ {warning_message}"

  approvals:
    required: ["{role1}", "{role2}"]
    completed:
      - role: "{role}"
        user: "{username}"
        at: "{datetime}"
    pending: ["{role}"]

  blocked_reasons:
    - "{reason1}"
    - "{reason2}"

  next_actions:
    - action: "{action_type}"
      description: "{action_description}"
      target_file: "{file}" | null
      role: "{role}" | null

  recommendation: |
    建议操作：
    1. {step1}
    2. {step2}
```

## 执行步骤

### 1. 读取配置和状态文件

```yaml
# 读取规则配置
config = load_yaml("docs/{feature}/PHASE_GATE.yaml")

# 读取运行状态
status = load_yaml("docs/{feature}/PHASE_GATE_STATUS.yaml")

# 获取 feature_profile（条件判断的事实源）
feature_profile = config.feature_profile
```

### 2. 解析 Phase 参数

```python
# 支持数字或名称
if phase is number:
    phase_key = f"phase_{phase}_*"  # 匹配 phase_1_kickoff 等
else:
    phase_key = f"phase_*_{phase}"  # 匹配 phase_1_kickoff 等

phase_config = config[phase_key]
phase_status = status[phase_key]
```

### 3. 检查阶段是否启用

```python
if "enabled_condition" in phase_config:
    if not eval_condition(phase_config.enabled_condition, feature_profile):
        return GateResult(
            state="skipped",
            reason="阶段已跳过（条件不满足）"
        )
```

### 4. 检查 required_outputs

```python
for output in phase_config.required_outputs:
    # 检查条件
    if "condition" in output:
        if not eval_condition(output.condition, feature_profile):
            results.append({
                path: output.path,
                exists: "skipped",
                status: f"⏭️ 跳过（条件不满足：{output.condition}）"
            })
            continue

    # 检查文件是否存在（支持 glob）
    matched_files = glob_match(output.path, feature_dir)

    if output.required and len(matched_files) == 0:
        blocked_reasons.append(f"缺少必需文件: {output.path}")
        results.append({
            path: output.path,
            exists: false,
            status: "❌ 缺失"
        })
    else:
        results.append({
            path: output.path,
            exists: true,
            status: "✅ 存在"
        })
```

### 5. 执行 quality_checks

```python
for check in phase_config.quality_checks:
    result = run_quality_check(check, feature_dir, feature_profile)

    if not result.passed:
        if check.severity == "block":
            blocked_reasons.append(f"质量检查失败: {check.description}")
        else:
            warnings.append({
                id: check.id,
                message: f"⚠️ {check.description}"
            })

    check_results.append(result)
```

#### 5.1 content_check 实现

```python
def run_content_check(check, feature_dir):
    target_files = glob_match(check.target, feature_dir)

    for file in target_files:
        content = read_file(file)

        # 搜索 anchor（正则匹配）
        matches = regex_findall(check.anchor, content)

        if len(matches) >= check.get("min_items", 1):
            return CheckResult(
                passed=True,
                evidence={
                    location: f"{file}:{line_number}",
                    matched: matches[0]
                }
            )

        # 检查 min_chars
        if "min_chars" in check:
            section_content = extract_section(content, check.anchor)
            if len(section_content) >= check.min_chars:
                return CheckResult(passed=True)

    return CheckResult(
        passed=False,
        evidence={
            location: None,
            searched: check.anchor.split("|")
        }
    )
```

#### 5.2 yaml_check 实现

```python
def run_yaml_check(check, feature_dir):
    target_file = glob_match(check.target, feature_dir)[0]
    yaml_data = load_yaml(target_file)

    # 使用字段路径获取值
    actual_value = get_nested_value(yaml_data, check.field)

    if actual_value == check.expected:
        return CheckResult(passed=True)
    else:
        return CheckResult(
            passed=False,
            message=f"字段 {check.field} 期望值为 {check.expected}，实际为 {actual_value}"
        )
```

#### 5.3 code_scan 实现

```python
def run_code_scan(check, feature_dir):
    # 在代码文件中搜索模式
    matches = grep_pattern(check.pattern, feature_dir, exclude=check.get("exclude", []))

    if len(matches) == 0:
        return CheckResult(passed=True)
    else:
        return CheckResult(
            passed=False,
            message=f"发现 {len(matches)} 处匹配: {check.pattern}",
            evidence={
                location: matches[0].file + ":" + matches[0].line,
                matched: matches[0].content
            }
        )
```

#### 5.4 manual 类型

```python
def run_manual_check(check, feature_dir):
    # manual 类型需要人工确认，始终返回 pending
    return CheckResult(
        passed=None,  # 未确认
        message="需要人工确认",
        checklist=check.get("checklist", [])
    )
```

### 6. 检查审批状态

```python
required_roles = phase_config.approvals.required_roles
completed_approvals = [
    a for a in phase_status.approvals
    if a.user is not None
]
completed_roles = [a.role for a in completed_approvals]
pending_roles = [r for r in required_roles if r not in completed_roles]

if pending_roles:
    return GateResult(
        state="pending",
        reason=f"等待审批: {', '.join(pending_roles)}"
    )
```

### 7. 计算最终状态

```python
if blocked_reasons:
    overall_state = "blocked"
elif pending_roles:
    overall_state = "pending"
else:
    overall_state = "passed"
```

### 8. 更新 PHASE_GATE_STATUS.yaml

```python
# 只更新 last_check，不直接设置 gate_state（除非是 blocked）
phase_status.last_check = {
    checked_at: current_datetime,
    blocked_reason: blocked_reasons[0] if blocked_reasons else None,
    check_results: check_results
}

# 如果是 blocked，更新 gate_state
if overall_state == "blocked":
    phase_status.gate_state = "blocked"
    phase_status.gate_state_meta = {
        last_updated_at: current_datetime,
        last_updated_by_command: "gate_checker",
        last_updated_by_user: null
    }

# 追加到 check_history
phase_status.check_history.append({
    checked_at: current_datetime,
    result: overall_state,
    blocked_reasons: blocked_reasons
})

# 保存文件
save_yaml(status, "docs/{feature}/PHASE_GATE_STATUS.yaml")
```

### 9. 生成 next_actions

```python
next_actions = []

for reason in blocked_reasons:
    if "缺少必需文件" in reason:
        next_actions.append({
            action: "create_file",
            description: f"创建缺失的文件: {extract_path(reason)}",
            target_file: extract_path(reason)
        })
    elif "质量检查失败" in reason:
        next_actions.append({
            action: "fix_content",
            description: reason,
            target_file: related_file
        })

for role in pending_roles:
    next_actions.append({
        action: "request_approval",
        description: f"请 {role} 审批",
        role: role
    })
```

### 10. 输出结果

输出结构化的检查结果，格式参见「输出」部分。

## 输出示例

### 示例 1：Gate 被阻断

```
📋 Phase Gate 检查结果

功能模块: user-auth
阶段: Phase 2 Spec
检查时间: 2024-12-15T11:00:00

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
状态: ❌ BLOCKED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 必需产出物:
  ✅ 11_UI_FLOW_SPEC.md - 存在

📊 质量检查:
  ✅ spec_has_pages - SPEC 包含页面定义
     └─ 位置: 11_UI_FLOW_SPEC.md:15
     └─ 匹配: "## 1. 登录页面"
  ❌ spec_has_error_cases - SPEC 未定义错误处理
     └─ 搜索: ["错误处理", "Error", "异常"]
  ⚠️ spec_has_edge_cases - 建议补充边界条件

✍️ 审批状态:
  ✅ PM: alice (2024-12-15T10:00:00)
  ⏳ Architect: 待审批

🚫 阻断原因:
  1. 质量检查失败: SPEC 未定义错误处理

📝 建议操作:
  1. 在 11_UI_FLOW_SPEC.md 中添加「## 错误处理」章节
  2. 请 Architect 审批
```

### 示例 2：Gate 通过

```
📋 Phase Gate 检查结果

功能模块: user-auth
阶段: Phase 1 Kickoff
检查时间: 2024-12-15T10:30:00

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
状态: ✅ PASSED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 必需产出物:
  ✅ 00_CONTEXT.md - 存在
  ✅ 30_PROGRESS_LOG.yaml - 存在

📊 质量检查:
  ✅ context_has_goals - 包含功能目标 (3 条)
  ✅ context_has_non_goals - 包含 Non-Goals (2 条)
  ✅ context_has_acceptance - 包含验收标准 (120 字符)

✍️ 审批状态:
  ✅ PM: alice (2024-12-15T10:00:00)

🎉 Gate 已通过，可以进入下一阶段！
```

## 注意事项

1. **只读原则**：此 skill 只更新 `PHASE_GATE_STATUS.yaml`，不修改其他文件
2. **安全写入**：`gate_state` 只能设置为 `blocked`，`passed` 需要通过 `/approve-gate` 设置
3. **条件解析**：使用安全的表达式解释器，不执行任意代码
4. **Glob 匹配**：`*` 只匹配根目录，`**` 才递归子目录
5. **幂等性**：多次运行相同检查应产生相同结果

## 关联工具

- `/check-gate` - 调用此 skill 显示 Gate 状态
- `/approve-gate` - 在此 skill 检查通过后记录审批
- `/next-phase` - 在执行前调用此 skill 验证
- `progress_updater` - 协同更新进度信息
