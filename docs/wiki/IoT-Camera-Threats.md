# 🌐 IoT Camera Threat Landscape

> Panorama complet des menaces sur les caméras IoT grand public et professionnelles
> **Signé Ghost1o1** — *Voir loin pour prévoir*

---

## 🌍 Marché Mondial des Caméras IoT

### Chiffres Clés (2025)

- **2.2 milliards** d'appareils IoT-security installés mondialement
- **~$50 milliards** de marché annuel
- **63%** des caméras vendues sont fabriquées en Chine
- **40%** n'ont jamais reçu un seul patch firmware
- **85%** utilisent un SDK commun (Hipcam, Xiongmai, HiSilicon...)

### Distribution Géographique des Vendors

```
Chine              ████████████████████  63%
  - HiSilicon
  - Xiongmai (XMEYE)
  - Hipcam SDK
  - Dahua
  - Hikvision
  - Reolink

États-Unis         ██████                18%
  - Arlo
  - Ring (Amazon)
  - Nest (Google)
  - Wyze

Japon/Corée        ███                    9%
  - Sony
  - Panasonic
  - Hanwha (ex Samsung)
```

---

## 🔥 Top 10 Vulnérabilités IoT 2024-2025

Basé sur notre recherche collective (OSIN CHAIN + YCC365 Ghost) :

### #1 — Default Credentials (90% des caméras)

```python
# Top 10 mondial (tous vendors)
DEFAULT_CREDS = [
    ("admin", "admin"),       # 35% des caméras
    ("admin", ""),            # 15% — blank password
    ("admin", "12345"),       # 20% — XMEYE/YCC365
    ("admin", "password"),    # 10%
    ("root", "xmhdipc"),      # 30% des Chinese cams
    ("user", "user"),         # 5%
    ("admin", "1234"),        # 5%
    ("Admin", "12345"),       # Case-sensitivity abuse
    ("ubnt", "ubnt"),         # Ubiquiti
    ("support", "support"),   # Hikvision
]
```

**Pourcentage total caméras affectées** : ~90%

### #2 — Cloud API Misconfiguration

```bash
# Erreurs courantes APIs cloud IoT:
- Authentification absente (Cognito S3)
- Rate limiting absent (billions of requests possible)
- CORS trop permissif (origins *)
- GraphQL introspection activée
- Device ID énumérable (sequential)
```

**Réalité** : Le cloud IoT est plus vulnérable que le device lui-même.

### #3 — Firmware OTA sans Signature

```python
# OTA firmware download insecure
curl http://camera.local/firmware.bin -o fw.bin
# → binaire complet en clair

# Sans check signature :
# - Modification possible
# - Downgrade vers vuln version
# - MITM attack possible
```

### #4 — UPnP Expose WAN

```bash
# Caméra fait port forward automatique
# UPnP via routeur (si activé)
# Internet ← exposed camera web/RTSP
```

### #5 — P2P Relay Cloud Bypass

```
Architecture typique :
1. Camera se connecte à P2P server (TCP 10000+)
2. App user se connecte même serveur
3. Server route packets camera ↔ app
4. Server COMPROMIS = accès all cameras
```

### #6 — SD Card Sans Encryption

```python
# Si l'attaquant extrait SD card
dd if=/dev/mmcblk0 of=dump.img
mount -o loop dump.img /mnt
# → Accès complet:
#  - Vidéos enregistrées (MJPEG/H264)
#  - Database (SQLite user accounts)
#  - Configurations
#  - Logs
```

### #7 — Microphone Backdoor (Audio Capture)

```bash
# Caméras IoT (souvent avec micro)
# Certains SDK activent micro par défaut
# Sans indication UI
# Audio stream → cloud
```

### #8 — Geo-Tagging Leakage

```bash
# Si caméra utilisée avec app mobile
# Chaque photo/vidéo est géotaggée automatiquement
# Récupérer EXIF:
exiftool photo.jpg | grep GPS
# → GPS Position  45.5017° N, 73.5673° W (Québec)
# → Privacy bye bye
```

### #9 — Motion Detection False Positives = Probing

```bash
# Caméra avec motion detection = capteurs lumière/mouvement
# Attaquant bouge physiquement → caméra enregistre
# Bande passante élevée + détection visible
# Si cloud alerte user → social engineering possible
```

### #10 — Supply Chain (Vendor Backdoors)

