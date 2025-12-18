/**
 * useCliOutput Composable 单元测试
 * CO-001 ~ CO-003: CLI 输出订阅生命周期测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useCliOutput } from '../useCliOutput'

// Mock window.electronAPI
let eventHandlers: Map<string, Function> = new Map()
const mockOn = vi.fn((channel: string, handler: Function) => {
  eventHandlers.set(channel, handler)
  // Return unsubscribe function
  return () => {
    eventHandlers.delete(channel)
  }
})

vi.stubGlobal('window', {
  electronAPI: {
    on: mockOn
  }
})

// Helper to trigger events
function triggerEvent(channel: string, data: any) {
  const handler = eventHandlers.get(channel)
  if (handler) {
    handler({}, data)
  }
}

describe('useCliOutput', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    eventHandlers.clear()
  })

  describe('CO-001: 初始状态', () => {
    it('should not be subscribed initially when autoSubscribe is false', () => {
      const { isSubscribed } = useCliOutput({ autoSubscribe: false })
      expect(isSubscribed.value).toBe(false)
    })

    it('should have empty outputBuffer initially', () => {
      const { outputBuffer } = useCliOutput({ autoSubscribe: false })
      expect(outputBuffer.value).toEqual([])
    })
  })

  describe('subscribe', () => {
    it('should subscribe to cli:output events', () => {
      const { subscribe, isSubscribed } = useCliOutput({ autoSubscribe: false })

      subscribe()

      expect(isSubscribed.value).toBe(true)
      expect(mockOn).toHaveBeenCalledWith('cli:output', expect.any(Function))
    })

    it('should not subscribe twice', () => {
      const { subscribe } = useCliOutput({ autoSubscribe: false })

      subscribe()
      subscribe()

      expect(mockOn).toHaveBeenCalledTimes(1)
    })
  })

  describe('unsubscribe', () => {
    it('should unsubscribe from cli:output events', () => {
      const { subscribe, unsubscribe, isSubscribed } = useCliOutput({ autoSubscribe: false })

      subscribe()
      expect(isSubscribed.value).toBe(true)

      unsubscribe()
      expect(isSubscribed.value).toBe(false)
    })

    it('should not error when unsubscribing without subscription', () => {
      const { unsubscribe } = useCliOutput({ autoSubscribe: false })

      expect(() => unsubscribe()).not.toThrow()
    })
  })

  describe('CO-002: executionId 过滤', () => {
    it('should filter events by executionId', () => {
      const { subscribe, outputBuffer } = useCliOutput({
        autoSubscribe: false,
        executionId: 'exec-123'
      })

      subscribe()

      // Trigger event for matching executionId
      triggerEvent('cli:output', {
        executionId: 'exec-123',
        type: 'stdout',
        content: 'Matched',
        timestamp: ''
      })

      // Trigger event for different executionId
      triggerEvent('cli:output', {
        executionId: 'exec-456',
        type: 'stdout',
        content: 'Not matched',
        timestamp: ''
      })

      expect(outputBuffer.value.length).toBe(1)
      expect(outputBuffer.value[0].content).toBe('Matched')
    })

    it('should accept all events when no executionId filter', () => {
      const { subscribe, outputBuffer } = useCliOutput({
        autoSubscribe: false
      })

      subscribe()

      triggerEvent('cli:output', {
        executionId: 'exec-123',
        type: 'stdout',
        content: 'Event 1',
        timestamp: ''
      })

      triggerEvent('cli:output', {
        executionId: 'exec-456',
        type: 'stdout',
        content: 'Event 2',
        timestamp: ''
      })

      expect(outputBuffer.value.length).toBe(2)
    })
  })

  describe('onOutput callback', () => {
    it('should call onOutput for each event', () => {
      const onOutput = vi.fn()
      const { subscribe } = useCliOutput({
        autoSubscribe: false,
        onOutput
      })

      subscribe()

      triggerEvent('cli:output', {
        executionId: 'exec-123',
        type: 'stdout',
        content: 'Hello',
        timestamp: ''
      })

      expect(onOutput).toHaveBeenCalledWith(expect.objectContaining({
        content: 'Hello'
      }))
    })
  })

  describe('onComplete callback', () => {
    it('should call onComplete when process exits', () => {
      const onComplete = vi.fn()
      const { subscribe } = useCliOutput({
        autoSubscribe: false,
        onComplete
      })

      subscribe()

      triggerEvent('cli:output', {
        executionId: 'exec-123',
        type: 'system',
        content: 'Process exited with code 0',
        timestamp: ''
      })

      expect(onComplete).toHaveBeenCalledWith('exec-123', 0)
    })

    it('should parse non-zero exit codes', () => {
      const onComplete = vi.fn()
      const { subscribe } = useCliOutput({
        autoSubscribe: false,
        onComplete
      })

      subscribe()

      triggerEvent('cli:output', {
        executionId: 'exec-123',
        type: 'system',
        content: 'Process exited with code 127',
        timestamp: ''
      })

      expect(onComplete).toHaveBeenCalledWith('exec-123', 127)
    })
  })

  describe('clearBuffer', () => {
    it('should clear outputBuffer', () => {
      const { subscribe, outputBuffer, clearBuffer } = useCliOutput({
        autoSubscribe: false
      })

      subscribe()

      triggerEvent('cli:output', {
        executionId: 'exec-123',
        type: 'stdout',
        content: 'Hello',
        timestamp: ''
      })

      expect(outputBuffer.value.length).toBe(1)

      clearBuffer()

      expect(outputBuffer.value).toEqual([])
    })
  })

  describe('getOutputForExecution', () => {
    it('should return events for specific execution', () => {
      const { subscribe, getOutputForExecution } = useCliOutput({
        autoSubscribe: false
      })

      subscribe()

      triggerEvent('cli:output', {
        executionId: 'exec-123',
        type: 'stdout',
        content: 'Event 1',
        timestamp: ''
      })

      triggerEvent('cli:output', {
        executionId: 'exec-456',
        type: 'stdout',
        content: 'Event 2',
        timestamp: ''
      })

      triggerEvent('cli:output', {
        executionId: 'exec-123',
        type: 'stdout',
        content: 'Event 3',
        timestamp: ''
      })

      const exec123Events = getOutputForExecution('exec-123')

      expect(exec123Events.length).toBe(2)
      expect(exec123Events.every(e => e.executionId === 'exec-123')).toBe(true)
    })
  })

  describe('CO-003: 生命周期管理', () => {
    it('should handle multiple subscribe/unsubscribe cycles', () => {
      const { subscribe, unsubscribe, isSubscribed, outputBuffer } = useCliOutput({
        autoSubscribe: false
      })

      // First cycle
      subscribe()
      triggerEvent('cli:output', { executionId: '1', type: 'stdout', content: 'A', timestamp: '' })
      expect(outputBuffer.value.length).toBe(1)
      unsubscribe()

      // Should not receive events when unsubscribed
      triggerEvent('cli:output', { executionId: '2', type: 'stdout', content: 'B', timestamp: '' })
      expect(outputBuffer.value.length).toBe(1) // Still 1

      // Second cycle
      subscribe()
      triggerEvent('cli:output', { executionId: '3', type: 'stdout', content: 'C', timestamp: '' })
      expect(outputBuffer.value.length).toBe(2)

      unsubscribe()
      expect(isSubscribed.value).toBe(false)
    })

    it('should buffer events correctly during subscription', () => {
      const { subscribe, outputBuffer } = useCliOutput({ autoSubscribe: false })

      subscribe()

      for (let i = 0; i < 5; i++) {
        triggerEvent('cli:output', {
          executionId: 'exec-123',
          type: 'stdout',
          content: `Line ${i}`,
          timestamp: ''
        })
      }

      expect(outputBuffer.value.length).toBe(5)
      expect(outputBuffer.value[0].content).toBe('Line 0')
      expect(outputBuffer.value[4].content).toBe('Line 4')
    })
  })
})
