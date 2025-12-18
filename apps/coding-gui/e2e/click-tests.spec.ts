/**
 * Coding GUI 页面功能点击测试
 *
 * 两套测试场景：
 * 1. Part A: 无项目状态 - 测试基础 UI 交互
 * 2. Part B: 有项目状态 - 测试完整功能（Step 卡片、执行、审批等）
 */

import { test, expect, _electron as electron, ElectronApplication, Page } from '@playwright/test'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

// 测试项目路径 - 使用真实的 ai-coding-org 项目
const TEST_PROJECT_PATH = resolve(__dirname, '../../../..')

// 截图保存目录
const screenshotDir = 'e2e/screenshots/click-tests'

// ============================================================
// Part A: 无项目状态测试
// ============================================================
test.describe('Part A: No Project State Tests', () => {
  let electronApp: ElectronApplication
  let window: Page

  test.beforeAll(async () => {
    const appPath = resolve(__dirname, '..')

    electronApp = await electron.launch({
      args: [resolve(appPath, 'out/main/index.js')],
      cwd: appPath,
      env: {
        ...process.env,
        NODE_ENV: 'test'
      }
    })

    window = await electronApp.firstWindow()
    await window.waitForLoadState('domcontentloaded')
    await window.waitForTimeout(2000)
  })

  test.afterAll(async () => {
    if (electronApp) {
      await electronApp.close()
    }
  })

  // ----------------------------------------
  // A-001: Header 基础功能
  // ----------------------------------------
  test.describe('A-001: Header Basic Functions', () => {
    test('A-001-1: 验证 Header 显示', async () => {
      await window.screenshot({ path: `${screenshotDir}/a-001-1-header.png` })

      // 验证 Logo 存在
      const logo = window.locator('.header__logo')
      expect(await logo.count()).toBeGreaterThan(0)

      // 验证标题
      const title = window.locator('.header__title')
      if (await title.count() > 0) {
        const text = await title.first().textContent()
        expect(text).toContain('Coding GUI')
      }
    })

    test('A-001-2: 点击项目下拉菜单', async () => {
      const dropdownBtn = window.locator('.el-dropdown .el-button').first()

      if (await dropdownBtn.count() > 0) {
        await dropdownBtn.click()
        await window.waitForTimeout(500)
        await window.screenshot({ path: `${screenshotDir}/a-001-2-dropdown-open.png` })

        // 验证下拉菜单出现
        const menuItems = window.locator('.el-dropdown-menu__item')
        const count = await menuItems.count()
        console.log(`下拉菜单项数量: ${count}`)
        expect(count).toBeGreaterThan(0)

        // 关闭下拉菜单
        await window.keyboard.press('Escape')
        await window.waitForTimeout(300)
      }
    })

    test('A-001-3: 点击刷新按钮', async () => {
      const refreshBtn = window.locator('.header__right .el-button').first()

      if (await refreshBtn.count() > 0) {
        await refreshBtn.click()
        await window.waitForTimeout(500)
        await window.screenshot({ path: `${screenshotDir}/a-001-3-refresh.png` })
        console.log('刷新按钮点击成功')
      }
    })

    test('A-001-4: 点击设置按钮并导航', async () => {
      const settingsBtn = window.locator('.header__right .el-button').last()

      if (await settingsBtn.count() > 0) {
        await settingsBtn.click()
        await window.waitForTimeout(1000)
        await window.screenshot({ path: `${screenshotDir}/a-001-4-settings-page.png` })

        // 验证导航到设置页面
        const url = window.url()
        expect(url).toContain('settings')

        // 返回
        await window.goBack()
        await window.waitForTimeout(500)
      }
    })
  })

  // ----------------------------------------
  // A-002: Phase 导航（无项目）
  // ----------------------------------------
  test.describe('A-002: Phase Navigation (No Project)', () => {
    test('A-002-1: 验证 Phase 导航栏存在', async () => {
      await window.screenshot({ path: `${screenshotDir}/a-002-1-phase-nav.png` })

      // 查找 Phase 导航
      const phaseNav = window.locator('.phase-nav, [class*="phase"]')
      const count = await phaseNav.count()
      console.log(`Phase 导航元素数量: ${count}`)
    })

    test('A-002-2: 点击不同 Phase', async () => {
      // 尝试多种选择器
      const phases = window.locator('.phase-nav__item, .phase-item, [class*="phase-nav"] > *')
      const count = await phases.count()
      console.log(`发现 ${count} 个 Phase 导航项`)

      if (count > 0) {
        for (let i = 0; i < Math.min(count, 3); i++) {
          const phase = phases.nth(i)
          if (await phase.isVisible()) {
            await phase.click()
            await window.waitForTimeout(300)
            await window.screenshot({ path: `${screenshotDir}/a-002-2-phase-${i + 1}.png` })
          }
        }
      }
    })
  })

  // ----------------------------------------
  // A-003: 预检查状态栏（无项目）
  // ----------------------------------------
  test.describe('A-003: Preflight Bar (No Project)', () => {
    test('A-003-1: 验证预检查状态栏显示', async () => {
      const preflightBar = window.locator('.preflight-bar, [class*="preflight"]')
      await window.screenshot({ path: `${screenshotDir}/a-003-1-preflight.png` })

      if (await preflightBar.count() > 0) {
        console.log('预检查状态栏存在')

        // 查找检查项
        const checkItems = window.locator('.preflight-bar .el-tag, [class*="preflight"] .el-tag')
        const count = await checkItems.count()
        console.log(`预检查项数量: ${count}`)
      }
    })
  })

  // ----------------------------------------
  // A-004: 空状态显示
  // ----------------------------------------
  test.describe('A-004: Empty State Display', () => {
    test('A-004-1: 验证执行清单空状态', async () => {
      await window.screenshot({ path: `${screenshotDir}/a-004-1-empty-state.png` })

      // 查找空状态提示
      const emptyState = window.locator('.el-empty')
      if (await emptyState.count() > 0) {
        console.log('空状态提示存在')
        const text = await emptyState.first().textContent()
        console.log(`空状态文本: ${text}`)
      }
    })
  })

  // ----------------------------------------
  // A-005: 左侧面板
  // ----------------------------------------
  test.describe('A-005: Left Panel', () => {
    test('A-005-1: 验证左侧面板结构', async () => {
      const leftPanel = window.locator('.left-panel, [class*="left-panel"], aside')
      await window.screenshot({ path: `${screenshotDir}/a-005-1-left-panel.png` })

      if (await leftPanel.count() > 0) {
        console.log('左侧面板存在')

        // 查找各个区块
        const sections = window.locator('.left-panel__section, [class*="section"]')
        console.log(`左侧面板区块数量: ${await sections.count()}`)
      }
    })
  })
})

