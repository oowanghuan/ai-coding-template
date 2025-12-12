<template>
  <div class="deep-dive-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="container">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: '/role/ai-pe' }">AI 产品工程师</el-breadcrumb-item>
          <el-breadcrumb-item>核心能力</el-breadcrumb-item>
        </el-breadcrumb>
        <h1 class="page-title">🎯 AI PE 的核心能力与结构化思维</h1>
        <p class="page-subtitle">理解 AI PE 的本质定位与能力要求</p>
      </div>
    </div>

    <div class="page-content">
      <div class="container">
        <!-- Section 1: 核心判断 -->
        <el-card class="content-section" shadow="never">
          <h2 class="section-title">核心判断：AI PE 是什么样的人？</h2>

          <div class="definition-box">
            <h3>AI Product Engineer（AI PE）的本质</h3>
            <p><strong>AI PE ≠ 纯产品经理，也 ≠ 纯工程师</strong></p>
            <div class="formula">
              AI PE = 懂业务逻辑 × 懂工程结构 × 能 orchestrate AI × 能 debug
            </div>
          </div>

          <div class="quote-box">
            <strong>这个岗位不是把"PM + UI + 前端"合在一起，而是：</strong><br/><br/>
            从产品经理 → 向工程靠近（这是主流）<br/>
            从前端工程师 → 向产品逻辑靠近（少数）
          </div>

          <el-row :gutter="24" class="stat-row">
            <el-col :xs="24" :sm="12">
              <div class="stat-box">
                <div class="stat-number">90%</div>
                <div class="stat-label">强产品 + 中等技术 → AI PE</div>
              </div>
            </el-col>
            <el-col :xs="24" :sm="12">
              <div class="stat-box">
                <div class="stat-number">10%</div>
                <div class="stat-label">强前端 + 基本产品 sense → AI PE</div>
              </div>
            </el-col>
          </el-row>

          <div class="highlight-box">
            <h4>为什么是这个比例？</h4>
            <p>因为 AI coding 不是工程，而是<strong>编排（orchestration）</strong>和<strong>规则设计（specification design）</strong>。</p>
          </div>
        </el-card>

        <!-- Section 2: 5大核心能力 -->
        <el-card class="content-section" shadow="never">
          <h2 class="section-title">AI Product Engineer 的 5 大核心能力</h2>

          <div class="capability-card" v-for="(cap, index) in capabilities" :key="index">
            <h4>
              <span class="capability-number">{{ index + 1 }}</span>
              {{ cap.title }}
            </h4>
            <p v-if="cap.subtitle"><strong>{{ cap.subtitle }}</strong></p>
            <ul>
              <li v-for="(point, i) in cap.points" :key="i">{{ point }}</li>
            </ul>
            <div class="highlight-box" v-if="cap.highlight">
              <p v-html="cap.highlight"></p>
            </div>
            <div class="quote-box" v-if="cap.quote">
              {{ cap.quote }}
            </div>
          </div>
        </el-card>

        <!-- Section 3: 核心总结 -->
        <el-card class="content-section" shadow="never">
          <h2 class="section-title">核心总结：AI PE 是"结构高手"而非"技术高手"</h2>

          <div class="quote-box">
            <strong>看这句话你就懂了：</strong><br/><br/>
            传统工程师靠"写代码"增值。<br/>
            AI 时代工程师靠"写清楚结构，告诉 AI 写代码"增值。
          </div>

          <div class="skill-matrix">
            <h3>AI PE 的技能矩阵</h3>
            <el-row :gutter="24">
              <el-col :xs="24" :sm="12">
                <div class="skill-item not-needed">
                  <h5><span class="cross-icon">✗</span> 不需要的能力</h5>
                  <ul>
                    <li>会写后端</li>
                    <li>会写复杂数据结构</li>
                    <li>会做高深技术</li>
                    <li>会写工程级前端</li>
                    <li>会搭服务器</li>
                    <li>会优化性能</li>
                  </ul>
                </div>
              </el-col>
              <el-col :xs="24" :sm="12">
                <div class="skill-item needed">
                  <h5><span class="check-icon">✓</span> 需要的能力</h5>
                  <ul>
                    <li>会拆解</li>
                    <li>会抽象</li>
                    <li>会定义规则</li>
                    <li>会 orchestrate AI</li>
                    <li>会 debug 提示</li>
                    <li>会结构化表达</li>
                  </ul>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>

        <!-- Section 4: 结构化需求详解 -->
        <el-card class="content-section" shadow="never">
          <h2 class="section-title">深入解析：什么是"结构化需求"？</h2>

          <div class="key-insight">
            AI 不会推理"隐含逻辑"，AI 只会执行"明确规则"
          </div>

          <h3>传统 PRD 的问题</h3>
          <ul class="problem-list">
            <li>写得像文章</li>
            <li>模糊、含义多</li>
            <li>不告诉每个状态是什么</li>
            <li>不告诉失败要怎么办</li>
            <li>不告诉按钮何时可点</li>
            <li>不告诉字段边界条件</li>
            <li>不告诉 API 的返回结构</li>
          </ul>

          <div class="quote-box">
            <strong>所以 AI PE 的工作就是：</strong><br/><br/>
            把需求拆成：变量、状态、输入输出、状态机、组件规则、API 行为、错误态、边界条件。<br/>
            让 AI 无需猜测，只需执行。<br/><br/>
            <strong>这就是结构化。</strong>
          </div>
        </el-card>

        <!-- Section 5: 6大核心要素 -->
        <el-card class="content-section" shadow="never">
          <h2 class="section-title">结构化的 6 大核心要素详解</h2>

          <div class="concept-card" v-for="(concept, index) in structuredElements" :key="index">
            <h4>{{ index + 1 }}. {{ concept.title }}</h4>
            <p>{{ concept.desc }}</p>
            <div class="concept-example">
              <ul>
                <li v-for="(item, i) in concept.examples" :key="i">{{ item }}</li>
              </ul>
            </div>
            <div class="highlight-box">
              <strong>{{ concept.insight }}</strong>
            </div>
          </div>
        </el-card>

        <!-- Section 6: 实战对比 -->
        <el-card class="content-section" shadow="never">
          <h2 class="section-title">实战对比：传统 PRD vs 结构化需求</h2>

          <div class="prd-comparison">
            <h4>案例：产品创建功能</h4>

            <div class="prd-old">
              <h5>❌ 传统 PM 的写法</h5>
              <p>用户可以创建一个产品。</p>
              <p>点击保存后会提交表单。</p>
              <p>失败时给用户提示。</p>
              <p class="problem-text">问题：非常模糊，AI 无法执行</p>
            </div>

            <div class="prd-new">
              <h5>✅ AI PE 的结构化写法</h5>

              <div class="spec-section">
                <h6>变量</h6>
                <div class="spec-item">• productName: string</div>
                <div class="spec-item">• price: number</div>
                <div class="spec-item">• isSubmitting: boolean</div>
              </div>

              <div class="spec-section">
                <h6>状态</h6>
                <div class="spec-item">• default（默认状态）</div>
                <div class="spec-item">• invalid（验证失败）</div>
                <div class="spec-item">• submitting（提交中）</div>
                <div class="spec-item">• success（成功）</div>
                <div class="spec-item">• error（失败）</div>
              </div>

              <div class="spec-section">
                <h6>API 行为</h6>
                <div class="spec-item">• 200 → toast("成功") → navigate('/products')</div>
                <div class="spec-item">• 400 → 展示字段错误文案</div>
                <div class="spec-item">• 500 → toast("系统错误")</div>
              </div>

              <div class="spec-section">
                <h6>错误态</h6>
                <div class="spec-item">• productName 为空 → "请输入产品名"</div>
                <div class="spec-item">• 价格 &lt;=0 → "请输入正确价格"</div>
              </div>
            </div>
          </div>

          <div class="key-insight">
            你看，一个不懂代码的人，也能写出这些结构。<br/>
            但一个只会写作文式 PRD 的 PM，做不到。
          </div>
        </el-card>

        <!-- Section 7: 最终公式 -->
        <el-card class="content-section" shadow="never">
          <div class="formula-box">
            <h3>🧩 AI PE 能力模型的最终公式</h3>
            <div class="formula-content">
              AI PE = 产品经理的业务理解<br/>
              + 架构师的抽象能力<br/>
              + 初级工程师的代码理解<br/>
              + AI 工程师的工具能力
            </div>
            <p>完全不是传统的 PM / UI / 前端哪一边的简单延伸。</p>
          </div>
        </el-card>

        <!-- 底部导航 -->
        <div class="action-section">
          <el-button @click="router.push('/role/ai-pe')">
            <el-icon class="el-icon--left"><ArrowLeft /></el-icon>
            返回 AI PE 详情
          </el-button>
          <el-button type="primary" @click="router.push('/deep-dive/ai-pe')">
            查看更多 AI PE 专题
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

