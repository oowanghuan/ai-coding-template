// Project Dashboard Data Types and Mock Data

// ============ Type Definitions ============

export type PhaseStatus = 'done' | 'wip' | 'delayed' | 'plan'
export type TaskPriority = 'critical' | 'ready' | 'running'

export interface Phase {
  id: number
  name: string
  status: PhaseStatus
  startPercent: number
  widthPercent: number
}

export interface Project {
  id: string
  name: string
  owner: string
  status: PhaseStatus
  phases: Phase[]
}

export interface AITask {
  id: string
  role: string
  priority: TaskPriority
  title: string
  description: string
}

export interface Role {
  name: string
  color: string
  icon: string
}

export interface FileRef {
  name: string
  path?: string
  isSystemRef: boolean
}

export interface Processor {
  agent: string
  skills: string[]
  workflow: string
  command: string
  logs: string[]
}

export interface Artifact {
  path: string
  versions: string[]
  currentVersion: number
  preview: string
}

export interface PhaseDetail {
  id: string
  role: Role
  objectives: string[]
  inputs: FileRef[]
  processor: Processor
  artifacts: Artifact[]
  fsTree: string
}

export interface FeatureData {
  featureId: string
  featureName: string
  phases: Record<string, PhaseDetail>
}

// ============ Mock Data ============

export const mockProjects: Project[] = [
  {
    id: 'cc-tools-library',
    name: 'Claude Code 工具库',
    owner: '@Huan',
    status: 'done',
    phases: [
      { id: 0, name: 'Foundation', status: 'done', startPercent: 0, widthPercent: 8 },
      { id: 1, name: 'Kickoff', status: 'done', startPercent: 8, widthPercent: 8 },
      { id: 2, name: 'Spec', status: 'done', startPercent: 16, widthPercent: 8 },
      { id: 3, name: 'Demo', status: 'done', startPercent: 24, widthPercent: 10 },
      { id: 4, name: 'Design', status: 'done', startPercent: 34, widthPercent: 10 },
      { id: 5, name: 'Code', status: 'done', startPercent: 44, widthPercent: 20 },
      { id: 6, name: 'Test', status: 'done', startPercent: 64, widthPercent: 10 },
      { id: 7, name: 'Deploy', status: 'done', startPercent: 74, widthPercent: 8 }
    ]
  },
  {
    id: 'gantt-dashboard',
    name: '甘特图看板',
    owner: '@Huan',
    status: 'done',
    phases: [
      { id: 0, name: 'Foundation', status: 'done', startPercent: 5, widthPercent: 8 },
      { id: 1, name: 'Kickoff', status: 'done', startPercent: 13, widthPercent: 8 },
      { id: 2, name: 'Spec', status: 'done', startPercent: 21, widthPercent: 8 },
      { id: 3, name: 'Demo', status: 'done', startPercent: 29, widthPercent: 10 },
      { id: 4, name: 'Design', status: 'done', startPercent: 39, widthPercent: 10 },
      { id: 5, name: 'Code', status: 'done', startPercent: 49, widthPercent: 20 },
      { id: 6, name: 'Test', status: 'done', startPercent: 69, widthPercent: 10 },
      { id: 7, name: 'Deploy', status: 'done', startPercent: 79, widthPercent: 8 }
    ]
  },
  {
    id: 'github-doc-viewer',
    name: 'GitHub 文档查看器',
    owner: '@Huan',
    status: 'done',
    phases: [
      { id: 0, name: 'Foundation', status: 'done', startPercent: 10, widthPercent: 8 },
      { id: 1, name: 'Kickoff', status: 'done', startPercent: 18, widthPercent: 8 },
      { id: 2, name: 'Spec', status: 'done', startPercent: 26, widthPercent: 8 },
      { id: 3, name: 'Demo', status: 'done', startPercent: 34, widthPercent: 10 },
      { id: 4, name: 'Design', status: 'done', startPercent: 44, widthPercent: 10 },
      { id: 5, name: 'Code', status: 'done', startPercent: 54, widthPercent: 20 },
      { id: 6, name: 'Test', status: 'done', startPercent: 74, widthPercent: 10 },
      { id: 7, name: 'Deploy', status: 'done', startPercent: 84, widthPercent: 8 }
    ]
  },
  {
    id: 'panorama-guide',
    name: '全景指南页面',
    owner: '@Huan',
    status: 'wip',
    phases: [
      { id: 0, name: 'Foundation', status: 'done', startPercent: 15, widthPercent: 8 },
      { id: 1, name: 'Kickoff', status: 'done', startPercent: 23, widthPercent: 8 },
      { id: 2, name: 'Spec', status: 'done', startPercent: 31, widthPercent: 8 },
      { id: 3, name: 'Demo', status: 'wip', startPercent: 39, widthPercent: 10 },
      { id: 4, name: 'Design', status: 'plan', startPercent: 49, widthPercent: 10 },
      { id: 5, name: 'Code', status: 'plan', startPercent: 59, widthPercent: 20 },
      { id: 6, name: 'Test', status: 'plan', startPercent: 79, widthPercent: 10 },
      { id: 7, name: 'Deploy', status: 'plan', startPercent: 89, widthPercent: 8 }
    ]
  },
  {
    id: 'project-dashboard-system',
    name: 'AI 协作开发框架',
    owner: '@Huan',
    status: 'wip',
    phases: [
      { id: 0, name: 'Foundation', status: 'wip', startPercent: 20, widthPercent: 8 },
      { id: 1, name: 'Kickoff', status: 'plan', startPercent: 28, widthPercent: 8 },
      { id: 2, name: 'Spec', status: 'plan', startPercent: 36, widthPercent: 8 },
      { id: 3, name: 'Demo', status: 'plan', startPercent: 44, widthPercent: 10 },
      { id: 4, name: 'Design', status: 'plan', startPercent: 54, widthPercent: 10 },
      { id: 5, name: 'Code', status: 'plan', startPercent: 64, widthPercent: 20 },
      { id: 6, name: 'Test', status: 'plan', startPercent: 84, widthPercent: 10 },
      { id: 7, name: 'Deploy', status: 'plan', startPercent: 94, widthPercent: 6 }
    ]
  }
]

