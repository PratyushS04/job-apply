---
name: resume-review
description: >-
  Critically review a tailored resume against the target job's requirements and
  suggest improvements. Use this skill after a resume has been generated (status
  RESUME_READY) or when the user asks to review, critique, or improve a resume.
  Acts as a "resume critic" that catches issues before submission.
---

# Resume Review

Act as an expert resume reviewer. Critically evaluate a tailored resume against
the target job's requirements and provide actionable feedback.

## Inputs

1. **Tailored Resume** — the `.tex` file from `resumes/<job_id>/`
2. **Job Object** — with requirements and description
3. **Candidate Profile** — to verify accuracy of claims

## Review Criteria

### 1. Relevance Check
- Does the resume lead with the most relevant experience?
- Are the highlighted skills aligned with the job's required skills?
- Are irrelevant experiences de-emphasized or removed?

### 2. Impact Assessment
- Do bullet points show measurable impact (numbers, percentages)?
- Are achievements framed as outcomes, not just responsibilities?
- Is each bullet following Action → Context → Result?

### 3. Keyword Coverage
- Are critical keywords from the job posting naturally incorporated?
- Will this resume pass ATS keyword scanning?
- Missing critical keywords that should be added?

### 4. Accuracy Verification
- Cross-reference all claims against `candidate/` data
- Flag any potential embellishments or inaccuracies
- Verify dates, titles, and company names

### 5. Formatting & Length
- Is it within 1 page (or 2 if 10+ years experience)?
- Is whitespace balanced? Not too cramped or too sparse?
- Does the rendered one-page resume make substantial use of the page, without a
  conspicuously empty lower third? If not, request a revision using relevant,
  supported content and comfortable spacing.
- Consistent formatting (bullet styles, date formats, spacing)?
- LaTeX compiles without errors?
- Are the LinkedIn and GitHub labels clickable, with PDF link targets matching
  the addresses in the candidate profile?

### 6. Common Pitfalls
- Generic phrases ("team player", "hard worker", "detail-oriented")
- Duties instead of achievements ("responsible for" → what did you achieve?)
- Missing quantification ("improved performance" → by how much?)
- Skill listing without context (better to show skills in experience bullets)

## Output Format

```
Resume Review: job_001 — resume_v1.tex

Overall: 7/10

✅ Strengths:
- Strong opening with relevant Python/AWS experience
- Good quantification in TechCo bullet points
- Skills section well-ordered for this role

⚠️ Improvements Needed:
1. [HIGH] Missing "Kubernetes" — add mention in the Cloud Migration project
   context even if experience is limited (e.g., "exposure to K8s orchestration")
2. [MEDIUM] Second experience bullet is too vague — "worked on backend systems"
   → specify what systems and what impact
3. [LOW] Consider adding a 1-line summary targeting this specific role

🔄 Suggested Revisions:
- Line 45: "Developed backend services" →
  "Designed and deployed 3 Python microservices handling 10K+ requests/day"
- Line 52: Add "Docker, Kubernetes" to project technologies
```

## After Review

Update the job object:
```json
"resume": {
  "status": "REVIEWED",
  "review_notes": "7/10 — needs Kubernetes mention, quantify backend bullet"
}
```

If the resume passes review (8+/10), set `pipeline_status` to `"RESUME_REVIEWED"`.
If significant changes are needed, flag for revision and keep status at
`"RESUME_READY"` until the tailoring skill produces a new version.

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
