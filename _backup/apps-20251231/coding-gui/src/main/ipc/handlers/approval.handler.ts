/**
 * 审批相关 IPC 处理器
 * CODE-003 & CODE-009: approval:submit, approval:status
 */

import { readFile, writeFile, appendFile, mkdir } from 'fs/promises'
import { join, dirname } from 'path'
import { parse as parseYaml, stringify as stringifyYaml } from 'yaml'
import { execSync } from 'child_process'
import { hostname } from 'os'
import type {
  ApprovalSubmitRequest,
  ApprovalSubmitResponse,
  ApprovalStatusRequest,
  ApprovalStatusResponse
} from '../../../shared/types/ipc.types'
import type { PhaseGateStatus } from '../../../shared/types/project.types'
import { ERROR_CODES, createError } from '../../../shared/types/error.types'
import { getCurrentProject } from './project.handler'

// 审批日志格式
interface ApprovalLogEntry {
  step_id: string
  approved_by: string
  approved_at: string
  source: 'gui' | 'cli' | 'api'
  action: 'approve' | 'reject'
  note?: string
  client_info: {
    app_version: string
    hostname: string
  }
}

// 应用版本
const APP_VERSION = '1.0.0'

/**
 * 获取当前用户身份
 * 从 Git config 或环境变量获取
 */
function getCurrentUserIdentity(): string {
  try {
    // 尝试从 Git config 获取
    const email = execSync('git config user.email', { encoding: 'utf-8' }).trim()
    if (email) return email
  } catch {
    // 忽略错误
  }

  // 尝试从环境变量获取
  if (process.env.USER_EMAIL) {
    return process.env.USER_EMAIL
  }

  // 使用系统用户名
  return process.env.USER || process.env.USERNAME || 'unknown'
}

/**
 * 提交审批
 */
export async function handleApprovalSubmit(
  request: ApprovalSubmitRequest
): Promise<ApprovalSubmitResponse> {
  const project = getCurrentProject()
  if (!project) {
    throw createError(
      ERROR_CODES.CFG_MISSING,
      'No project is currently open'
    )
  }

  const { stepId, featureId, action, note } = request
  const approvedBy = getCurrentUserIdentity()
  const approvedAt = new Date().toISOString()

  // 找到对应的 feature 路径
  const feature = project.features.find(f => f.id === featureId)
  if (!feature) {
    throw createError(
      ERROR_CODES.FS_NOT_FOUND,
      `Feature not found: ${featureId}`
    )
  }

  try {
    // 1. 更新 PHASE_GATE_STATUS.yaml
    await updatePhaseGateStatus(feature.path, stepId, action, approvedBy, approvedAt)

    // 2. 记录审批日志
    await appendApprovalLog(project.path, {
      step_id: stepId,
      approved_by: approvedBy,
      approved_at: approvedAt,
      source: 'gui',
      action,
      note,
      client_info: {
        app_version: APP_VERSION,
        hostname: hostname()
      }
    })

    return {
      success: true,
      stepId,
      newStatus: action === 'approve' ? 'approved' : 'rejected',
      approvedBy,
      approvedAt
    }

  } catch (error) {
    if ((error as { code?: string }).code?.startsWith('E-')) {
      throw error
    }
    throw createError(
      ERROR_CODES.FS_WRITE_FAILED,
      `Failed to submit approval: ${(error as Error).message}`,
      { stepId, featureId }
    )
  }
}

/**
 * 查询审批状态
 */
