# Architecture & Visual Design Reference

> Solution design documentation for the SalesNow Web Scraping & Data Extraction technical test.

<p align="center">
  <img src="assets/salesnow.svg" alt="SalesNow Logo" width="200"/>
  <br/>
  <img src="assets/hero.webp" alt="SalesNow Hero" width="600"/>
</p>

---

## 1. Business Context — Why SalesNow Cares About Web Scraping

[SalesNow](https://salesnow.jp/) is Japan's **No.1 B2B corporate database** (1,400万+ records). Their product automates exactly what this test evaluates: collecting structured company data from diverse corporate websites.

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {
  'primaryColor': '#E8F4FD',
  'primaryTextColor': '#1a1a2e',
  'primaryBorderColor': '#2563EB',
  'secondaryColor': '#FEF3C7',
  'tertiaryColor': '#D1FAE5',
  'lineColor': '#64748B',
  'fontSize': '14px'
}}}%%
mindmap
  root((SalesNow Platform))
    Data Collection
      Web scraping pipelines
      AI field extraction
      1,400万+ company records
    Sales Enablement
      Target list creation
      SFA/CRM enrichment
      Intent & hiring signals
    AI Workflows
      Company profile summaries
      Form auto-fill
      Slack re-engagement alerts
    Integration
      Salesforce / HubSpot
      API & MCP
      Custom AI agents
```

### Sales Pain Points → Test Alignment

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {
  'primaryColor': '#FEE2E2',
  'secondaryColor': '#DBEAFE',
  'tertiaryColor': '#D1FAE5'
}}}%%
flowchart LR
    subgraph PAIN["😰 Sales Pain Points"]
        P1["Low list accuracy"]
        P2["Messy CRM data"]
        P3["Manual research time"]
    end

    subgraph TEST["🎯 This Test Evaluates"]
        T1["Generic scraper design"]
        T2["Structured field extraction"]
        T3["AI-assisted parsing"]
    end

    subgraph VALUE["✅ SalesNow Value"]
        V1["1-min list creation"]
        V2["Auto CRM enrichment"]
        V3["Instant company profiles"]
    end

    P1 --> T1 --> V1
    P2 --> T2 --> V2
    P3 --> T3 --> V3

    style PAIN fill:#FEE2E2,stroke:#EF4444
    style TEST fill:#DBEAFE,stroke:#2563EB
    style VALUE fill:#D1FAE5,stroke:#10B981
```

---

## 2. Assignment Requirements Map

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'fontSize': '13px'}}}%%
flowchart TB
    subgraph TASK_A["📋 Task A — Required"]
        A1["10 listed company URLs"]
        A2["Discover profile pages"]
        A3["Extract 4 fields per company"]
        A4["Output CSV + JSON"]
        A5["Save AI prompts"]
    end

    subgraph FIELDS["🏢 Fields to Extract"]
        F1["本社住所 — Head office address"]
        F2["代表氏名 — Representative name"]
        F3["資本金 — Capital stock"]
        F4["設立年月 — Date of establishment"]
    end

    subgraph TASK_B["🛡️ Task B — Bonus"]
        B1["Indeed Vietnam bot-protected site"]
        B2["Document protection mechanisms"]
        B3["Compare httpx vs Playwright"]
    end

    A1 --> A2 --> A3 --> FIELDS
    A3 --> A4
    A3 --> A5
    A4 --> TASK_B

    style TASK_A fill:#DBEAFE,stroke:#2563EB,color:#1e3a5f
    style FIELDS fill:#FEF3C7,stroke:#F59E0B,color:#78350f
    style TASK_B fill:#EDE9FE,stroke:#7C3AED,color:#4c1d95
```

---

## 3. Solution Design — High-Level Architecture

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'fontSize': '13px'}}}%%
flowchart TB
    subgraph INPUT["📥 Input Layer"]
        URL["companies.json<br/>10 seed URLs"]
        ENV["Environment<br/>OPENAI_API_KEY optional"]
    end

    subgraph CORE["⚙️ Processing Pipeline"]
        MAIN["main.py<br/>CLI orchestrator"]
        DISC["discover.py<br/>Profile URL discovery"]
        FETCH["fetcher.py<br/>HTTP client + rate limit"]
        EXT["extractor.py<br/>Rule-based HTML parsing"]
        AI["ai_extractor.py<br/>LLM extraction + prompts"]
    end

    subgraph OUTPUT["📤 Output Layer"]
        CSV["result/companies.csv"]
        JSON["result/companies.json"]
        PRM["prompts/*.txt"]
        RPT["report.md"]
    end

    subgraph BONUS["🎁 Task B"]
        INDEED["indeed_scraper.py"]
        INJSON["result/indeed_remote_jobs.json"]
    end

    URL --> MAIN
    ENV --> AI
    MAIN --> DISC --> FETCH
    FETCH --> EXT --> AI
    AI --> CSV
    AI --> JSON
    AI --> PRM
    MAIN --> INDEED --> INJSON
    INDEED --> RPT

    style INPUT fill:#E0F2FE,stroke:#0284C7
    style CORE fill:#F0FDF4,stroke:#16A34A
    style OUTPUT fill:#FEF9C3,stroke:#CA8A04
    style BONUS fill:#F3E8FF,stroke:#9333EA
```

### Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Generic & reusable** | Keyword-based link scoring + fallback path candidates |
| **Resilient extraction** | Rule-based parser first, AI enrichment second |
| **Transparent AI usage** | Every prompt/response saved to `prompts/` |
| **Graceful degradation** | Works without API key via rule-based fallback |
| **Polite crawling** | Configurable delay between requests (default 0.8s) |

---

## 4. Database ER Model

Multi-source crawled data is modeled as seed → page → field → record. See [`DATABASE.md`](DATABASE.md) for the full schema.

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'fontSize': '12px'}}}%%
flowchart TB
    subgraph SOURCES["Data Sources"]
        DS1["corporate_web<br/>10 JP listed companies"]
        DS2["indeed_vn<br/>bot-protected jobs"]
    end

    subgraph TASK_A["Task A Pipeline"]
        SEED["COMPANY_SEED"]
        PAGE["PROFILE_PAGE"]
        FIELD["FIELD_VALUE"]
        REC["COMPANY_RECORD"]
    end

    subgraph TASK_B["Task B Pipeline"]
        INDEED["INDEED_SCRAPE"]
        ATTEMPT["SCRAPE_ATTEMPT"]
        JOB["JOB_LISTING"]
    end

    DS1 --> SEED --> PAGE --> FIELD --> REC
    DS2 --> INDEED --> ATTEMPT --> JOB

    style SOURCES fill:#FEF3C7,stroke:#F59E0B
    style TASK_A fill:#DBEAFE,stroke:#2563EB
    style TASK_B fill:#EDE9FE,stroke:#7C3AED
```

---

## 5. Technology Selection Matrix

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'fontSize': '12px'}}}%%
quadrantChart
    title Technology Approach Comparison
    x-axis Low Development Cost --> High Development Cost
    y-axis Low Data Quality --> High Data Quality
    quadrant-1 Premium / Complex
    quadrant-2 Best Balance
    quadrant-3 Quick & Dirty
    quadrant-4 High Cost Low Return
    Python httpx + BS4 + Rules: [0.25, 0.55]
    Python + Playwright + OpenAI: [0.55, 0.85]
    TypeScript Firecrawl + AI SDK: [0.65, 0.80]
    n8n / Dify no-code: [0.35, 0.45]
    Manual copy-paste: [0.10, 0.30]
```

| Approach | Cost | Speed | Quality | Selected |
|----------|:----:|:-----:|:-------:|:--------:|
| **Python httpx + BeautifulSoup + rules** | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ✅ Base layer |
| **+ OpenAI structured extraction** | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ✅ AI layer |
| TypeScript + Firecrawl + Vercel AI SDK | ⭐ | ⭐⭐ | ⭐⭐⭐ | ❌ Higher setup cost |
| n8n / Dify no-code | ⭐⭐ | ⭐ | ⭐⭐ | ❌ Less control for 10 heterogeneous sites |
| Playwright-only (no AI) | ⭐⭐ | ⭐ | ⭐⭐ | ❌ Slower, still needs parsing logic |

**Selection rationale:** Python stack offers the best balance for a 9-hour test — fast to develop, no browser infra for Task A, and optional LLM for ambiguous layouts.

---

## 6. Engineering — Main Function Flow (Task A)

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'fontSize': '12px'}}}%%
sequenceDiagram
    autonumber
    actor User
    participant Main as main.py
    participant Disc as discover.py
    participant Fetch as fetcher.py
    participant Ext as extractor.py
    participant AI as ai_extractor.py
    participant Out as result/

    User->>Main: python -m src.main --task a
    Main->>Main: load_companies()

    loop For each of 10 companies
        Main->>Disc: discover_profile_urls(seed_url)
        Disc->>Fetch: GET homepage
        Fetch-->>Disc: HTML
        Disc->>Disc: Score links by keywords<br/>+ fallback path candidates
        Disc-->>Main: profile_urls[]

        loop For each profile URL
            Main->>Fetch: get_text(url)
            Fetch-->>Main: html_pages[]
        end

        Main->>Disc: collect_page_texts(urls)
        Disc-->>Main: plain_text

        Main->>AI: extract_with_ai(name, url, pages, text)
        AI->>Ext: extract_from_html() per page
        AI->>Ext: extract_from_text()
        AI->>AI: build_prompt() → save prompts/
        alt OPENAI_API_KEY set
            AI->>AI: OpenAI chat completion
            AI->>AI: merge AI + rule results
        else No API key
            AI->>AI: rule-based only
        end
        AI-->>Main: extracted fields + source_url

        Main->>Main: to_japanese_record()
    end

    Main->>Out: Write companies.json + companies.csv
    Main-->>User: Done ✓
