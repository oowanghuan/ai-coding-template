# 框架核心原则与行为约束

> 版本：v1.0
> 最后更新：2026-01-09
> 适用范围：所有使用 Claude Code 的开发活动

---

## 1. 概述

本文档定义 Claude Code 与人类开发者协作的核心原则，确保：
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

## 4. 错误处理原则

### 4.1 遇到错误时

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

### 4.2 阻塞记录格式

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

## 5. 代码规范

### 5.1 Vue 组件规范

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

### 5.2 命名规范

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

### 5.3 注释规范

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

_框架版本：v1.0 | 最后更新：2026-01-09_
