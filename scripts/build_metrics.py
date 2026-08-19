#!/usr/bin/env python3
"""Generate sanitized documentation content and charts from uploaded arb data.

Supported inputs under data/uploads/:
- individual arb_execution_stats_*.csv / arb_opportunity_stats_*.csv / arb_near_miss_stats_*.csv
- ZIP exports containing those CSVs

The script runs inside GitHub Actions before Docusaurus builds.
"""
from __future__ import annotations

from csv import DictReader
from datetime import datetime
from io import StringIO, TextIOWrapper
from pathlib import Path
from zipfile import ZipFile, BadZipFile
import json
import math

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "data" / "sanitized" / "live_executions.csv"
UPLOAD_DIR = ROOT / "data" / "uploads"
LIVE_DOC = ROOT / "docs" / "live-executions.md"
SUMMARY_JSON = ROOT / "static" / "data" / "generated_metrics.json"
IMG_DIR = ROOT / "static" / "img"


def classify_name(name: str):
    base = Path(name).name
    if base.startswith("arb_execution_stats_"):
        return "execution"
    if base.startswith("arb_opportunity_stats_"):
        return "opportunity"
    if base.startswith("arb_near_miss_stats_"):
        return "near_miss"
    return None


def read_uploaded_frames():
    families = {"execution": [], "opportunity": [], "near_miss": []}
    if not UPLOAD_DIR.exists():
        return families

    for path in sorted(UPLOAD_DIR.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix.lower() == ".csv":
            kind = classify_name(path.name)
            if not kind:
                continue
            try:
                df = pd.read_csv(path)
                df["_source_upload"] = path.name
                families[kind].append(df)
            except Exception as exc:
                print(f"Skipping {path}: {exc}")
        elif path.suffix.lower() == ".zip":
            try:
                with ZipFile(path) as zf:
                    for member in zf.namelist():
                        kind = classify_name(member)
                        if not kind or not member.lower().endswith(".csv"):
                            continue
                        try:
                            with zf.open(member) as fh:
                                df = pd.read_csv(fh)
                            df["_source_upload"] = f"{path.name}:{Path(member).name}"
                            families[kind].append(df)
                        except Exception as exc:
                            print(f"Skipping {path.name}:{member}: {exc}")
            except BadZipFile as exc:
                print(f"Skipping bad ZIP {path}: {exc}")

    return families


def concat(frames):
    return pd.concat(frames, ignore_index=True, sort=False) if frames else pd.DataFrame()


def clean_direction(value: str) -> str:
    value = str(value or "").strip()
    return {
        "Buy YES @ Kalshi + Buy NO @ PM": "Kalshi YES + PM NO",
        "Buy YES @ PM + Buy NO @ Kalshi": "PM YES + Kalshi NO",
    }.get(value, value)


def parse_date(value: str) -> str:
    value = str(value or "").strip()
    if not value:
        return ""
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except Exception:
        return value[:10]


def fmt_qty(value) -> str:
    try:
        n = float(value)
        return str(int(n)) if n.is_integer() else f"{n:g}"
    except Exception:
        return str(value or "").strip() or "?"


def fmt_edge_cents(value) -> str:
    try:
        return f"+{float(value) * 100:.2f}¢"
    except Exception:
        return "—"


def baseline_completed_rows():
    if not BASELINE.exists():
        return []
    df = pd.read_csv(BASELINE)
    rows = []
    for _, r in df.iterrows():
        rows.append({
            "date": str(r.get("date", "")),
            "market": str(r.get("market", "")),
            "direction": str(r.get("direction", "")),
            "pm_filled_qty": r.get("pm_filled_qty", ""),
            "kalshi_filled_qty": r.get("kalshi_filled_qty", ""),
            "status": "both_filled" if str(r.get("outcome", "")) == "completed" else str(r.get("outcome", "")),
            "edge": r.get("conservative_realized_edge", ""),
            "started_at_utc": str(r.get("date", "")),
        })
    return rows


def execution_completed_rows(execution: pd.DataFrame):
    if execution.empty or "status" not in execution.columns:
        return []
    rows = []
    subset = execution[execution["status"].astype(str).eq("both_filled")].copy()
    for _, r in subset.iterrows():
        rows.append({
            "date": parse_date(r.get("started_at_utc", "")),
            "market": str(r.get("matchup_label", "")).strip(),
            "direction": clean_direction(r.get("direction", "")),
            "pm_filled_qty": r.get("pm_filled_qty", ""),
            "kalshi_filled_qty": r.get("kalshi_filled_qty", ""),
            "status": "both_filled",
            "edge": r.get("conservative_realized_edge", ""),
            "started_at_utc": str(r.get("started_at_utc", "")).strip(),
        })
    return rows


def dedupe_completed(rows):
    seen = set()
    out = []
    for r in sorted(rows, key=lambda x: (x.get("started_at_utc", ""), x.get("market", ""))):
        key = (
            r.get("date", ""), r.get("market", ""), r.get("direction", ""),
            fmt_qty(r.get("pm_filled_qty", "")), fmt_qty(r.get("kalshi_filled_qty", "")),
            fmt_edge_cents(r.get("edge", "")),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def build_live_doc(completed, execution):
    lines = [
        "---", "title: Live Executions", "sidebar_position: 8", "---",
        "# Live execution ledger", "",
        "This page is generated automatically from the sanitized baseline plus execution CSVs contained in files uploaded to `data/uploads/`.", "",
        "## PM-first era", "",
        "| Outcome | Date | Market | Direction | Quantity | Conservative realized edge |",
        "|---|---|---|---|---:|---:|",
    ]
    for r in completed:
        qty = f"{fmt_qty(r.get('pm_filled_qty'))} + {fmt_qty(r.get('kalshi_filled_qty'))}"
        lines.append(f"| ✅ Completed | {r.get('date','')} | {r.get('market','')} | {r.get('direction','')} | {qty} | {fmt_edge_cents(r.get('edge'))} |")

    counts = {}
    if not execution.empty and "status" in execution.columns:
        counts = execution["status"].fillna("missing").astype(str).value_counts().to_dict()

    lines += ["", f"**Confirmed PM-first completions shown:** {len(completed)}", "", "## Uploaded execution classifications", ""]
    if counts:
        lines += ["| Status | Rows |", "|---|---:|"]
        for status, count in sorted(counts.items()):
            lines.append(f"| `{status}` | {int(count)} |")
    else:
        lines.append("No uploaded execution rows are available yet.")

    lines += [
        "", "## Safe aborts", "",
        "Under PM-first execution, a verified PM zero fill causes the Kalshi order to remain unsent. `pm_no_fill_kalshi_not_sent` rows are safe aborts, not failed arbitrages.",
        "", "## Historical failures", "",
        "Before PM-first execution, three live mismatches were observed with the high-level pattern `PM filled 0 / Kalshi filled 1`. Those incidents drove stronger verification, exchange-timestamp freshness, mismatch recovery, PM-first execution and post-preparation revalidation.",
        "", "![Execution outcomes](/img/live_execution_outcomes.png)", "",
    ]
    LIVE_DOC.write_text("\n".join(lines), encoding="utf-8")


def save_execution_outcomes(execution: pd.DataFrame, completed_count: int):
    safe = int((execution.get("status", pd.Series(dtype=str)).astype(str) == "pm_no_fill_kalshi_not_sent").sum()) if not execution.empty else 0
    mismatch = int(execution.get("status", pd.Series(dtype=str)).astype(str).isin(["mismatch", "mismatch_recovery_failed", "mismatch_recovered"]).sum()) if not execution.empty else 0
    labels = ["Safe PM aborts", "Completed arbs", "Mismatches"]
    values = [safe, completed_count, mismatch]
    fig = plt.figure(figsize=(8.5, 5.0))
    ax = fig.add_subplot(111)
    bars = ax.bar(labels, values)
    ax.set_ylabel("Count")
    ax.set_title("Live Execution Outcomes")
    ax.grid(True, axis="y", alpha=0.25)
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width()/2, v, str(v), ha="center", va="bottom")
    fig.tight_layout()
    fig.savefig(IMG_DIR / "live_execution_outcomes.png", dpi=180)
    plt.close(fig)


def save_pm_latency(execution: pd.DataFrame):
    needed = {"detected_to_pm_send_call_ms", "status"}
    if execution.empty or not needed.issubset(execution.columns):
        return
    df = execution.copy()
    df["lat"] = pd.to_numeric(df["detected_to_pm_send_call_ms"], errors="coerce")
    df = df[df["lat"].notna() & df["status"].astype(str).isin(["both_filled", "mismatch", "mismatch_recovery_failed", "mismatch_recovered"])]
    if df.empty:
        return
    if "started_at_utc" in df:
        df = df.sort_values("started_at_utc")
    df = df.tail(20)
    labels = []
    for i, (_, r) in enumerate(df.iterrows(), 1):
        status = "success" if str(r.get("status")) == "both_filled" else "mismatch"
        labels.append(f"{status} {i}")
    fig = plt.figure(figsize=(9.5, 5.0))
    ax = fig.add_subplot(111)
    bars = ax.bar(range(len(df)), df["lat"].tolist())
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_ylabel("Detection → PM HTTP send (ms)")
    ax.set_title("PM Critical-Path Latency")
    ax.grid(True, axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(IMG_DIR / "pm_send_latency.png", dpi=180)
    plt.close(fig)


def dedupe_opportunity_episodes(opportunity: pd.DataFrame):
    required = {"detected_at_utc", "matchup_label", "direction", "t0_pm_depth_at_initial_limit", "t0_kalshi_depth_at_initial_limit"}
    if opportunity.empty or not required.issubset(opportunity.columns):
        return pd.DataFrame()
    df = opportunity.copy()
    df["dt"] = pd.to_datetime(df["detected_at_utc"], errors="coerce", utc=True)
    df["pm_depth"] = pd.to_numeric(df["t0_pm_depth_at_initial_limit"], errors="coerce")
    df["kal_depth"] = pd.to_numeric(df["t0_kalshi_depth_at_initial_limit"], errors="coerce")
    df["bottleneck_depth"] = df[["pm_depth", "kal_depth"]].min(axis=1)
    df = df[df["bottleneck_depth"].notna()].sort_values(["matchup_label", "direction", "dt"])
    if df.empty:
        return df
    episode = 0
    last = {}
    ids = []
    for _, r in df.iterrows():
        key = (str(r.get("matchup_label")), str(r.get("direction")))
        t = r.get("dt")
        prev = last.get(key)
        if prev is None or pd.isna(t) or pd.isna(prev) or (t - prev).total_seconds() > 5:
            episode += 1
        ids.append(episode)
        last[key] = t
    df["episode"] = ids
    return df.groupby("episode", as_index=False).first()


def save_depth_availability(opportunity: pd.DataFrame):
    episodes = dedupe_opportunity_episodes(opportunity)
    if episodes.empty:
        return
    thresholds = [1, 2, 5, 10, 20, 50]
    pct = [float((episodes["bottleneck_depth"] >= n).mean() * 100) for n in thresholds]
    fig = plt.figure(figsize=(8.8, 5.0))
    ax = fig.add_subplot(111)
    bars = ax.bar([str(x) for x in thresholds], pct)
    ax.set_xlabel("Contracts available on both venues within profitable limits")
    ax.set_ylabel("Opportunity episodes meeting threshold (%)")
    ax.set_title("Executable Depth Availability")
    ax.set_ylim(0, 100)
    ax.grid(True, axis="y", alpha=0.25)
    for b, v in zip(bars, pct):
        ax.text(b.get_x() + b.get_width()/2, v, f"{v:.0f}%", ha="center", va="bottom")
    fig.tight_layout()
    fig.savefig(IMG_DIR / "depth_availability.png", dpi=180)
    plt.close(fig)


def boolish(series):
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin(["true", "1", "1.0", "yes"])


def save_durability_survival(opportunity: pd.DataFrame):
    if opportunity.empty or "durability_score" not in opportunity.columns:
        return
    times = [0, 25, 50, 100, 250, 500, 1000]
    valid_times = [t for t in times if f"t{t}_both_initial_limits_fillable" in opportunity.columns and f"t{t}_modeled_edge_now" in opportunity.columns]
    if len(valid_times) < 2:
        return
    df = opportunity.copy()
    df["durability_score_num"] = pd.to_numeric(df["durability_score"], errors="coerce")
    if "opportunity_id" in df.columns:
        df = df.drop_duplicates(subset=["opportunity_id"])
    if df.empty:
        return

    groups = [
        ("All opportunities", df),
        ("Score ≥ 3", df[df["durability_score_num"] >= 3]),
        ("Score ≤ 2", df[df["durability_score_num"] <= 2]),
    ]
    fig = plt.figure(figsize=(8.8, 5.0))
    ax = fig.add_subplot(111)
    plotted = False
    for label, g in groups:
        if g.empty:
            continue
        vals = []
        for t in valid_times:
            fill = boolish(g[f"t{t}_both_initial_limits_fillable"].fillna(False))
            edge = pd.to_numeric(g[f"t{t}_modeled_edge_now"], errors="coerce")
            vals.append(float((fill & (edge >= 0.01)).mean() * 100))
        ax.plot(valid_times, vals, marker="o", label=label)
        plotted = True
    if not plotted:
        plt.close(fig)
        return
    ax.set_xlabel("Milliseconds after detection")
    ax.set_ylabel("Opportunity still executable (%)")
    ax.set_title("Durability: Opportunity Survival")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(IMG_DIR / "durability_survival_curve.png", dpi=180)
    plt.close(fig)


def main():
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    families = read_uploaded_frames()
    execution = concat(families["execution"])
    opportunity = concat(families["opportunity"])
    near_miss = concat(families["near_miss"])

    completed = dedupe_completed(baseline_completed_rows() + execution_completed_rows(execution))
    build_live_doc(completed, execution)

    save_execution_outcomes(execution, len(completed))
    save_pm_latency(execution)
    save_depth_availability(opportunity)
    save_durability_survival(opportunity)

    status_counts = {}
    if not execution.empty and "status" in execution.columns:
        status_counts = {str(k): int(v) for k, v in execution["status"].fillna("missing").astype(str).value_counts().to_dict().items()}

    episodes = dedupe_opportunity_episodes(opportunity)
    summary = {
        "confirmed_pm_first_completions": len(completed),
        "uploaded_execution_rows": int(len(execution)),
        "uploaded_opportunity_rows": int(len(opportunity)),
        "uploaded_near_miss_rows": int(len(near_miss)),
        "deduplicated_opportunity_episodes": int(len(episodes)),
        "uploaded_execution_status_counts": status_counts,
    }
    SUMMARY_JSON.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"Execution rows: {len(execution)}")
    print(f"Opportunity rows: {len(opportunity)}")
    print(f"Near-miss rows: {len(near_miss)}")
    print(f"Completed arbs shown: {len(completed)}")
    print("Generated live ledger and available dashboard charts")


if __name__ == "__main__":
    main()
