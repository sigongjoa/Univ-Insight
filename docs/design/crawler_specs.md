# Crawler Specification

This document defines the specific targets and parsing logic for the `CrawlerService`.

## 1. Target Sites & Strategy

We will start with **KAIST** (School of Computing) as the primary target for the MVP.

### Target A: KAIST School of Computing - Research News
*   **URL:** `https://cs.kaist.ac.kr/news/research` (Example URL - *Needs verification*)
*   **Type:** Static/Dynamic (Playwright required for pagination)
*   **Frequency:** Weekly

## 2. DOM Selectors (CSS)

*Note: These selectors are hypothetical and must be verified by inspecting the actual page source during implementation.*

### List Page (The list of articles)
*   **Item Container:** `.board-list-item` or `tr`
*   **Link Selector:** `a.post-link` (Extract `href`)
*   **Date Selector:** `span.date` or `td.date`

### Detail Page (The actual article)
*   **Title:** `h1.post-title` or `.subject`
*   **Content:** `div.post-content` or `.view-content`
    *   *Constraint:* Must exclude "Previous/Next Post" navigation links.
    *   *Constraint:* Must exclude footer and sidebar text.
*   **Images:** `div.post-content img` (Extract `src` for thumbnail)

## 3. Data Cleaning Rules

1.  **Whitespace:** Replace multiple newlines/spaces with a single newline.
2.  **Noise Removal:** Remove text like "Print", "Share", "List".
3.  **Length Check:** Discard content shorter than 200 characters (likely an error or empty post).

## 4. Error Handling Policy

*   **Timeout:** 30 seconds per page.
*   **Retries:** 3 times with 2-second delay.
*   **User-Agent:** Rotate User-Agent string to avoid blocking.
*   **Robots.txt:** Respect `Disallow` rules if present.

## 5. Fallback Strategy (Resilience)

If CSS selectors fail (e.g., site renewal):
1.  **Primary:** Use defined CSS selectors.
2.  **Secondary (Fallback):** Extract full `<body>` text and use a lightweight LLM (e.g., GPT-3.5-turbo) to parse the main content.
    *   *Prompt:* "Extract the main article content from this HTML text, excluding navigation and footers."
