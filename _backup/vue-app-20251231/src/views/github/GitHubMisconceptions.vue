<template>
  <div class="github-page">
    <header class="page-header">
      <div class="header-content">
        <h1>常见误区解析 (Concept Clarification)</h1>
        <p class="subtitle">澄清 GitHub 中容易混淆的概念</p>
      </div>
    </header>

    <div class="mis-container">
      <div class="mis-grid">
        <!-- Issue Misconception -->
        <div class="mis-card">
          <h3>🎫 1. Issue (工单)</h3>
          <div class="compare-box">
            <div class="myth">❌ 误解：Issue = 问题 / Bug / 报错</div>
            <div class="fact">✅ 真相：Issue = "要做的事" (To-Do)</div>
          </div>
          <div class="qa-box">
            <div class="q-item">为什么叫 Issue？</div>
            <div class="a-item">
              它是"发行/分发"的意思（像发行报纸一样）。在工程界，它指的是"发出来的一张单子"。
            </div>
            <div class="q-item">它包含什么？</div>
            <div class="a-item">
              <ul>
                <li><strong>Bug：</strong>马桶漏水了，修一下。（你理解的"问题"）</li>
                <li><strong>Task：</strong>去买十袋水泥。（这是一个"任务"）</li>
                <li><strong>Idea：</strong>觉得墙壁刷粉色更好看。（这是一个"提议"）</li>
              </ul>
            </div>
            <div class="a-item highlight">
              👉 一句话定义：只要是需要人去处理的任何事情，在 GitHub 上都叫 Issue。
            </div>
          </div>
        </div>

        <!-- Feature Misconception -->
        <div class="mis-card">
          <h3>📦 2. Feature (特性)</h3>
          <div class="compare-box">
            <div class="myth">❌ 误解：Feature = 一个按钮 / 一个页面</div>
            <div class="fact">✅ 真相：Feature = "完整能力" (Value Capability)</div>
          </div>
          <div class="qa-box">
            <div class="q-item">它是什么？</div>
            <div class="a-item">
              Feature 是用户能感知到的完整价值。比如"微信支付"、"暗黑模式"、"购物车"。
            </div>
            <div class="q-item">它和 Issue 的关系？</div>
            <div class="a-item">
              <strong>Feature 是目标，Issue 是步骤。</strong><br>
              要实现一个 Feature（目标），往往需要拆解成几十个 Issue（步骤）。
              例如：Feature 是"智能安防系统"，Issue 1 是"买门锁"，Issue 2 是"打孔"。
            </div>
          </div>
        </div>

        <!-- Issue vs Ticket Misconception -->
        <div class="mis-card wide-card">
          <h3>🎫 vs 🎟️ 3. Issue 与 Ticket 的区别</h3>
          <div class="compare-box">
            <div class="myth">❌ 误解：Issue 和 Ticket 是同一个东西</div>
            <div class="fact">✅ 真相：Issue 管代码任务，Ticket 找官方客服</div>
          </div>

          <div class="definition-grid">
            <div class="def-block">
              <div class="def-header issue-header">
                <span class="def-icon">🎫</span>
                <span class="def-name">GitHub Issue (议题)</span>
              </div>
              <ul class="def-list">
                <li><strong>是什么：</strong>GitHub 平台的核心功能，用于追踪 bug、新功能建议、任务列表或讨论</li>
                <li><strong>给谁用：</strong>开发者、项目维护者、开源社区贡献者</li>
                <li><strong>在哪里：</strong>每个仓库顶部的 "Issues" 标签页</li>
                <li><strong>用途：</strong>"发现代码有个 bug"、"需要开发新功能"、"这里有个讨论"</li>
              </ul>
            </div>

            <div class="def-block">
              <div class="def-header ticket-header">
                <span class="def-icon">🎟️</span>
                <span class="def-name">GitHub Support Ticket (支持工单)</span>
              </div>
              <ul class="def-list">
                <li><strong>是什么：</strong>你向 GitHub <strong>官方客服团队</strong>发起的求助请求</li>
                <li><strong>给谁用：</strong>遇到账户被封、账单问题、服务器故障的用户</li>
                <li><strong>在哪里：</strong>GitHub 的 Support Portal（不在代码仓库里）</li>
                <li><strong>用途：</strong>"登录不上账号"、"CI/CD 额度算错了"、"举报恶意仓库"</li>
              </ul>
            </div>
          </div>

          <div class="qa-box">
            <div class="q-item">为什么大家经常混用这两个词？</div>
            <div class="a-item">
              虽然 GitHub 官方叫 "Issue"，但在软件开发行业，大家习惯把<strong>所有的任务单元</strong>都口语化地称为 "Ticket"。
              <ul>
                <li><strong>口语习惯：</strong>很多从 Jira、Zendesk 转过来的开发者，嘴上说 "建一个 Ticket"，实际上指 "去 GitHub 提一个 Issue"。</li>
                <li><strong>集成场景：</strong>很多公司使用 Jira 管理需求，GitHub 管理代码。产品经理在 Jira 建 Ticket，同步给程序员在 GitHub 建 Issue。</li>
              </ul>
            </div>
          </div>

          <!-- 对比表格 -->
          <div class="compare-table">
            <table>
              <thead>
                <tr>
                  <th>特性</th>
                  <th>GitHub Issue (议题)</th>
                  <th>Support Ticket (官方工单)</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>可见性</strong></td>
                  <td>公开/团队可见（取决于仓库权限）</td>
                  <td>私密（只有你和客服能看）</td>
                </tr>
                <tr>
                  <td><strong>主要目的</strong></td>
                  <td>项目协作、代码开发、Bug 追踪</td>
                  <td>解决账户、账单、平台故障问题</td>
                </tr>
                <tr>
                  <td><strong>交互对象</strong></td>
                  <td>你的同事、开源社区贡献者</td>
                  <td>GitHub 公司的客服人员</td>
                </tr>
                <tr>
                  <td><strong>能否关联代码</strong></td>
                  <td>能（可关联 PR 和 Commit）</td>
                  <td>不能</td>
                </tr>
                <tr>
                  <td><strong>费用</strong></td>
                  <td>免费（包含在仓库功能中）</td>
                  <td>基础免费，高级支持可能收费</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 场景判断 -->
          <div class="scenario-box">
            <div class="scenario-title">场景判断指南</div>
            <div class="scenario-item">
              <span class="scenario-label">场景 A：</span>
              <span class="scenario-desc">你的代码跑不通，或者你想建议开源作者加个功能</span>
              <span class="scenario-action">👉 去仓库提一个 <strong>Issue</strong></span>
            </div>
            <div class="scenario-item">
              <span class="scenario-label">场景 B：</span>
              <span class="scenario-desc">你的 GitHub 账号被盗了，或者信用卡扣款失败</span>
              <span class="scenario-action">👉 去 Support Portal 提交 <strong>Ticket</strong></span>
            </div>
            <div class="scenario-item">
              <span class="scenario-label">场景 C：</span>
              <span class="scenario-desc">老板跟你说："给这个 Bug 开个 Ticket"</span>
              <span class="scenario-action">👉 翻译：老板是让你去仓库里提一个 <strong>Issue</strong></span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 常见误区页面 - 无需额外逻辑
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
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(239, 68, 68, 0.15) 100%);
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

