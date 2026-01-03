# api_scanner

API 路由扫描 Skill - 从代码中提取 API 端点定义

## 用途

扫描后端项目的路由定义，提取 API 端点信息，返回结构化数据供文档生成使用。

## 输入

```yaml
input:
  project_path: string      # 项目根目录路径
  framework: string         # express | koa | nestjs | fastify | hono（可选，自动检测）
  include_patterns: [string] # 包含的文件模式（可选）
  exclude_patterns: [string] # 排除的文件模式（可选）
```

## 输出

```yaml
output:
  success: boolean
  data:
    framework: string
    total_endpoints: number

    # 端点列表
    endpoints:
      - method: string        # GET | POST | PUT | DELETE | PATCH
        path: string          # /api/users/:id
        handler: string       # 处理函数名
        file: string          # 源文件路径
        line: number          # 行号

        # 请求信息（尽可能提取）
        params:               # 路径参数
          - name: string
            type: string
            required: boolean
        query:                # 查询参数
          - name: string
            type: string
            required: boolean
        body:                 # 请求体
          type: string        # 类型名或内联定义
          schema: object      # JSON Schema（如果能提取）

        # 响应信息
        response:
          type: string
          schema: object

        # 元数据
        middleware: [string]  # 中间件列表
        auth_required: boolean # 是否需要认证
        deprecated: boolean

        # 置信度
        confidence: number    # 0.0 - 1.0
        confidence_reason: string

    # 按模块分组
    modules:
      - name: string
        base_path: string
        file: string
        endpoints: [endpoint_index]

    # 扫描统计
    stats:
      files_scanned: number
      endpoints_found: number
      high_confidence: number   # >= 0.8
      medium_confidence: number # 0.5 - 0.8
      low_confidence: number    # < 0.5

  error: string | null
```

## 框架检测规则

### Express

```javascript
// 检测模式
app.get('/path', handler)
app.post('/path', handler)
router.get('/path', handler)
router.post('/path', handler)

// 路由文件位置
src/routes/**/*.{js,ts}
src/router/**/*.{js,ts}
routes/**/*.{js,ts}
app.{js,ts}

// 中间件检测
app.use('/api', authMiddleware, router)
router.use(validateBody(schema))
```

### Koa

```javascript
// 检测模式
router.get('/path', handler)
router.post('/path', handler)

// 路由文件位置
src/routes/**/*.{js,ts}
src/router/**/*.{js,ts}
```

### NestJS

```typescript
// 检测模式（装饰器）
@Controller('users')
@Get(':id')
@Post()
@Put(':id')
@Delete(':id')
@Patch(':id')

// 路由文件位置
src/**/*.controller.ts

// 额外信息提取
@Body() dto: CreateUserDto    → body 类型
@Param('id') id: string       → params
@Query('page') page: number   → query
@UseGuards(AuthGuard)         → auth_required
```

### Fastify

```javascript
// 检测模式
fastify.get('/path', handler)
fastify.post('/path', { schema }, handler)
fastify.register(routes, { prefix: '/api' })

// 路由文件位置
src/routes/**/*.{js,ts}
```

### Hono

```javascript
// 检测模式
app.get('/path', handler)
app.post('/path', handler)
app.route('/api', apiRoutes)

// 路由文件位置
src/routes/**/*.{js,ts}
src/index.ts
```

## 参数提取规则

### 路径参数

```javascript
// 从路由路径提取
'/users/:id'        → { name: 'id', type: 'string', required: true }
'/posts/:id/comments/:commentId' → 两个参数

// NestJS 装饰器
@Param('id') id: string → { name: 'id', type: 'string' }
@Param('id', ParseIntPipe) id: number → { name: 'id', type: 'number' }
```

### 查询参数

```javascript
// 从代码推断
req.query.page      → { name: 'page', type: 'unknown' }
ctx.query.limit     → { name: 'limit', type: 'unknown' }

// TypeScript 类型
@Query() query: PaginationDto → 从 DTO 提取

// Zod/Joi Schema
z.object({ page: z.number() }) → { name: 'page', type: 'number' }
```

### 请求体

```javascript
// TypeScript 类型
@Body() dto: CreateUserDto → type: 'CreateUserDto'

// Zod Schema
const schema = z.object({
  name: z.string(),
  email: z.string().email()
})

// Joi Schema
Joi.object({
  name: Joi.string().required(),
  email: Joi.string().email()
})
```

