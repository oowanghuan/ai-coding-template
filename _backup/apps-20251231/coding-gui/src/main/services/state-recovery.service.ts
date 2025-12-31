/**
 * 状态恢复服务
 * CODE-007: StateRecoveryService + 推断算法
 *
 * 关键约束（DESIGN 1.3 节）：
 * - 任何情况不自动恢复 approved 状态
 * - 状态推断基于 Artifact 存在性
 */

import { readFile, stat, readdir } from 'fs/promises'
import { join } from 'path'
import { parse as parseYaml } from 'yaml'
import { EventEmitter } from 'events'
import type { Step, StepStatus, Feature, Phase } from '../../shared/types/project.types'
import { projectStateCacheService } from './project-state-cache.service'

/** 推断结果 */
interface InferredStepStatus {
  stepId: string
  status: StepStatus
  confidence: 'high' | 'medium' | 'low'
  reason: string
  artifacts: Array<{ path: string; exists: boolean; valid: boolean }>
}

/** 恢复结果 */
interface RecoveryResult {
  success: boolean
  featureId: string
  recoveredSteps: InferredStepStatus[]
  conflicts: ConflictResolution[]
  duration: number
}

/** 冲突解决 */
interface ConflictResolution {
  stepId: string
  type: 'state_mismatch' | 'artifact_conflict' | 'log_inconsistent'
  description: string
  resolution: 'use_inferred' | 'use_logged' | 'manual_required'
  resolvedStatus?: StepStatus
}

/**
 * 状态恢复服务（单例）
 */
class StateRecoveryService extends EventEmitter {
  private static instance: StateRecoveryService | null = null

  private constructor() {
    super()
  }

  static getInstance(): StateRecoveryService {
    if (!StateRecoveryService.instance) {
      StateRecoveryService.instance = new StateRecoveryService()
    }
    return StateRecoveryService.instance
  }

  /**
   * 重建项目状态
   */
  async rebuildState(projectPath: string, featureId: string): Promise<RecoveryResult> {
    const startTime = Date.now()
    const featurePath = join(projectPath, 'docs', featureId)

    const recoveredSteps: InferredStepStatus[] = []
    const conflicts: ConflictResolution[] = []

    try {
      // 1. 读取 PROGRESS_LOG
      const progressLog = await this.readProgressLog(featurePath)

      // 2. 读取 PHASE_GATE_STATUS（用于对比）
      const gateStatus = await this.readGateStatus(featurePath)

      // 3. 对每个 Phase 的 Step 进行状态推断
      for (const [phaseKey, phaseData] of Object.entries(progressLog)) {
        if (!phaseKey.startsWith('phase_')) continue

        const tasks = (phaseData as Record<string, unknown>).tasks as Array<Record<string, unknown>> || []

        for (const task of tasks) {
          const stepId = task.id as string
          const loggedStatus = task.status as string

          // 推断状态
          const inferred = await this.inferStepStatus(featurePath, stepId, task)

          // 检查冲突
          if (inferred.status !== this.mapLoggedStatus(loggedStatus)) {
            // 状态不一致，需要解决
            const conflict = this.resolveConflict(stepId, loggedStatus, inferred)
            conflicts.push(conflict)

            // 应用解决方案
            if (conflict.resolvedStatus) {
              inferred.status = conflict.resolvedStatus
            }
          }

          // 关键约束：不自动恢复 approved 状态
          if (inferred.status === 'approved') {
            inferred.status = 'generated'
            inferred.reason = 'approved status not auto-recovered (requires manual re-approval)'
            inferred.confidence = 'high'
          }

          recoveredSteps.push(inferred)
        }
      }

      // 4. 同步到缓存
      await this.syncToCache(projectPath, featureId)

      const duration = Date.now() - startTime

      this.emit('recovery-complete', { featureId, recoveredSteps, conflicts, duration })

      return {
        success: true,
        featureId,
        recoveredSteps,
        conflicts,
        duration
      }

    } catch (error) {
      this.emit('recovery-failed', { featureId, error })

      return {
        success: false,
        featureId,
        recoveredSteps: [],
        conflicts: [],
        duration: Date.now() - startTime
      }
    }
  }

