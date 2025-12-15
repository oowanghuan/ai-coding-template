# DESIGN_TEMPLATE.md
# 详细设计文档模板

---

> **使用说明**
> 1. 复制此模板到功能目录，重命名为 `40_DESIGN_FINAL.md`
> 2. 根据功能复杂度增删章节
> 3. Demo 评审通过后填写
> 4. 删除本使用说明块

---

# 40_DESIGN_FINAL.md
# {功能名称} - 详细设计

> 版本：v1.0
> 最后更新：{YYYY-MM-DD}
> 状态：{Draft | Review | Approved}
> 设计者：{@username}
> 关联文档：`21_UI_FLOW_SPEC.md`, `20_API_SPEC.md`, `30_DEMO_REVIEW.md`

---

## 1. 概述

### 1.1 设计目标

{本设计要达成的技术目标}

### 1.2 设计约束

| 约束类型 | 描述 |
|----------|------|
| 技术栈 | Vue 3 + Element Plus / Node.js + Express |
| 数据库 | PostgreSQL / Supabase |
| 性能要求 | 列表接口 < 200ms，表单提交 < 500ms |
| 安全要求 | 需要认证、RBAC 权限控制 |

### 1.3 变更记录

| 变更 | 原设计 | 新设计 | 原因 |
|------|--------|--------|------|
| {变更点} | {原内容} | {新内容} | {来自 Demo 评审} |

---

## 2. 架构设计

### 2.1 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                          前端 (Vue 3)                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Views     │  │  Components │  │   Stores    │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         后端 (Node.js)                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  Controllers│  │   Services  │  │Repositories │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ SQL
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        数据库 (PostgreSQL)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Tables    │  │   Indexes   │  │    RLS      │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 目录结构

**前端**

```
src/
├── views/{feature}/
│   ├── index.vue           # 列表页
│   ├── Detail.vue          # 详情页
│   └── components/
│       └── FormDialog.vue  # 表单弹窗
├── api/{feature}.js        # API 调用
├── stores/{feature}.js     # 状态管理（如需要）
└── types/{feature}.d.ts    # 类型定义
```

**后端**

```
src/
├── controllers/{feature}.controller.ts
├── services/{feature}.service.ts
├── repositories/{feature}.repository.ts
├── dto/{feature}.dto.ts
├── entities/{feature}.entity.ts
└── routes/{feature}.routes.ts
```

---

## 3. 数据模型设计

### 3.1 ER 图

```
┌─────────────────────┐
│    {table_name}     │
├─────────────────────┤
│ id          PK      │
│ name        varchar │
│ description text    │
│ status      enum    │
│ type        enum    │
│ created_by  FK      │──────┐
│ created_at  timestamp     │
│ updated_at  timestamp     │
│ deleted_at  timestamp     │
└─────────────────────┘      │
                             │
┌─────────────────────┐      │
│       users         │◀─────┘
├─────────────────────┤
│ id          PK      │
│ name        varchar │
│ email       varchar │
└─────────────────────┘
```

### 3.2 表结构定义

**{table_name} 表**

| 字段 | 类型 | 约束 | 默认值 | 说明 |
|------|------|------|--------|------|
| id | bigint | PK, AUTO_INCREMENT | - | 主键 |
| name | varchar(100) | NOT NULL | - | 名称 |
| description | text | - | NULL | 描述 |
| status | varchar(20) | NOT NULL | 'active' | 状态：active/inactive |
| type | varchar(50) | NOT NULL | 'default' | 类型 |
| created_by | bigint | FK → users.id | - | 创建人 |
| created_at | timestamp | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | timestamp | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |
| deleted_at | timestamp | - | NULL | 软删除时间 |

**索引设计**

| 索引名 | 字段 | 类型 | 说明 |
|--------|------|------|------|
| idx_{table}_status | status | BTREE | 状态筛选 |
| idx_{table}_created_at | created_at | BTREE | 时间排序 |
| idx_{table}_name | name | BTREE | 名称搜索 |

### 3.3 Migration 脚本

