#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TESTS DE GÉNÉRALISATION DU PIPELINE
Test de la capacité du système à traiter différents cas d'usage
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

# Cas de test
TEST_CASES = [
    {
        "id": 1,
        "nom": "Académique Classique",
        "texte": "Alice Martin enseigne les bases de données à l'Université Paris-Saclay. Elle travaille aussi au CNRS.",
        "entites_attendues": ["Alice Martin", "bases de données", "Université Paris-Saclay", "CNRS"],
        "relations_attendues": ["teachesSubject", "teaches", "worksAt"],
        "types_attendus": {"PER": 1, "TOPIC": 1, "ORG": 2}
    },
    {
        "id": 2,
        "nom": "Auteur + Enseignement",
        "texte": "Mohamed Bennani a écrit un livre sur l'Intelligence Artificielle. Il enseigne à l'ENSIAS de Rabat.",
        "entites_attendues": ["Mohamed Bennani", "Intelligence Artificielle", "ENSIAS", "Rabat"],
        "relations_attendues": ["author", "teaches", "locatedIn"],
        "types_attendus": {"PER": 1, "TOPIC": 1, "ORG": 1, "PLACE": 1}
    },
    {
        "id": 3,
        "nom": "Technologies Sémantiques",
        "texte": "Jean Dupont a publié des articles sur SPARQL et OWL. Il dirige le laboratoire d'ontologies à Lyon.",
        "entites_attendues": ["Jean Dupont", "SPARQL", "OWL", "laboratoire", "Lyon"],
        "relations_attendues": ["author", "manages", "locatedIn"],
        "types_attendus": {"PER": 1, "DOCUMENT": 2, "ORG": 1, "PLACE": 1}
    },
    {
        "id": 4,
        "nom": "JSON-LD et Turtle",
        "texte": "Sophie Durand enseigne JSON-LD et Turtle à l'Université de Nantes. Elle collabore avec l'INRIA.",
        "entites_attendues": ["Sophie Durand", "JSON-LD", "Turtle", "Université de Nantes", "INRIA"],
        "relations_attendues": ["teachesSubject", "teaches", "collaboratesWith"],
        "types_attendus": {"PER": 1, "TOPIC": 2, "ORG": 2}
    },
    {
        "id": 5,
        "nom": "Hiérarchie Organisationnelle",
        "texte": "Pierre Rousseau dirige le département informatique. Il travaille à l'École Polytechnique de Paris.",
        "entites_attendues": ["Pierre Rousseau", "département informatique", "École Polytechnique", "Paris"],
        "relations_attendues": ["manages", "worksAt", "locatedIn"],
        "types_attendus": {"PER": 1, "ORG": 2, "PLACE": 1}
    },
    {
        "id": 6,
        "nom": "Relationnel Complexe",
        "texte": "Fatima El Amrani étudie la sémantique formelle à l'Université Mohammed V. Elle collabore avec des chercheurs de Casablanca.",
        "entites_attendues": ["Fatima El Amrani", "sémantique formelle", "Université Mohammed V", "Casablanca"],
        "relations_attendues": ["studiesAt", "relatedTo", "locatedIn"],
        "types_attendus": {"PER": 2, "TOPIC": 1, "ORG": 1, "PLACE": 1}
    },
    {
        "id": 7,
        "nom": "RDFS + Graphes",
        "texte": "Laura Sanchez a écrit des tutoriels sur RDFS et les graphes de connaissances. Elle enseigne à Barcelone.",
        "entites_attendues": ["Laura Sanchez", "RDFS", "graphes de connaissances", "Barcelone"],
        "relations_attendues": ["author", "teaches"],
        "types_attendus": {"PER": 1, "DOCUMENT": 1, "TOPIC": 1, "PLACE": 1}
    },
    {
        "id": 8,
        "nom": "Multi-Matières",
        "texte": "Thomas Bernard enseigne les mathématiques et la physique à l'Université de Toulouse. Il gère le département sciences.",
        "entites_attendues": ["Thomas Bernard", "mathématiques", "physique", "Université de Toulouse", "département sciences"],
        "relations_attendues": ["teachesSubject", "teaches", "manages"],
        "types_attendus": {"PER": 1, "TOPIC": 2, "ORG": 2}
    },
    {
        "id": 9,
        "nom": "Relations Géographiques",
        "texte": "Marie Leblanc travaille au laboratoire GREYC à Caen. Elle collabore avec l'Université de Versailles.",
        "entites_attendues": ["Marie Leblanc", "GREYC", "Caen", "Université de Versailles"],
        "relations_attendues": ["worksAt", "locatedIn", "collaboratesWith"],
        "types_attendus": {"PER": 1, "ORG": 2, "PLACE": 1}
    },
    {
        "id": 10,
        "nom": "Ontologie Médicale",
        "texte": "David Cohen a écrit une thèse sur l'ontologie médicale. Il enseigne à l'hôpital universitaire de Strasbourg et collabore avec le CHU.",
        "entites_attendues": ["David Cohen", "ontologie médicale", "hôpital universitaire", "Strasbourg", "CHU"],
        "relations_attendues": ["author", "teaches", "locatedIn", "collaboratesWith"],
        "types_attendus": {"PER": 1, "TOPIC": 1, "ORG": 2, "PLACE": 1}
    },
    {
        "id": 11,
        "nom": "Bilingue (Anglais)",
        "texte": "Emily Johnson teaches computer science at MIT. She published papers on semantic web and ontology.",
        "entites_attendues": ["Emily Johnson", "computer science", "MIT", "semantic web", "ontology"],
        "relations_attendues": ["teachesSubject", "teaches", "author"],
        "types_attendus": {"PER": 1, "TOPIC": 3, "ORG": 1}
    },
    {
        "id": 12,
        "nom": "Validation OWL Stricte (Rejet attendu)",
        "texte": "Le Web Sémantique enseigne à Paris.",
        "entites_attendues": ["Web Sémantique", "Paris"],
        "relations_attendues": [],  # Aucune relation valide (domain violation)
        "types_attendus": {"TOPIC": 1, "PLACE": 1},
        "rejet_attendu": True
    }
]


