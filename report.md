# Technical Report — SalesNow Web Scraping Test

## 1. Technology Comparison

| Approach | Cost | Speed | Quality / Completeness | Selected? |
|----------|------|-------|------------------------|-----------|
| **Python + httpx + BeautifulSoup** (chosen baseline) | Low — no paid APIs, minimal infra | Fast — ~2–3 min for 10 sites | High for static HTML tables; weak on JS-only pages | **Yes (core)** |
| **Python + Playwright** | Medium — browser install, higher RAM | Slower — ~15–20s per JS page | High when DOM is rendered (e.g. Umios profile) | **Yes (fallback)** |
| **PDF extraction (pypdf)** | Low | Fast | High for IR PDFs (Kyokuyo company profile) | **Yes (supplement)** |
| **OpenAI API + prompt** | Medium — API cost per company | Fast inference | Excellent if API available; prompts saved in `prompts/` | Optional |
| **TypeScript + Firecrawl** | High — SaaS fees | Fast setup | Good managed extraction | No |
| **Dify / n8n no-code** | Medium — hosting + LLM nodes | Fast prototyping | Good for demos, harder to version-control | No |

### Selection Rationale

1. **Cost:** A pure-Python pipeline keeps the solution free to run locally and easy for reviewers to reproduce. Playwright is only invoked for JavaScript-heavy pages (Umios). No mandatory paid LLM API — rule-based extraction plus saved prompts satisfies the AI documentation requirement.
2. **Speed:** httpx fetches are parallelizable and complete 10 companies in under 3 minutes. Playwright adds ~30s only where needed.
3. **Quality:** Japanese corporate sites commonly expose 会社概要 in HTML `<table>` / `<dl>` structures. Combining link discovery, known profile URLs, PDF fallback, and Playwright covers all 10 targets with 4/4 fields each.

### Architecture

```
seed URL → link discovery → fetch HTML (httpx)
                         → render JS (Playwright, if needed)
                         → fetch PDF (pypdf, if configured)
                         → extract fields (table/dl/regex)
                         → optional LLM (OPENAI_API_KEY)
                         → result/companies.json + .csv
```

---

## 2. Task B — Indeed Vietnam (Bot-Protected Site)

**Target:** https://vn.indeed.com/jobs?q=remote

### Bot Protection Observed

| Mechanism | Evidence |
|-----------|----------|
| Cloudflare / anti-bot **challenge** page | `"challenge"` string in HTML from both httpx and Playwright |
| Rate limiting / fingerprinting | Identical job titles repeated in httpx sample (8 duplicates) |
| JavaScript-rendered job cards | httpx returns large HTML (1.2MB) but incomplete job metadata |
| Session / cookie requirements | Static fetch gets partial listing; full detail pages need browser context |

### Approaches Tried & Results

| Method | Result | Job titles captured |
|--------|--------|---------------------|
| **httpx** (static HTTP) | Partial — 8 titles, challenge signal detected | Mostly duplicate "NHÂN VIÊN CHĂM SÓC KHÁCH HÀNG REMOTE NHÀ" |
| **Playwright** (headless Chromium) | Partial — 15 unique titles, challenge signal still present | Data Entry Specialist, Online ESL Tutors, Freelance Data Operations Specialist, etc. |

**Conclusion:** Indeed serves enough DOM for a headless browser to read job titles, but applies bot protection (challenge/fingerprinting). Playwright outperformed raw httpx for title diversity. Full job-detail scraping (salary, description) would require authenticated sessions, residential proxies, or official APIs — out of scope for a fair-use technical test.

Full machine-readable output: [`result/indeed_remote_jobs.json`](result/indeed_remote_jobs.json)

---

## 3. AI Utilization

- Extraction prompts for each company are saved under `prompts/task_a_*.txt`.
- Rule-based parsing was used as the primary extractor (reproducible without API keys).
- Set `OPENAI_API_KEY` to enable LLM post-processing of page text.

---

## 4. Task A Results Summary

| Company | Address | Representative | Capital | Established |
|---------|---------|----------------|---------|-------------|
| ニッスイ | ✓ | ✓ | ✓ | ✓ |
| Ｕｍｉｏｓ | ✓ | ✓ | ✓ | ✓ |
| ユキグニファクトリー | ✓ | ✓ | ✓ | ✓ |
| サカタのタネ | ✓ | ✓ | ✓ | ✓ |
| ホクト | ✓ | ✓ | ✓ | ✓ |
| ショーボンドHD | ✓ | ✓ | ✓ | ✓ |
| ミライト・ワン | ✓ | ✓ | ✓ | ✓ |
| タマホーム | ✓ | ✓ | ✓ | ✓ |
| 極洋 | ✓ | ✓ | ✓ | ✓ |
| 日本アクア | ✓ | ✓ | ✓ | ✓ |

Output files: `result/companies.json`, `result/companies.csv`
