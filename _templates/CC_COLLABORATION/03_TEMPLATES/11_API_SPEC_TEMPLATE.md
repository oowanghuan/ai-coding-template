# API_SPEC_TEMPLATE.md
# API 规格文档模板

---

> **使用说明**
> 1. 复制此模板到功能目录，重命名为 `11_API_SPEC.md`
> 2. 替换 `{placeholder}` 为实际内容
> 3. 根据功能复杂度增删接口
> 4. 删除本使用说明块

---

# 11_API_SPEC.md
# {功能名称} - API 规格

> 版本：v1.0
> 最后更新：{YYYY-MM-DD}
> 状态：{Draft | Review | Approved}
> 设计者：{@username}
> 关联文档：`00_CONTEXT.md`

---

## 1. 概述

### 1.1 功能简介

{简述本功能的 API 部分要实现什么}

### 1.2 接口清单

| 接口 | 方法 | 路径 | 描述 |
|------|------|------|------|
| 列表查询 | GET | `/api/v1/{resources}` | 分页查询{资源}列表 |
| 详情查询 | GET | `/api/v1/{resources}/:id` | 获取{资源}详情 |
| 创建 | POST | `/api/v1/{resources}` | 创建{资源} |
| 更新 | PUT | `/api/v1/{resources}/:id` | 更新{资源} |
| 删除 | DELETE | `/api/v1/{resources}/:id` | 删除{资源} |

### 1.3 通用约定

- 基础路径：`/api/v1`
- 认证方式：Bearer Token
- 内容类型：`application/json`
- 字符编码：UTF-8

---

## 2. 接口详情

### 2.1 列表查询

#### 基本信息

| 属性 | 值 |
|------|-----|
| 路径 | `GET /api/v1/{resources}` |
| 认证 | 需要 |
| 权限 | `{resource}:read` |

#### 请求参数

**Query Parameters**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | integer | 否 | 1 | 页码，从 1 开始 |
| pageSize | integer | 否 | 20 | 每页条数，最大 100 |
| keyword | string | 否 | - | 搜索关键词 |
| status | string | 否 | - | 状态筛选：active / inactive |
| sortBy | string | 否 | createdAt | 排序字段 |
| sortOrder | string | 否 | desc | 排序方向：asc / desc |

#### 响应示例

**成功响应 (200)**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "name": "示例名称",
        "status": "active",
        "createdAt": "2024-12-09T10:00:00Z",
        "updatedAt": "2024-12-09T12:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "pageSize": 20,
      "total": 100,
      "totalPages": 5
    }
  }
}
```

#### 错误响应

| 状态码 | 错误码 | 说明 |
|--------|--------|------|
| 401 | AUTH_001 | 未登录或 Token 过期 |
| 403 | AUTH_002 | 无权限访问 |

---

### 2.2 详情查询

#### 基本信息

| 属性 | 值 |
|------|-----|
| 路径 | `GET /api/v1/{resources}/:id` |
| 认证 | 需要 |
| 权限 | `{resource}:read` |

#### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | integer | 是 | 资源 ID |

#### 响应示例

**成功响应 (200)**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "name": "示例名称",
    "description": "这是描述",
    "status": "active",
    "type": "default",
    "metadata": {
      "key": "value"
    },
    "createdAt": "2024-12-09T10:00:00Z",
    "updatedAt": "2024-12-09T12:00:00Z",
    "createdBy": {
      "id": 1,
      "name": "用户名"
    }
  }
}
```

#### 错误响应

| 状态码 | 错误码 | 说明 |
|--------|--------|------|
| 404 | RES_001 | 资源不存在 |
| 401 | AUTH_001 | 未登录或 Token 过期 |

---

### 2.3 创建资源

#### 基本信息

| 属性 | 值 |
|------|-----|
| 路径 | `POST /api/v1/{resources}` |
| 认证 | 需要 |
| 权限 | `{resource}:create` |

#### 请求体

**Body (application/json)**

| 字段 | 类型 | 必填 | 验证规则 | 说明 |
|------|------|------|----------|------|
| name | string | 是 | 2-50 字符 | 名称 |
| description | string | 否 | 最多 500 字符 | 描述 |
| type | string | 是 | enum: default, custom | 类型 |
| status | string | 否 | enum: active, inactive | 状态，默认 active |
| metadata | object | 否 | - | 扩展信息 |

