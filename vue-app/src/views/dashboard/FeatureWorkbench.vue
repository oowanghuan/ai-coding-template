<template>
  <div class="workbench-v2">
    <!-- 顶部导航 -->
    <div class="top-nav">
      <el-button text @click="goBack" class="back-btn">
        <el-icon><ArrowLeft /></el-icon>
        返回看板
      </el-button>
      <div class="phase-tabs">
        <div
          v-for="(step, index) in processSteps"
          :key="index"
          class="phase-tab"
          :class="{ active: currentPhase === index }"
          @click="switchPhase(index)"
        >
          <span class="phase-num">{{ index }}</span>
          <span class="phase-name">{{ step.name }}</span>
        </div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content" v-if="currentPhaseConfig">
      <!-- 页面标题 -->
      <div class="page-header">
        <div class="header-left">
          <h1>Phase {{ currentPhase }}: {{ currentPhaseConfig.name }}</h1>
          <p class="subtitle">{{ currentPhaseConfig.description }}</p>
          <div class="owner-badge" v-if="currentPhaseConfig.owner">
            <span class="owner-icon">👤</span>
            <span class="owner-text">负责角色: {{ currentPhaseConfig.owner }}</span>
          </div>
        </div>
        <div class="header-right">
          <div class="progress-ring">
            <span class="progress-text">{{ phaseProgress.done }}/{{ phaseProgress.total }}</span>
            <span class="progress-label">完成</span>
          </div>
        </div>
      </div>

      <!-- 内容区域 - 左右两栏布局 -->
      <div class="content-layout">
        <!-- 左栏：目标、上游输入、可用工具 -->
        <div class="left-column">
          <!-- 🎯 本阶段目标 -->
          <section class="section objectives-section">
            <h2><span class="icon">🎯</span> 本阶段目标</h2>
            <ul class="objective-list">
              <li v-for="(obj, idx) in currentPhaseConfig.objectives" :key="idx">
                {{ obj }}
              </li>
            </ul>
          </section>

          <!-- 📥 上游输入 -->
          <section class="section inputs-section">
            <h2>
              <span class="icon">📥</span> 上游输入
              <span class="from-phase" v-if="currentPhase > 0">
                (来自 Phase {{ currentPhase - 1 }})
              </span>
              <span class="status-badge" :class="upstreamReady ? 'ready' : 'pending'">
                {{ upstreamReady ? '✓' : '...' }}
              </span>
            </h2>
            <div class="input-list">
              <div
                v-for="(input, idx) in currentPhaseConfig.inputs"
                :key="idx"
                class="input-item"
                :class="{ ready: input.ready }"
              >
                <span class="status-icon">{{ input.ready ? '✓' : '○' }}</span>
                <span class="input-name">{{ input.name }}</span>
                <span class="input-desc">{{ input.description }}</span>
                <el-button size="small" text class="view-btn" @click="viewDocument(input)">
                  查看
                </el-button>
              </div>
            </div>
          </section>

          <!-- 📄 参考文档 -->
          <section class="section docs-section">
            <h2><span class="icon">📄</span> 参考文档 <span class="hint">(CC 参考模板)</span></h2>
            <div class="doc-list">
              <div
                v-for="(doc, idx) in currentPhaseConfig.referenceDocs"
                :key="idx"
                class="doc-item"
              >
                <span class="doc-name">{{ doc.name }}</span>
                <span class="doc-desc">{{ doc.description }}</span>
                <el-button size="small" text class="view-btn" @click="viewDocument(doc)">
                  查看
                </el-button>
              </div>
            </div>
          </section>

          <!-- 🛠️ 可用工具 -->
          <section class="section tools-section">
            <h2><span class="icon">🛠️</span> 可用工具</h2>
            <div class="tool-list">
              <div
                v-for="(tool, idx) in currentPhaseConfig.tools"
                :key="idx"
                class="tool-item"
                :class="[tool.type, tool.status]"
              >
                <div class="tool-header">
                  <span class="tool-command">{{ tool.command }}</span>
                  <span class="tool-type-badge">{{ getToolTypeName(tool.type) }}</span>
                  <span class="tool-priority-badge" :class="tool.priority">{{ tool.priority }}</span>
                  <span class="tool-status-badge" :class="tool.status">
                    {{ getToolStatusText(tool.status) }}
                  </span>
                </div>
                <div class="tool-desc">{{ tool.description }}</div>
                <div class="tool-actions">
                  <el-button size="small" text @click="showToolGuide(tool)">使用说明</el-button>
                  <el-button
                    v-if="tool.status === 'implemented'"
                    size="small"
                    text
                    @click="viewToolSource(tool)"
                  >查看源码</el-button>
                </div>
              </div>
            </div>
          </section>
        </div>

        <!-- 右栏：执行清单 -->
        <div class="right-column">
          <!-- 📋 执行清单 -->
          <section class="section execution-section">
            <h2>
              <span class="icon">📋</span> 执行清单
              <span class="progress-badge">{{ executionProgress.completed }}/{{ executionProgress.total }} 完成</span>
            </h2>
            <div class="execution-list">
              <div
                v-for="(step, idx) in executionSteps"
                :key="idx"
                class="execution-step"
                :class="step.status"
              >
                <!-- Step 头部 -->
                <div class="step-header" @click="toggleStep(idx)">
                  <div class="step-header-left">
                    <span class="step-num">Step {{ idx + 1 }}</span>
                    <span class="step-title">{{ step.title }}</span>
                  </div>
                  <div class="step-header-right">
                    <span class="step-status-badge" :class="step.status">
                      {{ getStepStatusText(step.status) }}
                    </span>
                    <el-icon class="expand-icon" :class="{ expanded: expandedSteps.includes(idx) }">
                      <ArrowDown />
                    </el-icon>
                  </div>
                </div>

                <!-- Step 内容（可折叠） -->
                <div class="step-content" v-show="expandedSteps.includes(idx)">
                  <!-- 操作步骤 -->
                  <div class="step-actions">
                    <div v-for="(action, aidx) in step.actions" :key="aidx" class="action-item">
                      <span class="actor" :class="action.actor">
                        {{ action.actor === 'human' ? '👤 你' : '🤖 CC' }}
                      </span>
                      <span class="action-text">{{ action.text }}</span>
                    </div>
                  </div>
                  <div v-if="step.loop" class="loop-indicator">🔁 {{ step.loop }}</div>

                  <!-- 交付物列表 -->
                  <div class="step-deliverables" v-if="step.deliverables && step.deliverables.length > 0">
                    <div class="deliverables-header">
                      <span class="icon">📄</span> 交付物
                    </div>
                    <div class="deliverable-list">
                      <div
                        v-for="(item, didx) in step.deliverables"
                        :key="didx"
                        class="deliverable-item"
                        :class="item.status"
                      >
                        <span class="status-icon">{{ getStatusIcon(item.status) }}</span>
                        <span class="item-name">{{ item.name }}</span>
                        <div class="deliverable-right">
                          <span class="version-tag" v-if="item.status === 'done' && item.currentVersion">
                            v{{ item.currentVersion }}
                          </span>
                          <div class="deliverable-actions" v-if="item.status === 'done' && item.path">
                            <el-button size="small" text class="view-btn" @click.stop="viewDeliverable(item)">
                              查看
                            </el-button>
                            <el-button size="small" text class="changelog-btn" @click.stop="viewChangelog(item)">
                              变更记录
                            </el-button>
                          </div>
                          <span class="pending-tag" v-if="item.status === 'pending'">待完成</span>
                          <span class="wip-tag" v-if="item.status === 'wip'">进行中</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- ➡️ 下游 -->
          <section class="section downstream-section" v-if="currentPhase < 7">
            <div class="downstream-info">
              <span class="icon">➡️</span>
              <span>下游: Phase {{ currentPhase + 1 }} {{ getPhaseName(currentPhase + 1) }}</span>
            </div>
          </section>
        </div>
      </div>
    </div>

    <!-- 文档查看弹窗 -->
    <el-dialog
      v-model="docDialogVisible"
      :title="currentDoc?.name || '文档预览'"
      width="70%"
      class="doc-dialog"
    >
      <div class="doc-content">
        <pre>{{ currentDoc?.content || '暂无内容' }}</pre>
      </div>
    </el-dialog>

    <!-- 工具说明弹窗 -->
    <el-dialog
      v-model="toolDialogVisible"
      :title="currentTool?.command || '工具说明'"
      width="60%"
      class="tool-dialog"
    >
      <div class="tool-guide">
        <h3>{{ currentTool?.description }}</h3>
        <div class="guide-section">
          <h4>使用方式</h4>
          <code>{{ currentTool?.command }}</code>
        </div>
        <div class="guide-section" v-if="currentTool?.status === 'implemented'">
          <h4>源文件</h4>
          <p>
            <code class="source-path">{{ getToolSourcePath(currentTool) }}</code>
          </p>
          <p>
            <a href="#" @click.prevent="viewToolSourceFromDialog" class="source-link">
              📄 查看 {{ getToolFileName(currentTool) }}
            </a>
          </p>
        </div>
        <div class="guide-section" v-if="currentTool?.prerequisites">
          <h4>前置条件</h4>
          <ul>
            <li v-for="(pre, idx) in currentTool?.prerequisites" :key="idx">{{ pre }}</li>
          </ul>
        </div>
        <div class="guide-section" v-if="currentTool?.output">
          <h4>预期输出</h4>
          <p>{{ currentTool?.output }}</p>
        </div>
      </div>
    </el-dialog>

    <!-- 交付物查看弹窗 -->
    <el-dialog
      v-model="deliverableDialogVisible"
      :title="currentDeliverable?.name || '交付物预览'"
      width="70%"
      class="doc-dialog"
    >
      <div class="doc-content">
        <div class="deliverable-meta">
          <span class="meta-item"><strong>路径:</strong> {{ currentDeliverable?.path }}</span>
          <span class="meta-item" v-if="currentDeliverable?.versions">
            <strong>当前版本:</strong> v{{ currentDeliverable?.currentVersion || currentDeliverable?.versions?.length }}
          </span>
        </div>
        <pre>{{ currentDeliverable?.preview || '（预览功能开发中...）' }}</pre>
      </div>
    </el-dialog>

    <!-- 变更记录弹窗 -->
    <el-dialog
      v-model="changelogDialogVisible"
      :title="currentDeliverable?.name ? `${currentDeliverable.name} - 变更记录` : '变更记录'"
      width="60%"
      class="changelog-dialog"
    >
      <div class="changelog-content">
        <div v-if="currentDeliverable?.changelog && currentDeliverable.changelog.length > 0">
          <div
            v-for="(entry, idx) in currentDeliverable.changelog"
            :key="idx"
            class="changelog-entry"
          >
            <div class="changelog-header">
              <span class="changelog-version">v{{ entry.version }}</span>
              <span class="changelog-date">{{ entry.date }}</span>
            </div>
            <ul class="changelog-changes">
              <li v-for="(change, cidx) in entry.changes" :key="cidx">{{ change }}</li>
            </ul>
          </div>
        </div>
        <div v-else class="no-changelog">
          <p>暂无变更记录</p>
          <p class="hint">文件首次创建，尚未有版本更新</p>
        </div>
      </div>
    </el-dialog>

    <!-- GitHub 文档查看器 -->
    <DocViewerModal
      v-model="docViewerVisible"
      :title="docViewerTitle"
      :file-path="docViewerPath"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { PHASE_NAMES, PHASE_COLORS, type PhaseId } from '@/data/projectRegistry'
