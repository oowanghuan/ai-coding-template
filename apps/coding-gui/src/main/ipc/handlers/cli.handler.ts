/**
 * CLI 相关 IPC 处理器
 * CODE-003: cli:execute, cli:cancel, cli:output
 */

import { spawn, ChildProcess } from 'child_process'
import { BrowserWindow } from 'electron'
import { randomUUID } from 'crypto'
import type {
  CliExecuteRequest,
  CliExecuteResponse,
  CliCancelRequest,
  CliOutputEvent,
  CliCompleteEvent
} from '../../../shared/types/ipc.types'
import { ERROR_CODES, createError } from '../../../shared/types/error.types'
import { CLI_CHANNELS } from '../../../shared/constants/ipc-channels'

// 活跃的 CLI 进程
const activeProcesses = new Map<string, {
  process: ChildProcess
  startedAt: Date
  request: CliExecuteRequest
}>()

// CLI 可执行文件路径
const CLAUDE_CODE_PATH = process.env.CLAUDE_CODE_PATH || 'claude'

/**
 * 执行 CLI 命令
 */
export async function handleCliExecute(
  request: CliExecuteRequest,
  window: BrowserWindow
): Promise<CliExecuteResponse> {
  const executionId = randomUUID()
  const startedAt = new Date()

  // 命令处理逻辑：
  // 1. 如果命令以 'claude' 开头，直接执行完整命令
  // 2. 如果命令以 '/' 开头（slash command），添加 claude 前缀
  // 3. 其他情况视为 shell 命令直接执行
  let fullCommand = request.command

  if (fullCommand.startsWith('/')) {
    // Slash command: 添加 claude 前缀
    fullCommand = `${CLAUDE_CODE_PATH} "${fullCommand}"`
  } else if (!fullCommand.startsWith('claude') && !fullCommand.includes(' ')) {
    // 简单命令（如 skill 名称），添加 claude 前缀
    fullCommand = `${CLAUDE_CODE_PATH} ${fullCommand}`
  }

  // 如果是 print 模式且命令是 claude 开头，添加 --print 参数
  if (request.mode === 'print' && fullCommand.startsWith('claude')) {
    fullCommand = fullCommand.replace(/^claude\s*/, `${CLAUDE_CODE_PATH} --print `)
  }

  try {
    // 创建子进程 - 使用 shell 执行完整命令字符串
    const childProcess = spawn(fullCommand, [], {
      cwd: request.projectPath,
      shell: true,
      env: {
        ...process.env,
        FORCE_COLOR: '1'
      }
    })

    // 存储进程引用
    activeProcesses.set(executionId, {
      process: childProcess,
      startedAt,
      request
    })

    // 处理标准输出
    childProcess.stdout?.on('data', (data: Buffer) => {
      const event: CliOutputEvent = {
        executionId,
        type: 'stdout',
        content: data.toString(),
        timestamp: new Date().toISOString()
      }
      window.webContents.send(CLI_CHANNELS.OUTPUT, event)
    })

    // 处理标准错误
    childProcess.stderr?.on('data', (data: Buffer) => {
      const event: CliOutputEvent = {
        executionId,
        type: 'stderr',
        content: data.toString(),
        timestamp: new Date().toISOString()
      }
      window.webContents.send(CLI_CHANNELS.OUTPUT, event)
    })

    // 处理进程退出
    childProcess.on('close', (code: number | null) => {
      const endTime = new Date()
      const duration = endTime.getTime() - startedAt.getTime()

      const completeEvent: CliCompleteEvent = {
        executionId,
        exitCode: code ?? -1,
        duration
      }

      // 发送完成事件
      window.webContents.send(CLI_CHANNELS.OUTPUT, {
        executionId,
        type: 'system',
        content: `Process exited with code ${code}`,
        timestamp: endTime.toISOString()
      } as CliOutputEvent)

      // 清理
      activeProcesses.delete(executionId)
    })

    // 处理错误
    childProcess.on('error', (err: Error) => {
      const event: CliOutputEvent = {
        executionId,
        type: 'system',
        content: `Error: ${err.message}`,
        timestamp: new Date().toISOString()
      }
      window.webContents.send(CLI_CHANNELS.OUTPUT, event)
      activeProcesses.delete(executionId)
    })

    return {
      executionId,
      status: 'running',
      startedAt: startedAt.toISOString()
    }

  } catch (error) {
    throw createError(
      ERROR_CODES.CLI_SPAWN_FAILED,
      `Failed to spawn CLI process: ${(error as Error).message}`,
      { command: request.command }
    )
  }
}

/**
 * 取消 CLI 命令
 */
export async function handleCliCancel(
  request: CliCancelRequest
): Promise<{ success: boolean; executionId: string }> {
  const record = activeProcesses.get(request.executionId)

  if (!record) {
    throw createError(
      ERROR_CODES.CLI_NOT_FOUND,
      `No active process found with ID: ${request.executionId}`
    )
  }

  try {
    // 发送 SIGTERM
    record.process.kill('SIGTERM')

    // 如果 3 秒后还没退出，发送 SIGKILL
    setTimeout(() => {
      if (activeProcesses.has(request.executionId)) {
        record.process.kill('SIGKILL')
        activeProcesses.delete(request.executionId)
      }
    }, 3000)

    return {
      success: true,
      executionId: request.executionId
    }

  } catch (error) {
    throw createError(
      ERROR_CODES.CLI_CANCELLED,
      `Failed to cancel process: ${(error as Error).message}`,
      { executionId: request.executionId }
    )
  }
}

/**
 * 获取活跃进程列表
 */
export function getActiveProcesses(): string[] {
  return Array.from(activeProcesses.keys())
}

/**
 * 清理所有活跃进程
 */
export function cleanupAllProcesses(): void {
  for (const [id, record] of activeProcesses) {
    try {
      record.process.kill('SIGKILL')
    } catch {
      // 忽略错误
    }
  }
  activeProcesses.clear()
}
