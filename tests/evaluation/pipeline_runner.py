#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline Runner - Safe wrapper for executing the KG extraction pipeline.

Key design decisions (fixes for v2):
  1. Text is fed via STDIN  (highest priority in kg_extraction_semantic_web.py)
  2. TTL output file is deleted BEFORE each run to avoid stale data
  3. Entities/relations are extracted from the RDF graph (rdflib) NOT from logs
  4. RDF class URIs are mapped to evaluation labels (PER / ORG / LOC / TOPIC …)
  5. Only data: instances are considered (T-Box triples are ignored)
  6. First-test debug mode prints input text, graph content, entities, relations
"""

import sys
import os
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

import rdflib
from rdflib import Graph, Namespace, RDF, RDFS, OWL

# ---------------------------------------------------------------------------
# RDF namespaces used by the pipeline
# ---------------------------------------------------------------------------
FOAF   = Namespace("http://xmlns.com/foaf/0.1/")
EX     = Namespace("http://example.org/master2/ontology#")
DATA   = Namespace("http://example.org/master2/data#")
SCHEMA = Namespace("http://schema.org/")
DC     = Namespace("http://purl.org/dc/elements/1.1/")

# ---------------------------------------------------------------------------
# Mapping from RDF class URI -> evaluation label used in scenarios.py
# ---------------------------------------------------------------------------
_RDF_CLASS_TO_EVAL_TYPE: Dict[str, str] = {
    str(FOAF.Person):         "PER",
    str(EX.Person):           "PER",
    str(SCHEMA.Person):       "PER",
    str(SCHEMA.Place):        "LOC",
    str(EX.Place):            "LOC",
    str(SCHEMA.Organization): "ORG",
    str(EX.Organization):     "ORG",
    str(FOAF.Organization):   "ORG",
    str(EX.Document):         "DOCUMENT",
    str(EX.ValidatedCourse):  "DOCUMENT",
    str(EX.Topic):            "TOPIC",
    str(RDFS.Resource):       "TOPIC",
    str(EX.Concept):          "TOPIC",
}

# RDF class URIs that carry no semantic entity-type information
_SKIP_CLASSES = frozenset([
    str(OWL.Thing),           # added by OWL reasoner – not a domain type
    str(OWL.Class),
    str(OWL.ObjectProperty),
    str(OWL.DatatypeProperty),
    str(OWL.AnnotationProperty),
    str(RDF.Statement),       # reification nodes
])

# Predicates to skip when extracting relations
_SKIP_PREDICATES = frozenset([
    str(RDF.type),
    str(RDFS.label),
    str(RDFS.comment),
    str(RDFS.subClassOf),
    str(RDFS.domain),
    str(RDFS.range),
    str(OWL.equivalentClass),
    str(OWL.disjointWith),
    str(OWL.sameAs),          # self-loops added by OWL reasoner
    "http://xmlns.com/foaf/0.1/name",
    str(EX.intitule),
    str(EX.nom),
    str(EX.age),
    str(RDF.subject),
    str(RDF.predicate),
    str(RDF.object),
    "http://purl.org/dc/elements/1.1/source",
])


class PipelineRunner:
    """
    Executes the KG extraction pipeline and captures results.
    Does NOT modify the extraction system.
    """

    _debug_done: bool = False

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.main_script  = self.project_root / "kg_extraction_semantic_web.py"
        if not self.main_script.exists():
            raise FileNotFoundError(f"Main script not found: {self.main_script}")

    # ------------------------------------------------------------------
    # PUBLIC
    # ------------------------------------------------------------------

    def run_pipeline(self,
                     input_text: str,
                     scenario_id: str = "test",
                     timeout: int = 90) -> Dict[str, Any]:
        """
        Run the pipeline on input_text (via stdin) and return a result dict.
        """
        start_time  = time.time()
        turtle_file = self.project_root / "knowledge_graph.ttl"

        result: Dict[str, Any] = {
            "scenario_id":     scenario_id,
            "input_text":      input_text,
            "entities":        [],
            "relations":       [],
            "triples":         [],
            "errors":          [],
            "warnings":        [],
            "execution_time":  0.0,
            "timestamp":       datetime.now().isoformat(),
            "pipeline_ran_ok": False,
            "success":         False,
            "outputs":         {"turtle_file": None, "xml_file": None},
            "metrics": {
                "entity_count":      0,
                "relation_count":    0,
                "triple_count":      0,
                "domain_violations": 0,
                "range_violations":  0,
            },
        }

        try:
            # 1. Delete old outputs FIRST
            self._delete_output_files()

            # 2. Run pipeline – feed text via STDIN
            proc = subprocess.run(
                [sys.executable, str(self.main_script)],
                input=input_text,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.project_root),
            )

            result["execution_time"] = time.time() - start_time
            stdout = proc.stdout or ""
            stderr = proc.stderr or ""

            result["errors"]   = self._collect_errors(stdout, stderr)
            result["warnings"] = self._collect_warnings(stdout)

            # 3. Parse TTL with rdflib
            if turtle_file.exists():
                result["outputs"]["turtle_file"] = str(turtle_file)
                xml_file = self.project_root / "knowledge_graph.xml"
                if xml_file.exists():
                    result["outputs"]["xml_file"] = str(xml_file)

                g = Graph()
                try:
                    g.parse(str(turtle_file), format="turtle")
                except Exception as parse_err:
                    result["errors"].append(f"TTL parse error: {parse_err}")
                    g = Graph()

                # 4. Extract entities from rdf:type triples
                result["entities"] = self._extract_entities_from_graph(g)

                # 5. Extract relations from object-property triples
                result["relations"] = self._extract_relations_from_graph(g)

                result["triples"] = [
                    {"subject": str(s), "predicate": str(p), "object": str(o)}
                    for s, p, o in g
                ]

                result["metrics"]["domain_violations"] = (
                    stdout.lower().count("domaine invalide") +
                    stdout.lower().count("domain invalide")
                )
                result["metrics"]["range_violations"] = stdout.lower().count("range invalide")
                result["pipeline_ran_ok"] = (proc.returncode == 0)
                result["success"]         = result["pipeline_ran_ok"]
            else:
                result["errors"].append(
                    "Pipeline produced no TTL output (knowledge_graph.ttl missing)"
                )

            result["metrics"]["entity_count"]  = len(result["entities"])
            result["metrics"]["relation_count"] = len(result["relations"])
            result["metrics"]["triple_count"]   = len(result["triples"])

            # 6. Debug output for the very first test only
            if not PipelineRunner._debug_done:
                PipelineRunner._debug_done = True
                self._print_debug(scenario_id, input_text, turtle_file, result, stdout)

        except subprocess.TimeoutExpired:
            result["errors"].append(f"Pipeline timeout after {timeout}s")
            result["execution_time"] = timeout
        except Exception as exc:
            result["errors"].append(f"Runner exception: {exc}")
            result["execution_time"] = time.time() - start_time

        return result

    # ------------------------------------------------------------------
    # PRIVATE HELPERS
    # ------------------------------------------------------------------

    def _delete_output_files(self):
        """Remove stale output files before each pipeline run."""
        for name in ["knowledge_graph.ttl", "knowledge_graph.xml",
                     "graphe_connaissance.png", "texte_temp.txt"]:
            try:
                p = self.project_root / name
                if p.exists():
                    p.unlink()
            except OSError:
                pass

    # Priority order for entity types (higher index = more specific / preferred).
    # PER is kept lower than ORG/LOC/DOCUMENT because the pipeline adds foaf:Person
    # to nearly every entity as a side-effect of the OWL reasoner.  A node that
    # also has schema:Organization / schema:Place / ex:Document should use that
    # more informative type instead.
    _TYPE_PRIORITY = ["THING", "PER", "TOPIC", "DOCUMENT", "LOC", "ORG"]

    def _type_priority(self, eval_type: str) -> int:
        """Return priority of an eval_type (higher = more specific)."""
        try:
            return self._TYPE_PRIORITY.index(eval_type)
        except ValueError:
            return -1

    def _extract_entities_from_graph(self, g: Graph) -> List[Dict[str, Any]]:
        """
        Return A-Box entities: data: subjects that have rdf:type.

        When a subject has multiple rdf:type triples (e.g. foaf:Person AND
        owl:Thing added by the reasoner), we keep only the most specific
        domain type using _TYPE_PRIORITY.  rdf:Statement reification nodes
        and owl:Thing / blank-node restriction classes are ignored.
        """
        data_prefix = str(DATA)

        # Pass 1 – collect best (eval_type, class_uri) per data: subject URI
        per_subject: Dict[str, Dict] = {}

        for subject, _, rdf_class in g.triples((None, RDF.type, None)):
            subj_str  = str(subject)
            class_str = str(rdf_class)

            if not subj_str.startswith(data_prefix):
                continue

            # Skip non-semantic / reasoner-added classes
            if class_str in _SKIP_CLASSES:
                continue

            # Skip OWL restriction blank nodes
            if isinstance(rdf_class, rdflib.BNode):
                continue

            eval_type = _RDF_CLASS_TO_EVAL_TYPE.get(class_str)
            if eval_type is None:
                eval_type = class_str.split("#")[-1].split("/")[-1].upper()

            label = self._get_label(g, subject)
            if not label:
                continue

            prev = per_subject.get(subj_str)
            if prev is None or self._type_priority(eval_type) > self._type_priority(prev["type"]):
                per_subject[subj_str] = {
                    "text":       label,
                    "type":       eval_type,
                    "uri":        subj_str,
                    "rdf_class":  class_str,
                    "confidence": 1.0,
                }

        # Pass 2 – deduplicate by (label_lower, type)
        seen: set = set()
        entities: List[Dict[str, Any]] = []
        for candidate in per_subject.values():
            key = (candidate["text"].lower(), candidate["type"])
            if key not in seen:
                seen.add(key)
                entities.append(candidate)

        return entities

    def _extract_relations_from_graph(self, g: Graph) -> List[Dict[str, str]]:
        """
        Return semantic relations: (data:X, property, data:Y) triples
        where predicate is not in _SKIP_PREDICATES and neither node is
        an rdf:Statement reification.
        """
        relations: List[Dict[str, str]] = []
        seen: set = set()
        data_prefix = str(DATA)

        # Reification nodes are structurally identified: any subject that
        # appears as the subject of a rdf:subject triple is a reification node.
        # This is robust against the pipeline also assigning rdf:Statement to
        # real entity URIs (which breaks the URI-pattern-based filter).
        reif_nodes = frozenset(
            str(s)
            for s, p, _ in g
            if str(p) == str(RDF.subject)
        )

        for subject, predicate, obj in g:
            subj_str = str(subject)
            obj_str  = str(obj)
            pred_str = str(predicate)

            if not subj_str.startswith(data_prefix):
                continue
            if not obj_str.startswith(data_prefix):
                continue
            # Skip structural reification helper nodes
            if subj_str in reif_nodes or obj_str in reif_nodes:
                continue
            if pred_str in _SKIP_PREDICATES:
                continue

            subj_label = self._get_label(g, rdflib.URIRef(subj_str))
            obj_label  = self._get_label(g, rdflib.URIRef(obj_str))
            if not subj_label or not obj_label:
                continue

            pred_local = pred_str.split("#")[-1].split("/")[-1]

            key = (subj_label.lower(), pred_local.lower(), obj_label.lower())
            if key in seen:
                continue
            seen.add(key)

            relations.append({
                "subject":   subj_label,
                "predicate": pred_local,
                "object":    obj_label,
            })

        return relations

    def _get_label(self, g: Graph, node: rdflib.URIRef) -> Optional[str]:
        """Preferred label order: rdfs:label (fr) > rdfs:label > foaf:name > schema:name > dc:title > URI slug."""
        # 1. rdfs:label @fr
        for _, _, lbl in g.triples((node, RDFS.label, None)):
            if isinstance(lbl, rdflib.Literal) and getattr(lbl, "language", None) == "fr":
                return str(lbl).strip()
        # 2. rdfs:label (any language)
        for _, _, lbl in g.triples((node, RDFS.label, None)):
            if isinstance(lbl, rdflib.Literal):
                return str(lbl).strip()
        # 3. foaf:name
        for _, _, lbl in g.triples((node, rdflib.URIRef(str(FOAF.name)), None)):
            if isinstance(lbl, rdflib.Literal):
                return str(lbl).strip()
        # 4. schema:name
        for _, _, lbl in g.triples((node, rdflib.URIRef(str(SCHEMA.name)), None)):
            if isinstance(lbl, rdflib.Literal):
                return str(lbl).strip()
        # 5. dc:title
        for _, _, lbl in g.triples((node, rdflib.URIRef(str(DC.title)), None)):
            if isinstance(lbl, rdflib.Literal):
                return str(lbl).strip()
        # 6. URI local-name slug fallback
        node_str = str(node)
        slug = node_str.split("#")[-1].split("/")[-1]
        if slug and slug != node_str:
            return slug.replace("_", " ").strip()
        return None

    def _collect_errors(self, stdout: str, stderr: str) -> List[str]:
        errors: List[str] = []
        ignorable = ("UserWarning", "FutureWarning", "DeprecationWarning")
        for line in stderr.splitlines():
            stripped = line.strip()
            if stripped and not any(stripped.startswith(w) for w in ignorable):
                if any(kw in stripped.lower() for kw in ("error", "exception", "traceback")):
                    errors.append(f"STDERR: {stripped}")
        for line in stdout.splitlines():
            stripped = line.strip()
            if stripped.startswith("❌") or stripped.upper().startswith("ERROR:"):
                errors.append(stripped)
        return errors

    def _collect_warnings(self, stdout: str) -> List[str]:
        warnings: List[str] = []
        for line in stdout.splitlines():
            stripped = line.strip()
            if stripped.startswith("⚠️") or "[WARNING]" in stripped or \
               stripped.upper().startswith("WARNING:"):
                warnings.append(stripped)
        return warnings

    def _print_debug(self, scenario_id: str, input_text: str,
                     turtle_file: Path, result: Dict[str, Any],
                     stdout: str) -> None:
        sep = "=" * 70
        print(f"\n{sep}")
        print(f"  DEBUG – First test: {scenario_id}")
        print(sep)
        print("\n[INPUT TEXT]")
        print(repr(input_text))
        print("\n[PIPELINE STDOUT – last 30 lines]")
        for ln in (stdout.strip().splitlines() or ["(empty)"])[-30:]:
            print(" ", ln)
        print("\n[RDF GRAPH CONTENT – first 60 lines]")
        if turtle_file.exists():
            for ln in turtle_file.read_text(encoding="utf-8", errors="replace").splitlines()[:60]:
                print(" ", ln)
        else:
            print("  (no TTL file)")
        print("\n[EXTRACTED ENTITIES]")
        if result["entities"]:
            for e in result["entities"]:
                print(f"  - '{e['text']}' → {e['type']}  (rdf_class: {e.get('rdf_class','?')})")
        else:
            print("  (none)")
        print("\n[EXTRACTED RELATIONS]")
        if result["relations"]:
            for r in result["relations"]:
                print(f"  - '{r['subject']}' --[{r['predicate']}]--> '{r['object']}'")
        else:
            print("  (none)")
        print(f"\n[ERRORS]  {result['errors']}")
        print(sep + "\n")

    # ------------------------------------------------------------------
    # PERSISTENCE
    # ------------------------------------------------------------------

    def save_result(self, result: Dict[str, Any], output_dir: Path) -> Path:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        ts = result["timestamp"].replace(":", "-")
        filepath = output_dir / f"{result['scenario_id']}_{ts}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        return filepath


# ---------------------------------------------------------------------------
# Standalone smoke-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    runner = PipelineRunner(str(project_root))
    text = "Zoubida Kedad enseigne le Web Sémantique à l'Université de Versailles."
    print(f"Smoke test text: {text}\n")
    result = runner.run_pipeline(text, scenario_id="SMOKE_TEST", timeout=90)
    print(f"pipeline_ran_ok : {result['pipeline_ran_ok']}")
    print(f"Execution time  : {result['execution_time']:.2f}s")
    print(f"Entities ({len(result['entities'])}):")
    for e in result["entities"]:
        print(f"  {e['text']} → {e['type']}")
    print(f"Relations ({len(result['relations'])}):")
    for r in result["relations"]:
        print(f"  {r['subject']} --[{r['predicate']}]--> {r['object']}")
