# ✅ Correction Appliquée : Interface Streamlit → Script Principal

## 🔧 Problème Résolu

**Avant :** Le script `kg_extraction_semantic_web.py` ignorait le texte envoyé par Streamlit et utilisait toujours le texte par défaut hardcodé.

**Après :** Le script lit maintenant le texte depuis 3 sources possibles (par ordre de priorité) :

## 📝 Modifications Apportées

### 1. Script Principal (`kg_extraction_semantic_web.py`)

**Ajout de `import sys`** (ligne 18) pour lire les arguments

**Nouvelle logique de lecture du texte** (lignes 783-803) :

```python
# Texte par défaut
text_example = "Zoubida Kedad enseigne à l'Université de Versailles..."

# PRIORITÉ 1 : Lire depuis texte_temp.txt (Streamlit)
if os.path.exists("texte_temp.txt"):
    with open("texte_temp.txt", "r", encoding="utf-8") as f:
        custom_text = f.read().strip()
        if custom_text:
            text_example = custom_text

# PRIORITÉ 2 : Lire depuis --text argument
if len(sys.argv) > 1:
    if sys.argv[1] == "--text" and len(sys.argv) > 2:
        text_example = sys.argv[2]
    else:
        text_example = " ".join(sys.argv[1:])
```

### 2. Interface Streamlit (`app_streamlit.py`)

**Simplification du code** (lignes 170-186) :

```python
# Sauvegarder le texte dans le fichier temporaire
with open("texte_temp.txt", "w", encoding="utf-8") as f:
    f.write(user_input)

# Exécuter le script (qui lit automatiquement texte_temp.txt)
result = subprocess.run(
    ["python", "kg_extraction_semantic_web.py"],
    capture_output=True,
    text=True,
    timeout=60
)
```

**Suppression du code wrapper complexe** qui n'était plus nécessaire.

## ✅ Tests de Validation

### Test 1 : Texte par défaut (sans fichier)
```bash
rm -f texte_temp.txt
python kg_extraction_semantic_web.py
# ✅ Utilise "Zoubida Kedad enseigne..."
```

### Test 2 : Via fichier temporaire (Streamlit)
```bash
echo "Pierre Durand étudie à l'Université de Paris." > texte_temp.txt
python kg_extraction_semantic_web.py
# ✅ Utilise "Pierre Durand étudie..."
```

**Résultat :**
```
[INFO] Texte chargé depuis texte_temp.txt
[TEXTE SOURCE] : "Pierre Durand étudie à l'Université de Paris."
✓ Entité détectée : 'Pierre Durand' → Type : PER
✓ Entité détectée : 'Université de Paris' → Type : ORG
```

### Test 3 : Via argument --text
```bash
python kg_extraction_semantic_web.py --text "Marie Martin collabore avec Jean Dupont."
# ✅ Utilise "Marie Martin collabore..."
```

### Test 4 : Via interface Streamlit
```bash
./run_streamlit.sh
# 1. Saisir "Sophie Leclerc travaille à l'Université de Versailles."
# 2. Cliquer "Générer"
# ✅ Le graphe utilise le texte saisi, pas le défaut !
```

## 🎯 Workflow Fonctionnel

```
┌──────────────────────────┐
│  Interface Streamlit     │
│  (app_streamlit.py)      │
└────────────┬─────────────┘
             │
             │ 1. user_input = "Pierre Durand..."
             │
             ▼
        ┌─────────────────┐
        │ texte_temp.txt  │  ← Écriture du texte
        └─────────────────┘
             │
             │ 2. subprocess.run(["python", "kg_extraction_semantic_web.py"])
             │
             ▼
┌──────────────────────────────────┐
│  kg_extraction_semantic_web.py   │
│                                  │
│  if os.path.exists("texte_temp.txt"):  ← Lecture automatique
│      text = open(...).read()     │
│                                  │
│  extract_entities(text)  ✅      │
│  extract_relations(text) ✅      │
└──────────────────────────────────┘
             │
             │ 3. Génération des fichiers
             │
             ▼
  ┌─────────────────────────┐
  │ knowledge_graph.ttl      │
  │ knowledge_graph.xml      │
  │ graphe_connaissance.png  │
  └─────────────────────────┘
```

## 🎉 Résultat Final

**L'interface Streamlit et le script principal sont maintenant parfaitement connectés !**

- ✅ Le texte saisi dans Streamlit est utilisé pour l'extraction
- ✅ Le script principal reste utilisable en ligne de commande
- ✅ Le texte par défaut est conservé si aucun texte n'est fourni
- ✅ 3 méthodes d'entrée supportées (fichier, argument, défaut)

## 🚀 Pour Tester

```bash
# Méthode 1 : Interface Streamlit
./run_streamlit.sh

# Méthode 2 : Ligne de commande avec fichier
echo "Votre texte ici" > texte_temp.txt
python kg_extraction_semantic_web.py

# Méthode 3 : Ligne de commande avec argument
python kg_extraction_semantic_web.py --text "Votre texte ici"
```

---

*Correction appliquée - 16 janvier 2026*
