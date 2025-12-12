import { reactive, computed } from 'vue'

// Mock user database - stored in localStorage
const USERS_KEY = 'ai_coding_org_users'
const CURRENT_USER_KEY = 'ai_coding_org_current_user'

// Initialize mock users if not exists
const initMockUsers = () => {
  const existingUsers = localStorage.getItem(USERS_KEY)
  if (!existingUsers) {
    // Pre-populate with a demo user
    const defaultUsers = [
      { id: 1, username: 'demo', password: 'demo123', email: 'demo@example.com', createdAt: new Date().toISOString() }
    ]
    localStorage.setItem(USERS_KEY, JSON.stringify(defaultUsers))
  }
}

// Get all users from localStorage
const getUsers = () => {
  initMockUsers()
  return JSON.parse(localStorage.getItem(USERS_KEY) || '[]')
}

// Save users to localStorage
const saveUsers = (users) => {
  localStorage.setItem(USERS_KEY, JSON.stringify(users))
}

// Auth state
const state = reactive({
  user: JSON.parse(localStorage.getItem(CURRENT_USER_KEY) || 'null'),
  loading: false,
  error: null
})

// Computed properties
const isAuthenticated = computed(() => !!state.user)
const currentUser = computed(() => state.user)

// Actions
const login = (username, password) => {
  state.loading = true
  state.error = null

  return new Promise((resolve, reject) => {
    // Simulate network delay
    setTimeout(() => {
      const users = getUsers()
      const user = users.find(u => u.username === username && u.password === password)

      if (user) {
        const { password: _, ...safeUser } = user
        state.user = safeUser
        localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(safeUser))
        state.loading = false
        resolve(safeUser)
      } else {
        state.loading = false
        state.error = '用户名或密码错误'
        reject(new Error('用户名或密码错误'))
      }
    }, 500)
  })
}

const register = (username, password, email) => {
  state.loading = true
  state.error = null

  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const users = getUsers()

      // Check if username exists
      if (users.find(u => u.username === username)) {
        state.loading = false
        state.error = '用户名已存在'
        reject(new Error('用户名已存在'))
        return
      }

      // Check if email exists
      if (users.find(u => u.email === email)) {
        state.loading = false
        state.error = '邮箱已被注册'
        reject(new Error('邮箱已被注册'))
        return
      }

      // Create new user
      const newUser = {
        id: Date.now(),
        username,
        password,
        email,
        createdAt: new Date().toISOString()
      }

      users.push(newUser)
      saveUsers(users)

      // Auto login after registration
      const { password: _, ...safeUser } = newUser
      state.user = safeUser
      localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(safeUser))
      state.loading = false
      resolve(safeUser)
    }, 500)
  })
}

const logout = () => {
  state.user = null
  localStorage.removeItem(CURRENT_USER_KEY)
}

const clearError = () => {
  state.error = null
}

export const useAuth = () => ({
  state,
  isAuthenticated,
  currentUser,
  login,
  register,
  logout,
  clearError
})
