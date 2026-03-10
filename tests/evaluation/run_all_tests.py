#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Test Runner - Executes all evaluation scenarios and generates report
Run with: python tests/evaluation/run_all_tests.py
"""

import re
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.evaluation.scenarios import generate_all_scenarios, get_scenario_categories
from tests.evaluation.pipeline_runner import PipelineRunner
from tests.evaluation.metrics import MetricsCalculator


class TestOrchestrator:
    """Orchestrates the complete evaluation suite"""
    
    def __init__(self, project_root: str, output_dir: str = None, log_dir: str = None):
        """
        Initialize test orchestrator.
        
        Args:
            project_root: Path to project root
            output_dir: Directory for test outputs (default: tests/evaluation/outputs)
            log_dir: Directory for logs (default: tests/evaluation/logs)
        """
        self.project_root = Path(project_root)
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent / "outputs"
        self.log_dir = Path(log_dir) if log_dir else Path(__file__).parent / "logs"
        
        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.runner = PipelineRunner(str(self.project_root))
        self.calculator = MetricsCalculator()
        
        # Storage
        self.all_results = []
        self.failed_tests = []
        self.category_stats = {}
    
    def run_all_tests(self, 
                     max_tests: int = None,
                     categories: List[str] = None,
                     verbose: bool = True) -> Dict[str, Any]:
        """
        Run all test scenarios.
        
        Args:
            max_tests: Maximum number of tests to run (None = all)
            categories: List of categories to test (None = all)
            verbose: Print progress messages
            
        Returns:
            Summary dictionary
        """
        scenarios = generate_all_scenarios()
        
        # Filter by category if specified
        if categories:
            scenarios = [s for s in scenarios if s.category in categories]
        
        # Limit number of tests if specified
        if max_tests:
            scenarios = scenarios[:max_tests]
        
        total_scenarios = len(scenarios)
        
        if verbose:
            print("=" * 80)
            print("NEURO-SYMBOLIC KG EXTRACTION - EVALUATION SUITE")
            print("=" * 80)
            print(f"\nTotal scenarios to test: {total_scenarios}")
            print(f"Output directory: {self.output_dir}")
            print(f"Log directory: {self.log_dir}")
            print("\nStarting tests...\n")
        
        start_time = time.time()
        
        for idx, scenario in enumerate(scenarios, 1):
            if verbose:
                print(f"[{idx}/{total_scenarios}] Running {scenario.scenario_id}: {scenario.description}")
            
            try:
                # Run pipeline
                result = self.runner.run_pipeline(
                    input_text=scenario.input_text,
                    scenario_id=scenario.scenario_id,
                    timeout=60
                )
                
                # ----------------------------------------------------------
                # Ground-truth comparison: overwrite result["success"] with
                # whether predictions match the expected annotations.
                # ----------------------------------------------------------
                gt_pass, gt_details = self._evaluate_against_ground_truth(
                    scenario, result
                )
                result["success"] = gt_pass
                result["gt_details"] = gt_details

                # Save individual result
                result_file = self.runner.save_result(result, self.output_dir)
                
                # Log to file
                self._log_test(scenario, result)
                
                # Add to metrics calculator
                self.calculator.add_result(
                    expected=scenario.to_dict(),
                    actual=result
                )
                
                # Store result
                self.all_results.append({
                    "scenario": scenario.to_dict(),
                    "result": result
                })
                
                # Track failures
                if not gt_pass:
                    self.failed_tests.append({
                        "scenario_id": scenario.scenario_id,
                        "category": scenario.category,
                        "description": scenario.description,
                        "errors": result["errors"],
                        "gt_details": gt_details
                    })
                
                # Update category stats
                if scenario.category not in self.category_stats:
                    self.category_stats[scenario.category] = {
                        "total": 0,
                        "passed": 0,
                        "failed": 0
                    }
                
                self.category_stats[scenario.category]["total"] += 1
                if gt_pass:
                    self.category_stats[scenario.category]["passed"] += 1
                else:
                    self.category_stats[scenario.category]["failed"] += 1
                
                if verbose:
                    status = "✅ PASS" if gt_pass else "❌ FAIL"
                    print(f"  {status} - {result['execution_time']:.2f}s - "
                          f"Entities: {len(result['entities'])}, "
                          f"Relations: {len(result['relations'])}, "
                          f"Errors: {len(result['errors'])}")
                
            except Exception as e:
                if verbose:
                    print(f"  ❌ EXCEPTION: {str(e)}")
                
                self.failed_tests.append({
                    "scenario_id": scenario.scenario_id,
                    "category": scenario.category,
                    "description": scenario.description,
                    "errors": [f"Test execution exception: {str(e)}"]
                })
            
            if verbose:
                print()
        
        total_time = time.time() - start_time
        
        if verbose:
            print("=" * 80)
            print(f"Testing complete! Total time: {total_time:.2f}s")
            print("=" * 80)
        
        # Generate summary
        summary = self._generate_summary(total_time)
        
        # Save summary
        summary_file = self.output_dir / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        if verbose:
            print(f"\nSummary saved to: {summary_file}")
        
        return summary
    
    def _log_test(self, scenario, result):
        """Log test execution to file"""
        log_file = self.log_dir / f"{scenario.scenario_id}.log"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"Scenario ID: {scenario.scenario_id}\n")
            f.write(f"Category: {scenario.category}\n")
            f.write(f"Description: {scenario.description}\n")
            f.write(f"Timestamp: {result['timestamp']}\n")
            f.write(f"Success: {result['success']}\n")
            f.write(f"Execution Time: {result['execution_time']:.3f}s\n")
            f.write(f"\n{'=' * 80}\n")
            f.write(f"INPUT TEXT:\n{scenario.input_text}\n")
            f.write(f"\n{'=' * 80}\n")
            f.write(f"EXPECTED ENTITIES:\n")
            for ent in scenario.expected_entities:
                f.write(f"  - {ent['text']} ({ent['type']})\n")
            f.write(f"\nEXPECTED RELATIONS:\n")
            for rel in scenario.expected_relations:
                f.write(f"  - {rel['subject']} --[{rel['predicate']}]--> {rel['object']}\n")
            f.write(f"\n{'=' * 80}\n")
            f.write(f"ACTUAL ENTITIES:\n")
            for ent in result['entities']:
                f.write(f"  - {ent['text']} ({ent['type']}) [conf: {ent.get('confidence', 1.0):.2f}]\n")
            f.write(f"\nACTUAL RELATIONS:\n")
            for rel in result['relations']:
                f.write(f"  - {rel['subject']} --[{rel['predicate']}]--> {rel['object']}\n")
            f.write(f"\n{'=' * 80}\n")
            f.write(f"METRICS:\n")
            for key, value in result['metrics'].items():
                f.write(f"  {key}: {value}\n")
            f.write(f"\n{'=' * 80}\n")
            if result['errors']:
                f.write(f"ERRORS:\n")
                for error in result['errors']:
                    f.write(f"  - {error}\n")
            if result['warnings']:
                f.write(f"\nWARNINGS:\n")
                for warning in result['warnings']:
                    f.write(f"  - {warning}\n")
    
    # ------------------------------------------------------------------
    # GROUND-TRUTH EVALUATION
    # ------------------------------------------------------------------

    # Canonical type aliases: map pipeline output types → scenario types
    # This lets us match "ORG" == "ORG", "PER" == "PER", etc., and also
    # accept the looser TOPIC/DOCUMENT labels used in scenario annotations.
    _TYPE_ALIASES: Dict[str, str] = {
        # Pipeline NER tags (spaCy / custom)
        "PER":       "PER",
        "PERSON":    "PER",
        "ORG":       "ORG",
        "ORGANIZATION": "ORG",
        "LOC":       "LOC",
        "LOCATION":  "LOC",
        "GPE":       "LOC",
        "MISC":      "MISC",
        "TOPIC":     "TOPIC",
        "CONCEPT":   "TOPIC",
        "DOCUMENT":  "DOCUMENT",
        "DOC":       "DOCUMENT",
    }

    @classmethod
    def _normalise_type(cls, t: str) -> str:
        """Return a canonical type string, upper-cased."""
        return cls._TYPE_ALIASES.get(t.upper(), t.upper())

    def _evaluate_against_ground_truth(
        self, scenario, result: Dict[str, Any]
    ) -> tuple:
        """
        Compare pipeline output against ground-truth annotations.

        A test PASSES when ALL of the following hold:
          1. Every expected entity is present in predictions (text match,
             case-insensitive; type match after normalisation).
          2. Every expected relation is present in predictions
             (subject + predicate + object, case-insensitive substring match).
          3. No ontology violations appear in the pipeline output when
             `should_fail` is False; if `should_fail` is True the test
             passes only when at least one violation is detected.

        Returns:
            (passed: bool, details: dict)
        """
        details = {
            "missing_entities": [],
            "extra_entities": [],
            "missing_relations": [],
            "extra_relations": [],
            "violations_found": 0,
            "passed_reason": "",
        }

        # ---- 1. Edge-case: no ground-truth at all -----------------------
        has_expected_entities = bool(scenario.expected_entities)
        has_expected_relations = bool(scenario.expected_relations)

        # Skip ground-truth check for pure edge-case / noise tests that
        # have empty expected lists (e.g. empty input, random chars).
        if not has_expected_entities and not has_expected_relations:
            details["passed_reason"] = "no ground-truth annotations (trivial pass)"
            return True, details

        # ---- 2. Entity comparison ----------------------------------------
        def _ent_key(text: str, etype: str) -> tuple:
            return (text.strip().lower(), self._normalise_type(etype))

        expected_ent_keys = {
            _ent_key(e["text"], e["type"]) for e in scenario.expected_entities
        }
        predicted_ent_keys = {
            _ent_key(e["text"], e["type"]) for e in result.get("entities", [])
        }

        # Fuzzy token-overlap match: titles like "Prof." are stripped,
        # then token-level Jaccard (≥0.7) is required, plus same type.
        # This prevents false positives like "Einstein Institute" vs "Albert Einstein".
        def _token_set(text: str) -> set:
            # Strip honorifics/titles, punctuation, then split
            cleaned = re.sub(
                r'\b(?:dr\.?|prof\.?|professeur|docteur|mr\.?|mrs\.?|mme\.?|monsieur|madame)\b',
                '', text, flags=re.IGNORECASE
            )
            cleaned = re.sub(r'[^\w\s]', '', cleaned)
            return {w for w in cleaned.lower().split() if len(w) > 1}

        def _token_overlap(text_a: str, text_b: str) -> float:
            ta, tb = _token_set(text_a), _token_set(text_b)
            if not ta or not tb:
                return 0.0
            return len(ta & tb) / len(ta | tb)  # Jaccard coefficient

        def _fuzzy_entity_match(exp_key: tuple, pred_keys: set) -> bool:
            exp_text, exp_type = exp_key
            if exp_key in pred_keys:  # exact match first
                return True
            for pred_text, pred_type in pred_keys:
                if pred_type == exp_type and _token_overlap(exp_text, pred_text) >= 0.7:
                    return True
            return False

        def _fuzzy_extra(pred_key: tuple, exp_keys: set) -> bool:
            """Return True if pred_key is NOT covered by any expected key."""
            pred_text, pred_type = pred_key
            if pred_key in exp_keys:
                return False
            for exp_text, exp_type in exp_keys:
                if pred_type == exp_type and _token_overlap(pred_text, exp_text) >= 0.7:
                    return False
            return True

        missing_ents = [k for k in expected_ent_keys if not _fuzzy_entity_match(k, predicted_ent_keys)]
        extra_ents   = [k for k in predicted_ent_keys if _fuzzy_extra(k, expected_ent_keys)]

        details["missing_entities"] = [
            {"text": t, "type": tp} for t, tp in missing_ents
        ]
        details["extra_entities"] = [
            {"text": t, "type": tp} for t, tp in extra_ents
        ]

        # ---- 3. Relation comparison ---------------------------------------
        def _rel_key(subj: str, pred: str, obj: str) -> tuple:
            return (subj.strip().lower(), pred.strip().lower(), obj.strip().lower())

        expected_rel_keys = {
            _rel_key(r["subject"], r["predicate"], r["object"])
            for r in scenario.expected_relations
        }

        predicted_rel_keys = {
            _rel_key(r["subject"], r["predicate"], r["object"])
            for r in result.get("relations", [])
        }

        missing_rels = expected_rel_keys - predicted_rel_keys
        extra_rels   = predicted_rel_keys - expected_rel_keys

        details["missing_relations"] = [
            {"subject": s, "predicate": p, "object": o}
            for s, p, o in missing_rels
        ]
        details["extra_relations"] = [
            {"subject": s, "predicate": p, "object": o}
            for s, p, o in extra_rels
        ]

        # ---- 4. Ontology violations ---------------------------------------
        violations = (
            result.get("metrics", {}).get("domain_violations", 0)
            + result.get("metrics", {}).get("range_violations", 0)
        )
        details["violations_found"] = violations

        # ---- 5. Pass/fail decision ----------------------------------------
        entities_ok  = len(missing_ents) == 0
        relations_ok = len(missing_rels) == 0
        violations_ok = (
            (violations > 0) if scenario.should_fail else (violations == 0)
        )

        # For violation tests, only check that violations were raised;
        # entity/relation matching is still evaluated but not required.
        if scenario.should_fail:
            passed = violations_ok
            details["passed_reason"] = (
                "expected violation detected"
                if passed
                else "expected violation NOT detected"
            )
        else:
            passed = entities_ok and relations_ok and violations_ok
            reasons = []
            if not entities_ok:
                reasons.append(
                    f"{len(missing_ents)} missing entity/entities"
                )
            if not relations_ok:
                reasons.append(
                    f"{len(missing_rels)} missing relation(s)"
                )
            if not violations_ok:
                reasons.append("unexpected ontology violations")
            details["passed_reason"] = (
                "all checks passed" if passed else "; ".join(reasons)
            )

        return passed, details

    def _generate_summary(self, total_time: float) -> Dict[str, Any]:
        """Generate test summary"""
        metrics = self.calculator.get_all_metrics()
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "execution_time": total_time,
            "test_counts": {
                "total": len(self.all_results),
                "passed": metrics["success_metrics"]["successful"],
                "failed": metrics["success_metrics"]["failed"],
                "success_rate": metrics["success_metrics"]["success_rate"]
            },
            "category_breakdown": self.category_stats,
            "entity_metrics": metrics["entity_metrics"],
            "relation_metrics": metrics["relation_metrics"],
            "ontology_metrics": metrics["ontology_metrics"],
            "performance_metrics": metrics["performance_metrics"],
            "hallucination_rate": metrics["hallucination_rate"],
            "type_confusion_matrix": metrics["type_confusion_matrix"],
            "failed_tests": self.failed_tests[:20]  # Top 20 failures
        }
        
        return summary
    
    def print_summary(self, summary: Dict[str, Any]):
        """Print formatted summary to console"""
        print("\n" + "=" * 80)
        print("EVALUATION SUMMARY")
        print("=" * 80)
        
        print(f"\n📊 Test Counts:")
        print(f"  Total Tests: {summary['test_counts']['total']}")
        print(f"  Passed: {summary['test_counts']['passed']} ✅")
        print(f"  Failed: {summary['test_counts']['failed']} ❌")
        print(f"  Success Rate: {summary['test_counts']['success_rate']:.1%}")
        
        print(f"\n📂 Category Breakdown:")
        for category, stats in summary['category_breakdown'].items():
            success_rate = stats['passed'] / stats['total'] if stats['total'] > 0 else 0
            print(f"  {category}: {stats['passed']}/{stats['total']} ({success_rate:.1%})")
        
        print(f"\n🏷️  Entity Recognition Metrics:")
        em = summary['entity_metrics']
        print(f"  Precision: {em['precision']:.1%}")
        print(f"  Recall: {em['recall']:.1%}")
        print(f"  F1 Score: {em['f1_score']:.1%}")
        print(f"  Type Accuracy: {em['type_accuracy']:.1%}")
        
        print(f"\n🔗 Relation Extraction Metrics:")
        rm = summary['relation_metrics']
        print(f"  Precision: {rm['precision']:.1%}")
        print(f"  Recall: {rm['recall']:.1%}")
        print(f"  F1 Score: {rm['f1_score']:.1%}")
        
        print(f"\n⚖️  Ontology Validation:")
        om = summary['ontology_metrics']
        print(f"  Total Violations: {om['total_violations']}")
        print(f"  Domain Violations: {om['domain_violations']}")
        print(f"  Range Violations: {om['range_violations']}")
        print(f"  Violation Rate: {om['violation_rate']:.1%}")
        
        print(f"\n⚡ Performance:")
        pm = summary['performance_metrics']
        print(f"  Avg Execution Time: {pm['avg_execution_time']:.2f}s")
        print(f"  Min: {pm['min_execution_time']:.2f}s")
        print(f"  Max: {pm['max_execution_time']:.2f}s")
        
        print(f"\n🎭 Hallucination Rate: {summary['hallucination_rate']:.1%}")
        
        if summary['failed_tests']:
            print(f"\n❌ Top Failed Tests:")
            for test in summary['failed_tests'][:5]:
                print(f"  - {test['scenario_id']}: {test['description']}")
        
        print("\n" + "=" * 80)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run KG Extraction Evaluation Suite")
    parser.add_argument("--max-tests", type=int, help="Maximum number of tests to run")
    parser.add_argument("--categories", nargs="+", help="Specific categories to test")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output")
    parser.add_argument("--project-root", default=str(Path(__file__).parent.parent.parent),
                       help="Project root directory")
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = TestOrchestrator(args.project_root)
    
    # Run tests
    summary = orchestrator.run_all_tests(
        max_tests=args.max_tests,
        categories=args.categories,
        verbose=not args.quiet
    )
    
    # Print summary
    orchestrator.print_summary(summary)
    
    # Generate detailed report
    from tests.evaluation.generate_report import ReportGenerator
    generator = ReportGenerator(
        summary=summary,
        all_results=orchestrator.all_results,
        output_dir=orchestrator.output_dir
    )
    report_path = generator.generate_markdown_report()
    
    print(f"\n📄 Detailed report generated: {report_path}")
    print(f"📊 Full results in: {orchestrator.output_dir}")
    print(f"📝 Logs in: {orchestrator.log_dir}")


if __name__ == "__main__":
    main()
