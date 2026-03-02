#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANALYSEUR DE RÉSULTATS - GÉNÉRATION RAPPORT
============================================
Analyse les graphes RDF générés par la suite de tests
et génère un rapport détaillé avec métriques académiques.
"""

import os
from pathlib import Path
from rdflib import Graph, Namespace, RDF, RDFS, OWL
from rdflib.namespace import FOAF
from datetime import datetime
import json

# Namespaces
EX = Namespace("http://example.org/master2/ontology#")
DATA = Namespace("http://example.org/master2/data#")
SCHEMA = Namespace("http://schema.org/")


class TestAnalyzer:
    """Analyse les résultats de tests"""
    
    def __init__(self, outputs_dir="tests/outputs"):
        self.outputs_dir = Path(outputs_dir)
        self.results = []
        
    def analyze_test(self, test_id, test_name, category, expected_behavior):
        """Analyse un test individuel"""
        
        graph_file = self.outputs_dir / f"{test_id}_graph.ttl"
        output_file = self.outputs_dir / f"{test_id}_output.txt"
        
        result = {
            "test_id": test_id,
            "test_name": test_name,
            "category": category,
            "expected": expected_behavior,
            "observations": [],
            "metrics": {},
            "passed": False
        }
        
        if not graph_file.exists():
            result["observations"].append("❌ Fichier graphe non trouvé")
            return result
        
        # Charger graphe
        try:
            graph = Graph()
            graph.parse(graph_file, format="turtle")
            
            result["metrics"]["triples_total"] = len(graph)
            
            # Extraire entités
            entities_query = """
            SELECT ?entity ?type ?label WHERE {
                ?entity rdf:type ?type .
                OPTIONAL { ?entity rdfs:label ?label }
                FILTER(STRSTARTS(STR(?entity), "http://example.org/master2/data#"))
            }
            """
            entities = list(graph.query(entities_query))
            result["metrics"]["entities"] = len(entities)
            
            # Extraire relations
            relations_query = """
            SELECT ?s ?p ?o WHERE {
                ?s ?p ?o .
                FILTER(STRSTARTS(STR(?p), "http://example.org/master2/ontology#"))
                FILTER(?p != rdf:type)
            }
            """
            relations = list(graph.query(relations_query))
            result["metrics"]["relations"] = len(relations)
            
            # Détails entités
            entity_details = []
            for ent_uri, ent_type, label in entities:
                ent_name = str(label) if label else str(ent_uri).split('#')[-1]
                type_name = str(ent_type).split('#')[-1].split('/')[-1]
                entity_details.append(f"{ent_name} ({type_name})")
            
            if entity_details:
                result["observations"].append(f"Entités : {', '.join(entity_details)}")
            
            # Détails relations
            relation_details = []
            for s, p, o in relations:
                s_label = list(graph.objects(s, RDFS.label))
                o_label = list(graph.objects(o, RDFS.label))
                
                s_name = str(s_label[0]) if s_label else str(s).split('#')[-1]
                o_name = str(o_label[0]) if o_label else str(o).split('#')[-1]
                p_name = str(p).split('#')[-1]
                
                relation_details.append(f"{s_name} --[{p_name}]--> {o_name}")
            
            if relation_details:
                result["observations"].append(f"Relations : {', '.join(relation_details[:5])}")
            
            # Évaluation comportement attendu
            result["passed"] = self._evaluate_behavior(test_id, graph, result)
            
        except Exception as e:
            result["observations"].append(f"⚠️  Erreur analyse : {str(e)[:100]}")
        
        return result
    
    def _evaluate_behavior(self, test_id, graph, result):
        """Évalue si le comportement attendu est respecté"""
        
        # TEST_01 : Apple doit être ORG
        if test_id == "TEST_01":
            for s, _, _ in graph.triples((None, RDF.type, SCHEMA.Organization)):
                label = list(graph.objects(s, RDFS.label))
                if label and "Apple" in str(label[0]):
                    result["observations"].append("✅ Apple typé Organization")
                    return True
            result["observations"].append("⚠️  Apple non typé Organization")
            return False
        
        # TEST_02 : Université Paris-Saclay doit être entité unique
        elif test_id == "TEST_02":
            labels = [str(l) for _, _, l in graph.triples((None, RDFS.label, None))]
            has_full = any("Université Paris-Saclay" in l for l in labels)
            has_paris_only = any(l == "Paris" for l in labels)
            has_saclay_only = any(l == "Saclay" or l == "Paris-Saclay" for l in labels)
            
            if has_full and not (has_paris_only or has_saclay_only):
                result["observations"].append("✅ Entité unique 'Université Paris-Saclay'")
                return True
            else:
                result["observations"].append("❌ Entité fragmentée")
                return False
        
        # TEST_05 : doit avoir worksAt
        elif test_id == "TEST_05":
            has_works_at = (None, EX.worksAt, None) in graph
            if has_works_at:
                result["observations"].append("✅ Relation worksAt détectée")
                return True
            else:
                result["observations"].append("⚠️  worksAt non détectée")
                return False
        
        # TEST_06 : Violation domain - Web Sémantique NE doit PAS être Person
        elif test_id == "TEST_06":
            for s, _, _ in graph.triples((None, RDF.type, FOAF.Person)):
                label = list(graph.objects(s, RDFS.label))
                if label and "Web Sémantique" in str(label[0]):
                    result["observations"].append("❌ Web Sémantique typé Person (violation)")
                    return False
            result["observations"].append("✅ Violation domain gérée")
            return True
        
        # TEST_11 : Hallucination - NE doit PAS avoir marriedTo
        elif test_id == "TEST_11":
            relations = [str(p) for _, p, _ in graph.triples((None, None, None))]
            has_married = any("married" in r.lower() or "spouse" in r.lower() for r in relations)
            if not has_married:
                result["observations"].append("✅ Hallucination rejetée")
                return True
            else:
                result["observations"].append("❌ Hallucination acceptée")
                return False
        
        # Par défaut : réussi si au moins 1 entité
        return result["metrics"].get("entities", 0) > 0
    
    def generate_report(self):
        """Génère rapport complet"""
        
        print("\n" + "="*100)
        print("📊 RAPPORT D'ANALYSE DES TESTS")
        print("="*100)
        print(f"Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Tests à analyser
        tests = [
            ("TEST_01", "Ambiguïté lexicale (Apple)", "1_NER", "Apple doit être Organization"),
            ("TEST_02", "Entités imbriquées", "1_NER", "Université Paris-Saclay entité unique"),
            ("TEST_03", "Entité hors ontologie", "1_NER", "Gestion entité inconnue"),
            ("TEST_04A", "Synonymes verbaux (donne)", "2_MAPPING", "Relation teaches/teachesSubject"),
            ("TEST_04B", "Synonymes verbaux (enseigne)", "2_MAPPING", "Relation teaches/teachesSubject"),
            ("TEST_05", "Verbe ambigu (travaille)", "2_MAPPING", "Relation worksAt"),
            ("TEST_06", "Violation Domain", "3_DOMAIN_RANGE", "Rejet ou gestion violation"),
            ("TEST_07", "Violation Range", "3_DOMAIN_RANGE", "Rejet ou adaptation"),
            ("TEST_11", "Hallucination LLM", "5_LLM", "Rejet relation absurde"),
            ("TEST_12", "Texte bruité", "5_LLM", "Extraction robuste au bruit"),
        ]
        
        categories_stats = {}
        
        for test_id, name, category, expected in tests:
            result = self.analyze_test(test_id, name, category, expected)
            self.results.append(result)
            
            # Stats par catégorie
            if category not in categories_stats:
                categories_stats[category] = {"total": 0, "passed": 0}
            categories_stats[category]["total"] += 1
            if result["passed"]:
                categories_stats[category]["passed"] += 1
        
        # Affichage résultats
        print("📂 RÉSULTATS PAR CATÉGORIE")
        print("-" * 100)
        for cat, stats in sorted(categories_stats.items()):
            rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            print(f"  {cat:<20} : {stats['passed']}/{stats['total']} ({rate:.0f}%)")
        print()
        
        print("🔍 DÉTAILS DES TESTS")
        print("-" * 100)
        for result in self.results:
            status = "✅" if result["passed"] else "❌"
            print(f"\n{status} {result['test_id']} : {result['test_name']}")
            print(f"   Catégorie : {result['category']}")
            print(f"   Attendu : {result['expected']}")
            print(f"   Métriques : {result['metrics']}")
            for obs in result['observations']:
                print(f"   {obs}")
        
        # Statistiques globales
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print()
        print("="*100)
        print("📈 RÉSUMÉ GLOBAL")
        print("="*100)
        print(f"  Tests totaux     : {total}")
        print(f"  ✅ Réussis       : {passed}")
        print(f"  ❌ Échoués       : {total - passed}")
        print(f"  📊 Taux réussite : {success_rate:.1f}%")
        print("="*100)
        
        # Sauvegarder JSON
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": total,
                "passed": passed,
                "failed": total - passed,
                "success_rate": success_rate
            },
            "categories": categories_stats,
            "results": self.results
        }
        
        report_path = self.outputs_dir / "rapport_analyse.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Rapport JSON sauvegardé : {report_path}")
        
        return report_data


def main():
    analyzer = TestAnalyzer()
    analyzer.generate_report()


if __name__ == "__main__":
    main()
