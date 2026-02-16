# 🕸️ Extraction de Graphes de Connaissances avec LLM

**Projet Master 2 - Web Sémantique**  
Architecture T-Box/A-Box avec extraction intelligente de relations par IA

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![spaCy](https://img.shields.io/badge/spaCy-NER-green.svg)](https://spacy.io/)
[![Groq](https://img.shields.io/badge/Groq-Llama%203.1-orange.svg)](https://console.groq.com/)
[![RDFLib](https://img.shields.io/badge/RDFLib-OWL%202-red.svg)](https://rdflib.readthedocs.io/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-ff4b4b.svg)](https://streamlit.io/)

---

## 📋 Table des Matières

- [🎯 Vue d'Ensemble](#-vue-densemble)
- [✨ Fonctionnalités Principales](#-fonctionnalités-principales)
- [🏗️ Architecture](#️-architecture)
- [⚡ Démarrage Rapide](#-démarrage-rapide)
- [📖 Guide Détaillé](#-guide-détaillé)
- [🔧 Configuration](#-configuration)
- [🧪 Tests](#-tests)
- [📊 Résultats](#-résultats)
- [📁 Structure du Projet](#-structure-du-projet)

---

## 🎯 Vue d'Ensemble

Ce projet implémente une **plateforme complète d'extraction de graphes de connaissances** à partir de texte non structuré en français, en utilisant :

- **Architecture Sémantique** : T-Box (ontologie OWL) + A-Box (instances RDF)
- **NLP Avancé** : spaCy pour la reconnaissance d'entités nommées (NER)
- **IA Générative** : Groq API avec Llama 3.1 pour l'extraction de relations
- **Standards W3C** : OWL 2, RDFS, RDF/XML, Turtle
- **Interface Web** : Application Streamlit interactive

### 🎓 Contexte Académique

**Objectif** : Démontrer la maîtrise des technologies du Web Sémantique en construisant un système capable de :
1. Définir une ontologie formelle (T-Box) avec restrictions OWL
2. Extraire automatiquement des données factuelles (A-Box)
3. Réifier les triplets RDF pour la traçabilité
4. Exporter en formats standards (Turtle, RDF/XML)

---

## ✨ Fonctionnalités Principales

### 🔬 Technologies Implémentées

#### 1. **Ontologie OWL Complète (T-Box)**
- ✅ Classes OWL standards (`foaf:Person`, `schema:Place`, `schema:Organization`)
- ✅ **Restriction OWL avec BNode** (différencie OWL de RDFS)
- ✅ ObjectProperties avec contraintes `domain`/`range`
- ✅ DatatypeProperties typées (XSD)

```turtle
# Exemple de restriction OWL
ex:ValidatedCourse rdfs:subClassOf ex:Document ;
    rdfs:subClassOf [
        a owl:Restriction ;
        owl:onProperty ex:author ;
        owl:someValuesFrom foaf:Person
    ] .
```

#### 2. **Extraction de Relations par LLM**
- 🤖 **API Groq** avec **Meta Llama 3.1-8B-Instant** (gratuit et rapide)
- 📊 9 types de relations détectés automatiquement :
  - `teaches` (personne → lieu)
  - `teachesSubject` (personne → matière/topic)
  - `author` (personne → document)
  - `worksAt` (personne → organisation)
  - `locatedIn` (entité → lieu)
  - `collaboratesWith` (personne ↔ personne)
  - `studiesAt` (personne → organisation)
  - `manages` (personne → organisation)
  - `relatedTo` (relation générique)

#### 3. **Détection Intelligente de Topics**
- 🎓 Re-classification dynamique des entités via Groq/Llama-3
- 📚 Détection automatique des matières académiques (Physique, Maths, Informatique, etc.)
- 🧠 Correction des erreurs de spaCy en contexte

#### 4. **Réification RDF**
- 📝 Traçabilité complète des sources d'information
- 🔗 Métadonnées Dublin Core sur chaque triplet
- 🕰️ Support pour horodatage et score de confiance

#### 5. **Export Multi-Format**
- 🐢 **Turtle** : Format lisible par l'humain
- 📄 **RDF/XML** : Standard W3C pour l'interopérabilité
- 🖼️ **Visualisation PNG** : Graphe NetworkX coloré

#### 6. **Interface Web Interactive**
- 🌐 Application **Streamlit** moderne
- 📝 Exemples pré-chargés + saisie libre
- 📊 Visualisation en temps réel
- ⬇️ Téléchargement des exports RDF

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    TEXTE NON STRUCTURÉ                  │
│  "Zoubida Kedad enseigne à l'Université de Versailles" │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              T-BOX (Ontologie OWL)                      │
│  • Classes : foaf:Person, schema:Place, ex:Document    │
│  • Propriétés : ex:teaches, ex:author, ex:worksAt      │
│  • Restrictions OWL : ex:ValidatedCourse                │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│               PIPELINE NLP + IA                         │
│  1. spaCy NER     : Extraction entités (PER/ORG/LOC)   │
│  2. Groq/Llama-3  : Raffinement types + Topics         │
│  3. Groq/Llama-3  : Prédiction relations               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              A-BOX (Instances RDF)                      │
│  • data:Zoubida_Kedad rdf:type foaf:Person             │
│  • data:Universite_de_Versailles rdf:type schema:Place │
│  • Relations : ex:teaches, ex:author, etc.              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 RÉIFICATION                             │
│  • rdf:Statement avec dc:source                         │
│  • Métadonnées de traçabilité                           │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           EXPORT MULTI-FORMAT                           │
│  • knowledge_graph.ttl (Turtle)                         │
│  • knowledge_graph.xml (RDF/XML)                        │
│  • graphe_connaissance.png (Visualisation)              │
└─────────────────────────────────────────────────────────┘
```

---

## ⚡ Démarrage Rapide

### Prérequis

- Python 3.12+
- pip
- Clé API Groq (gratuite)

### Installation (3 minutes)

```bash
# 1. Cloner le projet
git clone https://github.com/mohamedabi17/web_semantique.git
cd web_semantique

# 2. Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou : venv\Scripts\activate  # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Télécharger le modèle français spaCy
python -m spacy download fr_core_news_sm

# 5. Configurer les clés API
cp .env.example .env
# Éditer .env et ajouter vos clés :
# GROQ_API_KEY=votre_cle_groq_ici
# HF_TOKEN=votre_token_huggingface_ici (optionnel)
```

### Utilisation Immédiate

#### Option A : Interface Web (Recommandée)

```bash
./run_streamlit.sh
# ou : streamlit run app_streamlit.py
```

➡️ Ouvre automatiquement http://localhost:8501

#### Option B : Ligne de Commande

```bash
python kg_extraction_semantic_web.py
```

➡️ Génère 3 fichiers :
- `knowledge_graph.ttl` (Turtle)
- `knowledge_graph.xml` (RDF/XML)
- `graphe_connaissance.png` (Visualisation)

---

## 📖 Guide Détaillé

### 1. Configuration des Clés API

Le projet utilise **2 APIs gratuites** :

#### Groq API (OBLIGATOIRE)
- **Modèle** : Meta Llama 3.1-8B-Instant
- **Usage** : Extraction de relations + raffinement d'entités
- **Obtenir une clé** : https://console.groq.com/keys
- **Limite** : 30 requêtes/minute (gratuit)

#### Hugging Face (OPTIONNEL)
- **Modèle** : Qwen2.5-Coder-32B-Instruct
- **Usage** : Fallback si Groq indisponible
- **Obtenir un token** : https://huggingface.co/settings/tokens

**Fichier `.env`** :
```bash
# OBLIGATOIRE
GROQ_API_KEY=gsk_votre_cle_ici_52_caracteres

# OPTIONNEL
HF_TOKEN=hf_votre_token_ici_34_caracteres
```

### 2. Exemples d'Utilisation

#### Exemple 1 : Texte Académique

```python
python kg_extraction_semantic_web.py --text "Zoubida Kedad enseigne la Physique à l'Université de Versailles. Elle a rédigé un cours sur RDFS."
```

**Résultat** :
```turtle
data:Zoubida_Kedad a foaf:Person ;
    foaf:name "Zoubida Kedad" ;
    ex:teachesSubject data:Physique ;
    ex:teaches data:Universite_de_Versailles ;
    ex:author data:cours_RDFS .

data:Physique a ex:Document ;  # TOPIC détecté automatiquement
    foaf:name "Physique" .

data:cours_RDFS a ex:ValidatedCourse ;  # Restriction OWL appliquée
    foaf:name "cours sur RDFS" .
```

#### Exemple 2 : Texte Professionnel

```bash
python kg_extraction_semantic_web.py --text "Bill Gates dirige Microsoft basé à Redmond. Il collabore avec Satya Nadella."
```

### 3. Interface Streamlit

L'application web offre :

- **3 exemples pré-chargés** (académique, professionnel, géographique)
- **Saisie libre** de texte personnalisé
- **Visualisation en temps réel** du graphe
- **Export Turtle et RDF/XML** téléchargeables
- **Statistiques** : nombre de triplets, entités, relations

---

## 🔧 Configuration

### Variables d'Environnement (`.env`)

| Variable | Obligatoire | Description | Exemple |
|----------|-------------|-------------|---------|
| `GROQ_API_KEY` | ✅ Oui | Clé API Groq pour Llama 3.1 | `gsk_xxxx...` (52 car.) |
| `HF_TOKEN` | ❌ Non | Token Hugging Face (fallback) | `hf_xxxx...` (34 car.) |

---

## 🧪 Tests

### Tests Automatiques

```bash
# Tests académiques (3 corrections validées)
python test_corrections.py

# Tests de détection de topics
python test_topic_detection.py

# Tests d'exemples variés
python test_exemples.py

# Démonstration complète
./demo.sh
```

---

## 📊 Résultats

### Statistiques Typiques

Pour un texte académique standard :

| Métrique | Valeur |
|----------|--------|
| **Entités extraites** | 3-7 |
| **Relations détectées** | 2-6 |
| **Triplets RDF totaux** | 50-100 |
| **Triplets réifiés** | 2-6 |
| **Classes OWL** | 6 |
| **Propriétés OWL** | 12 |

---

## 📁 Structure du Projet

```
web_semantique/
├── README.md                          # Documentation principale
├── requirements.txt                   # Dépendances Python
├── .env.example                       # Template de configuration
│
├── kg_extraction_semantic_web.py      # Script principal (1413 lignes)
├── app_streamlit.py                   # Interface web Streamlit
│
├── Tests/
│   ├── test_corrections.py            # Tests académiques
│   ├── test_exemples.py               # Tests cas d'usage
│   └── test_topic_detection.py        # Tests détection topics
│
├── Scripts/
│   ├── run_streamlit.sh               # Lancement Streamlit
│   └── demo.sh                        # Démonstration complète
│
└── Outputs/ (générés)
    ├── knowledge_graph.ttl            # Export Turtle
    ├── knowledge_graph.xml            # Export RDF/XML
    └── graphe_connaissance.png        # Visualisation
```

---

## 🚀 Déploiement Streamlit Cloud

### Étapes

1. **Push sur GitHub** ✅ (déjà fait)

2. **Connexion à Streamlit Cloud**
   - Allez sur https://share.streamlit.io/
   - Cliquez sur "New app"

3. **Configuration**
   - Repository: `mohamedabi17/web_semantique`
   - Branch: `main`
   - Main file path: `app_streamlit.py`
   - App URL: Choisir un nom personnalisé (ex: `kg-extraction`)

4. **Secrets (IMPORTANT)**
   - Cliquez sur "Advanced settings"
   - Dans "Secrets", ajoutez :
   ```toml
   GROQ_API_KEY = "votre_cle_groq_ici"
   HF_TOKEN = "votre_token_hf_ici"
   ```

5. **Deploy** ✅

---

## 📚 Références

### Standards W3C

- **OWL 2** : https://www.w3.org/TR/owl2-overview/
- **RDF 1.1** : https://www.w3.org/TR/rdf11-concepts/
- **RDFS 1.1** : https://www.w3.org/TR/rdf-schema/
- **SPARQL 1.1** : https://www.w3.org/TR/sparql11-query/

### Ontologies

- **FOAF** : http://xmlns.com/foaf/spec/
- **Schema.org** : https://schema.org/
- **Dublin Core** : https://www.dublincore.org/

### Outils

- **RDFLib** : https://rdflib.readthedocs.io/
- **spaCy** : https://spacy.io/
- **Groq API** : https://console.groq.com/docs
- **Streamlit** : https://docs.streamlit.io/

---

## 📞 Contact

**GitHub** : https://github.com/mohamedabi17/web_semantique  
**Projet** : Master 2 Datascale - Web Sémantique  
**Date** : Janvier 2026

---

## 📜 Licence

MIT License - Libre d'utilisation pour projets académiques et commerciaux.

---

**⭐ Si ce projet vous a été utile, n'hésitez pas à lui donner une étoile sur GitHub !**
