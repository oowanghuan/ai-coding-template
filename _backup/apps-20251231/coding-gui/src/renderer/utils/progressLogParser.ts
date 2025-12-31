/**
 * PROGRESS_LOG.yaml 解析器
 * 将 YAML 解析后的进度日志转换为 UI 可用的数据结构
 */

// ============ 类型定义 ============

export type PhaseId = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7
export type TaskStatus = 'pending' | 'wip' | 'done' | 'blocked'
export type TaskPriority = 'P0' | 'P1' | 'P2' | 'P3'
export type PhaseStatus = 'pending' | 'wip' | 'done' | 'blocked'

export interface Task {
  id: string
  task: string
  status: TaskStatus
  priority?: TaskPriority
  completedAt?: string
  verification?: string
  notes?: string
  dependsOn?: string[]
}

export interface PhaseData {
  status: PhaseStatus
  description?: string
  tasks: Task[]
  total: number
  done: number
  percentage: number
}

export interface FeatureMeta {
  feature: string
  featureName: string
  currentPhase: PhaseId
  status: PhaseStatus
  owner: string
  startedAt: string
  lastUpdated: string
}

export interface FeatureProgress {
  meta: FeatureMeta
  phases: Record<PhaseId, PhaseData>
  stats: {
    totalTasks: number
    done: number
    wip: number
    pending: number
    blocked: number
    completionRate: string
  }
}

// ============ 常量配置 ============

export const PHASE_NAMES: Record<PhaseId, string> = {
  0: 'Foundation',
  1: 'Kickoff',
  2: 'Spec',
  3: 'Demo',
  4: 'Design',
  5: 'Code',
  6: 'Test',
  7: 'Deploy'
}

export const PHASE_COLORS: Record<PhaseId, string> = {
  0: '#8b5cf6',
  1: '#6366f1',
  2: '#f43f5e',
  3: '#ec4899',
  4: '#3b82f6',
  5: '#10b981',
  6: '#f59e0b',
  7: '#06b6d4'
}

const PHASE_KEY_MAP: Record<string, PhaseId> = {
  'phase_0_foundation': 0,
  'phase_1_kickoff': 1,
  'phase_2_spec': 2,
  'phase_3_demo': 3,
  'phase_4_design': 4,
  'phase_5_code': 5,
  'phase_6_test': 6,
  'phase_7_deploy': 7
}

// Phase 目标配置
export const PHASE_OBJECTIVES: Record<PhaseId, string[]> = {
  0: ['建立系统级规范', '配置项目基础设施', '创建 UI 设计系统'],
  1: ['创建 {feature}/ 目录', '编写 00_CONTEXT.md', '明确功能边界，无歧义'],
  2: ['编写 UI Flow Spec', '定义 API 接口', '完成需求确认'],
  3: ['创建交互原型', '用户验收测试', '收集反馈意见'],
  4: ['完成设计定稿', '技术架构评审', '准备开发计划'],
  5: ['代码实现', '代码评审', '单元测试'],
  6: ['集成测试', '性能测试', '问题修复'],
  7: ['生产部署', '发布文档', '上线验证']
}

// Phase 上游输入配置
export const PHASE_INPUTS: Record<PhaseId, Array<{ name: string; description: string; path: string }>> = {
  0: [],
  1: [
    { name: '_system/* 规范', description: '系统级规范文档', path: '_system/README.md' },
    { name: '用户需求描述', description: '功能需求输入（外部输入）', path: 'docs/requirements.md' }
  ],
  2: [
    { name: '10_CONTEXT.md', description: '功能上下文', path: 'docs/{feature}/10_CONTEXT.md' }
  ],
  3: [
    { name: '21_UI_FLOW_SPEC.md', description: 'UI 流程规格', path: 'docs/{feature}/21_UI_FLOW_SPEC.md' }
  ],
  4: [
    { name: '30_DEMO_FEEDBACK.md', description: 'Demo 反馈', path: 'docs/{feature}/30_DEMO_FEEDBACK.md' }
  ],
  5: [
    { name: '40_DESIGN.md', description: '设计文档', path: 'docs/{feature}/40_DESIGN.md' }
  ],
  6: [
    { name: '源代码', description: '开发完成的代码', path: 'src/' }
  ],
  7: [
    { name: '测试报告', description: '测试通过报告', path: 'docs/{feature}/61_TEST_REPORT.md' }
  ]
}

