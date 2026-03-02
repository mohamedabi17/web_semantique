#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SUITE DE TESTS COMPLÈTE - ÉVALUATION ACADÉMIQUE
================================================

6 Catégories de tests :
1️⃣ Tests NER (Module 0++)
2️⃣ Tests Mapping Verbes → OWL
3️⃣ Tests Domain/Range
4️⃣ Tests Raisonnement OWL
5️⃣ Tests Robustesse LLM
6️⃣ Tests Confiance & Réification

Auteur : Évaluation Master 2 Web Sémantique
Date : 2 mars 2026
"""

import sys
import os
import time
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple, Any
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import spacy
from rdflib import Graph, Namespace, URIRef, RDF, RDFS, OWL, Literal
from rdflib.namespace import FOAF

# Imports des modules du système
from hybrid_ner_module import HybridNERModule
from owl_reasoning_engine import apply_owl_reasoning
from confidence_scorer import ConfidenceScorer

# Namespaces
EX = Namespace("http://example.org/master2/ontology#")
DATA = Namespace("http://example.org/master2/data#")
SCHEMA = Namespace("http://schema.org/")


class TestResult:
    """Résultat d'un test unitaire"""
    def __init__(self, test_id: str, category: str, name: str):
        self.test_id = test_id
        self.category = category
        self.name = name
        self.status = "PENDING"
        self.passed = False
        self.metrics = {}
        self.observations = []
        self.execution_time = 0.0
        self.errors = []
    
    def to_dict(self):
        return {
            "test_id": self.test_id,
            "category": self.category,
            "name": self.name,
            "status": self.status,
            "passed": self.passed,
            "metrics": self.metrics,
            "observations": self.observations,
            "execution_time": self.execution_time,
            "errors": self.errors
        }


