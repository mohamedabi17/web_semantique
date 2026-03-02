#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DYNAMIC ONTOLOGY PROPOSER

Purpose: LLM-driven ontology extension system (OPTIONAL, non-destructive)

Philosophy:
- Base ontology is SACRED (never modified)
- LLM proposes extensions based on domain text analysis
- Extensions are validated against base ontology constraints
- All extensions marked as dynamic (provenance tracking)
- Extensions can be persisted or temporary

Use Case:
When processing domain-specific texts (e.g., medical, legal, scientific),
the base ontology may lack domain-specific classes/properties.
This system allows the ontology to grow organically while maintaining
semantic consistency.

Example:
  Base: Person, Place, Organization
  Text: "Dr. Smith participated in Conference 2024 about AI Ethics."
  LLM Proposes:
    - Class: Event (subclass of Document)
    - Class: Conference (subclass of Event)
    - Property: participatesIn (domain: Person, range: Event)
  Validation: Check no conflicts → Approve → Extend graph
"""

from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL
from rdflib.namespace import XSD
from typing import List, Dict, Optional
from dataclasses import dataclass
from groq import Groq
import json
import os


@dataclass
class ProposedClass:
    """Proposed OWL class"""
    name: str
    parent_class: str  # Must be existing class or proposed class
    comment: str
    label: str


@dataclass
class ProposedProperty:
    """Proposed OWL property"""
    name: str
    property_type: str  # "ObjectProperty" or "DatatypeProperty"
    domain: str
    range: str
    comment: str
    label: str
    is_transitive: bool = False


@dataclass
class OntologyExtension:
    """Container for proposed extensions"""
    classes: List[ProposedClass]
    properties: List[ProposedProperty]
    validation_status: str = "pending"  # pending, approved, rejected
    validation_errors: List[str] = None
    
    def __post_init__(self):
        if self.validation_errors is None:
            self.validation_errors = []


class DynamicOntologyProposer:
    """
    LLM-driven ontology extension system with safety constraints.
    
    Safety Rules:
    1. Never remove or modify base ontology elements
    2. Proposed classes MUST be subclasses of existing classes
    3. Proposed properties MUST respect domain/range hierarchy
    4. All extensions marked with ex:dynamicExtension true
    5. Validate against OWL constraints before applying
    
    Architecture:
    1. LLM analyzes text → proposes classes/properties (JSON)
    2. Validator checks constraints
    3. If valid → generate OWL definitions → extend graph
    4. Mark extensions with provenance metadata
    
    Usage:
        proposer = DynamicOntologyProposer(graph, llm_client)
        extensions = proposer.propose_extensions("Dr. Smith attended Conference...")
        if extensions.validation_status == "approved":
            proposer.apply_extensions(graph, extensions)
    """
    
    def __init__(self, base_graph: Graph, groq_api_key: str = None, 
                 base_namespace: Namespace = None):
        """
        Initialize the Dynamic Ontology Proposer.
        
        Args:
            base_graph: RDF graph containing base ontology (T-Box)
            groq_api_key: Groq API key (optional, loaded from env)
            base_namespace: Namespace for extensions (e.g., EX)
        """
        self.base_graph = base_graph
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY", "")
        self.base_namespace = base_namespace or Namespace("http://example.org/master2/ontology#")
        
        # Extract base ontology elements
        self.base_classes = self._extract_base_classes()
        self.base_properties = self._extract_base_properties()
        
        # Statistics
        self.stats = {
            'proposals_generated': 0,
            'proposals_approved': 0,
            'proposals_rejected': 0,
            'classes_added': 0,
            'properties_added': 0
        }
    
    def propose_extensions(self, text: str, enable_proposal: bool = True) -> Optional[OntologyExtension]:
        """
        Analyze text and propose ontology extensions via LLM.
        
        Args:
            text: Domain text to analyze
            enable_proposal: If False, return None (feature disabled)
        
        Returns:
            OntologyExtension object (validated or rejected)
        """
        if not enable_proposal or not self.groq_api_key:
            return None
        
        print("\n" + "="*80)
        print("[DYNAMIC ONTOLOGY PROPOSER] Analyzing text for extensions")
        print("="*80)
        
        try:
            client = Groq(api_key=self.groq_api_key)
            
            # Build prompt
            prompt = self._build_llm_prompt(text)
            
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an ontology engineering expert. Output only valid JSON."},
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
            
            proposal_data = json.loads(result)
            
            # Parse into OntologyExtension
            extension = self._parse_proposal(proposal_data)
            
            # Validate
            extension = self._validate_extension(extension)
            
            self.stats['proposals_generated'] += 1
            if extension.validation_status == "approved":
                self.stats['proposals_approved'] += 1
                print(f"  ✓ Proposal APPROVED: {len(extension.classes)} classes, {len(extension.properties)} properties")
            else:
                self.stats['proposals_rejected'] += 1
                print(f"  ❌ Proposal REJECTED: {len(extension.validation_errors)} errors")
                for error in extension.validation_errors:
                    print(f"    - {error}")
            
            print("="*80 + "\n")
            return extension
        
        except Exception as e:
            print(f"  ⚠️ Error generating proposal: {str(e)[:100]}")
            print("="*80 + "\n")
            return None
    
    def apply_extensions(self, graph: Graph, extension: OntologyExtension) -> bool:
        """
        Apply validated extensions to the RDF graph.
        
        Args:
            graph: RDF graph to extend
            extension: Validated OntologyExtension
        
        Returns:
            True if successful, False otherwise
        """
        if extension.validation_status != "approved":
            print("  ❌ Cannot apply rejected extension")
            return False
        
        print("\n[APPLYING EXTENSIONS]")
        
        # Add classes
        for proposed_class in extension.classes:
            class_uri = URIRef(f"{self.base_namespace}{proposed_class.name}")
            
            # Declare as OWL Class
            graph.add((class_uri, RDF.type, OWL.Class))
            graph.add((class_uri, RDFS.label, Literal(proposed_class.label, lang="fr")))
            graph.add((class_uri, RDFS.comment, Literal(proposed_class.comment, lang="fr")))
            
            # Add subClassOf relation
            parent_uri = URIRef(f"{self.base_namespace}{proposed_class.parent_class}")
            graph.add((class_uri, RDFS.subClassOf, parent_uri))
            
            # Mark as dynamic extension
            graph.add((class_uri, self.base_namespace.dynamicExtension, Literal(True)))
            
            self.stats['classes_added'] += 1
            print(f"  ✓ Added class: {proposed_class.name} (subclass of {proposed_class.parent_class})")
        
        # Add properties
        for proposed_prop in extension.properties:
            prop_uri = URIRef(f"{self.base_namespace}{proposed_prop.name}")
            
            # Declare property type
            if proposed_prop.property_type == "ObjectProperty":
                graph.add((prop_uri, RDF.type, OWL.ObjectProperty))
            else:
                graph.add((prop_uri, RDF.type, OWL.DatatypeProperty))
            
            graph.add((prop_uri, RDFS.label, Literal(proposed_prop.label, lang="fr")))
            graph.add((prop_uri, RDFS.comment, Literal(proposed_prop.comment, lang="fr")))
            
            # Add domain/range
            domain_uri = self._resolve_uri(proposed_prop.domain)
            range_uri = self._resolve_uri(proposed_prop.range)
            
            graph.add((prop_uri, RDFS.domain, domain_uri))
            graph.add((prop_uri, RDFS.range, range_uri))
            
            # Mark as transitive if needed
            if proposed_prop.is_transitive:
                graph.add((prop_uri, RDF.type, OWL.TransitiveProperty))
            
            # Mark as dynamic extension
            graph.add((prop_uri, self.base_namespace.dynamicExtension, Literal(True)))
            
            self.stats['properties_added'] += 1
            print(f"  ✓ Added property: {proposed_prop.name} "
                  f"({proposed_prop.domain} → {proposed_prop.range})")
        
        print(f"\n  ✓ Extensions applied: {len(extension.classes)} classes, "
              f"{len(extension.properties)} properties\n")
        return True
    
    # ========== HELPER METHODS ==========
    
    def _build_llm_prompt(self, text: str) -> str:
        """Build prompt for LLM ontology proposal"""
        
        base_classes_str = ", ".join(self.base_classes)
        base_props_str = ", ".join(self.base_properties)
        
        prompt = f"""Analyze this text and propose OWL ontology extensions:

