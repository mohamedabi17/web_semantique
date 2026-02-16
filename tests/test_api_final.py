#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test API Hugging Face - Méthode Serverless Inference
"""

import requests
import os

# API Serverless Inference (gratuite)
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
HF_TOKEN = os.getenv("HF_TOKEN", "your_huggingface_token_here")
HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

print("=" * 70)
print("🧪 TEST API HUGGING FACE - SERVERLESS INFERENCE")
print("=" * 70)

# Test 1: Vérification du modèle
print("\n📌 TEST 1: Vérifier si le modèle est accessible")
print(f"   URL: {API_URL}")

try:
    # Requête GET pour vérifier le modèle
    response = requests.get("https://huggingface.co/api/models/mistralai/Mistral-7B-Instruct-v0.2", timeout=10)
    if response.status_code == 200:
        print("   ✅ Modèle trouvé sur Hugging Face")
    else:
        print(f"   ⚠️  Code: {response.status_code}")
except Exception as e:
    print(f"   ⚠️  Erreur vérification: {e}")

# Test 2: Appel API simple
print("\n📌 TEST 2: Appel API avec prompt simple")

prompt = "Bonjour"
payload = {
    "inputs": prompt,
    "parameters": {
        "max_new_tokens": 20,
        "temperature": 0.7
    }
}

print(f"   Prompt: '{prompt}'")
print("   🔄 Envoi requête...\n")

try:
    response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
    
    print(f"   📡 Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("   ✅ SUCCÈS!")
        print(f"   Type réponse: {type(result)}")
        print(f"   Contenu: {result}")
        
        if isinstance(result, list) and len(result) > 0:
            print(f"\n   📝 Texte généré: {result[0].get('generated_text', 'N/A')}")
            
    elif response.status_code == 503:
        print("   ⚠️  Modèle en cours de chargement")
        print("   💡 Attendez 20 secondes et réessayez")
        
    elif response.status_code == 401:
        print("   ❌ Token invalide ou expiré")
        print("   💡 Vérifiez votre token sur https://huggingface.co/settings/tokens")
        
    else:
        print(f"   ❌ Erreur {response.status_code}")
        print(f"   Message: {response.text[:300]}")
        
except requests.exceptions.Timeout:
    print("   ⏱️  Timeout (>30s)")
except Exception as e:
    print(f"   ❌ Exception: {type(e).__name__}: {str(e)[:150]}")

# Test 3: Extraction de relation
print("\n📌 TEST 3: Extraction de relation (cas d'usage réel)")

prompt_relation = "Marie Curie teaches at University of Paris. What is the relation? Answer with one word: teaches"
payload_relation = {
    "inputs": prompt_relation,
    "parameters": {
        "max_new_tokens": 5,
        "temperature": 0.1
    }
}

print(f"   Prompt: '{prompt_relation[:60]}...'")
print("   🔄 Envoi requête...\n")

try:
    response = requests.post(API_URL, headers=HEADERS, json=payload_relation, timeout=30)
    
    print(f"   📡 Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("   ✅ SUCCÈS!")
        if isinstance(result, list) and len(result) > 0:
            text = result[0].get('generated_text', '')
            print(f"   📝 Réponse: {text}")
    else:
        print(f"   ⚠️  Code: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Erreur: {str(e)[:100]}")

print("\n" + "=" * 70)
print("🏁 FIN DES TESTS")
print("=" * 70)

print("\n💡 CONSEILS:")
print("   - Si 503: Attendez que le modèle se charge (~20s)")
print("   - Si 401: Vérifiez votre token HF")
print("   - Si 429: Rate limit atteint, attendez 1 minute")
print("   - Modèle gratuit mais peut être lent lors du premier appel")
