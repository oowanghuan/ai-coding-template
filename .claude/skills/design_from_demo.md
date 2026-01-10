# design_from_demo - 从 Demo 反推设计

> 类型：Skill（自动触发）
> 版本：v2.0
> 最后更新：2026-01-09

---

## 何时自动使用

Claude 应该在以下情况**自动应用**这个 skill：

- Demo 评审通过后，需要提炼正式 API 契约时
- 用户说「把 Demo 里的接口整理成正式设计」
- 用户说「从 Mock 反推 API 定义」
- Phase 3 → Phase 4 过渡时，需要将 Demo 成果固化为设计文档

**不适用场景**：
- Demo 还没完成或没通过评审
- 已经有完整的 API 设计文档

---

## 执行方式

### 1. 收集 Demo 产出物

读取 Demo 阶段产生的文件：
- `docs/{feature}/demo/` 下的 UI Demo
- `docs/{feature}/demo/mock/` 下的 Mock API
- `docs/{feature}/30_DEMO_REVIEW.md` 评审记录

### 2. 提取接口定义

从 Mock API 中提取：
- 接口路径
- HTTP 方法
- 请求参数（名称、类型、是否必填）
- 响应结构（字段、类型）
- 错误码定义

### 3. 提取数据模型

从 Mock 数据中推断：
- 实体定义（User, Order 等）
- 字段列表
- 字段类型
- 关联关系

### 4. 生成正式设计文档

输出到：
- `docs/{feature}/20_API_SPEC.md`（如果是 API 项目）
- `docs/{feature}/40_DESIGN_FINAL.md`（技术设计）

### 5. 标注来源

在文档中标注「从 Demo 反推」，便于追溯。

---

## 示例对话

### 示例 1：Demo 评审后提炼设计

**User**: Demo 评审通过了，帮我整理下正式的 API 设计

**Claude**: [自动应用 design_from_demo skill]

好的，我来从 Demo 中提炼正式的 API 设计。

正在读取 Demo 文件...
- `docs/user-auth/demo/mock/auth.json`
- `docs/user-auth/demo/mock/handlers/auth.js`

**提取到的接口**：

| 接口 | 方法 | 路径 |
|------|------|------|
| 用户登录 | POST | /api/auth/login |
| 用户注册 | POST | /api/auth/register |
| 获取当前用户 | GET | /api/auth/me |

**提取到的数据模型**：

```typescript
interface User {
  id: number;
  email: string;
  name: string;
  created_at: string;
}

interface LoginResponse {
  token: string;
  user: User;
}
```

我将这些整理到 `20_API_SPEC.md`，你要先看一下吗？

### 示例 2：只提取部分接口

**User**: 把登录相关的 Mock 整理成正式接口文档

**Claude**: [自动应用 design_from_demo skill]

好的，我只整理登录相关的接口...

[提取 login/register/logout 相关的 Mock]

已生成 API 定义草稿，包含：
1. POST /api/auth/login
2. POST /api/auth/register
3. POST /api/auth/logout

需要我写入 API_SPEC.md 吗？

---

## 输出格式

### API 定义格式

```markdown
## POST /api/auth/login

**描述**：用户登录

**来源**：从 Demo Mock 反推（2026-01-09）

### 请求

```json
{
  "email": "string (required)",
  "password": "string (required)"
}
```

### 响应

**成功 (200)**
```json
{
  "token": "string",
  "user": {
    "id": "number",
    "email": "string",
    "name": "string"
  }
}
```

**失败 (401)**
```json
{
  "code": "INVALID_CREDENTIALS",
  "message": "string"
}
```
```

---

## 注意事项

1. **保持一致**：反推出的字段名应与 Mock 完全一致
2. **标注来源**：明确标注「从 Demo 反推」
3. **人工确认**：反推结果需要人工确认后才能作为正式设计
4. **补充细节**：Mock 可能缺少一些细节（如字段约束），需要补充

---

## 关联工具

- `mock_api_generator` - 生成的 Mock 是此 skill 的输入
- `doc_generator` - 可能调用此 skill 生成文档框架
- `/next-phase` - Phase 3 → Phase 4 时可能触发

---

_CC_COLLABORATION Framework v3.1_
