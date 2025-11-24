import { test, expect } from '@playwright/test'

test.describe('UC-2: 논문 검색 및 상세 정보 조회', () => {
  test.beforeEach(async ({ page }) => {
    // 테스트 전 로그인
    await page.goto('/login')
    await page.fill('input[placeholder*="사용자"]', 'testuser')
    await page.fill('input[placeholder*="이름"]', '테스트')
    await page.fill('input[type="password"]', 'test123')
    await page.locator('button:has-text("로그인")').click()
    await page.waitForURL('/')
  })

  test('should navigate to research page from homepage', async ({ page }) => {
    // 홈페이지에서 "논문 검색" 버튼 클릭
    await page.locator('text=논문 검색').click()
    
    // /research 페이지로 이동
    await expect(page).toHaveURL('/research')
    await expect(page.locator('text=논문 검색')).toBeVisible()
  })

  test('should search papers with filters', async ({ page }) => {
    await page.goto('/research')

    // 검색 주제 입력
    await page.fill('input[placeholder*="주제"]', '인공지능')

    // 대학 필터 선택
    await page.selectOption('select', 'KAIST')

    // 검색 버튼 클릭
    await page.locator('button:has-text("검색")').click()

    // 로딩 스피너 표시 후 논문 카드 로드
    await page.waitForLoadState('networkidle')
    
    // 논문 카드 확인 (mock 데이터 포함)
    const paperCards = page.locator('div').filter({ has: page.locator('text=/논문|연구/') })
    await expect(paperCards.first()).toBeVisible({ timeout: 5000 })
  })

  test('should open detail modal when clicking 상세 정보', async ({ page }) => {
    await page.goto('/research')

    // 첫 번째 논문의 "상세 정보" 버튼 클릭
    const detailButtons = page.locator('button:has-text("상세 정보")')
    await detailButtons.first().click()

    // 모달 팝업 표시 확인
    await expect(page.locator('text=연구 요약')).toBeVisible()
    
    // 모달에 논문 정보 표시 확인
    await expect(page.locator('text=진로 정보').or(page.locator('text=실천 항목'))).toBeVisible()
  })

  test('should navigate to Plan B page from detail modal', async ({ page }) => {
    await page.goto('/research')

    // 첫 번째 논문의 "상세 정보" 버튼 클릭
    const detailButtons = page.locator('button:has-text("상세 정보")')
    await detailButtons.first().click()

    // 모달에서 "Plan B 보기" 버튼 클릭
    await page.locator('button:has-text("Plan B 보기")').click()

    // /research/:paperId/plan-b 페이지로 이동
    await expect(page).toHaveURL(/\/research\/.*\/plan-b/)
    await expect(page.locator('text=Plan B')).toBeVisible()
  })

  test('should display empty state when no papers found', async ({ page }) => {
    await page.goto('/research')

    // 검색 주제에 없는 주제 입력
    await page.fill('input[placeholder*="주제"]', 'xyzabc12345notexist')

    // 검색 버튼 클릭
    await page.locator('button:has-text("검색")').click()

    // 빈 결과 메시지 표시
    await expect(page.locator('text=검색 결과가 없습니다')).toBeVisible({ timeout: 5000 })
  })
})
