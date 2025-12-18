/**
 * SessionChannel 服务
 * 提供 GUI-CLI Session 通信能力
 */

import { ref, computed, type Ref } from 'vue'
import type {
  Session,
  SessionListRequest,
  SessionListResponse,
  SessionSendCommandRequest,
  SessionSendCommandResponse,
  SessionWaitResultRequest,
  SessionExecutionResult,
  SessionChangeEvent
} from '../../shared/types/ipc.types'
import { SESSION_CHANNELS } from '../../shared/constants/ipc-channels'

// IPC 接口（使用 preload 中定义的类型）
// 注意：实际类型在 preload/index.ts 中通过 contextBridge 暴露

/**
 * 命令上下文
 */
export interface CommandContext {
  phaseId?: number
  featureId?: string
  stepId?: string
}

/**
 * 命令结果
 */
export interface CommandResult {
  cmdId: string
  status: 'sent' | 'received' | 'duplicate' | 'timeout' | 'error'
  retryCount: number
  error?: string
}

/**
 * SessionChannel 类
 * 管理与 CLI Session 的通信
 */
class SessionChannel {
  // 当前项目路径
  private projectPath: Ref<string | null> = ref(null)

  // Session 列表
  private sessions: Ref<Session[]> = ref([])

  // 当前连接的 Session
  private currentSessionId: Ref<string | null> = ref(null)

  // 变更回调
  private changeCallbacks: Set<(sessions: Session[]) => void> = new Set()

  // 是否已初始化监听
  private isWatching = false

  // IPC 事件取消订阅函数
  private unsubscribeChange: (() => void) | null = null

  /**
   * 是否已连接
   */
  get isConnected(): boolean {
    return this.currentSessionId.value !== null
  }

  /**
   * 当前 Session
   */
  get currentSession(): Session | null {
    if (!this.currentSessionId.value) return null
    return this.sessions.value.find(s => s.id === this.currentSessionId.value) || null
  }

  /**
   * 所有 Session（响应式）
   */
  get allSessions(): Ref<Session[]> {
    return this.sessions
  }

  /**
   * 当前 Session ID（响应式）
   */
  get connectedSessionId(): Ref<string | null> {
    return this.currentSessionId
  }

  /**
   * 初始化
   */
  async init(projectPath: string): Promise<void> {
    this.projectPath.value = projectPath
    await this.refreshSessions()
    this.startWatch()
  }

  /**
   * 销毁
   */
  destroy(): void {
    this.stopWatch()
    this.changeCallbacks.clear()
    this.sessions.value = []
    this.currentSessionId.value = null
    this.projectPath.value = null
  }

  /**
   * 刷新 Session 列表
   */
  async refreshSessions(): Promise<Session[]> {
    if (!this.projectPath.value) {
      return []
    }

    try {
      const request: SessionListRequest = {
        projectPath: this.projectPath.value
      }

      const response = await window.electronAPI?.invoke(
        SESSION_CHANNELS.LIST,
        request
      ) as SessionListResponse

      this.sessions.value = response?.sessions || []

      // 如果当前连接的 Session 不在列表中或已断开，清除连接
      if (this.currentSessionId.value) {
        const current = this.sessions.value.find(s => s.id === this.currentSessionId.value)
        if (!current || current.status === 'disconnected') {
          this.currentSessionId.value = null
        }
      }

      return this.sessions.value
    } catch (error) {
      console.error('[SessionChannel] Failed to list sessions:', error)
      return []
    }
  }

  /**
   * 连接到指定 Session
   */
  connect(sessionId: string): boolean {
    const session = this.sessions.value.find(s => s.id === sessionId)

    if (!session) {
      console.warn(`[SessionChannel] Session not found: ${sessionId}`)
      return false
    }

    if (session.status === 'disconnected') {
      console.warn(`[SessionChannel] Session is disconnected: ${sessionId}`)
      return false
    }

    this.currentSessionId.value = sessionId
    console.log(`[SessionChannel] Connected to session: ${sessionId}`)
    return true
  }

  /**
   * 断开连接
   */
  disconnect(): void {
    if (this.currentSessionId.value) {
      console.log(`[SessionChannel] Disconnected from session: ${this.currentSessionId.value}`)
      this.currentSessionId.value = null
    }
  }

