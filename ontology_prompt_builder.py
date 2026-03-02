#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODULE 3 - Ontology-Driven Prompt Generator
============================================

Ce module génère dynamiquement des prompts LLM à partir de l'ontologie OWL.

Fonctionnalités:
- Extraction automatique des classes et propriétés de l'ontologie
- Génération de prompts structurés avec contraintes domain/range
- Support multi-modèle (Groq, Hugging Face, OpenAI)
- Adaptation contextuelle selon le texte à analyser

Architecture neuro-symbolique:
- Couche symbolique: Schéma OWL formel
- Couche neuronale: Prompt engineering pour LLM
- Pont neuro-symbolique: Contraintes ontologiques → Instructions LLM

Avantages:
- Cohérence garantie entre ontologie et extraction
- Maintenance simplifiée (1 seule source de vérité: l'ontologie)
- Évolutivité (ajout de classes/propriétés sans modifier le code)
"""

from rdflib import Graph, Namespace, URIRef, RDF, RDFS, OWL
from typing import Dict, List, Set, Optional
import logging
import json

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OntologyPromptBuilder:
    """
    Générateur de prompts LLM guidés par l'ontologie.
    
    Ce builder analyse la T-Box (ontologie) et construit des prompts
    structurés qui contraignent le LLM à respecter le schéma ontologique.
    """
    
    def __init__(self, graph: Graph):
        """
        Initialise le builder avec un graphe RDF contenant l'ontologie.
        
        Args:
            graph: Le graphe RDF contenant la T-Box
        """
        self.graph = graph
        self.classes = {}  # {class_uri: {label, comment}}
        self.properties = {}  # {prop_uri: {label, domain, range, type}}
        
        # Extraction de l'ontologie
        self._extract_ontology_schema()
        
        logger.info(f"✓ Builder initialisé avec {len(self.classes)} classes, "
                   f"{len(self.properties)} propriétés")
    
    def _extract_ontology_schema(self):
        """
        Extrait le schéma ontologique du graphe (classes et propriétés).
        
        Cette méthode parse la T-Box pour identifier:
        - owl:Class et leurs labels/commentaires
        - owl:ObjectProperty avec domain/range
        - owl:DatatypeProperty
        """
        # Extraction des classes (owl:Class)
        for class_uri, _, _ in self.graph.triples((None, RDF.type, OWL.Class)):
            if isinstance(class_uri, URIRef):
                self.classes[class_uri] = self._extract_class_metadata(class_uri)
        
        # Extraction des ObjectProperties
        for prop_uri, _, _ in self.graph.triples((None, RDF.type, OWL.ObjectProperty)):
            if isinstance(prop_uri, URIRef):
                self.properties[prop_uri] = self._extract_property_metadata(prop_uri, "ObjectProperty")
        
        # Extraction des DatatypeProperties
        for prop_uri, _, _ in self.graph.triples((None, RDF.type, OWL.DatatypeProperty)):
            if isinstance(prop_uri, URIRef):
                self.properties[prop_uri] = self._extract_property_metadata(prop_uri, "DatatypeProperty")
        
        logger.info(f"  Schéma extrait: {len(self.classes)} classes, "
                   f"{len(self.properties)} propriétés")
    
    def _extract_class_metadata(self, class_uri: URIRef) -> Dict:
        """Extrait les métadonnées d'une classe (label, comment)."""
        metadata = {
            "uri": class_uri,
            "short_name": self._format_uri(class_uri),
            "label": None,
            "comment": None
        }
        
        # Label (rdfs:label)
        for _, _, label in self.graph.triples((class_uri, RDFS.label, None)):
            metadata["label"] = str(label)
            break
        
        # Commentaire (rdfs:comment)
        for _, _, comment in self.graph.triples((class_uri, RDFS.comment, None)):
            metadata["comment"] = str(comment)
            break
        
        return metadata
    
    def _extract_property_metadata(self, prop_uri: URIRef, prop_type: str) -> Dict:
        """Extrait les métadonnées d'une propriété (label, domain, range)."""
        metadata = {
            "uri": prop_uri,
            "short_name": self._format_uri(prop_uri),
            "type": prop_type,
            "label": None,
            "comment": None,
            "domains": [],
            "ranges": []
        }
        
        # Label
        for _, _, label in self.graph.triples((prop_uri, RDFS.label, None)):
            metadata["label"] = str(label)
            break
        
        # Commentaire
        for _, _, comment in self.graph.triples((prop_uri, RDFS.comment, None)):
            metadata["comment"] = str(comment)
            break
        
        # Domain(s)
        for _, _, domain in self.graph.triples((prop_uri, RDFS.domain, None)):
            if isinstance(domain, URIRef):
                metadata["domains"].append(self._format_uri(domain))
        
        # Range(s)
        for _, _, range_val in self.graph.triples((prop_uri, RDFS.range, None)):
            if isinstance(range_val, URIRef):
                metadata["ranges"].append(self._format_uri(range_val))
        
        return metadata
    
    def build_relation_extraction_prompt(self, entity1: str, entity2: str, 
                                        sentence: str, 
                                        model_style: str = "groq") -> str:
        """
        Génère un prompt pour l'extraction de relations entre deux entités.
        
        Le prompt est construit dynamiquement à partir de l'ontologie
        pour garantir la cohérence avec le schéma formel.
        
        Args:
            entity1: Première entité
            entity2: Deuxième entité
            sentence: Phrase contenant les entités
            model_style: Style de prompt ("groq", "huggingface", "openai")
            
        Returns:
            Prompt structuré pour le LLM
        """
        # Construction de la liste des relations autorisées
        relations_list = self._build_relations_list()
        
        # Génération du prompt selon le style
        if model_style == "groq":
            return self._build_groq_style_prompt(entity1, entity2, sentence, relations_list)
        elif model_style == "huggingface":
            return self._build_huggingface_style_prompt(entity1, entity2, sentence, relations_list)
        else:
            return self._build_generic_prompt(entity1, entity2, sentence, relations_list)
    
    def _build_relations_list(self) -> List[Dict]:
        """
        Construit la liste formatée des relations de l'ontologie.
        
        Returns:
            Liste de dictionnaires avec nom, domaine, range, description
        """
        relations = []
        
        for prop_uri, metadata in self.properties.items():
            # Ne garder que les ObjectProperties (relations entre entités)
            if metadata["type"] != "ObjectProperty":
                continue
            
            relation_info = {
                "name": metadata["short_name"],
                "label": metadata["label"] or metadata["short_name"],
                "domains": ", ".join(metadata["domains"]) if metadata["domains"] else "Any",
                "ranges": ", ".join(metadata["ranges"]) if metadata["ranges"] else "Any",
                "description": metadata["comment"] or "No description"
            }
            
            relations.append(relation_info)
        
        return relations
    
    def _build_groq_style_prompt(self, entity1: str, entity2: str, 
                                sentence: str, relations: List[Dict]) -> str:
        """Construit un prompt optimisé pour Groq/Llama."""
        
        # Construction de la liste numérotée
        relations_text = ""
        for i, rel in enumerate(relations, 1):
            relations_text += f"{i}. **{rel['name']}** ({rel['label']})\n"
            relations_text += f"   - Domain: {rel['domains']}\n"
            relations_text += f"   - Range: {rel['ranges']}\n"
            relations_text += f"   - Description: {rel['description']}\n\n"
        
        prompt = f"""Context: "{sentence}"

Analyze the semantic relationship between: "{entity1}" and "{entity2}".

You MUST choose EXACTLY ONE relation from this ontology schema:

{relations_text}

IMPORTANT CONSTRAINTS:
- You MUST verify domain/range compatibility
- Only use relations where entity types match domain/range constraints
- Reply with ONLY the relation name (e.g., "teaches", "worksAt")
- NO explanations, NO punctuation, just the relation name

Your answer (one word only):"""

        return prompt
    
    def _build_huggingface_style_prompt(self, entity1: str, entity2: str,
                                       sentence: str, relations: List[Dict]) -> str:
        """Construit un prompt pour Hugging Face Inference API."""
        
        # Format JSON pour meilleure structuration
        relations_json = []
        for rel in relations:
            relations_json.append({
                "relation": rel["name"],
                "label": rel["label"],
                "domain": rel["domains"],
                "range": rel["ranges"]
            })
        
        prompt = f"""Task: Semantic Relation Extraction

Given:
- Sentence: "{sentence}"
- Entity 1: "{entity1}"
- Entity 2: "{entity2}"

Available Relations (from OWL ontology):
{json.dumps(relations_json, indent=2)}

Instructions:
1. Identify the semantic relationship between the two entities
2. Select the most appropriate relation from the list above
3. Ensure domain/range constraints are satisfied
4. Return ONLY the relation name

Output format: <relation_name>

Answer:"""

        return prompt
    
    def _build_generic_prompt(self, entity1: str, entity2: str,
                            sentence: str, relations: List[Dict]) -> str:
        """Construit un prompt générique pour n'importe quel LLM."""
        
        # Liste simple et concise
        relations_names = [rel["name"] for rel in relations]
        
        prompt = f"""Extract the semantic relation between "{entity1}" and "{entity2}" in this context:

"{sentence}"

Available relations: {", ".join(relations_names)}

Constraints:
- Choose the most specific relation
- Verify type compatibility
- Reply with ONE word only

Relation:"""

        return prompt
    
    def build_entity_classification_prompt(self, entity: str, sentence: str,
                                          model_style: str = "groq") -> str:
        """
        Génère un prompt pour la classification d'entités.
        
        Le prompt liste toutes les classes de l'ontologie pour guider
        le LLM dans le typage correct des entités.
        
        Args:
            entity: L'entité à classifier
            sentence: Phrase contenant l'entité
            model_style: Style de prompt
            
        Returns:
            Prompt structuré pour la classification
        """
        # Construction de la liste des classes
        classes_list = []
        for class_uri, metadata in self.classes.items():
            class_info = {
                "name": metadata["short_name"],
                "label": metadata["label"] or metadata["short_name"],
                "description": metadata["comment"] or "No description"
            }
            classes_list.append(class_info)
        
        # Construction du prompt
        classes_text = ""
        for i, cls in enumerate(classes_list, 1):
            classes_text += f"{i}. **{cls['name']}** ({cls['label']})\n"
            classes_text += f"   - {cls['description']}\n\n"
        
        prompt = f"""Context: "{sentence}"

Classify the entity "{entity}" into ONE of these ontology classes:

{classes_text}

IMPORTANT:
- Choose the most specific class
- Consider the context of the sentence
- Reply with ONLY the class name (e.g., "Person", "Place", "Organization")

Your answer (one word only):"""

        return prompt
    
    def get_ontology_summary(self) -> str:
        """
        Génère un résumé textuel de l'ontologie.
        
        Utile pour inclure dans les prompts de niveau supérieur
        ou pour la documentation.
        
        Returns:
            Résumé formaté de l'ontologie
        """
        summary = "=== ONTOLOGY SCHEMA ===\n\n"
        
        # Classes
        summary += f"Classes ({len(self.classes)}):\n"
        for class_uri, metadata in self.classes.items():
            summary += f"  - {metadata['short_name']}: {metadata['label'] or 'N/A'}\n"
        
        summary += f"\nObject Properties ({len([p for p in self.properties.values() if p['type'] == 'ObjectProperty'])}):\n"
        for prop_uri, metadata in self.properties.items():
            if metadata['type'] == 'ObjectProperty':
                domain_str = ", ".join(metadata['domains']) or "Any"
                range_str = ", ".join(metadata['ranges']) or "Any"
                summary += f"  - {metadata['short_name']}: {domain_str} → {range_str}\n"
        
        return summary
    
    def _format_uri(self, uri: URIRef) -> str:
        """Formate une URI pour l'affichage."""
        return str(uri).split('#')[-1].split('/')[-1]
    
    def export_ontology_schema_json(self, output_file: str = "ontology_schema.json"):
        """
        Export le schéma ontologique en JSON pour réutilisation.
        
        Args:
            output_file: Chemin du fichier de sortie
        """
        schema = {
            "classes": {
                metadata["short_name"]: {
                    "label": metadata["label"],
                    "comment": metadata["comment"]
                }
                for metadata in self.classes.values()
            },
            "properties": {
                metadata["short_name"]: {
                    "type": metadata["type"],
                    "label": metadata["label"],
                    "domains": metadata["domains"],
                    "ranges": metadata["ranges"],
                    "comment": metadata["comment"]
                }
                for metadata in self.properties.values()
            }
        }
        
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Schéma exporté vers {output_file}")


# ============================================================================
# FONCTION D'INTÉGRATION POUR LE PIPELINE PRINCIPAL
# ============================================================================

def generate_ontology_guided_prompt(graph: Graph, entity1: str, entity2: str,
                                   sentence: str, model_style: str = "groq") -> str:
    """
    Point d'entrée principal pour générer un prompt guidé par l'ontologie.
    
    Cette fonction remplace les prompts statiques par des prompts
    dynamiques construits à partir du schéma ontologique.
    
    Args:
        graph: Le graphe RDF contenant l'ontologie
        entity1: Première entité
        entity2: Deuxième entité
        sentence: Phrase source
        model_style: Style de prompt ("groq", "huggingface", "openai")
        
    Returns:
        Prompt structuré prêt à l'emploi
    """
    builder = OntologyPromptBuilder(graph)
    prompt = builder.build_relation_extraction_prompt(entity1, entity2, sentence, model_style)
    
    return prompt


# ============================================================================
# TESTS UNITAIRES (optionnel, pour validation standalone)
# ============================================================================

if __name__ == "__main__":
    print("Module de génération de prompts ontologiques chargé.")
    print("Utilisez generate_ontology_guided_prompt(graph, ...) dans le pipeline principal.")
