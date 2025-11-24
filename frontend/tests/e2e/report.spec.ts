import { test, expect } from '@playwright/test'

test.describe('UC-4: 개인 맞춤 리포트 생성', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[placeholder*="사용자"]', 'testuser')
    await page.fill('input[placeholder*="이름"]', '테스트')
    await page.fill('input[type="password"]', 'test123')
    await page.locator('button:has-text("로그인")').click()
    await page.waitForURL('/')
  })

  test('should navigate to report page from homepage', async ({ page }) => {
    // 홈페이지에서 "리포트 보기" 버튼 클릭
    await page.locator('text=리포트').click()

    // /reports 페이지로 이동
    await expect(page).toHaveURL('/reports')
    await expect(page.locator('text=개인 맞춤 리포트')).toBeVisible()
  })

  test('should display generate report button', async ({ page }) => {
    await page.goto('/reports')

    // "새 리포트 생성" 버튼 확인
    const generateButton = page.locator('button:has-text("생성")')
    await expect(generateButton).toBeVisible()
  })

  test('should generate report successfully', async ({ page }) => {
    await page.goto('/reports')

    // "새 리포트 생성" 버튼 클릭
    await page.locator('button:has-text("생성")').click()

    // 로딩 상태 표시
    await expect(page.locator('text=생성 중')).toBeVisible({ timeout: 2000 })

    // 생성 완료 후 성공 메시지
    await expect(page.locator('text=생성되었습니다')).toBeVisible({ timeout: 5000 })
  })

  test('should display generated reports in list', async ({ page }) => {
    await page.goto('/reports')

    // 리포트 생성
    await page.locator('button:has-text("생성")').click()
    await page.waitForTimeout(2000)

    // 리포트 카드 확인
    const reportCards = page.locator('div').filter({ 
      has: page.locator('text=/리포트|논문/')
    })
    
    await expect(reportCards.first()).toBeVisible({ timeout: 5000 })
  })

  test('should expand/collapse report card', async ({ page }) => {
    await page.goto('/reports')

    // 리포트 카드 클릭 (전개)
    const firstReportCard = page.locator('button').filter({ 
      has: page.locator('text=/리포트/')
    }).first()
    
    await firstReportCard.click()

    // 상세 정보 표시
    await expect(page.locator('text=상태')).toBeVisible()
    await expect(page.locator('text=포함된 논문')).toBeVisible()

    // 다시 클릭 (축소)
    await firstReportCard.click()
    await expect(page.locator('text=상태')).not.toBeVisible()
  })

  test('should display report details in expanded view', async ({ page }) => {
    await page.goto('/reports')

    // 리포트 카드 전개
    const firstReportCard = page.locator('button').filter({ 
      has: page.locator('text=/리포트/')
    }).first()
    
    await firstReportCard.click()

    // 상세 정보 확인
    await expect(page.locator('text=✅ 완료됨')).toBeVisible()
    await expect(page.locator('text=다운로드')).toBeVisible()
    await expect(page.locator('text=상세 보기')).toBeVisible()
  })

  test('should display tips section', async ({ page }) => {
    await page.goto('/reports')

    // 팁 섹션 확인
    await expect(page.locator('text=리포트 활용 팁')).toBeVisible()
    
    // 팁 내용 확인
    await expect(page.locator('text=매주 자동 생성')).toBeVisible()
    await expect(page.locator('text=관심사 기반')).toBeVisible()
  })
})
