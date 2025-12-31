/**
 * 项目状态缓存服务
 * CODE-011: ProjectStateCache + LRU 策略
 */

import { EventEmitter } from 'events'
import type { Project } from '../../shared/types/project.types'

/** 缓存条目 */
interface CacheEntry {
  project: Project
  cachedAt: Date
  accessedAt: Date
  accessCount: number
}

/** 缓存配置 */
interface CacheConfig {
  maxSize: number
  ttlMs: number
}

const DEFAULT_CONFIG: CacheConfig = {
  maxSize: 10,
  ttlMs: 5 * 60 * 1000 // 5 分钟
}

/**
 * 项目状态缓存服务（单例）
 * 实现 LRU 策略
 */
class ProjectStateCacheService extends EventEmitter {
  private static instance: ProjectStateCacheService | null = null

  /** 缓存存储 */
  private cache = new Map<string, CacheEntry>()

  /** 订阅者 */
  private subscribers = new Map<string, Set<(project: Project) => void>>()

  /** 配置 */
  private config: CacheConfig

  private constructor(config: CacheConfig = DEFAULT_CONFIG) {
    super()
    this.config = config

    // 定期清理过期条目
    setInterval(() => this.cleanupExpired(), 60000)
  }

  static getInstance(): ProjectStateCacheService {
    if (!ProjectStateCacheService.instance) {
      ProjectStateCacheService.instance = new ProjectStateCacheService()
    }
    return ProjectStateCacheService.instance
  }

  /**
   * 获取缓存的项目状态
   */
  get(projectPath: string): Project | null {
    const entry = this.cache.get(projectPath)

    if (!entry) {
      this.emit('cache-miss', { projectPath })
      return null
    }

    // 检查是否过期
    if (this.isExpired(entry)) {
      this.cache.delete(projectPath)
      this.emit('cache-expired', { projectPath })
      return null
    }

    // 更新访问信息（LRU）
    entry.accessedAt = new Date()
    entry.accessCount++

    this.emit('cache-hit', { projectPath })
    return entry.project
  }

  /**
   * 设置缓存
   */
  set(projectPath: string, project: Project): void {
    // 检查是否需要淘汰
    if (this.cache.size >= this.config.maxSize && !this.cache.has(projectPath)) {
      this.evictLRU()
    }

    const now = new Date()
    const entry: CacheEntry = {
      project,
      cachedAt: now,
      accessedAt: now,
      accessCount: 1
    }

    this.cache.set(projectPath, entry)
    this.emit('cache-set', { projectPath })

    // 通知订阅者
    this.notifySubscribers(projectPath, project)
  }

  /**
   * 使缓存失效
   */
  invalidate(projectPath: string): void {
    const existed = this.cache.delete(projectPath)
    if (existed) {
      this.emit('cache-invalidate', { projectPath })
    }
  }

  /**
   * 刷新缓存
   * 注意：需要外部提供项目加载逻辑
   */
  async refresh(projectPath: string, loader?: () => Promise<Project>): Promise<Project | null> {
    if (loader) {
      try {
        const project = await loader()
        this.set(projectPath, project)
        return project
      } catch (error) {
        this.emit('refresh-failed', { projectPath, error })
        return null
      }
    }

    // 无 loader 时返回现有缓存或 null
    return this.get(projectPath)
  }

  /**
   * 订阅项目状态变更
   */
  subscribe(projectPath: string, callback: (project: Project) => void): () => void {
    if (!this.subscribers.has(projectPath)) {
      this.subscribers.set(projectPath, new Set())
    }

    this.subscribers.get(projectPath)!.add(callback)

    // 返回取消订阅函数
    return () => {
      const subs = this.subscribers.get(projectPath)
      if (subs) {
        subs.delete(callback)
        if (subs.size === 0) {
          this.subscribers.delete(projectPath)
        }
      }
    }
  }

  /**
   * 获取缓存统计
   */
  getStats(): {
    size: number
    maxSize: number
    entries: Array<{ path: string; cachedAt: string; accessCount: number }>
  } {
    const entries = Array.from(this.cache.entries()).map(([path, entry]) => ({
      path,
      cachedAt: entry.cachedAt.toISOString(),
      accessCount: entry.accessCount
    }))

    return {
      size: this.cache.size,
      maxSize: this.config.maxSize,
      entries
    }
  }

  /**
   * 清空所有缓存
   */
  clear(): void {
    this.cache.clear()
    this.emit('cache-clear')
  }

  // ============================================================
  // 私有方法
  // ============================================================

  /**
   * 检查条目是否过期
   */
  private isExpired(entry: CacheEntry): boolean {
    const age = Date.now() - entry.cachedAt.getTime()
    return age > this.config.ttlMs
  }

  /**
   * LRU 淘汰
   */
  private evictLRU(): void {
    let oldestPath: string | null = null
    let oldestTime = Date.now()

    for (const [path, entry] of this.cache) {
      if (entry.accessedAt.getTime() < oldestTime) {
        oldestTime = entry.accessedAt.getTime()
        oldestPath = path
      }
    }

    if (oldestPath) {
      this.cache.delete(oldestPath)
      this.emit('cache-evict', { projectPath: oldestPath, reason: 'lru' })
    }
  }

  /**
   * 清理过期条目
   */
  private cleanupExpired(): void {
    const expired: string[] = []

    for (const [path, entry] of this.cache) {
      if (this.isExpired(entry)) {
        expired.push(path)
      }
    }

    for (const path of expired) {
      this.cache.delete(path)
      this.emit('cache-evict', { projectPath: path, reason: 'expired' })
    }
  }

  /**
   * 通知订阅者
   */
  private notifySubscribers(projectPath: string, project: Project): void {
    const subs = this.subscribers.get(projectPath)
    if (subs) {
      for (const callback of subs) {
        try {
          callback(project)
        } catch (error) {
          console.error('[ProjectStateCache] Subscriber error:', error)
        }
      }
    }
  }
}

export const projectStateCacheService = ProjectStateCacheService.getInstance()
export { ProjectStateCacheService, CacheEntry, CacheConfig }
