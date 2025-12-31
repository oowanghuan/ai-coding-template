/**
 * IPC 调用封装
 * CODE-005: useIpc composable
 */

import { ref } from 'vue'
import type { IpcResult, IpcError } from '@shared/types/ipc.types'

/**
 * 通用 IPC 调用 composable
 */
export function useIpc<TRequest, TResponse>(channel: string) {
  const isLoading = ref(false)
  const error = ref<IpcError | null>(null)
  const data = ref<TResponse | null>(null)

  async function invoke(request: TRequest): Promise<TResponse | null> {
    isLoading.value = true
    error.value = null

    try {
      const response = await window.electronAPI.invoke<TResponse>(
        channel as Parameters<typeof window.electronAPI.invoke>[0],
        request
      )
      data.value = response
      return response
    } catch (e) {
      const err = e as Error
      error.value = {
        code: 'E-IPC-UNKNOWN',
        message: err.message
      }
      return null
    } finally {
      isLoading.value = false
    }
  }

  function reset() {
    isLoading.value = false
    error.value = null
    data.value = null
  }

  return {
    isLoading,
    error,
    data,
    invoke,
    reset
  }
}

/**
 * 项目操作 IPC
 */
export function useProjectIpc() {
  return {
    open: useIpc('project:open'),
    state: useIpc('project:state')
  }
}

/**
 * CLI 操作 IPC
 */
export function useCliIpc() {
  return {
    execute: useIpc('cli:execute'),
    cancel: useIpc('cli:cancel')
  }
}

/**
 * 文件操作 IPC
 */
export function useFileIpc() {
  return {
    read: useIpc('file:read')
  }
}

/**
 * 审批操作 IPC
 */
export function useApprovalIpc() {
  return {
    submit: useIpc('approval:submit'),
    status: useIpc('approval:status')
  }
}
