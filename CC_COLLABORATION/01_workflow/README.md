# AI 协作开发工作流文档

> 版本：v2.1 | 最后更新：2026-01-11

---

## 文档导航

根据你的需求选择合适的文档：

| 文档 | 适用场景 | 阅读时间 |
|------|---------|---------
| [01_QUICKSTART.md](./01_QUICKSTART.md) | 首次使用，快速上手 | 5 分钟 |
| [02_FRAMEWORK_OVERVIEW.md](./02_FRAMEWORK_OVERVIEW.md) | 理解框架体系、Phase 0.5 机制 | 15 分钟 |
| [03_DAILY_OPERATIONS.md](./03_DAILY_OPERATIONS.md) | 开发过程中查阅、人机协作详解 | 按需 |
| [04_REFERENCE.md](./04_REFERENCE.md) | 查阅命令、工具、模板、Commit 规范 | 按需 |
| [05_PM_DRIVER_WORKFLOW.md](./05_PM_DRIVER_WORKFLOW.md) | **PM Driver 详解**：项目级和功能级自动化编排 | 30 分钟 |
| [recipes/](./recipes/) | 工作流 Recipe（上下文恢复、新功能等） | 按需 |

---

## 快速入口

### 新手上路

```bash
/init-project              # 初始化项目
/new-feature user-auth     # 创建第一个功能
```

→ 详见 [01_QUICKSTART.md](./01_QUICKSTART.md)

### 每日工作

```bash
/start-day                 # 上班第一件事
/iresume {feature}         # 恢复上下文（最重要！）
/end-day                   # 下班前
```

→ 详见 [03_DAILY_OPERATIONS.md](./03_DAILY_OPERATIONS.md)

### Phase Gate

```bash
/check-gate {feature} --phase=N
/approve-gate {feature} --phase=N --role=XX
/next-phase {feature}
```

→ 详见 [02_FRAMEWORK_OVERVIEW.md](./02_FRAMEWORK_OVERVIEW.md)

### PM Driver（项目级编排）

```bash
/project-pm init              # 初始化项目追踪
/project-pm ready             # 获取可执行任务
/project-pm assign            # 生成 dev agent 命令
/project-pm check             # 检查进度
/project-pm status            # 查看整体状态
```

→ 详见 [05_PM_DRIVER_WORKFLOW.md](./05_PM_DRIVER_WORKFLOW.md)

### AI PM Driver（功能级编排）

```bash
/ai-pm start {feature} --mode=full_auto    # 启动自动编排
/ai-pm status {feature}                    # 查看状态
/ai-pm pause/resume/stop {feature}         # 控制执行
```

→ 详见 [05_PM_DRIVER_WORKFLOW.md](./05_PM_DRIVER_WORKFLOW.md)

---

## 核心概念

```
8+1 阶段工作流:
Phase 0 (Foundation) → Phase 0.5 (User Journey) → Phase 1-7 (功能开发循环)

三大核心机制:
1. Phase Gate - 质量门禁
2. Expert Review - 独立评审
3. /iresume - 上下文恢复
```

---

## Recipe 快速索引

| Recipe | 用途 |
|--------|------|
| [CONTEXT_RECOVERY.md](./recipes/CONTEXT_RECOVERY.md) | 上下文恢复（compact/新对话） |
| [START_NEW_FEATURE.md](./recipes/START_NEW_FEATURE.md) | 启动新功能开发 |
| [END_OF_DAY.md](./recipes/END_OF_DAY.md) | 每日结束保存进度 |
| [UI_DEMO.md](./recipes/UI_DEMO.md) | 生成 UI Demo + Mock API |
| [PARALLEL_DEVELOPMENT.md](./recipes/PARALLEL_DEVELOPMENT.md) | **多 Feature 并行开发**（PM Driver） |

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v2.1 | 2026-01-11 | 新增 PM Driver 工作流文档，添加项目级和功能级编排详解 |
| v2.0 | 2026-01-09 | 目录重组：合并 workflow 文档，整合 commit 规范 |
| v1.5 | 2026-01-02 | 新增 Phase 0.5 Foundation Gate 机制 |
| v1.4 | 2024-12-16 | 添加 Phase 5/6 实战详解 |

---

_Generated with Claude Code_
