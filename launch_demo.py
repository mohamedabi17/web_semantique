#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lanceur simplifié pour la démo Streamlit
Vérifie les modules et lance l'interface
"""

import os
import sys
import subprocess

def main():
    print("\n" + "="*80)
    print("🚀 LANCEMENT DEMO STREAMLIT - Web Sémantique".center(80))
    print("="*80 + "\n")
    
    # Vérification rapide
    print("📋 Vérification des modules...")
    
    modules = [
        "kg_extraction_semantic_web.py",
        "hybrid_ner_module.py",
        "owl_reasoning_engine.py",
        "confidence_scorer.py",
        "app_streamlit.py"
    ]
    
    all_present = True
    for module in modules:
        if os.path.exists(module):
            print(f"  ✅ {module}")
        else:
            print(f"  ❌ {module} MANQUANT")
            all_present = False
    
    if not all_present:
        print("\n❌ Certains modules sont manquants. Impossible de lancer la démo.")
        sys.exit(1)
    
    print("\n✅ Tous les modules sont présents")
    print("\n" + "="*80)
    print("🌐 Lancement de Streamlit...".center(80))
    print("="*80 + "\n")
    print("💡 L'interface s'ouvrira à l'adresse : http://localhost:8501")
    print("💡 Pour arrêter : Ctrl+C\n")
    
    # Lancer Streamlit
    try:
        subprocess.run(["streamlit", "run", "app_streamlit.py"])
    except KeyboardInterrupt:
        print("\n\n✅ Streamlit arrêté proprement")
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
