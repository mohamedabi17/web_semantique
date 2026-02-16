#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test API Hugging Face - Chat Completion (Mistral)
"""

from huggingface_hub import InferenceClient
import os

# Configuration
HF_TOKEN = os.getenv("HF_TOKEN", "your_huggingface_token_here")
MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

print("=" * 70)
print("🧪 TEST API HUGGING FACE - CHAT COMPLETION")
print("=" * 70)
print(f"\n🤖 Modèle: {MODEL}")
print(f"🔑 Token: {HF_TOKEN[:10]}...{HF_TOKEN[-5:]}\n")

# Créer le client
client = InferenceClient(token=HF_TOKEN)

# TEST 1: Simple question
print("📌 TEST 1: Question simple")
messages = [{"role": "user", "content": "Quelle est la capitale de la France? Réponds en un mot."}]

try:
    response = client.chat_completion(
        messages=messages,
        model=MODEL,
        max_tokens=10
    )
    answer = response.choices[0].message.content
    print(f"   ✅ Réponse: {answer}\n")
except Exception as e:
    print(f"   ❌ Erreur: {type(e).__name__}: {str(e)[:200]}\n")

# TEST 2: Extraction de relation
print("📌 TEST 2: Extraction de relation")

messages_relation = [{
    "role": "user",
    "content": """Tu es un expert en Web Sémantique.
Analyse la phrase suivante : "Marie Curie enseigne à l'Université de Paris"
Quelle est la relation entre "Marie Curie" et "Université de Paris" ?

Choisis UNIQUEMENT une relation parmi cette liste :
- teaches
- worksAt
- writtenBy
- locatedIn
- relatedTo

Réponds uniquement avec le mot de la relation, sans explication."""
}]

print("   Phrase: 'Marie Curie enseigne à l'Université de Paris'")
print("   🔄 Envoi de la requête...\n")

try:
    response = client.chat_completion(
        messages=messages_relation,
        model=MODEL,
        max_tokens=10,
        temperature=0.1
    )
    relation = response.choices[0].message.content.strip().lower()
    print(f"   ✅ Relation détectée: {relation}")
    print(f"   🎯 Marie Curie --[{relation}]--> Université de Paris\n")
except Exception as e:
    print(f"   ❌ Erreur: {type(e).__name__}: {str(e)[:200]}\n")

# TEST 3: Test avec plusieurs phrases
print("📌 TEST 3: Plusieurs extractions")

test_cases = [
    ("Albert Einstein works at ETH Zurich", "Albert Einstein", "ETH Zurich"),
    ("The book was written by Victor Hugo", "The book", "Victor Hugo"),
    ("Paris is located in France", "Paris", "France")
]

for i, (sentence, e1, e2) in enumerate(test_cases, 1):
    messages = [{
        "role": "user",
        "content": f"""Sentence: "{sentence}"
Entity 1: "{e1}"
Entity 2: "{e2}"

What semantic relation connects them? Choose ONLY from:
teaches, worksAt, writtenBy, locatedIn, relatedTo

Answer with one word only."""
    }]
    
    try:
        response = client.chat_completion(
            messages=messages,
            model=MODEL,
            max_tokens=5,
            temperature=0.1
        )
        relation = response.choices[0].message.content.strip()
        print(f"   {i}. {e1} --[{relation}]--> {e2}")
    except Exception as e:
        print(f"   {i}. ❌ Erreur: {type(e).__name__}")

print("\n" + "=" * 70)
print("🏁 FIN DES TESTS")
print("=" * 70)

print("\n💡 CONCLUSION:")
print("   ✅ Utilisez chat_completion() au lieu de text_generation()")
print("   ✅ Format messages: [{'role': 'user', 'content': '...'}]")
print("   ✅ Paramètres: model, max_tokens, temperature")
