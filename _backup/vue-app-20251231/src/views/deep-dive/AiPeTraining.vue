<template>
  <div class="training-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="container">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: '/deep-dive/ai-pe' }">AI PE 专题</el-breadcrumb-item>
          <el-breadcrumb-item>培训指南</el-breadcrumb-item>
        </el-breadcrumb>
        <h1 class="page-title">📚 AI PE 培训与转型指南</h1>
        <p class="page-subtitle">从传统 PM 转型为 AI PE 的完整路径，包括技能培养和实践建议</p>
      </div>
    </div>

    <div class="page-content">
      <div class="container">
        <!-- 培训目标 -->
        <el-card class="content-card" shadow="never">
          <h2 class="section-title">培训目标（OKR）</h2>

          <div class="objective-box">
            <h3>🎯 Objective</h3>
            <div class="objective-text">
              让 PM 从"写需求文档的人" → 变成"能驱动 AI 生成 Demo、UI、代码的人"
            </div>

            <h4>关键结果（Key Results）：</h4>
            <div class="kr-list">
              <div class="kr-item" v-for="kr in keyResults" :key="kr">
                {{ kr }}
              </div>
            </div>

            <p class="objective-note">这是 AI PE 的核心能力闭环</p>
          </div>
        </el-card>

        <!-- Part 1 -->
        <div class="part-divider">📅 Part 1：7天速成训练营</div>

        <!-- 速成介绍 -->
        <el-card class="content-card" shadow="never">
          <h2 class="section-title">AI PE 结构化写作训练营 · 7天版本</h2>

          <el-alert type="info" :closable="false">
            <template #title>
              <strong>核心目标</strong>
            </template>
            让 PM/UI/前端从"写 PRD/画图/写组件" → 转换为 <strong>向 AI 写结构化可执行规格</strong>的能力。
          </el-alert>

          <el-alert type="warning" :closable="false" style="margin-top: 16px;">
            <template #title>
              <strong>训练方式</strong>
            </template>
            每天一个主题 ➜ 给模版 ➜ 给练习题 ➜ 给对照答案<br/>
            每天训练 45–60 分钟
          </el-alert>

          <h3 style="margin-top: 24px;">适用人群</h3>
          <ul>
            <li>现有 PM</li>
            <li>UI 设计师</li>
            <li>前端工程师想往上走的人</li>
            <li>新人 onboarding</li>
          </ul>
        </el-card>

        <!-- 7天训练 -->
        <el-card class="content-card" shadow="never">
          <div v-for="(day, index) in trainingDays" :key="index" class="day-card">
            <div class="day-header">
              <span class="day-badge">Day {{ index + 1 }}</span>
              <h3>{{ day.title }}</h3>
            </div>

            <div class="goal-badge">🎯 目标：{{ day.goal }}</div>

            <div v-if="day.content" class="content-section">
              <h5>🧩 教学内容</h5>
              <p v-if="day.contentDesc">{{ day.contentDesc }}</p>
              <ul v-if="day.contentItems">
                <li v-for="item in day.contentItems" :key="item">{{ item }}</li>
              </ul>
            </div>

            <div class="template-section">
              <h5>📌 模板</h5>
              <pre class="template-code">{{ day.template }}</pre>
            </div>

            <div class="practice-section">
              <h5>📝 练习题</h5>
              <p>{{ day.practice }}</p>
            </div>

            <div class="answer-section">
              <h5>✔ 标准答案</h5>
              <pre class="answer-code">{{ day.answer }}</pre>
            </div>
          </div>
        </el-card>

        <!-- 7天完成后 -->
        <el-card class="content-card" shadow="never">
          <h2 class="section-title">🏆 7天训练完成后能做到什么？</h2>

          <div class="completion-badge">
            你的团队将具备：
          </div>

          <ul class="completion-list">
            <li>✅ 不写 PRD，直接写 AI 可执行的"程序规格"</li>
            <li>✅ 把需求写成结构，AI 直接生成 Demo</li>
            <li>✅ AI 生成的代码稳定、不发散</li>
            <li>✅ QA 成本大降，因为所有状态明确</li>
            <li>✅ PM/前端/UI 都能转成 AI PE</li>
          </ul>

          <div class="key-insight">这是 AI 时代最重要的基础能力</div>
        </el-card>

        <!-- Part 2 -->
        <div class="part-divider">🎓 Part 2：4周进阶课程</div>

        <!-- 进阶课程 -->
        <el-card class="content-card" shadow="never">
          <h2 class="section-title">AI PE 进阶 4 周课程（完全胜任大型项目）</h2>

          <el-alert type="info" :closable="false">
            <template #title>
              <strong>课程安排</strong>
            </template>
            每周 3 次课，每次 1 小时<br/>
            <strong>适用人群：</strong>完成7天速成的学员，希望承担模块 Owner 职责
          </el-alert>

          <div v-for="week in advancedWeeks" :key="week.week" class="week-card">
            <h4>🗓 Week {{ week.week }}：{{ week.title }}</h4>

            <h5>学习内容：</h5>
            <ul>
              <li v-for="item in week.items" :key="item">{{ item }}</li>
            </ul>

            <div class="assignment-box">
              <h5>📋 作业</h5>
              <p>{{ week.assignment }}</p>
            </div>
          </div>
        </el-card>

        <!-- 培训完成 -->
        <el-card class="content-card" shadow="never">
          <h2 class="section-title">🧾 培训完成后的 PM = AI Product Engineer</h2>

          <div class="key-insight">完整掌握 AI 时代 PM 的终极能力</div>

          <h3>核心能力清单：</h3>
          <ul class="capability-list">
            <li>✅ 写结构化规格</li>
            <li>✅ 建 UI 组件规则</li>
            <li>✅ 自己生成 demo</li>
            <li>✅ 能用 AI 修代码</li>
            <li>✅ 能定义 API 行为</li>
            <li>✅ 能写测试规则</li>
            <li>✅ 能管理模块级交付</li>
          </ul>
        </el-card>

        <!-- 评估标准 -->
        <el-card class="content-card" shadow="never">
          <h2 class="section-title">🔎 评估标准（考核体系）</h2>

          <el-row :gutter="20">
            <el-col :xs="24" :sm="12" :md="6" v-for="level in evaluationLevels" :key="level.level">
              <div class="level-card">
                <h5>Level {{ level.level }}（{{ level.name }}）</h5>
                <p class="level-desc">{{ level.desc }}</p>
                <ul>
                  <li v-for="item in level.items" :key="item">{{ item }}</li>
                </ul>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <!-- 底部导航 -->
        <div class="action-section">
          <el-button @click="router.push('/deep-dive/ai-pe-spec-template')">
            <el-icon class="el-icon--left"><ArrowLeft /></el-icon>
            返回模板库
          </el-button>
          <el-button type="primary" @click="router.push('/deep-dive/ai-spec-generation')">
            AI 自动生成 Spec
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

