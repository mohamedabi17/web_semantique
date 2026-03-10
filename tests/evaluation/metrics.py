#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Metrics Calculator - Compute precision, recall, F1, and other evaluation metrics
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from collections import defaultdict


# ---------------------------------------------------------------------------
# Type normalisation table shared across all metric functions.
# Maps raw pipeline output types → canonical labels used in scenarios.
# ---------------------------------------------------------------------------
_TYPE_ALIASES: Dict[str, str] = {
    "PER":          "PER",
    "PERSON":       "PER",
    "ORG":          "ORG",
    "ORGANIZATION": "ORG",
    "LOC":          "LOC",
    "LOCATION":     "LOC",
    "GPE":          "LOC",
    "MISC":         "MISC",
    "TOPIC":        "TOPIC",
    "CONCEPT":      "TOPIC",
    "DOCUMENT":     "DOCUMENT",
    "DOC":          "DOCUMENT",
}


def _norm_type(t: str) -> str:
    """Return canonical entity type (upper-cased)."""
    return _TYPE_ALIASES.get(t.upper(), t.upper())


class MetricsCalculator:
    """Calculate research-grade evaluation metrics for KG extraction"""
    
    def __init__(self):
        self.results = []
    
    def add_result(self, expected: Dict[str, Any], actual: Dict[str, Any]):
        """Add a test result for metric calculation"""
        self.results.append({
            "expected": expected,
            "actual": actual
        })
    
    def calculate_entity_metrics(self) -> Dict[str, float]:
        """
        Calculate entity recognition metrics.

        Entity matching is case-insensitive on the text, and uses
        _norm_type() for type comparison so that e.g. "PERSON" == "PER".

        Returns:
            {
                "precision": float,
                "recall": float,
                "f1_score": float,
                "accuracy": float,
                "type_accuracy": float
            }
        """
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        type_correct = 0
        type_total = 0

        for result in self.results:
            expected_entities: set[tuple] = set()
            actual_entities:   set[tuple] = set()

            # Build sets of (text_lower, normalised_type) tuples
            if "expected_entities" in result["expected"]:
                for ent in result["expected"]["expected_entities"]:
                    expected_entities.add(
                        (ent["text"].strip().lower(), _norm_type(ent["type"]))
                    )

            if "entities" in result["actual"]:
                for ent in result["actual"]["entities"]:
                    actual_entities.add(
                        (ent["text"].strip().lower(), _norm_type(ent["type"]))
                    )

            # Token-overlap Jaccard match (≥0.7) with same type.
            # Strips honorifics before comparison so "Prof. Albert Einstein" ≈ "Albert Einstein".
            import re as _re
            def _token_set_m(text: str) -> set:
                cleaned = _re.sub(
                    r'\b(?:dr\.?|prof\.?|professeur|docteur|mr\.?|mrs\.?|mme\.?|monsieur|madame)\b',
                    '', text, flags=_re.IGNORECASE)
                cleaned = _re.sub(r'[^\w\s]', '', cleaned)
                return {w for w in cleaned.lower().split() if len(w) > 1}

            def _jaccard(a: str, b: str) -> float:
                ta, tb = _token_set_m(a), _token_set_m(b)
                if not ta or not tb:
                    return 0.0
                return len(ta & tb) / len(ta | tb)

            def _ent_covered_m(exp_key: tuple, preds: set) -> bool:
                exp_t, exp_type = exp_key
                if exp_key in preds:
                    return True
                for pred_t, pred_type in preds:
                    if pred_type == exp_type and _jaccard(exp_t, pred_t) >= 0.7:
                        return True
                return False

            def _ent_extra_m(pred_key: tuple, exps: set) -> bool:
                pred_t, pred_type = pred_key
                if pred_key in exps:
                    return False
                for exp_t, exp_type in exps:
                    if pred_type == exp_type and _jaccard(pred_t, exp_t) >= 0.7:
                        return False
                return True

            tp = sum(1 for k in expected_entities if _ent_covered_m(k, actual_entities))
            fp = sum(1 for k in actual_entities  if _ent_extra_m(k, expected_entities))
            fn = sum(1 for k in expected_entities if not _ent_covered_m(k, actual_entities))

            true_positives  += tp
            false_positives += fp
            false_negatives += fn

            # Check type accuracy for text-matched entities
            for exp_t, exp_type in expected_entities:
                for pred_t, pred_type in actual_entities:
                    if _jaccard(exp_t, pred_t) >= 0.7:
                        type_total += 1
                        if pred_type == exp_type:
                            type_correct += 1
                        break  # count each expected entity once

        # Calculate metrics
        precision = (
            true_positives / (true_positives + false_positives)
            if (true_positives + false_positives) > 0 else 0.0
        )
        recall = (
            true_positives / (true_positives + false_negatives)
            if (true_positives + false_negatives) > 0 else 0.0
        )
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0 else 0.0
        )
        accuracy = (
            true_positives / (true_positives + false_positives + false_negatives)
            if (true_positives + false_positives + false_negatives) > 0 else 0.0
        )
        type_accuracy = type_correct / type_total if type_total > 0 else 0.0

        return {
            "precision":       precision,
            "recall":          recall,
            "f1_score":        f1,
            "accuracy":        accuracy,
            "type_accuracy":   type_accuracy,
            "true_positives":  true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
        }
    
    def calculate_relation_metrics(self) -> Dict[str, float]:
        """
        Calculate relation extraction metrics.
        
        Returns:
            {
                "precision": float,
                "recall": float,
                "f1_score": float
            }
        """
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        
        for result in self.results:
            expected_relations = set()
            actual_relations = set()
            
            # Build sets of (subject, predicate, object) tuples
            if "expected_relations" in result["expected"]:
                for rel in result["expected"]["expected_relations"]:
                    expected_relations.add((
                        rel["subject"].lower(),
                        rel["predicate"].lower(),
                        rel["object"].lower()
                    ))
            
            if "relations" in result["actual"]:
                for rel in result["actual"]["relations"]:
                    actual_relations.add((
                        rel["subject"].lower(),
                        rel["predicate"].lower(),
                        rel["object"].lower()
                    ))
            
            # Calculate TP, FP, FN
            true_positives += len(expected_relations & actual_relations)
            false_positives += len(actual_relations - expected_relations)
            false_negatives += len(expected_relations - actual_relations)
        
        # Calculate metrics
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives
        }
    
    def calculate_ontology_metrics(self) -> Dict[str, Any]:
        """
        Calculate ontology violation metrics.
        
        Returns:
            {
                "total_violations": int,
                "domain_violations": int,
                "range_violations": int,
                "violation_rate": float
            }
        """
        total_tests = len(self.results)
        domain_violations = 0
        range_violations = 0
        
        for result in self.results:
            if "metrics" in result["actual"]:
                domain_violations += result["actual"]["metrics"].get("domain_violations", 0)
                range_violations += result["actual"]["metrics"].get("range_violations", 0)
        
        total_violations = domain_violations + range_violations
        violation_rate = total_violations / total_tests if total_tests > 0 else 0.0
        
        return {
            "total_violations": total_violations,
            "domain_violations": domain_violations,
            "range_violations": range_violations,
            "violation_rate": violation_rate,
            "tests_with_violations": sum(1 for r in self.results 
                                        if r["actual"].get("metrics", {}).get("domain_violations", 0) > 0 
                                        or r["actual"].get("metrics", {}).get("range_violations", 0) > 0)
        }
    
    def calculate_performance_metrics(self) -> Dict[str, float]:
        """
        Calculate performance metrics.
        
        Returns:
            {
                "avg_execution_time": float,
                "min_execution_time": float,
                "max_execution_time": float,
                "std_execution_time": float
            }
        """
        execution_times = [
            r["actual"].get("execution_time", 0.0) 
            for r in self.results
        ]
        
        if not execution_times:
            return {
                "avg_execution_time": 0.0,
                "min_execution_time": 0.0,
                "max_execution_time": 0.0,
                "std_execution_time": 0.0
            }
        
        return {
            "avg_execution_time": np.mean(execution_times),
            "min_execution_time": np.min(execution_times),
            "max_execution_time": np.max(execution_times),
            "std_execution_time": np.std(execution_times)
        }
    
    def calculate_success_rate(self) -> Dict[str, Any]:
        """
        Calculate overall success rate.

        'success' on each result is the ground-truth pass/fail flag set by
        the orchestrator *after* comparing predictions against expected
        annotations. It is NOT the raw pipeline exit-code flag.

        Returns:
            {
                "total_tests": int,
                "successful": int,
                "failed": int,
                "success_rate": float
            }
        """
        total = len(self.results)
        # result["actual"]["success"] is overwritten by ground-truth logic
        successful = sum(
            1 for r in self.results if r["actual"].get("success", False)
        )
        failed = total - successful

        return {
            "total_tests": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0.0,
        }
    
    def calculate_hallucination_rate(self) -> float:
        """
        Calculate hallucination rate for *relations*.

        Hallucination rate = hallucinated_relations / predicted_relations

        A predicted relation is "hallucinated" when it does not appear in
        the ground-truth expected_relations for that test case.

        Returns:
            Hallucination rate in [0.0, 1.0].
            Returns 0.0 when no relations were predicted across all tests.
        """
        total_predicted_relations = 0
        total_hallucinated_relations = 0

        for result in self.results:
            expected_rels: set[tuple] = set()
            predicted_rels: set[tuple] = set()

            if "expected_relations" in result["expected"]:
                for rel in result["expected"]["expected_relations"]:
                    expected_rels.add((
                        rel["subject"].strip().lower(),
                        rel["predicate"].strip().lower(),
                        rel["object"].strip().lower(),
                    ))

            if "relations" in result["actual"]:
                for rel in result["actual"]["relations"]:
                    predicted_rels.add((
                        rel["subject"].strip().lower(),
                        rel["predicate"].strip().lower(),
                        rel["object"].strip().lower(),
                    ))

            total_predicted_relations += len(predicted_rels)
            # Hallucinated = predicted but NOT in expected
            total_hallucinated_relations += len(predicted_rels - expected_rels)

        if total_predicted_relations == 0:
            return 0.0

        return total_hallucinated_relations / total_predicted_relations
    
    def calculate_entity_type_confusion_matrix(self) -> Dict[str, Dict[str, int]]:
        """
        Calculate confusion matrix for entity types.
        
        Returns:
            Dictionary mapping expected_type -> {predicted_type: count}
        """
        confusion = defaultdict(lambda: defaultdict(int))
        
        for result in self.results:
            expected_dict = {}
            
            # Build mapping of text_lower -> normalised expected type
            if "expected_entities" in result["expected"]:
                for ent in result["expected"]["expected_entities"]:
                    expected_dict[ent["text"].strip().lower()] = _norm_type(ent["type"])
            
            # Compare with actual
            if "entities" in result["actual"]:
                for ent in result["actual"]["entities"]:
                    text_lower = ent["text"].strip().lower()
                    if text_lower in expected_dict:
                        expected_type = expected_dict[text_lower]
                        actual_type   = _norm_type(ent["type"])
                        confusion[expected_type][actual_type] += 1
        
        return dict(confusion)
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Calculate all metrics and return comprehensive report"""
        return {
            "entity_metrics": self.calculate_entity_metrics(),
            "relation_metrics": self.calculate_relation_metrics(),
            "ontology_metrics": self.calculate_ontology_metrics(),
            "performance_metrics": self.calculate_performance_metrics(),
            "success_metrics": self.calculate_success_rate(),
            "hallucination_rate": self.calculate_hallucination_rate(),
            "type_confusion_matrix": self.calculate_entity_type_confusion_matrix()
        }


if __name__ == "__main__":
    # Test metrics calculator
    calculator = MetricsCalculator()
    
    # Add some dummy results
    calculator.add_result(
        expected={
            "expected_entities": [
                {"text": "Zoubida Kedad", "type": "PER"},
                {"text": "RDF", "type": "TOPIC"}
            ],
            "expected_relations": [
                {"subject": "Zoubida Kedad", "predicate": "teachesSubject", "object": "RDF"}
            ]
        },
        actual={
            "entities": [
                {"text": "Zoubida Kedad", "type": "PER"},
                {"text": "RDF", "type": "TOPIC"}
            ],
            "relations": [
                {"subject": "Zoubida Kedad", "predicate": "teachesSubject", "object": "RDF"}
            ],
            "success": True,
            "execution_time": 0.5,
            "metrics": {
                "domain_violations": 0,
                "range_violations": 0
            }
        }
    )
    
    metrics = calculator.get_all_metrics()
    print("Entity Metrics:")
    print(f"  Precision: {metrics['entity_metrics']['precision']:.2%}")
    print(f"  Recall: {metrics['entity_metrics']['recall']:.2%}")
    print(f"  F1 Score: {metrics['entity_metrics']['f1_score']:.2%}")
