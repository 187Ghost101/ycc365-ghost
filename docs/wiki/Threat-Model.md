# ⚠️ Threat Model — YCC365 Caméra IoT

> Modélisation STRIDE complète des menaces sur une caméra YCC365 / Hipcam
> **Signé Ghost1o1** — *Threat modeling = penser comme l'attaquant*

---

## 🎯 Adversaires Considérés

| Adversaire | Capacité | Motivation | Accès |
|------------|----------|------------|-------|
| **Curieux LAN** | Faible (script kiddie) | Espionnage familial | WiFi/LAN |
| **Script Kiddie** | Moyenne (Metasploit) | Fun/profil | Internet |
| **Worm IoT** | Élevée (Mirai variant) | Botnet recruitment | Internet |
| **APT Nation-State** | Très élevée | Surveillance | Multi-vector |
| **Concurrent/espion** | Variable | Industrie/espionage | PHY ou LAN |
| **Famille abusive** | Faible-moyenne | Harcèlement | PHY |

---

## 🎭 STRIDE par Couche

### S — Spoofing (Usurpation identité)

| Menace | Vecteur | Impact |
|--------|---------|--------|
| Caméra usurpe serveur cloud | DNS hijack + cert absent | Score **CVSS 7.4** |
| Client usurpe camera RTSP | Same LAN + path guess | CVSS **6.5** |
| Telnet backdoor = identité faible | Hardcoded creds | CVSS **9.1** |
| Cloud usurpe MAJ firmware | Server compromise | CVSS **8.8** |

**Mitigations** :
- ✅ Épinglage certificat HTTPS dans app YCC365
- ✅ Auth RTSP obligatoire (digest)
- ⚠️ Pas de fix pour hardcoded backdoor
- ✅ Signature firmware (rare)

### T — Tampering (Modification données)

| Menace | Vecteur | Impact |
|--------|---------|--------|
| Modification firmware OTA | Server compromise | CVSS **8.8** |
| Modification config caméra | ADB port 5552 | CVSS **9.8** |
| Modification live stream | MITM RTSP | CVSS **5.3** |
| Modification cloud data | API compromise | CVSS **8.5** |

**Mitigations** :
- ✅ Vérification signature firmware
- ✅ Désactiver ADB (souvent activé)
- ⚠️ Stream RTSP non chiffré
- ✅ Auth forte compte cloud

### R — Repudiation (Déni action)

| Menace | Vecteur | Impact |
|--------|---------|--------|
| Pas de logs Telnet | Backdoor actif | Auditabilité **nulle** |
| Logs cloud hors contrôle utilisateur | Server-side only | Opacité |
| Logs RTSP inexistants | Pas de tracking | Aucune traçabilité |
| Modification timestamps | Accès root | Détection compromise |

**Mitigations** :
- ⚠️ Utiliser syslog externe (si supporté)
- ✅ Activer logs cloud côté app YCC365
- ⚠️ Stream RTSP non loggué nativement
- ✅ Intégrité logs via append-only

### I — Information Disclosure (Fuite données)

| Menace | Vecteur | Données exposées | Impact |
|--------|---------|------------------|--------|
| ONVIF probe sans auth | Port 8899 | Modèle, firmware, serial | CVSS **5.3** |
| WS-Discovery broadcast | UDP 3702 | IP, UUID, capabilities | CVSS **3.7** |
| RTSP sans auth | Port 554 | Live video | CVSS **7.5** |
| Cloud API IDOR | HTTP API | Device list, GPS | CVSS **6.5** |
| Firmware OTA accessible | HTTP /firmware.bin | Code source firmware | CVSS **5.3** |
| Backdoor Telnet `/etc/passwd` | Port 9527 | Liste users | CVSS **9.8** |
| Snapshot endpoint sans auth | HTTP /snapshot.jpg | Image fixe | CVSS **5.3** |

**Mitigations** :
- ✅ Auth obligatoire ONVIF
- ✅ Bloquer UDP 3702 sur switch
- ✅ RTSP auth + digest
- ✅ Rate limiting API cloud
- ⚠️ OTA téléchargeable (rare fix)
- ⚠️ Backdoor Telnet = inherent issue
- ✅ Désactiver snapshot

### D — Denial of Service

| Menace | Vecteur | Impact |
|--------|---------|--------|
| Flood TCP port 554 | RTSP flood | Service halt |
| Replay authentification | Cloud auth replay | Resource exhaustion |
| Scan agressif | nmap -T5 | Camera freeze |
| Cloud outage | XMEYE down | Remote access lost |
| Power glitch | PHY access | Reboot persistant |

