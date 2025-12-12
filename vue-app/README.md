# AI 时代团队转型蓝图 - 项目看板

Vue 3 + Element Plus 构建的项目管理看板应用，配合 AI 协作开发框架使用。

## 快速开始

```bash
# 1. 安装依赖
npm install

# 2. 启动开发服务器
npm run dev

# 3. 访问
open http://localhost:5173
```

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 下一代前端构建工具
- **Element Plus** - 基于 Vue 3 的组件库
- **Vue Router** - Vue.js 官方路由管理器
- **TypeScript** - 类型安全的 JavaScript

## 项目结构

```
vue-app/
├── src/
│   ├── components/         # 公共组件
│   │   └── MainLayout.vue  # 主布局组件
│   ├── config/
│   │   └── github.ts       # GitHub 配置
│   ├── data/
│   │   └── roles.js        # 角色数据配置
│   ├── services/
│   │   └── githubProxyClient.ts  # GitHub API 客户端
│   ├── views/
│   │   ├── PanoramaGuide.vue     # 首页/全景指南
│   │   ├── WorkflowGuide.vue     # 工作流指南
│   │   ├── Resources.vue         # 资源与工具
│   │   └── dashboard/            # 项目看板相关
│   ├── router/
│   │   └── index.js        # 路由配置
│   ├── App.vue             # 根组件
│   └── main.js             # 应用入口
├── .env                    # 环境变量配置
├── package.json
└── vite.config.js
```

## 核心功能

### 首页 (PanoramaGuide.vue)
- 8 阶段工作流全景展示
- 项目搭建指引（3 步快速开始）
- 角色入口选择

### 项目看板 (ProjectDashboard.vue)
- 功能列表与进度跟踪
- GitHub Issue/PR 实时同步
- 文档查看器（Context、Spec、Design 等）
- 每日进度摘要

### 实践指南
- 工作流指南（Tab 切换）
- 资源与工具集合

## 环境变量配置

看板从 GitHub 实时读取仓库文档，需要配置 Supabase Edge Function 作为代理。

```bash
# 1. 复制环境变量模板
cp .env.example .env

# 2. 编辑 .env，填写你的 Supabase 配置
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

> **注意**: `.env` 文件不会被提交到 git，需要自行创建。

## GitHub 仓库配置

修改 `src/config/github.ts` 指向你的 GitHub 仓库：

```typescript
export const GITHUB_DOC_CONFIG = {
  owner: 'your-username',      // GitHub 用户名/组织名
  repo: 'your-repo',           // 仓库名
  branch: 'main',              // 分支名
  docsBasePath: 'docs',        // 文档目录路径
}
```

## Supabase Edge Function 部署

看板通过 Supabase Edge Function 代理 GitHub API 请求，避免 CORS 问题和 API 限流。

详细部署步骤参见项目看板页面的配置指引。

## 开发命令

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 类型检查
npx vue-tsc --noEmit

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

## 路由配置

| 路径 | 页面 |
|------|------|
| `/` | 首页/全景指南 |
| `/workflow-guide` | 工作流指南 |
| `/resources` | 资源与工具 |
| `/project-dashboard` | 项目看板 |
| `/role/:id` | 角色详情页 |
| `/github/*` | GitHub 专区 |

## 部署

### Vercel 部署

```bash
# 安装 Vercel CLI
npm i -g vercel

# 部署
vercel
```

### 手动部署

```bash
# 构建
npm run build

# 产物在 dist/ 目录，可部署到任何静态托管服务
```

## 与 AI 协作框架配合使用

本看板与 `_templates/` 中的 AI 协作框架配合使用：

1. 在 Claude Code 中执行 `/new-feature my-feature` 创建功能
2. 功能文档自动生成在 `docs/my-feature/` 目录
3. 执行 `/start-day` 和 `/end-day` 更新进度
4. 看板自动读取并展示功能进度

---

_由 Claude Code 生成_
