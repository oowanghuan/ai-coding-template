/**
 * 路径验证中间件
 * CODE-003: PathValidator - 目录穿越防护
 */

import { resolve, normalize, isAbsolute } from 'path'
import { ERROR_CODES, createError } from '../../../shared/types/error.types'

// 危险路径模式
const DANGEROUS_PATTERNS = [
  /\.\./,           // 父目录引用
  /^\/etc\//,       // 系统配置
  /^\/usr\//,       // 系统程序
  /^\/bin\//,       // 系统二进制
  /^\/sbin\//,      // 系统管理二进制
  /^\/var\/log\//,  // 系统日志
  /^~\//,           // 用户目录引用
  /\0/,             // NULL 字节
]

// 允许的基础目录（运行时设置）
let allowedBasePaths: string[] = []

/**
 * 设置允许的基础目录
 */
export function setAllowedBasePaths(paths: string[]): void {
  allowedBasePaths = paths.map(p => normalize(resolve(p)))
}

/**
 * 添加允许的基础目录
 */
export function addAllowedBasePath(path: string): void {
  allowedBasePaths.push(normalize(resolve(path)))
}

/**
 * 验证路径安全性
 * @param targetPath 目标路径
 * @param basePath 可选的基础路径约束
 * @returns 规范化后的绝对路径
 */
export function validatePath(targetPath: string, basePath?: string): string {
  // 检查危险模式
  for (const pattern of DANGEROUS_PATTERNS) {
    if (pattern.test(targetPath)) {
      throw createError(
        ERROR_CODES.FS_PATH_TRAVERSAL,
        `Path contains dangerous pattern: ${targetPath}`,
        { pattern: pattern.toString() }
      )
    }
  }

  // 规范化路径
  let normalizedPath: string
  if (basePath) {
    const baseResolved = normalize(resolve(basePath))
    normalizedPath = normalize(resolve(baseResolved, targetPath))

    // 确保路径在基础目录内
    if (!normalizedPath.startsWith(baseResolved)) {
      throw createError(
        ERROR_CODES.FS_PATH_TRAVERSAL,
        `Path escapes base directory: ${targetPath}`,
        { basePath: baseResolved, resolved: normalizedPath }
      )
    }
  } else {
    // 必须是绝对路径
    if (!isAbsolute(targetPath)) {
      throw createError(
        ERROR_CODES.VERIFY_PATH,
        `Path must be absolute: ${targetPath}`
      )
    }
    normalizedPath = normalize(resolve(targetPath))
  }

  // 检查是否在允许的基础目录内
  if (allowedBasePaths.length > 0) {
    const isAllowed = allowedBasePaths.some(base =>
      normalizedPath.startsWith(base)
    )
    if (!isAllowed) {
      throw createError(
        ERROR_CODES.FS_PATH_TRAVERSAL,
        `Path not in allowed directories: ${normalizedPath}`,
        { allowed: allowedBasePaths }
      )
    }
  }

  return normalizedPath
}

/**
 * 验证项目路径
 * 项目路径必须包含 .claude 目录
 */
export function validateProjectPath(projectPath: string): string {
  const validated = validatePath(projectPath)
  // 这里可以添加额外的项目路径验证逻辑
  return validated
}

/**
 * 创建路径验证中间件
 */
export function createPathValidatorMiddleware() {
  return async (
    channel: string,
    args: unknown[],
    next: () => Promise<unknown>
  ): Promise<unknown> => {
    // args[0] 是 IpcMainInvokeEvent，args[1] 才是请求数据
    const data = args[1] as Record<string, unknown> | undefined

    if (!data) {
      return next()
    }

    // 验证 projectPath 字段
    if (typeof data.projectPath === 'string') {
      data.projectPath = validateProjectPath(data.projectPath)
    }

    // 验证 path 字段（相对于 projectPath）
    if (typeof data.path === 'string' && typeof data.projectPath === 'string') {
      data.path = validatePath(data.path, data.projectPath)
    } else if (typeof data.path === 'string') {
      data.path = validatePath(data.path)
    }

    return next()
  }
}
