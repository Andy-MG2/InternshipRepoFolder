# Job Application System

Paste a job description into Claude Code. Get a tailored one-page resume, a
matching cover letter, the saved posting, a log of every change, and a row in a
SQLite tracker. A Streamlit dashboard sits on top.

## Setup

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

Python 3.11+ (tested 3.14.7). SQLite is stdlib. [requirements.txt](requirements.txt)
pins everything: `python-docx` and `reportlab` for rendering, `streamlit[pdf]`,
`pandas`, `plotly` for the dashboard, `claude-agent-sdk` for the chat page.

## Usage

```
/resume-tailoring
<paste the job description>
```

The cover letter runs automatically afterward. Say **"resume only"** to skip it,
or run `/coverletter-tailoring` alone on an existing application folder. For
several postings at once, say so ("these 3 jobs") — see `multi-job-workflow.md`.

Output, one folder per application in `applications/<date>-<company>-<role>/`:

```
job-description.md                                   the posting, verbatim
tailoring-changes.md                                 what changed and why (reorders excluded)
AndyGarcia_<Company>_<Role>_<date>.md/.docx/.pdf     the resume
AndyGarcia_<Company>_<Role>_CoverLetter_<date>.*     the letter
```

## Dashboard

```bash
.venv/bin/streamlit run dashboard/app.py
```

**Applications** — the tracker table. A search box filters by company, role,
stage, type or location. Rows sort by stage (accepted, offer, interviewing,
applied, rejected, ghosted), newest first. Click any row to open its documents
below: resume and cover letter PDFs side by side, then tabs for the tailoring
change log and the job description. A second search box picks an application
by name instead. **Edit mode** swaps the table for a spreadsheet-style editor: edit any cell,
type into the blank bottom row to add an application (company, position, and
date are enough), or select rows and press Delete to remove them. **Save
changes** applies edits, adds, and deletes together; deleted rows leave the
tracker but their folders stay on disk.

**New application** — a chat with Claude Code running the project's skills,
every command auto-approved. Paste a posting and ask for the resume and/or
cover letter as in the terminal; checkpoint questions come back as chat
messages and your reply continues the session. Uses the same login as Claude
Code and is billed the same way. The session survives page reloads (a turn in
progress keeps streaming) and, after a server restart, **Resume last chat**
reconnects to the same conversation with full context.

**Analytics** — range presets (7 / 30 / 90 days / all) or a custom date range,
a stage filter, and day/week grouping. Shows totals, running total over time,
applications per day (click a bar to list that day's applications; drag the
slider to zoom), and outcomes by stage.

## Rules

Non-negotiable constraints in the skills:

- **Structure is frozen, content is not.** The master resume's sections and
  order never change; wording is rewritten to fit the posting.
- **One page.** The renderer exits non-zero on overflow.
- **Never invent** experience, numbers, names, or enthusiasm.
- **Match the verb to the involvement.**

## Renderer

`render_resume.py` owns all layout; the markdown is a content spec.

```bash
.venv/bin/python .claude/skills/resume-tailoring/render_resume.py in.md out.pdf out.docx
.venv/bin/python .claude/skills/resume-tailoring/render_resume.py --letter in.md out.pdf out.docx
```

Times New Roman; name 19pt, body 10pt; margins 0.5in top/bottom, 0.6in sides.
`left — **right**` puts dates flush right. Prints `fits one page: Npt left` or
`OVERFLOW: exceeds one page by Npt` (exit 1).

## Tracker schema

```sql
CREATE TABLE applications (
    id              TEXT PRIMARY KEY,   -- 2026-09-08-stripe-software-engineer-intern
    company         TEXT NOT NULL,
    role            TEXT NOT NULL,
    role_type       TEXT,               -- Internship | Co-op | New Grad
    link            TEXT,               -- job posting
    location        TEXT,
    applied_date    DATE NOT NULL,
    stage           TEXT NOT NULL        -- applied | interviewing | offer
                    DEFAULT 'applied',   -- accepted | rejected | ghosted
    portal_link     TEXT,               -- where to check application status
    portal_email    TEXT,
    portal_password TEXT,               -- plaintext; applications/ is gitignored
    folder          TEXT NOT NULL,
    cover_letter    TEXT NOT NULL DEFAULT 'no'
);
```

The skills insert rows with `stage = 'applied'`. Stage, portal link and
credentials are yours to set — in the dashboard, or directly:

```bash
sqlite3 applications/tracker.db "UPDATE applications SET stage='interviewing' WHERE id='<folder-name>';"
```

## Layout

```
.claude/skills/
├── resume-tailoring/
│   ├── SKILL.md
│   ├── multi-job-workflow.md          batch mode for 2+ postings
│   └── render_resume.py
└── coverletter-tailoring/
    └── SKILL.md
dashboard/
├── app.py                             entry point, page navigation
├── tracker.py                         DB access, search, save
├── agent.py                           Claude Code session for the chat page
└── views/
    ├── applications.py
    ├── analytics.py
    └── new_application.py
experiences/                           source material (gitignored)
├── AndyGarcia_Resume_Master.md
└── notes/                             STAR stories, voice samples
applications/                          output (gitignored)
├── tracker.db
└── <date>-<company>-<role>/
requirements.txt
```

## Not built

- Gmail scanning — propose stage changes from replies, for approval.
