/**
 * CLI 输出订阅 composable
 * CODE-005: useCliOutput - 订阅/反订阅 CLI 输出
 */

import { ref, onMounted, onUnmounted, watch } from 'vue'
import type { CliOutputEvent } from '@shared/types/ipc.types'

interface UseCliOutputOptions {
  /** 过滤的执行 ID（只接收此 ID 的输出） */
  executionId?: string
  /** 自动订阅（默认 true） */
  autoSubscribe?: boolean
  /** 输出回调 */
  onOutput?: (event: CliOutputEvent) => void
  /** 完成回调 */
  onComplete?: (executionId: string, exitCode: number) => void
}

/**
 * CLI 输出订阅 composable
 * 实现 cli:output 订阅生命周期管理
 */
export function useCliOutput(options: UseCliOutputOptions = {}) {
  const { executionId, autoSubscribe = true, onOutput, onComplete } = options

  /** 订阅状态 */
  const isSubscribed = ref(false)

  /** 输出缓冲 */
  const outputBuffer = ref<CliOutputEvent[]>([])

  /** 取消订阅函数 */
  let unsubscribe: (() => void) | null = null

  /**
   * 处理输出事件
   */
  function handleOutput(event: CliOutputEvent): void {
    // executionId 过滤
    if (executionId && event.executionId !== executionId) {
      return
    }

    // 添加到缓冲
    outputBuffer.value.push(event)

    // 调用回调
    onOutput?.(event)

    // 检查是否完成
    if (event.type === 'system' && event.content.includes('exited with code')) {
      const match = event.content.match(/code (\d+)/)
      const exitCode = match ? parseInt(match[1], 10) : -1
      onComplete?.(event.executionId, exitCode)
    }
  }

  /**
   * 开始订阅
   */
  function subscribe(): void {
    if (isSubscribed.value) return

    unsubscribe = window.electronAPI.on('cli:output', (_event, data) => {
      handleOutput(data as CliOutputEvent)
    })

    isSubscribed.value = true
  }

  /**
   * 停止订阅
   */
  function unsubscribeNow(): void {
    if (!isSubscribed.value) return

    if (unsubscribe) {
      unsubscribe()
      unsubscribe = null
    }

    isSubscribed.value = false
  }

  /**
   * 清空缓冲
   */
  function clearBuffer(): void {
    outputBuffer.value = []
  }

  /**
   * 获取指定执行 ID 的输出
   */
  function getOutputForExecution(execId: string): CliOutputEvent[] {
    return outputBuffer.value.filter(e => e.executionId === execId)
  }

  // 自动订阅
  onMounted(() => {
    if (autoSubscribe) {
      subscribe()
    }
  })

  // 组件卸载时自动取消订阅（生命周期管理）
  onUnmounted(() => {
    unsubscribeNow()
  })

  // 监听 executionId 变化，清空不相关的缓冲
  if (executionId) {
    watch(
      () => executionId,
      () => {
        outputBuffer.value = outputBuffer.value.filter(
          e => e.executionId === executionId
        )
      }
    )
  }

  return {
    isSubscribed,
    outputBuffer,
    subscribe,
    unsubscribe: unsubscribeNow,
    clearBuffer,
    getOutputForExecution
  }
}
