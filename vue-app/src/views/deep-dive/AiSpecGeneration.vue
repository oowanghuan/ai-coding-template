<template>
  <div class="spec-gen-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="container">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: '/deep-dive/ai-pe' }">AI PE 专题</el-breadcrumb-item>
          <el-breadcrumb-item>AI 自动生成 Spec</el-breadcrumb-item>
        </el-breadcrumb>
        <h1 class="page-title">🤖 AI 自动生成 Spec 与 Schema 标准</h1>
        <p class="page-subtitle">如何让 AI 帮助生成规范的 Spec，以及公司级 Schema 标准的设计方法</p>
      </div>
    </div>

    <div class="page-content">
      <div class="container">
        <!-- 核心洞察 -->
        <el-card class="content-card" shadow="never">
          <h2 class="section-title">核心洞察</h2>

          <div class="key-insight">
            这其实就是 UI（产品需求）按规则做 Spec 的问题
          </div>

          <div class="definition-box">
            <h3>✔ 是的。AI Coding 的核心不是"写代码"，而是"写 Spec"</h3>
            <p class="definition-text">
              <strong>Spec = 写给 AI 的程序规则</strong>
            </p>
          </div>
        </el-card>

        <!-- Part 1 -->
        <div class="part-divider">🎯 Part 1：AI 能否从 UI 生成 Spec？</div>

        <!-- 为什么需要 Spec -->
        <el-card class="content-card" shadow="never">
          <h2 class="section-title">为什么 AI 需要 Spec？</h2>

          <el-row :gutter="20">
            <el-col :xs="24" :md="12">
              <el-alert type="error" :closable="false">
                <template #title>
                  <strong>AI 不会：</strong>
                </template>
                <ul class="alert-list">
                  <li>❌ 从 UI 猜逻辑</li>
                  <li>❌ 从 PRD 推断流程</li>
                  <li>❌ 自动推导 API 行为</li>
                  <li>❌ 知道错误态属于哪个字段</li>
                  <li>❌ 自创组件库规范</li>
                </ul>
              </el-alert>
            </el-col>
            <el-col :xs="24" :md="12">
              <el-alert type="success" :closable="false">
                <template #title>
                  <strong>AI 只会：</strong>
                </template>
                <p class="ai-can">👉 执行你明确写出来的结构</p>
              </el-alert>
            </el-col>
          </el-row>

          <el-alert type="warning" :closable="false" style="margin-top: 20px;">
            <template #title>
              <strong>本质就是：</strong>
            </template>
            UI（视觉 + 交互）<br/>
            ＋ 业务需求（流程 + 逻辑）<br/>
            → 转换成结构化 Spec（程序语言）<br/>
            → AI 生成 Demo/Code/Test
          </el-alert>

          <h3 style="margin-top: 24px;">Spec 是整个 AI 驱动开发体系的"核心语言"</h3>
          <ul>
            <li>Figma 本身不是输入</li>
            <li>PRD 文案也不是输入</li>
            <li>聊天描述不是输入</li>
            <li><strong>Spec 才是 AI 的完整输入</strong></li>
          </ul>

          <div class="key-insight">
            AI PE 的核心价值 = 把"UI + 需求"转换成 Spec（结构化规则）
          </div>
        </el-card>

        <!-- AI 从 UI 生成 Spec -->
        <el-card class="content-card" shadow="never">
          <h2 class="section-title">⭐ AI 完全可以从 UI 生成 Spec</h2>

          <el-alert type="warning" :closable="false">
            而且这会成为未来标准流程
          </el-alert>

          <h3 style="margin-top: 24px;">AI 可以做到：</h3>
          <ol class="ai-can-list">
            <li>读取 Figma（结构化 JSON）</li>
            <li>识别页面结构（layout tree）</li>
            <li>识别组件（Input/Button/Card/Uploader）</li>
            <li>识别字段名（Label → 字段 key）</li>
            <li>识别错误态提示</li>
            <li>识别按钮行为（根据文案推断 action）</li>
            <li>识别成功/失败状态</li>
            <li>识别数据结构</li>
            <li>识别模块（表单区 / 列表区）</li>
            <li>生成 Spec 模板骨架</li>
          </ol>

          <h3>🎁 AI 可以自动生成的 Spec（70% 骨架）示例</h3>
          <div class="schema-code">
            <pre>{{ specExample }}</pre>
          </div>
        </el-card>

        <!-- 60-70% 自动化 -->
        <el-card class="content-card" shadow="never">
          <h2 class="section-title">🔥 AI 可以生成 60-70% 的 Spec</h2>

          <el-row :gutter="20">
            <el-col :xs="24" :md="12">
              <div class="comparison-item can-auto">
                <h4>✅ AI 可以自动识别（60-70%）</h4>
                <ul>
                  <li>页面结构（布局）</li>
                  <li>模块结构（Header/Form/Table）</li>
                  <li>字段（Input/Select/TextArea）</li>
                  <li>Placeholder / Label / Description</li>
                  <li>必填 vs 非必填</li>
                  <li>组件类型</li>
                  <li>按钮文案</li>
                  <li>错误文案（如果 UI 中有）</li>
                  <li>静态状态（default/disabled）</li>
                </ul>
                <p class="comparison-note success">这些都是"机械性规则"，AI 可以从 UI/Figma/自然语言中自动识别</p>
              </div>
            </el-col>
            <el-col :xs="24" :md="12">
              <div class="comparison-item need-human">
                <h4>⚠️ 需要 AI PE 补充（30-40%）</h4>
                <ul>
                  <li>API 行为（200/400/500）</li>
                  <li>业务校验逻辑</li>
                  <li>边界条件（超时/权限/网络错误）</li>
                  <li>角色权限（admin vs user）</li>
                  <li>输入输出关系</li>
                  <li>数据结构（object 深层结构）</li>
                  <li>多步骤流程（Step1 → Step2）</li>
                  <li>字段合法性（业务约束）</li>
                </ul>
                <p class="comparison-note warning">这些逻辑永远无法从 UI 推导，属于"业务语义"</p>
              </div>
            </el-col>
          </el-row>

          <div class="key-insight">
            未来完美分工：<br/><br/>
            AI 自动从 UI → 生成基础 Spec（结构化骨架）<br/>
            AI PE 填补逻辑、行为、状态、API、错误态
          </div>
        </el-card>

        <!-- 洞见总结 -->
        <el-card class="content-card" shadow="never">
          <h2 class="section-title">✨ 洞见总结</h2>

          <div class="definition-box">
            <h3>三层关系：</h3>
            <ul class="three-layers">
              <li><strong>UI = 静态样子</strong></li>
              <li><strong>Spec = 动态规则</strong></li>
              <li><strong>Code = 规则的执行文件</strong></li>
            </ul>
          </div>

          <el-alert type="warning" :closable="false">
            AI 能从 UI 自动生成 Spec 的"静态部分"，<br/>
            但"动态逻辑部分"还是 AI PE 来完成。<br/><br/>
            <strong>这就是为什么 AI PE 是 AI 时代最重要的角色。</strong>
          </el-alert>
        </el-card>

        <!-- Part 2 -->
        <div class="part-divider">📐 Part 2：80% Standard Schema 详解</div>

        <!-- Schema 定义 -->
        <el-card class="content-card" shadow="never">
          <h2 class="section-title">什么是 80% Standard Schema？</h2>

          <div class="definition-box">
            <h3>🎯 一句话解释</h3>
            <p class="definition-text">
              <strong>Standard Schema = AI 生成结构化 Spec 时必须遵循的统一"骨架"格式</strong>
            </p>
            <div class="percentage-badges">
              <span class="percentage-badge">80% 是模板</span>
              <span class="percentage-badge">20% 由业务补齐</span>
            </div>
          </div>

          <el-alert type="warning" :closable="false">
            <template #title>
              <strong>它的作用：</strong>
            </template>
            让 AI 从 UI（Figma）或自然语言需求中自动生成可执行 Spec，<br/>
            把 80% 的机械化内容自动化，<br/>
            减轻 AI PE 的工作量，<br/>
            减少漏项、发散、歧义。
          </el-alert>
        </el-card>

        <!-- 完整 Schema -->
        <el-card class="content-card" shadow="never">
          <h2 class="section-title">🧱 Schema 到底是什么？它长什么样？</h2>

          <el-alert type="info" :closable="false">
            <template #title>
              <strong>Schema = 一个标准的 Spec 数据结构</strong>
            </template>
            <ul class="alert-list">
              <li>知道生成 Spec 时要有哪些字段</li>
              <li>知道从 UI 抽取哪些信息</li>
              <li>知道不能遗漏哪些内容</li>
              <li>知道结构化输出应该是什么形态</li>
            </ul>
          </el-alert>

          <h3>⭐ 完整的《80% Spec Standard Schema（V1）》</h3>
          <el-alert type="warning" :closable="false" style="margin-bottom: 16px;">
            👇 这是 AI 生成 Spec 时必须遵守的格式（你们的 AI PE 只需要填剩下 20%）
          </el-alert>

          <div class="schema-code full-schema">
            <pre>{{ fullSchema }}</pre>
          </div>

          <div class="key-insight">
            这个 Schema 的本质：<br/><br/>
            AI 自动把"UI / 自然语言"转成 Spec 的 80%<br/>
            结构固定、通用、可评审、可扩展<br/><br/>
            业务逻辑的 20% 由 AI PE 补齐，形成最终可执行 Spec
          </div>
        </el-card>

        <!-- 实际使用方式 -->
        <el-card class="content-card" shadow="never">
          <h2 class="section-title">🌈 实际使用方式</h2>

          <div class="usage-scenario">
            <h5>📊 当甲方给 UI（Figma）时：</h5>
            <div class="flow-diagram">
              <span class="flow-step">UI</span>
              <span class="flow-arrow">→</span>
              <span class="flow-step">AI 提取 Schema（自动生成80%）</span>
              <span class="flow-arrow">→</span>
              <span class="flow-step">AI PE补 20%</span>
              <span class="flow-arrow">→</span>
              <span class="flow-step">完整Spec</span>
              <span class="flow-arrow">→</span>
              <span class="flow-step">Demo</span>
              <span class="flow-arrow">→</span>
              <span class="flow-step">Code</span>
            </div>
          </div>

          <div class="usage-scenario" style="margin-top: 24px;">
            <h5>💻 当你们自己做后台页面时：</h5>
            <div class="flow-diagram">
              <span class="flow-step">自然语言</span>
              <span class="flow-arrow">→</span>
              <span class="flow-step">AI 自动生成 Schema 80%</span>
              <span class="flow-arrow">→</span>
              <span class="flow-step">AI PE补 20%</span>
              <span class="flow-arrow">→</span>
              <span class="flow-step">Spec</span>
              <span class="flow-arrow">→</span>
              <span class="flow-step">Demo</span>
              <span class="flow-arrow">→</span>
              <span class="flow-step">Code</span>
            </div>
          </div>

          <el-alert type="warning" :closable="false" style="margin-top: 24px;">
            <template #title>
              <strong>关键概念</strong>
            </template>
            Spec = 标准语言<br/>
            Schema = Spec 的格式模板
          </el-alert>
        </el-card>

        <!-- Schema 效果 -->
        <el-card class="content-card" shadow="never">
          <h2 class="section-title">💡 这个 Schema 能带来的效果</h2>

          <el-row :gutter="16">
            <el-col :xs="24" :sm="12" :md="8" v-for="benefit in benefits" :key="benefit.title">
              <div class="benefit-card">
                <h5>{{ benefit.title }}</h5>
                <p>{{ benefit.desc }}</p>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <!-- 意义总结 -->
        <el-card class="content-card" shadow="never">
          <div class="key-insight">
            ✨ Schema 的意义<br/><br/>
            Schema 是 AI 时代取代 PRD 的"结构化蓝图"<br/><br/>
            UI + 自然语言需求经过 Schema<br/>
            → 变成可执行规格<br/>
            → AI coding 的能力释放出来
          </div>
        </el-card>

        <!-- 底部导航 -->
        <div class="action-section">
          <el-button @click="router.push('/deep-dive/ai-pe-training')">
            <el-icon class="el-icon--left"><ArrowLeft /></el-icon>
            返回培训指南
          </el-button>
          <el-button type="primary" @click="router.push('/deep-dive/ai-pe')">
            返回 AI PE 专题
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

