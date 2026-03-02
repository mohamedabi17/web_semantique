#!/bin/bash
# Quick Test Script - Améliorations Neuro-Symboliques

echo "=============================================================================="
echo "TESTS RAPIDES - 4 AMÉLIORATIONS"
echo "=============================================================================="

# Test 1: Lemmes spaCy
echo ""
echo "[TEST 1] Détection de verbes par lemmes (habiter, travailler, enseigner)"
python3 kg_extraction_semantic_web.py --text "Mohamed habite à Paris mais travaille à l'UVSQ. Il enseigne les algorithmes." 2>&1 | grep "Lemme détecté"

# Test 2: Normalisation
echo ""
echo "[TEST 2] Normalisation des entités (paris → Paris)"
python3 kg_extraction_semantic_web.py --text "Mohamed habite à paris en france." 2>&1 | grep "Normalisée"

# Test 3: Validation LOC→LOC
echo ""
echo "[TEST 3] Validation LOC→LOC (rejeter relations invalides)"
python3 kg_extraction_semantic_web.py --text "Paris enseigne à Lyon." 2>&1 | grep "LOC→LOC"

# Test 4: Métadonnées Module 2
echo ""
echo "[TEST 4] Métadonnées prov:wasDerivedFrom 'Module2'"
python3 kg_extraction_semantic_web.py --text "L'UVSQ se situe à Versailles. Versailles est en france." > /dev/null 2>&1
grep "prov:wasDerivedFrom" knowledge_graph.ttl || echo "⚠️  Pas d'inférence (relations directes détectées)"

echo ""
echo "=============================================================================="
echo "✅ Tests terminés - Voir IMPROVEMENTS_SUMMARY.md pour détails"
echo "=============================================================================="
