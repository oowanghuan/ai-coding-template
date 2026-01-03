# tech_stack_detector

技术栈检测 Skill - 分析项目的技术栈、依赖和构建工具

## 用途

从项目配置文件中提取技术栈信息，返回结构化数据供其他命令使用。

## 输入

```yaml
input:
  project_path: string  # 项目根目录路径
```

## 输出

```yaml
output:
  success: boolean
  data:
    project_name: string
    version: string
    description: string

    # 核心技术栈
    framework:
      name: string        # vue | react | angular | express | nestjs | ...
      version: string

    language:
      name: string        # typescript | javascript
      version: string

    build_tool:
      name: string        # vite | webpack | rollup | esbuild | ...
      version: string

    # 依赖分类
    dependencies:
      ui_library:         # element-plus | antd | vuetify | ...
        name: string
        version: string
      state_management:   # pinia | vuex | redux | zustand | ...
        name: string
        version: string
      router:             # vue-router | react-router | ...
        name: string
        version: string
      orm:                # prisma | typeorm | sequelize | drizzle | ...
        name: string
        version: string
      database:           # postgresql | mysql | mongodb | sqlite | ...
        name: string
        inferred_from: string  # 从 ORM 配置推断
      test_framework:     # vitest | jest | mocha | ...
        name: string
        version: string
      http_client:        # axios | fetch | got | ...
        name: string
        version: string

    # 原始依赖列表
    all_dependencies:
      production: [{name: string, version: string}]
      development: [{name: string, version: string}]

    # 项目类型推断
    project_type:
      is_frontend: boolean
      is_backend: boolean
      is_fullstack: boolean
      is_monorepo: boolean

    # 配置文件存在性
    config_files:
      - path: string
        type: string  # package.json | tsconfig.json | vite.config.ts | ...

  error: string | null
```

## 检测逻辑

### 1. 读取 package.json

```
必需文件：{project_path}/package.json

提取：
  - name, version, description
  - dependencies
  - devDependencies
  - scripts（用于推断构建工具）
```

### 2. 检测框架

```
检测优先级：

前端框架：
  vue        → dependencies 包含 "vue"
  react      → dependencies 包含 "react"
  angular    → dependencies 包含 "@angular/core"
  svelte     → dependencies 包含 "svelte"
  solid      → dependencies 包含 "solid-js"

后端框架：
  nestjs     → dependencies 包含 "@nestjs/core"
  express    → dependencies 包含 "express"
  koa        → dependencies 包含 "koa"
  fastify    → dependencies 包含 "fastify"
  hono       → dependencies 包含 "hono"

全栈框架：
  nextjs     → dependencies 包含 "next"
  nuxt       → dependencies 包含 "nuxt"
  remix      → dependencies 包含 "@remix-run/react"
```

### 3. 检测语言

```
TypeScript：
  - devDependencies 包含 "typescript"
  - 或存在 tsconfig.json

JavaScript：
  - 默认（无 TypeScript 配置）
```

### 4. 检测构建工具

```
vite       → devDependencies 包含 "vite"
webpack    → devDependencies 包含 "webpack"
rollup     → devDependencies 包含 "rollup"
esbuild    → devDependencies 包含 "esbuild"
parcel     → devDependencies 包含 "parcel"
turbopack  → devDependencies 包含 "turbo"
```

### 5. 检测 ORM

```
prisma     → dependencies 包含 "@prisma/client"
             → 检查 prisma/schema.prisma
typeorm    → dependencies 包含 "typeorm"
sequelize  → dependencies 包含 "sequelize"
mongoose   → dependencies 包含 "mongoose"
drizzle    → dependencies 包含 "drizzle-orm"
knex       → dependencies 包含 "knex"
```

### 6. 推断数据库

```
从 ORM 配置推断：
  prisma     → 读取 schema.prisma 的 datasource
  typeorm    → 读取 ormconfig 或 data-source.ts
  mongoose   → MongoDB

从依赖推断：
  pg         → PostgreSQL
  mysql2     → MySQL
  better-sqlite3 → SQLite
  mongodb    → MongoDB
  redis      → Redis（缓存）
```