const keyResults = ref([
  'KR1：能把任何需求写成结构化规格（Spec）',
  'KR2：能通过 Claude Code / Cursor 生成可运行 Demo',
  'KR3：能进行基础调试（看懂错误、指挥 AI 修复）',
  'KR4：能交付完整模块（UI + 前端 demo + 后端 API 协作）',
  'KR5：能产出 Rulebook（可供 AI 自动测试）'
])

const trainingDays = ref([
  {
    title: '写变量（Variables）',
    goal: '从自然语言需求中提取"会改变的东西"，并定义变量',
    content: true,
    contentDesc: '变量通常包括：',
    contentItems: ['用户输入（input fields）', '页面状态（loading/error/success）', '数据结构（list/items）', '控制逻辑（currentStep/tab/index）'],
    template: `// 变量定义模板
变量：
- <变量名>: <类型> - <用途>`,
    practice: '需求：用户创建产品，包含名称、价格、图片、状态。\n任务：提取变量。',
    answer: `变量：
- productName: string - 产品名称
- price: number - 产品价格
- imageUrl: string - 上传后的图片链接
- status: "active" | "inactive" - 产品状态
- isSubmitting: boolean - 正在提交
- formErrors: object - 表单错误状态`
  },
  {
    title: '写状态（States）',
    goal: '把界面所有可能出现的形态列出来，让 AI 可控',
    content: true,
    contentDesc: '状态类型：',
    contentItems: ['default（默认）', 'editing（编辑中）', 'validating（验证中）', 'loading（加载中）', 'submitting（提交中）', 'success（成功）', 'error（错误）', 'empty（空状态）'],
    template: `状态：
- <状态名>: <触发条件> → <UI 呈现方式>`,
    practice: '为一个登录页面写状态。',
    answer: `状态：
- default：未输入 → 按钮 disabled
- typing：输入中 → 按钮 enabled
- submitting：点击登录 → 按钮 loading
- error：API 返回 401 → 显示错误提示
- success：API 返回 200 → 跳转首页`
  },
  {
    title: '写输入输出（Input/Output）',
    goal: '让 PM 从"文字需求" → 转成"程序化 I/O"',
    template: `输入 → 输出：
- 当 用户做 <动作> → 执行 <结果>`,
    practice: '为"创建产品"写 I/O。',
    answer: `输入 → 输出：
- 用户填写 productName → 更新本地变量
- 用户点击提交 → 调用 POST /products
- API 返回 200 → toast("成功") + 跳转列表页
- API 返回 400 → 显示字段错误
- API 超时 → toast("请稍后再试")`
  },
  {
    title: '写模块化（Modularization）',
    goal: '让 AI 产出的代码有结构，而不是大一坨',
    template: `模块拆分：
- <模块名>: <功能说明>`,
    practice: '产品创建页有哪些模块？',
    answer: `模块拆分：
- PageHeader: 页面标题 + 返回
- ProductForm: 表单区
- ImageUploader: 图片上传
- ActionBar: 保存/取消按钮
- Toast: 操作提示`
  },
  {
    title: '写 API 行为（API Behavior）',
    goal: '让 AI 与后端契约一致，不瞎猜',
    template: `API:
  路径：
  方法：
  请求体：
  返回体：
  成功处理：
  失败处理：
  超时处理：
  权限错误处理：`,
    practice: '定义产品创建 API。',
    answer: `API:
  路径：POST /products
  请求体：{ name: string, price: number, status: string }
  返回体：{ id: string }
  成功处理：toast("创建成功") + navigate('/products')
  失败处理：400 → 显示字段错误
  超时处理：toast("网络异常")
  401 处理：跳转登录页`
  },
  {
    title: '写错误态（Error States）',
    goal: '这是 AI 常漏掉的，需要 PM 教它',
    template: `错误态：
- <错误类型> → <界面展示> + <动作>`,
    practice: '为"价格输入错误"写错误态。',
    answer: `错误态：
- price 为空 → 显示 "请输入价格"
- price ≤ 0 → 显示 "价格必须大于 0"
- image 上传失败 → toast("上传失败，请重试")`
  },
  {
    title: '完整整合（写一个完整结构化规格）',
    goal: '像 AI PE 一样写一个可直接交给 AI 的规范',
    template: `【需求背景】
描述功能目标

【变量】
- <变量>: <类型> - <说明>

【状态】
- <状态>: <触发条件> → <UI表现>

【输入输出】
- 用户 <动作> → 触发 <结果>

【模块拆分】
- <模块>: <说明>

【API 行为】
path: ...
method: ...
body: ...
success: ...
error: ...

【错误态】
- <错误> → <提示>

【示例数据】
<mock data>`,
    practice: '用以上模板写一个完整的产品编辑功能 Spec。',
    answer: '（学员自行完成，讲师评审）'
  }
])

