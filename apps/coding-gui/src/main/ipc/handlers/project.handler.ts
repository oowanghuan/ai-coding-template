/**
 * 项目相关 IPC 处理器
 * CODE-003: project:open, project:state
 */

import { readFile, stat } from 'fs/promises'
import { join } from 'path'
import { parse as parseYaml } from 'yaml'
import type {
  ProjectOpenRequest,
  ProjectOpenResponse,
  ProjectStateResponse
} from '../../../shared/types/ipc.types'
import type { Project, Feature, Phase, Step, ProjectConfig } from '../../../shared/types/project.types'
import { ERROR_CODES, createError } from '../../../shared/types/error.types'
import { featureRegistry, getVisibleFeatures, type FeatureRegistryEntry } from '../../../shared/config/feature-registry'

// 当前打开的项目缓存
let currentProject: Project | null = null

/**
 * 打开项目
 */
export async function handleProjectOpen(
  request: ProjectOpenRequest
): Promise<ProjectOpenResponse> {
  const projectPath = request.path

  try {
    // 验证项目目录存在
    const projectStat = await stat(projectPath)
    if (!projectStat.isDirectory()) {
      throw createError(
        ERROR_CODES.FS_NOT_FOUND,
        `Path is not a directory: ${projectPath}`
      )
    }

    // 检查 .claude 目录
    const claudeDir = join(projectPath, '.claude')
    try {
      await stat(claudeDir)
    } catch {
      throw createError(
        ERROR_CODES.CFG_MISSING,
        `Not a valid Claude Code project: .claude directory not found`
      )
    }

    // 读取项目配置
    const config = await loadProjectConfig(projectPath)

    // 从 registry 加载 features
    const features = await loadFeaturesFromRegistry(projectPath)

    // 构建项目对象
    const project: Project = {
      id: projectPath, // 使用路径作为 ID
      name: projectPath.split('/').pop() || 'Unknown',
      path: projectPath,
      features,
      activeFeatureId: features.length > 0 ? features[0].id : undefined,
      config
    }

    currentProject = project

    return { project }

  } catch (error) {
    if ((error as { code?: string }).code?.startsWith('E-')) {
      throw error
    }
    throw createError(
      ERROR_CODES.FS_READ_FAILED,
      `Failed to open project: ${(error as Error).message}`,
      { path: projectPath }
    )
  }
}

/**
 * 获取项目状态
 */
export async function handleProjectState(): Promise<ProjectStateResponse> {
  if (!currentProject) {
    throw createError(
      ERROR_CODES.CFG_MISSING,
      'No project is currently open'
    )
  }

  // 从 registry 加载 features 获取最新状态
  const features = await loadFeaturesFromRegistry(currentProject.path)
  currentProject.features = features

  const activeFeature = currentProject.activeFeatureId
    ? features.find(f => f.id === currentProject!.activeFeatureId)
    : features[0]

  return {
    project: currentProject,
    features,
    activeFeature
  }
}

/**
 * 加载项目配置
 */
async function loadProjectConfig(projectPath: string): Promise<ProjectConfig> {
  const configPath = join(projectPath, '.claude', 'config', 'project.yaml')

  try {
    const content = await readFile(configPath, 'utf-8')
    const parsed = parseYaml(content)
    return {
      version: parsed.version || '1.0.0',
      claudeCodePath: parsed.claude_code_path,
      defaultModel: parsed.default_model,
      autoSave: parsed.auto_save ?? true
    }
  } catch {
    // 返回默认配置
    return {
      version: '1.0.0',
      autoSave: true
    }
  }
}

/**
 * 从 Registry 加载 features（不扫描目录）
 * 使用 Registry 方式确保 feature 不会因文件误删而丢失
 */
async function loadFeaturesFromRegistry(projectPath: string, includeArchived = false): Promise<Feature[]> {
  const registryEntries = includeArchived ? featureRegistry : getVisibleFeatures()
  const features: Feature[] = []

  for (const entry of registryEntries) {
    const feature = await loadFeatureFromRegistry(projectPath, entry)
    features.push(feature)
  }

  return features
}

/**
 * 从 Registry entry 加载单个 feature
 * 即使 progress log 不存在，也返回基本的 feature 信息
 */
