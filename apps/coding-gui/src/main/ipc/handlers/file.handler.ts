/**
 * 文件相关 IPC 处理器
 * CODE-003: file:read, file:watch
 */

import { readFile, stat } from 'fs/promises'
import { watch, FSWatcher } from 'chokidar'
import { BrowserWindow } from 'electron'
import { extname } from 'path'
import type {
  FileReadRequest,
  FileReadResponse,
  FileChangeEvent
} from '../../../shared/types/ipc.types'
import { ERROR_CODES, createError } from '../../../shared/types/error.types'
import { FILE_CHANNELS } from '../../../shared/constants/ipc-channels'

// MIME 类型映射
const MIME_TYPES: Record<string, string> = {
  '.md': 'text/markdown',
  '.yaml': 'text/yaml',
  '.yml': 'text/yaml',
  '.json': 'application/json',
  '.ts': 'text/typescript',
  '.tsx': 'text/typescript',
  '.js': 'text/javascript',
  '.jsx': 'text/javascript',
  '.vue': 'text/vue',
  '.css': 'text/css',
  '.scss': 'text/scss',
  '.html': 'text/html',
  '.txt': 'text/plain'
}

// 活跃的文件监控器
const activeWatchers = new Map<string, FSWatcher>()

// 默认最大文件大小 (5MB)
const DEFAULT_MAX_SIZE = 5 * 1024 * 1024

/**
 * 读取文件内容
 */
export async function handleFileRead(
  request: FileReadRequest
): Promise<FileReadResponse> {
  const { path: filePath, maxSize = DEFAULT_MAX_SIZE } = request

  try {
    // 检查文件是否存在
    const fileStat = await stat(filePath)

    if (!fileStat.isFile()) {
      throw createError(
        ERROR_CODES.FS_NOT_FOUND,
        `Path is not a file: ${filePath}`
      )
    }

    // 检查文件大小
    if (fileStat.size > maxSize) {
      throw createError(
        ERROR_CODES.FS_READ_FAILED,
        `File too large: ${fileStat.size} bytes (max: ${maxSize})`,
        { size: fileStat.size, maxSize }
      )
    }

    // 读取文件内容
    const content = await readFile(filePath, 'utf-8')

    // 确定 MIME 类型
    const ext = extname(filePath).toLowerCase()
    const mimeType = MIME_TYPES[ext] || 'text/plain'

    return {
      content,
      path: filePath,
      size: fileStat.size,
      mimeType,
      lastModified: fileStat.mtime.toISOString()
    }

  } catch (error) {
    if ((error as { code?: string }).code?.startsWith('E-')) {
      throw error
    }

    const nodeError = error as NodeJS.ErrnoException
    if (nodeError.code === 'ENOENT') {
      throw createError(
        ERROR_CODES.FS_NOT_FOUND,
        `File not found: ${filePath}`
      )
    }
    if (nodeError.code === 'EACCES') {
      throw createError(
        ERROR_CODES.FS_PERMISSION,
        `Permission denied: ${filePath}`
      )
    }

    throw createError(
      ERROR_CODES.FS_READ_FAILED,
      `Failed to read file: ${(error as Error).message}`,
      { path: filePath }
    )
  }
}

/**
 * 开始监控文件变更
 */
export function startFileWatch(
  projectPath: string,
  window: BrowserWindow
): void {
  // 如果已经在监控，先停止
  stopFileWatch(projectPath)

  // 监控的文件模式
  const patterns = [
    `${projectPath}/.claude/**/*.yaml`,
    `${projectPath}/.claude/**/*.yml`,
    `${projectPath}/docs/**/*.md`,
    `${projectPath}/docs/**/*.yaml`
  ]

  const watcher = watch(patterns, {
    ignored: /(^|[\/\\])\../, // 忽略隐藏文件（除了 .claude）
    persistent: true,
    ignoreInitial: true,
    awaitWriteFinish: {
      stabilityThreshold: 100,
      pollInterval: 50
    }
  })

  // 文件变更事件
  watcher.on('change', (path) => {
    const event: FileChangeEvent = {
      path,
      type: 'update',
      timestamp: new Date().toISOString()
    }
    window.webContents.send(FILE_CHANNELS.CHANGE, event)
  })

  watcher.on('add', (path) => {
    const event: FileChangeEvent = {
      path,
      type: 'create',
      timestamp: new Date().toISOString()
    }
    window.webContents.send(FILE_CHANNELS.CHANGE, event)
  })

  watcher.on('unlink', (path) => {
    const event: FileChangeEvent = {
      path,
      type: 'delete',
      timestamp: new Date().toISOString()
    }
    window.webContents.send(FILE_CHANNELS.CHANGE, event)
  })

  watcher.on('error', (error) => {
    console.error('[FileWatcher] Error:', error)
  })

  activeWatchers.set(projectPath, watcher)
}

/**
 * 停止文件监控
 */
export function stopFileWatch(projectPath: string): void {
  const watcher = activeWatchers.get(projectPath)
  if (watcher) {
    watcher.close()
    activeWatchers.delete(projectPath)
  }
}

/**
 * 停止所有文件监控
 */
export function stopAllFileWatches(): void {
  for (const [path, watcher] of activeWatchers) {
    watcher.close()
  }
  activeWatchers.clear()
}

/**
 * 获取活跃的监控器数量
 */
export function getActiveWatcherCount(): number {
  return activeWatchers.size
}
