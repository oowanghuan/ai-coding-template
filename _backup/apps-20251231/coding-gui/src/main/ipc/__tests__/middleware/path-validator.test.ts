/**
 * Path Validator Middleware 单元测试
 * 对应 60_TEST_PLAN.md PV-001 ~ PV-004
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import {
  validatePath,
  validateProjectPath,
  setAllowedBasePaths,
  addAllowedBasePath,
  createPathValidatorMiddleware
} from '../../middleware/path-validator'

describe('Path Validator Middleware', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // 重置允许的路径
    setAllowedBasePaths([])
  })

  describe('PV-001: 项目内路径通过', () => {
    it('should pass valid absolute path', () => {
      const result = validatePath('/home/user/project')

      expect(result).toBe('/home/user/project')
    })

    it('should pass path within base directory', () => {
      const basePath = '/home/user/project'
      const result = validatePath('src/main.ts', basePath)

      expect(result).toBe('/home/user/project/src/main.ts')
    })

    it('should pass path when in allowed directories', () => {
      setAllowedBasePaths(['/home/user/projects'])

      const result = validatePath('/home/user/projects/myapp/src/index.ts')

      expect(result).toBe('/home/user/projects/myapp/src/index.ts')
    })
  })

  describe('PV-002: 路径穿越拒绝 (../)', () => {
    it('should reject path containing ../', () => {
      expect(() => validatePath('../etc/passwd')).toThrow()
    })

    it('should reject path with embedded ../', () => {
      expect(() => validatePath('/home/user/../root/secret')).toThrow()
    })

    it('should reject deep traversal attempts', () => {
      expect(() => validatePath('../../../../../../etc/passwd')).toThrow()
    })
  })

  describe('PV-003: 绝对路径外部拒绝', () => {
    it('should reject path escaping base directory', () => {
      const basePath = '/home/user/project'

      expect(() => validatePath('/etc/passwd', basePath)).toThrow()
    })

    it('should reject path not in allowed directories', () => {
      setAllowedBasePaths(['/home/user/projects'])

      expect(() => validatePath('/etc/passwd')).toThrow()
    })

    it('should reject relative path without base', () => {
      expect(() => validatePath('relative/path')).toThrow()
    })
  })

  describe('PV-004: 危险模式检测', () => {
    it('should reject /etc/ paths', () => {
      expect(() => validatePath('/etc/passwd')).toThrow()
    })

    it('should reject /usr/ paths', () => {
      expect(() => validatePath('/usr/bin/bash')).toThrow()
    })

    it('should reject /bin/ paths', () => {
      expect(() => validatePath('/bin/sh')).toThrow()
    })

    it('should reject /sbin/ paths', () => {
      expect(() => validatePath('/sbin/init')).toThrow()
    })

    it('should reject /var/log/ paths', () => {
      expect(() => validatePath('/var/log/syslog')).toThrow()
    })

    it('should reject ~ home directory reference', () => {
      expect(() => validatePath('~/secret')).toThrow()
    })

    it('should reject NULL byte injection', () => {
      expect(() => validatePath('/home/user/file\0.txt')).toThrow()
    })
  })

  describe('validateProjectPath', () => {
    it('should validate and return normalized path', () => {
      const result = validateProjectPath('/home/user/project')

      expect(result).toBe('/home/user/project')
    })

    it('should normalize path with trailing slash', () => {
      const result = validateProjectPath('/home/user/project/')

      expect(result).toBe('/home/user/project')
    })
  })

  describe('setAllowedBasePaths / addAllowedBasePath', () => {
    it('should set allowed base paths', () => {
      setAllowedBasePaths(['/allowed/path1', '/allowed/path2'])

      expect(() => validatePath('/allowed/path1/file.txt')).not.toThrow()
      expect(() => validatePath('/allowed/path2/file.txt')).not.toThrow()
      expect(() => validatePath('/not/allowed/file.txt')).toThrow()
    })

    it('should add to allowed base paths', () => {
      setAllowedBasePaths(['/allowed/path1'])
      addAllowedBasePath('/allowed/path2')

      expect(() => validatePath('/allowed/path1/file.txt')).not.toThrow()
      expect(() => validatePath('/allowed/path2/file.txt')).not.toThrow()
    })
  })

  describe('createPathValidatorMiddleware', () => {
    it('should validate projectPath field', async () => {
      const middleware = createPathValidatorMiddleware()
      const next = vi.fn().mockResolvedValue('success')

      const args = [{
        projectPath: '/home/user/project',
        command: '/help'
      }]

      await middleware('cli:execute', args, next)

      expect(next).toHaveBeenCalled()
      expect((args[0] as any).projectPath).toBe('/home/user/project')
    })

    it('should validate path field relative to projectPath', async () => {
      const middleware = createPathValidatorMiddleware()
      const next = vi.fn().mockResolvedValue('success')

      const args = [{
        projectPath: '/home/user/project',
        path: 'src/index.ts'
      }]

      await middleware('file:read', args, next)

      expect(next).toHaveBeenCalled()
      expect((args[0] as any).path).toBe('/home/user/project/src/index.ts')
    })

    it('should reject path traversal in middleware', async () => {
      const middleware = createPathValidatorMiddleware()
      const next = vi.fn()

      const args = [{
        projectPath: '/home/user/project',
        path: '../../../etc/passwd'
      }]

      await expect(middleware('file:read', args, next)).rejects.toThrow()
      expect(next).not.toHaveBeenCalled()
    })

    it('should pass through when no path fields', async () => {
      const middleware = createPathValidatorMiddleware()
      const next = vi.fn().mockResolvedValue('success')

      const args = [{ someField: 'value' }]

      await middleware('some:channel', args, next)

      expect(next).toHaveBeenCalled()
    })

    it('should handle empty args', async () => {
      const middleware = createPathValidatorMiddleware()
      const next = vi.fn().mockResolvedValue('success')

      await middleware('some:channel', [], next)

      expect(next).toHaveBeenCalled()
    })
  })
})