const specExample = `// 如果你丢给 AI 一个 Figma 页面，它可以输出：

【页面结构】
- PageHeader
- ProductForm
- ImageUploader
- ActionButtons

【字段】
productName:
  component: Input
  label: "产品名称"
  placeholder: "请输入名称"
  required: true

price:
  component: Input
  type: number
  required: true

category:
  component: Select
  options: 从 UI 识别出来的下拉框
  required: true

【状态机】
default:
  - 所有字段为空
typing:
  - 字段正在输入
submitting:
  - 保存按钮 loading
success:
  - 显示成功提示
error:
  - 显示表单错误

【输入输出】
输入：点击保存 → 输出：调用 API
输入：上传图片 → 输出：更新 imageUrl

【模块拆分】
- Header
- Form
- Uploader
- ActionBar`

const fullSchema = `spec:
  meta:
    feature_name: ""          # 功能名称
    module: ""                # 所属模块
    version: "v1.0"
    last_updated: ""          # 自动填入
    role_access: []           # 角色权限（AI 可推断部分）

  ui_structure:
    layout:                   # 页面布局
      - type: "PageHeader"
      - type: "FormSection"
      - type: "ImageUploader"
      - type: "ActionBar"
    component_tree: []        # 从 UI/Figma 自动抽取

  fields:
    - key: ""                 # AI 从 label/placeholder 推断
      label: ""
      component: ""           # Input / Select / Uploader
      placeholder: ""
      required: true/false
      data_type: ""           # string/number/date (AI 自推断)
      validations:            # AI 识别不到时保持 empty
        length: ""
        min: ""
        max: ""
        pattern: ""
      ui_states:
        default: true
        disabled: false
        error: ""             # 如果 UI 有红字可被识别

  actions:
    - action: "click_save"    # 按钮行为
      triggers:
        - "validate_form"
        - "call_api:create_product"
      success:
        ui: "toast: 创建成功"
        navigation: "/products"
      failure:
        ui: "show_form_errors"
      states:
        isSubmitting: false

  states:
    default: {}
    typing: {}
    submitting:
      disabled_buttons: ["save"]
      loading_buttons: ["save"]
    success:
      toast: ""
      redirect: ""
    error:
      error_display: ""

  modules:
    - name: "ProductForm"
      description: ""
    - name: "ImageUploader"
    - name: "ActionButtons"

  api:                         # ⚠️ 这一块 AI 会保留空，由 AI PE 补
    create:
      path: ""
      method: "POST"
      body: {}
      success: {}
      error: {}
      timeout: ""
      auth_fail: ""

  error_states:
    - field: ""
      condition: ""
      message: ""

  mock_data: {}                # AI 自动生成`

