/**
 * ExecutionEngine 服务
 * 构建执行清单、管理执行流程
 * 基于 WORKFLOW_CONFIG_SYSTEM_DESIGN.md v1.1 第 5 章
 */

import { configLoader } from './configLoader'
import {
  computeFrameworkStepStatus,
  mapTaskStatus,
  areAllTasksCompleted,
  canExecute,
  type PrerequisiteContext,
} from '../utils/executionStatus'
import type {
  ExecutionItem,
  ExecutionStatus,
  FrameworkStep,
  FeatureTask,
  PhaseGateStatus,
  RerunPolicy,
} from '../types/workflow.types'

// ============================================================
// ExecutionEngine 类
// ============================================================

class ExecutionEngine {
  /**
   * 构建执行清单
   * 合并框架步骤和 Feature 任务
   */
  async buildExecutionList(
    phaseId: number,
    featureId: string
  ): Promise<ExecutionItem[]> {
    // 1. 加载配置
    const [phaseConfig, frameworkSteps, featureTasks, gateStatus] = await Promise.all([
      configLoader.loadPhaseConfig(phaseId, featureId),
      configLoader.getFrameworkSteps(phaseId),
      configLoader.loadFeatureTasks(featureId, phaseId),
      configLoader.loadGateStatus(featureId),
    ])

    const phaseGateStatus = gateStatus.phases[phaseId] || {}

    // 2. 计算上下文
    const allTasksCompleted = areAllTasksCompleted(featureTasks)
    const expertReviewPassed = phaseGateStatus.review_status === 'completed'

    const context: PrerequisiteContext = {
      allTasksCompleted,
      expertReviewPassed,
      gateStatus: phaseGateStatus,
      phaseHasExpertReview: phaseConfig.hasExpertReview,
    }

    // 3. 构建执行清单
    const executionList: ExecutionItem[] = []

    // 3.1 before_tasks 框架步骤
    const beforeTaskSteps = frameworkSteps.filter(s => s.position === 'before_tasks')
    for (const step of beforeTaskSteps) {
      executionList.push(this.frameworkStepToExecutionItem(step, context))
    }

    // 3.2 Feature 任务
    for (const task of featureTasks) {
      executionList.push(this.featureTaskToExecutionItem(task))
    }

    // 3.3 after_tasks 框架步骤
    const afterTaskSteps = frameworkSteps.filter(s => s.position === 'after_tasks')
    for (const step of afterTaskSteps) {
      executionList.push(this.frameworkStepToExecutionItem(step, context))
    }

    // 3.4 end 框架步骤
    const endSteps = frameworkSteps.filter(s => s.position === 'end')
    for (const step of endSteps) {
      const item = this.frameworkStepToExecutionItem(step, context)
      // end-day 始终可执行
      if (step.id === 'end-day') {
        item.status = 'ready'
      }
      executionList.push(item)
    }

    return executionList
  }

  /**
   * 获取分组后的执行清单
   */
  async getGroupedExecutionList(phaseId: number, featureId: string): Promise<{
    beforeTasks: ExecutionItem[]
    tasks: ExecutionItem[]
    afterTasks: ExecutionItem[]
    endSteps: ExecutionItem[]
  }> {
    const list = await this.buildExecutionList(phaseId, featureId)

    // 根据位置分组
    const beforeTasks: ExecutionItem[] = []
    const tasks: ExecutionItem[] = []
    const afterTasks: ExecutionItem[] = []
    const endSteps: ExecutionItem[] = []

    let inTaskSection = false

    for (const item of list) {
      if (item.type === 'task') {
        inTaskSection = true
        tasks.push(item)
      } else if (item.type === 'framework') {
        // 使用 item.id 判断位置（框架步骤有固定 id）
        if (item.id === 'start-day') {
          beforeTasks.push(item)
        } else if (item.id === 'end-day') {
          endSteps.push(item)
        } else if (inTaskSection || afterTaskIds.includes(item.id)) {
          afterTasks.push(item)
        } else {
          beforeTasks.push(item)
        }
      }
    }

    return { beforeTasks, tasks, afterTasks, endSteps }
  }

  /**
   * 检查项是否可执行
   */
  canExecuteItem(item: ExecutionItem): boolean {
    return canExecute(item.status)
  }

