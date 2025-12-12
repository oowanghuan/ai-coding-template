<template>
  <div class="examples-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="container">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: '/deep-dive/ai-pe' }">AI PE 专题</el-breadcrumb-item>
          <el-breadcrumb-item>实战案例</el-breadcrumb-item>
        </el-breadcrumb>
        <h1 class="page-title">💡 AI PE 实战案例与双模式工作流</h1>
        <p class="page-subtitle">从 PRD → 结构化需求 → AI Demo 的完整示例与双模式选择指南</p>
      </div>
    </div>

    <div class="page-content">
      <div class="container">
        <!-- Part 1 标题 -->
        <div class="part-divider">📝 Part 1：真实功能完整示例</div>

        <!-- 功能案例介绍 -->
        <el-card class="content-card" shadow="never">
          <h2 class="section-title">从 PRD → 结构化需求 → AI Demo 的完整示例</h2>

          <div class="key-insight">
            功能案例：产品创建（Create Product）<br/>
            这是公司常见且不复杂的场景，最适合作为学习示例
          </div>

          <el-alert type="warning" :closable="false" class="quote-alert">
            <template #title>
              <strong>这个示例展示：</strong>
            </template>
            <ul class="alert-list">
              <li>传统 PM 如何写需求（模糊、不可执行）</li>
              <li>AI PE 如何转换为结构化规格（清晰、可执行）</li>
              <li>Claude Code 如何根据规格生成完整 Demo</li>
            </ul>
          </el-alert>
        </el-card>

        <!-- 三步转换 -->
        <el-card class="content-card" shadow="never">
          <!-- Step 1 -->
          <div class="step-card">
            <div class="step-header">
              <span class="step-number">1</span>
              <h3>第一步：PM 写的传统 PRD</h3>
            </div>

            <div class="prd-old">
              <h4>❌ 传统 PRD（不适合 AI）</h4>
              <p>用户可以创建一个新的产品，包括填写名称、价格、类别，并上传图片。</p>
              <p>点击保存后，系统会保存数据并返回到列表页。</p>
              <p>如果有错误会提醒用户。</p>
              <p>图片上传失败时提醒用户。</p>
              <p>管理员可以进行此操作，普通用户没有权限。</p>
              <p class="problem-text">问题：文字化、模糊、AI 无法执行</p>
            </div>
          </div>

          <!-- Step 2 -->
          <div class="step-card">
            <div class="step-header">
              <span class="step-number">2</span>
              <h3>第二步：AI PE 转换为结构化规格</h3>
            </div>

            <div class="spec-new">
              <h4>✅ AI PE 的结构化写法</h4>

              <div v-for="section in specSections" :key="section.title" class="spec-section">
                <h5>{{ section.title }}</h5>
                <pre class="spec-content">{{ section.content }}</pre>
              </div>
            </div>
          </div>

          <!-- Step 3 -->
          <div class="step-card">
            <div class="step-header">
              <span class="step-number">3</span>
              <h3>第三步：Claude Code 生成可运行 Demo</h3>
            </div>

            <div class="result-box">
              <h4>🎉 Claude Code 自动生成：</h4>
              <ul>
                <li>✅ 页面层级结构（PageHeader / Form / Uploader / Footer）</li>
                <li>✅ React/Tailwind 完整前端代码</li>
                <li>✅ Mock API</li>
                <li>✅ 错误态处理</li>
                <li>✅ 成功 toast</li>
                <li>✅ 跳转逻辑</li>
                <li>✅ 全部组件的文件结构</li>
                <li>✅ 类型约束</li>
              </ul>
              <p class="result-highlight">你无需写一行代码，就获得一个可运行的前端 Demo</p>
            </div>
          </div>
        </el-card>

        <!-- 团队理解 -->
        <el-card class="content-card" shadow="never">
          <h2 class="section-title">🧠 团队会理解到什么？</h2>
          <ul class="understanding-list">
            <li>✅ PRD 这种模糊写法已经不适合 AI 时代</li>
            <li>✅ 结构化 Spec 是新的标准</li>
            <li>✅ AI 在得到清晰结构化指令后表现极稳</li>
            <li>✅ PM 能自己生成 UI + Demo，无需等前端</li>
            <li>✅ 大型项目可以由多个 AI PE 拆分模块并行执行</li>
            <li>✅ Claude Code/Cursor 才是前端生产力的主力</li>
            <li>✅ 研发节奏会从"UI→前端→联调"变成"Spec→Demo→后端配合"</li>
          </ul>
          <div class="key-insight">这是一种完全新的软件开发模式</div>
        </el-card>

        <!-- Part 2 标题 -->
        <div class="part-divider">🔄 Part 2：双模式工作流</div>

        <!-- 双模式介绍 -->
        <el-card class="content-card" shadow="never">
          <h2 class="section-title">Figma → 结构化 → AI Demo 的双模式</h2>

          <el-alert type="warning" :closable="false" class="quote-alert">
            <template #title>
              <strong>核心问题：</strong>
            </template>
            甲方 insist Figma → 你们团队想走 Spec → AI Demo 的方式。<br/>
            如何兼容？怎么让 AI 在两种输入下都不发散？
          </el-alert>

          <el-alert type="info" :closable="false" style="margin-top: 16px;">
            <template #title>
              <strong>为什么需要"双模式"？</strong>
            </template>
            <ul class="alert-list">
              <li>AI 生成 UI 很快，但是 UI 设计图（甲方给的）经常乱、不一致</li>
              <li>有些项目必须遵循甲方 Figma</li>
              <li>有些项目越不用 Figma 越快</li>
              <li>用 Figma 作为中间层容易造成重复劳动</li>
            </ul>
          </el-alert>

          <div class="key-insight">
            正确做法：在不同场景使用不同模式，并用 Spec 做桥梁对齐<br/>
            <strong>Spec 是唯一的单一真实来源（Single Source of Truth）</strong>
          </div>
        </el-card>

        <!-- 整体框架 -->
        <el-card class="content-card" shadow="never">
          <h2 class="section-title">整体框架：双模式工作流</h2>

          <div class="flow-diagram">
            <div class="flow-label">（甲方给 UI 时）</div>
            <div class="flow-steps">
              <span class="flow-step">Figma</span>
              <span class="flow-arrow">→</span>
              <span class="flow-step">结构化 Spec</span>
              <span class="flow-arrow">→</span>
              <span class="flow-step">AI Demo</span>
              <span class="flow-arrow">→</span>
              <span class="flow-step">最终代码</span>
            </div>

            <div class="flow-divider">↑</div>

            <div class="flow-label">（无 UI 时）</div>
            <div class="flow-steps">
              <span class="flow-step">Spec</span>
              <span class="flow-arrow">→</span>
              <span class="flow-step">Demo</span>
              <span class="flow-arrow">→</span>
              <span class="flow-step">Code</span>
            </div>
          </div>

          <el-alert type="info" :closable="false">
            <strong>关键：</strong>Spec 是关键层，两种模式都通过它对齐
          </el-alert>
        </el-card>

        <!-- 模式 A -->
        <el-card class="content-card mode-card" shadow="never">
          <div class="mode-badge">模式 A</div>
          <h2 class="mode-title">Figma → 结构化 Spec → AI Demo</h2>
          <p class="mode-subtitle">适用于：甲方强 UI、重品牌、要求像原图</p>

          <h3>📌 流程步骤（6步）</h3>

          <el-collapse>
            <el-collapse-item v-for="(step, index) in modeASteps" :key="index" :name="index">
              <template #title>
                <span class="collapse-title">
                  <span class="step-badge">{{ index + 1 }}</span>
                  {{ step.title }}
                </span>
              </template>
              <div class="collapse-content">
                <p>{{ step.desc }}</p>
                <ul v-if="step.items">
                  <li v-for="item in step.items" :key="item">{{ item }}</li>
                </ul>
                <el-alert v-if="step.highlight" type="success" :closable="false">
                  {{ step.highlight }}
                </el-alert>
              </div>
            </el-collapse-item>
          </el-collapse>

          <div class="benefits-box">
            <h4>🎁 模式 A 的好处</h4>
            <ul>
              <li>✅ 甲方 UI 要求得到满足</li>
              <li>✅ 你们团队不被 Figma 拖垮</li>
              <li>✅ AI 能正确生成一致 UI，而不是发散</li>
              <li>✅ PM 仍然是 Spec Owner</li>
              <li>✅ 交付速度比传统 UI → 前端 快 3–10 倍</li>
            </ul>
          </div>
        </el-card>

        <!-- 模式 B -->
        <el-card class="content-card mode-card" shadow="never">
          <div class="mode-badge mode-b">模式 B</div>
          <h2 class="mode-title">Spec → AI Demo（无 Figma，更快）</h2>
          <p class="mode-subtitle">适用于：后台、工具类、内部系统、你们自己的产品</p>

          <h3>📌 流程步骤（5步）</h3>

          <el-collapse>
            <el-collapse-item v-for="(step, index) in modeBSteps" :key="index" :name="index">
              <template #title>
                <span class="collapse-title">
                  <span class="step-badge">{{ index + 1 }}</span>
                  {{ step.title }}
                </span>
              </template>
              <div class="collapse-content">
                <p>{{ step.desc }}</p>
                <ul v-if="step.items">
                  <li v-for="item in step.items" :key="item">{{ item }}</li>
                </ul>
              </div>
            </el-collapse-item>
          </el-collapse>

          <div class="benefits-box benefits-b">
            <h4>🎁 模式 B 的好处</h4>
            <ul>
              <li>✅ 大幅减少 UI 工作量</li>
              <li>✅ 适合你们团队高度自动化的后台系统</li>
              <li>✅ 让 AI 产品工程师独立交付完整模块</li>
              <li>✅ Demo 驱动需求，不再需要巨量 UI 图</li>
            </ul>
          </div>
        </el-card>

        <!-- 模式选择指南 -->
        <el-card class="content-card" shadow="never">
          <h2 class="section-title">⭐ 模式选择指南</h2>

          <el-table :data="modeGuide" stripe>
            <el-table-column prop="scenario" label="场景" min-width="200" />
            <el-table-column prop="mode" label="推荐模式" min-width="250" />
          </el-table>
        </el-card>

        <!-- 特别建议 -->
        <el-card class="content-card" shadow="never">
          <div class="key-insight">
            🔥 特别建议（对你们团队最有价值）<br/><br/>
            把 Spec（结构化规格）作为统一标准<br/>
            不管是模式 A 还是 B
          </div>

          <ul class="suggestion-list">
            <li>✅ 甲方给 UI → PM 转 Spec</li>
            <li>✅ 自己内部用 Demo → PM 写 Spec</li>
            <li>✅ 测试 Rulebook → 基于 Spec</li>
            <li>✅ UI 校验 → 基于 Spec</li>
            <li>✅ 前端联调 → 基于 Spec</li>
            <li>✅ AI coding → 必须吃 Spec</li>
          </ul>

          <el-alert type="warning" :closable="false">
            <strong>Spec 是项目的"唯一真实来源（SSOT）"</strong>
          </el-alert>
        </el-card>

        <!-- 可贴墙流程图 -->
        <el-card class="content-card final-flow-card" shadow="never">
          <h2 class="section-title" style="color: white;">🧩 可以贴墙上的流程图</h2>
          <div class="final-flow">
            <div class="flow-note">（甲方给 UI）</div>
            <div class="flow-text">
              Figma<br/>
              ↓<br/>
              结构化规格（Spec） ←（无 UI 时 PM 直接写 Spec）<br/>
              ↓<br/>
              Claude Code 生成 Demo<br/>
              ↓<br/>
              UI 校验 / 后端 API 接入<br/>
              ↓<br/>
              QA Rulebook（AI 自动测试）<br/>
              ↓<br/>
              上线交付
            </div>
          </div>
        </el-card>

        <!-- 底部导航 -->
        <div class="action-section">
          <el-button @click="router.push('/deep-dive/ai-pe')">
            <el-icon class="el-icon--left"><ArrowLeft /></el-icon>
            返回 AI PE 专题
          </el-button>
          <el-button type="primary" @click="router.push('/deep-dive/ai-pe-spec-template')">
            查看模板库
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

