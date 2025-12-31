/**
 * CLI Handler 单元测试
 * 对应 60_TEST_PLAN.md CH-001 ~ CH-005
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
  randomUUID: vi.fn(() => 'mock-uuid-' + Math.random().toString(36).substring(7))
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

describe('CLI Handler', () => {
  let handleCliExecute: any
  let handleCliCancel: any
  let getActiveProcesses: any
  let cleanupAllProcesses: any
  let spawn: any

  beforeEach(async () => {
    vi.clearAllMocks()
    vi.resetModules()

    const childProcess = await import('child_process')
    spawn = vi.mocked(childProcess.spawn)

    const module = await import('../../handlers/cli.handler')
    handleCliExecute = module.handleCliExecute
    handleCliCancel = module.handleCliCancel
    getActiveProcesses = module.getActiveProcesses
    cleanupAllProcesses = module.cleanupAllProcesses
  })

  afterEach(() => {
    cleanupAllProcesses()
  })

  describe('CH-001: cli:execute 有效命令', () => {
    it('should return executionId when executing valid command', async () => {
      const mockWindow = createMockWindow()
      const mockProcess = createMockProcess()
      spawn.mockReturnValue(mockProcess)

      const result = await handleCliExecute(
        { command: '/help', projectPath: '/test/project', mode: 'print' },
        mockWindow as any
      )

      expect(result.executionId).toBeDefined()
      expect(result.status).toBe('running')
      expect(result.startedAt).toBeDefined()
      expect(spawn).toHaveBeenCalled()
    })

    it('should spawn with correct arguments for print mode', async () => {
      const mockWindow = createMockWindow()
      const mockProcess = createMockProcess()
      spawn.mockReturnValue(mockProcess)

      await handleCliExecute(
        { command: '/help', projectPath: '/test/project', mode: 'print' },
        mockWindow as any
      )

      expect(spawn).toHaveBeenCalledWith(
        expect.any(String),
        ['--print', '/help'],
        expect.objectContaining({
          cwd: '/test/project',
          shell: true
        })
      )
    })
  })

  describe('CH-002: cli:execute 空命令', () => {
    it('should still execute (validation happens in middleware)', async () => {
      const mockWindow = createMockWindow()
      const mockProcess = createMockProcess()
      spawn.mockReturnValue(mockProcess)

      // 注意：实际验证在 validator middleware 中完成
      // handler 本身不做验证
      const result = await handleCliExecute(
        { command: '', projectPath: '/test/project', mode: 'print' },
        mockWindow as any
      )

      expect(result.executionId).toBeDefined()
    })
  })

  describe('CH-003: cli:cancel 有效 executionId', () => {
    it('should cancel running command', async () => {
      const mockWindow = createMockWindow()
      const mockProcess = createMockProcess()
      spawn.mockReturnValue(mockProcess)

      // 先执行一个命令
      const execResult = await handleCliExecute(
        { command: '/help', projectPath: '/test/project', mode: 'print' },
        mockWindow as any
      )

      // 取消命令
      const cancelResult = await handleCliCancel({
        executionId: execResult.executionId
      })

      expect(cancelResult.success).toBe(true)
      expect(cancelResult.executionId).toBe(execResult.executionId)
      expect(mockProcess.kill).toHaveBeenCalledWith('SIGTERM')
    })
  })

  describe('CH-004: cli:cancel 无效 executionId', () => {
    it('should throw error for non-existent executionId', async () => {
      await expect(
        handleCliCancel({ executionId: 'non-existent-id' })
      ).rejects.toThrow()
    })
  })

  describe('CH-005: cli:output 订阅', () => {
    it('should send stdout output events', async () => {
      const mockWindow = createMockWindow()
      const mockProcess = createMockProcess()
      spawn.mockReturnValue(mockProcess)

      await handleCliExecute(
        { command: '/help', projectPath: '/test/project', mode: 'print' },
        mockWindow as any
      )

      // 模拟 stdout 输出
      mockProcess.stdout.emit('data', Buffer.from('Hello World'))

      expect(mockWindow.webContents.send).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          type: 'stdout',
          content: 'Hello World'
        })
      )
    })

    it('should send stderr output events', async () => {
      const mockWindow = createMockWindow()
      const mockProcess = createMockProcess()
      spawn.mockReturnValue(mockProcess)

      await handleCliExecute(
        { command: '/help', projectPath: '/test/project', mode: 'print' },
        mockWindow as any
      )

      // 模拟 stderr 输出
      mockProcess.stderr.emit('data', Buffer.from('Error message'))

      expect(mockWindow.webContents.send).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          type: 'stderr',
          content: 'Error message'
        })
      )
    })

    it('should send system events on process close', async () => {
      const mockWindow = createMockWindow()
      const mockProcess = createMockProcess()
      spawn.mockReturnValue(mockProcess)

      await handleCliExecute(
        { command: '/help', projectPath: '/test/project', mode: 'print' },
        mockWindow as any
      )

      // 模拟进程退出
      mockProcess.emit('close', 0)

      expect(mockWindow.webContents.send).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          type: 'system',
          content: expect.stringContaining('exited')
        })
      )
    })
  })

  describe('getActiveProcesses', () => {
    it('should return list of active execution IDs', async () => {
      const mockWindow = createMockWindow()
      const mockProcess = createMockProcess()
      spawn.mockReturnValue(mockProcess)

      const result = await handleCliExecute(
        { command: '/help', projectPath: '/test/project', mode: 'print' },
        mockWindow as any
      )

      const activeIds = getActiveProcesses()
      expect(activeIds).toContain(result.executionId)
    })

    it('should remove process from active list on close', async () => {
      const mockWindow = createMockWindow()
      const mockProcess = createMockProcess()
      spawn.mockReturnValue(mockProcess)

      const result = await handleCliExecute(
        { command: '/help', projectPath: '/test/project', mode: 'print' },
        mockWindow as any
      )

      // 模拟进程退出
      mockProcess.emit('close', 0)

      const activeIds = getActiveProcesses()
      expect(activeIds).not.toContain(result.executionId)
    })
  })

  describe('cleanupAllProcesses', () => {
    it('should kill all active processes', async () => {
      const mockWindow = createMockWindow()
      const mockProcess1 = createMockProcess()
      const mockProcess2 = createMockProcess()

      let callCount = 0
      spawn.mockImplementation(() => {
        callCount++
        return callCount === 1 ? mockProcess1 : mockProcess2
      })

      await handleCliExecute(
        { command: 'cmd1', projectPath: '/test', mode: 'print' },
        mockWindow as any
      )
      await handleCliExecute(
        { command: 'cmd2', projectPath: '/test', mode: 'print' },
        mockWindow as any
      )

      expect(getActiveProcesses().length).toBe(2)

      cleanupAllProcesses()

      expect(mockProcess1.kill).toHaveBeenCalledWith('SIGKILL')
      expect(mockProcess2.kill).toHaveBeenCalledWith('SIGKILL')
      expect(getActiveProcesses().length).toBe(0)
    })
  })
})
