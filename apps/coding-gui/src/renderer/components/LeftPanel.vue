<script setup lang="ts">
import { computed, toRef } from 'vue'
import { useConfigLoader } from '../composables/useConfigLoader'
import type { Phase } from '../types'

const props = defineProps<{
  phase: Phase
  featureId?: string
}>()

const emit = defineEmits<{
  (e: 'preview', path: string): void
  (e: 'previewGitHub', path: string): void
  (e: 'viewUsage', command: string): void
}>()

// 从 phase id 获取 phaseId
const phaseIdMap: Record<string, number> = {
  'foundation': 0,
  'kickoff': 1,
  'spec': 2,
  'demo': 3,
  'design': 4,
  'code': 5,
  'test': 6,
  'deploy': 7
}

const phaseId = computed(() => phaseIdMap[props.phase?.id] ?? 1)

// 使用 ConfigLoader
const {
  loading,
  error,
  objectives,
  inputs,
  references,
  tools,
  hasExpertReview,
  refresh
} = useConfigLoader(
  () => phaseId.value,
  () => props.featureId
)

// 上游输入（带状态）
const inputsWithStatus = computed(() => {
  return inputs.value.map(input => ({
    ...input,
    status: 'verified' // TODO: 从实际数据获取状态
  }))
})

// 处理预览（本地文件）
const handlePreview = (path: string) => {
  emit('preview', path)
}

// 处理 GitHub 预览
const handleGitHubPreview = (path: string) => {
  emit('previewGitHub', path)
}

// 处理 Input 预览 - 尝试多个路径
const handleInputPreview = async (paths: string[]) => {
  if (!paths || paths.length === 0) return

  // 逐个尝试路径，找到第一个存在的
  for (const path of paths) {
    emit('previewGitHub', path)
    break // 目前先简单处理，后续可以加 fallback 检测
  }
}

// 处理查看使用说明
const handleViewUsage = (tool: typeof tools.value[0]) => {
  if (tool.usage_doc) {
    emit('previewGitHub', tool.usage_doc)
  } else {
    emit('viewUsage', tool.command)
  }
}

// 处理查看源码
const handleViewSource = (tool: typeof tools.value[0]) => {
  if (tool.source_path) {
    emit('preview', tool.source_path)
  }
}

// 获取 owner 标签样式
const getOwnerTag = (owner: string) => {
  switch (owner) {
    case 'cc':
      return { label: 'CC', type: 'success' }
    case 'human':
      return { label: '人工', type: 'warning' }
    case 'hybrid':
    default:
      return { label: '协作', type: 'info' }
  }
}
</script>

