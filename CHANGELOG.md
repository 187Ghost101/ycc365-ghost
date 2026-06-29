# 📜 Changelog — YCC365 Ghost Scanner

Toutes les modifications notables de ce projet sont documentées ici.
Format basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).

---

## [1.0.0] — 2026-06-29 — Signé Ghost1o1 🏴‍☠️

### ✨ Ajouté
- **Scanner multi-phases** : 5 phases (ports, credentials, RTSP, Telnet BD, ONVIF)
- **APK Android** signé (RSA 2048 SHA384) — package `com.ghost1o1.ycc365`
- **Script Termux** standalone (13 KB) — `assets/ycc365-ghost.sh`
- **UI Ghost1o1** : palette `#ffd60a` / `#4da6ff` / `#ff3860` / `#0a0f1e`
- **16 ports YCC365/Hipcam** scannés (34567, 9527, 554, 8899, …)
- **23 wordlist credentials** incluant backdoor `root/xmhdipc`
- **21 paths RTSP** énumérés (Hikvision, Dahua, YCC365-compatibles)
- **Détection ONVIF** avec `GetDeviceInformation` SOAP probe
- **Détection backdoor Telnet** 9527 + brute root/xmhdipc (Hipcam SDK)
- **Rapport horodaté** `.txt` exporté sous `/tmp/`
- **Banner ASCII Ghost1o1** custom avec skull + drapeau pirate
- **README.md** complet : 11 sections, table des matières, charte graphique
- **MIT License** + Disclaimer légal détaillé
- **Build script** (`build.sh`) one-shot

### 🔧 Technique
- Java 8 source, Android API 33 compile
- aapt v29.0.3 + d8 v30.0.3 + apksigner v30.0.3
- zipalign v10.0.0+r36
- min SDK 21 (Android 5.0 Lollipop) → target SDK 33 (Android 13)
- arm64-v8a + armeabi-v7a support via Java pur (pas de NDK)
- Bash 4+ + Python 3.10+ requis pour scanner CLI

### 🔒 Sécurité & Légale
- Avertissement explicite dans l'APK
- Avertissement dans le script CLI
- Disclaimer dans README + LICENSE
- Aucun payload offensif autonome (toutes actions requièrent confirmation)

### 📦 Artefacts
- `bin/ycc365-ghost-1.0.0.apk` — 16.9 KB
- `assets/ycc365-ghost.sh` — 13 KB (600+ lignes bash)
- `src/com/ghost1o1/ycc365/MainActivity.java` — 200 lignes
- `scanner/core.py` — moteur Python
- `scanner/theme.py` — palette ANSI 256

---

## [Unreleased] — Roadmap

### 🎯 v1.1.0 — Q3 2026
- [ ] Support Hikvision (CVE-2021-36260 command injection)
- [ ] Support Dahua (CVE-2021-33044 auth bypass)
- [ ] Export PDF du rapport (weasyprint ou reportlab)
- [ ] Intégration Shodan API pour scan distant
- [ ] UI Android Material You (Compose)

### 🎯 v1.2.0 — Q4 2026
- [ ] Plugin Frida pour analyse dynamique
- [ ] Détection automatique firmware version
- [ ] Module GPS/location disclosure check
- [ ] Multi-targets depuis CSV

### 🎯 v2.0.0 — 2027
- [ ] Refactor full Python (Kivy mobile)
- [ ] GUI web Flask + FastAPI backend
- [ ] Docker image self-hosted
- [ ] CI/CD GitHub Actions (build APK auto)

---

*YCC365 Ghost Scanner* — *Signé Ghost1o1* 🏴‍☠️
