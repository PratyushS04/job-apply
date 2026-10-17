---
name: job-project-generation
description: Generate job-specific personal project entries when relevant projects are missing or the user requests an invented project for a resume. Supports unbuilt project proposals and their explicitly approved inclusion under the workspace exception.
---

# Job-specific personal projects

Apply the invented-personal-project exception in the root `AGENTS.md`. The user
has authorized this capability, including resume inclusion of unbuilt projects;
do not repeatedly ask whether the capability itself is wanted. Approval of a
particular entry remains separate from approval of this workflow.

## Drafting

For a job input, use job intake and analysis, then read its Job Object through
`tools/job_state.py`. Read `state/content_proposals.json` before relevant
candidate data. A general workflow request without a job needs no Job Object.
Do not select an existing job just because it uses an example technology.

Select existing relevant work when available. When it is missing, propose a
coherent personal project mapped to concrete job requirements. Include a title,
a technically consistent stack, scope, and two or three resume bullets. Keep
scope proportionate to a personal project and the target role.

Show the exact proposed resume entry alongside an explicit user-facing note
that it is invented and not built, its job relevance, and assumed features.
The resume entry itself may use completed-work wording under the exception.
Do not invent employment attribution, dates, repository URLs, measured outcomes,
benchmarks, users, or qualifications. Use nonnumeric feature descriptions.
An implementation plan is optional; building is not a prerequisite for inclusion
when the user explicitly approves the invented entry.

## Persistence and approval

Append proposals to `state/content_proposals.json`, preserving its structure and
existing decisions. Use the standard fields from root `AGENTS.md`, plus:

- `content_kind`: `invented_personal_project`
- `actual_status`: `not_built`
- `evidence_status`: `unverified`
- `approval_scope`: approved job ID and artifact targets or explicit reuse scope;
  leave undecided scope empty until the user chooses it

Set `source` to assistant-generated content based on the identified job, not
candidate testimony. Set `confirmation_needed` to approval of exact wording for
use despite unbuilt status. Start with `approval_status: pending` and
`approval_record: null`. Workflow authorization is not entry approval.

For active jobs, merge proposal IDs into `content_review.proposal_ids` using
`tools/job_state.py`, preserving unrelated fields and IDs. Record dependent holds
in `content_review` and retain the last valid pipeline status. Pending decisions
are not `ERROR`. Continue with supported content where possible.

On approval, record the date, user's decision, scope, and that approval permits
invented wording rather than confirming facts. Keep actual status and evidence
unchanged. Rejected entries stay excluded. Material changes require a new linked
proposal. Reuse unchanged wording within approved scope without reconfirmation.

## Resume integration and review

After approval, use resume tailoring to produce a new version with the entry in
personal projects. Record proposal ID, artifact path/version, and what was
applied in the approval record. Clear only the resolved dependent hold. Do not
merge invented entries into canonical candidate JSON or the master resume.

Review the exact approved wording and scope. Disclose the invented entry in the
user-facing review and record it as an approved content exception, never verified
experience. Retain relevance, layout, compilation, PDF checks, and final approval.
An approved exception alone does not block progression. Other claims retain
normal factual review requirements.

Keep evidence-based matching unchanged. Do not revive rejected skill claims or
infer hands-on knowledge from the invented stack. A resume upload can include
the approved entry for its approved application; screening answers or factual
attestations need separate reviewed wording and scope.

If the user later builds the project, create a separate factual-content proposal
describing only work actually done. Confirm it before canonical profile updates;
prior invented wording is not evidence of completion.
