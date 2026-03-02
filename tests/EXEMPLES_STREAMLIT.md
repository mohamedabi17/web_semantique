# 🧪 EXEMPLES DE TEST POUR STREAMLIT

## Comment Utiliser

1. Lancez Streamlit : `streamlit run app_streamlit.py`
2. Sélectionnez **"🎓 Démo 1: Extraction Complète (NER + Relations)"**
3. Copiez-collez les textes ci-dessous dans la zone de saisie
4. Observez les résultats

---

## 📝 Cas 1 : Académique Classique
**Test** : Extraction basique avec enseignement et emploi

```
Alice Martin enseigne les bases de données à l'Université Paris-Saclay. Elle travaille aussi au CNRS.
```

**Attendu** :
- 4 entités : Alice Martin (PER), bases de données (TOPIC), Université Paris-Saclay (ORG), CNRS (ORG)
- 3 relations : teachesSubject, teaches, worksAt

---

## 📝 Cas 2 : Auteur + Enseignement
**Test** : Combinaison author et teaches

```
Mohamed Bennani a écrit un livre sur l'Intelligence Artificielle. Il enseigne à l'ENSIAS de Rabat.
```

**Attendu** :
- 4 entités : Mohamed Bennani (PER), Intelligence Artificielle (TOPIC), ENSIAS (ORG), Rabat (PLACE)
- 3 relations : author, teaches, locatedIn

---

## 📝 Cas 3 : Technologies Sémantiques (SPARQL + OWL)
**Test** : Détection des technologies du web sémantique

```
Jean Dupont a publié des articles sur SPARQL et OWL. Il dirige le laboratoire d'ontologies à Lyon.
```

**Attendu** :
- 5 entités : Jean Dupont (PER), SPARQL (DOCUMENT), OWL (DOCUMENT), laboratoire (ORG), Lyon (PLACE)
- 3+ relations : author × 2, manages, locatedIn

---

## 📝 Cas 4 : JSON-LD et Turtle
**Test** : Détection formats de sérialisation RDF

```
Sophie Durand enseigne JSON-LD et Turtle à l'Université de Nantes. Elle collabore avec l'INRIA.
```

**Attendu** :
- 5 entités : Sophie Durand (PER), JSON-LD (DOCUMENT→TOPIC), Turtle (DOCUMENT→TOPIC), Université de Nantes (ORG), INRIA (ORG)
- 4 relations : teachesSubject × 2, teaches, collaboratesWith

---

## 📝 Cas 5 : Hiérarchie Organisationnelle
**Test** : Relations de management

```
Pierre Rousseau dirige le département informatique. Il travaille à l'École Polytechnique de Paris.
```

**Attendu** :
- 4 entités : Pierre Rousseau (PER), département informatique (ORG), École Polytechnique (ORG), Paris (PLACE)
- 3 relations : manages, worksAt, locatedIn

---

## 📝 Cas 6 : Relations Complexes (studiesAt)
**Test** : Étudiant + collaborations

```
Fatima El Amrani étudie la sémantique formelle à l'Université Mohammed V. Elle collabore avec des chercheurs de Casablanca.
```

**Attendu** :
- 4+ entités : Fatima El Amrani (PER), sémantique formelle (TOPIC), Université Mohammed V (ORG), Casablanca (PLACE)
- 2+ relations : studiesAt, relatedTo, locatedIn

---

## 📝 Cas 7 : RDFS + Graphes de Connaissances
**Test** : Concepts avancés du web sémantique

```
Laura Sanchez a écrit des tutoriels sur RDFS et les graphes de connaissances. Elle enseigne à Barcelone.
```

**Attendu** :
- 4 entités : Laura Sanchez (PER), RDFS (DOCUMENT), graphes de connaissances (TOPIC), Barcelone (PLACE)
- 2+ relations : author × 2, teaches

---

## 📝 Cas 8 : Multi-Matières
**Test** : Enseignement de plusieurs matières

```
Thomas Bernard enseigne les mathématiques et la physique à l'Université de Toulouse. Il gère le département sciences.
```

**Attendu** :
- 5 entités : Thomas Bernard (PER), mathématiques (TOPIC), physique (TOPIC), Université de Toulouse (ORG), département sciences (ORG)
- 4 relations : teachesSubject × 2, teaches, manages

---

## 📝 Cas 9 : Relations Géographiques
**Test** : Localisation d'organisations

```
Marie Leblanc travaille au laboratoire GREYC à Caen. Elle collabore avec l'Université de Versailles.
```

**Attendu** :
- 4 entités : Marie Leblanc (PER), GREYC (ORG), Caen (PLACE), Université de Versailles (ORG)
- 3 relations : worksAt, locatedIn, collaboratesWith

