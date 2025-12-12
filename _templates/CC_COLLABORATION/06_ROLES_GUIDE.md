# 六大岗位内容评审文档

> 本文档包含六大岗位的**工作范围、能力模型、核心技能**详细内容，供评审使用。评审通过后将更新到各角色页面。

---

## 📋 目录

1. [AI 产品工程师 (AI PE)](#1-ai-产品工程师-ai-pe)
2. [系统架构师](#2-系统架构师)
3. [UI 规则设计师](#3-ui-规则设计师)
4. [后端工程师](#4-后端工程师)
5. [AI QA](#5-ai-qa)
6. [项目经理 / Producer](#6-项目经理--producer)

---

## 1. AI 产品工程师 (AI PE)

### 📋 Tab 1: 工作范围与职责边界

#### 核心定位
把需求/UI 转化为结构化 Spec，生成 Demo，调试 AI 输出。不是前端，也不是 PM，是"需求工程化"的负责人。

#### 主要工作内容
- **编写结构化 Spec：** 将自然语言需求或 Figma 设计转化为 AI 可执行的结构化规格说明
- **生成和调试 Demo：** 使用 Claude Code / Cursor 等工具生成前端 Demo，并进行调试
- **定义系统规则：** 明确变量、状态、输入输出、API 行为、错误处理
- **模块级 Owner：** 对一个业务模块的全链路负责（UI → Spec → Demo → 测试）
- **协作桥梁：** 连接架构师、UI 设计师、后端工程师和 QA

#### 工作产出物
- 结构化 Spec 文档（YAML/JSON/Markdown 格式）
- 可运行的前端 Demo
- 模块级 API 需求说明
- 测试场景和边界条件定义

#### 与其他角色的区别

| 角色 | 关注点 | 产出物 |
|------|--------|--------|
| 传统 PM | 需求、流程、商业价值 | PRD（自然语言）|
| 传统前端 | 代码实现、性能优化 | 可运行的代码 |
| **AI PE** | **规则、结构、AI 可理解性** | **Spec + Demo** |

#### 职责边界
✅ **负责**：
- Spec 编写
- Demo 生成与调试
- 前端逻辑定义
- API 需求定义
- 测试场景定义

❌ **不负责**：
- 商业决策（PM 负责）
- 设计规范（UI 设计师负责）
- API 实现（后端负责）
- Production 代码（可能需要前端优化）

---

### 💪 Tab 2: 能力模型

#### 五大核心能力

**1️⃣ 结构化思维**
- 能够将模糊的需求拆解为清晰的变量、状态、流程
- 像写代码一样写需求
- 逻辑清晰，善于抽象
- 能识别边界条件和异常情况
- 理解状态机和数据流

**2️⃣ Spec 撰写能力**
- 熟练使用 Spec Schema，能快速产出高质量的结构化规格说明
- 掌握 Spec 的 12 大要素
- 能从 Figma 提取 UI 结构
- 能从需求推导业务规则

**3️⃣ AI 协作能力**
- 面向 AI 沟通，而不是面向人类
- 理解 AI 的优势和局限
- 会写有效的 Prompt
- 能调试 AI 生成的代码
- 理解 AI 的边界

**4️⃣ 技术理解力**
- 不需要写代码，但要能读懂代码、理解架构、看懂错误
- 理解前端基础（组件、状态、路由）
- 理解 API 基础（REST、错误码）
- 能读懂常见错误信息

**5️⃣ 产品思维**
- 理解用户需求、业务流程、产品逻辑
- 理解用户旅程
- 识别核心场景
- 考虑边界情况

#### 理想背景
适合转型为 AI PE 的人：
- 懂产品的技术型人才（前端转型）
- 懂技术的产品人才（PM 转型）
- 有结构化思维的 UI 设计师
- 理解业务的测试工程师

---

### 🎯 Tab 3: 核心技能详解

#### 1. Spec 的六大要素
每个 AI PE 都必须掌握的结构化思维框架：

1. **Variables（变量）** - 数据的定义和类型
2. **States（状态）** - 系统的所有可能状态
3. **I/O（输入输出）** - 用户操作和系统响应
4. **Modules（模块）** - 功能的拆分和组合
5. **API（接口）** - 前后端交互定义
6. **Errors（错误处理）** - 异常和边界条件

#### 2. 从 PRD 到 Spec 的转化能力
**传统 PRD 写法（❌）：**
```
"用户可以创建产品，需要填写产品名称、价格、库存等信息。
如果信息不完整，提示用户补充。"
```

**结构化 Spec 写法（✅）：**
```yaml
fields:
  - key: productName
    label: "产品名称"
    type: text
    required: true
    validation:
      minLength: 2
      maxLength: 50
  - key: price
    label: "价格"
    type: number
    required: true
    validation:
      min: 0.01
      max: 999999.99

states:
  - idle: 表单初始状态
  - validating: 正在验证
  - submitting: 正在提交
  - success: 提交成功
  - error: 提交失败

errors:
  - code: PRODUCT_NAME_REQUIRED
    message: "请输入产品名称"
  - code: PRICE_INVALID
    message: "价格必须大于 0"
```

#### 3. 从 Figma 到 Spec 的提取能力
AI PE 需要能够：
- 识别 Figma 中的组件层级
- 提取 UI 元素的属性（文本、颜色、尺寸）
- 理解交互状态（hover、active、disabled）
- 识别响应式布局规则

#### 4. Prompt 工程技能
- 编写清晰、明确的 Prompt
- 理解 Prompt 的结构（Context + Task + Format）
- 知道何时需要分步骤 Prompt
- 掌握 Few-shot Learning 技巧

#### 5. Demo 调试技能
- 阅读和理解 AI 生成的代码
- 识别常见错误（语法错误、逻辑错误、边界条件）
- 使用浏览器开发者工具
- 理解控制台错误信息

#### 6. 协作沟通技能
- 与 PM 沟通：理解需求，澄清边界条件
- 与 UI 设计师沟通：理解设计意图，提取规则
- 与后端沟通：定义 API 接口，明确数据格式
- 与 QA 沟通：定义测试场景，提供边界条件

---

## 2. 系统架构师

### 📋 Tab 1: 工作范围与职责边界

#### 核心定位
制定公司级和项目级规范，包括 API 框架、Spec Schema、组件规则、AI 使用规范等，为团队铺设"开发高速公路"。

#### AI 时代架构师的职责变化

**传统架构师关注：**
- 技术选型（Java/Go/Node/Vue/React）
- 部署、集群、数据库、缓存
- 模块划分、性能、稳定性
- 代码规范与 review

**AI 时代新增职责：**
- **制定"团队开发语言"：** Spec Schema + API 规则 + 组件规范 + AI 使用规范
- **建立开发宪法：** 项目级别的 Development Constitution
- **Kickoff 包准备：** 每个新项目的 6 件套规范文档
- **AI 使用规范：** Prompt 模板、代码结构、禁止项清单

#### 三层规范体系

**第一层：公司级基础规范（长期不变）**
- API 行为框架（响应格式、状态码、错误码）
- 认证与权限框架（JWT/OAuth/RBAC）
- 领域建模基础原则
- 日志 & 监控规范
- 错误处理统一规则

**第二层：项目级专属规范**
- 本项目模块划分 & 边界
- API 命名空间 & URL 约定
- 项目专用错误码扩展
- 数据一致性 / 事务策略
- 性能 & 分页约束
- 安全约束

**第三层：AI 使用级规范**
- 标准 Spec Schema（80% Schema）
- 标准 Prompt 模板
- 代码风格 & 目录结构规范
- AI 生成代码的"禁止事项列表"
- 默认 Mock 行为规范

#### 工作产出物
- Kickoff 6 件套文档
- API 行为规范文档
- Spec Schema 定义
- 项目技术蓝图
- AI 使用规范文档

---

### 💪 Tab 2: 能力模型

#### 五大核心能力

**1️⃣ 系统思维与抽象能力**
- 能够从全局视角设计规范体系，提炼通用规则
- 识别共性和特性
- 设计分层架构
- 平衡灵活性和一致性

**2️⃣ API 设计能力**
- 制定清晰、一致、可扩展的 API 规范
- RESTful 设计最佳实践
- 错误处理和状态码规范
- 版本管理和向后兼容

**3️⃣ 规范制定与推广能力**
- 不仅要定义规范，还要让团队理解和执行
- 文档编写能力
- 培训和辅导能力
- 持续优化和迭代

**4️⃣ AI 时代的新技能**
- 理解 AI 工具的特点，为 AI 设计规范
- 理解 AI 的能力边界
- 设计 AI 可理解的规范格式
- 制定 Prompt 工程标准

**5️⃣ 跨角色协作能力**
- 连接 AI PE、后端、前端、QA 等多个角色
- 理解各角色的需求
- 协调不同视角
- 推动规范落地

---

### 🎯 Tab 3: 核心技能详解

#### 1. Kickoff 6 件套制作能力
每个新项目开始前，架构师必须准备的 6 份文档：

1. **项目技术蓝图：** 架构图、技术栈、模块划分
2. **API 行为规范：** 错误码表、前端处理建议、认证行为
3. **领域模型与资源命名：** 核心实体、关系、URL 规则
4. **前端项目结构：** 目录结构、组件标准、UI tokens
5. **Spec Schema & 示例：** 80% Schema 文档 + 完美示例
6. **AI 使用规范：** Prompt 模板、代码约束、Debug 工作流

#### 2. API 行为框架设计
统一整个系统的 API 行为：

**响应格式规范：**
```json
{
  "data": { /* 成功时的数据 */ },
  "error": { /* 失败时的错误信息 */ },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "requestId": "uuid"
  }
}
```

**统一错误格式：**
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "用户友好的错误信息",
    "details": {
      "field": "具体字段错误"
    }
  }
}
```

#### 3. Spec Schema 标准制定
定义 80% Schema 的具体结构，让 AI PE 有清晰的模板可遵循。

#### 4. 规范文档编写技能
- 清晰的结构
- 丰富的示例
- 明确的约束
- 易于理解的语言

#### 5. 技术选型与评估
- 评估新技术的成熟度
- 考虑团队技能匹配
- 权衡成本和收益
- 制定技术升级路径

#### 6. 架构 Review 能力
- Review Spec 是否符合规范
- Review API 设计是否合理
- Review 代码结构是否清晰
- 发现潜在的架构问题

---

## 3. UI 规则设计师

### 📋 Tab 1: 工作范围与职责边界

#### 核心定位
Design System Owner - 防止 UI 发散。制定和维护设计系统，确保整个产品的视觉和交互一致性。

#### AI 时代 UI 设计师的职责变化

**传统 UI 设计师关注：**
- 画 Figma 原型
- 定义视觉风格
- 输出设计稿
- 标注切图

**AI 时代新增职责：**
- **制定 6 层 UI 规则体系：** Design Tokens → 组件库 → 页面模板 → 交互规则 → 响应式规则 → AI Prompt 规则
- **建立 Design System：** 可被 AI 理解和执行的设计系统
- **编写结构化 UI 规则：** 将设计决策转化为 AI 可执行的规则
- **UI 规则审查：** 确保 AI 生成的 UI 符合设计规范

#### 6 层 UI 规则体系

**第 1 层：Design Tokens（设计原子）**
- 颜色系统（primary、secondary、neutral、semantic colors）
- 字体系统（字号、字重、行高）
- 间距系统（4px、8px、12px、16px、24px、32px、48px、64px）
- 圆角系统（0、2px、4px、8px、16px、9999px）
- 阴影系统（none、sm、md、lg、xl）

**第 2 层：组件库规则**
- 基础组件（Button、Input、Select、Checkbox、Radio）
- 复合组件（Form、Table、Modal、Drawer）
- 每个组件的状态（default、hover、active、disabled、error）
- 每个组件的尺寸（sm、md、lg）
- 每个组件的变体（primary、secondary、outline、ghost、link）

**第 3 层：布局规则**
- 网格系统（12 列 / 24 列）
- 容器宽度（sm: 640px、md: 768px、lg: 1024px、xl: 1280px、2xl: 1536px）
- 内容区域规则
- 侧边栏规则
- 导航栏规则

**第 4 层：交互规则**
- 动画时长（fast: 150ms、base: 300ms、slow: 500ms）
- 动画曲线（ease-in、ease-out、ease-in-out）
- 状态转换规则
- 微交互规则
- 加载状态规则

**第 5 层：响应式规则**
- 断点定义
- 移动端适配规则
- 平板适配规则
- 桌面端布局规则

**第 6 层：AI 生成 UI 规则**
- UI Prompt 模板
- 组件使用禁止项
- 默认行为规范
- 可访问性规则（WCAG 2.1 AA 标准）

#### 主要工作内容
- 制定和维护 Design System
- 编写结构化 UI 规则文档
- 审查 AI 生成的 UI 代码
- 培训团队使用设计系统
- 持续优化设计规范

#### 工作产出物
- Design Tokens 定义文件
- 组件库规则文档
- Figma 组件库
- UI 规则 Prompt 模板
- 设计审查报告

#### 与传统 UI 设计师的区别

| 维度 | 传统 UI 设计师 | AI 时代 UI 规则设计师 |
|------|---------------|---------------------|
| 产出物 | Figma 设计稿 | Design System + 规则文档 |
| 工作方式 | 画图 + 标注 | 制定规则 + 审查 AI 输出 |
| 协作对象 | 前端工程师 | AI PE + AI + 前端工程师 |
| 核心能力 | 视觉设计 | 系统化规则制定 |

---

### 💪 Tab 2: 能力模型

#### 五大核心能力

**1️⃣ 系统化设计能力**
- 能够从全局视角设计 Design System
- 提炼设计原则和规则
- 保持设计一致性
- 平衡灵活性和约束性

**2️⃣ 规则化思维**
- 将设计决策转化为明确的规则
- 定义设计原子和组合方式
- 建立设计决策树
- 识别设计模式

**3️⃣ 视觉设计能力**
- 色彩理论与应用
- 排版与字体设计
- 布局与视觉层级
- 品牌视觉设计

**4️⃣ 交互设计能力**
- 用户体验设计
- 交互模式设计
- 微交互设计
- 可访问性设计（WCAG 标准）

**5️⃣ AI 协作能力**
- 理解 AI 生成 UI 的能力边界
- 编写 AI 可理解的设计规则
- 审查和优化 AI 生成的 UI
- 迭代设计系统以适应 AI

#### 理想背景
- 有设计系统搭建经验的 UI 设计师
- 理解前端技术的设计师
- 有品牌设计经验的设计师
- 关注细节和一致性的设计师

---

### 🎯 Tab 3: 核心技能详解

#### 1. Design Tokens 定义能力
建立可被代码直接使用的设计原子：

**颜色系统示例：**
```json
{
  "color": {
    "primary": {
      "50": "#f0f9ff",
      "500": "#3b82f6",
      "900": "#1e3a8a"
    },
    "semantic": {
      "success": "#10b981",
      "warning": "#f59e0b",
      "error": "#ef4444",
      "info": "#3b82f6"
    }
  }
}
```

**间距系统示例：**
```json
{
  "spacing": {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px",
    "2xl": "48px"
  }
}
```

#### 2. 组件规则编写能力
为每个组件定义清晰的规则：

**Button 组件规则示例：**
```yaml
component: Button
variants:
  - primary: 主要操作，每页最多 1 个
  - secondary: 次要操作
  - outline: 边框按钮
  - ghost: 幽灵按钮（文本 + hover 背景）
  - link: 链接样式

sizes:
  - sm: padding: 8px 16px, fontSize: 14px
  - md: padding: 10px 20px, fontSize: 16px
  - lg: padding: 12px 24px, fontSize: 18px

states:
  - default: 默认状态
  - hover: 鼠标悬停
  - active: 点击激活
  - disabled: 禁用状态
  - loading: 加载状态

rules:
  - 按钮文本使用动词开头（如"创建"、"保存"、"取消"）
  - 破坏性操作使用 error 颜色
  - 主要操作按钮放置在右侧
  - 取消按钮放置在主要按钮左侧
```

#### 3. Figma 到规则的转化能力
- 从 Figma 提取 Design Tokens
- 识别设计模式
- 建立组件库
- 编写设计规则文档

#### 4. 设计审查技能
- 审查 UI 一致性
- 检查设计规范遵循情况
- 识别设计债务
- 提出改进建议

#### 5. 响应式设计规则制定
- 定义断点
- 制定移动端优先策略
- 定义组件响应式行为
- 制定触摸交互规则

#### 6. 可访问性规则制定
- WCAG 2.1 AA 标准
- 颜色对比度要求（至少 4.5:1）
- 键盘导航支持
- 屏幕阅读器支持
- 焦点状态可见性

---

## 4. 后端工程师

### 📋 Tab 1: 工作范围与职责边界

#### 核心定位
Backend Engineer - 业务逻辑 Owner。实现 API、处理业务逻辑、管理数据模型。

#### AI 时代后端工程师的职责变化

**传统后端工程师关注：**
- 编写业务逻辑代码
- 设计数据库 Schema
- 实现 API 接口
- 性能优化
- 部署和运维

**AI 时代新增职责：**
- **基于 Spec 实现 API：** 根据 AI PE 提供的 Spec 快速实现标准化 API
- **遵循架构师规范：** 严格遵循 API 行为框架和项目规范
- **为 AI PE 提供反馈：** 对 Spec 的可行性提供技术反馈
- **使用 AI 加速开发：** 使用 AI 工具生成样板代码、测试用例

#### 主要工作内容
- **API 实现：** 根据 Spec 实现 RESTful API
- **业务逻辑：** 实现核心业务规则和数据处理逻辑
- **数据模型设计：** 设计和维护数据库 Schema
- **性能优化：** 查询优化、缓存策略、并发处理
- **错误处理：** 实现统一的错误处理机制
- **集成第三方服务：** 对接外部 API、支付、消息队列等

#### 工作产出物
- 可运行的 API 服务
- 数据库 Schema 和迁移文件
- API 文档（基于 Spec 生成）
- 单元测试和集成测试
- 性能优化报告

#### 与其他角色的协作

**与 AI PE 协作：**
- 接收：Spec、API 需求定义
- 提供：技术可行性反馈、实现建议
- 输出：符合 Spec 的 API 实现

**与架构师协作：**
- 接收：API 规范、项目规范、技术蓝图
- 提供：技术难点反馈、性能数据
- 遵循：统一的 API 行为框架

**与 QA 协作：**
- 提供：API 文档、测试环境
- 接收：Bug 报告、性能问题
- 修复：错误和性能问题

#### 职责边界
✅ **负责**：
- API 实现
- 业务逻辑
- 数据模型
- 性能优化
- 错误处理

❌ **不负责**：
- Spec 编写（AI PE 负责）
- API 规范制定（架构师负责）
- 前端实现（AI PE 或前端负责）
- 测试用例编写（QA 主导，后端协助）

---

### 💪 Tab 2: 能力模型

#### 五大核心能力

**1️⃣ API 实现能力**
- RESTful API 设计和实现
- HTTP 协议理解
- 请求/响应处理
- 中间件和拦截器
- 路由和控制器设计

**2️⃣ 业务逻辑建模能力**
- 领域驱动设计（DDD）理解
- 业务流程建模
- 复杂业务规则实现
- 事务管理
- 数据一致性保证

**3️⃣ 数据库设计与优化**
- 数据库 Schema 设计
- SQL 查询优化
- 索引设计
- 事务处理
- 数据库迁移管理

**4️⃣ 系统设计能力**
- 缓存策略（Redis、Memcached）
- 消息队列（Kafka、RabbitMQ）
- 微服务架构
- API 网关
- 服务间通信

**5️⃣ AI 协作能力**
- 理解结构化 Spec
- 将 Spec 转化为代码实现
- 使用 AI 工具加速开发
- 为 AI PE 提供技术反馈

#### 技术栈要求（根据项目选择）
- **语言：** Node.js/Python/Java/Go/PHP
- **框架：** Express/NestJS/Django/Spring Boot/Gin
- **数据库：** PostgreSQL/MySQL/MongoDB
- **缓存：** Redis
- **消息队列：** Kafka/RabbitMQ
- **工具：** Docker、Git、Postman

---

### 🎯 Tab 3: 核心技能详解

#### 1. 从 Spec 到 API 实现
根据 AI PE 提供的 Spec，快速实现标准化 API。

**Spec 示例：**
```yaml
endpoint: POST /api/products
description: 创建新产品
request:
  body:
    productName: string (required, 2-50 chars)
    price: number (required, > 0)
    stock: integer (required, >= 0)
response:
  success:
    code: 201
    data:
      productId: string
      productName: string
      price: number
      stock: integer
      createdAt: datetime
  errors:
    - code: PRODUCT_NAME_REQUIRED
      status: 400
    - code: PRICE_INVALID
      status: 400
```

**API 实现思路：**
1. 创建路由：`POST /api/products`
2. 验证请求参数（使用 validation 库）
3. 实现业务逻辑
4. 返回统一格式的响应
5. 处理错误并返回标准错误码

#### 2. 统一错误处理
实现符合架构师规范的错误处理机制：

```javascript
// 错误类定义
class ApiError extends Error {
  constructor(code, message, statusCode = 400) {
    super(message);
    this.code = code;
    this.statusCode = statusCode;
  }
}

// 全局错误处理中间件
app.use((err, req, res, next) => {
  if (err instanceof ApiError) {
    return res.status(err.statusCode).json({
      error: {
        code: err.code,
        message: err.message
      },
      meta: {
        timestamp: new Date().toISOString(),
        requestId: req.id
      }
    });
  }
  // 未知错误
  res.status(500).json({
    error: {
      code: 'INTERNAL_SERVER_ERROR',
      message: '服务器内部错误'
    }
  });
});
```

#### 3. 数据库 Schema 设计
根据业务需求设计清晰、可扩展的数据库结构：

**产品表示例：**
```sql
CREATE TABLE products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_name VARCHAR(50) NOT NULL,
  price DECIMAL(10, 2) NOT NULL CHECK (price > 0),
  stock INTEGER NOT NULL CHECK (stock >= 0),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  deleted_at TIMESTAMP
);

CREATE INDEX idx_products_created_at ON products(created_at);
```

#### 4. API 性能优化
- 数据库查询优化（使用索引、避免 N+1 查询）
- 使用缓存（Redis）减少数据库访问
- 分页查询（避免一次性加载大量数据）
- 异步处理（使用消息队列）
- 接口限流和防抖

#### 5. 单元测试编写
为关键业务逻辑编写测试用例：

```javascript
describe('Product API', () => {
  it('should create product successfully', async () => {
    const response = await request(app)
      .post('/api/products')
      .send({
        productName: 'Test Product',
        price: 99.99,
        stock: 100
      });

    expect(response.status).toBe(201);
    expect(response.body.data).toHaveProperty('productId');
  });

  it('should return error for invalid price', async () => {
    const response = await request(app)
      .post('/api/products')
      .send({
        productName: 'Test Product',
        price: -10,
        stock: 100
      });

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('PRICE_INVALID');
  });
});
```

#### 6. AI 工具使用技巧
- 使用 AI 生成样板代码（CRUD 操作）
- 使用 AI 生成测试用例
- 使用 AI 优化 SQL 查询
- 使用 AI 调试错误
- 但要人工 Review 生成的代码

---

## 5. AI QA

### 📋 Tab 1: 工作范围与职责边界

#### 核心定位
AI 测试工程师 - 自动化测试专家。基于 Rulebook 进行测试，确保产品质量。

#### AI 时代 QA 的职责变化

**传统 QA 关注：**
- 手动执行测试用例
- 记录 Bug
- 回归测试
- 探索性测试

**AI 时代新增职责：**
- **编写 Rulebook：** 将测试场景结构化为 AI 可执行的 Rulebook
- **自动化测试设计：** 设计可被 AI 执行的自动化测试
- **边界条件挖掘：** 系统化地发现边界条件和异常场景
- **使用 AI 工具测试：** 使用 AI 生成测试用例、执行测试、分析结果

#### 主要工作内容
- **编写 Rulebook：** 基于 Spec 编写结构化测试规则
- **测试场景设计：** 设计正常流程、异常流程、边界条件测试
- **自动化测试实现：** 编写或生成自动化测试脚本
- **Bug 跟踪：** 发现、记录、跟踪 Bug 修复
- **回归测试：** 确保修复后没有引入新问题
- **性能测试：** 测试系统性能和负载能力

#### 工作产出物
- Rulebook 文档
- 测试用例集
- 自动化测试脚本
- Bug 报告
- 测试覆盖率报告
- 测试总结报告

#### Rulebook 是什么？
Rulebook 是结构化的测试规则文档，定义了：
- 测试场景（用户故事 + 操作步骤）
- 预期结果（正常情况 + 边界条件 + 异常情况）
- 验证规则（断言条件）
- 测试数据（输入数据 + 预期输出）

**Rulebook vs 传统测试用例：**

| 维度 | 传统测试用例 | Rulebook |
|------|-------------|----------|
| 格式 | 表格、自然语言 | 结构化（YAML/JSON）|
| 执行方式 | 手动执行 | 可被 AI 自动执行 |
| 覆盖率 | 依赖人工经验 | 系统化覆盖边界条件 |
| 可维护性 | 难以维护 | 易于维护和更新 |

#### 与其他角色的协作

**与 AI PE 协作：**
- 接收：Spec、测试场景定义
- 提供：测试反馈、边界条件建议
- 输出：Rulebook、测试报告

**与后端协作：**
- 接收：API 文档、测试环境
- 提供：Bug 报告、性能问题
- 验证：API 行为是否符合 Spec

#### 职责边界
✅ **负责**：
- Rulebook 编写
- 测试场景设计
- 自动化测试实现
- Bug 发现和跟踪
- 测试报告

❌ **不负责**：
- Spec 编写（AI PE 负责）
- Bug 修复（开发负责）
- 产品决策（PM 负责）

---

### 💪 Tab 2: 能力模型

#### 五大核心能力

**1️⃣ 测试思维**
- 理解用户场景和业务流程
- 识别边界条件和异常情况
- 设计测试策略
- 评估测试覆盖率

**2️⃣ Rulebook 编写能力**
- 将测试场景结构化
- 定义清晰的验证规则
- 覆盖正常流程、边界条件、异常情况
- 使用 YAML/JSON 编写 Rulebook

**3️⃣ 自动化测试能力**
- 编写自动化测试脚本
- 使用测试框架（Playwright、Cypress、Jest）
- API 测试（Postman、REST Assured）
- 性能测试（JMeter、k6）

**4️⃣ Bug 分析能力**
- 定位 Bug 根因
- 编写清晰的 Bug 报告
- 重现步骤描述
- 优先级评估

**5️⃣ AI 协作能力**
- 使用 AI 生成测试用例
- 使用 AI 分析测试结果
- 理解 Spec 并转化为 Rulebook
- 使用 AI 工具执行测试

#### 理想背景
- 有自动化测试经验的 QA
- 理解业务和用户场景的测试工程师
- 有编程基础的 QA
- 关注细节和边界条件的人才

---

### 🎯 Tab 3: 核心技能详解

#### 1. Rulebook 编写技能
从 Spec 到 Rulebook 的转化：

**Spec 示例：**
```yaml
endpoint: POST /api/products
request:
  body:
    productName: string (required, 2-50 chars)
    price: number (required, > 0)
    stock: integer (required, >= 0)
```

**Rulebook 示例：**
```yaml
rulebook:
  testCase: 创建产品
  scenarios:
    - name: 正常流程
      steps:
        - action: 发送 POST 请求到 /api/products
          data:
            productName: "测试产品"
            price: 99.99
            stock: 100
      expected:
        status: 201
        body:
          productId: exists
          productName: "测试产品"
          price: 99.99
          stock: 100

    - name: 边界条件 - 产品名称最短长度
      steps:
        - action: 发送 POST 请求
          data:
            productName: "AB"  # 2 个字符（最小值）
            price: 0.01
            stock: 0
      expected:
        status: 201

    - name: 边界条件 - 产品名称过短
      steps:
        - action: 发送 POST 请求
          data:
            productName: "A"  # 1 个字符（不足最小值）
            price: 99.99
            stock: 100
      expected:
        status: 400
        error:
          code: PRODUCT_NAME_TOO_SHORT

    - name: 异常情况 - 价格为负数
      steps:
        - action: 发送 POST 请求
          data:
            productName: "测试产品"
            price: -10
            stock: 100
      expected:
        status: 400
        error:
          code: PRICE_INVALID

    - name: 异常情况 - 缺少必填字段
      steps:
        - action: 发送 POST 请求
          data:
            productName: "测试产品"
            # 缺少 price
            stock: 100
      expected:
        status: 400
        error:
          code: PRICE_REQUIRED
```

#### 2. 边界条件识别
系统化识别边界条件的方法：

**数值边界：**
- 最小值、最小值 -1、最小值 +1
- 最大值、最大值 -1、最大值 +1
- 零值、负值

**字符串边界：**
- 空字符串
- 最小长度、最小长度 -1、最小长度 +1
- 最大长度、最大长度 -1、最大长度 +1
- 特殊字符（emoji、HTML 标签、SQL 注入）

**数组边界：**
- 空数组
- 单元素数组
- 最大长度数组

**状态边界：**
- 初始状态
- 中间状态
- 最终状态
- 错误状态

#### 3. 自动化测试脚本编写
使用 Playwright 进行 UI 自动化测试：

```javascript
import { test, expect } from '@playwright/test';

test('创建产品流程', async ({ page }) => {
  // 1. 访问产品创建页面
  await page.goto('/products/new');

  // 2. 填写表单
  await page.fill('[name="productName"]', '测试产品');
  await page.fill('[name="price"]', '99.99');
  await page.fill('[name="stock"]', '100');

  // 3. 提交表单
  await page.click('button[type="submit"]');

  // 4. 验证结果
  await expect(page.locator('.success-message')).toBeVisible();
  await expect(page.locator('.product-name')).toHaveText('测试产品');
});

test('价格验证 - 负数', async ({ page }) => {
  await page.goto('/products/new');
  await page.fill('[name="productName"]', '测试产品');
  await page.fill('[name="price"]', '-10');
  await page.click('button[type="submit"]');

  // 验证错误提示
  await expect(page.locator('.error-message')).toHaveText('价格必须大于 0');
});
```

#### 4. API 测试技能
使用工具或代码进行 API 测试：

```javascript
describe('Product API Tests', () => {
  it('should create product successfully', async () => {
    const response = await fetch('/api/products', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        productName: '测试产品',
        price: 99.99,
        stock: 100
      })
    });

    expect(response.status).toBe(201);
    const data = await response.json();
    expect(data.data.productId).toBeDefined();
  });
});
```

#### 5. Bug 报告编写
清晰、可重现的 Bug 报告结构：

```markdown
# Bug 标题：创建产品时价格输入负数未报错

