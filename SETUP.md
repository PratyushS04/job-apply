# Run the job application workspace

The dashboard is a **local** website. It edits JSON in this repository and shows
an illustrative HTML resume. It does not generate or approve the final PDF.

## 1. Start the dashboard

Use Python 3.9 or newer and run the command from the repository root. No web
packages or Node installation are required.

| macOS Terminal | Windows PowerShell |
| --- | --- |
| `python3 tools/dashboard_server.py` | `py -3 tools/dashboard_server.py` |

Open `http://127.0.0.1:8765`. Stop the server with `Ctrl+C`. The site binds to
your own computer only. It lists `candidate/`, `jobs/`, and `state/` JSON files;
edits make a prior-version copy under `.dashboard/backups/`. Education is visible
but locked. The right pane updates while you edit, supports zero or many projects,
and offers a printable **sample**. A browser refresh loads saved files again.

## 2. Bring in jobs

Paste a job URL to the agent and ask it to follow `AGENTS.md`, or use the URL
intake command directly:

| macOS | Windows |
| --- | --- |
| `python3 tools/intake_urls.py --text "https://example.com/job"` | `py -3 tools/intake_urls.py --text "https://example.com/job"` |

For a CSV, use `tools/intake_csv.py path/to/jobs.csv`. For Excel, install the
optional `openpyxl` package (`python3 -m pip install openpyxl` on Mac or
`py -3 -m pip install openpyxl` on Windows), then use
`tools/intake_excel.py path/to/jobs.xlsx`. The intake scripts create `NEW` Job
Objects; they do not analyze the posting by themselves.

## 3. Run the application flow

Ask the agent: “Analyze `job_001`, match it to my profile, tailor and review the
resume, prepare the application, fill and verify the form, and stop for my final
submission approval. Follow `AGENTS.md`.” The agent uses the Job Object and
updates it through the pipeline. Check the status with:

| macOS | Windows |
| --- | --- |
| `python3 tools/job_state.py summary` | `py -3 tools/job_state.py summary` |

Job-specific invented personal projects can be proposed, but an exact entry and
its job scope need approval before inclusion. Education stays unchanged during
tailoring. Final application submission always needs separate explicit approval.

## 4. Compile and review the final resume

The agent creates `resumes/<job_id>/resume_v<N>.tex`. Tectonic compiles that
source to the application PDF. On Windows, this repository includes
`.tools\tectonic\tectonic.exe`; on macOS, install [Tectonic](https://tectonic-typesetting.github.io/book/latest/installation/)
if `tectonic` is not on your PATH (with Homebrew: `brew install tectonic`).

| macOS Terminal | Windows PowerShell |
| --- | --- |
| `tectonic -X compile --outdir resumes/job_001 resumes/job_001/resume_v2.tex` | `& .\.tools\tectonic\tectonic.exe -X compile --outdir resumes/job_001 resumes/job_001/resume_v2.tex` |

Use the actual job ID and resume version. Inspect the PDF visually and extract
its text before treating it as ready. The website preview is for editing and
orientation; the reviewed PDF is the application artifact.
