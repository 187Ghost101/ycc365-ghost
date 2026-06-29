<div align="center">

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ▓██▓▒░       ░▒▓██▓                                       ║
║    ▓█▓▒░ ░▒▓██▓▒░ ░▒▓█    🏴‍☠️  Y C C 3 6 5   G H O S T    ║
║     █▒░ ░▓██▓▒░ ░▒▓█      ═══════════════════════════════    ║
║     ▓█▒░ ░▒░░░░░ ░▒▓█      S C A N N E R   v 1 . 0 . 0      ║
║      ▓█▒░░░░░░░░░░░▒▓█                                      ║
║       █▒░░░░░░░░░░░▒█       S i g n é   G h o s t 1 o 1     ║
║       ▓█▒░░░░░░░░░▒▓█       ═══════════════════════════════    ║
║        ▓██▒░░░░░▒██▓                                        ║
║         ░▒▓███▓▒░             I o T   P e n t e s t         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

**Audit & exploitation YCC365 Plus / IPCAM / Hipcam SDK**

[![Version](https://img.shields.io/badge/version-1.0.0-ffd60a?style=for-the-badge&logo=android)](https://github.com/ghost1o1/ycc365-ghost)
[![License](https://img.shields.io/badge/license-MIT--style-4da6ff?style=for-the-badge)](LICENSE)
[![Author](https://img.shields.io/badge/author-Ghost1o1-ff3860?style=for-the-badge)](https://github.com/ghost1o1)
[![Platform](https://img.shields.io/badge/platform-Android%205.0%2B-0a0f1e?style=for-the-badge&logo=android)](https://developer.android.com)
[![Tools](https://img.shields.io/badge/bash%20%7C%20python3-94a3b8?style=for-the-badge)](https://www.python.org)

</div>

---

## 📋 Table des Matières

- [🎯 Contexte](#-contexte)
- [⚠️ Avertissement Légal](#️-avertissement-légal)
- [🎯 Surface d'Attaque](#-surface-dattaque)
- [📦 Contenu du Repo](#-contenu-du-repo)
- [🚀 Installation](#-installation)
  - [APK Android](#apk-android)
  - [Termux (Recommandé)](#termux-recommandé)
  - [Build from Source](#build-from-source)
- [🔧 Utilisation](#-utilisation)
  - [Scanner une IP](#scanner-une-ip)
  - [Découverte Réseau](#découverte-réseau)
  - [Bruteforce Credentials](#bruteforce-credentials)
  - [Test RTSP](#test-rtsp)
  - [Backdoor Telnet](#backdoor-telnet-9527)
  - [ONVIF Probe](#onvif-probe)
- [🔍 Modules & Scripts](#-modules--scripts)
- [🎨 Charte Graphique](#-charte-graphique-ghost1o1)
- [📊 Architecture](#-architecture)
- [🛡️ CVE & Références](#️-cve--références)
- [🤝 Contribution](#-contribution)
- [📜 Licence](#-licence)
- [🏴‍☠️ Signature](#-signature)

---

## 🎯 Contexte

**YCC365 Plus** est une caméra IoT low-cost vendue massivement sur Temu, AliExpress, Wish. Distribution mondiale, firmware basé sur le SDK **Hipcam** (société chinoise HiSilicon). Le même firmware sert des dizaines de clones IPCAM.

### 🐛 Faiblesses Documentées

| Catégorie | Détail |
|-----------|--------|
| **Credentials par défaut** | 23 couples connus (admin/admin, root/xmhdipc…) |
| **Backdoor Telnet** | Port 9527 ouvert avec root/xmhdipc (Hipcam SDK) |
| **RTSP sans auth** | Port 554 expose souvent le flux sans authentification |
| **ONVIF non sécurisé** | Port 8899 répond aux probes sans auth |
| **QR Code WiFi** | Format `WIFI:T:WPA;S:ssid;P:pass;H:false;;` capturable |
| **Partage device** | QR code contient UID + token de vérification |

### 🎯 Objectif de ce Projet

Fournir un **scanner autonome et distribuable** permettant à un propriétaire de caméra YCC365 d'identifier rapidement les vulnérabilités de son propre équipement IoT, avec:

- ✅ APK Android natif signé (distribuable à un tiers de confiance)
- ✅ Script Bash + Python portable pour Termux
- ✅ UI Ghost1o1 stylisée (or / cyan / rouge sur fond sombre)
- ✅ Rapport JSON horodaté automatique
- ✅ AUCUNE dépendance externe critique (juste `ncat`, `curl`, `python3`)

---

## ⚠️ Avertissement Légal

```
╔════════════════════════════════════════════════════════════════╗
║  ⚠️  USAGE STRICTEMENT LIMITÉ À L'AUDIT DE TES PROPRES        ║
║      ÉQUIPEMENTS, OU AVEC AUTORISATION ÉCRITE EXPLICITE       ║
║                                                                ║
║  • CFAA (Computer Fraud and Abuse Act, USA)                    ║
║  • Computer Misuse Act 1990 (UK)                               ║
║  • Article 323-1 Code Pénal (France) — accès frauduleux       ║
║  • Article 323-2 Code Pénal (France) — atteinte systèmes     ║
║  • Loi canadienne anti-crime cybernétique PIPEDA              ║
╚════════════════════════════════════════════════════════════════╝
```

**Tu es seul responsable de l'usage de cet outil.**

Auteur : **Ghost1o1** — Pentest professionnel autorisé uniquement.

---

## 🎯 Surface d'Attaque

### 📡 Ports Scannés (16 ports YCC365 / Hipcam)

| Port | Service | Description |
|------|---------|-------------|
| `34567` | Custom YCC365 | Admin HTTP backend |
| `34599` | Custom YCC365 | Login web secondaire |
| `9527` | Telnet backdoor | **Hipcam SDK root/xmhdipc** |
| `554`  | RTSP | Streaming vidéo |
| `8000` | ONVIF + admin | Interface admin alternative |
| `8899` | ONVIF | Device discovery SOAP |
| `80`   | HTTP | Web UI standard |
| `443`  | HTTPS | Web UI sécurisé |
| `23`   | Telnet | Classique |
| `8080` | HTTP-Alt | Backend Java/Python |
| `8081` | HTTP-Alt | Backup |
| `8443` | HTTPS-Alt | TLS backend |
| `5552` | ADB (parfois) | Android Debug Bridge |
| `37777` | Dahua | Protocole propriétaire |
| `5000` | UPnP | Discovery |
| `34567-34599` | Range scan | Plage propriétaire YCC365 |

### 🔑 Credentials Testés (23 wordlist)

| Priorité | User | Password | Source |
|----------|------|----------|--------|
| 🔴 CRITIQUE | `root` | `xmhdipc` | Hipcam SDK backdoor |
| 🔴 CRITIQUE | `admin` | `admin` | Default factory |
| 🟠 HIGH | `admin` | `12345` | YCC365 default |
| 🟠 HIGH | `admin` | `888888` | Popular Chinese IoT |
| 🟠 HIGH | `admin` | `666666` | IPCAM generic |
| 🟡 MED | `admin` | `123` | Default factory short |
| 🟡 MED | `user` | `user` | OEM user account |
| 🟡 MED | `root` | `root` | Linux default |
| ⚪ LOW | `support` | `support` | Vendor maintenance |
| ⚪ LOW | `service` | `service` | Service account |
| + 13 autres | — | — | `operator`, `guest`, `abc123`… |

> **Wordlist complète** : voir `scanner/wordlists/credentials.txt`

### 📹 Paths RTSP (21 chemins énumérés)

```
/onvif/streaming/channels/101    ← Hikvision compatible
/streaming/channels/101
/11                              ← YCC365 spécifique
/12                              ← Channel 2
/live/ch00_0
/live/main
/live/sub
/live/0/main
/live/0/sub
/user=admin&password=&channel=1&stream=0.sdp
/av0_0
/video/main
/mpeg4
/cam/realmonitor                 ← Dahua
/0/usrnm:admin/0/usrpw:admin/0/1
/Streaming/Channels/101
/Streaming/Channels/1
/Streaming/Channels/2
/h264
/h264/ch01/main/av_stream
/trackID=1
```

---

## 📦 Contenu du Repo

```
ycc365-ghost/
├── 📄 README.md                          ← Ce fichier
├── 📄 LICENSE                            ← MIT-style
├── 📄 CHANGELOG.md                       ← Historique versions
├── 📄 SECURITY.md                        ← Politique divulgation
├── 🔧 build.sh                           ← Build APK en 1 commande
├── 📱 bin/ycc365-ghost-1.0.0.apk          ← APK signé (16.9 KB)
├── 📱 src/com/ghost1o1/ycc365/
│   └── MainActivity.java                 ← Source Java de l'APK
├── 📦 AndroidManifest.xml                ← Manifest Android
├── 🎨 res/
│   ├── values/colors.xml                 ← Palette Ghost1o1
│   ├── values/strings.xml
│   └── values/styles.xml
├── 🛠️ scanner/                           ← Modules Python réutilisables
│   ├── core.py                           ← Moteur de scan
│   ├── theme.py                          ← Charte graphique
│   └── wordlists/                        ← Dictionnaires
│       ├── credentials.txt
│       └── rtsp_paths.txt
├── 🔥 assets/
│   └── ycc365-ghost.sh                   ← Scanner CLI complet
├── 📚 docs/
│   ├── ATTACK_SURFACE.md                 ← Détail vector d'attaque
│   ├── ARCHITECTURE.md                   ← Diagramme technique
│   ├── METHODOLOGY.md                    ← Méthodologie pentest
│   └── SCREENSHOTS.md                    ← Visuels UI
└── 🧪 examples/
    └── sample_report.txt                 ← Exemple de rapport
```

---

## 🚀 Installation

### 📱 APK Android

1. **Télécharge** `bin/ycc365-ghost-1.0.0.apk` depuis ce repo
2. **Autorise** les sources inconnues :
   ```
   Paramètres → Sécurité → Sources inconnues → Activer
   ```
3. **Clique** sur le fichier APK → **Installer**
4. **Lance** "YCC365 Ghost" depuis ton launcher

L'APK affiche le banner Ghost1o1, liste les modules embarqués, et donne les instructions pour Termux.

### 📱 Termux (Recommandé)

```bash
# 1. Installer Termux depuis F-Droid (PAS Google Play — version obsolète)
https://f-droid.org/en/packages/com.termux/

# 2. Dans Termux :
pkg update && pkg upgrade
pkg install ncat curl python

# 3. Copier le scanner
cp /sdcard/ycc365-ghost.sh ~/ycc365-ghost.sh
chmod +x ~/ycc365-ghost.sh

# 4. Lancer
bash ~/ycc365-ghost.sh
```

### 🔨 Build from Source

```bash
# Cloner le repo
git clone https://github.com/ghost1o1/ycc365-ghost.git
cd ycc365-ghost

# Build APK (Debian/Ubuntu)
./build.sh

# Résultat:
ls -la bin/ycc365-ghost-1.0.0.apk
```

Pré-requis build :
- `apt install aapt apksigner zipalign default-jdk-headless`
- `android.jar` (API 33+) — voir `docs/ARCHITECTURE.md`
- `keytool` (inclus dans OpenJDK)

---

## 🔧 Utilisation

### Scanner une IP

```bash
bash ycc365-ghost.sh
# Choisir option [1]
# IP: 192.168.1.100
```

Affiche :
- ✅ Ports ouverts détectés
- ✅ Credentials valides (bruteforce HTTP Basic Auth)
- ✅ RTSP accessible (sans auth)
- ⚠️ Backdoor Telnet 9527 (si vulnérable)
- ⚠️ ONVIF device info disclosure

### Découverte Réseau

```bash
bash ycc365-ghost.sh
# Choisir option [2]
# Détecte ton réseau /24 et liste les hôtes actifs
```

### Bruteforce Credentials

Le module teste 23 couples sur tous les ports HTTP découverts :

```
[*] Test sur port 80...
  [VALID] admin:12345 (HTTP 200)
  [VALID] admin:888888 (HTTP 200)
[SUCCESS] 2 credentials valides trouvées
```

### Test RTSP

```
[*] Test RTSP sur port 554
  [✓] RTSP ACTIF
  Banner: Server: Hipcam RTSP Server 1.0
    [ACCESSIBLE] /onvif/streaming/channels/101
    [ACCESSIBLE] /live/ch00_0
    [ACCESSIBLE] /11
[ALERTE] Flux vidéo accessible sans auth — visionnage direct possible
```

### Backdoor Telnet 9527

```
[*] Test backdoor Telnet port 9527
[*] Tentative root/xmhdipc...
[CRITICAL] BACKDOOR TELNET ACTIF!
  Sortie: root@camera:/#
[ALERTE] Prise de contrôle root complète possible
```

### ONVIF Probe

```
[*] ONVIF probe sur port 8899
[ONVIF] Device répond sans auth
  Manufacturer: HiSilicon
  Model: YCC365 Plus
  FirmwareVersion: V5.0.4
  SerialNumber: HISCAM-XXX-XXX
```

---

## 🔍 Modules & Scripts

### 📄 `scanner/core.py` — Moteur de scan

- Scan multi-thread TCP
- Bruteforce HTTP Basic Auth avec gestion rate-limit
- Probe RTSP avec fallback de chemins
- Détection backdoor Telnet avec payload root/xmhdipc
- ONVIF WS-Discovery + GetDeviceInformation
- Export JSON structuré

### 📄 `scanner/theme.py` — Charte graphique

```python
GOLD  = "\033[38;5;220m"   # #ffd60a — Titres & succès
CYAN  = "\033[38;5;39m"    # #4da6ff — Sous-titres & liens
RED   = "\033[38;5;196m"   # #ff3860 — Alertes critiques
GRAY  = "\033[38;5;245m"   # #94a3b8 — Texte secondaire
DARK  = "#0a0f1e"          # Fond sombre
```

### 📄 `assets/ycc365-ghost.sh` — Scanner CLI

Script bash standalone de 13 KB incluant :
- 5 phases de scan
- 16 ports, 23 credentials, 21 paths RTSP
- Export rapport texte horodaté
- Gestion d'erreurs (`set -e`, fallbacks)
- Banner ASCII Ghost1o1 custom

### 📄 `src/MainActivity.java` — Activity Android

`Activity` Java native (~200 lignes) :
- `ScrollView` + `LinearLayout` pur (pas de XML inflation)
- Palette Ghost1o1 appliquée via `Color.parseColor()`
- Banner + signature + 5 sections d'info
- Pas de dépendances externes (pas de Material design)

---

## 🎨 Charte Graphique Ghost1o1

| Usage | Couleur | Hex |
|-------|---------|-----|
| Fond principal | Dark Blue/Black | `#0a0f1e` |
| Titres & succès | Gold Jaune | `#ffd60a` |
| Sous-titres & accents | Cyan Bleu | `#4da6ff` |
| Alertes critiques | Rouge Vif | `#ff3860` |
| Texte secondaire | Gris Clair | `#94a3b8` |
| Texte principal | Blanc Cassé | `#e8edf5` |

### 🏴‍☠️ Éléments de marque

- Banner skull + drapeau pirate ASCII
- Mention **"Signé Ghost1o1"** systémique
- Format monospace (terminal/CLI)
- Tableaux colorés pour les rapports
- Icônes emoji (🏴‍☠️ ⚠️ ✅ ❌) pour la lisibilité

---

## 📊 Architecture

```
┌─────────────────────────────────────────────┐
│              UTILISATEUR                    │
│         (propriétaire caméra)               │
└──────────┬──────────────────┬───────────────┘
           │                  │
           ▼                  ▼
   ┌──────────────┐   ┌──────────────────┐
   │  APK Android │   │  Termux + Bash   │
   │   Launcher   │   │   + Python       │
   └──────┬───────┘   └──────┬───────────┘
          │                  │
          │   ┌──────────────┴──────────────┐
          └──►│     SCANNER (core)          │
              │                             │
              │  ┌─────────────────────┐    │
              │  │ Phase 1: Port Scan  │    │
              │  │ Phase 2: Bruteforce │    │
              │  │ Phase 3: RTSP Test  │    │
              │  │ Phase 4: Telnet BD  │    │
              │  │ Phase 5: ONVIF      │    │
              │  └─────────┬───────────┘    │
              │            │                │
              │            ▼                │
              │  ┌─────────────────────┐    │
              │  │ Report Generator    │    │
              │  │ (JSON + text)       │    │
              │  └─────────────────────┘    │
              └─────────────────────────────┘
                          │
                          ▼
                ┌──────────────────┐
                │  CAMÉRA CIBLE    │
                │  YCC365 Plus     │
                │  192.168.1.X     │
                └──────────────────┘
```

### 🔧 Stack Technique

| Composant | Technologie |
|-----------|-------------|
| APK | Java 8 + Android SDK 33 |
| Build tools | aapt, d8, zipalign, apksigner |
| Signature | RSA 2048 SHA384withRSA |
| CLI | Bash 4+ + Python 3.10+ |
| Réseau | `ncat`, `curl`, `bash /dev/tcp` |
| Theme | ANSI 256 colors + AOSP color |

---

## 🛡️ CVE & Références

### 📚 CVEs liés au SDK Hipcam

| CVE | Année | Description |
|-----|-------|-------------|
| `CVE-2017-16919` | 2017 | Hipcam backdoor root/xmhdipc port 9527 |
| `CVE-2020-9525` | 2020 | HiSilicon IPCAM RTSP auth bypass |
| `CVE-2021-36260` | 2021 | Hikvision command injection |
| `CVE-2022-2208` | 2022 | HiSilicon firmware credential leak |
| `CVE-2023-30313` | 2023 | YCC365 Plus UID/tokens exposure |

### 📖 Lectures recommandées

- [Hipcam SDK reverse engineering — DEFCON 2018](https://defcon.org)
- [IoT Inspector — YCC365](https://www.iot-inspector.com)
- [OWASP IoT Top 10 2018](https://owasp.org/www-pdf-archive/OWASP-IoT-Top-10-2018.pdf)
- [CISA — Default passwords list](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)

---

## 🤝 Contribution

Les PRs sont les bienvenues ! Domaines d'amélioration :

- [ ] Support multi-cibles (Hikvision, Dahua, Reolink)
- [ ] Export PDF automatisé du rapport
- [ ] Intégration Shodan/Censys pour scan distant
- [ ] UI Material Design pour Android (au lieu de ScrollView brute)
- [ ] Module détection firmware (lecture version exacte)

**Code style** :
- Python : PEP 8 + nommage snake_case
- Bash : shellcheck clean, fonctions courtes
- Java : Google Java Style
- Markdown : tables + emojis 🏴‍☠️

---

## 📜 Licence

```
MIT License

Copyright (c) 2026 Ghost1o1

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
```

⚠️ **Rappel : l'usage reste sous ta responsabilité légale.**

---

## 🏴‍☠️ Signature

```
╔══════════════════════════════════════════╗
║                                          ║
║       🏴‍☠️  Signé Ghost1o1  🏴‍☠️           ║
║                                          ║
║       Pentest IoT • Audit • Sécurité     ║
║       Québec, Canada — Juin 2026         ║
║                                          ║
║       "Le pentest, c'est pas juste       ║
║        trouver des failles. C'est        ║
║        comprendre l'autre côté          ║
║        du miroir."                       ║
║                                          ║
╚══════════════════════════════════════════╝
```

<div align="center">

**[⬆ Retour en haut](#-table-des-matières)**

Made with 🏴‍☠️ by **Ghost1o1**

</div>
