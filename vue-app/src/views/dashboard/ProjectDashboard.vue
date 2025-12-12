<template>
  <div class="project-dashboard">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="container">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">
            <el-icon><HomeFilled /></el-icon>
            首页
          </el-breadcrumb-item>
          <el-breadcrumb-item>项目看板</el-breadcrumb-item>
        </el-breadcrumb>
        <div class="header-content">
          <div class="header-left">
            <h1 class="page-title">系统总控看板</h1>
            <p class="page-subtitle">全周期交付进度追踪</p>
          </div>
          <div class="header-right">
            <span class="date-badge">
              <el-icon><Calendar /></el-icon>
              {{ currentDate }}
            </span>
            <span class="status-badge online">
              <span class="status-dot"></span>
              Online
            </span>
          </div>
        </div>
      </div>
    </div>

    <div class="page-content">
      <div class="container">
        <!-- AI Agent Daily Standup 面板 -->
        <div class="ai-task-panel">
          <div class="ai-header">
            <div class="ai-info">
              <div class="ai-avatar">
                <span>🤖</span>
              </div>
              <div class="ai-text">
                <h3>AI Project Agent · Daily Standup</h3>
                <p>{{ standupSummary }}</p>
              </div>
            </div>
            <el-button class="refresh-btn" @click="refreshTasks">
              <el-icon><Refresh /></el-icon>
              Refresh Plan
            </el-button>
          </div>
          <div class="standup-content">
            <!-- 今日进展 -->
            <div class="standup-section highlights">
              <div class="section-title">
                <span class="icon">✨</span> 今日进展
              </div>
              <div class="standup-items">
                <div v-for="(item, idx) in dailyStandup.highlights" :key="idx" class="standup-item">
                  <span class="feature-tag">{{ item.featureName }}</span>
                  <span class="item-text">{{ item.summary }}</span>
                </div>
              </div>
            </div>

            <!-- 阻塞问题 -->
            <div v-if="dailyStandup.blockers.length > 0" class="standup-section blockers">
              <div class="section-title">
                <span class="icon">⚠️</span> 阻塞问题
              </div>
              <div class="standup-items">
                <div v-for="(item, idx) in dailyStandup.blockers" :key="idx" class="standup-item blocker">
                  <span class="item-text">{{ item.issue }}</span>
                  <span class="blocked-since">已阻塞 {{ getBlockedDays(item.blockedSince) }} 天</span>
                </div>
              </div>
            </div>

            <!-- 明日计划 -->
            <div class="standup-section tomorrow">
              <div class="section-title">
                <span class="icon">📅</span> 明日计划
              </div>
              <div class="standup-items">
                <div v-for="(item, idx) in dailyStandup.tomorrow" :key="idx" class="standup-item">
                  <span class="item-text">{{ item.plan }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 初始化配置说明 -->
        <el-collapse class="setup-guide-collapse">
          <el-collapse-item name="setup">
            <template #title>
              <div class="setup-guide-title">
                <el-icon><Setting /></el-icon>
                <span>项目初始化配置指南</span>
                <el-tag size="small" type="info">新同事必读</el-tag>
              </div>
            </template>
            <div class="setup-guide-content">
              <el-row :gutter="20">
                <!-- GitHub Token 配置 -->
                <el-col :span="12">
                  <div class="setup-step">
                    <div class="step-header">
                      <span class="step-number">1</span>
                      <h4>获取 GitHub Personal Access Token</h4>
                    </div>
                    <div class="step-content">
                      <ol>
                        <li>
                          访问
                          <el-link
                            type="primary"
                            href="https://github.com/settings/tokens?type=beta"
                            target="_blank"
                          >
                            GitHub Token 设置页面
                          </el-link>
                        </li>
                        <li>点击 <strong>"Generate new token"</strong></li>
                        <li>配置 Token:
                          <ul>
                            <li>Token name: <code>ai-coding-org-doc-viewer</code></li>
                            <li>Expiration: 选择有效期（建议 90 天）</li>
                            <li>Repository access: 选择 <strong>Only select repositories</strong> → 选 <code>ai-coding-org</code></li>
                            <li>Permissions → Contents: <strong>Read-only</strong></li>
                          </ul>
                        </li>
                        <li>点击 <strong>"Generate token"</strong> 并复制</li>
                      </ol>
                    </div>
                  </div>
                </el-col>

                <!-- Supabase 配置 -->
                <el-col :span="12">
                  <div class="setup-step">
                    <div class="step-header">
                      <span class="step-number">2</span>
                      <h4>配置 Supabase Edge Function</h4>
                    </div>
                    <div class="step-content">
                      <ol>
                        <li>
                          访问
                          <el-link
                            type="primary"
                            href="https://supabase.com/dashboard/project/mvabqxkfekbrzgmjkvih/settings/functions"
                            target="_blank"
                          >
                            Supabase Functions 设置
                          </el-link>
                        </li>
                        <li>在 <strong>"Edge Function Secrets"</strong> 添加:
                          <ul>
                            <li>Name: <code>GITHUB_TOKEN</code></li>
                            <li>Value: 粘贴你的 GitHub Token</li>
                          </ul>
                        </li>
                        <li>确保 <code>github-docs-proxy</code> 函数的 <strong>Verify JWT</strong> 设置为 <strong>OFF</strong></li>
                      </ol>
                      <el-alert
                        type="info"
                        :closable="false"
                        show-icon
                      >
                        <template #title>
                          Edge Function 已部署，只需配置 Token 即可使用
                        </template>
                      </el-alert>
                    </div>
                  </div>
                </el-col>
              </el-row>

              <!-- 本地开发配置 -->
              <div class="setup-step local-dev">
                <div class="step-header">
                  <span class="step-number">3</span>
                  <h4>本地开发环境配置</h4>
                </div>
                <div class="step-content">
                  <p>在 <code>vue-app/.env</code> 文件中添加：</p>
                  <el-input
                    type="textarea"
                    :rows="2"
                    :model-value="envExample"
                    readonly
                    class="code-block"
                  />
                  <el-button
                    size="small"
                    @click="copyEnvExample"
                    style="margin-top: 8px;"
                  >
                    <el-icon><DocumentCopy /></el-icon>
                    复制配置
                  </el-button>
                </div>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>

        <!-- 甘特图卡片 -->
        <el-card class="gantt-card" shadow="never">
          <template #header>
            <div class="card-header">
              <div class="card-title">
                <el-icon><Calendar /></el-icon>
                全周期交付进度
                <span class="feature-count">
                  {{ visibleFeatures.length }} 个功能
                  <span v-if="archivedCount > 0" class="archived-hint">
                    ({{ archivedCount }} 个已归档)
                  </span>
                </span>
              </div>
              <div class="header-controls">
                <!-- 归档筛选 -->
                <el-checkbox
                  v-model="showArchived"
                  class="archive-toggle"
                  size="small"
                >
                  <el-icon><FolderOpened /></el-icon>
                  显示已归档
                </el-checkbox>
                <!-- 时间粒度切换 -->
                <div class="granularity-switch">
                  <el-radio-group v-model="timeGranularity" size="small">
                    <el-radio-button label="day">日</el-radio-button>
                    <el-radio-button label="week">周</el-radio-button>
                    <el-radio-button label="month">月</el-radio-button>
                  </el-radio-group>
                </div>
                <!-- 图例 -->
                <div class="legend">
                  <span class="legend-item">
                    <span class="legend-dot done"></span>
                    已完成
                  </span>
                  <span class="legend-item">
                    <span class="legend-dot wip"></span>
                    进行中
                  </span>
                  <span class="legend-item">
                    <span class="legend-dot blocked"></span>
                    阻塞
                  </span>
                  <span class="legend-item">
                    <span class="legend-dot pending"></span>
                    待开始
                  </span>
                </div>
              </div>
            </div>
          </template>

          <!-- 时间轴导航控制（固定不滚动） -->
          <div class="timeline-nav">
            <el-button
              size="small"
              text
              class="nav-btn"
              @click="extendTimelineBefore(7)"
              title="向前扩展一周"
            >
              ← 更早
            </el-button>
            <span class="timeline-range-info">
              {{ formatDateRange(timelineRange.start) }} ~ {{ formatDateRange(timelineRange.end) }}
            </span>
            <el-button
              size="small"
              text
              class="nav-btn"
              @click="scrollToToday()"
              title="滚动到今天"
            >
              📍 今天
            </el-button>
            <el-button
              size="small"
              text
              class="nav-btn"
              @click="resetTimelineRange()"
              title="重置时间范围"
            >
              重置
            </el-button>
            <el-button
              size="small"
              text
              class="nav-btn"
              @click="extendTimelineAfter(7)"
              title="向后扩展一周"
            >
              更晚 →
            </el-button>
          </div>

          <div class="gantt-container" :style="ganttCssVars">
            <!-- 左侧固定列 -->
            <div class="gantt-fixed-left">
              <!-- 表头 -->
              <div class="gantt-info-header">
                <div class="header-cell feature-col">功能模块</div>
                <div class="header-cell owner-col">负责人</div>
                <div class="header-cell progress-col">进度</div>
              </div>
              <!-- 数据行 -->
              <div
                v-for="feature in visibleFeatures"
                :key="'fixed-' + feature.id"
                class="gantt-info-cells"
                :class="{ collapsed: collapsedFeatures[feature.id] }"
                :style="{ height: getFeatureRowHeight(feature) + 'px' }"
              >
                <div class="info-cell feature-col">
                  <div class="feature-name-row">
                    <el-button
                      size="small"
                      text
                      class="collapse-btn"
                      @click.stop="toggleFeatureCollapse(feature.id)"
                      :title="collapsedFeatures[feature.id] ? '展开 Phase' : '收起 Phase'"
                    >
                      <el-icon :class="{ rotated: !collapsedFeatures[feature.id] }">
                        <ArrowRight />
                      </el-icon>
                    </el-button>
                    <div class="feature-name">{{ feature.name }}</div>
                  </div>
                  <div class="feature-date">{{ feature.startDate }} ~ {{ feature.endDate }}</div>
                </div>
                <div class="info-cell owner-col">
                  <span class="owner-tag">{{ feature.owner }}</span>
                </div>
                <div class="info-cell progress-col">
                  <el-button
                    size="small"
                    text
                    class="progress-btn"
                    @click="showProgressModal(feature)"
                    title="查看进度摘要"
                  >
                    📋
                  </el-button>
                </div>
              </div>
            </div>

            <!-- 右侧可滚动时间轴 -->
            <div class="gantt-scrollable" ref="ganttWrapperRef">
              <!-- 时间轴表头 -->
              <div class="gantt-timeline-header" :style="{ width: timelineWidthPx + 'px' }">
                <!-- TODAY 标志线 -->
                <div
                  class="today-line-header"
                  :style="{ left: `${todayLinePositionPx}px` }"
                  v-if="todayLinePositionPx >= 0"
                >
                  <span class="today-badge">TODAY</span>
                </div>
                <div
                  v-for="(date, index) in timelineDates"
                  :key="index"
                  class="timeline-cell"
                  :class="{ today: isToday(date), weekend: isWeekend(date) }"
                >
                  <div class="date-num">{{ formatCellDate(date) }}</div>
                  <div class="weekday">{{ getCellSubtitle(date) }}</div>
                </div>
              </div>

              <!-- 甘特条区域 -->
              <div
                v-for="feature in visibleFeatures"
                :key="'timeline-' + feature.id"
                class="gantt-phases-area"
                :class="{ collapsed: collapsedFeatures[feature.id] }"
                :style="{ height: getFeatureRowHeight(feature) + 'px', width: timelineWidthPx + 'px' }"
              >
                <!-- TODAY 标志线 -->
                <div
                  class="today-line"
                  :style="{ left: `${todayLinePositionPx}px` }"
                  v-if="todayLinePositionPx >= 0"
                ></div>

                <!-- Phase 条 - 瀑布式 (收起时隐藏) -->
                <template v-if="!collapsedFeatures[feature.id]">
                  <div
                    v-for="(phase, phaseIndex) in feature.schedule"
                    :key="phase.phaseId"
                    class="gantt-bar-row"
                    :style="{ top: phaseIndex * 40 + 'px' }"
                  >
                    <div
                      class="gantt-bar"
                      :class="phase.status"
                      :style="getBarStyle(phase)"
                      :title="`${phase.phaseName} (${getStatusLabel(phase.status)}) ${phase.progress}%`"
                      @click="goToFeaturePhase(feature.id, phase.phaseId)"
                    >
                      <span class="bar-label">{{ phase.phaseName }}</span>
                    </div>
                  </div>
                </template>
                <!-- 收起时显示简化的进度条 -->
                <div v-else class="collapsed-progress-bar" :style="getCollapsedBarStyle(feature)">
                  <span class="collapsed-label">{{ getFeatureProgress(feature) }}%</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>

      <!-- 底部提示 -->
      <div class="bottom-hint">
        <el-icon><InfoFilled /></el-icon>
        点击功能模块名称进入执行工作台 | 点击 Phase 条进入对应阶段
      </div>
    </div>
  </div>

    <!-- 进度摘要弹窗 -->
    <el-dialog
      v-model="progressModalVisible"
      :title="selectedFeature?.name + ' - 进度摘要'"
      width="560px"
      :style="{
        '--el-dialog-bg-color': '#1e293b',
        '--el-dialog-title-font-size': '16px',
        '--el-text-color-primary': '#f8fafc',
        '--el-text-color-regular': '#e2e8f0',
        '--el-border-color-lighter': '#334155'
      }"
    >
      <div v-if="selectedFeature" style="color: #e2e8f0;">
        <div style="margin-bottom: 20px;">
          <div style="font-size: 12px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">进度概览</div>
          <div style="font-size: 14px; color: #f1f5f9; padding: 12px; background: rgba(255, 255, 255, 0.05); border-radius: 8px; line-height: 1.6;">{{ selectedFeature.progressSummary }}</div>
        </div>
        <div>
          <div style="font-size: 12px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">各阶段状态</div>
          <div style="display: flex; flex-direction: column; gap: 8px;">
            <div
              v-for="phase in selectedFeature.schedule"
              :key="phase.phaseId"
              :style="{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '10px 12px',
                background: phase.status === 'done' ? 'rgba(16, 185, 129, 0.1)' : phase.status === 'wip' ? 'rgba(59, 130, 246, 0.1)' : 'rgba(255, 255, 255, 0.05)',
                borderRadius: '6px',
                borderLeft: '3px solid ' + (phase.status === 'done' ? '#10b981' : phase.status === 'wip' ? '#3b82f6' : phase.status === 'blocked' ? '#ef4444' : '#64748b')
              }"
            >
              <span style="font-size: 13px; font-weight: 600; color: #f1f5f9;">P{{ phase.phaseId }} {{ phase.phaseName }}</span>
              <span style="font-size: 12px; font-weight: 500; color: #cbd5e1;">{{ getStatusLabel(phase.status) }}</span>
              <span style="font-size: 12px; font-weight: 600; color: #60a5fa;">{{ phase.progress }}%</span>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
          <el-button text @click="viewDetailedLog(selectedFeature)" style="color: #94a3b8;">
            <el-icon><DocumentCopy /></el-icon>
            查看详细日志
          </el-button>
          <el-button @click="progressModalVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- GitHub 文档查看器弹窗 -->
    <DocViewerModal
      v-model="docViewerVisible"
      :title="docViewerTitle"
      :file-path="docViewerPath"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { HomeFilled, Calendar, Refresh, InfoFilled, Setting, DocumentCopy, FolderOpened, ArrowRight } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import DocViewerModal from '@/components/DocViewerModal.vue'
