# COMPACT_RECOVERY.md
# 上下文压缩恢复工作流

> 版本：v1.0
> 最后更新：2024-12-10
> 阶段：Phase 5 Code
> 触发：当系统提示上下文已压缩时

---

## 1. 概述

本文档定义上下文压缩后的强制恢复流程，确保：
- 快速识别上下文丢失
- 自动恢复工作状态
- 避免重复或遗漏工作
- 保持开发连续性

---

## 2. 触发条件

以下情况表明上下文已被压缩：
- 系统提示 "Context has been compacted"
- 系统提示 "Previous conversation summarized"
- Claude Code 无法记起之前的对话内容
- 用户说"你忘了我们在做什么"

---

## 3. 压缩识别

### 3.1 压缩信号

```yaml
# 系统提示示例
"This session is being continued from a previous conversation that ran out of context."
"The conversation is summarized below:"

# 用户信号
- "继续"
- "接着做"
- "刚才说到哪了"
- "你还记得吗"
```

### 3.2 自我检测

```yaml
# Claude Code 自检
检查项:
  - 是否知道当前功能模块名称
  - 是否知道当前任务 ID
  - 是否知道上次编辑的文件
  - 是否知道下一步操作

如果任一检查失败 → 执行强制恢复
```

---

## 4. 强制恢复流程

### Step 1: 立即声明

```markdown
⚠️ 检测到上下文压缩，正在执行强制恢复...

请稍候，我需要重新加载工作上下文。
```

### Step 2: 查找 PROGRESS_LOG

```yaml
# 搜索策略
1. 检查 Docs/ 目录下所有功能模块
2. 查找每个模块的 30_PROGRESS_LOG.yaml
3. 按 last_updated 排序
4. 选择最近更新的模块

# 搜索命令
find Docs/ -name "30_PROGRESS_LOG.yaml" -type f
```

### Step 3: 读取 Checkpoint

```yaml
# 从 PROGRESS_LOG 读取
cc_checkpoint:
  session_id: "cc-2024-12-10-002"
  last_file_edited: "..."
  last_action: "..."
  next_step: "..."
  context_files:
    - "..."
```

### Step 4: 加载上下文文件

```yaml
# 按顺序读取
1. 30_PROGRESS_LOG.yaml    # 当前进度
2. 20_DEV_PLAN.md          # 任务清单
3. 10_DESIGN_FINAL.md      # 技术设计（如需要）
4. 其他 context_files 列表中的文件
```

### Step 5: 分析当前状态

```yaml
# 提取关键信息
当前功能: {feature-name}
当前阶段: Phase {n}
进行中任务: {task_id} - {task_name}
已完成任务: {n} / {total}
完成率: {n}%

上次操作: {last_action}
下一步: {next_step}
```

### Step 6: 验证代码状态

```yaml
# 检查最后编辑的文件
1. 文件是否存在
2. 内容是否与预期一致
3. 是否有未完成的修改

# 检查 git 状态
git status
git diff
```

### Step 7: 输出恢复报告

```markdown
## 恢复完成

**功能模块**: {feature-name}
**当前阶段**: Phase {n} ({phase_name})
**进度**: {完成率}% ({完成}/{总数})

### 上下文恢复
- 上次操作: {last_action}
- 最后编辑: {last_file_edited}
- 进行中任务: {current_task}

### 代码状态
- Git 状态: {clean / has changes}
- 未提交文件: {n} 个

### 下一步
{next_step}

---
是否继续进行 {next_step}？
```

---

## 5. 恢复策略

### 5.1 完整恢复

```yaml
场景: checkpoint 完整，文件状态一致
策略: 直接继续 next_step
```

### 5.2 部分恢复

```yaml
场景: checkpoint 存在，但部分信息缺失
策略:
  1. 从 DEV_PLAN 推断当前进度
  2. 检查代码变更确认实际状态
  3. 更新 PROGRESS_LOG
  4. 继续工作
```

### 5.3 最小恢复

```yaml
场景: 只有 PROGRESS_LOG，其他上下文缺失
策略:
  1. 读取 PROGRESS_LOG 获取基本信息
  2. 询问用户确认当前任务
  3. 重新加载必要文档
  4. 继续工作
```

