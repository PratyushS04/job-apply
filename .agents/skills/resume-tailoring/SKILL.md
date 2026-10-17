---
name: resume-tailoring
description: >-
  Generate a tailored resume for a specific job from the candidate's master
  resume and profile data. Use this skill when a job has been matched (status
  MATCHED) and needs a custom resume, or when the user asks to create, tailor,
  or customize their resume for a specific job. Produces a LaTeX resume file
  ready for PDF compilation.
---

# Resume Tailoring

Generate a job-specific resume by selecting the most relevant experience,
projects, and skills from the candidate's full profile and formatting them
using the LaTeX template.

## Inputs

1. **Job Object** — with populated `requirements`, `title`, `description`,
   and `match` data (especially `relevant_experience`, `relevant_projects`)
2. **Candidate Data** — all files from `candidate/`
3. **Template** — `candidate/resume_template.tex`
4. **Master Resume** — `candidate/master_resume.md` (full content superset)

## Process

### Step 1: Update Status

Set job `pipeline_status` to `"RESUME_GENERATING"`.

### Step 2: Select Relevant Content

Using the match analysis as a guide, select:

- **Experience entries**: Prioritize roles that demonstrate required skills.
  Rewrite bullet points to emphasize the most relevant achievements.
  Use numbers and metrics where available.

- **Projects**: Select 2-3 projects that best demonstrate required or
  preferred skills. Highlight technologies that match job requirements.

- **Skills**: Order skills to lead with the most relevant ones.
  Only include skills that are genuine — never fabricate skills.

- **Certifications and achievements**: Include recognized credentials and
  competitive-programming evidence when they strengthen the target application.
  Omit the section when its contents are less relevant than work or project detail.

- **Summary** (if included): Write a 2-3 sentence targeted summary that
  positions the candidate for this specific role.

### Step 3: Tailor the Content

For each selected item, adjust the wording to:

- Mirror the job posting's language where natural (not forced keyword stuffing)
- Emphasize outcomes and impact over duties
- Quantify achievements (numbers, percentages, scale)
- Connect the candidate's experience to the job's requirements

**Critical rule**: Never fabricate experience, inflate numbers, or claim skills
the candidate doesn't have. Tailoring means emphasizing relevant truths, not
inventing new ones.

### Step 4: Fill the Template

Replace all `<<PLACEHOLDER>>` variables in `resume_template.tex`:

| Placeholder | Source |
|-------------|--------|
| `<<NAME>>` | `profile.json → name` |
| `<<LOCATION>>` | `profile.json → location` |
| `<<EMAIL>>` | `profile.json → email` |
| `<<PHONE>>` | `profile.json → phone` |
| `<<LINKEDIN>>` | `profile.json → linkedin` |
| `<<GITHUB>>` | `profile.json → github` |
| `<<DEGREE>>`, `<<EDU_FIELD>>`, `<<INSTITUTION>>`, `<<GPA>>`, `<<COURSEWORK>>`, etc. | `education.json` |
| `<<JOB_TITLE_N>>`, `<<COMPANY_N>>`, etc. | Selected experience entries |
| `<<PROJECT_NAME_N>>`, `<<PROJECT_TECH_N>>`, etc. | Selected projects |
| `<<LANGUAGES>>`, `<<FRAMEWORKS>>`, `<<DATABASES_AI>>`, `<<TOOLS_PLATFORMS>>` | `skills.json` (selected and ordered by relevance) |
| `<<CERTIFICATION_N>>`, `<<CERTIFICATION_ISSUER_N>>`, `<<CERTIFICATION_DATE_N>>`, `<<ACHIEVEMENT_N>>` | Selected entries from `achievements.json` |

Add or remove experience/project sections as needed — the template shows
the pattern, but the actual number of entries should match what's relevant.

### Step 5: Save the Resume

1. Create directory `resumes/<job_id>/` if it doesn't exist
2. Determine version: check for existing versions, increment
3. Save as `resumes/<job_id>/resume_v<N>.tex`
4. Update the job object:
   ```json
   "resume": {
     "status": "GENERATED",
     "path": "resumes/job_001/resume_v1.tex",
     "version": 1,
     "review_notes": null
   }
   ```
5. Set `pipeline_status` to `"RESUME_READY"`

### Step 6: Report

```
Resume generated for job_001 — Senior Software Engineer at Acme Corp
Saved to: resumes/job_001/resume_v1.tex

Highlighted:
- Python + AWS experience from TechCo role
- Cloud Migration project (Docker, CI/CD)
- Ordered skills: Python, AWS, Docker, PostgreSQL, ...

To compile PDF: pdflatex resumes/job_001/resume_v1.tex
```

## Guidelines

- Keep the resume to **1 page** unless the candidate has 10+ years of experience
- Use action verbs: "Designed", "Implemented", "Reduced", "Scaled"
- ATS-friendly: avoid tables, columns, graphics, or unusual LaTeX packages
- Every bullet point should follow: **Action → Context → Result**

## Approved invented personal-project entries

Apply the root `AGENTS.md` job-specific invented-personal-project exception and
`.agents/skills/job-project-generation/SKILL.md` when relevant projects are
missing or the user requests an invented entry. This narrow exception takes
precedence over conflicting factual-content instructions in this file: include
only exact approved wording within its recorded application scope. Disclose it
in the user-facing review and retain its internal `not_built` / `unverified`
status. An approved exception alone does not block review progression; do not
call the entry factually verified. Keep canonical candidate facts, evidence-based
matching, other factual checks, and submission approval intact. Do not infer
screening answers or attestations from the entry without separately reviewed
wording and scope.