export const mockAITasks: AITask[] = [
  {
    id: '1',
    role: 'AI PE',
    priority: 'running',
    title: 'Demo 完善',
    description: '全景指南页面 Phase 3 (Demo) 进行中，91% 完成。交互原型验证中。'
  },
  {
    id: '2',
    role: 'Architect',
    priority: 'ready',
    title: 'Foundation Setup',
    description: 'AI 协作开发框架 Phase 0 进行中，62% 完成。系统基础设施配置中。'
  },
  {
    id: '3',
    role: 'PM',
    priority: 'critical',
    title: 'Release Review',
    description: '3 个 Feature 已完成部署：Claude Code 工具库、甘特图看板、GitHub 文档查看器。'
  }
]

export const timelineWeeks = [
  { label: 'Nov W3', isCurrent: false },
  { label: 'Nov W4', isCurrent: false },
  { label: 'Dec W1', isCurrent: false },
  { label: 'Dec W2', isCurrent: true },
  { label: 'Dec W3', isCurrent: false }
]

// ============ Feature Detail Mock Data ============

const roleColors = {
  sys: '#8b5cf6',
  arch: '#6366f1',
  aip: '#f43f5e',
  dev: '#10b981',
  qa: '#f59e0b',
  pm: '#3b82f6'
}

