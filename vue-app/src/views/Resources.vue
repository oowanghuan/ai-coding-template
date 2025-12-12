<template>
  <div class="resources-page">
    <!-- Hero Section -->
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

    <div class="container">
      <!-- 快速导航 -->
      <div class="quick-nav">
        <el-button @click="scrollToSection('prompts')" type="primary" plain>
          <el-icon><Document /></el-icon>
          Prompt 模板库
        </el-button>
        <el-button @click="scrollToSection('standards')" type="primary" plain>
          <el-icon><Folder /></el-icon>
          规范文档
        </el-button>
        <el-button @click="scrollToSection('tools')" type="primary" plain>
          <el-icon><Tools /></el-icon>
          自动化工具
        </el-button>
      </div>

      <!-- Part 1: Prompt 模板库 -->
      <div id="prompts" class="section">
        <div class="section-header">
          <h2 class="section-title">📝 Prompt 模板库</h2>
          <p class="section-subtitle">按角色和场景分类的结构化 Prompt，复制即用</p>
        </div>

        <div class="prompt-categories">
          <!-- AI Product Engineer Prompts -->
          <div class="category-card">
            <div class="category-header">
              <span class="category-icon">⭐</span>
              <h3 class="category-title">AI Product Engineer</h3>
            </div>
            <el-collapse v-model="activePrompts.aipe" accordion>
              <el-collapse-item
                v-for="(prompt, index) in aipePrompts"
                :key="index"
                :name="index"
              >
                <template #title>
                  <div class="prompt-title">
                    <span class="prompt-icon">{{ prompt.icon }}</span>
                    <span>{{ prompt.name }}</span>
                    <el-tag size="small" :type="prompt.tagType">{{ prompt.phase }}</el-tag>
                  </div>
                </template>
                <div class="prompt-content">
                  <p class="prompt-description">{{ prompt.description }}</p>
                  <div class="prompt-usage">
                    <strong>使用场景：</strong>{{ prompt.usage }}
                  </div>
                  <div class="code-block">
                    <div class="code-header">
                      <span class="code-language">Prompt</span>
                      <el-button size="small" text @click="copyToClipboard(prompt.template, prompt.name)">
                        <el-icon><CopyDocument /></el-icon>
                        复制
                      </el-button>
                    </div>
                    <pre class="code-content">{{ prompt.template }}</pre>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>

          <!-- 架构师 Prompts -->
          <div class="category-card">
            <div class="category-header">
              <span class="category-icon">🏗️</span>
              <h3 class="category-title">系统架构师</h3>
            </div>
            <el-collapse v-model="activePrompts.architect" accordion>
              <el-collapse-item
                v-for="(prompt, index) in architectPrompts"
                :key="index"
                :name="index"
              >
                <template #title>
                  <div class="prompt-title">
                    <span class="prompt-icon">{{ prompt.icon }}</span>
                    <span>{{ prompt.name }}</span>
                    <el-tag size="small" type="info">{{ prompt.phase }}</el-tag>
                  </div>
                </template>
                <div class="prompt-content">
                  <p class="prompt-description">{{ prompt.description }}</p>
                  <div class="prompt-usage">
                    <strong>使用场景：</strong>{{ prompt.usage }}
                  </div>
                  <div class="code-block">
                    <div class="code-header">
                      <span class="code-language">Prompt</span>
                      <el-button size="small" text @click="copyToClipboard(prompt.template, prompt.name)">
                        <el-icon><CopyDocument /></el-icon>
                        复制
                      </el-button>
                    </div>
                    <pre class="code-content">{{ prompt.template }}</pre>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>

          <!-- QA Prompts -->
          <div class="category-card">
            <div class="category-header">
              <span class="category-icon">🔍</span>
              <h3 class="category-title">AI QA</h3>
            </div>
            <el-collapse v-model="activePrompts.qa" accordion>
              <el-collapse-item
                v-for="(prompt, index) in qaPrompts"
                :key="index"
                :name="index"
              >
                <template #title>
                  <div class="prompt-title">
                    <span class="prompt-icon">{{ prompt.icon }}</span>
                    <span>{{ prompt.name }}</span>
                    <el-tag size="small" type="warning">{{ prompt.phase }}</el-tag>
                  </div>
                </template>
                <div class="prompt-content">
                  <p class="prompt-description">{{ prompt.description }}</p>
                  <div class="prompt-usage">
                    <strong>使用场景：</strong>{{ prompt.usage }}
                  </div>
                  <div class="code-block">
                    <div class="code-header">
                      <span class="code-language">Prompt</span>
                      <el-button size="small" text @click="copyToClipboard(prompt.template, prompt.name)">
                        <el-icon><CopyDocument /></el-icon>
                        复制
                      </el-button>
                    </div>
                    <pre class="code-content">{{ prompt.template }}</pre>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </div>
      </div>

      <!-- Part 2: 规范文档 -->
      <div id="standards" class="section">
        <div class="section-header">
          <h2 class="section-title">📐 规范文档</h2>
          <p class="section-subtitle">标准化的规范文档模板，确保团队一致性</p>
        </div>

        <el-row :gutter="24">
          <el-col :xs="24" :md="12" v-for="(standard, index) in standards" :key="index">
            <el-card class="standard-card" shadow="hover">
              <div class="standard-header">
                <span class="standard-icon">{{ standard.icon }}</span>
                <h3 class="standard-title">{{ standard.name }}</h3>
              </div>
              <p class="standard-description">{{ standard.description }}</p>
              <div class="standard-includes">
                <strong>包含内容：</strong>
                <ul class="standard-list">
                  <li v-for="(item, i) in standard.includes" :key="i">{{ item }}</li>
                </ul>
              </div>
              <div class="code-block">
                <div class="code-header">
                  <span class="code-language">{{ standard.language }}</span>
                  <el-button size="small" text @click="copyToClipboard(standard.template, standard.name)">
                    <el-icon><CopyDocument /></el-icon>
                    复制
                  </el-button>
                </div>
                <pre class="code-content">{{ standard.template }}</pre>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- Part 3: 自动化工具 -->
      <div id="tools" class="section">
        <div class="section-header">
          <h2 class="section-title">🤖 自动化工具</h2>
          <p class="section-subtitle">提升效率的脚本和配置文件</p>
        </div>

        <div class="tools-grid">
          <el-card
            v-for="(tool, index) in tools"
            :key="index"
            class="tool-card"
            shadow="hover"
          >
            <div class="tool-header">
              <span class="tool-icon">{{ tool.icon }}</span>
              <div class="tool-info">
                <h3 class="tool-title">{{ tool.name }}</h3>
                <el-tag size="small" :type="tool.tagType">{{ tool.type }}</el-tag>
              </div>
            </div>
            <p class="tool-description">{{ tool.description }}</p>
            <div class="tool-usage-section" v-if="tool.usage">
              <strong>使用方法：</strong>
              <code class="inline-code">{{ tool.usage }}</code>
            </div>
            <div class="code-block">
              <div class="code-header">
                <span class="code-language">{{ tool.language }}</span>
                <el-button size="small" text @click="copyToClipboard(tool.code, tool.name)">
                  <el-icon><CopyDocument /></el-icon>
                  复制
                </el-button>
              </div>
              <pre class="code-content">{{ tool.code }}</pre>
            </div>
          </el-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document, Folder, Tools, CopyDocument, HomeFilled } from '@element-plus/icons-vue'

