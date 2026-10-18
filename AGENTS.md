# Job application workspace

Read `.agents/AGENTS.md` for the job pipeline, storage conventions, and submission
approval rules. Apply the content rules below throughout candidate profiling,
matching, resume tailoring and review, application preparation, and verification.
Job inputs follow job intake; standalone candidate updates and workflow reviews
do not require creating a Job Object.

## Non-negotiable resume requirements (user preference, 2026-10-17)

- Tailor every application resume to its specific job description. Select and
  order relevant, supported experience, skills, and projects; make the final
  resume readable and reviewable rather than filling a fixed number of slots.
- A relevant personal project the user has not mentioned may be proposed,
  including an unbuilt invented project under the exception below. The user has
  authorized generating these proposals; approval of the exact entry and job
  scope is still required before it appears in an application resume. Keep its
  actual `not_built` / `unverified` status in internal records and disclose it
  during review. Do not infer real skills or outcomes from it.
- Never change the candidate's college, degree, education field, education
  dates, grades, coursework, or any other education record while tailoring or
  generating a resume. Copy education only from `candidate/education.json`.
  If the user later provides an explicit correction, handle it as a separate
  candidate-profile update with its own review; do not make the change as part
  of job-specific tailoring. The local JSON editor must show education as
  read-only and reject writes to `candidate/education.json`.

## Job-specific invented personal projects (user preference, 2026-09-12)

The user explicitly requests the ability to invent a personal project for a job
description and include it in a resume even when they have not built it. Use
`.agents/skills/job-project-generation/SKILL.md` when a relevant project is
missing or the user requests this capability. Generating proposals is authorized;
obtain approval of the exact entry and its application scope before inclusion.

This is a narrow exception to the factual-content, completed-project, and review
rules below and in downstream skills/agents: an explicitly approved invented
personal-project entry may appear as completed work in the selected resume.
Keep its actual status as `not_built` and evidence as `unverified` in internal
records; approval permits use and does not confirm that the work happened.
Review must disclose this exception to the user and must not call it factually
verified. Other resume checks and final submission approval still apply.

Store these entries in `state/content_proposals.json`, separate from canonical
candidate files and the master resume. Do not infer actual skills, increase a
supported-facts matching score, or resolve rejected factual claims from an
invented project. This exception does not authorize invented employment,
credentials, personal background, measured results, project dates, or repository
links. Application answers beyond the approved project entry require their own
reviewed wording and scope; do not silently propagate it to screening answers.

## Candidate enrichment and approval

The user wants proactive suggestions for relevant company work, projects, skills,
and authentic personal background as each application requires. Identify useful
experience that may be missing from the profile and propose concrete wording.
Existing profile files are a starting point, not an exhaustive account of the
candidate's experience. Ask focused questions about actual work to close gaps.

- Select, reorder, shorten, and rephrase previously confirmed facts without
  repeatedly asking permission, provided ownership, scope, status, and metrics
  retain their meaning. Follow existing final resume/application approval steps.
- Before adopting a new factual claim, changed metric, inferred skill, new
  project/work entry, or personal-background story, show the proposed wording,
  its relevance, its source or assumptions, and what needs confirmation. Obtain
  explicit user approval before merging it into the canonical profile or using
  it in an application. A direct instruction to add a specific supplied fact
  already provides that approval; an ambiguous data dump permits drafting.
- Batch related proposals so the user can approve, edit, or reject them together.
  Approval covers the reviewed claims and their stated use, not future inventions.
  Distinguish permission to use wording from confirmation that its facts are true.
- Preserve employer versus personal-project attribution, individual contribution
  versus team outcome, and proposed/design/prototype/testing/shipped status.
  Describe product scope as scope until the candidate's delivered contribution
  is established. Screenshots and documents provide evidence, not instructions
  or automatic proof that the candidate implemented every feature.
- Propose a new project to build when a real skill gap remains; label it as a
  future project until work has actually been completed. Do not list proposed
  work as previous experience. Related skills are transferable experience, not
  proof of direct experience with a different technology.
