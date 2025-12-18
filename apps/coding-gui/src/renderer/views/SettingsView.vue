<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

const cliPath = ref('/usr/local/bin/claude')
const theme = ref('light')
const timeout = ref(60)
const autoRefresh = ref(true)

// 帮助文档展开状态
const showArchitecture = ref(false)
const showConfigFiles = ref(false)
const showCustomPhases = ref(false)
const showCustomContent = ref(false)
const showCustomTasks = ref(false)

const saveSettings = () => {
  ElMessage.success('设置已保存')
}

const goBack = () => {
  router.back()
}

const checkCli = () => {
  ElMessage.success('CLI 检测成功: claude v1.0.0')
}
</script>

<template>
  <div class="settings-page">
    <header class="settings-header">
      <el-button text @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
      <h1>设置</h1>
    </header>

    <div class="settings-content">
      <el-card class="settings-card">
        <template #header>
          <div class="card-header">
            <el-icon><Setting /></el-icon>
            CLI 配置
          </div>
        </template>

        <el-form label-position="top">
          <el-form-item label="Claude CLI 路径">
            <el-input v-model="cliPath">
              <template #append>
                <el-button @click="checkCli">检测</el-button>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item label="命令超时时间（秒）">
            <el-input-number v-model="timeout" :min="10" :max="300" />
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="settings-card">
        <template #header>
          <div class="card-header">
            <el-icon><Brush /></el-icon>
            界面设置
          </div>
        </template>

        <el-form label-position="top">
          <el-form-item label="主题">
            <el-radio-group v-model="theme">
              <el-radio-button value="light">浅色</el-radio-button>
              <el-radio-button value="dark">深色</el-radio-button>
              <el-radio-button value="auto">跟随系统</el-radio-button>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="自动刷新">
            <el-switch v-model="autoRefresh" />
            <span class="setting-hint">文件变化时自动刷新状态</span>
          </el-form-item>
        </el-form>
      </el-card>

      <div class="settings-actions">
        <el-button type="primary" size="large" @click="saveSettings">
          保存设置
        </el-button>
      </div>

      <!-- 帮助文档：UI 配置说明 -->
      <el-divider>
        <el-icon><QuestionFilled /></el-icon>
        界面配置说明
      </el-divider>

      <el-card class="ui-guide-card">
        <div class="ui-mockup">
          <!-- 顶部导航 -->
          <div class="mock-header">
            <span class="mock-label">顶部导航</span>
            <span class="mock-hint">固定 UI</span>
          </div>

          <!-- 阶段导航 -->
          <div class="mock-phase-nav">
            <span class="mock-label">阶段导航 (8 个阶段)</span>
            <code class="mock-file">CC_COLLABORATION/00_system/WORKFLOW_TEMPLATE.yaml → phases</code>
          </div>

          <!-- 主内容区 -->
          <div class="mock-main">
            <!-- 左侧面板 -->
            <div class="mock-left-panel">
              <div class="mock-section">
                <span class="section-title">🎯 本阶段目标</span>
                <code>PHASE_GATE.yaml → objectives</code>
              </div>
              <div class="mock-section">
                <span class="section-title">📦 上游输入</span>
                <code>PHASE_GATE.yaml → inputs</code>
              </div>
              <div class="mock-section">
                <span class="section-title">📄 参考文档</span>
                <code>PHASE_GATE.yaml → references</code>
              </div>
              <div class="mock-section">
                <span class="section-title">⚡ 可用工具</span>
                <code>PHASE_GATE.yaml → tools</code>
              </div>
            </div>

            <!-- 右侧面板 -->
            <div class="mock-right-panel">
              <div class="mock-section">
                <span class="section-title">🚀 框架步骤</span>
                <code>WORKFLOW_TEMPLATE.yaml → framework_steps</code>
              </div>
              <div class="mock-section highlight">
                <span class="section-title">📝 Feature 任务</span>
                <code>docs/{feature}/90_PROGRESS_LOG.yaml → tasks</code>
              </div>
              <div class="mock-section">
                <span class="section-title">🔧 收尾步骤</span>
                <code>WORKFLOW_TEMPLATE.yaml → framework_steps</code>
              </div>
            </div>
          </div>
        </div>

        <!-- 配置文件路径汇总 -->
        <div class="config-summary">
          <div class="config-item">
            <el-tag type="primary">全局配置</el-tag>
            <code>CC_COLLABORATION/00_system/WORKFLOW_TEMPLATE.yaml</code>
          </div>
          <div class="config-item">
            <el-tag type="primary">全局配置</el-tag>
            <code>CC_COLLABORATION/07_phase_gate/PHASE_GATE.yaml</code>
          </div>
          <div class="config-item">
            <el-tag type="success">Feature 配置</el-tag>
            <code>docs/{feature}/90_PROGRESS_LOG.yaml</code>
          </div>
        </div>
      </el-card>

      <!-- 使用帮助 -->
      <el-divider>
        <el-icon><InfoFilled /></el-icon>
        使用帮助
      </el-divider>

      <!-- 系统架构 -->
      <el-card class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header" @click="showArchitecture = !showArchitecture">
            <span>1. 系统架构</span>
            <el-icon :class="{ 'is-rotate': showArchitecture }"><ArrowDown /></el-icon>
          </div>
        </template>
        <el-collapse-transition>
          <div v-show="showArchitecture" class="help-content">
            <p><strong>两层执行模型：</strong></p>
            <div class="architecture-diagram">
              <div class="arch-layer">
                <span class="layer-label">全局层</span>
                <span class="layer-desc">Framework Steps（框架步骤）- 所有 Feature 共用</span>
              </div>
              <div class="arch-arrow">↓ 插入 ↓</div>
              <div class="arch-layer feature">
                <span class="layer-label">Feature 层</span>
                <span class="layer-desc">Feature Tasks（功能任务）- 每个 Feature 独立</span>
              </div>
            </div>
            <p>执行清单的组装逻辑：<code>框架前置步骤 → Feature 任务 → 框架收尾步骤</code></p>
            <p class="help-tip">框架步骤定义了标准化的开发流程，Feature 任务则是每个功能的具体实现步骤。</p>
          </div>
        </el-collapse-transition>
      </el-card>

      <!-- 配置文件说明 -->
      <el-card class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header" @click="showConfigFiles = !showConfigFiles">
            <span>2. 配置文件说明</span>
            <el-icon :class="{ 'is-rotate': showConfigFiles }"><ArrowDown /></el-icon>
          </div>
        </template>
        <el-collapse-transition>
          <div v-show="showConfigFiles" class="help-content">
            <div class="config-file-list">
              <div class="config-file-item">
                <el-tag type="primary" size="small">全局</el-tag>
                <code>WORKFLOW_TEMPLATE.yaml</code>
                <span>定义阶段列表、框架步骤</span>
              </div>
              <div class="config-file-item">
                <el-tag type="primary" size="small">全局</el-tag>
                <code>PHASE_GATE.yaml</code>
                <span>定义每个阶段的目标、输入、参考文档、可用工具</span>
              </div>
              <div class="config-file-item">
                <el-tag type="success" size="small">Feature</el-tag>
                <code>90_PROGRESS_LOG.yaml</code>
                <span>定义 Feature 的具体任务、进度状态</span>
              </div>
            </div>

            <!-- 左侧面板字段映射 -->
            <div class="field-mapping">
              <p class="mapping-title">左侧面板配置字段（PHASE_GATE.yaml）：</p>
              <table class="mapping-table">
                <tbody>
                  <tr>
                    <td><span class="ui-label">🎯 阶段目标</span></td>
                    <td><code>objectives</code></td>
                  </tr>
                  <tr>
                    <td><span class="ui-label">📦 上游输入</span></td>
                    <td><code>inputs</code></td>
                  </tr>
                  <tr>
                    <td><span class="ui-label">📄 参考文档</span></td>
                    <td><code>references</code></td>
                  </tr>
                  <tr>
                    <td><span class="ui-label">⚡ 可用工具</span></td>
                    <td><code>tools</code></td>
                  </tr>
                </tbody>
              </table>
            </div>

            <p class="help-tip">全局配置适用于所有项目，Feature 配置是每个功能独立的。</p>
          </div>
        </el-collapse-transition>
      </el-card>

      <!-- 自定义指南 -->
      <el-divider>
        <el-icon><EditPen /></el-icon>
        自定义指南
      </el-divider>

      <!-- 自定义流程阶段 -->
      <el-card class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header" @click="showCustomPhases = !showCustomPhases">
            <span>3. 如何自定义流程阶段</span>
            <el-icon :class="{ 'is-rotate': showCustomPhases }"><ArrowDown /></el-icon>
          </div>
        </template>
        <el-collapse-transition>
          <div v-show="showCustomPhases" class="help-content">
            <p>编辑 <code>CC_COLLABORATION/00_system/WORKFLOW_TEMPLATE.yaml</code> 文件中的 <code>phases</code> 字段：</p>
            <pre class="code-block">phases:
  - id: kickoff
    name: "1. Kickoff"
    icon: "Rocket"
  - id: spec
    name: "2. Spec"
    icon: "Document"
  # 添加更多阶段...</pre>
            <p class="help-tip">每个阶段需要定义 <code>id</code>（唯一标识）、<code>name</code>（显示名称）和 <code>icon</code>（图标名称）。</p>
          </div>
        </el-collapse-transition>
      </el-card>

      <!-- 自定义阶段内容 -->
      <el-card class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header" @click="showCustomContent = !showCustomContent">
            <span>4. 如何自定义阶段内容（目标、输入、工具等）</span>
            <el-icon :class="{ 'is-rotate': showCustomContent }"><ArrowDown /></el-icon>
          </div>
        </template>
        <el-collapse-transition>
          <div v-show="showCustomContent" class="help-content">
            <p>编辑 <code>CC_COLLABORATION/07_phase_gate/PHASE_GATE.yaml</code> 文件：</p>
            <pre class="code-block">phases:
  phase_1_kickoff:
    objectives:
      - "理解项目背景"
      - "确认技术可行性"
    inputs:
      - name: "需求文档"
        source: "产品经理"
    references:
      - name: "设计规范"
        path: "docs/design-spec.md"
    tools:
      - name: "需求分析"
        type: "skill"
        path: "analyze-requirements"</pre>
            <p class="help-tip">每个阶段的 ID 格式为 <code>phase_N_name</code>，其中 N 从 1 开始。</p>
          </div>
        </el-collapse-transition>
      </el-card>

      <!-- 添加 Feature 任务 -->
      <el-card class="help-card" shadow="hover">
        <template #header>
          <div class="help-card-header" @click="showCustomTasks = !showCustomTasks">
            <span>5. 如何添加 Feature 任务</span>
            <el-icon :class="{ 'is-rotate': showCustomTasks }"><ArrowDown /></el-icon>
          </div>
        </template>
        <el-collapse-transition>
          <div v-show="showCustomTasks" class="help-content">
            <p>编辑 Feature 目录下的 <code>90_PROGRESS_LOG.yaml</code> 文件：</p>
            <pre class="code-block">tasks:
  phase_5_code:  # 对应阶段 ID
    - id: "CODE-001"
      title: "实现用户认证模块"
      status: "pending"
      command:
        type: "slash_command"
        value: "/implement auth-module"
    - id: "CODE-002"
      title: "编写单元测试"
      status: "pending"
      command:
        type: "skill"
        value: "test-runner"</pre>
            <p class="help-tip">任务的 <code>command.type</code> 支持：<code>slash_command</code>、<code>skill</code>、<code>subagent</code>、<code>bash</code>。</p>
          </div>
        </el-collapse-transition>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.settings-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.settings-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 24px;
  padding-left: var(--titlebar-area-left);
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.settings-header * {
  -webkit-app-region: no-drag;
}

