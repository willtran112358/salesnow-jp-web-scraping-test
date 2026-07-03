# Web Scraping & Data Extraction Test

<p align="center">
  <img src="docs/assets/salesnow.svg" alt="SalesNow" width="180"/>
  <br/><br/>
  <strong>Technical assessment submission</strong> for <a href="https://salesnow.jp/">SalesNow</a> (株式会社 SalesNow)
  <br/>Japan's No.1 B2B corporate database SaaS — 1,400万+ company records
</p>

<p align="center">
  <img src="docs/assets/cert-badge-01.webp" alt="No.1 Certification" width="140"/>
  <img src="docs/assets/cert-badge-02.webp" alt="Customer Satisfaction" width="140"/>
  <img src="docs/assets/badge-appexchange.png" alt="Salesforce AppExchange" width="100"/>
</p>

---

## Overview

This repository contains my solution for SalesNow's **Web Scraping and Data Extraction** practical test — the same core capability that powers [SalesNow's company enrichment](https://salesnow.jp/) (本社住所, 資本金, 代表者, 設立年月, and more).

| Evaluated Skill | How This Repo Demonstrates It |
|-----------------|-------------------------------|
| Data collection | Generic scraper across 10 heterogeneous JP corporate sites |
| Technical decisions | Documented comparison in [`report.md`](report.md) and [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) |
| Generative AI | Prompt templates + saved history in `prompts/` |

---

## Business Context

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {
  'primaryColor': '#DBEAFE',
  'secondaryColor': '#D1FAE5',
  'tertiaryColor': '#FEF3C7'
}}}%%
flowchart TB
    subgraph CHALLENGE["Sales Challenge"]
        C1["Manual company research"]
        C2["Inconsistent CRM data"]
        C3["Low targeting accuracy"]
    end

    subgraph SALESNOW["SalesNow Platform"]
        S1["1,400万+ company DB"]
        S2["AI-powered enrichment"]
        S3["SFA/CRM auto-sync"]
    end

    subgraph TEST["This Assessment"]
        T1["Scrape 10 corporate sites"]
        T2["Extract 4 core fields"]
        T3["Handle bot protection"]
    end

    C1 & C2 & C3 --> SALESNOW
    SALESNOW -.->|"validates engineering skill"| TEST

    style CHALLENGE fill:#FEE2E2,stroke:#EF4444
    style SALESNOW fill:#DBEAFE,stroke:#2563EB
    style TEST fill:#D1FAE5,stroke:#10B981
```

---

## Solution Architecture

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'fontSize': '13px'}}}%%
flowchart LR
    subgraph IN["Input"]
        U["10 Company URLs"]
    end

    subgraph PIPE["Pipeline"]
        D["discover.py"]
        F["fetcher.py"]
        E["extractor.py"]
        A["ai_extractor.py"]
    end

    subgraph OUT["Output"]
        J["companies.json"]
        C["companies.csv"]
        P["prompts/"]
    end

    U --> D --> F --> E --> A --> J & C & P

    style IN fill:#E0F2FE,stroke:#0284C7
    style PIPE fill:#F0FDF4,stroke:#16A34A
    style OUT fill:#FEF9C3,stroke:#CA8A04
```

> Full diagrams: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)

---

## Database Design

