---
name: resume-tailoring
description: Use when creating tailored resumes for job applications - researches company/role, conducts branching experience discovery to surface undocumented skills, and rewrites the user's master resume content to fit the job description while keeping its structure, one-page length, and exact formatting, without fabricating experience
---

# Resume Tailoring Skill

## Overview

Takes a job description and produces one application folder containing the JD,
a tailored resume in MD + DOCX + PDF, and a written record of every change made
and why.

**Core principle:** truth-preserving optimization. Maximize fit with the
posting; never fabricate. The structure of the master resume is fixed; the
words inside it are not.

**Mission:** a person's ability to get a job should rest on their experience,
not on their resume-writing skill.

---

## Non-Negotiable Constraints

These override every other instruction in this file. A resume that violates one
is a failure even if it scores well on JD coverage.

### 1. Structure is frozen. Content is not.

The baseline is `experiences/AndyGarcia_Resume_Master.md`. Copy it, then rewrite
inside its skeleton.

**Change freely — this is the actual work, and it should be visible:**
- Rewrite any bullet into the JD's terminology, as long as the facts hold
- Reorder or swap items *within* a list (Languages, Coursework, Tools)
- Add a real tool/skill to a list when it appears in `experiences/` or `notes/`
- Fold a genuine detail from `experiences/` or `notes/` into an existing bullet
- Swap which coursework, achievement, or project descriptor is listed
- Tighten or lengthen a bullet to use the page well
- Fix grammar, tense, and misspelled proper nouns

**Ask the user before doing any of these:**
- Adding, removing, renaming, or reordering sections
- Reordering roles or projects
- Changing how many bullets a role or project gets
- Splitting one bullet into several, or merging several into one
- Moving content between sections
- Retitling a role or changing a company, date, or degree

A diff against the master should show **zero structural lines changed and many
content lines changed**. If a posting genuinely calls for restructuring, say so
and let the user decide — never restructure first and explain after.

### 2. One page, and the master's exact look

One page, always. The renderer reports remaining space or overflow; resolve
overflow by cutting words from the *newly added* material first, never by
dropping content that was already on the master.

Typography is fixed and is produced only by `render_resume.py` (Phase 4.3) —
never hand-build a DOCX or PDF:
- Times New Roman throughout
- Name 19pt centered; contact 9.5pt centered; body 10pt; section headings 10pt bold
- Section headings uppercase with a full-width rule beneath
- **Dates right-aligned at the right margin** on every entry line
- Margins 0.5in top/bottom, 0.6in left/right

### 3. Never invent an experience

Course titles, certifications, employers, job titles, tools, team names,
credentials, and **numbers** must appear somewhere in the user's own material,
spelled the way they spell it.

A note describing something is not a name for it. "a course on big data which
teaches us AWS, Java, and Hadoop" licenses `Big Data` — it does not license an
official-sounding course title you synthesized.

Misspelled proper nouns in the source ARE fixed, since the real-world spelling
is verifiable: `Pyanote` → `pyannote`, `Sickit-Learn` → `Scikit-learn`.

**Match the verb to the level of involvement. This is the most common way this
skill fabricates.** The source material records exactly how far the user's own
hands went — attended, observed, reviewed, shadowed, assisted, accepted, built,
led, shipped. Never promote one of those to a stronger one:

- "reviewed the CI/CD pipeline" ≠ "worked the SDLC end to end"
- "gained exposure to" ≠ "owned" / "drove" / "ran"
- "contributed to" ≠ "architected"
- "on a team that built X" ≠ "built X"

If a note says a step was *not* done — not merged, not deployed, not executed,
not in production — the resume must not imply it was, in any phrasing. When the
posting rewards a scope the user did not have, that is a **gap**: record it in
`tailoring-changes.md`. A gap is never closed with a stronger verb.

When a bullet already states the involvement level accurately, the safest edit
is no edit. Leave it as the master has it and spend the tailoring elsewhere.

### 4. Ask instead of guessing

When a bullet would be stronger with a detail that is not in `experiences/` or
`notes/` — a metric, a scale, a duration, a team size, a technology you suspect
was used — **ask the user**. Never estimate, never round up, never write "~" or
a vague magnifier ("significantly", "dramatically") in place of a number the
user never gave.

Collect these into **one batch of questions** before generation rather than
interrupting repeatedly:

```
To sharpen this resume for {Company}, three things would help. Skip any you
don't have:

1. {Bullet} — the JD asks for scale. Roughly how many {records/users/queries}?
2. The JD lists {tool}. Did you use it in {project}, or should I leave it out?
3. {Bullet} — did this ship to production, or stay a prototype?
```

Anything the user doesn't answer stays as it is in the master. An unanswered
question is never a license to fill the blank yourself.

---

## When to Use

Use when the user provides a job description and wants a tailored resume.

Do not use for: resume writing from scratch with no library, cover letters
(separate skill), or LinkedIn optimization.

---

## Inputs and Outputs

**Inputs**
- Job description (pasted text or URL)
- `experiences/` — master resume + any prior tailored resumes (`*.md`)
- `experiences/notes/` — cover letters, STAR stories, project write-ups, raw notes

**Outputs** — one folder, `applications/<YYYY-MM-DD>-<company-slug>-<role-slug>/`:

```
job-description.md                                    Full JD text, verbatim
tailoring-changes.md                                  Every change + why (4.4)
AndyGarcia_<Company>_<Role>_<YYYY-MM-DD>.md           Tailored resume  (4.2)
AndyGarcia_<Company>_<Role>_<YYYY-MM-DD>.docx         Word version     (4.3)
AndyGarcia_<Company>_<Role>_<YYYY-MM-DD>.pdf          PDF version      (4.3)
```

Plus one row in `applications/tracker.db` (4.5).

**Filename rule:** `AndyGarcia_<Company>_<Role>_<YYYY-MM-DD>.<ext>`. Company and
Role are PascalCase with no spaces or punctuation — `JPMorganChase`,
`DataAISummerAnalyst`, `Stripe`, `SoftwareEngineeringIntern`. A recruiter sees
this filename in the portal, so it carries the user's name, the company, and the
role — never a generic `resume.docx`. The company and role appear in the
**filename only**; nothing about the target employer appears inside the resume.

`job-description.md` and `tailoring-changes.md` keep fixed names.

---

## Workflow

Phase 0 → 1 → (2.5 optional) → 3 → 4 → 5. Stop at each checkpoint.

**Never ask permission to run a command.** Creating folders, writing files,
rendering the PDF and DOCX, and inserting the tracker row are the task itself —
run them. Asking the user to approve each one wastes their time. Checkpoints are
for content decisions only; mechanics are never a checkpoint.

Multiple postings in one request (2+ URLs, "these 3 jobs", a list of companies)?
Offer batch mode and follow `multi-job-workflow.md`. Single-job flow below is
unchanged by it.

### Phase 0: Library Initialization

Always runs first.

Read both locations — `experiences/*.md` and `experiences/notes/*.md` (skip
`notes/` silently if absent). Announce: "Building library... {N} resumes,
{N} supporting notes."

**The two locations are parsed differently. Getting this wrong fabricates
experience.**

**`experiences/*.md` — resumes.** Resume-ready text. Extract roles, bullets,
skills, education, and the formatting pattern. These bullets may be used
verbatim or rewritten. The file named `*_Master*.md` is the baseline structure.

**`experiences/notes/*.md` — evidence, not resume content.** Cover letters,
STAR stories, project write-ups, planning docs. Do NOT extract "roles" from
these — a project write-up is not a job, and a planning doc's headings are not
job titles. Index what the user did, where, with what technologies, and any
metrics *they stated*. **Never lift a line from `notes/` verbatim** — it is
first-person prose, not an achievement bullet. Notes answer gaps (Phase 2.5)
and feed drafted bullets that the user confirms (Phase 3.3). A hackathon plan
describes what a team intended to build, not what the user shipped.

Build an in-memory library:

```json
{
  "roles": [{"company": "", "title": "", "dates": "",
             "bullets": [{"text": "", "themes": [], "metrics": [],
                          "keywords": [], "source": "resume.md"}]}],
  "skills": {"languages": [], "frameworks": [], "ai_ml": [], "tools": []},
  "education": [],
  "evidence": [{"source": "notes/Projects.md", "topic": "",
                "what_user_did": "", "technologies": [], "metrics": [],
                "resume_ready": false}]
}
```

`evidence` entries are always `resume_ready: false`. They become resume content
only after being drafted into a bullet and confirmed by the user.

### Phase 1: Research

