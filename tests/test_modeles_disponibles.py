#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test avec modèle gratuit accessible - Meta Llama ou alternatives
"""

from huggingface_hub import InferenceClient
import os

HF_TOKEN = os.getenv("HF_TOKEN", "your_huggingface_token_here")

print("=" * 70)
print("🧪 TEST MODÈLES GRATUITS DISPONIBLES")
print("=" * 70)

# Liste de modèles à tester
models = [
    "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "meta-llama/Llama-2-7b-chat-hf",
    "HuggingFaceH4/zephyr-7b-beta",
    "google/flan-t5-large",
    "microsoft/phi-2"
]

client = InferenceClient(token=HF_TOKEN)

for model_name in models:
    print(f"\n🤖 Test: {model_name}")
    
    messages = [{
        "role": "user",
        "content": "What is 2+2? Answer with just the number."
    }]
    
    try:
        response = client.chat_completion(
            messages=messages,
            model=model_name,
            max_tokens=10
        )
        answer = response.choices[0].message.content
        print(f"   ✅ FONCTIONNE! Réponse: {answer}")
        print(f"   👉 Utilisez ce modèle: {model_name}")
        break
    except Exception as e:
        error_msg = str(e)[:150]
        print(f"   ❌ Non disponible: {error_msg}")

print("\n" + "=" * 70)
