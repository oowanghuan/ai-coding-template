# AI 协作开发框架 - 5分钟快速入门

> 适用于：首次使用者 | 阅读时间：5 分钟

---

## 这个框架是做什么的？

**一句话**：让 AI 按照标准化流程开发软件，解决三大痛点：

| 痛点 | 解决方案 |
|------|---------
| AI 质量不稳定 | Phase Gate 质量门禁 |
| Context 容易丢失 | `/iresume` 断点恢复 |
| 需求和开发脱节 | Phase 0.5 User Journey |

---

## 最小工作流（10 步上线一个功能）

```
/init-project           # 1. 初始化项目（一次性）
/plan-features          # 2. 生成功能清单

/new-feature user-auth  # 3. 创建功能
# 编写 10_CONTEXT.md    # 4. 填写功能背景
/next-phase             # 5. 进入下一阶段

# ... 编写规格、设计、代码 ...

/start-day              # 6. 每天开始
/iresume user-auth      # 7. 恢复上下文（最重要！）
/end-day                # 8. 每天结束

/run-tests user-auth    # 9. 执行测试
/release user-auth v1.0 # 10. 发布上线
```

---

## 10 个最常用命令

### 每日必用（4 个）

| 命令 | 用途 | 使用时机 |
|------|------|----------|
| `/start-day` | 同步代码，显示待办 | 上班第一件事 |
| `/iresume {feature}` | 恢复工作上下文 | **对话变长时必用** |
| `/check-progress` | 查看进度 | 随时 |
| `/end-day` | 提交代码，保存断点 | 下班前 |

### 功能开发（3 个）

| 命令 | 用途 | 使用阶段 |
|------|------|----------|
| `/new-feature {name}` | 创建新功能模块 | Phase 1 |
| `/gen-demo {feature}` | 生成可交互 Demo | Phase 3 |
| `/run-tests {feature}` | 执行测试 | Phase 6 |

### 阶段控制（3 个）

| 命令 | 用途 | 使用时机 |
|------|------|----------|
| `/check-gate` | 检查是否可以通过 | 阶段完成时 |
| `/approve-gate` | 审批通过 | Gate 检查通过后 |
| `/next-phase` | 进入下一阶段 | 审批后 |

---

## 快速开始：3 步创建第一个功能

### Step 1: 初始化项目

```bash
# 在 Claude Code 中执行
/init-project
```

这会创建 `docs/_foundation/` 目录，包含项目基础文档。

### Step 2: 创建功能

```bash
/new-feature user-auth
```

这会创建 `docs/user-auth/` 目录和初始文档。

### Step 3: 开始开发

```bash
# 每天工作前
/start-day
/iresume user-auth

# 开发完成后
/end-day
```

---

## 遇到问题怎么办？

### 对话太长，Claude 忘记上下文了

```bash
/iresume user-auth
```

这是**最重要的命令**，会自动读取之前的进度和上下文。

### 不知道当前状态

```bash
/check-progress user-auth
```

会显示当前阶段、完成百分比、下一步任务。

### 阶段完成后怎么办

```bash
/check-gate user-auth --phase=2   # 检查
/approve-gate user-auth --phase=2 --role=PM  # 审批
/next-phase user-auth             # 进入下一阶段
```

---

## 下一步

- 想了解完整框架？→ [02_FRAMEWORK_OVERVIEW.md](./02_FRAMEWORK_OVERVIEW.md)
- 想了解每日工作细节？→ [03_DAILY_OPERATIONS.md](./03_DAILY_OPERATIONS.md)
- 想查阅所有命令？→ [04_REFERENCE.md](./04_REFERENCE.md)

---

_阅读完成！现在可以执行 `/new-feature my-first-feature` 开始你的第一个功能了。_
