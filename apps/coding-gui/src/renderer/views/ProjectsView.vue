<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useProjectStore } from '../stores/project.store'

const router = useRouter()
const projectStore = useProjectStore()

// 从 store 获取最近项目，如果为空则显示示例
const projects = ref<Array<{ name: string; path: string; lastOpened: string }>>([])

onMounted(() => {
  projectStore.loadRecentProjects()
  if (projectStore.recentProjects.length > 0) {
    projects.value = projectStore.recentProjects
  } else {
    // 没有最近项目时显示当前 ai-coding-org 项目作为示例
    projects.value = [
      {
        name: 'ai-coding-org',
        path: '/Users/huanwang/Desktop/ai-coding-org',
        lastOpened: new Date().toISOString().split('T')[0]
      }
    ]
  }
})

const isLoading = ref(false)

const selectProject = async (project: typeof projects.value[0]) => {
  isLoading.value = true
  try {
    await projectStore.openProject(project.path)
    ElMessage.success(`已打开项目: ${project.name}`)
    router.push('/workspace')
  } catch (error: any) {
    ElMessage.error(`打开项目失败: ${error.message}`)
  } finally {
    isLoading.value = false
  }
}

const browseFolder = async () => {
  // 使用 Electron 原生文件夹选择对话框
  try {
    const result = await window.electronAPI.invoke<{ canceled: boolean; path: string | null }>('dialog:openFolder')
    if (result.canceled || !result.path) {
      return
    }

    isLoading.value = true
    const success = await projectStore.openProject(result.path)
    if (success) {
      ElMessage.success(`已打开项目: ${result.path.split('/').pop()}`)
      router.push('/workspace')
    } else {
      ElMessage.error(`打开项目失败: ${projectStore.error || '未知错误'}`)
    }
  } catch (error: any) {
    ElMessage.error(`打开项目失败: ${error.message}`)
  } finally {
    isLoading.value = false
  }
}

const goBack = () => {
  router.back()
}
</script>

<template>
  <div class="projects-page">
    <header class="projects-header">
      <el-button text @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
      <h1>选择项目</h1>
    </header>

    <div class="projects-content">
      <div class="projects-list">
        <div
          v-for="project in projects"
          :key="project.path"
          class="project-item"
          @click="selectProject(project)"
        >
          <el-icon size="32" color="#409eff"><Folder /></el-icon>
          <div class="project-info">
            <div class="project-name">{{ project.name }}</div>
            <div class="project-path">{{ project.path }}</div>
          </div>
          <div class="project-meta">
            最近打开: {{ project.lastOpened }}
          </div>
        </div>
      </div>

      <el-button type="primary" size="large" @click="browseFolder">
        <el-icon><FolderAdd /></el-icon>
        浏览其他文件夹
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.projects-page {
  min-height: 100vh;
  background: #f5f7fa;
}

.projects-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 24px;
  padding-left: var(--titlebar-area-left);
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

/* 所有可交互元素都不能被拖动区域拦截 */
.projects-header * {
  -webkit-app-region: no-drag;
}

.projects-header h1 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.projects-content {
  max-width: 800px;
  margin: 40px auto;
  padding: 0 24px;
}

.projects-list {
  margin-bottom: 24px;
}

.project-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: #fff;
  border-radius: 8px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.project-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.1);
}

.project-info {
  flex: 1;
}

.project-name {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.project-path {
  font-size: 13px;
  color: #909399;
  font-family: monospace;
}

.project-meta {
  font-size: 12px;
  color: #909399;
}
</style>
