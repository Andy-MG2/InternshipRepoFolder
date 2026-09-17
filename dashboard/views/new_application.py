"""New application page: a Claude Code chat with the project's skills loaded.

Paste a job description and ask for a resume and/or cover letter the same way
as in the terminal. Every tool call is auto-approved; the skills write the
application folder, render PDFs, and insert the tracker row themselves.
"""

from __future__ import annotations

import time

import streamlit as st

from agent import AgentSession, Turn, saved_state

EXAMPLES = {
    "Resume + cover letter": "Make the resume and cover letter for this job:\n\n",
    "Resume only": "/resume-tailoring resume only\n\n",
    "Cover letter only": "/coverletter-tailoring for this posting:\n\n",
}


@st.cache_resource(show_spinner=False)
def _holder() -> dict:
    """Process-wide slot for the live session, so reloads re-attach to it."""
    return {"agent": None}


def current() -> AgentSession | None:
    return _holder()["agent"]


def start(resume: str | None = None, history: list | None = None) -> AgentSession:
    stop()
    with st.spinner("Connecting to Claude Code…"):
        s = AgentSession(resume=resume, history=[Turn(**t) for t in history or []],
                         session_id=resume)
        s.start()
    _holder()["agent"] = s
    return s


def stop() -> None:
    if current():
        current().close()
        _holder()["agent"] = None


def render_turn(turn: Turn, live: bool = False) -> None:
    with st.chat_message(turn.role):
        if turn.tools:
            with st.expander(f"{len(turn.tools)} tool calls", expanded=live):
                st.markdown("\n".join(f"- `{t}`" for t in turn.tools))
        st.markdown(turn.content + (" ▌" if live else ""))
        if turn.error:
            st.error(turn.error)
        if turn.meta:
            st.caption(turn.meta)


st.title("New application")
st.caption("Paste a job description and ask for the resume and/or cover letter, exactly as in "
           "the terminal. Runs the project's skills with every command auto-approved.")

agent = current()
saved = saved_state()

top = st.columns([3, 1, 1], vertical_alignment="center")
starter = top[0].selectbox("Start with", list(EXAMPLES), label_visibility="collapsed")
if top[1].button("Stop", disabled=not (agent and agent.busy), width="stretch"):
    agent.interrupt()
if top[2].button("New chat", width="stretch"):
    start()
    st.rerun()

if agent is None:
    if saved and saved.get("session_id"):
        n = len(saved.get("history", []))
        st.info(f"A previous conversation ({n} messages) can be resumed — Claude keeps its own "
                "transcript, so it picks up with full context.")
        c1, c2 = st.columns(2)
        if c1.button("Resume last chat", type="primary", width="stretch"):
            start(saved["session_id"], saved.get("history"))
            st.rerun()
        if c2.button("Start fresh", width="stretch"):
            start()
            st.rerun()
        st.stop()
    agent = start()

for turn in agent.history:
    render_turn(turn)

if agent.busy and agent.live is not None:
    # A turn is streaming (possibly started before a page reload): show it and poll.
    slot = st.empty()
    while agent.busy:
        with slot.container():
            render_turn(agent.live, live=True)
        time.sleep(0.3)
    st.rerun()

if not agent.history:
    st.info(f"Tip: choose a starter above, then paste the posting. It pre-fills "
            f"“{EXAMPLES[starter].strip()}”.")

prompt = st.chat_input("Paste the job description and say what you want…")
if prompt:
    if not agent.history and not prompt.lstrip().startswith("/"):
        prompt = EXAMPLES[starter] + prompt
    agent.send(prompt)
    st.rerun()
