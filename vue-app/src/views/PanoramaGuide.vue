<template>
  <div class="panorama-guide">
    <!-- 侧边导航点 -->
    <div class="section-nav">
      <div
        v-for="(section, index) in sections"
        :key="index"
        class="nav-dot"
        :class="{ active: currentSection === index }"
        @click="scrollToSection(index)"
      >
        <el-tooltip :content="section.title" placement="left">
          <span></span>
        </el-tooltip>
      </div>
    </div>

    <!-- Section 1: 痛点共鸣 -->
    <section ref="section0" class="guide-section section-pain-points">
      <div class="section-content">
        <h1 class="main-title">Vibe Coding 两年后，我们知道你不知道你不知道</h1>
        <p class="main-subtitle">"AI 写代码很快，但...文档乱拉x、功能越改越乱、compact 就忘、前后端字段对不齐"</p>

        <div class="pain-points-grid">
          <div class="pain-card">
            <div class="pain-icon">
              <el-icon :size="32"><Warning /></el-icon>
            </div>
            <h3>上下文丢失</h3>
            <p>每次都要重新解释背景，AI 不记得之前说过什么</p>
          </div>

          <div class="pain-card">
            <div class="pain-icon">
              <el-icon :size="32"><QuestionFilled /></el-icon>
            </div>
            <h3>进度不可见</h3>
            <p>不知道做到哪了，无法断点续作，换人接手困难</p>
          </div>

          <div class="pain-card">
            <div class="pain-icon">
              <el-icon :size="32"><SwitchFilled /></el-icon>
            </div>
            <h3>协作混乱</h3>
            <p>人和 AI 职责边界不清，不知道谁该做什么</p>
          </div>

          <div class="pain-card">
            <div class="pain-icon">
              <el-icon :size="32"><CircleCloseFilled /></el-icon>
            </div>
            <h3>质量失控</h3>
            <p>没有评审和测试流程，代码质量难以保证</p>
          </div>
        </div>

        <div class="scroll-hint" @click="scrollToSection(1)">
          <p>我们的解决方案</p>
          <el-icon class="bounce"><ArrowDown /></el-icon>
        </div>
      </div>
    </section>

    <!-- Section 2: 8 阶段流程全景 -->
    <section ref="section1" class="guide-section section-workflow">
      <div class="section-content">
        <h2 class="section-title">8 阶段工作流全景</h2>
        <p class="section-subtitle">每个阶段有明确的目标、模板和工具，人机协作分工清晰</p>

        <div class="phases-container">
          <!-- 第一行 Phase 0-4 -->
          <div class="phases-row">
            <div
              v-for="phase in phases.slice(0, 5)"
              :key="phase.id"
              class="phase-card"
              :class="{ expanded: expandedPhase === phase.id }"
              @click="togglePhase(phase.id)"
            >
              <div class="phase-header">
                <div class="phase-number">{{ phase.id }}</div>
                <div class="phase-info">
                  <div class="phase-name">{{ phase.name }}</div>
                  <div class="phase-name-cn">{{ phase.nameCn }}</div>
                </div>
              </div>

              <div class="phase-details" v-show="expandedPhase === phase.id">
                <div class="detail-section">
                  <div class="detail-label">目标</div>
                  <div class="detail-content">{{ phase.goal }}</div>
                </div>

                <div class="detail-section detail-what" v-if="phase.details?.what?.length">
                  <div class="detail-label">做什么</div>
                  <ul class="detail-list">
                    <li v-for="(item, idx) in phase.details.what" :key="idx">{{ item }}</li>
                  </ul>
                </div>

                <div class="detail-section detail-why" v-if="phase.details?.why?.length">
                  <div class="detail-label">为什么</div>
                  <ul class="detail-list">
                    <li v-for="(item, idx) in phase.details.why" :key="idx">{{ item }}</li>
                  </ul>
                </div>

                <div class="detail-section detail-value" v-if="phase.details?.value?.length">
                  <div class="detail-label">价值</div>
                  <ul class="detail-list">
                    <li v-for="(item, idx) in phase.details.value" :key="idx">{{ item }}</li>
                  </ul>
                </div>

                <div class="detail-section" v-if="phase.templates.length">
                  <div class="detail-label">模板</div>
                  <div class="detail-tags">
                    <el-tag v-for="t in phase.templates" :key="t" size="small" type="info">
                      {{ t }}
                    </el-tag>
                  </div>
                </div>

                <div class="detail-section" v-if="phase.tools.slashCommands.length">
                  <div class="detail-label">Slash Commands</div>
                  <div class="detail-tags">
                    <el-tag v-for="t in phase.tools.slashCommands" :key="t" size="small" type="success">
                      {{ t }}
                    </el-tag>
                  </div>
                </div>

                <div class="detail-section" v-if="phase.tools.skills.length">
                  <div class="detail-label">Skills</div>
                  <div class="detail-tags">
                    <el-tag v-for="t in phase.tools.skills" :key="t" size="small" type="warning">
                      {{ t }}
                    </el-tag>
                  </div>
                </div>
              </div>

              <div class="phase-arrow" v-if="phase.id < 4">
                <el-icon><ArrowRight /></el-icon>
              </div>
            </div>
          </div>

          <!-- 第二行 Phase 5-7 -->
          <div class="phases-row phases-row-bottom">
            <div
              v-for="phase in phases.slice(5)"
              :key="phase.id"
              class="phase-card"
              :class="{ expanded: expandedPhase === phase.id }"
              @click="togglePhase(phase.id)"
            >
              <div class="phase-header">
                <div class="phase-number">{{ phase.id }}</div>
                <div class="phase-info">
                  <div class="phase-name">{{ phase.name }}</div>
                  <div class="phase-name-cn">{{ phase.nameCn }}</div>
                </div>
              </div>

              <div class="phase-details" v-show="expandedPhase === phase.id">
                <div class="detail-section">
                  <div class="detail-label">目标</div>
                  <div class="detail-content">{{ phase.goal }}</div>
                </div>

                <div class="detail-section detail-what" v-if="phase.details?.what?.length">
                  <div class="detail-label">做什么</div>
                  <ul class="detail-list">
                    <li v-for="(item, idx) in phase.details.what" :key="idx">{{ item }}</li>
                  </ul>
                </div>

                <div class="detail-section detail-why" v-if="phase.details?.why?.length">
                  <div class="detail-label">为什么</div>
                  <ul class="detail-list">
                    <li v-for="(item, idx) in phase.details.why" :key="idx">{{ item }}</li>
                  </ul>
                </div>

                <div class="detail-section detail-value" v-if="phase.details?.value?.length">
                  <div class="detail-label">价值</div>
                  <ul class="detail-list">
                    <li v-for="(item, idx) in phase.details.value" :key="idx">{{ item }}</li>
                  </ul>
                </div>

                <div class="detail-section" v-if="phase.templates.length">
                  <div class="detail-label">模板</div>
                  <div class="detail-tags">
                    <el-tag v-for="t in phase.templates" :key="t" size="small" type="info">
                      {{ t }}
                    </el-tag>
                  </div>
                </div>

                <div class="detail-section" v-if="phase.tools.slashCommands.length">
                  <div class="detail-label">Slash Commands</div>
                  <div class="detail-tags">
                    <el-tag v-for="t in phase.tools.slashCommands" :key="t" size="small" type="success">
                      {{ t }}
                    </el-tag>
                  </div>
                </div>

                <div class="detail-section" v-if="phase.tools.skills.length">
                  <div class="detail-label">Skills</div>
                  <div class="detail-tags">
                    <el-tag v-for="t in phase.tools.skills" :key="t" size="small" type="warning">
                      {{ t }}
                    </el-tag>
                  </div>
                </div>
              </div>

              <div class="phase-arrow" v-if="phase.id < 7">
                <el-icon><ArrowRight /></el-icon>
              </div>
            </div>
          </div>
        </div>

        <p class="click-hint">点击任意阶段查看详情</p>

        <div class="scroll-hint" @click="scrollToSection(2)">
          <p>开始使用</p>
          <el-icon class="bounce"><ArrowDown /></el-icon>
        </div>
      </div>
    </section>

    <!-- Section 3: 搭建项目 -->
    <section ref="section2" class="guide-section section-setup">
      <div class="section-content">
        <h2 class="section-title">搭建你的项目</h2>
        <p class="section-subtitle">3 步完成环境准备</p>

        <div class="setup-steps-row">
          <div class="setup-step">
            <div class="step-number">1</div>
            <h3>Clone 克隆仓库</h3>
            <div class="command-box">
              <code>git clone https://github.com/oowanghuan/ai-coding-org.git</code>
              <el-button type="primary" size="small" @click="copyCommand('git clone https://github.com/oowanghuan/ai-coding-org.git')">
                <el-icon><CopyDocument /></el-icon>
              </el-button>
            </div>
          </div>

          <div class="setup-step">
            <div class="step-number">2</div>
            <h3>Install 安装 Claude 工具</h3>
            <div class="command-box">
              <code>./scripts/init-claude-tools.sh --target=.</code>
              <el-button type="primary" size="small" @click="copyCommand('./scripts/init-claude-tools.sh --target=.')">
                <el-icon><CopyDocument /></el-icon>
              </el-button>
            </div>
          </div>

          <div class="setup-step">
            <div class="step-number">3</div>
            <h3>Run 启动看板</h3>
            <div class="command-box">
              <code>cd vue-app && npm install && npm run dev</code>
              <el-button type="primary" size="small" @click="copyCommand('cd vue-app && npm install && npm run dev')">
                <el-icon><CopyDocument /></el-icon>
              </el-button>
            </div>
            <p class="step-note">访问 http://localhost:5173</p>
          </div>
        </div>

        <div class="setup-info-row">
          <div class="directory-tree">
            <h4>目录结构</h4>
            <pre>├── .claude/commands/   ← Slash Commands
