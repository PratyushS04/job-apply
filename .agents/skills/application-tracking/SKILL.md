---
name: application-tracking
description: >-
  Track job application status, handle submission flow, and maintain the
  application pipeline. Use this skill when the user asks about the status of
  their applications, wants to submit an approved application, wants a summary
  of all jobs in the pipeline, or needs to manage (skip, retry, resubmit)
  specific jobs. Also use for generating application reports and dashboards.
---

# Application Tracking & Submission

Manage the full lifecycle of job applications — from submission approval through
tracking outcomes.

## Submission Flow

### Human Approval

When a job reaches `"AWAITING_APPROVAL"`:

1. Present a final summary:
   ```
   Ready to submit: job_001
   Position: Senior Software Engineer
   Company: Acme Corp
   Match Score: 78/100
   Resume: resume_v1.tex
   
   Application answers reviewed ✅
   Form verification passed ✅
   
   Type "submit" to proceed, or "skip" to skip this job.
   ```

2. Wait for explicit approval
3. On approval: proceed to submission
4. On skip: set `pipeline_status` to `"SKIPPED"` with reason

### Submission

When the user approves:

1. Click the submit/send button on the application form
2. Wait for confirmation page
3. Take a screenshot of the confirmation
4. Save confirmation screenshot to `applications/<job_id>/screenshots/`
5. Record any confirmation number or reference
6. Set `pipeline_status` to `"SUBMITTED"`
7. Update the `application` section:
   ```json
   "application": {
     "status": "SUBMITTED",
     "submitted_at": "2026-09-05T22:00:00Z",
     "confirmation_number": "REF-12345",
     "confirmation_screenshot": "applications/job_001/screenshots/confirmation.png"
   }
   ```

## Pipeline Management

### Status Summary

When the user asks "what's the status?" or "show me my applications":

```
📊 Application Pipeline Summary
═══════════════════════════════

Total Jobs: 15

NEW (3):
  job_010: https://... (TechCorp)
  job_011: https://... (StartupXYZ)
  job_012: https://... (BigCo)

ANALYZED (2):
  job_008: Backend Developer at DataCo (Score: pending)
  job_009: Full Stack at WebInc (Score: pending)

MATCHED (4):
  job_004: SDE II at Amazon (Score: 82) ✅
  job_005: Backend at Google (Score: 75) ✅
  job_006: DevOps at Meta (Score: 61) ⚠️
  job_007: ML Engineer at OpenAI (Score: 45) ❌

SUBMITTED (3):
  job_001: Senior SE at Acme — submitted Sep 3
  job_002: Backend at Beta — submitted Sep 4
  job_003: SDE at Gamma — submitted Sep 5

SKIPPED (2):
  job_013: Score too low (38/100)
  job_014: Deal-breaker: requires 8+ years

ERROR (1):
  job_015: Page not found (404)
```

### Job Actions

Support these management commands:

- **Skip a job**: `Set pipeline_status to "SKIPPED"` with reason
- **Retry a failed job**: Reset status to appropriate earlier stage
- **Re-analyze**: Reset to "NEW" to re-fetch and re-analyze
- **Priority**: Process specific jobs first (reorder the pipeline)

### Reports

Generate reports on request:

**Application history**: Chronological list of all submissions with dates
**Success rate**: Tracking responses and outcomes over time
**Match analysis**: Distribution of match scores, common skill gaps
**Pipeline velocity**: Average time from intake to submission

## Data Persistence

All tracking data is stored in the individual job JSON files.
The global pipeline state in `state/pipeline.json` provides an aggregated view.

Use `tools/job_state.py summary` to generate the current pipeline state,
and `tools/job_state.py list --status <STATUS>` to filter jobs.
