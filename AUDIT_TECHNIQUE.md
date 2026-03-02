# 🔍 AUDIT TECHNIQUE - ANALYSE CRITIQUE DE L'IMPLÉMENTATION

**Examinateur** : Professeur en Web Sémantique  
**Date** : 17 février 2026  
**Candidat** : Master 2 - Architecture Neuro-Symbolique pour KG

---

## 📋 MÉTHODOLOGIE D'AUDIT

Analyse systématique du code source pour vérifier :
1. **Existence réelle** des composants annoncés
2. **Complétude** de l'implémentation
3. **Conformité** avec la théorie OWL/RDFS
4. **Écarts** entre architecture annoncée et code réel

**Critères d'évaluation** :
- ✅ **Implémenté** : Code complet et fonctionnel
- ⚠️ **Partiel** : Implémentation simplifiée ou incomplète
- ❌ **Absent** : Non implémenté ou simulé

---

## 🔬 MODULE 0++ : NER HYBRIDE

### Architecture Annoncée
```
1) spaCy NER baseline
2) EntityRuler avec patterns
3) Heuristiques linguistiques
4) Normalisation + déduplication
5) Filtrage par confiance
6) Vérification type ontologique
7) Mapping lemme → propriété OWL
```

### Code Réel Trouvé

**Fichier** : `kg_extraction_semantic_web.py` ligne 686

```python
def extract_entities_with_spacy(text, nlp):
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        entities.append((ent.text, ent.label_))
    return entities
```

### ❌ VERDICT MODULE 0++ : **SIMPLIFICATION MAJEURE**

| Composant Annoncé | État | Preuve |
|-------------------|------|--------|
| spaCy NER baseline | ✅ Présent | `doc.ents` ligne 704 |
| EntityRuler | ❌ **ABSENT** | Aucune trace de `nlp.add_pipe("entity_ruler")` |
| Heuristiques linguistiques | ❌ **ABSENT** | Pas de `token.pos_ == "PROPN"` ni analyse syntaxique |
| Normalisation | ❌ **ABSENT** | Pas de `normalize_entity()` appelée |
| Déduplication | ❌ **ABSENT** | Pas de `set()` ni vérification doublons |
| Filtrage confiance | ❌ **ABSENT** | Pas de `ent._.score` ni seuil |
| Vérification ontologique | ❌ **ABSENT** | Pas d'appel à `validate_entity_type()` |
| Mapping lemme | ❌ **ABSENT** | Pas de `smart_relation_mapper()` intégré |

### 📊 Score Module 0++ : **1/7 = 14%**

**Conclusion** : Vous n'avez implémenté qu'un **wrapper basique autour de spaCy NER**. 
C'est une extraction NER standard, **PAS une architecture hybride**.

---

## 🔬 MODULE 3 : PROMPT BUILDER GUIDÉ ONTOLOGIE

### Architecture Annoncée
```
1) Extraction automatique classes OWL
2) Extraction propriétés avec domain/range
3) Inclusion contraintes dans prompts
4) Format contraint (JSON forcé)
5) LLM propose uniquement relations valides
```

### Code Réel Trouvé

**Fichier** : `ontology_prompt_builder.py` ligne 1-200

```python
class OntologyPromptBuilder:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.classes = {}
        self.properties = {}
        self._extract_ontology_schema()
    
    def _extract_ontology_schema(self):
        # Extraction des classes (owl:Class)
        for class_uri, _, _ in self.graph.triples((None, RDF.type, OWL.Class)):
            self.classes[class_uri] = self._extract_class_metadata(class_uri)
        
        # Extraction des ObjectProperties
        for prop_uri, _, _ in self.graph.triples((None, RDF.type, OWL.ObjectProperty)):
            self.properties[prop_uri] = self._extract_property_metadata(prop_uri, "ObjectProperty")
```

### ✅ VERDICT MODULE 3 : **IMPLÉMENTÉ CORRECTEMENT**

