# 现有项目整合指南

> 版本：v1.0
> 最后更新：2026-01-03

---

## 为什么需要这个？

当你有一个**已经存在的项目**，想要用 AI 协作框架来管理时，会遇到一个问题：

> AI 不知道这个项目「已经做了什么」，每次都要重新解释背景

这套工具解决的核心问题是：

> **让 AI 知道「我们在什么地基上工作」**

---

## 核心概念

### 1. 单一信息来源（SSoT）

SSoT = Single Source of Truth

**目标**：把散落在各处的信息，整理成 AI 能理解的标准格式

| 散落的信息 | 整理后 |
|-----------|--------|
| 数据库里有哪些表？ | → `03_DATA_MODEL.md` |
| 后端有哪些 API？ | → `20_API_SPEC.md` |
| 前端有哪些页面？ | → `21_UI_FLOW_SPEC.md` |
| 项目用了什么技术栈？ | → `10_CONTEXT.md` |

### 2. 对历史功能的态度

**核心原则**：

```
能用就用 → 不改动正常运行的功能
能改就改 → 有机会时渐进式规范化
新的按新规范 → 新功能严格走 Phase 1-7
```

**不会强迫你**：
- ❌ 补齐所有历史文档
- ❌ 重构所有旧代码
- ❌ 为旧功能写测试

**但会帮你**：
- ✅ 登记项目基本信息
- ✅ 自动识别技术栈和模块
- ✅ 逆向生成 API/Schema 文档（可选）

### 3. 整合级别（Level 0-3）

不同项目需要不同程度的整合，用级别来区分：

```
Level 0: 最小登记 ──→ 只是让 AI 知道「有这个项目」
Level 1: AI 可协作 ──→ AI 可以帮你维护和开发
Level 2: 深度协作 ──→ AI 完全理解项目结构
Level 3: 完全规范 ──→ 和新项目一样的完整文档
```

---

## 整合级别详解

### Level 0：最小登记

**适用场景**：
- 老项目，只是偶尔改一下
- 不打算大改，只需要纳入管理
- 试水阶段，先登记再说

**产出物**：
```
docs/{project}/
└── 10_CONTEXT.md    # 极简版，只有基本信息
```

**10_CONTEXT.md 内容示例**：
```markdown
# my-legacy-app - 项目上下文

> 状态：Legacy
> 整合级别：Level 0

## 项目概述

**名称**：my-legacy-app
**路径**：/path/to/project
**技术栈**：Express + JavaScript
**状态**：[legacy] 已存在项目

## 简要描述

一个遗留的后台管理系统，用于...

---
_整合时间：2026-01-03_
```

**耗时**：5-10 分钟

---

### Level 1：AI 可协作（推荐）

**适用场景**：
- 需要 AI 帮忙维护的项目
- 要在旧项目上开发新功能
- 团队日常使用的项目

**产出物**：
```
docs/{project}/
├── 10_CONTEXT.md              # 包含技术栈和模块划分
├── 90_PROGRESS_LOG.yaml       # 进度日志
├── PHASE_GATE.yaml            # Gate 规则
├── PHASE_GATE_STATUS.yaml     # Gate 状态（Phase 1 追溯通过）
└── _foundation/
    └── 05_TECH_DECISIONS.md   # 技术栈详情 [逆向]
```

**与 Level 0 的区别**：
| 项目 | Level 0 | Level 1 |
|------|---------|---------|
| 模块划分 | ❌ | ✅ 自动识别 |
| 技术栈详情 | 简单列举 | 完整版本信息 |
| 进度追踪 | ❌ | ✅ 可用 /check-progress |
| Phase Gate | ❌ | ✅ Phase 1 已追溯通过 |
| 新功能开发 | 手动创建 | ✅ 可用 /new-feature |

**耗时**：30 分钟 - 1 小时

---

### Level 2：深度协作

**适用场景**：
- 核心业务项目
- 需要持续开发的项目
- 团队多人协作的项目

**产出物**：
```
docs/{project}/
├── 10_CONTEXT.md
├── 20_API_SPEC.md             # API 文档 [逆向]
├── 90_PROGRESS_LOG.yaml
├── PHASE_GATE.yaml
├── PHASE_GATE_STATUS.yaml
└── _foundation/
    ├── 03_DATA_MODEL.md       # 数据模型 [逆向]
    └── 05_TECH_DECISIONS.md
```

**与 Level 1 的区别**：
| 项目 | Level 1 | Level 2 |
|------|---------|---------|
| API 文档 | ❌ | ✅ 自动逆向生成 |
| 数据模型 | ❌ | ✅ 自动逆向生成 |
| AI 理解深度 | 知道结构 | 理解业务逻辑 |

