<template>
  <div class="github-page">
    <header class="page-header">
      <div class="header-content">
        <h1>实操模拟 (Simulator)</h1>
        <p class="subtitle">模拟 Git 工作流，理解每一步操作的含义</p>
      </div>
    </header>

    <div class="sim-layout">
      <!-- 步骤导航 -->
      <div class="sim-sidebar">
        <div
          v-for="(step, index) in simulatorSteps"
          :key="index"
          class="nav-item"
          :class="{ active: currentStep === index + 1 }"
          @click="runScene(index + 1)"
        >
          <div class="nav-step">Step {{ index + 1 }}</div>
          <div class="nav-head">{{ step.navTitle }}</div>
        </div>
      </div>

      <div class="sim-stage">
        <!-- 解释器 -->
        <div class="sim-explainer">
          <div class="exp-title">{{ scenes[currentStep].title }}</div>
          <div class="exp-text" v-html="scenes[currentStep].desc"></div>
        </div>

        <!-- 视觉演示 -->
        <div class="sim-visualizer">
          <!-- 轨道 -->
          <div class="git-track track-main">
            <div class="commit c-main" style="left: 5%;"></div>
            <div class="commit c-main" style="left: 15%;"></div>
            <div class="commit c-main" style="left: 25%;"></div>
            <div class="commit c-main" :style="{ left: '75%', opacity: mergePointVisible ? 1 : 0, transform: mergePointVisible ? 'scale(1.5)' : 'scale(1)' }"></div>
          </div>
          <div class="lbl lbl-main">main (Production)</div>

          <div class="git-track track-feat" :style="{ width: featTrackWidth }">
            <div class="commit c-feat" style="left: 20%;" :style="{ opacity: c1Visible }"></div>
            <div class="commit c-feat" style="left: 50%;" :style="{ opacity: c2Visible }"></div>
            <div class="commit c-feat" style="left: 80%;" :style="{ opacity: c3Visible }"></div>
          </div>
          <div class="lbl lbl-feat" :style="{ opacity: featLabelVisible }">feature/subscription-v3</div>

          <!-- 连线 SVG -->
          <svg class="svg-lines">
            <path
              d="M 200 350 Q 250 350 250 200 L 600 200"
              fill="none"
              stroke="#a371f7"
              stroke-width="2"
              stroke-dasharray="5,5"
              :style="{ opacity: branchLineVisible }"
            />
            <path
              d="M 500 200 Q 600 200 610 350"
              fill="none"
              :stroke="mergeLineColor"
              stroke-width="2"
              :style="{ opacity: mergeLineVisible }"
            />
          </svg>

          <!-- 弹窗 -->
          <div class="popup" :class="{ show: popupVisible }" :style="{ left: popupLeft, top: popupTop }">
            {{ popupText }}
          </div>
        </div>

        <!-- CLI -->
        <div class="sim-cli">
          <div class="cli-head">Claude Code Terminal Output</div>
          <div class="cli-rows">
            <div v-for="(line, index) in scenes[currentStep].cli" :key="index" class="cmd-row">
              <span class="prompt">$</span>
              <span class="cmd-text">{{ line.cmd }}</span>
              <span class="comment">{{ line.cmt }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const currentStep = ref(1)

// Simulator state
const featTrackWidth = ref('0')
const featLabelVisible = ref(0)
const branchLineVisible = ref(0)
const mergeLineVisible = ref(0)
const mergeLineColor = ref('#238636')
const mergePointVisible = ref(false)
const c1Visible = ref(0)
const c2Visible = ref(0)
const c3Visible = ref(0)
const popupVisible = ref(false)
const popupText = ref('')
const popupLeft = ref('50%')
const popupTop = ref('40%')

const simulatorSteps = [
  { navTitle: '主宇宙 (Main Context)' },
  { navTitle: '开启平行宇宙 (Branch)' },
  { navTitle: '时空存档 (Commit)' },
  { navTitle: '上传云端 (Push)' },
  { navTitle: '申请合并 (PR)' },
  { navTitle: '宇宙融合 (Merge)' }
]

const scenes = {
  1: {
    title: "1. 确认基准 (Checkout Main)",
    desc: "在开始任何工作前，必须回到<span class='exp-tag'>主宇宙 (Main)</span>。这保证了你的新功能是基于最新、最稳定的代码开发的。",
    cli: [
      { cmd: "git checkout main", cmt: "# 切换回主分支" },
      { cmd: "git pull origin main", cmt: "# 拉取云端最新代码 (Sync)" }
    ]
  },
  2: {
    title: "2. 开启平行宇宙 (Create Branch)",
    desc: "为了安全，Claude Code 会为你创建一个<span class='exp-tag'>平行宇宙 (Feature Branch)</span>。在这个空间里，你可以随意破坏、重组，完全不会影响线上用户。",
    cli: [
      { cmd: "git checkout -b feature/subscription-v3", cmt: "# 创建并切换到新分支" },
      { cmd: "echo 'Start' > dev.md", cmt: "# 开始干活..." }
    ]
  },
  3: {
    title: "3. 时空存档 (Commit)",
    desc: "你在平行宇宙里写代码。每完成一个小任务，Claude Code 就会执行一次<span class='exp-tag'>Commit (存档)</span>。这是你的后悔药。",
    cli: [
      { cmd: "git add .", cmt: "# 暂存修改" },
      { cmd: "git commit -m 'feat: api done'", cmt: "# 存档1：API 完成" },
      { cmd: "git commit -m 'fix: bug'", cmt: "# 存档2：修复 Bug" }
    ]
  },
  4: {
    title: "4. 上传云端 (Push)",
    desc: "现在，这些存档只存在于你的电脑里。你需要把这个平行宇宙<span class='exp-tag'>Push (推送)</span>到 GitHub 云端，让团队其他人能看到。",
    cli: [
      { cmd: "git push origin feature/subscription-v3", cmt: "# 发射到云端" }
    ]
  },
  5: {
    title: "5. 申请合并 (Pull Request)",
    desc: `这是最关键的一步。你告诉架构师：「我的活干完了，请求<span class='exp-tag'>Merge (合并)</span>回主宇宙！」<br>GitHub 会生成一个 PR 页面，供大家进行 Code Review。`,
    cli: [
      { cmd: "gh pr create --title 'Sub V3' --body 'Done'", cmt: "# 发起合并请求" },
      { cmd: "// Waiting for Review...", cmt: "" }
    ]
  },
  6: {
    title: "6. 宇宙融合 (Merge)",
    desc: "审核通过！点击 Merge。你的代码瞬间变成了主宇宙的一部分。GitHub Actions 会自动触发<span class='exp-tag'>Deploy (部署)</span>，新功能上线！",
    cli: [
      { cmd: "// GitHub Action: Test Passed", cmt: "" },
      { cmd: "// Merged into Main", cmt: "" },
      { cmd: "git checkout main", cmt: "# 回到主宇宙" },
      { cmd: "git pull origin main", cmt: "# 同步最新结果" }
    ]
  }
}

const resetAnim = () => {
  branchLineVisible.value = 0
  mergeLineVisible.value = 0
  featTrackWidth.value = '0'
  featLabelVisible.value = 0
  c1Visible.value = 0
  c2Visible.value = 0
  c3Visible.value = 0
  mergePointVisible.value = false
  popupVisible.value = false
}

const showPopup = (text, left, top) => {
  popupText.value = text
  popupLeft.value = left + '%'
  popupTop.value = top + '%'
  popupVisible.value = true
}

// 设置步骤3的基础动画状态
const setupStep3Base = () => {
  resetAnim()
  branchLineVisible.value = 1
  featTrackWidth.value = '60%'
  featLabelVisible.value = 1
  setTimeout(() => { c1Visible.value = 1 }, 200)
  setTimeout(() => { c2Visible.value = 1 }, 600)
  setTimeout(() => { c3Visible.value = 1 }, 1000)
}

const runScene = (id) => {
  currentStep.value = id

  switch(id) {
    case 1:
      resetAnim()
      break
    case 2:
      resetAnim()
      branchLineVisible.value = 1
      featTrackWidth.value = '20%'
      featLabelVisible.value = 1
      break
    case 3:
      setupStep3Base()
      break
    case 4:
      setupStep3Base()
      showPopup("Synced to GitHub Cloud", 50, 40)
      break
    case 5:
      setupStep3Base()
      mergeLineVisible.value = 0.5
      mergeLineColor.value = '#f59e0b'
      showPopup("PR Created: Waiting for Review...", 60, 20)
      break
    case 6:
      setupStep3Base()
      mergeLineVisible.value = 1
      mergeLineColor.value = '#238636'
      setTimeout(() => {
        mergePointVisible.value = true
        showPopup("Merged! Deployed to Prod.", 75, 55)
      }, 800)
      break
  }
}
</script>

<style scoped>
.github-page {
  --bg: #0d1117;
  --card-bg: #161b22;
  --border: #30363d;
  --text-main: #f8fafc;
  --text-dim: #8b949e;
  --c-task: #3b82f6;
  --c-space: #a855f7;
  --c-action: #10b981;

  min-height: 100vh;
  background: var(--bg);
  color: var(--text-main);
  display: flex;
  flex-direction: column;
}

.page-header {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(59, 130, 246, 0.15) 100%);
  border-bottom: 1px solid var(--border);
  padding: 40px;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 10px 0;
  color: #fff;
}

