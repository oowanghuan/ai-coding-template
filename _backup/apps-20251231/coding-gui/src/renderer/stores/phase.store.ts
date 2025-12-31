/**
 * Phase/Step 状态管理
 * CODE-004: phaseStore - Phase/Step 状态、执行状态
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Phase, Step, StepStatus } from '@shared/types/project.types'
import type { ApprovalSubmitRequest, ApprovalSubmitResponse } from '@shared/types/ipc.types'
import { useProjectStore } from './project.store'

export const usePhaseStore = defineStore('phase', () => {
  // ============================================================
  // State
  // ============================================================

  /** 当前选中的 Phase 索引 */
  const currentPhaseIndex = ref(0)

  /** 当前选中的 Step ID */
  const currentStepId = ref<string | null>(null)

  /** 审批中的 Step */
  const approvingStepId = ref<string | null>(null)

  /** 审批错误 */
  const approvalError = ref<string | null>(null)

  // ============================================================
  // Getters
  // ============================================================

  const projectStore = useProjectStore()

  /** 所有 Phases */
  const phases = computed<Phase[]>(() => {
    return projectStore.activeFeature?.phases || []
  })

  /** 当前 Phase */
  const currentPhase = computed<Phase | undefined>(() => {
    return phases.value[currentPhaseIndex.value]
  })

  /** 当前 Phase 的 Steps */
  const currentSteps = computed<Step[]>(() => {
    return currentPhase.value?.steps || []
  })

  /** 当前选中的 Step */
  const currentStep = computed<Step | undefined>(() => {
    if (!currentStepId.value) return undefined
    return currentSteps.value.find(s => s.id === currentStepId.value)
  })

  /** Phase 是否可访问 */
  const isPhaseAccessible = (index: number): boolean => {
    const phase = phases.value[index]
    if (!phase) return false
    return phase.status !== 'blocked'
  }

  // ============================================================
  // Actions
  // ============================================================

  /**
   * 设置当前 Phase
   */
  function setCurrentPhase(index: number): void {
    if (isPhaseAccessible(index)) {
      currentPhaseIndex.value = index
      // 选择第一个 Step
      const steps = phases.value[index]?.steps || []
      currentStepId.value = steps.length > 0 ? steps[0].id : null
    }
  }

  /**
   * 设置当前 Step
   */
  function setCurrentStep(stepId: string): void {
    currentStepId.value = stepId
  }

  /**
   * 审批 Step
   */
  async function approveStep(
    stepId: string,
    action: 'approve' | 'reject',
    note?: string
  ): Promise<boolean> {
    const featureId = projectStore.activeFeature?.id
    if (!featureId) {
      approvalError.value = 'No active feature'
      return false
    }

    approvingStepId.value = stepId
    approvalError.value = null

    try {
      const request: ApprovalSubmitRequest = {
        stepId,
        featureId,
        action,
        note
      }

      const response = await window.electronAPI.invoke<ApprovalSubmitResponse>(
        'approval:submit',
        request
      )

      if (response.success) {
        // 刷新项目状态以获取最新数据
        await projectStore.refreshState()
        return true
      }

      return false
    } catch (e) {
      approvalError.value = (e as Error).message
      return false
    } finally {
      approvingStepId.value = null
    }
  }

  /**
   * 更新 Step 状态（本地）
   */
  function updateStepStatus(phaseIndex: number, stepId: string, status: StepStatus): void {
    const phase = phases.value[phaseIndex]
    if (!phase) return

    const step = phase.steps.find(s => s.id === stepId)
    if (step) {
      step.status = status
    }
  }

  /**
   * 检查 Step 是否可审批
   */
  function canApproveStep(step: Step): boolean {
    return step.status === 'generated' && step.canApprove
  }

  /**
   * 检查 Step 是否已锁定
   */
  function isStepLocked(step: Step, phaseIndex: number): boolean {
    // 如果 Phase 被阻断，所有 Step 都锁定
    const phase = phases.value[phaseIndex]
    if (phase?.status === 'blocked') return true

    // 检查前置 Step 是否都已完成
    const steps = phase?.steps || []
    const stepIndex = steps.findIndex(s => s.id === step.id)

    for (let i = 0; i < stepIndex; i++) {
      const prevStep = steps[i]
      if (prevStep.status !== 'approved' && prevStep.status !== 'skipped') {
        return true
      }
    }

    return false
  }

  /**
   * 清除审批错误
   */
  function clearApprovalError(): void {
    approvalError.value = null
  }

  /**
   * 重置状态
   */
  function reset(): void {
    currentPhaseIndex.value = 0
    currentStepId.value = null
    approvingStepId.value = null
    approvalError.value = null
  }

  return {
    // State
    currentPhaseIndex,
    currentStepId,
    approvingStepId,
    approvalError,

    // Getters
    phases,
    currentPhase,
    currentSteps,
    currentStep,
    isPhaseAccessible,

    // Actions
    setCurrentPhase,
    setCurrentStep,
    approveStep,
    updateStepStatus,
    canApproveStep,
    isStepLocked,
    clearApprovalError,
    reset
  }
})
