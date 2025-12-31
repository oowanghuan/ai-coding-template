/**
 * IPC 输入验证中间件
 * CODE-003: IpcValidator - Joi Schema 校验
 */

import Joi from 'joi'
import { ERROR_CODES, createError } from '../../../shared/types/error.types'

// ============================================================
// Schema 定义
// ============================================================

/** CLI 执行请求 Schema */
export const cliExecuteSchema = Joi.object({
  command: Joi.string().required().min(1).max(10000),
  projectPath: Joi.string().required().min(1).max(1000),
  featureId: Joi.string().optional().max(100),
  stepId: Joi.string().optional().max(100),
  mode: Joi.string().valid('print', 'full_interactive').default('print')
})

/** CLI 取消请求 Schema */
export const cliCancelSchema = Joi.object({
  executionId: Joi.string().required().uuid()
})

/** 项目打开请求 Schema */
export const projectOpenSchema = Joi.object({
  path: Joi.string().required().min(1).max(1000)
})

/** 文件读取请求 Schema */
export const fileReadSchema = Joi.object({
  path: Joi.string().required().min(1).max(1000),
  projectPath: Joi.string().optional().min(1).max(1000),
  maxSize: Joi.number().optional().min(1).max(10 * 1024 * 1024) // 10MB
})

/** 审批提交请求 Schema */
export const approvalSubmitSchema = Joi.object({
  stepId: Joi.string().required().max(100),
  featureId: Joi.string().required().max(100),
  action: Joi.string().valid('approve', 'reject').required(),
  note: Joi.string().optional().max(1000)
})

/** 审批状态查询请求 Schema */
export const approvalStatusSchema = Joi.object({
  featureId: Joi.string().required().max(100)
})

// Schema 映射
const schemaMap: Record<string, Joi.Schema> = {
  'cli:execute': cliExecuteSchema,
  'cli:cancel': cliCancelSchema,
  'project:open': projectOpenSchema,
  'file:read': fileReadSchema,
  'approval:submit': approvalSubmitSchema,
  'approval:status': approvalStatusSchema
}

// ============================================================
// 验证函数
// ============================================================

/**
 * 验证 IPC 请求参数
 * @param channel IPC 通道名
 * @param data 请求数据
 * @returns 验证后的数据或抛出错误
 */
export function validateIpcRequest<T>(channel: string, data: unknown): T {
  const schema = schemaMap[channel]

  if (!schema) {
    // 无需验证的通道
    return data as T
  }

  const { error, value } = schema.validate(data, {
    abortEarly: false,
    stripUnknown: true
  })

  if (error) {
    const details = error.details.map(d => ({
      field: d.path.join('.'),
      message: d.message
    }))

    throw createError(
      ERROR_CODES.VERIFY_SCHEMA,
      `Validation failed: ${error.details.map(d => d.message).join(', ')}`,
      { details }
    )
  }

  return value as T
}

/**
 * 创建验证中间件
 */
export function createValidatorMiddleware() {
  return async (
    channel: string,
    args: unknown[],
    next: () => Promise<unknown>
  ): Promise<unknown> => {
    // args[0] 是 IpcMainInvokeEvent，args[1] 才是请求数据
    if (args.length > 1) {
      args[1] = validateIpcRequest(channel, args[1])
    }
    return next()
  }
}
