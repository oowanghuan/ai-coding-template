# START_NEW_FEATURE.md
# 新功能启动工作流

> 版本：v1.0
> 最后更新：2024-12-09
> 阶段：Phase 1 Kickoff
> 触发：当需要开发新功能模块时

---

## 1. 概述

本文档定义启动新功能模块的标准流程，确保：
- 功能目录结构统一
- 初始文档完整
- 上下文信息清晰
- Claude Code 能快速进入工作状态

---

## 2. 触发条件

以下情况需要执行本流程：
- 产品需求确认，需要开发新功能
- 技术重构需要，需要新建模块
- 用户执行 `/new-feature` 命令

---

## 3. 执行流程

### Step 1: 确认功能信息

```yaml
# 收集以下信息
feature_name: "{feature-name}"        # 功能代号，kebab-case
feature_title: "{功能中文名称}"
feature_description: "{一句话描述}"
owner: "{@负责人}"
has_ui: true/false                    # 是否有前端 UI
has_api: true/false                   # 是否有后端 API
```

### Step 2: 创建目录结构

```bash
# 在 Docs/ 下创建功能目录
Docs/{feature-name}/
├── 10_CONTEXT.md              # 功能上下文（必须）
├── 40_DESIGN_FINAL.md         # 设计文档（Phase 4 创建）
├── 21_UI_FLOW_SPEC.md         # UI 规格（如有 UI）
├── 20_API_SPEC.md             # API 规格（如有 API）
├── 50_DEV_PLAN.md             # 开发计划（Phase 5 创建）
├── 90_PROGRESS_LOG.yaml       # 进度日志（必须）
├── 91_DAILY_SUMMARY/          # 每日总结目录
├── 60_TEST_PLAN.md            # 测试计划（Phase 6 创建）
├── 61_TEST_REPORT.md          # 测试报告（Phase 6 创建）
└── 70_RELEASE_NOTE.md         # 发布说明（Phase 7 创建）
```

### Step 3: 生成 10_CONTEXT.md

使用 `CONTEXT_TEMPLATE.md` 模板，填写以下内容：

```markdown
# 10_CONTEXT.md
# {功能名称} - 功能上下文

> 版本：v1.0
> 最后更新：{YYYY-MM-DD}
> 状态：Draft
> 负责人：{@username}

## 1. 功能概述

### 1.1 背景
{为什么需要这个功能}

### 1.2 目标
- 目标 1
- 目标 2

### 1.3 预期价值
{功能上线后的收益}

## 2. 功能范围

### 2.1 包含内容（In Scope）
- {功能点 1}
- {功能点 2}

### 2.2 不包含内容（Out of Scope）
- {排除项}

## 3. 用户与场景
{核心用户和使用场景}

## 4. 依赖与集成
{内部/外部依赖}

## 5. 里程碑
| 阶段 | 交付物 | 预计时间 |
|------|--------|----------|
| Kickoff | 10_CONTEXT.md | {日期} |
| ... | ... | ... |
```

### Step 4: 初始化 90_PROGRESS_LOG.yaml

```yaml
# 90_PROGRESS_LOG.yaml
# 功能模块：{feature-name}

meta:
  feature: "{feature-name}"
  feature_name: "{功能中文名称}"
  current_phase: 1  # Kickoff
  status: wip
  owner: "{@负责人}"
  started_at: {YYYY-MM-DD}
  last_updated: {YYYY-MM-DD}

# Phase 1: Kickoff
phase_1_kickoff:
  status: wip
  tasks:
    - id: P1-001
      task: "完成 10_CONTEXT.md"
      status: done
      completed_at: {YYYY-MM-DD}

# Phase 2: Spec
phase_2_spec:
  status: pending
  tasks:
    - id: P2-001
      task: "完成 UI_FLOW_SPEC.md"
      status: pending

# ... 其他阶段

cc_checkpoint:
  session_id: "cc-{YYYY-MM-DD}-001"
  last_file_edited: "Docs/{feature-name}/10_CONTEXT.md"
  last_action: "创建功能目录和初始文档"
  next_step: "完善 CONTEXT 文档，进入 Phase 2 Spec"
  context_files:
    - "Docs/{feature-name}/10_CONTEXT.md"
    - "Docs/_system/01_PROJECT_PROFILE.yaml"

stats:
  summary:
    total_tasks: 0
    done: 1
    pending: 0
    completion_rate: "0%"
```

### Step 5: 创建 91_DAILY_SUMMARY 目录

```bash
mkdir -p Docs/{feature-name}/91_DAILY_SUMMARY
```

### Step 6: 验证完成

检查以下条件：
- [ ] 目录结构已创建
- [ ] 10_CONTEXT.md 已填写基本信息
- [ ] 90_PROGRESS_LOG.yaml 已初始化
- [ ] 91_DAILY_SUMMARY/ 目录已创建