import { generateRealProgressData } from '@/utils/progressLogParser'
import DocViewerModal from '@/components/DocViewerModal.vue'

const route = useRoute()
const router = useRouter()

// 8-Phase 流程步骤
const processSteps = [
  { name: 'Foundation', description: '系统基础建设' },
  { name: 'Kickoff', description: '功能启动' },
  { name: 'Spec', description: '需求规格' },
  { name: 'Demo', description: '原型演示' },
  { name: 'Design', description: '设计定稿' },
  { name: 'Code', description: '开发实现' },
  { name: 'Test', description: '测试验证' },
  { name: 'Deploy', description: '发布上线' }
]

// 工具状态类型
type ToolStatus = 'pending' | 'implemented'
type ToolPriority = 'P0' | 'P1' | 'P2' | 'P3'

// 各阶段配置数据 - 与 04_AI_WORKFLOW.md 完全同步
const phaseConfigs = computed(() => {
  const progress = generateRealProgressData()

  return {
    0: {
      name: 'Foundation',
      description: '建立项目级系统规范，为所有功能模块提供统一约束',
      owner: 'System Architect',
      objectives: [
        '建立 _system/ 目录结构',
        '配置 01_PROJECT_PROFILE.yaml',
        '创建 API/DB 规范文档',
        '创建 UI 设计系统（6层规范）'
      ],
      inputs: [
        { name: 'Brand Guidelines', description: '品牌设计指南（外部输入）', ready: true, info: '用户提供的品牌设计资料，如 Logo、配色、字体等' },
        { name: 'Tech Stack 决策', description: 'Vue3 + Supabase（外部输入）', ready: true, info: '技术选型决策，如前端框架、后端服务、数据库等' }
      ],
      tools: [
        {
          command: '/init-project',
          type: 'slash',
          description: '初始化 _system 目录和基础文档',
          status: 'implemented' as ToolStatus,
          priority: 'P3' as ToolPriority,
          prerequisites: ['确认技术栈选型', '准备品牌设计资料'],
          output: '生成 _system 目录结构和基础规范文档'
        },
        {
          command: 'system_scaffolder',
          type: 'skill',
          description: '根据 Profile 生成目录结构',
          status: 'implemented' as ToolStatus,
          priority: 'P3' as ToolPriority,
          output: '生成标准目录结构'
        }
      ],
      referenceDocs: [
        { name: 'CONTEXT_TEMPLATE.md', description: '项目上下文模板', path: '_templates/CC_COLLABORATION/03_TEMPLATES/00_CONTEXT_TEMPLATE.md' },
        { name: 'PROJECT_PROFILE_TEMPLATE.yaml', description: '项目画像模板', path: '_templates/CC_COLLABORATION/03_TEMPLATES/01_PROJECT_PROFILE_TEMPLATE.yaml' },
        { name: '02_API_CONVENTIONS.md', description: 'API 命名、错误码规范（示例）', path: 'docs/_foundation/02_API_CONVENTIONS.md' },
        { name: '03_DB_CONVENTIONS.md', description: '数据库命名、索引策略（示例）', path: 'docs/_foundation/03_DB_CONVENTIONS.md' },
        { name: '_ui_system_template/', description: 'UI 设计系统模板（6层规范）', path: '_templates/_foundation_templates/_ui_system_template/00_UI_TOKENS_TEMPLATE.md' }
      ],
      deliverables: getPhaseDeliverables(progress, 0),
      workflow: [
        {
          title: '每日开始',
          icon: '🌅',
          actions: [
            { actor: 'human', text: '输入 /start-day 或 "开始工作"' },
            { actor: 'cc', text: '执行 git pull，检查是否有冲突' },
            { actor: 'cc', text: '执行 /resume 恢复上下文，显示今日待办' }
          ],
          isDaily: true
        },
        {
          title: '准备上下文',
          actions: [
            { actor: 'human', text: '确认技术栈选型和品牌资料' },
            { actor: 'cc', text: '（等待指令）' }
          ]
        },
        {
          title: '初始化系统',
          actions: [
            { actor: 'human', text: '输入 /init-project' },
            { actor: 'cc', text: '创建 _system 目录结构，生成基础规范文档' },
            { actor: 'human', text: '审核生成的文档，必要时修改' }
          ]
        },
        {
          title: '完善 UI 系统',
          actions: [
            { actor: 'human', text: '指定 UI 风格偏好' },
            { actor: 'cc', text: '生成 6 层 UI 规范文档' },
            { actor: 'human', text: '审核 UI Token、组件规范等' }
          ]
        },
        {
          title: '确认交付',
          actions: [
            { actor: 'human', text: '确认所有系统级文档就绪' },
            { actor: 'cc', text: '（等待下一阶段指令）' }
          ]
        },
        {
          title: '每日结束',
          icon: '🌙',
          actions: [
            { actor: 'human', text: '输入 /end-day 或 "下班了"' },
            { actor: 'cc', text: '更新 PROGRESS_LOG，生成 DAILY_SUMMARY' },
            { actor: 'cc', text: '执行 git add + commit' },
            { actor: 'human', text: '确认后执行 git push' }
          ],
          isDaily: true
        }
      ]
    },
    1: {
      name: 'Kickoff',
      description: '为新功能模块建立上下文，明确边界、目标、约束',
      owner: 'Architect / PM',
      objectives: [
        '创建 {feature}/ 目录',
        '编写 00_CONTEXT.md',
        '明确功能边界，无歧义'
      ],
      inputs: [
        { name: '_system/* 规范', description: '系统级规范文档', ready: true, isSystem: true, path: 'docs/_foundation/00_PROJECT_CONTEXT.md' },
        { name: '用户需求描述', description: '功能需求输入（外部输入）', ready: true, info: '用户提供的功能需求描述，包括用户故事、验收标准等' }
      ],
      tools: [
        {
          command: '/new-feature <name>',
          type: 'slash',
          description: '创建功能模块目录和初始文档',
          status: 'implemented' as ToolStatus,
          priority: 'P0' as ToolPriority,
          args: "<name>",
          prerequisites: ['Phase 0 系统规范已就绪'],
          output: '生成功能目录和 00_CONTEXT.md'
        },
        {
          command: 'context_writer',
          type: 'skill',
          description: '根据需求描述生成 00_CONTEXT.md',
          status: 'implemented' as ToolStatus,
          priority: 'P2' as ToolPriority,
          prerequisites: ['明确功能边界和目标'],
          output: '生成 00_CONTEXT.md'
        }
      ],
      referenceDocs: [
        { name: 'CONTEXT_TEMPLATE.md', description: '功能上下文模板', path: '_templates/CC_COLLABORATION/03_TEMPLATES/00_CONTEXT_TEMPLATE.md' },
        { name: 'CHANGELOG_TEMPLATE.md', description: '变更记录模板', path: '_templates/CC_COLLABORATION/03_TEMPLATES/51_CHANGELOG_TEMPLATE.md' }
      ],
      deliverables: getPhaseDeliverables(progress, 1),
      workflow: [
        {
          title: '每日开始',
          icon: '🌅',
          actions: [
            { actor: 'human', text: '输入 /start-day 或 "开始工作"' },
            { actor: 'cc', text: '执行 git pull，检查是否有冲突' },
            { actor: 'cc', text: '执行 /resume 恢复上下文，显示今日待办' }
          ],
          isDaily: true
        },
        {
          title: '准备需求',
          actions: [
            { actor: 'human', text: '整理用户需求，明确功能边界' },
            { actor: 'cc', text: '（等待指令）' }
          ]
        },
        {
          title: '创建功能模块',
          actions: [
            { actor: 'human', text: "输入 /new-feature <name>" },
            { actor: 'cc', text: '创建功能目录，继承系统规范，生成上下文文档' },
            { actor: 'human', text: '审核 00_CONTEXT.md，确认边界和目标' }
          ]
        },
        {
          title: '确认交付',
          actions: [
            { actor: 'human', text: '确认上下文文档完整，通知下游' }
          ]
        },
        {
          title: '每日结束',
          icon: '🌙',
          actions: [
            { actor: 'human', text: '输入 /end-day 或 "下班了"' },
            { actor: 'cc', text: '更新 PROGRESS_LOG，生成 DAILY_SUMMARY' },
            { actor: 'cc', text: '执行 git add + commit' },
            { actor: 'human', text: '确认后执行 git push' }
          ],
          isDaily: true
        }
      ]
    },
    2: {
      name: 'Spec',
      description: '将功能需求转化为可执行的规格说明（UI 流程或 API 规范）',
      owner: 'AI Product Engineer',
      objectives: [
        '编写 11_UI_FLOW_SPEC.md（has_ui=true）',
        '或编写 11_API_SPEC.md（has_ui=false）',
        '定义交互规则和错误处理'
      ],
      inputs: [
        { name: '00_CONTEXT.md', description: '功能上下文', ready: true, path: '_templates/CC_COLLABORATION/03_TEMPLATES/00_CONTEXT_TEMPLATE.md', pathLabel: '查看模板' },
        { name: '_system 规范', description: '系统级规范', ready: true, isSystem: true, path: 'docs/_foundation/00_PROJECT_CONTEXT.md' }
      ],
      tools: [
        {
          command: 'spec_writer',
          type: 'subagent',
          description: '根据 CONTEXT 生成 SPEC 文档',
          status: 'implemented' as ToolStatus,
          priority: 'P1' as ToolPriority,
          prerequisites: ['功能上下文已就绪'],
          output: '生成 11_UI_FLOW_SPEC.md 或 11_API_SPEC.md'
        },
        {
          command: 'spec_validator',
          type: 'skill',
          description: '检查 SPEC 完整性和一致性',
          status: 'implemented' as ToolStatus,
          priority: 'P2' as ToolPriority,
          prerequisites: ['SPEC 文档已生成'],
          output: '验证报告'
        }
      ],
      referenceDocs: [
        { name: 'UI_FLOW_SPEC_TEMPLATE.md', description: 'UI 流程规格模板', path: '_templates/CC_COLLABORATION/03_TEMPLATES/11_UI_FLOW_SPEC_TEMPLATE.md' },
        { name: 'API_SPEC_TEMPLATE.md', description: 'API 规格模板', path: '_templates/CC_COLLABORATION/03_TEMPLATES/11_API_SPEC_TEMPLATE.md' },
        { name: 'CHANGELOG_TEMPLATE.md', description: '变更记录模板', path: '_templates/CC_COLLABORATION/03_TEMPLATES/51_CHANGELOG_TEMPLATE.md' }
      ],
      deliverables: getPhaseDeliverables(progress, 2),
      workflow: [
        {
          title: '每日开始',
          icon: '🌅',
          actions: [
            { actor: 'human', text: '输入 /start-day 或 "开始工作"' },
            { actor: 'cc', text: '执行 git pull，检查是否有冲突' },
            { actor: 'cc', text: '执行 /resume 恢复上下文，显示今日待办' }
          ],
          isDaily: true
        },
        {
          title: '读取上下文',
          actions: [
            { actor: 'human', text: '确认 00_CONTEXT.md 已就绪' },
            { actor: 'cc', text: '读取上下文，理解功能边界' }
          ]
        },
        {
          title: '生成规格',
          actions: [
            { actor: 'human', text: '让 CC 使用 spec_writer 生成规格' },
            { actor: 'cc', text: '按模板生成 UI Flow Spec 或 API Spec' },
            { actor: 'human', text: '审核规格是否完整、合理' }
          ]
        },
        {
          title: '迭代完善',
          actions: [
            { actor: 'human', text: '提出修改意见' },
            { actor: 'cc', text: '根据反馈调整规格' }
          ],
          loop: '直到规格确认'
        },
        {
          title: '每日结束',
          icon: '🌙',
          actions: [
            { actor: 'human', text: '输入 /end-day 或 "下班了"' },
            { actor: 'cc', text: '更新 PROGRESS_LOG，生成 DAILY_SUMMARY' },
            { actor: 'cc', text: '执行 git add + commit' },
            { actor: 'human', text: '确认后执行 git push' }
          ],
          isDaily: true
        }
      ]
    },
    3: {
      name: 'Demo',
      description: '生成可运行的 UI 原型 + Mock API，验证设计可行性',
      owner: 'AI Product Engineer',
      objectives: [
        '生成 playgrounds/{feature}/Demo.vue',
        '生成 playgrounds/{feature}/mock/api.js',
        '完成 Demo 评审，记录反馈'
      ],
      inputs: [
        { name: '11_UI_FLOW_SPEC.md', description: 'UI 流程规格', ready: true, path: '_templates/CC_COLLABORATION/03_TEMPLATES/11_UI_FLOW_SPEC_TEMPLATE.md', pathLabel: '查看模板' },
        { name: '_ui_system_template/*', description: 'UI 设计系统模板', ready: true, isSystem: true, path: '_templates/_foundation_templates/_ui_system_template/00_UI_TOKENS_TEMPLATE.md' }
      ],
      tools: [
        {
          command: '/gen-demo <feature>',
          type: 'slash',
          description: '一键生成 Demo + Mock API',
          status: 'implemented' as ToolStatus,
          priority: 'P2' as ToolPriority,
          args: '<feature>',
          prerequisites: ['UI Flow Spec 已确认'],
          output: '生成 playgrounds/{feature}/Demo.vue 和 mock/api.js'
        },
        {
          command: 'ui_demo',
          type: 'skill',
          description: '根据 SPEC + UI System 生成 Demo',
          status: 'implemented' as ToolStatus,
          priority: 'P1' as ToolPriority,
          output: '可运行的 Demo 组件'
        },
        {
          command: 'mock_api_generator',
          type: 'skill',
          description: '根据 SPEC 生成 Mock API',
          status: 'implemented' as ToolStatus,
          priority: 'P1' as ToolPriority,
          output: 'Mock 数据文件'
        }
      ],
      referenceDocs: [
        { name: 'DEMO_REVIEW_TEMPLATE.md', description: 'Demo 评审模板', path: '_templates/CC_COLLABORATION/03_TEMPLATES/12_DEMO_REVIEW_TEMPLATE.md' },
        { name: 'UI_DEMO_WITH_MOCK_API.md', description: 'Mock API Demo 工作流', path: '_templates/CC_COLLABORATION/02_WORKFLOWS/UI_DEMO_WITH_MOCK_API.md' }
      ],
      deliverables: getPhaseDeliverables(progress, 3),
      workflow: [
        {
          title: '每日开始',
          icon: '🌅',
          actions: [
            { actor: 'human', text: '输入 /start-day 或 "开始工作"' },
            { actor: 'cc', text: '执行 git pull，检查是否有冲突' },
            { actor: 'cc', text: '执行 /resume 恢复上下文，显示今日待办' }
          ],
          isDaily: true
        },
        {
          title: '生成原型',
          actions: [
            { actor: 'human', text: '输入 /gen-demo <feature>' },
            { actor: 'cc', text: '读取 UI Spec，生成 Vue 组件原型' },
            { actor: 'human', text: '运行 Demo，体验交互' }
          ]
        },
        {
          title: '收集反馈',
          actions: [
            { actor: 'human', text: '记录问题和改进建议' },
            { actor: 'cc', text: '根据反馈修改 Demo' }
          ],
          loop: '直到 Demo 通过评审'
        },
        {
          title: '确认交付',
          actions: [
            { actor: 'human', text: '填写 12_DEMO_REVIEW.md，确认通过' }
          ]
        },
        {
          title: '每日结束',
          icon: '🌙',
          actions: [
            { actor: 'human', text: '输入 /end-day 或 "下班了"' },
            { actor: 'cc', text: '更新 PROGRESS_LOG，生成 DAILY_SUMMARY' },
            { actor: 'cc', text: '执行 git add + commit' },
            { actor: 'human', text: '确认后执行 git push' }
          ],
          isDaily: true
        }
      ]
    },
    4: {
      name: 'Design',
      description: '基于 SPEC 和 Demo 反馈，完成技术设计，确定 API 契约和数据模型',
      owner: 'Architect',
      objectives: [
        '确定 API 契约（路径、参数、响应）',
        '定义数据模型',
        '验证与 Demo Mock API 的一致性'
      ],
      inputs: [
        { name: 'Demo.vue', description: '可交互原型（运行时生成）', ready: true, info: '由 /gen-demo 生成的 Vue 组件原型，位于 playgrounds/{feature}/Demo.vue' },
        { name: '11_UI_FLOW_SPEC.md', description: 'UI 流程规格', ready: true, path: '_templates/CC_COLLABORATION/03_TEMPLATES/11_UI_FLOW_SPEC_TEMPLATE.md', pathLabel: '查看模板' },
        { name: '_ui_system_template/*', description: 'UI 设计系统模板', ready: true, isSystem: true, path: '_templates/_foundation_templates/_ui_system_template/00_UI_TOKENS_TEMPLATE.md' }
      ],
      tools: [
        {
          command: 'design_from_demo',
          type: 'skill',
          description: '从 Demo Mock API 反推正式 API 契约',
          status: 'implemented' as ToolStatus,
          priority: 'P2' as ToolPriority,
          prerequisites: ['Demo 已通过评审'],
          output: '生成 10_DESIGN_FINAL.md'
        },
        {
          command: 'schema_generator',
          type: 'skill',
          description: '根据 DESIGN 生成数据库 Schema',
          status: 'implemented' as ToolStatus,
          priority: 'P3' as ToolPriority,
          output: 'SQL Schema 文件'
        }
      ],
      referenceDocs: [
        { name: 'DESIGN_TEMPLATE.md', description: '设计定稿模板', path: '_templates/CC_COLLABORATION/03_TEMPLATES/10_DESIGN_TEMPLATE.md' },
        { name: 'CHANGELOG_TEMPLATE.md', description: '变更记录模板', path: '_templates/CC_COLLABORATION/03_TEMPLATES/51_CHANGELOG_TEMPLATE.md' }
      ],
      deliverables: getPhaseDeliverables(progress, 4),
      workflow: [
        {
          title: '每日开始',
          icon: '🌅',
          actions: [
            { actor: 'human', text: '输入 /start-day 或 "开始工作"' },
            { actor: 'cc', text: '执行 git pull，检查是否有冲突' },
            { actor: 'cc', text: '执行 /resume 恢复上下文，显示今日待办' }
          ],
          isDaily: true
        },
        {
          title: '生成设计稿',
          actions: [
            { actor: 'human', text: '让 CC 使用 design_from_demo 生成设计' },
            { actor: 'cc', text: '读取 Demo 和 Spec，按模板生成设计定稿' },
            { actor: 'human', text: '审核设计是否符合 UI 系统' }
          ]
        },
        {
          title: '确认定稿',
          actions: [
            { actor: 'human', text: '确认 10_DESIGN_FINAL.md 完成' }
          ]
        },
        {
          title: '每日结束',
          icon: '🌙',
          actions: [
            { actor: 'human', text: '输入 /end-day 或 "下班了"' },
            { actor: 'cc', text: '更新 PROGRESS_LOG，生成 DAILY_SUMMARY' },
            { actor: 'cc', text: '执行 git add + commit' },
            { actor: 'human', text: '确认后执行 git push' }
          ],
          isDaily: true
        }
      ]
    },
    5: {
      name: 'Code',
      description: '按照 DESIGN 和 DEV_PLAN 进行开发，持续追踪进度',
      owner: 'Developer / Claude Code',
      objectives: [
        '完成所有 DEV_PLAN 任务',
        'PROGRESS_LOG 状态为 done',
        '代码已提交并通过 CI'
      ],
      inputs: [
        { name: '10_DESIGN_FINAL.md', description: '设计定稿', ready: true, path: '_templates/CC_COLLABORATION/03_TEMPLATES/10_DESIGN_TEMPLATE.md', pathLabel: '查看模板' },
        { name: 'Demo.vue', description: '可交互原型（运行时生成）', ready: true, info: '由 /gen-demo 生成的 Vue 组件原型，位于 playgrounds/{feature}/Demo.vue' }
      ],
      tools: [
        {
          command: '/check-progress <feature>',
          type: 'slash',
          description: '查看当前进度状态',
          status: 'implemented' as ToolStatus,
          priority: 'P1' as ToolPriority,
          args: '<feature>',
          output: '显示当前进度摘要'
        },
        {
          command: '/resume <feature>',
          type: 'slash',
          description: '断点恢复，读取 checkpoint 继续',
          status: 'implemented' as ToolStatus,
          priority: 'P0' as ToolPriority,
          args: '<feature>',
          prerequisites: ['存在 cc_checkpoint'],
          output: '恢复上下文，继续开发'
        },
        {
          command: '/daily-summary',
          type: 'slash',
          description: '从 PROGRESS_LOG 生成今日总结',
          status: 'implemented' as ToolStatus,
          priority: 'P0' as ToolPriority,
          output: '生成 31_DAILY_SUMMARY/{date}.md'
        },
        {
          command: 'review_alignment',
          type: 'skill',
          description: '检查代码与 DESIGN 一致性',
          status: 'implemented' as ToolStatus,
          priority: 'P1' as ToolPriority,
          output: '一致性检查报告'
        },
        {
          command: 'progress_updater',
          type: 'skill',
          description: '自动更新 PROGRESS_LOG',
          status: 'implemented' as ToolStatus,
          priority: 'P0' as ToolPriority,
          output: '更新任务状态和进度'
        },
        {
          command: 'progress_tracker',
          type: 'subagent',
          description: '解析 PROGRESS_LOG 生成 DAILY_SUMMARY',
          status: 'implemented' as ToolStatus,
          priority: 'P1' as ToolPriority,
          output: '每日进度摘要'
        }
      ],
      referenceDocs: [
        { name: 'DEV_PLAN_TEMPLATE.md', description: '开发计划模板', path: '_templates/CC_COLLABORATION/03_TEMPLATES/20_DEV_PLAN_TEMPLATE.md' },
        { name: 'PROGRESS_LOG_TEMPLATE.yaml', description: '进度日志模板', path: '_templates/CC_COLLABORATION/03_TEMPLATES/30_PROGRESS_LOG_TEMPLATE.yaml' },
        { name: 'DAILY_SUMMARY_TEMPLATE.md', description: '每日总结模板', path: '_templates/CC_COLLABORATION/03_TEMPLATES/31_DAILY_SUMMARY_TEMPLATE.md' },
        { name: 'RESUME_FROM_CHECKPOINT.md', description: '断点恢复工作流', path: '_templates/CC_COLLABORATION/02_WORKFLOWS/RESUME_FROM_CHECKPOINT.md' },
        { name: 'END_OF_DAY_PUSH.md', description: '每日提交工作流', path: '_templates/CC_COLLABORATION/02_WORKFLOWS/END_OF_DAY_PUSH.md' },
        { name: 'COMPACT_RECOVERY.md', description: '上下文压缩恢复', path: '_templates/CC_COLLABORATION/02_WORKFLOWS/COMPACT_RECOVERY.md' }
      ],
      deliverables: getPhaseDeliverables(progress, 5),
      workflow: [
        {
          title: '每日开始',
          icon: '🌅',
          actions: [
            { actor: 'human', text: '输入 /start-day 或 "开始工作"' },
            { actor: 'cc', text: '执行 git pull，检查是否有冲突' },
            { actor: 'cc', text: '执行 /resume 恢复上下文，显示今日待办' }
          ],
          isDaily: true
        },
        {
          title: '准备上下文',
          actions: [
            { actor: 'human', text: '确认设计文档已就绪' },
            { actor: 'cc', text: '（等待指令）' }
          ]
        },
        {
          title: '拆解任务',
          actions: [
            { actor: 'human', text: '让 CC 生成开发计划' },
            { actor: 'cc', text: '读取设计文档，按模板生成 20_DEV_PLAN.md' },
            { actor: 'human', text: '审核任务拆解是否合理' }
          ]
        },
        {
          title: '开发实现',
          actions: [
            { actor: 'human', text: '指定要实现的任务' },
            { actor: 'cc', text: '实现代码，更新 PROGRESS_LOG' },
            { actor: 'human', text: 'Code Review，确认实现符合设计' }
          ],
          loop: '直到所有任务完成'
        },
        {
          title: '交付下游',
          actions: [
            { actor: 'human', text: '确认所有交付物完成，通知 Phase 6' }
          ]
        },
        {
          title: '每日结束',
          icon: '🌙',
          actions: [
            { actor: 'human', text: '输入 /end-day 或 "下班了"' },
            { actor: 'cc', text: '更新 PROGRESS_LOG，生成 DAILY_SUMMARY' },
            { actor: 'cc', text: '执行 git add + commit' },
            { actor: 'human', text: '确认后执行 git push' }
          ],
          isDaily: true
        }
      ]
    },
    6: {
      name: 'Test',
      description: '根据 SPEC 编写测试计划，执行测试，生成报告',
      owner: 'QA / Claude Code',
      objectives: [
        '测试计划覆盖所有关键路径',
        '所有测试用例执行完毕',
        '无 P0/P1 级 Bug'
      ],
      inputs: [
        { name: '11_UI_FLOW_SPEC.md', description: 'UI 流程规格', ready: true, path: '_templates/CC_COLLABORATION/03_TEMPLATES/11_UI_FLOW_SPEC_TEMPLATE.md', pathLabel: '查看模板' },
        { name: 'src/modules/*', description: '代码实现（运行时生成）', ready: true, info: '开发阶段产出的源代码，位于 src/modules/{feature}/' },
        { name: '30_PROGRESS_LOG.yaml', description: '开发进度', ready: true, path: '_templates/CC_COLLABORATION/03_TEMPLATES/30_PROGRESS_LOG_TEMPLATE.yaml', pathLabel: '查看模板' }
      ],
      tools: [
        {
          command: '/run-tests <feature>',
          type: 'slash',
          description: '执行测试并生成报告',
          status: 'implemented' as ToolStatus,
          priority: 'P2' as ToolPriority,
          args: '<feature>',
          prerequisites: ['代码实现完成'],
          output: '生成 40_TEST_PLAN.md 和 41_TEST_REPORT.md'
        },
        {
          command: 'test_plan_writer',
          type: 'subagent',
          description: '根据 SPEC 生成测试计划',
          status: 'implemented' as ToolStatus,
          priority: 'P2' as ToolPriority,
          output: '测试计划文档'
        },
        {
          command: 'test_runner',
          type: 'skill',
          description: '执行测试计划（Chrome MCP / API 测试）',
          status: 'implemented' as ToolStatus,
          priority: 'P2' as ToolPriority,
          output: '测试执行结果'
        },
        {
          command: 'test_report_generator',
          type: 'skill',
          description: '汇总测试结果生成报告',
          status: 'implemented' as ToolStatus,
          priority: 'P2' as ToolPriority,
          output: '测试报告文档'
        }
      ],
      referenceDocs: [
        { name: 'TEST_PLAN_TEMPLATE.md', description: '测试计划模板', path: '_templates/CC_COLLABORATION/03_TEMPLATES/40_TEST_PLAN_TEMPLATE.md' },
        { name: 'TEST_REPORT_TEMPLATE.md', description: '测试报告模板', path: '_templates/CC_COLLABORATION/03_TEMPLATES/41_TEST_REPORT_TEMPLATE.md' }
      ],
      deliverables: getPhaseDeliverables(progress, 6),
      workflow: [
        {
          title: '每日开始',
          icon: '🌅',
          actions: [
            { actor: 'human', text: '输入 /start-day 或 "开始工作"' },
            { actor: 'cc', text: '执行 git pull，检查是否有冲突' },
            { actor: 'cc', text: '执行 /resume 恢复上下文，显示今日待办' }
          ],
          isDaily: true
        },
        {
          title: '生成测试计划',
          actions: [
            { actor: 'human', text: '确认开发已完成' },
            { actor: 'cc', text: '使用 test_plan_writer 生成测试计划' },
            { actor: 'human', text: '审核测试用例' }
          ]
        },
        {
          title: '执行测试',
          actions: [
            { actor: 'human', text: '输入 /run-tests <feature>' },
            { actor: 'cc', text: '执行测试，记录结果' }
          ]
        },
        {
          title: '处理问题',
          actions: [
            { actor: 'human', text: '确认测试结果' },
            { actor: 'cc', text: '如有失败，修复问题' }
          ],
          loop: '直到全部通过'
        },
        {
          title: '生成报告',
          actions: [
            { actor: 'cc', text: '生成 41_TEST_REPORT.md' },
            { actor: 'human', text: '确认测试通过' }
          ]
        },
        {
          title: '每日结束',
          icon: '🌙',
          actions: [
            { actor: 'human', text: '输入 /end-day 或 "下班了"' },
            { actor: 'cc', text: '更新 PROGRESS_LOG，生成 DAILY_SUMMARY' },
            { actor: 'cc', text: '执行 git add + commit' },
            { actor: 'human', text: '确认后执行 git push' }
          ],
          isDaily: true
        }
      ]
    },
    7: {
      name: 'Deploy',
      description: '汇总所有变更，生成发布说明，完成上线',
      owner: 'PM',
      objectives: [
        'RELEASE_NOTE 已生成',
        '所有文档已更新到最终状态',
        '代码已合并到主分支并部署'
      ],
      inputs: [
        { name: '30_PROGRESS_LOG.yaml', description: '开发进度', ready: true, path: '_templates/CC_COLLABORATION/03_TEMPLATES/30_PROGRESS_LOG_TEMPLATE.yaml', pathLabel: '查看模板' },
        { name: '41_TEST_REPORT.md', description: '测试报告', ready: true, path: '_templates/CC_COLLABORATION/03_TEMPLATES/41_TEST_REPORT_TEMPLATE.md', pathLabel: '查看模板' }
      ],
      tools: [
        {
          command: '/release <feature> <version>',
          type: 'slash',
          description: '生成 RELEASE_NOTE 并打 tag',
          status: 'implemented' as ToolStatus,
          priority: 'P2' as ToolPriority,
          args: '<feature> <version>',
          prerequisites: ['测试全部通过'],
          output: '生成 50_RELEASE_NOTE.md'
        },
        {
          command: 'release_summarizer',
          type: 'subagent',
          description: '汇总 PROGRESS_LOG + TEST_REPORT 生成 RELEASE_NOTE',
          status: 'implemented' as ToolStatus,
          priority: 'P2' as ToolPriority,
          output: 'Release Note'
        }
      ],
      referenceDocs: [
        { name: 'RELEASE_NOTE_TEMPLATE.md', description: '发布说明模板', path: '_templates/CC_COLLABORATION/03_TEMPLATES/50_RELEASE_NOTE_TEMPLATE.md' }
      ],
      deliverables: getPhaseDeliverables(progress, 7),
      workflow: [
        {
          title: '每日开始',
          icon: '🌅',
          actions: [
            { actor: 'human', text: '输入 /start-day 或 "开始工作"' },
            { actor: 'cc', text: '执行 git pull，检查是否有冲突' },
            { actor: 'cc', text: '执行 /resume 恢复上下文，显示今日待办' }
          ],
          isDaily: true
        },
        {
          title: '准备发布',
          actions: [
            { actor: 'human', text: '确认测试报告通过' },
            { actor: 'cc', text: '读取进度日志和测试报告' }
          ]
        },
        {
          title: '生成 Release Note',
          actions: [
            { actor: 'human', text: '输入 /release <feature> <version>' },
            { actor: 'cc', text: '汇总变更，生成 50_RELEASE_NOTE.md' },
            { actor: 'human', text: '审核发布内容' }
          ]
        },
        {
          title: '部署上线',
          actions: [
            { actor: 'human', text: '确认发布，触发部署' },
            { actor: 'cc', text: '（等待下一功能指令）' }
          ]
        },
        {
          title: '每日结束',
          icon: '🌙',
          actions: [
            { actor: 'human', text: '输入 /end-day 或 "下班了"' },
            { actor: 'cc', text: '更新 PROGRESS_LOG，生成 DAILY_SUMMARY' },
            { actor: 'cc', text: '执行 git add + commit' },
            { actor: 'human', text: '确认后执行 git push' }
          ],
          isDaily: true
        }
      ]
    }
  }
})

