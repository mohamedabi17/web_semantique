#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface Streamlit pour l'Extraction de Graphes de Connaissances
Master 2 Web Sémantique - Projet T-Box/A-Box avec LLM
"""

import streamlit as st
import os
import sys
from PIL import Image
import subprocess
import tempfile
from pathlib import Path

# Configuration de la page
st.set_page_config(
    page_title="Extraction de Graphe RDF",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================

st.markdown('<div class="main-header">🕸️ Extraction de Graphe de Connaissances</div>', unsafe_allow_html=True)
st.markdown('''
<div class="sub-header">
<strong>Master 2 Datascale - Web Sémantique (Sujet 1)</strong><br>
<em>Technologies : SpaCy (NER) + Groq Llama 3.1 (Relations) + RDFLib (OWL/RDFS)</em>
</div>
''', unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - Informations et configuration
# ============================================================================

with st.sidebar:
    st.header("ℹ️ À propos")
    st.markdown("""
    **Architecture T-Box/A-Box**
    - ✅ Restriction OWL avec BNode
    - ✅ LLM réel (Groq API)
    - ✅ Double sérialisation RDF
    """)
    
    st.divider()
    
    st.header("📊 Statistiques")
    if os.path.exists("knowledge_graph.ttl"):
        try:
            with open("knowledge_graph.ttl", "r") as f:
                content = f.read()
                triplets_count = content.count(" .") - content.count("...") 
                st.metric("Triplets RDF", triplets_count)
        except:
            st.metric("Triplets RDF", "N/A")
    else:
        st.metric("Triplets RDF", 0)
    
    st.divider()
    
    st.header("🔧 Actions")
    if st.button("🗑️ Nettoyer les fichiers"):
        files_to_clean = [
            "knowledge_graph.ttl",
            "knowledge_graph.xml",
            "graphe_connaissance.png",
            "texte_temp.txt"
        ]
        for file in files_to_clean:
            if os.path.exists(file):
                os.remove(file)
        st.success("Fichiers nettoyés !")
        st.rerun()
    
    st.divider()
    st.caption("Version 2.0 - Groq API + Llama-3.1-8B")

# ============================================================================
# MAIN CONTENT - Colonnes Input/Output
# ============================================================================

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Texte source")
    
    # Exemples prédéfinis - Tests de validation ontologique
    examples = {
        "🧪 Test 1: Priorité travaille vs Paris": "Emmanuel Macron travaille au Palais de l'Élysée à Paris.",
        "🧪 Test 2: Contrainte OWL (Littérature)": "Victor Hugo a écrit le roman Les Misérables.",
        "🧪 Test 3: Validation 'enseigne'": "Albert Einstein a enseigné la physique à l'Université de Princeton.",
        "🧪 Test 4: Chaîne multi-sauts": "Satya Nadella dirige Microsoft qui est situé à Redmond.",
        "Exemple académique": "Zoubida Kedad enseigne à l'Université de Versailles. Elle a rédigé un cours sur RDFS.",
        "Exemple collaboration": "Jean Dupont et Marie Martin collaborent sur un projet d'IA à Paris.",
        "Texte personnalisé": ""
    }
    
    selected_example = st.selectbox(
        "Choisir un exemple :",
        list(examples.keys()),
        index=0
    )
    
    if selected_example == "Texte personnalisé":
        default_text = ""
    else:
        default_text = examples[selected_example]
    
    user_input = st.text_area(
        "Entrez votre texte ici :",
        value=default_text,
        height=200,
        placeholder="Saisissez un texte contenant des entités (personnes, lieux, organisations)..."
    )
    
    st.markdown("**💡 Conseils :**")
    st.info("""
    - Mentionnez des **personnes** (noms complets)
    - Ajoutez des **lieux** ou **organisations**
    - Utilisez des **verbes d'action** (enseigne, travaille, étudie, collabore...)
    """)
    
    generate_btn = st.button("🚀 Générer le Graphe RDF", type="primary")

# ============================================================================
# TRAITEMENT - Génération du graphe
# ============================================================================

if generate_btn:
    if not user_input.strip():
        st.error("❌ Veuillez entrer un texte à analyser !")
    else:
        with col1:
            with st.spinner('🔄 Analyse en cours...'):
                # Créer un progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Sauvegarder le texte dans le fichier temporaire
                with open("texte_temp.txt", "w", encoding="utf-8") as f:
                    f.write(user_input)
                
                status_text.text("📊 Extraction des entités avec spaCy...")
                progress_bar.progress(25)
                
                status_text.text("🤖 Interrogation du LLM (Groq/Llama-3.1)...")
                progress_bar.progress(50)
                
                try:
                    # Exécuter le script d'extraction avec python3
                    result = subprocess.run(
                        ["python3", "kg_extraction_semantic_web.py"],
                        capture_output=True,
                        text=True,
                        timeout=60,
                        cwd=os.getcwd()
                    )
                    
                    status_text.text("📦 Génération des fichiers RDF...")
                    progress_bar.progress(75)
                    
                    status_text.text("🎨 Création de la visualisation...")
                    progress_bar.progress(90)
                    
                    progress_bar.progress(100)
                    status_text.empty()
                    progress_bar.empty()
                    
                    if result.returncode == 0:
                        st.success("✅ Extraction terminée avec succès !")
                        
                        # Extraire les logs intéressants (entités + relations LLM + priorités)
                        output_lines = result.stdout.split('\n')
                        llm_logs = [line for line in output_lines if any(x in line for x in [
                            '✓ Entité', '🚀 Appel', '🤖 Groq', 'détecté',
                            '🎓 Priorité', '💼 Priorité', '✍️ Priorité', '📍 Priorité',
                            '✓ Relation LLM', '→ Contrainte OWL', 'Force '
                        ])]
                        
                        if llm_logs:
                            with st.expander("📋 Détails de l'extraction (Relations détectées par Llama-3)", expanded=True):
                                st.markdown("**🤖 Analyse IA en temps réel :**")
                                for log in llm_logs:
                                    # Coloriser les logs selon le type
                                    if '🤖 Groq' in log:
                                        st.markdown(f"**:blue[{log}]**")
                                    elif '🎓 Priorité' in log or '💼 Priorité' in log or '✍️ Priorité' in log or '📍 Priorité' in log:
                                        st.markdown(f"**:green[{log}]**")
                                    elif '→ Contrainte OWL' in log:
                                        st.markdown(f"**:orange[{log}]**")
                                    elif '✓ Relation LLM' in log:
                                        st.markdown(f"**:violet[{log}]**")
                                    elif '✓ Entité' in log:
                                        st.markdown(f"**:gray[{log}]**")
                                    else:
                                        st.text(log)
                        else:
                            st.warning("⚠️ Aucun log LLM capturé")
                        
                        # NE PAS faire de rerun automatique pour garder les logs visibles
                        # L'utilisateur doit recharger manuellement pour voir le graphe mis à jour
                    else:
                        st.warning("⚠️ Le script s'est exécuté mais certains fichiers peuvent être manquants.")
                        with st.expander("🔍 Détails de l'erreur"):
                            st.code(result.stderr if result.stderr else result.stdout)
                
                except subprocess.TimeoutExpired:
                    st.error("❌ Timeout : le traitement a pris trop de temps (> 60s)")
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'exécution : {str(e)}")

# ============================================================================
# VISUALISATION - Colonne de droite
# ============================================================================

with col2:
    st.subheader("📊 Visualisation du Graphe")
    
    # Vérifier l'existence du fichier à chaque rafraîchissement
    graph_file = "graphe_connaissance.png"
    
    if os.path.exists(graph_file):
        try:
            # Utiliser le timestamp pour forcer le rechargement
            file_time = os.path.getmtime(graph_file)
            
            image = Image.open(graph_file)
            st.image(image, caption=f"Graphe généré via NetworkX (màj: {os.path.getmtime(graph_file)})")
            
            # Téléchargement
            with open(graph_file, "rb") as file:
                st.download_button(
                    label="⬇️ Télécharger le graphe",
                    data=file,
                    file_name="graphe_connaissance.png",
                    mime="image/png",
                    key=f"download_graph_{file_time}"
                )
        except Exception as e:
            st.error(f"Erreur lors du chargement de l'image : {str(e)}")
    else:
        st.info("👆 Générez d'abord le graphe pour voir la visualisation")
        st.image("https://via.placeholder.com/600x400?text=En+attente+de+g%C3%A9n%C3%A9ration")

# ============================================================================
# EXPORTS RDF - Section du bas
# ============================================================================

st.divider()
st.subheader("💾 Export RDF Multi-format")

tab1, tab2, tab3 = st.tabs(["🐢 Turtle (.ttl)", "📄 RDF/XML (.xml)", "📈 Statistiques"])

with tab1:
    if os.path.exists("knowledge_graph.ttl"):
        with open("knowledge_graph.ttl", "r", encoding="utf-8") as f:
            turtle_content = f.read()
            st.code(turtle_content, language="turtle", line_numbers=True)
            
            # Bouton de téléchargement
            st.download_button(
                label="⬇️ Télécharger Turtle",
                data=turtle_content,
                file_name="knowledge_graph.ttl",
                mime="text/turtle"
            )
    else:
        st.info("📝 En attente de génération...")
        st.code("""# Exemple de format Turtle
