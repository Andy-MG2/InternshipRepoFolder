---
name: coverletter-tailoring
description: Writes a cover letter for a specific job application in the user's own voice, reusing the research, job description, and tailored resume that resume-tailoring already produced instead of repeating that work. Runs automatically alongside resume-tailoring unless the user opts out, works standalone, supports multi-job batches, and never invents experience or enthusiasm.
---

# Cover Letter Tailoring

## Overview

The companion to `resume-tailoring`. The resume proves the match; the letter
explains the choice — why this role, why this person, in language a human
actually wrote.

**Core principle:** same as the resume skill — truth-preserving. Never invent
experience, interest, or a connection to the company.

**Second principle:** never redo work the resume run already did. The research,
the JD analysis, the gap list, and the discovery interview all live in the
application folder. Read them.

---

## When It Runs

**Alongside `resume-tailoring` — the default.** After the resume's Phase 4
finishes, write the letter for that application without being asked again.

Do not run it when:
- The user says resume only, no cover letter, or skip the letter
- The posting states no cover letter is accepted

Ask before writing only when the choice is genuinely open — for example the user
said "just the resume for now" earlier in the session and it is unclear whether
that still holds. One line, not a checkpoint: *"Want the cover letter for this
one too?"*

**Standalone.** The user asks for a letter for a role with no application folder,
or an existing folder whose resume was generated in an earlier session. Same
output, but this skill does the research itself — see Inputs.

---

## Non-Negotiable Constraints

### 1. Never invent

Everything in `resume-tailoring`'s Constraint 3 applies here unchanged, including
**matching the verb to the level of involvement** — a letter is where scope
inflation is easiest and least noticed. "Reviewed the CI/CD pipeline" does not
become "owned the release process" because the sentence needed a stronger verb.

Letters add three ways to fabricate that resumes don't have:

- **Invented enthusiasm.** Never claim to use, follow, or admire a product the
  user has not mentioned using. "I've been a user of X for years" is a lie the
  first interview question exposes.
- **Invented connection.** No mutual contacts, no events attended, no talks
  watched, unless they appear in `experiences/` or the user says so.
- **Invented company knowledge.** Only reference company facts that came from
  the job description, the user's own material, or research you actually
  performed this session. Never from memory of the company.

### 2. One page, and shorter is better

250-350 words of body text. Four paragraphs. The renderer reports space left;
a letter that fills the page is usually padded.

### 3. The letter is not the resume in sentences

Never restate a resume bullet. The letter takes one or two things the resume
lists and says what they were actually like — the decision made, the problem
that took longest, why the approach was chosen. If a sentence could be deleted
and the resume would still convey it, delete it.

### 4. It has to sound like the user

See **Voice** below. A letter that reads like an LLM wrote it fails, even if
every fact in it is true.

### 5. Do not bury the lead
Burying the lead. If you have a direct connection to the role (you use their product, you know someone there, you have deep domain expertise), say it in the first line.

---

## Inputs

**Companion mode** — read these from `applications/<folder>/`, and do not
regenerate any of them:

| File | What to take from it |
|---|---|
| `job-description.md` | The role's own words, the team, the domain, any named product |
| `tailoring-changes.md` | "What the posting wants" (the analysis is done), Coverage, and **Gaps** |
| `AndyGarcia_<Company>_<Role>_<date>.md` | What the resume already claims, so the letter doesn't repeat it |

**No discovery interview** — `resume-tailoring` Phase 2.5 already ran and its
findings are in `experiences/notes/`. Repeating it wastes the user's time and
risks contradicting the resume.

**Company research is this skill's job, not the resume's.** The resume is
screened on JD keywords and never names the employer; the letter is read by the
hiring manager, and "why this company" is the paragraph that earns the callback.
Run 2-3 searches per posting — what the team actually builds, a recent launch or
engineering post, how they describe their own work — and use only what comes
back. **Never state a company fact you did not verify this session**, and prefer
a fact the posting itself supplies over one you found. If the searches return
nothing usable, open on the work instead; that is always available.

**Standalone mode** — read `job-description.md` if the folder exists, otherwise
take the posting from the user and save it there first. Then do a short version
of `resume-tailoring` Phase 1 (JD parse + company research), and read the master
resume for what the user can honestly claim.

