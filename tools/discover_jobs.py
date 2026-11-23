#!/usr/bin/env python3
"""
Job Discovery: find new postings on job boards with JobSpy.

Two steps, so a person reviews what was found before anything enters the
pipeline:

1. Search: runs every search term x location from the candidate's
   job_search.json across the configured boards (LinkedIn, Indeed, Naukri,
   Glassdoor, ...), drops duplicates and jobs already in jobs/, applies the
   title/company filters, and saves a numbered shortlist to
   state/discovered_jobs.json. No Job Objects are created.

2. Import: turns the picked shortlist entries into NEW Job Objects in jobs/,
   in the same format as the other intake tools (source "jobspy").

Requires Python 3.10+ and python-jobspy (see requirements.txt). The other
tools still run on the system Python.

Usage:
    .venv/bin/python tools/discover_jobs.py search --candidate candidates/animesh_murai
    .venv/bin/python tools/discover_jobs.py import 1,4,7
    .venv/bin/python tools/discover_jobs.py import all
    .venv/bin/python tools/discover_jobs.py --test

Options:
    --config PATH      search config (default: <candidate>/job_search.json)
    --jobs-dir DIR     default: jobs
    --state-dir DIR    default: state
"""

from __future__ import annotations

import json
import math
import os
import re
import sys
import unicodedata
from datetime import date, datetime, timezone
from urllib.parse import urlsplit, urlunsplit

# Reuse the shared Job Object shape and ID scheme from URL intake.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from intake_urls import create_job_object, generate_job_id  # noqa: E402

SHORTLIST_FILE = "discovered_jobs.json"

DEFAULT_CONFIG = {
    "search_terms": [],
    "locations": [],
    "sites": ["indeed", "linkedin", "naukri", "glassdoor"],
    "country_indeed": "India",
    "results_per_search": 20,
    "hours_old": 72,
    "is_remote": False,
    "job_type": None,
    "fetch_description": True,
    "require_title_keywords": [],
    "exclude_title_keywords": [],
    "exclude_companies": [],
    "max_experience_years": None,
    "min_skill_hits": 0,
    "auto_import_limit": 10,
    "min_match_score": 50,
    "proxies": [],
}

# skills.json keys that are not skills to look for in a posting.
SKILL_KEYS_IGNORED = {"soft", "unconfirmed_not_used"}
# Skill names that are also everyday words and would match almost any posting.
SKILL_STOPWORDS = {"room", "combine", "problem solving", "decision making"}
MAX_PLAUSIBLE_YEARS = 25  # "27 years" in a description is usually a lost dash ("2-7")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean(value):
    """Turn pandas/numpy values into plain JSON-safe Python values."""
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    try:
        if value != value:  # NaN / pandas NaT
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if hasattr(value, "item") and not isinstance(value, (str, bytes)):
        try:
            return _clean(value.item())
        except (ValueError, AttributeError):
            pass
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def normalize_url(url: str | None) -> str | None:
    """Comparable form of a URL: lowercase host, no query/fragment/trailing slash.

    Job boards put the job ID in the path (LinkedIn /jobs/view/<id>, Naukri
    slug-<id>), except Indeed, whose ID lives in the ``jk`` query parameter.
    """
    if not url:
        return None
    parts = urlsplit(url.strip())
    query = ""
    if "indeed." in parts.netloc:
        match = re.search(r"(?:^|&)jk=([^&]+)", parts.query)
        if match:
            query = f"jk={match.group(1)}"
    path = parts.path.rstrip("/")
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, query, ""))


def _norm_text(text: str | None) -> str:
    # "Hyderābād" -> "hyderabad" before dropping punctuation.
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


_COMPANY_NOISE = {"private", "pvt", "ltd", "limited", "inc", "llc", "llp", "corp",
                  "corporation", "co", "india", "the", "plc", "gmbh"}
_CITY_NOISE = {"division", "district", "urban", "rural", "metropolitan", "region"}
_CITY_ALIASES = {"bangalore": "bengaluru", "gurgaon": "gurugram", "bombay": "mumbai",
                 "new delhi": "delhi", "secunderabad": "hyderabad"}