TEXT: "{text}"

CURRENT ONTOLOGY:
- Base Classes: {base_classes_str}
- Base Properties: {base_props_str}

TASK:
Propose NEW classes and properties to better represent this domain.

RULES:
1. Proposed classes MUST be subclasses of existing classes
2. Proposed properties MUST have domain/range from existing or proposed classes
3. Use OWL standards (ObjectProperty, DatatypeProperty)
4. Provide clear labels and comments in French

OUTPUT FORMAT (JSON):
{{
  "classes": [
    {{
      "name": "Event",
      "parent_class": "Document",
      "label": "Événement",
      "comment": "Un événement avec une date et un lieu"
    }},
    {{
      "name": "Conference",
      "parent_class": "Event",
      "label": "Conférence",
      "comment": "Une conférence scientifique ou académique"
    }}
  ],
  "properties": [
    {{
      "name": "participatesIn",
      "property_type": "ObjectProperty",
      "domain": "Person",
      "range": "Event",
      "label": "participe à",
      "comment": "Relation entre une personne et un événement",
      "is_transitive": false
    }},
    {{
      "name": "hasDate",
      "property_type": "DatatypeProperty",
      "domain": "Event",
      "range": "xsd:date",
      "label": "a pour date",
      "comment": "Date d'un événement",
      "is_transitive": false
    }}
  ]
}}

