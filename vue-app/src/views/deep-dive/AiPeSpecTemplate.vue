<template>
  <div class="template-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="container">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: '/deep-dive/ai-pe' }">AI PE 专题</el-breadcrumb-item>
          <el-breadcrumb-item>模板库</el-breadcrumb-item>
        </el-breadcrumb>
        <h1 class="page-title">📝 AI PE 结构化需求模板库</h1>
        <p class="page-subtitle">可直接复用的 Spec 模板、状态定义模板、API 行为模板等实用工具</p>
      </div>
    </div>

    <div class="page-content">
      <div class="container">
        <!-- 模板简介 -->
        <el-card class="content-card" shadow="never">
          <h2 class="section-title">模板简介</h2>

          <div class="key-insight">
            这是你们团队未来所有需求、UI、Demo、开发前置规范的核心文档格式<br/>
            <strong>PRD 2.0（Structure Spec）</strong>
          </div>

          <div class="intro-box">
            <h3>这个模板能让 AI 自动生成什么？</h3>
            <ul>
              <li>✅ 可运行 Demo</li>
              <li>✅ 完整 UI</li>
              <li>✅ 完整前端代码</li>
              <li>✅ Mock API</li>
              <li>✅ 联调逻辑</li>
              <li>✅ 测试用例（可选）</li>
            </ul>
            <p class="intro-highlight">
              只需要把"自然语言需求"按照这个模板填写 → 直接投喂给 Claude Code / Cursor / GPT
            </p>
          </div>

          <el-alert type="warning" :closable="false">
            <template #title>
              <strong>使用说明</strong>
            </template>
            这是高度标准化的模板，可给 PM/UI/前端/甲方/外包/AI 使用。每个章节都有详细说明和示例。
          </el-alert>
        </el-card>

        <!-- 完整模板 -->
        <el-card class="content-card" shadow="never">
          <h2 class="section-title">完整结构化需求模板（12个章节）</h2>

          <div v-for="(section, index) in templateSections" :key="index" class="template-section">
            <h3>
              <span class="section-number">{{ index }}</span>
              {{ section.title }}
            </h3>
            <p>{{ section.description }}</p>

            <div class="template-code">
              <pre>{{ section.template }}</pre>
            </div>

            <div v-if="section.example" class="example-box">
              <h4>示例</h4>
              <pre>{{ section.example }}</pre>
            </div>

            <el-alert v-if="section.note" type="info" :closable="false" style="margin-top: 12px;">
              {{ section.note }}
            </el-alert>
          </div>
        </el-card>

        <!-- 如何使用 -->
        <el-card class="content-card" shadow="never">
          <h2 class="section-title">如何使用这个模板？</h2>

          <el-row :gutter="20">
            <el-col :xs="24" :sm="12" :md="8" v-for="usage in usageGuide" :key="usage.role">
              <div class="usage-card">
                <h5>{{ usage.icon }} {{ usage.role }}</h5>
                <ul>
                  <li v-for="item in usage.items" :key="item">{{ item }}</li>
                </ul>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <!-- 一句话使用指南 -->
        <el-card class="content-card final-template" shadow="never">
          <h2 class="section-title" style="color: white; border-left-color: rgba(255,255,255,0.5);">
            🎁 一句话使用指南（给 Claude Code）
          </h2>
          <div class="final-code">
            <pre>请根据以下结构化规格，生成完整可运行 Demo
（使用 React/Tailwind/组件库）
并包含所有变量、状态、模块、API 行为及错误态：

&lt;将上面填写好的完整模板贴进去&gt;</pre>
          </div>
        </el-card>

        <!-- 提示 -->
        <el-card class="content-card" shadow="never">
          <div class="key-insight">
            🔥 这是你们团队之后所有需求的核心模板（非常强）
          </div>

          <el-alert type="warning" :closable="false">
            <template #title>
              <strong>提示</strong>
            </template>
            <ul class="tip-list">
              <li>这个模板可以复制到 Notion / Confluence / 飞书文档</li>
              <li>可以制作成 Word/Markdown 模板文件</li>
              <li>建议打印一份贴在办公区</li>
              <li>新人入职时作为必读文档</li>
            </ul>
          </el-alert>
        </el-card>

        <!-- 底部导航 -->
        <div class="action-section">
          <el-button @click="router.push('/deep-dive/ai-pe-examples')">
            <el-icon class="el-icon--left"><ArrowLeft /></el-icon>
            返回实战案例
          </el-button>
          <el-button type="primary" @click="router.push('/deep-dive/ai-pe-training')">
            查看培训指南
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