// State
const currentPhase = ref(0)
const docDialogVisible = ref(false)
const toolDialogVisible = ref(false)
const deliverableDialogVisible = ref(false)
const changelogDialogVisible = ref(false)
const currentDoc = ref<any>(null)
const currentTool = ref<any>(null)
const currentDeliverable = ref<any>(null)
const expandedSteps = ref<number[]>([]) // 当前展开的步骤

// GitHub 文档查看器
const docViewerVisible = ref(false)
const docViewerTitle = ref('')
const docViewerPath = ref('')

// Computed
const currentPhaseConfig = computed(() => phaseConfigs.value[currentPhase.value as PhaseId])

const phaseProgress = computed(() => {
  const deliverables = currentPhaseConfig.value?.deliverables || []
  const done = deliverables.filter((d: any) => d.status === 'done').length
  return { done, total: deliverables.length }
})

const upstreamReady = computed(() => {
  const inputs = currentPhaseConfig.value?.inputs || []
  return inputs.every((i: any) => i.ready)
})

// 将 workflow 和 deliverables 融合为执行步骤
const executionSteps = computed(() => {
  const config = currentPhaseConfig.value
  if (!config) return []

  const workflow = config.workflow || []
  const deliverables = config.deliverables || []

  // 为每个阶段定义步骤与交付物的映射
  const stepDeliverableMapping = getStepDeliverableMapping(currentPhase.value, deliverables)

  // 先创建带交付物的步骤数组
  const stepsWithDeliverables = workflow.map((step: any, idx: number) => {
    const stepDeliverables = stepDeliverableMapping[idx] || []
    return {
      ...step,
      deliverables: stepDeliverables,
      status: 'pending' // 临时状态
    }
  })

  // 再计算每个步骤的状态（需要知道所有步骤的信息）
  return stepsWithDeliverables.map((step: any, idx: number) => ({
    ...step,
    status: calculateStepStatus(step.deliverables, idx, stepsWithDeliverables)
  }))
})

