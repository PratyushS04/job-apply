---
name: job-intake
description: >-
  Normalize any job input source into standardized Job objects. Use this skill
  whenever the user provides job URLs (in chat, as a list, pasted text), uploads
  a CSV file, uploads an Excel/XLSX file, or mentions jobs they want to apply to.
  This skill handles all input formats and converts them into the unified Job
  object stored in the jobs/ directory.
---

# Job Intake

Convert any input source into normalized Job objects. The intake layer is the
single entry point for all jobs — no downstream skill ever reads raw input.

## Supported Input Sources

### 1. Chat / Plain Text URLs

When the user pastes URLs directly in chat or provides a text file:

1. Run `tools/intake_urls.py` with the text content
2. The script extracts all URLs, deduplicates, and attempts company name extraction
3. Each URL becomes a Job object with `source: "chat"`

**Example user input:**
```
Apply to these jobs:
https://careers.google.com/jobs/12345
https://www.amazon.jobs/en/jobs/67890
```

### 2. CSV Files

When the user provides a `.csv` file:

1. Run `tools/intake_csv.py <filepath> --output-dir jobs`
2. Expected columns: `url` (required), `company` (optional), `comment` (optional)
3. The parser is flexible with column naming — it recognizes variants like
   `link`, `job_url`, `company_name`, `notes`, `description`, etc.
4. Extra columns are preserved in a `metadata` field

### 3. Excel Files

When the user provides a `.xlsx` file:

1. Run `tools/intake_excel.py <filepath> --output-dir jobs`
2. Same column expectations as CSV
3. Requires `openpyxl` — if not installed, run `pip install openpyxl` first

### 4. Job Discovery (job boards via JobSpy)

When the user asks to find new jobs rather than supplying them:

1. Run `.venv/bin/python tools/discover_jobs.py search --candidate candidates/<name>`.
   It reads `candidates/<name>/job_search.json` (search terms, locations,
   boards, recency, title/company filters), searches LinkedIn, Indeed, Naukri
   and Glassdoor, removes cross-board duplicates and jobs already in `jobs/`,
   and saves a numbered shortlist to `state/discovered_jobs.json`. It creates
   no Job Objects.
2. Show the shortlist to the user and let them choose. Do not import the whole
   list on your own initiative.
3. Run `.venv/bin/python tools/discover_jobs.py import <numbers>` (e.g. `1,4,7`,
   `2-6` or `all`) with the user's picks. Each becomes a `NEW` Job Object with
   `source: "jobspy"`, the board's title/company/location/description, and
   board details in `posting_metadata` (including `candidate_profile`).
4. The description is the board's copy. Job analysis still opens the posting,
   confirms it is live, and fills in requirements.

Setup (Python 3.10+): `uv venv --python 3.12 .venv && uv pip install --python
.venv/bin/python -r requirements.txt`. Some searches failing (LinkedIn
rate-limits heavily) does not stop the others; failures are listed in the
shortlist file.

## Output

Every intake operation produces:

1. **Job JSON files** in `jobs/` — one file per job (e.g., `jobs/job_001.json`)
2. **Console output** — summary of how many jobs were imported
3. **Pipeline state update** — run `tools/job_state.py summary` to see current state

## Job Object Created

Each job starts with this structure:

```json
{
  "id": "job_001",
  "url": "https://...",
  "source": "csv|excel|chat",
  "company": "extracted or null",
  "user_comment": "user's note or null",
  "pipeline_status": "NEW",
  ...all other fields null/empty...
}
```

## Duplicate Detection

Before creating a new job, check if a job with the same URL already exists in
`jobs/`. If it does:
- Skip the duplicate
- Report it to the user: "Skipped duplicate: <url> (already exists as <job_id>)"

To check for duplicates, scan existing job files for matching URLs.

## After Intake

Once jobs are imported, inform the user:

```
Imported N jobs:
- job_001: https://... (Company Name)
- job_002: https://... (Unknown)
- job_003: https://... (Company Name)

Next: Run job analysis to extract job descriptions and requirements.
```

The orchestrator will then advance these jobs through the pipeline.

## Error Handling

- If a CSV/Excel file has no URL column, report the error with the columns found
- If a row has no URL, skip it silently
- If the file can't be read, report the error and don't create partial jobs
- Always report the count of successful imports vs. skipped rows