const router = useRouter()
const activeTab = ref('resources')

// Tab 切换处理
const handleTabChange = (value) => {
  if (value === 'workflow') {
    router.push('/workflow-guide')
  }
}

// Active collapse items
const activePrompts = ref({
  aipe: null,
  architect: null,
  qa: null
})

// AI Product Engineer Prompts
const aipePrompts = ref([
  {
    icon: '📝',
    name: '编写 UI Flow Spec',
    phase: 'Phase 1',
    tagType: 'primary',
    description: '根据需求和 6 件套文档，编写详细的 UI Flow Spec',
    usage: '收到 PM 需求和架构师的 6 件套后，开始编写 Spec',
    template: `你是一名 AI Product Engineer，负责将产品需求转化为详细的 UI Flow Spec。

我现在有以下输入：
1. 产品需求：[描述需求]
2. 架构师提供的 6 件套文档：
   - 模块划分图
   - API 规范文档
   - 数据库 Schema
   - Design System 文档
   - 部署架构图
   - 技术栈清单

请帮我编写一份详细的 UI Flow Spec，包含：

## 1. 功能概述
- 目标：[要解决的问题]
- 用户场景：[典型使用场景]
- 成功标准：[如何衡量成功]

## 2. 用户流程
使用 Mermaid 图表描述完整的用户流程，包括：
- 入口点
- 主要步骤
- 决策分支
- 错误处理
- 出口点

## 3. 界面元素
对每个界面，详细说明：
- 页面标题和导航
- 主要组件（按 Design System 命名）
- 数据展示格式
- 交互元素（按钮、表单等）
- 状态变化（loading、error、success）

## 4. 数据流
- 需要调用的 API（引用 API 规范）
- 数据格式和验证规则
- 状态管理需求

## 5. 边界情况
- 空状态
- 错误状态
- Loading 状态
- 权限不足

请使用 Markdown 格式输出，确保所有组件名称都符合 Design System 规范。`
  },
  {
    icon: '🎨',
    name: '生成 UI Demo',
    phase: 'Phase 2',
    tagType: 'success',
    description: '使用 ui_demo skill 根据 Spec 生成可交互的 Demo',
    usage: 'UI Flow Spec 完成并通过评审后，生成 Demo',
    template: `你现在要使用 ui_demo skill 来生成 UI Demo。

输入文件：
- docs/<feature-slug>/11_UI_FLOW_SPEC.md

请按照以下步骤：
1. 读取 UI Flow Spec
2. 读取 _templates/_foundation_templates/_ui_system_template/ 下的全局 Design System 模板
3. 生成符合 Design System 的可运行 Demo
4. 确保 Demo 包含所有关键交互流程
5. 添加必要的 mock 数据

生成的 Demo 应该：
- 使用真实的组件（不是占位符）
- 完整实现用户流程
- 包含所有状态（loading、error、success）
- 响应式设计
- 可以在浏览器中运行

请开始生成 Demo。`
  },
  {
    icon: '📋',
    name: '编写 Dev Plan',
    phase: 'Phase 3',
    tagType: 'warning',
    description: '根据评审后的 Spec 和 Demo，制定详细的开发计划',
    usage: 'Demo 评审通过后，开始制定开发计划',
    template: `你是 AI Product Engineer，现在要制定详细的开发计划。

已完成的工作：
- ✅ UI Flow Spec（已评审通过）
- ✅ UI Demo（已评审通过）
- ✅ 设计师的反馈已整合

现在请帮我编写 Dev Plan，包含：

## 1. 任务分解
将功能分解为可独立开发的任务：
- 任务 1：[任务名称]
  - 描述：[做什么]
  - 涉及文件：[文件列表]
  - 依赖：[依赖的其他任务]
  - 预计工作量：[时间估计]

## 2. 技术方案
- 状态管理方案
- 数据获取策略
- 组件复用策略
- 性能优化点

## 3. API 清单
列出需要调用的所有 API：
- GET /api/xxx - [用途]
- POST /api/xxx - [用途]

## 4. 组件清单
需要创建/修改的组件：
- ComponentName - [用途]
- 使用的 Design System 组件

## 5. 测试要点
- 单元测试重点
- 集成测试场景
- E2E 测试流程

## 6. 风险和注意事项
- 技术风险
- 依赖风险
- 需要特别注意的点

请使用 Markdown 格式输出到 docs/<feature-slug>/20_DEV_PLAN_FINAL.md`
  },
  {
    icon: '💻',
    name: '执行开发任务',
    phase: 'Phase 4',
    tagType: 'danger',
    description: '按照 Dev Plan 执行具体的开发任务',
    usage: '开始编码时使用',
    template: `你是 AI Product Engineer，现在要执行具体的开发任务。

当前任务：[任务名称]

参考文档：
- docs/<feature-slug>/11_UI_FLOW_SPEC.md
- docs/<feature-slug>/20_DEV_PLAN_FINAL.md
- _templates/_foundation_templates/_ui_system_template/ (Design System 模板)

请按照以下步骤执行：

1. **理解任务**
   - 阅读任务描述
   - 理解技术方案
   - 确认依赖已完成

2. **编写代码**
   - 严格遵循 Dev Plan 中的技术方案
   - 使用 Design System 中的组件
   - 遵循代码规范
   - 添加必要的注释

3. **自测**
   - 功能是否完整
   - 是否符合 Spec 描述
   - 是否处理了边界情况
   - 性能是否满足要求

4. **更新 Progress Log**
   - 记录完成的工作
   - 记录遇到的问题和解决方案
   - 更新任务状态

请开始执行任务，并在完成后更新 docs/<feature-slug>/30_PROGRESS_LOG.md`
  }
])