.subtitle {
  color: var(--text-dim);
  font-size: 16px;
  margin: 0;
}

/* Simulator Layout */
.sim-layout {
  display: flex;
  width: 100%;
  flex: 1;
  min-height: calc(100vh - 140px);
}

.sim-sidebar {
  width: 280px;
  background: #010409;
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  padding: 20px;
  flex-shrink: 0;
}

.nav-item {
  padding: 14px;
  margin-bottom: 10px;
  border-radius: 8px;
  cursor: pointer;
  color: var(--text-dim);
  border: 1px solid transparent;
  transition: all 0.2s;
}

.nav-item:hover {
  background: rgba(255,255,255,0.05);
}

.nav-item.active {
  background: rgba(56, 189, 248, 0.1);
  border-color: rgba(56, 189, 248, 0.3);
  color: #38bdf8;
}

.nav-step {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 4px;
  font-weight: 700;
}

.nav-head {
  font-weight: 600;
  font-size: 14px;
}

.sim-stage {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  min-width: 0;
}

.sim-explainer {
  height: 140px;
  padding: 25px 30px;
  border-bottom: 1px solid var(--border);
  background: var(--card-bg);
  display: flex;
  flex-direction: column;
  justify-content: center;
  flex-shrink: 0;
}

.exp-title {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 10px;
}

