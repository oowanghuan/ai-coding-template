<script setup lang="ts">
/**
 * TaskCard - 简化的任务卡片组件
 * 用于显示 Feature 任务（来自 90_PROGRESS_LOG.yaml）
 */
import { computed } from 'vue'
import type { ExecutionItem } from '../types/workflow.types'

const props = defineProps<{
  task: ExecutionItem
  index: number
}>()

const emit = defineEmits<{
  (e: 'execute', task: ExecutionItem): void
  (e: 'approve', task: ExecutionItem): void
  (e: 'preview', path: string): void
}>()

// 状态配置
const statusConfig = {
  pending: { label: '待处理', type: 'info', icon: 'Clock' },
  ready: { label: '就绪', type: 'primary', icon: 'VideoPlay' },
  running: { label: '执行中', type: 'warning', icon: 'Loading' },
  generated: { label: '已生成', type: 'warning', icon: 'SuccessFilled' },
  verified: { label: '已验证', type: 'success', icon: 'CircleCheckFilled' },
  approved: { label: '已完成', type: 'success', icon: 'CircleCheckFilled' },
  failed: { label: '失败', type: 'danger', icon: 'CircleCloseFilled' },
  blocked: { label: '阻塞', type: 'info', icon: 'Lock' },
  skipped: { label: '跳过', type: 'info', icon: 'Remove' },
}

const currentStatus = computed(() => statusConfig[props.task.status] || statusConfig.pending)

const isCompleted = computed(() =>
  ['verified', 'approved', 'skipped'].includes(props.task.status)
)

const canExecute = computed(() =>
  ['pending', 'ready', 'failed'].includes(props.task.status)
)

const canApprove = computed(() =>
  props.task.status === 'generated'
)

// 获取 artifact 状态颜色
const getArtifactStatusColor = (status: string) => {
  switch (status) {
    case 'verified': return '#67c23a'
    case 'generated': return '#e6a23c'
    default: return '#909399'
  }
}
</script>

<template>
  <div class="task-card" :class="{ 'task-card--completed': isCompleted }">
    <!-- Header -->
    <div class="task-card__header">
      <div class="task-card__title">
        <span class="task-number">{{ index + 1 }}.</span>
        <span class="task-name">{{ task.name }}</span>
      </div>
      <el-tag :type="currentStatus.type as any" size="small">
        <el-icon v-if="task.status === 'running'" class="is-loading"><Loading /></el-icon>
        {{ currentStatus.label }}
      </el-tag>
    </div>

    <!-- Description -->
    <div v-if="task.description" class="task-card__desc">
      {{ task.description }}
    </div>

    <!-- Artifacts -->
    <div v-if="task.artifacts && task.artifacts.length > 0" class="task-card__artifacts">
      <div
        v-for="artifact in task.artifacts"
        :key="artifact.path"
        class="artifact-item"
        @click="emit('preview', artifact.path)"
      >
        <el-icon :color="getArtifactStatusColor(artifact.status)">
          <Document />
        </el-icon>
        <span class="artifact-path">{{ artifact.path.split('/').pop() }}</span>
      </div>
    </div>

    <!-- Actions -->
    <div class="task-card__actions">
      <el-button
        v-if="canExecute"
        size="small"
        type="primary"
        @click="emit('execute', task)"
      >
        <el-icon><VideoPlay /></el-icon>
        执行
      </el-button>
      <el-button
        v-if="canApprove"
        size="small"
        type="success"
        @click="emit('approve', task)"
      >
        <el-icon><Check /></el-icon>
        确认完成
      </el-button>
      <el-icon v-if="isCompleted" color="#67c23a" :size="20">
        <CircleCheckFilled />
      </el-icon>
    </div>
  </div>
</template>

<style scoped>
.task-card {
  background: #252a34;
  border: 1px solid #2d3748;
  border-radius: 8px;
  padding: 12px 16px;
  transition: all 0.2s;
}

.task-card:hover {
  border-color: #4a5568;
}

.task-card--completed {
  opacity: 0.7;
  background: #1e222a;
}

.task-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.task-card__title {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.task-number {
  color: #718096;
  font-size: 13px;
  font-weight: 500;
}

.task-name {
  color: #e2e8f0;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.task-card__desc {
  margin-top: 8px;
  font-size: 13px;
  color: #a0aec0;
  line-height: 1.5;
}

.task-card__artifacts {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.artifact-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: #1a1d24;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.artifact-item:hover {
  background: #2d3748;
}

.artifact-path {
  font-size: 12px;
  color: #63b3ed;
  font-family: 'Monaco', 'Menlo', monospace;
}

.task-card__actions {
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

:deep(.el-tag--small) {
  height: 22px;
  padding: 0 8px;
}
</style>
