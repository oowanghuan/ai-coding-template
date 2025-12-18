/**
 * CLI 调用队列服务
 * CODE-006: 实现 CLI 命令串行化执行
 *
 * 关键约束（DESIGN 1.3 节）：
 * - 全局队列，任意时刻只执行一个 CLI 命令
 * - FIFO 顺序
 * - 支持取消正在排队的命令
 */

import { spawn, ChildProcess } from 'child_process'
import { BrowserWindow } from 'electron'
import { randomUUID } from 'crypto'
import { EventEmitter } from 'events'
import type { CliExecuteRequest, CliOutputEvent } from '../../shared/types/ipc.types'
import { CLI_CHANNELS } from '../../shared/constants/ipc-channels'

/** 队列项 */
interface QueueItem {
  id: string
  request: CliExecuteRequest
  window: BrowserWindow
  resolve: (value: ExecutionResult) => void
  reject: (reason: Error) => void
  queuedAt: Date
}

/** 执行结果 */
interface ExecutionResult {
  executionId: string
  exitCode: number
  duration: number
  cancelled: boolean
}

/** CLI 可执行文件路径 */
const CLAUDE_CODE_PATH = process.env.CLAUDE_CODE_PATH || 'claude'

/** 命令超时（默认 10 分钟） */
const DEFAULT_TIMEOUT = 10 * 60 * 1000

/**
 * CLI 调用队列服务（单例）
 */
class CliQueueService extends EventEmitter {
  private static instance: CliQueueService | null = null

  /** 命令队列 */
  private queue: QueueItem[] = []

  /** 当前正在执行的命令 */
  private currentExecution: {
    id: string
    process: ChildProcess
    startedAt: Date
    request: CliExecuteRequest
    window: BrowserWindow
    timeoutId?: NodeJS.Timeout
  } | null = null

  /** 是否正在处理 */
  private isProcessing = false

  private constructor() {
    super()
  }

  /**
   * 获取单例实例
   */
  static getInstance(): CliQueueService {
    if (!CliQueueService.instance) {
      CliQueueService.instance = new CliQueueService()
    }
    return CliQueueService.instance
  }

  /**
   * 将命令加入队列
   */
  enqueue(request: CliExecuteRequest, window: BrowserWindow): Promise<ExecutionResult> {
    return new Promise((resolve, reject) => {
      const id = randomUUID()

      const item: QueueItem = {
        id,
        request,
        window,
        resolve,
        reject,
        queuedAt: new Date()
      }

      this.queue.push(item)
      this.emit('enqueue', { id, position: this.queue.length })

      // 发送排队事件
      const event: CliOutputEvent = {
        executionId: id,
        type: 'system',
        content: `Command queued (position: ${this.queue.length})`,
        timestamp: new Date().toISOString()
      }
      window.webContents.send(CLI_CHANNELS.OUTPUT, event)

      // 尝试处理队列
      this.processQueue()
    })
  }

  /**
   * 取消命令
   */
  cancel(executionId: string): boolean {
    // 检查是否在队列中
    const queueIndex = this.queue.findIndex(item => item.id === executionId)
    if (queueIndex >= 0) {
      const item = this.queue.splice(queueIndex, 1)[0]
      item.resolve({
        executionId,
        exitCode: -1,
        duration: 0,
        cancelled: true
      })
      this.emit('cancelled', { id: executionId, wasQueued: true })
      return true
    }

    // 检查是否正在执行
    if (this.currentExecution?.id === executionId) {
      this.cancelCurrentExecution()
      return true
    }

    return false
  }

  /**
   * 获取队列状态
   */
  getQueueStatus(): {
    queueLength: number
    currentExecution: { id: string; command: string; startedAt: string } | null
    queuedCommands: Array<{ id: string; command: string; queuedAt: string }>
  } {
    return {
      queueLength: this.queue.length,
      currentExecution: this.currentExecution
        ? {
            id: this.currentExecution.id,
            command: this.currentExecution.request.command,
            startedAt: this.currentExecution.startedAt.toISOString()
          }
        : null,
      queuedCommands: this.queue.map(item => ({
        id: item.id,
        command: item.request.command,
        queuedAt: item.queuedAt.toISOString()
      }))
    }
  }

  /**
   * 处理队列
   */
  private async processQueue(): Promise<void> {
    // 如果正在处理或队列为空，直接返回
    if (this.isProcessing || this.queue.length === 0) {
      return
    }

    this.isProcessing = true

    while (this.queue.length > 0) {
      const item = this.queue.shift()!

      try {
        const result = await this.executeCommand(item)
        item.resolve(result)
      } catch (error) {
        item.reject(error as Error)
      }
    }

    this.isProcessing = false
  }

