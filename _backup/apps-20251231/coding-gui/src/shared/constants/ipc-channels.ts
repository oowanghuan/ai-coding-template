/**
 * IPC 通道名常量
 */

/** CLI 相关通道 */
export const CLI_CHANNELS = {
  EXECUTE: 'cli:execute',
  CANCEL: 'cli:cancel',
  OUTPUT: 'cli:output',
} as const

/** 项目相关通道 */
export const PROJECT_CHANNELS = {
  OPEN: 'project:open',
  STATE: 'project:state',
  STATE_CHANGE: 'project:state-change',
} as const

/** 文件相关通道 */
export const FILE_CHANNELS = {
  READ: 'file:read',
  WATCH: 'file:watch',
  CHANGE: 'file:change',
} as const

/** 审批相关通道 */
export const APPROVAL_CHANNELS = {
  SUBMIT: 'approval:submit',
  STATUS: 'approval:status',
} as const

/** Shell 相关通道 */
export const SHELL_CHANNELS = {
  OPEN_TERMINAL: 'shell:openTerminal',
} as const

/** Session 相关通道 (GUI-CLI 通信) */
export const SESSION_CHANNELS = {
  LIST: 'session:list',
  SEND_COMMAND: 'session:sendCommand',
  WAIT_RESULT: 'session:waitResult',
  CHANGE: 'session:change',
  START_WATCH: 'session:startWatch',
  STOP_WATCH: 'session:stopWatch',
} as const

/** 所有 IPC 通道 */
export const IPC_CHANNELS = {
  ...CLI_CHANNELS,
  ...PROJECT_CHANNELS,
  ...FILE_CHANNELS,
  ...APPROVAL_CHANNELS,
  ...SHELL_CHANNELS,
  ...SESSION_CHANNELS,
} as const
