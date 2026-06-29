# 📜 Changelog — YCC365 Ghost Scanner

Toutes les modifications notables de ce projet sont documentées ici.
Format basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/).

---

## [1.2.0] — 2026-06-29 — Signé Ghost1o1 🏴‍☠️

### ✨ Ajouté

- **🆕 Phase 8 — Device Serial Intel** (adapté OSIN CHAIN Module #1 PhoneIntel)
  - 📁 `scanner/serialintel.py` (10.6 KB)
  - 📁 `scanner/wordlists/mac_oui_prefixes.txt` (38 vendors YCC365/Hipcam/XMEYE/Hikvision/Dahua)
  - 📁 `scanner/wordlists/serial_patterns.txt` (10 patterns séries caméra)
  - **OUI Vendor Lookup** : 50+ vendors YCC365 / Hipcam / Xiongmai / Dahua / Hikvision / Reolink / GeoVision / Vivotek / Axis
  - **Serial Pattern Match** : YCC365 standard `YK123456789ABC`, UUID ONVIF, Hipcam `HC[0-9]+`, etc.
  - **Cloud UID Check** : détection automatique UID cloud XMEYE/YCC365/Hipcam
  - **IP Geolocation** : ipinfo.io lookup (pays, ASN, organisation)
  - **BSSID WiGLE** : lookup WiFi BSSID (géoloc caméra WiFi)
- **🆕 Phase 9 — Firmware Metadata Extractor** (adapté OSIN CHAIN Module #2 ImageDeepScan)
  - 📁 `scanner/firmware_meta.py` (16.3 KB)
  - **HTTP Banner Grab** : extraction headers + fingerprinting
  - **RTSP Banner Grab** : identification serveur (Hipcam RTSP Server, etc.)
  - **Firmware .bin Analysis** : signature detection (uImage, CRAMFS, SquashFS, JFFS2, BusyBox, HiSilicon, XMEYE, YCC365)
  - **Strings Extraction** : URLs hardcodées dans firmware (.cn, .net, etc.)
  - **EXIF Snapshot** : extraction métadonnées image snapshot.jpg (GPS si activé = risque privacy)
  - **Cloud Headers Forensic** : analyse des réponses HTTPS des domaines XMEYE/YCC365

### 🔧 Scanner

- **9 phases totales** (vs 7 en v1.1.0)
- `scanner/__init__.py` bumped to v1.2.0
- Smoke test : imports OK, tous les modules chargent
- `core.py` étendu : Phase 8 + Phase 9 intégrées
- ScanResult dataclass : 2 nouveaux champs (`device_serial_intel`, `firmware_metadata`)

### 🛠️ Technique

- Architecture inspirée OSIN CHAIN (modules + registre + données structurées)
- Pas de dépendance externe critique (dataclasses + urllib)
- Compatibilité F-Droid maintenue (pure Java/Python, no Play Services)
- Risk scoring intégré pour chaque identification (0.0 → 1.0)

---

## [1.1.0] — 2026-06-29 — Signé Ghost1o1 🏴‍☠️

### ✨ Ajouté

- **🆕 Phase 6 — Username Arsenal (Sherlock-style)**
  - Adapté de OSIN CHAIN Module #4
  - 68 usernames × 19 passwords = 1292 combinaisons
- **🆕 Phase 7 — Cloud Domain Mapper**
  - Adapté de OSIN CHAIN Module #5
  - 45 domaines XMEYE/YCC365 cartographiés
- **📚 Wiki GitHub** : 11 pages techniques disponibles
- **🐧 F-Droid Submission Package** (`fdroid/`)

---

## [1.0.0] — 2026-06-29 — Signé Ghost1o1 🏴‍☠️

### ✨ Ajouté

- Scanner multi-phases : 5 phases (port scan, credentials, RTSP, Telnet BD, ONVIF)
- APK Android signé (16.9 KB)
- Script Termux standalone (13 KB)
- 16 ports YCC365/Hipcam, 23 credentials, 21 paths RTSP
- UI Ghost1o1 signée
- Release GitHub v1.0.0 + APK asset

---

## Liens

- 🔗 **GitHub** : https://github.com/187Ghost101/ycc365-ghost
- 📦 **Release v1.2.0** : https://github.com/187Ghost101/ycc365-ghost/releases/tag/v1.2.0
- 📚 **Wiki** : https://github.com/187Ghost101/ycc365-ghost/wiki

---

*YCC365 Ghost Scanner* — *Signé Ghost1o1* 🏴‍☠️
