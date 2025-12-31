<template>
  <div class="github-page">
    <header class="page-header">
      <div class="header-content">
        <h1>核心概念 (Core Concepts)</h1>
        <p class="subtitle">理解 GitHub 协作的三大维度：任务、空间、动作</p>
      </div>
    </header>

    <div class="mech-container">
      <div class="mech-grid">
        <!-- Column 1: 任务维 -->
        <div class="column">
          <div class="col-header col-task">
            <span>任务维 (Task)</span>
          </div>

          <div class="card">
            <span class="card-role" style="background: var(--c-task)">PM 规划</span>
            <span class="card-icon">📦</span>
            <div class="term-title">Feature (特性)</div>
            <div class="term-en">System Master Board Item</div>
            <div class="definition">
              <strong>定义：</strong> 一个完整的功能交付物。它是用户能感知的价值单元。<br>
              <strong>关系：</strong> Feature 是目标，Issue 是步骤。
            </div>
            <div class="analogy">
              比喻：精装修工程（包含水电、木工多个环节）。
            </div>
          </div>

          <div class="arrow-down">↓ 拆解为</div>

          <div class="card">
            <span class="card-role" style="background: var(--c-task)">AI 执行</span>
            <span class="card-icon">🎫</span>
            <div class="term-title">Issue (工单)</div>
            <div class="term-en">GitHub Issue</div>
            <div class="definition">
              <strong>定义：</strong> 最小的工作单元。AI 只能针对一个 Issue 干活。<br>
              <strong>Claude：</strong> 读取 Issue 描述 → 干活 → 提交代码时引用 Issue ID (#123)。
            </div>
            <div class="analogy">
              比喻：施工派工单（如"给客厅铺瓷砖"）。
            </div>
            <div class="cli-box">
              <span class="cli-label">Claude Action</span>
              <div class="code">gh issue create --title "P1: Spec"</div>
            </div>
          </div>
        </div>

        <!-- Column 2: 空间维 -->
        <div class="column">
          <div class="col-header col-space">
            <span>空间维 (Space)</span>
          </div>

          <div class="card">
            <span class="card-role" style="background: var(--c-space)">神圣不可侵犯</span>
            <span class="card-icon">🌍</span>
            <div class="term-title">Main (主宇宙)</div>
            <div class="term-en">Production Branch</div>
            <div class="definition">
              <strong>定义：</strong> 线上正在运行的代码。它是唯一的、稳定的、真实的。<br>
              <strong>铁律：</strong> 绝对禁止直接在 Main 上修改代码。
            </div>
            <div class="analogy">
              比喻：正在营业的商场大厅。不能在顾客脚下修地板。
            </div>
          </div>

          <div class="arrow-down">⑂ (Fork/Branch)</div>

          <div class="card">
            <span class="card-role" style="background: var(--c-space)">AI 工作区</span>
            <span class="card-icon">🌿</span>
            <div class="term-title">Branch (平行宇宙)</div>
            <div class="term-en">Feature Branch</div>
            <div class="definition">
              <strong>定义：</strong> 复制一个一模一样的世界。在这里把天捅破了也没关系，不会影响真实世界。<br>
              Claude 每次接单，都会自动创建一个新 Branch。
            </div>
            <div class="analogy">
              比喻：封闭施工的样板间。
            </div>
            <div class="cli-box">
              <span class="cli-label">Claude Action</span>
              <div class="code">git checkout -b feature/login</div>
            </div>
          </div>
        </div>

        <!-- Column 3: 动作维 -->
        <div class="column">
          <div class="col-header col-action">
            <span>动作维 (Action)</span>
          </div>

          <div class="card">
            <span class="card-role" style="background: var(--c-action)">Dev 存档</span>
            <span class="card-icon">📸</span>
            <div class="term-title">Commit (时空存档)</div>
            <div class="term-en">Git Commit</div>
            <div class="definition">
              <strong>定义：</strong> 在平行宇宙里，每完成一小步，就拍一张照片存档。如果后面搞砸了，可以读档重来。
            </div>
            <div class="cli-box">
              <span class="cli-label">Claude Action</span>
              <div class="code">git commit -m "feat: add api"</div>
            </div>
          </div>

          <div class="arrow-down">↓</div>

          <div class="card">
            <span class="card-role" style="background: var(--c-action)">Dev 同步</span>
            <span class="card-icon">☁️</span>
            <div class="term-title">Push (上传云端)</div>
            <div class="term-en">Git Push</div>
            <div class="definition">
              <strong>定义：</strong> 把你电脑里（本地）的平行宇宙和存档，上传到 GitHub 服务器（云端）。
            </div>
            <div class="cli-box">
              <span class="cli-label">Claude Action</span>
              <div class="code">git push origin feature/login</div>
            </div>
          </div>

          <div class="arrow-down">↓</div>

          <div class="card" style="border-color: #f59e0b;">
            <span class="card-role" style="background: #f59e0b">架构师 审核</span>
            <span class="card-icon">🔀</span>
            <div class="term-title">PR (申请合并)</div>
            <div class="term-en">Pull Request</div>
            <div class="definition">
              <strong>关键时刻：</strong> 你告诉架构师："我的样板间修好了，请把这些改动应用到真实的大厅里去！"
            </div>
            <div class="analogy">
              比喻：竣工验收申请。
            </div>
            <div class="cli-box">
              <span class="cli-label">Claude Action</span>
              <div class="code">gh pr create --title "Done"</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 核心概念页面 - 无需额外逻辑
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
}

