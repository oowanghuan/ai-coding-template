<template>
  <div class="workflow-guide-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="container">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">
            <el-icon><HomeFilled /></el-icon>
            首页
          </el-breadcrumb-item>
          <el-breadcrumb-item>实践指南</el-breadcrumb-item>
        </el-breadcrumb>
        <h1 class="page-title">🛠️ 实践指南</h1>
        <p class="page-subtitle">工作流程、模板资源、自动化工具</p>

        <!-- Tab 切换 -->
        <div class="guide-tabs">
          <el-radio-group v-model="activeTab" size="large" @change="handleTabChange">
            <el-radio-button value="workflow">工作流指南</el-radio-button>
            <el-radio-button value="resources">资源与工具</el-radio-button>
          </el-radio-group>
        </div>
      </div>
    </div>

    <div class="page-content">
      <div class="container">
        <!-- 概述 -->
        <el-card class="content-section intro-section" shadow="never">
          <div class="intro-content">
            <h2 class="section-title">📖 指南概述</h2>
            <p class="intro-text">
              这份指南提供了 AI 时代下，从需求到上线的完整工作流程实践方案。
              与<router-link to="/roles-overview" class="link">角色与协作</router-link>页面的概念介绍不同，
              这里是<strong>可执行的操作手册</strong>，包含详细的文档模板、工具配置、代码示例和实战案例。
            </p>
            <div class="intro-features">
              <div class="feature-item">
                <span class="feature-icon">📁</span>
                <span class="feature-text">文件结构规范</span>
              </div>
              <div class="feature-item">
                <span class="feature-icon">📝</span>
                <span class="feature-text">文档模板库</span>
              </div>
              <div class="feature-item">
                <span class="feature-icon">⚙️</span>
                <span class="feature-text">工具配置</span>
              </div>
              <div class="feature-item">
                <span class="feature-icon">💻</span>
                <span class="feature-text">代码示例</span>
              </div>
              <div class="feature-item">
                <span class="feature-icon">🎯</span>
                <span class="feature-text">实战案例</span>
              </div>
            </div>
          </div>
        </el-card>

        <!-- Part 1: 快速开始 -->
        <el-card class="content-section" shadow="never">
          <h2 class="section-title">🚀 快速开始</h2>

          <div class="quick-start-grid">
            <div class="quick-start-card">
              <div class="qs-header">
                <span class="qs-icon">🔧</span>
                <h3 class="qs-title">1. 工具链准备</h3>
              </div>
              <ul class="qs-list">
                <li>安装 Claude Code（AI coding 主力工具）</li>
                <li>配置 MCP 工具：Supabase MCP、Chrome Dev MCP</li>
                <li>准备 Chat/Gemini API（用于设计评审）</li>
                <li>Git 仓库初始化</li>
              </ul>
            </div>

            <div class="quick-start-card">
              <div class="qs-header">
                <span class="qs-icon">📁</span>
                <h3 class="qs-title">2. 初始化项目结构</h3>
              </div>
              <div class="code-block-wrapper">
                <pre class="code-block">{{ initProjectCode }}</pre>
                <el-button size="small" class="copy-btn" @click="copyCode(initProjectCode)">
                  <el-icon><DocumentCopy /></el-icon>
                  复制
                </el-button>
              </div>
            </div>

            <div class="quick-start-card">
              <div class="qs-header">
                <span class="qs-icon">🎯</span>
                <h3 class="qs-title">3. 第一个功能</h3>
              </div>
              <ul class="qs-list">
                <li>运行初始化脚本创建功能文档结构</li>
                <li>填写 00_CONTEXT.md（业务背景）</li>
                <li>编写 11_UI_FLOW_SPEC.md（UI规格）</li>
                <li>用 Claude Code 生成第一个 Demo</li>
              </ul>
            </div>
          </div>
        </el-card>

        <!-- Part 2: 文件结构规范 -->
        <el-card class="content-section" shadow="never">
          <h2 class="section-title">📁 文件结构规范</h2>
          <p class="section-desc">每个功能都在独立的目录下维护完整的生命周期文档</p>

          <div class="file-structure-section">
            <h3 class="subsection-title">🗂️ 功能目录结构：/docs/&lt;feature-slug&gt;/</h3>
            <div class="file-tree">
              <div class="file-item" v-for="(file, index) in featureFiles" :key="index">
                <div class="file-header" @click="file.expanded = !file.expanded">
                  <el-icon class="file-icon">
                    <template v-if="file.expanded">
                      <FolderOpened />
                    </template>
                    <template v-else>
                      <Folder />
                    </template>
                  </el-icon>
                  <span class="file-name">{{ file.name }}</span>
                  <span class="file-badge" :style="{ background: file.color }">{{ file.phase }}</span>
                </div>
                <div v-if="file.expanded" class="file-content">
                  <p class="file-desc">{{ file.description }}</p>
                  <div class="file-details">
                    <div class="detail-label">包含内容：</div>
                    <ul class="detail-list">
                      <li v-for="(item, i) in file.includes" :key="i">{{ item }}</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="file-structure-section">
            <h3 class="subsection-title">🎨 全局 UI 系统模板：/_templates/_foundation_templates/_ui_system_template/</h3>
            <el-alert type="info" :closable="false" show-icon>
              <p><strong>重要：</strong>这个目录只需要维护一次，被所有功能复用，确保 UI 一致性。</p>
            </el-alert>
            <div class="ui-system-grid">
              <div class="ui-system-card" v-for="(doc, index) in uiSystemDocs" :key="index">
                <div class="ui-header">
                  <span class="ui-icon">{{ doc.icon }}</span>
                  <h4 class="ui-title">{{ doc.name }}</h4>
                </div>
                <p class="ui-desc">{{ doc.description }}</p>
              </div>
            </div>
          </div>
        </el-card>

        <!-- Part 3: 六个阶段操作手册 -->
        <el-card class="content-section" shadow="never">
          <h2 class="section-title">📚 六个阶段操作手册</h2>
          <p class="section-desc">每个阶段的详细操作步骤、文档模板和工具使用</p>

          <el-tabs v-model="activePhase" class="phase-tabs">
            <el-tab-pane
              v-for="(phase, index) in phases"
              :key="index"
              :label="phase.name"
              :name="String(index)"
            >
              <template #label>
                <div class="tab-label">
                  <span class="tab-icon">{{ phase.icon }}</span>
                  <span class="tab-text">{{ phase.name }}</span>
                </div>
              </template>

              <div class="phase-content">
                <!-- 阶段概述 -->
                <div class="phase-overview">
                  <h3 class="phase-title">{{ phase.name }} - {{ phase.subtitle }}</h3>
                  <p class="phase-goal">🎯 <strong>目标：</strong>{{ phase.goal }}</p>
                </div>

                <!-- 操作步骤 -->
                <div class="phase-section">
                  <h4 class="phase-section-title">📋 操作步骤</h4>
                  <div class="steps-list">
                    <div
                      class="step-item"
                      v-for="(step, i) in phase.steps"
                      :key="i"
                    >
                      <div class="step-number">{{ i + 1 }}</div>
                      <div class="step-content">
                        <h5 class="step-title">{{ step.title }}</h5>
                        <p class="step-desc">{{ step.description }}</p>
                        <ul class="step-actions" v-if="step.actions">
                          <li v-for="(action, j) in step.actions" :key="j">{{ action }}</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 文档模板 -->
                <div class="phase-section" v-if="phase.template">
                  <h4 class="phase-section-title">📝 文档模板</h4>
                  <div class="template-card">
                    <div class="template-header">
                      <span class="template-name">{{ phase.template.name }}</span>
                      <el-button
                        size="small"
                        @click="copyCode(phase.template.content)"
                      >
                        <el-icon><DocumentCopy /></el-icon>
                        复制模板
                      </el-button>
                    </div>
                    <pre class="template-content">{{ phase.template.content }}</pre>
                  </div>
                </div>

                <!-- 工具使用 -->
                <div class="phase-section" v-if="phase.tools && phase.tools.length > 0">
                  <h4 class="phase-section-title">🔧 工具使用</h4>
                  <div class="tools-grid">
                    <div class="tool-card" v-for="(tool, i) in phase.tools" :key="i">
                      <h5 class="tool-name">{{ tool.name }}</h5>
                      <p class="tool-desc">{{ tool.description }}</p>
                      <div class="tool-command" v-if="tool.command">
                        <code>{{ tool.command }}</code>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 示例 -->
                <div class="phase-section" v-if="phase.example">
                  <h4 class="phase-section-title">💡 示例</h4>
                  <div class="example-card">
                    <h5 class="example-title">{{ phase.example.title }}</h5>
                    <p class="example-desc">{{ phase.example.description }}</p>
                    <div class="example-code" v-if="phase.example.code">
                      <pre>{{ phase.example.code }}</pre>
                    </div>
                  </div>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>

        <!-- Part 4: Skills & Agents 配置 -->
        <el-card class="content-section" shadow="never">
          <h2 class="section-title">⚙️ Skills & Agents 配置</h2>
          <p class="section-desc">配置 Claude Code 的 Skills 和 Agents，实现自动化工作流</p>

          <div class="skills-grid">
            <div class="skill-card" v-for="(skill, index) in skills" :key="index">
              <div class="skill-header">
                <span class="skill-icon">{{ skill.icon }}</span>
                <h3 class="skill-name">{{ skill.name }}</h3>
                <span class="skill-badge">{{ skill.type }}</span>
              </div>
              <p class="skill-purpose"><strong>用途：</strong>{{ skill.purpose }}</p>
              <div class="skill-trigger">
                <strong>触发时机：</strong>{{ skill.trigger }}
              </div>
              <div class="skill-config">
                <div class="config-header">
                  <span>配置示例</span>
                  <el-button size="small" @click="copyCode(skill.config)">
                    <el-icon><DocumentCopy /></el-icon>
                    复制
                  </el-button>
                </div>
                <pre class="config-code">{{ skill.config }}</pre>
              </div>
            </div>
          </div>
        </el-card>

        <!-- Part 5: 工具和脚本 -->
        <el-card class="content-section" shadow="never">
          <h2 class="section-title">🛠️ 工具和脚本</h2>
          <p class="section-desc">提高效率的自动化脚本</p>

          <div class="scripts-list">
            <div class="script-card" v-for="(script, index) in scripts" :key="index">
              <div class="script-header">
                <div class="script-info">
                  <h3 class="script-name">{{ script.name }}</h3>
                  <span class="script-file">{{ script.file }}</span>
                </div>
                <el-button type="primary" size="small" @click="copyCode(script.code)">
                  <el-icon><DocumentCopy /></el-icon>
                  复制脚本
                </el-button>
              </div>
              <p class="script-desc">{{ script.description }}</p>
              <div class="script-usage">
                <strong>使用方法：</strong>
                <code>{{ script.usage }}</code>
              </div>
              <div class="script-code-block">
                <pre>{{ script.code }}</pre>
              </div>
            </div>
          </div>
        </el-card>

        <!-- Part 6: 实战案例 -->
        <el-card class="content-section" shadow="never">
          <h2 class="section-title">🎯 实战案例</h2>
          <p class="section-desc">完整案例：订阅计费系统 V3 - 从需求到上线的全流程演练</p>

          <el-alert type="warning" :closable="false" show-icon class="case-alert">
            <p><strong>说明：</strong>这是一个真实的项目案例，展示如何将本指南应用到实际开发中。</p>
          </el-alert>

          <div class="case-timeline">
            <div class="case-step" v-for="(step, index) in caseStudy" :key="index">
              <div class="case-step-header">
                <div class="case-step-number">{{ index + 1 }}</div>
                <div class="case-step-info">
                  <h3 class="case-step-title">{{ step.phase }}</h3>
                  <span class="case-step-duration">{{ step.duration }}</span>
                </div>
              </div>
              <div class="case-step-content">
                <p class="case-step-desc">{{ step.description }}</p>
                <div class="case-deliverables">
                  <strong>交付物：</strong>
                  <ul>
                    <li v-for="(item, i) in step.deliverables" :key="i">{{ item }}</li>
                  </ul>
                </div>
                <div class="case-highlights" v-if="step.highlights">
                  <strong>关键点：</strong>
                  <ul>
                    <li v-for="(item, i) in step.highlights" :key="i">{{ item }}</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 底部导航 -->
        <div class="bottom-navigation">
          <el-button size="large" @click="router.push('/roles-overview')">
            <el-icon class="el-icon--left"><Back /></el-icon>
            返回角色与协作
          </el-button>
          <el-button type="primary" size="large" @click="router.push('/')">
            <el-icon class="el-icon--left"><HomeFilled /></el-icon>
            返回首页
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { HomeFilled, DocumentCopy, FolderOpened, Folder, Back } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const activeTab = ref('workflow')
const activePhase = ref('0')

