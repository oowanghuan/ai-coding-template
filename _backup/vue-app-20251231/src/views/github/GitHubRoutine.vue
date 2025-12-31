<template>
  <div class="routine-page">
    <header class="page-header">
      <div class="header-content">
        <div class="header-icon">🛡️</div>
        <div class="header-text">
          <h1>团队 GitHub 协作"早晚课"规范</h1>
          <p class="core-principle">核心原则：<strong>代码不过夜，冲突早解决。</strong></p>
          <p class="slogan">口号：<span class="highlight">上班第一件事 Pull，下班最后一件事 Push。</span></p>
        </div>
      </div>
    </header>

    <div class="routine-container">
      <!-- 时间线 -->
      <div class="timeline">
        <!-- 早晨 -->
        <div class="timeline-item morning">
          <div class="time-badge">
            <span class="time-icon">🕒</span>
            <span class="time-text">09:00 AM</span>
          </div>
          <div class="timeline-content">
            <div class="section-header">
              <span class="section-num">1</span>
              <h2>早晨：且慢开工，先同步</h2>
            </div>

            <div class="scenario-box">
              <div class="scenario-label">场景</div>
              <p>你刚到公司，喝了一口咖啡，准备开始写代码。</p>
            </div>

            <div class="action-box">
              <div class="action-label">动作</div>
              <p>在写任何一行新代码之前，<strong>必须</strong>执行一次拉取。</p>
              <div class="code-block">
                <code>git checkout main</code>
                <code>git pull origin main</code>
              </div>
            </div>

            <div class="why-box">
              <div class="why-label">为什么？</div>
              <p>你的同事（比如 Bob）可能昨晚加班推了新代码。如果你不拉取直接写，你的起跑线就是"旧的"，等你写完再推，<span class="danger">必定冲突</span>。</p>
            </div>

            <div class="rule-box">
              <span class="rule-icon">⚖️</span>
              <span class="rule-text">铁律：不 Pull 不开工。</span>
            </div>
          </div>
        </div>

        <!-- 白天 -->
        <div class="timeline-item daytime">
          <div class="time-badge">
            <span class="time-icon">💻</span>
            <span class="time-text">10:00 - 17:00</span>
          </div>
          <div class="timeline-content">
            <div class="section-header">
              <span class="section-num">2</span>
              <h2>白天：小步快跑，勤存档</h2>
            </div>

            <div class="scenario-box">
              <div class="scenario-label">场景</div>
              <p>开发一个大功能（Feature）。</p>
            </div>

            <div class="action-box">
              <div class="action-label">动作</div>
              <p>不要等写完 500 行代码才提交。每完成一个小的逻辑闭环（比如写完了一个函数，改好了一个样式），就本地 Commit 一次。</p>
              <div class="code-block">
                <code>git add .</code>
                <code>git commit -m "feat: 完成了登录框样式"</code>
                <code class="comment"># ... 又过了一小时 ...</code>
                <code>git add .</code>
                <code>git commit -m "fix: 修复了输入框校验 Bug"</code>
              </div>
            </div>

            <div class="why-box">
              <div class="why-label">为什么？</div>
              <p>Commit 是你的<span class="highlight">"游戏存档"</span>。存档越密，写崩了回滚的代价越小。这也是给同事看的"工作日志"。</p>
            </div>
          </div>
        </div>

        <!-- 傍晚 -->
        <div class="timeline-item evening">
          <div class="time-badge">
            <span class="time-icon">🌙</span>
            <span class="time-text">18:00 PM</span>
          </div>
          <div class="timeline-content">
            <div class="section-header">
              <span class="section-num">3</span>
              <h2>傍晚：下班前，必须交作业</h2>
            </div>

            <div class="scenario-box">
              <div class="scenario-label">场景</div>
              <p>准备收拾包回家。</p>
            </div>

            <div class="action-box">
              <div class="action-label">动作</div>
              <p>确保本地代码已经 Commit，然后尝试推送到云端。</p>
            </div>

            <!-- 情况 A -->
            <div class="case-box case-success">
              <div class="case-header">
                <span class="case-icon">✅</span>
                <span class="case-title">情况 A：一切顺利</span>
              </div>
              <div class="code-block">
                <code>git push origin main</code>
                <code class="success"># 显示 Success -> 关机回家 🏃‍♂️</code>
              </div>
            </div>

            <!-- 情况 B -->
            <div class="case-box case-error">
              <div class="case-header">
                <span class="case-icon">🛑</span>
                <span class="case-title">情况 B：报错 Rejected (被拒绝)</span>
              </div>
              <div class="case-reason">
                <strong>原因：</strong>有人（Bob）在你前面 Push 了，云端有了新东西。
              </div>

              <div class="sop-box">
                <div class="sop-header">SOP (标准处理流程)：</div>
                <div class="sop-steps">
                  <div class="sop-step">
                    <span class="step-num">1</span>
                    <div class="step-content">
                      <strong>冷静：</strong>不要慌，不要强行覆盖。
                    </div>
                  </div>
                  <div class="sop-step">
                    <span class="step-num">2</span>
                    <div class="step-content">
                      <strong>拉取：</strong>把对方的代码拉下来合并。
                      <div class="code-block mini">
                        <code>git pull origin main</code>
                        <code class="comment"># Git 会自动弹出合并提示，保存退出即可（如果无代码冲突）</code>
                      </div>
                    </div>
                  </div>
                  <div class="sop-step">
                    <span class="step-num">3</span>
                    <div class="step-content">
                      <strong>再次推送：</strong>
                      <div class="code-block mini">
                        <code>git push origin main</code>
                        <code class="success"># 这次一定成功 -> 关机回家 🏃‍♂️</code>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 冲突处理 -->
        <div class="timeline-item conflict">
          <div class="time-badge warning">
            <span class="time-icon">⚠️</span>
            <span class="time-text">特别条款</span>
          </div>
          <div class="timeline-content">
            <div class="section-header">
              <span class="section-num">4</span>
              <h2>冲突处理 (Conflict)</h2>
            </div>

            <div class="conflict-trigger">
              如果在 <code>git pull</code> 时提示 <span class="danger">CONFLICT (content)</span>：
            </div>

            <div class="conflict-steps">
              <div class="conflict-step">
                <span class="step-icon">🚫</span>
                <span>不要直接提交。</span>
              </div>
              <div class="conflict-step">
                <span class="step-icon">🔍</span>
                <span>打开代码编辑器，搜索 <code>&lt;&lt;&lt;&lt;&lt;&lt;&lt;</code>。</span>
              </div>
              <div class="conflict-step">
                <span class="step-icon">🤔</span>
                <span>人工决定：保留你的？保留他的？还是都要？</span>
              </div>
              <div class="conflict-step">
                <span class="step-icon">✅</span>
                <span>修改完后，执行：</span>
              </div>
            </div>

            <div class="code-block">
              <code>git add .</code>
              <code>git commit -m "fix: 解决与 Bob 的代码冲突"</code>
              <code>git push origin main</code>
            </div>
          </div>
        </div>
      </div>

      <!-- 总结 -->
      <div class="summary-section">
        <div class="summary-header">
          <span class="summary-icon">📢</span>
          <h2>总结</h2>
        </div>
        <p class="summary-intro">记住这个循环，保你开发无忧：</p>

        <div class="workflow-cycle">
          <div class="cycle-step pull">
            <span class="cycle-icon">🔄</span>
            <span class="cycle-label">Pull</span>
            <span class="cycle-time">(早晨)</span>
          </div>
          <div class="cycle-arrow">➡️</div>
          <div class="cycle-step commit">
            <span class="cycle-icon">✍️</span>
            <span class="cycle-label">Commit</span>
            <span class="cycle-time">(白天)</span>
          </div>
          <div class="cycle-arrow">➡️</div>
          <div class="cycle-step pull-check">
            <span class="cycle-icon">🔄</span>
            <span class="cycle-label">Pull</span>
            <span class="cycle-time">(推前检查)</span>
          </div>
          <div class="cycle-arrow">➡️</div>
          <div class="cycle-step push">
            <span class="cycle-icon">🚀</span>
            <span class="cycle-label">Push</span>
            <span class="cycle-time">(傍晚)</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 早晚课规范页面 - 无需额外逻辑