├── _templates/         ← 模板库（核心）
├── docs/               ← 功能文档
├── vue-app/            ← 看板应用
└── scripts/            ← 工具脚本</pre>
          </div>

          <div class="github-config">
            <h4>看板配置</h4>
            <p class="config-desc">看板从 GitHub 实时读取仓库文档，需配置：</p>
            <ol class="config-steps">
              <li>复制 <code>.env.example</code> 为 <code>.env</code></li>
              <li>填写你的 Supabase 项目 URL 和 Key</li>
              <li>修改 <code>src/config/github.ts</code> 中的仓库信息</li>
            </ol>
            <p class="config-note">Supabase Edge Function 用于代理 GitHub API 请求</p>
          </div>
        </div>

        <div class="scroll-hint" @click="scrollToSection(3)">
          <p>创建第一个功能</p>
          <el-icon class="bounce"><ArrowDown /></el-icon>
        </div>
      </div>
    </section>

    <!-- Section 4: 创建第一个功能 -->
    <section ref="section3" class="guide-section section-first-feature">
      <div class="section-content">
        <h2 class="section-title">创建你的第一个功能</h2>
        <p class="section-subtitle">在 Claude Code 中执行</p>

        <div class="feature-grid">
          <div class="feature-left">
            <div class="command-box large">
              <code>/new-feature my-login</code>
              <el-button type="primary" size="small" @click="copyCommand('/new-feature my-login')">
                <el-icon><CopyDocument /></el-icon>
              </el-button>
            </div>
            <div class="feature-result">
              <pre>docs/my-login/
