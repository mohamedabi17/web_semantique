#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Test Automatique pour la Démo
Vérifie que tous les modules sont prêts et connectés
"""

import sys
import os
from pathlib import Path
import subprocess

# Couleurs ANSI pour terminal
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_header(text):
    """Affiche un en-tête formaté"""
    print(f"\n{BOLD}{CYAN}{'='*80}{RESET}")
    print(f"{BOLD}{CYAN}{text.center(80)}{RESET}")
    print(f"{BOLD}{CYAN}{'='*80}{RESET}\n")

def print_success(text):
    """Affiche un message de succès"""
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    """Affiche un message d'erreur"""
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    """Affiche un avertissement"""
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_info(text):
    """Affiche une information"""
    print(f"{BLUE}ℹ️  {text}{RESET}")

def check_file_exists(filepath, description):
    """Vérifie l'existence d'un fichier"""
    if os.path.exists(filepath):
        print_success(f"{description} : {filepath}")
        return True
    else:
        print_error(f"{description} MANQUANT : {filepath}")
        return False

def check_python_module(module_name):
    """Vérifie qu'un module Python peut être importé"""
    try:
        __import__(module_name)
        print_success(f"Module Python '{module_name}' installé")
        return True
    except ImportError:
        print_error(f"Module Python '{module_name}' NON INSTALLÉ")
        return False

def test_module_import(module_file, class_name):
    """Teste l'import d'une classe depuis un module"""
    try:
        # Ajouter le répertoire courant au PYTHONPATH
        sys.path.insert(0, os.getcwd())
        
        # Importer le module
        module_name = module_file.replace('.py', '')
        module = __import__(module_name)
        
        # Vérifier que la classe existe
        if hasattr(module, class_name):
            print_success(f"Classe '{class_name}' disponible dans {module_file}")
            return True
        else:
            print_error(f"Classe '{class_name}' INTROUVABLE dans {module_file}")
            return False
    except Exception as e:
        print_error(f"Erreur lors de l'import de {module_file}: {str(e)}")
        return False

