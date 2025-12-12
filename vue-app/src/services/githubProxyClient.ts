import { GITHUB_DOC_CONFIG, CACHE_CONFIG } from '@/config/github'

export interface GitHubFileResponse {
  name: string
  path: string
  sha: string
  size: number
  html_url: string
  content?: string
  encoding?: 'base64'
  type?: 'file' | 'dir'
}

export interface ProxyError {
  error: string
  message: string
  status?: number
  path?: string
  resetTime?: string
}

export interface FetchError {
  isNotFound: boolean
  isRateLimit: boolean
  isConfigError: boolean
  message: string
  status: number
  resetTime?: string
}

class GitHubProxyClient {
  private proxyUrl: string
  private anonKey: string
  private cache: Map<string, { data: any; timestamp: number }> = new Map()

  constructor() {
    this.proxyUrl = GITHUB_DOC_CONFIG.proxyBaseUrl
    this.anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || ''
    this.loadCacheFromStorage()
  }

  /**
   * 获取文件内容
   */
  async getFileContent(path: string): Promise<GitHubFileResponse> {
    // 检查缓存
    const cached = this.getFromCache(path)
    if (cached) return cached

    const url = `${this.proxyUrl}?path=${encodeURIComponent(path)}&action=file`

    let response: Response
    try {
      response = await fetch(url, {
        headers: this.getHeaders()
      })
    } catch (e) {
      throw this.createError('network_error', '网络错误，请检查连接', 0)
    }

    if (!response.ok) {
      const errorData: ProxyError = await response.json().catch(() => ({
        error: 'unknown',
        message: '未知错误'
      }))

      throw this.createError(
        errorData.error,
        errorData.message,
        response.status,
        errorData.resetTime
      )
    }

    const data = await response.json()

    // 缓存结果
    this.setToCache(path, data)

    return data
  }

  /**
   * 获取目录内容
   */
  async getDirectoryContent(path: string): Promise<GitHubFileResponse[]> {
    const cached = this.getFromCache(path)
    if (cached) return cached

    const url = `${this.proxyUrl}?path=${encodeURIComponent(path)}&action=dir`

    let response: Response
    try {
      response = await fetch(url, {
        headers: this.getHeaders()
      })
    } catch (e) {
      throw this.createError('network_error', '网络错误，请检查连接', 0)
    }

    if (!response.ok) {
      const errorData: ProxyError = await response.json().catch(() => ({
        error: 'unknown',
        message: '未知错误'
      }))

      throw this.createError(
        errorData.error,
        errorData.message,
        response.status,
        errorData.resetTime
      )
    }

    const data = await response.json()
    this.setToCache(path, data)
    return data
  }

  /**
   * 获取 GitHub 网页 URL
   */
  getHtmlUrl(path: string): string {
    const { owner, repo, branch } = GITHUB_DOC_CONFIG
    return `https://github.com/${owner}/${repo}/blob/${branch}/${path}`
  }

  /**
   * 清除缓存
   */
  clearCache(): void {
    this.cache.clear()
    try {
      sessionStorage.removeItem(CACHE_CONFIG.storageKey)
    } catch {
      // Ignore storage errors
    }
  }

  // ======== 私有方法 ========

  private getHeaders(): HeadersInit {
    return {
      'Content-Type': 'application/json',
      'apikey': this.anonKey,
      'Authorization': `Bearer ${this.anonKey}`
    }
  }

  private createError(
    errorType: string,
    message: string,
    status: number,
    resetTime?: string
  ): FetchError {
    return {
      isNotFound: errorType === 'not_found',
      isRateLimit: errorType === 'rate_limit',
      isConfigError: errorType === 'config_error',
      message,
      status,
      resetTime,
    }
  }

  private getFromCache(key: string): any | null {
    if (!CACHE_CONFIG.enabled) return null

    const entry = this.cache.get(key)
    if (!entry) return null

    // 检查是否过期
    if (Date.now() - entry.timestamp > CACHE_CONFIG.ttlMs) {
      this.cache.delete(key)
      return null
    }

    return entry.data
  }

  private setToCache(key: string, data: any): void {
    if (!CACHE_CONFIG.enabled) return

    this.cache.set(key, { data, timestamp: Date.now() })
    this.saveCacheToStorage()
  }

  private loadCacheFromStorage(): void {
    try {
      const stored = sessionStorage.getItem(CACHE_CONFIG.storageKey)
      if (stored) {
        const parsed = JSON.parse(stored)
        this.cache = new Map(Object.entries(parsed))
      }
    } catch {
      // Ignore storage errors
    }
  }

  private saveCacheToStorage(): void {
    try {
      const obj = Object.fromEntries(this.cache)
      sessionStorage.setItem(CACHE_CONFIG.storageKey, JSON.stringify(obj))
    } catch {
      // Ignore storage errors
    }
  }
}

export const githubProxyClient = new GitHubProxyClient()
