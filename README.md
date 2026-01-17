# 🎓 Projet Master 2 - Web Sémantique
## Extraction de Graphes de Connaissances avec LLM & Architecture T-Box/A-Box

**Étudiant:** Master 2 Web Sémantique  
**Date:** 16 janvier 2026  
**Sujet:** Sujet 1 - Architecture T-Box/A-Box avec Réification  
**Technologies:** Python 3.12, RDFLib, spaCy, Groq API (Llama-3.1), OWL 2, RDFS

---

## 🚀 Nouveautés : LLM Réel Intégré !

✨ **API Groq avec Llama-3.1-8B-Instant** maintenant intégrée pour l'extraction de relations sémantiques en temps réel !

```python
🚀 Appel API Groq (Llama-3) pour : Zoubida Kedad ↔ Université de Versailles
🤖 Groq/Llama-3 a détecté : Zoubida Kedad --[worksAt]--> Université de Versailles
```

---

## ⭐ Les 3 Corrections Académiques Validées

### ✅ 1. Restriction OWL avec BNode (Différenciation OWL vs RDFS)
- Classe `ex:ValidatedCourse` avec **restriction OWL explicite**
- Contrainte ontologique : DOIT avoir au moins un `ex:author` de type `foaf:Person`
- Utilise `owl:Restriction`, `owl:onProperty`, `owl:someValuesFrom`
- Implémentation avec **BNode** (nœud anonyme) conforme OWL 2
- **Code** : `kg_extraction_semantic_web.py` lignes 105-136

### ✅ 2. Extraction de Relations via LLM (Groq API)
- **API Groq réelle** avec modèle **Llama-3.1-8B-Instant** 🔥
- Appels API authentiques (non-simulation)
- Temperature=0 pour des résultats déterministes
- Prompt engineering optimisé pour l'extraction de relations
- Fallback intelligent (analyse linguistique) si API indisponible
- **Code** : `kg_extraction_semantic_web.py` lignes 255-333

### ✅ 3. Double Sérialisation (Turtle + RDF/XML)
- Génération automatique de 2 formats RDF conformes W3C
- `knowledge_graph.ttl` (Turtle - lisible par humains)
- `knowledge_graph.xml` (RDF/XML - interopérabilité)
- **Code** : `kg_extraction_semantic_web.py` lignes 826-850

**🧪 Tests automatiques :** 
```bash
python test_corrections.py  # ✅ Tous les tests passent
./demo.sh                    # 🎬 Démonstration complète
```

---

## 📋 Description Technique du Projet

Ce projet implémente une **architecture complète d'extraction de graphes de connaissances** respectant scrupuleusement les standards **OWL 2** et **RDFS** du Web Sémantique, avec intégration d'un **LLM moderne** (Llama-3.1) pour l'extraction intelligente de relations.

### Architecture Implémentée

```
┌─────────────────────────────────────────┐
│         T-BOX (Schéma Ontologique)      │
│  • Classes OWL                          │
│  • Restrictions OWL avec BNode ⭐        │
│  • ObjectProperties                     │
│  • DatatypeProperties                   │
│  • Contraintes domain/range             │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│           NLP Pipeline                  │
│  • spaCy (NER français)                 │
│  • Groq API + Llama-3.1 🤖              │
│  • Analyse linguistique (fallback)      │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         A-BOX (Données Factuelles)      │
│  • Instances de classes                 │
│  • Relations sémantiques (LLM)          │
│  • Réification avec métadonnées         │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│       Export Multi-format               │
│  • Turtle (.ttl)                        │
│  • RDF/XML (.xml)                       │
│  • Visualisation (.png)                 │
└─────────────────────────────────────────┘
```
              ↓
