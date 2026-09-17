# Setup

## 1. Install

```bash
git clone <repo-url> && cd InternshipRepoFolder
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

Python 3.11+. Claude Code must be logged in on this machine (`claude` in a
terminal, or the VS Code extension) — the dashboard chat reuses that login.

## 2. Add your source material

These folders are gitignored; create them yourself:

```
experiences/
├── AndyGarcia_Resume_Master.md    your master resume — the structure every tailored one keeps
└── notes/                         anything true about your work: STAR stories,
                                   project write-ups, past cover letters (voice samples)
applications/                      created automatically on the first run
```

The master resume must follow the markdown shape in `README.md` → Renderer
(`## SECTION` headings, `left — **right**` for dates).

## 3. Run

```bash
.venv/bin/streamlit run dashboard/app.py
```

Then either paste a job description into the **New application** page, or run
`/resume-tailoring` in Claude Code from the repo root.
