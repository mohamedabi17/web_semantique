# 🎯 GUIDE DE DÉMONSTRATION - Interface Streamlit

## 📋 Prérequis (Vérification Automatique)

Avant de lancer la démo, exécutez le script de vérification :

```bash
python3 test_demo_modules.py
```

**Résultat attendu :** `✅ TOUS LES MODULES SONT PRÊTS POUR LA DÉMO ✨` (100%)

---

## 🚀 Lancement de l'Interface

```bash
streamlit run app_streamlit.py
```

L'interface s'ouvrira automatiquement dans votre navigateur à l'adresse : **http://localhost:8501**

---

## 🎬 Scénario de Démonstration (5-7 minutes)

### **Étape 1 : Présentation de l'Architecture (30 secondes)**

1. Montrez le **bandeau vert** en haut : `✅ SYSTÈME OPÉRATIONNEL - Score: 100%`
2. Cliquez sur **"🔍 Diagnostic des Modules"** pour montrer :
   - Module 0++ (NER Hybride) : 7/7 couches ✅
   - Module 1 (OWL Reasoning) : Validation + Reasoning ✅
   - Confidence System : Actif ✅
   - Pipeline Principal : Intégré ✅

**Ce que ça démontre :** Tous les modules identifiés dans l'audit sont désormais implémentés à 100%

---

### **Étape 2 : Démo NER Hybride - 7 Couches (2 minutes)**

**Sélectionnez :** `🎓 Démo 1: Extraction Complète (NER + Relations)`

**Texte pré-rempli :**
```
Zoubida Kedad enseigne le Web Sémantique à l'Université de Versailles. Elle a écrit plusieurs articles sur RDF.
```

**Actions :**
1. Cochez ✅ **"📋 Afficher les logs détaillés du pipeline"**
2. Cliquez sur **"🚀 Générer le Graphe RDF"**

**Observez le Pipeline (7 étapes) :**
- ⏳ Étape 1/7 : Préparation du texte
- 🔍 Étape 2/7 : **Module 0++ - Extraction NER Hybride (7 couches)**
- 🔧 Étape 3/7 : Normalisation + Déduplication
- 🤖 Étape 4/7 : Interrogation LLM (Groq/Llama-3.1)
- ⚙️ Étape 5/7 : **Module 1 - Validation OWL + Reasoning**
- 📊 Étape 6/7 : **Calcul des scores de confiance**
- 📦 Étape 7/7 : Génération fichiers RDF + Visualisation

**Logs à montrer :**

Ouvrez les expanders :

1. **🔍 Module 0++ - NER Hybride (7 Couches)**
   - Montrez les différentes couches détectant les entités :
     * Couche 1 : spaCy NER (Zoubida Kedad, Université de Versailles)
     * Couche 2 : EntityRuler (patterns universitaires)
     * Couche 3 : PROPN heuristics
     * Couche 4 : Normalisation
     * Couche 5 : Déduplication
     * Couche 6 : Filtrage confiance
     * Couche 7 : Validation ontologique

2. **⚙️ Module 1 - OWL Reasoning Engine**
   - Montrez la validation domain/range
   - Vérification des contraintes OWL

3. **📊 Confidence Scoring System**
   - Scores multi-sources (spaCy: 0.90, LLM: 0.85, etc.)
   - Statistiques : Min/Max/Mean

4. **🔗 Relations Extraites (Verbes + LLM)**
   - Mapping verbes : `enseigne` → `ex:teaches`
   - Mapping verbes : `écrit` → `ex:author`

**Ce que ça démontre :** 
- ✅ Module 0++ : 7 couches fonctionnelles (14% → 100%)
- ✅ Module 1 : Validation OWL active
- ✅ Confidence System : Scores calculés

---

### **Étape 3 : Démo Mapping Verbes → OWL (1 minute)**

**Sélectionnez :** `💼 Démo 2: Multi-Entités + Verbes`

**Texte pré-rempli :**
```
Emmanuel Macron travaille à Paris. Il dirige la France et collabore avec l'Union Européenne.
```

**Actions :**
1. Cliquez sur **"🚀 Générer le Graphe RDF"**
2. Observez dans les logs :

**Logs attendus :**
```
🔍 Lemme détecté : 'travailler' (VERB)
✓ Verbe 'travaille' → Emmanuel Macron --[ex:worksAt]--> Paris

🔍 Lemme détecté : 'diriger' (VERB)
✓ Verbe 'dirige' → Emmanuel Macron --[ex:manages]--> France
```

**Ce que ça démontre :** 
- ✅ Couche 7 du Module 0++ : Mapping lemme → propriété OWL
- ✅ Validation domain/range automatique
- ✅ Score de confiance 0.80 pour les verbes

---

### **Étape 4 : Visualisation RDF (1 minute)**

**Colonne de droite :** Graphe généré automatiquement

**Montrez :**
1. Le graphe NetworkX avec nœuds et arêtes colorés
2. Les propriétés détectées (worksAt, teaches, author, manages)

**Onglets en bas :**

1. **🐢 Turtle (.ttl)** :
   - Montrez les triplets RDF
   - Cherchez `ex:confidence` dans le code → **Montrez les scores de confiance**
   - Exemple :
     ```turtle
     ex:Zoubida_Kedad ex:teaches ex:Universite_de_Versailles ;
         ex:confidence "0.90"^^xsd:float .
     ```

