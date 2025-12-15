// Project Registry - Aligned with PROGRESS_LOG.yaml structure
// This file defines types and utilities for the 8-phase AI workflow system

// ============ Type Definitions ============

// Phase status from PROGRESS_LOG.yaml
export type PhaseStatus = 'pending' | 'wip' | 'done' | 'blocked'

// Task status
export type TaskStatus = 'pending' | 'wip' | 'done' | 'blocked'

// Task priority
export type TaskPriority = 'P0' | 'P1' | 'P2' | 'P3'

// Phase ID (0-7)
export type PhaseId = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7

// Phase names matching 04_AI_WORKFLOW.md
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

// Phase colors for UI
export const PHASE_COLORS: Record<PhaseId, string> = {
  0: '#8b5cf6', // Purple - System
  1: '#6366f1', // Indigo - Architect
  2: '#f43f5e', // Rose - AI PE
  3: '#ec4899', // Pink - AI PE Demo
  4: '#3b82f6', // Blue - Design
  5: '#10b981', // Green - Dev
  6: '#f59e0b', // Amber - QA
  7: '#06b6d4'  // Cyan - Deploy
}

// Single task in a phase
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

// Phase data structure
export interface PhaseData {
  status: PhaseStatus
  description?: string
  tasks: Task[]
  // Computed
  total: number
  done: number
  percentage: number
}

// CC Checkpoint for recovery
export interface CCCheckpoint {
  sessionId: string
  lastFileEdited: string
  lastAction: string
  nextStep: string
  contextFiles: string[]
  tempState?: Record<string, unknown>
}

// Feature/Project metadata
export interface FeatureMeta {
  feature: string
  featureName: string
  currentPhase: PhaseId
  status: PhaseStatus
  owner: string
  startedAt: string
  lastUpdated: string
}

// Complete feature data (parsed from PROGRESS_LOG.yaml)
export interface FeatureProgress {
  meta: FeatureMeta
  phases: Record<PhaseId, PhaseData>
  ccCheckpoint: CCCheckpoint
  stats: {
    totalTasks: number
    done: number
    wip: number
    pending: number
    blocked: number
    completionRate: string
    nextMilestone: string
  }
}

// Project for dashboard display
export interface DashboardProject {
  id: string
  name: string
  owner: string
  status: PhaseStatus
  currentPhase: PhaseId
  completionRate: number
  phases: DashboardPhase[]
  lastUpdated: string
}

// Phase for dashboard timeline view
export interface DashboardPhase {
  id: PhaseId
  name: string
  status: PhaseStatus
  percentage: number
  tasksDone: number
  tasksTotal: number
}

// ============ Utility Functions ============

/**
 * Calculate phase percentage from tasks
 */
export function calculatePhasePercentage(tasks: Task[]): number {
  if (tasks.length === 0) return 0
  const done = tasks.filter(t => t.status === 'done').length
  return Math.round((done / tasks.length) * 100)
}

/**
 * Determine phase status from tasks
 */
export function determinePhaseStatus(tasks: Task[]): PhaseStatus {
  if (tasks.length === 0) return 'pending'

  const statuses = tasks.map(t => t.status)

  if (statuses.every(s => s === 'done')) return 'done'
  if (statuses.some(s => s === 'blocked')) return 'blocked'
  if (statuses.some(s => s === 'wip')) return 'wip'
  if (statuses.some(s => s === 'done')) return 'wip' // Partial progress

  return 'pending'
}

/**
 * Determine project status from phases
 */
export function determineProjectStatus(phases: Record<PhaseId, PhaseData>): PhaseStatus {
  const phaseStatuses = Object.values(phases).map(p => p.status)

  if (phaseStatuses.every(s => s === 'done')) return 'done'
  if (phaseStatuses.some(s => s === 'blocked')) return 'blocked'
  if (phaseStatuses.some(s => s === 'wip')) return 'wip'

  return 'pending'
}

/**
 * Find current phase (first non-done phase)
 */
export function findCurrentPhase(phases: Record<PhaseId, PhaseData>): PhaseId {
  for (let i = 0; i <= 7; i++) {
    const phase = phases[i as PhaseId]
    if (phase && phase.status !== 'done') {
      return i as PhaseId
    }
  }
  return 7 // All done, return last phase
}

/**
 * Calculate overall completion rate
 */
