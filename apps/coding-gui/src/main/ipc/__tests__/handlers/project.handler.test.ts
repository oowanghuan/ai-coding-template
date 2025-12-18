/**
 * Project Handler 单元测试
 * 对应 60_TEST_PLAN.md PH-001 ~ PH-004
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

// Mock fs/promises
vi.mock('fs/promises', () => ({
  readFile: vi.fn(),
  readdir: vi.fn(),
  stat: vi.fn()
}))

describe('Project Handler', () => {
  let handleProjectOpen: any
  let handleProjectState: any
  let getCurrentProject: any
  let setCurrentProject: any
  let readFile: any
  let readdir: any
  let stat: any

  beforeEach(async () => {
    vi.clearAllMocks()
    vi.resetModules()

    const fs = await import('fs/promises')
    readFile = vi.mocked(fs.readFile)
    readdir = vi.mocked(fs.readdir)
    stat = vi.mocked(fs.stat)

    const module = await import('../../handlers/project.handler')
    handleProjectOpen = module.handleProjectOpen
    handleProjectState = module.handleProjectState
    getCurrentProject = module.getCurrentProject
    setCurrentProject = module.setCurrentProject

    // 重置当前项目
    setCurrentProject(null)
  })

  describe('PH-001: project:open 有效路径', () => {
    it('should return Project object for valid path', async () => {
      // Mock 有效的项目结构
      stat.mockImplementation((path: string) => {
        return Promise.resolve({
          isDirectory: () => true,
          isFile: () => false
        })
      })

      readdir.mockResolvedValue([
        { name: 'coding-GUI', isDirectory: () => true }
      ])

      readFile.mockImplementation((path: string) => {
        if (path.includes('project.yaml')) {
          return Promise.resolve('version: 1.0.0\nauto_save: true')
        }
        if (path.includes('90_PROGRESS_LOG.yaml')) {
          return Promise.resolve(`
meta:
  feature_name: "Coding GUI"
  current_phase: 5
phase_1_kickoff:
  status: done
  tasks: []
`)
        }
        return Promise.reject(new Error('ENOENT'))
      })

      const result = await handleProjectOpen({ path: '/test/project' })

      expect(result.project).toBeDefined()
      expect(result.project.path).toBe('/test/project')
      expect(result.project.features).toBeDefined()
    })

    it('should set current project after open', async () => {
      stat.mockResolvedValue({
        isDirectory: () => true,
        isFile: () => false
      })

      readdir.mockResolvedValue([])
      readFile.mockRejectedValue(new Error('ENOENT'))

      await handleProjectOpen({ path: '/test/project' })

      const current = getCurrentProject()
      expect(current).not.toBeNull()
      expect(current.path).toBe('/test/project')
    })
  })

  describe('PH-002: project:open 无效路径', () => {
    it('should throw error for non-existent path', async () => {
      stat.mockRejectedValue(new Error('ENOENT'))

      await expect(
        handleProjectOpen({ path: '/non/existent/path' })
      ).rejects.toThrow()
    })

    it('should throw error for file path instead of directory', async () => {
      stat.mockResolvedValue({
        isDirectory: () => false,
        isFile: () => true
      })

      await expect(
        handleProjectOpen({ path: '/path/to/file.txt' })
      ).rejects.toThrow()
    })

    it('should throw error when .claude directory missing', async () => {
      let statCount = 0
      stat.mockImplementation(() => {
        statCount++
        if (statCount === 1) {
          // 项目目录存在
          return Promise.resolve({ isDirectory: () => true })
        }
        // .claude 目录不存在
        return Promise.reject(new Error('ENOENT'))
      })

      await expect(
        handleProjectOpen({ path: '/test/project' })
      ).rejects.toThrow(/\.claude/)
    })
  })

  describe('PH-003: project:state 有效项目', () => {
    it('should return project state when project is open', async () => {
      // 先设置一个已打开的项目
      setCurrentProject({
        id: '/test/project',
        name: 'test',
        path: '/test/project',
        features: [],
        config: { version: '1.0.0', autoSave: true }
      })

      stat.mockResolvedValue({ isDirectory: () => true })
      readdir.mockResolvedValue([])

      const result = await handleProjectState()

      expect(result.project).toBeDefined()
      expect(result.features).toBeDefined()
    })

    it('should throw error when no project is open', async () => {
      setCurrentProject(null)

      await expect(handleProjectState()).rejects.toThrow(/No project/)
    })
  })

  describe('PH-004: project:state 使用缓存', () => {
    it('should update features from file system', async () => {
      setCurrentProject({
        id: '/test/project',
        name: 'test',
        path: '/test/project',
        features: [{ id: 'old-feature', name: 'Old', path: '/test/project/docs/old' }],
        config: { version: '1.0.0', autoSave: true }
      })

      stat.mockResolvedValue({ isDirectory: () => true })
      readdir.mockResolvedValue([
        { name: 'new-feature', isDirectory: () => true }
      ])
      readFile.mockImplementation((path: string) => {
        if (path.includes('90_PROGRESS_LOG.yaml')) {
          return Promise.resolve(`
meta:
  feature_name: "New Feature"
  current_phase: 1
phase_1_kickoff:
  status: wip
  tasks: []
`)
        }
        return Promise.reject(new Error('ENOENT'))
      })

      const result = await handleProjectState()

      // 应该包含新扫描的 feature
      expect(result.features.some((f: any) => f.id === 'new-feature')).toBe(true)
    })
  })

  describe('Feature scanning', () => {
    it('should parse PROGRESS_LOG correctly', async () => {
      setCurrentProject({
        id: '/test/project',
        name: 'test',
        path: '/test/project',
        features: [],
        config: { version: '1.0.0', autoSave: true }
      })

      stat.mockResolvedValue({ isDirectory: () => true })
      readdir.mockResolvedValue([
        { name: 'my-feature', isDirectory: () => true }
      ])
      readFile.mockImplementation((path: string) => {
        if (path.includes('90_PROGRESS_LOG.yaml')) {
          return Promise.resolve(`
meta:
  feature_name: "My Feature"
  current_phase: 2
  started_at: "2024-12-17"
phase_1_kickoff:
  status: done
  gate_passed: true
  tasks:
    - id: KICK-001
      task: "Create context"
      status: done
phase_2_spec:
  status: wip
  tasks:
    - id: SPEC-001
      task: "Write spec"
      status: wip
`)
        }
        return Promise.reject(new Error('ENOENT'))
      })

      const result = await handleProjectState()

      const feature = result.features.find((f: any) => f.id === 'my-feature')
      expect(feature).toBeDefined()
      expect(feature.name).toBe('My Feature')
      expect(feature.currentPhase).toBe(2)
      expect(feature.phases.length).toBe(7)

      // 验证 phase 1 状态
      const phase1 = feature.phases.find((p: any) => p.id === 'kickoff')
      expect(phase1.status).toBe('completed')
      expect(phase1.gateStatus).toBe('passed')

      // 验证 phase 2 状态
      const phase2 = feature.phases.find((p: any) => p.id === 'spec')
      expect(phase2.status).toBe('active')
    })

    it('should map task status correctly', async () => {
      setCurrentProject({
        id: '/test/project',
        name: 'test',
        path: '/test/project',
        features: [],
        config: { version: '1.0.0', autoSave: true }
      })

      stat.mockResolvedValue({ isDirectory: () => true })
      readdir.mockResolvedValue([
        { name: 'test-feature', isDirectory: () => true }
      ])
      readFile.mockImplementation((path: string) => {
        if (path.includes('90_PROGRESS_LOG.yaml')) {
          return Promise.resolve(`
meta:
  feature_name: "Test"
  current_phase: 1
phase_1_kickoff:
  status: wip
  tasks:
    - id: KICK-001
      status: done
    - id: KICK-002
      status: wip
    - id: KICK-003
      status: pending
    - id: KICK-004
      status: failed
    - id: KICK-005
      status: skipped
`)
        }
        return Promise.reject(new Error('ENOENT'))
      })

      const result = await handleProjectState()
      const feature = result.features.find((f: any) => f.id === 'test-feature')
      const phase1 = feature.phases.find((p: any) => p.id === 'kickoff')

      // 验证状态映射
      expect(phase1.steps[0].status).toBe('generated')  // done -> generated
      expect(phase1.steps[1].status).toBe('running')    // wip -> running
      expect(phase1.steps[2].status).toBe('pending')    // pending -> pending
      expect(phase1.steps[3].status).toBe('failed')     // failed -> failed
      expect(phase1.steps[4].status).toBe('skipped')    // skipped -> skipped
    })
  })
})
