#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test avec la nouvelle API Hugging Face (router.huggingface.co)
"""

import requests
import os

# NOUVELLE URL (router.huggingface.co)
API_URL = "https://router.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
HF_TOKEN = os.getenv("HF_TOKEN", "your_huggingface_token_here")
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

print("=" * 60)
print("🧪 TEST AVEC NOUVELLE URL HUGGING FACE")
print("=" * 60)
print(f"\n📍 URL: {API_URL}")
print(f"🔑 Token: {HF_TOKEN[:10]}...{HF_TOKEN[-5:]}\n")

# Test simple
prompt = "[INST] Réponds uniquement par 'teaches' si tu comprends. [/INST]"
payload = {
    "inputs": prompt,
    "parameters": {
        "max_new_tokens": 10,
        "temperature": 0.1,
        "return_full_text": False
    }
}

print("🔄 Envoi de la requête...\n")

try:
    response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
    
    print(f"📡 Code HTTP: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ SUCCÈS!")
        print(f"📝 Réponse: {result[0]['generated_text']}")
    else:
        print(f"❌ Erreur {response.status_code}")
        print(f"Message: {response.text}")
        
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n" + "=" * 60)