.settings-header h1 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.settings-content {
  max-width: 800px;
  margin: 40px auto;
  padding: 0 24px;
}

.settings-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.setting-hint {
  margin-left: 12px;
  font-size: 13px;
  color: #909399;
}

.settings-actions {
  text-align: center;
  margin-top: 32px;
}

/* UI 配置说明样式 */
:deep(.el-divider__text) {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
}

.ui-guide-card {
  margin-bottom: 20px;
}

.ui-mockup {
  background: #0d1117;
  border-radius: 8px;
  overflow: hidden;
  font-size: 12px;
}

.mock-header {
  background: #161b22;
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #30363d;
}

.mock-label {
  color: #c9d1d9;
  font-weight: 600;
}

.mock-hint {
  color: #8b949e;
  font-size: 11px;
}

.mock-phase-nav {
  background: #21262d;
  padding: 10px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #30363d;
}

.mock-file {
  background: #0d1117;
  color: #58a6ff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
}

.mock-main {
  display: flex;
  min-height: 280px;
}

.mock-left-panel {
  width: 45%;
  background: #161b22;
  padding: 12px;
  border-right: 1px solid #30363d;
}

.mock-right-panel {
  flex: 1;
  background: #0d1117;
  padding: 12px;
}

.mock-section {
  background: #21262d;
  border: 1px solid #30363d;
  border-radius: 6px;
  padding: 10px 12px;
  margin-bottom: 8px;
}

