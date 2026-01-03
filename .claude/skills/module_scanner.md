# module_scanner

模块结构扫描 Skill - 分析项目的目录结构和模块划分

## 用途

扫描项目目录结构，识别模块划分，返回结构化数据供项目分析使用。

## 输入

```yaml
input:
  project_path: string      # 项目根目录路径
  framework: string         # 框架类型（可选，影响识别策略）
  max_depth: number         # 最大扫描深度（默认 4）
  exclude_patterns: [string] # 排除的目录（默认 node_modules, dist, .git）
```

## 输出

```yaml
output:
  success: boolean
  data:
    project_type: string    # frontend | backend | fullstack | library | monorepo

    # 目录结构树
    tree:
      - path: string
        type: directory | file
        name: string
        children: [tree_node]
        file_count: number  # 目录下文件数
        has_index: boolean  # 是否有 index 文件

    # 识别的模块
    modules:
      - name: string        # 模块名称
        path: string        # 模块路径
        type: string        # component | view | service | util | store | ...
        entry_file: string  # 入口文件
        file_count: number  # 文件数量
        exports: [string]   # 导出的内容（如果能识别）
        description: string # 模块描述（从注释或 README 提取）

    # 前端特有结构
    frontend:
      components:
        path: string
        count: number
        items: [{name: string, path: string}]
      views:
        path: string
        count: number
        items: [{name: string, path: string}]
      stores:
        path: string
        count: number
        items: [{name: string, path: string}]
      composables:
        path: string
        count: number
        items: [{name: string, path: string}]
      hooks:
        path: string
        count: number
        items: [{name: string, path: string}]

    # 后端特有结构
    backend:
      controllers:
        path: string
        count: number
        items: [{name: string, path: string}]
      services:
        path: string
        count: number
        items: [{name: string, path: string}]
      models:
        path: string
        count: number
        items: [{name: string, path: string}]
      routes:
        path: string
        count: number
        items: [{name: string, path: string}]
      middlewares:
        path: string
        count: number
        items: [{name: string, path: string}]

    # 通用结构
    common:
      utils:
        path: string
        count: number
      types:
        path: string
        count: number
      constants:
        path: string
        count: number
      config:
        path: string
        count: number
      tests:
        path: string
        count: number

    # 统计
    stats:
      total_files: number
      total_directories: number
      by_extension:
        - ext: string
          count: number
      largest_modules: [{name: string, file_count: number}]

  error: string | null
```

## 目录识别规则

### 前端项目

```yaml
components:
  patterns:
    - src/components/**
    - components/**
  indicators:
    - 包含 .vue / .tsx / .jsx 文件
    - 文件名 PascalCase

views:
  patterns:
    - src/views/**
    - src/pages/**
    - pages/**
    - views/**
  indicators:
    - 通常对应路由

stores:
  patterns:
    - src/stores/**
    - src/store/**
    - store/**
  indicators:
    - 包含 pinia/vuex/redux 相关代码

composables:  # Vue 3
  patterns:
    - src/composables/**
    - src/hooks/**
  indicators:
    - 文件名以 use 开头

hooks:  # React
  patterns:
    - src/hooks/**
  indicators:
    - 文件名以 use 开头

assets:
  patterns:
    - src/assets/**
    - assets/**
    - public/**
```

### 后端项目

```yaml
controllers:
  patterns:
    - src/controllers/**
    - src/**/*.controller.ts  # NestJS
    - controllers/**
  indicators:
    - 包含路由处理逻辑

services:
  patterns:
    - src/services/**
    - src/**/*.service.ts  # NestJS
    - services/**
  indicators:
    - 业务逻辑层

models:
  patterns:
    - src/models/**
    - src/entities/**  # TypeORM
    - models/**
  indicators:
    - 数据模型定义

routes:
  patterns:
    - src/routes/**
    - src/router/**
    - routes/**
  indicators:
    - 路由定义

middlewares:
  patterns:
    - src/middlewares/**
    - src/middleware/**
    - middlewares/**
  indicators:
    - 中间件定义
```

### 通用结构

