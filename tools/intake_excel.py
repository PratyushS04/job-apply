#!/usr/bin/env python3
"""
Job Intake: Excel Parser

Reads an XLSX file and outputs normalized Job objects as JSON.
Expected columns: url, company, comment (all optional except url).

Usage:
    python intake_excel.py <xlsx_file> [--output-dir <jobs_dir>]
    python intake_excel.py --test

Requires: openpyxl (pip install openpyxl)
"""

from __future__ import annotations

import json
import sys
import os
import re
from datetime import datetime, timezone

try:
    from openpyxl import load_workbook
except ImportError:
    print("Error: openpyxl is required. Install with: pip install openpyxl")
    sys.exit(1)


def generate_job_id(jobs_dir: str) -> str:
    """Generate the next sequential job ID based on existing files."""
    existing = []
    if os.path.exists(jobs_dir):
        for f in os.listdir(jobs_dir):
            match = re.match(r"job_(\d+)\.json", f)
            if match:
                existing.append(int(match.group(1)))
    next_num = max(existing, default=0) + 1
    return f"job_{next_num:03d}"


def create_job_object(url: str, company: str = "", comment: str = "",
                      source: str = "excel", job_id: str = "") -> dict:
    """Create a normalized Job object from raw input."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "id": job_id,
        "url": url.strip(),
        "source": source,
        "created_at": now,
        "updated_at": now,

        "company": company.strip() if company else None,
        "title": None,
        "location": None,
        "job_type": None,

        "description": None,

        "requirements": {
            "required_skills": [],
            "preferred_skills": [],
            "experience_years": None,
            "education": None
        },

        "match": {
            "score": None,
            "reasoning": None,
            "relevant_experience": [],
            "relevant_projects": [],
            "skill_gaps": [],
            "status": "NOT_SCORED"
        },

        "resume": {
            "status": "NOT_STARTED",
            "path": None,
            "version": None,
            "review_notes": None
        },

        "application": {
            "status": "NOT_STARTED",
            "questions": [],
            "answers": [],
            "required_fields": {},
            "screenshots": []
        },

        "user_comment": comment.strip() if comment else None,
        "pipeline_status": "NEW",
        "error": None
    }


def parse_excel(filepath: str, jobs_dir: str = "jobs",
                sheet_name: str | None = None) -> list[dict]:
    """Parse an Excel file into a list of Job objects."""
    wb = load_workbook(filepath, read_only=True, data_only=True)

    if sheet_name:
        ws = wb[sheet_name]
    else:
        ws = wb.active

    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        raise ValueError("Excel file is empty")

    # First row is the header
    header = [str(cell).lower().strip() if cell else "" for cell in rows[0]]

    # Find the URL column
    url_idx = None
    for candidate in ["url", "link", "job_url", "job_link", "apply_url"]:
        if candidate in header:
            url_idx = header.index(candidate)
            break

    if url_idx is None:
        raise ValueError(
            f"Excel must have a URL column. Found columns: {header}. "
            f"Expected one of: url, link, job_url, job_link, apply_url"
        )

    # Find optional columns
    company_idx = None
    for candidate in ["company", "company_name", "employer"]:
        if candidate in header:
            company_idx = header.index(candidate)
            break

    comment_idx = None
    for candidate in ["comment", "comments", "description", "notes", "note"]:
        if candidate in header:
            comment_idx = header.index(candidate)
            break

    jobs = []
    for row in rows[1:]:
        # Skip empty rows
        if not row or all(cell is None for cell in row):
            continue

        url = str(row[url_idx]).strip() if url_idx < len(row) and row[url_idx] else ""
        if not url:
            continue

        company = ""
        if company_idx is not None and company_idx < len(row) and row[company_idx]:
            company = str(row[company_idx])

        comment = ""
        if comment_idx is not None and comment_idx < len(row) and row[comment_idx]:
            comment = str(row[comment_idx])

        job_id = generate_job_id(jobs_dir)
        job = create_job_object(
            url=url,
            company=company,
            comment=comment,
            source="excel",
            job_id=job_id
        )

        # Preserve extra columns as metadata
        known_indices = {url_idx, company_idx, comment_idx}
        extra = {}
        for i, cell in enumerate(row):
            if i not in known_indices and i < len(header) and header[i] and cell:
                extra[header[i]] = str(cell)
        if extra:
            job["metadata"] = extra

        jobs.append(job)

        # Write to disk
        os.makedirs(jobs_dir, exist_ok=True)
        with open(os.path.join(jobs_dir, f"{job_id}.json"), "w") as jf:
            json.dump(job, jf, indent=2)

    wb.close()
    return jobs


def run_test():
    """Run a self-test with a temporary Excel file."""
    import tempfile
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.append(["url", "company", "comment"])
    ws.append(["https://example.com/job/1", "Acme Corp", "Great company"])
    ws.append(["https://example.com/job/2", "Beta Inc", None])
    ws.append(["https://example.com/job/3", None, "Remote position"])

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        temp_path = f.name
    wb.save(temp_path)
    wb.close()

    with tempfile.TemporaryDirectory() as temp_dir:
        jobs_dir = os.path.join(temp_dir, "jobs")
        try:
            jobs = parse_excel(temp_path, jobs_dir)
            assert len(jobs) == 3, f"Expected 3 jobs, got {len(jobs)}"
            assert jobs[0]["url"] == "https://example.com/job/1"
            assert jobs[0]["company"] == "Acme Corp"
            assert jobs[0]["user_comment"] == "Great company"
            assert jobs[0]["source"] == "excel"
            assert jobs[1]["company"] == "Beta Inc"
            assert jobs[2]["user_comment"] == "Remote position"

            files = os.listdir(jobs_dir)
            assert len(files) == 3
            print("All Excel intake tests passed!")
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_test()
    elif len(sys.argv) > 1:
        xlsx_path = sys.argv[1]
        output_dir = "jobs"
        if "--output-dir" in sys.argv:
            idx = sys.argv.index("--output-dir")
            output_dir = sys.argv[idx + 1]

        jobs = parse_excel(xlsx_path, output_dir)
        print(f"Imported {len(jobs)} jobs from {xlsx_path}")
        print(json.dumps(jobs, indent=2))
    else:
        print("Usage: python intake_excel.py <xlsx_file> [--output-dir <jobs_dir>]")
        print("       python intake_excel.py --test")