export function calculateOverallCompletion(phases: Record<PhaseId, PhaseData>): number {
  let totalTasks = 0
  let doneTasks = 0

  Object.values(phases).forEach(phase => {
    totalTasks += phase.total
    doneTasks += phase.done
  })

  if (totalTasks === 0) return 0
  return Math.round((doneTasks / totalTasks) * 100)
}

/**
 * Convert FeatureProgress to DashboardProject
 */
export function toDashboardProject(fp: FeatureProgress): DashboardProject {
  const phases: DashboardPhase[] = []

  for (let i = 0; i <= 7; i++) {
    const phaseId = i as PhaseId
    const phase = fp.phases[phaseId]

    if (phase) {
      phases.push({
        id: phaseId,
        name: PHASE_NAMES[phaseId],
        status: phase.status,
        percentage: phase.percentage,
        tasksDone: phase.done,
        tasksTotal: phase.total
      })
    } else {
      phases.push({
        id: phaseId,
        name: PHASE_NAMES[phaseId],
        status: 'pending',
        percentage: 0,
        tasksDone: 0,
        tasksTotal: 0
      })
    }
  }

  return {
    id: fp.meta.feature,
    name: fp.meta.featureName,
    owner: fp.meta.owner,
    status: fp.meta.status,
    currentPhase: fp.meta.currentPhase,
    completionRate: calculateOverallCompletion(fp.phases),
    phases,
    lastUpdated: fp.meta.lastUpdated
  }
}

// ============ Status Display Helpers ============

export const STATUS_LABELS: Record<PhaseStatus, string> = {
  pending: '待开始',
  wip: '进行中',
  done: '已完成',
  blocked: '阻塞'
}

export const STATUS_COLORS: Record<PhaseStatus, string> = {
  pending: '#94a3b8', // Slate
  wip: '#3b82f6',     // Blue
  done: '#10b981',    // Green
  blocked: '#ef4444'  // Red
}

export const PRIORITY_LABELS: Record<TaskPriority, string> = {
  P0: '必须',
  P1: '高优',
  P2: '标准',
  P3: '低优'
}

export const PRIORITY_COLORS: Record<TaskPriority, string> = {
  P0: '#ef4444', // Red
  P1: '#f59e0b', // Amber
  P2: '#3b82f6', // Blue
  P3: '#94a3b8'  // Slate
}

// ============ Gantt Chart Types ============

// Phase schedule for Gantt view
export interface PhaseSchedule {
  phaseId: PhaseId
  phaseName: string
  startDate: string         // "2024-12-09"
  endDate: string           // "2024-12-10"
  status: PhaseStatus
  progress: number          // 0-100
}

// Feature entry for Gantt dashboard
export interface GanttFeatureEntry {
  id: string                // "project-dashboard-system"
  name: string              // "项目看板系统"
  owner: string             // "@Huan"
  startDate: string         // 功能整体开始日期
  endDate: string           // 功能整体结束日期（预估）
  schedule: PhaseSchedule[] // 各 Phase 的时间安排
  progressSummary: string   // 进度摘要（弹窗展示）
  progressLogPath: string   // PROGRESS_LOG.yaml 路径
  archived?: boolean        // 是否已归档（已交付的功能设为 true 隐藏）
}

// Daily standup highlight
export interface StandupHighlight {
  featureId: string
  featureName: string
  summary: string
}

// Daily standup blocker
export interface StandupBlocker {
  featureId: string
  issue: string
  blockedSince: string
}

// Daily standup data
export interface DailyStandup {
  date: string
  generatedBy: string
  generatedAt: string
  highlights: StandupHighlight[]
  blockers: StandupBlocker[]
  tomorrow: { featureId: string; plan: string }[]
  milestones: { date: string; content: string }[]
}

// ============ Gantt Chart Data ============

