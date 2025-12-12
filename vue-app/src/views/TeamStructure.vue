<template>
  <div class="team-structure-page">
    <div class="page-header">
      <div class="container">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">
            <el-icon><HomeFilled /></el-icon>
            首页
          </el-breadcrumb-item>
          <el-breadcrumb-item>新团队架构</el-breadcrumb-item>
        </el-breadcrumb>
        <h1 class="page-title">🔄 怎么变：新团队架构全景</h1>
      </div>
    </div>

    <div class="page-content">
      <div class="container">
        <el-card class="content-section" shadow="never">
          <h2 class="section-title">核心问题：大型项目如何划分团队？</h2>

          <el-alert
            type="success"
            :closable="false"
            show-icon
            class="key-insight"
          >
            <template #default>
              <p style="font-size: 18px; margin: 0;">
                AI 让"个人功能开发"超快，但"大型项目的组织协作"仍然必须结构化
              </p>
            </template>
          </el-alert>

          <div class="quote-box">
            <p><strong>关键洞察：</strong></p>
            <p>小功能可以 1 个人全链路完成。</p>
            <p>但大型系统仍然需要明确职责，不再是传统划分，而是基于"结构化输入"的新划分。</p>
          </div>
        </el-card>

        <el-card class="content-section" shadow="never">
          <h2 class="section-title">两种成功模式</h2>

          <div class="quote-box">
            <p>经过国内外 AI coding 团队验证（包括 Replit、Cursor、大厂内部 AI coding 团队），最终只剩下两种成功模式。</p>
          </div>

          <div class="models-grid">
            <div class="model-card small-project">
              <div class="model-badge">✅ 推荐</div>
              <h3 class="model-title">小项目模式</h3>
              <p class="model-subtitle">1 名 AI PE + AI 工具即可完成</p>

              <div class="model-content">
                <h4>适用场景</h4>
                <ul>
                  <li>单一功能模块</li>
                  <li>MVP 快速验证</li>
                  <li>内部工具开发</li>
                  <li>小型 Web 应用</li>
                </ul>

                <h4>工作流程</h4>
                <div class="workflow-steps">
                  需求 → Spec → Demo → 测试 → 上线
                </div>

                <h4>优势</h4>
                <ul>
                  <li>开发速度极快</li>
                  <li>沟通成本接近为零</li>
                  <li>不需要传统 UI / 前端 / QA</li>
                  <li>全链路一个人负责</li>
                </ul>
              </div>
            </div>

            <div class="model-card large-project">
              <div class="model-badge">🏢 企业级</div>
              <h3 class="model-title">大项目模式</h3>
              <p class="model-subtitle">模块化协作 + 全链路责任</p>

              <div class="model-content">
                <h4>适用场景</h4>
                <ul>
                  <li>大型企业系统</li>
                  <li>多模块复杂应用</li>
                  <li>需要多人协作</li>
                  <li>长期维护项目</li>
                </ul>

                <h4>组织方式</h4>
                <ul>
                  <li>按业务模块拆分（User/Product/Order...）</li>
                  <li>每个模块一个 AI PE Owner</li>
                  <li>架构师定义模块边界和规范</li>
                  <li>各模块并行开发</li>
                </ul>

                <h4>核心理念</h4>
                <div class="highlight-text">
                  每个功能模块 = 一个 AI Product Engineer 负责到底
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <el-card class="content-section" shadow="never">
          <h2 class="section-title">大型项目模块化示例</h2>

          <p class="section-text">例如一个大型项目可以拆分为以下模块，每个模块由一个 AI PE 负责：</p>

          <div class="modules-grid">
            <div class="module-item" v-for="module in modules" :key="module">
              <span class="module-icon">📦</span>
              <span class="module-name">{{ module }}</span>
            </div>
          </div>

          <el-alert
            type="info"
            :closable="false"
            show-icon
            class="mt-lg"
          >
            <template #default>
              <p style="margin: 0;">
                <strong>注意：</strong>模块 Owner 不是写所有代码，而是 orchestrate AI，
                负责全链路交付（需求理解 → UI设计 → Prompt → Demo → 代码 → 测试 → 文档）
              </p>
            </template>
          </el-alert>
        </el-card>

        <el-card class="content-section" shadow="never">
          <h2 class="section-title">六大核心角色</h2>

          <div class="roles-list">
            <div class="role-item" v-for="role in coreRoles" :key="role.id" @click="router.push(`/role/${role.id}`)">
              <div class="role-header">
                <span class="role-icon">{{ role.icon }}</span>
                <div class="role-info">
                  <h4 class="role-title">{{ role.title }}</h4>
                  <p class="role-tagline">{{ role.tagline }}</p>
                </div>
              </div>
              <p class="role-desc">{{ role.description }}</p>
            </div>
          </div>

          <div class="action-center">
            <el-button type="primary" size="large" @click="router.push('/roles-overview')">
              查看详细角色协作方式
              <el-icon class="el-icon--right"><ArrowRight /></el-icon>
            </el-button>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { HomeFilled, ArrowRight } from '@element-plus/icons-vue'

const router = useRouter()

const modules = ref([
  '用户系统',
  '权限系统',
  '产品管理',
  '订单管理',
  '风控审核',
  '多步流程',
  '仪表盘',
  '内容审核',
  '设置模块'
])

