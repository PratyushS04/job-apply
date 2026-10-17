---
name: candidate-profile
description: >-
  Manage the candidate's persistent profile data — load, update, and validate
  profile information stored in the candidate/ directory. Use this skill whenever
  the user wants to view, edit, or populate their profile, experience, skills,
  education, projects, achievements, or job preferences. Also use when any other
  skill needs to read candidate data for matching, resume tailoring, or
  application preparation.
---

# Candidate Profile Management

The candidate's profile is the foundation of the entire job application system.
Every downstream skill (matching, resume tailoring, application prep) depends on
rich, accurate candidate data.

## Data Location

All candidate data lives in the `candidate/` directory at the project root:

```
candidate/
├── profile.json        # Name, contact, links, summary
├── experience.json     # Work experience array
├── projects.json       # Project portfolio array
├── skills.json         # Technical and soft skills
├── education.json      # Education history array
├── achievements.json   # Awards, certifications array
├── preferences.json    # Job search preferences and filters
├── master_resume.md    # Full superset resume (all content)
└── resume_template.tex # LaTeX template with <<PLACEHOLDER>> variables
```

## Loading Candidate Data

When any skill or agent needs candidate information:

1. Read the relevant JSON file(s) from `candidate/`
2. Parse and validate that required fields are non-empty
3. Report any missing critical fields (name, email, at least one experience entry)

For a **full candidate profile load**, read all JSON files and construct a
unified view. This is needed for matching and resume tailoring.

## Updating Candidate Data

When the user provides profile information (via chat, file upload, or paste):

1. Identify which file(s) need updating
2. Parse the user's input into the correct schema
3. Merge with existing data (don't overwrite unless explicitly asked)
4. Write updated JSON back to the file
5. Confirm what was updated

### Schema Reference

**profile.json** fields:
- `name` (string, required)
- `email` (string, required)
- `phone` (string)
- `location` (object: city, state, country)
- `linkedin` (string, URL)
- `github` (string, URL)
- `portfolio` (string, URL)
- `summary` (string, 3-5 sentence professional summary)

**experience.json** — array of:
- `company` (string, required)
- `title` (string, required)
- `start_date` (string, YYYY-MM)
- `end_date` (string, YYYY-MM or empty if current)
- `current` (boolean)
- `location` (string)
- `description` (string)
- `technologies` (string array)
- `achievements` (string array — quantified where possible)

**projects.json** — array of:
- `name` (string, required)
- `description` (string)
- `technologies` (string array)
- `url` (string)
- `highlights` (string array)
- `start_date`, `end_date` (strings)

**skills.json**:
- `technical.languages` (string array)
- `technical.frameworks` (string array)
- `technical.tools` (string array)
- `technical.platforms` (string array)
- `technical.databases` (string array)
- `technical.other` (string array)
- `soft_skills` (string array)
- `certifications` (string array)

**education.json** — array of:
- `institution` (string, required)
- `degree` (string, required)
- `field` (string)
- `start_date`, `end_date` (strings)
- `gpa` (string)
- `coursework` (string array)
- `honors` (string array)

**achievements.json** — array of:
- `title` (string, required)
- `type` (string: "certification", "award", "publication", "talk", "other")
- `date` (string)
- `issuer` (string)
- `description` (string)

**preferences.json**:
- `target_roles` (string array)
- `target_locations` (string array)
- `remote_preference` ("remote", "hybrid", "onsite", "flexible")
- `min_salary`, `max_salary` (number or null)
- `salary_currency` (string)
- `job_types` (string array: "full-time", "part-time", "contract", "internship")
- `industries` (string array)
- `deal_breakers` (string array — things that auto-reject a job)
- `max_experience_years_required` (number or null)
- `min_match_score` (number, 0-100 — jobs below this are auto-skipped)

## Validation

Before any downstream skill uses candidate data, validate:

1. `profile.json` has non-empty `name` and `email`
2. `experience.json` has at least one entry with `company` and `title`
3. `skills.json` has at least one non-empty array in `technical`
4. `education.json` has at least one entry

If validation fails, inform the user which fields are missing and offer to help
fill them in before proceeding with the pipeline.

## Master Resume

The `master_resume.md` file is the human-readable superset of all candidate
content. It should contain everything — the resume-tailoring skill selects
relevant subsets for each specific job. When updating structured JSON files,
also update the master resume to keep them in sync.
