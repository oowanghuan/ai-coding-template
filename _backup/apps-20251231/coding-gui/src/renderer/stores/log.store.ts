/**
 * 日志状态管理
 * CODE-004: logStore - CLI 输出、交互日志
 */

import { defineStore } from 'pinia'
import { ref, computed, onUnmounted } from 'vue'
import type { CliOutputEvent, CliExecuteRequest, CliExecuteResponse } from '@shared/types/ipc.types'

interface LogEntry {
  id: string
  executionId: string
  type: 'stdout' | 'stderr' | 'system' | 'command'
  content: string
  timestamp: string
}

interface Execution {
  id: string
  command: string
  status: 'queued' | 'running' | 'completed' | 'failed' | 'cancelled'
  startedAt: string
  endedAt?: string
  exitCode?: number
  stepId?: string
}

export const useLogStore = defineStore('log', () => {
  // ============================================================
  // State
  // ============================================================

  /** 所有日志条目 */
  const logs = ref<LogEntry[]>([])

  /** 执行记录 */
  const executions = ref<Map<string, Execution>>(new Map())

  /** 当前活跃的执行 ID */
  const activeExecutionId = ref<string | null>(null)

  /** 日志抽屉是否展开 */
  const isDrawerOpen = ref(false)

  /** 自动滚动 */
  const autoScroll = ref(true)

  /** 最大日志条目数 */
  const MAX_LOGS = 10000

  // CLI 输出订阅取消函数
  let unsubscribe: (() => void) | null = null

  // ============================================================
  // Getters
  // ============================================================

  /** 当前执行的日志 */
  const currentLogs = computed<LogEntry[]>(() => {
    if (!activeExecutionId.value) return []
    return logs.value.filter(log => log.executionId === activeExecutionId.value)
  })

  /** 当前执行信息 */
  const currentExecution = computed<Execution | undefined>(() => {
    if (!activeExecutionId.value) return undefined
    return executions.value.get(activeExecutionId.value)
  })

  /** 是否有正在执行的命令 */
  const isExecuting = computed(() => {
    return Array.from(executions.value.values()).some(
      e => e.status === 'running' || e.status === 'queued'
    )
  })

  /** 获取指定 Step 的日志 */
  function getLogsForStep(stepId: string): LogEntry[] {
    const executionIds = Array.from(executions.value.entries())
      .filter(([_, e]) => e.stepId === stepId)
      .map(([id]) => id)

    return logs.value.filter(log => executionIds.includes(log.executionId))
  }

  // ============================================================
  // Actions
  // ============================================================

  /**
   * 执行 CLI 命令
   */
  async function executeCommand(
    command: string,
    projectPath: string,
    stepId?: string
  ): Promise<string | null> {
    try {
      const request: CliExecuteRequest = {
        command,
        projectPath,
        stepId,
        mode: 'print'
      }

      const response = await window.electronAPI.invoke<CliExecuteResponse>(
        'cli:execute',
        request
      )

      const executionId = response.executionId

      // 记录执行
      executions.value.set(executionId, {
        id: executionId,
        command,
        status: response.status,
        startedAt: response.startedAt || new Date().toISOString(),
        stepId
      })

      // 添加命令日志
      addLog({
        executionId,
        type: 'command',
        content: `$ ${command}`,
        timestamp: new Date().toISOString()
      })

      // 设置为当前活跃执行
      activeExecutionId.value = executionId

      return executionId
    } catch (e) {
      console.error('[LogStore] Execute failed:', e)
      return null
    }
  }

  /**
   * 取消执行
   */
  async function cancelExecution(executionId: string): Promise<boolean> {
    try {
      await window.electronAPI.invoke('cli:cancel', { executionId })

      const execution = executions.value.get(executionId)
      if (execution) {
        execution.status = 'cancelled'
        execution.endedAt = new Date().toISOString()
      }

      return true
    } catch (e) {
      console.error('[LogStore] Cancel failed:', e)
      return false
    }
  }

  /**
   * 添加日志条目
   */
  function addLog(entry: Omit<LogEntry, 'id'>): void {
    const log: LogEntry = {
      id: `log-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
      ...entry
    }

    logs.value.push(log)

    // 限制日志数量
    if (logs.value.length > MAX_LOGS) {
      logs.value = logs.value.slice(-MAX_LOGS)
    }
  }

  /**
   * 处理 CLI 输出事件
   */
  function handleCliOutput(event: CliOutputEvent): void {
    addLog({
      executionId: event.executionId,
      type: event.type,
      content: event.content,
      timestamp: event.timestamp
    })

    // 检查是否完成
    if (event.type === 'system' && event.content.includes('exited with code')) {
      const execution = executions.value.get(event.executionId)
      if (execution) {
        const match = event.content.match(/code (\d+)/)
        const exitCode = match ? parseInt(match[1], 10) : -1

        execution.status = exitCode === 0 ? 'completed' : 'failed'
        execution.exitCode = exitCode
        execution.endedAt = event.timestamp
      }
    }
  }

  /**
   * 订阅 CLI 输出
   */
  function subscribeToCliOutput(): void {
    if (unsubscribe) return // 已订阅

    unsubscribe = window.electronAPI.on('cli:output', (_event, data) => {
      handleCliOutput(data as CliOutputEvent)
    })
  }

  /**
   * 取消订阅 CLI 输出
   */
  function unsubscribeFromCliOutput(): void {
    if (unsubscribe) {
      unsubscribe()
      unsubscribe = null
    }
  }

  /**
   * 切换日志抽屉
   */
  function toggleDrawer(): void {
    isDrawerOpen.value = !isDrawerOpen.value
  }

  /**
   * 设置活跃执行
   */
  function setActiveExecution(executionId: string | null): void {
    activeExecutionId.value = executionId
  }

  /**
   * 清除日志
   */
  function clearLogs(executionId?: string): void {
    if (executionId) {
      logs.value = logs.value.filter(log => log.executionId !== executionId)
    } else {
      logs.value = []
    }
  }

  /**
   * 重置状态
   */
  function reset(): void {
    logs.value = []
    executions.value.clear()
    activeExecutionId.value = null
    isDrawerOpen.value = false
    unsubscribeFromCliOutput()
  }

  // 组件卸载时取消订阅
  onUnmounted(() => {
    unsubscribeFromCliOutput()
  })

  return {
    // State
    logs,
    executions,
    activeExecutionId,
    isDrawerOpen,
    autoScroll,

    // Getters
    currentLogs,
    currentExecution,
    isExecuting,
    getLogsForStep,

    // Actions
    executeCommand,
    cancelExecution,
    addLog,
    subscribeToCliOutput,
    unsubscribeFromCliOutput,
    toggleDrawer,
    setActiveExecution,
    clearLogs,
    reset
  }
})
