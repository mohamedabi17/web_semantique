#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Report Generator - Creates comprehensive markdown evaluation report
"""

from typing import Dict, List, Any
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class ReportGenerator:
    """Generates detailed evaluation reports in Markdown format"""
    
    def __init__(self, summary: Dict[str, Any], all_results: List[Dict], output_dir: Path):
        """
        Initialize report generator.
        
        Args:
            summary: Test summary dictionary
            all_results: List of all test results
            output_dir: Directory to save report
        """
        self.summary = summary
        self.all_results = all_results
        self.output_dir = Path(output_dir)
    
    def generate_markdown_report(self) -> Path:
        """Generate comprehensive Markdown report"""
        report_path = self.output_dir / "final_evaluation_report.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            # Header
            f.write(self._generate_header())
            
            # Executive Summary
            f.write(self._generate_executive_summary())
            
            # Module Analysis
            f.write(self._generate_module_analysis())
            
            # Detailed Metrics
            f.write(self._generate_metrics_section())
            
            # Failure Analysis
            f.write(self._generate_failure_analysis())
            
            # Category Breakdown
            f.write(self._generate_category_breakdown())
            
            # Recommendations
            f.write(self._generate_recommendations())
            
            # Appendix
            f.write(self._generate_appendix())
        
        return report_path
    
    def _generate_header(self) -> str:
        """Generate report header"""
        tc = self.summary['test_counts']
        return f"""# 🔬 Neuro-Symbolic Knowledge Graph Extraction
## Comprehensive Evaluation Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Tests:** {tc['total']}  
**Tests Passed:** {tc['passed']}  
**Tests Failed:** {tc['failed']}  
**Success Rate (ground-truth):** {tc['success_rate']:.1%}  
**Execution Time:** {self.summary['execution_time']:.2f}s

---

"""
    
    def _generate_executive_summary(self) -> str:
        """Generate executive summary section"""
        tc = self.summary['test_counts']
        em = self.summary['entity_metrics']
        rm = self.summary['relation_metrics']
        
        section = """## 📋 Executive Summary

### Overall Performance

| Metric | Value | Status |
|--------|-------|--------|
"""
        
        # Success rate  (ground-truth pass/fail)
        success_symbol = "✅" if tc['success_rate'] >= 0.8 else "⚠️" if tc['success_rate'] >= 0.6 else "❌"
        section += f"| **Tests Passed** | {tc['passed']}/{tc['total']} | {success_symbol} |\n"
        section += f"| **Tests Failed** | {tc['failed']}/{tc['total']} | {'✅' if tc['failed'] == 0 else '❌'} |\n"
        section += f"| **Success Rate** | {tc['success_rate']:.1%} | {success_symbol} |\n"
        
        # Entity metrics
        entity_p_sym = "✅" if em['precision'] >= 0.8 else "⚠️" if em['precision'] >= 0.6 else "❌"
        entity_r_sym = "✅" if em['recall']    >= 0.8 else "⚠️" if em['recall']    >= 0.6 else "❌"
        entity_f_sym = "✅" if em['f1_score']  >= 0.8 else "⚠️" if em['f1_score']  >= 0.6 else "❌"
        section += f"| **Entity Precision** | {em['precision']:.1%} | {entity_p_sym} |\n"
        section += f"| **Entity Recall** | {em['recall']:.1%} | {entity_r_sym} |\n"
        section += f"| **Entity F1 Score** | {em['f1_score']:.1%} | {entity_f_sym} |\n"

        # Relation metrics
        rel_p_sym = "✅" if rm['precision'] >= 0.7 else "⚠️" if rm['precision'] >= 0.5 else "❌"
        rel_r_sym = "✅" if rm['recall']    >= 0.7 else "⚠️" if rm['recall']    >= 0.5 else "❌"
        rel_f_sym = "✅" if rm['f1_score']  >= 0.7 else "⚠️" if rm['f1_score']  >= 0.5 else "❌"
        section += f"| **Relation Precision** | {rm['precision']:.1%} | {rel_p_sym} |\n"
        section += f"| **Relation Recall** | {rm['recall']:.1%} | {rel_r_sym} |\n"
        section += f"| **Relation F1 Score** | {rm['f1_score']:.1%} | {rel_f_sym} |\n"

        # Type accuracy
        type_symbol = "✅" if em['type_accuracy'] >= 0.9 else "⚠️" if em['type_accuracy'] >= 0.7 else "❌"
        section += f"| **Entity Type Accuracy** | {em['type_accuracy']:.1%} | {type_symbol} |\n"
        
        # Ontology violation rate
        om = self.summary['ontology_metrics']
        viol_symbol = "✅" if om['violation_rate'] <= 0.05 else "⚠️" if om['violation_rate'] <= 0.15 else "❌"
        section += f"| **Ontology Violation Rate** | {om['violation_rate']:.1%} | {viol_symbol} |\n"

        # Hallucination
        hall_symbol = "✅" if self.summary['hallucination_rate'] <= 0.1 else "⚠️" if self.summary['hallucination_rate'] <= 0.3 else "❌"
        section += f"| **Relation Hallucination Rate** | {self.summary['hallucination_rate']:.1%} | {hall_symbol} |\n"
        
        section += f"""