// 执行进度
const executionProgress = computed(() => {
  const steps = executionSteps.value
  const completed = steps.filter((s: any) => s.status === 'done').length
  return { completed, total: steps.length }
})

// 初始化展开状态：展开第一个非完成的步骤
watch(executionSteps, (steps) => {
  if (steps.length > 0 && expandedSteps.value.length === 0) {
    // 找到第一个非 done 的步骤
    const firstActiveIdx = steps.findIndex((s: any) => s.status !== 'done')
    if (firstActiveIdx >= 0) {
      expandedSteps.value = [firstActiveIdx]
    } else {
      // 都完成了，展开最后一个
      expandedSteps.value = [steps.length - 1]
    }
  }
}, { immediate: true })

// 切换阶段时重置展开状态
watch(currentPhase, () => {
  expandedSteps.value = []
})

// Methods
const getPhaseName = (index: number): string => {
  return processSteps[index]?.name || ''
}

const getStatusIcon = (status: string): string => {
  switch (status) {
    case 'done': return '✓'
    case 'wip': return '⏳'
    case 'blocked': return '🚫'
    default: return '○'
  }
}

const getStepStatusText = (status: string): string => {
  switch (status) {
    case 'done': return '已完成'
    case 'in_progress': return '执行中'
    default: return '待开始'
  }
}

