---
name: daily-job-search-setup
description: >-
  Set up the job-apply project's daily job search on a Windows laptop: clone
  the repo, create the Python environment, test the tools, and schedule the
  2am search with Windows Task Scheduler. Use when the user asks to set up,
  install, move, fix, or check the daily job search / job finder / 2am job
  digest on this computer, or to change its time or remove it.
---

# Daily job search setup (Windows)

The job-apply project searches LinkedIn, Indeed, Naukri and Glassdoor every
night and writes a numbered list of the best new jobs to
`state\daily_jobs\latest.md`. In the morning the user replies with numbers
("apply to 1st, 3rd, 9th from today's jobs") and the application agent
prepares those applications, asking before anything is submitted.

This laptop runs both the nightly search and the applications. Do the steps
below in order, report what happened after each, and stop at the first
failure with the exact error.

## Ground rules

- Ask before installing any software (Git, Python) and say what you'll install.
- Never type, store, or ask for passwords or tokens. If Git asks the user to
  sign in to GitHub, let them do it in the window that opens.
- Do not change Windows power, security, or system settings yourself. When
  a setting is needed, tell the user where it is and let them change it.
- Do not commit, push, or switch other people's branches. The user's branch
  is `feature/kali-job-discovery`; `feature/prats` and `feature/sarvesh`
  belong to Pratyush and Sarvesh.
- Use PowerShell. Paths below are relative to the repo folder.

## 1. Get the code

1. Check Git: `git --version`. If missing, ask to install it
   (`winget install --id Git.Git -e`), then open a new terminal.
2. If the repo is not on this laptop yet, ask the user where to put it
   (default `%USERPROFILE%\job-apply`) and clone it:
   `git clone https://github.com/PratyushS04/job-apply.git "$env:USERPROFILE\job-apply"`
   If it already exists, `cd` into it and run `git status`. Stop and ask if
   there are uncommitted changes.
3. `git fetch origin`, then `git switch feature/kali-job-discovery`
   (if that fails: `git switch -c feature/kali-job-discovery --track origin/feature/kali-job-discovery`).
4. Confirm these exist: `tools\daily_search.py`, `tools\discover_jobs.py`,
   `tools\schedule\install_daily_search.ps1`, `tools\schedule\run_daily_search.cmd`,
   `candidate\job_search.json`.

## 2. Python environment

The job finder needs Python 3.10 or newer (3.12 recommended).

1. `py -3.12 --version`. If missing, ask to install it
   (`winget install --id Python.Python.3.12 -e`), then open a new terminal.
2. In the repo: `py -3.12 -m venv .venv`
3. `.venv\Scripts\python.exe -m pip install --upgrade pip`
4. `.venv\Scripts\python.exe -m pip install -r requirements.txt`

## 3. Test

1. Offline tests; each must end with "tests passed":
   - `.venv\Scripts\python.exe tools\discover_jobs.py --test`
   - `.venv\Scripts\python.exe tools\daily_search.py --test`
   - `.venv\Scripts\python.exe tools\find_and_match.py --test`
   - `py -3 tools\job_state.py --test`
2. A live run through the same script the schedule uses (takes 1-3 minutes):
   `tools\schedule\run_daily_search.cmd candidate`
3. Check `logs\discovery\daily_search.log` ends with "Digest written to ...",
   then show the user the first five entries of `state\daily_jobs\latest.md`.
   A few failed searches (LinkedIn rate-limits) are fine; all of them failing
   means a network or blocking problem, so report it.

## 4. Schedule it

1. Install the task (2am daily by default; the user may name another time):
   `powershell -ExecutionPolicy Bypass -File tools\schedule\install_daily_search.ps1`
   With another time: add `-Time 07:30`.
2. Verify: `Get-ScheduledTask -TaskName "JobApply Daily Search" | Get-ScheduledTaskInfo`
   shows a NextRunTime for the chosen time.
3. Test the task itself: `Start-ScheduledTask -TaskName "JobApply Daily Search"`,
   wait about two minutes, then check that the log has a new
   "=== Daily job search" section ending in "Digest written". Check
   `LastTaskResult` is 0 with the same Get-ScheduledTaskInfo command.
4. Wake timers: read the current setting with
   `powercfg /q SCHEME_CURRENT SUB_SLEEP RTCWAKE` (read only; change
   nothing). If wake timers are disabled, tell the user: Control Panel >
   Power Options > Change plan settings > Change advanced power settings >
   Sleep > Allow wake timers > Enable (both On battery and Plugged in).

Tell the user what the schedule needs:
- Signed in to Windows (a locked screen is fine; signed out is not).
- Asleep is fine when wake timers are allowed. If the laptop is shut down or
  hibernating, the run happens as soon as possible after it starts again.
- Plugged in is safest; the task is allowed on battery.

## 5. Daily use (tell the user)

- Morning: open `state\daily_jobs\latest.md` (dated copies sit beside it).
- Reply to the agent in this repo: "apply to 1st, 3rd, 4th, 5th, 9th and 10th
  from today's jobs". The orchestrator's Daily Picks Flow imports them with
  `.venv\Scripts\python.exe tools\discover_jobs.py import <numbers>` and
  prepares each application up to AWAITING_APPROVAL.
- Approve the finished ones: "submit all ready" or "submit 1, 3 and 9".
- Change the time: rerun the installer with `-Time HH:MM`.
- Turn it off: `powershell -ExecutionPolicy Bypass -File tools\schedule\install_daily_search.ps1 -Uninstall`.
- Search settings (terms, cities, experience limit, title filters):
  `candidate\job_search.json`.

## Troubleshooting

- `LastTaskResult` not 0: read the end of `logs\discovery\daily_search.log`.
- `UnicodeEncodeError` in the log: run the task through
  `run_daily_search.cmd` (it sets UTF-8), not python directly.
- Task never ran overnight: check the user was signed in and wake timers are
  enabled; Modern Standby laptops sometimes ignore wake timers. Then the run
  happens when the laptop wakes, thanks to "start when available".
- `py -3.12` not found right after installing Python: open a new terminal.