// Phase 参考文档配置
export const PHASE_REFERENCES: Record<PhaseId, Array<{ name: string; description: string; path: string }>> = {
  0: [
    { name: 'PROJECT_PROFILE.yaml', description: '项目配置模板', path: '_templates/PROJECT_PROFILE.yaml' }
  ],
  1: [
    { name: 'CONTEXT_TEMPLATE.md', description: '功能上下文模板', path: '03_TEMPLATES/CONTEXT_TEMPLATE.md' },
    { name: 'CHANGELOG_TEMPLATE.md', description: '变更记录模板', path: '03_TEMPLATES/CHANGELOG_TEMPLATE.md' }
  ],
  2: [
    { name: 'UI_FLOW_SPEC_TEMPLATE.md', description: 'UI 流程规格模板', path: '03_TEMPLATES/UI_FLOW_SPEC_TEMPLATE.md' }
  ],
  3: [
    { name: 'DEMO_REVIEW_TEMPLATE.md', description: 'Demo 评审模板', path: '03_TEMPLATES/DEMO_REVIEW_TEMPLATE.md' }
  ],
  4: [
    { name: 'DESIGN_TEMPLATE.md', description: '设计文档模板', path: '03_TEMPLATES/DESIGN_TEMPLATE.md' }
  ],
  5: [
    { name: 'DEV_PLAN_TEMPLATE.md', description: '开发计划模板', path: '03_TEMPLATES/DEV_PLAN_TEMPLATE.md' }
  ],
  6: [
    { name: 'TEST_PLAN_TEMPLATE.md', description: '测试计划模板', path: '03_TEMPLATES/TEST_PLAN_TEMPLATE.md' }
  ],
  7: [
    { name: 'RELEASE_NOTE_TEMPLATE.md', description: '发布说明模板', path: '03_TEMPLATES/RELEASE_NOTE_TEMPLATE.md' }
  ]
}

// Phase 可用工具配置
export const PHASE_TOOLS: Record<PhaseId, Array<{
  command: string
  type: string
  priority: string
  status: 'implemented' | 'planned'
  description: string
  usagePath: string
  sourcePath: string
}>> = {
  0: [
    {
      command: '/init-project',
      type: 'Slash Command',
      priority: 'P0',
      status: 'implemented',
      description: '初始化项目结构',
      usagePath: 'CC_COLLABORATION/05_tools/slash-commands/init-project.md',
      sourcePath: '.claude/commands/init-project.md'
    }
  ],
  1: [
    {
      command: '/new-feature <name>',
      type: 'Slash Command',
      priority: 'P0',
      status: 'implemented',
      description: '创建功能模块目录和初始文档',
      usagePath: 'CC_COLLABORATION/05_tools/slash-commands/new-feature.md',
      sourcePath: '.claude/commands/new-feature.md'
    }
  ],
  2: [
    {
      command: '/write-spec',
      type: 'Slash Command',
      priority: 'P1',
      status: 'implemented',
      description: '编写需求规格文档',
      usagePath: 'CC_COLLABORATION/05_tools/slash-commands/write-spec.md',
      sourcePath: '.claude/commands/write-spec.md'
    }
  ],
  3: [
    {
      command: '/create-demo',
      type: 'Slash Command',
      priority: 'P1',
      status: 'planned',
      description: '创建交互原型',
      usagePath: '',
      sourcePath: ''
    }
  ],
  4: [
    {
      command: '/expert-review',
      type: 'Slash Command',
      priority: 'P0',
      status: 'implemented',
      description: '执行专家评审',
      usagePath: 'CC_COLLABORATION/05_tools/slash-commands/expert-review.md',
      sourcePath: '.claude/commands/expert-review.md'
    }
  ],
  5: [
    {
      command: '/resume',
      type: 'Slash Command',
      priority: 'P0',
      status: 'implemented',
      description: '从检查点恢复开发',
      usagePath: 'CC_COLLABORATION/05_tools/slash-commands/resume.md',
      sourcePath: '.claude/commands/resume.md'
    }
  ],
  6: [
    {
      command: '/run-tests',
      type: 'Slash Command',
      priority: 'P0',
      status: 'implemented',
      description: '运行测试套件',
      usagePath: 'CC_COLLABORATION/05_tools/slash-commands/run-tests.md',
      sourcePath: '.claude/commands/run-tests.md'
    }
  ],
  7: [
    {
      command: '/deploy',
      type: 'Slash Command',
      priority: 'P1',
      status: 'planned',
      description: '部署到生产环境',
      usagePath: '',
      sourcePath: ''
    }
  ]
}

// ============ 解析函数 ============

interface RawTask {
  id: string
  task: string
  status: string
  priority?: string
  completed_at?: string
  verification?: string
  notes?: string
  depends_on?: string[]
}

