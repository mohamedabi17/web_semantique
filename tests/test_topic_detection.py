#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de la détection intelligente des TOPICS (matières académiques)
avec raffinement via Groq/Llama-3
"""

import subprocess
import sys

# Tests avec des matières académiques
tests = [
    {
        "nom": "TEST TOPIC 1 : Einstein - Physique",
        "texte": "Albert Einstein a enseigné la physique à l'Université de Princeton.",
        "attendu": [
            "Entité TOPIC détectée",
            "Physique",
            "teachesSubject"
        ]
    },
    {
        "nom": "TEST TOPIC 2 : Marie Curie - Chimie",
        "texte": "Marie Curie a enseigné la chimie à l'Université de Paris.",
        "attendu": [
            "Entité TOPIC détectée",
            "Chimie",
            "teachesSubject"
        ]
    },
    {
        "nom": "TEST TOPIC 3 : Zoubida Kedad - RDFS",
        "texte": "Zoubida Kedad enseigne RDFS à l'Université de Versailles.",
        "attendu": [
            "RDFS",
            "TOPIC"
        ]
    },
    {
        "nom": "TEST TOPIC 4 : Matières multiples",
        "texte": "Jean Dupont enseigne les mathématiques et l'informatique.",
        "attendu": [
            "mathématiques",
            "informatique",
            "TOPIC"
        ]
    }
]

print("=" * 80)
print("TEST DE DÉTECTION INTELLIGENTE DES TOPICS (MATIÈRES)")
print("=" * 80)

for i, test in enumerate(tests, 1):
    print(f"\n{test['nom']}")
    print("-" * 80)
    
    # Écrire le texte dans le fichier temporaire
    with open("texte_temp.txt", "w", encoding="utf-8") as f:
        f.write(test["texte"])
    
    # Lancer l'extraction
    try:
        result = subprocess.run(
            ["/home/mohamedabi/Téléchargements/web_semantique/venv/bin/python", 
             "kg_extraction_semantic_web.py"],
            capture_output=True,
            text=True,
            timeout=45,
            cwd="/home/mohamedabi/Téléchargements/web_semantique"
        )
        
        output = result.stdout + result.stderr
        
        # Vérifier les résultats attendus
        success = True
        for pattern in test['attendu']:
            if pattern in output:
                print(f"  ✅ Trouvé: {pattern}")
            else:
                print(f"  ❌ MANQUANT: {pattern}")
                success = False
        
        if success:
            print(f"  🎉 Test {i} RÉUSSI")
        else:
            print(f"  ⚠️  Test {i} ÉCHOUÉ - Voir les détails ci-dessous:")
            # Afficher les lignes pertinentes
            for line in output.split('\n'):
                if 'TOPIC' in line or 'teachesSubject' in line or 'Raffinement' in line:
                    print(f"    {line}")
            
    except subprocess.TimeoutExpired:
        print(f"  ❌ TIMEOUT après 45 secondes")
    except Exception as e:
        print(f"  ❌ ERREUR: {e}")

print("\n" + "=" * 80)
print("FIN DES TESTS TOPIC")
print("=" * 80)