const benefits = ref([
  { title: '✔ 让所有需求看起来一样有条理', desc: '每个字段、状态、模块、行为都清晰' },
  { title: '✔ 避免 AI 发散', desc: '因为结构固定，输出稳定' },
  { title: '✔ 能够自动生成测试 Rulebook', desc: 'Spec 结构固定 → Rulebook 可自动生成' },
  { title: '✔ 能够自动生成 Demo、代码、UI', desc: '所有生成都基于 Schema' },
  { title: '✔ PM 能 1 天变 AI PE', desc: '不需要学习怎么写结构，只需填空' },
  { title: '✔ QA 能只根据 Schema 自动写用例', desc: '机器可直接读取' }
])
</script>

<style scoped>
.spec-gen-page {
  min-height: 100%;
  background-color: var(--color-bg-page);
}

/* ========== Page Header ========== */
.page-header {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  color: #2c3e50;
  padding: var(--spacing-xxl) 0 var(--spacing-xl);
}

.page-header :deep(.el-breadcrumb__inner),
.page-header :deep(.el-breadcrumb__separator) {
  color: rgba(44, 62, 80, 0.8);
}

.page-title {
  font-size: 36px;
  font-weight: var(--font-weight-bold);
  margin: var(--spacing-lg) 0 var(--spacing-sm);
  color: #2c3e50;
}

