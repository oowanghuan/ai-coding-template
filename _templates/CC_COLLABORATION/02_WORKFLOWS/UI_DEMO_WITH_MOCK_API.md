# UI_DEMO_WITH_MOCK_API.md
# UI Demo + Mock API 生成工作流

> 版本：v1.0
> 最后更新：2024-12-10
> 阶段：Phase 3 Demo
> 触发：当 UI SPEC 完成后需要生成可交互原型时

---

## 1. 概述

本文档定义生成 UI Demo 和 Mock API 的标准流程，确保：
- Demo 与 UI SPEC 保持一致
- Mock API 与 API SPEC 对齐
- Demo 可独立运行和演示
- 便于产品/设计评审

---

## 2. 触发条件

以下情况需要执行本流程：
- UI SPEC 已完成并通过初审
- 需要生成可交互原型供评审
- 用户执行 `/gen-demo` 命令

---

## 3. 前置条件

### 3.1 必需文档

| 文档 | 路径 | 状态 |
|------|------|------|
| UI SPEC | `Docs/{feature}/11_UI_FLOW_SPEC.md` | 必须存在 |
| API SPEC | `Docs/{feature}/11_API_SPEC.md` | 可选（如有 API） |
| UI System | `Docs/_system/_ui_system/` | 必须存在 |

### 3.2 技术环境

| 项目 | 要求 |
|------|------|
| 前端框架 | Vue 3 + Element Plus |
| Demo 目录 | `playgrounds/{feature}/` |
| Mock 工具 | Mock Service Worker 或本地 JSON |

---

## 4. 执行流程

### Step 1: 读取规格文档

```yaml
# Claude Code 执行
1. 读取 UI SPEC：
   - Docs/{feature}/11_UI_FLOW_SPEC.md
   - 提取页面清单、组件定义、交互规则

2. 读取 API SPEC（如有）：
   - Docs/{feature}/11_API_SPEC.md
   - 提取接口清单、请求/响应结构

3. 读取 UI System：
   - Docs/_system/_ui_system/00_UI_TOKENS.md
   - Docs/_system/_ui_system/01_COMPONENT_LIBRARY.md
   - 确保组件使用符合规范
```

### Step 2: 创建 Demo 目录结构

```bash
playgrounds/{feature}/
├── index.html           # 入口页面
├── src/
│   ├── main.js          # Vue 应用入口
│   ├── App.vue          # 根组件
│   ├── router/
│   │   └── index.js     # 路由配置
│   ├── views/           # 页面组件
│   │   ├── ListView.vue
│   │   ├── DetailView.vue
│   │   └── FormDialog.vue
│   ├── components/      # 业务组件
│   │   └── ...
│   ├── mock/            # Mock 数据
│   │   ├── handlers.js  # Mock 处理器
│   │   └── data.js      # Mock 数据
│   └── api/             # API 调用
│       └── index.js
├── package.json
└── vite.config.js
```

### Step 3: 生成页面组件

#### 3.1 列表页模板

```vue
<!-- views/ListView.vue -->
<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="page-header__left">
        <h1 class="page-title">{页面标题}</h1>
        <p class="page-desc">{页面描述}</p>
      </div>
      <div class="page-header__right">
        <el-button type="primary" @click="handleCreate">
          新增{资源}
        </el-button>
      </div>
    </div>

    <!-- 搜索区域 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="请输入关键词"
            clearable
            @clear="handleSearch"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable>
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="inactive" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
      >
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <FormDialog
      v-model:visible="dialogVisible"
      :data="currentRow"
      @success="handleSuccess"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import FormDialog from './FormDialog.vue'
import { getList, deleteItem } from '@/api'

// 状态
const loading = ref(false)
const dialogVisible = ref(false)
const currentRow = ref(null)
const tableData = ref([])

// 搜索表单
const searchForm = reactive({
  keyword: '',
  status: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 方法
const fetchData = async () => {
  loading.value = true
  try {
    const res = await getList({
      ...searchForm,
      page: pagination.page,
      pageSize: pagination.pageSize
    })
    tableData.value = res.data.list
    pagination.total = res.data.pagination.total
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.keyword = ''
  searchForm.status = ''
  handleSearch()
}

const handleCreate = () => {
  currentRow.value = null
  dialogVisible.value = true
}

const handleEdit = (row) => {
  currentRow.value = { ...row }
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定要删除吗？', '提示', { type: 'warning' })
  await deleteItem(row.id)
  ElMessage.success('删除成功')
  fetchData()
}

const handleSuccess = () => {
  dialogVisible.value = false
  fetchData()
}

const handleSizeChange = () => fetchData()
const handlePageChange = () => fetchData()

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.page-container {
  padding: 20px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}
.page-title {
  margin: 0 0 8px;
  font-size: 20px;
}
.page-desc {
  margin: 0;
  color: #909399;
  font-size: 14px;
}
.search-card {
  margin-bottom: 20px;
}
.table-card {
  margin-bottom: 20px;
}
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
```

