<template>
  <div class="hub-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="container">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: '/role/ai-pe' }">AI 产品工程师</el-breadcrumb-item>
          <el-breadcrumb-item>深入专题</el-breadcrumb-item>
        </el-breadcrumb>
        <h1 class="page-title">⭐ AI PE 深入专题</h1>
        <p class="page-subtitle">从核心能力到实战案例，全面掌握 AI 产品工程师的工作方法</p>
      </div>
    </div>

    <div class="page-content">
      <div class="container">
        <!-- 专题列表 -->
        <el-row :gutter="24">
          <el-col :xs="24" :md="12" v-for="topic in topics" :key="topic.id">
            <el-card
              class="topic-card"
              shadow="hover"
              @click="goToTopic(topic.route)"
            >
              <div class="topic-header">
                <span class="topic-icon">{{ topic.icon }}</span>
                <span class="topic-number">{{ topic.number }}</span>
              </div>
              <h3 class="topic-title">{{ topic.title }}</h3>
              <p class="topic-desc">{{ topic.description }}</p>
              <div class="topic-tags">
                <el-tag
                  v-for="tag in topic.tags"
                  :key="tag"
                  size="small"
                  effect="plain"
                >
                  {{ tag }}
                </el-tag>
              </div>
              <div class="topic-footer">
                <span class="read-time">{{ topic.readTime }}</span>
                <el-button type="primary" text>
                  阅读专题
                  <el-icon class="el-icon--right"><ArrowRight /></el-icon>
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 学习路径建议 -->
        <el-card class="learning-path" shadow="never">
          <h2 class="section-title">📚 推荐学习路径</h2>
          <div class="path-steps">
            <div class="path-step" v-for="(step, index) in learningPath" :key="index">
              <div class="step-number">{{ index + 1 }}</div>
              <div class="step-content">
                <h4>{{ step.title }}</h4>
                <p>{{ step.desc }}</p>
              </div>
              <div class="step-arrow" v-if="index < learningPath.length - 1">
                <el-icon><ArrowRight /></el-icon>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 底部导航 -->
        <div class="action-section">
          <el-button @click="router.push('/role/ai-pe')">
            <el-icon class="el-icon--left"><ArrowLeft /></el-icon>
            返回 AI PE 详情
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

const topics = ref([
  {
    id: 'capabilities',
    number: '01',
    icon: '🎯',
    title: 'AI PE 的核心能力与结构化思维',
    description: '理解 AI PE 的本质定位、5 大核心能力模型，以及结构化需求的 6 大要素。',
    tags: ['核心能力', '结构化思维', '能力模型'],
    readTime: '15 分钟',
    route: '/deep-dive/ai-pe-capabilities'
  },
  {
    id: 'examples',
    number: '02',
    icon: '💼',
    title: 'AI PE 实战案例与双模式工作流',
    description: '通过真实案例学习 AI PE 的日常工作流程，掌握 Spec 驱动和 Demo 驱动两种模式。',
    tags: ['实战案例', '工作流程', '双模式'],
    readTime: '20 分钟',
    route: '/deep-dive/ai-pe-examples'
  },
  {
    id: 'spec-template',
    number: '03',
    icon: '📋',
    title: 'AI PE 结构化需求模板库',
    description: '可直接复用的 Spec 模板、状态定义模板、API 行为模板等实用工具。',
    tags: ['模板库', 'Spec 模板', '即用工具'],
    readTime: '10 分钟',
    route: '/deep-dive/ai-pe-spec-template'
  },
  {
    id: 'training',
    number: '04',
    icon: '📖',
    title: 'AI PE 培训与转型指南',
    description: '从传统 PM 转型为 AI PE 的完整路径，包括技能培养和实践建议。',
    tags: ['转型指南', 'PM 升级', '技能培养'],
    readTime: '12 分钟',
    route: '/deep-dive/ai-pe-training'
  },
  {
    id: 'spec-generation',
    number: '05',
    icon: '🤖',
    title: 'AI 自动生成 Spec 与 Schema 标准',
    description: '如何让 AI 帮助生成规范的 Spec，以及公司级 Schema 标准的设计方法。',
    tags: ['AI 生成', 'Schema 标准', '自动化'],
    readTime: '15 分钟',
    route: '/deep-dive/ai-spec-generation'
  }
])

const learningPath = ref([
  {
    title: '理解定位',
    desc: '先学习核心能力，理解 AI PE 是什么'
  },
  {
    title: '掌握模板',
    desc: '熟悉结构化需求模板，能快速上手'
  },
  {
    title: '实战练习',
    desc: '通过案例学习，在项目中实践'
  },
  {
    title: '持续精进',
    desc: '掌握 AI 生成 Spec 等高级技能'
  }
])

const goToTopic = (route) => {
  router.push(route)
}
</script>

<style scoped>
.hub-page {
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

/* ========== Topic Card ========== */
.topic-card {
  height: 100%;
  border-radius: var(--border-radius-lg);
  cursor: pointer;
  transition: all var(--transition-base);
  margin-bottom: var(--spacing-lg);
}

.topic-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.topic-card :deep(.el-card__body) {
  padding: var(--spacing-xl);
}

.topic-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.topic-icon {
  font-size: 36px;
}

.topic-number {
  font-size: 14px;
  font-weight: 600;
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
  padding: 4px 12px;
  border-radius: 20px;
}

.topic-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-sm);
  line-height: 1.4;
}

.topic-desc {
  font-size: var(--font-size-md);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  margin: 0 0 var(--spacing-md);
}

.topic-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-xs);
  margin-bottom: var(--spacing-md);
}

.topic-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border-light);
}

.read-time {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
}

/* ========== Learning Path ========== */
.learning-path {
  margin-top: var(--spacing-xl);
  border-radius: var(--border-radius-lg);
  border: none;
  box-shadow: var(--shadow-base);
}

.learning-path :deep(.el-card__body) {
  padding: var(--spacing-xxl);
}

.section-title {
  font-size: 22px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-xl);
  border-left: 4px solid #667eea;
  padding-left: var(--spacing-md);
}

.path-steps {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.path-step {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  flex: 1;
  min-width: 200px;
}

.step-number {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  flex-shrink: 0;
}

.step-content h4 {
  margin: 0 0 var(--spacing-xs);
  font-size: var(--font-size-md);
  color: var(--color-text-primary);
}

.step-content p {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.step-arrow {
  display: flex;
  align-items: center;
  color: #667eea;
  font-size: 20px;
  margin-top: 8px;
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

  .path-steps {
    flex-direction: column;
  }

  .step-arrow {
    transform: rotate(90deg);
    margin: var(--spacing-sm) 0;
  }
}
</style>
