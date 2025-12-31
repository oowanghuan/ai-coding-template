/**
 * Shell 相关 IPC 处理器
 * INT-002: 打开终端功能
 */

import { clipboard } from 'electron'
import { spawn } from 'child_process'
import { platform } from 'os'
import { stat } from 'fs/promises'
import type { ShellOpenTerminalRequest, ShellOpenTerminalResponse } from '../../../shared/types/ipc.types'
import { ERROR_CODES, createError } from '../../../shared/types/error.types'

/**
 * 打开系统终端
 */
export async function handleShellOpenTerminal(
  request: ShellOpenTerminalRequest
): Promise<ShellOpenTerminalResponse> {
  const { cwd, prompt } = request

  // 验证工作目录
  try {
    const cwdStat = await stat(cwd)
    if (!cwdStat.isDirectory()) {
      throw createError(
        ERROR_CODES.FS_NOT_FOUND,
        `Path is not a directory: ${cwd}`
      )
    }
  } catch (error) {
    if ((error as { code?: string }).code?.startsWith('E-')) {
      throw error
    }
    throw createError(
      ERROR_CODES.FS_NOT_FOUND,
      `Directory not found: ${cwd}`
    )
  }

  // 复制 prompt 到剪贴板
  if (prompt) {
    clipboard.writeText(prompt)
  }

  // 根据平台打开终端
  const os = platform()

  try {
    if (os === 'darwin') {
      // macOS: 打开 Terminal.app 并 cd 到目录
      const script = `
        tell application "Terminal"
          if not running then
            activate
            delay 0.5
          end if
          do script "cd ${escapeAppleScript(cwd)}"
          activate
        end tell
      `
      spawn('osascript', ['-e', script], { detached: true })
    } else if (os === 'win32') {
      // Windows: 打开 cmd
      spawn('cmd', ['/c', 'start', 'cmd', '/k', `cd /d "${cwd}"`], {
        detached: true,
        shell: true
      })
    } else {
      // Linux: 尝试常见终端
      const terminals = [
        { cmd: 'gnome-terminal', args: ['--working-directory', cwd] },
        { cmd: 'konsole', args: ['--workdir', cwd] },
        { cmd: 'xfce4-terminal', args: ['--working-directory', cwd] },
        { cmd: 'xterm', args: ['-e', `cd "${cwd}" && $SHELL`] }
      ]

      let launched = false
      for (const terminal of terminals) {
        try {
          spawn(terminal.cmd, terminal.args, { detached: true })
          launched = true
          break
        } catch {
          continue
        }
      }

      if (!launched) {
        throw createError(
          ERROR_CODES.CLI_NOT_FOUND,
          'No supported terminal found'
        )
      }
    }

    return {
      success: true,
      promptCopied: !!prompt
    }
  } catch (error) {
    if ((error as { code?: string }).code?.startsWith('E-')) {
      throw error
    }
    throw createError(
      ERROR_CODES.CLI_EXEC_FAILED,
      `Failed to open terminal: ${(error as Error).message}`
    )
  }
}

/**
 * 转义 AppleScript 字符串
 */
function escapeAppleScript(str: string): string {
  return str.replace(/\\/g, '\\\\').replace(/"/g, '\\"')
}
