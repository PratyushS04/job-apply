# Job Application Automation System — Global Rules

## Non-negotiable resume requirements

- Tailor each resume to the actual Job Object description and requirements.
  Select and reorder relevant supported content rather than filling a fixed
  number of experience or project slots.
- Proactively propose relevant personal projects the candidate has not listed.
  Unbuilt invented projects follow the exact-entry approval, scope, internal
  status, and disclosure rules in root `AGENTS.md`; workflow permission alone
  is not approval of a particular entry.
- Preserve `candidate/education.json` exactly during job-specific tailoring.
  Never change college, degree, field, dates, grades, or coursework to match a
  posting. An explicit correction is a separate reviewed profile update.

## Core Principle: Job-Centric Architecture

The **Job Object** (`jobs/<job_id>.json`) is the single source of truth for every job in the pipeline. Every agent, skill, and tool operates on Job Objects — never on raw input formats.

## Rules

### 1. Input Format Independence
- Skills and agents must NEVER assume a specific input format (CSV, Excel, chat).
- All input is normalized into Job Objects by the `job-intake` skill before any processing.
- If you need job data, read it from `jobs/` — not from the original input source.

### 2. Persistent State
- All job state is persisted to `jobs/<job_id>.json` after every mutation.
- Use `tools/job_state.py` for all CRUD operations on jobs.
- Never hold job state only in memory — always write back to disk.

### 3. Candidate Data
- The candidate's profile, experience, skills, and preferences live in `candidate/`.
- Load candidate data from these files — never hardcode personal information.
- The master resume in `candidate/master_resume.md` contains the full superset of all experience.

### 4. Pipeline Status Flow
Jobs progress through these statuses in order:
```
NEW → ANALYZING → ANALYZED → MATCHING → MATCHED → RESUME_GENERATING → RESUME_READY → RESUME_REVIEWED → APP_PREPARING → APP_READY → FILLING → READY_TO_SUBMIT → AWAITING_APPROVAL → SUBMITTED
```
A job can also be set to `SKIPPED` or `ERROR` at any point.

### 5. Skill Independence from MCP
- Skills define **what to do** (behavior), not **how to do it** (tool calls).
- Skills should never reference specific MCP tool names.
- The agent/orchestrator layer maps skill behavior to tool execution.

### 6. Error Handling
- If a job fails at any stage, set `pipeline_status` to `ERROR` and populate the `error` field.
- Never silently skip errors — always record them.
- A failed job should not block other jobs in the pipeline.

### 7. Human Approval
- Before submitting any application, the job must reach `AWAITING_APPROVAL` status.
- The system must present a summary and wait for explicit human confirmation before submitting.
- Never auto-submit without approval (this can be relaxed later via policy).

### 8. File Organization
```
candidate/     — Persistent candidate profile and resume data
jobs/          — One JSON file per job (the Job Object)
resumes/       — Generated tailored resumes, organized by job_id
applications/  — Application artifacts and screenshots, organized by job_id
tools/         — Shared utility scripts (parsers, CRUD)
state/         — Global pipeline state
logs/          — Execution logs
```

### 9. Resume Format
- Resumes are generated as LaTeX (.tex) files.
- The template lives at `candidate/resume_template.tex`.
- Tailored resumes are saved to `resumes/<job_id>/resume_v<N>.tex`.

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
