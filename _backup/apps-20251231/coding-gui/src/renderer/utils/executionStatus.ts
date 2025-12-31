/**
 * 执行状态计算（FSM 有限状态机）
 * 基于 WORKFLOW_CONFIG_SYSTEM_DESIGN.md v1.1 第 3 章
 */

import type {
  ExecutionStatus,
  FrameworkStep,
  PhaseGateStatus,
  PrerequisiteType,
  FeatureTask,
} from '../types/workflow.types'

// ============================================================
// 状态计算上下文
// ============================================================

export interface PrerequisiteContext {
  allTasksCompleted: boolean
  expertReviewPassed: boolean
  gateStatus: PhaseGateStatus
  phaseHasExpertReview: boolean
}

// ============================================================
// 框架步骤状态计算
// ============================================================

/**
 * 计算框架步骤的执行状态
 */
export function computeFrameworkStepStatus(
  step: FrameworkStep,
  context: PrerequisiteContext
): ExecutionStatus {
  const { gateStatus, phaseHasExpertReview } = context

  // 1. 检查是否已完成（根据步骤类型）
  const completedStatus = getCompletedStatus(step.id, gateStatus)
  if (completedStatus) {
    return completedStatus
  }

  // 2. 检查前置条件
  if (step.prerequisite) {
    const prerequisiteMet = checkPrerequisite(step.prerequisite, context)
    if (!prerequisiteMet) {
      return 'blocked'
    }
  }

  // 3. 特殊处理：如果阶段没有专家评审，expert-review 步骤跳过
  if (step.id === 'expert-review' && !phaseHasExpertReview) {
    return 'skipped'
  }

  return 'ready'
}

/**
 * 获取已完成状态（如果适用）
 */
function getCompletedStatus(
  stepId: string,
  gateStatus: PhaseGateStatus
): ExecutionStatus | null {
  switch (stepId) {
    case 'expert-review':
      if (gateStatus.review_status === 'completed') {
        return 'verified'
      }
      break

    case 'check-gate':
      if (gateStatus.check_status === 'passed') {
        return 'verified'
      }
      if (gateStatus.check_status === 'failed') {
        return 'failed'
      }
      break

    case 'approve-gate':
      if (gateStatus.approval_status === 'approved') {
        return 'approved'
      }
      if (gateStatus.approval_status === 'rejected') {
        return 'failed'
      }
      break

    case 'next-phase':
      if (gateStatus.transitioned) {
        return 'approved'
      }
      break
  }

  return null
}

/**
 * 检查前置条件是否满足
 */
export function checkPrerequisite(
  prerequisite: PrerequisiteType,
  context: PrerequisiteContext
): boolean {
  const { allTasksCompleted, expertReviewPassed, gateStatus, phaseHasExpertReview } = context

  switch (prerequisite) {
    case 'all_tasks_completed':
      return allTasksCompleted

    case 'expert_review_passed':
      return expertReviewPassed

    case 'expert_review_passed_if_required':
      // 如果阶段没有专家评审要求，则视为通过
      if (!phaseHasExpertReview) {
        return true
      }
      return expertReviewPassed

    case 'check_gate_passed':
      return gateStatus.check_status === 'passed'

    case 'gate_approved':
      return gateStatus.approval_status === 'approved'

    default:
      return true
  }
}

// ============================================================
// Feature 任务状态映射
// ============================================================

/**
 * 将 PROGRESS_LOG 中的任务状态映射到 FSM 状态
 */
export function mapTaskStatus(status: string): ExecutionStatus {
  switch (status) {
    case 'done':
    case 'completed':
      return 'verified'

    case 'wip':
    case 'in_progress':
      return 'running'

    case 'skipped':
      return 'skipped'

    case 'blocked':
      return 'blocked'

    case 'failed':
      return 'failed'

    case 'pending':
    default:
      return 'ready' // 任务默认为可执行状态
  }
}

/**
 * 检查所有任务是否完成
 */
export function areAllTasksCompleted(tasks: FeatureTask[]): boolean {
  if (tasks.length === 0) {
    return true // 没有任务视为完成
  }

  return tasks.every(task => {
    const status = task.status
    return status === 'done' || status === 'completed' || status === 'skipped'
  })
}

// ============================================================
// 状态显示辅助
// ============================================================

/**
 * 获取状态的显示样式
 */
export function getStatusStyle(status: ExecutionStatus): {
  color: string
  bgColor: string
  icon: string
  label: string
} {
  const styles: Record<ExecutionStatus, { color: string; bgColor: string; icon: string; label: string }> = {
    pending: {
      color: '#9ca3af',
      bgColor: '#f3f4f6',
      icon: 'clock',
      label: '待处理',
    },
    blocked: {
      color: '#9ca3af',
      bgColor: '#f3f4f6',
      icon: 'lock',
      label: '已锁定',
    },
    ready: {
      color: '#3b82f6',
      bgColor: '#eff6ff',
      icon: 'play',
      label: '可执行',
    },
    running: {
      color: '#3b82f6',
      bgColor: '#eff6ff',
      icon: 'loading',
      label: '执行中',
    },
    generated: {
      color: '#f59e0b',
      bgColor: '#fffbeb',
      icon: 'file',
      label: '待验证',
    },
    verified: {
      color: '#10b981',
      bgColor: '#ecfdf5',
      icon: 'check',
      label: '已验证',
    },
    approved: {
      color: '#10b981',
      bgColor: '#ecfdf5',
      icon: 'check-circle',
      label: '已通过',
    },
    failed: {
      color: '#ef4444',
      bgColor: '#fef2f2',
      icon: 'x-circle',
      label: '失败',
    },
    skipped: {
      color: '#9ca3af',
      bgColor: '#f3f4f6',
      icon: 'minus',
      label: '跳过',
    },
  }

  return styles[status]
}

/**
 * 获取阻塞原因描述
 */
export function getBlockedReason(
  prerequisite: PrerequisiteType | undefined,
  context: PrerequisiteContext
): string {
  if (!prerequisite) {
    return '未知原因'
  }

  switch (prerequisite) {
    case 'all_tasks_completed':
      return '请先完成所有 Feature 任务'

    case 'expert_review_passed':
      return '请先完成专家评审'

    case 'expert_review_passed_if_required':
      if (context.phaseHasExpertReview) {
        return '请先完成专家评审'
      }
      return '请完成前置步骤'

    case 'check_gate_passed':
      return '请先通过 Gate 检查'

    case 'gate_approved':
      return '请先审批 Gate'

    default:
      return '请完成前置步骤'
  }
}

/**
 * 判断步骤是否可执行
 */
export function canExecute(status: ExecutionStatus): boolean {
  return status === 'ready' || status === 'failed'
}

/**
 * 判断步骤是否可重试
 */
export function canRetry(status: ExecutionStatus): boolean {
  return status === 'failed'
}

/**
 * 判断步骤是否已完成（包括 verified 和 approved）
 */
export function isCompleted(status: ExecutionStatus): boolean {
  return status === 'verified' || status === 'approved'
}

/**
 * 判断步骤是否需要用户操作
 */
export function requiresUserAction(status: ExecutionStatus): boolean {
  return status === 'ready' || status === 'generated' || status === 'failed'
}
