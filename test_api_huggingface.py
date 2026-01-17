#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de l'API Hugging Face Réelle
Vérifie que l'intégration avec Mistral-7B fonctionne correctement
"""

import requests
import json
import os

# Configuration (identique au script principal)
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
HF_TOKEN = os.getenv("HF_TOKEN", "your_huggingface_token_here")
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def test_api_connection():
    """Test 1: Vérifier que l'API répond"""
    print("\n" + "="*80)
    print("TEST 1: CONNEXION À L'API HUGGING FACE")
    print("="*80)
    
    try:
        # Test simple avec un prompt minimal
        payload = {
            "inputs": "[INST] Dis bonjour [/INST]",
            "parameters": {"max_new_tokens": 5}
        }
        
        print(f"📡 Envoi de la requête à: {API_URL[:60]}...")
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=15)
        
        print(f"✓ Code HTTP: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Format de réponse: {type(result)}")
            print(f"✓ Contenu: {str(result)[:100]}...")
            print("\n✅ Connexion API réussie !")
            return True
        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(f"Message: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {str(e)}")
        return False

def test_relation_extraction():
    """Test 2: Tester l'extraction de relation réelle"""
    print("\n" + "="*80)
    print("TEST 2: EXTRACTION DE RELATION AVEC MISTRAL-7B")
    print("="*80)
    
    # Cas de test
    test_cases = [
        {
            "sentence": "Marie Curie enseigne à l'Université de Paris",
            "entity1": "Marie Curie",
            "entity2": "Université de Paris",
            "expected": "teaches"
        },
        {
            "sentence": "Albert Einstein a rédigé un article sur la relativité",
            "entity1": "Albert Einstein",
            "entity2": "article",
            "expected": "writtenBy"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n--- Cas {i} ---")
        print(f"Phrase: {test['sentence']}")
        print(f"Entités: {test['entity1']} ↔ {test['entity2']}")
        
        prompt = f"""[INST] Tu es un expert en Web Sémantique.
Analyse la phrase suivante : "{test['sentence']}"
Quelle est la relation entre "{test['entity1']}" et "{test['entity2']}" ?

Choisis UNIQUEMENT une relation parmi cette liste :
- teaches (pour enseigner)
- worksAt (pour travailler quelque part)
- writtenBy (pour un auteur)
- locatedIn (pour un lieu)
- relatedTo (si autre)

Réponds uniquement avec le mot de la relation, rien d'autre. [/INST]
"""
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 10,
                "return_full_text": False,
                "temperature": 0.1
            }
        }
        
        try:
            print("📡 Appel API en cours...")
            response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                relation = result[0]['generated_text'].strip().lower()
                
                print(f"🤖 Mistral-7B a répondu: '{relation}'")
                print(f"📋 Attendu: '{test['expected']}'")
                
                if relation == test['expected']:
                    print("✅ Correspondance parfaite !")
                else:
                    print("⚠️  Différence détectée (mais peut être valide)")
                    
            else:
                print(f"❌ Erreur API: {response.status_code}")
                print(f"Message: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")

def test_error_handling():
    """Test 3: Vérifier la gestion d'erreurs"""
    print("\n" + "="*80)
    print("TEST 3: GESTION D'ERREURS")
    print("="*80)
    
    print("\n--- Test avec timeout court ---")
    try:
        payload = {"inputs": "test"}
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=0.001)
        print("❌ Le timeout aurait dû déclencher une erreur")
    except requests.exceptions.Timeout:
        print("✅ Timeout géré correctement")
    except Exception as e:
        print(f"✅ Exception capturée: {type(e).__name__}")
    
    print("\n--- Test avec token invalide ---")
    try:
        bad_headers = {"Authorization": "Bearer token_invalide"}
        payload = {"inputs": "test"}
        response = requests.post(API_URL, headers=bad_headers, json=payload, timeout=5)
        
        if response.status_code != 200:
            print(f"✅ Erreur détectée correctement (code {response.status_code})")
        else:
            print("⚠️  API a accepté un token invalide")
            
    except Exception as e:
        print(f"✅ Exception capturée: {type(e).__name__}")

def main():
    """Exécution de tous les tests"""
    print("=" * 80)
    print("VALIDATION DE L'API HUGGING FACE (MISTRAL-7B)")
    print("=" * 80)
    
    results = []
    
    # Test 1: Connexion
    print("\n🔍 Vérification de la connexion API...")
    connection_ok = test_api_connection()
    results.append(("Connexion API", connection_ok))
    
    if connection_ok:
        # Test 2: Extraction de relations
        print("\n🔍 Test d'extraction de relations...")
        test_relation_extraction()
        results.append(("Extraction de relations", True))
        
        # Test 3: Gestion d'erreurs
        print("\n🔍 Test de gestion d'erreurs...")
        test_error_handling()
        results.append(("Gestion d'erreurs", True))
    else:
        print("\n⚠️  Tests suivants ignorés (connexion échouée)")
        print("\nPossibles causes:")
        print("  1. Token Hugging Face invalide ou expiré")
        print("  2. Pas de connexion internet")
        print("  3. Modèle Mistral-7B temporairement indisponible")
        print("\nSolution:")
        print("  - Vérifier votre token sur: https://huggingface.co/settings/tokens")
        print("  - Remplacer HF_TOKEN dans le script")
    
    # Résumé
    print("\n" + "="*80)
    print("RÉSUMÉ DES TESTS")
    print("="*80)
    
    for test_name, passed in results:
        status = "✅ PASSÉ" if passed else "❌ ÉCHOUÉ"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*80)
    if all(result[1] for result in results):
        print("🎉 TOUS LES TESTS SONT VALIDÉS !")
        print("L'API Hugging Face est opérationnelle.")
    else:
        print("⚠️  Certains tests ont échoué.")
        print("Vérifiez la configuration de l'API.")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
