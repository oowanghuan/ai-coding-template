<template>
  <div class="beginning-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="container">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item>一切的开始</el-breadcrumb-item>
        </el-breadcrumb>
        <h1 class="page-title">💡 一切的开始</h1>
        <p class="page-subtitle">一场关于 AI 时代团队变革的深度对话</p>
      </div>
    </div>

    <!-- 对话内容 -->
    <div class="content-section">
      <div class="container">
        <!-- 问题部分 -->
        <div class="conversation-block question-block">
          <div class="block-header">
            <div class="speaker-tag user-tag">
              <span class="speaker-icon">🙋</span>
              <span class="speaker-name">团队负责人的困惑</span>
            </div>
          </div>
          <div class="block-content">
            <p class="main-question">
              Hi Chat，我们在开发流程中一直在探讨一个问题，就是 <strong>AI 介入之后，导致开发流程非常快</strong>（单纯指 coding 这个开发阶段），但是<strong>对于产品定义、UI、测试这些环节干扰很厉害</strong>。
            </p>
            <div class="question-detail">
              <p>职能结合起来，给一个人干？干活的人其实是 AI，现在流程是产品、设计师、前端开发分别去根据一个需求流程式指导 AI 干活然后串起来。</p>
              <p><strong>未来是一个人（这个岗位叫啥？）</strong>，根据需求把产品和 UI 和前端一起搞定。</p>
              <p>我把群组讨论也分享给你，你看怎么参加一下我们的讨论并给一些反馈。</p>
            </div>
          </div>
        </div>

        <!-- 回答部分 -->
        <div class="conversation-block answer-block">
          <div class="block-header">
            <div class="speaker-tag ai-tag">
              <span class="speaker-icon">🤖</span>
              <span class="speaker-name">ChatGPT 的深度分析</span>
            </div>
          </div>
          <div class="block-content">
            <div class="intro-text">
              <p>下面我会用<strong>"专家加入讨论的方式"</strong>，不光是总结你们群里的讨论，而是<strong>直接给出你们现在正在寻找的：未来岗位叫什么、AI 时代新的流程怎么落地、怎么拆分任务、怎么管理甲方、怎么减少 UI/测试卡点、怎么让一个人把产品/UI/前端串起来</strong>。</p>
              <p>我会非常具体，不讲空话，让你们能马上在团队里执行。</p>
            </div>

            <!-- 章节1：结构性变化 -->
            <div class="insight-section">
              <h2 class="insight-title">🧠 ① 你们正在经历的是行业级的结构性变化</h2>
              <h3 class="insight-subtitle">AI 让原本 3 个岗位（PM/UI/前端）趋向合并</h3>

              <div class="insight-content">
                <p class="highlight-text">你们群里大量讨论的本质都是这一句话：</p>
                <div class="quote-box">
                  <p><strong>AI 让"前端编码成本"从高成本 → 接近零成本。<br/>于是上游的 PM / UI / 流程 / 测试细节变成新的瓶颈。</strong></p>
                </div>

                <p>以前前端是贵的，UI 和 PM 必须拼命准备「完美输入」。<br/>现在前端不贵了，反而 PM 和 UI 太慢、太不结构化 → 卡住流程。</p>

                <div class="info-list">
                  <div class="list-title">你们讨论里所有矛盾，都来自这一点：</div>
                  <div class="info-list-item">
                    <span class="dot"></span>
                    <span class="info-text">「甲方要设计图」</span>
                  </div>
                  <div class="info-list-item">
                    <span class="dot"></span>
                    <span class="info-text">「AI 做前端快，但产品要求不够细导致测试不全」</span>
                  </div>
                  <div class="info-list-item">
                    <span class="dot"></span>
                    <span class="info-text">「UI 多、流程复杂、prompt 不够细导致 AI 输出不稳定」</span>
                  </div>
                  <div class="info-list-item">
                    <span class="dot"></span>
                    <span class="info-text">「Figma 中间层到底要不要」</span>
                  </div>
                  <div class="info-list-item">
                    <span class="dot"></span>
                    <span class="info-text">「要不要从 chat → Figma → code，还是 chat → demo」</span>
                  </div>
                  <div class="info-list-item">
                    <span class="dot"></span>
                    <span class="info-text">「到底一个人能不能把 PM + UI + 前端都做掉」</span>
                  </div>
                </div>

                <p class="note-text">这些不是你们团队独有的问题，而是所有 AI coding 团队都会经历的。</p>
              </div>
            </div>

            <!-- 章节2：新岗位定义 -->
            <div class="insight-section">
              <h2 class="insight-title">🧑‍🚀 ② 未来真正的岗位是 —— AI Product Engineer</h2>
              <h3 class="insight-subtitle">AI 产品工程师</h3>

              <div class="insight-content">
                <p>不是 PM，不是 UI，不是前端，而是：</p>

                <div class="definition-box">
                  <h4>💡 AI Product Engineer = 产品结构设计 + UI 交互 + AI 工具编排 + 代码验证 + 交付质量</h4>
                  <div class="quote-box">
                    <p><strong>一句话：把需求 → 转化成结构化 → 用 AI 自动生成 UI、组件、API、前端代码、甚至部分测试的"全链路工程师"。</strong></p>
                  </div>
                </div>

                <p>你们在群里其实已经说出这个岗位的 80% 特征：</p>
                <div class="info-list">
                  <div class="info-list-item">
                    <span class="dot"></span>
                    <span class="info-text">PM 必须能把需求拆成能被 AI 理解的结构化 plan → tasks</span>
                  </div>
                  <div class="info-list-item">
                    <span class="dot"></span>
                    <span class="info-text">UI 必须能直接用于 AI 生成 demo，而不是传统出图</span>
                  </div>
                  <div class="info-list-item">
                    <span class="dot"></span>
                    <span class="info-text">前端开发由 AI 主力完成，人负责验证、补洞、结构决策</span>
                  </div>
                  <div class="info-list-item">
                    <span class="dot"></span>
                    <span class="info-text">流程必须从 demo → code，而不是 Figma → code</span>
                  </div>
                  <div class="info-list-item">
                    <span class="dot"></span>
                    <span class="info-text">测试必须结构化，否则根本无法对 AI 验收</span>
                  </div>
                </div>

                <div class="skills-box">
                  <h4>AI Product Engineer 的"核心技能"</h4>
                  <div class="skill-grid">
                    <div class="skill-item">
                      <span class="skill-number">1</span>
                      <span class="skill-name">需求抽象能力（比 PM 更强）</span>
                    </div>
                    <div class="skill-item">
                      <span class="skill-number">2</span>
                      <span class="skill-name">交互/UI 组件的拆解能力（比 UI 设计师更懂结构）</span>
                    </div>
                    <div class="skill-item">
                      <span class="skill-number">3</span>
                      <span class="skill-name">AI prompt 工程能力（自动生成代码、UI、API）</span>
                    </div>
                    <div class="skill-item">
                      <span class="skill-number">4</span>
                      <span class="skill-name">工程架构 sense（决定组件、路由、数据结构等）</span>
                    </div>
                    <div class="skill-item">
                      <span class="skill-number">5</span>
                      <span class="skill-name">强测试意识（AI 必须靠明确的 rules 去执行）</span>
                    </div>
                  </div>
                </div>

                <p class="conclusion-text">这种人，不是传统意义上的 PM / UI / 前端 合体，而是一个"AI 时代下的新角色"。</p>

                <div class="highlight-box">
                  <h4>⭐ 岗位名称建议</h4>
                  <p><strong>AI 产品工程师（AI Product Engineer）</strong></p>
                  <p>或者</p>
                  <p><strong>AI 全链路工程师（AI Full-stack Product Engineer）</strong></p>
                </div>
              </div>
            </div>

            <!-- 章节3：新流程模型 -->
            <div class="insight-section">
              <h2 class="insight-title">🔧 ③ 新的开发流程模型</h2>
              <h3 class="insight-subtitle">你们群里讨论的最终答案，其实是这个</h3>

              <div class="insight-content">
                <div class="problem-summary">
                  <p class="summary-title">现在的流程痛点是：</p>
                  <div class="info-list">
                    <div class="info-list-item">
                      <span class="dot"></span>
                      <span class="info-text">PM → 描述不够结构化</span>
                    </div>
                    <div class="info-list-item">
                      <span class="dot"></span>
                      <span class="info-text">UI → 甲方给图，内耗严重</span>
                    </div>
                    <div class="info-list-item">
                      <span class="dot"></span>
                      <span class="info-text">前端 → AI 做得快，但依赖上游质量</span>
                    </div>
                    <div class="info-list-item">
                      <span class="dot"></span>
                      <span class="info-text">测试 → 用例不全导致反复返工</span>
                    </div>
                  </div>
                </div>

                <div class="workflow-section">
                  <h4 class="workflow-title">🔥 未来最优流程（强烈推荐你们落地）</h4>

                  <div class="workflow-step">
                    <div class="step-header">
                      <span class="step-number">1</span>
                      <h5 class="step-title">Product Spec by AI Product Engineer（结构化产品说明）</h5>
                    </div>
                    <div class="step-content">
                      <p>由 AI 产品工程师负责把需求拆成结构：</p>
                      <div class="info-list compact">
                        <div class="info-list-item">
                          <span class="dot small"></span>
                          <span class="info-text">用户流程</span>
                        </div>
                        <div class="info-list-item">
                          <span class="dot small"></span>
                          <span class="info-text">交互逻辑</span>
                        </div>
                        <div class="info-list-item">
                          <span class="dot small"></span>
                          <span class="info-text">每个步骤的输入/输出</span>
                        </div>
                        <div class="info-list-item">
                          <span class="dot small"></span>
                          <span class="info-text">组件 & UI状态</span>
                        </div>
                        <div class="info-list-item">
                          <span class="dot small"></span>
                          <span class="info-text">所有边界条件</span>
                        </div>
                        <div class="info-list-item">
                          <span class="dot small"></span>
                          <span class="info-text">错误态</span>
                        </div>
                        <div class="info-list-item">
                          <span class="dot small"></span>
                          <span class="info-text">示例数据</span>
                        </div>
                      </div>
                      <div class="quote-box small">
                        <p>这一步非常关键，相当于：<strong>写给 AI 的「结构化 prompt」</strong></p>
                      </div>
                    </div>
                  </div>

                  <div class="workflow-step">
                    <div class="step-header">
                      <span class="step-number">2</span>
                      <h5 class="step-title">Chat → Demo（直接用 AI 生成可运行 Demo）</h5>
                    </div>
                    <div class="step-content">
                      <p>跳过传统 Figma 出图。直接让 LLM 生成：</p>
                      <div class="tag-list">
                        <span class="tag">页面结构</span>
                        <span class="tag">UI 布局</span>
                        <span class="tag">样式</span>
                        <span class="tag">路由</span>
                        <span class="tag">动态交互</span>
                        <span class="tag">API 假数据</span>
                        <span class="tag">组件逻辑</span>
                      </div>
                      <p>这其实你们群里已经确认：<strong>AI coding 足够成熟，前端 demo 的成本几乎为零。</strong></p>
                      <div class="quote-box small">
                        <p>效果图 = Demo<br/>Demo = 可评审<br/>评审后直接转化为生产代码</p>
                      </div>
                    </div>
                  </div>

                  <div class="workflow-step">
                    <div class="step-header">
                      <span class="step-number">3</span>
                      <h5 class="step-title">Demo → Production Code（AI 自动升级 + 人类审核）</h5>
                    </div>
                    <div class="step-content">
                      <p>通过 MCP + AI coding：</p>
                      <div class="two-column-list">
                        <div class="column">
                          <p class="column-title">AI 负责：</p>
                          <div class="info-list compact">
                            <div class="info-list-item">
                              <span class="dot small"></span>
                              <span class="info-text">生成正式组件</span>
                            </div>
                            <div class="info-list-item">
                              <span class="dot small"></span>
                              <span class="info-text">绑定真 API</span>
                            </div>
                            <div class="info-list-item">
                              <span class="dot small"></span>
                              <span class="info-text">写 CRUD</span>
                            </div>
                            <div class="info-list-item">
                              <span class="dot small"></span>
                              <span class="info-text">接入全站路由、store、context</span>
                            </div>
                            <div class="info-list-item">
                              <span class="dot small"></span>
                              <span class="info-text">自动生成测试</span>
                            </div>
                          </div>
                        </div>
                        <div class="column">
                          <p class="column-title">人类工程师负责：</p>
                          <div class="info-list compact">
                            <div class="info-list-item">
                              <span class="dot small"></span>
                              <span class="info-text">架构检查</span>
                            </div>
                            <div class="info-list-item">
                              <span class="dot small"></span>
                              <span class="info-text">组件命名</span>
                            </div>
                            <div class="info-list-item">
                              <span class="dot small"></span>
                              <span class="info-text">复用抽象</span>
                            </div>
                            <div class="info-list-item">
                              <span class="dot small"></span>
                              <span class="info-text">分层优化</span>
                            </div>
                            <div class="info-list-item">
                              <span class="dot small"></span>
                              <span class="info-text">可读性/一致性保证</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div class="workflow-step">
                    <div class="step-header">
                      <span class="step-number">4</span>
                      <h5 class="step-title">Testing by AI + Rulebook</h5>
                    </div>
                    <div class="step-content">
                      <p>测试最大的问题：你们现在的 prompt 不够结构。</p>
                      <div class="quote-box small highlight">
                        <p><strong>测试用例不是 QA 写，是 AI 产品工程师写一本 Rulebook</strong><br/>（你们群里也反复讲到这一点：写到这个程度 AI 才能干好）</p>
                      </div>
                      <p>Rulebook 包含：</p>
                      <div class="tag-list">
                        <span class="tag">所有交互状态</span>
                        <span class="tag">成功态/失败态</span>
                        <span class="tag">输入框颜色</span>
                        <span class="tag">验证提示</span>
                        <span class="tag">禁用/可点击状态</span>
                        <span class="tag">边界条件</span>
                        <span class="tag">API 异常</span>
                        <span class="tag">用户误操作场景</span>
                      </div>
                      <p>AI 根据 Rulebook 自动跑用例。</p>
                    </div>
                  </div>

                  <div class="workflow-step">
                    <div class="step-header">
                      <span class="step-number">5</span>
                      <h5 class="step-title">QA 最终验收</h5>
                    </div>
                    <div class="step-content">
                      <p>只需检查：</p>
                      <div class="info-list compact">
                        <div class="info-list-item">
                          <span class="dot small"></span>
                          <span class="info-text">是否符合 Rulebook</span>
                        </div>
                        <div class="info-list-item">
                          <span class="dot small"></span>
                          <span class="info-text">是否符合 Demo</span>
                        </div>
                        <div class="info-list-item">
                          <span class="dot small"></span>
                          <span class="info-text">是否符合需求</span>
                        </div>
                      </div>
                      <p class="highlight-text">减少 80% QA 成本。</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 章节4：岗位合并的必然性 -->
            <div class="insight-section">
              <h2 class="insight-title">🧩 ④ 为什么 AI 时代的 PM/UI/前端必须合并？</h2>
              <h3 class="insight-subtitle">你们讨论的真实答案</h3>

              <div class="insight-content">
                <p>你们群里所有争论其实有一个核心：</p>
                <div class="quote-box">
                  <p><strong>AI coding 的速度太快，让 PM/UI 的"自然语言表达"无法满足工程生产要求。</strong></p>
                </div>

                <p>这导致：</p>
                <div class="info-list">
                  <div class="info-list-item">
                    <span class="dot"></span>
                    <span class="info-text">UI 图不一致 → 反复改</span>
                  </div>
                  <div class="info-list-item">
                    <span class="dot"></span>
                    <span class="info-text">产品文字需求太模糊 → AI 生成不稳定</span>
                  </div>
                  <div class="info-list-item">
                    <span class="dot"></span>
                    <span class="info-text">测试没写清楚 → AI 结果不完整</span>
                  </div>
                  <div class="info-list-item">
                    <span class="dot"></span>
                    <span class="info-text">甲方设计图逻辑不成熟 → 产品方要管理甲方</span>
                  </div>
                </div>

                <p>所以最终必然回到：</p>
                <div class="quote-box highlight">
                  <p><strong>所有"结构化输入"必须由同一人写完。<br/>最好不是三个部门的人，而是一个岗位。</strong></p>
                </div>

                <div class="role-transformation">
                  <h4>🎯 AI Product Engineer = 主人岗位<br/>其他角色变成辅助角色</h4>
                  <div class="role-grid">
                    <div class="role-item">
                      <span class="role-name">PM →</span>
                      <span class="role-desc">提供 business 目标（不是交互）</span>
                    </div>
                    <div class="role-item">
                      <span class="role-name">UI →</span>
                      <span class="role-desc">提供视觉风格、组件库（不是页面）</span>
                    </div>
                    <div class="role-item">
                      <span class="role-name">前端 →</span>
                      <span class="role-desc">做工程性 review（不是大量 coding）</span>
                    </div>
                    <div class="role-item">
                      <span class="role-name">测试 →</span>
                      <span class="role-desc">管规则（不是大量手工点点点）</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 章节5：10个关键问题的解答 -->
            <div class="insight-section">
              <h2 class="insight-title">🧨 ⑤ 给你们团队当前争议 10 个关键点的"官方解答"</h2>

              <div class="insight-content">
                <p>根据你们微信群的对话，给出清晰判断：</p>

                <div class="qa-list">
                  <div class="qa-item">
                    <div class="question">
                      <span class="q-mark">Q1</span>
                      <span class="q-text">Chat → Demo > Figma → Code？</span>
                    </div>
                    <div class="answer">
                      <span class="a-mark">A</span>
                      <span class="a-text">对，Figma 原型层是多余的，会被 AI 时代淘汰。</span>
                    </div>
                  </div>

                  <div class="qa-item">
                    <div class="question">
                      <span class="q-mark">Q2</span>
                      <span class="q-text">后端管理系统 demo 直接出 UI 是正确方向？</span>
                    </div>
                    <div class="answer">
                      <span class="a-mark">A</span>
                      <span class="a-text">完全正确，是 AI coding 的核心优势。</span>
                    </div>
                  </div>

                  <div class="qa-item">
                    <div class="question">
                      <span class="q-mark">Q3</span>
                      <span class="q-text">甲方 insist 设计图，怎么办？</span>
                    </div>
                    <div class="answer">
                      <span class="a-mark">A</span>
                      <span class="a-text">你们的猜测是对的：<strong>你们要 manage 甲方</strong>。Demo 给得更快、更准确，甲方自然跟着你们走。</span>
                    </div>
                  </div>

                  <div class="qa-item">
                    <div class="question">
                      <span class="q-mark">Q4</span>
                      <span class="q-text">产品逻辑不够细导致测试不全？</span>
                    </div>
                    <div class="answer">
                      <span class="a-mark">A</span>
                      <span class="a-text">必然。<strong>AI coding 需要结构化需求，不是模糊文本。</strong>这是流程痛点，不是技术问题。</span>
                    </div>
                  </div>

                  <div class="qa-item">
                    <div class="question">
                      <span class="q-mark">Q5</span>
                      <span class="q-text">那这细节到底谁写？</span>
                    </div>
                    <div class="answer">
                      <span class="a-mark">A</span>
                      <span class="a-text">AI 产品工程师。</span>
                    </div>
                  </div>

                  <div class="qa-item">
                    <div class="question">
                      <span class="q-mark">Q6</span>
                      <span class="q-text">现在你们产品/设计写得不够细，是开发慢还是需求不够细？</span>
                    </div>
                    <div class="answer">
                      <span class="a-mark">A</span>
                      <span class="a-text">是需求不够结构化，不是开发不够用。</span>
                    </div>
                  </div>

                  <div class="qa-item">
                    <div class="question">
                      <span class="q-mark">Q7</span>
                      <span class="q-text">那怎么写细？</span>
                    </div>
                    <div class="answer">
                      <span class="a-mark">A</span>
                      <span class="a-text">写 Rulebook（交互规则），写到能喂 AI。</span>
                    </div>
                  </div>

                  <div class="qa-item">
                    <div class="question">
                      <span class="q-mark">Q8</span>
                      <span class="q-text">一个 UI 组件的 input、状态、错误态都要写？</span>
                    </div>
                    <div class="answer">
                      <span class="a-mark">A</span>
                      <span class="a-text">是，这是 AI coding 的核心输入。</span>
                    </div>
                  </div>

                  <div class="qa-item">
                    <div class="question">
                      <span class="q-mark">Q9</span>
                      <span class="q-text">AI 不是熟手怎么办？</span>
                    </div>
                    <div class="answer">
                      <span class="a-mark">A</span>
                      <span class="a-text">你说的比喻很好："<strong>AI 是生瓜蛋子，不是熟练工，必须教。</strong>"对，AI 不是凭常识写代码，是靠结构化指令。</span>
                    </div>
                  </div>

                  <div class="qa-item">
                    <div class="question">
                      <span class="q-mark">Q10</span>
                      <span class="q-text">需要把 PM/UI/前端合到一个角色吗？</span>
                    </div>
                    <div class="answer">
                      <span class="a-mark">A</span>
                      <span class="a-text">是的，这就是 AI Product Engineer。</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 最终总结 -->
            <div class="insight-section final-summary">
              <h2 class="insight-title">🚀 ⑥ 最终总结</h2>

              <div class="big-quote-box">
                <p class="big-quote-text">
                  AI coding 时代，真正的瓶颈不再是写代码。<br/>
                  瓶颈变成：<strong>谁能把需求"结构化、规格化、可执行化"</strong>。
                </p>
                <p class="big-quote-conclusion">
                  未来最关键的岗位，是 <strong>AI Product Engineer</strong>。
                </p>
              </div>

              <p class="closing-text">你们现在正好站在这个岗位诞生的时间点。</p>
            </div>

            <!-- 后续输出 -->
            <div class="next-steps-section">
              <h3 class="next-title">如果你愿意，我可以继续输出</h3>
              <div class="next-grid">
                <div class="next-item">
                  <span class="next-icon">✅</span>
                  <p class="next-text">一个完整岗位 JD：AI 产品工程师（行业最前沿版本）</p>
                </div>
                <div class="next-item">
                  <span class="next-icon">✅</span>
                  <p class="next-text">一套新流程 SOP：Chat → Demo → Production（你们团队可以直接执行）</p>
                </div>
                <div class="next-item">
                  <span class="next-icon">✅</span>
                  <p class="next-text">一个结构化 Rulebook 模版（输入给 AI 的黄金格式）</p>
                </div>
                <div class="next-item">
                  <span class="next-icon">✅</span>
                  <p class="next-text">一个训练你团队的清单：怎么从 PM/UI/前端转型为 AI Product Engineer</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部导航 -->
        <div class="bottom-navigation">
          <el-button type="primary" size="large" @click="goToNextPage">
            继续探索：为什么要变
            <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ArrowRight } from '@element-plus/icons-vue'

