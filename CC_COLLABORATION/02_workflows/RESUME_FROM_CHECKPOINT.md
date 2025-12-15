# RESUME_FROM_CHECKPOINT.md
# 断点恢复工作流

> 版本：v1.0
> 最后更新：2024-12-10
> 阶段：Phase 5 Code
> 触发：新会话开始时 / 上下文压缩后 / 执行 /iresume 命令

---

## 1. 概述

本文档定义 Claude Code 断点恢复的标准流程，确保：
- 快速恢复工作上下文
- 准确定位当前进度
- 避免重复工作
- 保持开发连续性

---

## 2. 触发条件

以下情况需要执行本流程：
- 新的对话会话开始
- 上下文窗口压缩后
- 用户执行 `/iresume` 命令
- 用户要求"继续之前的工作"

---

## 3. 恢复流程

### Step 1: 读取 Checkpoint

```yaml
# 读取 PROGRESS_LOG.yaml 中的 cc_checkpoint
cc_checkpoint:
  session_id: "cc-2024-12-10-001"
  last_file_edited: "src/views/UserList.vue"
  last_action: "完成列表页基础结构"
  next_step: "实现搜索功能"
  context_files:
    - "Docs/{feature}/90_PROGRESS_LOG.yaml"
    - "Docs/{feature}/50_DEV_PLAN.md"
    - "Docs/{feature}/40_DESIGN_FINAL.md"
```

### Step 2: 加载上下文文件

```yaml
# 按顺序读取关键文件
1. 90_PROGRESS_LOG.yaml   # 当前进度
2. 50_DEV_PLAN.md         # 任务清单
3. 40_DESIGN_FINAL.md     # 技术设计
4. 21_UI_FLOW_SPEC.md     # UI 规格（如需要）
5. 20_API_SPEC.md         # API 规格（如需要）
```

### Step 3: 分析当前状态

```yaml
# 从 PROGRESS_LOG 中提取
当前阶段: Phase 5 Code
进行中任务:
  - FE-003: 列表页实现 (wip)

已完成任务:
  - DB-001 ~ DB-003
  - BE-001 ~ BE-007
  - FE-001, FE-002

待开始任务:
  - FE-004 ~ FE-008
  - IT-001 ~ IT-004

完成率: 52%
```

### Step 4: 确定下一步

```yaml
# 根据 checkpoint 和任务状态确定
next_step: "实现搜索功能"
current_task: FE-003
verification: "搜索关键词能正确过滤列表"
```

### Step 5: 输出恢复结果

```markdown
## 恢复完成

**功能模块**: {feature-name}
**当前阶段**: Phase 5 Code (开发实现)
**进度**: 52% (13/25 任务)

### 上次工作
- 文件: `src/views/UserList.vue`
- 操作: 完成列表页基础结构

### 进行中任务
- FE-003: 列表页实现
  - 下一步: 实现搜索功能

### 待处理任务
- FE-004: 详情页实现
- FE-005: 表单弹窗实现
- ...

是否继续 FE-003 的开发？
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
  last_timestamp: "2024-12-10T15:30:00+08:00"

  # 下一步指引
  next_step: "待执行操作"
  next_task_id: "FE-003"

  # 上下文文件列表
  context_files:
    - "必须读取的文件1"
    - "必须读取的文件2"

  # 可选：临时状态
  temp_state:
    form_data: {...}       # 临时表单数据
    search_params: {...}   # 搜索条件
    error_info: {...}      # 错误信息
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

### 5.1 正常恢复

```yaml
# 上次正常结束
场景: checkpoint 完整，任务状态清晰
策略: 直接继续 next_step
```

### 5.2 中断恢复

```yaml
# 上次异常中断（没有更新 checkpoint）
场景: last_action 与代码状态不一致
策略:
  1. 检查最后编辑的文件状态
  2. 对比 DEV_PLAN 确定实际进度
  3. 更新 PROGRESS_LOG
  4. 继续未完成任务
```

### 5.3 冲突恢复

```yaml
# 有未提交的更改
场景: 工作目录有未保存的修改
策略:
  1. 询问用户如何处理
  2. 选项 A: 保留并继续
  3. 选项 B: 放弃并重新开始
```

---

## 6. /iresume 命令

### 6.1 使用方式

```bash
# 恢复指定功能模块
/iresume {feature-name}

# 恢复当前目录的功能模块
/iresume
```

### 6.2 执行逻辑

```markdown
1. 解析功能名称
2. 查找 PROGRESS_LOG.yaml
3. 读取 cc_checkpoint
4. 加载上下文文件
5. 输出恢复结果
6. 等待用户确认继续
```

### 6.3 输出格式

```
正在恢复工作上下文...

读取文件:
  ✓ Docs/{feature}/90_PROGRESS_LOG.yaml
  ✓ Docs/{feature}/50_DEV_PLAN.md
  ✓ Docs/{feature}/40_DESIGN_FINAL.md

恢复完成

功能: {功能名称}
阶段: Phase 5 Code
进度: 52% (13/25)

上次操作: 完成列表页基础结构
下一步: 实现搜索功能

继续开发？[Y/n]
```

---

## 7. Claude Code 执行指南

### 7.1 新会话开始时

```markdown
## 自动检测恢复

1. 检查是否存在 PROGRESS_LOG.yaml
2. 如果存在且状态为 wip：
   - 读取 checkpoint
   - 输出恢复建议
3. 如果不存在或状态为 done：
   - 询问用户需求
```

### 7.2 恢复检查清单

```markdown
- [ ] checkpoint 存在且有效
- [ ] context_files 都可读取
- [ ] 任务状态与代码一致
- [ ] 无冲突的未提交更改
- [ ] 下一步操作明确
```

### 7.3 异常处理

```markdown
## 常见问题

1. checkpoint 不存在
   → 从 PROGRESS_LOG 推断当前状态

2. context_files 文件缺失
   → 警告用户，尝试继续

3. 任务状态不一致
   → 重新分析代码状态，更新 PROGRESS_LOG

4. 功能模块已完成
   → 提示用户功能已完成，询问下一步
```

---

## 8. 示例场景

### 场景 1: 正常恢复

```yaml
# 用户发送 /iresume user-management

输入:
  feature: user-management
  checkpoint:
    session_id: "cc-2024-12-09-003"
    last_action: "完成 UserList.vue 列表渲染"
    next_step: "添加搜索表单"

输出:
  恢复 user-management 工作上下文

  上次进度:
  - 完成 UserList.vue 列表渲染
  - 进度 40% (10/25)

  继续任务:
  - FE-003: 列表页实现
  - 下一步: 添加搜索表单

  开始工作...
```

### 场景 2: 上下文压缩后恢复

```yaml
# 对话上下文被压缩，用户说"继续"

输入:
  user_message: "继续"
  context_lost: true

执行:
  1. 检测到上下文丢失
  2. 查找最近的 PROGRESS_LOG
  3. 读取 checkpoint
  4. 恢复上下文

输出:
  检测到上下文压缩，正在恢复...

  已恢复功能: user-management
  当前任务: FE-003 列表页实现
  下一步: 添加搜索表单

  继续...
```

---

## CHANGELOG

| 版本 | 日期 | 作者 | 变更内容 |
|------|------|------|----------|
| v1.0 | 2024-12-10 | Claude | 初始版本 |
