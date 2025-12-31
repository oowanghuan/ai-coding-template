/**
 * Renderer 类型定义
 * 重新导出共享类型并定义 UI 专用类型
 */

// 重新导出共享类型
export type {
  StepStatus,
  PhaseStatus,
  Artifact,
  Interaction,
  PreflightCheck,
  Step,
  Phase,
  Feature,
  Project,
  ProjectConfig,
  PhaseGateStatus
} from '@shared/types/project.types'

import type { StepStatus, Artifact, Interaction } from '@shared/types/project.types'

/** Step 卡片组件 Props */
export interface StepCardProps {
  stepId: string
  stepNumber: number
  title: string
  status: StepStatus
  interactions: Array<{ actor: 'human' | 'ai'; action: string }>
  artifacts: Array<{
    path: string
    status: 'pending' | 'generated' | 'verified'
    canPreview: boolean
  }>
  isLocked: boolean
  logs: Array<{ timestamp: string; type: string; message: string }>
  isLogExpanded: boolean
}

/** Log 抽屉组件 Props */
export interface LogDrawerProps {
  logs: Array<{ timestamp: string; type: string; message: string }>
  stepId: string
}

/** 日志条目类型 */
export interface LogEntry {
  id: string
  timestamp: string
  type: 'command' | 'output' | 'error' | 'info'
  message: string
  source?: string
}
