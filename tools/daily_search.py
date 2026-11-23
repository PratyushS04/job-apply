#!/usr/bin/env python3
"""
Daily job search: run by the 2am schedule (see tools/schedule/).

Searches the job boards with the candidate's job_search.json (same filters as
tools/discover_jobs.py search), ranks the new postings best first, and writes
a numbered digest to state/daily_jobs/<date>.md (and latest.md). It imports
nothing and runs no agent, so it needs no sign-in and costs nothing.

In the morning, read the digest and tell the agent which numbers to apply to,
e.g. "apply to 1, 3, 4, 5, 9 and 10 from today's jobs". The agent imports them
(tools/discover_jobs.py import ...) and runs the application pipeline, stopping
for your approval before anything is submitted.

Usage:
    .venv/bin/python tools/daily_search.py --candidate candidates/animesh_murai
    .venv/bin/python tools/daily_search.py --test
Options: --config PATH, --jobs-dir DIR, --state-dir DIR, --no-notify
"""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import discover_jobs  # noqa: E402

DIGEST_DIR = "daily_jobs"
DEFAULT_DIGEST_SIZE = 15


def _salary_text(row: dict) -> str | None:
    low, high = row.get("min_amount"), row.get("max_amount")
    if low is None and high is None:
        return None
    amounts = " - ".join(f"{int(v):,}" for v in (low, high) if v is not None)
    return f"{row.get('currency') or ''} {amounts} {row.get('interval') or ''}".strip()


def render_digest(shortlist: list[dict], stats: dict, errors: list[dict],
                  candidate: str, size: int, when: datetime) -> str:
    top = shortlist[:size]
    lines = [
        f"# Jobs for {when:%A %d %B %Y}",
        "",
        f"Candidate: `{candidate}` · searched {when:%H:%M} · "
        f"{stats['found']} postings found, {stats['shortlisted']} new after filters"
        + (f", showing the best {len(top)}" if len(shortlist) > len(top) else "") + ".",
        "",
    ]
    if not top:
        lines += ["No new jobs passed the filters today.", ""]
    for row in top:
        years = row.get("required_experience_years")
        skills = row.get("matching_skills") or []
        details = [
            row.get("location") or "location not given",
            f"{years}+ yrs experience" if years is not None else "experience not stated",
            f"posted {row.get('date_posted') or '?'}",
            f"via {row.get('site')}",
        ]
        salary = _salary_text(row)
        if salary:
            details.append(salary)
        lines.append(f"**{row['number']}. {row.get('title')}** at {row.get('company')}  ")
        lines.append(" · ".join(details) + "  ")
        lines.append(f"Your skills mentioned: {', '.join(skills) if skills else 'none found'}  ")
        lines.append(f"<{row.get('job_url')}>")
        lines.append("")
    if errors:
        lines.append(f"_{len(errors)} searches failed: "
                     + "; ".join(e["search"] for e in errors) + "._")
        lines.append("")
    lines += [
        "---",
        "To apply, tell the agent the numbers, e.g. "
        "\"apply to 1, 3, 4 from today's jobs\". It prepares each application and "
        "asks you before submitting. Numbers refer to this list until the next search runs.",
        "",
    ]
    return "\n".join(lines)


def notify(title: str, message: str) -> None:
    """macOS banner; silently does nothing elsewhere or if it fails."""
    if sys.platform != "darwin":
        return
    script = f'display notification "{message}" with title "{title}"'
    try:
        subprocess.run(["osascript", "-e", script], check=False, timeout=10,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError):
        pass