import { DOC_PATHS } from '@/config/github'
import {
  STATUS_LABELS,
  type PhaseStatus,
  type PhaseId,
  ganttFeatures as registryFeatures,
  currentDailyStandup,
  type GanttFeatureEntry,
  type PhaseSchedule,
  calculateTimelineRange,
  generateDateRange,
  formatDateShort as formatDate,
  getWeekdayCN as getWeekday,
  isToday as checkIsToday,
  isWeekend as checkIsWeekend,
  daysBetween
} from '@/data/projectRegistry'

const router = useRouter()

// 状态
const timeGranularity = ref<'day' | 'week' | 'month'>('day')
const progressModalVisible = ref(false)
const selectedFeature = ref<GanttFeatureEntry | null>(null)

// GitHub 文档查看器状态
const docViewerVisible = ref(false)
const docViewerTitle = ref('')
const docViewerPath = ref('')

// 环境配置示例
const envExample = `# Supabase 配置
VITE_SUPABASE_URL=https://mvabqxkfekbrzgmjkvih.supabase.co`

// 复制环境配置
function copyEnvExample() {
  navigator.clipboard.writeText(envExample).then(() => {
    ElMessage.success('已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败，请手动复制')
  })
}

// 时间轴范围扩展（天数）
const timelineExtendBefore = ref(3)  // 向前扩展的天数（减少空白）
const timelineExtendAfter = ref(7)   // 向后扩展的天数

