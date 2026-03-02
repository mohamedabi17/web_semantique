#!/bin/bash
# Script de lancement automatique pour la démo Streamlit
# Vérifie les modules et lance l'interface

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Fonction pour afficher un en-tête
print_header() {
    echo -e "\n${BOLD}${CYAN}============================================================${NC}"
    echo -e "${BOLD}${CYAN}$1${NC}"
    echo -e "${BOLD}${CYAN}============================================================${NC}\n"
}

# Fonction pour afficher un message de succès
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Fonction pour afficher un message d'erreur
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Fonction pour afficher un avertissement
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Fonction pour afficher une info
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Début du script
print_header "🎯 LANCEMENT DEMO STREAMLIT - Web Sémantique"

# Étape 1 : Vérification des modules
print_info "Étape 1/3 : Vérification des modules..."

if python3 test_demo_modules.py > /tmp/test_output.log 2>&1; then
    print_success "Tous les modules sont opérationnels (100%)"
else
    print_warning "Certains modules peuvent être manquants"
    print_info "Voir les détails : cat /tmp/test_output.log"
fi

# Étape 2 : Vérification de la clé API Groq (optionnel)
print_info "Étape 2/3 : Vérification de la clé API..."

if [ -f ".env" ]; then
    if grep -q "GROQ_API_KEY" .env; then
        print_success "Clé API Groq configurée"
    else
        print_warning "Clé API Groq non trouvée dans .env"
        print_info "Certaines fonctionnalités LLM peuvent être limitées"
    fi
else
    print_warning "Fichier .env non trouvé"
    print_info "Créez un fichier .env avec : GROQ_API_KEY=votre_cle"
fi

# Étape 3 : Lancement de Streamlit
print_info "Étape 3/3 : Lancement de l'interface Streamlit..."

echo ""
echo -e "${BOLD}${GREEN}🚀 Lancement de Streamlit...${NC}"
echo ""
print_info "L'interface s'ouvrira automatiquement dans votre navigateur"
print_info "URL : http://localhost:8501"
echo ""
print_info "Pour arrêter l'application : Ctrl+C"
echo ""

# Lancer Streamlit
streamlit run app_streamlit.py
