# /next-phase - 进入下一开发阶段

你是一个 AI 协作开发助手。用户请求将功能模块推进到下一个开发阶段。

## 参数

- `$ARGUMENTS`：功能模块名称

## 用法

```
/next-phase {feature-name}
```

## 执行步骤

### 1. 验证参数

```
如果 $ARGUMENTS 为空，提示：
  请提供功能名称，例如：/next-phase user-auth
```

### 2. 验证功能模块存在

```
检查目录是否存在：docs/{feature}/
检查文件是否存在：
  - docs/{feature}/90_PROGRESS_LOG.yaml

如果不存在，提示错误并退出。
```

### 3. 读取当前 Phase

```yaml
progress_log = 读取 docs/{feature}/90_PROGRESS_LOG.yaml
current_phase = progress_log.meta.current_phase
```

### 4. **Gate 检查（核心新增）**

**硬规则**：必须通过当前 Phase 的 Gate 才能进入下一阶段

```
# 检查 Gate 文件是否存在
如果存在 docs/{feature}/PHASE_GATE_STATUS.yaml：

    status = 读取 docs/{feature}/PHASE_GATE_STATUS.yaml
    phase_key = "phase_{current_phase}_*"
    gate_state = status[phase_key].gate_state

    # 检查 Gate 状态
    如果 gate_state == "pending":
        ❌ 无法进入下一阶段

        Phase {current_phase} 的 Gate 尚未检查或审批完成。

        当前状态: ⏳ PENDING

        请先执行以下操作：
        1. /check-gate {feature} --phase={current_phase}
        2. /approve-gate {feature} --phase={current_phase} --role={required_role}

        Gate 审批通过后才能进入下一阶段。

    如果 gate_state == "blocked":
        ❌ 无法进入下一阶段

        Phase {current_phase} 的 Gate 被阻断。

        当前状态: ❌ BLOCKED
        阻断原因: {status[phase_key].last_check.blocked_reason}

        请先修复以下问题：
        {列出 blocked_reasons}

        修复后执行：
        1. /check-gate {feature} --phase={current_phase}
        2. /approve-gate {feature} --phase={current_phase} --role={required_role}

    如果 gate_state == "passed" 或 gate_state == "skipped":
        # 继续执行
        通过 Gate 检查，可以进入下一阶段
```

### 5. 确定下一个 Phase

```
Phase 顺序：
1 → 2 → 3 → 4 → 5 → 6 → 7

next_phase = current_phase + 1

如果 next_phase > 7:
    提示：
      🎉 功能模块 "{feature}" 已完成所有阶段！

      恭喜！功能开发流程已全部完成。
      请查看 docs/{feature}/70_RELEASE_NOTE.md
```

### 6. 检查下一 Phase 是否需要跳过

```
如果存在 docs/{feature}/PHASE_GATE.yaml：
    config = 读取 docs/{feature}/PHASE_GATE.yaml
    feature_profile = config.feature_profile
    next_phase_config = config["phase_{next_phase}_*"]

    如果 next_phase_config 有 enabled_condition：
        如果 eval_condition(enabled_condition, feature_profile) == false：
            # 跳过此阶段
            更新 status["phase_{next_phase}_*"].gate_state = "skipped"
            递归检查下一个 phase
```

### 7. 更新 PROGRESS_LOG

```yaml
# 更新 meta
progress_log.meta.current_phase = next_phase
progress_log.meta.last_updated = current_datetime

# 更新当前阶段状态
progress_log["phase_{current_phase}_*"].status = "done"

# 更新下一阶段状态
progress_log["phase_{next_phase}_*"].status = "wip"

# 更新断点信息
progress_log.cc_checkpoint = {
    session_id: "cc-{date}-{feature}",
    last_file_edited: "90_PROGRESS_LOG.yaml",
    last_action: "进入 Phase {next_phase}",
    next_step: "{next_phase_description}",
    context_files: [...]
}

保存 docs/{feature}/90_PROGRESS_LOG.yaml
```

### 8. 初始化下一 Phase 的 Gate 状态

```yaml
如果存在 PHASE_GATE_STATUS.yaml：
    # 确保下一阶段的 approvals 数组已初始化
    # （通常在创建 feature 时已初始化）
```

### 9. 创建下一 Phase 的模板文件（如果需要）