**请求示例**

```json
{
  "name": "新资源名称",
  "description": "这是描述",
  "type": "default",
  "status": "active",
  "metadata": {
    "key": "value"
  }
}
```

#### 响应示例

**成功响应 (201)**

```json
{
  "code": 0,
  "message": "创建成功",
  "data": {
    "id": 2,
    "name": "新资源名称",
    "description": "这是描述",
    "type": "default",
    "status": "active",
    "createdAt": "2024-12-09T14:00:00Z"
  }
}
```

#### 错误响应

| 状态码 | 错误码 | 说明 |
|--------|--------|------|
| 400 | VAL_001 | 参数验证失败 |
| 409 | RES_002 | 名称已存在 |
| 401 | AUTH_001 | 未登录或 Token 过期 |

---

### 2.4 更新资源

#### 基本信息

| 属性 | 值 |
|------|-----|
| 路径 | `PUT /api/v1/{resources}/:id` |
| 认证 | 需要 |
| 权限 | `{resource}:update` |

#### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | integer | 是 | 资源 ID |

#### 请求体

**Body (application/json)**

| 字段 | 类型 | 必填 | 验证规则 | 说明 |
|------|------|------|----------|------|
| name | string | 否 | 2-50 字符 | 名称 |
| description | string | 否 | 最多 500 字符 | 描述 |
| type | string | 否 | enum: default, custom | 类型 |
| status | string | 否 | enum: active, inactive | 状态 |
| metadata | object | 否 | - | 扩展信息 |

**请求示例**

```json
{
  "name": "更新后的名称",
  "status": "inactive"
}
```

#### 响应示例

**成功响应 (200)**

```json
{
  "code": 0,
  "message": "更新成功",
  "data": {
    "id": 1,
    "name": "更新后的名称",
    "description": "这是描述",
    "type": "default",
    "status": "inactive",
    "updatedAt": "2024-12-09T15:00:00Z"
  }
}
```

#### 错误响应

| 状态码 | 错误码 | 说明 |
|--------|--------|------|
| 400 | VAL_001 | 参数验证失败 |
| 404 | RES_001 | 资源不存在 |
| 409 | RES_002 | 名称已存在 |

---

### 2.5 删除资源

#### 基本信息

| 属性 | 值 |
|------|-----|
| 路径 | `DELETE /api/v1/{resources}/:id` |
| 认证 | 需要 |
| 权限 | `{resource}:delete` |

#### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | integer | 是 | 资源 ID |

#### 响应示例

**成功响应 (200)**

```json
{
  "code": 0,
  "message": "删除成功",
  "data": null
}
```

#### 错误响应

| 状态码 | 错误码 | 说明 |
|--------|--------|------|
| 404 | RES_001 | 资源不存在 |
| 409 | RES_003 | 资源被引用，无法删除 |

---

## 3. 数据模型

### 3.1 {Resource} 实体

```typescript
interface Resource {
  id: number;
  name: string;
  description?: string;
  type: 'default' | 'custom';
  status: 'active' | 'inactive';
  metadata?: Record<string, any>;
  createdAt: string;  // ISO 8601 格式
  updatedAt: string;
  createdBy?: {
    id: number;
    name: string;
  };
}
```

### 3.2 分页响应结构

```typescript
interface PaginatedResponse<T> {
  code: number;
  message: string;
  data: {
    list: T[];
    pagination: {
      page: number;
      pageSize: number;
      total: number;
      totalPages: number;
    };
  };
}
```

### 3.3 错误响应结构

```typescript
interface ErrorResponse {
  code: number;
  message: string;
  error: {
    code: string;        // 错误码
    details?: string;    // 详细信息
    fields?: {           // 字段验证错误
      [field: string]: string;
    };
  };
}
```

---

## 4. 错误码定义

### 4.1 通用错误码

| 错误码 | HTTP 状态码 | 说明 |
|--------|-------------|------|
| AUTH_001 | 401 | 未登录或 Token 过期 |
| AUTH_002 | 403 | 无权限访问 |
| VAL_001 | 400 | 参数验证失败 |
| SYS_001 | 500 | 系统内部错误 |

### 4.2 业务错误码