// 架构师 Prompts
const architectPrompts = ref([
  {
    icon: '🎯',
    name: 'Kickoff - 生成 6 件套',
    phase: 'Kickoff',
    description: '项目启动时，根据需求生成完整的 6 件套文档',
    usage: '收到新项目或大功能需求时使用',
    template: `你是一名资深系统架构师，负责项目的技术架构设计。

我现在有一个新项目/功能需求：
[描述需求]

请帮我生成完整的 6 件套文档：

## 1. 模块划分图
使用 Mermaid 图表展示：
- 前端模块划分
- 后端服务划分
- 模块间的依赖关系
- 数据流向

## 2. API 规范文档
使用 OpenAPI 3.0 格式，定义：
- 所有 API 端点
- 请求/响应格式
- 认证方式
- 错误码定义

## 3. 数据库 Schema
提供 SQL DDL 或 ER 图，包含：
- 表结构设计
- 字段类型和约束
- 索引设计
- 表关系

## 4. Design System 文档
定义前端设计规范：
- 颜色系统
- 字体系统
- 间距系统
- 组件库清单
- 使用规范

## 5. 部署架构图
说明系统部署方案：
- 服务器架构
- 负载均衡
- 数据库部署
- 缓存策略
- CDN 配置

## 6. 技术栈清单
列出所有技术选型：
- 前端框架和库
- 后端框架和库
- 数据库
- 中间件
- 工具链

所有文档请使用 Markdown 格式，图表使用 Mermaid。`
  },
  {
    icon: '🔍',
    name: '架构评审',
    phase: 'Review',
    description: '评审 AI PE 提交的技术方案',
    usage: 'AI PE 提交 Dev Plan 后进行评审',
    template: `你是系统架构师，现在要评审 AI Product Engineer 提交的开发计划。

评审重点：

## 1. 架构一致性
检查是否符合：
- 模块划分是否合理
- 是否遵循了系统架构设计
- 是否正确使用了架构模式

## 2. API 使用
检查：
- API 调用是否符合规范
- 是否有遗漏的 API
- 错误处理是否完整

## 3. 数据流
验证：
- 数据流向是否清晰
- 状态管理是否合理
- 是否有性能瓶颈

## 4. 扩展性
评估：
- 是否易于扩展
- 是否考虑了未来需求
- 技术债务风险

请对以下 Dev Plan 进行评审：
[粘贴 Dev Plan 内容]

请给出：
1. 通过/不通过的结论
2. 具体的问题和建议
3. 需要修改的地方`
  }
])