// 甘特图容器 ref
const ganttWrapperRef = ref<HTMLElement | null>(null)

// 数据
const ganttFeatures = ref<GanttFeatureEntry[]>(registryFeatures)
const dailyStandup = ref(currentDailyStandup)

// 归档筛选
const showArchived = ref(false)

// 每个功能的展开/收起状态
const collapsedFeatures = ref<Record<string, boolean>>({})

// 切换功能展开/收起
function toggleFeatureCollapse(featureId: string) {
  collapsedFeatures.value[featureId] = !collapsedFeatures.value[featureId]
}

// 获取功能行高度
function getFeatureRowHeight(feature: GanttFeatureEntry): number {
  if (collapsedFeatures.value[feature.id]) {
    return 40 // 收起时只显示一行
  }
  return feature.schedule.length * 40
}

// 获取功能整体进度
function getFeatureProgress(feature: GanttFeatureEntry): number {
  if (feature.schedule.length === 0) return 0
  const totalProgress = feature.schedule.reduce((sum, phase) => sum + phase.progress, 0)
  return Math.round(totalProgress / feature.schedule.length)
}

// 获取收起时的简化进度条样式
function getCollapsedBarStyle(feature: GanttFeatureEntry) {
  // 计算整个功能的时间范围
  const startDate = new Date(feature.startDate)
  const endDate = new Date(feature.endDate)
  const rangeStart = new Date(timelineRange.value.start)

  const startOffset = Math.floor((startDate.getTime() - rangeStart.getTime()) / (1000 * 60 * 60 * 24))
  const duration = Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)) + 1

  const cellWidth = timeGranularity.value === 'day' ? 60 : timeGranularity.value === 'week' ? 80 : 100
  const left = startOffset * cellWidth
  const width = duration * cellWidth

  const progress = getFeatureProgress(feature)
  // 根据进度设置颜色
  const bgColor = progress === 100 ? '#10b981' : progress > 0 ? '#3b82f6' : '#475569'

  return {
    left: `${left}px`,
    width: `${width}px`,
    background: bgColor,
    top: '8px'
  }
}