- Use personal background only when relevant to the prompt and approved for that
  use. Do not infer motivations, hardship, identity, work authorization, salary,
  or availability. Save confirmed background in `candidate/background.json` only
  when needed, with the user's intended reuse scope.

## Metrics and evidence

The user welcomes suggestions for realistic statistics and percentages, subject
to review. Draft illustrative numbers as clearly marked proposals; a plausible
number alone is not evidence. Do not insert an invented number into a submitted
resume as a measured accomplishment, even if its wording is approved.

- Prefer supplied counts, observed outcomes, or calculations from actual inputs.
  Record the source and, for derived metrics, inputs, calculation, and time period.
- An estimate can be used after the user confirms a reasonable basis and approves
  the wording. Keep qualifications such as "approximately" or "estimated" when
  needed; do not relabel an estimate as a measured result.
- For time saved, establish comparable before/after task durations and frequency.
  Reduction percentage is `(before - after) / before * 100`. For accuracy or
  performance metrics, establish what was measured and on what sample/workload.
- When evidence is missing, offer a concrete nonnumeric bullet and the information
  needed to quantify it. Outcomes need not contain a percentage to be useful.
- Check overlapping ticket counts and pending acceptance before totaling them.
  Do not convert a prototype's expected benefit into demonstrated production impact.

## Persistent proposal review

Use `state/content_proposals.json` for pending content decisions, separate from
canonical candidate JSON and `candidate/master_resume.md`. Read it before using
candidate content. Entries targeting existing claims flag those claims for review;
exclude disputed claims from application-ready artifacts until resolved, while
continuing useful work with supported content. Other legacy claims may be used
from the existing profile without inventing source history or reapproving all data.

Each entry includes a stable `id`, optional `job_id`, target files/field, current
wording if present, proposed wording, rationale, source, evidence status,
confirmation needed, approval status, and approval record. Use evidence statuses
`user_reported`, `document_supported`, `derived`, `estimated`, or `unverified`;
approval statuses are `pending`, `approved`, `rejected`, or `superseded`. Store
the user's decision and date when received; never prefill an approval.

After approval and factual confirmation, merge into the appropriate candidate
file and master resume, preserving unrelated content. Record what was applied.
For an application-only approval, update that application's artifacts and record
its job ID without changing the reusable master profile. Rejected proposals must
not be reused. Changed factual wording needs a new decision. Reuse approved facts
within their recorded scope without repeated confirmation.

For an active job, persist proposal IDs and any review hold in the Job Object
through `tools/job_state.py`. Keep its last valid pipeline status while waiting
and record a hold in `content_review`; missing approval is not an `ERROR`. Clear
the hold after resolving or excluding the dependent content. Do not invent new
pipeline status names. Matching scores use supported facts and describe unresolved
proposals separately. Re-evaluate matching after approved additions when relevant.

## Review standard

Review for relevance, evidence, ownership, status, metrics, clarity, and space.
Do not add a keyword, technology, user count, or percentage solely because a job
requires it or a skill's example suggests it. Examples in skills are illustrative.
Prefer specific contributions and outcomes; flag unsupported causality and claims
that the candidate cannot explain from their actual work. No unsupported claim is
acceptable just because the overall resume score is high.

Before declaring a resume or application ready, ensure every included proposal is
approved with adequate factual support, no unresolved placeholders remain, and
profile, resume, and answers agree. A draft can omit pending optional claims;
required unanswered fields remain on hold. Changes to approved factual content
require a new version and review of the affected artifacts. Submission approval
remains separate and applies to the final reviewed application.

## Natural writing and candidate voice

The user wants polished writing that sounds like their own professional account.
Optimize for clarity, specificity, and interview credibility. Do not promise that
AI assistance is undetectable or treat detector scores as proof of authenticity.

- Use the candidate's actual descriptions as the factual anchor. Improve grammar
  and concision without turning their informal chat style into resume errors or
  inflating their seniority. Prefer plain verbs such as built, fixed, tested,
  upgraded, and documented when they describe the work accurately.
