#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface Streamlit — Knowledge Graph Extraction
Master 2 Web Sémantique — Neuro-Symbolic Architecture
"""

import streamlit as st
import os
import sys
from PIL import Image
import subprocess
import tempfile
from pathlib import Path
import json
from datetime import datetime
import time

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="KG Extractor · Web Sémantique",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS  — dark glass-morphism + neon accent
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

:root {
  --bg-deep:    #0a0e1a;
  --bg-card:    rgba(16, 22, 40, 0.85);
  --bg-glass:   rgba(255,255,255,0.04);
  --border:     rgba(99,179,237,0.15);
  --accent-1:   #63b3ed;
  --accent-2:   #76e4b0;
  --accent-3:   #f6ad55;
  --accent-4:   #fc8181;
  --accent-5:   #b794f4;
  --text-main:  #e2e8f0;
  --text-muted: #718096;
  --text-dim:   #4a5568;
}

.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1423 40%, #0a1628 100%);
    background-attachment: fixed;
    color: var(--text-main);
}
.block-container { padding: 1.5rem 2.5rem 3rem; max-width: 1600px; }

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1525 0%, #0a1020 100%) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text-main) !important; }

[data-testid="metric-container"] {
    background: var(--bg-glass);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.7rem 1rem;
    margin-bottom: 0.5rem;
}
[data-testid="metric-container"] label { color: var(--text-muted) !important; font-size: 0.75rem; }
[data-testid="metric-container"] [data-testid="metric-value"] { color: var(--accent-1) !important; font-weight: 700; }

.stButton > button {
    background: linear-gradient(135deg, #1a365d 0%, #2a4a8a 100%) !important;
    border: 1px solid var(--accent-1) !important;
    color: var(--accent-1) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em !important;
    transition: all 0.2s ease !important;
    padding: 0.5rem 1.2rem !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #2a4a8a 0%, #3a5f9a 100%) !important;
    box-shadow: 0 0 20px rgba(99,179,237,0.3) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1a4fd6 0%, #5b21b6 100%) !important;
    border: 1px solid var(--accent-5) !important;
    color: #fff !important;
    font-size: 1rem !important;
    padding: 0.7rem 2rem !important;
    box-shadow: 0 0 24px rgba(91,33,182,0.4) !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 0 36px rgba(99,179,237,0.5) !important;
    transform: translateY(-2px) !important;
}

.stTextArea textarea {
    background: rgba(10,14,26,0.9) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-main) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.92rem !important;
    caret-color: var(--accent-1);
    transition: border-color 0.2s;
}
.stTextArea textarea:focus {
    border-color: var(--accent-1) !important;
    box-shadow: 0 0 0 2px rgba(99,179,237,0.15) !important;
}

.stSelectbox > div > div {
    background: rgba(10,14,26,0.9) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-main) !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid var(--border);
    gap: 0.5rem;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 8px 8px 0 0 !important;
    color: var(--text-muted) !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
    padding: 0.5rem 1.2rem !important;
}
.stTabs [aria-selected="true"] {
    background: var(--bg-glass) !important;
    border-color: var(--border) !important;
    border-bottom-color: transparent !important;
    color: var(--accent-1) !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-top: none;
    border-radius: 0 0 10px 10px;
    padding: 1.2rem !important;
}

.streamlit-expanderHeader {
    background: var(--bg-glass) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-main) !important;
    font-weight: 500 !important;
}
.streamlit-expanderContent {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
}

.stCodeBlock { border-radius: 10px !important; border: 1px solid var(--border) !important; }
.stCodeBlock pre { background: #0d1117 !important; font-family: 'JetBrains Mono', monospace !important; font-size: 0.8rem !important; }

hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--accent-1), var(--accent-5)) !important;
    border-radius: 4px !important;
    box-shadow: 0 0 10px rgba(99,179,237,0.5) !important;
}
.stProgress > div > div {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 4px !important;
}

.stAlert { border-radius: 10px !important; border-left-width: 4px !important; }

.stDownloadButton > button {
    background: rgba(118,228,176,0.1) !important;
    border: 1px solid rgba(118,228,176,0.3) !important;
    color: var(--accent-2) !important;
    border-radius: 7px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}
.stDownloadButton > button:hover {
    background: rgba(118,228,176,0.18) !important;
    box-shadow: 0 0 14px rgba(118,228,176,0.25) !important;
}

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

/* Custom components */
.hero-wrap {
    background: linear-gradient(135deg, rgba(26,53,93,0.6) 0%, rgba(91,33,182,0.35) 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2.2rem 2.8rem;
    margin-bottom: 1.8rem;
    position: relative;
    overflow: hidden;
}
.hero-wrap::before {
    content: '';
    position: absolute; top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(ellipse at 70% 30%, rgba(99,179,237,0.07) 0%, transparent 60%);
    pointer-events: none;
}
.hero-title { font-size: 2rem; font-weight: 700; color: #fff; letter-spacing: -0.02em; margin: 0 0 0.3rem; line-height: 1.2; }
.hero-title span { color: var(--accent-1); }
.hero-sub { color: var(--text-muted); font-size: 0.92rem; margin: 0; font-weight: 400; }
.hero-badges { margin-top: 1rem; display: flex; gap: 0.5rem; flex-wrap: wrap; }
.badge {
    display: inline-flex; align-items: center; gap: 0.35rem;
    background: rgba(99,179,237,0.1); border: 1px solid rgba(99,179,237,0.25);
    color: var(--accent-1); font-size: 0.75rem; font-weight: 600;
    padding: 0.25rem 0.65rem; border-radius: 999px;
}
.badge.green  { background:rgba(118,228,176,0.1); border-color:rgba(118,228,176,0.25); color:var(--accent-2); }
.badge.amber  { background:rgba(246,173, 85,0.1); border-color:rgba(246,173, 85,0.25); color:var(--accent-3); }
.badge.purple { background:rgba(183,148,244,0.1); border-color:rgba(183,148,244,0.25); color:var(--accent-5); }

.section-heading {
    font-size: 0.72rem; font-weight: 600; letter-spacing: 0.12em;
    text-transform: uppercase; color: var(--text-muted);
    margin: 0 0 0.75rem; padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
}

.glass-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: 12px; padding: 1.4rem; margin-bottom: 1rem;
    backdrop-filter: blur(12px);
}

.status-row {
    display: flex; align-items: center; gap: 0.65rem;
    padding: 0.55rem 0.9rem; border-radius: 8px;
    margin-bottom: 0.4rem; border: 1px solid transparent; font-size: 0.85rem;
}
.status-ok    { background:rgba(118,228,176,0.07); border-color:rgba(118,228,176,0.2); }
.status-warn  { background:rgba(246,173, 85,0.07); border-color:rgba(246,173, 85,0.2); }
.status-error { background:rgba(252,129,129,0.07); border-color:rgba(252,129,129,0.2); }
.status-dot { width:7px; height:7px; border-radius:50%; flex-shrink:0; }
.dot-ok    { background:var(--accent-2); box-shadow:0 0 6px var(--accent-2); }
.dot-warn  { background:var(--accent-3); box-shadow:0 0 6px var(--accent-3); }
.dot-error { background:var(--accent-4); box-shadow:0 0 6px var(--accent-4); }
.status-name   { font-weight:600; flex:1; color:var(--text-main); }
.status-detail { color:var(--text-muted); font-size:0.78rem; }

.pipe-step {
    display:flex; align-items:flex-start; gap:0.9rem;
    padding:0.7rem 1rem; border-radius:8px;
    border:1px solid var(--border); background:var(--bg-glass);
    margin-bottom:0.5rem; transition:border-color 0.3s,background 0.3s;
}
.pipe-step.active { border-color:var(--accent-1); background:rgba(99,179,237,0.06); }
.pipe-step.done   { border-color:rgba(118,228,176,0.3); background:rgba(118,228,176,0.04); }
.pipe-icon  { font-size:1.1rem; margin-top:0.05rem; }
.pipe-label { font-size:0.88rem; font-weight:600; color:var(--text-main); }
.pipe-desc  { font-size:0.78rem; color:var(--text-muted); margin-top:0.1rem; }

.stat-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:0.8rem; margin-bottom:1rem; }
.stat-card {
    background:var(--bg-glass); border:1px solid var(--border);
    border-radius:10px; padding:1rem; text-align:center;
}
.stat-value { font-size:1.8rem; font-weight:700; line-height:1; margin-bottom:0.2rem; }
.stat-label { font-size:0.75rem; color:var(--text-muted); font-weight:500; text-transform:uppercase; letter-spacing:0.06em; }

.log-success { color:var(--accent-2) !important; }
.log-info    { color:var(--accent-1) !important; }
.log-warn    { color:var(--accent-3) !important; }
.log-error   { color:var(--accent-4) !important; }
.log-rel     { color:var(--accent-5) !important; }

.sidebar-brand { text-align:center; padding:1.2rem 0 0.8rem; border-bottom:1px solid var(--border); margin-bottom:1rem; }
.sidebar-brand h2 { font-size:1.05rem; font-weight:700; color:#fff; margin:0; }
.sidebar-brand p  { font-size:0.72rem; color:var(--text-muted); margin:0.2rem 0 0; }

[data-testid="stCheckbox"] label { color:var(--text-muted) !important; font-size:0.88rem !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def check_modules_status():
    status = {"modules": {}, "overall": True, "score": 100}
    checks = [
        ("hybrid_ner_module.py",         "NER Hybride",         "7 couches actives"),
        ("owl_reasoning_engine.py",       "OWL Reasoning",       "Validation + Inférence"),
        ("confidence_scorer.py",          "Confidence Scorer",   "Multi-sources"),
        ("kg_extraction_semantic_web.py", "Pipeline Principal",  "Neuro-Symbolique"),
    ]
    for fname, label, detail in checks:
        ok = os.path.exists(fname)
        status["modules"][label] = {"ok": ok, "detail": detail if ok else "Fichier manquant"}
        if not ok:
            status["overall"] = False
            status["score"] -= 25
    try:
        import spacy
        nlp = spacy.load("fr_core_news_sm")
        status["modules"]["spaCy fr_core_news_sm"] = {"ok": True, "detail": f"v{spacy.__version__}"}
    except Exception:
        status["modules"]["spaCy fr_core_news_sm"] = {"ok": False, "detail": "Non installé"}
        status["overall"] = False
        status["score"] -= 15
    try:
        import rdflib
        status["modules"]["RDFLib"] = {"ok": True, "detail": f"v{rdflib.__version__}"}
    except Exception:
        status["modules"]["RDFLib"] = {"ok": False, "detail": "Non installé"}
        status["overall"] = False
    return status


def read_graph_file(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None


def graph_stats(content):
    if not content:
        return {"persons": 0, "orgs": 0, "topics": 0, "relations": 0, "triples": 0}
    return {
        "persons":   content.count("foaf:Person"),
        "orgs":      content.count("schema:Organization") + content.count("schema:Place"),
        "topics":    content.count("ex:Document") + content.count("ex:Topic"),
        "relations": sum(content.count(r) for r in
                         ["ex:worksAt","ex:teachesSubject","ex:author","ex:manages",
                          "ex:studiesAt","ex:collaboratesWith","ex:uses","ex:locatedIn"]),
        "triples":   content.count(" .") - content.count("..."),
    }


def render_log_line(line):
    if not line.strip():
        return None
    if any(x in line for x in ["✓", "✅", "PASS"]):
        cls = "log-success"
    elif any(x in line for x in ["🤖", "Groq", "LLM", "Relation"]):
        cls = "log-rel"
    elif any(x in line for x in ["⚠️", "WARN", "Type", "rejeté"]):
        cls = "log-warn"
    elif any(x in line for x in ["❌", "Error", "FAIL", "Erreur"]):
        cls = "log-error"
    elif any(x in line for x in ["MODULE", "COUCHE", "===", "───"]):
        cls = "log-info"
    else:
        cls = ""
    esc = line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    return f'<span class="{cls}">{esc}</span>' if cls else f'<span style="color:var(--text-muted)">{esc}</span>'


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
modules_status = check_modules_status()

with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
      <h2>🕸️ KG Extractor</h2>
      <p>Master 2 · Web Sémantique</p>
    </div>
    """, unsafe_allow_html=True)

    all_ok = modules_status["overall"]
    score  = modules_status["score"]
    color  = "var(--accent-2)" if all_ok else "var(--accent-4)"
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:0.6rem;padding:0.6rem 0.8rem;
         background:{'rgba(118,228,176,0.07)' if all_ok else 'rgba(252,129,129,0.07)'};
         border:1px solid {'rgba(118,228,176,0.2)' if all_ok else 'rgba(252,129,129,0.2)'};
         border-radius:8px;margin-bottom:1rem;">
      <span style="color:{color};font-size:0.55rem;">&#9679;</span>
      <span style="font-size:0.82rem;font-weight:600;color:{color};">
        {'Système opérationnel' if all_ok else 'Modules manquants'}
      </span>
      <span style="margin-left:auto;font-size:0.75rem;color:var(--text-muted);">{score}%</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="section-heading">Modules</p>', unsafe_allow_html=True)
    for name, info in modules_status["modules"].items():
        cls  = "status-ok" if info["ok"] else "status-error"
        dcls = "dot-ok"    if info["ok"] else "dot-error"
        st.markdown(f"""
        <div class="status-row {cls}">
          <div class="status-dot {dcls}"></div>
          <span class="status-name">{name}</span>
          <span class="status-detail">{info['detail']}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section-heading">Graphe courant</p>', unsafe_allow_html=True)
    ttl_content = read_graph_file("outputs/knowledge_graph_output.ttl") or \
                  read_graph_file("knowledge_graph.ttl")
    stats = graph_stats(ttl_content)

    if ttl_content:
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Triplets",  stats["triples"])
            st.metric("Personnes", stats["persons"])
        with c2:
            st.metric("Relations", stats["relations"])
            st.metric("Org/Lieu",  stats["orgs"])
    else:
        st.caption("Aucun graphe généré")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p class="section-heading">Actions</p>', unsafe_allow_html=True)
    if st.button("🗑️ Vider le cache"):
        for f in ["knowledge_graph.ttl","knowledge_graph.xml",
                  "graphe_connaissance.png","texte_temp.txt",
                  "outputs/knowledge_graph_output.ttl"]:
            if os.path.exists(f):
                os.remove(f)
        st.success("Cache vidé !")
        st.rerun()
    if st.button("🔄 Rafraîchir"):
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="text-align:center;color:var(--text-dim);font-size:0.72rem;line-height:1.8;">
      Groq · Llama-3.1-8B<br>RDFLib · spaCy · owlrl<br>
      {datetime.now().strftime('%d %b %Y')}
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
  <h1 class="hero-title">Knowledge Graph <span>Extraction</span></h1>
  <p class="hero-sub">Architecture Neuro-Symbolique · spaCy + Groq Llama-3.1 + OWL/RDFS T-Box/A-Box</p>
  <div class="hero-badges">
    <span class="badge">🧠 NER Hybride 7 couches</span>
    <span class="badge green">✓ OWL Reasoning</span>
    <span class="badge amber">⚡ Groq API</span>
    <span class="badge purple">🎯 Confiance multi-sources</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN COLUMNS
# ─────────────────────────────────────────────────────────────────────────────
col_input, col_sep, col_output = st.columns([5, 0.08, 5])

with col_sep:
    st.markdown("""<div style="width:1px;background:var(--border);height:100%;
        min-height:500px;margin:auto;"></div>""", unsafe_allow_html=True)


