# /expert-review - 执行专家评审

你是一个 AI 协作开发助手。用户请求对功能模块执行独立的专家评审。

## 参数

- `$ARGUMENTS`：功能模块路径，可选参数 `--phase=N`、`--target=FILE`、`--model=MODEL`、`--dry-run`

## 用法

```
/expert-review docs/user-auth
/expert-review docs/user-auth --phase=4
/expert-review docs/user-auth --phase=4 --target=40_DESIGN_FINAL.md
/expert-review docs/user-auth --dry-run
```

## 执行步骤

### 1. 解析参数

```
如果 $ARGUMENTS 为空，提示：
  请提供功能路径，例如：/expert-review docs/user-auth
  或指定阶段：/expert-review docs/user-auth --phase=4

解析参数：
  feature_path = 第一个参数（如 docs/user-auth）
  phase = --phase 参数值（可选）
  target = --target 参数值（可选）
  model = --model 参数值（默认 gpt-4.1）
  dry_run = --dry-run 是否存在
```

### 2. 验证功能目录存在

```
检查目录是否存在：{feature_path}/
检查文件是否存在：{feature_path}/90_PROGRESS_LOG.yaml

如果不存在，提示：
  ❌ 功能目录 "{feature_path}" 不存在

  请检查路径是否正确，或使用以下命令创建：
  /new-feature {feature_name}
```

### 3. 确定评审阶段和目标文件

```
如果未指定 --phase：
  读取 {feature_path}/90_PROGRESS_LOG.yaml
  phase = meta.current_phase

如果未指定 --target：
  根据 phase 自动选择：
    Phase 1 → 10_CONTEXT.md
    Phase 2 → 20_API_SPEC.md（如果存在）或 21_UI_FLOW_SPEC.md
    Phase 4 → 40_DESIGN_FINAL.md
    Phase 5 → 询问用户指定文件
    Phase 6 → 60_TEST_PLAN.md

检查目标文件是否存在：{feature_path}/{target}
如果不存在，提示错误并退出
```

### 4. 读取目标文件内容

```
读取：{feature_path}/{target}
如果文件过大（>50000 字符）：
  提示：文件过大，建议拆分评审或使用 --target 指定具体章节
```

### 5. 构建评审 Prompt

```markdown
你是一个独立的第三方专家评审员。你的职责是评审 AI 协作开发项目中的设计文档。

## 评审原则

1. **独立性**：你与设计方（Claude）完全独立，必须客观公正
2. **可执行性**：每个问题必须有明确、可执行的修复建议
3. **硬规则优先**：以下情况必须 BLOCK：
   - Gate 可被绕过
   - 状态/配置混写
   - 审批形同虚设
   - 设计无法被测试验证
   - 存在安全风险

## 评审阶段

当前阶段：Phase {phase}
评审重点：
- Phase 1 (Kickoff): Context 完整性、目标清晰度、边界定义
- Phase 2 (Spec): 接口契约、错误处理、边界条件
- Phase 4 (Design): 架构合理性、可测试性、安全性
- Phase 5 (Code): 代码与设计一致性、实现质量
- Phase 6 (Test): 测试覆盖率、测试有效性

## 被评审文档

```
{document_content}
```

## 输出格式

请严格按照以下 YAML 格式输出：

```yaml
verdict: GO | REVISE | BLOCK
summary:
  total_issues: N
  block_count: N
  warn_count: N
actions:
  - id: "MUST-001"
    severity: block | warn
    category: design | security | testability | clarity | consistency
    target: "{file_name}"
    location: "{section/line}"
    issue: "{one-line description}"
    evidence: "{quote from document}"
    impact: "{impact scope}"
    fix: "{actionable fix suggestion}"
    owner_role: PM | Architect | Developer | QA
```

## 判定规则

- **GO**: 无 block 级问题，warn 级问题 ≤ 3
- **REVISE**: 无 block 级问题，warn 级问题 > 3
- **BLOCK**: 存在任意 block 级问题
```

### 6. 执行评审（调用 OpenAI API）

**如果 --dry-run**：
```
📝 Dry Run 模式 - 仅显示 Prompt

功能：{feature_path}
阶段：Phase {phase}
目标：{target}
模型：{model}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Prompt 内容：
{prompt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 移除 --dry-run 参数以执行实际评审
```

**否则，调用 openai_expert_review skill**：

```
使用 openai_expert_review skill：
- prompt: {构建的 Prompt}
- model: {model}

如果 API Key 未配置：
  ❌ OPENAI_API_KEY 未配置

  请在环境变量或 .env 文件中配置：
  export OPENAI_API_KEY="your-api-key"

如果 API 调用失败：
  ❌ API 调用失败

  错误：{error_message}

  请检查：
  1. API Key 是否有效
  2. 网络连接是否正常
  3. 模型名称是否正确
```

