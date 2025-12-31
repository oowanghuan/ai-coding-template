<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { join } from 'path'
import { useProjectStore } from '../stores/project.store'
import { usePhaseStore } from '../stores/phase.store'
import { useLogStore } from '../stores/log.store'
import { useCliOutput } from '../composables/useCliOutput'
import PhaseNav from '../components/PhaseNav.vue'
import LeftPanel from '../components/LeftPanel.vue'
import RightPanel from '../components/RightPanel.vue'
import StepCard from '../components/StepCard.vue'
import PreflightBar from '../components/PreflightBar.vue'
import ArtifactPreview from '../components/ArtifactPreview.vue'
import SessionManager from '../components/SessionManager.vue'
import type { Step, PreflightCheck } from '@shared/types/project.types'
import type { ExecutionItem } from '../types/workflow.types'
import type { Session } from '../../shared/types/ipc.types'
import { githubDocService } from '../services/githubDocService'
import { useSessionChannel } from '../services/sessionChannel'

const router = useRouter()
const projectStore = useProjectStore()
const phaseStore = usePhaseStore()
const logStore = useLogStore()
const sessionChannel = useSessionChannel()

// Session 连接状态
const isSessionConnected = computed(() => sessionChannel.isConnected)
const currentProjectPath = computed(() => projectStore.currentProject?.path || null)

// ============================================================
// Preview modal state
// ============================================================
const previewVisible = ref(false)
const previewPath = ref('')
const previewContent = ref('')
const previewLoading = ref(false)

// ============================================================
// Preflight checks state
// ============================================================
const preflightChecks = ref<PreflightCheck[]>([
  { id: 'cli', name: 'CLI', description: 'Claude CLI 已安装', status: 'pending' },
  { id: 'project', name: '项目', description: '项目路径有效', status: 'pending' },
  { id: 'commands', name: 'Commands', description: 'Commands 目录存在', status: 'pending' }
])

const preflightPassed = computed(() =>
  preflightChecks.value.every(check => check.status === 'pass')
)

// ============================================================
// CLI Output subscription
// ============================================================
const { subscribe: subscribeCliOutput, unsubscribe: unsubscribeCliOutput } = useCliOutput({
  autoSubscribe: false,
  onOutput: (event) => {
    logStore.addLog({
      executionId: event.executionId,
      type: event.type,
      content: event.content,
      timestamp: event.timestamp
    })
  },
  onComplete: (executionId, exitCode) => {
    if (exitCode === 0) {
      ElMessage.success('命令执行完成')
    } else {
      ElMessage.warning(`命令执行完成，退出码: ${exitCode}`)
    }
    // Refresh project state to get updated artifacts
    projectStore.refreshState()
  }
})

// ============================================================
// Computed Properties
// ============================================================

// Map phases from store to UI format
const phases = computed(() => {
  const storePhases = phaseStore.phases
  if (!storePhases.length) {
    // Return default phases if no data loaded
    return [
      { id: 'kickoff', name: 'Kickoff', shortName: 'Kick', status: 'pending', steps: [] },
      { id: 'spec', name: 'Spec', shortName: 'Spec', status: 'pending', steps: [] },
      { id: 'demo', name: 'Demo', shortName: 'Demo', status: 'pending', steps: [] },
      { id: 'design', name: 'Design', shortName: 'Dsgn', status: 'pending', steps: [] },
      { id: 'code', name: 'Code', shortName: 'Code', status: 'pending', steps: [] },
      { id: 'test', name: 'Test', shortName: 'Test', status: 'pending', steps: [] },
      { id: 'deploy', name: 'Deploy', shortName: 'Dply', status: 'pending', steps: [] }
    ]
  }
  return storePhases.map((phase, index) => ({
    id: phase.id,
    name: phase.name,
    shortName: phase.name.slice(0, 4),
    status: mapPhaseStatusToUI(phase.status),
    steps: phase.steps.map((step, stepIndex) => mapStepToUI(step, stepIndex))
  }))
})

const currentPhaseIndex = computed(() => phaseStore.currentPhaseIndex)
const currentPhase = computed(() => phases.value[currentPhaseIndex.value] || phases.value[0])

