# 现有项目整合 & 接口契约解析

> 版本：v2.0
> 最后更新：2026-01-03

---

## 背景：AI 编程的两个痛点

### 痛点 1：项目接入 - AI 不知道「我们在什么地基上工作」

当你有一个**已经存在的项目**，想要用 AI 协作开发时：

```
用户：帮我在这个项目上加一个用户导出功能
AI：好的，我来创建 UserExportService...

问题：
- AI 不知道项目用的是 Express 还是 NestJS
- AI 不知道已有的 User 模型长什么样
- AI 不知道项目的目录结构规范
- 每次都要重新解释背景
```

### 痛点 2：字段名猜测 - Mock 切 Real 时页面空白

```typescript
// AI 写的前端代码
const user = await api.getUser(id);
console.log(user.userName);      // undefined!
console.log(user.createdAt);     // undefined!

// 实际后端返回
{
  "username": "zhangsan",        // 是 username 不是 userName
  "created_at": "2026-01-03"     // 是 snake_case 不是 camelCase
}
```

**这个问题在以下场景尤其严重**：
- Mock API 切换到 Real API
- 前后端分离开发
- AI 生成类型定义时

---

## 解决方案：契约式 Skills

### 设计理念

**传统做法（命令式）**：为每种框架写检测规则
```yaml
# 不好的设计 - 每种框架都要写规则
express_patterns:
  - "app.get("
  - "router.post("
fastapi_patterns:
  - "@app.get("
  - "@router.post("
nestjs_patterns:
  - "@Get("
  - "@Controller("
# ... 无限扩展
```

**我们的做法（契约式）**：只定义输出格式，让 Claude 自动识别
```yaml
# 好的设计 - 只定义输出契约
output:
  endpoints:
    - method: string      # GET | POST | ...
      path: string        # /api/users
      handler: string     # 处理函数名
      confidence: number  # 置信度
```

**优势**：
| 对比项 | 命令式 | 契约式 |
|--------|--------|--------|
| 支持新框架 | 需要添加规则 | 自动支持 |
| 代码量 | 1200+ 行 | 500 行 |
| 维护成本 | 高 | 低 |
| 适用范围 | 预定义的框架 | 任意语言/框架 |

---

## Skills 清单

### 项目扫描类

| Skill | 用途 | 输入 | 输出 |
|-------|------|------|------|
| `tech_stack_detector` | 检测技术栈 | 项目路径 | 语言、框架、数据库、版本 |
| `api_scanner` | 扫描 API 端点 | 项目路径 | 端点列表、参数、响应类型 |
| `schema_scanner` | 扫描数据模型 | 项目路径 | 模型、字段、关系、ER 图 |
| `module_scanner` | 扫描模块结构 | 项目路径 | 目录树、模块分类、统计 |

### 接口解析类

| Skill | 用途 | 输入 | 输出 |
|-------|------|------|------|
| `contract_resolver` | 查询字段定义 | 实体名/端点 | 真实字段名、类型、约束 |

---

## contract_resolver 详解

### 问题场景

```
场景 1: 写前端组件
─────────────────
❌ 之前: AI 猜测 { userName: string }
✅ 之后: 先查 contract → { username: string }

场景 2: 写 Mock 数据
─────────────────
❌ 之前: 手写 mock，字段名与后端不一致
✅ 之后: 从 contract 生成，保证一致

场景 3: Mock → Real 切换
─────────────────
❌ 之前: 切换后字段对不上，页面空白
✅ 之后: 验证 mock 与 real 的 contract 一致性
```

### SSoT 查找优先级

按以下顺序查找，找到即返回：

```
1. 项目 Contract 文件（如果有）
   └─ shared/contracts/{entity}.yaml
   └─ contracts/{entity}.json

2. OpenAPI / Swagger
   └─ openapi.yaml / swagger.json

3. API Spec 文档
   └─ docs/{feature}/20_API_SPEC.md
   └─ docs/{feature}/21_UI_FLOW_SPEC.md

4. 后端 Schema 定义（推荐 SSoT）
   └─ Python: app/schemas/{entity}.py (Pydantic)
   └─ TypeScript: src/schemas/{entity}.ts (Zod/io-ts)
   └─ Prisma: prisma/schema.prisma

5. 后端 Model 定义
   └─ Python: app/models/{entity}.py (SQLAlchemy)
   └─ TypeScript: src/models/{entity}.ts (TypeORM)

6. 前端类型定义（最低优先级）
   └─ src/types/{entity}.ts
```

### 使用示例

#### 示例 1: 按实体查询