| 错误码 | HTTP 状态码 | 说明 |
|--------|-------------|------|
| RES_001 | 404 | 资源不存在 |
| RES_002 | 409 | 名称/编码重复 |
| RES_003 | 409 | 资源被引用 |
| RES_004 | 400 | 状态不允许此操作 |

---

## 5. 认证与授权

### 5.1 认证方式

```
Authorization: Bearer <access_token>
```

### 5.2 权限列表

| 权限 | 说明 |
|------|------|
| `{resource}:read` | 查看权限 |
| `{resource}:create` | 创建权限 |
| `{resource}:update` | 更新权限 |
| `{resource}:delete` | 删除权限 |

---

## 6. 特殊场景

### 6.1 批量操作

#### 批量删除

```
POST /api/v1/{resources}/batch-delete
```

**请求体**

```json
{
  "ids": [1, 2, 3]
}
```

**响应**

```json
{
  "code": 0,
  "message": "删除成功",
  "data": {
    "success": 2,
    "failed": 1,
    "errors": [
      { "id": 3, "reason": "资源被引用" }
    ]
  }
}
```

### 6.2 导出数据

#### 导出为 Excel

```
GET /api/v1/{resources}/export?format=xlsx
```

**Query Parameters**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| format | string | 是 | 导出格式：xlsx / csv |
| ids | string | 否 | 指定 ID，逗号分隔 |
| ... | - | 否 | 支持列表查询的筛选参数 |

---

## 7. Claude Code 执行指南

### 7.1 实现检查清单

- [ ] 路由已配置
- [ ] Controller 已实现
- [ ] Service 层已实现
- [ ] 参数验证已实现
- [ ] 权限检查已实现
- [ ] 错误处理已完成
- [ ] 日志记录已添加
- [ ] 单元测试已编写
- [ ] API 文档已更新

### 7.2 文件命名

```
# Controller
src/controllers/{resource}.controller.ts

# Service
src/services/{resource}.service.ts

# DTO
src/dto/{resource}.dto.ts

# Entity
src/entities/{resource}.entity.ts

# Route
src/routes/{resource}.routes.ts
```

### 7.3 代码模板

**Controller 模板**

```typescript
// src/controllers/{resource}.controller.ts
import { Request, Response, NextFunction } from 'express';
import { {Resource}Service } from '../services/{resource}.service';
import { Create{Resource}Dto, Update{Resource}Dto } from '../dto/{resource}.dto';

export class {Resource}Controller {
  private service: {Resource}Service;

  constructor() {
    this.service = new {Resource}Service();
  }

  // GET /api/v1/{resources}
  async list(req: Request, res: Response, next: NextFunction) {
    try {
      const { page, pageSize, keyword, status, sortBy, sortOrder } = req.query;
      const result = await this.service.list({ page, pageSize, keyword, status, sortBy, sortOrder });
      res.json({ code: 0, message: 'success', data: result });
    } catch (error) {
      next(error);
    }
  }

  // GET /api/v1/{resources}/:id
  async getById(req: Request, res: Response, next: NextFunction) {
    try {
      const { id } = req.params;
      const result = await this.service.getById(Number(id));
      res.json({ code: 0, message: 'success', data: result });
    } catch (error) {
      next(error);
    }
  }

  // POST /api/v1/{resources}
  async create(req: Request, res: Response, next: NextFunction) {
    try {
      const dto: Create{Resource}Dto = req.body;
      const result = await this.service.create(dto);
      res.status(201).json({ code: 0, message: '创建成功', data: result });
    } catch (error) {
      next(error);
    }
  }

  // PUT /api/v1/{resources}/:id
  async update(req: Request, res: Response, next: NextFunction) {
    try {
      const { id } = req.params;
      const dto: Update{Resource}Dto = req.body;
      const result = await this.service.update(Number(id), dto);
      res.json({ code: 0, message: '更新成功', data: result });
    } catch (error) {
      next(error);
    }
  }

  // DELETE /api/v1/{resources}/:id
  async delete(req: Request, res: Response, next: NextFunction) {
    try {
      const { id } = req.params;
      await this.service.delete(Number(id));
      res.json({ code: 0, message: '删除成功', data: null });
    } catch (error) {
      next(error);
    }
  }
}
```

---

## CHANGELOG

| 版本 | 日期 | 作者 | 变更内容 |
|------|------|------|----------|
| v1.0 | {日期} | {作者} | 初始版本 |