// QA Prompts
const qaPrompts = ref([
  {
    icon: '📋',
    name: '生成测试计划',
    phase: 'Phase 5',
    description: '根据 Spec 和 Dev Plan 生成完整的测试计划',
    usage: '开发完成后，开始测试前使用',
    template: `你是 AI QA，负责制定测试计划。

参考文档：
- docs/<feature-slug>/11_UI_FLOW_SPEC.md
- docs/<feature-slug>/20_DEV_PLAN_FINAL.md

请生成完整的测试计划：

## 1. 测试范围
- 功能测试范围
- 性能测试范围
- 兼容性测试范围

## 2. 测试用例
对每个功能点，编写测试用例：
### 用例 1：[用例名称]
- 前置条件：
- 测试步骤：
- 预期结果：
- 实际结果：
- 状态：

## 3. 边界测试
- 空数据测试
- 大数据量测试
- 异常输入测试
- 权限测试

## 4. 自动化测试
- 单元测试清单
- 集成测试清单
- E2E 测试清单

## 5. 性能测试
- 响应时间要求
- 并发用户数要求
- 资源使用要求

请使用 Markdown 格式输出到 docs/<feature-slug>/40_TEST_PLAN.md`
  },
  {
    icon: '🤖',
    name: '执行自动化测试',
    phase: 'Phase 5',
    description: '使用 Claude Code 和 MCP 工具执行自动化测试',
    usage: '测试计划完成后，执行自动化测试',
    template: `你是 AI QA，现在要执行自动化测试。

测试环境：
- URL: [测试环境 URL]
- 测试账号：[账号信息]

可用工具：
- Chrome Dev MCP（浏览器自动化）
- test_runner skill（运行测试脚本）

请按照以下步骤执行：

1. **启动测试环境**
   - 打开浏览器
   - 导航到测试页面
   - 登录测试账号

2. **执行测试用例**
   按照 docs/<feature-slug>/40_TEST_PLAN.md 中的测试用例：
   - 执行每个测试步骤
   - 记录实际结果
   - 截图保存证据

3. **bug 报告**
   发现问题时，记录：
   - Bug 描述
   - 复现步骤
   - 预期 vs 实际
   - 截图/视频
   - 严重程度

4. **生成测试报告**
   - 测试通过率
   - 发现的 bug 列表
   - 测试覆盖率
   - 建议

请开始执行测试。`
  }
])

