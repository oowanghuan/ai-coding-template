/**
 * Approval Handler 单元测试
 * 对应 60_TEST_PLAN.md AH-001 ~ AH-005
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

// Mock fs/promises
vi.mock('fs/promises', () => ({
  readFile: vi.fn(),
  writeFile: vi.fn(),
  appendFile: vi.fn(),
  mkdir: vi.fn()
}))

// Mock child_process
vi.mock('child_process', () => ({
  execSync: vi.fn(() => 'test@example.com')
}))

// Mock os
vi.mock('os', () => ({
  hostname: vi.fn(() => 'test-host')
}))

describe('Approval Handler', () => {
  let handleApprovalSubmit: any
  let handleApprovalStatus: any
  let setCurrentProject: any
  let readFile: any
  let writeFile: any
  let appendFile: any
  let mkdir: any

  beforeEach(async () => {
    vi.clearAllMocks()
    vi.resetModules()

    const fs = await import('fs/promises')
    readFile = vi.mocked(fs.readFile)
    writeFile = vi.mocked(fs.writeFile)
    appendFile = vi.mocked(fs.appendFile)
    mkdir = vi.mocked(fs.mkdir)

    // 导入 handler
    const approvalModule = await import('../../handlers/approval.handler')
    handleApprovalSubmit = approvalModule.handleApprovalSubmit
    handleApprovalStatus = approvalModule.handleApprovalStatus

    // 导入 project handler 以设置当前项目
    const projectModule = await import('../../handlers/project.handler')
    setCurrentProject = projectModule.setCurrentProject

    // 重置当前项目
    setCurrentProject(null)
  })

  afterEach(() => {
    setCurrentProject(null)
  })

  describe('AH-001: approval:submit 有效 stepId', () => {
    it('should submit approval successfully', async () => {
      // 设置当前项目
      setCurrentProject({
        id: '/test/project',
        name: 'test',
        path: '/test/project',
        features: [{
          id: 'my-feature',
          name: 'My Feature',
          path: '/test/project/docs/my-feature'
        }],
        config: { version: '1.0.0', autoSave: true }
      })

      // Mock 文件操作
      readFile.mockRejectedValue({ code: 'ENOENT' }) // PHASE_GATE_STATUS.yaml 不存在
      writeFile.mockResolvedValue(undefined)
      appendFile.mockResolvedValue(undefined)
      mkdir.mockResolvedValue(undefined)

      const result = await handleApprovalSubmit({
        stepId: 'KICK-001',
        featureId: 'my-feature',
        action: 'approve',
        note: 'Looks good'
      })

      expect(result.success).toBe(true)
      expect(result.stepId).toBe('KICK-001')
      expect(result.newStatus).toBe('approved')
      expect(result.approvedBy).toBeDefined()
      expect(result.approvedAt).toBeDefined()
    })

    it('should update PHASE_GATE_STATUS.yaml', async () => {
      setCurrentProject({
        id: '/test/project',
        name: 'test',
        path: '/test/project',
        features: [{
          id: 'my-feature',
          name: 'My Feature',
          path: '/test/project/docs/my-feature'
        }],
        config: { version: '1.0.0', autoSave: true }
      })

      readFile.mockRejectedValue({ code: 'ENOENT' })
      writeFile.mockResolvedValue(undefined)
      appendFile.mockResolvedValue(undefined)
      mkdir.mockResolvedValue(undefined)

      await handleApprovalSubmit({
        stepId: 'SPEC-002',
        featureId: 'my-feature',
        action: 'approve'
      })

      expect(writeFile).toHaveBeenCalledWith(
        '/test/project/docs/my-feature/PHASE_GATE_STATUS.yaml',
        expect.stringContaining('SPEC-002'),
        'utf-8'
      )
    })

    it('should handle reject action', async () => {
      setCurrentProject({
        id: '/test/project',
        name: 'test',
        path: '/test/project',
        features: [{
          id: 'my-feature',
          name: 'My Feature',
          path: '/test/project/docs/my-feature'
        }],
        config: { version: '1.0.0', autoSave: true }
      })

      readFile.mockRejectedValue({ code: 'ENOENT' })
      writeFile.mockResolvedValue(undefined)
      appendFile.mockResolvedValue(undefined)
      mkdir.mockResolvedValue(undefined)

      const result = await handleApprovalSubmit({
        stepId: 'KICK-001',
        featureId: 'my-feature',
        action: 'reject',
        note: 'Needs more work'
      })

      expect(result.newStatus).toBe('rejected')
    })
  })

  describe('AH-002: approval:submit 无效 featureId', () => {
    it('should throw error for non-existent feature', async () => {
      setCurrentProject({
        id: '/test/project',
        name: 'test',
        path: '/test/project',
        features: [],
        config: { version: '1.0.0', autoSave: true }
      })

      await expect(
        handleApprovalSubmit({
          stepId: 'KICK-001',
          featureId: 'non-existent-feature',
          action: 'approve'
        })
      ).rejects.toThrow(/Feature not found/)
    })

    it('should throw error when no project is open', async () => {
      setCurrentProject(null)

      await expect(
        handleApprovalSubmit({
          stepId: 'KICK-001',
          featureId: 'any-feature',
          action: 'approve'
        })
      ).rejects.toThrow(/No project/)
    })
  })

  describe('AH-003: approval:status 有效 feature', () => {
    it('should return approval status', async () => {
      setCurrentProject({
        id: '/test/project',
        name: 'test',
        path: '/test/project',
        features: [{
          id: 'my-feature',
          name: 'My Feature',
          path: '/test/project/docs/my-feature'
        }],
        config: { version: '1.0.0', autoSave: true }
      })

      readFile.mockResolvedValue(`
phases:
  phase_1:
    gate_passed: true
    approved_by: test@example.com
    approved_at: "2024-12-17T00:00:00.000Z"
    source: gui
    steps:
      KICK-001:
        status: approved
        approved_by: test@example.com
        approved_at: "2024-12-17T00:00:00.000Z"
`)

      const result = await handleApprovalStatus({
        featureId: 'my-feature'
      })

      expect(result.gates).toBeDefined()
      expect(result.gates.length).toBe(1)
      expect(result.gates[0].status).toBe('passed')

      expect(result.steps).toBeDefined()
      expect(result.steps.length).toBe(1)
      expect(result.steps[0].stepId).toBe('KICK-001')
      expect(result.steps[0].status).toBe('approved')
    })

    it('should return empty status when file does not exist', async () => {
      setCurrentProject({
        id: '/test/project',
        name: 'test',
        path: '/test/project',
        features: [{
          id: 'my-feature',
          name: 'My Feature',
          path: '/test/project/docs/my-feature'
        }],
        config: { version: '1.0.0', autoSave: true }
      })

      readFile.mockRejectedValue({ code: 'ENOENT' })

      const result = await handleApprovalStatus({
        featureId: 'my-feature'
      })

      expect(result.gates).toEqual([])
      expect(result.steps).toEqual([])
    })
  })

  describe('AH-004: approval:status 无项目打开', () => {
    it('should throw error when no project is open', async () => {
      setCurrentProject(null)

      await expect(
        handleApprovalStatus({ featureId: 'any-feature' })
      ).rejects.toThrow(/No project/)
    })

    it('should throw error for non-existent feature', async () => {
      setCurrentProject({
        id: '/test/project',
        name: 'test',
        path: '/test/project',
        features: [],
        config: { version: '1.0.0', autoSave: true }
      })

      await expect(
        handleApprovalStatus({ featureId: 'non-existent' })
      ).rejects.toThrow(/Feature not found/)
    })
  })

  describe('AH-005: 审批日志 Append-Only', () => {
    it('should append to approval_log.jsonl', async () => {
      setCurrentProject({
        id: '/test/project',
        name: 'test',
        path: '/test/project',
        features: [{
          id: 'my-feature',
          name: 'My Feature',
          path: '/test/project/docs/my-feature'
        }],
        config: { version: '1.0.0', autoSave: true }
      })

      readFile.mockRejectedValue({ code: 'ENOENT' })
      writeFile.mockResolvedValue(undefined)
      appendFile.mockResolvedValue(undefined)
      mkdir.mockResolvedValue(undefined)

      await handleApprovalSubmit({
        stepId: 'KICK-001',
        featureId: 'my-feature',
        action: 'approve',
        note: 'LGTM'
      })

      // 验证 mkdir 被调用以确保目录存在
      expect(mkdir).toHaveBeenCalledWith(
        '/test/project/.claude/state',
        { recursive: true }
      )

      // 验证 appendFile 被调用
      expect(appendFile).toHaveBeenCalledWith(
        '/test/project/.claude/state/approval_log.jsonl',
        expect.stringContaining('"step_id":"KICK-001"'),
        'utf-8'
      )

      // 验证日志格式包含必要字段
      const appendCall = appendFile.mock.calls[0][1] as string
      const logEntry = JSON.parse(appendCall.trim())

      expect(logEntry.step_id).toBe('KICK-001')
      expect(logEntry.action).toBe('approve')
      expect(logEntry.source).toBe('gui')
      expect(logEntry.note).toBe('LGTM')
      expect(logEntry.client_info).toBeDefined()
      expect(logEntry.client_info.app_version).toBeDefined()
      expect(logEntry.client_info.hostname).toBe('test-host')
    })

    it('should use JSONL format (one JSON per line)', async () => {
      setCurrentProject({
        id: '/test/project',
        name: 'test',
        path: '/test/project',
        features: [{
          id: 'my-feature',
          name: 'My Feature',
          path: '/test/project/docs/my-feature'
        }],
        config: { version: '1.0.0', autoSave: true }
      })

      readFile.mockRejectedValue({ code: 'ENOENT' })
      writeFile.mockResolvedValue(undefined)
      appendFile.mockResolvedValue(undefined)
      mkdir.mockResolvedValue(undefined)

      await handleApprovalSubmit({
        stepId: 'KICK-001',
        featureId: 'my-feature',
        action: 'approve'
      })

      const appendCall = appendFile.mock.calls[0][1] as string

      // 验证以换行符结尾
      expect(appendCall.endsWith('\n')).toBe(true)

      // 验证是有效的 JSON
      expect(() => JSON.parse(appendCall.trim())).not.toThrow()
    })
  })

  describe('User Identity', () => {
    it('should use git config email for approval', async () => {
      setCurrentProject({
        id: '/test/project',
        name: 'test',
        path: '/test/project',
        features: [{
          id: 'my-feature',
          name: 'My Feature',
          path: '/test/project/docs/my-feature'
        }],
        config: { version: '1.0.0', autoSave: true }
      })

      readFile.mockRejectedValue({ code: 'ENOENT' })
      writeFile.mockResolvedValue(undefined)
      appendFile.mockResolvedValue(undefined)
      mkdir.mockResolvedValue(undefined)

      const result = await handleApprovalSubmit({
        stepId: 'KICK-001',
        featureId: 'my-feature',
        action: 'approve'
      })

      // mock execSync 返回 test@example.com
      expect(result.approvedBy).toBe('test@example.com')
    })
  })

  describe('Phase mapping', () => {
    it('should map step prefixes to correct phases', async () => {
      setCurrentProject({
        id: '/test/project',
        name: 'test',
        path: '/test/project',
        features: [{
          id: 'my-feature',
          name: 'My Feature',
          path: '/test/project/docs/my-feature'
        }],
        config: { version: '1.0.0', autoSave: true }
      })

      readFile.mockRejectedValue({ code: 'ENOENT' })
      writeFile.mockResolvedValue(undefined)
      appendFile.mockResolvedValue(undefined)
      mkdir.mockResolvedValue(undefined)

      const testCases = [
        { stepId: 'KICK-001', expectedPhase: 'phase_1' },
        { stepId: 'SPEC-001', expectedPhase: 'phase_2' },
        { stepId: 'DEMO-001', expectedPhase: 'phase_3' },
        { stepId: 'DSGN-001', expectedPhase: 'phase_4' },
        { stepId: 'CODE-001', expectedPhase: 'phase_5' },
        { stepId: 'TEST-001', expectedPhase: 'phase_6' },
        { stepId: 'DEPL-001', expectedPhase: 'phase_7' }
      ]

      for (const { stepId, expectedPhase } of testCases) {
        vi.clearAllMocks()
        readFile.mockRejectedValue({ code: 'ENOENT' })
        writeFile.mockResolvedValue(undefined)
        appendFile.mockResolvedValue(undefined)
        mkdir.mockResolvedValue(undefined)

        await handleApprovalSubmit({
          stepId,
          featureId: 'my-feature',
          action: 'approve'
        })

        const writeCall = writeFile.mock.calls[0][1] as string
        expect(writeCall).toContain(expectedPhase)
      }
    })
  })
})