const specSections = ref([
  {
    title: '0. 元信息',
    content: `功能名称：Create Product
版本：v1.0
负责人：AI PE
更新时间：2025-12-03
模块：Product Management`
  },
  {
    title: '1. 功能背景',
    content: `管理员可以创建产品，维护产品目录。
该页面提交成功后跳回产品列表页。`
  },
  {
    title: '2. 用户角色',
    content: `- admin：允许访问与操作
- user：禁止访问（跳转 403）`
  },
  {
    title: '3. 用户流程',
    content: `1. 用户（admin）打开创建页
2. 用户填写产品名称、价格、类别
3. 用户上传主图
4. 用户点击"保存"
5. 调用 POST /api/products
6. 成功 → toast("创建成功") → 跳转列表页
7. 失败 → 展示错误（字段或全局）`
  },
  {
    title: '4. 页面结构',
    content: `- PageHeader（标题 + 返回）
- ProductForm（名称、价格、类别）
- ImageUploader（上传主图）
- ActionBar（保存 / 取消）
- Toast`
  },
  {
    title: '5. 变量',
    content: `- productName: string
- price: number
- categoryId: string
- imageUrl: string
- isSubmitting: boolean
- formErrors: object
- apiError: string`
  },
  {
    title: '6. 状态',
    content: `default:
  - 所有字段为空
  - 保存按钮 disabled

typing:
  - 输入中
  - 保存按钮 enabled

submitting:
  - 按钮 loading
  - 禁止重复点击

error:
  - 展示 formErrors 或 apiError

success:
  - 创建成功 → 跳转列表页`
  },
  {
    title: '7. 输入与输出',
    content: `输入：填写 productName
输出：更新变量 productName

输入：点击保存
输出：isSubmitting = true, 调用 POST /api/products

输入：API 返回 200
输出：toast("创建成功"), navigate('/products')

输入：API 400（字段错误）
输出：formErrors 显示字段错误, isSubmitting = false`
  },
  {
    title: '8. API 行为',
    content: `API: 创建产品
路径：POST /api/products

请求体：{ name, price, categoryId, imageUrl }

成功（200）：返回 { id }, toast("创建成功"), navigate
失败（400）：返回 { errors }, 展示字段错误
失败（500）：toast("系统错误，请稍后重试")
401：navigate('/login')
403：navigate('/403')`
  },
  {
    title: '9. 错误态',
    content: `productName 为空 → "请输入产品名称"
price <= 0 → "请输入正确价格"
categoryId 为空 → "请选择分类"
image 上传失败 → toast("上传失败，请重试")
API 500 → toast("服务器错误")
网络超时 → toast("网络异常，请重试")`
  }
])