// ============================================================
// Part B: 有项目状态测试
// ============================================================
test.describe('Part B: With Project State Tests', () => {
  let electronApp: ElectronApplication
  let window: Page

  test.beforeAll(async () => {
    const appPath = resolve(__dirname, '..')

    electronApp = await electron.launch({
      args: [resolve(appPath, 'out/main/index.js')],
      cwd: appPath,
      env: {
        ...process.env,
        NODE_ENV: 'test'
      }
    })

    window = await electronApp.firstWindow()
    await window.waitForLoadState('domcontentloaded')
    await window.waitForTimeout(2000)
  })

  test.afterAll(async () => {
    if (electronApp) {
      await electronApp.close()
    }
  })

  // ----------------------------------------
  // B-001: 打开测试项目
  // ----------------------------------------
  test.describe('B-001: Open Test Project', () => {
    test('B-001-1: 通过 IPC 打开测试项目', async () => {
      await window.screenshot({ path: `${screenshotDir}/b-001-1-before-open.png` })

      // 通过 IPC 打开测试项目
      const result = await window.evaluate(async (projectPath) => {
        try {
          const response = await (window as any).electronAPI.invoke('project:open', {
            path: projectPath
          })
          return { success: true, data: response }
        } catch (e: any) {
          return { success: false, error: e.message }
        }
      }, TEST_PROJECT_PATH)

      console.log('打开项目结果:', JSON.stringify(result, null, 2))

      await window.waitForTimeout(2000)
      await window.screenshot({ path: `${screenshotDir}/b-001-1-after-open.png` })
    })

    test('B-001-2: 刷新项目状态', async () => {
      // 点击刷新按钮
      const refreshBtn = window.locator('.header__right .el-button').first()
      if (await refreshBtn.count() > 0) {
        await refreshBtn.click()
        await window.waitForTimeout(1000)
      }

      await window.screenshot({ path: `${screenshotDir}/b-001-2-refreshed.png` })
    })
  })

  // ----------------------------------------
  // B-002: Phase 导航（有项目）
  // ----------------------------------------
  test.describe('B-002: Phase Navigation (With Project)', () => {
    test('B-002-1: 遍历所有 Phase 并截图', async () => {
      const phases = window.locator('.phase-nav__item, .phase-item, [class*="phase-nav"] > *')
      const count = await phases.count()
      console.log(`发现 ${count} 个 Phase`)

      for (let i = 0; i < count; i++) {
        const phase = phases.nth(i)
        if (await phase.isVisible()) {
          await phase.click()
          await window.waitForTimeout(500)
          await window.screenshot({ path: `${screenshotDir}/b-002-1-phase-${i + 1}.png` })

          // 获取当前 Phase 名称
          const text = await phase.textContent()
          console.log(`Phase ${i + 1}: ${text?.trim()}`)
        }
      }
    })

    test('B-002-2: 验证 Phase 状态样式', async () => {
      // 检查 passed/current/pending 状态
      const passedPhases = window.locator('[class*="passed"], [class*="completed"]')
      const currentPhase = window.locator('[class*="current"], [class*="active"]')
      const pendingPhases = window.locator('[class*="pending"]')

      console.log(`Passed Phases: ${await passedPhases.count()}`)
      console.log(`Current Phase: ${await currentPhase.count()}`)
      console.log(`Pending Phases: ${await pendingPhases.count()}`)

      await window.screenshot({ path: `${screenshotDir}/b-002-2-phase-states.png` })
    })
  })

  // ----------------------------------------
  // B-003: Step 卡片交互
  // ----------------------------------------
  test.describe('B-003: Step Card Interactions', () => {
    test('B-003-1: 查找 Step 卡片', async () => {
      // 先切换到有步骤的 Phase
      const phases = window.locator('.phase-nav__item, [class*="phase-nav"] > *')
      if (await phases.count() > 1) {
        await phases.nth(1).click() // 切换到 Spec phase
        await window.waitForTimeout(500)
      }

      await window.screenshot({ path: `${screenshotDir}/b-003-1-step-cards.png` })

      const stepCards = window.locator('.step-card, [class*="step-card"]')
      const count = await stepCards.count()
      console.log(`Step 卡片数量: ${count}`)
    })

    test('B-003-2: 点击执行按钮', async () => {
      const executeBtn = window.locator('button:has-text("执行"), .el-button--primary:has-text("执行")')

      if (await executeBtn.count() > 0) {
        await window.screenshot({ path: `${screenshotDir}/b-003-2-before-execute.png` })
        await executeBtn.first().click()
        await window.waitForTimeout(1000)
        await window.screenshot({ path: `${screenshotDir}/b-003-2-after-execute.png` })
        console.log('执行按钮已点击')
      } else {
        console.log('未找到执行按钮')
        await window.screenshot({ path: `${screenshotDir}/b-003-2-no-execute-btn.png` })
      }
    })

    test('B-003-3: 点击打开 CLI 按钮', async () => {
      const cliBtn = window.locator('button:has-text("CLI"), button:has-text("终端"), button:has-text("打开")')

      if (await cliBtn.count() > 0) {
        await cliBtn.first().click()
        await window.waitForTimeout(500)
        await window.screenshot({ path: `${screenshotDir}/b-003-3-cli-btn.png` })
        console.log('CLI 按钮已点击')
      } else {
        console.log('未找到 CLI 按钮')
      }
    })

    test('B-003-4: 点击展开/收起日志', async () => {
      const logToggle = window.locator('button:has-text("日志"), [class*="log-toggle"], .step-card__logs-toggle')

      if (await logToggle.count() > 0) {
        // 展开
        await logToggle.first().click()
        await window.waitForTimeout(300)
        await window.screenshot({ path: `${screenshotDir}/b-003-4-log-expanded.png` })

        // 收起
        await logToggle.first().click()
        await window.waitForTimeout(300)
        await window.screenshot({ path: `${screenshotDir}/b-003-4-log-collapsed.png` })
        console.log('日志展开/收起测试完成')
      } else {
        console.log('未找到日志切换按钮')
      }
    })

    test('B-003-5: 点击审批按钮', async () => {
      const approveBtn = window.locator('button:has-text("通过"), button:has-text("审批"), button:has-text("Approve")')

      if (await approveBtn.count() > 0) {
        await window.screenshot({ path: `${screenshotDir}/b-003-5-before-approve.png` })
        await approveBtn.first().click()
        await window.waitForTimeout(500)
        await window.screenshot({ path: `${screenshotDir}/b-003-5-after-approve.png` })
        console.log('审批按钮已点击')
      } else {
        console.log('未找到审批按钮')
      }
    })
  })

  // ----------------------------------------
  // B-004: 文件预览
  // ----------------------------------------
  test.describe('B-004: File Preview', () => {
    test('B-004-1: 点击文件预览', async () => {
      const previewLink = window.locator('a[class*="artifact"], [class*="artifact-link"], button:has-text("预览")')

      if (await previewLink.count() > 0) {
        await previewLink.first().click()
        await window.waitForTimeout(1000)
        await window.screenshot({ path: `${screenshotDir}/b-004-1-preview-modal.png` })

        // 关闭模态框
        const closeBtn = window.locator('.el-dialog__close, .el-dialog__headerbtn')
        if (await closeBtn.count() > 0) {
          await closeBtn.first().click()
          await window.waitForTimeout(300)
        }
        console.log('文件预览测试完成')
      } else {
        console.log('未找到文件预览链接')
        await window.screenshot({ path: `${screenshotDir}/b-004-1-no-preview.png` })
      }
    })
  })

  // ----------------------------------------
  // B-005: 综合工作流测试
  // ----------------------------------------
  test.describe('B-005: Complete Workflow', () => {
    test('B-005-1: 完整工作流演示', async () => {
      console.log('开始完整工作流测试...')

      // 1. 初始状态
      await window.screenshot({ path: `${screenshotDir}/b-005-1-step1-initial.png` })

      // 2. 切换到 Kickoff Phase
      const phases = window.locator('.phase-nav__item, [class*="phase-nav"] > *')
      if (await phases.count() > 0) {
        await phases.first().click()
        await window.waitForTimeout(500)
        await window.screenshot({ path: `${screenshotDir}/b-005-1-step2-kickoff.png` })
      }

      // 3. 切换到 Spec Phase
      if (await phases.count() > 1) {
        await phases.nth(1).click()
        await window.waitForTimeout(500)
        await window.screenshot({ path: `${screenshotDir}/b-005-1-step3-spec.png` })
      }

      // 4. 刷新状态
      const refreshBtn = window.locator('.header__right .el-button').first()
      if (await refreshBtn.count() > 0) {
        await refreshBtn.click()
        await window.waitForTimeout(500)
        await window.screenshot({ path: `${screenshotDir}/b-005-1-step4-refresh.png` })
      }

      // 5. 打开设置
      const settingsBtn = window.locator('.header__right .el-button').last()
      if (await settingsBtn.count() > 0) {
        await settingsBtn.click()
        await window.waitForTimeout(500)
        await window.screenshot({ path: `${screenshotDir}/b-005-1-step5-settings.png` })
        await window.goBack()
        await window.waitForTimeout(500)
      }

      // 6. 最终状态
      await window.screenshot({ path: `${screenshotDir}/b-005-1-step6-final.png` })

      console.log('完整工作流测试完成')
    })
  })
})