```yaml
# 输入
input:
  entity: "Agent"
  project_path: "./backend"

# 输出
output:
  success: true
  data:
    source:
      type: "backend_schema"
      file: "app/schemas/agent.py"
      line: 46

    fields:
      - name: "id"
        type: "string"
        format: "uuid"
        required: true

      - name: "agent_type"           # 真实字段名是 snake_case
        type: "string"
        enum: ["assistant", "user_proxy", "group_chat_manager"]
        default: "assistant"

      - name: "system_message"       # 不是 systemMessage
        type: "string"
        nullable: true

      - name: "created_at"           # 不是 createdAt
        type: "datetime"

    formatted:
      typescript: |
        interface Agent {
          id: string;
          agent_type: 'assistant' | 'user_proxy' | 'group_chat_manager';
          system_message?: string | null;
          created_at: string;
        }

    confidence: 0.95
    confidence_reason: "Pydantic schema 类型定义完整"
```

#### 示例 2: 按端点查询

```yaml
# 输入
input:
  endpoint: "GET /api/v1/agents"
  project_path: "./backend"

# 输出
output:
  success: true
  data:
    source:
      type: "api_route"
      file: "app/api/v1/agents.py"

    endpoint:
      method: "GET"
      path: "/api/v1/agents"
      response_body:
        type: "AgentListResponse"
        properties:
          total: { type: "number" }
          page: { type: "number" }
          page_size: { type: "number" }
          items: { type: "array", items: "Agent" }
```

#### 示例 3: Mock 验证

```yaml
# 输入
input:
  mode: "validate_mock"
  mock_file: "src/mocks/agents.json"
  entity: "Agent"
  project_path: "./backend"

# 输出
output:
  success: true
  data:
    validation:
      status: "mismatch"
      issues:
        - field: "agentType"
          expected: "agent_type"
          issue: "命名不一致 (camelCase vs snake_case)"

        - field: "createdAt"
          expected: "created_at"
          issue: "命名不一致"

      suggestion: |
        建议修改 Mock 数据:
        - agentType → agent_type
        - createdAt → created_at
```

### AI 协作规则建议

在 `CLAUDE.md` 中添加以下规则，确保 AI 在编码前查询契约：

```markdown
## 接口编码规则

在编写以下代码时，必须先调用 contract_resolver skill：
- 前端接口调用代码（fetch, axios）
- 前端类型定义（interface, type）
- Mock 数据
- API 响应处理逻辑

示例流程：
1. 用户说「写一个 Agent 列表组件」
2. 先查 contract: entity="Agent"
3. 得到真实字段名: agent_type, created_at, ...
4. 按真实字段名写代码
```

---

## 项目整合指南

### 核心概念

#### 1. 单一信息来源（SSoT）

**目标**：把散落在各处的信息，整理成 AI 能理解的标准格式

| 散落的信息 | 整理后 |
|-----------|--------|
| 数据库里有哪些表？ | → `03_DATA_MODEL.md` |
| 后端有哪些 API？ | → `20_API_SPEC.md` |
| 前端有哪些页面？ | → `21_UI_FLOW_SPEC.md` |
| 项目用了什么技术栈？ | → `10_CONTEXT.md` |

#### 2. 对历史功能的态度

**核心原则**：

```
能用就用 → 不改动正常运行的功能
能改就改 → 有机会时渐进式规范化
新的按新规范 → 新功能严格走 Phase 1-7
```

**不会强迫你**：
- ❌ 补齐所有历史文档
- ❌ 重构所有旧代码
- ❌ 为旧功能写测试

**但会帮你**：
- ✅ 登记项目基本信息
- ✅ 自动识别技术栈和模块
- ✅ 逆向生成 API/Schema 文档（可选）

---

### 整合级别（Level 0-3）

不同项目需要不同程度的整合：

```
Level 0: 最小登记 ──→ 只是让 AI 知道「有这个项目」
Level 1: AI 可协作 ──→ AI 可以帮你维护和开发（推荐）
Level 2: 深度协作 ──→ AI 完全理解项目结构
Level 3: 完全规范 ──→ 和新项目一样的完整文档
```

#### 快速判断

```
┌─────────────────────────────────────────────────────────┐
│                   你的项目是什么情况？                    │
└─────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
      很少改动         日常维护        核心项目
      偶尔看看         需要AI帮忙      持续开发
           │               │               │
           ▼               ▼               ▼
       Level 0         Level 1         Level 2+
       最小登记        AI可协作        深度协作
```

#### Level 0：最小登记

**产出物**：
```
docs/{project}/
└── 10_CONTEXT.md    # 极简版，只有基本信息
```

**耗时**：5-10 分钟

#### Level 1：AI 可协作（推荐）

**产出物**：
```
docs/{project}/
├── 10_CONTEXT.md              # 包含技术栈和模块划分
├── 90_PROGRESS_LOG.yaml       # 进度日志
├── PHASE_GATE.yaml            # Gate 规则
├── PHASE_GATE_STATUS.yaml     # Gate 状态（Phase 1 追溯通过）
└── _foundation/
    └── 05_TECH_DECISIONS.md   # 技术栈详情 [逆向]
```

**耗时**：30 分钟 - 1 小时

#### Level 2：深度协作