const capabilities = ref([
  {
    title: '能理解业务流程（PM 出身优势）',
    subtitle: '包括：',
    points: [
      '业务抽象能力',
      '用户流程推演能力',
      '把需求拆成状态机/步骤/条件的能力',
      '找到流程边界、风险点'
    ],
    highlight: '这部分 90% 来自 <strong>PM</strong>。'
  },
  {
    title: '能把需求"结构化"，写得足够清晰让 AI 完成工作（关键能力）',
    subtitle: '不需要会代码，但要会：',
    points: [
      '变量（Variables）',
      '状态（States）',
      '输入输出（Input/Output）',
      '模块化（Modularization）',
      'API 行为（API Behavior）',
      '错误态（Error States）'
    ],
    highlight: '这就是 AI PE 的核心能力：<br/>写结构化语言，而不是写 PRD 文案'
  },
  {
    title: '能看得懂前端结构、组件、接口（中等技术能力即可）',
    subtitle: '不是要会写复杂代码，是要做到：',
    points: [
      '看得懂 React/Vue 组件',
      '知道 state / props / hooks / emit 是什么',
      '知道如何 mock API',
      '能看懂错误日志',
      '知道如何"提示 AI 去修复问题"'
    ],
    quote: '换句话说：不是把 bug 修好，而是把错误讲给 AI，让 AI 修好。'
  },
  {
    title: '能使用 AI 工具链（Claude Code / Cursor / Copilot / MCP）',
    subtitle: '这个是关键，包括：',
    points: [
      '调试 AI 工具的错误',
      '调用多个 agent',
      '分任务交给 AI',
      '与工具链（MCP、CLI、Agent）协作',
      '知道什么时候让 AI 重写、重构、重生成'
    ],
    highlight: '这叫 <strong>AI 工程心智（AI Engineering Mindset）</strong>。<br/>它更像"指挥官"，不是"码农"。'
  },
  {
    title: '强逻辑能力 & 抽象能力',
    subtitle: 'AI PE 必须能：',
    points: [
      '看到模糊需求 → 拆成结构化 tasks',
      '把混乱 UI → 抽象成组件体系',
      '把流程拆成状态机',
      '把测试拆成 rulebook',
      '把 AI 输出的 chaos → 整理成模块化 code'
    ],
    highlight: '这个能力往往来自：产品经理、算法背景、架构师、咨询顾问'
  }
])

