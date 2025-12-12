export const ROLES = {
  'ai-pe': {
    id: 'ai-pe',
    icon: '⭐',
    title: 'AI 产品工程师',
    subtitle: 'AI Product Engineer, AI PE',
    tagline: '把「需求/UI → Spec → Demo → 测试场景」串成闭环的人',
    badges: ['模块级Owner', '需求工程化', 'Spec驱动'],
    color: '#667eea',
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    deepLink: '/deep-dive/ai-pe',
    deepTitle: 'AI PE 深入专题：核心能力、实战案例、模板库'
  },
  'architect': {
    id: 'architect',
    icon: '🏗️',
    title: '系统架构师',
    subtitle: 'Software Architect',
    tagline: '负责定义系统的「技术结构和统一规范」，让所有模块、所有角色（包括 AI）都在同一套技术规则下工作',
    badges: ['系统结构设计', '技术规范', 'AI使用规则'],
    color: '#1e3c72',
    gradient: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)',
    deepLink: '/deep-dive/architect-kickoff',
    deepTitle: '架构师 Kickoff 指南：项目启动规范体系'
  },
  'ui-designer': {
    id: 'ui-designer',
    icon: '🎨',
    title: 'UI 规则设计师',
    subtitle: 'Design System Owner',
    tagline: '不画单个界面，而是设计一套「可被 AI 和开发执行」的 UI 规则系统',
    badges: ['Design System', 'Design Tokens', 'UI Prompt规则'],
    color: '#f093fb',
    gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    deepLink: '/ui-consistency',
    deepTitle: 'UI 一致性规范与结构化 Prompt 模板'
  },
  'backend': {
    id: 'backend',
    icon: '⚙️',
    title: '后端工程师',
    subtitle: 'Backend Engineer',
    tagline: '将 Spec 中定义的行为，落地为稳定可靠、可观测的后端系统',
    badges: ['API实现', '数据模型', '可观测性'],
    color: '#11998e',
    gradient: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
    deepLink: '#',
    deepTitle: '后端工程师详细内容（即将推出）'
  },
  'qa': {
    id: 'qa',
    icon: '🔍',
    title: 'AI QA',
    subtitle: 'Rulebook QA',
    tagline: '从「手工执行用例的人」升级为「测试规则工程师」',
    badges: ['Rulebook设计', '自动化测试', '规则驱动'],
    color: '#ff9800',
    gradient: 'linear-gradient(135deg, #ff9800 0%, #ff5722 100%)',
    deepLink: '#',
    deepTitle: 'Rulebook Testing详解（即将推出）'
  },
  'pm': {
    id: 'pm',
    icon: '🎬',
    title: '项目经理 / Producer',
    subtitle: 'Project Manager',
    tagline: '基于「业务目标 + 架构方案」，安排"谁在什么时候把什么东西交付出来"，并持续管理依赖、风险和资源',
    badges: ['节奏与交付', '任务拆解', '风险管理'],
    color: '#06beb6',
    gradient: 'linear-gradient(135deg, #06beb6 0%, #48b1bf 100%)',
    deepLink: '#',
    deepTitle: '项目管理详细内容（即将推出）'
  }
}

export const getRoleById = (id) => ROLES[id]

export const getAllRoles = () => Object.values(ROLES)
