<script setup lang="ts">
/**
 * SessionManager 组件
 * 管理 GUI-CLI Session 连接
 */
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Session } from '../../shared/types/ipc.types'
import { useSessionChannel } from '../services/sessionChannel'

const props = defineProps<{
  projectPath: string | null
}>()

const emit = defineEmits<{
  (e: 'connected', session: Session): void
  (e: 'disconnected'): void
}>()

// Session 服务
const sessionChannel = useSessionChannel()

// 状态
const loading = ref(false)
const showDropdown = ref(false)
const sessions = computed(() => sessionChannel.allSessions.value)
const currentSession = computed(() => sessionChannel.currentSession)
const isConnected = computed(() => sessionChannel.isConnected)

// 状态图标
const getStatusIcon = (status: string) => {
  switch (status) {
    case 'active': return { icon: 'CircleCheckFilled', color: '#67c23a' }
    case 'stale': return { icon: 'WarningFilled', color: '#e6a23c' }
    case 'disconnected': return { icon: 'CircleCloseFilled', color: '#909399' }
    default: return { icon: 'QuestionFilled', color: '#909399' }
  }
}

// 状态文本
const getStatusText = (status: string) => {
  switch (status) {
    case 'active': return '活跃'
    case 'stale': return '陈旧'
    case 'disconnected': return '已断开'
    default: return '未知'
  }
}

// 终端类型文本
const getTerminalText = (type: string) => {
  switch (type) {
    case 'console': return 'Terminal'
    case 'vscode': return 'VS Code'
    case 'idea': return 'IDEA'
    default: return 'Unknown'
  }
}

// 格式化时间
const formatTime = (isoString: string) => {
  const date = new Date(isoString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 1) return '刚刚'
  if (diffMins < 60) return `${diffMins} 分钟前`

  const hours = date.getHours().toString().padStart(2, '0')
  const mins = date.getMinutes().toString().padStart(2, '0')
  return `${hours}:${mins}`
}

// 刷新 Session 列表
const refreshSessions = async () => {
  if (!props.projectPath) return

  loading.value = true
  try {
    await sessionChannel.refreshSessions()
  } catch (error) {
    console.error('Failed to refresh sessions:', error)
  } finally {
    loading.value = false
  }
}

// 连接到 Session
const connectToSession = (session: Session) => {
  if (session.status === 'disconnected') {
    ElMessage.warning('该 Session 已断开，无法连接')
    return
  }

  if (session.status === 'stale') {
    ElMessageBox.confirm(
      '该 Session 可能已失去响应，是否仍要连接？',
      '警告',
      { confirmButtonText: '连接', cancelButtonText: '取消', type: 'warning' }
    ).then(() => {
      doConnect(session)
    }).catch(() => {})
    return
  }

  doConnect(session)
}

const doConnect = (session: Session) => {
  const success = sessionChannel.connect(session.id)
  if (success) {
    ElMessage.success(`已连接到 ${session.id.slice(0, 8)}`)
    showDropdown.value = false
    emit('connected', session)
  } else {
    ElMessage.error('连接失败')
  }
}

// 断开连接
const disconnect = () => {
  sessionChannel.disconnect()
  ElMessage.info('已断开连接')
  emit('disconnected')
}

// 监听项目路径变化
watch(() => props.projectPath, async (newPath) => {
  if (newPath) {
    await sessionChannel.init(newPath)
    await refreshSessions()
  } else {
    sessionChannel.destroy()
  }
}, { immediate: true })

// 组件卸载时清理
onUnmounted(() => {
  sessionChannel.destroy()
})
</script>