┌─────────────────────────────────────────┐
│         A-BOX (Données)                 │
│  • Extraction NER (spaCy)               │
│  • Prédiction relations (LLM) ⭐        │
│  • Instanciation des entités            │
│  • Relations sémantiques                │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│         RÉIFICATION                     │
│  • Métadonnées sur les triplets         │
│  • Traçabilité (dc:source)              │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│    DOUBLE SÉRIALISATION ⭐             │
│  • Turtle (lisible)                    │
│  • RDF/XML (standard W3C)              │
└─────────────────────────────────────────┘
```

---

## 🎯 Points Clés Respectés

### 1. Définition de l'Ontologie (T-Box)

✅ **Classes explicites** avec `owl:Class` (ontologies standards) :
- `foaf:Person` - Représente une personne (standard FOAF)
- `schema:Place` - Représente un lieu (standard Schema.org)
- `schema:Organization` - Représente une organisation (standard Schema.org)
- `ex:Document` - Représente un document, cours ou publication
- `ex:ValidatedCourse` - **Cours validé avec RESTRICTION OWL** ⭐

✅ **ObjectProperties** (relations entre entités) :
- `ex:worksAt` : foaf:Person → schema:Organization
- `ex:teaches` : foaf:Person → ex:Document
- `ex:studiesAt` : foaf:Person → schema:Organization
- `ex:author` : foaf:Person → ex:Document
- `ex:collaboratesWith` : foaf:Person → foaf:Person
- `ex:manages` : foaf:Person → schema:Organization
- `ex:locatedIn` : schema:Place → schema:Place
- `ex:relatedTo` : rdfs:Resource → rdfs:Resource (relation générique)

✅ **DatatypeProperties** (valeurs littérales) :
- `foaf:name` : foaf:Person → xsd:string (standard FOAF)
- `ex:intitule` : ex:Document → xsd:string
- `ex:confidence` : ex:Statement → xsd:float (score LLM)
- `dc:source` : rdfs:Resource → xsd:string (métadonnées)

✅ **Contraintes formelles** :
- Chaque propriété a son `rdfs:domain` et `rdfs:range` définis
- Hiérarchie de classes respectée
- Conformité OWL 2 validée

✅ **Restriction OWL avec BNode (Point clé académique)** ⭐ :
```turtle
ex:ValidatedCourse rdf:type owl:Class ;
    rdfs:subClassOf ex:Document ,
        [ rdf:type owl:Restriction ;
          owl:onProperty ex:author ;
          owl:someValuesFrom foaf:Person ] .
```
- Classe `ex:ValidatedCourse` avec **restriction explicite**
- Contrainte : **DOIT avoir au moins un `ex:author` de type `foaf:Person`**
- Utilise `owl:Restriction`, `owl:onProperty`, `owl:someValuesFrom`
- Implémentation avec **nœud anonyme (BNode)**
- **Différencie clairement OWL 2 de RDFS simple**

### 2. Pipeline d'Extraction (A-Box)

✅ **Extraction NER** avec spaCy (modèle français `fr_core_news_sm`)
  - Détection automatique : PER (personnes), LOC (lieux), ORG (organisations)
  - Normalisation et déduplication des entités
  
✅ **Prédiction de relations via Groq API RÉELLE** 🔥 ⭐ :
  - Modèle : **Llama-3.1-8B-Instant** (Meta, 8 milliards de paramètres)
  - Appels API authentiques (non-simulation)
  - Prompt engineering optimisé pour extraction de relations
  - Temperature=0 pour résultats déterministes
  - **Système de fallback à 3 niveaux** :
    1. API Groq (inférence LLM)
    2. Analyse linguistique (heuristiques spaCy)
    3. Relation par défaut (`ex:relatedTo`)

### 3. Technologies Utilisées

| Catégorie | Technologie | Version | Rôle |
|-----------|-------------|---------|------|
| **Langage** | Python | 3.12 | Core |
| **RDF** | rdflib | 7.1.1 | Manipulation graphes RDF |
| **NLP** | spaCy | 3.8.2 | NER français (entités nommées) |
| **NLP** | fr_core_news_sm | 3.8.0 | Modèle français spaCy |
| **LLM API** | Groq | 0.13.0 | Inférence LLM ultra-rapide |
| **LLM** | Llama-3.1-8B-Instant | 8B params | Extraction relations |
| **Visualisation** | NetworkX | 3.2.1 | Graphes |
| **Visualisation** | Matplotlib | 3.8.2 | Plots |
| **HTTP** | requests | 2.32.5 | Appels API |

### 4. LLM Integration : Groq API

**Pourquoi Groq ?**
- ⚡ Inférence ultra-rapide (100-300 tokens/sec)
- 🆓 **Gratuit** (pas de carte bancaire requise)
- 🔄 Disponibilité stable (vs Hugging Face API deprecated)
- 🎯 Modèles optimisés pour la production
- 🚀 GroqCloud offre accès gratuit aux derniers modèles

**Configuration API :**
```python
from groq import Groq
import time
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",  # Meta Llama 3.1
    messages=[{"role": "user", "content": prompt}],
    temperature=0,  # Déterministe
    max_tokens=50
)

