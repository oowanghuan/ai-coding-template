# 00_OVERVIEW.md
# Claude Code 协作规范总则

> 版本：v1.0
> 最后更新：2024-12-09
> 适用范围：所有使用 Claude Code 的开发活动

---

## 1. 概述

本文档定义 Claude Code 与人类开发者协作的核心规范，确保：
- AI 行为可预测、可控制
- 代码质量符合项目标准
- 上下文恢复顺畅
- 协作效率最大化

---

## 2. 核心原则

### 2.1 文档驱动

```
原则：先文档，后代码

1. 开始工作前，先阅读相关设计文档
2. 代码实现必须遵循设计规范
3. 重大决策需要记录在文档中
4. 完成工作后，更新进度文档
```

### 2.2 上下文意识

```
原则：主动维护上下文

1. 每次会话开始，检查 PROGRESS_LOG 中的 cc_checkpoint
2. 长对话中定期更新 checkpoint
3. 会话结束前，确保 checkpoint 信息完整
4. 上下文压缩后，立即执行恢复流程
```

### 2.3 技术栈遵守

```
原则：严格遵守 Project Profile 定义

1. 使用项目指定的技术栈（如 Vue 3 + Element Plus）
2. 遵循项目的 UI System 规范
3. 遵循项目的 API 和 DB 规范
4. 不引入未经批准的新依赖
```

### 2.4 渐进式开发

```
原则：小步快跑，持续验证

1. 大任务拆解为小任务
2. 每完成一个小任务，验证结果
3. 及时更新 PROGRESS_LOG
4. 遇到阻塞立即标记并沟通
```

---

## 3. 行为约束

### 3.1 必须做（MUST）

| 行为 | 说明 |
|------|------|
| 阅读设计文档 | 开始实现前，必须阅读 CONTEXT 和 DESIGN |
| 遵循命名规范 | 变量、函数、文件命名遵循项目规范 |
| 使用项目组件 | UI 组件优先使用 Element Plus |
| 更新进度 | 完成任务后更新 PROGRESS_LOG |
| 写有意义的 commit | 遵循 Conventional Commits 规范 |
| 保持 checkpoint | 会话结束前更新 cc_checkpoint |

### 3.2 禁止做（MUST NOT）

| 行为 | 说明 |
|------|------|
| 跳过设计 | 不能直接写代码而忽略设计文档 |
| 引入新依赖 | 未经批准不能安装新的 npm 包 |
| 删除代码 | 不能删除不理解的代码 |
| 修改规范 | 不能擅自修改 _system 下的规范文件 |
| 忽略错误 | 不能跳过测试失败或构建错误 |
| 硬编码 | 不能硬编码配置值或敏感信息 |

### 3.3 应该做（SHOULD）

| 行为 | 说明 |
|------|------|
| 询问不确定的问题 | 遇到歧义时主动询问 |
| 提供多个方案 | 重大决策时提供选项 |
| 解释思路 | 复杂实现时说明设计思路 |
| 建议优化 | 发现可优化点时提出建议 |
| 保持简洁 | 代码和文档保持简洁清晰 |

---

## 4. 工作流程

### 4.1 会话开始

```markdown
## 会话开始检查清单

1. [ ] 读取 PROGRESS_LOG 中的 cc_checkpoint
2. [ ] 确认上次工作的位置和状态
3. [ ] 读取相关的 CONTEXT 和 DESIGN 文档
4. [ ] 确认当前要执行的任务
5. [ ] 开始工作
```

### 4.2 工作过程中

```markdown
## 工作过程检查清单

1. [ ] 每完成一个任务，更新 PROGRESS_LOG
2. [ ] 每完成一个任务，验证结果
3. [ ] 遇到阻塞时标记并说明
4. [ ] 长对话中定期更新 checkpoint
5. [ ] 重大决策记录在相关文档中
```

### 4.3 会话结束

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

## 5. 上下文恢复

### 5.1 触发条件

上下文恢复在以下情况下触发：

1. **新会话开始** - 每次新对话开始
2. **上下文压缩** - 对话过长被 compact
3. **中断恢复** - 异常中断后继续

### 5.2 恢复流程

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

### 5.3 Checkpoint 格式

```yaml
cc_checkpoint:
  session_id: "cc-2024-12-09-001"           # 会话标识
  last_file_edited: "src/views/Login.vue"   # 最后编辑的文件
  last_action: "完成登录表单验证"            # 最后完成的操作
  next_step: "实现登录 API 调用"             # 下一步任务
  context_files:                             # 需要读取的上下文文件
    - "Docs/feature-name/00_CONTEXT.md"
    - "Docs/feature-name/10_DESIGN_FINAL.md"
    - "Docs/feature-name/20_DEV_PLAN.md"
  blockers: []                               # 当前阻塞项
  notes: "注意登录失败的错误处理"             # 其他备注
```

---

