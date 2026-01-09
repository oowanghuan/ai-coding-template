# 启动新功能工作流

> 版本：v2.0
> 最后更新：2026-01-09
> 触发：/new-feature 命令 或 开始新功能开发时

---

## 1. 概述

本文档定义启动新功能开发的标准流程，确保：
- 功能目录结构规范
- 初始文档完整
- 上下文清晰
- 可追溯到 User Journey

---

## 2. 触发条件

- 用户执行 `/new-feature {name}` 命令
- 从 FEATURE_CHECKLIST 选择新功能开始开发
- PM 审批通过后开始新功能

---

## 3. 启动流程

### Step 1: 验证功能名称

```yaml
# 功能名称规范
格式: kebab-case (小写字母 + 连字符)
示例: user-auth, dashboard-chart, payment-gateway

# 检查
- 不含特殊字符
- 不含空格
- 不与现有功能重名
```

### Step 2: 创建目录结构

```bash
docs/{feature-name}/
├── 10_CONTEXT.md           # 功能上下文（Phase 1）
├── 90_PROGRESS_LOG.yaml    # 进度日志
└── 91_DAILY_SUMMARY/       # 每日总结目录
```

### Step 3: 初始化 10_CONTEXT.md

```markdown
# {Feature Name} - 功能上下文

> 阶段：Phase 1 Kickoff
> 创建时间：{date}
> 负责人：{owner}

---

## 1. 功能背景

### 1.1 关联用户步骤

| 用户步骤 | 描述 |
|---------|------|
| U{n} | {从 01_USER_JOURNEY.md 引用} |

### 1.2 系统责任

- {从 USER_JOURNEY 提取的系统责任}

---

## 2. 功能目标

- [ ] 目标 1
- [ ] 目标 2

---

## 3. 范围定义

### 3.1 包含（In Scope）

-

### 3.2 不包含（Out of Scope）

-

---

## 4. 验收标准

- [ ] 验收标准 1
- [ ] 验收标准 2

---

## 5. 依赖关系

### 5.1 依赖的模块

| 模块 | 依赖内容 |
|------|---------|
| | |

### 5.2 被依赖的模块

| 模块 | 依赖内容 |
|------|---------|
| | |

---

## 6. 技术约束

-

---

## 7. 相关文档

- [01_USER_JOURNEY.md](../_foundation/01_USER_JOURNEY.md)
- [03_MODULE_DECOMPOSITION.md](../_foundation/03_MODULE_DECOMPOSITION.md)
```

### Step 4: 初始化 90_PROGRESS_LOG.yaml

```yaml
# 进度日志

meta:
  feature_id: "{feature-name}"
  feature_name: "{功能中文名}"
  current_phase: 1
  current_phase_name: "Kickoff"
  started_at: {date}
  updated_at: {date}

tasks: []

cc_checkpoint:
  session_id: "cc-{date}-001"
  last_file_edited: "docs/{feature-name}/10_CONTEXT.md"
  last_action: "创建功能目录"
  next_step: "完善 10_CONTEXT.md"
  context_files:
    - "docs/{feature-name}/10_CONTEXT.md"
  blockers: []
  notes: ""
```

### Step 5: 输出启动报告

```markdown
## ✓ 功能创建成功

**功能名称**: {feature-name}
**功能目录**: docs/{feature-name}/

### 已创建文件
- 10_CONTEXT.md (功能上下文)
- 90_PROGRESS_LOG.yaml (进度日志)
- 91_DAILY_SUMMARY/ (每日总结目录)

### 下一步
1. 完善 10_CONTEXT.md 的功能背景
2. 定义功能目标和验收标准
3. 确认依赖关系
4. 提交 Phase 1 Gate 审批

### 相关命令
/check-gate {feature-name} --phase=1  # 检查 Gate
/approve-gate {feature-name} --phase=1 --role=PM  # 审批
/next-phase {feature-name}  # 进入 Phase 2
```

---

## 4. 从 User Journey 注入上下文

### 4.1 自动注入内容

从 `01_USER_JOURNEY.md` 提取：
- 关联的用户步骤 (U1, U2...)
- 系统责任声明
- 相关失败场景 (F1, F2...)

从 `03_MODULE_DECOMPOSITION.md` 提取：
- 模块 scope
- acceptance criteria
- 依赖关系

### 4.2 注入示例

```markdown
## 1. 功能背景

### 1.1 关联用户步骤

| 用户步骤 | 描述 |
|---------|------|
| U2 | 用户输入账号密码登录系统 |
| U3 | 用户查看个人信息 |

### 1.2 系统责任

- 验证用户凭证
- 生成访问 Token
- 存储用户会话
- 返回用户基本信息

### 1.3 需要处理的失败场景

| 场景 | 处理方式 |
|------|---------|
| F1 | 密码错误：显示错误提示，记录失败次数 |
| F2 | 账号不存在：提示账号不存在，引导注册 |
```

---

## 5. 检查清单

```markdown
- [ ] 功能名称符合规范 (kebab-case)
- [ ] 目录结构已创建
- [ ] 10_CONTEXT.md 已初始化
- [ ] 90_PROGRESS_LOG.yaml 已初始化
- [ ] User Journey 上下文已注入
- [ ] 依赖关系已确认
- [ ] 可以开始 Phase 1 工作
```

---

## CHANGELOG

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v2.0 | 2026-01-09 | 更新目录结构，添加 User Journey 注入 |
| v1.0 | 2024-12-10 | 初始版本 |
