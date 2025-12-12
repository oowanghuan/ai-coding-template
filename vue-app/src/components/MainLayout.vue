<template>
  <el-container class="main-layout">
    <!-- 左侧一级导航栏 -->
    <el-aside :width="isCollapsed ? '64px' : asideWidth" class="main-aside" :class="{ collapsed: isCollapsed }">
      <div class="aside-header">
        <h1 class="aside-title" v-show="!isCollapsed">AI 团队转型</h1>
        <button class="collapse-btn" @click="toggleCollapse" :title="isCollapsed ? '展开导航' : '收起导航'">
          <el-icon><component :is="isCollapsed ? 'Expand' : 'Fold'" /></el-icon>
        </button>
        <!-- User info -->
        <div class="user-info" v-if="auth.isAuthenticated.value && !isCollapsed">
          <el-dropdown trigger="click" @command="handleUserCommand">
            <div class="user-avatar-wrapper">
              <el-avatar :size="32" class="user-avatar">
                {{ auth.currentUser.value?.username?.charAt(0).toUpperCase() }}
              </el-avatar>
              <span class="user-name">{{ auth.currentUser.value?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item disabled>
                  <el-icon><User /></el-icon>
                  {{ auth.currentUser.value?.email }}
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
      <el-scrollbar class="aside-scrollbar">
        <el-menu
          :default-active="activeCategory"
          class="aside-menu"
          :router="false"
          @select="handleCategorySelect"
        >
          <el-menu-item
            v-for="category in navCategories"
            :key="category.key"
            :index="category.key"
          >
            <el-icon><component :is="category.icon" /></el-icon>
            <span>{{ category.label }}</span>
          </el-menu-item>
        </el-menu>
      </el-scrollbar>
    </el-aside>

    <!-- 右侧主内容区 -->
    <el-container class="main-container">
      <!-- 顶部二级导航 -->
      <el-header v-if="currentSubNav.length > 0" class="sub-nav-header">
        <div class="sub-nav-wrapper">
          <router-link
            v-for="item in currentSubNav"
            :key="item.path"
            :to="item.path"
            class="sub-nav-item"
            :class="{ active: route.path === item.path }"
          >
            <el-icon v-if="item.icon"><component :is="item.icon" /></el-icon>
            <span>{{ item.label }}</span>
          </router-link>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="main-content">
        <div class="content-wrapper">
          <slot />
        </div>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, watch, markRaw } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  House,
  ChatDotRound,
  Document,
  Refresh,
  User,
  Star,
  Grid,
  Brush,
  Setting,
  View,
  DataAnalysis,
  Box,
  ArrowDown,
  SwitchButton,
  Connection,
  QuestionFilled,
  VideoPlay,
  Calendar,
  Clock,
  Reading,
  UserFilled,
  Promotion,
  Share,
  Fold,
  Expand,
  Warning
} from '@element-plus/icons-vue'
import { useAuth } from '../stores/auth'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const auth = useAuth()

const asideWidth = ref('200px')
const isCollapsed = ref(false)

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}

// 导航数据结构
const navCategories = [
  {
    key: 'home',
    label: '首页',
    icon: markRaw(House),
    defaultPath: '/',
    children: []
  },
  {
    key: 'background',
    label: '了解背景',
    icon: markRaw(Reading),
    defaultPath: '/the-beginning',
    children: [
      { path: '/the-beginning', label: '一切的开始', icon: markRaw(ChatDotRound) },
      { path: '/why-change', label: '为什么要变', icon: markRaw(Document) },
      { path: '/team-structure', label: '怎么变：新架构', icon: markRaw(Refresh) }
    ]
  },
  {
    key: 'roles',
    label: '六大岗位',
    icon: markRaw(UserFilled),
    defaultPath: '/roles-overview',
    children: [
      { path: '/roles-overview', label: '岗位总览', icon: markRaw(Grid) },
      { path: '/role/pm', label: '项目经理', icon: markRaw(DataAnalysis) },
      { path: '/role/architect', label: '系统架构师', icon: markRaw(Grid) },
      { path: '/role/ai-pe', label: 'AI 产品工程师', icon: markRaw(Star) },
      { path: '/role/ui-designer', label: 'UI 规则设计师', icon: markRaw(Brush) },
      { path: '/role/backend', label: '后端工程师', icon: markRaw(Setting) },
      { path: '/role/qa', label: 'AI QA', icon: markRaw(View) }
    ]
  },
  {
    key: 'guide',
    label: '实践指南',
    icon: markRaw(Promotion),
    defaultPath: '/workflow-guide',
    children: []
  },
  {
    key: 'github',
    label: 'GitHub 专区',
    icon: markRaw(Share),
    defaultPath: '/github/concepts',
    children: [
      { path: '/github/concepts', label: '核心概念', icon: markRaw(Connection) },
      { path: '/github/simulator', label: '实操模拟', icon: markRaw(VideoPlay) },
      { path: '/github/scenario', label: '三天实战演练', icon: markRaw(Calendar) },
      { path: '/github/routine', label: '早晚课规范', icon: markRaw(Clock) }
    ]
  },
  {
    key: 'pitfall',
    label: '踩坑分享',
    icon: markRaw(Warning),
    defaultPath: '/pitfall-sharing',
    children: []
  },
  {
    key: 'dashboard',
    label: '项目看板',
    icon: markRaw(DataAnalysis),
    defaultPath: '/project-dashboard',
    children: []
  }
]

const handleUserCommand = (command) => {
  if (command === 'logout') {
    auth.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  }
}

