# doc_generator - 根据模板生成文档

## 能力描述

根据 `03_TEMPLATES/` 目录下的标准模板，生成任意阶段的文档。这是一个通用的文档生成工具，被多个 Slash Commands 和 Subagents 调用。

## 输入

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| template | string | 是 | 模板名称，如 `CONTEXT`, `DESIGN`, `TEST_PLAN` |
| feature | string | 是 | 功能模块名称 |
| output_path | string | 否 | 输出路径，默认按模板类型自动确定 |
| variables | object | 否 | 模板变量，用于填充模板中的占位符 |

## 输出

- 生成的文档文件
- 填充的变量列表
- 待补充的内容提示

## 支持的模板

| 模板名称 | 文件 | 输出位置 | 阶段 |
|---------|------|---------|------|
| `CONTEXT` | `CONTEXT_TEMPLATE.md` | `{feature}/00_CONTEXT.md` | Phase 1 |
| `CHANGELOG` | `CHANGELOG_TEMPLATE.md` | `{feature}/*_CHANGELOG.md` | 通用 |
| `UI_FLOW_SPEC` | `UI_FLOW_SPEC_TEMPLATE.md` | `{feature}/11_UI_FLOW_SPEC.md` | Phase 2 |
| `API_SPEC` | `API_SPEC_TEMPLATE.md` | `{feature}/11_API_SPEC.md` | Phase 2 |
| `DEMO_REVIEW` | `DEMO_REVIEW_TEMPLATE.md` | `{feature}/12_DEMO_REVIEW.md` | Phase 3 |
| `DESIGN` | `DESIGN_TEMPLATE.md` | `{feature}/10_DESIGN_FINAL.md` | Phase 4 |
| `DEV_PLAN` | `DEV_PLAN_TEMPLATE.md` | `{feature}/20_DEV_PLAN.md` | Phase 5 |
| `PROGRESS_LOG` | `PROGRESS_LOG_TEMPLATE.yaml` | `{feature}/30_PROGRESS_LOG.yaml` | Phase 5 |
| `DAILY_SUMMARY` | `DAILY_SUMMARY_TEMPLATE.md` | `{feature}/31_DAILY_SUMMARY/{date}.md` | Phase 5 |
| `TEST_PLAN` | `TEST_PLAN_TEMPLATE.md` | `{feature}/40_TEST_PLAN.md` | Phase 6 |
| `TEST_REPORT` | `TEST_REPORT_TEMPLATE.md` | `{feature}/41_TEST_REPORT.md` | Phase 6 |
| `RELEASE_NOTE` | `RELEASE_NOTE_TEMPLATE.md` | `{feature}/50_RELEASE_NOTE.md` | Phase 7 |

## 执行步骤

### 1. 加载模板

```
读取：docs/_system/CC_COLLABORATION/03_TEMPLATES/{template}_TEMPLATE.md
```

### 2. 解析变量

模板中的变量使用 `{variable_name}` 格式：

```markdown
# {feature_name} - 功能上下文

> 版本：{version}
> 创建日期：{created_at}
> 负责人：{owner}

## 功能概述

{description}
```

### 3. 填充变量

从 `variables` 参数和系统信息填充：

**自动填充的变量**：
- `{feature}` - 功能模块名称
- `{feature_name}` - 功能名称（中文）
- `{created_at}` - 当前日期
- `{current_datetime}` - 当前时间戳
- `{version}` - 默认 v1.0

**需要手动提供的变量**：
- `{owner}` - 负责人
- `{description}` - 功能描述
- 其他业务相关变量

### 4. 生成文档

```markdown
# user-auth - 功能上下文

> 版本：v1.0
> 创建日期：2024-12-11
> 负责人：@Huan

## 功能概述

<!-- TODO: 请填写功能概述 -->

## 用户故事

<!-- TODO: 请填写用户故事 -->

...
```

### 5. 标记待填充内容

未提供变量的位置标记为 TODO：

```markdown
<!-- TODO: 请填写 {variable_name} -->
```

### 6. 输出结果

```
✅ 文档生成成功

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 生成的文档
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
文件：docs/{feature}/00_CONTEXT.md
模板：CONTEXT_TEMPLATE.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ 已填充的变量
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• feature: user-auth
• feature_name: 用户认证
• created_at: 2024-12-11
• version: v1.0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ 待填充的内容
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• owner - 负责人
• description - 功能概述
• user_stories - 用户故事

💡 请打开文档补充标记为 TODO 的内容
```

## 示例

### 示例 1：生成 CONTEXT 文档

```
请使用 doc_generator skill：
- template: CONTEXT
- feature: user-auth
- variables:
    feature_name: 用户认证
    owner: "@Huan"
```

### 示例 2：生成 DAILY_SUMMARY

```
请使用 doc_generator skill：
- template: DAILY_SUMMARY
- feature: user-auth
- variables:
    date: 2024-12-11
    completed_tasks:
      - CODE-001: 完成登录表单
      - CODE-002: 完成注册表单
    wip_tasks:
      - CODE-003: 实现 API 调用
```

### 示例 3：生成 PROGRESS_LOG

```
请使用 doc_generator skill：
- template: PROGRESS_LOG
- feature: user-auth
- variables:
    owner: "@Huan"
    started_at: 2024-12-11
```

## 注意事项

1. **模板位置**：所有模板位于 `03_TEMPLATES/` 目录
2. **变量格式**：使用 `{variable}` 格式，不要使用 `${variable}` 或 `{{variable}}`
3. **YAML 文件**：PROGRESS_LOG 等 YAML 文件需特别注意格式
4. **TODO 标记**：未填充的变量会标记为 TODO，方便后续补充
5. **覆盖保护**：如果目标文件已存在，会提示确认是否覆盖

## 关联工具

- `/new-feature` - 创建功能时调用此 skill 生成初始文档
- `context_writer` - 智能填充 CONTEXT 内容
- `changelog_updater` - 更新 CHANGELOG 文档
