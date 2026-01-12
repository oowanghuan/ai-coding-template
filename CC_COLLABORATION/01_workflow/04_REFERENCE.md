# AI 协作开发框架 - 完整参考手册

> 适用于：开发过程中查阅 | 阅读时间：按需

---

## 一、命令速查表

### 1.1 每日命令

| 命令 | 用途 | 参数 |
|------|------|------|
| `/start-day` | 开始一天工作 | 无 |
| `/iresume {feature}` | 恢复上下文 | feature: 功能ID |
| `/check-progress {feature}` | 查看进度 | feature: 功能ID |
| `/end-day` | 结束一天工作 | 无 |
| `/daily-summary {feature}` | 生成每日总结 | feature: 功能ID |

### 1.2 功能开发命令

| 命令 | 用途 | 参数 |
|------|------|------|
| `/new-feature {name}` | 创建新功能 | name: 功能名称 |
| `/gen-demo {feature}` | 生成 Demo | feature: 功能ID |
| `/run-tests {feature}` | 执行测试 | feature: 功能ID |
| `/release {feature} {version}` | 发布版本 | feature, version |

### 1.3 阶段控制命令

| 命令 | 用途 | 参数 |
|------|------|------|
| `/check-gate {feature}` | 检查 Gate 状态 | --phase=N |
| `/approve-gate {feature}` | 审批 Gate | --phase=N --role=XX |
| `/next-phase {feature}` | 进入下一阶段 | 无 |
| `/expert-review {feature}` | 发起专家评审 | 无 |

### 1.4 项目管理命令

| 命令 | 用途 | 参数 |
|------|------|------|
| `/init-project` | 初始化项目 | 无 |
| `/plan-features` | 生成功能清单 | 无 |
| `/scan-project` | 扫描项目结构 | 无 |
| `/sync-docs` | 同步文档 | 无 |

### 1.5 文档命令

| 命令 | 用途 | 参数 |
|------|------|------|
| `/doc-design-validation` | 验证设计文档 | 无 |
| `/reverse-api` | 逆向生成 API 文档 | 无 |
| `/reverse-schema` | 逆向生成数据模型 | 无 |

---

## 二、文件结构

### 2.1 项目级文件

```
docs/
├── _foundation/                     # 项目基础文档
│   ├── _planning/                   # 规划文档
│   │   ├── 01_USER_JOURNEY.md       # 用户旅程
│   │   ├── 02_ARCHITECTURE.md       # 系统架构
│   │   ├── 03_MODULE_DECOMPOSITION.md # 模块分解
│   │   ├── 04_ROADMAP.md            # 路线图
│   │   └── 05_TECH_DECISIONS.md     # 技术决策
│   ├── _api_system/                 # API 规范
│   ├── _db_system/                  # DB 规范
│   ├── _ui_system/                  # UI 规范
│   ├── FOUNDATION_GATE_STATUS.yaml  # Foundation Gate 状态
│   └── PROJECT_TRACKER.yaml         # 项目跟踪（可选）
│
├── FEATURE_CHECKLIST.md             # 功能开发清单
└── {feature}/                       # 功能目录
```

### 2.2 功能级文件

```
docs/{feature}/
├── 10_CONTEXT.md                   # 功能背景（Phase 1）
├── 20_API_SPEC.md                  # API 规格（Phase 2）
├── 21_UI_FLOW_SPEC.md              # UI 流程规格（Phase 2）
├── 30_DEMO_REVIEW.md               # Demo 评审（Phase 3）
├── 40_DESIGN_FINAL.md              # 最终设计（Phase 4）
├── 50_DEV_PLAN.md                  # 开发计划（Phase 5）
├── 60_TEST_PLAN.md                 # 测试计划（Phase 6）
├── 61_TEST_REPORT.md               # 测试报告（Phase 6）
├── 70_RELEASE_NOTE.md              # 发布说明（Phase 7）
├── 71_CHANGELOG.md                 # 变更日志（Phase 7）
├── 90_PROGRESS_LOG.yaml            # 进度日志
└── 91_DAILY_SUMMARY/               # 每日总结目录
```

### 2.3 CC_COLLABORATION 结构

