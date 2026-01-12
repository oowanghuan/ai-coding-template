# system_scaffolder - 生成目录结构

## 能力描述

根据 `01_PROJECT_PROFILE.yaml` 中的配置，自动生成项目的目录结构和基础文件。这是 Phase 0 Foundation 阶段的核心工具。

## 输入

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| profile_path | string | 否 | PROJECT_PROFILE 路径，默认 `docs/_system/01_PROJECT_PROFILE.yaml` |
| target_dir | string | 否 | 目标目录，默认项目根目录 |
| dry_run | boolean | 否 | 预览模式，不实际创建文件 |

## 输出

- 创建的目录和文件列表
- 跳过的已存在文件列表
- 配置摘要

## 执行步骤

### 1. 读取 PROJECT_PROFILE

```yaml
# docs/_system/01_PROJECT_PROFILE.yaml
project:
  name: "my-app"
  type: "fullstack"  # frontend/backend/fullstack

tech_stack:
  frontend:
    framework: "vue3"
    ui_library: "element-plus"
    state_management: "pinia"
  backend:
    framework: "express"
    database: "postgresql"
    orm: "prisma"

workflow:
  phases:
    demo_required: true
    test_required: true

directories:
  docs: "docs"
  src: "src"
  tests: "tests"
```

### 2. 生成目录结构

根据配置生成对应的目录：

#### 前端项目 (frontend)

```
{project}/
├── src/
│   ├── components/
│   │   ├── common/
│   │   └── layout/
│   ├── views/
│   ├── stores/
│   ├── api/
│   ├── utils/
│   ├── styles/
│   └── router/
├── public/
├── tests/
│   ├── unit/
│   └── e2e/
└── docs/
    └── _system/
```

#### 后端项目 (backend)

```
{project}/
├── src/
│   ├── controllers/
│   ├── services/
│   ├── models/
│   ├── middlewares/
│   ├── routes/
│   └── utils/
├── prisma/
│   └── schema.prisma
├── tests/
│   ├── unit/
│   └── integration/
└── docs/
    └── _system/
```

#### 全栈项目 (fullstack)

```
{project}/
├── frontend/
│   └── (frontend structure)
├── backend/
│   └── (backend structure)
├── shared/
│   └── types/
└── docs/
    └── _system/
```

### 3. 生成基础文件

根据技术栈生成配置文件：

```yaml
files_to_generate:
  # 通用
  - path: ".gitignore"
    template: "gitignore/{project_type}"

  - path: "README.md"
    template: "readme/basic"

  # Vue 3 项目
  - path: "vite.config.ts"
    template: "vite/vue3"

  - path: "tsconfig.json"
    template: "tsconfig/vue3"

  # Express 项目
  - path: "package.json"
    template: "package/express"
```

### 4. 创建 _foundation 目录

```
docs/_foundation/
├── _planning/                   # 规划文档
│   ├── 01_USER_JOURNEY.md       # 用户旅程
│   ├── 02_ARCHITECTURE.md       # 系统架构
│   ├── 03_MODULE_DECOMPOSITION.md # 模块分解
│   ├── 04_ROADMAP.md            # 路线图
│   └── 05_TECH_DECISIONS.md     # 技术决策
├── _api_system/                 # API 规范
│   └── 00_REST_CONVENTIONS.md
├── _db_system/                  # DB 规范
│   └── 00_DB_CONVENTIONS.md
├── _ui_system/                  # UI 规范
│   ├── 01_COMPONENT_LIBRARY.md
│   ├── 02_LAYOUT_RULES.md
│   └── ...
└── FOUNDATION_GATE_STATUS.yaml  # Foundation Gate 状态
```

### 5. 输出结果

```
✅ 目录结构生成成功

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 配置摘要
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
项目名称：my-app
项目类型：fullstack
前端框架：Vue 3 + Element Plus
后端框架：Express + Prisma

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 创建的目录 (15)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ src/components/common/
✓ src/components/layout/
✓ src/views/
✓ src/stores/
✓ src/api/
✓ src/utils/
✓ src/styles/
✓ src/router/
✓ tests/unit/
✓ tests/e2e/
✓ docs/_foundation/
✓ docs/_foundation/_planning/
✓ docs/_foundation/_api_system/
✓ docs/_foundation/_db_system/
✓ docs/_foundation/_ui_system/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 创建的文件 (8)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ .gitignore
✓ README.md
✓ vite.config.ts
✓ tsconfig.json
✓ docs/_foundation/_planning/01_USER_JOURNEY.md
✓ docs/_foundation/_planning/02_ARCHITECTURE.md
✓ docs/_foundation/_api_system/00_REST_CONVENTIONS.md
✓ docs/_foundation/FOUNDATION_GATE_STATUS.yaml

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏭️ 跳过的文件 (已存在)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• package.json

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 下一步：
1. 填写 docs/_foundation/_planning/ 规划文档
2. 完善 docs/_foundation/_api_system/ API 规范
3. 执行 /check-gate --phase=0 检查 Foundation Gate
4. 使用 /new-feature <name> 创建第一个功能模块
```

## 示例

### 示例 1：预览模式

```
请使用 system_scaffolder skill：
- dry_run: true
```

**输出**：
显示将要创建的目录和文件，但不实际创建。

### 示例 2：指定配置文件

```
请使用 system_scaffolder skill：
- profile_path: ./custom-profile.yaml
- target_dir: ./new-project
```

## 注意事项

1. **不覆盖**：默认不覆盖已存在的文件
2. **配置优先**：以 PROJECT_PROFILE 为准，自定义目录结构
3. **模板化**：基础文件从模板生成，可自定义模板
4. **Git 友好**：自动生成适合的 .gitignore

## 关联工具

- `/init-project` - Slash Command 封装
- `doc_generator` - 生成 _system 目录下的文档
- `context_writer` - 填充 PROJECT_CONTEXT 内容
