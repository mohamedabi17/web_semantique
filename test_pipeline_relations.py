#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_pipeline_relations.py
==========================
Full pipeline integration test for relation extraction.

Tests MODULE 0++ (NER) → MODULE 1 (OWL instantiation) → MODULE 2 (relation
extraction) and validates the resulting RDF triples with rdflib.

Each test case:
  1. Runs NER on a French sentence
  2. Instantiates entities in an in-memory RDF graph
  3. Calls extract_relations() (Layer 7 + LLM path)
  4. Asserts expected (subject, predicate, object) triples exist in the graph

Run:
    python test_pipeline_relations.py
"""

import sys
import os
import unicodedata
import re
from typing import List, Tuple, Optional

# ── ensure project root is importable ─────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import spacy
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL
from rdflib.namespace import FOAF
from dotenv import load_dotenv

load_dotenv()

# ── project modules ────────────────────────────────────────────────────────
from hybrid_ner_module import HybridNERModule
from kg_extraction_semantic_web import (
    define_tbox,
    instantiate_entities_in_abox,
    extract_relations,
    normalize_uri_fragment,
    extract_entities_with_spacy,
    EX,
    DATA,
    SCHEMA,
)

# ── namespaces ─────────────────────────────────────────────────────────────
EX_NS   = Namespace("http://example.org/master2/ontology#")
DATA_NS = Namespace("http://example.org/master2/data#")

# ===========================================================================
# HELPER UTILITIES
# ===========================================================================

def build_pipeline(nlp) -> HybridNERModule:
    """Return a freshly initialised HybridNERModule."""
    return HybridNERModule(nlp, confidence_threshold=0.6, enable_validation=False)


def run_pipeline(text: str, nlp) -> Graph:
    """
    Execute the full pipeline on *text* and return the populated RDF graph.

    Steps:
        1. NER  → list of (entity_text, entity_type)
        2. T-Box definition in a fresh Graph
        3. A-Box instantiation (entity URIs created)
        4. Relation extraction (Layer 7 + LLM)
    """
    # ── Step 1 : NER ──────────────────────────────────────────────────────
    entities = extract_entities_with_spacy(text, nlp)

    # ── Step 2 : fresh graph + T-Box ─────────────────────────────────────
    g = Graph()
    g.bind("ex",     EX_NS)
    g.bind("data",   DATA_NS)
    g.bind("foaf",   FOAF)
    g.bind("schema", SCHEMA)
    define_tbox(g)

    # ── Step 3 : A-Box ───────────────────────────────────────────────────
    entity_uris = instantiate_entities_in_abox(g, entities)

    # ── Step 4 : relations ───────────────────────────────────────────────
    extract_relations(g, entity_uris, text)

    return g


def triple_exists(graph: Graph, subject_frag: str, predicate: URIRef,
                  object_frag: str) -> bool:
    """
    Return True if (DATA:<subject_frag>, predicate, DATA:<object_frag>)
    exists in *graph*.

    *subject_frag* and *object_frag* are already URI-normalised fragments
    (underscored, accent-free) as produced by normalize_uri_fragment().
    """
    s = DATA_NS[subject_frag]
    o = DATA_NS[object_frag]
    return (s, predicate, o) in graph


def _frag(text: str) -> str:
    """Convenience wrapper for normalize_uri_fragment."""
    return normalize_uri_fragment(text)


# ===========================================================================
# TEST HARNESS
# ===========================================================================

class RelationTestResult:
    def __init__(self, sentence: str, triple_label: str, found: bool):
        self.sentence     = sentence
        self.triple_label = triple_label
        self.found        = found


def check_triple(graph: Graph, s_text: str, pred: URIRef, o_text: str,
                 sentence: str, results: List[RelationTestResult]) -> None:
    """Assert one triple and append the outcome to *results*."""
    s_frag = _frag(s_text)
    o_frag = _frag(o_text)
    pred_name = str(pred).split("#")[-1].split("/")[-1]
    label = f"{s_text} --[{pred_name}]--> {o_text}"
    found = triple_exists(graph, s_frag, pred, o_frag)
    results.append(RelationTestResult(sentence, label, found))
    if found:
        print(f"  ✅ PASS : {label}")
    else:
        print(f"  ❌ FAIL : triple not found — {label}")
        _debug_graph(graph, s_frag, o_frag)


def _debug_graph(graph: Graph, s_frag: str, o_frag: str) -> None:
    """Print triples involving the subject or object URI to aid debugging."""
    s_uri = DATA_NS[s_frag]
    o_uri = DATA_NS[o_frag]
    outgoing = list(graph.triples((s_uri, None, None)))
    incoming = list(graph.triples((None, None, o_uri)))
    if outgoing:
        print(f"    ↪  Triples with subject <{s_frag}>:")
        for _, p, obj in outgoing[:6]:
            p_label = str(p).split("#")[-1].split("/")[-1]
            o_label = str(obj).split("#")[-1].split("/")[-1]
            print(f"       --[{p_label}]--> {o_label}")
    if incoming:
        print(f"    ↪  Triples with object <{o_frag}>:")
        for subj, p, _ in incoming[:6]:
            p_label = str(p).split("#")[-1].split("/")[-1]
            s_label = str(subj).split("#")[-1].split("/")[-1]
            print(f"       {s_label} --[{p_label}]-->")


# ===========================================================================
# TEST CASES
# ===========================================================================

def test_works_at_mit(nlp, results: List[RelationTestResult]) -> None:
    """
    Input    : Tim Berners-Lee travaille au MIT.
    Expected : Tim_Berners_Lee --[worksAt]--> MIT
    """
    sentence = "Tim Berners-Lee travaille au MIT."
    print(f"\n{'='*70}")
    print(f"TEST 1 — worksAt")
    print(f"Input  : {sentence}")
    print(f"{'='*70}")

    g = run_pipeline(sentence, nlp)

    check_triple(g,
                 "Tim Berners-Lee", EX_NS.worksAt, "MIT",
                 sentence, results)


def test_located_in_cambridge(nlp, results: List[RelationTestResult]) -> None:
    """
    Input    : Le MIT est situé à Cambridge.
    Expected : MIT --[locatedIn]--> Cambridge
    """
    sentence = "Le MIT est situé à Cambridge."
    print(f"\n{'='*70}")
    print(f"TEST 2 — locatedIn")
    print(f"Input  : {sentence}")
    print(f"{'='*70}")

    g = run_pipeline(sentence, nlp)

    check_triple(g,
                 "MIT", EX_NS.locatedIn, "Cambridge",
                 sentence, results)


def test_teaches_subject_and_works_at(nlp, results: List[RelationTestResult]) -> None:
    """
    Input    : Zoubida Kedad enseigne le Web Sémantique à l'Université de Versailles.
    Expected :
        Zoubida_Kedad --[teachesSubject]--> Web_Semantique
        Zoubida_Kedad --[worksAt]---------> Universite_de_Versailles
    """
    sentence = "Zoubida Kedad enseigne le Web Sémantique à l'Université de Versailles."
    print(f"\n{'='*70}")
    print(f"TEST 3 — teachesSubject + worksAt")
    print(f"Input  : {sentence}")
    print(f"{'='*70}")

    g = run_pipeline(sentence, nlp)

    check_triple(g,
                 "Zoubida Kedad", EX_NS.teachesSubject, "Web Sémantique",
                 sentence, results)
    check_triple(g,
                 "Zoubida Kedad", EX_NS.worksAt, "Université de Versailles",
                 sentence, results)


def test_related_to_rdf_owl(nlp, results: List[RelationTestResult]) -> None:
    """
    Input    : Le Web Sémantique utilise RDF et OWL.
    Expected :
        Web_Semantique --[uses]--> RDF
        Web_Semantique --[uses]--> OWL
    """
    sentence = "Le Web Sémantique utilise RDF et OWL."
    print(f"\n{'='*70}")
    print(f"TEST 4 — uses (TOPIC↔TOPIC)")
    print(f"Input  : {sentence}")
    print(f"{'='*70}")

    g = run_pipeline(sentence, nlp)

    check_triple(g,
                 "Web Sémantique", EX_NS.uses, "RDF",
                 sentence, results)
    check_triple(g,
                 "Web Sémantique", EX_NS.uses, "OWL",
                 sentence, results)


# ===========================================================================
# MAIN
# ===========================================================================

def main() -> int:
    print("=" * 70)
    print("PIPELINE RELATION EXTRACTION TEST SUITE")
    print("=" * 70)

    # Load spaCy once — shared across all tests
    print("\n[setup] Loading spaCy model fr_core_news_sm …")
    nlp = spacy.load("fr_core_news_sm")
    print("[setup] Model loaded ✓")

    results: List[RelationTestResult] = []

    # Run all test cases
    test_works_at_mit(nlp, results)
    test_located_in_cambridge(nlp, results)
    test_teaches_subject_and_works_at(nlp, results)
    test_related_to_rdf_owl(nlp, results)

    # ── Summary ───────────────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    passed = [r for r in results if r.found]
    failed = [r for r in results if not r.found]

    for r in results:
        icon = "✅" if r.found else "❌"
        print(f"  {icon}  {r.triple_label}")

    print(f"\n  Total : {len(results)} checks | "
          f"Passed : {len(passed)} | Failed : {len(failed)}")
    print()

    if not failed:
        print("🎉 ALL RELATION TESTS PASSED")
        return 0
    else:
        print("⚠️  SOME RELATION TESTS FAILED")
        print("\nFailed triples:")
        for r in failed:
            print(f"  ❌ {r.triple_label}")
            print(f"     in: \"{r.sentence}\"")
        return 1


if __name__ == "__main__":
    sys.exit(main())