Logical ER model for crawled data across corporate sites (Task A) and Indeed (Task B):

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'fontSize': '12px'}}}%%
erDiagram
    DATA_SOURCE ||--o{ COMPANY_SEED : seeds
    COMPANY_SEED ||--o{ PROFILE_PAGE : discovers
    PROFILE_PAGE ||--o{ FIELD_VALUE : extracts
    COMPANY_SEED ||--|| COMPANY_RECORD : exports
    DATA_SOURCE ||--o{ INDEED_SCRAPE : "Task B"
    INDEED_SCRAPE ||--o{ JOB_LISTING : yields

    COMPANY_RECORD {
        string name_jp "企業名"
        string head_office_address "本社住所"
        string representative_name "代表氏名"
        string capital_stock "資本金"
        string establishment_date "設立年月"
    }

    JOB_LISTING {
        string title "求人タイトル"
        string method "httpx | playwright"
    }
```

Full schema, source mapping & field dictionary → [`docs/DATABASE.md`](docs/DATABASE.md)

---

## Assignment Summary

### Task A — Scrape Corporate Websites (Required)

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

| Field (JP) | Field (EN) |
|------------|------------|
| 本社住所 | Head office address |
| 代表氏名 | Representative name |
| 資本金 | Capital stock |
| 設立年月 | Date of establishment |

### Task B — Bot-Protected Site (Bonus)

Target: https://vn.indeed.com/jobs?q=remote — documented in [`report.md`](report.md)

---

## Repository Structure

```
salesnow-jp-web-scraping-test/
├── docs/
│   ├── ARCHITECTURE.md    # Visual design docs & mermaid diagrams
│   ├── DATABASE.md        # ER model for multi-source crawled data
│   └── assets/            # SalesNow reference images
├── prompts/               # AI prompt & response history
├── result/                # Scraped output (CSV/JSON)
├── src/                   # Scraper source code
│   ├── main.py            # CLI entrypoint
│   ├── discover.py        # Profile page discovery
│   ├── fetcher.py         # HTTP client
│   ├── extractor.py       # Rule-based field parsing
│   ├── ai_extractor.py    # LLM extraction layer
│   └── indeed_scraper.py  # Task B bot-protection attempt
├── README.md
└── report.md
```

---

## Setup & Execution

### Prerequisites

- Python 3.11+
- Optional: `OPENAI_API_KEY` for AI-enhanced extraction

### Install

```bash
pip install -r requirements.txt
python -m playwright install chromium   # JS pages (Umios) + Task B
```

### Run

```bash
# Task A only
python -m src.main --task a

# Task B only
python -m src.main --task b

# Both tasks
python -m src.main --task all
```

### Verified execution (screenshots)

Real terminal output from a successful run on Windows PowerShell:

| Task A — 10 companies | Task B — Indeed | Full pipeline |
|:---:|:---:|:---:|
| ![Task A run](docs/screenshots/task-a-run.png) | ![Task B run](docs/screenshots/task-b-run.png) | ![Full pipeline run](docs/screenshots/full-pipeline-run.png) |

See also [`docs/screenshots/README.md`](docs/screenshots/README.md) and raw logs in `docs/run-logs/`.

### Optional: Enable AI extraction

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_MODEL="gpt-4o-mini"   # default
python -m src.main --task a
```

---

## 環境構築・実行方法

### 必要環境

- Python 3.11 以上
- 任意: OpenAI API キー（AI による抽出を有効化する場合）

### セットアップ

```bash
pip install -r requirements.txt
python -m playwright install chromium   # JSページ（Umios等）+ 課題B
```

### 実行方法

```bash
# 課題Aのみ（10社の企業情報スクレイピング）
python -m src.main --task a

# 課題Bのみ（Indeed ボット対策サイト）
python -m src.main --task b

# 両方実行
python -m src.main --task all
```

### 出力ファイル

| ファイル | 内容 |
|----------|------|
| `result/companies.csv` | 10社分の抽出結果（Excel対応 UTF-8 BOM） |
| `result/companies.json` | 同上 JSON 形式 |
| `prompts/task_a_*.txt` | 各社の AI プロンプト履歴 |
| `prompts/task_a_*_response.txt` | AI レスポンスまたはルールベース結果 |
| `result/indeed_remote_jobs.json` | 課題Bの調査結果 |
| `prompts/task_b_*.txt` | 課題Bのプロンプト・結果 |
| `docs/screenshots/` | 実行成功時のターミナル画面キャプチャ |

### 実行確認（スクリーンショット）

実際の PowerShell 実行結果: [`docs/screenshots/task-a-run.png`](docs/screenshots/task-a-run.png)

### 処理の流れ

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'fontSize': '12px'}}}%%
flowchart TD
    A["企業URL読み込み"] --> B["プロフィールページ自動発見"]
    B --> C["HTML取得（0.8秒間隔）"]
    C --> D["ルールベース抽出"]
    D --> E{"OpenAI API?"}
    E -->|あり| F["AIで構造化抽出"]
    E -->|なし| G["ルール結果のみ"]
    F --> H["CSV/JSON出力"]
    G --> H

    style A fill:#DBEAFE,stroke:#2563EB
    style H fill:#D1FAE5,stroke:#10B981
```

---

## Main Code Flow

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'fontSize': '11px'}}}%%
sequenceDiagram
    participant M as main.py
    participant D as discover.py
    participant F as fetcher.py
    participant X as extractor.py
    participant AI as ai_extractor.py

    M->>D: discover_profile_urls()
    D->>F: GET homepage + candidate pages
    M->>AI: extract_with_ai()
    AI->>X: extract_from_html() + extract_from_text()
    AI->>AI: OpenAI or rule-based fallback
    M->>M: Save CSV + JSON
```

---

## Technology Selection

| Approach | Cost | Speed | Quality | Used |
|----------|:----:|:-----:|:-------:|:----:|
| Python httpx + BeautifulSoup + rules | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ✅ |
| + OpenAI structured extraction | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ✅ |
| TypeScript Firecrawl + AI SDK | ⭐ | ⭐⭐ | ⭐⭐⭐ | — |
| n8n / Dify no-code | ⭐⭐ | ⭐ | ⭐⭐ | — |

See [`report.md`](report.md) for full rationale.

---

## Generative AI Usage

Chat-based AI (Cursor / Claude) was used for development. Per-company extraction prompts are saved under `prompts/`.

---

## Submission

| Item | Detail |
|------|--------|
| Repository | https://github.com/willtran112358/salesnow-jp-web-scraping-test |
| Collaborators | `atsunori0406`, `yuji-um`, `salesnow-tomohiro` |

---

## License

Private assessment submission for SalesNow. Not for public distribution.

<p align="center">
  <img src="docs/assets/data-volume.webp" alt="SalesNow Data" width="400"/>
  <br/>
  <em>© SalesNow Co., Ltd. — images used for assessment documentation only.</em>
</p>