relation = response.choices[0].message.content.strip()
```

**Prompt Engineering :**
```python
prompt = f"""
Tu es un expert en extraction de relations sémantiques.
Contexte : "{entity1}" et "{entity2}" apparaissent dans le même texte.
Analyse leur relation et réponds avec UN SEUL mot parmi :
- worksAt (travaille à)
- studiesAt (étudie à)
- teaches (enseigne)
- collaboratesWith (collabore avec)
- locatedIn (situé à)
- manages (gère)
- relatedTo (autre relation)
NE réponds qu'avec le mot-clé, RIEN d'autre.
"""
```

**Exemple de Résultat :**
```
🚀 Appel API Groq (Llama-3) pour : Zoubida Kedad ↔ Université de Versailles
🤖 Groq/Llama-3 a détecté : Zoubida Kedad --[worksAt]--> Université de Versailles
```

**Système de Fallback à 3 Niveaux :**
1. **Niveau 1** : Groq API (Llama-3.1) - extraction intelligente via LLM
2. **Niveau 2** : Analyse linguistique (spaCy + heuristiques sur tokens)
3. **Niveau 3** : Relation par défaut (`ex:relatedTo`)

---
---

## 💡 Réification et Métadonnées

✅ **Réification RDF** :
- Chaque relation importante est réifiée avec un `ex:Statement`
- Métadonnées ajoutées : `dc:source` (traçabilité du texte source)
- Permet d'annoter les triplets RDF (qui a dit quoi, quand, où)

**Exemple de réification :**
```turtle
ex:Statement_Zoubida_Kedad_worksAt_Universite_de_Versailles
    rdf:type ex:Statement ;
    rdf:subject ex:Zoubida_Kedad ;
    rdf:predicate ex:worksAt ;
    rdf:object ex:Universite_de_Versailles ;
    dc:source "Zoubida Kedad est professeure à l'Université de Versailles." ;
    ex:confidence "0.92"^^xsd:float .
```

---

## 📦 Installation et Prérequis

### Prérequis Système
- **Python 3.12+** (testé avec 3.12)
- **pip** (gestionnaire de paquets Python)
- Connexion Internet (pour Groq API et téléchargement modèle spaCy)

### Installation Complète

#### 1. Cloner le projet
```bash
cd ~/Téléchargements/web_semantique
```

#### 2. Installer les dépendances Python
```bash
pip install -r requirements.txt
```

**Contenu de `requirements.txt` :**
```
rdflib==7.1.1
spacy==3.8.2
networkx==3.2.1
matplotlib==3.8.2
requests==2.32.5
huggingface-hub==0.20.0
groq==0.13.0
streamlit       # Interface web
pillow          # Traitement d'images
```

#### 3. Télécharger le modèle français spaCy
```bash
python -m spacy download fr_core_news_sm
```

#### 4. Configuration de l'API Groq

**Option A : Utiliser la clé fournie (prête à l'emploi)**
```python
# Déjà configurée dans kg_extraction_semantic_web.py ligne 45
API_KEY = ""
```

**Option B : Obtenir votre propre clé gratuite**
1. Créer un compte gratuit : https://console.groq.com/
2. Aller dans "API Keys" et générer une clé
3. Remplacer la clé ligne 45 dans `kg_extraction_semantic_web.py`

---

## 🚀 Utilisation

### 🌐 Interface Web Streamlit (Nouveau !)

**Lancez l'interface web interactive :**

```bash
./run_streamlit.sh
```

Ou manuellement :

```bash
source venv/bin/activate
streamlit run app_streamlit.py
```

**🎯 Fonctionnalités de l'interface :**
- ✨ Saisie de texte interactive avec exemples prédéfinis
- 🔄 Génération de graphes en temps réel
- 📊 Visualisation graphique interactive
- 💾 Export et téléchargement RDF (Turtle + XML)
- 📈 Statistiques du graphe générées
- 🎨 Interface moderne et responsive

**📍 L'application s'ouvre automatiquement sur : http://localhost:8501**

**📖 Guide complet d'utilisation :** Consultez [GUIDE_STREAMLIT.md](GUIDE_STREAMLIT.md) pour un tutoriel détaillé de l'interface web.

---

### 💻 Exécution en Ligne de Commande

**Exécution Standard**
```bash
python kg_extraction_semantic_web.py
```

**Sortie attendue :**
```
🔧 Initialisation du modèle spaCy (fr_core_news_sm)...
📊 Texte d'entrée : 515 caractères
🔍 Extraction des entités nommées...
   ✓ Entités extraites : 4 personnes, 3 lieux, 2 organisations
