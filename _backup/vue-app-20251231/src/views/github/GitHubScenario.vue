<template>
  <div class="scenario-page">
    <!-- Header -->
    <header class="scenario-header">
      <div class="brand">
        <span>🏗️ GitHub 实战演练</span>
        <span class="badge">3-Day Scenario</span>
      </div>
      <div class="legend">
        <div class="l-item"><div class="dot" style="background: var(--c-local)"></div>Me</div>
        <div class="l-item"><div class="dot" style="background: var(--c-bob)"></div>Bob</div>
        <div class="l-item"><div class="dot" style="background: var(--c-day1)"></div>D1</div>
        <div class="l-item"><div class="dot" style="background: var(--c-day2)"></div>D2</div>
        <div class="l-item"><div class="dot" style="background: var(--c-day3)"></div>D3</div>
        <div class="l-item"><div class="dot" style="background: var(--c-history)"></div>Past</div>
      </div>
    </header>

    <div class="scenario-container">
      <!-- Sidebar -->
      <div class="sidebar">
        <template v-for="(step, idx) in steps" :key="idx">
          <!-- Group Header -->
          <div
            v-if="idx === 0 || step.group !== steps[idx - 1].group"
            class="day-header"
          >
            {{ step.group }}
          </div>
          <!-- Step Item -->
          <div
            class="step-item"
            :class="{ active: currentStepIndex === idx }"
            @click="loadStep(idx)"
          >
            <div class="step-num">{{ idx + 1 }}</div>
            <div class="step-content">
              <div class="step-title">{{ step.title }}</div>
              <div class="step-desc" v-html="step.desc"></div>
            </div>
          </div>
        </template>
      </div>

      <!-- Main View -->
      <div class="main-view">
        <div class="canvas-wrapper">
          <div class="env-label label-remote">☁️ Remote Origin</div>
          <div class="env-label label-local">💻 Your Local</div>

          <svg ref="gitSvg" viewBox="0 0 1000 450">
            <g ref="pathsLayer"></g>
            <g ref="nodesLayer"></g>
            <g ref="animLayer"></g>
          </svg>

          <div
            class="tooltip"
            ref="tooltip"
            :style="{ left: tooltipLeft, top: tooltipTop, opacity: tooltipVisible ? 1 : 0 }"
          >
            <span :style="{ fontWeight: 'bold', color: tooltipColor }">{{ tooltipMsg }}</span><br>
            <span style="color: #aaa; font-size: 10px">{{ tooltipSub }}</span>
          </div>

          <div class="err-toast" :class="{ show: showErrToast }">
            🚫 PUSH REJECTED<br>
            <span style="font-size: 12px; font-weight: normal; color: #ffcfcc">remote is ahead of your local</span>
          </div>
        </div>

        <div class="terminal" ref="terminalEl">
          <div
            v-for="(line, idx) in terminalLines"
            :key="idx"
            class="term-line"
            :style="{ animationDelay: idx * 0.2 + 's' }"
          >
            <span :class="['term-tag', getRoleClass(line.user)]">{{ line.user }}</span>
            <div style="flex: 1">
              <div :class="line.isErr ? 'term-err' : 'term-cmd'">{{ line.isErr ? '' : '$ ' }}{{ line.cmd }}</div>
              <div class="term-out">{{ line.out }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'

// Constants
const REMOTE_Y = 100
const LOCAL_Y = 350

const C = {
  history: 'var(--c-history)',
  day1: 'var(--c-day1)',
  day2: 'var(--c-day2)',
  day3: 'var(--c-day3)',
  bob: 'var(--c-bob)',
  you: 'var(--c-local)'
}

// Steps Data
const steps = [
  // --- DAY 1 (Detailed) ---
  {
    id: 0,
    group: 'Day 1: 单人开发 (Solo)',
    role: 'You',
    title: '1. 拉取 (Pull)',
    desc: '每天开始工作第一件事：拉取最新代码，确保本地与云端同步。',
    cmds: [
      { user: 'You', cmd: 'git pull origin main', out: 'Already up to date.' }
    ],
    state: {
      commits: [
        { id: 'R0', x: 50, y: REMOTE_Y, color: C.day1, icon: '☁️', msg: 'Init', sub: 'Remote' },
        { id: 'L0', x: 50, y: LOCAL_Y, color: C.day1, icon: '👩‍💻', msg: 'Init', sub: 'Local' }
      ],
      branches: [
        { pts: [{ x: 20, y: REMOTE_Y }, { x: 50, y: REMOTE_Y }], color: C.day1 },
        { pts: [{ x: 20, y: LOCAL_Y }, { x: 50, y: LOCAL_Y }], color: C.day1 }
      ]
    }
  },
  {
    id: 1,
    group: 'Day 1: 单人开发 (Solo)',
    role: 'You',
    title: '2. 开发 & 提交 (Commit)',
    desc: '你在本地写代码。Commit 将你的修改保存到本地仓库（存了一个档）。',
    cmds: [
      { user: 'You', cmd: 'git add .', out: '' },
      { user: 'You', cmd: 'git commit -m "Feat: Base"', out: '[main] Feat: Base' }
    ],
    state: {
      commits: [
        { id: 'R0', x: 50, y: REMOTE_Y, color: C.day1, icon: '☁️', msg: 'Init' },
        { id: 'L0', x: 50, y: LOCAL_Y, color: C.day1, icon: '👩‍💻', msg: 'Init' },
        { id: 'L1', x: 150, y: LOCAL_Y, color: C.day1, icon: '👩‍💻', msg: 'Base Feat', sub: 'You' }
      ],
      branches: [
        { pts: [{ x: 20, y: REMOTE_Y }, { x: 50, y: REMOTE_Y }], color: C.day1 },
        { pts: [{ x: 20, y: LOCAL_Y }, { x: 150, y: LOCAL_Y }], color: C.day1 }
      ]
    }
  },
  {
    id: 2,
    group: 'Day 1: 单人开发 (Solo)',
    role: 'You',
    title: '3. 推送 (Push)',
    desc: '下班了，把本地的存档推送到云端。此时云端节点向前移动。',
    cmds: [{ user: 'You', cmd: 'git push', out: 'main -> main' }],
    anim: { from: { x: 150, y: LOCAL_Y }, to: { x: 150, y: REMOTE_Y }, icon: '🚀' },
    state: {
      commits: [
        { id: 'R0', x: 50, y: REMOTE_Y, color: C.day1, icon: '☁️', msg: 'Init' },
        { id: 'R1', x: 150, y: REMOTE_Y, color: C.day1, icon: '☁️', msg: 'Base Feat', sub: 'Synced' },
        { id: 'L0', x: 50, y: LOCAL_Y, color: C.day1, icon: '👩‍💻', msg: 'Init' },
        { id: 'L1', x: 150, y: LOCAL_Y, color: C.day1, icon: '👩‍💻', msg: 'Base Feat' }
      ],
      branches: [
        { pts: [{ x: 20, y: REMOTE_Y }, { x: 150, y: REMOTE_Y }], color: C.day1 },
        { pts: [{ x: 20, y: LOCAL_Y }, { x: 150, y: LOCAL_Y }], color: C.day1 }
      ],
      links: [{ from: 'L1', to: 'R1', dashed: true }]
    }
  },

  // --- DAY 2 (Parallel - Smooth) ---
  {
    id: 3,
    group: 'Day 2: 多人并行 (顺畅)',
    role: 'System',
    title: '第二天：并行开始',
    desc: '第二天，Bob 加入了。昨天的代码变灰（保留历史）。云端目前停留在昨天的进度。',
    cmds: [{ user: 'System', cmd: '--- DAY 2 START ---', out: 'Bob joined. Day 1 archived.' }],
    state: {
      commits: [
        { id: 'R0', x: 50, y: REMOTE_Y, color: C.history, icon: '☁️', msg: 'Init' },
        { id: 'R1', x: 150, y: REMOTE_Y, color: C.history, icon: '☁️', msg: 'Base Feat', sub: 'History' },
        { id: 'L0', x: 50, y: LOCAL_Y, color: C.history, icon: '👩‍💻', msg: 'Init' },
        { id: 'L1', x: 150, y: LOCAL_Y, color: C.history, icon: '👩‍💻', msg: 'Base Feat' }
      ],
      branches: [
        { pts: [{ x: 20, y: REMOTE_Y }, { x: 150, y: REMOTE_Y }], color: C.history },
        { pts: [{ x: 20, y: LOCAL_Y }, { x: 150, y: LOCAL_Y }], color: C.history }
      ]
    }
  },
  {
    id: 4,
    group: 'Day 2: 多人并行 (顺畅)',
    role: 'Team',
    title: '双线开工 (Parallel)',
    desc: 'Bob 在写【登录】，你在写【首页】。注意看：云端出现了 Bob 的提交，本地出现了你的提交。',
    cmds: [
      { user: 'Bob', cmd: 'git push', out: 'Pushed "Login"' },
      { user: 'You', cmd: 'git commit -m "Home"', out: '[main] Home' }
    ],
    state: {
      commits: [
        { id: 'R0', x: 50, y: REMOTE_Y, color: C.history, icon: '☁️', msg: 'Init' },
        { id: 'R1', x: 150, y: REMOTE_Y, color: C.history, icon: '☁️', msg: 'Base' },
        { id: 'R2', x: 250, y: REMOTE_Y, color: C.bob, icon: '👱', msg: 'Login', sub: 'Bob (Remote)' },
        { id: 'L0', x: 50, y: LOCAL_Y, color: C.history, icon: '👩‍💻', msg: 'Init' },
        { id: 'L1', x: 150, y: LOCAL_Y, color: C.history, icon: '👩‍💻', msg: 'Base' },
        { id: 'L2', x: 250, y: LOCAL_Y, color: C.day2, icon: '👩‍💻', msg: 'Home', sub: 'You (Local)' }
      ],
      branches: [
        { pts: [{ x: 20, y: REMOTE_Y }, { x: 150, y: REMOTE_Y }], color: C.history },
        { pts: [{ x: 150, y: REMOTE_Y }, { x: 250, y: REMOTE_Y }], color: C.bob },
        { pts: [{ x: 20, y: LOCAL_Y }, { x: 150, y: LOCAL_Y }], color: C.history },
        { pts: [{ x: 150, y: LOCAL_Y }, { x: 250, y: LOCAL_Y }], color: C.day2 }
      ]
    }
  },
  {
    id: 5,
    group: 'Day 2: 多人并行 (顺畅)',
    role: 'You',
    title: '拉取合并 (Merge)',
    desc: '你执行 `git pull`。Git 发现分叉了，于是自动把 Bob 的代码合入你的本地，形成一个菱形闭环。',
    cmds: [
      { user: 'You', cmd: 'git pull', out: 'Merge made by the "ort" strategy.' },
      { user: 'System', cmd: 'Merge', out: 'Merged "Login" into main' }
    ],
    anim: { from: { x: 250, y: REMOTE_Y }, to: { x: 350, y: LOCAL_Y }, icon: '📥' },
    state: {
      commits: [
        { id: 'R0', x: 50, y: REMOTE_Y, color: C.history, icon: '☁️', msg: 'Init' },
        { id: 'R1', x: 150, y: REMOTE_Y, color: C.history, icon: '☁️', msg: 'Base' },
        { id: 'R2', x: 250, y: REMOTE_Y, color: C.bob, icon: '👱', msg: 'Login' },
        { id: 'L0', x: 50, y: LOCAL_Y, color: C.history, icon: '👩‍💻', msg: 'Init' },
        { id: 'L1', x: 150, y: LOCAL_Y, color: C.history, icon: '👩‍💻', msg: 'Base' },
        { id: 'L2', x: 250, y: LOCAL_Y, color: C.day2, icon: '👩‍💻', msg: 'Home' },
        { id: 'L_GHOST', x: 250, y: LOCAL_Y + 60, color: C.bob, icon: '👱', msg: 'Login', opacity: 0.5 },
        { id: 'L3', x: 350, y: LOCAL_Y, color: C.day2, icon: '🔀', msg: 'Merge', sub: 'Merged' }
      ],
      branches: [
        { pts: [{ x: 20, y: REMOTE_Y }, { x: 150, y: REMOTE_Y }], color: C.history },
        { pts: [{ x: 150, y: REMOTE_Y }, { x: 250, y: REMOTE_Y }], color: C.bob },
        { pts: [{ x: 20, y: LOCAL_Y }, { x: 150, y: LOCAL_Y }], color: C.history },
        { pts: [{ x: 150, y: LOCAL_Y }, { x: 250, y: LOCAL_Y }, { x: 350, y: LOCAL_Y }], color: C.day2 },
        { pts: [{ x: 150, y: LOCAL_Y }, { x: 250, y: LOCAL_Y + 60 }, { x: 350, y: LOCAL_Y }], color: C.bob, dashed: true }
      ],
      links: [{ from: 'R2', to: 'L_GHOST', dashed: true }]
    }
  },
  {
    id: 6,
    group: 'Day 2: 多人并行 (顺畅)',
    role: 'You',
    title: '推送 (Push Success)',
    desc: '本地合并完成后，你的版本是最新的。直接 Push，云端也完成了闭环。',
    cmds: [{ user: 'You', cmd: 'git push', out: 'main -> main' }],
    anim: { from: { x: 350, y: LOCAL_Y }, to: { x: 350, y: REMOTE_Y }, icon: '🚀' },
    state: {
      commits: [
        { id: 'R0', x: 50, y: REMOTE_Y, color: C.history, icon: '☁️', msg: 'Init' },
        { id: 'R1', x: 150, y: REMOTE_Y, color: C.history, icon: '☁️', msg: 'Base' },
        { id: 'R2', x: 250, y: REMOTE_Y, color: C.bob, icon: '👱', msg: 'Login' },
        { id: 'R3', x: 350, y: REMOTE_Y, color: C.day2, icon: '🔀', msg: 'Merge', sub: 'Synced' },
        { id: 'L0', x: 50, y: LOCAL_Y, color: C.history, icon: '👩‍💻', msg: 'Init' },
        { id: 'L1', x: 150, y: LOCAL_Y, color: C.history, icon: '👩‍💻', msg: 'Base' },
        { id: 'L2', x: 250, y: LOCAL_Y, color: C.day2, icon: '👩‍💻', msg: 'Home' },
        { id: 'L3', x: 350, y: LOCAL_Y, color: C.day2, icon: '🔀', msg: 'Merge' }
      ],
      branches: [
        { pts: [{ x: 20, y: REMOTE_Y }, { x: 150, y: REMOTE_Y }], color: C.history },
        { pts: [{ x: 150, y: REMOTE_Y }, { x: 250, y: REMOTE_Y }, { x: 350, y: REMOTE_Y }], color: C.bob },
        { pts: [{ x: 20, y: LOCAL_Y }, { x: 150, y: LOCAL_Y }], color: C.history },
        { pts: [{ x: 150, y: LOCAL_Y }, { x: 250, y: LOCAL_Y }, { x: 350, y: LOCAL_Y }], color: C.day2 }
      ],
      links: [{ from: 'L3', to: 'R3', dashed: true }]
    }
  },

  // --- DAY 3 (Conflict/Reject) ---
  {
    id: 7,
    group: 'Day 3: 冲突实战 (Reject)',
    role: 'System',
    title: '第三天：准备',
    desc: '新的一天。Day 1 和 Day 2 的工作都保留并变灰。',
    cmds: [{ user: 'System', cmd: '--- DAY 3 START ---', out: 'Previous history archived.' }],
    state: {
      commits: [
        { id: 'R1', x: 150, y: REMOTE_Y, color: C.history, icon: '☁️', msg: 'Base' },
        { id: 'R2', x: 250, y: REMOTE_Y, color: C.history, icon: '👱', msg: 'Login' },
        { id: 'R3', x: 350, y: REMOTE_Y, color: C.history, icon: '🔀', msg: 'Merge' },
        { id: 'L1', x: 150, y: LOCAL_Y, color: C.history, icon: '👩‍💻', msg: 'Base' },
        { id: 'L2', x: 250, y: LOCAL_Y, color: C.history, icon: '👩‍💻', msg: 'Home' },
        { id: 'L3', x: 350, y: LOCAL_Y, color: C.history, icon: '🔀', msg: 'Merge' }
      ],
      branches: [
        { pts: [{ x: 20, y: REMOTE_Y }, { x: 150, y: REMOTE_Y }, { x: 250, y: REMOTE_Y }, { x: 350, y: REMOTE_Y }], color: C.history },
        { pts: [{ x: 20, y: LOCAL_Y }, { x: 150, y: LOCAL_Y }, { x: 250, y: LOCAL_Y }, { x: 350, y: LOCAL_Y }], color: C.history }
      ]
    }
  },
  {
    id: 8,
    group: 'Day 3: 冲突实战 (Reject)',
    role: 'You',
    title: '1. 拉取 (Pull)',
    desc: '第一步永远是 Pull。当前云端没有新代码，所以是最新的。',
    cmds: [{ user: 'You', cmd: 'git pull', out: 'Already up to date.' }],
    state: {
      commits: [
        { id: 'R2', x: 250, y: REMOTE_Y, color: C.history, icon: '👱', msg: 'Login' },
        { id: 'R3', x: 350, y: REMOTE_Y, color: C.history, icon: '🔀', msg: 'Merge' },
        { id: 'L2', x: 250, y: LOCAL_Y, color: C.history, icon: '👩‍💻', msg: 'Home' },
        { id: 'L3', x: 350, y: LOCAL_Y, color: C.history, icon: '🔀', msg: 'Merge' }
      ],
      branches: [
        { pts: [{ x: 150, y: REMOTE_Y }, { x: 350, y: REMOTE_Y }], color: C.history },
        { pts: [{ x: 150, y: LOCAL_Y }, { x: 350, y: LOCAL_Y }], color: C.history }
      ]
    }
  },
  {
    id: 9,
    group: 'Day 3: 冲突实战 (Reject)',
    role: 'You',
    title: '2. 开发 (Commit)',
    desc: '你在本地开发 Feature A 并提交。此时你还没与外界同步。',
    cmds: [{ user: 'You', cmd: 'git commit -m "Feat A"', out: '[main] Feat A' }],
    state: {
      commits: [
        { id: 'R3', x: 350, y: REMOTE_Y, color: C.history, icon: '🔀', msg: 'Merge' },
        { id: 'L3', x: 350, y: LOCAL_Y, color: C.history, icon: '🔀', msg: 'Merge' },
        { id: 'L4', x: 450, y: LOCAL_Y, color: C.day3, icon: '👩‍💻', msg: 'Feat A', sub: 'You' }
      ],
      branches: [
        { pts: [{ x: 150, y: REMOTE_Y }, { x: 350, y: REMOTE_Y }], color: C.history },
        { pts: [{ x: 150, y: LOCAL_Y }, { x: 350, y: LOCAL_Y }], color: C.history },
        { pts: [{ x: 350, y: LOCAL_Y }, { x: 450, y: LOCAL_Y }], color: C.day3 }
      ]
    }
  },
  {
    id: 10,
    group: 'Day 3: 冲突实战 (Reject)',
    role: 'Bob',
    title: '3. Bob 抢先 Push',
    desc: '<b>意外发生！</b> Bob 已经把 Feature B 推送到了云端。云端现在有了你不知道的代码。',
    cmds: [{ user: 'Bob', cmd: 'git push', out: 'Pushed "Feat B"' }],
    state: {
      commits: [
        { id: 'R3', x: 350, y: REMOTE_Y, color: C.history, icon: '🔀', msg: 'Merge' },
        { id: 'R4', x: 450, y: REMOTE_Y, color: C.bob, icon: '👱', msg: 'Feat B', sub: 'Bob' },
        { id: 'L3', x: 350, y: LOCAL_Y, color: C.history, icon: '🔀', msg: 'Merge' },
        { id: 'L4', x: 450, y: LOCAL_Y, color: C.day3, icon: '👩‍💻', msg: 'Feat A' }
      ],
      branches: [
        { pts: [{ x: 150, y: REMOTE_Y }, { x: 350, y: REMOTE_Y }], color: C.history },
        { pts: [{ x: 350, y: REMOTE_Y }, { x: 450, y: REMOTE_Y }], color: C.bob },
        { pts: [{ x: 150, y: LOCAL_Y }, { x: 350, y: LOCAL_Y }], color: C.history },
        { pts: [{ x: 350, y: LOCAL_Y }, { x: 450, y: LOCAL_Y }], color: C.day3 }
      ]
    }
  },
  {
    id: 11,
    group: 'Day 3: 冲突实战 (Reject)',
    role: 'You',
    title: '4. 尝试 Push (Reject)',
    desc: '你试图 Push，但 Git 报错："云端包含了你没有的工作"。<b>你的推送被拒绝了。</b>',
    cmds: [
      { user: 'You', cmd: 'git push', out: 'To github.com:repo.git' },
      { user: 'System', cmd: '! [rejected]', out: 'error: failed to push some refs', isErr: true }
    ],
    showErr: true,
    state: {
      commits: [
        { id: 'R3', x: 350, y: REMOTE_Y, color: C.history, icon: '🔀', msg: 'Merge' },
        { id: 'R4', x: 450, y: REMOTE_Y, color: C.bob, icon: '👱', msg: 'Feat B' },
        { id: 'L3', x: 350, y: LOCAL_Y, color: C.history, icon: '🔀', msg: 'Merge' },
        { id: 'L4', x: 450, y: LOCAL_Y, color: C.day3, icon: '👩‍💻', msg: 'Feat A' }
      ],
      branches: [
        { pts: [{ x: 150, y: REMOTE_Y }, { x: 350, y: REMOTE_Y }], color: C.history },
        { pts: [{ x: 350, y: REMOTE_Y }, { x: 450, y: REMOTE_Y }], color: C.bob },
        { pts: [{ x: 150, y: LOCAL_Y }, { x: 350, y: LOCAL_Y }], color: C.history },
        { pts: [{ x: 350, y: LOCAL_Y }, { x: 450, y: LOCAL_Y }], color: C.day3 }
      ],
      links: [{ from: 'L4', to: 'R4', color: '#f85149', dashed: true, width: 2 }]
    }
  },
  {
    id: 12,
    group: 'Day 3: 冲突实战 (Reject)',
    role: 'You',
    title: '5. 拉取合并 (Pull)',
    desc: '必须先 `git pull`。把 Bob 的 Feature B 拉下来，和你的 Feature A 合并。',
    cmds: [
      { user: 'You', cmd: 'git pull', out: 'Merge made by the "ort" strategy.' },
      { user: 'System', cmd: 'Merge', out: 'Merged "Feat B" into main' }
    ],
    anim: { from: { x: 450, y: REMOTE_Y }, to: { x: 550, y: LOCAL_Y }, icon: '📥' },
    state: {
      commits: [
        { id: 'R3', x: 350, y: REMOTE_Y, color: C.history, icon: '🔀', msg: 'Merge' },
        { id: 'R4', x: 450, y: REMOTE_Y, color: C.bob, icon: '👱', msg: 'Feat B' },
        { id: 'L3', x: 350, y: LOCAL_Y, color: C.history, icon: '🔀', msg: 'Merge' },
        { id: 'L4', x: 450, y: LOCAL_Y, color: C.day3, icon: '👩‍💻', msg: 'Feat A' },
        { id: 'L_GHOST', x: 450, y: LOCAL_Y + 60, color: C.bob, icon: '👱', msg: 'Feat B', opacity: 0.5 },
        { id: 'L5', x: 550, y: LOCAL_Y, color: C.day3, icon: '🔀', msg: 'Merge', sub: 'A + B' }
      ],
      branches: [
        { pts: [{ x: 150, y: REMOTE_Y }, { x: 350, y: REMOTE_Y }], color: C.history },
        { pts: [{ x: 350, y: REMOTE_Y }, { x: 450, y: REMOTE_Y }], color: C.bob },
        { pts: [{ x: 150, y: LOCAL_Y }, { x: 350, y: LOCAL_Y }], color: C.history },
        { pts: [{ x: 350, y: LOCAL_Y }, { x: 450, y: LOCAL_Y }, { x: 550, y: LOCAL_Y }], color: C.day3 },
        { pts: [{ x: 350, y: LOCAL_Y }, { x: 450, y: LOCAL_Y + 60 }, { x: 550, y: LOCAL_Y }], color: C.bob, dashed: true }
      ],
      links: [{ from: 'R4', to: 'L_GHOST', dashed: true }]
    }
  },
  {
    id: 13,
    group: 'Day 3: 冲突实战 (Reject)',
    role: 'You',
    title: '6. 再次推送 (Success)',
    desc: '合并成功后，本地包含了所有人的修改。现在再次 Push，成功上岸！',
    cmds: [{ user: 'You', cmd: 'git push', out: 'main -> main' }],
    anim: { from: { x: 550, y: LOCAL_Y }, to: { x: 550, y: REMOTE_Y }, icon: '🚀' },
    state: {
      commits: [
        { id: 'R4', x: 450, y: REMOTE_Y, color: C.bob, icon: '👱', msg: 'Feat B' },
        { id: 'R5', x: 550, y: REMOTE_Y, color: C.day3, icon: '🔀', msg: 'Merge', sub: 'Synced' },
        { id: 'L5', x: 550, y: LOCAL_Y, color: C.day3, icon: '🔀', msg: 'Merge' }
      ],
      branches: [
        { pts: [{ x: 150, y: REMOTE_Y }, { x: 350, y: REMOTE_Y }], color: C.history },
        { pts: [{ x: 350, y: REMOTE_Y }, { x: 450, y: REMOTE_Y }, { x: 550, y: REMOTE_Y }], color: C.day3 },
        { pts: [{ x: 150, y: LOCAL_Y }, { x: 350, y: LOCAL_Y }], color: C.history },
        { pts: [{ x: 350, y: LOCAL_Y }, { x: 550, y: LOCAL_Y }], color: C.day3 }
      ],
      links: [{ from: 'L5', to: 'R5', dashed: true }]
    }
  }
]

// Refs
const gitSvg = ref(null)
const pathsLayer = ref(null)
const nodesLayer = ref(null)
const animLayer = ref(null)
const terminalEl = ref(null)
const tooltip = ref(null)

// State
const currentStepIndex = ref(-1)
const terminalLines = ref([])
const showErrToast = ref(false)

// Tooltip state
const tooltipVisible = ref(false)
const tooltipLeft = ref('0px')
const tooltipTop = ref('0px')
const tooltipMsg = ref('')
const tooltipSub = ref('')
const tooltipColor = ref('#fff')

// Helper functions
const getRoleClass = (user) => {
  if (user === 'You') return 'role-you'
  if (user === 'Bob') return 'role-bob'
  return 'role-sys'
}

const findNode = (state, id) => {
  return state.commits.find(c => c.id === id)
}

const createSvgElement = (tag) => {
  return document.createElementNS('http://www.w3.org/2000/svg', tag)
}

const drawPath = (points, color, dashed) => {
  if (points.length < 2) return
  let d = `M ${points[0].x} ${points[0].y}`
  for (let i = 1; i < points.length; i++) {
    const p1 = points[i - 1]
    const p2 = points[i]
    const midX = (p1.x + p2.x) / 2
    d += ` C ${midX} ${p1.y}, ${midX} ${p2.y}, ${p2.x} ${p2.y}`
  }

  const path = createSvgElement('path')
  path.setAttribute('d', d)
  path.setAttribute('stroke', color)
  path.setAttribute('fill', 'none')
  path.setAttribute('stroke-width', '4')
  if (dashed) path.setAttribute('stroke-dasharray', '8,4')
  path.classList.add('branch-path')
  pathsLayer.value.appendChild(path)
}

const drawLink = (p1, p2, color, dashed, width) => {
  const d = `M ${p1.x} ${p1.y} L ${p2.x} ${p2.y}`
  const path = createSvgElement('path')
  path.setAttribute('d', d)
  path.setAttribute('stroke', color || '#4b5563')
  path.setAttribute('stroke-width', width || '1')
  if (dashed) path.setAttribute('stroke-dasharray', '4,4')
  pathsLayer.value.appendChild(path)
}

const drawNode = (c) => {
  const g = createSvgElement('g')
  g.classList.add('commit-node')
  if (c.opacity) g.style.opacity = c.opacity

  const circle = createSvgElement('circle')
  circle.setAttribute('cx', c.x)
  circle.setAttribute('cy', c.y)
  circle.setAttribute('r', 12)
  circle.setAttribute('fill', '#0d1117')
  circle.setAttribute('stroke', c.color)

  const icon = createSvgElement('text')
  icon.setAttribute('x', c.x)
  icon.setAttribute('y', c.y + 1)
  icon.classList.add('commit-avatar')
  icon.textContent = c.icon

  const lbl = createSvgElement('text')
  lbl.setAttribute('x', c.x)
  lbl.setAttribute('y', c.y + 28)
  lbl.setAttribute('text-anchor', 'middle')
  lbl.setAttribute('fill', '#8b949e')
  lbl.setAttribute('font-size', '10px')
  lbl.textContent = c.sub || ''

  g.addEventListener('mouseenter', (e) => showTooltip(e, c))
  g.addEventListener('mouseleave', hideTooltip)

  g.appendChild(circle)
  g.appendChild(icon)
  g.appendChild(lbl)
  nodesLayer.value.appendChild(g)
}

const showTooltip = (e, data) => {
  const rect = e.target.getBoundingClientRect()
  const parentRect = document.querySelector('.canvas-wrapper').getBoundingClientRect()
  tooltipMsg.value = data.msg
  tooltipSub.value = data.sub || 'Commit'
  tooltipColor.value = data.color
  tooltipLeft.value = (rect.left - parentRect.left + 10) + 'px'
  tooltipTop.value = (rect.top - parentRect.top - 10) + 'px'
  tooltipVisible.value = true
}

const hideTooltip = () => {
  tooltipVisible.value = false
}

const renderGraph = (state) => {
  pathsLayer.value.innerHTML = ''
  nodesLayer.value.innerHTML = ''
  animLayer.value.innerHTML = ''

  state.branches.forEach(br => drawPath(br.pts, br.color, br.dashed))

  if (state.links) {
    state.links.forEach(l => {
      const from = findNode(state, l.from)
      const to = findNode(state, l.to)
      if (from && to) drawLink(from, to, l.color, l.dashed, l.width)
    })
  }

  state.commits.forEach(c => drawNode(c))
}

const runAnim = (anim) => {
  const g = createSvgElement('g')
  const circle = createSvgElement('circle')
  circle.setAttribute('r', 10)
  circle.setAttribute('fill', '#fff')
  circle.classList.add('packet')

  const txt = createSvgElement('text')
  txt.textContent = anim.icon
  txt.setAttribute('font-size', '12px')
  txt.setAttribute('text-anchor', 'middle')
  txt.setAttribute('dominant-baseline', 'central')

  g.appendChild(circle)
  g.appendChild(txt)
  animLayer.value.appendChild(g)

  const start = anim.from
  const end = anim.to
  let startTimestamp = null
  const duration = 1000

  const step = (timestamp) => {
    if (!startTimestamp) startTimestamp = timestamp
    const progress = Math.min((timestamp - startTimestamp) / duration, 1)

    const currX = start.x + (end.x - start.x) * progress
    const currY = start.y + (end.y - start.y) * progress

    g.setAttribute('transform', `translate(${currX}, ${currY})`)

    if (progress < 1) {
      window.requestAnimationFrame(step)
    } else {
      g.remove()
    }
  }
  window.requestAnimationFrame(step)
}

const loadStep = (idx) => {
  if (idx === currentStepIndex.value) return
  currentStepIndex.value = idx

  const stepData = steps[idx]

  // Show/hide error toast
  showErrToast.value = !!stepData.showErr

  // Render graph
  renderGraph(stepData.state)

  // Render terminal
  terminalLines.value = stepData.cmds

  // Run animation if exists
  if (stepData.anim) {
    runAnim(stepData.anim)
  }

  // Scroll terminal to bottom
  nextTick(() => {
    if (terminalEl.value) {
      terminalEl.value.scrollTop = terminalEl.value.scrollHeight
    }
  })
}

onMounted(() => {
  loadStep(0)
})
</script>

<style scoped>
.scenario-page {
  --bg: #0d1117;
  --sidebar-bg: #010409;
  --border: #30363d;
  --text-main: #c9d1d9;
  --text-dim: #8b949e;

  /* Colors */
  --c-remote: #ea580c;
  --c-local: #3b82f6;
  --c-bob: #d29922;
  --c-day1: #238636;
  --c-day2: #a371f7;
  --c-day3: #f43f5e;
  --c-history: #424a56;
  --c-err: #f85149;

  background: var(--bg);
  color: var(--text-main);
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* --- Header --- */
.scenario-header {
  height: 60px;
  border-bottom: 1px solid var(--border);
  background: var(--sidebar-bg);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
}

.brand {
  font-weight: 700;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #fff;
}

.badge {
  font-size: 11px;
  background: #21262d;
  padding: 2px 6px;
  border-radius: 4px;
  color: #8b949e;
  margin-left: 8px;
}

.legend {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: var(--text-dim);
}

.l-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

/* --- Layout --- */
.scenario-container {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* --- Sidebar --- */
.sidebar {
  width: 320px;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  flex-shrink: 0;
}

.day-header {
  padding: 15px 20px;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text-dim);
  border-top: 1px solid var(--border);
  background: #010409;
  position: sticky;
  top: 0;
  z-index: 10;
  border-bottom: 1px solid #21262d;
}

.day-header:first-child {
  border-top: none;
}

.step-item {
  display: flex;
  gap: 12px;
  padding: 12px 20px;
  border-radius: 0;
  cursor: pointer;
  border-left: 2px solid transparent;
  border-bottom: 1px solid rgba(48, 54, 61, 0.4);
  transition: all 0.2s;
  opacity: 0.7;
}

.step-item:hover {
  background: rgba(255, 255, 255, 0.03);
  opacity: 1;
}

.step-item.active {
  background: rgba(56, 139, 253, 0.08);
  border-left-color: #3b82f6;
  opacity: 1;
}

.step-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 800;
  color: var(--text-dim);
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-title {
  font-size: 13px;
  font-weight: 600;
  color: #e6edf3;
  margin-bottom: 2px;
}

.step-desc {
  font-size: 11px;
  color: var(--text-dim);
  line-height: 1.4;
}

/* --- Main View --- */
.main-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #0d1117;
  position: relative;
  min-width: 0;
}

.env-label {
  position: absolute;
  font-size: 10px;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 1px;
  padding: 6px 10px;
  border-radius: 4px;
  z-index: 10;
}

.label-remote {
  top: 20px;
  left: 20px;
  color: var(--c-remote);
  background: rgba(234, 88, 12, 0.1);
  border: 1px solid rgba(234, 88, 12, 0.2);
}

.label-local {
  bottom: 180px;
  left: 20px;
  color: var(--c-local);
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.canvas-wrapper {
  flex: 1;
  position: relative;
  overflow: hidden;
  background-image: linear-gradient(to right, #21262d 50%, transparent 50%);
  background-size: 20px 1px;
  background-repeat: repeat-x;
  background-position: 0 45%;
}

.canvas-wrapper svg {
  width: 100%;
  height: 100%;
}

/* Nodes & Animations */
:deep(.commit-node) {
  transition: all 0.6s ease;
  cursor: pointer;
}

:deep(.commit-node circle) {
  stroke-width: 2px;
  transition: stroke 0.6s, fill 0.6s;
}

:deep(.commit-node:hover circle) {
  stroke-width: 4px;
  stroke: #fff;
}

:deep(.commit-avatar) {
  font-size: 10px;
  text-anchor: middle;
  dominant-baseline: central;
  pointer-events: none;
}

:deep(.branch-path) {
  fill: none;
  stroke-width: 3px;
  stroke-linecap: round;
  transition: all 1s ease;
  animation: drawLine 1s forwards;
}

@keyframes drawLine {
  from { stroke-dashoffset: 1000; }
  to { stroke-dashoffset: 0; }
}

:deep(.packet) {
  fill: #fff;
  filter: drop-shadow(0 0 4px rgba(255, 255, 255, 0.8));
}

/* Terminal */
.terminal {
  height: 150px;
  background: #010409;
  border-top: 1px solid var(--border);
  padding: 15px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 12px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  z-index: 20;
  flex-shrink: 0;
}

.term-line {
  margin-bottom: 6px;
  display: flex;
  gap: 10px;
  opacity: 0;
  animation: slideIn 0.3s forwards;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.term-tag {
  padding: 1px 4px;
  border-radius: 3px;
  font-size: 10px;
  font-weight: bold;
  margin-right: 5px;
  min-width: 60px;
  text-align: center;
}

.role-you {
  color: #3b82f6;
  background: rgba(59, 130, 246, 0.1);
}

.role-bob {
  color: #d29922;
  background: rgba(210, 153, 34, 0.1);
}

.role-sys {
  color: #8b949e;
  background: rgba(139, 148, 158, 0.1);
}

.term-cmd {
  color: #fff;
  font-weight: bold;
}

.term-out {
  color: var(--text-dim);
  padding-left: 20px;
  white-space: pre-wrap;
}

.term-err {
  color: var(--c-err);
  padding-left: 20px;
  font-weight: bold;
}

/* Alerts */
.err-toast {
  position: absolute;
  top: 40%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(40, 0, 0, 0.95);
  border: 1px solid var(--c-err);
  color: var(--c-err);
  padding: 15px 25px;
  border-radius: 8px;
  font-weight: bold;
  font-family: monospace;
  opacity: 0;
  pointer-events: none;
  transition: all 0.3s;
  z-index: 50;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.err-toast.show {
  opacity: 1;
  transform: translate(-50%, -60%);
}

.tooltip {
  position: absolute;
  background: rgba(30, 41, 59, 0.95);
  color: #fff;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 12px;
  pointer-events: none;
  transition: opacity 0.2s;
  transform: translate(-50%, -150%);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
  border: 1px solid var(--border);
  text-align: center;
  z-index: 100;
}

/* Responsive */
@media (max-width: 900px) {
  .scenario-container {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
    max-height: 200px;
  }

  .legend {
    display: none;
  }
}
</style>