**Mitigations** :
- ✅ Rate limit port par switch
- ✅ Captcha sur cloud login (rare)
- ✅ Pentest éduqué (faible T3-T4)
- ⚠️ Cloud dépendance (pas de fallback)
- ✅ UPS pour caméra critique

### E — Elevation of Privilege

| Menace | Vecteur | Impact |
|--------|---------|--------|
| ADB port 5552 | connect + shell | **Root** sur caméra |
| Telnet backdoor | login root/xmhdipc | **Root** |
| U-boot non sécurisé | Console UART PHY | **Boot manipulate** |
| Cloud API privilege escalation | Vulnérabilité serveur | Admin distant |
| RTSP bypass auth | Path encoding | **Stream sans auth** |
| Firmware downgrade | OTA non-signé | Versions vulnérables |

**Mitigations** :
- ✅ Désactiver ADB
- ⚠️ Pas de fix Telnet backdoor
- ✅ Protection PHY sur caméra
- ✅ MFA compte cloud
- ⚠️ Stream RTSP nécessite firmware patch
- ⚠️ OTA signature vary per OEM

---

## 🔐 Authentication Map

```
┌──────────────────────────────────────────────────────────┐
│              AUTHENTICATION FLOW                         │
└──────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   ┌────▼────┐       ┌────▼────┐       ┌────▼────┐
   │ HTTP    │       │ RTSP    │       │ Telnet  │
   │ 80/443/ │       │ 554     │       │ 9527    │
   │ 8000/   │       │         │       │         │
   │ 34567   │       │         │       │         │
   └────┬────┘       └────┬────┘       └────┬────┘
        │                 │                 │
   Basic Auth         Basic/Digest      Hardcoded
   admin:12345        (bypassable)      root:xmhdipc
        │                 │                 │
        ▼                 ▼                 ▼
   ⚠️ DEFAULT         🔓 OFTEN          💀 BACKDOOR
```

---

## 🌐 Trust Boundaries

```
┌────────────────────────┐
│     INTERNET           │
│  - Cloud XMEYE         │
│  - DNS resolvers       │
│  - Attacker            │
└───────────┬────────────┘
            │ HTTPS/HTTP/DNS
            │ (Untrusted)
            │
   ─────────TB1 (Internet/LAN boundary)──────────
            │
            │ Most cameras: port forwarded
            │ Optional: VPN, no NAT
            │
┌───────────▼────────────┐
│   LOCAL NETWORK        │
│  ┌──────────────────┐  │
│  │  CAMERA          │  │◄──── TB2 (admin UI / LAN boundary)
│  │  (YCC365)        │  │
│  │                  │  │
│  │  - Web admin     │  │──── Attacker LAN
│  │  - RTSP          │  │     (script kiddie, family)
│  │  - Telnet BD     │  │
│  │  - ONVIF         │  │
│  │  - WS-Discovery  │  │
│  └──────────────────┘  │
└────────────────────────┘
```

---

## 📊 Asset Model

### Assets Sensibles (Data at Rest)

```
DATA TYPE                  LOCATION              CIA
─────────────────────────────────────────────────────
Live video stream          Camera SD / Cloud     C-I-A
Recorded videos            SD card / Cloud       C-I-A
Device credentials         NVRAM / Flash         C-I-A
User accounts (admin)      Flash / Cloud         I-A
WiFi PSK                   NVRAM                 C-I
Firmware source            Flash / OTA server    I-A
Serial/MAC identifiers     Flash                 -
GPS coordinates (mobile)   Cloud                 C
Timezone settings          Flash                 I
```

### Assets en Transit

```
DATA TYPE                  PROTOCOL            ENCRYPTION
─────────────────────────────────────────────────────────
RTSP stream                TCP 554             ⚠️ Often plain
HTTP admin UI              TCP 80/34567        ⚠️ Often plain
HTTPS admin UI             TCP 443/8443        ✅ TLS
Cloud API                  HTTPS 443           ✅ TLS (no pin)
Telnet BD                  TCP 9527            ❌ Plain + hardcoded creds
WS-Discovery               UDP 3702            ❌ Plain
Cloud P2P relay            TCP 10000+          ⚠️ DTLS-like (reversible)
OTA firmware               HTTP/HTTPS          ⚠️ Varies
NTP time sync              UDP 123             ❌ Plain
```

---

## 🎯 Scénarios d'Attaque (Attack Trees)

### Scénario 1: Désactiver sécurité caméra

