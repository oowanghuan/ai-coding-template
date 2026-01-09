# 上下文恢复工作流

> 版本：v2.0
> 最后更新：2026-01-09
> 触发：新会话开始 / 上下文压缩 / /iresume 命令

---

## 1. 概述

本文档定义 Claude Code 上下文恢复的标准流程，确保：
- 快速恢复工作状态
- 准确定位当前进度
- 避免重复工作
- 保持开发连续性

---

## 2. 触发条件

以下情况需要执行恢复流程：

| 场景 | 信号 |
|------|------|
| 新会话开始 | 对话开始无上下文 |
| 上下文压缩 | "Context has been compacted" |
| 用户命令 | `/iresume {feature}` |
| 用户提示 | "继续"、"接着做"、"你还记得吗" |

### 2.1 压缩信号识别

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

### 2.2 自我检测

```yaml
# Claude Code 自检
检查项:
  - 是否知道当前功能模块名称
  - 是否知道当前任务 ID
  - 是否知道上次编辑的文件
  - 是否知道下一步操作

如果任一检查失败 → 执行恢复流程
```

---

## 3. 恢复流程

### Step 1: 立即声明

```markdown
⚠️ 检测到上下文丢失，正在执行恢复...

请稍候，我需要重新加载工作上下文。
```

### Step 2: 查找 PROGRESS_LOG

```yaml
# 搜索策略
1. 检查 docs/ 目录下所有功能模块
2. 查找每个模块的 90_PROGRESS_LOG.yaml
3. 按 last_updated 排序
4. 选择最近更新的模块（或用户指定的模块）
```

### Step 3: 读取 Checkpoint

```yaml
# 从 PROGRESS_LOG 读取
cc_checkpoint:
  session_id: "cc-2026-01-09-002"
  last_file_edited: "src/views/Login.vue"
  last_action: "完成登录表单验证"
  next_step: "实现登录 API 调用"
  context_files:
    - "docs/user-auth/10_CONTEXT.md"
    - "docs/user-auth/40_DESIGN_FINAL.md"
```

### Step 4: 加载上下文文件

```yaml
# 按优先级读取
1. 90_PROGRESS_LOG.yaml   # 当前进度（必须）
2. 50_DEV_PLAN.md         # 任务清单（必须）
3. 40_DESIGN_FINAL.md     # 技术设计（按需）
4. 10_CONTEXT.md          # 功能背景（按需）
5. 其他 context_files 列表中的文件
```

### Step 5: 分析当前状态

```yaml
# 提取关键信息
当前功能: user-auth
当前阶段: Phase 5
进行中任务: TASK-003 - 登录 API 调用
已完成任务: 3 / 5
完成率: 60%

上次操作: 完成登录表单验证
下一步: 实现登录 API 调用
```

### Step 6: 验证代码状态

```yaml
# 检查最后编辑的文件
1. 文件是否存在
2. 内容是否与预期一致
3. 是否有未提交的修改

# 检查 git 状态
git status
git diff
```

### Step 7: 输出恢复报告

```markdown
## 🔄 恢复完成

**功能模块**: user-auth (用户认证)
**当前阶段**: Phase 5 Code
**进度**: 60% (3/5 任务)

### 上下文恢复
- 上次操作: 完成登录表单验证
- 最后编辑: src/views/Login.vue
- 进行中任务: TASK-003 登录 API 调用

### 代码状态
- Git 状态: clean
- 未提交文件: 0 个

### 下一步
实现登录 API 调用

---
是否继续进行 "实现登录 API 调用"？
```

---

## 4. Checkpoint 结构

### 4.1 完整结构

```yaml
cc_checkpoint:
  # 会话标识
  session_id: "cc-{YYYY-MM-DD}-{序号}"

  # 最后操作记录
  last_file_edited: "文件路径"
  last_action: "操作描述"
  last_timestamp: "2026-01-09T15:30:00+08:00"

  # 下一步指引
  next_step: "待执行操作"
  next_task_id: "TASK-003"

  # 上下文文件列表
  context_files:
    - "docs/user-auth/10_CONTEXT.md"
    - "docs/user-auth/40_DESIGN_FINAL.md"
    - "docs/user-auth/50_DEV_PLAN.md"

  # 阻塞项
  blockers: []

  # 备注
  notes: "注意登录失败的错误处理"

  # 可选：临时状态
  temp_state:
    form_data: {...}
    error_info: {...}
```

