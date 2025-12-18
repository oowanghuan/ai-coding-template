/**
 * ConfigLoader 服务
 * 加载工作流配置（WORKFLOW_TEMPLATE.yaml, PHASE_GATE.yaml 等）
 * 支持缓存和降级到默认值
 */

import { githubDocService, DocError } from './githubDocService'
import type {
  WorkflowTemplate,
  FrameworkStep,
  PhaseMetadata,
  PhaseConfig,
  PhaseGateConfig,
  PhaseUIConfig,
  ToolConfig,
  FeatureTask,
  GateStatus,
  PhaseGateStatus,
  ProgressLog,
  PhaseInput,
  PhaseReference,
} from '../types/workflow.types'
import { CACHE_CONFIG } from '../config/github'

// ============================================================
// 配置路径
// ============================================================

const CONFIG_PATHS = {
  workflowTemplate: 'CC_COLLABORATION/00_system/WORKFLOW_TEMPLATE.yaml',
  phaseGate: 'CC_COLLABORATION/07_phase_gate/PHASE_GATE.yaml',
  toolsDir: 'CC_COLLABORATION/05_tools',
  progressLog: (featureId: string) => `docs/${featureId}/90_PROGRESS_LOG.yaml`,
  gateStatus: (featureId: string) => `docs/${featureId}/PHASE_GATE_STATUS.yaml`,
}

// ============================================================
// 缓存结构
// ============================================================

interface CacheEntry<T> {
  data: T
  timestamp: number
}

class ConfigCache {
  private cache: Map<string, CacheEntry<any>> = new Map()
  private ttlMs: number

  constructor(ttlMs: number = CACHE_CONFIG.ttlMs) {
    this.ttlMs = ttlMs
  }

  get<T>(key: string): T | null {
    const entry = this.cache.get(key)
    if (!entry) return null

    if (Date.now() - entry.timestamp > this.ttlMs) {
      this.cache.delete(key)
      return null
    }

    return entry.data as T
  }

  set<T>(key: string, data: T): void {
    this.cache.set(key, { data, timestamp: Date.now() })
  }

  clear(): void {
    this.cache.clear()
  }
}

// ============================================================
// 默认配置（降级用）
// ============================================================

const DEFAULT_FRAMEWORK_STEPS: FrameworkStep[] = [
  {
    id: 'start-day',
    name: '每日开始',
    icon: 'calendar-check',
    command: '/start-day',
    position: 'before_tasks',
    applicable_phases: [0, 1, 2, 3, 4, 5, 6, 7],
    description: '同步最新代码和状态',
    execution_mode: 'non_interactive',
    owner: 'cc',
    rerun_policy: { strategy: 'allow' },
    expected_artifacts: [],
    verify: { type: 'command_exit_code' },
  },
  {
    id: 'expert-review',
    name: '专家评审',
    icon: 'search',
    command: '/expert-review',
    position: 'after_tasks',
    applicable_phases: [4, 5, 6],
    description: '发起技术方案评审',
    prerequisite: 'all_tasks_completed',
    execution_mode: 'interactive',
    owner: 'cc',
    rerun_policy: { strategy: 'confirm', confirm_message: '是否重新评审？' },
    expected_artifacts: [
      { path: 'docs/{feature}/REVIEW_REPORT.md', required: true },
    ],
    verify: { type: 'file_exists' },
  },
  {
    id: 'check-gate',
    name: 'Gate 检查',
    icon: 'clipboard-check',
    command: '/check-gate',
    position: 'after_tasks',
    applicable_phases: [0, 1, 2, 3, 4, 5, 6, 7],
    description: '检查阶段通过条件',
    prerequisite: 'expert_review_passed_if_required',
    execution_mode: 'non_interactive',
    owner: 'cc',
    rerun_policy: { strategy: 'allow' },
    expected_artifacts: [],
    verify: { type: 'command_exit_code' },
  },
  {
    id: 'approve-gate',
    name: 'Gate 审批',
    icon: 'check-circle',
    command: '/approve-gate',
    position: 'after_tasks',
    applicable_phases: [0, 1, 2, 3, 4, 5, 6, 7],
    description: '人工审批阶段通过',
    prerequisite: 'check_gate_passed',
    execution_mode: 'hybrid',
    owner: 'human',
    rerun_policy: { strategy: 'block', block_message: '已审批通过' },
    expected_artifacts: [],
    verify: { type: 'command_exit_code' },
  },
  {
    id: 'next-phase',
    name: '进入下一阶段',
    icon: 'arrow-right',
    command: '/next-phase',
    position: 'after_tasks',
    applicable_phases: [0, 1, 2, 3, 4, 5, 6],
    description: '迁移到下一个阶段',
    prerequisite: 'gate_approved',
    execution_mode: 'non_interactive',
    owner: 'cc',
    rerun_policy: { strategy: 'block', block_message: '已进入下一阶段' },
    expected_artifacts: [],
    verify: { type: 'command_exit_code' },
  },
  {
    id: 'end-day',
    name: '每日结束',
    icon: 'calendar-x',
    command: '/end-day',
    position: 'end',
    applicable_phases: [0, 1, 2, 3, 4, 5, 6, 7],
    description: '保存工作进度',
    execution_mode: 'non_interactive',
    owner: 'cc',
    rerun_policy: { strategy: 'allow' },
    expected_artifacts: [],
    verify: { type: 'command_exit_code' },
  },
]