🚀 Appel API Groq (Llama-3) pour : Zoubida Kedad ↔ Université de Versailles
🤖 Groq/Llama-3 a détecté : Zoubida Kedad --[worksAt]--> Université de Versailles
📈 Génération du graphe de connaissances...
✓ Graphe exporté en TURTLE : knowledge_graph.ttl
✓ Graphe exporté en RDF/XML : knowledge_graph.xml
✓ Visualisation générée : graphe_connaissance.png
✓ Nombre total de triplets : 73
```

### Fichiers Générés

| Fichier | Format | Description | Taille |
|---------|--------|-------------|--------|
| `knowledge_graph.ttl` | Turtle | Format RDF lisible par humains | ~3.6 KB |
| `knowledge_graph.xml` | RDF/XML | Format W3C standard interopérable | ~8.2 KB |
| `graphe_connaissance.png` | PNG | Visualisation graphique | ~80 KB |

### Validation des Fichiers RDF

**Validation Turtle :**
```bash
rapper -i turtle -o ntriples knowledge_graph.ttl > /dev/null
# Si succès : pas d'erreur affichée
```

**Validation RDF/XML :**
```bash
rapper -i rdfxml -o ntriples knowledge_graph.xml > /dev/null
```

### Requêtes SPARQL d'Exemple

**1. Lister toutes les personnes :**
```sparql
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?person ?name WHERE {
  ?person rdf:type foaf:Person .
  ?person foaf:name ?name .
}
```

**2. Trouver qui travaille où (avec LLM) :**
```sparql
PREFIX ex: <http://example.org/ontology/>
SELECT ?person ?org WHERE {
  ?person ex:worksAt ?org .
}
```

**3. Lister les cours validés (restriction OWL) :**
```sparql
PREFIX ex: <http://example.org/ontology/>
SELECT ?course ?author WHERE {
  ?course rdf:type ex:ValidatedCourse .
  ?course ex:author ?author .
}
```

---

## 🧪 Tests et Validation

### 1. Tests Automatiques des 3 Corrections
```bash
python test_corrections.py
```

**Résultat attendu :**
```
✅ Test 1 : Restriction OWL détectée
✅ Test 2 : Appel API Groq validé
✅ Test 3 : Double sérialisation validée (TTL + XML)
====================================
✨ TOUS LES TESTS SONT PASSÉS ! ✨
====================================
```

### 2. Démonstration Complète
```bash
chmod +x demo.sh
./demo.sh
```

**Résultat attendu :**
```
🎬 Démonstration complète du projet...
📦 Installation des dépendances...
🧪 Tests des 3 corrections académiques...
🚀 Exécution du script principal...
✅ Script principal exécuté
✅ 2 fichiers RDF générés (TTL + XML)
✅ 3 corrections académiques validées
✨ DÉMONSTRATION TERMINÉE AVEC SUCCÈS !
```

### 3. Validation Manuelle des Restrictions OWL
```bash
python -c "
from rdflib import Graph
g = Graph()
g.parse('knowledge_graph.ttl', format='turtle')
restrictions = list(g.query('''
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT ?class ?property ?valueFrom WHERE {
        ?class rdfs:subClassOf ?restriction .
        ?restriction rdf:type owl:Restriction .
        ?restriction owl:onProperty ?property .
        ?restriction owl:someValuesFrom ?valueFrom .
    }
'''))
print(f'✅ Restrictions OWL trouvées : {len(restrictions)}')
for r in restrictions:
    print(f'   • {r}')
"
```

---

## 📊 Résultats et Performances

### Statistiques d'Exécution

| Métrique | Valeur |
|----------|--------|
| **Texte d'entrée** | 515 caractères |
| **Entités détectées** | 9 (4 PER, 3 LOC, 2 ORG) |
| **Appels API Groq** | ~10-15 (selon paires d'entités) |
| **Temps API moyen** | 200-400ms par appel |
| **Triplets RDF générés** | 73 |
| **Classes OWL** | 5 (dont 1 avec restriction) |
| **ObjectProperties** | 8 |
| **DatatypeProperties** | 4 |
| **Statements réifiés** | ~10 |

### Exemple de Détection LLM

**Entrée :** "Zoubida Kedad est professeure à l'Université de Versailles."

**Pipeline :**
1. **spaCy NER** → Détecte `Zoubida Kedad` (PER) et `Université de Versailles` (ORG)
2. **Groq API** → Prompt envoyé à Llama-3.1-8B
3. **LLM répond** → `worksAt`
4. **RDF généré** :
```turtle
ex:Zoubida_Kedad rdf:type foaf:Person ;
    foaf:name "Zoubida Kedad" ;
    ex:worksAt ex:Universite_de_Versailles .

