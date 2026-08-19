#!/usr/bin/env python3
from pathlib import Path
import json
import sys
import pandas as pd

def read_family(folder: Path, prefix: str) -> pd.DataFrame:
    frames = []
    for path in folder.glob(f"{prefix}*.csv"):
        try:
            frames.append(pd.read_csv(path))
        except Exception as exc:
            print(f"Skipping {path.name}: {exc}")
    return pd.concat(frames, ignore_index=True, sort=False) if frames else pd.DataFrame()

def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: build_metrics.py <csv-directory>")
    src = Path(sys.argv[1])
    execution = read_family(src, "arb_execution_stats_")
    opportunity = read_family(src, "arb_opportunity_stats_")
    near_miss = read_family(src, "arb_near_miss_stats_")

    summary = {
        "execution_rows": int(len(execution)),
        "opportunity_rows": int(len(opportunity)),
        "near_miss_rows": int(len(near_miss)),
    }
    if not execution.empty and "status" in execution:
        summary["execution_status_counts"] = execution["status"].fillna("missing").value_counts().to_dict()

    out = Path("static/data/generated_metrics.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, default=str))
    print(f"Wrote {out}")

if __name__ == "__main__":
    main()