├── 10_CONTEXT.md        ← 待填写
└── 90_PROGRESS_LOG.yaml ← 自动更新</pre>
            </div>
          </div>

          <div class="feature-right">
            <h4>接下来</h4>
            <ol>
              <li>填写 <code>10_CONTEXT.md</code></li>
              <li>进入 Phase 2 编写规格</li>
              <li>按 8 阶段流程推进</li>
            </ol>
            <div class="daily-workflow">
              <el-tag type="success" size="small">/start-day</el-tag>
              <el-tag type="warning" size="small">/end-day</el-tag>
            </div>
          </div>
        </div>

        <div class="scroll-hint" @click="scrollToSection(4)">
          <p>项目看板</p>
          <el-icon class="bounce"><ArrowDown /></el-icon>
        </div>
      </div>
    </section>

    <!-- Section 5: Dashboard 看板 -->
    <section ref="section4" class="guide-section section-dashboard">
      <div class="section-content">
        <h2 class="section-title">项目看板</h2>
        <p class="section-subtitle">AI 既写代码也写日报，好用听话的强力下属</p>

        <div class="dashboard-layout">
          <!-- 左侧：看板截图 -->
          <div class="dashboard-screenshot">
            <img src="/images/dashboard-preview.png" alt="项目看板预览" />
          </div>

          <!-- 右侧：核心价值 -->
          <div class="dashboard-values">
            <div class="value-highlight">
              <div class="value-icon">🔄</div>
              <div class="value-content">
                <h3>自动同步更新</h3>
                <p>每天执行 <code>/start-day</code> 和 <code>/end-day</code>，进度自动同步到看板和 GitHub，无需手动汇报</p>
              </div>
            </div>

            <div class="value-highlight">
              <div class="value-icon">🔗</div>
              <div class="value-content">
                <h3>GitHub 深度集成</h3>
                <p>Issue、PR、Branch 状态实时同步，一个界面掌握所有动态</p>
              </div>
            </div>

            <div class="value-highlight">
              <div class="value-icon">👥</div>
              <div class="value-content">
                <h3>团队透明协作</h3>
                <p>谁在做什么、做到哪了，一目了然，交接无缝</p>
              </div>
            </div>

            <div class="value-highlight">
              <div class="value-icon">📝</div>
              <div class="value-content">
                <h3>文档一键直达</h3>
                <p>Context、Spec、Design 等文档直接查看，无需翻目录</p>
              </div>
            </div>
          </div>
        </div>

        <div class="scroll-hint" @click="scrollToSection(5)">
          <p>选择你的角色</p>
          <el-icon class="bounce"><ArrowDown /></el-icon>
        </div>
      </div>
    </section>

    <!-- Section 6: 角色入口 -->
    <section ref="section5" class="guide-section section-roles">
      <div class="section-content">
        <h2 class="section-title">选择你的角色</h2>
        <p class="section-subtitle">不同角色关注不同阶段和工具</p>

        <div class="roles-grid">
          <div class="role-card" v-for="role in roles" :key="role.id">
            <div class="role-icon">{{ role.icon }}</div>
            <h3>{{ role.name }}</h3>

            <div class="role-section" v-if="role.focusPhases.length">
              <div class="role-label">关注阶段</div>
              <ul>
                <li v-for="p in role.focusPhases" :key="p">
                  Phase {{ p }} {{ phases[p].nameCn }}
                </li>
              </ul>
            </div>

            <div class="role-section" v-if="role.tools.length">
              <div class="role-label">常用工具</div>
              <ul>
                <li v-for="t in role.tools" :key="t">{{ t }}</li>
              </ul>
            </div>

            <div class="role-section" v-if="role.tips">
              <div class="role-label">{{ role.tipsLabel }}</div>
              <ul>
                <li v-for="(tip, idx) in role.tips" :key="idx">{{ tip }}</li>
              </ul>
            </div>

            <el-button
              type="primary"
              class="role-action"
              @click="navigateToRole(role)"
            >
              {{ role.actionLabel }}
            </el-button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Warning,
  QuestionFilled,
  SwitchFilled,
  CircleCloseFilled,
  ArrowDown,
  ArrowRight,
  CopyDocument
} from '@element-plus/icons-vue'

