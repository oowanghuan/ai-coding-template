# /doc-design-validation - Foundation 文档设计验证

你是一个 AI 协作开发助手。用户请求对 Phase 0 Foundation 文档进行设计验证。

## 设计理念

> **"验证"而非"评审"**：本命令按用户步骤逐步"模拟执行"设计，
> 检查是否存在系统责任缺失、状态矛盾、用户流程断裂。
> 输出客观的 PASS/FAIL 结果，不输出主观意见。

## 参数

- `$ARGUMENTS`：可选参数 `--verbose`、`--step=U{N}`

## 用法

```bash
/doc-design-validation                      # 完整验证
/doc-design-validation --verbose            # 详细输出每一步验证过程
/doc-design-validation --step=U3            # 只验证指定步骤
```

---

## 1. 输入要求

### 1.1 必需文档

验证需要以下文档存在：

| 文档 | 路径 | 用途 |
|------|------|------|
| User Journey | `docs/_foundation/01_USER_JOURNEY.md` | 用户流程定义 |
| Architecture | `docs/_foundation/02_ARCHITECTURE.md` | 系统边界定义 |
| Module Decomposition | `docs/_foundation/03_MODULE_DECOMPOSITION.md` | 模块定义 |

### 1.2 前置检查

```
1. 检查上述 3 个文档是否存在
2. 如果任一不存在：
   ❌ 设计验证失败：缺少必需文档

   缺失文件：
   • {missing_files}

   请先完成 Foundation 文档
```

---

## 2. 验证规则

### 2.1 用户流程完整性检查

| 检查项 | 规则 | 级别 |
|--------|------|------|
| Happy Path 存在 | 至少包含 3 个用户步骤（U1, U2, U3...） | FAIL |
| 步骤连续性 | U{N} 之后必须有 U{N+1} 或明确的结束标志 | FAIL |
| 无死路 | 每个步骤都有明确的下一步或终点 | FAIL |
| 失败路径存在 | 至少包含 2 个失败场景（F1, F2...） | WARN |

### 2.2 系统责任完整性检查

| 检查项 | 规则 | 级别 |
|--------|------|------|
| 每步有责任 | 每个 U{N} 都有对应的「系统必须做」 | FAIL |
| 责任非空 | 「系统必须做」不能是空白或占位符 | FAIL |
| 失败有处理 | 每个 F{N} 都有对应的「系统处理」 | WARN |

### 2.3 模块映射完整性检查

| 检查项 | 规则 | 级别 |
|--------|------|------|
| P0 模块全映射 | 所有 P0 模块都出现在映射表中 | FAIL |
| 映射有效 | 映射表中的 Module ID 在 03_MODULE 中存在 | FAIL |
| 无孤立模块 | P0 模块不能没有对应的用户步骤 | FAIL |

### 2.4 边界一致性检查

| 检查项 | 规则 | 级别 |
|--------|------|------|
| 系统边界对齐 | 01_USER_JOURNEY 的系统边界与 02_ARCHITECTURE 一致 | WARN |
| 模块责任对齐 | 系统责任声明与 03_MODULE 的 scope 一致 | WARN |

---

## 3. 验证流程

### 3.1 逐步模拟执行

```
对于 Happy Path 中的每一步 U{N}：

1. 检查步骤定义
   - 用户动作是否明确？
   - 系统响应是否明确？
   - 成功标志是否明确？

2. 检查系统责任
   - 是否有对应的「系统必须做」？
   - 是否有对应的模块承接？

3. 检查状态转换
   - 从 U{N-1} 到 U{N} 是否有前置条件？
   - 前置条件是否被满足？

4. 检查失败分支
   - 在这一步可能发生什么失败？
   - 失败后系统如何处理？
   - 用户是否有恢复路径？
```

### 3.2 收集问题

```
对于每个检查项：
- FAIL 级别：记录为 blocking issue
- WARN 级别：记录为 warning

如果存在任何 FAIL 级别问题：
  整体结果 = FAIL
否则：
  整体结果 = PASS（可能带 warnings）
```

---

## 4. 输出格式

### 4.1 验证通过