// 计算可见的功能列表
const visibleFeatures = computed(() => {
  if (showArchived.value) {
    return ganttFeatures.value
  }
  return ganttFeatures.value.filter(f => !f.archived)
})

// 计算已归档数量
const archivedCount = computed(() => {
  return ganttFeatures.value.filter(f => f.archived).length
})

// 计算时间轴范围（基于可见任务 + 扩展范围）
const timelineRange = computed(() => {
  // 只计算可见功能的时间范围，减少空白
  const featuresToCalc = visibleFeatures.value.length > 0 ? visibleFeatures.value : ganttFeatures.value
  const range = calculateTimelineRange(featuresToCalc)
  const start = new Date(range.start)
  const end = new Date(range.end)
  // 根据用户设置的扩展范围调整
  start.setDate(start.getDate() - timelineExtendBefore.value)
  end.setDate(end.getDate() + timelineExtendAfter.value)
  return { start, end }
})

// 扩展时间轴范围
function extendTimelineBefore(days: number = 7) {
  timelineExtendBefore.value += days
}

function extendTimelineAfter(days: number = 7) {
  timelineExtendAfter.value += days
}

// 重置时间轴范围
function resetTimelineRange() {
  timelineExtendBefore.value = 3
  timelineExtendAfter.value = 7
}