const advancedWeeks = ref([
  {
    week: 1,
    title: '组件化 / 设计系统 / Tokens',
    items: [
      '为什么 AI 一致性取决于"组件 + tokens"',
      '如何写 Component Contract',
      '如何强制 AI 使用组件库',
      '如何定义 UI 系统规则'
    ],
    assignment: '为公司组件库写一页组件规范'
  },
  {
    week: 2,
    title: 'AI Coding 编排（Orchestration）',
    items: [
      '如何让 AI 生成模块化代码',
      '如何提示 AI 重构',
      '如何让 AI 自动生成 API mock',
      '如何让 AI 自我纠错',
      '如何避免"AI 胡写"'
    ],
    assignment: '用 Claude Code 重构一个已有页面'
  },
  {
    week: 3,
    title: 'AI 驱动测试（Rulebook Testing）',
    items: [
      '如何写 Rulebook',
      '如何让 AI 自动跑测试',
      '错误态覆盖的关键',
      '成功态 + 边界态',
      '前后端联调测试'
    ],
    assignment: '为一个 CRUD 页面写完整 Rulebook'
  },
  {
    week: 4,
    title: '大型模块 Ownership（模块负责人训练）',
    items: [
      '一个模块如何拆成子模块',
      '怎么写模块级结构化规格',
      '怎么管理跨模块依赖',
      '如何做 AI code review',
      '如何与甲方对接',
      '如何控制输出一致性'
    ],
    assignment: '完成一个模块（完整交付）'
  }
])