  /**
   * 执行单个命令
   */
  private executeCommand(item: QueueItem): Promise<ExecutionResult> {
    return new Promise((resolve, reject) => {
      const { id, request, window } = item
      const startedAt = new Date()

      // 构建命令参数
      const args = [request.command]
      if (request.mode === 'print') {
        args.unshift('--print')
      }

      // 发送开始事件
      const startEvent: CliOutputEvent = {
        executionId: id,
        type: 'system',
        content: `Starting: ${request.command}`,
        timestamp: startedAt.toISOString()
      }
      window.webContents.send(CLI_CHANNELS.OUTPUT, startEvent)

      try {
        // 创建子进程
        const childProcess = spawn(CLAUDE_CODE_PATH, args, {
          cwd: request.projectPath,
          shell: true,
          env: {
            ...process.env,
            FORCE_COLOR: '1'
          }
        })

        // 设置超时
        const timeoutId = setTimeout(() => {
          this.cancelCurrentExecution()
          reject(new Error('Command timed out'))
        }, DEFAULT_TIMEOUT)

        // 存储当前执行
        this.currentExecution = {
          id,
          process: childProcess,
          startedAt,
          request,
          window,
          timeoutId
        }

        this.emit('started', { id, command: request.command })

        // 处理标准输出
        childProcess.stdout?.on('data', (data: Buffer) => {
          const event: CliOutputEvent = {
            executionId: id,
            type: 'stdout',
            content: data.toString(),
            timestamp: new Date().toISOString()
          }
          window.webContents.send(CLI_CHANNELS.OUTPUT, event)
        })

        // 处理标准错误
        childProcess.stderr?.on('data', (data: Buffer) => {
          const event: CliOutputEvent = {
            executionId: id,
            type: 'stderr',
            content: data.toString(),
            timestamp: new Date().toISOString()
          }
          window.webContents.send(CLI_CHANNELS.OUTPUT, event)
        })

        // 处理进程退出
        childProcess.on('close', (code: number | null) => {
          clearTimeout(timeoutId)
          const endTime = new Date()
          const duration = endTime.getTime() - startedAt.getTime()

          // 发送完成事件
          const completeEvent: CliOutputEvent = {
            executionId: id,
            type: 'system',
            content: `Process exited with code ${code}`,
            timestamp: endTime.toISOString()
          }
          window.webContents.send(CLI_CHANNELS.OUTPUT, completeEvent)

          this.currentExecution = null
          this.emit('completed', { id, exitCode: code, duration })

          resolve({
            executionId: id,
            exitCode: code ?? -1,
            duration,
            cancelled: false
          })
        })

        // 处理错误
        childProcess.on('error', (err: Error) => {
          clearTimeout(timeoutId)
          this.currentExecution = null
          this.emit('error', { id, error: err })
          reject(err)
        })

      } catch (error) {
        this.currentExecution = null
        reject(error)
      }
    })
  }

  /**
   * 取消当前执行
   */
  private cancelCurrentExecution(): void {
    if (!this.currentExecution) return

    const { id, process, timeoutId, window, startedAt } = this.currentExecution

    // 清除超时
    if (timeoutId) {
      clearTimeout(timeoutId)
    }

    // 发送取消事件
    const cancelEvent: CliOutputEvent = {
      executionId: id,
      type: 'system',
      content: 'Command cancelled',
      timestamp: new Date().toISOString()
    }
    window.webContents.send(CLI_CHANNELS.OUTPUT, cancelEvent)

    // 终止进程
    try {
      process.kill('SIGTERM')

      // 3 秒后强制终止
      setTimeout(() => {
        try {
          process.kill('SIGKILL')
        } catch {
          // 进程可能已经退出
        }
      }, 3000)
    } catch {
      // 忽略错误
    }

    this.emit('cancelled', { id, wasQueued: false })
    this.currentExecution = null
  }

  /**
   * 清理所有命令
   */
  cleanup(): void {
    // 取消当前执行
    this.cancelCurrentExecution()

    // 清空队列
    for (const item of this.queue) {
      item.resolve({
        executionId: item.id,
        exitCode: -1,
        duration: 0,
        cancelled: true
      })
    }
    this.queue = []

    this.emit('cleanup')
  }
}

// 导出单例
export const cliQueueService = CliQueueService.getInstance()

// 导出类型供测试使用
export { CliQueueService, QueueItem, ExecutionResult }
