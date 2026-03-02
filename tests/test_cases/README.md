# 🧪 Cas de Test - Généralisation du Pipeline

## Liste des Cas

### Cas 01 : Académique Classique

**Texte** : `Alice Martin enseigne les bases de données à l'Université Paris-Saclay. Elle travaille aussi au CNRS.`

**Entités attendues** : Alice Martin, bases de données, Université Paris-Saclay, CNRS

**Relations attendues** : teachesSubject, teaches, worksAt

---

### Cas 02 : Auteur + Enseignement

**Texte** : `Mohamed Bennani a écrit un livre sur l'Intelligence Artificielle. Il enseigne à l'ENSIAS de Rabat.`

**Entités attendues** : Mohamed Bennani, Intelligence Artificielle, ENSIAS, Rabat

**Relations attendues** : author, teaches, locatedIn

---

### Cas 03 : Technologies Sémantiques

**Texte** : `Jean Dupont a publié des articles sur SPARQL et OWL. Il dirige le laboratoire d'ontologies à Lyon.`

**Entités attendues** : Jean Dupont, SPARQL, OWL, laboratoire, Lyon

**Relations attendues** : author, manages, locatedIn

---

### Cas 04 : JSON-LD et Turtle

**Texte** : `Sophie Durand enseigne JSON-LD et Turtle à l'Université de Nantes. Elle collabore avec l'INRIA.`

**Entités attendues** : Sophie Durand, JSON-LD, Turtle, Université de Nantes, INRIA

**Relations attendues** : teachesSubject, teaches, collaboratesWith

---

### Cas 05 : Hiérarchie Organisationnelle

**Texte** : `Pierre Rousseau dirige le département informatique. Il travaille à l'École Polytechnique de Paris.`

**Entités attendues** : Pierre Rousseau, département informatique, École Polytechnique, Paris

**Relations attendues** : manages, worksAt, locatedIn

---

### Cas 06 : Relationnel Complexe

**Texte** : `Fatima El Amrani étudie la sémantique formelle à l'Université Mohammed V. Elle collabore avec des chercheurs de Casablanca.`

**Entités attendues** : Fatima El Amrani, sémantique formelle, Université Mohammed V, Casablanca

**Relations attendues** : studiesAt, relatedTo, locatedIn

---

### Cas 07 : RDFS + Graphes

**Texte** : `Laura Sanchez a écrit des tutoriels sur RDFS et les graphes de connaissances. Elle enseigne à Barcelone.`

**Entités attendues** : Laura Sanchez, RDFS, graphes de connaissances, Barcelone

**Relations attendues** : author, teaches

---

### Cas 08 : Multi-Matières

**Texte** : `Thomas Bernard enseigne les mathématiques et la physique à l'Université de Toulouse. Il gère le département sciences.`

**Entités attendues** : Thomas Bernard, mathématiques, physique, Université de Toulouse, département sciences

**Relations attendues** : teachesSubject, teaches, manages

---

### Cas 09 : Relations Géographiques

**Texte** : `Marie Leblanc travaille au laboratoire GREYC à Caen. Elle collabore avec l'Université de Versailles.`

**Entités attendues** : Marie Leblanc, GREYC, Caen, Université de Versailles

**Relations attendues** : worksAt, locatedIn, collaboratesWith

---

### Cas 10 : Ontologie Médicale

**Texte** : `David Cohen a écrit une thèse sur l'ontologie médicale. Il enseigne à l'hôpital universitaire de Strasbourg et collabore avec le CHU.`

**Entités attendues** : David Cohen, ontologie médicale, hôpital universitaire, Strasbourg, CHU

**Relations attendues** : author, teaches, locatedIn, collaboratesWith

---

### Cas 11 : Bilingue (Anglais)

**Texte** : `Emily Johnson teaches computer science at MIT. She published papers on semantic web and ontology.`

**Entités attendues** : Emily Johnson, computer science, MIT, semantic web, ontology

**Relations attendues** : teachesSubject, teaches, author

---

### Cas 12 : Validation OWL Stricte (Rejet attendu)

**Texte** : `Le Web Sémantique enseigne à Paris.`

**Entités attendues** : Web Sémantique, Paris

**Relations attendues** : 

**⚠️ Rejet attendu** : Violation de contrainte OWL (domain/range)

---

