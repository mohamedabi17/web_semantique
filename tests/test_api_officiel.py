#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test API Hugging Face avec bibliothèque officielle
"""

from huggingface_hub import InferenceClient
import os

# Configuration
HF_TOKEN = os.getenv("HF_TOKEN", "your_huggingface_token_here")
MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

print("=" * 70)
print("🧪 TEST API HUGGING FACE - BIBLIOTHÈQUE OFFICIELLE")
print("=" * 70)
print(f"\n🤖 Modèle: {MODEL}")
print(f"🔑 Token: {HF_TOKEN[:10]}...{HF_TOKEN[-5:]}\n")

# Créer le client
try:
    client = InferenceClient(model=MODEL, token=HF_TOKEN)
    print("✅ Client créé avec succès\n")
except Exception as e:
    print(f"❌ Erreur création client: {e}\n")
    exit(1)

# TEST 1: Génération de texte simple
print("📌 TEST 1: Génération de texte simple")
print("   Prompt: 'Bonjour, je suis'")

try:
    response = client.text_generation(
        "Bonjour, je suis",
        max_new_tokens=20,
        temperature=0.7
    )
    print(f"   ✅ Réponse: {response}")
except Exception as e:
    print(f"   ❌ Erreur: {type(e).__name__}: {str(e)[:150]}")

# TEST 2: Extraction de relation
print("\n📌 TEST 2: Extraction de relation (cas d'usage projet)")

prompt = """[INST] Tu es un expert en Web Sémantique.
Analyse la phrase suivante : "Marie Curie enseigne à l'Université de Paris"
Quelle est la relation entre "Marie Curie" et "Université de Paris" ?

Choisis UNIQUEMENT une relation parmi cette liste :
- teaches, worksAt, writtenBy, locatedIn, relatedTo

Réponds uniquement avec le mot de la relation. [/INST]"""

print(f"   Phrase analysée: 'Marie Curie enseigne à l'Université de Paris'")
print("   🔄 Envoi de la requête...\n")

try:
    response = client.text_generation(
        prompt,
        max_new_tokens=10,
        temperature=0.1
    )
    print(f"   ✅ Relation détectée: {response.strip()}")
    print(f"   🎯 Marie Curie --[{response.strip()}]--> Université de Paris")
except Exception as e:
    print(f"   ❌ Erreur: {type(e).__name__}: {str(e)[:200]}")

# TEST 3: Chat completion (alternative)
print("\n📌 TEST 3: Chat Completion (méthode alternative)")

messages = [
    {"role": "user", "content": "Quelle est la capitale de la France ? Réponds en un mot."}
]

try:
    response = client.chat_completion(
        messages=messages,
        max_tokens=10
    )
    answer = response.choices[0].message.content
    print(f"   ✅ Réponse: {answer}")
except Exception as e:
    print(f"   ⚠️  Chat non supporté: {type(e).__name__}")

print("\n" + "=" * 70)
print("🏁 FIN DES TESTS")
print("=" * 70)

print("\n💡 RÉSULTAT:")
if 'response' in locals():
    print("   ✅ L'API Hugging Face fonctionne correctement!")
    print("   ✅ Le modèle Mistral-7B est accessible")
    print("   ✅ Prêt pour l'intégration dans le projet principal")
else:
    print("   ⚠️  Vérifiez votre token et connexion internet")
