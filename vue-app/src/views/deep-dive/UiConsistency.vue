<template>
  <div class="ui-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="container">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: '/role/ui-designer' }">UI 规则设计师</el-breadcrumb-item>
          <el-breadcrumb-item>一致性规范</el-breadcrumb-item>
        </el-breadcrumb>
        <h1 class="page-title">🎨 UI 开发的一致性规范</h1>
        <p class="page-subtitle">UI 规则体系与结构化 Prompt 模板</p>
      </div>
    </div>

    <div class="page-content">
      <div class="container">
        <!-- Part 1 -->
        <div class="part-divider">⭐ 第一部分：UI 规则体系</div>

        <!-- UI 规则介绍 -->
        <el-card class="content-card" shadow="never">
          <h2 class="section-title">如何让 UI 设计遵循规则到极高的一致性？</h2>

          <div class="key-insight">
            UI 设计必须高度规则化，否则 AI 生成的 UI 会发散。<br/>
            尤其是 Chat→Demo 模式，越规则 → AI 越稳定。
          </div>

          <el-alert type="warning" :closable="false">
            <template #title>
              <strong>核心理念</strong>
            </template>
            AI 不是"画 UI"，AI 是"复用规则生成 UI"。<br/>
            规则越细，结果越稳定。
          </el-alert>

          <h3 style="margin-top: 24px;">🧱 UI 规则体系 = 6 层规范</h3>
          <p>以下是已经在多家 AI Coding 团队验证过的方案，可以直接落地使用。</p>
        </el-card>

        <!-- 6 层规范 -->
        <el-card class="content-card" shadow="never">
          <div v-for="(layer, index) in ruleLayers" :key="index" class="rule-layer">
            <h3>
              <span class="number-badge">{{ index + 1 }}</span>
              {{ layer.title }}
            </h3>

            <p v-if="layer.intro">{{ layer.intro }}</p>

            <ul v-if="layer.items">
              <li v-for="item in layer.items" :key="item">{{ item }}</li>
            </ul>

            <div v-if="layer.componentSpec" class="component-spec">
              <h4>每个组件必须有：</h4>
              <div class="spec-item" v-for="spec in layer.componentSpec" :key="spec.label">
                <div class="spec-label">{{ spec.label }}</div>
                <div class="spec-value">{{ spec.value }}</div>
              </div>
            </div>

            <el-alert v-if="layer.note" type="info" :closable="false" style="margin-top: 12px;">
              {{ layer.note }}
            </el-alert>

            <div class="benefits-list" v-if="layer.benefits">
              <strong>👉 效果：</strong>
              <ul>
                <li v-for="benefit in layer.benefits" :key="benefit">{{ benefit }}</li>
              </ul>
            </div>

            <div v-if="layer.examples" class="example-box">
              <h5 v-for="example in layer.examples" :key="example.title">
                {{ example.title }}
              </h5>
              <ul v-for="example in layer.examples" :key="example.title + '-items'">
                <li v-for="item in example.items" :key="item">{{ item }}</li>
              </ul>
            </div>
          </div>
        </el-card>

        <!-- 角色定位 -->
        <el-card class="content-card" shadow="never">
          <div class="key-insight">
            你需要的不是 UI 设计师，而是 UI System Architect<br/>
            （角色通常由 AI Product Engineer 承担）
          </div>
        </el-card>

        <!-- Part 2 -->
        <div class="part-divider">⭐ 第二部分：结构化 Prompt 模板</div>

        <!-- Prompt 模板介绍 -->
        <el-card class="content-card" shadow="never">
          <h2 class="section-title">需求拆分 → 写给 AI 的结构化 Prompt 模板</h2>

          <el-alert type="warning" :closable="false">
            <template #title>
              <strong>未来的流程非常简单</strong>
            </template>
            写完下面这个模板 → 粘给 LLM → 直接生成 Demo（Vue/React/Tailwind 均可）
          </el-alert>

          <h3 style="margin-top: 24px;">📄 AI 产品工程师结构化 Prompt 模板（V1）</h3>
          <p>以下模板可以直接复制使用，只需填充具体内容即可。</p>
        </el-card>

        <!-- Prompt 模板各部分 -->
        <el-card class="content-card" shadow="never">
          <div v-for="(section, index) in promptSections" :key="index" class="template-section">
            <h4>🧩 {{ index + 1 }}. {{ section.title }}</h4>
            <p><strong>{{ section.instruction }}</strong></p>
            <div v-if="section.example" class="example-box">
              <strong>示例：</strong><br/>
              <span v-html="section.example"></span>
            </div>

            <div v-if="section.componentSpec" class="component-spec">
              <h4>{{ section.specTitle }}</h4>
              <div class="spec-item" v-for="spec in section.componentSpec" :key="spec.label">
                <div class="spec-label">{{ spec.label }}</div>
                <div class="spec-value">{{ spec.value }}</div>
              </div>
            </div>

            <ul v-if="section.items">
              <li v-for="item in section.items" :key="item">{{ item }}</li>
            </ul>
          </div>
        </el-card>

        <!-- 完整 Prompt 示例 -->
        <el-card class="content-card" shadow="never">
          <h2 class="section-title">⭐ 完整 Prompt 示例（直接复制给 AI 使用）</h2>

          <div class="prompt-template">
            <pre>{{ fullPromptExample }}</pre>
          </div>
        </el-card>

        <!-- 底部导航 -->
        <div class="action-section">
          <el-button @click="router.push('/role/ui-designer')">
            <el-icon class="el-icon--left"><ArrowLeft /></el-icon>
            返回 UI 设计师
          </el-button>
          <el-button type="primary" @click="router.push('/roles-overview')">
            查看角色协作
            <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'