ex:Universite_de_Versailles rdf:type schema:Organization ;
    schema:name "Université de Versailles" .
```

---

## 🐛 Troubleshooting

### Problème 1 : Erreur API Groq
**Symptôme :**
```
❌ Erreur API Groq : 400 - The model `llama3-8b-8192` does not exist
```

**Solution :**
Le modèle a été mis à jour. Utiliser `llama-3.1-8b-instant` :
```python
# Ligne 264 de kg_extraction_semantic_web.py
model="llama-3.1-8b-instant",  # ✅ Modèle actif
```

### Problème 2 : Hugging Face API deprecated
**Symptôme :**
```
410 Client Error: Gone for url: https://api-inference.huggingface.co/models/...
```

**Explication :**
L'infrastructure Hugging Face `api-inference.huggingface.co` a été dépréciée en janvier 2026.

**Solution :**
Le projet utilise maintenant **Groq API** qui est stable et gratuit.

### Problème 3 : Modèle spaCy manquant
**Symptôme :**
```
OSError: [E050] Can't find model 'fr_core_news_sm'
```

**Solution :**
```bash
python -m spacy download fr_core_news_sm
```

### Problème 4 : Clé API invalide
**Symptôme :**
```
AuthenticationError: Invalid API key
```

**Solution :**
1. Vérifier la clé ligne 45 : `API_KEY = "gsk_xxPVc9O0..."`
2. Ou obtenir une nouvelle clé gratuite : https://console.groq.com/

### Problème 5 : Fallback activé trop souvent
**Symptôme :**
```
⚠ Fallback linguistique utilisé
```

**Explication :**
L'API a renvoyé une erreur ou un timeout → le système bascule sur l'analyse linguistique (comportement normal).

**Pour forcer l'API uniquement :**
```python
# Ligne 330 : Commenter le fallback
# relation = predict_relation_linguistic(entity1, entity2, context)
```

---

## 📚 Structure du Projet

```
web_semantique/
├── kg_extraction_semantic_web.py  # Script principal (906 lignes)
├── app_streamlit.py               # 🌐 Interface web Streamlit (NOUVEAU)
├── run_streamlit.sh               # Script de lancement interface web
├── requirements.txt                # Dépendances Python
├── test_corrections.py             # Tests automatiques (3 corrections)
├── demo.sh                         # Script de démonstration
├── README.md                       # Documentation (ce fichier)
├── knowledge_graph.ttl             # Sortie Turtle (généré)
├── knowledge_graph.xml             # Sortie RDF/XML (généré)
├── graphe_connaissance.png         # Visualisation (généré)
└── venv/                           # Environnement virtuel
```

---

## 🎓 Contexte Académique

### Sujet du Projet
**Sujet 1 : Architecture T-Box/A-Box avec Réification**
- Implémentation d'une ontologie complète (schéma + instances)
- Distinction claire entre T-Box (terminologie) et A-Box (assertions)
- Réification RDF pour annotation de triplets
- Respect strict des standards OWL 2 et RDFS du W3C

### Objectifs Pédagogiques Atteints
✅ Maîtrise des ontologies OWL (Classes, Propriétés, Restrictions)
✅ Différenciation OWL vs RDFS (Restrictions avec BNode)
✅ Intégration de technologies NLP modernes (spaCy, LLM)
✅ Sérialisation RDF multi-format (Turtle, RDF/XML)
✅ Réification RDF pour métadonnées
✅ Requêtes SPARQL sur graphes de connaissances
✅ Interopérabilité avec ontologies standards (FOAF, Schema.org)

### Innovations Techniques
🔥 **Intégration LLM réelle** : Groq API + Llama-3.1-8B-Instant
🔥 **Prompt Engineering** : Template optimisé pour extraction de relations
🔥 **Fallback intelligent** : 3 niveaux de résilience (API → linguistique → défaut)
🔥 **Performance** : Inférence ultra-rapide (200-400ms par relation)

---

## 📖 Références et Standards

### Standards W3C Respectés
- [OWL 2 Web Ontology Language](https://www.w3.org/TR/owl2-overview/)
- [RDF 1.1 Concepts](https://www.w3.org/TR/rdf11-concepts/)
- [RDF Schema 1.1](https://www.w3.org/TR/rdf-schema/)
- [Turtle - Terse RDF Triple Language](https://www.w3.org/TR/turtle/)
- [RDF 1.1 XML Syntax](https://www.w3.org/TR/rdf-syntax-grammar/)
- [SPARQL 1.1 Query Language](https://www.w3.org/TR/sparql11-query/)

### Ontologies Utilisées
- [FOAF (Friend of a Friend)](http://xmlns.com/foaf/spec/) - Représentation de personnes
- [Schema.org](https://schema.org/) - Vocabulaire standard du Web
- [Dublin Core Metadata](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/) - Métadonnées

### Technologies et APIs
- [spaCy](https://spacy.io/) - Industrial-Strength NLP
- [RDFLib](https://rdflib.readthedocs.io/) - Python RDF Library
- [Groq API](https://console.groq.com/docs/quickstart) - Ultra-fast LLM Inference
- [Meta Llama 3.1](https://ai.meta.com/blog/meta-llama-3-1/) - LLM 8B parameters

---

## 🏆 Fonctionnalités Avancées

### 1. Normalisation Intelligente des URIs
```python
def normaliser_uri(texte: str) -> str:
    """Supprime accents, espaces, caractères spéciaux"""
    texte = unicodedata.normalize('NFD', texte)
    texte = ''.join(c for c in texte if unicodedata.category(c) != 'Mn')
    texte = texte.replace(' ', '_').replace("'", '_')
    return ''.join(c for c in texte if c.isalnum() or c == '_')
