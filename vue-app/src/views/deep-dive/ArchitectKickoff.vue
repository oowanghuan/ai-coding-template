<template>
  <div class="deep-dive-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="container">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: '/role/architect' }">系统架构师</el-breadcrumb-item>
          <el-breadcrumb-item>Kickoff 指南</el-breadcrumb-item>
        </el-breadcrumb>
        <h1 class="page-title">🏗️ 架构师 Kickoff 指南</h1>
        <p class="page-subtitle">AI 时代的项目启动规范体系</p>
      </div>
    </div>

    <div class="page-content">
      <div class="container">
        <!-- Section 1: 核心定位 -->
        <el-card class="content-section" shadow="never">
          <h2 class="section-title">架构师的核心定位</h2>

          <div class="definition-box">
            <h3>架构师 = 技术结构与规范 Owner</h3>
            <p>负责定义系统的「技术结构和统一规范」，让所有模块、所有角色（包括 AI）都在同一套技术规则下工作。</p>
          </div>

          <div class="key-insight">
            架构师不是写代码最多的人，而是定义"规则"最多的人。<br/>
            他产出的不是功能，而是"让团队和 AI 能高效协作的基础设施"。
          </div>

          <div class="highlight-box">
            <h4>关键区分：架构师 vs 项目经理</h4>
            <el-row :gutter="20">
              <el-col :xs="24" :sm="12">
                <div class="compare-item architect">
                  <h5>架构师负责</h5>
                  <ul>
                    <li>系统结构设计</li>
                    <li>技术规范制定</li>
                    <li>AI 使用规则</li>
                    <li>技术风险评估</li>
                  </ul>
                </div>
              </el-col>
              <el-col :xs="24" :sm="12">
                <div class="compare-item pm">
                  <h5>架构师不负责</h5>
                  <ul>
                    <li>排期和里程碑</li>
                    <li>任务看板管理</li>
                    <li>需求优先级排序</li>
                    <li>人力配置</li>
                  </ul>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>

        <!-- Section 2: 三层规范体系 -->
        <el-card class="content-section" shadow="never">
          <h2 class="section-title">架构师的三层规范体系</h2>

          <div class="layer-overview">
            <div class="layer-item" v-for="(layer, index) in layers" :key="index">
              <div class="layer-header" :style="{ background: layer.color }">
                <span class="layer-number">{{ index + 1 }}</span>
                <span class="layer-title">{{ layer.title }}</span>
              </div>
              <div class="layer-body">
                <p class="layer-desc">{{ layer.desc }}</p>
                <div class="layer-content">
                  <div class="layer-card" v-for="(item, i) in layer.items" :key="i">
                    <h5>{{ item.title }}</h5>
                    <ul>
                      <li v-for="(point, j) in item.points" :key="j">{{ point }}</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- Section 3: Kickoff 6件套 -->
        <el-card class="content-section" shadow="never">
          <h2 class="section-title">Kickoff 6件套清单</h2>

          <div class="key-insight">
            每个新项目开始前，架构师必须交付的 6 件东西
          </div>

          <div class="checklist">
            <div class="checklist-item" v-for="(item, index) in kickoffItems" :key="index">
              <div class="checklist-header">
                <span class="checklist-number">{{ index + 1 }}</span>
                <h4>{{ item.title }}</h4>
              </div>
              <ul>
                <li v-for="(point, i) in item.points" :key="i">{{ point }}</li>
              </ul>
            </div>
          </div>

          <div class="success-box">
            <strong>💡 核心价值：</strong><br/>
            架构师把这 6 件东西准备好，相当于：<br/>
            <strong>把高速公路、路灯、限速标志、收费站都建好了，AI PE/前端/后端/QA 只需要"开车"即可。</strong>
          </div>
        </el-card>

        <!-- Section 4: Spec Schema 示例 -->
        <el-card class="content-section" shadow="never">
          <h2 class="section-title">Spec Schema 示例（80% 通用结构）</h2>

          <p class="section-desc">这是架构师需要定义的标准 Spec 结构，所有 AI PE 写 Spec 都要遵循这个框架：</p>

          <div class="code-block">
            <div class="code-header">
              <span>标准 Spec Schema</span>
              <el-button size="small" @click="copySchema">
                <el-icon><DocumentCopy /></el-icon>
                复制
              </el-button>
            </div>
            <pre>{{ specSchema }}</pre>
          </div>

          <div class="highlight-box">
            <h4>为什么需要统一 Schema？</h4>
            <ul>
              <li><strong>一致性：</strong>所有模块 Spec 格式相同，便于阅读和维护</li>
              <li><strong>AI 友好：</strong>AI 可以基于固定格式生成和解析 Spec</li>
              <li><strong>可验证：</strong>可以自动检查 Spec 是否完整</li>
              <li><strong>可复用：</strong>Prompt 模板可以基于 Schema 设计</li>
            </ul>
          </div>
        </el-card>

        <!-- Section 5: AI 使用规范 -->
        <el-card class="content-section" shadow="never">
          <h2 class="section-title">AI 使用规范（架构师必须定义）</h2>

          <div class="warning-box">
            <strong>⚠️ 这是 AI 时代新增的关键工作</strong><br/>
            架构师负主责，与 AI PE 共同制定。
          </div>

          <el-row :gutter="20">
            <el-col :xs="24" :md="12" v-for="(rule, index) in aiRules" :key="index">
              <div class="rule-card">
                <h4>{{ rule.title }}</h4>
                <ul>
                  <li v-for="(point, i) in rule.points" :key="i">{{ point }}</li>
                </ul>
              </div>
            </el-col>
          </el-row>

          <div class="success-box">
            <strong>关键价值：</strong><br/>
            定义好 AI 使用边界后，AI PE 和工程师知道"哪些可以放心让 AI 做，哪些必须人工把关"。
          </div>
        </el-card>

        <!-- 底部导航 -->
        <div class="action-section">
          <el-button @click="router.push('/role/architect')">
            <el-icon class="el-icon--left"><ArrowLeft /></el-icon>
            返回架构师详情
          </el-button>
          <el-button type="primary" @click="router.push('/roles-overview')">
            查看角色协作
            <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, ArrowRight, DocumentCopy } from '@element-plus/icons-vue'