const router = useRouter()

const ruleLayers = ref([
  {
    title: '视觉原子层（Tokens）',
    intro: '全部视觉用「变量」表达：',
    items: [
      'Color Tokens — Primary/Secondary/Success/Warning/Error/Neutral',
      'Spacing Tokens — 4/8/12/16/24/32/48...',
      'Radius Tokens — XS/S/M/L/XL',
      'Shadow Tokens — sm/md/lg/xl',
      'Font Tokens — H1/H2/H3/Body/Caption/Small'
    ],
    note: 'AI 必须统一使用 tokens，而不是写死 CSS 参数。',
    benefits: ['任意界面统一，风格绝不会乱', '全局样式调整只需修改 token 定义', 'AI 生成的代码自动符合设计规范']
  },
  {
    title: '组件库（Component Library）',
    intro: 'AI 应该永远复用你们的组件库，而不是随便写 div：',
    items: [
      'Button（Primary/Secondary/Tertiary/Danger）',
      'Input（with Label / Error / Hint / Icon）',
      'Select / MultiSelect / DatePicker / TimePicker',
      'Card / Panel',
      'Table / Pagination',
      'Drawer / Modal / Dialog',
      'Empty State / Loading State / Error State',
      'Notification / Toast / Alert',
      'Stepper / Tabs / Accordion',
      'Tag / Badge / Chip',
      'Breadcrumb / Menu / Dropdown'
    ],
    componentSpec: [
      { label: '允许的 props', value: '明确哪些属性可以传入' },
      { label: '必须的 props', value: '哪些属性是必填的' },
      { label: '状态定义', value: 'default / hover / focus / disabled / error / loading' },
      { label: 'UI 示例', value: '可以是文字描述，AI 可使用' },
      { label: '最佳实践', value: '推荐的使用场景和方式' },
      { label: '禁止行为', value: 'AI 最容易犯错的地方' }
    ],
    benefits: ['AI 输出全部是同一风格的组件组合，不再乱写 UI', '代码复用率大幅提高', '维护成本降低']
  },
  {
    title: '布局规则（Layout Guideline）',
    intro: '避免 AI 任意排列布局，你需要规则化：',
    items: [
      '主布局方式 — 左右栏/上下栏/最大宽度限制',
      '表单布局 — 单列还是双列，字段对齐方式',
      '间距固定规则 — Section 间距，标题与内容的间距等',
      '页面必备元素 — Page Title + Breadcrumb（可选）',
      '内容区域最大宽度 — 避免超宽屏显示异常',
      '响应式断点 — 移动端/平板/桌面端的适配规则'
    ],
    benefits: ['AI 不会生成奇怪布局，所有页面整齐一致', '用户体验统一，降低学习成本']
  },
  {
    title: '交互统一规范（Interaction Rules）',
    intro: '示例规则：',
    items: [
      '输入错误必须显示红色描述文字',
      '必填项必须带 * 标记',
      '保存类按钮必须右对齐',
      '按钮顺序：Primary → Secondary → Danger',
      'Modal 必须有"取消 / 确定"两按钮',
      '表格操作统一放最右侧"操作栏"',
      '空状态统一使用 Empty 组件，文案格式固定',
      'Loading 状态必须有明确的加载提示',
      '删除操作必须有二次确认',
      '表单提交成功后显示 Toast 提示'
    ],
    benefits: ['交互稳定，用户体验一致', '减少用户困惑和误操作']
  },
  {
    title: '页面模板（Page Template）',
    intro: '强制所有页面都从同样模板生成，例如：',
    examples: [
      {
        title: 'Example: Create Form Template',
        items: ['Page Title', 'Description（可选）', 'Form Container (Field Groups + Validation Messages)', 'Action Buttons (Submit / Cancel)', 'Error Handling', 'Success Toast']
      },
      {
        title: 'Example: List Page Template',
        items: ['Breadcrumb', 'Page Title + Action Button', 'Filters & Search Bar', 'Table (Column Headers + Data Rows + Action Column)', 'Pagination', 'Empty State', 'Error State', 'Loading State']
      }
    ],
    benefits: ['AI 自动生成的页面永远不会乱，因为骨架固定', '开发效率提升，减少重复决策']
  },
  {
    title: '流程模板（Workflow Template）',
    intro: '比如审批流/创建流/多步流程：',
    items: [
      '多步骤流程 — Step1 → Step2 → Step3 的规则',
      '每步的定义 — 输入、输出、验证规则',
      '状态流转 — 草稿/待审批/已通过/已拒绝',
      '操作按钮 — 拒绝/撤回/通过的统一 UI 处理',
      '完成页面 — 成功页 & 返回位置',
      '进度指示 — 当前在哪一步，还有几步'
    ],
    benefits: ['流程 UI 永远一致，不会出现怪异跳转', '用户清楚地知道自己在哪个环节']
  }
])