const coreRoles = ref([
  {
    id: 'pm',
    icon: '🎬',
    title: '项目经理 / Producer',
    tagline: '管节奏、管依赖、管资源',
    description: '把复杂项目拆成可并行的模块，管理依赖与风险，协调六大角色协作'
  },
  {
    id: 'architect',
    icon: '🏗️',
    title: '系统架构师',
    tagline: '规则体系设计者',
    description: '设计三层规范体系（公司级、项目级、AI使用级），确保团队在统一规则下协作'
  },
  {
    id: 'ai-pe',
    icon: '⭐',
    title: 'AI 产品工程师',
    tagline: '需求工程化核心',
    description: '把需求/UI → Spec → Demo → 测试场景串成闭环，是模块级全链路Owner'
  },
  {
    id: 'ui-designer',
    icon: '🎨',
    title: 'UI 规则设计师',
    tagline: 'Design System Owner',
    description: '设计可被AI和开发执行的UI规则系统，维护Design Tokens和组件规范'
  },
  {
    id: 'backend',
    icon: '⚙️',
    title: '后端工程师',
    tagline: '业务逻辑 Owner',
    description: '将Spec中定义的行为落地为稳定可靠、可观测的后端系统'
  },
  {
    id: 'qa',
    icon: '🔍',
    title: 'AI QA',
    tagline: '测试规则工程师',
    description: '基于Spec设计Rulebook，让AI/自动化工具执行测试，聚焦规则设计与归因'
  }
])
</script>

<style scoped>
.team-structure-page {
  min-height: 100%;
  background-color: var(--color-bg-page);
}

/* ========== Page Header ========== */
.page-header {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
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
  border-left: 4px solid #fa709a;
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

.quote-box {
  background: #fff9e6;
  border-left: 4px solid #ffc107;
  padding: var(--spacing-lg);
  margin: var(--spacing-lg) 0;
  border-radius: var(--border-radius-base);
}

.quote-box p {
  margin: var(--spacing-xs) 0;
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
}

/* ========== Models Grid ========== */
.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: var(--spacing-xl);
  margin: var(--spacing-xl) 0;
}

.model-card {
  padding: var(--spacing-xl);
  border-radius: var(--border-radius-lg);
  border: 3px solid;
  position: relative;
}

.model-badge {
  position: absolute;
  top: var(--spacing-md);
  right: var(--spacing-md);
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: 20px;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: white;
}

.model-title {
  font-size: var(--font-size-xxl);
  font-weight: var(--font-weight-semibold);
  margin: 0 0 var(--spacing-xs);
  line-height: 1.2;
}

.model-subtitle {
  font-size: var(--font-size-md);
  margin: 0 0 var(--spacing-lg);
  opacity: 0.8;
}

.model-content h4 {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  margin: var(--spacing-lg) 0 var(--spacing-sm);
  color: inherit;
}

.model-content ul {
  list-style: none;
  padding: 0;
  margin: var(--spacing-sm) 0;
}

.model-content li {
  padding: var(--spacing-xs) 0;
  padding-left: var(--spacing-lg);
  position: relative;
  line-height: var(--line-height-base);
}

.model-content li::before {
  content: '▸';
  position: absolute;
  left: 0;
  font-weight: var(--font-weight-bold);
}

.small-project {
  background-color: #e5f9ff;
  border-color: #11998e;
  color: #0d7e71;
}

.small-project .model-badge {
  background-color: #11998e;
}

.small-project li::before {
  color: #11998e;
}

.large-project {
  background-color: #f0f4ff;
  border-color: #1e3c72;
  color: #152a54;
}

.large-project .model-badge {
  background-color: #1e3c72;
}

.large-project li::before {
  color: #1e3c72;
}

.workflow-steps {
  font-family: 'Courier New', monospace;
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  text-align: center;
  padding: var(--spacing-md);
  background-color: rgba(255, 255, 255, 0.5);
  border-radius: var(--border-radius-base);
  margin: var(--spacing-sm) 0 var(--spacing-md);
}

.highlight-text {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  text-align: center;
  padding: var(--spacing-md);
  background-color: rgba(255, 255, 255, 0.5);
  border-radius: var(--border-radius-base);
  margin: var(--spacing-sm) 0;
  line-height: var(--line-height-relaxed);
}

/* ========== Modules Grid ========== */
.modules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: var(--spacing-md);
  margin: var(--spacing-lg) 0;
}

.module-item {
  background: linear-gradient(135deg, #f1f8e9 0%, #e8f5e9 100%);
  border: 2px solid #7cb342;
  border-radius: var(--border-radius-base);
  padding: var(--spacing-md);
  text-align: center;
  transition: all var(--transition-base);
  cursor: default;
}

.module-item:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.module-icon {
  font-size: 24px;
  display: block;
  margin-bottom: var(--spacing-xs);
}

.module-name {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: #558b2f;
}

.mt-lg {
  margin-top: var(--spacing-lg);
}

/* ========== Roles List ========== */
.roles-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  margin: var(--spacing-lg) 0;
}

.role-item {
  background-color: var(--color-bg-light);
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-base);
  border: 2px solid var(--color-border-light);
  transition: all var(--transition-base);
  cursor: pointer;
}

.role-item:hover {
  border-color: var(--color-primary-light);
  box-shadow: var(--shadow-sm);
  transform: translateY(-2px);
}

.role-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-sm);
}

.role-icon {
  font-size: 40px;
  line-height: 1;
}

.role-info {
  flex: 1;
}

.role-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-xs);
}

.role-tagline {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0;
}

.role-desc {
  font-size: var(--font-size-md);
  color: var(--color-text-secondary);
  line-height: var(--line-height-base);
  margin: 0;
}

.action-center {
  text-align: center;
  margin-top: var(--spacing-xxl);
}

/* ========== Responsive ========== */
@media (max-width: 768px) {
  .page-title {
    font-size: 28px;
  }

  .content-section :deep(.el-card__body) {
    padding: var(--spacing-lg);
  }

  .models-grid {
    grid-template-columns: 1fr;
  }

  .modules-grid {
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  }
}
</style>
