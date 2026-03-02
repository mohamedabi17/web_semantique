#!/bin/bash
# Script de lancement de l'interface Streamlit

echo "🚀 Lancement de l'interface web Streamlit..."
echo ""

# Se déplacer vers le répertoire racine du projet
cd "$(dirname "$0")/.." || exit 1

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "❌ Environnement virtuel non trouvé. Créez-le avec : python3 -m venv venv"
    exit 1
fi

# Activer l'environnement virtuel
source venv/bin/activate

# Vérifier si Streamlit est installé
if ! python -c "import streamlit" 2>/dev/null; then
    echo "📦 Installation de Streamlit..."
    pip install streamlit pillow -q
fi

# Lancer Streamlit
echo "✅ Ouverture dans le navigateur..."
echo ""
echo "📍 URL locale : http://localhost:8501"
echo "⚠️  Appuyez sur Ctrl+C pour arrêter le serveur"
echo ""

streamlit run app_streamlit.py
