/**
 * executionStatus.ts 单元测试
 * FSM 状态计算测试
 */

import { describe, it, expect } from 'vitest'
import {
  computeFrameworkStepStatus,
  checkPrerequisite,
  mapTaskStatus,
  areAllTasksCompleted,
  getStatusStyle,
  getBlockedReason,
  canExecute,
  canRetry,
  isCompleted,
  requiresUserAction,
  type PrerequisiteContext,
} from '../executionStatus'
import type { FrameworkStep, FeatureTask, PhaseGateStatus } from '../../types/workflow.types'

// ============================================================
// Test Fixtures
// ============================================================

const createStep = (overrides: Partial<FrameworkStep> = {}): FrameworkStep => ({
  id: 'test-step',
  name: 'Test Step',
  icon: 'play',
  command: '/test',
  position: 'before_tasks',
  applicable_phases: [1, 2, 3, 4, 5, 6, 7],
  description: 'Test step description',
  execution_mode: 'non_interactive',
  owner: 'cc',
  rerun_policy: { strategy: 'allow' },
  expected_artifacts: [],
  verify: { type: 'command_exit_code' },
  ...overrides,
})

const createContext = (overrides: Partial<PrerequisiteContext> = {}): PrerequisiteContext => ({
  allTasksCompleted: false,
  expertReviewPassed: false,
  gateStatus: {},
  phaseHasExpertReview: true,
  ...overrides,
})

const createTask = (overrides: Partial<FeatureTask> = {}): FeatureTask => ({
  id: 'TASK-001',
  task: 'Test task',
  status: 'pending',
  ...overrides,
})

// ============================================================
// computeFrameworkStepStatus Tests
// ============================================================

describe('computeFrameworkStepStatus', () => {
  describe('FS-001~003: prerequisite handling', () => {
    it('FS-001: should return ready when no prerequisite', () => {
      const step = createStep({ prerequisite: undefined })
      const context = createContext()

      const status = computeFrameworkStepStatus(step, context)

      expect(status).toBe('ready')
    })

    it('FS-002: should return ready when prerequisite is met', () => {
      const step = createStep({ prerequisite: 'all_tasks_completed' })
      const context = createContext({ allTasksCompleted: true })

      const status = computeFrameworkStepStatus(step, context)

      expect(status).toBe('ready')
    })

    it('FS-003: should return blocked when prerequisite is not met', () => {
      const step = createStep({ prerequisite: 'all_tasks_completed' })
      const context = createContext({ allTasksCompleted: false })

      const status = computeFrameworkStepStatus(step, context)

      expect(status).toBe('blocked')
    })
  })

  describe('FS-004: expert-review skipped handling', () => {
    it('FS-004: should return skipped for expert-review in phase without expert review', () => {
      const step = createStep({ id: 'expert-review', prerequisite: 'all_tasks_completed' })
      const context = createContext({
        allTasksCompleted: true,
        phaseHasExpertReview: false,
      })

      const status = computeFrameworkStepStatus(step, context)

      expect(status).toBe('skipped')
    })

    it('should return ready for expert-review in phase with expert review', () => {
      const step = createStep({ id: 'expert-review', prerequisite: 'all_tasks_completed' })
      const context = createContext({
        allTasksCompleted: true,
        phaseHasExpertReview: true,
      })

      const status = computeFrameworkStepStatus(step, context)

      expect(status).toBe('ready')
    })
  })

  describe('FS-005~007: gate status handling', () => {
    it('FS-005: should return verified when check-gate passed', () => {
      const step = createStep({ id: 'check-gate' })
      const context = createContext({
        gateStatus: { check_status: 'passed' },
      })

      const status = computeFrameworkStepStatus(step, context)

      expect(status).toBe('verified')
    })

    it('FS-006: should return approved when approve-gate approved', () => {
      const step = createStep({ id: 'approve-gate' })
      const context = createContext({
        gateStatus: { approval_status: 'approved' },
      })

      const status = computeFrameworkStepStatus(step, context)

      expect(status).toBe('approved')
    })

    it('FS-007: should return failed when check-gate failed', () => {
      const step = createStep({ id: 'check-gate' })
      const context = createContext({
        gateStatus: { check_status: 'failed' },
      })

      const status = computeFrameworkStepStatus(step, context)

      expect(status).toBe('failed')
    })

    it('should return failed when approve-gate rejected', () => {
      const step = createStep({ id: 'approve-gate' })
      const context = createContext({
        gateStatus: { approval_status: 'rejected' },
      })

      const status = computeFrameworkStepStatus(step, context)

      expect(status).toBe('failed')
    })

    it('should return verified when expert-review completed', () => {
      const step = createStep({ id: 'expert-review' })
      const context = createContext({
        gateStatus: { review_status: 'completed' },
        phaseHasExpertReview: true,
      })

      const status = computeFrameworkStepStatus(step, context)

      expect(status).toBe('verified')
    })

    it('should return approved when next-phase transitioned', () => {
      const step = createStep({ id: 'next-phase' })
      const context = createContext({
        gateStatus: { transitioned: true },
      })

      const status = computeFrameworkStepStatus(step, context)

      expect(status).toBe('approved')
    })
  })
})

