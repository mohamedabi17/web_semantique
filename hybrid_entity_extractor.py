#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODULE 0++: HYBRID ENTITY EXTRACTION ENGINE

This module implements a multi-layer entity extraction strategy combining:
- Layer 1: spaCy NER (baseline neural)
- Layer 2: PROPN Heuristic (capitalization-based)
- Layer 3: Rule-Based Matcher (pattern-based)
- Layer 4: Dependency Parser (syntactic structure)
- Layer 5: LLM Fallback (for uncertain cases)
- Layer 6: Entity Recovery System (synthetic entity builder)

Architecture: Symbolic-first with neural fallback
Each layer adds confidence-scored entities, preventing information loss.
"""

import spacy
from spacy.matcher import Matcher
from dataclasses import dataclass
from typing import List, Optional, Tuple, Set
from enum import Enum
import re
from groq import Groq
import os
import json


class EntityType(Enum):
    """Standard entity types in our ontology"""
    PERSON = "PER"
    ORGANIZATION = "ORG"
    LOCATION = "LOC"
    TOPIC = "TOPIC"
    DOCUMENT = "DOC"
    MISC = "MISC"


class ExtractionLayer(Enum):
    """Source layer for provenance tracking"""
    SPACY_NER = "spacy_ner"
    PROPN_HEURISTIC = "propn_heuristic"
    RULE_MATCHER = "rule_matcher"
    DEPENDENCY_PARSER = "dependency_parser"
    LLM_FALLBACK = "llm_fallback"
    ENTITY_RECOVERY = "entity_recovery"


@dataclass
class DetectedEntity:
    """Entity with confidence and provenance metadata"""
    text: str
    entity_type: EntityType
    confidence: float
    source_layer: ExtractionLayer
    start_char: int = 0
    end_char: int = 0
    
    def __hash__(self):
        return hash((self.text.lower(), self.entity_type.value))
    
    def __eq__(self, other):
        if not isinstance(other, DetectedEntity):
            return False
        return self.text.lower() == other.text.lower() and \
               self.entity_type == other.entity_type


class HybridEntityExtractor:
    """
    Multi-layer hybrid entity extraction engine.
    
    Design Philosophy:
    - Symbolic layers (rules, patterns) run first (fast, explainable)
    - Neural layers (spaCy, LLM) fill gaps (accurate but slower)
    - Confidence scoring enables layer prioritization
    - All entities preserved (no information loss)
    
    Usage:
        extractor = HybridEntityExtractor(nlp, enable_llm_fallback=True)
        entities = extractor.extract("Marie travaille à Paris.")
        # Returns: [DetectedEntity("Marie", PERSON, 0.95, SPACY_NER), ...]
    """
    
    def __init__(self, nlp, enable_llm_fallback: bool = False, groq_api_key: str = None):
        """
        Initialize the hybrid extractor.
        
        Args:
            nlp: Loaded spaCy model (fr_core_news_sm)
            enable_llm_fallback: Enable Layer 5 (LLM) for uncertain entities
            groq_api_key: Groq API key (optional, loaded from env if None)
        """
        self.nlp = nlp
        self.enable_llm_fallback = enable_llm_fallback
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY", "")
        
        # Initialize spaCy Matcher for rule-based patterns
        self.matcher = Matcher(nlp.vocab)
        self._init_patterns()
        
        # Statistics tracking
        self.stats = {
            'spacy_ner': 0,
            'propn_heuristic': 0,
            'rule_matcher': 0,
            'dependency_parser': 0,
            'llm_fallback': 0,
            'entity_recovery': 0
        }
    
    def _init_patterns(self):
        """Initialize rule-based patterns for Layer 3"""
        
        # Pattern: PERSON works at ORGANIZATION
        # Ex: "Marie travaille chez Google"
        pattern_work = [
            {"LOWER": {"IN": ["travaille", "travaillé", "travaillant", "works", "worked"]}},
            {"LOWER": {"IN": ["à", "chez", "dans", "at", "in"]}, "OP": "?"},
            {"POS": "PROPN", "OP": "+"}
        ]
        self.matcher.add("WORK_AT_ORG", [pattern_work])
        
        # Pattern: PERSON lives in LOCATION
        # Ex: "Jean habite Paris"
        pattern_live = [
            {"LOWER": {"IN": ["habite", "habité", "habitant", "lives", "lived"]}},
            {"LOWER": {"IN": ["à", "dans", "in"]}, "OP": "?"},
            {"POS": "PROPN", "OP": "+"}
        ]
        self.matcher.add("LIVES_IN_LOC", [pattern_live])
        
        # Pattern: PERSON teaches TOPIC
        # Ex: "Prof enseigne Physique"
        pattern_teach = [
            {"LOWER": {"IN": ["enseigne", "enseigné", "enseignant", "teaches", "taught"]}},
            {"POS": "PROPN", "OP": "+"}
        ]
        self.matcher.add("TEACHES_SUBJECT", [pattern_teach])
        
        # Pattern: PERSON collaborates with PERSON
        # Ex: "Alice collabore avec Bob"
        pattern_collab = [
            {"POS": "PROPN", "OP": "+"},
            {"LOWER": {"IN": ["collabore", "collaborates"]}},
            {"LOWER": "avec", "OP": "?"},
            {"POS": "PROPN", "OP": "+"}
        ]
        self.matcher.add("COLLABORATES_WITH", [pattern_collab])
    
    def extract(self, text: str) -> List[DetectedEntity]:
        """
        Main extraction pipeline - runs all layers sequentially.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of DetectedEntity objects with confidence and provenance
        """
        print("\n" + "="*80)
        print("[MODULE 0++] HYBRID ENTITY EXTRACTION ENGINE")
        print("="*80)
        
        # Parse text with spaCy (used by multiple layers)
        doc = self.nlp(text)
        
        # Container for all detected entities (set prevents duplicates)
        all_entities = set()
        
        # LAYER 1: spaCy NER (baseline)
        layer1_entities = self._layer1_spacy_ner(doc)
        all_entities.update(layer1_entities)
        self.stats['spacy_ner'] = len(layer1_entities)
        print(f"  [Layer 1] spaCy NER: {len(layer1_entities)} entities")
        
        # LAYER 2: PROPN Heuristic (capitalization)
        layer2_entities = self._layer2_propn_heuristic(doc, all_entities)
        all_entities.update(layer2_entities)
        self.stats['propn_heuristic'] = len(layer2_entities)
        print(f"  [Layer 2] PROPN Heuristic: {len(layer2_entities)} new entities")
        
        # LAYER 3: Rule-Based Matcher
        layer3_entities = self._layer3_rule_matcher(doc, all_entities)
        all_entities.update(layer3_entities)
        self.stats['rule_matcher'] = len(layer3_entities)
        print(f"  [Layer 3] Rule Matcher: {len(layer3_entities)} new entities")
        
        # LAYER 4: Dependency Parser
        layer4_entities = self._layer4_dependency_parser(doc, all_entities)
        all_entities.update(layer4_entities)
        self.stats['dependency_parser'] = len(layer4_entities)
        print(f"  [Layer 4] Dependency Parser: {len(layer4_entities)} new entities")
        
        # LAYER 5: LLM Fallback (optional, for uncertain entities)
        if self.enable_llm_fallback and self.groq_api_key:
            layer5_entities = self._layer5_llm_fallback(text, doc, all_entities)
            all_entities.update(layer5_entities)
            self.stats['llm_fallback'] = len(layer5_entities)
            print(f"  [Layer 5] LLM Fallback: {len(layer5_entities)} new entities")
        
        # LAYER 6: Entity Recovery System
        layer6_entities = self._layer6_entity_recovery(doc, all_entities)
        all_entities.update(layer6_entities)
        self.stats['entity_recovery'] = len(layer6_entities)
        print(f"  [Layer 6] Entity Recovery: {len(layer6_entities)} new entities")
        
        # Convert to list and sort by position in text
        final_entities = sorted(list(all_entities), key=lambda e: e.start_char)
        
        print(f"\n  ✓ Total Entities Extracted: {len(final_entities)}")
        print(f"  ✓ Breakdown by layer: {self.stats}")
        print("="*80 + "\n")
        
        return final_entities
    
    def _layer1_spacy_ner(self, doc) -> Set[DetectedEntity]:
        """
        Layer 1: Standard spaCy NER (baseline).
        Confidence: 0.85 (spaCy's baseline accuracy)
        """
        entities = set()
        
        for ent in doc.ents:
            # Normalize entity text (remove articles, etc.)
            normalized_text = self._normalize_entity(ent.text)
            if not normalized_text:
                continue
            
            # Map spaCy labels to our EntityType
            entity_type = self._map_spacy_label(ent.label_)
            
            entity = DetectedEntity(
                text=normalized_text,
                entity_type=entity_type,
                confidence=0.85,
                source_layer=ExtractionLayer.SPACY_NER,
                start_char=ent.start_char,
                end_char=ent.end_char
            )
            entities.add(entity)
            print(f"    ✓ [spaCy] {normalized_text} → {entity_type.value}")
        
        return entities
    
    def _layer2_propn_heuristic(self, doc, existing_entities: Set[DetectedEntity]) -> Set[DetectedEntity]:
        """
        Layer 2: PROPN Heuristic - detect capitalized proper nouns missed by spaCy.
        
        Rule: If token.pos_ == PROPN AND starts_with_uppercase AND not_in_existing
              → Candidate PERSON or ORG (disambiguate via context)
        
        Confidence: 0.70 (heuristic-based)
        """
        entities = set()
        existing_texts = {e.text.lower() for e in existing_entities}
        
        for token in doc:
            # Skip if already detected
            if token.text.lower() in existing_texts:
                continue
            
            # Check PROPN + capitalization
            if token.pos_ == "PROPN" and token.text[0].isupper():
                # Disambiguate: PERSON vs ORGANIZATION
                # Heuristic: Common first names → PERSON, else → ORG
                entity_type = self._heuristic_type_from_context(token, doc)
                
                entity = DetectedEntity(
                    text=token.text,
                    entity_type=entity_type,
                    confidence=0.70,
                    source_layer=ExtractionLayer.PROPN_HEURISTIC,
                    start_char=token.idx,
                    end_char=token.idx + len(token.text)
                )
                entities.add(entity)
                print(f"    ✓ [PROPN] {token.text} → {entity_type.value} (capitalized)")
        
        return entities
    
    def _layer3_rule_matcher(self, doc, existing_entities: Set[DetectedEntity]) -> Set[DetectedEntity]:
        """
        Layer 3: Rule-Based Matcher using spaCy patterns.
        
        Patterns:
        - "X travaille à Y" → Y is ORGANIZATION
        - "X habite Y" → Y is LOCATION
        - "X enseigne Y" → Y is TOPIC
        - "X collabore avec Y" → X and Y are PERSON
        
        Confidence: 0.80 (pattern-based)
        """
        entities = set()
        existing_texts = {e.text.lower() for e in existing_entities}
        
        matches = self.matcher(doc)
        
        for match_id, start, end in matches:
            span = doc[start:end]
            match_label = self.nlp.vocab.strings[match_id]
            
            # Extract entity from pattern
            entity_text = None
            entity_type = None
            
            if match_label == "WORK_AT_ORG":
                # Extract organization name (last PROPN tokens)
                entity_text = " ".join([t.text for t in span if t.pos_ == "PROPN"])
                entity_type = EntityType.ORGANIZATION
            
            elif match_label == "LIVES_IN_LOC":
                # Extract location
                entity_text = " ".join([t.text for t in span if t.pos_ == "PROPN"])
                entity_type = EntityType.LOCATION
            
            elif match_label == "TEACHES_SUBJECT":
                # Extract subject/topic
                entity_text = " ".join([t.text for t in span if t.pos_ == "PROPN"])
                entity_type = EntityType.TOPIC
            
            elif match_label == "COLLABORATES_WITH":
                # Extract both persons
                propns = [t.text for t in span if t.pos_ == "PROPN"]
                for propn in propns:
                    if propn.lower() not in existing_texts:
                        entity = DetectedEntity(
                            text=propn,
                            entity_type=EntityType.PERSON,
                            confidence=0.80,
                            source_layer=ExtractionLayer.RULE_MATCHER,
                            start_char=span.start_char,
                            end_char=span.end_char
                        )
                        entities.add(entity)
                        print(f"    ✓ [Rule] {propn} → PERSON (collaboration pattern)")
                continue
            
            if entity_text and entity_text.lower() not in existing_texts:
                entity = DetectedEntity(
                    text=entity_text,
                    entity_type=entity_type,
                    confidence=0.80,
                    source_layer=ExtractionLayer.RULE_MATCHER,
                    start_char=span.start_char,
                    end_char=span.end_char
                )
                entities.add(entity)
                print(f"    ✓ [Rule] {entity_text} → {entity_type.value} (pattern: {match_label})")
        
        return entities
    
    def _layer4_dependency_parser(self, doc, existing_entities: Set[DetectedEntity]) -> Set[DetectedEntity]:
        """
        Layer 4: Dependency Parser - extract entities from syntactic roles.
        
        Strategy: Find VERB tokens, extract nsubj (subject) and obj (object)
        If subject/object is PROPN but not in existing → add as entity
        
        Confidence: 0.75 (syntax-based)
        """
        entities = set()
        existing_texts = {e.text.lower() for e in existing_entities}
        
        for token in doc:
            if token.pos_ == "VERB":
                # Find subject (nsubj)
                for child in token.children:
                    if child.dep_ in ["nsubj", "nsubjpass"] and \
                       child.pos_ == "PROPN" and \
                       child.text.lower() not in existing_texts:
                        
                        # Infer type from verb lemma
                        entity_type = self._infer_type_from_verb(token.lemma_, role="subject")
                        
                        entity = DetectedEntity(
                            text=child.text,
                            entity_type=entity_type,
                            confidence=0.75,
                            source_layer=ExtractionLayer.DEPENDENCY_PARSER,
                            start_char=child.idx,
                            end_char=child.idx + len(child.text)
                        )
                        entities.add(entity)
                        print(f"    ✓ [Dep] {child.text} → {entity_type.value} (nsubj of '{token.lemma_}')")
                    
                    # Find object (obj, obl)
                    elif child.dep_ in ["obj", "obl"] and \
                         child.pos_ == "PROPN" and \
                         child.text.lower() not in existing_texts:
                        
                        entity_type = self._infer_type_from_verb(token.lemma_, role="object")
                        
                        entity = DetectedEntity(
                            text=child.text,
                            entity_type=entity_type,
                            confidence=0.75,
                            source_layer=ExtractionLayer.DEPENDENCY_PARSER,
                            start_char=child.idx,
                            end_char=child.idx + len(child.text)
                        )
                        entities.add(entity)
                        print(f"    ✓ [Dep] {child.text} → {entity_type.value} (obj of '{token.lemma_}')")
        
        return entities
    
    def _layer5_llm_fallback(self, text: str, doc, existing_entities: Set[DetectedEntity]) -> Set[DetectedEntity]:
        """
        Layer 5: LLM Fallback - query Groq for entities with low confidence.
        
        Only called when:
        - enable_llm_fallback=True
        - Groq API key available
        - Existing entities have average confidence < 0.8
        
        Confidence: 0.90 (LLM-based, high accuracy)
        """
        entities = set()
        
        # Check if LLM call is needed
        if not existing_entities:
            # No entities found by previous layers → definitely need LLM
            pass
        else:
            avg_confidence = sum(e.confidence for e in existing_entities) / len(existing_entities)
            if avg_confidence > 0.80:
                print(f"    ℹ️ [LLM] Skipped (avg confidence {avg_confidence:.2f} > 0.80)")
                return entities
        
        try:
            client = Groq(api_key=self.groq_api_key)
            
            prompt = f"""Extract ALL named entities from this text:

Text: "{text}"

Output a JSON array of entities with format:
[
  {{"text": "Marie", "type": "PERSON"}},
  {{"text": "Paris", "type": "LOCATION"}},
  {{"text": "Physique", "type": "TOPIC"}}
]

Types: PERSON, ORGANIZATION, LOCATION, TOPIC, DOCUMENT

JSON:"""
            
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an entity extraction expert. Output only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.1-8b-instant",
                temperature=0
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse JSON
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            
            llm_entities = json.loads(result)
            existing_texts = {e.text.lower() for e in existing_entities}
            
            for ent_data in llm_entities:
                entity_text = ent_data.get("text", "")
                entity_type_str = ent_data.get("type", "MISC")
                
                if entity_text.lower() in existing_texts:
                    continue
                
                # Map string type to EntityType
                entity_type = self._map_string_to_entity_type(entity_type_str)
                
                entity = DetectedEntity(
                    text=entity_text,
                    entity_type=entity_type,
                    confidence=0.90,
                    source_layer=ExtractionLayer.LLM_FALLBACK,
                    start_char=0,
                    end_char=0
                )
                entities.add(entity)
                print(f"    ✓ [LLM] {entity_text} → {entity_type.value}")
        
        except Exception as e:
            print(f"    ⚠️ [LLM] Error: {str(e)[:80]}")
        
        return entities
    
    def _layer6_entity_recovery(self, doc, existing_entities: Set[DetectedEntity]) -> Set[DetectedEntity]:
        """
        Layer 6: Entity Recovery System - build synthetic entities from patterns.
        
        Strategy:
        - Detect pattern: [nsubj VERB obj] where obj exists but nsubj doesn't
        - Build synthetic entity for missing nsubj
        - Example: "works at MIT" → MIT exists, but subject missing
        
        Confidence: 0.65 (synthetic, lowest priority)
        """
        entities = set()
        existing_texts = {e.text.lower() for e in existing_entities}
        
        for token in doc:
            if token.pos_ == "VERB":
                # Find subject and object
                subject = None
                obj = None
                
                for child in token.children:
                    if child.dep_ in ["nsubj", "nsubjpass"]:
                        subject = child
                    elif child.dep_ in ["obj", "obl"]:
                        obj = child
                
                # Pattern: subject exists but not detected, object detected
                if subject and subject.pos_ == "PROPN" and \
                   subject.text.lower() not in existing_texts and \
                   obj and obj.text.lower() in existing_texts:
                    
                    entity_type = self._infer_type_from_verb(token.lemma_, role="subject")
                    
                    entity = DetectedEntity(
                        text=subject.text,
                        entity_type=entity_type,
                        confidence=0.65,
                        source_layer=ExtractionLayer.ENTITY_RECOVERY,
                        start_char=subject.idx,
                        end_char=subject.idx + len(subject.text)
                    )
                    entities.add(entity)
                    print(f"    ✓ [Recovery] {subject.text} → {entity_type.value} (synthetic from pattern)")
        
        return entities
    
    # ========== HELPER METHODS ==========
    
    def _normalize_entity(self, text: str) -> Optional[str]:
        """Normalize entity text (remove articles, validate length)"""
        text = text.strip()
        
        # Reject entities <= 1 character
        if len(text) <= 1:
            return None
        
        # Remove articles
        articles = ["La ", "Le ", "Les ", "L'", "l'", "D'", "d'"]
        for article in articles:
            if text.startswith(article):
                text = text[len(article):]
                break
        
        if len(text) <= 1:
            return None
        
        # Title case (unless acronym)
        if text.isupper() and len(text) <= 6:
            return text
        return text.title()
    
    def _map_spacy_label(self, label: str) -> EntityType:
        """Map spaCy NER labels to our EntityType"""
        mapping = {
            "PER": EntityType.PERSON,
            "PERSON": EntityType.PERSON,
            "ORG": EntityType.ORGANIZATION,
            "LOC": EntityType.LOCATION,
            "GPE": EntityType.LOCATION,
            "MISC": EntityType.MISC
        }
        return mapping.get(label, EntityType.MISC)
    
    def _map_string_to_entity_type(self, type_str: str) -> EntityType:
        """Map string type to EntityType enum"""
        mapping = {
            "PERSON": EntityType.PERSON,
            "ORGANIZATION": EntityType.ORGANIZATION,
            "LOCATION": EntityType.LOCATION,
            "TOPIC": EntityType.TOPIC,
            "DOCUMENT": EntityType.DOCUMENT,
            "MISC": EntityType.MISC
        }
        return mapping.get(type_str.upper(), EntityType.MISC)
    
    def _heuristic_type_from_context(self, token, doc) -> EntityType:
        """
        Heuristic to determine entity type from context.
        
        Rules:
        - If token is nsubj of "works"/"teaches" → PERSON
        - If token is obj of "works at" → ORGANIZATION
        - If token is obj of "located in" → LOCATION
        - Common first names → PERSON
        - Else → ORGANIZATION (default for proper nouns)
        """
        # Check if it's a subject of a person-oriented verb
        if token.dep_ == "nsubj":
            head = token.head
            if head.lemma_ in ["travailler", "enseigner", "habiter", "étudier", "work", "teach", "live", "study"]:
                return EntityType.PERSON
        
        # Check common first names (French)
        common_names = ["marie", "jean", "paul", "sophie", "alice", "bob", "john", "julie", "marc", "pierre"]
        if token.text.lower() in common_names:
            return EntityType.PERSON
        
        # Default: ORGANIZATION
        return EntityType.ORGANIZATION
    
    def _infer_type_from_verb(self, verb_lemma: str, role: str) -> EntityType:
        """
        Infer entity type based on verb and syntactic role.
        
        Args:
            verb_lemma: Lemma of the verb
            role: "subject" or "object"
        
        Returns:
            Inferred EntityType
        """
        if role == "subject":
            # Subjects of these verbs are typically PERSON
            person_verbs = ["travailler", "enseigner", "habiter", "étudier", "diriger", 
                           "gérer", "collaborer", "work", "teach", "live", "study", "manage"]
            if verb_lemma in person_verbs:
                return EntityType.PERSON
            return EntityType.ORGANIZATION
        
        elif role == "object":
            # Objects depend on verb
            # "travaille à X" → X is ORG or LOC (ambiguous, default ORG)
            # "habite X" → X is LOC
            # "enseigne X" → X is TOPIC
            if verb_lemma in ["habiter", "situer", "localiser", "live", "locate"]:
                return EntityType.LOCATION
            elif verb_lemma in ["enseigner", "étudier", "teach", "study"]:
                return EntityType.TOPIC
            else:
                return EntityType.ORGANIZATION
        
        return EntityType.MISC
    
    def get_statistics(self) -> dict:
        """Return extraction statistics"""
        return self.stats.copy()


# ============================================================================
# STANDALONE TESTING
# ============================================================================

if __name__ == "__main__":
    print("Testing HybridEntityExtractor...\n")
    
    # Load spaCy model
    try:
        nlp = spacy.load("fr_core_news_sm")
    except:
        print("Error: Please install fr_core_news_sm: python -m spacy download fr_core_news_sm")
        exit(1)
    
    # Test cases
    test_texts = [
        "Marie travaille à Paris.",
        "Alice collabore avec Bob sur le projet RDFS.",
        "Jean habite Lyon et enseigne la Physique à l'Université.",
        "Sofia dirige Google France.",
    ]
    
    # Initialize extractor
    extractor = HybridEntityExtractor(nlp, enable_llm_fallback=False)
    
    for text in test_texts:
        print(f"\n{'='*80}")
        print(f"TEXT: {text}")
        print('='*80)
        
        entities = extractor.extract(text)
        
        print("\nExtracted Entities:")
        for entity in entities:
            print(f"  - {entity.text} ({entity.entity_type.value}) "
                  f"[confidence: {entity.confidence:.2f}, source: {entity.source_layer.value}]")
        
        print(f"\nStatistics: {extractor.get_statistics()}")