def run(candidate: str, config_path: str, jobs_dir: str, state_dir: str,
        send_notification: bool = True, scraper=None, now: datetime | None = None) -> str:
    now = now or datetime.now()
    print(f"=== Daily job search {now:%Y-%m-%d %H:%M} ===", flush=True)
    result = discover_jobs.cmd_search(candidate, config_path, jobs_dir, state_dir,
                                      scraper=scraper, quiet_hint=True)
    size = int(result["config"].get("digest_size") or DEFAULT_DIGEST_SIZE)
    digest = render_digest(result["shortlist"], result["stats"], result["errors"],
                           candidate, size, now)
    out_dir = os.path.join(state_dir, DIGEST_DIR)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{now:%Y-%m-%d}.md")
    for target in (path, os.path.join(out_dir, "latest.md")):
        with open(target, "w") as f:
            f.write(digest)
    count = min(len(result["shortlist"]), size)
    print(f"Digest written to {path}", flush=True)
    if send_notification:
        notify("Job search", f"{count} new jobs ready to review" if count else "No new jobs today")
    return path


def run_test():
    import json
    import tempfile

    class FakeFrame:
        def __init__(self, records):
            self.records = records

        def to_dict(self, orient):
            return self.records

    def fake_scraper(**kwargs):
        return FakeFrame([
            {"site": "indeed", "job_url": "https://in.indeed.com/viewjob?jk=1", "title": "Software Engineer",
             "company": "Acme", "location": "Hyderabad", "date_posted": "2026-11-22",
             "description": "Python and SQL, 1+ years of experience", "min_amount": 900000.0,
             "max_amount": 1400000.0, "currency": "INR", "interval": "yearly"},
            {"site": "linkedin", "job_url": "https://www.linkedin.com/jobs/view/2", "title": "SDE",
             "company": "Beta", "location": "Pune", "date_posted": "2026-11-23", "description": "Java"},
            {"site": "linkedin", "job_url": "https://www.linkedin.com/jobs/view/3", "title": "Engineer",
             "company": "Gamma", "location": "Pune", "date_posted": "2026-11-23", "description": "Go"},
        ])

    with tempfile.TemporaryDirectory() as tmp:
        cand = os.path.join(tmp, "cand")
        os.makedirs(cand)
        json.dump({"languages": ["Python", "SQL", "Java"]}, open(os.path.join(cand, "skills.json"), "w"))
        config = os.path.join(cand, "job_search.json")
        json.dump({"search_terms": ["x"], "locations": ["y"], "digest_size": 2}, open(config, "w"))
        jobs_dir, state_dir = os.path.join(tmp, "jobs"), os.path.join(tmp, "state")
        path = run(cand, config, jobs_dir, state_dir, send_notification=False,
                   scraper=fake_scraper, now=datetime(2026, 11, 24, 2, 0))
        text = open(path).read()
        assert path.endswith("2026-11-24.md")
        assert open(os.path.join(state_dir, DIGEST_DIR, "latest.md")).read() == text
        assert "**1. Software Engineer** at Acme" in text  # 2 skills ranks first
        assert "**2. SDE** at Beta" in text
        assert "Gamma" not in text  # beyond digest_size
        assert "INR 900,000 - 1,400,000 yearly" in text and "1+ yrs experience" in text
        assert "showing the best 2" in text
        # The digest numbers are the shortlist numbers used by import.
        created = discover_jobs.cmd_import("1st and 2nd", jobs_dir, state_dir)
        assert [j["company"] for j in created] == ["Acme", "Beta"]
    print("\nAll daily search tests passed!")


def main(argv: list[str]) -> int:
    if argv and argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv and argv[0] == "--test":
        run_test()
        return 0
    opt = discover_jobs._option
    candidate = opt(argv, "--candidate")
    if not candidate:
        print("Needs --candidate, e.g. --candidate candidates/animesh_murai")
        return 2
    candidate = candidate.rstrip("/")
    try:
        run(candidate,
            opt(argv, "--config", os.path.join(candidate, "job_search.json")),
            opt(argv, "--jobs-dir", "jobs"),
            opt(argv, "--state-dir", "state"),
            send_notification="--no-notify" not in argv)
    except Exception as exc:  # scheduled run: always leave a readable error in the log
        print(f"Daily search failed: {type(exc).__name__}: {exc}", flush=True)
        if "--no-notify" not in argv:
            notify("Job search", "Daily search failed; see logs/discovery/daily_search.log")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