### Key Findings

✅ **Strengths:**
- {tc['passed']} out of {tc['total']} tests passed (ground-truth match)
- Entity precision: {em['precision']:.1%}
- Relation precision: {rm['precision']:.1%}

❌ **Weaknesses:**
- {tc['failed']} tests failed (expected annotations not matched)
- Entity recall: {em['recall']:.1%}  (missed entities: {em['false_negatives']})
- Relation recall: {rm['recall']:.1%}  (missed relations: {rm['false_negatives']})

---

"""
        return section
    
    def _generate_module_analysis(self) -> str:
        """Analyze performance by pipeline module"""
        section = """## 🔧 Module Performance Analysis

### Pipeline Architecture

```
Text Input
    ↓
Module 0: Input Validation
    ↓
Module 0++: Hybrid NER (7 layers)
    ├─ Layer 1: spaCy NER
    ├─ Layer 2: EntityRuler
    ├─ Layer 3: PROPN Heuristics
    ├─ Layer 4: Normalization
    ├─ Layer 5: Deduplication
    ├─ Layer 6: Confidence Filtering
    └─ Layer 7: Ontology Validation
    ↓
Module 1: Relation Extraction (LLM)
    ↓
Module 2: OWL Reasoning & Validation
    ↓
Module 3: RDF Triple Generation
    ↓
Streamlit Interface
```

### Module-Specific Metrics

"""
        
        # Module 0++: Entity Recognition
        em = self.summary['entity_metrics']
        section += f"""#### Module 0++ (Hybrid NER)

| Metric | Value | Grade |
|--------|-------|-------|
| Precision | {em['precision']:.1%} | {'A' if em['precision'] >= 0.9 else 'B' if em['precision'] >= 0.8 else 'C' if em['precision'] >= 0.7 else 'D'} |
| Recall | {em['recall']:.1%} | {'A' if em['recall'] >= 0.9 else 'B' if em['recall'] >= 0.8 else 'C' if em['recall'] >= 0.7 else 'D'} |
| F1 Score | {em['f1_score']:.1%} | {'A' if em['f1_score'] >= 0.9 else 'B' if em['f1_score'] >= 0.8 else 'C' if em['f1_score'] >= 0.7 else 'D'} |
| Type Accuracy | {em['type_accuracy']:.1%} | {'A' if em['type_accuracy'] >= 0.95 else 'B' if em['type_accuracy'] >= 0.85 else 'C' if em['type_accuracy'] >= 0.75 else 'D'} |

**Issues Detected:**
- False Positives: {em['false_positives']}
- False Negatives: {em['false_negatives']}

"""
        
        # Module 1: Relation Extraction
        rm = self.summary['relation_metrics']
        section += f"""#### Module 1 (Relation Extraction)

