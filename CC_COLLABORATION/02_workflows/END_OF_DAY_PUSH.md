# END_OF_DAY_PUSH.md
# 每日结束工作流

> 版本：v1.0
> 最后更新：2024-12-10
> 阶段：Phase 5 Code
> 触发：每日工作结束时 / 用户要求提交时

---

## 1. 概述

本文档定义每日工作结束时的标准流程，确保：
- 工作进度被正确记录
- 代码变更被正确提交
- 下次工作可快速恢复
- 团队成员了解进度

---

## 2. 触发条件

以下情况需要执行本流程：
- 用户说"今天就到这里"
- 用户说"下班了"
- 用户要求"保存进度"
- 用户要求"提交代码"
- 长时间无交互（可选自动触发）

---

## 3. 执行流程

### Step 1: 保存当前工作

```yaml
# 检查当前状态
1. 检查是否有未保存的文件编辑
   - 如有，确认保存

2. 检查当前任务状态
   - 如任务进行中，记录进度
   - 如任务完成，更新状态为 done

3. 记录临时状态（如有）
   - 表单填写进度
   - 调试信息
   - 待处理问题
```

### Step 2: 更新 PROGRESS_LOG

```yaml
# 更新任务状态
phase_5_code:
  tasks:
    - id: FE-003
      task: "列表页实现"
      status: wip → done  # 或保持 wip
      progress: "80%"     # 如果未完成
      notes: "搜索功能已完成，待实现分页"

# 更新 checkpoint
cc_checkpoint:
  session_id: "cc-2024-12-10-003"
  last_file_edited: "src/views/UserList.vue"
  last_action: "完成搜索功能"
  next_step: "实现分页功能"
  context_files:
    - "Docs/user-management/90_PROGRESS_LOG.yaml"
    - "Docs/user-management/50_DEV_PLAN.md"

# 更新统计
stats:
  summary:
    total_tasks: 25
    done: 14
    wip: 1
    pending: 10
    completion_rate: "56%"
```

### Step 3: 生成 DAILY_SUMMARY

```markdown
# 91_DAILY_SUMMARY/{YYYY-MM-DD}.md

## {功能名称} - 每日总结

日期：2024-12-10
阶段：Phase 5 Code
进度：56% (14/25)

### 今日完成

| 任务 ID | 任务描述 | 状态 |
|---------|----------|------|
| FE-002 | 路由配置 | done |
| FE-003 | 列表页实现（部分）| wip |

### 具体工作

1. **FE-002: 路由配置**
   - 添加列表页路由
   - 添加详情页路由
   - 配置路由守卫

2. **FE-003: 列表页实现**
   - 完成基础表格结构
   - 完成搜索表单
   - 待完成：分页功能

### 遇到的问题

1. Element Plus Table 列宽自适应问题
   - 原因：固定宽度导致溢出
   - 解决：使用 min-width 替代 width

### 明日计划

- [ ] 完成 FE-003 分页功能
- [ ] 开始 FE-004 详情页实现
- [ ] 开始 FE-005 表单弹窗

### 风险提示

- 无

---
自动生成于 2024-12-10 18:30
```

### Step 4: 提交代码

```bash
# 1. 检查变更
git status
git diff

# 2. 暂存变更
git add .

# 3. 提交代码
git commit -m "feat(user): 完成用户列表页搜索功能

- 添加搜索表单组件
- 实现关键词搜索
- 实现状态筛选
- 待完成分页功能

进度：56% (14/25)
任务：FE-003 列表页实现

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### Step 5: 输出总结

```markdown
今日工作总结

📊 进度：56% (14/25)

✅ 今日完成：
- FE-002: 路由配置
- FE-003: 列表页搜索功能

🔄 进行中：
- FE-003: 待完成分页功能

📝 已更新：
- Docs/{feature}/90_PROGRESS_LOG.yaml
- Docs/{feature}/91_DAILY_SUMMARY/2024-12-10.md

💾 已提交：
- commit: abc1234

📌 明日继续：
- 完成 FE-003 分页功能
- 开始 FE-004 详情页

祝您晚安！🌙
```

---

## 4. Commit 规范

### 4.1 提交信息格式

```
<type>(<scope>): <subject>

<body>

进度：{完成率}% ({完成}/{总数})
任务：{task_id} {task_name}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### 4.2 Type 类型

| Type | 说明 |
|------|------|
| feat | 新功能 |
| fix | Bug 修复 |
| refactor | 重构 |
| style | 样式调整 |
| docs | 文档更新 |
| test | 测试相关 |
| chore | 构建/工具变更 |

### 4.3 示例

```
feat(user): 完成用户列表页基础功能

- 实现数据表格展示
- 添加分页组件
- 添加搜索筛选
- 添加新增/编辑/删除操作

进度：60% (15/25)
任务：FE-003 列表页实现

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## 5. DAILY_SUMMARY 模板

```markdown
# {YYYY-MM-DD}.md

## {功能名称} - 每日总结

日期：{YYYY-MM-DD}
阶段：{当前阶段}
进度：{完成率}% ({完成}/{总数})

### 今日完成

| 任务 ID | 任务描述 | 状态 |
|---------|----------|------|
| {id} | {描述} | {done/wip} |

### 具体工作

1. **{任务ID}: {任务名称}**
   - {工作内容1}
   - {工作内容2}

### 遇到的问题

1. {问题描述}
   - 原因：{原因分析}
   - 解决：{解决方案}

### 明日计划

- [ ] {计划1}
- [ ] {计划2}

### 风险提示

- {风险描述，无则填"无"}

---
自动生成于 {YYYY-MM-DD HH:mm}
```

---

## 6. Claude Code 执行指南

### 6.1 检测结束信号

```yaml
# 识别以下表述
触发词:
  - "今天就到这里"
  - "下班了"
  - "先这样吧"
  - "保存一下进度"
  - "提交代码"
  - "commit 一下"
  - "收工"
```

### 6.2 执行检查清单

```markdown
- [ ] 所有文件已保存
- [ ] PROGRESS_LOG 已更新
- [ ] cc_checkpoint 已更新
- [ ] DAILY_SUMMARY 已生成
- [ ] 代码已提交（如用户要求）
- [ ] 输出今日总结
```

### 6.3 异常处理

```markdown
## 常见问题

1. 有未保存的修改
   → 提示用户并询问是否保存

2. 任务状态不确定
   → 询问用户当前任务完成度

3. git 提交失败
   → 显示错误信息，建议手动处理

4. 冲突或合并问题
   → 警告用户，不自动处理
```

---

## 7. 自动化程度

| 操作 | 自动化程度 | 说明 |
|------|------------|------|
| 更新 PROGRESS_LOG | 自动 | 每次任务状态变更时 |
| 更新 checkpoint | 自动 | 每次操作后 |
| 生成 DAILY_SUMMARY | 半自动 | 用户触发后自动生成 |
| Git add | 需确认 | 显示变更后询问 |
| Git commit | 需确认 | 显示信息后询问 |
| Git push | 手动 | 不自动执行 |

---

## CHANGELOG

| 版本 | 日期 | 作者 | 变更内容 |
|------|------|------|----------|
| v1.0 | 2024-12-10 | Claude | 初始版本 |
