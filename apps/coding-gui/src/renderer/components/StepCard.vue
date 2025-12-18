<script setup lang="ts">
import { computed, ref } from 'vue'
import type { StepCardProps, StepStatus } from '../types'
import LogDrawer from './LogDrawer.vue'

const props = defineProps<StepCardProps>()

const emit = defineEmits<{
  (e: 'execute', stepId: string): void
  (e: 'openCli', stepId: string): void
  (e: 'refresh', stepId: string): void
  (e: 'approve', stepId: string): void
  (e: 'preview', path: string): void
  (e: 'viewChangelog', path: string): void
  (e: 'toggleLog', stepId: string): void
}>()

const statusConfig: Record<StepStatus, { label: string; type: string; icon: string }> = {
  pending: { label: '待执行', type: 'info', icon: 'Clock' },
  running: { label: '执行中...', type: 'primary', icon: 'Loading' },
  generated: { label: '已生成', type: 'warning', icon: 'SuccessFilled' },
  failed: { label: '执行失败', type: 'danger', icon: 'CircleCloseFilled' },
  approved: { label: '已通过', type: 'success', icon: 'CircleCheckFilled' }
}

const currentStatus = computed(() => statusConfig[props.status])

const canExecute = computed(() => {
  if (props.isLocked) return false
  if (props.status === 'running') return false
  return true
})

const canApprove = computed(() => {
  return props.status === 'generated'
})

const executeButtonText = computed(() => {
  if (props.status === 'running') return '执行中...'
  if (props.status === 'generated') return '重跑'
  if (props.status === 'failed') return '重试'
  if (props.status === 'approved') return '解锁重跑'
  return '执行'
})

const getArtifactStatusIcon = (status: string) => {
  switch (status) {
    case 'verified': return 'CircleCheckFilled'
    case 'generated': return 'SuccessFilled'
    default: return 'Clock'
  }
}

const getArtifactStatusColor = (status: string) => {
  switch (status) {
    case 'verified': return '#67c23a'
    case 'generated': return '#e6a23c'
    default: return '#909399'
  }
}

const showApproveDialog = ref(false)
const approverName = ref('developer@example.com')
const approverRole = ref('Developer')
const approveNote = ref('')

const handleApprove = () => {
  showApproveDialog.value = true
}

const confirmApprove = () => {
  emit('approve', props.stepId)
  showApproveDialog.value = false
}
</script>

