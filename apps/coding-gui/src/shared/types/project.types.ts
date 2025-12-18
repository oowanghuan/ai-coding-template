/**
 * 项目相关类型定义
 * 对应 40_DESIGN_FINAL.md 数据模型
 */

/** Step 状态枚举 */
export type StepStatus = 'pending' | 'running' | 'generated' | 'approved' | 'failed' | 'skipped'

/** Phase 状态枚举 */
export type PhaseStatus = 'pending' | 'active' | 'completed' | 'blocked' | 'skipped'

/** 交付物类型 */
export interface Artifact {
  id: string
  name: string
  path: string
  type: 'markdown' | 'yaml' | 'json' | 'code' | 'other'
  exists: boolean
  lastModified?: string
}

/** 交互记录 */
export interface Interaction {
  id: string
  timestamp: string
  type: 'command' | 'approval' | 'rollback' | 'manual'
  actor: 'user' | 'system' | 'ai'
  description: string
  payload?: Record<string, unknown>
}

/** 预检项目 */
export interface PreflightCheck {
  id: string
  name: string
  description: string
  status: 'pass' | 'fail' | 'skip' | 'pending'
  message?: string
}

/** Step 定义 */
export interface Step {
  id: string
  name: string
  description: string
  status: StepStatus
  artifacts: Artifact[]
  interactions: Interaction[]
  preflightChecks: PreflightCheck[]
  command?: string
  canApprove: boolean
  canRollback: boolean
}

/** Phase 定义 */
export interface Phase {
  id: string
  name: string
  description: string
  status: PhaseStatus
  steps: Step[]
  gateStatus: 'open' | 'closed' | 'passed'
}

/** Feature 定义 */
export interface Feature {
  id: string
  name: string
  path: string
  description?: string
  phases: Phase[]
  currentPhase: number
  createdAt: string
  updatedAt: string
}

/** Project 定义 */
export interface Project {
  id: string
  name: string
  path: string
  features: Feature[]
  activeFeatureId?: string
  config: ProjectConfig
}

/** 项目配置 */
export interface ProjectConfig {
  version: string
  claudeCodePath?: string
  defaultModel?: string
  autoSave?: boolean
}

/** Phase Gate 状态 */
export interface PhaseGateStatus {
  phase: number
  status: 'pending' | 'passed' | 'blocked'
  approvedBy?: string
  approvedAt?: string
  source?: 'gui' | 'cli' | 'api'
}
