# /integrate-project - 整合现有项目到 AI 协作框架

你是一个 AI 协作开发助手。用户请求将一个现有项目整合到 AI 协作框架中，建立单一信息来源（SSoT）。

## 参数

- `$ARGUMENTS`：项目路径和选项
  - `--level=N`：整合级别（0-3，默认 1）
  - `--manual`：手动模式，只生成骨架不自动填充
  - `--name=NAME`：指定功能模块名称（默认使用项目名）

## 用法

```
/integrate-project ./my-project
/integrate-project ./my-project --level=0
/integrate-project ./my-project --level=1 --name=legacy-dashboard
/integrate-project ./my-project --manual
```

## 整合级别说明

| 级别 | 名称 | 产出物 | 耗时 |
|------|------|--------|------|
| Level 0 | 最小登记 | 10_CONTEXT.md（极简） | 1-2h |
| Level 1 | AI 可协作 | + 模块划分 + 技术栈 | 0.5-1d |
| Level 2 | 深度协作 | + API 文档 + 数据模型 | 1-3d |
| Level 3 | 完全规范 | 全套 Foundation | 按需 |

## 执行步骤

### 1. 解析参数

```
解析 $ARGUMENTS：
  project_path = 第一个非选项参数
  level = --level 值（默认 1）
  manual = --manual 是否存在
  name = --name 值（默认从 package.json 提取）

验证：
  如果 project_path 为空 → 提示用法
  如果 project_path 不存在 → 报错
  如果 level 不在 0-3 → 报错
```

### 2. 执行项目扫描

```
如果没有现有扫描结果：
  自动执行 /scan-project {project_path}
  获取：tech_stack, modules, existing_docs

显示扫描摘要：
  📊 项目扫描完成
  技术栈：{framework} + {language}
  模块数：{module_count}
  现有文档：{doc_coverage}%
```

### 3. 创建功能目录

```
在当前工作目录的 docs/ 下创建：

docs/{feature-name}/
├── 10_CONTEXT.md              # 功能上下文
├── 90_PROGRESS_LOG.yaml       # 进度日志
├── PHASE_GATE.yaml            # Gate 规则配置
├── PHASE_GATE_STATUS.yaml     # Gate 运行状态（带追溯标记）
└── _foundation/               # Foundation 文档（Level 1+）
    └── .gitkeep
```

### 4. 生成 10_CONTEXT.md

根据整合级别生成不同详细程度的 Context：

#### Level 0（极简版）

```markdown
# 10_CONTEXT.md
# {project_name} - 项目上下文

> 版本：v0.1
> 最后更新：{current_date}
> 状态：Legacy
> 整合级别：Level 0
> 来源：现有项目整合

---

## 项目概述

**名称**：{project_name}
**路径**：{project_path}
**技术栈**：{framework} + {language}
**状态**：[legacy] 已存在项目

## 简要描述

{从 package.json description 或 README 提取，标记 [逆向]}

## 整合说明

本项目通过 Level 0 整合纳入 AI 协作框架管理。
- 历史功能保持 [legacy] 标记
- 新功能按 Phase 1-7 流程开发

---

_整合时间：{datetime}_
_整合方式：/integrate-project --level=0_
```

#### Level 1（基础版）

```markdown
# 10_CONTEXT.md
# {project_name} - 项目上下文

> 版本：v0.1
> 最后更新：{current_date}
> 状态：Legacy
> 整合级别：Level 1
> 来源：现有项目整合

---

## 1. 项目概述

### 1.1 基本信息

| 字段 | 值 |
|------|-----|
| 名称 | {project_name} |
| 版本 | {version} |
| 路径 | {project_path} |
| 技术栈 | {framework} + {language} |
| 整合状态 | [legacy] |

### 1.2 项目描述

{从 README 提取或 [待补充]}

---

## 2. 技术栈 [逆向]

| 类别 | 技术 | 版本 |
|------|------|------|
| 框架 | {framework} | {version} |
| 语言 | {language} | - |
| 构建 | {build_tool} | {version} |
| 测试 | {test_framework} | {version} |
{如果有 ORM}
| ORM | {orm} | {version} |
{如果有 DB}
| 数据库 | {database} | - |

---

## 3. 模块划分 [逆向]

{从目录结构推断的模块列表}

| 模块 | 路径 | 说明 |
|------|------|------|
{列出主要模块}

---

## 4. 历史功能说明

本项目的历史功能保持 [legacy] 标记，不强制补齐文档。

### 对历史功能的态度

```
能用就用 → 不改动正常运行的功能
能改就改 → 有机会时渐进式规范化
新的按新规范 → 新功能严格走 Phase 1-7
```

---

## 5. 相关文档

- 进度日志：`90_PROGRESS_LOG.yaml`
- Foundation：`_foundation/`（待补充）

---

## CHANGELOG

| 版本 | 日期 | 变更 |
|------|------|------|
| v0.1 | {date} | 项目整合，Level 1 |
```

### 5. 生成 PHASE_GATE_STATUS.yaml（带追溯标记）

```yaml
# PHASE_GATE_STATUS.yaml
# Phase Gate 运行态文件 - 现有项目整合
# 功能模块：{feature-name}

meta:
  feature: "{feature-name}"
  integration_type: "legacy"
  integration_level: {level}
  integrated_at: "{datetime}"
  last_updated: "{datetime}"

# Phase 1: Kickoff - 追溯标记为已完成
phase_1_kickoff:
  gate_state: passed
  gate_state_meta:
    retroactive: true
    retroactive_at: "{datetime}"
    retroactive_reason: "现有项目整合，Phase 1 视为已完成"

# Phase 2-7: 根据整合级别设置
{Level 0/1: 其他 Phase 保持 pending}
{Level 2+: 可能有更多追溯标记}
```