const evaluationLevels = ref([
  {
    level: 1,
    name: '入门',
    desc: '能写结构化规格，能生成 Demo',
    items: ['掌握6大核心要素', '能独立完成小功能', '能使用 AI 工具']
  },
  {
    level: 2,
    name: '熟练',
    desc: '能调试 AI，能写组件规范',
    items: ['能处理复杂状态机', '能定义组件契约', '能优化 AI 输出']
  },
  {
    level: 3,
    name: '高级',
    desc: '能管理一个完整模块',
    items: ['能拆分子模块', '能管理依赖关系', '能产出 Rulebook']
  },
  {
    level: 4,
    name: '专家',
    desc: '能建立全项目规范 + UI 系统 + 组件库',
    items: ['能制定团队标准', '能培训新人', '能优化工作流']
  }
])
</script>

<style scoped>
.training-page {
  min-height: 100%;
  background-color: var(--color-bg-page);
}

/* ========== Page Header ========== */
.page-header {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
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
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  color: white;
  padding: var(--spacing-lg) var(--spacing-xl);
  margin: var(--spacing-xl) 0;
  border-radius: var(--border-radius-lg);
  text-align: center;
  font-size: 24px;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(17, 153, 142, 0.3);
}

/* ========== Section Title ========== */
.section-title {
  font-size: 24px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-lg);
  border-left: 4px solid #11998e;
  padding-left: var(--spacing-md);
}

/* ========== Key Insight ========== */
.key-insight {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  color: white;
  padding: var(--spacing-xl);
  margin: var(--spacing-lg) 0;
  border-radius: var(--border-radius-lg);
  font-size: 18px;
  text-align: center;
  font-weight: 500;
  line-height: 1.8;
}

/* ========== Objective Box ========== */
.objective-box {
  background: linear-gradient(135deg, #e0f7f4 0%, #f0fff4 100%);
  border: 3px solid #11998e;
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-xl);
  margin: var(--spacing-lg) 0;
}

.objective-box h3 {
  color: #0d7377;
  margin: 0 0 var(--spacing-md);
  font-size: 22px;
}

.objective-text {
  font-size: 18px;
  font-weight: 600;
  color: #0d7377;
  margin: var(--spacing-md) 0;
}

.objective-box h4 {
  color: #0d7377;
  margin: var(--spacing-lg) 0 var(--spacing-md);
}

.kr-list {
  background: white;
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
}

.kr-item {
  padding: var(--spacing-sm) var(--spacing-md);
  margin: var(--spacing-xs) 0;
  background: #f8f9fa;
  border-left: 4px solid #38ef7d;
  border-radius: var(--border-radius-sm);
}