const router = useRouter()

// 当前激活的 section
const currentSection = ref(0)
const expandedPhase = ref(null)

// Section refs
const section0 = ref(null)
const section1 = ref(null)
const section2 = ref(null)
const section3 = ref(null)
const section4 = ref(null)
const section5 = ref(null)

const sections = [
  { title: '痛点共鸣', ref: section0 },
  { title: '工作流全景', ref: section1 },
  { title: '搭建项目', ref: section2 },
  { title: '创建功能', ref: section3 },
  { title: '项目看板', ref: section4 },
  { title: '角色入口', ref: section5 }
]

// 8 阶段数据
const phases = [
  {
    id: 0,
    name: 'Kickoff',
    nameCn: '功能初始化',
    goal: '一条命令创建功能目录，自动生成标准文档结构（Context / Spec / Design / Test / Release）。避免重复劳动，确保所有功能遵循统一规范。',
    details: {
      what: [
        '执行标准化命令：/new-feature user-login',
        '自动创建目录结构：10_CONTEXT.md / 11_SPEC.md / 40_DESIGN.md ...',
        '自动生成文档模板和可编辑占位符',
        '自动登记任务 ID、负责人、上下游依赖'
      ],
      why: [
        '消除"从零开始"的混乱与浪费',
        '确保所有功能在开始阶段就站在同一标准上',
        '避免遗漏文档、结构不一致、命名混乱等问题'
      ],
      value: [
        '开发启动成本接近 0',
        '所有功能天然标准化',
        '后续 AI 处理文档更准确，团队协作更可控'
      ]
    },
    templates: [],
    tools: {
      slashCommands: ['/new-feature'],
      skills: [],
      subagents: []
    }
  },
  {
    id: 1,
    name: 'Context',
    nameCn: '背景/目标/范围',
    goal: '写清楚「为什么做」「做什么」「不做什么」。这是 AI 理解需求的基础，也是团队对齐的起点。好的上下文 = AI 更少幻觉 + 团队更少返工。',
    details: {
      what: [
        '描述业务背景、用户场景',
        '明确本次功能的目标与成功标准',
        '写清楚 Out of Scope（本次不做什么）',
        '明确边界条件、依赖项、风险点'
      ],
      why: [
        'AI 和团队都必须知道"问题的来龙去脉"才能做对事',
        '上下文不清是返工、跑偏、误解的最大来源',
        'Boundaries（边界）是控制范围和节省预算的关键'
      ],
      value: [
        '减少 50–70% 的沟通损耗',
        '确保所有角色从同一认知出发',
        '为 Spec、设计、代码奠定高质量基础'
      ]
    },
    templates: ['10_CONTEXT', '90_PROGRESS_LOG'],
    tools: {
      slashCommands: ['/iresume', '/start-day', '/end-day'],
      skills: ['context_writer', 'progress_updater'],
      subagents: []
    }
  },
  {
    id: 2,
    name: 'Spec',
    nameCn: 'UI/流程/接口定义',
    goal: '把模糊的需求变成精确可执行的规格：UI 流程图、交互细节、API 接口定义。规格越清晰，后续开发越顺畅。',
    details: {
      what: [
        '产出 UI 流程图 / 交互流程 / 状态机',
        '写清楚所有页面元素、输入、验证规则',
        '完整定义 API 接口（request / response / error cases）',
        '定义事件流、边界情况、异常处理逻辑'
      ],
      why: [
        '模糊需求导致的返工成本极高',
        'AI coding 依赖精确定义才能持续正确生成代码',
        'Spec 是唯一真实的对齐标准'
      ],
      value: [
        '开发不再靠猜',
        'AI 稳定性提高',
        '产品最终效果更一致、更少缺失功能点'
      ]
    },
    templates: ['21_UI_FLOW_SPEC', '20_API_SPEC'],
    tools: {
      slashCommands: [],
      skills: ['spec_validator'],
      subagents: ['spec_writer']
    }
  },
  {
    id: 3,
    name: 'Demo',
    nameCn: '快速原型验证',
    goal: '用最小成本做出可点击的原型，让用户「看到」而不是「想象」。早期验证 = 早期纠错。',
    details: {
      what: [
        '自动生成 Demo（HTML / Vue / React / Figma-like Mock）',
        '允许用户点击、跳转、体验流程',
        '收集反馈并迭代',
        '验证 Spec 是否准确、流程是否合理'
      ],
      why: [
        '人的想象 ≠ 实际效果',
        '越早看到界面，越早发现问题',
        '避免开发完才大改 UI 或流程'
      ],
      value: [
        '缩短决策周期',
        '大幅减少后期返工',
        '让需求方、PM、研发在视觉上达成一致'
      ]
    },
    templates: ['30_DEMO_REVIEW'],
    tools: {
      slashCommands: ['/gen-demo'],
      skills: ['ui_demo', 'mock_api_generator'],
      subagents: []
    }
  },
  {
    id: 4,
    name: 'Design',
    nameCn: '技术方案设计',
    goal: '从已验证的 Demo 反推技术方案：数据模型、组件拆分、接口设计。基于真实交互设计，而不是凭空想象架构。',
    details: {
      what: [
        '数据库模型（ERD）',
        '组件树设计 & 状态管理方案',
        'API 结构、鉴权策略、错误恢复',
        '性能、扩展性、边界场景设计'
      ],
      why: [
        '技术设计必须基于最终用户体验',
        '避免"架构过度复杂"或"功能无法支撑"',
        '为 AI coding 提供明确的技术轨道'
      ],
      value: [
        '系统可维护性、稳定性极大提升',
        '防止技术债',
        '多人协作时不再互相踩逻辑'
      ]
    },
    templates: ['40_DESIGN'],
    tools: {
      slashCommands: [],
      skills: ['design_from_demo'],
      subagents: []
    }
  },
  {
    id: 5,
    name: 'Code',
    nameCn: '功能实现',
    goal: 'AI 按设计文档逐步实现，人类审核关键决策。每日进度自动更新，断点续传不丢上下文，多人协作有迹可循。',
    details: {
      what: [
        '按 Spec / Design 有序生成代码',
        '自动拆分任务（前端 / 后端 / DB / 测试代码）',
        '人类只需审核架构、关键逻辑、异常路径',
        '每次提交自动更新 Daily Summary'
      ],
      why: [
        'AI coding 的质量依赖输入的结构化信息',
        '多人协作需要清晰可追踪的进度与变更记录',
        '避免"清空上下文后 AI 重写错误代码"'
      ],
      value: [
        '效率远高于传统写法',
        '保证交付的一致性与完整性',
        '项目追踪更透明、更容易管理'
      ]
    },
    templates: ['50_DEV_PLAN', '91_DAILY_SUMMARY'],
    tools: {
      slashCommands: ['/iresume', '/check-progress', '/daily-summary'],
      skills: ['progress_updater'],
      subagents: ['progress_tracker']
    }
  },
  {
    id: 6,
    name: 'Test',
    nameCn: '测试与质量验证',
    goal: '自动生成测试计划，覆盖核心场景和边界条件。测试报告清晰展示通过率和问题点，质量可量化、可追溯。',
    details: {
      what: [
        '自动生成测试用例（正常、异常、边界、性能）',
        '手动 + 自动化执行测试',
        '输出结构化测试报告',
        '对问题自动定位到 Spec / Design / Code 的对应部分'
      ],
      why: [
        '缺乏测试是 AI 时代最大隐患之一',
        '回归测试能避免"改 A 崩 B"的灾难',
        'AI coding 在边缘场景容易漏逻辑，必须结构化测试'
      ],
      value: [
        '系统质量可以被持续衡量',
        '回归测试自动化 → 发布风险更低',
        'Bug 变成可控成本，而不是无限返工'
      ]
    },
    templates: ['60_TEST_PLAN', '61_TEST_REPORT'],
    tools: {
      slashCommands: ['/run-tests'],
      skills: ['test_runner', 'test_report_generator'],
      subagents: ['test_plan_writer']
    }
  },
  {
    id: 7,
    name: 'Deploy',
    nameCn: '发布上线',
    goal: '自动生成发布说明和更新日志，记录本次发布的所有变更。对外沟通有据可依，版本历史清晰可查。',
    details: {
      what: [
        '生成版本说明（Breaking changes / Added / Updated / Fixed）',
        '自动生成 Changelog',
        '检查迁移脚本和环境变量',
        '正式部署到生产环境'
      ],
      why: [
        '文档化发布流程能避免遗漏操作',
        '版本历史是后期排查问题的重要依据',
        '用户、团队都需要一个可引用的官方记录'
      ],
      value: [
        '减少发布风险',
        '增强团队透明度',
        '上线过程可复盘、可自动化、可重复执行'
      ]
    },
    templates: ['70_RELEASE_NOTE', '71_CHANGELOG'],
    tools: {
      slashCommands: ['/release'],
      skills: ['changelog_updater'],
      subagents: ['release_summarizer']
    }
  }
]