export const mockFeatureData: Record<string, FeatureData> = {
  'subscription-v3': {
    featureId: 'subscription-v3',
    featureName: '订阅计费 V3',
    phases: {
      '0': {
        id: 'Foundation',
        role: { name: 'System Lead', color: roleColors.sys, icon: 'SYS' },
        objectives: ['定义全局 UI 规范', '配置基础设施', '建立自动化脚本'],
        inputs: [
          { name: 'Brand Guidelines', isSystemRef: false },
          { name: 'Tech Stack (Vue3+Supabase)', isSystemRef: false }
        ],
        processor: {
          agent: 'System_Architect_Agent',
          skills: ['System_Design', 'Scaffold_Gen'],
          workflow: 'foundation_setup',
          command: "/init-system --stack='Vue3'",
          logs: ['> Initializing project structure...', '> Generating UI Tokens...', '> System Foundation Ready.']
        },
        artifacts: [
          {
            path: '_templates/_foundation_templates/_ui_system_template/00_UI_TOKENS_TEMPLATE.md',
            versions: ['v1.0 (Init)', 'v1.1 (Dark Mode)'],
            currentVersion: 1,
            preview: '# UI Tokens v1.1\n- Primary: #6366f1\n- Bg: #0f172a\n- Font: Inter\n...'
          },
          {
            path: 'docs/00_PROJECT_CONTEXT.md',
            versions: ['v1.0'],
            currentVersion: 0,
            preview: '# Project Context\n- Name: SuperDev Platform\n- Stack: Vue3 + Supabase'
          }
        ],
        fsTree: '_templates/<br>├── <span class="fs-sys">_foundation_templates/_ui_system_template/ [6层规范]</span><br>docs/<br>├── <span class="fs-sys">00_PROJECT_CONTEXT.md [CREATED]</span>'
      },
      '1': {
        id: 'Feature Kickoff',
        role: { name: 'Architect', color: roleColors.arch, icon: 'AR' },
        objectives: ['引用系统规范', '定义业务边界', '设计 API 与 Schema'],
        inputs: [
          { name: 'User Feature Request', isSystemRef: false },
          { name: '_templates/_foundation_templates/_ui_system_template/*', path: '_templates/_foundation_templates/_ui_system_template/', isSystemRef: true },
          { name: 'docs/00_PROJECT_CONTEXT.md', isSystemRef: true }
        ],
        processor: {
          agent: 'Feature_Architect_Agent',
          skills: ['Context_Inheritance', 'Feature_Design'],
          workflow: 'feature_kickoff',
          command: "/kickoff --feature='Subscription'",
          logs: ['> Loading System Context...', '> Designing Schema...', '> Draft generated.']
        },
        artifacts: [
          {
            path: 'docs/subscription-v3/10_CONTEXT.md',
            versions: ['v0.9 (Draft)', 'v1.0 (Signed)'],
            currentVersion: 1,
            preview: '# Feature Context v1.0\n- Scope: Recurring Billing\n- Status: Approved by PM'
          },
          {
            path: 'docs/subscription-v3/40_DESIGN_FINAL.md',
            versions: ['v1.0 (Schema)', 'v1.1 (API Added)'],
            currentVersion: 1,
            preview: '# Design v1.1\n## Schema\n- subscriptions table\n## API\n- POST /api/subscribe'
          }
        ],
        fsTree: '_templates/<br>├── <span class="fs-sys">_foundation_templates/_ui_system_template/</span><br>docs/<br>└── subscription-v3/<br>&nbsp;&nbsp;&nbsp;&nbsp;├── <span class="fs-highlight">10_CONTEXT.md [NEW]</span><br>&nbsp;&nbsp;&nbsp;&nbsp;└── <span class="fs-highlight">40_DESIGN_FINAL.md [NEW]</span>'
      },
      '2': {
        id: 'Spec',
        role: { name: 'AI Product Engineer', color: roleColors.aip, icon: 'PE' },
        objectives: ['技术设计转 UI 流程', '定义交互规则'],
        inputs: [
          { name: 'docs/subscription-v3/40_DESIGN_FINAL.md', isSystemRef: false },
          { name: '_templates/_foundation_templates/_ui_system_template/04_PAGE_TEMPLATES_TEMPLATE.md', isSystemRef: true }
        ],
        processor: {
          agent: 'AIP_Agent',
          skills: ['Spec_Writer'],
          workflow: 'spec_gen',
          command: '/gen-spec --design=40_DESIGN_FINAL.md',
          logs: ['> Reading Design...', '> Applying Templates...', '> Generating Spec...']
        },
        artifacts: [
          {
            path: 'docs/subscription-v3/21_UI_FLOW_SPEC.md',
            versions: ['v0.1 (Raw)', 'v0.5 (Review)', 'v1.0 (Final)'],
            currentVersion: 2,
            preview: '# UI Flow v1.0\n- Page: /settings/plan\n- Action: Upgrade Plan\n- Error State: Insufficient Funds Modal'
          }
        ],
        fsTree: 'docs/<br>└── subscription-v3/<br>&nbsp;&nbsp;&nbsp;&nbsp;└── <span class="fs-highlight">21_UI_FLOW_SPEC.md [NEW]</span>'
      },
      '3': {
        id: 'Demo',
        role: { name: 'AI Product Engineer', color: roleColors.aip, icon: 'PE' },
        objectives: ['生成交互原型', '验证 UI Flow'],
        inputs: [
          { name: 'docs/subscription-v3/21_UI_FLOW_SPEC.md', isSystemRef: false },
          { name: '_templates/_foundation_templates/_ui_system_template/01_COMPONENT_LIBRARY_TEMPLATE.md', isSystemRef: true }
        ],
        processor: {
          agent: 'UI_Agent',
          skills: ['ui_demo_skill', 'Mock_Gen'],
          workflow: 'rapid_prototyping',
          command: '/gen-demo --spec=21_UI_FLOW_SPEC.md',
          logs: ['> Loading UI System...', '> Scaffolding Vue3...', '> Injecting Mock Data...']
        },
        artifacts: [
          {
            path: 'playgrounds/Demo.vue',
            versions: ['v1 (Layout)', 'v2 (Styled)', 'v3 (Interactive)'],
            currentVersion: 2,
            preview: '<template>\n  <PricingCard :plan="plan" @upgrade="handle" />\n</template>\n<script>\n  // Mock Logic v3\n</script>'
          }
        ],
        fsTree: 'playgrounds/<br>└── <span class="fs-highlight">Demo.vue [NEW]</span>'
      },
      '4': {
        id: 'Design',
        role: { name: 'UI Designer', color: '#3b82f6', icon: 'DS' },
        objectives: ['设计系统对齐', '组件库适配', '完成 UI 设计稿'],
        inputs: [
          { name: 'docs/subscription-v3/21_UI_FLOW_SPEC.md', isSystemRef: false },
          { name: 'playgrounds/Demo.vue', isSystemRef: false },
          { name: '_templates/_foundation_templates/_ui_system_template/00_UI_TOKENS_TEMPLATE.md', isSystemRef: true }
        ],
        processor: {
          agent: 'Design_Agent',
          skills: ['UI_Design', 'Component_Mapping', 'Style_System'],
          workflow: 'design_finalization',
          command: '/design --feature=subscription-v3',
          logs: ['> Loading UI System...', '> Mapping Components...', '> Generating Design Spec...', '> Design Ready.']
        },
        artifacts: [
          {
            path: 'docs/subscription-v3/40_DESIGN_FINAL.md',
            versions: ['v0.9 (Draft)', 'v1.0 (Final)'],
            currentVersion: 1,
            preview: '# Design Final v1.0\n## Component Mapping\n- PricingCard → el-card\n- PlanSelector → el-radio-group\n## Color Scheme\n- Primary: #6366f1'
          }
        ],
        fsTree: 'docs/<br>└── subscription-v3/<br>&nbsp;&nbsp;&nbsp;&nbsp;└── <span class="fs-highlight">40_DESIGN_FINAL.md [UPDATE]</span>'
      },
      '5': {
        id: 'Code',
        role: { name: 'Fullstack Dev', color: roleColors.dev, icon: 'DE' },
        objectives: ['实现 API & DB', '集成前端', '同步进度'],
        inputs: [
          { name: 'docs/subscription-v3/40_DESIGN_FINAL.md', isSystemRef: false },
          { name: 'playgrounds/Demo.vue', isSystemRef: false }
        ],
        processor: {
          agent: 'Fullstack_Agent',
          skills: ['API_impl', 'DB_Migration', 'Progress_Sync'],
          workflow: 'feature_implementation',
          command: '/implement --mode=fullstack',
          logs: ['> Generating Migrations...', '> Implementing API...', '> Refactoring Demo to Prod...', '> Syncing Log...']
        },
        artifacts: [
          {
            path: 'src/modules/subscription/*',
            versions: ['v0.1 (Scaffold)', 'v1.0 (Impl)'],
            currentVersion: 1,
            preview: "export const subscribe = async (id) => {\n  // Prod Implementation\n  return supabase.rpc('sub', { id });\n}"
          },
          {
            path: 'docs/subscription-v3/90_PROGRESS_LOG.md',
            versions: ['v1 (Start)', 'v5 (Completed)'],
            currentVersion: 1,
            preview: '# Progress Log\n- [x] DB Schema\n- [x] API\n- [x] UI Integration'
          }
        ],
        fsTree: 'src/<br>└── <span class="fs-highlight">modules/subscription/ [NEW]</span><br>docs/<br>└── <span class="fs-highlight">90_PROGRESS_LOG.md [UPDATE]</span>'
      },
      '6': {
        id: 'Test',
        role: { name: 'AI QA', color: roleColors.qa, icon: 'QA' },
        objectives: ['生成测试用例', '执行 E2E 测试', '报告 Bug'],
        inputs: [
          { name: 'docs/subscription-v3/21_UI_FLOW_SPEC.md', isSystemRef: false },
          { name: 'src/modules/subscription/*', isSystemRef: false }
        ],
        processor: {
          agent: 'QA_Agent',
          skills: ['Test_Gen', 'E2E_Runner'],
          workflow: 'qa_automation',
          command: '/test-run --target=subscription-v3',
          logs: ['> Generating Test Plan...', '> Running Playwright...', '> 14 Pass, 1 Fail.']
        },
        artifacts: [
          {
            path: 'docs/subscription-v3/60_TEST_PLAN.md',
            versions: ['v1.0'],
            currentVersion: 0,
            preview: '- Case 1: Upgrade Success\n- Case 2: Payment Fail'
          },
          {
            path: 'docs/subscription-v3/61_TEST_REPORT.md',
            versions: ['v1 (Fail)', 'v2 (Pass)'],
            currentVersion: 1,
            preview: '# Test Report v2\n- Total: 15\n- Passed: 15\n- Status: Ready'
          }
        ],
        fsTree: 'docs/<br>└── subscription-v3/<br>&nbsp;&nbsp;&nbsp;&nbsp;├── <span class="fs-highlight">60_TEST_PLAN.md</span><br>&nbsp;&nbsp;&nbsp;&nbsp;└── <span class="fs-highlight">61_TEST_REPORT.md</span>'
      },
      '7': {
        id: 'Deploy',
        role: { name: 'Project Manager', color: roleColors.pm, icon: 'PM' },
        objectives: ['汇总发布内容', '生成 Release Note', '上线'],
        inputs: [
          { name: 'docs/subscription-v3/90_PROGRESS_LOG.md', isSystemRef: false },
          { name: 'docs/subscription-v3/61_TEST_REPORT.md', isSystemRef: false }
        ],
        processor: {
          agent: 'PM_Agent',
          skills: ['Release_Manager', 'Doc_Summarizer'],
          workflow: 'deployment',
          command: '/release --version=v3.0.0',
          logs: ['> Summarizing changes...', '> Deploying to Prod...', '> Done.']
        },
        artifacts: [
          {
            path: 'docs/subscription-v3/70_RELEASE_NOTE.md',
            versions: ['v1.0'],
            currentVersion: 0,
            preview: '# Release v3.0.0\n## Features\n- Subscription Upgrades\n## Fixes\n- Mobile layout'
          }
        ],
        fsTree: 'docs/<br>└── <span class="fs-highlight">70_RELEASE_NOTE.md [NEW]</span>'
      }
    }
  }
}