// 规范文档
const standards = ref([
  {
    icon: '🎨',
    name: 'Design System 规范',
    description: '前端设计系统规范，定义颜色、字体、组件等设计元素',
    language: 'Markdown',
    includes: [
      '颜色系统（Primary、Secondary、状态色）',
      '字体系统（字号、字重、行高）',
      '间距系统（Spacing Scale）',
      '组件规范（Button、Input、Card 等）',
      '响应式断点',
      '动画规范'
    ],
    template: `# Design System 规范

## 1. 颜色系统

### 主色调
- Primary: #409EFF
- Primary Light: #79BBFF
- Primary Dark: #337ECC

### 功能色
- Success: #67C23A
- Warning: #E6A23C
- Danger: #F56C6C
- Info: #909399

### 中性色
- Text Primary: #303133
- Text Regular: #606266
- Text Secondary: #909399
- Border Base: #DCDFE6
- Background: #F5F7FA

## 2. 字体系统

### 字号
- xs: 12px
- sm: 14px
- base: 16px
- lg: 18px
- xl: 20px
- 2xl: 24px
- 3xl: 30px

### 字重
- light: 300
- normal: 400
- medium: 500
- semibold: 600
- bold: 700

### 行高
- tight: 1.25
- base: 1.5
- relaxed: 1.75

## 3. 间距系统
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px
- 2xl: 48px

## 4. 组件规范

### Button
- 尺寸：small (28px), default (32px), large (40px)
- 类型：primary, success, warning, danger, info, text
- 状态：default, hover, active, disabled

### Input
- 尺寸：small, default, large
- 类型：text, password, number, textarea
- 状态：default, focus, error, disabled

## 5. 响应式断点
- xs: < 768px (mobile)
- sm: ≥ 768px (tablet)
- md: ≥ 992px (desktop)
- lg: ≥ 1200px (large desktop)
- xl: ≥ 1920px (extra large)

## 6. 动画规范
- Duration: 0.3s (fast), 0.5s (base), 0.8s (slow)
- Easing: ease-in-out, ease-out, cubic-bezier(0.4, 0, 0.2, 1)`
  },
  {
    icon: '🔌',
    name: 'API 规范文档',
    description: 'RESTful API 设计规范，定义接口格式、错误码等',
    language: 'YAML',
    includes: [
      'RESTful 设计原则',
      '请求/响应格式',
      '认证方式（JWT）',
      '错误码定义',
      '分页规范',
      '版本控制'
    ],
    template: `openapi: 3.0.0
info:
  title: API 规范文档
  version: 1.0.0
  description: 项目 API 接口规范

servers:
  - url: https://api.example.com/v1
    description: 生产环境
  - url: https://api-staging.example.com/v1
    description: 测试环境

# 认证方式
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  # 通用响应格式
  schemas:
    SuccessResponse:
      type: object
      properties:
        code:
          type: integer
          example: 0
        message:
          type: string
          example: "success"
        data:
          type: object

    ErrorResponse:
      type: object
      properties:
        code:
          type: integer
          example: 400
        message:
          type: string
          example: "Bad Request"
        details:
          type: string

    PaginatedResponse:
      type: object
      properties:
        code:
          type: integer
        data:
          type: object
          properties:
            items:
              type: array
            total:
              type: integer
            page:
              type: integer
            pageSize:
              type: integer

# 通用错误码
# 0: 成功
# 400: 请求参数错误
# 401: 未认证
# 403: 无权限
# 404: 资源不存在
# 500: 服务器错误

paths:
  /users:
    get:
      summary: 获取用户列表
      security:
        - bearerAuth: []
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: pageSize
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/PaginatedResponse'`
  },
  {
    icon: '🗄️',
    name: '数据库 Schema 规范',
    description: '数据库设计规范，定义表结构、命名规则等',
    language: 'SQL',
    includes: [
      '命名规范（snake_case）',
      '字段类型选择',
      '主键和索引设计',
      '外键约束',
      '时间戳字段',
      '软删除标记'
    ],
    template: `-- 数据库 Schema 规范

-- 命名规范：
-- 1. 表名：复数形式，snake_case，如 users, order_items
-- 2. 字段名：snake_case，如 user_name, created_at
-- 3. 主键：id (BIGINT AUTO_INCREMENT)
-- 4. 外键：<table_name>_id，如 user_id, product_id
-- 5. 布尔字段：is_<name>，如 is_active, is_deleted

-- 通用字段：
-- id: 主键
-- created_at: 创建时间
-- updated_at: 更新时间
-- deleted_at: 软删除时间（可选）

-- 示例：用户表
CREATE TABLE users (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  username VARCHAR(50) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(100),
  avatar_url VARCHAR(500),
  is_active BOOLEAN DEFAULT TRUE,
  is_email_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL,

  INDEX idx_email (email),
  INDEX idx_username (username),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 示例：订单表
CREATE TABLE orders (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  order_number VARCHAR(50) NOT NULL UNIQUE,
  status ENUM('pending', 'paid', 'shipped', 'completed', 'cancelled') DEFAULT 'pending',
  total_amount DECIMAL(10, 2) NOT NULL,
  currency VARCHAR(3) DEFAULT 'USD',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  FOREIGN KEY (user_id) REFERENCES users(id),
  INDEX idx_user_id (user_id),
  INDEX idx_status (status),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;`
  },
  {
    icon: '✅',
    name: '测试规范',
    description: '自动化测试规范，定义测试策略和编写规范',
    language: 'Markdown',
    includes: [
      '测试金字塔（单元、集成、E2E）',
      '测试覆盖率要求',
      '命名规范',
      'Mock 策略',
      '测试数据管理',
      'CI/CD 集成'
    ],
    template: `# 测试规范

## 1. 测试策略

### 测试金字塔
- 单元测试：70%（测试函数、组件逻辑）
- 集成测试：20%（测试模块间交互）
- E2E 测试：10%（测试关键用户流程）

### 覆盖率要求
- 核心业务逻辑：≥ 90%
- 工具函数：≥ 80%
- UI 组件：≥ 70%
- 整体覆盖率：≥ 75%

## 2. 命名规范

### 测试文件
- 单元测试：\`<component>.test.ts\`
- 集成测试：\`<feature>.integration.test.ts\`
- E2E 测试：\`<flow>.e2e.test.ts\`

### 测试用例
\`\`\`typescript
describe('ComponentName', () => {
  describe('methodName', () => {
    it('should do something when condition', () => {
      // Test implementation
    })

    it('should throw error when invalid input', () => {
      // Test implementation
    })
  })
})
\`\`\`

## 3. 单元测试

### 原则
- 每个测试只测一个功能点
- 测试应该独立，不依赖其他测试
- 使用 AAA 模式：Arrange, Act, Assert

### 示例
\`\`\`typescript
import { calculateTotal } from './utils'

describe('calculateTotal', () => {
  it('should return sum of prices', () => {
    // Arrange
    const items = [
      { price: 10, quantity: 2 },
      { price: 20, quantity: 1 }
    ]

    // Act
    const result = calculateTotal(items)

    // Assert
    expect(result).toBe(40)
  })
})
\`\`\`

## 4. 集成测试

测试多个模块的交互：
- API 调用和响应处理
- 状态管理的完整流程
- 组件间的数据传递

## 5. E2E 测试

测试关键用户流程：
- 用户注册和登录
- 核心业务流程
- 支付流程
- 错误处理

## 6. Mock 策略

### API Mock
使用 MSW (Mock Service Worker) mock API：
\`\`\`typescript
import { rest } from 'msw'
import { setupServer } from 'msw/node'

const server = setupServer(
  rest.get('/api/users', (req, res, ctx) => {
    return res(ctx.json({ users: [] }))
  })
)
\`\`\`

### 组件 Mock
\`\`\`typescript
vi.mock('./HeavyComponent', () => ({
  default: () => <div>Mocked Component</div>
}))
\`\`\`

## 7. CI/CD 集成

测试应该在以下情况自动运行：
- 每次 commit
- PR 创建/更新
- 合并到主分支前

不通过测试的代码不允许合并。`
  }
])

