/**
 * useFileWatch Composable 单元测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useFileWatch } from '../useFileWatch'

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

describe('useFileWatch', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    eventHandlers.clear()
  })

  describe('Initial State', () => {
    it('should not be subscribed initially when autoSubscribe is false', () => {
      const { isSubscribed } = useFileWatch({ autoSubscribe: false })
      expect(isSubscribed.value).toBe(false)
    })

    it('should have empty recentChanges initially', () => {
      const { recentChanges } = useFileWatch({ autoSubscribe: false })
      expect(recentChanges.value).toEqual([])
    })
  })

  describe('subscribe', () => {
    it('should subscribe to file:change events', () => {
      const { subscribe, isSubscribed } = useFileWatch({ autoSubscribe: false })

      subscribe()

      expect(isSubscribed.value).toBe(true)
      expect(mockOn).toHaveBeenCalledWith('file:change', expect.any(Function))
    })

    it('should not subscribe twice', () => {
      const { subscribe } = useFileWatch({ autoSubscribe: false })

      subscribe()
      subscribe()

      expect(mockOn).toHaveBeenCalledTimes(1)
    })
  })

  describe('unsubscribe', () => {
    it('should unsubscribe from file:change events', () => {
      const { subscribe, unsubscribe, isSubscribed } = useFileWatch({ autoSubscribe: false })

      subscribe()
      expect(isSubscribed.value).toBe(true)

      unsubscribe()
      expect(isSubscribed.value).toBe(false)
    })
  })

  describe('onChange callback', () => {
    it('should call onChange for each file change event', () => {
      const onChange = vi.fn()
      const { subscribe } = useFileWatch({
        autoSubscribe: false,
        onChange
      })

      subscribe()

      triggerEvent('file:change', {
        path: '/test/file.md',
        type: 'change',
        timestamp: '2024-12-17T00:00:00Z'
      })

      expect(onChange).toHaveBeenCalledWith(expect.objectContaining({
        path: '/test/file.md',
        type: 'change'
      }))
    })
  })

  describe('pathFilter', () => {
    it('should filter events by path', () => {
      const onChange = vi.fn()
      const { subscribe, recentChanges } = useFileWatch({
        autoSubscribe: false,
        pathFilter: (path) => path.endsWith('.md'),
        onChange
      })

      subscribe()

      // Trigger matching event
      triggerEvent('file:change', {
        path: '/test/file.md',
        type: 'change',
        timestamp: ''
      })

      // Trigger non-matching event
      triggerEvent('file:change', {
        path: '/test/file.ts',
        type: 'change',
        timestamp: ''
      })

      expect(recentChanges.value.length).toBe(1)
      expect(recentChanges.value[0].path).toBe('/test/file.md')
      expect(onChange).toHaveBeenCalledTimes(1)
    })

    it('should accept all events when no pathFilter', () => {
      const { subscribe, recentChanges } = useFileWatch({ autoSubscribe: false })

      subscribe()

      triggerEvent('file:change', { path: '/test/file.md', type: 'change', timestamp: '' })
      triggerEvent('file:change', { path: '/test/file.ts', type: 'change', timestamp: '' })

      expect(recentChanges.value.length).toBe(2)
    })
  })

  describe('recentChanges buffer', () => {
    it('should buffer file change events', () => {
      const { subscribe, recentChanges } = useFileWatch({ autoSubscribe: false })

      subscribe()

      for (let i = 0; i < 5; i++) {
        triggerEvent('file:change', {
          path: `/test/file${i}.md`,
          type: 'change',
          timestamp: ''
        })
      }

      expect(recentChanges.value.length).toBe(5)
    })

    it('should limit to MAX_EVENTS (100)', () => {
      const { subscribe, recentChanges } = useFileWatch({ autoSubscribe: false })

      subscribe()

      for (let i = 0; i < 105; i++) {
        triggerEvent('file:change', {
          path: `/test/file${i}.md`,
          type: 'change',
          timestamp: ''
        })
      }

      expect(recentChanges.value.length).toBe(100)
    })
  })

  describe('clearChanges', () => {
    it('should clear recentChanges', () => {
      const { subscribe, recentChanges, clearChanges } = useFileWatch({ autoSubscribe: false })

      subscribe()

      triggerEvent('file:change', { path: '/test/file.md', type: 'change', timestamp: '' })

      expect(recentChanges.value.length).toBe(1)

      clearChanges()

      expect(recentChanges.value).toEqual([])
    })
  })

  describe('hasChanged', () => {
    it('should return true if file has changed', () => {
      const { subscribe, hasChanged } = useFileWatch({ autoSubscribe: false })

      subscribe()

      triggerEvent('file:change', { path: '/test/file.md', type: 'change', timestamp: '' })

      expect(hasChanged('/test/file.md')).toBe(true)
      expect(hasChanged('/test/other.md')).toBe(false)
    })
  })

  describe('getLatestChange', () => {
    it('should return latest change for file', () => {
      const { subscribe, getLatestChange } = useFileWatch({ autoSubscribe: false })

      subscribe()

      triggerEvent('file:change', {
        path: '/test/file.md',
        type: 'change',
        timestamp: '2024-12-17T00:00:00Z'
      })

      triggerEvent('file:change', {
        path: '/test/file.md',
        type: 'change',
        timestamp: '2024-12-17T01:00:00Z'
      })

      const latest = getLatestChange('/test/file.md')

      expect(latest).toBeDefined()
      expect(latest?.timestamp).toBe('2024-12-17T01:00:00Z')
    })

    it('should return undefined for file without changes', () => {
      const { getLatestChange } = useFileWatch({ autoSubscribe: false })

      const latest = getLatestChange('/test/file.md')

      expect(latest).toBeUndefined()
    })
  })

  describe('File change types', () => {
    it('should handle add events', () => {
      const onChange = vi.fn()
      const { subscribe } = useFileWatch({ autoSubscribe: false, onChange })

      subscribe()

      triggerEvent('file:change', {
        path: '/test/new-file.md',
        type: 'add',
        timestamp: ''
      })

      expect(onChange).toHaveBeenCalledWith(expect.objectContaining({
        type: 'add'
      }))
    })

    it('should handle unlink events', () => {
      const onChange = vi.fn()
      const { subscribe } = useFileWatch({ autoSubscribe: false, onChange })

      subscribe()

      triggerEvent('file:change', {
        path: '/test/deleted-file.md',
        type: 'unlink',
        timestamp: ''
      })

      expect(onChange).toHaveBeenCalledWith(expect.objectContaining({
        type: 'unlink'
      }))
    })
  })

  describe('Lifecycle management', () => {
    it('should not receive events after unsubscribe', () => {
      const onChange = vi.fn()
      const { subscribe, unsubscribe } = useFileWatch({ autoSubscribe: false, onChange })

      subscribe()

      triggerEvent('file:change', { path: '/test/file1.md', type: 'change', timestamp: '' })
      expect(onChange).toHaveBeenCalledTimes(1)

      unsubscribe()

      triggerEvent('file:change', { path: '/test/file2.md', type: 'change', timestamp: '' })
      expect(onChange).toHaveBeenCalledTimes(1) // Still 1
    })

    it('should handle resubscribe', () => {
      const onChange = vi.fn()
      const { subscribe, unsubscribe } = useFileWatch({ autoSubscribe: false, onChange })

      subscribe()
      unsubscribe()
      subscribe()

      triggerEvent('file:change', { path: '/test/file.md', type: 'change', timestamp: '' })

      expect(onChange).toHaveBeenCalledTimes(1)
    })
  })
})