// Phase ID 映射（与 LeftPanel 保持一致）
// phases 数组不包含 Foundation，所以需要偏移 +1
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

// 当前阶段的实际 phaseId（用于 RightPanel 和 ConfigLoader）
const currentPhaseId = computed(() => phaseIdMap[currentPhase.value?.id] ?? 1)

const projectName = computed(() =>
  projectStore.currentProject?.name || 'No Project'
)

// 检查是否选择了项目
const hasProject = computed(() => !!projectStore.currentProject)

// Feature 列表和当前 Feature
const features = computed(() => projectStore.currentProject?.features || [])
const activeFeature = computed(() => projectStore.activeFeature)
const activeFeatureId = computed(() => projectStore.currentProject?.activeFeatureId)

const handleFeatureChange = (featureId: string) => {
  projectStore.setActiveFeature(featureId)
  phaseStore.reset()
}

const completedSteps = computed(() => {
  return currentPhase.value?.steps.filter(s => s.status === 'approved').length || 0
})

const totalSteps = computed(() => {
  return currentPhase.value?.steps.length || 0
})

// ============================================================
// Helper Functions
// ============================================================

function mapPhaseStatusToUI(status: string): 'passed' | 'current' | 'pending' | 'locked' {
  switch (status) {
    case 'completed': return 'passed'
    case 'active': return 'current'
    case 'blocked': return 'locked'
    default: return 'pending'
  }
}

function mapStepToUI(step: Step, index: number) {
  return {
    stepId: step.id,
    title: step.name,
    stepNumber: index + 1,
    status: step.status,
    isLocked: step.status === 'pending' && index > 0,
    interactions: step.interactions.map(i => ({
      actor: i.actor === 'user' ? 'human' : i.actor === 'ai' ? 'cc' : i.actor,
      action: i.description
    })),
    artifacts: step.artifacts.map(a => ({
      path: a.path,
      status: a.exists ? 'verified' : 'pending',
      canPreview: true
    })),
    executionMode: step.command ? 'non_interactive' : 'interactive_handoff',
    command: step.command,
    suggestedPrompt: step.command,
    logs: logStore.getLogsForStep(step.id).map(l => l.content),
    isLogExpanded: false
  }
}

// ============================================================
// Lifecycle
// ============================================================

onMounted(async () => {
  // Subscribe to CLI output
  subscribeCliOutput()
  logStore.subscribeToCliOutput()

  // If project is open, refresh state and run preflight
  if (projectStore.currentProject) {
    await initializeWorkspace()
  }
})

onUnmounted(() => {
  unsubscribeCliOutput()
  logStore.unsubscribeFromCliOutput()
})

// Watch for project changes - only trigger on project path change
watch(() => projectStore.currentProject?.path, async (newPath, oldPath) => {
  if (newPath && newPath !== oldPath) {
    await initializeWorkspace()
  }
})

async function initializeWorkspace() {
  // Refresh project state
  await projectStore.refreshState()

  // Run preflight checks
  await runPreflightChecks()

  // Reset phase to first
  phaseStore.reset()
}

async function runPreflightChecks() {
  const projectPath = projectStore.currentProject?.path
  if (!projectPath) return

  // Check CLI
  preflightChecks.value[0].status = 'pending'
  try {
    // Simple check - try to get CLI version (we'll assume it exists if project opened)
    preflightChecks.value[0].status = 'pass'
  } catch {
    preflightChecks.value[0].status = 'fail'
  }

  // Check project path (already validated by opening)
  preflightChecks.value[1].status = 'pass'

  // Check commands directory - just mark as pass since it's optional
  // TODO: Add proper directory check IPC handler
  preflightChecks.value[2].status = 'pass'
}

// ============================================================
// Event Handlers
// ============================================================

const handlePhaseSelect = (index: number) => {
  phaseStore.setCurrentPhase(index)
}

