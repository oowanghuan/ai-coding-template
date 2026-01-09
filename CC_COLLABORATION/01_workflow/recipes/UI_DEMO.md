# UI Demo 生成工作流

> 版本：v2.0
> 最后更新：2026-01-09
> 触发：Phase 3 Demo 阶段 / /gen-demo 命令

---

## 1. 概述

本文档定义 UI Demo 生成的标准流程，确保：
- Demo 可交互运行
- Mock API 数据完整
- 符合 UI 规范
- 便于评审和修改

---

## 2. 触发条件

- 进入 Phase 3 Demo 阶段
- 用户执行 `/gen-demo {feature}` 命令
- 需要快速原型验证

---

## 3. 生成流程

### Step 1: 读取规格文档

```yaml
必读文档:
  - 21_UI_FLOW_SPEC.md    # UI 流程规格
  - 20_API_SPEC.md        # API 规格（用于 Mock）

可选文档:
  - 10_CONTEXT.md         # 功能背景
  - _ui_system/           # UI 规范
```

### Step 2: 分析 UI 组件需求

```yaml
从 UI_FLOW_SPEC 提取:
  - 页面列表
  - 组件结构
  - 状态定义
  - 交互流程
  - 数据展示需求
```

### Step 3: 生成 Mock API

```javascript
// src/mock/user-auth.js

export const mockApi = {
  // 登录接口
  'POST /api/auth/login': (req) => {
    const { username, password } = req.body

    // 模拟验证
    if (username === 'admin' && password === '123456') {
      return {
        code: 200,
        data: {
          token: 'mock-token-xxx',
          user: {
            id: 1,
            username: 'admin',
            name: '管理员'
          }
        }
      }
    }

    return {
      code: 401,
      error: {
        code: 'INVALID_CREDENTIALS',
        message: '用户名或密码错误'
      }
    }
  },

  // 获取用户信息
  'GET /api/auth/me': () => ({
    code: 200,
    data: {
      id: 1,
      username: 'admin',
      name: '管理员',
      avatar: 'https://via.placeholder.com/100'
    }
  })
}
```

### Step 4: 生成 Demo 页面

```vue
<!-- src/views/demo/LoginDemo.vue -->

<template>
  <div class="login-demo">
    <el-card class="login-card">
      <template #header>
        <h2>用户登录</h2>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 状态展示 -->
      <div class="demo-state">
        <h4>当前状态: {{ currentState }}</h4>
        <pre>{{ JSON.stringify(form, null, 2) }}</pre>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

// 状态
const currentState = ref('idle')
const loading = ref(false)

// 表单数据
const form = reactive({
  username: '',
  password: ''
})

// 验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度 6-20 位', trigger: 'blur' }
  ]
}

// 登录处理
const handleLogin = async () => {
  currentState.value = 'submitting'
  loading.value = true

  try {
    // 模拟 API 调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    if (form.username === 'admin' && form.password === '123456') {
      currentState.value = 'success'
      ElMessage.success('登录成功！')
    } else {
      currentState.value = 'error'
      ElMessage.error('用户名或密码错误')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-demo {
  padding: 40px;
  display: flex;
  justify-content: center;
}

.login-card {
  width: 400px;
}

.demo-state {
  margin-top: 20px;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 4px;
}
</style>
```

### Step 5: 配置路由

```javascript
// src/router/demo.js

export const demoRoutes = [
  {
    path: '/demo/login',
    name: 'LoginDemo',
    component: () => import('@/views/demo/LoginDemo.vue'),
    meta: { title: '登录 Demo' }
  }
]
```

### Step 6: 输出生成报告

```markdown
## ✓ Demo 生成完成

**功能**: user-auth (用户认证)
**页面**: 登录页

### 生成的文件
- src/views/demo/LoginDemo.vue
- src/mock/user-auth.js
- src/router/demo.js (已更新)

### Demo 访问
- 地址: http://localhost:5173/demo/login
- 测试账号: admin / 123456

### 包含的交互
- [x] 表单验证
- [x] 登录提交
- [x] 加载状态
- [x] 成功/失败反馈
- [x] 状态展示（调试用）

### 下一步
1. 启动开发服务器: npm run dev
2. 访问 Demo 页面验证
3. 根据反馈调整
4. 提交 Phase 3 评审
```

---

## 4. Mock API 规范

### 4.1 目录结构

```
src/mock/
├── index.js          # Mock 入口
├── user-auth.js      # 用户认证 Mock
├── dashboard.js      # 看板 Mock
└── ...
```

### 4.2 Mock 格式

```javascript
// 标准 Mock 格式
export const mockApi = {
  'METHOD /api/path': (req) => {
    // req.body - 请求体
    // req.query - 查询参数
    // req.params - 路径参数

    return {
      code: 200,
      data: { ... },
      // 或
      error: {
        code: 'ERROR_CODE',
        message: '错误信息'
      }
    }
  }
}
```

### 4.3 常用 Mock 场景

```javascript
// 列表数据
'GET /api/users': () => ({
  code: 200,
  data: {
    list: [
      { id: 1, name: '用户1' },
      { id: 2, name: '用户2' }
    ],
    total: 100,
    page: 1,
    pageSize: 10
  }
})

// 详情数据
'GET /api/users/:id': (req) => ({
  code: 200,
  data: {
    id: req.params.id,
    name: '用户详情'
  }
})

// 创建数据
'POST /api/users': (req) => ({
  code: 201,
  data: {
    id: Date.now(),
    ...req.body
  }
})

// 错误响应
'POST /api/auth/login': () => ({
  code: 401,
  error: {
    code: 'INVALID_CREDENTIALS',
    message: '用户名或密码错误'
  }
})
```

---

## 5. Demo 规范

### 5.1 必须包含

- 完整的页面 UI
- 所有交互状态
- 表单验证
- 加载状态
- 成功/失败反馈

### 5.2 调试辅助

```vue
<!-- 状态展示组件 -->
<div class="demo-debug" v-if="isDev">
  <h4>调试信息</h4>
  <p>当前状态: {{ state }}</p>
  <pre>{{ JSON.stringify(data, null, 2) }}</pre>
</div>
```

### 5.3 UI 规范遵守

```vue
<!-- 使用项目 UI 组件 -->
<el-button type="primary">主要按钮</el-button>
<el-input placeholder="输入框" />
<el-table :data="list">...</el-table>

<!-- 使用项目 Design Tokens -->
<style scoped>
.container {
  padding: var(--spacing-md);
  color: var(--color-text-primary);
}
</style>
```

---

## 6. 评审要点

### 6.1 UI 评审

- [ ] 布局符合规格
- [ ] 组件使用正确
- [ ] 响应式适配
- [ ] 交互流程完整

### 6.2 功能评审

- [ ] 表单验证正确
- [ ] 状态切换正确
- [ ] 错误处理完整
- [ ] 边界情况覆盖

### 6.3 代码评审

- [ ] 组件结构清晰
- [ ] 命名规范
- [ ] 无冗余代码
- [ ] 可读性良好

---

## CHANGELOG

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v2.0 | 2026-01-09 | 重构文档结构，添加 Mock 规范 |
| v1.0 | 2024-12-10 | 初始版本 |
