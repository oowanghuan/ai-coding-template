# mock_api_generator - Mock API 生成器

> 类型：Skill（自动触发）
> 版本：v2.0
> 最后更新：2026-01-09

---

## 何时自动使用

Claude 应该在以下情况**自动应用**这个 skill：

- 用户说「生成 Mock API」「做个假接口」「前端先用 Mock」
- 在 Phase 3 Demo 阶段，UI Demo 需要接口数据时
- 用户说「后端还没好，先 Mock 一下」
- 前后端并行开发时，前端需要接口 Mock

**不适用场景**：
- 后端接口已经完成
- 用户要求的是真实接口实现

---

## 执行方式

### 1. 确定 Mock 范围

从以下来源获取接口定义：
- `docs/{feature}/20_API_SPEC.md`（如果存在）
- `docs/{feature}/21_UI_FLOW_SPEC.md` 中的数据需求
- 用户口头描述

### 2. 选择 Mock 方式

| 方式 | 适用场景 | 实现 |
|------|----------|------|
| JSON 文件 | 简单静态数据 | `/mock/data.json` |
| JS Mock | 需要简单逻辑 | Mock.js / faker.js |
| Mock Server | 需要完整 REST | json-server / msw |

### 3. 生成 Mock 数据

根据接口定义生成：
- 请求路径
- 请求方法
- 响应数据（符合 SPEC 定义的结构）
- 边界情况（空数据、错误响应）

### 4. 输出 Mock 文件

```
输出位置: docs/{feature}/demo/mock/
```

---

## 示例对话

### 示例 1：为登录接口生成 Mock

**User**: 帮我 mock 一下登录接口

**Claude**: [自动应用 mock_api_generator skill]

好的，我来生成登录接口的 Mock。

请确认接口定义：
- 路径：`POST /api/auth/login`
- 请求：`{ email, password }`
- 响应：`{ token, user }`

这样对吗？

**User**: 对的

**Claude**: 生成中...

我创建了以下 Mock 文件：

**1. Mock 数据** `docs/user-auth/demo/mock/auth.json`
```json
{
  "login": {
    "success": {
      "token": "mock-jwt-token-xxx",
      "user": {
        "id": 1,
        "email": "test@example.com",
        "name": "Test User"
      }
    },
    "error": {
      "code": "INVALID_CREDENTIALS",
      "message": "邮箱或密码错误"
    }
  }
}
```

**2. Mock 逻辑** `docs/user-auth/demo/mock/handler.js`
```javascript
// 模拟登录逻辑
function mockLogin(email, password) {
  if (email === 'test@example.com' && password === '123456') {
    return mockData.login.success;
  }
  return mockData.login.error;
}
```

测试账号：
- 邮箱：test@example.com
- 密码：123456

### 示例 2：根据 API SPEC 生成全部 Mock

**User**: 按照 API SPEC 生成所有接口的 Mock

**Claude**: [自动应用 mock_api_generator skill]

好的，我先读取 API SPEC...

找到 `docs/user-auth/20_API_SPEC.md`，包含以下接口：
1. `POST /api/auth/login`
2. `POST /api/auth/register`
3. `POST /api/auth/logout`
4. `GET /api/auth/me`

正在生成 Mock...

[生成所有接口的 Mock 数据和处理逻辑]

---

## Mock 输出规范

### 文件结构

```
docs/{feature}/demo/mock/
├── README.md           # Mock 使用说明
├── db.json             # json-server 数据库（如使用）
├── {module}.json       # 静态 Mock 数据
└── handlers/           # Mock 处理逻辑
    └── {module}.js
```

### Mock 数据要求

1. **符合 SPEC**：字段名、类型与 API SPEC 一致
2. **覆盖场景**：成功、失败、边界情况
3. **真实感**：使用合理的假数据
4. **可配置**：方便切换不同场景

---

## 注意事项

1. **字段一致性**：Mock 字段必须与 API SPEC 完全一致，避免后续切换真实接口时出问题
2. **标注 Mock**：在代码中明确标注这是 Mock 数据
3. **易于切换**：设计时考虑后续切换到真实 API 的便利性
4. **不要过度**：Mock 只用于 Demo 阶段，不要在生产代码中保留

---

## 关联工具

- `ui_demo` - UI Demo 可能调用此 skill 获取 Mock 数据
- `design_from_demo` - 从 Mock API 反推正式 API 契约

---

_CC_COLLABORATION Framework v3.1_
