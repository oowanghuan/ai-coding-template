# ui_demo - 生成 UI Demo

## 能力描述

根据 `21_UI_FLOW_SPEC.md` 和项目的 UI System 规范，自动生成可运行的 Vue 3 Demo 组件，用于快速验证 UI 设计。

## 输入

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| feature | string | 是 | 功能模块名称 |
| page | string | 否 | 指定页面/组件名，不指定则生成所有 |
| style | string | 否 | 样式方案：`element-plus`（默认）, `naive-ui`, `custom` |

## 输出

- `playgrounds/{feature}/Demo.vue` - 主 Demo 组件
- `playgrounds/{feature}/components/*.vue` - 子组件（如需）
- `playgrounds/{feature}/mock/api.js` - Mock API（调用 `mock_api_generator`）

## 执行步骤

### 1. 读取规格文档

```
读取：
- docs/{feature}/21_UI_FLOW_SPEC.md - UI 流程规格
- docs/_system/_ui_system/* - 项目 UI System 规范（如有）
```

### 2. 解析 UI 规格

从 `21_UI_FLOW_SPEC.md` 提取：

```yaml
pages:
  - name: LoginPage
    components:
      - type: form
        fields:
          - name: email
            type: input
            validation: required|email
          - name: password
            type: password
            validation: required|min:8
    actions:
      - trigger: submit
        handler: login()
    states:
      - loading
      - error
      - success
```

### 3. 应用 UI System 规范

读取项目级 UI 规范：
- 颜色变量
- 间距系统
- 组件规范
- 响应式断点

### 4. 生成 Demo 代码

#### 4.1 主组件 Demo.vue

```vue
<template>
  <div class="demo-container">
    <h1>{{ feature }} Demo</h1>

    <!-- 页面切换 -->
    <el-tabs v-model="activeTab">
      <el-tab-pane
        v-for="page in pages"
        :key="page.name"
        :label="page.label"
        :name="page.name"
      >
        <component :is="page.component" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
// 导入各页面组件
import LoginPage from './components/LoginPage.vue'
// ...

const activeTab = ref('LoginPage')
const pages = [
  { name: 'LoginPage', label: '登录', component: LoginPage },
  // ...
]
</script>

<style scoped>
.demo-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}
</style>
```

#### 4.2 页面组件

```vue
<!-- playgrounds/{feature}/components/LoginPage.vue -->
<template>
  <div class="login-page">
    <el-card class="login-card">
      <template #header>
        <h2>用户登录</h2>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @submit.prevent="handleLogin"
      >
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="form.email"
            type="email"
            placeholder="请输入邮箱"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            native-type="submit"
            :loading="loading"
            class="login-btn"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 状态提示 -->
      <el-alert
        v-if="error"
        :title="error"
        type="error"
        show-icon
        closable
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { mockLogin } from '../mock/api'

const formRef = ref()
const loading = ref(false)
const error = ref('')

const form = reactive({
  email: '',
  password: ''
})

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码至少 8 个字符', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  try {
    await formRef.value?.validate()
    loading.value = true
    error.value = ''

    const result = await mockLogin(form)
    console.log('登录成功', result)
    // 处理成功状态
  } catch (e: any) {
    error.value = e.message || '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  padding: 40px 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
}

.login-btn {
  width: 100%;
}
</style>
```

### 5. 输出结果

```
✅ UI Demo 生成成功

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 生成的文件
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
playgrounds/{feature}/
├── Demo.vue                 # 主入口
├── components/
│   ├── LoginPage.vue        # 登录页
│   ├── RegisterPage.vue     # 注册页
│   └── ForgotPassword.vue   # 忘记密码
└── mock/
    └── api.js               # Mock API

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎨 应用的 UI System
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 组件库: Element Plus
• 主色调: #409EFF
• 表单布局: 顶部标签

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 运行方式:
1. 在 vue-app 中引入 Demo.vue
2. 或使用 Vite 单独运行 playground
```

## 示例

### 示例输入

```
请使用 ui_demo skill：
- feature: user-auth
- style: element-plus
```

### 示例输出

生成完整的登录/注册 Demo，包含：
- 登录表单（带验证）
- 注册表单（带验证）
- 忘记密码流程
- 所有交互状态（loading, error, success）

## 注意事项

1. **依赖 UI_FLOW_SPEC**：必须先有完整的 UI 规格文档
2. **组件库选择**：默认使用 Element Plus，可切换
3. **Mock API**：自动调用 `mock_api_generator` 生成配套 Mock
4. **响应式**：生成的 Demo 默认支持移动端适配
5. **状态完整**：确保覆盖所有定义的状态（loading, error, empty 等）

## 关联工具

- `/gen-demo` - Slash Command 封装，调用此 skill
- `mock_api_generator` - 配套生成 Mock API
- `spec_validator` - 生成前验证 SPEC 完整性
