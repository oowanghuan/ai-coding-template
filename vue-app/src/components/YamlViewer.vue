<template>
  <div class="yaml-viewer">
    <!-- 视图切换 + 操作 -->
    <div class="yaml-toolbar">
      <el-radio-group v-model="viewMode" size="small">
        <el-radio-button value="tree">树形视图</el-radio-button>
        <el-radio-button value="raw">原始视图</el-radio-button>
      </el-radio-group>

      <div v-if="viewMode === 'tree'" class="tree-actions">
        <el-button size="small" text @click="expandAll">全部展开</el-button>
        <el-button size="small" text @click="collapseAll">全部折叠</el-button>
      </div>
    </div>

    <!-- 树形视图 -->
    <div v-if="viewMode === 'tree'" class="tree-view">
      <el-tree
        ref="treeRef"
        :data="treeData"
        :props="{ label: 'label', children: 'children' }"
        default-expand-all
        :expand-on-click-node="false"
      >
        <template #default="{ data }">
          <span class="tree-node">
            <span class="node-key">{{ data.key }}</span>
            <span v-if="data.value !== undefined" class="node-value">
              : {{ formatValue(data.value) }}
            </span>
          </span>
        </template>
      </el-tree>
    </div>

    <!-- 原始视图 -->
    <pre v-else class="raw-view"><code>{{ rawContent }}</code></pre>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ElTree } from 'element-plus'

const props = defineProps<{
  content: any
  rawContent?: string
}>()

const viewMode = ref<'tree' | 'raw'>('tree')
const treeRef = ref<InstanceType<typeof ElTree>>()

interface TreeNode {
  key: string
  label: string
  value?: any
  children?: TreeNode[]
}

const treeData = computed(() => {
  return convertToTreeData(props.content)
})

function convertToTreeData(obj: any, prefix = ''): TreeNode[] {
  if (!obj || typeof obj !== 'object') return []

  const nodes: TreeNode[] = []

  for (const [key, value] of Object.entries(obj)) {
    const node: TreeNode = {
      key,
      label: key,
    }

    if (value === null || value === undefined) {
      node.value = 'null'
    } else if (typeof value === 'object' && !Array.isArray(value)) {
      node.children = convertToTreeData(value, `${prefix}${key}.`)
    } else if (Array.isArray(value)) {
      node.children = value.map((item, index) => {
        if (typeof item === 'object' && item !== null) {
          return {
            key: `[${index}]`,
            label: `[${index}]`,
            children: convertToTreeData(item, `${prefix}${key}[${index}].`)
          }
        }
        return {
          key: `[${index}]`,
          label: `[${index}]`,
          value: item
        }
      })
    } else {
      node.value = value
    }

    nodes.push(node)
  }

  return nodes
}

function formatValue(value: any): string {
  if (typeof value === 'string') {
    // 长字符串截断
    return value.length > 100 ? value.slice(0, 100) + '...' : value
  }
  return String(value)
}

function expandAll() {
  const tree = treeRef.value
  if (tree) {
    const nodes = (tree as any).store.nodesMap
    for (const key in nodes) {
      nodes[key].expanded = true
    }
  }
}

function collapseAll() {
  const tree = treeRef.value
  if (tree) {
    const nodes = (tree as any).store.nodesMap
    for (const key in nodes) {
      nodes[key].expanded = false
    }
  }
}
</script>

<style scoped>
.yaml-viewer {
  padding: 12px 0;
}

.yaml-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.tree-view {
  background: var(--el-fill-color-lighter);
  border-radius: 8px;
  padding: 16px;
  max-height: 60vh;
  overflow: auto;
}

.tree-node {
  font-family: 'SF Mono', Monaco, monospace;
  font-size: 13px;
}

.node-key {
  color: var(--el-color-primary);
}

.node-value {
  color: var(--el-text-color-regular);
}

.raw-view {
  background: var(--el-fill-color-lighter);
  border-radius: 8px;
  padding: 16px;
  overflow-x: auto;
  font-family: 'SF Mono', Monaco, monospace;
  font-size: 13px;
  line-height: 1.5;
  margin: 0;
  max-height: 60vh;
}
</style>
