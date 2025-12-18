/**
 * CLI Queue Service 单元测试
 * 对应 60_TEST_PLAN.md CQ-001 ~ CQ-007
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { EventEmitter } from 'events'

// Mock Electron
vi.mock('electron', () => ({
  BrowserWindow: vi.fn()
}))

// Mock child_process
vi.mock('child_process', () => ({
  spawn: vi.fn()
}))

// Mock crypto
vi.mock('crypto', () => ({
  randomUUID: vi.fn(() => 'test-uuid-' + Math.random().toString(36).substring(7))
}))

// 创建 mock 的 BrowserWindow
const createMockWindow = () => ({
  webContents: {
    send: vi.fn()
  }
})

// 创建 mock 的 ChildProcess
const createMockProcess = () => {
  const proc = new EventEmitter() as any
  proc.stdout = new EventEmitter()
  proc.stderr = new EventEmitter()
  proc.kill = vi.fn()
  return proc
}

describe('CliQueueService', () => {
  let CliQueueService: any
  let cliQueueService: any
  let spawn: any

  beforeEach(async () => {
    vi.clearAllMocks()
    vi.resetModules()

    // 获取 mocked spawn
    const childProcess = await import('child_process')
    spawn = vi.mocked(childProcess.spawn)

    // 动态导入以获取新实例
    const module = await import('../cli-queue.service')
    CliQueueService = module.CliQueueService

    // 重置单例
    ;(CliQueueService as any).instance = null
    cliQueueService = CliQueueService.getInstance()
  })

  afterEach(() => {
    cliQueueService.cleanup()
  })

  describe('CQ-001: enqueue 单个命令', () => {
    it('should enqueue command and return executionId', async () => {
      const mockWindow = createMockWindow()
      const mockProcess = createMockProcess()
      spawn.mockReturnValue(mockProcess)

      const enqueuePromise = cliQueueService.enqueue(
        { command: 'echo hello', projectPath: '/test', mode: 'print' },
        mockWindow as any
      )

      // 模拟进程完成
      setTimeout(() => {
        mockProcess.emit('close', 0)
      }, 10)

      const result = await enqueuePromise

      expect(result.executionId).toBeDefined()
      expect(result.exitCode).toBe(0)
      expect(result.cancelled).toBe(false)
    })
  })

  describe('CQ-002: enqueue 多个命令串行执行', () => {
    it('should serialize multiple commands', async () => {
      const mockWindow = createMockWindow()
      const executionOrder: string[] = []

      // 第一个命令
      const mockProcess1 = createMockProcess()
      // 第二个命令
      const mockProcess2 = createMockProcess()

      let spawnCount = 0
      spawn.mockImplementation(() => {
        spawnCount++
        if (spawnCount === 1) {
          setTimeout(() => {
            executionOrder.push('cmd1-complete')
            mockProcess1.emit('close', 0)
          }, 50)
          return mockProcess1
        } else {
          setTimeout(() => {
            executionOrder.push('cmd2-complete')
            mockProcess2.emit('close', 0)
          }, 20)
          return mockProcess2
        }
      })

      // 同时入队两个命令
      const cmd1Promise = cliQueueService.enqueue(
        { command: 'cmd1', projectPath: '/test', mode: 'print' },
        mockWindow as any
      )
      const cmd2Promise = cliQueueService.enqueue(
        { command: 'cmd2', projectPath: '/test', mode: 'print' },
        mockWindow as any
      )

      await Promise.all([cmd1Promise, cmd2Promise])

      // 验证串行执行顺序
      expect(executionOrder).toEqual(['cmd1-complete', 'cmd2-complete'])
    })
  })

  describe('CQ-003: cancel 正在执行的命令', () => {
    it('should cancel running command', async () => {
      const mockWindow = createMockWindow()
      const mockProcess = createMockProcess()
      spawn.mockReturnValue(mockProcess)

      const enqueuePromise = cliQueueService.enqueue(
        { command: 'long-running', projectPath: '/test', mode: 'print' },
        mockWindow as any
      )

      // 等待命令开始执行
      await new Promise(resolve => setTimeout(resolve, 10))

      // 获取 executionId
      const status = cliQueueService.getQueueStatus()
      expect(status.currentExecution).not.toBeNull()

      const executionId = status.currentExecution!.id

      // 取消命令
      const cancelled = cliQueueService.cancel(executionId)
      expect(cancelled).toBe(true)
      expect(mockProcess.kill).toHaveBeenCalledWith('SIGTERM')

      // 模拟进程退出
      mockProcess.emit('close', -1)

      // 验证取消事件被发送
      expect(mockWindow.webContents.send).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          type: 'system',
          content: 'Command cancelled'
        })
      )
    })
  })

  describe('CQ-004: cancel 队列中的命令', () => {
    it('should cancel queued command', async () => {
      const mockWindow = createMockWindow()
      const mockProcess = createMockProcess()
      spawn.mockReturnValue(mockProcess)

      // 第一个命令开始执行
      cliQueueService.enqueue(
        { command: 'cmd1', projectPath: '/test', mode: 'print' },
        mockWindow as any
      )

      // 第二个命令进入队列
      const cmd2Promise = cliQueueService.enqueue(
        { command: 'cmd2', projectPath: '/test', mode: 'print' },
        mockWindow as any
      )

      // 等待第二个命令进入队列
      await new Promise(resolve => setTimeout(resolve, 10))

      // 获取队列状态
      const status = cliQueueService.getQueueStatus()
      expect(status.queueLength).toBe(1)

      const queuedId = status.queuedCommands[0].id

      // 取消队列中的命令
      const cancelled = cliQueueService.cancel(queuedId)
      expect(cancelled).toBe(true)

      // 验证队列为空
      const newStatus = cliQueueService.getQueueStatus()
      expect(newStatus.queueLength).toBe(0)

      // 验证 Promise 被 resolve
      const result = await cmd2Promise
      expect(result.cancelled).toBe(true)

      // 清理：完成第一个命令
      mockProcess.emit('close', 0)
    })
  })

  describe('CQ-005: getQueueStatus 返回正确状态', () => {
    it('should return correct queue status', async () => {
      const mockWindow = createMockWindow()
      const mockProcess = createMockProcess()
      spawn.mockReturnValue(mockProcess)

      // 初始状态
      let status = cliQueueService.getQueueStatus()
      expect(status.queueLength).toBe(0)
      expect(status.currentExecution).toBeNull()

      // 入队一个命令
      cliQueueService.enqueue(
        { command: 'test-cmd', projectPath: '/test', mode: 'print' },
        mockWindow as any
      )

      // 等待开始执行
      await new Promise(resolve => setTimeout(resolve, 10))

      status = cliQueueService.getQueueStatus()
      expect(status.currentExecution).not.toBeNull()
      expect(status.currentExecution!.command).toBe('test-cmd')
      expect(status.currentExecution!.startedAt).toBeDefined()

      // 清理
      mockProcess.emit('close', 0)
    })
  })

  describe('CQ-006: 命令超时处理', () => {
    it('should handle command timeout', async () => {
      vi.useFakeTimers()

      const mockWindow = createMockWindow()
      const mockProcess = createMockProcess()
      spawn.mockReturnValue(mockProcess)

      let rejected = false
      let rejectionError: any = null

      const enqueuePromise = cliQueueService.enqueue(
        { command: 'timeout-cmd', projectPath: '/test', mode: 'print' },
        mockWindow as any
      ).catch((error: any) => {
        rejected = true
        rejectionError = error
      })

      // 推进时间到超时（10 分钟）
      await vi.advanceTimersByTimeAsync(10 * 60 * 1000 + 100)

      // 等待 Promise 处理
      await vi.runAllTimersAsync()

      expect(mockProcess.kill).toHaveBeenCalledWith('SIGTERM')
      expect(rejected).toBe(true)
      if (rejectionError) {
        expect(rejectionError.message).toContain('timed out')
      }

      vi.useRealTimers()
    })
  })

  describe('CQ-007: SIGTERM 失败后 SIGKILL', () => {
    it('should use SIGKILL after SIGTERM fails', async () => {
      vi.useFakeTimers()

      const mockWindow = createMockWindow()
      const mockProcess = createMockProcess()
      spawn.mockReturnValue(mockProcess)

      cliQueueService.enqueue(
        { command: 'stubborn-cmd', projectPath: '/test', mode: 'print' },
        mockWindow as any
      )

      // 等待命令开始执行
      await vi.advanceTimersByTimeAsync(10)

      const status = cliQueueService.getQueueStatus()
      const executionId = status.currentExecution!.id

      // 取消命令
      cliQueueService.cancel(executionId)

      // 验证 SIGTERM 被调用
      expect(mockProcess.kill).toHaveBeenCalledWith('SIGTERM')

      // 推进时间 3 秒
      await vi.advanceTimersByTimeAsync(3100)

      // 验证 SIGKILL 被调用
      expect(mockProcess.kill).toHaveBeenCalledWith('SIGKILL')

      vi.useRealTimers()
    })
  })
})
