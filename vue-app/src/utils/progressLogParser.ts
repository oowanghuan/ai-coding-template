// PROGRESS_LOG.yaml Parser
// Parses YAML progress logs into typed FeatureProgress objects

import type {
  FeatureProgress,
  FeatureMeta,
  PhaseData,
  Task,
  CCCheckpoint,
  PhaseId,
  TaskStatus,
  TaskPriority,
  PhaseStatus
} from '@/data/projectRegistry'

import {
  calculatePhasePercentage,
  determinePhaseStatus,
  findCurrentPhase,
  PHASE_NAMES,
  PHASE_COLORS
} from '@/data/projectRegistry'

import type {
  FeatureData,
  PhaseDetail,
  Role,
  FileRef,
  Processor,
  Artifact
} from '@/data/projectDashboard'

// ============ YAML Parsing (using js-yaml) ============

// Note: In production, use a proper YAML parser like js-yaml
// For now, we'll create a simplified parser that works with our structure

interface RawProgressLog {
  meta: {
    feature: string
    feature_name: string
    current_phase: number
    status: string
    owner: string
    started_at: string
    last_updated: string
  }
  [key: string]: unknown
  cc_checkpoint?: {
    session_id: string
    last_file_edited: string
    last_action: string
    next_step: string
    context_files: string[]
    temp_state?: Record<string, unknown>
  }
  stats?: {
    summary: {
      total_tasks: number
      done: number
      wip: number
      pending: number
      blocked?: number
      completion_rate: string
    }
    next_milestone?: string
  }
}

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

// Phase key mapping
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

/**
 * Parse a raw task object into Task type
 */
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

/**
 * Extract all tasks from a phase section
 */