def _norm_company(company: str | None) -> str:
    return " ".join(w for w in _norm_text(company).split() if w not in _COMPANY_NOISE)


def _norm_city(location: str | None) -> str:
    """First part of a location, cleaned. "" when unknown or only a state code."""
    first = (location or "").split(",")[0]
    city = " ".join(w for w in _norm_text(first).split() if w not in _CITY_NOISE)
    city = _CITY_ALIASES.get(city, city)
    if len(city) <= 2:  # Indeed India gives state codes: "TS, India", "MH, India"
        return ""
    return city


def job_key(company: str | None, title: str | None, location: str | None) -> str:
    """Same job posted on several boards usually shares company+title+city."""
    return f"{_norm_company(company)}|{_norm_text(title)}|{_norm_city(location)}"


class SeenJobs:
    """Finds a posting already seen, by URL or by company+title+city.

    A location that is unknown or only a state code matches any city for the
    same company and title, since boards disagree on how they write it.
    """

    def __init__(self):
        self.urls: dict[str, str] = {}
        self.places: dict[str, dict[str, str]] = {}

    @staticmethod
    def _urls(*urls: str | None) -> set[str]:
        return {normalize_url(u) for u in urls} - {None}

    def add(self, ident: str, urls: set[str], company, title, location) -> None:
        for url in urls:
            self.urls[url] = ident
        if company and title:
            company_title = f"{_norm_company(company)}|{_norm_text(title)}"
            self.places.setdefault(company_title, {}).setdefault(_norm_city(location), ident)

    def find(self, urls: set[str], company, title, location) -> str | None:
        for url in urls:
            if url in self.urls:
                return self.urls[url]
        if not (company and title):
            return None
        cities = self.places.get(f"{_norm_company(company)}|{_norm_text(title)}")
        if not cities:
            return None
        city = _norm_city(location)
        if not city:
            return next(iter(cities.values()))
        return cities.get(city) or cities.get("")


def _contains_keyword(text: str, keyword: str) -> bool:
    """Whole-word, case-insensitive match ("sr" must not match "src")."""
    pattern = r"(?<![a-z0-9])" + re.escape(keyword.lower()) + r"(?![a-z0-9])"
    return re.search(pattern, text.lower()) is not None


_RANGE_RE = re.compile(r"(\d{1,2})\s*\+?\s*(?:-|–|—|to)\s*(\d{1,2})|(\d{1,2})\s*\+?", re.I)
_DESC_YEARS_RE = re.compile(
    r"(?:minimum|min\.?|at\s+least)?\s*(\d{1,2})\s*\+?\s*(?:(?:-|–|—|to)\s*\d{1,2}\s*\+?\s*)?"
    r"(?:years?|yrs?)\b(?:'s)?(?=[^.\n]{0,60}experience)",
    re.I,
)
_DESC_EXPERIENCE_LABEL_RE = re.compile(
    r"experience(?:\s+required)?\s*\**\s*[:\-]\s*\**\s*(\d{1,2})\s*\+?\s*(?:(?:-|–|—|to)\s*\d{1,2}\s*)?(?:years?|yrs?)",
    re.I,
)


def required_experience_years(row: dict) -> int | None:
    """Minimum years of experience a posting asks for, or None if not stated.

    Uses the board's structured range when it has one (Naukri: "3-8 Yrs"),
    then the experience range in a Naukri URL, then the first
    "N years ... experience" / "Experience: N years" statement in the description.
    """
    exp_range = row.get("experience_range")
    if exp_range:
        match = _RANGE_RE.search(str(exp_range))
        if match:
            return int(match.group(1) or match.group(3))
    url_match = re.search(r"-(\d{1,2})-to-\d{1,2}-years", row.get("job_url") or "")
    if url_match:
        return int(url_match.group(1))
    description = row.get("description") or ""
    found: list[tuple[int, int]] = []
    for regex in (_DESC_YEARS_RE, _DESC_EXPERIENCE_LABEL_RE):
        for match in regex.finditer(description):
            years = int(match.group(1))
            if years <= MAX_PLAUSIBLE_YEARS:
                found.append((match.start(), years))
    if found:
        return min(found)[1]  # first statement in the posting, usually the basic requirement
    return None