// 角色数据
const roles = [
  {
    id: 'pm',
    icon: '👔',
    name: '我是 PM',
    focusPhases: [1, 2, 3],
    tools: ['/new-feature', '/check-progress', '/daily-summary'],
    actionLabel: '进入 PM 视图',
    actionRoute: '/role/pm'
  },
  {
    id: 'developer',
    icon: '👨‍💻',
    name: '我是开发者',
    focusPhases: [4, 5, 6],
    tools: ['/iresume', '/run-tests', '/release'],
    actionLabel: '进入开发者视图',
    actionRoute: '/role/ai-pe'
  },
  {
    id: 'beginner',
    icon: '🆕',
    name: '我是新手',
    focusPhases: [],
    tools: [],
    tipsLabel: '建议路径',
    tips: ['看完本指南', '跑示例项目', '创建第一个功能'],
    actionLabel: '查看示例项目',
    actionRoute: '/project-dashboard'
  }
]

// 滚动到指定 section
const scrollToSection = (index) => {
  const sectionRefs = [section0, section1, section2, section3, section4]
  const section = sectionRefs[index]?.value
  if (section) {
    section.scrollIntoView({ behavior: 'smooth' })
  }
}

// 切换 Phase 展开状态
const togglePhase = (phaseId) => {
  expandedPhase.value = expandedPhase.value === phaseId ? null : phaseId
}

