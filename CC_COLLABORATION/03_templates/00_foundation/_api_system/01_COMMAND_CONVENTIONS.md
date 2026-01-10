# 01_COMMAND_CONVENTIONS.md
# Slash Command 设计规范

> 版本：v1.0
> 最后更新：{timestamp}
> 适用范围：所有 Claude Code Slash Command 定义

---

## 1. 概述

本文档定义项目中所有 Slash Command 的设计规范，确保：
- 命令命名一致性
- 参数格式标准化
- 输出行为可预测
- 便于 Claude Code 理解和执行

---

## 2. 命令设计原则

### 2.1 命名规范

```
# 格式
/{action}-{target}

# 规则
- 使用小写字母
- 使用连字符（kebab-case）分隔单词
- 动词在前，名词在后
- 保持简洁，2-3 个单词最佳

# 正确示例
/new-feature           # 创建新功能
/check-gate            # 检查 Gate 状态
/approve-gate          # 审批 Gate
/next-phase            # 进入下一阶段
/expert-review         # 执行专家评审

# 错误示例
/newFeature            # 不要用驼峰命名
/new_feature           # 不要用下划线
/create-new-feature    # 过于冗长
/feature               # 缺少动词，不明确
```

### 2.2 参数规范

```
# 位置参数（必填）
/{command} <required-param>

# 选项参数（可选）
/{command} [options]
/{command} --option=value
/{command} --flag

# 混合使用
/{command} <required> [--option=value]

# 示例
/new-feature <feature-name>
/check-gate <feature-path> --phase=N
/approve-gate <feature-path> --role=PM
```

### 2.3 参数类型

| 类型 | 格式 | 示例 |
|------|------|------|
| 路径 | `<path>` | `docs/user-auth` |
| 名称 | `<name>` | `user-auth` |
| 数字 | `--num=N` | `--phase=2` |
| 枚举 | `--enum=VAL` | `--role=PM` |
| 布尔 | `--flag` | `--dry-run` |

---

## 3. 命令文件结构

### 3.1 标准模板

```markdown
# {command-name}.md
# /{command-name} - {一句话描述}

## 用途
{详细说明命令的用途和使用场景}

## 语法
/{command-name} <required-param> [options]

## 参数
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `<param>` | string | 是 | 参数说明 |
| `--option` | string | 否 | 选项说明（默认值：xxx） |

## 前置条件
- 条件 1
- 条件 2

## 执行步骤
1. 步骤 1
2. 步骤 2
3. 步骤 3

## 输出
- 成功时：{描述}
- 失败时：{描述}

## 示例
/{command-name} example-value
/{command-name} example-value --option=value

## 相关命令
- `/{related-command-1}`: 描述
- `/{related-command-2}`: 描述
```

### 3.2 文件位置

```
.claude/
  commands/
    {command-name}.md      # 命令定义文件
```

---

## 4. 命令分类

### 4.1 工作流命令

| 命令 | 用途 | 生命周期阶段 |
|------|------|-------------|
| `/new-feature` | 创建新功能目录和文件 | 启动 |
| `/check-gate` | 检查当前阶段 Gate 状态 | 阶段转换 |
| `/approve-gate` | 审批当前阶段 Gate | 阶段转换 |
| `/next-phase` | 进入下一阶段 | 阶段转换 |
| `/iresume` | 恢复中断的工作 | 恢复 |

### 4.2 评审命令

| 命令 | 用途 | 触发时机 |
|------|------|----------|
| `/expert-review` | 触发第三方评审 | Spec/Design/Code 完成后 |

### 4.3 查询命令

| 命令 | 用途 |
|------|------|
| `/status` | 查看功能当前状态 |
| `/history` | 查看操作历史 |

---

## 5. 输出规范

### 5.1 成功输出

```markdown
✅ {命令名称} 执行成功

**操作摘要**：
- {操作 1}
- {操作 2}

**下一步**：
- {建议的下一步操作}
```

### 5.2 失败输出

```markdown
❌ {命令名称} 执行失败

**错误原因**：
{具体原因}

**解决方法**：
{可执行的修复建议}
```

### 5.3 阻断输出

```markdown
🚫 {命令名称} 被阻断

**阻断原因**：
- {原因 1}
- {原因 2}

**解决方法**：
1. {步骤 1}
2. {步骤 2}
```

---

## 6. 错误处理

### 6.1 标准错误类型

| 错误类型 | 错误码 | 用户提示 |
|----------|--------|----------|
| 参数缺失 | `ERR_MISSING_PARAM` | "缺少必填参数：{param}" |
| 参数无效 | `ERR_INVALID_PARAM` | "参数值无效：{param}={value}" |
| 路径不存在 | `ERR_PATH_NOT_FOUND` | "路径不存在：{path}" |
| 前置条件不满足 | `ERR_PRECONDITION` | "前置条件不满足：{condition}" |
| Gate 阻断 | `ERR_GATE_BLOCKED` | "Gate 检查未通过，无法继续" |

### 6.2 错误恢复指引

每个错误必须提供：
1. 具体的错误原因
2. 可执行的修复建议
3. 相关的帮助文档链接（如有）

---

## 7. 命令间协作

### 7.1 命令链示例

```
# 新功能开发流程
/new-feature user-auth
  ↓
/check-gate docs/user-auth --phase=1
  ↓
/approve-gate docs/user-auth --phase=1 --role=PM
  ↓
/next-phase docs/user-auth
  ↓
... (重复 check-gate → approve-gate → next-phase)
```

### 7.2 命令依赖关系

```
/next-phase
  ├── 依赖 /check-gate（必须先执行）
  └── 依赖 /approve-gate（审批完成）

/approve-gate
  └── 依赖 /check-gate（质量检查通过）
```

---

## 8. 安全考虑

### 8.1 危险操作标识

危险命令必须：
- 在命令名称中体现（如 `/force-xxx`、`/delete-xxx`）
- 在执行前显示确认提示
- 记录操作日志

### 8.2 权限控制

| 命令类型 | 权限要求 |
|----------|----------|
| 查询类 | 无限制 |
| 修改类 | 当前阶段负责人 |
| 审批类 | 指定角色 |
| 危险类 | 需要二次确认 |

---

## 9. Claude Code 使用指南

### 9.1 生成命令时的检查清单

- [ ] 命令名称是否使用 kebab-case
- [ ] 必填参数是否用 `<>` 标记
- [ ] 可选参数是否用 `[]` 或 `--` 标记
- [ ] 是否定义了前置条件
- [ ] 是否定义了输出格式
- [ ] 是否定义了错误处理

### 9.2 执行命令时的检查清单

- [ ] 参数是否完整
- [ ] 路径是否正确
- [ ] 前置条件是否满足
- [ ] 是否在正确的工作目录

---

## 附录：命令速查表

```
# 功能生命周期
/new-feature <name>                          # 创建功能
/check-gate <path> [--phase=N]               # 检查 Gate
/approve-gate <path> --role=ROLE [--phase=N] # 审批 Gate
/next-phase <path>                           # 下一阶段

# 评审
/expert-review <path> [--phase=N]            # 专家评审

# 恢复
/iresume <path>                              # 恢复工作
```

---

## 模板使用说明

1. 复制此文件到 `docs/_foundation/_api_system/01_COMMAND_CONVENTIONS.md`
2. 替换 `{timestamp}` 为当前日期
3. 根据项目实际情况调整命令列表
4. 删除此"模板使用说明"段落