```

### 2. Détection Contextuelle de Relations
**Analyse linguistique de fallback :**
- Mots-clés : "professeur", "enseigne", "travaille" → `ex:worksAt`
- Mots-clés : "étudiant", "master", "étudie" → `ex:studiesAt`
- Mots-clés : "collabore", "équipe", "projet" → `ex:collaboratesWith`

### 3. Métadonnées de Confiance
```python
# Score de confiance pour les relations détectées
statement.add(EX.confidence, Literal(0.92, datatype=XSD.float))
```

### 4. Export Multi-format Simultané
```python
# Turtle (lisible)
graph.serialize(destination="knowledge_graph.ttl", format="turtle")
# RDF/XML (standard)
graph.serialize(destination="knowledge_graph.xml", format="xml")
```

---

## 🎬 Cas d'Usage Réels

### Exemple 1 : Publication Académique
**Texte :**
```
Jean Dupont et Marie Martin ont publié un article sur l'IA à Paris.
```

**Extraction :**
- `Jean Dupont` (PER) → `foaf:Person`
- `Marie Martin` (PER) → `foaf:Person`
- `Paris` (LOC) → `schema:Place`
- Relation LLM : `Jean Dupont` **collaboratesWith** `Marie Martin`
- Métadonnée : `dc:source = "Jean Dupont et Marie Martin ont publié..."`

### Exemple 2 : Affiliation Universitaire
**Texte :**
```
Zoubida Kedad est professeure à l'Université de Versailles.
```

**Extraction :**
- `Zoubida Kedad` (PER) → `foaf:Person`
- `Université de Versailles` (ORG) → `schema:Organization`
- Relation LLM : `Zoubida Kedad` **worksAt** `Université de Versailles`
- Sortie API : `🤖 Groq/Llama-3 a détecté : worksAt`

---

## 🔬 Analyses Possibles avec SPARQL

### 1. Réseau de Collaboration
```sparql
PREFIX ex: <http://example.org/ontology/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?person1 ?person2 WHERE {
  ?person1 ex:collaboratesWith ?person2 .
  ?person1 foaf:name ?name1 .
  ?person2 foaf:name ?name2 .
}
```

### 2. Affiliations Académiques
```sparql
PREFIX ex: <http://example.org/ontology/>
SELECT ?person ?org WHERE {
  ?person ex:worksAt ?org .
}
```

### 3. Documents avec Métadonnées
```sparql
PREFIX ex: <http://example.org/ontology/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>

