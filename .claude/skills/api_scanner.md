# api_scanner

API 路由扫描 Skill - 从代码中提取 API 端点定义

## 用途

扫描项目的路由/控制器代码，提取 API 端点信息，返回结构化数据。

## 输入契约

```yaml
input:
  project_path: string        # 项目根目录路径
  include_patterns: [string]  # 可选：包含的文件模式
  exclude_patterns: [string]  # 可选：排除的文件模式
```

## 输出契约

```yaml
output:
  success: boolean
  data:
    # 检测到的框架
    framework: string         # fastapi | express | django | flask | nestjs | gin | ...
    language: string          # python | javascript | typescript | go | java | ...

    total_endpoints: number

    # 端点列表
    endpoints:
      - method: string        # GET | POST | PUT | DELETE | PATCH | OPTIONS | HEAD
        path: string          # /api/users/:id 或 /api/users/{id}
        handler: string       # 处理函数名
        file: string          # 源文件路径
        line: number          # 行号

        # 请求信息（尽可能提取）
        params:               # 路径参数
          - name: string
            type: string | null
            required: boolean
        query:                # 查询参数
          - name: string
            type: string | null
            required: boolean
        body:                 # 请求体
          type: string | null     # 类型名或 "object"
          schema: object | null   # 如果能提取到具体结构

        # 响应信息
        response:
          type: string | null
          status_codes: [number]  # 可能的状态码

        # 元数据
        middleware: [string]      # 中间件/装饰器列表
        auth_required: boolean    # 是否需要认证（推断）
        deprecated: boolean       # 是否已废弃
        tags: [string]            # API 分组标签
        description: string | null

        # 置信度
        confidence: number        # 0.0 - 1.0
        confidence_reason: string

    # 按模块/路由器分组
    modules:
      - name: string
        base_path: string         # 路由前缀
        file: string
        endpoint_count: number

    # 扫描统计
    stats:
      files_scanned: number
      endpoints_found: number
      high_confidence: number     # >= 0.8
      medium_confidence: number   # 0.5 - 0.8
      low_confidence: number      # < 0.5
      by_method:
        GET: number
        POST: number
        PUT: number
        DELETE: number
        PATCH: number

  error: string | null
```

## 能力边界

### 能做
- 识别各种框架的路由定义语法
- 提取 HTTP 方法、路径、处理函数
- 推断路径参数和查询参数
- 识别认证中间件/装饰器
- 从类型注解或文档提取请求/响应结构

### 不能做
- 执行代码或调用 API
- 解析动态生成的路由
- 访问运行时状态
- 100% 准确提取复杂的类型信息

## 执行流程

```
1. 检测框架类型
   └─ 读取配置文件或导入语句

2. 定位路由文件
   └─ 根据项目结构查找（routes/, controllers/, api/, views/ 等）

3. 解析每个文件
   └─ 识别路由定义模式（装饰器、函数调用等）
   └─ 提取方法、路径、处理函数

4. 提取参数信息
   └─ 从路径提取路径参数
   └─ 从代码提取查询参数和请求体

5. 检测认证需求
   └─ 识别认证相关的中间件/装饰器

6. 组织输出
   └─ 按模块分组
   └─ 计算统计信息
```

## 使用示例

```yaml
# FastAPI 项目示例
output:
  success: true
  data:
    framework: "fastapi"
    language: "python"
    total_endpoints: 12

    endpoints:
      - method: "POST"
        path: "/api/v1/users"
        handler: "create_user"
        file: "app/api/users.py"
        line: 25
        body:
          type: "UserCreate"
        response:
          type: "UserResponse"
          status_codes: [201]
        auth_required: false
        confidence: 0.95

      - method: "GET"
        path: "/api/v1/users/{user_id}"
        handler: "get_user"
        file: "app/api/users.py"
        line: 45
        params:
          - { name: "user_id", type: "str", required: true }
        response:
          type: "UserResponse"
        auth_required: true
        confidence: 0.95

    modules:
      - { name: "users", base_path: "/api/v1/users", file: "app/api/users.py", endpoint_count: 5 }
      - { name: "auth", base_path: "/api/v1/auth", file: "app/api/auth.py", endpoint_count: 4 }

# Express 项目示例
output:
  success: true
  data:
    framework: "express"
    language: "typescript"
    total_endpoints: 8

    endpoints:
      - method: "GET"
        path: "/api/users/:id"
        handler: "getUserById"
        file: "src/routes/user.ts"
        line: 15
        params:
          - { name: "id", type: "string", required: true }
        middleware: ["authMiddleware", "validateParams"]
        auth_required: true
        confidence: 0.85
```

## 置信度规则

```yaml
high (>= 0.8):
  - 有完整的类型注解
  - 有 OpenAPI/Swagger 文档
  - 框架提供的元数据完整

medium (0.5 - 0.8):
  - 能识别路由和方法
  - 部分参数信息可提取
  - 无完整类型定义

low (< 0.5):
  - 只能识别路由路径
  - 动态路由或复杂模式
  - 无法确定参数类型
```

## 错误处理

```yaml
# 无法识别框架
output:
  success: true
  data:
    framework: "unknown"
    endpoints: []
  warning: "Could not detect web framework, no API routes found"

# 部分文件解析失败
output:
  success: true
  data:
    # ... 正常数据
  warnings:
    - "Failed to parse src/routes/legacy.py: SyntaxError"
```
