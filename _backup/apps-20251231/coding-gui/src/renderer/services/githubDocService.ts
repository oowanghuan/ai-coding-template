import { githubProxyClient, FetchError } from './githubProxyClient'
import { DOC_TYPE_MAP, DOC_PATHS } from '../config/github'
import YAML from 'yaml'

export interface DocContent {
  type: 'markdown' | 'yaml'
  rawContent: string
  parsedContent?: any
  htmlUrl: string
  sha: string
  size: number
}

export interface DocMeta {
  sha: string
  size: number
  htmlUrl: string
}

export type DocState = 'idle' | 'loading' | 'success' | 'error' | 'not_found' | 'empty'

export interface DocError {
  isEmpty?: boolean
  isNotFound?: boolean
  isRateLimit?: boolean
  isConfigError?: boolean
  message: string
  resetTime?: string
}

class GitHubDocService {
  /**
   * 获取文档内容
   */
  async fetchDocument(path: string): Promise<DocContent> {
    const response = await githubProxyClient.getFileContent(path)

    // 解码 base64 内容（处理 UTF-8）
    const rawContent = response.content
      ? this.decodeBase64(response.content)
      : ''

    // 检查空内容
    if (!rawContent.trim()) {
      const error: DocError = { isEmpty: true, message: '文档内容为空' }
      throw error
    }

    // 确定文档类型
    const ext = path.substring(path.lastIndexOf('.'))
    const type = DOC_TYPE_MAP[ext] || 'markdown'

    // 如果是 YAML，尝试解析
    let parsedContent
    if (type === 'yaml') {
      try {
        parsedContent = YAML.parse(rawContent)
      } catch (e) {
        console.warn('YAML parse error, falling back to raw content:', e)
      }
    }

    return {
      type,
      rawContent,
      parsedContent,
      htmlUrl: response.html_url,
      sha: response.sha,
      size: response.size,
    }
  }

  /**
   * 获取文档元信息（用于检测更新）
   */
  async fetchDocumentMeta(path: string): Promise<DocMeta> {
    const response = await githubProxyClient.getFileContent(path)
    return {
      sha: response.sha,
      size: response.size,
      htmlUrl: response.html_url,
    }
  }

  /**
   * 获取功能的 PROGRESS_LOG
   */
  async fetchProgressLog(featureId: string): Promise<DocContent> {
    const path = DOC_PATHS.progressLog(featureId)
    return this.fetchDocument(path)
  }

  /**
   * 获取功能的 CONTEXT
   */
  async fetchContext(featureId: string): Promise<DocContent> {
    const path = DOC_PATHS.context(featureId)
    return this.fetchDocument(path)
  }

  /**
   * 获取功能的 DESIGN
   */
  async fetchDesign(featureId: string): Promise<DocContent> {
    const path = DOC_PATHS.design(featureId)
    return this.fetchDocument(path)
  }

  /**
   * 获取功能的 UI SPEC
   */
  async fetchUiSpec(featureId: string): Promise<DocContent> {
    const path = DOC_PATHS.uiSpec(featureId)
    return this.fetchDocument(path)
  }

  /**
   * 获取每日总结列表
   */
  async fetchDailySummaryList(featureId: string): Promise<string[]> {
    const path = DOC_PATHS.dailySummaryDir(featureId)
    try {
      const files = await githubProxyClient.getDirectoryContent(path)
      return files
        .filter(f => f.type === 'file' && f.name.endsWith('.md'))
        .map(f => f.name.replace('.md', ''))
        .sort()
        .reverse() // 最新的在前
    } catch {
      return []
    }
  }

  /**
   * 获取特定日期的每日总结
   */
  async fetchDailySummary(featureId: string, date: string): Promise<DocContent> {
    const path = DOC_PATHS.dailySummary(featureId, date)
    return this.fetchDocument(path)
  }

  /**
   * 获取 GitHub 网页 URL
   */
  getGitHubUrl(path: string): string {
    return githubProxyClient.getHtmlUrl(path)
  }

  /**
   * 清除缓存
   */
  clearCache(): void {
    githubProxyClient.clearCache()
  }

  // ======== 私有方法 ========

  /**
   * 解码 base64 内容（处理 UTF-8 字符）
   */
  private decodeBase64(base64: string): string {
    try {
      // 移除可能的换行符
      const cleaned = base64.replace(/\n/g, '')
      // 解码 base64 并处理 UTF-8
      return decodeURIComponent(escape(atob(cleaned)))
    } catch (e) {
      console.error('Base64 decode error:', e)
      return ''
    }
  }
}

export const githubDocService = new GitHubDocService()