**耗时**：1-3 天（需人工验证逆向结果）

---

### Level 3：完全规范

**适用场景**：
- 最核心的项目
- 需要完整文档的项目
- 准备重构或重写的项目

**产出物**：
```
docs/{project}/
├── 10_CONTEXT.md
├── 20_API_SPEC.md             # [已验证]
├── 21_UI_FLOW_SPEC.md         # [已验证]
├── 90_PROGRESS_LOG.yaml
├── PHASE_GATE.yaml
├── PHASE_GATE_STATUS.yaml
└── _foundation/
    ├── 01_USER_JOURNEY.md     # 用户旅程
    ├── 02_ARCHITECTURE.md     # 架构文档
    ├── 03_DATA_MODEL.md       # [已验证]
    ├── 04_ROADMAP.md          # 路线图
    └── 05_TECH_DECISIONS.md   # [已验证]
```

**与 Level 2 的区别**：
- 所有 `[逆向]` 标记改为 `[已验证]`
- 补充完整的 Foundation 文档
- 和新项目享有同等待遇

**耗时**：按需（可能需要几周）

---

## 如何选择级别？

```
┌─────────────────────────────────────────────────────────┐
│                   你的项目是什么情况？                    │
└─────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
      很少改动         日常维护        核心项目
      偶尔看看         需要AI帮忙      持续开发
           │               │               │
           ▼               ▼               ▼
       Level 0         Level 1         Level 2+
       最小登记        AI可协作        深度协作
```

**快速判断**：

| 问题 | 是 | 否 |
|------|----|----|
| 这个项目还在活跃开发吗？ | Level 1+ | Level 0 |
| 需要 AI 帮写代码吗？ | Level 1+ | Level 0 |
| 有后端 API 需要维护吗？ | Level 2 | Level 1 |
| 有数据库需要改动吗？ | Level 2 | Level 1 |
| 是公司最核心的项目吗？ | Level 3 | Level 1-2 |

---

## 命令使用指南

### 第一步：扫描项目

```bash
/scan-project ./path/to/project
```

**这个命令会**：
1. 检测技术栈（Vue/React/Express/NestJS...）
2. 识别模块结构
3. 评估文档完整度
4. 推荐整合级别

**输出示例**：
```
📊 项目扫描报告：my-project

技术栈：Vue 3 + TypeScript + Vite
模块数：5
文档完整度：10%
推荐整合级别：Level 1

下一步：
/integrate-project ./my-project --level=1
```

---

### 第二步：执行整合

```bash
# Level 0 整合
/integrate-project ./path/to/project --level=0

# Level 1 整合（推荐）
/integrate-project ./path/to/project --level=1

# Level 2 整合
/integrate-project ./path/to/project --level=2
```

**可选参数**：
| 参数 | 说明 | 示例 |
|------|------|------|
| `--level=N` | 整合级别 0-3 | `--level=1` |
| `--name=NAME` | 指定功能名称 | `--name=legacy-admin` |
| `--manual` | 手动模式，只生成骨架 | `--manual` |

**输出示例**：
```
✅ 项目整合完成！

项目：my-project
级别：Level 1

📁 生成的文件：
docs/my-project/
├── 10_CONTEXT.md              ✅
├── 90_PROGRESS_LOG.yaml       ✅
├── PHASE_GATE.yaml            ✅
├── PHASE_GATE_STATUS.yaml     ✅ (Phase 1 追溯通过)
└── _foundation/
    └── 05_TECH_DECISIONS.md   ✅ [逆向]

📝 下一步：
• 开发新功能：/new-feature my-project/new-xxx
• 补充文档：编辑 10_CONTEXT.md
```

---

### 第三步（可选）：逆向生成文档

如果选择 Level 2，还需要执行：

```bash
# 逆向生成 API 文档
/reverse-api ./path/to/project

# 逆向生成数据模型文档
/reverse-schema ./path/to/project
```

**支持的技术栈**：

| 命令 | 语言 | 说明 |
|------|------|------|
| `/reverse-api` | 任意（Python, JS/TS, Go, Java...） | 从路由定义生成 API 文档 |
| `/reverse-schema` | 任意（SQLAlchemy, Prisma, TypeORM...） | 从 ORM 定义生成数据模型 |

> 💡 采用契约式设计，Claude 自动识别框架语法，无需预定义规则

**输出带有置信度标记**：
```markdown
### GET /api/users

获取用户列表

**请求参数**：
| 参数 | 类型 | 说明 |
|------|------|------|
| page | number | 页码 [推断] |

_置信度：0.8（有 TypeScript 类型定义）_
```