const toggleStep = (idx: number) => {
  const index = expandedSteps.value.indexOf(idx)
  if (index > -1) {
    expandedSteps.value.splice(index, 1)
  } else {
    expandedSteps.value.push(idx)
  }
}

// 计算步骤状态
function calculateStepStatus(deliverables: any[], stepIndex: number, allSteps: any[]): string {
  // 如果没有交付物，根据后续步骤的状态来判断
  if (deliverables.length === 0) {
    // 检查后续步骤是否有已完成或进行中的
    const laterStepsHaveProgress = allSteps.slice(stepIndex + 1).some(s => {
      const stepDeliverables = s.deliverables || []
      return stepDeliverables.some((d: any) => d.status === 'done' || d.status === 'wip')
    })
    // 如果后续步骤有进展，说明当前步骤已经完成
    if (laterStepsHaveProgress) return 'done'
    // 检查前面的步骤是否都完成了
    const previousStepsAllDone = allSteps.slice(0, stepIndex).every(s => {
      const stepDeliverables = s.deliverables || []
      if (stepDeliverables.length === 0) return true
      return stepDeliverables.every((d: any) => d.status === 'done')
    })
    if (previousStepsAllDone && stepIndex === 0) return 'done' // 第一步准备工作通常已完成
    return previousStepsAllDone ? 'in_progress' : 'pending'
  }

  const allDone = deliverables.every(d => d.status === 'done')
  const hasWip = deliverables.some(d => d.status === 'wip')
  const hasDone = deliverables.some(d => d.status === 'done')

  if (allDone) return 'done'
  if (hasWip || hasDone) return 'in_progress'
  return 'pending'
}