# ══ LEFT — Input ══════════════════════════════════════════════════════════════
with col_input:
    st.markdown('<p class="section-heading">Entrée texte</p>', unsafe_allow_html=True)

    examples = {
        "🎓 Enseignement · NER complet":
            "Zoubida Kedad enseigne le Web Sémantique à l'Université de Versailles. Elle a écrit plusieurs articles sur RDF.",
        "💼 Multi-entités · Verbes riches":
            "Emmanuel Macron travaille à Paris. Il dirige la France et collabore avec l'Union Européenne.",
        "✍️ Propriété author · Documents":
            "Victor Hugo a écrit Les Misérables. Albert Camus a écrit L'Étranger.",
        "🏢 Organisations · Localisations":
            "Microsoft est situé à Redmond. Google travaille à Mountain View. Apple est basé à Cupertino.",
        "🔬 Validation OWL · Reasoning":
            "Alice enseigne la physique. Bob étudie les mathématiques. Charlie travaille à l'université.",
        "🧬 NER Hybride · 7 couches":
            "Marie Dupont travaille à l'Université Paris-Saclay. Elle enseigne l'intelligence artificielle et étudie le deep learning.",
        "✏️ Texte personnalisé": "",
    }

    selected = st.selectbox("Exemple de démonstration", list(examples.keys()),
                            help="Textes optimisés pour illustrer chaque module")
    user_input = st.text_area("Texte à analyser", value=examples[selected],
                              height=160,
                              placeholder="Entrez un texte : personnes, lieux, organisations, concepts…",
                              label_visibility="collapsed")

    st.markdown("""
    <div style="display:flex;gap:1rem;flex-wrap:wrap;margin:0.5rem 0 1rem;
         font-size:0.78rem;color:var(--text-muted);">
      <span>🔵 enseigner → <code style="color:var(--accent-1)">teachesSubject</code></span>
      <span>🟢 écrire → <code style="color:var(--accent-2)">author</code></span>
      <span>🟡 travailler → <code style="color:var(--accent-3)">worksAt</code></span>
      <span>🟣 diriger → <code style="color:var(--accent-5)">manages</code></span>
    </div>
    """, unsafe_allow_html=True)

    show_logs = st.checkbox("Afficher les logs pipeline", value=True)

    generate_btn = st.button(
        "⚡ Générer le graphe RDF", type="primary",
        use_container_width=True,
        disabled=not modules_status["overall"],
    )

    pipeline_placeholder = st.empty()

    PIPELINE_STEPS = [
        ("📄", "Préparation",   "Écriture du texte source"),
        ("🔍", "NER Hybride",   "Module 0++ · 7 couches"),
        ("🔧", "Normalisation", "Déduplication + typage"),
        ("🤖", "LLM Groq",      "Llama-3.1 · extraction relations"),
        ("⚙️", "OWL Reasoning", "Validation domain / range"),
        ("📊", "Confidence",    "Scores multi-sources"),
        ("💾", "Sérialisation", "Turtle + RDF/XML"),
    ]

    def render_pipeline(active_idx=-1, done_all=False):
        html = ""
        for i, (icon, label, desc) in enumerate(PIPELINE_STEPS):
            if done_all or i < active_idx:
                cls, prefix = "done",   "✓"
            elif i == active_idx:
                cls, prefix = "active", "→"
            else:
                cls, prefix = "",       str(i + 1)
            html += (f'<div class="pipe-step {cls}">'
                     f'<span class="pipe-icon">{icon}</span>'
                     f'<div><div class="pipe-label">{prefix} · {label}</div>'
                     f'<div class="pipe-desc">{desc}</div></div></div>')
        return html


