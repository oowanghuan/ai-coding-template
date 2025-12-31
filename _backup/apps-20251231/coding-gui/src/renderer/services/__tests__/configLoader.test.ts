/**
 * ConfigLoader Service 单元测试
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { configLoader } from '../configLoader'
import { githubDocService } from '../githubDocService'

// Mock githubDocService
vi.mock('../githubDocService', () => ({
  githubDocService: {
    fetchDocument: vi.fn(),
    clearCache: vi.fn(),
  },
}))

// ============================================================
// Test Fixtures
// ============================================================

const mockWorkflowTemplate = {
  version: '1.1',
  framework_steps: [
    {
      id: 'start-day',
      name: '每日开始',
      icon: 'calendar-check',
      command: '/start-day',
      position: 'before_tasks',
      applicable_phases: [0, 1, 2, 3, 4, 5, 6, 7],
      description: '同步最新代码',
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
  ],
  phases: [
    { id: 0, name: 'Foundation', display_name: '基础设施', description: 'desc', has_expert_review: false, color: '#6b7280' },
    { id: 5, name: 'Code', display_name: '编码实现', description: 'desc', has_expert_review: true, color: '#f59e0b' },
  ],
}

const mockPhaseGate = {
  phases: [
    {
      id: 5,
      ui_config: {
        objectives: ['按设计实现代码', '编写单元测试'],
        inputs: [{ name: '设计文档', description: 'desc', source_phase: 4, paths: ['docs/{feature}/40_DESIGN.md'] }],
        references: [{ name: '模板', path: 'templates/code.md', description: 'desc' }],
      },
    },
  ],
}

const mockProgressLog = {
  meta: { feature: 'coding-GUI', current_phase: 5 },
  phase_5_code: {
    status: 'wip',
    tasks: [
      { id: 'CODE-001', task: '创建开发计划', status: 'done' },
      { id: 'CODE-002', task: '实现服务层', status: 'wip' },
    ],
  },
}

const mockGateStatus = {
  phases: {
    5: {
      check_status: 'passed',
      approval_status: 'approved',
      review_status: 'completed',
    },
  },
}

// ============================================================
// Tests
// ============================================================

describe('ConfigLoader', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    configLoader.clearCache()
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  // ========== loadWorkflowTemplate ==========

  describe('loadWorkflowTemplate', () => {
    it('CL-001: should load remote WORKFLOW_TEMPLATE.yaml', async () => {
      vi.mocked(githubDocService.fetchDocument).mockResolvedValue({
        content: '',
        metadata: {},
        parsedContent: mockWorkflowTemplate,
      })

      const template = await configLoader.loadWorkflowTemplate()

      expect(githubDocService.fetchDocument).toHaveBeenCalledWith(
        'CC_COLLABORATION/00_system/WORKFLOW_TEMPLATE.yaml'
      )
      expect(template.version).toBe('1.1')
      expect(template.framework_steps).toHaveLength(2)
    })

    it('CL-002: should fallback to defaults when remote fails', async () => {
      vi.mocked(githubDocService.fetchDocument).mockRejectedValue(new Error('Network error'))

      const template = await configLoader.loadWorkflowTemplate()

      expect(template.framework_steps).toBeDefined()
      expect(template.framework_steps.length).toBeGreaterThan(0)
      expect(template.framework_steps[0].id).toBe('start-day')
    })

    it('CL-003: should use cache on second call', async () => {
      vi.mocked(githubDocService.fetchDocument).mockResolvedValue({
        content: '',
        metadata: {},
        parsedContent: mockWorkflowTemplate,
      })

      await configLoader.loadWorkflowTemplate()
      await configLoader.loadWorkflowTemplate()

      expect(githubDocService.fetchDocument).toHaveBeenCalledTimes(1)
    })

    it('CL-004: should include all 6 default framework steps on fallback', async () => {
      vi.mocked(githubDocService.fetchDocument).mockRejectedValue(new Error('Network error'))

      const template = await configLoader.loadWorkflowTemplate()

      const stepIds = template.framework_steps.map(s => s.id)
      expect(stepIds).toContain('start-day')
      expect(stepIds).toContain('expert-review')
      expect(stepIds).toContain('check-gate')
      expect(stepIds).toContain('approve-gate')
      expect(stepIds).toContain('next-phase')
      expect(stepIds).toContain('end-day')
    })
  })

  // ========== loadPhaseConfig ==========

  describe('loadPhaseConfig', () => {
    beforeEach(() => {
      // Mock both template and phase gate
      vi.mocked(githubDocService.fetchDocument).mockImplementation(async (path: string) => {
        if (path.includes('WORKFLOW_TEMPLATE')) {
          return { content: '', metadata: {}, parsedContent: mockWorkflowTemplate }
        }
        if (path.includes('PHASE_GATE.yaml')) {
          return { content: '', metadata: {}, parsedContent: mockPhaseGate }
        }
        throw new Error('Not found')
      })
    })

    it('CL-005: should load phase config with complete data', async () => {
      const config = await configLoader.loadPhaseConfig(5, 'coding-GUI')

      expect(config.id).toBe(5)
      expect(config.name).toBe('Code')
      expect(config.displayName).toBe('编码实现')
      expect(config.hasExpertReview).toBe(true)
    })

    it('CL-006: should replace {feature} path variable', async () => {
      const config = await configLoader.loadPhaseConfig(5, 'coding-GUI')

      expect(config.inputs[0].paths[0]).toBe('docs/coding-GUI/40_DESIGN.md')
    })

    it('CL-007: should load ui_config from PHASE_GATE.yaml', async () => {
      const config = await configLoader.loadPhaseConfig(5, 'coding-GUI')

      expect(config.objectives).toContain('按设计实现代码')
      expect(config.inputs).toHaveLength(1)
    })

    it('CL-008: should use default objectives when ui_config not found', async () => {
      vi.mocked(githubDocService.fetchDocument).mockImplementation(async (path: string) => {
        if (path.includes('WORKFLOW_TEMPLATE')) {
          return { content: '', metadata: {}, parsedContent: mockWorkflowTemplate }
        }
        throw new Error('Not found')
      })

      const config = await configLoader.loadPhaseConfig(5)

      expect(config.objectives).toBeDefined()
      expect(config.objectives.length).toBeGreaterThan(0)
    })
  })

  // ========== loadTools ==========

  describe('loadTools', () => {
    it('CL-009: should filter tools by phase', async () => {
      const tools = await configLoader.loadTools(4)

      // Phase 4 should include expert-review
      const commandNames = tools.map(t => t.command)
      expect(commandNames).toContain('/expert-review')
    })

    it('CL-010: should not include expert-review for Phase 0', async () => {
      const tools = await configLoader.loadTools(0)

      const commandNames = tools.map(t => t.command)
      expect(commandNames).not.toContain('/expert-review')
    })
  })

  // ========== loadFeatureTasks ==========

  describe('loadFeatureTasks', () => {
    it('CL-011: should load tasks from 90_PROGRESS_LOG.yaml', async () => {
      vi.mocked(githubDocService.fetchDocument).mockResolvedValue({
        content: '',
        metadata: {},
        parsedContent: mockProgressLog,
      })

      const tasks = await configLoader.loadFeatureTasks('coding-GUI', 5)

      expect(tasks).toHaveLength(2)
      expect(tasks[0].id).toBe('CODE-001')
      expect(tasks[0].status).toBe('done')
    })

    it('CL-012: should support various phase key formats', async () => {
      const progressLogWithAltKey = {
        meta: { current_phase: 5 },
        code: {
          tasks: [{ id: 'CODE-001', task: 'Test', status: 'done' }],
        },
      }

      vi.mocked(githubDocService.fetchDocument).mockResolvedValue({
        content: '',
        metadata: {},
        parsedContent: progressLogWithAltKey,
      })

      const tasks = await configLoader.loadFeatureTasks('coding-GUI', 5)

      expect(tasks).toHaveLength(1)
    })

    it('CL-013: should return empty array when file not found', async () => {
      vi.mocked(githubDocService.fetchDocument).mockRejectedValue(new Error('Not found'))

      const tasks = await configLoader.loadFeatureTasks('coding-GUI', 5)

      expect(tasks).toEqual([])
    })
  })

  // ========== loadGateStatus ==========

  describe('loadGateStatus', () => {
    it('CL-014: should load PHASE_GATE_STATUS.yaml', async () => {
      vi.mocked(githubDocService.fetchDocument).mockResolvedValue({
        content: '',
        metadata: {},
        parsedContent: mockGateStatus,
      })

      const status = await configLoader.loadGateStatus('coding-GUI')

      expect(status.feature).toBe('coding-GUI')
      expect(status.phases[5].check_status).toBe('passed')
    })

    it('CL-015: should return default status when file not found', async () => {
      const notFoundError = new Error('Not found') as any
      notFoundError.isNotFound = true
      vi.mocked(githubDocService.fetchDocument).mockRejectedValue(notFoundError)

      const status = await configLoader.loadGateStatus('new-feature')

      expect(status.feature).toBe('new-feature')
      expect(status.phases).toEqual({})
    })
  })

  // ========== Cache Management ==========

  describe('Cache Management', () => {
    it('CL-016: clearCache should invalidate all cached data', async () => {
      vi.mocked(githubDocService.fetchDocument).mockResolvedValue({
        content: '',
        metadata: {},
        parsedContent: mockWorkflowTemplate,
      })

      await configLoader.loadWorkflowTemplate()
      expect(githubDocService.fetchDocument).toHaveBeenCalledTimes(1)

      configLoader.clearCache()

      await configLoader.loadWorkflowTemplate()
      expect(githubDocService.fetchDocument).toHaveBeenCalledTimes(2)
    })

    it('CL-017: should cache by phaseId and featureId', async () => {
      vi.mocked(githubDocService.fetchDocument).mockResolvedValue({
        content: '',
        metadata: {},
        parsedContent: mockProgressLog,
      })

      await configLoader.loadFeatureTasks('feature-1', 5)
      await configLoader.loadFeatureTasks('feature-2', 5)

      // Different features should make separate calls
      expect(githubDocService.fetchDocument).toHaveBeenCalledTimes(2)
    })
  })

  // ========== getFrameworkSteps ==========

  describe('getFrameworkSteps', () => {
    it('should filter framework steps by phase', async () => {
      vi.mocked(githubDocService.fetchDocument).mockResolvedValue({
        content: '',
        metadata: {},
        parsedContent: mockWorkflowTemplate,
      })

      const steps = await configLoader.getFrameworkSteps(5)

      // Phase 5 should include start-day and expert-review from our mock
      const stepIds = steps.map(s => s.id)
      expect(stepIds).toContain('start-day')
      expect(stepIds).toContain('expert-review')
    })

    it('should exclude expert-review for phases without it', async () => {
      vi.mocked(githubDocService.fetchDocument).mockResolvedValue({
        content: '',
        metadata: {},
        parsedContent: mockWorkflowTemplate,
      })

      const steps = await configLoader.getFrameworkSteps(0)

      // Phase 0 should not include expert-review (only phases 4,5,6)
      const stepIds = steps.map(s => s.id)
      expect(stepIds).toContain('start-day')
      expect(stepIds).not.toContain('expert-review')
    })
  })

  // ========== getCurrentPhase ==========

  describe('getCurrentPhase', () => {
    it('should return current phase from progress log', async () => {
      vi.mocked(githubDocService.fetchDocument).mockResolvedValue({
        content: '',
        metadata: {},
        parsedContent: mockProgressLog,
      })

      const phase = await configLoader.getCurrentPhase('coding-GUI')

      expect(phase).toBe(5)
    })

    it('should return default phase 1 when file not found', async () => {
      vi.mocked(githubDocService.fetchDocument).mockRejectedValue(new Error('Not found'))

      const phase = await configLoader.getCurrentPhase('new-feature')

      expect(phase).toBe(1)
    })
  })
})