// 步骤与交付物的映射关系
function getStepDeliverableMapping(phaseId: number, deliverables: any[]): Record<number, any[]> {
  // 根据不同阶段定义映射
  // Phase 0: Foundation
  if (phaseId === 0) {
    return {
      0: [], // 准备上下文 - 无交付物，只是确认
      1: deliverables.filter(d =>
        d.name.includes('API_CONVENTIONS') ||
        d.name.includes('DB_CONVENTIONS') ||
        d.name.includes('/init-project')
      ),
      2: deliverables.filter(d =>
        d.name.includes('_ui_system') ||
        d.name.includes('UI_TOKENS') ||
        d.name.includes('COMPONENT_LIBRARY') ||
        d.name.includes('LAYOUT_RULES') ||
        d.name.includes('INTERACTION_RULES') ||
        d.name.includes('PAGE_TEMPLATES') ||
        d.name.includes('WORKFLOW_TEMPLATES')
      ),
      3: deliverables.filter(d =>
        d.name.includes('CC_COLLABORATION') ||
        d.name.includes('OVERVIEW') ||
        d.name.includes('COMMIT_RULES') ||
        d.name.includes('TEMPLATE')
      )
    }
  }

  // Phase 1: Kickoff
  if (phaseId === 1) {
    return {
      0: [], // 准备需求
      1: deliverables.filter(d => d.name.includes('CONTEXT')),
      2: [] // 确认交付
    }
  }

  // Phase 2: Spec
  if (phaseId === 2) {
    return {
      0: [],
      1: deliverables.filter(d =>
        d.name.includes('UI_FLOW') ||
        d.name.includes('API_SPEC')
      ),
      2: [] // 迭代完善
    }
  }

  // Phase 3: Demo
  if (phaseId === 3) {
    return {
      0: deliverables.filter(d => d.name.includes('Demo')),
      1: [], // 收集反馈
      2: deliverables.filter(d => d.name.includes('REVIEW'))
    }
  }

  // Phase 4: Design
  if (phaseId === 4) {
    return {
      0: deliverables.filter(d => d.name.includes('DESIGN')),
      1: []
    }
  }

  // Phase 5: Code
  if (phaseId === 5) {
    return {
      0: [],
      1: deliverables.filter(d => d.name.includes('DEV_PLAN')),
      2: deliverables.filter(d =>
        !d.name.includes('DEV_PLAN') &&
        !d.name.includes('DAILY_SUMMARY')
      ),
      3: deliverables.filter(d => d.name.includes('DAILY_SUMMARY')),
      4: []
    }
  }

  // Phase 6: Test
  if (phaseId === 6) {
    return {
      0: deliverables.filter(d => d.name.includes('TEST_PLAN')),
      1: [],
      2: [],
      3: deliverables.filter(d => d.name.includes('TEST_REPORT'))
    }
  }

  // Phase 7: Deploy
  if (phaseId === 7) {
    return {
      0: [],
      1: deliverables.filter(d => d.name.includes('RELEASE')),
      2: []
    }
  }

  // 默认：平均分配
  const stepsCount = 4
  const perStep = Math.ceil(deliverables.length / stepsCount)
  const mapping: Record<number, any[]> = {}
  for (let i = 0; i < stepsCount; i++) {
    mapping[i] = deliverables.slice(i * perStep, (i + 1) * perStep)
  }
  return mapping
}

const getToolTypeName = (type: string): string => {
  switch (type) {
    case 'slash': return 'Slash Command'
    case 'skill': return 'Skill'
    case 'subagent': return 'Subagent'
    default: return type
  }
}

const getToolStatusText = (status: string): string => {
  return status === 'implemented' ? '已实现' : '待实现'
}

const getPriorityLabel = (priority: string): string => {
  switch (priority) {
    case 'P0': return 'P0 必须'
    case 'P1': return 'P1 高优'
    case 'P2': return 'P2 标准'
    case 'P3': return 'P3 低优'
    default: return priority
  }
}

const switchPhase = (index: number) => {
  currentPhase.value = index
}

const goBack = () => {
  router.push('/project-dashboard')
}

