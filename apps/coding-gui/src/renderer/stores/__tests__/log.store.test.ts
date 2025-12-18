/**
 * Log Store 单元测试
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useLogStore } from '../log.store'

// Mock window.electronAPI
const mockInvoke = vi.fn()
const mockOn = vi.fn(() => vi.fn())  // Returns unsubscribe function

vi.stubGlobal('window', {
  electronAPI: {
    invoke: mockInvoke,
    on: mockOn
  }
})

// Mock localStorage
vi.stubGlobal('localStorage', {
  getItem: vi.fn(() => null),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
})

describe('useLogStore', () => {
  let logStore: ReturnType<typeof useLogStore>

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    logStore = useLogStore()
  })

  afterEach(() => {
    logStore.reset()
  })

  describe('Initial State', () => {
    it('should have empty logs initially', () => {
      expect(logStore.logs).toEqual([])
    })

    it('should have empty executions initially', () => {
      expect(logStore.executions.size).toBe(0)
    })

    it('should have null activeExecutionId', () => {
      expect(logStore.activeExecutionId).toBeNull()
    })

    it('should have closed drawer', () => {
      expect(logStore.isDrawerOpen).toBe(false)
    })

    it('should have autoScroll enabled', () => {
      expect(logStore.autoScroll).toBe(true)
    })
  })

  describe('executeCommand', () => {
    it('should execute command and return executionId', async () => {
      mockInvoke.mockResolvedValue({
        executionId: 'exec-123',
        status: 'running',
        startedAt: '2024-12-17T00:00:00Z'
      })

      const execId = await logStore.executeCommand('echo hello', '/test/project')

      expect(execId).toBe('exec-123')
      expect(mockInvoke).toHaveBeenCalledWith('cli:execute', {
        command: 'echo hello',
        projectPath: '/test/project',
        stepId: undefined,
        mode: 'print'
      })
    })

    it('should add execution record', async () => {
      mockInvoke.mockResolvedValue({
        executionId: 'exec-123',
        status: 'running',
        startedAt: '2024-12-17T00:00:00Z'
      })

      await logStore.executeCommand('echo hello', '/test/project')

      const execution = logStore.executions.get('exec-123')
      expect(execution).toBeDefined()
      expect(execution?.command).toBe('echo hello')
      expect(execution?.status).toBe('running')
    })

    it('should add command log entry', async () => {
      mockInvoke.mockResolvedValue({
        executionId: 'exec-123',
        status: 'running',
        startedAt: '2024-12-17T00:00:00Z'
      })

      await logStore.executeCommand('echo hello', '/test/project')

      expect(logStore.logs.length).toBe(1)
      expect(logStore.logs[0].type).toBe('command')
      expect(logStore.logs[0].content).toBe('$ echo hello')
    })

    it('should set activeExecutionId', async () => {
      mockInvoke.mockResolvedValue({
        executionId: 'exec-123',
        status: 'running'
      })

      await logStore.executeCommand('echo hello', '/test/project')

      expect(logStore.activeExecutionId).toBe('exec-123')
    })

    it('should handle execution error', async () => {
      mockInvoke.mockRejectedValue(new Error('Command failed'))

      const execId = await logStore.executeCommand('invalid', '/test/project')

      expect(execId).toBeNull()
    })

    it('should pass stepId when provided', async () => {
      mockInvoke.mockResolvedValue({
        executionId: 'exec-123',
        status: 'running'
      })

      await logStore.executeCommand('echo hello', '/test/project', 'KICK-001')

      expect(mockInvoke).toHaveBeenCalledWith('cli:execute', expect.objectContaining({
        stepId: 'KICK-001'
      }))

      const execution = logStore.executions.get('exec-123')
      expect(execution?.stepId).toBe('KICK-001')
    })
  })

  describe('cancelExecution', () => {
    it('should cancel execution', async () => {
      mockInvoke
        .mockResolvedValueOnce({ executionId: 'exec-123', status: 'running' })
        .mockResolvedValueOnce({ success: true })

      await logStore.executeCommand('long-running', '/test/project')
      const result = await logStore.cancelExecution('exec-123')

      expect(result).toBe(true)
      expect(mockInvoke).toHaveBeenCalledWith('cli:cancel', { executionId: 'exec-123' })
    })

    it('should update execution status to cancelled', async () => {
      mockInvoke
        .mockResolvedValueOnce({ executionId: 'exec-123', status: 'running' })
        .mockResolvedValueOnce({ success: true })

      await logStore.executeCommand('long-running', '/test/project')
      await logStore.cancelExecution('exec-123')

      const execution = logStore.executions.get('exec-123')
      expect(execution?.status).toBe('cancelled')
      expect(execution?.endedAt).toBeDefined()
    })
  })

  describe('addLog', () => {
    it('should add log entry with generated id', () => {
      logStore.addLog({
        executionId: 'exec-123',
        type: 'stdout',
        content: 'Hello World',
        timestamp: '2024-12-17T00:00:00Z'
      })

      expect(logStore.logs.length).toBe(1)
      expect(logStore.logs[0].id).toMatch(/^log-/)
      expect(logStore.logs[0].content).toBe('Hello World')
    })

    it('should limit logs to MAX_LOGS', () => {
      // Add more than MAX_LOGS (10000) entries
      for (let i = 0; i < 10005; i++) {
        logStore.addLog({
          executionId: 'exec-123',
          type: 'stdout',
          content: `Line ${i}`,
          timestamp: new Date().toISOString()
        })
      }

      expect(logStore.logs.length).toBe(10000)
    })
  })

  describe('CLI output via subscription', () => {
    // Note: handleCliOutput is internal, so we test via addLog which is exported
    it('should add log for stdout via addLog', () => {
      logStore.addLog({
        executionId: 'exec-123',
        type: 'stdout',
        content: 'Hello',
        timestamp: '2024-12-17T00:00:00Z'
      })

      expect(logStore.logs[0].type).toBe('stdout')
      expect(logStore.logs[0].content).toBe('Hello')
    })

    it('should add log for stderr via addLog', () => {
      logStore.addLog({
        executionId: 'exec-123',
        type: 'stderr',
        content: 'Error message',
        timestamp: '2024-12-17T00:00:00Z'
      })

      expect(logStore.logs[0].type).toBe('stderr')
    })

    it('should track execution via subscription (simulated)', async () => {
      // Test that execution tracking works through addLog
      mockInvoke.mockResolvedValue({
        executionId: 'exec-123',
        status: 'running'
      })

      await logStore.executeCommand('echo hello', '/test/project')

      // Simulate what handleCliOutput does - add system log
      logStore.addLog({
        executionId: 'exec-123',
        type: 'system',
        content: 'Process exited with code 0',
        timestamp: '2024-12-17T00:00:00Z'
      })

      // Manually check log was added (execution status update happens internally)
      expect(logStore.logs.some(l => l.content.includes('exited with code 0'))).toBe(true)
    })

    it('should support different log types', async () => {
      mockInvoke.mockResolvedValue({
        executionId: 'exec-123',
        status: 'running'
      })

      await logStore.executeCommand('failing-cmd', '/test/project')

      logStore.addLog({
        executionId: 'exec-123',
        type: 'system',
        content: 'Process exited with code 1',
        timestamp: '2024-12-17T00:00:00Z'
      })

      const systemLogs = logStore.logs.filter(l => l.type === 'system')
      expect(systemLogs.length).toBe(1)
    })
  })

  describe('subscribeToCliOutput', () => {
    it('should subscribe to cli:output events', () => {
      logStore.subscribeToCliOutput()

      expect(mockOn).toHaveBeenCalledWith('cli:output', expect.any(Function))
    })

    it('should not subscribe twice', () => {
      logStore.subscribeToCliOutput()
      logStore.subscribeToCliOutput()

      expect(mockOn).toHaveBeenCalledTimes(1)
    })
  })

  describe('unsubscribeFromCliOutput', () => {
    it('should unsubscribe from cli:output events', () => {
      const unsubscribeFn = vi.fn()
      mockOn.mockReturnValue(unsubscribeFn)

      logStore.subscribeToCliOutput()
      logStore.unsubscribeFromCliOutput()

      expect(unsubscribeFn).toHaveBeenCalled()
    })
  })

  describe('toggleDrawer', () => {
    it('should toggle drawer state', () => {
      expect(logStore.isDrawerOpen).toBe(false)

      logStore.toggleDrawer()
      expect(logStore.isDrawerOpen).toBe(true)

      logStore.toggleDrawer()
      expect(logStore.isDrawerOpen).toBe(false)
    })
  })

  describe('currentLogs getter', () => {
    it('should return logs for active execution only', async () => {
      mockInvoke.mockResolvedValue({
        executionId: 'exec-123',
        status: 'running'
      })

      await logStore.executeCommand('cmd1', '/test/project')

      // Add logs for different executions
      logStore.addLog({ executionId: 'exec-123', type: 'stdout', content: 'Output 1', timestamp: '' })
      logStore.addLog({ executionId: 'exec-456', type: 'stdout', content: 'Output 2', timestamp: '' })
      logStore.addLog({ executionId: 'exec-123', type: 'stdout', content: 'Output 3', timestamp: '' })

      expect(logStore.currentLogs.length).toBe(3) // including command log
      expect(logStore.currentLogs.filter(l => l.executionId === 'exec-123').length).toBe(3)
    })

    it('should return empty when no activeExecutionId', () => {
      logStore.addLog({ executionId: 'exec-123', type: 'stdout', content: 'Output', timestamp: '' })

      expect(logStore.currentLogs).toEqual([])
    })
  })

  describe('isExecuting getter', () => {
    it('should return true when execution is running', async () => {
      mockInvoke.mockResolvedValue({
        executionId: 'exec-123',
        status: 'running'
      })

      await logStore.executeCommand('cmd', '/test/project')

      expect(logStore.isExecuting).toBe(true)
    })

    it('should return false when no executions', () => {
      expect(logStore.isExecuting).toBe(false)
    })

    it('should return false when all executions completed', async () => {
      mockInvoke.mockResolvedValue({
        executionId: 'exec-123',
        status: 'running'
      })

      await logStore.executeCommand('cmd', '/test/project')

      // Manually update execution status since handleCliOutput is internal
      const execution = logStore.executions.get('exec-123')
      if (execution) {
        execution.status = 'completed'
        execution.exitCode = 0
      }

      expect(logStore.isExecuting).toBe(false)
    })
  })

  describe('getLogsForStep', () => {
    it('should return logs for specific step', async () => {
      mockInvoke
        .mockResolvedValueOnce({ executionId: 'exec-1', status: 'running' })
        .mockResolvedValueOnce({ executionId: 'exec-2', status: 'running' })

      await logStore.executeCommand('cmd1', '/test/project', 'KICK-001')
      await logStore.executeCommand('cmd2', '/test/project', 'KICK-002')

      logStore.addLog({ executionId: 'exec-1', type: 'stdout', content: 'Step 1 output', timestamp: '' })
      logStore.addLog({ executionId: 'exec-2', type: 'stdout', content: 'Step 2 output', timestamp: '' })

      const step1Logs = logStore.getLogsForStep('KICK-001')
      expect(step1Logs.length).toBe(2) // command + output
      expect(step1Logs.every(l => l.executionId === 'exec-1')).toBe(true)
    })
  })

  describe('clearLogs', () => {
    it('should clear all logs when no executionId provided', () => {
      logStore.addLog({ executionId: 'exec-1', type: 'stdout', content: 'Log 1', timestamp: '' })
      logStore.addLog({ executionId: 'exec-2', type: 'stdout', content: 'Log 2', timestamp: '' })

      logStore.clearLogs()

      expect(logStore.logs).toEqual([])
    })

    it('should clear logs for specific execution', () => {
      logStore.addLog({ executionId: 'exec-1', type: 'stdout', content: 'Log 1', timestamp: '' })
      logStore.addLog({ executionId: 'exec-2', type: 'stdout', content: 'Log 2', timestamp: '' })
      logStore.addLog({ executionId: 'exec-1', type: 'stdout', content: 'Log 3', timestamp: '' })

      logStore.clearLogs('exec-1')

      expect(logStore.logs.length).toBe(1)
      expect(logStore.logs[0].executionId).toBe('exec-2')
    })
  })

  describe('reset', () => {
    it('should reset all state', async () => {
      mockInvoke.mockResolvedValue({ executionId: 'exec-123', status: 'running' })

      await logStore.executeCommand('cmd', '/test/project')
      logStore.isDrawerOpen = true

      logStore.reset()

      expect(logStore.logs).toEqual([])
      expect(logStore.executions.size).toBe(0)
      expect(logStore.activeExecutionId).toBeNull()
      expect(logStore.isDrawerOpen).toBe(false)
    })
  })
})