// Tab 切换处理
const handleTabChange = (value) => {
  if (value === 'resources') {
    router.push('/resources')
  }
}

// 初始化项目代码
const initProjectCode = `# 创建文档目录结构
mkdir -p _templates/_foundation_templates/_ui_system_template
mkdir -p tools

# 初始化 UI 系统模板文档（只需一次）
touch _templates/_foundation_templates/_ui_system_template/00_UI_TOKENS_TEMPLATE.md
touch _templates/_foundation_templates/_ui_system_template/01_COMPONENT_LIBRARY_TEMPLATE.md
touch _templates/_foundation_templates/_ui_system_template/02_LAYOUT_RULES_TEMPLATE.md
touch _templates/_foundation_templates/_ui_system_template/03_INTERACTION_RULES_TEMPLATE.md
touch _templates/_foundation_templates/_ui_system_template/04_PAGE_TEMPLATES_TEMPLATE.md
touch _templates/_foundation_templates/_ui_system_template/05_WORKFLOW_TEMPLATES_TEMPLATE.md

# 创建初始化脚本
touch tools/init_feature.sh
chmod +x tools/init_feature.sh`

// 功能文件列表
const featureFiles = ref([
  {
    name: '00_CONTEXT.md',
    phase: 'Phase 1',
    color: '#1e3c72',
    description: '功能的业务背景、目标、约束条件',
    includes: ['业务背景和问题', '目标用户', '成功标准', '技术约束', '与现有系统的关系'],
    expanded: false
  },
  {
    name: '11_UI_FLOW_SPEC.md',
    phase: 'Phase 1',
    color: '#667eea',
    description: 'UI/UX 的结构化说明，供 AI 生成 Demo 使用',
    includes: ['用户角色和流程', '交互逻辑', '页面结构', '字段和组件定义', '边界条件和错误态', '示例数据'],
    expanded: false
  },
  {
    name: '10_DESIGN_FINAL.md',
    phase: 'Phase 3',
    color: '#11998e',
    description: '技术和架构设计方案',
    includes: ['架构概览', '数据模型', 'API 设计', '前后端分工', '错误处理和权限'],
    expanded: false
  },
  {
    name: '20_DEV_PLAN_FINAL.md',
    phase: 'Phase 3',
    color: '#11998e',
    description: '开发计划和任务清单',
    includes: ['按阶段拆分的任务', '每个任务的验证方式', '依赖关系', '风险评估'],
    expanded: false
  },
  {
    name: '30_PROGRESS_LOG.md',
    phase: 'Phase 4',
    color: '#ff9800',
    description: '开发进度日志（抗 compact 锚点）',
    includes: ['Checklist 状态', 'History 历史记录', 'Next Step 下一步', '遇到的问题和解决方案'],
    expanded: false
  },
  {
    name: '40_TEST_PLAN.md',
    phase: 'Phase 5',
    color: '#f093fb',
    description: '测试计划和用例列表',
    includes: ['后端测试用例', '前端测试用例', 'MCP 工具使用点', '测试数据准备'],
    expanded: false
  },
  {
    name: '41_TEST_REPORT.md',
    phase: 'Phase 5',
    color: '#f093fb',
    description: '测试执行结果报告',
    includes: ['通过/失败统计', 'Bug 清单', '测试覆盖率', 'Go/No-Go 建议'],
    expanded: false
  },
  {
    name: '50_RELEASE_NOTE.md',
    phase: 'Phase 6',
    color: '#06beb6',
    description: '发布说明和复盘总结',
    includes: ['本次迭代内容', '影响范围', '已知问题', '后续计划', '经验教训'],
    expanded: false
  }
])