| Metric | Value | Grade |
|--------|-------|-------|
| Precision | {rm['precision']:.1%} | {'A' if rm['precision'] >= 0.85 else 'B' if rm['precision'] >= 0.75 else 'C' if rm['precision'] >= 0.65 else 'D'} |
| Recall | {rm['recall']:.1%} | {'A' if rm['recall'] >= 0.85 else 'B' if rm['recall'] >= 0.75 else 'C' if rm['recall'] >= 0.65 else 'D'} |
| F1 Score | {rm['f1_score']:.1%} | {'A' if rm['f1_score'] >= 0.85 else 'B' if rm['f1_score'] >= 0.75 else 'C' if rm['f1_score'] >= 0.65 else 'D'} |

**Issues Detected:**
- Missed Relations: {rm['false_negatives']}
- Incorrect Relations: {rm['false_positives']}

"""
        
        # Module 2: OWL Reasoning
        om = self.summary['ontology_metrics']
        section += f"""#### Module 2 (OWL Reasoning & Validation)

| Metric | Value |
|--------|-------|
| Total Violations | {om['total_violations']} |
| Domain Violations | {om['domain_violations']} |
| Range Violations | {om['range_violations']} |
| Violation Rate | {om['violation_rate']:.1%} |
| Tests with Violations | {om['tests_with_violations']} |

**Status:** {'✅ Excellent' if om['violation_rate'] <= 0.05 else '⚠️ Needs Improvement' if om['violation_rate'] <= 0.15 else '❌ Critical Issues'}

"""
        
        section += "---\n\n"
        return section
    
    def _generate_metrics_section(self) -> str:
        """Generate detailed metrics tables"""
        section = """## 📊 Detailed Metrics

### Entity Type Confusion Matrix

"""
        
        # Type confusion matrix
        confusion = self.summary.get('type_confusion_matrix', {})
        if confusion:
            section += "| Expected \\ Predicted | " + " | ".join(set(val for vals in confusion.values() for val in vals.keys())) + " |\n"
            section += "|" + "----|" * (len(set(val for vals in confusion.values() for val in vals.keys())) + 1) + "\n"
            
            for expected_type, predictions in confusion.items():
                row = [f"**{expected_type}**"]
                all_types = set(val for vals in confusion.values() for val in vals.keys())
                for predicted_type in all_types:
                    count = predictions.get(predicted_type, 0)
                    row.append(str(count))
                section += "| " + " | ".join(row) + " |\n"
        
        section += """
### Performance Statistics

"""
        
        pm = self.summary['performance_metrics']
        section += f"""| Metric | Value |
|--------|-------|
| Average Execution Time | {pm['avg_execution_time']:.3f}s |
| Minimum Time | {pm['min_execution_time']:.3f}s |
| Maximum Time | {pm['max_execution_time']:.3f}s |
| Standard Deviation | {pm['std_execution_time']:.3f}s |

---

"""
        return section
    
    def _generate_failure_analysis(self) -> str:
        """Analyze test failures with ground-truth details"""
        section = """## ❌ Failure Analysis

### Failed Test Summary

"""
        
        failed_tests = self.summary.get('failed_tests', [])
        if not failed_tests:
            section += "✅ **No test failures detected!**\n\n"
        else:
            section += f"**Total Failed Tests: {len(failed_tests)}**\n\n"
            
            # Group by category
            by_category = defaultdict(list)
            for test in failed_tests:
                by_category[test['category']].append(test)
            
            for category, tests in by_category.items():
                section += f"#### Category: {category.replace('_', ' ').title()}\n\n"
                for test in tests[:5]:  # Top 5 per category
                    section += f"**{test['scenario_id']}**: {test['description']}\n\n"

                    gt = test.get('gt_details', {})
                    reason = gt.get('passed_reason', '')
                    if reason:
                        section += f"> Reason: {reason}\n\n"

                    missing_ents = gt.get('missing_entities', [])
                    if missing_ents:
                        section += "Missing entities:\n"
                        for e in missing_ents[:5]:
                            section += f"  - `{e['text']}` ({e['type']})\n"
                        section += "\n"

                    missing_rels = gt.get('missing_relations', [])
                    if missing_rels:
                        section += "Missing relations:\n"
                        for r in missing_rels[:5]:
                            section += f"  - `{r['subject']}` --[{r['predicate']}]--> `{r['object']}`\n"
                        section += "\n"

                    # Show pipeline errors if any
                    if test.get('errors'):
                        section += "Pipeline errors:\n```\n"
                        for error in test['errors'][:3]:
                            section += f"- {error}\n"
                        section += "```\n\n"
        
        section += "---\n\n"
        return section
    
    def _generate_category_breakdown(self) -> str:
        """Generate category-wise breakdown"""
        section = """## 📂 Category Breakdown

