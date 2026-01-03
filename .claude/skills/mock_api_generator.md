# mock_api_generator - 生成 Mock API

## 能力描述

根据 `21_UI_FLOW_SPEC.md` 或 `20_API_SPEC.md` 自动生成 Mock API 代码，用于前端独立开发和 Demo 演示。

## 输入

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| feature | string | 是 | 功能模块名称 |
| output_dir | string | 否 | 输出目录，默认 `playgrounds/{feature}/mock/` |
| format | string | 否 | 输出格式：`js`（默认）, `ts`, `json` |
| delay | number | 否 | 模拟延迟毫秒数，默认 500 |

## 输出

- `mock/api.js` 或 `mock/api.ts` - Mock API 函数
- `mock/data.json` - Mock 数据（可选）

## 执行步骤

### 1. 读取规格文档

```
读取：
- docs/{feature}/21_UI_FLOW_SPEC.md - UI 流程规格
- docs/{feature}/20_API_SPEC.md - API 规格（如有）
- docs/_system/02_API_CONVENTIONS.md - API 约定
```

### 2. 提取 API 定义

从规格文档提取：

```yaml
apis:
  - name: login
    method: POST
    path: /api/auth/login
    request:
      body:
        email: string
        password: string
    response:
      success:
        code: 200
        data:
          token: string
          user:
            id: number
            email: string
            name: string
      errors:
        - code: 401
          message: "邮箱或密码错误"
        - code: 422
          message: "参数验证失败"
```

### 3. 生成 Mock 代码

#### JavaScript 格式

```javascript
// playgrounds/{feature}/mock/api.js

/**
 * Mock API for {feature}
 * 自动生成，请勿手动修改
 * 生成时间：{datetime}
 */

const DELAY = 500 // 模拟网络延迟

// 工具函数
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms))

const success = (data) => ({ code: 200, data, message: 'success' })

const error = (code, message) => {
  const err = new Error(message)
  err.code = code
  throw err
}

// Mock 数据
const mockUsers = [
  { id: 1, email: 'admin@example.com', name: '管理员', password: 'admin123' },
  { id: 2, email: 'user@example.com', name: '普通用户', password: 'user1234' }
]

let mockTokens = {}

/**
 * 登录
 * POST /api/auth/login
 */
export async function mockLogin({ email, password }) {
  await delay(DELAY)

  const user = mockUsers.find(u => u.email === email)

  if (!user) {
    error(401, '用户不存在')
  }

  if (user.password !== password) {
    error(401, '密码错误')
  }

  const token = `mock_token_${Date.now()}`
  mockTokens[token] = user.id

  return success({
    token,
    user: {
      id: user.id,
      email: user.email,
      name: user.name
    }
  })
}

/**
 * 注册
 * POST /api/auth/register
 */
export async function mockRegister({ email, password, name }) {
  await delay(DELAY)

  if (mockUsers.some(u => u.email === email)) {
    error(409, '邮箱已被注册')
  }

  const newUser = {
    id: mockUsers.length + 1,
    email,
    password,
    name
  }
  mockUsers.push(newUser)

  return success({
    user: {
      id: newUser.id,
      email: newUser.email,
      name: newUser.name
    }
  })
}

/**
 * 获取当前用户
 * GET /api/auth/me
 */
export async function mockGetCurrentUser(token) {
  await delay(DELAY)

  const userId = mockTokens[token]
  if (!userId) {
    error(401, '未登录或 token 已过期')
  }

  const user = mockUsers.find(u => u.id === userId)
  return success({
    id: user.id,
    email: user.email,
    name: user.name
  })
}

/**
 * 退出登录
 * POST /api/auth/logout
 */
export async function mockLogout(token) {
  await delay(DELAY)

  delete mockTokens[token]
  return success({ message: '退出成功' })
}

// 导出所有 Mock API
export default {
  login: mockLogin,
  register: mockRegister,
  getCurrentUser: mockGetCurrentUser,
  logout: mockLogout
}
```

#### TypeScript 格式

```typescript
// playgrounds/{feature}/mock/api.ts

interface ApiResponse<T> {
  code: number
  data: T
  message: string
}

interface User {
  id: number
  email: string
  name: string
}

interface LoginRequest {
  email: string
  password: string
}

interface LoginResponse {
  token: string
  user: User
}

// ... 类型定义

export async function mockLogin(params: LoginRequest): Promise<ApiResponse<LoginResponse>> {
  // 实现同上
}
```

### 4. 生成 Mock 数据文件（可选）

```json
// playgrounds/{feature}/mock/data.json
{
  "users": [
    { "id": 1, "email": "admin@example.com", "name": "管理员" },
    { "id": 2, "email": "user@example.com", "name": "普通用户" }
  ],
  "tokens": {}
}
```

### 5. 输出结果

```
✅ Mock API 生成成功

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 生成的文件
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
playgrounds/{feature}/mock/
├── api.js              # Mock API 函数
└── data.json           # Mock 数据

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 生成的 API
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• mockLogin()         - POST /api/auth/login
• mockRegister()      - POST /api/auth/register
• mockGetCurrentUser() - GET /api/auth/me
• mockLogout()        - POST /api/auth/logout

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 使用方式:
import { mockLogin, mockRegister } from './mock/api'

const result = await mockLogin({ email, password })
```

## 示例

### 示例输入

```
请使用 mock_api_generator skill：
- feature: user-auth
- format: ts
- delay: 300
```

### 示例输出

生成 TypeScript 格式的 Mock API，延迟 300ms。

## 注意事项

1. **数据一致性**：Mock 数据应覆盖正常和异常场景
2. **延迟模拟**：默认 500ms，可调整以模拟真实网络
3. **错误场景**：必须包含所有设计的错误响应
4. **状态持久**：Mock 使用内存存储，刷新后重置
5. **类型安全**：TypeScript 格式包含完整类型定义

## 关联工具

- `ui_demo` - 生成 Demo 时自动调用此 skill
- `/gen-demo` - Slash Command 封装
- `design_from_demo` - 从 Mock API 反推正式 API 契约
