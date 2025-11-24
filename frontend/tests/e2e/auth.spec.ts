import { test, expect } from '@playwright/test'

test.describe('UC-1: 사용자 회원가입 및 로그인', () => {
  test('should register and login successfully', async ({ page }) => {
    // 1. /login 페이지 접속
    await page.goto('/login')
    
    // 페이지 로드 확인
    await expect(page.locator('text=로그인')).toBeVisible()
    await expect(page.locator('text=회원가입')).toBeVisible()

    // 2. userId 입력
    await page.fill('input[placeholder*="사용자"]', 'student01')

    // 3. 이름 입력
    await page.fill('input[placeholder*="이름"]', '김철수')

    // 4. 비밀번호 입력
    await page.fill('input[type="password"]', 'password123')

    // 5. role 선택 - student
    await page.selectOption('select', 'student')

    // 6. 관심사 추가
    const interestInput = page.locator('input[placeholder*="관심사"]')
    await interestInput.fill('AI')
    await page.locator('button:has-text("추가")').first().click()
    
    await interestInput.fill('ML')
    await page.locator('button:has-text("추가")').first().click()
    
    await interestInput.fill('빅데이터')
    await page.locator('button:has-text("추가")').first().click()

    // 3개 태그 확인
    await expect(page.locator('text=AI')).toBeVisible()
    await expect(page.locator('text=ML')).toBeVisible()
    await expect(page.locator('text=빅데이터')).toBeVisible()

    // 7. "로그인" 버튼 클릭
    await page.locator('button:has-text("로그인")').click()

    // 8. 홈페이지로 리다이렉트되고 사용자 정보 표시
    await expect(page).toHaveURL('/')
    await expect(page.locator('text=김철수')).toBeVisible()
    await expect(page.locator('text=AI')).toBeVisible()
    await expect(page.locator('text=ML')).toBeVisible()
  })

  test('should show login form with all required fields', async ({ page }) => {
    await page.goto('/login')

    // 필수 입력 필드 확인
    await expect(page.locator('input[placeholder*="사용자"]')).toBeVisible()
    await expect(page.locator('input[placeholder*="이름"]')).toBeVisible()
    await expect(page.locator('input[type="password"]')).toBeVisible()
    await expect(page.locator('select')).toBeVisible()
  })
})
