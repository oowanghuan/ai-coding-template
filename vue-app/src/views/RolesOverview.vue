<template>
  <div class="roles-overview-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="container">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">
            <el-icon><HomeFilled /></el-icon>
            首页
          </el-breadcrumb-item>
          <el-breadcrumb-item>角色与协作</el-breadcrumb-item>
        </el-breadcrumb>
        <h1 class="page-title">👥 角色与协作：8 阶段 × 6 角色</h1>
        <p class="page-subtitle">从 Kickoff 到 Deploy 的完整协作流程（Phase 0-7）</p>
      </div>
    </div>

    <div class="page-content">
      <div class="container">
        <!-- Part 1: 开发流程全景图 -->
        <el-card class="content-section" shadow="never">
          <h2 class="section-title">📊 开发流程全景图</h2>
          <p class="section-desc">AI 时代的完整开发流程包含 8 个阶段（Phase 0-7），每个阶段都有明确的目标、负责人和交付物</p>

          <div class="timeline-container">
            <div class="timeline-item" v-for="(stage, index) in stages" :key="index">
              <div class="timeline-card" :style="{ borderColor: stage.color }">
                <div class="timeline-header" :style="{ background: stage.color }">
                  <span class="timeline-icon">{{ stage.icon }}</span>
                  <span class="timeline-number">{{ index + 1 }}</span>
                </div>
                <div class="timeline-body">
                  <h3 class="timeline-title">{{ stage.name }}</h3>
                  <p class="timeline-duration">{{ stage.duration }}</p>
                  <p class="timeline-owner">主导：{{ stage.owner }}</p>
                  <div class="timeline-output">
                    <span class="output-label">交付物：</span>
                    <span class="output-value">{{ stage.output }}</span>
                  </div>
                </div>
              </div>
              <div v-if="index < stages.length - 1" class="timeline-arrow">
                <el-icon><ArrowRight /></el-icon>
              </div>
            </div>
          </div>
        </el-card>

        <!-- Part 2: RACI 责任矩阵 -->
        <el-card class="content-section" shadow="never">
          <h2 class="section-title">📋 RACI 责任矩阵</h2>
          <p class="section-desc">明确每个角色在各阶段的责任类型：R=负责执行 | A=最终批准 | C=需要咨询 | I=需要知情</p>

          <div class="raci-legend">
            <div class="legend-item">
              <span class="legend-badge responsible">R</span>
              <span class="legend-text">Responsible - 负责执行</span>
            </div>
            <div class="legend-item">
              <span class="legend-badge accountable">A</span>
              <span class="legend-text">Accountable - 最终批准</span>
            </div>
            <div class="legend-item">
              <span class="legend-badge consulted">C</span>
              <span class="legend-text">Consulted - 需要咨询</span>
            </div>
            <div class="legend-item">
              <span class="legend-badge informed">I</span>
              <span class="legend-text">Informed - 需要知情</span>
            </div>
          </div>

          <div class="raci-table-wrapper">
            <table class="raci-table">
              <thead>
                <tr>
                  <th class="role-column">角色 \ 阶段</th>
                  <th v-for="stage in stages" :key="stage.name">
                    <div class="stage-header">
                      <span class="stage-icon">{{ stage.icon }}</span>
                      <span class="stage-name">{{ stage.name }}</span>
                    </div>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="role in raciMatrix" :key="role.name">
                  <td class="role-name-cell">
                    <span class="role-icon">{{ role.icon }}</span>
                    <span class="role-name">{{ role.name }}</span>
                  </td>
                  <td v-for="(raci, index) in role.responsibilities" :key="index" class="raci-cell">
                    <span
                      v-for="(letter, i) in raci.split('/')"
                      :key="i"
                      :class="['raci-badge', getRaciClass(letter)]"
                    >
                      {{ letter }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </el-card>

        <!-- Part 3: 八个阶段详解 -->
        <el-card class="content-section" shadow="never">
          <h2 class="section-title">🎯 八个阶段详解</h2>
          <p class="section-desc">每个阶段的目标、参与角色、输入输出和关键决策点</p>

          <el-collapse v-model="activeStages" class="stages-collapse">
            <el-collapse-item
              v-for="(stage, index) in stageDetails"
              :key="index"
              :name="index"
            >
              <template #title>
                <div class="collapse-title">
                  <span class="collapse-icon" :style="{ color: stages[index].color }">
                    {{ stages[index].icon }}
                  </span>
                  <span class="collapse-number">阶段 {{ index + 1 }}</span>
                  <span class="collapse-name">{{ stages[index].name }}</span>
                  <span class="collapse-tag" :style="{ background: stages[index].color }">
                    {{ stages[index].owner }}
                  </span>
                </div>
              </template>

              <div class="stage-detail-content">
                <!-- 阶段目标 -->
                <div class="detail-section">
                  <h4 class="detail-title">🎯 阶段目标</h4>
                  <p class="detail-text">{{ stage.goal }}</p>
                </div>

                <!-- 参与角色 -->
                <div class="detail-section">
                  <h4 class="detail-title">👥 参与角色</h4>
                  <div class="role-participation">
                    <div
                      v-for="(participant, i) in stage.participants"
                      :key="i"
                      class="participant-item"
                    >
                      <div class="participant-header">
                        <span class="participant-role">{{ participant.role }}</span>
                        <span class="participant-badge" :style="{ background: participant.color }">
                          {{ participant.type }}
                        </span>
                      </div>
                      <ul class="participant-tasks">
                        <li v-for="(task, j) in participant.tasks" :key="j">{{ task }}</li>
                      </ul>
                    </div>
                  </div>
                </div>

                <!-- 输入输出 -->
                <div class="detail-section">
                  <h4 class="detail-title">📦 输入 → 输出</h4>
                  <div class="io-grid">
                    <div class="io-box input-box">
                      <div class="io-label">输入 Input</div>
                      <ul class="io-list">
                        <li v-for="(item, i) in stage.input" :key="i">{{ item }}</li>
                      </ul>
                    </div>
                    <div class="io-arrow">
                      <el-icon><Right /></el-icon>
                    </div>
                    <div class="io-box output-box">
                      <div class="io-label">输出 Output</div>
                      <ul class="io-list">
                        <li v-for="(item, i) in stage.output" :key="i">{{ item }}</li>
                      </ul>
                    </div>
                  </div>
                </div>

                <!-- 关键决策点 -->
                <div class="detail-section" v-if="stage.decisions && stage.decisions.length > 0">
                  <h4 class="detail-title">🔸 关键决策点</h4>
                  <div class="decision-list">
                    <div
                      v-for="(decision, i) in stage.decisions"
                      :key="i"
                      class="decision-item"
                    >
                      <div class="decision-header">{{ decision.question }}</div>
                      <div class="decision-meta">
                        <span class="decision-label">决策者：</span>
                        <span class="decision-value">{{ decision.maker }}</span>
                        <span class="decision-separator">|</span>
                        <span class="decision-label">咨询：</span>
                        <span class="decision-value">{{ decision.consulted }}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 验收标准 -->
                <div class="detail-section">
                  <h4 class="detail-title">✅ 验收标准</h4>
                  <ul class="checklist">
                    <li v-for="(item, i) in stage.acceptance" :key="i">{{ item }}</li>
                  </ul>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </el-card>

        <!-- Part 4: 关键交接点 -->
        <el-card class="content-section" shadow="never">
          <h2 class="section-title">🔄 关键交接点</h2>
          <p class="section-desc">各阶段之间的工作成果如何传递？包含交接物清单、格式标准和验收标准</p>

          <div class="handoff-flow">
            <div
              v-for="(handoff, index) in handoffs"
              :key="index"
              class="handoff-item"
            >
              <div class="handoff-card">
                <div class="handoff-header">
                  <span class="handoff-number">{{ index + 1 }}</span>
                  <div class="handoff-roles">
                    <span class="handoff-from">{{ handoff.from }}</span>
                    <el-icon class="handoff-icon"><Right /></el-icon>
                    <span class="handoff-to">{{ handoff.to }}</span>
                  </div>
                </div>
                <div class="handoff-body">
                  <div class="handoff-deliverable">{{ handoff.deliverable }}</div>
                  <div class="handoff-items">
                    <div class="handoff-label">交接物清单：</div>
                    <ul class="handoff-list">
                      <li v-for="(item, i) in handoff.items" :key="i">{{ item }}</li>
                    </ul>
                  </div>
                  <div class="handoff-standard">
                    <div class="handoff-label">验收标准：</div>
                    <p class="handoff-text">{{ handoff.standard }}</p>
                  </div>
                </div>
              </div>
              <div v-if="index < handoffs.length - 1" class="handoff-connector">
                <el-icon><ArrowDown /></el-icon>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 与传统模式的对比 -->
        <el-card class="content-section" shadow="never">
          <h2 class="section-title">⚖️ 与传统模式的对比</h2>

          <el-table :data="comparisonData" stripe style="width: 100%">
            <el-table-column prop="aspect" label="维度" width="150" />
            <el-table-column prop="traditional" label="传统模式">
              <template #default="{ row }">
                <span style="color: #c62828;">{{ row.traditional }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="ai" label="AI 时代模式">
              <template #default="{ row }">
                <span style="color: #2e7d32;">{{ row.ai }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- 底部行动 -->
        <div class="action-section">
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
import { HomeFilled, ArrowRight, Right, ArrowDown } from '@element-plus/icons-vue'

const router = useRouter()
const activeStages = ref([0]) // 默认展开第一个阶段

// 8个阶段数据 (Phase 0-7)
const stages = ref([
  {
    icon: '🎯',
    name: 'Kickoff',
    phase: 0,
    duration: '0.5-1天',
    owner: '项目经理',
    output: '功能初始化',
    color: '#1e3c72'
  },
  {
    icon: '📋',
    name: 'Context',
    phase: 1,
    duration: '1-2天',
    owner: '架构师',
    output: '背景/目标/范围',
    color: '#2d5a87'
  },
  {
    icon: '📝',
    name: 'Spec',
    phase: 2,
    duration: '2-3天',
    owner: 'AI PE',
    output: 'UI/流程/接口定义',
    color: '#667eea'
  },
  {
    icon: '🎨',
    name: 'Demo',
    phase: 3,
    duration: '2-3天',
    owner: 'AI PE',
    output: '快速原型验证',
    color: '#f093fb'
  },
  {
    icon: '🏗️',
    name: 'Design',
    phase: 4,
    duration: '1-2天',
    owner: '架构师',
    output: '技术方案设计',
    color: '#8b5cf6'
  },
  {
    icon: '💻',
    name: 'Code',
    phase: 5,
    duration: '5-10天',
    owner: '前端/后端工程师',
    output: '功能实现',
    color: '#11998e'
  },
  {
    icon: '🔍',
    name: 'Test',
    phase: 6,
    duration: '2-3天',
    owner: 'AI QA',
    output: '测试与质量验证',
    color: '#ff9800'
  },
  {
    icon: '🚀',
    name: 'Deploy',
    phase: 7,
    duration: '0.5-1天',
    owner: '项目经理',
    output: '发布上线',
    color: '#06beb6'
  }
])

// RACI 矩阵数据 (8阶段: Kickoff, Context, Spec, Demo, Design, Code, Test, Deploy)
const raciMatrix = ref([
  {
    icon: '🎬',
    name: '项目经理',
    responsibilities: ['R/A', 'I', 'I', 'I', 'I', 'I', 'C', 'R/A']
  },
  {
    icon: '🏗️',
    name: '架构师',
    responsibilities: ['C', 'R/A', 'C', 'I', 'R/A', 'C', 'I', 'I']
  },
  {
    icon: '⭐',
    name: 'AI PE',
    responsibilities: ['I', 'C', 'R/A', 'R/A', 'C', 'C', 'C', 'I']
  },
  {
    icon: '🎨',
    name: 'UI设计师',
    responsibilities: ['I', 'C', 'C', 'C', 'I', 'I', 'I', 'I']
  },
  {
    icon: '💻',
    name: '前端工程师',
    responsibilities: ['I', 'I', 'I', 'C', 'C', 'R', 'C', 'I']
  },
  {
    icon: '⚙️',
    name: '后端工程师',
    responsibilities: ['I', 'C', 'I', 'I', 'C', 'R', 'C', 'I']
  },
  {
    icon: '🔍',
    name: 'AI QA',
    responsibilities: ['I', 'I', 'C', 'C', 'I', 'C', 'R/A', 'C']
  }
])

// 阶段详解数据 (8阶段)
const stageDetails = ref([
  // Phase 0: Kickoff
  {
    goal: '功能初始化，创建项目/功能分支，设置协作框架，明确参与人员和沟通渠道',
    participants: [
      {
        role: '项目经理',
        type: '主导',
        color: '#1e3c72',
        tasks: ['创建功能分支', '设置项目看板', '明确参与人员', '建立沟通渠道']
      },
      {
        role: '架构师',
        type: '咨询',
        color: '#2d5a87',
        tasks: ['确认技术边界', '评估影响范围']
      }
    ],
    input: ['需求描述', '业务优先级', '资源情况'],
    output: ['功能分支', '项目看板', '参与人员清单', '沟通渠道'],
    decisions: [
      {
        question: '功能粒度是否合适？',
        maker: '项目经理',
        consulted: '架构师'
      }
    ],
    acceptance: [
      '功能分支已创建',
      '项目看板已设置',
      '参与人员已明确',
      '沟通渠道已建立'
    ]
  },
  // Phase 1: Context
  {
    goal: '明确功能背景、目标、范围、约束条件，输出上下文文档作为后续阶段的基础',
    participants: [
      {
        role: '架构师',
        type: '主导',
        color: '#2d5a87',
        tasks: ['分析业务背景', '定义目标和范围', '识别约束条件', '输出6件套文档']
      },
      {
        role: 'AI PE',
        type: '参与',
        color: '#667eea',
        tasks: ['理解业务需求', '提出实施疑问', '确认架构可行性']
      },
      {
        role: '后端工程师',
        type: '咨询',
        color: '#11998e',
        tasks: ['确认API设计', '评估技术风险']
      }
    ],
    input: ['产品需求文档（PRD）', '业务目标', '现有系统状况'],
    output: ['Context 文档', '6件套文档包', '技术风险清单', '开发排期预估'],
    decisions: [
      {
        question: '功能范围是否明确？',
        maker: '架构师',
        consulted: '项目经理、AI PE'
      },
      {
        question: '是否有技术依赖阻塞？',
        maker: '架构师',
        consulted: '后端工程师'
      }
    ],
    acceptance: [
      '背景和目标文档完整',
      '范围边界清晰',
      '约束条件已识别',
      '技术风险已评估',
      '6件套文档完整且格式规范'
    ]
  },
  // Phase 2: Spec
  {
    goal: '将自然语言需求转化为结构化的、AI 可执行的规格说明，明确所有交互逻辑、字段定义和边界条件',
    participants: [
      {
        role: 'AI PE',
        type: '主导',
        color: '#667eea',
        tasks: ['编写结构化Spec', '定义所有字段和状态', '明确边界条件和错误态']
      },
      {
        role: '架构师',
        type: '咨询',
        color: '#1e3c72',
        tasks: ['Review架构合规性', '确认技术可行性']
      },
      {
        role: 'UI设计师',
        type: '咨询',
        color: '#f093fb',
        tasks: ['确认Design System适配', '提供UI组件规范']
      }
    ],
    input: ['6件套文档', '业务需求', 'Design System规范'],
    output: ['结构化Spec文档', 'API Schema定义', '组件状态定义', '测试用例大纲'],
    decisions: [
      {
        question: '复杂交互如何拆解？',
        maker: 'AI PE',
        consulted: 'UI设计师、架构师'
      }
    ],
    acceptance: [
      'Spec包含所有用户流程和交互逻辑',
      '所有字段有类型、校验、错误提示定义',
      '边界条件和错误态已全部列出',
      '后端工程师确认API行为可实现',
      'UI设计师确认符合Design System'
    ]
  },
  {
    goal: '用 AI 快速生成可交互的 Demo，验证 UI/UX 设计和交互流程，避免在生产代码阶段返工',
    participants: [
      {
        role: 'AI PE',
        type: '主导',
        color: '#667eea',
        tasks: ['使用AI生成Demo代码', '调试交互逻辑', '优化UI细节']
      },
      {
        role: 'UI设计师',
        type: '咨询',
        color: '#f093fb',
        tasks: ['Review UI一致性', '确认交互合理性']
      },
      {
        role: '前端工程师',
        type: '咨询',
        color: '#667eea',
        tasks: ['评估实现复杂度', '提供技术建议']
      }
    ],
    input: ['Spec文档', 'Design System', 'API Schema'],
    output: ['可运行的Demo', 'UI组件清单', '交互流程确认'],
    decisions: [
      {
        question: 'Demo是否满足需求？',
        maker: 'AI PE',
        consulted: 'UI设计师、产品负责人'
      }
    ],
    acceptance: [
      'Demo能完整展示核心用户流程',
      'UI符合Design System规范',
      '交互逻辑与Spec一致',
      '各状态（loading/error/empty）都有展示',
      '利益相关方确认可以进入开发'
    ]
  },
  // Phase 4: Design
  {
    goal: '基于 Demo 验证结果，制定详细的技术方案，包括架构设计、API设计、数据库设计等',
    participants: [
      {
        role: '架构师',
        type: '主导',
        color: '#8b5cf6',
        tasks: ['制定技术方案', '设计API契约', '规划数据库Schema', '评估技术风险']
      },
      {
        role: '后端工程师',
        type: '咨询',
        color: '#11998e',
        tasks: ['确认实现可行性', '提供技术建议', '评估工作量']
      },
      {
        role: '前端工程师',
        type: '咨询',
        color: '#667eea',
        tasks: ['确认API需求', '评估前端实现复杂度']
      }
    ],
    input: ['Demo验证结果', 'Spec文档', '6件套文档'],
    output: ['技术方案文档', 'API契约', '数据库Schema', '实现计划'],
    decisions: [
      {
        question: '技术方案是否满足需求？',
        maker: '架构师',
        consulted: '后端工程师、前端工程师'
      },
      {
        question: 'API设计是否合理？',
        maker: '架构师',
        consulted: 'AI PE、后端工程师'
      }
    ],
    acceptance: [
      '技术方案文档完整',
      'API契约清晰可执行',
      '数据库Schema经过评审',
      '技术风险已识别并有应对方案',
      '实现计划得到各方确认'
    ]
  },
  // Phase 5: Code
  {
    goal: '将 Demo 转化为生产级代码，对接真实 API，实现完整的业务逻辑和错误处理',
    participants: [
      {
        role: '前端工程师',
        type: '主导',
        color: '#667eea',
        tasks: ['编写生产级前端代码', '对接后端API', '实现状态管理']
      },
      {
        role: '后端工程师',
        type: '主导',
        color: '#11998e',
        tasks: ['实现API业务逻辑', '数据库操作', '错误处理']
      },
      {
        role: 'AI PE',
        type: '咨询',
        color: '#667eea',
        tasks: ['解释Spec细节', '确认实现符合预期']
      }
    ],
    input: ['Demo代码', 'Spec文档', 'API Schema', 'Design System'],
    output: ['生产代码', 'API实现', '单元测试', '技术文档'],
    decisions: [
      {
        question: 'API行为与Spec不一致时如何处理？',
        maker: '后端工程师',
        consulted: 'AI PE、架构师'
      }
    ],
    acceptance: [
      '所有API按Schema实现',
      '前端与后端联调通过',
      '错误处理完整',
      '代码通过静态检查和单元测试',
      '性能指标在可接受范围'
    ]
  },
  {
    goal: '根据 Spec 和 Rulebook 自动化测试，确保所有功能、交互、边界条件符合规格',
    participants: [
      {
        role: 'AI QA',
        type: '主导',
        color: '#ff9800',
        tasks: ['编写测试用例', '执行自动化测试', '记录bug和问题']
      },
      {
        role: 'AI PE',
        type: '支持',
        color: '#667eea',
        tasks: ['解释Spec疑问', '确认bug优先级']
      },
      {
        role: '前端/后端工程师',
        type: '修复',
        color: '#11998e',
        tasks: ['修复测试发现的问题', '补充单元测试']
      }
    ],
    input: ['生产代码', 'Spec文档', 'Rulebook', 'Design System'],
    output: ['测试报告', 'Bug清单', 'Go/No-Go决策'],
    decisions: [
      {
        question: '是否可以上线？',
        maker: 'AI QA',
        consulted: '项目经理、AI PE'
      },
      {
        question: 'P1/P2 bug是否需要阻塞上线？',
        maker: '项目经理',
        consulted: 'AI QA、产品负责人'
      }
    ],
    acceptance: [
      '所有P0 bug已修复',
      'Spec中定义的核心功能100%通过',
      'UI在主流浏览器/设备上正常显示',
      'API响应时间在可接受范围',
      '没有安全漏洞'
    ]
  },
  {
    goal: '安全稳定地将代码部署到生产环境，监控上线后系统状态，确保业务正常运行',
    participants: [
      {
        role: '项目经理',
        type: '主导',
        color: '#06beb6',
        tasks: ['协调发布时间', '管理发布流程', '监控上线状态']
      },
      {
        role: '后端工程师',
        type: '执行',
        color: '#11998e',
        tasks: ['执行部署脚本', '数据库迁移', '服务配置']
      },
      {
        role: 'AI QA',
        type: '验证',
        color: '#ff9800',
        tasks: ['生产环境冒烟测试', '监控错误率']
      }
    ],
    input: ['测试通过的代码', '测试报告', '部署脚本', '回滚预案'],
    output: ['上线成功确认', '监控面板', '发布报告', '知识沉淀'],
    decisions: [
      {
        question: '是否继续灰度放量？',
        maker: '项目经理',
        consulted: '后端工程师、AI QA'
      },
      {
        question: '是否需要回滚？',
        maker: '项目经理',
        consulted: '架构师、后端工程师'
      }
    ],
    acceptance: [
      '生产环境所有服务启动正常',
      '冒烟测试通过',
      '错误率在基线范围内（<1%）',
      '响应时间在SLA范围内',
      '没有数据丢失或损坏'
    ]
  }
])

// 关键交接点数据 (8阶段)
const handoffs = ref([
  // Kickoff → Context
  {
    from: '项目经理',
    to: '架构师',
    deliverable: '功能初始化信息',
    items: [
      '功能分支已创建',
      '项目看板已设置',
      '参与人员清单',
      '沟通渠道（Slack/钉钉群等）',
      '业务优先级和截止日期'
    ],
    standard: '架构师能够快速了解功能背景，开始进行上下文分析和技术规划'
  },
  // Context → Spec
  {
    from: '架构师',
    to: 'AI PE',
    deliverable: 'Context 文档 + 6件套技术文档包',
    items: [
      '功能背景和目标文档',
      '模块划分图（Mermaid / 图片）',
      'API 规范文档（OpenAPI/Swagger）',
      '数据库 Schema（SQL DDL / ER 图）',
      'Design System 文档（Figma 链接 + Token 配置）',
      '部署架构图',
      '技术栈清单'
    ],
    standard: 'AI PE 能够在绝大多数场景下独立编写 Spec，仅在少数边界问题时需要再咨询架构师'
  },
  // Spec → Demo
  {
    from: 'AI PE',
    to: 'UI设计师 + 前端 + 后端 + AI QA',
    deliverable: 'Spec v1.0 + 流程图',
    items: [
      '结构化 Spec 文档（包含字段、状态、交互逻辑）',
      '关键用户流程图 / 状态机图',
      '接口行为需求（成功/失败/错误码）',
      '边界条件与错误态清单'
    ],
    standard: '所有实现 / 测试角色能仅凭 Spec 理解模块行为，不再需要频繁追问需求细节'
  },
  // Demo → Design
  {
    from: 'AI PE',
    to: '架构师 + 前端 + 项目经理',
    deliverable: '可运行 Demo + 交互说明',
    items: [
      'Demo 仓库地址 / 访问链接',
      '关键交互录屏或动图（可选）',
      '与正式 Design System 的差异说明',
      '已知限制（例如：仅支持小数据量、仅假数据）',
      '验证结论和待确认问题'
    ],
    standard: 'UI 能确认视觉与交互方向，架构师可以开始技术方案设计，PM/业务能用 Demo 做早期评审'
  },
  // Design → Code
  {
    from: '架构师',
    to: '前端 + 后端工程师',
    deliverable: '技术方案 + API契约',
    items: [
      '技术方案文档',
      'API契约（请求/响应Schema）',
      '数据库Schema变更',
      '实现计划和任务拆分',
      '技术风险和应对方案'
    ],
    standard: '工程师能够按照技术方案独立实现，API契约清晰，前后端可并行开发'
  },
  // Code → Test
  {
    from: '前端 + 后端工程师',
    to: 'AI QA',
    deliverable: '可测版本（测试环境）',
    items: [
      '测试环境访问地址',
      '版本号 / Git 标签',
      'API 文档（包含鉴权方式）',
      '测试账号与测试数据准备情况',
      '已知技术风险与临时绕过方案'
    ],
    standard: 'AI QA 能基于 Spec 和 API 文档，在测试环境中完成 Rulebook 设计与自动化测试执行'
  },
  // Test → Deploy
  {
    from: 'AI QA',
    to: '项目经理',
    deliverable: '测试报告 + 上线风险建议',
    items: [
      '通过 / 失败用例统计',
      '按级别归类的 Bug 清单（P0/P1/P2…）',
      '已覆盖 / 未覆盖的测试范围说明',
      '对当前版本的风险评估与 Go/No-Go 建议'
    ],
    standard: '项目经理可以据此做「是否上线」决策，并与业务方对齐风险与范围'
  },
  // Deploy → 全员
  {
    from: '项目经理',
    to: '全员',
    deliverable: '上线通知 + 监控结果 + 复盘信息',
    items: [
      '上线时间窗口与影响范围',
      '变更内容摘要（做了什么 / 没做什么）',
      '关键监控面板链接（错误率、延迟、核心指标）',
      '上线结果（成功 / 回滚）',
      '复盘会议邀请与文档链接'
    ],
    standard: '所有相关角色知道当前版本状态，能够在问题发生时快速响应，并在事后参与复盘'
  }
])

// 对比数据
const comparisonData = ref([
  {
    aspect: '组织方式',
    traditional: '按职能划分（PM/UI/前端/后端/QA）',
    ai: '按模块设置 Owner + 规则专家'
  },
  {
    aspect: '沟通方式',
    traditional: '人与人反复沟通',
    ai: '通过 Spec/Schema 结构化文档'
  },
  {
    aspect: '责任边界',
    traditional: '各管一段，边界模糊',
    ai: '模块 Owner 全链路负责'
  },
  {
    aspect: '交付物',
    traditional: 'PRD/Figma/代码',
    ai: 'Spec/Demo/Code/Rulebook'
  },
  {
    aspect: '瓶颈',
    traditional: '编码速度慢',
    ai: '规则制定和一致性维护'
  },
  {
    aspect: '核心能力',
    traditional: '写代码',
    ai: '结构化思维 + AI Orchestration'
  }
])

// RACI 样式类
const getRaciClass = (letter) => {
  const classMap = {
    'R': 'responsible',
    'A': 'accountable',
    'C': 'consulted',
    'I': 'informed'
  }
  return classMap[letter] || ''
}
</script>

<style scoped>
.roles-overview-page {
  min-height: 100%;
  background-color: var(--color-bg-page);
}

/* ========== Page Header ========== */
.page-header {
  background: linear-gradient(135deg, #06beb6 0%, #48b1bf 100%);
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
  border-left: 4px solid #06beb6;
  padding-left: var(--spacing-md);
}

.section-desc {
  font-size: var(--font-size-md);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  margin-bottom: var(--spacing-xl);
}

/* ========== Timeline ========== */
.timeline-container {
  display: flex;
  align-items: stretch;
  gap: var(--spacing-md);
  margin: var(--spacing-xl) 0;
  overflow-x: auto;
  padding-bottom: var(--spacing-md);
}

.timeline-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.timeline-card {
  min-width: 180px;
  background: white;
  border: 2px solid;
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  transition: all var(--transition-base);
}

.timeline-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.timeline-header {
  padding: var(--spacing-md);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.timeline-icon {
  font-size: 28px;
  line-height: 1;
}

.timeline-number {
  width: 24px;
  height: 24px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
}

.timeline-body {
  padding: var(--spacing-md);
}

.timeline-title {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 var(--spacing-xs);
}

.timeline-duration {
  font-size: 12px;
  color: #6b7280;
  margin: 0 0 var(--spacing-xs);
}

.timeline-owner {
  font-size: 13px;
  color: #374151;
  margin: 0 0 var(--spacing-sm);
}

.timeline-output {
  font-size: 12px;
  margin-top: var(--spacing-sm);
  padding-top: var(--spacing-sm);
  border-top: 1px solid var(--color-border-light);
}

.output-label {
  color: #6b7280;
  font-weight: 500;
}

.output-value {
  color: #111827;
  font-weight: 600;
}

.timeline-arrow {
  font-size: 24px;
  color: #9ca3af;
  flex-shrink: 0;
}

/* ========== RACI Matrix ========== */
.raci-legend {
  display: flex;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
  padding: var(--spacing-md);
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border-radius: var(--border-radius-base);
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.legend-badge {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 13px;
  color: white;
}

.legend-badge.responsible {
  background: #10b981;
}

.legend-badge.accountable {
  background: #3b82f6;
}

.legend-badge.consulted {
  background: #f59e0b;
}

.legend-badge.informed {
  background: #9ca3af;
}

.legend-text {
  font-size: 13px;
  color: #374151;
}

.raci-table-wrapper {
  overflow-x: auto;
  margin: var(--spacing-lg) 0;
}

.raci-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border: 1px solid var(--color-border-light);
  border-radius: var(--border-radius-base);
}

.raci-table thead {
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
}

.raci-table th {
  padding: var(--spacing-md);
  text-align: center;
  border: 1px solid var(--color-border-light);
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.raci-table th.role-column {
  text-align: left;
  min-width: 150px;
}

.stage-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
}

.stage-icon {
  font-size: 20px;
}

.stage-name {
  font-size: 13px;
}

.raci-table td {
  padding: var(--spacing-md);
  text-align: center;
  border: 1px solid var(--color-border-light);
  font-size: 14px;
}

.role-name-cell {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  text-align: left !important;
}

.role-name-cell .role-icon {
  font-size: 20px;
}

.role-name-cell .role-name {
  font-weight: 500;
  color: #111827;
}

.raci-cell {
  background: #fafafa;
}

.raci-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 13px;
  color: white;
  margin: 0 2px;
}

.raci-badge.responsible {
  background: #10b981;
}

.raci-badge.accountable {
  background: #3b82f6;
}

.raci-badge.consulted {
  background: #f59e0b;
}

.raci-badge.informed {
  background: #9ca3af;
}

/* ========== Stages Collapse ========== */
.stages-collapse {
  border: none;
  margin-top: var(--spacing-lg);
}

.stages-collapse :deep(.el-collapse-item) {
  margin-bottom: var(--spacing-md);
  border: 1px solid var(--color-border-light);
  border-radius: var(--border-radius-base);
  overflow: hidden;
}

.stages-collapse :deep(.el-collapse-item__header) {
  background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
  padding: var(--spacing-md) var(--spacing-lg);
  border: none;
  font-size: 16px;
}

.stages-collapse :deep(.el-collapse-item__wrap) {
  border: none;
}

.stages-collapse :deep(.el-collapse-item__content) {
  padding: 0;
}

.collapse-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  width: 100%;
}

.collapse-icon {
  font-size: 24px;
  line-height: 1;
}

.collapse-number {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.collapse-name {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  flex: 1;
}

.collapse-tag {
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;
  color: white;
}

.stage-detail-content {
  padding: var(--spacing-xl);
  background: white;
}

.detail-section {
  margin-bottom: var(--spacing-xl);
  padding-bottom: var(--spacing-xl);
  border-bottom: 1px solid var(--color-border-light);
}

.detail-section:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.detail-title {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 var(--spacing-md);
}

.detail-text {
  font-size: 14px;
  color: #374151;
  line-height: 1.7;
  margin: 0;
}

.role-participation {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-md);
}

.participant-item {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border: 1px solid var(--color-border-light);
  border-radius: var(--border-radius-base);
  padding: var(--spacing-md);
}

.participant-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-sm);
}

.participant-role {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
}

.participant-badge {
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  color: white;
}

.participant-tasks {
  list-style: none;
  padding: 0;
  margin: 0;
}

.participant-tasks li {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.6;
  padding: var(--spacing-xs) 0;
  padding-left: var(--spacing-lg);
  position: relative;
}

.participant-tasks li::before {
  content: '▸';
  position: absolute;
  left: 0;
  color: #667eea;
  font-weight: 600;
}

.io-grid {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: var(--spacing-md);
  align-items: center;
}

.io-box {
  background: white;
  border: 2px solid var(--color-border-light);
  border-radius: var(--border-radius-base);
  padding: var(--spacing-md);
}

.input-box {
  border-color: #f59e0b;
}

.output-box {
  border-color: #10b981;
}

.io-label {
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  margin-bottom: var(--spacing-sm);
}

.io-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.io-list li {
  font-size: 13px;
  color: #374151;
  line-height: 1.6;
  padding: var(--spacing-xs) 0;
  padding-left: var(--spacing-md);
  position: relative;
}

.io-list li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: #667eea;
}