.page-subtitle {
  font-size: var(--font-size-lg);
  color: rgba(44, 62, 80, 0.8);
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
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  color: #2c3e50;
  padding: var(--spacing-lg) var(--spacing-xl);
  margin: var(--spacing-xl) 0;
  border-radius: var(--border-radius-lg);
  text-align: center;
  font-size: 24px;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(168, 237, 234, 0.3);
}

/* ========== Section Title ========== */
.section-title {
  font-size: 24px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-lg);
  border-left: 4px solid #a8edea;
  padding-left: var(--spacing-md);
}

/* ========== Key Insight ========== */
.key-insight {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: var(--spacing-xl);
  margin: var(--spacing-lg) 0;
  border-radius: var(--border-radius-lg);
  font-size: 18px;
  text-align: center;
  font-weight: 500;
  line-height: 1.8;
}

/* ========== Definition Box ========== */
.definition-box {
  background: linear-gradient(135deg, #e0f7fa 0%, #f0f9ff 100%);
  border: 3px solid #00bcd4;
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-xl);
  margin: var(--spacing-lg) 0;
}

.definition-box h3 {
  color: #00838f;
  margin: 0 0 var(--spacing-md);
  font-size: 20px;
}

.definition-text {
  font-size: 18px;
  margin: var(--spacing-md) 0;
}

