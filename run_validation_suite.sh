#!/bin/bash

# SUITE DE VALIDATION COMPLÈTE
# Tests des 7 corrections + fonctionnalités neuro-symboliques

echo "================================================================="
echo "SUITE DE VALIDATION - 17 CAS DE TEST"
echo "================================================================="

# Fonction pour extraire les résultats clés
run_test() {
    local test_num=$1
    local test_desc=$2
    local text=$3
    
    echo ""
    echo "================================================================="
    echo "TEST $test_num: $test_desc"
    echo "================================================================="
    echo "Texte: \"$text\""
    echo "-----------------------------------------------------------------"
    
    python3 kg_extraction_semantic_web.py --text "$text" 2>&1 | grep -E "(Entité détectée|Article retiré|Doublon supprimé|Entité rejetée|Relation détectée|Groq/Llama-3 a détecté|CORRECTION PROBLÈME|LOC→LOC|Garde-fou|Skip LLM|Triplets valides|Triplets rejetés|Triplets inférés|Chaîne transitive)"
    
    echo ""
}

# TEST 1
run_test "1" "Normalisation + Déduplication" \
    "La France appartient à l'Europe. France est un pays."

# TEST 2  
run_test "2" "Normalisation minuscules" \
    "paris se situe en france."

# TEST 3
run_test "3" "habite → locatedIn" \
    "mohamed habite à paris."

# TEST 4
run_test "4" "worksAt avec variantes temporelles" \
    "Sofia travaille chez AlgoTech. Paul travaillait à l'UVSQ. Marie a travaillé chez Microsoft."

# TEST 5
run_test "5" "habite → locatedIn (ville)" \
    "Ahmed habite à Pau."

# TEST 6
run_test "6" "collaboratesWith invalide (LOC↔ORG)" \
    "Paris collabore avec AlgoTech."

# TEST 7
run_test "7" "collaboratesWith valide (PER↔PER)" \
    "Marie collabore avec Paul."

# TEST 8
run_test "8" "LOC→LOC ville→ville REJET" \
    "Pau se situe à Paris."

# TEST 9
run_test "9" "Inférence transitive 2 niveaux" \
    "Versailles se trouve dans les Yvelines. Les Yvelines sont en France."

# TEST 10
run_test "10" "habite + détection organisation" \
    "Sofia habite à Bayonne. AlgoTech est une entreprise."

# TEST 11 - CRITIQUE
run_test "11" "PROBLÈME 1: travaille+ville → locatedIn" \
    "Sofia travaille à Bayonne."

# TEST 12
run_test "12" "travaille+organisation → worksAt" \
    "Sofia travaille chez AlgoTech."

# TEST 13
run_test "13" "Inférence transitive 3 niveaux" \
    "Paul habite à Versailles. Versailles est dans les Yvelines. Les Yvelines sont en France."

# TEST 14
run_test "14" "teachesSubject (TOPIC)" \
    "Marie enseigne la physique."

# TEST 15
run_test "15" "teaches (lieu/organisation)" \
    "Marie enseigne à l'Université de Bordeaux."

# TEST 16
run_test "16" "author (personne→document)" \
    "Zoubida Kedad a écrit un cours de Web Sémantique."

# TEST 17 - FULL PIPELINE
run_test "17" "FULL PIPELINE COMPLET" \
    "Sofia habite à Bayonne. Bayonne se situe dans les Pyrénées-Atlantiques. Les Pyrénées-Atlantiques sont en France. Sofia travaille chez DataAlgo. Elle collabore avec Paul. Paul enseigne la physique à l'Université de Pau."

echo ""
echo "================================================================="
echo "FIN DE LA SUITE DE VALIDATION"
echo "================================================================="
