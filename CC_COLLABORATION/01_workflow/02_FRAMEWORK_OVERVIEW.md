# AI 协作开发框架 - 框架概览

> 适用于：需要理解框架体系的用户 | 阅读时间：15 分钟

---

## 一、框架整体架构

### 1.1 8+1 阶段工作流

```
┌─────────────────────────────────────────────────────────────────────┐
│                        AI Coding 8+1 阶段工作流                       │
└─────────────────────────────────────────────────────────────────────┘

项目级（做一次）                      功能级（每个 Feature 循环）
    │                                      │
    ▼                                      ▼
┌──────────┐                         ┌──────────┐
│ Phase 0  │                         │ Phase 1  │
│Foundation│ ────▶ Foundation ────▶  │ Kickoff  │
│ 基础建设  │        Gate            │ 功能启动  │
└──────────┘        ▲                └────┬─────┘
                    │                     │
              ┌─────┴─────┐               ▼
              │ Phase 0.5 │         ┌──────────┐
              │ User Story │         │ Phase 2  │
              │ + PM 规划  │         │   Spec   │
              └───────────┘         │ 规格定义  │
                                    └────┬─────┘
                                         │
    ┌────────────────────────────────────┼────────────────────────────┐
    │                                    ▼                            │
    │   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐ │
    │   │ Phase 3  │───▶│ Phase 4  │───▶│ Phase 5  │───▶│ Phase 6  │ │
    │   │  Demo    │    │  Design  │    │   Code   │    │   Test   │ │
    │   │ 原型验证  │    │ 详细设计  │    │ 开发实现  │    │ 测试验证  │ │
    │   └──────────┘    └──────────┘    └──────────┘    └──────────┘ │
    │         │                                               │       │
    │         │              ┌──────────┐                     │       │
    │         └── (无UI) ───▶│ Phase 7  │◀────────────────────┘       │
    │                        │  Deploy  │                             │
    │                        │ 发布上线  │                             │
    │                        └──────────┘                             │
    └─────────────────────────────────────────────────────────────────┘
```

### 1.2 各阶段概览

| 阶段 | 名称 | 目的 | 关键产出 | 负责角色 |
|------|------|------|----------|---------
| 0 | Foundation | 建立项目基础 | _foundation/ 目录 | Architect |
| 0.5 | User Journey | 需求起源验证 | 01_USER_JOURNEY.md | **PM** |
| 1 | Kickoff | 功能启动 | 10_CONTEXT.md | PM/Architect |
| 2 | Spec | 规格定义 | 21_UI_FLOW_SPEC.md | AI + PM |
| 3 | Demo | 原型验证 | Demo.vue | AI + PM |
| 4 | Design | 详细设计 | 40_DESIGN_FINAL.md | AI + Architect |
| 5 | Code | 开发实现 | 功能代码 | AI + Developer |
| 6 | Test | 测试验证 | 61_TEST_REPORT.md | AI + QA |
| 7 | Deploy | 发布上线 | 70_RELEASE_NOTE.md | PM |

---

## 二、Phase 0.5：需求起源层（核心机制）

### 2.1 为什么需要 Phase 0.5？

**问题**：传统开发流程中，需求往往在传递过程中失真：

```
用户需求 → PM 理解 → 文档描述 → AI 理解 → 代码实现
    ↓          ↓          ↓          ↓          ↓
   100%       80%        60%        40%       ???
```

**解决方案**：建立「需求起源层」，确保每行代码都可追溯到用户价值：

```
User Journey → System Responsibility → Module Mapping → Feature Development
     ↑                                                           │
     └────────────────────── 可追溯 ◀────────────────────────────┘
```

### 2.2 核心文档：01_USER_JOURNEY.md

这是整个框架的**需求起源**，决定了后续所有开发的方向。