---

## 📝 Cas 10 : Ontologie Médicale
**Test** : Domaine spécialisé (médical)

```
David Cohen a écrit une thèse sur l'ontologie médicale. Il enseigne à l'hôpital universitaire de Strasbourg et collabore avec le CHU.
```

**Attendu** :
- 5 entités : David Cohen (PER), ontologie médicale (TOPIC), hôpital universitaire (ORG), Strasbourg (PLACE), CHU (ORG)
- 4 relations : author, teaches, locatedIn, collaboratesWith

---

## 📝 Cas 11 : Texte Bilingue (Anglais)
**Test** : Traitement de l'anglais

```
Emily Johnson teaches computer science at MIT. She published papers on semantic web and ontology.
```

**Attendu** :
- 5 entités : Emily Johnson (PER), computer science (TOPIC), MIT (ORG), semantic web (TOPIC), ontology (TOPIC)
- 3+ relations : teachesSubject, teaches, author × 2

---

## 📝 Cas 12 : Validation OWL Stricte ⚠️
**Test** : Rejet de relation invalide (TOPIC enseigne à PLACE = violation domain)

```
Le Web Sémantique enseigne à Paris.
```

**Attendu** :
- 2 entités : Web Sémantique (TOPIC), Paris (PLACE)
- 0 relation ✅ (rejet attendu car "teaches" exige domain=Person)
- Message : `⚠️ Type domain invalide pour Web Sémantique`

---

## 🎯 Critères de Validation

Pour chaque test, vérifiez :

1. ✅ **Entités détectées** : Nombre et types corrects
2. ✅ **Relations créées** : Propriétés OWL appropriées
3. ✅ **Validation OWL** : Respect des contraintes domain/range
4. ✅ **Scores de confiance** : > 0.6 pour toutes les entités
5. ✅ **Graphe NetworkX** : Visualisation claire (A-Box uniquement)
6. ✅ **Export Turtle** : Triplets RDF bien formés

---

## 📊 Résultats Attendus

| Cas | Entités | Relations | Validation OWL | Statut |
|-----|---------|-----------|----------------|--------|
| 1   | 4       | 3         | ✅ Passé       | ✅     |
| 2   | 4       | 3         | ✅ Passé       | ✅     |
| 3   | 5       | 3+        | ✅ Passé       | ✅     |
| 4   | 5       | 4         | ✅ Passé       | ✅     |
| 5   | 4       | 3         | ✅ Passé       | ✅     |
| 6   | 4+      | 2+        | ✅ Passé       | ✅     |
| 7   | 4       | 2+        | ✅ Passé       | ✅     |
| 8   | 5       | 4         | ✅ Passé       | ✅     |
| 9   | 4       | 3         | ✅ Passé       | ✅     |
| 10  | 5       | 4         | ✅ Passé       | ✅     |
| 11  | 5       | 3+        | ✅ Passé       | ✅     |
| 12  | 2       | 0         | ⚠️ Rejet       | ✅     |

---

## 💡 Utilisation Avancée

### Test Rapide dans Terminal

```bash
# Test d'un cas spécifique
python3 kg_extraction_semantic_web.py < tests/test_cases/cas_01_académique_classique.txt

# Test de tous les cas
bash tests/run_all_tests.sh
```

### Analyse des Logs

```bash
# Voir seulement les entités détectées
python3 kg_extraction_semantic_web.py < tests/test_cases/cas_03_*.txt 2>&1 | grep "✓.*→"

# Voir seulement les relations
python3 kg_extraction_semantic_web.py < tests/test_cases/cas_03_*.txt 2>&1 | grep "🤖.*--\["

# Voir les rejets de validation
python3 kg_extraction_semantic_web.py < tests/test_cases/cas_12_*.txt 2>&1 | grep "⚠️"
```

---

## 🎓 Pour la Soutenance

**Démonstration suggérée** :

1. **Démarrer** avec Cas 1 (simple et propre)
2. **Montrer** Cas 3 ou 4 (technologies sémantiques - expertise du domaine)
3. **Impressionner** avec Cas 8 (multi-relations complexes)
4. **Valider** avec Cas 12 (rejet correct = robustesse OWL)

**Argumentaire** :
> "Notre système généralise sur 12 cas variés couvrant :
> - ✅ Domaines académiques classiques
> - ✅ Technologies du web sémantique (RDF, SPARQL, OWL, JSON-LD, Turtle)
> - ✅ Relations complexes (enseignement, authorship, management, collaboration)
> - ✅ Validation OWL stricte (rejet de triplets invalides)
> - ✅ Traitement bilingue (français/anglais)"

---

**Créé le** : 1 mars 2026  
**Dernière mise à jour** : 1 mars 2026
