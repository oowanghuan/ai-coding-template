<template>
  <div class="why-change-page">
    <div class="page-header">
      <div class="container">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">
            <el-icon><HomeFilled /></el-icon>
            首页
          </el-breadcrumb-item>
          <el-breadcrumb-item>为什么要变</el-breadcrumb-item>
        </el-breadcrumb>
        <h1 class="page-title">🎯 为什么要变：AI 时代的挑战</h1>
      </div>
    </div>

    <div class="page-content">
      <div class="container">
        <el-card class="content-section" shadow="never">
          <h2 class="section-title">核心问题：AI coding 带来的根本性冲突</h2>
          <p class="section-text">
            传统开发模式在 AI coding 时代遇到了根本性冲突。
            前端编码成本接近为零，但需求和规则不清晰时导致严重问题。
          </p>

          <el-alert
            title="核心矛盾"
            type="warning"
            :closable="false"
            show-icon
            class="key-insight"
          >
            <template #default>
              <p style="font-size: 18px; margin: 0;">
                真正的瓶颈不是写代码，而是<strong>把需求/UI 变成规则（Spec）</strong>。
              </p>
            </template>
          </el-alert>
        </el-card>

        <el-card class="content-section" shadow="never">
          <h2 class="section-title">AI coding 时代的5大核心问题</h2>

          <div class="problem-list">
            <div class="problem-item" v-for="(problem, index) in problems" :key="index">
              <div class="problem-header">
                <span class="problem-icon">{{ problem.icon }}</span>
                <h3 class="problem-title">{{ problem.title }}</h3>
              </div>
              <p class="problem-desc">{{ problem.description }}</p>
              <ul class="problem-details">
                <li v-for="(detail, i) in problem.details" :key="i">{{ detail }}</li>
              </ul>
            </div>
          </div>
        </el-card>

        <el-card class="content-section" shadow="never">
          <h2 class="section-title">传统模式 vs AI 时代的瓶颈</h2>

          <div class="comparison-grid">
            <div class="comparison-item old">
              <h3>❌ 传统软件瓶颈</h3>
              <ul>
                <li>前端编码慢</li>
                <li>UI 产能有限</li>
                <li>PM 需要反复协调</li>
                <li>测试要等开发完成</li>
                <li>转化时间长</li>
              </ul>
            </div>

            <div class="comparison-item new">
              <h3>✅ AI 时代新瓶颈</h3>
              <ul>
                <li>需求不清晰 → AI 输出不稳定</li>
                <li>规则不明确 → UI 发散</li>
                <li>缺少 Spec → 重复指导 AI</li>
                <li>缺少 Owner → 模块混乱</li>
                <li>Figma 成为新瓶颈</li>
              </ul>
            </div>
          </div>

          <el-alert
            type="info"
            :closable="false"
            show-icon
            class="conclusion"
          >
            <template #default>
              <p style="font-size: 16px; margin: 0;">
                <strong>关键洞察：</strong>AI 让"功能级别开发"变成快进模式，
                但"规则制定"和"模块协调"仍然必须结构化。
                从 <strong>"做不出来"</strong> 变成 <strong>"谁来保证一切一致、可控、可维护"</strong>。
              </p>
            </template>
          </el-alert>
        </el-card>

        <el-card class="content-section" shadow="never">
          <h2 class="section-title">传统流程为什么失效</h2>

          <div class="workflow-box old-workflow">
            <h4>❌ 传统流程</h4>
            <div class="workflow-steps">
              PM 只写一句需求 → UI 只画图 → 前端只写页面 → QA 最后兜底
            </div>
            <p class="workflow-note">这种流程在 AI 时代完全失效</p>
          </div>

          <div class="workflow-box new-workflow">
            <h4>✅ AI 时代需要</h4>
            <div class="workflow-steps">
              结构化 Spec → AI 生成 → 模块 Owner 负责 → 自动化测试
            </div>
            <p class="workflow-note">每个模块需要全链路 Owner</p>
          </div>
        </el-card>

        <div class="action-section">
          <el-button type="primary" size="large" @click="router.push('/team-structure')">
            查看解决方案：新团队架构
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
import { HomeFilled, ArrowRight } from '@element-plus/icons-vue'

const router = useRouter()

const problems = ref([
  {
    icon: '⚠️',
    title: 'AI 输出不稳定',
    description: '每次生成的结果不同，缺少一致性',
    details: [
      '同样的需求描述，AI 生成的代码结构差异很大',
      '组件命名、状态管理方式不统一',
      '需要反复调整 Prompt 才能得到期望结果'
    ]
  },
  {
    icon: '🎨',
    title: 'UI 发散严重',
    description: '没有统一的设计系统，组件样式混乱',
    details: [
      'AI 生成的组件不遵循设计规范',
      '颜色、间距、字体大小不一致',
      'Figma 设计稿无法完全约束 AI 输出'
    ]
  },
  {
    icon: '🔄',
    title: '重复指导 AI',
    description: 'PM、UI、前端都需要单独指导 AI，效率低下',
    details: [
      '缺少统一的 Spec 文档',
      '每个角色都在用自然语言描述需求',
      'AI 需要反复理解和调整'
    ]
  },
  {
    icon: '📦',
    title: '缺少模块 Owner',
    description: '大项目没有人对单个模块全链路负责',
    details: [
      '需求、设计、开发、测试割裂',
      '出问题时无法快速定位责任人',
      '模块之间的集成问题无人管'
    ]
  },
  {
    icon: '🎯',
    title: 'Figma 成为瓶颈',
    description: 'UI 设计师产能跟不上 AI 的开发速度',
    details: [
      'AI 可以几分钟生成 Demo，但 Figma 需要几天',
      '设计稿交付速度成为新的瓶颈',
      '需要新的设计系统来替代 Figma'
    ]
  }
])
</script>

