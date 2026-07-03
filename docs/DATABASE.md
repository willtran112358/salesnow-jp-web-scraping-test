# Database Design — Crawled & Extracted Data

> Logical data model for multi-source scraping outputs (Task A corporate sites + Task B Indeed).

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {
  'primaryColor': '#DBEAFE',
  'primaryTextColor': '#1e3a5f',
  'primaryBorderColor': '#2563EB',
  'lineColor': '#64748B',
  'fontSize': '13px'
}}}%%
erDiagram
    DATA_SOURCE ||--o{ COMPANY_SEED : provides
    DATA_SOURCE ||--o{ SCRAPE_RUN : triggers
    COMPANY_SEED ||--o{ PROFILE_PAGE : "discovers (1:N)"
    SCRAPE_RUN ||--o{ PROFILE_PAGE : fetches
    PROFILE_PAGE ||--o{ FIELD_VALUE : extracts
    COMPANY_SEED ||--|| COMPANY_RECORD : "exports (1:1)"
    FIELD_VALUE }o--|| COMPANY_RECORD : aggregates
    COMPANY_SEED ||--o{ AI_PROMPT_LOG : "logs (1:N)"
    DATA_SOURCE ||--o{ INDEED_SCRAPE : "Task B"
    INDEED_SCRAPE ||--o{ SCRAPE_ATTEMPT : tries
    SCRAPE_ATTEMPT ||--o{ JOB_LISTING : "may yield"

    DATA_SOURCE {
        string source_id PK "corporate_web | indeed_vn"
        string source_name "表示名"
        string base_url "起点URL"
        string source_type "html | bot_protected"
    }

    COMPANY_SEED {
        int seed_id PK
        string source_id FK
        string name_jp "企業名"
        string name_en "英語名"
        string seed_url "公式サイトURL"
        boolean use_browser "Playwright要否"
    }

    PROFILE_PAGE {
        int page_id PK
        int seed_id FK
        int run_id FK
        string page_url "取得元ページ"
        string fetch_method "httpx | playwright | pdf"
        int http_status "HTTPステータス"
        datetime fetched_at "取得日時"
    }

    FIELD_VALUE {
        int field_id PK
        int seed_id FK
        int page_id FK
        string field_key "head_office_address等"
        string field_label_jp "本社住所等"
        string raw_value "抽出値"
        string extractor "rules | openai | pdf"
        float confidence "0-1 任意"
    }

    COMPANY_RECORD {
        int record_id PK
        int seed_id FK "UNIQUE"
        string name_jp "企業名"
        string seed_url "URL"
        string source_page_url "取得元ページ"
        string head_office_address "本社住所"
        string representative_name "代表氏名"
        string capital_stock "資本金"
        string establishment_date "設立年月"
        datetime exported_at "出力日時"
    }

    AI_PROMPT_LOG {
        int prompt_id PK
        int seed_id FK
        string prompt_file "prompts/task_a_*.txt"
        string response_file "prompts/*_response.txt"
        string model "gpt-4o-mini等"
        datetime created_at "生成日時"
    }

    SCRAPE_RUN {
        int run_id PK
        string source_id FK
        string task "a | b | all"
        datetime started_at "開始"
        datetime finished_at "終了"
        string status "success | partial | failed"
    }

    INDEED_SCRAPE {
        int indeed_id PK
        int run_id FK
        string target_url "vn.indeed.com/jobs?q=remote"
        string summary "結果サマリー"
    }

    SCRAPE_ATTEMPT {
        int attempt_id PK
        int indeed_id FK
        string method "httpx | playwright"
        boolean success "成功フラグ"
        string blocked_signals "captcha,403等"
        int job_count "取得件数"
    }

    JOB_LISTING {
        int job_id PK
        int attempt_id FK
        string title "求人タイトル"
        int rank "表示順"
    }
```

---

## Source → Storage Mapping

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'fontSize': '12px'}}}%%
flowchart LR
    subgraph SRC_A["🌐 Task A — Corporate Web"]
        S1["src/companies.json<br/><i>COMPANY_SEED</i>"]
        S2["discover.py<br/><i>PROFILE_PAGE</i>"]
        S3["extractor + ai_extractor<br/><i>FIELD_VALUE</i>"]
    end

    subgraph SRC_B["🛡️ Task B — Indeed VN"]
        B1["indeed_scraper.py<br/><i>SCRAPE_ATTEMPT</i>"]
        B2["job titles<br/><i>JOB_LISTING</i>"]
    end

    subgraph OUT["💾 File Outputs (current)"]
        O1["result/companies.json<br/><i>COMPANY_RECORD</i>"]
        O2["result/companies.csv"]
        O3["prompts/*.txt<br/><i>AI_PROMPT_LOG</i>"]
        O4["result/indeed_remote_jobs.json<br/><i>INDEED_SCRAPE</i>"]
    end

    S1 --> S2 --> S3 --> O1 & O2 & O3
    B1 --> B2 --> O4

    style SRC_A fill:#DBEAFE,stroke:#2563EB
    style SRC_B fill:#EDE9FE,stroke:#7C3AED
    style OUT fill:#D1FAE5,stroke:#10B981
```

---

## Entity Summary

| Entity | Role | Current file |
|--------|------|--------------|
| `DATA_SOURCE` | Crawl origin (corporate web / Indeed) | implicit in `config.py` |
| `COMPANY_SEED` | Input company list | `src/companies.json` |
| `PROFILE_PAGE` | Discovered & fetched pages | runtime / `取得元ページ` |
| `FIELD_VALUE` | Per-field extraction audit trail | merged into record |
| `COMPANY_RECORD` | Final 4-field company row | `result/companies.json` |
| `AI_PROMPT_LOG` | Generative AI audit trail | `prompts/` |
| `JOB_LISTING` | Indeed job titles (Task B) | `result/indeed_remote_jobs.json` |

---

## Field Dictionary (Task A)

| `field_key` | JP label | EN label | Example |
|-------------|----------|----------|---------|
| `head_office_address` | 本社住所 | Head office address | 東京都港区… |
| `representative_name` | 代表氏名 | Representative name | 代表取締役社長 山田太郎 |
| `capital_stock` | 資本金 | Capital stock | 100億円 |
| `establishment_date` | 設立年月 | Date of establishment | 1911年12月 |

> **Design note:** `FIELD_VALUE` keeps per-page provenance (which URL, which extractor). `COMPANY_RECORD` is the denormalized export — mirrors how SalesNow surfaces a single enriched company profile from multiple web sources.