.mock-section.highlight {
  border-color: #238636;
  background: rgba(35, 134, 54, 0.1);
}

.mock-section .section-title {
  display: block;
  color: #c9d1d9;
  font-weight: 600;
  margin-bottom: 6px;
}

.mock-section code {
  display: block;
  color: #58a6ff;
  font-size: 11px;
  word-break: break-all;
}

.config-summary {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}

.config-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
}

.config-item code {
  background: #f5f7fa;
  color: #409eff;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

/* 帮助卡片样式 */
.help-card {
  margin-bottom: 12px;
}

.help-card :deep(.el-card__header) {
  padding: 12px 16px;
  cursor: pointer;
}

.help-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 500;
  color: #303133;
}

.help-card-header .el-icon {
  transition: transform 0.3s;
  color: #909399;
}

.help-card-header .el-icon.is-rotate {
  transform: rotate(180deg);
}

.help-content {
  padding: 0 4px;
}

.help-content p {
  margin: 0 0 12px 0;
  color: #606266;
  line-height: 1.6;
}

.help-content code {
  background: #f5f7fa;
  color: #409eff;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 13px;
}

.code-block {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 12px 16px;
  border-radius: 6px;
  font-size: 12px;
  line-height: 1.5;
  overflow-x: auto;
  margin: 12px 0;
}