def load_skill_terms(candidate_dir: str) -> list[str]:
    """Skill names from <candidate>/skills.json, without notes in parentheses."""
    path = os.path.join(candidate_dir, "skills.json")
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        data = json.load(f)

    def walk(value, key=""):
        if key in SKILL_KEYS_IGNORED:
            return
        if isinstance(value, dict):
            for k, v in value.items():
                yield from walk(v, k)
        elif isinstance(value, list):
            for item in value:
                yield from walk(item, key)
        elif isinstance(value, str) and key and not key.endswith("_note"):
            yield value

    terms: list[str] = []
    for raw in walk(data):
        term = raw.split("(")[0].strip()
        if term and term.lower() not in SKILL_STOPWORDS and term.lower() not in {t.lower() for t in terms}:
            terms.append(term)
    return terms


def matching_skills(row: dict, skill_terms: list[str]) -> list[str]:
    text = f"{row.get('title') or ''}\n{row.get('description') or ''}"
    return [term for term in skill_terms if _contains_keyword(text, term)]


def load_config(path: str) -> dict:
    with open(path, "r") as f:
        user_config = json.load(f)
    config = dict(DEFAULT_CONFIG)
    config.update({k: v for k, v in user_config.items() if not k.startswith("_")})
    if not config["search_terms"]:
        raise ValueError(f"{path}: 'search_terms' is empty")
    if not config["locations"]:
        raise ValueError(f"{path}: 'locations' is empty")
    return config


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def run_searches(config: dict, scraper=None) -> tuple[list[dict], list[dict]]:
    """Run every search term x location. Returns (raw rows, errors).

    ``scraper`` defaults to jobspy.scrape_jobs; tests pass a fake.
    """
    if scraper is None:
        from jobspy import scrape_jobs as scraper

    rows: list[dict] = []
    errors: list[dict] = []
    for term in config["search_terms"]:
        for location in config["locations"]:
            label = f"'{term}' in {location}"
            print(f"Searching {label} on {', '.join(config['sites'])}...", flush=True)
            try:
                df = scraper(
                    site_name=config["sites"],
                    search_term=term,
                    google_search_term=f"{term} jobs near {location}",
                    location=location,
                    results_wanted=config["results_per_search"],
                    hours_old=config["hours_old"],
                    is_remote=config["is_remote"],
                    job_type=config["job_type"],
                    country_indeed=config["country_indeed"],
                    fetch_description=config["fetch_description"],
                    proxies=config["proxies"] or None,
                    verbose=0,
                )
            except Exception as exc:  # one failed search must not stop the rest
                errors.append({"search": label, "error": f"{type(exc).__name__}: {exc}"})
                print(f"  failed: {exc}", flush=True)
                continue
            records = df.to_dict(orient="records") if df is not None else []
            print(f"  {len(records)} results", flush=True)
            for record in records:
                record = {k: _clean(v) for k, v in record.items()}
                record["_search_term"] = term
                record["_search_location"] = location
                rows.append(record)
    return rows, errors


def existing_job_index(jobs_dir: str) -> SeenJobs:
    """Index of the Job Objects already in jobs_dir."""
    index = SeenJobs()
    if not os.path.isdir(jobs_dir):
        return index
    for filename in sorted(os.listdir(jobs_dir)):
        if not filename.endswith(".json"):
            continue
        with open(os.path.join(jobs_dir, filename), "r") as f:
            job = json.load(f)
        meta = job.get("posting_metadata") or {}
        urls = SeenJobs._urls(job.get("url"), meta.get("job_url_direct"), meta.get("board_url"))
        index.add(job["id"], urls, job.get("company"), job.get("title"), job.get("location"))
    return index