// Project features for Gantt view
// 数据来源：各功能的 PROGRESS_LOG.yaml
// 最后同步：2025-12-11
export const ganttFeatures: GanttFeatureEntry[] = [
  {
    id: 'cc-tools-library',
    name: 'Claude Code 工具库',
    owner: '@Huan',
    startDate: '2025-12-05',
    endDate: '2025-12-08',
    schedule: [
      {
        phaseId: 1,
        phaseName: 'Kickoff',
        startDate: '2025-12-05',
        endDate: '2025-12-05',
        status: 'done',
        progress: 100
      },
      {
        phaseId: 5,
        phaseName: 'Code',
        startDate: '2025-12-05',
        endDate: '2025-12-06',
        status: 'done',
        progress: 100
      },
      {
        phaseId: 6,
        phaseName: 'Test',
        startDate: '2025-12-07',
        endDate: '2025-12-07',
        status: 'done',
        progress: 100
      },
      {
        phaseId: 7,
        phaseName: 'Deploy',
        startDate: '2025-12-08',
        endDate: '2025-12-08',
        status: 'done',
        progress: 100
      }
    ],
    progressSummary: '功能已完成！10 个 Slash Commands + 13 个 Skills + 4 个 Subagents 全部实现。完成率 100%。',
    progressLogPath: 'docs/cc-tools-library/90_PROGRESS_LOG.yaml',
    archived: true  // 已完成交付，归档隐藏
  },
  {
    id: 'gantt-dashboard',
    name: '甘特图看板系统',
    owner: '@Huan',
    startDate: '2025-12-06',
    endDate: '2025-12-07',
    schedule: [
      {
        phaseId: 1,
        phaseName: 'Kickoff',
        startDate: '2025-12-06',
        endDate: '2025-12-06',
        status: 'done',
        progress: 100
      },
      {
        phaseId: 4,
        phaseName: 'Design',
        startDate: '2025-12-06',
        endDate: '2025-12-06',
        status: 'done',
        progress: 100
      },
      {
        phaseId: 5,
        phaseName: 'Code',
        startDate: '2025-12-06',
        endDate: '2025-12-07',
        status: 'done',
        progress: 100
      }
    ],
    progressSummary: '功能已完成！甘特图看板系统开发完成，支持 TODAY 标志线、日/周/月切换。完成率 100%。',
    progressLogPath: 'docs/gantt-dashboard/90_PROGRESS_LOG.yaml',
    archived: true  // 已完成交付，归档隐藏
  },
  {
    id: 'github-doc-viewer',
    name: 'GitHub 文档查看器',
    owner: '@Huan',
    startDate: '2025-12-07',
    endDate: '2025-12-09',
    schedule: [
      {
        phaseId: 1,
        phaseName: 'Kickoff',
        startDate: '2025-12-07',
        endDate: '2025-12-07',
        status: 'done',
        progress: 100
      },
      {
        phaseId: 2,
        phaseName: 'Spec',
        startDate: '2025-12-07',
        endDate: '2025-12-07',
        status: 'done',
        progress: 100
      },
      {
        phaseId: 4,
        phaseName: 'Design',
        startDate: '2025-12-07',
        endDate: '2025-12-07',
        status: 'done',
        progress: 100
      },
      {
        phaseId: 5,
        phaseName: 'Code',
        startDate: '2025-12-08',
        endDate: '2025-12-08',
        status: 'done',
        progress: 100
      },
      {
        phaseId: 6,
        phaseName: 'Test',
        startDate: '2025-12-09',
        endDate: '2025-12-09',
        status: 'done',
        progress: 100
      }
    ],
    progressSummary: '功能已完成！Edge Function 部署成功，文档查看器正常工作。完成率 89%。',
    progressLogPath: 'docs/github-doc-viewer/90_PROGRESS_LOG.yaml',
    archived: true  // 已完成交付，归档隐藏
  },
  {
    id: 'panorama-guide',
    name: '全景指南页面',
    owner: '@Huan',
    startDate: '2025-12-09',
    endDate: '2025-12-11',
    schedule: [
      {
        phaseId: 0,
        phaseName: 'Foundation',
        startDate: '2025-12-09',
        endDate: '2025-12-09',
        status: 'done',
        progress: 100
      },
      {
        phaseId: 1,
        phaseName: 'Kickoff',
        startDate: '2025-12-09',
        endDate: '2025-12-09',
        status: 'done',
        progress: 100
      },
      {
        phaseId: 2,
        phaseName: 'Spec',
        startDate: '2025-12-10',
        endDate: '2025-12-10',
        status: 'done',
        progress: 100
      },
      {
        phaseId: 3,
        phaseName: 'Demo',
        startDate: '2025-12-10',
        endDate: '2025-12-11',
        status: 'done',
        progress: 100
      },
      {
        phaseId: 7,
        phaseName: 'Deploy',
        startDate: '2025-12-11',
        endDate: '2025-12-11',
        status: 'done',
        progress: 100
      }
    ],
    progressSummary: '功能已完成！5 屏渐进式引导页面已部署为应用首页。完成率 100%。',
    progressLogPath: 'docs/panorama-guide/90_PROGRESS_LOG.yaml',
    archived: true  // 已完成交付，归档隐藏
  },
  {
    id: 'project-dashboard-system',
    name: 'AI 协作开发框架',
    owner: '@Huan',
    startDate: '2025-12-05',
    endDate: '2025-12-11',
    schedule: [
      {
        phaseId: 0,
        phaseName: 'Foundation',
        startDate: '2025-12-05',
        endDate: '2025-12-09',
        status: 'done',
        progress: 100
      },
      {
        phaseId: 1,
        phaseName: 'Kickoff',
        startDate: '2025-12-09',
        endDate: '2025-12-09',
        status: 'done',
        progress: 100
      },
      {
        phaseId: 2,
        phaseName: 'Spec',
        startDate: '2025-12-09',
        endDate: '2025-12-10',
        status: 'done',
        progress: 100
      },
      {
        phaseId: 5,
        phaseName: 'Code',
        startDate: '2025-12-10',
        endDate: '2025-12-11',
        status: 'done',
        progress: 100
      },
      {
        phaseId: 7,
        phaseName: 'Deploy',
        startDate: '2025-12-11',
        endDate: '2025-12-11',
        status: 'done',
        progress: 100
      }
    ],
    progressSummary: '📚 框架样例：8 阶段工作流 + 全套模板文档 + 10 个 Slash Commands + 13 个 Skills + 4 个 Subagents。点击查看完整工作流演示。',
    progressLogPath: 'docs/project-dashboard-system/90_PROGRESS_LOG.yaml',
    archived: false  // 作为样例项目展示，不归档
  }
]

