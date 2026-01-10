# Skills - 自动触发能力

> 版本：v3.0
> 最后更新：2026-01-09
> 状态：已实现

---

## 什么是 Skill？

> **Skills 是 Claude 自动判断何时应用的能力**，不需要用户显式调用。
>
> 与 Slash Commands 不同，Skills 通过自然语言描述匹配来触发。当用户的需求符合某个 Skill 的触发条件时，Claude 会自动应用该 Skill。

**核心区别**：

| 类型 | 触发方式 | 示例 |
|------|----------|------|
| **Slash Commands** | 用户显式输入 `/xxx` | `/new-feature user-auth` |
| **Skills** | Claude 自动匹配触发 | 用户说「生成个文档」→ Claude 自动应用 doc_generator |

---

## Skills 列表（5 个）

```
skills/
├── README.md              # 本文件
├── doc_generator.md       # 文档生成器
├── review_alignment.md    # 设计一致性检查
├── ui_demo.md             # UI Demo 生成器
├── mock_api_generator.md  # Mock API 生成器
└── design_from_demo.md    # 从 Demo 反推设计
```

| Skill | 触发条件 | 用途 |
|-------|----------|------|
| `doc_generator` | 用户说「生成文档」「创建 SPEC」等 | 根据模板生成标准化文档 |
| `review_alignment` | 用户说「检查一致性」或任务完成后 | 检查代码与设计文档是否一致 |
| `ui_demo` | 用户说「做个 demo」「生成原型」 | 生成可运行的 UI Demo |
| `mock_api_generator` | 用户说「mock 接口」「前端先用假数据」 | 生成 Mock API 代码 |
| `design_from_demo` | Demo 评审后，用户说「整理成正式设计」 | 从 Mock API 反推正式设计文档 |

---

## Skill 文件格式

每个 Skill 文件采用「**触发条件 + 执行指南**」格式：

```markdown
# {skill_name} - {简短描述}

> 类型：Skill（自动触发）
> 版本：v2.0

---

## 何时自动使用

Claude 应该在以下情况**自动应用**这个 skill：

- 触发条件 1
- 触发条件 2
- ...

**不适用场景**：
- 排除条件 1
- ...

---

## 执行方式

### 1. 步骤一
...

### 2. 步骤二
...

---

## 示例对话

**User**: {用户说的话}

**Claude**: [自动应用 xxx skill]
{Claude 的响应}

---

## 注意事项

1. ...
2. ...
```

---

## 与 Phase 的关系

```
Phase 3 Demo     → ui_demo, mock_api_generator
Phase 4 Design   → design_from_demo
Phase 5 Code     → review_alignment

跨阶段通用       → doc_generator
```

---

## 为什么精简到 5 个？

之前的 15 个 Skills 中，大部分实际是「被 Command 调用的内部逻辑」，而非「Claude 自动触发的能力」。

根据 Claude Code 官方定义：
- **Skills = 自动匹配触发**，Claude 根据描述判断何时应用
- **被 Command 调用的逻辑** → 应该合并到 Command 文件中

因此：
- `gate_checker` → 合并到 `/check-gate`
- `progress_updater` → 合并到 `/check-progress`, `/end-day`
- `test_runner` → 合并到 `/run-tests`
- `context_writer` → 合并到 `/new-feature`
- 其他 10 个类似处理...

保留的 5 个 Skills 是真正适合「自动触发」的能力。

---

## 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| v3.0 | 2026-01-09 | 重构：精简至 5 个，采用触发条件格式 |
| v2.0 | 2026-01-09 | 更新至 15 个 Skills |
| v1.0 | 2024-12-11 | 初始版本 |

---

_CC_COLLABORATION Framework v3.1_
