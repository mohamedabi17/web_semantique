# ✅ Correction Ontologique : locatedIn pour Organisations et Lieux

## 🔧 Problème Identifié

**Erreur Sémantique :** Le LLM détectait `Meta --[worksAt]--> Paris`, ce qui est ontologiquement incorrect car :
- Une **Organisation** ne "travaille" pas
- Une **Organisation** est **située** (locatedIn) dans un lieu
- Seules les **Personnes** peuvent **travailler** (worksAt) dans des organisations

**Conséquence :** Le triplet `Meta worksAt Paris` violait la contrainte `rdfs:domain` de la propriété `worksAt` qui spécifie que seul un `foaf:Person` peut être le sujet de cette relation.

---

## ✨ Solution Implémentée

### 1. Ajout de la Propriété `locatedIn` dans le T-Box

**Fichier :** `kg_extraction_semantic_web.py` (lignes 203-210)

```python
# Propriété : Une organisation ou une personne est située dans un lieu
graph.add((EX.locatedIn, RDF.type, OWL.ObjectProperty))
graph.add((EX.locatedIn, RDFS.label, Literal("situé à", lang="fr")))
graph.add((EX.locatedIn, RDFS.domain, RDFS.Resource))  # Organisation ou Personne
graph.add((EX.locatedIn, RDFS.range, SCHEMA.Place))  # Dans un Lieu
graph.add((EX.locatedIn, RDFS.comment, 
           Literal("Relation de localisation géographique", lang="fr")))
```

**Contraintes Ontologiques :**
- **Domain :** `rdfs:Resource` (accepte organisations, personnes, etc.)
- **Range :** `schema:Place` (lieux géographiques uniquement)

### 2. Propriété `worksAt` Clarifiée

```python
# Propriété : Une personne travaille dans une organisation
graph.add((EX.worksAt, RDF.type, OWL.ObjectProperty))
graph.add((EX.worksAt, RDFS.label, Literal("travaille à", lang="fr")))
graph.add((EX.worksAt, RDFS.domain, FOAF.Person))  # Seules les Personnes
graph.add((EX.worksAt, RDFS.range, SCHEMA.Organization))  # Dans des Organisations
```

**Contraintes Ontologiques :**
- **Domain :** `foaf:Person` (seules les personnes peuvent travailler)
- **Range :** `schema:Organization` (uniquement dans des organisations)

---

### 3. Prompt LLM Amélioré

**Fichier :** `kg_extraction_semantic_web.py` (lignes 295-313)

```python
prompt = f"""Context: "{sentence}"
Analyze the relationship between the entities: "{entity1}" and "{entity2}".

You must choose ONE relation from this exact list:
1. teaches (if a PERSON teaches at a place or subject)
2. author (if a PERSON wrote something)
3. worksAt (if a PERSON works at an ORGANIZATION)
4. locatedIn (if an ORGANIZATION or PERSON is in a PLACE/CITY)
5. collaboratesWith (if two PERSONS work together)
6. studiesAt (if a PERSON studies at an ORGANIZATION)
7. manages (if a PERSON manages an ORGANIZATION)
8. relatedTo (default fallback)

IMPORTANT:
- Only PERSONS can worksAt organizations
- Organizations are locatedIn places, NOT worksAt
- Cities and places use locatedIn

Reply ONLY with the single word of the relation. No explanation."""
```

**Améliorations :**
- ✅ Ajout de `locatedIn` dans les choix
- ✅ Précision explicite : "PERSON works at ORGANIZATION"
- ✅ Instruction claire : "Organizations are locatedIn places"
- ✅ Ajout de relations supplémentaires (collaboratesWith, studiesAt, manages)

---

### 4. Heuristiques Intelligentes de Détection

**Fichier :** `kg_extraction_semantic_web.py` (lignes 335-350)

```python
# Détection de lieux connus (force locatedIn)
lieux_connus = ["Paris", "France", "Versailles", "Lyon", "Marseille", "Toulouse", 
                "Bordeaux", "Lille", "États-Unis", "USA", "New York", "Londres",
                "Californie", "Silicon Valley"]

for lieu in lieux_connus:
    if lieu.lower() in entity2.lower():
        print(f"  🔍 Détection de lieu '{lieu}' dans '{entity2}' → Force locatedIn")
        relation = "locatedIn"
        break
```

**Logique :**
- Si `entity2` contient un nom de ville/pays connu → **force `locatedIn`**
- Cela compense les erreurs potentielles du LLM
- Liste extensible avec d'autres lieux

---

### 5. Fallback avec Détection de Lieux

**Fichier :** `kg_extraction_semantic_web.py` (lignes 386-412)

```python
except Exception as e:
    print(f"  ⚠️ Erreur Groq ({str(e)[:80]}). Passage au fallback.")
    # Fallback avec détection de lieux
    sentence_lower = sentence.lower()
    entity2_lower = entity2.lower()
    
    # Détection de lieux dans le fallback
    lieux = ["paris", "france", "versailles", ...]
    
    for lieu in lieux:
        if lieu in entity2_lower:
            print(f"  🔍 Fallback : Détection de lieu '{lieu}' → locatedIn")
            return "locatedIn"
```

**Résilience :**
- Même si l'API Groq échoue, le système détecte correctement les lieux
- Double sécurité (API + fallback)

---

## 🧪 Tests de Validation

### Test 1 : Organisation → Lieu

**Texte :** `"Meta est situé à Paris."`

