# 🛡️ Défense & Remédiation — YCC365 / Hipcam

> Guide complet de défense pour sécuriser vos caméras YCC365 / Hipcam
> **Signé Ghost1o1** — *La défense, c'est l'art d'être plus malin que l'attaquant*

---

## 🎯 Principes Fondamentaux

### 1. Defense in Depth

```
┌──────────────────────────────────────────────────┐
│ Layer 7 : Politique & Formation                  │
│ Layer 6 : Monitoring & Détection (IDS, SIEM)     │
│ Layer 5 : Application (MFA, encryption)          │
│ Layer 4 : Cloud (Auth forte, rate limit)         │
│ Layer 3 : Caméra (Patch firmware, services off)  │
│ Layer 2 : Réseau (VLAN, firewall)                │
│ Layer 1 : Physique (Boitier sécurisé)            │
└──────────────────────────────────────────────────┘
Si 1 layer = compromis → 6 autres protègent
```

### 2. Least Privilege

- Caméra : VLAN IoT uniquement
- Pas d'Internet sortant (sauf NTP + vendor OTA)
- Compte cloud : permissions minimales

### 3. Zero Trust

- Chaque requête = vérifiée
- Pas de confiance implicite LAN
- Encryption end-to-end

---

## 🛠️ Plan de Remédiation (30 jours)

### Jour 1-3 : Quick Wins

```
[ ] Scanner la caméra (YCC365 Ghost)
[ ] Documenter findings
[ ] Changer TOUS les mots de passe:
    - admin
    - support
    - root (si possible via interface)
    - Minimum 12 chars: Maj+Min+Chiffre+Spéciaux
    - Exemple: "Gh0st1o1Cam!2026#Ycc365"
[ ] Activer 2FA sur compte cloud
[ ] Désactiver UPnP sur routeur
[ ] Activer HTTPS sur caméra (si possible)
[ ] Update firmware (dernière version officielle)
[ ] Stocker credentials chiffrés (KeePass/Bitwarden/Pass)
```

### Jour 4-7 : Segmentation Réseau

```
OPTION A: Routeur enterprise (Mikrotik, OpenWRT, pfSense)
- VLAN 10 - IoT Cameras: 192.168.10.0/24
- VLAN 20 - LAN family: 192.168.20.0/24
- Firewall: VLAN 10 → VLAN 20: DENY
- Firewall: VLAN 10 → Internet: ALLOW only NTP, OTA

OPTION B: Routeur grand public
- Use "Guest Network" feature pour IoT
- Activer Network Isolation / Client Isolation
```

#### DNS Filtering (Pi-hole / AdGuard Home)

```bash
# Setup Pi-hole / AdGuard Home sur Raspberry Pi

# Blacklist domains :
# - *.xmeye.net (cloud XMEYE si non utilisé)
# - *.ycc365.net (cloud YCC365)
# - *.amazonaws.com (potential exfil)
# - *.cloudfront.net

# Whitelist (autoriser):
# - pool.ntp.org (time)
# - update.ycc365.com (firmware officiel)
```

### Jour 8-14 : Monitoring & Détection

#### Suricata IDS

```bash
sudo apt install suricata

# Règles custom YCC365/Hipcam
cat > /etc/suricata/rules/ycc365-ghost.rules << 'EOF'
alert http any any -> $HOME_NET 34567 (
  msg:"YCC365 ADMIN BRUTE FORCE";
  content:"Authorization"; http_header;
  threshold: type both, track by_src, count 5, seconds 60;
  sid:1000001; rev:1;)

alert tcp any any -> $HOME_NET 554 (
  msg:"RTSP UNAUTH REQUEST";
  flow:to_server,established;
  content:"DESCRIBE"; nocase;
  sid:1000002; rev:1;)

alert http any any -> $HOME_NET 8899 (
  msg:"ONVIF PROBE ATTEMPT";
  content:"GetDeviceInformation";
  sid:1000003; rev:1;)

alert tcp any any -> $HOME_NET 9527 (
  msg:"TELNET BACKDOOR PORT TOUCHED";
  classtype:trojan-activity;
  sid:1000004; rev:1;)

alert tcp any any -> $HOME_NET 5552 (
  msg:"ADB DEVICE ACCESS";
  classtype:trojan-activity;
  sid:1000005; rev:1;)
EOF

sudo systemctl restart suricata
```

### Jour 15-21 : Application Layer

#### YCC365 App Hardening