const structuredElements = ref([
  {
    title: '变量（Variables）—— 页面中会变的东西',
    desc: '比如一个登录界面：',
    examples: ['username', 'password', 'remember_me', 'isLoading', 'errorMessage', 'apiResponse'],
    insight: '为什么 AI 需要变量？因为页面逻辑 = 变量变化。'
  },
  {
    title: '状态（States）—— 页面可能出现的形态',
    desc: '一个按钮可不是"一个按钮"，而是：',
    examples: ['default（默认状态）', 'hover（悬停状态）', 'disabled（禁用状态）', 'loading（加载中）', 'error（错误状态）', 'success（成功状态）'],
    insight: 'AI 需要你告诉它有哪些状态，否则就瞎猜。'
  },
  {
    title: '输入 & 输出（Inputs/Outputs）—— 每一步的 I/O',
    desc: '必须明确每个操作的输入和输出：',
    examples: ['用户输入 username → 更新本地 state', '用户点击 Login → 触发 API 请求', 'API 响应 200 → 跳转到首页', 'API 响应 400 → 显示错误文案'],
    insight: '你必须告诉 AI：当输入 X → 输出 Y。这样它才能写出稳定逻辑。'
  },
  {
    title: '模块化（Modularization）—— 功能拆盒子',
    desc: '比如一个产品创建页：',
    examples: ['表单区', '图片上传', '分类选择', '库存设置', '提交按钮区', 'Toast 通知区'],
    insight: 'AI 需要知道这些是不同模块，否则它会一次乱写成一大坨。'
  },
  {
    title: 'API 行为（API Behavior）—— 成功、失败、边界的规则',
    desc: '你必须告诉 AI：',
    examples: ['API 请求 body 包含哪些字段', 'API 成功 → 页面行为是什么', 'API 失败 → 哪些错误码 → 对应文案', 'API 超时 → 怎么处理', 'API 未授权 → 怎么处理'],
    insight: '否则 AI 会写一个"想象中的 API 逻辑"，与你后端不一致。'
  },
  {
    title: '错误态（Error States）—— AI 最容易忘的地方',
    desc: '比如表单：',
    examples: ['字段为空 → 显示错误文案 A', '字段不合法 → 显示错误文案 B', '网络失败 → 显示错误文案 C', '提交失败 → 显示错误文案 D', '401 → 跳登录页'],
    insight: '如果你不写，AI 一定会漏掉，导致用户报错。'
  }
])
</script>