class TestSuite:
    """Suite de tests complète"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.nlp = None
        
    def setup(self):
        """Initialisation des composants"""
        print("\n" + "="*80)
        print("🔧 INITIALISATION DES COMPOSANTS")
        print("="*80)
        
        # Charger spaCy
        print("  📦 Chargement spaCy fr_core_news_sm...")
        self.nlp = spacy.load("fr_core_news_sm")
        
        print("  ✅ Initialisation terminée\n")
    
    def extract_kg(self, text: str) -> Tuple[Graph, Dict]:
        """
        Extrait un graphe de connaissances du texte via le script principal
        
        Returns:
            (graph, metrics) : graphe RDF + métriques
        """
        start_time = time.time()
        
        # Créer fichier temporaire
        temp_input = Path("tests/temp_input.txt")
        temp_output = Path("outputs/temp_output.ttl")
        
        temp_input.write_text(text, encoding='utf-8')
        
        # Exécuter pipeline principal
        result = subprocess.run(
            [sys.executable, "kg_extraction_semantic_web.py"],
            stdin=open(temp_input),
            capture_output=True,
            text=True
        )
        
        # Charger graphe résultant
        graph = Graph()
        if temp_output.exists():
            graph.parse(temp_output, format="turtle")
        
        execution_time = time.time() - start_time
        
        # Métriques
        metrics = {
            "triples_total": len(graph),
            "execution_time": execution_time,
            "stdout_lines": len(result.stdout.splitlines())
        }
        
        # Nettoyer
        if temp_input.exists():
            temp_input.unlink()
        
        return graph, metrics
    
    # ========================================================================
    # 1️⃣ TESTS MODULE 0++ (NER HYBRIDE)
    # ========================================================================
    
    def test_01_ambiguite_lexicale(self):
        """Test 1 : Ambiguïté lexicale (Apple = entreprise ou fruit ?)"""
        result = TestResult("TEST_01", "1_NER", "Ambiguïté lexicale")
        print("\n" + "─"*80)
        print("🧪 TEST 01 : Ambiguïté lexicale (Apple)")
        print("─"*80)
        
        try:
            text = "Apple publie un article sur RDF."
            graph, metrics = self.extract_kg(text, verbose=False)
            
            # Vérifier entités détectées
            entities_query = """
            SELECT ?entity ?type WHERE {
                ?entity rdf:type ?type .
                FILTER(STRSTARTS(STR(?entity), "http://example.org/master2/data#"))
            }
            """
            entities_found = list(graph.query(entities_query))
            
            result.metrics = metrics
            result.metrics["entities_found"] = len(entities_found)
            
            # Analyser Apple
            apple_found = False
            apple_type = None
            
            for entity_uri, entity_type in entities_found:
                entity_label = str(entity_uri).split('#')[-1]
                if "Apple" in entity_label or "apple" in entity_label.lower():
                    apple_found = True
                    apple_type = str(entity_type)
                    result.observations.append(f"Apple détecté comme : {apple_type}")
            
            if not apple_found:
                result.observations.append("⚠️  Apple non détecté comme entité")
            
            # Vérification cohérence
            if apple_type and "Organization" in apple_type:
                result.observations.append("✅ Apple correctement typé comme Organisation")
                result.passed = True
            elif apple_type:
                result.observations.append(f"⚠️  Type ambigu : {apple_type}")
                result.passed = False
            else:
                result.observations.append("❌ Apple non typé")
                result.passed = False
            
            result.status = "COMPLETED"
            
        except Exception as e:
            result.status = "ERROR"
            result.errors.append(str(e))
            result.passed = False
        
        self.results.append(result)
        return result
    
    def test_02_entites_imbriquees(self):
        """Test 2 : Entités imbriquées (Université Paris-Saclay)"""
        result = TestResult("TEST_02", "1_NER", "Entités imbriquées")
        print("\n" + "─"*80)
        print("🧪 TEST 02 : Entités imbriquées (Université Paris-Saclay)")
        print("─"*80)
        
        try:
            text = "Université Paris-Saclay enseigne le Web Sémantique."
            
            # Extraction NER seulement
            ner_module = HybridNERModule(
                self.nlp, 
                confidence_threshold=0.5,
                ontology_graph=self.graph,
                enable_validation=True
            )
            entities = ner_module.extract(text, verbose=False)
            
            result.metrics["entities_detected"] = len(entities)
            
            # Vérifier présence Université Paris-Saclay
            entity_names = [ent[0] for ent in entities]
            
            has_full = "Université Paris-Saclay" in entity_names
            has_paris = "Paris" in entity_names
            has_saclay = "Saclay" in entity_names or "Paris-Saclay" in entity_names
            
            result.observations.append(f"Entités détectées : {entity_names}")
            
            if has_full and not (has_paris or (has_saclay and not has_full)):
                result.observations.append("✅ 'Université Paris-Saclay' détecté comme entité unique")
                result.passed = True
            elif has_paris or (has_saclay and not has_full):
                result.observations.append("❌ Entité fragmentée en sous-parties")
                result.passed = False
            else:
                result.observations.append("⚠️  'Université Paris-Saclay' non détecté")
                result.passed = False
            
            result.status = "COMPLETED"
            
        except Exception as e:
            result.status = "ERROR"
            result.errors.append(str(e))
            result.passed = False
        
        self.results.append(result)
        return result
    
    def test_03_entite_hors_ontologie(self):
        """Test 3 : Entité non présente dans ontologie"""
        result = TestResult("TEST_03", "1_NER", "Entité hors ontologie")
        print("\n" + "─"*80)
        print("🧪 TEST 03 : Entité hors ontologie (Dr. Xyzzq)")
        print("─"*80)
        
        try:
            text = "Dr. Xyzzq enseigne Astro-Sémantique Quantique."
            graph, metrics = self.extract_kg(text, verbose=False)
            
            result.metrics = metrics
            
            # Vérifier si nouvelles classes créées
            classes_query = """
            SELECT ?class WHERE {
                ?class rdf:type owl:Class .
                FILTER(STRSTARTS(STR(?class), "http://example.org/master2/data#"))
            }
            """
            custom_classes = list(graph.query(classes_query))
            
            result.metrics["custom_classes_created"] = len(custom_classes)
            
            if len(custom_classes) == 0:
                result.observations.append("✅ Aucune classe personnalisée créée (bon comportement)")
                result.passed = True
            else:
                result.observations.append(f"⚠️  {len(custom_classes)} classe(s) créée(s) dynamiquement")
                result.passed = False
            
            # Vérifier entités
            entities_query = """
            SELECT ?entity ?type WHERE {
                ?entity rdf:type ?type .
                FILTER(STRSTARTS(STR(?entity), "http://example.org/master2/data#"))
            }
            """
            entities_found = list(graph.query(entities_query))
            result.observations.append(f"Entités créées : {len(entities_found)}")
            
            result.status = "COMPLETED"
            
        except Exception as e:
            result.status = "ERROR"
            result.errors.append(str(e))
            result.passed = False
        
        self.results.append(result)
        return result
    
    # ========================================================================
    # 2️⃣ TESTS MAPPING VERBES → PROPRIÉTÉS OWL
    # ========================================================================
    
    def test_04_synonymes_verbaux(self):
        """Test 4 : Synonymes verbaux (donne un cours vs enseigne)"""
        result = TestResult("TEST_04", "2_MAPPING", "Synonymes verbaux")
        print("\n" + "─"*80)
        print("🧪 TEST 04 : Synonymes verbaux")
        print("─"*80)
        
        try:
            text1 = "Zoubida Kedad donne un cours de RDF."
            text2 = "Zoubida Kedad enseigne RDF."
            
            graph1, metrics1 = self.extract_kg(text1, verbose=False)
            graph2, metrics2 = self.extract_kg(text2, verbose=False)
            
            # Extraire relations
            relations1_query = """
            SELECT ?prop WHERE {
                ?s ?prop ?o .
                FILTER(STRSTARTS(STR(?prop), "http://example.org/master2/ontology#"))
                FILTER(?prop != rdf:type)
            }
            """
            relations1 = set([str(r[0]) for r in graph1.query(relations1_query)])
            relations2 = set([str(r[0]) for r in graph2.query(relations2_query)])
            
            result.observations.append(f"Relations texte 1 : {relations1}")
            result.observations.append(f"Relations texte 2 : {relations2}")
            
            # Vérifier similarité
            if relations1 == relations2:
                result.observations.append("✅ Mêmes relations extraites (normalisation réussie)")
                result.passed = True
            else:
                result.observations.append("⚠️  Relations différentes (manque normalisation)")
                result.passed = False
            
            result.metrics = {
                "relations_text1": len(relations1),
                "relations_text2": len(relations2),
                "intersection": len(relations1 & relations2)
            }
            
            result.status = "COMPLETED"
            
        except Exception as e:
            result.status = "ERROR"
            result.errors.append(str(e))
            result.passed = False
        
        self.results.append(result)
        return result
    
    def test_05_verbe_ambigu(self):
        """Test 5 : Verbe ambigu (travaille)"""
        result = TestResult("TEST_05", "2_MAPPING", "Verbe ambigu")
        print("\n" + "─"*80)
        print("🧪 TEST 05 : Verbe ambigu (travaille)")
        print("─"*80)
        
        try:
            text = "Zoubida Kedad travaille à Versailles."
            graph, metrics = self.extract_kg(text, verbose=False)
            
            result.metrics = metrics
            
            # Extraire relations
            relations_query = """
            SELECT ?prop WHERE {
                ?s ?prop ?o .
                FILTER(STRSTARTS(STR(?prop), "http://example.org/master2/ontology#"))
                FILTER(?prop != rdf:type)
            }
            """
            relations = [str(r[0]).split('#')[-1] for r in graph.query(relations_query)]
            
            result.observations.append(f"Relations détectées : {relations}")
            
            if "worksAt" in relations:
                result.observations.append("✅ Relation worksAt correctement mappée")
                result.passed = True
            elif "locatedIn" in relations:
                result.observations.append("❌ Relation locatedIn utilisée (mapping incorrect)")
                result.passed = False
            else:
                result.observations.append(f"⚠️  Relation inattendue : {relations}")
                result.passed = False
            
            result.status = "COMPLETED"
            
        except Exception as e:
            result.status = "ERROR"
            result.errors.append(str(e))
            result.passed = False
        
        self.results.append(result)
        return result
    
    # ========================================================================
    # 3️⃣ TESTS DOMAIN / RANGE
    # ========================================================================
    
    def test_06_violation_domain(self):
        """Test 6 : Violation Domain"""
        result = TestResult("TEST_06", "3_DOMAIN_RANGE", "Violation Domain")
        print("\n" + "─"*80)
        print("🧪 TEST 06 : Violation Domain")
        print("─"*80)
        
        try:
            text = "Web Sémantique enseigne Zoubida Kedad."
            graph, metrics = self.extract_kg(text, verbose=False)
            
            result.metrics = metrics
            
            # Vérifier si relation créée
            teaches_query = """
            SELECT ?s ?o WHERE {
                ?s <http://example.org/master2/ontology#teaches> ?o .
            }
            """
            teaches_relations = list(graph.query(teaches_query))
            
            # Vérifier type de Web Sémantique
            ws_type_query = """
            SELECT ?type WHERE {
                ?entity rdf:type ?type .
                ?entity rdfs:label "Web Sémantique"@fr .
            }
            """
            ws_types = [str(t[0]) for t in graph.query(ws_type_query)]
            
            result.observations.append(f"Relations teaches : {len(teaches_relations)}")
            result.observations.append(f"Types Web Sémantique : {ws_types}")
            
            # Vérification
            has_person_type = any("Person" in t for t in ws_types)
            
            if len(teaches_relations) == 0:
                result.observations.append("✅ Relation rejetée (bon comportement)")
                result.passed = True
            elif has_person_type:
                result.observations.append("❌ Web Sémantique typé Person (violation grave)")
                result.passed = False
            else:
                result.observations.append("⚠️  Relation créée malgré violation domain")
                result.passed = False
            
            result.status = "COMPLETED"
            
        except Exception as e:
            result.status = "ERROR"
            result.errors.append(str(e))
            result.passed = False
        
        self.results.append(result)
        return result
    
    def test_07_violation_range(self):
        """Test 7 : Violation Range"""
        result = TestResult("TEST_07", "3_DOMAIN_RANGE", "Violation Range")
        print("\n" + "─"*80)
        print("🧪 TEST 07 : Violation Range")
        print("─"*80)
        
        try:
            text = "Zoubida Kedad enseigne Versailles."
            graph, metrics = self.extract_kg(text, verbose=False)
            
            result.metrics = metrics
            
            # Vérifier teachesSubject
            teaches_subject_query = """
            SELECT ?s ?o WHERE {
                ?s <http://example.org/master2/ontology#teachesSubject> ?o .
            }
            """
            teaches_subject = list(graph.query(teaches_subject_query))
            
            result.observations.append(f"Relations teachesSubject : {len(teaches_subject)}")
            
            # Vérifier si Versailles accepté comme sujet
            for s, o in teaches_subject:
                obj_label = list(graph.objects(o, RDFS.label))
                if obj_label and "Versailles" in str(obj_label[0]):
                    result.observations.append("⚠️  Versailles (Place) accepté comme sujet")
                    result.passed = False
                    break
            else:
                result.observations.append("✅ Violation range détectée/gérée")
                result.passed = True
            
            result.status = "COMPLETED"
            
        except Exception as e:
            result.status = "ERROR"
            result.errors.append(str(e))
            result.passed = False
        
        self.results.append(result)
        return result
    
    # ========================================================================
    # 4️⃣ TESTS RAISONNEMENT OWL
    # ========================================================================
    
    def test_08_inference_hierarchique(self):
        """Test 8 : Inférence hiérarchique (rdfs:subClassOf)"""
        result = TestResult("TEST_08", "4_REASONING", "Inférence hiérarchique")
        print("\n" + "─"*80)
        print("🧪 TEST 08 : Inférence hiérarchique")
        print("─"*80)
        
        try:
            # Créer graphe avec hiérarchie
            graph = Graph()
            create_ontology(graph)
            
            # Ajouter hiérarchie
            graph.add((EX.Professor, RDF.type, OWL.Class))
            graph.add((EX.Professor, RDFS.subClassOf, FOAF.Person))
            graph.add((DATA.Zoubida, RDF.type, EX.Professor))
            
            # Avant raisonnement
            is_person_before = (DATA.Zoubida, RDF.type, FOAF.Person) in graph
            triples_before = len(graph)
            
            # Appliquer raisonnement
            apply_owl_reasoning(graph)
            
            # Après raisonnement
            is_person_after = (DATA.Zoubida, RDF.type, FOAF.Person) in graph
            triples_after = len(graph)
            
            result.metrics = {
                "triples_before": triples_before,
                "triples_after": triples_after,
                "triples_inferred": triples_after - triples_before
            }
            
            result.observations.append(f"Zoubida est Person avant raisonnement : {is_person_before}")
            result.observations.append(f"Zoubida est Person après raisonnement : {is_person_after}")
            
            if not is_person_before and is_person_after:
                result.observations.append("✅ Inférence rdfs:subClassOf réussie")
                result.passed = True
            elif is_person_before:
                result.observations.append("⚠️  Déjà Person avant raisonnement")
                result.passed = True
            else:
                result.observations.append("❌ Inférence échouée")
                result.passed = False
            
            result.status = "COMPLETED"
            
        except Exception as e:
            result.status = "ERROR"
            result.errors.append(str(e))
            result.passed = False
        
        self.results.append(result)
        return result
    
    def test_09_restriction_owl(self):
        """Test 9 : Restriction OWL"""
        result = TestResult("TEST_09", "4_REASONING", "Restriction OWL")
        print("\n" + "─"*80)
        print("🧪 TEST 09 : Restriction OWL")
        print("─"*80)
        
        try:
            # Ce test vérifie si le système supporte les restrictions OWL
            graph = Graph()
            create_ontology(graph)
            
            # Vérifier présence restrictions dans ontologie
            restrictions_query = """
            SELECT ?class WHERE {
                ?class rdf:type owl:Class .
                ?class owl:equivalentClass ?restriction .
                ?restriction rdf:type owl:Restriction .
            }
            """
            restrictions = list(graph.query(restrictions_query))
            
            result.metrics["restrictions_found"] = len(restrictions)
            
            if len(restrictions) > 0:
                result.observations.append(f"✅ {len(restrictions)} restriction(s) OWL détectée(s)")
                result.passed = True
            else:
                result.observations.append("⚠️  Aucune restriction OWL dans l'ontologie")
                result.passed = False
            
            result.status = "COMPLETED"
            
        except Exception as e:
            result.status = "ERROR"
            result.errors.append(str(e))
            result.passed = False
        
        self.results.append(result)
        return result
    
    def test_10_detection_incoherence(self):
        """Test 10 : Détection incohérence (disjointWith)"""
        result = TestResult("TEST_10", "4_REASONING", "Détection incohérence")
        print("\n" + "─"*80)
        print("🧪 TEST 10 : Détection incohérence")
        print("─"*80)
        
        try:
            graph = Graph()
            create_ontology(graph)
            
            # Ajouter disjonction
            graph.add((FOAF.Person, OWL.disjointWith, SCHEMA.Place))
            
            # Créer incohérence
            graph.add((DATA.Versailles, RDF.type, FOAF.Person))
            graph.add((DATA.Versailles, RDF.type, SCHEMA.Place))
            
            # Tester raisonnement
            try:
                apply_owl_reasoning(graph)
                
                # Vérifier si incohérence détectée
                # (owlrl ne lève pas d'exception, il faut vérifier manuellement)
                has_both_types = (
                    (DATA.Versailles, RDF.type, FOAF.Person) in graph and
                    (DATA.Versailles, RDF.type, SCHEMA.Place) in graph
                )
                
                if has_both_types:
                    result.observations.append("⚠️  Incohérence non détectée par le raisonneur")
                    result.passed = False
                else:
                    result.observations.append("✅ Incohérence gérée")
                    result.passed = True
                
            except Exception as reason_error:
                result.observations.append(f"✅ Incohérence détectée : {str(reason_error)[:100]}")
                result.passed = True
            
            result.status = "COMPLETED"
            
        except Exception as e:
            result.status = "ERROR"
            result.errors.append(str(e))
            result.passed = False
        
        self.results.append(result)
        return result
    
    # ========================================================================
    # 5️⃣ TESTS ROBUSTESSE LLM
    # ========================================================================
    
    def test_11_hallucination_controlee(self):
        """Test 11 : Hallucination contrôlée LLM"""
        result = TestResult("TEST_11", "5_LLM_ROBUSTESSE", "Hallucination LLM")
        print("\n" + "─"*80)
        print("🧪 TEST 11 : Hallucination LLM")
        print("─"*80)
        
        try:
            text = "Le Web Sémantique est marié à RDF."
            graph, metrics = self.extract_kg(text, verbose=False)
            
            result.metrics = metrics
            
            # Vérifier relations absurdes
            absurd_relations = ["marriedTo", "married", "spouse"]
            
            relations_query = """
            SELECT ?prop WHERE {
                ?s ?prop ?o .
                FILTER(STRSTARTS(STR(?prop), "http://example.org/master2/ontology#"))
            }
            """
            relations = [str(r[0]).split('#')[-1] for r in graph.query(relations_query)]
            
            result.observations.append(f"Relations détectées : {relations}")
            
            has_absurd = any(rel in absurd_relations for rel in relations)
            
            if not has_absurd:
                result.observations.append("✅ Relation absurde rejetée")
                result.passed = True
            else:
                result.observations.append("❌ Relation absurde acceptée (hallucination)")
                result.passed = False
            
            result.status = "COMPLETED"
            
        except Exception as e:
            result.status = "ERROR"
            result.errors.append(str(e))
            result.passed = False
        
        self.results.append(result)
        return result
    
    def test_12_texte_bruite(self):
        """Test 12 : Texte bruité"""
        result = TestResult("TEST_12", "5_LLM_ROBUSTESSE", "Texte bruité")
        print("\n" + "─"*80)
        print("🧪 TEST 12 : Texte bruité")
        print("─"*80)
        
        try:
            text = "Zoubida ... euh ... RDF ... Versailles ... enseigne ?"
            graph, metrics = self.extract_kg(text, verbose=False)
            
            result.metrics = metrics
            
            # Vérifier si extraction réussit malgré bruit
            entities_query = """
            SELECT ?entity WHERE {
                ?entity rdf:type ?type .
                FILTER(STRSTARTS(STR(?entity), "http://example.org/master2/data#"))
            }
            """
            entities = list(graph.query(entities_query))
            
            result.observations.append(f"Entités extraites malgré bruit : {len(entities)}")
            
            if len(entities) >= 2:
                result.observations.append("✅ Extraction robuste au bruit")
                result.passed = True
            else:
                result.observations.append("⚠️  Extraction affaiblie par le bruit")
                result.passed = False
            
            result.status = "COMPLETED"
            
        except Exception as e:
            result.status = "ERROR"
            result.errors.append(str(e))
            result.passed = False
        
        self.results.append(result)
        return result
    
    # ========================================================================
    # 6️⃣ TESTS CONFIANCE & RÉIFICATION
    # ========================================================================
    
    def test_13_comparaison_confiance(self):
        """Test 13 : Comparaison scores confiance"""
        result = TestResult("TEST_13", "6_CONFIANCE", "Comparaison confiance")
        print("\n" + "─"*80)
        print("🧪 TEST 13 : Comparaison scores confiance")
        print("─"*80)
        
        try:
            text_clear = "Zoubida Kedad enseigne RDF."
            text_ambiguous = "Zoubida parle de RDF."
            
            graph1, metrics1 = self.extract_kg(text_clear, verbose=False)
            graph2, metrics2 = self.extract_kg(text_ambiguous, verbose=False)
            
            # Extraire scores confiance
            confidence_query = """
            SELECT ?statement ?conf WHERE {
                ?statement <http://example.org/master2/ontology#confidence> ?conf .
            }
            """
            
            confidences1 = [float(c[1]) for c in graph1.query(confidence_query)]
            confidences2 = [float(c[1]) for c in graph2.query(confidence_query)]
            
            avg_conf1 = sum(confidences1) / len(confidences1) if confidences1 else 0
            avg_conf2 = sum(confidences2) / len(confidences2) if confidences2 else 0
            
            result.metrics = {
                "confidence_clear": avg_conf1,
                "confidence_ambiguous": avg_conf2,
                "difference": avg_conf1 - avg_conf2
            }
            
            result.observations.append(f"Confiance texte clair : {avg_conf1:.3f}")
            result.observations.append(f"Confiance texte ambigu : {avg_conf2:.3f}")
            
            if avg_conf1 > avg_conf2:
                result.observations.append("✅ Scoring discrimine bien clarté/ambiguïté")
                result.passed = True
            else:
                result.observations.append("⚠️  Pas de différence de confiance")
                result.passed = False
            
            result.status = "COMPLETED"
            
        except Exception as e:
            result.status = "ERROR"
            result.errors.append(str(e))
            result.passed = False
        
        self.results.append(result)
        return result
    
    def test_14_triplets_inferes_vs_extraits(self):
        """Test 14 : Triplets inférés vs extraits"""
        result = TestResult("TEST_14", "6_CONFIANCE", "Triplets inférés vs extraits")
        print("\n" + "─"*80)
        print("🧪 TEST 14 : Triplets inférés vs extraits")
        print("─"*80)
        
        try:
            text = "Zoubida Kedad enseigne RDF."
            graph, metrics = self.extract_kg(text, verbose=False)
            
            result.metrics = metrics
            
            # Comparer triplets
            result.observations.append(f"Triplets extraits : {metrics['triples_initial']}")
            result.observations.append(f"Triplets inférés : {metrics['triples_inferred']}")
            
            if metrics['triples_inferred'] > 0:
                result.observations.append("✅ Raisonnement produit inférences")
                result.passed = True
            else:
                result.observations.append("⚠️  Aucune inférence (raisonnement limité)")
                result.passed = False
            
            result.status = "COMPLETED"
            
        except Exception as e:
            result.status = "ERROR"
            result.errors.append(str(e))
            result.passed = False
        
        self.results.append(result)
        return result
    
    # ========================================================================
    # 🔬 TESTS MÉTA-ARCHITECTURE
    # ========================================================================
    
    def test_15_suppression_llm(self):
        """Test 15 : Système sans LLM"""
        result = TestResult("TEST_15", "7_META", "Suppression LLM")
        print("\n" + "─"*80)
        print("🧪 TEST 15 : Système sans LLM")
        print("─"*80)
        
        try:
            text = "Zoubida Kedad enseigne RDF à Versailles."
            
            # Extraction NER seulement (pas LLM)
            graph = Graph()
            create_ontology(graph)
            confidence_scorer = ConfidenceScorer()
            
            ner_module = HybridNERModule(
                self.nlp, 
                confidence_threshold=0.5,
                ontology_graph=graph,
                enable_validation=True
            )
            entities = ner_module.extract(text, verbose=False)
            entity_uris = add_entities_to_graph(graph, entities, confidence_scorer)
            
            # Pas d'appel LLM !
            
            triples_count = len(graph)
            entities_count = len(entity_uris)
            
            result.metrics = {
                "entities_extracted": entities_count,
                "triples_created": triples_count
            }
            
            result.observations.append(f"Entités extraites sans LLM : {entities_count}")
            
            if entities_count >= 3:
                result.observations.append("✅ Pipeline fonctionne sans LLM")
                result.passed = True
            else:
                result.observations.append("❌ Dépendance forte au LLM")
                result.passed = False
            
            result.status = "COMPLETED"
            
        except Exception as e:
            result.status = "ERROR"
            result.errors.append(str(e))
            result.passed = False
        
        self.results.append(result)
        return result
    
    def test_16_suppression_owl(self):
        """Test 16 : Système sans raisonnement OWL"""
        result = TestResult("TEST_16", "7_META", "Suppression OWL")
        print("\n" + "─"*80)
        print("🧪 TEST 16 : Système sans raisonnement OWL")
        print("─"*80)
        
        try:
            text = "Zoubida Kedad enseigne RDF."
            
            # Extraction complète
            graph = Graph()
            create_ontology(graph)
            confidence_scorer = ConfidenceScorer()
            
            ner_module = HybridNERModule(self.nlp, confidence_threshold=0.5)
            entities = ner_module.extract(text, verbose=False)
            entity_uris = add_entities_to_graph(graph, entities, confidence_scorer)
            relations = extract_relations_with_llm(text, entities, self.nlp)
            add_relations_to_graph(graph, relations, entity_uris, confidence_scorer)
            
            triples_without_reasoning = len(graph)
            
            # Appliquer raisonnement
            apply_owl_reasoning(graph)
            
            triples_with_reasoning = len(graph)
            inferred = triples_with_reasoning - triples_without_reasoning
            
            result.metrics = {
                "triples_before_reasoning": triples_without_reasoning,
                "triples_after_reasoning": triples_with_reasoning,
                "triples_inferred": inferred,
                "reasoning_value_percent": (inferred / triples_without_reasoning * 100) if triples_without_reasoning > 0 else 0
            }
            
            result.observations.append(f"Triplets avant raisonnement : {triples_without_reasoning}")
            result.observations.append(f"Triplets inférés : {inferred}")
            result.observations.append(f"Valeur ajoutée : {result.metrics['reasoning_value_percent']:.1f}%")
            
            if inferred > 0:
                result.observations.append("✅ Raisonnement apporte valeur")
                result.passed = True
            else:
                result.observations.append("⚠️  Raisonnement n'apporte rien")
                result.passed = False
            
            result.status = "COMPLETED"
            
        except Exception as e:
            result.status = "ERROR"
            result.errors.append(str(e))
            result.passed = False
        
        self.results.append(result)
        return result
    
    # ========================================================================
    # EXÉCUTION ET RAPPORT
    # ========================================================================
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        print("\n" + "="*80)
        print("🧪 SUITE DE TESTS COMPLÈTE - DÉMARRAGE")
        print("="*80)
        
        start_time = time.time()
        
        # 1️⃣ Tests NER
        self.test_01_ambiguite_lexicale()
        self.test_02_entites_imbriquees()
        self.test_03_entite_hors_ontologie()
        
        # 2️⃣ Tests Mapping
        self.test_04_synonymes_verbaux()
        self.test_05_verbe_ambigu()
        
        # 3️⃣ Tests Domain/Range
        self.test_06_violation_domain()
        self.test_07_violation_range()
        
        # 4️⃣ Tests Raisonnement
        self.test_08_inference_hierarchique()
        self.test_09_restriction_owl()
        self.test_10_detection_incoherence()
        
        # 5️⃣ Tests Robustesse LLM
        self.test_11_hallucination_controlee()
        self.test_12_texte_bruite()
        
        # 6️⃣ Tests Confiance
        self.test_13_comparaison_confiance()
        self.test_14_triplets_inferes_vs_extraits()
        
        # 🔬 Tests Méta
        self.test_15_suppression_llm()
        self.test_16_suppression_owl()
        
        total_time = time.time() - start_time
        
        print("\n" + "="*80)
        print(f"✅ TOUS LES TESTS TERMINÉS ({total_time:.2f}s)")
        print("="*80)
        
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Génère rapport complet"""
        
        # Statistiques globales
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = sum(1 for r in self.results if not r.passed and r.status == "COMPLETED")
        error_tests = sum(1 for r in self.results if r.status == "ERROR")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Rapport par catégorie
        categories = {}
        for result in self.results:
            cat = result.category
            if cat not in categories:
                categories[cat] = {"passed": 0, "failed": 0, "error": 0, "total": 0}
            
            categories[cat]["total"] += 1
            if result.passed:
                categories[cat]["passed"] += 1
            elif result.status == "ERROR":
                categories[cat]["error"] += 1
            else:
                categories[cat]["failed"] += 1
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "errors": error_tests,
                "success_rate": success_rate
            },
            "categories": categories,
            "results": [r.to_dict() for r in self.results]
        }
        
        return report
    
    def print_report(self, report: Dict[str, Any]):
        """Affiche rapport formaté"""
        
        print("\n" + "="*80)
        print("📊 RAPPORT DE TESTS ACADÉMIQUE")
        print("="*80)
        print(f"Date : {report['timestamp']}")
        print()
        
        summary = report['summary']
        print("📈 RÉSUMÉ GLOBAL")
        print("-" * 80)
        print(f"  Tests totaux     : {summary['total_tests']}")
        print(f"  ✅ Réussis       : {summary['passed']}")
        print(f"  ❌ Échoués       : {summary['failed']}")
        print(f"  ⚠️  Erreurs       : {summary['errors']}")
        print(f"  📊 Taux réussite : {summary['success_rate']:.1f}%")
        print()
        
        print("📂 RÉSULTATS PAR CATÉGORIE")
        print("-" * 80)
        for cat_name, cat_stats in report['categories'].items():
            rate = (cat_stats['passed'] / cat_stats['total'] * 100) if cat_stats['total'] > 0 else 0
            print(f"  {cat_name}")
            print(f"    ✅ {cat_stats['passed']}/{cat_stats['total']} ({rate:.0f}%)")
        print()
        
        print("🔍 DÉTAILS DES TESTS")
        print("-" * 80)
        for result in report['results']:
            status_icon = "✅" if result['passed'] else "❌" if result['status'] == "COMPLETED" else "⚠️"
            print(f"\n{status_icon} {result['test_id']} : {result['name']}")
            print(f"   Catégorie : {result['category']}")
            
            if result['observations']:
                print("   Observations :")
                for obs in result['observations']:
                    print(f"     • {obs}")
            
            if result['metrics']:
                print("   Métriques :")
                for key, value in result['metrics'].items():
                    if isinstance(value, float):
                        print(f"     • {key}: {value:.3f}")
                    else:
                        print(f"     • {key}: {value}")
            
            if result['errors']:
                print("   ⚠️  Erreurs :")
                for error in result['errors']:
                    print(f"     • {error}")
        
        print("\n" + "="*80)


def main():
    """Point d'entrée principal"""
    
    suite = TestSuite()
    suite.setup()
    
    report = suite.run_all_tests()
    suite.print_report(report)
    
    # Sauvegarder rapport JSON
    report_path = "tests/rapport_tests_complet.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Rapport sauvegardé : {report_path}")
    
    # Sauvegarder rapport texte
    report_txt_path = "tests/rapport_tests_complet.txt"
    with open(report_txt_path, 'w', encoding='utf-8') as f:
        import sys
        from io import StringIO
        
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        
        suite.print_report(report)
        
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        
        f.write(output)
    
    print(f"💾 Rapport texte sauvegardé : {report_txt_path}")
    
    return report


if __name__ == "__main__":
    main()