</script>

<style scoped>
.routine-page {
  --bg: #0d1117;
  --card-bg: #161b22;
  --border: #30363d;
  --text-main: #c9d1d9;
  --text-dim: #8b949e;

  --c-morning: #f59e0b;
  --c-daytime: #3b82f6;
  --c-evening: #a855f7;
  --c-conflict: #ef4444;
  --c-success: #10b981;

  min-height: 100vh;
  background: var(--bg);
  color: var(--text-main);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* Header */
.page-header {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%);
  border-bottom: 1px solid var(--border);
  padding: 40px;
}

.header-content {
  max-width: 1000px;
  margin: 0 auto;
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.header-icon {
  font-size: 48px;
}

.header-text h1 {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 12px 0;
}

.core-principle {
  font-size: 16px;
  color: var(--text-dim);
  margin: 0 0 8px 0;
}

.core-principle strong {
  color: var(--c-morning);
}

.slogan {
  font-size: 14px;
  color: var(--text-dim);
  margin: 0;
}

.highlight {
  color: var(--c-success);
  font-weight: 600;
}

.danger {
  color: var(--c-conflict);
  font-weight: 600;
}

/* Container */
.routine-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 20px;
}

/* Timeline */
.timeline {
  position: relative;
  padding-left: 40px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 15px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(to bottom, var(--c-morning), var(--c-daytime), var(--c-evening), var(--c-conflict));
}

