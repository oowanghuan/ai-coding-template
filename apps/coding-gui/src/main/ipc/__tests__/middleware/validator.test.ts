/**
 * Validator Middleware 单元测试
 * 对应 60_TEST_PLAN.md VL-001 ~ VL-004
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import {
  validateIpcRequest,
  createValidatorMiddleware,
  cliExecuteSchema,
  cliCancelSchema
} from '../../middleware/validator'

describe('Validator Middleware', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('VL-001: 有效输入通过', () => {
    it('should pass valid cli:execute request', () => {
      const validRequest = {
        command: '/help',
        projectPath: '/home/user/project',
        mode: 'print'
      }

      const result = validateIpcRequest<typeof validRequest>('cli:execute', validRequest)

      expect(result.command).toBe('/help')
      expect(result.projectPath).toBe('/home/user/project')
      expect(result.mode).toBe('print')
    })

    it('should pass valid cli:cancel request', () => {
      const validRequest = {
        executionId: '550e8400-e29b-41d4-a716-446655440000'
      }

      const result = validateIpcRequest<typeof validRequest>('cli:cancel', validRequest)

      expect(result.executionId).toBe('550e8400-e29b-41d4-a716-446655440000')
    })

    it('should pass valid project:open request', () => {
      const validRequest = {
        path: '/home/user/project'
      }

      const result = validateIpcRequest<typeof validRequest>('project:open', validRequest)

      expect(result.path).toBe('/home/user/project')
    })
  })

  describe('VL-002: 无效输入拒绝', () => {
    it('should reject empty command', () => {
      const invalidRequest = {
        command: '',
        projectPath: '/home/user/project'
      }

      expect(() => validateIpcRequest('cli:execute', invalidRequest)).toThrow()
    })

    it('should reject command exceeding max length', () => {
      const invalidRequest = {
        command: 'x'.repeat(10001),
        projectPath: '/home/user/project'
      }

      expect(() => validateIpcRequest('cli:execute', invalidRequest)).toThrow()
    })

    it('should reject invalid UUID for executionId', () => {
      const invalidRequest = {
        executionId: 'not-a-valid-uuid'
      }

      expect(() => validateIpcRequest('cli:cancel', invalidRequest)).toThrow()
    })
  })

  describe('VL-003: 缺少必填字段', () => {
    it('should reject missing command field', () => {
      const invalidRequest = {
        projectPath: '/home/user/project'
      }

      expect(() => validateIpcRequest('cli:execute', invalidRequest)).toThrow()
    })

    it('should reject missing projectPath field', () => {
      const invalidRequest = {
        command: '/help'
      }

      expect(() => validateIpcRequest('cli:execute', invalidRequest)).toThrow()
    })

    it('should reject empty object for project:open', () => {
      expect(() => validateIpcRequest('project:open', {})).toThrow()
    })
  })

  describe('VL-004: 类型不匹配', () => {
    it('should reject number as command', () => {
      const invalidRequest = {
        command: 123,
        projectPath: '/home/user/project'
      }

      expect(() => validateIpcRequest('cli:execute', invalidRequest)).toThrow()
    })

    it('should reject array as projectPath', () => {
      const invalidRequest = {
        command: '/help',
        projectPath: ['/home/user/project']
      }

      expect(() => validateIpcRequest('cli:execute', invalidRequest)).toThrow()
    })

    it('should reject invalid mode value', () => {
      const invalidRequest = {
        command: '/help',
        projectPath: '/home/user/project',
        mode: 'invalid_mode'
      }

      expect(() => validateIpcRequest('cli:execute', invalidRequest)).toThrow()
    })
  })

  describe('createValidatorMiddleware', () => {
    it('should validate and call next on valid input', async () => {
      const middleware = createValidatorMiddleware()
      const next = vi.fn().mockResolvedValue('success')

      const args = [{
        command: '/help',
        projectPath: '/home/user/project',
        mode: 'print'
      }]

      const result = await middleware('cli:execute', args, next)

      expect(next).toHaveBeenCalled()
      expect(result).toBe('success')
    })

    it('should throw error on invalid input', async () => {
      const middleware = createValidatorMiddleware()
      const next = vi.fn()

      const args = [{
        command: '',
        projectPath: '/home/user/project'
      }]

      await expect(middleware('cli:execute', args, next)).rejects.toThrow()
      expect(next).not.toHaveBeenCalled()
    })

    it('should strip unknown fields', async () => {
      const middleware = createValidatorMiddleware()
      const next = vi.fn().mockResolvedValue('success')

      const args = [{
        command: '/help',
        projectPath: '/home/user/project',
        unknownField: 'should be removed'
      }]

      await middleware('cli:execute', args, next)

      expect(args[0]).not.toHaveProperty('unknownField')
    })

    it('should apply default values', async () => {
      const middleware = createValidatorMiddleware()
      const next = vi.fn().mockResolvedValue('success')

      const args = [{
        command: '/help',
        projectPath: '/home/user/project'
        // mode not specified, should default to 'print'
      }]

      await middleware('cli:execute', args, next)

      expect((args[0] as any).mode).toBe('print')
    })
  })

  describe('approval:submit schema', () => {
    it('should validate approve action', () => {
      const validRequest = {
        stepId: 'KICK-001',
        featureId: 'coding-GUI',
        action: 'approve'
      }

      const result = validateIpcRequest<typeof validRequest>('approval:submit', validRequest)

      expect(result.action).toBe('approve')
    })

    it('should validate reject action', () => {
      const validRequest = {
        stepId: 'KICK-001',
        featureId: 'coding-GUI',
        action: 'reject',
        note: 'Needs revision'
      }

      const result = validateIpcRequest<typeof validRequest>('approval:submit', validRequest)

      expect(result.action).toBe('reject')
      expect(result.note).toBe('Needs revision')
    })

    it('should reject invalid action', () => {
      const invalidRequest = {
        stepId: 'KICK-001',
        featureId: 'coding-GUI',
        action: 'invalid'
      }

      expect(() => validateIpcRequest('approval:submit', invalidRequest)).toThrow()
    })
  })
})