<template>
  <div class="session-manager">
    <el-popover
      v-model:visible="showDropdown"
      placement="bottom-end"
      :width="340"
      trigger="click"
    >
      <template #reference>
        <el-button
          :type="isConnected ? 'success' : 'default'"
          size="small"
          :loading="loading"
        >
          <el-icon v-if="!loading">
            <component :is="isConnected ? 'Connection' : 'Link'" />
          </el-icon>
          <span v-if="isConnected && currentSession">
            {{ currentSession.id.slice(0, 8) }}
          </span>
          <span v-else>
            CLI 连接
          </span>
          <el-icon class="el-icon--right"><ArrowDown /></el-icon>
        </el-button>
      </template>

      <div class="session-popover">
        <div class="session-popover__header">
          <span class="title">CLI Sessions</span>
          <el-button
            link
            type="primary"
            size="small"
            :loading="loading"
            @click="refreshSessions"
          >
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>

        <!-- 当前连接 -->
        <div v-if="isConnected && currentSession" class="session-popover__current">
          <div class="current-label">当前连接</div>
          <div class="current-session">
            <div class="session-info">
              <el-icon :style="{ color: getStatusIcon(currentSession.status).color }">
                <component :is="getStatusIcon(currentSession.status).icon" />
              </el-icon>
              <span class="session-id">{{ currentSession.id.slice(0, 8) }}</span>
              <el-tag size="small" type="info">
                {{ getTerminalText(currentSession.terminal.type) }}
              </el-tag>
            </div>
            <el-button
              size="small"
              type="danger"
              link
              @click="disconnect"
            >
              断开
            </el-button>
          </div>
        </div>

        <!-- Session 列表 -->
        <div class="session-popover__list">
          <div class="list-label">
            可用 Sessions ({{ sessions.length }})
          </div>

          <div v-if="sessions.length === 0" class="empty-state">
            <el-icon><InfoFilled /></el-icon>
            <div class="empty-text">
              <p>没有可用的 CLI Session</p>
              <p class="empty-hint">请在 CLI 中执行 <code>/gui-connect</code></p>
            </div>
          </div>

          <div
            v-for="session in sessions"
            :key="session.id"
            class="session-item"
            :class="{
              'session-item--active': session.id === currentSession?.id,
              'session-item--stale': session.status === 'stale',
              'session-item--disconnected': session.status === 'disconnected'
            }"
            @click="connectToSession(session)"
          >
            <div class="session-item__icon">
              <el-icon :style="{ color: getStatusIcon(session.status).color }">
                <component :is="getStatusIcon(session.status).icon" />
              </el-icon>
            </div>
            <div class="session-item__info">
              <div class="session-item__main">
                <span class="session-id">session-{{ session.id.slice(0, 8) }}</span>
                <el-tag size="small" type="info">
                  {{ getTerminalText(session.terminal.type) }}
                </el-tag>
              </div>
              <div class="session-item__meta">
                <span>{{ formatTime(session.heartbeatAt) }}</span>
                <span class="status-text">{{ getStatusText(session.status) }}</span>
              </div>
            </div>
            <div
              v-if="session.id === currentSession?.id"
              class="session-item__badge"
            >
              <el-icon><Check /></el-icon>
            </div>
          </div>
        </div>

        <!-- 帮助信息 -->
        <div class="session-popover__help">
          <el-icon><QuestionFilled /></el-icon>
          <span>在 CLI 中执行 <code>/gui-connect</code> 创建新连接</span>
        </div>
      </div>
    </el-popover>
  </div>
</template>

<style scoped>
.session-manager {
  display: inline-flex;
}

.session-popover {
  margin: -12px;
}

.session-popover__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.session-popover__header .title {
  font-weight: 600;
  font-size: 14px;
  color: var(--el-text-color-primary);
}

.session-popover__current {
  padding: 12px 16px;
  background: var(--el-fill-color-light);
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.current-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 8px;
}

.current-session {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.session-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.session-id {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 13px;
}

.session-popover__list {
  padding: 12px 0;
  max-height: 240px;
  overflow-y: auto;
}

.list-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  padding: 0 16px 8px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 16px;
  color: var(--el-text-color-secondary);
}

.empty-state .el-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.empty-text {
  text-align: center;
  font-size: 13px;
}

.empty-text p {
  margin: 0;
}

.empty-hint {
  margin-top: 8px !important;
  color: var(--el-text-color-placeholder);
}

.empty-text code {
  background: var(--el-fill-color);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
}

.session-item {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.session-item:hover {
  background: var(--el-fill-color-light);
}

.session-item--active {
  background: var(--el-color-success-light-9);
}

.session-item--stale {
  opacity: 0.8;
}

.session-item--disconnected {
  opacity: 0.5;
  cursor: not-allowed;
}

.session-item__icon {
  margin-right: 12px;
  font-size: 16px;
}

.session-item__info {
  flex: 1;
  min-width: 0;
}

.session-item__main {
  display: flex;
  align-items: center;
  gap: 8px;
}

.session-item__meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

.status-text {
  font-weight: 500;
}

.session-item__badge {
  color: var(--el-color-success);
}

.session-popover__help {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 12px 16px;
  border-top: 1px solid var(--el-border-color-lighter);
  font-size: 12px;
  color: var(--el-text-color-secondary);
  background: var(--el-fill-color-lighter);
}

.session-popover__help code {
  background: var(--el-fill-color);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', monospace;
}
</style>
