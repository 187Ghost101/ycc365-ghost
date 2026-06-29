# 🧪 Testing Guide — Utilisation du Scanner

> Guide pratique d'utilisation du scanner YCC365 Ghost sur vos propres équipements
> **Signé Ghost1o1** — *Testez comme un pro*

---

## 🚀 Installation

### Prérequis

```bash
# Linux (Debian/Kali)
sudo apt install -y nmap ncat curl jq python3 python3-pip binwalk

# Termux (Android)
pkg install -y nmap ncat curl jq python binutils

# macOS (Homebrew)
brew install nmap ncat curl jq python3 binwalk
```

### Versions Requises

| Outil | Version Min | Vérification |
|-------|-------------|--------------|
| Python | 3.10+ | `python3 --version` |
| nmap | 7.80+ | `nmap --version` |
| curl | 7.74+ | `curl --version` |
| Bash | 4+ | `bash --version` |
| Java (pour APK) | 8+ | `javac -version` |

---

## 📥 Téléchargement

### Option 1: Clone Git (développeurs)

```bash
git clone https://github.com/187Ghost101/ycc365-ghost.git
cd ycc365-ghost
ls -la
```

### Option 2: APK seul (Android)

```
https://github.com/187Ghost101/ycc365-ghost/releases/download/v1.0.0/ycc365-ghost-1.0.0.apk
```

Télécharger, transférer sur téléphone, installer (autoriser "sources inconnues").

### Option 3: Script Termux seul

```bash
curl -L https://github.com/187Ghost101/ycc365-ghost/releases/download/v1.0.0/ycc365-ghost-1.0.0.apk \
  -o ycc365-ghost.apk
# Extract assets via:
unzip -j ycc365-ghost.apk "assets/ycc365-ghost.sh" -d /tmp/
chmod +x /tmp/ycc365-ghost.sh
```

---

## 🎯 Usage Python (Recommandé)

### Scan Rapide

```bash
cd ycc365-ghost
python3 -m scanner.core 192.168.1.100
```

Output :
```
🎯 Cible: 192.168.1.100
⏱️  Démarrage: 2026-06-29T17:23:09Z

═══ Phase 1: Port Scan ═══
  [OPEN] 34567 (YCC365 admin)
  [OPEN] 9527  (Telnet backdoor)
  [OPEN] 554   (RTSP)
  [OPEN] 8899  (ONVIF)

═══ Phase 2: Bruteforce ═══
  [*] Test port 34567...
  [VALID] admin:12345 (HTTP 200)
  [VALID] root:xmhdipc (HTTP 200)

═══ Phase 3: RTSP ═══
  [ACCESSIBLE] /11
  [ACCESSIBLE] /live/main

═══ Phase 4: Telnet Backdoor ═══
  [CRITICAL] BACKDOOR ACTIF!

═══ Phase 5: ONVIF ═══
  [ONVIF] {'manufacturer': 'HiSilicon', 'model': 'YCC365-Plus', ...}

═══ Module 4: Username Arsenal (Sherlock-style) ═══
  [*] 58 usernames × 19 passwords
  [*] Ports cibles: [34567]

  [HIT] admin:12345 → HTTP 200 (port 34567)
  [HIT] root:xmhdipc → HTTP 200 (port 34567)

  ✅ 2 credentials valides découverts

═══ Module 5: Cloud Domain Mapper ═══
  [*] 42 domaines à cartographier

  [ 1/42] xmeye.net... ✅ 1 IPs (aliyun)
  [ 2/42] ycc365.com... ✅ 2 IPs
  [ 3/42] lookcam.live... ✅ 1 IPs
  ...

  ✅ 38/42 domaines accessibles
  🔒 32 avec HTTPS actif
  📜 30 certificats SSL valides

✅ Rapport: /tmp/ycc365_192.168.1.100_20260629_172309.json
```

### Scan Custom

```python
# custom_scan.py
from scanner import GhostScanner
from scanner.usernames import UsernameArsenal
from scanner.cloudmapper import CloudDomainMapper

target = "192.168.1.100"

# Phase 6: Username Arsenal seulement
ua = UsernameArsenal(target, timeout=5)
hits = ua.run(http_ports=[80, 443, 8000, 34567])
print(f"Hits Username Arsenal: {len(hits)}")
for h in hits:
    print(f"  {h.username}:{h.password} → port {h.port} HTTP {h.http_code}")

# Phase 7: Cloud Mapper seulement
cm = CloudDomainMapper(target)
results = cm.run()
print(f"Stats: {cm.stats()}")
print(f"Reachable domains: {[r.domain for r in cm.results if r.reachable]}")
```

