"""Streamlit dashboard over applications/tracker.db.

Run from the repo root:  streamlit run dashboard/app.py

Pages: Applications (editable tracker table + resume / cover letter PDFs) and
Analytics (totals, applications over time, outcomes by stage). Only the DB is
ever written; the application folders are read-only.
"""

import importlib
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

import tracker  # noqa: E402

# Streamlit hot-reloads page files but keeps helper modules cached, so an edit
# to tracker.py would otherwise need a server restart. Reloading is cheap.
tracker = importlib.reload(tracker)
DB_PATH, ROOT = tracker.DB_PATH, tracker.ROOT

st.set_page_config(page_title="Job Application Tracker", page_icon="🗂️", layout="wide")

if not DB_PATH.exists():
    st.error(f"No tracker database at `{DB_PATH.relative_to(ROOT)}`. "
             "Run the resume-tailoring skill once to create it.")
    st.stop()

pages = [
    st.Page("views/applications.py", title="Applications", icon="🗂️", default=True),
    st.Page("views/analytics.py", title="Analytics", icon="📈"),
    st.Page("views/new_application.py", title="New application", icon="💬"),
]
st.navigation(pages).run()