<style scoped>
.why-change-page {
  min-height: 100%;
  background-color: var(--color-bg-page);
}

/* ========== Page Header ========== */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: var(--spacing-xxl) 0 var(--spacing-xl);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.page-header :deep(.el-breadcrumb__inner) {
  color: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.page-header :deep(.el-breadcrumb__inner:hover) {
  color: #fff;
}

.page-header :deep(.el-breadcrumb__separator) {
  color: rgba(255, 255, 255, 0.6);
}

.page-title {
  font-size: 36px;
  font-weight: var(--font-weight-bold);
  margin: var(--spacing-lg) 0 0;
  color: white;
  line-height: 1.2;
}

/* ========== Page Content ========== */
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
  font-size: var(--font-size-title);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-lg);
  line-height: 1.3;
  border-left: 4px solid var(--color-primary);
  padding-left: var(--spacing-md);
}

.section-text {
  font-size: var(--font-size-md);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  margin-bottom: var(--spacing-lg);
}

.key-insight {
  margin: var(--spacing-xl) 0;
  border-radius: var(--border-radius-base);
}

/* ========== Problem List ========== */
.problem-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.problem-item {
  background-color: var(--color-bg-light);
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-base);
  border: 2px solid var(--color-border-light);
  transition: all var(--transition-base);
}

.problem-item:hover {
  border-color: var(--color-primary-light);
  box-shadow: var(--shadow-sm);
}

.problem-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}

.problem-icon {
  font-size: 32px;
  line-height: 1;
}

.problem-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.problem-desc {
  font-size: var(--font-size-md);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-md);
  line-height: var(--line-height-base);
}

.problem-details {
  list-style: none;
  padding: 0;
  margin: 0;
}

.problem-details li {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-base);
  padding: var(--spacing-xs) 0;
  padding-left: var(--spacing-lg);
  position: relative;
}

.problem-details li::before {
  content: '▸';
  position: absolute;
  left: 0;
  color: var(--color-warning);
  font-weight: var(--font-weight-bold);
}

/* ========== Comparison Grid ========== */
.comparison-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-lg);
  margin: var(--spacing-lg) 0;
}

.comparison-item {
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-base);
  border: 2px solid;
}

.comparison-item h3 {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin-top: 0;
  margin-bottom: var(--spacing-md);
}

.comparison-item ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.comparison-item li {
  font-size: var(--font-size-md);
  line-height: var(--line-height-relaxed);
  padding: var(--spacing-xs) 0;
  padding-left: var(--spacing-lg);
  position: relative;
}

.comparison-item.old {
  background-color: #ffe5e5;
  border-color: #ff6b6b;
}

.comparison-item.old h3 {
  color: #c62828;
}

.comparison-item.old li::before {
  content: '×';
  position: absolute;
  left: 0;
  color: #c62828;
  font-weight: var(--font-weight-bold);
}

.comparison-item.new {
  background-color: #e5f9ff;
  border-color: #4dabf7;
}

.comparison-item.new h3 {
  color: #1e3c72;
}

.comparison-item.new li::before {
  content: '→';
  position: absolute;
  left: 0;
  color: #1e3c72;
  font-weight: var(--font-weight-bold);
}

.conclusion {
  margin-top: var(--spacing-xl);
  border-radius: var(--border-radius-base);
}

/* ========== Workflow Boxes ========== */
.workflow-box {
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-base);
  margin: var(--spacing-lg) 0;
  border: 2px solid;
}

.workflow-box h4 {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin: 0 0 var(--spacing-md);
  text-align: center;
}

.workflow-steps {
  font-size: var(--font-size-md);
  font-family: 'Courier New', monospace;
  text-align: center;
  padding: var(--spacing-md);
  border-radius: var(--border-radius-base);
  font-weight: var(--font-weight-medium);
  line-height: var(--line-height-relaxed);
}

.workflow-note {
  text-align: center;
  font-size: var(--font-size-sm);
  margin: var(--spacing-sm) 0 0;
  font-weight: var(--font-weight-medium);
}

.old-workflow {
  background-color: #ffebee;
  border-color: #c62828;
}

.old-workflow h4 {
  color: #c62828;
}

.old-workflow .workflow-steps {
  background-color: #ffcdd2;
  color: #b71c1c;
}

.old-workflow .workflow-note {
  color: #c62828;
}

.new-workflow {
  background-color: #e8f5e9;
  border-color: #2e7d32;
}

.new-workflow h4 {
  color: #2e7d32;
}

.new-workflow .workflow-steps {
  background-color: #c8e6c9;
  color: #1b5e20;
}

.new-workflow .workflow-note {
  color: #2e7d32;
}

/* ========== Action Section ========== */
.action-section {
  text-align: center;
  margin-top: var(--spacing-xxl);
  padding: var(--spacing-xl) 0;
}

/* ========== Responsive ========== */
@media (max-width: 768px) {
  .page-title {
    font-size: 28px;
  }

  .content-section :deep(.el-card__body) {
    padding: var(--spacing-lg);
  }

  .comparison-grid {
    grid-template-columns: 1fr;
  }
}
</style>