```sql
-- Migration: create_{table_name}_table
-- Version: 20241210001

CREATE TABLE IF NOT EXISTS {table_name} (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    type VARCHAR(50) NOT NULL DEFAULT 'default',
    created_by BIGINT REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- 索引
CREATE INDEX idx_{table}_status ON {table_name}(status);
CREATE INDEX idx_{table}_created_at ON {table_name}(created_at DESC);
CREATE INDEX idx_{table}_name ON {table_name}(name);

-- 更新时间触发器
CREATE TRIGGER update_{table}_updated_at
    BEFORE UPDATE ON {table_name}
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- RLS 策略
ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;

CREATE POLICY "{table}_select_policy" ON {table_name}
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "{table}_insert_policy" ON {table_name}
    FOR INSERT WITH CHECK (auth.uid() = created_by);

CREATE POLICY "{table}_update_policy" ON {table_name}
    FOR UPDATE USING (auth.uid() = created_by);

CREATE POLICY "{table}_delete_policy" ON {table_name}
    FOR DELETE USING (auth.uid() = created_by);
```

---

## 4. API 契约

### 4.1 接口清单

| 接口 | 方法 | 路径 | 认证 | 权限 |
|------|------|------|------|------|
| 列表查询 | GET | `/api/v1/{resources}` | 是 | read |
| 详情查询 | GET | `/api/v1/{resources}/:id` | 是 | read |
| 创建 | POST | `/api/v1/{resources}` | 是 | create |
| 更新 | PUT | `/api/v1/{resources}/:id` | 是 | update |
| 删除 | DELETE | `/api/v1/{resources}/:id` | 是 | delete |

### 4.2 请求/响应契约

详见 `20_API_SPEC.md`，本节补充实现细节：

**分页规则**
- 默认 pageSize: 20
- 最大 pageSize: 100
- 超出范围自动修正

**软删除**
- 删除操作设置 deleted_at
- 查询默认排除已删除记录
- 管理员可查看已删除记录

---

## 5. 前端设计

### 5.1 组件设计

| 组件 | 路径 | 职责 |
|------|------|------|
| ListView | views/{feature}/index.vue | 列表页主组件 |
| DetailView | views/{feature}/Detail.vue | 详情页主组件 |
| FormDialog | views/{feature}/components/FormDialog.vue | 新增/编辑表单 |

### 5.2 状态管理

```typescript
// stores/{feature}.ts
import { defineStore } from 'pinia'

interface State {
  list: Resource[]
  current: Resource | null
  loading: boolean
  pagination: Pagination
}

export const use{Feature}Store = defineStore('{feature}', {
  state: (): State => ({
    list: [],
    current: null,
    loading: false,
    pagination: { page: 1, pageSize: 20, total: 0 }
  }),

  actions: {
    async fetchList(params: ListParams) {
      this.loading = true
      try {
        const res = await api.getList(params)
        this.list = res.data.list
        this.pagination = res.data.pagination
      } finally {
        this.loading = false
      }
    },

    async fetchById(id: number) {
      this.loading = true
      try {
        const res = await api.getById(id)
        this.current = res.data
      } finally {
        this.loading = false
      }
    }
  }
})
```

### 5.3 API 封装

```typescript
// api/{feature}.ts
import request from '@/utils/request'

const BASE_URL = '/api/v1/{resources}'

export interface ListParams {
  page?: number
  pageSize?: number
  keyword?: string
  status?: string
}

export const {feature}Api = {
  getList(params: ListParams) {
    return request.get(BASE_URL, { params })
  },

  getById(id: number) {
    return request.get(`${BASE_URL}/${id}`)
  },

  create(data: CreateDto) {
    return request.post(BASE_URL, data)
  },

  update(id: number, data: UpdateDto) {
    return request.put(`${BASE_URL}/${id}`, data)
  },

  delete(id: number) {
    return request.delete(`${BASE_URL}/${id}`)
  }
}
```

---

## 6. 后端设计

### 6.1 分层职责

| 层 | 职责 | 示例 |
|-----|------|------|
| Controller | 接收请求、参数校验、调用 Service、返回响应 | 路由处理、DTO 验证 |
| Service | 业务逻辑、事务管理、调用 Repository | 权限检查、数据转换 |
| Repository | 数据访问、SQL 查询 | CRUD 操作 |

### 6.2 关键逻辑

**创建流程**

```typescript
// services/{feature}.service.ts
async create(dto: CreateDto, userId: number): Promise<Resource> {
  // 1. 检查名称唯一性
  const existing = await this.repository.findByName(dto.name)
  if (existing) {
    throw new BusinessError('RES_002', '名称已存在')
  }

  // 2. 创建记录
  const entity = {
    ...dto,
    createdBy: userId,
    status: dto.status || 'active'
  }

  // 3. 保存并返回
  return this.repository.create(entity)
}
```

**删除流程**