## 严重程度：高
## 优先级：P1

## 重现步骤：
1. 访问产品创建页面 /products/new
2. 输入产品名称："测试产品"
3. 输入价格：-10
4. 点击"创建"按钮

## 预期结果：
显示错误提示："价格必须大于 0"

## 实际结果：
产品创建成功，价格显示为 -10

## 环境信息：
- 浏览器：Chrome 120
- 系统：macOS 14.0
- 测试环境：staging

## 截图/录屏：
[附加截图]

## 相关 Spec：
POST /api/products - price 字段要求 > 0
```

#### 6. 测试覆盖率分析
- 功能覆盖率：是否覆盖所有功能点
- 边界条件覆盖率：是否覆盖所有边界条件
- 代码覆盖率：自动化测试的代码覆盖率
- 场景覆盖率：是否覆盖所有用户场景

---

## 6. 项目经理 / Producer

### 📋 Tab 1: 工作范围与职责边界

#### 核心定位
项目 Owner - 节奏与资源管理。全局协调项目进度、模块拆解、依赖管理。

#### AI 时代项目经理的职责变化

**传统项目经理关注：**
- 项目计划
- 进度跟踪
- 资源协调
- 风险管理
- 会议组织

**AI 时代新增职责：**
- **模块级别拆解：** 将项目拆解为独立的、可并行开发的模块
- **模块边界定义：** 明确模块之间的接口和依赖关系
- **角色任务分配：** 为 AI PE、架构师、后端、QA 等分配任务
- **AI 开发节奏管理：** 理解 AI 工具的开发节奏，合理安排时间
- **跨模块协调：** 协调模块间的接口对接和依赖关系

#### 主要工作内容
- **项目拆解：** 将项目拆解为模块 → 页面 → 功能点
- **模块边界定义：** 定义模块的输入、输出、依赖关系
- **任务分配与跟踪：** 为各角色分配任务，跟踪进度
- **依赖管理：** 识别和管理模块间依赖，避免阻塞
- **风险管理：** 识别风险，制定应对方案
- **沟通协调：** 组织会议，协调团队协作

#### 工作产出物
- 项目计划文档
- 模块拆解清单
- 任务分配表
- 依赖关系图
- 进度报告
- 风险管理清单

#### AI 时代的项目管理特点

**传统瀑布式开发：**
```
需求分析 → 设计 → 开发 → 测试 → 上线
（线性，周期长）
```

**AI 时代模块化并行开发：**
```
模块 A: Spec → Demo → API → 测试 ──┐
模块 B: Spec → Demo → API → 测试 ──┼→ 集成 → 上线
模块 C: Spec → Demo → API → 测试 ──┘
（并行，周期短）
```

#### 与其他角色的协作

**与架构师协作：**
- 获取：技术蓝图、模块划分建议
- 讨论：技术可行性、时间评估

**与 AI PE 协作：**
- 分配：模块任务
- 跟踪：Spec 和 Demo 进度
- 协调：模块间依赖

**与后端协作：**
- 协调：API 开发进度
- 跟踪：技术难点

**与 QA 协作：**
- 协调：测试计划
- 跟踪：Bug 修复进度

#### 职责边界
✅ **负责**：
- 项目计划
- 模块拆解
- 任务分配
- 进度跟踪
- 依赖管理
- 风险管理

❌ **不负责**：
- Spec 编写（AI PE 负责）
- 技术方案（架构师负责）
- 代码实现（开发负责）
- 设计决策（UI 设计师负责）

---

### 💪 Tab 2: 能力模型

#### 五大核心能力

**1️⃣ 项目拆解能力**
- 将复杂项目拆解为清晰的模块
- 识别模块边界和依赖关系
- 评估模块复杂度和工作量
- 设计合理的开发顺序

**2️⃣ 资源协调能力**
- 合理分配团队资源
- 平衡各角色工作负载
- 识别资源瓶颈
- 协调跨团队协作

**3️⃣ 进度管理能力**
- 制定合理的项目计划
- 跟踪任务进度
- 识别进度风险
- 调整计划应对变化

**4️⃣ 风险管理能力**
- 识别项目风险（技术风险、进度风险、资源风险）
- 评估风险影响
- 制定应对方案
- 跟踪风险状态

**5️⃣ 沟通协调能力**
- 组织有效的会议
- 促进团队协作
- 解决冲突
- 向上汇报

#### 理想背景
- 有技术背景的项目经理
- 理解 AI 工具开发流程的 PM
- 有模块化开发经验的项目经理
- 善于沟通和协调的管理者

---

### 🎯 Tab 3: 核心技能详解

#### 1. 项目拆解方法论
**三层拆解法：项目 → 模块 → 页面 → 功能点**

**示例：电商项目拆解**

**第一层：模块拆解**
```
电商项目
├── 用户模块（User Module）
├── 商品模块（Product Module）
├── 订单模块（Order Module）
├── 支付模块（Payment Module）
└── 后台管理模块（Admin Module）
```

**第二层：页面拆解（以商品模块为例）**
```
商品模块
├── 商品列表页
├── 商品详情页
├── 商品创建页
└── 商品编辑页
```

**第三层：功能点拆解（以商品列表页为例）**
```
商品列表页
├── 商品列表展示
│   ├── 获取商品列表 API
│   ├── 商品卡片渲染
│   └── 分页功能
├── 搜索功能
│   ├── 搜索框
│   ├── 搜索 API
│   └── 搜索结果展示
├── 筛选功能
│   ├── 分类筛选
│   ├── 价格筛选
│   └── 筛选 API
└── 排序功能
    ├── 价格排序
    ├── 时间排序
    └── 销量排序
