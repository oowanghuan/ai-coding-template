# test_plan_writer - 生成测试计划

## 能力描述

根据 `21_UI_FLOW_SPEC.md` 或 `20_API_SPEC.md`，自动生成完整的测试计划 `60_TEST_PLAN.md`，包括测试用例、测试数据、预期结果。

## 输入

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| feature | string | 是 | 功能模块名称 |
| test_type | string | 否 | 测试类型：`ui`, `api`, `unit`, `all`（默认） |
| coverage | string | 否 | 覆盖程度：`smoke`（冒烟）, `standard`（默认）, `full`（全量） |

## 输出

- `docs/{feature}/60_TEST_PLAN.md` - 测试计划文档

## 工作流程

```
┌─────────────────────────────────────────────────────┐
│                  test_plan_writer                    │
├─────────────────────────────────────────────────────┤
│                                                      │
│  1. 读取 SPEC 文档                                   │
│     ├── 21_UI_FLOW_SPEC.md                          │
│     └── 20_API_SPEC.md                              │
│     ↓                                                │
│  2. 分析测试场景                                     │
│     ├── 正常流程                                    │
│     ├── 边界条件                                    │
│     ├── 异常处理                                    │
│     └── 安全验证                                    │
│     ↓                                                │
│  3. 生成测试用例                                     │
│     ├── UI 测试用例                                 │
│     ├── API 测试用例                                │
│     └── 单元测试用例                                │
│     ↓                                                │
│  4. 生成测试数据                                     │
│     ├── 正常数据                                    │
│     └── 边界数据                                    │
│     ↓                                                │
│  5. 生成测试计划文档                                 │
│     └── 调用 doc_generator skill                    │
│     ↓                                                │
│  6. 输出结果                                         │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## 调用的 Skills

| Skill | 用途 |
|-------|------|
| `doc_generator` | 生成 TEST_PLAN 文档框架 |

## 执行步骤

### 1. 读取 SPEC 文档

从 SPEC 中提取测试相关信息：

```yaml
# 从 UI_FLOW_SPEC 提取
pages:
  - name: LoginPage
    fields: [email, password, remember]
    actions: [submit, forgotPassword, register]
    validations:
      email: [required, email_format]
      password: [required, min_8]
    states: [initial, loading, error, success]
    error_scenarios:
      - code: 401
        message: "账号或密码错误"

# 从 API_SPEC 提取
endpoints:
  - method: POST
    path: /api/auth/login
    params: [email, password]
    responses:
      success: { status: 200, body: { token, user } }
      errors:
        - { status: 401, code: "AUTH_FAILED" }
        - { status: 422, code: "VALIDATION_ERROR" }
```

### 2. 生成测试用例

根据覆盖程度生成不同数量的测试用例：

#### Smoke 测试（冒烟）
- 只覆盖核心正常流程
- 用例数量：5-10

#### Standard 测试（标准）
- 覆盖正常流程 + 主要异常
- 用例数量：15-25

#### Full 测试（全量）
- 覆盖所有场景包括边界条件
- 用例数量：30+

### 3. 生成测试计划文档

```markdown
# 测试计划 - {feature}

> 版本：v1.0
> 创建日期：{date}
> 覆盖程度：{coverage}
> 预计用例数：{total_cases}

---

## 测试范围

### 测试目标
验证 {feature} 功能的正确性、稳定性和用户体验。

### 测试类型
- [x] UI 测试 - 用户界面交互验证
- [x] API 测试 - 接口功能验证
- [x] 单元测试 - 核心逻辑验证

### 不在测试范围
- 性能测试
- 安全渗透测试
- 兼容性测试

---

## UI 测试用例

### 登录功能

#### TC-UI-001: 登录成功
**优先级**: P0
**前置条件**: 已注册用户 test@example.com / password123

| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 访问 /login | 显示登录页面 |
| 2 | 输入邮箱 test@example.com | 邮箱字段显示输入值 |
| 3 | 输入密码 password123 | 密码字段显示掩码 |
| 4 | 点击登录按钮 | 显示加载状态 |
| 5 | 等待响应 | 跳转到首页 /dashboard |

**测试数据**:
```json
{
  "email": "test@example.com",
  "password": "password123"
}
```

---

#### TC-UI-002: 登录失败 - 密码错误
**优先级**: P1
**前置条件**: 已注册用户 test@example.com

| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 访问 /login | 显示登录页面 |
| 2 | 输入邮箱 test@example.com | 邮箱字段显示输入值 |
| 3 | 输入错误密码 wrongpassword | 密码字段显示掩码 |
| 4 | 点击登录按钮 | 显示加载状态 |
| 5 | 等待响应 | 显示错误提示"账号或密码错误" |

---

#### TC-UI-003: 表单验证 - 邮箱格式错误
**优先级**: P1

| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 输入无效邮箱 invalid-email | 显示验证错误"请输入有效的邮箱" |
| 2 | 登录按钮 | 按钮禁用或点击无效 |

---

#### TC-UI-004: 表单验证 - 密码太短
**优先级**: P1

| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 输入短密码 123 | 显示验证错误"密码至少 8 个字符" |

---

#### TC-UI-005: 记住我功能
**优先级**: P2

| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 勾选"记住我" | 复选框被选中 |
| 2 | 登录成功 | 存储持久化 Token |
| 3 | 关闭浏览器后重新访问 | 保持登录状态 |

---

## API 测试用例

### POST /api/auth/login

#### TC-API-001: 登录接口 - 成功
**优先级**: P0

**请求**:
```json
{
  "email": "test@example.com",
  "password": "password123"
}
```

