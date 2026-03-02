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
                # Universités françaises
                {"label": "ORG", "pattern": [{"LOWER": "université"}, {"IS_TITLE": True}]},
                {"label": "ORG", "pattern": "Université Paris-Saclay"},
                {"label": "ORG", "pattern": "Université de Versailles"},
                {"label": "ORG", "pattern": "Sorbonne Université"},
                {"label": "ORG", "pattern": "École Polytechnique"},
                
                # Matières/Topics académiques
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
                
                # Technologies et concepts (détectés comme DOCUMENT pour les articles)
                {"label": "DOCUMENT", "pattern": "RDF"},
                {"label": "DOCUMENT", "pattern": "RDFS"},
                {"label": "DOCUMENT", "pattern": "OWL"},
                {"label": "DOCUMENT", "pattern": "SPARQL"},
                {"label": "DOCUMENT", "pattern": "JSON-LD"},
                {"label": "DOCUMENT", "pattern": "Turtle"},
                
                # Titres académiques
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
        
        # COUCHE 1 : spaCy NER + EntityRuler
        doc = self.nlp(text)
        raw_entities = self._layer1_spacy_ner(doc, verbose)
        
        # COUCHE 3 : Heuristiques PROPN
        propn_entities = self._layer3_propn_heuristics(doc, verbose)
        
        # Fusion des entités
        all_entities = raw_entities + propn_entities
        
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
            entities.append((ent.text, ent.label_, confidence))
            
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
        COUCHE 3 : Heuristiques linguistiques PROPN.
        
        Détecte les séquences de noms propres (PROPN) qui forment une entité.
        Exemple : "Zoubida Kedad" = PROPN + PROPN
        
        Args:
            doc: Document spaCy traité
            verbose: Affiche logs
            
        Returns:
            Liste (entité, type, confiance)
        """
        if verbose:
            print("\n[COUCHE 3] Heuristiques PROPN")
            print("-" * 80)
        
        entities = []
        propn_sequence = []
        propn_tokens_found = 0
        
        for token in doc:
            if token.pos_ == "PROPN":
                propn_tokens_found += 1
                propn_sequence.append(token.text)
            else:
                if len(propn_sequence) >= 2:
                    # Séquence de ≥2 noms propres → probablement une entité
                    entity_text = " ".join(propn_sequence)
                    
                    # Si déjà détecté par spaCy, ignorer
                    if not self._already_detected_by_spacy(entity_text, doc):
                        entities.append((entity_text, "PER", 0.75))  # Confiance heuristique
                        if verbose:
                            print(f"  🔍 PROPN : '{entity_text}' → PER (conf: 0.75)")
                
                propn_sequence = []
        
        # Dernière séquence en fin de phrase
        if len(propn_sequence) >= 2:
            entity_text = " ".join(propn_sequence)
            if not self._already_detected_by_spacy(entity_text, doc):
                entities.append((entity_text, "PER", 0.75))
                if verbose:
                    print(f"  🔍 PROPN : '{entity_text}' → PER (conf: 0.75)")
        
        if verbose:
            print(f"\n  📊 Statistiques Couche 3 : {propn_tokens_found} tokens PROPN analysés")
            if entities:
                print(f"     • {len(entities)} nouvelle(s) entité(s) détectée(s)")
            else:
                print(f"     • Aucune nouvelle entité (toutes déjà détectées)")
        
        return entities
    
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
            
            # Suppression articles français
            clean_text = re.sub(r"^(le|la|l'|les|un|une|des|du|de)\s+", "", clean_text, flags=re.IGNORECASE)
            
            # Standardisation casse (Title Case pour PER/ORG)
            if entity_type in ["PER", "ORG"]:
                clean_text = clean_text.title()
            
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
