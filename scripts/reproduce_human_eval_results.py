#!/usr/bin/env python3
"""Reproduce human-evaluation system rankings from the public release.

Runs the six ranking methods (system_rank, wilson_win_rate, pairwise_matrix,
bradley_terry, least_squares, elo) on the released de-identified forced-choice
responses and prints the rankings. The results match data/public/system_scores.csv.
Bradley-Terry is the headline method.

Requires data/public/responses_public.csv. If only aggregate tables are present,
the system-level scores are available directly in data/public/system_scores.csv.

Usage:
    python scripts/reproduce_human_eval_results.py --method bradley_terry
    python scripts/reproduce_human_eval_results.py --method all
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = REPO_ROOT / "data" / "public"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--method", default="all",
                        help="One ranking method, or 'all' (default).")
    args = parser.parse_args(argv)

    responses = PUBLIC_DIR / "responses_public.csv"
    if not responses.exists():
        print("responses_public.csv not found.")
        print("System-level scores are available in data/public/system_scores.csv.")
        return 1

    sys.path.insert(0, str(REPO_ROOT / "src"))
    from amt_dual_eval.human_eval import score_all_methods

    df = pd.read_csv(responses)
    long = score_all_methods(df)
    if args.method and args.method != "all":
        methods = [args.method]
    else:
        methods = sorted(long["method"].unique())
    for m in methods:
        sub = long[long["method"] == m].sort_values("rank")
        print(f"\n=== {m} ===")
        for _, r in sub.iterrows():
            print(f"  {int(r['rank']):>2}. {r['system']:<40} {r['score']:+.5f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