// Real feature data based on PROGRESS_LOG.yaml files
mockFeatureData['cc-tools-library'] = {
  featureId: 'cc-tools-library',
  featureName: 'Claude Code 工具库',
  phases: { ...mockFeatureData['subscription-v3'].phases }
}

mockFeatureData['gantt-dashboard'] = {
  featureId: 'gantt-dashboard',
  featureName: '甘特图看板',
  phases: { ...mockFeatureData['subscription-v3'].phases }
}

mockFeatureData['github-doc-viewer'] = {
  featureId: 'github-doc-viewer',
  featureName: 'GitHub 文档查看器',
  phases: { ...mockFeatureData['subscription-v3'].phases }
}

mockFeatureData['panorama-guide'] = {
  featureId: 'panorama-guide',
  featureName: '全景指南页面',
  phases: { ...mockFeatureData['subscription-v3'].phases }
}

// 📚 AI 协作开发框架 - 作为样例项目，展示真实的框架工具和模板
mockFeatureData['project-dashboard-system'] = {
  featureId: 'project-dashboard-system',
  featureName: 'AI 协作开发框架（样例）',
  phases: {
    '0': {
      id: 'Foundation',
      role: { name: 'System Lead', color: roleColors.sys, icon: 'SYS' },
      objectives: ['建立项目级系统规范', '配置 UI 设计系统', '定义 API 和数据库约定'],
      inputs: [
        { name: '项目需求描述', isSystemRef: false },
        { name: '技术栈选型 (Vue3+Supabase)', isSystemRef: false }
      ],
      processor: {
        agent: 'System_Architect_Agent',
        skills: ['system_scaffolder', 'doc_generator'],
        workflow: 'foundation_setup',
        command: "/init-project --name='my-project'",
        logs: ['> 创建 _foundation 目录结构...', '> 生成 UI Tokens 规范...', '> 生成 API/DB 约定文档...', '> 系统基础设施就绪。']
      },
      artifacts: [
        {
          path: 'docs/_foundation/00_PROJECT_CONTEXT.md',
          versions: ['v1.0 (初始化)'],
          currentVersion: 0,
          preview: '# 项目上下文\n- 项目名: AI 协作开发框架\n- 技术栈: Vue3 + Supabase + Claude Code'
        },
        {
          path: '_templates/_foundation_templates/_ui_system_template/00_UI_TOKENS_TEMPLATE.md',
          versions: ['v1.0 (6层规范)'],
          currentVersion: 0,
          preview: '# UI 设计系统\n- 00_UI_TOKENS.md\n- 01_COMPONENT_LIBRARY.md\n- 02_LAYOUT_RULES.md\n- 03_INTERACTION_RULES.md\n- 04_PAGE_TEMPLATES.md\n- 05_WORKFLOW_TEMPLATES.md'
        },
        {
          path: 'docs/_foundation/02_API_CONVENTIONS.md',
          versions: ['v1.0'],
          currentVersion: 0,
          preview: '# API 约定\n- RESTful 命名规范\n- 错误码定义\n- 响应格式标准'
        }
      ],
      fsTree: '_templates/<br>└── _foundation_templates/<br>&nbsp;&nbsp;&nbsp;&nbsp;└── <span class="fs-sys">_ui_system_template/ [6层规范]</span><br>docs/<br>└── _foundation/<br>&nbsp;&nbsp;&nbsp;&nbsp;├── <span class="fs-sys">00_PROJECT_CONTEXT.md</span><br>&nbsp;&nbsp;&nbsp;&nbsp;├── <span class="fs-sys">02_API_CONVENTIONS.md</span><br>&nbsp;&nbsp;&nbsp;&nbsp;└── <span class="fs-sys">03_DB_CONVENTIONS.md</span>'
    },
    '1': {
      id: 'Feature Kickoff',
      role: { name: 'Architect', color: roleColors.arch, icon: 'AR' },
      objectives: ['创建功能模块目录', '定义功能上下文', '继承系统规范'],
      inputs: [
        { name: '用户功能需求', isSystemRef: false },
        { name: 'docs/_foundation/*', path: 'docs/_foundation/', isSystemRef: true },
        { name: '_templates/CC_COLLABORATION/03_TEMPLATES/', isSystemRef: true }
      ],
      processor: {
        agent: 'Feature_Architect_Agent',
        skills: ['context_writer', 'doc_generator'],
        workflow: 'feature_kickoff',
        command: "/new-feature --name='my-feature'",
        logs: ['> 创建功能目录 docs/my-feature/...', '> 继承系统上下文...', '> 生成 10_CONTEXT.md 框架...', '> 功能模块初始化完成。']
      },
      artifacts: [
        {
          path: 'docs/{feature}/10_CONTEXT.md',
          versions: ['v0.9 (草稿)', 'v1.0 (确认)'],
          currentVersion: 1,
          preview: '# 功能上下文\n## 背景\n## 目标\n## 范围边界\n## 技术约束\n## 团队分工'
        },
        {
          path: 'docs/{feature}/90_PROGRESS_LOG.yaml',
          versions: ['v1.0 (初始化)'],
          currentVersion: 0,
          preview: '# 进度日志\nmeta:\n  feature: my-feature\n  current_phase: 1\n  status: wip'
        }
      ],
      fsTree: 'docs/<br>├── _foundation/<br>└── {feature}/<br>&nbsp;&nbsp;&nbsp;&nbsp;├── <span class="fs-highlight">10_CONTEXT.md [NEW]</span><br>&nbsp;&nbsp;&nbsp;&nbsp;└── <span class="fs-highlight">90_PROGRESS_LOG.yaml [NEW]</span>'
    },
    '2': {
      id: 'Spec',
      role: { name: 'AI Product Engineer', color: roleColors.aip, icon: 'PE' },
      objectives: ['技术设计转 UI 流程', '定义页面交互规则', '输出可执行规格'],
      inputs: [
        { name: 'docs/{feature}/10_CONTEXT.md', isSystemRef: false },
        { name: '_templates/CC_COLLABORATION/03_TEMPLATES/21_UI_FLOW_SPEC_TEMPLATE.md', isSystemRef: true },
        { name: '_templates/CC_COLLABORATION/03_TEMPLATES/20_API_SPEC_TEMPLATE.md', isSystemRef: true }
      ],
      processor: {
        agent: 'spec_writer (Subagent)',
        skills: ['spec_validator'],
        workflow: 'spec_generation',
        command: '调用 spec_writer subagent',
        logs: ['> 读取功能上下文...', '> 应用 UI Flow 模板...', '> 生成交互规格说明...', '> Spec 完成。']
      },
      artifacts: [
        {
          path: 'docs/{feature}/21_UI_FLOW_SPEC.md',
          versions: ['v0.1 (初稿)', 'v0.5 (评审)', 'v1.0 (定稿)'],
          currentVersion: 2,
          preview: '# UI Flow Spec\n## 页面结构\n## 组件定义\n## 交互逻辑\n## 边界条件\n## 示例数据'
        },
        {
          path: 'docs/{feature}/20_API_SPEC.md',
          versions: ['v1.0'],
          currentVersion: 0,
          preview: '# API Spec\n## Endpoints\n## 请求/响应格式\n## 错误码'
        }
      ],
      fsTree: 'docs/<br>└── {feature}/<br>&nbsp;&nbsp;&nbsp;&nbsp;├── <span class="fs-highlight">21_UI_FLOW_SPEC.md [NEW]</span><br>&nbsp;&nbsp;&nbsp;&nbsp;└── <span class="fs-highlight">20_API_SPEC.md [NEW]</span>'
    },
    '3': {
      id: 'Demo',
      role: { name: 'AI Product Engineer', color: roleColors.aip, icon: 'PE' },
      objectives: ['生成交互原型', '创建 Mock API', '验证 UI Flow'],
      inputs: [
        { name: 'docs/{feature}/21_UI_FLOW_SPEC.md', isSystemRef: false },
        { name: '_templates/_foundation_templates/_ui_system_template/', isSystemRef: true }
      ],
      processor: {
        agent: 'UI_Demo_Agent',
        skills: ['ui_demo', 'mock_api_generator'],
        workflow: 'rapid_prototyping',
        command: "/gen-demo --spec='21_UI_FLOW_SPEC.md'",
        logs: ['> 加载 UI 设计系统...', '> 生成 Vue3 组件...', '> 注入 Mock 数据...', '> Demo 就绪。']
      },
      artifacts: [
        {
          path: 'playgrounds/{feature}/Demo.vue',
          versions: ['v1 (布局)', 'v2 (样式)', 'v3 (交互)'],
          currentVersion: 2,
          preview: '<template>\n  <div class="demo-container">\n    <!-- 原型组件 -->\n  </div>\n</template>'
        },
        {
          path: 'playgrounds/{feature}/mock/api.js',
          versions: ['v1.0'],
          currentVersion: 0,
          preview: '// Mock API\nexport const mockData = {...}'
        }
      ],
      fsTree: 'playgrounds/<br>└── {feature}/<br>&nbsp;&nbsp;&nbsp;&nbsp;├── <span class="fs-highlight">Demo.vue [NEW]</span><br>&nbsp;&nbsp;&nbsp;&nbsp;└── mock/<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── <span class="fs-highlight">api.js [NEW]</span>'
    },
    '4': {
      id: 'Design',
      role: { name: 'UI Designer', color: '#3b82f6', icon: 'DS' },
      objectives: ['设计系统对齐', '组件库适配', '完成详细设计'],
      inputs: [
        { name: 'docs/{feature}/21_UI_FLOW_SPEC.md', isSystemRef: false },
        { name: 'playgrounds/{feature}/Demo.vue', isSystemRef: false },
        { name: '_templates/_foundation_templates/_ui_system_template/', isSystemRef: true }
      ],
      processor: {
        agent: 'Design_Agent',
        skills: ['design_from_demo', 'schema_generator'],
        workflow: 'design_finalization',
        command: '调用 design_from_demo skill',
        logs: ['> 分析 Demo 组件...', '> 映射到设计系统...', '> 生成详细设计文档...', '> 设计完成。']
      },
      artifacts: [
        {
          path: 'docs/{feature}/40_DESIGN.md',
          versions: ['v0.9 (草稿)', 'v1.0 (定稿)'],
          currentVersion: 1,
          preview: '# 详细设计\n## 架构图\n## API 契约\n## 数据模型\n## 组件映射'
        }
      ],
      fsTree: 'docs/<br>└── {feature}/<br>&nbsp;&nbsp;&nbsp;&nbsp;└── <span class="fs-highlight">40_DESIGN.md [NEW]</span>'
    },
    '5': {
      id: 'Code',
      role: { name: 'Fullstack Dev', color: roleColors.dev, icon: 'DE' },
      objectives: ['实现 API & DB', '集成前端组件', '同步进度日志'],
      inputs: [
        { name: 'docs/{feature}/40_DESIGN.md', isSystemRef: false },
        { name: 'playgrounds/{feature}/Demo.vue', isSystemRef: false }
      ],
      processor: {
        agent: 'Fullstack_Agent',
        skills: ['progress_updater', 'review_alignment'],
        workflow: 'feature_implementation',
        command: "/start-day → 开发 → /end-day",
        logs: ['> /start-day: 恢复上下文...', '> 实现功能代码...', '> 更新 PROGRESS_LOG...', '> /end-day: 提交代码。']
      },
      artifacts: [
        {
          path: 'src/modules/{feature}/*',
          versions: ['v0.1 (脚手架)', 'v1.0 (实现)'],
          currentVersion: 1,
          preview: '// 生产代码实现\nexport const feature = () => {...}'
        },
        {
          path: 'docs/{feature}/90_PROGRESS_LOG.yaml',
          versions: ['v1 (开始)', 'v5 (完成)'],
          currentVersion: 1,
          preview: '# 进度日志\nphase_5_code:\n  status: done\n  tasks:\n    - [x] API 实现\n    - [x] 前端集成'
        }
      ],
      fsTree: 'src/<br>└── <span class="fs-highlight">modules/{feature}/ [NEW]</span><br>docs/<br>└── <span class="fs-highlight">90_PROGRESS_LOG.yaml [UPDATE]</span>'
    },
    '6': {
      id: 'Test',
      role: { name: 'AI QA', color: roleColors.qa, icon: 'QA' },
      objectives: ['生成测试计划', '执行 E2E 测试', '输出测试报告'],
      inputs: [
        { name: 'docs/{feature}/21_UI_FLOW_SPEC.md', isSystemRef: false },
        { name: 'src/modules/{feature}/*', isSystemRef: false }
      ],
      processor: {
        agent: 'test_plan_writer (Subagent)',
        skills: ['test_runner', 'test_report_generator'],
        workflow: 'qa_automation',
        command: "/run-tests --feature='{feature}'",
        logs: ['> 生成测试计划...', '> 执行 Vitest 测试...', '> 14 通过, 1 失败...', '> 修复后全部通过。']
      },
      artifacts: [
        {
          path: 'docs/{feature}/60_TEST_PLAN.md',
          versions: ['v1.0'],
          currentVersion: 0,
          preview: '# 测试计划\n- Case 1: 正常流程\n- Case 2: 边界条件\n- Case 3: 异常处理'
        },
        {
          path: 'docs/{feature}/61_TEST_REPORT.md',
          versions: ['v1 (失败)', 'v2 (通过)'],
          currentVersion: 1,
          preview: '# 测试报告\n- 总计: 15\n- 通过: 15\n- 状态: 就绪'
        }
      ],
      fsTree: 'docs/<br>└── {feature}/<br>&nbsp;&nbsp;&nbsp;&nbsp;├── <span class="fs-highlight">60_TEST_PLAN.md [NEW]</span><br>&nbsp;&nbsp;&nbsp;&nbsp;└── <span class="fs-highlight">61_TEST_REPORT.md [NEW]</span>'
    },
    '7': {
      id: 'Deploy',
      role: { name: 'Project Manager', color: roleColors.pm, icon: 'PM' },
      objectives: ['汇总发布内容', '生成 Release Note', '完成发布'],
      inputs: [
        { name: 'docs/{feature}/90_PROGRESS_LOG.yaml', isSystemRef: false },
        { name: 'docs/{feature}/61_TEST_REPORT.md', isSystemRef: false }
      ],
      processor: {
        agent: 'release_summarizer (Subagent)',
        skills: ['changelog_updater'],
        workflow: 'deployment',
        command: "/release --version='v1.0.0'",
        logs: ['> 汇总变更内容...', '> 生成 Release Note...', '> 创建 Git Tag...', '> 发布完成。']
      },
      artifacts: [
        {
          path: 'docs/{feature}/70_RELEASE_NOTE.md',
          versions: ['v1.0.0'],
          currentVersion: 0,
          preview: '# Release v1.0.0\n## 新功能\n- 功能描述\n## 修复\n- Bug 修复\n## 已知问题'
        }
      ],
      fsTree: 'docs/<br>└── {feature}/<br>&nbsp;&nbsp;&nbsp;&nbsp;└── <span class="fs-highlight">70_RELEASE_NOTE.md [NEW]</span>'
    }
  }
}