const DEFAULT_PHASES: PhaseMetadata[] = [
  { id: 0, name: 'Foundation', display_name: '基础设施', description: '建立系统级规范', has_expert_review: false, color: '#6b7280' },
  { id: 1, name: 'Kickoff', display_name: '需求启动', description: '明确需求边界', has_expert_review: false, color: '#8b5cf6' },
  { id: 2, name: 'Spec', display_name: '需求规格', description: '定义验收标准', has_expert_review: false, color: '#3b82f6' },
  { id: 3, name: 'Demo', display_name: '原型演示', description: '验证用户体验', has_expert_review: false, color: '#06b6d4' },
  { id: 4, name: 'Design', display_name: '技术设计', description: '定义接口契约', has_expert_review: true, color: '#10b981' },
  { id: 5, name: 'Code', display_name: '编码实现', description: '实现功能代码', has_expert_review: true, color: '#f59e0b' },
  { id: 6, name: 'Test', display_name: '测试验证', description: '验证功能正确性', has_expert_review: true, color: '#ef4444' },
  { id: 7, name: 'Deploy', display_name: '部署发布', description: '发布到生产环境', has_expert_review: false, color: '#ec4899' },
]

const DEFAULT_OBJECTIVES: Record<number, string[]> = {
  0: ['建立系统级规范', '配置项目基础设施', '创建 UI 设计系统'],
  1: ['创建功能目录', '编写 10_CONTEXT.md', '明确功能边界'],
  2: ['编写 21_UI_FLOW_SPEC.md', '定义验收标准', '进行专家评审'],
  3: ['创建可交互原型', '验证用户体验', '收集用户反馈'],
  4: ['编写 40_DESIGN_FINAL.md', '定义 API 契约', '进行设计评审'],
  5: ['按设计文档实现代码', '编写单元测试', '进行代码评审'],
  6: ['编写测试计划', '执行测试用例', '生成测试报告'],
  7: ['部署到生产环境', '发布版本', '编写发布说明'],
}

// ============================================================
// ConfigLoader 类
// ============================================================

class ConfigLoader {
  private cache: ConfigCache

  constructor() {
    this.cache = new ConfigCache()
  }

  // ========== 公共方法 ==========

  /**
   * 加载工作流模板
   */
  async loadWorkflowTemplate(): Promise<WorkflowTemplate> {
    const cacheKey = 'workflow-template'
    const cached = this.cache.get<WorkflowTemplate>(cacheKey)
    if (cached) return cached

    try {
      const doc = await githubDocService.fetchDocument(CONFIG_PATHS.workflowTemplate)
      if (doc.parsedContent) {
        const template: WorkflowTemplate = {
          version: doc.parsedContent.version || '1.0',
          framework_steps: doc.parsedContent.framework_steps || DEFAULT_FRAMEWORK_STEPS,
          phases: doc.parsedContent.phases || DEFAULT_PHASES,
        }
        this.cache.set(cacheKey, template)
        return template
      }
    } catch (error) {
      console.warn('Failed to load WORKFLOW_TEMPLATE.yaml, using defaults:', error)
    }

    const defaultTemplate: WorkflowTemplate = {
      version: '1.0',
      framework_steps: DEFAULT_FRAMEWORK_STEPS,
      phases: DEFAULT_PHASES,
    }
    this.cache.set(cacheKey, defaultTemplate)
    return defaultTemplate
  }

