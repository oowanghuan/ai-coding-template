/**
 * 错误码定义
 * 对应 40_DESIGN_FINAL.md 错误处理
 */

/** 错误码前缀 */
export const ERROR_PREFIX = {
  FS: 'E-FS',      // 文件系统
  IPC: 'E-IPC',    // IPC 通信
  CLI: 'E-CLI',    // CLI 执行
  SYNC: 'E-SYNC',  // 状态同步
  CFG: 'E-CFG',    // 配置
  VERIFY: 'E-VERIFY', // 校验
  GATE: 'E-GATE',  // Gate
} as const

/** 错误码定义 */
export const ERROR_CODES = {
  // 文件系统错误 E-FS-xxx
  FS_NOT_FOUND: 'E-FS-001',
  FS_PERMISSION: 'E-FS-002',
  FS_READ_FAILED: 'E-FS-003',
  FS_WRITE_FAILED: 'E-FS-004',
  FS_PATH_TRAVERSAL: 'E-FS-005',

  // IPC 错误 E-IPC-xxx
  IPC_INVALID_CHANNEL: 'E-IPC-001',
  IPC_INVALID_PARAMS: 'E-IPC-002',
  IPC_RATE_LIMITED: 'E-IPC-003',
  IPC_TIMEOUT: 'E-IPC-004',

  // CLI 错误 E-CLI-xxx
  CLI_NOT_FOUND: 'E-CLI-001',
  CLI_SPAWN_FAILED: 'E-CLI-002',
  CLI_EXECUTION_FAILED: 'E-CLI-003',
  CLI_TIMEOUT: 'E-CLI-004',
  CLI_CANCELLED: 'E-CLI-005',

  // 状态同步错误 E-SYNC-xxx
  SYNC_CONFLICT: 'E-SYNC-001',
  SYNC_STALE: 'E-SYNC-002',
  SYNC_RECOVERY_FAILED: 'E-SYNC-003',

  // 配置错误 E-CFG-xxx
  CFG_INVALID: 'E-CFG-001',
  CFG_MISSING: 'E-CFG-002',
  CFG_VERSION_MISMATCH: 'E-CFG-003',

  // 校验错误 E-VERIFY-xxx
  VERIFY_SCHEMA: 'E-VERIFY-001',
  VERIFY_PATH: 'E-VERIFY-002',
  VERIFY_PERMISSION: 'E-VERIFY-003',
  VERIFY_ARTIFACT: 'E-VERIFY-004',
  VERIFY_IDENTITY: 'E-VERIFY-005',

  // Gate 错误 E-GATE-xxx
  GATE_BLOCKED: 'E-GATE-001',
  GATE_PREREQUISITE: 'E-GATE-002',
  GATE_BYPASS_ATTEMPT: 'E-GATE-003',
} as const

export type ErrorCode = typeof ERROR_CODES[keyof typeof ERROR_CODES]

/** 创建标准错误对象 */
export function createError(
  code: ErrorCode,
  message: string,
  details?: Record<string, unknown>
): { code: ErrorCode; message: string; details?: Record<string, unknown> } {
  return { code, message, details }
}
