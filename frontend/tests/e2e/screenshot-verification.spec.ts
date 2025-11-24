import { test, expect } from '@playwright/test'
import * as fs from 'fs'
import * as crypto from 'crypto'
import * as path from 'path'

/**
 * 스크린샷 검증 테스트
 * 각 페이지에서 스크린샷을 찍고 MD5 해시로 검증합니다
 */

interface ScreenshotInfo {
  pageName: string
  fileName: string
  path: string
  md5Hash: string
  fileSize: number
  timestamp: string
}

// 스크린샷 디렉토리
const SCREENSHOT_DIR = path.join(__dirname, '../../screenshots')
const VERIFICATION_FILE = path.join(SCREENSHOT_DIR, 'screenshot-verification.json')

// 디렉토리 생성 함수
function ensureScreenshotDir() {
  if (!fs.existsSync(SCREENSHOT_DIR)) {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true })
  }
}

// 파일의 MD5 해시 계산
function calculateMD5(filePath: string): string {
  const fileBuffer = fs.readFileSync(filePath)
  const hashSum = crypto.createHash('md5')
  hashSum.update(fileBuffer)
  return hashSum.digest('hex')
}

// 스크린샷 정보 저장
function saveScreenshotInfo(info: ScreenshotInfo) {
  ensureScreenshotDir()

  let screenshots: ScreenshotInfo[] = []
  if (fs.existsSync(VERIFICATION_FILE)) {
    const data = fs.readFileSync(VERIFICATION_FILE, 'utf-8')
    screenshots = JSON.parse(data)
  }

  // 같은 페이지의 이전 스크린샷은 제거
  screenshots = screenshots.filter((s) => s.pageName !== info.pageName)

  // 새 정보 추가
  screenshots.push(info)

  fs.writeFileSync(VERIFICATION_FILE, JSON.stringify(screenshots, null, 2))
}

// 스크린샷 검증
async function captureAndVerifyScreenshot(
  page: any,
  pageName: string,
  fileName: string
) {
  ensureScreenshotDir()

  const screenshotPath = path.join(SCREENSHOT_DIR, fileName)

  // 스크린샷 캡처
  await page.screenshot({ path: screenshotPath, fullPage: true })

  // 파일 존재 확인
  expect(fs.existsSync(screenshotPath)).toBeTruthy()

  // 파일 크기 확인 (0보다 커야 함)
  const stats = fs.statSync(screenshotPath)
  expect(stats.size).toBeGreaterThan(0)

  // MD5 해시 계산
  const md5Hash = calculateMD5(screenshotPath)

  // 스크린샷 정보 저장
  const info: ScreenshotInfo = {
    pageName,
    fileName,
    path: screenshotPath,
    md5Hash,
    fileSize: stats.size,
    timestamp: new Date().toISOString(),
  }

  saveScreenshotInfo(info)

  console.log(`✅ ${pageName} 스크린샷 저장됨`)
  console.log(`   파일: ${fileName}`)
  console.log(`   크기: ${stats.size} bytes`)
  console.log(`   MD5: ${md5Hash}`)

  return info
}

