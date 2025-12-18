/**
 * 工作流配置系统类型定义
 * 基于 WORKFLOW_CONFIG_SYSTEM_DESIGN.md v1.1
 */

// ============================================================
// 执行状态（FSM）
// ============================================================

export type ExecutionStatus =
  | 'pending'      // 未开始，等待前置条件
  | 'blocked'      // 被前置条件阻塞
  | 'ready'        // 前置条件满足，可执行
  | 'running'      // 执行中
  | 'generated'    // 命令已完成，产物已生成
  | 'verified'     // 产物验证通过
  | 'approved'     // 人工审批通过（仅 Gate 类步骤）
  | 'failed'       // 执行失败或验证失败
  | 'skipped'      // 跳过（不适用于当前阶段）

export type ExecutionMode = 'non_interactive' | 'interactive' | 'hybrid'

export type Owner = 'human' | 'cc' | 'hybrid'

export type RerunStrategy = 'allow' | 'block' | 'confirm'

export type VerifyType = 'command_exit_code' | 'file_exists' | 'yaml_valid'

export type StepPosition = 'before_tasks' | 'after_tasks' | 'end'

export type PrerequisiteType =
  | 'all_tasks_completed'
  | 'expert_review_passed'
  | 'expert_review_passed_if_required'
  | 'check_gate_passed'
  | 'gate_approved'

// ============================================================
// 配置结构
// ============================================================

export interface RerunPolicy {
  strategy: RerunStrategy
  block_message?: string
  confirm_message?: string
  on_rerun?: string[]
}

export interface VerifyRule {
  field: string
  expected: string
}

export interface Verify {
  type: VerifyType
  path?: string
  rules?: VerifyRule[]
}

export interface ExpectedArtifact {
  path: string
  required: boolean
}

export interface FailureRecovery {
  suggestion: string
  fallback_command?: string
  log_path?: string
}

export interface FrameworkStep {
  id: string
  name: string
  icon: string
  command: string
  position: StepPosition
  applicable_phases: number[]
  description: string
  prerequisite?: PrerequisiteType

  execution_mode: ExecutionMode
  owner: Owner

  rerun_policy: RerunPolicy
  expected_artifacts: ExpectedArtifact[]
  verify: Verify

  failure_recovery?: FailureRecovery
}

export interface PhaseMetadata {
  id: number
  name: string
  display_name: string
  description: string
  has_expert_review: boolean
  color: string
}

export interface WorkflowTemplate {
  version: string
  framework_steps: FrameworkStep[]
  phases: PhaseMetadata[]
}

// ============================================================
// Phase Gate 配置
// ============================================================

export interface PhaseInput {
  name: string
  description: string
  source_phase: number
  paths: string[]
}

export interface PhaseReference {
  name: string
  path: string
  description: string
}

export interface PhaseUIConfig {
  objectives: string[]
  inputs: PhaseInput[]
  references: PhaseReference[]
}

export interface PhaseGateConfig {
  id: number
  name: string
  entry_criteria: string[]
  exit_criteria: string[]
  required_artifacts: string[]
  ui_config?: PhaseUIConfig
}

// ============================================================
// 工具配置
// ============================================================

export interface ToolConfig {
  name: string
  type: 'slash-command' | 'skill' | 'subagent'
  command: string
  description: string
  phases: number[]
  priority: 'required' | 'recommended' | 'optional'
  status: 'implemented' | 'planned'
  owner: Owner
  execution_mode: ExecutionMode
  rerun_policy?: RerunPolicy
  failure_recovery?: FailureRecovery
  usage_doc?: string
  source_path?: string
  inputs?: Array<{ name: string; description: string }>
  outputs?: Array<{ name: string; description: string }>
}

// ============================================================
// Feature 任务（来自 PROGRESS_LOG）
// ============================================================

export interface FeatureTaskArtifact {
  path: string
  status: 'pending' | 'in_progress' | 'completed'
}

/**
 * 任务命令配置
 * 支持多种执行方式
 */
export interface TaskCommand {
  type: 'slash_command' | 'skill' | 'subagent' | 'bash'
  value: string
}

export interface FeatureTask {
  id: string
  task: string
  name?: string
  status: 'pending' | 'in_progress' | 'completed' | 'done' | 'wip' | 'skipped'
  completed_at?: string
  notes?: string
  artifacts?: FeatureTaskArtifact[]
  command?: TaskCommand
}

export interface FeaturePhase {
  status: string
  gate_passed?: boolean
  tasks?: FeatureTask[]
}

export interface ProgressLog {
  meta: {
    feature: string
    feature_name: string
    current_phase: number
    status: string
    owner: string
    started_at: string
    last_updated: string
    note?: string
  }
  [key: string]: any // phase_X_name 动态字段
}

// ============================================================
// Gate 状态
// ============================================================

export interface PhaseGateStatus {
  check_status?: 'pending' | 'passed' | 'failed'
  approval_status?: 'pending' | 'approved' | 'rejected'
  review_status?: 'pending' | 'completed'
  requires_expert_review?: boolean
  transitioned?: boolean
}

export interface GateStatus {
  feature: string
  phases: Record<number, PhaseGateStatus>
}

// ============================================================
// 执行清单项
// ============================================================

export interface ExecutionItem {
  id: string
  name: string
  type: 'framework' | 'task'
  icon?: string
  command?: string
  status: ExecutionStatus
  executionMode: ExecutionMode
  rerunPolicy: RerunPolicy
  prerequisite?: PrerequisiteType
  expectedArtifacts?: ExpectedArtifact[]
  owner?: Owner
  description?: string
  failureRecovery?: FailureRecovery
  // 任务特有字段
  artifacts?: FeatureTaskArtifact[]
  notes?: string
}

// ============================================================
// 阶段完整配置
// ============================================================

export interface PhaseConfig {
  id: number
  name: string
  displayName: string
  description: string
  color: string
  hasExpertReview: boolean
  objectives: string[]
  inputs: PhaseInput[]
  references: PhaseReference[]
  tools: ToolConfig[]
}