def build_shortlist(rows: list[dict], config: dict, jobs_dir: str,
                    skill_terms: list[str] | None = None) -> tuple[list[dict], dict]:
    """Dedupe, drop already-tracked jobs, apply filters, sort newest first."""
    tracked = existing_job_index(jobs_dir)
    seen = SeenJobs()
    stats = {"found": len(rows), "duplicate": 0, "already_tracked": 0, "filtered": 0,
             "too_much_experience": 0}
    max_years = config["max_experience_years"]
    require = config["require_title_keywords"]
    exclude = config["exclude_title_keywords"]
    excluded_companies = {_norm_text(c) for c in config["exclude_companies"]}
    shortlist: list[dict] = []

    for row in rows:
        url = row.get("job_url")
        if not url:
            continue
        title = row.get("title") or ""
        company = row.get("company") or ""
        location = row.get("location")
        urls = SeenJobs._urls(url, row.get("job_url_direct"))

        if tracked.find(urls, company, title, location):
            stats["already_tracked"] += 1
            continue
        if seen.find(urls, company, title, location):
            stats["duplicate"] += 1
            continue
        seen.add(url, urls, company, title, location)

        if require and not any(_contains_keyword(title, k) for k in require):
            stats["filtered"] += 1
            continue
        if any(_contains_keyword(title, k) for k in exclude):
            stats["filtered"] += 1
            continue
        if _norm_text(company) in excluded_companies:
            stats["filtered"] += 1
            continue

        row["required_experience_years"] = required_experience_years(row)
        if max_years is not None and row["required_experience_years"] is not None \
                and row["required_experience_years"] > max_years:
            stats["too_much_experience"] += 1
            continue
        row["matching_skills"] = matching_skills(row, skill_terms or [])

        shortlist.append(row)

    # Best first: most of the candidate's skills mentioned, then newest.
    shortlist.sort(key=lambda r: (len(r.get("matching_skills") or []), r.get("date_posted") or ""),
                   reverse=True)
    for number, row in enumerate(shortlist, start=1):
        row["number"] = number
    stats["shortlisted"] = len(shortlist)
    return shortlist, stats


def save_shortlist(shortlist: list[dict], stats: dict, errors: list[dict],
                   candidate: str, config_path: str, state_dir: str) -> str:
    os.makedirs(state_dir, exist_ok=True)
    path = os.path.join(state_dir, SHORTLIST_FILE)
    payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "candidate_profile": candidate,
        "config": config_path,
        "stats": stats,
        "errors": errors,
        "jobs": shortlist,
    }
    with open(path, "w") as f:
        json.dump(payload, f, indent=2, default=str)
    return path


def print_shortlist(shortlist: list[dict]) -> None:
    for row in shortlist:
        posted = row.get("date_posted") or "?"
        years = row.get("required_experience_years")
        years_text = f"{years}+ yrs" if years is not None else "yrs not stated"
        skills = row.get("matching_skills") or []
        print(f"{row['number']:>3}. {row.get('title')} | {row.get('company')} | "
              f"{row.get('location')} | {row.get('site')} | posted {posted}")
        print(f"     {years_text} | {len(skills)} of your skills"
              f"{': ' + ', '.join(skills[:6]) if skills else ''}")
        print(f"     {row.get('job_url')}")


def cmd_search(candidate: str, config_path: str, jobs_dir: str, state_dir: str,
               scraper=None, quiet_hint: bool = False) -> dict:
    config = load_config(config_path)
    rows, errors = run_searches(config, scraper)
    shortlist, stats = build_shortlist(rows, config, jobs_dir, load_skill_terms(candidate))
    path = save_shortlist(shortlist, stats, errors, candidate, config_path, state_dir)
    print()
    print_shortlist(shortlist)
    print()
    print(f"Found {stats['found']} postings: {stats['shortlisted']} new, "
          f"{stats['duplicate']} cross-board duplicates, "
          f"{stats['already_tracked']} already in jobs/, {stats['filtered']} filtered by title/company, "
          f"{stats['too_much_experience']} asking for more than "
          f"{config['max_experience_years']} years.")
    if errors:
        print(f"{len(errors)} searches failed (details in {path}).")
    print(f"Shortlist saved to {path}.")
    if shortlist and not quiet_hint:
        print("Import the ones you want:  .venv/bin/python tools/discover_jobs.py import 1,3,5   (or 'all')")
    return {"shortlist": shortlist, "stats": stats, "errors": errors, "path": path,
            "config": config}


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------