const router = useRouter()

const goToNextPage = () => {
  router.push('/why-change')
}
</script>

<style scoped>
.beginning-page {
  min-height: 100%;
  background: var(--color-bg-page);
}

/* ========== 页面头部 ========== */
.page-header {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  padding: var(--spacing-xl) 0;
  margin-bottom: var(--spacing-xxl);
}

.page-title {
  font-size: 36px;
  font-weight: var(--font-weight-bold);
  margin: var(--spacing-md) 0 var(--spacing-sm);
  line-height: 1.2;
}

.page-subtitle {
  font-size: var(--font-size-lg);
  opacity: 0.95;
  margin: 0;
}

/* ========== 对话块 ========== */
.conversation-block {
  margin-bottom: var(--spacing-xxl);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
}

.block-header {
  padding: var(--spacing-lg) var(--spacing-xl);
}

.speaker-tag {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: 20px;
  font-weight: var(--font-weight-medium);
  font-size: var(--font-size-md);
}

.user-tag {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.ai-tag {
  background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  color: white;
}

.speaker-icon {
  font-size: 20px;
  line-height: 1;
}

.speaker-name {
  font-size: 15px;
}

.block-content {
  padding: var(--spacing-xl);
  background: white;
  border: 1px solid var(--color-border-light);
  border-radius: 0 0 var(--border-radius-lg) var(--border-radius-lg);
}

/* 问题部分 */
.question-block .block-header {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.1) 100%);
}

