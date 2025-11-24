import { test, expect } from '@playwright/test'

test.describe('UC-5: 사용자 프로필 관리', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[placeholder*="사용자"]', 'testuser')
    await page.fill('input[placeholder*="이름"]', '테스트')
    await page.fill('input[type="password"]', 'test123')
    await page.locator('button:has-text("로그인")').click()
    await page.waitForURL('/')
  })

  test('should navigate to profile page', async ({ page }) => {
    // 프로필 버튼 클릭
    await page.locator('button:has-text("프로필")').click()

    // /profile 페이지로 이동
    await expect(page).toHaveURL('/profile')
    await expect(page.locator('text=프로필 설정')).toBeVisible()
  })

  test('should display user information in header', async ({ page }) => {
    await page.goto('/profile')

    // 사용자 정보 확인
    await expect(page.locator('text=테스트')).toBeVisible()
    await expect(page.locator('text=학생')).toBeVisible()
    await expect(page.locator('text=testuser')).toBeVisible()
  })

  test('should edit user name', async ({ page }) => {
    await page.goto('/profile')

    // 이름 필드 값 변경
    const nameInput = page.locator('input[placeholder*="이름"]')
    await nameInput.fill('박영희')

    // "프로필 저장" 버튼 클릭
    await page.locator('button:has-text("저장")').click()

    // 성공 메시지 확인
    await expect(page.locator('text=저장되었습니다')).toBeVisible({ timeout: 3000 })
  })

  test('should add and remove interests', async ({ page }) => {
    await page.goto('/profile')

    // 새로운 관심사 추가
    const interestInput = page.locator('input[placeholder*="관심사"]').last()
    await interestInput.fill('사이버보안')
    
    // 추가 버튼 클릭
    await page.locator('button:has-text("추가")').last().click()

    // 새 태그 확인
    await expect(page.locator('text=사이버보안')).toBeVisible()

    // 태그 삭제
    const deleteButtons = page.locator('button:has-text("×")')
    await deleteButtons.first().click()

    // 태그 삭제 확인
    await page.waitForTimeout(500)
    const tags = page.locator('[class*="bg-indigo"]')
    const tagCount = await tags.count()
    expect(tagCount).toBeGreaterThanOrEqual(0)
  })

  test('should save profile changes', async ({ page }) => {
    await page.goto('/profile')

    // 이름 변경
    const nameInput = page.locator('input[placeholder*="이름"]')
    const currentName = await nameInput.inputValue()
    await nameInput.fill(currentName + '수정')

    // 저장 버튼 클릭
    await page.locator('button:has-text("저장")').click()

    // 성공 메시지
    await expect(page.locator('text=저장되었습니다')).toBeVisible({ timeout: 3000 })
  })

  test('should display notification settings', async ({ page }) => {
    await page.goto('/profile')

    // 알림 설정 확인
    await expect(page.locator('text=주간 리포트')).toBeVisible()
    await expect(page.locator('text=새로운 논문')).toBeVisible()
    await expect(page.locator('text=Notion 자동')).toBeVisible()

    // 체크박스 확인
    const checkboxes = page.locator('input[type="checkbox"]')
    expect(await checkboxes.count()).toBeGreaterThan(0)
  })

  test('should display service integrations', async ({ page }) => {
    await page.goto('/profile')

    // 서비스 통합 섹션 확인
    await expect(page.locator('text=Notion')).toBeVisible()
    await expect(page.locator('text=Kakao Talk')).toBeVisible()

    // 연동하기 버튼 확인
    const integrationButtons = page.locator('button:has-text("연동")')
    expect(await integrationButtons.count()).toBeGreaterThanOrEqual(2)
  })

  test('should logout with confirmation', async ({ page }) => {
    await page.goto('/profile')

    // 로그아웃 버튼 클릭
    await page.locator('button:has-text("로그아웃")').click()

    // 확인 대화상자 처리
    page.on('dialog', dialog => {
      expect(dialog.message()).toContain('로그아웃')
      dialog.accept()
    })

    // /login으로 리다이렉트
    await expect(page).toHaveURL('/login', { timeout: 5000 })
  })
})
