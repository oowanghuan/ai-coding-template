/**
 * Session 相关 IPC 处理器
 * GUI-CLI 通信通道实现
 */

import * as fs from 'fs'
import * as path from 'path'
import { BrowserWindow } from 'electron'
import { randomUUID } from 'crypto'
import type {
  Session,
  SessionStatus,
  SessionListRequest,
  SessionListResponse,
  SessionSendCommandRequest,
  SessionSendCommandResponse,
  SessionWaitResultRequest,
  SessionExecutionResult,
  SessionChangeEvent
} from '../../../shared/types/ipc.types'
import { SESSION_CHANNELS } from '../../../shared/constants/ipc-channels'

// Session 目录名
const SESSIONS_DIR = '.claude/gui-sessions'

// Session 文件后缀
const SESSION_FILE = '.json'
const CMD_FILE = '.cmd'
const ACK_FILE = '.ack'
const RESULT_FILE = '.result'

// 超时配置
const DEFAULT_RESULT_TIMEOUT = 30000 // 30秒

// 活跃的 Session 目录监听器
const activeWatchers = new Map<string, fs.FSWatcher>()

// 等待结果的回调
const resultCallbacks = new Map<string, {
  resolve: (result: SessionExecutionResult) => void
  timeout: NodeJS.Timeout
}>()

/**
 * 获取 Session 目录路径
 */
function getSessionsDir(projectPath: string): string {
  return path.join(projectPath, SESSIONS_DIR)
}

/**
 * 获取 Session 文件路径
 */
function getSessionFilePath(projectPath: string, sessionId: string, suffix: string): string {
  return path.join(getSessionsDir(projectPath), `session-${sessionId}${suffix}`)
}

/**
 * 检查 Session 状态
 */
function checkSessionStatus(session: Session): SessionStatus {
  const now = Date.now()
  const heartbeatTime = new Date(session.heartbeatAt).getTime()
  const heartbeatAge = now - heartbeatTime

  // 心跳超过 60 秒，标记为 stale
  if (heartbeatAge > 60000) {
    // 超过 5 分钟，标记为 disconnected
    if (heartbeatAge > 300000) {
      return 'disconnected'
    }
    return 'stale'
  }

  return session.status === 'disconnected' ? 'disconnected' : 'active'
}

/**
 * 读取 Session 文件
 */
function readSessionFile(filePath: string): Session | null {
  try {
    if (!fs.existsSync(filePath)) {
      return null
    }
    const content = fs.readFileSync(filePath, 'utf-8')
    const session = JSON.parse(content) as Session
    // 更新状态
    session.status = checkSessionStatus(session)
    return session
  } catch {
    return null
  }
}

/**
 * 获取 Session 列表
 */
export async function handleSessionList(
  request: SessionListRequest
): Promise<SessionListResponse> {
  const sessionsDir = getSessionsDir(request.projectPath)

  // 如果目录不存在，返回空列表
  if (!fs.existsSync(sessionsDir)) {
    return { sessions: [] }
  }

  const sessions: Session[] = []
  const files = fs.readdirSync(sessionsDir)

  for (const file of files) {
    if (file.endsWith(SESSION_FILE) && file.startsWith('session-')) {
      const filePath = path.join(sessionsDir, file)
      const session = readSessionFile(filePath)
      if (session) {
        sessions.push(session)
      }
    }
  }

  // 按最后活跃时间排序（最近的在前）
  sessions.sort((a, b) =>
    new Date(b.lastActiveAt).getTime() - new Date(a.lastActiveAt).getTime()
  )

  return { sessions }
}

/**
 * 发送命令到 CLI Session
 *
 * 注意：使用方案 A（UserPromptSubmit Hook）时，命令写入文件后立即返回。
 * CLI 端的 Hook 会在用户下次输入时检测到命令并执行。
 */
