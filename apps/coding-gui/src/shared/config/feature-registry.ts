/**
 * Feature Registry 配置
 * 注册所有 features，支持 archived 标记
 *
 * 设计原则：
 * - 使用注册表方式而非目录扫描，避免文件误删/重命名导致 feature 丢失
 * - archived: true 的 feature 默认不显示，可通过设置切换显示
 * - progressLogPath 指向实际的 90_PROGRESS_LOG.yaml 文件
 */

export interface FeatureRegistryEntry {
  /** Feature ID，唯一标识 */
  id: string
  /** Feature 显示名称 */
  name: string
  /** 负责人 */
  owner: string
  /** 相对于项目根目录的路径 */
  docsPath: string
  /** Progress Log 文件路径（相对于 docsPath） */
  progressLogFile: string
  /** 是否已归档（已完成交付的 feature） */
  archived: boolean
  /** 描述 */
  description?: string
}

/**
 * Feature Registry
 * 同步自 vue-app/src/data/projectRegistry.ts
 * 最后更新：2025-12-17
 */
export const featureRegistry: FeatureRegistryEntry[] = [
  {
    id: 'coding-GUI',
    name: 'Coding GUI',
    owner: '@Huan',
    docsPath: 'docs/coding-GUI',
    progressLogFile: '90_PROGRESS_LOG.yaml',
    archived: false,
    description: 'Electron 执行工作台应用'
  },
  {
    id: 'expert-reviewer',
    name: 'Expert Reviewer',
    owner: '@Huan',
    docsPath: 'docs/expert-reviewer',
    progressLogFile: '90_PROGRESS_LOG.yaml',
    archived: false,
    description: '专家评审系统'
  },
  {
    id: 'cc-tools-library',
    name: 'Claude Code 工具库',
    owner: '@Huan',
    docsPath: 'docs/cc-tools-library',
    progressLogFile: '90_PROGRESS_LOG.yaml',
    archived: true,
    description: '10 个 Slash Commands + 13 个 Skills + 4 个 Subagents'
  },
  {
    id: 'gantt-dashboard',
    name: '甘特图看板系统',
    owner: '@Huan',
    docsPath: 'docs/gantt-dashboard',
    progressLogFile: '90_PROGRESS_LOG.yaml',
    archived: true,
    description: '项目甘特图看板'
  },
  {
    id: 'github-doc-viewer',
    name: 'GitHub 文档查看器',
    owner: '@Huan',
    docsPath: 'docs/github-doc-viewer',
    progressLogFile: '90_PROGRESS_LOG.yaml',
    archived: true,
    description: 'GitHub 文档在线查看'
  },
  {
    id: 'panorama-guide',
    name: '全景指南页面',
    owner: '@Huan',
    docsPath: 'docs/panorama-guide',
    progressLogFile: '90_PROGRESS_LOG.yaml',
    archived: true,
    description: '5 屏渐进式引导页面'
  },
  {
    id: 'project-dashboard-system',
    name: 'AI 协作开发框架',
    owner: '@Huan',
    docsPath: 'docs/project-dashboard-system',
    progressLogFile: '90_PROGRESS_LOG.yaml',
    archived: true,
    description: '8 阶段工作流框架样例'
  }
]

/**
 * 获取可见的 features（排除 archived）
 */
export function getVisibleFeatures(): FeatureRegistryEntry[] {
  return featureRegistry.filter(f => !f.archived)
}

/**
 * 获取所有 features（包含 archived）
 */
export function getAllFeatures(): FeatureRegistryEntry[] {
  return featureRegistry
}

/**
 * 根据 ID 获取 feature
 */
export function getFeatureById(id: string): FeatureRegistryEntry | undefined {
  return featureRegistry.find(f => f.id === id)
}

/**
 * 检查 feature 是否存在
 */
export function hasFeature(id: string): boolean {
  return featureRegistry.some(f => f.id === id)
}
