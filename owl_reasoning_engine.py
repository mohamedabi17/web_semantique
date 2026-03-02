#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODULE 1 : OWL REASONING ENGINE (Raisonnement OWL Réel)

Implémentation d'un véritable raisonneur OWL avec owlrl.

Fonctionnalités :
=================
1. Validation domain/range (existante)
2. Raisonnement OWL avec owlrl + DeductiveClosure
3. Inférence de types via rdfs:subClassOf
4. Inférence de propriétés transitives
5. Détection d'inconsistances

Auteur : Implémentation académique Master 2 Web Sémantique
Date : 28 février 2026
Révision : Ajout raisonnement OWL réel (conformité audit)
"""

from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS, OWL
from typing import Tuple, List, Set, Optional, Dict

# Import conditionnel de owlrl
try:
    import owlrl
    from owlrl import DeductiveClosure, OWLRL_Semantics
    OWLRL_AVAILABLE = True
    print("[OWLReasoningEngine] ✅ owlrl disponible (raisonnement OWL complet)")
except ImportError:
    OWLRL_AVAILABLE = False
    print("[OWLReasoningEngine] ⚠️ owlrl non installé (fallback: validation syntaxique uniquement)")
    print("                      Install avec: pip install owlrl")


# ============================================================================
# CONFIGURATION
# ============================================================================

FOAF = Namespace("http://xmlns.com/foaf/0.1/")
SCHEMA = Namespace("http://schema.org/")
EX = Namespace("http://example.org/master2/ontology#")


# ============================================================================
# CLASSE PRINCIPALE : OWLReasoningEngine
# ============================================================================

class OWLReasoningEngine:
    """
    Moteur de raisonnement OWL avec validation et inférence.
    
    Architecture :
    --------------
    MODE 1 : Avec owlrl (raisonnement OWL complet)
        - DeductiveClosure avec OWLRL_Semantics
        - Inférence automatique de types
        - Inférence de propriétés transitives
        - Détection d'inconsistances
    
    MODE 2 : Sans owlrl (validation syntaxique uniquement)
        - Validation domain/range manuelle
        - Hiérarchie de classes simple
        - Pas d'inférence automatique
    
    Utilisation :
    -------------
    >>> graph = Graph()
    >>> # ... définir ontologie ...
    >>> reasoner = OWLReasoningEngine(graph)
    >>> reasoner.apply_reasoning()  # Applique raisonnement OWL
    >>> is_valid, error = reasoner.validate_triple(subject, predicate, obj)
    """
    
    def __init__(self, graph: Graph, verbose: bool = True):
        """
        Initialise le moteur de raisonnement.
        
        Args:
            graph: Graphe RDF contenant l'ontologie (T-Box + A-Box)
            verbose: Affiche logs détaillés
        """
        self.graph = graph
        self.verbose = verbose
        self.owlrl_available = OWLRL_AVAILABLE
        
        # Extraction des contraintes ontologiques (domain/range)
        self.property_domains: Dict[URIRef, Set[URIRef]] = {}
        self.property_ranges: Dict[URIRef, Set[URIRef]] = {}
        self.class_hierarchy: Dict[URIRef, Set[URIRef]] = {}
        
        self._extract_ontology_constraints()
        
        if self.verbose:
            print(f"[OWLReasoningEngine] Initialisé (mode: {'OWL complet' if OWLRL_AVAILABLE else 'syntaxique'})")
    
    def _extract_ontology_constraints(self):
        """
        Extrait les contraintes de l'ontologie (domain, range, subClassOf).
        
        Cette méthode parcourt le graphe pour identifier :
        - rdfs:domain (domaine des propriétés)
        - rdfs:range (portée des propriétés)
        - rdfs:subClassOf (hiérarchie de classes)
        """
        # Extraction des domaines (rdfs:domain)
        for prop, _, domain_class in self.graph.triples((None, RDFS.domain, None)):
            if isinstance(prop, URIRef) and isinstance(domain_class, URIRef):
                if prop not in self.property_domains:
                    self.property_domains[prop] = set()
                self.property_domains[prop].add(domain_class)
        
        # Extraction des portées (rdfs:range)
        for prop, _, range_class in self.graph.triples((None, RDFS.range, None)):
            if isinstance(prop, URIRef) and isinstance(range_class, URIRef):
                if prop not in self.property_ranges:
                    self.property_ranges[prop] = set()
                self.property_ranges[prop].add(range_class)
        
        # Extraction de la hiérarchie de classes (rdfs:subClassOf)
        for subclass, _, superclass in self.graph.triples((None, RDFS.subClassOf, None)):
            if isinstance(subclass, URIRef) and isinstance(superclass, URIRef):
                if subclass not in self.class_hierarchy:
                    self.class_hierarchy[subclass] = set()
                self.class_hierarchy[subclass].add(superclass)
        
        if self.verbose:
            print(f"  • {len(self.property_domains)} propriétés avec domain")
            print(f"  • {len(self.property_ranges)} propriétés avec range")
            print(f"  • {len(self.class_hierarchy)} relations rdfs:subClassOf")
    
    def apply_reasoning(self) -> int:
        """
        Applique le raisonnement OWL sur le graphe.
        
        Selon la disponibilité de owlrl :
        - Si disponible : DeductiveClosure avec OWLRL_Semantics
        - Sinon : Pas de raisonnement (validation syntaxique seulement)
        
        Returns:
            Nombre de triplets inférés
        """
        if not self.owlrl_available:
            if self.verbose:
                print("[OWLReasoningEngine] ⚠️ Raisonnement OWL ignoré (owlrl non disponible)")
            return 0
        
        # Comptage triplets avant raisonnement
        triplets_before = len(self.graph)
        
        if self.verbose:
            print(f"\n[OWLReasoningEngine] Application raisonnement OWL...")
            print(f"  • Triplets avant raisonnement : {triplets_before}")
        
        # Application de la fermeture déductive avec sémantique OWL-RL
        try:
            # DeductiveClosure applique les règles OWL-RL sur le graphe
            # Cela inclut :
            # - Inférence de types via rdfs:subClassOf
            # - Inférence de propriétés via rdfs:subPropertyOf
            # - Inférence de propriétés transitives (owl:TransitiveProperty)
            # - Inférence de propriétés symétriques (owl:SymmetricProperty)
            # - Inférence via owl:sameAs, owl:equivalentClass, etc.
            DeductiveClosure(OWLRL_Semantics).expand(self.graph)
            
            triplets_after = len(self.graph)
            inferred_count = triplets_after - triplets_before
            
            if self.verbose:
                print(f"  • Triplets après raisonnement : {triplets_after}")
                print(f"  ✅ {inferred_count} triplets inférés par raisonnement OWL")
            
            return inferred_count
        
        except Exception as e:
            if self.verbose:
                print(f"  ❌ Erreur lors du raisonnement OWL : {e}")
            return 0
    
    def validate_triple(
        self, 
        subject: URIRef, 
        predicate: URIRef, 
        obj: URIRef
    ) -> Tuple[bool, Optional[str]]:
        """
        Valide un triplet selon les contraintes ontologiques.
        
        Validation :
        1. Vérification domain (le sujet a le bon type)
        2. Vérification range (l'objet a le bon type)
        3. Gestion hiérarchie de classes (rdfs:subClassOf)
        
        Args:
            subject: Sujet du triplet (URI)
            predicate: Prédicat (propriété OWL)
            obj: Objet du triplet (URI)
            
        Returns:
            Tuple (is_valid, error_message)
            - (True, None) si valide
            - (False, "DOMAIN VIOLATION") si domain invalide
            - (False, "RANGE VIOLATION") si range invalide
        """
        # Récupération des types du sujet et de l'objet
        subject_types = self._get_entity_types(subject)
        object_types = self._get_entity_types(obj)
        
        # VALIDATION DU DOMAINE (rdfs:domain)
        if predicate in self.property_domains:
            required_domains = self.property_domains[predicate]
            
            if not self._is_compatible_type(subject_types, required_domains):
                if self.verbose:
                    print(f"  ❌ DOMAIN VIOLATION : {subject} n'est pas {required_domains}")
                return False, "DOMAIN VIOLATION"
        
        # VALIDATION DE LA PORTÉE (rdfs:range)
        if predicate in self.property_ranges:
            required_ranges = self.property_ranges[predicate]
            
            if not self._is_compatible_type(object_types, required_ranges):
                if self.verbose:
                    print(f"  ❌ RANGE VIOLATION : {obj} n'est pas {required_ranges}")
                return False, "RANGE VIOLATION"
        
        # Triplet valide
        return True, None
    
    def _get_entity_types(self, entity: URIRef) -> Set[URIRef]:
        """
        Récupère tous les types (rdf:type) d'une entité.
        
        Args:
            entity: URI de l'entité
            
        Returns:
            Ensemble des types (classes OWL)
        """
        types = set()
        for _, _, entity_type in self.graph.triples((entity, RDF.type, None)):
            if isinstance(entity_type, URIRef):
                types.add(entity_type)
        return types
    
    def _is_compatible_type(
        self, 
        entity_types: Set[URIRef], 
        required_types: Set[URIRef]
    ) -> bool:
        """
        Vérifie si les types de l'entité sont compatibles avec les types requis.
        
        Compatibilité :
        - Correspondance directe (entity_type ∈ required_types)
        - Hiérarchie de classes (entity_type sous-classe de required_type)
        
        Args:
            entity_types: Types actuels de l'entité
            required_types: Types requis par la contrainte
            
        Returns:
            True si compatible, False sinon
        """
        # Vérification directe
        if entity_types & required_types:  # Intersection non vide
            return True
        
        # Vérification via hiérarchie de classes (rdfs:subClassOf)
        for entity_type in entity_types:
            if self._is_subclass_of(entity_type, required_types):
                return True
        
        return False
    
    def _is_subclass_of(
        self, 
        subclass: URIRef, 
        superclasses: Set[URIRef]
    ) -> bool:
        """
        Vérifie si une classe est sous-classe d'une des superclasses.
        
        Parcours récursif de la hiérarchie rdfs:subClassOf.
        
        Args:
            subclass: Classe à vérifier
            superclasses: Ensemble de superclasses candidates
            
        Returns:
            True si subclass hérite d'une des superclasses
        """
        if subclass in superclasses:
            return True
        
        # Parcours récursif de la hiérarchie
        if subclass in self.class_hierarchy:
            for parent_class in self.class_hierarchy[subclass]:
                if self._is_subclass_of(parent_class, superclasses):
                    return True
        
        return False
    
    def get_inferred_types(self, entity: URIRef) -> Set[URIRef]:
        """
        Récupère tous les types inférés d'une entité (après raisonnement).
        
        Args:
            entity: URI de l'entité
            
        Returns:
            Ensemble des types (directs + inférés)
        """
        return self._get_entity_types(entity)
    
    def check_consistency(self) -> Tuple[bool, List[str]]:
        """
        Vérifie la cohérence du graphe RDF.
        
        Vérifie :
        - Absence de classes disjointes violées (owl:disjointWith)
        - Absence de contradictions de types
        
        Returns:
            Tuple (is_consistent, list_of_errors)
        """
        errors = []
        
        # Vérification des classes disjointes (owl:disjointWith)
        for class1, _, class2 in self.graph.triples((None, OWL.disjointWith, None)):
            if isinstance(class1, URIRef) and isinstance(class2, URIRef):
                # Chercher entités ayant les deux types
                for entity, _, _ in self.graph.triples((None, RDF.type, class1)):
                    if (entity, RDF.type, class2) in self.graph:
                        errors.append(
                            f"INCONSISTANCE : {entity} est à la fois {class1} et {class2} (classes disjointes)"
                        )
        
        is_consistent = len(errors) == 0
        
        if self.verbose:
            if is_consistent:
                print("[OWLReasoningEngine] ✅ Graphe cohérent (pas d'inconsistances)")
            else:
                print(f"[OWLReasoningEngine] ❌ {len(errors)} inconsistance(s) détectée(s)")
                for error in errors:
                    print(f"  • {error}")
        
        return is_consistent, errors


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def apply_owl_reasoning(graph: Graph, verbose: bool = True) -> Graph:
    """
    Fonction standalone pour appliquer le raisonnement OWL.
    
    Utilisation simple :
    >>> graph = Graph()
    >>> # ... définir ontologie ...
    >>> graph = apply_owl_reasoning(graph)
    
    Args:
        graph: Graphe RDF (ontologie + données)
        verbose: Affiche logs détaillés
        
    Returns:
        Graphe enrichi avec triplets inférés
    """
    reasoner = OWLReasoningEngine(graph, verbose=verbose)
    inferred_count = reasoner.apply_reasoning()
    
    if verbose:
        print(f"\n[apply_owl_reasoning] ✅ Raisonnement appliqué ({inferred_count} triplets inférés)")
    
    return graph


# ============================================================================
# TESTS UNITAIRES
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("TEST MODULE 1 : OWLReasoningEngine")
    print("="*80)
    
    # Création d'un graphe de test
    graph = Graph()
    graph.bind("ex", EX)
    graph.bind("foaf", FOAF)
    graph.bind("schema", SCHEMA)
    
    # Définition d'une ontologie simple
    print("\n[Test] Définition ontologie...")
    
    # Classes
    graph.add((FOAF.Person, RDF.type, OWL.Class))
    graph.add((EX.Student, RDF.type, OWL.Class))
    graph.add((EX.Student, RDFS.subClassOf, FOAF.Person))  # Student hérite de Person
    graph.add((EX.Document, RDF.type, OWL.Class))
    
    # Propriétés
    graph.add((EX.teaches, RDF.type, OWL.ObjectProperty))
    graph.add((EX.teaches, RDFS.domain, FOAF.Person))
    graph.add((EX.teaches, RDFS.range, EX.Document))
    
    # Instances
    graph.add((EX.Alice, RDF.type, EX.Student))  # Alice est un Student
    graph.add((EX.WebSemantique, RDF.type, EX.Document))
    
    print(f"  • {len(graph)} triplets définis")
    
    # Initialisation du raisonneur
    print("\n[Test] Initialisation OWLReasoningEngine...")
    reasoner = OWLReasoningEngine(graph, verbose=True)
    
    # Application du raisonnement
    print("\n[Test] Application raisonnement OWL...")
    inferred_count = reasoner.apply_reasoning()
    
    # Vérification des types inférés
    print("\n[Test] Vérification types inférés...")
    alice_types = reasoner.get_inferred_types(EX.Alice)
    print(f"  Types de Alice : {[str(t) for t in alice_types]}")
    
    # Test validation triplet
    print("\n[Test] Validation triplet...")
    is_valid, error = reasoner.validate_triple(EX.Alice, EX.teaches, EX.WebSemantique)
    print(f"  Alice teaches WebSemantique : {'✅ VALIDE' if is_valid else f'❌ INVALIDE ({error})'}")
    
    # Test cohérence
    print("\n[Test] Vérification cohérence...")
    is_consistent, errors = reasoner.check_consistency()
    print(f"  Graphe cohérent : {'✅ OUI' if is_consistent else f'❌ NON ({len(errors)} erreurs)'}")
    
    print("\n" + "="*80)
    print("✅ Tests terminés")
    print("="*80)