# ══ PROCESSING ════════════════════════════════════════════════════════════════
if generate_btn:
    if not user_input.strip():
        st.error("Veuillez saisir un texte avant de lancer l'extraction.")
    else:
        with col_input:
            progress_bar = st.progress(0)
            with open("texte_temp.txt", "w", encoding="utf-8") as f:
                f.write(user_input)

            for step in range(len(PIPELINE_STEPS)):
                pipeline_placeholder.markdown(render_pipeline(step), unsafe_allow_html=True)
                progress_bar.progress(int((step + 1) / len(PIPELINE_STEPS) * 90))
                time.sleep(0.18)

            try:
                result = subprocess.run(
                    ["python3", "kg_extraction_semantic_web.py"],
                    capture_output=True, text=True, timeout=90, cwd=os.getcwd(),
                )
                progress_bar.progress(100)
                pipeline_placeholder.markdown(render_pipeline(done_all=True), unsafe_allow_html=True)
                time.sleep(0.5)
                pipeline_placeholder.empty()
                progress_bar.empty()

                if result.returncode == 0:
                    st.success("Extraction terminée — graphe RDF généré avec succès.", icon="✅")

                    if show_logs and result.stdout:
                        st.markdown('<p class="section-heading" style="margin-top:1rem;">Logs pipeline</p>',
                                    unsafe_allow_html=True)
                        lines = result.stdout.split("\n")
                        chunks = {
                            "🔍 NER Hybride": [l for l in lines if any(x in l for x in
                                ["MODULE 0","COUCHE","Entité","EntityRuler",
                                 "PROPN","Normali","Dédup","Filtrage"])],
                            "⚙️ OWL & Relations": [l for l in lines if any(x in l for x in
                                ["→","Relation","worksAt","teaches","author",
                                 "locatedIn","manages","OWL","Groq","LLM","Priorité"])],
                            "📊 Confidence": [l for l in lines if any(x in l for x in
                                ["confidence","Confiance","Score","STAT","Min:","Max:","Mean:"])],
                        }
                        for section, log_lines in chunks.items():
                            if log_lines:
                                with st.expander(section, expanded=(section == "⚙️ OWL & Relations")):
                                    rendered = [render_log_line(l) for l in log_lines if l.strip()]
                                    body = "<br>".join(r for r in rendered if r)
                                    st.markdown(
                                        f'<div style="font-family:\'JetBrains Mono\',monospace;'
                                        f'font-size:0.78rem;line-height:1.8;background:#0d1117;'
                                        f'border-radius:8px;padding:1rem;">{body}</div>',
                                        unsafe_allow_html=True)
                else:
                    st.warning("Le script s'est terminé avec des erreurs.")
                    with st.expander("Détail"):
                        st.code(result.stderr or result.stdout)

            except subprocess.TimeoutExpired:
                pipeline_placeholder.empty(); progress_bar.empty()
                st.error("Timeout : le traitement a dépassé 90 secondes.")
            except Exception as exc:
                pipeline_placeholder.empty(); progress_bar.empty()
                st.error(f"Erreur : {exc}")