def sauvegarder_cas_tests():
    """Sauvegarde chaque cas dans un fichier texte séparé"""
    
    test_dir = Path(__file__).parent / "test_cases"
    test_dir.mkdir(exist_ok=True)
    
    for test_case in TEST_CASES:
        filename = test_dir / f"cas_{test_case['id']:02d}_{test_case['nom'].lower().replace(' ', '_')}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(test_case['texte'])
        
        print(f"✓ Cas {test_case['id']:02d} sauvegardé : {filename.name}")
    
    print(f"\n📁 {len(TEST_CASES)} cas de test créés dans : {test_dir}")
    
    # Créer aussi un fichier README
    readme_path = test_dir / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write("# 🧪 Cas de Test - Généralisation du Pipeline\n\n")
        f.write("## Liste des Cas\n\n")
        
        for test_case in TEST_CASES:
            f.write(f"### Cas {test_case['id']:02d} : {test_case['nom']}\n\n")
            f.write(f"**Texte** : `{test_case['texte']}`\n\n")
            f.write(f"**Entités attendues** : {', '.join(test_case['entites_attendues'])}\n\n")
            f.write(f"**Relations attendues** : {', '.join(test_case['relations_attendues'])}\n\n")
            
            if test_case.get('rejet_attendu'):
                f.write(f"**⚠️ Rejet attendu** : Violation de contrainte OWL (domain/range)\n\n")
            
            f.write("---\n\n")
    
    print(f"📄 README créé : {readme_path}")


def generer_commandes_test():
    """Génère les commandes pour tester chaque cas"""
    
    print("\n" + "="*80)
    print("🚀 COMMANDES DE TEST")
    print("="*80 + "\n")
    
    print("# Test individuel (exemple cas 1):")
    print('echo "Alice Martin enseigne les bases de données à l\'Université Paris-Saclay. Elle travaille aussi au CNRS." | python3 kg_extraction_semantic_web.py\n')
    
    print("# Test via fichiers:")
    for test_case in TEST_CASES[:3]:  # Afficher seulement les 3 premiers
        print(f"python3 kg_extraction_semantic_web.py < tests/test_cases/cas_{test_case['id']:02d}_*.txt")
    
    print("...\n")
    
    print("# Test tous les cas (boucle bash):")
    print("for file in tests/test_cases/cas_*.txt; do")
    print("    echo \"\\n=== Test: $file ===\"")
    print("    python3 kg_extraction_semantic_web.py < \"$file\" | grep -E '(✓|⚠️|❌)' ")
    print("done\n")


def afficher_matrice_test():
    """Affiche une matrice des cas de test"""
    
    print("\n" + "="*80)
    print("📊 MATRICE DES CAS DE TEST")
    print("="*80 + "\n")
    
    print(f"{'ID':<4} {'Nom':<30} {'Entités':<8} {'Relations':<10} {'Rejet':<8}")
    print("-" * 80)
    
    for test_case in TEST_CASES:
        nb_entites = len(test_case['entites_attendues'])
        nb_relations = len(test_case['relations_attendues'])
        rejet = "OUI ⚠️" if test_case.get('rejet_attendu') else "NON"
        
        print(f"{test_case['id']:<4} {test_case['nom']:<30} {nb_entites:<8} {nb_relations:<10} {rejet:<8}")
    
    print("-" * 80)
    print(f"TOTAL: {len(TEST_CASES)} cas de test\n")


if __name__ == "__main__":
    print("🧪 GÉNÉRATION DES CAS DE TEST - GÉNÉRALISATION DU PIPELINE\n")
    
    sauvegarder_cas_tests()
    afficher_matrice_test()
    generer_commandes_test()
    
    print("\n✅ Fichiers de test prêts !")
    print("\n💡 Utilisation dans Streamlit :")
    print("   → Copiez-collez les textes dans l'interface")
    print("   → Utilisez l'option 'Démo 1: Extraction Complète'\n")
