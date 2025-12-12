import { test, expect } from '@playwright/test'

/**
 * Dashboard 文档查看器测试
 * 测试所有 Phase 的参考文档是否能正常加载
 */

const BASE_URL = 'http://localhost:5174'

// Phase 0 的参考文档
const phase0Docs = [
  { name: 'CONTEXT_TEMPLATE.md', expectedContent: '功能模块上下文文档模板' },
  { name: 'PROJECT_PROFILE_TEMPLATE.yaml', expectedContent: 'project_name' },
  { name: '02_API_CONVENTIONS.md', expectedContent: 'API' },
  { name: '03_DB_CONVENTIONS.md', expectedContent: '数据库' },
  { name: '_ui_system_template/', expectedContent: 'UI' },
]

test.describe('Dashboard 文档查看器测试', () => {
  test.beforeEach(async ({ page }) => {
    // 导航到 Phase 0 页面
    await page.goto(`${BASE_URL}/project-dashboard/project-dashboard-system/0`)
    await page.waitForLoadState('networkidle')
  })

  test('Phase 0 页面应该正确加载', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Phase 0: Foundation')
  })

  test.describe('Phase 0 参考文档测试', () => {
    for (const doc of phase0Docs) {
      test(`应该能加载 ${doc.name}`, async ({ page }) => {
        // 找到文档名称对应的"查看"按钮
        const docRow = page.locator(`text=${doc.name}`).locator('..')
        const viewButton = docRow.locator('button:has-text("查看")')

        // 如果找不到，尝试其他方式定位
        if (await viewButton.count() === 0) {
          // 直接在参考文档区域查找
          const refDocsSection = page.locator('h2:has-text("参考文档")').locator('..')
          const allViewButtons = refDocsSection.locator('button:has-text("查看")')

          // 点击对应索引的按钮
          const docIndex = phase0Docs.findIndex(d => d.name === doc.name)
          await allViewButtons.nth(docIndex).click()
        } else {
          await viewButton.click()
        }

        // 等待弹窗出现
        const dialog = page.locator('[role="dialog"], .el-dialog, .doc-viewer-modal')
        await expect(dialog).toBeVisible({ timeout: 10000 })

        // 等待加载完成（不再显示"正在加载"）
        await page.waitForFunction(() => {
          const loadingText = document.body.innerText
          return !loadingText.includes('正在从 GitHub 加载文档')
        }, { timeout: 15000 })

        // 检查是否有错误
        const hasError = await page.locator('text=加载失败').count() > 0 ||
                         await page.locator('text=文档尚未创建').count() > 0 ||
                         await page.locator('text=404').count() > 0

        if (hasError) {
          // 截图记录错误
          await page.screenshot({ path: `test-results/error-${doc.name.replace(/[\/\.]/g, '_')}.png` })
          throw new Error(`文档 ${doc.name} 加载失败`)
        }

        // 验证内容包含预期文本
        const dialogContent = await dialog.textContent()
        expect(dialogContent).toContain(doc.expectedContent)

        // 关闭弹窗
        await page.keyboard.press('Escape')
        await expect(dialog).not.toBeVisible({ timeout: 3000 })
      })
    }
  })
})

// Phase 1-7 的测试
const phases = [
  { id: 1, name: 'Kickoff' },
  { id: 2, name: 'Spec' },
  { id: 3, name: 'Demo' },
  { id: 4, name: 'Design' },
  { id: 5, name: 'Code' },
  { id: 6, name: 'Test' },
  { id: 7, name: 'Deploy' },
]

test.describe('其他 Phase 页面测试', () => {
  for (const phase of phases) {
    test(`Phase ${phase.id} (${phase.name}) 页面应该正确加载`, async ({ page }) => {
      await page.goto(`${BASE_URL}/project-dashboard/project-dashboard-system/${phase.id}`)
      await page.waitForLoadState('networkidle')

      // 验证页面标题
      await expect(page.locator('h1')).toContainText(`Phase ${phase.id}`)

      // 验证参考文档区域存在
      const refDocsSection = page.locator('h2:has-text("参考文档")')
      if (await refDocsSection.count() > 0) {
        // 获取所有"查看"按钮
        const viewButtons = page.locator('button:has-text("查看")')
        const buttonCount = await viewButtons.count()

        console.log(`Phase ${phase.id} 有 ${buttonCount} 个文档链接`)

        // 测试第一个文档链接（如果存在）
        if (buttonCount > 0) {
          await viewButtons.first().click()

          // 等待弹窗
          const dialog = page.locator('[role="dialog"], .el-dialog, .doc-viewer-modal')
          await expect(dialog).toBeVisible({ timeout: 10000 })

          // 等待加载
          await page.waitForTimeout(3000)

          // 检查是否有错误
          const hasError = await page.locator('text=加载失败').count() > 0 ||
                           await page.locator('text=文档尚未创建').count() > 0

          if (hasError) {
            await page.screenshot({ path: `test-results/error-phase${phase.id}.png` })
          }

          // 关闭弹窗
          await page.keyboard.press('Escape')
        }
      }
    })
  }
})