.main-question {
  font-size: 16px;
  line-height: 1.8;
  color: #111827;
  margin-bottom: var(--spacing-lg);
}

.question-detail p {
  font-size: 15px;
  line-height: 1.7;
  color: #374151;
  margin-bottom: var(--spacing-md);
}

/* 回答部分 */
.answer-block .block-header {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(124, 58, 237, 0.1) 100%);
}

.intro-text {
  margin-bottom: var(--spacing-xxl);
  padding: var(--spacing-lg);
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.05) 0%, rgba(124, 58, 237, 0.05) 100%);
  border-left: 4px solid #8b5cf6;
  border-radius: var(--border-radius-base);
}

.intro-text p {
  font-size: 15px;
  line-height: 1.8;
  color: #374151;
  margin-bottom: var(--spacing-sm);
}

.intro-text p:last-child {
  margin-bottom: 0;
}

/* ========== 洞察章节 ========== */
.insight-section {
  margin-bottom: var(--spacing-xxl);
  padding-bottom: var(--spacing-xxl);
  border-bottom: 1px solid var(--color-border-light);
}

.insight-section:last-of-type {
  border-bottom: none;
}

.insight-title {
  font-size: 24px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 var(--spacing-sm);
  line-height: 1.3;
}

.insight-subtitle {
  font-size: 16px;
  font-weight: 500;
  color: #6b7280;
  margin: 0 0 var(--spacing-lg);
  line-height: 1.5;
}