## 置信度计算

```yaml
confidence_rules:
  high (>= 0.8):
    - 有 TypeScript 类型定义
    - 有 Zod/Joi 验证 schema
    - 有 JSDoc 注释
    - NestJS 装饰器完整

  medium (0.5 - 0.8):
    - 能识别路由和方法
    - 能推断部分参数
    - 无完整类型定义

  low (< 0.5):
    - 只能识别路由路径
    - 无法确定参数类型
    - 动态路由注册
```

## 扫描流程

```
1. 检测框架类型
   ├─ 读取 package.json
   └─ 或使用传入的 framework 参数

2. 定位路由文件
   ├─ 根据框架类型确定搜索模式
   └─ 应用 include/exclude patterns

3. 解析每个文件
   ├─ 使用正则匹配路由定义
   ├─ 提取 HTTP 方法和路径
   ├─ 提取处理函数名
   └─ 记录文件和行号

4. 提取参数信息
   ├─ 分析路径参数
   ├─ 查找查询参数使用
   ├─ 查找请求体类型
   └─ 查找响应类型

5. 检测中间件
   ├─ 查找 auth/guard 中间件
   ├─ 查找验证中间件
   └─ 标记 auth_required

6. 计算置信度
   ├─ 根据信息完整度打分
   └─ 记录置信度原因

7. 分组和统计
   ├─ 按模块/Controller 分组
   └─ 生成统计信息
```

## 使用示例

### 示例 1：Express 项目

```yaml
input:
  project_path: "./backend"
  framework: "express"

output:
  success: true
  data:
    framework: "express"
    total_endpoints: 12
    endpoints:
      - method: "GET"
        path: "/api/users"
        handler: "getUsers"
        file: "src/routes/user.ts"
        line: 15
        query:
          - name: "page"
            type: "number"
            required: false
          - name: "limit"
            type: "number"
            required: false
        response:
          type: "User[]"
        middleware: ["authMiddleware"]
        auth_required: true
        confidence: 0.85
        confidence_reason: "TypeScript 类型定义完整"

      - method: "GET"
        path: "/api/users/:id"
        handler: "getUserById"
        file: "src/routes/user.ts"
        line: 28
        params:
          - name: "id"
            type: "string"
            required: true
        response:
          type: "User"
        confidence: 0.9

    modules:
      - name: "user"
        base_path: "/api/users"
        file: "src/routes/user.ts"
        endpoints: [0, 1, 2, 3]

    stats:
      files_scanned: 5
      endpoints_found: 12
      high_confidence: 8
      medium_confidence: 3
      low_confidence: 1
```

### 示例 2：NestJS 项目

```yaml
input:
  project_path: "./backend"
  framework: "nestjs"

output:
  success: true
  data:
    framework: "nestjs"
    total_endpoints: 20
    endpoints:
      - method: "POST"
        path: "/users"
        handler: "create"
        file: "src/users/users.controller.ts"
        line: 25
        body:
          type: "CreateUserDto"
          schema:
            type: "object"
            properties:
              name: { type: "string" }
              email: { type: "string", format: "email" }
            required: ["name", "email"]
        response:
          type: "User"
        middleware: []
        auth_required: false
        confidence: 0.95
        confidence_reason: "NestJS 装饰器 + DTO 类型完整"
```

## 错误处理

```yaml
# 无法识别框架
output:
  success: false
  error: "Cannot detect framework. Please specify --framework parameter"

# 没有找到路由文件
output:
  success: true
  data:
    framework: "express"
    total_endpoints: 0
    endpoints: []
    stats:
      files_scanned: 0
      endpoints_found: 0
  warning: "No route files found. Searched: src/routes/, routes/"

# 部分文件解析失败
output:
  success: true
  data:
    # ... 正常数据
  warnings:
    - "Failed to parse src/routes/legacy.js: SyntaxError at line 42"
```

## 限制和说明

1. **静态分析**：只能分析静态定义的路由，动态注册的路由可能遗漏
2. **类型推断**：JavaScript 项目的类型推断准确度较低
3. **复杂路由**：嵌套路由、路由组合可能需要额外处理
4. **中间件链**：深层中间件链可能无法完全解析

## 关联 Skills

- `tech_stack_detector` - 检测框架类型
- `schema_scanner` - 扫描相关的数据模型