<style scoped>
.deep-dive-page {
  min-height: 100%;
  background-color: var(--color-bg-page);
}

/* ========== Page Header ========== */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: var(--spacing-xxl) 0 var(--spacing-xl);
}

.page-header :deep(.el-breadcrumb__inner) {
  color: rgba(255, 255, 255, 0.9);
}

.page-header :deep(.el-breadcrumb__separator) {
  color: rgba(255, 255, 255, 0.6);
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

.content-section {
  margin-bottom: var(--spacing-xl);
  border-radius: var(--border-radius-lg);
  border: none;
  box-shadow: var(--shadow-base);
}

.content-section :deep(.el-card__body) {
  padding: var(--spacing-xxl);
}

.section-title {
  font-size: 24px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-xl);
  border-left: 4px solid #667eea;
  padding-left: var(--spacing-md);
}

/* ========== Definition Box ========== */
.definition-box {
  background: linear-gradient(135deg, #e0f7ff 0%, #f0f9ff 100%);
  border: 3px solid #667eea;
  border-radius: 12px;
  padding: 30px;
  margin: 20px 0;
  text-align: center;
}

.definition-box h3 {
  color: #667eea;
  margin: 0 0 15px;
  font-size: 22px;
}

.definition-box p {
  font-size: 18px;
  margin: 10px 0;
  color: #333;
}

.definition-box .formula {
  font-size: 18px;
  font-weight: 600;
  margin: 20px 0 0;
  padding: 15px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 8px;
  color: #667eea;
}

/* ========== Quote Box ========== */
.quote-box {
  background: #fff9e6;
  border-left: 4px solid #ffc107;
  padding: 20px 25px;
  margin: 20px 0;
  border-radius: 8px;
  font-size: 16px;
  line-height: 1.8;
}

/* ========== Highlight Box ========== */
.highlight-box {
  background: #f0f8ff;
  border-left: 4px solid #667eea;
  padding: 15px 20px;
  margin: 15px 0;
  border-radius: 8px;
}

.highlight-box h4 {
  margin: 0 0 10px;
  color: #667eea;
}

.highlight-box p {
  margin: 0;
}

/* ========== Stat Box ========== */
.stat-row {
  margin: 20px 0;
}

.stat-box {
  background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
  border-radius: 12px;
  padding: 25px;
  text-align: center;
  margin-bottom: 15px;
}

.stat-number {
  font-size: 48px;
  font-weight: bold;
  color: #667eea;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 10px;
}

/* ========== Capability Card ========== */
.capability-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-left: 4px solid #667eea;
  padding: 25px;
  margin: 20px 0;
  border-radius: 8px;
}

.capability-card h4 {
  margin: 0 0 15px;
  color: #667eea;
  font-size: 18px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.capability-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  font-weight: bold;
  font-size: 16px;
  flex-shrink: 0;
}

