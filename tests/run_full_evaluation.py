#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full Evaluation Pipeline
========================
Evaluates the KG extraction system against all texts in tests/test_cases/
using gold triples from tests/gold_triples.json.

Usage:
    python3 tests/run_full_evaluation.py [--timeout 120] [--output results.json]

Metrics computed per test case and globally:
    - Precision, Recall, F1  (triple-level matching, case-insensitive, token-overlap)
    - Execution time
    - Success / Failure
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# ---------------------------------------------------------------------------
# Path setup — allow running from any working directory
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
EVAL_DIR     = PROJECT_ROOT / "tests" / "evaluation"
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(EVAL_DIR))

from pipeline_runner import PipelineRunner  # noqa: E402
from metrics import MetricsCalculator       # noqa: E402


# ---------------------------------------------------------------------------
# Fuzzy triple matching helpers
# ---------------------------------------------------------------------------

def _token_set(text: str) -> set:
    """Lower-cased word tokens after stripping punctuation."""
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    return {w for w in cleaned.split() if len(w) > 1}


def _jaccard(a: str, b: str) -> float:
    ta, tb = _token_set(a), _token_set(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _triple_matches(pred: Tuple[str, str, str],
                    gold: Tuple[str, str, str],
                    threshold: float = 0.6) -> bool:
    """
    Return True when a predicted triple is close enough to a gold triple.

    - subject  : Jaccard ≥ threshold (token overlap)
    - predicate: exact (lower-cased) OR Jaccard ≥ 0.8
    - object   : Jaccard ≥ threshold
    """
    ps, pp, po = pred
    gs, gp, go = gold
    subj_ok = (ps == gs) or (_jaccard(ps, gs) >= threshold)
    obj_ok  = (po == go) or (_jaccard(po, go) >= threshold)
    pred_ok = (pp == gp) or (_jaccard(pp, gp) >= 0.8)
    return subj_ok and pred_ok and obj_ok


def _compute_triple_metrics(
    predicted: List[Tuple[str, str, str]],
    gold: List[Tuple[str, str, str]],
) -> Dict[str, float]:
    """
    Compute precision / recall / F1 using fuzzy triple matching.

    Each gold triple is matched at most once (greedy left-to-right).
    """
    if not gold:
        # Special case: cas_12 expects NO triples → penalise if any produced
        if not predicted:
            return {"precision": 1.0, "recall": 1.0, "f1": 1.0, "tp": 0, "fp": 0, "fn": 0}
        else:
            fp = len(predicted)
            return {"precision": 0.0, "recall": 1.0, "f1": 0.0, "tp": 0, "fp": fp, "fn": 0}

    matched_gold  = [False] * len(gold)
    matched_pred  = [False] * len(predicted)

    for gi, gt in enumerate(gold):
        for pi, pt in enumerate(predicted):
            if matched_pred[pi]:
                continue
            if _triple_matches(pt, gt):
                matched_gold[gi] = True
                matched_pred[pi] = True
                break

    tp = sum(matched_gold)
    fp = sum(1 for m in matched_pred if not m)
    fn = sum(1 for m in matched_gold if not m)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1        = (2 * precision * recall / (precision + recall)
                 if (precision + recall) > 0 else 0.0)

    return {"precision": precision, "recall": recall, "f1": f1,
            "tp": tp, "fp": fp, "fn": fn}


# ---------------------------------------------------------------------------
# Main evaluation loop
# ---------------------------------------------------------------------------

def run_evaluation(timeout: int = 120, output_path: Optional[Path] = None) -> int:
    """
    Run the pipeline on every test case and compare with gold triples.
    Returns exit code (0 = all gold triples covered, 1 = some failures).
    """
    test_cases_dir = PROJECT_ROOT / "tests" / "test_cases"
    gold_file      = PROJECT_ROOT / "tests" / "gold_triples.json"

    # Load gold triples
    if not gold_file.exists():
        print(f"[ERROR] Gold file not found: {gold_file}", file=sys.stderr)
        return 2
    with open(gold_file, encoding="utf-8") as f:
        gold_data: Dict[str, List] = json.load(f)

    # Collect test case files (sorted)
    txt_files = sorted(test_cases_dir.glob("cas_*.txt"))
    if not txt_files:
        print(f"[ERROR] No test case files found in {test_cases_dir}", file=sys.stderr)
        return 2

    runner    = PipelineRunner(str(PROJECT_ROOT))
    calc      = MetricsCalculator()
    per_case  = []

    # ── Header ────────────────────────────────────────────────────────────
    width = 72
    print("=" * width)
    print("  FULL EVALUATION — KG Extraction Pipeline")
    print(f"  Test cases : {len(txt_files)}")
    print(f"  Gold file  : tests/gold_triples.json")
    print("=" * width)

    total_wall = time.time()

    for txt_path in txt_files:
        cas_id = txt_path.stem.split("_")[0] + "_" + txt_path.stem.split("_")[1]
        text   = txt_path.read_text(encoding="utf-8").strip()
        gold_raw: List[List[str]] = gold_data.get(cas_id, [])

        # Normalise gold to lower-case tuples
        gold_triples: List[Tuple[str, str, str]] = [
            (s.strip().lower(), p.strip().lower(), o.strip().lower())
            for s, p, o in gold_raw
        ]

        print(f"\n{'─' * width}")
        print(f"  [{cas_id}]  {txt_path.name}")
        print(f"  Text  : {text[:90]}{'…' if len(text) > 90 else ''}")
        print(f"  Gold  : {len(gold_triples)} triple(s)")

        # Run pipeline
        result = runner.run_pipeline(text, scenario_id=cas_id, timeout=timeout)
        exec_time = result["execution_time"]

        if not result["pipeline_ran_ok"]:
            errors = "; ".join(result["errors"][:3]) or "unknown error"
            # Special case: pipeline intentionally rejected the input (entry gate)
            # AND the gold expects 0 triples → correct rejection → perfect score.
            is_intentional_rejection = (
                "ENTRY GATE" in " ".join(result["errors"])
                or "Nombre d'entités insuffisant" in " ".join(result["errors"])
            )
            if is_intentional_rejection and not gold_triples:
                print(f"  ✅ Intentional rejection (entry gate) — gold=0 triples  [{exec_time:.1f}s]")
                per_case.append({
                    "cas_id": cas_id, "precision": 1.0, "recall": 1.0, "f1": 1.0,
                    "tp": 0, "fp": 0, "fn": 0,
                    "predicted": 0, "exec_time": exec_time, "ok": True,
                })
                calc.add_result(
                    expected={"expected_relations": []},
                    actual={"relations": [], "success": True,
                            "execution_time": exec_time, "metrics": result["metrics"]},
                )
                continue
            print(f"  ❌ Pipeline FAILED  ({exec_time:.1f}s) — {errors}")
            per_case.append({
                "cas_id": cas_id, "precision": 0.0, "recall": 0.0, "f1": 0.0,
                "tp": 0, "fp": 0, "fn": len(gold_triples),
                "predicted": 0, "exec_time": exec_time, "ok": False,
            })
            continue

        # Normalise predicted triples
        predicted_triples: List[Tuple[str, str, str]] = [
            (r["subject"].strip().lower(),
             r["predicate"].strip().lower(),
             r["object"].strip().lower())
            for r in result["relations"]
        ]

        metrics = _compute_triple_metrics(predicted_triples, gold_triples)

        # Print predicted relations for transparency
        if predicted_triples:
            print(f"  Predicted relations ({len(predicted_triples)}):")
            for s, p, o in predicted_triples:
                print(f"    • {s!r:30s} --[{p}]--> {o!r}")
        else:
            print("  Predicted relations : (none)")

        # Verdict per gold triple
        norm_pred = list(predicted_triples)
        for gs, gp, go in gold_triples:
            hit = any(_triple_matches(pt, (gs, gp, go)) for pt in norm_pred)
            icon = "✅" if hit else "❌"
            print(f"  {icon}  {gs!r:30s} --[{gp}]--> {go!r}")

        p, r, f = metrics["precision"], metrics["recall"], metrics["f1"]
        print(f"  Metrics : precision={p:.2f}  recall={r:.2f}  F1={f:.2f}"
              f"  (TP={metrics['tp']} FP={metrics['fp']} FN={metrics['fn']})"
              f"  [{exec_time:.1f}s]")

        per_case.append({
            "cas_id": cas_id,
            "precision": p, "recall": r, "f1": f,
            "tp": metrics["tp"], "fp": metrics["fp"], "fn": metrics["fn"],
            "predicted": len(predicted_triples),
            "exec_time": exec_time,
            "ok": result["pipeline_ran_ok"],
        })

        # Feed MetricsCalculator for aggregate stats
        calc.add_result(
            expected={
                "expected_relations": [
                    {"subject": s, "predicate": p_, "object": o}
                    for s, p_, o in gold_triples
                ]
            },
            actual={
                "relations": [
                    {"subject": s, "predicate": p_, "object": o}
                    for s, p_, o in predicted_triples
                ],
                "success": f >= 0.5,
                "execution_time": exec_time,
                "metrics": result["metrics"],
            },
        )

    total_wall = time.time() - total_wall

    # ── Summary ───────────────────────────────────────────────────────────
    print(f"\n{'=' * width}")
    print("  EVALUATION RESULTS")
    print(f"{'=' * width}")
    print(f"  {'Case':<12} {'P':>6} {'R':>6} {'F1':>6}  {'TP':>3} {'FP':>3} {'FN':>3}  {'Time':>6}")
    print(f"  {'─'*12} {'─'*6} {'─'*6} {'─'*6}  {'─'*3} {'─'*3} {'─'*3}  {'─'*6}")

    ok_count = 0
    for c in per_case:
        status = "✅" if c["f1"] >= 1.0 else ("⚠️ " if c["f1"] > 0 else "❌")
        if c["f1"] >= 1.0:
            ok_count += 1
        print(f"  {status} {c['cas_id']:<10} "
              f"{c['precision']:>5.2f}  {c['recall']:>5.2f}  {c['f1']:>5.2f}  "
              f"{c['tp']:>3} {c['fp']:>3} {c['fn']:>3}  "
              f"{c['exec_time']:>5.1f}s")

    if per_case:
        avg_p  = sum(c["precision"] for c in per_case) / len(per_case)
        avg_r  = sum(c["recall"]    for c in per_case) / len(per_case)
        avg_f1 = sum(c["f1"]        for c in per_case) / len(per_case)
        print(f"\n  {'─'*12} {'─'*6} {'─'*6} {'─'*6}")
        print(f"  {'Average':<12} {avg_p:>5.2f}  {avg_r:>5.2f}  {avg_f1:>5.2f}")
        print(f"\n  Cases perfect (F1=1.0) : {ok_count}/{len(per_case)}")
        print(f"  Total wall-clock time  : {total_wall:.1f}s")
        print(f"\n  Average F1 = {avg_f1:.2f}")

    print("=" * width)

    # ── Optional JSON export ──────────────────────────────────────────────
    if output_path:
        report = {
            "summary": {
                "avg_precision": avg_p,
                "avg_recall":    avg_r,
                "avg_f1":        avg_f1,
                "perfect_cases": ok_count,
                "total_cases":   len(per_case),
                "wall_time_s":   round(total_wall, 2),
            },
            "per_case": per_case,
        }
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n  📄 Results saved to: {output_path}")

    return 0 if ok_count == len(per_case) else 1


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Full evaluation of the KG extraction pipeline."
    )
    parser.add_argument(
        "--timeout", type=int, default=120,
        help="Timeout in seconds per test case (default: 120)"
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Optional path to save JSON evaluation report"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    sys.exit(run_evaluation(
        timeout=args.timeout,
        output_path=Path(args.output) if args.output else None,
    ))
