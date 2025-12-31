<script setup lang="ts">
import type { Phase } from '../types'

const props = defineProps<{
  phases: Phase[]
  currentIndex: number
}>()

const emit = defineEmits<{
  (e: 'select', index: number): void
}>()

const getStatusIcon = (status: string) => {
  switch (status) {
    case 'passed': return 'CircleCheck'
    case 'current': return 'Loading'
    case 'locked': return 'Lock'
    case 'blocked': return 'CircleClose'
    case 'skipped': return 'Right'
    default: return ''
  }
}

const getStatusClass = (status: string, index: number) => {
  const classes = ['phase-tab']
  classes.push(`phase-tab--${status}`)
  if (index === props.currentIndex) {
    classes.push('phase-tab--selected')
  }
  return classes.join(' ')
}

const handleClick = (index: number, status: string) => {
  if (status !== 'locked') {
    emit('select', index)
  }
}
</script>

<template>
  <div class="phase-nav">
    <div
      v-for="(phase, index) in phases"
      :key="phase.id"
      :class="getStatusClass(phase.status, index)"
      @click="handleClick(index, phase.status)"
    >
      <div class="phase-tab__number">{{ phase.id }}</div>
      <div class="phase-tab__name">{{ phase.shortName }}</div>
      <el-icon v-if="getStatusIcon(phase.status)" class="phase-tab__icon">
        <component :is="getStatusIcon(phase.status)" />
      </el-icon>
    </div>
  </div>
</template>

<style scoped>
.phase-nav {
  display: flex;
  gap: 8px;
  padding: 8px 16px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  overflow-x: auto;
}

.phase-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 16px;
  min-width: 70px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
  position: relative;
}

.phase-tab:hover:not(.phase-tab--locked) {
  background: #f5f7fa;
}

.phase-tab--selected {
  background: #ecf5ff !important;
  border-color: #409eff;
}

.phase-tab--passed {
  border-color: #67c23a;
}

.phase-tab--passed .phase-tab__icon {
  color: #67c23a;
}

.phase-tab--current .phase-tab__icon {
  color: #409eff;
  animation: spin 1s linear infinite;
}

.phase-tab--locked {
  opacity: 0.5;
  cursor: not-allowed;
}

.phase-tab--locked .phase-tab__icon {
  color: #909399;
}

.phase-tab--blocked {
  border-color: #f56c6c;
}

.phase-tab--blocked .phase-tab__icon {
  color: #f56c6c;
}

.phase-tab--skipped {
  border-style: dashed;
  border-color: #909399;
}

.phase-tab--skipped .phase-tab__icon {
  color: #909399;
}

.phase-tab__number {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.phase-tab__name {
  font-size: 12px;
  color: #606266;
  margin-top: 2px;
}

.phase-tab__icon {
  position: absolute;
  top: 4px;
  right: 4px;
  font-size: 14px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