interface RawPhaseSection {
  status?: string
  description?: string
  tasks?: RawTask[]
  templates?: RawTask[]
  workflows?: RawTask[]
  tools?: RawTask[]
  completed?: RawTask[]
  system_docs?: RawTask[]
  ui_system_docs?: RawTask[]
  cc_docs?: RawTask[]
}

function parseTask(raw: RawTask): Task {
  return {
    id: raw.id,
    task: raw.task,
    status: (raw.status as TaskStatus) || 'pending',
    priority: raw.priority as TaskPriority | undefined,
    completedAt: raw.completed_at,
    verification: raw.verification,
    notes: raw.notes,
    dependsOn: raw.depends_on
  }
}

function extractTasks(section: RawPhaseSection): Task[] {
  const tasks: Task[] = []
  const taskArrays = [
    section.tasks,
    section.templates,
    section.workflows,
    section.tools,
    section.completed,
    section.system_docs,
    section.ui_system_docs,
    section.cc_docs
  ]

  taskArrays.forEach(arr => {
    if (Array.isArray(arr)) {
      arr.forEach(t => tasks.push(parseTask(t)))
    }
  })

  return tasks
}

function calculatePhasePercentage(tasks: Task[]): number {
  if (tasks.length === 0) return 0
  const done = tasks.filter(t => t.status === 'done').length
  return Math.round((done / tasks.length) * 100)
}

function determinePhaseStatus(tasks: Task[]): PhaseStatus {
  if (tasks.length === 0) return 'pending'
  const allDone = tasks.every(t => t.status === 'done')
  if (allDone) return 'done'
  const hasWip = tasks.some(t => t.status === 'wip')
  if (hasWip) return 'wip'
  const hasBlocked = tasks.some(t => t.status === 'blocked')
  if (hasBlocked) return 'blocked'
  return 'pending'
}

function parsePhase(section: RawPhaseSection): PhaseData {
  const tasks = extractTasks(section)
  const done = tasks.filter(t => t.status === 'done').length

  return {
    status: (section.status as PhaseStatus) || determinePhaseStatus(tasks),
    description: section.description,
    tasks,
    total: tasks.length,
    done,
    percentage: calculatePhasePercentage(tasks)
  }
}

/**
 * 从已解析的对象解析进度日志
 */
export function parseProgressLogFromObject(data: any): FeatureProgress {
  const meta: FeatureMeta = {
    feature: data.meta?.feature || '',
    featureName: data.meta?.feature_name || '',
    currentPhase: (data.meta?.current_phase || 1) as PhaseId,
    status: (data.meta?.status || 'pending') as PhaseStatus,
    owner: data.meta?.owner || '',
    startedAt: data.meta?.started_at || '',
    lastUpdated: data.meta?.last_updated || ''
  }

  const phases: Record<PhaseId, PhaseData> = {} as Record<PhaseId, PhaseData>

  Object.entries(PHASE_KEY_MAP).forEach(([key, phaseId]) => {
    const section = data[key] as RawPhaseSection | undefined
    if (section) {
      phases[phaseId] = parsePhase(section)
    } else {
      phases[phaseId] = {
        status: 'pending',
        tasks: [],
        total: 0,
        done: 0,
        percentage: 0
      }
    }
  })

  // 计算统计
  let totalTasks = 0
  let doneTasks = 0
  let wipTasks = 0
  let pendingTasks = 0
  let blockedTasks = 0

  Object.values(phases).forEach(phase => {
    totalTasks += phase.total
    phase.tasks.forEach(t => {
      if (t.status === 'done') doneTasks++
      else if (t.status === 'wip') wipTasks++
      else if (t.status === 'blocked') blockedTasks++
      else pendingTasks++
    })
  })

  return {
    meta,
    phases,
    stats: {
      totalTasks,
      done: doneTasks,
      wip: wipTasks,
      pending: pendingTasks,
      blocked: blockedTasks,
      completionRate: totalTasks > 0 ? `${Math.round((doneTasks / totalTasks) * 100)}%` : '0%'
    }
  }
}

/**
 * 获取指定 Phase 的配置信息
 */
export function getPhaseConfig(phaseId: PhaseId, featureId?: string) {
  const replacePath = (path: string) => featureId ? path.replace('{feature}', featureId) : path

  return {
    name: PHASE_NAMES[phaseId],
    color: PHASE_COLORS[phaseId],
    objectives: PHASE_OBJECTIVES[phaseId],
    inputs: PHASE_INPUTS[phaseId].map(input => ({
      ...input,
      path: replacePath(input.path)
    })),
    references: PHASE_REFERENCES[phaseId].map(ref => ({
      ...ref,
      path: replacePath(ref.path)
    })),
    tools: PHASE_TOOLS[phaseId]
  }
}
