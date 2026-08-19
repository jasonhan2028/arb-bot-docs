#!/usr/bin/env python3
"""Generate public, sanitized site content from uploaded arb execution CSVs.

Drop raw execution CSVs into data/uploads/ and push them to main. The GitHub
Pages workflow runs this script before the Docusaurus build.
"""
from __future__ import annotations

from csv import DictReader
from datetime import datetime
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "data" / "sanitized" / "live_executions.csv"
UPLOAD_DIR = ROOT / "data" / "uploads"
LIVE_DOC = ROOT / "docs" / "live-executions.md"
SUMMARY_JSON = ROOT / "static" / "data" / "generated_metrics.json"


def read_rows(path: Path):
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            return list(DictReader(f))
    except Exception as exc:
        print(f"Skipping {path}: {exc}")
        return []


def clean_direction(value: str) -> str:
    value = (value or "").strip()
    replacements = {
        "Buy YES @ Kalshi + Buy NO @ PM": "Kalshi YES + PM NO",
        "Buy YES @ PM + Buy NO @ Kalshi": "PM YES + Kalshi NO",
    }
    return replacements.get(value, value)


def parse_date(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except Exception:
        return value[:10]


def fmt_qty(value: str) -> str:
    try:
        n = float(value)
        return str(int(n)) if n.is_integer() else f"{n:g}"
    except Exception:
        return (value or "").strip() or "?"


def fmt_edge_cents(value: str) -> str:
    try:
        return f"+{float(value) * 100:.2f}¢"
    except Exception:
        return "—"


def load_baseline():
    out = []
    for r in read_rows(BASELINE):
        out.append({
            "date": r.get("date", ""),
            "market": r.get("market", ""),
            "direction": r.get("direction", ""),
            "pm_filled_qty": r.get("pm_filled_qty", ""),
            "kalshi_filled_qty": r.get("kalshi_filled_qty", ""),
            "status": "both_filled" if r.get("outcome") == "completed" else r.get("outcome", ""),
            "edge": r.get("conservative_realized_edge", ""),
            "started_at_utc": r.get("date", ""),
        })
    return out


def load_uploaded_execution_rows():
    rows = []
    if not UPLOAD_DIR.exists():
        return rows
    for path in sorted(UPLOAD_DIR.rglob("*.csv")):
        for r in read_rows(path):
            # Only treat files/rows that look like execution-stat records as executions.
            if "status" not in r or "matchup_label" not in r:
                continue
            rows.append({
                "date": parse_date(r.get("started_at_utc", "")),
                "market": (r.get("matchup_label") or "").strip(),
                "direction": clean_direction(r.get("direction", "")),
                "pm_filled_qty": r.get("pm_filled_qty", ""),
                "kalshi_filled_qty": r.get("kalshi_filled_qty", ""),
                "status": (r.get("status") or "").strip(),
                "edge": r.get("conservative_realized_edge", ""),
                "started_at_utc": (r.get("started_at_utc") or "").strip(),
            })
    return rows


def dedupe_completed(rows):
    completed = [r for r in rows if r.get("status") == "both_filled"]
    seen = set()
    out = []
    for r in sorted(completed, key=lambda x: (x.get("started_at_utc", ""), x.get("market", ""))):
        key = (
            r.get("date", ""),
            r.get("market", ""),
            r.get("direction", ""),
            fmt_qty(r.get("pm_filled_qty", "")),
            fmt_qty(r.get("kalshi_filled_qty", "")),
            fmt_edge_cents(r.get("edge", "")),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def build_live_doc(completed, uploaded_rows):
    lines = [
        "---",
        "title: Live Executions",
        "sidebar_position: 8",
        "---",
        "# Live execution ledger",
        "",
        "This page is generated automatically from the sanitized baseline plus CSV files uploaded to `data/uploads/`.",
        "",
        "## PM-first era",
        "",
        "| Outcome | Date | Market | Direction | Quantity | Conservative realized edge |",
        "|---|---|---|---|---:|---:|",
    ]
    for r in completed:
        qty = f"{fmt_qty(r.get('pm_filled_qty', ''))} + {fmt_qty(r.get('kalshi_filled_qty', ''))}"
        lines.append(
            f"| ✅ Completed | {r.get('date','')} | {r.get('market','')} | {r.get('direction','')} | {qty} | {fmt_edge_cents(r.get('edge',''))} |"
        )

    uploaded_counts = {}
    for r in uploaded_rows:
        status = r.get("status") or "missing"
        uploaded_counts[status] = uploaded_counts.get(status, 0) + 1

    lines += [
        "",
        f"**Confirmed PM-first completions shown:** {len(completed)}",
        "",
        "## Uploaded execution classifications",
        "",
    ]
    if uploaded_counts:
        lines += ["| Status | Rows |", "|---|---:|"]
        for status, count in sorted(uploaded_counts.items()):
            lines.append(f"| `{status}` | {count} |")
    else:
        lines.append("No raw execution CSVs have been uploaded yet.")

    lines += [
        "",
        "## Safe aborts",
        "",
        "Under PM-first execution, a verified PM zero fill causes the Kalshi order to remain unsent. These are logged as `pm_no_fill_kalshi_not_sent` and are not counted as failed arbitrages because the second venue was never exposed.",
        "",
        "## Historical failures",
        "",
        "Before PM-first execution, three live mismatches were observed with the high-level pattern `PM filled 0 / Kalshi filled 1`. Those failures drove PM order verification, exchange-timestamp freshness, automatic recovery, PM-first execution and post-preparation revalidation.",
        "",
        "![Execution outcomes](/img/live_execution_outcomes.png)",
        "",
    ]
    LIVE_DOC.write_text("\n".join(lines), encoding="utf-8")


def main():
    baseline = load_baseline()
    uploaded = load_uploaded_execution_rows()
    completed = dedupe_completed(baseline + uploaded)

    build_live_doc(completed, uploaded)

    status_counts = {}
    for r in uploaded:
        status = r.get("status") or "missing"
        status_counts[status] = status_counts.get(status, 0) + 1

    summary = {
        "confirmed_pm_first_completions": len(completed),
        "uploaded_execution_rows": len(uploaded),
        "uploaded_execution_status_counts": status_counts,
    }
    SUMMARY_JSON.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"Generated {LIVE_DOC.relative_to(ROOT)} with {len(completed)} completed arbs")
    print(f"Generated {SUMMARY_JSON.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