**Always read, both modes:**
- `experiences/` — the master resume and any tailored ones
- `experiences/notes/` — STAR stories, project write-ups; the "why" material a
  letter needs and a resume has no room for
- `experiences/notes/*Cover_Letter*.md` and `coverletters/*.md` — **the voice
  samples.** These are how the user actually writes. Read them before drafting.

---

## Voice

The user's own letters are the specification. Read them every run; the notes
below are what they currently show, not a replacement for reading them.

**What his letters do:**
- Open with the specific thing that caught his attention — a detail of the role,
  something seen at an event, a problem he has been circling. Never with the
  fact that he is applying.
- Use contractions throughout: I'm, I've, didn't, it's.
- Name real technologies plainly, without adjectives: "Python, Flask, and SQL
  Server", not "cutting-edge technologies".
- State the standing facts in one plain sentence: senior at NJIT studying
  Computer Science, recently accepted into the BS/MS program.
- Vary sentence length. Short declaratives sit next to longer ones.
- Occasionally allow one dry, human aside — the Google letter mentions the
  bathrooms at the summit. At most one per letter, and only if it is true.
- Close plainly: "I'd welcome the chance to talk through…", then "Thank you for
  your time and consideration."

**Banned outright** — these are the tells:

`I am writing to express my interest` · `passionate about` · `leverage` ·
`delve` · `tapestry` · `in today's fast-paced world` · `wealth of experience` ·
`I am confident that I would be a great fit` · `eager to contribute` ·
`I believe my skills align` · `thrilled` · `Furthermore` · `Moreover` ·
`Additionally,` as a paragraph opener · `not only… but also` ·
`It's not just X, it's Y` · three-adjective lists · em-dash tricolons ·
any sentence that could describe a different applicant

**Other rules:**
- No two consecutive sentences may start with "I".
- No paragraph is a summary of the paragraph before it.
- Don't end on a grand statement about the future of the industry.
- Never describe yourself with a superlative or a personality adjective
  ("driven", "detail-oriented"). Show it or drop it.
- Read the draft aloud in your head. Anything you would not say to a person at a
  table gets cut.

---

## Structure

Header: name and contact, matching the resume. Then the date, the company and
team, the salutation. Address a named person only if the user supplied one —
never guess a hiring manager's name. Otherwise "Dear Hiring Team," or the team
name from the posting.

**Paragraph 1 — the hook.** The specific reason this posting, in one or two
sentences, connected to something real the user has done. Best source: a
responsibility in the JD that matches work the user actually did.

**Paragraph 2 — the evidence.** The two strongest matches from the resume's, and exeperience folder
coverage table, told as work rather than credentials: what the problem was, what
was decided, what came out of it. This is where `experiences/notes/` earns its
keep — the notes hold the reasoning the resume had no room for.

**Paragraph 3 — the fit.** Why this company, using only facts you actually have.
Show you have done your homework. Reference their product, mission, recent news, company culture, or a specific project. Explain why this matters to you personally. Generic flattery ("I admire your innovative approach") does not count.
Where the user stands (senior at NJIT, BS/MS) and what they are looking for. If
a `tailoring-changes.md` gap is a stated requirement, one honest sentence goes
here — what is adjacent, and how they closed a comparable gap before. Never
apologize, never say "although I lack".

**Paragraph 4 — the close.** make it have a clear call to action.  "I'd welcome the chance to discuss how my experience in X could support your team's work on Y. I'm available for a conversation at your convenience." Confident, not desperate. One sentence offering a conversation, one thanking
them. Then "Sincerely," and the name Confident, not desperate.

---
## Cover Letter Example
Too generic:

Dear Hiring Manager,

I am writing to express my interest in the Marketing Manager position. I have 5 years of marketing experience and am a strong communicator with excellent organisational skills. I believe I would be a great addition to your team.

Right approach:

Hi Sarah,

Your job listing mentioned you are looking for someone to rebuild the content strategy from the ground up — that is exactly what I did at Redgum Digital over the past two years, taking their blog from 400 monthly visitors to 12,000 and making it their primary lead channel.

The two things that stood out in the listing were the focus on SEO-driven content and the need to work closely with the sales team on case studies. At Redgum, I built both of those functions: a keyword-driven editorial calendar that targeted commercial intent terms, and a case study pipeline where I partnered with account managers to document client wins monthly. Five of those case studies became our top-converting landing pages.

