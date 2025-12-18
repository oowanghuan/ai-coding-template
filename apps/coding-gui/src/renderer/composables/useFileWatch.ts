/**
 * 文件监控订阅 composable
 * CODE-005: useFileWatch - 订阅文件变更事件
 */

import { ref, onMounted, onUnmounted } from 'vue'
import type { FileChangeEvent } from '@shared/types/ipc.types'

interface UseFileWatchOptions {
  /** 自动订阅（默认 true） */
  autoSubscribe?: boolean
  /** 文件变更回调 */
  onChange?: (event: FileChangeEvent) => void
  /** 路径过滤器 */
  pathFilter?: (path: string) => boolean
}

/**
 * 文件监控订阅 composable
 */
export function useFileWatch(options: UseFileWatchOptions = {}) {
  const { autoSubscribe = true, onChange, pathFilter } = options

  /** 订阅状态 */
  const isSubscribed = ref(false)

  /** 最近的变更事件 */
  const recentChanges = ref<FileChangeEvent[]>([])

  /** 取消订阅函数 */
  let unsubscribe: (() => void) | null = null

  /** 最大保留事件数 */
  const MAX_EVENTS = 100

  /**
   * 处理文件变更事件
   */
  function handleChange(event: FileChangeEvent): void {
    // 应用路径过滤器
    if (pathFilter && !pathFilter(event.path)) {
      return
    }

    // 添加到最近变更
    recentChanges.value.push(event)

    // 限制数量
    if (recentChanges.value.length > MAX_EVENTS) {
      recentChanges.value = recentChanges.value.slice(-MAX_EVENTS)
    }

    // 调用回调
    onChange?.(event)
  }

  /**
   * 开始订阅
   */
  function subscribe(): void {
    if (isSubscribed.value) return

    unsubscribe = window.electronAPI.on('file:change', (_event, data) => {
      handleChange(data as FileChangeEvent)
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
   * 清空变更记录
   */
  function clearChanges(): void {
    recentChanges.value = []
  }

  /**
   * 检查文件是否有变更
   */
  function hasChanged(path: string): boolean {
    return recentChanges.value.some(e => e.path === path)
  }

  /**
   * 获取文件的最新变更
   */
  function getLatestChange(path: string): FileChangeEvent | undefined {
    const changes = recentChanges.value.filter(e => e.path === path)
    return changes[changes.length - 1]
  }

  // 自动订阅
  onMounted(() => {
    if (autoSubscribe) {
      subscribe()
    }
  })

  // 组件卸载时自动取消订阅
  onUnmounted(() => {
    unsubscribeNow()
  })

  return {
    isSubscribed,
    recentChanges,
    subscribe,
    unsubscribe: unsubscribeNow,
    clearChanges,
    hasChanged,
    getLatestChange
  }
}