.exp-text {
  font-size: 14px;
  color: var(--text-dim);
  line-height: 1.6;
  max-width: 800px;
}

:deep(.exp-tag) {
  display: inline-block;
  background: #334155;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  margin-right: 6px;
  color: #fff;
  vertical-align: middle;
  font-weight: bold;
}

.sim-visualizer {
  flex: 1;
  background: #0d1117;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  min-height: 300px;
}

/* Git Graph */
.git-track {
  position: absolute;
  height: 6px;
  background: #21262d;
  border-radius: 3px;
}

.track-main {
  top: 65%;
  width: 80%;
  background: rgba(35, 134, 54, 0.2);
}

.track-feat {
  top: 35%;
  left: 20%;
  background: rgba(163, 113, 247, 0.2);
  transition: width 1s ease;
}

.commit {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 3px solid #fff;
  position: absolute;
  top: -5px;
  cursor: pointer;
  transition: all 0.5s;
  z-index: 2;
}

.c-main {
  background: var(--c-action);
  border-color: var(--c-action);
}

.c-feat {
  background: var(--c-space);
  border-color: var(--c-space);
  transition: opacity 0.5s;
}

.lbl {
  position: absolute;
  font-family: monospace;
  font-size: 12px;
  color: var(--text-dim);
  font-weight: bold;
}

.lbl-main {
  top: 68%;
  left: 5%;
  color: var(--c-action);
}

.lbl-feat {
  top: 32%;
  left: 20%;
  color: var(--c-space);
  transition: opacity 0.5s;
}

.svg-lines {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.popup {
  position: absolute;
  background: #1f2937;
  border: 1px solid #4b5563;
  padding: 12px 18px;
  border-radius: 8px;
  color: #fff;
  font-size: 13px;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s;
  z-index: 10;
  box-shadow: 0 10px 25px rgba(0,0,0,0.5);
}

.popup.show {
  opacity: 1;
  transform: translateY(-10px);
}

/* CLI Terminal */
.sim-cli {
  height: 200px;
  background: #010409;
  border-top: 1px solid var(--border);
  padding: 20px;
  font-family: 'Consolas', monospace;
  overflow-y: auto;
  color: #33ff00;
  flex-shrink: 0;
}

.cli-head {
  font-size: 11px;
  color: #475569;
  margin-bottom: 8px;
  text-transform: uppercase;
  font-weight: 700;
}

.cmd-row {
  display: flex;
  gap: 10px;
  margin-bottom: 6px;
  opacity: 0.9;
  font-size: 13px;
}

.prompt {
  color: #475569;
  user-select: none;
}

.cmd-text {
  color: #e2e8f0;
}

.comment {
  color: #475569;
  font-style: italic;
}

/* 响应式 */
@media (max-width: 900px) {
  .sim-layout {
    flex-direction: column;
  }

  .sim-sidebar {
    width: 100%;
    flex-direction: row;
    overflow-x: auto;
    padding: 10px;
  }

  .nav-item {
    min-width: 150px;
    margin-bottom: 0;
    margin-right: 10px;
  }
}
</style>