.io-arrow {
  font-size: 24px;
  color: #9ca3af;
}

.decision-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.decision-item {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.05) 0%, rgba(217, 119, 6, 0.05) 100%);
  border-left: 4px solid #f59e0b;
  padding: var(--spacing-md);
  border-radius: var(--border-radius-base);
}

.decision-header {
  font-size: 14px;
  font-weight: 600;
  color: #92400e;
  margin-bottom: var(--spacing-xs);
}

.decision-meta {
  font-size: 13px;
  color: #6b7280;
}

.decision-label {
  font-weight: 500;
  color: #374151;
}

.decision-value {
  color: #6b7280;
}

.decision-separator {
  margin: 0 var(--spacing-sm);
  color: #d1d5db;
}

.checklist {
  list-style: none;
  padding: 0;
  margin: 0;
}

.checklist li {
  font-size: 14px;
  color: #374151;
  line-height: 1.7;
  padding: var(--spacing-xs) 0;
  padding-left: var(--spacing-xl);
  position: relative;
}

.checklist li::before {
  content: '✓';
  position: absolute;
  left: 0;
  width: 20px;
  height: 20px;
  background: #10b981;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
}

/* ========== Handoff Flow ========== */
.handoff-flow {
  margin: var(--spacing-xl) 0;
}

