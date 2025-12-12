<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <div class="logo">
          <span class="logo-icon">🚀</span>
          <span class="logo-text">AI 时代团队转型蓝图</span>
        </div>
        <h1>登录</h1>
        <p class="subtitle">请登录以访问完整内容</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @submit.prevent="handleSubmit"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            prefix-icon="User"
            placeholder="请输入用户名"
            size="large"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            prefix-icon="Lock"
            placeholder="请输入密码"
            size="large"
            show-password
            @keyup.enter="handleSubmit"
          />
        </el-form-item>

        <el-alert
          v-if="auth.state.error"
          :title="auth.state.error"
          type="error"
          show-icon
          :closable="true"
          @close="auth.clearError"
          style="margin-bottom: 20px;"
        />

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="auth.state.loading"
            @click="handleSubmit"
            style="width: 100%;"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <p>还没有账号？ <router-link to="/register">立即注册</router-link></p>
      </div>

      <div class="demo-hint">
        <el-divider>演示账号</el-divider>
        <p>用户名: <code>demo</code> / 密码: <code>demo123</code></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '../stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const auth = useAuth()
const formRef = ref(null)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await auth.login(form.username, form.password)
        ElMessage.success('登录成功！')
        // Redirect to intended page or home
        const redirect = route.query.redirect || '/'
        router.push(redirect)
      } catch (error) {
        // Error is handled by auth store
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 24px;
}

.logo-icon {
  font-size: 32px;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.login-header h1 {
  font-size: 28px;
  color: #333;
  margin: 0 0 8px 0;
}

.subtitle {
  color: #666;
  margin: 0;
}

.login-footer {
  text-align: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #eee;
}

.login-footer p {
  color: #666;
  margin: 0;
}

.login-footer a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.login-footer a:hover {
  text-decoration: underline;
}

.demo-hint {
  margin-top: 20px;
  text-align: center;
}

.demo-hint p {
  color: #999;
  font-size: 14px;
  margin: 0;
}

.demo-hint code {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  color: #667eea;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #333;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
}
</style>