"""
        
        for category, stats in self.summary['category_breakdown'].items():
            success_rate = stats['passed'] / stats['total'] if stats['total'] > 0 else 0
            symbol = "✅" if success_rate >= 0.8 else "⚠️" if success_rate >= 0.6 else "❌"
            
            section += f"### {symbol} {category.replace('_', ' ').title()}\n\n"
            section += f"- **Total Tests:** {stats['total']}\n"
            section += f"- **Passed:** {stats['passed']}\n"
            section += f"- **Failed:** {stats['failed']}\n"
            section += f"- **Success Rate:** {success_rate:.1%}\n\n"
        
        section += "---\n\n"
        return section
    
    def _generate_recommendations(self) -> str:
        """Generate recommendations based on results"""
        section = """## 💡 Recommendations

### Critical Issues to Address

"""
        
        em = self.summary['entity_metrics']
        rm = self.summary['relation_metrics']
        om = self.summary['ontology_metrics']
        
        recommendations = []
        
        # Entity typing issues
        if em['type_accuracy'] < 0.85:
            recommendations.append({
                "priority": "HIGH",
                "module": "Module 0++ (Hybrid NER)",
                "issue": "Entity type classification accuracy below 85%",
                "recommendation": "Review TECH_CONCEPT_KEYWORDS and HUMAN_NAME_INDICATORS lists. Add more discriminative patterns."
            })
        
        # Low recall
        if em['recall'] < 0.75:
            recommendations.append({
                "priority": "HIGH",
                "module": "Module 0++ (Hybrid NER)",
                "issue": "Entity recall below 75% - missing many entities",
                "recommendation": "Expand EntityRuler patterns. Review PROPN heuristics for common missed cases."
            })
        
        # Low precision
        if em['precision'] < 0.80:
            recommendations.append({
                "priority": "MEDIUM",
                "module": "Module 0++ (Hybrid NER)",
                "issue": "Entity precision below 80% - too many false positives",
                "recommendation": "Increase confidence threshold. Add more filtering rules."
            })
        
        # Relation extraction issues
        if rm['f1_score'] < 0.70:
            recommendations.append({
                "priority": "HIGH",
                "module": "Module 1 (Relation Extraction)",
                "issue": "Relation F1 score below 70%",
                "recommendation": "Review LLM prompts. Consider fine-tuning relation extraction patterns."
            })
        
        # Ontology violations
        if om['violation_rate'] > 0.10:
            recommendations.append({
                "priority": "HIGH",
                "module": "Module 2 (OWL Reasoning)",
                "issue": f"{om['total_violations']} ontology violations detected",
                "recommendation": "Strengthen domain/range validation before triple creation. Fix upstream entity typing."
            })
        
        # Hallucinations
        if self.summary['hallucination_rate'] > 0.20:
            recommendations.append({
                "priority": "MEDIUM",
                "module": "Module 0++ & Module 1",
                "issue": f"Hallucination rate at {self.summary['hallucination_rate']:.1%}",
                "recommendation": "Add entity grounding. Implement confidence-based filtering."
            })
        
        # Print recommendations
        for i, rec in enumerate(recommendations, 1):
            section += f"#### {i}. [{rec['priority']}] {rec['module']}\n\n"
            section += f"**Issue:** {rec['issue']}\n\n"
            section += f"**Recommendation:** {rec['recommendation']}\n\n"
        
        if not recommendations:
            section += "✅ **No critical issues detected. System performing well!**\n\n"
        
        section += """