const viewDocument = (doc: any) => {
  if (doc.path) {
    // 使用 DocViewerModal 打开 GitHub 文档
    // 统一路径格式：将 Docs/ 转为 docs/（GitHub 大小写敏感）
    let docPath = doc.path.replace(/^Docs\//, 'docs/')

    // 支持动态路径模板，替换 {featureId}
    const featureId = route.params.featureId as string
    if (featureId && docPath.includes('{feature}')) {
      docPath = docPath.replace('{feature}', featureId)
    }

    docViewerPath.value = docPath
    docViewerTitle.value = doc.pathLabel ? `${doc.name} - ${doc.pathLabel}` : doc.name
    docViewerVisible.value = true
  } else if (doc.info) {
    // 有 info 属性的外部输入，显示说明信息
    currentDoc.value = {
      name: doc.name,
      content: `# ${doc.name}\n\n**类型**：外部输入\n\n**说明**：${doc.info}\n\n---\n\n> 💡 这是一个外部输入项，由用户在实际开发时提供，不是系统预置的文档模板。`
    }
    docDialogVisible.value = true
  } else {
    // 没有 path 也没有 info 的情况，使用原来的 fallback dialog
    currentDoc.value = {
      name: doc.name,
      content: `# ${doc.name}\n\n${doc.description || ''}\n\n（文档路径未配置）`
    }
    docDialogVisible.value = true
  }
}

const viewDeliverable = (item: any) => {
  if (item.path) {
    // 使用 DocViewerModal 打开 GitHub 文档
    let docPath = item.path.replace(/^Docs\//, 'docs/')

    // 支持动态路径模板
    const featureId = route.params.featureId as string
    if (featureId && docPath.includes('{feature}')) {
      docPath = docPath.replace('{feature}', featureId)
    }

    docViewerPath.value = docPath
    docViewerTitle.value = item.name
    docViewerVisible.value = true
  } else {
    // fallback: 使用旧的交付物弹窗
    currentDeliverable.value = {
      name: item.name,
      path: `docs/_foundation/${item.name}`,
      versions: item.versions || ['1.0'],
      currentVersion: item.currentVersion || 1,
      preview: item.preview || `# ${item.name}\n\n${item.description || ''}\n\n（文件内容预览功能开发中...）`,
      changelog: item.changelog || []
    }
    deliverableDialogVisible.value = true
  }
}

const viewChangelog = (item: any) => {
  currentDeliverable.value = {
    name: item.name,
    path: item.path || `docs/_foundation/${item.name}`,
    changelog: item.changelog || [
      // 默认示例 changelog
      {
        version: 1,
        date: '2024-12-09',
        changes: ['初始版本创建']
      }
    ]
  }
  changelogDialogVisible.value = true
}

const showToolGuide = (tool: any) => {
  currentTool.value = tool
  toolDialogVisible.value = true
}

// 从工具命令生成源文件名
const getToolFileName = (tool: any): string => {
  if (!tool) return ''

  if (tool.type === 'slash') {
    // Slash Command: 从 /command <args> 中提取命令名
    const command = tool.command.split(' ')[0].replace('/', '')
    return `${command}.md`
  } else if (tool.type === 'skill' || tool.type === 'subagent') {
    // Skill / Subagent: 直接使用命令名
    return `${tool.command}.md`
  }
  return ''
}

// 获取工具源文件的路径
const getToolSourcePath = (tool: any): string => {
  if (!tool) return ''

  const fileName = getToolFileName(tool)
  const basePath = '_templates/CC_COLLABORATION/05_TOOLS'

  if (tool.type === 'slash') {
    return `${basePath}/slash-commands/${fileName}`
  } else if (tool.type === 'skill') {
    return `${basePath}/skills/${fileName}`
  } else if (tool.type === 'subagent') {
    return `${basePath}/subagents/${fileName}`
  }
  return ''
}

// 查看工具源码 - 使用 DocViewerModal
const viewToolSource = (tool: any) => {
  const docPath = getToolSourcePath(tool)
  const fileName = getToolFileName(tool)
  docViewerPath.value = docPath
  docViewerTitle.value = fileName
  docViewerVisible.value = true
}

// 从工具说明弹窗中查看源文件
const viewToolSourceFromDialog = () => {
  if (currentTool.value) {
    toolDialogVisible.value = false  // 先关闭工具说明弹窗
    viewToolSource(currentTool.value)
  }
}

// 键盘快捷键 0-7 切换阶段
const handleKeydown = (e: KeyboardEvent) => {
  const key = e.key
  if (key >= '0' && key <= '7') {
    switchPhase(Number(key))
  }
}

// 从路由参数获取初始阶段
watch(() => route.params.phaseId, (newPhaseId) => {
  if (newPhaseId) {
    currentPhase.value = parseInt(newPhaseId as string, 10)
  }
}, { immediate: true })

onMounted(() => {
  if (route.params.phaseId) {
    currentPhase.value = parseInt(route.params.phaseId as string, 10)
  }
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})

// 辅助函数：获取阶段交付物
function getPhaseDeliverables(progress: any, phaseId: number) {
  const phase = progress.phases[phaseId as PhaseId]
  if (!phase) return []

  return phase.tasks.map((t: any) => ({
    name: t.task,
    description: t.verification || '',
    status: t.status,
    // 为已完成的任务添加文件路径（基于任务名推断）
    path: t.status === 'done' ? inferFilePath(t.task) : undefined,
    // 版本信息
    versions: t.status === 'done' ? ['1.0'] : undefined,
    currentVersion: t.status === 'done' ? 1 : undefined,
    // changelog
    changelog: t.status === 'done' ? [{
      version: 1,
      date: t.completedAt || '2024-12-09',
      changes: ['初始版本创建']
    }] : undefined
  }))
}

// 根据任务名推断文件路径
function inferFilePath(taskName: string): string {
  // 如果任务名本身就是文件名格式
  if (taskName.includes('.md') || taskName.includes('.yaml') || taskName.includes('.ts')) {
    if (taskName.includes('_ui_system')) {
      return `docs/_foundation/${taskName}`
    }
    if (taskName.includes('CC_COLLABORATION')) {
      return `_templates/${taskName}`
    }
    return `docs/_foundation/${taskName}`
  }
  // 否则返回一个通用路径
  return `docs/_foundation/${taskName.replace(/\s+/g, '_')}`
}
</script>

<style scoped>
.workbench-v2 {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  color: #e2e8f0;
}

/* ========== Top Nav ========== */
.top-nav {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 12px 24px;
  background: rgba(15, 23, 42, 0.95);
  border-bottom: 1px solid #334155;
  position: sticky;
  top: 0;
  z-index: 100;
}

.back-btn {
  color: #94a3b8;
  font-size: 13px;
}

.back-btn:hover {
  color: #e2e8f0;
}

.phase-tabs {
  display: flex;
  gap: 4px;
  flex: 1;
  overflow-x: auto;
}

.phase-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  opacity: 0.6;
}

.phase-tab:hover {
  opacity: 0.8;
  background: rgba(255, 255, 255, 0.05);
}

.phase-tab.active {
  opacity: 1;
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.5);
}

.phase-num {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background: #334155;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

.phase-tab.active .phase-num {
  background: #3b82f6;
}

.phase-name {
  font-size: 13px;
  color: #94a3b8;
}

.phase-tab.active .phase-name {
  color: #e2e8f0;
}

/* ========== Main Content ========== */
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

/* ========== Two-Column Layout ========== */
.content-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.left-column,
.right-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* ========== Page Header ========== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  padding-bottom: 20px;
  border-bottom: 1px solid #334155;
}

.header-left h1 {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 8px;
}

.subtitle {
  font-size: 14px;
  color: #94a3b8;
  margin: 0;
}

.owner-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 10px;
  padding: 4px 12px;
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 999px;
  font-size: 12px;
}

.owner-icon {
  font-size: 14px;
}

.owner-text {
  color: #a78bfa;
}

.progress-ring {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 20px;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 12px;
}

.progress-text {
  font-size: 20px;
  font-weight: 600;
  color: #10b981;
}

.progress-label {
  font-size: 11px;
  color: #94a3b8;
}

/* ========== Sections ========== */
.section {
  margin-bottom: 24px;
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 16px 20px;
}

.section h2 {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.section h2 .icon {
  font-size: 16px;
}

.section h2 .hint {
  font-size: 12px;
  color: #64748b;
  font-weight: 400;
}

.section h2 .from-phase {
  font-size: 12px;
  color: #64748b;
  font-weight: 400;
}

.section h2 .status-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 999px;
  margin-left: auto;
}