def parse_picks(spec: str, available: list[int]) -> list[int]:
    """Accepts "1,3,5", "2-6", "all", and natural forms like "1st, 3rd and #9"."""
    if spec.strip().lower() == "all":
        return list(available)
    text = re.sub(r"(\d+)\s*(?:st|nd|rd|th)\b", r"\1", spec.lower())
    text = re.sub(r"\band\b|#", ",", text)
    text = re.sub(r"\s*(?:-|–|to)\s*", "-", text)
    picks: list[int] = []
    for part in re.split(r"[,\s]+", text):
        if not part:
            continue
        try:
            if "-" in part:
                start, end = (int(x) for x in part.split("-", 1))
                picks.extend(range(start, end + 1))
            else:
                picks.append(int(part))
        except ValueError:
            raise ValueError(f"Can't read '{part}' as a shortlist number.") from None
    missing = [p for p in picks if p not in available]
    if missing:
        raise ValueError(f"Not in the shortlist: {missing}. Shortlist has 1-{max(available, default=0)}.")
    return list(dict.fromkeys(picks))


def row_to_job(row: dict, job_id: str, candidate: str) -> dict:
    job = create_job_object(
        url=row["job_url"],
        company=row.get("company") or "",
        source="jobspy",
        job_id=job_id,
    )
    job["title"] = row.get("title")
    job["location"] = row.get("location")
    job["job_type"] = row.get("job_type")
    # Board text only; job-analysis still reads the posting and fills requirements.
    job["description"] = row.get("description")
    salary = None
    if row.get("min_amount") is not None or row.get("max_amount") is not None:
        salary = {
            "min": row.get("min_amount"),
            "max": row.get("max_amount"),
            "currency": row.get("currency"),
            "interval": row.get("interval"),
        }
    job["posting_metadata"] = {
        "candidate_profile": candidate,
        "discovered_via": "jobspy",
        "board": row.get("site"),
        "board_url": row.get("job_url"),
        "job_url_direct": row.get("job_url_direct"),
        "date_posted": row.get("date_posted"),
        "is_remote": row.get("is_remote"),
        "salary": salary,
        "job_level": row.get("job_level"),
        "experience_range": row.get("experience_range"),
        "required_experience_years_estimate": row.get("required_experience_years"),
        "candidate_skills_mentioned": row.get("matching_skills"),
        "company_url": row.get("company_url"),
        "search_term": row.get("_search_term"),
        "search_location": row.get("_search_location"),
        "description_source": "job board listing via JobSpy; verify against the live posting",
    }
    return job


def cmd_import(spec: str, jobs_dir: str, state_dir: str) -> list[dict]:
    path = os.path.join(state_dir, SHORTLIST_FILE)
    if not os.path.exists(path):
        raise FileNotFoundError(f"No shortlist at {path}. Run the 'search' command first.")
    with open(path, "r") as f:
        payload = json.load(f)
    rows = {row["number"]: row for row in payload["jobs"]}
    picks = parse_picks(spec, sorted(rows))
    candidate = payload.get("candidate_profile")
    created_at = payload.get("created_at")
    print(f"Using the shortlist from {created_at} ({len(rows)} jobs).")
    try:
        age_hours = (datetime.now(timezone.utc) - datetime.fromisoformat(created_at)).total_seconds() / 3600
        if age_hours > 36:
            print(f"Warning: this shortlist is {age_hours / 24:.1f} days old; numbers refer to that list.")
    except (TypeError, ValueError):
        pass

    created: list[dict] = []
    for number in picks:
        row = rows[number]
        # Re-check: jobs may have been added since the search ran.
        existing = existing_job_index(jobs_dir).find(
            SeenJobs._urls(row["job_url"], row.get("job_url_direct")),
            row.get("company"), row.get("title"), row.get("location"))
        if existing:
            print(f"Skipped duplicate: #{number} {row['job_url']} (already exists as {existing})")
            continue
        job_id = generate_job_id(jobs_dir)
        job = row_to_job(row, job_id, candidate)
        os.makedirs(jobs_dir, exist_ok=True)
        with open(os.path.join(jobs_dir, f"{job_id}.json"), "w") as f:
            json.dump(job, f, indent=2)
        created.append(job)

    print(f"Imported {len(created)} job(s):")
    for job in created:
        print(f"- {job['id']}: {job['title']} | {job['company']} | {job['url']}")
    if created:
        print("\nNext: run job analysis on these NEW jobs.")
    return created


