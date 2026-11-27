# /check-gate - 检查 Phase Gate 状态

你是一个 AI 协作开发助手。用户请求检查 Phase Gate 状态。

## 参数

- `$ARGUMENTS`：功能模块名称（或空），可选参数 `--phase=N`

## 用法

```
# Foundation Gate (Phase 0)
/check-gate --phase=0                   # 检查项目 Foundation Gate

# Feature Gate (Phase 1-7)
/check-gate {feature-name}              # 检查功能模块所有 Phase 的 Gate
/check-gate {feature-name} --phase=1    # 只检查 Phase 1 的 Gate
/check-gate {feature-name} --phase=2    # 只检查 Phase 2 的 Gate
```

## 执行步骤

### 1. 解析参数

```
解析参数：
  feature = 第一个参数（可选，当 phase=0 时不需要）
  phase = --phase 参数值（可选）

如果 phase == 0：
  # Foundation Gate 模式，不需要 feature 参数
  跳转到 Step 2a

如果 feature 为空且 phase != 0：
  提示：
    请提供功能名称，例如：/check-gate user-auth
    或检查 Foundation Gate：/check-gate --phase=0
```

### 2a. Foundation Gate 检查 (Phase 0)

```
检查文件是否存在：
  - docs/_foundation/FOUNDATION_GATE_STATUS.yaml

如果文件不存在，提示：
  ❌ 项目 Foundation 尚未初始化

  请先运行以下命令初始化：
  /init-project

# 读取状态
status = 读取 docs/_foundation/FOUNDATION_GATE_STATUS.yaml

# Foundation Gate 检查项
foundation_checks:
  - id: planning_docs_exist
    description: "_planning/ 目录下的规划文档必须存在"
    check: 检查以下文件是否存在
      - docs/_foundation/_planning/01_USER_JOURNEY.md
      - docs/_foundation/_planning/02_ARCHITECTURE.md
      - docs/_foundation/_planning/03_MODULE_DECOMPOSITION.md
      - docs/_foundation/_planning/04_ROADMAP.md
    severity: block

  - id: user_journey_filled
    description: "用户旅程文档必须填写核心内容"
    check: 01_USER_JOURNEY.md 中不包含 "{请" 或 "{用户" 等占位符
    severity: block

  - id: architecture_filled
    description: "架构文档必须填写技术选型"
    check: 02_ARCHITECTURE.md 包含技术栈定义
    severity: block

  - id: module_decomposition_filled
    description: "模块划分必须定义功能列表"
    check: 03_MODULE_DECOMPOSITION.md 包含 module_id 定义
    severity: block

  - id: roadmap_has_milestones
    description: "路线图必须定义里程碑"
    check: 04_ROADMAP.md 包含 M0/M1 等里程碑定义
    severity: warn

跳转到 Step 6a 输出 Foundation 结果
```

### 2b. Feature Gate 检查 (Phase 1-7)

```
检查目录是否存在：docs/{feature}/
检查文件是否存在：
  - docs/{feature}/PHASE_GATE.yaml
  - docs/{feature}/PHASE_GATE_STATUS.yaml

如果文件不存在，提示：
  ❌ 功能模块 "{feature}" 未启用 Gate 机制

  请先运行以下命令初始化 Gate 文件：
  按 /new-feature 的 Gate 文件生成步骤补齐缺失文件；已存在的规则或状态不得覆盖。

  或重新创建功能模块：
  /new-feature {feature}
```

### 3. 读取配置和状态

```yaml
# 读取规则配置
config = 读取 docs/{feature}/PHASE_GATE.yaml

# 读取运行状态
status = 读取 docs/{feature}/PHASE_GATE_STATUS.yaml

# 获取 feature_profile
feature_profile = config.feature_profile
```

### 4. 确定检查范围

```
如果指定了 --phase：
  只检查该 phase
否则：
  检查所有 phase（phase_1 到 phase_7）
```

### 5. 执行 Gate 检查（内置逻辑）

对每个需要检查的 Phase，执行以下检查逻辑：

```
Gate 检查流程：
1. 读取 PHASE_GATE.yaml 中该 phase 的规则配置
2. 检查 required_outputs 是否存在
3. 执行 quality_checks（content_check, yaml_check, manual 等）
4. 检查 approvals 是否满足
5. 汇总结果，确定 gate_state (passed | blocked | pending)
6. 更新 PHASE_GATE_STATUS.yaml 的 last_check 字段
```

**检查类型说明**：