const modeASteps = ref([
  {
    title: 'PM / AI PE 从 Figma 中抽取"结构化信息"',
    desc: '不能让 AI 直接看 Figma，必须提取：',
    items: ['页面结构（Header / Sidebar / Main）', '组件（Input、Button、Card）', '交互（hover / disabled / error）', '状态（loading/error/success）', '文案', '输入输出', '特殊规则'],
    highlight: '✔ 这是 AI PE 的核心增值点'
  },
  {
    title: 'UI 系统化约束（保证 AI 不发散）',
    desc: '把 Figma 中的样式转换成 Design Tokens 和可复用组件',
    items: ['Color tokens', 'Spacing tokens', 'Typography tokens', '可复用组件（Form、Card、Uploader）', '禁用行为（不能 invent 新组件）']
  },
  {
    title: '用结构化 Spec 喂 Claude Code 生成 Demo',
    desc: 'Demo 会忠实呈现 Figma 的 UI，但用的是你们的组件库风格。'
  },
  {
    title: '设计比对 Demo → Figma（UI 审核）',
    desc: 'UI 设计师只需要检查主色/字体/间距、组件匹配、布局偏移。不需要 review code。'
  },
  {
    title: '后端补 API / AI 自动联调',
    desc: '因为 Spec 写了每个 API 的行为，AI 能自动生成 mock API、API 请求函数、错误态处理、loading 处理。'
  },
  {
    title: 'QA 根据 Spec 写 Rulebook → AI 自动测试',
    desc: 'Spec 是结构化的，所以测试可自动化。'
  }
])