// 自动化工具
const tools = ref([
  {
    icon: '🚀',
    name: '功能初始化脚本',
    type: 'Bash Script',
    tagType: 'primary',
    description: '快速创建新功能的完整文档结构',
    usage: './tools/init_feature.sh <feature-slug> "<Feature Name>"',
    language: 'bash',
    code: `#!/usr/bin/env bash
# tools/init_feature.sh
# 快速初始化新功能的文档结构

set -e

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <feature-slug> <feature-name>"
  echo "Example: $0 subscription-billing \"Subscription Billing\""
  exit 1
fi

FEATURE_SLUG=$1
FEATURE_NAME=$2
FEATURE_DIR="docs/$FEATURE_SLUG"

echo "🚀 Initializing feature: $FEATURE_NAME ($FEATURE_SLUG)"

# 创建目录
mkdir -p "$FEATURE_DIR"

# 创建 8 个文档
cat > "$FEATURE_DIR/00_CONTEXT.md" << EOF
# $FEATURE_NAME - Context

## 业务背景
TODO: 描述要解决的问题

## 目标用户
TODO: 描述目标用户群体

## 成功标准
TODO: 如何衡量功能成功

## 技术约束
TODO: 技术限制和依赖

## 与现有系统的关系
TODO: 如何与现有系统集成
EOF

cat > "$FEATURE_DIR/11_UI_FLOW_SPEC.md" << EOF
# $FEATURE_NAME - UI Flow Spec

## 1. 功能概述
TODO

## 2. 用户流程
\`\`\`mermaid
graph TD
  A[开始] --> B[步骤1]
  B --> C[步骤2]
  C --> D[结束]
\`\`\`

## 3. 界面元素
TODO

## 4. 数据流
TODO

## 5. 边界情况
TODO
EOF

cat > "$FEATURE_DIR/12_UI_DEMO_NOTES.md" << EOF
# $FEATURE_NAME - UI Demo Notes

## Demo 生成时间
$(date)

## 评审反馈
TODO: 记录设计评审反馈

## 修改历史
TODO: 记录修改内容
EOF

cat > "$FEATURE_DIR/20_DEV_PLAN_FINAL.md" << EOF
# $FEATURE_NAME - Development Plan

## 1. 任务分解
TODO

## 2. 技术方案
TODO

## 3. API 清单
TODO

## 4. 组件清单
TODO

## 5. 测试要点
TODO

## 6. 风险和注意事项
TODO
EOF

cat > "$FEATURE_DIR/30_PROGRESS_LOG.md" << EOF
# $FEATURE_NAME - Progress Log

## 进度概览
- 状态: Not Started
- 开始时间:
- 预计完成:
- 实际完成:

## 开发日志
### $(date +%Y-%m-%d)
- 初始化项目文档
EOF

cat > "$FEATURE_DIR/40_TEST_PLAN.md" << EOF
# $FEATURE_NAME - Test Plan

## 1. 测试范围
TODO

## 2. 测试用例
TODO

## 3. 边界测试
TODO

## 4. 自动化测试
TODO

## 5. 性能测试
TODO
EOF

cat > "$FEATURE_DIR/41_TEST_RESULTS.md" << EOF
# $FEATURE_NAME - Test Results

## 测试执行时间
TODO

## 测试结果汇总
- 通过: 0
- 失败: 0
- 跳过: 0

## 发现的问题
TODO

## 测试截图
TODO
EOF

cat > "$FEATURE_DIR/50_RELEASE_NOTE.md" << EOF
# $FEATURE_NAME - Release Note

## 版本
TODO: v1.0.0

## 发布日期
TODO

## 新功能
- $FEATURE_NAME

## 改进
TODO

## 修复
TODO

## 已知问题
TODO
EOF

echo "✅ Feature initialized at $FEATURE_DIR"
echo ""
echo "Next steps:"
echo "1. Fill in docs/$FEATURE_SLUG/00_CONTEXT.md"
echo "2. Write UI Flow Spec in 11_UI_FLOW_SPEC.md"
echo "3. Generate UI Demo"
echo "4. Start development"
`
  },
  {
    icon: '📊',
    name: '进度同步脚本',
    type: 'Bash Script',
    tagType: 'success',
    description: '将 Progress Log 同步到项目管理工具',
    usage: './tools/sync_progress.sh <feature-slug>',
    language: 'bash',
    code: `#!/usr/bin/env bash
# tools/sync_progress.sh
# 同步 Progress Log 到项目管理工具

set -e

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <feature-slug>"
  exit 1
fi

FEATURE_SLUG=$1
PROGRESS_FILE="docs/$FEATURE_SLUG/30_PROGRESS_LOG.md"

if [ ! -f "$PROGRESS_FILE" ]; then
  echo "Error: $PROGRESS_FILE not found"
  exit 1
fi

echo "📊 Syncing progress for $FEATURE_SLUG..."

# 提取进度信息
STATUS=$(grep "^- 状态:" "$PROGRESS_FILE" | cut -d: -f2 | xargs)
START_DATE=$(grep "^- 开始时间:" "$PROGRESS_FILE" | cut -d: -f2 | xargs)
PLANNED_END=$(grep "^- 预计完成:" "$PROGRESS_FILE" | cut -d: -f2 | xargs)
ACTUAL_END=$(grep "^- 实际完成:" "$PROGRESS_FILE" | cut -d: -f2 | xargs)

echo "Status: $STATUS"
echo "Start Date: $START_DATE"
echo "Planned End: $PLANNED_END"
echo "Actual End: $ACTUAL_END"

# TODO: 集成你的项目管理工具 API
# 示例：发送到 Jira/Linear/GitHub Projects

# 示例：更新 GitHub Issue
# gh issue edit <issue-number> --add-label "$STATUS"

# 示例：发送 Slack 通知
# curl -X POST "https://hooks.slack.com/services/YOUR/WEBHOOK/URL" \\
#   -H 'Content-Type: application/json' \\
#   -d "{\"text\": \"Progress update for $FEATURE_SLUG: $STATUS\"}"

echo "✅ Progress synced"`
  },
  {
    icon: '📝',
    name: 'Release Note 生成器',
    type: 'Bash Script',
    tagType: 'warning',
    description: '根据 Git commits 自动生成 Release Note',
    usage: './tools/generate_release_note.sh <feature-slug> <version>',
    language: 'bash',
    code: `#!/usr/bin/env bash
# tools/generate_release_note.sh
# 根据 Git commits 自动生成 Release Note

set -e

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 <feature-slug> <version>"
  echo "Example: $0 subscription-billing v1.0.0"
  exit 1
fi

FEATURE_SLUG=$1
VERSION=$2
RELEASE_FILE="docs/$FEATURE_SLUG/50_RELEASE_NOTE.md"
TODAY=$(date +%Y-%m-%d)

echo "📝 Generating release note for $FEATURE_SLUG $VERSION..."

# 获取最近的 commits
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -z "$LAST_TAG" ]; then
  COMMITS=$(git log --oneline --no-merges)
else
  COMMITS=$(git log $LAST_TAG..HEAD --oneline --no-merges)
fi

# 分类 commits
FEATURES=$(echo "$COMMITS" | grep -i "^[a-f0-9]* feat" || true)
FIXES=$(echo "$COMMITS" | grep -i "^[a-f0-9]* fix" || true)
IMPROVEMENTS=$(echo "$COMMITS" | grep -i "^[a-f0-9]* refactor\\|improve\\|perf" || true)

# 生成 Release Note
cat > "$RELEASE_FILE" << EOF
# Release Note - $VERSION

## 发布日期
$TODAY

## 版本信息
- Version: $VERSION
- Feature: $FEATURE_SLUG

## 新功能 ✨
EOF

if [ -n "$FEATURES" ]; then
  echo "$FEATURES" | sed 's/^[a-f0-9]* feat[:(]*/- /' | sed 's/)://' >> "$RELEASE_FILE"
else
  echo "- 无" >> "$RELEASE_FILE"
fi

cat >> "$RELEASE_FILE" << EOF

## 改进 🚀
EOF

if [ -n "$IMPROVEMENTS" ]; then
  echo "$IMPROVEMENTS" | sed 's/^[a-f0-9]* \\(refactor\\|improve\\|perf\\)[:(]*/- /' | sed 's/)://' >> "$RELEASE_FILE"
else
  echo "- 无" >> "$RELEASE_FILE"
fi

cat >> "$RELEASE_FILE" << EOF

## 修复 🐛
EOF

if [ -n "$FIXES" ]; then
  echo "$FIXES" | sed 's/^[a-f0-9]* fix[:(]*/- /' | sed 's/)://' >> "$RELEASE_FILE"
else
  echo "- 无" >> "$RELEASE_FILE"
fi

cat >> "$RELEASE_FILE" << EOF

## 已知问题
- 待补充

## 升级指南
1. 备份当前数据
2. 运行迁移脚本
3. 重启服务
4. 验证功能

## 贡献者
$(git log $LAST_TAG..HEAD --format='- %an' | sort -u)
EOF

echo "✅ Release note generated at $RELEASE_FILE"
cat "$RELEASE_FILE"`
  },
  {
    icon: '⚙️',
    name: 'Claude Code Skills 配置',
    type: 'JSON Config',
    tagType: 'info',
    description: 'Claude Code 的 Skills 配置文件',
    usage: '保存到 .claude/skills.json',
    language: 'json',
    code: `{
  "skills": [
    {
      "name": "ui_demo",
      "description": "Generate UI Demo from Spec",
      "prompt": "你是 UI System Architect，负责根据 UI Flow Spec 生成可运行的 Demo。\\n\\n请按照以下步骤：\\n1. 读取 docs/<feature-slug>/11_UI_FLOW_SPEC.md\\n2. 读取 _templates/_foundation_templates/_ui_system_template/ 下的全局 Design System 模板\\n3. 生成符合 Design System 的可运行 HTML/JS/CSS Demo\\n4. 确保 Demo 包含所有关键交互流程\\n5. 添加必要的 mock 数据\\n\\nDemo 要求：\\n- 使用真实的组件（不是占位符）\\n- 完整实现用户流程\\n- 包含所有状态（loading、error、success）\\n- 响应式设计\\n- 可以在浏览器中运行\\n\\n生成完成后，将 Demo 保存到 demos/<feature-slug>/ 目录"
    },
    {
      "name": "review_alignment",
      "description": "Update Progress Log with completed work",
      "prompt": "你是 review_alignment agent，负责更新 Progress Log。\\n\\n请执行：\\n1. 检查最近完成的 commits\\n2. 识别完成的任务\\n3. 更新 docs/<feature-slug>/30_PROGRESS_LOG.md\\n4. 记录遇到的问题和解决方案\\n5. 更新进度状态\\n\\n更新格式：\\n### YYYY-MM-DD\\n- [完成] 任务名称\\n  - 完成内容描述\\n  - 遇到的问题\\n  - 解决方案\\n- [进行中] 当前任务\\n  - 进度说明"
    },
    {
      "name": "test_runner",
      "description": "Run automated tests and generate report",
      "prompt": "你是 test_runner agent，负责执行自动化测试。\\n\\n请执行：\\n1. 读取 docs/<feature-slug>/40_TEST_PLAN.md\\n2. 运行单元测试\\n3. 运行集成测试\\n4. 运行 E2E 测试（使用 Chrome Dev MCP）\\n5. 生成测试报告\\n\\n报告包含：\\n- 测试通过率\\n- 失败的测试用例\\n- 测试覆盖率\\n- 发现的问题\\n- 测试截图（E2E）\\n\\n将结果保存到 docs/<feature-slug>/41_TEST_RESULTS.md"
    },
    {
      "name": "main_agent",
      "description": "Main orchestration agent",
      "prompt": "你是 main_agent，负责协调整个开发流程。\\n\\n职责：\\n1. 理解任务需求\\n2. 分解为子任务\\n3. 调用合适的 skills/agents\\n4. 监控进度\\n5. 处理异常\\n\\n可调用的 agents：\\n- ui_demo: 生成 UI Demo\\n- review_alignment: 更新进度\\n- test_runner: 执行测试\\n\\n工作流程：\\nPhase 1 → Phase 2 (ui_demo) → Phase 3 → Phase 4 (review_alignment) → Phase 5 (test_runner) → Phase 6"
    }
  ]
}`
  },
  {
    icon: '🔧',
    name: 'MCP 工具配置',
    type: 'JSON Config',
    tagType: 'danger',
    description: 'Claude Code 的 MCP 服务器配置',
    usage: '保存到 ~/Library/Application Support/Claude/claude_desktop_config.json',
    language: 'json',
    code: `{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-supabase"
      ],
      "env": {
        "SUPABASE_URL": "your-project-url",
        "SUPABASE_SERVICE_ROLE_KEY": "your-service-role-key"
      }
    },
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-chrome-devtools"
      ]
    }
  }
}`
  }
])

