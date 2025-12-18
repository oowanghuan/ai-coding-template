/**
 * 速率限制中间件
 * CODE-003: IpcRateLimiter - 防止 IPC 滥用
 */

import { ERROR_CODES, createError } from '../../../shared/types/error.types'

interface RateLimitConfig {
  /** 时间窗口（毫秒） */
  windowMs: number
  /** 最大请求数 */
  maxRequests: number
}

interface RequestRecord {
  count: number
  windowStart: number
}

// 默认限制配置
const DEFAULT_LIMITS: Record<string, RateLimitConfig> = {
  // CLI 执行限制较严格
  'cli:execute': { windowMs: 1000, maxRequests: 5 },
  'cli:cancel': { windowMs: 1000, maxRequests: 10 },

  // 项目操作适中
  'project:open': { windowMs: 1000, maxRequests: 10 },
  'project:state': { windowMs: 100, maxRequests: 50 },

  // 文件操作较宽松
  'file:read': { windowMs: 1000, maxRequests: 100 },

  // 审批操作限制严格
  'approval:submit': { windowMs: 1000, maxRequests: 5 },
  'approval:status': { windowMs: 1000, maxRequests: 20 },

  // 默认限制
  '_default': { windowMs: 1000, maxRequests: 100 }
}

// 请求记录存储
const requestRecords = new Map<string, RequestRecord>()

/**
 * 获取通道的限制配置
 */
function getLimitConfig(channel: string): RateLimitConfig {
  return DEFAULT_LIMITS[channel] || DEFAULT_LIMITS['_default']
}

/**
 * 检查是否超过速率限制
 * @param channel IPC 通道名
 * @returns true 如果允许，false 如果被限制
 */
export function checkRateLimit(channel: string): boolean {
  const config = getLimitConfig(channel)
  const now = Date.now()
  const key = channel

  let record = requestRecords.get(key)

  if (!record || now - record.windowStart >= config.windowMs) {
    // 新窗口
    record = { count: 1, windowStart: now }
    requestRecords.set(key, record)
    return true
  }

  if (record.count >= config.maxRequests) {
    return false
  }

  record.count++
  return true
}

/**
 * 获取剩余等待时间
 */
export function getRemainingWaitTime(channel: string): number {
  const config = getLimitConfig(channel)
  const record = requestRecords.get(channel)

  if (!record) {
    return 0
  }

  const elapsed = Date.now() - record.windowStart
  if (elapsed >= config.windowMs) {
    return 0
  }

  return config.windowMs - elapsed
}

/**
 * 重置某个通道的限制
 */
export function resetRateLimit(channel: string): void {
  requestRecords.delete(channel)
}

/**
 * 清理过期的记录
 */
export function cleanupExpiredRecords(): void {
  const now = Date.now()

  for (const [channel, record] of requestRecords.entries()) {
    const config = getLimitConfig(channel)
    if (now - record.windowStart >= config.windowMs * 2) {
      requestRecords.delete(channel)
    }
  }
}

// 定期清理
setInterval(cleanupExpiredRecords, 60000)

/**
 * 创建速率限制中间件
 */
export function createRateLimiterMiddleware() {
  return async (
    channel: string,
    _args: unknown[],
    next: () => Promise<unknown>
  ): Promise<unknown> => {
    if (!checkRateLimit(channel)) {
      const waitTime = getRemainingWaitTime(channel)
      throw createError(
        ERROR_CODES.IPC_RATE_LIMITED,
        `Rate limit exceeded for channel: ${channel}`,
        { channel, retryAfterMs: waitTime }
      )
    }

    return next()
  }
}