### 5.4 失败恢复

```yaml
场景: PROGRESS_LOG 也不存在
策略:
  1. 列出 Docs/ 下所有功能目录
  2. 询问用户当前在哪个功能
  3. 如有多个，显示列表供选择
  4. 从头开始读取该功能文档
```

---

## 6. 异常处理

### 6.1 多功能模块

```yaml
场景: Docs/ 下有多个功能目录
处理:
  1. 按 last_updated 排序
  2. 显示最近 3 个模块
  3. 询问用户当前在哪个

输出:
  检测到多个功能模块：
  1. user-management (更新于 2024-12-10 15:30)
  2. project-dashboard (更新于 2024-12-10 12:00)
  3. payment-gateway (更新于 2024-12-09 18:00)

  请选择当前正在开发的模块 [1/2/3]：
```

### 6.2 状态不一致

```yaml
场景: checkpoint 与代码实际状态不一致
处理:
  1. 对比 last_action 与代码变更
  2. 显示差异
  3. 询问用户如何处理

选项:
  A. 以代码为准，更新 PROGRESS_LOG
  B. 以 PROGRESS_LOG 为准，回滚代码
  C. 手动解决
```

### 6.3 文件丢失

```yaml
场景: context_files 中的文件不存在
处理:
  1. 跳过缺失文件
  2. 记录警告
  3. 尝试从其他来源获取信息
  4. 继续恢复流程
```

---

## 7. Claude Code 执行指南

### 7.1 检测到压缩时

```markdown
## 立即行动

1. 停止当前思考
2. 输出恢复声明
3. 执行强制恢复流程
4. 不要假设任何上下文
5. 必须从文件重新读取
```

### 7.2 恢复检查清单

```markdown
- [ ] PROGRESS_LOG 已读取
- [ ] cc_checkpoint 已解析
- [ ] context_files 已加载
- [ ] 当前任务已确认
- [ ] 代码状态已验证
- [ ] 下一步已明确
- [ ] 用户已确认继续
```

### 7.3 恢复后行为

```markdown
1. 更新 session_id 为新 ID
2. 继续执行 next_step
3. 正常更新 PROGRESS_LOG
4. 任务完成后正常记录
```

---

## 8. 预防措施

### 8.1 及时保存

```yaml
# 触发 checkpoint 更新的时机
- 每完成一个任务
- 每编辑一个文件
- 每隔 10 分钟
- 用户要求保存时
```

### 8.2 关键信息冗余

```yaml
# 在 PROGRESS_LOG 中保存足够信息
cc_checkpoint:
  session_id: "..."
  last_file_edited: "..."      # 最后编辑的文件
  last_action: "..."           # 最后的操作
  next_step: "..."             # 下一步计划
  current_task_id: "..."       # 当前任务 ID
  current_task_progress: "..." # 任务进度描述
  context_files: [...]         # 必要的上下文文件
  temp_state: {...}            # 临时状态（可选）
```

### 8.3 定期提交

```yaml
# 建议的提交频率
- 每完成一个任务
- 每 30 分钟
- 重要变更后
- 休息之前
```

---

## 9. 示例场景

### 场景 1: 正常恢复

```
系统: This session is being continued from a previous conversation...

Claude: ⚠️ 检测到上下文压缩，正在执行强制恢复...

读取文件:
  ✓ Docs/user-management/30_PROGRESS_LOG.yaml
  ✓ Docs/user-management/20_DEV_PLAN.md

恢复完成

功能: user-management (用户管理)
阶段: Phase 5 Code
进度: 60% (15/25)

上次操作: 完成 UserList.vue 搜索功能
下一步: 实现分页功能

继续实现分页功能？[Y/n]
```

### 场景 2: 多模块选择

```
Claude: ⚠️ 检测到上下文压缩，正在执行强制恢复...

检测到多个功能模块：
1. user-management (更新于 15:30)
2. project-dashboard (更新于 12:00)

您当前在开发哪个模块？[1/2]

用户: 1

读取 user-management 上下文...

恢复完成
...
```

---

## CHANGELOG

| 版本 | 日期 | 作者 | 变更内容 |
|------|------|------|----------|
| v1.0 | 2024-12-10 | Claude | 初始版本 |