### 7. 解析响应并生成输出文件

```
从 API 响应中提取 YAML 块
验证格式正确性

生成 REVIEW_ACTIONS.yaml：
  {feature_path}/REVIEW_ACTIONS.yaml

生成 REVIEW_REPORT.md：
  {feature_path}/REVIEW_REPORT.md
```

### 8. 更新 Gate 状态（如果 verdict=BLOCK）

```
如果 verdict == "BLOCK"：
  提示：External Gate 被阻断
  /next-phase 命令将被拒绝
```

### 9. 输出结果

#### verdict = GO

```
✅ Expert Review PASSED

功能：{feature_path}
阶段：Phase {phase}
评审文件：{target}
评审时间：{datetime}
评审模型：{model}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 问题统计：
  Block: 0
  Warn:  {warn_count}
  Total: {total_issues}

📁 输出文件：
  ✅ {feature_path}/REVIEW_ACTIONS.yaml
  ✅ {feature_path}/REVIEW_REPORT.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✔ 可以继续下一阶段
  执行：/next-phase {feature_name}
```

#### verdict = REVISE

```
⚠️ Expert Review - REVISE RECOMMENDED

功能：{feature_path}
阶段：Phase {phase}
评审文件：{target}
评审时间：{datetime}
评审模型：{model}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 问题统计：
  Block: 0
  Warn:  {warn_count}
  Total: {total_issues}

⚠️ Warn 级问题：
{列出 warn 级问题摘要}

📁 输出文件：
  ✅ {feature_path}/REVIEW_ACTIONS.yaml
  ✅ {feature_path}/REVIEW_REPORT.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 建议修复 warn 级问题后继续
  查看详情：{feature_path}/REVIEW_ACTIONS.yaml

  或直接继续：/next-phase {feature_name}
```

#### verdict = BLOCK

```
⛔ Expert Review BLOCKED

功能：{feature_path}
阶段：Phase {phase}
评审文件：{target}
评审时间：{datetime}
评审模型：{model}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 问题统计：
  Block: {block_count}
  Warn:  {warn_count}
  Total: {total_issues}

🚫 Block 级问题：
{列出 block 级问题摘要}

📁 输出文件：
  ✅ {feature_path}/REVIEW_ACTIONS.yaml
  ✅ {feature_path}/REVIEW_REPORT.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⛔ External Gate 已阻断
  /next-phase 命令将被拒绝

📝 下一步操作：
  1. 查看详细问题：{feature_path}/REVIEW_ACTIONS.yaml
  2. 修复所有 block 级问题
  3. 重新执行评审：/expert-review {feature_path}
```

## 输出文件模板

评审完成后，使用以下模板生成输出文件：

| 模板文件 | 输出文件 | 说明 |
|---------|---------|------|
| `CC_COLLABORATION/03_templates/_shared/REVIEW_ACTIONS_TEMPLATE.yaml` | `{feature_path}/REVIEW_ACTIONS.yaml` | 结构化评审结果（机器可读） |
| `CC_COLLABORATION/03_templates/_shared/REVIEW_REPORT_TEMPLATE.md` | `{feature_path}/REVIEW_REPORT.md` | 评审报告（人类可读） |

### 模板使用说明

1. 读取模板文件
2. 替换 `{{变量}}` 占位符为实际值
3. 写入到功能目录下

### 变量映射

| 变量 | 来源 | 示例 |
|------|------|------|
| `{{feature}}` | 功能名称 | `expert-reviewer` |
| `{{phase}}` | 当前阶段 | `4` |
| `{{target_file}}` | 被评审文件 | `40_DESIGN_FINAL.md` |
| `{{reviewed_at}}` | 评审时间 | `2024-12-16T10:00:00` |
| `{{model}}` | 评审模型 | `gpt-4o` |
| `{{verdict}}` | 评审结论 | `GO` / `REVISE` / `BLOCK` |
| `{{total_issues}}` | 问题总数 | `5` |
| `{{block_count}}` | Block 数量 | `0` |
| `{{warn_count}}` | Warn 数量 | `5` |

## 注意事项

1. **API Key 必需**：需要配置 OPENAI_API_KEY 环境变量
2. **权威来源**：REVIEW_ACTIONS.yaml 是 Gate 判定的唯一依据
3. **CLI 非权威**：本命令的输出仅供人类参考
4. **成本提醒**：每次评审会消耗 OpenAI API 配额

## 关联工具

- `expert_reviewer` - 此命令调用的 Subagent
- `openai_expert_review` - 执行 API 调用的 Skill
- `/check-gate` - 检查 Gate 状态
- `/next-phase` - 进入下一阶段