| Composant Annoncé | État | Preuve |
|-------------------|------|--------|
| Extraction classes OWL | ✅ **Présent** | `_extract_ontology_schema()` ligne 51 |
| Extraction propriétés | ✅ **Présent** | Boucle sur `OWL.ObjectProperty` ligne 59 |
| Domain/range | ✅ **Présent** | `_extract_property_metadata()` ligne 97 |
| Format contraint | ✅ **Présent** | `_build_relations_list()` ligne 161 |
| Prompts structurés | ✅ **Présent** | `build_relation_extraction_prompt()` ligne 133 |

### 📊 Score Module 3 : **5/5 = 100%**

**Conclusion** : Module 3 est **fidèlement implémenté**. 
L'extraction de l'ontologie est dynamique et les prompts sont bien guidés par le schéma OWL.

---

## 🔬 MODULE 1 : VALIDATION ONTOLOGIQUE

### Architecture Annoncée
```
1) Vérification domain (rdfs:domain)
2) Vérification range (rdfs:range)
3) Hiérarchie classes (rdfs:subClassOf)
4) Raisonnement OWL (owlrl ou équivalent)
```

### Code Réel Trouvé

**Fichier** : `ontology_validator.py` ligne 1-307

```python
class OntologyConstraintValidator:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.property_domains = {}
        self.property_ranges = {}
        self.class_hierarchy = {}
        self._extract_ontology_constraints()
    
    def validate_triple(self, subject: URIRef, predicate: URIRef, obj: URIRef):
        subject_types = self._get_entity_types(subject)
        object_types = self._get_entity_types(obj)
        
        # VALIDATION DU DOMAINE
        if predicate in self.property_domains:
            required_domains = self.property_domains[predicate]
            if not self._is_compatible_type(subject_types, required_domains):
                return False, "DOMAIN VIOLATION"
        
        # VALIDATION DE LA PORTÉE
        if predicate in self.property_ranges:
            required_ranges = self.property_ranges[predicate]
            if not self._is_compatible_type(object_types, required_ranges):
                return False, "RANGE VIOLATION"
```

### ⚠️ VERDICT MODULE 1 : **PARTIEL (75%)**

| Composant Annoncé | État | Preuve |
|-------------------|------|--------|
| Vérification domain | ✅ **Présent** | `validate_triple()` ligne 164-174 |
| Vérification range | ✅ **Présent** | `validate_triple()` ligne 176-183 |
| Hiérarchie classes | ✅ **Présent** | `_extract_ontology_constraints()` ligne 80 |
| Raisonnement OWL (owlrl) | ❌ **ABSENT** | Pas d'import `owlrl`, pas de `DeductiveClosure` |

### 📊 Score Module 1 : **3/4 = 75%**

**Conclusion** : Module 1 valide correctement domain/range et gère la hiérarchie.
**MAIS** : Pas de véritable raisonnement OWL (pas d'owlrl, pas d'inférence de types).
C'est une **validation syntaxique**, pas un **raisonneur OWL complet**.

---

## 🔬 MODULE 2 : RAISONNEMENT TRANSITIF

### Architecture Annoncée
```
1) Détection owl:TransitiveProperty
2) Fermeture itérative jusqu'à point fixe
3) Protection cycles infinis
4) Métadonnées de provenance
```

### Code Réel Trouvé

**Fichier** : `transitive_reasoner.py` ligne 1-390

```python
class TransitiveInferenceEngine:
    def _detect_transitive_properties(self):
        for prop, _, _ in self.graph.triples((None, RDF.type, OWL.TransitiveProperty)):
            if isinstance(prop, URIRef):
                self.transitive_properties.append(prop)
    
    def _build_transitive_closure(self, property_uri: URIRef):
        # Algorithme de Floyd-Warshall adapté
        max_iterations = 100
        iteration = 0
        
        while iteration < max_iterations:
            new_relations = False
            
            for source in list(relations.keys()):
                for intermediate in intermediates:
                    if intermediate in relations:
                        for target in targets:
                            if source != target and target not in relations[source]:
                                relations[source].add(target)
                                inferred.append((source, property_uri, target))
                                new_relations = True
            
            if not new_relations:
                break
            
            iteration += 1
```

### ✅ VERDICT MODULE 2 : **IMPLÉMENTÉ CORRECTEMENT**