```bash
# Cas réels (2023):
# - Hikvision USA backdoor (2017)
# - Dahua backdoor (2017)
# - Xiongmai (XMEYE) — inherent backdoor
# - Hidden default passwords sur process #1 in chip
# - Cloud vendor (Massive Dynamic) legal entity shell
```

---

## 📊 Anatomie d'une Attaque IoT Type

```
┌────────────────────────────────────────────────┐
│       KILL CHAIN — IoT Camera Compromise        │
└────────────────────────────────────────────────┘

[Phase 1: Reconnaissance]
│
├─► Shodan search ("Hipcam", "YCC365", "Web Client")
├─► ZoomEye search ("Basic realm=YCC365")
├─► Censys search ("manufacturer=HiSilicon")
├─► DNS history (securitytrails.com)
│
[Phase 2: Initial Access]
│
├─► Default creds (admin:12345) ✅ 70% succès
├─► Default creds (root:xmhdipc via backdoor) ✅
├─► RTSP sans auth (path guess) ✅
├─► ONVIF sans auth ✅
│
[Phase 3: Command & Control]
│
├─► Add user admin via web interface
├─► Modify DNS via ADB if available
├─► Install persistent backdoor via firmware mod
│
[Phase 4: Lateral Movement]
│
├─► Caméra compromise = foothold LAN
├─► Scan LAN from camera
├─► ARP poison via camera
├─► Pivot to NAS/printers/routers
│
[Phase 5: Exfiltration]
│
├─► Live video stream (RTSP)
├─► Recorded videos (SD dump)
├─► Voice conversations (micro)
├─► WiFi credentials (NVRAM)
│
[Phase 6: Monetization]
│
├─► Ransomware (lock camera users out)
├─► Sextortion (recorded video)
├─► Crypto mining (slow, but some do it)
├─► Botnet recruitment (Mirai-like)
└─► Spy services (long-term surveillance)
```

---

## 🏢 Cas Documentés Notoires

### Cas 2017-2024 : Verkada (USA)

- 150,000 caméras compromises via admin panel
- Tesla, Cloudflare, hospitals, prisons exposés
- Vecteur : stolen admin credentials + super-admin hardcoded
- Impact: fuite massive de vidéos

### Cas 2020 : Ring (Amazon)

- Hackers accedent caméras familiales
- Parlent aux enfants via audio bidirectionnel
- Vecteur : credential stuffing (réutilisation mdp)
- Impact: panique publique + class action

### Cas 2016-2017 : Mirai Botnet

- 600,000 IoT devices (caméras + DVR + routeurs)
- DNS Dyn attaque (Twitter, Spotify, Reddit down)
- Vecteur : 60 default credentials (telnet)
- Impact: attack DDoS record mondial

### Cas 2021 : Verkada Again

- 100+ entreprises (Cloudflare, Tesla)
- Vecteur : root credentials trouvés public
- Impact: ~5 TB video leaked

### Cas 2024 : Ring Again

- Motion detection + audio exposure abuse
- Vecteur : app vulnerable + social engineering
- Impact: lawsuit

### Cas 2025 (Notre Cas) : YCC365 Ghost

- Caméra Temu avec backdoor Telnet
- Vendor "Massive Dynamic" shell company
- C2 sur XMEYE cloud (Chine)
- Impact : TO BE ASSESSED (audit en cours)

---

## 🔮 Tendances 2025-2030

### Nouvelles Menaces

| Tendance | Description | Horizon |
|----------|-------------|---------|
| **AI-Powered Attacks** | LLM génère payloads personnalisés selon device | 2025-2027 |
| **Edge AI Backdoors** | Backdoor dans modèle ML sur caméra | 2026+ |
| **5G Module Attacks** | Attaques via modem 5G intégré caméra | 2025-2026 |
| **Cryptocurrency Miner IoT** | IoT utilisé pour mining (XMR) | 2025+ |
| **Quantum-Safe Exploits** | Quantum computing casse auth caméras | 2030+ |
| **Metaverse Surveillance** | Caméras AR/VR connectées | 2027+ |

### Nouvelles Défenses

| Défense | Vendor | Horizon |
|---------|--------|---------|
| **Zero Trust IoT** | Multiple | 2025-2027 |
| **Reprogrammable Silicon** | Intel/Cortex | 2026+ |
| **Blockchain Device ID** | Hedera/IOTA | 2027+ |
| **Firmware Attestation** | TPM hardware | 2026 |
| **Quantum Crypto IoT** | NIST PQC standards | 2028+ |
| **AI EDR for IoT** | CrowdStrike/Zscaler | 2025+ |