test.describe('스크린샷 검증 테스트', () => {
  test.beforeEach(async ({ page }) => {
    // 로그인
    await page.goto('/login')
    await page.fill('input[placeholder*="사용자"]', 'screenshot-test')
    await page.fill('input[placeholder*="이름"]', '스크린샷테스트')
    await page.fill('input[type="password"]', 'test123')
    await page.locator('button:has-text("로그인")').click()
    await page.waitForURL('/')
  })

  test('홈페이지 스크린샷', async ({ page }) => {
    await page.goto('/')

    const info = await captureAndVerifyScreenshot(page, 'Home Page', 'homepage.png')

    // 해시가 유효한 MD5 형식인지 확인
    expect(info.md5Hash).toMatch(/^[a-f0-9]{32}$/)
  })

  test('논문 검색 페이지 스크린샷', async ({ page }) => {
    await page.goto('/research')

    const info = await captureAndVerifyScreenshot(page, 'Research Page', 'research-page.png')

    expect(info.md5Hash).toMatch(/^[a-f0-9]{32}$/)
  })

  test('프로필 페이지 스크린샷', async ({ page }) => {
    await page.goto('/profile')

    const info = await captureAndVerifyScreenshot(page, 'Profile Page', 'profile-page.png')

    expect(info.md5Hash).toMatch(/^[a-f0-9]{32}$/)
  })

  test('리포트 페이지 스크린샷', async ({ page }) => {
    await page.goto('/reports')

    const info = await captureAndVerifyScreenshot(page, 'Report Page', 'report-page.png')

    expect(info.md5Hash).toMatch(/^[a-f0-9]{32}$/)
  })

  test('스크린샷 해시 검증', async ({ page }) => {
    ensureScreenshotDir()

    // 모든 스크린샷이 저장되었는지 확인
    expect(fs.existsSync(VERIFICATION_FILE)).toBeTruthy()

    const data = fs.readFileSync(VERIFICATION_FILE, 'utf-8')
    const screenshots: ScreenshotInfo[] = JSON.parse(data)

    console.log('\n📸 저장된 스크린샷 검증 결과:')
    console.log('═'.repeat(60))

    for (const screenshot of screenshots) {
      // 파일 존재 확인
      expect(fs.existsSync(screenshot.path)).toBeTruthy()

      // 현재 파일의 MD5 해시 다시 계산
      const currentHash = calculateMD5(screenshot.path)

      // 저장된 해시와 일치하는지 확인
      expect(currentHash).toBe(screenshot.md5Hash)

      console.log(`\n✅ ${screenshot.pageName}`)
      console.log(`   파일: ${screenshot.fileName}`)
      console.log(`   MD5: ${screenshot.md5Hash}`)
      console.log(`   크기: ${screenshot.fileSize} bytes`)
      console.log(`   생성시간: ${screenshot.timestamp}`)
    }

    console.log('\n' + '═'.repeat(60))
    console.log(`\n✨ 모든 스크린샷이 성공적으로 검증되었습니다!`)
    console.log(`   총 ${screenshots.length}개의 스크린샷`)
  })

  test('서로 다른 스크린샷 비교', async ({ page }) => {
    ensureScreenshotDir()

    if (!fs.existsSync(VERIFICATION_FILE)) {
      test.skip()
    }

    const data = fs.readFileSync(VERIFICATION_FILE, 'utf-8')
    const screenshots: ScreenshotInfo[] = JSON.parse(data)

    console.log('\n🔍 스크린샷 MD5 해시 비교:')
    console.log('═'.repeat(70))

    const hashes = screenshots.map((s) => s.md5Hash)

    // 각 해시가 고유한지 확인 (모든 스크린샷이 다른지)
    const uniqueHashes = new Set(hashes)
    expect(uniqueHashes.size).toBe(hashes.length)

    console.log(`\n✅ 모든 스크린샷이 서로 다릅니다!`)
    console.log(`   총 ${hashes.length}개의 고유한 이미지\n`)

    // 모든 해시 비교 출력
    for (let i = 0; i < screenshots.length; i++) {
      for (let j = i + 1; j < screenshots.length; j++) {
        const hash1 = screenshots[i].md5Hash
        const hash2 = screenshots[j].md5Hash
        const isSame = hash1 === hash2 ? '동일' : '다름'

        console.log(
          `${screenshots[i].pageName.padEnd(15)} vs ${screenshots[j].pageName.padEnd(15)} : ${isSame}`
        )
      }
    }

    console.log('\n' + '═'.repeat(70))
  })

  test('스크린샷 세부 정보 출력', async ({ page }) => {
    ensureScreenshotDir()

    if (!fs.existsSync(VERIFICATION_FILE)) {
      test.skip()
    }

    const data = fs.readFileSync(VERIFICATION_FILE, 'utf-8')
    const screenshots: ScreenshotInfo[] = JSON.parse(data)

    console.log('\n📋 스크린샷 세부 정보:')
    console.log('═'.repeat(80))

    const table = screenshots.map((s) => ({
      '페이지명': s.pageName,
      '파일명': s.fileName,
      '파일 크기': `${s.fileSize} bytes`,
      'MD5 해시': s.md5Hash,
      '생성시간': new Date(s.timestamp).toLocaleString('ko-KR'),
    }))

    console.table(table)

    console.log('═'.repeat(80))

    // 검증 JSON 파일 경로 출력
    console.log(`\n📁 검증 파일 위치: ${VERIFICATION_FILE}`)
    console.log(`📁 스크린샷 디렉토리: ${SCREENSHOT_DIR}`)
  })
})