**产出物**：
```
docs/{project}/
├── 10_CONTEXT.md
├── 20_API_SPEC.md             # API 文档 [逆向]
├── 90_PROGRESS_LOG.yaml
├── PHASE_GATE.yaml
├── PHASE_GATE_STATUS.yaml
└── _foundation/
    ├── 03_DATA_MODEL.md       # 数据模型 [逆向]
    └── 05_TECH_DECISIONS.md
```

**耗时**：1-3 天（需人工验证逆向结果）

---

### 命令使用指南

#### 第一步：扫描项目

```bash
/scan-project ./path/to/project
```

**输出示例**：
```
📊 项目扫描报告：my-project

技术栈：Vue 3 + TypeScript + Vite
模块数：5
文档完整度：10%
推荐整合级别：Level 1

下一步：
/integrate-project ./my-project --level=1
```

#### 第二步：执行整合

```bash
# Level 0 整合
/integrate-project ./path/to/project --level=0

# Level 1 整合（推荐）
/integrate-project ./path/to/project --level=1

# Level 2 整合
/integrate-project ./path/to/project --level=2
```

#### 第三步（可选）：逆向生成文档

```bash
# 逆向生成 API 文档
/reverse-api ./path/to/project

# 逆向生成数据模型文档
/reverse-schema ./path/to/project
```

**支持的技术栈**：任意语言/框架（契约式设计，Claude 自动识别）

---

### 标记系统

整合产生的文档会有特殊标记，帮助区分内容来源：

| 标记 | 含义 | 示例 |
|------|------|------|
| `[legacy]` | 历史功能，已存在 | `## 用户管理 [legacy]` |
| `[逆向]` | 从代码自动生成 | `### GET /api/users [逆向]` |
| `[推断]` | AI 根据代码推断 | `page: number [推断]` |
| `[已验证]` | 人工确认正确 | `### 数据模型 [已验证]` |

**验证流程**：
```
[逆向] → 人工检查 → [已验证]
[推断] → 人工确认 → [已验证] 或 修正
```

---

## 置信度说明

所有 skill 输出都包含置信度评分：

```yaml
high (>= 0.8):
  - 有完整的类型注解
  - 有 OpenAPI/Swagger 文档
  - Schema 语法明确（Pydantic, Prisma）

medium (0.5 - 0.8):
  - 能识别基本结构
  - 部分类型信息缺失
  - 无完整类型定义

low (< 0.5):
  - 只能识别基本信息
  - 动态类型或复杂模式
  - 需要人工验证
```

**使用建议**：
- 置信度 >= 0.8：可直接使用
- 置信度 0.5-0.8：建议人工确认
- 置信度 < 0.5：必须人工验证

---

## FAQ

### Q: 我的项目用的框架很小众，能支持吗？

可以。采用契约式设计，Claude 会自动识别框架语法。只要代码结构清晰，就能提取信息。

### Q: contract_resolver 找不到定义怎么办？

会返回错误信息和搜索路径：
```yaml
output:
  success: false
  error: "Cannot find contract for entity 'User'"
  warnings:
    - "Searched: shared/contracts/, app/schemas/, prisma/schema.prisma"
    - "Consider creating a contract file or API spec"
```

建议：在 `docs/{feature}/20_API_SPEC.md` 中手动定义契约。

### Q: 如何让 AI 在编码前自动查询契约？

在 `CLAUDE.md` 中添加规则：
```markdown
## 接口编码规则

在编写前端接口调用代码时，必须先调用 contract_resolver skill 查询真实字段定义。
```

### Q: 逆向生成的文档不准确怎么办？

这是正常的。逆向生成的内容都有 `[逆向]` 或 `[推断]` 标记，需要人工验证后改为 `[已验证]`。

---

## 命令速查表

| 命令 | 用途 | 常用参数 |
|------|------|----------|
| `/scan-project` | 扫描项目 | `./path` |
| `/integrate-project` | 执行整合 | `--level=N`, `--name=NAME` |
| `/reverse-api` | 逆向 API 文档 | `--format=openapi` |
| `/reverse-schema` | 逆向数据模型 | 无需指定 ORM |
| `/sync-docs` | 检查一致性 | `--fix`, `--strict` |

---

## Skills 文件位置

```
.claude/skills/
├── tech_stack_detector.md    # 技术栈检测
├── api_scanner.md            # API 端点扫描
├── schema_scanner.md         # 数据模型扫描
├── module_scanner.md         # 模块结构扫描
└── contract_resolver.md      # 接口契约解析
```

---

## 相关文档

- [AI 工作流总纲](../04_ai_workflow/README.md)
- [Phase Gate 机制](../07_phase_gate/README.md)
- [文档模板](../03_templates/)

---

## CHANGELOG

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v2.0 | 2026-01-03 | 添加 contract_resolver，契约式设计说明 |
| v1.0 | 2026-01-02 | 初始版本 |

---

_Generated by Claude Code | 2026-01-03_