const handleExecute = async (stepId: string) => {
  const step = currentPhase.value?.steps.find(s => s.stepId === stepId)
  if (!step || !step.command) {
    ElMessage.warning('此步骤没有可执行的命令')
    return
  }

  const projectPath = projectStore.currentProject?.path
  if (!projectPath) {
    ElMessage.error('未打开项目')
    return
  }

  // Execute using log store
  const executionId = await logStore.executeCommand(
    step.command,
    projectPath,
    stepId
  )

  if (executionId) {
    ElMessage.info('命令已开始执行')
    // Expand log for this step
    logStore.isDrawerOpen = true
  } else {
    ElMessage.error('命令执行失败')
  }
}

const handleOpenCli = async (stepId: string) => {
  const step = currentPhase.value?.steps.find(s => s.stepId === stepId)
  const projectPath = projectStore.currentProject?.path

  if (!projectPath) {
    ElMessage.error('未打开项目')
    return
  }

  // Copy suggested prompt to clipboard
  if (step?.suggestedPrompt) {
    try {
      await navigator.clipboard.writeText(step.suggestedPrompt)
      ElMessage.success('建议 prompt 已复制到剪贴板')
    } catch {
      ElMessage.warning('无法复制到剪贴板')
    }
  }

  // Try to open terminal via IPC
  try {
    await window.electronAPI.invoke('shell:openTerminal', {
      cwd: projectPath,
      prompt: step?.suggestedPrompt
    })
    ElMessage.info('正在打开终端...')
  } catch {
    // Fallback: just show message
    ElMessage.info(`请在终端中切换到: ${projectPath}`)
  }
}

const handleRefresh = async (_stepId: string) => {
  await projectStore.refreshState()
  ElMessage.success('状态已刷新')
}

const handleApprove = async (stepId: string) => {
  const result = await phaseStore.approveStep(stepId, 'approve')

  if (result) {
    ElMessage.success('步骤已通过审批')

    // Unlock next step if exists
    const steps = currentPhase.value?.steps || []
    const currentIndex = steps.findIndex(s => s.stepId === stepId)
    if (currentIndex >= 0 && currentIndex < steps.length - 1) {
      // Refresh to get updated lock status
      await projectStore.refreshState()
    }
  } else {
    ElMessage.error(phaseStore.approvalError || '审批失败')
  }
}

const handlePreview = async (path: string) => {
  const projectPath = projectStore.currentProject?.path
  if (!projectPath) {
    ElMessage.error('未打开项目')
    return
  }

  previewPath.value = path
  previewLoading.value = true
  previewVisible.value = true

  try {
    // Construct full path if relative
    const fullPath = path.startsWith('/') ? path : `${projectPath}/${path}`

    const result = await window.electronAPI.invoke('file:read', {
      path: fullPath
    })

    previewContent.value = result.content
  } catch (error: any) {
    previewContent.value = `# 无法读取文件\n\n错误: ${error.message || '未知错误'}`
    ElMessage.error(`读取文件失败: ${error.message}`)
  } finally {
    previewLoading.value = false
  }
}

const handleToggleLog = (stepId: string) => {
  logStore.toggleDrawer()
}

const handleViewUsage = (command: string) => {
  // TODO: 打开工具使用说明文档
  ElMessage.info(`查看 ${command} 使用说明`)
}

const handleGitHubPreview = async (path: string) => {
  previewPath.value = path
  previewLoading.value = true
  previewVisible.value = true

  try {
    const doc = await githubDocService.fetchDocument(path)
    previewContent.value = doc.rawContent
  } catch (error: any) {
    if (error.isNotFound) {
      previewContent.value = `# 文件未找到\n\n路径: ${path}\n\n该文件在 GitHub 仓库中不存在。`
    } else if (error.isRateLimit) {
      previewContent.value = `# API 限制\n\n请求过于频繁，请稍后再试。\n\n重置时间: ${error.resetTime || '未知'}`
    } else {
      previewContent.value = `# 加载失败\n\n错误: ${error.message || '未知错误'}\n\n路径: ${path}`
    }
    ElMessage.error(`加载文档失败: ${error.message}`)
  } finally {
    previewLoading.value = false
  }
}

