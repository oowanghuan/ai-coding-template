<template>
  <div class="home-page">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="container">
        <div class="hero-content">
          <h1 class="hero-title">🚀 AI 时代团队转型蓝图</h1>
          <p class="hero-subtitle">从传统开发到 AI 驱动的组织变革完整指南</p>
          <p class="hero-description">
            当 AI coding 让编码成本接近为零，真正的瓶颈是什么？<br/>
            如何重构团队角色、工作流程和协作方式？<br/>
            这份文档提供从理论到实践的完整解决方案。
          </p>
          <div class="hero-buttons">
            <el-button type="primary" size="large" @click="scrollToSection('overview')">
              <el-icon class="el-icon--left"><Reading /></el-icon>
              开始了解
            </el-button>
            <el-button size="large" @click="scrollToSection('roles')">
              <el-icon class="el-icon--left"><UserFilled /></el-icon>
              查看岗位
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Part 1: 背景与总览 -->
    <div id="overview" class="content-section">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">📖 背景与总览</h2>
          <p class="section-subtitle">理解为什么要变，以及如何变革团队结构</p>
        </div>

        <el-row :gutter="24">
          <el-col :xs="24" :sm="12" :lg="6" v-for="(card, index) in overviewCards" :key="index">
            <el-card class="overview-card card-hover" shadow="hover" :body-style="{ padding: '32px' }">
              <div class="card-icon">{{ card.icon }}</div>
              <h3 class="card-title">{{ card.title }}</h3>
              <p class="card-desc">{{ card.description }}</p>
              <ul class="card-list">
                <li v-for="(item, i) in card.points" :key="i">{{ item }}</li>
              </ul>
              <el-button type="primary" text class="card-action" @click="handleCardClick(card.link)">
                查看详情
                <el-icon class="el-icon--right"><ArrowRight /></el-icon>
              </el-button>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </div>

    <!-- Part 2: 六大岗位 -->
    <div id="roles" class="roles-section">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">👥 六大核心岗位</h2>
          <p class="section-subtitle">每个岗位都有明确的职责边界、能力要求和工具箱</p>
        </div>

        <el-row :gutter="24">
          <el-col :xs="24" :sm="12" :lg="8" v-for="role in homeRoles" :key="role.id">
            <el-card
              class="role-card card-hover"
              shadow="hover"
              :body-style="{ padding: '28px' }"
              @click="goToRole(role.id)"
            >
              <div class="role-card-header">
                <div class="role-icon">{{ role.icon }}</div>
                <div class="role-badge" :style="{ background: role.color }">
                  {{ role.badge }}
                </div>
              </div>
              <h3 class="role-title" :style="{ color: role.color }">{{ role.title }}</h3>
              <p class="role-tagline">{{ role.tagline }}</p>
              <p class="role-description">{{ role.description }}</p>
              <ul class="role-highlights">
                <li v-for="(highlight, index) in role.highlights" :key="index">{{ highlight }}</li>
              </ul>
              <el-button
                type="primary"
                class="role-button"
                :style="{ background: role.color, borderColor: role.color }"
              >
                查看详情
                <el-icon class="el-icon--right"><ArrowRight /></el-icon>
              </el-button>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </div>

    <!-- Part 3: 资源与工具 -->
    <div id="resources" class="content-section">
      <div class="container">
        <div class="section-header">
          <h2 class="section-title">🛠️ 资源与工具</h2>
          <p class="section-subtitle">Prompt 模板、规范文档、自动化工具</p>
        </div>

        <el-row :gutter="24">
          <el-col :xs="24" :md="8" v-for="(resource, index) in resources" :key="index">
            <el-card class="resource-card card-hover" shadow="hover" :body-style="{ padding: '32px', textAlign: 'center' }">
              <div class="resource-icon">{{ resource.icon }}</div>
              <h3 class="card-title">{{ resource.title }}</h3>
              <p class="card-desc">{{ resource.description }}</p>
              <el-button type="primary" text class="card-action" @click="handleResourceClick(resource.link)">
                {{ resource.linkText }}
                <el-icon class="el-icon--right"><ArrowRight /></el-icon>
              </el-button>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight, Reading, UserFilled } from '@element-plus/icons-vue'

const router = useRouter()