.capability-card ul {
  margin: 10px 0;
  padding-left: 20px;
}

.capability-card li {
  margin: 8px 0;
  color: #555;
}

/* ========== Skill Matrix ========== */
.skill-matrix {
  background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
  border-radius: 12px;
  padding: 30px;
  margin: 25px 0;
}

.skill-matrix h3 {
  color: #e65100;
  margin: 0 0 20px;
  text-align: center;
}

.skill-item {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 15px;
}

.skill-item.not-needed {
  border-left: 3px solid #f44336;
}

.skill-item.needed {
  border-left: 3px solid #4caf50;
}

.skill-item h5 {
  margin: 0 0 15px;
  font-size: 16px;
}

.check-icon {
  color: #4caf50;
  font-weight: bold;
}

.cross-icon {
  color: #f44336;
  font-weight: bold;
}

.skill-item ul {
  margin: 0;
  padding-left: 20px;
}

.skill-item li {
  margin: 6px 0;
  font-size: 14px;
  color: #555;
}

/* ========== Key Insight ========== */
.key-insight {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 25px;
  margin: 25px 0;
  border-radius: 12px;
  font-size: 18px;
  text-align: center;
  font-weight: 500;
  line-height: 1.8;
}

/* ========== Concept Card ========== */
.concept-card {
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 25px;
  margin: 20px 0;
}

.concept-card h4 {
  margin: 0 0 10px;
  color: #667eea;
  font-size: 18px;
}

.concept-example {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 6px;
  margin: 15px 0;
  border-left: 3px solid #667eea;
}

.concept-example ul {
  margin: 0;
  padding-left: 20px;
}

.concept-example li {
  margin: 5px 0;
  color: #555;
}

/* ========== PRD Comparison ========== */
.prd-comparison {
  background: white;
  border: 2px solid #dee2e6;
  border-radius: 12px;
  padding: 30px;
  margin: 25px 0;
}

.prd-comparison h4 {
  margin: 0 0 20px;
  text-align: center;
  padding-bottom: 15px;
  border-bottom: 2px solid #dee2e6;
}

.prd-old {
  background: #ffebee;
  padding: 20px;
  border-radius: 8px;
  margin: 15px 0;
  border-left: 4px solid #f44336;
}

.prd-old h5 {
  color: #c62828;
  margin: 0 0 10px;
}

.prd-old .problem-text {
  color: #c62828;
  font-weight: 600;
  margin-top: 15px;
}

.prd-new {
  background: #e8f5e9;
  padding: 20px;
  border-radius: 8px;
  margin: 15px 0;
  border-left: 4px solid #4caf50;
}

.prd-new h5 {
  color: #2e7d32;
  margin: 0 0 15px;
}

.spec-section {
  background: rgba(255, 255, 255, 0.7);
  padding: 12px 15px;
  margin: 10px 0;
  border-radius: 6px;
}

.spec-section h6 {
  margin: 0 0 8px;
  color: #495057;
  font-size: 14px;
}

.spec-item {
  margin: 5px 0;
  padding-left: 10px;
  color: #6c757d;
  font-size: 13px;
}

/* ========== Formula Box ========== */
.formula-box {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 35px;
  border-radius: 12px;
  text-align: center;
}

.formula-box h3 {
  color: white;
  margin: 0 0 20px;
  font-size: 22px;
}

.formula-content {
  font-size: 18px;
  font-weight: 500;
  line-height: 2;
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  margin-bottom: 15px;
}

.formula-box p {
  margin: 0;
  opacity: 0.9;
}

/* ========== Problem List ========== */
.problem-list {
  background: #fff5f5;
  padding: 20px 20px 20px 40px;
  border-radius: 8px;
  border-left: 4px solid #f44336;
}

.problem-list li {
  margin: 8px 0;
  color: #c62828;
}

/* ========== Action Section ========== */
.action-section {
  text-align: center;
  margin-top: var(--spacing-xl);
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

  .content-section :deep(.el-card__body) {
    padding: var(--spacing-lg);
  }

  .stat-number {
    font-size: 36px;
  }

  .formula-content {
    font-size: 16px;
  }
}
</style>