// UI 系统文档
const uiSystemDocs = ref([
  {
    icon: '🎨',
    name: '00_UI_TOKENS.md',
    description: '颜色、间距、圆角、阴影、字体等 Design Tokens'
  },
  {
    icon: '🧩',
    name: '01_COMPONENT_LIBRARY.md',
    description: '所有基础组件规范（Button、Input、Card、Table等）'
  },
  {
    icon: '📐',
    name: '02_LAYOUT_RULES.md',
    description: '布局规则（页面骨架、表单/列表规范）'
  },
  {
    icon: '👆',
    name: '03_INTERACTION_RULES.md',
    description: '交互规范（错误态、禁用、按钮顺序等）'
  },
  {
    icon: '📄',
    name: '04_PAGE_TEMPLATES.md',
    description: '常用页面模板（列表页/表单页/详情页）'
  },
  {
    icon: '🔄',
    name: '05_WORKFLOW_TEMPLATES.md',
    description: '多步流程模板（创建向导、审批流）'
  }
])

// 六个阶段数据
const phases = ref([
  {
    name: 'Phase 1: 需求 & UI/UX',
    icon: '🎯',
    subtitle: '结构化需求和 UI 规格',
    goal: '把自然语言需求转化为机器可读的结构化说明，约束 UI 遵循全局规则',
    steps: [
      {
        title: '填写业务背景',
        description: '在 00_CONTEXT.md 中记录功能的业务背景、目标用户、约束条件',
        actions: [
          '描述要解决的问题',
          '明确目标用户',
          '列出业务和技术约束',
          '说明与现有系统的关系'
        ]
      },
      {
        title: '编写 UI Flow Spec',
        description: '按结构化模板填写 11_UI_FLOW_SPEC.md',
        actions: [
          '定义用户角色和流程',
          '描述交互逻辑（主流程 + 边界）',
          '划分页面结构和模块',
          '定义所有字段（类型、校验、错误提示）',
          '列出所有组件状态',
          '准备示例数据'
        ]
      },
      {
        title: 'Chat/Gemini 评审',
        description: '让 AI 检查并补充 UI Flow Spec',
        actions: [
          '上传 00_CONTEXT 和 11_UI_FLOW_SPEC',
          '要求 AI 检查完整性和合理性',
          '补充遗漏的边界条件和错误态',
          '确认符合 /_templates/_foundation_templates/_ui_system_template/ 规则'
        ]
      }
    ],
    template: {
      name: '11_UI_FLOW_SPEC.md',
      content: `# [功能名称] - UI Flow Spec

## 1. 背景 / 目标
TODO: 填写本功能解决的问题和目标

## 2. 用户角色（Roles）
- 角色1：描述
- 角色2：描述

## 3. 用户流程（User Flow）
1. 步骤1
2. 步骤2
3. 步骤3

## 4. 交互逻辑
### 主流程
- ...

### 边界条件
- ...

## 5. 页面结构（Page Structure）
- 模块1
- 模块2

## 6. 字段与组件
| 字段名 | 类型 | 必填 | 校验规则 | 错误提示 | 默认值 |
|--------|------|------|----------|----------|--------|
| ...    | ...  | ...  | ...      | ...      | ...    |

## 7. 组件状态
- loading / disabled / error / success

## 8. 边界条件 & 错误态
- 场景1：处理方式
- 场景2：处理方式

## 9. 示例数据（Mock Data）
\`\`\`json
{
  "example": "data"
}
\`\`\`

## 10. 输出要求
- 使用 React/Vue + Tailwind
- 严格遵守 /_templates/_foundation_templates/_ui_system_template/ 规范
- 只使用项目中的组件库`
    },
    tools: [
      {
        name: 'Chat/Gemini',
        description: '用于评审和完善 Spec',
        command: null
      }
    ],
    example: null
  },
  {
    name: 'Phase 2: Demo',
    icon: '🎨',
    subtitle: 'Chat → UI Demo',
    goal: '用 AI 快速生成可交互的 Demo，验证 UI/UX 设计',
    steps: [
      {
        title: '配置 ui_demo skill',
        description: '在 Claude Code 中配置 UI Demo 生成模式',
        actions: [
          '创建 ui_demo skill 配置',
          '指定读取 _ui_system_template 和 11_UI_FLOW_SPEC',
          '要求输出可运行的页面'
        ]
      },
      {
        title: 'Claude Code 生成 Demo',
        description: '让 Claude Code 根据 Spec 生成 Demo 代码',
        actions: [
          '运行 ui_demo skill',
          '生成到 /playgrounds/<feature-slug>/',
          '本地运行查看效果'
        ]
      },
      {
        title: '评审和调整',
        description: '检查 Demo 是否符合预期',
        actions: [
          '验证风格是否统一',
          '检查流程是否顺畅',
          '确认按钮/错误态/空态合理',
          '如需修改，先更新 Spec 再重新生成'
        ]
      }
    ],
    template: null,
    tools: [
      {
        name: 'Claude Code ui_demo skill',
        description: '自动生成 UI Demo',
        command: 'claude code --skill=ui_demo'
      }
    ],
    example: {
      title: '订阅状态组件 Demo',
      description: '根据 Spec 生成的订阅状态展示组件',
      code: `// 生成的 Demo 示例
<template>
  <div class="subscription-status">
    <div class="status-badge" :class="statusClass">
      {{ statusText }}
    </div>
    <div class="quota-info">
      <span>已用：{{ used }}</span>
      <span>总量：{{ total }}</span>
    </div>
  </div>
</template>`
    }
  },
  {
    name: 'Phase 3: 设计 & 计划',
    icon: '📐',
    subtitle: '技术设计和开发计划',
    goal: '确定技术方案，拆解开发任务',
    steps: [
      {
        title: '编写技术设计',
        description: 'Claude Code 生成 10_DESIGN_FINAL.md',
        actions: [
          '定义数据模型（DB 表结构/Types）',
          '设计 API（路径、方法、参数、返回）',
          '划分前后端分工',
          '设计状态管理',
          '规划错误处理和权限'
        ]
      },
      {
        title: 'Chat/Gemini 架构评审',
        description: '让 AI 评审技术方案',
        actions: [
          '上传 10_DESIGN_FINAL',
          '检查架构合理性',
          '识别潜在风险',
          '建议优化方案'
        ]
      },
      {
        title: '制定开发计划',
        description: '拆解任务并定义验证方式',
        actions: [
          '按阶段拆分（P1/P2/P3）',
          '每个任务定义验证方式',
          '标记依赖关系',
          '评估时间和风险'
        ]
      }
    ],
    template: {
      name: '20_DEV_PLAN_FINAL.md',
      content: `# [功能名称] - Dev Plan Final

## 开发任务清单

### P1 - 核心功能
- [ ] P1-DB: 创建数据表
      验证：Supabase MCP 查询表和字段
- [ ] P1-API: 实现核心 API
      验证：curl 调用返回正确结果

### P2 - 次要功能
- [ ] P2-FE: 前端页面实现
      验证：UI 与 Demo 一致

### P3 - 优化
- [ ] P3-OPT: 性能优化
      验证：响应时间 < 500ms

## 依赖关系
- P2 依赖 P1 完成
- P3 可并行开发

## 风险评估
- 风险1：缓解措施
- 风险2：缓解措施`
    },
    tools: [],
    example: null
  },
  {
    name: 'Phase 4: 开发执行',
    icon: '💻',
    subtitle: 'Progress Log + Review Subagent',
    goal: '按计划开发，用文件驱动而非对话记忆',
    steps: [
      {
        title: '初始化 Progress Log',
        description: '创建 30_PROGRESS_LOG.md',
        actions: [
          '从 DEV_PLAN 复制 Checklist',
          '标记所有任务为 [ ]',
          '记录初始状态'
        ]
      },
      {
        title: '开发循环',
        description: '每完成一个任务就更新 Progress Log',
        actions: [
          '读取 DEV_PLAN 和 PROGRESS_LOG',
          '确认当前任务',
          '编写代码',
          '本地和 MCP 验证',
          '调用 review_alignment skill',
          '更新 PROGRESS_LOG'
        ]
      },
      {
        title: '处理 Compact',
        description: '当上下文被压缩时强制跳回锚点',
        actions: [
          '检测到 compact 提示时停止',
          '重新读取 DEV_PLAN 和 PROGRESS_LOG',
          '明确声明当前状态',
          '从正确位置继续'
        ]
      }
    ],
    template: {
      name: '30_PROGRESS_LOG.md',
      content: `# Progress Log – [feature-slug]

## Checklist
- [ ] P1-DB: 创建数据表
- [ ] P1-API: 实现核心 API
- [ ] P2-FE: 前端页面实现

## History

### 2025-02-07
- 初始化开发计划
- NEXT STEP: 实现 P1-DB

### 2025-02-08
- 完成 P1-DB，表结构已创建
- NEXT STEP: 实现 P1-API`
    },
    tools: [
      {
        name: 'review_alignment skill',
        description: '自动更新 Progress Log',
        command: 'claude code --skill=review_alignment'
      }
    ],
    example: null
  },
  {
    name: 'Phase 5: 测试',
    icon: '🔍',
    subtitle: 'MCP 驱动的自动化测试',
    goal: '用 MCP 工具自动执行测试，确保质量',
    steps: [
      {
        title: '生成测试计划',
        description: 'Claude Code 根据 DEV_PLAN 生成测试用例',
        actions: [
          '后端测试：DB、RPC、API',
          '前端测试：页面、按钮、流程',
          '标记使用的 MCP 工具'
        ]
      },
      {
        title: '执行测试',
        description: '用 test_runner skill 自动跑测试',
        actions: [
          '读取 40_TEST_PLAN',
          '逐条用 MCP 执行',
          '记录通过/失败',
          '写入 41_TEST_REPORT'
        ]
      },
      {
        title: '修复问题',
        description: '根据测试结果修复 bug',
        actions: [
          '分析失败原因',
          '修复代码',
          '重新测试',
          '更新 Progress Log'
        ]
      }
    ],
    template: {
      name: '40_TEST_PLAN.md',
      content: `# [功能名称] - Test Plan

## 后端测试用例
- [ ] DB-001: 验证表结构
      工具：Supabase MCP
      步骤：查询 schema

- [ ] API-001: 测试创建接口
      工具：curl
      步骤：POST /api/xxx
      期望：200 + 数据写入

## 前端测试用例
- [ ] UI-001: 页面加载测试
      工具：Chrome Dev MCP
      步骤：打开页面
      期望：无错误，正确渲染`
    },
    tools: [
      {
        name: 'test_runner skill',
        description: '自动执行测试用例',
        command: 'claude code --skill=test_runner'
      },
      {
        name: 'Supabase MCP',
        description: '测试数据库和 API',
        command: null
      },
      {
        name: 'Chrome Dev MCP',
        description: '测试前端页面',
        command: null
      }
    ],
    example: null
  },
  {
    name: 'Phase 6: 发布',
    icon: '🚀',
    subtitle: '生成发布说明',
    goal: '汇总所有文档，生成发布说明',
    steps: [
      {
        title: '生成 Release Note',
        description: 'Claude Code 根据各阶段文档生成',
        actions: [
          '读取 DESIGN、PLAN、PROGRESS、TEST',
          '汇总功能点',
          '说明影响范围',
          '列出已知问题',
          '记录经验教训'
        ]
      },
      {
        title: '复盘会议',
        description: '团队复盘和经验总结',
        actions: [
          '回顾做得好的地方',
          '识别改进点',
          '更新团队流程文档'
        ]
      }
    ],
    template: {
      name: '50_RELEASE_NOTE.md',
      content: `# [功能名称] - Release Note

## 概要
本次迭代实现了 XXX 功能...

## 功能点
- 功能1：描述
- 功能2：描述

## 影响范围
- 前端：新增 3 个页面
- 后端：新增 5 个 API
- 数据库：新增 2 张表

## 已知问题
- 问题1：计划在下个版本修复
- 问题2：workaround 方案

## 后续计划
- TODO1
- TODO2

## 经验教训
### 做得好的地方
- 经验1
- 经验2

### 需要改进
- 改进点1
- 改进点2`
    },
    tools: [],
    example: null
  }
])