const modeBSteps = ref([
  {
    title: 'PM 写结构化 Spec（不需要 UI 图）',
    desc: 'Spec 包含页面结构、组件、状态、输入输出、API 行为、错误态。'
  },
  {
    title: 'Claude Code 生成 Demo（可运行）',
    desc: 'AI 自动完成：',
    items: ['自动生成 UI', '自动对齐组件库', '自动完成布局', '自动处理状态机']
  },
  {
    title: '设计师提供最小 UI 反馈（可选）',
    desc: '只需要调整间距、字体、层级。不需要画完整 Figma。'
  },
  {
    title: 'AI 重构 UI → 最终定稿',
    desc: '设计只需要给出高层规则，不需要画图。'
  },
  {
    title: '后端 + QA Rulebook（同模式 A）',
    desc: '流程与模式 A 相同。'
  }
])

const modeGuide = ref([
  { scenario: '甲方要求视觉一致、品牌要求高', mode: '模式 A：Figma → Spec → Demo' },
  { scenario: '后台管理系统、数据产品', mode: '模式 B：Spec → Demo' },
  { scenario: '你们自己开发 SaaS、内部工具', mode: '模式 B' },
  { scenario: '想提速、减少 UI 工作', mode: '模式 B' },
  { scenario: '多团队协作的大项目', mode: '模式 A（保证对齐）' },
  { scenario: '小模块 / 快速验证', mode: '模式 B（小功能直接干）' }
])
</script>

