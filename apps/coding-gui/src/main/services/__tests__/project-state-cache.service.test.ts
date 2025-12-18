/**
 * Project State Cache Service 单元测试
 * 对应 60_TEST_PLAN.md PC-001 ~ PC-009
 *
 * 关键测试：PC-007 验证 WARN-001 修复（refresh 无 loader 的行为）
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

describe('ProjectStateCacheService', () => {
  let ProjectStateCacheService: any
  let projectStateCacheService: any

  const mockProject = {
    path: '/test/project',
    name: 'Test Project',
    features: []
  }

  beforeEach(async () => {
    vi.clearAllMocks()
    vi.resetModules()
    vi.useFakeTimers()

    const module = await import('../project-state-cache.service')
    ProjectStateCacheService = module.ProjectStateCacheService

    // 重置单例
    ;(ProjectStateCacheService as any).instance = null
    projectStateCacheService = ProjectStateCacheService.getInstance()
  })

  afterEach(() => {
    projectStateCacheService.clear()
    vi.useRealTimers()
  })

  describe('PC-001: get 缓存命中', () => {
    it('should return cached data and emit cache-hit', () => {
      const hitHandler = vi.fn()
      projectStateCacheService.on('cache-hit', hitHandler)

      // 设置缓存
      projectStateCacheService.set('/test/project', mockProject)

      // 获取缓存
      const result = projectStateCacheService.get('/test/project')

      expect(result).toEqual(mockProject)
      expect(hitHandler).toHaveBeenCalledWith({ projectPath: '/test/project' })
    })
  })

  describe('PC-002: get 缓存未命中', () => {
    it('should return null and emit cache-miss', () => {
      const missHandler = vi.fn()
      projectStateCacheService.on('cache-miss', missHandler)

      const result = projectStateCacheService.get('/nonexistent/project')

      expect(result).toBeNull()
      expect(missHandler).toHaveBeenCalledWith({ projectPath: '/nonexistent/project' })
    })
  })

  describe('PC-003: get 缓存过期', () => {
    it('should return null and emit cache-expired after TTL', () => {
      const expiredHandler = vi.fn()
      projectStateCacheService.on('cache-expired', expiredHandler)

      // 设置缓存
      projectStateCacheService.set('/test/project', mockProject)

      // 推进时间超过 TTL (5 分钟)
      vi.advanceTimersByTime(5 * 60 * 1000 + 1000)

      const result = projectStateCacheService.get('/test/project')

      expect(result).toBeNull()
      expect(expiredHandler).toHaveBeenCalledWith({ projectPath: '/test/project' })
    })
  })

  describe('PC-004: set 超过 maxSize 触发 LRU 淘汰', () => {
    it('should evict oldest entry when maxSize exceeded', () => {
      const evictHandler = vi.fn()
      projectStateCacheService.on('cache-evict', evictHandler)

      // 填满缓存 (maxSize = 10)
      for (let i = 0; i < 10; i++) {
        projectStateCacheService.set(`/project/${i}`, { ...mockProject, path: `/project/${i}` })
        vi.advanceTimersByTime(100) // 让每个有不同的 accessedAt
      }

      // 访问第一个以外的所有项目，让第一个成为最旧的
      for (let i = 1; i < 10; i++) {
        projectStateCacheService.get(`/project/${i}`)
      }

      // 添加第 11 个
      projectStateCacheService.set('/project/10', { ...mockProject, path: '/project/10' })

      // 应该淘汰最旧的 /project/0
      expect(evictHandler).toHaveBeenCalledWith({
        projectPath: '/project/0',
        reason: 'lru'
      })

      // 验证 /project/0 被删除
      expect(projectStateCacheService.get('/project/0')).toBeNull()
    })
  })

  describe('PC-005: invalidate 删除缓存', () => {
    it('should delete cache entry and emit event', () => {
      const invalidateHandler = vi.fn()
      projectStateCacheService.on('cache-invalidate', invalidateHandler)

      projectStateCacheService.set('/test/project', mockProject)
      projectStateCacheService.invalidate('/test/project')

      expect(projectStateCacheService.get('/test/project')).toBeNull()
      expect(invalidateHandler).toHaveBeenCalledWith({ projectPath: '/test/project' })
    })

    it('should not emit event if entry does not exist', () => {
      const invalidateHandler = vi.fn()
      projectStateCacheService.on('cache-invalidate', invalidateHandler)

      projectStateCacheService.invalidate('/nonexistent/project')

      expect(invalidateHandler).not.toHaveBeenCalled()
    })
  })

  describe('PC-006: refresh 带 loader', () => {
    it('should call loader and update cache', async () => {
      const newProject = { ...mockProject, name: 'Updated Project' }
      const loader = vi.fn().mockResolvedValue(newProject)

      const result = await projectStateCacheService.refresh('/test/project', loader)

      expect(loader).toHaveBeenCalled()
      expect(result).toEqual(newProject)
      expect(projectStateCacheService.get('/test/project')).toEqual(newProject)
    })

    it('should emit refresh-failed on loader error', async () => {
      const failHandler = vi.fn()
      projectStateCacheService.on('refresh-failed', failHandler)

      const loader = vi.fn().mockRejectedValue(new Error('Load failed'))

      const result = await projectStateCacheService.refresh('/test/project', loader)

      expect(result).toBeNull()
      expect(failHandler).toHaveBeenCalledWith({
        projectPath: '/test/project',
        error: expect.any(Error)
      })
    })
  })

  describe('PC-007: refresh 无 loader (WARN-001 验证)', () => {
    it('should return null when no cache and no loader', async () => {
      // 这是 WARN-001 的验证测试
      // 当没有 loader 且缓存不存在时，应该返回 null
      const result = await projectStateCacheService.refresh('/nonexistent/project')

      expect(result).toBeNull()
    })

    it('should return cached data when cache exists and no loader', async () => {
      // 先设置缓存
      projectStateCacheService.set('/test/project', mockProject)

      // 不传 loader 调用 refresh
      const result = await projectStateCacheService.refresh('/test/project')

      // 应该返回现有缓存
      expect(result).toEqual(mockProject)
    })

    it('should not throw error when called without loader', async () => {
      // 确保不会抛出异常
      await expect(
        projectStateCacheService.refresh('/any/path')
      ).resolves.not.toThrow()
    })
  })

  describe('PC-008: subscribe 收到状态变更通知', () => {
    it('should notify subscriber when cache is updated', () => {
      const callback = vi.fn()

      projectStateCacheService.subscribe('/test/project', callback)
      projectStateCacheService.set('/test/project', mockProject)

      expect(callback).toHaveBeenCalledWith(mockProject)
    })

    it('should return unsubscribe function', () => {
      const callback = vi.fn()

      const unsubscribe = projectStateCacheService.subscribe('/test/project', callback)
      unsubscribe()

      projectStateCacheService.set('/test/project', mockProject)

      expect(callback).not.toHaveBeenCalled()
    })

    it('should handle multiple subscribers', () => {
      const callback1 = vi.fn()
      const callback2 = vi.fn()

      projectStateCacheService.subscribe('/test/project', callback1)
      projectStateCacheService.subscribe('/test/project', callback2)
      projectStateCacheService.set('/test/project', mockProject)

      expect(callback1).toHaveBeenCalledWith(mockProject)
      expect(callback2).toHaveBeenCalledWith(mockProject)
    })
  })

  describe('PC-009: cleanupExpired 定期清理', () => {
    it('should cleanup expired entries periodically', () => {
      const evictHandler = vi.fn()
      projectStateCacheService.on('cache-evict', evictHandler)

      // 设置缓存
      projectStateCacheService.set('/test/project', mockProject)

      // 推进时间超过 TTL
      vi.advanceTimersByTime(5 * 60 * 1000 + 1000)

      // 推进到定期清理时间 (60 秒)
      vi.advanceTimersByTime(60 * 1000)

      expect(evictHandler).toHaveBeenCalledWith({
        projectPath: '/test/project',
        reason: 'expired'
      })
    })
  })

  describe('getStats', () => {
    it('should return correct cache statistics', () => {
      projectStateCacheService.set('/project/1', { ...mockProject, path: '/project/1' })
      projectStateCacheService.set('/project/2', { ...mockProject, path: '/project/2' })

      // 访问一个以增加 accessCount
      projectStateCacheService.get('/project/1')
      projectStateCacheService.get('/project/1')

      const stats = projectStateCacheService.getStats()

      expect(stats.size).toBe(2)
      expect(stats.maxSize).toBe(10)
      expect(stats.entries.length).toBe(2)

      const entry1 = stats.entries.find((e: any) => e.path === '/project/1')
      expect(entry1?.accessCount).toBe(3) // 1 from set + 2 from get
    })
  })

  describe('clear', () => {
    it('should clear all cache entries', () => {
      const clearHandler = vi.fn()
      projectStateCacheService.on('cache-clear', clearHandler)

      projectStateCacheService.set('/project/1', mockProject)
      projectStateCacheService.set('/project/2', mockProject)

      projectStateCacheService.clear()

      expect(projectStateCacheService.getStats().size).toBe(0)
      expect(clearHandler).toHaveBeenCalled()
    })
  })
})
