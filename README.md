# Job Application System

Paste a job description into Claude Code. Get back a tailored one-page resume, a
matching cover letter, a saved copy of the posting, a written record of every
change that was made and why, and a row in a SQLite tracker.

---

## Status

| Piece | State |
|---|---|
| `resume-tailoring` skill | Working |
| `coverletter-tailoring` skill | Working |
| `render_resume.py` | working |
| SQLite tracker | Working — 4 applications |
| Streamlit dashboard | Not built |
| Gmail scanning | Not built |
| `/apply` slash command | Not built — invoke the skills directly |

---

## Using it

Invoke the skill and paste the posting:

```
/resume-tailoring
<paste the job description>
```

The cover letter runs automatically afterward. Say **"resume only"** to skip it,
or run `/coverletter-tailoring` on its own against an application folder that
already exists.

For several postings at once, say so ("these 3 jobs") — batch mode runs the
experience-discovery interview once across all of them instead of repeating it
per job. See `multi-job-workflow.md`.

**Setup**, once, for the renderer:

```bash
python3 -m venv venv
venv/bin/pip install python-docx reportlab
```

---

## What you get

One folder per application, `applications/<date>-<company>-<role>/`:

```
job-description.md                                   the posting, verbatim
tailoring-changes.md                                 what changed and why
AndyGarcia_<Company>_<Role>_<date>.md/.docx/.pdf     the resume
AndyGarcia_<Company>_<Role>_CoverLetter_<date>.*     the letter
```

`tailoring-changes.md` is the audit trail: what the posting asked for, a coverage
table scoring how much of it landed, every Was → Now rewrite with the source file
that backs it, the questions that got asked, and an honest list of what's still
missing from your background.

---

## The rules that keep it honest

These live in the skills as non-negotiable constraints. They exist because each
one was violated at some point and the output was worse for it.

- **Structure is frozen, content is not.** 
- **One page.** T
- **Never invent** 
- **Match the verb to the involvement.** 
- **Cover letters don't invent enthusiasm.** 

---

## Structure

```
InternshipRepoFolder/
├── .claude/skills/
│   ├── resume-tailoring/
│   │   ├── SKILL.md
│   │   ├── multi-job-workflow.md      batch mode for 2+ postings
│   │   └── render_resume.py           all layout lives here
│   └── coverletter-tailoring/
│       └── SKILL.md
│
├── experiences/                       source material you write  (gitignored)
│   ├── AndyGarcia_Resume_Master.md    the baseline structure
│   └── notes/                         STAR stories, project write-ups,
│                                      past cover letters (voice samples)
│
├── applications/                      output                     (gitignored)
│   ├── tracker.db
│   └── 2026-09-08-stripe-software-engineer-intern/
│       ├── job-description.md
│       ├── tailoring-changes.md
│       └── AndyGarcia_Stripe_SoftwareEngineerIntern_2026-09-08.*
│
├── .gitignore
└── README.md
```

---

## The renderer

`render_resume.py` owns every layout decision, so the markdown stays a *content*
spec. Two modes:

```bash
venv/bin/python .claude/skills/resume-tailoring/render_resume.py in.md out.pdf out.docx
venv/bin/python .claude/skills/resume-tailoring/render_resume.py --letter in.md out.pdf out.docx
```

Times New Roman throughout; name 19pt centered, body 10pt, section headings 10pt
bold with a rule beneath; margins 0.5in top/bottom and 0.6in left/right. In
resume mode, `left — **right**` puts dates flush right at the margin. Letter mode
treats each line as a paragraph and blank lines as spacing, with the same header
so the two documents look like a set.

It prints either `fits one page: 20pt (~2 lines) of space left` or
`OVERFLOW: exceeds one page by 22pt` and exits 1. This matters: the canvas
doesn't paginate, so without the check, overflow silently falls off the page.

---

## Schema

```sql
CREATE TABLE applications (
    id              TEXT PRIMARY KEY,   -- 2026-09-08-stripe-software-engineer-intern
    company         TEXT NOT NULL,
    role            TEXT NOT NULL,
    role_type       TEXT,               -- Internship | Co-op | New Grad
    link            TEXT,
    location        TEXT,
    applied_date    DATE NOT NULL,
    stage           TEXT NOT NULL        -- applied | interviewing | offer
                    DEFAULT 'applied',   -- accepted | rejected | ghosted
    portal_email    TEXT,
    portal_password TEXT,
    folder          TEXT NOT NULL,
    cover_letter    TEXT NOT NULL        -- yes | no
                    DEFAULT 'no'
);
```

The skills write everything except `stage` beyond `'applied'`, `portal_email`,
and `portal_password`. Stage transitions are yours to make.

`portal_password` is plaintext. That's the tradeoff for a single-file store with
no server; it's why `applications/` is gitignored.

---

## Planned

**Dashboard.** `streamlit run dashboard/app.py` over the applications table —
`st.data_editor` for editing stage and pasting portal credentials, plus a stage
breakdown and applications-over-time chart. Worth building once there are enough
rows to look at.

**Email scanning.** Needs a Gmail MCP connector. `/scan-email` would search for
each non-terminal company since its `applied_date`, classify replies, and
**propose** stage changes for approval rather than writing them — rejections and
"still reviewing" look alike to a classifier, and a wrong automatic update costs
more than it saves.