// Skills 配置
const skills = ref([
  {
    icon: '🎨',
    name: 'ui_demo',
    type: 'Skill',
    purpose: '根据 UI Flow Spec 自动生成可运行的 UI Demo',
    trigger: 'Phase 2 - 需要生成 Demo 时',
    config: `{
  "name": "ui_demo",
  "description": "Generate UI Demo from Spec",
  "prompt": "你是 UI System Architect。\\n生成的 UI 必须：\\n- 严格遵守 /_templates/_foundation_templates/_ui_system_template/ 规范\\n- 根据 /docs/<feature>/11_UI_FLOW_SPEC.md\\n- 只使用项目组件库，不写裸 div\\n- 输出完整可运行的页面",
  "actions": [
    "read_file: /_templates/_foundation_templates/_ui_system_template/*",
    "read_file: /docs/<feature>/11_UI_FLOW_SPEC.md",
    "write_file: /playgrounds/<feature>/DemoPage.tsx"
  ]
}`
  },
  {
    icon: '✅',
    name: 'review_alignment',
    type: 'Skill',
    purpose: '检查代码变更，更新 Progress Log',
    trigger: 'Phase 4 - 每完成一个开发任务时',
    config: `{
  "name": "review_alignment",
  "description": "Review and update Progress Log",
  "prompt": "读取 DEV_PLAN 和 PROGRESS_LOG\\n对照本轮代码变更\\n标记完成的任务\\n更新 Checklist 和 History\\n写明 NEXT STEP",
  "actions": [
    "read_file: /docs/<feature>/20_DEV_PLAN_FINAL.md",
    "read_file: /docs/<feature>/30_PROGRESS_LOG.md",
    "git_diff",
    "write_file: /docs/<feature>/30_PROGRESS_LOG.md"
  ]
}`
  },
  {
    icon: '🧪',
    name: 'test_runner',
    type: 'Skill',
    purpose: '自动执行测试用例，生成测试报告',
    trigger: 'Phase 5 - 代码开发完成，需要测试时',
    config: `{
  "name": "test_runner",
  "description": "Run tests and generate report",
  "prompt": "读取 TEST_PLAN\\n逐条用 MCP 执行测试\\n记录通过/失败\\n写入 TEST_REPORT",
  "actions": [
    "read_file: /docs/<feature>/40_TEST_PLAN.md",
    "mcp_supabase: query schema",
    "mcp_chrome: open page and test",
    "write_file: /docs/<feature>/41_TEST_REPORT.md"
  ]
}`
  },
  {
    icon: '🤖',
    name: 'main_agent',
    type: 'Agent',
    purpose: 'Claude Code 主 Agent，协调整个开发流程',
    trigger: '全流程',
    config: `{
  "name": "main_agent",
  "description": "Main development agent",
  "prompt": "你是 AI Product Engineer。\\n严格按照 /docs/<feature>/ 中的文档执行\\n每个阶段完成后调用相应 skill\\n遇到 compact 时强制跳回 PROGRESS_LOG",
  "skills": ["ui_demo", "review_alignment", "test_runner"],
  "context": [
    "/docs/<feature>/00_CONTEXT.md",
    "/docs/<feature>/30_PROGRESS_LOG.md"
  ]
}`
  }
])

