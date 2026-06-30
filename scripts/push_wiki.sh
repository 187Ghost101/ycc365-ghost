#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════
# 🏴‍☠️ YCC365 Wiki Push — One-Liner Helper — Signé Ghost1o1
# ════════════════════════════════════════════════════════════════════
# Usage: ./scripts/push_wiki.sh <github_token>
# Ce script amorce + push le wiki en 1 commande.
# Pré-requis: avoir visité https://github.com/187Ghost101/ycc365-ghost/wiki
#             UNE fois (cliqué "Create the first page") pour amorcer le .wiki.git
# ════════════════════════════════════════════════════════════════════

set -e

REPO="ycc365-ghost"
OWNER="187Ghost101"
WIKI_DIR=".ycc365-wiki-clone"
TOKEN="${1:-${GH_TOKEN:-${GITHUB_TOKEN:-}}}"

GOLD="\033[38;5;220m"
CYAN="\033[38;5;39m"
RED="\033[38;5;196m"
GREEN="\033[38;5;46m"
RESET="\033[0m"
BOLD="\033[1m"

echo -e "${GOLD}${BOLD}"
echo "  🏴‍☠️  YCC365 WIKI PUSH — One-Liner  🏴‍☠️"
echo -e "${RESET}"

if [ -z "$TOKEN" ]; then
    echo -e "${RED}[X] Token manquant${RESET}"
    echo "Usage: $0 <github_token>"
    echo "   ou: export GH_TOKEN=ghp_xxx && $0"
    exit 1
fi

# Activer le wiki si nécessaire
echo -e "${CYAN}[1/5] Activation du wiki sur GitHub...${RESET}"
curl -s -X PATCH \
  -H "Authorization: token $TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "https://api.github.com/repos/${OWNER}/${REPO}" \
  -d '{"has_wiki": true}' > /dev/null

# Tester si le wiki repo existe déjà
echo -e "${CYAN}[2/5] Vérification du wiki repo...${RESET}"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: token $TOKEN" \
  "https://api.github.com/repos/${OWNER}/${REPO}.wiki")

if [ "$HTTP_CODE" != "200" ]; then
    echo -e "${RED}[!] Wiki repo pas encore matérialisé (HTTP $HTTP_CODE)${RESET}"
    echo ""
    echo "👉 Étape manuelle requise :"
    echo "   1. Ouvre: ${CYAN}https://github.com/${OWNER}/${REPO}/wiki${RESET}"
    echo "   2. Clique ${GREEN}'Create the first page'${RESET}"
    echo "   3. Tape n'importe quoi (ex: 'Bootstrap') et sauvegarde"
    echo "   4. Relance: $0 <token>"
    echo ""
    exit 2
fi

echo -e "${GREEN}[✓] Wiki repo accessible${RESET}"

# Cloner
echo -e "${CYAN}[3/5] Clone du wiki...${RESET}"
rm -rf "$WIKI_DIR"
git clone "https://${TOKEN}@github.com/${OWNER}/${REPO}.wiki.git" "$WIKI_DIR" 2>&1 | tail -2

cd "$WIKI_DIR"

# Supprimer la page bootstrap si elle existe
rm -f Bootstrap.md bootstrap.md Home.md home.md 2>/dev/null || true

# Copier les 11 pages depuis docs/wiki/
cd ..
echo -e "${CYAN}[4/5] Copie de 11 pages depuis docs/wiki/...${RESET}"

for f in Home.md Architecture.md Attack-Surface.md Methodology.md \
         Modules-Reference.md CVE-Mapping.md Threat-Model.md \
         Testing-Guide.md IoT-Camera-Threats.md \
         Defense-Recommendations.md Sample-Reports.md; do
    if [ -f "docs/wiki/$f" ]; then
        cp "docs/wiki/$f" "$WIKI_DIR/$f"
        echo "  📄 $f"
    else
        echo -e "  ${RED}[X] $f manquant dans docs/wiki/${RESET}"
    fi
done

cd "$WIKI_DIR"

# Commit + Push
echo -e "${CYAN}[5/5] Commit + Push...${RESET}"
git config user.name "Ghost1o1"
git config user.email "ghost1o1@ghost-sec.ca"
git add -A
git commit -m "🏴‍☠️ Wiki v1.2 — 11 pages techniques (Modules 1+2+4+5)" 2>&1 | tail -2
git push origin master 2>&1 | tail -3

echo ""
echo -e "${GOLD}${BOLD}═══════════════════════════════════════════════════════${RESET}"
echo -e "${GOLD}${BOLD}  ✅ WIKI LIVE${RESET}"
echo -e "${GOLD}${BOLD}═══════════════════════════════════════════════════════${RESET}"
echo ""
echo -e "🔗 ${CYAN}https://github.com/${OWNER}/${REPO}/wiki${RESET}"
echo ""
echo -e "${GREEN}Pages publiées:${RESET}"
ls -la *.md | awk '{printf "  📄 %-35s %7d bytes\n", $9, $5}'
echo ""
echo -e "${CYAN}Signé Ghost1o1 🏴‍☠️${RESET}"
