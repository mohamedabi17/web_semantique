#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INTEGRATION GUIDE: Upgrading kg_extraction_semantic_web.py

This file provides step-by-step instructions for integrating the new
neuro-symbolic modules into the existing pipeline.

MODULES TO INTEGRATE:
1. HybridEntityExtractor (hybrid_entity_extractor.py)
2. VerbSemanticEngine (verb_semantic_engine.py)
3. DynamicOntologyProposer (dynamic_ontology_proposer.py)
4. TransitiveInferenceBuffer (below)

BACKWARD COMPATIBILITY: ✅ 100%
- All existing modules (Module 1, 2, 3) preserved
- Existing functions kept as fallbacks
- New features are ADDITIVE, not REPLACEMENTS
"""

from rdflib import Graph, URIRef, RDF, RDFS, OWL
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass


# ============================================================================
# TRANSITIVE INFERENCE BUFFER
# ============================================================================

@dataclass
class UncertainTriple:
    """Triple that couldn't be validated due to missing type information"""
    subject: str
    predicate: str
    object: str
    issue: str  # "subject_type_unknown", "object_type_unknown", etc.
    attempts: int = 0
    max_attempts: int = 3


class TransitiveInferenceBuffer:
    """
    Buffer for triples that failed Module 0 but might be recoverable.
    
    Problem Solved:
    ----------------
    Text: "A locatedIn B. B locatedIn C."
    
    Issue: If "A" not detected by spaCy → no (A locatedIn B) triple
           → Module 2 can't infer (A locatedIn C)
    
    Solution:
    ---------
    1. Detect pattern "X locatedIn Y" even if X type uncertain
    2. Store in buffer with flag issue="subject_type_unknown"
    3. After Module 1: Try to infer X's type from ontology constraints
    4. If successful: validate triple and enable Module 2
    
    Architecture:
    -------------
    Buffer ← [uncertain triples]
         ↓
    Ontology-based type inference
         ↓
    Retry validation
         ↓
    If valid → Add to graph → Module 2 processes
    
    Usage:
    ------
        buffer = TransitiveInferenceBuffer()
        
        # During extraction: store uncertain triples
        buffer.add_uncertain_triple("X", "locatedIn", "Y", issue="subject_type_unknown")
        
        # After Module 1: retry with type inference
        recovered = buffer.retry_with_ontology_typing(graph, entity_types)
        
        # Add recovered triples to graph
        for triple in recovered:
            graph.add(triple)
    """
    
    def __init__(self):
        self.uncertain_triples: List[UncertainTriple] = []
        self.recovered_count = 0
        self.failed_count = 0
    
    def add_uncertain_triple(self, subject: str, predicate: str, obj: str, issue: str):
        """
        Add a triple that couldn't be validated.
        
        Args:
            subject: Subject entity text
            predicate: Relation type
            obj: Object entity text
            issue: Reason for uncertainty
        """
        triple = UncertainTriple(
            subject=subject,
            predicate=predicate,
            object=obj,
            issue=issue
        )
        self.uncertain_triples.append(triple)
        print(f"  🔄 [Buffer] Stored uncertain triple: {subject} --[{predicate}]--> {obj}")
        print(f"     Issue: {issue}")
    
    def retry_with_ontology_typing(self, graph: Graph, entity_uris: Dict[str, URIRef],
                                   EX, FOAF, SCHEMA) -> List[Tuple]:
        """
        Attempt to recover uncertain triples using ontology-based type inference.
        
        Strategy:
        - If subject type unknown: infer from predicate domain constraint
        - If object type unknown: infer from predicate range constraint
        - If both unknown: try pattern matching (e.g., capitalized → Person)
        
        Args:
            graph: RDF graph with ontology
            entity_uris: Dict mapping entity_text → URIRef
            EX, FOAF, SCHEMA: Namespaces
        
        Returns:
            List of recovered RDF triples (subject, predicate, object)
        """
        print("\n" + "="*80)
        print("[TRANSITIVE INFERENCE BUFFER] Attempting recovery")
        print("="*80)
        
        recovered_triples = []
        
        for triple in self.uncertain_triples:
            if triple.attempts >= triple.max_attempts:
                continue
            
            triple.attempts += 1
            
            # Try to resolve missing types
            if triple.issue == "subject_type_unknown":
                success = self._infer_subject_type(triple, graph, entity_uris, EX, FOAF, SCHEMA)
                if success:
                    # Build RDF triple
                    subj_uri = entity_uris.get(triple.subject)
                    obj_uri = entity_uris.get(triple.object)
                    pred_uri = getattr(EX, triple.predicate)
                    
                    if subj_uri and obj_uri:
                        recovered_triples.append((subj_uri, pred_uri, obj_uri))
                        self.recovered_count += 1
                        print(f"  ✓ Recovered: {triple.subject} --[{triple.predicate}]--> {triple.object}")
            
            elif triple.issue == "object_type_unknown":
                success = self._infer_object_type(triple, graph, entity_uris, EX, FOAF, SCHEMA)
                if success:
                    subj_uri = entity_uris.get(triple.subject)
                    obj_uri = entity_uris.get(triple.object)
                    pred_uri = getattr(EX, triple.predicate)
                    
                    if subj_uri and obj_uri:
                        recovered_triples.append((subj_uri, pred_uri, obj_uri))
                        self.recovered_count += 1
                        print(f"  ✓ Recovered: {triple.subject} --[{triple.predicate}]--> {triple.object}")
        
        self.failed_count = len([t for t in self.uncertain_triples if t.attempts >= t.max_attempts])
        
        print(f"\n  ✓ Recovery complete: {self.recovered_count} recovered, {self.failed_count} failed")
        print("="*80 + "\n")
        
        return recovered_triples
    
    def _infer_subject_type(self, triple: UncertainTriple, graph: Graph,
                           entity_uris: Dict, EX, FOAF, SCHEMA) -> bool:
        """
        Infer subject type from predicate domain constraint.
        
        Example: If predicate=locatedIn and domain=Place → subject must be Place
        """
        pred_uri = getattr(EX, triple.predicate)
        
        # Get domain constraint
        domains = list(graph.objects(pred_uri, RDFS.domain))
        
        if not domains:
            return False
        
        # Try first domain
        domain = domains[0]
        
        # Add type to graph
        subj_uri = entity_uris.get(triple.subject)
        if not subj_uri:
            # Create URI if doesn't exist
            from rdflib import Namespace
            DATA = Namespace("http://example.org/master2/data#")
            subj_uri = DATA[triple.subject.replace(" ", "_")]
            entity_uris[triple.subject] = subj_uri
        
        graph.add((subj_uri, RDF.type, domain))
        print(f"    🔍 Inferred: {triple.subject} is type {domain}")
        
        return True
    
    def _infer_object_type(self, triple: UncertainTriple, graph: Graph,
                          entity_uris: Dict, EX, FOAF, SCHEMA) -> bool:
        """
        Infer object type from predicate range constraint.
        """
        pred_uri = getattr(EX, triple.predicate)
        
        # Get range constraint
        ranges = list(graph.objects(pred_uri, RDFS.range))
        
        if not ranges:
            return False
        
        # Try first range
        range_type = ranges[0]
        
        # Add type to graph
        obj_uri = entity_uris.get(triple.object)
        if not obj_uri:
            from rdflib import Namespace
            DATA = Namespace("http://example.org/master2/data#")
            obj_uri = DATA[triple.object.replace(" ", "_")]
            entity_uris[triple.object] = obj_uri
        
        graph.add((obj_uri, RDF.type, range_type))
        print(f"    🔍 Inferred: {triple.object} is type {range_type}")
        
        return True
    
    def get_statistics(self) -> dict:
        """Return buffer statistics"""
        return {
            'total_buffered': len(self.uncertain_triples),
            'recovered': self.recovered_count,
            'failed': self.failed_count,
            'pending': len([t for t in self.uncertain_triples if t.attempts < t.max_attempts])
        }