// 滚动到指定 section
const scrollToSection = (sectionId) => {
  const element = document.getElementById(sectionId)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

// 复制到剪贴板
const copyToClipboard = (text, name) => {
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success(`${name} 已复制到剪贴板`)
  }).catch(() => {
    ElMessage.error('复制失败，请手动复制')
  })
}
</script>

<style scoped>
.resources-page {
  min-height: 100%;
}

/* ========== Page Header ========== */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: var(--spacing-xxl) 0;
  margin-bottom: var(--spacing-xxl);
}

.page-title {
  font-size: 36px;
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-md);
  text-align: center;
}

.page-subtitle {
  font-size: var(--font-size-xl);
  text-align: center;
  margin-bottom: var(--spacing-md);
  opacity: 0.95;
}

/* ========== Guide Tabs ========== */
.guide-tabs {
  margin-top: 24px;
  text-align: center;
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

/* ========== Quick Nav ========== */
.quick-nav {
  display: flex;
  gap: var(--spacing-md);
  justify-content: center;
  margin-bottom: var(--spacing-xxl);
  flex-wrap: wrap;
}

/* ========== Section ========== */
.section {
  margin-bottom: var(--spacing-xxl);
}

.section-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.section-title {
  font-size: var(--font-size-hero);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-sm);
}

