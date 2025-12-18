/**
 * File Handler 单元测试
 * 对应 60_TEST_PLAN.md FH-001 ~ FH-003
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

// Mock fs/promises
vi.mock('fs/promises', () => ({
  readFile: vi.fn(),
  stat: vi.fn()
}))

// Mock chokidar
vi.mock('chokidar', () => ({
  watch: vi.fn(() => ({
    on: vi.fn().mockReturnThis(),
    close: vi.fn()
  }))
}))

// Mock Electron
vi.mock('electron', () => ({
  BrowserWindow: vi.fn()
}))

describe('File Handler', () => {
  let handleFileRead: any
  let startFileWatch: any
  let stopFileWatch: any
  let stopAllFileWatches: any
  let getActiveWatcherCount: any
  let readFile: any
  let stat: any
  let watch: any

  beforeEach(async () => {
    vi.clearAllMocks()
    vi.resetModules()

    const fs = await import('fs/promises')
    readFile = vi.mocked(fs.readFile)
    stat = vi.mocked(fs.stat)

    const chokidar = await import('chokidar')
    watch = vi.mocked(chokidar.watch)

    const module = await import('../../handlers/file.handler')
    handleFileRead = module.handleFileRead
    startFileWatch = module.startFileWatch
    stopFileWatch = module.stopFileWatch
    stopAllFileWatches = module.stopAllFileWatches
    getActiveWatcherCount = module.getActiveWatcherCount
  })

  afterEach(() => {
    stopAllFileWatches()
  })

  describe('FH-001: file:read 有效路径', () => {
    it('should return file content for valid path', async () => {
      stat.mockResolvedValue({
        isFile: () => true,
        size: 100,
        mtime: new Date('2024-12-17')
      })
      readFile.mockResolvedValue('# Hello World\n\nThis is content.')

      const result = await handleFileRead({
        path: '/test/project/docs/README.md',
        projectPath: '/test/project'
      })

      expect(result.content).toBe('# Hello World\n\nThis is content.')
      expect(result.path).toBe('/test/project/docs/README.md')
      expect(result.size).toBe(100)
      expect(result.mimeType).toBe('text/markdown')
    })

    it('should detect correct MIME types', async () => {
      stat.mockResolvedValue({
        isFile: () => true,
        size: 50,
        mtime: new Date()
      })
      readFile.mockResolvedValue('content')

      const testCases = [
        { path: '/test/file.md', expectedMime: 'text/markdown' },
        { path: '/test/file.yaml', expectedMime: 'text/yaml' },
        { path: '/test/file.yml', expectedMime: 'text/yaml' },
        { path: '/test/file.json', expectedMime: 'application/json' },
        { path: '/test/file.ts', expectedMime: 'text/typescript' },
        { path: '/test/file.tsx', expectedMime: 'text/typescript' },
        { path: '/test/file.js', expectedMime: 'text/javascript' },
        { path: '/test/file.vue', expectedMime: 'text/vue' },
        { path: '/test/file.css', expectedMime: 'text/css' },
        { path: '/test/file.html', expectedMime: 'text/html' },
        { path: '/test/file.unknown', expectedMime: 'text/plain' }
      ]

      for (const { path, expectedMime } of testCases) {
        const result = await handleFileRead({ path, projectPath: '/test' })
        expect(result.mimeType).toBe(expectedMime)
      }
    })
  })

  describe('FH-002: file:read 路径穿越', () => {
    // 注意：实际的路径穿越验证在 path-validator 中间件中完成
    // 这里测试 handler 本身的错误处理

    it('should throw error for non-existent file', async () => {
      stat.mockRejectedValue({ code: 'ENOENT' })

      await expect(
        handleFileRead({ path: '/test/nonexistent.md', projectPath: '/test' })
      ).rejects.toThrow(/not found/i)
    })

    it('should throw error for permission denied', async () => {
      stat.mockRejectedValue({ code: 'EACCES' })

      await expect(
        handleFileRead({ path: '/test/protected.md', projectPath: '/test' })
      ).rejects.toThrow(/permission/i)
    })
  })

  describe('FH-003: file:watch 建立监控', () => {
    it('should create watcher for project path', () => {
      const mockWindow = {
        webContents: { send: vi.fn() }
      }

      const mockWatcher = {
        on: vi.fn().mockReturnThis(),
        close: vi.fn()
      }
      watch.mockReturnValue(mockWatcher)

      startFileWatch('/test/project', mockWindow as any)

      expect(watch).toHaveBeenCalledWith(
        expect.arrayContaining([
          expect.stringContaining('/test/project')
        ]),
        expect.any(Object)
      )
      expect(getActiveWatcherCount()).toBe(1)
    })

    it('should register change event handler', () => {
      const mockWindow = {
        webContents: { send: vi.fn() }
      }

      const eventHandlers: Record<string, Function> = {}
      const mockWatcher = {
        on: vi.fn().mockImplementation((event: string, handler: Function) => {
          eventHandlers[event] = handler
          return mockWatcher
        }),
        close: vi.fn()
      }
      watch.mockReturnValue(mockWatcher)

      startFileWatch('/test/project', mockWindow as any)

      expect(eventHandlers['change']).toBeDefined()
      expect(eventHandlers['add']).toBeDefined()
      expect(eventHandlers['unlink']).toBeDefined()
    })

    it('should stop previous watcher when starting new one for same path', () => {
      const mockWindow = {
        webContents: { send: vi.fn() }
      }

      const mockWatcher1 = {
        on: vi.fn().mockReturnThis(),
        close: vi.fn()
      }
      const mockWatcher2 = {
        on: vi.fn().mockReturnThis(),
        close: vi.fn()
      }

      watch.mockReturnValueOnce(mockWatcher1).mockReturnValueOnce(mockWatcher2)

      startFileWatch('/test/project', mockWindow as any)
      startFileWatch('/test/project', mockWindow as any)

      expect(mockWatcher1.close).toHaveBeenCalled()
      expect(getActiveWatcherCount()).toBe(1)
    })
  })

  describe('File size limits', () => {
    it('should reject files exceeding max size', async () => {
      stat.mockResolvedValue({
        isFile: () => true,
        size: 10 * 1024 * 1024, // 10MB
        mtime: new Date()
      })

      await expect(
        handleFileRead({
          path: '/test/large-file.md',
          projectPath: '/test',
          maxSize: 5 * 1024 * 1024 // 5MB limit
        })
      ).rejects.toThrow(/too large/i)
    })

    it('should accept files within size limit', async () => {
      stat.mockResolvedValue({
        isFile: () => true,
        size: 1024, // 1KB
        mtime: new Date()
      })
      readFile.mockResolvedValue('content')

      const result = await handleFileRead({
        path: '/test/small-file.md',
        projectPath: '/test'
      })

      expect(result.content).toBe('content')
    })
  })

  describe('stopFileWatch', () => {
    it('should close watcher for specific path', () => {
      const mockWindow = {
        webContents: { send: vi.fn() }
      }

      const mockWatcher = {
        on: vi.fn().mockReturnThis(),
        close: vi.fn()
      }
      watch.mockReturnValue(mockWatcher)

      startFileWatch('/test/project', mockWindow as any)
      expect(getActiveWatcherCount()).toBe(1)

      stopFileWatch('/test/project')
      expect(mockWatcher.close).toHaveBeenCalled()
      expect(getActiveWatcherCount()).toBe(0)
    })
  })

  describe('stopAllFileWatches', () => {
    it('should close all active watchers', () => {
      const mockWindow = {
        webContents: { send: vi.fn() }
      }

      const mockWatcher1 = { on: vi.fn().mockReturnThis(), close: vi.fn() }
      const mockWatcher2 = { on: vi.fn().mockReturnThis(), close: vi.fn() }

      watch.mockReturnValueOnce(mockWatcher1).mockReturnValueOnce(mockWatcher2)

      startFileWatch('/test/project1', mockWindow as any)
      startFileWatch('/test/project2', mockWindow as any)
      expect(getActiveWatcherCount()).toBe(2)

      stopAllFileWatches()

      expect(mockWatcher1.close).toHaveBeenCalled()
      expect(mockWatcher2.close).toHaveBeenCalled()
      expect(getActiveWatcherCount()).toBe(0)
    })
  })
})