// 脚本列表
const scripts = ref([
  {
    name: '功能初始化脚本',
    file: 'tools/init_feature.sh',
    description: '快速创建新功能的文档结构',
    usage: './tools/init_feature.sh subscription-billing-v3 "Subscription Billing V3"',
    code: `#!/usr/bin/env bash
# 用法: ./tools/init_feature.sh <feature-slug> "Feature Name"

set -e

FEATURE_SLUG=$1
FEATURE_NAME=$2

if [ -z "$FEATURE_SLUG" ] || [ -z "$FEATURE_NAME" ]; then
  echo "Usage: $0 <feature-slug> \\"Feature Name\\""
  exit 1
fi

BASE_DIR="docs/\${FEATURE_SLUG}"
mkdir -p "\${BASE_DIR}"

# 创建所有文档文件
cat > "\${BASE_DIR}/00_CONTEXT.md" <<EOF
# \${FEATURE_NAME} – Context

## 背景 / 目标
TODO: 填写功能背景

## 相关模块
- TODO

## 约束条件
- TODO
EOF

cat > "\${BASE_DIR}/11_UI_FLOW_SPEC.md" <<EOF
# \${FEATURE_NAME} – UI Flow Spec
TODO: 按模板填写
EOF

# ... 创建其他文件 ...

echo "✅ Initialized feature docs under \${BASE_DIR}"`
  },
  {
    name: '进度同步脚本',
    file: 'tools/sync_progress.sh',
    description: '同步 Progress Log 到项目管理工具',
    usage: './tools/sync_progress.sh subscription-billing-v3',
    code: `#!/usr/bin/env bash
# 同步 Progress Log 到 GitHub Issues / Jira

FEATURE_SLUG=$1
PROGRESS_FILE="docs/\${FEATURE_SLUG}/30_PROGRESS_LOG.md"

if [ ! -f "$PROGRESS_FILE" ]; then
  echo "Progress Log not found"
  exit 1
fi

# 解析 Checklist
# 更新 GitHub Issues
# ...

echo "✅ Progress synced"`
  },
  {
    name: 'Release Note 生成脚本',
    file: 'tools/generate_release_note.sh',
    description: '自动生成发布说明',
    usage: './tools/generate_release_note.sh subscription-billing-v3',
    code: `#!/usr/bin/env bash
# 根据各阶段文档自动生成 Release Note

FEATURE_SLUG=$1
DOCS_DIR="docs/\${FEATURE_SLUG}"

# 读取所有文档
CONTEXT=$(cat "\${DOCS_DIR}/00_CONTEXT.md")
DESIGN=$(cat "\${DOCS_DIR}/10_DESIGN_FINAL.md")
TEST=$(cat "\${DOCS_DIR}/41_TEST_REPORT.md")

# 用 LLM 生成 Release Note
# ...

echo "✅ Release Note generated"`
  }
])

