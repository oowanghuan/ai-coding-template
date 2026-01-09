# 人机协作指南

> 版本：v1.0
> 最后更新：2026-01-09
> 适用范围：Claude Code 与人类开发者的协作规范

---

## 1. 沟通原则

### 1.1 主动汇报进度

- 完成任务时告知
- 遇到问题时说明

### 1.2 清晰表达

- 说明做了什么
- 说明为什么这样做
- 说明下一步是什么

### 1.3 询问不确定的问题

- 遇到歧义时询问
- 提供选项让人类决策
- 解释各选项的利弊

---

## 2. 决策边界

### 2.1 Claude Code 可自主决策

- 代码实现细节
- 变量命名选择
- 代码格式调整
- 小范围重构

### 2.2 需要人类确认

- 架构设计决策
- 新依赖引入
- API 接口设计
- 数据库 Schema
- 删除功能代码

---

## 3. 工作流程

### 3.1 会话开始

```markdown
## 会话开始检查清单

1. [ ] 读取 PROGRESS_LOG 中的 cc_checkpoint
2. [ ] 确认上次工作的位置和状态
3. [ ] 读取相关的 CONTEXT 和 DESIGN 文档
4. [ ] 确认当前要执行的任务
5. [ ] 开始工作
```

### 3.2 工作过程中

```markdown
## 工作过程检查清单

1. [ ] 每完成一个任务，更新 PROGRESS_LOG
2. [ ] 每完成一个任务，验证结果
3. [ ] 遇到阻塞时标记并说明
4. [ ] 长对话中定期更新 checkpoint
5. [ ] 重大决策记录在相关文档中
```

### 3.3 会话结束

```markdown
## 会话结束检查清单

1. [ ] 更新 PROGRESS_LOG 中所有完成的任务状态
2. [ ] 更新 cc_checkpoint：
   - session_id
   - last_file_edited
   - last_action
   - next_step
   - context_files
3. [ ] 提交代码（如有变更）
4. [ ] 生成或更新 DAILY_SUMMARY（如需要）
```

---

## 4. 上下文恢复

### 4.1 触发条件

上下文恢复在以下情况下触发：

1. **新会话开始** - 每次新对话开始
2. **上下文压缩** - 对话过长被 compact
3. **中断恢复** - 异常中断后继续

### 4.2 恢复流程

```markdown
## 上下文恢复步骤

1. 读取 PROGRESS_LOG
   - 获取 cc_checkpoint 信息
   - 获取当前阶段和进度

2. 读取上下文文件
   - 根据 context_files 列表读取
   - 至少包含 CONTEXT 和 DESIGN

3. 确认当前状态
   - 确认 next_step 是否仍然有效
   - 确认是否有阻塞项

4. 继续工作
   - 从 next_step 继续
   - 或根据实际情况调整
```

### 4.3 Checkpoint 格式

```yaml
cc_checkpoint:
  session_id: "cc-2024-12-09-001"           # 会话标识
  last_file_edited: "src/views/Login.vue"   # 最后编辑的文件
  last_action: "完成登录表单验证"            # 最后完成的操作
  next_step: "实现登录 API 调用"             # 下一步任务
  context_files:                             # 需要读取的上下文文件
    - "Docs/feature-name/10_CONTEXT.md"
    - "Docs/feature-name/40_DESIGN_FINAL.md"
    - "Docs/feature-name/50_DEV_PLAN.md"
  blockers: []                               # 当前阻塞项
  notes: "注意登录失败的错误处理"             # 其他备注
```

---

## 5. 进度追踪

### 5.1 PROGRESS_LOG 更新

```yaml
# 任务完成时更新
tasks:
  - id: TASK-001
    task: "实现登录表单"
    status: done                    # pending → wip → done
    completed_at: 2024-12-09        # 添加完成时间

# 开始新任务时更新
  - id: TASK-002
    task: "实现登录 API"
    status: wip                     # 标记为进行中
```

### 5.2 状态定义

| 状态 | 说明 | 使用场景 |
|------|------|----------|
| `pending` | 待开始 | 任务尚未开始 |
| `wip` | 进行中 | 正在执行的任务 |
| `done` | 已完成 | 任务完成且验证通过 |
| `blocked` | 阻塞 | 因依赖或问题无法继续 |

---

## 6. 快速参考

### 6.1 常用文件路径

```
CC_COLLABORATION/
├── _gui_config/               # GUI 依赖配置
├── _project_context/          # 项目背景（本文档所在）
├── 01_workflow/               # 工作流文档
├── 03_templates/              # 文档模板
├── 05_tools/                  # 工具说明
├── 07_phase_gate/             # Phase Gate 机制
└── 08_legacy_integration/     # 现有项目整合

docs/_foundation/
├── 00_PROJECT_CONTEXT.md      # 项目背景
├── 01_PROJECT_PROFILE.yaml    # 项目配置
├── 02_API_CONVENTIONS.md      # API 规范
├── 03_DB_CONVENTIONS.md       # DB 规范
└── _ui_system/                # UI 规范

docs/{feature}/
├── 10_CONTEXT.md              # 功能背景
├── 40_DESIGN_FINAL.md         # 设计文档
├── 50_DEV_PLAN.md             # 开发计划
├── 90_PROGRESS_LOG.yaml       # 进度日志
└── 91_DAILY_SUMMARY/          # 每日总结
```

### 6.2 状态速查

| 任务状态 | 含义 | 下一步 |
|----------|------|--------|
| pending | 待开始 | 开始任务，标记为 wip |
| wip | 进行中 | 完成后标记为 done |
| done | 已完成 | 验证通过，继续下一个 |
| blocked | 阻塞 | 记录原因，寻求帮助 |

### 6.3 Commit 类型

| 类型 | 说明 |
|------|------|
| feat | 新功能 |
| fix | 修复 Bug |
| docs | 文档更新 |
| style | 格式调整 |
| refactor | 重构 |
| test | 测试 |
| chore | 其他 |

---

_文档版本：v1.0 | 最后更新：2026-01-09_