.three-layers {
  font-size: 18px;
  line-height: 2;
  padding-left: var(--spacing-lg);
}

.three-layers li {
  margin: var(--spacing-sm) 0;
}

/* ========== Alert List ========== */
.alert-list {
  margin: var(--spacing-sm) 0 0;
  padding-left: var(--spacing-lg);
}

.alert-list li {
  margin: var(--spacing-xs) 0;
}

.ai-can {
  font-size: 18px;
  font-weight: 600;
  color: #2e7d32;
  margin: var(--spacing-md) 0 0;
}

/* ========== AI Can List ========== */
.ai-can-list {
  padding-left: var(--spacing-lg);
}

.ai-can-list li {
  margin: var(--spacing-sm) 0;
}

/* ========== Schema Code ========== */
.schema-code {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-md);
  margin: var(--spacing-lg) 0;
  overflow-x: auto;
}

.schema-code pre {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
}

.full-schema {
  max-height: 500px;
  overflow-y: auto;
}

/* ========== Comparison Item ========== */
.comparison-item {
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-md);
  border: 2px solid;
  margin-bottom: var(--spacing-lg);
  height: calc(100% - var(--spacing-lg));
}

.comparison-item.can-auto {
  background: #e8f5e9;
  border-color: #4caf50;
}

.comparison-item.need-human {
  background: #fff3e0;
  border-color: #ff9800;
}

.comparison-item h4 {
  margin: 0 0 var(--spacing-md);
}

.comparison-item ul {
  margin: 0;
  padding-left: var(--spacing-lg);
}

.comparison-item li {
  margin: var(--spacing-xs) 0;
}

.comparison-note {
  margin-top: var(--spacing-md);
  font-weight: 600;
  font-size: 14px;
}

.comparison-note.success {
  color: #2e7d32;
}

.comparison-note.warning {
  color: #e65100;
}

/* ========== Percentage Badges ========== */
.percentage-badges {
  display: flex;
  gap: var(--spacing-md);
  margin-top: var(--spacing-md);
  flex-wrap: wrap;
}

.percentage-badge {
  display: inline-block;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: var(--spacing-xs) var(--spacing-lg);
  border-radius: 20px;
  font-weight: bold;
  font-size: 16px;
}

/* ========== Usage Scenario ========== */
.usage-scenario {
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: var(--border-radius-md);
  padding: var(--spacing-lg);
}

.usage-scenario h5 {
  margin: 0 0 var(--spacing-md);
  color: #424242;
  font-size: 16px;
}

/* ========== Flow Diagram ========== */
.flow-diagram {
  background: #f8f9fa;
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-md);
  text-align: center;
  border: 2px dashed #dee2e6;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-sm);
}

.flow-step {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  color: #2c3e50;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius-md);
  font-weight: 600;
  font-size: 14px;
}

.flow-arrow {
  color: #495057;
  font-size: 20px;
}

/* ========== Benefit Card ========== */
.benefit-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-left: 4px solid #00bcd4;
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-md);
  border-radius: var(--border-radius-md);
  height: calc(100% - var(--spacing-md));
}

.benefit-card h5 {
  margin: 0 0 var(--spacing-sm);
  color: #00838f;
  font-size: 15px;
}

.benefit-card p {
  margin: 0;
  font-size: 14px;
  color: var(--color-text-secondary);
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

  .flow-diagram {
    flex-direction: column;
  }

  .flow-arrow {
    transform: rotate(90deg);
  }
}
</style>
