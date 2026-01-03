# tech_stack_detector

技术栈检测 Skill - 从项目配置和代码中识别技术栈

## 用途

分析项目的配置文件和代码，识别使用的技术栈，返回结构化数据。

## 输入契约

```yaml
input:
  project_path: string  # 项目根目录路径
```

## 输出契约

```yaml
output:
  success: boolean
  data:
    # 项目基本信息
    project_name: string
    version: string | null
    description: string | null

    # 语言和运行时
    language:
      name: string        # python | javascript | typescript | go | java | rust | ...
      version: string | null

    # 包管理器
    package_manager:
      name: string        # npm | yarn | pnpm | pip | poetry | cargo | go mod | maven | ...
      config_file: string # package.json | pyproject.toml | Cargo.toml | ...

    # 框架（可多个）
    frameworks:
      - name: string      # fastapi | express | django | vue | react | nestjs | ...
        category: string  # web-backend | web-frontend | fullstack | cli | library
        version: string | null

    # 数据库/ORM
    database:
      orm: string | null           # sqlalchemy | prisma | typeorm | django-orm | ...
      database_type: string | null # postgresql | mysql | mongodb | sqlite | ...
      inferred_from: string        # 推断来源

    # UI/样式
    ui:
      library: string | null       # element-plus | antd | tailwind | bootstrap | ...
      css_framework: string | null

    # 构建工具
    build_tool:
      name: string | null   # vite | webpack | esbuild | setuptools | cargo | ...
      version: string | null

    # 测试框架
    test_framework:
      name: string | null   # pytest | vitest | jest | go test | ...

    # 项目类型推断
    project_type:
      is_frontend: boolean
      is_backend: boolean
      is_fullstack: boolean
      is_library: boolean
      is_monorepo: boolean

    # 检测到的配置文件
    config_files:
      - path: string
        type: string

    # 置信度
    confidence: number        # 0.0 - 1.0
    confidence_reason: string

  error: string | null
```

## 能力边界

### 能做
- 从配置文件（package.json, pyproject.toml, Cargo.toml 等）提取依赖信息
- 从代码导入语句推断使用的框架
- 识别项目结构类型（前端/后端/全栈/库）
- 检测 monorepo 结构

### 不能做
- 运行项目或执行构建命令
- 访问私有包仓库信息
- 推断业务逻辑

## 执行流程

```
1. 检测项目语言
   └─ 查找配置文件（package.json, pyproject.toml, go.mod, Cargo.toml 等）

2. 读取依赖列表
   └─ 从配置文件提取 dependencies

3. 识别框架
   └─ 根据依赖名称推断（Claude 自行判断）

4. 推断数据库
   └─ 从 ORM 依赖或配置文件推断

5. 分类项目类型
   └─ 根据框架和目录结构推断

6. 计算置信度
   └─ 根据信息完整度评分
```

## 使用示例

```yaml
# Node.js 项目示例输出
output:
  success: true
  data:
    project_name: "my-app"
    language: { name: "typescript", version: "5.0" }
    package_manager: { name: "pnpm", config_file: "package.json" }
    frameworks:
      - { name: "vue", category: "web-frontend", version: "3.5" }
    database:
      orm: "prisma"
      database_type: "postgresql"
      inferred_from: "prisma/schema.prisma"
    build_tool: { name: "vite", version: "5.0" }
    project_type:
      is_frontend: true
      is_backend: false
    confidence: 0.95

# Python 项目示例输出
output:
  success: true
  data:
    project_name: "api-server"
    language: { name: "python", version: "3.11" }
    package_manager: { name: "poetry", config_file: "pyproject.toml" }
    frameworks:
      - { name: "fastapi", category: "web-backend", version: "0.100" }
    database:
      orm: "sqlalchemy"
      database_type: "postgresql"
      inferred_from: "alembic.ini"
    test_framework: { name: "pytest" }
    project_type:
      is_backend: true
    confidence: 0.90
```

## 错误处理

```yaml
# 找不到配置文件
output:
  success: false
  error: "No package manager config found (package.json, pyproject.toml, etc.)"

# 无法识别语言
output:
  success: true
  data:
    language: { name: "unknown" }
    confidence: 0.3
    confidence_reason: "无法从配置文件确定项目语言"
```