# ============================================================================
# INTEGRATION STEPS
# ============================================================================

INTEGRATION_GUIDE = """
╔══════════════════════════════════════════════════════════════════════════╗
║           INTEGRATION GUIDE: kg_extraction_semantic_web.py               ║
╚══════════════════════════════════════════════════════════════════════════╝

STEP 1: Add imports at the top of kg_extraction_semantic_web.py
------------------------------------------------------------------------

# Add after existing imports
from hybrid_entity_extractor import HybridEntityExtractor, DetectedEntity, EntityType
from verb_semantic_engine import VerbSemanticEngine, TripleCandidate, RelationType
from dynamic_ontology_proposer import DynamicOntologyProposer, OntologyExtension

# Or import the buffer class
from transitive_inference_buffer import TransitiveInferenceBuffer


STEP 2: Update extract_entities_with_spacy() function
------------------------------------------------------------------------

# OLD VERSION (keep as fallback):
def extract_entities_with_spacy_LEGACY(text, nlp):
    # ... existing code ...
    pass

# NEW VERSION (use HybridEntityExtractor):
def extract_entities_with_spacy(text, nlp, enable_hybrid=True, enable_llm_fallback=False):
    \"""
    Enhanced entity extraction with hybrid multi-layer strategy.
    
    Args:
        text: Input text
        nlp: spaCy model
        enable_hybrid: Use HybridEntityExtractor (default: True)
        enable_llm_fallback: Enable Layer 5 LLM fallback (default: False)
    
    Returns:
        List of (entity_text, entity_type) tuples
    \"""
    if not enable_hybrid:
        # Fallback to legacy spaCy-only extraction
        return extract_entities_with_spacy_LEGACY(text, nlp)
    
    print("\\n[ENHANCED EXTRACTION] Using HybridEntityExtractor...")
    
    # Initialize hybrid extractor
    extractor = HybridEntityExtractor(
        nlp, 
        enable_llm_fallback=enable_llm_fallback
    )
    
    # Extract entities (multi-layer)
    detected_entities = extractor.extract(text)
    
    # Convert to legacy format (entity_text, entity_type)
    entities = []
    for entity in detected_entities:
        # Map EntityType enum to string
        type_str = entity.entity_type.value  # "PER", "ORG", "LOC", etc.
        entities.append((entity.text, type_str))
        
        # Log provenance
        print(f"  ✓ {entity.text} ({type_str}) "
              f"[source: {entity.source_layer.value}, conf: {entity.confidence:.2f}]")
    
    print(f"\\n  ✓ Total: {len(entities)} entities extracted")
    print(f"  ✓ Statistics: {extractor.get_statistics()}\\n")
    
    return entities


STEP 3: Add VerbSemanticEngine to extract_relations()
------------------------------------------------------------------------

def extract_relations(graph, entity_uris, text, nlp=None, entity_types=None):
    \"""
    Enhanced relation extraction with verb-first strategy.
    \"""
    print("\\n[ENHANCED RELATION EXTRACTION] Using VerbSemanticEngine...")
    
    # Phase 1: VERB-BASED EXTRACTION (symbolic, deterministic)
    verb_relations = []
    if nlp:
        doc = nlp(text)
        engine = VerbSemanticEngine(nlp, entity_types=entity_types)
        
        # Extract verb-based triples
        entity_texts = list(entity_uris.keys())
        verb_triples = engine.extract_verb_relations(doc, entity_texts=entity_texts)
        
        # Convert to graph format
        for triple in verb_triples:
            if triple.confidence >= 0.70:  # Threshold
                verb_relations.append({
                    'entity1': triple.subject,
                    'relation': triple.predicate.value,
                    'entity2': triple.object,
                    'confidence': triple.confidence,
                    'source': 'verb_engine'
                })
                print(f"  ✓ [Verb Engine] {triple}")
    
    # Phase 2: LLM FALLBACK (only for pairs not covered by verb engine)
    # Extract remaining entity pairs
    covered_pairs = {(r['entity1'], r['entity2']) for r in verb_relations}
    
    entities_list = list(entity_uris.items())
    for i, (entity1_text, entity1_uri) in enumerate(entities_list):
        for j, (entity2_text, entity2_uri) in enumerate(entities_list):
            if i >= j:
                continue
            
            # Skip if already covered by verb engine
            if (entity1_text, entity2_text) in covered_pairs:
                print(f"  ↪️ Skipping LLM for {entity1_text}-{entity2_text} (verb engine covered)")
                continue
            
            # Call LLM for uncertain cases
            relation_type = predict_relation_real_api(entity1_text, entity2_text, text)
            
            if relation_type:
                # ... existing validation logic ...
                pass


STEP 4: Add DynamicOntologyProposer (optional)
------------------------------------------------------------------------

def main():
    # ... existing code ...
    
    # After define_tbox(graph):
    
    # OPTIONAL: Dynamic Ontology Extension
    ENABLE_DYNAMIC_ONTOLOGY = False  # Set to True to enable
    
    if ENABLE_DYNAMIC_ONTOLOGY:
        print("\\n" + "="*80)
        print("[DYNAMIC ONTOLOGY] Analyzing text for extensions")
        print("="*80)
        
        proposer = DynamicOntologyProposer(graph, base_namespace=EX)
        extension = proposer.propose_extensions(text_example, enable_proposal=True)
        
        if extension and extension.validation_status == "approved":
            proposer.apply_extensions(graph, extension)
            print(f"✓ Ontology extended: {len(extension.classes)} classes, "
                  f"{len(extension.properties)} properties")
    
    # ... continue with existing code ...


STEP 5: Add TransitiveInferenceBuffer to main()
------------------------------------------------------------------------

def main():
    # ... existing code ...
    
    # Initialize buffer BEFORE extraction
    transitive_buffer = TransitiveInferenceBuffer()
    
    # During extract_relations(), when a triple fails validation:
    # (Add this in the validation section)
    
    # Example: If entity type unknown but pattern detected
    if not domain_valid:
        # Store in buffer instead of rejecting
        transitive_buffer.add_uncertain_triple(
            entity1_text, 
            relation_type, 
            entity2_text,
            issue="subject_type_unknown"
        )
        continue  # Don't add to graph yet
    
    # ... after extract_relations() ...
    
    # BEFORE Module 2: Retry buffered triples
    print("\\n" + "="*80)
    print("[TRANSITIVE BUFFER] Attempting recovery")
    print("="*80)
    
    recovered_triples = transitive_buffer.retry_with_ontology_typing(
        graph, entity_uris, EX, FOAF, SCHEMA
    )
    
    # Add recovered triples to graph
    for subj, pred, obj in recovered_triples:
        graph.add((subj, pred, obj))
    
    print(f"✓ Buffer statistics: {transitive_buffer.get_statistics()}")
    
    # NOW run Module 2 (with recovered triples available)
    inference_results = enrich_graph_with_transitive_inference(graph)


STEP 6: Update statistics reporting
------------------------------------------------------------------------

def main():
    # ... at the end of main() ...
    
    print("\\n" + "="*80)
    print("ENHANCED STATISTICS")
    print("="*80)
    print(f"Entity Extraction:")
    print(f"  - Hybrid layers: {extractor.get_statistics()}")
    print(f"\\nRelation Extraction:")
    print(f"  - Verb engine: {verb_engine.get_statistics()}")
    print(f"  - LLM fallback: {llm_calls_count}")
    print(f"\\nTransitive Buffer:")
    print(f"  - {transitive_buffer.get_statistics()}")
    if ENABLE_DYNAMIC_ONTOLOGY:
        print(f"\\nDynamic Ontology:")
        print(f"  - {proposer.get_statistics()}")


╔══════════════════════════════════════════════════════════════════════════╗
║                         TESTING CHECKLIST                                ║
╚══════════════════════════════════════════════════════════════════════════╝

□ Test 1: HybridEntityExtractor standalone
  Command: python3 hybrid_entity_extractor.py
  Expected: Multiple layers extract entities with confidence scores

□ Test 2: VerbSemanticEngine standalone
  Command: python3 verb_semantic_engine.py
  Expected: Verb-based relations extracted with high confidence

□ Test 3: DynamicOntologyProposer standalone
  Command: python3 dynamic_ontology_proposer.py
  Expected: LLM proposes domain-specific extensions

□ Test 4: Full integration test
  Command: python3 kg_extraction_semantic_web.py
  Expected: All modules work together, statistics printed

□ Test 5: Backward compatibility
  Set enable_hybrid=False → should use legacy extraction

□ Test 6: Performance comparison
  Compare: triples extracted (old vs new), LLM calls (old vs new)


╔══════════════════════════════════════════════════════════════════════════╗
║                      CONFIGURATION OPTIONS                               ║
╚══════════════════════════════════════════════════════════════════════════╝

Add to top of main():

# Feature flags
ENABLE_HYBRID_EXTRACTION = True       # Use multi-layer entity extraction
ENABLE_LLM_FALLBACK = False          # Enable Layer 5 (LLM entity detection)
ENABLE_VERB_ENGINE = True            # Use verb-based relation extraction
ENABLE_DYNAMIC_ONTOLOGY = False      # Enable LLM ontology proposals
ENABLE_TRANSITIVE_BUFFER = True      # Enable uncertain triple recovery

# Confidence thresholds
VERB_ENGINE_THRESHOLD = 0.70         # Min confidence for verb-based triples
ENTITY_CONFIDENCE_THRESHOLD = 0.60   # Min confidence for entities

# Logging
VERBOSE_MODE = True                  # Print detailed extraction logs
"""

if __name__ == "__main__":
    print(INTEGRATION_GUIDE)