### 7. 检测 UI 库

```
element-plus    → dependencies 包含 "element-plus"
antd            → dependencies 包含 "antd"
vuetify         → dependencies 包含 "vuetify"
naive-ui        → dependencies 包含 "naive-ui"
shadcn          → 检查 components.json
tailwind        → devDependencies 包含 "tailwindcss"
```

### 8. 检测状态管理

```
Vue:
  pinia       → dependencies 包含 "pinia"
  vuex        → dependencies 包含 "vuex"

React:
  redux       → dependencies 包含 "@reduxjs/toolkit" 或 "redux"
  zustand     → dependencies 包含 "zustand"
  jotai       → dependencies 包含 "jotai"
  recoil      → dependencies 包含 "recoil"
  mobx        → dependencies 包含 "mobx"
```

### 9. 检测测试框架

```
vitest      → devDependencies 包含 "vitest"
jest        → devDependencies 包含 "jest"
mocha       → devDependencies 包含 "mocha"
playwright  → devDependencies 包含 "@playwright/test"
cypress     → devDependencies 包含 "cypress"
```

### 10. 判断项目类型

```
is_frontend：
  - 有前端框架（vue/react/angular）
  - 无后端框架

is_backend：
  - 有后端框架（express/nestjs/koa）
  - 无前端框架

is_fullstack：
  - 同时有前端和后端框架
  - 或使用全栈框架（next/nuxt）

is_monorepo：
  - 存在 pnpm-workspace.yaml
  - 或 package.json 有 workspaces 字段
  - 或存在 lerna.json
```

## 配置文件扫描

```
扫描以下配置文件：
  - package.json（必需）
  - tsconfig.json
  - vite.config.ts / vite.config.js
  - webpack.config.js
  - next.config.js / next.config.mjs
  - nuxt.config.ts
  - prisma/schema.prisma
  - .env / .env.example
  - docker-compose.yml
  - Dockerfile
```

## 使用示例

### 示例 1：Vue 3 前端项目

```yaml
input:
  project_path: "./demos/coding-gui"

output:
  success: true
  data:
    project_name: "coding-gui"
    version: "0.0.0"
    framework:
      name: "vue"
      version: "^3.5.24"
    language:
      name: "typescript"
      version: "~5.9.3"
    build_tool:
      name: "vite"
      version: "^7.2.4"
    dependencies:
      ui_library:
        name: "element-plus"
        version: "^2.12.0"
      state_management:
        name: "pinia"
        version: "^3.0.4"
      router:
        name: "vue-router"
        version: "^4.6.4"
    project_type:
      is_frontend: true
      is_backend: false
      is_fullstack: false
```

### 示例 2：NestJS 后端项目

```yaml
input:
  project_path: "./backend"

output:
  success: true
  data:
    project_name: "my-backend"
    version: "1.0.0"
    framework:
      name: "nestjs"
      version: "^10.0.0"
    language:
      name: "typescript"
      version: "^5.0.0"
    dependencies:
      orm:
        name: "prisma"
        version: "^5.0.0"
      database:
        name: "postgresql"
        inferred_from: "prisma/schema.prisma"
    project_type:
      is_frontend: false
      is_backend: true
      is_fullstack: false
```

## 错误处理

```yaml
# package.json 不存在
output:
  success: false
  error: "package.json not found at {project_path}"

# package.json 解析失败
output:
  success: false
  error: "Failed to parse package.json: {error_message}"

# 无法识别框架
output:
  success: true
  data:
    framework:
      name: "unknown"
      version: null
    # 其他字段正常返回
```

## 注意事项

1. **只读操作**：不修改任何文件
2. **容错处理**：单个检测失败不影响整体
3. **版本提取**：保留原始版本字符串（如 `^3.5.24`）
4. **推断标记**：通过 `inferred_from` 标记推断来源