.section-subtitle {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
}

/* ========== Prompt Categories ========== */
.prompt-categories {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

.category-card {
  background: white;
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-base);
}

.category-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-md);
  border-bottom: 2px solid var(--color-border-light);
}

.category-icon {
  font-size: 32px;
}

.category-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.prompt-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  width: 100%;
}

.prompt-icon {
  font-size: 20px;
}

.prompt-content {
  padding: var(--spacing-lg);
}

.prompt-description {
  font-size: var(--font-size-md);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-md);
  line-height: var(--line-height-relaxed);
}

.prompt-usage {
  background: #f5f7fa;
  padding: var(--spacing-md);
  border-radius: var(--border-radius-base);
  margin-bottom: var(--spacing-lg);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

/* ========== Code Block ========== */
.code-block {
  background: #282c34;
  border-radius: var(--border-radius-base);
  overflow: hidden;
  margin-top: var(--spacing-md);
}

.code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  background: #21252b;
  border-bottom: 1px solid #181a1f;
}

.code-language {
  color: #abb2bf;
  font-size: var(--font-size-sm);
  font-family: 'Monaco', 'Menlo', monospace;
}

.code-content {
  padding: var(--spacing-md);
  margin: 0;
  color: #abb2bf;
  font-size: var(--font-size-sm);
  font-family: 'Monaco', 'Menlo', monospace;
  line-height: 1.6;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* ========== Standards ========== */
.standard-card {
  height: 100%;
  margin-bottom: var(--spacing-lg);
}

.standard-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.standard-icon {
  font-size: 28px;
}

.standard-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.standard-description {
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-md);
  line-height: var(--line-height-relaxed);
}

.standard-includes {
  background: #f5f7fa;
  padding: var(--spacing-md);
  border-radius: var(--border-radius-base);
  margin-bottom: var(--spacing-md);
}

.standard-list {
  margin: var(--spacing-sm) 0 0 var(--spacing-lg);
  padding: 0;
}

.standard-list li {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  line-height: var(--line-height-relaxed);
}

/* ========== Tools ========== */
.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: var(--spacing-xl);
}

.tool-card {
  height: 100%;
}

.tool-header {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.tool-icon {
  font-size: 32px;
}

.tool-info {
  flex: 1;
}

.tool-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-xs);
}

.tool-description {
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  margin-bottom: var(--spacing-md);
}

.tool-usage-section {
  background: #f5f7fa;
  padding: var(--spacing-md);
  border-radius: var(--border-radius-base);
  margin-bottom: var(--spacing-md);
}

.inline-code {
  background: #282c34;
  color: #abb2bf;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: var(--font-size-sm);
}

/* ========== Responsive ========== */
@media (max-width: 768px) {
  .page-title {
    font-size: 28px;
  }

  .tools-grid {
    grid-template-columns: 1fr;
  }

  .quick-nav {
    flex-direction: column;
  }

  .code-content {
    font-size: 12px;
  }
}
</style>