<style scoped>
.examples-page {
  min-height: 100%;
  background-color: var(--color-bg-page);
}

/* ========== Page Header ========== */
.page-header {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
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
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
  color: white;
  padding: var(--spacing-lg) var(--spacing-xl);
  margin: var(--spacing-xl) 0;
  border-radius: var(--border-radius-lg);
  text-align: center;
  font-size: 24px;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
}

/* ========== Section Title ========== */
.section-title {
  font-size: 24px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-lg);
  border-left: 4px solid #ff6b6b;
  padding-left: var(--spacing-md);
}

/* ========== Key Insight ========== */
.key-insight {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
  color: white;
  padding: var(--spacing-xl);
  margin: var(--spacing-lg) 0;
  border-radius: var(--border-radius-lg);
  font-size: 18px;
  text-align: center;
  font-weight: 500;
  line-height: 1.8;
}

/* ========== Quote Alert ========== */
.quote-alert {
  margin: var(--spacing-lg) 0;
}

.alert-list {
  margin: var(--spacing-sm) 0 0;
  padding-left: var(--spacing-lg);
}

.alert-list li {
  margin: var(--spacing-xs) 0;
}

/* ========== Step Card ========== */
.step-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-left: 4px solid #ff6b6b;
  padding: var(--spacing-xl);
  margin: var(--spacing-lg) 0;
  border-radius: var(--border-radius-md);
}

.step-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.step-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  font-weight: bold;
  font-size: 16px;
}

.step-header h3 {
  margin: 0;
  font-size: 20px;
  color: #c92a2a;
}

/* ========== PRD Old vs Spec New ========== */
.prd-old {
  background: #ffebee;
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-md);
  border-left: 4px solid #f44336;
}

.prd-old h4 {
  color: #c62828;
  margin: 0 0 var(--spacing-md);
}

.prd-old p {
  margin: var(--spacing-sm) 0;
}

.problem-text {
  color: #c62828;
  font-weight: 600;
  margin-top: var(--spacing-lg) !important;
}

.spec-new {
  background: #e8f5e9;
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-md);
  border-left: 4px solid #4caf50;
}

.spec-new h4 {
  color: #2e7d32;
  margin: 0 0 var(--spacing-md);
}

.spec-section {
  background: #f5f5f5;
  padding: var(--spacing-md);
  margin: var(--spacing-sm) 0;
  border-radius: var(--border-radius-sm);
  border-left: 3px solid #4caf50;
}

.spec-section h5 {
  margin: 0 0 var(--spacing-sm);
  color: #2e7d32;
  font-size: 15px;
}

