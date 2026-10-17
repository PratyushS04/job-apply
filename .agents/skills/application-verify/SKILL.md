---
name: application-verify
description: >-
  Verify a filled-out job application before submission by checking all form
  fields, screenshots, and data accuracy. Use this skill when a job has status
  READY_TO_SUBMIT and needs pre-submission verification, or when the user asks
  to double-check or verify an application before submitting.
---

# Application Verification

Final quality check before submitting a job application. Acts as a safety net
to catch errors before they become permanent.

## When to Use

- Job has `pipeline_status: "READY_TO_SUBMIT"`
- User asks to verify, check, or review a filled application
- After browser automation completes form filling

## Verification Checklist

### 1. Personal Information
- [ ] Name matches profile exactly (no typos)
- [ ] Email is correct and professional
- [ ] Phone number is correct with country code
- [ ] LinkedIn URL is valid and correct
- [ ] Location/address is accurate

### 2. Resume
- [ ] Correct resume version was uploaded (tailored for this job)
- [ ] File uploaded successfully (not 0 bytes, correct format)
- [ ] Resume filename is professional (not "resume_final_FINAL_v2.pdf")

### 3. Application Answers
- [ ] All required questions answered (no empty required fields)
- [ ] Answers are consistent with the resume and profile
- [ ] No placeholder text remaining ("[fill in]", "TODO", "<<>>")
- [ ] Salary expectations are reasonable for the role and market
- [ ] Years of experience claims match actual experience

### 4. Form Completeness
- [ ] All form pages/steps have been completed
- [ ] All required fields are filled (no red validation errors)
- [ ] Dropdown selections are correct (not default/placeholder values)
- [ ] Checkboxes for terms/agreements are checked as appropriate

### 5. Content Quality
- [ ] No obvious copy-paste artifacts
- [ ] No mention of other companies in answers (common mistake)
- [ ] Company name is spelled correctly in all answers
- [ ] Job title referenced correctly

### 6. Screenshot Audit
- [ ] Screenshots exist for all form sections
- [ ] All visible fields in screenshots appear correctly filled
- [ ] No error messages visible in any screenshot

## Process

### Step 1: Load Data

1. Read the job object from `jobs/<job_id>.json`
2. Read application data from the `application` section
3. Load screenshots from `applications/<job_id>/screenshots/`
4. Load the candidate profile for cross-reference

### Step 2: Automated Checks

Run through the verification checklist programmatically where possible:
- Check for empty required fields
- Verify name/email consistency
- Detect placeholder text patterns
- Verify resume file exists and has content

### Step 3: Visual Verification

Examine screenshots for:
- All fields visually filled
- No red error indicators
- Correct data in each field
- Professional appearance

### Step 4: Report

```
Verification Report: job_001 — Senior Software Engineer at Acme Corp

✅ PASS (12/14 checks)

✅ Personal info: All correct
✅ Resume: resume_v1.pdf uploaded (245 KB)
✅ Required fields: All 8 filled
✅ Answers: 5/5 questions answered

⚠️ WARNINGS:
1. Salary field says "Negotiable" — some systems prefer a number
2. Start date says "Immediately" — verify this is accurate

❌ ISSUES:
None

Recommendation: READY TO SUBMIT
```

### Step 5: Update Status

- If all checks pass: keep `pipeline_status` at `"READY_TO_SUBMIT"`
  and set `pipeline_status` to `"AWAITING_APPROVAL"`
- If issues found: report them and keep at `"READY_TO_SUBMIT"` until fixed