// 复制命令
const copyCommand = async (command) => {
  try {
    await navigator.clipboard.writeText(command)
    ElMessage.success('已复制到剪贴板')
  } catch (err) {
    ElMessage.error('复制失败')
  }
}

// 导航到角色视图
const navigateToRole = (role) => {
  router.push(role.actionRoute)
}

// 监听滚动，更新当前 section
const handleScroll = () => {
  const sectionRefs = [section0, section1, section2, section3, section4]
  const scrollY = window.scrollY + window.innerHeight / 2

  for (let i = sectionRefs.length - 1; i >= 0; i--) {
    const section = sectionRefs[i]?.value
    if (section && section.offsetTop <= scrollY) {
      currentSection.value = i
      break
    }
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.panorama-guide {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 侧边导航点 */
.section-nav {
  position: fixed;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 100;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.nav-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  transition: all 0.3s;
}

.nav-dot.active {
  background: #fff;
  transform: scale(1.3);
}

.nav-dot:hover {
  background: rgba(255, 255, 255, 0.8);
}

/* Section 通用样式 */
.guide-section {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.section-content {
  max-width: 1200px;
  width: 100%;
  text-align: center;
}

.section-title {
  font-size: 2.5rem;
  color: #fff;
  margin-bottom: 10px;
}

.section-subtitle {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 40px;
}

.subtitle-highlight {
  background: linear-gradient(135deg, #67c23a 0%, #409eff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-weight: 700;
}

/* Section 1: 痛点共鸣 */
.section-pain-points {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

.main-title {
  font-size: 2.5rem;
  color: #fff;
  margin-bottom: 20px;
  line-height: 1.3;
}

.main-subtitle {
  font-size: 1.3rem;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 50px;
  font-style: italic;
}

.pain-points-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 30px;
  max-width: 800px;
  margin: 0 auto 60px;
}

.pain-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 30px;
  text-align: left;
  transition: all 0.3s;
}

.pain-card:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-5px);
}

.pain-icon {
  color: #f56c6c;
  margin-bottom: 15px;
}

.pain-card h3 {
  color: #fff;
  font-size: 1.3rem;
  margin-bottom: 10px;
}

.pain-card p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.95rem;
  line-height: 1.6;
}

/* 滚动提示 */
.scroll-hint {
  margin-top: 40px;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.8);
}