  /**
   * 发送命令
   */
  async sendCommand(command: string, context?: CommandContext): Promise<CommandResult> {
    if (!this.isConnected || !this.projectPath.value || !this.currentSessionId.value) {
      return {
        cmdId: '',
        status: 'error',
        retryCount: 0,
        error: '未连接到 CLI Session'
      }
    }

    try {
      const request: SessionSendCommandRequest = {
        sessionId: this.currentSessionId.value,
        projectPath: this.projectPath.value,
        command,
        context
      }

      const response = await window.electronAPI?.invoke(
        SESSION_CHANNELS.SEND_COMMAND,
        request
      ) as SessionSendCommandResponse

      return response || {
        cmdId: '',
        status: 'error',
        retryCount: 0,
        error: 'IPC 调用失败'
      }
    } catch (error) {
      return {
        cmdId: '',
        status: 'error',
        retryCount: 0,
        error: (error as Error).message
      }
    }
  }

  /**
   * 等待执行结果
   */
  async waitForResult(cmdId: string, timeout?: number): Promise<SessionExecutionResult> {
    if (!this.projectPath.value || !this.currentSessionId.value) {
      return {
        cmdId,
        status: 'failed',
        error: '未连接到 CLI Session'
      }
    }

    try {
      const request: SessionWaitResultRequest = {
        sessionId: this.currentSessionId.value,
        projectPath: this.projectPath.value,
        cmdId,
        timeout
      }

      const response = await window.electronAPI?.invoke(
        SESSION_CHANNELS.WAIT_RESULT,
        request
      ) as SessionExecutionResult

      return response || {
        cmdId,
        status: 'failed',
        error: 'IPC 调用失败'
      }
    } catch (error) {
      return {
        cmdId,
        status: 'failed',
        error: (error as Error).message
      }
    }
  }

  /**
   * 监听 Session 变化
   */
  onSessionChange(callback: (sessions: Session[]) => void): () => void {
    this.changeCallbacks.add(callback)
    return () => {
      this.changeCallbacks.delete(callback)
    }
  }

  /**
   * 启动目录监听
   */
  private startWatch(): void {
    if (this.isWatching || !this.projectPath.value) return

    // 启动主进程的文件监听
    window.electronAPI?.invoke(SESSION_CHANNELS.START_WATCH, {
      projectPath: this.projectPath.value
    })

    // 监听变更事件
    const handleChange = (_event: unknown, data: unknown) => {
      const event = data as SessionChangeEvent
      this.sessions.value = event.sessions

      // 检查当前连接状态
      if (this.currentSessionId.value) {
        const current = this.sessions.value.find(s => s.id === this.currentSessionId.value)
        if (!current || current.status === 'disconnected') {
          this.currentSessionId.value = null
        }
      }

      // 通知回调
      this.changeCallbacks.forEach(cb => cb(event.sessions))
    }

    // 订阅变更事件，保存取消订阅函数
    this.unsubscribeChange = window.electronAPI?.on(
      SESSION_CHANNELS.CHANGE as 'session:change',
      handleChange
    ) || null

    this.isWatching = true
    console.log('[SessionChannel] Started watching')
  }

  /**
   * 停止目录监听
   */
  private stopWatch(): void {
    if (!this.isWatching || !this.projectPath.value) return

    // 取消事件订阅
    if (this.unsubscribeChange) {
      this.unsubscribeChange()
      this.unsubscribeChange = null
    }

    // 停止主进程的文件监听
    window.electronAPI?.invoke(SESSION_CHANNELS.STOP_WATCH, {
      projectPath: this.projectPath.value
    })

    this.isWatching = false
    console.log('[SessionChannel] Stopped watching')
  }
}

// 单例实例
let instance: SessionChannel | null = null

/**
 * 获取 SessionChannel 单例
 */
export function useSessionChannel(): SessionChannel {
  if (!instance) {
    instance = new SessionChannel()
  }
  return instance
}

/**
 * 创建新的 SessionChannel 实例（用于测试）
 */
export function createSessionChannel(): SessionChannel {
  return new SessionChannel()
}

export default useSessionChannel
