# 🎬 Démonstration Interface Streamlit

## 📸 Aperçu de l'Interface

### 🏠 Page d'Accueil

```
╔══════════════════════════════════════════════════════════════════╗
║  🕸️ Extraction de Graphe de Connaissances                       ║
║                                                                  ║
║  Master 2 Datascale - Web Sémantique (Sujet 1)                 ║
║  Technologies : SpaCy + Groq Llama 3.1 + RDFLib                ║
╚══════════════════════════════════════════════════════════════════╝

┌─────────────────────────────┬─────────────────────────────────┐
│  📝 TEXTE SOURCE            │  📊 VISUALISATION               │
│                             │                                 │
│  ┌─ Exemples ─────────┐    │  ┌─────────────────────────┐   │
│  │ • Exemple 1        │    │  │                         │   │
│  │ • Exemple 2        │    │  │   [Graphe NetworkX]     │   │
│  │ • Texte perso      │    │  │                         │   │
│  └────────────────────┘    │  │   🔵 Personnes          │   │
│                             │  │   �� Lieux              │   │
│  ┌─ Zone de texte ────┐    │  │   🟠 Organisations      │   │
│  │ Zoubida Kedad      │    │  │                         │   │
│  │ enseigne à...      │    │  └─────────────────────────┘   │
│  │                    │    │                                 │
│  └────────────────────┘    │  [⬇️ Télécharger]              │
│                             │                                 │
│  [🚀 Générer le Graphe]    │                                 │
│                             │                                 │
│  ✅ Extraction terminée!    │                                 │
└─────────────────────────────┴─────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════╗
║  �� EXPORT RDF                                                   ║
║                                                                  ║
║  [🐢 Turtle] [📄 RDF/XML] [📈 Statistiques]                    ║
║                                                                  ║
║  @prefix ex: <http://example.org/master2/ontology#> .           ║
║  @prefix foaf: <http://xmlns.com/foaf/0.1/> .                  ║
║                                                                  ║
║  ex:Zoubida_Kedad a foaf:Person ;                              ║
║      foaf:name "Zoubida Kedad" ;                               ║
║      ex:worksAt ex:Universite_de_Versailles .                  ║
║                                                                  ║
║  [⬇️ Télécharger Turtle]                                        ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## 🎯 Workflow Utilisateur

### Étape 1 : Sélection du Texte
1. Ouvrir http://localhost:8501
2. Choisir un exemple ou saisir un texte personnalisé
3. Le texte apparaît dans la zone d'édition

### Étape 2 : Génération
1. Cliquer sur **"🚀 Générer le Graphe RDF"**
2. Barre de progression s'affiche :
   - 📊 Extraction des entités (25%)
   - 🤖 Interrogation LLM (50%)
   - 📦 Génération RDF (75%)
   - 🎨 Visualisation (100%)
3. Message de succès : **"✅ Extraction terminée !"**

### Étape 3 : Visualisation
- **Colonne droite** : Graphe NetworkX coloré
- **Onglet Turtle** : Code RDF lisible
- **Onglet RDF/XML** : Export W3C standard
- **Onglet Stats** : Métriques du graphe

### Étape 4 : Export
- Boutons de téléchargement disponibles
- Formats : PNG, TTL, XML

---

## ✨ Fonctionnalités Mises en Avant

### 🎨 Design Moderne
- Interface responsive
- Thème bleu (#1f77b4)
- Emojis pour meilleure UX
- Layout en 2 colonnes

### ⚡ Performance
- Extraction en 5-15 secondes
- Barre de progression en temps réel
- Feedback immédiat

### 📊 Statistiques Temps Réel
- Nombre de triplets RDF
- Personnes détectées
- Organisations/lieux
- Relations extraites

### 🔧 Actions Utilisateur
- Nettoyage des fichiers en 1 clic
- Téléchargement des exports
- Exemples prêts à l'emploi

---

## 🎬 Scénarios de Démonstration

### Scénario 1 : Professeur Universitaire

**Input :**
```
Zoubida Kedad enseigne à l'Université de Versailles. 
Elle a rédigé un cours sur RDFS.
```

**Output visible :**
- Graphe avec 2 nœuds : 🔵 Zoubida Kedad, 🟠 Université de Versailles
- Relation : worksAt (détectée par Groq/Llama-3)
- 73 triplets RDF générés
- Temps : ~7 secondes

### Scénario 2 : Collaboration Académique

**Input :**
```
Jean Dupont et Marie Martin collaborent sur un projet d'IA à Paris. 
Ils travaillent ensemble à l'INRIA.
```

**Output visible :**
- Graphe avec 4 nœuds : 🔵 Jean, 🔵 Marie, 🟢 Paris, 🟠 INRIA
- Relations : collaboratesWith, worksAt
- ~85 triplets RDF
- Temps : ~12 secondes

### Scénario 3 : Parcours Étudiant

**Input :**
```
Pierre Durand est étudiant en Master 2 à l'Université de Paris.
```

**Output visible :**
- Graphe avec 2 nœuds : 🔵 Pierre Durand, 🟠 Université de Paris
- Relation : studiesAt
- ~65 triplets RDF
- Temps : ~6 secondes

---

## 🎥 Captures d'Écran Clés

### 1. Interface au Démarrage
- Layout propre et organisé
- Sidebar avec informations
- Exemples prédéfinis visibles

### 2. Pendant l'Extraction
- Barre de progression animée
- Messages de statut (spaCy, LLM, RDF)
- Spinner visuel

### 3. Résultat Affiché
- Graphe coloré dans colonne droite
- Code RDF dans onglet Turtle
- Statistiques dans onglet dédié

### 4. Export
- Boutons de téléchargement actifs
- Preview du code RDF avec coloration syntaxique
- Compteurs de métriques

---

## 🏆 Points Forts de l'Interface

1. **Simplicité** : 3 clics pour générer un graphe
2. **Feedback** : Messages et barres de progression
3. **Esthétique** : Design moderne et professionnel
4. **Fonctionnalité** : Export multi-format intégré
5. **Pédagogique** : Exemples et conseils intégrés

---

## 📊 Métriques de Performance

| Métrique | Valeur |
|----------|--------|
| Temps de chargement | < 2s |
| Temps d'extraction | 5-15s |
| Taille de l'interface | ~15 KB |
| Responsive | ✅ Oui |
| Compatible | Chrome, Firefox, Safari |

---

## 🎓 Utilisation Académique

**Pour une présentation orale :**
1. Lancer `./run_streamlit.sh`
2. Ouvrir le navigateur en mode présentation
3. Démontrer avec Exemple 1 (Zoubida Kedad)
4. Montrer le graphe généré
5. Expliquer le code Turtle
6. Afficher les statistiques

**Points à mettre en avant :**
- ✅ Restriction OWL visible dans code
- ✅ LLM réel (logs visibles)
- ✅ Double sérialisation (onglets)
- ✅ Architecture T-Box/A-Box respectée

---

*Guide de démonstration - Version 2.0 - 16 janvier 2026*