```markdown
# 01_USER_JOURNEY.md 结构

## 1. 用户画像
- 主要用户 A：描述
- 次要用户 B：描述

## 2. 主成功路径（Happy Path）

### U1: 用户访问系统
- 用户动作: 打开浏览器，访问网址
- 系统响应: 显示登录页面
- 成功标志: 看到登录表单
- **系统必须做**: 渲染登录页，检查 Session  ← 关键！

### U2: 用户登录
- 用户动作: 输入账号密码，点击登录
- 系统响应: 验证凭证，跳转首页
- 成功标志: 看到欢迎语
- **系统必须做**: 验证凭证，生成 Token，存储 Session

### U3: 用户完成核心操作
...

## 3. 失败路径

### F1: 登录失败 - 密码错误
- 触发条件: 密码不匹配
- 系统处理: 显示错误提示，记录失败次数
- 用户恢复: 重新输入，或找回密码

### F2: 网络异常
...

## 4. 模块映射表 ← 关键！

| 用户步骤 | 模块 ID | 模块名称 | 责任说明 |
|---------|---------|---------|---------
| U1 | M001 | user-auth | 渲染登录页 |
| U2 | M001 | user-auth | 验证凭证 |
| U3 | M002 | dashboard | 展示数据 |
```

### 2.3 Foundation Gate MVS（最小可通过要求）

| 必填区块 | 最小要求 |
|----------|----------|
| 用户画像 | ≥ 1 个主要用户 |
| 主成功路径 | ≥ 3 个用户步骤（U1, U2, U3...） |
| 失败路径 | ≥ 2 个失败场景（F1, F2...） |
| 系统责任声明 | 每个用户步骤都有「系统必须做」 |
| 模块映射表 | 所有 P0 模块都有对应的用户步骤 |

### 2.4 Phase 0.5 工作流程

```bash
# 1. PM 编写 User Journey 文档
# 编辑 docs/_foundation/01_USER_JOURNEY.md

# 2. 执行设计验证
/doc-design-validation
# → 检查用户流程完整性
# → 检查系统责任完整性
# → 检查模块映射完整性

# 3. 检查 Foundation Gate 状态
/check-gate --phase=0

# 4. 审批（需要 PM + Architect）
/approve-gate --phase=0 --role=PM
/approve-gate --phase=0 --role=Architect

# 5. 通过后，生成功能开发清单
/plan-features
# → 输出 FEATURE_CHECKLIST.md
# → 按依赖关系分批：Batch 1, 2, 3...
```

---

## 三、Phase 0.5 与后续阶段的衔接

### 3.1 信息传递链

```
01_USER_JOURNEY.md (Phase 0.5)
    │
    │ 提供：用户步骤、系统责任、失败场景
    │
    ▼
03_MODULE_DECOMPOSITION.md (Phase 0)
    │
    │ 提供：模块定义、scope、acceptance、priority
    │
    ▼
FEATURE_CHECKLIST.md (/plan-features 生成)
    │
    │ 提供：开发顺序、依赖关系、批次分组
    │
    ▼
10_CONTEXT.md (Phase 1)
    │
    │ 注入：scope, acceptance, 相关用户步骤
    │
    ▼
21_UI_FLOW_SPEC.md (Phase 2)
    │
    │ 基于：用户步骤设计页面流程
    │
    ▼
后续 Phase 3-7...
```

### 3.2 衔接示例

**01_USER_JOURNEY.md 中定义**：
```markdown
### U2: 用户登录
- 用户动作: 输入账号密码，点击登录
- 系统响应: 验证凭证，跳转首页
- 系统必须做: 验证凭证，生成 Token，存储 Session

### F1: 登录失败
- 触发条件: 密码不匹配
- 系统处理: 显示错误提示
```

**自动注入到 10_CONTEXT.md**：
```markdown
## 相关用户步骤
- U2: 用户登录

## 系统责任
- 验证凭证
- 生成 Token
- 存储 Session

## 需要处理的失败场景
- F1: 登录失败（密码错误）
```

---

## 四、Phase Gate 机制

### 4.1 三层检查

每个阶段结束时，必须通过 Gate 才能进入下一阶段：

