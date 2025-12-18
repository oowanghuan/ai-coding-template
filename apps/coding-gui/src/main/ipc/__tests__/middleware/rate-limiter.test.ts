/**
 * Rate Limiter Middleware 单元测试
 * 对应 60_TEST_PLAN.md RL-001 ~ RL-003
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import {
  checkRateLimit,
  getRemainingWaitTime,
  resetRateLimit,
  createRateLimiterMiddleware
} from '../../middleware/rate-limiter'

describe('Rate Limiter Middleware', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    // 重置所有限制
    resetRateLimit('cli:execute')
    resetRateLimit('project:open')
    resetRateLimit('file:read')
    resetRateLimit('approval:submit')
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  describe('RL-001: 正常频率通过', () => {
    it('should allow first request', () => {
      const allowed = checkRateLimit('cli:execute')

      expect(allowed).toBe(true)
    })

    it('should allow requests within limit', () => {
      // cli:execute 限制是 1 秒内 5 次
      for (let i = 0; i < 5; i++) {
        const allowed = checkRateLimit('cli:execute')
        expect(allowed).toBe(true)
      }
    })

    it('should allow requests for different channels independently', () => {
      // 填满 cli:execute 限制
      for (let i = 0; i < 5; i++) {
        checkRateLimit('cli:execute')
      }

      // project:open 仍然可以
      const allowed = checkRateLimit('project:open')
      expect(allowed).toBe(true)
    })
  })

  describe('RL-002: 超过限制拒绝', () => {
    it('should reject when limit exceeded', () => {
      // cli:execute 限制是 1 秒内 5 次
      for (let i = 0; i < 5; i++) {
        checkRateLimit('cli:execute')
      }

      const allowed = checkRateLimit('cli:execute')
      expect(allowed).toBe(false)
    })

    it('should return remaining wait time', () => {
      // 填满限制
      for (let i = 0; i < 5; i++) {
        checkRateLimit('cli:execute')
      }

      const waitTime = getRemainingWaitTime('cli:execute')
      expect(waitTime).toBeGreaterThan(0)
      expect(waitTime).toBeLessThanOrEqual(1000)
    })
  })

  describe('RL-003: 窗口重置后恢复', () => {
    it('should reset after window expires', () => {
      // 填满限制
      for (let i = 0; i < 5; i++) {
        checkRateLimit('cli:execute')
      }

      // 确认被限制
      expect(checkRateLimit('cli:execute')).toBe(false)

      // 推进时间超过窗口 (1 秒)
      vi.advanceTimersByTime(1100)

      // 应该可以再次请求
      expect(checkRateLimit('cli:execute')).toBe(true)
    })

    it('should return 0 wait time after window expires', () => {
      for (let i = 0; i < 5; i++) {
        checkRateLimit('cli:execute')
      }

      vi.advanceTimersByTime(1100)

      const waitTime = getRemainingWaitTime('cli:execute')
      expect(waitTime).toBe(0)
    })
  })

  describe('resetRateLimit', () => {
    it('should reset limit for specific channel', () => {
      // 填满限制
      for (let i = 0; i < 5; i++) {
        checkRateLimit('cli:execute')
      }

      expect(checkRateLimit('cli:execute')).toBe(false)

      resetRateLimit('cli:execute')

      expect(checkRateLimit('cli:execute')).toBe(true)
    })
  })

  describe('createRateLimiterMiddleware', () => {
    it('should allow and call next when within limit', async () => {
      const middleware = createRateLimiterMiddleware()
      const next = vi.fn().mockResolvedValue('success')

      const result = await middleware('cli:execute', [{}], next)

      expect(next).toHaveBeenCalled()
      expect(result).toBe('success')
    })

    it('should throw error when limit exceeded', async () => {
      const middleware = createRateLimiterMiddleware()
      const next = vi.fn()

      // 填满限制
      for (let i = 0; i < 5; i++) {
        await middleware('cli:execute', [{}], vi.fn().mockResolvedValue('ok'))
      }

      await expect(middleware('cli:execute', [{}], next)).rejects.toThrow()
      expect(next).not.toHaveBeenCalled()
    })

    it('should include retry info in error', async () => {
      const middleware = createRateLimiterMiddleware()

      // 填满限制
      for (let i = 0; i < 5; i++) {
        await middleware('cli:execute', [{}], vi.fn().mockResolvedValue('ok'))
      }

      try {
        await middleware('cli:execute', [{}], vi.fn())
        expect.fail('Should have thrown')
      } catch (error: any) {
        expect(error.details).toHaveProperty('channel', 'cli:execute')
        expect(error.details).toHaveProperty('retryAfterMs')
      }
    })
  })

  describe('不同通道的限制配置', () => {
    it('should have stricter limit for cli:execute', async () => {
      // cli:execute: 5 requests per second
      for (let i = 0; i < 5; i++) {
        expect(checkRateLimit('cli:execute')).toBe(true)
      }
      expect(checkRateLimit('cli:execute')).toBe(false)
    })

    it('should have more lenient limit for file:read', async () => {
      // file:read: 100 requests per second
      for (let i = 0; i < 100; i++) {
        expect(checkRateLimit('file:read')).toBe(true)
      }
      expect(checkRateLimit('file:read')).toBe(false)
    })

    it('should have strict limit for approval:submit', async () => {
      // approval:submit: 5 requests per second
      for (let i = 0; i < 5; i++) {
        expect(checkRateLimit('approval:submit')).toBe(true)
      }
      expect(checkRateLimit('approval:submit')).toBe(false)
    })

    it('should use default limit for unknown channels', async () => {
      // _default: 100 requests per second
      for (let i = 0; i < 100; i++) {
        expect(checkRateLimit('unknown:channel')).toBe(true)
      }
      expect(checkRateLimit('unknown:channel')).toBe(false)
    })
  })
})
