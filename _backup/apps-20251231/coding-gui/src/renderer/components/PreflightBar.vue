<script setup lang="ts">
import type { PreflightCheck } from '../types'

defineProps<{
  checks: PreflightCheck[]
  allPassed: boolean
}>()

const emit = defineEmits<{
  (e: 'action', checkId: string): void
}>()

const getActionText = (checkId: string) => {
  switch (checkId) {
    case 'cli': return '安装指引'
    case 'project': return '选择目录'
    case 'commands': return '初始化'
    case 'git': return 'git init'
    default: return '修复'
  }
}
</script>

<template>
  <transition name="slide">
    <div v-if="!allPassed" class="preflight-bar">
      <div class="preflight-bar__checks">
        <div
          v-for="check in checks"
          :key="check.id"
          class="check-item"
          :class="{ 'check-item--passed': check.passed, 'check-item--failed': !check.passed }"
        >
          <el-icon>
            <component :is="check.passed ? 'CircleCheckFilled' : 'CircleCloseFilled'" />
          </el-icon>
          <span class="check-label">{{ check.label }}</span>
          <el-button
            v-if="!check.passed"
            size="small"
            type="primary"
            link
            @click="emit('action', check.id)"
          >
            {{ getActionText(check.id) }}
          </el-button>
        </div>
      </div>
      <div class="preflight-bar__message">
        <el-icon><WarningFilled /></el-icon>
        请先完成上述配置，才能执行命令
      </div>
    </div>
  </transition>
</template>

<style scoped>
.preflight-bar {
  background: linear-gradient(to right, #fef0f0, #fdf6ec);
  border: 1px solid #fde2e2;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
}

.preflight-bar__checks {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 8px;
}

.check-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: white;
  border-radius: 6px;
  font-size: 13px;
}

.check-item--passed {
  color: #67c23a;
}

.check-item--failed {
  color: #f56c6c;
}

.check-label {
  color: #303133;
}

.preflight-bar__message {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #e6a23c;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}
</style>
