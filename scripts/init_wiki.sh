#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════
# 🏴‍☠️ YCC365 Wiki Bootstrap Script — Signé Ghost1o1
# ════════════════════════════════════════════════════════════════════
# Script qui pousse le wiki GitHub complet après initialisation.
#
# PRÉ-REQUIS:
#   1. Avoir visité https://github.com/187Ghost101/ycc365-ghost/wiki
#      une première fois (pour amorcer le .wiki.git)
#   2. Avoir un token GitHub avec scope `repo`
#
# Usage:
#   ./scripts/init_wiki.sh [<token>]
# ════════════════════════════════════════════════════════════════════

set -e

REPO="ycc365-ghost"
OWNER="187Ghost101"
WIKI_DIR=".ycc365-wiki-clone"

# ─── Couleurs ───
GOLD="\033[38;5;220m"
CYAN="\033[38;5;39m"
RED="\033[38;5;196m"
GREEN="\033[38;5;46m"
RESET="\033[0m"
BOLD="\033[1m"

echo -e "${GOLD}${BOLD}"
echo "    ▓██▓▒░       ░▒▓██▓    ╔══════════════════════════════════╗"
echo "     ▓█▓▒░ ░▒▓██▓▒░ ░▒▓█    ║  🏴‍☠️  YCC365 WIKI BOOTSTRAP  🏴‍☠️  ║"
echo "      █▒░ ░▓██▓▒░ ░▒▓█      ╚══════════════════════════════════╝"
echo "      ▓█▒░ ░▒░░░░░ ░▒▓█"
echo "       █▒░ ░▓██▓▒░ ░▒▓█"
echo "       ▓█▒░ ░▒██▓▒░ ░▒██"
echo "        █▓▒░ ░░░ ░▒██▓"
echo "        ░▒██▓▒░ ░▒██▓▒░"
echo "          ░▒▓██▓▒░ ░▒▓██▓"
echo -e "${RESET}"

# ─── Vérifications ───

# Token
if [ -z "$1" ]; then
    echo -e "${CYAN}[*] Demande du token GitHub...${RESET}"
    read -s -p "Token (scope repo): " TOKEN
    echo ""
else
    TOKEN="$1"
fi

if [ -z "$TOKEN" ]; then
    echo -e "${RED}[X] Token requis${RESET}"
    exit 1
fi

# Vérifier que le wiki est accessible
echo -e "${CYAN}[*] Vérification du wiki repo ${OWNER}/${REPO}.wiki...${RESET}"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/${OWNER}/${REPO}.wiki")

if [ "$HTTP_CODE" != "200" ]; then
    echo -e "${RED}[X] Le wiki n'existe pas encore!${RESET}"
    echo ""
    echo -e "${GOLD}PRÉ-REQUIS MANQUANT${RESET}"
    echo ""
    echo "Le wiki git repo doit d'abord être amorcé en visitant :"
    echo ""
    echo "  👉 ${CYAN}https://github.com/${OWNER}/${REPO}/wiki${RESET}"
    echo ""
    echo "Cliquez sur le bouton vert ${GREEN}'Create the first page'${RESET}"
    echo "Tapez n'importe quoi (ex: 'Bootstrap'), sauvegardez."
    echo "Puis relancez ce script:"
    echo ""
    echo "  $0"
    echo ""
    exit 1
fi

echo -e "${GREEN}[✓] Wiki repo accessible${RESET}"

# Cloner le wiki existant
echo -e "${CYAN}[*] Cloning wiki repo...${RESET}"
rm -rf "$WIKI_DIR"
git clone "https://${TOKEN}@github.com/${OWNER}/${REPO}.wiki.git" "$WIKI_DIR" 2>&1 | tail -3

# Sauvegarder la première page si elle existe
cd "$WIKI_DIR"
if [ -f "Bootstrap.md" ] || [ -f "bootstrap.md" ]; then
    echo -e "${CYAN}[*] Removing bootstrap page...${RESET}"
    rm -f "Bootstrap.md" "bootstrap.md"
fi

# Copier toutes les pages wiki depuis docs/wiki/
cd ..
echo -e "${CYAN}[*] Copying wiki pages from docs/wiki/...${RESET}"

cp docs/wiki/Home.md "$WIKI_DIR/Home.md"
cp docs/wiki/Architecture.md "$WIKI_DIR/"
cp docs/wiki/Attack-Surface.md "$WIKI_DIR/"
cp docs/wiki/Methodology.md "$WIKI_DIR/"
cp docs/wiki/Modules-Reference.md "$WIKI_DIR/"
cp docs/wiki/CVE-Mapping.md "$WIKI_DIR/"
cp docs/wiki/Threat-Model.md "$WIKI_DIR/"
cp docs/wiki/Testing-Guide.md "$WIKI_DIR/"
cp docs/wiki/IoT-Camera-Threats.md "$WIKI_DIR/"
cp docs/wiki/Defense-Recommendations.md "$WIKI_DIR/"
cp docs/wiki/Sample-Reports.md "$WIKI_DIR/"

cd "$WIKI_DIR"

# Stats
echo -e "${CYAN}[*] Pushing $(ls -1 *.md | wc -l) wiki pages...${RESET}"

git config user.name "Ghost1o1"
git config user.email "ghost1o1@ghost-sec.ca"
git add -A
git commit -m "🏴‍☠️ Wiki v1.1 — 11 pages techniques Signé Ghost1o1" 2>&1 | tail -3
git push origin master 2>&1 | tail -5

echo ""
echo -e "${GOLD}${BOLD}═══════════════════════════════════════════════════════${RESET}"
echo -e "${GOLD}${BOLD}  ✅ WIKI LIVE — https://github.com/${OWNER}/${REPO}/wiki ${RESET}"
echo -e "${GOLD}${BOLD}═══════════════════════════════════════════════════════${RESET}"
echo ""
echo -e "${GREEN}Pages publiées:${RESET}"
git log --oneline -1
echo ""
ls -la *.md | awk '{print "  📄 " $9 " (" $5 " bytes)"}'

echo ""
echo -e "${CYAN}Signé Ghost1o1 🏴‍☠️ — Wiki publié.${RESET}"
