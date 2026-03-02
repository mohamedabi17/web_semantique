# 🚀 Démarrage Rapide - Démo Streamlit

## Vérification Préalable

```bash
python3 test_demo_modules.py
```

**Résultat attendu :** ✅ 24/24 tests réussis (100%)

---

## Lancement de l'Interface

### Option 1 : Lanceur Python (Recommandé)
```bash
python3 launch_demo.py
```

### Option 2 : Streamlit Direct
```bash
streamlit run app_streamlit.py
```

### Option 3 : Script Bash
```bash
./scripts/launch_demo.sh
```

---

## 🎯 Que Faire Ensuite ?

**L'interface Streamlit s'ouvrira automatiquement à :** http://localhost:8501

### 1. Vérifier le Diagnostic (en haut de page)
- Bandeau vert : `✅ SYSTÈME OPÉRATIONNEL - Score: 100%`
- Cliquer sur "🔍 Diagnostic des Modules" pour voir les détails

### 2. Lancer un Exemple
- Sélectionner : `🎓 Démo 1: Extraction Complète (NER + Relations)`
- Cocher : `📋 Afficher les logs détaillés du pipeline`
- Cliquer : `🚀 Générer le Graphe RDF`

### 3. Observer le Pipeline (7 étapes)
- Étape 2/7 : **Module 0++** (NER Hybride - 7 couches)
- Étape 5/7 : **Module 1** (OWL Reasoning)
- Étape 6/7 : **Confidence Scoring**

### 4. Consulter les Logs
- **🔍 Module 0++** : Voir les 7 couches d'extraction
- **⚙️ Module 1** : Validation OWL domain/range
- **📊 Confidence System** : Scores calculés
- **🔗 Relations** : Verbes mappés vers propriétés OWL

### 5. Visualiser le Graphe
- Graphe NetworkX (colonne de droite)
- Onglet Turtle : Voir `ex:confidence` dans le code RDF
- Statistiques : Triplets, Entités, Relations

---

## 📖 Documentation Complète

**Guide de démonstration complet :** `GUIDE_DEMO.md`

**Scénario 5-7 minutes avec exemples détaillés**

---

## 🎬 Exemples Pré-Configurés

| Exemple | Ce qu'il démontre |
|---------|-------------------|
| 🎓 Démo 1 | Extraction complète (NER + Relations) |
| 💼 Démo 2 | Multi-entités + Verbes mappés |
| ✍️ Démo 3 | Propriété `author` (écrire → ex:author) |
| 🏢 Démo 4 | Organisations + Lieux |
| 🔬 Démo 5 | Validation OWL Reasoning |
| 🧪 Test Audit | NER Hybride 7 couches |

---

## ✅ Checklist Avant Démo

- [ ] Tests passent à 100% (`python3 test_demo_modules.py`)
- [ ] Streamlit se lance sans erreur
- [ ] Bandeau vert "SYSTÈME OPÉRATIONNEL" affiché
- [ ] Au moins 1 exemple testé avec succès
- [ ] Logs détaillés visibles

**Si tout est coché : 🎉 PRÊT POUR LA DÉMO !**

---

## 🛠️ Résolution de Problèmes

### Streamlit ne se lance pas
```bash
pip install streamlit
streamlit --version
```

### Module manquant (erreur import)
```bash
python3 test_demo_modules.py  # Voir quel module manque
```

### Pas de graphe généré
- Vérifier que le texte n'est pas vide
- Vérifier les logs d'erreur dans l'interface
- Relancer avec un exemple pré-configuré

---

**Version :** 3.0  
**Date :** 1er mars 2026  
**Statut :** ✅ Production Ready