```

### Profile URL Discovery Logic

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'fontSize': '12px'}}}%%
flowchart TD
    START(["discover_profile_urls()"]) --> SEED{"Pre-configured<br/>profile_urls?"}
    SEED -->|Yes| ADD1["Add with score 100"]
    SEED -->|No| FETCH
    ADD1 --> FETCH

    FETCH["Fetch homepage HTML"] --> PARSE["Parse all &lt;a&gt; tags"]
    PARSE --> FILTER{"Same domain?"}
    FILTER -->|No| PARSE
    FILTER -->|Yes| SCORE["Score by keywords:<br/>会社概要, profile, outline..."]
    SCORE --> RANK["Sort by score DESC"]
    RANK --> FALLBACK["Add PROFILE_PATH_CANDIDATES<br/>e.g. /company/outline/"]
    FALLBACK --> TOP["Return top 6 URLs"]

    style START fill:#DBEAFE,stroke:#2563EB
    style TOP fill:#D1FAE5,stroke:#10B981
```

### Field Extraction Pipeline

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'fontSize': '12px'}}}%%
flowchart LR
    HTML["Raw HTML"] --> BS4["BeautifulSoup"]
    BS4 --> TBL["Table rows th/td"]
    BS4 --> DL["Definition lists dt/dd"]
    BS4 --> DIV["Labeled divs"]
    TBL --> PAIRS["label → value pairs"]
    DL --> PAIRS
    DIV --> PAIRS
    PAIRS --> MATCH["Match against FIELD_LABELS"]
    MATCH --> MERGE["Merge with regex text patterns"]
    MERGE --> RULES["Rule-based result"]

    RULES --> AI{"OpenAI available?"}
    AI -->|Yes| LLM["GPT structured JSON extraction"]
    AI -->|No| OUT
    LLM --> OUT["Final 4 fields"]

    style HTML fill:#FEF3C7,stroke:#F59E0B
    style RULES fill:#DBEAFE,stroke:#2563EB
    style OUT fill:#D1FAE5,stroke:#10B981
```

---

## 7. Task B — Bot Protection Flow

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'fontSize': '12px'}}}%%
flowchart TD
    START(["run_task_b()"]) --> H["Approach 1: httpx static GET"]
    H --> HCHK{"Status 403/429?<br/>CAPTCHA signals?"}
    HCHK -->|Blocked| PW
    HCHK -->|OK| HSUCCESS["Extract job titles from HTML"]

    PW["Approach 2: Playwright headless Chromium"] --> PCHK{"Page title / CAPTCHA?<br/>jobTitle elements?"}
    PCHK --> PARTIAL["Partial or full job list"]
    PCHK --> BLOCKED["Document blocked signals"]

    HSUCCESS --> REPORT
    PARTIAL --> REPORT
    BLOCKED --> REPORT["Write indeed_remote_jobs.json<br/>+ report.md findings"]

    style START fill:#EDE9FE,stroke:#7C3AED
    style REPORT fill:#D1FAE5,stroke:#10B981
    style BLOCKED fill:#FEE2E2,stroke:#EF4444
```

---

## 8. Data Flow — End to End

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'fontSize': '12px'}}}%%
flowchart LR
    subgraph SOURCES["🌐 Corporate Websites"]
        S1["nissui.co.jp"]
        S2["umios.com"]
        S3["...8 more"]
    end

    subgraph PIPELINE["Pipeline"]
        P["Scraper + AI"]
    end

    subgraph ARTIFACTS["Deliverables"]
        D1["companies.csv"]
        D2["companies.json"]
        D3["prompts/"]
        D4["report.md"]
    end

  subgraph SALESNOW_CONTEXT["SalesNow Product Parallels"]
        SN["企業詳細ページ<br/>基本情報・資本金・所在地"]
    end

    S1 & S2 & S3 --> P --> D1 & D2 & D3 & D4
    D2 -.->|"Same fields SalesNow enriches"| SN

    style SOURCES fill:#E0F2FE,stroke:#0284C7
    style PIPELINE fill:#F0FDF4,stroke:#16A34A
    style ARTIFACTS fill:#FEF9C3,stroke:#CA8A04
    style SALESNOW_CONTEXT fill:#FCE7F3,stroke:#DB2777
```

---

## 9. Module Dependency Graph

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'fontSize': '12px'}}}%%
flowchart BT
    config["config.py<br/>paths, headers, keywords"]
    companies["companies.py<br/>load company list"]
    fetcher["fetcher.py<br/>httpx client"]
    discover["discover.py"]
    extractor["extractor.py"]
    ai_extractor["ai_extractor.py"]
    indeed["indeed_scraper.py"]
    main["main.py"]

    config --> fetcher
    config --> discover
    config --> extractor
    config --> ai_extractor
    config --> indeed
    companies --> main
    fetcher --> discover
    fetcher --> ai_extractor
    discover --> main
    extractor --> ai_extractor
    ai_extractor --> main
    indeed --> main

    style main fill:#2563EB,color:#fff,stroke:#1D4ED8
    style config fill:#64748B,color:#fff
```

---

<p align="center">
  <img src="assets/no1title01.svg" alt="No.1 Badge" width="120"/>
  <img src="assets/badge-appexchange.png" alt="AppExchange" width="80"/>
  <img src="assets/data-volume.webp" alt="Data Volume" width="300"/>
</p>

*Documentation for SalesNow technical assessment — Will Tran*