### Timeout Custom

```bash
# Scan agressif (5 sec timeout)
python3 -m scanner.core 192.168.1.100 --timeout 5

# Scan lent (anti-IDS, 10 sec timeout)
python3 -m scanner.core 192.168.1.100 --timeout 10
```

### Output JSON

```bash
# Le rapport est sauvé dans /tmp/
cat /tmp/ycc365_192.168.1.100_*.json | jq . | head -50
```

---

## 📱 Usage APK Android

### Installation

```
1. Téléchargez ycc365-ghost-1.0.0.apk depuis GitHub Releases
2. Transférez sur téléphone (USB / cloud / email)
3. Activez "Sources inconnues" dans Paramètres > Sécurité
4. Ouvrez le fichier APK avec un File Manager
5. Installez
6. Lancez "YCC365 Ghost Scanner" depuis le menu
```

### UI

```
┌────────────────────────────────────┐
│   🏴‍☠️ YCC365 Ghost Scanner      │  ← Banner Ghost1o1 (or/cyan)
│   v1.0.0 — Signé Ghost1o1          │
├────────────────────────────────────┤
│                                    │
│  IP Cible: [192.168.1.100____]     │  ← Input IP caméra
│                                    │
│  [   DÉMARRER SCAN PHASE 1+2   ]  │  ← Bouton 1
│  [   TEST RTSP (Phase 3)       ]  │  ← Bouton 2
│  [   TEST ONVIF (Phase 5)      ]  │  ← Bouton 3
│  [   BACKDOOR TELNET (Phase 4) ]  │  ← Bouton 4
│                                    │
│  ┌──────────────────────────────┐  │
│  │ Output:                      │  │  ← ScrollView
│  │ [OPEN] 9527: Telnet BD       │  │
│  │ [VALID] admin:12345          │  │
│  │ ...                          │  │
│  └──────────────────────────────┘  │
│                                    │
│  Signé Ghost1o1 🏴‍☠️              │
└────────────────────────────────────┘
```

### Limitations APK

- Pas d'accès root requis (utilise `Runtime.exec` Java)
- Network en arrière-plan : OUI nécessaire pour scan
- Les payloads sont exécutés via bash intégré Java (proc/self/exe)
- Pour exploitation avancée, utilsez le Python scan plutôt

---

## 🐚 Usage Termux

### Installation Rapide

```bash
# Si APK installé:
unzip -j /data/data/com.termux/files/home/ycc365-ghost.apk \
  "assets/ycc365-ghost.sh" -d $PREFIX/bin/

chmod +x $PREFIX/bin/ycc365-ghost.sh
ycc365-ghost.sh 192.168.1.100
```

### Scan One-Shot

```bash
bash ycc365-ghost.sh 192.168.1.100 --all --json
```

### Options

```bash
bash ycc365-ghost.sh <IP> [options]

Options:
  --all          Active TOUTES les phases
  --ports-only   Que Phase 1 (port scan)
  --creds-only   Que Phase 2 (bruteforce)
  --rtsp-only    Que Phase 3
  --telnet-only  Que Phase 4
  --onvif-only   Que Phase 5
  --json         Output JSON structuré
  --timeout N    Timeout en secondes (défaut: 5)
  --report PATH  Chemin du fichier rapport
```

---

## 🔬 Exemples Avancés

### Exemple 1: Scan Multi-Cibles

```python
# scan_multi.py
import sys
sys.path.insert(0, '.')

from scanner import GhostScanner

targets = [
    "192.168.1.100",
    "192.168.1.101",
    "192.168.1.102",
]

for target in targets:
    print(f"\n{'='*60}")
    print(f"SCAN: {target}")
    print(f"{'='*60}\n")
    
    scanner = GhostScanner(target, timeout=3)
    result = scanner.run_full_scan()
    
    # Summary
    print(f"\n📊 Summary for {target}:")
    print(f"  Open ports: {len(result.open_ports)}")
    print(f"  Valid creds: {len(result.valid_credentials)}")
    print(f"  Backdoor: {result.telnet_backdoor_active}")
    print(f"  Vulnerabilities: {len(result.vulnerabilities)}")
```