```
✅ Doc Design Validation PASSED

验证时间：{datetime}
验证范围：{step_count} 个用户步骤

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 验证摘要：
  用户步骤：{N} 个（全部通过）
  失败路径：{N} 个（已覆盖）
  模块映射：{N} 个 P0 模块（全部映射）

⚠️ Warnings（{N} 个）：
{列出 WARN 级别问题}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✔ 设计验证通过，可以继续 Foundation Gate 检查
  执行：/check-gate --phase=0
```

### 4.2 验证失败

```
❌ Doc Design Validation FAILED

验证时间：{datetime}
验证范围：{step_count} 个用户步骤

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 问题摘要：
  FAIL：{N} 个
  WARN：{N} 个

🚫 FAIL 级别问题：

1. [流程断裂] U3 → U4
   位置：01_USER_JOURNEY.md / U3
   问题：U3 完成后没有明确的下一步指引
   建议：在 U3 的「成功标志」中明确下一步

2. [系统责任缺失] U4
   位置：01_USER_JOURNEY.md / §4.1
   问题：U4 没有对应的「系统必须做」
   建议：补充 U4 的系统责任声明

3. [模块未映射] M003 dashboard
   位置：01_USER_JOURNEY.md / §5.1
   问题：P0 模块 M003 未映射到任何用户步骤
   建议：确认 M003 支持哪个用户步骤，或调整优先级

⚠️ WARN 级别问题：
{列出 WARN 级别问题}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⛔ 设计验证失败，Foundation Gate 将被阻断

📝 下一步操作：
  1. 修复上述 FAIL 级别问题
  2. 重新执行：/doc-design-validation
  3. 通过后执行：/check-gate --phase=0
```

### 4.3 详细模式（--verbose）

```
📋 Doc Design Validation 详细报告

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 U1: 用户访问系统
  ├─ 用户动作：✅ 已定义
  ├─ 系统响应：✅ 已定义
  ├─ 成功标志：✅ 已定义
  ├─ 系统责任：✅ 已声明
  ├─ 模块映射：✅ M001 user-auth
  └─ 结果：PASS

🔍 U2: 用户登录
  ├─ 用户动作：✅ 已定义
  ├─ 系统响应：✅ 已定义
  ├─ 成功标志：✅ 已定义
  ├─ 系统责任：✅ 已声明
  ├─ 模块映射：✅ M001 user-auth
  ├─ 失败分支：✅ F1 登录失败（已覆盖）
  └─ 结果：PASS

🔍 U3: 用户创建内容
  ├─ 用户动作：✅ 已定义
  ├─ 系统响应：✅ 已定义
  ├─ 成功标志：⚠️ 缺少明确的下一步
  ├─ 系统责任：✅ 已声明
  ├─ 模块映射：✅ M002 content
  └─ 结果：WARN（建议补充下一步指引）

...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 5. 与 Foundation Gate 集成

### 5.1 Gate 规则

Doc Design Validation 结果会影响 Foundation Gate：

```yaml
# 00_FOUNDATION_GATE.md 检查项

design_validation:
  rule: "/doc-design-validation 结果为 PASS"
  level: BLOCK
  description: "设计必须通过验证才能进入开发"
```

### 5.2 状态记录

验证结果记录在 `docs/_foundation/DESIGN_VALIDATION_RESULT.yaml`：

```yaml
# DESIGN_VALIDATION_RESULT.yaml

meta:
  validated_at: "{datetime}"
  validator: "claude-code"

result: PASS | FAIL

summary:
  total_steps: {N}
  passed_steps: {N}
  failed_steps: {N}
  warnings: {N}

issues:
  - level: FAIL | WARN
    type: "流程断裂 | 责任缺失 | 模块未映射 | ..."
    location: "{file} / {section}"
    description: "{问题描述}"
    suggestion: "{修复建议}"
```

---

## 6. 注意事项

1. **这是"验证"不是"评审"**：只输出客观的检查结果，不评价设计质量
2. **FAIL 会阻断 Gate**：任何 FAIL 级别问题都会导致 Foundation Gate 被阻断
3. **WARN 不阻断但建议修复**：WARN 级别问题不阻断，但建议在进入开发前修复
4. **可重复执行**：每次执行会覆盖之前的验证结果

## 关联工具

- `/check-gate --phase=0` - 检查 Foundation Gate 状态
- `/plan-features` - 生成开发顺序清单（需要先通过设计验证）