// 滚动到今天
function scrollToToday() {
  if (!ganttWrapperRef.value) return

  // 计算今天的位置（像素）
  const todayPos = todayLinePositionPx.value

  // 左侧固定列宽度
  const fixedColsWidth = 180 + 100 + 60 // feature + owner + progress

  // 计算需要滚动到的位置（让今天显示在视口中间偏左）
  const viewportWidth = ganttWrapperRef.value.clientWidth - fixedColsWidth
  const scrollTarget = Math.max(0, todayPos - viewportWidth / 3)

  ganttWrapperRef.value.scrollTo({
    left: scrollTarget,
    behavior: 'smooth'
  })
}

// 生成时间轴日期（根据粒度调整格子数量）
const timelineDates = computed(() => {
  const dates = generateDateRange(timelineRange.value.start, timelineRange.value.end)

  if (timeGranularity.value === 'week') {
    // 按周：只返回每周一（或第一天）
    return dates.filter((d, i) => i === 0 || d.getDay() === 1)
  } else if (timeGranularity.value === 'month') {
    // 按月：只返回每月1号（或第一天）
    return dates.filter((d, i) => i === 0 || d.getDate() === 1)
  }

  return dates // 日视图返回所有日期
})

// 单格宽度（百分比）- 基于显示的格子数量
const cellWidthPercent = computed(() => {
  return 100 / timelineDates.value.length
})

// 单格像素宽度 - 根据粒度调整
const cellWidthPx = computed(() => {
  if (timeGranularity.value === 'day') {
    return 60  // 日视图：60px/格
  } else if (timeGranularity.value === 'week') {
    return 120 // 周视图：120px/格（一周）
  } else {
    return 200 // 月视图：200px/格（一个月）
  }
})

// 格子数量
const cellCount = computed(() => timelineDates.value.length)

// 时间轴总宽度（像素）
const timelineWidthPx = computed(() => cellWidthPx.value * cellCount.value)

// CSS 变量样式
const ganttCssVars = computed(() => ({
  '--cell-width': `${cellWidthPx.value}px`,
  '--cell-count': cellCount.value
}))

// 辅助函数：找到日期在哪个格子中，以及在格子内的偏移比例
function findCellPosition(date: Date): { cellIndex: number; offset: number } {
  const dates = timelineDates.value

  for (let i = 0; i < dates.length; i++) {
    const cellStart = dates[i]
    const cellEnd = dates[i + 1] || new Date(timelineRange.value.end.getTime() + 86400000)

    if (date >= cellStart && date < cellEnd) {
      // 计算在当前格子内的偏移比例
      const cellDays = daysBetween(cellStart, cellEnd)
      const offsetDays = daysBetween(cellStart, date)
      return {
        cellIndex: i,
        offset: cellDays > 0 ? offsetDays / cellDays : 0
      }
    }
  }

  // 日期在最后一个格子之后
  return { cellIndex: dates.length - 1, offset: 1 }
}

// 今日线位置（像素）- 基于格子位置计算
const todayLinePositionPx = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const { cellIndex, offset } = findCellPosition(today)
  // 定位到当天格子的中间
  const dates = timelineDates.value
  const cellStart = dates[cellIndex]
  const cellEnd = dates[cellIndex + 1] || new Date(timelineRange.value.end.getTime() + 86400000)
  const cellDays = daysBetween(cellStart, cellEnd) || 1
  const halfDayOffset = 0.5 / cellDays
  return (cellIndex + offset + halfDayOffset) * cellWidthPx.value
})

// 当前日期显示
const currentDate = computed(() => {
  const now = new Date()
  const month = now.toLocaleString('zh-CN', { month: 'short' })
  const day = now.getDate()
  return `${month} ${day}日`
})

// 站会摘要
const standupSummary = computed(() => {
  const highlights = dailyStandup.value.highlights.length
  const blockers = dailyStandup.value.blockers.length
  if (blockers > 0) {
    return `${highlights} 项进展, ${blockers} 项阻塞需关注`
  }
  return `${highlights} 项进展, 一切顺利`
})