const templateSections = ref([
  {
    title: '元信息（Meta Information）',
    description: '基本信息，便于项目管理和版本追踪。',
    template: `功能名称：
版本号：
最后编辑人：
最近更新时间：
所属模块：
依赖模块：`,
    example: `功能名称：产品创建
版本号：v1.0
最后编辑人：张三
最近更新时间：2025-12-03
所属模块：Product Management
依赖模块：Image Upload, Category Service`
  },
  {
    title: '功能背景（Purpose & Context）',
    description: '用 2–3 句话阐述功能目标和用户场景。',
    template: `// 回答三个问题：
// - 这是一个什么功能？
// - 解决什么业务问题？
// - 最终用户是谁？

功能背景：`,
    example: `功能背景：
用于创建新品，供管理员维护产品目录。
帮助快速上架新商品，支持多种分类和属性配置。`
  },
  {
    title: '用户角色（User Roles）',
    description: '明确谁能使用此功能，不同角色的权限。',
    template: `用户角色：
- 管理员（admin）: 允许创建、编辑、删除
- 普通用户（user）: 禁止访问
- 审核员（reviewer）: 仅可查看`,
    note: '列出每种角色允许/不允许做的事，AI 会据此生成权限控制逻辑。'
  },
  {
    title: '用户流程（User Flow）',
    description: '必须写得清晰、可执行、无歧义。只写关键路径，不写废话。',
    template: `用户流程：
1. 用户打开创建页
2. 用户填写产品基本信息
3. 用户上传主图
4. 用户点击"保存"
5. API 请求成功 → 跳转列表页
6. API 失败 → 显示错误提示`
  },
  {
    title: '页面结构（Page Structure）',
    description: '结构拆解为模块，方便 AI 生成组件化代码。',
    template: `页面结构：
- PageHeader: 标题 + 返回按钮
- FormSection:
    - productName 输入框
    - price 输入框
    - category 选择器
- ImageUploader: 上传产品主图
- ActionButtons: 保存 / 取消
- ToastMessage`
  },
  {
    title: '变量定义（Variables）',
    description: '这是 AI 生成代码的"输入核心"。',
    template: `变量：
- productName: string - 产品名称
- price: number - 产品价格
- categoryId: string - 分类 ID
- imageUrl: string - 上传后的图片链接
- isSubmitting: boolean - 提交按钮状态
- formErrors: object - 表单错误
- apiError: string - API 级别错误`
  },
  {
    title: '状态机（Page States）',
    description: '这部分是传统 PRD 完全没有的，也是 AI PE 的核心能力。',
    template: `状态：

default:
  - 所有输入为空
  - 保存按钮 disabled

typing:
  - 用户正在输入
  - 保存按钮 enabled

submitting:
  - 按钮 loading
  - 禁止重复点击

success:
  - toast("创建成功")
  - navigate('/products')

error:
  - 展示 formErrors 或 apiError`
  },
  {
    title: '输入与输出规则（Inputs → Outputs）',
    description: '明确每个用户动作触发什么行为。',
    template: `输入 → 输出：

输入：用户填写 productName
输出：更新本地变量 productName

输入：用户点击"保存"
输出：
    - 调用 POST /products
    - isSubmitting = true

输入：API 返回 400
输出：
    - formErrors 显示字段错误
    - isSubmitting = false

输入：API 返回 200
输出：
    - toast("创建成功")
    - navigate('/products')`
  },
  {
    title: 'API 行为规范（API Behavior）',
    description: 'AI 必须严格按你定义执行，否则代码会乱。',
    template: `API: 创建产品
路径：POST /products

请求体：
{
  name: string,
  price: number,
  categoryId: string,
  imageUrl: string
}

成功响应：200
{
  id: string
}
成功处理：
- toast("创建成功")
- 跳转产品列表

失败响应：
- 400：字段错误 → 显示在表单中
- 500：toast("系统错误，请稍后重试")
- 超时：toast("网络异常")

401:
- 跳登录页`
  },
  {
    title: '错误态（Error States）',
    description: 'AI 最容易漏掉，所以必须结构化。',
    template: `错误态：

productName 为空 → "请输入产品名称"
price <= 0 → "请输入正确价格"
image 上传失败 → toast("上传失败，请重试")
API 500 → toast("系统异常")`
  },
  {
    title: '组件与样式规范（Component Rules）',
    description: '为 AI 限定组件库，避免乱写 div。',
    template: `组件库必须使用：
- <Input />
- <Select />
- <Uploader />
- <Button />
- <Card />
- <Toast />

样式统一使用：
- color.primary
- spacing.4
- radius.md
- text.body`
  },
  {
    title: '完整示例数据（Mock Data）',
    description: 'AI 会自动使用这些作为默认数据。',
    template: `示例数据：
{
  "productName": "Thai Green Curry",
  "price": 199,
  "categoryId": "food",
  "imageUrl": "https://..."
}`
  },
  {
    title: '输出要求（Output Requirements）',
    description: '这是告诉 AI "你想要什么"。',
    template: `请生成：
1. 完整可运行 demo（React + Tailwind）
2. 使用统一组件库
3. 使用 mock API
4. 代码必须模块化（每个组件单独文件）
5. 包含错误态处理
6. 包含加载态
7. 包含成功提示
8. 页面必须可直接运行`
  }
])

