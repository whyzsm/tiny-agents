import { expect, test } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test('renders the blank workspace without accessibility violations', async ({
  page,
}) => {
  await page.goto('/')
  await expect(
    page.getByRole('heading', { name: 'A clear place for the first module.' }),
  ).toBeVisible()

  const accessibilityScan = await new AxeBuilder({ page }).analyze()
  expect(accessibilityScan.violations).toEqual([])
})

test('toggles the navigation rail', async ({ page }) => {
  await page.goto('/')
  const toggle = page.getByRole('button', { name: 'Collapse sidebar' })
  await toggle.click()

  await expect(page.getByRole('button', { name: 'Expand sidebar' })).toBeVisible()
})
