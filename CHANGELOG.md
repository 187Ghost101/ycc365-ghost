# 📜 Changelog — YCC365 Ghost Scanner

Toutes les modifications notables de ce projet sont documentées ici.
Format basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).

---

## [1.1.0] — 2026-06-29 — Signé Ghost1o1 🏴‍☠️

### ✨ Ajouté

- **🆕 Phase 6 — Username Arsenal (Sherlock-style)**
  - Adapté de OSIN CHAIN Module #4
  - 58 usernames × 19 passwords = 1102+ combinaisons
  - Wordlist `usernames.txt` : admin, root, xmeye, hipcam, ycc365, hikvision, dahua, etc.
  - Méthode `scanner/usernames.py`
- **🆕 Phase 7 — Cloud Domain Mapper**
  - Adapté de OSIN CHAIN Module #5
  - 42 domaines XMEYE/YCC365/LookCam cartographiés
  - DNS resolution + HTTP/HTTPS probe + SSL/TLS cert inspection
  - Cloud provider detection (Aliyun / Tencent / AWS / Akamai)
  - Méthode `scanner/cloudmapper.py`
- **📚 Wiki GitHub** : 11 pages techniques disponibles (script `scripts/init_wiki.sh`)
  - Home, Architecture, Attack-Surface, Methodology, Modules-Reference, CVE-Mapping, Threat-Model, Testing-Guide, IoT-Camera-Threats, Defense-Recommendations, Sample-Reports
- **🐧 F-Droid Submission Package** (`fdroid/`)
  - `metadata/com.ghost1o1.ycc365.yml` — Metadata standard
  - `build.gradle` — Config Gradle pour build reproductible
  - `SUBMIT.md` — Guide de soumission complet
- **🔧 Scripts** : `scripts/init_wiki.sh` pour bootstrap du wiki

### 🔧 Technique

- Module `scanner/core.py` étendu à **7 phases**
- `scanner/__init__.py` v1.1.0
- Tests : 1102+ credentials × N ports + 42 domaines cloud
- Pas de régression sur v1.0.0 (Phases 1-5)

### 📚 Documentation

- 11 pages wiki techniques (~5000 lignes Markdown total)
- Charte graphique Ghost1o1 maintenue
- Diagrams ASCII + tables complètes

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
- min SDK 21 (Android 5.0) → target SDK 33 (Android 13)
- Bash 4+ + Python 3.10+ requis pour scanner CLI

### 🔒 Sécurité & Légale

- Avertissement explicite dans l'APK
- Avertissement dans le script CLI
- Disclaimer dans README + LICENSE

### 📦 Artefacts

- `bin/ycc365-ghost-1.0.0.apk` — 16.9 KB
- `assets/ycc365-ghost.sh` — 13 KB
- `src/com/ghost1o1/ycc365/MainActivity.java` — 200 lignes
- `scanner/core.py` — moteur Python
- `scanner/theme.py` — palette ANSI

---

## [Unreleased] — Roadmap

### 🎯 v1.2.0 — Q3 2026

- [ ] Support Hikvision (CVE-2021-36260)
- [ ] Support Dahua (CVE-2021-33044) full exploit
- [ ] Export PDF rapport (weasyprint)
- [ ] Module GPS/location leakage detection
- [ ] Multi-targets depuis CSV
- [ ] GUI web Flask + FastAPI backend

### 🎯 v2.0.0 — 2027

- [ ] Refactor full Python (Kivy mobile)
- [ ] Docker image self-hosted
- [ ] Frida integration pour analyse dynamique
- [ ] CI/CD GitHub Actions (build APK auto)

---

## Liens Utiles

- 🔗 **GitHub** : https://github.com/187Ghost101/ycc365-ghost
- 📦 **Release v1.1.0** : https://github.com/187Ghost101/ycc365-ghost/releases/tag/v1.1.0
- 📦 **Release v1.0.0** : https://github.com/187Ghost101/ycc365-ghost/releases/tag/v1.0.0
- 📚 **Wiki** : https://github.com/187Ghost101/ycc365-ghost/wiki
- 🐧 **F-Droid** : (à venir — voir `fdroid/SUBMIT.md`)

---

*YCC365 Ghost Scanner* — *Signé Ghost1o1* 🏴‍☠️
