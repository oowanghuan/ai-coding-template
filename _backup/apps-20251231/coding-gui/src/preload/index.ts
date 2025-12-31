/**
 * Coding GUI - Preload 脚本
 * 安全地暴露 IPC 通信接口给渲染进程
 */

import { contextBridge, ipcRenderer } from 'electron'
import type { IpcRendererEvent } from 'electron'

// IPC 通道白名单
const ALLOWED_CHANNELS = {
  invoke: [
    'cli:execute',
    'cli:cancel',
    'project:open',
    'project:state',
    'file:read',
    'approval:submit',
    'approval:status',
    'dialog:openFolder',
    'shell:openTerminal',
    // Session 相关通道
    'session:list',
    'session:sendCommand',
    'session:waitResult',
    'session:startWatch',
    'session:stopWatch'
  ],
  on: [
    'cli:output',
    'file:change',
    'project:state-change',
    // Session 变更事件
    'session:change'
  ]
} as const

type InvokeChannel = typeof ALLOWED_CHANNELS.invoke[number]
type OnChannel = typeof ALLOWED_CHANNELS.on[number]

/**
 * 暴露给渲染进程的安全 API
 */
const electronAPI = {
  /**
   * 调用主进程 IPC 方法
   */
  invoke: async <T = unknown>(channel: InvokeChannel, ...args: unknown[]): Promise<T> => {
    if (!ALLOWED_CHANNELS.invoke.includes(channel)) {
      throw new Error(`IPC channel "${channel}" is not allowed`)
    }
    return ipcRenderer.invoke(channel, ...args)
  },

  /**
   * 订阅主进程事件
   */
  on: (channel: OnChannel, callback: (event: IpcRendererEvent, ...args: unknown[]) => void): (() => void) => {
    if (!ALLOWED_CHANNELS.on.includes(channel)) {
      throw new Error(`IPC channel "${channel}" is not allowed`)
    }

    const subscription = (_event: IpcRendererEvent, ...args: unknown[]) => {
      callback(_event, ...args)
    }

    ipcRenderer.on(channel, subscription)

    // 返回取消订阅函数
    return () => {
      ipcRenderer.removeListener(channel, subscription)
    }
  },

  /**
   * 一次性监听事件
   */
  once: (channel: OnChannel, callback: (event: IpcRendererEvent, ...args: unknown[]) => void): void => {
    if (!ALLOWED_CHANNELS.on.includes(channel)) {
      throw new Error(`IPC channel "${channel}" is not allowed`)
    }
    ipcRenderer.once(channel, callback)
  }
}

// 将 API 暴露到 window.electronAPI
contextBridge.exposeInMainWorld('electronAPI', electronAPI)

// 类型声明
declare global {
  interface Window {
    electronAPI: typeof electronAPI
  }
}
