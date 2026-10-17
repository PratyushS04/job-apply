---
name: job-analysis
description: >-
  Analyze a job posting by visiting its URL, extracting the job description,
  and structuring it into the Job object's fields (title, company, location,
  requirements, skills). Use this skill whenever a job has status NEW or
  ANALYZING and needs its description extracted and parsed. Also use when the
  user asks to analyze, examine, or understand a specific job posting.
---

# Job Analysis

Given a Job object with a URL, fetch the job posting page, extract all relevant
information, and populate the structured fields in the Job object.

## When to Use

- Job has `pipeline_status: "NEW"` and needs analysis
- User asks "analyze this job" or "what does this job require?"
- User wants to understand a job's requirements before applying

## Process

### Step 1: Update Status

Set the job's `pipeline_status` to `"ANALYZING"`.

### Step 2: Fetch the Job Page

Navigate to the job URL and extract the full page content. The job page may be:
- A direct job posting (company career page)
- A job board listing (LinkedIn, Indeed, Glassdoor, Naukri, etc.)
- An ATS page (Lever, Greenhouse, Workday, etc.)

Read the page content. If the page requires JavaScript rendering, use browser
navigation to load the full content.

### Step 3: Extract Structured Data

From the job posting, extract:

| Field | Description |
|-------|-------------|
| `title` | Job title (e.g., "Senior Software Engineer") |
| `company` | Company name (if not already set) |
| `location` | Location(s), including remote status |
| `job_type` | "full-time", "part-time", "contract", "internship" |
| `description` | Full job description text (cleaned of HTML) |
| `requirements.required_skills` | Must-have technical skills |
| `requirements.preferred_skills` | Nice-to-have skills |
| `requirements.experience_years` | Required years of experience (number or null) |
| `requirements.education` | Required education level |

### Step 4: Structure the Requirements

Parse the job description into structured requirements. Look for:

- **Required skills**: "must have", "required", "minimum qualifications"
- **Preferred skills**: "nice to have", "preferred", "bonus", "plus"
- **Experience**: "X+ years", "X-Y years of experience"
- **Education**: "Bachelor's", "Master's", "PhD", degree requirements

### Step 5: Update the Job Object

Write all extracted data back to the job's JSON file in `jobs/`.
Set `pipeline_status` to `"ANALYZED"`.

### Step 6: Report

Provide a concise summary:

```
Job Analyzed: job_001
Title: Senior Software Engineer
Company: Acme Corp
Location: Bangalore, India (Hybrid)
Experience: 3-5 years
Required Skills: Python, AWS, Docker, PostgreSQL
Preferred Skills: Kubernetes, Terraform
Education: Bachelor's in CS or equivalent
```

## Error Handling

- If the URL is unreachable, set status to `ERROR` with the error message
- If the page has no job content (404, login wall), report it and set `ERROR`
- If some fields can't be extracted, fill what's available and note gaps

## Important Notes

- Do NOT modify the `match`, `resume`, or `application` sections — those are
  handled by their respective skills
- Preserve the `user_comment` field — it contains the user's original note
- If the company was already set during intake, only overwrite if the extracted
  value is more accurate (e.g., full name vs. domain guess)