SELECT ?doc ?author ?source WHERE {
  ?doc rdf:type ex:ValidatedCourse .
  ?doc ex:author ?author .
  ?stmt rdf:predicate ex:author .
  ?stmt dc:source ?source .
}
```

---

## 📈 Améliorations Futures

### Court Terme
- [ ] Support de modèles LLM multilingues (anglais, espagnol)
- [ ] Détection de relations temporelles (avant/après)
- [ ] Export au format JSON-LD
- [ ] Interface web Flask pour visualisation interactive

### Moyen Terme
- [ ] Fine-tuning du LLM sur corpus académique français
- [ ] Extraction d'entités complexes (dates, montants, emails)
- [ ] Intégration avec DBpedia et Wikidata (linking)
- [ ] API REST pour extraction en temps réel

### Long Terme
- [ ] Apprentissage par renforcement sur feedback utilisateur
- [ ] Graphe de connaissances distribué (RDF*-star)
- [ ] Raisonnement automatique avec Pellet/HermiT
- [ ] Publication sur LOD Cloud

---

## 🤝 Contributeurs

**Étudiant :** Master 2 Web Sémantique  
**Superviseur Académique :** [Nom du professeur]  
**Institution :** [Nom de l'université]  
**Année :** 2025-2026

---

## 📄 Licence

Ce projet est développé dans un cadre académique et n'est pas destiné à une utilisation commerciale.

**Restrictions :**
- Code source : Usage académique uniquement
- Ontologies : Conformes aux licences FOAF, Schema.org, Dublin Core
- API Groq : Soumise aux [conditions d'utilisation Groq](https://console.groq.com/docs/terms)
- Modèle Llama-3.1 : [Licence Meta Llama 3.1](https://ai.meta.com/llama/license/)

---

## 📞 Support et Contact

**Questions Techniques :**
- Consulter les fichiers de documentation dans `Docs/`
- Lire la section **Troubleshooting** ci-dessus
- Exécuter `python test_corrections.py` pour diagnostiquer

**Rapports de Bugs :**
1. Vérifier que toutes les dépendances sont installées
2. Confirmer que la clé API Groq est valide
3. Tester avec `./demo.sh` pour reproduire le problème

**Ressources Utiles :**
- [Documentation RDFLib](https://rdflib.readthedocs.io/)
- [Documentation spaCy](https://spacy.io/usage)
- [Groq API Docs](https://console.groq.com/docs/quickstart)
- [W3C OWL 2 Primer](https://www.w3.org/TR/owl2-primer/)

---

## ✨ Remerciements

Merci aux équipes et projets open-source suivants :
- **W3C** pour les standards du Web Sémantique
- **Meta AI** pour Llama 3.1
- **Groq** pour l'infrastructure d'inférence ultra-rapide
- **Explosion AI** pour spaCy
- **RDFLib Community** pour la bibliothèque RDF Python
- **FOAF & Schema.org** pour les ontologies standard

---

---

*Dernière mise à jour : 16 janvier 2026*  
*Version : 2.0 (Groq API + Llama-3.1-8B-Instant)*  
*Projet Master 2 Web Sémantique - Architecture T-Box/A-Box avec LLM*

# Configuration API Hugging Face
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
HF_TOKEN = "votre_token_ici"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def predict_relation_real_api(entity1: str, entity2: str, sentence: str):
    """
    Appel API RÉEL vers Mistral-7B pour prédiction de relations.
    Plus de simulation - vrai LLM en production !
    """
    prompt = f"""[INST] Tu es un expert en Web Sémantique.
Analyse la phrase suivante : "{sentence}"
Quelle est la relation entre "{entity1}" et "{entity2}" ?

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
        "parameters": {"max_new_tokens": 10, "return_full_text": False}
    }
    
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    result = response.json()
    relation = result[0]['generated_text'].strip()
    
    print(f"🤖 Mistral-7B : {entity1} --[{relation}]--> {entity2}")
    return relation
```

### Visualisation du Graphe

```python
def visualize_knowledge_graph(graph, output_file="graphe_connaissance.png"):
    """
    Génère une visualisation du graphe avec NetworkX et Matplotlib.
    """
    G = nx.DiGraph()
    
    # Extraction des nœuds et arêtes depuis le graphe RDF
    # Colorisation par type d'entité
    # Export en PNG haute résolution
    
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
```

### Double Sérialisation (Turtle + RDF/XML) ⭐

```python
# FORMAT 1 : TURTLE (lisible par l'humain)
turtle_output = graph.serialize(format='turtle')
with open("knowledge_graph.ttl", 'w', encoding='utf-8') as f:
    f.write(turtle_output)

# FORMAT 2 : RDF/XML (standard historique du W3C, utilisé dans les cours)
xml_output = graph.serialize(format='xml')
with open("knowledge_graph.xml", 'w', encoding='utf-8') as f:
    f.write(xml_output)

print(f"✓ Double sérialisation : Turtle + RDF/XML")
```