.timeline-item {
  position: relative;
  margin-bottom: 40px;
}

.timeline-item::before {
  content: '';
  position: absolute;
  left: -33px;
  top: 8px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 3px solid;
}

.timeline-item.morning::before { border-color: var(--c-morning); background: var(--bg); }
.timeline-item.daytime::before { border-color: var(--c-daytime); background: var(--bg); }
.timeline-item.evening::before { border-color: var(--c-evening); background: var(--bg); }
.timeline-item.conflict::before { border-color: var(--c-conflict); background: var(--bg); }

.time-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 15px;
}

.morning .time-badge { background: rgba(245, 158, 11, 0.15); color: var(--c-morning); }
.daytime .time-badge { background: rgba(59, 130, 246, 0.15); color: var(--c-daytime); }
.evening .time-badge { background: rgba(168, 85, 247, 0.15); color: var(--c-evening); }
.conflict .time-badge { background: rgba(239, 68, 68, 0.15); color: var(--c-conflict); }

.time-icon {
  font-size: 16px;
}

.timeline-content {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 25px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.section-num {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  color: #fff;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

/* Boxes */
.scenario-box,
.action-box,
.why-box {
  margin-bottom: 15px;
  padding: 15px;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.2);
}

.scenario-box { border-left: 3px solid var(--text-dim); }
.action-box { border-left: 3px solid var(--c-daytime); }
.why-box { border-left: 3px solid var(--c-morning); }

.scenario-label,
.action-label,
.why-label {
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 8px;
}

.scenario-label { color: var(--text-dim); }
.action-label { color: var(--c-daytime); }
.why-label { color: var(--c-morning); }

.scenario-box p,
.action-box p,
.why-box p {
  font-size: 14px;
  color: var(--text-main);
  margin: 0;
  line-height: 1.6;
}

/* Code Block */
.code-block {
  background: #010409;
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 12px 15px;
  margin-top: 10px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
}

.code-block code {
  display: block;
  font-size: 13px;
  color: #e6edf3;
  margin-bottom: 4px;
}

.code-block code:last-child {
  margin-bottom: 0;
}

.code-block code.comment {
  color: #6e7681;
  font-style: italic;
}

.code-block code.success {
  color: var(--c-success);
}

.code-block.mini {
  margin-top: 8px;
  padding: 8px 12px;
}

.code-block.mini code {
  font-size: 12px;
}

/* Rule Box */
.rule-box {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 15px;
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 8px;
  margin-top: 15px;
}

.rule-icon {
  font-size: 20px;
}

.rule-text {
  font-size: 14px;
  font-weight: 700;
  color: var(--c-morning);
}

/* Case Boxes */
.case-box {
  margin-top: 15px;
  border-radius: 8px;
  overflow: hidden;
}

.case-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 15px;
  font-weight: 700;
  font-size: 14px;
}