```
CC_COLLABORATION/
├── _gui_config/                    # GUI 依赖配置
│   ├── WORKFLOW_TEMPLATE.yaml
│   ├── PHASE_GATE.yaml
│   └── README.md
│
├── _project_context/               # 项目背景与协作理念
│   ├── FRAMEWORK_PRINCIPLES.md
│   ├── COLLABORATION_GUIDE.md
│   └── ROLES_GUIDE.md
│
├── 01_workflow/                    # 工作流文档（本目录）
│   ├── README.md
│   ├── 01_QUICKSTART.md
│   ├── 02_FRAMEWORK_OVERVIEW.md
│   ├── 03_DAILY_OPERATIONS.md
│   ├── 04_REFERENCE.md
│   └── recipes/
│
├── 03_templates/                   # 文档模板
├── 05_tools/                       # 工具定义
├── 07_phase_gate/                  # Phase Gate 配置
└── 08_legacy_integration/          # 现有项目整合指南
```

---

## 三、模板清单

### 3.1 Foundation 模板

| 模板 | 用途 |
|------|------|
| `01_USER_JOURNEY_TEMPLATE.md` | 用户旅程 |
| `02_ARCHITECTURE_TEMPLATE.md` | 系统架构 |
| `03_MODULE_DECOMPOSITION_TEMPLATE.md` | 模块分解 |
| `04_ROADMAP_TEMPLATE.md` | 路线图 |
| `05_TECH_DECISIONS_TEMPLATE.md` | 技术决策 |

### 3.2 功能开发模板

| 模板 | Phase | 用途 |
|------|-------|------|
| `10_CONTEXT_TEMPLATE.md` | 1 | 功能上下文 |
| `20_API_SPEC_TEMPLATE.md` | 2 | API 规格 |
| `21_UI_FLOW_SPEC_TEMPLATE.md` | 2 | UI 流程规格 |
| `30_DEMO_REVIEW_TEMPLATE.md` | 3 | Demo 评审 |
| `40_DESIGN_TEMPLATE.md` | 4 | 详细设计 |
| `50_DEV_PLAN_TEMPLATE.md` | 5 | 开发计划 |
| `60_TEST_PLAN_TEMPLATE.md` | 6 | 测试计划 |
| `61_TEST_REPORT_TEMPLATE.md` | 6 | 测试报告 |
| `70_RELEASE_NOTE_TEMPLATE.md` | 7 | 发布说明 |
| `71_CHANGELOG_TEMPLATE.md` | 7 | 变更日志 |

---

## 四、Phase Gate 要求

### 4.1 各阶段 Exit Criteria

| Phase | 名称 | Exit Criteria |
|-------|------|--------------|
| 0 | Foundation | _foundation/ 目录完整 |
| 0.5 | User Journey | 01_USER_JOURNEY.md 通过 MVS |
| 1 | Kickoff | 10_CONTEXT.md 完整，目标≥2条 |
| 2 | Spec | 21_UI_FLOW_SPEC.md 完整 |
| 3 | Demo | Demo 可运行，评审通过 |
| 4 | Design | 40_DESIGN_FINAL.md 完整，API 契约确定 |
| 5 | Code | 50_DEV_PLAN.md 任务全完成 |
| 6 | Test | 无 P0/P1 Bug |
| 7 | Deploy | 文档更新，代码合并 |

### 4.2 审批角色

| Phase | 审批角色 |
|-------|---------|
| 0.5 | PM + Architect |
| 1 | PM |
| 2 | Architect |
| 3 | PM |
| 4 | Architect |
| 5 | Developer |
| 6 | QA |
| 7 | PM |

---

## 五、状态定义

### 5.1 任务状态

| 状态 | 说明 | 颜色 |
|------|------|------|
| `pending` | 待开始 | 灰色 |
| `wip` | 进行中 | 蓝色 |
| `done` | 已完成 | 绿色 |
| `blocked` | 阻塞 | 红色 |

### 5.2 Gate 状态

| 状态 | 说明 |
|------|------|
| `not_checked` | 未检查 |
| `checking` | 检查中 |
| `passed` | 检查通过 |
| `failed` | 检查失败 |
| `approved` | 已审批 |

### 5.3 Bug 优先级