// 计算 Phase 条的样式 - 使用像素定位确保对齐
function getBarStyle(phase: PhaseSchedule) {
  const phaseStart = new Date(phase.startDate)
  const phaseEnd = new Date(phase.endDate)

  // 找到开始和结束位置
  const startPos = findCellPosition(phaseStart)
  const endPos = findCellPosition(phaseEnd)

  // 使用像素计算 left 位置
  const leftPx = (startPos.cellIndex + startPos.offset) * cellWidthPx.value

  // 计算宽度（像素）
  let widthPx: number

  if (timeGranularity.value === 'day') {
    // 日视图：每格1天，宽度 = 占用天数 × 单格宽度
    widthPx = (endPos.cellIndex - startPos.cellIndex + 1) * cellWidthPx.value
  } else {
    // 周/月视图：宽度 = 跨越的格子数（含小数部分）× 单格宽度
    const startCellDays = getDaysInCell(startPos.cellIndex)
    const endCellDays = getDaysInCell(endPos.cellIndex)

    if (startPos.cellIndex === endPos.cellIndex) {
      // 同一格子内：宽度 = (结束日 - 开始日 + 1) / 格子天数 × 单格宽度
      const phaseDays = daysBetween(phaseStart, phaseEnd) + 1
      widthPx = (phaseDays / startCellDays) * cellWidthPx.value
    } else {
      // 跨多个格子
      const startCellPart = (1 - startPos.offset)
      const endCellPart = endPos.offset + (1 / endCellDays)
      const middleCells = endPos.cellIndex - startPos.cellIndex - 1

      widthPx = (startCellPart + middleCells + endCellPart) * cellWidthPx.value
    }
  }

  // 最小宽度（像素）
  const minWidthPx = 50

  return {
    left: `${leftPx}px`,
    width: `${Math.max(widthPx, minWidthPx)}px`
  }
}

// 获取指定格子包含的天数
function getDaysInCell(cellIndex: number): number {
  const dates = timelineDates.value
  const cellStart = dates[cellIndex]
  const cellEnd = dates[cellIndex + 1] || new Date(timelineRange.value.end.getTime() + 86400000)
  return daysBetween(cellStart, cellEnd) || 1
}

// 工具函数
function formatDateShort(date: Date): string {
  return formatDate(date)
}

// 格式化时间范围显示
function formatDateRange(date: Date): string {
  const month = date.getMonth() + 1
  const day = date.getDate()
  return `${month}/${day}`
}

function getWeekdayCN(date: Date): string {
  return getWeekday(date)
}

function isToday(date: Date): boolean {
  return checkIsToday(date)
}

function isWeekend(date: Date): boolean {
  return checkIsWeekend(date)
}

// 格式化格子日期显示
function formatCellDate(date: Date): string {
  if (timeGranularity.value === 'month') {
    return `${date.getMonth() + 1}月`
  }
  return formatDate(date)
}

// 格式化格子副标题
function getCellSubtitle(date: Date): string {
  if (timeGranularity.value === 'month') {
    return `${date.getFullYear()}`
  }
  if (timeGranularity.value === 'week') {
    return `W${getWeekNumber(date)}`
  }
  return getWeekday(date)
}

// 获取周数
function getWeekNumber(date: Date): number {
  const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()))
  const dayNum = d.getUTCDay() || 7
  d.setUTCDate(d.getUTCDate() + 4 - dayNum)
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1))
  return Math.ceil((((d.getTime() - yearStart.getTime()) / 86400000) + 1) / 7)
}

function getStatusLabel(status: PhaseStatus): string {
  return STATUS_LABELS[status] || status
}

function getBlockedDays(since: string): number {
  const blockedDate = new Date(since)
  const today = new Date()
  return daysBetween(blockedDate, today)
}

// 弹窗
function showProgressModal(feature: GanttFeatureEntry) {
  selectedFeature.value = feature
  progressModalVisible.value = true
}

// 查看详细日志（从摘要弹窗跳转）
function viewDetailedLog(feature: GanttFeatureEntry | null) {
  if (!feature) return
  progressModalVisible.value = false
  docViewerTitle.value = `${feature.name} - 详细日志`
  docViewerPath.value = DOC_PATHS.progressLog(feature.id)
  docViewerVisible.value = true
}

// 导航
function goToFeature(featureId: string) {
  progressModalVisible.value = false
  router.push(`/project-dashboard/${featureId}`)
}

function goToFeaturePhase(featureId: string, phaseId: PhaseId) {
  router.push(`/project-dashboard/${featureId}/${phaseId}`)
}

function refreshTasks() {
  // TODO: 实现刷新逻辑
}
</script>

