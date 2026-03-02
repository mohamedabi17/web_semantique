#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERB SEMANTIC ENGINE

Purpose: Rule-based verb → relation mapping BEFORE LLM disambiguation.

Architecture Philosophy:
- LLM should NOT decide verb semantics
- Linguistic analysis (lemma + dependency parsing) provides deterministic mapping
- LLM becomes ONLY a fallback for ambiguous cases
- Confidence scoring enables prioritization

Core Innovation:
Instead of asking LLM "what is the relation between X and Y?",
we extract: subject-VERB-object via dependency parsing,
then map VERB.lemma → OWL property deterministically.

Example:
  Text: "Marie travaille à Paris."
  1. Dependency parse: Marie[nsubj] ← travaille[VERB] → Paris[obl]
  2. Extract: (Marie, travailler, Paris)
  3. Context check: Paris is Place (not Organization)
  4. Map: travailler + Place → locatedIn
  5. Output: (Marie, locatedIn, Paris) [confidence: 0.95]
"""

import spacy
from typing import List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class RelationType(Enum):
    """OWL ObjectProperty types in our ontology"""
    TEACHES = "teaches"
    TEACHES_SUBJECT = "teachesSubject"
    AUTHOR = "author"
    WORKS_AT = "worksAt"
    LOCATED_IN = "locatedIn"
    COLLABORATES_WITH = "collaboratesWith"
    STUDIES_AT = "studiesAt"
    MANAGES = "manages"
    RELATED_TO = "relatedTo"


@dataclass
class TripleCandidate:
    """
    Candidate RDF triple extracted from verb analysis.
    
    Attributes:
        subject: Subject entity text
        predicate: Relation type (OWL property)
        object: Object entity text
        confidence: Confidence score (0.0 - 1.0)
        verb_lemma: Original verb lemma (for provenance)
        sentence: Source sentence (for validation)
    """
    subject: str
    predicate: RelationType
    object: str
    confidence: float
    verb_lemma: str
    sentence: str
    
    def __repr__(self):
        return f"{self.subject} --[{self.predicate.value}]--> {self.object} (conf: {self.confidence:.2f})"


class VerbSemanticEngine:
    """
    Deterministic verb-to-relation mapper using linguistic analysis.
    
    Design:
    1. Dependency parsing extracts subject-verb-object triples
    2. Verb lemma mapped to base relation type
    3. Context-aware disambiguation (e.g., works + Place → locatedIn)
    4. Confidence scoring based on pattern certainty
    
    Usage:
        engine = VerbSemanticEngine(nlp)
        doc = nlp("Marie travaille à Paris.")
        triples = engine.extract_verb_relations(doc, entity_texts=["Marie", "Paris"])
        # Returns: [TripleCandidate(Marie, locatedIn, Paris, 0.95, "travailler", ...)]
    """
    
    def __init__(self, nlp, entity_types: dict = None):
        """
        Initialize the Verb Semantic Engine.
        
        Args:
            nlp: Loaded spaCy model
            entity_types: Optional dict mapping entity_text → type (PER, LOC, ORG)
        """
        self.nlp = nlp
        self.entity_types = entity_types or {}
        
        # Core verb → relation mapping
        self.lemma_to_relation = {
            # Location/Residence
            "habiter": self._resolve_habiter,
            "vivre": self._resolve_habiter,
            "résider": self._resolve_habiter,
            "live": self._resolve_habiter,
            "reside": self._resolve_habiter,
            
            # Work/Employment
            "travailler": self._resolve_travailler,
            "work": self._resolve_travailler,
            "employer": self._resolve_travailler,
            
            # Teaching
            "enseigner": self._resolve_enseigner,
            "teach": self._resolve_enseigner,
            "former": self._resolve_enseigner,
            
            # Management
            "diriger": self._resolve_diriger,
            "gérer": self._resolve_diriger,
            "manage": self._resolve_diriger,
            "administrer": self._resolve_diriger,
            
            # Authorship
            "écrire": self._resolve_ecrire,
            "rédiger": self._resolve_ecrire,
            "write": self._resolve_ecrire,
            "author": self._resolve_ecrire,
            
            # Location (placement)
            "situer": self._resolve_situer,
            "localiser": self._resolve_situer,
            "locate": self._resolve_situer,
            "se trouver": self._resolve_situer,
            
            # Collaboration
            "collaborer": self._resolve_collaborer,
            "collaborate": self._resolve_collaborer,
            "coopérer": self._resolve_collaborer,
            
            # Study
            "étudier": self._resolve_etudier,
            "study": self._resolve_etudier,
            "apprendre": self._resolve_etudier,
        }
        
        # Statistics
        self.stats = {
            'triples_extracted': 0,
            'high_confidence': 0,  # confidence >= 0.9
            'medium_confidence': 0,  # 0.7 <= confidence < 0.9
            'low_confidence': 0,  # confidence < 0.7
        }
    
    def extract_verb_relations(self, doc, entity_texts: List[str] = None) -> List[TripleCandidate]:
        """
        Extract all verb-based relations from a document.
        
        Args:
            doc: spaCy Doc object
            entity_texts: Optional list of entity texts to focus on
        
        Returns:
            List of TripleCandidate objects
        """
        print("\n" + "="*80)
        print("[VERB SEMANTIC ENGINE] Extracting verb-based relations")
        print("="*80)
        
        triples = []
        entity_set = set([e.lower() for e in entity_texts]) if entity_texts else None
        
        # Iterate over all VERB tokens
        for token in doc:
            if token.pos_ != "VERB":
                continue
            
            # Extract subject and object via dependency parsing
            subject = self._find_subject(token)
            obj = self._find_object(token)
            
            # Skip if subject or object not found
            if not subject or not obj:
                continue
            
            # Skip if not in entity list (if provided)
            if entity_set:
                if subject.text.lower() not in entity_set or \
                   obj.text.lower() not in entity_set:
                    continue
            
            # Get verb lemma
            verb_lemma = token.lemma_
            
            # Check if verb has a mapping
            if verb_lemma not in self.lemma_to_relation:
                continue
            
            # Resolve relation using context-aware resolver
            resolver = self.lemma_to_relation[verb_lemma]
            
            try:
                relation_type, confidence = resolver(
                    subject=subject,
                    verb=token,
                    obj=obj,
                    doc=doc
                )
                
                if relation_type:
                    # Extract sentence containing this triple
                    sentence = self._get_sentence_for_token(token)
                    
                    triple = TripleCandidate(
                        subject=subject.text,
                        predicate=relation_type,
                        object=obj.text,
                        confidence=confidence,
                        verb_lemma=verb_lemma,
                        sentence=sentence
                    )
                    
                    triples.append(triple)
                    self.stats['triples_extracted'] += 1
                    
                    # Update confidence stats
                    if confidence >= 0.9:
                        self.stats['high_confidence'] += 1
                    elif confidence >= 0.7:
                        self.stats['medium_confidence'] += 1
                    else:
                        self.stats['low_confidence'] += 1
                    
                    print(f"  ✓ {triple}")
            
            except Exception as e:
                print(f"  ⚠️ Error resolving '{verb_lemma}': {e}")
                continue
        
        print(f"\n  ✓ Extracted {len(triples)} verb-based relations")
        print(f"  ✓ Confidence distribution: High={self.stats['high_confidence']}, "
              f"Medium={self.stats['medium_confidence']}, Low={self.stats['low_confidence']}")
        print("="*80 + "\n")
        
        return triples
    
    # ========== VERB RESOLVERS (Context-Aware Disambiguation) ==========
    
    def _resolve_habiter(self, subject, verb, obj, doc) -> Tuple[Optional[RelationType], float]:
        """
        habiter → locatedIn
        
        Rule: PERSON habite LOCATION
        Confidence: 0.95 (unambiguous)
        """
        return (RelationType.LOCATED_IN, 0.95)
    
    def _resolve_travailler(self, subject, verb, obj, doc) -> Tuple[Optional[RelationType], float]:
        """
        travailler → worksAt OR locatedIn (context-dependent)
        
        Context Check:
        - If object is Organization → worksAt (confidence: 0.95)
        - If object is Place/City → locatedIn (confidence: 0.90)
        - Ambiguous → worksAt (confidence: 0.70)
        """
        obj_type = self.entity_types.get(obj.text, "UNKNOWN")
        
        # Check if object is a known place/city
        cities = ["paris", "lyon", "marseille", "toulouse", "bordeaux", "lille", 
                 "nice", "nantes", "strasbourg", "montpellier", "bayonne"]
        
        if obj_type == "LOC" or any(city in obj.text.lower() for city in cities):
            print(f"    🔍 Context: '{obj.text}' is Place → travailler → locatedIn")
            return (RelationType.LOCATED_IN, 0.90)
        elif obj_type == "ORG":
            print(f"    🔍 Context: '{obj.text}' is Organization → travailler → worksAt")
            return (RelationType.WORKS_AT, 0.95)
        else:
            # Ambiguous: default to worksAt with lower confidence
            print(f"    ⚠️ Ambiguous: '{obj.text}' type unknown → default worksAt")
            return (RelationType.WORKS_AT, 0.70)
    
    def _resolve_enseigner(self, subject, verb, obj, doc) -> Tuple[Optional[RelationType], float]:
        """
        enseigner → teaches OR teachesSubject (context-dependent)
        
        Context Check:
        - If object is Organization/Place → teaches (confidence: 0.95)
        - If object is Topic/Subject → teachesSubject (confidence: 0.95)
        - Heuristic: Capitalized singular noun → teachesSubject
        """
        obj_type = self.entity_types.get(obj.text, "UNKNOWN")
        
        # Check for academic subjects
        subjects = ["physique", "mathématiques", "maths", "informatique", "biologie",
                   "chimie", "histoire", "géographie", "philosophie", "littérature",
                   "physics", "mathematics", "computer science", "biology", "rdfs", "owl"]
        
        if obj_type == "TOPIC" or any(subj in obj.text.lower() for subj in subjects):
            print(f"    🔍 Context: '{obj.text}' is Topic → enseigner → teachesSubject")
            return (RelationType.TEACHES_SUBJECT, 0.95)
        elif obj_type in ["ORG", "LOC"]:
            print(f"    🔍 Context: '{obj.text}' is Place/Org → enseigner → teaches")
            return (RelationType.TEACHES, 0.95)
        else:
            # Heuristic: Capitalized single word → likely a subject
            if obj.text[0].isupper() and " " not in obj.text:
                print(f"    🔍 Heuristic: '{obj.text}' capitalized → teachesSubject")
                return (RelationType.TEACHES_SUBJECT, 0.80)
            else:
                return (RelationType.TEACHES, 0.75)
    
    def _resolve_diriger(self, subject, verb, obj, doc) -> Tuple[Optional[RelationType], float]:
        """
        diriger/gérer → manages
        
        Rule: PERSON manages ORGANIZATION
        Confidence: 0.95 (unambiguous)
        """
        return (RelationType.MANAGES, 0.95)
    
    def _resolve_ecrire(self, subject, verb, obj, doc) -> Tuple[Optional[RelationType], float]:
        """
        écrire/rédiger → author
        
        Rule: PERSON author DOCUMENT
        Confidence: 0.95 (unambiguous)
        """
        return (RelationType.AUTHOR, 0.95)
    
    def _resolve_situer(self, subject, verb, obj, doc) -> Tuple[Optional[RelationType], float]:
        """
        situer/localiser → locatedIn
        
        Rule: ENTITY locatedIn PLACE
        Confidence: 0.95 (unambiguous)
        """
        return (RelationType.LOCATED_IN, 0.95)
    
    def _resolve_collaborer(self, subject, verb, obj, doc) -> Tuple[Optional[RelationType], float]:
        """
        collaborer → collaboratesWith
        
        Rule: PERSON collaboratesWith PERSON
        Confidence: 0.95 (unambiguous)
        
        Note: Should be validated by semantic guardrail (PER↔PER only)
        """
        return (RelationType.COLLABORATES_WITH, 0.95)
    
    def _resolve_etudier(self, subject, verb, obj, doc) -> Tuple[Optional[RelationType], float]:
        """
        étudier → studiesAt OR teachesSubject (context-dependent)
        
        Context Check:
        - If object is Organization → studiesAt (confidence: 0.95)
        - If object is Topic → teachesSubject (confidence: 0.85)
        """
        obj_type = self.entity_types.get(obj.text, "UNKNOWN")
        
        if obj_type == "ORG":
            return (RelationType.STUDIES_AT, 0.95)
        else:
            # Assume it's a subject being studied
            return (RelationType.TEACHES_SUBJECT, 0.85)
    
    # ========== HELPER METHODS ==========
    
    def _find_subject(self, verb_token):
        """
        Find the subject of a verb via dependency parsing.
        
        Looks for: nsubj, nsubjpass
        Returns the subject token or None
        """
        for child in verb_token.children:
            if child.dep_ in ["nsubj", "nsubjpass"]:
                # Handle compound subjects (e.g., "Marie et Jean")
                if child.pos_ == "PROPN" or child.pos_ == "NOUN":
                    return child
        return None
    
    def _find_object(self, verb_token):
        """
        Find the object of a verb via dependency parsing.
        
        Looks for: obj, dobj, obl (oblique)
        Returns the object token or None
        """
        for child in verb_token.children:
            if child.dep_ in ["obj", "dobj", "obl"]:
                # For oblique, check if it has a preposition
                if child.dep_ == "obl":
                    # Find the actual noun (skip preposition)
                    for grandchild in child.children:
                        if grandchild.pos_ in ["PROPN", "NOUN"]:
                            return grandchild
                    return child
                else:
                    return child
        
        # Fallback: look for prepositional phrase children
        for child in verb_token.children:
            if child.dep_ == "prep":
                for grandchild in child.children:
                    if grandchild.pos_ in ["PROPN", "NOUN"]:
                        return grandchild
        
        return None
    
    def _get_sentence_for_token(self, token) -> str:
        """Extract the sentence containing a token"""
        return token.sent.text.strip()
    
    def get_statistics(self) -> dict:
        """Return extraction statistics"""
        return self.stats.copy()


# ============================================================================
# STANDALONE TESTING
# ============================================================================

if __name__ == "__main__":
    print("Testing VerbSemanticEngine...\n")
    
    # Load spaCy model
    try:
        nlp = spacy.load("fr_core_news_sm")
    except:
        print("Error: Please install fr_core_news_sm: python -m spacy download fr_core_news_sm")
        exit(1)
    
    # Test cases
    test_cases = [
        {
            "text": "Marie travaille à Paris.",
            "entities": ["Marie", "Paris"],
            "entity_types": {"Marie": "PER", "Paris": "LOC"},
            "expected": "Marie locatedIn Paris"
        },
        {
            "text": "Jean travaille chez Google.",
            "entities": ["Jean", "Google"],
            "entity_types": {"Jean": "PER", "Google": "ORG"},
            "expected": "Jean worksAt Google"
        },
        {
            "text": "Sophie enseigne la Physique.",
            "entities": ["Sophie", "Physique"],
            "entity_types": {"Sophie": "PER", "Physique": "TOPIC"},
            "expected": "Sophie teachesSubject Physique"
        },
        {
            "text": "Paul enseigne à l'Université.",
            "entities": ["Paul", "Université"],
            "entity_types": {"Paul": "PER", "Université": "ORG"},
            "expected": "Paul teaches Université"
        },
        {
            "text": "Alice collabore avec Bob.",
            "entities": ["Alice", "Bob"],
            "entity_types": {"Alice": "PER", "Bob": "PER"},
            "expected": "Alice collaboratesWith Bob"
        },
        {
            "text": "Marc dirige AlgoTech.",
            "entities": ["Marc", "AlgoTech"],
            "entity_types": {"Marc": "PER", "AlgoTech": "ORG"},
            "expected": "Marc manages AlgoTech"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}: {test['text']}")
        print(f"Expected: {test['expected']}")
        print('='*80)
        
        # Parse text
        doc = nlp(test['text'])
        
        # Initialize engine with entity types
        engine = VerbSemanticEngine(nlp, entity_types=test['entity_types'])
        
        # Extract relations
        triples = engine.extract_verb_relations(doc, entity_texts=test['entities'])
        
        if triples:
            print(f"\n✓ Extracted: {triples[0]}")
            
            # Validate against expected
            expected_parts = test['expected'].split()
            if len(expected_parts) == 3:
                subj, pred, obj = expected_parts
                if triples[0].subject == subj and \
                   triples[0].predicate.value == pred and \
                   triples[0].object == obj:
                    print("✅ TEST PASSED")
                else:
                    print("❌ TEST FAILED")
        else:
            print("❌ No triples extracted")
        
        print(f"Statistics: {engine.get_statistics()}")