```

#### 2. 模块边界定义
为每个模块定义清晰的边界：

**模块边界定义模板：**
```yaml
moduleName: 商品模块
owner: AI PE - 张三
dependencies:
  - 用户模块（获取用户信息）
  - 订单模块（商品库存查询）
inputs:
  - userId: 当前登录用户 ID
  - categoryId: 商品分类 ID（可选）
outputs:
  - 商品列表数据
  - 商品详情数据
apis:
  - GET /api/products - 获取商品列表
  - GET /api/products/:id - 获取商品详情
  - POST /api/products - 创建商品
  - PUT /api/products/:id - 更新商品
  - DELETE /api/products/:id - 删除商品
timeline:
  - Spec 编写：2 天
  - Demo 生成：1 天
  - API 实现：3 天
  - 测试：2 天
  - 总计：8 天
risks:
  - 商品图片上传可能需要额外时间
  - 与订单模块的库存同步逻辑复杂
```

#### 3. 依赖管理技能
识别和管理模块间的依赖关系：

**依赖类型：**
- **数据依赖：** 模块 B 需要模块 A 的数据
- **接口依赖：** 模块 B 需要调用模块 A 的 API
- **顺序依赖：** 模块 B 必须在模块 A 完成后才能开始

**依赖管理策略：**
- 识别关键路径（Critical Path）
- 优先开发被依赖的模块
- 使用 Mock 数据解耦依赖
- 定期检查依赖状态

**依赖关系图示例：**
```
用户模块 ──────┐
              ↓
