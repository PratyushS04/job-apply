---
name: candidate-matching
description: >-
  Match a candidate's profile against a job's requirements to produce a
  compatibility score, reasoning, and evidence. Use this skill when a job has
  been analyzed (status ANALYZED) and needs matching against the candidate, or
  when the user asks "am I a good fit?" or "should I apply to this job?" or
  wants to compare themselves against job requirements.
---

# Candidate Matching

Compare a Job object's requirements against the candidate's profile to determine
fit. This is a critical filtering step — it prevents the candidate from wasting
time on poorly-matched jobs and helps prioritize applications.

## Inputs

1. **Job Object** — must have `pipeline_status: "ANALYZED"` with populated
   `requirements`, `title`, `description`
2. **Candidate Profile** — loaded from `candidate/` directory:
   - `profile.json`, `experience.json`, `projects.json`, `skills.json`,
     `education.json`, `achievements.json`
3. **Preferences** — loaded from `candidate/preferences.json`

## Process

### Step 1: Update Status

Set job `pipeline_status` to `"MATCHING"`.

### Step 2: Skills Match

Compare `requirements.required_skills` and `requirements.preferred_skills`
against `candidate/skills.json`:

- **Direct match**: Skill listed in candidate's skills
- **Equivalent match**: Similar technology (e.g., "React" ≈ "React.js")
- **Related match**: Candidate has related skill (e.g., "Vue.js" for "React")
- **Gap**: Skill not found in candidate's profile

### Step 3: Experience Match

Compare `requirements.experience_years` against candidate's work history:

- Calculate total relevant years from `experience.json`
- Check if candidate has experience in the right domain/role
- Identify the most relevant positions and projects

### Step 4: Education Match

Compare `requirements.education` against `candidate/education.json`:

- Exact degree match
- Equivalent or higher degree
- Field of study alignment

### Step 5: Preference Check

Check against `candidate/preferences.json`:

- Location match (or remote compatibility)
- Role type match
- Industry alignment
- Deal-breaker check — if any deal-breaker matches, flag it prominently

### Step 6: Generate Match Score

Produce a score from 0–100 based on:

| Factor | Weight | Description |
|--------|--------|-------------|
| Required skills | 35% | % of required skills matched |
| Experience level | 25% | Years + relevance of experience |
| Preferred skills | 15% | % of preferred skills matched |
| Education | 10% | Degree and field match |
| Preferences fit | 15% | Location, role type, deal-breakers |

### Step 7: Compile Evidence

For each area, list specific evidence from the candidate's profile:

```json
{
  "score": 78,
  "reasoning": "Strong technical match with 3/4 required skills...",
  "relevant_experience": [
    "2 years at Acme Corp as Backend Developer using Python and AWS"
  ],
  "relevant_projects": [
    "Cloud Migration Tool — demonstrates Docker and Terraform experience"
  ],
  "skill_gaps": [
    "Kubernetes — not in candidate's skills, but has Docker experience"
  ],
  "status": "SCORED"
}
```

### Step 8: Update and Decide

Update the job's `match` field and set `pipeline_status` to `"MATCHED"`.

If the score is below `preferences.min_match_score`:
- Set `pipeline_status` to `"SKIPPED"`
- Report: "Job skipped — match score (45) below threshold (50)"

If any deal-breakers triggered:
- Flag prominently but don't auto-skip (let the user decide)

## Output Format

Present the match result clearly:

```
Match Result: job_001 — Senior Software Engineer at Acme Corp
Score: 78/100

✅ Strengths:
- Python (required) — 3 years of professional experience
- AWS (required) — used in 2 projects
- Docker (required) — daily use at current role

⚠️ Gaps:
- Kubernetes (required) — no direct experience, but Docker knowledge transfers
- GraphQL (preferred) — not in skill set

📋 Relevant Experience:
- Backend Developer at TechCo (2 years) — Python, AWS, PostgreSQL
- Cloud Migration project — Docker, CI/CD pipelines

Recommendation: APPLY — strong overall match despite Kubernetes gap
```

## Batch Matching

When matching multiple jobs, sort the results by score (highest first) and
present a summary table before detailed breakdowns.
