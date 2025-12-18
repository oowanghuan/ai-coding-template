/**
 * useIpc Composable 单元测试
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useIpc, useProjectIpc, useCliIpc, useFileIpc, useApprovalIpc } from '../useIpc'

// Mock window.electronAPI
const mockInvoke = vi.fn()
const mockOn = vi.fn()

vi.stubGlobal('window', {
  electronAPI: {
    invoke: mockInvoke,
    on: mockOn
  }
})

describe('useIpc', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Initial State', () => {
    it('should have isLoading false initially', () => {
      const { isLoading } = useIpc<{}, {}>('test:channel')
      expect(isLoading.value).toBe(false)
    })

    it('should have null error initially', () => {
      const { error } = useIpc<{}, {}>('test:channel')
      expect(error.value).toBeNull()
    })

    it('should have null data initially', () => {
      const { data } = useIpc<{}, {}>('test:channel')
      expect(data.value).toBeNull()
    })
  })

  describe('invoke', () => {
    it('should invoke electronAPI with correct channel', async () => {
      mockInvoke.mockResolvedValue({ result: 'success' })

      const { invoke } = useIpc<{ param: string }, { result: string }>('test:channel')
      await invoke({ param: 'value' })

      expect(mockInvoke).toHaveBeenCalledWith('test:channel', { param: 'value' })
    })

    it('should set isLoading during invoke', async () => {
      let loadingDuringCall = false
      mockInvoke.mockImplementation(() => {
        return new Promise(resolve => {
          setTimeout(() => resolve({ result: 'success' }), 10)
        })
      })

      const { invoke, isLoading } = useIpc<{}, {}>('test:channel')

      const invokePromise = invoke({})

      // Check loading immediately after invoke
      expect(isLoading.value).toBe(true)

      await invokePromise

      expect(isLoading.value).toBe(false)
    })

    it('should set data on success', async () => {
      mockInvoke.mockResolvedValue({ result: 'success' })

      const { invoke, data } = useIpc<{}, { result: string }>('test:channel')
      await invoke({})

      expect(data.value).toEqual({ result: 'success' })
    })

    it('should return response on success', async () => {
      mockInvoke.mockResolvedValue({ result: 'success' })

      const { invoke } = useIpc<{}, { result: string }>('test:channel')
      const response = await invoke({})

      expect(response).toEqual({ result: 'success' })
    })

    it('should set error on failure', async () => {
      mockInvoke.mockRejectedValue(new Error('Network error'))

      const { invoke, error } = useIpc<{}, {}>('test:channel')
      await invoke({})

      expect(error.value).not.toBeNull()
      expect(error.value?.code).toBe('E-IPC-UNKNOWN')
      expect(error.value?.message).toBe('Network error')
    })

    it('should return null on failure', async () => {
      mockInvoke.mockRejectedValue(new Error('Network error'))

      const { invoke } = useIpc<{}, {}>('test:channel')
      const response = await invoke({})

      expect(response).toBeNull()
    })

    it('should clear previous error on new invoke', async () => {
      mockInvoke
        .mockRejectedValueOnce(new Error('First error'))
        .mockResolvedValueOnce({ result: 'success' })

      const { invoke, error } = useIpc<{}, {}>('test:channel')

      await invoke({})
      expect(error.value).not.toBeNull()

      await invoke({})
      expect(error.value).toBeNull()
    })
  })

  describe('reset', () => {
    it('should reset all state', async () => {
      mockInvoke.mockResolvedValue({ result: 'data' })

      const { invoke, isLoading, error, data, reset } = useIpc<{}, {}>('test:channel')

      await invoke({})
      expect(data.value).not.toBeNull()

      reset()

      expect(isLoading.value).toBe(false)
      expect(error.value).toBeNull()
      expect(data.value).toBeNull()
    })
  })
})

describe('useProjectIpc', () => {
  it('should return open and state ipc handlers', () => {
    const projectIpc = useProjectIpc()

    expect(projectIpc.open).toBeDefined()
    expect(projectIpc.open.invoke).toBeDefined()
    expect(projectIpc.state).toBeDefined()
    expect(projectIpc.state.invoke).toBeDefined()
  })
})

describe('useCliIpc', () => {
  it('should return execute and cancel ipc handlers', () => {
    const cliIpc = useCliIpc()

    expect(cliIpc.execute).toBeDefined()
    expect(cliIpc.execute.invoke).toBeDefined()
    expect(cliIpc.cancel).toBeDefined()
    expect(cliIpc.cancel.invoke).toBeDefined()
  })
})

describe('useFileIpc', () => {
  it('should return read ipc handler', () => {
    const fileIpc = useFileIpc()

    expect(fileIpc.read).toBeDefined()
    expect(fileIpc.read.invoke).toBeDefined()
  })
})

describe('useApprovalIpc', () => {
  it('should return submit and status ipc handlers', () => {
    const approvalIpc = useApprovalIpc()

    expect(approvalIpc.submit).toBeDefined()
    expect(approvalIpc.submit.invoke).toBeDefined()
    expect(approvalIpc.status).toBeDefined()
    expect(approvalIpc.status.invoke).toBeDefined()
  })
})
