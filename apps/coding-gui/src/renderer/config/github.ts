// GitHub 文档服务配置（前端）
export const GITHUB_DOC_CONFIG = {
  // 仓库信息（用于显示 GitHub 链接）
  owner: 'oowanghuan',
  repo: 'ai-coding-org',
  branch: 'main',
  docsBasePath: 'docs',

  // Supabase Edge Function URL
  proxyBaseUrl: import.meta.env.VITE_SUPABASE_URL
    ? `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/github-docs-proxy`
    : 'https://mvabqxkfekbrzgmjkvih.supabase.co/functions/v1/github-docs-proxy',
}

// Supabase 配置
export const SUPABASE_CONFIG = {
  url: import.meta.env.VITE_SUPABASE_URL || 'https://mvabqxkfekbrzgmjkvih.supabase.co',
  anonKey: import.meta.env.VITE_SUPABASE_ANON_KEY || '',
}

// 文档类型映射
export const DOC_TYPE_MAP: Record<string, 'markdown' | 'yaml'> = {
  '.md': 'markdown',
  '.yaml': 'yaml',
  '.yml': 'yaml',
}

// 文档路径模板
export const DOC_PATHS = {
  // 功能级文档
  context: (featureId: string) => `docs/${featureId}/10_CONTEXT.md`,
  design: (featureId: string) => `docs/${featureId}/40_DESIGN.md`,
  uiSpec: (featureId: string) => `docs/${featureId}/21_UI_FLOW_SPEC.md`,
  progressLog: (featureId: string) => `docs/${featureId}/90_PROGRESS_LOG.yaml`,
  dailySummaryDir: (featureId: string) => `docs/${featureId}/91_DAILY_SUMMARY`,
  dailySummary: (featureId: string, date: string) =>
    `docs/${featureId}/91_DAILY_SUMMARY/${date}.md`,

  // 系统级文档
  projectStandup: () => `docs/_foundation/PROJECT_DAILY_STANDUP.yaml`,
  projectProfile: () => `docs/_foundation/01_PROJECT_PROFILE.yaml`,

  // 模板文件
  template: (templateName: string) => `_templates/${templateName}`,
}

// 缓存配置
export const CACHE_CONFIG = {
  enabled: true,
  ttlMs: 5 * 60 * 1000, // 5 分钟缓存
  storageKey: 'github-doc-cache',
}
