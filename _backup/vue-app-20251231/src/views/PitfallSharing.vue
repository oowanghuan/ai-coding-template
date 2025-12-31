<template>
  <div class="pitfall-page">
    <header class="page-header">
      <div class="header-content">
        <h1>踩坑分享</h1>
        <p class="subtitle">团队协作中的经验总结与最佳实践</p>
      </div>
    </header>

    <div class="pitfall-container">
      <div class="pitfall-grid">
        <!-- YAML vs Markdown -->
        <div class="pitfall-card">
          <div class="card-header">
            <span class="card-icon">📄</span>
            <span class="card-tag">文档规范</span>
          </div>
          <h3>YAML vs Markdown 选择</h3>
          <div class="compare-box">
            <div class="myth">误解：所有文档都用 Markdown</div>
            <div class="fact">真相：给人读用 MD，给程序读用 YAML</div>
          </div>
          <div class="qa-box">
            <div class="q-item">为什么 PROGRESS_LOG 用 YAML？</div>
            <div class="a-item">
              因为 Dashboard 需要<strong>结构化数据</strong>来展示甘特图、计算完成率。
              <ul>
                <li><strong>YAML：</strong>程序可以直接 <code>YAML.load()</code> 解析，判断 <code>if task.status === 'done'</code></li>
                <li><strong>Markdown：</strong><code>- [x] 任务完成</code> 这种格式程序很难可靠解析</li>
              </ul>
            </div>
            <div class="q-item">什么时候用 Markdown？</div>
            <div class="a-item">
              <ul>
                <li><strong>10_CONTEXT.md：</strong>功能背景说明，给人读</li>
                <li><strong>40_DESIGN.md：</strong>设计文档，有代码块、表格、架构图</li>
                <li><strong>91_DAILY_SUMMARY/*.md：</strong>每日总结，给人读</li>
              </ul>
            </div>
            <div class="a-item highlight">
              一句话总结：给人读 → Markdown，给程序读 → YAML
            </div>
          </div>
        </div>

        <!-- 占位：更多踩坑分享 -->
        <div class="pitfall-card placeholder-card">
          <div class="card-header">
            <span class="card-icon">💡</span>
            <span class="card-tag">待添加</span>
          </div>
          <h3>更多经验待分享...</h3>
          <div class="placeholder-content">
            <p>遇到问题？总结经验？</p>
            <p>告诉 Claude Code，它会帮你整理到这里！</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 踩坑分享页面
</script>

<style scoped>
.pitfall-page {
  --bg: #0d1117;
  --card-bg: #161b22;
  --border: #30363d;
  --text-main: #f8fafc;
  --text-dim: #8b949e;
  --c-primary: #3b82f6;
  --c-success: #10b981;
  --c-warning: #f59e0b;
  --c-danger: #ef4444;

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

.pitfall-container {
  padding: 40px;
  max-width: 1400px;
  margin: 0 auto;
}

.pitfall-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
  gap: 30px;
}

.pitfall-card {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px;
  transition: border-color 0.2s;
}

.pitfall-card:hover {
  border-color: var(--c-primary);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.card-icon {
  font-size: 24px;
}

.card-tag {
  font-size: 12px;
  padding: 4px 10px;
  background: rgba(59, 130, 246, 0.15);
  color: var(--c-primary);
  border-radius: 20px;
  font-weight: 500;
}

.pitfall-card h3 {
  font-size: 18px;
  color: #fff;
  margin: 0 0 16px 0;
}

.compare-box {
  display: flex;
  gap: 0;
  margin-bottom: 20px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border);
}

.myth {
  color: #f87171;
  font-size: 13px;
  flex: 1;
  background: rgba(239, 68, 68, 0.1);
  padding: 12px 15px;
  border-right: 1px solid var(--border);
}

.myth::before {
  content: '❌ ';
}

.fact {
  color: #4ade80;
  font-size: 13px;
  flex: 1;
  background: rgba(34, 197, 94, 0.1);
  padding: 12px 15px;
  font-weight: bold;
}

.fact::before {
  content: '✅ ';
}

.qa-box {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.q-item {
  font-size: 14px;
  font-weight: 700;
  color: #e2e8f0;
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
  margin: 8px 0 0 0;
  padding-left: 20px;
}

.a-item li {
  margin-bottom: 6px;
}

.a-item.highlight {
  color: var(--c-primary);
  font-weight: bold;
  margin-top: 8px;
  padding: 12px 16px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 8px;
  border-left: 3px solid var(--c-primary);
}

.a-item.highlight::before {
  content: '👉 ';
}

.a-item code {
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'SF Mono', Monaco, monospace;
  font-size: 12px;
}

/* 占位卡片 */
.placeholder-card {
  border-style: dashed;
  opacity: 0.7;
}

.placeholder-card:hover {
  opacity: 1;
}

.placeholder-content {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-dim);
}

.placeholder-content p {
  margin: 8px 0;
  font-size: 14px;
}

@media (max-width: 600px) {
  .pitfall-grid {
    grid-template-columns: 1fr;
  }

  .compare-box {
    flex-direction: column;
  }

  .myth {
    border-right: none;
    border-bottom: 1px solid var(--border);
  }
}
</style>
