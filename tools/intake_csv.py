#!/usr/bin/env python3
"""
Job Intake: CSV Parser

Reads a CSV file and outputs normalized Job objects as JSON.
Expected columns: url, company, comment (all optional except url).
Any unrecognized columns are preserved in a "metadata" field.

Usage:
    python intake_csv.py <csv_file> [--output-dir <jobs_dir>]
    python intake_csv.py --test
"""

import csv
import json
import sys
import os
import re
from datetime import datetime, timezone


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
                      source: str = "csv", job_id: str = "") -> dict:
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


def parse_csv(filepath: str, jobs_dir: str = "jobs") -> list[dict]:
    """Parse a CSV file into a list of Job objects."""
    jobs = []

    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        # Normalize column names to lowercase
        if reader.fieldnames is None:
            raise ValueError("CSV file is empty or has no header row")

        fieldnames_lower = {name.lower().strip(): name for name in reader.fieldnames}

        # Find the URL column (try common names)
        url_col = None
        for candidate in ["url", "link", "job_url", "job_link", "apply_url"]:
            if candidate in fieldnames_lower:
                url_col = fieldnames_lower[candidate]
                break

        if url_col is None:
            raise ValueError(
                f"CSV must have a URL column. Found columns: {list(reader.fieldnames)}. "
                f"Expected one of: url, link, job_url, job_link, apply_url"
            )

        # Find optional columns
        company_col = None
        for candidate in ["company", "company_name", "employer"]:
            if candidate in fieldnames_lower:
                company_col = fieldnames_lower[candidate]
                break

        comment_col = None
        for candidate in ["comment", "comments", "description", "notes", "note"]:
            if candidate in fieldnames_lower:
                comment_col = fieldnames_lower[candidate]
                break

        for row in reader:
            url = row.get(url_col, "").strip()
            if not url:
                continue  # Skip rows without URLs

            company = row.get(company_col, "") if company_col else ""
            comment = row.get(comment_col, "") if comment_col else ""

            job_id = generate_job_id(jobs_dir)
            job = create_job_object(
                url=url,
                company=company,
                comment=comment,
                source="csv",
                job_id=job_id
            )

            # Preserve any extra columns as metadata
            known_cols = {url_col, company_col, comment_col}
            extra = {k: v for k, v in row.items()
                     if k not in known_cols and k is not None and v}
            if extra:
                job["metadata"] = extra

            jobs.append(job)

            # Write to disk immediately so generate_job_id sees it
            os.makedirs(jobs_dir, exist_ok=True)
            with open(os.path.join(jobs_dir, f"{job_id}.json"), "w") as jf:
                json.dump(job, jf, indent=2)

    return jobs


def run_test():
    """Run a self-test with a temporary CSV."""
    import tempfile

    test_csv = "url,company,comment\n"
    test_csv += "https://example.com/job/1,Acme Corp,Great company\n"
    test_csv += "https://example.com/job/2,Beta Inc,\n"
    test_csv += "https://example.com/job/3,,Remote position\n"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write(test_csv)
        temp_path = f.name

    with tempfile.TemporaryDirectory() as temp_dir:
        jobs_dir = os.path.join(temp_dir, "jobs")
        try:
            jobs = parse_csv(temp_path, jobs_dir)
            assert len(jobs) == 3, f"Expected 3 jobs, got {len(jobs)}"
            assert jobs[0]["url"] == "https://example.com/job/1"
            assert jobs[0]["company"] == "Acme Corp"
            assert jobs[0]["user_comment"] == "Great company"
            assert jobs[0]["pipeline_status"] == "NEW"
            assert jobs[1]["company"] == "Beta Inc"
            assert jobs[1]["user_comment"] is None
            assert jobs[2]["company"] is None
            assert jobs[2]["user_comment"] == "Remote position"

            # Verify files were written
            files = os.listdir(jobs_dir)
            assert len(files) == 3, f"Expected 3 job files, got {len(files)}"

            print("All CSV intake tests passed!")
        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_test()
    elif len(sys.argv) > 1:
        csv_path = sys.argv[1]
        output_dir = "jobs"
        if "--output-dir" in sys.argv:
            idx = sys.argv.index("--output-dir")
            output_dir = sys.argv[idx + 1]

        jobs = parse_csv(csv_path, output_dir)
        print(f"Imported {len(jobs)} jobs from {csv_path}")
        print(json.dumps(jobs, indent=2))
    else:
        print("Usage: python intake_csv.py <csv_file> [--output-dir <jobs_dir>]")
        print("       python intake_csv.py --test")