.insight-content {
  font-size: 15px;
  line-height: 1.7;
  color: #374151;
}

.insight-content > p {
  margin-bottom: var(--spacing-md);
}

.highlight-text {
  font-weight: 600;
  color: #111827;
}

.note-text {
  font-style: italic;
  color: #6b7280;
}

.conclusion-text {
  margin-top: var(--spacing-lg);
  font-size: 15px;
  color: #374151;
}

/* ========== 引用框 ========== */
.quote-box {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(79, 70, 229, 0.08) 100%);
  border-left: 4px solid #6366f1;
  padding: var(--spacing-lg);
  margin: var(--spacing-lg) 0;
  border-radius: var(--border-radius-base);
}

.quote-box p {
  font-size: 15px;
  line-height: 1.8;
  color: #1e293b;
  margin: 0;
}

.quote-box.small {
  padding: var(--spacing-md);
  margin: var(--spacing-md) 0;
}

.quote-box.small p {
  font-size: 14px;
}

.quote-box.highlight {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.1) 100%);
  border-left-color: #f59e0b;
}

/* ========== 信息列表 ========== */
.info-list {
  margin: var(--spacing-lg) 0;
}

.list-title {
  font-size: 15px;
  font-weight: 600;
  color: #111827;
  margin-bottom: var(--spacing-md);
}

