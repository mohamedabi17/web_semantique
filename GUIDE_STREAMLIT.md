# 🌐 Guide d'Utilisation - Interface Web Streamlit

## 🚀 Démarrage Rapide

### Méthode 1 : Script de lancement (Recommandé)
```bash
./run_streamlit.sh
```

### Méthode 2 : Commande manuelle
```bash
source venv/bin/activate
streamlit run app_streamlit.py
```

**➡️ L'interface s'ouvre automatiquement sur : http://localhost:8501**

---

## 📖 Utilisation de l'Interface

### 1️⃣ Sélectionner ou Saisir un Texte

**Option A : Exemples Prédéfinis**
- Choisissez un exemple dans le menu déroulant
- 3 exemples fournis :
  - Professeur à l'université
  - Collaboration de chercheurs
  - Étudiant en Master

**Option B : Texte Personnalisé**
- Sélectionnez "Texte personnalisé"
- Saisissez votre propre texte dans la zone de texte

**💡 Conseils pour de meilleurs résultats :**
- Mentionnez des **noms complets** de personnes
- Ajoutez des **organisations** ou **lieux**
- Utilisez des **verbes d'action** (enseigne, travaille, étudie, collabore)

---

### 2️⃣ Générer le Graphe

Cliquez sur le bouton **"🚀 Générer le Graphe RDF"**

**Processus (barre de progression) :**
1. 📊 Extraction des entités avec spaCy (NER)
2. 🤖 Interrogation du LLM (Groq/Llama-3.1)
3. 📦 Génération des fichiers RDF (Turtle + XML)
4. 🎨 Création de la visualisation graphique

**Durée :** ~5-15 secondes selon la longueur du texte

---

### 3️⃣ Visualiser les Résultats

**📊 Graphe Visuel (Colonne de droite)**
- Visualisation interactive du graphe de connaissances
- Couleurs par type d'entité :
  - 🔵 Personnes (bleu)
  - 🟢 Lieux (vert)
  - 🟠 Organisations (orange)
  - 🟣 Documents (violet)
- **Téléchargement** : Bouton pour sauvegarder l'image PNG

**💾 Exports RDF (Onglets en bas)**

**Onglet 1 : 🐢 Turtle (.ttl)**
- Format RDF lisible par humains
- Syntaxe concise et claire
- ⬇️ Bouton de téléchargement disponible

**Onglet 2 : 📄 RDF/XML (.xml)**
- Format W3C standard
- Interopérabilité maximale
- ⬇️ Bouton de téléchargement disponible

**Onglet 3 : 📈 Statistiques**
- Nombre de personnes détectées
- Nombre d'organisations/lieux
- Nombre de relations extraites
- Classes OWL utilisées

---

## 🎛️ Barre Latérale (Sidebar)

### ℹ️ À propos
Informations sur l'architecture T-Box/A-Box et les 3 corrections académiques

### 📊 Statistiques
Métriques en temps réel :
- Nombre total de triplets RDF générés

### 🔧 Actions
- **🗑️ Nettoyer les fichiers** : Supprime tous les fichiers générés pour repartir de zéro

---

## 🎯 Exemples d'Utilisation

### Exemple 1 : Analyse d'une Publication Académique

**Texte :**
```
Jean Dupont et Marie Martin ont publié un article sur l'IA à Paris. 
Ils travaillent ensemble à l'INRIA.
```

**Résultats attendus :**
- ✅ 2 personnes détectées (Jean Dupont, Marie Martin)
- ✅ 2 lieux/organisations (Paris, INRIA)
- ✅ Relations : collaboratesWith, worksAt
- ✅ ~40-50 triplets RDF

### Exemple 2 : Parcours Étudiant

**Texte :**
```
Pierre Durand est étudiant en Master 2 à l'Université de Paris. 
Il étudie le Web Sémantique sous la direction du professeur Sophie Leclerc.
```

**Résultats attendus :**
- ✅ 2 personnes (Pierre Durand, Sophie Leclerc)
- ✅ 1 organisation (Université de Paris)
- ✅ Relations : studiesAt, teaches
- ✅ ~35-45 triplets RDF

---

## 🐛 Résolution de Problèmes

### Problème 1 : "❌ Veuillez entrer un texte à analyser !"
**Cause :** Zone de texte vide  
**Solution :** Saisissez ou sélectionnez un exemple de texte

### Problème 2 : "⚠️ Le script s'est exécuté mais certains fichiers peuvent être manquants"
**Cause :** Erreur dans le traitement NLP ou API  
**Solution :**
- Vérifiez que spaCy est installé : `python -m spacy download fr_core_news_sm`
- Vérifiez la clé API Groq dans `kg_extraction_semantic_web.py` (ligne 45)

### Problème 3 : Visualisation ne s'affiche pas
**Cause :** Fichier PNG non généré  
**Solution :** Cliquez sur "🗑️ Nettoyer les fichiers" dans la sidebar, puis régénérez

### Problème 4 : Timeout (> 60s)
**Cause :** Texte trop long ou API lente  
**Solution :** Réduisez la longueur du texte ou réessayez

### Problème 5 : Port 8501 déjà utilisé
**Cause :** Une autre instance Streamlit est en cours  
**Solution :**
```bash
# Tuer le processus existant
pkill -f streamlit
# Relancer
./run_streamlit.sh
```

---

## 🎨 Personnalisation

### Changer le Port

Éditez `.streamlit/config.toml` :
```toml
[server]
port = 8502  # Changer ici
```

### Modifier le Thème

Éditez `.streamlit/config.toml` :
```toml
[theme]
primaryColor = "#FF4B4B"      # Rouge
backgroundColor = "#0E1117"    # Fond sombre
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
```

---

## 📊 Performance et Limitations

### Performance
- ⚡ Extraction NER : ~1-2 secondes
- 🤖 Appels API Groq : ~200-400ms par relation
- 📦 Génération RDF : ~1 seconde
- 🎨 Visualisation : ~1-2 secondes

**Total : 5-15 secondes** selon la complexité du texte

### Limitations
- **Texte maximal** : ~1000 mots (recommandé : 100-300 mots)
- **Entités** : Fonctionne mieux avec 2-10 entités
- **Langue** : Français uniquement (modèle spaCy fr_core_news_sm)
- **API Groq** : Limite de 30 requêtes/minute (tier gratuit)

---

## 🚀 Fonctionnalités Avancées

### Mode Développement

Activer le mode "debug" dans Streamlit :
```bash
streamlit run app_streamlit.py --server.runOnSave true
```

### Partage de l'Application

**Option 1 : Réseau local**
```bash
streamlit run app_streamlit.py --server.address 0.0.0.0
# Accès via : http://<votre-ip>:8501
```

**Option 2 : Déploiement Streamlit Cloud**
1. Créer un compte sur [streamlit.io/cloud](https://streamlit.io/cloud)
2. Connecter votre dépôt GitHub
3. Déployer en 1 clic

---

## 📞 Support

**Questions :**
- Consultez le README.md principal
- Section Troubleshooting du README

**Ressources :**
- [Documentation Streamlit](https://docs.streamlit.io/)
- [Documentation Groq API](https://console.groq.com/docs)
- [Documentation spaCy](https://spacy.io/usage)

---

*Version 2.0 - Interface Web Streamlit - 16 janvier 2026*