// ============================================================
// checkPrerequisite Tests
// ============================================================

describe('checkPrerequisite', () => {
  describe('FS-008~009: all_tasks_completed', () => {
    it('FS-008: should return true when all tasks completed', () => {
      const context = createContext({ allTasksCompleted: true })
      expect(checkPrerequisite('all_tasks_completed', context)).toBe(true)
    })

    it('FS-009: should return false when tasks not completed', () => {
      const context = createContext({ allTasksCompleted: false })
      expect(checkPrerequisite('all_tasks_completed', context)).toBe(false)
    })
  })

  describe('FS-010~011: expert_review_passed', () => {
    it('FS-010: should return true when expert review passed', () => {
      const context = createContext({ expertReviewPassed: true })
      expect(checkPrerequisite('expert_review_passed', context)).toBe(true)
    })

    it('FS-011: should return false when expert review not passed', () => {
      const context = createContext({ expertReviewPassed: false })
      expect(checkPrerequisite('expert_review_passed', context)).toBe(false)
    })
  })

  describe('FS-012~013: expert_review_passed_if_required', () => {
    it('FS-012: should return true when phase has no expert review', () => {
      const context = createContext({
        phaseHasExpertReview: false,
        expertReviewPassed: false,
      })
      expect(checkPrerequisite('expert_review_passed_if_required', context)).toBe(true)
    })

    it('FS-013: should return false when phase requires expert review but not passed', () => {
      const context = createContext({
        phaseHasExpertReview: true,
        expertReviewPassed: false,
      })
      expect(checkPrerequisite('expert_review_passed_if_required', context)).toBe(false)
    })

    it('should return true when phase requires expert review and passed', () => {
      const context = createContext({
        phaseHasExpertReview: true,
        expertReviewPassed: true,
      })
      expect(checkPrerequisite('expert_review_passed_if_required', context)).toBe(true)
    })
  })

  describe('FS-014~015: gate status prerequisites', () => {
    it('FS-014: should return true when check_gate_passed', () => {
      const context = createContext({
        gateStatus: { check_status: 'passed' },
      })
      expect(checkPrerequisite('check_gate_passed', context)).toBe(true)
    })

    it('should return false when check_gate not passed', () => {
      const context = createContext({
        gateStatus: { check_status: 'pending' },
      })
      expect(checkPrerequisite('check_gate_passed', context)).toBe(false)
    })

    it('FS-015: should return true when gate_approved', () => {
      const context = createContext({
        gateStatus: { approval_status: 'approved' },
      })
      expect(checkPrerequisite('gate_approved', context)).toBe(true)
    })

    it('should return false when gate not approved', () => {
      const context = createContext({
        gateStatus: { approval_status: 'pending' },
      })
      expect(checkPrerequisite('gate_approved', context)).toBe(false)
    })
  })
})

// ============================================================
// mapTaskStatus Tests
// ============================================================

describe('mapTaskStatus', () => {
  it('FS-016: should map "done" to "verified"', () => {
    expect(mapTaskStatus('done')).toBe('verified')
  })

  it('FS-017: should map "completed" to "verified"', () => {
    expect(mapTaskStatus('completed')).toBe('verified')
  })

  it('FS-018: should map "wip" to "running"', () => {
    expect(mapTaskStatus('wip')).toBe('running')
  })

  it('FS-019: should map "in_progress" to "running"', () => {
    expect(mapTaskStatus('in_progress')).toBe('running')
  })

  it('FS-020: should map "pending" to "ready"', () => {
    expect(mapTaskStatus('pending')).toBe('ready')
  })

  it('FS-021: should map "skipped" to "skipped"', () => {
    expect(mapTaskStatus('skipped')).toBe('skipped')
  })

  it('FS-022: should map "blocked" to "blocked"', () => {
    expect(mapTaskStatus('blocked')).toBe('blocked')
  })

  it('FS-023: should map "failed" to "failed"', () => {
    expect(mapTaskStatus('failed')).toBe('failed')
  })

  it('should map unknown status to "ready"', () => {
    expect(mapTaskStatus('unknown')).toBe('ready')
  })
})