export async function handleSessionSendCommand(
  request: SessionSendCommandRequest
): Promise<SessionSendCommandResponse> {
  const { sessionId, projectPath, command, context } = request
  const cmdId = `cmd-${randomUUID()}`

  // 构建命令对象
  const cmdPayload = {
    cmdId,
    timestamp: new Date().toISOString(),
    command,
    source: 'gui-button',
    context: context || {}
  }

  // 获取文件路径
  const cmdFilePath = getSessionFilePath(projectPath, sessionId, CMD_FILE)

  try {
    // 写入命令文件
    fs.writeFileSync(cmdFilePath, JSON.stringify(cmdPayload, null, 2))

    // 方案 A：命令写入后立即返回，不等待 ACK
    // CLI 端的 UserPromptSubmit Hook 会在用户下次输入时处理命令
    return {
      cmdId,
      status: 'sent',
      retryCount: 0
    }
  } catch (error) {
    return {
      cmdId,
      status: 'error',
      retryCount: 0,
      error: (error as Error).message
    }
  }
}

/**
 * 等待执行结果
 */
export async function handleSessionWaitResult(
  request: SessionWaitResultRequest
): Promise<SessionExecutionResult> {
  const { sessionId, projectPath, cmdId, timeout = DEFAULT_RESULT_TIMEOUT } = request
  const resultFilePath = getSessionFilePath(projectPath, sessionId, RESULT_FILE)

  return new Promise((resolve) => {
    // 设置超时
    const timeoutId = setTimeout(() => {
      resultCallbacks.delete(cmdId)
      resolve({
        cmdId,
        status: 'timeout',
        error: '等待执行结果超时'
      })
    }, timeout)

    // 存储回调
    resultCallbacks.set(cmdId, { resolve, timeout: timeoutId })

    // 检查结果文件
    const checkResult = () => {
      try {
        if (fs.existsSync(resultFilePath)) {
          const content = fs.readFileSync(resultFilePath, 'utf-8')
          const result = JSON.parse(content)
          if (result.cmdId === cmdId) {
            clearTimeout(timeoutId)
            resultCallbacks.delete(cmdId)
            resolve(result as SessionExecutionResult)
            return true
          }
        }
      } catch {
        // 忽略读取错误
      }
      return false
    }

    // 立即检查一次
    if (checkResult()) return

    // 轮询检查
    const interval = setInterval(() => {
      if (checkResult()) {
        clearInterval(interval)
        return
      }

      // 检查是否已超时（通过 callback 是否还存在）
      if (!resultCallbacks.has(cmdId)) {
        clearInterval(interval)
      }
    }, 500)
  })
}

/**
 * 启动 Session 目录监听
 */
export function startSessionWatch(projectPath: string, window: BrowserWindow): void {
  const sessionsDir = getSessionsDir(projectPath)

  // 如果已经在监听，跳过
  if (activeWatchers.has(projectPath)) {
    return
  }

  // 确保目录存在
  if (!fs.existsSync(sessionsDir)) {
    fs.mkdirSync(sessionsDir, { recursive: true, mode: 0o700 })
  }

  try {
    const watcher = fs.watch(sessionsDir, async (eventType, filename) => {
      // 只关注 session-*.json 文件的变化
      if (filename && filename.endsWith(SESSION_FILE) && filename.startsWith('session-')) {
        // 获取最新的 Session 列表
        const response = await handleSessionList({ projectPath })

        // 发送变更事件到渲染进程
        const event: SessionChangeEvent = {
          sessions: response.sessions,
          timestamp: new Date().toISOString()
        }

        window.webContents.send(SESSION_CHANNELS.CHANGE, event)
      }
    })

    activeWatchers.set(projectPath, watcher)
    console.log(`[Session] Started watching: ${sessionsDir}`)
  } catch (error) {
    console.error(`[Session] Failed to watch: ${sessionsDir}`, error)
  }
}

/**
 * 停止 Session 目录监听
 */
export function stopSessionWatch(projectPath: string): void {
  const watcher = activeWatchers.get(projectPath)
  if (watcher) {
    watcher.close()
    activeWatchers.delete(projectPath)
    console.log(`[Session] Stopped watching: ${projectPath}`)
  }
}

/**
 * 停止所有 Session 监听
 */
export function stopAllSessionWatches(): void {
  for (const [projectPath, watcher] of activeWatchers) {
    watcher.close()
    console.log(`[Session] Stopped watching: ${projectPath}`)
  }
  activeWatchers.clear()
}
