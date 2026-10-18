#!/usr/bin/env python3
"""
Job Intake: URL Extractor

Extracts job URLs from plain text (chat messages, pasted lists, etc.)
and creates normalized Job objects.

Usage:
    python intake_urls.py <text_file> [--output-dir <jobs_dir>]
    python intake_urls.py --text "url1 url2 ..." [--output-dir <jobs_dir>]
    python intake_urls.py --test
"""

from __future__ import annotations

import json
import sys
import os
import re
from datetime import datetime, timezone


URL_PATTERN = re.compile(
    r'https?://[^\s<>"\'`\]\)]+',
    re.IGNORECASE
)


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
                      source: str = "chat", job_id: str = "") -> dict:
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


def extract_urls_from_text(text: str) -> list[str]:
    """Extract all URLs from a text blob. Deduplicates while preserving order."""
    urls = URL_PATTERN.findall(text)

    # Clean trailing punctuation that might have been captured
    cleaned = []
    for url in urls:
        url = url.rstrip(".,;:!?)>")
        if url not in cleaned:
            cleaned.append(url)

    return cleaned


def try_extract_company_from_url(url: str) -> str | None:
    """Attempt to extract company name from URL domain."""
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).hostname or ""
        # Remove common prefixes/suffixes
        domain = domain.replace("www.", "")
        parts = domain.split(".")
        if len(parts) >= 2:
            # e.g., "careers.google.com" → "google"
            # e.g., "jobs.lever.co" → try the path instead
            company = parts[-2] if parts[-2] not in (
                "lever", "greenhouse", "workday", "icims", "taleo",
                "smartrecruiters", "ashbyhq", "bamboohr", "jazz",
                "applytojob", "myworkdayjobs", "careers"
            ) else None
            if company:
                return company.capitalize()
    except Exception:
        pass
    return None


def parse_text(text: str, jobs_dir: str = "jobs") -> list[dict]:
    """Parse a text blob, extract URLs, create Job objects."""
    urls = extract_urls_from_text(text)
    jobs = []

    for url in urls:
        job_id = generate_job_id(jobs_dir)
        company = try_extract_company_from_url(url)
        job = create_job_object(
            url=url,
            company=company or "",
            source="chat",
            job_id=job_id
        )
        jobs.append(job)

        # Write to disk
        os.makedirs(jobs_dir, exist_ok=True)
        with open(os.path.join(jobs_dir, f"{job_id}.json"), "w") as jf:
            json.dump(job, jf, indent=2)

    return jobs


def run_test():
    """Run a self-test."""
    import tempfile

    # Test URL extraction
    text = """
    Apply to these jobs:
    1. https://careers.google.com/jobs/12345
    2. https://www.amazon.jobs/en/jobs/67890
    3. https://boards.greenhouse.io/stripe/jobs/111
    4. Also check out https://lever.co/company/jobs/222

    Don't apply to these yet:
    - https://example.com/job/333
    """

    urls = extract_urls_from_text(text)
    assert len(urls) == 5, f"Expected 5 URLs, got {len(urls)}: {urls}"
    assert urls[0] == "https://careers.google.com/jobs/12345"
    assert urls[4] == "https://example.com/job/333"

    # Test company extraction
    assert try_extract_company_from_url("https://careers.google.com/jobs/1") == "Google"
    assert try_extract_company_from_url("https://www.amazon.jobs/en/1") == "Amazon"

    # Test full parse
    with tempfile.TemporaryDirectory() as temp_dir:
        jobs_dir = os.path.join(temp_dir, "jobs")
        jobs = parse_text(text, jobs_dir)
        assert len(jobs) == 5
        assert jobs[0]["source"] == "chat"
        assert jobs[0]["pipeline_status"] == "NEW"
        assert all(j["url"].startswith("http") for j in jobs)

        files = os.listdir(jobs_dir)
        assert len(files) == 5

    # Test deduplication
    dup_text = "https://example.com/job/1 and again https://example.com/job/1"
    urls = extract_urls_from_text(dup_text)
    assert len(urls) == 1

    print("All URL intake tests passed!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_test()
    elif "--text" in sys.argv:
        idx = sys.argv.index("--text")
        text = sys.argv[idx + 1]
        output_dir = "jobs"
        if "--output-dir" in sys.argv:
            oidx = sys.argv.index("--output-dir")
            output_dir = sys.argv[oidx + 1]
        jobs = parse_text(text, output_dir)
        print(f"Extracted {len(jobs)} jobs")
        print(json.dumps(jobs, indent=2))
    elif len(sys.argv) > 1:
        filepath = sys.argv[1]
        with open(filepath, "r") as f:
            text = f.read()
        output_dir = "jobs"
        if "--output-dir" in sys.argv:
            idx = sys.argv.index("--output-dir")
            output_dir = sys.argv[idx + 1]
        jobs = parse_text(text, output_dir)
        print(f"Extracted {len(jobs)} jobs from {filepath}")
        print(json.dumps(jobs, indent=2))
    else:
        print("Usage: python intake_urls.py <text_file> [--output-dir <jobs_dir>]")
        print("       python intake_urls.py --text \"url1 url2\" [--output-dir <jobs_dir>]")
        print("       python intake_urls.py --test")
