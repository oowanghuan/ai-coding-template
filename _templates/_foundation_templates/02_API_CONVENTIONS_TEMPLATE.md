# 02_API_CONVENTIONS.md
# API 设计规范

> 版本：v1.0
> 最后更新：{date}
> 状态：Draft

---

## 1. 概述

本文档定义了 {project_name} 项目的 API 设计规范，所有后端 API 开发必须遵循本规范。

---

## 2. URL 命名规范

### 2.1 基本规则

- 使用小写字母
- 使用连字符 `-` 分隔单词
- 使用名词复数表示资源集合
- 避免使用动词（CRUD 操作由 HTTP 方法表示）

### 2.2 示例

```
# 资源集合
GET    /api/v1/{resources}
POST   /api/v1/{resources}

# 单个资源
GET    /api/v1/{resources}/{id}
PUT    /api/v1/{resources}/{id}
DELETE /api/v1/{resources}/{id}

# 嵌套资源
GET    /api/v1/{resources}/{id}/{sub-resources}
```

---

## 3. 请求规范

### 3.1 请求头

| Header | 必需 | 说明 |
|--------|------|------|
| `Content-Type` | 是 | `application/json` |
| `Authorization` | 视接口 | `Bearer {token}` |
| `X-Request-ID` | 推荐 | 请求追踪 ID |

### 3.2 请求体

```json
{
  "field1": "value1",
  "field2": "value2"
}
```

---

## 4. 响应规范

### 4.1 成功响应

```json
{
  "code": 0,
  "message": "success",
  "data": {
    // 业务数据
  }
}
```

### 4.2 列表响应

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "pageSize": 20
  }
}
```

### 4.3 错误响应

```json
{
  "code": 10001,
  "message": "错误描述",
  "details": {
    // 错误详情（可选）
  }
}
```

---

## 5. 错误码规范

### 5.1 错误码分段

| 范围 | 说明 |
|------|------|
| 0 | 成功 |
| 10000-19999 | 通用错误 |
| 20000-29999 | {module1} 模块错误 |
| 30000-39999 | {module2} 模块错误 |

### 5.2 通用错误码

| 错误码 | HTTP 状态码 | 说明 |
|--------|------------|------|
| 10001 | 400 | 参数错误 |
| 10002 | 401 | 未授权 |
| 10003 | 403 | 禁止访问 |
| 10004 | 404 | 资源不存在 |
| 10005 | 500 | 服务器内部错误 |

---

## 6. 版本控制

API 版本通过 URL 路径体现：

```
/api/v1/...
/api/v2/...
```

---

## 7. 示例 API

### 7.1 {示例接口名}

```
{METHOD} /api/v1/{path}
```

**请求参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| {param} | {type} | {required} | {description} |

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

---

## CHANGELOG

| 版本 | 日期 | 作者 | 变更内容 |
|------|------|------|----------|
| v1.0 | {date} | {author} | 初始版本 |

---

_从 02_API_CONVENTIONS_TEMPLATE.md 生成_