商品模块 ────→ 订单模块 ────→ 支付模块
              ↑
后台管理模块 ──┘
```

#### 4. 任务分配与跟踪
使用工具（如 Jira、Notion、Trello）进行任务管理：

**任务分配示例：**
```
任务：商品列表页开发
负责人：AI PE - 张三
依赖：用户模块（已完成）
优先级：高
状态：进行中

子任务：
- [ ] Spec 编写（1天，AI PE）
- [ ] Demo 生成（0.5天，AI PE）
- [ ] API 实现（2天，后端 - 李四）
- [ ] 测试用例编写（1天，QA - 王五）
- [ ] 测试执行（1天，QA - 王五）
```

#### 5. 风险识别与管理
常见风险类型和应对策略：

**技术风险：**
- 风险：新技术不成熟，可能遇到未知问题
- 应对：技术预研、制定 Plan B

**进度风险：**
- 风险：某个模块延期，影响整体进度
- 应对：识别关键路径、准备备用资源

**资源风险：**
- 风险：核心人员请假或离职
- 应对：知识共享、交叉培训

**需求风险：**
- 风险：需求变更频繁
- 应对：固定核心需求、灵活调整边缘需求

#### 6. Agile / Scrum 方法应用
结合 AI 时代的开发特点，灵活应用敏捷方法：

**Sprint 规划：**
- Sprint 周期：1-2 周
- 每个 Sprint 完成 1-2 个模块
- 每日站会：同步进度、识别阻塞

**Retrospective（回顾会议）：**
- 哪些做得好？
- 哪些可以改进？
- 下个 Sprint 的改进行动

---

## 📝 评审说明

### 评审要点
1. **内容完整性：** 每个角色的三个 Tab 是否内容完整、逻辑清晰？
2. **角色定位准确性：** 每个角色的定位是否准确，与其他角色的区别是否清晰？
3. **能力模型合理性：** 能力模型是否合理，是否覆盖核心能力？
4. **技能清单实用性：** 核心技能是否实用，示例是否清晰？
5. **语言表达：** 语言是否简洁明了，易于理解？

### 评审后续步骤
1. 根据评审反馈修改内容
2. 更新各角色页面的 HTML 文件
3. 补充工具箱和深入专题内容

---

**文档版本：** V1.0
**创建日期：** 2024-12-03
**待评审**