export async function handleApprovalStatus(
  request: ApprovalStatusRequest
): Promise<ApprovalStatusResponse> {
  const project = getCurrentProject()
  if (!project) {
    throw createError(
      ERROR_CODES.CFG_MISSING,
      'No project is currently open'
    )
  }

  const feature = project.features.find(f => f.id === request.featureId)
  if (!feature) {
    throw createError(
      ERROR_CODES.FS_NOT_FOUND,
      `Feature not found: ${request.featureId}`
    )
  }

  try {
    const gateStatusPath = join(feature.path, 'PHASE_GATE_STATUS.yaml')
    const content = await readFile(gateStatusPath, 'utf-8')
    const parsed = parseYaml(content) as Record<string, unknown>

    // 解析 gates
    const gates: PhaseGateStatus[] = []
    const steps: ApprovalStatusResponse['steps'] = []

    if (parsed.phases && typeof parsed.phases === 'object') {
      for (const [phase, data] of Object.entries(parsed.phases as Record<string, unknown>)) {
        const phaseData = data as Record<string, unknown>
        const phaseNum = parseInt(phase.replace('phase_', ''), 10)

        gates.push({
          phase: phaseNum,
          status: phaseData.gate_passed ? 'passed' : 'pending',
          approvedBy: phaseData.approved_by as string | undefined,
          approvedAt: phaseData.approved_at as string | undefined,
          source: phaseData.source as 'gui' | 'cli' | 'api' | undefined
        })

        // 解析 steps
        if (phaseData.steps && typeof phaseData.steps === 'object') {
          for (const [stepId, stepData] of Object.entries(phaseData.steps as Record<string, unknown>)) {
            const step = stepData as Record<string, unknown>
            steps.push({
              stepId,
              status: step.status as 'approved' | 'rejected' | 'pending',
              approvedBy: step.approved_by as string | undefined,
              approvedAt: step.approved_at as string | undefined
            })
          }
        }
      }
    }

    return { gates, steps }

  } catch (error) {
    // 文件不存在时返回空状态
    if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
      return { gates: [], steps: [] }
    }
    throw createError(
      ERROR_CODES.FS_READ_FAILED,
      `Failed to read approval status: ${(error as Error).message}`,
      { featureId: request.featureId }
    )
  }
}

/**
 * 更新 PHASE_GATE_STATUS.yaml
 * 注意：只有 ApprovalService 可以写入此文件
 */
async function updatePhaseGateStatus(
  featurePath: string,
  stepId: string,
  action: 'approve' | 'reject',
  approvedBy: string,
  approvedAt: string
): Promise<void> {
  const gateStatusPath = join(featurePath, 'PHASE_GATE_STATUS.yaml')

  let content: Record<string, unknown> = {}

  try {
    const existing = await readFile(gateStatusPath, 'utf-8')
    content = parseYaml(existing) as Record<string, unknown>
  } catch {
    // 文件不存在，创建新的
  }

  // 初始化结构
  if (!content.phases) {
    content.phases = {}
  }

  // 从 stepId 解析 phase（假设格式为 PHASE-STEP，如 KICK-001）
  const stepPrefix = stepId.split('-')[0]?.toUpperCase()
  const phaseMap: Record<string, string> = {
    'KICK': 'phase_1',
    'SPEC': 'phase_2',
    'DEMO': 'phase_3',
    'DSGN': 'phase_4',
    'CODE': 'phase_5',
    'TEST': 'phase_6',
    'DEPL': 'phase_7'
  }
  const phaseKey = phaseMap[stepPrefix] || 'phase_1'

  const phases = content.phases as Record<string, unknown>
  if (!phases[phaseKey]) {
    phases[phaseKey] = { steps: {} }
  }

  const phaseData = phases[phaseKey] as Record<string, unknown>
  if (!phaseData.steps) {
    phaseData.steps = {}
  }

  const steps = phaseData.steps as Record<string, unknown>
  steps[stepId] = {
    status: action === 'approve' ? 'approved' : 'rejected',
    approved_by: approvedBy,
    approved_at: approvedAt,
    source: 'gui'
  }

  // 更新 last_updated
  content.last_updated = approvedAt

  // 写入文件
  await writeFile(gateStatusPath, stringifyYaml(content), 'utf-8')
}

/**
 * 追加审批日志
 */
async function appendApprovalLog(
  projectPath: string,
  entry: ApprovalLogEntry
): Promise<void> {
  const logDir = join(projectPath, '.claude', 'state')
  const logPath = join(logDir, 'approval_log.jsonl')

  // 确保目录存在
  await mkdir(logDir, { recursive: true })

  // 追加日志条目
  const line = JSON.stringify(entry) + '\n'
  await appendFile(logPath, line, 'utf-8')
}
