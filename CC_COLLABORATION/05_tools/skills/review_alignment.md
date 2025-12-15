# review_alignment - 检查代码与设计一致性

## 能力描述

检查已实现的代码是否与设计文档（`10_DESIGN_FINAL.md`）和 UI 规格（`11_UI_FLOW_SPEC.md`）保持一致，发现偏差并生成对齐报告。

## 输入

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| feature | string | 是 | 功能模块名称 |
| scope | string | 否 | 检查范围：`full`（完整）, `api`（仅 API）, `ui`（仅 UI），默认 `full` |
| code_paths | array | 否 | 要检查的代码路径，不指定则自动扫描 |

## 输出

- 对齐检查报告
- 偏差列表及严重程度
- 修复建议

## 执行步骤

### 1. 读取设计文档

```
读取以下文档：
- docs/{feature}/10_DESIGN_FINAL.md - 技术设计
- docs/{feature}/11_UI_FLOW_SPEC.md - UI 规格（如有）
- docs/{feature}/11_API_SPEC.md - API 规格（如有）
```

### 2. 提取设计要点

从设计文档中提取：

**API 层面**：
- API 端点路径
- 请求参数（必填/可选）
- 响应格式
- 错误码定义

**UI 层面**：
- 页面/组件列表
- 字段名称和类型
- 交互行为
- 状态定义

**数据层面**：
- 数据模型字段
- 字段类型和约束
- 关联关系

### 3. 扫描代码实现

根据 `scope` 参数扫描相关代码：

```
scope = full:
  - src/**/*.vue      # Vue 组件
  - src/**/*.ts       # TypeScript 文件
  - src/api/**/*      # API 调用
  - src/stores/**/*   # 状态管理

scope = api:
  - src/api/**/*
  - server/**/*（如有）

scope = ui:
  - src/**/*.vue
  - src/components/**/*
```

### 4. 逐项对比

对比设计与实现：

| 检查项 | 设计要求 | 实际实现 | 状态 |
|--------|----------|----------|------|
| API 路径 | `/api/users` | `/api/users` | ✅ |
| 请求参数 | `{email, password}` | `{email, password, remember}` | ⚠️ 多出 remember |
| 响应格式 | `{token, user}` | `{token, user}` | ✅ |
| 字段名 | `userName` | `username` | ❌ 命名不一致 |

### 5. 生成报告

```markdown
# 代码与设计对齐检查报告

> 功能：{feature}
> 检查时间：{datetime}
> 范围：{scope}

---

## 摘要

| 指标 | 数值 |
|------|------|
| 检查项总数 | {total} |
| 完全一致 | {aligned} |
| 有偏差 | {deviation} |
| 严重偏差 | {critical} |
| 一致率 | {percentage}% |

---

## 偏差详情

### ❌ 严重偏差（必须修复）

1. **{issue_title}**
   - 设计：{design_spec}
   - 实现：{actual_impl}
   - 位置：{file_path}:{line}
   - 建议：{suggestion}

### ⚠️ 轻微偏差（建议修复）

1. **{issue_title}**
   - 设计：{design_spec}
   - 实现：{actual_impl}
   - 位置：{file_path}:{line}
   - 建议：{suggestion}

---

## 修复建议

按优先级排序的修复任务：

1. [ ] {fix_task_1}
2. [ ] {fix_task_2}

---

## 需要澄清

以下设计文档中有歧义或未定义的内容：

1. {ambiguity_1}
2. {ambiguity_2}
```

## 示例

### 示例输入

```
请使用 review_alignment skill：
- feature: user-auth
- scope: api
```

### 示例输出

```
# 代码与设计对齐检查报告

> 功能：user-auth
> 检查时间：2024-12-11T16:00:00+08:00
> 范围：api

---

## 摘要

| 指标 | 数值 |
|------|------|
| 检查项总数 | 15 |
| 完全一致 | 12 |
| 有偏差 | 2 |
| 严重偏差 | 1 |
| 一致率 | 80% |

---

## 偏差详情

### ❌ 严重偏差

1. **登录响应缺少 refreshToken**
   - 设计：响应应包含 `{token, refreshToken, user}`
   - 实现：只返回 `{token, user}`
   - 位置：src/api/auth.ts:25
   - 建议：添加 refreshToken 到响应对象

### ⚠️ 轻微偏差

1. **额外的 remember 参数**
   - 设计：未定义 remember 参数
   - 实现：请求包含可选的 remember 参数
   - 位置：src/api/auth.ts:10
   - 建议：补充设计文档或移除参数
```

## 注意事项

1. **设计文档为准**：以设计文档为基准，代码应向设计看齐
2. **严重程度判断**：
   - ❌ 严重：影响功能、安全、数据一致性
   - ⚠️ 轻微：命名差异、额外功能、文档遗漏
3. **自动扫描路径**：未指定 `code_paths` 时，根据项目结构自动推断
4. **增量检查**：支持只检查特定文件，提高效率

## 关联工具

- `/check-progress` - 检查前可先查看进度
- `doc_generator` - 发现文档遗漏时可补充
- `changelog_updater` - 修复后更新变更日志