**预期响应**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "token": "eyJhbGci...",
    "user": {
      "id": 1,
      "email": "test@example.com",
      "name": "测试用户"
    }
  }
}
```

**断言**:
- 状态码 = 200
- data.token 存在且非空
- data.user.email = 请求中的 email

---

#### TC-API-002: 登录接口 - 密码错误
**优先级**: P1

**请求**:
```json
{
  "email": "test@example.com",
  "password": "wrongpassword"
}
```

**预期响应**:
```json
{
  "code": 401,
  "message": "账号或密码错误"
}
```

---

#### TC-API-003: 登录接口 - 参数缺失
**优先级**: P1

**请求**:
```json
{
  "email": "test@example.com"
}
```

**预期响应**:
```json
{
  "code": 422,
  "message": "密码不能为空"
}
```

---

## 单元测试用例

### 验证函数测试

#### TC-UNIT-001: validateEmail - 有效邮箱
```typescript
expect(validateEmail('test@example.com')).toBe(true)
expect(validateEmail('user.name@domain.co.uk')).toBe(true)
```

#### TC-UNIT-002: validateEmail - 无效邮箱
```typescript
expect(validateEmail('invalid')).toBe(false)
expect(validateEmail('test@')).toBe(false)
expect(validateEmail('@domain.com')).toBe(false)
```

#### TC-UNIT-003: validatePassword - 有效密码
```typescript
expect(validatePassword('password123')).toBe(true)
expect(validatePassword('12345678')).toBe(true)
```

#### TC-UNIT-004: validatePassword - 无效密码
```typescript
expect(validatePassword('123')).toBe(false)  // 太短
expect(validatePassword('')).toBe(false)     // 空
```

---

## 测试数据

### 用户数据

| 邮箱 | 密码 | 用途 |
|------|------|------|
| test@example.com | password123 | 正常用户 |
| admin@example.com | admin123456 | 管理员 |
| locked@example.com | password123 | 被锁定用户 |

### 边界数据

| 场景 | 数据 |
|------|------|
| 最短有效密码 | 12345678（8 位） |
| 最长有效密码 | a*128（128 位） |
| 特殊字符邮箱 | user+tag@example.com |

---

## 测试环境

| 项目 | 配置 |
|------|------|
| 浏览器 | Chrome 最新版 |
| 操作系统 | macOS / Windows |
| 前端地址 | http://localhost:3000 |
| API 地址 | http://localhost:8080 |
| 数据库 | 测试环境 PostgreSQL |

---

## 测试进度追踪

| 测试类型 | 总数 | 通过 | 失败 | 待执行 |
|---------|------|------|------|--------|
| UI 测试 | 10 | 0 | 0 | 10 |
| API 测试 | 8 | 0 | 0 | 8 |
| 单元测试 | 6 | 0 | 0 | 6 |
| **合计** | **24** | **0** | **0** | **24** |

---

_Generated by test_plan_writer | {datetime}_
```

### 4. 输出结果

```
✅ 测试计划生成成功

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 生成的文档
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• docs/{feature}/60_TEST_PLAN.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 测试用例统计
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• UI 测试: 10 个
• API 测试: 8 个
• 单元测试: 6 个
• 总计: 24 个

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 覆盖情况
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 页面覆盖: 100%
• API 覆盖: 100%
• 用户故事覆盖: 100%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 下一步：
1. 人工评审测试计划
2. 准备测试数据
3. 使用 /run-tests 执行测试
```

## 示例

### 示例输入

```
请使用 test_plan_writer subagent：
- feature: user-auth
- test_type: all
- coverage: standard
```

### 示例输出

生成包含 UI、API、单元测试的完整测试计划。

## 测试失败处理策略

测试计划中应包含失败处理说明：

### 问题分级标准

| 级别 | 定义 | 处理方式 | 示例 |
|------|------|----------|------|
| P0 | 功能完全不可用 | **立即修复** | 页面白屏、登录崩溃 |
| P1 | 核心流程受阻 | **立即修复** | 无法提交表单、跳转错误 |
| P2 | 功能异常但可绕过 | 记录，后续修复 | 错误提示不准确、样式错位 |
| P3 | 体验问题 | 记录，后续修复 | 按钮位置不理想、文案不清晰 |

### 处理原则

1. **P0/P1 阻塞性问题**：暂停测试 → 立即修复 → 重跑当前用例 → 继续
2. **P2/P3 非阻塞问题**：记录问题 → 继续测试 → 全部完成后统一修复 → 回归测试

### 测试计划模板中应包含

在生成的 `60_TEST_PLAN.md` 中添加失败处理章节：

```markdown
## 失败处理策略

### 问题分级
- **P0**: 功能完全不可用 → 立即修复
- **P1**: 核心流程受阻 → 立即修复
- **P2**: 功能异常可绕过 → 记录后续修复
- **P3**: 体验问题 → 记录后续修复

### 处理流程
1. 发现失败 → 判定级别
2. P0/P1: 暂停 → 修复 → 重跑
3. P2/P3: 记录 → 继续 → 后续修复
4. 全部完成 → 统一修复 P2/P3 → 回归测试
```

## 注意事项

1. **SPEC 依赖**：必须先有完整的 SPEC 文档
2. **优先级分配**：P0 是必测，P1 是重要，P2 是可选
3. **测试数据**：提供的测试数据需要与测试环境匹配
4. **人工评审**：生成的计划需要测试人员评审
5. **失败处理**：测试计划应包含失败处理策略说明

## 关联工具

- `spec_validator` - 验证 SPEC 完整性
- `test_runner` - 执行测试计划
- `test_report_generator` - 生成测试报告
