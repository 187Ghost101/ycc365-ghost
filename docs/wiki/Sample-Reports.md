# 📊 Exemples de Rapports Générés

> Samples des outputs du scanner YCC365 Ghost
> **Signé Ghost1o1** — *Voir c'est comprendre*

---

## 📄 Rapport A: Scan Complet (High Risk)

### Contexte

- Cible: `192.168.1.100` (caméra YCC365 Plus Temu)
- Vendor: Massive Dynamic (Cloud: XMEYE)
- Date: 2026-06-29
- Durée: 47 secondes

### Output Console (Extrait)

```
🎯 Cible: 192.168.1.100

═══ Phase 1: Port Scan ═══
  [OPEN] 34567 (YCC365 admin)
  [OPEN] 9527  (Telnet backdoor)
  [OPEN] 554   (RTSP)
  [OPEN] 8899  (ONVIF)
  [OPEN] 80    (HTTP)
  [OPEN] 23    (Telnet)
  [OPEN] 5552  (ADB)
  [OPEN] 37777 (Dahua)

═══ Phase 2: Bruteforce ═══
  [VALID] admin:12345 (HTTP 200)
  [VALID] admin:admin (HTTP 200)
  [VALID] root:xmhdipc (HTTP 200)

═══ Phase 3: RTSP ═══
  [ACCESSIBLE] /11, /12, /onvif/streaming/channels/101, etc.

═══ Phase 4: Telnet Backdoor ═══
  [CRITICAL] BACKDOOR ACTIF! root:x:0:0:root:/root:/bin/sh

═══ Phase 5: ONVIF ═══
  [ONVIF] manufacturer=HiSilicon, model=YCC365-Plus, firmware=V2.1.4.2

═══ Module 4: Username Arsenal ═══
  [HIT] admin:12345, admin:admin, root:xmhdipc, support:support, user:user
  ✅ 6 credentials valides

═══ Module 5: Cloud Domain Mapper ═══
  ✅ 32/42 domaines accessibles
  🔒 28 avec HTTPS
  🌐 Cloud: aliyun, tencent, aws

✅ Rapport: /tmp/ycc365_192.168.1.100_*.json
```

### JSON Output (Extrait)

```json
{
  "target": "192.168.1.100",
  "timestamp": "2026-06-29T17:23:09Z",
  "duration_seconds": 47.3,
  "open_ports": [
    {"port": 34567, "state": "open", "service": "YCC365 admin"},
    {"port": 9527, "state": "open", "service": "Telnet backdoor"},
    {"port": 554, "state": "open", "service": "RTSP"},
    {"port": 8899, "state": "open", "service": "ONVIF"},
    {"port": 80, "state": "open", "service": "HTTP"},
    {"port": 23, "state": "open", "service": "Telnet"},
    {"port": 5552, "state": "open", "service": "ADB"},
    {"port": 37777, "state": "open", "service": "Dahua"}
  ],
  "valid_credentials": [
    {"user": "admin", "password": "12345", "port": 34567, "success": true, "http_code": 200},
    {"user": "root", "password": "xmhdipc", "port": 34567, "success": true, "http_code": 200}
  ],
  "telnet_backdoor_active": true,
  "onvif_info": {
    "manufacturer": "HiSilicon",
    "model": "YCC365-Plus",
    "firmware": "V2.1.4.2",
    "serial": "YK123456789"
  },
  "vulnerabilities": [
    {"id": "VULN-001", "title": "Telnet Backdoor Active (CVE-2021-32960)",
     "cvss": 9.8, "severity": "CRITICAL", "cwe": "CWE-798"},
    {"id": "VULN-002", "title": "Default Credentials",
     "cvss": 9.1, "severity": "CRITICAL", "cwe": "CWE-798"},
    {"id": "VULN-003", "title": "ADB Exposed",
     "cvss": 9.8, "severity": "CRITICAL", "cwe": "CWE-489"},
    {"id": "VULN-004", "title": "RTSP Stream Sans Auth",
     "cvss": 7.5, "severity": "HIGH", "cwe": "CWE-306"},
    {"id": "VULN-005", "title": "ONVIF Info Disclosure",
     "cvss": 5.3, "severity": "MEDIUM", "cwe": "CWE-200"}
  ]
}
```

### Résumé Management