兼容说明：对 exec_check、test_check、e2e_check 等细化检查，显式读取已保留的 `.claude/skills/gate_checker.md` 作为 V3 规则素材；不要假定旧平铺文件会被当前 CLI 原生自动加载。这个 V3 命令仍不是 V4 可信证据执行器，未执行的测试必须标未测，不能自报 passed。

| 类型 | 说明 | 执行方式 |
|------|------|----------|
| `content_check` | 检查文件内容是否包含关键字 | 读取文件，搜索 anchor 模式 |
| `yaml_check` | 检查 YAML 字段值 | 读取 YAML，验证字段 |
| `manual` | 人工检查项 | 标记为待人工确认 |
| `serve_check` | 启动服务检查 | 执行命令，验证健康检查 |
| `code_scan` | 扫描代码模式 | 搜索指定模式 |

### 6a. Foundation Gate 输出

```
📋 Foundation Gate 检查结果

项目: {project_name}
阶段: Phase 0 Foundation
检查时间: {datetime}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
状态: {✅ PASSED | ❌ BLOCKED | ⏳ PENDING}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 规划文档:
  {✅|❌} _planning/01_USER_JOURNEY.md
  {✅|❌} _planning/02_ARCHITECTURE.md
  {✅|❌} _planning/03_MODULE_DECOMPOSITION.md
  {✅|❌} _planning/04_ROADMAP.md
  {✅|❌} _planning/05_TECH_DECISIONS.md

📊 质量检查:
  {✅|❌} user_journey_filled - 用户旅程已填写
  {✅|❌} architecture_filled - 架构文档已填写
  {✅|❌} module_decomposition_filled - 模块划分已定义
  {✅|⚠️} roadmap_has_milestones - 里程碑已定义

✍️ 审批状态:
  {✅|⏳} PM: {user} ({datetime})
  {✅|⏳} Architect: {user} ({datetime})

{如果 blocked}
🚫 阻断原因:
{列出阻断原因}

📝 建议操作:
{列出下一步操作}
```

### 6b. Feature Gate 输出

#### 单个 Phase 检查结果

```
📋 Phase Gate 检查结果

功能模块: {feature}
阶段: Phase {N} {Name}
检查时间: {datetime}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
状态: {✅ PASSED | ❌ BLOCKED | ⏳ PENDING | ⏭️ SKIPPED}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 必需产出物:
{列出每个 required_output 的状态}

📊 质量检查:
{列出每个 quality_check 的结果}

✍️ 审批状态:
{列出每个角色的审批状态}

{如果 blocked}
🚫 阻断原因:
{列出阻断原因}

📝 建议操作:
{列出下一步操作}
```

#### 全部 Phase 概览

```
📋 Phase Gate 状态概览：{feature}

检查时间: {datetime}

Phase 0 (Foundation): {状态图标} {状态文字}  ← 项目级别
─────────────────────────────────────────────
Phase 1 (Kickoff):  {状态图标} {状态文字}
Phase 2 (Spec):     {状态图标} {状态文字}
Phase 3 (Demo):     {状态图标} {状态文字}
Phase 4 (Design):   {状态图标} {状态文字}
Phase 5 (Code):     {状态图标} {状态文字}
Phase 6 (Test):     {状态图标} {状态文字}
Phase 7 (Deploy):   {状态图标} {状态文字}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

当前阻断点: {第一个 blocked 的 Phase，或 "无"}
责任角色: {待审批角色}

{如果有 blocked}
📝 建议操作:
{列出修复建议}
```

### 7. 状态图标说明

| 状态 | 图标 | 文字 |
|------|------|------|
| `passed` | ✅ | Passed |
| `blocked` | ❌ | Blocked |
| `pending` | ⏳ | Pending |
| `skipped` | ⏭️ | Skipped |
| 前置阶段未通过 | 🔒 | Locked |

**Locked 规则**：如果前一个非 skipped 的 Phase 未 passed，当前 Phase 显示为 Locked。

## 输出示例

### 示例 1：检查 Foundation Gate

```
/check-gate --phase=0
```

输出：

