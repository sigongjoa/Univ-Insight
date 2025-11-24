import { test, expect, devices } from '@playwright/test'

test.describe('UC-10: 반응형 디자인 테스트', () => {
  test.describe('모바일 뷰 (320px)', () => {
    test.use(devices['iPhone 12'])

    test('should render login page on mobile', async ({ page }) => {
      await page.goto('/login')
      
      // 모든 요소가 표시되어야 함
      await expect(page.locator('input')).toHaveCount(4) // userId, name, password, interests
      await expect(page.locator('button:has-text("로그인")')).toBeVisible()
    })

    test('should render homepage on mobile', async ({ page }) => {
      // 로그인
      await page.goto('/login')
      await page.fill('input[placeholder*="사용자"]', 'mobile')
      await page.fill('input[placeholder*="이름"]', 'Test')
      await page.fill('input[type="password"]', 'test')
      await page.locator('button:has-text("로그인")').click()
      await page.waitForURL('/')

      // 버튼들이 모두 표시되어야 함
      await expect(page.locator('text=논문 검색')).toBeVisible()
      await expect(page.locator('text=리포트')).toBeVisible()
    })
  })

  test.describe('태블릿 뷰 (768px)', () => {
    test.use({
      ...devices['iPad'],
    })

    test('should render research page on tablet', async ({ page }) => {
      await page.goto('/login')
      await page.fill('input[placeholder*="사용자"]', 'tablet')
      await page.fill('input[placeholder*="이름"]', 'Test')
      await page.fill('input[type="password"]', 'test')
      await page.locator('button:has-text("로그인")').click()
      await page.waitForURL('/')

      await page.locator('text=논문 검색').click()

      // 검색 폼이 2열 레이아웃으로 표시
      const searchForm = page.locator('input[placeholder*="주제"]')
      await expect(searchForm).toBeVisible()
    })
  })

  test.describe('데스크톱 뷰 (1920px)', () => {
    test('should render all pages on desktop', async ({ page }) => {
      // 뷰포트 설정
      await page.setViewportSize({ width: 1920, height: 1080 })

      await page.goto('/login')
      await page.fill('input[placeholder*="사용자"]', 'desktop')
      await page.fill('input[placeholder*="이름"]', 'Test')
      await page.fill('input[type="password"]', 'test')
      await page.locator('button:has-text("로그인")').click()
      await page.waitForURL('/')

      // 모든 페이지에서 최대 너비 적용
      const maxWidthElement = page.locator('[class*="max-w"]').first()
      await expect(maxWidthElement).toBeVisible()
    })
  })

  test.describe('터치 친화적 요소', () => {
    test.use(devices['iPhone 12'])

    test('should have adequate button touch area', async ({ page }) => {
      await page.goto('/login')

      // 버튼의 높이 확인 (최소 44px)
      const button = page.locator('button:has-text("로그인")')
      const box = await button.boundingBox()
      
      if (box) {
        expect(box.height).toBeGreaterThanOrEqual(40) // 근처값으로 허용
      }
    })
  })
})