.info-list-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 12px;
  line-height: 1.6;
}

.info-list-item .dot {
  margin-top: 6px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #667eea;
  flex-shrink: 0;
}

.info-list-item .dot.small {
  width: 6px;
  height: 6px;
  margin-top: 7px;
}

.info-list-item .info-text {
  flex: 1;
  font-size: 14px;
  color: #374151;
}

.info-list.compact .info-list-item {
  margin-bottom: 8px;
}

.info-list.compact .info-text {
  font-size: 13px;
}

/* ========== 定义框 ========== */
.definition-box {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(5, 150, 105, 0.08) 100%);
  border: 2px solid #10b981;
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-xl);
  margin: var(--spacing-lg) 0;
}

.definition-box h4 {
  font-size: 18px;
  font-weight: 600;
  color: #065f46;
  margin: 0 0 var(--spacing-md);
  line-height: 1.4;
}

/* ========== 技能框 ========== */
.skills-box {
  background: white;
  border: 1px solid var(--color-border-light);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-xl);
  margin: var(--spacing-lg) 0;
}

.skills-box h4 {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 var(--spacing-lg);
}

.skill-grid {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.skill-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(79, 70, 229, 0.05) 100%);
  border-radius: var(--border-radius-base);
}

.skill-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #6366f1;
  color: white;
  border-radius: 50%;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.skill-name {
  font-size: 14px;
  color: #374151;
  line-height: 1.5;
}