const usageGuide = ref([
  {
    icon: '💼',
    role: '产品经理',
    items: ['用此模板替代传统 PRD', '培养结构化思维', '直接生成可交付 Demo']
  },
  {
    icon: '🎨',
    role: 'UI 设计师',
    items: ['定义组件规范', '确保 UI 一致性', '减少重复画图']
  },
  {
    icon: '💻',
    role: '前端工程师',
    items: ['作为开发输入', '减少理解成本', '提高 AI 辅助效率']
  },
  {
    icon: '🧪',
    role: '测试工程师',
    items: ['基于 Spec 写 Rulebook', '自动化测试', '完整状态覆盖']
  },
  {
    icon: '🤝',
    role: '甲方/外包',
    items: ['明确需求边界', '减少沟通成本', '快速验证 Demo']
  },
  {
    icon: '🤖',
    role: 'AI 工具',
    items: ['Claude Code', 'Cursor', 'GPT-4']
  }
])
</script>

<style scoped>
.template-page {
  min-height: 100%;
  background-color: var(--color-bg-page);
}

/* ========== Page Header ========== */
.page-header {
  background: linear-gradient(135deg, #06beb6 0%, #48b1bf 100%);
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

/* ========== Section Title ========== */
.section-title {
  font-size: 24px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-lg);
  border-left: 4px solid #06beb6;
  padding-left: var(--spacing-md);
}

/* ========== Key Insight ========== */
.key-insight {
  background: linear-gradient(135deg, #06beb6 0%, #48b1bf 100%);
  color: white;
  padding: var(--spacing-xl);
  margin: var(--spacing-lg) 0;
  border-radius: var(--border-radius-lg);
  font-size: 18px;
  text-align: center;
  font-weight: 500;
  line-height: 1.8;
}

/* ========== Intro Box ========== */
.intro-box {
  background: linear-gradient(135deg, #e0f7fa 0%, #f0f9ff 100%);
  border: 3px solid #06beb6;
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-xl);
  margin: var(--spacing-lg) 0;
}

.intro-box h3 {
  color: #00695c;
  margin: 0 0 var(--spacing-md);
  font-size: 20px;
}

.intro-box ul {
  margin: var(--spacing-md) 0;
  padding-left: var(--spacing-lg);
}

.intro-box li {
  margin: var(--spacing-sm) 0;
}

.intro-highlight {
  margin-top: var(--spacing-lg);
  font-weight: 600;
  color: #00695c;
}

/* ========== Template Section ========== */
.template-section {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-left: 4px solid #06beb6;
  padding: var(--spacing-xl);
  margin: var(--spacing-lg) 0;
  border-radius: var(--border-radius-md);
}

.template-section h3 {
  margin: 0 0 var(--spacing-md);
  color: #00695c;
  font-size: 20px;
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.section-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #06beb6 0%, #48b1bf 100%);
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  font-weight: bold;
  font-size: 14px;
}

.template-section > p {
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-md);
}

/* ========== Template Code ========== */
.template-code {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-md);
  margin: var(--spacing-md) 0;
  overflow-x: auto;
}

.template-code pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
}

/* ========== Example Box ========== */
.example-box {
  background: #fff3e0;
  border-left: 4px solid #ff9800;
  padding: var(--spacing-md) var(--spacing-lg);
  margin: var(--spacing-md) 0;
  border-radius: var(--border-radius-md);
}

.example-box h4 {
  margin: 0 0 var(--spacing-sm);
  color: #e65100;
  font-size: 16px;
}

.example-box pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  color: #424242;
  background: transparent;
}

/* ========== Usage Card ========== */
.usage-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-md);
  border-left: 4px solid #06beb6;
  margin-bottom: var(--spacing-lg);
  height: calc(100% - var(--spacing-lg));
}

.usage-card h5 {
  margin: 0 0 var(--spacing-md);
  color: #00695c;
  font-size: 16px;
}

.usage-card ul {
  margin: 0;
  padding-left: var(--spacing-lg);
  font-size: 14px;
}

.usage-card li {
  margin: var(--spacing-xs) 0;
}

/* ========== Final Template ========== */
.final-template {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
}

.final-code {
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.3);
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-md);
}

.final-code pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.8;
  color: #4ec9b0;
  white-space: pre-wrap;
}

/* ========== Tip List ========== */
.tip-list {
  margin: var(--spacing-sm) 0 0;
  padding-left: var(--spacing-lg);
}

.tip-list li {
  margin: var(--spacing-xs) 0;
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
}
</style>