```
GOAL: Disable camera security
│
├─ OR1: Brute force web admin
│   ├─ Phase 2 Bruteforce (admin:12345) ✅
│   ├─ Phase 6 Username Arsenal (exhaustif) ✅
│   └─ Result: Admin access web
│
├─ OR2: Backdoor Telnet
│   └─ Phase 4 Telnet BD (root:xmhdipc) ✅ → Direct root
│
├─ OR3: ADB
│   └─ Phase 1 if port 5552 open + `adb connect` ✅
│
└─ OR4: Cloud-side attack
    ├─ Phishing app user
    ├─ Account takeover via credential stuffing
    └─ Cloud admin add camera to attacker account
```

### Scénario 2: Voler vidéo streaming

```
GOAL: Stream camera video
│
├─ OR1: RTSP anonymous
│   └─ Phase 3 RTSP scan × 21 paths ✅
│
├─ OR2: RTSP auth guessed
│   └─ Phase 2 Bruteforce + Phase 3 → use creds ✅
│
├─ OR3: Cloud relay hijack
│   ├─ Compromise cloud account
│   └─ Modify camera config → forward to attacker cloud
│
├─ OR4: MITM if WiFi owned
│   └─ ARP poison + intercept RTSP
│
└─ OR5: Snapshot endpoint
    └─ Direct curl /snapshot.jpg paths
```

### Scénario 3: Pivot LAN interne

```
GOAL: Move into internal network
│
├─ OR1: Caméra root → scan LAN
│   └─ After backdoor: bash scan.sh on subnet ✅
│
├─ OR2: Use camera as proxy
│   └─ iptables rules or socat
│
├─ OR3: ARP poison from camera
│   └─ Bettercap/mitmproxy installed via ADB
│
└─ OR4: Lateral via cloud
    └─ All camera users = same network? Maybe not
```

### Scénario 4: Persistance longue durée

```
GOAL: Persistent access (years)
│
├─ OR1: Modify firmware
│   └─ Embed backdoor at NAND flash level
│
├─ OR2: Cloud-bound
│   └─ Add backdoor camera account in cloud DB
│
├─ OR3: PHY implant
│   └─ Add small WiFi device on LAN
│
└─ OR4: Modify NTP/DNS
    └─ Redirect firmware OTA updates
```

---

## 💼 Impact Business

| Impact | Coût Estimé | Catégorie |
|--------|-------------|-----------|
| Surveillance familiale abusive | **$5000-$50000** lawsuit | Privacité |
| Vol de propriété intellectuelle | **Variable** | Industrie |
| Botnet recruitment | **Publicity damage** | Réputation |
| Spy camera (sextortion) | **Catastrophic** | Image |
| Non-compliance GDPR | **4% revenue ou 20M€** | Régulier |
| Ransomware via caméra | **$100K-$1M** | Crime |

---

## 🎯 Hiérarchie Menaces (Top 10)

| # | Menace | Probabilité | Impact | Priorité |
|---|--------|-------------|--------|----------|
| 1 | Backdoor Telnet 9527 | Très haute | Critique | 🔴 P0 |
| 2 | Default creds admin:12345 | Très haute | Critique | 🔴 P0 |
| 3 | RTSP sans auth | Haute | Élevé | 🔴 P1 |
| 4 | ONVIF info disclosure | Haute | Modéré | 🟠 P2 |
| 5 | ADB port 5552 ouvert | Moyenne | Critique | 🔴 P0 |
| 6 | Cloud IDOR énumération | Moyenne | Élevé | 🟠 P2 |
| 7 | WS-Discovery passive | Très haute | Faible | 🟡 P3 |
| 8 | Firmware OTA hijack | Faible | Très élevé | 🟠 P2 |
| 9 | Snapshot endpoint | Haute | Modéré | 🟡 P3 |
| 10 | U-boot PHY non lock | Très faible | Critique | 🟡 P3 |

---

## ✅ Contrôles Recommandés (Defense in Depth)

### Layer 1: Réseau
- VLAN isolé IoT
- Firewall deny-all entrant caméras
- Bloquer accès sortant cloud (sauf NTP)
- Switch avec port security
- Bloquer UDP 3702 multicast

### Layer 2: Caméra
- Changer TOUS les passwords
- Mettre à jour firmware
- Désactiver ADB et Telnet (si firmware le permet)
- Désactiver RTSP si non utilisé

### Layer 3: Cloud
- Compter cloud app YCC365 fort (12+ chars)
- 2FA sur compte cloud
- Logs activité surveillance
- Déconnecter cloud si non utilisé (LAN only)

### Layer 4: Monitoring
- IDS sur LAN (Suricata signatures YCC365)
- Honeypot caméra (cOwRANG 🏴)
- Logs syslog externe
- Surveillance DNS caméra

---

**Signé Ghost1o1** 🏴‍☠️ — *Le threat model est la boussole du défenseur*
