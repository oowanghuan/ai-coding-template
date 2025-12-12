import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import RoleDetail from '../views/RoleDetail.vue'
import TheBeginning from '../views/TheBeginning.vue'
import WhyChange from '../views/WhyChange.vue'
import TeamStructure from '../views/TeamStructure.vue'
import RolesOverview from '../views/RolesOverview.vue'
import WorkflowGuide from '../views/WorkflowGuide.vue'
import Resources from '../views/Resources.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'

// Deep Dive Pages
import AiPeHub from '../views/deep-dive/AiPeHub.vue'
import AiPeCapabilities from '../views/deep-dive/AiPeCapabilities.vue'
import AiPeExamples from '../views/deep-dive/AiPeExamples.vue'
import AiPeSpecTemplate from '../views/deep-dive/AiPeSpecTemplate.vue'
import AiPeTraining from '../views/deep-dive/AiPeTraining.vue'
import AiSpecGeneration from '../views/deep-dive/AiSpecGeneration.vue'
import ArchitectKickoff from '../views/deep-dive/ArchitectKickoff.vue'
import UiConsistency from '../views/deep-dive/UiConsistency.vue'

// GitHub Section Pages
import GitHubConcepts from '../views/github/GitHubConcepts.vue'
import GitHubMisconceptions from '../views/github/GitHubMisconceptions.vue'
import GitHubSimulator from '../views/github/GitHubSimulator.vue'
import GitHubScenario from '../views/github/GitHubScenario.vue'
import GitHubRoutine from '../views/github/GitHubRoutine.vue'

// Project Dashboard Pages
import ProjectDashboard from '../views/dashboard/ProjectDashboard.vue'
import FeatureWorkbench from '../views/dashboard/FeatureWorkbench.vue'

// Pitfall Sharing Page
import PitfallSharing from '../views/PitfallSharing.vue'

// Panorama Guide Page
import PanoramaGuide from '../views/PanoramaGuide.vue'

// Auth store
import { useAuth } from '../stores/auth'

const routes = [
  // Auth routes (public)
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false, isAuthPage: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresAuth: false, isAuthPage: true }
  },
  // Protected routes
  {
    path: '/',
    name: 'Home',
    component: PanoramaGuide,
    meta: { requiresAuth: true }
  },
  {
    path: '/role/:id',
    name: 'RoleDetail',
    component: RoleDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/the-beginning',
    name: 'TheBeginning',
    component: TheBeginning,
    meta: { requiresAuth: true }
  },
  {
    path: '/why-change',
    name: 'WhyChange',
    component: WhyChange,
    meta: { requiresAuth: true }
  },
  {
    path: '/team-structure',
    name: 'TeamStructure',
    component: TeamStructure,
    meta: { requiresAuth: true }
  },
  {
    path: '/roles-overview',
    name: 'RolesOverview',
    component: RolesOverview,
    meta: { requiresAuth: true }
  },
  {
    path: '/workflow-guide',
    name: 'WorkflowGuide',
    component: WorkflowGuide,
    meta: { requiresAuth: true }
  },
  {
    path: '/resources',
    name: 'Resources',
    component: Resources,
    meta: { requiresAuth: true }
  },
  // Pitfall Sharing Route
  {
    path: '/pitfall-sharing',
    name: 'PitfallSharing',
    component: PitfallSharing,
    meta: { requiresAuth: true }
  },
  // Panorama Guide Route
  {
    path: '/guide',
    name: 'PanoramaGuide',
    component: PanoramaGuide,
    meta: { requiresAuth: true }
  },
  // Deep Dive Routes
  {
    path: '/deep-dive/ai-pe',
    name: 'AiPeHub',
    component: AiPeHub,
    meta: { requiresAuth: true }
  },
  {
    path: '/deep-dive/ai-pe-capabilities',
    name: 'AiPeCapabilities',
    component: AiPeCapabilities,
    meta: { requiresAuth: true }
  },
  {
    path: '/deep-dive/ai-pe-examples',
    name: 'AiPeExamples',
    component: AiPeExamples,
    meta: { requiresAuth: true }
  },
  {
    path: '/deep-dive/ai-pe-spec-template',
    name: 'AiPeSpecTemplate',
    component: AiPeSpecTemplate,
    meta: { requiresAuth: true }
  },
  {
    path: '/deep-dive/ai-pe-training',
    name: 'AiPeTraining',
    component: AiPeTraining,
    meta: { requiresAuth: true }
  },
  {
    path: '/deep-dive/ai-spec-generation',
    name: 'AiSpecGeneration',
    component: AiSpecGeneration,
    meta: { requiresAuth: true }
  },
  {
    path: '/deep-dive/architect-kickoff',
    name: 'ArchitectKickoff',
    component: ArchitectKickoff,
    meta: { requiresAuth: true }
  },
  {
    path: '/ui-consistency',
    name: 'UiConsistency',
    component: UiConsistency,
    meta: { requiresAuth: true }
  },
  // GitHub Section Routes
  {
    path: '/github',
    redirect: '/github/concepts'
  },
  {
    path: '/github/concepts',
    name: 'GitHubConcepts',
    component: GitHubConcepts,
    meta: { requiresAuth: true }
  },
  {
    path: '/github/misconceptions',
    name: 'GitHubMisconceptions',
    component: GitHubMisconceptions,
    meta: { requiresAuth: true }
  },
  {
    path: '/github/simulator',
    name: 'GitHubSimulator',
    component: GitHubSimulator,
    meta: { requiresAuth: true }
  },
  {
    path: '/github/scenario',
    name: 'GitHubScenario',
    component: GitHubScenario,
    meta: { requiresAuth: true }
  },
  {
    path: '/github/routine',
    name: 'GitHubRoutine',
    component: GitHubRoutine,
    meta: { requiresAuth: true }
  },
  // Project Dashboard Routes
  {
    path: '/project-dashboard',
    name: 'ProjectDashboard',
    component: ProjectDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/project-dashboard/:featureId',
    name: 'FeatureWorkbench',
    component: FeatureWorkbench,
    meta: { requiresAuth: true }
  },
  {
    path: '/project-dashboard/:featureId/:phaseId',
    name: 'FeatureWorkbenchPhase',
    component: FeatureWorkbench,
    meta: { requiresAuth: true }
  },
  // 工作流工作台 - 简化版人机协作视图
  {
    path: '/workflow',
    name: 'Workflow',
    component: FeatureWorkbench,
    meta: { requiresAuth: true }
  },
  {
    path: '/workflow/:phaseId',
    name: 'WorkflowPhase',
    component: FeatureWorkbench,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else if (to.hash) {
      return {
        el: to.hash,
        behavior: 'smooth'
      }
    } else {
      return { top: 0 }
    }
  }
})

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
  const auth = useAuth()
  const requiresAuth = to.meta.requiresAuth
  const isAuthPage = to.meta.isAuthPage

  if (requiresAuth && !auth.isAuthenticated.value) {
    // Redirect to login with the intended destination
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (isAuthPage && auth.isAuthenticated.value) {
    // If already logged in, redirect away from auth pages
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