def run_module_test(module_file):
    """Exécute un module en mode test"""
    print_info(f"Test d'exécution de {module_file}...")
    try:
        result = subprocess.run(
            ["python3", module_file],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print_success(f"{module_file} s'exécute sans erreur")
            # Afficher les premières lignes de sortie
            output_lines = result.stdout.split('\n')[:5]
            for line in output_lines:
                if line.strip():
                    print(f"  {CYAN}│{RESET} {line}")
            return True
        else:
            print_error(f"{module_file} a renvoyé une erreur (code {result.returncode})")
            # Afficher l'erreur
            error_lines = result.stderr.split('\n')[:3]
            for line in error_lines:
                if line.strip():
                    print(f"  {RED}│{RESET} {line}")
            return False
    except subprocess.TimeoutExpired:
        print_warning(f"{module_file} a dépassé le timeout (10s)")
        return False
    except Exception as e:
        print_error(f"Erreur lors de l'exécution de {module_file}: {str(e)}")
        return False

def main():
    """Fonction principale de test"""
    print_header("TEST DE DÉMONSTRATION - VÉRIFICATION DES MODULES")
    print(f"{BOLD}Date du test :{RESET} {os.popen('date').read().strip()}")
    print(f"{BOLD}Répertoire :{RESET} {os.getcwd()}\n")
    
    total_tests = 0
    passed_tests = 0
    
    # ============================================================================
    # TEST 1 : Fichiers de modules principaux
    # ============================================================================
    
    print_header("TEST 1 : VÉRIFICATION DES FICHIERS")
    
    files_to_check = [
        ("kg_extraction_semantic_web.py", "Pipeline principal"),
        ("hybrid_ner_module.py", "Module 0++ (NER Hybride)"),
        ("owl_reasoning_engine.py", "Module 1 (OWL Reasoning)"),
        ("confidence_scorer.py", "Confidence System"),
        ("app_streamlit.py", "Interface Streamlit"),
    ]
    
    for filepath, description in files_to_check:
        total_tests += 1
        if check_file_exists(filepath, description):
            passed_tests += 1
    
    # ============================================================================
    # TEST 2 : Dépendances Python
    # ============================================================================
    
    print_header("TEST 2 : DÉPENDANCES PYTHON")
    
    dependencies = [
        "spacy",
        "rdflib",
        "requests",
        "streamlit",
        "networkx",
        "matplotlib"
    ]
    
    for dep in dependencies:
        total_tests += 1
        if check_python_module(dep):
            passed_tests += 1
    
    # Vérifier spaCy modèle
    total_tests += 1
    try:
        import spacy
        nlp = spacy.load("fr_core_news_sm")
        print_success(f"Modèle spaCy 'fr_core_news_sm' chargé (version {spacy.__version__})")
        passed_tests += 1
    except:
        print_error("Modèle spaCy 'fr_core_news_sm' NON DISPONIBLE")
        print_info("Installez avec : python3 -m spacy download fr_core_news_sm")
    
    # ============================================================================
    # TEST 3 : Import des classes principales
    # ============================================================================
    
    print_header("TEST 3 : IMPORT DES CLASSES")
    
    classes_to_test = [
        ("hybrid_ner_module.py", "HybridNERModule"),
        ("owl_reasoning_engine.py", "OWLReasoningEngine"),
        ("confidence_scorer.py", "ConfidenceScorer"),
    ]
    
    for module_file, class_name in classes_to_test:
        total_tests += 1
        if test_module_import(module_file, class_name):
            passed_tests += 1
    
    # ============================================================================
    # TEST 4 : Exécution standalone des modules
    # ============================================================================
    
    print_header("TEST 4 : EXÉCUTION STANDALONE")
    
    modules_to_run = [
        "hybrid_ner_module.py",
        "owl_reasoning_engine.py",
        "confidence_scorer.py",
    ]
    
    for module_file in modules_to_run:
        if os.path.exists(module_file):
            total_tests += 1
            if run_module_test(module_file):
                passed_tests += 1
    
    # ============================================================================
    # TEST 5 : Vérification de l'intégration dans le pipeline
    # ============================================================================
    
    print_header("TEST 5 : INTÉGRATION DANS LE PIPELINE")
    
    print_info("Vérification des imports dans kg_extraction_semantic_web.py...")
    
    total_tests += 1
    try:
        with open("kg_extraction_semantic_web.py", "r") as f:
            content = f.read()
            
            imports_found = []
            
            if "from hybrid_ner_module import HybridNERModule" in content:
                imports_found.append("HybridNERModule")
            
            if "from owl_reasoning_engine import OWLReasoningEngine" in content:
                imports_found.append("OWLReasoningEngine")
            
            if "from confidence_scorer import ConfidenceScorer" in content:
                imports_found.append("ConfidenceScorer")
            
            if len(imports_found) == 3:
                print_success(f"Tous les modules sont importés : {', '.join(imports_found)}")
                passed_tests += 1
            else:
                print_error(f"Imports manquants. Trouvés : {', '.join(imports_found)}")
    except Exception as e:
        print_error(f"Erreur lors de la vérification des imports : {str(e)}")
    
    # ============================================================================
    # TEST 6 : Fichiers de documentation
    # ============================================================================
    
    print_header("TEST 6 : DOCUMENTATION")
    
    docs_to_check = [
        ("README.md", "README principal"),
        ("IMPLEMENTATION_COMPLETE.md", "Documentation implémentation"),
        ("MODULE_0_COMPLETION.md", "Documentation Module 0++"),
        ("INTEGRATION_INSTRUCTIONS.md", "Instructions d'intégration"),
    ]
    
    for filepath, description in docs_to_check:
        total_tests += 1
        if check_file_exists(filepath, description):
            passed_tests += 1
    
    # ============================================================================
    # TEST 7 : Configuration Streamlit
    # ============================================================================
    
    print_header("TEST 7 : STREAMLIT")
    
    total_tests += 1
    try:
        with open("app_streamlit.py", "r") as f:
            content = f.read()
            
            if "check_modules_status" in content:
                print_success("Fonction check_modules_status() présente dans Streamlit")
                passed_tests += 1
            else:
                print_error("Fonction check_modules_status() MANQUANTE dans Streamlit")
    except Exception as e:
        print_error(f"Erreur lors de la vérification de Streamlit : {str(e)}")
    
    # ============================================================================
    # RÉSUMÉ FINAL
    # ============================================================================
    
    print_header("RÉSUMÉ DES TESTS")
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n{BOLD}Tests réussis : {passed_tests}/{total_tests}{RESET}")
    print(f"{BOLD}Taux de réussite : {success_rate:.1f}%{RESET}\n")
    
    if success_rate == 100:
        print_success("✨ TOUS LES MODULES SONT PRÊTS POUR LA DÉMO ✨")
        print_info("Vous pouvez lancer l'interface Streamlit avec : streamlit run app_streamlit.py")
        return 0
    elif success_rate >= 80:
        print_warning("⚠️  La plupart des modules sont prêts, mais certains éléments manquent")
        print_info("Vérifiez les erreurs ci-dessus avant la démo")
        return 1
    else:
        print_error("❌ TROP DE MODULES MANQUANTS - La démo ne peut pas fonctionner correctement")
        print_info("Installez les modules manquants et relancez ce test")
        return 2

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