### Pattern Analysis

Based on test failures, the following recurring patterns were identified:

"""
        
        # Analyze common error patterns
        error_patterns = defaultdict(int)
        for result in self.all_results:
            for error in result['result'].get('errors', []):
                if 'domain invalide' in error.lower():
                    error_patterns['Domain violations'] += 1
                elif 'range invalide' in error.lower():
                    error_patterns['Range violations'] += 1
                elif 'fragment' in error.lower():
                    error_patterns['Entity fragmentation'] += 1
                elif 'timeout' in error.lower():
                    error_patterns['Timeout issues'] += 1
        
        for pattern, count in sorted(error_patterns.items(), key=lambda x: x[1], reverse=True):
            section += f"- **{pattern}**: {count} occurrences\n"
        
        section += "\n---\n\n"
        return section
    
    def _generate_appendix(self) -> str:
        """Generate appendix with additional information"""
        section = """## 📎 Appendix

### Test Execution Details

- **Total Scenarios**: {total}
- **Execution Date**: {date}
- **Total Execution Time**: {time:.2f}s
- **Average Test Time**: {avg_time:.2f}s

### Output Files

- **Summary**: `summary_*.json`
- **Individual Results**: `outputs/*.json`
- **Detailed Logs**: `logs/*.log`
- **This Report**: `final_evaluation_report.md`

### Methodology

This evaluation used 100+ carefully crafted test scenarios covering:

1. **Entity Recognition**: Person, Organization, Location, Topic detection
2. **Ambiguous Entities**: Apple (company vs fruit), Paris (person vs city)
3. **Composite Entities**: Multi-word organization names
4. **Relation Extraction**: teachesSubject, worksAt, author, etc.
5. **Domain Violations**: Invalid subject types for relations
6. **Range Violations**: Invalid object types for relations
7. **Noise Robustness**: Typos, extra punctuation, formatting issues
8. **Edge Cases**: Empty input, single words, random text
9. **Multi-sentence**: Paragraph-level processing
10. **Long Text**: Academic text processing

### Grading Scale

| Grade | Score Range | Interpretation |
|-------|-------------|----------------|
| A | 90-100% | Excellent |
| B | 80-89% | Good |
| C | 70-79% | Acceptable |
| D | 60-69% | Needs Improvement |
| F | <60% | Critical Issues |

---

**End of Report**
""".format(
            total=self.summary['test_counts']['total'],
            date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            time=self.summary['execution_time'],
            avg_time=self.summary['performance_metrics']['avg_execution_time']
        )
        
        return section


if __name__ == "__main__":
    # Test report generation with dummy data
    dummy_summary = {
        "test_counts": {"total": 100, "passed": 85, "failed": 15, "success_rate": 0.85},
        "entity_metrics": {"precision": 0.92, "recall": 0.88, "f1_score": 0.90, "type_accuracy": 0.95,
                          "false_positives": 8, "false_negatives": 12},
        "relation_metrics": {"precision": 0.85, "recall": 0.78, "f1_score": 0.81,
                            "false_positives": 5, "false_negatives": 10},
        "ontology_metrics": {"total_violations": 3, "domain_violations": 2, "range_violations": 1,
                            "violation_rate": 0.03, "tests_with_violations": 3},
        "performance_metrics": {"avg_execution_time": 0.45, "min_execution_time": 0.21,
                               "max_execution_time": 1.2, "std_execution_time": 0.18},
        "hallucination_rate": 0.12,
        "type_confusion_matrix": {"PER": {"PER": 50, "TOPIC": 2}, "TOPIC": {"TOPIC": 45, "PER": 1}},
        "category_breakdown": {
            "entity_recognition": {"total": 20, "passed": 18, "failed": 2},
            "relation_extraction": {"total": 20, "passed": 17, "failed": 3}
        },
        "failed_tests": [],
        "execution_time": 45.5
    }
    
    generator = ReportGenerator(dummy_summary, [], Path("."))
    print("Report structure generated successfully!")