.scroll-hint p {
  margin-bottom: 10px;
  font-size: 1rem;
}

.bounce {
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

/* Section 2: 工作流全景 */
.section-workflow {
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
}

.phases-container {
  margin-bottom: 30px;
}

.phases-row {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.phase-card {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 20px;
  min-width: 140px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.phase-card:hover {
  background: rgba(255, 255, 255, 0.15);
}

.phase-card.expanded {
  background: rgba(255, 255, 255, 0.2);
  min-width: 280px;
}

.phase-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.phase-number {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.1rem;
}

.phase-info {
  text-align: left;
}

.phase-name {
  color: #fff;
  font-weight: 600;
  font-size: 1rem;
}

.phase-name-cn {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.85rem;
}

.phase-details {
  margin-top: 15px;
  text-align: left;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 15px;
}

.detail-section {
  margin-bottom: 12px;
}

.detail-label {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.75rem;
  margin-bottom: 5px;
  text-transform: uppercase;
}

.detail-content {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
}

.detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.detail-list {
  margin: 0;
  padding-left: 18px;
  color: rgba(255, 255, 255, 0.85);
  font-size: 0.85rem;
  line-height: 1.6;
}

.detail-list li {
  margin-bottom: 4px;
}

.detail-list li:last-child {
  margin-bottom: 0;
}

.detail-what .detail-label {
  color: #67c23a;
}

.detail-why .detail-label {
  color: #e6a23c;
}

.detail-value .detail-label {
  color: #409eff;
}

.phase-arrow {
  position: absolute;
  right: -20px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.3);
  z-index: 1;
}

.click-hint {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.9rem;
}

/* Section 3: 搭建项目 */
.section-setup {
  background: linear-gradient(135deg, #134e5e 0%, #71b280 100%);
}

.setup-steps-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  max-width: 1000px;
  margin: 0 auto 24px;
}

.setup-info-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.setup-step {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}

.setup-step h3 {
  color: #fff;
  margin-bottom: 12px;
  font-size: 0.95rem;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #fff;
  color: #134e5e;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  font-weight: bold;
  margin: 0 auto 12px;
}

.step-note {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.75rem;
  margin-top: 8px;
}

.command-box {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  padding: 10px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.command-box code {
  color: #7bed9f;
  font-family: 'Fira Code', monospace;
  font-size: 0.75rem;
  word-break: break-all;
}

.command-box.large {
  padding: 20px;
}

.command-box.large code {
  font-size: 1.2rem;
}

.directory-tree {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
  padding: 20px;
  text-align: left;
}

.directory-tree h4 {
  color: #fff;
  margin-bottom: 12px;
  text-align: center;
  font-size: 0.95rem;
}

.directory-tree pre {
  color: #7bed9f;
  font-family: 'Fira Code', monospace;
  font-size: 0.75rem;
  line-height: 1.5;
  margin: 0;
}

.github-config {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
  padding: 20px;
  text-align: left;
}

.github-config h4 {
  color: #fff;
  margin-bottom: 12px;
  text-align: center;
  font-size: 0.95rem;
}

.config-desc {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.85rem;
  margin-bottom: 12px;
}

.config-steps {
  color: rgba(255, 255, 255, 0.9);
  padding-left: 20px;
  margin-bottom: 12px;
  font-size: 0.8rem;
  line-height: 1.6;
}

.config-steps li {
  margin-bottom: 6px;
}

.config-steps code {
  background: rgba(0, 0, 0, 0.3);
  padding: 2px 5px;
  border-radius: 4px;
  color: #7bed9f;
  font-size: 0.75rem;
}

.config-note {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.75rem;
  font-style: italic;
}

/* Section 4: 创建第一个功能 */
.section-first-feature {
  background: linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%);
}

.feature-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  max-width: 800px;
  margin: 0 auto;
}

.feature-left {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feature-left .command-box.large {
  padding: 14px 16px;
}

.feature-left .command-box.large code {
  font-size: 1rem;
}

.feature-result {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 10px;
  padding: 16px;
  text-align: left;
}

.feature-result pre {
  color: #7bed9f;
  font-family: 'Fira Code', monospace;
  font-size: 0.75rem;
  line-height: 1.5;
  margin: 0;
}

.feature-right {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 16px;
  text-align: left;
}

.feature-right h4 {
  color: #fff;
  margin-bottom: 12px;
  font-size: 0.95rem;
}

.feature-right ol {
  color: rgba(255, 255, 255, 0.9);
  padding-left: 18px;
  margin-bottom: 12px;
  font-size: 0.85rem;
}

.feature-right li {
  margin-bottom: 6px;
}

.feature-right code {
  background: rgba(0, 0, 0, 0.3);
  padding: 2px 5px;
  border-radius: 4px;
  color: #7bed9f;
  font-size: 0.8rem;
}

.daily-workflow {
  display: flex;
  gap: 8px;
}

/* Section 5: Dashboard 看板 */
.section-dashboard {
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
}

.dashboard-layout {
  display: flex;
  gap: 40px;
  max-width: 1100px;
  margin: 0 auto 40px;
  align-items: flex-start;
}

.dashboard-screenshot {
  flex: 1.2;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.dashboard-screenshot img {
  width: 100%;
  height: auto;
  display: block;
}

.dashboard-values {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.value-highlight {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 18px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: all 0.3s ease;
}

.value-highlight:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(5px);
}

.value-icon {
  font-size: 1.8rem;
  flex-shrink: 0;
  width: 50px;
  text-align: center;
}

.value-content {
  flex: 1;
  text-align: left;
}

.value-content h3 {
  color: #fff;
  font-size: 1rem;
  margin: 0 0 6px 0;
  text-align: left;
}

.value-content p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.85rem;
  line-height: 1.5;
  margin: 0;
  text-align: left;
}

.value-content code {
  background: rgba(103, 194, 58, 0.2);
  color: #67c23a;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.8rem;
}

.dashboard-cta {
  display: flex;
  justify-content: center;
  margin-bottom: 40px;
}

@media (max-width: 900px) {
  .dashboard-layout {
    flex-direction: column;
  }

  .dashboard-screenshot {
    max-width: 100%;
  }
}

/* Section 6: 角色入口 */
.section-roles {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

.roles-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
  max-width: 1000px;
  margin: 0 auto;
}

.role-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 30px;
  text-align: left;
  transition: all 0.3s;
}

.role-card:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-5px);
}

.role-icon {
  font-size: 3rem;
  margin-bottom: 15px;
}

.role-card h3 {
  color: #fff;
  font-size: 1.3rem;
  margin-bottom: 20px;
}

.role-section {
  margin-bottom: 15px;
}

.role-label {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.8rem;
  margin-bottom: 8px;
  text-transform: uppercase;
}

.role-section ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.role-section li {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
  padding: 4px 0;
}

.role-action {
  width: 100%;
  margin-top: 20px;
}

/* 响应式 */
@media (max-width: 768px) {
  .pain-points-grid {
    grid-template-columns: 1fr;
  }

  .phases-row {
    flex-direction: column;
    align-items: center;
  }

  .phase-card {
    width: 100%;
    max-width: 300px;
  }

  .phase-arrow {
    display: none;
  }

  .setup-grid {
    grid-template-columns: 1fr;
  }

  .feature-grid {
    grid-template-columns: 1fr;
  }

  .roles-grid {
    grid-template-columns: 1fr;
  }

  .section-nav {
    right: 10px;
  }
}
</style>