  /**
   * 处理重试策略
   * 返回 true 表示可以执行，false 表示取消执行
   */
  async handleRerunPolicy(
    item: ExecutionItem,
    showConfirm: (message: string) => Promise<boolean>,
    showToast: (message: string) => void
  ): Promise<boolean> {
    const { rerunPolicy, status } = item

    // 检查是否已执行过
    const hasExecuted = ['generated', 'verified', 'approved'].includes(status)

    if (!hasExecuted) {
      return true // 首次执行，直接允许
    }

    switch (rerunPolicy.strategy) {
      case 'block':
        showToast(rerunPolicy.block_message || '无法重复执行')
        return false

      case 'confirm':
        return await showConfirm(
          rerunPolicy.confirm_message || '确定要重新执行吗？'
        )

      case 'allow':
      default:
        return true
    }
  }

  /**
   * 获取执行按钮配置
   */
  getExecuteButtonConfig(item: ExecutionItem): {
    label: string
    icon: string
    type: 'primary' | 'success' | 'warning' | 'danger' | 'info'
    disabled: boolean
    showDropdown: boolean
    dropdownOptions?: Array<{ label: string; value: string }>
  } {
    const { executionMode, status } = item

    // 基于状态的按钮禁用
    const disabled = !canExecute(status)

    // 基于执行模式的按钮配置
    switch (executionMode) {
      case 'non_interactive':
        return {
          label: status === 'failed' ? '重试' : '执行',
          icon: status === 'failed' ? 'refresh' : 'play',
          type: 'primary',
          disabled,
          showDropdown: false,
        }

      case 'interactive':
        return {
          label: '在终端中打开',
          icon: 'terminal',
          type: 'info',
          disabled,
          showDropdown: false,
        }

      case 'hybrid':
        return {
          label: status === 'failed' ? '重试' : '执行',
          icon: status === 'failed' ? 'refresh' : 'play',
          type: 'primary',
          disabled,
          showDropdown: true,
          dropdownOptions: [
            { label: '直接执行', value: 'execute' },
            { label: '在终端中继续', value: 'terminal' },
          ],
        }

      default:
        return {
          label: '执行',
          icon: 'play',
          type: 'primary',
          disabled,
          showDropdown: false,
        }
    }
  }

  // ========== 私有方法 ==========

  /**
   * 将 FrameworkStep 转换为 ExecutionItem
   */
  private frameworkStepToExecutionItem(
    step: FrameworkStep,
    context: PrerequisiteContext
  ): ExecutionItem {
    const status = computeFrameworkStepStatus(step, context)

    return {
      id: step.id,
      name: step.name,
      type: 'framework',
      icon: step.icon,
      command: step.command,
      status,
      executionMode: step.execution_mode,
      rerunPolicy: step.rerun_policy,
      prerequisite: step.prerequisite,
      expectedArtifacts: step.expected_artifacts,
      owner: step.owner,
      description: step.description,
      failureRecovery: step.failure_recovery,
    }
  }

  /**
   * 将 FeatureTask 转换为 ExecutionItem
   */
  private featureTaskToExecutionItem(task: FeatureTask): ExecutionItem {
    const status = mapTaskStatus(task.status)

    // 构建命令字符串
    const command = this.buildCommandString(task)

    return {
      id: task.id,
      name: task.name || task.task,
      type: 'task',
      command,
      status,
      executionMode: 'hybrid', // Feature 任务默认 hybrid
      rerunPolicy: { strategy: 'allow' },
      owner: 'hybrid',
      description: task.notes,
      artifacts: task.artifacts,
    }
  }

  /**
   * 根据 TaskCommand 构建可执行的命令字符串
   */
  private buildCommandString(task: FeatureTask): string | undefined {
    const { command } = task

    if (!command) {
      // 没有配置命令，返回默认的任务提示命令
      // 使用任务描述作为提示内容
      return `claude --print "请帮我完成任务: ${task.task}"`
    }

    switch (command.type) {
      case 'slash_command':
        // Slash command: 直接使用 claude 执行
        return `claude ${command.value}`

      case 'skill':
        // Skill: 使用 claude --skill
        return `claude --skill ${command.value}`

      case 'subagent':
        // Subagent: 使用 claude --subagent
        return `claude --subagent ${command.value}`

      case 'bash':
        // Bash: 直接执行 shell 命令
        return command.value

      default:
        return `claude --print "${command.value}"`
    }
  }
}

// after_tasks 位置的框架步骤 ID
const afterTaskIds = ['expert-review', 'check-gate', 'approve-gate', 'next-phase']

// 导出单例
export const executionEngine = new ExecutionEngine()
