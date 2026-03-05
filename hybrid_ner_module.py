#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODULE 0++ : EXTRACTION HYBRIDE NER (7 COUCHES)

Architecture Neuro-Symbolique Complète :
========================================
1. spaCy NER baseline (réseau neuronal)
2. EntityRuler (patterns symboliques)
3. Heuristiques linguistiques (PROPN)
4. Normalisation + déduplication
5. Filtrage par confiance
6. Vérification type ontologique
7. Mapping lemme → propriété OWL

Auteur : Implémentation académique Master 2 Web Sémantique
Date : 28 février 2026
Révision : Conformité audit technique
"""

import re
import unicodedata
from typing import List, Tuple, Dict, Set, Optional
from rdflib import Graph, URIRef, Namespace, RDF, OWL
import spacy
from spacy.language import Language
from spacy.tokens import Doc, Token


# ============================================================================
# CONFIGURATION
# ============================================================================

# Namespace pour validation ontologique
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
SCHEMA = Namespace("http://schema.org/")
EX = Namespace("http://example.org/master2/ontology#")


# ============================================================================
# MODULE 0 — NORMALISATION DU TEXTE D'ENTRÉE
# ============================================================================

def normalize_input_text(text: str) -> str:
    """
    Normalise le texte avant l'extraction NER (Module 0 preprocessing).

    Corrections appliquées :
      1. Ponctuation répétée   : "Prof.." → "Prof.", "!!!" → "!"
      2. Mots entièrement en MAJUSCULES → Title Case, sauf acronymes connus
         (RDF, OWL, SPARQL, INRIA, CNRS, MIT, AI, ML, DL, NLP, KG, CV, GL …)
      3. Espaces multiples / tabulations → espace simple

    Args:
        text: Texte brut en entrée.

    Returns:
        Texte nettoyé.
    """
    # Known acronyms/abbreviations that must stay uppercase
    _KEEP_UPPER: frozenset = frozenset([
        # Tech standards
        "RDF", "RDFS", "OWL", "SPARQL", "JSON", "XML", "HTML", "HTTP",
        "URI", "URL", "API", "SQL", "CSS",
        # AI/ML acronyms
        "AI", "ML", "DL", "NLP", "KG", "CV", "GL", "NLU", "NLG",
        # Institutions / organisations
        "INRIA", "CNRS", "MIT", "IEEE", "ACM", "NIST",
        "UN", "EU", "USA", "UK",
        # Common French abbreviations
        "UFR", "IUT", "BTS", "DEUG", "DESS",
    ])

    # 1. Repeated punctuation
    text = re.sub(r'([.!?,;:])\1+', r'\1', text)        # "Prof.." → "Prof."
    text = re.sub(r'\.{3,}', ' ', text)                 # "…" (3+ dots) → space
    text = re.sub(r'[!?]{2,}', '!', text)               # "!!!" → "!"

    # 2. ALL-CAPS words → Title Case (unless in _KEEP_UPPER)
    def _fix_allcaps(m: re.Match) -> str:
        w = m.group(0)
        if w in _KEEP_UPPER:
            return w          # preserve known acronyms
        if len(w) <= 2:
            return w          # keep 1-2 char tokens (LE, DE, DU …)
        return w.capitalize()

    text = re.sub(r'\b[A-ZÀÂÉÈÊÙÛÎÔŒÆÇ]{2,}\b', _fix_allcaps, text)

    # 3. Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text


# ============================================================================
# CLASSE PRINCIPALE : HybridNERModule
# ============================================================================

class HybridNERModule:
    """
    Extracteur d'entités hybride combinant 7 couches de traitement.
    
    Architecture Académique :
    -------------------------
    COUCHE 1 : spaCy NER (réseau neuronal fr_core_news_sm)
    COUCHE 2 : EntityRuler (patterns regex pour entités académiques)
    COUCHE 3 : Heuristiques PROPN (détection noms propres composés)
    COUCHE 4 : Normalisation (standardisation casse/espaces/accents)
    COUCHE 5 : Déduplication (canonicalisation + élimination doublons)
    COUCHE 6 : Filtrage Confiance (seuil de certitude minimum)
    COUCHE 7 : Validation Ontologique (vérification types OWL déclarés)
    
    Utilisation :
    -------------
    >>> nlp = spacy.load("fr_core_news_sm")
    >>> graph = Graph()  # Graphe ontologique
    >>> ner = HybridNERModule(nlp, ontology_graph=graph, enable_validation=True)
    >>> entities = ner.extract("Zoubida Kedad enseigne à l'Université de Versailles")
    >>> # [("Zoubida Kedad", "PER", 0.95), ("Université de Versailles", "ORG", 0.92)]
    """

    # ── Classe-level constants ──────────────────────────────────────────────

    TECH_CONCEPT_KEYWORDS: frozenset = frozenset([
        # Web & Linked Data
        "rdf", "rdfs", "owl", "sparql", "turtle", "json-ld", "n-triples",
        "linked data", "linked open data", "lod",
        "web sémantique", "semantic web",
        # Ontology & KG
        "ontologie", "ontology", "knowledge graph", "graphe de connaissances",
        "triple store", "triplestore", "reasoner", "raisonneur",
        "inference", "inférence", "kg",
        # Standards & formats
        "namespace", "uri", "iri", "xsd", "dc", "foaf", "schema.org",
        "wikidata", "dbpedia",
        # Paradigms
        "intelligence artificielle", "artificial intelligence",
        "machine learning", "apprentissage automatique",
        "natural language processing", "traitement du langage naturel",
        "nlp", "tal",
        "deep learning", "neural network", "réseau de neurones",
        "big data", "données massives",
        # Short academic acronyms (Task 3)
        "ai", "ml", "dl", "cv",
        "algebra", "algèbre",
        "databases", "base de données", "bases de données",
        "génie logiciel", "gl",
        "réseaux", "networks",
        "systèmes", "systems",
        "compilation", "compilateurs",
        "arithmétique", "arithmetic",
        "statistiques", "statistics",
        "probabilités", "probabilities",
        "complexité", "complexity",
        "théorie des graphes", "graph theory",
        # Algorithms & structures
        "algorithme", "algorithm", "framework", "architecture",
        "api", "rest", "graphql",
        # Teaching subjects (generic)
        "mathématiques", "mathematics", "physique", "physics",
        "informatique", "computer science",
        "programmation", "programming",
        "data", "données",
        "data mining", "fouille de données",
        "data science", "text mining",
        "information retrieval", "recherche d'information",
        # Additional academic subjects
        "formal verification", "vérification formelle",
        "quantum computing", "quantum error correction", "informatique quantique",
        "parallel computing", "calcul parallèle",
        "bioinformatique", "bioinformatics",
        "sécurité informatique", "cybersécurité", "cybersecurity",
        "réseaux de neurones", "vision par ordinateur",
        "raisonnement automatique", "automated reasoning",
        "knowledge engineering", "ingénierie des connaissances",
        "semantic web", "web semantique",
        "computer vision", "robotique", "robotics",
        "optimisation", "optimization",
        "cryptographie", "cryptography",
        "théorie des langages", "language theory",
        "algorithmique", "algorithmics",
    ])

    HUMAN_NAME_INDICATORS: frozenset = frozenset([
        "dr", "dr.", "prof", "prof.", "professeur", "docteur",
        "mr", "mr.", "mrs", "mrs.", "mme", "mme.", "monsieur", "madame",
    ])

    def __init__(
        self, 
        nlp: Language,
        confidence_threshold: float = 0.5,
        ontology_graph: Optional[Graph] = None,
        enable_validation: bool = False
    ):
        """
        Initialise le module NER hybride.
        
        Args:
            nlp: Modèle spaCy chargé (doit contenir 'ner')
            confidence_threshold: Seuil minimum de confiance (0.0 à 1.0)
            ontology_graph: Graphe RDFLib pour validation ontologique (optionnel)
            enable_validation: Active la couche 7 (validation types OWL)
        """
        self.nlp = nlp
        self.confidence_threshold = confidence_threshold
        self.ontology_graph = ontology_graph
        self.enable_validation = enable_validation
        
        # COUCHE 2 : Configuration de l'EntityRuler
        self._setup_entity_ruler()
        
        # COUCHE 7 : Mapping lemme → propriété OWL
        self.verb_to_property_map = {
            "enseigner": ("teaches", FOAF.Person, EX.Document),
            "écrire": ("author", FOAF.Person, EX.Document),
            "travailler": ("worksAt", FOAF.Person, SCHEMA.Organization),
            "diriger": ("manages", FOAF.Person, SCHEMA.Organization),
            "publier": ("publishes", FOAF.Person, EX.Document),
            "étudier": ("studies", FOAF.Person, EX.Document),
            "créer": ("creates", FOAF.Person, None),
            "développer": ("develops", FOAF.Person, None),
        }
        
        print("[HybridNERModule] ✅ Initialisé avec 7 couches activées")
    
    def _setup_entity_ruler(self):
        """
        COUCHE 2 : Configuration de l'EntityRuler avec patterns personnalisés.
        
        L'EntityRuler permet d'ajouter des règles symboliques pour détecter
        des entités spécifiques qui échappent au modèle neuronal.
        
        Patterns ajoutés :
        - Universités françaises
        - Matières académiques (TOPIC)
        - Titres académiques (Professeur, Dr)
        """
        # Vérifier si l'EntityRuler existe déjà
        if "entity_ruler" not in self.nlp.pipe_names:
            ruler = self.nlp.add_pipe("entity_ruler", before="ner")
            
            # Patterns pour entités académiques françaises
            patterns = [
                # ── Universités : formes spécifiques ──────────────────────
                {"label": "ORG", "pattern": "Université Paris-Saclay"},
                {"label": "ORG", "pattern": "Université de Versailles"},
                {"label": "ORG", "pattern": "Sorbonne Université"},
                {"label": "ORG", "pattern": "École Polytechnique"},
                {"label": "ORG", "pattern": "Université de Lyon"},
                {"label": "ORG", "pattern": "Université de Paris"},
                {"label": "ORG", "pattern": "Université de Bordeaux"},
                {"label": "ORG", "pattern": "Université de Strasbourg"},
                {"label": "ORG", "pattern": "Université de Lille"},
                {"label": "ORG", "pattern": "Université de Montpellier"},
                {"label": "ORG", "pattern": "Université de Rennes"},
                {"label": "ORG", "pattern": "Université de Grenoble"},
                {"label": "ORG", "pattern": "Université de Nantes"},
                {"label": "ORG", "pattern": "Université de Toulon"},
                {"label": "ORG", "pattern": "University of Oxford"},
                {"label": "ORG", "pattern": "University of Cambridge"},
                {"label": "ORG", "pattern": "MIT Media Lab"},
                # Generic: université/university + one title-case word
                {"label": "ORG", "pattern": [{"LOWER": "université"}, {"IS_TITLE": True}]},
                {"label": "ORG", "pattern": [{"LOWER": "university"}, {"LOWER": "of"}, {"IS_TITLE": True}]},
                {"label": "ORG", "pattern": [{"LOWER": {"IN": ["institute", "institut"]}}, {"IS_TITLE": True}]},
                {"label": "ORG", "pattern": [{"LOWER": {"IN": ["center", "centre"]}}, {"LOWER": {"IN": ["de", "of", "for"]}}, {"IS_TITLE": True}]},
                {"label": "ORG", "pattern": [{"LOWER": {"IN": ["department", "département"]}}, {"LOWER": "of"}, {"IS_TITLE": True}]},
                {"label": "ORG", "pattern": [{"LOWER": {"IN": ["école", "school", "college"]}}, {"IS_TITLE": True}]},

                # ── Matières/Topics académiques ────────────────────────────
                {"label": "TOPIC", "pattern": "Web Sémantique"},
                {"label": "TOPIC", "pattern": "web sémantique"},
                {"label": "TOPIC", "pattern": "Intelligence Artificielle"},
                {"label": "TOPIC", "pattern": "intelligence artificielle"},
                {"label": "TOPIC", "pattern": "Bases de Données"},
                {"label": "TOPIC", "pattern": "bases de données"},
                {"label": "TOPIC", "pattern": "base de données"},
                {"label": "TOPIC", "pattern": "Génie Logiciel"},
                {"label": "TOPIC", "pattern": "génie logiciel"},
                {"label": "TOPIC", "pattern": "Réseaux de Neurones"},
                {"label": "TOPIC", "pattern": "réseaux de neurones"},
                {"label": "TOPIC", "pattern": "mathématiques"},
                {"label": "TOPIC", "pattern": "physique"},
                {"label": "TOPIC", "pattern": "informatique"},
                {"label": "TOPIC", "pattern": "algorithmes"},
                {"label": "TOPIC", "pattern": "réseaux"},
                {"label": "TOPIC", "pattern": "machine learning"},
                {"label": "TOPIC", "pattern": "deep learning"},
                {"label": "TOPIC", "pattern": "Théorie des Graphes"},
                {"label": "TOPIC", "pattern": "théorie des graphes"},
                {"label": "TOPIC", "pattern": "Compilation"},
                {"label": "TOPIC", "pattern": "compilation"},
                {"label": "TOPIC", "pattern": "Algèbre"},
                {"label": "TOPIC", "pattern": "algèbre"},
                {"label": "TOPIC", "pattern": "Algebra"},
                {"label": "TOPIC", "pattern": "Databases"},
                {"label": "TOPIC", "pattern": "Graph Theory"},
                {"label": "TOPIC", "pattern": "Computer Science"},
                {"label": "TOPIC", "pattern": "Data Science"},
                {"label": "TOPIC", "pattern": "data science"},
                {"label": "TOPIC", "pattern": "Knowledge Engineering"},
                {"label": "TOPIC", "pattern": "Semantic Web"},
                {"label": "TOPIC", "pattern": "semantic web"},
                {"label": "TOPIC", "pattern": "Natural Language Processing"},
                {"label": "TOPIC", "pattern": "natural language processing"},
                # Short academic acronyms (Task 3)
                {"label": "TOPIC", "pattern": [{"TEXT": {"REGEX": r"^(AI|ML|DL|NLP|KG|CV|GL)$"}}]},
                # Common multi-word academic subjects
                {"label": "TOPIC", "pattern": "Data Mining"},
                {"label": "TOPIC", "pattern": "data mining"},
                {"label": "TOPIC", "pattern": "Text Mining"},
                {"label": "TOPIC", "pattern": "Information Retrieval"},
                {"label": "TOPIC", "pattern": "information retrieval"},
                {"label": "TOPIC", "pattern": "Data Science"},
                {"label": "TOPIC", "pattern": "data science"},
                # English department patterns
                {"label": "ORG", "pattern": "Department of Computer Science"},
                {"label": "ORG", "pattern": "Department of Mathematics"},
                {"label": "ORG", "pattern": "Department of Physics"},
                {"label": "ORG", "pattern": [{"LOWER": "department"}, {"LOWER": "of"}, {"IS_TITLE": True}]},
                {"label": "ORG", "pattern": [{"LOWER": "dept"}, {"LOWER": "of"}, {"IS_TITLE": True}]},

                # ── Technologies (DOCUMENT context) ───────────────────────
                {"label": "DOCUMENT", "pattern": "RDF"},
                {"label": "DOCUMENT", "pattern": "RDFS"},
                {"label": "DOCUMENT", "pattern": "OWL"},
                {"label": "DOCUMENT", "pattern": "SPARQL"},
                {"label": "DOCUMENT", "pattern": "JSON-LD"},
                {"label": "DOCUMENT", "pattern": "Turtle"},

                # ── Titres académiques ─────────────────────────────────────
                {"label": "PER", "pattern": [{"LOWER": {"IN": ["professeur", "prof", "dr", "docteur"]}}, {"IS_TITLE": True}]},
            ]
            
            ruler.add_patterns(patterns)
            print("  [Couche 2] EntityRuler configuré : Universités, Topics, Titres")
        else:
            print("  [Couche 2] EntityRuler déjà présent dans le pipeline")
    
    def extract(self, text: str, verbose: bool = True) -> List[Tuple[str, str, float]]:
        """
        Extrait les entités avec les 7 couches de traitement.
        
        Pipeline complet :
        ------------------
        1. spaCy NER + EntityRuler → entités brutes
        2. Heuristiques PROPN → entités composées supplémentaires
        3. Normalisation → standardisation texte
        4. Déduplication → élimination doublons
        5. Filtrage confiance → seuil qualité
        6. Validation ontologique → vérification types OWL (si activée)
        
        Args:
            text: Texte à analyser
            verbose: Affiche logs détaillés (default: True)
            
        Returns:
            Liste de tuples (entité, type, confiance)
            Exemple: [("Zoubida Kedad", "PER", 0.95), ("Web Sémantique", "TOPIC", 0.85)]
        """
        if verbose:
            print("\n" + "="*80)
            print("MODULE 0++ : EXTRACTION HYBRIDE NER (7 COUCHES)")
            print("="*80)

        # ── Module 0 : Normalisation du texte d'entrée ─────────────────────
        normalized = normalize_input_text(text)
        if verbose and normalized != text:
            print(f"[Module 0] Texte normalisé : '{text}' → '{normalized}'")
        text = normalized
        # ───────────────────────────────────────────────────────────────────

        # COUCHE 1 : spaCy NER + EntityRuler
        doc = self.nlp(text)
        raw_entities = self._layer1_spacy_ner(doc, verbose)
        
        # COUCHE 3 : Heuristiques PROPN
        propn_entities = self._layer3_propn_heuristics(doc, verbose)
        
        # Fusion des entités
        all_entities = raw_entities + propn_entities

        # ── Module 0++ : Coordination splitting (cross-layer) ───────────────
        # Splits "X and Y" / "X et Y" / "X, Y" TOPIC/ORG entities that span
        # what should be two distinct entities.  Applied here (post-fusion) so
        # that both Layer-1 and Layer-3 entities are covered.
        all_entities = self._split_coordinated_entities(all_entities, verbose)
        # ────────────────────────────────────────────────────────────────────
        
        # COUCHE 4 : Normalisation
        normalized_entities = self._layer4_normalize(all_entities, verbose)
        
        # COUCHE 5 : Déduplication
        deduplicated_entities = self._layer5_deduplicate(normalized_entities, verbose)
        
        # COUCHE 6 : Filtrage par confiance
        filtered_entities = self._layer6_filter_confidence(deduplicated_entities, verbose)
        
        # COUCHE 7 : Validation ontologique (si activée)
        if self.enable_validation and self.ontology_graph:
            validated_entities = self._layer7_validate_ontology(filtered_entities, verbose)
        else:
            validated_entities = filtered_entities
        
        if verbose:
            print("="*80)
            print(f"✅ RÉSULTAT FINAL : {len(validated_entities)} entités extraites")
            print("="*80)
        
        return validated_entities
    
    def _layer1_spacy_ner(self, doc: Doc, verbose: bool) -> List[Tuple[str, str, float]]:
        """
        COUCHE 1 : Extraction spaCy NER + EntityRuler.
        
        Args:
            doc: Document spaCy traité
            verbose: Affiche logs
            
        Returns:
            Liste (entité, type, confiance)
        """
        if verbose:
            print("\n[COUCHE 1] spaCy NER + EntityRuler")
            print("-" * 80)
        
        entities = []
        type_counts = {}
        
        for ent in doc.ents:
            # Récupération du score de confiance (heuristique si non disponible)
            confidence = self._get_entity_confidence(ent)
            label = ent.label_

            # ── Tech-term override ────────────────────────────────────────────
            # The French spaCy model sometimes tags English/mixed tech terms as
            # PER, MISC, X, LOC, or even ORG. Reclassify them as TOPIC when they
            # match known keywords or short acronyms.
            ent_lower = ent.text.lower()
            first_word_lower = ent_lower.split()[0].rstrip("'") if ent_lower.split() else ""
            _is_real_org = first_word_lower in self._ORG_PREFIX_LOWER

            if label in ("PER", "MISC", "X", "LOC"):
                # Reclassify as ORG when the entity starts with an org-keyword
                # (e.g. spaCy tags "INRIA Saclay" as MISC)
                if _is_real_org:
                    label = "ORG"
                    confidence = max(confidence, 0.85)
                elif any(kw in ent_lower for kw in self.TECH_CONCEPT_KEYWORDS):
                    label = "TOPIC"
                    confidence = max(confidence, 0.80)
                elif ent.text in self._SHORT_TOPIC_ACRONYMS:
                    label = "TOPIC"
                    confidence = max(confidence, 0.83)
            elif label == "ORG" and not _is_real_org:
                # ORG entities that don't start with an org-prefix word may be
                # mislabelled tech/academic subjects (e.g. "Formal Verification")
                if any(kw in ent_lower for kw in self.TECH_CONCEPT_KEYWORDS):
                    label = "TOPIC"
                    confidence = max(confidence, 0.78)
                elif ent.text in self._SHORT_TOPIC_ACRONYMS:
                    label = "TOPIC"
                    confidence = max(confidence, 0.83)
            # ─────────────────────────────────────────────────────────────────

            entities.append((ent.text, label, confidence))
            
            # Comptage par type
            type_counts[ent.label_] = type_counts.get(ent.label_, 0) + 1
            
            if verbose:
                source = "🎯 EntityRuler" if ent.label_ in ["TOPIC", "DOCUMENT"] else "🧠 spaCy"
                print(f"  {source} : '{ent.text}' → {ent.label_} (conf: {confidence:.2f})")
        
        if verbose:
            print(f"\n  📊 Statistiques Couche 1 : {len(entities)} entités détectées")
            for ent_type, count in sorted(type_counts.items()):
                print(f"     • {ent_type}: {count}")
        
        return entities
    
    def _layer3_propn_heuristics(self, doc: Doc, verbose: bool) -> List[Tuple[str, str, float]]:
        """
        COUCHE 3 : Heuristiques linguistiques PROPN (améliorée).

        Amélioration v2 :
        - Les connecteurs "-", "de", "d'", "of" ne brisent plus une séquence
          → "Université Paris-Saclay" reste une entité unique (ORG)
        - Chaque séquence est typée via _classify_compound_entity()
          au lieu d'être systématiquement "PER"
        - Regex complémentaires : titres humains + paires Prénom Nom

        Args:
            doc: Document spaCy traité
            verbose: Affiche logs

        Returns:
            Liste (entité, type, confiance)
        """
        if verbose:
            print("\n[COUCHE 3] Heuristiques PROPN")
            print("-" * 80)

        # ── 3a. Multi-word PROPN grouping ───────────────────────────────────
        # Tokens that are transparent inside a compound entity name.
        # A connector is absorbed only when the token immediately after it
        # is a PROPN or NOUN (bridging pattern: PROPN ADP/DET PROPN).
        _CONNECTORS = frozenset(["de", "d'", "du", "des", "of", "for", "la", "le", "-", "–", "—"])

        entities: List[Tuple[str, str, float]] = []
        propn_tokens_found = 0

        def _is_content(tok_: "Token") -> bool:
            """True when a token can extend a compound entity (PROPN or bridgeable NOUN)."""
            return tok_.pos_ in ("PROPN", "NOUN")

        # Iterate token-by-token; accumulate a "window" of tokens that
        # form a single compound entity.
        # Bridging rule:
        #   • consecutive PROPN/NOUN always absorb
        #   • an ADP/DET connector token is absorbed when the *next non-space*
        #     token is a PROPN (strict) to avoid over-generating
        i = 0
        tokens = list(doc)
        n = len(tokens)

        while i < n:
            tok = tokens[i]
            if tok.pos_ != "PROPN":
                i += 1
                continue

            propn_tokens_found += 1
            window: List[str] = [tok.text]
            propn_count = 1   # count of PROPN tokens (not connectors/NOUNs)
            j = i + 1

            while j < n:
                t = tokens[j]
                t_lower = t.text.lower().rstrip("'")

                if t.pos_ == "PROPN":
                    window.append(t.text)
                    propn_tokens_found += 1
                    propn_count += 1
                    j += 1
                elif t.pos_ == "NOUN" and j + 1 < n and tokens[j + 1].pos_ in ("PROPN", "NOUN"):
                    # Bridge: NOUN between two content tokens (e.g. "MIT Media Lab",
                    # "Department of Computer Science" where Science is NOUN after PROPN)
                    window.append(t.text)
                    j += 1
                elif t.pos_ == "NOUN" and j + 1 == n:
                    # Trailing NOUN at end of sentence — absorb only when window already
                    # has multiple PROPN tokens (avoids false positives)
                    if propn_count >= 2:
                        window.append(t.text)
                    j += 1
                    break
                elif t.pos_ == "NOUN" and window and tokens[j - 1].pos_ == "PROPN":
                    # Trailing NOUN directly after a PROPN (e.g. "...of Computer Science.")
                    # peek: if next is PUNCT/end, absorb
                    nxt = tokens[j + 1] if j + 1 < n else None
                    if nxt is None or nxt.pos_ in ("PUNCT", "SPACE"):
                        window.append(t.text)
                        j += 1
                    break
                elif t_lower in _CONNECTORS and j + 1 < n and tokens[j + 1].pos_ == "PROPN":
                    # ADP/DET connector immediately before a PROPN
                    window.append(t.text)
                    j += 1
                else:
                    break

            i = j  # advance past the consumed window

            # Require at least 2 PROPN tokens to avoid single-token noise
            if propn_count < 2:
                continue

            entity_text = " ".join(window)

            # Collapse spaces around hyphens ("Paris - Saclay" → "Paris-Saclay")
            entity_text = re.sub(r'\s*-\s*', '-', entity_text)

            if self._already_detected_by_spacy(entity_text, doc):
                continue

            etype, conf = self._classify_compound_entity(entity_text)
            entities.append((entity_text, etype, conf))
            if verbose:
                print(f"  🔍 PROPN multi-mot : '{entity_text}' → {etype} (conf: {conf:.2f})")

        # ── 3a2. Institutional-keyword ORG detection ───────────────────────
        # Catches spans like "Université de Versailles", "Centre de Recherche en
        # Informatique", "University of Oxford", "Department of Computer Science".
        #
        # Pattern: ORG_KEYWORD  (ADP|DET)*  (PROPN|NOUN|ADJ)+
        #          optionally bridged by connectors between content tokens.
        #
        # Strategy: scan for tokens whose lowercase text is in _ORG_KEYWORDS;
        # from there greedily extend the span through connectors and content
        # words.  Stop at VERB, PUNCT, end of sentence.

        _ORG_KEYWORDS_L3 = frozenset([
            "université", "universités", "university", "universities",
            "institute", "institut", "instituts",
            "laboratoire", "laboratoires", "laboratory", "lab",
            "department", "département", "departments",
            "centre", "center", "centers",
            "école", "ecole", "school", "college",
            "inria", "cnrs",
            "fondation", "foundation",
            "académie", "academy",
        ])
        # Prepositions / determiners that can bridge inside an org name
        _ORG_CONNECTORS = frozenset([
            "de", "d'", "du", "des", "d",
            "of", "for", "at",
            "la", "le", "les",
            "en", "et", "and",
            "-",
        ])
        # POS tags that terminate an org span
        _STOP_POS = frozenset(["VERB", "AUX", "PUNCT", "SCONJ", "CCONJ"])

        already_in_doc = {ent.text for ent in doc.ents}
        already_in_entities = {e[0] for e in entities}

        i_org = 0
        while i_org < n:
            tok = tokens[i_org]
            if tok.lower_.rstrip("'") not in _ORG_KEYWORDS_L3:
                i_org += 1
                continue

            # Start of an institutional name — collect the span
            window_org: List[str] = [tok.text]
            j_org = i_org + 1
            content_count = 0  # PROPN/NOUN/ADJ tokens added after the keyword

            # Content POS tags inside an org span
            # PRON is included because spaCy sometimes tags place names as PRON
            # (e.g. "Bordeaux" in "Centre de Recherche … de Bordeaux")
            _ORG_CONTENT_POS = frozenset(["PROPN", "NOUN", "ADJ", "PRON"])

            while j_org < n:
                t = tokens[j_org]
                t_lower = t.lower_.rstrip("'")

                if t.pos_ in _ORG_CONTENT_POS:
                    # For NOUN/ADJ, require title-case (avoids absorbing lowercase
                    # verbs that spaCy mislabels as NOUN, e.g. "recrute")
                    if t.pos_ in ("NOUN", "ADJ") and t.text[0].islower():
                        break
                    window_org.append(t.text)
                    content_count += 1
                    j_org += 1
                elif t_lower in _ORG_CONNECTORS:
                    # Absorb connector only when a content word follows
                    peek = j_org + 1
                    if peek < n and tokens[peek].pos_ in _ORG_CONTENT_POS:
                        window_org.append(t.text)
                        j_org += 1
                    else:
                        break
                elif t.pos_ in _STOP_POS:
                    break
                else:
                    break

            i_org = j_org  # advance past consumed window

            # Need at least one content token after the keyword
            if content_count < 1:
                continue

            entity_text = " ".join(window_org)
            # Normalise spaces around hyphens
            entity_text = re.sub(r'\s*-\s*', '-', entity_text)
            # Collapse spaces before apostrophes: "d' Informatique" → "d'Informatique"
            entity_text = re.sub(r"(\w)'\s+", r"\1'", entity_text)
            entity_text = re.sub(r"\s+'\s*", "'", entity_text)

            # Skip if spaCy already tagged this span
            if entity_text in already_in_doc or entity_text in already_in_entities:
                continue
            # Skip substrings of already-found entities
            if any(entity_text in e for e in already_in_entities):
                continue

            entities.append((entity_text, "ORG", 0.85))
            already_in_entities.add(entity_text)
            if verbose:
                print(f"  🏛️  ORG-keyword : '{entity_text}' → ORG (conf: 0.85)")

        # refresh sets for subsequent sections
        already_in_entities = {e[0] for e in entities}

        # ── 3b. Regex: titled human names ──────────────────────────────────
        already_in_doc = {ent.text for ent in doc.ents}
        already_in_entities = {e[0] for e in entities}

        title_re = re.compile(
            r'\b(?:Dr\.?|Prof\.?|Professeur|Docteur|Mr\.?|Mrs\.?|Mme\.?|Monsieur|Madame)\s+'
            r'([A-ZÀÂÉÈÊÙÛÎÔŒÆÇ][a-zàâéèêùûîôœæç]+'
            r'(?:\s+[A-ZÀÂÉÈÊÙÛÎÔŒÆÇ][a-zàâéèêùûîôœæç]+)*)'
        )
        for m in title_re.finditer(doc.text):
            full_match = m.group(0).strip()
            if full_match not in already_in_doc and full_match not in already_in_entities:
                entities.append((full_match, "PER", 0.88))
                already_in_entities.add(full_match)
                if verbose:
                    print(f"  👤 Regex-titre : '{full_match}' → PER (conf: 0.88)")

        # ── 3c. Regex: bare Firstname Lastname ─────────────────────────────
        _ORG_WORDS = frozenset([
            "université", "university", "institute", "institut", "school",
            "école", "college", "laboratory", "laboratoire", "department",
            "département", "center", "centre", "research", "national",
            "inria", "cnrs", "mit", "stanford",
        ])
        bare_re = re.compile(
            r'(?<!\w)([A-ZÀÂÉÈÊÙÛÎÔŒÆÇ][a-zàâéèêùûîôœæç]{1,})'
            r'\s+([A-ZÀÂÉÈÊÙÛÎÔŒÆÇ][a-zàâéèêùûîôœæç]{1,})(?!\w)'
        )
        for m in bare_re.finditer(doc.text):
            first, last = m.group(1), m.group(2)
            full = f"{first} {last}"
            tl = full.lower()
            if any(kw in tl for kw in self.TECH_CONCEPT_KEYWORDS):
                continue
            if any(w in tl for w in _ORG_WORDS):
                continue
            if full in already_in_doc or full in already_in_entities:
                continue
            entities.append((full, "PER", 0.78))
            already_in_entities.add(full)
            if verbose:
                print(f"  👤 Regex-nom : '{full}' → PER (conf: 0.78)")

        # ── 3d. Teaching-verb TOPIC detection ─────────────────────────────
        # If a teaching/research verb is followed by a noun/propn, treat it
        # as a potential TOPIC (e.g. "enseigne Data", "teach Algebra").
        _TEACHING_VERBS = frozenset([
            "enseigne", "enseigner", "enseignons", "enseignez",
            "teach", "teaches", "teaching",
            "étudie", "étudier", "étudions",
            "study", "studies", "studying",
            "recherche", "rechercher",
            "research", "researches",
            "présente", "présenter",
            "present", "presents",
            "cours",  # "donne un cours de X"
        ])
        already_in_doc2 = {ent.text.lower() for ent in doc.ents}
        already_in_entities2 = {e[0].lower() for e in entities}

        for idx, tok in enumerate(doc):
            if tok.lower_ not in _TEACHING_VERBS:
                continue
            # Look ahead: skip determiners/prepositions, grab the next noun chunk
            j2 = idx + 1
            # skip one optional ADP/DET token ("enseigne le", "teaches the")
            if j2 < n and tokens[j2].pos_ in ("ADP", "DET"):
                j2 += 1
            if j2 >= n:
                continue
            candidate_tok = tokens[j2]
            if candidate_tok.pos_ not in ("NOUN", "PROPN"):
                continue

            # Collect consecutive NOUN/PROPN/ADJ tokens as the topic span
            span_tokens: List[str] = [candidate_tok.text]
            k = j2 + 1
            while k < n and tokens[k].pos_ in ("NOUN", "PROPN", "ADJ"):
                span_tokens.append(tokens[k].text)
                k += 1
            topic_text = " ".join(span_tokens)
            topic_lower = topic_text.lower()

            # Avoid re-adding already-known entities
            if topic_lower in already_in_doc2 or topic_lower in already_in_entities2:
                continue
            # Skip single PROPN that looks like a personal name (not a tech/org keyword)
            if candidate_tok.pos_ == "PROPN" and len(span_tokens) == 1:
                if candidate_tok.lower_ not in self._ORG_PREFIX_LOWER:
                    if not any(kw in topic_lower for kw in self.TECH_CONCEPT_KEYWORDS):
                        if topic_text not in self._SHORT_TOPIC_ACRONYMS:
                            continue
            entities.append((topic_text, "TOPIC", 0.72))
            already_in_entities2.add(topic_lower)
            if verbose:
                print(f"  📚 Verbe-enseignement : '{tok.text}' → '{topic_text}' = TOPIC (conf: 0.72)")

        # ── 3e. POS-pattern topic detection (noun chunks near teaching verbs) ──
        # Catches topics that appear as noun chunks in the vicinity of a teaching
        # or research verb even if not immediately following it.
        # Examples: "Bioinformatique" (single NOUN), "Algèbre linéaire" (NOUN+ADJ),
        #           "Formal Verification" (ADJ+NOUN), "Quantum Error Correction".
        _TEACHING_VERBS_SET = frozenset([
            "enseigne", "enseigner", "enseignons", "enseignez",
            "teach", "teaches", "teaching",
            "étudie", "étudier", "étudions",
            "study", "studies", "studying",
            "recherche", "rechercher",
            "research", "researches",
            "présente", "présenter",
            "present", "presents",
            "cours",
            "couvre", "cover", "covers",
            "aborde", "aborder",
            "introduit", "introduce", "introduces",
            "travaille", "work", "works",
            "implémente", "implement", "implements",
        ])
        # Pre-compute set of teaching-verb token indices for fast window checks
        teaching_verb_indices: Set[int] = {
            idx2 for idx2, tok2 in enumerate(tokens)
            if tok2.lower_ in _TEACHING_VERBS_SET
        }
        _VERB_WINDOW = 6  # tokens left/right to count as "near a teaching verb"

        # Common French/English function words and generic nouns that should
        # never become TOPIC on their own.
        _CHUNK_STOPWORDS: frozenset = frozenset([
            # Generic academic/meta nouns
            "cours", "cours de", "le cours", "un cours",
            "matière", "la matière", "domaine", "le domaine",
            "sujet", "le sujet", "thème", "le thème",
            "travail", "le travail", "projet", "le projet",
            "étude", "l'étude", "recherche", "la recherche", "analyse",
            # Determiners / pronouns standing alone
            "il", "elle", "je", "nous", "vous", "ils", "elles",
            "ce", "cet", "cette", "ces",
            "le", "la", "les", "l", "un", "une", "des",
            "son", "sa", "ses", "mon", "ma", "mes",
            # English generic
            "year", "author", "paper", "topic", "field", "area",
            "course", "the course", "a course",
            "subject", "the subject",
        ])
        # Roots (lemmas) whose chunks should not become TOPIC
        _CHUNK_ROOT_STOP: frozenset = frozenset([
            "cours", "matière", "domaine", "sujet", "thème",
            "travail", "projet", "étude", "recherche", "analyse",
            "course", "topic", "field",
        ])

        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.strip()
            chunk_lower = chunk_text.lower()

            # Skip very short/trivial chunks
            if len(chunk_text) < 3:
                continue
            # Skip degenerate chunks that span nearly the whole sentence
            if len(chunk) > 8 or len(chunk_text) > 60:
                continue
            # Skip function/stop words (exact match on full chunk text)
            if chunk_lower in _CHUNK_STOPWORDS:
                continue
            # Skip if chunk root is a generic meta-noun
            if chunk.root.lower_ in _CHUNK_ROOT_STOP:
                continue
            # Skip if already known
            if chunk_lower in already_in_doc2 or chunk_lower in already_in_entities2:
                continue
            # Skip pure personal names (PER) and org names
            if chunk.root.lower_ in self._ORG_PREFIX_LOWER:
                continue
            # Heuristic: skip chunks whose root is likely a name
            # (single lowercase root that starts with uppercase in original
            #  and is NOT a tech keyword → defer to PROPN section)
            root_lower = chunk.root.lower_
            is_tech = (
                any(kw in chunk_lower for kw in self.TECH_CONCEPT_KEYWORDS)
                or chunk_text in self._SHORT_TOPIC_ACRONYMS
            )
            # Only accept if near a teaching verb OR clearly a known tech term
            near_verb = any(
                abs(vi - chunk.start) <= _VERB_WINDOW
                for vi in teaching_verb_indices
            )
            if not near_verb and not is_tech:
                continue

            # Check POS composition: must contain at least one NOUN or ADJ
            pos_tags = [t.pos_ for t in chunk]
            if not any(p in ("NOUN", "ADJ") for p in pos_tags):
                continue

            # Skip chunks that are just a single PROPN (already handled by 3a)
            if len(chunk) == 1 and chunk[0].pos_ == "PROPN":
                continue

            entities.append((chunk_text, "TOPIC", 0.70))
            already_in_entities2.add(chunk_lower)
            if verbose:
                print(f"  🔬 Chunk-TOPIC : '{chunk_text}' → TOPIC (conf: 0.70)")

        # ── 3f. Coordination splitting ──────────────────────────────────────
        # "Machine Learning and Knowledge Graphs" → two separate TOPIC entities.
        # "NLP, ML et Deep Learning" → three separate TOPIC entities.
        # Matches: " and ", " et ", ", and ", ", et ", ", " (list separator)
        _COORD_RE = re.compile(
            r'(?:\s*,\s*(?:and|et)\s*|\s+(?:and|et)\s+|\s*,\s+)',
            re.IGNORECASE
        )
        # Entity types eligible for coordination splitting
        _SPLIT_TYPES = {"TOPIC", "ORG", "MISC", "PER"}

        split_entities: List[Tuple[str, str, float]] = []
        kept_entities: List[Tuple[str, str, float]] = []

        for ent_text, etype, conf in entities:
            # Split entities whose text contains coordination AND have multiple words
            if etype in _SPLIT_TYPES and _COORD_RE.search(ent_text):
                raw_parts = [p.strip().strip(',').strip() for p in _COORD_RE.split(ent_text)]
                parts = [p for p in raw_parts if p and len(p) >= 2]
                if len(parts) >= 2:
                    # Determine the best type for the split parts
                    # If the original is ORG but parts look like topics, reclassify
                    split_type = etype
                    if etype in ("ORG", "MISC"):
                        # Check if parts look like tech topics
                        if any(
                            any(kw in p.lower() for kw in self.TECH_CONCEPT_KEYWORDS)
                            or p in self._SHORT_TOPIC_ACRONYMS
                            for p in parts
                        ):
                            split_type = "TOPIC"
                    for part in parts:
                        part_lower = part.lower()
                        if part_lower not in already_in_entities2:
                            split_entities.append((part, split_type, conf))
                            already_in_entities2.add(part_lower)
                            if verbose:
                                print(f"  ✂️  Coordination split : '{part}' → {split_type} (conf: {conf:.2f})")
                    continue  # don't keep the original fused entity
            kept_entities.append((ent_text, etype, conf))

        entities = kept_entities + split_entities

        if verbose:
            print(f"\n  📊 Statistiques Couche 3 : {propn_tokens_found} tokens PROPN analysés")
            if entities:
                print(f"     • {len(entities)} nouvelle(s) entité(s) détectée(s)")
            else:
                print(f"     • Aucune nouvelle entité (toutes déjà détectées)")

        return entities

    # ── helpers ────────────────────────────────────────────────────────────

    def _split_coordinated_entities(
        self,
        entities: List[Tuple[str, str, float]],
        verbose: bool,
    ) -> List[Tuple[str, str, float]]:
        """
        Coordination splitting (section 3f, applied post-fusion).

        Splits entity texts like:
          "Machine Learning and Knowledge Graphs"  → ML  +  KG
          "NLP, ML et Deep Learning"               → NLP + ML + Deep Learning

        Eligible types: TOPIC, ORG, MISC, PER.
        ORG/MISC parts that look like tech topics are reclassified to TOPIC.
        """
        _COORD_RE = re.compile(
            r'(?:\s*,\s*(?:and|et)\s*|\s+(?:and|et)\s+|\s*,\s+)',
            re.IGNORECASE
        )
        _SPLIT_TYPES = {"TOPIC", "ORG", "MISC"}

        seen: Set[str] = set()
        result: List[Tuple[str, str, float]] = []

        for ent_text, etype, conf in entities:
            if etype not in _SPLIT_TYPES or not _COORD_RE.search(ent_text):
                key = ent_text.lower()
                if key not in seen:
                    seen.add(key)
                    result.append((ent_text, etype, conf))
                continue

            raw_parts = [p.strip().strip(',').strip()
                         for p in _COORD_RE.split(ent_text)]
            parts = [p for p in raw_parts if p and len(p) >= 2]

            if len(parts) < 2:
                # Can't split sensibly — keep original
                key = ent_text.lower()
                if key not in seen:
                    seen.add(key)
                    result.append((ent_text, etype, conf))
                continue

            # Decide label for split parts
            split_type = etype
            if etype in ("ORG", "MISC"):
                if any(
                    any(kw in p.lower() for kw in self.TECH_CONCEPT_KEYWORDS)
                    or p in self._SHORT_TOPIC_ACRONYMS
                    for p in parts
                ):
                    split_type = "TOPIC"

            for part in parts:
                part_lower = part.lower()
                if part_lower not in seen:
                    seen.add(part_lower)
                    result.append((part, split_type, conf))
                    if verbose:
                        print(f"  ✂️  Coord-split : '{ent_text}' → '{part}' [{split_type}]")

        return result


    _ORG_PREFIX_LOWER = frozenset([
        "université", "university", "universités",
        "institute", "institut", "école", "ecole",
        "laboratory", "laboratoire", "lab",
        "department", "département",
        "center", "centre",
        "inria", "cnrs", "mit",
    ])

    # Short all-caps acronyms that should always be TOPIC (Task 3)
    _SHORT_TOPIC_ACRONYMS: frozenset = frozenset([
        "AI", "ML", "DL", "NLP", "KG", "CV", "GL",
        "RDF", "OWL", "RDFS", "SPARQL",  # also tech concepts
    ])

    def _classify_compound_entity(self, entity_text: str) -> Tuple[str, float]:
        """
        Determine the entity type and confidence for a multi-word compound.

        Rules (in priority order):
        1. First token is an ORG keyword   → ORG   (0.85)
        2. Any token is a short TOPIC acr. → TOPIC (0.83)  [Task 3]
        3. Text contains a TECH keyword    → TOPIC (0.82)
        4. Text contains a HUMAN indicator → PER   (0.88)
        5. Default                          → PER   (0.75)
        """
        text_lower = entity_text.lower()
        first_word = text_lower.split()[0].rstrip("'")

        if first_word in self._ORG_PREFIX_LOWER:
            return "ORG", 0.85

        # Any token that is a known short acronym → TOPIC
        for tok_str in entity_text.split():
            if tok_str in self._SHORT_TOPIC_ACRONYMS:
                return "TOPIC", 0.83

        for kw in self.TECH_CONCEPT_KEYWORDS:
            if kw in text_lower:
                return "TOPIC", 0.82

        for indicator in self.HUMAN_NAME_INDICATORS:
            if re.search(r'\b' + re.escape(indicator) + r'\b', text_lower):
                return "PER", 0.88

        return "PER", 0.75

    def _already_detected_by_spacy(self, entity_text: str, doc: Doc) -> bool:
        """Vérifie si l'entité a déjà été détectée par spaCy/EntityRuler."""
        for ent in doc.ents:
            if ent.text == entity_text:
                return True
        return False

    def _layer4_normalize(self, entities: List[Tuple[str, str, float]], verbose: bool) -> List[Tuple[str, str, float]]:
        """
        COUCHE 4 : Normalisation des entités.
        
        Transformations :
        - Suppression espaces superflus (trim)
        - Standardisation casse (Title Case pour PER/ORG)
        - Suppression articles (le, la, l', les)
        
        Args:
            entities: Liste brute (entité, type, confiance)
            verbose: Affiche logs
            
        Returns:
            Liste normalisée
        """
        if verbose:
            print("\n[COUCHE 4] Normalisation")
            print("-" * 80)
        
        normalized = []
        normalized_count = 0
        
        for entity_text, entity_type, confidence in entities:
            original = entity_text
            
            # Suppression espaces superflus
            clean_text = entity_text.strip()
            clean_text = re.sub(r'\s+', ' ', clean_text)  # Espaces multiples → 1 espace
            
            # Suppression articles français (seulement si l'entité n'est pas une ORG connue)
            # On ne supprime PAS 'de/du/des' car ils font partie du nom (Université de Versailles)
            if entity_type not in ["ORG"]:
                clean_text = re.sub(r"^(le|la|l'|les|un|une)\s+", "", clean_text, flags=re.IGNORECASE)

            # Standardisation casse (Title Case intelligent pour PER/ORG)
            # Les connecteurs de/d'/du/des/of/en/le/la/les restent en minuscule
            # Les mots après un tiret (Paris-Saclay) sont aussi capitalisés
            if entity_type in ["PER", "ORG"]:
                _LOWERCASE_CONNECTORS = frozenset([
                    "de", "d'", "du", "des", "of", "for", "en",
                    "le", "la", "les", "et", "and",
                ])
                words = clean_text.split()
                cased = [
                    w if (i > 0 and w.lower().rstrip("'") in _LOWERCASE_CONNECTORS)
                    else w.capitalize()
                    for i, w in enumerate(words)
                ]
                # Capitalize the part after a hyphen (Paris-Saclay, Jean-Pierre)
                clean_text = re.sub(
                    r'(-[a-zàâéèêùûîôœæç])',
                    lambda m: m.group(0).upper(),
                    " ".join(cased)
                )
            
            normalized.append((clean_text, entity_type, confidence))
            
            if verbose and clean_text != original:
                normalized_count += 1
                print(f"  🔧 Normalisé : '{original}' → '{clean_text}'")
        
        if verbose:
            print(f"\n  📊 Statistiques Couche 4 : {normalized_count}/{len(entities)} entités normalisées")
        
        return normalized
    
    def _layer5_deduplicate(self, entities: List[Tuple[str, str, float]], verbose: bool) -> List[Tuple[str, str, float]]:
        """
        COUCHE 5 : Déduplication avec canonicalisation.
        
        Stratégie :
        - Normalisation canonique (minuscules, sans accents)
        - Regroupement par forme canonique
        - Conservation de la variante avec la meilleure confiance
        - ⚡ NOUVEAU : Élimination des sous-entités (ex: "Paris-Saclay" dans "Université Paris-Saclay")
        
        Args:
            entities: Liste normalisée (entité, type, confiance)
            verbose: Affiche logs
            
        Returns:
            Liste dédupliquée
        """
        if verbose:
            print("\n[COUCHE 5] Déduplication")
            print("-" * 80)
        
        canonical_map: Dict[str, Tuple[str, str, float]] = {}
        
        for entity_text, entity_type, confidence in entities:
            # Forme canonique : minuscules + sans accents
            canonical = self._canonicalize(entity_text)
            
            # Si déjà présent, garder la meilleure confiance
            if canonical in canonical_map:
                existing_text, existing_type, existing_conf = canonical_map[canonical]
                if confidence > existing_conf:
                    canonical_map[canonical] = (entity_text, entity_type, confidence)
                    if verbose:
                        print(f"  ✓ Doublon remplacé : '{existing_text}' → '{entity_text}'")
            else:
                canonical_map[canonical] = (entity_text, entity_type, confidence)
        
        deduplicated = list(canonical_map.values())
        initial_count = len(deduplicated)
        
        # ⚡ NOUVEAU FILTRE : Éliminer les sous-entités
        # Ex: Si "Université Paris-Saclay" existe, supprimer "Paris-Saclay"
        filtered = []
        removed_substrings = []
        
        for entity_text, entity_type, confidence in deduplicated:
            is_substring = False
            
            # Vérifier si cette entité est contenue dans une autre plus longue
            for other_text, other_type, _ in deduplicated:
                if entity_text != other_text and entity_text in other_text:
                    is_substring = True
                    removed_substrings.append(f"'{entity_text}' (contenu dans '{other_text}')")
                    break
            
            if not is_substring:
                filtered.append((entity_text, entity_type, confidence))
        
        duplicates_removed = len(entities) - initial_count
        substrings_removed = initial_count - len(filtered)
        
        if verbose:
            print(f"\n  📊 Statistiques Couche 5 :")
            print(f"     • Doublons éliminés : {duplicates_removed}")
            print(f"     • Sous-entités éliminées : {substrings_removed}")
            if removed_substrings:
                print(f"\n  🗑️  Sous-entités supprimées :")
                for removed in removed_substrings:
                    print(f"     ➜ {removed}")
        
        return filtered
    
    def _canonicalize(self, text: str) -> str:
        """
        Crée une forme canonique pour la déduplication.
        
        Transformations :
        - Minuscules
        - Suppression accents
        - Suppression articles
        
        Args:
            text: Texte à canonicaliser
            
        Returns:
            Forme canonique
        """
        # Minuscules
        canonical = text.lower()
        
        # Suppression accents
        canonical = ''.join(
            c for c in unicodedata.normalize('NFD', canonical)
            if unicodedata.category(c) != 'Mn'
        )
        
        # Suppression articles français
        canonical = re.sub(r"\b(le|la|l'|les|un|une|des|du|de)\b", "", canonical)
        canonical = re.sub(r'\s+', ' ', canonical).strip()
        
        return canonical
    
    def _layer6_filter_confidence(self, entities: List[Tuple[str, str, float]], verbose: bool) -> List[Tuple[str, str, float]]:
        """
        COUCHE 6 : Filtrage par seuil de confiance.
        
        Élimine les entités avec une confiance < threshold.
        
        Args:
            entities: Liste dédupliquée (entité, type, confiance)
            verbose: Affiche logs
            
        Returns:
            Liste filtrée
        """
        if verbose:
            print(f"\n[COUCHE 6] Filtrage Confiance (seuil: {self.confidence_threshold})")
            print("-" * 80)
        
        filtered = [
            (text, etype, conf) 
            for text, etype, conf in entities 
            if conf >= self.confidence_threshold
        ]
        
        rejected_count = len(entities) - len(filtered)
        
        if verbose:
            print(f"\n  📊 Statistiques Couche 6 :")
            print(f"     • Entités validées : {len(filtered)}")
            print(f"     • Entités rejetées : {rejected_count}")
            
            if rejected_count > 0:
                print(f"\n  ⚠️  Entités rejetées (confiance < {self.confidence_threshold}) :")
                for entity_text, entity_type, confidence in entities:
                    if confidence < self.confidence_threshold:
                        print(f"     ➜ '{entity_text}' ({entity_type}, conf={confidence:.2f})")
        
        return filtered
    
    def _layer7_validate_ontology(self, entities: List[Tuple[str, str, float]], verbose: bool) -> List[Tuple[str, str, float]]:
        """
        COUCHE 7 : Validation types ontologiques.
        
        Vérifie que le type NER correspond à une classe OWL déclarée.
        
        Args:
            entities: Liste filtrée (entité, type, confiance)
            verbose: Affiche logs
            
        Returns:
            Liste validée ontologiquement
        """
        if verbose:
            print("\n[COUCHE 7] Validation Ontologique")
            print("-" * 80)
        
        # Mapping NER → Classes OWL
        type_to_owl = {
            "PER": FOAF.Person,
            "ORG": SCHEMA.Organization,
            "LOC": SCHEMA.Place,
            "TOPIC": EX.Document,
            "DOC": EX.Document,
        }
        
        validated = []
        validation_results = {"accepted": [], "rejected": []}
        
        for entity_text, entity_type, confidence in entities:
            owl_class = type_to_owl.get(entity_type)
            
            if owl_class:
                # Vérifier que la classe OWL est déclarée dans l'ontologie
                if (owl_class, RDF.type, OWL.Class) in self.ontology_graph:
                    validated.append((entity_text, entity_type, confidence))
                    validation_results["accepted"].append((entity_text, entity_type))
                    if verbose:
                        owl_name = str(owl_class).split('#')[-1].split('/')[-1]
                        print(f"  ✅ '{entity_text}' → {entity_type} (classe {owl_name} validée)")
                else:
                    validation_results["rejected"].append((entity_text, entity_type))
                    if verbose:
                        owl_name = str(owl_class).split('#')[-1].split('/')[-1]
                        print(f"  ❌ '{entity_text}' → {entity_type} (classe {owl_name} non déclarée)")
            else:
                # Type NER non mappé → ignorer
                validation_results["rejected"].append((entity_text, entity_type))
                if verbose:
                    print(f"  ❌ Type NER non mappé : {entity_type}")
        
        if verbose:
            print(f"\n  📊 Statistiques Couche 7 :")
            print(f"     • Entités validées : {len(validation_results['accepted'])}")
            print(f"     • Entités rejetées : {len(validation_results['rejected'])}")
        
        return validated
    
    def _get_entity_confidence(self, ent) -> float:
        """
        Récupère le score de confiance d'une entité spaCy.
        
        Note : spaCy fr_core_news_sm ne fournit pas de scores de confiance
        par défaut. On utilise une heuristique basée sur la longueur.
        
        Heuristique :
        - Longueur ≥ 2 tokens : 0.90
        - Longueur = 1 token + POS=PROPN : 0.85
        - Sinon : 0.70
        
        Args:
            ent: Entité spaCy (Span)
            
        Returns:
            Score de confiance (0.0 à 1.0)
        """
        # Si spaCy fournit un score (modèles custom), l'utiliser
        if hasattr(ent, '_') and hasattr(ent._, 'score'):
            return ent._.score
        
        # Heuristique basée sur la structure
        token_count = len(ent)
        
        if token_count >= 2:
            return 0.90  # Entité composée → haute confiance
        elif token_count == 1 and ent[0].pos_ == "PROPN":
            return 0.85  # Nom propre unique → confiance moyenne-haute
        else:
            return 0.70  # Entité simple → confiance moyenne


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def normalize_uri_fragment(text: str) -> str:
    """
    Normalise un texte pour créer un fragment d'URI valide.
    
    Transformations :
    - Minuscules
    - Suppression accents
    - Espaces → underscores
    - Caractères spéciaux → supprimés
    
    Args:
        text: Texte à normaliser
        
    Returns:
        Fragment URI valide (snake_case)
        
    Exemple:
        >>> normalize_uri_fragment("Zoubida Kedad")
        'zoubida_kedad'
    """
    # Minuscules
    normalized = text.lower()
    
    # Suppression accents
    normalized = ''.join(
        c for c in unicodedata.normalize('NFD', normalized)
        if unicodedata.category(c) != 'Mn'
    )
    
    # Espaces → underscores
    normalized = normalized.replace(' ', '_')
    
    # Suppression caractères non-alphanumériques (sauf underscore)
    normalized = re.sub(r'[^a-z0-9_]', '', normalized)
    
    return normalized


# ============================================================================
# TESTS UNITAIRES
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("TEST MODULE 0++ : HybridNERModule")
    print("="*80)
    
    # Chargement du modèle spaCy
    print("\n[Test] Chargement modèle spaCy...")
    nlp = spacy.load("fr_core_news_sm")
    
    # Initialisation extracteur hybride
    print("\n[Test] Initialisation HybridNERModule...")
    ner = HybridNERModule(
        nlp=nlp,
        confidence_threshold=0.6,
        enable_validation=False  # Pas de graphe pour test isolé
    )
    
    # Test extraction
    test_text = """
    Zoubida Kedad est professeur à l'Université de Versailles.
    Elle enseigne le Web Sémantique et les Bases de Données.
    Jean Dupont travaille également à l'Université Paris-Saclay.
    """
    
    print(f"\n[Test] Texte à analyser :\n{test_text}")
    
    entities = ner.extract(test_text, verbose=True)
    
    print("\n" + "="*80)
    print("RÉSULTATS FINAUX")
    print("="*80)
    for entity_text, entity_type, confidence in entities:
        print(f"  • {entity_text:30} | Type: {entity_type:8} | Confiance: {confidence:.2f}")