.page-header {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%);
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

.mech-container {
  padding: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.mech-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 40px;
  max-width: 1400px;
  width: 100%;
}

.col-header {
  font-size: 16px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 1px;
  padding-bottom: 15px;
  border-bottom: 4px solid;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.col-task { border-color: var(--c-task); color: var(--c-task); }
.col-space { border-color: var(--c-space); color: var(--c-space); }
.col-action { border-color: var(--c-action); color: var(--c-action); }

.card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px;
  position: relative;
  margin-bottom: 24px;
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-3px);
  border-color: #58a6ff;
}

.card-icon {
  font-size: 28px;
  margin-bottom: 12px;
  display: block;
}

.card-role {
  position: absolute;
  top: 15px;
  right: 15px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  padding: 4px 8px;
  border-radius: 6px;
  background: rgba(255,255,255,0.1);
  color: #fff;
}

.term-title {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 4px;
  color: #fff;
}

.term-en {
  font-size: 12px;
  color: var(--text-dim);
  font-family: 'SF Mono', 'Monaco', monospace;
  margin-bottom: 12px;
}

.definition {
  font-size: 14px;
  color: var(--text-dim);
  line-height: 1.6;
  margin-bottom: 10px;
}

.analogy {
  font-size: 12px;
  color: #f59e0b;
  background: rgba(245, 158, 11, 0.1);
  padding: 8px 12px;
  border-radius: 6px;
  margin-top: 12px;
}

.cli-box {
  margin-top: 15px;
  background: #0d1117;
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
}

.cli-label {
  display: block;
  font-size: 10px;
  text-transform: uppercase;
  color: var(--text-dim);
  background: rgba(255,255,255,0.03);
  padding: 6px 12px;
  letter-spacing: 0.5px;
}

.code {
  font-family: 'SF Mono', 'Monaco', monospace;
  font-size: 12px;
  color: #4ade80;
  padding: 10px 12px;
}

.arrow-down {
  text-align: center;
  color: var(--text-dim);
  font-size: 14px;
  padding: 10px 0;
  opacity: 0.6;
}

@media (max-width: 1200px) {
  .mech-grid {
    grid-template-columns: 1fr;
    gap: 30px;
  }
}
</style>
