import { test, expect } from '@playwright/test'

test.describe('UC-3: Plan B 대학 대안 조회', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[placeholder*="사용자"]', 'testuser')
    await page.fill('input[placeholder*="이름"]', '테스트')
    await page.fill('input[type="password"]', 'test123')
    await page.locator('button:has-text("로그인")').click()
    await page.waitForURL('/')
  })

  test('should display original paper header', async ({ page }) => {
    // 임시로 plan-b 페이지 직접 접속 (실제로는 research에서 네비게이션)
    await page.goto('/research')
    await page.locator('button:has-text("Plan B 보기")').first().click()

    // Plan B 페이지로 이동 확인
    await expect(page).toHaveURL(/\/research\/.*\/plan-b/)

    // 헤더에 원본 논문 정보 표시
    await expect(page.locator('text=Plan B 대안')).toBeVisible()
  })

  test('should display Plan B suggestions list', async ({ page }) => {
    await page.goto('/research')
    await page.locator('button:has-text("Plan B 보기")').first().click()

    await expect(page).toHaveURL(/\/research\/.*\/plan-b/)

    // Plan B 제안 리스트 표시
    const suggestionCards = page.locator('div').filter({ 
      has: page.locator('text=/Plan B|유사도/')
    })
    
    await expect(suggestionCards.first()).toBeVisible({ timeout: 5000 })
  })

  test('should display similarity score with progress bar', async ({ page }) => {
    await page.goto('/research')
    await page.locator('button:has-text("Plan B 보기")').first().click()

    await expect(page).toHaveURL(/\/research\/.*\/plan-b/)

    // 유사도 진행바 확인
    const progressBar = page.locator('.bg-green-400, .bg-green-600')
    await expect(progressBar.first()).toBeVisible({ timeout: 5000 })

    // 유사도 백분율 확인
    await expect(page.locator('text=/%/')).toBeVisible()
  })

  test('should display Plan B tips section', async ({ page }) => {
    await page.goto('/research')
    await page.locator('button:has-text("Plan B 보기")').first().click()

    await expect(page).toHaveURL(/\/research\/.*\/plan-b/)

    // 팁 섹션 확인
    await expect(page.locator('text=Plan B 선택 팁')).toBeVisible()
    
    // 팁 항목들 확인
    await expect(page.locator('text=유사도가 높을수록')).toBeVisible()
    await expect(page.locator('text=Tier가 높을수록')).toBeVisible()
  })

  test('should navigate back to research page', async ({ page }) => {
    await page.goto('/research')
    await page.locator('button:has-text("Plan B 보기")').first().click()

    await expect(page).toHaveURL(/\/research\/.*\/plan-b/)

    // "다른 논문 보기" 버튼 클릭
    await page.locator('button:has-text("다른 논문")').click()

    // /research로 리다이렉트
    await expect(page).toHaveURL('/research')
  })
})
