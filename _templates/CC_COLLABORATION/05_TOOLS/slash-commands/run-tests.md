# /run-tests - 执行测试

你是一个 AI 协作开发助手。用户请求执行功能模块的测试。

## 参数

- `$ARGUMENTS`：功能模块名称（如 `user-auth`、`payment-system`）

## 执行步骤

### 1. 验证参数

如果 `$ARGUMENTS` 为空，请提示用户：
```
请提供功能名称，例如：/run-tests user-auth

或使用 /run-tests --all 执行全部测试
```

### 2. 查找测试文件

查找与功能相关的测试文件：
- `src/**/{feature-name}/**/*.spec.ts`
- `src/**/{feature-name}/**/*.test.ts`
- `tests/{feature-name}/**/*.spec.ts`
- `tests/{feature-name}/**/*.test.ts`

如果没有找到测试文件，提示：
```
⚠️ 未找到 {feature-name} 相关的测试文件

建议在以下位置创建测试：
• src/{feature-name}/__tests__/*.spec.ts
• tests/{feature-name}/*.spec.ts

是否需要生成测试模板？[Y/n]
```

### 3. 执行测试

使用项目配置的测试框架执行测试：

```bash
# Vitest（推荐）
npx vitest run --reporter=verbose src/**/{feature-name}/**

# Jest
npx jest --verbose {feature-name}

# 或自定义命令
npm run test -- --grep "{feature-name}"
```

### 4. 收集测试结果

收集测试输出，包括：
- 通过的测试数量
- 失败的测试数量
- 跳过的测试数量
- 测试覆盖率（如果启用）
- 失败测试的详细信息

### 5. 生成测试报告

创建 `docs/{feature-name}/40_TEST_REPORT.md`：

```markdown
# 40_TEST_REPORT.md
# {Feature Name} - 测试报告

> 生成时间：{current_datetime}
> 测试框架：{test_framework}
> 执行环境：{node_version}

---

## 1. 测试概览

| 指标 | 数值 |
|------|------|
| 总测试数 | {total} |
| 通过 | {passed} |
| 失败 | {failed} |
| 跳过 | {skipped} |
| 通过率 | {pass_rate}% |
| 执行时间 | {duration}s |

---

## 2. 测试覆盖率

| 类型 | 覆盖率 |
|------|--------|
| 语句覆盖 | {statements}% |
| 分支覆盖 | {branches}% |
| 函数覆盖 | {functions}% |
| 行覆盖 | {lines}% |

---

## 3. 测试详情

### 3.1 通过的测试 ✅

{列出所有通过的测试}

### 3.2 失败的测试 ❌

{列出所有失败的测试，包含错误信息}

### 3.3 跳过的测试 ⏭️

{列出所有跳过的测试，包含原因}

---

## 4. 失败分析

### 失败测试 1: {test_name}

**错误类型**: {error_type}
**错误信息**: {error_message}
**位置**: {file_path}:{line_number}

**堆栈跟踪**:
```
{stack_trace}
```

**建议修复**:
- {fix_suggestion}

---

## 5. 改进建议

根据测试结果，建议：
1. {suggestion_1}
2. {suggestion_2}
3. {suggestion_3}

---

_由 /run-tests 自动生成_
```

### 6. 输出结果

```
🧪 测试执行完成 - {feature-name}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 测试结果
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 通过: {passed}
❌ 失败: {failed}
⏭️ 跳过: {skipped}

通过率: {pass_rate}%
执行时间: {duration}s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 覆盖率
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
语句: {statements}% | 分支: {branches}%
函数: {functions}% | 行: {lines}%

{如果有失败的测试，显示失败详情}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ 失败的测试
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. {test_name}
   {error_message}
   at {file_path}:{line_number}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 已生成报告: docs/{feature-name}/40_TEST_REPORT.md

{根据测试结果给出下一步建议}
```

### 7. 更新进度日志

如果测试全部通过，更新 `30_PROGRESS_LOG.yaml`：
- 将 Phase 6 Test 阶段标记为 done
- 更新 `stats.completion_rate`

## 测试模板生成

如果用户确认生成测试模板，创建：

```typescript
// tests/{feature-name}/{feature-name}.spec.ts
import { describe, it, expect, beforeEach } from 'vitest'

describe('{Feature Name}', () => {
  beforeEach(() => {
    // 测试前准备
  })

  describe('基本功能', () => {
    it('应该正确初始化', () => {
      // TODO: 实现测试
      expect(true).toBe(true)
    })

    it('应该处理正常输入', () => {
      // TODO: 实现测试
    })

    it('应该处理边界情况', () => {
      // TODO: 实现测试
    })
  })

  describe('错误处理', () => {
    it('应该处理无效输入', () => {
      // TODO: 实现测试
    })

    it('应该抛出适当的错误', () => {
      // TODO: 实现测试
    })
  })
})
```

## 注意事项

- 默认使用 Vitest，可根据项目配置调整
- 覆盖率需要项目启用覆盖率收集
- 失败的测试会阻止进入 Deploy 阶段
- 测试报告会覆盖已有文件
