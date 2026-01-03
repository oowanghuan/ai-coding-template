# contract_resolver

接口契约解析 Skill - 在编写接口代码前查找真实的字段定义

## 用途

解决 AI 编程时「猜字段名」的问题。在写前端接口调用、Mock 数据、类型定义时，先查找 SSoT（单一信息来源），确保字段名、类型与后端一致。

## 使用场景

```
场景 1: 写前端组件
─────────────────
❌ 之前: AI 猜测 { userName: string }
✅ 之后: 先查 contract → { username: string }

场景 2: 写 Mock 数据
─────────────────
❌ 之前: 手写 mock，字段名可能与后端不一致
✅ 之后: 从 contract 生成，保证一致

场景 3: Mock → Real 切换
─────────────────
❌ 之前: 切换后字段对不上，页面空白
✅ 之后: 验证 mock 与 real 的 contract 一致性
```

## 输入契约

```yaml
input:
  # 查询模式（二选一）
  entity: string | null       # 按实体名查询: "User" | "Order" | "Agent"
  endpoint: string | null     # 按端点查询: "GET /api/users" | "POST /api/orders"

  # 项目路径
  project_path: string

  # 可选参数
  include_nested: boolean     # 是否包含嵌套对象的字段（默认 true）
  format: string              # 输出格式: "fields" | "typescript" | "mock"（默认 "fields"）
```

## 输出契约

```yaml
output:
  success: boolean
  data:
    # 来源信息
    source:
      type: string            # "api_spec" | "backend_schema" | "openapi" | "typescript" | "contract_file"
      file: string            # 来源文件路径
      line: number | null     # 行号（如果适用）

    # 实体信息
    entity:
      name: string            # "User"
      description: string | null

    # 字段列表（SSoT）
    fields:
      - name: string          # 真实字段名（如 "username" 不是 "userName"）
        type: string          # 类型: "string" | "number" | "boolean" | "datetime" | "object" | "array"
        required: boolean
        nullable: boolean
        description: string | null
        default: any | null
        format: string | null       # "email" | "uuid" | "date-time" | ...
        enum: [string] | null       # 枚举值
        nested_fields: [field] | null  # 嵌套对象的字段

    # API 端点信息（如果查询的是端点）
    endpoint:
      method: string          # "GET" | "POST" | ...
      path: string            # "/api/users/{id}"
      request_body: object | null
      response_body: object | null
      status_codes: [number]

    # 格式化输出（根据 format 参数）
    formatted:
      typescript: string | null     # TypeScript 类型定义
      mock: object | null           # Mock 数据示例
      zod: string | null            # Zod schema

    # 置信度
    confidence: number
    confidence_reason: string

  error: string | null
  warnings: [string] | null
```

## SSoT 查找优先级

按以下顺序查找，找到即返回：

```
1. 项目 Contract 文件
   └─ shared/contracts/{entity}.yaml
   └─ contracts/{entity}.json

2. OpenAPI / Swagger
   └─ openapi.yaml / swagger.json
   └─ docs/api/openapi.yaml

3. API Spec 文档
   └─ docs/{feature}/20_API_SPEC.md
   └─ docs/{feature}/21_UI_FLOW_SPEC.md

4. 后端 Schema 定义
   └─ Python: app/schemas/{entity}.py (Pydantic)
   └─ TypeScript: src/schemas/{entity}.ts
   └─ Prisma: prisma/schema.prisma

5. 后端 Model 定义
   └─ Python: app/models/{entity}.py (SQLAlchemy)
   └─ TypeScript: src/models/{entity}.ts

6. 前端类型定义（最低优先级）
   └─ src/types/{entity}.ts
   └─ src/api/types.ts
```

## 能力边界

### 能做
- 从多种来源查找实体/端点的字段定义
- 返回统一格式的字段列表
- 生成 TypeScript 类型定义
- 生成 Mock 数据示例
- 检测字段名命名风格（camelCase, snake_case）

### 不能做
- 执行 API 调用
- 访问数据库
- 解析运行时动态生成的 Schema
- 保证 100% 准确（需人工验证）

## 执行流程

```
1. 解析查询参数
   └─ entity="User" 或 endpoint="GET /api/users"

2. 按优先级查找 SSoT
   └─ 依次检查各来源

3. 解析找到的定义
   └─ 提取字段名、类型、约束

4. 标准化输出
   └─ 统一字段格式

5. 生成格式化输出（可选）
   └─ TypeScript 类型
   └─ Mock 数据
```

## 使用示例

### 示例 1: 查询实体字段