```
Phase 2 Spec:
  如果 feature_profile.has_ui == true:
    创建 21_UI_FLOW_SPEC.md（从模板）
  否则:
    创建 20_API_SPEC.md（从模板）

Phase 4 Design:
  创建 40_DESIGN_FINAL.md（从模板）

Phase 5 Code:
  创建 50_DEV_PLAN.md（从模板）

Phase 6 Test:
  创建 60_TEST_PLAN.md（从模板）

Phase 7 Deploy:
  创建 70_RELEASE_NOTE.md（从模板）
```

### 10. 输出结果

```
🚀 进入下一阶段

功能模块: {feature}
当前阶段: Phase {next_phase} {phase_name}
前一阶段: Phase {current_phase} {prev_phase_name} ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 已创建/更新文件：
{列出创建的模板文件}

📋 Phase {next_phase} 任务清单：
{列出该阶段的主要任务}

📝 下一步操作：
1. {具体操作建议}
2. 完成后执行 /check-gate {feature} --phase={next_phase}
3. 请相关角色审批后继续

💡 提示：
- 使用 /check-progress {feature} 查看详细进度
- 使用 /iresume {feature} 恢复工作上下文
```

## 输出示例

### 示例 1：Gate 通过，成功进入下一阶段

```
/next-phase user-auth
```

输出：

```
🚀 进入下一阶段

功能模块: user-auth
当前阶段: Phase 2 Spec
前一阶段: Phase 1 Kickoff ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 已创建文件：
  ✅ docs/user-auth/21_UI_FLOW_SPEC.md

📋 Phase 2 任务清单：
  - [ ] 定义所有页面和用户流程
  - [ ] 描述各页面的交互行为
  - [ ] 列出错误处理和边界情况
  - [ ] 获取 Architect 和 PM 审批

📝 下一步操作：
1. 编辑 21_UI_FLOW_SPEC.md 补充 SPEC 内容
2. 完成后执行 /check-gate user-auth --phase=2
3. 请 Architect 和 PM 审批后继续

💡 提示：
- 使用 /check-progress user-auth 查看详细进度
- 使用 /iresume user-auth 恢复工作上下文
```

### 示例 2：Gate 被阻断，无法进入

```
/next-phase user-auth
```

输出：

```
❌ 无法进入下一阶段

Phase 1 的 Gate 被阻断。

当前状态: ❌ BLOCKED
阻断原因: Context 必须明确 Non-Goals（不做什么）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

请先修复以下问题：

1. ❌ context_has_non_goals: Context 未定义 Non-Goals
   └─ 位置: docs/user-auth/10_CONTEXT.md
   └─ 建议: 添加「不包含内容」或「Out of Scope」章节

修复后执行：
1. /check-gate user-auth --phase=1
2. /approve-gate user-auth --phase=1 --role=PM
```

### 示例 3：Gate 待审批

```
/next-phase user-auth
```

输出：

```
❌ 无法进入下一阶段

Phase 2 的 Gate 尚未审批完成。

当前状态: ⏳ PENDING

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✍️ 审批状态:
  ✅ PM: alice (2024-12-15T11:30:00)
  ⏳ Architect: 待审批

请执行以下操作：
  /approve-gate user-auth --phase=2 --role=Architect

Gate 审批通过后才能进入下一阶段。
```

### 示例 4：跳过可选阶段

```
/next-phase api-service
```

输出：

```
🚀 进入下一阶段

功能模块: api-service
当前阶段: Phase 4 Design
前一阶段: Phase 2 Spec ✅
跳过阶段: Phase 3 Demo ⏭️ (无 UI 组件)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 已创建文件：
  ✅ docs/api-service/40_DESIGN_FINAL.md

...
```

## 注意事项

1. **Gate 硬阻断**：这是核心功能，未通过 Gate 绝对不能进入下一阶段
2. **自动跳过**：如果阶段的 `enabled_condition` 不满足，自动跳过并检查下一阶段
3. **模板创建**：只创建必要的模板文件，不覆盖已存在的文件
4. **进度同步**：自动更新 `90_PROGRESS_LOG.yaml` 的所有相关字段

## 关联工具

- `/check-gate` - 检查 Gate 状态
- `/approve-gate` - 审批 Gate
- `gate_checker` skill - Gate 检查的核心实现
- `/check-progress` - 查看详细进度
- `/iresume` - 恢复工作上下文
