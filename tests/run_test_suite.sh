#!/bin/bash
# Script d'exécution de la suite de tests

cd /home/mohamedabi/Téléchargements/web_semantique

echo "================================================================================================"
echo "🧪 SUITE DE TESTS COMPLÈTE - ÉVALUATION ACADÉMIQUE"
echo "================================================================================================"
echo ""

# Activer environnement virtuel
source venv/bin/activate

# Créer répertoire de sortie
mkdir -p tests/outputs

# Fonction pour exécuter un test
run_test() {
    local test_id="$1"
    local test_name="$2"
    local input_text="$3"
    
    echo "────────────────────────────────────────────────────────────────────────────────────────────"
    echo "🧪 $test_id : $test_name"
    echo "────────────────────────────────────────────────────────────────────────────────────────────"
    echo "Input : $input_text"
    echo ""
    
    # Exécuter pipeline
    echo "$input_text" | python3 kg_extraction_semantic_web.py > "tests/outputs/${test_id}_output.txt" 2>&1
    
    # Vérifier résultat
    if [ -f "knowledge_graph.ttl" ]; then
        cp "knowledge_graph.ttl" "tests/outputs/${test_id}_graph.ttl"
        echo "✅ Graphe généré : tests/outputs/${test_id}_graph.ttl"
    else
        echo "❌ Échec génération graphe"
    fi
    
    echo ""
}

# 1️⃣ TESTS NER
echo "═══════════════════════════════════════════════════════════════════════════════════════════════"
echo "1️⃣ TESTS MODULE 0++ (NER HYBRIDE)"
echo "═══════════════════════════════════════════════════════════════════════════════════════════════"
echo ""

run_test "TEST_01" "Ambiguïté lexicale" "Apple publie un article sur RDF."

run_test "TEST_02" "Entités imbriquées" "Université Paris-Saclay enseigne le Web Sémantique."

run_test "TEST_03" "Entité hors ontologie" "Dr. Xyzzq enseigne Astro-Sémantique Quantique."

# 2️⃣ TESTS MAPPING
echo "═══════════════════════════════════════════════════════════════════════════════════════════════"
echo "2️⃣ TESTS MAPPING VERBES → OWL"
echo "═══════════════════════════════════════════════════════════════════════════════════════════════"
echo ""

run_test "TEST_04A" "Synonymes verbaux (donne)" "Zoubida Kedad donne un cours de RDF."

run_test "TEST_04B" "Synonymes verbaux (enseigne)" "Zoubida Kedad enseigne RDF."

run_test "TEST_05" "Verbe ambigu" "Zoubida Kedad travaille à Versailles."

# 3️⃣ TESTS DOMAIN/RANGE
echo "═══════════════════════════════════════════════════════════════════════════════════════════════"
echo "3️⃣ TESTS DOMAIN / RANGE"
echo "═══════════════════════════════════════════════════════════════════════════════════════════════"
echo ""

run_test "TEST_06" "Violation Domain" "Web Sémantique enseigne Zoubida Kedad."

run_test "TEST_07" "Violation Range" "Zoubida Kedad enseigne Versailles."

# 5️⃣ TESTS ROBUSTESSE LLM
echo "═══════════════════════════════════════════════════════════════════════════════════════════════"
echo "5️⃣ TESTS ROBUSTESSE LLM"
echo "═══════════════════════════════════════════════════════════════════════════════════════════════"
echo ""

run_test "TEST_11" "Hallucination LLM" "Le Web Sémantique est marié à RDF."

run_test "TEST_12" "Texte bruité" "Zoubida ... euh ... RDF ... Versailles ... enseigne ?"

echo "════════════════════════════════════════════════════════════════════════════════════════════════"
echo "✅ SUITE DE TESTS TERMINÉE"
echo "════════════════════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "📂 Résultats : tests/outputs/"
echo ""
