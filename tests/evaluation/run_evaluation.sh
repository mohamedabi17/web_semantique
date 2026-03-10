#!/bin/bash
# Quick Start Script for Evaluation Framework

echo "=================================================="
echo "🧪 Neuro-Symbolic KG Extraction - Evaluation Suite"
echo "=================================================="
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Virtual environment not detected. Activating..."
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f "../../../venv/bin/activate" ]; then
        source ../../../venv/bin/activate
    else
        echo "❌ Virtual environment not found. Please create one first."
        exit 1
    fi
fi

echo "✅ Virtual environment active"
echo ""

# Check dependencies
echo "🔍 Checking dependencies..."
python3 -c "import numpy" 2>/dev/null || pip install numpy
echo "✅ Dependencies OK"
echo ""

# Run tests
echo "🚀 Starting evaluation..."
echo ""

cd "$(dirname "$0")/../.." || exit

python3 tests/evaluation/run_all_tests.py "$@"

EXIT_CODE=$?

echo ""
echo "=================================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Evaluation complete!"
    echo "📊 Check outputs in: tests/evaluation/outputs/"
    echo "📄 Read report: tests/evaluation/outputs/final_evaluation_report.md"
else
    echo "❌ Evaluation encountered errors"
    echo "📝 Check logs in: tests/evaluation/logs/"
fi
echo "=================================================="

exit $EXIT_CODE
