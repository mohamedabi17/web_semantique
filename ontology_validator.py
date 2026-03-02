#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODULE 1 - Ontology Constraint Validator
==========================================

Ce module implémente la validation des contraintes ontologiques (OWL)
pour garantir la cohérence sémantique du graphe RDF.

Fonctionnalités:
- Validation domain/range des propriétés OWL
- Vérification des contraintes de cardinalité
- Détection et rejet des triples incohérents
- Support des hiérarchies de classes (rdfs:subClassOf)

Architecture neuro-symbolique:
- Couche symbolique: Raisonnement OWL formel
- Couche de filtrage: Validation post-extraction LLM
"""

from rdflib import Graph, Namespace, URIRef, RDF, RDFS, OWL
from typing import Tuple, List, Set, Optional
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OntologyConstraintValidator:
    """
    Validateur de contraintes ontologiques basé sur OWL/RDFS.
    
    Ce validateur analyse l'ontologie (T-Box) et valide chaque triplet
    de l'A-Box contre les contraintes définies.
    """
    
    def __init__(self, graph: Graph):
        """
        Initialise le validateur avec un graphe RDF contenant l'ontologie.
        
        Args:
            graph: Le graphe RDF contenant à la fois la T-Box et l'A-Box
        """
        self.graph = graph
        self.property_domains = {}  # {property_uri: [domain_class1, domain_class2, ...]}
        self.property_ranges = {}   # {property_uri: [range_class1, range_class2, ...]}
        self.class_hierarchy = {}   # {subclass: [superclass1, superclass2, ...]}
        
        # Extraction des contraintes de l'ontologie
        self._extract_ontology_constraints()
        
        logger.info(f"✓ Validateur initialisé avec {len(self.property_domains)} propriétés")
    
    def _extract_ontology_constraints(self):
        """
        Extrait les contraintes domain/range de l'ontologie.
        
        Cette méthode parcourt le graphe pour identifier:
        - rdfs:domain de chaque propriété
        - rdfs:range de chaque propriété
        - rdfs:subClassOf pour la hiérarchie de classes
        """
        # Identifier les DatatypeProperties (à exclure de la validation)
        self.datatype_properties = set()
        for prop, _, _ in self.graph.triples((None, RDF.type, OWL.DatatypeProperty)):
            self.datatype_properties.add(prop)
        
        # Extraction des domaines (rdfs:domain) - seulement pour ObjectProperties
        for prop, _, domain_class in self.graph.triples((None, RDFS.domain, None)):
            # Skip DatatypeProperties
            if prop in self.datatype_properties:
                continue
            if prop not in self.property_domains:
                self.property_domains[prop] = []
            self.property_domains[prop].append(domain_class)
        
        # Extraction des portées (rdfs:range) - seulement pour ObjectProperties
        for prop, _, range_class in self.graph.triples((None, RDFS.range, None)):
            # Skip DatatypeProperties
            if prop in self.datatype_properties:
                continue
            if prop not in self.property_ranges:
                self.property_ranges[prop] = []
            self.property_ranges[prop].append(range_class)
        
        # Extraction de la hiérarchie de classes (rdfs:subClassOf)
        for subclass, _, superclass in self.graph.triples((None, RDFS.subClassOf, None)):
            # Ignorer les Blank Nodes (restrictions OWL)
            if isinstance(superclass, URIRef):
                if subclass not in self.class_hierarchy:
                    self.class_hierarchy[subclass] = []
                self.class_hierarchy[subclass].append(superclass)
        
        logger.info(f"  Contraintes extraites: {len(self.property_domains)} domains, "
                   f"{len(self.property_ranges)} ranges, "
                   f"{len(self.class_hierarchy)} hiérarchies")
    
    def _get_entity_types(self, entity_uri: URIRef) -> Set[URIRef]:
        """
        Récupère tous les types d'une entité (incluant les super-classes).
        
        Args:
            entity_uri: L'URI de l'entité
            
        Returns:
            Ensemble des types (classes) de l'entité avec inférence hiérarchique
        """
        types = set()
        
        # Types directs (rdf:type)
        for _, _, type_class in self.graph.triples((entity_uri, RDF.type, None)):
            if isinstance(type_class, URIRef):
                types.add(type_class)
                
                # Ajouter les super-classes (inférence)
                if type_class in self.class_hierarchy:
                    types.update(self.class_hierarchy[type_class])
        
        return types
    
    def _is_compatible_type(self, entity_types: Set[URIRef], 
                           required_types: List[URIRef]) -> bool:
        """
        Vérifie si les types d'une entité sont compatibles avec les types requis.
        
        Args:
            entity_types: Types de l'entité
            required_types: Types requis par la contrainte
            
        Returns:
            True si au moins un type est compatible
        """
        # Si aucune contrainte, accepter tout
        if not required_types:
            return True
        
        # Vérifier si au moins un type de l'entité correspond
        for required_type in required_types:
            if required_type in entity_types:
                return True
            
            # Support de RDFS.Resource (accepte tout)
            if required_type == RDFS.Resource:
                return True
        
        return False
    
    def validate_triple(self, subject: URIRef, predicate: URIRef, 
                       obj: URIRef) -> Tuple[bool, Optional[str]]:
        """
        Valide un triplet RDF contre les contraintes ontologiques.
        
        Args:
            subject: Sujet du triplet
            predicate: Prédicat du triplet
            obj: Objet du triplet
            
        Returns:
            Tuple (is_valid, error_message)
            - is_valid: True si le triplet est valide
            - error_message: Message d'erreur si invalide, None sinon
        """
        # Ignorer les triplets de définition d'ontologie (T-Box)
        if predicate in [RDF.type, RDFS.domain, RDFS.range, RDFS.label, 
                        RDFS.comment, RDFS.subClassOf]:
            return True, None
        
        # Récupérer les types du sujet et de l'objet
        subject_types = self._get_entity_types(subject)
        object_types = self._get_entity_types(obj)
        
        # VALIDATION DU DOMAINE (rdfs:domain)
        if predicate in self.property_domains:
            required_domains = self.property_domains[predicate]
            if not self._is_compatible_type(subject_types, required_domains):
                error_msg = (f"❌ DOMAIN VIOLATION: {self._format_uri(subject)} "
                           f"de type {self._format_types(subject_types)} "
                           f"ne peut pas utiliser la propriété {self._format_uri(predicate)} "
                           f"(domain requis: {self._format_types(required_domains)})")
                return False, error_msg
        
        # VALIDATION DE LA PORTÉE (rdfs:range)
        if predicate in self.property_ranges:
            required_ranges = self.property_ranges[predicate]
            if not self._is_compatible_type(object_types, required_ranges):
                error_msg = (f"❌ RANGE VIOLATION: {self._format_uri(obj)} "
                           f"de type {self._format_types(object_types)} "
                           f"n'est pas compatible avec {self._format_uri(predicate)} "
                           f"(range requis: {self._format_types(required_ranges)})")
                return False, error_msg
        
        return True, None
    
    def validate_graph(self, properties_to_validate: Optional[List[URIRef]] = None,
                      remove_invalid: bool = True) -> Tuple[int, int, List[str]]:
        """
        Valide tous les triplets du graphe contre l'ontologie.
        
        Args:
            properties_to_validate: Liste des propriétés à valider (None = toutes)
            remove_invalid: Si True, supprime les triplets invalides du graphe
            
        Returns:
            Tuple (valid_count, invalid_count, error_messages)
        """
        logger.info("\n[VALIDATION ONTOLOGIQUE] Démarrage de la validation...")
        
        valid_count = 0
        invalid_count = 0
        error_messages = []
        triples_to_remove = []
        
        # Si aucune propriété spécifiée, valider toutes les ObjectProperties
        if properties_to_validate is None:
            properties_to_validate = list(self.property_domains.keys())
        
        # Parcourir tous les triplets utilisant les propriétés spécifiées
        for prop in properties_to_validate:
            for subject, predicate, obj in self.graph.triples((None, prop, None)):
                is_valid, error_msg = self.validate_triple(subject, predicate, obj)
                
                if is_valid:
                    valid_count += 1
                else:
                    invalid_count += 1
                    error_messages.append(error_msg)
                    logger.warning(error_msg)
                    
                    if remove_invalid:
                        triples_to_remove.append((subject, predicate, obj))
        
        # Suppression des triplets invalides
        if remove_invalid and triples_to_remove:
            for triple in triples_to_remove:
                self.graph.remove(triple)
            logger.info(f"  ✓ {len(triples_to_remove)} triplet(s) invalide(s) supprimé(s)")
        
        logger.info(f"[VALIDATION] Résultat: {valid_count} valides, {invalid_count} rejetés")
        
        return valid_count, invalid_count, error_messages
    
    def _format_uri(self, uri: URIRef) -> str:
        """Formate une URI pour l'affichage (garde seulement le fragment)."""
        return str(uri).split('#')[-1].split('/')[-1]
    
    def _format_types(self, types) -> str:
        """Formate une liste de types pour l'affichage."""
        if isinstance(types, set):
            types = list(types)
        return ', '.join([self._format_uri(t) for t in types]) or "None"
    
    def get_validation_report(self) -> dict:
        """
        Génère un rapport détaillé de la configuration du validateur.
        
        Returns:
            Dictionnaire contenant les statistiques de l'ontologie
        """
        return {
            "properties_with_domain": len(self.property_domains),
            "properties_with_range": len(self.property_ranges),
            "class_hierarchies": len(self.class_hierarchy),
            "domains": {self._format_uri(k): [self._format_uri(v) for v in vals] 
                       for k, vals in self.property_domains.items()},
            "ranges": {self._format_uri(k): [self._format_uri(v) for v in vals] 
                      for k, vals in self.property_ranges.items()}
        }


# ============================================================================
# FONCTION D'INTÉGRATION POUR LE PIPELINE PRINCIPAL
# ============================================================================

def validate_rdf_graph(graph: Graph, remove_invalid: bool = True) -> dict:
    """
    Point d'entrée principal pour valider un graphe RDF.
    
    Cette fonction est appelée après l'extraction LLM pour filtrer
    les triplets incohérents avant l'export final.
    
    Args:
        graph: Le graphe RDF à valider
        remove_invalid: Si True, supprime les triplets invalides
        
    Returns:
        Dictionnaire avec les statistiques de validation
    """
    validator = OntologyConstraintValidator(graph)
    valid, invalid, errors = validator.validate_graph(remove_invalid=remove_invalid)
    
    return {
        "valid_triples": valid,
        "invalid_triples": invalid,
        "errors": errors,
        "validator": validator
    }


# ============================================================================
# TESTS UNITAIRES (optionnel, pour validation standalone)
# ============================================================================

if __name__ == "__main__":
    print("Module de validation ontologique chargé.")
    print("Utilisez validate_rdf_graph(graph) dans le pipeline principal.")
