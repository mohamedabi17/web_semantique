#!/bin/bash
# 🧪 Script de test de tous les cas de généralisation

echo "🧪 TESTS DE GÉNÉRALISATION DU PIPELINE"
echo "======================================"
echo ""

TOTAL=0
SUCCESS=0
FAILED=0

for file in tests/test_cases/cas_*.txt; do
    TOTAL=$((TOTAL + 1))
    
    cas_name=$(basename "$file" .txt)
    echo "📝 Test $TOTAL: $cas_name"
    echo "   Texte: $(cat "$file")"
    echo ""
    
    # Exécuter le pipeline
    output=$(python3 kg_extraction_semantic_web.py < "$file" 2>&1)
    
    # Vérifier si des entités ont été détectées
    entites=$(echo "$output" | grep -c "✓.*→")
    relations=$(echo "$output" | grep -c "🤖.*--\[")
    
    echo "   📊 Résultats:"
    echo "      • Entités détectées: $entites"
    echo "      • Relations proposées: $relations"
    
    # Vérifier les erreurs
    errors=$(echo "$output" | grep -c "❌\|Error\|Traceback")
    
    if [ $errors -eq 0 ] && [ $entites -gt 0 ]; then
        echo "   ✅ TEST RÉUSSI"
        SUCCESS=$((SUCCESS + 1))
    else
        echo "   ❌ TEST ÉCHOUÉ"
        FAILED=$((FAILED + 1))
        
        # Afficher les erreurs si présentes
        if [ $errors -gt 0 ]; then
            echo "   🔍 Erreurs détectées:"
            echo "$output" | grep -E "❌|Error|Traceback" | head -5
        fi
    fi
    
    echo ""
    echo "---"
    echo ""
done

echo ""
echo "======================================"
echo "📊 RÉSUMÉ DES TESTS"
echo "======================================"
echo "Total de tests : $TOTAL"
echo "Réussis        : $SUCCESS ✅"
echo "Échecs         : $FAILED ❌"
echo "Taux de succès : $((SUCCESS * 100 / TOTAL))%"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 TOUS LES TESTS SONT PASSÉS !"
else
    echo "⚠️  Certains tests ont échoué. Vérifiez les logs ci-dessus."
fi