const router = useRouter()

const layers = ref([
  {
    title: '公司级基础规范（全项目通用）',
    desc: '这些规范一旦定好，所有项目都能直接复用。',
    color: '#1e3c72',
    items: [
      {
        title: 'API 行为框架',
        points: ['统一响应格式（{ data, error }）', 'HTTP 状态码语义标准', '错误码规范', '分页/排序/过滤规则']
      },
      {
        title: '认证与权限框架',
        points: ['登录方案（JWT/Session/OAuth）', '401/403 处理行为', 'RBAC 约定写法']
      },
      {
        title: '日志 & 监控规范',
        points: ['后端日志标准', '前端错误上报', 'Trace ID 传递规则']
      }
    ]
  },
  {
    title: '项目级规范（本项目专属）',
    desc: '新项目立项时，架构师要做一次"项目专用的收口"。',
    color: '#667eea',
    items: [
      {
        title: '模块划分 & 边界',
        points: ['业务域划分', '模块 Owner 分配', '模块间调用方式']
      },
      {
        title: 'API 命名空间',
        points: ['统一前缀（/api/v1/...）', 'REST 资源命名', 'URL 约定']
      },
      {
        title: '项目专用错误码',
        points: ['业务错误码扩展', '前端行为建议', '错误文案规范']
      }
    ]
  },
  {
    title: 'AI 使用级规范（给 AI PE 用）',
    desc: 'AI 时代新增的关键工作，架构师负主责。',
    color: '#f093fb',
    items: [
      {
        title: '标准 Spec Schema',
        points: ['80% 通用结构', 'JSON/YAML/Markdown 格式', '完美示例 Spec']
      },
      {
        title: 'Prompt 模板集',
        points: ['需求 → Spec 模板', 'Spec → Demo 模板', 'Spec → Test 模板']
      },
      {
        title: '代码生成规范',
        points: ['目录结构约定', '命名规范', 'AI 生成代码禁止事项']
      }
    ]
  }
])