| Composant Annoncé | État | Preuve |
|-------------------|------|--------|
| Détection owl:TransitiveProperty | ✅ **Présent** | `_detect_transitive_properties()` ligne 56 |
| Fermeture itérative | ✅ **Présent** | Boucle `while` ligne 111 |
| Point fixe | ✅ **Présent** | `if not new_relations: break` ligne 149 |
| Protection cycles | ✅ **Présent** | `max_iterations = 100` ligne 108 |
| Provenance | ✅ **Présent** | `_add_inference_metadata()` ligne 244 |

### 📊 Score Module 2 : **5/5 = 100%**

**Conclusion** : Module 2 est **correctement implémenté**. 
Algorithme de fermeture transitive avec détection de point fixe et protection contre les cycles.

---

## 📊 TABLEAU RÉCAPITULATIF

| Module | Annoncé | Réel | Score | Verdict |
|--------|---------|------|-------|---------|
| **Module 0++** | NER hybride 7 couches | spaCy NER basique | **14%** | ❌ **SIMPLIFICATION MAJEURE** |
| **Module 3** | Prompt builder ontologique | Extraction OWL dynamique | **100%** | ✅ **FIDÈLE** |
| **Module 1** | Validation + raisonnement OWL | Domain/range sans owlrl | **75%** | ⚠️ **PARTIEL** |
| **Module 2** | Inférence transitive | Fermeture itérative | **100%** | ✅ **FIDÈLE** |

---

## 🎯 ÉCARTS CRITIQUES IDENTIFIÉS

### 1. **Module 0++ : Écart Architecture ↔ Code**

**Vous avez annoncé** :
```python
# Architecture neuro-symbolique hybride
- spaCy NER (couche 1)
- EntityRuler patterns (couche 2)
- Heuristiques PROPN (couche 3)
- Normalisation (couche 4)
- Filtrage confiance (couche 5)
- Validation ontologique (couche 6)
- Mapping verbes→OWL (couche 7)
```

**Vous avez implémenté** :
```python
def extract_entities_with_spacy(text, nlp):
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        entities.append((ent.text, ent.label_))  # C'est tout
    return entities
```

**Conclusion** : Ceci n'est **PAS** une architecture hybride. 
C'est un simple appel à `doc.ents`. **Aucune des 7 couches n'est présente**.

---

### 2. **Module 1 : Pas de Raisonneur OWL**

**Vous avez annoncé** :
> "Raisonnement OWL (rdflib + owlrl ou équivalent)"

**Vérification** :
```bash
$ grep -r "owlrl" .
# Aucun résultat

$ grep -r "DeductiveClosure" .
# Aucun résultat

$ grep -r "import owlrl" .
# Aucun résultat
```

**Conclusion** : Pas de raisonneur OWL réel. 
Vous faites de la **validation syntaxique**, pas du **raisonnement sémantique**.

---

### 3. **Filtrage par Confiance : Absent**

**Recherche dans le code** :
```bash
$ grep -r "confidence" kg_extraction_semantic_web.py
# Ligne 1017: # graph.add((statement_uri, EX.confidence, Literal(0.95)))
# ^^^ COMMENTÉ
```

**Conclusion** : Le système de confiance est **commenté**, donc **non actif**.

---

## 🔴 POINTS BLOQUANTS POUR SOUTENANCE

### 1. **Incohérence Documentation ↔ Code**

Votre `ARCHITECTURE_UPGRADE_PLAN.md` décrit :
- 6 couches d'extraction hybride
- VerbSemanticEngine avec lemmes
- DynamicOntologyProposer

**OR** : Ces modules existent en standalone mais **ne sont PAS intégrés** dans `kg_extraction_semantic_web.py`.

### 2. **Module 0 : Fausse Présentation**

Vous ne pouvez PAS présenter `extract_entities_with_spacy()` comme un "NER hybride" 
alors que c'est un **wrapper basique** autour de spaCy.

### 3. **Module 1 : Pas de Raisonnement OWL**

Sans owlrl, vous ne faites **PAS** de raisonnement OWL au sens académique.
Vous faites de la **validation de contraintes**, ce qui est différent.

---

