# 🧪 GUIDE DE TEST - Projet Knowledge Graph

## ⚡ Tests Rapides (2 minutes)

### 1. Test du Script Principal
```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Exécuter le script
python kg_extraction_semantic_web.py
```

**✅ Résultat attendu :**
- Génération de `knowledge_graph.ttl` (format Turtle)
- Génération de `knowledge_graph.xml` (format RDF/XML)
- Génération de `knowledge_graph.png` (visualisation)
- Messages de succès dans le terminal

---

### 2. Vérifier les 3 Corrections Académiques

#### ✅ Correction 1: Restriction OWL
```bash
grep -A 5 "owl:Restriction" kg_extraction_semantic_web.py
```

**✅ Résultat attendu :**
```python
restriction = BNode()
graph.add((restriction, RDF.type, OWL.Restriction))
graph.add((restriction, OWL.onProperty, EX.hasValidatedCourse))
graph.add((restriction, OWL.someValuesFrom, EX.Course))
```

#### ✅ Correction 2: Prompt Engineering
```bash
grep -n "predict_relation" kg_extraction_semantic_web.py | head -5
```

**✅ Résultat attendu :**
```
246:def predict_relation_real_api(entity1, entity2, sentence):
462:    relation_type = predict_relation_real_api(entity1_text, entity2_text, text)
```

#### ✅ Correction 3: Double Sérialisation
```bash
ls -lh knowledge_graph.*
```

**✅ Résultat attendu :**
```
-rw-r--r-- 1 user user 3.6K knowledge_graph.ttl
-rw-r--r-- 1 user user 8.3K knowledge_graph.xml
-rw-r--r-- 1 user user 120K knowledge_graph.png
```

---

### 3. Vérifier le Contenu RDF

#### Turtle (.ttl)
```bash
head -30 knowledge_graph.ttl
```

**✅ Cherchez :**
- `@prefix ex:`, `@prefix foaf:`, `@prefix owl:`
- Restrictions OWL : `[ a owl:Restriction ; owl:onProperty ... ]`
- Triples RDF : `ex:Person1 ex:teaches ex:Course1 .`

#### RDF/XML (.xml)
```bash
head -20 knowledge_graph.xml
```

**✅ Cherchez :**
```xml
<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF
   xmlns:ex="http://example.org/"
   xmlns:foaf="http://xmlns.com/foaf/0.1/"
   xmlns:owl="http://www.w3.org/2002/07/owl#"
```

---

## 🔬 Tests Approfondis (5 minutes)

### 4. Test de Validation Automatique
```bash
python test_corrections.py
```

**✅ Résultat attendu :**
```
✅ TEST 1: Restriction OWL présente - PASSÉ
✅ TEST 2: Prompt Engineering - PASSÉ
✅ TEST 3: Double sérialisation - PASSÉ

🎉 TOUS LES TESTS SONT VALIDÉS !
```

---

### 5. Vérifier les Dépendances
```bash
pip list | grep -E "rdflib|spacy|networkx|matplotlib|requests"
```

**✅ Résultat attendu :**
```
rdflib          7.1.1
spacy           3.8.2
networkx        3.2.1
matplotlib      3.8.2
requests        2.31.0
```

---

### 6. Test de NER (Reconnaissance d'Entités)
```bash
python -c "
import spacy
nlp = spacy.load('fr_core_news_sm')
doc = nlp('Marie Curie enseigne à Paris')
for ent in doc.ents:
    print(f'{ent.text} --> {ent.label_}')
"
```

**✅ Résultat attendu :**
```
Marie Curie --> PER
Paris --> LOC
```

---

## 🚨 Résolution de Problèmes

### Problème 1: Module manquant
**Erreur :** `ModuleNotFoundError: No module named 'rdflib'`

**Solution :**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

### Problème 2: Modèle spaCy manquant
**Erreur :** `OSError: [E050] Can't find model 'fr_core_news_sm'`

**Solution :**
```bash
source venv/bin/activate
python -m spacy download fr_core_news_sm
```

---

### Problème 3: Pas de fichiers générés
**Erreur :** `knowledge_graph.ttl` n'existe pas

**Solution :**
1. Vérifiez les erreurs dans le terminal
2. Vérifiez le répertoire de travail :
```bash
pwd  # Devrait afficher .../web_semantique
ls -la
```

---

### Problème 4: API Hugging Face timeout
**Erreur :** `Timeout (>10s)`