**1.1 Parse the JD.** Extract required skills, preferred skills, responsibilities,
recurring terminology, role archetype, seniority signals, and red flags. Keep a
**keyword inventory** — the exact words the posting and its ATS will screen on.

**1.2 Company research — conditional, usually skip.** The resume never names the
employer, and screening matches the posting's words, not the company's. Run it
only when the JD is thin on terminology: one search for how the company words
this kind of work, feeding the keyword inventory. Real company research belongs
to `coverletter-tailoring`, where it converts.

**1.3 Role benchmarking — conditional.** Only when the JD leaves the role
archetype genuinely unclear. One search; skip gracefully if sparse.

**1.4 Success profile.** Core requirements, valued capabilities, cultural
signals, narrative themes, terminology map (user's words → their words), risks.

**Checkpoint:** present the success profile and the keyword inventory in 5-8
lines. "Does this match your read of the role? Anything to add?" Wait.

### Phase 2: Template

**The template is the master resume.** Same sections in the same order, same
roles in the same order, same bullet counts. There is nothing to design here —
confirm the baseline and move on.

Only if the user has asked for a structural change, or you proposed one and they
approved it, deviate — and record it in `tailoring-changes.md`. Options worth
proposing (never doing unprompted): consolidating two positions at the same
company, reframing a title toward the target role's standard terminology, or
re-allocating bullets toward the most relevant role. Company names, dates, and
degrees are exact and never negotiable.

### Phase 2.5: Experience Discovery (optional)

If Phase 1 surfaced requirements the library answers weakly, offer a 10-15
minute branching interview:

```
{N} requirements have weak or no match in your library:
  - {requirement} — best match {N}%
  - {requirement} — no match

Want to spend ~10 minutes surfacing experience you haven't written down?
```

Run it conversationally, one gap at a time:
1. **Open probe** — "Have you worked with {skill}, anywhere — coursework,
   personal projects, a class assignment?"
2. **Branch** — strong answer → dig for scale, challenge, outcome, metrics.
   Indirect/adjacent → explore transferability. No → move on quickly.
3. **Qualify** — did *you* do it, or a teammate? Did it ship or stay a plan?
   Any numbers?
4. **Capture immediately** as `Context / Scope / Addresses gap / Draft bullet`.

Help articulate; never fabricate. Time-box it and stop when the user fades.

Write every discovery into `experiences/notes/` before moving on — that is the
part that compounds.

### Phase 3: Fit Maximization

This is where the resume actually gets tailored. Work bullet by bullet through
the master.

**3.1 Map the keyword inventory to evidence.** For every keyword and requirement
from Phase 1, find where in the library it is genuinely supported. Mark each
one: `covered` (already on the master, possibly in different words),
`coverable` (true and supported by `experiences/` or `notes/`, but not on the
master today), or `gap` (no honest support).

**3.2 Rewrite each bullet toward the posting.** Score candidates when a slot has
options:

```
Direct match (40%) + Transferable (30%) + Adjacent (20%) + Impact (10%)
  90-100% DIRECT   75-89% TRANSFERABLE   60-74% ADJACENT   <60% GAP
```

Then apply these moves, in order of preference:

| Move | Example |
|---|---|
| Terminology swap | "accuracy" → "data quality" when the JD says data quality |
| Surface a buried real detail | add "SQL Server" to a bullet that used it |
| Reorder within a list | move SQL first in Languages for a data role |
| Add a real skill to a list | add AWS to Tools when `notes/` shows AWS use |
| Emphasis shift | same facts, foregrounding the part the JD cares about |
| Abstraction shift | more or less technical detail, matching the audience |

**Use the posting's own words wherever they honestly fit.** If the JD says "data
pipeline", "end to end", "code review", or "data quality" and that is what the
work was, write it that way — matching language is most of what tailoring buys.
Lift phrasing, not requirements: never adopt a phrase describing something the
user didn't do, and never transplant whole sentences from the posting.

Every rewrite must keep the underlying fact intact and traceable to a source
file. If you can't name the source line, don't write the claim.

**Aim high on coverage.** A tailored resume that changes three words has not
been tailored. Expect most bullets to differ from the master in wording while
every one remains true. But do not stuff keywords: a bullet that reads like a
skills list has failed, and a `gap` keyword never gets forced in.

**3.3 Drafting a bullet from `notes/` evidence.** When a `coverable` item has no
resume bullet behind it, draft one and confirm before using it:

```
GAP: {requirement}
EVIDENCE: {source file} — "{excerpt}"
DRAFT: "{achievement-focused bullet}"

Before I use this: did you personally do this, or a teammate? Did it ship, or
stay a plan? Any numbers you can attach?
```

Do not insert the draft until the user answers. Once confirmed, it also gets
written back to `experiences/notes/`.

**3.4 Batch the open questions.** Everything Constraint 4 turned up goes here,
in one message, with the checkpoint below.

**Checkpoint:**

```
TAILORING PLAN — {Company} {Role}

Keyword coverage: {N}/{N} ({N}%)
  Covered already: {list}
  Newly surfaced:  {list}
  Gaps:            {list} — {how each is handled}

Bullets rewritten: {N} of {N}
  {Role}: "{old fragment}" → "{new fragment}"   [reason]
  ...

Questions before I generate:
  1. ...

Structure: unchanged from master.   Approve, or tell me what to adjust.
```

Wait for approval before generating.

### Phase 4: Generation

**4.1 Create the folder.**

```
applications/<YYYY-MM-DD>-<company-slug>-<role-slug>/
```

Slugs are lowercase, hyphenated, alphanumeric ("Bank of America" →
`bank-of-america`, "Software Engineer Intern" → `software-engineer-intern`).

**First action:** write the complete JD text to `job-description.md` — the full
posting, not a summary. It is the record of what was applied to.

**4.2 Write the resume markdown.**

The markdown is a *content* spec; the renderer supplies layout. Follow the
master's shape exactly — the `left — **right**` convention is what puts dates
flush right:

```markdown
# Andy M. Garcia

(908) 242-4501 | garciaa262005@gmail.com | /in/andymg2 | github.com/Andy-MG2

## EDUCATION

**NEW JERSEY INSTITUTE OF TECHNOLOGY** *Newark, NJ* — **Expected May 2027**
*B.S. in Computer Science, Ying Wu College of Computing* | **GPA: 3.8**
- **Relevant Coursework:** ...
- **Achievements:** ...
- **Certifications:** ... — **Aug 2025**

## SKILLS

- **Languages:** ...
- **Frontend, Backend & DB:** ...
- **AI/ML:** ...
- **Tools/Platforms:** ...

## PROFESSIONAL EXPERIENCE

**{Job Title}** — **{Start} - {End}**
*{Company}*
- {bullet}

## PROJECTS

**{Project}** | {Role} | {Descriptor} ({Tech})
- {bullet}
```

Rules that keep the render correct:
- Every entry line ends with ` — **{dates}**`. That trailing bold segment is
  what the renderer right-aligns. Keep it under 44 characters.
- `##` headings are section headings; they get the rule beneath automatically.
- Job title bold on its own line, company italic on the next line.
- No `---` separators, no `###` headings, no tables, no blockquotes.

Save as `AndyGarcia_<Company>_<Role>_<YYYY-MM-DD>.md`.

**4.3 Render DOCX + PDF.** Always both. Never hand-build either.

```bash
# one-time setup
python3 -m venv <scratchpad>/venv
<scratchpad>/venv/bin/pip install python-docx reportlab

# render
<scratchpad>/venv/bin/python .claude/skills/resume-tailoring/render_resume.py \
    <folder>/AndyGarcia_<Company>_<Role>_<YYYY-MM-DD>.md \
    <folder>/AndyGarcia_<Company>_<Role>_<YYYY-MM-DD>.pdf \
    <folder>/AndyGarcia_<Company>_<Role>_<YYYY-MM-DD>.docx
```

The renderer prints one of:

```
fits one page: 34pt (~2 lines) of space left
OVERFLOW: exceeds one page by 22pt (~2 lines) - trim content
```

`OVERFLOW` exits non-zero and means the bottom of the resume is being silently
cut off the page. **Never report done on an overflow.** Trim the newest wording
first — a rewritten bullet that grew, a skill added to a list — and re-render
until it fits. If more than ~4 lines of space are left, there is room to say
something more useful; consider a `coverable` item you left out.

**4.4 Write `tailoring-changes.md`.** Every application folder gets this record.
**Keep it tight** — it is a change log, not an essay. One line per explanation,
no restating the resume, no listing what you chose not to do beyond a short
summary. The Was/Now/Why lines each get their own paragraph so they don't run
together when the markdown renders.

```markdown
# Tailoring Changes — {Company}, {Role}
**Date:** {YYYY-MM-DD}  ·  **Baseline:** experiences/AndyGarcia_Resume_Master.md

## What the posting wants
{5-8 bullets in the posting's own words, most-repeated first. This is the read
of the role, not a copy of the JD — one short line each.}

## Coverage — {N}/{N} ({N}%)

| Asked for | Status | Where it landed |
|---|---|---|
| {requirement} | Covered / Added / Gap | {section — short phrase} |

## JD language now on the resume
{exact words and phrases lifted from the posting because they truthfully
describe the work: "end to end", "data pipeline", "code review". Comma list.}

## Changes

### {Section}

**Was:** {master text}

**Now:** {tailored text}

**Why:** {one line}  ·  **Source:** {file backing the new wording}

{blank line, then the next change}

## Not changed
{2-3 lines total. What stayed verbatim and the one reason why. Do not enumerate
every untouched bullet.}

## Questions asked
- {question} → {answer, or "unanswered — kept master wording"}

## Gaps
{The honest weak spots, most damaging first. For each: what's missing, how much
it costs for this role, and the smallest thing that would close it. Include
standing gaps that show up across applications (a tool listed but thin, a skill
claimed only through coursework) — the user is compiling these over time, so be
specific and useful rather than reassuring.}

## Structure
{One line: unchanged from master, or the change the user approved.}
```

Every content line that changed appears under Changes — that exhaustiveness is
what lets the user audit that nothing was invented. The *explanations* are what
stay short.

**4.5 Record in the tracker.**

```bash
sqlite3 applications/tracker.db "INSERT INTO applications
  (id, company, role, role_type, link, location, applied_date, stage, folder)
  VALUES ('<folder-name>', '<company>', '<role>', '<role type>',
          '<url>', '<location>', '<YYYY-MM-DD>', 'applied',
          'applications/<folder-name>');"
```

- `id` is the folder name; `folder` is `applications/<folder-name>`
- `stage` is always `'applied'` — every later transition is the user's
- Double single quotes in names: `Moody's` → `'Moody''s'`
- Leave `link`/`location` empty if the JD didn't give them; never invent one

**4.6 Report.** In conversation, not in another file:

```
applications/<folder-name>/
  job-description.md
  tailoring-changes.md
  AndyGarcia_<Company>_<Role>_<YYYY-MM-DD>.md / .docx / .pdf

One page, {N}pt of space left.   Tracked as '<folder-name>' (applied).
Keyword coverage {N}%, {N} bullets rewritten, structure unchanged.
Remaining gaps: {gap} — {how handled}

Next: 1) save to library  2) revise  3) done, don't save to library
```

**4.7 Cover letter.** Unless the user has said resume only, run the
`coverletter-tailoring` skill for this application before reporting done. It
reads this folder's `job-description.md`, `tailoring-changes.md`, and the
tailored resume — do not re-run research or discovery on its behalf.

### Phase 5: Library Update (conditional)

If the user picks "save to library": copy (don't move) the tailored `.md` to
`experiences/<company-slug>-<role-slug>.md`, then re-run Phase 0 so its wording
is available to future matches. Only the markdown goes to `experiences/`; the
DOCX and PDF stay in the application folder as the record of what was submitted.

If the user asks for revisions, make them, re-render, and update
`tailoring-changes.md` before re-presenting.

`experiences/` is append-only — never delete a bullet because one posting didn't
need it.

---

## Edge Cases

| Situation | Handling |
|---|---|
| Thin library (1-2 resumes) | Warn, proceed, push harder on Phase 2.5 discovery |
| Critical requirement <60% match | Offer: discovery, reframe best available, leave the slot as-is, or note it for the cover letter. Never force a match |
| Research fails / obscure company | Say so, fall back to JD-only analysis, ask the user for context |
| Vague JD | Name the missing areas, ask the user for what they know, proceed with what's there |
| PDF overflows one page | Trim newest wording first, re-render. Never ship an overflow |
| Renderer fails | Report the error with the markdown intact; do not hand-build a substitute |
| User asks for a restructure | Do it, and record it under "Structure" in `tailoring-changes.md` |

Every checkpoint allows going back a phase. The user can revise at any point.