.spec-content {
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #424242;
  margin: 0;
  white-space: pre-wrap;
}

/* ========== Result Box ========== */
.result-box {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: var(--spacing-xl);
  border-radius: var(--border-radius-lg);
}

.result-box h4 {
  color: white;
  margin: 0 0 var(--spacing-md);
  font-size: 20px;
}

.result-box ul {
  margin: var(--spacing-md) 0;
  padding-left: var(--spacing-lg);
}

.result-box li {
  margin: var(--spacing-sm) 0;
}

.result-highlight {
  text-align: center;
  font-weight: 600;
  margin-top: var(--spacing-lg);
}

/* ========== Understanding List ========== */
.understanding-list {
  font-size: 16px;
  padding-left: var(--spacing-lg);
}

.understanding-list li {
  margin: var(--spacing-md) 0;
}

/* ========== Flow Diagram ========== */
.flow-diagram {
  background: #f8f9fa;
  padding: var(--spacing-xl);
  border-radius: var(--border-radius-md);
  text-align: center;
  border: 2px dashed #dee2e6;
  margin: var(--spacing-lg) 0;
}

.flow-label {
  font-weight: 600;
  color: #495057;
  margin-bottom: var(--spacing-md);
}

.flow-steps {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}

.flow-step {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
  color: white;
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--border-radius-md);
  font-weight: 600;
}

.flow-arrow {
  color: #495057;
  font-size: 24px;
}

.flow-divider {
  font-size: 24px;
  color: #495057;
  margin: var(--spacing-lg) 0;
}

/* ========== Mode Card ========== */
.mode-card {
  border: 3px solid #dee2e6;
}

.mode-badge {
  display: inline-block;
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
  color: white;
  padding: var(--spacing-xs) var(--spacing-lg);
  border-radius: 20px;
  font-weight: bold;
  font-size: 16px;
  margin-bottom: var(--spacing-md);
}

.mode-badge.mode-b {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.mode-title {
  font-size: 24px;
  color: #495057;
  margin: 0 0 var(--spacing-sm);
  text-align: center;
  border-bottom: 2px solid #dee2e6;
  padding-bottom: var(--spacing-md);
}

.mode-subtitle {
  text-align: center;
  color: #6c757d;
  margin-bottom: var(--spacing-xl);
}

.collapse-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.step-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-weight: bold;
  font-size: 12px;
}

.collapse-content {
  padding: var(--spacing-md);
}

.collapse-content ul {
  padding-left: var(--spacing-lg);
}

/* ========== Benefits Box ========== */
.benefits-box {
  background: #e7f5ff;
  border-left: 4px solid #1c7ed6;
  padding: var(--spacing-lg);
  margin-top: var(--spacing-xl);
  border-radius: var(--border-radius-md);
}

.benefits-box.benefits-b {
  background: #f3e8ff;
  border-left-color: #764ba2;
}

.benefits-box h4 {
  margin: 0 0 var(--spacing-md);
  color: #1864ab;
}

.benefits-box.benefits-b h4 {
  color: #764ba2;
}

.benefits-box ul {
  margin: 0;
  padding-left: var(--spacing-lg);
}

.benefits-box li {
  margin: var(--spacing-sm) 0;
}

/* ========== Suggestion List ========== */
.suggestion-list {
  font-size: 16px;
  padding-left: var(--spacing-lg);
  margin: var(--spacing-lg) 0;
}

.suggestion-list li {
  margin: var(--spacing-md) 0;
}

/* ========== Final Flow Card ========== */
.final-flow-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
}

.final-flow-card :deep(.el-card__body) {
  padding: var(--spacing-xxl);
}

.final-flow {
  background: rgba(255, 255, 255, 0.1);
  padding: var(--spacing-xl);
  border-radius: var(--border-radius-md);
  margin: var(--spacing-lg) 0;
}

.flow-note {
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: var(--spacing-md);
}

.flow-text {
  font-family: monospace;
  font-size: 16px;
  line-height: 2;
  color: white;
  text-align: center;
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

  .flow-steps {
    flex-direction: column;
  }

  .flow-arrow {
    transform: rotate(90deg);
  }
}
</style>
