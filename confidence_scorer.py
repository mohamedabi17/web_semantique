#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODULE CONFIDENCE SCORING : Système de Confiance pour Triplets RDF

Gestion des scores de confiance pour :
- Entités extraites (spaCy, heuristiques)
- Relations extraites (LLM, patterns)
- Triplets inférés (raisonnement)

Auteur : Implémentation académique Master 2 Web Sémantique
Date : 28 février 2026
Révision : Système de confiance complet
"""

from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS, OWL
from rdflib.namespace import XSD, DC
from typing import Dict, Tuple, Optional


# ============================================================================
# CONFIGURATION
# ============================================================================

EX = Namespace("http://example.org/master2/ontology#")
DATA = Namespace("http://example.org/master2/data#")


# ============================================================================
# CLASSE : ConfidenceScorer
# ============================================================================

class ConfidenceScorer:
    """
    Système de scoring de confiance pour triplets RDF.
    
    Scores par source :
    -------------------
    - spaCy NER (entité composée ≥2 tokens) : 0.90
    - spaCy NER (entité simple) : 0.70
    - EntityRuler (patterns) : 0.95
    - Heuristique PROPN : 0.75
    - LLM (relation extraction) : 0.85
    - Raisonnement OWL (inférence) : 1.00
    
    Métadonnées ajoutées :
    ----------------------
    - ex:confidence (score 0.0 à 1.0)
    - dc:source (provenance)
    - ex:extractionMethod (méthode utilisée)
    
    Utilisation :
    -------------
    >>> scorer = ConfidenceScorer(graph)
    >>> scorer.add_entity_confidence(entity_uri, 0.90, source="spacy_ner")
    >>> scorer.add_relation_confidence(subj, pred, obj, 0.85, source="llm")
    """
    
    def __init__(self, graph: Graph, verbose: bool = True):
        """
        Initialise le système de scoring.
        
        Args:
            graph: Graphe RDF où ajouter les métadonnées
            verbose: Affiche logs détaillés
        """
        self.graph = graph
        self.verbose = verbose
        
        # Définition de la propriété de confiance dans l'ontologie
        self._define_confidence_property()
        
        if self.verbose:
            print("[ConfidenceScorer] ✅ Initialisé")
    
    def _define_confidence_property(self):
        """
        Définit la propriété ex:confidence dans l'ontologie.
        
        Ajoute :
        - ex:confidence rdf:type owl:DatatypeProperty
        - ex:confidence rdfs:domain rdf:Statement (pour réification)
        - ex:confidence rdfs:range xsd:float
        """
        # Déclaration de la propriété
        self.graph.add((EX.confidence, RDF.type, OWL.DatatypeProperty))
        self.graph.add((EX.confidence, RDFS.label, Literal("Confidence Score", lang="en")))
        self.graph.add((EX.confidence, RDFS.comment, 
                       Literal("Score de confiance d'une assertion (0.0 à 1.0)", lang="fr")))
        
        # Domaine : rdf:Statement (triplets réifiés)
        self.graph.add((EX.confidence, RDFS.domain, RDF.Statement))
        
        # Portée : xsd:float
        self.graph.add((EX.confidence, RDFS.range, XSD.float))
        
        # Propriété ex:extractionMethod
        self.graph.add((EX.extractionMethod, RDF.type, OWL.DatatypeProperty))
        self.graph.add((EX.extractionMethod, RDFS.domain, RDF.Statement))
        self.graph.add((EX.extractionMethod, RDFS.range, XSD.string))
    
    def add_entity_confidence(
        self, 
        entity_uri: URIRef, 
        confidence: float,
        source: str = "unknown"
    ):
        """
        Ajoute un score de confiance à une entité.
        
        Args:
            entity_uri: URI de l'entité
            confidence: Score de confiance (0.0 à 1.0)
            source: Source d'extraction (ex: "spacy_ner", "propn_heuristic")
        """
        # Ajout de la propriété ex:confidence directement sur l'entité
        self.graph.add((entity_uri, EX.confidence, Literal(confidence, datatype=XSD.float)))
        self.graph.add((entity_uri, EX.extractionMethod, Literal(source, datatype=XSD.string)))
        
        if self.verbose:
            print(f"  [Confidence] {entity_uri.split('#')[-1]} : {confidence:.2f} (source: {source})")
    
    def add_relation_confidence(
        self,
        subject: URIRef,
        predicate: URIRef,
        obj: URIRef,
        confidence: float,
        source: str = "unknown",
        use_reification: bool = True
    ):
        """
        Ajoute un score de confiance à une relation (triplet).
        
        Stratégie :
        - Si use_reification=True : utilise réification RDF
        - Sinon : ajoute métadonnées directement (non standard)
        
        Args:
            subject: Sujet du triplet
            predicate: Prédicat (propriété)
            obj: Objet du triplet
            confidence: Score de confiance (0.0 à 1.0)
            source: Source d'extraction (ex: "llm", "rule_based")
            use_reification: Utilise réification RDF (recommandé)
        """
        if use_reification:
            # Création d'un nœud de réification
            statement_uri = self._create_reified_statement(subject, predicate, obj)
            
            # Ajout métadonnées sur le statement
            self.graph.add((statement_uri, EX.confidence, Literal(confidence, datatype=XSD.float)))
            self.graph.add((statement_uri, EX.extractionMethod, Literal(source, datatype=XSD.string)))
            self.graph.add((statement_uri, DC.source, Literal(source, datatype=XSD.string)))
            
            if self.verbose:
                print(f"  [Confidence] {subject.split('#')[-1]} --{predicate.split('#')[-1]}--> {obj.split('#')[-1]} : {confidence:.2f} (source: {source})")
        else:
            # Mode non-réifié (non recommandé, mais plus simple)
            # Ajoute simplement le triplet avec métadonnées dans un graphe nommé (nécessite quad store)
            pass
    
    def _create_reified_statement(
        self,
        subject: URIRef,
        predicate: URIRef,
        obj: URIRef
    ) -> URIRef:
        """
        Crée un nœud de réification pour un triplet.
        
        Structure RDF créée :
        ---------------------
        _:statement1 rdf:type rdf:Statement
        _:statement1 rdf:subject <subject>
        _:statement1 rdf:predicate <predicate>
        _:statement1 rdf:object <object>
        
        Args:
            subject: Sujet du triplet
            predicate: Prédicat
            obj: Objet
            
        Returns:
            URI du nœud de réification
        """
        # Génération d'une URI unique pour le statement
        statement_uri = DATA[f"statement_{hash((subject, predicate, obj)) & 0xFFFFFF}"]
        
        # Déclaration du type : rdf:Statement
        self.graph.add((statement_uri, RDF.type, RDF.Statement))
        
        # Décomposition du triplet
        self.graph.add((statement_uri, RDF.subject, subject))
        self.graph.add((statement_uri, RDF.predicate, predicate))
        self.graph.add((statement_uri, RDF.object, obj))
        
        return statement_uri
    
    def get_entity_confidence(self, entity_uri: URIRef) -> Optional[float]:
        """
        Récupère le score de confiance d'une entité.
        
        Args:
            entity_uri: URI de l'entité
            
        Returns:
            Score de confiance (ou None si absent)
        """
        for _, _, conf_lit in self.graph.triples((entity_uri, EX.confidence, None)):
            if isinstance(conf_lit, Literal):
                return float(conf_lit)
        return None
    
    def get_relation_confidence(
        self,
        subject: URIRef,
        predicate: URIRef,
        obj: URIRef
    ) -> Optional[float]:
        """
        Récupère le score de confiance d'une relation.
        
        Args:
            subject: Sujet du triplet
            predicate: Prédicat
            obj: Objet
            
        Returns:
            Score de confiance (ou None si absent)
        """
        # Chercher le statement réifié correspondant
        for stmt, _, _ in self.graph.triples((None, RDF.type, RDF.Statement)):
            # Vérifier que c'est bien notre triplet
            if (stmt, RDF.subject, subject) in self.graph and \
               (stmt, RDF.predicate, predicate) in self.graph and \
               (stmt, RDF.object, obj) in self.graph:
                # Récupérer la confiance
                for _, _, conf_lit in self.graph.triples((stmt, EX.confidence, None)):
                    if isinstance(conf_lit, Literal):
                        return float(conf_lit)
        return None
    
    def filter_low_confidence_entities(self, threshold: float = 0.5) -> int:
        """
        Supprime les entités avec une confiance < threshold.
        
        Args:
            threshold: Seuil minimum de confiance
            
        Returns:
            Nombre d'entités supprimées
        """
        entities_to_remove = []
        
        for entity, _, conf_lit in self.graph.triples((None, EX.confidence, None)):
            if isinstance(conf_lit, Literal):
                confidence = float(conf_lit)
                if confidence < threshold:
                    entities_to_remove.append(entity)
        
        # Suppression des entités et de tous leurs triplets
        for entity in entities_to_remove:
            # Supprimer tous les triplets où l'entité est sujet
            for s, p, o in list(self.graph.triples((entity, None, None))):
                self.graph.remove((s, p, o))
            
            # Supprimer tous les triplets où l'entité est objet
            for s, p, o in list(self.graph.triples((None, None, entity))):
                self.graph.remove((s, p, o))
        
        if self.verbose:
            print(f"[ConfidenceScorer] 🗑️ {len(entities_to_remove)} entités supprimées (confiance < {threshold})")
        
        return len(entities_to_remove)
    
    def get_confidence_statistics(self) -> Dict[str, float]:
        """
        Calcule des statistiques sur les scores de confiance.
        
        Returns:
            Dictionnaire avec min, max, moyenne
        """
        confidences = []
        
        for _, _, conf_lit in self.graph.triples((None, EX.confidence, None)):
            if isinstance(conf_lit, Literal):
                confidences.append(float(conf_lit))
        
        if not confidences:
            return {"min": 0.0, "max": 0.0, "mean": 0.0, "count": 0}
        
        return {
            "min": min(confidences),
            "max": max(confidences),
            "mean": sum(confidences) / len(confidences),
            "count": len(confidences)
        }


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def add_inference_confidence(
    graph: Graph,
    subject: URIRef,
    predicate: URIRef,
    obj: URIRef,
    inference_type: str = "owl_reasoning"
):
    """
    Ajoute un score de confiance maximal (1.0) pour un triplet inféré.
    
    Args:
        graph: Graphe RDF
        subject: Sujet du triplet inféré
        predicate: Prédicat
        obj: Objet
        inference_type: Type d'inférence (ex: "owl_reasoning", "transitive")
    """
    scorer = ConfidenceScorer(graph, verbose=False)
    scorer.add_relation_confidence(
        subject, predicate, obj,
        confidence=1.0,
        source=inference_type
    )


# ============================================================================
# TESTS UNITAIRES
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("TEST MODULE CONFIDENCE SCORING")
    print("="*80)
    
    # Création d'un graphe de test
    graph = Graph()
    graph.bind("ex", EX)
    graph.bind("data", DATA)
    graph.bind("foaf", Namespace("http://xmlns.com/foaf/0.1/"))
    
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    
    # Initialisation du scorer
    print("\n[Test] Initialisation ConfidenceScorer...")
    scorer = ConfidenceScorer(graph, verbose=True)
    
    # Ajout d'entités avec confiance
    print("\n[Test] Ajout entités avec confiance...")
    alice_uri = DATA["alice"]
    graph.add((alice_uri, RDF.type, FOAF.Person))
    scorer.add_entity_confidence(alice_uri, 0.90, source="spacy_ner")
    
    bob_uri = DATA["bob"]
    graph.add((bob_uri, RDF.type, FOAF.Person))
    scorer.add_entity_confidence(bob_uri, 0.75, source="propn_heuristic")
    
    # Ajout d'une relation avec confiance
    print("\n[Test] Ajout relation avec confiance...")
    graph.add((alice_uri, FOAF.knows, bob_uri))
    scorer.add_relation_confidence(alice_uri, FOAF.knows, bob_uri, 0.85, source="llm")
    
    # Récupération confiance
    print("\n[Test] Récupération confiance...")
    alice_conf = scorer.get_entity_confidence(alice_uri)
    print(f"  Alice confidence : {alice_conf}")
    
    knows_conf = scorer.get_relation_confidence(alice_uri, FOAF.knows, bob_uri)
    print(f"  Alice knows Bob confidence : {knows_conf}")
    
    # Statistiques
    print("\n[Test] Statistiques confiance...")
    stats = scorer.get_confidence_statistics()
    print(f"  Min: {stats['min']:.2f}, Max: {stats['max']:.2f}, Mean: {stats['mean']:.2f}, Count: {stats['count']}")
    
    # Filtrage
    print("\n[Test] Filtrage entités faible confiance...")
    removed = scorer.filter_low_confidence_entities(threshold=0.80)
    print(f"  {removed} entités supprimées")
    
    print("\n" + "="*80)
    print("✅ Tests terminés")
    print("="*80)
