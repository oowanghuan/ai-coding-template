<template>
  <div class="role-header" :style="headerStyle">
    <div class="role-header-content container">
      <!-- 面包屑 -->
      <el-breadcrumb separator="/" class="role-breadcrumb">
        <el-breadcrumb-item :to="{ path: '/' }">
          <el-icon><HomeFilled /></el-icon>
          首页
        </el-breadcrumb-item>
        <el-breadcrumb-item>{{ role.title }}</el-breadcrumb-item>
      </el-breadcrumb>

      <!-- 角色信息 -->
      <div class="role-info">
        <div class="role-icon">{{ role.icon }}</div>
        <div class="role-details">
          <h1 class="role-title">{{ role.title }}</h1>
          <p class="role-tagline">{{ role.tagline }}</p>
          <div class="role-badges">
            <el-tag
              v-for="(badge, index) in role.badges"
              :key="index"
              type="info"
              effect="plain"
              size="default"
            >
              {{ badge }}
            </el-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- 装饰性渐变层 -->
    <div class="header-overlay"></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { HomeFilled } from '@element-plus/icons-vue'

const props = defineProps({
  role: {
    type: Object,
    required: true
  }
})

const headerStyle = computed(() => ({
  background: props.role.gradient || 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
}))
</script>

<style scoped>
.role-header {
  position: relative;
  padding: var(--spacing-xxl) 0 var(--spacing-xl);
  color: white;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.header-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at top right, rgba(255, 255, 255, 0.1), transparent 50%);
  pointer-events: none;
}

.role-header-content {
  position: relative;
  z-index: 1;
}

/* ========== 面包屑 ========== */
.role-breadcrumb {
  margin-bottom: var(--spacing-lg);
}

.role-breadcrumb :deep(.el-breadcrumb__inner) {
  color: rgba(255, 255, 255, 0.9);
  font-weight: var(--font-weight-medium);
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.role-breadcrumb :deep(.el-breadcrumb__inner:hover) {
  color: #fff;
}

.role-breadcrumb :deep(.el-breadcrumb__separator) {
  color: rgba(255, 255, 255, 0.6);
}

/* ========== 角色信息 ========== */
.role-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-xl);
}

.role-icon {
  font-size: 72px;
  line-height: 1;
  text-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  animation: iconFloat 3s ease-in-out infinite;
}

@keyframes iconFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.role-details {
  flex: 1;
}

.role-title {
  font-size: var(--font-size-hero);
  font-weight: var(--font-weight-bold);
  margin: 0 0 var(--spacing-sm);
  line-height: 1.2;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.role-tagline {
  font-size: var(--font-size-lg);
  margin: 0 0 var(--spacing-md);
  opacity: 0.95;
  font-weight: var(--font-weight-normal);
}

.role-badges {
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
}

.role-badges :deep(.el-tag) {
  background-color: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.3);
  color: #fff;
  backdrop-filter: blur(8px);
  font-weight: var(--font-weight-medium);
  padding: 6px 14px;
}

/* ========== 响应式 ========== */
@media (max-width: 768px) {
  .role-header {
    padding: var(--spacing-lg) 0;
  }

  .role-info {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);
  }

  .role-icon {
    font-size: 56px;
  }

  .role-title {
    font-size: var(--font-size-title);
  }

  .role-tagline {
    font-size: var(--font-size-md);
  }
}
</style>
