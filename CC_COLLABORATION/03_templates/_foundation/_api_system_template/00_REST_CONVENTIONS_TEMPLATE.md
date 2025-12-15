# 00_REST_CONVENTIONS.md
# HTTP REST API 设计规范

> 版本：v1.0
> 最后更新：{timestamp}
> 适用范围：所有 HTTP REST API 接口设计

---

## 1. 概述

本文档定义项目中所有 HTTP REST API 接口的设计规范，确保：
- 接口命名一致性
- 错误处理标准化
- 响应格式统一
- 便于 Claude Code 理解和生成符合规范的代码

---

## 2. RESTful 设计原则

### 2.1 HTTP 方法使用

| 方法 | 用途 | 幂等性 | 示例 |
|------|------|--------|------|
| `GET` | 获取资源 | 是 | `GET /api/users/123` |
| `POST` | 创建资源 | 否 | `POST /api/users` |
| `PUT` | 完整更新资源 | 是 | `PUT /api/users/123` |
| `PATCH` | 部分更新资源 | 是 | `PATCH /api/users/123` |
| `DELETE` | 删除资源 | 是 | `DELETE /api/users/123` |

### 2.2 URL 命名规范

```
# 格式
/api/{version}/{resource}/{id}/{sub-resource}

# 规则
- 使用小写字母
- 使用连字符（kebab-case）分隔单词
- 资源名使用复数形式
- 避免动词，用 HTTP 方法表达操作

# 正确示例
GET    /api/v1/users
GET    /api/v1/users/123
GET    /api/v1/users/123/orders
POST   /api/v1/users
PATCH  /api/v1/users/123

# 错误示例
GET    /api/v1/getUsers          # 不要在 URL 中使用动词
GET    /api/v1/user/123          # 使用复数 users
POST   /api/v1/users/create      # 创建用 POST 方法表达
```

### 2.3 查询参数

```
# 分页
?page=1&page_size=20

# 排序
?sort_by=created_at&sort_order=desc

# 过滤
?status=active&role=admin

# 搜索
?q=keyword

# 字段选择
?fields=id,name,email
```

---

## 3. 响应格式

### 3.1 统一响应结构

```typescript
// 成功响应
interface SuccessResponse<T> {
  success: true;
  data: T;
  meta?: {
    page?: number;
    page_size?: number;
    total?: number;
    total_pages?: number;
  };
}

// 错误响应
interface ErrorResponse {
  success: false;
  error: {
    code: string;           // 错误码，如 "USER_NOT_FOUND"
    message: string;        // 用户可见的错误信息
    details?: any;          // 可选的详细信息
    trace_id?: string;      // 用于追踪的请求 ID
  };
}
```

### 3.2 响应示例

```json
// 成功：获取单个资源
{
  "success": true,
  "data": {
    "id": 123,
    "name": "张三",
    "email": "zhangsan@example.com",
    "created_at": "2024-12-09T10:30:00Z"
  }
}

// 成功：获取列表
{
  "success": true,
  "data": [
    { "id": 1, "name": "项目A" },
    { "id": 2, "name": "项目B" }
  ],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 42,
    "total_pages": 3
  }
}

// 错误响应
{
  "success": false,
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "用户不存在",
    "trace_id": "req-abc123"
  }
}
```

---

## 4. 错误码规范

### 4.1 HTTP 状态码使用

| 状态码 | 含义 | 使用场景 |
|--------|------|----------|
| `200` | OK | 请求成功 |
| `201` | Created | 资源创建成功 |
| `204` | No Content | 删除成功，无返回内容 |
| `400` | Bad Request | 请求参数错误 |
| `401` | Unauthorized | 未认证 |
| `403` | Forbidden | 无权限 |
| `404` | Not Found | 资源不存在 |
| `409` | Conflict | 资源冲突（如重复创建） |
| `422` | Unprocessable Entity | 业务逻辑错误 |
| `429` | Too Many Requests | 请求过于频繁 |
| `500` | Internal Server Error | 服务器内部错误 |

### 4.2 业务错误码命名

```
# 格式
{DOMAIN}_{ACTION}_{REASON}

# 示例
AUTH_LOGIN_FAILED           # 认证 - 登录 - 失败
USER_NOT_FOUND              # 用户 - 未找到
USER_EMAIL_DUPLICATE        # 用户 - 邮箱 - 重复
ORDER_PAYMENT_INSUFFICIENT  # 订单 - 支付 - 余额不足
FILE_UPLOAD_SIZE_EXCEEDED   # 文件 - 上传 - 大小超限
```

### 4.3 标准错误码列表