| 优先级 | 说明 | SLA |
|--------|------|-----|
| P0 | 阻塞发布 | 立即修复 |
| P1 | 严重问题 | 当天修复 |
| P2 | 一般问题 | 3天内修复 |
| P3 | 轻微问题 | 可延后 |

---

## 附录 A：Git Commit 规范

### A.1 基本格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### A.2 Type 类型

| Type | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | feat: 添加用户登录功能 |
| `fix` | 修复 Bug | fix: 修复登录验证失败问题 |
| `docs` | 文档更新 | docs: 更新 API 文档 |
| `style` | 代码格式（不影响逻辑） | style: 格式化代码 |
| `refactor` | 重构（不添加功能或修复） | refactor: 重构用户模块 |
| `test` | 测试相关 | test: 添加登录单元测试 |
| `chore` | 构建/工具/依赖 | chore: 升级依赖版本 |
| `perf` | 性能优化 | perf: 优化列表渲染性能 |
| `build` | 构建系统 | build: 配置生产环境打包 |
| `ci` | CI 配置 | ci: 添加 GitHub Actions |
| `revert` | 回滚 | revert: 回滚 feat: 添加登录 |

### A.3 Scope 范围

```bash
# 功能模块
auth          # 认证相关
user          # 用户模块
project       # 项目模块
dashboard     # 看板模块

# 技术层面
api           # API 相关
ui            # UI 相关
db            # 数据库相关
config        # 配置相关
```

### A.4 Subject 规则

1. **使用祈使句**：描述做了什么，不是描述状态
2. **首字母不大写**（英文时）
3. **不使用句号结尾**
4. **控制在 50 字符以内**

```bash
# 正确
feat: 添加用户登录功能
fix: 修复密码验证逻辑

# 错误
feat: 添加了用户登录功能。   # 不用"了"，不用句号
fix: Fixed password bug.      # 首字母不大写，不用过去式
```

### A.5 完整示例

```bash
# 简单提交
feat: 添加登录页面
fix: 修复表单验证错误
docs: 更新 README

# 带 Scope 的提交
feat(auth): 添加 JWT 认证中间件
fix(user): 修复用户头像上传失败
docs(api): 完善用户接口文档

# 完整格式提交（使用 HEREDOC）
git commit -m "$(cat <<'EOF'
feat(dashboard): 添加项目进度追踪功能

实现项目进度的可视化追踪，包括：
- 按阶段显示进度条
- 任务完成率统计
- 阻塞项高亮显示

Closes #45
Refs #32

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

### A.6 Breaking Change

```bash
feat(api)!: 重构用户 API 响应格式

BREAKING CHANGE: 用户 API 响应格式变更

Before:
{
  "user": { "id": 1, "name": "张三" }
}

After:
{
  "data": { "id": 1, "name": "张三" }
}

迁移指南：
1. 更新所有调用 /api/users 的代码
2. 将 response.user 改为 response.data
```

### A.7 Claude Code 提交

```bash
feat(user): 添加用户列表分页功能

实现用户列表的服务端分页，支持：
- 每页 10/20/50 条记录
- 页码跳转
- 总数显示

Co-Authored-By: Claude <noreply@anthropic.com>
```

### A.8 Type 速查表

| Type | 含义 | 会出现在 CHANGELOG |
|------|------|-------------------|
| feat | 新功能 | ✓ Features |
| fix | 修复 | ✓ Bug Fixes |
| docs | 文档 | ✗ |
| style | 格式 | ✗ |
| refactor | 重构 | ✗ |
| perf | 性能 | ✓ Performance |
| test | 测试 | ✗ |
| build | 构建 | ✗ |
| ci | CI | ✗ |
| chore | 杂项 | ✗ |
| revert | 回滚 | ✓ Reverts |

---

## 附录 B：常用动词

| 中文 | 英文 | 使用场景 |
|------|------|----------|
| 添加 | add | 新增功能/文件 |
| 修复 | fix | 修复问题 |
| 更新 | update | 更新已有内容 |
| 删除 | remove | 删除功能/文件 |
| 重构 | refactor | 重构代码 |
| 优化 | optimize | 优化性能 |
| 移动 | move | 移动文件 |
| 重命名 | rename | 重命名 |

---

_文档版本：v2.0 | 最后更新：2026-01-09_
