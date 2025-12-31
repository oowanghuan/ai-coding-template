<script setup lang="ts">
import { useExecutionEngine } from '../composables/useExecutionEngine'
import FrameworkStepCard from './FrameworkStepCard.vue'
import TaskCard from './TaskCard.vue'
import type { ExecutionItem } from '../types/workflow.types'

const props = defineProps<{
  phaseId: number
  featureId: string
}>()

const emit = defineEmits<{
  (e: 'execute', item: ExecutionItem): void
  (e: 'openTerminal', item: ExecutionItem): void
  (e: 'preview', path: string): void
  (e: 'approve', item: ExecutionItem): void
}>()

// 使用 ExecutionEngine
const {
  loading,
  error,
  beforeTaskSteps,
  featureTasks,
  afterTaskSteps,
  endSteps,
  progress,
  completedSteps,
  totalSteps,
  refresh,
} = useExecutionEngine(
  () => props.phaseId,
  () => props.featureId
)

// 处理执行
const handleExecute = (item: ExecutionItem) => {
  emit('execute', item)
}

// 处理打开终端
const handleOpenTerminal = (item: ExecutionItem) => {
  emit('openTerminal', item)
}

// 处理预览
const handlePreview = (path: string) => {
  emit('preview', path)
}

// 处理审批
const handleApprove = (item: ExecutionItem) => {
  emit('approve', item)
}
</script>

<template>
  <div class="right-panel">
    <!-- Header -->
    <div class="panel-header">
      <div class="header-title">
        <span class="title-text">执行清单</span>
        <el-tag size="small" type="info">{{ completedSteps }}/{{ totalSteps }}</el-tag>
      </div>
      <div class="header-actions">
        <el-button size="small" text @click="refresh">
          <el-icon><Refresh /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- Progress Bar -->
    <div class="progress-section">
      <el-progress
        :percentage="progress"
        :stroke-width="6"
        :show-text="false"
        color="#10b981"
      />
      <span class="progress-text">{{ progress }}% 完成</span>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载执行清单...</span>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="error-state">
      <el-icon color="#ef4444"><WarningFilled /></el-icon>
      <span>{{ error }}</span>
      <el-button size="small" @click="refresh">重试</el-button>
    </div>

    <!-- Execution List -->
    <div v-else class="execution-list">
      <!-- Before Tasks: Framework Steps -->
      <div v-if="beforeTaskSteps.length > 0" class="step-section">
        <div class="section-label">
          <el-icon><Flag /></el-icon>
          <span>开始</span>
        </div>
        <div class="step-group">
          <FrameworkStepCard
            v-for="step in beforeTaskSteps"
            :key="step.id"
            :step="step"
            @execute="handleExecute"
            @open-terminal="handleOpenTerminal"
          />
        </div>
      </div>

      <!-- Feature Tasks -->
      <div v-if="featureTasks.length > 0" class="step-section">
        <div class="section-label">
          <el-icon><List /></el-icon>
          <span>Feature 任务</span>
          <el-tag size="small" type="info">{{ featureTasks.length }} 项</el-tag>
        </div>
        <div class="step-group tasks-group">
          <TaskCard
            v-for="(task, index) in featureTasks"
            :key="task.id"
            :task="task"
            :index="index"
            @execute="handleExecute"
            @approve="handleApprove"
            @preview="handlePreview"
          />
        </div>
      </div>

      <!-- Empty Tasks Hint -->
      <div v-else class="empty-tasks">
        <el-icon><Document /></el-icon>
        <span>暂无 Feature 任务</span>
        <span class="hint-sub">任务来自 90_PROGRESS_LOG.yaml</span>
      </div>

      <!-- After Tasks: Framework Steps -->
      <div v-if="afterTaskSteps.length > 0" class="step-section">
        <div class="section-label">
          <el-icon><Finished /></el-icon>
          <span>收尾</span>
        </div>
        <div class="step-group">
          <FrameworkStepCard
            v-for="step in afterTaskSteps"
            :key="step.id"
            :step="step"
            @execute="handleExecute"
            @open-terminal="handleOpenTerminal"
          />
        </div>
      </div>

      <!-- End Steps -->
      <div v-if="endSteps.length > 0" class="step-section end-section">
        <div class="section-label">
          <el-icon><Calendar /></el-icon>
          <span>每日</span>
        </div>
        <div class="step-group">
          <FrameworkStepCard
            v-for="step in endSteps"
            :key="step.id"
            :step="step"
            @execute="handleExecute"
            @open-terminal="handleOpenTerminal"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.right-panel {
  width: var(--right-panel-width);
  background: #1a1d24;
  border-left: 1px solid #2d3748;
  display: flex;
  flex-direction: column;
  height: calc(100vh - var(--header-height) - var(--phase-nav-height));
  overflow: hidden;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid #2d3748;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-text {
  font-size: 14px;
  font-weight: 600;
  color: #f7fafc;
}

.progress-section {
  padding: 12px 16px;
  border-bottom: 1px solid #2d3748;
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-section :deep(.el-progress) {
  flex: 1;
}

.progress-text {
  font-size: 12px;
  color: #a0aec0;
  white-space: nowrap;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px 20px;
  color: #718096;
}

.error-state {
  color: #ef4444;
}

.execution-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.step-section {
  margin-bottom: 24px;
}

.step-section:last-child {
  margin-bottom: 0;
}

.section-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #718096;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px dashed #2d3748;
}

.step-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.tasks-group {
  gap: 12px;
}

.empty-tasks {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #718096;
  gap: 8px;
}

.empty-tasks .hint-sub {
  font-size: 12px;
  color: #4a5568;
}

.end-section {
  padding-top: 16px;
  border-top: 1px solid #2d3748;
}

:deep(.el-tag--small) {
  height: 20px;
  padding: 0 6px;
  font-size: 11px;
}
</style>