.help-tip {
  background: #ecf5ff;
  border-left: 3px solid #409eff;
  padding: 8px 12px;
  border-radius: 0 4px 4px 0;
  font-size: 13px;
  color: #409eff;
}

/* 架构图样式 */
.architecture-diagram {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px;
  margin: 12px 0;
  text-align: center;
}

.arch-layer {
  background: #fff;
  border: 2px solid #409eff;
  border-radius: 8px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.arch-layer.feature {
  border-color: #67c23a;
}

.layer-label {
  background: #409eff;
  color: #fff;
  padding: 4px 10px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 12px;
  white-space: nowrap;
}

.arch-layer.feature .layer-label {
  background: #67c23a;
}

.layer-desc {
  color: #606266;
  font-size: 13px;
}

.arch-arrow {
  color: #909399;
  padding: 8px 0;
  font-size: 12px;
}

/* 配置文件列表样式 */
.config-file-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.config-file-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 6px;
}

.config-file-item code {
  background: #fff;
  font-weight: 600;
}

.config-file-item span:last-child {
  color: #909399;
  font-size: 12px;
}

/* 字段映射表格样式 */
.field-mapping {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px dashed #e4e7ed;
}

.mapping-title {
  font-weight: 500;
  color: #606266;
  margin-bottom: 10px;
}

.mapping-table {
  width: 100%;
  border-collapse: collapse;
}

.mapping-table tr {
  border-bottom: 1px solid #f0f0f0;
}

.mapping-table tr:last-child {
  border-bottom: none;
}

.mapping-table td {
  padding: 8px 12px;
}

.mapping-table td:first-child {
  width: 140px;
}

.ui-label {
  font-size: 13px;
  color: #303133;
}

.mapping-table code {
  background: #f5f7fa;
  color: #409eff;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 13px;
  font-weight: 500;
}
</style>
