import { test, expect } from '@playwright/test'

test.describe('UC-6 & UC-7: 네비게이션 및 접근 제어', () => {
  test.describe('로그인 후 네비게이션', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/login')
      await page.fill('input[placeholder*="사용자"]', 'testuser')
      await page.fill('input[placeholder*="이름"]', '테스트')
      await page.fill('input[type="password"]', 'test123')
      await page.locator('button:has-text("로그인")').click()
      await page.waitForURL('/')
    })

    test('should navigate between all pages', async ({ page }) => {
      // 홈페이지
      await expect(page).toHaveURL('/')

      // 논문 검색으로 이동
      await page.locator('text=논문 검색').click()
      await expect(page).toHaveURL('/research')

      // 프로필로 이동
      await page.locator('button:has-text("프로필")').click()
      await expect(page).toHaveURL('/profile')

      // 홈으로 이동
      await page.locator('text=홈').click()
      await expect(page).toHaveURL('/')

      // 리포트로 이동
      await page.locator('text=리포트').click()
      await expect(page).toHaveURL('/reports')
    })

    test('should return home when clicking logo', async ({ page }) => {
      // 논문 검색 페이지로 이동
      await page.locator('text=논문 검색').click()
      await expect(page).toHaveURL('/research')

      // 로고 클릭
      await page.locator('text=Univ-Insight').first().click()

      // 홈으로 이동
      await expect(page).toHaveURL('/')
    })

    test('should maintain header consistency', async ({ page }) => {
      const pages = [
        { url: '/', name: 'Home' },
        { url: '/research', name: 'Research' },
        { url: '/reports', name: 'Reports' },
        { url: '/profile', name: 'Profile' },
      ]

      for (const { url } of pages) {
        await page.goto(url)

        // 헤더에 로고 확인
        await expect(page.locator('text=Univ-Insight')).toBeVisible()

        // 헤더에 프로필 버튼 확인
        await expect(page.locator('button:has-text("프로필")')).toBeVisible()
      }
    })
  })

  test.describe('미인증 사용자 접근 제어', () => {
    test('should redirect to login when accessing research page without auth', async ({ page }) => {
      // 직접 /research 접속
      await page.goto('/research')

      // /login으로 리다이렉트
      await expect(page).toHaveURL('/login', { timeout: 5000 })
    })

    test('should redirect to login when accessing reports page without auth', async ({ page }) => {
      await page.goto('/reports')
      await expect(page).toHaveURL('/login', { timeout: 5000 })
    })

    test('should redirect to login when accessing profile page without auth', async ({ page }) => {
      await page.goto('/profile')
      await expect(page).toHaveURL('/login', { timeout: 5000 })
    })

    test('should allow accessing login page without auth', async ({ page }) => {
      await page.goto('/login')
      await expect(page).toHaveURL('/login')
      await expect(page.locator('text=로그인')).toBeVisible()
    })

    test('should show loading message when checking auth', async ({ page }) => {
      // 보호된 페이지에 직접 접속하면 로딩 메시지 또는 리다이렉트 확인
      await page.goto('/research')
      
      // 로딩 메시지 또는 login 페이지 확인
      const isLoading = await page.locator('text=로딩').isVisible().catch(() => false)
      const isLoginPage = page.url().includes('/login')
      
      expect(isLoading || isLoginPage).toBeTruthy()
    })
  })
})