// Current daily standup data
export const currentDailyStandup: DailyStandup = {
  date: '2025-12-11',
  generatedBy: 'CC',
  generatedAt: '2025-12-11T14:00:00+08:00',
  highlights: [
    {
      featureId: 'cc-tools-library',
      featureName: 'Claude Code 工具库',
      summary: '功能完成！10 个 Slash Commands + 13 个 Skills + 4 个 Subagents 全部实现并测试通过'
    },
    {
      featureId: 'panorama-guide',
      featureName: '全景指南页面',
      summary: 'Demo 阶段 91% 完成，5 屏渐进式引导页面开发中'
    }
  ],
  blockers: [],
  tomorrow: [
    { featureId: 'panorama-guide', plan: '完成 Demo 评审，添加导航入口' },
    { featureId: 'project-dashboard-system', plan: '继续完善 Phase 0 工具实现' }
  ],
  milestones: [
    { date: '2025-12-11', content: 'Claude Code 工具库 v2.2 发布' },
    { date: '2025-12-15', content: '全景指南页面完成' },
    { date: '2025-12-20', content: 'AI 协作开发框架 v1.0 发布' }
  ]
}

// ============ Gantt Utility Functions ============

/**
 * Calculate days between two dates
 */
export function daysBetween(date1: Date, date2: Date): number {
  const oneDay = 24 * 60 * 60 * 1000
  return Math.round((date2.getTime() - date1.getTime()) / oneDay)
}

/**
 * Calculate timeline range from features
 */
export function calculateTimelineRange(features: GanttFeatureEntry[]): { start: Date; end: Date } {
  const allDates: string[] = []

  features.forEach(f => {
    f.schedule.forEach(s => {
      allDates.push(s.startDate, s.endDate)
    })
  })

  if (allDates.length === 0) {
    const today = new Date()
    return { start: today, end: today }
  }

  allDates.sort()
  return {
    start: new Date(allDates[0]),
    end: new Date(allDates[allDates.length - 1])
  }
}

/**
 * Generate date range array
 */
export function generateDateRange(start: Date, end: Date): Date[] {
  const dates: Date[] = []
  const current = new Date(start)

  while (current <= end) {
    dates.push(new Date(current))
    current.setDate(current.getDate() + 1)
  }

  return dates
}

/**
 * Format date for display
 */
export function formatDateShort(date: Date): string {
  return `${date.getMonth() + 1}/${date.getDate()}`
}

/**
 * Get weekday name in Chinese
 */
export function getWeekdayCN(date: Date): string {
  const weekdays = ['日', '一', '二', '三', '四', '五', '六']
  return weekdays[date.getDay()]
}

/**
 * Check if date is today
 */
export function isToday(date: Date): boolean {
  const today = new Date()
  return date.toDateString() === today.toDateString()
}

/**
 * Check if date is weekend
 */
export function isWeekend(date: Date): boolean {
  const day = date.getDay()
  return day === 0 || day === 6
}