.handoff-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.handoff-card {
  width: 100%;
  max-width: 800px;
  background: white;
  border: 2px solid var(--color-border-light);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  transition: all var(--transition-base);
}

.handoff-card:hover {
  box-shadow: var(--shadow-lg);
  border-color: #06beb6;
}

.handoff-header {
  background: linear-gradient(135deg, #06beb6 0%, #48b1bf 100%);
  padding: var(--spacing-md) var(--spacing-lg);
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.handoff-number {
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: white;
  font-size: 16px;
}

.handoff-roles {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex: 1;
}

.handoff-from,
.handoff-to {
  padding: var(--spacing-xs) var(--spacing-md);
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  font-size: 14px;
  font-weight: 600;
  color: white;
}

.handoff-icon {
  color: white;
  font-size: 20px;
}

.handoff-body {
  padding: var(--spacing-lg);
}

.handoff-deliverable {
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  margin-bottom: var(--spacing-md);
}

.handoff-items,
.handoff-standard {
  margin-bottom: var(--spacing-md);
}

.handoff-label {
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  margin-bottom: var(--spacing-xs);
}

.handoff-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.handoff-list li {
  font-size: 14px;
  color: #374151;
  line-height: 1.7;
  padding: var(--spacing-xs) 0;
  padding-left: var(--spacing-lg);
  position: relative;
}

.handoff-list li::before {
  content: '▸';
  position: absolute;
  left: 0;
  color: #06beb6;
  font-weight: 600;
}

.handoff-text {
  font-size: 14px;
  color: #374151;
  line-height: 1.7;
  margin: 0;
  padding: var(--spacing-sm);
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(5, 150, 105, 0.05) 100%);
  border-radius: var(--border-radius-base);
}

.handoff-connector {
  font-size: 32px;
  color: #06beb6;
  margin: var(--spacing-md) 0;
}

/* ========== Action Section ========== */
.action-section {
  text-align: center;
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

  .timeline-container {
    flex-direction: column;
  }

  .timeline-arrow {
    transform: rotate(90deg);
  }

  .raci-table-wrapper {
    font-size: 12px;
  }

  .raci-table th,
  .raci-table td {
    padding: var(--spacing-xs);
  }

  .role-participation {
    grid-template-columns: 1fr;
  }

  .io-grid {
    grid-template-columns: 1fr;
  }

  .io-arrow {
    transform: rotate(90deg);
  }
}
</style>