| 错误码 | HTTP 状态码 | 描述 |
|--------|-------------|------|
| `INVALID_REQUEST` | 400 | 请求格式错误 |
| `MISSING_PARAMETER` | 400 | 缺少必要参数 |
| `INVALID_PARAMETER` | 400 | 参数值无效 |
| `UNAUTHORIZED` | 401 | 未提供认证信息 |
| `TOKEN_EXPIRED` | 401 | Token 已过期 |
| `FORBIDDEN` | 403 | 无操作权限 |
| `RESOURCE_NOT_FOUND` | 404 | 资源不存在 |
| `RESOURCE_CONFLICT` | 409 | 资源冲突 |
| `RATE_LIMIT_EXCEEDED` | 429 | 请求频率超限 |
| `INTERNAL_ERROR` | 500 | 服务器内部错误 |

---

## 5. 版本管理

### 5.1 版本策略

```
# URL 路径版本（推荐）
/api/v1/users
/api/v2/users

# Header 版本（备选）
Accept: application/vnd.api+json; version=1
```

### 5.2 版本兼容规则

- **向后兼容的变更**（不需要新版本）：
  - 添加新的可选字段
  - 添加新的 endpoint
  - 添加新的可选查询参数

- **破坏性变更**（需要新版本）：
  - 删除或重命名字段
  - 改变字段类型
  - 改变必填/可选状态
  - 改变错误码

---

## 6. 认证与授权

### 6.1 认证方式

```
# JWT Bearer Token（推荐）
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

# API Key（服务间调用）
X-API-Key: sk_live_xxxxx
```

### 6.2 Token 格式

```typescript
// JWT Payload
interface TokenPayload {
  sub: string;           // 用户 ID
  email: string;         // 用户邮箱
  role: string;          // 角色
  iat: number;           // 签发时间
  exp: number;           // 过期时间
}
```

---

## 7. 日期时间格式

### 7.1 统一使用 ISO 8601

```
# 格式
YYYY-MM-DDTHH:mm:ss.sssZ

# 示例
2024-12-09T10:30:00.000Z     # UTC 时间
2024-12-09T18:30:00+08:00    # 带时区
2024-12-09                    # 仅日期
```

### 7.2 时间戳字段命名

```
created_at      # 创建时间
updated_at      # 更新时间
deleted_at      # 删除时间（软删除）
started_at      # 开始时间
completed_at    # 完成时间
expired_at      # 过期时间
```

---

## 8. 字段命名规范

### 8.1 命名风格

```
# JSON 字段使用 snake_case
{
  "user_id": 123,
  "first_name": "张",
  "last_name": "三",
  "created_at": "2024-12-09T10:30:00Z"
}

# 避免缩写，使用完整单词
# 正确
"description": "..."
"configuration": {...}

# 避免
"desc": "..."
"config": {...}
```

### 8.2 布尔字段命名

```
# 使用 is_、has_、can_、should_ 前缀
{
  "is_active": true,
  "is_verified": false,
  "has_permission": true,
  "can_edit": false,
  "should_notify": true
}
```

### 8.3 ID 字段命名

```
# 主键
"id": 123

# 外键
"user_id": 456
"order_id": 789

# UUID 格式
"id": "550e8400-e29b-41d4-a716-446655440000"
```

---

## 9. 分页规范

### 9.1 请求参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `page` | integer | 1 | 页码，从 1 开始 |
| `page_size` | integer | 20 | 每页数量，最大 100 |

### 9.2 响应格式

```json
{
  "success": true,
  "data": [...],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

---

## 10. Claude Code 使用指南

### 10.1 生成 API 时的检查清单

- [ ] URL 是否使用复数资源名
- [ ] HTTP 方法是否正确
- [ ] 响应格式是否符合统一结构
- [ ] 错误码是否在标准列表中
- [ ] 字段命名是否使用 snake_case
- [ ] 时间字段是否使用 ISO 8601

### 10.2 Mock API 数据规范

```typescript
// 生成 Mock 数据时遵循
const mockUser = {
  id: 1,                                    // 数字 ID 或 UUID
  name: "测试用户",                          // 使用中文测试数据
  email: "test@example.com",                // 使用 example.com 域名
  status: "active",                         // 使用枚举值
  created_at: "2024-12-09T10:30:00Z",       // ISO 8601 格式
  is_verified: true                         // 布尔值带 is_ 前缀
};
```

---

## 附录：快速参考

### A. URL 模式速查

```
GET    /api/v1/{resource}              # 列表
GET    /api/v1/{resource}/{id}         # 详情
POST   /api/v1/{resource}              # 创建
PUT    /api/v1/{resource}/{id}         # 完整更新
PATCH  /api/v1/{resource}/{id}         # 部分更新
DELETE /api/v1/{resource}/{id}         # 删除
GET    /api/v1/{resource}/{id}/{sub}   # 子资源列表
```

### B. 常用状态码速查

```
200 - 成功
201 - 已创建
204 - 无内容（删除成功）
400 - 请求错误
401 - 未认证
403 - 无权限
404 - 未找到
422 - 业务错误
500 - 服务器错误
```

---

## 模板使用说明

1. 复制此文件到 `docs/_foundation/_api_system/00_REST_CONVENTIONS.md`
2. 替换 `{timestamp}` 为当前日期
3. 根据项目实际情况调整具体规范
4. 删除此"模板使用说明"段落