const promptSections = ref([
  {
    title: '背景 / 目标',
    instruction: '【填写】用一句话描述：这是一个什么功能，解决什么问题。',
    example: '这是一个产品创建页面，允许管理员创建新产品并设置基本信息。'
  },
  {
    title: '用户角色（Roles）',
    instruction: '【填写】明确有哪些用户角色会使用此功能。',
    example: '管理员、普通用户、访客、供应商等。'
  },
  {
    title: '用户流程（User Flow）',
    instruction: '按顺序写：越短越清晰，越适合 AI。',
    example: '1. 用户打开页面<br/>2. 用户填写产品信息<br/>3. 用户点击"保存"按钮<br/>4. 系统验证并保存数据<br/>5. 显示成功提示并返回列表页'
  },
  {
    title: '交互逻辑（Interaction Logic）',
    instruction: '每个动作→对应结果',
    example: '• 用户点击"创建" → 打开表单<br/>• 用户填写信息 → 实时验证<br/>• 用户保存 → 调用 create API → 显示成功 toast → 返回列表页'
  },
  {
    title: '页面结构（Page Structure）',
    instruction: '写清楚有哪些模块',
    example: '• Page Header（标题 + 操作按钮）<br/>• Filters（关键词 + 状态筛选）<br/>• Table（数据展示）<br/>• Pagination（分页）<br/>• Drawer / Modal（详情/编辑）'
  },
  {
    title: '字段与组件（Fields & Components）',
    instruction: '每个字段都写成 AI 最喜欢的格式',
    specTitle: '字段名（field key）示例',
    componentSpec: [
      { label: '类型', value: 'input / select / date / textarea ...' },
      { label: '必填', value: '是 / 否' },
      { label: '校验规则', value: '例如长度 1-50，邮箱格式等' },
      { label: '占位文案', value: 'placeholder 文字' },
      { label: '错误提示', value: '验证失败时的提示文案' },
      { label: '状态', value: 'default / focus / error / disabled' }
    ]
  },
  {
    title: '组件状态（Component States）',
    instruction: '为每个组件列出可用状态',
    example: '<strong>Button 状态：</strong>primary / secondary / danger / loading / disabled / default<br/><strong>Input 状态：</strong>default / focus / error / disabled'
  },
  {
    title: '所有边界条件（Edge Cases）',
    instruction: '越细越好，这是 AI 最容易遗漏的部分',
    items: [
      'API 超时 → 显示"请稍后再试"',
      'API 返回错误码 → 显示对应错误文案',
      '表单有必填项为空 → 不允许提交',
      '网络断开 → 显示网络错误提示',
      '数据加载失败 → 显示重试按钮',
      '用户权限不足 → 显示权限不足提示'
    ]
  },
  {
    title: '错误态（Error States）',
    instruction: '必须明确',
    items: [
      '页面加载失败 → 显示错误组件 + 重试按钮',
      '提交失败 → toast 提示 + 保留原数据',
      '表单验证失败 → 高亮错误字段 + 显示错误信息',
      'API 500错误 → 显示"服务器错误，请稍后再试"'
    ]
  },
  {
    title: '示例数据（Mock Data）',
    instruction: '提供你希望 AI 使用的例子',
    example: `{<br/>
  "product_name": "Lightweight Tom Yum",<br/>
  "price": 129900,<br/>
  "status": "active",<br/>
  "category": "food",<br/>
  "description": "Delicious Thai soup with authentic flavors"<br/>
}`
  },
  {
    title: '输出要求（Output Requirements）',
    instruction: '明确告诉 AI 你期望的输出',
    items: [
      '使用 React + Tailwind / Vue + Element UI',
      '使用你们的组件库',
      '生成可运行的 demo',
      '生成 mock 接口',
      '所有 UI 必须使用 Tokens',
      '所有组件必须来自组件库',
      '代码必须包含注释',
      '遵循项目的目录结构规范'
    ]
  }
])