// ============================================================
// areAllTasksCompleted Tests
// ============================================================

describe('areAllTasksCompleted', () => {
  it('FS-024: should return true for empty task list', () => {
    expect(areAllTasksCompleted([])).toBe(true)
  })

  it('FS-025: should return true when all tasks are done', () => {
    const tasks = [
      createTask({ status: 'done' }),
      createTask({ status: 'done' }),
    ]
    expect(areAllTasksCompleted(tasks)).toBe(true)
  })

  it('FS-026: should return true when all tasks are done or skipped', () => {
    const tasks = [
      createTask({ status: 'done' }),
      createTask({ status: 'skipped' }),
      createTask({ status: 'completed' }),
    ]
    expect(areAllTasksCompleted(tasks)).toBe(true)
  })

  it('FS-027: should return false when some tasks are pending', () => {
    const tasks = [
      createTask({ status: 'done' }),
      createTask({ status: 'pending' }),
    ]
    expect(areAllTasksCompleted(tasks)).toBe(false)
  })

  it('FS-028: should return false when some tasks are wip', () => {
    const tasks = [
      createTask({ status: 'done' }),
      createTask({ status: 'wip' }),
    ]
    expect(areAllTasksCompleted(tasks)).toBe(false)
  })
})

// ============================================================
// Helper Functions Tests
// ============================================================

describe('getStatusStyle', () => {
  it('FS-029: should return correct style for each status', () => {
    const statuses = [
      'pending', 'blocked', 'ready', 'running',
      'generated', 'verified', 'approved', 'failed', 'skipped'
    ] as const

    statuses.forEach(status => {
      const style = getStatusStyle(status)
      expect(style).toHaveProperty('color')
      expect(style).toHaveProperty('bgColor')
      expect(style).toHaveProperty('icon')
      expect(style).toHaveProperty('label')
    })
  })

  it('should return green color for verified status', () => {
    const style = getStatusStyle('verified')
    expect(style.color).toBe('#10b981')
  })

  it('should return red color for failed status', () => {
    const style = getStatusStyle('failed')
    expect(style.color).toBe('#ef4444')
  })
})

describe('getBlockedReason', () => {
  it('FS-030: should return correct reason for each prerequisite', () => {
    const context = createContext({ phaseHasExpertReview: true })

    expect(getBlockedReason('all_tasks_completed', context)).toContain('任务')
    expect(getBlockedReason('expert_review_passed', context)).toContain('评审')
    expect(getBlockedReason('expert_review_passed_if_required', context)).toContain('评审')
    expect(getBlockedReason('check_gate_passed', context)).toContain('Gate')
    expect(getBlockedReason('gate_approved', context)).toContain('Gate')
  })

  it('should return unknown reason for undefined prerequisite', () => {
    const context = createContext()
    expect(getBlockedReason(undefined, context)).toContain('未知')
  })
})

describe('canExecute', () => {
  it('FS-031: should return true for ready status', () => {
    expect(canExecute('ready')).toBe(true)
  })

  it('should return true for failed status (retry)', () => {
    expect(canExecute('failed')).toBe(true)
  })

  it('should return false for blocked status', () => {
    expect(canExecute('blocked')).toBe(false)
  })

  it('should return false for running status', () => {
    expect(canExecute('running')).toBe(false)
  })

  it('should return false for approved status', () => {
    expect(canExecute('approved')).toBe(false)
  })
})

describe('canRetry', () => {
  it('FS-032: should return true only for failed status', () => {
    expect(canRetry('failed')).toBe(true)
    expect(canRetry('ready')).toBe(false)
    expect(canRetry('blocked')).toBe(false)
  })
})

describe('isCompleted', () => {
  it('FS-033: should return true for verified status', () => {
    expect(isCompleted('verified')).toBe(true)
  })

  it('should return true for approved status', () => {
    expect(isCompleted('approved')).toBe(true)
  })

  it('should return false for other statuses', () => {
    expect(isCompleted('ready')).toBe(false)
    expect(isCompleted('running')).toBe(false)
    expect(isCompleted('failed')).toBe(false)
  })
})

describe('requiresUserAction', () => {
  it('should return true for ready status', () => {
    expect(requiresUserAction('ready')).toBe(true)
  })

  it('should return true for generated status', () => {
    expect(requiresUserAction('generated')).toBe(true)
  })

  it('should return true for failed status', () => {
    expect(requiresUserAction('failed')).toBe(true)
  })

  it('should return false for running status', () => {
    expect(requiresUserAction('running')).toBe(false)
  })
})