---

## 4. 命令使用

### 4.1 /new-feature 命令

```bash
# 使用方式
/new-feature {feature-name}

# 示例
/new-feature user-subscription
/new-feature payment-gateway
/new-feature dashboard-v2
```

### 4.2 命令执行逻辑

```
1. 解析 feature-name
2. 检查目录是否已存在
3. 创建目录结构
4. 生成 10_CONTEXT.md（基础框架）
5. 生成 90_PROGRESS_LOG.yaml
6. 创建 91_DAILY_SUMMARY/ 目录
7. 输出创建结果
8. 提示下一步操作
```

---

## 5. Claude Code 执行指南

### 5.1 收到 /new-feature 命令时

```markdown
## Claude Code 执行步骤

1. 解析功能名称
   - 确认 feature-name 格式正确（kebab-case）
   - 询问功能中文名称和简要描述

2. 创建目录和文件
   - 创建 Docs/{feature-name}/ 目录
   - 生成 10_CONTEXT.md
   - 生成 90_PROGRESS_LOG.yaml
   - 创建 91_DAILY_SUMMARY/ 目录

3. 输出结果
   - 显示创建的文件列表
   - 提示下一步操作

4. 引导用户
   - 询问是否需要帮助完善 CONTEXT
   - 建议进入 Phase 2 Spec
```

### 5.2 输出示例

```
✅ 功能模块 "user-subscription" 已创建

📁 创建的文件：
  - Docs/user-subscription/10_CONTEXT.md
  - Docs/user-subscription/90_PROGRESS_LOG.yaml
  - Docs/user-subscription/91_DAILY_SUMMARY/

📋 下一步：
  1. 完善 10_CONTEXT.md 中的功能背景和目标
  2. 确认功能范围和依赖
  3. 准备进入 Phase 2 Spec，编写 UI/API 规格

是否需要我帮你完善 CONTEXT 文档？
```

---

## 6. 常见问题

### Q1: 功能名称如何命名？

```
# 规则
- 使用 kebab-case（小写 + 连字符）
- 简短且有意义
- 避免缩写

# 示例
✅ user-subscription
✅ payment-gateway
✅ project-dashboard
❌ UserSubscription
❌ usr-sub
❌ feature_1
```

### Q2: 如果目录已存在怎么办？

```
- 如果是误操作：确认后删除重建
- 如果是继续工作：直接进入，不重新创建
- 如果是版本迭代：使用 feature-v2 命名
```

### Q3: 是否需要一次性填完 CONTEXT？

```
不需要。可以分步完成：
1. 先填写基本信息（背景、目标）
2. 与产品/业务确认后补充范围
3. 技术评审后补充依赖和里程碑
```

---

## 7. 检查清单

### 新功能启动完成标准

- [ ] 目录 `Docs/{feature-name}/` 已创建
- [ ] `10_CONTEXT.md` 包含：
  - [ ] 功能背景
  - [ ] 功能目标
  - [ ] 功能范围（In/Out of Scope）
  - [ ] 负责人信息
- [ ] `90_PROGRESS_LOG.yaml` 已初始化
- [ ] `91_DAILY_SUMMARY/` 目录已创建
- [ ] PROGRESS_LOG 中 Phase 1 标记为 wip

---

## 附录

### A. 目录结构速查

```
Docs/{feature-name}/
├── 10_CONTEXT.md           # Phase 1 创建
├── 40_DESIGN_FINAL.md      # Phase 4 创建
├── 21_UI_FLOW_SPEC.md      # Phase 2 创建（有 UI）
├── 20_API_SPEC.md          # Phase 2 创建（有 API）
├── 50_DEV_PLAN.md          # Phase 5 创建
├── 90_PROGRESS_LOG.yaml    # Phase 1 创建
├── 91_DAILY_SUMMARY/       # Phase 1 创建
├── 60_TEST_PLAN.md         # Phase 6 创建
├── 61_TEST_REPORT.md       # Phase 6 创建
└── 70_RELEASE_NOTE.md      # Phase 7 创建
```

### B. 文档编号说明

| 编号 | 文档 | 创建阶段 |
|------|------|----------|
| 00_ | CONTEXT | Phase 1 |
| 10_ | DESIGN | Phase 4 |
| 11_ | SPEC | Phase 2 |
| 20_ | DEV_PLAN | Phase 5 |
| 30_ | PROGRESS_LOG | Phase 1 |
| 31_ | DAILY_SUMMARY | Phase 1 |
| 40_ | TEST_PLAN | Phase 6 |
| 41_ | TEST_REPORT | Phase 6 |
| 50_ | RELEASE_NOTE | Phase 7 |
