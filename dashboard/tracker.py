"""Shared data access and constants for the dashboard pages."""

from __future__ import annotations

import re
import sqlite3
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "applications" / "tracker.db"

# Display order: outcomes that matter most first, closed ones last.
STAGE_ORDER = ["accepted", "offer", "interviewing", "applied", "rejected", "ghosted"]
# Validated 6-slot palette (dataviz validator, light mode, all pairs).
STAGE_COLORS = {
    "applied": "#2a78d6",
    "interviewing": "#eda100",
    "offer": "#1baf7a",
    "accepted": "#008300",
    "rejected": "#e34948",
    "ghosted": "#4a3aa7",
}
ROLE_TYPES = ["Internship", "Co-op", "New Grad"]

# Columns the user may edit in the table; everything else is written by the skills.
EDITABLE = [
    "company", "role", "applied_date", "stage", "link", "portal_link",
    "portal_email", "portal_password", "location", "role_type", "cover_letter",
]
SEARCH_COLUMNS = ["company", "role", "stage", "role_type", "location"]


def load_applications() -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as con:
        df = pd.read_sql_query("SELECT * FROM applications", con)
    df["applied_date"] = pd.to_datetime(df["applied_date"]).dt.date
    for col in EDITABLE:
        if col not in df.columns:
            df[col] = None
    text_cols = [c for c in EDITABLE if c != "stage"]
    df[text_cols] = df[text_cols].fillna("")  # NULL would render as the text "None"
    rank = df["stage"].map({s: i for i, s in enumerate(STAGE_ORDER)}).fillna(len(STAGE_ORDER))
    return (
        df.assign(_rank=rank)
        .sort_values(["_rank", "applied_date"], ascending=[True, False])
        .drop(columns="_rank")
        .reset_index(drop=True)
    )


def search(df: pd.DataFrame, query: str) -> pd.DataFrame:
    """Rows where every whitespace-separated term appears in some searchable column."""
    terms = query.lower().split()
    if not terms:
        return df
    haystack = df[SEARCH_COLUMNS].fillna("").astype(str).agg(" ".join, axis=1).str.lower()
    mask = pd.Series(True, index=df.index)
    for term in terms:
        mask &= haystack.str.contains(term, regex=False)
    return df[mask]


def save_changes(original: pd.DataFrame, edited: pd.DataFrame) -> dict:
    """Apply a data_editor result to the DB: updates, added rows, deleted rows.

    Rows are matched by id. Rows in `original` missing from `edited` are
    deleted (the application folder stays on disk). Rows in `edited` with no
    id are new and go through add_application, which needs company, role and
    a date. Returns counts plus any rows that could not be added.
    """
    orig = original.set_index("id")
    has_id = edited["id"].notna() & (edited["id"].astype(str) != "")
    kept, new = edited[has_id].set_index("id"), edited[~has_id]

    updates = []
    for app_id, row in kept.iterrows():
        if app_id not in orig.index:
            continue
        changed = {}
        for col in EDITABLE:
            before, after = orig.at[app_id, col], row[col]
            if pd.isna(before) and pd.isna(after):
                continue
            if before != after:
                changed[col] = None if pd.isna(after) else (
                    str(after) if col == "applied_date" else after)
        if changed:
            updates.append((app_id, changed))
    deleted = [i for i in orig.index if i not in kept.index]

    with sqlite3.connect(DB_PATH) as con:
        for app_id, changed in updates:
            assignments = ", ".join(f"{col} = ?" for col in changed)
            con.execute(f"UPDATE applications SET {assignments} WHERE id = ?",
                        [*changed.values(), app_id])
        for app_id in deleted:
            con.execute("DELETE FROM applications WHERE id = ?", (app_id,))

    added, skipped = 0, []
    for _, row in new.iterrows():
        company = "" if pd.isna(row.get("company")) else str(row["company"]).strip()
        role = "" if pd.isna(row.get("role")) else str(row["role"]).strip()
        if not company or not role:
            skipped.append(f"{company or '?'} — {role or '?'} (needs company and position)")
            continue
        fields = {col: (None if pd.isna(row.get(col)) else row[col]) for col in EDITABLE}
        fields.update(company=company, role=role,
                      applied_date=row["applied_date"] if not pd.isna(row.get("applied_date")) else date.today(),
                      stage=fields.get("stage") or "applied")
        try:
            add_application(fields)
            added += 1
        except ValueError as e:
            skipped.append(str(e))
    return {"updated": len(updates), "added": added, "deleted": len(deleted), "skipped": skipped}


def find_pdfs(folder: str) -> tuple[Path | None, Path | None]:
    """(resume, cover letter) PDFs inside an application folder, if present."""
    path = ROOT / folder
    if not path.is_dir():
        return None, None
    pdfs = sorted(p for p in path.glob("*.pdf") if not p.name.startswith("~$"))
    letters = [p for p in pdfs if "CoverLetter" in p.name]
    resumes = [p for p in pdfs if "CoverLetter" not in p.name]
    return (resumes[0] if resumes else None), (letters[0] if letters else None)


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def add_application(fields: dict, resume_pdf: bytes | None = None,
                    letter_pdf: bytes | None = None, resume_name: str = "",
                    letter_name: str = "") -> str:
    """Insert a manually tracked application and create its folder.

    Same id/folder convention as the skills. Uploaded PDFs are saved into the
    folder under their original names; a cover letter that lacks "CoverLetter"
    in its name gets the prefix so find_pdfs can tell the two apart.
    Returns the new id. Raises ValueError if the id already exists.
    """
    app_id = f"{fields['applied_date']}-{slugify(fields['company'])}-{slugify(fields['role'])}"
    folder = f"applications/{app_id}"
    with sqlite3.connect(DB_PATH) as con:
        if con.execute("SELECT 1 FROM applications WHERE id = ?", (app_id,)).fetchone():
            raise ValueError(f"'{app_id}' is already tracked.")
        con.execute(
            """INSERT INTO applications
               (id, company, role, role_type, link, location, applied_date, stage,
                portal_link, portal_email, portal_password, folder, cover_letter)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (app_id, fields["company"], fields["role"], fields.get("role_type") or None,
             fields.get("link") or "", fields.get("location") or "",
             str(fields["applied_date"]), fields.get("stage") or "applied",
             fields.get("portal_link") or "", fields.get("portal_email") or "",
             fields.get("portal_password") or "", folder,
             "yes" if (letter_pdf or fields.get("cover_letter") == "yes") else "no"),
        )
    path = ROOT / folder
    path.mkdir(parents=True, exist_ok=True)
    if resume_pdf:
        name = resume_name or f"Resume_{app_id}.pdf"
        (path / name.replace("CoverLetter", "Resume")).write_bytes(resume_pdf)
    if letter_pdf:
        name = letter_name or f"CoverLetter_{app_id}.pdf"
        if "CoverLetter" not in name:
            name = "CoverLetter_" + name
        (path / name).write_bytes(letter_pdf)
    return app_id
