# Phase Gate System 用户指南

> 版本：v1.0
> 最后更新：2024-12-15
> 适用范围：ai-coding-template 框架

---

## 目录

1. [什么是 Phase Gate](#1-什么是-phase-gate)
2. [核心概念](#2-核心概念)
3. [快速入门](#3-快速入门)
4. [命令参考](#4-命令参考)
5. [常见问题与解决方案](#5-常见问题与解决方案)
6. [最佳实践](#6-最佳实践)

---

## 1. 什么是 Phase Gate

### 1.1 背景问题

在软件开发中，我们经常遇到这样的问题：

- Phase UI 显示"完成"了，但实际产出物不完整
- 开发人员跳过了关键的设计评审就开始写代码
- 测试没做完就急着上线
- 出了问题追溯不到是哪个环节出的问题

**根本原因**：流程"完成" ≠ 阶段"可交接"

### 1.2 Phase Gate 是什么

Phase Gate 是一个**阶段准入控制机制**：

```
┌─────────┐    Gate    ┌─────────┐    Gate    ┌─────────┐
│ Phase 1 │───────────►│ Phase 2 │───────────►│ Phase 3 │
│ Kickoff │  必须通过   │  Spec   │  必须通过   │  Demo   │
└─────────┘            └─────────┘            └─────────┘
```

**核心规则**：未通过当前阶段的 Gate，系统禁止进入下一阶段。

### 1.3 Phase Gate 的价值

| 价值点 | 说明 |
|--------|------|
| 交接质量保障 | 每个阶段必须产出完整才能交接 |
| 问题前置发现 | 在早期阶段发现问题，降低返工成本 |
| 责任可追溯 | 每次检查、审批都有记录 |
| AI 可判断 | AI Agent 能基于 Gate 状态做决策 |

---

## 2. 核心概念

### 2.1 Gate 状态

| 状态 | 图标 | 含义 | 能否进入下一阶段 |
|------|------|------|-----------------|
| `pending` | ⏳ | 未检查 / 等待审批 | ❌ 不能 |
| `blocked` | ❌ | 检查不通过 | ❌ 不能 |
| `passed` | ✅ | 检查通过 + 审批完成 | ✅ 可以 |
| `skipped` | ⏭️ | 阶段被跳过（条件不满足） | ✅ 可以（跳过） |

### 2.2 Gate 检查内容

每个 Phase 的 Gate 包含三类检查：

#### 1. 必需产出物（required_outputs）

```yaml
required_outputs:
  - path: "10_CONTEXT.md"      # 必须存在这个文件
    required: true
  - path: "21_UI_FLOW_SPEC.md"
    required: true
    condition: "feature_profile.has_ui == true"  # 条件检查
```

#### 2. 质量检查（quality_checks）

```yaml
quality_checks:
  - id: context_has_goals
    description: "Context 必须明确功能目标"
    type: content_check
    target: "10_CONTEXT.md"
    anchor: "目标|Goals"
    min_items: 2              # 至少 2 条目标
    severity: block           # block = 必须通过；warn = 仅警告
```

#### 3. 审批要求（approvals）

```yaml
approvals:
  required_roles:
    - PM                      # 需要 PM 审批
    - Architect               # 需要架构师审批
```

### 2.3 文件结构

每个功能模块包含两个 Gate 相关文件：

```
docs/{feature-name}/
├── PHASE_GATE.yaml           # 规则配置（很少修改）
├── PHASE_GATE_STATUS.yaml    # 运行状态（系统自动更新）
├── 10_CONTEXT.md
├── 90_PROGRESS_LOG.yaml
└── ...
```

| 文件 | 职责 | 谁来修改 |
|------|------|---------|
| `PHASE_GATE.yaml` | 定义 Gate 规则 | 项目初始化时设置，一般不改 |
| `PHASE_GATE_STATUS.yaml` | 记录检查结果和审批状态 | 系统自动更新，禁止手动修改 |

---

## 3. 快速入门

### 3.1 创建新功能模块

```bash
# 执行命令
/new-feature user-auth
```

系统会自动创建：
- `docs/user-auth/10_CONTEXT.md` - 功能上下文（需要你填写）
- `docs/user-auth/90_PROGRESS_LOG.yaml` - 进度日志
- `docs/user-auth/PHASE_GATE.yaml` - Gate 规则配置
- `docs/user-auth/PHASE_GATE_STATUS.yaml` - Gate 运行状态

### 3.2 完整工作流程

```
┌──────────────────────────────────────────────────────────────┐
│                    Phase Gate 工作流程                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1. 编写内容                                                  │
│     └─ 填写 10_CONTEXT.md、编写代码等                         │
│                         ↓                                    │
│  2. 检查 Gate                                                │
│     └─ /check-gate user-auth --phase=1                      │
│                         ↓                                    │
│          ┌─────────────┴─────────────┐                       │
│          ↓                           ↓                       │
│     ❌ blocked                   ⏳ pending                   │
│     └─ 根据提示修复              └─ 检查通过，等待审批         │
│     └─ 返回步骤 1                          ↓                 │
│                                                              │
│  3. 申请审批                                                  │
│     └─ /approve-gate user-auth --phase=1 --role=PM          │
│                         ↓                                    │
│                    ✅ passed                                  │
│                         ↓                                    │
│  4. 进入下一阶段                                              │
│     └─ /next-phase user-auth                                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 3.3 实际操作示例

#### 场景：完成 Kickoff 阶段，进入 Spec 阶段

**Step 1**：编写 10_CONTEXT.md，确保包含：
- 至少 2 条目标
- 至少 1 条 Non-Goals（不做什么）
- 验收标准

**Step 2**：检查 Gate 状态
```bash
/check-gate user-auth --phase=1
```

**如果 blocked**，会看到类似输出：
```
📋 Phase Gate 检查结果

状态: ❌ BLOCKED

📊 质量检查:
  ❌ context_has_goals - 目标数量不足（当前 1 条，要求至少 2 条）
  ❌ context_has_non_goals - 缺少 Non-Goals 章节

📝 建议操作:
  1. 在 10_CONTEXT.md 中添加更多目标
  2. 添加"不包含内容"或"Out of Scope"章节
```

→ 根据提示修复后，再次执行 `/check-gate`

**如果 pending**（检查通过，等待审批）：
```
📋 Phase Gate 检查结果

状态: ⏳ PENDING

📊 质量检查:
  ✅ context_has_goals - 包含功能目标（3 条）
  ✅ context_has_non_goals - 包含 Non-Goals（2 条）

✍️ 审批状态:
  ⏳ PM: 待审批

📝 下一步:
  请 PM 审批
```

**Step 3**：申请审批
```bash
/approve-gate user-auth --phase=1 --role=PM --user=alice
```

输出：
```
✅ 审批成功！

Phase 1 Kickoff Gate 已通过
审批人: alice (PM)
审批时间: 2024-12-15T14:15:00

可以执行 /next-phase user-auth 进入下一阶段
```

**Step 4**：进入下一阶段
```bash
/next-phase user-auth
```

输出：
```
✅ 成功进入 Phase 2 Spec

已更新:
• current_phase: 1 → 2
• phase_1_kickoff.status: wip → done
• phase_2_spec.status: pending → wip

下一步:
• 编写 21_UI_FLOW_SPEC.md（如果是 UI 功能）
• 或 20_API_SPEC.md（如果是纯后端功能）
```

---

## 4. 命令参考

### 4.1 /check-gate

**功能**：检查指定功能模块的 Gate 状态

**用法**：
```bash
/check-gate {feature-name}              # 检查所有 Phase 的 Gate
/check-gate {feature-name} --phase=1    # 只检查指定 Phase 的 Gate
/check-gate {feature-name} --phase=kickoff  # 也可以用阶段名称
```

**输出说明**：

| 符号 | 含义 |
|------|------|
| ✅ | 检查通过 |
| ❌ | 检查失败（severity=block） |
| ⚠️ | 警告（severity=warn，不阻断） |
| ⏭️ | 跳过（条件不满足） |
| 🔒 | 锁定（等待前置 Gate 通过） |

---

### 4.2 /approve-gate

**功能**：对指定 Phase 进行审批

**用法**：
```bash
/approve-gate {feature-name} --phase=1 --role=PM --user=alice
```

**参数说明**：

| 参数 | 必需 | 说明 |
|------|------|------|
| feature-name | 是 | 功能模块名称 |
| --phase | 是 | Phase 编号（1-7）或名称 |
| --role | 是 | 审批角色（PM / Architect / Developer / QA） |
| --user | 否 | 审批人姓名（默认为当前用户） |

**前置条件**：
- 所有 severity=block 的检查必须通过
- 如果有检查失败，审批会被拒绝

**错误处理**：
```
❌ 无法审批：存在未通过的 Block 级检查

失败的检查项：
• context_has_goals: 目标数量不足
• context_has_non_goals: 缺少 Non-Goals 章节

请先执行 /check-gate 查看详情并修复
```

---

### 4.3 /next-phase

**功能**：进入下一开发阶段

**用法**：
```bash
/next-phase {feature-name}
```

**行为**：
1. 检查当前 Phase 的 Gate 状态
2. 如果 Gate = passed 或 skipped → 允许进入下一阶段
3. 如果 Gate = pending 或 blocked → 拒绝，显示原因

**错误处理**：
```
❌ 无法进入下一阶段

当前阶段: Phase 1 Kickoff
Gate 状态: blocked

阻断原因:
• 目标数量不足（当前 1 条，要求至少 2 条）

建议操作:
1. 修复以上问题
2. 执行 /check-gate user-auth --phase=1 重新检查
3. 请 PM 审批
```

---

### 4.4 /new-feature

**功能**：创建新功能模块（自动生成 Gate 文件）

**用法**：
```bash
/new-feature {feature-name}
```

**生成的文件**：
```
docs/{feature-name}/
├── 10_CONTEXT.md              # 功能上下文模板
├── 90_PROGRESS_LOG.yaml       # 进度日志
├── PHASE_GATE.yaml            # Gate 规则配置
├── PHASE_GATE_STATUS.yaml     # Gate 运行状态
└── _demos/                    # Demo 文件目录
    └── .gitkeep
```

**初始配置**：
- `feature_profile.has_ui = true`（默认有 UI）
- `feature_profile.demo_required = true`（默认需要 Demo）

如果是纯后端/工具类功能，可以修改 `PHASE_GATE.yaml`：
```yaml
feature_profile:
  has_ui: false           # 无 UI
  demo_required: false    # 不需要 Demo
```

---

## 5. 常见问题与解决方案

### 5.1 Gate blocked 了怎么办？

**问题现象**：
```
状态: ❌ BLOCKED
阻断原因: 质量检查失败: Context 必须明确功能目标（当前 1 条，要求至少 2 条）
```

**解决步骤**：
1. 阅读 `blocked_reason` 了解具体原因
2. 根据提示修复对应文件（如补充目标）
3. 重新执行 `/check-gate` 验证修复
4. 如果通过，再申请审批

**常见阻断原因及修复**：

| 原因 | 修复方法 |
|------|---------|
| 目标数量不足 | 在"目标"章节补充更多目标（至少 2 条） |
| 缺少 Non-Goals | 添加"不包含内容"或"Out of Scope"章节 |
| 缺少验收标准 | 添加"验收标准"或"Acceptance Criteria"章节 |
| 缺少必需文件 | 创建对应文件（如 21_UI_FLOW_SPEC.md） |

---

### 5.2 审批被拒绝怎么办？

**问题现象**：
```
❌ 无法审批：存在未通过的 Block 级检查
```

**解决方法**：
1. 执行 `/check-gate` 查看哪些检查失败
2. 修复所有 severity=block 的检查项
3. 再次执行 `/check-gate` 确认通过
4. 然后再申请审批

**注意**：审批前会自动执行检查，不能绕过。

---

### 5.3 如何跳过某个阶段？

**方法 1**：修改 feature_profile（推荐）

如果是因为功能类型不需要某个阶段（如纯后端不需要 Demo）：

编辑 `PHASE_GATE.yaml`：
```yaml
feature_profile:
  has_ui: false           # 设为 false
  demo_required: false    # 设为 false
```

然后执行 `/check-gate`，该阶段会显示为 `skipped`。

**方法 2**：直接设置 skipped（不推荐）

> ⚠️ 不建议手动修改 PHASE_GATE_STATUS.yaml

如果确实需要手动跳过，需要有正当理由并记录在 PROGRESS_LOG 中。

---

### 5.4 check_history 太长了怎么办？

每次执行 `/check-gate` 都会在 `check_history` 中追加一条记录。

**V1 设计**：全部保留，不会自动清理。

**建议**：
- 正常使用不需要担心，文件大小通常不会成为问题
- 如果确实太长（>100 条），可以手动清理历史记录，只保留最近 10 条

---

### 5.5 如何查看 Gate 检查的详细证据？

执行 `/check-gate` 后，检查 `PHASE_GATE_STATUS.yaml` 文件：

```yaml
last_check:
  check_results:
    - id: context_has_goals
      passed: true
      message: "✅ 包含功能目标（3 条）"
      evidence:
        location: "10_CONTEXT.md:17-21"    # 匹配位置
        matched: "- **目标 1**：..."        # 匹配内容
        found_count: 3                     # 找到数量
        required_count: 2                  # 要求数量
```

---

### 5.6 Gate 状态文件被意外修改了怎么办？

`PHASE_GATE_STATUS.yaml` 的 `gate_state` 字段只能由系统写入。

如果发现状态不一致：
1. 执行 `/check-gate` 重新检查，系统会更新状态
2. 如果需要回滚到 pending，删除对应的 approvals 记录

---

## 6. 最佳实践

### 6.1 Gate 检查频率

| 时机 | 建议 |
|------|------|
| 每次重大修改后 | 执行 `/check-gate` 验证 |
| 提交代码前 | 确保当前阶段 Gate 状态正常 |
| 申请审批前 | 先执行 `/check-gate` 自检 |

### 6.2 审批流程

1. **开发者自检**：先执行 `/check-gate` 确保所有检查通过
2. **申请审批**：通知对应角色（PM/Architect）进行审批
3. **审批确认**：审批人执行 `/approve-gate` 记录审批

### 6.3 文档内容建议

为了顺利通过 Gate 检查，建议在文档中：

| 文档 | 必须包含 |
|------|---------|
| 10_CONTEXT.md | 至少 2 条目标、至少 1 条 Non-Goals、验收标准 |
| 21_UI_FLOW_SPEC.md | 页面列表（用 ## 1. 格式）、错误处理章节 |
| 40_DESIGN_FINAL.md | API 接口定义 |

### 6.4 团队协作

1. **PM**：负责 Kickoff 和 Deploy 阶段的审批
2. **Architect**：负责 Spec 和 Design 阶段的审批
3. **Developer**：负责 Code 阶段的审批（自检）
4. **QA**：负责 Test 阶段的审批

---

## 附录

### A. Phase 与 Gate 对照表

| Phase | 名称 | required_outputs | 主要 quality_checks | 审批角色 |
|-------|------|-----------------|-------------------|---------|
| 1 | Kickoff | 10_CONTEXT.md, 90_PROGRESS_LOG.yaml | 目标≥2、Non-Goals≥1 | PM |
| 2 | Spec | 21_UI_FLOW_SPEC.md 或 20_API_SPEC.md | 页面/端点列表、错误处理 | Architect, PM |
| 3 | Demo | _demos/*.vue | Demo 可运行、已评审 | PM |
| 4 | Design | 40_DESIGN_FINAL.md | API 定义 | Architect |
| 5 | Code | 50_DEV_PLAN.md, 90_PROGRESS_LOG.yaml | 所有任务完成 | Developer, Architect |
| 6 | Test | 60_TEST_PLAN.md, 61_TEST_REPORT.md | 无 P0 Bug | QA |
| 7 | Deploy | 70_RELEASE_NOTE.md | 版本号、变更列表 | PM |

### B. 常用命令速查

```bash
# 创建新功能
/new-feature {name}

# 检查 Gate
/check-gate {name}                 # 检查所有阶段
/check-gate {name} --phase=1       # 检查指定阶段

# 审批
/approve-gate {name} --phase=1 --role=PM --user=alice

# 进入下一阶段
/next-phase {name}

# 恢复工作上下文
/iresume {name}
```

---

## CHANGELOG

| 版本 | 日期 | 作者 | 变更内容 |
|------|------|------|----------|
| v1.0 | 2024-12-15 | Claude | 初始版本 |
