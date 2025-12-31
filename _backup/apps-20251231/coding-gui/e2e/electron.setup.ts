/**
 * Electron E2E 测试 Setup
 * 启动和关闭 Electron 应用
 */

import { _electron as electron, ElectronApplication, Page } from '@playwright/test'
import { resolve } from 'path'

let electronApp: ElectronApplication | null = null
let mainWindow: Page | null = null

/**
 * 启动 Electron 应用
 */
export async function launchElectronApp(): Promise<{ app: ElectronApplication; window: Page }> {
  // 先构建应用
  const appPath = resolve(__dirname, '..')

  electronApp = await electron.launch({
    args: [resolve(appPath, 'out/main/index.js')],
    cwd: appPath,
  })

  // 等待第一个窗口
  mainWindow = await electronApp.firstWindow()

  // 等待页面加载完成
  await mainWindow.waitForLoadState('domcontentloaded')

  return { app: electronApp, window: mainWindow }
}

/**
 * 关闭 Electron 应用
 */
export async function closeElectronApp(): Promise<void> {
  if (electronApp) {
    await electronApp.close()
    electronApp = null
    mainWindow = null
  }
}

/**
 * 获取当前应用实例
 */
export function getElectronApp(): ElectronApplication | null {
  return electronApp
}

/**
 * 获取主窗口
 */
export function getMainWindow(): Page | null {
  return mainWindow
}