const kickoffItems = ref([
  {
    title: '《项目技术蓝图》',
    points: ['架构图（前后端、服务、数据库、第三方）', '技术栈说明', '模块划分 & 边界说明']
  },
  {
    title: '《API 行为规范 - 项目版》',
    points: ['本项目错误码表', '每类错误的前端处理建议', '权限/认证行为', '成功/失败/超时处理策略']
  },
  {
    title: '《领域模型与资源命名规范》',
    points: ['核心实体定义', '实体关系', 'URL 路径与资源命名规则']
  },
  {
    title: '《前端项目结构 & 组件标准》',
    points: ['目录结构', '组件拆分原则', 'UI 组件库规范', 'UI tokens 和主题规范']
  },
  {
    title: '《Spec Schema & 示例》',
    points: ['80% Standard Schema 文档', '1~2 个完美示例 Spec', '所有 AI PE 按此标准写 Spec']
  },
  {
    title: '《AI 使用规范 & Prompt 模板集》',
    points: ['Prompt 模板（需求 → Spec → Demo → Test）', 'AI 生成代码的约束说明', '基础 Debug 工作流']
  }
])

const aiRules = ref([
  {
    title: 'AI 可修改的目录',
    points: ['src/views/', 'src/components/', 'src/pages/', '业务逻辑层代码']
  },
  {
    title: 'AI 禁止修改的目录',
    points: ['src/core/', 'src/auth/', '基础设施代码', '安全相关模块']
  },
  {
    title: 'AI 生成代码禁止事项',
    points: ['禁止硬编码 URL', '禁止跳过统一 error handler', '禁止写裸 fetch', '禁止直接操作 localStorage']
  },
  {
    title: 'Mock 行为规范',
    points: ['Mock 数据结构规范', 'Mock 与真实 API 保持一致', 'Demo 默认使用 Mock']
  }
])

const specSchema = `# Spec 标准结构（80% Schema）

## meta
- module_name: 模块名称
- version: 版本号
- owner: 负责人
- last_updated: 更新时间

## ui_structure
- layout: 页面布局
- components: 组件列表
- responsive: 响应式规则

## fields
- name: 字段名
- type: 类型
- required: 是否必填
- validation: 校验规则
- error_message: 错误提示

## states
- idle: 默认状态
- loading: 加载中
- success: 成功
- error: 错误

## actions
- trigger: 触发条件
- handler: 处理逻辑
- result: 结果状态

## api
- endpoint: 接口地址
- method: 请求方法
- request: 请求参数
- response: 响应格式
- error_codes: 错误码映射

## error_states
- field_errors: 字段错误
- api_errors: 接口错误
- network_errors: 网络错误

## mock_data
- success_case: 成功示例
- error_case: 错误示例`

const copySchema = () => {
  navigator.clipboard.writeText(specSchema)
  ElMessage.success('已复制到剪贴板')
}
</script>

<style scoped>
.deep-dive-page {
  min-height: 100%;
  background-color: var(--color-bg-page);
}

/* ========== Page Header ========== */
.page-header {
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  color: white;
  padding: var(--spacing-xxl) 0 var(--spacing-xl);
}

.page-header :deep(.el-breadcrumb__inner) {
  color: rgba(255, 255, 255, 0.9);
}

.page-header :deep(.el-breadcrumb__separator) {
  color: rgba(255, 255, 255, 0.6);
}

.page-title {
  font-size: 36px;
  font-weight: var(--font-weight-bold);
  margin: var(--spacing-lg) 0 var(--spacing-sm);
  color: white;
}

.page-subtitle {
  font-size: var(--font-size-lg);
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
}

/* ========== Content ========== */
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
  margin: 0 0 var(--spacing-xl);
  border-left: 4px solid #1e3c72;
  padding-left: var(--spacing-md);
}

.section-desc {
  font-size: var(--font-size-md);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-lg);
}