async function loadFeatureFromRegistry(projectPath: string, entry: FeatureRegistryEntry): Promise<Feature> {
  const featurePath = join(projectPath, entry.docsPath)
  const progressLogPath = join(featurePath, entry.progressLogFile)

  try {
    const content = await readFile(progressLogPath, 'utf-8')
    const parsed = parseYaml(content)

    const phases = buildPhasesFromProgressLog(parsed)

    return {
      id: entry.id,
      name: entry.name,
      path: featurePath,
      description: entry.description || parsed.meta?.description,
      phases,
      currentPhase: parsed.meta?.current_phase || 1,
      createdAt: parsed.meta?.started_at || new Date().toISOString(),
      updatedAt: parsed.meta?.last_updated || new Date().toISOString()
    }
  } catch {
    // Progress log 不存在时，返回 registry 中的基本信息
    return {
      id: entry.id,
      name: entry.name,
      path: featurePath,
      description: entry.description,
      phases: buildDefaultPhases(),
      currentPhase: 1,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
  }
}

/**
 * 构建默认的 phases（当 progress log 不存在时）
 */
function buildDefaultPhases(): Phase[] {
  const phaseNames = [
    { id: 'kickoff', name: 'Kickoff' },
    { id: 'spec', name: 'Spec' },
    { id: 'demo', name: 'Demo' },
    { id: 'design', name: 'Design' },
    { id: 'code', name: 'Code' },
    { id: 'test', name: 'Test' },
    { id: 'deploy', name: 'Deploy' }
  ]

  return phaseNames.map((phase, index) => ({
    id: phase.id,
    name: phase.name,
    description: `Phase ${index + 1}`,
    status: 'pending' as Phase['status'],
    steps: [],
    gateStatus: 'open' as const
  }))
}

/**
 * 从 progress log 构建 phases
 */
function buildPhasesFromProgressLog(progressLog: Record<string, unknown>): Phase[] {
  const phaseNames = [
    { key: 'phase_1_kickoff', name: 'Kickoff', id: 'kickoff' },
    { key: 'phase_2_spec', name: 'Spec', id: 'spec' },
    { key: 'phase_3_demo', name: 'Demo', id: 'demo' },
    { key: 'phase_4_design', name: 'Design', id: 'design' },
    { key: 'phase_5_code', name: 'Code', id: 'code' },
    { key: 'phase_6_test', name: 'Test', id: 'test' },
    { key: 'phase_7_deploy', name: 'Deploy', id: 'deploy' }
  ]

  return phaseNames.map((phase, index) => {
    const phaseData = progressLog[phase.key] as Record<string, unknown> | undefined
    const status = phaseData?.status as string || 'pending'
    const tasks = (phaseData?.tasks || []) as Array<Record<string, unknown>>

    const steps: Step[] = tasks.map(task => ({
      id: task.id as string,
      name: task.task as string,
      description: task.notes as string || '',
      status: mapTaskStatus(task.status as string),
      artifacts: [],
      interactions: [],
      preflightChecks: [],
      command: task.command as string | undefined,
      canApprove: task.status === 'done',
      canRollback: false
    }))

    return {
      id: phase.id,
      name: phase.name,
      description: `Phase ${index + 1}`,
      status: mapPhaseStatus(status),
      steps,
      gateStatus: phaseData?.gate_passed ? 'passed' : 'open'
    }
  })
}

function mapTaskStatus(status: string): Step['status'] {
  switch (status) {
    case 'done': return 'generated'
    case 'wip': return 'running'
    case 'pending': return 'pending'
    case 'failed': return 'failed'
    case 'skipped': return 'skipped'
    default: return 'pending'
  }
}

function mapPhaseStatus(status: string): Phase['status'] {
  switch (status) {
    case 'done': return 'completed'
    case 'wip': return 'active'
    case 'pending': return 'pending'
    case 'blocked': return 'blocked'
    case 'skipped': return 'skipped'
    default: return 'pending'
  }
}

/**
 * 获取当前项目
 */
export function getCurrentProject(): Project | null {
  return currentProject
}

/**
 * 设置当前项目（用于测试）
 */
export function setCurrentProject(project: Project | null): void {
  currentProject = project
}