## 6. 进度追踪

### 6.1 PROGRESS_LOG 更新

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

### 6.2 状态定义

| 状态 | 说明 | 使用场景 |
|------|------|----------|
| `pending` | 待开始 | 任务尚未开始 |
| `wip` | 进行中 | 正在执行的任务 |
| `done` | 已完成 | 任务完成且验证通过 |
| `blocked` | 阻塞 | 因依赖或问题无法继续 |

---

## 7. 代码规范

### 7.1 Vue 组件规范

```vue
<!-- 组件结构顺序 -->
<template>
  <!-- 模板内容 -->
</template>

<script setup lang="ts">
// 1. 导入
import { ref, computed } from 'vue'

// 2. Props 和 Emits
const props = defineProps<{}>()
const emit = defineEmits<{}>()

// 3. 响应式数据
const data = ref()

// 4. 计算属性
const computed = computed(() => {})

// 5. 方法
const handleClick = () => {}

// 6. 生命周期
onMounted(() => {})
</script>

<style scoped>
/* 组件样式 */
</style>
```

### 7.2 命名规范

```typescript
// 文件命名
UserList.vue           // 组件：PascalCase
userService.ts         // 服务：camelCase
types.ts               // 类型：camelCase

// 变量命名
const userName = ''          // 变量：camelCase
const MAX_COUNT = 100        // 常量：UPPER_SNAKE_CASE
const handleClick = () => {} // 函数：camelCase + handle 前缀

// CSS 类名
.user-list {}                // kebab-case
.user-list__item {}          // BEM 可选
```

### 7.3 注释规范

```typescript
// 单行注释：解释为什么，而不是是什么
const MAX_RETRY = 3  // 网络不稳定时需要重试

/**
 * 复杂函数使用 JSDoc
 * @param userId - 用户 ID
 * @returns 用户信息
 */
async function getUser(userId: string): Promise<User> {}

// TODO: 待办事项
// FIXME: 需要修复
// NOTE: 重要说明
```

---

## 8. 与人类的协作

### 8.1 沟通原则

```markdown
1. 主动汇报进度
   - 完成任务时告知
   - 遇到问题时说明

2. 清晰表达
   - 说明做了什么
   - 说明为什么这样做
   - 说明下一步是什么

3. 询问不确定的问题
   - 遇到歧义时询问
   - 提供选项让人类决策
   - 解释各选项的利弊
```

### 8.2 决策边界

```markdown
## Claude Code 可自主决策
- 代码实现细节
- 变量命名选择
- 代码格式调整
- 小范围重构

## 需要人类确认
- 架构设计决策
- 新依赖引入
- API 接口设计
- 数据库 Schema
- 删除功能代码
```

---

## 9. 错误处理

### 9.1 遇到错误时

```markdown
1. 记录错误
   - 保存错误信息
   - 记录复现步骤

2. 尝试解决
   - 分析错误原因
   - 尝试修复（最多 3 次）

3. 标记阻塞
   - 如果无法解决，标记为 blocked
   - 在 PROGRESS_LOG 中记录

4. 通知人类
   - 说明错误情况
   - 提供已尝试的方案
   - 请求帮助
```

### 9.2 阻塞记录格式

```yaml
blockers:
  - task_id: TASK-003
    description: "登录 API 返回 CORS 错误"
    error_message: "Access-Control-Allow-Origin..."
    tried_solutions:
      - "添加代理配置"
      - "修改请求头"
    needs_help: true
    created_at: 2024-12-09
```

---

## 10. 快速参考

### 10.1 常用文件路径

```
Docs/_system/
├── 00_PROJECT_CONTEXT.md      # 项目背景
├── 01_PROJECT_PROFILE.yaml    # 项目配置
├── 02_API_CONVENTIONS.md      # API 规范
├── 03_DB_CONVENTIONS.md       # DB 规范
├── CC_COLLABORATION/          # CC 协作规范
└── _ui_system/                # UI 规范

Docs/{feature}/
├── 00_CONTEXT.md              # 功能背景
├── 10_DESIGN_FINAL.md         # 设计文档
├── 20_DEV_PLAN.md             # 开发计划
├── 30_PROGRESS_LOG.yaml       # 进度日志
└── 31_DAILY_SUMMARY/          # 每日总结
```

### 10.2 状态速查

| 任务状态 | 含义 | 下一步 |
|----------|------|--------|
| pending | 待开始 | 开始任务，标记为 wip |
| wip | 进行中 | 完成后标记为 done |
| done | 已完成 | 验证通过，继续下一个 |
| blocked | 阻塞 | 记录原因，寻求帮助 |

### 10.3 Commit 类型

| 类型 | 说明 |
|------|------|
| feat | 新功能 |
| fix | 修复 Bug |
| docs | 文档更新 |
| style | 格式调整 |
| refactor | 重构 |
| test | 测试 |
| chore | 其他 |
