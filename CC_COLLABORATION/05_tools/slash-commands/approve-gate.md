# /approve-gate - 审批 Phase Gate

你是一个 AI 协作开发助手。用户请求审批功能模块的 Phase Gate。

## 参数

- `$ARGUMENTS`：功能模块名称，必需参数 `--phase=N`、`--role=ROLE`，可选参数 `--user=USERNAME`

## 用法

```
/approve-gate {feature} --phase=1 --role=PM
/approve-gate {feature} --phase=2 --role=Architect --user=bob
```

## 执行步骤

### 1. 解析参数

```
必需参数：
  feature = 第一个参数
  phase = --phase 参数值（必需）
  role = --role 参数值（必需）

可选参数：
  user = --user 参数值（默认为 "human"）

如果缺少必需参数，提示：
  请提供完整参数，例如：
  /approve-gate user-auth --phase=2 --role=PM --user=alice
```

### 2. 验证功能模块和文件存在

```
检查目录是否存在：docs/{feature}/
检查文件是否存在：
  - docs/{feature}/PHASE_GATE.yaml
  - docs/{feature}/PHASE_GATE_STATUS.yaml

如果文件不存在，提示错误并退出。
```

### 3. 读取配置和状态

```yaml
config = 读取 docs/{feature}/PHASE_GATE.yaml
status = 读取 docs/{feature}/PHASE_GATE_STATUS.yaml

phase_key = "phase_{phase}_*"  # 匹配 phase_1_kickoff 等
phase_config = config[phase_key]
phase_status = status[phase_key]
```

### 4. 验证角色有效性

```
required_roles = phase_config.approvals.required_roles

如果 role 不在 required_roles 中：
  ❌ 角色 "{role}" 不在 Phase {phase} 的审批列表中

  Phase {phase} 需要以下角色审批：
  {列出 required_roles}

  请使用正确的角色重试。
```

### 5. 检查是否已审批

```
for approval in phase_status.approvals:
    if approval.role == role and approval.user is not None:
        提示：
          ⚠️ {role} 已在 {approval.approved_at} 由 {approval.user} 审批

          如需重新审批，请先执行：
          /reset-approval {feature} --phase={phase} --role={role}
```

### 6. **核心：先检查后审批**

**硬规则**：审批前必须通过 block 级检查

```
# 调用 gate_checker skill 执行检查
使用 gate_checker skill：
- feature: {feature}
- phase: {phase}

获取检查结果 check_result

# 检查是否有 block 级失败
block_failures = [
    c for c in check_result.quality_checks
    if c.severity == "block" and not c.passed
]

如果 block_failures 不为空：
  ❌ 无法审批：存在未通过的 Block 级检查

  以下检查必须先通过：
  {列出 block_failures}

  请修复后重新运行 /check-gate {feature} --phase={phase}
```

### 7. 记录审批

```yaml
# 找到对应的 approval 记录并更新
for approval in phase_status.approvals:
    if approval.role == role:
        approval.user = user
        approval.approved_at = current_datetime

# 更新元数据
phase_status.last_check.checked_at = current_datetime
```

### 8. 检查是否所有审批完成

```
all_approved = all(
    a.user is not None
    for a in phase_status.approvals
)

如果 all_approved 且无 block 级失败：
    # 设置 gate_state 为 passed
    phase_status.gate_state = "passed"
    phase_status.gate_state_meta = {
        last_updated_at: current_datetime,
        last_updated_by_command: "/approve-gate",
        last_updated_by_user: user
    }
```

### 9. 保存状态文件

```
保存 status 到 docs/{feature}/PHASE_GATE_STATUS.yaml
```

### 10. 输出结果

#### 审批成功，Gate 通过

```
✅ Phase {phase} Gate 审批成功

功能模块: {feature}
阶段: Phase {phase} {Name}
审批角色: {role}
审批人: {user}
审批时间: {datetime}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✍️ 审批状态:
{列出所有角色的审批状态，全部 ✅}

🎉 Gate 状态: PASSED

所有审批已完成，可以进入下一阶段！
执行 /next-phase {feature} 继续。
```

#### 审批成功，等待其他角色

```
✅ Phase {phase} 审批已记录

功能模块: {feature}
阶段: Phase {phase} {Name}
审批角色: {role}
审批人: {user}
审批时间: {datetime}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✍️ 审批状态:
  ✅ {role}: {user} ({datetime})
  ⏳ {other_role}: 待审批

⏳ Gate 状态: PENDING

还需要以下角色审批：
  - {other_role}

请通知相关人员执行：
  /approve-gate {feature} --phase={phase} --role={other_role}
```

#### 审批失败（检查未通过）

```
❌ 无法审批 Phase {phase} Gate

功能模块: {feature}
阶段: Phase {phase} {Name}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚫 以下 Block 级检查未通过：

  ❌ {check_id}: {check_description}
     └─ {failure_detail}

📝 建议操作：
  1. {fix_suggestion}
  2. 修复后运行 /check-gate {feature} --phase={phase}
  3. 确认通过后重新执行此命令
```

## 完整示例

### 示例 1：首个角色审批

```
/approve-gate user-auth --phase=2 --role=PM --user=alice
```

输出：

```
✅ Phase 2 审批已记录

功能模块: user-auth
阶段: Phase 2 Spec
审批角色: PM
审批人: alice
审批时间: 2024-12-15T11:30:00

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✍️ 审批状态:
  ✅ PM: alice (2024-12-15T11:30:00)
  ⏳ Architect: 待审批

⏳ Gate 状态: PENDING

还需要以下角色审批：
  - Architect

请通知相关人员执行：
  /approve-gate user-auth --phase=2 --role=Architect
```

### 示例 2：最后一个角色审批，Gate 通过

```
/approve-gate user-auth --phase=2 --role=Architect --user=bob
```

输出：

```
✅ Phase 2 Gate 审批成功

功能模块: user-auth
阶段: Phase 2 Spec
审批角色: Architect
审批人: bob
审批时间: 2024-12-15T14:00:00

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✍️ 审批状态:
  ✅ PM: alice (2024-12-15T11:30:00)
  ✅ Architect: bob (2024-12-15T14:00:00)

🎉 Gate 状态: PASSED

所有审批已完成，可以进入下一阶段！
执行 /next-phase user-auth 继续。
```

### 示例 3：审批被拒绝（检查未通过）

```
/approve-gate user-auth --phase=2 --role=PM
```

输出：

```
❌ 无法审批 Phase 2 Gate

功能模块: user-auth
阶段: Phase 2 Spec

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚫 以下 Block 级检查未通过：

  ❌ spec_has_error_cases: SPEC 未定义错误处理
     └─ 搜索: ["错误处理", "Error", "异常"]
     └─ 文件: 11_UI_FLOW_SPEC.md

📝 建议操作：
  1. 在 11_UI_FLOW_SPEC.md 中添加「错误处理」章节
  2. 修复后运行 /check-gate user-auth --phase=2
  3. 确认通过后重新执行此命令
```

## 注意事项

1. **先检查后审批**：这是硬规则，无法绕过
2. **审计追踪**：所有审批记录保存在 `PHASE_GATE_STATUS.yaml` 中
3. **gate_state 写入权限**：只有此命令能将 `gate_state` 设置为 `passed`
4. **幂等性**：重复审批同一角色会提示已审批
5. **用户名**：如果不提供 `--user`，默认为 "human"

## 关联工具

- `gate_checker` skill - 审批前的检查
- `/check-gate` - 查看 Gate 状态
- `/next-phase` - 审批通过后进入下一阶段
- `/reset-approval` - 重置审批（未来功能）
