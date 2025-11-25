
import { describe, it, expect, beforeAll, afterAll } from 'vitest'
import { preview } from 'vite'
import type { PreviewServer } from 'vite'
import { chromium, type Browser, type Page } from 'playwright'

describe('University Explorer E2E Tests', () => {
    let server: PreviewServer
    let browser: Browser
    let page: Page

    beforeAll(async () => {
        server = await preview({ preview: { port: 4173 } })
        browser = await chromium.launch()
        page = await browser.newPage()
    })

    afterAll(async () => {
        await browser.close()
        await new Promise<void>((resolve, reject) => {
            server.httpServer.close((error) => (error ? reject(error) : resolve()))
        })
    })

    it('UC-E2E-001: should load university list page', async () => {
        await page.goto('http://localhost:4173/universities')
        await page.waitForSelector('.university-list-container')

        const title = await page.textContent('.page-title')
        expect(title).toContain('University Explorer')
    })

    it('UC-E2E-002: should search universities', async () => {
        await page.goto('http://localhost:4173/universities')
        await page.waitForSelector('.search-bar')

        await page.fill('.search-bar', '서울')
        await page.waitForTimeout(500) // Wait for filter

        const cards = await page.$$('.university-card')
        expect(cards.length).toBeGreaterThan(0)
    })

    it('UC-E2E-003: should navigate to university detail', async () => {
        await page.goto('http://localhost:4173/universities')
        await page.waitForSelector('.university-card')

        await page.click('.university-card:first-child')
        await page.waitForSelector('.university-detail-container')

        const header = await page.textContent('.uni-header h1')
        expect(header).toBeTruthy()
    })

    it('UC-E2E-004: should trigger crawl job', async () => {
        await page.goto('http://localhost:4173/universities')
        await page.waitForSelector('.university-card')
        await page.click('.university-card:first-child')
        await page.waitForSelector('.crawl-section')

        await page.fill('.crawl-input', 'https://example.com')
        await page.click('.crawl-button')

        await page.waitForSelector('.status-message')
        const message = await page.textContent('.status-message')
        expect(message).toContain('queued')
    })
})
