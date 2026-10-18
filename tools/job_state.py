#!/usr/bin/env python3
"""
Job State Manager

CRUD operations for Job objects stored as JSON files in the jobs/ directory.

Usage:
    python job_state.py list [--status <STATUS>] [--jobs-dir <dir>]
    python job_state.py get <job_id> [--jobs-dir <dir>]
    python job_state.py update <job_id> <field> <value> [--jobs-dir <dir>]
    python job_state.py set-status <job_id> <status> [--jobs-dir <dir>]
    python job_state.py summary [--jobs-dir <dir>]
    python job_state.py --test
"""

from __future__ import annotations

import json
import sys
import os
import re
from datetime import datetime, timezone


VALID_STATUSES = [
    "NEW", "ANALYZING", "ANALYZED", "MATCHING", "MATCHED",
    "RESUME_GENERATING", "RESUME_READY", "RESUME_REVIEWED",
    "APP_PREPARING", "APP_READY", "FILLING",
    "READY_TO_SUBMIT", "AWAITING_APPROVAL", "SUBMITTED",
    "SKIPPED", "ERROR"
]


def get_jobs_dir(args: list[str]) -> str:
    """Extract --jobs-dir from args, default to 'jobs'."""
    if "--jobs-dir" in args:
        idx = args.index("--jobs-dir")
        return args[idx + 1]
    return "jobs"


def load_job(job_id: str, jobs_dir: str = "jobs") -> dict | None:
    """Load a single job by ID."""
    filepath = os.path.join(jobs_dir, f"{job_id}.json")
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r") as f:
        return json.load(f)


def save_job(job: dict, jobs_dir: str = "jobs") -> None:
    """Save a job back to disk."""
    job["updated_at"] = datetime.now(timezone.utc).isoformat()
    os.makedirs(jobs_dir, exist_ok=True)
    filepath = os.path.join(jobs_dir, f"{job['id']}.json")
    with open(filepath, "w") as f:
        json.dump(job, f, indent=2)


def list_jobs(jobs_dir: str = "jobs", status_filter: str | None = None) -> list[dict]:
    """List all jobs, optionally filtered by status."""
    if not os.path.exists(jobs_dir):
        return []

    jobs = []
    for filename in sorted(os.listdir(jobs_dir)):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(jobs_dir, filename)
        with open(filepath, "r") as f:
            job = json.load(f)
        if status_filter is None or job.get("pipeline_status") == status_filter:
            jobs.append(job)

    return jobs


def get_summary(jobs_dir: str = "jobs") -> dict:
    """Get a summary of all jobs grouped by status."""
    jobs = list_jobs(jobs_dir)
    summary = {
        "total": len(jobs),
        "by_status": {},
        "jobs": []
    }

    for status in VALID_STATUSES:
        count = sum(1 for j in jobs if j.get("pipeline_status") == status)
        if count > 0:
            summary["by_status"][status] = count

    for job in jobs:
        summary["jobs"].append({
            "id": job["id"],
            "url": job["url"],
            "company": job.get("company"),
            "title": job.get("title"),
            "status": job.get("pipeline_status"),
            "match_score": job.get("match", {}).get("score")
        })

    return summary


def update_job_field(job_id: str, field_path: str, value: str,
                     jobs_dir: str = "jobs") -> dict | None:
    """Update a specific field in a job. Supports dot notation (e.g., 'match.score')."""
    job = load_job(job_id, jobs_dir)
    if job is None:
        return None

    # Parse the value
    parsed_value = value
    try:
        parsed_value = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        pass

    # Navigate dot-separated path
    parts = field_path.split(".")
    obj = job
    for part in parts[:-1]:
        if part not in obj:
            obj[part] = {}
        obj = obj[part]

    obj[parts[-1]] = parsed_value
    save_job(job, jobs_dir)
    return job


def set_status(job_id: str, status: str, jobs_dir: str = "jobs") -> dict | None:
    """Set a job's pipeline status."""
    if status not in VALID_STATUSES:
        print(f"Error: Invalid status '{status}'. Valid: {VALID_STATUSES}")
        return None

    job = load_job(job_id, jobs_dir)
    if job is None:
        print(f"Error: Job '{job_id}' not found")
        return None

    job["pipeline_status"] = status
    if status == "ERROR":
        pass  # error field should be set separately
    save_job(job, jobs_dir)
    return job