---

### 第四步（可选）：检查一致性

```bash
/sync-docs docs/my-project
```

**这个命令会**：
- 对比文档和代码的差异
- 发现新增/删除/修改的 API
- 发现数据模型变更
- 生成同步报告

**输出示例**：
```
📊 文档同步检查报告

📈 总体状态：⚠️ 有差异

| 类型 | 文档项 | 代码项 | 匹配 | 差异 |
|------|--------|--------|------|------|
| API 端点 | 15 | 18 | 12 | 6 |

🆕 新增端点（代码有，文档没有）：
• POST /api/users/batch
• DELETE /api/users/:id

📝 建议：
1. 更新 20_API_SPEC.md
2. 或执行 /reverse-api --fix
```

---

## 整合后的工作流

### 场景 1：在旧项目上开发新功能

```bash
# 1. 确保项目已整合（Level 1+）
/check-progress my-project

# 2. 创建新功能
/new-feature my-project/user-export

# 3. 按 Phase 1-7 正常开发
# ... 正常的开发流程 ...
```

### 场景 2：维护旧功能

```bash
# 不需要补文档，直接修改代码
# 如果有时间，可以渐进式补充

# 可选：把修改记录到进度日志
# 编辑 90_PROGRESS_LOG.yaml
```

### 场景 3：文档同步

```bash
# 定期检查文档与代码的一致性
/sync-docs docs/my-project

# 有差异时更新
/sync-docs docs/my-project --fix
```

---

## 标记系统

整合产生的文档会有特殊标记，帮助区分内容来源：

| 标记 | 含义 | 示例 |
|------|------|------|
| `[legacy]` | 历史功能，已存在 | `## 用户管理 [legacy]` |
| `[逆向]` | 从代码自动生成 | `### GET /api/users [逆向]` |
| `[推断]` | AI 根据代码推断 | `page: number [推断]` |
| `[补充]` | 人工后续补充 | `说明：... [补充]` |
| `[已验证]` | 人工确认正确 | `### 数据模型 [已验证]` |

**验证流程**：
```
[逆向] → 人工检查 → [已验证]
[推断] → 人工确认 → [已验证] 或 修正
```

---

## 追溯标记（Retroactive）

对于已存在的项目，Phase 1（Kickoff）会自动标记为「追溯通过」：

```yaml
# PHASE_GATE_STATUS.yaml
phase_1_kickoff:
  gate_state: passed
  gate_state_meta:
    retroactive: true
    retroactive_at: "2026-01-03T10:00:00"
    retroactive_reason: "现有项目整合，Phase 1 视为已完成"
```

**这意味着**：
- ✅ 不需要补 Phase 1 的文档
- ✅ 可以直接在项目上开发新功能
- ✅ 新功能从 Phase 1 开始正常走流程

---

## FAQ

### Q: 我的项目结构不标准，能整合吗？

可以。使用 `--manual` 模式：
```bash
/integrate-project ./my-project --level=0 --manual
```
然后手动编辑生成的 `10_CONTEXT.md`。

### Q: 逆向生成的文档不准确怎么办？

这是正常的。逆向生成的内容都有 `[逆向]` 或 `[推断]` 标记，需要人工验证后改为 `[已验证]`。

### Q: Level 2 太麻烦，但我需要 API 文档怎么办？

可以：
1. 先执行 Level 1 整合
2. 之后单独执行 `/reverse-api`
3. 只验证你需要的部分

### Q: 整合后可以升级级别吗？

可以。级别只是初始整合的深度，之后可以随时：
- 补充更多文档
- 执行逆向命令
- 手动添加 Foundation 文档

### Q: 旧项目的测试怎么办？

不强制。原则是「能用就用」：
- 有测试：继续用
- 没测试：不强制补
- 新功能：建议写测试

---

## 命令速查表

| 命令 | 用途 | 常用参数 |
|------|------|----------|
| `/scan-project` | 扫描项目 | `./path` |
| `/integrate-project` | 执行整合 | `--level=N`, `--name=NAME` |
| `/reverse-api` | 逆向 API 文档 | `--format=openapi` |
| `/reverse-schema` | 逆向数据模型 | `--orm=prisma` |
| `/sync-docs` | 检查一致性 | `--fix`, `--strict` |

---

## 相关文档

- [AI 工作流总纲](../04_ai_workflow/README.md)
- [Phase Gate 机制](../07_phase_gate/README.md)
- [文档模板](../03_templates/)

---

_Generated by Claude Code | 2026-01-03_
