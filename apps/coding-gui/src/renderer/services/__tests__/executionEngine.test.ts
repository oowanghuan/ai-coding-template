/**
 * ExecutionEngine Service 单元测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { executionEngine } from '../executionEngine'
import { configLoader } from '../configLoader'
import type { ExecutionItem, FrameworkStep, FeatureTask, PhaseConfig, GateStatus } from '../../types/workflow.types'

// Mock configLoader
vi.mock('../configLoader', () => ({
  configLoader: {
    loadPhaseConfig: vi.fn(),
    getFrameworkSteps: vi.fn(),
    loadFeatureTasks: vi.fn(),
    loadGateStatus: vi.fn(),
  },
}))

// ============================================================
// Test Fixtures
// ============================================================

const mockPhaseConfig: PhaseConfig = {
  id: 5,
  name: 'Code',
  displayName: '编码实现',
  description: '实现功能代码',
  color: '#f59e0b',
  hasExpertReview: true,
  objectives: ['按设计实现代码'],
  inputs: [],
  references: [],
  tools: [],
}

const mockFrameworkSteps: FrameworkStep[] = [
  {
    id: 'start-day',
    name: '每日开始',
    icon: 'calendar-check',
    command: '/start-day',
    position: 'before_tasks',
    applicable_phases: [0, 1, 2, 3, 4, 5, 6, 7],
    description: '同步代码',
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
    description: '发起评审',
    prerequisite: 'all_tasks_completed',
    execution_mode: 'interactive',
    owner: 'cc',
    rerun_policy: { strategy: 'confirm', confirm_message: '重新评审？' },
    expected_artifacts: [],
    verify: { type: 'file_exists' },
  },
  {
    id: 'check-gate',
    name: 'Gate 检查',
    icon: 'clipboard-check',
    command: '/check-gate',
    position: 'after_tasks',
    applicable_phases: [0, 1, 2, 3, 4, 5, 6, 7],
    description: '检查通过条件',
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
    description: '人工审批',
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
    description: '迁移阶段',
    prerequisite: 'gate_approved',
    execution_mode: 'non_interactive',
    owner: 'cc',
    rerun_policy: { strategy: 'block', block_message: '已迁移' },
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
    description: '保存进度',
    execution_mode: 'non_interactive',
    owner: 'cc',
    rerun_policy: { strategy: 'allow' },
    expected_artifacts: [],
    verify: { type: 'command_exit_code' },
  },
]

const mockFeatureTasks: FeatureTask[] = [
  { id: 'CODE-001', task: '创建开发计划', status: 'done' },
  { id: 'CODE-002', task: '实现服务层', status: 'wip' },
  { id: 'CODE-003', task: '编写测试', status: 'pending' },
]

const mockGateStatus: GateStatus = {
  feature: 'coding-GUI',
  phases: {
    5: {
      check_status: 'pending',
      approval_status: 'pending',
      review_status: 'pending',
    },
  },
}

// ============================================================
// Tests
// ============================================================

describe('ExecutionEngine', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(configLoader.loadPhaseConfig).mockResolvedValue(mockPhaseConfig)
    vi.mocked(configLoader.getFrameworkSteps).mockResolvedValue(mockFrameworkSteps)
    vi.mocked(configLoader.loadFeatureTasks).mockResolvedValue(mockFeatureTasks)
    vi.mocked(configLoader.loadGateStatus).mockResolvedValue(mockGateStatus)
  })

  // ========== buildExecutionList ==========

  describe('buildExecutionList', () => {
    it('EE-001: should merge framework steps and feature tasks', async () => {
      const list = await executionEngine.buildExecutionList(5, 'coding-GUI')

      const frameworkItems = list.filter(item => item.type === 'framework')
      const taskItems = list.filter(item => item.type === 'task')

      expect(frameworkItems.length).toBeGreaterThan(0)
      expect(taskItems.length).toBe(3) // 3 mock tasks
    })

    it('EE-002: should order items by position', async () => {
      const list = await executionEngine.buildExecutionList(5, 'coding-GUI')

      // Find indices
      const startDayIndex = list.findIndex(item => item.id === 'start-day')
      const firstTaskIndex = list.findIndex(item => item.type === 'task')
      const expertReviewIndex = list.findIndex(item => item.id === 'expert-review')
      const endDayIndex = list.findIndex(item => item.id === 'end-day')

      // Verify order: start-day < tasks < expert-review < end-day
      expect(startDayIndex).toBeLessThan(firstTaskIndex)
      expect(firstTaskIndex).toBeLessThan(expertReviewIndex)
      expect(expertReviewIndex).toBeLessThan(endDayIndex)
    })

    it('EE-003: should have start-day at the beginning', async () => {
      const list = await executionEngine.buildExecutionList(5, 'coding-GUI')

      expect(list[0].id).toBe('start-day')
    })

    it('EE-004: should have end-day at the end', async () => {
      const list = await executionEngine.buildExecutionList(5, 'coding-GUI')

      expect(list[list.length - 1].id).toBe('end-day')
    })

    it('EE-005: should compute framework step status', async () => {
      const list = await executionEngine.buildExecutionList(5, 'coding-GUI')

      const expertReview = list.find(item => item.id === 'expert-review')
      // Tasks not all completed, so expert-review should be blocked
      expect(expertReview?.status).toBe('blocked')
    })

    it('EE-006: should map feature task status', async () => {
      const list = await executionEngine.buildExecutionList(5, 'coding-GUI')

      const task1 = list.find(item => item.id === 'CODE-001')
      const task2 = list.find(item => item.id === 'CODE-002')

      expect(task1?.status).toBe('verified') // done -> verified
      expect(task2?.status).toBe('running')  // wip -> running
    })
  })

  // ========== getGroupedExecutionList ==========

  describe('getGroupedExecutionList', () => {
    it('EE-007: should group beforeTasks correctly', async () => {
      const grouped = await executionEngine.getGroupedExecutionList(5, 'coding-GUI')

      const beforeTaskIds = grouped.beforeTasks.map(item => item.id)
      expect(beforeTaskIds).toContain('start-day')
    })

    it('EE-008: should group tasks correctly', async () => {
      const grouped = await executionEngine.getGroupedExecutionList(5, 'coding-GUI')

      expect(grouped.tasks).toHaveLength(3)
      expect(grouped.tasks.every(item => item.type === 'task')).toBe(true)
    })

    it('EE-009: should group afterTasks correctly', async () => {
      const grouped = await executionEngine.getGroupedExecutionList(5, 'coding-GUI')

      const afterTaskIds = grouped.afterTasks.map(item => item.id)
      expect(afterTaskIds).toContain('expert-review')
      expect(afterTaskIds).toContain('check-gate')
      expect(afterTaskIds).toContain('approve-gate')
      expect(afterTaskIds).toContain('next-phase')
    })

    it('EE-010: should group endSteps correctly', async () => {
      const grouped = await executionEngine.getGroupedExecutionList(5, 'coding-GUI')

      const endStepIds = grouped.endSteps.map(item => item.id)
      expect(endStepIds).toContain('end-day')
    })
  })

  // ========== canExecuteItem ==========

  describe('canExecuteItem', () => {
    it('EE-011: should return true for ready status', () => {
      const item: ExecutionItem = {
        id: 'test',
        name: 'Test',
        type: 'task',
        status: 'ready',
        executionMode: 'non_interactive',
        rerunPolicy: { strategy: 'allow' },
      }

      expect(executionEngine.canExecuteItem(item)).toBe(true)
    })

    it('EE-012: should return true for failed status (retry)', () => {
      const item: ExecutionItem = {
        id: 'test',
        name: 'Test',
        type: 'task',
        status: 'failed',
        executionMode: 'non_interactive',
        rerunPolicy: { strategy: 'allow' },
      }

      expect(executionEngine.canExecuteItem(item)).toBe(true)
    })

    it('EE-013: should return false for blocked status', () => {
      const item: ExecutionItem = {
        id: 'test',
        name: 'Test',
        type: 'task',
        status: 'blocked',
        executionMode: 'non_interactive',
        rerunPolicy: { strategy: 'allow' },
      }

      expect(executionEngine.canExecuteItem(item)).toBe(false)
    })

    it('EE-014: should return false for running status', () => {
      const item: ExecutionItem = {
        id: 'test',
        name: 'Test',
        type: 'task',
        status: 'running',
        executionMode: 'non_interactive',
        rerunPolicy: { strategy: 'allow' },
      }

      expect(executionEngine.canExecuteItem(item)).toBe(false)
    })

    it('EE-015: should return false for approved status', () => {
      const item: ExecutionItem = {
        id: 'test',
        name: 'Test',
        type: 'task',
        status: 'approved',
        executionMode: 'non_interactive',
        rerunPolicy: { strategy: 'allow' },
      }

      expect(executionEngine.canExecuteItem(item)).toBe(false)
    })
  })

  // ========== handleRerunPolicy ==========

  describe('handleRerunPolicy', () => {
    const showConfirm = vi.fn()
    const showToast = vi.fn()

    beforeEach(() => {
      vi.clearAllMocks()
    })

    it('EE-016: should return true for allow strategy on first execution', async () => {
      const item: ExecutionItem = {
        id: 'test',
        name: 'Test',
        type: 'task',
        status: 'ready', // Not yet executed
        executionMode: 'non_interactive',
        rerunPolicy: { strategy: 'allow' },
      }

      const result = await executionEngine.handleRerunPolicy(item, showConfirm, showToast)

      expect(result).toBe(true)
    })

    it('EE-017: should return true for allow strategy on re-execution', async () => {
      const item: ExecutionItem = {
        id: 'test',
        name: 'Test',
        type: 'task',
        status: 'verified', // Already executed
        executionMode: 'non_interactive',
        rerunPolicy: { strategy: 'allow' },
      }

      const result = await executionEngine.handleRerunPolicy(item, showConfirm, showToast)

      expect(result).toBe(true)
    })

    it('EE-018: should return true for block strategy on first execution', async () => {
      const item: ExecutionItem = {
        id: 'test',
        name: 'Test',
        type: 'task',
        status: 'ready',
        executionMode: 'non_interactive',
        rerunPolicy: { strategy: 'block', block_message: 'Cannot re-run' },
      }

      const result = await executionEngine.handleRerunPolicy(item, showConfirm, showToast)

      expect(result).toBe(true)
      expect(showToast).not.toHaveBeenCalled()
    })

    it('EE-019: should return false and show toast for block strategy on re-execution', async () => {
      const item: ExecutionItem = {
        id: 'test',
        name: 'Test',
        type: 'task',
        status: 'approved', // Already executed
        executionMode: 'non_interactive',
        rerunPolicy: { strategy: 'block', block_message: '已审批通过' },
      }

      const result = await executionEngine.handleRerunPolicy(item, showConfirm, showToast)

      expect(result).toBe(false)
      expect(showToast).toHaveBeenCalledWith('已审批通过')
    })

    it('EE-020: should return true for confirm strategy on first execution', async () => {
      const item: ExecutionItem = {
        id: 'test',
        name: 'Test',
        type: 'task',
        status: 'ready',
        executionMode: 'non_interactive',
        rerunPolicy: { strategy: 'confirm', confirm_message: '确定重新执行？' },
      }

      const result = await executionEngine.handleRerunPolicy(item, showConfirm, showToast)

      expect(result).toBe(true)
      expect(showConfirm).not.toHaveBeenCalled()
    })

    it('EE-021: should call showConfirm for confirm strategy on re-execution', async () => {
      showConfirm.mockResolvedValue(true)

      const item: ExecutionItem = {
        id: 'test',
        name: 'Test',
        type: 'task',
        status: 'verified',
        executionMode: 'non_interactive',
        rerunPolicy: { strategy: 'confirm', confirm_message: '确定重新执行？' },
      }

      await executionEngine.handleRerunPolicy(item, showConfirm, showToast)

      expect(showConfirm).toHaveBeenCalledWith('确定重新执行？')
    })

    it('EE-022: should return true when user confirms', async () => {
      showConfirm.mockResolvedValue(true)

      const item: ExecutionItem = {
        id: 'test',
        name: 'Test',
        type: 'task',
        status: 'verified',
        executionMode: 'non_interactive',
        rerunPolicy: { strategy: 'confirm', confirm_message: '确定？' },
      }

      const result = await executionEngine.handleRerunPolicy(item, showConfirm, showToast)

      expect(result).toBe(true)
    })

    it('EE-023: should return false when user cancels', async () => {
      showConfirm.mockResolvedValue(false)

      const item: ExecutionItem = {
        id: 'test',
        name: 'Test',
        type: 'task',
        status: 'verified',
        executionMode: 'non_interactive',
        rerunPolicy: { strategy: 'confirm', confirm_message: '确定？' },
      }

      const result = await executionEngine.handleRerunPolicy(item, showConfirm, showToast)

      expect(result).toBe(false)
    })
  })

  // ========== getExecuteButtonConfig ==========

  describe('getExecuteButtonConfig', () => {
    it('EE-024: should return correct config for non_interactive mode', () => {
      const item: ExecutionItem = {
        id: 'test',
        name: 'Test',
        type: 'task',
        status: 'ready',
        executionMode: 'non_interactive',
        rerunPolicy: { strategy: 'allow' },
      }

      const config = executionEngine.getExecuteButtonConfig(item)

      expect(config.label).toBe('执行')
      expect(config.showDropdown).toBe(false)
    })

    it('EE-025: should return correct config for interactive mode', () => {
      const item: ExecutionItem = {
        id: 'test',
        name: 'Test',
        type: 'task',
        status: 'ready',
        executionMode: 'interactive',
        rerunPolicy: { strategy: 'allow' },
      }

      const config = executionEngine.getExecuteButtonConfig(item)

      expect(config.label).toBe('在终端中打开')
      expect(config.showDropdown).toBe(false)
    })

    it('EE-026: should return dropdown config for hybrid mode', () => {
      const item: ExecutionItem = {
        id: 'test',
        name: 'Test',
        type: 'task',
        status: 'ready',
        executionMode: 'hybrid',
        rerunPolicy: { strategy: 'allow' },
      }

      const config = executionEngine.getExecuteButtonConfig(item)

      expect(config.showDropdown).toBe(true)
      expect(config.dropdownOptions).toHaveLength(2)
    })

    it('EE-027: should show retry label for failed status', () => {
      const item: ExecutionItem = {
        id: 'test',
        name: 'Test',
        type: 'task',
        status: 'failed',
        executionMode: 'non_interactive',
        rerunPolicy: { strategy: 'allow' },
      }

      const config = executionEngine.getExecuteButtonConfig(item)

      expect(config.label).toBe('重试')
    })

    it('EE-028: should disable button for blocked status', () => {
      const item: ExecutionItem = {
        id: 'test',
        name: 'Test',
        type: 'task',
        status: 'blocked',
        executionMode: 'non_interactive',
        rerunPolicy: { strategy: 'allow' },
      }

      const config = executionEngine.getExecuteButtonConfig(item)

      expect(config.disabled).toBe(true)
    })
  })

  // ========== Integration scenarios ==========

  describe('Integration scenarios', () => {
    it('should correctly compute status when all tasks are done', async () => {
      vi.mocked(configLoader.loadFeatureTasks).mockResolvedValue([
        { id: 'TASK-001', task: 'Task 1', status: 'done' },
        { id: 'TASK-002', task: 'Task 2', status: 'done' },
      ])

      const list = await executionEngine.buildExecutionList(5, 'coding-GUI')

      const expertReview = list.find(item => item.id === 'expert-review')
      // All tasks done, so expert-review should be ready
      expect(expertReview?.status).toBe('ready')
    })

    it('should handle gate status correctly', async () => {
      vi.mocked(configLoader.loadGateStatus).mockResolvedValue({
        feature: 'coding-GUI',
        phases: {
          5: {
            check_status: 'passed',
            review_status: 'completed',
          },
        },
      })
      vi.mocked(configLoader.loadFeatureTasks).mockResolvedValue([
        { id: 'TASK-001', task: 'Task 1', status: 'done' },
      ])

      const list = await executionEngine.buildExecutionList(5, 'coding-GUI')

      const checkGate = list.find(item => item.id === 'check-gate')
      expect(checkGate?.status).toBe('verified')
    })
  })
})