/* ========== Definition Box ========== */
.definition-box {
  background: linear-gradient(135deg, #e8eaf6 0%, #c5cae9 100%);
  border: 3px solid #1e3c72;
  border-radius: 12px;
  padding: 30px;
  margin: 20px 0;
  text-align: center;
}

.definition-box h3 {
  color: #1e3c72;
  margin: 0 0 15px;
  font-size: 22px;
}

.definition-box p {
  font-size: 16px;
  margin: 0;
  color: #333;
}

/* ========== Key Insight ========== */
.key-insight {
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  color: white;
  padding: 25px;
  margin: 25px 0;
  border-radius: 12px;
  font-size: 18px;
  text-align: center;
  font-weight: 500;
  line-height: 1.8;
}

/* ========== Highlight Box ========== */
.highlight-box {
  background: #f0f8ff;
  border-left: 4px solid #1e3c72;
  padding: 20px;
  margin: 20px 0;
  border-radius: 8px;
}

.highlight-box h4 {
  margin: 0 0 15px;
  color: #1e3c72;
}

.highlight-box ul {
  margin: 10px 0 0;
  padding-left: 20px;
}

.highlight-box li {
  margin: 8px 0;
}

/* ========== Compare Items ========== */
.compare-item {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-top: 15px;
}

.compare-item.architect {
  border-left: 4px solid #4caf50;
}

.compare-item.pm {
  border-left: 4px solid #f44336;
}

.compare-item h5 {
  margin: 0 0 10px;
  font-size: 16px;
}

.compare-item ul {
  margin: 0;
  padding-left: 20px;
}

.compare-item li {
  margin: 6px 0;
  font-size: 14px;
}

/* ========== Layer Overview ========== */
.layer-overview {
  margin: 20px 0;
}

.layer-item {
  margin-bottom: 30px;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.layer-header {
  padding: 15px 20px;
  color: white;
  display: flex;
  align-items: center;
  gap: 15px;
}

.layer-number {
  width: 32px;
  height: 32px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.layer-title {
  font-size: 18px;
  font-weight: 600;
}

.layer-body {
  background: white;
  padding: 20px;
}

.layer-desc {
  color: #666;
  margin: 0 0 15px;
  font-size: 14px;
}

.layer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.layer-card {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  border-left: 3px solid #1e3c72;
}

.layer-card h5 {
  margin: 0 0 10px;
  color: #1e3c72;
  font-size: 15px;
}

.layer-card ul {
  margin: 0;
  padding-left: 18px;
}

.layer-card li {
  margin: 5px 0;
  font-size: 13px;
  color: #555;
}

/* ========== Checklist ========== */
.checklist {
  margin: 20px 0;
}

.checklist-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 15px;
  border-left: 4px solid #1e3c72;
}

.checklist-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.checklist-number {
  width: 28px;
  height: 28px;
  background: #1e3c72;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
}

.checklist-item h4 {
  margin: 0;
  font-size: 16px;
  color: #1e3c72;
}

.checklist-item ul {
  margin: 0;
  padding-left: 40px;
}

.checklist-item li {
  margin: 6px 0;
  color: #555;
  font-size: 14px;
}

/* ========== Success Box ========== */
.success-box {
  background: #e8f5e9;
  border-left: 4px solid #4caf50;
  padding: 20px;
  margin: 20px 0;
  border-radius: 8px;
  line-height: 1.8;
}

/* ========== Warning Box ========== */
.warning-box {
  background: #fff3e0;
  border-left: 4px solid #ff9800;
  padding: 20px;
  margin: 20px 0;
  border-radius: 8px;
  line-height: 1.8;
}

/* ========== Code Block ========== */
.code-block {
  background: #1e1e1e;
  border-radius: 8px;
  overflow: hidden;
  margin: 20px 0;
}

.code-header {
  background: #333;
  padding: 10px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #ccc;
  font-size: 14px;
}

.code-block pre {
  margin: 0;
  padding: 20px;
  color: #d4d4d4;
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
}

/* ========== Rule Card ========== */
.rule-card {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  border-left: 3px solid #1e3c72;
  height: calc(100% - 20px);
}

.rule-card h4 {
  margin: 0 0 12px;
  color: #1e3c72;
  font-size: 16px;
}

.rule-card ul {
  margin: 0;
  padding-left: 18px;
}

.rule-card li {
  margin: 6px 0;
  font-size: 14px;
  color: #555;
}

/* ========== Action Section ========== */
.action-section {
  text-align: center;
  margin-top: var(--spacing-xl);
  padding: var(--spacing-xl) 0;
  display: flex;
  justify-content: center;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

/* ========== Responsive ========== */
@media (max-width: 768px) {
  .page-title {
    font-size: 24px;
  }

  .content-section :deep(.el-card__body) {
    padding: var(--spacing-lg);
  }

  .layer-content {
    grid-template-columns: 1fr;
  }
}
</style>
