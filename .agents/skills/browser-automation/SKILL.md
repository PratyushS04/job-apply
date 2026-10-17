---
name: browser-automation
description: >-
  Navigate job application websites and fill in application forms using the
  prepared application data. Use this skill when a job has status APP_READY and
  the user has approved the application answers, or when the user explicitly
  asks to fill out or submit an application through the browser. This skill
  defines the browser interaction behavior for ATS systems and career pages.
---

# Browser Automation for Job Applications

Navigate to job application pages and fill in forms using the prepared
application data. This skill defines **what** the browser should do — the
execution is handled by the tool layer (Playwright MCP or equivalent).

## Prerequisites

- Job must have `pipeline_status: "APP_READY"`
- Application answers must be reviewed and approved by the user
- Resume PDF must be compiled and ready for upload
- Browser tool must be available

## Process

### Step 1: Update Status

Set job `pipeline_status` to `"FILLING"`.

### Step 2: Navigate to Application Page

1. Open the job URL from the Job object
2. Look for "Apply" / "Apply Now" / "Submit Application" button
3. Click the apply button to reach the application form
4. If redirected to an external ATS (Lever, Greenhouse, Workday, etc.),
   follow the redirect

### Step 3: Identify the ATS Platform

Recognize common ATS systems by URL pattern or page structure:

| Platform | URL Pattern | Notes |
|----------|-------------|-------|
| Greenhouse | `boards.greenhouse.io` | Multi-step form |
| Lever | `jobs.lever.co` | Single-page form |
| Workday | `*.myworkdayjobs.com` | Complex multi-page |
| iCIMS | `*.icims.com` | May require account |
| Taleo | `*.taleo.net` | Legacy, complex |
| SmartRecruiters | `*.smartrecruiters.com` | Modern, clean |
| AshbyHQ | `*.ashbyhq.com` | Simple form |
| Direct | Company career page | Custom forms |

### Step 4: Fill Form Fields

For each form field:

1. **Identify the field** — read the label, placeholder, or aria-label
2. **Map to prepared data** — look up in `application.required_fields`
   and `application.answers`
3. **Fill the field** — type text, select dropdown options, check checkboxes
4. **Verify** — confirm the field was filled correctly

**Field Type Handling**:
- **Text inputs**: Type the value
- **Dropdowns**: Find the closest matching option and select it
- **Checkboxes/Radio**: Select the appropriate option
- **File upload**: Upload the resume PDF
- **Multi-step forms**: Complete each step before proceeding

### Step 5: Handle Unknown Questions

If the form has questions not predicted during application prep:

1. Take a screenshot of the question
2. Try to draft an answer from candidate data
3. If unsure, flag for user input:
   ```
   ⚠️ New question encountered:
   "Describe a time you led a cross-functional team."
   
   Suggested answer: [draft based on experience data]
   
   Should I use this answer or would you like to modify it?
   ```

### Step 6: Screenshot Before Submit

Before clicking any submit button:

1. Scroll through the entire filled form
2. Take screenshots of each section
3. Save screenshots to `applications/<job_id>/screenshots/`
4. Present to the user for review

Set `pipeline_status` to `"READY_TO_SUBMIT"`.

### Step 7: Wait for Approval

**Do NOT submit without explicit user approval.**

Present the filled application:
```
Application filled for job_001 — Senior Software Engineer at Acme Corp

Screenshots of filled form:
[screenshot_1.png] — Personal information
[screenshot_2.png] — Experience questions
[screenshot_3.png] — Resume uploaded
[screenshot_4.png] — Additional questions

Review the screenshots above. Type "submit" to proceed or provide corrections.
```

## Error Recovery

- **Login required**: Pause and ask the user to log in, then continue
- **CAPTCHA**: Pause and ask the user to solve it
- **Form validation error**: Read the error message, correct the field, retry
- **Page timeout**: Retry navigation up to 3 times
- **Unexpected page structure**: Take a screenshot, report to user

## Important Guidelines

- **Never rush through forms** — verify each field after filling
- **Take screenshots at every major step** — for audit trail
- **Handle multi-page forms** — don't skip pages or sections
- **Respect rate limits** — don't navigate too quickly between pages
- **Save progress** — if the form supports draft saving, save periodically