**Résultat :**
```
✓ Entité détectée : 'Meta' → Type : ORG
✓ Entité détectée : 'Paris' → Type : LOC
🔍 Détection de lieu 'Paris' dans 'Paris' → Force locatedIn
🤖 Groq/Llama-3 a détecté : Meta --[locatedIn]--> Paris
```

**RDF Généré :**
```turtle
data:meta a schema:Organization ;
    ex:locatedIn data:paris ;
    foaf:name "Meta"@fr .

data:paris a schema:Place ;
    foaf:name "Paris"@fr .
```

✅ **Correct !** Organisation → locatedIn → Lieu

---

### Test 2 : Personne → Organisation → Lieu

**Texte :** `"Yann LeCun travaille chez Meta. Meta est situé à Paris en France."`

**Résultat :**
```
✓ Entité détectée : 'Yann LeCun' → Type : PER
✓ Entité détectée : 'Meta' → Type : ORG
✓ Entité détectée : 'Paris' → Type : LOC
✓ Entité détectée : 'France' → Type : LOC

🤖 Groq/Llama-3 a détecté : Yann LeCun --[worksAt]--> Meta
🔍 Détection de lieu 'Paris' dans 'Paris' → Force locatedIn
🤖 Groq/Llama-3 a détecté : Meta --[locatedIn]--> Paris
🔍 Détection de lieu 'France' dans 'France' → Force locatedIn
🤖 Groq/Llama-3 a détecté : Paris --[locatedIn]--> France
```

**RDF Généré :**
```turtle
data:yann_lecun a foaf:Person ;
    ex:worksAt data:meta ;  # ✅ Personne → worksAt → Organisation
    foaf:name "Yann LeCun"@fr .

data:meta a schema:Organization ;
    ex:locatedIn data:paris ;  # ✅ Organisation → locatedIn → Lieu
    foaf:name "Meta"@fr .

data:paris a schema:Place ;
    ex:locatedIn data:france ;  # ✅ Lieu → locatedIn → Lieu
    foaf:name "Paris"@fr .

data:france a schema:Place ;
    foaf:name "France"@fr .
```

✅ **Parfait !** Toutes les relations sont ontologiquement correctes.

---

## 📊 Comparaison Avant/Après

| Cas | Avant (Incorrect) | Après (Correct) |
|-----|-------------------|-----------------|
| **Meta à Paris** | `Meta --[worksAt]--> Paris` ❌ | `Meta --[locatedIn]--> Paris` ✅ |
| **Yann LeCun chez Meta** | `Yann LeCun --[worksAt]--> Meta` ✅ | `Yann LeCun --[worksAt]--> Meta` ✅ |
| **Domaine worksAt** | Accepte tout ❌ | Restreint à `foaf:Person` ✅ |
| **Range worksAt** | Accepte tout ❌ | Restreint à `schema:Organization` ✅ |

---

## 🎯 Bénéfices de la Correction

### 1. Conformité Ontologique
✅ Les contraintes `rdfs:domain` et `rdfs:range` sont respectées  
✅ Pas de triplets violant les règles OWL  
✅ Graphe validable par un raisonneur OWL (Pellet, HermiT)

### 2. Interopérabilité
✅ Conforme aux standards Schema.org et FOAF  
✅ Compatible avec les graphes de connaissances existants (DBpedia, Wikidata)  
✅ Requêtes SPARQL plus précises et fiables

### 3. Qualité Sémantique
✅ Relations ontologiquement correctes  
✅ Distinction claire Personne vs Organisation vs Lieu  
✅ Modélisation cohérente du domaine

### 4. Intelligence du Système
✅ Détection automatique de lieux (heuristiques)  
✅ Prompt LLM explicite et pédagogique  
✅ Fallback robuste en cas d'erreur API

---

## 🚀 Utilisation

### Test Direct
```bash
cd /home/mohamedabi/Téléchargements/web_semantique
echo "Meta est situé à Paris." > texte_temp.txt
python kg_extraction_semantic_web.py
```

### Via Interface Streamlit
```bash
./run_streamlit.sh
# Saisir : "Yann LeCun travaille chez Meta à Paris."
# Observer : Relations correctes générées
```

### Vérification RDF
```bash
grep -E "(worksAt|locatedIn)" knowledge_graph.ttl
```

**Attendu :**
```turtle
data:yann_lecun ex:worksAt data:meta .
data:meta ex:locatedIn data:paris .
```

---

## 📚 Fichiers Modifiés

1. **kg_extraction_semantic_web.py**
   - Lignes 203-210 : Ajout propriété `locatedIn` (T-Box)
   - Lignes 195-202 : Clarification propriété `worksAt` (T-Box)
   - Lignes 295-313 : Prompt LLM amélioré
   - Lignes 335-350 : Heuristiques de détection de lieux
   - Lignes 386-412 : Fallback avec détection de lieux

---

## ✅ Checklist de Validation

- [x] Propriété `locatedIn` ajoutée dans T-Box
- [x] Contraintes `rdfs:domain` et `rdfs:range` définies
- [x] Prompt LLM mis à jour avec distinctions Personne/Organisation/Lieu
- [x] Heuristiques de détection de lieux implémentées
- [x] Fallback robuste avec détection de lieux
- [x] Tests validés : Meta → Paris ✅
- [x] Tests validés : Yann LeCun → Meta → Paris ✅
- [x] Relations ontologiquement correctes ✅

---

**🎉 Correction Ontologique Complète et Validée !**

---

*Correction appliquée - 16 janvier 2026*  
*Projet Master 2 Web Sémantique - Architecture T-Box/A-Box*
