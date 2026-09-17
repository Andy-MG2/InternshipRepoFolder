"""Analytics page: totals, applications over time, outcomes by stage."""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from tracker import STAGE_COLORS, STAGE_ORDER, load_applications

SERIES_BLUE = "#2a78d6"
GRID = "#e6e5e1"
INK_SECONDARY = "#52514e"
PRESETS = {"Last 7 days": 7, "Last 30 days": 30, "Last 90 days": 90, "All time": None}


# --- charts ----------------------------------------------------------------

def _base_layout(fig: go.Figure, granularity: str, height: int = 340) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=8, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=INK_SECONDARY, size=12),
        hovermode="x unified",
        showlegend=False,
        dragmode="pan",
    )
    fig.update_xaxes(
        showgrid=False, showline=True, linecolor=GRID, zeroline=False,
        tickformat="%b %-d", dtick="D1" if granularity == "Day" else "D7",
        rangeslider=dict(visible=True, thickness=0.08, bgcolor="#f5f5f3"),
    )
    fig.update_yaxes(showgrid=True, gridcolor=GRID, showline=False, zeroline=False,
                     rangemode="tozero", fixedrange=True)
    return fig


def bucket_counts(df: pd.DataFrame, start: date, end: date, granularity: str) -> pd.Series:
    """Applications per day (or ISO week) across [start, end], zeros included."""
    dates = pd.to_datetime(df["applied_date"])
    freq = "D" if granularity == "Day" else "W-MON"
    idx = pd.date_range(pd.Timestamp(start), pd.Timestamp(end), freq="D")
    counts = pd.Series(1, index=dates).resample("D").sum().reindex(idx, fill_value=0)
    if freq != "D":
        counts = counts.resample(freq, label="left", closed="left").sum()
    return counts


def cumulative_chart(per_bucket: pd.Series, carried: int, granularity: str) -> go.Figure:
    total = per_bucket.cumsum() + carried
    fig = go.Figure(go.Scatter(
        x=total.index, y=total.values, mode="lines+markers",
        line=dict(color=SERIES_BLUE, width=2, shape="hv"),
        marker=dict(size=8, color=SERIES_BLUE, line=dict(color="#ffffff", width=2)),
        hovertemplate="%{y} total<extra></extra>",
    ))
    if total.max() < 12:
        fig.update_yaxes(dtick=1)
    return _base_layout(fig, granularity)


def per_bucket_chart(per_bucket: pd.Series, granularity: str) -> go.Figure:
    fig = go.Figure(go.Bar(
        x=per_bucket.index, y=per_bucket.values,
        marker=dict(color=SERIES_BLUE, line=dict(width=0)),
        hovertemplate="%{y} applied<extra></extra>",
    ))
    fig.update_layout(bargap=0.5)
    if per_bucket.max() < 12:
        fig.update_yaxes(dtick=1)
    return _base_layout(fig, granularity)


def stage_pie(df: pd.DataFrame) -> go.Figure:
    counts = df["stage"].value_counts()
    present = [s for s in STAGE_ORDER if counts.get(s, 0) > 0]
    fig = go.Figure(go.Pie(
        labels=[s.capitalize() for s in present],
        values=[int(counts[s]) for s in present],
        marker=dict(colors=[STAGE_COLORS[s] for s in present],
                    line=dict(color="#ffffff", width=2)),
        hole=0.55, sort=False, direction="clockwise",
        textinfo="label+value", textposition="inside",
        insidetextorientation="horizontal",
        textfont=dict(color="#ffffff", size=13),
        hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
    ))
    fig.update_layout(
        height=340, margin=dict(l=24, r=24, t=24, b=24),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=INK_SECONDARY, size=12),
        showlegend=True, legend=dict(orientation="v", x=1.02, y=0.5, yanchor="middle"),
        annotations=[dict(text=f"<b>{len(df)}</b><br>total", x=0.5, y=0.5,
                          showarrow=False, font=dict(size=16))],
    )
    return fig


# --- page ------------------------------------------------------------------

st.title("Analytics")

apps = load_applications()
if apps.empty:
    st.info("The tracker is empty. Run the resume-tailoring skill to add an application.")
    st.stop()

first_day = min(apps["applied_date"])
today = date.today()

# Filters ---------------------------------------------------------------------