### Exemple 2: Scan avec Fichier de Sortie

```python
# scan_with_report.py
import sys, json
sys.path.insert(0, '.')

from scanner import GhostScanner
from scanner.usernames import UsernameArsenal
from scanner.cloudmapper import CloudDomainMapper

target = "192.168.1.100"

# Phases 1-5
gs = GhostScanner(target, timeout=4)
gs.run_full_scan()
result = gs.result

# Phase 6 seule
ua = UsernameArsenal(target)
ua.run(http_ports=[p.port for p in result.open_ports
                    if p.port in (80, 443, 8000, 8080)])

# Phase 7 seule
cm = CloudDomainMapper(target)
cm.run()

# Aggregate
combined = {
    "target": target,
    "phases_1_to_5": result.to_dict(),
    "phase_6_username_arsenal": {
        "hits": [h.__dict__ for h in ua.hits],
        "stats": ua.stats(),
    },
    "phase_7_cloud_mapper": {
        "domains": [d.to_dict() for d in cm.results],
        "stats": cm.stats(),
    },
}

# Save
import datetime
ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
path = f"/tmp/combined_{target}_{ts}.json"
with open(path, 'w') as f:
    json.dump(combined, f, indent=2, default=str)
print(f"Saved: {path}")
```

### Exemple 3: Custom Wordlist

```python
# Custom wordlist integration
import sys
sys.path.insert(0, '.')

from scanner import GhostScanner

gs = GhostScanner("192.168.1.100")

# Custom creds
gs.DEFAULT_CREDENTIALS = [
    ("admin", "12345"),    # YCC365 default
    ("admin", "ycc365"),   # Custom
    ("admin", "ghost1o1"), # Branded
    # ... ajouter ici
]

gs.run_full_scan()
```

### Exemple 4: Filtre Rapide par Findings Critiques

```python
# audit_critical.py
import sys, glob
sys.path.insert(0, '.')
import json

# Scan tous les rapports générés
for report in glob.glob("/tmp/ycc365_*.json"):
    with open(report) as f:
        data = json.load(f)
    
    critical = [v for v in data.get('vulnerabilities', [])
                if v.get('severity') == 'CRITICAL']
    
    if critical:
        print(f"\n🚨 {report}:")
        for v in critical:
            print(f"  [{v['cvss']}] {v['title']}")
            print(f"     CWE: {v.get('cwe', 'N/A')}")
            print(f"     Evidence: {v.get('evidence', 'N/A')[:100]}")
```

---

## 🐛 Troubleshooting

### "Java not found"

```bash
sudo apt install default-jdk
# Or:
sudo apt install openjdk-17-jdk-headless
```

### "ncat non installé"

```bash
sudo apt install ncat
# Or:
sudo apt install netcat-openbsd
```

### "Permission denied" sur APK

Paramètres Android > Sécurité > Sources inconnues > ON

### "Connection timed out" sur caméras offline

```bash
# Verify IP connectivity d'abord
ping -c 1 192.168.1.100

# Check firewall rules
sudo iptables -L -n
```

### "no module named scanner"

```bash
# Run from repo root
cd ycc365-ghost
python3 -m scanner.core <IP>
```

### Scan Lent

```bash
# Réduire timeout
python3 -m scanner.core 192.168.1.100 --timeout 1

# Ou scanner que les ports connus
python3 -c "
import sys; sys.path.insert(0, '.')
from scanner import GhostScanner
gs = GhostScanner('192.168.1.100', timeout=1)
gs.phase1_port_scan()  # Phase 1 seulement
"
```

---

## 📚 Ressources

- [📋 Methodology](Methodology) — Framework pentest
- [🎯 Attack-Surface](Attack-Surface) — Surface d'attaque
- [🧩 Modules-Reference](Modules-Reference) — Référence des modules
- [💀 CVE-Mapping](CVE-Mapping) — CVEs affectant l'écosystème

---

**Signé Ghost1o1** 🏴‍☠️ — *Tester, c'est apprendre à défendre*