.mis-container {
  padding: 40px;
  max-width: 1400px;
  margin: 0 auto;
}

.mis-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
}

.mis-card {
  background: rgba(255,255,255,0.02);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 30px;
}

.wide-card {
  grid-column: 1 / -1;
}

.mis-card h3 {
  font-size: 18px;
  color: #fff;
  margin-bottom: 20px;
}

.compare-box {
  display: flex;
  gap: 0;
  margin-bottom: 25px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border);
}

.myth {
  color: #f87171;
  font-size: 13px;
  flex: 1;
  background: rgba(239,68,68,0.1);
  padding: 12px 15px;
  border-right: 1px solid var(--border);
}

.fact {
  color: #4ade80;
  font-size: 13px;
  flex: 1;
  background: rgba(34,197,94,0.1);
  padding: 12px 15px;
  font-weight: bold;
}

.qa-box {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.q-item {
  font-size: 14px;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 4px;
}

.q-item::before {
  content: 'Q: ';
  color: var(--text-dim);
}

.a-item {
  font-size: 13px;
  color: var(--text-dim);
  line-height: 1.6;
  padding-left: 20px;
}

.a-item ul {
  margin: 5px 0 0 0;
  padding-left: 20px;
}

.a-item li {
  margin-bottom: 4px;
}

.a-item.highlight {
  color: var(--c-task);
  font-weight: bold;
  margin-top: 5px;
}

/* Issue vs Ticket 样式 */
.definition-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 25px;
}

.def-block {
  background: rgba(0,0,0,0.2);
  border-radius: 10px;
  padding: 20px;
  border: 1px solid var(--border);
}

.def-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
  padding-bottom: 12px;
  border-bottom: 2px solid;
}

.issue-header {
  border-color: var(--c-task);
}

.ticket-header {
  border-color: #f59e0b;
}

.def-icon {
  font-size: 24px;
}

.def-name {
  font-size: 15px;
  font-weight: 700;
  color: #fff;
}

.def-list {
  margin: 0;
  padding-left: 20px;
  font-size: 13px;
  color: var(--text-dim);
  line-height: 1.8;
}

.def-list li {
  margin-bottom: 6px;
}

/* 对比表格 */
.compare-table {
  margin: 25px 0;
  overflow-x: auto;
}

.compare-table table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.compare-table th,
.compare-table td {
  padding: 12px 15px;
  text-align: left;
  border: 1px solid var(--border);
}

.compare-table th {
  background: rgba(255,255,255,0.05);
  color: #fff;
  font-weight: 600;
}

.compare-table td {
  color: var(--text-dim);
}

.compare-table tbody tr:hover {
  background: rgba(255,255,255,0.02);
}

/* 场景判断 */
.scenario-box {
  background: linear-gradient(135deg, rgba(59,130,246,0.1) 0%, rgba(168,85,247,0.1) 100%);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 20px;
}

.scenario-title {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border);
}

.scenario-item {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 8px;
  padding: 10px 0;
  border-bottom: 1px dashed rgba(255,255,255,0.1);
}

.scenario-item:last-child {
  border-bottom: none;
}

.scenario-label {
  font-weight: 700;
  color: #a78bfa;
  font-size: 13px;
  min-width: 70px;
}

.scenario-desc {
  color: var(--text-dim);
  font-size: 13px;
  flex: 1;
}

.scenario-action {
  color: #4ade80;
  font-size: 13px;
  font-weight: 600;
  width: 100%;
  padding-left: 78px;
}

@media (max-width: 900px) {
  .mis-grid {
    grid-template-columns: 1fr;
  }

  .definition-grid {
    grid-template-columns: 1fr;
  }
}
</style>