I have been following [Company]'s expansion into the SME market since the product launch in October. The positioning challenge — making enterprise-grade software feel approachable for smaller teams — is something I find genuinely interesting, and it is the kind of messaging work I do best.

I would welcome the chance to talk through how I could help build out your content operation. Happy to chat whenever suits.

---

## Generation

**Never ask permission to run a command.** Writing the letter, rendering the PDF
and DOCX, and updating the tracker are the task itself — run them. Asking the
user to approve each one wastes their time. Ask about content only.

Write into the same application folder as the resume:

```
applications/<YYYY-MM-DD>-<company-slug>-<role-slug>/
  AndyGarcia_<Company>_<Role>_CoverLetter_<YYYY-MM-DD>.md
  AndyGarcia_<Company>_<Role>_CoverLetter_<YYYY-MM-DD>.docx
  AndyGarcia_<Company>_<Role>_CoverLetter_<YYYY-MM-DD>.pdf
```

Company and Role in the filename match the resume's exactly, so the two files
sort together in a portal upload.

**Markdown shape** — one line per paragraph, blank line between blocks:

```markdown
# Andy M. Garcia

(908) 242-4501 | garciaa262005@gmail.com | /in/andymg2 | github.com/Andy-MG2

{Month D, YYYY}

{Company}
{Team or role, if the posting names one}

Dear {Hiring Team / named person},

{Paragraph 1}

{Paragraph 2}

{Paragraph 3}

{Paragraph 4}

Sincerely,

Andy Garcia
```

**Render with the same renderer as the resume, in letter mode** — Times New
Roman, same margins, same centered header, so the pair looks like one set:

```bash
<scratchpad>/venv/bin/python .claude/skills/resume-tailoring/render_resume.py --letter \
    <folder>/AndyGarcia_<Company>_<Role>_CoverLetter_<date>.md \
    <folder>/AndyGarcia_<Company>_<Role>_CoverLetter_<date>.pdf \
    <folder>/AndyGarcia_<Company>_<Role>_CoverLetter_<date>.docx
```

`--letter` treats each line as a paragraph and blank lines as spacing. It reports
space left and exits non-zero on overflow, exactly like the resume path. Never
hand-build the DOCX or PDF.

No new tracker row — the letter belongs to the application the resume already
recorded. Set its `cover_letter` column to `'yes'`:

```bash
sqlite3 applications/tracker.db "UPDATE applications SET cover_letter='yes' WHERE id='<folder-name>';"
```

---

## Multi-Job Batches

When `resume-tailoring` ran `multi-job-workflow.md`, write one letter per
posting after the batch resumes are done, reading each folder's own
`job-description.md` and `tailoring-changes.md`.

**The risk in batch mode is a template with the nouns swapped.** Before
finishing, compare the letters against each other:

- Paragraph 1 must be different in *substance* for every posting, not just in
  company name
- Paragraph 3 must reference something true and specific to each company
- No sentence may appear in two letters

Paragraph 2 may legitimately reuse the same projects across postings — that is
the user's real experience — but the framing follows each posting's priorities.

If two postings are so similar that the letters converge, say so and ask whether
the user wants one letter reused rather than pretending they are distinct.

---

## Report and using resume/ resume generated artifacts

```
applications/<folder-name>/
  AndyGarcia_<Company>_<Role>_CoverLetter_<date>.md / .docx / .pdf

{N} words, one page, {N}pt of space left.
Hook: {the specific thing paragraph 1 opens on}
Evidence: {the two matches used}
Gap addressed: {which, or none}

Next: 1) done  2) revise a paragraph  3) different angle on the opening
```

Then offer the honest read: if the letter is thin because the match is thin, say
that rather than dressing it up.

---

## Edge Cases

| Situation | Handling |
|---|---|
| No application folder | Standalone mode — save the JD to a folder first, then research |
| Resume from an earlier session | Read the folder's files; do not re-run research or discovery |
| No honest hook available | One targeted search; if still nothing, open on the work |
| Posting names no company (recruiter listing) | Write to the role; skip the company paragraph and say so |
| User wants a named recipient | Ask for the name; never guess or search for one to guess with |
| Gap is a hard requirement | One honest sentence, or leave it out — never claim it is covered |
| Letter overflows a page | Cut paragraph 2 first; it is always the one that grew |
| User asks for a letter only, no resume | Fine — run standalone, and mention the resume skill exists |
