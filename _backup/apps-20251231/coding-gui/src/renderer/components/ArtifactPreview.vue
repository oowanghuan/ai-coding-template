<script setup lang="ts">
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  visible: boolean
  path: string
  content: string
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const fileName = computed(() => props.path.split('/').pop() || '')

const lineCount = computed(() => props.content.split('\n').length)

const charCount = computed(() => props.content.length.toLocaleString())

const searchQuery = ref('')
const showSearch = ref(false)

const copyContent = () => {
  navigator.clipboard.writeText(props.content).then(() => {
    ElMessage.success('内容已复制到剪贴板')
  })
}

const openInEditor = () => {
  ElMessage.info('在 VS Code 中打开（Demo）')
}

const toggleSearch = () => {
  showSearch.value = !showSearch.value
  if (!showSearch.value) {
    searchQuery.value = ''
  }
}
</script>

<template>
  <el-dialog
    :model-value="visible"
    :title="' '"
    width="900px"
    top="5vh"
    @close="emit('close')"
  >
    <template #header>
      <div class="preview-header">
        <div class="preview-title">
          <el-icon><Document /></el-icon>
          {{ fileName }}
        </div>
        <el-button size="small" @click="openInEditor">
          <el-icon><Edit /></el-icon>
          在 VS Code 中打开
        </el-button>
      </div>
    </template>

    <div class="preview-toolbar">
      <div class="preview-actions">
        <el-button size="small" text @click="copyContent">
          <el-icon><CopyDocument /></el-icon>
          复制
        </el-button>
        <el-button size="small" text @click="toggleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
      </div>
      <div class="preview-meta">
        <span>行数: {{ lineCount }}</span>
        <el-divider direction="vertical" />
        <span>字符: {{ charCount }}</span>
      </div>
    </div>

    <transition name="fade">
      <div v-if="showSearch" class="preview-search">
        <el-input
          v-model="searchQuery"
          placeholder="搜索内容..."
          size="small"
          prefix-icon="Search"
          clearable
        />
      </div>
    </transition>

    <div class="preview-content">
      <div v-if="loading" class="preview-loading">
        <el-icon class="is-loading" :size="32"><Loading /></el-icon>
        <span>加载中...</span>
      </div>
      <pre v-else><code>{{ content }}</code></pre>
    </div>
  </el-dialog>
</template>

<style scoped>
.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-right: 40px;
}

.preview-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.preview-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 6px;
  margin-bottom: 12px;
}

.preview-actions {
  display: flex;
  gap: 4px;
}

.preview-meta {
  display: flex;
  align-items: center;
  font-size: 13px;
  color: #909399;
}

.preview-search {
  margin-bottom: 12px;
}

.preview-content {
  background: #fafafa;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  padding: 16px;
  max-height: 60vh;
  overflow: auto;
}

.preview-content pre {
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
}

.preview-content code {
  color: #303133;
}

.preview-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px;
  color: #909399;
}

/* Scrollbar styling */
.preview-content::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.preview-content::-webkit-scrollbar-track {
  background: #f0f0f0;
}

.preview-content::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 4px;
}

.preview-content::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