// 实战案例
const caseStudy = ref([
  {
    phase: 'Phase 1: 需求 & UI/UX',
    duration: '2 天',
    description: '订阅计费系统需要展示用户的订阅状态、配额使用情况，并支持升级操作',
    deliverables: [
      '00_CONTEXT.md - 记录业务背景：SaaS 产品需要订阅管理',
      '11_UI_FLOW_SPEC.md - 详细的 UI 规格：订阅状态卡片、配额进度条、升级按钮等'
    ],
    highlights: [
      '用 Chat 评审 Spec，补充了"配额不足"的错误提示',
      '明确了三种订阅状态：Free/Pro/Enterprise'
    ]
  },
  {
    phase: 'Phase 2: Demo',
    duration: '1 天',
    description: '用 Claude Code 的 ui_demo skill 生成可交互的订阅状态页面',
    deliverables: [
      'Demo 代码：/playgrounds/subscription-billing-v3/SubscriptionCard.vue',
      '包含所有状态：激活、过期、配额不足'
    ],
    highlights: [
      'Demo 完全符合 Design System',
      '产品经理直接在 Demo 上确认交互流程'
    ]
  },
  {
    phase: 'Phase 3: 设计 & 计划',
    duration: '1 天',
    description: '技术方案：3 张表（subscriptions/orders/usage_logs）+ 5 个 API + 1 个 Edge Function',
    deliverables: [
      '10_DESIGN_FINAL.md - 完整的技术设计',
      '20_DEV_PLAN_FINAL.md - 拆分成 12 个开发任务'
    ],
    highlights: [
      'Gemini 评审建议增加"幂等性"处理',
      '识别风险：支付回调可能失败'
    ]
  },
  {
    phase: 'Phase 4: 开发执行',
    duration: '5 天',
    description: '按 DEV_PLAN 逐个任务开发，每完成一个就更新 Progress Log',
    deliverables: [
      '30_PROGRESS_LOG.md - 实时记录进度',
      '12 个任务全部完成，包括前后端代码'
    ],
    highlights: [
      '中途遇到 2 次 compact，都成功跳回锚点',
      'review_alignment skill 自动更新进度，节省大量时间'
    ]
  },
  {
    phase: 'Phase 5: 测试',
    duration: '2 天',
    description: '用 test_runner skill 自动跑测试，发现 3 个 P1 bug',
    deliverables: [
      '40_TEST_PLAN.md - 25 个测试用例',
      '41_TEST_REPORT.md - 通过率 88%，3 个 bug 已修复'
    ],
    highlights: [
      'Supabase MCP 验证数据库结构',
      'Chrome Dev MCP 自动测试前端流程'
    ]
  },
  {
    phase: 'Phase 6: 发布',
    duration: '0.5 天',
    description: '生成 Release Note，部署到生产环境',
    deliverables: [
      '50_RELEASE_NOTE.md - 发布说明',
      '复盘会议记录 - 团队经验总结'
    ],
    highlights: [
      '从需求到上线共 11.5 天',
      '代码质量高，上线后 0 bug'
    ]
  }
])