const fullPromptExample = `/*
 * AI 产品工程师结构化 Prompt 完整示例
 * 复制以下内容，修改具体参数后直接使用
 */

你现在是一个 AI Frontend Engineer + UI System Architect。
请根据下面的结构化规范，为我生成一个完整可运行的 Demo（React + Tailwind）。

【背景/目标】
这是一个产品创建页面，允许管理员创建新产品。

【用户角色】
- 管理员

【用户流程】
1. 管理员进入创建页
2. 填写表单（产品名称、价格、状态）
3. 点击保存
4. 成功后跳回产品列表

【交互逻辑】
主流程：
- 所有必填项为空 → 禁用提交按钮
- 输入不合法 → 显示错误提示
- 保存成功 → toast("创建成功") → navigate('/products')

边界条件：
- API 错误 → toast("创建失败，请重试")
- API 超时 → toast("网络异常，请稍后再试")

【页面结构】
- Page Title: "创建产品"
- Breadcrumb: 首页 / 产品管理 / 创建产品
- Form Container
  - product_name (input)
  - price (input number)
  - status (select)
- Action Buttons: 取消 / 保存

【字段与组件】
product_name:
  类型：input(text)
  必填：是
  校验：1–50 字符
  占位文案：请输入产品名称
  错误提示：产品名称长度应在1-50个字符之间

price:
  类型：input(number)
  必填：是
  校验：大于 0
  占位文案：请输入价格
  错误提示：请输入正确的价格

status:
  类型：select
  必填：是
  选项：
    - active (上架)
    - inactive (下架)
  默认值：active

【组件状态】
Button:
  - primary: 保存按钮
  - secondary: 取消按钮
  - disabled: 表单验证不通过时
  - loading: 提交中

Input:
  - default: 正常状态
  - focus: 聚焦状态
  - error: 验证失败状态
  - disabled: 禁用状态

【边界条件】
- 表单验证失败 → 不允许提交
- API 超时 → toast 提示网络异常
- API 返回 400 → 显示具体错误信息
- API 返回 500 → 显示服务器错误

【错误态】
- 页面加载失败 → 显示错误页面 + 重试按钮
- 提交失败 → toast 提示 + 保留用户输入
- 字段验证失败 → 高亮错误字段 + 显示错误信息

【示例数据】
{
  "product_name": "Thai Noodles",
  "price": 199900,
  "status": "active"
}

【输出要求】
- 使用 React + Tailwind CSS
- 使用组件库（Button, Input, Select, Form, Card）
- 输出完整可运行的 demo（含 mock API 服务）
- UI 风格使用 tokens:
  - color.primary: #667eea
  - color.error: #f56565
  - radius.md: 8px
  - spacing.4: 16px
- 代码包含必要的注释
- 遵循组件化开发规范`
</script>

<style scoped>
.ui-page {
  min-height: 100%;
  background-color: var(--color-bg-page);
}

/* ========== Page Header ========== */
.page-header {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  padding: var(--spacing-xxl) 0 var(--spacing-xl);
}

.page-header :deep(.el-breadcrumb__inner),
.page-header :deep(.el-breadcrumb__separator) {
  color: rgba(255, 255, 255, 0.9);
}

.page-title {
  font-size: 36px;
  font-weight: var(--font-weight-bold);
  margin: var(--spacing-lg) 0 var(--spacing-sm);
  color: white;
}