const handleViewChangelog = async (path: string) => {
  // 查看变更记录 - 尝试打开对应的 CHANGELOG 文件
  const projectPath = projectStore.currentProject?.path
  if (!projectPath) {
    ElMessage.error('未打开项目')
    return
  }

  // 尝试查找对应的变更记录文件
  const changelogPath = path.replace(/\.md$/, '_CHANGELOG.md')
  handlePreview(changelogPath)
}

const handlePreflightAction = async (checkId: string) => {
  ElMessage.info(`正在修复: ${checkId}`)
  await runPreflightChecks()
}

const goToSettings = () => {
  router.push('/settings')
}

const goToProjects = () => {
  router.push('/projects')
}

// ============================================================
// RightPanel 事件处理
// ============================================================

const handleRightPanelExecute = async (item: ExecutionItem) => {
  if (!item.command) {
    ElMessage.warning('此步骤没有可执行的命令')
    return
  }

  const projectPath = projectStore.currentProject?.path
  if (!projectPath) {
    ElMessage.error('未打开项目')
    return
  }

  // 检查是否已连接 CLI Session
  if (sessionChannel.isConnected) {
    // 通过 Session 通道发送命令到 CLI
    const result = await sessionChannel.sendCommand(item.command, {
      phaseId: currentPhaseId.value,
      featureId: activeFeatureId.value || undefined,
      stepId: item.id
    })

    if (result.status === 'sent' || result.status === 'received') {
      // 命令已发送，提示用户在 CLI 中输入"执行"并回车
      ElMessage({
        message: '命令已发送，请在 CLI 中输入"执行"并回车',
        type: 'success',
        duration: 8000,
        showClose: true
      })
    } else if (result.status === 'duplicate') {
      ElMessage.info('命令已在队列中')
    } else {
      ElMessage.error(result.error || '发送命令失败')
    }
  } else {
    // 未连接时使用传统方式（启动新进程）
    const executionId = await logStore.executeCommand(
      item.command,
      projectPath,
      item.id
    )

    if (executionId) {
      ElMessage.info(`正在执行: ${item.name}`)
      logStore.isDrawerOpen = true
    } else {
      ElMessage.error('命令执行失败')
    }
  }
}

// Session 事件处理
const handleSessionConnected = (session: Session) => {
  console.log('[Workspace] Connected to session:', session.id)
}

const handleSessionDisconnected = () => {
  console.log('[Workspace] Disconnected from session')
}

const handleRightPanelOpenTerminal = async (item: ExecutionItem) => {
  const projectPath = projectStore.currentProject?.path
  if (!projectPath) {
    ElMessage.error('未打开项目')
    return
  }

  // 复制命令到剪贴板
  if (item.command) {
    try {
      await navigator.clipboard.writeText(item.command)
      ElMessage.success('命令已复制到剪贴板')
    } catch {
      ElMessage.warning('无法复制到剪贴板')
    }
  }

  // 打开终端
  try {
    await window.electronAPI.invoke('shell:openTerminal', {
      cwd: projectPath,
      prompt: item.command
    })
    ElMessage.info('正在打开终端...')
  } catch {
    ElMessage.info(`请在终端中切换到: ${projectPath}`)
  }
}

const handleRightPanelApprove = async (item: ExecutionItem) => {
  const result = await phaseStore.approveStep(item.id, 'approve')

  if (result) {
    ElMessage.success(`${item.name} 已通过审批`)
    await projectStore.refreshState()
  } else {
    ElMessage.error(phaseStore.approvalError || '审批失败')
  }
}

// ============================================================
// 日志抽屉辅助函数
// ============================================================

const getExecutionStatusType = (status: string) => {
  switch (status) {
    case 'running': return 'primary'
    case 'completed': return 'success'
    case 'failed': return 'danger'
    case 'cancelled': return 'info'
    default: return 'info'
  }
}

const formatLogTime = (timestamp: string) => {
  try {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch {
    return ''
  }
}

const copyLogs = async () => {
  const text = logStore.currentLogs.map(l => `[${formatLogTime(l.timestamp)}] ${l.content}`).join('\n')
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('日志已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败')
  }
}
</script>