2. **📄 RDF/XML (.xml)** :
   - Montrez le format XML équivalent

3. **📈 Statistiques** :
   - 👤 Personnes : X
   - 🏢 Organisations/Lieux : Y
   - 🔗 Relations : Z
   - Classes OWL détectées :
     * ✅ Classes OWL définies
     * ✅ Restriction OWL (ValidatedCourse)
     * ✅ ObjectProperties
     * ✅ DatatypeProperties

**Ce que ça démontre :** 
- ✅ Double sérialisation RDF (Turtle + XML)
- ✅ Confidence system actif
- ✅ Architecture T-Box/A-Box complète

---

### **Étape 5 : Sidebar - Statistiques Temps Réel (30 secondes)**

**Montrez la barre latérale (sidebar) :**

```
📊 Statistiques du Graphe
- Triplets RDF : 45
- Personnes : 3
- Organisations : 2
- Scores Confiance : 8
```

**Actions rapides :**
1. **🔄 Rafraîchir la page** → Recharge l'interface
2. **🗑️ Nettoyer les fichiers** → Efface les graphes générés

**Ce que ça démontre :** 
- ✅ Interface interactive et réactive
- ✅ Statistiques calculées dynamiquement

---

## 🎯 Points Clés à Mentionner

### **Avant les Corrections (Audit initial : 72%)**

| Module | Score Initial | Problème |
|--------|---------------|----------|
| Module 0++ | 14% | Simple wrapper spaCy, pas de NER hybride |
| Module 1 | 75% | Validation syntaxique uniquement, pas de raisonneur OWL |
| Confidence | 0% | Code commenté, système inactif |

### **Après les Corrections (Score actuel : 100%)**

| Module | Score Final | Implémentation |
|--------|-------------|----------------|
| Module 0++ | **100%** | ✅ 7 couches complètes : spaCy, EntityRuler, PROPN, normalisation, déduplication, confiance, verbe mapping |
| Module 1 | **100%** | ✅ Validation domain/range + hiérarchie + owlrl (optionnel) |
| Confidence | **100%** | ✅ Scores multi-sources actifs avec reification |

---

## 🧪 Exemples Supplémentaires pour Questions

### **Test OWL Reasoning :**
```
Alice enseigne la physique. Bob étudie les mathématiques. Charlie travaille à l'université.
```
→ Montre la validation des contraintes OWL (domain/range)

### **Test Littérature (propriété 'author') :**
```
Victor Hugo a écrit Les Misérables. Albert Camus a écrit L'Étranger.
```
→ Montre le mapping `écrire` → `ex:author`

### **Test Multi-Organisations :**
```
Microsoft est situé à Redmond. Google travaille à Mountain View. Apple est basé à Cupertino.
```
→ Montre la détection d'organisations et lieux

---

## 📊 Métriques de Démo

**Temps total :** 5-7 minutes  
**Nombre d'exemples :** 3-4 (selon questions)  
**Modules démontrés :** 
- ✅ Module 0++ (7 couches)
- ✅ Module 1 (OWL Reasoning)
- ✅ Confidence System
- ✅ Double sérialisation RDF

**Score final affiché :** **100% conformité**

---

## 🚨 Troubleshooting

### Problème : Streamlit ne se lance pas

```bash
# Vérifier l'installation
pip install streamlit

# Relancer
streamlit run app_streamlit.py
```

### Problème : Modules non détectés

```bash
# Vérifier avec le script de test
python3 test_demo_modules.py

# Résultat attendu : 100%
```

### Problème : Erreur LLM (Groq API)

```bash
# Vérifier la clé API
cat .env
# GROQ_API_KEY=gsk_...

# Si absente, ajouter votre clé
echo "GROQ_API_KEY=votre_cle_ici" > .env
```

---

## ✅ Checklist Avant Démo

- [ ] `python3 test_demo_modules.py` → 100% ✅
- [ ] Clé Groq API configurée dans `.env`
- [ ] Streamlit s'ouvre sans erreur
- [ ] Bandeau vert "SYSTÈME OPÉRATIONNEL" affiché
- [ ] Diagnostic des modules montre tout en vert
- [ ] Logs détaillés activables

**Si toutes les cases sont cochées : 🎉 PRÊT POUR LA DÉMO !**

---

## 📝 Script de Présentation (1 minute d'intro)

> "Bonjour, je vais vous présenter mon projet de Web Sémantique : une architecture neuro-symbolique pour l'extraction de graphes de connaissances.
>
> Suite à l'audit technique qui avait révélé un score de 72%, j'ai implémenté les trois modules manquants :
> - **Module 0++** : Un NER hybride à 7 couches combinant spaCy, EntityRuler, heuristiques PROPN, normalisation, déduplication, filtrage par confiance, et mapping de verbes vers propriétés OWL
> - **Module 1** : Un moteur de raisonnement OWL avec validation domain/range et support de la hiérarchie de classes
> - **Confidence System** : Un système de scores multi-sources avec reification RDF
>
> Le système atteint maintenant **100% de conformité**. Je vais vous faire une démonstration de l'interface Streamlit que j'ai développée pour visualiser le pipeline complet."

**[Puis suivre le scénario ci-dessus]**

---

**Bonne démo ! 🚀**
