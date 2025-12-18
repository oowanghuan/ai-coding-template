/**
 * Phase Store 单元测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { usePhaseStore } from '../phase.store'
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
vi.stubGlobal('localStorage', {
  getItem: vi.fn(() => null),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
})

describe('usePhaseStore', () => {
  let projectStore: ReturnType<typeof useProjectStore>
  let phaseStore: ReturnType<typeof usePhaseStore>

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()

    projectStore = useProjectStore()
    phaseStore = usePhaseStore()
  })

  describe('Initial State', () => {
    it('should have default currentPhaseIndex of 0', () => {
      expect(phaseStore.currentPhaseIndex).toBe(0)
    })

    it('should have null currentStepId', () => {
      expect(phaseStore.currentStepId).toBeNull()
    })

    it('should have null approvingStepId', () => {
      expect(phaseStore.approvingStepId).toBeNull()
    })
  })

  describe('phases getter', () => {
    it('should return empty array when no project', () => {
      expect(phaseStore.phases).toEqual([])
    })

    it('should return feature phases when project is open', () => {
      projectStore.currentProject = {
        id: '/test/project',
        name: 'Test',
        path: '/test/project',
        activeFeatureId: 'feature1',
        features: [{
          id: 'feature1',
          name: 'Feature 1',
          path: '/path',
          currentPhase: 1,
          phases: [
            { id: 'kickoff', name: 'Kickoff', status: 'completed', steps: [] },
            { id: 'spec', name: 'Spec', status: 'active', steps: [] }
          ]
        }],
        config: { version: '1.0.0', autoSave: true }
      }

      expect(phaseStore.phases.length).toBe(2)
      expect(phaseStore.phases[0].id).toBe('kickoff')
    })
  })

  describe('setCurrentPhase', () => {
    beforeEach(() => {
      projectStore.currentProject = {
        id: '/test/project',
        name: 'Test',
        path: '/test/project',
        activeFeatureId: 'feature1',
        features: [{
          id: 'feature1',
          name: 'Feature 1',
          path: '/path',
          currentPhase: 1,
          phases: [
            { id: 'kickoff', name: 'Kickoff', status: 'completed', steps: [{ id: 'KICK-001', name: 'Step 1', status: 'approved', canApprove: false }] },
            { id: 'spec', name: 'Spec', status: 'active', steps: [{ id: 'SPEC-001', name: 'Step 1', status: 'pending', canApprove: true }] },
            { id: 'demo', name: 'Demo', status: 'blocked', steps: [] }
          ]
        }],
        config: { version: '1.0.0', autoSave: true }
      }
    })

    it('should set current phase index', () => {
      phaseStore.setCurrentPhase(1)
      expect(phaseStore.currentPhaseIndex).toBe(1)
    })

    it('should select first step of phase', () => {
      phaseStore.setCurrentPhase(1)
      expect(phaseStore.currentStepId).toBe('SPEC-001')
    })

    it('should not set blocked phase', () => {
      phaseStore.setCurrentPhase(2) // blocked phase
      expect(phaseStore.currentPhaseIndex).toBe(0) // stays at 0
    })
  })

  describe('setCurrentStep', () => {
    it('should set currentStepId', () => {
      phaseStore.setCurrentStep('KICK-001')
      expect(phaseStore.currentStepId).toBe('KICK-001')
    })
  })

  describe('approveStep', () => {
    beforeEach(() => {
      projectStore.currentProject = {
        id: '/test/project',
        name: 'Test',
        path: '/test/project',
        activeFeatureId: 'feature1',
        features: [{
          id: 'feature1',
          name: 'Feature 1',
          path: '/path',
          currentPhase: 1,
          phases: [
            { id: 'kickoff', name: 'Kickoff', status: 'active', steps: [{ id: 'KICK-001', name: 'Step 1', status: 'generated', canApprove: true }] }
          ]
        }],
        config: { version: '1.0.0', autoSave: true }
      }
    })

    it('should submit approval successfully', async () => {
      mockInvoke
        .mockResolvedValueOnce({ success: true, stepId: 'KICK-001', newStatus: 'approved' })
        .mockResolvedValueOnce({ project: projectStore.currentProject })

      const result = await phaseStore.approveStep('KICK-001', 'approve', 'LGTM')

      expect(result).toBe(true)
      expect(mockInvoke).toHaveBeenCalledWith('approval:submit', {
        stepId: 'KICK-001',
        featureId: 'feature1',
        action: 'approve',
        note: 'LGTM'
      })
    })

    it('should set approvingStepId during approval', async () => {
      let approvingDuringCall = false
      mockInvoke.mockImplementation(() => {
        approvingDuringCall = phaseStore.approvingStepId === 'KICK-001'
        return Promise.resolve({ success: true })
      })

      await phaseStore.approveStep('KICK-001', 'approve')

      expect(approvingDuringCall).toBe(true)
      expect(phaseStore.approvingStepId).toBeNull() // cleared after
    })

    it('should set approvalError on failure', async () => {
      mockInvoke.mockRejectedValue(new Error('Permission denied'))

      const result = await phaseStore.approveStep('KICK-001', 'approve')

      expect(result).toBe(false)
      expect(phaseStore.approvalError).toBe('Permission denied')
    })

    it('should return false when no active feature', async () => {
      projectStore.currentProject = null

      const result = await phaseStore.approveStep('KICK-001', 'approve')

      expect(result).toBe(false)
      expect(phaseStore.approvalError).toBe('No active feature')
    })
  })

  describe('canApproveStep', () => {
    it('should return true for generated step with canApprove', () => {
      const step = { id: 'KICK-001', name: 'Step', status: 'generated' as const, canApprove: true }
      expect(phaseStore.canApproveStep(step)).toBe(true)
    })

    it('should return false for pending step', () => {
      const step = { id: 'KICK-001', name: 'Step', status: 'pending' as const, canApprove: true }
      expect(phaseStore.canApproveStep(step)).toBe(false)
    })

    it('should return false when canApprove is false', () => {
      const step = { id: 'KICK-001', name: 'Step', status: 'generated' as const, canApprove: false }
      expect(phaseStore.canApproveStep(step)).toBe(false)
    })
  })

  describe('isStepLocked', () => {
    beforeEach(() => {
      projectStore.currentProject = {
        id: '/test/project',
        name: 'Test',
        path: '/test/project',
        activeFeatureId: 'feature1',
        features: [{
          id: 'feature1',
          name: 'Feature 1',
          path: '/path',
          currentPhase: 1,
          phases: [
            {
              id: 'kickoff',
              name: 'Kickoff',
              status: 'active',
              steps: [
                { id: 'KICK-001', name: 'Step 1', status: 'approved', canApprove: false },
                { id: 'KICK-002', name: 'Step 2', status: 'generated', canApprove: true },
                { id: 'KICK-003', name: 'Step 3', status: 'pending', canApprove: true }
              ]
            },
            {
              id: 'spec',
              name: 'Spec',
              status: 'blocked',
              steps: [{ id: 'SPEC-001', name: 'Step 1', status: 'pending', canApprove: true }]
            }
          ]
        }],
        config: { version: '1.0.0', autoSave: true }
      }
    })

    it('should return false for first step', () => {
      const step = phaseStore.phases[0].steps[0]
      expect(phaseStore.isStepLocked(step, 0)).toBe(false)
    })

    it('should return false for step after approved step', () => {
      const step = phaseStore.phases[0].steps[1]
      expect(phaseStore.isStepLocked(step, 0)).toBe(false)
    })

    it('should return true for step after non-approved step', () => {
      const step = phaseStore.phases[0].steps[2]
      expect(phaseStore.isStepLocked(step, 0)).toBe(true)
    })

    it('should return true for all steps in blocked phase', () => {
      const step = phaseStore.phases[1].steps[0]
      expect(phaseStore.isStepLocked(step, 1)).toBe(true)
    })
  })

  describe('updateStepStatus', () => {
    it('should update step status locally', () => {
      projectStore.currentProject = {
        id: '/test/project',
        name: 'Test',
        path: '/test/project',
        activeFeatureId: 'feature1',
        features: [{
          id: 'feature1',
          name: 'Feature 1',
          path: '/path',
          currentPhase: 1,
          phases: [
            { id: 'kickoff', name: 'Kickoff', status: 'active', steps: [{ id: 'KICK-001', name: 'Step 1', status: 'pending', canApprove: true }] }
          ]
        }],
        config: { version: '1.0.0', autoSave: true }
      }

      phaseStore.updateStepStatus(0, 'KICK-001', 'running')

      expect(phaseStore.phases[0].steps[0].status).toBe('running')
    })
  })

  describe('reset', () => {
    it('should reset all state', () => {
      phaseStore.currentPhaseIndex = 5
      phaseStore.currentStepId = 'KICK-001'
      phaseStore.approvingStepId = 'KICK-002'
      phaseStore.approvalError = 'some error'

      phaseStore.reset()

      expect(phaseStore.currentPhaseIndex).toBe(0)
      expect(phaseStore.currentStepId).toBeNull()
      expect(phaseStore.approvingStepId).toBeNull()
      expect(phaseStore.approvalError).toBeNull()
    })
  })
})
