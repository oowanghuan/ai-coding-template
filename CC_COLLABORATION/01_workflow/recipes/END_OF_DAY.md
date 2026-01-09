# 每日结束工作流

> 版本：v2.0
> 最后更新：2026-01-09
> 触发：/end-day 命令 或 下班前

---

## 1. 概述

本文档定义每日工作结束时的标准流程，确保：
- 进度被正确保存
- 代码被提交
- 断点信息完整
- 明天可以顺利恢复

---

## 2. 触发条件

- 用户执行 `/end-day` 命令
- 下班前
- 长时间中断前
- 切换到其他任务前

---

## 3. 结束流程

### Step 1: 更新任务状态

```yaml
# 在 PROGRESS_LOG 中更新
tasks:
  - id: TASK-003
    task: "实现登录表单验证"
    status: done                # wip → done
    completed_at: 2026-01-09

  - id: TASK-004
    task: "实现登录 API 调用"
    status: wip                 # 保持 wip 或改为 pending
```

### Step 2: 保存 Checkpoint

```yaml
cc_checkpoint:
  session_id: "cc-2026-01-09-003"
  last_file_edited: "src/views/Login.vue"
  last_action: "完成登录表单验证"
  next_step: "完成登录 API 错误处理"
  context_files:
    - "docs/user-auth/10_CONTEXT.md"
    - "docs/user-auth/40_DESIGN_FINAL.md"
    - "docs/user-auth/50_DEV_PLAN.md"
  blockers: []
  notes: "注意处理网络超时情况"
```

### Step 3: 提交代码

```bash
# 检查变更
git status
git diff

# 提交
git add .
git commit -m "feat(auth): 实现登录表单验证逻辑

完成内容：
- 表单字段验证
- 错误提示显示
- 提交按钮状态控制

Co-Authored-By: Claude <noreply@anthropic.com>"

# 推送
git push origin {branch}
```

### Step 4: 生成每日总结（可选）

```markdown
# 每日总结 - 2026-01-09

## 今日完成

### user-auth (用户认证)
- [x] TASK-003: 实现登录表单验证
- [ ] TASK-004: 实现登录 API 调用 (进行中 50%)

## 代码变更
- +150 行 / -20 行
- 修改文件: 3 个

## 进度更新
- Phase 5 Code: 60% → 75%

## 明日计划
- 完成 TASK-004: 登录 API 错误处理
- 开始 TASK-005: Token 存储

## 阻塞项
- 无
```

### Step 5: 输出结束报告

```markdown
## 📤 今日工作已保存

### 进度更新
- ✓ TASK-003: 实现登录表单验证 [done]
- ○ TASK-004: 实现登录 API 调用 [wip]

### Checkpoint 已保存
- next_step: "完成登录 API 错误处理"

### 代码已提交
- feat(auth): 实现登录表单验证逻辑
- 已推送到 origin/feature/user-auth

### 今日统计
- 完成任务: 1
- 进行中: 1
- 代码变更: +150 / -20

---
明天执行 `/iresume user-auth` 继续工作
```

---

## 4. Checkpoint 保存要点

### 4.1 必填字段

| 字段 | 说明 | 重要性 |
|------|------|--------|
| session_id | 会话标识 | 高 |
| last_file_edited | 最后编辑的文件 | 高 |
| last_action | 最后完成的操作 | 高 |
| next_step | 下一步任务 | **最高** |
| context_files | 需要加载的文件列表 | 高 |

### 4.2 next_step 撰写要点

```yaml
# 好的 next_step
next_step: "完成登录 API 的错误处理，包括网络超时和服务器错误"

# 不好的 next_step
next_step: "继续工作"  # 太模糊
next_step: "登录"      # 不够具体
```

### 4.3 context_files 选择

```yaml
# 必须包含
- 90_PROGRESS_LOG.yaml   # 进度日志
- 50_DEV_PLAN.md         # 任务清单

# 根据需要包含
- 40_DESIGN_FINAL.md     # 技术设计（开发阶段）
- 21_UI_FLOW_SPEC.md     # UI 规格（前端开发）
- 20_API_SPEC.md         # API 规格（后端开发）
```

---

## 5. 提交规范

### 5.1 Commit Message 格式

```
<type>(<scope>): <subject>

<body>

Co-Authored-By: Claude <noreply@anthropic.com>
```

### 5.2 常用 Type

| Type | 说明 |
|------|------|
| feat | 新功能 |
| fix | 修复 |
| docs | 文档 |
| style | 格式 |
| refactor | 重构 |
| test | 测试 |
| chore | 杂项 |

### 5.3 示例

```bash
git commit -m "feat(auth): 实现登录表单验证逻辑

完成内容：
- 用户名必填验证
- 密码长度验证 (6-20字符)
- 表单提交防重复点击

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## 6. 检查清单

```markdown
## 每日结束检查清单

- [ ] 任务状态已更新 (wip/done)
- [ ] PROGRESS_LOG 已保存
- [ ] cc_checkpoint 信息完整
  - [ ] next_step 具体明确
  - [ ] context_files 列表正确
- [ ] 代码已提交
- [ ] 代码已推送
- [ ] 每日总结已生成（可选）
```

---

## 7. 异常处理

### 7.1 有未完成的改动

```yaml
场景: 代码改动未完成，不适合提交
处理:
  1. 在 checkpoint 中记录当前状态
  2. 使用 git stash 暂存（可选）
  3. 明确记录 next_step
```

### 7.2 有阻塞项

```yaml
场景: 遇到阻塞无法继续
处理:
  1. 在 blockers 中详细记录
  2. 标记相关任务为 blocked
  3. 记录已尝试的解决方案
```

### 7.3 紧急中断

```yaml
场景: 需要紧急离开
处理:
  1. 至少更新 next_step
  2. 保存 PROGRESS_LOG
  3. 其他可以明天补充
```

---

## CHANGELOG

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v2.0 | 2026-01-09 | 重构文档结构，添加检查清单 |
| v1.0 | 2024-12-10 | 初始版本 |