// 六大核心岗位数据（与 RolesOverview 保持一致）
const homeRoles = ref([
  {
    id: 'pm',
    icon: '🎬',
    title: '项目经理 / Producer',
    tagline: '节奏与交付 Owner',
    badge: '节奏管理',
    color: '#06beb6',
    description: '基于「业务目标 + 架构方案」，安排"谁在什么时候把什么东西交付出来"，并持续管理依赖、风险和资源。',
    highlights: [
      '基于架构方案做项目拆解',
      '节奏与里程碑管理',
      '依赖与资源管理',
      '风险与沟通管理'
    ]
  },
  {
    id: 'architect',
    icon: '🏗️',
    title: '系统架构师',
    tagline: '技术结构与规范 Owner',
    badge: '结构设计',
    color: '#1e3c72',
    description: '负责定义系统的「技术结构和统一规范」，让所有模块、所有角色（包括 AI）都在同一套技术规则下工作。',
    highlights: [
      '系统结构设计（模块划分、数据流）',
      '公司级/项目级技术规范',
      'AI 使用与工程规则',
      '技术决策与风险评估'
    ]
  },
  {
    id: 'ai-pe',
    icon: '⭐',
    title: 'AI 产品工程师',
    tagline: '把「需求/UI → Spec → Demo → 测试场景」串成闭环的人',
    badge: '核心角色',
    color: '#667eea',
    description: '负责单个业务模块的「需求工程化」：从模糊需求 + UI 设计，到结构化 Spec、可运行 Demo 与测试场景。',
    highlights: [
      '编写结构化 Spec',
      '生成与调试前端 Demo',
      '模块级链路 Owner',
      '跨角色协调'
    ]
  },
  {
    id: 'ui-designer',
    icon: '🎨',
    title: 'UI 规则设计师',
    tagline: '设计一套「可被 AI 和开发执行」的 UI 规则系统',
    badge: 'Design System',
    color: '#f093fb',
    description: '不画单个界面，而是维护 Design System 与 UI 规则体系，让 AI 和工程人员生成风格统一的界面。',
    highlights: [
      'Design Tokens 设计',
      '组件库及状态定义',
      '编写 UI Prompt 规则',
      '审核 AI 生成的 UI'
    ]
  },
  {
    id: 'backend',
    icon: '⚙️',
    title: '后端工程师',
    tagline: '将 Spec 中定义的行为，落地为稳定可靠、可观测的后端系统',
    badge: '业务逻辑',
    color: '#11998e',
    description: '根据 Spec 和 API 行为规范，实现后端服务与数据库结构，保证正确性、性能、可维护性与可观测性。',
    highlights: [
      '实现接口与业务逻辑',
      '设计数据模型与缓存策略',
      '提供可观测性能力',
      '支持自动化测试'
    ]
  },
  {
    id: 'qa',
    icon: '🔍',
    title: 'AI QA',
    tagline: '从「手工执行用例的人」升级为「测试规则工程师」',
    badge: 'Rulebook Testing',
    color: '#ff9800',
    description: '基于 Spec 和业务规则，设计结构化测试规则（Rulebook），让 AI / 自动化工具执行大部分测试。',
    highlights: [
      '从 Spec 提取测试维度',
      '编写结构化 Rulebook',
      '搭建自动化测试管线',
      '分析测试结果与归因'
    ]
  }
])

const overviewCards = ref([
  {
    icon: '💡',
    title: '一切的开始',
    description: '一场关于 AI 时代团队变革的深度对话',
    points: [
      'AI 介入后开发流程的困惑',
      '未来岗位定位的探索',
      'ChatGPT 的深度分析与解答'
    ],
    link: '/the-beginning'
  },
  {
    icon: '🤔',
    title: '为什么要变',
    description: 'AI coding 改变了什么？团队面临什么新挑战？',
    points: [
      '编码成本趋近于零',
      '新瓶颈：需求 & 架构 & 一致性',
      '传统分工模式失效'
    ],
    link: '/why-change'
  },
  {
    icon: '🔄',
    title: '怎么变：新架构',
    description: '重构团队结构，明确新的角色定位与协作方式',
    points: [
      'AI Product Engineer 作为核心',
      '架构师前置设计',
      '6 个明确分工的岗位'
    ],
    link: '/team-structure'
  },
  {
    icon: '🤝',
    title: '角色与协作',
    description: '各岗位如何配合，确保高效产出',
    points: [
      'Kickoff 明确架构',
      'Spec + Schema 统一理解',
      '规则化降低沟通成本'
    ],
    link: '/roles-overview'
  }
])

const resources = ref([
  {
    icon: '📝',
    title: 'Prompt 模板库',
    description: '结构化 Prompt 模板，复制即用',
    linkText: '查看模板',
    link: '/resources#prompts'
  },
  {
    icon: '📐',
    title: '规范文档',
    description: 'Design System、API 规范、测试规范',
    linkText: '查看规范',
    link: '/resources#standards'
  },
  {
    icon: '🤖',
    title: '自动化工具',
    description: 'Subagent、测试脚本、代码生成器',
    linkText: '查看工具',
    link: '/resources#tools'
  }
])