<template>
  <div class="workspace">
    <!-- Header -->
    <header class="workspace__header">
      <div class="header__left">
        <div class="header__logo">
          <el-icon size="24" color="#409eff"><Monitor /></el-icon>
          <span class="header__title">Coding GUI</span>
        </div>
        <el-dropdown @command="goToProjects">
          <el-button text>
            {{ projectName }}
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item>{{ projectName }}</el-dropdown-item>
              <el-dropdown-item divided>选择其他项目...</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-divider direction="vertical" />
        <el-select
          v-if="features.length > 0"
          :model-value="activeFeatureId"
          placeholder="选择 Feature"
          size="default"
          style="width: 200px"
          @change="handleFeatureChange"
        >
          <el-option
            v-for="feature in features"
            :key="feature.id"
            :label="feature.name"
            :value="feature.id"
          />
        </el-select>
        <el-button
          v-if="activeFeature"
          text
          type="primary"
          @click="handlePreview(`docs/${activeFeatureId}/90_PROGRESS_LOG.yaml`)"
        >
          <el-icon><Document /></el-icon>
          查看 Progress Log
        </el-button>
      </div>
      <div class="header__right">
        <!-- Session 管理器 -->
        <SessionManager
          v-if="hasProject"
          :project-path="currentProjectPath"
          @connected="handleSessionConnected"
          @disconnected="handleSessionDisconnected"
        />
        <el-divider v-if="hasProject" direction="vertical" />
        <el-button text circle @click="handleRefresh('')">
          <el-icon><Refresh /></el-icon>
        </el-button>
        <el-button text circle @click="goToSettings">
          <el-icon><Setting /></el-icon>
        </el-button>
      </div>
    </header>

    <!-- 已选择项目时显示主内容 -->
    <template v-if="hasProject">
      <!-- Phase Navigation -->
      <PhaseNav
        :phases="phases"
        :current-index="currentPhaseIndex"
        @select="handlePhaseSelect"
      />

      <!-- Main Content -->
      <div class="workspace__main">
        <!-- Left Panel -->
        <LeftPanel
          :phase="currentPhase"
          :feature-id="activeFeatureId"
          @preview="handlePreview"
          @preview-git-hub="handleGitHubPreview"
          @view-usage="handleViewUsage"
        />

        <!-- Content Area: 使用 RightPanel 展示两层执行模型 -->
        <div class="workspace__content">
          <!-- Preflight Bar -->
          <PreflightBar
            :checks="preflightChecks"
            :all-passed="preflightPassed"
            @action="handlePreflightAction"
          />

          <!-- RightPanel: 框架步骤 + Feature 任务 -->
          <RightPanel
            v-if="activeFeatureId"
            :phase-id="currentPhaseId"
            :feature-id="activeFeatureId"
            @execute="handleRightPanelExecute"
            @open-terminal="handleRightPanelOpenTerminal"
            @preview="handlePreview"
            @approve="handleRightPanelApprove"
          />

          <!-- 未选择 Feature 时显示提示 -->
          <div v-else class="no-feature-hint">
            <el-empty description="请先选择一个 Feature">
              <template #image>
                <el-icon :size="64" color="#718096"><Document /></el-icon>
              </template>
            </el-empty>
          </div>
        </div>
      </div>
    </template>

    <!-- 未选择项目时显示空状态 -->
    <div v-else class="workspace__empty-state">
      <el-empty
        :image-size="200"
        description=""
      >
        <template #image>
          <el-icon :size="120" color="#c0c4cc"><FolderOpened /></el-icon>
        </template>
        <template #description>
          <div class="empty-state__content">
            <h2 class="empty-state__title">请选择一个项目</h2>
            <p class="empty-state__desc">
              选择或打开一个项目以开始使用 Coding GUI 工作流
            </p>
          </div>
        </template>
        <el-button type="primary" size="large" @click="goToProjects">
          <el-icon><FolderOpened /></el-icon>
          选择项目
        </el-button>
      </el-empty>
    </div>

    <!-- Preview Modal -->
    <ArtifactPreview
      :visible="previewVisible"
      :path="previewPath"
      :content="previewContent"
      :loading="previewLoading"
      @close="previewVisible = false"
    />

    <!-- 日志抽屉 -->
    <el-drawer
      v-model="logStore.isDrawerOpen"
      title="执行日志"
      direction="btt"
      size="40%"
      :with-header="true"
    >
      <template #header>
        <div class="log-drawer-header">
          <div class="log-drawer-title">
            <el-icon v-if="logStore.isExecuting" class="is-loading"><Loading /></el-icon>
            <el-icon v-else><Document /></el-icon>
            <span>执行日志</span>
            <el-tag v-if="logStore.currentExecution" size="small" :type="getExecutionStatusType(logStore.currentExecution.status)">
              {{ logStore.currentExecution.status }}
            </el-tag>
          </div>
          <div class="log-drawer-actions">
            <el-button size="small" text @click="copyLogs">
              <el-icon><CopyDocument /></el-icon>
              复制
            </el-button>
            <el-button size="small" text @click="logStore.clearLogs">
              <el-icon><Delete /></el-icon>
              清空
            </el-button>
          </div>
        </div>
      </template>

      <div class="log-content">
        <div v-if="logStore.currentLogs.length === 0" class="log-empty">
          <el-icon :size="48" color="#909399"><Document /></el-icon>
          <p>暂无执行日志</p>
        </div>
        <div v-else class="log-lines">
          <div
            v-for="log in logStore.currentLogs"
            :key="log.id"
            class="log-line"
            :class="`log-line--${log.type}`"
          >
            <span class="log-time">{{ formatLogTime(log.timestamp) }}</span>
            <span class="log-text">{{ log.content }}</span>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<style scoped>