```yaml
utils:
  patterns:
    - src/utils/**
    - src/lib/**
    - utils/**
    - lib/**

types:
  patterns:
    - src/types/**
    - src/@types/**
    - types/**

constants:
  patterns:
    - src/constants/**
    - src/config/**
    - constants/**

tests:
  patterns:
    - src/**/*.test.ts
    - src/**/*.spec.ts
    - tests/**
    - __tests__/**
```

## Monorepo 识别

```yaml
检测条件：
  - 存在 pnpm-workspace.yaml
  - 或 package.json 有 workspaces
  - 或存在 lerna.json
  - 或存在 nx.json

Monorepo 结构：
  packages:
    - name: string      # 包名
      path: string      # 包路径
      type: string      # app | lib | shared
      dependencies: [string]
```

## 扫描流程

```
1. 确定项目类型
   ├─ 检查 package.json
   └─ 检测框架

2. 扫描目录结构
   ├─ 递归遍历目录
   ├─ 应用 exclude patterns
   └─ 记录文件和目录

3. 识别模块
   ├─ 匹配目录模式
   ├─ 检查指示器
   └─ 提取模块信息

4. 分析入口文件
   ├─ 查找 index.ts/js
   └─ 提取导出内容

5. 统计信息
   ├─ 按扩展名统计
   └─ 识别大型模块
```

## 使用示例

### 示例 1：Vue 3 前端项目

```yaml
input:
  project_path: "./demos/coding-gui"

output:
  success: true
  data:
    project_type: "frontend"

    modules:
      - name: "components"
        path: "src/components"
        type: "component"
        file_count: 7
      - name: "views"
        path: "src/views"
        type: "view"
        file_count: 3
      - name: "stores"
        path: "src/stores"
        type: "store"
        file_count: 1
      - name: "router"
        path: "src/router"
        type: "router"
        file_count: 1

    frontend:
      components:
        path: "src/components"
        count: 7
        items:
          - { name: "ArtifactPreview", path: "src/components/ArtifactPreview.vue" }
          - { name: "LeftPanel", path: "src/components/LeftPanel.vue" }
          - { name: "PhaseNav", path: "src/components/PhaseNav.vue" }
      views:
        path: "src/views"
        count: 3
        items:
          - { name: "WorkspaceView", path: "src/views/WorkspaceView.vue" }
          - { name: "ProjectsView", path: "src/views/ProjectsView.vue" }
          - { name: "SettingsView", path: "src/views/SettingsView.vue" }
      stores:
        path: "src/stores"
        count: 1
        items:
          - { name: "project", path: "src/stores/project.ts" }

    common:
      types:
        path: "src/types"
        count: 1
      assets:
        path: "src/assets"
        count: 1

    stats:
      total_files: 15
      total_directories: 8
      by_extension:
        - { ext: ".vue", count: 10 }
        - { ext: ".ts", count: 4 }
        - { ext: ".css", count: 1 }
```

### 示例 2：NestJS 后端项目

```yaml
input:
  project_path: "./backend"

output:
  success: true
  data:
    project_type: "backend"

    modules:
      - name: "users"
        path: "src/users"
        type: "nestjs-module"
        file_count: 5
      - name: "posts"
        path: "src/posts"
        type: "nestjs-module"
        file_count: 5

    backend:
      controllers:
        path: "src/**/*.controller.ts"
        count: 4
        items:
          - { name: "UsersController", path: "src/users/users.controller.ts" }
          - { name: "PostsController", path: "src/posts/posts.controller.ts" }
      services:
        path: "src/**/*.service.ts"
        count: 4
        items:
          - { name: "UsersService", path: "src/users/users.service.ts" }
          - { name: "PostsService", path: "src/posts/posts.service.ts" }
      models:
        path: "prisma/schema.prisma"
        count: 1

    stats:
      total_files: 25
      total_directories: 10
      by_extension:
        - { ext: ".ts", count: 22 }
        - { ext: ".prisma", count: 1 }
```

## 错误处理

```yaml
# 目录不存在
output:
  success: false
  error: "Directory not found: {project_path}"

# 空项目
output:
  success: true
  data:
    project_type: "unknown"
    modules: []
  warning: "No source files found"
```

## 关联 Skills

- `tech_stack_detector` - 检测项目类型
- `api_scanner` - 深入扫描 routes/controllers
- `schema_scanner` - 深入扫描 models/entities
