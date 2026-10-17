---
name: application-prep
description: >-
  Prepare a job application by predicting common application questions, drafting
  answers, and assembling all required fields. Use this skill when a job has a
  reviewed resume (status RESUME_REVIEWED) and is ready for application
  preparation, or when the user asks to prepare answers for a specific job
  application. Handles cover letters, screening questions, and form field mapping.
---

# Application Preparation

Prepare everything needed to submit a job application — questions, answers,
cover letter, and required form fields — so the browser automation step can
fill forms without improvisation.

## Inputs

1. **Job Object** — with `description`, `requirements`, and `match` data
2. **Candidate Profile** — all `candidate/` files
3. **Tailored Resume** — from `resumes/<job_id>/`
4. **Match Analysis** — the `match` section with evidence and gaps

## Process

### Step 1: Update Status

Set job `pipeline_status` to `"APP_PREPARING"`.

### Step 2: Predict Application Questions

Based on the job posting and common ATS patterns, predict likely questions:

**Standard Fields** (almost always required):
- Full name, email, phone
- Current location / authorized to work in [country]
- LinkedIn profile URL
- How did you hear about this position?
- Are you willing to relocate?
- Expected salary / salary range
- Available start date
- Do you require visa sponsorship?

**Role-Specific Questions** (derived from job requirements):
- Years of experience with [required_skill]
- Describe your experience with [technology]
- Why are you interested in this role?
- Why [company]?
- Tell us about a challenging project...

### Step 3: Draft Answers

For each predicted question, draft an answer using:

- **Factual answers**: Pull directly from candidate profile (name, email, etc.)
- **Experience answers**: Reference specific entries from `experience.json`
  and `projects.json`, emphasizing relevance to this job
- **Motivation answers**: Combine job description insights with candidate
  preferences to craft genuine, specific responses (avoid generic answers)
- **Skill-specific answers**: Use match evidence to highlight relevant experience

**Answer Guidelines**:
- Be specific and use examples
- Keep answers concise (2-4 sentences for short-answer, 1-2 paragraphs for long)
- Mirror the job posting's language and values
- Never fabricate experience or skills
- For skill gaps, be honest but frame transferable experience positively

### Step 4: Draft Cover Letter (if likely needed)

Generate a cover letter that:
- Opens with the specific role and genuine interest
- Maps 2-3 key job requirements to candidate experience
- Shows knowledge of the company
- Closes with enthusiasm and call to action
- Keeps it under 300 words

Save to `applications/<job_id>/cover_letter.txt`.

### Step 5: Map Required Form Fields

Create a mapping of common form fields to candidate data:

```json
{
  "required_fields": {
    "first_name": "from profile.json",
    "last_name": "from profile.json",
    "email": "from profile.json",
    "phone": "from profile.json",
    "linkedin": "from profile.json",
    "resume_file": "resumes/job_001/resume_v1.tex → compiled PDF",
    "location": "from profile.json",
    "work_authorization": "from preferences or ask user",
    "salary_expectation": "from preferences.json"
  }
}
```

### Step 6: Save Application State

Update the job's `application` section:

```json
"application": {
  "status": "PREPARED",
  "questions": [
    {"question": "Why are you interested in this role?", "type": "long_answer"},
    {"question": "Years of Python experience?", "type": "number"},
    ...
  ],
  "answers": [
    {"question_index": 0, "answer": "...drafted answer..."},
    {"question_index": 1, "answer": "3"},
    ...
  ],
  "required_fields": { ... },
  "cover_letter_path": "applications/job_001/cover_letter.txt",
  "screenshots": []
}
```

Set `pipeline_status` to `"APP_READY"`.

### Step 7: Present for Review

Show the user the prepared application:

```
Application Prepared: job_001 — Senior Software Engineer at Acme Corp

📋 Predicted Questions & Draft Answers:

Q1: Why are you interested in this role?
A1: [draft answer — 2 paragraphs]

Q2: Years of Python experience?
A2: 3

Q3: Do you require visa sponsorship?
A3: [needs user input]

⚠️ Questions needing your input:
- Visa sponsorship status
- Expected salary (preferences show range: ₹X-Y LPA)
- Available start date

Ready to proceed with browser automation?
```

## Important

- Flag any questions that require user input (can't be inferred)
- The user should review and approve all answers before browser automation
- Keep all drafts editable — the user may want to adjust tone or content

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