### Step 4: 生成 Mock API

#### 4.1 Mock 数据定义

```javascript
// src/mock/data.js

// 生成 Mock ID
let idCounter = 1
const generateId = () => idCounter++

// 生成 Mock 数据
const generateMockItem = (overrides = {}) => ({
  id: generateId(),
  name: `示例名称 ${idCounter}`,
  description: '这是一段描述文字',
  status: Math.random() > 0.3 ? 'active' : 'inactive',
  type: 'default',
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  ...overrides
})

// 初始数据
export const mockData = Array.from({ length: 50 }, () => generateMockItem())

// 数据操作方法
export const mockDb = {
  list: mockData,

  getList({ page = 1, pageSize = 20, keyword = '', status = '' }) {
    let filtered = [...this.list]

    if (keyword) {
      filtered = filtered.filter(item =>
        item.name.includes(keyword) || item.description?.includes(keyword)
      )
    }

    if (status) {
      filtered = filtered.filter(item => item.status === status)
    }

    const total = filtered.length
    const start = (page - 1) * pageSize
    const list = filtered.slice(start, start + pageSize)

    return {
      list,
      pagination: { page, pageSize, total, totalPages: Math.ceil(total / pageSize) }
    }
  },

  getById(id) {
    return this.list.find(item => item.id === Number(id))
  },

  create(data) {
    const newItem = generateMockItem(data)
    this.list.unshift(newItem)
    return newItem
  },

  update(id, data) {
    const index = this.list.findIndex(item => item.id === Number(id))
    if (index === -1) throw new Error('资源不存在')
    this.list[index] = { ...this.list[index], ...data, updatedAt: new Date().toISOString() }
    return this.list[index]
  },

  delete(id) {
    const index = this.list.findIndex(item => item.id === Number(id))
    if (index === -1) throw new Error('资源不存在')
    this.list.splice(index, 1)
    return true
  }
}
```

#### 4.2 Mock 处理器（MSW 方式）

```javascript
// src/mock/handlers.js
import { http, HttpResponse, delay } from 'msw'
import { mockDb } from './data'

const BASE_URL = '/api/v1/{resources}'

export const handlers = [
  // 列表查询
  http.get(`${BASE_URL}`, async ({ request }) => {
    await delay(300) // 模拟网络延迟
    const url = new URL(request.url)
    const params = {
      page: Number(url.searchParams.get('page')) || 1,
      pageSize: Number(url.searchParams.get('pageSize')) || 20,
      keyword: url.searchParams.get('keyword') || '',
      status: url.searchParams.get('status') || ''
    }
    const result = mockDb.getList(params)
    return HttpResponse.json({ code: 0, message: 'success', data: result })
  }),

  // 详情查询
  http.get(`${BASE_URL}/:id`, async ({ params }) => {
    await delay(200)
    const item = mockDb.getById(params.id)
    if (!item) {
      return HttpResponse.json(
        { code: 404, message: '资源不存在', error: { code: 'RES_001' } },
        { status: 404 }
      )
    }
    return HttpResponse.json({ code: 0, message: 'success', data: item })
  }),

  // 创建
  http.post(`${BASE_URL}`, async ({ request }) => {
    await delay(500)
    const body = await request.json()
    const item = mockDb.create(body)
    return HttpResponse.json(
      { code: 0, message: '创建成功', data: item },
      { status: 201 }
    )
  }),

  // 更新
  http.put(`${BASE_URL}/:id`, async ({ params, request }) => {
    await delay(500)
    const body = await request.json()
    try {
      const item = mockDb.update(params.id, body)
      return HttpResponse.json({ code: 0, message: '更新成功', data: item })
    } catch (e) {
      return HttpResponse.json(
        { code: 404, message: e.message, error: { code: 'RES_001' } },
        { status: 404 }
      )
    }
  }),

  // 删除
  http.delete(`${BASE_URL}/:id`, async ({ params }) => {
    await delay(300)
    try {
      mockDb.delete(params.id)
      return HttpResponse.json({ code: 0, message: '删除成功', data: null })
    } catch (e) {
      return HttpResponse.json(
        { code: 404, message: e.message, error: { code: 'RES_001' } },
        { status: 404 }
      )
    }
  })
]
```

