"""Applications page: tracker table, documents below it.

Click a row (view mode) or type in the Documents search to pick an application.
Edit mode swaps the table for an editor with a Save button.
"""

from __future__ import annotations

import base64
import re
from pathlib import Path

import streamlit as st

from tracker import (
    ROLE_TYPES, ROOT, STAGE_ORDER, find_pdfs, load_applications, save_changes, search,
)

PDF_HEIGHT = 800
COLUMN_ORDER = [
    "company", "role", "stage", "applied_date", "role_type", "location",
    "link", "portal_link", "portal_email", "portal_password", "cover_letter",
]
COLUMN_CONFIG = {
    "company": st.column_config.TextColumn("Company"),
    "role": st.column_config.TextColumn("Position", width="medium"),
    "stage": st.column_config.SelectboxColumn("Status", options=STAGE_ORDER, required=True),
    "applied_date": st.column_config.DateColumn("Applied", format="MMM D, YYYY"),
    "role_type": st.column_config.SelectboxColumn("Type", options=ROLE_TYPES),
    "location": st.column_config.TextColumn("Location", width="medium"),
    "link": st.column_config.LinkColumn("Posting", display_text="open"),
    "portal_link": st.column_config.LinkColumn("Portal", display_text="status"),
    "portal_email": st.column_config.TextColumn("Portal email"),
    "portal_password": st.column_config.TextColumn("Portal password"),
    "cover_letter": st.column_config.SelectboxColumn("Cover letter", options=["yes", "no"]),
}


def show_pdf(path: Path | None, label: str, key: str) -> None:
    if path is None:
        st.info(f"No {label.lower()} PDF in this folder.")
        return
    data = path.read_bytes()
    docx = path.with_suffix(".docx")
    pdf_col, docx_col = st.columns(2)
    pdf_col.download_button("Download PDF", data, file_name=path.name,
                            mime="application/pdf", key=f"dl-{key}-pdf", width="stretch")
    docx_col.download_button(
        "Download Word", docx.read_bytes() if docx.is_file() else b"", file_name=docx.name,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        key=f"dl-{key}-docx", width="stretch", disabled=not docx.is_file(),
        help=None if docx.is_file() else "No .docx in this folder",
    )
    try:
        st.pdf(data, height=PDF_HEIGHT, key=f"pdf-{key}")
    except Exception:  # older Streamlit or streamlit[pdf] missing: inline the bytes
        b64 = base64.b64encode(data).decode()
        st.markdown(
            f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="{PDF_HEIGHT}" '
            'style="border:1px solid #e6e5e1;border-radius:6px"></iframe>',
            unsafe_allow_html=True,
        )


def read_markdown(folder: str, name: str) -> str | None:
    path = ROOT / folder / name
    if not path.is_file():
        return None
    text = path.read_text()
    # Demote headings two levels so the file sits under the page's own hierarchy.
    return re.sub(r"^(#{1,4}) ", lambda m: "#" * min(m.end(1) + 2, 6) + " ", text, flags=re.M)


def _clear_row_selection() -> None:
    """Typing in the Documents search overrides whatever row was clicked."""
    st.session_state["doc-selected"] = None


