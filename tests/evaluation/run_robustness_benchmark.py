#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Robustness Benchmark Runner
===========================
Loads  tests/evaluation/robustness_benchmark.json  and evaluates each test
against the live HybridNERModule pipeline.

Usage
-----
  python run_robustness_benchmark.py [--verbose] [--category <cat>] [--json]

Options
-------
  --verbose     Print per-test entity diff
  --category    Run only tests from one category (e.g. org_detection)
  --json        Write results to outputs/robustness_results.json

Exit code
---------
  0  all tests pass (or no test has a hard expected set)
  1  one or more tests fail
"""

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ── path wiring ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent.parent   # repo root
sys.path.insert(0, str(ROOT))

# ── imports (lazy spaCy load) ─────────────────────────────────────────────────
import spacy
from hybrid_ner_module import HybridNERModule

# ── constants ─────────────────────────────────────────────────────────────────
BENCHMARK_PATH = Path(__file__).parent / "robustness_benchmark.json"
OUTPUTS_DIR    = Path(__file__).parent / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

# Map JSON "type" values → internal NER labels used by HybridNERModule
_TYPE_ALIASES: Dict[str, List[str]] = {
    "PER":      ["PER", "Person"],
    "ORG":      ["ORG", "Organization"],
    "TOPIC":    ["TOPIC", "Topic"],
    "LOC":      ["LOC", "Location", "GPE"],
    "DOCUMENT": ["DOCUMENT", "Document"],
    "MISC":     ["MISC"],
}

# Minimum Jaccard token-overlap to count an entity as matched
_JACCARD_THRESHOLD = 0.6


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _strip_json_comments(text: str) -> str:
    """Remove // line-comments so json.loads can parse the file."""
    return re.sub(r'//[^\n]*', '', text)


def _canonical(s: str) -> str:
    """Lower-case + remove accents + collapse whitespace."""
    s = s.lower()
    s = ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )
    return re.sub(r'\s+', ' ', s).strip()


def _tokens(s: str) -> set:
    return set(re.findall(r'\w+', _canonical(s)))