  /**
   * 推断 Step 状态
   */
  async inferStepStatus(
    featurePath: string,
    stepId: string,
    taskDef: Record<string, unknown>
  ): Promise<InferredStepStatus> {
    const artifacts: Array<{ path: string; exists: boolean; valid: boolean }> = []

    // 获取预期的 artifacts
    const expectedArtifacts = this.getExpectedArtifacts(stepId, featurePath)

    let existingCount = 0
    let validCount = 0

    for (const artifactPath of expectedArtifacts) {
      const exists = await this.fileExists(artifactPath)
      const valid = exists ? await this.validateArtifact(artifactPath) : false

      artifacts.push({ path: artifactPath, exists, valid })

      if (exists) existingCount++
      if (valid) validCount++
    }

    // 推断规则（DESIGN 9.3.2 节）
    let status: StepStatus
    let confidence: 'high' | 'medium' | 'low'
    let reason: string

    if (expectedArtifacts.length === 0) {
      // 无预期 artifacts，使用日志状态
      status = this.mapLoggedStatus(taskDef.status as string)
      confidence = 'low'
      reason = 'No expected artifacts, using logged status'
    } else if (validCount === expectedArtifacts.length) {
      // 所有 artifacts 存在且有效 → generated
      status = 'generated'
      confidence = 'high'
      reason = 'All artifacts exist and are valid'
    } else if (existingCount > 0 && existingCount < expectedArtifacts.length) {
      // 部分 artifacts 存在 → failed
      status = 'failed'
      confidence = 'medium'
      reason = `Partial artifacts: ${existingCount}/${expectedArtifacts.length}`
    } else if (existingCount === 0) {
      // 无 artifacts → pending
      status = 'pending'
      confidence = 'high'
      reason = 'No artifacts found'
    } else {
      // 有 artifacts 但部分无效 → failed
      status = 'failed'
      confidence = 'medium'
      reason = `Invalid artifacts: ${existingCount - validCount}/${existingCount}`
    }

    return {
      stepId,
      status,
      confidence,
      reason,
      artifacts
    }
  }

  /**
   * 解决冲突
   */
  resolveConflicts(featureId: string): ConflictResolution[] {
    // 目前返回空数组，实际冲突在 rebuildState 中处理
    return []
  }

  /**
   * 同步到缓存
   */
  async syncToCache(projectPath: string, featureId: string): Promise<void> {
    await projectStateCacheService.invalidate(projectPath)
    await projectStateCacheService.refresh(projectPath)
  }

  /**
   * 使缓存失效
   */
  async invalidateCache(projectPath: string): Promise<void> {
    projectStateCacheService.invalidate(projectPath)
  }

  // ============================================================
  // 私有方法
  // ============================================================

  private async readProgressLog(featurePath: string): Promise<Record<string, unknown>> {
    const logPath = join(featurePath, '90_PROGRESS_LOG.yaml')
    try {
      const content = await readFile(logPath, 'utf-8')
      return parseYaml(content) as Record<string, unknown>
    } catch {
      return {}
    }
  }

  private async readGateStatus(featurePath: string): Promise<Record<string, unknown>> {
    const statusPath = join(featurePath, 'PHASE_GATE_STATUS.yaml')
    try {
      const content = await readFile(statusPath, 'utf-8')
      return parseYaml(content) as Record<string, unknown>
    } catch {
      return {}
    }
  }

  private getExpectedArtifacts(stepId: string, featurePath: string): string[] {
    // 根据 stepId 前缀确定预期 artifacts
    const prefix = stepId.split('-')[0]?.toUpperCase()

    const artifactMap: Record<string, string[]> = {
      'KICK': ['10_CONTEXT.md', '90_PROGRESS_LOG.yaml'],
      'SPEC': ['21_UI_FLOW_SPEC.md', '20_API_SPEC.md'],
      'DEMO': [], // Demo artifacts 在 demos/ 目录
      'DSGN': ['40_DESIGN_FINAL.md'],
      'CODE': ['50_DEV_PLAN.md'],
      'TEST': ['60_TEST_PLAN.md'],
      'DEPL': ['70_DEPLOY_CHECKLIST.md']
    }

    const relativePaths = artifactMap[prefix] || []
    return relativePaths.map(p => join(featurePath, p))
  }

  private async fileExists(path: string): Promise<boolean> {
    try {
      await stat(path)
      return true
    } catch {
      return false
    }
  }

  private async validateArtifact(path: string): Promise<boolean> {
    try {
      const content = await readFile(path, 'utf-8')
      // 基本验证：文件不为空且至少有 10 个字符
      return content.trim().length >= 10
    } catch {
      return false
    }
  }

  private mapLoggedStatus(status: string): StepStatus {
    const statusMap: Record<string, StepStatus> = {
      'done': 'generated',
      'wip': 'running',
      'pending': 'pending',
      'failed': 'failed',
      'skipped': 'skipped'
    }
    return statusMap[status] || 'pending'
  }

  private resolveConflict(
    stepId: string,
    loggedStatus: string,
    inferred: InferredStepStatus
  ): ConflictResolution {
    // 如果推断置信度高，使用推断结果
    if (inferred.confidence === 'high') {
      return {
        stepId,
        type: 'state_mismatch',
        description: `Logged: ${loggedStatus}, Inferred: ${inferred.status}`,
        resolution: 'use_inferred',
        resolvedStatus: inferred.status
      }
    }

    // 否则使用日志状态
    return {
      stepId,
      type: 'state_mismatch',
      description: `Logged: ${loggedStatus}, Inferred: ${inferred.status}`,
      resolution: 'use_logged',
      resolvedStatus: this.mapLoggedStatus(loggedStatus)
    }
  }
}

export const stateRecoveryService = StateRecoveryService.getInstance()
export { StateRecoveryService, InferredStepStatus, RecoveryResult, ConflictResolution }