function extractTasks(section: RawPhaseSection): Task[] {
  const tasks: Task[] = []

  // Collect tasks from all possible arrays
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

/**
 * Parse a phase section into PhaseData
 */
function parsePhase(section: RawPhaseSection): PhaseData {
  const tasks = extractTasks(section)
  const done = tasks.filter(t => t.status === 'done').length

  return {
    status: section.status as PhaseStatus || determinePhaseStatus(tasks),
    description: section.description,
    tasks,
    total: tasks.length,
    done,
    percentage: calculatePhasePercentage(tasks)
  }
}

/**
 * Parse CC Checkpoint
 */
function parseCheckpoint(raw?: RawProgressLog['cc_checkpoint']): CCCheckpoint {
  if (!raw) {
    return {
      sessionId: '',
      lastFileEdited: '',
      lastAction: '',
      nextStep: '',
      contextFiles: []
    }
  }

  return {
    sessionId: raw.session_id,
    lastFileEdited: raw.last_file_edited,
    lastAction: raw.last_action,
    nextStep: raw.next_step,
    contextFiles: raw.context_files || [],
    tempState: raw.temp_state
  }
}

/**
 * Parse the complete PROGRESS_LOG.yaml content
 */
export function parseProgressLog(yamlContent: string): FeatureProgress {
  // In production, use js-yaml: import YAML from 'js-yaml'
  // const data = YAML.load(yamlContent) as RawProgressLog

  // For now, we'll assume the content is passed as a parsed object
  // This function signature accepts string for future YAML parsing
  throw new Error('YAML parsing requires js-yaml library. Use parseProgressLogFromObject instead.')
}

/**
 * Parse from a pre-parsed JavaScript object
 * (Use this when YAML is already parsed, e.g., from an API)
 */
export function parseProgressLogFromObject(data: RawProgressLog): FeatureProgress {
  // Parse metadata
  const meta: FeatureMeta = {
    feature: data.meta.feature,
    featureName: data.meta.feature_name,
    currentPhase: data.meta.current_phase as PhaseId,
    status: data.meta.status as PhaseStatus,
    owner: data.meta.owner,
    startedAt: data.meta.started_at,
    lastUpdated: data.meta.last_updated
  }

  // Parse all phases
  const phases: Record<PhaseId, PhaseData> = {} as Record<PhaseId, PhaseData>

  Object.entries(PHASE_KEY_MAP).forEach(([key, phaseId]) => {
    const section = data[key] as RawPhaseSection | undefined
    if (section) {
      phases[phaseId] = parsePhase(section)
    } else {
      // Default empty phase
      phases[phaseId] = {
        status: 'pending',
        tasks: [],
        total: 0,
        done: 0,
        percentage: 0
      }
    }
  })

  // Also check for cross_phase and dashboard_adaptation
  const crossPhase = data['cross_phase'] as RawPhaseSection | undefined
  const dashboard = data['dashboard_adaptation'] as RawPhaseSection | undefined

  // Merge cross-phase tasks into appropriate phases (or keep separate)
  // For now, we'll add them to phase 5 (Code)
  if (crossPhase) {
    const crossTasks = extractTasks(crossPhase)
    phases[5].tasks.push(...crossTasks)
    phases[5].total = phases[5].tasks.length
    phases[5].done = phases[5].tasks.filter(t => t.status === 'done').length
    phases[5].percentage = calculatePhasePercentage(phases[5].tasks)
  }

  // Update current phase based on actual progress
  meta.currentPhase = findCurrentPhase(phases)

  // Parse checkpoint
  const ccCheckpoint = parseCheckpoint(data.cc_checkpoint)

  // Parse stats
  const rawStats = data.stats
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

  const stats = {
    totalTasks: rawStats?.summary?.total_tasks || totalTasks,
    done: rawStats?.summary?.done || doneTasks,
    wip: rawStats?.summary?.wip || wipTasks,
    pending: rawStats?.summary?.pending || pendingTasks,
    blocked: rawStats?.summary?.blocked || blockedTasks,
    completionRate: rawStats?.summary?.completion_rate ||
      `${Math.round((doneTasks / totalTasks) * 100)}%`,
    nextMilestone: rawStats?.next_milestone || ''
  }

  return {
    meta,
    phases,
    ccCheckpoint,
    stats
  }
}

/**
 * Generate mock data matching our PROGRESS_LOG structure
 */
export function generateMockProgressData(): FeatureProgress {
  return parseProgressLogFromObject({
    meta: {
      feature: 'project-dashboard-system',
      feature_name: 'AI 协作开发框架 + 项目看板系统',
      current_phase: 5,
      status: 'wip',
      owner: '@Huan',
      started_at: '2024-12-09',
      last_updated: '2024-12-10T00:30:00+08:00'
    },
    phase_0_foundation: {
      status: 'wip',
      description: '建立 _system 级文档和工具',
      tasks: [
        { id: 'P0-DOC-001', task: '02_API_CONVENTIONS.md', status: 'done' },
        { id: 'P0-DOC-002', task: '03_DB_CONVENTIONS.md', status: 'done' },
        { id: 'P0-UI-001', task: '_ui_system_template/00_UI_TOKENS_TEMPLATE.md', status: 'done' },
        { id: 'P0-UI-002', task: '_ui_system_template/01_COMPONENT_LIBRARY_TEMPLATE.md', status: 'done' },
        { id: 'P0-TOOL-001', task: '/init-project Slash Command', status: 'pending' }
      ]
    },
    phase_1_kickoff: {
      status: 'done',
      tasks: [
        { id: 'P1-TPL-001', task: 'CONTEXT_TEMPLATE.md', status: 'done' },
        { id: 'P1-WF-001', task: 'START_NEW_FEATURE.md', status: 'done' }
      ]
    },
    phase_2_spec: {
      status: 'done',
      tasks: [
        { id: 'P2-TPL-001', task: 'UI_FLOW_SPEC_TEMPLATE.md', status: 'done' },
        { id: 'P2-TPL-002', task: 'API_SPEC_TEMPLATE.md', status: 'done' }
      ]
    },
    phase_3_demo: {
      status: 'done',
      tasks: [
        { id: 'P3-TPL-001', task: 'DEMO_REVIEW_TEMPLATE.md', status: 'done' },
        { id: 'P3-WF-001', task: 'UI_DEMO_WITH_MOCK_API.md', status: 'done' }
      ]
    },
    phase_4_design: {
      status: 'done',
      tasks: [
        { id: 'P4-TPL-001', task: 'DESIGN_TEMPLATE.md', status: 'done' }
      ]
    },
    phase_5_code: {
      status: 'wip',
      tasks: [
        { id: 'P5-TPL-001', task: 'DEV_PLAN_TEMPLATE.md', status: 'done' },
        { id: 'P5-WF-001', task: 'RESUME_FROM_CHECKPOINT.md', status: 'done' },
        { id: 'P5-WF-002', task: 'END_OF_DAY_PUSH.md', status: 'done' },
        { id: 'P5-WF-003', task: 'COMPACT_RECOVERY.md', status: 'done' },
        { id: 'DASH-001', task: 'projectRegistry.ts 新结构', status: 'done' },
        { id: 'DASH-002', task: 'PROGRESS_LOG.yaml 解析器', status: 'wip' }
      ]
    },
    phase_6_test: {
      status: 'done',
      tasks: [
        { id: 'P6-TPL-001', task: 'TEST_PLAN_TEMPLATE.md', status: 'done' },
        { id: 'P6-TPL-002', task: 'TEST_REPORT_TEMPLATE.md', status: 'done' }
      ]
    },
    phase_7_deploy: {
      status: 'done',
      tasks: [
        { id: 'P7-TPL-001', task: 'RELEASE_NOTE_TEMPLATE.md', status: 'done' }
      ]
    },
    cc_checkpoint: {
      session_id: 'cc-2024-12-10-003',
      last_file_edited: 'vue-app/src/utils/progressLogParser.ts',
      last_action: '创建 YAML 解析器',
      next_step: '更新 Vue 组件使用新数据结构',
      context_files: [
        'Docs/project-dashboard-system/90_PROGRESS_LOG.yaml',
        'vue-app/src/data/projectRegistry.ts'
      ]
    },
    stats: {
      summary: {
        total_tasks: 22,
        done: 19,
        wip: 1,
        pending: 2,
        completion_rate: '86%'
      },
      next_milestone: '完成看板系统适配'
    }
  })
}

// ============ Phase Role Configuration ============

const PHASE_ROLES: Record<PhaseId, Role> = {
  0: { name: 'System Lead', color: PHASE_COLORS[0], icon: 'SYS' },
  1: { name: 'Architect', color: PHASE_COLORS[1], icon: 'AR' },
  2: { name: 'AI Product Engineer', color: PHASE_COLORS[2], icon: 'PE' },
  3: { name: 'AI Product Engineer', color: PHASE_COLORS[3], icon: 'PE' },
  4: { name: 'UI Designer', color: PHASE_COLORS[4], icon: 'DS' },
  5: { name: 'Fullstack Dev', color: PHASE_COLORS[5], icon: 'DE' },
  6: { name: 'AI QA', color: PHASE_COLORS[6], icon: 'QA' },
  7: { name: 'Project Manager', color: PHASE_COLORS[7], icon: 'PM' }
}

const PHASE_OBJECTIVES: Record<PhaseId, string[]> = {
  0: ['建立系统级规范', '配置项目基础设施', '创建 UI 设计系统'],
  1: ['定义功能边界', '创建功能上下文', '识别依赖关系'],
  2: ['编写 UI Flow Spec', '定义 API 接口', '设计交互流程'],
  3: ['生成可交互原型', '验证 UI 流程', '收集反馈'],
  4: ['设计系统对齐', '组件库适配', '完成 UI 设计稿'],
  5: ['实现 API & DB', '集成前端组件', '追踪开发进度'],
  6: ['生成测试计划', '执行测试用例', '输出测试报告'],
  7: ['汇总发布内容', '生成 Release Note', '部署上线']
}

const PHASE_WORKFLOWS: Record<PhaseId, { workflow: string; command: string; agent: string; skills: string[] }> = {
  0: {
    workflow: 'foundation_setup',
    command: '/init-system',
    agent: 'System_Architect_Agent',
    skills: ['System_Design', 'Scaffold_Gen', 'UI_Token_Gen']
  },
  1: {
    workflow: 'feature_kickoff',
    command: '/kickoff',
    agent: 'Feature_Architect_Agent',
    skills: ['Context_Inheritance', 'Feature_Design']
  },
  2: {
    workflow: 'spec_generation',
    command: '/gen-spec',
    agent: 'AIP_Agent',
    skills: ['Spec_Writer', 'API_Designer']
  },
  3: {
    workflow: 'rapid_prototyping',
    command: '/gen-demo',
    agent: 'UI_Agent',
    skills: ['ui_demo_skill', 'Mock_Gen']
  },
  4: {
    workflow: 'design_finalization',
    command: '/design',
    agent: 'Design_Agent',
    skills: ['UI_Design', 'Component_Mapping']
  },
  5: {
    workflow: 'feature_implementation',
    command: '/implement',
    agent: 'Fullstack_Agent',
    skills: ['API_impl', 'DB_Migration', 'Progress_Sync']
  },
  6: {
    workflow: 'qa_automation',
    command: '/test-run',
    agent: 'QA_Agent',
    skills: ['Test_Gen', 'E2E_Runner']
  },
  7: {
    workflow: 'deployment',
    command: '/release',
    agent: 'PM_Agent',
    skills: ['Release_Manager', 'Doc_Summarizer']
  }
}

/**
 * Convert FeatureProgress to FeatureData for FeatureWorkbench display
 */
export function toFeatureData(fp: FeatureProgress): FeatureData {
  const phases: Record<string, PhaseDetail> = {}

  for (let i = 0; i <= 7; i++) {
    const phaseId = i as PhaseId
    const phase = fp.phases[phaseId]
    const workflowConfig = PHASE_WORKFLOWS[phaseId]

    // Generate task list for display
    const taskItems = phase.tasks.map(t => ({
      id: t.id,
      name: t.task,
      status: t.status,
      statusIcon: t.status === 'done' ? '✓' : t.status === 'wip' ? '⏳' : t.status === 'blocked' ? '🚫' : '○'
    }))

    // Generate logs from tasks
    const logs = phase.tasks.slice(0, 4).map(t =>
      t.status === 'done'
        ? `> ✓ ${t.task}`
        : t.status === 'wip'
          ? `> ⏳ ${t.task} (进行中...)`
          : `> ○ ${t.task} (待开始)`
    )

    // Generate artifacts from completed tasks
    const artifacts: Artifact[] = phase.tasks
      .filter(t => t.status === 'done')
      .slice(0, 3)
      .map(t => ({
        path: `docs/_foundation/${t.task}`,
        versions: ['v1.0'],
        currentVersion: 0,
        preview: `# ${t.task}\n\n任务 ${t.id} 已完成\n状态: ${t.status}\n${t.verification || ''}`
      }))

    // Generate inputs (context files from checkpoint + system refs)
    const inputs: FileRef[] = [
      ...(phaseId > 0 ? [{
        name: `Phase ${phaseId - 1} 产物`,
        isSystemRef: false
      }] : []),
      { name: 'docs/_foundation/*', path: 'docs/_foundation/', isSystemRef: true }
    ]

    phases[String(phaseId)] = {
      id: PHASE_NAMES[phaseId],
      role: PHASE_ROLES[phaseId],
      objectives: PHASE_OBJECTIVES[phaseId],
      inputs,
      processor: {
        agent: workflowConfig.agent,
        skills: workflowConfig.skills,
        workflow: workflowConfig.workflow,
        command: `${workflowConfig.command} --feature='${fp.meta.feature}'`,
        logs: logs.length > 0 ? logs : ['> 等待开始...']
      },
      artifacts: artifacts.length > 0 ? artifacts : [{
        path: `Docs/${fp.meta.feature}/phase_${phaseId}_output.md`,
        versions: ['(待生成)'],
        currentVersion: 0,
        preview: `# Phase ${phaseId}: ${PHASE_NAMES[phaseId]}\n\n状态: ${phase.status}\n进度: ${phase.percentage}%\n任务: ${phase.done}/${phase.total}`
      }],
      fsTree: generateFsTree(fp.meta.feature, phaseId, phase)
    }
  }

  return {
    featureId: fp.meta.feature,
    featureName: fp.meta.featureName,
    phases
  }
}

/**
 * Generate file system tree HTML for phase
 */
function generateFsTree(featureId: string, phaseId: PhaseId, phase: PhaseData): string {
  const doneTasks = phase.tasks.filter(t => t.status === 'done')
  const wipTasks = phase.tasks.filter(t => t.status === 'wip')

  let tree = 'Docs/<br>'
  tree += `├── <span class="fs-sys">_system/</span><br>`
  tree += `└── ${featureId}/<br>`

  doneTasks.slice(0, 3).forEach(t => {
    tree += `&nbsp;&nbsp;&nbsp;&nbsp;├── <span class="fs-highlight">${t.task.split('/').pop()} [DONE]</span><br>`
  })

  wipTasks.forEach(t => {
    tree += `&nbsp;&nbsp;&nbsp;&nbsp;└── <span class="fs-highlight" style="color:#3b82f6">${t.task.split('/').pop()} [WIP]</span><br>`
  })

  return tree
}

/**
 * Get real feature data for the project-dashboard-system
 */
export function getRealFeatureData(): FeatureData {
  const progress = generateRealProgressData()
  return toFeatureData(progress)
}

/**
 * Generate real progress data matching actual PROGRESS_LOG.yaml
 */
export function generateRealProgressData(): FeatureProgress {
  return parseProgressLogFromObject({
    meta: {
      feature: 'project-dashboard-system',
      feature_name: 'AI 协作开发框架 + 项目看板系统',
      current_phase: 5,
      status: 'wip',
      owner: '@Huan',
      started_at: '2024-12-09',
      last_updated: '2024-12-10T01:30:00+08:00'
    },
    phase_0_foundation: {
      status: 'wip',
      description: '建立 _system 级文档和工具',
      tasks: [
        { id: 'P0-DOC-001', task: '02_API_CONVENTIONS.md', status: 'done', verification: '包含 RESTful 规范、错误码定义' },
        { id: 'P0-DOC-002', task: '03_DB_CONVENTIONS.md', status: 'done', verification: '包含表命名、字段命名、索引策略' },
        { id: 'P0-UI-001', task: '_ui_system_template/00_UI_TOKENS_TEMPLATE.md', status: 'done', verification: '颜色、字体、间距、圆角、阴影' },
        { id: 'P0-UI-002', task: '_ui_system_template/01_COMPONENT_LIBRARY_TEMPLATE.md', status: 'done', verification: 'Button、Input、Table、Modal 规范' },
        { id: 'P0-UI-003', task: '_ui_system_template/02_LAYOUT_RULES_TEMPLATE.md', status: 'done', verification: '页面布局模式、栅格系统' },
        { id: 'P0-UI-004', task: '_ui_system_template/03_INTERACTION_RULES_TEMPLATE.md', status: 'done', verification: '加载态、空态、错误态' },
        { id: 'P0-UI-005', task: '_ui_system_template/04_PAGE_TEMPLATES_TEMPLATE.md', status: 'done', verification: '列表页、详情页、表单页模板' },
        { id: 'P0-UI-006', task: '_ui_system_template/05_WORKFLOW_TEMPLATES_TEMPLATE.md', status: 'done', verification: '多步骤流程、审批流程模板' },
        { id: 'P0-CC-001', task: 'CC_COLLABORATION/00_OVERVIEW.md', status: 'done', verification: '核心原则、行为约束' },
        { id: 'P0-CC-002', task: 'CC_COLLABORATION/01_COMMIT_RULES.md', status: 'done', verification: 'commit 格式、type 定义' },
        { id: 'P0-TPL-001', task: '03_TEMPLATES/CONTEXT_TEMPLATE.md', status: 'done' },
        { id: 'P0-TPL-002', task: '03_TEMPLATES/CHANGELOG_TEMPLATE.md', status: 'done' },
        { id: 'P0-TPL-003', task: '03_TEMPLATES/PROJECT_PROFILE_TEMPLATE.yaml', status: 'done' },
        { id: 'P0-TOOL-001', task: '/init-project Slash Command', status: 'pending', priority: 'P3' }
      ]
    },
    phase_1_kickoff: {
      status: 'done',
      description: '功能启动阶段的文档和工作流',
      tasks: [
        { id: 'P1-TPL-001', task: '03_TEMPLATES/CONTEXT_TEMPLATE.md', status: 'done' },
        { id: 'P1-WF-001', task: '02_WORKFLOWS/START_NEW_FEATURE.md', status: 'done' },
        { id: 'P1-TOOL-001', task: '/new-feature Slash Command', status: 'pending', priority: 'P1' },
        { id: 'P1-TOOL-002', task: 'context_writer Skill', status: 'pending', priority: 'P1' }
      ]
    },
    phase_2_spec: {
      status: 'done',
      description: '需求规格阶段的模板和工具',
      tasks: [
        { id: 'P2-TPL-001', task: '03_TEMPLATES/UI_FLOW_SPEC_TEMPLATE.md', status: 'done' },
        { id: 'P2-TPL-002', task: '03_TEMPLATES/API_SPEC_TEMPLATE.md', status: 'done' },
        { id: 'P2-TOOL-001', task: 'spec_writer Subagent', status: 'pending', priority: 'P2' },
        { id: 'P2-TOOL-002', task: '/gen-spec Slash Command', status: 'pending', priority: 'P2' }
      ]
    },
    phase_3_demo: {
      status: 'done',
      description: '原型演示阶段的模板和工具',
      tasks: [
        { id: 'P3-TPL-001', task: '03_TEMPLATES/DEMO_REVIEW_TEMPLATE.md', status: 'done' },
        { id: 'P3-WF-001', task: '02_WORKFLOWS/UI_DEMO_WITH_MOCK_API.md', status: 'done' },
        { id: 'P3-TOOL-001', task: 'ui_demo Skill', status: 'pending', priority: 'P2' },
        { id: 'P3-TOOL-002', task: 'mock_api_gen Skill', status: 'pending', priority: 'P2' },
        { id: 'P3-TOOL-003', task: '/gen-demo Slash Command', status: 'pending', priority: 'P2' }
      ]
    },
    phase_4_design: {
      status: 'done',
      description: '设计定稿阶段的模板和工具',
      tasks: [
        { id: 'P4-TPL-001', task: '03_TEMPLATES/DESIGN_TEMPLATE.md', status: 'done' },
        { id: 'P4-TOOL-001', task: 'design_reviewer Subagent', status: 'pending', priority: 'P3' },
        { id: 'P4-TOOL-002', task: 'schema_generator Skill', status: 'pending', priority: 'P3' }
      ]
    },
    phase_5_code: {
      status: 'wip',
      description: '开发实现阶段的文档和工具',
      tasks: [
        { id: 'P5-TPL-001', task: '03_TEMPLATES/DEV_PLAN_TEMPLATE.md', status: 'done' },
        { id: 'P5-TPL-002', task: '03_TEMPLATES/PROGRESS_LOG_TEMPLATE.yaml', status: 'done' },
        { id: 'P5-TPL-003', task: '03_TEMPLATES/DAILY_SUMMARY_TEMPLATE.md', status: 'done' },
        { id: 'P5-WF-001', task: '02_WORKFLOWS/RESUME_FROM_CHECKPOINT.md', status: 'done' },
        { id: 'P5-WF-002', task: '02_WORKFLOWS/END_OF_DAY_PUSH.md', status: 'done' },
        { id: 'P5-WF-003', task: '02_WORKFLOWS/COMPACT_RECOVERY.md', status: 'done' },
        { id: 'DASH-001', task: 'projectRegistry.ts 新结构', status: 'done', verification: '与 PROGRESS_LOG 格式对齐' },
        { id: 'DASH-002', task: 'progressLogParser.ts 解析器', status: 'done', verification: '能正确解析 YAML' },
        { id: 'DASH-003', task: 'ProjectDashboard.vue 8-phase', status: 'done', verification: '使用新数据结构' },
        { id: 'DASH-004', task: 'FeatureWorkbench.vue 8-phase', status: 'done', verification: '使用 PHASE_COLORS' },
        { id: 'P5-TOOL-001', task: '/iresume Slash Command', status: 'pending', priority: 'P0' },
        { id: 'P5-TOOL-002', task: '/daily-summary Slash Command', status: 'pending', priority: 'P0' },
        { id: 'P5-TOOL-003', task: '/check-progress Slash Command', status: 'pending', priority: 'P1' },
        { id: 'P5-TOOL-004', task: 'progress_updater Skill', status: 'pending', priority: 'P0' }
      ]
    },
    phase_6_test: {
      status: 'done',
      description: '测试验证阶段的模板和工具',
      tasks: [
        { id: 'P6-TPL-001', task: '03_TEMPLATES/TEST_PLAN_TEMPLATE.md', status: 'done' },
        { id: 'P6-TPL-002', task: '03_TEMPLATES/TEST_REPORT_TEMPLATE.md', status: 'done' },
        { id: 'P6-TOOL-001', task: 'test_plan_writer Subagent', status: 'pending', priority: 'P2' },
        { id: 'P6-TOOL-002', task: 'test_runner Skill', status: 'pending', priority: 'P2' },
        { id: 'P6-TOOL-003', task: '/run-tests Slash Command', status: 'pending', priority: 'P2' }
      ]
    },
    phase_7_deploy: {
      status: 'done',
      description: '发布上线阶段的模板和工具',
      tasks: [
        { id: 'P7-TPL-001', task: '03_TEMPLATES/RELEASE_NOTE_TEMPLATE.md', status: 'done' },
        { id: 'P7-TOOL-001', task: 'release_summarizer Subagent', status: 'pending', priority: 'P2' },
        { id: 'P7-TOOL-002', task: '/release Slash Command', status: 'pending', priority: 'P2' }
      ]
    },
    cc_checkpoint: {
      session_id: 'cc-2024-12-10-004',
      last_file_edited: 'vue-app/src/views/dashboard/FeatureWorkbench.vue',
      last_action: '完成看板系统适配（DASH-001~004），所有 Vue 组件已更新为 8-phase 模型',
      next_step: '让 FeatureWorkbench 展示真实数据',
      context_files: [
        'Docs/project-dashboard-system/90_PROGRESS_LOG.yaml',
        'vue-app/src/data/projectRegistry.ts',
        'vue-app/src/utils/progressLogParser.ts'
      ]
    },
    stats: {
      summary: {
        total_tasks: 59,
        done: 38,
        wip: 0,
        pending: 21,
        completion_rate: '64%'
      },
      next_milestone: '实现 Slash Commands 和 Skills'
    }
  })
}