/* ========== 高亮框 ========== */
.highlight-box {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.1) 100%);
  border: 2px solid #f59e0b;
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-xl);
  margin: var(--spacing-lg) 0;
}

.highlight-box h4 {
  font-size: 16px;
  font-weight: 600;
  color: #92400e;
  margin: 0 0 var(--spacing-md);
}

.highlight-box p {
  font-size: 15px;
  line-height: 1.7;
  color: #451a03;
  margin: var(--spacing-xs) 0;
}

/* ========== 问题总结 ========== */
.problem-summary {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.05) 0%, rgba(220, 38, 38, 0.05) 100%);
  border-left: 4px solid #ef4444;
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-base);
  margin-bottom: var(--spacing-xl);
}

.summary-title {
  font-size: 15px;
  font-weight: 600;
  color: #991b1b;
  margin-bottom: var(--spacing-md);
}

/* ========== 工作流程 ========== */
.workflow-section {
  margin-top: var(--spacing-xl);
}

.workflow-title {
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  margin: 0 0 var(--spacing-xl);
  padding: var(--spacing-md);
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.1) 100%);
  border-left: 4px solid #f59e0b;
  border-radius: var(--border-radius-base);
}

.workflow-step {
  background: white;
  border: 1px solid var(--color-border-light);
  border-radius: var(--border-radius-lg);
  margin-bottom: var(--spacing-lg);
  overflow: hidden;
}