// 根据当前路由判断所属分类
const activeCategory = computed(() => {
  const path = route.path

  if (path === '/') return 'home'
  if (path === '/the-beginning' || path === '/why-change' || path === '/team-structure') {
    return 'background'
  }
  if (path === '/roles-overview' || path.startsWith('/role/')) return 'roles'
  if (path === '/workflow-guide' || path === '/resources') return 'guide'
  if (path.startsWith('/github/')) return 'github'
  if (path === '/pitfall-sharing') return 'pitfall'
  if (path.startsWith('/project-dashboard')) return 'dashboard'

  return 'home'
})

// 获取当前分类的二级导航
const currentSubNav = computed(() => {
  const category = navCategories.find(c => c.key === activeCategory.value)
  return category?.children || []
})

// 处理一级分类点击
const handleCategorySelect = (key) => {
  const category = navCategories.find(c => c.key === key)
  if (category) {
    router.push(category.defaultPath)
  }
}

// 监听路由变化
watch(() => route.path, () => {
  // 可以在这里添加页面切换的逻辑
})
</script>

<style scoped>
.main-layout {
  height: 100vh;
  overflow: hidden;
}

/* ========== 左侧一级导航栏 ========== */
.main-aside {
  background-color: var(--color-bg-aside);
  color: #fff;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  z-index: var(--z-index-aside);
}

.aside-header {
  padding: var(--spacing-lg) var(--spacing-md);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
}

/* User info section */
.user-info {
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.user-avatar-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: var(--border-radius-base);
  cursor: pointer;
  transition: background-color var(--transition-fast);
  color: rgba(255, 255, 255, 0.9);
}

.user-avatar-wrapper:hover {
  background-color: var(--color-bg-aside-hover);
}

.user-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
}

.user-name {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.aside-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: #fff;
  margin: 0;
}

.aside-scrollbar {
  flex: 1;
  overflow: hidden;
}

.aside-scrollbar :deep(.el-scrollbar__wrap) {
  overflow-x: hidden;
}

/* ========== 一级菜单样式 ========== */
.aside-menu {
  border-right: none;
  background-color: transparent;
  padding: var(--spacing-md) 0;
}

.aside-menu :deep(.el-menu-item) {
  height: 48px;
  line-height: 48px;
  color: rgba(255, 255, 255, 0.8);
  margin: 4px var(--spacing-sm);
  border-radius: var(--border-radius-base);
  transition: all var(--transition-fast);
  font-size: 15px;
}

.aside-menu :deep(.el-menu-item:hover) {
  background-color: var(--color-bg-aside-hover);
  color: #fff;
}

.aside-menu :deep(.el-menu-item.is-active) {
  background-color: var(--color-primary);
  color: #fff;
  position: relative;
}

.aside-menu :deep(.el-menu-item.is-active)::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 24px;
  background-color: #fff;
  border-radius: 0 2px 2px 0;
}

.aside-menu :deep(.el-icon) {
  font-size: 18px;
  margin-right: var(--spacing-sm);
  transition: transform var(--transition-fast);
}

.aside-menu :deep(.el-menu-item:hover .el-icon) {
  transform: scale(1.1);
}

/* ========== 收起按钮 ========== */
.collapse-btn {
  position: absolute;
  right: 12px;
  top: 20px;
  width: 28px;
  height: 28px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.collapse-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
}

/* ========== 收起状态 ========== */
.main-aside.collapsed {
  transition: width 0.3s ease;
}

.main-aside.collapsed .aside-header {
  padding: var(--spacing-md) var(--spacing-sm);
  display: flex;
  justify-content: center;
}

.main-aside.collapsed .collapse-btn {
  position: static;
  margin: 0;
}

.main-aside.collapsed .aside-menu :deep(.el-menu-item) {
  padding: 0 !important;
  justify-content: center;
  margin: 4px 8px;
}

.main-aside.collapsed .aside-menu :deep(.el-menu-item span) {
  display: none;
}

.main-aside.collapsed .aside-menu :deep(.el-icon) {
  margin-right: 0;
  font-size: 20px;
}

/* ========== 主容器 ========== */
.main-container {
  flex-direction: column;
  overflow: hidden;
}

/* ========== 顶部二级导航 ========== */
.sub-nav-header {
  height: auto;
  padding: 0;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  z-index: 10;
}

.sub-nav-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0 24px;
  max-width: 1200px;
  margin: 0 auto;
  overflow-x: auto;
  scrollbar-width: none;
}

.sub-nav-wrapper::-webkit-scrollbar {
  display: none;
}

.sub-nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 16px 20px;
  font-size: 14px;
  color: #666;
  text-decoration: none;
  transition: all 0.2s ease;
  white-space: nowrap;
  background-color: transparent;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
}

.sub-nav-item:hover {
  color: var(--color-primary);
  background-color: rgba(64, 158, 255, 0.04);
}

.sub-nav-item.active {
  color: var(--color-primary);
  font-weight: 600;
  border-bottom-color: var(--color-primary);
  background-color: transparent;
}

.sub-nav-item .el-icon {
  font-size: 15px;
  opacity: 0.8;
}

.sub-nav-item.active .el-icon {
  opacity: 1;
}

/* ========== 右侧内容区 ========== */
.main-content {
  background-color: var(--color-bg-page);
  overflow-y: auto;
  padding: 0;
  flex: 1;
}

.content-wrapper {
  min-height: 100%;
  transition: opacity var(--transition-base), transform var(--transition-base);
  animation: contentFadeIn 0.4s ease;
}

@keyframes contentFadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ========== 响应式 ========== */
@media (max-width: 768px) {
  .main-aside {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    transform: translateX(-100%);
    transition: transform var(--transition-base);
    z-index: 1000;
  }

  .main-aside.mobile-open {
    transform: translateX(0);
  }

  .sub-nav-wrapper {
    padding: 0 12px;
  }

  .sub-nav-item {
    padding: 12px 14px;
    font-size: 13px;
  }
}
</style>