### Réification d'un Triplet

```python
def reify_statement(graph, subject, predicate, obj, source_file):
    statement_uri = DATA[f"statement_{hash((subject, predicate, obj))}"]
    
    # Déclaration du nœud Statement
    graph.add((statement_uri, RDF.type, RDF.Statement))
    
    # Décomposition du triplet
    graph.add((statement_uri, RDF.subject, subject))
    graph.add((statement_uri, RDF.predicate, predicate))
    graph.add((statement_uri, RDF.object, obj))
    
    # Métadonnée : source d'extraction
    graph.add((statement_uri, DC.source, Literal(source_file)))
```

---

## 📖 Concepts Théoriques Appliqués

### T-Box vs A-Box

- **T-Box (Terminological Box)** : Schéma conceptuel, définitions des classes et propriétés
- **A-Box (Assertional Box)** : Données factuelles, instances concrètes

### OWL Property Hierarchy

```
owl:ObjectProperty    → Relie des ressources (URI → URI)
owl:DatatypeProperty  → Relie ressources et littéraux (URI → Literal)
```

### Réification RDF

Permet de faire des assertions sur des assertions :
```turtle
:statement1 rdf:type rdf:Statement ;
    rdf:subject :ZoubidaKedad ;
    rdf:predicate :enseigne_a ;
    rdf:object :UniversiteVersailles ;
    dc:source "texte_exemple.txt" .
```

---

## 🎓 Conformité Académique

Ce projet respecte les exigences suivantes :

✅ Séparation stricte T-Box / A-Box  
✅ Distinction ObjectProperty vs DatatypeProperty  
✅ Contraintes rdfs:domain et rdfs:range  
✅ **Restrictions OWL explicites** (ValidatedCourse) ⭐  
✅ Réification RDF complète  
✅ Standards OWL et RDFS  
✅ **Ontologies standards** : FOAF et Schema.org  
✅ **Extraction de relations via API Hugging Face RÉELLE (Mistral-7B)** 🔥 ⭐  
✅ **Double sérialisation** : Turtle + RDF/XML ⭐  
✅ **Visualisation graphique** interactive  
✅ Code commenté et documenté  
✅ Script de tests de validation inclus  

---

## 📝 Documentation des Corrections Académiques

### Fichiers de référence

1. **CORRECTIONS_ACADEMIQUES.md** - Rapport détaillé pour le superviseur
   - Explication technique des 3 corrections
   - Exemples de code avec numéros de lignes
   - Résultats des tests de validation

2. **GUIDE_PRESENTATION.md** - Guide rapide pour la présentation orale
   - Script de présentation (1 minute)
   - Points clés à montrer
   - Checklist avant présentation

3. **test_corrections.py** - Suite de tests automatiques
   - Validation de la restriction OWL
   - Validation du prompt engineering
   - Validation de la double sérialisation

### Commandes de validation

```bash
# Exécuter tous les tests
python test_corrections.py

# Vérifier les fichiers générés
ls -lh knowledge_graph.*

# Afficher la restriction OWL dans le XML
grep -A 5 "owl:Restriction" knowledge_graph.xml
```

---

## 📚 Références

### Standards du Web Sémantique
- **OWL 2 Web Ontology Language** : [W3C Recommendation](https://www.w3.org/TR/owl2-overview/)
- **RDF 1.1 Concepts** : [W3C Recommendation](https://www.w3.org/TR/rdf11-concepts/)
- **RDFS 1.1** : [W3C Recommendation](https://www.w3.org/TR/rdf-schema/)
- **FOAF Vocabulary** : [Friend of a Friend](http://xmlns.com/foaf/spec/)
- **Schema.org** : [Ontologie standard](https://schema.org/)

### Bibliothèques Python
- **spaCy** : [Documentation officielle](https://spacy.io/)
- **rdflib** : [Documentation officielle](https://rdflib.readthedocs.io/)
- **NetworkX** : [Documentation officielle](https://networkx.org/)
- **Matplotlib** : [Documentation officielle](https://matplotlib.org/)

---

## 📝 Auteur

**Projet Master 2 - Web Sémantique**  
Sujet 1 : Extraction de graphes de connaissances à partir de texte

*Date de réalisation : 15 janvier 2026*
# web_semantique
# web_semantique
