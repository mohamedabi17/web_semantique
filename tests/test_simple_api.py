#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Simple de l'API Hugging Face - Étape par étape
"""

import requests
import time
import os

# Configuration
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
HF_TOKEN = os.getenv("HF_TOKEN", "your_huggingface_token_here")
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

print("=" * 60)
print("🧪 TEST SIMPLE DE L'API HUGGING FACE")
print("=" * 60)

# TEST 1: Vérification du token
print("\n📌 TEST 1: Vérification du token")
print(f"   Token configuré: {HF_TOKEN[:10]}...{HF_TOKEN[-5:]}")
print("   ✅ Token présent\n")

# TEST 2: Connexion à l'API
print("📌 TEST 2: Connexion à l'API Hugging Face")
print(f"   URL: {API_URL}")

try:
    # Prompt simple
    prompt = "[INST] Dis bonjour en français. [/INST]"
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 50,
            "temperature": 0.1,
            "return_full_text": False
        }
    }
    
    print("   🔄 Envoi de la requête...")
    response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
    
    print(f"   📡 Code HTTP: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("   ✅ Connexion réussie!")
        print(f"   📝 Réponse: {result[0]['generated_text'][:100]}...")
    elif response.status_code == 503:
        print("   ⚠️  Modèle en chargement (attendre 20 secondes)...")
        time.sleep(20)
        print("   🔄 Nouvelle tentative...")
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Connexion réussie après rechargement!")
            print(f"   📝 Réponse: {result[0]['generated_text'][:100]}...")
        else:
            print(f"   ❌ Échec: {response.status_code}")
    else:
        print(f"   ❌ Erreur: {response.status_code}")
        print(f"   Message: {response.text[:200]}")
        
except requests.exceptions.Timeout:
    print("   ❌ Timeout (>30 secondes)")
except Exception as e:
    print(f"   ❌ Erreur: {str(e)[:100]}")

print("\n" + "=" * 60)

# TEST 3: Extraction de relation (comme dans le projet)
print("\n📌 TEST 3: Extraction de relation")
print("   Phrase: 'Marie Curie enseigne à l'Université de Paris'")
print("   Entités: Marie Curie ↔ Université de Paris")

try:
    prompt = """[INST] Tu es un expert en Web Sémantique.
Analyse la phrase suivante : "Marie Curie enseigne à l'Université de Paris"
Quelle est la relation entre "Marie Curie" et "Université de Paris" ?

Choisis UNIQUEMENT une relation parmi cette liste :
- teaches, worksAt, writtenBy, locatedIn, relatedTo

Réponds uniquement avec le mot de la relation. [/INST]"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 10,
            "temperature": 0.1,
            "return_full_text": False
        }
    }
    
    print("   🔄 Envoi de la requête...")
    response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        relation = result[0]['generated_text'].strip().lower()
        print(f"   ✅ Relation détectée: {relation}")
        print(f"   🎯 Marie Curie --[{relation}]--> Université de Paris")
    elif response.status_code == 503:
        print("   ⚠️  Modèle encore en chargement...")
    else:
        print(f"   ❌ Erreur: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Erreur: {str(e)[:100]}")

print("\n" + "=" * 60)
print("🏁 FIN DES TESTS")
print("=" * 60)