preset = st.pills("Range", list(PRESETS), default="All time")
days = PRESETS.get(preset)
default_start = first_day if days is None else max(first_day, today - timedelta(days=days - 1))

f1, f2, f3 = st.columns([2, 3, 1], vertical_alignment="bottom")
picked = f1.date_input("Custom range", value=(default_start, today),
                       min_value=first_day, max_value=today, key=f"range-{preset}")
start, end = (picked if isinstance(picked, tuple) and len(picked) == 2
              else (default_start, today))
stages = f2.multiselect("Stages", STAGE_ORDER, default=STAGE_ORDER,
                        format_func=str.capitalize)
granularity = f3.segmented_control("Group by", ["Day", "Week"], default="Day")

by_stage = apps[apps["stage"].isin(stages)]
in_range = by_stage[(by_stage["applied_date"] >= start) & (by_stage["applied_date"] <= end)]
carried = int((by_stage["applied_date"] < start).sum())  # applications before the window

# Metrics ----------------------------------------------------------------------

total = len(in_range)
responded = int((in_range["stage"] != "applied").sum())
active = int(in_range["stage"].isin(["applied", "interviewing", "offer"]).sum())
offers = int(in_range["stage"].isin(["offer", "accepted"]).sum())

m1, m2, m3, m4 = st.columns(4)
m1.metric("Applications in range", total)
m2.metric("Response rate", f"{responded / total:.0%}" if total else "—",
          help="Applications no longer in the 'applied' stage")
m3.metric("Still active", active)
m4.metric("Offers", offers)

if in_range.empty and carried == 0:
    st.warning("No applications in this range.")
    st.stop()

# Time charts -----------------------------------------------------------------

per_bucket = bucket_counts(in_range, start, end, granularity)
unit = "day" if granularity == "Day" else "week"

c1, c2 = st.columns(2, gap="large")
with c1:
    st.markdown("**Total applications over time**")
    st.caption("Running total, including applications before the range.")
    st.plotly_chart(cumulative_chart(per_bucket, carried, granularity), width="stretch",
                    config={"displayModeBar": False, "scrollZoom": True})
with c2:
    st.markdown(f"**Applications per {unit}**")
    st.caption(f"Click a bar to list that {unit}'s applications. Drag the slider to zoom.")
    event = st.plotly_chart(per_bucket_chart(per_bucket, granularity), width="stretch",
                            config={"displayModeBar": False, "scrollZoom": True},
                            on_select="rerun", selection_mode="points", key="per-bucket")

points = event.selection.points if event and event.selection else []
if points:
    picked_days = [pd.Timestamp(p["x"]).date() for p in points]
    span = timedelta(days=1 if granularity == "Day" else 7)
    mask = pd.Series(False, index=in_range.index)
    for d in picked_days:
        mask |= (in_range["applied_date"] >= d) & (in_range["applied_date"] < d + span)
    picked_label = ", ".join(d.strftime("%b %-d") for d in picked_days)
    st.markdown(f"**Applications on {picked_label}** — {int(mask.sum())}")
    st.dataframe(
        in_range[mask][["company", "role", "stage", "applied_date", "location"]],
        hide_index=True, width="stretch",
        column_config={
            "company": "Company", "role": "Position", "stage": "Status",
            "applied_date": st.column_config.DateColumn("Applied", format="MMM D, YYYY"),
            "location": "Location",
        },
    )

# Outcomes ---------------------------------------------------------------------

st.divider()
c3, c4 = st.columns(2, gap="large")
with c3:
    st.markdown("**Outcomes by stage**")
    if in_range.empty:
        st.info("No applications in this range.")
    else:
        st.plotly_chart(stage_pie(in_range), width="stretch",
                        config={"displayModeBar": False})
with c4:
    st.markdown("**Stage breakdown**")
    breakdown = (
        in_range["stage"].value_counts().reindex(STAGE_ORDER, fill_value=0)
        .rename_axis("Stage").reset_index(name="Applications")
    )
    breakdown["Share"] = breakdown["Applications"] / total * 100 if total else 0
    st.dataframe(
        breakdown, hide_index=True, width="stretch",
        column_config={"Share": st.column_config.ProgressColumn(
            "Share", format="%.0f%%", min_value=0, max_value=100)},
    )