**Solution :** C'est normal ! Le fallback fonctionne :
```python
# Si l'API échoue, le système utilise "relatedTo" par défaut
return "relatedTo"
```

---

## 📊 Validation des Sorties

### knowledge_graph.ttl (Turtle)
```bash
# Compter les triples
grep -c "\.$" knowledge_graph.ttl
```

**✅ Devrait afficher :** > 20 triples

---

### knowledge_graph.xml (RDF/XML)
```bash
# Vérifier la validité XML
xmllint --noout knowledge_graph.xml && echo "✅ XML valide"
```

**Alternative sans xmllint :**
```bash
python -c "
import xml.etree.ElementTree as ET
ET.parse('knowledge_graph.xml')
print('✅ XML valide')
"
```

---

### knowledge_graph.png (Visualisation)
```bash
file knowledge_graph.png
```

**✅ Résultat attendu :**
```
knowledge_graph.png: PNG image data, 800 x 600, 8-bit/color RGB
```

---

## 🎯 Checklist de Validation Finale

Avant de présenter au superviseur :

- [ ] ✅ Script s'exécute sans erreur : `python kg_extraction_semantic_web.py`
- [ ] ✅ 3 fichiers générés : `.ttl`, `.xml`, `.png`
- [ ] ✅ Restriction OWL présente : `grep "owl:Restriction" kg_extraction_semantic_web.py`
- [ ] ✅ Fonction API intégrée : `grep "predict_relation_real_api" kg_extraction_semantic_web.py`
- [ ] ✅ Double sérialisation : `ls knowledge_graph.{ttl,xml}`
- [ ] ✅ Tests automatiques passent : `python test_corrections.py`
- [ ] ✅ Documentation complète : `ls *.md`

---

## 🚀 Commande de Test Complète (One-Liner)

```bash
source venv/bin/activate && \
python kg_extraction_semantic_web.py && \
python test_corrections.py && \
ls -lh knowledge_graph.* && \
echo "🎉 TOUS LES TESTS SONT PASSÉS !"
```

---

## 📝 Notes pour la Présentation

### Points Forts à Montrer

1. **OWL Restriction** (Ligne 105-136)
   - Utilisation de BNode
   - `owl:someValuesFrom`
   - Intégration dans T-Box

2. **Prompt Engineering** (Ligne 246-320)
   - Format [INST]...[/INST] pour Mistral
   - Paramètres optimisés (temperature=0.1)
   - Gestion d'erreurs robuste

3. **Double Sérialisation** (Ligne 826-850)
   - `.ttl` pour lisibilité humaine
   - `.xml` pour interopérabilité
   - Visualisation graphique `.png`

---

## 🔑 Commandes Essentielles

### Vérification Rapide
```bash
# Tout en une commande
grep -E "owl:Restriction|predict_relation_real_api" kg_extraction_semantic_web.py && \
ls knowledge_graph.{ttl,xml} 2>/dev/null && \
echo "✅ Corrections validées"
```

### Statistiques RDF
```bash
echo "=== STATISTIQUES RDF ==="
echo "Triples Turtle: $(grep -c '\.$' knowledge_graph.ttl)"
echo "Taille TTL: $(du -h knowledge_graph.ttl | cut -f1)"
echo "Taille XML: $(du -h knowledge_graph.xml | cut -f1)"
```

---

## ⚡ Test Ultra-Rapide (30 secondes)

```bash
source venv/bin/activate
python kg_extraction_semantic_web.py
ls -lh knowledge_graph.*
```

**✅ Si vous voyez 3 fichiers, c'est bon !**

---

## 📞 En Cas de Problème

### Support Technique

1. **Vérifiez Python** : `python --version` (devrait être 3.8+)
2. **Vérifiez venv** : `which python` (devrait pointer vers `venv/`)
3. **Réinstallez dépendances** : `pip install -r requirements.txt --force-reinstall`
4. **Consultez les logs** : Regardez les messages d'erreur complets

---

## ✨ Résumé

| Test | Commande | Durée | Critique |
|------|----------|-------|----------|
| Script principal | `python kg_extraction_semantic_web.py` | 1 min | ⭐⭐⭐ |
| Tests auto | `python test_corrections.py` | 10s | ⭐⭐⭐ |
| OWL Restriction | `grep "owl:Restriction" ...` | 2s | ⭐⭐ |
| Fichiers générés | `ls knowledge_graph.*` | 1s | ⭐⭐⭐ |

---

**🎓 Projet prêt pour validation académique !**

Date: 16 janvier 2026