.workspace {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.workspace__header {
  height: var(--header-height);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  padding-left: var(--titlebar-area-left);
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.workspace__header * {
  -webkit-app-region: no-drag;
}

.header__left {
  display: flex;
  align-items: center;
  gap: 24px;
}

.header__logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header__title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header__right {
  display: flex;
  gap: 8px;
}

.workspace__main {
  flex: 1;
  display: flex;
}

.workspace__content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  height: calc(100vh - var(--header-height) - var(--phase-nav-height));
}

.content__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.content__title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.content__steps {
  max-width: 900px;
}

/* Empty State - 未选择项目时的空状态 */
.workspace__empty-state {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  height: calc(100vh - var(--header-height));
  background: linear-gradient(180deg, #f5f7fa 0%, #fff 100%);
}

.empty-state__content {
  text-align: center;
}

.empty-state__title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.empty-state__desc {
  font-size: 14px;
  color: #909399;
  margin: 0 0 24px 0;
}

/* No Feature Hint - 未选择 Feature 时的提示 */
.no-feature-hint {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px;
}

/* Log Drawer Styles */
.log-drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.log-drawer-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
}

.log-drawer-actions {
  display: flex;
  gap: 8px;
}

.log-content {
  height: 100%;
  background: #1e1e1e;
  border-radius: 8px;
  overflow: hidden;
}

.log-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #909399;
}

.log-lines {
  padding: 16px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.6;
  max-height: calc(40vh - 80px);
  overflow-y: auto;
}

.log-line {
  display: flex;
  gap: 12px;
  padding: 2px 0;
}

.log-time {
  color: #666;
  flex-shrink: 0;
}

.log-text {
  white-space: pre-wrap;
  word-break: break-all;
}

.log-line--stdout .log-text {
  color: #e2e8f0;
}

.log-line--stderr .log-text {
  color: #f56c6c;
}

.log-line--system .log-text {
  color: #67c23a;
}

.log-line--command .log-text {
  color: #409eff;
  font-weight: 600;
}

/* Scrollbar for log content */
.log-lines::-webkit-scrollbar {
  width: 8px;
}

.log-lines::-webkit-scrollbar-track {
  background: #2d2d2d;
}

.log-lines::-webkit-scrollbar-thumb {
  background: #555;
  border-radius: 4px;
}

.log-lines::-webkit-scrollbar-thumb:hover {
  background: #666;
}
</style>
