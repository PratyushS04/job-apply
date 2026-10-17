# Resume writing and template review

Reviewed: 2026-09-10.

Scope: `candidate/resume_template.tex`, the master resume, candidate data,
content proposals, and the workflow instructions. The source template has now
been updated for the candidate's India-focused software applications.

## Assessment

The template is a credible starting point for a software resume: conventional
serif typography, black text, clear headings, bullets, and no decorative graphics.
It now uses A4 paper, 0.65-inch margins, wrapping heading tables, an India-relevant
contact location, and the order Experience, Technical Skills, Projects, Education.
It must still be tested with populated content before final approval. No compiled
PDF exists in the inspected workspace. No
`pdflatex`, `xelatex`, or `tectonic` executable was found on PATH, and the checked
common MiKTeX/TeX Live locations were absent. Poppler is available, but it renders
PDFs and cannot compile this LaTeX template.

Validation update (2026-09-10): Tectonic 0.17.0 compiled a populated preview to
one A4 page. Visual inspection found and corrected a collision between the long
degree title and date. A second render showed no clipping or overlap. PDF text
extraction preserved all four sections in the intended order with no unresolved
placeholders. Contact hyperlinks were included. The preview is a layout fixture,
not an approved application resume; every tailored version still needs its own
content and render review.

## Template findings

| Priority | Source location | Finding and recommendation |
| --- | --- | --- |
| Resolved in source | `candidate/resume_template.tex:82` | Experience now precedes skills, projects, and education for the candidate's software applications. |
| Resolved in source; render pending | `candidate/resume_template.tex:40` and `:48` | Heading tables now use wrapping `tabularx` columns. Long real entries still require a rendered check. |
| Medium | `candidate/resume_template.tex:40` through `:64` | Repeated negative vertical spacing compresses headings and bullets. This is a crowding risk, not an observed overlap. Replace ad hoc compression with consistent spacing if the rendered sample is cramped. |
| Resolved in source; render pending | `candidate/resume_template.tex:128` | The education block now includes the degree field and CGPA. Graduation is confirmed as July 2025. |
| Partially resolved | `candidate/resume_template.tex:69` | Location is now present. Social links retain concise labels; verify their targets in the exported PDF. |
| Resolved in source; render pending | `candidate/resume_template.tex:6` | A4 is now the default paper size for the candidate's India-focused applications. |
| Low | `candidate/resume_template.tex:129` | Skills categories omit explicit AI concepts and databases. Add only relevant, supported categories when needed; avoid a long inventory of every tool. No database skill should be invented to fill a category. |

Keep the standard typography and simple hierarchy. The 11pt document class uses
smaller text for bullets and metadata, so verify their actual appearance rather
than treating every element as 11pt. Prefer a readable one-page selection over
fitting the complete master resume into this template.

MIT recommends a familiar, consistent format, at least 10pt type, at least
half-inch margins, specific contributions, and factual accomplishments. These
support the basic review criteria; they do not certify this template's output.
[MIT resume guidance](https://capd.mit.edu/resources/resumes/).

## Writing findings and proposed examples

Authentic wording preserves recognizable work details and the candidate's real
level of responsibility. It does not require slang, mistakes, forced variation,
or a percentage on every line. A reviewer should understand both the contribution
and why it mattered without decoding internal performance-review language.

Examples below are editorial proposals, not newly approved achievements:

- Current: "Resolved a customer-reported stability defect in the
  sync-currency-exchange-rates service, improving the reliability of currency
  exchange-rate synchronization."
  Suggested: "Fixed a customer-reported stability defect in the currency
  exchange-rate synchronization service."
  Reason: retains the actual work and removes a redundant outcome clause.
- Current: "Strengthened engineering documentation by creating detailed Rally
  notes, research findings, and implementation analyses for previously
  undocumented or under-documented GMS areas."
  Suggested: "Documented research findings and implementation decisions for GMS
  areas with limited existing documentation."
  Reason: direct language and a clear knowledge gap, without promotional wording.
- Current: "Advanced internal innovation efforts by drafting three Lift
  proposals, contributing to the Internship Idea Program, and presenting an
  AI-based Hotel Receptionist concept to the GMS initiative group."
  Recommendation: omit from a constrained engineering resume unless innovation
  activity is particularly relevant. Delivered engineering work is stronger
  evidence; this content can support an application answer when appropriate.

Keep useful details such as Java 17, Spring 6, Black Duck, MCP, and the actual
customer defect when relevant. Remove internal ticket numbers like DE93897 from
external resumes unless they convey something the reader needs. Do not substitute
a grander technical claim simply to make a sentence sound impressive.

The existing pending reviews for ContX AI ownership, inferred skills, and
security counts still apply. Natural wording cannot resolve missing factual
support, and the review does not approve those claims.

## Final acceptance checks

1. The opening makes the target role and relevant experience immediately clear.
2. Every included contribution has support, correct ownership, and accurate status.
3. Wording is concise, varied without being forced, and explainable by the candidate.
4. A populated PDF compiles cleanly and has readable spacing without overflow.
5. Extracted text preserves the intended reading order and content; links work.
6. The user approves new claims and the final application under the existing rules.

No promise is made that a human or automated detector cannot identify AI
assistance. The practical standard is accurate, specific, professional writing
that the candidate recognizes as their own experience.