def update_pipeline_state(jobs_dir: str = "jobs",
                          state_dir: str = "state") -> None:
    """Update the global pipeline.json with current counts."""
    summary = get_summary(jobs_dir)

    pipeline = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "total_jobs": summary["total"],
        "status_counts": {},
        "active_jobs": [],
        "recent_errors": []
    }

    for status in VALID_STATUSES:
        pipeline["status_counts"][status] = summary["by_status"].get(status, 0)

    # Active = not in terminal states
    terminal = {"SUBMITTED", "SKIPPED", "ERROR"}
    for job_info in summary["jobs"]:
        if job_info["status"] not in terminal:
            pipeline["active_jobs"].append(job_info["id"])
        elif job_info["status"] == "ERROR":
            pipeline["recent_errors"].append(job_info["id"])

    os.makedirs(state_dir, exist_ok=True)
    with open(os.path.join(state_dir, "pipeline.json"), "w") as f:
        json.dump(pipeline, f, indent=2)


def run_test():
    """Run self-tests."""
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        jobs_dir = os.path.join(temp_dir, "jobs")
        state_dir = os.path.join(temp_dir, "state")
        os.makedirs(jobs_dir)

        # Create test jobs
        for i in range(3):
            job = {
                "id": f"job_{i+1:03d}",
                "url": f"https://example.com/job/{i+1}",
                "source": "test",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "company": f"Company {i+1}",
                "title": None,
                "pipeline_status": "NEW",
                "match": {"score": None, "status": "NOT_SCORED"},
                "error": None
            }
            save_job(job, jobs_dir)

        # Test list
        jobs = list_jobs(jobs_dir)
        assert len(jobs) == 3, f"Expected 3 jobs, got {len(jobs)}"

        # Test filter
        jobs = list_jobs(jobs_dir, "NEW")
        assert len(jobs) == 3

        jobs = list_jobs(jobs_dir, "SUBMITTED")
        assert len(jobs) == 0

        # Test get
        job = load_job("job_001", jobs_dir)
        assert job is not None
        assert job["company"] == "Company 1"

        # Test update field
        updated = update_job_field("job_001", "title", "Software Engineer", jobs_dir)
        assert updated["title"] == "Software Engineer"

        # Test dot notation update
        updated = update_job_field("job_001", "match.score", "85", jobs_dir)
        assert updated["match"]["score"] == 85

        # Test set status
        updated = set_status("job_001", "ANALYZING", jobs_dir)
        assert updated["pipeline_status"] == "ANALYZING"

        # Test invalid status
        result = set_status("job_001", "INVALID", jobs_dir)
        assert result is None

        # Test summary
        summary = get_summary(jobs_dir)
        assert summary["total"] == 3
        assert summary["by_status"].get("ANALYZING") == 1
        assert summary["by_status"].get("NEW") == 2

        # Test pipeline state update
        update_pipeline_state(jobs_dir, state_dir)
        with open(os.path.join(state_dir, "pipeline.json")) as f:
            pipeline = json.load(f)
        assert pipeline["total_jobs"] == 3
        assert len(pipeline["active_jobs"]) == 3

        print("All job state tests passed!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python job_state.py list [--status STATUS] [--jobs-dir DIR]")
        print("  python job_state.py get <job_id> [--jobs-dir DIR]")
        print("  python job_state.py update <job_id> <field> <value> [--jobs-dir DIR]")
        print("  python job_state.py set-status <job_id> <status> [--jobs-dir DIR]")
        print("  python job_state.py summary [--jobs-dir DIR]")
        print("  python job_state.py --test")
        sys.exit(1)

    cmd = sys.argv[1]
    jobs_dir = get_jobs_dir(sys.argv)

    if cmd == "--test":
        run_test()
    elif cmd == "list":
        status = None
        if "--status" in sys.argv:
            idx = sys.argv.index("--status")
            status = sys.argv[idx + 1]
        jobs = list_jobs(jobs_dir, status)
        print(json.dumps(jobs, indent=2))
    elif cmd == "get":
        job = load_job(sys.argv[2], jobs_dir)
        if job:
            print(json.dumps(job, indent=2))
        else:
            print(f"Job {sys.argv[2]} not found")
    elif cmd == "update":
        result = update_job_field(sys.argv[2], sys.argv[3], sys.argv[4], jobs_dir)
        if result:
            print(f"Updated {sys.argv[2]}.{sys.argv[3]}")
        else:
            print(f"Job {sys.argv[2]} not found")
    elif cmd == "set-status":
        result = set_status(sys.argv[2], sys.argv[3], jobs_dir)
        if result:
            print(f"Job {sys.argv[2]} → {sys.argv[3]}")
    elif cmd == "summary":
        summary = get_summary(jobs_dir)
        print(json.dumps(summary, indent=2))
    else:
        print(f"Unknown command: {cmd}")