### 4.2 更新时机

| 时机 | 更新内容 |
|------|----------|
| 完成任务时 | last_action, next_step, next_task_id |
| 编辑文件时 | last_file_edited |
| 切换任务时 | next_step, next_task_id |
| 会话结束时 | 完整更新所有字段 |

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
  1. 列出 docs/ 下所有功能目录
  2. 询问用户当前在哪个功能
  3. 如有多个，显示列表供选择
  4. 从头开始读取该功能文档
```

---

## 6. 异常处理

### 6.1 多功能模块

```yaml
场景: docs/ 下有多个功能目录
处理:
  1. 按 last_updated 排序
  2. 显示最近 3 个模块
  3. 询问用户当前在哪个

输出:
  检测到多个功能模块：
  1. user-auth (更新于 2026-01-09 15:30)
  2. dashboard (更新于 2026-01-09 12:00)
  3. payment (更新于 2026-01-08 18:00)

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

## 7. /iresume 命令

### 7.1 使用方式

```bash
# 恢复指定功能模块
/iresume user-auth

# 恢复当前目录的功能模块（自动检测）
/iresume
```

### 7.2 执行逻辑

```markdown
1. 解析功能名称
2. 查找 90_PROGRESS_LOG.yaml
3. 读取 cc_checkpoint
4. 加载上下文文件
5. 输出恢复结果
6. 等待用户确认继续
```

### 7.3 输出格式

```
🔄 正在恢复工作上下文...

读取文件:
  ✓ docs/user-auth/90_PROGRESS_LOG.yaml
  ✓ docs/user-auth/50_DEV_PLAN.md
  ✓ docs/user-auth/40_DESIGN_FINAL.md

恢复完成

功能: user-auth (用户认证)
阶段: Phase 5 Code
进度: 60% (3/5)

上次操作: 完成登录表单验证
下一步: 实现登录 API 调用

继续开发？[Y/n]
```

---

## 8. Claude Code 执行指南

### 8.1 检测到压缩时

```markdown
## 立即行动

1. 停止当前思考
2. 输出恢复声明
3. 执行恢复流程
4. 不要假设任何上下文
5. 必须从文件重新读取
```

### 8.2 恢复检查清单

```markdown
- [ ] PROGRESS_LOG 已读取
- [ ] cc_checkpoint 已解析
- [ ] context_files 已加载
- [ ] 当前任务已确认
- [ ] 代码状态已验证
- [ ] 下一步已明确
- [ ] 用户已确认继续
```

### 8.3 恢复后行为

```markdown
1. 更新 session_id 为新 ID
2. 继续执行 next_step
3. 正常更新 PROGRESS_LOG
4. 任务完成后正常记录
```

---

## 9. 预防措施

### 9.1 及时保存

```yaml
# 触发 checkpoint 更新的时机
- 每完成一个任务
- 每编辑一个文件
- 每隔 10 分钟
- 用户要求保存时
```

### 9.2 关键信息冗余

```yaml
# 在 PROGRESS_LOG 中保存足够信息
cc_checkpoint:
  session_id: "..."
  last_file_edited: "..."      # 最后编辑的文件
  last_action: "..."           # 最后的操作
  next_step: "..."             # 下一步计划
  current_task_id: "..."       # 当前任务 ID
  context_files: [...]         # 必要的上下文文件
```

### 9.3 定期提交

```yaml
# 建议的提交频率
- 每完成一个任务
- 每 30 分钟
- 重要变更后
- 休息之前
```

---

## CHANGELOG

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v2.0 | 2026-01-09 | 合并 COMPACT_RECOVERY 和 RESUME_FROM_CHECKPOINT |
| v1.0 | 2024-12-10 | 初始版本 |
