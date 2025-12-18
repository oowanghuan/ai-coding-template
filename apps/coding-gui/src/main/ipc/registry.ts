/**
 * IPC 通道注册中心
 * CODE-003: 实现 IPC API 层 (IPC Bridge)
 */

import type { IpcMain, BrowserWindow } from 'electron'
import { IPC_CHANNELS } from '../../shared/constants/ipc-channels'
import { createValidatorMiddleware } from './middleware/validator'
import { createPathValidatorMiddleware } from './middleware/path-validator'
import { createRateLimiterMiddleware } from './middleware/rate-limiter'

// Handlers
import { handleCliExecute, handleCliCancel, cleanupAllProcesses } from './handlers/cli.handler'
import { handleProjectOpen, handleProjectState } from './handlers/project.handler'
import { handleFileRead, startFileWatch, stopAllFileWatches } from './handlers/file.handler'
import { handleApprovalSubmit, handleApprovalStatus } from './handlers/approval.handler'
import { handleShellOpenTerminal } from './handlers/shell.handler'
import {
  handleSessionList,
  handleSessionSendCommand,
  handleSessionWaitResult,
  startSessionWatch,
  stopSessionWatch,
  stopAllSessionWatches
} from './handlers/session.handler'
import { dialog } from 'electron'

// IPC 中间件类型
export type IpcMiddleware = (
  channel: string,
  args: unknown[],
  next: () => Promise<unknown>
) => Promise<unknown>

// 主窗口引用
let mainWindow: BrowserWindow | null = null

/**
 * 设置主窗口引用
 */
export function setMainWindow(window: BrowserWindow): void {
  mainWindow = window
}

/**
 * 应用中间件链
 */
function applyMiddlewares(
  handler: (...args: unknown[]) => Promise<unknown>,
  middlewares: IpcMiddleware[],
  channel: string
): (...args: unknown[]) => Promise<unknown> {
  return async (...args: unknown[]) => {
    let index = 0

    const next = async (): Promise<unknown> => {
      if (index < middlewares.length) {
        const middleware = middlewares[index++]
        return middleware(channel, args, next)
      }
      return handler(...args)
    }

    return next()
  }
}

/**
 * 注册所有 IPC 处理器
 */
export function registerIpcHandlers(ipcMain: IpcMain): void {
  // 创建中间件
  const middlewares: IpcMiddleware[] = [
    createRateLimiterMiddleware(),
    createValidatorMiddleware(),
    createPathValidatorMiddleware()
  ]

  // CLI 处理器
  ipcMain.handle(
    IPC_CHANNELS.EXECUTE,
    applyMiddlewares(
      async (_event, request) => {
        if (!mainWindow) throw new Error('Main window not available')
        return handleCliExecute(request as Parameters<typeof handleCliExecute>[0], mainWindow)
      },
      middlewares,
      IPC_CHANNELS.EXECUTE
    )
  )

  ipcMain.handle(
    IPC_CHANNELS.CANCEL,
    applyMiddlewares(
      async (_event, request) => handleCliCancel(request as Parameters<typeof handleCliCancel>[0]),
      middlewares,
      IPC_CHANNELS.CANCEL
    )
  )

  // 项目处理器
  ipcMain.handle(
    IPC_CHANNELS.OPEN,
    applyMiddlewares(
      async (_event, request) => {
        const result = await handleProjectOpen(request as Parameters<typeof handleProjectOpen>[0])
        // 打开项目后启动文件监控
        if (mainWindow && result.project) {
          startFileWatch(result.project.path, mainWindow)
        }
        return result
      },
      middlewares,
      IPC_CHANNELS.OPEN
    )
  )

  ipcMain.handle(
    IPC_CHANNELS.STATE,
    applyMiddlewares(
      async () => handleProjectState(),
      middlewares,
      IPC_CHANNELS.STATE
    )
  )

  // 文件处理器
  ipcMain.handle(
    IPC_CHANNELS.READ,
    applyMiddlewares(
      async (_event, request) => handleFileRead(request as Parameters<typeof handleFileRead>[0]),
      middlewares,
      IPC_CHANNELS.READ
    )
  )

  // 审批处理器
  ipcMain.handle(
    IPC_CHANNELS.SUBMIT,
    applyMiddlewares(
      async (_event, request) => handleApprovalSubmit(request as Parameters<typeof handleApprovalSubmit>[0]),
      middlewares,
      IPC_CHANNELS.SUBMIT
    )
  )

  ipcMain.handle(
    IPC_CHANNELS.STATUS,
    applyMiddlewares(
      async (_event, request) => handleApprovalStatus(request as Parameters<typeof handleApprovalStatus>[0]),
      middlewares,
      IPC_CHANNELS.STATUS
    )
  )

  // Shell 处理器
  ipcMain.handle(
    IPC_CHANNELS.OPEN_TERMINAL,
    applyMiddlewares(
      async (_event, request) => handleShellOpenTerminal(request as Parameters<typeof handleShellOpenTerminal>[0]),
      middlewares,
      IPC_CHANNELS.OPEN_TERMINAL
    )
  )

  // Dialog 处理器 - 打开文件夹选择对话框
  ipcMain.handle('dialog:openFolder', async () => {
    const result = await dialog.showOpenDialog({
      properties: ['openDirectory'],
      title: '选择项目文件夹'
    })
    if (result.canceled || result.filePaths.length === 0) {
      return { canceled: true, path: null }
    }
    return { canceled: false, path: result.filePaths[0] }
  })

  // Session 处理器 (GUI-CLI 通信)
  ipcMain.handle(
    IPC_CHANNELS.LIST,
    applyMiddlewares(
      async (_event, request) => handleSessionList(request as Parameters<typeof handleSessionList>[0]),
      middlewares,
      IPC_CHANNELS.LIST
    )
  )

  ipcMain.handle(
    IPC_CHANNELS.SEND_COMMAND,
    applyMiddlewares(
      async (_event, request) => handleSessionSendCommand(request as Parameters<typeof handleSessionSendCommand>[0]),
      middlewares,
      IPC_CHANNELS.SEND_COMMAND
    )
  )

  ipcMain.handle(
    IPC_CHANNELS.WAIT_RESULT,
    applyMiddlewares(
      async (_event, request) => handleSessionWaitResult(request as Parameters<typeof handleSessionWaitResult>[0]),
      middlewares,
      IPC_CHANNELS.WAIT_RESULT
    )
  )

  ipcMain.handle(
    IPC_CHANNELS.START_WATCH,
    applyMiddlewares(
      async (_event, request) => {
        if (!mainWindow) throw new Error('Main window not available')
        const { projectPath } = request as { projectPath: string }
        startSessionWatch(projectPath, mainWindow)
        return { success: true }
      },
      middlewares,
      IPC_CHANNELS.START_WATCH
    )
  )

  ipcMain.handle(
    IPC_CHANNELS.STOP_WATCH,
    applyMiddlewares(
      async (_event, request) => {
        const { projectPath } = request as { projectPath: string }
        stopSessionWatch(projectPath)
        return { success: true }
      },
      middlewares,
      IPC_CHANNELS.STOP_WATCH
    )
  )

  console.log('[IPC Registry] All handlers registered')
}

/**
 * 清理所有资源
 */
export function cleanupIpcResources(): void {
  cleanupAllProcesses()
  stopAllFileWatches()
  stopAllSessionWatches()
  console.log('[IPC Registry] Resources cleaned up')
}