```
[ ] App Permissions:
    - Camera (requis)
    - Storage (optionnel)
    - Location (NON REQUIS - désactiver)
    - Contacts (NON REQUIS - refuser)
    - Microphone (NON REQUIS - désactiver)

[ ] Privacy:
    - Désactiver "Save recordings to cloud"
    - Use SD card local
    - Activer "E2E encryption" si dispo
    - Désactiver "Allow remote access" si non utilisé
    - Désactiver "Share with family"

[ ] Account:
    - Email dédié (pas Gmail principal)
    - 2FA activé
    - Sessions actives review
    - Sign out des anciens devices
```

#### Alternatives Open Source

```bash
# Option 1: Motion (NVR open source)
sudo apt install motion

# Option 2: ZoneMinder (NVR complet)
sudo apt install zoneminder

# Option 3: Frigate (AI + NVR)
docker run -d --name frigate \
  -v /path/to/config:/config \
  -p 8979:8979 \
  ghcr.io/blakeblackshear/frigate:stable

# Option 4: OpenIPC firmware (remplace firmware vendor)
# ⚠️ Vérifier compat avec votre modèle exact
# https://openipc.org/
```

### Jour 22-30 : Advanced Hardening

#### Désactiver Ports Non-Nécessaires

```
Via interface admin YCC365 :
- Settings → Network → Services → Disable:
  ⚠️ Telnet (9527) - MOST IMPORTANT
  ⚠️ RTSP (554) if not used
  ⚠️ ONVIF (8899) if not used
  ⚠️ ADB (5552) - VERY IMPORTANT
```

#### Replace Firmware with OpenIPC

```bash
# ⚠️ ATTENTION: Risque brick
# Suivre docs OpenIPC pour votre modèle

# Avantages:
# - Firmware open source
# - Pas de backdoor Telnet
# - Config Linux standard
# - HTTPS par défaut
# - RTSP over TLS
# - MAJ OTA sécurisées
```

---

## 🔥 Actions d'Urgence (Si Déjà Compromis)

### IoC (Indicateurs de Compromission)

```
[ ] Trafic réseau sortant non habituel (Wireshark)
[ ] Logs routeur / firewall avec connections bizarres
[ ] CPU/RAM utilization toujours élevée
[ ] LED caméra clignote même sans mouvement
[ ] Camera reboot toute seule
[ ] Settings admin modifiés sans votre action
[ ] Cloud account "online" 24/7
```

### Réponse Immédiate

```
1. DÉCONNECTER CAMÉRA DU RÉSEAU (débrancher Ethernet)
2. Documenter état (photos, settings)
3. Sauvegarder SD card avant reformat
4. Vérifier autres devices LAN compromis (nmap -sV)
5. Changer TOUS les passwords (autres services aussi)
6. Factory reset caméra (après débranchement)
7. Flash OpenIPC ou nouveau firmware vendor
8. Reconfigurer avec credentials forts
9. Surveiller trafic pendant 1 semaine (IDS)
```

### Investigation Forensic (Si accès PHY)

```bash
1. Extraire SD card
2. Image bit-perfect:
   dd if=/dev/mmcblk0 of=/tmp/cam_dump.img bs=1M conv=noerror,sync
3. Monter en read-only:
   sudo mount -o ro,loop /tmp/cam_dump.img /mnt/cam_forensic
4. Analyse:
   - /etc/passwd (backdoor users)
   - /etc/crontab (scheduled tasks)
   - /var/log/ (tous logs)
   - /tmp/ (fichiers temporaires)
5. Extraire firmware running:
   - /dev/mtdblock0 (raw flash)
   - binwalk sur firmware.bin
   - Strings pour malware signatures
```

---

## 📚 Matrice de Remédiation

| Finding | CVSS | Action | Effort | Impact |
|---------|------|--------|--------|--------|
| Telnet BD actif | 9.8 | Désactiver / OpenIPC | M | Critique |
| Default creds | 9.1 | Changer passwords | L | Critique |
| RTSP sans auth | 7.5 | Activer auth + digest | M | Élevé |
| ONVIF disc. | 5.3 | Limiter IP ONVIF | L | Modéré |
| ADB port 5552 | 9.8 | Désactiver ADB | L | Critique |
| Cloud IDOR | 6.5 | N/A (vendor) | N/A | Modéré |
| WS-Discovery | 3.7 | Firewall block | L | Faible |
| Firmware OTA open | 5.3 | Signature (rare) | H | Modéré |

L=Low (30min), M=Medium (2-4h), H=High (1-3 jours)

---

## 📚 Ressources

- **NIST CSF** : Identify, Protect, Detect, Respond, Recover
- **CIS Controls v8**
- **OWASP IoT Top 10**
- **ISO 27001/27002**
- **OpenIPC Project** (open source firmware)
- **Suricata/Snort** IDS

---

**Signé Ghost1o1** 🏴‍☠️ — *La meilleure défense, c'est la connaissance + l'action*