const scrollToSection = (sectionId) => {
  const element = document.getElementById(sectionId)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

const handleCardClick = (link) => {
  if (link.includes('#')) {
    // 处理带哈希的路由链接，如 /resources#prompts
    const [path, hash] = link.split('#')
    if (path.startsWith('/')) {
      router.push(link)
    } else {
      // 纯哈希链接，如 #section
      scrollToSection(hash)
    }
  } else if (link.startsWith('/')) {
    router.push(link)
  } else if (link.startsWith('#')) {
    const sectionId = link.substring(1)
    scrollToSection(sectionId)
  }
}

const handleResourceClick = (link) => {
  handleCardClick(link)
}

const goToRole = (roleId) => {
  router.push(`/role/${roleId}`)
}
</script>

<style scoped>
.home-page {
  min-height: 100%;
}

/* ========== Hero Section ========== */
.hero-section {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: white;
  padding: var(--spacing-xxl) 0;
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: radial-gradient(circle, rgba(255, 255, 255, 0.1) 1px, transparent 1px);
  background-size: 30px 30px;
  opacity: 0.3;
}

.hero-content {
  position: relative;
  z-index: 1;
  text-align: center;
  max-width: 900px;
  margin: 0 auto;
}

.hero-title {
  font-size: 40px;
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-lg);
  line-height: 1.2;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.hero-subtitle {
  font-size: var(--font-size-xl);
  margin-bottom: var(--spacing-lg);
  font-weight: var(--font-weight-medium);
  opacity: 0.95;
}

.hero-description {
  font-size: var(--font-size-md);
  line-height: var(--line-height-relaxed);
  margin-bottom: var(--spacing-xl);
  opacity: 0.9;
}

.hero-buttons {
  display: flex;
  gap: var(--spacing-md);
  justify-content: center;
  flex-wrap: wrap;
}

/* ========== Content Sections ========== */
.content-section {
  padding: var(--spacing-xxl) 0;
}

.roles-section {
  background-color: #fff;
  padding: var(--spacing-xxl) 0;
}

.section-header {
  text-align: center;
  margin-bottom: var(--spacing-xxl);
}

.section-title {
  font-size: var(--font-size-hero);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-sm);
  line-height: 1.3;
}

.section-subtitle {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-normal);
}

/* ========== Cards ========== */
.overview-card,
.resource-card {
  height: 100%;
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--color-border-light);
  transition: all var(--transition-base);
  cursor: pointer;
}

.overview-card:hover,
.resource-card:hover {
  border-color: var(--color-primary);
}

.card-icon {
  font-size: 48px;
  margin-bottom: var(--spacing-md);
  line-height: 1;
}

.card-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-sm);
  line-height: 1.4;
}

.card-desc {
  font-size: var(--font-size-md);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  margin-bottom: var(--spacing-md);
}

.card-list {
  list-style: none;
  padding: 0;
  margin-bottom: var(--spacing-lg);
}

.card-list li {
  font-size: var(--font-size-md);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  padding: var(--spacing-xs) 0;
  padding-left: var(--spacing-lg);
  position: relative;
}

.card-list li::before {
  content: '▸';
  position: absolute;
  left: 0;
  color: var(--color-primary);
  font-weight: var(--font-weight-bold);
}

.card-action {
  font-weight: var(--font-weight-medium);
}

/* ========== Role Cards ========== */
.role-card {
  height: 100%;
  border-radius: var(--border-radius-lg);
  border: 2px solid var(--color-border-light);
  cursor: pointer;
  transition: all var(--transition-base);
}

.role-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--color-primary-light);
}

.role-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-md);
}

.role-icon {
  font-size: 48px;
  line-height: 1;
}

.role-badge {
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: 20px;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: white;
}

.role-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-xs);
  line-height: 1.3;
}

.role-tagline {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-md);
  line-height: var(--line-height-base);
}

.role-description {
  font-size: var(--font-size-md);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  margin-bottom: var(--spacing-md);
}

.role-highlights {
  list-style: none;
  padding: 0;
  margin: 0 0 var(--spacing-lg);
}

.role-highlights li {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-base);
  padding: var(--spacing-xs) 0;
  padding-left: var(--spacing-lg);
  position: relative;
}

.role-highlights li::before {
  content: '✓';
  position: absolute;
  left: 0;
  font-weight: var(--font-weight-bold);
  font-size: 14px;
  color: #10b981;
}

.role-button {
  width: 100%;
  font-weight: var(--font-weight-medium);
}

/* ========== Responsive ========== */
@media (max-width: 768px) {
  .hero-section {
    padding: var(--spacing-xl) 0;
  }

  .hero-title {
    font-size: 28px;
  }

  .hero-subtitle {
    font-size: var(--font-size-md);
  }

  .hero-description {
    font-size: var(--font-size-sm);
  }

  .content-section,
  .roles-section {
    padding: var(--spacing-xl) 0;
  }

  .section-title {
    font-size: var(--font-size-xxl);
  }

  .section-subtitle {
    font-size: var(--font-size-base);
  }
}
</style>