.objective-note {
  text-align: center;
  margin-top: var(--spacing-lg);
  font-weight: 600;
  color: #0d7377;
}

/* ========== Day Card ========== */
.day-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-left: 4px solid #11998e;
  padding: var(--spacing-xl);
  margin: var(--spacing-lg) 0;
  border-radius: var(--border-radius-md);
}

.day-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.day-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  color: white;
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: 20px;
  font-weight: bold;
  font-size: 14px;
}

.day-header h3 {
  margin: 0;
  font-size: 20px;
  color: #0d7377;
}

.goal-badge {
  display: inline-block;
  background: #fff3cd;
  color: #856404;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-md);
  font-size: 14px;
  font-weight: 600;
  margin: var(--spacing-sm) 0;
}

.content-section {
  margin: var(--spacing-md) 0;
}

.content-section h5 {
  margin: 0 0 var(--spacing-sm);
  color: #0d7377;
}

.content-section ul {
  margin: 0;
  padding-left: var(--spacing-lg);
}

/* ========== Template Section ========== */
.template-section {
  margin: var(--spacing-md) 0;
}

.template-section h5 {
  margin: 0 0 var(--spacing-sm);
  color: #0d7377;
}

.template-code, .answer-code {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  margin: 0;
  overflow-x: auto;
}

/* ========== Practice Section ========== */
.practice-section {
  background: #f0f8ff;
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  margin: var(--spacing-md) 0;
  border-left: 3px solid #007aff;
}

.practice-section h5 {
  margin: 0 0 var(--spacing-sm);
  color: #0056b3;
}

.practice-section p {
  margin: 0;
  white-space: pre-wrap;
}

/* ========== Answer Section ========== */
.answer-section {
  background: #e8f5e9;
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  margin: var(--spacing-md) 0;
  border-left: 3px solid #4caf50;
}

.answer-section h5 {
  margin: 0 0 var(--spacing-sm);
  color: #2e7d32;
}

/* ========== Completion Badge ========== */
.completion-badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--border-radius-md);
  text-align: center;
  font-weight: 600;
  margin: var(--spacing-lg) 0;
}

.completion-list {
  font-size: 16px;
  padding-left: var(--spacing-lg);
}

.completion-list li {
  margin: var(--spacing-md) 0;
}

/* ========== Week Card ========== */
.week-card {
  background: white;
  border: 2px solid #dee2e6;
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-xl);
  margin: var(--spacing-lg) 0;
}

.week-card h4 {
  margin: 0 0 var(--spacing-md);
  color: #0d7377;
  border-bottom: 2px solid #e9ecef;
  padding-bottom: var(--spacing-sm);
}

.week-card h5 {
  margin: var(--spacing-md) 0 var(--spacing-sm);
  color: var(--color-text-primary);
}

.week-card ul {
  margin: 0;
  padding-left: var(--spacing-lg);
}

.assignment-box {
  background: #fff3e0;
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  margin-top: var(--spacing-md);
  border-left: 3px solid #ff9800;
}

.assignment-box h5 {
  margin: 0 0 var(--spacing-sm);
  color: #e65100;
}

.assignment-box p {
  margin: 0;
}

/* ========== Capability List ========== */
.capability-list {
  font-size: 16px;
  padding-left: var(--spacing-lg);
}

.capability-list li {
  margin: var(--spacing-md) 0;
}

/* ========== Level Card ========== */
.level-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-md);
  border-left: 4px solid #11998e;
  margin-bottom: var(--spacing-lg);
  height: calc(100% - var(--spacing-lg));
}

.level-card h5 {
  margin: 0 0 var(--spacing-sm);
  color: #0d7377;
  font-size: 16px;
}

.level-desc {
  color: var(--color-text-secondary);
  font-size: 14px;
  margin: 0 0 var(--spacing-sm);
}

.level-card ul {
  margin: 0;
  padding-left: var(--spacing-md);
  font-size: 14px;
}

.level-card li {
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

  .part-divider {
    font-size: 18px;
    padding: var(--spacing-md);
  }
}
</style>
