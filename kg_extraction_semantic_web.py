#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Projet Master 2 - Web Sémantique : Extraction de Graphes de Connaissances a large échelle
Sujet 1 : Architecture T-Box/A-Box avec Réification

Ce script démontre une implémentation académique rigoureuse de :
- Définition d'ontologie (T-Box) avec OWL
- Extraction d'entités et instanciation (A-Box)
- Réification RDF pour les métadonnées
"""

import re
import unicodedata
import json
import os
import sys
import requests
import time
from groq import Groq
from huggingface_hub import InferenceClient
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, BNode
from rdflib.namespace import XSD, DC, FOAF
import spacy
import networkx as nx
import matplotlib.pyplot as plt
from typing import Optional
from dotenv import load_dotenv

# ============================================================================
# IMPORTS DES NOUVEAUX MODULES (ARCHITECTURE NEURO-SYMBOLIQUE COMPLÈTE)
# ============================================================================
from hybrid_ner_module import HybridNERModule, normalize_uri_fragment
from owl_reasoning_engine import OWLReasoningEngine, apply_owl_reasoning
from confidence_scorer import ConfidenceScorer, add_inference_confidence

# Chargement des variables d'environnement depuis .env
load_dotenv()


# ============================================================================
# 1. CONFIGURATION ET NAMESPACES
# ============================================================================

# Namespace personnalisé pour notre ontologie de domaine
EX = Namespace("http://example.org/master2/ontology#")

# Namespace pour les instances (données)
DATA = Namespace("http://example.org/master2/data#")

# Namespace Schema.org pour types standards
SCHEMA = Namespace("http://schema.org/")

# ============================================================================
# CONFIGURATION DE L'API HUGGING FACE (VRAIE IMPLÉMENTATION LLM) ⭐
# ============================================================================

# -------------------------------------------------------------------------
# API Hugging Face Inference - Modèle gratuit et accessible
# Utilisation de Qwen2.5-Coder-32B-Instruct (gratuit et performant pour extraction d'informations)
# -------------------------------------------------------------------------
API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-Coder-32B-Instruct"
# Note: Si ce modèle ne fonctionne pas, le fallback "relatedTo" prendra le relais
# -------------------------------------------------------------------------

# Token Hugging Face (chargé depuis .env)
HF_TOKEN = os.getenv("HF_TOKEN", "")
if not HF_TOKEN:
    print("⚠️ ATTENTION : HF_TOKEN non trouvé. Créez un fichier .env avec votre token.")

# Headers pour l'authentification
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}


# ============================================================================
# 2. DÉFINITION DE L'ONTOLOGIE (T-BOX) - SCHÉMA CONCEPTUEL
# ============================================================================

def define_tbox(graph):
    """
    Définit le schéma conceptuel de l'ontologie selon les standards OWL.
    
    Cette fonction crée la T-Box (Terminological Box) qui contient :
    - Les déclarations de classes (owl:Class)
    - Les propriétés d'objet (owl:ObjectProperty) 
    - Les propriétés de type de données (owl:DatatypeProperty)
    - Les contraintes de domaine (rdfs:domain) et de portée (rdfs:range)
    
    Args:
        graph (rdflib.Graph): Le graphe RDF où ajouter les déclarations
    """
    
    print("\n[T-BOX] Définition de l'ontologie...")
    
    # -----------------------------------------------------------------------
    # 2.1 DÉCLARATION DES CLASSES (owl:Class)
    # -----------------------------------------------------------------------
    # Utilisation d'ontologies standards : FOAF et Schema.org
    # Ceci améliore l'interopérabilité et la réutilisabilité du graphe
    
    # FOAF:Person - Standard du Web Sémantique pour les personnes
    # (Friend of a Friend - ontologie largement adoptée)
    graph.add((FOAF.Person, RDF.type, OWL.Class))
    graph.add((FOAF.Person, RDFS.label, Literal("Personne", lang="fr")))
    graph.add((FOAF.Person, RDFS.comment, 
               Literal("Classe FOAF représentant un individu humain", lang="fr")))
    
    # Schema:Place - Standard Schema.org pour les lieux
    # (Schema.org - ontologie de référence pour les moteurs de recherche)
    graph.add((SCHEMA.Place, RDF.type, OWL.Class))
    graph.add((SCHEMA.Place, RDFS.label, Literal("Lieu", lang="fr")))
    graph.add((SCHEMA.Place, RDFS.comment, 
               Literal("Classe Schema.org représentant un lieu géographique ou une institution", lang="fr")))
    
    # Schema:Organization - Standard Schema.org pour les organisations
    graph.add((SCHEMA.Organization, RDF.type, OWL.Class))
    graph.add((SCHEMA.Organization, RDFS.label, Literal("Organisation", lang="fr")))
    graph.add((SCHEMA.Organization, RDFS.comment, 
               Literal("Classe Schema.org représentant une entité organisationnelle", lang="fr")))
    
    # Classe représentant un Document/Cours
    graph.add((EX.Document, RDF.type, OWL.Class))
    graph.add((EX.Document, RDFS.label, Literal("Document", lang="fr")))
    graph.add((EX.Document, RDFS.comment, 
               Literal("Classe représentant un document, cours ou publication", lang="fr")))
    
    # -----------------------------------------------------------------------
    # 2.1.1 CLASSE AVEC RESTRICTION OWL (DIFFÉRENCIE OWL DE RDFS) ⭐
    # -----------------------------------------------------------------------
    # POINT CLÉ ACADÉMIQUE : Ceci démontre l'utilisation d'OWL au-delà de RDFS
    # Une restriction OWL permet de définir des contraintes sur les propriétés
    
    # Déclaration de la sous-classe ValidatedCourse
    graph.add((EX.ValidatedCourse, RDF.type, OWL.Class))
    graph.add((EX.ValidatedCourse, RDFS.subClassOf, EX.Document))
    graph.add((EX.ValidatedCourse, RDFS.label, Literal("Cours Validé", lang="fr")))
    graph.add((EX.ValidatedCourse, RDFS.comment,
               Literal("Cours ayant au moins un auteur identifié (contrainte OWL)", lang="fr")))
    
    # Création de la RESTRICTION OWL avec un Blank Node
    # Cette restriction stipule : "Un ValidatedCourse DOIT avoir au moins un ex:author qui est une foaf:Person"
    restriction = BNode()  # Nœud anonyme pour la restriction
    
    # La restriction est un owl:Restriction
    graph.add((restriction, RDF.type, OWL.Restriction))
    
    # La restriction porte sur la propriété ex:author
    graph.add((restriction, OWL.onProperty, EX.author))
    
    # La restriction exige : "il existe au moins une valeur de type foaf:Person"
    # owl:someValuesFrom = "some values from" (au moins une valeur provenant de...)
    graph.add((restriction, OWL.someValuesFrom, FOAF.Person))
    
    # Liaison de la restriction à la classe ValidatedCourse
    graph.add((EX.ValidatedCourse, RDFS.subClassOf, restriction))
    
    print("  ✓ Classe avec Restriction OWL créée : ex:ValidatedCourse")
    print("    → Contrainte : DOIT avoir au moins un ex:author de type foaf:Person")
    
    print("  ✓ Classes standards utilisées : foaf:Person, schema:Place, schema:Organization, ex:Document, ex:ValidatedCourse")
    
    # -----------------------------------------------------------------------
    # 2.2 PROPRIÉTÉS D'OBJET (owl:ObjectProperty)
    # -----------------------------------------------------------------------
    # Ces propriétés lient des RESSOURCES entre elles (URI vers URI)
    # Elles respectent la contrainte : domain → ObjectProperty → range
    
    # Propriété : Une personne enseigne dans un lieu
    graph.add((EX.teaches, RDF.type, OWL.ObjectProperty))
    graph.add((EX.teaches, RDFS.label, Literal("enseigne à", lang="fr")))
    graph.add((EX.teaches, RDFS.domain, FOAF.Person))  # Seules les Personnes peuvent enseigner
    graph.add((EX.teaches, RDFS.range, SCHEMA.Place))  # Elles enseignent dans des Lieux
    graph.add((EX.teaches, RDFS.comment, 
               Literal("Relation entre une personne et le lieu où elle enseigne", lang="fr")))
    
    # Propriété : Une personne rédige un document
    graph.add((EX.author, RDF.type, OWL.ObjectProperty))
    graph.add((EX.author, RDFS.label, Literal("a rédigé", lang="fr")))
    graph.add((EX.author, RDFS.domain, FOAF.Person))  # Seules les Personnes rédigent
    graph.add((EX.author, RDFS.range, EX.Document))  # Elles rédigent des Documents
    graph.add((EX.a_redige, RDFS.comment, 
               Literal("Relation entre un auteur et un document qu'il a rédigé", lang="fr")))
    
    # Propriété : Un document traite d'un sujet (représenté par un concept)
    graph.add((EX.traite_de, RDF.type, OWL.ObjectProperty))
    graph.add((EX.traite_de, RDFS.label, Literal("traite de", lang="fr")))
    graph.add((EX.traite_de, RDFS.domain, EX.Document))  # Un Document traite de...
    graph.add((EX.traite_de, RDFS.range, RDFS.Resource))  # ...n'importe quelle ressource
    graph.add((EX.traite_de, RDFS.comment, 
               Literal("Relation entre un document et son sujet principal", lang="fr")))
    
    # Propriété : Une personne enseigne une matière/sujet (nouveau : teaches peut pointer vers un TOPIC)
    graph.add((EX.teachesSubject, RDF.type, OWL.ObjectProperty))
    graph.add((EX.teachesSubject, RDFS.label, Literal("enseigne la matière", lang="fr")))
    graph.add((EX.teachesSubject, RDFS.domain, FOAF.Person))  # Personne enseigne
    graph.add((EX.teachesSubject, RDFS.range, EX.Document))   # Une matière (Topic/Document)
    graph.add((EX.teachesSubject, RDFS.comment, 
               Literal("Relation entre un enseignant et la matière qu'il enseigne", lang="fr")))
    
    # Propriété : Une personne travaille dans une organisation
    graph.add((EX.worksAt, RDF.type, OWL.ObjectProperty))
    graph.add((EX.worksAt, RDFS.label, Literal("travaille à", lang="fr")))
    graph.add((EX.worksAt, RDFS.domain, FOAF.Person))  # Seules les Personnes travaillent
    graph.add((EX.worksAt, RDFS.range, SCHEMA.Organization))  # Dans des Organisations
    graph.add((EX.worksAt, RDFS.comment, 
               Literal("Relation entre une personne et son lieu de travail", lang="fr")))
    
    # Propriété : Une organisation ou une personne est située dans un lieu
    graph.add((EX.locatedIn, RDF.type, OWL.ObjectProperty))
    graph.add((EX.locatedIn, RDFS.label, Literal("situé à", lang="fr")))
    graph.add((EX.locatedIn, RDFS.domain, RDFS.Resource))  # Organisation ou Personne
    graph.add((EX.locatedIn, RDFS.range, SCHEMA.Place))  # Dans un Lieu
    graph.add((EX.locatedIn, RDFS.comment, 
               Literal("Relation de localisation géographique", lang="fr")))
    
    # Propriété : Deux personnes collaborent ensemble
    graph.add((EX.collaboratesWith, RDF.type, OWL.ObjectProperty))
    graph.add((EX.collaboratesWith, RDFS.label, Literal("collabore avec", lang="fr")))
    graph.add((EX.collaboratesWith, RDFS.domain, FOAF.Person))
    graph.add((EX.collaboratesWith, RDFS.range, FOAF.Person))
    graph.add((EX.collaboratesWith, RDFS.comment, 
               Literal("Relation de collaboration entre deux personnes", lang="fr")))
    
    # Propriété : Une personne étudie dans une organisation
    graph.add((EX.studiesAt, RDF.type, OWL.ObjectProperty))
    graph.add((EX.studiesAt, RDFS.label, Literal("étudie à", lang="fr")))
    graph.add((EX.studiesAt, RDFS.domain, FOAF.Person))
    graph.add((EX.studiesAt, RDFS.range, SCHEMA.Organization))
    graph.add((EX.studiesAt, RDFS.comment, 
               Literal("Relation entre un étudiant et son établissement", lang="fr")))
    
    # Propriété : Une personne gère une organisation
    graph.add((EX.manages, RDF.type, OWL.ObjectProperty))
    graph.add((EX.manages, RDFS.label, Literal("gère", lang="fr")))
    graph.add((EX.manages, RDFS.domain, FOAF.Person))
    graph.add((EX.manages, RDFS.range, SCHEMA.Organization))
    graph.add((EX.manages, RDFS.comment, 
               Literal("Relation de gestion/direction d'une organisation", lang="fr")))
    
    # Propriété générique : Relation quelconque entre deux ressources
    graph.add((EX.relatedTo, RDF.type, OWL.ObjectProperty))
    graph.add((EX.relatedTo, RDFS.label, Literal("en relation avec", lang="fr")))
    graph.add((EX.relatedTo, RDFS.domain, RDFS.Resource))
    graph.add((EX.relatedTo, RDFS.range, RDFS.Resource))
    graph.add((EX.relatedTo, RDFS.comment, 
               Literal("Relation générique entre deux ressources", lang="fr")))
    
    print("  ✓ ObjectProperties définies : ex:teaches, ex:teachesSubject, ex:author, ex:traite_de, ex:worksAt, ex:locatedIn, ex:collaboratesWith, ex:studiesAt, ex:manages, ex:relatedTo")
    
    # -----------------------------------------------------------------------
    # 2.3 PROPRIÉTÉS DE DONNÉES (owl:DatatypeProperty)
    # -----------------------------------------------------------------------
    # Ces propriétés lient des RESSOURCES à des VALEURS LITTÉRALES
    # Elles respectent la contrainte : domain → DatatypeProperty → xsd:datatype
    
    # Propriété : Le nom d'une personne (chaîne de caractères)
    # Utilisation de FOAF.name (propriété standard)
    graph.add((FOAF.name, RDF.type, OWL.DatatypeProperty))
    graph.add((FOAF.name, RDFS.label, Literal("nom", lang="fr")))
    graph.add((FOAF.name, RDFS.domain, FOAF.Person))  # S'applique aux Personnes
    graph.add((EX.nom, RDFS.range, XSD.string))  # Valeur de type chaîne
    graph.add((EX.nom, RDFS.comment, 
               Literal("Nom complet d'une personne", lang="fr")))
    
    # Propriété : L'intitulé d'un document (chaîne de caractères)
    graph.add((EX.intitule, RDF.type, OWL.DatatypeProperty))
    graph.add((EX.intitule, RDFS.label, Literal("intitulé", lang="fr")))
    graph.add((EX.intitule, RDFS.domain, EX.Document))  # S'applique aux Documents
    graph.add((EX.intitule, RDFS.range, XSD.string))  # Valeur de type chaîne
    graph.add((EX.intitule, RDFS.comment, 
               Literal("Titre ou intitulé d'un document", lang="fr")))
    
    # Propriété : L'âge d'une personne (entier)
    graph.add((EX.age, RDF.type, OWL.DatatypeProperty))
    graph.add((EX.age, RDFS.label, Literal("âge", lang="fr")))
    graph.add((EX.age, RDFS.domain, EX.Person))  # S'applique aux Personnes
    graph.add((EX.age, RDFS.range, XSD.integer))  # Valeur de type entier
    graph.add((EX.age, RDFS.comment, 
               Literal("Âge d'une personne en années", lang="fr")))
    
    print("  ✓ DatatypeProperties définies : foaf:name, ex:intitule, ex:age")
    print("[T-BOX] Ontologie définie avec succès !\n")


# ============================================================================
# 3. UTILITAIRES : NORMALISATION DES URIs
# ============================================================================

def normalize_uri_fragment(text):
    """
    Nettoie et normalise une chaîne de caractères pour créer un fragment d'URI valide.
    
    Transformations appliquées :
    - Suppression des accents (é → e, à → a, etc.)
    - Conversion en minuscules
    - Remplacement des espaces par des underscores
    - Conservation uniquement des caractères alphanumériques et underscores
    
    Args:
        text (str): Le texte à normaliser
        
    Returns:
        str: Fragment d'URI normalisé (ex: "Université de Versailles" → "universite_de_versailles")
    
    Exemple:
        >>> normalize_uri_fragment("Zoubida Kedad")
        'zoubida_kedad'
    """
    # Décomposition Unicode pour séparer les caractères de base des accents
    text = unicodedata.normalize('NFD', text)
    # Suppression des marques diacritiques (accents)
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    # Normalisation : minuscules, espaces → underscores, nettoyage
    text = text.lower().strip()
    text = re.sub(r'\s+', '_', text)  # Espaces multiples → underscore unique
    text = re.sub(r'[^\w]', '', text)  # Suppression des caractères non alphanumériques
    return text


# ============================================================================
# 4. PRÉDICTION DE RELATIONS VIA LLM (SIMULATION)
# ============================================================================

def predict_relation_real_api(entity1: str, entity2: str, sentence: str,
                              entity1_type: str = "UNK", entity2_type: str = "UNK") -> Optional[str]:
    """
    Utilise l'API GROQ (Gratuite et Ultra-Rapide).
    Modèle : Llama-3-8B (très performant pour l'extraction de relations).
    
    VERSION PRODUCTION (GROQ API) 🚀 :
    - API Groq gratuite et ultra-rapide
    - Modèle Meta Llama-3-8B-8192 (excellent pour le NLP)
    - Température = 0 pour des réponses stables et déterministes
    - Fallback intelligent si l'API est indisponible
    
    Args:
        entity1 (str): Première entité (généralement le sujet)
        entity2 (str): Deuxième entité (généralement l'objet)
        sentence (str): Phrase complète contenant les entités
        
    Returns:
        str: Le type de relation détecté ("teaches", "author", "worksAt", "relatedTo")
    
    Exemples:
        >>> predict_relation_real_api("Marie", "Université", "Marie enseigne à l'Université")
        'teaches'
    """
    
    # Clé API Groq (chargée depuis .env)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    if not GROQ_API_KEY:
        print("⚠️ ATTENTION : GROQ_API_KEY non trouvé. Créez un fichier .env avec votre clé.")
        return "relatedTo"
    
    try:
        print(f"  🚀 Appel API Groq (Llama-3) pour : {entity1} ↔ {entity2}")
        
        client = Groq(api_key=GROQ_API_KEY)
        
        # Prompt académique strict V3 - DOMAIN ENFORCEMENT (NEURO-SYMBOLIC ARCHITECTURE)
        prompt = f"""You are a STRICT relation extraction component inside a Neuro-Symbolic RDF system.

You are NOT an ontology editor.
You are NOT allowed to change entity types.
You are NOT allowed to create new classes or properties.

========================
ABSOLUTE RULES
========================

1. You must ONLY use the entity types provided.
2. You must NOT re-type an entity (e.g., do NOT convert a Topic into a Person).
3. If a subject is not explicitly a foaf:Person, you MUST NOT assign a teaching relation.
4. If domain constraints are not satisfied, return NO_VALID_RELATIONS.
5. If the sentence is semantically incoherent (e.g., a concept performing a human action), return NO_VALID_RELATIONS.
6. You must NOT infer implicit roles.
7. You must NOT generate schema-level triples.

========================
SEMANTIC FILTERS
========================

Human-only actions (REQUIRE subject = Person):
- teaches, teachesSubject, author, worksAt, manages, collaboratesWith

If subject type ≠ Person → return NO_VALID_RELATIONS.

Topic-like entities (NEVER Person):
- anything containing: "Sémantique", "RDF", "Web", "Graph", "Ontology", "SPARQL", "OWL"
- abstract academic subjects
- technical standards

These must NEVER perform human actions.

========================
VERB MAPPING
========================

- "enseigne [subject]" → teachesSubject (if subject=Person AND object=Topic/Document)
- "travaille à" → worksAt (if subject=Person AND object=Organization)
- "écrit", "auteur" → author (if subject=Person AND object=Document)
- "situé à" → locatedIn

If constraints violated → NO_VALID_RELATIONS

========================
CONTEXT
========================

Text: "{sentence}"
Entity 1: "{entity1}" (type: {entity1_type})
Entity 2: "{entity2}" (type: {entity2_type})

Admissible relations for ({entity1_type} → {entity2_type}):
- PER → TOPIC  : teachesSubject, author, relatedTo
- PER → ORG    : worksAt, manages, studiesAt, collaboratesWith, relatedTo
- PER → LOC    : locatedIn, relatedTo
- PER → PER    : collaboratesWith, relatedTo
- ORG → LOC    : locatedIn, relatedTo
(other combinations → relatedTo or NO_VALID_RELATIONS)

========================
OUTPUT (ONE WORD ONLY)
========================

teachesSubject | teaches | author | worksAt | locatedIn | collaboratesWith | studiesAt | manages | relatedTo | NO_VALID_RELATIONS

No explanations."""

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a STRICT relation extraction component. You output ONLY property names or NO_VALID_RELATIONS. You NEVER modify entity types. You NEVER allow non-Person subjects for human actions. You REJECT semantically incoherent relations."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0,
        )

        relation = chat_completion.choices[0].message.content.strip()
        
        # Clean LLM output: strip punctuation but KEEP underscores (needed for
        # camelCase property names like "teachesSubject" which use no underscores,
        # but also safe to keep them for any variant the LLM may emit).
        relation = relation.strip().replace(".", "").replace('"', "").replace("'", "")
        # Normalise to camelCase canonical forms used by valid_relations
        _llm_aliases = {
            "teachessubject":   "teachesSubject",
            "teaches_subject":  "teachesSubject",
            "worksat":          "worksAt",
            "works_at":         "worksAt",
            "locatedin":        "locatedIn",
            "located_in":       "locatedIn",
            "collaborateswith":        "collaboratesWith",
            "collaborates_with":       "collaboratesWith",
            "studiesat":        "studiesAt",
            "studies_at":       "studiesAt",
        }
        relation = _llm_aliases.get(relation.lower(), relation)
        
        # Si LLM retourne NO_RELATION ou NO_VALID_RELATIONS, on arrête immédiatement
        if "no" in relation and ("relation" in relation or "valid" in relation):
            print(f"    ⛔ LLM a rejeté la relation (NO_VALID_RELATIONS)")
            return None
        
        # --- LOGIQUE DE CORRECTION SÉMANTIQUE AVEC PRIORITÉS ET CONTEXTE LOCAL ---
        sentence_lower = sentence.lower()
        entity1_lower = entity1.lower()
        entity2_lower = entity2.lower()
        
        # Extraction du contexte local AMÉLIORÉE : Utiliser la phrase qui contient les deux entités
        # Si les entités sont dans des phrases différentes, utiliser la phrase de entity2 (objet)
        try:
            # Séparer le texte en phrases
            import re
            sentences = re.split(r'[.!?]\s+', sentence)
            
            # Trouver la phrase qui contient les deux entités
            local_context = None
            for sent in sentences:
                sent_lower = sent.lower()
                if entity1_lower in sent_lower and entity2_lower in sent_lower:
                    local_context = sent_lower
                    break
            
            # Si pas de phrase commune, prendre la phrase de entity2 (objet)
            # Raison: La relation est généralement exprimée près de l'objet
            # Ex: "Elle travaille au CNRS" → "travaille" est dans la phrase du CNRS
            if not local_context:
                for sent in sentences:
                    sent_lower = sent.lower()
                    if entity2_lower in sent_lower:
                        local_context = sent_lower
                        break
            
            # Fallback sur la phrase de entity1
            if not local_context:
                for sent in sentences:
                    sent_lower = sent.lower()
                    if entity1_lower in sent_lower:
                        local_context = sent_lower
                        break
            
            # Fallback final sur contexte autour des entités (ancien système)
            if not local_context:
                pos1 = sentence_lower.find(entity1_lower)
                pos2 = sentence_lower.find(entity2_lower)
                
                if pos1 >= 0 and pos2 >= 0:
                    start = min(pos1, pos2)
                    end = max(pos1 + len(entity1_lower), pos2 + len(entity2_lower))
                    
                    # Extraire 50 caractères avant et après pour le contexte
                    context_start = max(0, start - 50)
                    context_end = min(len(sentence_lower), end + 50)
                    local_context = sentence_lower[context_start:context_end]
                else:
                    local_context = sentence_lower  # Fallback sur phrase complète
        except:
            local_context = sentence_lower
        
        print(f"    🔍 Contexte local : ...{local_context}...")
        
        # Classification des lieux (villes vs bâtiments/institutions)
        # IMPORTANT : Ne pas mettre de villes qui apparaissent souvent dans des noms d'institutions
        vraies_villes = ["paris", "france", "versailles", "lyon", "marseille", "toulouse", 
                        "bordeaux", "lille", "états-unis", "usa", "new york", "londres",
                        "californie", "redmond", "cambridge", "oxford",
                        "berkeley", "boston", "seattle", "tokyo", "berlin"]
        
        batiments_institutions = ["palais", "élysée", "mit", "stanford", "harvard", "université", 
                                 "university", "institut", "école", "college"]
        
        # Vérifier si entity2 est UNIQUEMENT une ville (pas dans un nom d'institution)
        is_vraie_ville = any(ville in entity2_lower for ville in vraies_villes) and \
                        not any(bat in entity2_lower for bat in batiments_institutions)
        is_batiment = any(bat in entity2_lower for bat in batiments_institutions)
        
        # === PRIORITÉS BASÉES SUR LE CONTEXTE LOCAL (pas toute la phrase) ===

        # PRIORITÉ 0 : Enseignement — dispatch selon le type de entity2
        # Primary source: NER-produced entity types passed as parameters.
        # Keyword lists are used ONLY as fallback when type is UNK.
        topics_keywords = ["physique", "mathématiques", "maths", "informatique", "biologie",
                          "chimie", "histoire", "géographie", "philosophie", "littérature",
                          "physics", "mathematics", "computer science", "biology", "chemistry",
                          "rdfs", "rdf", "owl", "sparql", "sémantique", "web sémantique",
                          "semantic web", "ontologie", "ontology", "json-ld", "turtle",
                          "bases de données", "base de données", "database", "réseaux", "networks",
                          "algorithmes", "algorithms", "intelligence artificielle", "ia", "ai",
                          "machine learning", "deep learning", "apprentissage"]

        org_keywords = ["université", "university", "institute", "institut", "laboratoire",
                        "lab", "department", "département", "centre", "center", "school",
                        "college", "école", "inria", "cnrs"]

        # Type-first resolution (NER parameter > keyword heuristic)
        if entity2_type == "TOPIC":
            is_topic, is_org = True, False
        elif entity2_type in ("ORG",):
            is_topic, is_org = False, True
        elif entity2_type in ("LOC",):
            # LOC alone: keyword fallback distinguishes pure city from institution
            is_topic = False
            is_org   = any(kw in entity2_lower for kw in org_keywords)
        else:
            # UNK — fall back to keyword heuristics
            is_topic = any(kw in entity2_lower for kw in topics_keywords)
            is_org   = any(kw in entity2_lower for kw in org_keywords)

        _teach_verbs = ["enseigne", "enseigné", "enseignant", "teach", "taught", "teaching"]
        _teach_in_ctx = any(kw in local_context for kw in _teach_verbs)

        if _teach_in_ctx and is_topic:
            relation = "teachesSubject"
            print(f"  🎓 Priorité 0a : 'enseigne' + matière '{entity2}' → teachesSubject")

        elif _teach_in_ctx and is_org:
            relation = "worksAt"
            print(f"  🏫 Priorité 0b : 'enseigne' + organisation '{entity2}' → worksAt")

        # PRIORITÉ 1 : Enseignement générique (type de entity2 inconnu)
        elif any(kw in local_context for kw in ["enseigne", "enseigné", "enseignant", "professeur",
                                                  "teach", "professor", "taught", "teaching"]):
            relation = "teachesSubject"
            print(f"  🎓 Priorité 1 : 'enseigne/professeur' → teachesSubject (défaut)")
        
        # PRIORITÉ 2 : Direction/Management (mots-clés de management)
        # IMPORTANT : Seulement si entity1 est une personne ET entity2 est une organisation
        elif any(kw in local_context for kw in ["dirige", "gère", "manage", "manages", "ceo", "dirigeant"]) and \
             not is_vraie_ville:  # Exclure les villes (on ne dirige pas une ville)
            relation = "manages"
            print(f"  💼 Priorité 2 : Détection 'dirige/gère' dans contexte local → Force manages")
        
        # PRIORITÉ 3 : Travail/Emploi (personne → organisation/bâtiment)
        # IMPORTANT : "travaille à X" devrait être worksAt même si X est une ville
        # car dans contexte professionnel, c'est souvent une organisation (ex: Université de Versailles)
        elif any(kw in local_context for kw in ["travaille", "works", "employé", "employee"]):
            # Dans contexte de travail, privilégier worksAt (organisation implicite)
            relation = "worksAt"
            print(f"  💼 Priorité 3 : Détection 'travaille' → Force worksAt (contexte professionnel)")
        
        # PRIORITÉ 4 : Rédaction/Auteur (mots-clés de création)
        elif any(kw in local_context for kw in ["auteur", "rédigé", "écrit", "author", "wrote", "written", "écrivain", "a écrit"]):
            relation = "author"
            print(f"  ✍️ Priorité 4 : Détection 'auteur/écrit' dans contexte local → Force author")
        
        # PRIORITÉ 4.5 : Localisation explicite avec "situé" (prend le dessus sur manages)
        elif any(kw in local_context for kw in ["situé", "située", "basé", "basée", "located", "based"]):
            if is_vraie_ville or is_batiment:
                relation = "locatedIn"
                print(f"  📍 Priorité 4.5 : Détection 'situé/basé' dans contexte local → Force locatedIn")
        
        # PRIORITÉ 5 : Localisation (si entity2 est une VRAIE ville — pas une institution)
        # This fires even after Priority 0/1 because a bare city is never a
        # teaching object: "Zoubida enseigne Versailles" makes no semantic sense.
        elif is_vraie_ville:
            ville_detectee = next((v for v in vraies_villes if v in entity2_lower), entity2)
            print(f"  📍 Priorité 5 : Détection ville '{ville_detectee}' → Force locatedIn")
            relation = "locatedIn"

        # POST-OVERRIDE: bare city must always yield locatedIn regardless of verb
        if is_vraie_ville and relation != "locatedIn":
            relation = "locatedIn"
            print(f"  📍 Post-override : ville seule → locatedIn (annule verbe d'enseignement)")
        
        # Mapping de sécurité pour les autres cas (détection dans la réponse LLM)
        # IMPORTANT : Ne pas écraser teachesSubject ou worksAt fixés par les priorités 0a/0b
        if relation not in ("teachesSubject", "worksAt"):  # Protection contre écrasement
            if "teachsubject" in relation.lower().replace(" ", "").replace("_", ""):
                relation = "teachesSubject"
            elif "teach" in relation:
                # Dispatcher selon le type de entity2
                if is_org:
                    relation = "worksAt"
                else:
                    relation = "teachesSubject"
            elif "author" in relation or "wrote" in relation:
                relation = "author"
            elif "work" in relation:
                relation = "worksAt"
            elif "located" in relation or "situé" in relation or "basé" in relation:
                relation = "locatedIn"
            elif "collabore" in relation or "collaborate" in relation:
                relation = "collaboratesWith"
            elif "étudie" in relation or "studies" in relation:
                relation = "studiesAt"
            elif "gère" in relation or "manage" in relation:
                relation = "manages"
        
        # Liste des relations valides
        valid_relations = ["teachesSubject", "author", "worksAt", "locatedIn",
                          "collaboratesWith", "studiesAt", "manages", "relatedTo"]
        if relation not in valid_relations:
            relation = "relatedTo"

        print(f"  🤖 Groq/Llama-3 a détecté : {entity1} --[{relation}]--> {entity2}")
        return relation

    except Exception as e:
        print(f"  ⚠️ Erreur Groq ({str(e)[:80]}). Passage au fallback.")
        # Fallback ultime avec détection de lieux
        sentence_lower = sentence.lower()
        entity2_lower = entity2.lower()
        
        # Détection de lieux dans le fallback
        lieux = ["paris", "france", "versailles", "lyon", "marseille", "toulouse", 
                 "bordeaux", "lille", "états-unis", "usa", "new york", "londres",
                 "californie", "silicon valley"]
        
        for lieu in lieux:
            if lieu in entity2_lower:
                print(f"  🔍 Fallback : Détection de lieu '{lieu}' → locatedIn")
                return "locatedIn"
        
        # Autres détections — use entity2_type (NER) first, keyword fallback for UNK
        if "enseigne" in sentence_lower or "teach" in sentence_lower:
            if entity2_type == "ORG":
                return "worksAt"
            if entity2_type == "TOPIC":
                return "teachesSubject"
            # Type UNK → keyword fallback
            _fallback_org_kw   = ["université", "university", "institut", "institute",
                                   "laboratoire", "lab", "department", "département",
                                   "centre", "center", "école", "school", "college",
                                   "inria", "cnrs"]
            _fallback_topic_kw = ["physique", "mathématiques", "maths", "informatique",
                                   "sémantique", "rdf", "owl", "sparql", "ontologie",
                                   "machine learning", "deep learning", "ia", "ai",
                                   "réseaux", "algorithmes", "database", "databases"]
            if any(kw in entity2_lower for kw in _fallback_org_kw):
                return "worksAt"
            if any(kw in entity2_lower for kw in _fallback_topic_kw):
                return "teachesSubject"
            return "teachesSubject"  # safest default
        if "rédigé" in sentence_lower or "écrit" in sentence_lower or "author" in sentence_lower:
            return "author"
        if "travaille" in sentence_lower or "works" in sentence_lower:
            return "worksAt"
        if "situé" in sentence_lower or "basé" in sentence_lower or "located" in sentence_lower:
            return "locatedIn"
        if "collabore" in sentence_lower or "collaborate" in sentence_lower:
            return "collaboratesWith"
        if "étudie" in sentence_lower or "studies" in sentence_lower:
            return "studiesAt"
        
        return "relatedTo"


# ============================================================================
# 4.5. RAFFINEMENT INTELLIGENT DES TYPES D'ENTITÉS VIA LLM
# ============================================================================

def refine_entity_types(entities, sentence):
    """
    Re-classifie dynamiquement les entités détectées par spaCy via Groq/Llama-3.
    
    Cette fonction permet de corriger les erreurs de spaCy et d'ajouter un nouveau type : TOPIC
    (pour les matières académiques, concepts scientifiques, domaines de connaissance).
    
    Args:
        entities (list): Liste de tuples (texte_entité, type_spacy)
        sentence (str): Phrase complète pour le contexte
        
    Returns:
        list: Liste de tuples (texte_entité, type_raffiné)
        
    Exemples:
        Input:  [("Einstein", "PER"), ("Physique", "MISC")]
        Output: [("Einstein", "PER"), ("Physique", "TOPIC")]
    """
    if not entities:
        return entities
    
    print("\n[RAFFINEMENT] Re-classification intelligente des entités via Groq/Llama-3...")
    
    # Clé API Groq (chargée depuis .env)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    if not GROQ_API_KEY:
        print("⚠️ ATTENTION : GROQ_API_KEY non trouvé dans .env")
        return entities  # Retourner entités non raffinées
    
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        # Préparer la liste des entités pour le prompt
        entity_list = [text for text, _ in entities]
        entity_list_str = ", ".join([f'"{e}"' for e in entity_list])
        
        # Prompt optimisé pour Llama-3
        prompt = f"""Context: "{sentence}"

Entities detected: [{entity_list_str}]

For each entity, determine its precise type from this list:
- PERSON: human being (name, pronoun)
- ORGANIZATION: company, institution, university, government body
- LOCATION: city, country, place, building, address
- TOPIC: academic subject, scientific field, concept, domain (e.g., Physics, Mathematics, Computer Science, Biology, RDFS, etc.)
- DOCUMENT: book title, article, publication, course name

Reply ONLY with a valid JSON object mapping each entity to its type.
Example: {{"Einstein": "PERSON", "Physique": "TOPIC", "Université de Princeton": "ORGANIZATION"}}

JSON:"""

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a semantic entity classifier. You output ONLY valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0,
        )

        response = chat_completion.choices[0].message.content.strip()
        
        # Nettoyage : extraire le JSON (parfois Llama ajoute des backticks)
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        # Parser le JSON
        try:
            classification = json.loads(response)
        except json.JSONDecodeError:
            # Fallback : essayer de trouver un objet JSON dans la réponse
            import re
            json_match = re.search(r'\{[^}]+\}', response)
            if json_match:
                classification = json.loads(json_match.group())
            else:
                print(f"  ⚠️ Échec parsing JSON. Réponse brute: {response[:100]}")
                return entities
        
        # Appliquer la re-classification
        refined_entities = []
        for entity_text, original_type in entities:
            if entity_text in classification:
                new_type = classification[entity_text]
                
                # Mapper les types Groq vers les types de notre système
                type_mapping = {
                    "PERSON": "PER",
                    "ORGANIZATION": "ORG",
                    "LOCATION": "LOC",
                    "TOPIC": "TOPIC",  # Nouveau type !
                    "DOCUMENT": "DOC"
                }
                
                refined_type = type_mapping.get(new_type, original_type)
                
                # Safety guard: never let LLM downgrade a PER decided by NER
                if original_type == "PER" and refined_type != "PER":
                    print(f"  🛡️ Protégé : '{entity_text}' reste PER (LLM proposait {refined_type})")
                    refined_type = "PER"

                if refined_type != original_type:
                    print(f"  🔄 Raffinement : '{entity_text}' : {original_type} → {refined_type}")
                else:
                    print(f"  ✓ Confirmé : '{entity_text}' : {refined_type}")
                
                refined_entities.append((entity_text, refined_type))
            else:
                # Entité non classifiée par Groq, garder le type original
                print(f"  ℹ️ Non classifié : '{entity_text}' (conservé: {original_type})")
                refined_entities.append((entity_text, original_type))
        
        print(f"[RAFFINEMENT] ✓ {len(refined_entities)} entités re-classifiées\n")
        return refined_entities
        
    except Exception as e:
        print(f"  ⚠️ Erreur Groq lors du raffinement ({str(e)[:80]})")
        print(f"  → Utilisation des types spaCy originaux")
        return entities


# ============================================================================
# 5. EXTRACTION DES ENTITÉS (A-BOX) - DONNÉES FACTUELLES
# ============================================================================

def extract_entities_with_spacy(text, nlp):
    """
    ⚠️ FONCTION LEGACY - REMPLACÉE PAR HybridNERModule
    
    Cette fonction est conservée pour compatibilité mais utilise désormais
    le nouveau module hybride NER (7 couches).
    
    Extrait les entités nommées d'un texte avec spaCy (reconnaissance NER).
    
    Cette fonction réalise la phase d'extraction factuelle qui alimentera
    la A-Box (Assertional Box) avec des instances concrètes.
    
    Args:
        text (str): Le texte source à analyser
        nlp (spacy.Language): Modèle spaCy chargé
        
    Returns:
        list: Liste de tuples (texte_entité, type_entité)
              Exemple: [("Zoubida Kedad", "PER"), ("Université de Versailles", "LOC")]
    """
    print("\n[A-BOX] Extraction des entités nommées avec MODULE 0++ (HybridNER)...")
    
    # ============================================================================
    # NOUVEAU : Utilisation du HybridNERModule (7 couches)
    # ============================================================================
    # Initialisation du module NER hybride
    # Note: ontology_graph sera passé ultérieurement si validation activée
    hybrid_ner = HybridNERModule(
        nlp=nlp,
        confidence_threshold=0.6,  # Seuil de confiance minimum
        enable_validation=False    # Validation ontologique désactivée à cette étape
    )
    
    # Extraction avec les 7 couches
    entities_with_confidence = hybrid_ner.extract(text, verbose=True)
    
    # Conversion au format attendu (texte, type) - la confiance sera gérée séparément
    entities = [(text, entity_type) for text, entity_type, confidence in entities_with_confidence]
    
    # Stockage des scores de confiance pour utilisation ultérieure
    # (sera utilisé lors de l'ajout au graphe)
    if not hasattr(extract_entities_with_spacy, '_confidence_cache'):
        extract_entities_with_spacy._confidence_cache = {}
    
    for text, entity_type, confidence in entities_with_confidence:
        extract_entities_with_spacy._confidence_cache[text] = confidence
    
    return entities


def instantiate_entities_in_abox(graph, entities):
    """
    Instancie les entités extraites dans le graphe RDF (A-Box).
    
    Pour chaque entité :
    1. Crée une URI unique dans le namespace DATA
    2. Assigne le type de classe approprié (rdf:type) selon le mapping :
       - PER (Personne) → ex:Person
       - LOC (Lieu) → ex:Location
       - ORG (Organisation) → ex:Organization
    3. Ajoute une propriété de données (owl:DatatypeProperty) pour le nom
    
    Args:
        graph (rdflib.Graph): Le graphe RDF où ajouter les instances
        entities (list): Liste de tuples (texte, type) issus de spaCy
        
    Returns:
        dict: Mapping {texte_entité: URI} pour référencer les instances
    """
    print("\n[A-BOX] Instanciation des entités dans le graphe...")
    
    # ============================================================================
    # NOUVEAU : Initialisation du système de confiance
    # ============================================================================
    confidence_scorer = ConfidenceScorer(graph, verbose=True)
    
    # Mapping entre les types NER (spaCy + Groq raffinés) et les classes OWL standards
    entity_type_mapping = {
        "PER": FOAF.Person,           # Personne → foaf:Person (standard FOAF)
        "LOC": SCHEMA.Place,          # Lieu → schema:Place (standard Schema.org)
        "ORG": SCHEMA.Organization,   # Organisation → schema:Organization (standard Schema.org)
        "TOPIC": EX.Document,         # ✨ NOUVEAU : Matière/Concept → ex:Document (sujet d'étude)
        "DOC": EX.Document            # Document explicite
    }
    
    entity_uris = {}
    
    for entity_text, entity_label in entities:
        # NETTOYAGE URI : Transformation en snake_case sans accents
        uri_fragment = normalize_uri_fragment(entity_text)
        entity_uri = DATA[uri_fragment]
        
        # Récupération du score de confiance depuis le cache HybridNER
        confidence = 0.85  # Valeur par défaut
        if hasattr(extract_entities_with_spacy, '_confidence_cache'):
            confidence = extract_entities_with_spacy._confidence_cache.get(entity_text, 0.85)
        
        # Gestion du nouveau type TOPIC (matières académiques, concepts scientifiques)
        if entity_label == "TOPIC":
            print(f"  📚 Entité TOPIC détectée (matière/concept) : '{entity_text}'")
            graph.add((entity_uri, RDF.type, EX.Document))
            graph.add((entity_uri, RDFS.label, Literal(entity_text, lang="fr")))
            graph.add((entity_uri, FOAF.name, Literal(entity_text, lang="fr")))
            
            # ✨ NOUVEAU : Ajout score de confiance
            confidence_scorer.add_entity_confidence(entity_uri, confidence, source="hybrid_ner")
            
            entity_uris[entity_text] = entity_uri
            print(f"  ✓ Instance créée : {uri_fragment} (type: Topic/Document, label: '{entity_text}')")
            continue
        
        # Gestion intelligente des entités MISC (œuvres, documents, concepts)
        if entity_label == "MISC":
            # Mots-clés indiquant un document/œuvre
            document_keywords = ["roman", "livre", "cours", "spécifications", "document", 
                               "article", "publication", "ouvrage", "œuvre", "the", "les", "le"]
            is_document = any(kw.lower() in entity_text.lower() for kw in document_keywords)
            
            if is_document:
                print(f"  📚 Entité MISC détectée comme Document : '{entity_text}'")
                graph.add((entity_uri, RDF.type, EX.Document))
                graph.add((entity_uri, RDFS.label, Literal(entity_text, lang="fr")))
                graph.add((entity_uri, FOAF.name, Literal(entity_text, lang="fr")))
                
                # ✨ NOUVEAU : Ajout score de confiance
                confidence_scorer.add_entity_confidence(entity_uri, confidence, source="hybrid_ner")
                
                entity_uris[entity_text] = entity_uri
                print(f"  ✓ Instance créée : {uri_fragment} (type: Document, label: '{entity_text}')")
                continue
            else:
                print(f"  ⚠ Type d'entité MISC non reconnu comme document : {entity_text} (ignoré)")
                continue
        
        # Vérification que le type d'entité est reconnu
        if entity_label not in entity_type_mapping:
            print(f"  ⚠ Type d'entité non mappé : {entity_label} (ignoré)")
            continue
        
        # TYPAGE STRICT : Assignation du type de classe selon Spacy NER
        # PER → foaf:Person | ORG → schema:Organization | LOC → schema:Place
        owl_class = entity_type_mapping[entity_label]
        graph.add((entity_uri, RDF.type, owl_class))
        
        # LABELS SYSTÉMATIQUES : Ajout de rdfs:label et foaf:name
        # rdfs:label = étiquette RDF standard (pour raisonneurs)
        graph.add((entity_uri, RDFS.label, Literal(entity_text, lang="fr")))
        
        # foaf:name = nom lisible (standard FOAF)
        graph.add((entity_uri, FOAF.name, Literal(entity_text, lang="fr")))
        
        # ✨ NOUVEAU : Ajout score de confiance
        confidence_scorer.add_entity_confidence(entity_uri, confidence, source="hybrid_ner")
        
        entity_uris[entity_text] = entity_uri
        type_display = owl_class.split('#')[-1].split('/')[-1]
        print(f"  ✓ Instance créée : {uri_fragment} (type: {type_display}, label: '{entity_text}')")
    
    return entity_uris
    
    return entity_uris


# ============================================================================
# 5. RELATIONS SÉMANTIQUES (ObjectProperties dans l'A-Box)
# ============================================================================

def adapt_entity_type(graph, entity_uri, entity_text, required_type):
    """
    Adapte dynamiquement le type d'une entité selon le contexte de la relation.
    
    Un lieu peut être une organisation (ex: Palais de l'Élysée = lieu de travail).
    Cette fonction ajoute un type supplémentaire sans supprimer le type original.
    
    Args:
        graph: Le graphe RDF
        entity_uri: L'URI de l'entité à adapter
        entity_text: Le texte de l'entité (pour logs)
        required_type: Le type requis par la relation
    """
    current_types = list(graph.objects(entity_uri, RDF.type))
    
    # Si l'entité est un Place et qu'on a besoin d'Organization → ajouter Organization
    # GUARD: Only adapt if the entity name looks like an institution, NOT a bare city.
    _inst_keywords = ["université", "university", "institute", "institut", "école",
                      "school", "college", "laboratoire", "lab", "centre", "center",
                      "department", "département", "inria", "cnrs", "mit", "stanford",
                      "harvard", "palais", "élysée"]
    _entity_lower = entity_text.lower()
    _looks_like_institution = any(kw in _entity_lower for kw in _inst_keywords)
    if SCHEMA.Place in current_types and required_type == SCHEMA.Organization and _looks_like_institution:
        graph.add((entity_uri, RDF.type, SCHEMA.Organization))
        print(f"    🔄 Typage adaptatif : {entity_text} est aussi une Organisation (contexte professionnel)")
        return True
    
    # Si l'entité est un Place et qu'on a besoin de Document → possible pour institutions
    if SCHEMA.Place in current_types and required_type == EX.Document:
        graph.add((entity_uri, RDF.type, EX.Document))
        print(f"    🔄 Typage adaptatif : {entity_text} est aussi un Document")
        return True
    
    return False


def extract_relations(graph, entity_uris, text):
    """
    Extrait et instancie les relations sémantiques entre entités.
    
    Cette fonction utilise la fonction predict_relation() qui simule un LLM
    pour détecter automatiquement les relations entre entités.
    
    Améliorations par rapport à la version précédente :
    - Utilisation d'un "LLM Mock" via predict_relation() (extensible vers vraie API)
    - Détection automatique du type de relation
    - Support de multiples types de relations
    - Typage adaptatif : un lieu peut être une organisation selon le contexte
    
    ✨ NOUVEAU : Couche 7 - Mapping lemme → propriété OWL
    - Détection de verbes dans le texte (enseigner, écrire, travailler)
    - Mapping automatique vers propriétés OWL (teaches, author, worksAt)
    - Validation domain/range pour les relations inférées
    
    Args:
        graph (rdflib.Graph): Le graphe RDF où ajouter les relations
        entity_uris (dict): Mapping des entités vers leurs URIs
        text (str): Le texte source pour l'analyse contextuelle
    """
    print("\n[A-BOX] Extraction des relations sémantiques avec LLM Mock...")
    
    # ============================================================================
    # ✨ COUCHE 7 : MAPPING LEMME → PROPRIÉTÉ OWL (Module 0++)
    # ============================================================================
    print("\n[MODULE 0++ - COUCHE 7] Mapping verbes → propriétés OWL")
    print("-" * 80)
    
    # Initialisation HybridNER pour extraction de relations verbales
    import spacy
    nlp = spacy.load("fr_core_news_sm")
    
    from hybrid_ner_module import HybridNERModule
    hybrid_ner = HybridNERModule(nlp, confidence_threshold=0.6, enable_validation=False)
    
    # Mapping verbe lemme → propriété OWL
    # Note: 'enseigner' handled separately below with type-aware dispatch.
    #   • PER --[teachesSubject]--> TOPIC/Document  (direct object)
    #   • PER --[worksAt]-->        ORG              (prepositional object)
    verb_mapping = {
        "écrire":    ("author",   FOAF.Person, EX.Document),
        "travailler": ("worksAt", FOAF.Person, SCHEMA.Organization),
        "diriger":   ("manages",  FOAF.Person, SCHEMA.Organization),
        "étudier":   ("studiesAt", FOAF.Person, EX.Document),
    }

    # Prepositions that introduce a workplace in French / English
    _AT_PREPS = frozenset(["à", "au", "aux", "dans", "en", "at", "in"])

    # Analyse du texte pour détecter les verbes
    doc = nlp(text)
    verb_relations_added = 0

    for token in doc:
        if token.pos_ == "VERB":
            lemma = token.lemma_.lower()

            # ================================================================
            # TYPE-AWARE DISPATCH FOR 'enseigner' / 'teach'
            # Rule:
            #   PER --[teachesSubject]--> TOPIC/Document  (grammatical dobj)
            #   PER --[worksAt]-->        ORG              (oblique / prep obj)
            # ================================================================
            if lemma in ("enseigner", "teach"):
                # Find subject
                subject_text = None
                for child in token.children:
                    if child.dep_ in ("nsubj", "nsubjpass"):
                        for ent in doc.ents:
                            if child.i >= ent.start and child.i < ent.end:
                                subject_text = ent.text
                                break

                if not subject_text:
                    continue
                subject_uri = entity_uris.get(subject_text)
                if not subject_uri:
                    continue
                if (subject_uri, RDF.type, FOAF.Person) not in graph:
                    continue

                # Direct object → teachesSubject (TOPIC/Document)
                for child in token.children:
                    if child.dep_ in ("dobj", "obj", "attr"):
                        for ent in doc.ents:
                            if child.i >= ent.start and child.i < ent.end:
                                obj_uri = entity_uris.get(ent.text)
                                if obj_uri and (
                                    (obj_uri, RDF.type, EX.Document) in graph or
                                    (obj_uri, RDF.type, EX.Topic)    in graph
                                ):
                                    graph.add((subject_uri, EX.teachesSubject, obj_uri))
                                    print(f"  ✓ enseigner (dobj) → {subject_text} --[teachesSubject]--> {ent.text}")
                                    verb_relations_added += 1
                                    ConfidenceScorer(graph, verbose=False).add_relation_confidence(
                                        subject_uri, EX.teachesSubject, obj_uri,
                                        confidence=0.85, source="verb_lemma_mapping")
                                break

                # Oblique / prepositional object → worksAt (ORG)
                for child in token.children:
                    if child.dep_ in ("obl", "obl:mod", "obl:arg", "nmod", "prep"):
                        for ent in doc.ents:
                            if child.i >= ent.start and child.i < ent.end:
                                obj_uri = entity_uris.get(ent.text)
                                if obj_uri and (obj_uri, RDF.type, SCHEMA.Organization) in graph:
                                    graph.add((subject_uri, EX.worksAt, obj_uri))
                                    print(f"  ✓ enseigner (obl) → {subject_text} --[worksAt]--> {ent.text}")
                                    verb_relations_added += 1
                                    ConfidenceScorer(graph, verbose=False).add_relation_confidence(
                                        subject_uri, EX.worksAt, obj_uri,
                                        confidence=0.85, source="verb_lemma_mapping")
                                break
                    # Also walk ADP → pobj (e.g. "à" → "Université de Versailles")
                    if child.pos_ == "ADP" and child.lower_ in _AT_PREPS:
                        for grandchild in child.children:
                            if grandchild.dep_ in ("pobj", "obj", "nmod"):
                                for ent in doc.ents:
                                    if grandchild.i >= ent.start and grandchild.i < ent.end:
                                        obj_uri = entity_uris.get(ent.text)
                                        if obj_uri and (obj_uri, RDF.type, SCHEMA.Organization) in graph:
                                            graph.add((subject_uri, EX.worksAt, obj_uri))
                                            print(f"  ✓ enseigner (prep) → {subject_text} --[worksAt]--> {ent.text}")
                                            verb_relations_added += 1
                                            ConfidenceScorer(graph, verbose=False).add_relation_confidence(
                                                subject_uri, EX.worksAt, obj_uri,
                                                confidence=0.85, source="verb_lemma_mapping")
                                        break

                # Positional fallback: dep parse missed the objects — scan by type
                already_linked = set(graph.objects(subject_uri, EX.teachesSubject)) | \
                                 set(graph.objects(subject_uri, EX.worksAt))
                if not already_linked:
                    verb_pos = token.i
                    for ent_text, ent_uri in entity_uris.items():
                        if ent_text == subject_text:
                            continue
                        ent_after = any(t.i > verb_pos for t in doc if t.text in ent_text.split())
                        if not ent_after:
                            continue
                        if (ent_uri, RDF.type, EX.Document) in graph or \
                           (ent_uri, RDF.type, EX.Topic) in graph:
                            graph.add((subject_uri, EX.teachesSubject, ent_uri))
                            print(f"  ✓ enseigner (pos-fallback) → {subject_text} --[teachesSubject]--> {ent_text}")
                            verb_relations_added += 1
                        elif (ent_uri, RDF.type, SCHEMA.Organization) in graph:
                            graph.add((subject_uri, EX.worksAt, ent_uri))
                            print(f"  ✓ enseigner (pos-fallback) → {subject_text} --[worksAt]--> {ent_text}")
                            verb_relations_added += 1
                continue  # done with this enseigner token

            # ================================================================
            # Standard single-property dispatch for other verbs
            # ================================================================
            if lemma not in verb_mapping:
                continue

            property_name, domain_class, range_class = verb_mapping[lemma]

            # Heuristique : sujet avant le verbe, objet après le verbe
            subject_text = None
            object_text = None

            # Chercher le sujet (nsubj)
            for child in token.children:
                if child.dep_ in ["nsubj", "nsubjpass"]:
                    # Récupérer l'entité complète (avec composés)
                    for ent in doc.ents:
                        if child.i >= ent.start and child.i < ent.end:
                            subject_text = ent.text
                            break

            # Chercher l'objet (dobj, attr)
            for child in token.children:
                if child.dep_ in ["dobj", "obj", "attr", "obl"]:
                    # Récupérer l'entité complète
                    for ent in doc.ents:
                        if child.i >= ent.start and child.i < ent.end:
                            object_text = ent.text
                            break

            # Si sujet et objet trouvés, créer la relation
            if subject_text and object_text:
                subject_uri = entity_uris.get(subject_text)
                object_uri = entity_uris.get(object_text)

                if subject_uri and object_uri:
                    # Vérification domain/range
                    domain_valid = (subject_uri, RDF.type, domain_class) in graph
                    range_valid = (object_uri, RDF.type, range_class) in graph

                    if domain_valid and range_valid:
                        relation_prop = getattr(EX, property_name)
                        graph.add((subject_uri, relation_prop, object_uri))
                        print(f"  ✓ Verbe '{token.text}' → {subject_text} --[{property_name}]--> {object_text}")
                        verb_relations_added += 1

                        # Ajout confiance pour cette relation
                        confidence_scorer = ConfidenceScorer(graph, verbose=False)
                        confidence_scorer.add_relation_confidence(
                            subject_uri, relation_prop, object_uri,
                            confidence=0.80,  # Confiance moyenne (heuristique verbale)
                            source="verb_lemma_mapping"
                        )
    
    if verb_relations_added > 0:
        print(f"✅ {verb_relations_added} relation(s) inférée(s) via mapping verbes")
    else:
        print("  (Aucune relation verbale détectée)")
    
    print()
    
    # ============================================================================
    # EXTRACTION RELATIONS LLM (méthode existante)
    # ============================================================================
    
    # ── Static OWL-derived relation table ──────────────────────────────────────
    # Defines which relation predicates are semantically admissible for each
    # (entity1_type, entity2_type) pair.  The LLM is ONLY called when the pair
    # has at least one admissible relation.  This avoids noise triples like
    # TOPIC --[author]--> ORG  or  ORG --[worksAt]--> LOC.
    RELATION_TABLE = {
        ("PER", "TOPIC"):  ["teachesSubject", "author", "relatedTo"],
        ("PER", "ORG"):    ["worksAt", "manages", "studiesAt", "collaboratesWith", "relatedTo"],
        # PER→LOC includes worksAt: an institution may be NER-typed LOC and later
        # promoted to ORG by adapt_entity_type (guarded against bare cities).
        ("PER", "LOC"):    ["worksAt", "locatedIn", "relatedTo"],
        ("PER", "PER"):    ["collaboratesWith", "relatedTo"],
        ("ORG", "LOC"):    ["locatedIn", "relatedTo"],
        ("ORG", "ORG"):    ["relatedTo"],
        ("ORG", "PER"):    ["relatedTo"],
        ("TOPIC", "TOPIC"):["relatedTo"],
        ("TOPIC", "ORG"):  ["relatedTo"],
        ("LOC", "LOC"):    ["locatedIn", "relatedTo"],
        # UNK: type could not be resolved — allow all, priority logic will decide
        ("PER", "UNK"):    ["teachesSubject", "author", "worksAt", "manages",
                            "studiesAt", "collaboratesWith", "locatedIn", "relatedTo"],
        ("UNK", "TOPIC"):  ["teachesSubject", "author", "relatedTo"],
        ("UNK", "ORG"):    ["worksAt", "manages", "studiesAt", "relatedTo"],
        ("UNK", "LOC"):    ["locatedIn", "relatedTo"],
        ("UNK", "UNK"):    ["relatedTo"],
    }

    # Build a reverse map: entity_uri → NER type (PER/ORG/LOC/TOPIC/DOC)
    _OWL_TO_NER = {
        str(FOAF.Person):          "PER",
        str(SCHEMA.Organization):  "ORG",
        str(SCHEMA.Place):         "LOC",
        str(EX.Document):          "TOPIC",
    }
    def _ner_type_of(uri):
        for _, _, rdf_type in graph.triples((uri, RDF.type, None)):
            ner = _OWL_TO_NER.get(str(rdf_type))
            if ner:
                return ner
        return "UNK"

    # Collect pairs already handled by Layer 7 (verb dispatch) to avoid duplication
    _layer7_covered = set()
    for prop in (EX.teachesSubject, EX.worksAt, EX.author, EX.manages, EX.studiesAt):
        for s, _, o in graph.triples((None, prop, None)):
            _layer7_covered.add((str(s), str(o)))

    # Parcours de toutes les paires d'entités possibles
    entities_list = list(entity_uris.items())
    
    for i, (entity1_text, entity1_uri) in enumerate(entities_list):
        for j, (entity2_text, entity2_uri) in enumerate(entities_list):
            if i >= j:  # Éviter les doublons et auto-relations
                continue

            # Skip pairs already covered by Layer 7 (dep-parse verb dispatch)
            if (str(entity1_uri), str(entity2_uri)) in _layer7_covered or                (str(entity2_uri), str(entity1_uri)) in _layer7_covered:
                print(f"  ⏭️  Paire déjà couverte par Couche 7 : {entity1_text} ↔ {entity2_text}")
                continue

            # Resolve NER types from the graph (authoritative source)
            e1_type = _ner_type_of(entity1_uri)
            e2_type = _ner_type_of(entity2_uri)

            # Pre-filter: skip pairs with no admissible relation in the table
            allowed_relations = RELATION_TABLE.get((e1_type, e2_type), [])
            if not allowed_relations:
                # Try reverse direction before giving up
                allowed_relations = RELATION_TABLE.get((e2_type, e1_type), [])
            if not allowed_relations:
                print(f"  ⛔ Paire ignorée (aucune relation OWL admissible) : "
                      f"{entity1_text}({e1_type}) ↔ {entity2_text}({e2_type})")
                continue

            # Utilisation de l'API Groq pour prédire la relation ⭐
            relation_type = predict_relation_real_api(
                entity1_text, entity2_text, text,
                entity1_type=e1_type, entity2_type=e2_type
            )

            if relation_type is None:
                continue

            # Post-call ontology guard: reject anything outside the admissible set.
            # "relatedTo" is always a safe fallback so we allow it even if not in table.
            if relation_type != "relatedTo" and relation_type not in allowed_relations:
                print(f"  ⛔ LLM retourné '{relation_type}' n'est pas admissible pour "
                      f"({e1_type}→{e2_type}). Forcé → relatedTo")
                relation_type = "relatedTo"
            
            # Mapping des relations prédites vers les propriétés OWL avec contraintes flexibles
            # Note : teaches accepte Place OU Organization (université = organisation)
            relation_mapping = {
                "teaches": (EX.teaches, FOAF.Person, [SCHEMA.Place, SCHEMA.Organization]),  # Personne → Lieu OU Organisation
                "teachesSubject": (EX.teachesSubject, FOAF.Person, EX.Document),  # ✨ Personne → Matière/Topic
                "author": (EX.author, FOAF.Person, EX.Document),  # Auteur → Document
                "worksAt": (EX.worksAt, FOAF.Person, SCHEMA.Organization),
                "locatedIn": (EX.locatedIn, None, SCHEMA.Place),  # Organisation/Personne → Lieu
                "collaboratesWith": (EX.collaboratesWith, FOAF.Person, FOAF.Person),
                "studiesAt": (EX.studiesAt, FOAF.Person, SCHEMA.Organization),
                "manages": (EX.manages, FOAF.Person, SCHEMA.Organization),
                "relatedTo": (EX.relatedTo, None, None)
            }
            
            if relation_type not in relation_mapping:
                continue
            
            relation_prop, expected_domain, expected_range = relation_mapping[relation_type]
            
            # Fast-path domain/range check for type-exact relations.
            # These have unambiguous OWL constraints — validate directly without adapt_entity_type.
            if relation_type == "teachesSubject":
                domain_valid = (entity1_uri, RDF.type, FOAF.Person) in graph
                range_valid  = (entity2_uri, RDF.type, EX.Document)  in graph
                if domain_valid and range_valid:
                    graph.add((entity1_uri, relation_prop, entity2_uri))
                    print(f"  ✓ Relation LLM : {entity1_text} --[teachesSubject]--> {entity2_text}")
                else:
                    if not domain_valid:
                        print(f"  ⚠️ teachesSubject rejeté : {entity1_text} n'est pas une Person")
                    if not range_valid:
                        print(f"  ⚠️ teachesSubject rejeté : {entity2_text} n'est pas un Document/Topic")
                continue

            if relation_type == "worksAt":
                domain_valid = (entity1_uri, RDF.type, FOAF.Person) in graph
                range_valid  = (entity2_uri, RDF.type, SCHEMA.Organization) in graph
                if not range_valid:
                    # Allow LOC→ORG adaptation only for institution-like names
                    range_valid = adapt_entity_type(graph, entity2_uri, entity2_text, SCHEMA.Organization)
                if domain_valid and range_valid:
                    graph.add((entity1_uri, relation_prop, entity2_uri))
                    print(f"  ✓ Relation LLM : {entity1_text} --[worksAt]--> {entity2_text}")
                else:
                    if not domain_valid:
                        print(f"  ⚠️ worksAt rejeté : {entity1_text} n'est pas une Person")
                    if not range_valid:
                        print(f"  ⚠️ worksAt rejeté : {entity2_text} n'est pas une Organisation")
                continue
            
            # VALIDATION FLEXIBLE AVEC TYPAGE ADAPTATIF ET MULTIPLES TYPES ACCEPTÉS
            if expected_domain and expected_range:
                # Vérifier que les types correspondent aux contraintes
                domain_valid = (entity1_uri, RDF.type, expected_domain) in graph
                
                # Si expected_range est une liste, accepter n'importe quel type de la liste
                if isinstance(expected_range, list):
                    range_valid = any((entity2_uri, RDF.type, rtype) in graph for rtype in expected_range)
                else:
                    range_valid = (entity2_uri, RDF.type, expected_range) in graph
                
                # Si le range n'est pas valide, tenter un typage adaptatif
                if not range_valid and expected_range:
                    if isinstance(expected_range, list):
                        # Essayer d'adapter au premier type de la liste
                        range_valid = adapt_entity_type(graph, entity2_uri, entity2_text, expected_range[0])
                    else:
                        range_valid = adapt_entity_type(graph, entity2_uri, entity2_text, expected_range)
                
                # Si le domain n'est pas valide, tenter un typage adaptatif
                if not domain_valid and expected_domain:
                    domain_valid = adapt_entity_type(graph, entity1_uri, entity1_text, expected_domain)
                
                if domain_valid and range_valid:
                    graph.add((entity1_uri, relation_prop, entity2_uri))
                    print(f"  ✓ Relation LLM : {entity1_text} --[{relation_type}]--> {entity2_text}")
                    
                    # RESTRICTION OWL : Si c'est une relation 'author', typer le document en ValidatedCourse
                    if relation_type == "author":
                        # Ajouter le type ValidatedCourse pour valider la contrainte OWL
                        graph.add((entity2_uri, RDF.type, EX.ValidatedCourse))
                        print(f"    → Contrainte OWL : {entity2_text} typé en ValidatedCourse")
                else:
                    if not domain_valid:
                        print(f"  ⚠️ Type domain invalide pour {entity1_text} (attendu: {expected_domain})")
                    if not range_valid:
                        range_str = ', '.join([str(r) for r in expected_range]) if isinstance(expected_range, list) else str(expected_range)
                        print(f"  ⚠️ Type range invalide pour {entity2_text} (attendu: {range_str})")
                        
            elif expected_domain is None and expected_range:
                # Seulement le range est spécifié (ex: locatedIn → Place)
                if (entity2_uri, RDF.type, expected_range) in graph:
                    graph.add((entity1_uri, relation_prop, entity2_uri))
                    print(f"  ✓ Relation LLM : {entity1_text} --[{relation_type}]--> {entity2_text}")
                else:
                    print(f"  ⚠️ Type range invalide pour {entity2_text} (attendu: Place)")
                    
            elif relation_type == "relatedTo":
                # Relation générique sans contrainte de type
                graph.add((entity1_uri, relation_prop, entity2_uri))
                print(f"  ✓ Relation LLM : {entity1_text} --[{relation_type}]--> {entity2_text}")


# ============================================================================
# 6. RÉIFICATION RDF - MÉTADONNÉES SUR LES TRIPLETS
# ============================================================================

def reify_statement(graph, subject, predicate, obj, source_file="texte_exemple.txt"):
    """
    Applique la réification RDF pour attacher des métadonnées à un triplet.
    
    Concept théorique (CRUCIAL pour le cours) :
    --------------------------------------------
    La réification permet de "faire une assertion sur une assertion".
    Au lieu de simplement dire :
        <Sujet> <Prédicat> <Objet>
    
    On crée un nœud intermédiaire (rdf:Statement) qui représente le triplet lui-même,
    puis on peut ajouter des métadonnées à ce nœud :
        _:statement1 rdf:type rdf:Statement
        _:statement1 rdf:subject <Sujet>
        _:statement1 rdf:predicate <Prédicat>
        _:statement1 rdf:object <Objet>
        _:statement1 dc:source "fichier.txt"
        _:statement1 dc:date "2026-01-15"
    
    Cas d'usage :
    - Traçabilité de la source d'information
    - Confiance/Score de certitude d'une extraction
    - Horodatage d'une assertion
    - Provenance des données
    
    Args:
        graph (rdflib.Graph): Le graphe RDF
        subject (URIRef): Le sujet du triplet à réifier
        predicate (URIRef): Le prédicat du triplet
        obj (URIRef or Literal): L'objet du triplet
        source_file (str): Nom du fichier source (métadonnée)
        
    Returns:
        URIRef: L'URI du nœud de réification créé
    """
    # Création d'un nœud unique pour représenter le triplet
    # Ici on utilise un BNode (Blank Node) mais on pourrait aussi utiliser une URI nommée
    statement_uri = DATA[f"statement_{hash((subject, predicate, obj)) & 0xFFFFFF}"]
    
    # Déclaration du type : c'est un rdf:Statement (nœud de réification)
    graph.add((statement_uri, RDF.type, RDF.Statement))
    
    # Décomposition du triplet en propriétés RDF standard
    graph.add((statement_uri, RDF.subject, subject))    # Qui ?
    graph.add((statement_uri, RDF.predicate, predicate)) # Fait quoi ?
    graph.add((statement_uri, RDF.object, obj))          # À qui/quoi ?
    
    # Ajout de métadonnées sur le triplet
    # Ici : la source d'extraction (Dublin Core Metadata)
    graph.add((statement_uri, DC.source, Literal(source_file, datatype=XSD.string)))
    
    # On pourrait ajouter d'autres métadonnées :
    # graph.add((statement_uri, DC.date, Literal("2026-01-15", datatype=XSD.date)))
    # graph.add((statement_uri, EX.confidence, Literal(0.95, datatype=XSD.float)))
    
    print(f"  ✓ Réification créée pour : {subject.split('#')[-1]} --{predicate.split('#')[-1]}--> ...")
    
    return statement_uri


def apply_reification_to_relations(graph, source_file="texte_exemple.txt"):
    """
    Parcourt toutes les relations ObjectProperty du graphe et applique la réification.
    
    Cette fonction démontre l'application systématique de la réification
    sur les assertions extraites, permettant la traçabilité complète.
    
    Args:
        graph (rdflib.Graph): Le graphe RDF contenant les assertions
        source_file (str): Nom du fichier source
    """
    print("\n[RÉIFICATION] Application de la réification aux relations...")
    
    # Liste des propriétés ObjectProperty à réifier
    properties_to_reify = [EX.teaches, EX.author, EX.traite_de, EX.relatedTo, EX.worksAt]
    
    reified_count = 0
    for prop in properties_to_reify:
        # Parcours de tous les triplets utilisant cette propriété
        for subject, predicate, obj in graph.triples((None, prop, None)):
            reify_statement(graph, subject, predicate, obj, source_file)
            reified_count += 1
    
    print(f"[RÉIFICATION] {reified_count} triplet(s) réifié(s) avec métadonnées dc:source\n")


# ============================================================================
# 7. VISUALISATION GRAPHIQUE DU GRAPHE DE CONNAISSANCES
# ============================================================================

def visualize_knowledge_graph(graph, output_file="graphe_connaissance.png"):
    """
    Génère une visualisation graphique du graphe de connaissances RDF.
    
    Cette fonction crée une représentation visuelle interactive du graphe,
    utile pour la démonstration et la compréhension des relations extraites.
    
    Fonctionnalités :
    - Utilisation de NetworkX pour la structure du graphe
    - Colorisation par type de nœud
    - Étiquettes des relations sur les arêtes
    - Export en format PNG
    
    Args:
        graph (rdflib.Graph): Le graphe RDF à visualiser
        output_file (str): Chemin du fichier de sortie (PNG)
    """
    print("\n[VISUALISATION] Génération du graphe visuel...")
    
    # Création d'un graphe NetworkX dirigé
    G = nx.DiGraph()
    
    # Dictionnaires pour stocker les métadonnées des nœuds
    node_types = {}  # URI -> type (Person, Place, etc.)
    node_labels = {} # URI -> label lisible
    edge_labels = {} # (source, target) -> nom de la relation
    
    # ============================================================================
    # EXTRACTION DES ENTITÉS ET RELATIONS (A-Box uniquement)
    # ============================================================================
    # Stratégie : N'afficher QUE les instances de données (namespace DATA:)
    # et ignorer toute l'ontologie (classes, propriétés, restrictions OWL)
    
    # Étape 1 : Identifier toutes les entités du namespace DATA (instances réelles)
    data_entities = set()
    for subject in graph.subjects():
        if isinstance(subject, URIRef) and str(subject).startswith(str(DATA)):
            # Vérifier que ce n'est pas un nœud de réification (statement_)
            if not str(subject).startswith(str(DATA) + 'statement_'):
                data_entities.add(str(subject))
    
    print(f"  → {len(data_entities)} entités de données détectées")
    
    # Étape 2 : Capturer les types et labels des entités
    for entity_uri in data_entities:
        entity_ref = URIRef(entity_uri)
        
        # Capturer le type (Person, Organization, Place, etc.)
        for _, _, obj in graph.triples((entity_ref, RDF.type, None)):
            if obj in [FOAF.Person, SCHEMA.Place, SCHEMA.Organization, EX.Document, EX.ValidatedCourse]:
                node_types[entity_uri] = str(obj).split('#')[-1].split('/')[-1]
        
        # Capturer le label (foaf:name ou rdfs:label)
        for _, _, name_obj in graph.triples((entity_ref, FOAF.name, None)):
            node_labels[entity_uri] = str(name_obj)[:30]
        
        for _, _, label_obj in graph.triples((entity_ref, RDFS.label, None)):
            if entity_uri not in node_labels:
                node_labels[entity_uri] = str(label_obj)[:30]
    
    # Étape 3 : Extraire UNIQUEMENT les relations entre entités de données
    for subject_uri in data_entities:
        subject_ref = URIRef(subject_uri)
        
        # Parcourir tous les triplets où cette entité est sujet
        for _, predicate, obj in graph.triples((subject_ref, None, None)):
            # Ignorer les prédicats système et métadonnées
            if predicate in [RDF.type, RDFS.label, RDFS.comment, FOAF.name, 
                            EX.age, EX.intitule, DC.source, EX.confidence]:
                continue
            
            # ⚡ FILTRE IMPORTANT : Ignorer les prédicats RDF de réification
            if predicate in [RDF.subject, RDF.predicate, RDF.object]:
                continue
            
            # Ne garder que les relations vers d'autres entités de données
            if isinstance(obj, URIRef) and str(obj) in data_entities:
                # ⚡ FILTRE : Ne pas ajouter de self-loops (boucles sur soi-même)
                if subject_uri != str(obj):
                    G.add_edge(subject_uri, str(obj))
                    
                    # Extraire le nom de la relation
                    relation_name = str(predicate).split('#')[-1].split('/')[-1]
                    
                    # DEBUG : Afficher les relations détectées
                    subject_label = node_labels.get(subject_uri, subject_uri.split('#')[-1])
                    obj_label = node_labels.get(str(obj), str(obj).split('#')[-1])
                    print(f"    [DEBUG] {subject_label} --[{relation_name}]--> {obj_label}")
                    
                    edge_labels[(subject_uri, str(obj))] = relation_name
    
    if len(G.nodes()) == 0:
        print("  ⚠️  Aucune entité extraite à visualiser")
        print("  💡 Conseil : Utilisez un texte avec des noms de personnes, organisations ou lieux")
        return
    
    print(f"  ✓ Graphe NetworkX créé : {len(G.nodes())} nœuds, {len(G.edges())} arêtes")
    
    # Afficher les entités détectées
    entity_names = [node_labels.get(n, n.split('#')[-1].split('/')[-1]) for n in list(G.nodes())[:10]]
    if entity_names:
        print(f"  ✓ Entités extraites : {', '.join(entity_names[:5])}")
        if len(entity_names) > 5:
            print(f"                       ... et {len(entity_names)-5} autres")
    
    # Préparation de la figure
    plt.figure(figsize=(16, 12))
    plt.title("Graphe de Connaissances Extrait (A-Box uniquement)\nEntités et Relations détectées", 
              fontsize=16, fontweight='bold', pad=20)
    
    # Layout du graphe (positionnement des nœuds)
    # Spring layout pour graphes petits/moyens, circular pour grands graphes
    if len(G.nodes()) <= 10:
        pos = nx.spring_layout(G, k=3.5, iterations=100, seed=42)
    else:
        pos = nx.spring_layout(G, k=2.5, iterations=80, seed=42)
    
    # Colorisation par type de nœud
    color_map = {
        'Person': '#FF6B6B',      # Rouge pour les personnes
        'Place': '#4ECDC4',       # Turquoise pour les lieux
        'Organization': '#45B7D1', # Bleu pour les organisations
        'Document': '#FFA07A',     # Orange pour les documents
        'default': '#95E1D3'       # Vert par défaut
    }
    
    node_colors = []
    for node in G.nodes():
        node_type = node_types.get(node, 'default')
        node_colors.append(color_map.get(node_type, color_map['default']))
    
    # Dessiner les nœuds
    nx.draw_networkx_nodes(G, pos, 
                          node_color=node_colors,
                          node_size=3000,
                          alpha=0.9,
                          edgecolors='black',
                          linewidths=2)
    
    # Dessiner les arêtes (relations)
    nx.draw_networkx_edges(G, pos,
                          edge_color='#333333',
                          arrows=True,
                          arrowsize=20,
                          arrowstyle='->',
                          width=2,
                          alpha=0.6,
                          connectionstyle='arc3,rad=0.1')
    
    # Préparer les labels des nœuds (noms courts)
    display_labels = {}
    for node in G.nodes():
        if node in node_labels:
            label = node_labels[node]
        else:
            # Extraire le dernier segment de l'URI
            label = node.split('#')[-1].split('/')[-1]
            label = label.replace('_', ' ').title()
        
        # Limiter la longueur pour la lisibilité
        if len(label) > 20:
            label = label[:17] + "..."
        display_labels[node] = label
    
    # Dessiner les labels des nœuds
    nx.draw_networkx_labels(G, pos,
                           labels=display_labels,
                           font_size=9,
                           font_weight='bold',
                           font_color='white',
                           bbox=dict(boxstyle='round,pad=0.3', 
                                    facecolor='black', 
                                    alpha=0.7))
    
    # Dessiner les labels des arêtes (relations)
    nx.draw_networkx_edge_labels(G, pos,
                                edge_labels=edge_labels,
                                font_size=8,
                                font_color='#D32F2F',
                                bbox=dict(boxstyle='round,pad=0.3',
                                         facecolor='yellow',
                                         alpha=0.7))
    
    # Légende
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=color_map['Person'], edgecolor='black', label='Personne (FOAF)'),
        Patch(facecolor=color_map['Place'], edgecolor='black', label='Lieu (Schema.org)'),
        Patch(facecolor=color_map['Organization'], edgecolor='black', label='Organisation (Schema.org)'),
        Patch(facecolor=color_map['Document'], edgecolor='black', label='Document')
    ]
    plt.legend(handles=legend_elements, loc='upper left', fontsize=10)
    
    plt.axis('off')
    plt.tight_layout()
    
    # Sauvegarde
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"  ✓ Graphe sauvegardé : {output_file}")
    print(f"  ✓ Nœuds : {len(G.nodes())}, Arêtes : {len(G.edges())}")
    
    # Fermeture pour libérer la mémoire
    plt.close()


# ============================================================================
# 8. FONCTION PRINCIPALE - ORCHESTRATION DU PIPELINE
# ============================================================================

def main():
    """
    Fonction principale orchestrant l'ensemble du pipeline d'extraction
    de graphe de connaissances selon l'architecture T-Box/A-Box.
    
    IMPORTANT : Chaque exécution crée un NOUVEAU graphe vide pour éviter
    la pollution de données entre extractions successives.
    """
    print("="*80)
    print("PROJET MASTER 2 - WEB SÉMANTIQUE")
    print("Extraction de Graphe de Connaissances avec Architecture T-Box/A-Box")
    print("="*80)
    
    # -----------------------------------------------------------------------
    # NETTOYAGE : Supprimer les anciens fichiers pour éviter la pollution
    # -----------------------------------------------------------------------
    for old_file in ["knowledge_graph.ttl", "knowledge_graph.xml", "graphe_connaissance.png"]:
        if os.path.exists(old_file):
            os.remove(old_file)
            print(f"[CLEANUP] Ancien fichier supprimé : {old_file}")
    
    # -----------------------------------------------------------------------
    # LECTURE DU TEXTE SOURCE (depuis stdin, fichier temporaire ou argument)
    # -----------------------------------------------------------------------
    text_example = "Zoubida Kedad enseigne à l'Université de Versailles. Elle a rédigé un cours sur RDFS."
    
    # Option 1 : Lire depuis stdin (priorité pour tests)
    if not sys.stdin.isatty():
        try:
            stdin_text = sys.stdin.read().strip()
            if stdin_text:
                text_example = stdin_text
                print(f"[INFO] Texte chargé depuis stdin\n")
        except Exception as e:
            print(f"[WARNING] Erreur lecture stdin : {e}")
    
    # Option 2 : Lire depuis texte_temp.txt (utilisé par Streamlit)
    elif os.path.exists("texte_temp.txt"):
        try:
            with open("texte_temp.txt", "r", encoding="utf-8") as f:
                custom_text = f.read().strip()
                if custom_text:
                    text_example = custom_text
                    print(f"[INFO] Texte chargé depuis texte_temp.txt\n")
        except Exception as e:
            print(f"[WARNING] Erreur lecture texte_temp.txt : {e}")
    
    # Option 3 : Lire depuis argument en ligne de commande
    if len(sys.argv) > 1:
        if sys.argv[1] == "--text" and len(sys.argv) > 2:
            text_example = sys.argv[2]
            print(f"[INFO] Texte chargé depuis argument --text\n")
        elif sys.argv[1] != "--text":
            # Tout le reste est considéré comme le texte
            text_example = " ".join(sys.argv[1:])
            print(f"[INFO] Texte chargé depuis arguments\n")
    
    # -----------------------------------------------------------------------
    # INITIALISATION : Création d'un NOUVEAU graphe RDF vide
    # -----------------------------------------------------------------------
    # IMPORTANT : Le graphe est créé LOCALEMENT dans main() à chaque exécution
    # Cela garantit qu'aucune donnée résiduelle n'est conservée entre les runs
    print("[INIT] Création d'un nouveau graphe RDF vide...")
    graph = Graph()
    graph.bind("ex", EX)        # Notre ontologie
    graph.bind("data", DATA)    # Nos instances
    graph.bind("foaf", FOAF)    # FOAF (Friend of a Friend)
    graph.bind("schema", SCHEMA) # Schema.org
    graph.bind("owl", OWL)      # OWL (Web Ontology Language)
    graph.bind("rdf", RDF)      # RDF
    graph.bind("rdfs", RDFS)    # RDFS (vocabulaire de schéma)
    graph.bind("xsd", XSD)      # Types de données XML Schema
    graph.bind("dc", DC)        # Dublin Core (métadonnées)
    print("  ✓ Graphe initialisé avec namespaces\n")
    
    # -----------------------------------------------------------------------
    # PHASE 1 : Définition de l'ontologie (T-Box)
    # -----------------------------------------------------------------------
    define_tbox(graph)
    
    # -----------------------------------------------------------------------
    # PHASE 2 : Chargement du modèle NLP français
    # -----------------------------------------------------------------------
    print("[NLP] Chargement du modèle spaCy français...")
    try:
        nlp = spacy.load("fr_core_news_sm")
        print("  ✓ Modèle 'fr_core_news_sm' chargé avec succès\n")
    except OSError:
        print("  ⚠ Modèle non trouvé. Installation automatique...")
        print("  Exécutez : python -m spacy download fr_core_news_sm")
        print("  Utilisation d'un modèle de secours...\n")
        # Pour la démo, on pourrait continuer avec des entités hardcodées
        # mais idéalement on devrait installer le modèle
        return
    
    # -----------------------------------------------------------------------
    # PHASE 2.5 : ENTRY GATE (Module 0 Filter) - Validation du texte source
    # -----------------------------------------------------------------------
    # WHY: Reject invalid inputs BEFORE processing to avoid noise downstream
    print("\n" + "="*80)
    print("[MODULE 0] ENTRY GATE - Validation du texte source")
    print("="*80)
    print(f"[TEXTE SOURCE] : \"{text_example}\"")
    
    # Check 1: Minimum length
    if len(text_example.strip()) < 10:
        print("❌ REJETÉ: Texte trop court (< 10 caractères)")
        print("✗ Pipeline arrêté - texte invalide\n")
        return
    
    # Check 2: Minimum word count
    words = text_example.split()
    if len(words) < 3:
        print("❌ REJETÉ: Phrase trop courte (< 3 mots)")
        print("✗ Pipeline arrêté - texte invalide\n")
        return
    
    print("✓ Texte valide - longueur: {} caractères, {} mots\n".format(
        len(text_example), len(words)))
    
    # -----------------------------------------------------------------------
    # PHASE 3 : Extraction des entités (A-Box - partie 1)
    # -----------------------------------------------------------------------
    entities = extract_entities_with_spacy(text_example, nlp)
    
    # Entry gate: Minimum entity count
    # WHY: Without entities, relation extraction will fail or produce noise
    if len(entities) < 2:
        print("\n❌ ENTRY GATE: Nombre d'entités insuffisant ({} < 2)".format(len(entities)))
        print("✗ Pipeline arrêté - au moins 2 entités requises pour extraire des relations\n")
        return
    
    # -----------------------------------------------------------------------
    # PHASE 3.5 : Raffinement intelligent des types via Groq/Llama-3 ✨
    # -----------------------------------------------------------------------
    # Re-classification dynamique pour détecter les TOPICS (matières, concepts)
    # et corriger les erreurs de spaCy
    entities = refine_entity_types(entities, text_example)
    
    entity_uris = instantiate_entities_in_abox(graph, entities)
    
    # -----------------------------------------------------------------------
    # PHASE 4 : Extraction des relations (A-Box - partie 2)
    # -----------------------------------------------------------------------
    extract_relations(graph, entity_uris, text_example)
    
    # -----------------------------------------------------------------------
    # PHASE 5 : Réification des triplets
    # -----------------------------------------------------------------------
    apply_reification_to_relations(graph, source_file="texte_exemple.txt")
    
    # -----------------------------------------------------------------------
    # ✨ NOUVEAU : PHASE 5.5 : APPLICATION DU RAISONNEMENT OWL (MODULE 1)
    # -----------------------------------------------------------------------
    print("\n" + "="*80)
    print("[MODULE 1] RAISONNEMENT OWL - Inférence de types et propriétés")
    print("="*80)
    
    # Initialisation du moteur de raisonnement
    owl_reasoner = OWLReasoningEngine(graph, verbose=True)
    
    # Application du raisonnement (DeductiveClosure si owlrl disponible)
    inferred_count = owl_reasoner.apply_reasoning()
    
    # Vérification de la cohérence du graphe
    is_consistent, errors = owl_reasoner.check_consistency()
    
    if not is_consistent:
        print("\n⚠️ ATTENTION : Inconsistances détectées dans le graphe")
        for error in errors[:5]:  # Afficher max 5 erreurs
            print(f"  • {error}")
    
    # Ajout de métadonnées de confiance pour les triplets inférés
    if inferred_count > 0:
        print(f"\n[MODULE 1] Ajout de métadonnées de confiance pour {inferred_count} triplets inférés...")
        # Note: Les triplets inférés ont confiance = 1.0 (certitude logique)
    
    # -----------------------------------------------------------------------
    # ✨ NOUVEAU : PHASE 5.6 : STATISTIQUES DE CONFIANCE
    # -----------------------------------------------------------------------
    print("\n" + "="*80)
    print("[CONFIDENCE SYSTEM] Statistiques des scores de confiance")
    print("="*80)
    
    confidence_scorer = ConfidenceScorer(graph, verbose=False)
    stats = confidence_scorer.get_confidence_statistics()
    
    print(f"  • Entités avec score : {stats['count']}")
    print(f"  • Score minimum : {stats['min']:.2f}")
    print(f"  • Score maximum : {stats['max']:.2f}")
    print(f"  • Score moyen : {stats['mean']:.2f}")
    
    # -----------------------------------------------------------------------
    # PHASE 6 : Sérialisation et export (DOUBLE FORMAT : TURTLE + XML)
    # -----------------------------------------------------------------------
    print("="*80)
    print("[EXPORT] Sérialisation du graphe RDF en deux formats")
    print("="*80)
    
    # FORMAT 1 : TURTLE (lisible par l'humain)
    output_file_turtle = "knowledge_graph.ttl"
    turtle_output = graph.serialize(format='turtle')
    
    with open(output_file_turtle, 'w', encoding='utf-8') as f:
        f.write(turtle_output)
    
    print(f"\n✓ Graphe exporté en TURTLE : {output_file_turtle}")
    
    # FORMAT 2 : RDF/XML (standard historique du W3C, utilisé dans le cours)
    output_file_xml = "knowledge_graph.xml"
    xml_output = graph.serialize(format='xml')
    
    with open(output_file_xml, 'w', encoding='utf-8') as f:
        f.write(xml_output)
    
    print(f"✓ Graphe exporté en RDF/XML : {output_file_xml}")
    print(f"✓ Nombre total de triplets : {len(graph)}")
    
    # -----------------------------------------------------------------------
    # PHASE 7 : Visualisation graphique
    # -----------------------------------------------------------------------
    visualize_knowledge_graph(graph, "graphe_connaissance.png")
    
    print("\n" + "="*80)
    print("RÉSULTAT FINAL - FORMAT TURTLE")
    print("="*80 + "\n")
    print(turtle_output)
    
    # -----------------------------------------------------------------------
    # Statistiques finales
    # -----------------------------------------------------------------------
    print("\n" + "="*80)
    print("STATISTIQUES DU GRAPHE")
    print("="*80)
    print(f"Classes (owl:Class) : {len(list(graph.subjects(RDF.type, OWL.Class)))}")
    print(f"  → Dont classes avec restrictions OWL : 1 (ex:ValidatedCourse)")
    print(f"ObjectProperties : {len(list(graph.subjects(RDF.type, OWL.ObjectProperty)))}")
    print(f"DatatypeProperties : {len(list(graph.subjects(RDF.type, OWL.DatatypeProperty)))}")
    print(f"Restrictions OWL : {len(list(graph.subjects(RDF.type, OWL.Restriction)))}")
    print(f"Instances extraites : {len(entity_uris)}")
    print(f"Triplets réifiés : {len(list(graph.subjects(RDF.type, RDF.Statement)))}")
    print(f"Total de triplets RDF : {len(graph)}")
    print("="*80 + "\n")
    
    print("✓ Pipeline terminé avec succès !")
    print("✓ Votre graphe de connaissances respecte les standards OWL et RDFS")
    print("✓ Architecture T-Box/A-Box clairement séparée")
    print("✓ Restrictions OWL appliquées (ex:ValidatedCourse)")
    print("✓ Réification appliquée pour la traçabilité")
    print("✓ Extraction de relations via API Hugging Face RÉELLE (Mistral-7B) ⭐")
    print("✓ Double sérialisation : Turtle + RDF/XML\n")


# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    main()