  /**
   * 加载阶段配置（含 ui_config）
   */
  async loadPhaseConfig(phaseId: number, featureId?: string): Promise<PhaseConfig> {
    const cacheKey = `phase-config-${phaseId}-${featureId || 'default'}`
    const cached = this.cache.get<PhaseConfig>(cacheKey)
    if (cached) return cached

    // 加载基础模板
    const template = await this.loadWorkflowTemplate()
    const phaseMeta = template.phases.find(p => p.id === phaseId) || DEFAULT_PHASES[phaseId]

    // 尝试加载 PHASE_GATE.yaml 获取 ui_config
    let uiConfig: PhaseUIConfig | undefined
    try {
      const doc = await githubDocService.fetchDocument(CONFIG_PATHS.phaseGate)
      if (doc.parsedContent?.phases) {
        const phaseGate = doc.parsedContent.phases.find((p: any) => p.id === phaseId)
        uiConfig = phaseGate?.ui_config
      }
    } catch (error) {
      console.warn('Failed to load PHASE_GATE.yaml ui_config:', error)
    }

    // 加载工具
    const tools = await this.loadTools(phaseId)

    // 替换路径变量
    const replaceFeature = (str: string) =>
      featureId ? str.replace(/{feature}/g, featureId) : str

    const config: PhaseConfig = {
      id: phaseId,
      name: phaseMeta?.name || `Phase ${phaseId}`,
      displayName: phaseMeta?.display_name || `阶段 ${phaseId}`,
      description: phaseMeta?.description || '',
      color: phaseMeta?.color || '#6b7280',
      hasExpertReview: phaseMeta?.has_expert_review || false,
      objectives: uiConfig?.objectives || DEFAULT_OBJECTIVES[phaseId] || [],
      inputs: (uiConfig?.inputs || []).map(input => ({
        ...input,
        paths: input.paths.map(replaceFeature),
      })),
      references: (uiConfig?.references || []).map(ref => ({
        ...ref,
        path: replaceFeature(ref.path),
      })),
      tools,
    }

    this.cache.set(cacheKey, config)
    return config
  }

  /**
   * 加载工具列表（按阶段过滤）
   */
  async loadTools(phaseId: number): Promise<ToolConfig[]> {
    const cacheKey = `tools-${phaseId}`
    const cached = this.cache.get<ToolConfig[]>(cacheKey)
    if (cached) return cached

    // 目前使用默认工具配置
    // TODO: 从 05_tools/ 目录扫描工具定义
    const defaultTools: ToolConfig[] = [
      {
        name: 'expert-review',
        type: 'slash-command',
        command: '/expert-review',
        description: '发起专家评审',
        phases: [4, 5, 6],
        priority: 'required',
        status: 'implemented',
        owner: 'cc',
        execution_mode: 'interactive',
        usage_doc: 'CC_COLLABORATION/05_tools/slash-commands/expert-review.md',
        source_path: '.claude/commands/expert-review.md',
      },
      {
        name: 'check-gate',
        type: 'slash-command',
        command: '/check-gate',
        description: '检查阶段通过条件',
        phases: [0, 1, 2, 3, 4, 5, 6, 7],
        priority: 'required',
        status: 'implemented',
        owner: 'cc',
        execution_mode: 'non_interactive',
        usage_doc: 'CC_COLLABORATION/05_tools/slash-commands/check-gate.md',
        source_path: '.claude/commands/check-gate.md',
      },
      {
        name: 'next-phase',
        type: 'slash-command',
        command: '/next-phase',
        description: '进入下一阶段',
        phases: [0, 1, 2, 3, 4, 5, 6],
        priority: 'required',
        status: 'implemented',
        owner: 'cc',
        execution_mode: 'non_interactive',
        usage_doc: 'CC_COLLABORATION/05_tools/slash-commands/next-phase.md',
        source_path: '.claude/commands/next-phase.md',
      },
    ]

    const filtered = defaultTools.filter(tool => tool.phases.includes(phaseId))
    this.cache.set(cacheKey, filtered)
    return filtered
  }