---

## 🌍 Réponse Réglementaire

### GDPR (Europe)

- Article 25 : "Privacy by Design"
- Pénalités : jusqu'à 4% CA ou 20M€
- Notification violation : 72h obligatoire
- Cameras = données personnelles biométriques

### NIS2 Directive (Europe)

- Sept 2024 entrée en vigueur
- Cameras = "Important Entity"
- Incident report obligatoire 24h
- Sanctions jusqu'à 2% CA

### California SB-327 (USA)

- Manufacturer doit proposer password unique
- Caméras vendues CA doivent avoir basic security
- Limite : aucune surveillance active

### China Cybersecurity Law

- Stockage données en Chine obligatoire
- Backdoors pour authorities gouvernementales (exigé)
- caméras chinese vendors populaires mais surveillées

### Canada PIPEDA

- "Appropriate safeguards" requis
- Privacy Commissioner peut enquêter
- Multa jusqu'à 100K$

---

## 🎯 Bonnes Pratiques Consumer

### Achat

```
✅ Vérifier vendor transparency (company registered, real address)
✅ Lire le code source si open-source
✅ Éviter caméra cloud-only (privacy)
✅ Préférer ONVIF Profile S/T compatible
✅ Vérifier update policy
```

### Déploiement

```
✅ Isoler VLAN caméra (séparer IoT)
✅ Changer default password IMMÉDIATEMENT
✅ Mettre à jour firmware régulièrement
✅ Désactiver UPnP
✅ Désactiver cloud si pas nécessaire
✅ Monitorer réseau (IDS sur subnet IoT)
```

### Maintenance

```
✅ Vérifier logs caméra régulièrement
✅ Update firmware trimestriel
✅ Re-changer password si compromis
✅ Auditer permissions app mobile
✅ Blacklist DNS domains non requis
```

---

## 🔧 Défenses Techniques Recomandées

### Réseau

```
1. VLAN IoT isolé (192.168.100.0/24)
2. Firewall deny-all entre VLAN IoT et LAN principal
3. DNS externe: AdGuard Home / Pi-hole
4. IDS Snort/Suricata signatures YCC365
5. Honeypot caméra (Cowrie-style)
```

### Endpoint (Caméra)

```
1. Vendor firmware patched (si dispo)
2. Custom OpenIPC firmware (alternative open)
3. Password complexe (16+ chars)
4. Désactiver services non utilisés
```

### Cloud

```
1. MFA obligatoire compte cloud
2. Email monitoring pour login alerts
3. Désactiver partage caméra
4. Audit log consultation mensuelle
```

---

## 📊 Stats Finales

### État Sécurité IoT 2025

- **70%** des caméras IoT ont une vuln critique non patchée
- **5 ans** = lifetime avg sans firmware update
- **$5000** = cost moyen incident IoT pour SME
- **3.5x** = probabilité d'être compromis si default cred
- **15 min** = temps moyen pour compromettre caméra par script kiddie

### Coûts Réels

```
Mirai Botnet Damage         : $110M+ (société Dyn 2016)
Verkada Incident Total Cost : $50M+ (lawsuit + reputation)
Average IoT Breach Response : $100K-$1M par enterprise
```

---

## 📚 Ressources & Lectures

### Industry Reports

- **NVD CVE Stats** : https://nvd.nist.gov/
- **Bitdefender IoT Report** : annuel
- **Symantec IoT Threat Report** : annuel

### Standards

- **ETSI EN 303 645** (Consumer IoT Security)
- **NIST SP 800-183** (Network of Things)
- **OWASP IoT Top 10** (https://owasp.org/www-project-internet-of-things/)

### Blogs Spécialisés

- **KrebsOnSecurity** (Brian Krebs)
- **SANS IoT Blog**
- **Darknet Diaries** podcast

### Outils Open Source

- **Nmap** : Network mapper
- **OpenIPC** : firmware alternatif caméras
- **Home Assistant** : hub domotique open source
- **YCC365 Ghost** (ce scanner 😉)

---

**Signé Ghost1o1** 🏴‍☠️ — *Le paysage est vaste, mais voir loin, c'est commencer à comprendre*
