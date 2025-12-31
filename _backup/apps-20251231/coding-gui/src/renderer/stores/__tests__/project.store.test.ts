/**
 * Project Store 单元测试
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useProjectStore } from '../project.store'

// Mock window.electronAPI
const mockInvoke = vi.fn()
const mockOn = vi.fn()

vi.stubGlobal('window', {
  electronAPI: {
    invoke: mockInvoke,
    on: mockOn
  }
})

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}
vi.stubGlobal('localStorage', localStorageMock)

describe('useProjectStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorageMock.getItem.mockReturnValue(null)
  })

  describe('Initial State', () => {
    it('should have null currentProject initially', () => {
      const store = useProjectStore()
      expect(store.currentProject).toBeNull()
    })

    it('should have empty recentProjects initially', () => {
      const store = useProjectStore()
      expect(store.recentProjects).toEqual([])
    })

    it('should not be loading initially', () => {
      const store = useProjectStore()
      expect(store.isLoading).toBe(false)
    })

    it('should load recentProjects from localStorage', () => {
      const storedProjects = [
        { path: '/test/project', name: 'test', lastOpened: '2024-12-17' }
      ]
      localStorageMock.getItem.mockReturnValue(JSON.stringify(storedProjects))

      const store = useProjectStore()
      expect(store.recentProjects).toEqual(storedProjects)
    })
  })

  describe('openProject', () => {
    it('should set currentProject on successful open', async () => {
      const mockProject = {
        id: '/test/project',
        name: 'Test Project',
        path: '/test/project',
        features: [],
        config: { version: '1.0.0', autoSave: true }
      }

      mockInvoke.mockResolvedValue({ project: mockProject })

      const store = useProjectStore()
      const result = await store.openProject('/test/project')

      expect(result).toBe(true)
      expect(store.currentProject).toEqual(mockProject)
      expect(store.isLoading).toBe(false)
      expect(mockInvoke).toHaveBeenCalledWith('project:open', { path: '/test/project' })
    })

    it('should set error on failed open', async () => {
      mockInvoke.mockRejectedValue(new Error('Project not found'))

      const store = useProjectStore()
      const result = await store.openProject('/invalid/path')

      expect(result).toBe(false)
      expect(store.currentProject).toBeNull()
      expect(store.error).toBe('Project not found')
    })

    it('should add project to recentProjects', async () => {
      const mockProject = {
        id: '/test/project',
        name: 'Test Project',
        path: '/test/project',
        features: [],
        config: { version: '1.0.0', autoSave: true }
      }

      mockInvoke.mockResolvedValue({ project: mockProject })

      const store = useProjectStore()
      await store.openProject('/test/project')

      expect(store.recentProjects.length).toBe(1)
      expect(store.recentProjects[0].path).toBe('/test/project')
      expect(localStorageMock.setItem).toHaveBeenCalled()
    })

    it('should move existing project to top of recentProjects', async () => {
      const mockProject = {
        id: '/test/project2',
        name: 'Test Project 2',
        path: '/test/project2',
        features: [],
        config: { version: '1.0.0', autoSave: true }
      }

      mockInvoke.mockResolvedValue({ project: mockProject })

      const store = useProjectStore()

      // Add first project
      store.recentProjects = [
        { path: '/test/project1', name: 'Project 1', lastOpened: '2024-12-16' },
        { path: '/test/project2', name: 'Project 2', lastOpened: '2024-12-15' }
      ]

      await store.openProject('/test/project2')

      expect(store.recentProjects[0].path).toBe('/test/project2')
      expect(store.recentProjects.length).toBe(2)
    })
  })

  describe('refreshState', () => {
    it('should refresh project state', async () => {
      const store = useProjectStore()
      store.currentProject = {
        id: '/test/project',
        name: 'Test',
        path: '/test/project',
        features: [],
        config: { version: '1.0.0', autoSave: true }
      }

      const updatedProject = {
        ...store.currentProject,
        features: [{ id: 'feature1', name: 'Feature 1', path: '/test/project/docs/feature1', phases: [], currentPhase: 1 }]
      }

      mockInvoke.mockResolvedValue({ project: updatedProject })

      const result = await store.refreshState()

      expect(result).toBe(true)
      expect(store.currentProject?.features.length).toBe(1)
    })

    it('should return false when no project is open', async () => {
      const store = useProjectStore()
      const result = await store.refreshState()

      expect(result).toBe(false)
      expect(mockInvoke).not.toHaveBeenCalled()
    })
  })

  describe('setActiveFeature', () => {
    it('should set activeFeatureId', () => {
      const store = useProjectStore()
      store.currentProject = {
        id: '/test/project',
        name: 'Test',
        path: '/test/project',
        features: [{ id: 'feature1', name: 'Feature 1', path: '/path', phases: [], currentPhase: 1 }],
        config: { version: '1.0.0', autoSave: true }
      }

      store.setActiveFeature('feature1')

      expect(store.currentProject?.activeFeatureId).toBe('feature1')
    })
  })

  describe('closeProject', () => {
    it('should clear currentProject', () => {
      const store = useProjectStore()
      store.currentProject = {
        id: '/test/project',
        name: 'Test',
        path: '/test/project',
        features: [],
        config: { version: '1.0.0', autoSave: true }
      }
      store.error = 'some error'

      store.closeProject()

      expect(store.currentProject).toBeNull()
      expect(store.error).toBeNull()
    })
  })

  describe('Getters', () => {
    it('activeFeature should return correct feature', () => {
      const store = useProjectStore()
      store.currentProject = {
        id: '/test/project',
        name: 'Test',
        path: '/test/project',
        activeFeatureId: 'feature2',
        features: [
          { id: 'feature1', name: 'Feature 1', path: '/path1', phases: [], currentPhase: 1 },
          { id: 'feature2', name: 'Feature 2', path: '/path2', phases: [], currentPhase: 2 }
        ],
        config: { version: '1.0.0', autoSave: true }
      }

      expect(store.activeFeature?.id).toBe('feature2')
    })

    it('hasProject should return true when project is open', () => {
      const store = useProjectStore()
      expect(store.hasProject).toBe(false)

      store.currentProject = {
        id: '/test/project',
        name: 'Test',
        path: '/test/project',
        features: [],
        config: { version: '1.0.0', autoSave: true }
      }

      expect(store.hasProject).toBe(true)
    })
  })

  describe('recentProjects limit', () => {
    it('should keep only 10 recent projects', async () => {
      mockInvoke.mockResolvedValue({
        project: {
          id: '/test/new',
          name: 'New',
          path: '/test/new',
          features: [],
          config: { version: '1.0.0', autoSave: true }
        }
      })

      const store = useProjectStore()

      // Add 10 projects
      store.recentProjects = Array.from({ length: 10 }, (_, i) => ({
        path: `/test/project${i}`,
        name: `Project ${i}`,
        lastOpened: '2024-12-17'
      }))

      await store.openProject('/test/new')

      expect(store.recentProjects.length).toBe(10)
      expect(store.recentProjects[0].path).toBe('/test/new')
    })
  })
})
