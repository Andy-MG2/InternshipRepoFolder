"""Claude Code session for the New application page.

Runs the Claude Agent SDK (Claude Code as a library) against the repo root so
the project's skills are available, with every tool call auto-approved.

The SDK client is async and owns a subprocess, so it lives on a background
event loop. The session object is held process-wide (see views), not in the
browser's session state: a page reload re-attaches to it and, if a turn is in
flight, keeps showing it. After each turn the session id and transcript are
saved to disk so a later Streamlit restart can resume the same conversation.
"""

from __future__ import annotations

import asyncio
import json
import threading
from dataclasses import dataclass, field
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage, ClaudeAgentOptions, ClaudeSDKClient, ResultMessage,
    StreamEvent, SystemMessage, TextBlock, ToolUseBlock,
)

from tracker import ROOT

STATE_FILE = ROOT / "applications" / ".chat" / "last.json"


def _describe_tool(block: ToolUseBlock) -> str:
    inp = block.input or {}
    if block.name == "Bash":
        return f"Bash — {str(inp.get('description') or inp.get('command', ''))[:120]}"
    if block.name in ("Read", "Write", "Edit"):
        path = str(inp.get("file_path", ""))
        return f"{block.name} — {path.replace(str(ROOT) + '/', '')}"
    if block.name == "Skill":
        return f"Skill — /{inp.get('skill', '')} {inp.get('args', '')}".strip()
    if block.name in ("WebSearch", "WebFetch"):
        return f"{block.name} — {inp.get('query') or inp.get('url', '')}"
    return block.name


def saved_state() -> dict | None:
    """The last conversation's id and transcript, if one was saved."""
    try:
        return json.loads(STATE_FILE.read_text())
    except (OSError, ValueError):
        return None


@dataclass
class Turn:
    role: str
    content: str = ""
    tools: list[str] = field(default_factory=list)
    meta: str = ""
    error: str = ""


@dataclass
class AgentSession:
    """One Claude Code conversation. Lives for the Streamlit process."""

    resume: str | None = None
    history: list[Turn] = field(default_factory=list)
    session_id: str | None = None
    busy: bool = False
    live: Turn | None = None            # the assistant turn currently streaming
    loop: asyncio.AbstractEventLoop = field(default_factory=asyncio.new_event_loop)
    client: ClaudeSDKClient | None = None

    def start(self) -> None:
        threading.Thread(target=self.loop.run_forever, daemon=True).start()
        asyncio.run_coroutine_threadsafe(self._connect(), self.loop).result()

    async def _connect(self) -> None:
        self.client = ClaudeSDKClient(options=ClaudeAgentOptions(
            cwd=str(ROOT),
            setting_sources=["user", "project"],
            permission_mode="bypassPermissions",  # the user asked for auto-approve
            include_partial_messages=True,        # token-level streaming
            resume=self.resume,
        ))
        await self.client.connect()

    def send(self, text: str) -> None:
        """Start a turn; the page polls `live` / `busy` to render it."""
        self.history.append(Turn("user", text))
        self.live = Turn("assistant")
        self.busy = True
        asyncio.run_coroutine_threadsafe(self._turn(text), self.loop)

    async def _turn(self, text: str) -> None:
        turn = self.live
        try:
            await self.client.query(text)
            streamed = False
            async for msg in self.client.receive_response():
                if isinstance(msg, StreamEvent):
                    ev = msg.event
                    if (ev.get("type") == "content_block_delta"
                            and ev["delta"].get("type") == "text_delta"
                            and msg.parent_tool_use_id is None):
                        turn.content += ev["delta"]["text"]; streamed = True
                elif isinstance(msg, AssistantMessage) and msg.parent_tool_use_id is None:
                    for block in msg.content:
                        if isinstance(block, ToolUseBlock):
                            turn.tools.append(_describe_tool(block))
                            if turn.content and not turn.content.endswith("\n\n"):
                                turn.content += "\n\n"  # text after a tool is a new paragraph
                        elif isinstance(block, TextBlock) and not streamed:
                            turn.content += block.text
                    streamed = False
                elif isinstance(msg, SystemMessage) and msg.subtype == "init":
                    self.session_id = msg.data.get("session_id", self.session_id)
                elif isinstance(msg, ResultMessage):
                    self.session_id = msg.session_id
                    if msg.is_error and msg.result:
                        turn.error = msg.result
                    parts = [f"${msg.total_cost_usd:.2f}" if msg.total_cost_usd is not None else "",
                             f"{msg.num_turns} turns", f"{msg.duration_ms / 1000:.0f}s"]
                    turn.meta = " · ".join(p for p in parts if p)
        except Exception as e:  # surface instead of hanging the page
            turn.error = f"{type(e).__name__}: {e}"
        finally:
            self.history.append(turn)
            self.live = None
            self.busy = False
            self._save()

    def _save(self) -> None:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps({
            "session_id": self.session_id,
            "history": [t.__dict__ for t in self.history],
        }, indent=1))

    def interrupt(self) -> None:
        if self.client:
            asyncio.run_coroutine_threadsafe(self.client.interrupt(), self.loop)

    def close(self) -> None:
        if self.client:
            try:
                asyncio.run_coroutine_threadsafe(self.client.disconnect(), self.loop).result(timeout=10)
            except Exception:
                pass
        self.loop.call_soon_threadsafe(self.loop.stop)