### Step 5: 配置 Demo 入口

```javascript
// src/main.js
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import App from './App.vue'
import router from './router'

// 启用 Mock（仅开发环境）
async function enableMocking() {
  if (import.meta.env.DEV) {
    const { worker } = await import('./mock/browser')
    return worker.start({ onUnhandledRequest: 'bypass' })
  }
}

enableMocking().then(() => {
  createApp(App)
    .use(ElementPlus, { locale: zhCn })
    .use(router)
    .mount('#app')
})
```

### Step 6: 验证 Demo

```yaml
# 验证检查清单
1. 页面加载正常
   - [ ] 列表页显示正确
   - [ ] 分页功能正常
   - [ ] 搜索功能正常

2. CRUD 操作
   - [ ] 新增成功，刷新列表
   - [ ] 编辑成功，数据更新
   - [ ] 删除成功，提示确认

3. 状态处理
   - [ ] 加载中显示 loading
   - [ ] 空数据显示空状态
   - [ ] 错误显示错误提示

4. 交互反馈
   - [ ] 操作成功有提示
   - [ ] 表单验证生效
   - [ ] 按钮状态正确
```

---

## 5. 输出交付物

### 5.1 文件清单

| 文件 | 描述 |
|------|------|
| `playgrounds/{feature}/` | Demo 完整目录 |
| `playgrounds/{feature}/README.md` | Demo 说明文档 |

### 5.2 Demo README 模板

```markdown
# {功能名称} Demo

## 快速启动

\`\`\`bash
cd playgrounds/{feature}
npm install
npm run dev
\`\`\`

## 页面清单

| 页面 | 路由 | 说明 |
|------|------|------|
| 列表页 | / | 主列表页面 |
| 详情页 | /:id | 详情查看 |

## Mock API

| 接口 | 方法 | 路径 |
|------|------|------|
| 列表 | GET | /api/v1/{resources} |
| 详情 | GET | /api/v1/{resources}/:id |
| 创建 | POST | /api/v1/{resources} |
| 更新 | PUT | /api/v1/{resources}/:id |
| 删除 | DELETE | /api/v1/{resources}/:id |

## 注意事项

- Mock 数据仅在开发环境生效
- 刷新页面会重置 Mock 数据
```

---

## 6. Claude Code 执行指南

### 6.1 收到 /gen-demo 命令时

```markdown
## 执行步骤

1. 确认前置条件
   - 检查 UI SPEC 是否存在
   - 检查 API SPEC 是否存在
   - 确认 UI System 规范

2. 生成 Demo
   - 创建目录结构
   - 生成页面组件
   - 生成 Mock API
   - 配置路由和入口

3. 验证 Demo
   - 启动开发服务器
   - 使用 Chrome MCP 验证页面
   - 检查核心流程

4. 输出结果
   - 显示 Demo 地址
   - 列出生成的文件
   - 提示下一步操作
```

### 6.2 输出示例

```
Demo 已生成完成

Demo 地址：http://localhost:5173/demo/{feature}

生成的文件：
  - playgrounds/{feature}/src/views/ListView.vue
  - playgrounds/{feature}/src/views/DetailView.vue
  - playgrounds/{feature}/src/views/FormDialog.vue
  - playgrounds/{feature}/src/mock/handlers.js
  - playgrounds/{feature}/src/mock/data.js
  - playgrounds/{feature}/README.md

下一步：
  1. 启动 Demo：cd playgrounds/{feature} && npm run dev
  2. 组织评审会议，使用 DEMO_REVIEW_TEMPLATE.md 记录反馈
  3. 根据反馈修改 Demo 和 SPEC
  4. 评审通过后进入 Phase 4 Design
```

---

## 7. 检查清单

### Demo 生成完成标准

- [ ] Demo 可独立启动运行
- [ ] 所有页面与 UI SPEC 一致
- [ ] Mock API 与 API SPEC 一致
- [ ] 组件使用符合 UI System
- [ ] 核心交互流程可演示
- [ ] 加载/空/错误状态已处理
- [ ] README.md 已生成

---

## CHANGELOG

| 版本 | 日期 | 作者 | 变更内容 |
|------|------|------|----------|
| v1.0 | 2024-12-10 | Claude | 初始版本 |
