#!/usr/bin/env bash
# ════════════════════════════════════════════════════════════════════
# 🏴‍☠️ YCC365 GHOST — Build Script
# Signé Ghost1o1 — Build APK en 1 commande
# ════════════════════════════════════════════════════════════════════
set -e

GOLD="\033[38;5;220m"
CYAN="\033[38;5;39m"
RED="\033[38;5;196m"
GRAY="\033[38;5;245m"
RESET="\033[0m"
BOLD="\033[1m"

banner() {
    echo -e "${GOLD}${BOLD}"
    echo "    ╔══════════════════════════════════════╗"
    echo "    ║   🏴‍☠️  YCC365 GHOST BUILDER  🏴‍☠️    ║"
    echo "    ║       Signé Ghost1o1 • v1.0.0       ║"
    echo "    ╚══════════════════════════════════════╝"
    echo -e "${RESET}"
}

check_deps() {
    echo -e "${CYAN}[*] Vérification des dépendances...${RESET}"
    local missing=()

    for tool in aapt apksigner zipalign javac keytool zip; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            missing+=("$tool")
        fi
    done

    if [ ${#missing[@]} -gt 0 ]; then
        echo -e "${RED}[!] Outils manquants : ${missing[*]}${RESET}"
        echo -e "${CYAN}[*] Installation Debian/Ubuntu :${RESET}"
        echo "    sudo apt install aapt apksigner zipalign default-jdk-headless zip"
        exit 1
    fi

    echo -e "    ${GOLD}[✓]${RESET} Tous les outils présents"
}

check_android_jar() {
    echo -e "${CYAN}[*] Recherche android.jar (API 33)...${RESET}"

    local candidates=(
        "/opt/android-sdk/platforms/android-33/android.jar"
        "/usr/lib/android-sdk/platforms/android-33/android.jar"
        "$HOME/Android/Sdk/platforms/android-33/android.jar"
    )

    for path in "${candidates[@]}"; do
        if [ -f "$path" ]; then
            echo "$path"
            return 0
        fi
    done

    echo -e "${RED}[!] android.jar introuvable${RESET}"
    echo "    Voir docs/ARCHITECTURE.md pour l'installation"
    return 1
}

build_apk() {
    local ANDROID_JAR="$1"
    local AAPT=$(which aapt)
    local D8=$(find /usr/lib/android-sdk/build-tools -name "d8" -type f 2>/dev/null | head -1)
    local ZIPALIGN=$(which zipalign)
    local APKSIGNER=$(which apksigner)
    local KEYTOOL=$(which keytool)

    echo -e "${CYAN}[*] Création keystore...${RESET}"
    mkdir -p build
    "$KEYTOOL" -genkey -v \
        -keystore build/ghost1o1.keystore \
        -alias ghost1o1 \
        -keyalg RSA -keysize 2048 \
        -validity 10000 \
        -storepass ghost101 \
        -keypass ghost101 \
        -dname "CN=Ghost1o1, OU=Pentest, O=Ghost1o1, L=Quebec, ST=QC, C=CA" 2>&1 | tail -1
    echo -e "    ${GOLD}[✓]${RESET} Keystore Ghost1o1 généré"

    echo -e "${CYAN}[*] Compilation Java...${RESET}"
    mkdir -p build/classes
    javac -source 1.8 -target 1.8 \
        -bootclasspath "$ANDROID_JAR" \
        -classpath "$ANDROID_JAR" \
        -d build/classes \
        src/com/ghost1o1/ycc365/MainActivity.java 2>&1 | grep -v "warning" || true
    echo -e "    ${GOLD}[✓]${RESET} MainActivity.java → .class"

    echo -e "${CYAN}[*] Génération Dalvik DEX...${RESET}"
    mkdir -p build/dex
    "$D8" --release \
        --min-api 21 \
        --output build/dex \
        --lib "$ANDROID_JAR" \
        build/classes/com/ghost1o1/ycc365/MainActivity.class 2>&1
    echo -e "    ${GOLD}[✓]${RESET} .class → classes.dex"

    echo -e "${CYAN}[*] Packaging ressources (aapt)...${RESET}"
    "$AAPT" package -f -M AndroidManifest.xml \
        -S res \
        -A assets \
        -I "$ANDROID_JAR" \
        -F build/ycc365-unsigned.apk 2>&1
    echo -e "    ${GOLD}[✓]${RESET} APK unsigned créé"

    echo -e "${CYAN}[*] Injection du DEX dans l'APK...${RESET}"
    cp build/ycc365-unsigned.apk build/ycc365-with-dex.apk
    cd build/dex && zip -j ../ycc365-with-dex.apk classes.dex >/dev/null 2>&1
    cd ../..
    echo -e "    ${GOLD}[✓]${RESET} Classes.dex injecté"

    echo -e "${CYAN}[*] Alignement (zipalign)...${RESET}"
    "$ZIPALIGN" -v -p 4 build/ycc365-with-dex.apk build/ycc365-aligned.apk >/dev/null 2>&1
    echo -e "    ${GOLD}[✓]${RESET} APK aligné"

    echo -e "${CYAN}[*] Signature (apksigner)...${RESET}"
    mkdir -p bin
    "$APKSIGNER" sign \
        --ks build/ghost1o1.keystore \
        --ks-pass pass:ghost101 \
        --key-pass pass:ghost101 \
        --ks-key-alias ghost1o1 \
        --out bin/ycc365-ghost-1.0.0.apk \
        build/ycc365-aligned.apk 2>&1 | grep -v "WARNING" || true

    echo -e "${CYAN}[*] Vérification signature...${RESET}"
    "$APKSIGNER" verify bin/ycc365-ghost-1.0.0.apk 2>&1 | grep -v "WARNING" || true

    echo ""
    echo -e "${GOLD}${BOLD}════════════════════════════════════════════${RESET}"
    echo -e "${GOLD}${BOLD}  ✅ BUILD RÉUSSI${RESET}"
    echo -e "${GOLD}${BOLD}  📦 bin/ycc365-ghost-1.0.0.apk${RESET}"
    echo -e "${GOLD}${BOLD}════════════════════════════════════════════${RESET}"
    echo ""

    ls -lh bin/ycc365-ghost-1.0.0.apk
}

main() {
    banner
    check_deps

    ANDROID_JAR=$(check_android_jar) || exit 1

    echo -e "${CYAN}[*] Build APK YCC365 Ghost v1.0.0...${RESET}"
    build_apk "$ANDROID_JAR"
}

main "$@"
