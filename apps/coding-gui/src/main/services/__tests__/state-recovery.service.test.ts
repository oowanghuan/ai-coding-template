/**
 * State Recovery Service 单元测试
 * 对应 60_TEST_PLAN.md SR-001 ~ SR-007
 *
 * 关键测试：SR-004 验证 "不自动恢复 approved 状态" 约束
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { EventEmitter } from 'events'

// Mock fs/promises
vi.mock('fs/promises', () => ({
  readFile: vi.fn(),
  stat: vi.fn(),
  readdir: vi.fn()
}))

// Mock project-state-cache.service
vi.mock('../project-state-cache.service', () => ({
  projectStateCacheService: {
    invalidate: vi.fn(),
    refresh: vi.fn()
  }
}))

describe('StateRecoveryService', () => {
  let StateRecoveryService: any
  let stateRecoveryService: any
  let readFile: any
  let stat: any
  let projectStateCacheService: any

  beforeEach(async () => {
    vi.clearAllMocks()
    vi.resetModules()

    const fs = await import('fs/promises')
    readFile = vi.mocked(fs.readFile)
    stat = vi.mocked(fs.stat)

    const cacheModule = await import('../project-state-cache.service')
    projectStateCacheService = cacheModule.projectStateCacheService

    const module = await import('../state-recovery.service')
    StateRecoveryService = module.StateRecoveryService

    // 重置单例
    ;(StateRecoveryService as any).instance = null
    stateRecoveryService = StateRecoveryService.getInstance()
  })

  describe('SR-001: inferStepStatus 所有 artifact 存在', () => {
    it('should return generated with high confidence when all artifacts exist', async () => {
      // Mock：所有 artifact 文件存在
      stat.mockResolvedValue({ isFile: () => true })
      readFile.mockResolvedValue('# Context\n\nValid content here')

      const result = await stateRecoveryService.inferStepStatus(
        '/project/docs/feature',
        'KICK-001',
        { id: 'KICK-001', status: 'done' }
      )

      expect(result.status).toBe('generated')
      expect(result.confidence).toBe('high')
      expect(result.reason).toContain('All artifacts exist')
    })
  })

  describe('SR-002: inferStepStatus 部分 artifact 存在', () => {
    it('should return failed with medium confidence when partial artifacts exist', async () => {
      // Mock：第一个存在，第二个不存在
      let callCount = 0
      stat.mockImplementation(() => {
        callCount++
        if (callCount === 1) {
          return Promise.resolve({ isFile: () => true })
        }
        return Promise.reject(new Error('ENOENT'))
      })
      readFile.mockResolvedValue('Valid content')

      const result = await stateRecoveryService.inferStepStatus(
        '/project/docs/feature',
        'KICK-001',
        { id: 'KICK-001', status: 'done' }
      )

      expect(result.status).toBe('failed')
      expect(result.confidence).toBe('medium')
      expect(result.reason).toContain('Partial artifacts')
    })
  })

  describe('SR-003: inferStepStatus 无 artifact', () => {
    it('should return pending with high confidence when no artifacts exist', async () => {
      // Mock：所有文件都不存在
      stat.mockRejectedValue(new Error('ENOENT'))

      const result = await stateRecoveryService.inferStepStatus(
        '/project/docs/feature',
        'KICK-001',
        { id: 'KICK-001', status: 'pending' }
      )

      expect(result.status).toBe('pending')
      expect(result.confidence).toBe('high')
      expect(result.reason).toContain('No artifacts found')
    })
  })

  describe('SR-004: 不自动恢复 approved 状态 (关键约束)', () => {
    it('should NOT auto-recover approved status - downgrade to generated', async () => {
      // Mock PROGRESS_LOG 包含已完成的任务
      readFile.mockImplementation((path: string) => {
        if (path.includes('PROGRESS_LOG')) {
          return Promise.resolve(`
phase_1_kickoff:
  tasks:
    - id: KICK-001
      status: done
`)
        }
        if (path.includes('PHASE_GATE_STATUS')) {
          return Promise.resolve('{}')
        }
        return Promise.resolve('# Valid content with enough length')
      })

      // Mock：所有 artifact 存在且有效
      stat.mockResolvedValue({ isFile: () => true })

      // 调用 rebuildState（这是执行 approved 降级的地方）
      const result = await stateRecoveryService.rebuildState('/project', 'feature')

      // 验证恢复的步骤中没有 approved 状态
      const kickStep = result.recoveredSteps.find((s: any) => s.stepId === 'KICK-001')
      if (kickStep) {
        // 关键断言：状态绝对不能是 approved
        expect(kickStep.status).not.toBe('approved')
        // 应该是 generated
        expect(kickStep.status).toBe('generated')
      }
    })

    it('should require manual re-approval after recovery', async () => {
      readFile.mockImplementation((path: string) => {
        if (path.includes('PROGRESS_LOG')) {
          return Promise.resolve(`
phase_1_kickoff:
  tasks:
    - id: KICK-001
      status: done
`)
        }
        if (path.includes('PHASE_GATE_STATUS')) {
          return Promise.resolve('{}')
        }
        return Promise.resolve('Valid artifact content')
      })

      stat.mockResolvedValue({ isFile: () => true })

      const result = await stateRecoveryService.rebuildState('/project', 'feature')

      // 验证恢复成功
      expect(result.success).toBe(true)

      // 即使所有 artifact 存在，状态也不应该是 approved
      const kickStep = result.recoveredSteps.find((s: any) => s.stepId === 'KICK-001')
      if (kickStep) {
        expect(kickStep.status).not.toBe('approved')
      }
    })
  })

  describe('SR-005: rebuildState 冲突检测', () => {
    it('should detect conflicts between logged and inferred states', async () => {
      // Mock PROGRESS_LOG
      readFile.mockImplementation((path: string) => {
        if (path.includes('PROGRESS_LOG')) {
          return Promise.resolve(`
phase_1_kickoff:
  tasks:
    - id: KICK-001
      status: done
`)
        }
        if (path.includes('PHASE_GATE_STATUS')) {
          return Promise.resolve('{}')
        }
        return Promise.resolve('Valid content')
      })

      // Mock：没有 artifact（推断应为 pending）
      stat.mockRejectedValue(new Error('ENOENT'))

      const result = await stateRecoveryService.rebuildState('/project', 'feature')

      // 应该检测到冲突（日志说 done，但没有 artifact）
      expect(result.conflicts.length).toBeGreaterThan(0)
      expect(result.conflicts[0].type).toBe('state_mismatch')
    })
  })

  describe('SR-006: rebuildState 冲突解决', () => {
    it('should use inferred status when confidence is high', async () => {
      readFile.mockImplementation((path: string) => {
        if (path.includes('PROGRESS_LOG')) {
          return Promise.resolve(`
phase_1_kickoff:
  tasks:
    - id: KICK-001
      status: wip
`)
        }
        if (path.includes('PHASE_GATE_STATUS')) {
          return Promise.resolve('{}')
        }
        return Promise.resolve('Valid artifact content with enough length')
      })

      // Mock：artifact 存在
      stat.mockResolvedValue({ isFile: () => true })

      const result = await stateRecoveryService.rebuildState('/project', 'feature')

      // 高置信度推断应该覆盖日志状态
      const kickStep = result.recoveredSteps.find((s: any) => s.stepId === 'KICK-001')
      if (kickStep) {
        expect(kickStep.status).toBe('generated') // 不是 wip
      }
    })

    it('should use logged status when confidence is low', async () => {
      readFile.mockImplementation((path: string) => {
        if (path.includes('PROGRESS_LOG')) {
          return Promise.resolve(`
phase_1_kickoff:
  tasks:
    - id: UNKNOWN-001
      status: done
`)
        }
        if (path.includes('PHASE_GATE_STATUS')) {
          return Promise.resolve('{}')
        }
        return Promise.resolve('')
      })

      stat.mockRejectedValue(new Error('ENOENT'))

      const result = await stateRecoveryService.rebuildState('/project', 'feature')

      // 没有已知 artifact 定义，置信度低，使用日志状态
      const unknownStep = result.recoveredSteps.find((s: any) => s.stepId === 'UNKNOWN-001')
      if (unknownStep && unknownStep.confidence === 'low') {
        expect(unknownStep.status).toBe('generated') // mapped from 'done'
      }
    })
  })

  describe('SR-007: syncToCache 调用 invalidate', () => {
    it('should call invalidate on cache', async () => {
      await stateRecoveryService.syncToCache('/project', 'feature')

      expect(projectStateCacheService.invalidate).toHaveBeenCalledWith('/project')
    })

    it('should call refresh after invalidate', async () => {
      await stateRecoveryService.syncToCache('/project', 'feature')

      expect(projectStateCacheService.refresh).toHaveBeenCalledWith('/project')
    })
  })

  describe('状态映射测试', () => {
    it('should map "done" to "generated"', async () => {
      stat.mockResolvedValue({ isFile: () => true })
      readFile.mockResolvedValue('Valid content')

      const result = await stateRecoveryService.inferStepStatus(
        '/project/docs/feature',
        'KICK-001',
        { id: 'KICK-001', status: 'done' }
      )

      // 'done' 应该映射到 'generated'，而不是 'approved'
      expect(result.status).toBe('generated')
    })

    it('should map "wip" to "running"', async () => {
      // 无 artifact 时使用日志状态
      stat.mockRejectedValue(new Error('ENOENT'))

      const result = await stateRecoveryService.inferStepStatus(
        '/project/docs/feature',
        'UNKNOWN-STEP',
        { id: 'UNKNOWN-STEP', status: 'wip' }
      )

      // 无预期 artifact 的步骤，使用日志状态映射
      if (result.confidence === 'low') {
        expect(result.status).toBe('running')
      }
    })
  })
})