// 复制代码函数
const copyCode = (code) => {
  navigator.clipboard.writeText(code).then(() => {
    ElMessage.success('已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}
</script>

<style scoped>
.workflow-guide-page {
  min-height: 100%;
  background-color: var(--color-bg-page);
}

/* ========== Page Header ========== */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: var(--spacing-xxl) 0 var(--spacing-xl);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.page-header :deep(.el-breadcrumb__inner) {
  color: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.page-header :deep(.el-breadcrumb__inner:hover) {
  color: #fff;
}

.page-header :deep(.el-breadcrumb__separator) {
  color: rgba(255, 255, 255, 0.6);
}

.page-title {
  font-size: 36px;
  font-weight: var(--font-weight-bold);
  margin: var(--spacing-lg) 0 var(--spacing-sm);
  color: white;
  line-height: 1.2;
}

.page-subtitle {
  font-size: var(--font-size-lg);
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
}

/* ========== Guide Tabs ========== */
.guide-tabs {
  margin-top: 24px;
}

.guide-tabs :deep(.el-radio-button__inner) {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
  color: rgba(255, 255, 255, 0.9);
}

.guide-tabs :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: #fff;
  border-color: #fff;
  color: var(--primary-color);
  box-shadow: none;
}

/* ========== Page Content ========== */
.page-content {
  padding: var(--spacing-xxl) 0;
}

.content-section {
  margin-bottom: var(--spacing-xl);
  border-radius: var(--border-radius-lg);
  border: none;
  box-shadow: var(--shadow-base);
}

.content-section :deep(.el-card__body) {
  padding: var(--spacing-xxl);
}

.section-title {
  font-size: 24px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-sm);
  line-height: 1.3;
  border-left: 4px solid #667eea;
  padding-left: var(--spacing-md);
}

.section-desc {
  font-size: var(--font-size-md);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  margin-bottom: var(--spacing-xl);
}

/* ========== Intro Section ========== */
.intro-section {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border: 2px solid rgba(102, 126, 234, 0.2);
}

.intro-text {
  font-size: var(--font-size-md);
  line-height: 1.8;
  color: #374151;
  margin-bottom: var(--spacing-lg);
}

.intro-text .link {
  color: #667eea;
  text-decoration: underline;
  font-weight: 500;
}

.intro-features {
  display: flex;
  gap: var(--spacing-lg);
  flex-wrap: wrap;
  margin-top: var(--spacing-lg);
}

.feature-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  background: white;
  border-radius: var(--border-radius-base);
  border: 1px solid var(--color-border-light);
}

.feature-icon {
  font-size: 20px;
}

.feature-text {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

/* ========== Quick Start ========== */
.quick-start-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-lg);
}

.quick-start-card {
  background: white;
  border: 2px solid var(--color-border-light);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
  transition: all var(--transition-base);
}

.quick-start-card:hover {
  border-color: #667eea;
  box-shadow: var(--shadow-lg);
}

.qs-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.qs-icon {
  font-size: 32px;
}

.qs-title {
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.qs-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.qs-list li {
  font-size: 14px;
  color: #374151;
  line-height: 1.7;
  padding: var(--spacing-xs) 0;
  padding-left: var(--spacing-lg);
  position: relative;
}

.qs-list li::before {
  content: '▸';
  position: absolute;
  left: 0;
  color: #667eea;
  font-weight: 600;
}

.code-block-wrapper {
  position: relative;
}

.code-block {
  background: #1e293b;
  color: #e2e8f0;
  padding: var(--spacing-md);
  border-radius: var(--border-radius-base);
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
  margin: 0;
}

.copy-btn {
  position: absolute;
  top: var(--spacing-sm);
  right: var(--spacing-sm);
}

/* ========== File Structure ========== */
.file-structure-section {
  margin-bottom: var(--spacing-xxl);
}

.subsection-title {
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 var(--spacing-lg);
}

.file-tree {
  border: 1px solid var(--color-border-light);
  border-radius: var(--border-radius-base);
  overflow: hidden;
}

.file-item {
  border-bottom: 1px solid var(--color-border-light);
}

.file-item:last-child {
  border-bottom: none;
}

.file-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md) var(--spacing-lg);
  background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.file-header:hover {
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
}

.file-icon {
  font-size: 20px;
  color: #667eea;
}

.file-name {
  flex: 1;
  font-size: 15px;
  font-weight: 600;
  color: #111827;
  font-family: 'Monaco', 'Courier New', monospace;
}

.file-badge {
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  color: white;
}

.file-content {
  padding: var(--spacing-lg);
  background: white;
}

.file-desc {
  font-size: 14px;
  color: #374151;
  margin-bottom: var(--spacing-md);
}

.file-details {
  margin-top: var(--spacing-md);
}

.detail-label {
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
  margin-bottom: var(--spacing-sm);
}

.detail-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.detail-list li {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.6;
  padding: var(--spacing-xs) 0;
  padding-left: var(--spacing-lg);
  position: relative;
}

.detail-list li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: #667eea;
}

.ui-system-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-md);
  margin-top: var(--spacing-lg);
}

.ui-system-card {
  background: white;
  border: 1px solid var(--color-border-light);
  border-radius: var(--border-radius-base);
  padding: var(--spacing-md);
  transition: all var(--transition-base);
}

.ui-system-card:hover {
  border-color: #667eea;
  box-shadow: var(--shadow-base);
}

.ui-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}

.ui-icon {
  font-size: 24px;
}

.ui-title {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
  margin: 0;
  font-family: 'Monaco', 'Courier New', monospace;
}

.ui-desc {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.6;
  margin: 0;
}

/* ========== Phase Tabs ========== */
.phase-tabs {
  margin-top: var(--spacing-xl);
}

.phase-tabs :deep(.el-tabs__header) {
  margin-bottom: var(--spacing-xl);
}

.phase-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.tab-icon {
  font-size: 18px;
}

.tab-text {
  font-size: 14px;
}

.phase-content {
  padding: var(--spacing-lg) 0;
}

.phase-overview {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border-left: 4px solid #667eea;
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-base);
  margin-bottom: var(--spacing-xl);
}

.phase-title {
  font-size: 20px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 var(--spacing-sm);
}

.phase-goal {
  font-size: 15px;
  color: #374151;
  line-height: 1.7;
  margin: 0;
}

.phase-section {
  margin-bottom: var(--spacing-xl);
}

.phase-section-title {
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 var(--spacing-lg);
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.step-item {
  display: flex;
  gap: var(--spacing-md);
  background: white;
  border: 1px solid var(--color-border-light);
  border-radius: var(--border-radius-base);
  padding: var(--spacing-lg);
}

.step-number {
  width: 40px;
  height: 40px;
  background: #667eea;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-title {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 var(--spacing-xs);
}

.step-desc {
  font-size: 14px;
  color: #6b7280;
  line-height: 1.7;
  margin: 0 0 var(--spacing-sm);
}

.step-actions {
  list-style: none;
  padding: 0;
  margin: var(--spacing-sm) 0 0;
}

.step-actions li {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.6;
  padding: var(--spacing-xs) 0;
  padding-left: var(--spacing-lg);
  position: relative;
}

.step-actions li::before {
  content: '→';
  position: absolute;
  left: 0;
  color: #667eea;
  font-weight: 600;
}

.template-card,
.example-card {
  background: white;
  border: 1px solid var(--color-border-light);
  border-radius: var(--border-radius-base);
  overflow: hidden;
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md) var(--spacing-lg);
  background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
  border-bottom: 1px solid var(--color-border-light);
}

