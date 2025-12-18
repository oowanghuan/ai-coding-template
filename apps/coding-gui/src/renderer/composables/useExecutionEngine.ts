/**
 * useExecutionEngine Composable
 * 提供执行清单的响应式接口
 */

import { ref, computed, watch, onMounted } from 'vue'
import { executionEngine } from '../services/executionEngine'
import { configLoader } from '../services/configLoader'
import type { ExecutionItem } from '../types/workflow.types'

export interface UseExecutionEngineOptions {
  autoLoad?: boolean
}

export function useExecutionEngine(
  phaseIdRef: () => number,
  featureIdRef: () => string,
  options: UseExecutionEngineOptions = {}
) {
  const { autoLoad = true } = options

  // 状态
  const loading = ref(false)
  const error = ref<string | null>(null)
  const executionList = ref<ExecutionItem[]>([])

  // 分组后的执行清单
  const groupedList = ref<{
    beforeTasks: ExecutionItem[]
    tasks: ExecutionItem[]
    afterTasks: ExecutionItem[]
    endSteps: ExecutionItem[]
  }>({
    beforeTasks: [],
    tasks: [],
    afterTasks: [],
    endSteps: [],
  })

  // 计算属性
  const beforeTaskSteps = computed(() => groupedList.value.beforeTasks)
  const featureTasks = computed(() => groupedList.value.tasks)
  const afterTaskSteps = computed(() => groupedList.value.afterTasks)
  const endSteps = computed(() => groupedList.value.endSteps)

  const totalSteps = computed(() => executionList.value.length)
  const completedSteps = computed(() =>
    executionList.value.filter(item =>
      ['verified', 'approved', 'skipped'].includes(item.status)
    ).length
  )
  const progress = computed(() =>
    totalSteps.value > 0 ? Math.round((completedSteps.value / totalSteps.value) * 100) : 0
  )

  // 加载执行清单
  async function loadExecutionList() {
    const phaseId = phaseIdRef()
    const featureId = featureIdRef()

    if (phaseId === undefined || phaseId === null || !featureId) {
      return
    }

    loading.value = true
    error.value = null

    try {
      // 加载完整执行清单
      executionList.value = await executionEngine.buildExecutionList(phaseId, featureId)

      // 加载分组后的执行清单
      groupedList.value = await executionEngine.getGroupedExecutionList(phaseId, featureId)
    } catch (err: any) {
      console.error('Failed to load execution list:', err)
      error.value = err.message || '加载执行清单失败'
    } finally {
      loading.value = false
    }
  }

  // 刷新
  async function refresh() {
    configLoader.clearCache()
    await loadExecutionList()
  }

  // 获取执行按钮配置
  function getButtonConfig(item: ExecutionItem) {
    return executionEngine.getExecuteButtonConfig(item)
  }

  // 检查是否可执行
  function canExecute(item: ExecutionItem): boolean {
    return executionEngine.canExecuteItem(item)
  }

  // 处理重试策略
  async function handleRerunPolicy(
    item: ExecutionItem,
    showConfirm: (message: string) => Promise<boolean>,
    showToast: (message: string) => void
  ): Promise<boolean> {
    return executionEngine.handleRerunPolicy(item, showConfirm, showToast)
  }

  // 自动加载
  if (autoLoad) {
    onMounted(() => {
      loadExecutionList()
    })

    watch(
      [phaseIdRef, featureIdRef],
      () => {
        loadExecutionList()
      },
      { immediate: false }
    )
  }

  return {
    // 状态
    loading,
    error,
    executionList,

    // 分组
    beforeTaskSteps,
    featureTasks,
    afterTaskSteps,
    endSteps,

    // 统计
    totalSteps,
    completedSteps,
    progress,

    // 方法
    loadExecutionList,
    refresh,
    getButtonConfig,
    canExecute,
    handleRerunPolicy,
  }
}
