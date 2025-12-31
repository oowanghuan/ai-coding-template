<template>
  <el-dialog
    v-model="visible"
    :title="title"
    width="900px"
    class="doc-viewer-modal"
    :close-on-click-modal="true"
    :close-on-press-escape="true"
    destroy-on-close
  >
    <!-- 文档头部信息 -->
    <div v-if="state === 'success'" class="doc-header">
      <div class="doc-meta">
        <span class="doc-path">{{ filePath }}</span>
        <span v-if="docMeta.size" class="doc-size">
          {{ formatSize(docMeta.size) }}
        </span>
      </div>
      <div class="doc-actions">
        <el-button size="small" @click="refreshDocument" :loading="isRefreshing">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- Loading 状态 -->
    <div v-if="state === 'loading'" class="doc-loading">
      <el-icon class="loading-icon is-loading"><Loading /></el-icon>
      <p>正在从 GitHub 加载文档...</p>
    </div>

    <!-- Error 状态 -->
    <div v-else-if="state === 'error'" class="doc-error">
      <el-icon class="error-icon"><CircleCloseFilled /></el-icon>
      <p>加载失败</p>
      <p class="error-hint">{{ errorMessage }}</p>
      <el-button @click="loadDocument">重试</el-button>
    </div>

    <!-- Not Found 状态 -->
    <div v-else-if="state === 'not_found'" class="doc-not-found">
      <el-icon class="not-found-icon"><Document /></el-icon>
      <p>文档尚未创建</p>
      <p class="hint">请先在本地创建文档并 push 到 GitHub</p>
      <p class="hint path-hint">{{ filePath }}</p>
    </div>

    <!-- Empty 状态 -->
    <div v-else-if="state === 'empty'" class="doc-empty">
      <el-icon class="empty-icon"><DocumentRemove /></el-icon>
      <p>文档内容为空</p>
      <p class="hint">该文档已存在但尚未填写内容</p>
    </div>

    <!-- 内容区 -->
    <div v-else-if="state === 'success'" class="doc-content">
      <!-- Markdown 渲染 -->
      <div
        v-if="docType === 'markdown'"
        class="markdown-body"
        v-html="renderedMarkdown"
      />

      <!-- YAML 展示 -->
      <YamlViewer
        v-else
        :content="parsedYaml"
        :raw-content="docContent?.rawContent"
      />
    </div>

    <!-- Footer -->
    <template #footer>
      <div class="doc-footer">
        <el-button @click="openInGitHub" type="primary" plain>
          <el-icon><Link /></el-icon>
          在 GitHub 中查看
        </el-button>
        <el-button @click="close">关闭</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { githubDocService, DocContent, DocState, DocError } from '@/services/githubDocService'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import hljs from 'highlight.js'
import YamlViewer from './YamlViewer.vue'
import { Loading, CircleCloseFilled, Document, DocumentRemove, Link, Refresh } from '@element-plus/icons-vue'

// 配置 marked
marked.setOptions({
  highlight: (code: string, lang: string) => {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,
  gfm: true,
} as any)

const props = defineProps<{
  modelValue: boolean
  title: string
  filePath: string
}>()

const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const state = ref<DocState>('idle')
const docContent = ref<DocContent | null>(null)
const errorMessage = ref('')
const isRefreshing = ref(false)

const docType = computed(() => docContent.value?.type || 'markdown')
const docMeta = computed(() => ({
  sha: docContent.value?.sha || '',
  size: docContent.value?.size || 0,
}))

const renderedMarkdown = computed(() => {
  if (docContent.value?.type === 'markdown') {
    const html = marked(docContent.value.rawContent) as string
    return DOMPurify.sanitize(html)
  }
  return ''
})

const parsedYaml = computed(() => docContent.value?.parsedContent || {})

// 监听弹窗打开
watch(() => props.modelValue, async (newVal) => {
  if (newVal && props.filePath) {
    await loadDocument()
  }
})

async function loadDocument() {
  state.value = 'loading'
  errorMessage.value = ''

  try {
    docContent.value = await githubDocService.fetchDocument(props.filePath)
    state.value = 'success'
  } catch (error: any) {
    if (error.isNotFound) {
      state.value = 'not_found'
    } else if (error.isEmpty) {
      state.value = 'empty'
    } else if (error.isRateLimit) {
      state.value = 'error'
      errorMessage.value = 'GitHub API 调用次数已达上限，请稍后重试'
    } else if (error.isConfigError) {
      state.value = 'error'
      errorMessage.value = '服务器配置错误，请联系管理员'
    } else {
      state.value = 'error'
      errorMessage.value = error.message || '网络错误，请检查连接'
    }
  }
}

async function refreshDocument() {
  isRefreshing.value = true
  githubDocService.clearCache()
  await loadDocument()
  isRefreshing.value = false
}

function openInGitHub() {
  const url = githubDocService.getGitHubUrl(props.filePath)
  window.open(url, '_blank')
}

function close() {
  visible.value = false
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}
</script>

<style scoped>
.doc-viewer-modal :deep(.el-dialog__body) {
  max-height: 70vh;
  overflow-y: auto;
}

.doc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.doc-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.doc-path {
  font-family: 'SF Mono', Monaco, monospace;
}

.doc-loading,
.doc-error,
.doc-not-found,
.doc-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.doc-loading .loading-icon {
  font-size: 48px;
  color: var(--el-color-primary);
  margin-bottom: 16px;
}

.doc-error .error-icon {
  font-size: 48px;
  color: var(--el-color-danger);
  margin-bottom: 16px;
}

.doc-not-found .not-found-icon,
.doc-empty .empty-icon {
  font-size: 48px;
  color: var(--el-text-color-secondary);
  margin-bottom: 16px;
}

.error-hint,
.hint {
  color: var(--el-text-color-secondary);
  font-size: 14px;
  margin-top: 8px;
}

.path-hint {
  font-family: 'SF Mono', Monaco, monospace;
  background: var(--el-fill-color-light);
  padding: 4px 8px;
  border-radius: 4px;
}

.doc-content {
  line-height: 1.6;
}

.markdown-body {
  /* GitHub-like markdown styles */
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4) {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
}

.markdown-body :deep(h1) {
  font-size: 2em;
  border-bottom: 1px solid var(--el-border-color-lighter);
  padding-bottom: 0.3em;
}

.markdown-body :deep(h2) {
  font-size: 1.5em;
  border-bottom: 1px solid var(--el-border-color-lighter);
  padding-bottom: 0.3em;
}

.markdown-body :deep(pre) {
  background: var(--el-fill-color-light);
  padding: 16px;
  border-radius: 6px;
  overflow-x: auto;
}

.markdown-body :deep(code) {
  font-family: 'SF Mono', Monaco, monospace;
  font-size: 13px;
}

.markdown-body :deep(p code) {
  background: var(--el-fill-color-light);
  padding: 2px 6px;
  border-radius: 4px;
}

.markdown-body :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 16px 0;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  border: 1px solid var(--el-border-color);
  padding: 8px 12px;
}

.markdown-body :deep(th) {
  background: var(--el-fill-color-light);
}

.markdown-body :deep(blockquote) {
  border-left: 4px solid var(--el-border-color);
  padding: 0 16px;
  margin: 16px 0;
  color: var(--el-text-color-secondary);
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 2em;
  margin: 16px 0;
}

.markdown-body :deep(li) {
  margin: 4px 0;
}

.doc-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