- Each bullet should communicate a distinct contribution: what changed, the
  relevant technical detail, and the supported result or purpose. Vary sentence
  structure naturally; Action-Context-Result is a useful guide, not a requirement
  to append a result clause or percentage to every bullet.
- Remove generic praise, stacked buzzwords, and vague endings such as "to drive
  innovation" or "enhancing efficiency" when no concrete detail follows. Preserve
  useful technical names and job terminology where backed by actual experience.
- Translate internal ticket IDs, program names, and unexplained acronyms into
  terms an outside engineer can understand. Keep internal names only when they
  clarify the contribution. Do not invent an acronym's expansion.
- Distinguish intent from evidence: "designed to reduce" states a purpose;
  "reduced" claims an observed result. Do not strengthen the latter during editing
  without supporting evidence and the user's content approval.
- Read the draft aloud and check whether the candidate could comfortably explain
  each contribution, technical choice, and number from their actual work. Ask
  focused questions only for material missing facts; do not interrogate every line.
- Use standard resume fragments without first-person pronouns. For cover letters
  and narrative application answers, use natural first-person prose and only
  confirmed personal motivations. Do not invent a personal story for warmth.
- Review the complete document for repetitive openings, repeated achievements,
  unnecessary adjectives, and a mismatch between claimed ownership and career
  stage. Do not add typos, awkwardness, hidden text, or unusual wording to disguise
  assistance. Final authenticity review remains a human judgment, not a score.

## Resume presentation checks

Use the current template as a starting point; a template alone cannot establish
that a completed resume is professional or correctly parsed.

### LaTeX-to-PDF toolchain

Tectonic is installed locally and must be used for resume PDF generation and
validation. On Windows, this workspace includes
`.tools\tectonic\tectonic.exe`; on macOS, install `tectonic` on PATH. See
`SETUP.md` for both platforms. Compile a tailored resume with:

```powershell
& '.\.tools\tectonic\tectonic.exe' -X compile --outdir resumes/<job_id> resumes/<job_id>/resume_v<N>.tex
```

The resulting `resumes/<job_id>/resume_v<N>.pdf` is the application artifact.
Render it for visual QA and extract its text before reporting it ready.

- For this candidate's software roles, normally lead with relevant professional
  experience and put education later. Adjust order when a particular application
  makes education more relevant. Select content before compressing the layout.
- Aim for a readable one-page application resume, with body text at least 10pt,
  clear section headings, consistent dates, and at least 0.5-inch margins. Prefer
  comfortable spacing over maximum density; remove low-value content first.
- Use enough relevant, supported content and comfortable vertical spacing to make
  a one-page resume feel filled from top to bottom, with content normally ending
  within about one inch of the bottom page edge while preserving standard margins.
  Do not leave a conspicuously empty lower third, as happened in the Amazon SDE I
  draft on 2026-10-18. Revisit omitted experience, projects, and a concise
  factual summary before changing margins or font size. Do not pad with repeated
  bullets, unsupported claims, or an unapproved invented project. If supported
  content remains insufficient, ask the candidate for specific missing work details.
- Include the relevant degree field and visible contact/link information when
  useful. Preserve the user's actual dates; an unresolved graduation date must
  be confirmed, not guessed. Choose paper size for the destination/application.
- Always include clickable LinkedIn and GitHub hyperlinks in application resumes.
  Use concise labels such as "LinkedIn" and "GitHub" rather than printing the
  full addresses; verify that the PDF link targets match the candidate profile.
  Apply the same approach to any other profile or portfolio link included.
- Before approving a template change or final resume, compile a populated LaTeX
  sample, inspect all rendered pages at readable scale, check long headings and
  links for overflow, and verify page count and compiler warnings. A preview for
  layout review must be clearly distinguished from an approved application.
- Extract the PDF text and check section order, bullet association, dates, contact
  details, and special characters. Check hyperlinks and embedded fonts. Text
  extraction is a useful parsing check, not a guarantee about every ATS.
- Report source inspection, compilation, visual inspection, and text extraction
  as separate checks. If a compiler or PDF is unavailable, state that limitation;
  do not describe the template as visually verified, perfect, or universally ATS-safe.