.step-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-lg) var(--spacing-xl);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(79, 70, 229, 0.08) 100%);
}

.step-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: #6366f1;
  color: white;
  border-radius: 50%;
  font-weight: 600;
  font-size: 18px;
  flex-shrink: 0;
}

.step-title {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin: 0;
  line-height: 1.4;
}

.step-content {
  padding: var(--spacing-xl);
}

.step-content > p {
  font-size: 14px;
  line-height: 1.7;
  color: #374151;
  margin-bottom: var(--spacing-md);
}

/* ========== 标签列表 ========== */
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
  margin: var(--spacing-md) 0;
}

.tag {
  display: inline-block;
  padding: var(--spacing-xs) var(--spacing-md);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(79, 70, 229, 0.1) 100%);
  color: #4f46e5;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 500;
}

/* ========== 两列列表 ========== */
.two-column-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-xl);
  margin: var(--spacing-lg) 0;
}

.column-title {
  font-size: 14px;
  font-weight: 600;
  color: #111827;
  margin-bottom: var(--spacing-md);
}

/* ========== 角色转换 ========== */
.role-transformation {
  background: white;
  border: 2px solid #10b981;
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-xl);
  margin: var(--spacing-lg) 0;
}

.role-transformation h4 {
  font-size: 18px;
  font-weight: 600;
  color: #065f46;
  margin: 0 0 var(--spacing-lg);
  line-height: 1.4;
  text-align: center;
}

