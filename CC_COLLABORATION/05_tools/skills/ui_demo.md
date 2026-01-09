# ui_demo - UI Demo 生成器

> 类型：Skill（自动触发）
> 版本：v2.0
> 最后更新：2026-01-09

---

## 何时自动使用

Claude 应该在以下情况**自动应用**这个 skill：

- 用户说「做个 demo」「生成原型」「搞个可交互的页面看看」
- 在 Phase 3 Demo 阶段，需要快速验证 UI 设计时
- 用户提供了 UI SPEC，要求生成可运行的 Demo
- 用户说「让我看看这个页面长什么样」

**不适用场景**：
- 用户只是讨论设计，没有要求生成代码
- 用户要求的是最终生产代码（应该在 Phase 5）

---

## 执行方式

### 1. 确定 Demo 类型

| 类型 | 适用场景 | 技术栈 |
|------|----------|--------|
| 单页 HTML | 快速验证单个页面 | HTML + CSS + JS |
| React Demo | 需要组件化 | React + Tailwind |
| Vue Demo | Vue 项目 | Vue 3 + Tailwind |

### 2. 读取 UI SPEC（如果存在）

```
UI SPEC 位置: docs/{feature}/21_UI_FLOW_SPEC.md
```

从 SPEC 中提取：
- 页面布局
- 交互元素
- 状态变化
- 数据展示

### 3. 读取 UI System（如果存在）

```
UI System 位置: docs/_foundation/_ui_system/
```

应用项目的：
- 颜色规范
- 字体规范
- 组件样式

### 4. 生成 Demo 代码

生成一个自包含的、可直接运行的 Demo 文件：

```
输出位置: docs/{feature}/demo/
```

### 5. 提供运行说明

告诉用户如何运行 Demo：
- 直接用浏览器打开（HTML）
- 或者启动开发服务器

---

## 示例对话

### 示例 1：快速生成登录页 Demo

**User**: 帮我做个登录页面的 demo

**Claude**: [自动应用 ui_demo skill]

好的，我来生成一个登录页面的 Demo。

请确认几个设计细节：
1. 需要哪些登录方式？（邮箱/手机/第三方）
2. 是否需要「记住我」选项？
3. 有没有特定的设计风格偏好？

**User**: 邮箱登录就行，要记住我，简洁现代风格

**Claude**: 明白，生成中...

我创建了一个单页 HTML Demo：

```
docs/user-auth/demo/login-demo.html
```

你可以直接用浏览器打开这个文件查看效果。

Demo 包含：
- 邮箱输入框
- 密码输入框
- 「记住我」复选框
- 登录按钮
- 忘记密码链接

需要我调整什么吗？

### 示例 2：基于 SPEC 生成 Demo

**User**: 按照 UI SPEC 生成 demo

**Claude**: [自动应用 ui_demo skill]

好的，我先读取 UI SPEC...

找到 `docs/user-auth/21_UI_FLOW_SPEC.md`，包含以下页面：
1. 登录页
2. 注册页
3. 忘记密码页

你想先生成哪个页面的 Demo？还是全部生成？

---

## Demo 输出规范

### 文件结构

```
docs/{feature}/demo/
├── index.html          # 入口页面
├── styles.css          # 样式（如果需要分离）
├── script.js           # 交互逻辑（如果需要分离）
└── README.md           # 运行说明
```

### Demo 要求

1. **自包含**：尽量单文件，方便查看
2. **可运行**：直接打开或简单命令即可运行
3. **Mock 数据**：使用假数据，不依赖后端
4. **交互完整**：关键交互可以演示

---

## 注意事项

1. **Demo 不是生产代码**：Demo 目的是验证设计，不追求代码质量
2. **优先速度**：快速生成，快速验证
3. **标注 Mock**：明确标注哪些是 Mock 数据
4. **保持简单**：不引入复杂依赖

---

## 关联工具

- `/gen-demo` - 调用此 skill 生成 Demo
- `mock_api_generator` - 生成 Demo 所需的 Mock API

---

_CC_COLLABORATION Framework v3.1_