## ✅ CE QUI FONCTIONNE BIEN

### 1. **Module 3 : Excellente Implémentation**
- Extraction dynamique de l'ontologie
- Prompts bien guidés par domain/range
- Code propre et modulaire

### 2. **Module 2 : Raisonnement Transitif Correct**
- Algorithme de fermeture bien implémenté
- Détection de point fixe
- Métadonnées de provenance

### 3. **Architecture T-Box/A-Box**
- Séparation claire ontologie/données
- Utilisation standards FOAF/Schema.org
- Réification RDF présente

---

## 📝 RECOMMANDATIONS POUR SOUTENANCE

### 1. **Reformuler Module 0**

**Au lieu de** :
> "Module 0++ : NER hybride multi-couches avec EntityRuler et heuristiques"

**Dire** :
> "Module 0 : Extraction NER avec spaCy (fr_core_news_sm) suivi d'un raffinement LLM pour détection de topics académiques"

### 2. **Clarifier Module 1**

**Au lieu de** :
> "Raisonnement OWL avec owlrl"

**Dire** :
> "Validation de contraintes ontologiques (domain/range) avec support hiérarchie de classes. Note: pas de raisonneur OWL complet, validation syntaxique uniquement."

### 3. **Séparer Implémentation ↔ Proposition**

**Slide 1** : "Implémentation actuelle"
- Module 3 (prompt builder) ✅
- Module 2 (transitivité) ✅
- Module 1 (validation domain/range) ⚠️ partiel
- Module 0 (spaCy NER) ✅ basique

**Slide 2** : "Extensions proposées (standalone, non intégrées)"
- HybridEntityExtractor (6 couches)
- VerbSemanticEngine
- DynamicOntologyProposer

---

## 🎓 VERDICT FINAL

### Score Global : **72% (Partiellement Fidèle)**

**Détail** :
- Module 0++ : 14% ❌
- Module 3 : 100% ✅
- Module 1 : 75% ⚠️
- Module 2 : 100% ✅

### Qualification

**❌ Implémentation Fidèle** : Non, écarts trop importants sur Module 0  
**⚠️ Implémentation Partielle** : **OUI**, 2/4 modules complets, 1 partiel, 1 absent  
**❌ Implémentation Simplifiée** : Oui pour Module 0 et Module 1

---

## 💡 POINTS POSITIFS À VALORISER

1. ✅ **Architecture T-Box/A-Box** bien séparée
2. ✅ **Module 3** excellent (prompt builder ontologique)
3. ✅ **Module 2** correct (transitivité)
4. ✅ **Standards respectés** (FOAF, Schema.org, OWL)
5. ✅ **Code modulaire** et documenté
6. ✅ **Tests présents** (17 cas de validation)

---

## ⚠️ POINTS À AMÉLIORER AVANT SOUTENANCE

1. ❌ Intégrer réellement les modules standalone (ou ne pas les présenter comme implémentés)
2. ❌ Implémenter au moins 3/7 couches du Module 0 (PROPN + normalisation + déduplication minimum)
3. ❌ Ajouter owlrl OU reformuler Module 1 comme "validation" et non "raisonnement"
4. ❌ Activer le système de confiance (décommenter ligne 1017)
5. ❌ Synchroniser documentation ↔ code réel

---

## 📌 CONCLUSION DE L'AUDIT

Votre projet présente une **architecture théorique solide** avec des **modules bien conçus**,
MAIS il y a un **écart significatif** entre ce qui est **annoncé** et ce qui est **implémenté**.

**Pour une soutenance acceptable** :
- Soit vous intégrez les modules standalone avant soutenance
- Soit vous reformulez votre présentation pour refléter l'implémentation réelle

**Points forts** : Modules 2 et 3 sont excellents.  
**Point faible** : Module 0 est trop basique pour être qualifié d'hybride.

**Note estimée** : 13-14/20 (état actuel)  
**Note potentielle** : 16-17/20 (avec corrections)

---

**Examinateur** : Professeur Web Sémantique  
**Recommandation** : Intégrer au minimum la normalisation + déduplication dans Module 0  
**Statut** : Projet valable mais nécessite clarifications avant présentation