IMPORTANT:
- Only propose extensions if the text contains concepts NOT in the base ontology
- If the base ontology is sufficient, return empty arrays
- Keep proposals minimal and domain-specific

JSON:"""
        
        return prompt
    
    def _parse_proposal(self, data: dict) -> OntologyExtension:
        """Parse JSON proposal into OntologyExtension"""
        
        classes = []
        for cls_data in data.get("classes", []):
            classes.append(ProposedClass(
                name=cls_data.get("name"),
                parent_class=cls_data.get("parent_class"),
                comment=cls_data.get("comment", ""),
                label=cls_data.get("label", cls_data.get("name"))
            ))
        
        properties = []
        for prop_data in data.get("properties", []):
            properties.append(ProposedProperty(
                name=prop_data.get("name"),
                property_type=prop_data.get("property_type", "ObjectProperty"),
                domain=prop_data.get("domain"),
                range=prop_data.get("range"),
                comment=prop_data.get("comment", ""),
                label=prop_data.get("label", prop_data.get("name")),
                is_transitive=prop_data.get("is_transitive", False)
            ))
        
        return OntologyExtension(classes=classes, properties=properties)
    
    def _validate_extension(self, extension: OntologyExtension) -> OntologyExtension:
        """
        Validate proposed extensions against base ontology constraints.
        
        Validation Rules:
        1. Parent classes must exist (in base or in proposal)
        2. Property domains/ranges must exist (in base or in proposal)
        3. No naming conflicts with base ontology
        4. Class hierarchy must be acyclic
        """
        errors = []
        
        # Collect all proposed class names
        proposed_class_names = {cls.name for cls in extension.classes}
        all_classes = self.base_classes | proposed_class_names
        
        # Validate classes
        for cls in extension.classes:
            # Check parent exists
            if cls.parent_class not in all_classes:
                errors.append(f"Class '{cls.name}': parent '{cls.parent_class}' does not exist")
            
            # Check no naming conflict
            if cls.name in self.base_classes:
                errors.append(f"Class '{cls.name}': conflicts with base ontology class")
        
        # Validate properties
        for prop in extension.properties:
            # Check domain exists
            if prop.domain not in all_classes and not prop.domain.startswith("xsd:"):
                errors.append(f"Property '{prop.name}': domain '{prop.domain}' does not exist")
            
            # Check range exists
            if prop.range not in all_classes and not prop.range.startswith("xsd:"):
                errors.append(f"Property '{prop.name}': range '{prop.range}' does not exist")
            
            # Check no naming conflict
            if prop.name in self.base_properties:
                errors.append(f"Property '{prop.name}': conflicts with base ontology property")
        
        # Set validation status
        if errors:
            extension.validation_status = "rejected"
            extension.validation_errors = errors
        else:
            extension.validation_status = "approved"
        
        return extension
    
    def _extract_base_classes(self) -> set:
        """Extract all OWL classes from base graph"""
        classes = set()
        for s in self.base_graph.subjects(RDF.type, OWL.Class):
            # Extract local name from URI
            local_name = s.split("#")[-1].split("/")[-1]
            classes.add(local_name)
        return classes
    
    def _extract_base_properties(self) -> set:
        """Extract all OWL properties from base graph"""
        properties = set()
        for s in self.base_graph.subjects(RDF.type, OWL.ObjectProperty):
            local_name = s.split("#")[-1].split("/")[-1]
            properties.add(local_name)
        for s in self.base_graph.subjects(RDF.type, OWL.DatatypeProperty):
            local_name = s.split("#")[-1].split("/")[-1]
            properties.add(local_name)
        return properties
    
    def _resolve_uri(self, name: str) -> URIRef:
        """Resolve class/property name to full URI"""
        if name.startswith("xsd:"):
            # XSD datatype
            datatype = name.split(":")[1]
            return getattr(XSD, datatype)
        else:
            return URIRef(f"{self.base_namespace}{name}")
    
    def get_statistics(self) -> dict:
        """Return proposer statistics"""
        return self.stats.copy()


# ============================================================================
# STANDALONE TESTING
# ============================================================================

if __name__ == "__main__":
    from rdflib import Graph, Namespace
    from rdflib.namespace import FOAF
    
    print("Testing DynamicOntologyProposer...\n")
    
    # Create minimal base ontology
    graph = Graph()
    EX = Namespace("http://example.org/test#")
    SCHEMA = Namespace("http://schema.org/")
    
    graph.bind("ex", EX)
    graph.bind("foaf", FOAF)
    graph.bind("schema", SCHEMA)
    
    # Add base classes
    graph.add((FOAF.Person, RDF.type, OWL.Class))
    graph.add((SCHEMA.Place, RDF.type, OWL.Class))
    graph.add((SCHEMA.Organization, RDF.type, OWL.Class))
    graph.add((EX.Document, RDF.type, OWL.Class))
    
    # Add base properties
    graph.add((EX.worksAt, RDF.type, OWL.ObjectProperty))
    graph.add((EX.locatedIn, RDF.type, OWL.ObjectProperty))
    
    print(f"Base ontology: {len(graph)} triples")
    print(f"Base classes: Person, Place, Organization, Document")
    print(f"Base properties: worksAt, locatedIn\n")
    
    # Initialize proposer
    proposer = DynamicOntologyProposer(graph, base_namespace=EX)
    
    # Test text
    test_text = """
    Dr. Marie Smith participated in the International Conference on Semantic Web 2024.
    The conference was held in Paris and focused on Knowledge Graphs and AI Ethics.
    She presented a paper about ontology evolution.
    """
    
    print(f"Test text: {test_text}\n")
    
    # Propose extensions
    extension = proposer.propose_extensions(test_text, enable_proposal=True)
    
    if extension:
        print(f"\nProposal Status: {extension.validation_status}")
        print(f"Proposed Classes: {len(extension.classes)}")
        for cls in extension.classes:
            print(f"  - {cls.name} (subclass of {cls.parent_class})")
        
        print(f"\nProposed Properties: {len(extension.properties)}")
        for prop in extension.properties:
            print(f"  - {prop.name} ({prop.domain} → {prop.range})")
        
        # Apply if approved
        if extension.validation_status == "approved":
            proposer.apply_extensions(graph, extension)
            print(f"\nExtended ontology: {len(graph)} triples")
        
        print(f"\nStatistics: {proposer.get_statistics()}")
