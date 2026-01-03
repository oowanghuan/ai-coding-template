# spec_validator - 检查 SPEC 完整性

## 能力描述

检查 `21_UI_FLOW_SPEC.md` 或 `20_API_SPEC.md` 的完整性和一致性，确保规格文档符合标准，可以进入下一阶段。

## 输入

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| feature | string | 是 | 功能模块名称 |
| spec_type | string | 否 | 规格类型：`ui`, `api`, `auto`（默认自动检测） |
| strict | boolean | 否 | 严格模式，默认 false |

## 输出

- 验证报告
- 问题列表及严重程度
- 修复建议

## 检查项

### UI_FLOW_SPEC 检查项

| 检查项 | 级别 | 说明 |
|--------|------|------|
| 页面完整性 | ERROR | 所有页面都有定义 |
| 字段定义 | ERROR | 每个表单字段都有类型和验证规则 |
| 状态覆盖 | WARNING | 是否定义了 loading/error/empty 状态 |
| 交互行为 | ERROR | 按钮和链接都有对应的行为定义 |
| 导航流程 | WARNING | 页面间跳转是否清晰 |
| 响应式 | INFO | 是否考虑移动端适配 |

### API_SPEC 检查项

| 检查项 | 级别 | 说明 |
|--------|------|------|
| 端点完整性 | ERROR | 所有 API 端点都有定义 |
| 请求参数 | ERROR | 参数类型、必填/可选 |
| 响应格式 | ERROR | 成功和错误响应格式 |
| 错误码定义 | WARNING | 是否定义了所有可能的错误码 |
| 认证要求 | WARNING | 哪些接口需要认证 |
| 幂等性 | INFO | POST/PUT 接口的幂等性说明 |

## 执行步骤

### 1. 读取 SPEC 文档

```
读取：
- docs/{feature}/21_UI_FLOW_SPEC.md
- docs/{feature}/20_API_SPEC.md
- docs/{feature}/10_CONTEXT.md（用于交叉验证）
```

### 2. 解析文档结构

提取 SPEC 中的关键元素：

```yaml
# UI_FLOW_SPEC 解析结果
pages:
  - name: LoginPage
    fields: [email, password]
    actions: [submit, forgotPassword]
    states: [initial, loading, error, success]

# API_SPEC 解析结果
endpoints:
  - method: POST
    path: /api/auth/login
    params: [email, password]
    responses: [200, 401, 422]
```

### 3. 执行检查

#### 检查 1：页面/端点完整性

```
✅ LoginPage - 已定义
✅ RegisterPage - 已定义
❌ ForgotPasswordPage - CONTEXT 中提到但未定义
```

#### 检查 2：字段定义

```
✅ email - type: input, validation: required|email
✅ password - type: password, validation: required|min:8
⚠️ confirmPassword - 缺少 validation 规则
```

#### 检查 3：状态覆盖

```
✅ LoginPage - loading, error 状态已定义
⚠️ RegisterPage - 缺少 empty 状态定义
```

#### 检查 4：与 CONTEXT 一致性

```
✅ "记住我"功能 - SPEC 中有定义
❌ "邮箱验证"功能 - CONTEXT 中有，但 SPEC 未涵盖
```

### 4. 生成报告

```markdown
# SPEC 验证报告

> 功能：{feature}
> 检查时间：{datetime}
> 规格类型：{spec_type}
> 模式：{strict ? '严格' : '标准'}

---

## 摘要

| 级别 | 数量 |
|------|------|
| ❌ ERROR | 2 |
| ⚠️ WARNING | 3 |
| ℹ️ INFO | 1 |

**结论**：{pass ? '✅ 通过' : '❌ 未通过'}

---

## 问题详情

### ❌ ERROR（必须修复）

1. **缺少页面定义：ForgotPasswordPage**
   - 位置：21_UI_FLOW_SPEC.md
   - 说明：CONTEXT 中提到"忘记密码"功能，但 SPEC 未定义对应页面
   - 建议：添加 ForgotPasswordPage 的完整定义

2. **缺少功能覆盖：邮箱验证**
   - 位置：21_UI_FLOW_SPEC.md
   - 说明：CONTEXT 中要求的邮箱验证流程未在 SPEC 中体现
   - 建议：添加 EmailVerification 页面或流程

### ⚠️ WARNING（建议修复）

1. **缺少验证规则：confirmPassword**
   - 位置：21_UI_FLOW_SPEC.md > RegisterPage
   - 建议：添加 `validation: required|same:password`

2. **缺少状态定义：RegisterPage.empty**
   - 位置：21_UI_FLOW_SPEC.md > RegisterPage
   - 建议：定义表单初始状态

3. **缺少错误码：409 Conflict**
   - 位置：20_API_SPEC.md > POST /register
   - 建议：添加"邮箱已注册"的错误响应

### ℹ️ INFO（可选优化）

1. **未定义响应式断点**
   - 说明：建议添加移动端适配说明
   - 参考：docs/_system/_ui_system/05_RESPONSIVE.md

---

## 下一步

1. 修复 2 个 ERROR 级别问题
2. 建议修复 3 个 WARNING 级别问题
3. 修复后重新运行验证：`/check-spec {feature}`
```

## 示例

### 示例输入

```
请使用 spec_validator skill：
- feature: user-auth
- strict: true
```

### 示例输出

生成详细的验证报告，列出所有问题和修复建议。

## 注意事项

1. **严格模式**：strict=true 时，WARNING 也会导致不通过
2. **交叉验证**：会与 CONTEXT 进行对比检查
3. **自动检测**：spec_type=auto 时，根据文件存在情况自动选择
4. **增量检查**：支持只检查修改过的部分

## 关联工具

- `spec_writer` - 生成 SPEC 后调用此 skill 验证
- `ui_demo` - 验证通过后才生成 Demo
- `doc_generator` - 生成 SPEC 文档
