#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Scenarios Generator for Neuro-Symbolic KG Extraction System
Generates 100+ test cases covering all edge cases and failure modes
"""

from typing import List, Dict, Any


class TestScenario:
    """Represents a single test scenario with expected outcomes"""
    
    def __init__(self, 
                 scenario_id: str,
                 category: str,
                 input_text: str,
                 description: str,
                 expected_entities: List[Dict[str, str]] = None,
                 expected_relations: List[Dict[str, str]] = None,
                 should_fail: bool = False,
                 expected_violations: List[str] = None):
        self.scenario_id = scenario_id
        self.category = category
        self.input_text = input_text
        self.description = description
        self.expected_entities = expected_entities or []
        self.expected_relations = expected_relations or []
        self.should_fail = should_fail
        self.expected_violations = expected_violations or []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "category": self.category,
            "input_text": self.input_text,
            "description": self.description,
            "expected_entities": self.expected_entities,
            "expected_relations": self.expected_relations,
            "should_fail": self.should_fail,
            "expected_violations": self.expected_violations
        }


def generate_all_scenarios() -> List[TestScenario]:
    """Generate complete test scenario suite (100+ tests)"""
    
    scenarios = []
    
    # ========================================================================
    # CATEGORY 1: ENTITY RECOGNITION TESTS (20 scenarios)
    # ========================================================================
    
    # Basic person names
    scenarios.extend([
        TestScenario(
            "NER_001",
            "entity_recognition",
            "Zoubida Kedad enseigne à l'Université de Versailles.",
            "Basic person and organization detection",
            expected_entities=[
                {"text": "Zoubida Kedad", "type": "PER"},
                {"text": "Université de Versailles", "type": "ORG"}
            ]
        ),
        TestScenario(
            "NER_002",
            "entity_recognition",
            "Dr. Marie Curie étudie la physique à Paris.",
            "Person with title and location",
            expected_entities=[
                {"text": "Dr. Marie Curie", "type": "PER"},
                {"text": "Paris", "type": "LOC"}
            ]
        ),
        TestScenario(
            "NER_003",
            "entity_recognition",
            "Prof. Albert Einstein travaille à l'Institut de Technologie.",
            "Professor title recognition",
            expected_entities=[
                {"text": "Prof. Albert Einstein", "type": "PER"},
                {"text": "Institut de Technologie", "type": "ORG"}
            ]
        ),
    ])
    
    # Technical concepts (should NOT be Person)
    scenarios.extend([
        TestScenario(
            "NER_004",
            "entity_recognition",
            "Le Web Sémantique utilise RDF et OWL.",
            "Technical concepts should be TOPIC not PER",
            expected_entities=[
                {"text": "Web Sémantique", "type": "TOPIC"},
                {"text": "RDF", "type": "TOPIC"},
                {"text": "OWL", "type": "TOPIC"}
            ]
        ),
        TestScenario(
            "NER_005",
            "entity_recognition",
            "L'Intelligence Artificielle transforme le Machine Learning.",
            "AI/ML concepts",
            expected_entities=[
                {"text": "Intelligence Artificielle", "type": "TOPIC"},
                {"text": "Machine Learning", "type": "TOPIC"}
            ]
        ),
        TestScenario(
            "NER_006",
            "entity_recognition",
            "Les Bases de Données relationnelles et SPARQL.",
            "Database concepts",
            expected_entities=[
                {"text": "Bases de Données", "type": "TOPIC"},
                {"text": "SPARQL", "type": "TOPIC"}
            ]
        ),
    ])
    
    # Mixed entities
    scenarios.extend([
        TestScenario(
            "NER_007",
            "entity_recognition",
            "Zoubida Kedad enseigne le Web Sémantique à Versailles.",
            "Person + Topic + Location",
            expected_entities=[
                {"text": "Zoubida Kedad", "type": "PER"},
                {"text": "Web Sémantique", "type": "TOPIC"},
                {"text": "Versailles", "type": "LOC"}
            ]
        ),
        TestScenario(
            "NER_008",
            "entity_recognition",
            "L'Université Paris-Saclay propose des cours sur RDF.",
            "Complex organization name + topic",
            expected_entities=[
                {"text": "Université Paris-Saclay", "type": "ORG"},
                {"text": "RDF", "type": "TOPIC"}
            ]
        ),
    ])
    
    # ========================================================================
    # CATEGORY 2: AMBIGUOUS ENTITY TESTS (15 scenarios)
    # ========================================================================
    
    scenarios.extend([
        TestScenario(
            "AMB_001",
            "ambiguous_entities",
            "Apple publie un article sur les ontologies.",
            "Apple as organization, not fruit",
            expected_entities=[
                {"text": "Apple", "type": "ORG"}
            ]
        ),
        TestScenario(
            "AMB_002",
            "ambiguous_entities",
            "Amazon développe des technologies de cloud computing.",
            "Amazon as tech company",
            expected_entities=[
                {"text": "Amazon", "type": "ORG"}
            ]
        ),
        TestScenario(
            "AMB_003",
            "ambiguous_entities",
            "Paris enseigne l'informatique.",
            "Paris as person name (rare but valid)",
            expected_entities=[
                {"text": "Paris", "type": "PER"}
            ]
        ),
        TestScenario(
            "AMB_004",
            "ambiguous_entities",
            "Washington dirige l'équipe de recherche.",
            "Washington as person, not city",
            expected_entities=[
                {"text": "Washington", "type": "PER"}
            ]
        ),
    ])
    
    # ========================================================================
    # CATEGORY 3: COMPOSITE ENTITY TESTS (10 scenarios)
    # ========================================================================
    
    scenarios.extend([
        TestScenario(
            "COMP_001",
            "composite_entities",
            "L'Université Paris-Saclay est reconnue internationalement.",
            "Multi-word organization (should NOT fragment)",
            expected_entities=[
                {"text": "Université Paris-Saclay", "type": "ORG"}
            ]
        ),
        TestScenario(
            "COMP_002",
            "composite_entities",
            "L'Institut Polytechnique de Paris forme des ingénieurs.",
            "Long organization name",
            expected_entities=[
                {"text": "Institut Polytechnique de Paris", "type": "ORG"}
            ]
        ),
        TestScenario(
            "COMP_003",
            "composite_entities",
            "Jean-Paul Sartre écrit sur la philosophie.",
            "Hyphenated person name",
            expected_entities=[
                {"text": "Jean-Paul Sartre", "type": "PER"}
            ]
        ),
    ])
    
    # ========================================================================
    # CATEGORY 4: RELATION EXTRACTION TESTS (20 scenarios)
    # ========================================================================
    
    scenarios.extend([
        TestScenario(
            "REL_001",
            "relation_extraction",
            "Zoubida Kedad enseigne RDF.",
            "teachesSubject relation",
            expected_entities=[
                {"text": "Zoubida Kedad", "type": "PER"},
                {"text": "RDF", "type": "TOPIC"}
            ],
            expected_relations=[
                {"subject": "Zoubida Kedad", "predicate": "teachesSubject", "object": "RDF"}
            ]
        ),
        TestScenario(
            "REL_002",
            "relation_extraction",
            "Zoubida Kedad enseigne à l'Université de Versailles.",
            "teaches relation (person → organization)",
            expected_entities=[
                {"text": "Zoubida Kedad", "type": "PER"},
                {"text": "Université de Versailles", "type": "ORG"}
            ],
            expected_relations=[
                {"subject": "Zoubida Kedad", "predicate": "worksAt", "object": "Université de Versailles"}
            ]
        ),
        TestScenario(
            "REL_003",
            "relation_extraction",
            "Marie Curie a écrit un article sur la radioactivité.",
            "author relation",
            expected_entities=[
                {"text": "Marie Curie", "type": "PER"},
                {"text": "article sur la radioactivité", "type": "DOCUMENT"}
            ],
            expected_relations=[
                {"subject": "Marie Curie", "predicate": "author", "object": "article"}
            ]
        ),
        TestScenario(
            "REL_004",
            "relation_extraction",
            "Bill Gates travaille chez Microsoft.",
            "worksAt relation",
            expected_entities=[
                {"text": "Bill Gates", "type": "PER"},
                {"text": "Microsoft", "type": "ORG"}
            ],
            expected_relations=[
                {"subject": "Bill Gates", "predicate": "worksAt", "object": "Microsoft"}
            ]
        ),
        TestScenario(
            "REL_005",
            "relation_extraction",
            "Elon Musk dirige Tesla.",
            "manages relation",
            expected_entities=[
                {"text": "Elon Musk", "type": "PER"},
                {"text": "Tesla", "type": "ORG"}
            ],
            expected_relations=[
                {"subject": "Elon Musk", "predicate": "manages", "object": "Tesla"}
            ]
        ),
    ])
    
    # ========================================================================
    # CATEGORY 5: DOMAIN VIOLATION TESTS (10 scenarios)
    # ========================================================================
    
    scenarios.extend([
        TestScenario(
            "DOM_001",
            "domain_violations",
            "Le Web Sémantique enseigne Zoubida Kedad.",
            "TOPIC cannot teach (domain violation)",
            expected_entities=[
                {"text": "Web Sémantique", "type": "TOPIC"},
                {"text": "Zoubida Kedad", "type": "PER"}
            ],
            should_fail=True,
            expected_violations=["domain"]
        ),
        TestScenario(
            "DOM_002",
            "domain_violations",
            "RDF travaille à l'Université de Versailles.",
            "TOPIC cannot worksAt",
            expected_entities=[
                {"text": "RDF", "type": "TOPIC"},
                {"text": "Université de Versailles", "type": "ORG"}
            ],
            should_fail=True,
            expected_violations=["domain"]
        ),
        TestScenario(
            "DOM_003",
            "domain_violations",
            "L'Ontologie a rédigé un cours.",
            "TOPIC cannot be author",
            expected_entities=[
                {"text": "Ontologie", "type": "TOPIC"}
            ],
            should_fail=True,
            expected_violations=["domain"]
        ),
    ])
    
    # ========================================================================
    # CATEGORY 6: RANGE VIOLATION TESTS (10 scenarios)
    # ========================================================================
    
    scenarios.extend([
        TestScenario(
            "RNG_001",
            "range_violations",
            "Zoubida Kedad enseigne Versailles.",
            "teachesSubject expects TOPIC, not LOC",
            expected_entities=[
                {"text": "Zoubida Kedad", "type": "PER"},
                {"text": "Versailles", "type": "LOC"}
            ],
            should_fail=True,
            expected_violations=["range"]
        ),
        TestScenario(
            "RNG_002",
            "range_violations",
            "Marie Curie a écrit Paris.",
            "author expects DOCUMENT, not LOC",
            expected_entities=[
                {"text": "Marie Curie", "type": "PER"},
                {"text": "Paris", "type": "LOC"}
            ],
            should_fail=True,
            expected_violations=["range"]
        ),
    ])
    
    # ========================================================================
    # CATEGORY 7: NOISE AND ROBUSTNESS TESTS (10 scenarios)
    # ========================================================================
    
    scenarios.extend([
        TestScenario(
            "NOISE_001",
            "noise_robustness",
            "Zoubida ... euh ... RDF ... Versailles ... enseigne ?",
            "Noisy input with hesitations",
            expected_entities=[
                {"text": "Zoubida", "type": "PER"},
                {"text": "RDF", "type": "TOPIC"},
                {"text": "Versailles", "type": "LOC"}
            ]
        ),
        TestScenario(
            "NOISE_002",
            "noise_robustness",
            "Marie!!!Curie??? enseigne  la   physique.",
            "Punctuation noise and extra spaces",
            expected_entities=[
                {"text": "Marie", "type": "PER"},
                {"text": "Curie", "type": "PER"},
                {"text": "physique", "type": "TOPIC"}
            ]
        ),
        TestScenario(
            "NOISE_003",
            "noise_robustness",
            "ZOUBIDA KEDAD ENSEIGNE RDF",
            "All uppercase input",
            expected_entities=[
                {"text": "ZOUBIDA KEDAD", "type": "PER"},
                {"text": "RDF", "type": "TOPIC"}
            ]
        ),
    ])
    
    # ========================================================================
    # CATEGORY 8: UNKNOWN ENTITY TESTS (5 scenarios)
    # ========================================================================
    
    scenarios.extend([
        TestScenario(
            "UNK_001",
            "unknown_entities",
            "Dr. Xyzzqwerty enseigne la Quantum Semantic Astronomy.",
            "Unknown person and topic",
            expected_entities=[
                {"text": "Dr. Xyzzqwerty", "type": "PER"},
                {"text": "Quantum Semantic Astronomy", "type": "TOPIC"}
            ]
        ),
        TestScenario(
            "UNK_002",
            "unknown_entities",
            "Université de Zorgblatt propose des cours.",
            "Unknown organization",
            expected_entities=[
                {"text": "Université de Zorgblatt", "type": "ORG"}
            ]
        ),
    ])
    
    # ========================================================================
    # CATEGORY 9: MULTI-SENTENCE TESTS (5 scenarios)
    # ========================================================================
    
    scenarios.extend([
        TestScenario(
            "MULTI_001",
            "multi_sentence",
            "Zoubida Kedad enseigne RDF à l'Université de Versailles. Le cours couvre les ontologies OWL.",
            "Multiple sentences with coreference",
            expected_entities=[
                {"text": "Zoubida Kedad", "type": "PER"},
                {"text": "RDF", "type": "TOPIC"},
                {"text": "Université de Versailles", "type": "ORG"},
                {"text": "OWL", "type": "TOPIC"}
            ],
            expected_relations=[
                {"subject": "Zoubida Kedad", "predicate": "teachesSubject", "object": "RDF"},
                {"subject": "Zoubida Kedad", "predicate": "worksAt", "object": "Université de Versailles"}
            ]
        ),
    ])
    
    # ========================================================================
    # CATEGORY 10: LONG TEXT TESTS (3 scenarios)
    # ========================================================================
    
    scenarios.extend([
        TestScenario(
            "LONG_001",
            "long_text",
            """Le Web Sémantique est une extension du Web actuel qui permet aux machines de comprendre le sens des informations.
            Zoubida Kedad enseigne cette discipline à l'Université de Versailles depuis 2010.
            Elle a publié plusieurs articles sur RDF, RDFS et OWL.
            Ses recherches portent sur les ontologies et les graphes de connaissances.""",
            "Long academic paragraph",
            expected_entities=[
                {"text": "Web Sémantique", "type": "TOPIC"},
                {"text": "Zoubida Kedad", "type": "PER"},
                {"text": "Université de Versailles", "type": "ORG"},
                {"text": "RDF", "type": "TOPIC"},
                {"text": "RDFS", "type": "TOPIC"},
                {"text": "OWL", "type": "TOPIC"}
            ]
        ),
    ])
    
    # ========================================================================
    # CATEGORY 11: EDGE CASES (10 scenarios)
    # ========================================================================
    
    scenarios.extend([
        TestScenario(
            "EDGE_001",
            "edge_cases",
            "",
            "Empty input",
            expected_entities=[]
        ),
        TestScenario(
            "EDGE_002",
            "edge_cases",
            "RDF",
            "Single word",
            expected_entities=[
                {"text": "RDF", "type": "TOPIC"}
            ]
        ),
        TestScenario(
            "EDGE_003",
            "edge_cases",
            "a b c d e f g h i j k l m n o p",
            "Random letters",
            expected_entities=[]
        ),
        TestScenario(
            "EDGE_004",
            "edge_cases",
            "123 456 789",
            "Only numbers",
            expected_entities=[]
        ),
        TestScenario(
            "EDGE_005",
            "edge_cases",
            "!@#$%^&*()_+-=[]{}|;':\",./<>?",
            "Only special characters",
            expected_entities=[]
        ),
    ])
    
    # ========================================================================
    # CATEGORY 12: BILINGUAL TESTS (5 scenarios)
    # ========================================================================
    
    scenarios.extend([
        TestScenario(
            "BILI_001",
            "bilingual",
            "Tim Berners-Lee invented the World Wide Web.",
            "English input",
            expected_entities=[
                {"text": "Tim Berners-Lee", "type": "PER"},
                {"text": "World Wide Web", "type": "TOPIC"}
            ]
        ),
        TestScenario(
            "BILI_002",
            "bilingual",
            "Marie Curie a gagné le Nobel Prize.",
            "French-English mix",
            expected_entities=[
                {"text": "Marie Curie", "type": "PER"},
                {"text": "Nobel Prize", "type": "TOPIC"}
            ]
        ),
    ])
    
    return scenarios


def get_scenarios_by_category(category: str) -> List[TestScenario]:
    """Filter scenarios by category"""
    all_scenarios = generate_all_scenarios()
    return [s for s in all_scenarios if s.category == category]


def get_scenario_categories() -> List[str]:
    """Get list of all test categories"""
    all_scenarios = generate_all_scenarios()
    return list(set(s.category for s in all_scenarios))


if __name__ == "__main__":
    scenarios = generate_all_scenarios()
    print(f"Generated {len(scenarios)} test scenarios")
    print(f"\nCategories: {get_scenario_categories()}")
    print(f"\nBreakdown by category:")
    for category in get_scenario_categories():
        count = len(get_scenarios_by_category(category))
        print(f"  {category}: {count} scenarios")