```yaml
input:
  entity: "User"
  project_path: "./backend"

output:
  success: true
  data:
    source:
      type: "backend_schema"
      file: "app/schemas/user.py"
      line: 15

    entity:
      name: "User"
      description: "用户信息"

    fields:
      - name: "id"
        type: "string"
        required: true
        format: "uuid"
      - name: "username"          # 注意: 是 username 不是 userName
        type: "string"
        required: true
      - name: "email"
        type: "string"
        required: true
        format: "email"
      - name: "created_at"        # 注意: 是 snake_case
        type: "datetime"
        required: true
      - name: "role"
        type: "string"
        required: true
        enum: ["user", "admin", "super_admin"]

    formatted:
      typescript: |
        interface User {
          id: string;
          username: string;
          email: string;
          created_at: string;
          role: 'user' | 'admin' | 'super_admin';
        }
      mock: |
        {
          "id": "550e8400-e29b-41d4-a716-446655440000",
          "username": "zhangsan",
          "email": "zhangsan@example.com",
          "created_at": "2026-01-03T10:00:00Z",
          "role": "user"
        }

    confidence: 0.95
    confidence_reason: "Pydantic schema 类型定义完整"
```

### 示例 2: 查询 API 端点

```yaml
input:
  endpoint: "GET /api/v1/users"
  project_path: "./backend"

output:
  success: true
  data:
    source:
      type: "api_spec"
      file: "docs/user-management/20_API_SPEC.md"

    endpoint:
      method: "GET"
      path: "/api/v1/users"
      request_body: null
      response_body:
        type: "object"
        properties:
          total: { type: "number" }
          page: { type: "number" }
          items: { type: "array", items: "User" }
      status_codes: [200, 401, 500]

    fields:
      # response.items[*] 的字段
      - name: "id"
        type: "string"
      - name: "username"
        type: "string"
      # ...

    confidence: 0.90
```

### 示例 3: 生成 Mock 数据

```yaml
input:
  entity: "Order"
  project_path: "./backend"
  format: "mock"

output:
  success: true
  data:
    source:
      type: "openapi"
      file: "openapi.yaml"

    formatted:
      mock: |
        {
          "id": "ord_123456",
          "user_id": "usr_789",
          "status": "pending",
          "total_amount": 299.99,
          "items": [
            {
              "product_id": "prod_001",
              "quantity": 2,
              "price": 149.99
            }
          ],
          "created_at": "2026-01-03T10:00:00Z"
        }

    confidence: 0.92
```

## 与其他 Skills 的配合

```
┌─────────────────┐
│  api_scanner    │ ──→ 扫描发现所有端点
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│contract_resolver│ ──→ 查询特定端点/实体的详细字段
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  前端代码编写   │ ──→ 使用正确的字段名
└─────────────────┘
```

## AI 协作规则建议

在 `CLAUDE.md` 中添加：

```markdown
## 接口编码规则

在编写以下代码时，必须先调用 contract_resolver skill：
- 前端接口调用代码（fetch, axios）
- 前端类型定义（interface, type）
- Mock 数据
- API 响应处理逻辑

示例流程：
1. 用户说「写一个用户列表组件」
2. 先查 contract: entity="User"
3. 得到真实字段名: username, created_at, ...
4. 按真实字段名写代码
```

## 错误处理

```yaml
# 找不到定义
output:
  success: false
  error: "Cannot find contract for entity 'User'"
  warnings:
    - "Searched: shared/contracts/, app/schemas/, prisma/schema.prisma"
    - "Consider creating a contract file or API spec"

# 多个来源冲突
output:
  success: true
  data:
    # ... 使用优先级最高的来源
  warnings:
    - "Found multiple definitions for 'User'"
    - "Using: app/schemas/user.py (priority 1)"
    - "Ignored: src/types/user.ts (priority 2)"
    - "Conflict: 'createdAt' vs 'created_at' - check naming convention"
```

## Mock 切换验证

用于验证 Mock 数据与真实 API 的一致性：

```yaml
input:
  mode: "validate_mock"
  mock_file: "src/mocks/users.json"
  entity: "User"
  project_path: "./backend"

output:
  success: true
  data:
    validation:
      status: "mismatch"
      issues:
        - field: "userName"
          expected: "username"
          issue: "命名不一致 (camelCase vs snake_case)"
        - field: "createdAt"
          expected: "created_at"
          issue: "命名不一致"
        - field: "avatar"
          expected: null
          issue: "Mock 中存在但 contract 中不存在"

      suggestion: |
        建议修改 Mock 数据:
        - userName → username
        - createdAt → created_at
        - 删除 avatar 字段
```