.role-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}

.role-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(5, 150, 105, 0.05) 100%);
  border-radius: var(--border-radius-base);
}

.role-name {
  font-size: 14px;
  font-weight: 600;
  color: #065f46;
  min-width: 60px;
}

.role-desc {
  font-size: 13px;
  color: #047857;
  line-height: 1.5;
}

/* ========== Q&A 列表 ========== */
.qa-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  margin-top: var(--spacing-lg);
}

.qa-item {
  background: white;
  border: 1px solid var(--color-border-light);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
}

.question {
  display: flex;
  gap: var(--spacing-md);
  align-items: flex-start;
  margin-bottom: var(--spacing-md);
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--color-border-light);
}

.q-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 36px;
  height: 28px;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
  border-radius: 6px;
  font-weight: 600;
  font-size: 12px;
  flex-shrink: 0;
  padding: 0 var(--spacing-sm);
}

.q-text {
  font-size: 15px;
  font-weight: 600;
  color: #111827;
  line-height: 1.6;
}

.answer {
  display: flex;
  gap: var(--spacing-md);
  align-items: flex-start;
}

.a-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border-radius: 6px;
  font-weight: 600;
  font-size: 12px;
  flex-shrink: 0;
}

.a-text {
  font-size: 14px;
  color: #374151;
  line-height: 1.7;
}

/* ========== 最终总结 ========== */
.final-summary {
  margin-top: var(--spacing-xxl);
  padding-top: var(--spacing-xxl);
  border-top: 2px solid var(--color-border-light);
}

.big-quote-box {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(79, 70, 229, 0.1) 100%);
  border: 3px solid #6366f1;
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-xxl);
  margin: var(--spacing-xl) 0;
  text-align: center;
}

.big-quote-text {
  font-size: 18px;
  line-height: 1.8;
  color: #1e293b;
  margin: 0 0 var(--spacing-lg);
}

.big-quote-conclusion {
  font-size: 20px;
  font-weight: 600;
  color: #4f46e5;
  margin: 0;
  line-height: 1.5;
}

.closing-text {
  font-size: 16px;
  text-align: center;
  color: #6b7280;
  font-style: italic;
  margin: var(--spacing-xl) 0;
}

/* ========== 后续步骤 ========== */
.next-steps-section {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(5, 150, 105, 0.05) 100%);
  border: 1px solid #10b981;
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-xl);
  margin-top: var(--spacing-xxl);
}

.next-title {
  font-size: 18px;
  font-weight: 600;
  color: #065f46;
  margin: 0 0 var(--spacing-lg);
  text-align: center;
}

.next-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}

.next-item {
  display: flex;
  gap: var(--spacing-md);
  align-items: flex-start;
  padding: var(--spacing-md);
  background: white;
  border-radius: var(--border-radius-base);
}

.next-icon {
  font-size: 20px;
  line-height: 1;
  flex-shrink: 0;
}

.next-text {
  font-size: 14px;
  color: #374151;
  line-height: 1.6;
  margin: 0;
}

/* ========== 底部导航 ========== */
.bottom-navigation {
  margin-top: var(--spacing-xxl);
  padding-top: var(--spacing-xxl);
  border-top: 1px solid var(--color-border-light);
  text-align: center;
}

/* ========== 响应式 ========== */
@media (max-width: 768px) {
  .page-header {
    padding: var(--spacing-lg) 0;
  }

  .page-title {
    font-size: 24px;
  }

  .page-subtitle {
    font-size: var(--font-size-base);
  }

  .two-column-list {
    grid-template-columns: 1fr;
  }

  .role-grid {
    grid-template-columns: 1fr;
  }

  .next-grid {
    grid-template-columns: 1fr;
  }

  .insight-title {
    font-size: 20px;
  }

  .block-content {
    padding: var(--spacing-lg);
  }

  .step-content {
    padding: var(--spacing-lg);
  }
}
</style>