<style scoped>
.project-dashboard {
  min-height: 100%;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

/* ========== Setup Guide ========== */
.setup-guide-collapse {
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: hidden;
}

.setup-guide-collapse :deep(.el-collapse-item__header) {
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 12px 20px;
  height: auto;
  line-height: 1.5;
}

.setup-guide-collapse :deep(.el-collapse-item__wrap) {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid #334155;
  border-top: none;
  border-radius: 0 0 12px 12px;
}

.setup-guide-collapse :deep(.el-collapse-item__content) {
  padding: 20px;
}

.setup-guide-title {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #e2e8f0;
  font-size: 15px;
  font-weight: 500;
}

.setup-guide-title .el-icon {
  color: #60a5fa;
}

.setup-guide-content {
  color: #cbd5e1;
}

.setup-step {
  background: rgba(15, 23, 42, 0.5);
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 16px;
}

.setup-step.local-dev {
  margin-top: 16px;
  margin-bottom: 0;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.step-number {
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  color: white;
  flex-shrink: 0;
}

.step-header h4 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #f1f5f9;
}

.step-content {
  font-size: 13px;
  line-height: 1.8;
}

.step-content ol, .step-content ul {
  margin: 8px 0;
  padding-left: 20px;
}

.step-content li {
  margin-bottom: 6px;
}

.step-content code {
  background: rgba(59, 130, 246, 0.2);
  color: #93c5fd;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
}

.step-content :deep(.el-link) {
  font-size: 13px;
}

.step-content :deep(.el-alert) {
  margin-top: 12px;
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.3);
}

.step-content :deep(.el-alert .el-alert__title) {
  color: #93c5fd;
  font-size: 12px;
}

.code-block :deep(.el-textarea__inner) {
  background: #0f172a;
  color: #93c5fd;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 12px;
  border: 1px solid #334155;
}

/* ========== Page Header ========== */
.page-header {
  background: rgba(15, 23, 42, 0.8);
  border-bottom: 1px solid #334155;
  padding: 24px 0 20px;
}

.page-header :deep(.el-breadcrumb__inner) {
  color: #94a3b8;
  display: flex;
  align-items: center;
  gap: 6px;
}

.page-header :deep(.el-breadcrumb__inner:hover) {
  color: #e2e8f0;
}

.page-header :deep(.el-breadcrumb__separator) {
  color: #475569;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-top: 16px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #f8fafc;
  margin: 0 0 4px;
}

.page-subtitle {
  font-size: 14px;
  color: #94a3b8;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.date-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #94a3b8;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #94a3b8;
}

.status-badge.online .status-dot {
  width: 8px;
  height: 8px;
  background: #10b981;
  border-radius: 50%;
}

/* ========== Page Content ========== */
.page-content {
  padding: 24px 0;
}

/* ========== AI Task Panel (Daily Standup) ========== */
.ai-task-panel {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
}

.ai-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.ai-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  box-shadow: 0 0 20px rgba(139, 92, 246, 0.4);
}

.ai-text h3 {
  font-size: 16px;
  font-weight: 700;
  color: #f8fafc;
  margin: 0 0 4px;
}

.ai-text p {
  font-size: 13px;
  color: #94a3b8;
  margin: 0;
}

.refresh-btn {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid #475569;
  color: #e2e8f0;
}

.refresh-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: #64748b;
}

/* Standup Content */
.standup-content {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 16px;
}

.standup-section {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  padding: 12px;
}

.section-title {
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.section-title .icon {
  font-size: 14px;
}

.standup-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.standup-item {
  font-size: 13px;
  color: #e2e8f0;
  line-height: 1.4;
}

.feature-tag {
  display: inline-block;
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
  margin-right: 6px;
}

.standup-item.blocker {
  color: #fca5a5;
}

.blocked-since {
  font-size: 11px;
  color: #f87171;
  margin-left: 8px;
}

/* ========== Gantt Card ========== */
.gantt-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
}

.gantt-card :deep(.el-card__header) {
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid #334155;
}

.gantt-card :deep(.el-card__body) {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #e2e8f0;
}

.feature-count {
  font-size: 12px;
  font-weight: 400;
  color: #64748b;
  margin-left: 8px;
}

.archived-hint {
  color: #94a3b8;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 20px;
}

.archive-toggle {
  margin-right: 8px;
}

.archive-toggle :deep(.el-checkbox__label) {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #94a3b8;
  font-size: 12px;
}

.archive-toggle :deep(.el-checkbox__input.is-checked + .el-checkbox__label) {
  color: #60a5fa;
}

.granularity-switch :deep(.el-radio-button__inner) {
  background: transparent;
  border-color: #475569;
  color: #94a3b8;
}

.granularity-switch :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

.legend {
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #94a3b8;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 2px;
}

