# Web Scraping & Data Extraction Test

> **Technical assessment submission** for [SalesNow](https://salesnow.jp/) (株式会社 SalesNow) — Japan's leading B2B corporate database SaaS.

---

## Overview

This repository contains my solution for SalesNow's **Web Scraping and Data Extraction** practical test. The assignment evaluates:

- Data collection capability in real-world scenarios
- Technical decision-making and tool selection
- Effective use of generative AI

**Deadline:** Submit within **9 hours** from the start time. Evaluation is based on commits at the designated deadline. Partial work is acceptable — commit progress before the deadline so the approach and process can be reviewed.

---

## Assignment Summary (Translated from Japanese)

### Task A — Scrape Corporate Websites (Required)

Scrape official websites for **10 listed companies** by following links from the input URL list. Use generative AI to extract the specified fields. Sites differ in design and structure — the solution must be **generic and reusable**.

| Company | URL |
|---------|-----|
| Nissui (ニッスイ) | https://www.nissui.co.jp/ |
| Umios (Ｕｍｉｏｓ) | https://www.umios.com/ |
| Yukiguni Factory (ユキグニファクトリー) | https://www.yukiguni-factory.co.jp/ |
| Sakata Seed (サカタのタネ) | https://www.sakataseed.co.jp/ |
| Hokto (ホクト) | https://www.hokto-kinoko.co.jp/ |
| Sho-Bond Holdings (ショーボンドホールディングス) | https://www.sho-bondhd.jp/ |
| Mirait One (ミライト・ワン) | https://www.mirait-one.com/ |
| Tama Home (タマホーム) | https://www.tamahome.jp/ |
| Kyokuyo (極洋) | https://www.kyokuyo.co.jp/ |
| Nippon Aqua (日本アクア) | https://www.n-aqua.jp/ |

**Fields to extract:**

| Field (JP) | Field (EN) |
|------------|------------|
| 本社住所 | Head office address |
| 代表氏名 | Representative name |
| 資本金 | Capital stock |
| 設立年月 | Date of establishment |

> **Note:** The original test requires setup and execution instructions in **Japanese** in this README. A Japanese section (`## 環境構築・実行方法`) will be added once the implementation is complete.

---

### Task B — Bot-Protected Site (Optional / Bonus)

**Only after Task A is fully complete.**

Attempt to collect data from a site that blocks typical scraping:

- **Target:** https://vn.indeed.com/jobs?q=remote

Document in `report.md`:

1. What bot protection mechanisms are in place
2. What approaches were tried and the outcomes

---

### Technical Selection & Approach Comparison

Compare multiple approaches (libraries, frameworks, no-code tools, generative AI APIs, etc.).

Examples: Python + Playwright + LangChain, TypeScript + Firecrawl + Vercel AI SDK, Dify, n8n.

Evaluate along three axes and document the selection rationale in `report.md`:

| Axis | Criteria |
|------|----------|
| **Cost** | Development time, infrastructure cost, tool fees |
| **Speed** | Development velocity and runtime scraping speed |
| **Quality / Completeness** | Accuracy and coverage (minimize missed data) |

---

### Generative AI Usage

Use of ChatGPT, Claude, GitHub Copilot, or similar tools is **allowed**.

**Required:** If using chat-based AI (ChatGPT, Claude, etc.), submit prompt and response history (or share links) under `prompts/`.

---

### Submission Requirements

| Item | Detail |
|------|--------|
| Repository | Private GitHub repository |
| Collaborators | `atsunori0406`, `yuji-um`, `salesnow-tomohiro` |
| Evaluation time | Commits at the designated deadline |

**Recommended directory structure:**

```
├── prompts/      # Generative AI prompt history (.txt)
├── result/       # Scraped data (CSV or JSON)
├── src/          # Source code
├── README.md     # Setup & execution (Japanese required by test)
└── report.md     # Tech comparison & Task B findings
```

---

### Evaluation Criteria

| Criterion | Description |
|-----------|-------------|
| **Understanding** | Correct grasp of the assignment |
| **Design** | Sound technical choices balancing cost, speed, and quality |
| **AI utilization** | Efficient AI-assisted workflow |
| **Documentation** | Clear documentation for third parties |

---

## Repository Structure

```
salesnow-jp-web-scraping-test/
├── prompts/          # AI prompt logs
├── result/           # Output data (CSV/JSON)
├── src/              # Scraper & extraction code
├── README.md         # This file
└── report.md         # Tech comparison & Task B report
```

---

## Setup & Execution

> **Status:** Implementation in progress.

Japanese setup and run instructions (`## 環境構築・実行方法`) will be added here after the scraper is implemented.

---

## License

Private assessment submission for SalesNow. Not for public distribution.