```
🛑 CAMÉRA HAUT RISQUE — 4 vulnérabilités CRITICAL

❌ VULN-001 — Backdoor Telnet (root:xmhdipc) — Score 9.8/10
❌ VULN-002 — Default password admin:12345 — Score 9.1/10
❌ VULN-003 — ADB exposed — Score 9.8/10
⚠️  VULN-004 — RTSP sans auth — Score 7.5/10

ACTIONS REQUISES (URGENT):
1. Déconnecter caméra du réseau
2. Changer TOUS les mots de passe
3. Mettre à jour firmware
4. Isoler caméra sur VLAN dédié
5. Désactiver Telnet et ADB si possible
6. Activer auth RTSP
```

---

## 📄 Rapport B: Scan Partiel (Low Risk)

### Contexte

- Cible: `192.168.1.50` (Hikvision récent)
- Vendor: Hikvision officiel

### Output Console (Extrait)

```
🎯 Cible: 192.168.1.50

═══ Phase 1: Port Scan ═══
  [OPEN] 80, 443, 554

═══ Phase 2: Bruteforce ═══
  [FAIL] admin:12345 (HTTP 401)
  ...
  [VALID] admin:Admin12345 (HTTP 200) ✅

═══ Phase 4: Telnet Backdoor ═══
  [!] Port 9527 fermé

═══ Module 4: Username Arsenal ═══
  [HIT] admin:Admin12345 → HTTP 200
  ✅ 1 credential valide

═══ Module 5: Cloud Domain Mapper ═══
  ✅ 35/42 domaines accessibles
```

### Résumé

```
🟢 RISQUE MODÉRÉ — 1 finding MEDIUM

⚠️  VULN-002 — Password faible "Admin12345" — Score 4.5/10

ACTIONS:
1. Changer password pour 16+ chars
2. Activer 2FA si disponible
3. Limiter accès admin à votre IP locale
```

---

## 📄 Rapport C: Scan Vierge (No Findings)

### Contexte

- Cible: `192.168.1.150` (Frigate+Zoneminder, open source)

### Output

```
🎯 Cible: 192.168.1.150

═══ Phase 1: Port Scan ═══
  [OPEN] 80, 443, 554

═══ Phase 2: Bruteforce ═══
  [!] Aucun port HTTP ouvert sans auth

═══ Phase 3: RTSP ═══
  [REQUIRED AUTH] Tous paths 401

═══ Phase 4: Telnet Backdoor ═══
  [!] Port 9527 fermé

═══ Phase 5: ONVIF ═══
  [REQUIRED AUTH] GetDeviceInformation

═══ Module 4: Username Arsenal ═══
  [!] Aucun hit — Auth correcte

✅ RAPPORT: Caméra sécurisée — 0 vulnérabilités
```

---

## 🔍 Comment Lire un Rapport

### Étape 1: Identifier Vuln Critiques

```python
import json
with open("/tmp/ycc365_*.json") as f:
    data = json.load(f)

critical = [v for v in data['vulnerabilities']
            if v['severity'] == 'CRITICAL']

if critical:
    print(f"🚨 {len(critical)} vulnerabilités critiques")
    for v in critical:
        print(f"  {v['title']} (CVSS {v['cvss']})")
else:
    print("✅ Aucune vulnérabilité critique")
```

### Étape 2: Vérifier Credentials Exposés

```python
if data['valid_credentials']:
    print(f"❌ {len(data['valid_credentials'])} credentials exposées")
    for c in data['valid_credentials']:
        print(f"  {c['user']}:{c['password']} sur port {c['port']}")
```

### Étape 3: Vérifier Cloud C2

```python
cloud = data['cloud_mapper']
if cloud['reachable'] > 5:
    print(f"⚠️  Caméra contacte {cloud['reachable']} domaines cloud")
    print(f"   Providers: {cloud['cloud_providers_found']}")
```

---

## 📌 Conclusion des Samples

Les rapports du scanner YCC365 Ghost sont :

1. **Structurés** : JSON facilement parsable
2. **Complets** : 7 phases × multiples findings par phase
3. **Actionables** : chaque finding a une remediation connue
4. **Compatibles** : intégration possible avec outils tiers (DefectDojo)
5. **Format mixtes** : JSON brut + Markdown + custom templates

**Signé Ghost1o1** 🏴‍☠️ — *Un bon rapport, c'est 50% de la valeur d'un audit*