def _jaccard(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta and not tb:
        return 1.0
    inter = len(ta & tb)
    union = len(ta | tb)
    return inter / union if union else 0.0


def _normalize_type(raw: str) -> str:
    """Normalise a type label to the canonical short form."""
    r = raw.upper()
    for canon, aliases in _TYPE_ALIASES.items():
        if r in [a.upper() for a in aliases]:
            return canon
    return raw.upper()


def _match_entity(
    expected_text: str,
    expected_type: str,
    extracted: List[Tuple[str, str, float]],
) -> bool:
    """
    Return True if *any* extracted entity matches the expected one.

    Matching strategy (in order):
    1. Exact text + type
    2. Canonical text equality + type
    3. Jaccard ≥ threshold + type
    """
    e_type = _normalize_type(expected_type)
    e_can  = _canonical(expected_text)

    for ext_text, ext_type, _ in extracted:
        ext_type_n = _normalize_type(ext_type)

        # Type must match (or one of its aliases)
        type_ok = (ext_type_n == e_type)
        if not type_ok:
            continue

        # Text match
        if ext_text == expected_text:
            return True
        if _canonical(ext_text) == e_can:
            return True
        if _jaccard(expected_text, ext_text) >= _JACCARD_THRESHOLD:
            return True

    return False


# ─────────────────────────────────────────────────────────────────────────────
# Core evaluation
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_test(
    test: Dict[str, Any],
    ner: HybridNERModule,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Run a single benchmark test and return a result dict.

    Returns
    -------
    {
        "id": str,
        "category": str,
        "status": "PASS" | "FAIL" | "PARTIAL" | "SKIP",
        "expected_count": int,
        "matched_count": int,
        "missing": [ {"text": ..., "type": ...} ],
        "extracted": [ (text, type, conf) ]
    }
    """
    tid      = test.get("id", "?")
    text     = test.get("text", "")
    expected = test.get("expected_entities", [])

    # Empty-input edge case
    if not text.strip():
        return {
            "id": tid, "category": test.get("category", ""),
            "status": "SKIP", "expected_count": 0,
            "matched_count": 0, "missing": [], "extracted": [],
        }

    extracted = ner.extract(text, verbose=False)

    matched  = []
    missing  = []
    for exp in expected:
        if _match_entity(exp["text"], exp["type"], extracted):
            matched.append(exp)
        else:
            missing.append(exp)

    n_exp = len(expected)
    n_mat = len(matched)

    if n_exp == 0:
        status = "SKIP"          # no ground-truth defined
    elif n_mat == n_exp:
        status = "PASS"
    elif n_mat == 0:
        status = "FAIL"
    else:
        status = "PARTIAL"       # some entities matched

    if verbose:
        _print_diff(tid, text, expected, extracted, missing, status)

    return {
        "id": tid,
        "category": test.get("category", ""),
        "description": test.get("description", ""),
        "status": status,
        "expected_count": n_exp,
        "matched_count": n_mat,
        "missing": missing,
        "extracted": [(t, tp, round(c, 3)) for t, tp, c in extracted],
    }


def _print_diff(tid, text, expected, extracted, missing, status):
    """Pretty-print entity comparison for verbose mode."""
    icon = {"PASS": "✅", "FAIL": "❌", "PARTIAL": "⚠️ ", "SKIP": "⏭️ "}.get(status, "?")
    print(f"\n  {icon} [{tid}]  {status}")
    print(f"     Text: {text[:80]}{'…' if len(text) > 80 else ''}")
    if missing:
        print(f"     Missing entities:")
        for m in missing:
            print(f"       - {m['text']!r:35s} expected={m['type']}")
    if expected:
        found_texts = {_canonical(e[0]) for e in extracted}
        print(f"     Extracted:")
        for ext_t, ext_tp, ext_c in extracted:
            marker = "✓" if any(_jaccard(ext_t, e["text"]) >= _JACCARD_THRESHOLD for e in expected) else " "
            print(f"       {marker} [{ext_tp:8s}] {ext_t!r:40s} conf={ext_c:.2f}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Robustness Benchmark Runner")
    parser.add_argument("--verbose",  action="store_true", help="Show per-test entity diff")
    parser.add_argument("--category", type=str, default=None, help="Filter to one category")
    parser.add_argument("--json",     action="store_true", help="Write JSON results file")
    args = parser.parse_args()

    # Load benchmark
    raw = BENCHMARK_PATH.read_text(encoding="utf-8")
    data = json.loads(_strip_json_comments(raw))
    tests = data["tests"]

    if args.category:
        tests = [t for t in tests if t.get("category") == args.category]
        if not tests:
            print(f"[ERROR] No tests found for category '{args.category}'")
            sys.exit(1)

    # Build NER
    print("[Benchmark] Loading spaCy model…")
    nlp = spacy.load("fr_core_news_sm")
    ner = HybridNERModule(nlp)
    print(f"[Benchmark] Running {len(tests)} tests…\n")

    # Run
    results = []
    for test in tests:
        r = evaluate_test(test, ner, verbose=args.verbose)
        results.append(r)

    # Aggregate per-category
    categories: Dict[str, Dict] = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "pass": 0, "partial": 0,
                               "fail": 0, "skip": 0, "entity_hits": 0,
                               "entity_expected": 0}
        s = categories[cat]
        s["total"] += 1
        s[r["status"].lower()] += 1
        s["entity_hits"]     += r["matched_count"]
        s["entity_expected"] += r["expected_count"]

    # ── Summary table ────────────────────────────────────────────────────────
    print("\n" + "=" * 72)
    print("  ROBUSTNESS BENCHMARK — RESULTS SUMMARY")
    print("=" * 72)
    print(f"  {'Category':<28} {'Tests':>5} {'PASS':>5} {'PART':>5} {'FAIL':>5} {'Ent-F1':>8}")
    print("  " + "-" * 60)

    total_pass = total_partial = total_fail = total_skip = 0
    total_hits = total_expected = 0

    for cat, s in sorted(categories.items()):
        e_prec = s["entity_hits"] / max(sum(r["matched_count"] + len(r["missing"]) + r["matched_count"]
                                            for r in results if r["category"] == cat), 1)
        e_rec  = s["entity_hits"] / max(s["entity_expected"], 1)
        f1     = (2 * e_prec * e_rec / (e_prec + e_rec)) if (e_prec + e_rec) > 0 else 0.0

        print(f"  {cat:<28} {s['total']:>5} {s['pass']:>5} {s['partial']:>5} "
              f"{s['fail']:>5} {f1:>7.1%}")

        total_pass    += s["pass"]
        total_partial += s["partial"]
        total_fail    += s["fail"]
        total_skip    += s["skip"]
        total_hits    += s["entity_hits"]
        total_expected += s["entity_expected"]

    total_tests = len(results)
    overall_rec = total_hits / max(total_expected, 1)
    print("  " + "-" * 60)
    print(f"  {'TOTAL':<28} {total_tests:>5} {total_pass:>5} {total_partial:>5} {total_fail:>5}")
    print(f"\n  Entity Recall (overall) : {overall_rec:.1%}  "
          f"({total_hits}/{total_expected} expected entities matched)")
    print(f"  Pass rate               : {total_pass/max(total_tests-total_skip,1):.1%}  "
          f"({total_pass}/{total_tests - total_skip} non-skip tests)")
    print("=" * 72)

    # ── List failures ────────────────────────────────────────────────────────
    failures = [r for r in results if r["status"] in ("FAIL", "PARTIAL")]
    if failures and not args.verbose:
        print(f"\n  ⚠️  {len(failures)} test(s) with missing entities — run with --verbose for details")
        for r in failures:
            missing_str = ", ".join(f"{m['text']} ({m['type']})" for m in r["missing"])
            print(f"     [{r['id']:10s}] {r['status']:7s}  missing: {missing_str}")

    # ── JSON output ──────────────────────────────────────────────────────────
    if args.json:
        out_path = OUTPUTS_DIR / "robustness_results.json"
        payload = {
            "meta": {
                "total_tests":   total_tests,
                "pass":          total_pass,
                "partial":       total_partial,
                "fail":          total_fail,
                "skip":          total_skip,
                "entity_recall": round(overall_rec, 4),
            },
            "by_category": categories,
            "results":     results,
        }
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n  Results written to: {out_path}")

    sys.exit(0 if total_fail == 0 else 1)


if __name__ == "__main__":
    main()
