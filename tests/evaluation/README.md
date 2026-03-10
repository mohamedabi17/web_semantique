# 🧪 Evaluation Framework for Neuro-Symbolic KG Extraction

Complete testing and evaluation infrastructure for the Knowledge Graph Extraction system.

## 📋 Overview

This framework provides comprehensive evaluation of the neuro-symbolic pipeline through:

- **100+ test scenarios** covering all edge cases
- **Automated pipeline execution** with result capture
- **Research-grade metrics** (Precision, Recall, F1, etc.)
- **Detailed failure analysis** and recommendations
- **Module-level performance breakdown**

## 🗂️ Structure

```
tests/evaluation/
├── run_all_tests.py          # Main test orchestrator
├── scenarios.py               # 100+ test scenarios
├── pipeline_runner.py         # Pipeline execution wrapper
├── metrics.py                 # Metrics calculator
├── generate_report.py         # Report generator
├── outputs/                   # Test results (JSON)
├── logs/                      # Detailed execution logs
└── README.md                  # This file
```

## ⚡ Quick Start

### Run All Tests

```bash
# From project root
python tests/evaluation/run_all_tests.py
```

### Run Specific Categories

```bash
# Test only entity recognition
python tests/evaluation/run_all_tests.py --categories entity_recognition

# Test multiple categories
python tests/evaluation/run_all_tests.py --categories entity_recognition relation_extraction
```

### Run Limited Tests

```bash
# Run only first 20 tests
python tests/evaluation/run_all_tests.py --max-tests 20
```

### Quiet Mode

```bash
# Suppress verbose output
python tests/evaluation/run_all_tests.py --quiet
```

## 📊 Output Files

After running tests, you'll find:

### 1. Summary JSON
`outputs/summary_YYYYMMDD_HHMMSS.json`

Contains aggregated metrics and results.

### 2. Individual Test Results
`outputs/TEST_ID_*.json`

Detailed results for each test scenario:
```json
{
  "scenario_id": "NER_001",
  "input_text": "...",
  "entities": [...],
  "relations": [...],
  "triples": [...],
  "errors": [],
  "execution_time": 0.45,
  "success": true,
  "metrics": {...}
}
```

### 3. Detailed Logs
`logs/TEST_ID.log`

Execution logs with expected vs actual comparisons.

### 4. Evaluation Report
`outputs/final_evaluation_report.md`

Comprehensive markdown report with:
- Executive summary
- Module-level analysis
- Failure analysis
- Recommendations

## 📈 Metrics Calculated

### Entity Recognition
- **Precision**: Correct entities / Total predicted
- **Recall**: Correct entities / Total expected
- **F1 Score**: Harmonic mean of precision & recall
- **Type Accuracy**: Correctly typed entities / Total matched

### Relation Extraction
- **Precision**: Correct relations / Total predicted
- **Recall**: Correct relations / Total expected
- **F1 Score**: Harmonic mean of precision & recall

### Ontology Validation
- **Domain Violations**: Invalid subject types
- **Range Violations**: Invalid object types
- **Violation Rate**: Violations / Total tests

### Performance
- **Avg Execution Time**: Mean time per test
- **Min/Max Time**: Fastest and slowest tests
- **Standard Deviation**: Time variance

### Quality
- **Hallucination Rate**: False positives / Total predicted
- **Success Rate**: Passed tests / Total tests

## 🎯 Test Categories

### 1. Entity Recognition (20 tests)
- Basic person/organization detection
- Technical concepts (RDF, OWL, etc.)
- Mixed entity types

### 2. Ambiguous Entities (15 tests)
- Apple (company vs fruit)
- Amazon (company vs river)
- Paris (person vs city)

### 3. Composite Entities (10 tests)
- Multi-word organizations
- Hyphenated names
- Complex entity structures

### 4. Relation Extraction (20 tests)
- teachesSubject
- teaches
- author
- worksAt
- manages

### 5. Domain Violations (10 tests)
- TOPIC cannot teach
- TOPIC cannot work
- Invalid subject types

### 6. Range Violations (10 tests)
- teachesSubject expects TOPIC, not LOC
- author expects DOCUMENT, not LOC

### 7. Noise Robustness (10 tests)
- Extra punctuation
- Uppercase text
- Hesitations and fillers

### 8. Unknown Entities (5 tests)
- Fictional person names
- Made-up organizations

### 9. Multi-Sentence (5 tests)
- Paragraph processing
- Coreference resolution

