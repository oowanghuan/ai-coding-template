# {date} 开发日报

> 功能模块：{feature_name}
> 日期：{date}
> 作者：{author}

---

## 今日进展

### 完成的任务

| 任务 ID | 任务描述 | 状态 |
|---------|---------|------|
| {TASK-001} | {任务描述} | ✅ 完成 |
| {TASK-002} | {任务描述} | ✅ 完成 |

### 进行中的任务

| 任务 ID | 任务描述 | 进度 | 备注 |
|---------|---------|------|------|
| {TASK-003} | {任务描述} | 60% | {进展说明} |

### 阻塞/风险

<!-- 如无阻塞，删除此节 -->

| 问题 | 影响 | 需要支持 |
|------|------|---------|
| {问题描述} | {影响范围} | {需要谁/什么帮助} |

---

## 代码变更摘要

### 新增文件

```
{path/to/new/file1.ts}
{path/to/new/file2.vue}
```

### 修改文件

```
{path/to/modified/file.ts} - {修改说明}
```

### 关键代码片段

<!-- 可选：记录重要的实现逻辑 -->

```typescript
// {文件路径}:{行号}
// {简要说明}
{关键代码}
```

---

## Git 提交记录

```
{commit_hash_1} {commit_message_1}
{commit_hash_2} {commit_message_2}
```

---

## 明日计划

- [ ] {计划任务 1}
- [ ] {计划任务 2}
- [ ] {计划任务 3}

---

## 学习/经验记录

<!-- 可选：记录今天学到的东西或踩过的坑 -->

### 问题与解决方案

**问题**：{遇到的问题}

**原因**：{问题原因}

**解决**：{解决方法}

### 最佳实践

- {今天发现的好做法}

---

## 元信息

```yaml
# 用于工具解析
feature: "{feature_id}"
date: "{date}"
phase: {current_phase}
tasks_completed: {count}
tasks_in_progress: {count}
blockers: {count}
commits: {count}
```

---

<!--
模板使用说明（创建后删除）：

1. 文件命名：91_DAILY_SUMMARY/{YYYY-MM-DD}.md
   例如：91_DAILY_SUMMARY/2024-12-11.md

2. 替换占位符：
   - {date}: 日期，如 "2024-12-11"
   - {feature_name}: 功能名称
   - {feature_id}: 功能 ID
   - {author}: 作者名
   - {TASK-XXX}: 任务 ID（对应 90_PROGRESS_LOG.yaml）
   - {current_phase}: 当前阶段号 (0-7)

3. 删除不需要的节：
   - 无阻塞时删除"阻塞/风险"
   - 无学习记录时删除"学习/经验记录"

4. 工具生成：
   - /daily-summary 命令会自动生成此文件
   - 从 git log 和 PROGRESS_LOG 自动提取信息
-->