.case-success .case-header {
  background: rgba(16, 185, 129, 0.15);
  color: var(--c-success);
}

.case-error .case-header {
  background: rgba(239, 68, 68, 0.15);
  color: var(--c-conflict);
}

.case-box .code-block {
  border-radius: 0;
  border-left: none;
  border-right: none;
  border-bottom: none;
}

.case-reason {
  padding: 12px 15px;
  font-size: 13px;
  color: var(--text-dim);
  background: rgba(0, 0, 0, 0.2);
}

/* SOP Box */
.sop-box {
  padding: 15px;
  background: rgba(0, 0, 0, 0.2);
}

.sop-header {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-dim);
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.sop-steps {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.sop-step {
  display: flex;
  gap: 12px;
}

.sop-step .step-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--c-evening);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}

.sop-step .step-content {
  flex: 1;
  font-size: 13px;
  color: var(--text-main);
  line-height: 1.5;
}

/* Conflict Section */
.conflict-trigger {
  font-size: 14px;
  color: var(--text-main);
  margin-bottom: 20px;
  padding: 15px;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.conflict-trigger code {
  background: rgba(0, 0, 0, 0.3);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}

.conflict-steps {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 15px;
}

.conflict-step {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
}

.conflict-step .step-icon {
  font-size: 18px;
}

.conflict-step code {
  background: rgba(239, 68, 68, 0.2);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  color: var(--c-conflict);
}

/* Summary Section */
.summary-section {
  margin-top: 50px;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 30px;
  text-align: center;
}

.summary-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 15px;
}

.summary-icon {
  font-size: 28px;
}

.summary-header h2 {
  font-size: 22px;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.summary-intro {
  font-size: 16px;
  color: var(--text-dim);
  margin-bottom: 25px;
}

/* Workflow Cycle */
.workflow-cycle {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  flex-wrap: wrap;
}

.cycle-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 15px 20px;
  border-radius: 12px;
  min-width: 100px;
}

.cycle-step.pull,
.cycle-step.pull-check {
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.cycle-step.commit {
  background: rgba(245, 158, 11, 0.15);
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.cycle-step.push {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.cycle-icon {
  font-size: 24px;
}

.cycle-label {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
}

.cycle-time {
  font-size: 11px;
  color: var(--text-dim);
}

.cycle-arrow {
  font-size: 20px;
  color: var(--text-dim);
}

/* Responsive */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    text-align: center;
  }

  .header-icon {
    font-size: 40px;
  }

  .header-text h1 {
    font-size: 22px;
  }

  .timeline {
    padding-left: 30px;
  }

  .timeline::before {
    left: 10px;
  }

  .timeline-item::before {
    left: -28px;
  }

  .workflow-cycle {
    gap: 8px;
  }

  .cycle-step {
    padding: 10px 15px;
    min-width: 80px;
  }

  .cycle-arrow {
    font-size: 16px;
  }
}
</style>