.legend-dot.done { background: #10b981; }
.legend-dot.wip { background: #3b82f6; }
.legend-dot.blocked { background: #ef4444; }
.legend-dot.pending { background: transparent; border: 1px dashed #94a3b8; }

/* ========== Gantt Content ========== */
.gantt-container {
  display: flex;
  position: relative;
}

/* 左侧固定列 */
.gantt-fixed-left {
  flex-shrink: 0;
  background: #1e293b;
  z-index: 10;
  border-right: 2px solid #475569;
}

.gantt-info-header {
  display: flex;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid #334155;
}

/* 右侧可滚动区域 */
.gantt-scrollable {
  flex: 1;
  overflow-x: auto;
  position: relative;
}

.header-cell {
  padding: 12px 16px;
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  border-right: 1px solid #334155;
}

.feature-col { width: 180px; }
.owner-col { width: 100px; }
.progress-col { width: 60px; text-align: center; }

/* 时间轴导航控制 */
.timeline-nav {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid #334155;
}

.timeline-range-info {
  font-size: 12px;
  color: #94a3b8;
  font-weight: 500;
}

.nav-btn {
  font-size: 12px;
  color: #64748b;
  padding: 4px 8px;
}

.nav-btn:hover {
  color: #3b82f6;
  background: rgba(59, 130, 246, 0.1);
}

.gantt-timeline-header {
  display: flex;
  position: relative;
  background: rgba(255, 255, 255, 0.02);
  border-bottom: 1px solid #334155;
}

/* TODAY 标志线（表头） */
.today-line-header {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #ef4444;
  z-index: 20;
}

.today-badge {
  position: absolute;
  top: 2px;
  left: 4px;
  font-size: 9px;
  background: #ef4444;
  color: white;
  padding: 2px 6px;
  border-radius: 3px;
  font-weight: 700;
  white-space: nowrap;
}

/* 时间轴格子 - 固定宽度，根据粒度调整 */
.timeline-cell {
  width: var(--cell-width, 60px);
  min-width: var(--cell-width, 60px);
  padding: 8px 4px;
  text-align: center;
  border-left: 1px solid #334155;
  box-sizing: border-box;
  flex-shrink: 0;
}

.timeline-cell.today {
  background: rgba(239, 68, 68, 0.1);
}

.timeline-cell.weekend {
  background: rgba(100, 116, 139, 0.1);
}

.date-num {
  font-size: 12px;
  font-weight: 600;
  color: #e2e8f0;
}

.weekday {
  font-size: 10px;
  color: #64748b;
  margin-top: 2px;
}

.timeline-cell.today .date-num {
  color: #ef4444;
  font-weight: 700;
}

.gantt-info-cells {
  display: flex;
  border-bottom: 1px solid #334155;
}

.info-cell {
  padding: 12px 16px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  border-right: 1px solid #334155;
}

.info-cell.feature-col {
  cursor: default;
}

.feature-name-row {
  display: flex;
  align-items: center;
  gap: 4px;
}

.collapse-btn {
  padding: 2px;
  color: #64748b;
  transition: color 0.2s;
}

.collapse-btn:hover {
  color: #94a3b8;
}

.collapse-btn .el-icon {
  transition: transform 0.2s;
}

.collapse-btn .el-icon.rotated {
  transform: rotate(90deg);
}

.feature-name {
  font-size: 14px;
  font-weight: 600;
  color: #f8fafc;
  margin-bottom: 4px;
  transition: color 0.2s;
}

.gantt-info-cells.collapsed .feature-name {
  margin-bottom: 0;
}

.gantt-info-cells.collapsed .feature-date {
  display: none;
}

.feature-date {
  font-size: 11px;
  color: #64748b;
  margin-left: 24px;
}

/* 收起时的简化进度条 */
.collapsed-progress-bar {
  position: absolute;
  height: 24px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.collapsed-label {
  font-size: 11px;
  font-weight: 600;
  color: white;
}

.owner-tag {
  font-size: 12px;
  color: #94a3b8;
  background: rgba(100, 116, 139, 0.2);
  padding: 4px 8px;
  border-radius: 4px;
}

.progress-btn {
  font-size: 18px;
  padding: 8px;
}

.progress-btn:hover {
  background: rgba(59, 130, 246, 0.2);
}

/* ========== Gantt Phases Area (瀑布式) ========== */
.gantt-phases-area {
  position: relative;
  flex-shrink: 0;
  border-bottom: 1px solid #334155;
}

/* TODAY 标志线 */
.today-line {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #ef4444;
  z-index: 5;
  pointer-events: none;
}

/* Phase 条行 */
.gantt-bar-row {
  position: absolute;
  left: 0;
  right: 0;
  height: 40px;
  display: flex;
  align-items: center;
}

.gantt-bar {
  position: absolute;
  height: 28px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
  z-index: 1;
  min-width: 50px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.gantt-bar:hover {
  z-index: 10;
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.gantt-bar.done {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
}

.gantt-bar.wip {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.4);
}

.gantt-bar.blocked {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  animation: pulse-blocked 2s infinite;
}

.gantt-bar.pending {
  background: rgba(100, 116, 139, 0.3);
  border: 1px dashed #64748b;
  color: #94a3b8;
  box-shadow: none;
}

@keyframes pulse-blocked {
  0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
  70% { box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
  100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
}

.bar-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding: 0 8px;
  font-size: 11px;
}

/* ========== Bottom Hint ========== */
.bottom-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 20px;
  font-size: 13px;
  color: #64748b;
}

/* Progress Modal styles are in global style block at the end of file */

/* ========== Responsive ========== */
@media (max-width: 1200px) {
  .standup-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .page-title {
    font-size: 22px;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .header-controls {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