  /**
   * 加载 Feature 任务
   */
  async loadFeatureTasks(featureId: string, phaseId: number): Promise<FeatureTask[]> {
    const cacheKey = `feature-tasks-${featureId}-${phaseId}`
    const cached = this.cache.get<FeatureTask[]>(cacheKey)
    if (cached) return cached

    try {
      const doc = await githubDocService.fetchDocument(CONFIG_PATHS.progressLog(featureId))
      if (doc.parsedContent) {
        const progressLog = doc.parsedContent as ProgressLog

        // 查找对应阶段的任务
        const phaseKey = this.findPhaseKey(progressLog, phaseId)
        if (phaseKey && progressLog[phaseKey]?.tasks) {
          const tasks = progressLog[phaseKey].tasks as FeatureTask[]
          this.cache.set(cacheKey, tasks)
          return tasks
        }
      }
    } catch (error) {
      console.warn('Failed to load feature tasks:', error)
    }

    return []
  }

  /**
   * 加载 Gate 状态
   */
  async loadGateStatus(featureId: string): Promise<GateStatus> {
    const cacheKey = `gate-status-${featureId}`
    const cached = this.cache.get<GateStatus>(cacheKey)
    if (cached) return cached

    const defaultStatus: GateStatus = {
      feature: featureId,
      phases: {},
    }

    try {
      const doc = await githubDocService.fetchDocument(CONFIG_PATHS.gateStatus(featureId))
      if (doc.parsedContent) {
        const gateStatus: GateStatus = {
          feature: featureId,
          phases: doc.parsedContent.phases || {},
        }
        this.cache.set(cacheKey, gateStatus)
        return gateStatus
      }
    } catch (error) {
      // Gate status 文件可能不存在，这是正常的
      const docError = error as DocError
      if (!docError.isNotFound) {
        console.warn('Failed to load gate status:', error)
      }
    }

    this.cache.set(cacheKey, defaultStatus)
    return defaultStatus
  }

  /**
   * 获取当前阶段 ID
   */
  async getCurrentPhase(featureId: string): Promise<number> {
    try {
      const doc = await githubDocService.fetchDocument(CONFIG_PATHS.progressLog(featureId))
      if (doc.parsedContent?.meta?.current_phase !== undefined) {
        return doc.parsedContent.meta.current_phase
      }
    } catch (error) {
      console.warn('Failed to get current phase:', error)
    }
    return 1 // 默认 Kickoff 阶段
  }

  /**
   * 获取适用于指定阶段的框架步骤
   */
  async getFrameworkSteps(phaseId: number): Promise<FrameworkStep[]> {
    const template = await this.loadWorkflowTemplate()
    return template.framework_steps.filter(step =>
      step.applicable_phases.includes(phaseId)
    )
  }

  /**
   * 清除缓存
   */
  clearCache(): void {
    this.cache.clear()
    githubDocService.clearCache()
  }

  // ========== 私有方法 ==========

  /**
   * 在 ProgressLog 中查找阶段 key
   * ProgressLog 使用 phase_X_name 格式的 key
   */
  private findPhaseKey(progressLog: ProgressLog, phaseId: number): string | null {
    const phaseNames = ['foundation', 'kickoff', 'spec', 'demo', 'design', 'code', 'test', 'deploy']
    const possibleKeys = [
      `phase_${phaseId}_${phaseNames[phaseId]}`,
      `phase${phaseId}`,
      phaseNames[phaseId],
    ]

    for (const key of possibleKeys) {
      if (progressLog[key]) {
        return key
      }
    }

    // 尝试模糊匹配
    const phaseName = phaseNames[phaseId]
    for (const key of Object.keys(progressLog)) {
      if (key.includes(phaseName) || key.includes(`phase_${phaseId}`)) {
        return key
      }
    }

    return null
  }
}

// 导出单例
export const configLoader = new ConfigLoader()