# ---------------------------------------------------------------------------
# Self-test (no network)
# ---------------------------------------------------------------------------

def run_test():
    import tempfile

    assert normalize_url("https://in.indeed.com/viewjob?jk=abc123&from=serp") == \
        "https://in.indeed.com/viewjob?jk=abc123"
    assert normalize_url("https://www.linkedin.com/jobs/view/42/?trk=x") == \
        "https://www.linkedin.com/jobs/view/42"
    assert _contains_keyword("Senior Software Engineer", "senior")
    assert not _contains_keyword("Software Engineer, src team", "sr")
    assert job_key("Cisco", "Software Engineer", "Hyderabad, Telangana, India") == \
        job_key("CISCO", "Software  Engineer", "Hyderabad")
    assert job_key("Benovymed Healthcare Private Ltd", "CTO", "Pune") == \
        job_key("Benovymed Healthcare Private Limited", "CTO", "Pune, India")
    assert _norm_city("Hyderābād, India") == "hyderabad"
    assert _norm_city("Pune Division, Maharashtra, India") == "pune"
    assert _norm_city("Bangalore") == "bengaluru"
    assert _norm_city("MH, India") == ""
    seen_test = SeenJobs()
    seen_test.add("a", set(), "Rockwell Automation", "Software Engineer", "Pune Division, Maharashtra")
    assert seen_test.find(set(), "Rockwell Automation", "Software Engineer", "MH, India") == "a"
    assert seen_test.find(set(), "Rockwell Automation", "Software Engineer", "Pune") == "a"
    assert seen_test.find(set(), "Rockwell Automation", "Software Engineer", "Bengaluru") is None
    seen_test.add("b", set(), "Oracle", "Engineer", "TS, India")
    assert seen_test.find(set(), "Oracle", "Engineer", "Hyderabad") == "b"

    def fake_scraper(**kwargs):
        class FakeFrame:
            def __init__(self, records):
                self.records = records

            def to_dict(self, orient):
                return self.records

        if kwargs["location"] == "Pune":
            raise RuntimeError("blocked")
        base = [
            {"site": "linkedin", "job_url": "https://www.linkedin.com/jobs/view/1",
             "job_url_direct": "https://careers.acme.com/1", "title": "Software Engineer",
             "company": "Acme", "location": "Hyderabad, India", "date_posted": date(2026, 11, 20),
             "description": "Build things", "min_amount": float("nan"), "max_amount": float("nan")},
            {"site": "indeed", "job_url": "https://in.indeed.com/viewjob?jk=9&from=x",
             "job_url_direct": None, "title": "Software Engineer", "company": "ACME",
             "location": "Hyderabad", "date_posted": date(2026, 11, 21), "description": None,
             "min_amount": 1200000.0, "max_amount": 1800000.0, "currency": "INR", "interval": "yearly"},
            {"site": "naukri", "job_url": "https://www.naukri.com/job-listings-sde-2",
             "title": "Senior Software Engineer", "company": "Beta", "location": "Hyderabad",
             "date_posted": date(2026, 11, 22)},
            {"site": "naukri", "job_url": "https://www.naukri.com/job-listings-sde-3",
             "title": "Software Development Engineer", "company": "Cisco", "location": "Hyderabad",
             "date_posted": date(2026, 11, 22)},
            {"site": "naukri", "job_url": "https://www.naukri.com/job-listings-sde-4",
             "title": "SDE I", "company": "Gamma", "location": "Hyderabad",
             "date_posted": date(2026, 11, 23)},
        ]
        return FakeFrame(base)

    with tempfile.TemporaryDirectory() as tmp:
        jobs_dir = os.path.join(tmp, "jobs")
        state_dir = os.path.join(tmp, "state")
        os.makedirs(jobs_dir)
        # An existing tracked job that should be recognized.
        existing = create_job_object("https://www.naukri.com/job-listings-sde-3/", "Cisco",
                                     source="chat", job_id="job_001")
        existing["title"] = "Software Development Engineer"
        with open(os.path.join(jobs_dir, "job_001.json"), "w") as f:
            json.dump(existing, f)

        config_path = os.path.join(tmp, "job_search.json")
        with open(config_path, "w") as f:
            json.dump({"search_terms": ["software engineer"], "locations": ["Hyderabad", "Pune"],
                       "exclude_title_keywords": ["senior"]}, f)

        result = cmd_search("candidates/test", config_path, jobs_dir, state_dir, fake_scraper)
        stats = result["stats"]
        assert stats["found"] == 5, stats
        assert stats["already_tracked"] == 1, stats  # Cisco
        assert stats["duplicate"] == 1, stats        # Acme on Indeed duplicates LinkedIn
        assert stats["filtered"] == 1, stats         # Senior
        assert stats["shortlisted"] == 2, stats
        assert len(result["errors"]) == 1            # Pune search failed, others continued
        titles = [r["title"] for r in result["shortlist"]]
        assert titles == ["SDE I", "Software Engineer"], titles  # newest first
        assert os.listdir(jobs_dir) == ["job_001.json"]  # search creates no Job Objects

        created = cmd_import("2", jobs_dir, state_dir)
        assert len(created) == 1
        job = json.load(open(os.path.join(jobs_dir, "job_002.json")))
        assert job["source"] == "jobspy" and job["pipeline_status"] == "NEW"
        assert job["company"] == "Acme" and job["title"] == "Software Engineer"
        assert job["posting_metadata"]["candidate_profile"] == "candidates/test"
        assert job["posting_metadata"]["job_url_direct"] == "https://careers.acme.com/1"
        assert job["posting_metadata"]["salary"] is None

        again = cmd_import("all", jobs_dir, state_dir)
        assert [j["title"] for j in again] == ["SDE I"]  # #2 now a duplicate, skipped
        try:
            cmd_import("9", jobs_dir, state_dir)
            raise AssertionError("expected ValueError")
        except ValueError:
            pass

    print("\nAll job discovery tests passed!")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _option(args: list[str], name: str, default: str | None = None) -> str | None:
    if name in args:
        return args[args.index(name) + 1]
    return default


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "--test":
        run_test()
        return 0

    jobs_dir = _option(argv, "--jobs-dir", "jobs")
    state_dir = _option(argv, "--state-dir", "state")
    try:
        if argv[0] == "search":
            candidate = _option(argv, "--candidate")
            if not candidate:
                print("search needs --candidate, e.g. --candidate candidates/animesh_murai")
                return 2
            candidate = candidate.rstrip("/")
            config_path = _option(argv, "--config", os.path.join(candidate, "job_search.json"))
            cmd_search(candidate, config_path, jobs_dir, state_dir)
        elif argv[0] == "import":
            if len(argv) < 2 or argv[1].startswith("--"):
                print("import needs shortlist numbers, e.g. 'import 1,3,5', 'import 2-6' or 'import all'")
                return 2
            cmd_import(argv[1], jobs_dir, state_dir)
        else:
            print(f"Unknown command: {argv[0]}\n")
            print(__doc__)
            return 2
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