# ══ RIGHT — Output ═════════════════════════════════════════════════════════════
with col_output:
    st.markdown('<p class="section-heading">Visualisation & Export</p>', unsafe_allow_html=True)

    tab_graph, tab_ttl, tab_xml, tab_stats = st.tabs(
        ["🗺️ Graphe", "🐢 Turtle", "📄 RDF/XML", "📊 Stats"])

    with tab_graph:
        graph_file = "graphe_connaissance.png"
        if os.path.exists(graph_file):
            try:
                ts  = os.path.getmtime(graph_file)
                img = Image.open(graph_file)
                st.image(img, use_container_width=True)
                with open(graph_file, "rb") as fh:
                    st.download_button("⬇️ Télécharger PNG", data=fh,
                                       file_name="knowledge_graph.png",
                                       mime="image/png", key=f"dl_png_{ts}")
            except Exception as e:
                st.error(f"Erreur image : {e}")
        else:
            st.markdown("""
            <div class="glass-card" style="text-align:center;padding:3rem 2rem;min-height:260px;
                 display:flex;flex-direction:column;align-items:center;justify-content:center;">
              <div style="font-size:3rem;margin-bottom:0.8rem;">🕸️</div>
              <div style="font-size:0.9rem;color:var(--text-muted);">
                Le graphe apparaîtra ici<br>après la génération
              </div>
            </div>""", unsafe_allow_html=True)

    with tab_ttl:
        ttl = read_graph_file("outputs/knowledge_graph_output.ttl") \
           or read_graph_file("knowledge_graph.ttl")
        if ttl:
            st.code(ttl, language="turtle", line_numbers=True)
            st.download_button("⬇️ Télécharger .ttl", data=ttl,
                               file_name="knowledge_graph.ttl", mime="text/turtle")
        else:
            st.code("""# Exemple de sortie Turtle
@prefix ex:   <http://example.org/master2/ontology#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .

ex:Zoubida_Kedad a foaf:Person ;
    foaf:name "Zoubida Kedad" ;
    ex:worksAt ex:Universite_de_Versailles ;
    ex:teachesSubject ex:Web_Semantique .""", language="turtle")

    with tab_xml:
        xml = read_graph_file("outputs/knowledge_graph_output.xml") \
           or read_graph_file("knowledge_graph.xml")
        if xml:
            st.code(xml, language="xml", line_numbers=True)
            st.download_button("⬇️ Télécharger .xml", data=xml,
                               file_name="knowledge_graph.xml", mime="application/rdf+xml")
        else:
            st.code("""<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:ex="http://example.org/master2/ontology#">
  <!-- Le graphe sera sérialisé ici -->
</rdf:RDF>""", language="xml")

    with tab_stats:
        ttl_content = read_graph_file("outputs/knowledge_graph_output.ttl") \
                   or read_graph_file("knowledge_graph.ttl")
        s = graph_stats(ttl_content)

        if ttl_content:
            st.markdown(f"""
            <div class="stat-grid">
              <div class="stat-card">
                <div class="stat-value" style="color:var(--accent-1)">{s['triples']}</div>
                <div class="stat-label">Triplets RDF</div>
              </div>
              <div class="stat-card">
                <div class="stat-value" style="color:var(--accent-2)">{s['relations']}</div>
                <div class="stat-label">Relations</div>
              </div>
              <div class="stat-card">
                <div class="stat-value" style="color:var(--accent-3)">{s['persons']}</div>
                <div class="stat-label">Personnes</div>
              </div>
            </div>
            <div class="stat-grid">
              <div class="stat-card">
                <div class="stat-value" style="color:var(--accent-5)">{s['orgs']}</div>
                <div class="stat-label">Org / Lieux</div>
              </div>
              <div class="stat-card">
                <div class="stat-value" style="color:var(--accent-4)">{s['topics']}</div>
                <div class="stat-label">Topics</div>
              </div>
              <div class="stat-card">
                <div class="stat-value" style="color:var(--text-muted)">
                  {'✓' if 'owl:Class' in ttl_content else '✗'}
                </div>
                <div class="stat-label">Classes OWL</div>
              </div>
            </div>""", unsafe_allow_html=True)

            st.markdown('<p class="section-heading" style="margin-top:0.5rem;">Conformité OWL</p>',
                        unsafe_allow_html=True)
            for tag, label in [
                ("owl:Class",            "Classes OWL"),
                ("owl:ObjectProperty",   "ObjectProperties"),
                ("owl:DatatypeProperty", "DatatypeProperties"),
                ("owl:Restriction",      "Restrictions OWL"),
                ("ex:confidence",        "Confidence scores"),
            ]:
                ok   = tag in ttl_content
                cls  = "status-ok" if ok else "status-error"
                dcls = "dot-ok"    if ok else "dot-error"
                st.markdown(f"""
                <div class="status-row {cls}" style="padding:0.4rem 0.8rem;">
                  <div class="status-dot {dcls}"></div>
                  <span class="status-name" style="font-size:0.82rem;">{label}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="glass-card" style="text-align:center;padding:2.5rem;">
              <div style="font-size:2rem;margin-bottom:0.6rem;">📊</div>
              <div style="color:var(--text-muted);font-size:0.88rem;">
                Les statistiques apparaîtront après génération
              </div>
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"""
<div style="border-top:1px solid var(--border);padding-top:1.2rem;
     display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.8rem;">
  <div style="color:var(--text-dim);font-size:0.78rem;">
    🎓 Master 2 Web Sémantique · Architecture Neuro-Symbolique Hybride
  </div>
  <div style="display:flex;gap:1rem;font-size:0.75rem;color:var(--text-dim);">
    <span>RDFLib</span><span>·</span><span>spaCy</span><span>·</span>
    <span>Groq Llama-3.1</span><span>·</span><span>Streamlit</span><span>·</span>
    <span>owlrl</span>
  </div>
  <div style="color:var(--text-dim);font-size:0.78rem;">{datetime.now().strftime('%d %B %Y')}</div>
</div>
""", unsafe_allow_html=True)