### 6. 生成 _foundation 文档（Level 1+）

```
如果 level >= 1：
  创建 _foundation/ 目录

  生成 05_TECH_DECISIONS.md：
    # 技术决策记录 [逆向]

    ## 技术栈选择
    {从 package.json 提取的技术栈信息}

    ## 依赖说明
    {主要依赖及版本}

如果 level >= 2：
  提示执行：
    /reverse-api {project_path}
    /reverse-schema {project_path}
```

### 7. 生成 90_PROGRESS_LOG.yaml

```yaml
# 90_PROGRESS_LOG.yaml
# 功能模块：{feature-name}（现有项目整合）
# 最后更新：{datetime}

meta:
  feature: "{feature-name}"
  feature_name: "{Project Name}"
  current_phase: 1
  status: integrated
  integration_type: legacy
  integration_level: {level}
  integrated_at: "{datetime}"
  original_project_path: "{project_path}"
  last_updated: "{datetime}"

# ============================================================
# 整合记录
# ============================================================
integration:
  level: {level}
  completed_at: "{datetime}"
  scan_result:
    tech_stack: "{framework} + {language}"
    modules_count: {N}
    doc_coverage: "{score}%"

# ============================================================
# Phase 1: Kickoff - 追溯完成
# ============================================================
phase_1_kickoff:
  status: done
  retroactive: true
  tasks:
    - id: INT-001
      task: "执行项目扫描"
      status: done
      completed_at: "{datetime}"
    - id: INT-002
      task: "生成 10_CONTEXT.md"
      status: done
      completed_at: "{datetime}"
    - id: INT-003
      task: "配置 Phase Gate"
      status: done
      completed_at: "{datetime}"

# ============================================================
# 后续阶段 - 按需进行
# ============================================================
phase_2_spec:
  status: pending
  tasks: []

# ============================================================
# 断点恢复信息
# ============================================================
cc_checkpoint:
  session_id: "integrate-{date}-{feature}"
  last_action: "项目整合完成，Level {level}"
  next_step: "可使用 /new-feature 创建新功能，或补充 Foundation 文档"
  context_files:
    - "docs/{feature}/10_CONTEXT.md"
    - "{project_path}/package.json"
```

### 8. 输出整合结果

```
✅ 项目整合完成！

项目：{project_name}
路径：{project_path}
级别：Level {level}
耗时：{duration}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 生成的文件：
docs/{feature-name}/
├── 10_CONTEXT.md              ✅ 已生成
├── 90_PROGRESS_LOG.yaml       ✅ 已生成
├── PHASE_GATE.yaml            ✅ 已生成
├── PHASE_GATE_STATUS.yaml     ✅ 已生成（含追溯标记）
└── _foundation/               ✅ 已创建
    └── 05_TECH_DECISIONS.md   ✅ 已生成 [逆向]

📊 整合统计：
  技术栈：{framework} + {language}
  模块数：{module_count}
  标记：[legacy] + [逆向]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 整合后的项目状态：

  历史功能：保持 [legacy] 标记，能用就用
  新功能：可使用 /new-feature 创建，走完整流程
  Gate 状态：Phase 1 已追溯通过

📝 下一步操作：

{如果 level == 0}
  • 项目已纳入管理，无需更多操作
  • 如需开发新功能：/new-feature {feature-name}/new-xxx

{如果 level == 1}
  • 建议补充 10_CONTEXT.md 中的项目描述
  • 可选：补充 _foundation/ 下的文档
  • 开发新功能：/new-feature {feature-name}/new-xxx

{如果 level >= 2}
  • 执行 /reverse-api {project_path} 生成 API 文档
  • 执行 /reverse-schema {project_path} 生成数据模型
  • 人工验证并标记 [已验证]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Level 2+ 的额外步骤

```
如果 level >= 2 且不是 --manual：

  询问用户：
  是否现在执行 API 逆向？(y/n)

  如果 y：
    执行 /reverse-api {project_path}

  询问用户：
  是否现在执行数据模型逆向？(y/n)

  如果 y：
    执行 /reverse-schema {project_path}
```

## 错误处理

```
如果扫描失败：
  ⚠️ 项目扫描失败

  可能原因：
  1. 项目结构不标准
  2. 缺少 package.json
  3. 不支持的技术栈

  建议：
  使用 --manual 模式手动整合：
  /integrate-project {path} --level=0 --manual

如果目录已存在：
  ⚠️ 功能目录已存在：docs/{feature-name}/

  选项：
  1. 使用不同名称：/integrate-project {path} --name=new-name
  2. 删除现有目录后重试
  3. 手动合并内容
```

## 注意事项

1. **不修改源项目**：整合过程只在 docs/ 下生成文件，不修改原项目
2. **追溯标记**：所有整合的项目 Phase 1 自动标记为追溯通过
3. **[legacy] 标记**：历史功能不强制规范化，保持灵活性
4. **[逆向] 标记**：自动生成的内容标记为逆向，需人工验证

## 关联命令

- `/scan-project` - 项目扫描（整合前自动调用）
- `/reverse-api` - API 逆向生成
- `/reverse-schema` - 数据模型逆向
- `/new-feature` - 在整合后创建新功能
- `/check-gate` - 检查 Gate 状态
