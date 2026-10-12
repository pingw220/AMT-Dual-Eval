"""Command-line interface for AMT-Dual-Eval.

Usage:
    python -m amt_dual_eval.cli audio-score --metric dtw  --feature tempogram \\
        --reference ref.wav --candidate cand.wav
    python -m amt_dual_eval.cli audio-score --metric twed --all-top3 \\
        --reference ref.wav --candidate cand.wav --output-format json
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from typing import Dict, List

from .evaluate_audio import default_feature, score_all_top3, score_pair
from .utils import supported_features, top3


def _format_text(rows: List[Dict[str, object]]) -> str:
    if len(rows) == 1 and "feature" in rows[0]:
        r = rows[0]
        return f"{r['metric']}_score: {r['score']:.6f}  (feature={r['feature']})"
    width = max(len(str(r["feature"])) for r in rows)
    lines = [f"{'feature':<{width}}  {'metric':<5}  score"]
    for r in rows:
        lines.append(f"{str(r['feature']):<{width}}  {str(r['metric']):<5}  {r['score']:.6f}")
    return "\n".join(lines)


def _format_csv(rows: List[Dict[str, object]]) -> str:
    keys: List[str] = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=keys)
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().rstrip("\n")


def _emit(rows: List[Dict[str, object]], fmt: str, output_path: str | None) -> None:
    if fmt == "json":
        text = json.dumps(rows, indent=2)
    elif fmt == "csv":
        text = _format_csv(rows)
    else:
        text = _format_text(rows)
    if output_path:
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print(f"Wrote {len(rows)} row(s) to {output_path}")
    else:
        print(text)


def _cmd_audio_score(args: argparse.Namespace) -> int:
    metric = args.metric.lower()

    if args.all_top3:
        if args.feature:
            print("error: use either --feature or --all-top3, not both", file=sys.stderr)
            return 2
        rows = score_all_top3(
            args.reference, args.candidate, metric,
            nu=args.nu, lambd=args.lambda_value,
        )
    else:
        feature = args.feature or default_feature(metric)
        if feature not in supported_features():
            print(
                f"error: unsupported feature {feature!r}. "
                f"Choose from: {', '.join(supported_features())}",
                file=sys.stderr,
            )
            return 2
        rows = [score_pair(
            args.reference, args.candidate, metric, feature,
            nu=args.nu, lambd=args.lambda_value,
        )]

    _emit(rows, args.output_format, args.output_path)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="amt-dual-eval",
        description="Dual evaluation of automatic music transcription systems.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser(
        "audio-score",
        help="Score one (reference, candidate) audio pair with DTW or TWED.",
    )
    p.add_argument("--metric", required=True, choices=["dtw", "twed"])
    p.add_argument(
        "--feature",
        default=None,
        help=f"Feature name. Supported: {', '.join(supported_features())}. "
             "If omitted, uses the metric's default feature.",
    )
    p.add_argument(
        "--all-top3", action="store_true",
        help="Evaluate the verified top-3 features for the chosen metric.",
    )
    p.add_argument("--reference", required=True, help="Reference performance audio path.")
    p.add_argument("--candidate", required=True, help="Transcribed/rendered candidate audio path.")
    p.add_argument("--lambda-value", dest="lambda_value", type=float, default=None,
                   help="TWED lambda (deletion penalty) override.")
    p.add_argument("--nu", type=float, default=None,
                   help="TWED nu (stiffness) override.")
    p.add_argument("--output-format", choices=["text", "json", "csv"], default="text")
    p.add_argument("--output-path", default=None, help="Write results to this file.")
    p.set_defaults(func=_cmd_audio_score)
    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
