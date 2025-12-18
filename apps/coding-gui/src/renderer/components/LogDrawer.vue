<script setup lang="ts">
import { computed, ref, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  logs: string[]
  stepId: string
}>()

const logContainer = ref<HTMLElement | null>(null)

const parsedLogs = computed(() => {
  return props.logs.map(log => {
    if (log.startsWith('$')) {
      return { type: 'command', content: log }
    } else if (log.includes('✓') || log.includes('completed')) {
      return { type: 'success', content: log }
    } else if (log.includes('✗') || log.includes('Error') || log.includes('failed')) {
      return { type: 'error', content: log }
    } else if (log.includes('⚠') || log.includes('Warning')) {
      return { type: 'warning', content: log }
    } else if (log.match(/^\[[\d-:\s]+\]/)) {
      return { type: 'timestamp', content: log }
    } else {
      return { type: 'info', content: log }
    }
  })
})

const copyLogs = () => {
  const text = props.logs.join('\n')
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('日志已复制到剪贴板')
  })
}

const clearLogs = () => {
  // In real app, this would emit an event
  ElMessage.info('清空日志功能（Demo）')
}

// Auto-scroll to bottom when logs update
watch(() => props.logs.length, () => {
  nextTick(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight
    }
  })
})
</script>

<template>
  <div class="log-drawer">
    <div class="log-drawer__header">
      <span class="log-drawer__title">
        <el-icon><Document /></el-icon>
        执行日志
      </span>
      <div class="log-drawer__actions">
        <el-button size="small" text @click="copyLogs">
          <el-icon><CopyDocument /></el-icon>
          复制
        </el-button>
        <el-button size="small" text @click="clearLogs">
          <el-icon><Delete /></el-icon>
          清空
        </el-button>
      </div>
    </div>
    <div ref="logContainer" class="log-drawer__content">
      <div
        v-for="(log, index) in parsedLogs"
        :key="index"
        class="log-line"
        :class="`log-line--${log.type}`"
      >
        {{ log.content }}
      </div>
      <span class="log-cursor">|</span>
    </div>
  </div>
</template>

<style scoped>
.log-drawer {
  background: #1e1e1e;
  border-radius: 8px;
  overflow: hidden;
  margin-top: 12px;
}

.log-drawer__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #2d2d2d;
  border-bottom: 1px solid #3d3d3d;
}

.log-drawer__title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #ccc;
}

.log-drawer__actions {
  display: flex;
  gap: 4px;
}

.log-drawer__actions .el-button {
  color: #888;
}

.log-drawer__actions .el-button:hover {
  color: #ccc;
}

.log-drawer__content {
  padding: 12px;
  max-height: 300px;
  overflow-y: auto;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.6;
}

.log-line {
  white-space: pre-wrap;
  word-break: break-all;
}

.log-line--command {
  color: #fff;
}

.log-line--timestamp {
  color: #888;
}

.log-line--success {
  color: #6fbf73;
}

.log-line--error {
  color: #f56c6c;
}

.log-line--warning {
  color: #e6a23c;
}

.log-line--info {
  color: #66b1ff;
}

.log-cursor {
  color: #67c23a;
  animation: blink 1s infinite;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* Scrollbar styling */
.log-drawer__content::-webkit-scrollbar {
  width: 8px;
}

.log-drawer__content::-webkit-scrollbar-track {
  background: #2d2d2d;
}

.log-drawer__content::-webkit-scrollbar-thumb {
  background: #555;
  border-radius: 4px;
}

.log-drawer__content::-webkit-scrollbar-thumb:hover {
  background: #666;
}
</style>