### 10. Long Text (3 tests)
- Academic paragraphs
- Multiple entities and relations

### 11. Edge Cases (10 tests)
- Empty input
- Single word
- Random text
- Only numbers
- Only special characters

### 12. Bilingual (5 tests)
- English text
- French-English mix

## 🔍 Example Usage

### Run and Analyze

```python
from tests.evaluation.run_all_tests import TestOrchestrator

# Initialize
orchestrator = TestOrchestrator("/path/to/project")

# Run tests
summary = orchestrator.run_all_tests(max_tests=50, verbose=True)

# Print summary
orchestrator.print_summary(summary)
```

### Custom Scenario

```python
from tests.evaluation.scenarios import TestScenario
from tests.evaluation.pipeline_runner import PipelineRunner

# Create custom scenario
scenario = TestScenario(
    scenario_id="CUSTOM_001",
    category="custom",
    input_text="Your custom test text here",
    description="Testing custom case",
    expected_entities=[
        {"text": "Entity Name", "type": "PER"}
    ]
)

# Run pipeline
runner = PipelineRunner("/path/to/project")
result = runner.run_pipeline(scenario.input_text, "CUSTOM_001")

# Check results
print(f"Success: {result['success']}")
print(f"Entities: {result['entities']}")
```

## 📊 Reading the Report

The generated `final_evaluation_report.md` contains:

### Executive Summary
- Overall metrics
- Key strengths and weaknesses

### Module Analysis
- **Module 0++**: Entity recognition performance
- **Module 1**: Relation extraction performance
- **Module 2**: Ontology validation results

### Failure Analysis
- Grouped by category
- Concrete examples
- Error patterns

### Recommendations
- Priority-ranked improvements
- Specific module targets
- Actionable suggestions

## 🎓 Grading Scale

| Grade | Score | Interpretation |
|-------|-------|----------------|
| A | 90-100% | Excellent |
| B | 80-89% | Good |
| C | 70-79% | Acceptable |
| D | 60-69% | Needs Improvement |
| F | <60% | Critical Issues |

## 🛠️ Advanced Usage

### Extend Test Scenarios

Edit `scenarios.py` and add new scenarios:

```python
scenarios.append(
    TestScenario(
        "YOUR_ID",
        "your_category",
        "Your test text",
        "Description",
        expected_entities=[...],
        expected_relations=[...]
    )
)
```

### Custom Metrics

Extend `metrics.py`:

```python
class MetricsCalculator:
    def calculate_custom_metric(self):
        # Your custom calculation
        return metric_value
```

### Report Customization

Modify `generate_report.py` to add new sections:

```python
def _generate_custom_section(self):
    return "## Custom Section\n\nYour content here\n"
```

## 📝 Interpreting Results

### High Entity Precision, Low Recall
**Problem**: System is conservative, missing many entities  
**Solution**: Expand EntityRuler patterns, lower confidence threshold

### Low Entity Precision, High Recall
**Problem**: System is aggressive, detecting false positives  
**Solution**: Increase confidence threshold, add filtering rules

### Type Accuracy < 90%
**Problem**: Entities detected but wrong type  
**Solution**: Review TECH_CONCEPT_KEYWORDS and HUMAN_NAME_INDICATORS

### High Domain/Range Violations
**Problem**: Relations created with invalid types  
**Solution**: Fix upstream entity typing, strengthen validation

### High Hallucination Rate
**Problem**: System inventing entities/relations  
**Solution**: Add entity grounding, implement stricter filtering

## 🚀 Performance Optimization

If tests run slowly:

1. **Reduce test count**: Use `--max-tests 20`
2. **Select categories**: Test specific areas only
3. **Increase timeout**: Modify `timeout` parameter in code
4. **Parallel execution**: Future feature (not yet implemented)

## 📧 Support

For issues or questions:
- Check logs in `logs/` directory
- Review individual test results in `outputs/`
- Examine the evaluation report

## 🎯 Success Criteria

Recommended targets:

- ✅ Entity F1 Score: **> 85%**
- ✅ Relation F1 Score: **> 75%**
- ✅ Type Accuracy: **> 90%**
- ✅ Success Rate: **> 80%**
- ✅ Hallucination Rate: **< 15%**
- ✅ Violation Rate: **< 10%**

---

**Framework Version:** 1.0  
**Compatible with:** Neuro-Symbolic KG Extraction v1.0  
**Last Updated:** 2026-03-04