.status-badge.ready {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.status-badge.pending {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.section h2 .progress-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 999px;
  margin-left: auto;
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

/* ========== Objectives ========== */
.objective-list {
  margin: 0;
  padding: 0 0 0 20px;
}

.objective-list li {
  font-size: 14px;
  line-height: 1.8;
  color: #cbd5e1;
}

/* ========== Inputs ========== */
.input-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 8px;
  border: 1px solid #1e293b;
}

.input-item.ready {
  border-color: rgba(16, 185, 129, 0.3);
}

.input-item .status-icon {
  color: #64748b;
  font-size: 14px;
}

.input-item.ready .status-icon {
  color: #10b981;
}

.input-item .input-name {
  font-size: 13px;
  font-weight: 500;
  color: #e2e8f0;
}

.input-item .input-desc {
  font-size: 12px;
  color: #64748b;
  flex: 1;
}

.view-btn {
  color: #3b82f6;
  font-size: 12px;
}

/* ========== Tools ========== */
.tool-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tool-item {
  padding: 12px 14px;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 8px;
  border: 1px solid #1e293b;
}

.tool-item.slash {
  border-left: 3px solid #8b5cf6;
}

.tool-item.skill {
  border-left: 3px solid #10b981;
}

.tool-item.subagent {
  border-left: 3px solid #f59e0b;
}

.tool-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.tool-command {
  font-family: ui-monospace, monospace;
  font-size: 13px;
  font-weight: 600;
  color: #e2e8f0;
}

.tool-type-badge {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(148, 163, 184, 0.1);
  color: #94a3b8;
}

.tool-priority-badge {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 600;
}

.tool-priority-badge.P0 {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.tool-priority-badge.P1 {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.tool-priority-badge.P2 {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.tool-priority-badge.P3 {
  background: rgba(148, 163, 184, 0.15);
  color: #94a3b8;
}

.tool-status-badge {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: auto;
}

.tool-status-badge.pending {
  background: rgba(148, 163, 184, 0.15);
  color: #94a3b8;
  border: 1px dashed #64748b;
}

.tool-status-badge.implemented {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.tool-item.pending {
  opacity: 0.7;
}

.tool-desc {
  font-size: 13px;
  color: #94a3b8;
  margin-bottom: 8px;
}

.tool-actions {
  display: flex;
  gap: 8px;
}

.tool-actions .el-button {
  color: #3b82f6;
  font-size: 12px;
}

/* ========== Docs ========== */
.doc-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.doc-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 8px;
  border: 1px solid #1e293b;
}

.doc-name {
  font-family: ui-monospace, monospace;
  font-size: 12px;
  color: #e2e8f0;
}

.doc-desc {
  font-size: 12px;
  color: #64748b;
  flex: 1;
}

/* ========== Deliverables ========== */
.deliverable-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.deliverable-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 6px;
}

.deliverable-item.done {
  opacity: 0.7;
}

.deliverable-item.done .status-icon {
  color: #10b981;
}

.deliverable-item.wip .status-icon {
  color: #3b82f6;
}

.deliverable-item.pending .status-icon {
  color: #64748b;
}

.deliverable-item.blocked .status-icon {
  color: #ef4444;
}

.deliverable-item {
  flex-direction: column;
  align-items: stretch;
}

.deliverable-main {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.deliverable-item .item-name {
  font-size: 13px;
  color: #e2e8f0;
}

.deliverable-item .item-desc {
  font-size: 12px;
  color: #64748b;
  flex: 1;
}

.deliverable-actions {
  display: flex;
  gap: 4px;
  margin-left: auto;
}

.deliverable-actions .view-btn,
.deliverable-actions .changelog-btn {
  color: #3b82f6;
  font-size: 12px;
}

.deliverable-actions .changelog-btn {
  color: #8b5cf6;
}

.version-info {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  padding-left: 24px;
  font-size: 11px;
}

.version-label {
  color: #64748b;
}

.version-current {
  color: #10b981;
  font-weight: 500;
}

.version-history {
  color: #64748b;
}

/* ========== Changelog Dialog ========== */
.changelog-dialog :deep(.el-dialog) {
  background: #1e293b;
  border: 1px solid #334155;
}

.changelog-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid #334155;
}

.changelog-dialog :deep(.el-dialog__title) {
  color: #e2e8f0;
}

.changelog-content {
  max-height: 60vh;
  overflow-y: auto;
}

.changelog-entry {
  padding: 12px;
  margin-bottom: 12px;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 8px;
  border-left: 3px solid #8b5cf6;
}

.changelog-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.changelog-version {
  font-size: 14px;
  font-weight: 600;
  color: #8b5cf6;
}

.changelog-date {
  font-size: 12px;
  color: #64748b;
}

.changelog-changes {
  margin: 0;
  padding: 0 0 0 20px;
}

.changelog-changes li {
  font-size: 13px;
  color: #cbd5e1;
  line-height: 1.6;
}

.no-changelog {
  text-align: center;
  padding: 24px;
  color: #64748b;
}

.no-changelog p {
  margin: 4px 0;
}

.no-changelog .hint {
  font-size: 12px;
}

.deliverable-meta {
  display: flex;
  gap: 20px;
  padding: 10px 12px;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 6px;
  margin-bottom: 12px;
}

.deliverable-meta .meta-item {
  font-size: 12px;
  color: #94a3b8;
}

.deliverable-meta .meta-item strong {
  color: #e2e8f0;
}

/* ========== Execution List (执行清单) ========== */
.execution-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.execution-step {
  background: rgba(15, 23, 42, 0.5);
  border-radius: 10px;
  border: 1px solid #1e293b;
  overflow: hidden;
  transition: all 0.2s ease;
}

.execution-step.done {
  border-color: rgba(16, 185, 129, 0.3);
}

.execution-step.in_progress {
  border-color: rgba(59, 130, 246, 0.5);
  box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.2);
}

.execution-step.pending {
  opacity: 0.7;
}

.execution-step .step-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-bottom: 0;
}

.execution-step .step-header:hover {
  background: rgba(255, 255, 255, 0.03);
}

.step-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.step-header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.step-num {
  font-size: 11px;
  font-weight: 600;
  color: #3b82f6;
  background: rgba(59, 130, 246, 0.15);
  padding: 3px 10px;
  border-radius: 4px;
}

.execution-step.done .step-num {
  color: #10b981;
  background: rgba(16, 185, 129, 0.15);
}

.execution-step.in_progress .step-num {
  color: #3b82f6;
  background: rgba(59, 130, 246, 0.2);
}

.step-title {
  font-size: 14px;
  font-weight: 500;
  color: #e2e8f0;
}

.step-status-badge {
  font-size: 11px;
  padding: 3px 10px;
  border-radius: 999px;
  font-weight: 500;
}

.step-status-badge.done {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.step-status-badge.in_progress {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.step-status-badge.pending {
  background: rgba(100, 116, 139, 0.15);
  color: #64748b;
  border: 1px solid rgba(100, 116, 139, 0.3);
}

.expand-icon {
  color: #64748b;
  transition: transform 0.2s;
  font-size: 14px;
}

.expand-icon.expanded {
  transform: rotate(180deg);
}

.step-content {
  padding: 0 16px 16px;
  border-top: 1px solid #1e293b;
}

.step-actions {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px 0 12px 12px;
  border-left: 2px solid #334155;
  margin-left: 8px;
  margin-top: 12px;
}

.action-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 13px;
}

.actor {
  font-size: 12px;
  white-space: nowrap;
  min-width: 50px;
}

.actor.human {
  color: #f59e0b;
}

.actor.cc {
  color: #8b5cf6;
}

.action-text {
  color: #cbd5e1;
}

.loop-indicator {
  margin-top: 8px;
  margin-left: 20px;
  font-size: 12px;
  color: #64748b;
  font-style: italic;
}

/* Step Deliverables */
.step-deliverables {
  margin-top: 16px;
  padding: 12px;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 8px;
}

.deliverables-header {
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.deliverables-header .icon {
  font-size: 14px;
}

.step-deliverables .deliverable-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.step-deliverables .deliverable-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  background: rgba(30, 41, 59, 0.5);
  border-radius: 6px;
  flex-direction: row;
}

.step-deliverables .deliverable-item.done {
  opacity: 1;
}

.step-deliverables .deliverable-item .status-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.step-deliverables .deliverable-item.done .status-icon {
  color: #10b981;
}

.step-deliverables .deliverable-item.pending .status-icon {
  color: #64748b;
}

.step-deliverables .deliverable-item.wip .status-icon {
  color: #3b82f6;
}

.step-deliverables .deliverable-item .item-name {
  font-size: 12px;
  color: #e2e8f0;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.deliverable-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.version-tag {
  font-size: 11px;
  color: #10b981;
  background: rgba(16, 185, 129, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
}

.pending-tag {
  font-size: 11px;
  color: #64748b;
  background: rgba(100, 116, 139, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
}

.wip-tag {
  font-size: 11px;
  color: #3b82f6;
  background: rgba(59, 130, 246, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
}

.step-deliverables .deliverable-actions {
  display: flex;
  gap: 4px;
}

.step-deliverables .deliverable-actions .el-button {
  padding: 2px 6px;
  font-size: 11px;
}

/* ========== Downstream ========== */
.downstream-section {
  background: transparent;
  border: 1px dashed #334155;
}

.downstream-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #94a3b8;
}

/* ========== Dialogs ========== */
.doc-dialog :deep(.el-dialog) {
  background: #1e293b;
  border: 1px solid #334155;
}

.doc-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid #334155;
}

.doc-dialog :deep(.el-dialog__title) {
  color: #e2e8f0;
}

.doc-content {
  max-height: 60vh;
  overflow-y: auto;
}

.doc-content pre {
  font-family: ui-monospace, monospace;
  font-size: 13px;
  color: #cbd5e1;
  white-space: pre-wrap;
  margin: 0;
}

.tool-dialog :deep(.el-dialog) {
  background: #1e293b;
  border: 1px solid #334155;
}

.tool-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid #334155;
}

.tool-dialog :deep(.el-dialog__title) {
  color: #e2e8f0;
  font-family: ui-monospace, monospace;
}

.tool-guide h3 {
  font-size: 16px;
  margin: 0 0 16px;
  color: #e2e8f0;
}

.guide-section {
  margin-bottom: 16px;
}

.guide-section h4 {
  font-size: 13px;
  color: #94a3b8;
  margin: 0 0 8px;
}

.guide-section code {
  display: block;
  padding: 10px 12px;
  background: #0f172a;
  border-radius: 6px;
  font-family: ui-monospace, monospace;
  font-size: 13px;
  color: #10b981;
}

.guide-section ul {
  margin: 0;
  padding: 0 0 0 20px;
}

.guide-section li {
  font-size: 13px;
  color: #cbd5e1;
  line-height: 1.6;
}

.guide-section p {
  font-size: 13px;
  color: #cbd5e1;
  margin: 0;
}

.source-path {
  display: block;
  padding: 8px 12px;
  background: #1e293b;
  border-radius: 4px;
  font-size: 12px;
  color: #94a3b8;
  word-break: break-all;
}

.source-link {
  color: #60a5fa;
  text-decoration: none;
  font-family: ui-monospace, monospace;
}

.source-link:hover {
  color: #93c5fd;
  text-decoration: underline;
}

/* ========== Responsive ========== */
@media (max-width: 1200px) {
  .content-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .main-content {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .header-right {
    align-self: flex-start;
  }

  .phase-tabs {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }

  .phase-name {
    display: none;
  }
}
</style>
