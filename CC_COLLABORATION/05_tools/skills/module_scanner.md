# module_scanner

模块结构扫描 Skill - 分析项目的目录结构和模块划分

## 用途

扫描项目目录结构，识别模块划分和代码组织方式，返回结构化数据。

## 输入契约

```yaml
input:
  project_path: string        # 项目根目录路径
  max_depth: number           # 最大扫描深度（默认 4）
  exclude_patterns: [string]  # 排除的目录（默认 node_modules, dist, .git, __pycache__, .venv）
```

## 输出契约

```yaml
output:
  success: boolean
  data:
    # 项目类型
    project_type: string      # frontend | backend | fullstack | library | cli | monorepo

    # 目录结构树
    tree:
      - path: string
        type: string          # directory | file
        name: string
        children: [tree_node] # 子节点
        file_count: number    # 目录下文件数
        has_index: boolean    # 是否有入口文件

    # 识别的模块
    modules:
      - name: string          # 模块名称
        path: string          # 模块路径
        type: string          # 模块类型（见下方）
        entry_file: string | null  # 入口文件
        file_count: number    # 文件数量
        exports: [string] | null   # 导出内容（如果能识别）
        description: string | null # 模块描述

    # 按类型分组的模块
    categorized:
      # 通用模块类型
      components: [module_ref]    # UI 组件
      views: [module_ref]         # 页面/视图
      services: [module_ref]      # 服务层
      controllers: [module_ref]   # 控制器
      models: [module_ref]        # 数据模型
      routes: [module_ref]        # 路由定义
      middleware: [module_ref]    # 中间件
      utils: [module_ref]         # 工具函数
      hooks: [module_ref]         # Hooks (React/Vue)
      stores: [module_ref]        # 状态管理
      types: [module_ref]         # 类型定义
      tests: [module_ref]         # 测试文件
      config: [module_ref]        # 配置文件
      assets: [module_ref]        # 静态资源

    # Monorepo 结构（如果是 monorepo）
    packages:
      - name: string
        path: string
        type: string          # app | lib | shared | config
        dependencies: [string]

    # 统计信息
    stats:
      total_files: number
      total_directories: number
      by_extension:
        - ext: string
          count: number
      largest_modules:
        - name: string
          file_count: number
      source_lines: number | null  # 代码行数（如果计算）

    # 置信度
    confidence: number
    confidence_reason: string

  error: string | null
```

## 模块类型定义

```yaml
module_ref:
  name: string
  path: string
  count: number
```

## 能力边界

### 能做
- 遍历目录结构
- 根据目录名和文件模式识别模块类型
- 识别入口文件（index.*, main.*, __init__.py）
- 检测 monorepo 结构
- 统计文件数量和类型

### 不能做
- 解析代码依赖关系图
- 计算循环依赖
- 分析运行时模块加载
- 读取所有文件内容

## 执行流程

```
1. 确定项目类型
   └─ 检查配置文件和目录结构

2. 扫描目录结构
   └─ 递归遍历目录
   └─ 应用 exclude patterns
   └─ 记录文件和目录

3. 识别模块
   └─ 根据目录名推断模块类型
   └─ 查找入口文件
   └─ 统计文件数量

4. 分类模块
   └─ 按类型分组

5. 检测 Monorepo
   └─ 查找 workspace 配置
   └─ 识别各个 package

6. 统计信息
   └─ 按扩展名统计
   └─ 识别大型模块
```

## 使用示例

```yaml
# Vue 3 前端项目
output:
  success: true
  data:
    project_type: "frontend"

    modules:
      - { name: "components", path: "src/components", type: "components", file_count: 12 }
      - { name: "views", path: "src/views", type: "views", file_count: 5 }
      - { name: "stores", path: "src/stores", type: "stores", file_count: 3 }
      - { name: "composables", path: "src/composables", type: "hooks", file_count: 4 }
      - { name: "router", path: "src/router", type: "routes", file_count: 1 }

    categorized:
      components:
        - { name: "components", path: "src/components", count: 12 }
      views:
        - { name: "views", path: "src/views", count: 5 }
      stores:
        - { name: "stores", path: "src/stores", count: 3 }
      hooks:
        - { name: "composables", path: "src/composables", count: 4 }

    stats:
      total_files: 35
      total_directories: 12
      by_extension:
        - { ext: ".vue", count: 17 }
        - { ext: ".ts", count: 15 }
        - { ext: ".css", count: 3 }
      largest_modules:
        - { name: "components", file_count: 12 }

    confidence: 0.90

# Python FastAPI 后端
output:
  success: true
  data:
    project_type: "backend"

    modules:
      - { name: "api", path: "app/api", type: "routes", file_count: 8 }
      - { name: "models", path: "app/models", type: "models", file_count: 6 }
      - { name: "services", path: "app/services", type: "services", file_count: 5 }
      - { name: "schemas", path: "app/schemas", type: "types", file_count: 6 }
      - { name: "core", path: "app/core", type: "config", file_count: 4 }

    categorized:
      routes:
        - { name: "api", path: "app/api", count: 8 }
      models:
        - { name: "models", path: "app/models", count: 6 }
      services:
        - { name: "services", path: "app/services", count: 5 }

    stats:
      total_files: 45
      by_extension:
        - { ext: ".py", count: 42 }
        - { ext: ".yaml", count: 3 }

# Monorepo 项目
output:
  success: true
  data:
    project_type: "monorepo"

    packages:
      - name: "web"
        path: "packages/web"
        type: "app"
        dependencies: ["@repo/ui", "@repo/utils"]
      - name: "api"
        path: "packages/api"
        type: "app"
        dependencies: ["@repo/db", "@repo/utils"]
      - name: "ui"
        path: "packages/ui"
        type: "lib"
        dependencies: []
      - name: "utils"
        path: "packages/utils"
        type: "shared"
        dependencies: []

    stats:
      total_files: 150
      by_extension:
        - { ext: ".ts", count: 80 }
        - { ext: ".tsx", count: 45 }
        - { ext: ".css", count: 25 }
```

## 置信度规则

```yaml
high (>= 0.8):
  - 标准项目结构（src/, app/, packages/）
  - 清晰的目录命名
  - 有入口文件

medium (0.5 - 0.8):
  - 非标准但可识别的结构
  - 部分目录命名模糊
  - 混合的代码组织

low (< 0.5):
  - 扁平结构无明确模块
  - 命名无规律
  - 无法推断项目类型
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
