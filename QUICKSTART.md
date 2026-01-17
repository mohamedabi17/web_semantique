# 🚀 Démarrage Rapide - 3 Minutes

## Installation Express

```bash
# 1. Activer l'environnement virtuel
source venv/bin/activate

# 2. Installer les dépendances (si pas déjà fait)
pip install -r requirements.txt

# 3. Télécharger le modèle français spaCy
python -m spacy download fr_core_news_sm
```

## Option A : Interface Web 🌐 (Recommandé)

```bash
./run_streamlit.sh
```

➡️ Ouvre automatiquement http://localhost:8501

## Option B : Ligne de Commande 💻

```bash
python kg_extraction_semantic_web.py
```

➡️ Génère 3 fichiers :
- `knowledge_graph.ttl` (Turtle)
- `knowledge_graph.xml` (RDF/XML)
- `graphe_connaissance.png` (Visualisation)

## Tests ✅

```bash
python test_corrections.py
```

## Résultat Attendu

✅ 73 triplets RDF générés  
✅ Groq API (Llama-3.1) fonctionnel  
✅ Relations détectées automatiquement  

---

**📖 Documentation complète :** [README.md](README.md)  
**🌐 Guide Streamlit :** [GUIDE_STREAMLIT.md](GUIDE_STREAMLIT.md)
