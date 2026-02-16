#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test rapide pour valider les 4 exemples académiques
"""

import subprocess
import sys

tests = [
    {
        "nom": "TEST 1 : Emmanuel Macron - worksAt vs locatedIn",
        "texte": "Emmanuel Macron travaille au Palais de l'Élysée à Paris.",
        "attendu": [
            "Emmanuel Macron --[worksAt]--> Palais de l'Élysée",
            "Palais de l'Élysée --[locatedIn]--> Paris"
        ]
    },
    {
        "nom": "TEST 2 : Victor Hugo - Contrainte OWL",
        "texte": "Victor Hugo a écrit le roman Les Misérables.",
        "attendu": [
            "Victor Hugo --[author]--> Les Misérables",
            "Contrainte OWL : Les Misérables typé en ValidatedCourse"
        ]
    },
    {
        "nom": "TEST 3 : Albert Einstein - Priorité teaches",
        "texte": "Albert Einstein a enseigné la physique à l'Université de Princeton.",
        "attendu": [
            "Albert Einstein --[teaches]--> Université de Princeton"
        ]
    },
    {
        "nom": "TEST 4 : Satya Nadella - Chaîne multi-sauts",
        "texte": "Satya Nadella dirige Microsoft qui est situé à Redmond.",
        "attendu": [
            "Satya Nadella --[manages]--> Microsoft",
            "Microsoft --[locatedIn]--> Redmond"
        ]
    }
]

print("=" * 80)
print("VALIDATION DES 4 EXEMPLES ACADÉMIQUES")
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
            timeout=30
        )
        
        output = result.stdout + result.stderr
        
        # Vérifier les résultats attendus
        success = True
        for pattern in test['attendu']:
            if pattern in output:
                print(f"  ✅ {pattern}")
            else:
                print(f"  ❌ MANQUANT: {pattern}")
                success = False
        
        if success:
            print(f"  🎉 Test {i} RÉUSSI")
        else:
            print(f"  ⚠️  Test {i} ÉCHOUÉ")
            
    except subprocess.TimeoutExpired:
        print(f"  ❌ TIMEOUT après 30 secondes")
    except Exception as e:
        print(f"  ❌ ERREUR: {e}")

print("\n" + "=" * 80)
print("FIN DES TESTS")
print("=" * 80)
