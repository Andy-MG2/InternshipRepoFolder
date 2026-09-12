# Multi-Job Workflow

Batch processing for 2+ job descriptions. Runs the experience discovery
interview once across all postings instead of repeating it per job.

Referenced from SKILL.md. Uses the same folder conventions:
`experiences/` for source material, `applications/<slug>/` for output,
`applications/tracker.db` for tracking.

---

## Phase 0: Intake

1. Collect all job descriptions. Accept pasted text, URLs, or a mix. Fetch any
   URLs.

2. For each posting, extract company, role title, role type, location, and URL.
   Ask about anything genuinely missing — don't guess.

3. **Create every application folder now, before any tailoring work.** For each:

   ```
   applications/<YYYY-MM-DD>-<company-slug>-<role-slug>/job-description.md
   ```

   This makes the batch resumable. If the session dies partway through, folders
   with a `job-description.md` but no resume file are the ones still outstanding.
   There is no separate batch state file to keep in sync.

4. Run library initialization (SKILL.md Phase 0) once, reading `experiences/`
   including `experiences/notes/`.

5. Confirm the batch with the user:

   ```
   Batch of {N}:
     1. {Company} — {Role}
     2. {Company} — {Role}
     ...

   Library: {N} files, {N} roles, {N} bullets

   Proceed?
   ```

---

## Phase 1: Aggregate gap analysis

Extract requirements from every posting, then cross-reference all of them
against the library at once.

Deduplicate aggressively. "Python", "Python 3", and "proficiency in Python"
are one gap, not three. Requirements phrased differently across postings are
usually the same underlying thing.

Sort the deduplicated gaps into three buckets:

- **Critical** — appears in most or all postings, weak or no library match
- **Important** — appears in several, partial match
- **Job-specific** — one posting only

Present the map:

```
GAPS ACROSS {N} POSTINGS

Critical (appears in {N}/{N}):
  - {gap} — best library match {N}%

Important:
  - {gap} — appears in {N}, best match {N}%

Job-specific:
  - {gap} ({Company} only)

{N} raw requirements → {N} unique gaps
```

The deduplication is the whole point of batch mode. Say how many questions this
saved so the user knows what they're getting.

---

## Phase 2: Shared discovery

One branching interview covering every gap, ordered critical first.

Follow the interview approach in SKILL.md Phase 2.5, with two differences:

**Give multi-job context with each question.** "Three of your five postings ask
for SQL — have you used it anywhere, including coursework or a personal
project?" This tells the user why a question matters and how much a good answer
buys them.

**Tag each discovery with which postings it serves.** A discovery relevant to
four jobs gets used four times; one relevant to a single job might not be worth
pursuing further.

```
DISCOVERED: {short description}
  Context: {where, when, scale}
  Serves: {Company A}, {Company C}, {Company D}
  Draft bullet: "{achievement-focused phrasing}"
```

Time-box it. Twenty minutes is plenty for a batch; if the user is fading, stop
and work with what you have.

**Write every discovery into `experiences/notes/` before moving on.** This is
the part that compounds — next batch starts from a richer library and asks
fewer questions.

---

## Phase 3: Per-job processing

For each posting in the batch, run SKILL.md Phases 1 through 4 against the
enriched library:

- Research (company + role benchmarking)
- Template generation
- Content matching
- Generation into the folder created in Phase 0

Ask the user which mode before starting:

- **Interactive** — stop at the template and matching checkpoints for each job.
  Slower, more control. Use for jobs that matter most.
- **Express** — generate all of them, review at the end. Faster. Use when the
  postings are similar and the library is strong.

Express mode still stops for anything that would require inventing experience.
Never fabricate to avoid interrupting a batch.

Process jobs in the order the user listed them. Report progress as you go:
`[2/5] {Company} — done, {N}% coverage`.

---

## Phase 4: Finalization

Insert one row per application:

```bash
sqlite3 applications/tracker.db "INSERT INTO applications
  (id, company, role, role_type, link, location, applied_date, stage, folder)
  VALUES ('<folder-name>', '<company>', '<role>', '<role type>',
          '<url>', '<location>', '<YYYY-MM-DD>', 'applied',
          'applications/<folder-name>');"
```

Escape single quotes in company and role names by doubling them.

Stage is always `applied`. Never write any other value.

Then summarize:

```
BATCH COMPLETE — {N} applications

  {Company} — {Role}          {N}% coverage
  {Company} — {Role}          {N}% coverage
  ...

Discovered this session: {N} experiences, saved to experiences/notes/
Weakest coverage: {Company} — {biggest remaining gap}
```

Ask whether to revise any individual resume before finishing.

Then, unless the user opted out, run `coverletter-tailoring` across the batch —
one letter per posting, written from each folder's own artifacts. Its batch
section covers the checks that keep the letters from becoming one template with
the company name swapped.

---

## Adding to an existing batch

If the user brings more postings later, don't re-run the full flow:

1. Create folders and save JDs for the new postings (Phase 0, step 3)
2. Rebuild the library — it now includes previous discoveries
3. Run gap analysis on the new postings only, and subtract anything already
   covered by the library
4. Run a short discovery session for the genuinely new gaps only
5. Per-job processing and tracking as normal

Tell the user how many gaps were already covered from previous sessions. That
number is the system paying off.