@prefix ex: <http://example.org/master2/ontology#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .

ex:Zoubida_Kedad a foaf:Person ;
    foaf:name "Zoubida Kedad" ;
    ex:worksAt ex:Universite_de_Versailles .""", language="turtle")

with tab2:
    if os.path.exists("knowledge_graph.xml"):
        with open("knowledge_graph.xml", "r", encoding="utf-8") as f:
            xml_content = f.read()
            st.code(xml_content, language="xml", line_numbers=True)
            
            # Bouton de téléchargement
            st.download_button(
                label="⬇️ Télécharger RDF/XML",
                data=xml_content,
                file_name="knowledge_graph.xml",
                mime="application/rdf+xml"
            )
    else:
        st.info("📝 En attente de génération...")
        st.code("""<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <!-- Contenu RDF/XML ici -->
</rdf:RDF>""", language="xml")

with tab3:
    st.markdown("### 📊 Analyse du Graphe Généré")
    
    if os.path.exists("knowledge_graph.ttl"):
        with open("knowledge_graph.ttl", "r", encoding="utf-8") as f:
            content = f.read()
            
            # Compter les éléments
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            
            with col_stat1:
                persons = content.count("foaf:Person")
                st.metric("👤 Personnes", persons)
                
            with col_stat2:
                orgs = content.count("schema:Organization") + content.count("schema:Place")
                st.metric("🏢 Organisations/Lieux", orgs)
            
            with col_stat3:
                relations = content.count("ex:worksAt") + content.count("ex:teaches") + \
                           content.count("ex:collaboratesWith") + content.count("ex:studiesAt")
                st.metric("🔗 Relations", relations)
            
            st.divider()
            
            # Classes OWL
            st.markdown("**Classes OWL détectées :**")
            classes = []
            if "owl:Class" in content:
                classes.append("✅ Classes OWL définies")
            if "owl:Restriction" in content:
                classes.append("✅ Restriction OWL (ValidatedCourse)")
            if "owl:ObjectProperty" in content:
                classes.append("✅ ObjectProperties")
            if "owl:DatatypeProperty" in content:
                classes.append("✅ DatatypeProperties")
            
            for cls in classes:
                st.text(cls)
    else:
        st.info("Générez d'abord un graphe pour voir les statistiques")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p><strong>Projet Master 2 Web Sémantique</strong> | Architecture T-Box/A-Box avec Réification</p>
    <p>Technologies : RDFLib 7.1.1 | spaCy 3.8.2 | Groq API (Llama-3.1-8B-Instant) | Streamlit</p>
    <p><em>Version 2.0 - 16 janvier 2026</em></p>
</div>
""", unsafe_allow_html=True)
