# DAILY_WORKFLOW_GUIDE.md
# AI 协作开发日常工作流指南

> 版本：v1.3
> 最后更新：2026-01-02
> 适用于：Claude Code + AI 协作开发框架

---

## 目录

1. [概述](#1-概述)
2. [每日工作流程](#2-每日工作流程)
3. [功能开发完整流程](#3-功能开发完整流程)
   - 3.1-3.7 各阶段流程
   - **3.8 Phase 5 实战：人机协作详解** ⭐
   - **3.9 Phase 6 实战：测试工具详解** ⭐
4. [命令速查表](#4-命令速查表)
5. [Skills 和 Subagents](#5-skills-和-subagents)
6. [常见场景处理](#6-常见场景处理)
7. [最佳实践](#7-最佳实践)

---

## 1. 概述

本文档描述如何使用 AI 协作开发框架进行功能开发。框架采用 **Phase Gate** 机制，将开发过程分为多个阶段，每个阶段都有明确的交付物和质量门禁。

### 1.1 开发阶段概览

```
Phase 0: Foundation（项目基础）
    ↓
Phase 0.5: Foundation Gate（需求验证）← v1.3 新增
    ↓ Gate: PM + Architect 审批
Phase 1: Kickoff（功能启动）
    ↓ Gate: PM 审批
Phase 2: Spec（需求规格）
    ↓ Gate: Architect + PM 审批
Phase 3: Demo（原型验证）← 可跳过（无 UI 时）
    ↓ Gate: PM 审批
Phase 4: Design（详细设计）
    ↓ Gate: Architect 审批
Phase 5: Code（开发实现）
    ↓ Gate: Developer + Architect 审批
Phase 6: Test（测试验证）
    ↓ Gate: QA 审批
Phase 7: Deploy（发布上线）
    ↓ Gate: PM 审批
```

> **v1.3 新增**：Phase 0.5 Foundation Gate 确保需求起源层完整，所有 P0 模块都可追溯到用户步骤。

### 1.2 核心工具分类

| 类别 | 工具 | 说明 |
|------|------|------|
| **日常流程** | `/start-day`, `/end-day` | 每日开始和结束 |
| **功能管理** | `/new-feature`, `/check-progress`, `/iresume` | 创建和跟踪功能 |
| **Foundation Gate** | `/doc-design-validation`, `/check-foundation-gate`, `/plan-features` | Phase 0.5 需求验证（v1.3 新增） |
| **阶段控制** | `/next-phase`, `/check-gate`, `/approve-gate` | Phase Gate 机制 |
| **质量保障** | `/expert-review`, `/run-tests` | 专家评审和测试 |
| **辅助工具** | `/gen-demo`, `/daily-summary`, `/release` | 生成 Demo、总结、发布 |

---

## 2. 每日工作流程

### 2.1 开始工作

```bash
# 每日开始，同步代码并恢复上下文
/start-day
```

**执行内容**：
1. 执行 `git pull` 同步远程代码
2. 扫描活跃的功能模块
3. 显示当前进度和待办任务
4. 恢复工作上下文

**输出示例**：
```
🌅 每日开始 - user-auth

📥 Git 同步: ✅ 已同步最新代码
📍 上下文恢复:
  • 功能模块: user-auth
  • 当前阶段: Phase 5 - Code
  • 整体进度: 45%
  • 上次操作: 完成登录表单 UI

📋 今日待办:
  ⏭️ 下一步: 实现登录 API 调用
  🔄 进行中: [CODE-004] 实现登录 API 调用
```

### 2.2 恢复指定功能上下文

```bash
# 恢复特定功能的上下文
/iresume user-auth
```

**用途**：
- 切换到不同的功能模块
- 对话中断后恢复上下文
- 查看功能的详细状态

### 2.3 查看进度

```bash
# 查看当前功能的详细进度
/check-progress user-auth

# 查看所有功能的概览
/check-progress
```

### 2.4 结束工作

```bash
# 每日结束，更新进度并提交代码
/end-day
```

**执行内容**：
1. 询问今日完成的任务
2. 更新 `90_PROGRESS_LOG.yaml`
3. 更新 `cc_checkpoint` 断点信息
4. 生成每日总结
5. 执行 `git add` + `git commit`
6. 确认后执行 `git push`

---

## 3. 功能开发完整流程

### 3.0 Phase 0.5: Foundation Gate（需求验证）- v1.3 新增

> **重要**：在开始任何功能开发之前，必须先通过 Foundation Gate。

#### 核心理念

```
User Journey → System Responsibility → Module Mapping → Design Validation → Foundation Gate
     ↑                                                                              │
     └────────────────────────── 可追溯 ◀───────────────────────────────────────────┘
```

#### 标准文档

| 文档 | 用途 | 模板 |
|------|------|------|
| `01_USER_JOURNEY.md` | **需求起源层** - 用户流程、系统责任、模块映射 | `01_USER_JOURNEY_TEMPLATE.md` |
| `00_FOUNDATION_GATE.md` | Gate 规则定义、MVS 标准 | `00_FOUNDATION_GATE.md` |

#### User Journey MVS（最小可通过要求）

| 必填区块 | 最小要求 |
|----------|----------|
| 用户画像 | ≥ 1 个主要用户 |
| 主成功路径 | ≥ 3 个用户步骤（U1, U2, U3...） |
| 失败路径 | ≥ 2 个失败场景（F1, F2...） |
| 系统责任声明 | 每个用户步骤都有「系统必须做」 |
| 模块映射表 | 所有 P0 模块都有对应的用户步骤 |

#### 工作流程

```bash
# 1. 编写 User Journey 文档
#    docs/_foundation/01_USER_JOURNEY.md

# 2. 执行设计验证
/doc-design-validation

# 3. 检查 Foundation Gate 状态
/check-foundation-gate

# 4. 审批（PM + Architect）
/approve-foundation --role=PM
/approve-foundation --role=Architect

# 5. 通过后，生成功能开发清单
/plan-features
```

#### 设计验证输出

**验证通过**：
```
✅ Doc Design Validation PASSED

验证时间：2026-01-02T10:00:00
验证范围：5 个用户步骤

📊 验证摘要：
  用户步骤：5 个（全部通过）
  失败路径：3 个（已覆盖）
  模块映射：4 个 P0 模块（全部映射）

✔ 设计验证通过，可以继续 Foundation Gate 检查
  执行：/check-foundation-gate
```

**验证失败**：
```
❌ Doc Design Validation FAILED

🚫 FAIL 级别问题：

1. [模块未映射] M003 dashboard
   位置：01_USER_JOURNEY.md / §5.1
   问题：P0 模块 M003 未映射到任何用户步骤
   建议：确认 M003 支持哪个用户步骤，或调整优先级

📝 下一步操作：
  1. 修复上述 FAIL 级别问题
  2. 重新执行：/doc-design-validation
```

---

### 3.1 Phase 1: Kickoff（功能启动）

#### 创建新功能

```bash
/new-feature user-auth
```

**生成文件**：
```
docs/user-auth/
├── 10_CONTEXT.md              # 功能上下文（需补充）
├── 90_PROGRESS_LOG.yaml       # 进度日志
├── PHASE_GATE.yaml            # Gate 规则配置
├── PHASE_GATE_STATUS.yaml     # Gate 运行状态
└── _demos/                    # Demo 文件目录
```

#### 编写功能上下文

编辑 `10_CONTEXT.md`，补充：
- 功能背景和目标
- 功能范围（包含和不包含）
- 用户场景
- 验收标准

#### 可选：执行专家评审

```bash
# 对 Context 文档进行独立评审
/expert-review docs/user-auth --phase=1
```

**评审结果**：
- `GO`：可以继续
- `REVISE`：建议修改（非阻断）
- `BLOCK`：必须修改（阻断 Gate）

#### 检查并通过 Gate

```bash
# 检查 Phase 1 的 Gate 状态
/check-gate user-auth --phase=1

# PM 审批
/approve-gate user-auth --phase=1 --role=PM

# 进入下一阶段
/next-phase user-auth
```

---

### 3.2 Phase 2: Spec（需求规格）

#### 编写规格文档

根据功能类型，编写不同的规格文档：

- **有 UI 的功能**：`21_UI_FLOW_SPEC.md`
- **无 UI 的功能**：`20_API_SPEC.md`

#### 可选：执行专家评审

```bash
/expert-review docs/user-auth --phase=2
```

#### 检查并通过 Gate

```bash
/check-gate user-auth --phase=2
/approve-gate user-auth --phase=2 --role=PM
/approve-gate user-auth --phase=2 --role=Architect
/next-phase user-auth
```

---

### 3.3 Phase 3: Demo（原型验证）

> **跳过条件**：如果 `feature_profile.has_ui = false`，此阶段自动跳过

#### 生成 Demo

```bash
/gen-demo user-auth
```

**生成文件**：
```
docs/user-auth/_demos/
└── v1_initial.html
```

#### 迭代 Demo

1. 用浏览器打开 HTML 文件
2. 与团队确认交互是否符合预期
3. 根据反馈迭代（v2、v3...）
4. 确认后标记为 `final.html`

#### 检查并通过 Gate

```bash
/check-gate user-auth --phase=3
/approve-gate user-auth --phase=3 --role=PM
/next-phase user-auth
```

---

### 3.4 Phase 4: Design（详细设计）

#### 编写设计文档

编写 `40_DESIGN_FINAL.md`，包含：
- 架构设计
- 数据模型
- API 设计
- 组件设计

#### 执行专家评审（推荐）

```bash
/expert-review docs/user-auth --phase=4
```

**评审重点**：
- 架构合理性
- 可测试性
- 安全性
- 设计一致性

#### 处理评审结果

如果评审结果是 `BLOCK`：

```bash
# 查看详细问题
cat docs/user-auth/REVIEW_ACTIONS.yaml

# 修复问题后重新评审
/expert-review docs/user-auth --phase=4
```

#### 检查并通过 Gate

```bash
/check-gate user-auth --phase=4
/approve-gate user-auth --phase=4 --role=Architect
/next-phase user-auth
```

---

### 3.5 Phase 5: Code（开发实现）

#### 开发流程

1. **创建开发计划**（可选）
   - 编写 `50_DEV_PLAN.md`

2. **实现功能代码**
   - 按照设计文档实现
   - 遵循代码规范

3. **更新进度**
   - 使用 `progress_updater` skill 更新任务状态

#### 检查并通过 Gate

```bash
/check-gate user-auth --phase=5
/approve-gate user-auth --phase=5 --role=Developer
/approve-gate user-auth --phase=5 --role=Architect
/next-phase user-auth
```

---

### 3.8 Phase 5 实战：人机协作详解

本节以 Phase 5 Code 为例，详细展示人（Human）与 Claude Code CLI（CC）之间的交互流程，包括进度更新、断点恢复、多日开发等场景。

#### 3.8.1 核心概念

**90_PROGRESS_LOG.yaml 结构**：

```yaml
meta:
  feature: "user-auth"
  current_phase: 5
  status: wip
  last_updated: "2024-12-16T10:30:00"

phase_5_code:
  status: wip
  tasks:
    - id: CODE-001
      task: "创建 auth 模块目录结构"
      status: done                    # done | wip | pending
      completed_at: "2024-12-15"

    - id: CODE-002
      task: "实现登录页面 UI"
      status: done
      completed_at: "2024-12-15"

    - id: CODE-003
      task: "实现登录 API 调用"
      status: wip                     # 当前进行中的任务
      notes: "正在处理错误响应"

    - id: CODE-004
      task: "实现 Token 存储"
      status: pending

# 断点恢复信息（关键！）
cc_checkpoint:
  session_id: "cc-2024-12-16-user-auth"
  last_file_edited: "src/auth/api.ts"
  last_action: "完成登录 API 基础调用，待处理错误响应"
  next_step: "添加错误处理和重试逻辑"
  context_files:
    - "docs/user-auth/40_DESIGN_FINAL.md"
    - "docs/user-auth/90_PROGRESS_LOG.yaml"
    - "src/auth/api.ts"
    - "src/auth/login.vue"
```

**cc_checkpoint 的作用**：
- `session_id`：标识工作会话
- `last_file_edited`：上次编辑的文件（用于快速定位）
- `last_action`：上次完成的操作（人类可读）
- `next_step`：下一步要做什么（恢复时的起点）
- `context_files`：相关文件列表（恢复时自动加载）

---

#### 3.8.2 典型工作流程：Day 1

```
┌─────────────────────────────────────────────────────────────┐
│ 👤 Human                        │ 🤖 Claude Code CLI        │
├─────────────────────────────────┼───────────────────────────┤
│                                 │                           │
│ /start-day user-auth            │                           │
│                                 │ → git pull origin main    │
│                                 │ → 读取 90_PROGRESS_LOG    │
│                                 │ → 显示当前状态            │
│                                 │                           │
│                                 │ 📍 Phase 5 Code           │
│                                 │ 进度: 25%                 │
│                                 │ 下一步: CODE-003 登录API  │
│                                 │                           │
├─────────────────────────────────┼───────────────────────────┤
│                                 │                           │
│ "开始实现登录 API"              │                           │
│                                 │ → 读取 40_DESIGN_FINAL.md │
│                                 │ → 读取现有代码            │
│                                 │ → 开始编写 api.ts         │
│                                 │                           │
│                                 │ ✅ 已创建 src/auth/api.ts │
│                                 │ 实现了 login() 函数       │
│                                 │                           │
├─────────────────────────────────┼───────────────────────────┤
│                                 │                           │
│ "测试一下登录功能"              │                           │
│                                 │ → npm run dev             │
│                                 │ → 发现错误处理缺失        │
│                                 │                           │
│                                 │ ⚠️ 发现问题：             │
│                                 │ 需要添加错误处理逻辑      │
│                                 │                           │
├─────────────────────────────────┼───────────────────────────┤
│                                 │                           │
│ "好的，先到这里，明天继续"      │                           │
│                                 │                           │
│ /end-day                        │                           │
│                                 │ → 询问今日完成情况        │
│                                 │                           │
│ "CODE-003 进行中，完成了基础    │                           │
│  调用，错误处理明天做"          │                           │
│                                 │                           │
│                                 │ → 更新 PROGRESS_LOG:      │
│                                 │   CODE-003.status = wip   │
│                                 │   CODE-003.notes = "..."  │
│                                 │                           │
│                                 │ → 更新 cc_checkpoint:     │
│                                 │   last_file = api.ts      │
│                                 │   last_action = "完成.."  │
│                                 │   next_step = "添加错误.."│
│                                 │                           │
│                                 │ → git add . && git commit │
│                                 │ → git push (确认后)       │
│                                 │                           │
│                                 │ 🌙 下班流程完成！         │
│                                 │                           │
└─────────────────────────────────┴───────────────────────────┘
```

---

#### 3.8.3 断点恢复：Day 2

```
┌─────────────────────────────────────────────────────────────┐
│ 👤 Human                        │ 🤖 Claude Code CLI        │
├─────────────────────────────────┼───────────────────────────┤
│                                 │                           │
│ /start-day                      │                           │
│                                 │ → git pull origin main    │
│                                 │ → 扫描 docs/ 目录         │
│                                 │ → 找到 user-auth (wip)    │
│                                 │ → 读取 90_PROGRESS_LOG    │
│                                 │ → 读取 cc_checkpoint      │
│                                 │                           │
│                                 │ ┌─────────────────────┐   │
│                                 │ │ 📍 断点恢复         │   │
│                                 │ │                     │   │
│                                 │ │ Session: cc-12-16   │   │
│                                 │ │ 功能: user-auth     │   │
│                                 │ │ 阶段: Phase 5 Code  │   │
│                                 │ │ 进度: 50%           │   │
│                                 │ │                     │   │
│                                 │ │ 🕐 上次状态:        │   │
│                                 │ │ 文件: src/auth/api.ts│  │
│                                 │ │ 操作: 完成登录基础  │   │
│                                 │ │       调用          │   │
│                                 │ │                     │   │
│                                 │ │ ⏭️ 下一步:          │   │
│                                 │ │ 添加错误处理和      │   │
│                                 │ │ 重试逻辑            │   │
│                                 │ │                     │   │
│                                 │ │ 📂 相关文件:        │   │
│                                 │ │ • 40_DESIGN_FINAL   │   │
│                                 │ │ • src/auth/api.ts   │   │
│                                 │ │ • src/auth/login.vue│   │
│                                 │ └─────────────────────┘   │
│                                 │                           │
│                                 │ → 自动读取 context_files  │
│                                 │ → 恢复工作上下文          │
│                                 │                           │
├─────────────────────────────────┼───────────────────────────┤
│                                 │                           │
│ "继续昨天的工作，添加错误处理"  │                           │
│                                 │ → CC 已知道上下文         │
│                                 │ → 直接编辑 api.ts         │
│                                 │ → 添加 try-catch          │
│                                 │ → 添加重试逻辑            │
│                                 │                           │
│                                 │ ✅ 已更新 src/auth/api.ts │
│                                 │ 添加了错误处理和重试      │
│                                 │                           │
├─────────────────────────────────┼───────────────────────────┤
│                                 │                           │
│ "CODE-003 完成了，继续下一个"   │                           │
│                                 │ → 更新 PROGRESS_LOG:      │
│                                 │   CODE-003.status = done  │
│                                 │   CODE-003.completed_at   │
│                                 │   CODE-004.status = wip   │
│                                 │                           │
│                                 │ ✅ CODE-003 已完成        │
│                                 │ 🔄 开始 CODE-004 Token存储│
│                                 │                           │
│                                 │ → 读取设计文档 Token 部分 │
│                                 │ → 开始实现...             │
│                                 │                           │
└─────────────────────────────────┴───────────────────────────┘
```

---

#### 3.8.4 对话过长时的恢复

当对话变得很长，Claude 可能会丢失上下文。此时：

```
┌─────────────────────────────────────────────────────────────┐
│ 👤 Human                        │ 🤖 Claude Code CLI        │
├─────────────────────────────────┼───────────────────────────┤
│                                 │                           │
│ (对话已经很长了...)             │                           │
│                                 │                           │
│ "继续实现 Token 存储"           │                           │
│                                 │ ❓ 我需要更多上下文       │
│                                 │    来理解当前任务...      │
│                                 │                           │
├─────────────────────────────────┼───────────────────────────┤
│                                 │                           │
│ /iresume user-auth              │                           │
│                                 │ → 读取 90_PROGRESS_LOG    │
│                                 │ → 读取 cc_checkpoint      │
│                                 │ → 读取 context_files      │
│                                 │                           │
│                                 │ ┌─────────────────────┐   │
│                                 │ │ 📍 上下文已恢复     │   │
│                                 │ │                     │   │
│                                 │ │ 当前任务:           │   │
│                                 │ │ CODE-004 Token存储  │   │
│                                 │ │                     │   │
│                                 │ │ 已读取文件:         │   │
│                                 │ │ ✅ 40_DESIGN_FINAL  │   │
│                                 │ │ ✅ src/auth/api.ts  │   │
│                                 │ │ ✅ src/auth/store.ts│   │
│                                 │ └─────────────────────┘   │
│                                 │                           │
├─────────────────────────────────┼───────────────────────────┤
│                                 │                           │
│ "好，继续实现"                  │                           │
│                                 │ → 现在有完整上下文了      │
│                                 │ → 继续编写代码...         │
│                                 │                           │
└─────────────────────────────────┴───────────────────────────┘
```

---

#### 3.8.5 进度更新时机

**CC 自动更新进度的时机**：

| 时机 | 更新内容 |
|------|----------|
| 完成一个任务 | `task.status = done`, `task.completed_at` |
| 开始新任务 | `task.status = wip` |
| 遇到阻塞 | `task.status = blocked`, `task.notes` |
| `/end-day` | `cc_checkpoint` 全部字段 |
| 文件编辑后 | `cc_checkpoint.last_file_edited` |

**Human 需要参与的时机**：

| 时机 | Human 动作 |
|------|------------|
| 任务完成确认 | 告诉 CC "这个任务完成了" |
| 下班前 | 执行 `/end-day`，确认今日完成情况 |
| 遇到问题 | 告诉 CC 当前状态和阻塞原因 |
| 切换任务 | 告诉 CC "先做另一个任务" |

---

#### 3.8.6 完整示例对话

以下是一个完整的 Phase 5 工作日对话示例：

```markdown
# Day 1 上午

👤: /start-day user-auth

🤖: 🌅 每日开始 - user-auth

   📥 Git 同步: ✅ 已同步最新代码
   📍 当前阶段: Phase 5 Code
   📈 进度: 25% (1/4 任务完成)

   ⏭️ 下一步: [CODE-002] 实现登录页面 UI

   是否继续上次的工作？

👤: 是的，开始做登录页面

🤖: 好的，我来实现登录页面 UI。

   根据 40_DESIGN_FINAL.md 中的设计：
   - 登录表单包含用户名、密码输入框
   - 包含"记住我"复选框
   - 包含登录按钮和注册链接

   [开始编写 src/auth/login.vue...]

   ✅ 已创建 src/auth/login.vue
   包含以下功能：
   - 响应式表单布局
   - 表单验证
   - 登录按钮状态管理

👤: 看起来不错，这个任务完成了，继续下一个

🤖: ✅ 已更新进度：
   - CODE-002: done (刚完成)
   - CODE-003: wip (开始)

   现在开始 [CODE-003] 实现登录 API 调用...

   [读取设计文档 API 部分...]
   [创建 src/auth/api.ts...]

# Day 1 下午

👤: 我需要离开一会，先暂停

🤖: 好的，我记录一下当前状态：
   - CODE-003 进行中
   - 已完成：API 基础结构
   - 待完成：错误处理、重试逻辑

   稍后继续时，可以直接说"继续登录 API"。

# Day 1 下班

👤: /end-day

🤖: 🌙 好的，让我们整理今天的工作。

   📊 今日完成:
   ✅ CODE-002 实现登录页面 UI

   🔄 进行中:
   • CODE-003 实现登录 API 调用
     └─ 已完成基础结构，待添加错误处理

   更新 cc_checkpoint:
   - last_file: src/auth/api.ts
   - next_step: 添加错误处理和重试逻辑

   [git add . && git commit]
   提交信息: feat(user-auth): 完成登录页面UI，API调用进行中

   是否推送到远程？(y/n)

👤: y

🤖: ✅ 已推送到 origin/main

   🌙 下班流程完成！明天见！

   📋 明日待办:
   ⏭️ CODE-003 添加错误处理
   ⏳ CODE-004 实现 Token 存储

# Day 2 上午

👤: /start-day

🤖: 🌅 早上好！

   📥 Git 同步: ✅ 已是最新
   📍 功能: user-auth
   📈 进度: 50% (2/4 完成)

   🕐 上次状态:
   • 文件: src/auth/api.ts
   • 操作: 完成 API 基础结构

   ⏭️ 下一步: 添加错误处理和重试逻辑

   [已自动加载相关文件上下文]

   继续上次的工作？

👤: 是的

🤖: 好的，继续完善登录 API 的错误处理...

   [编辑 src/auth/api.ts]
   添加内容：
   - try-catch 错误捕获
   - 网络错误重试（最多3次）
   - 错误消息映射

   ✅ 错误处理已添加，CODE-003 完成！

   📊 进度更新:
   - CODE-003: done ✅
   - CODE-004: wip 🔄

   继续实现 Token 存储？

👤: 继续
```

---

### 3.6 Phase 6: Test（测试验证）

#### 编写测试计划

编写 `60_TEST_PLAN.md`，定义：
- 测试用例
- 测试数据
- 预期结果

#### 执行测试

```bash
/run-tests user-auth
```

#### 记录测试结果

编写 `61_TEST_REPORT.md`，记录：
- 测试执行结果
- 发现的问题
- 修复状态

#### 检查并通过 Gate

```bash
/check-gate user-auth --phase=6
/approve-gate user-auth --phase=6 --role=QA
/next-phase user-auth
```

---

### 3.9 Phase 6 实战：测试工具详解

本节详细介绍测试阶段的两大工具：
- **Chrome DevTools MCP**：前端 UI 测试
- **脚本测试**：后端 API 测试

---

#### 3.9.1 Chrome DevTools MCP 简介

Chrome DevTools MCP 是一个 MCP Server，让 Claude Code 可以直接控制浏览器进行 UI 测试。

**核心能力**：

| 能力 | MCP 工具 | 说明 |
|------|----------|------|
| 页面导航 | `navigate_page`, `new_page` | 打开/跳转页面 |
| 页面快照 | `take_snapshot`, `take_screenshot` | 获取页面状态 |
| 元素交互 | `click`, `fill`, `hover` | 点击、输入、悬停 |
| 表单操作 | `fill_form` | 批量填写表单 |
| 键盘操作 | `press_key` | 按键、快捷键 |
| 等待机制 | `wait_for` | 等待元素/文本出现 |
| 控制台 | `list_console_messages` | 查看 console 日志 |
| 网络请求 | `list_network_requests` | 查看 API 请求 |
| 脚本执行 | `evaluate_script` | 执行 JavaScript |

---

#### 3.9.2 前端 UI 测试流程

```
┌─────────────────────────────────────────────────────────────┐
│ 👤 Human                        │ 🤖 Claude Code CLI        │
├─────────────────────────────────┼───────────────────────────┤
│                                 │                           │
│ "测试登录页面的 UI 交互"        │                           │
│                                 │ → 打开浏览器页面          │
│                                 │   mcp: new_page           │
│                                 │   url: localhost:3000     │
│                                 │                           │
│                                 │ → 获取页面快照            │
│                                 │   mcp: take_snapshot      │
│                                 │                           │
│                                 │ 📸 页面结构:              │
│                                 │ - input[uid="u1"] 用户名  │
│                                 │ - input[uid="u2"] 密码    │
│                                 │ - button[uid="u3"] 登录   │
│                                 │                           │
├─────────────────────────────────┼───────────────────────────┤
│                                 │                           │
│ "测试正常登录流程"              │                           │
│                                 │ → 填写表单                │
│                                 │   mcp: fill_form          │
│                                 │   elements:               │
│                                 │   - uid: u1               │
│                                 │     value: testuser       │
│                                 │   - uid: u2               │
│                                 │     value: password123    │
│                                 │                           │
│                                 │ → 点击登录按钮            │
│                                 │   mcp: click              │
│                                 │   uid: u3                 │
│                                 │                           │
│                                 │ → 等待跳转                │
│                                 │   mcp: wait_for           │
│                                 │   text: "欢迎回来"        │
│                                 │                           │
│                                 │ ✅ 测试通过：             │
│                                 │ 登录成功，跳转到首页      │
│                                 │                           │
├─────────────────────────────────┼───────────────────────────┤
│                                 │                           │
│ "测试错误密码的情况"            │                           │
│                                 │ → 导航回登录页            │
│                                 │   mcp: navigate_page      │
│                                 │   url: /login             │
│                                 │                           │
│                                 │ → 填写错误密码            │
│                                 │   mcp: fill_form          │
│                                 │   - uid: u1, value: test  │
│                                 │   - uid: u2, value: wrong │
│                                 │                           │
│                                 │ → 点击登录                │
│                                 │   mcp: click uid: u3      │
│                                 │                           │
│                                 │ → 等待错误提示            │
│                                 │   mcp: wait_for           │
│                                 │   text: "密码错误"        │
│                                 │                           │
│                                 │ ✅ 测试通过：             │
│                                 │ 显示错误提示，未跳转      │
│                                 │                           │
└─────────────────────────────────┴───────────────────────────┘
```

---

#### 3.9.3 Chrome DevTools MCP 常用命令

**1. 页面导航**

```yaml
# 打开新页面
mcp: new_page
url: "http://localhost:3000/login"

# 页面跳转
mcp: navigate_page
type: url
url: "http://localhost:3000/dashboard"

# 返回/前进
mcp: navigate_page
type: back  # 或 forward

# 刷新页面
mcp: navigate_page
type: reload
```

**2. 获取页面状态**

```yaml
# 获取页面快照（推荐，比截图更有用）
mcp: take_snapshot
# 返回页面元素树，每个元素有唯一的 uid

# 截图
mcp: take_screenshot
fullPage: true  # 整页截图
```

**3. 元素交互**

```yaml
# 点击元素
mcp: click
uid: "u123"  # 从 snapshot 获取的 uid

# 双击
mcp: click
uid: "u123"
dblClick: true

# 输入文本
mcp: fill
uid: "u123"
value: "输入的内容"

# 批量填写表单（推荐）
mcp: fill_form
elements:
  - uid: "u1"
    value: "username"
  - uid: "u2"
    value: "password"

# 悬停
mcp: hover
uid: "u123"
```

**4. 等待和验证**

```yaml
# 等待文本出现
mcp: wait_for
text: "登录成功"
timeout: 5000  # 毫秒

# 查看控制台日志
mcp: list_console_messages

# 查看网络请求
mcp: list_network_requests
resourceTypes: ["fetch", "xhr"]
```

**5. 执行 JavaScript**

```yaml
# 执行脚本获取数据
mcp: evaluate_script
function: |
  () => {
    return document.title
  }

# 操作元素
mcp: evaluate_script
function: |
  (el) => {
    return el.innerText
  }
args:
  - uid: "u123"
```

---

#### 3.9.4 后端 API 测试

对于后端 API，使用脚本进行测试。

**测试脚本示例** (`tests/api/auth.test.sh`)：

```bash
#!/bin/bash
# API 测试脚本 - 用户认证

BASE_URL="http://localhost:3000/api"

echo "=========================================="
echo "API 测试: 用户认证模块"
echo "=========================================="

# 测试 1: 正常登录
echo -e "\n[TEST 1] 正常登录"
RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}')

if echo "$RESPONSE" | grep -q '"token"'; then
  echo "✅ PASS: 登录成功，返回 token"
  TOKEN=$(echo "$RESPONSE" | jq -r '.token')
else
  echo "❌ FAIL: 登录失败"
  echo "Response: $RESPONSE"
fi

# 测试 2: 错误密码
echo -e "\n[TEST 2] 错误密码"
RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "wrongpassword"}')

if echo "$RESPONSE" | grep -q '"error"'; then
  echo "✅ PASS: 返回错误信息"
else
  echo "❌ FAIL: 应该返回错误"
fi

# 测试 3: 使用 Token 访问受保护接口
echo -e "\n[TEST 3] Token 验证"
RESPONSE=$(curl -s -X GET "$BASE_URL/user/profile" \
  -H "Authorization: Bearer $TOKEN")

if echo "$RESPONSE" | grep -q '"username"'; then
  echo "✅ PASS: Token 验证成功"
else
  echo "❌ FAIL: Token 验证失败"
fi

echo -e "\n=========================================="
echo "测试完成"
echo "=========================================="
```

**人机交互流程**：

```
┌─────────────────────────────────────────────────────────────┐
│ 👤 Human                        │ 🤖 Claude Code CLI        │
├─────────────────────────────────┼───────────────────────────┤
│                                 │                           │
│ "运行 API 测试"                 │                           │
│                                 │ → 执行测试脚本            │
│                                 │   bash tests/api/auth.sh  │
│                                 │                           │
│                                 │ 📊 测试结果:              │
│                                 │ [TEST 1] ✅ PASS          │
│                                 │ [TEST 2] ✅ PASS          │
│                                 │ [TEST 3] ❌ FAIL          │
│                                 │                           │
│                                 │ ⚠️ 发现问题:              │
│                                 │ Token 验证失败            │
│                                 │                           │
├─────────────────────────────────┼───────────────────────────┤
│                                 │                           │
│ "查看失败原因"                  │                           │
│                                 │ → 分析响应内容            │
│                                 │   Response: 401 Unauthorized│
│                                 │   "Token expired"         │
│                                 │                           │
│                                 │ 💡 问题定位:              │
│                                 │ Token 过期时间设置过短    │
│                                 │ 建议修改 JWT_EXPIRES      │
│                                 │                           │
├─────────────────────────────────┼───────────────────────────┤
│                                 │                           │
│ "修复后重新测试"                │                           │
│                                 │ → 修改配置                │
│                                 │ → 重启服务                │
│                                 │ → 重新执行测试            │
│                                 │                           │
│                                 │ 📊 测试结果:              │
│                                 │ [TEST 1] ✅ PASS          │
│                                 │ [TEST 2] ✅ PASS          │
│                                 │ [TEST 3] ✅ PASS          │
│                                 │                           │
│                                 │ 🎉 全部测试通过！         │
│                                 │                           │
└─────────────────────────────────┴───────────────────────────┘
```

---

#### 3.9.5 测试计划模板

`60_TEST_PLAN.md` 示例：

```markdown
# 60_TEST_PLAN.md
# user-auth 测试计划

## 1. 前端 UI 测试（Chrome DevTools MCP）

### TC-UI-001: 登录页面渲染
- **步骤**: 打开 /login 页面
- **预期**: 显示用户名、密码输入框和登录按钮
- **工具**: take_snapshot

### TC-UI-002: 正常登录流程
- **步骤**:
  1. 输入正确的用户名密码
  2. 点击登录按钮
- **预期**: 跳转到 /dashboard
- **工具**: fill_form → click → wait_for

### TC-UI-003: 错误提示显示
- **步骤**: 输入错误密码，点击登录
- **预期**: 显示"密码错误"提示
- **工具**: fill_form → click → wait_for

### TC-UI-004: 表单验证
- **步骤**: 不输入任何内容，点击登录
- **预期**: 显示必填字段提示
- **工具**: click → take_snapshot

## 2. 后端 API 测试（脚本）

### TC-API-001: POST /api/auth/login 正常登录
- **请求**: {"username": "test", "password": "123"}
- **预期**: 200, 返回 token
- **脚本**: tests/api/auth.test.sh

### TC-API-002: POST /api/auth/login 密码错误
- **请求**: {"username": "test", "password": "wrong"}
- **预期**: 401, 返回错误信息

### TC-API-003: GET /api/user/profile Token 验证
- **请求**: Header Authorization: Bearer {token}
- **预期**: 200, 返回用户信息

## 3. 测试执行顺序

1. 启动开发服务器: `npm run dev`
2. 执行 API 测试: `bash tests/api/auth.test.sh`
3. 执行 UI 测试: 使用 Chrome DevTools MCP
4. 记录结果到 61_TEST_REPORT.md
```

---

#### 3.9.6 测试失败处理策略

**核心原则**：先完成全部测试，记录所有问题，再统一修复。

```
┌────────────────────────────────────────────────────────────┐
│                    测试失败处理流程                          │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  测试用例执行                                                │
│       ↓                                                     │
│  ┌─────────┐                                                │
│  │ 通过？  │                                                │
│  └────┬────┘                                                │
│       │                                                     │
│   Yes │    No                                               │
│       ↓     ↓                                               │
│   记录 ✅   判断严重程度                                     │
│             │                                               │
│     ┌───────┴───────┐                                       │
│     │               │                                       │
│   P0/P1          P2/P3                                      │
│  (阻塞性)       (非阻塞)                                     │
│     │               │                                       │
│     ↓               ↓                                       │
│  暂停测试       记录问题 ❌                                   │
│  立即修复       继续下一个用例                                │
│  重跑当前用例                                                │
│     │               │                                       │
│     └───────┬───────┘                                       │
│             ↓                                               │
│       全部用例执行完毕                                        │
│             ↓                                               │
│       生成测试报告                                           │
│             ↓                                               │
│       统一修复 P2/P3 问题                                    │
│             ↓                                               │
│       回归测试                                               │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

**问题分级标准**：

| 级别 | 定义 | 处理方式 | 示例 |
|------|------|----------|------|
| P0 | 功能完全不可用 | 立即修复 | 页面白屏、登录崩溃 |
| P1 | 核心流程受阻 | 立即修复 | 无法提交表单、跳转错误 |
| P2 | 功能异常但可绕过 | 记录，后续修复 | 错误提示不准确、样式错位 |
| P3 | 体验问题 | 记录，后续修复 | 按钮位置不理想、文案不清晰 |

---

#### 3.9.7 MCP 测试失败示例

**场景：UI 测试发现 P2 问题（继续测试）**

```
┌─────────────────────────────────────────────────────────────┐
│ 👤 Human                        │ 🤖 Claude Code CLI        │
├─────────────────────────────────┼───────────────────────────┤
│                                 │                           │
│ "执行登录功能测试"              │                           │
│                                 │                           │
│                                 │ [TC-UI-001] 页面渲染      │
│                                 │ → mcp: take_snapshot      │
│                                 │ ✅ PASS                   │
│                                 │                           │
│                                 │ [TC-UI-002] 正常登录      │
│                                 │ → mcp: fill_form          │
│                                 │ → mcp: click              │
│                                 │ → mcp: wait_for "欢迎"    │
│                                 │ ✅ PASS                   │
│                                 │                           │
│                                 │ [TC-UI-003] 错误提示      │
│                                 │ → mcp: fill (错误密码)    │
│                                 │ → mcp: click              │
│                                 │ → mcp: wait_for "密码错误"│
│                                 │ ⏱️ 超时...                │
│                                 │ → mcp: take_snapshot      │
│                                 │                           │
│                                 │ ❌ FAIL: 错误提示未显示   │
│                                 │                           │
│                                 │ 📸 当前页面状态:          │
│                                 │ - 表单仍在原位            │
│                                 │ - 无错误提示元素          │
│                                 │ - console: "API 401"      │
│                                 │                           │
│                                 │ 🏷️ 问题分级: P2          │
│                                 │ (功能正常阻止登录，       │
│                                 │  但缺少用户反馈)          │
│                                 │                           │
│                                 │ 📝 记录问题，继续测试...  │
│                                 │                           │
│                                 │ [TC-UI-004] 表单验证      │
│                                 │ → mcp: click (空表单)     │
│                                 │ → mcp: wait_for "必填"    │
│                                 │ ✅ PASS                   │
│                                 │                           │
│                                 │ ---                       │
│                                 │ 📊 测试结果:              │
│                                 │ 通过: 3  失败: 1          │
│                                 │                           │
│                                 │ ❌ 失败用例:              │
│                                 │ TC-UI-003 (P2)            │
│                                 │ - 问题: 错误提示未显示    │
│                                 │ - 原因: 缺少错误处理UI    │
│                                 │ - 建议: 添加 Toast 组件   │
│                                 │                           │
├─────────────────────────────────┼───────────────────────────┤
│                                 │                           │
│ "好的，先修复这个问题"          │                           │
│                                 │ → 读取 login.vue          │
│                                 │ → 添加错误提示逻辑        │
│                                 │                           │
│                                 │ ✅ 已修复:                │
│                                 │ 添加了 el-message 错误提示│
│                                 │                           │
├─────────────────────────────────┼───────────────────────────┤
│                                 │                           │
│ "回归测试 TC-UI-003"            │                           │
│                                 │ → mcp: navigate /login    │
│                                 │ → mcp: fill (错误密码)    │
│                                 │ → mcp: click              │
│                                 │ → mcp: wait_for "密码错误"│
│                                 │                           │
│                                 │ ✅ TC-UI-003 回归通过     │
│                                 │                           │
│                                 │ 📊 最终结果: 4/4 通过     │
│                                 │                           │
└─────────────────────────────────┴───────────────────────────┘
```

---

**场景：UI 测试发现 P0 问题（立即修复）**

```
┌─────────────────────────────────────────────────────────────┐
│ 👤 Human                        │ 🤖 Claude Code CLI        │
├─────────────────────────────────┼───────────────────────────┤
│                                 │                           │
│ "测试登录页面"                  │                           │
│                                 │                           │
│                                 │ [TC-UI-001] 页面渲染      │
│                                 │ → mcp: new_page /login    │
│                                 │ → mcp: take_snapshot      │
│                                 │                           │
│                                 │ ❌ FAIL: 页面渲染失败     │
│                                 │                           │
│                                 │ 📸 页面状态:              │
│                                 │ - 白屏                    │
│                                 │ - console: "Cannot read   │
│                                 │   property 'map' of       │
│                                 │   undefined"              │
│                                 │                           │
│                                 │ 🏷️ 问题分级: P0          │
│                                 │ (页面完全不可用)          │
│                                 │                           │
│                                 │ ⛔ 测试暂停               │
│                                 │ 需要先修复此问题          │
│                                 │                           │
├─────────────────────────────────┼───────────────────────────┤
│                                 │                           │
│ "定位问题"                      │                           │
│                                 │ → 分析 console 错误       │
│                                 │ → 读取 login.vue          │
│                                 │                           │
│                                 │ 💡 问题定位:              │
│                                 │ 第 42 行: users.map()     │
│                                 │ users 初始值为 undefined  │
│                                 │                           │
│                                 │ 建议修复:                 │
│                                 │ users: [] // 初始化空数组 │
│                                 │                           │
├─────────────────────────────────┼───────────────────────────┤
│                                 │                           │
│ "修复它"                        │                           │
│                                 │ → 编辑 login.vue:42       │
│                                 │ → 添加默认值              │
│                                 │                           │
│                                 │ ✅ 已修复                 │
│                                 │                           │
├─────────────────────────────────┼───────────────────────────┤
│                                 │                           │
│ "重新开始测试"                  │                           │
│                                 │ → mcp: navigate /login    │
│                                 │ → mcp: take_snapshot      │
│                                 │                           │
│                                 │ ✅ TC-UI-001 通过         │
│                                 │ 页面正常渲染              │
│                                 │                           │
│                                 │ 继续执行后续测试...       │
│                                 │                           │
└─────────────────────────────────┴───────────────────────────┘
```

---

#### 3.9.8 测试报告记录格式

测试失败时，在 `61_TEST_REPORT.md` 中记录：

```markdown
## 失败用例

### TC-UI-003: 错误提示显示

| 字段 | 内容 |
|------|------|
| 状态 | ❌ FAIL → ✅ FIXED |
| 级别 | P2 |
| 发现时间 | 2024-12-16 10:30 |
| 修复时间 | 2024-12-16 10:45 |

**问题描述**：
输入错误密码后，页面无任何错误提示，用户无法得知登录失败原因。

**复现步骤**：
1. 打开 /login 页面
2. 输入用户名: testuser
3. 输入密码: wrongpassword
4. 点击登录按钮

**预期结果**：
显示"密码错误"提示

**实际结果**：
页面无反应，表单保持原样

**Console 日志**：
```
POST /api/auth/login 401 (Unauthorized)
```

**根因分析**：
login.vue 中缺少 API 错误响应的 UI 处理逻辑

**修复方案**：
添加 el-message.error() 显示错误信息

**修复 Commit**：
`fix(auth): 添加登录失败错误提示 #a1b2c3d`

**回归测试**：
✅ 通过
```

---

#### 3.9.9 完整测试对话示例

```markdown
👤: 开始测试 user-auth 功能

🤖: 好的，我来按照 60_TEST_PLAN.md 执行测试。

   首先确保开发服务器已启动...
   [检查 localhost:3000]

   ✅ 服务器已运行

   ---
   📋 开始 UI 测试
   ---

   [TC-UI-001] 登录页面渲染
   → mcp: new_page url=localhost:3000/login
   → mcp: take_snapshot

   页面元素:
   - input[uid=u1] placeholder="用户名" ✅
   - input[uid=u2] placeholder="密码" ✅
   - button[uid=u3] "登录" ✅

   ✅ TC-UI-001 PASS

   [TC-UI-002] 正常登录流程
   → mcp: fill_form
     - u1: testuser
     - u2: password123
   → mcp: click uid=u3
   → mcp: wait_for text="欢迎回来"

   ✅ TC-UI-002 PASS - 成功跳转到 dashboard

   [TC-UI-003] 错误提示显示
   → mcp: navigate_page url=/login
   → mcp: fill_form
     - u1: testuser
     - u2: wrongpassword
   → mcp: click uid=u3
   → mcp: wait_for text="密码错误"

   ✅ TC-UI-003 PASS - 显示错误提示

   ---
   📋 开始 API 测试
   ---

   → bash tests/api/auth.test.sh

   [TC-API-001] POST /api/auth/login ✅ PASS
   [TC-API-002] POST /api/auth/login 错误密码 ✅ PASS
   [TC-API-003] GET /api/user/profile ✅ PASS

   ---
   📊 测试结果汇总
   ---

   | 测试类型 | 通过 | 失败 | 跳过 |
   |----------|------|------|------|
   | UI 测试  | 4    | 0    | 0    |
   | API 测试 | 3    | 0    | 0    |
   | **总计** | **7**| **0**| **0**|

   🎉 全部测试通过！

   已生成测试报告: docs/user-auth/61_TEST_REPORT.md

👤: 很好，继续下一阶段

🤖: ✅ Phase 6 Test 完成

   执行 Gate 检查...
   → /check-gate user-auth --phase=6

   📋 Gate 状态: ✅ PASSED
   - 测试计划已编写 ✅
   - 测试报告已生成 ✅
   - 无 P0/P1 Bug ✅

   请 QA 审批后继续：
   /approve-gate user-auth --phase=6 --role=QA
```

---

### 3.7 Phase 7: Deploy（发布上线）

#### 编写发布说明

编写 `70_RELEASE_NOTE.md`，包含：
- 版本号
- 新功能列表
- 已知问题
- 升级指南

#### 执行发布

```bash
/release user-auth
```

#### 检查并通过 Gate

```bash
/check-gate user-auth --phase=7
/approve-gate user-auth --phase=7 --role=PM
```

🎉 **功能开发完成！**

---

## 4. 命令速查表

### 4.1 日常命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `/start-day` | 每日开始工作 | `/start-day` 或 `/start-day user-auth` |
| `/end-day` | 每日结束工作 | `/end-day` 或 `/end-day user-auth` |
| `/iresume` | 恢复工作上下文 | `/iresume user-auth` |
| `/check-progress` | 查看进度 | `/check-progress user-auth` |

### 4.2 功能管理命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `/new-feature` | 创建新功能 | `/new-feature user-auth` |
| `/gen-demo` | 生成 Demo | `/gen-demo user-auth` |
| `/daily-summary` | 生成每日总结 | `/daily-summary user-auth` |
| `/release` | 执行发布 | `/release user-auth` |

### 4.3 Foundation Gate 命令（v1.3 新增）

| 命令 | 说明 | 示例 |
|------|------|------|
| `/doc-design-validation` | 执行设计验证 | `/doc-design-validation` 或 `/doc-design-validation --verbose` |
| `/check-foundation-gate` | 检查 Foundation Gate 状态 | `/check-foundation-gate` |
| `/plan-features` | 生成功能开发清单 | `/plan-features`（需先通过 Gate） |
| `/approve-foundation` | 审批 Foundation Gate | `/approve-foundation --role=PM` |

### 4.4 Phase Gate 命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `/next-phase` | 进入下一阶段 | `/next-phase user-auth` |
| `/check-gate` | 检查 Gate 状态 | `/check-gate user-auth --phase=2` |
| `/approve-gate` | 审批 Gate | `/approve-gate user-auth --phase=2 --role=PM` |

### 4.5 质量保障命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `/expert-review` | 执行专家评审 | `/expert-review docs/user-auth --phase=4` |
| `/run-tests` | 运行测试 | `/run-tests user-auth` |

---

## 5. Skills 和 Subagents

### 5.1 Skills（技能）

Skills 是可复用的能力模块，由 Claude 在需要时自动调用。

| Skill | 说明 | 触发场景 |
|-------|------|----------|
| `gate_checker` | Phase Gate 检查 | `/check-gate`、`/next-phase` |
| `progress_updater` | 更新进度日志 | 任务状态变更时 |
| `openai_expert_review` | 调用 OpenAI 执行评审 | `/expert-review` |
| `context_writer` | 编写上下文文档 | 创建功能时 |
| `spec_validator` | 验证规格文档 | Gate 检查时 |
| `test_runner` | 运行测试 | `/run-tests` |
| `doc_generator` | 生成文档 | 各阶段文档生成 |
| `ui_demo` | 生成 Demo | `/gen-demo` |

### 5.2 Subagents（子代理）

Subagents 是专门处理复杂任务的独立代理。

| Subagent | 说明 | 触发场景 |
|----------|------|----------|
| `expert_reviewer` | 独立第三方专家评审 | `/expert-review` |
| `progress_tracker` | 进度追踪 | `/check-progress` |
| `spec_writer` | 规格编写 | Phase 2 |
| `test_plan_writer` | 测试计划编写 | Phase 6 |
| `release_summarizer` | 发布总结 | Phase 7 |

---

## 6. 常见场景处理

### 6.1 对话超长时恢复上下文

当对话变得很长，Claude 可能会丢失上下文。使用以下方法恢复：

```bash
# 方法 1：使用 /iresume 恢复
/iresume user-auth

# 方法 2：查看进度获取上下文
/check-progress user-auth
```

**恢复的信息包括**：
- 当前阶段和状态
- 进行中的任务
- 上次操作和下一步
- 相关文件列表

### 6.2 多日开发同一功能

```bash
# Day 1 结束
/end-day user-auth  # 保存进度，提交代码

# Day 2 开始
/start-day user-auth  # 同步代码，恢复上下文

# Day 2 继续工作...

# Day 2 结束
/end-day user-auth
```

### 6.3 Gate 被阻断

```bash
# 检查阻断原因
/check-gate user-auth --phase=2

# 根据提示修复问题

# 重新检查
/check-gate user-auth --phase=2

# 审批通过
/approve-gate user-auth --phase=2 --role=PM
```

### 6.4 专家评审 BLOCK

```bash
# 查看评审详情
cat docs/user-auth/REVIEW_ACTIONS.yaml
cat docs/user-auth/REVIEW_REPORT.md

# 修复所有 block 级问题

# 重新评审
/expert-review docs/user-auth --phase=4

# 确认通过后继续
/next-phase user-auth
```

### 6.5 跳过 Demo 阶段

如果功能没有 UI，编辑 `PHASE_GATE.yaml`：

```yaml
feature_profile:
  has_ui: false
  demo_required: false
```

Phase 3 将自动跳过。

### 6.6 并行开发多个功能

```bash
# 功能 A
/iresume feature-a
# ... 工作 ...

# 切换到功能 B
/iresume feature-b
# ... 工作 ...

# 查看所有功能进度
/check-progress
```

---

## 7. 最佳实践

### 7.1 文档优先

1. **先写 Context**：明确功能目标和边界
2. **再写 Spec**：定义详细需求
3. **然后 Design**：设计技术方案
4. **最后 Code**：实现功能

### 7.2 及时更新进度

- 完成任务后立即更新状态
- 使用 `/end-day` 保存当日进度
- 保持 `cc_checkpoint` 最新

### 7.3 善用专家评审

- Phase 4 Design 阶段**强烈建议**执行专家评审
- 评审可以发现设计问题，避免后期返工
- `BLOCK` 级问题必须修复

### 7.4 Gate 审批要认真

- 不要跳过 Gate 检查
- 审批代表对质量的承诺
- 问题要在当前阶段解决

### 7.5 保持代码同步

- 每天开始前 `/start-day` 同步代码
- 每天结束时 `/end-day` 提交代码
- 避免长时间不同步导致冲突

---

## 附录：文件结构

```
docs/{feature-name}/
├── 10_CONTEXT.md              # Phase 1: 功能上下文
├── 20_API_SPEC.md             # Phase 2: API 规格（无 UI）
├── 21_UI_FLOW_SPEC.md         # Phase 2: UI 流程规格（有 UI）
├── 40_DESIGN_FINAL.md         # Phase 4: 详细设计
├── 50_DEV_PLAN.md             # Phase 5: 开发计划（可选）
├── 60_TEST_PLAN.md            # Phase 6: 测试计划
├── 61_TEST_REPORT.md          # Phase 6: 测试报告
├── 70_RELEASE_NOTE.md         # Phase 7: 发布说明
├── 90_PROGRESS_LOG.yaml       # 进度日志
├── 91_DAILY_SUMMARY/          # 每日总结
├── PHASE_GATE.yaml            # Gate 规则配置
├── PHASE_GATE_STATUS.yaml     # Gate 运行状态
├── REVIEW_ACTIONS.yaml        # 专家评审结果
├── REVIEW_REPORT.md           # 专家评审报告
└── _demos/                    # Demo 文件目录
```

---

## 更新日志

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.3 | 2026-01-02 | 新增 Phase 0.5 Foundation Gate 机制：User Journey 需求起源层、设计验证、4 个新命令 |
| v1.2 | 2024-12-16 | 添加 Phase 5/6 实战详解 |
| v1.0 | 2024-12-16 | 初始版本 |