<template>
  <el-card class="step-card" :class="{ 'step-card--locked': isLocked }">
    <!-- Header -->
    <template #header>
      <div class="step-card__header">
        <div class="step-card__title">
          <el-icon class="step-card__status-icon" :style="{ color: currentStatus.type === 'info' ? '#909399' : '' }">
            <component :is="currentStatus.icon" :class="{ 'is-loading': status === 'running' }" />
          </el-icon>
          <span>Step {{ stepNumber }}: {{ title }}</span>
        </div>
        <el-tag :type="currentStatus.type as any" size="small">
          {{ currentStatus.label }}
        </el-tag>
      </div>
    </template>

    <!-- Body -->
    <div class="step-card__body">
      <!-- Interactions -->
      <div class="step-card__interactions">
        <div
          v-for="(interaction, index) in interactions"
          :key="index"
          class="interaction-item"
        >
          <span class="interaction-actor">
            {{ interaction.actor === 'human' ? '你' : 'CC' }}
          </span>
          <span class="interaction-action">{{ interaction.action }}</span>
        </div>
      </div>

      <!-- Artifacts -->
      <div v-if="artifacts.length > 0" class="step-card__artifacts">
        <div class="artifacts-header">
          <el-icon><Folder /></el-icon>
          <span class="artifacts-title">交付物</span>
        </div>
        <div
          v-for="artifact in artifacts"
          :key="artifact.path"
          class="artifact-item"
        >
          <el-icon :style="{ color: getArtifactStatusColor(artifact.status) }">
            <component :is="getArtifactStatusIcon(artifact.status)" />
          </el-icon>
          <span class="artifact-path">{{ artifact.path }}</span>
          <div class="artifact-actions">
            <el-tag
              v-if="artifact.status !== 'pending'"
              size="small"
              type="info"
              class="version-tag"
            >
              v1
            </el-tag>
            <el-button
              v-if="artifact.canPreview && artifact.status !== 'pending'"
              size="small"
              text
              type="primary"
              @click="emit('preview', artifact.path)"
            >
              查看
            </el-button>
            <el-button
              v-if="artifact.status !== 'pending'"
              size="small"
              text
              type="primary"
              @click="emit('viewChangelog', artifact.path)"
            >
              变更记录
            </el-button>
            <el-tag v-if="artifact.status === 'pending'" size="small" type="info">
              待生成
            </el-tag>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="step-card__footer">
      <div class="step-card__actions">
        <el-button
          type="primary"
          :disabled="!canExecute"
          :loading="status === 'running'"
          @click="emit('execute', stepId)"
        >
          <el-icon v-if="status !== 'running'"><VideoPlay /></el-icon>
          {{ executeButtonText }}
        </el-button>
        <el-button
          :disabled="isLocked || status === 'running'"
          @click="emit('openCli', stepId)"
        >
          <el-icon><FolderOpened /></el-icon>
          打开 CLI
        </el-button>
        <el-button
          :disabled="status === 'running'"
          @click="emit('refresh', stepId)"
        >
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
      <el-button
        v-if="canApprove"
        type="success"
        @click="handleApprove"
      >
        <el-icon><Check /></el-icon>
        通过
      </el-button>
      <el-tag v-else-if="status === 'approved'" type="success">
        <el-icon><CircleCheckFilled /></el-icon>
        已通过
      </el-tag>
    </div>

    <!-- Log Toggle -->
    <div v-if="logs.length > 0" class="step-card__log-toggle">
      <el-button text type="info" @click="emit('toggleLog', stepId)">
        <el-icon>
          <component :is="isLogExpanded ? 'ArrowUp' : 'ArrowDown'" />
        </el-icon>
        {{ isLogExpanded ? '收起日志' : '展开日志' }} ({{ logs.length }} 行)
      </el-button>
    </div>

    <!-- Log Drawer -->
    <LogDrawer
      v-if="isLogExpanded"
      :logs="logs"
      :step-id="stepId"
    />

    <!-- Approve Dialog -->
    <el-dialog
      v-model="showApproveDialog"
      title="确认通过此步骤"
      width="500"
    >
      <el-form label-position="top">
        <el-form-item label="审批人">
          <el-input v-model="approverName" disabled />
        </el-form-item>
        <el-form-item label="审批角色">
          <el-select v-model="approverRole" style="width: 100%">
            <el-option label="Developer" value="Developer" />
            <el-option label="PM" value="PM" />
            <el-option label="Architect" value="Architect" />
            <el-option label="QA" value="QA" />
          </el-select>
        </el-form-item>
        <el-form-item label="审批备注（可选）">
          <el-input
            v-model="approveNote"
            type="textarea"
            :rows="3"
            placeholder="添加审批备注..."
          />
        </el-form-item>
      </el-form>
      <el-alert
        type="warning"
        :closable="false"
        show-icon
      >
        此操作将记录到审批日志，且不可撤销
      </el-alert>
      <template #footer>
        <el-button @click="showApproveDialog = false">取消</el-button>
        <el-button type="success" @click="confirmApprove">
          <el-icon><Check /></el-icon>
          确认通过
        </el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<style scoped>
.step-card {
  margin-bottom: 16px;
}

.step-card--locked {
  opacity: 0.6;
}

.step-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.step-card__title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
}

.step-card__status-icon {
  font-size: 20px;
}

.step-card__status-icon .is-loading {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.step-card__body {
  margin-bottom: 16px;
}

.step-card__interactions {
  margin-bottom: 16px;
}

.interaction-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 6px 0;
  font-size: 14px;
}

.interaction-actor {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 24px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  background: #f0f2f5;
  color: #606266;
}

.interaction-item:nth-child(odd) .interaction-actor {
  background: #ecf5ff;
  color: #409eff;
}

.interaction-action {
  color: #606266;
}

.step-card__artifacts {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 12px;
}

.artifacts-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 10px;
  color: #606266;
}

.artifacts-title {
  font-size: 13px;
  font-weight: 500;
  color: #606266;
}

.artifact-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: #fff;
  border-radius: 6px;
  margin-bottom: 6px;
}

.artifact-item:last-child {
  margin-bottom: 0;
}

.artifact-path {
  flex: 1;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
  color: #303133;
}

.artifact-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.version-tag {
  font-family: monospace;
}

.step-card__footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
}

.step-card__actions {
  display: flex;
  gap: 8px;
}

.step-card__log-toggle {
  margin-top: 12px;
  text-align: center;
  border-top: 1px dashed #ebeef5;
  padding-top: 8px;
}
</style>