@st.fragment
def documents(apps) -> None:
    """Resume, cover letter, change log, and posting for one application.

    The application comes from the search box if it has text, else from the
    row clicked in the table, else the top-ranked row. A fragment so typing
    here re-renders only this section; PDF viewer keys are fixed so they update
    in place instead of remounting.
    """
    st.subheader("Documents")
    query = st.text_input("Find application", placeholder="company or role…",
                          label_visibility="collapsed", key="doc-search",
                          on_change=_clear_row_selection)
    selected = st.session_state.get("doc-selected")
    if query.strip():
        matches = search(apps, query)
        if matches.empty:
            st.warning("No application matches that search.")
            return
        chosen = matches.iloc[0]
        others = [f"{r.company} — {r.role}" for r in matches.iloc[1:].itertuples()]
    elif selected is not None and (apps["id"] == selected).any():
        chosen = apps[apps["id"] == selected].iloc[0]
        others = []
    else:
        chosen, others = apps.iloc[0], []

    st.markdown(f"**{chosen.company} — {chosen.role}**")
    if others:
        st.caption("Also matches: " + "; ".join(others) + ". Refine the search to switch.")
    else:
        st.caption("Click a row in the table above or search to switch application.")

    resume_pdf, letter_pdf = find_pdfs(chosen.folder)
    resume_col, letter_col = st.columns(2, gap="large")
    with resume_col:
        st.markdown("Resume")
        show_pdf(resume_pdf, "Resume", "resume")
    with letter_col:
        st.markdown("Cover letter")
        show_pdf(letter_pdf, "Cover letter", "letter")

    changes_tab, jd_tab = st.tabs(["What was modified", "Job description"])
    with changes_tab:
        changes = read_markdown(chosen.folder, "tailoring-changes.md")
        if changes is None:
            st.info("No tailoring-changes.md in this folder.")
        else:
            with st.container(border=True):
                st.markdown(changes)
    with jd_tab:
        jd = read_markdown(chosen.folder, "job-description.md")
        if jd is None:
            st.info("No job-description.md in this folder.")
        else:
            with st.container(border=True):
                st.markdown(jd)


st.title("Applications")

apps = load_applications()
if apps.empty:
    st.info("The tracker is empty. Turn on Edit mode to add a row, or run the resume-tailoring skill.")
    st.stop()

# Search + table ------------------------------------------------------------

search_col, edit_col, secrets_col = st.columns([3, 1, 1], vertical_alignment="bottom")
query = search_col.text_input("Search", placeholder="company, role, stage, location…",
                              label_visibility="collapsed")
editing = edit_col.toggle("Edit mode", value=False)
show_secrets = secrets_col.toggle("Show portal credentials", value=False)

visible = search(apps, query)
st.caption(f"{len(visible)} of {len(apps)} applications"
           + (f" matching “{query}”" if query else "")
           + ("" if editing else " — click a row to open its documents"))

if visible.empty:
    st.warning("No applications match that search.")
    st.stop()

hidden = [] if show_secrets else ["portal_email", "portal_password"]
column_order = [c for c in COLUMN_ORDER if c not in hidden]
height = min(640, 40 + 36 * len(visible))

if editing:
    st.caption("Type into the empty bottom row to add an application. Select rows and press "
               "Delete (or the trash icon) to remove them. Nothing is written until you save.")
    edited = st.data_editor(
        visible, hide_index=True, num_rows="dynamic", width="stretch", height=height + 36,
        column_order=column_order, column_config=COLUMN_CONFIG,
        disabled=["id", "folder"], key="tracker-editor",
    )
    pending_deletes = visible[~visible["id"].isin(edited["id"].dropna())]
    if not pending_deletes.empty:
        st.warning("Will remove from the tracker: "
                   + "; ".join(f"{r.company} — {r.role}" for r in pending_deletes.itertuples())
                   + ". The application folders and PDFs stay on disk.")
    if st.button("Save changes", type="primary"):
        result = save_changes(visible, edited)
        parts = [f"{result[k]} {k}" for k in ("updated", "added", "deleted") if result[k]]
        for msg in result["skipped"]:
            st.error(f"Not added: {msg}")
        if parts:
            st.success(", ".join(parts) + ".")
            st.rerun()
        elif not result["skipped"]:
            st.info("Nothing changed.")
else:
    event = st.dataframe(
        visible, hide_index=True, width="stretch", height=height,
        column_order=column_order, column_config=COLUMN_CONFIG,
        on_select="rerun", selection_mode=["single-row", "single-cell"], key="tracker-table",
    )
    # Either a row checkbox or any cell in the row selects that application.
    sel = event.selection if event else None
    rows = list(sel.rows) if sel else []
    if not rows and sel and sel.cells:
        rows = [sel.cells[0][0]]
    clicked = visible.iloc[rows[0]]["id"] if rows else None
    # Only react to a *new* click, so a persisting selection doesn't keep
    # wiping out a search the user typed afterwards.
    if clicked is not None and clicked != st.session_state.get("_last_clicked"):
        st.session_state["_last_clicked"] = clicked
        st.session_state["doc-selected"] = clicked
        st.session_state["doc-search"] = ""

# Documents -----------------------------------------------------------------

st.divider()
documents(apps)