.template-name {
  font-size: 15px;
  font-weight: 600;
  color: #111827;
  font-family: 'Monaco', 'Courier New', monospace;
}

.template-content {
  background: #1e293b;
  color: #e2e8f0;
  padding: var(--spacing-lg);
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
  margin: 0;
  max-height: 400px;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-md);
}

.tool-card {
  background: white;
  border: 1px solid var(--color-border-light);
  border-radius: var(--border-radius-base);
  padding: var(--spacing-md);
}

.tool-name {
  font-size: 15px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 var(--spacing-xs);
}

.tool-desc {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.6;
  margin: 0 0 var(--spacing-sm);
}

.tool-command {
  background: #f3f4f6;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  font-family: 'Monaco', 'Courier New', monospace;
  font-size: 12px;
}

.example-title {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
}

.example-desc {
  font-size: 14px;
  color: #6b7280;
  line-height: 1.7;
  margin: 0;
  padding: 0 var(--spacing-lg) var(--spacing-md);
}

.example-code {
  background: #1e293b;
  padding: var(--spacing-lg);
}

.example-code pre {
  color: #e2e8f0;
  font-size: 13px;
  line-height: 1.6;
  margin: 0;
  overflow-x: auto;
}

/* ========== Skills ========== */
.skills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: var(--spacing-lg);
}

.skill-card {
  background: white;
  border: 2px solid var(--color-border-light);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
  transition: all var(--transition-base);
}

.skill-card:hover {
  border-color: #667eea;
  box-shadow: var(--shadow-lg);
}

.skill-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.skill-icon {
  font-size: 32px;
}

.skill-name {
  flex: 1;
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  margin: 0;
  font-family: 'Monaco', 'Courier New', monospace;
}

.skill-badge {
  padding: var(--spacing-xs) var(--spacing-sm);
  background: #667eea;
  color: white;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.skill-purpose,
.skill-trigger {
  font-size: 14px;
  color: #374151;
  line-height: 1.7;
  margin-bottom: var(--spacing-sm);
}

.skill-config {
  margin-top: var(--spacing-md);
  border: 1px solid var(--color-border-light);
  border-radius: var(--border-radius-base);
  overflow: hidden;
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
  border-bottom: 1px solid var(--color-border-light);
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
}

.config-code {
  background: #1e293b;
  color: #e2e8f0;
  padding: var(--spacing-md);
  font-size: 12px;
  line-height: 1.6;
  overflow-x: auto;
  margin: 0;
  max-height: 300px;
}

/* ========== Scripts ========== */
.scripts-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

.script-card {
  background: white;
  border: 2px solid var(--color-border-light);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-xl);
}

.script-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-md);
}

.script-info {
  flex: 1;
}

.script-name {
  font-size: 20px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 var(--spacing-xs);
}

.script-file {
  font-size: 13px;
  color: #6b7280;
  font-family: 'Monaco', 'Courier New', monospace;
}

.script-desc {
  font-size: 14px;
  color: #374151;
  line-height: 1.7;
  margin-bottom: var(--spacing-md);
}

.script-usage {
  font-size: 14px;
  margin-bottom: var(--spacing-md);
}

.script-usage code {
  background: #f3f4f6;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  font-family: 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  color: #111827;
}

.script-code-block {
  background: #1e293b;
  border-radius: var(--border-radius-base);
  padding: var(--spacing-lg);
  overflow-x: auto;
  max-height: 400px;
}

.script-code-block pre {
  color: #e2e8f0;
  font-size: 13px;
  line-height: 1.6;
  margin: 0;
}

/* ========== Case Study ========== */
.case-alert {
  margin-bottom: var(--spacing-xl);
}

.case-timeline {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

.case-step {
  background: white;
  border: 2px solid var(--color-border-light);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  transition: all var(--transition-base);
}

.case-step:hover {
  border-color: #667eea;
  box-shadow: var(--shadow-lg);
}

.case-step-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
  border-bottom: 2px solid var(--color-border-light);
}

.case-step-number {
  width: 48px;
  height: 48px;
  background: #667eea;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 600;
  flex-shrink: 0;
}

.case-step-info {
  flex: 1;
}

.case-step-title {
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 var(--spacing-xs);
}

.case-step-duration {
  font-size: 13px;
  color: #6b7280;
  font-weight: 500;
}

.case-step-content {
  padding: var(--spacing-xl);
}

.case-step-desc {
  font-size: 15px;
  color: #374151;
  line-height: 1.8;
  margin-bottom: var(--spacing-lg);
}

.case-deliverables,
.case-highlights {
  margin-bottom: var(--spacing-md);
}

.case-deliverables strong,
.case-highlights strong {
  font-size: 14px;
  color: #111827;
  display: block;
  margin-bottom: var(--spacing-sm);
}

.case-deliverables ul,
.case-highlights ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.case-deliverables li,
.case-highlights li {
  font-size: 14px;
  color: #6b7280;
  line-height: 1.7;
  padding: var(--spacing-xs) 0;
  padding-left: var(--spacing-lg);
  position: relative;
}

.case-deliverables li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #10b981;
  font-weight: 600;
}

.case-highlights li::before {
  content: '★';
  position: absolute;
  left: 0;
  color: #f59e0b;
}

/* ========== Bottom Navigation ========== */
.bottom-navigation {
  display: flex;
  justify-content: center;
  gap: var(--spacing-md);
  margin-top: var(--spacing-xxl);
  padding: var(--spacing-xl) 0;
}

/* ========== Responsive ========== */
@media (max-width: 768px) {
  .page-title {
    font-size: 24px;
  }

  .page-subtitle {
    font-size: var(--font-size-base);
  }

  .content-section :deep(.el-card__body) {
    padding: var(--spacing-lg);
  }

  .quick-start-grid,
  .ui-system-grid,
  .tools-grid,
  .skills-grid {
    grid-template-columns: 1fr;
  }

  .intro-features {
    flex-direction: column;
  }

  .bottom-navigation {
    flex-direction: column;
  }
}
</style>