.page-subtitle {
  font-size: var(--font-size-lg);
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
}

/* ========== Content ========== */
.page-content {
  padding: var(--spacing-xxl) 0;
}

.content-card {
  margin-bottom: var(--spacing-xl);
  border-radius: var(--border-radius-lg);
}

.content-card :deep(.el-card__body) {
  padding: var(--spacing-xl);
}

/* ========== Part Divider ========== */
.part-divider {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: var(--spacing-lg) var(--spacing-xl);
  margin: var(--spacing-xl) 0;
  border-radius: var(--border-radius-lg);
  text-align: center;
  font-size: 24px;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

/* ========== Section Title ========== */
.section-title {
  font-size: 24px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-lg);
  border-left: 4px solid #f093fb;
  padding-left: var(--spacing-md);
}

/* ========== Key Insight ========== */
.key-insight {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  padding: var(--spacing-xl);
  margin: var(--spacing-lg) 0;
  border-radius: var(--border-radius-lg);
  font-size: 18px;
  text-align: center;
  font-weight: 500;
  line-height: 1.8;
}

/* ========== Rule Layer ========== */
.rule-layer {
  background: linear-gradient(135deg, #f5f7fa 0%, #e8edf5 100%);
  border-left: 4px solid #667eea;
  padding: var(--spacing-xl);
  margin: var(--spacing-lg) 0;
  border-radius: var(--border-radius-md);
}

.rule-layer h3 {
  color: #667eea;
  margin: 0 0 var(--spacing-md);
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.number-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #667eea;
  color: white;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  font-weight: bold;
  font-size: 14px;
}

.rule-layer > p {
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-md);
}

.rule-layer ul {
  margin: 0;
  padding-left: var(--spacing-lg);
}

.rule-layer li {
  margin: var(--spacing-xs) 0;
}

/* ========== Component Spec ========== */
.component-spec {
  background: white;
  border: 2px solid #e9ecef;
  padding: var(--spacing-md);
  margin: var(--spacing-md) 0;
  border-radius: var(--border-radius-md);
}

.component-spec h4 {
  margin: 0 0 var(--spacing-sm);
  color: #667eea;
  border-bottom: 2px solid #e9ecef;
  padding-bottom: var(--spacing-sm);
}

.spec-item {
  display: flex;
  padding: var(--spacing-xs) 0;
  border-bottom: 1px solid #f1f3f5;
}

.spec-item:last-child {
  border-bottom: none;
}

.spec-label {
  font-weight: 600;
  color: #495057;
  min-width: 120px;
}

.spec-value {
  color: #6c757d;
}

/* ========== Benefits List ========== */
.benefits-list {
  background: #e7f5ff;
  border-left: 4px solid #1c7ed6;
  padding: var(--spacing-md) var(--spacing-lg);
  margin: var(--spacing-md) 0;
  border-radius: var(--border-radius-md);
}

.benefits-list ul {
  margin: var(--spacing-sm) 0 0;
  padding-left: var(--spacing-lg);
}

.benefits-list li {
  color: #1864ab;
  margin: var(--spacing-xs) 0;
}

/* ========== Example Box ========== */
.example-box {
  background: #f8f9fa;
  border: 2px solid #dee2e6;
  padding: var(--spacing-md);
  margin: var(--spacing-md) 0;
  border-radius: var(--border-radius-md);
}

.example-box h5 {
  margin: 0 0 var(--spacing-sm);
  color: #495057;
}

/* ========== Template Section ========== */
.template-section {
  background: #f8f9fa;
  border-radius: var(--border-radius-md);
  padding: var(--spacing-lg);
  margin: var(--spacing-lg) 0;
}

.template-section h4 {
  margin: 0 0 var(--spacing-md);
  color: #495057;
}

/* ========== Prompt Template ========== */
.prompt-template {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: var(--spacing-lg);
  margin: var(--spacing-lg) 0;
  border-radius: var(--border-radius-md);
  overflow-x: auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.prompt-template pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
}

/* ========== Action Section ========== */
.action-section {
  text-align: center;
  margin-top: var(--spacing-xxl);
  padding: var(--spacing-xl) 0;
  display: flex;
  justify-content: center;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

/* ========== Responsive ========== */
@media (max-width: 768px) {
  .page-title {
    font-size: 24px;
  }

  .part-divider {
    font-size: 18px;
    padding: var(--spacing-md);
  }
}
</style>
