# doc_generator - 文档生成器

> 类型：Skill（自动触发）
> 版本：v2.0
> 最后更新：2026-01-09

---

## 何时自动使用

Claude 应该在以下情况**自动应用**这个 skill：

- 用户说「生成 XX 文档」「创建 XX 文档」「写个 XX 文档」
- 用户提到需要「CONTEXT」「SPEC」「DESIGN」「TEST_PLAN」等标准文档
- 用户说「按模板生成」「用模板创建」
- 在执行 `/new-feature` 后，需要生成初始文档时

**不适用场景**：
- 用户只是询问文档内容，没有要求生成
- 用户要求修改已有文档（应该用 Edit 工具）

---

## 执行方式

### 1. 识别文档类型

根据用户描述判断目标文档：

| 关键词 | 文档类型 | 模板位置 |
|--------|----------|----------|
| CONTEXT、背景、功能概述 | 10_CONTEXT.md | `03_templates/01_kickoff/` |
| API SPEC、接口规格 | 20_API_SPEC.md | `03_templates/02_spec/` |
| UI SPEC、页面流程 | 21_UI_FLOW_SPEC.md | `03_templates/02_spec/` |
| DESIGN、设计文档 | 40_DESIGN_FINAL.md | `03_templates/04_design/` |
| TEST PLAN、测试计划 | 60_TEST_PLAN.md | `03_templates/06_test/` |
| RELEASE NOTE、发布说明 | 70_RELEASE_NOTE.md | `03_templates/07_deploy/` |

### 2. 读取模板

```
模板路径: CC_COLLABORATION/03_templates/{phase}/{TEMPLATE_NAME}_TEMPLATE.md
```

### 3. 收集必要信息

向用户询问模板中的必填项（如果用户没有提供）：
- 功能名称
- 功能描述
- 目标用户
- 关键约束

### 4. 填充模板生成文档

- 替换模板中的占位符
- 保持模板的章节结构
- 添加时间戳和版本信息

### 5. 保存到正确位置

```
输出路径: docs/{feature}/{NUMBER}_{DOC_NAME}.md
```

---

## 示例对话

### 示例 1：生成 CONTEXT

**User**: 帮我生成 user-auth 功能的 CONTEXT 文档，这是一个用户登录注册模块

**Claude**: [自动应用 doc_generator skill]

好的，我来为 user-auth 生成 CONTEXT 文档。

根据你的描述，我先整理一下关键信息：
- 功能名称：user-auth（用户认证模块）
- 核心能力：用户登录、注册

还需要确认几点：
1. 支持哪些登录方式？（邮箱/手机/第三方）
2. 是否需要邮箱验证？
3. 有什么特殊的安全要求？

[等待用户回复后，读取模板并生成文档]

### 示例 2：生成 UI SPEC

**User**: 写个 UI 规格文档，描述登录页面的交互流程

**Claude**: [自动应用 doc_generator skill]

我来生成 UI_FLOW_SPEC 文档。

首先读取模板...

请确认以下页面信息：
1. 页面名称：登录页
2. 入口：从哪里进入这个页面？
3. 主要交互元素有哪些？

---

## 关联模板

- `03_templates/01_kickoff/10_CONTEXT_TEMPLATE.md`
- `03_templates/02_spec/20_API_SPEC_TEMPLATE.md`
- `03_templates/02_spec/21_UI_FLOW_SPEC_TEMPLATE.md`
- `03_templates/04_design/40_DESIGN_TEMPLATE.md`
- `03_templates/06_test/60_TEST_PLAN_TEMPLATE.md`
- `03_templates/07_deploy/70_RELEASE_NOTE_TEMPLATE.md`

---

## 注意事项

1. **模板优先**：始终基于模板生成，保持文档格式统一
2. **信息完整**：确保必填章节都有内容
3. **路径正确**：输出到 `docs/{feature}/` 目录
4. **版本标注**：在文档头部添加版本和日期信息

---

_CC_COLLABORATION Framework v3.1_
