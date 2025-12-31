/**
 * useConfigLoader Composable
 * 提供配置加载的响应式接口
 */

import { ref, computed, watch, onMounted } from 'vue'
import { configLoader } from '../services/configLoader'
import type { PhaseConfig, ToolConfig } from '../types/workflow.types'

export interface UseConfigLoaderOptions {
  autoLoad?: boolean
}

export function useConfigLoader(
  phaseIdRef: () => number,
  featureIdRef: () => string | undefined,
  options: UseConfigLoaderOptions = {}
) {
  const { autoLoad = true } = options

  // 状态
  const loading = ref(false)
  const error = ref<string | null>(null)
  const phaseConfig = ref<PhaseConfig | null>(null)

  // 计算属性
  const objectives = computed(() => phaseConfig.value?.objectives || [])
  const inputs = computed(() => phaseConfig.value?.inputs || [])
  const references = computed(() => phaseConfig.value?.references || [])
  const tools = computed(() => phaseConfig.value?.tools || [])
  const phaseName = computed(() => phaseConfig.value?.displayName || '')
  const phaseColor = computed(() => phaseConfig.value?.color || '#6b7280')
  const hasExpertReview = computed(() => phaseConfig.value?.hasExpertReview || false)

  // 加载配置
  async function loadConfig() {
    const phaseId = phaseIdRef()
    const featureId = featureIdRef()

    if (phaseId === undefined || phaseId === null) {
      return
    }

    loading.value = true
    error.value = null

    try {
      phaseConfig.value = await configLoader.loadPhaseConfig(phaseId, featureId)
    } catch (err: any) {
      console.error('Failed to load phase config:', err)
      error.value = err.message || '加载配置失败'
    } finally {
      loading.value = false
    }
  }

  // 刷新配置
  async function refresh() {
    configLoader.clearCache()
    await loadConfig()
  }

  // 自动加载
  if (autoLoad) {
    onMounted(() => {
      loadConfig()
    })

    // 监听 phaseId 和 featureId 变化
    watch(
      [phaseIdRef, featureIdRef],
      () => {
        loadConfig()
      },
      { immediate: false }
    )
  }

  return {
    // 状态
    loading,
    error,
    phaseConfig,

    // 计算属性
    objectives,
    inputs,
    references,
    tools,
    phaseName,
    phaseColor,
    hasExpertReview,

    // 方法
    loadConfig,
    refresh,
  }
}

/**
 * 简化版 - 仅加载工具
 */
export function useTools(phaseIdRef: () => number) {
  const loading = ref(false)
  const error = ref<string | null>(null)
  const tools = ref<ToolConfig[]>([])

  async function loadTools() {
    const phaseId = phaseIdRef()
    if (phaseId === undefined || phaseId === null) return

    loading.value = true
    error.value = null

    try {
      tools.value = await configLoader.loadTools(phaseId)
    } catch (err: any) {
      error.value = err.message || '加载工具失败'
    } finally {
      loading.value = false
    }
  }

  onMounted(() => {
    loadTools()
  })

  watch(phaseIdRef, () => {
    loadTools()
  })

  return { loading, error, tools, loadTools }
}