```typescript
async delete(id: number, userId: number): Promise<void> {
  // 1. 检查记录是否存在
  const entity = await this.repository.findById(id)
  if (!entity) {
    throw new BusinessError('RES_001', '资源不存在')
  }

  // 2. 检查权限
  if (entity.createdBy !== userId) {
    throw new ForbiddenError('AUTH_002', '无权限删除')
  }

  // 3. 检查是否被引用
  const references = await this.checkReferences(id)
  if (references.length > 0) {
    throw new BusinessError('RES_003', '资源被引用，无法删除')
  }

  // 4. 软删除
  await this.repository.softDelete(id)
}
```

---

## 7. 安全设计

### 7.1 认证

- Token 类型：JWT / Supabase Auth
- 过期时间：1 小时
- 刷新机制：Refresh Token

### 7.2 授权

| 操作 | 权限 | 规则 |
|------|------|------|
| 查看列表 | read | 登录用户 |
| 查看详情 | read | 登录用户 |
| 创建 | create | 登录用户 |
| 编辑 | update | 创建者或管理员 |
| 删除 | delete | 创建者或管理员 |

### 7.3 数据安全

- 输入验证：使用 DTO + class-validator
- SQL 注入：使用参数化查询
- XSS 防护：前端输出转义
- CSRF 防护：SameSite Cookie

---

## 8. 性能设计

### 8.1 前端优化

| 优化项 | 方案 |
|--------|------|
| 列表加载 | 分页查询，每页 20 条 |
| 搜索防抖 | 300ms 防抖 |
| 组件懒加载 | 路由级别懒加载 |
| 状态缓存 | Pinia 持久化 |

### 8.2 后端优化

| 优化项 | 方案 |
|--------|------|
| 数据库查询 | 添加索引，避免 N+1 |
| 分页查询 | 使用 keyset 分页（大数据量） |
| 缓存 | Redis 缓存热点数据 |
| 连接池 | 数据库连接池 |

---

## 9. 错误处理

### 9.1 前端错误处理

```typescript
// 统一错误处理
request.interceptors.response.use(
  response => response,
  error => {
    const { status, data } = error.response || {}

    switch (status) {
      case 401:
        // Token 过期，跳转登录
        router.push('/login')
        break
      case 403:
        ElMessage.error('无权限访问')
        break
      case 404:
        ElMessage.error('资源不存在')
        break
      case 400:
        // 显示验证错误
        if (data.error?.fields) {
          // 表单字段错误
        } else {
          ElMessage.error(data.message)
        }
        break
      default:
        ElMessage.error(data?.message || '系统错误')
    }

    return Promise.reject(error)
  }
)
```

### 9.2 后端错误处理

```typescript
// 全局异常过滤器
app.use((err, req, res, next) => {
  if (err instanceof BusinessError) {
    return res.status(err.httpStatus).json({
      code: err.httpStatus,
      message: err.message,
      error: { code: err.code }
    })
  }

  // 未知错误
  console.error(err)
  return res.status(500).json({
    code: 500,
    message: '系统内部错误',
    error: { code: 'SYS_001' }
  })
})
```

---

## 10. 测试设计

### 10.1 单元测试

| 测试范围 | 覆盖率目标 |
|----------|------------|
| Service 层 | > 80% |
| Controller 层 | > 70% |
| 工具函数 | > 90% |

### 10.2 集成测试

| 测试场景 | 测试内容 |
|----------|----------|
| CRUD 操作 | 完整流程测试 |
| 权限控制 | 无权限访问返回 403 |
| 参数验证 | 无效参数返回 400 |
| 边界条件 | 不存在的 ID 返回 404 |

---

## 11. Claude Code 执行指南

### 11.1 实现顺序

```
1. 数据库层
   - 创建 Migration 脚本
   - 执行 Migration
   - 验证表结构

2. 后端层
   - Entity 定义
   - Repository 实现
   - Service 实现
   - Controller 实现
   - 路由配置

3. 前端层
   - API 封装
   - Store 实现（如需要）
   - 组件实现
   - 路由配置

4. 联调测试
   - API 联调
   - 功能测试
   - 错误处理测试
```

### 11.2 验收标准

- [ ] 数据库 Migration 执行成功
- [ ] API 接口可正常调用
- [ ] 前端页面功能正常
- [ ] 权限控制生效
- [ ] 错误处理正确
- [ ] 单元测试通过

---

## CHANGELOG

| 版本 | 日期 | 作者 | 变更内容 |
|------|------|------|----------|
| v1.0 | {日期} | {作者} | 初始版本 |