```
Phase N 完成
    │
    ▼
┌─────────────────────────────────────┐
│           Gate 检查（3层）            │
├─────────────────────────────────────┤
│ 1. 必需产出物检查（文件是否存在）      │
│ 2. 质量检查（内容是否完整）           │
│ 3. 审批要求（指定角色是否审批）        │
└──────────────────┬──────────────────┘
                   │
         ┌────────┴────────┐
         │                 │
      通过 ✓           未通过 ✗
         │                 │
         ▼                 ▼
  进入 Phase N+1       修复后重新检查
```

### 4.2 各阶段 Gate 要求

| 阶段 | Gate 检查项 | 审批角色 |
|------|------------|---------
| Phase 0.5 | User Journey MVS、设计验证 PASS | PM + Architect |
| Phase 1 | 10_CONTEXT 完整，目标≥2条 | PM |
| Phase 2 | SPEC 完整，页面/API 已列出 | Architect |
| Phase 3 | Demo 可运行，已评审 | PM |
| Phase 4 | API 契约确定，数据模型完整 | Architect |
| Phase 5 | DEV_PLAN 任务全完成 | Developer |
| Phase 6 | 无 P0/P1 Bug | QA |
| Phase 7 | 文档更新，代码合并 | PM |

### 4.3 Gate 命令

```bash
# 检查 Gate 状态
/check-gate user-auth --phase=2

# 审批通过
/approve-gate user-auth --phase=2 --role=PM

# 进入下一阶段
/next-phase user-auth
```

---

## 五、PM 在框架中的职责

### 5.1 职责清单

| 阶段 | PM 职责 | 交付物 |
|------|---------|--------
| Phase 0 | 编写路线图 | 04_ROADMAP.md |
| **Phase 0.5** | **编写 User Journey** | **01_USER_JOURNEY.md** |
| Phase 0.5 | 审批 Foundation Gate | `/approve-gate --phase=0 --role=PM` |
| Phase 0.5 | 确认功能开发顺序 | 审核 FEATURE_CHECKLIST.md |
| Phase 1 | 审批功能上下文 | `/approve-gate --role=PM` |
| Phase 3 | 评审 Demo | 30_DEMO_REVIEW.md |
| Phase 7 | 审批发布 | `/approve-gate --role=PM` |

### 5.2 PM 的日常命令

```bash
# Phase 0.5
/doc-design-validation         # 验证 User Journey
/check-gate --phase=0         # 检查 Foundation 状态
/approve-gate --phase=0 --role=PM  # 审批通过

# Phase 1
/approve-gate {feature} --phase=1 --role=PM

# Phase 3
/approve-gate {feature} --phase=3 --role=PM

# Phase 7
/approve-gate {feature} --phase=7 --role=PM
```

---

## 六、核心机制总结

### 6.1 三大核心机制

| 机制 | 解决问题 | 实现方式 |
|------|---------|---------
| **Phase Gate** | AI 质量不稳定 | 每阶段设质量关卡 |
| **Expert Review** | AI 既当运动员又当裁判 | 引入第三方 AI 评审 |
| **上下文恢复** | Context window 丢失 | 标准化文档 + `/iresume` |

### 6.2 上下文恢复机制

```
对话产生的信息
       │
       ▼
写入标准化文档
├── 90_PROGRESS_LOG.yaml  ← 进度断点
├── cc_checkpoint         ← 恢复起点
└── context_files         ← 相关文件列表
       │
       ▼
compact/新对话
       │
       ▼
/iresume {feature}
       │
       ▼
从文档恢复上下文
```

---

## 下一步

- 想了解每日具体操作？→ [03_DAILY_OPERATIONS.md](./03_DAILY_OPERATIONS.md)
- 想查阅完整命令参考？→ [04_REFERENCE.md](./04_REFERENCE.md)
- 想快速上手？→ [01_QUICKSTART.md](./01_QUICKSTART.md)

---

_框架版本：v2.0 | 最后更新：2026-01-09_