<template>
  <div class="left-panel">
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载配置中...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <el-icon color="#ef4444"><WarningFilled /></el-icon>
      <span>{{ error }}</span>
      <el-button size="small" @click="refresh">重试</el-button>
    </div>

    <!-- Content -->
    <template v-else>
      <!-- Goals Section -->
      <div class="panel-section">
        <div class="section-header">
          <span class="section-icon">🎯</span>
          <span class="section-title">本阶段目标</span>
        </div>
        <ul class="goal-list">
          <li v-for="(goal, index) in objectives" :key="index">
            {{ goal }}
          </li>
        </ul>
        <div v-if="objectives.length === 0" class="empty-hint">
          暂无目标配置
        </div>
      </div>

      <!-- Inputs Section -->
      <div v-if="inputsWithStatus.length > 0" class="panel-section">
        <div class="section-header">
          <span class="section-icon">📦</span>
          <span class="section-title">上游输入</span>
          <span class="section-subtitle">（来自 Phase {{ phaseId > 0 ? phaseId - 1 : 0 }}）</span>
          <el-icon class="section-status" color="#67c23a"><CircleCheckFilled /></el-icon>
        </div>
        <div class="input-list">
          <div
            v-for="input in inputsWithStatus"
            :key="input.name"
            class="input-item"
          >
            <div class="item-main">
              <el-icon :color="input.status === 'verified' ? '#67c23a' : '#909399'">
                <CircleCheckFilled />
              </el-icon>
              <span class="item-name">{{ input.name }}</span>
              <span class="item-desc">{{ input.description }}</span>
            </div>
            <el-button
              v-if="input.paths && input.paths.length > 0"
              size="small"
              text
              type="primary"
              @click="handleInputPreview(input.paths)"
            >
              查看
            </el-button>
          </div>
        </div>
      </div>

      <!-- References Section -->
      <div v-if="references.length > 0" class="panel-section">
        <div class="section-header">
          <span class="section-icon">📄</span>
          <span class="section-title">参考文档</span>
          <span class="section-subtitle">（CC 参考模板）</span>
        </div>
        <div class="reference-list">
          <div
            v-for="ref in references"
            :key="ref.name"
            class="reference-item"
          >
            <div class="item-main">
              <span class="item-name mono">{{ ref.name }}</span>
              <span class="item-desc">{{ ref.description }}</span>
            </div>
            <el-button
              size="small"
              text
              type="primary"
              @click="handleGitHubPreview(ref.path)"
            >
              查看
            </el-button>
          </div>
        </div>
      </div>

      <!-- Tools Section -->
      <div v-if="tools.length > 0" class="panel-section">
        <div class="section-header">
          <span class="section-icon">⚡</span>
          <span class="section-title">可用工具</span>
        </div>
        <div class="tool-list">
          <div
            v-for="tool in tools"
            :key="tool.command"
            class="tool-item"
          >
            <div class="tool-header">
              <code class="tool-command">{{ tool.command }}</code>
              <div class="tool-badges">
                <el-tag size="small" type="info">{{ tool.type }}</el-tag>
                <el-tag size="small" type="warning">{{ tool.priority }}</el-tag>
                <el-tag
                  size="small"
                  :type="getOwnerTag(tool.owner).type as any"
                >
                  {{ getOwnerTag(tool.owner).label }}
                </el-tag>
                <el-tag
                  v-if="tool.status === 'implemented'"
                  size="small"
                  type="success"
                >
                  已实现
                </el-tag>
                <el-tag
                  v-else
                  size="small"
                  type="info"
                >
                  计划中
                </el-tag>
              </div>
            </div>
            <div class="tool-desc">{{ tool.description }}</div>
            <div class="tool-actions">
              <el-button
                v-if="tool.usage_doc"
                size="small"
                text
                type="primary"
                @click="handleViewUsage(tool)"
              >
                使用说明
              </el-button>
              <el-button
                v-if="tool.source_path"
                size="small"
                text
                type="primary"
                @click="handleViewSource(tool)"
              >
                查看源码
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- Expert Review Hint -->
      <div v-if="hasExpertReview" class="panel-section hint-section">
        <div class="hint-content">
          <el-icon color="#f59e0b"><WarningFilled /></el-icon>
          <span>本阶段需要专家评审后才能进入下一阶段</span>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.left-panel {
  width: var(--left-panel-width);
  background: #1a1d24;
  border-right: 1px solid #2d3748;
  padding: 16px;
  overflow-y: auto;
  height: calc(100vh - var(--header-height) - var(--phase-nav-height));
  color: #e2e8f0;
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

.panel-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #2d3748;
}

.section-icon {
  font-size: 16px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #f7fafc;
}

.section-subtitle {
  font-size: 12px;
  color: #718096;
}

.section-status {
  margin-left: auto;
}

.goal-list {
  margin: 0;
  padding-left: 24px;
}

.goal-list li {
  font-size: 13px;
  color: #a0aec0;
  margin-bottom: 6px;
  line-height: 1.5;
}

.empty-hint {
  font-size: 13px;
  color: #718096;
  font-style: italic;
  padding: 8px 0;
}

.input-list,
.reference-list,
.tool-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-item,
.reference-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  background: #252a34;
  border-radius: 6px;
  border: 1px solid #2d3748;
}

.item-main {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.item-name {
  font-size: 13px;
  color: #e2e8f0;
  font-weight: 500;
}

.item-name.mono {
  font-family: 'Monaco', 'Menlo', monospace;
  color: #63b3ed;
}

.item-desc {
  font-size: 12px;
  color: #718096;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tool-item {
  padding: 12px;
  background: #252a34;
  border-radius: 6px;
  border: 1px solid #2d3748;
}

.tool-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  flex-wrap: wrap;
  gap: 8px;
}

.tool-command {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 14px;
  color: #68d391;
  background: #1a202c;
  padding: 4px 8px;
  border-radius: 4px;
}

.tool-badges {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.tool-desc {
  font-size: 13px;
  color: #a0aec0;
  margin-bottom: 10px;
}

.tool-actions {
  display: flex;
  gap: 8px;
}

.hint-section {
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 6px;
  padding: 12px;
}

.hint-content {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #f59e0b;
}

/* Override Element Plus styles for dark theme */
:deep(.el-button--small) {
  font-size: 12px;
}

:deep(.el-tag--small) {
  height: 20px;
  padding: 0 6px;
  font-size: 11px;
}
</style>