```
📋 Foundation Gate 检查结果

项目: my-project
阶段: Phase 0 Foundation
检查时间: 2024-12-15T10:00:00

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
状态: ❌ BLOCKED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 规划文档:
  ✅ _planning/01_USER_JOURNEY.md
  ✅ _planning/02_ARCHITECTURE.md
  ❌ _planning/03_MODULE_DECOMPOSITION.md (未填写)
  ✅ _planning/04_ROADMAP.md
  ✅ _planning/05_TECH_DECISIONS.md

📊 质量检查:
  ✅ user_journey_filled - 用户旅程已填写
  ✅ architecture_filled - 架构文档已填写
  ❌ module_decomposition_filled - 模块划分未定义
  ✅ roadmap_has_milestones - 里程碑已定义

✍️ 审批状态:
  ⏳ PM: 待审批
  ⏳ Architect: 待审批

🚫 阻断原因:
  1. 03_MODULE_DECOMPOSITION.md 未填写功能模块列表

📝 建议操作:
  1. 填写 docs/_foundation/_planning/03_MODULE_DECOMPOSITION.md
  2. 定义功能模块列表（module_id, feature_name, scope 等）
  3. 执行 /approve-gate --phase=0 --role=PM
```

### 示例 2：Foundation Gate 通过

```
📋 Foundation Gate 检查结果

项目: my-project
阶段: Phase 0 Foundation
检查时间: 2024-12-15T14:00:00

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
状态: ✅ PASSED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 规划文档:
  ✅ _planning/01_USER_JOURNEY.md
  ✅ _planning/02_ARCHITECTURE.md
  ✅ _planning/03_MODULE_DECOMPOSITION.md
  ✅ _planning/04_ROADMAP.md
  ✅ _planning/05_TECH_DECISIONS.md

📊 质量检查:
  ✅ user_journey_filled - 用户旅程已填写
  ✅ architecture_filled - 架构文档已填写
  ✅ module_decomposition_filled - 模块划分已定义
  ✅ roadmap_has_milestones - 里程碑已定义

✍️ 审批状态:
  ✅ PM: alice (2024-12-15T13:00:00)
  ✅ Architect: bob (2024-12-15T14:00:00)

🎉 Foundation Gate 已通过！

📝 下一步操作:
  执行 /plan-features 批量生成功能模块
```

### 示例 3：检查 Feature 单个 Phase

```
/check-gate user-auth --phase=2
```

输出：

```
📋 Phase Gate 检查结果

功能模块: user-auth
阶段: Phase 2 Spec
检查时间: 2024-12-15T11:00:00

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
状态: ❌ BLOCKED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 必需产出物:
  ✅ 21_UI_FLOW_SPEC.md - 存在

📊 质量检查:
  ✅ spec_has_pages - SPEC 包含页面定义
  ❌ spec_has_error_cases - SPEC 未定义错误处理
  ⚠️ spec_has_edge_cases - 建议补充边界条件

✍️ 审批状态:
  ✅ PM: alice (2024-12-15T10:00:00)
  ⏳ Architect: 待审批

🚫 阻断原因:
  1. 质量检查失败: SPEC 未定义错误处理

📝 建议操作:
  1. 在 21_UI_FLOW_SPEC.md 中添加「错误处理」章节
  2. 请 Architect 审批
```

### 示例 4：检查 Feature 所有 Phase

```
/check-gate user-auth
```

输出：

```
📋 Phase Gate 状态概览：user-auth

检查时间: 2024-12-15T11:00:00

Phase 0 (Foundation): ✅ Passed (项目级别)
─────────────────────────────────────────────
Phase 1 (Kickoff):  ✅ Passed
Phase 2 (Spec):     ❌ Blocked
                    └─ 原因: SPEC 未定义错误处理
Phase 3 (Demo):     🔒 Locked (等待 Phase 2)
Phase 4 (Design):   🔒 Locked
Phase 5 (Code):     🔒 Locked
Phase 6 (Test):     🔒 Locked
Phase 7 (Deploy):   🔒 Locked

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

当前阻断点: Phase 2 Spec
责任角色: Architect

📝 建议操作:
  1. 补充 21_UI_FLOW_SPEC.md 的错误处理章节
  2. 执行 /approve-gate user-auth --phase=2 --role=Architect
```

## 注意事项

1. **Phase 0 是项目级别**：Foundation Gate 检查 `docs/_foundation/`，与 feature 无关
2. **Phase 1-7 是功能级别**：检查 `docs/{feature}/` 下的文件
3. **自动更新状态**：执行检查会自动更新状态文件的 `last_check` 字段
4. **不修改 passed**：此命令不会将 `gate_state` 设置为 `passed`，需要使用 `/approve-gate`
5. **Locked 状态**：不是实际的 `gate_state`，只是显示用途

## 关联工具

- `/approve-gate` - 在检查通过后审批 Gate
- `/next-phase` - 在进入下一阶段前自动调用此命令
- `/new-feature` - 创建功能模块，生成 Gate 文件
- `/init-project` - 初始化 Foundation，生成 Phase 0 所需文件
- `/plan-features` - Foundation Gate 通过后，批量生成功能模块
