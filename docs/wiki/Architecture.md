# 🏛️ Architecture Technique

> Vue d'ensemble du scanner YCC365 Ghost — Composants, flux de données, design patterns

**Signé Ghost1o1** — *L'architecture, c'est le squelette de la machine.*

---

## 🎯 Vue d'Ensemble (C4 Model)

```
┌─────────────────────────────────────────────────────────────────┐
│                     YCC365 GHOST SCANNER v1.0                   │
│                     Signé Ghost1o1 🏴‍☠️                          │
└─────────────────────────────────────────────────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
   ┌────▼─────┐             ┌─────▼──────┐          ┌──────▼──────┐
   │  PYTHON  │             │  ANDROID   │          │   TERMUX    │
   │  CORE    │             │  APK       │          │   SHELL     │
   │  v3.10+  │             │  API 21-33 │          │  Bash 4+    │
   └────┬─────┘             └─────┬──────┘          └──────┬──────┘
        │                         │                         │
        │   ┌─────────────────────┼─────────────────────┐   │
        │   │                     │                     │   │
        │ ┌─▼────────┐    ┌──────▼──────┐    ┌────────▼─┐ │   │
        │ │ Scanner  │    │  Mappers    │    │  Reports │ │   │
        │ │ Modules  │    │  (DNS/HTTP) │    │ (JSON/   │ │   │
        │ │  (5)     │    │             │    │  TXT)    │ │   │
        │ └──────────┘    └─────────────┘    └──────────┘ │   │
        └─────────────────────────────────────────────────┘   │
                                  │                             │
                          ┌───────▼────────┐                    │
                          │   CAMERA IP    │ ◄──────────────────┘
                          │   (Target)     │
                          │ YCC365/Hipcam  │
                          └────────────────┘
```

---

## 🏗️ Composants Principaux

### 1️⃣ Scanner Core (`scanner/core.py`)

Le moteur principal orchestre 7 phases de scan :

| Phase | Module | Description |
|-------|--------|-------------|
| 1 | **Port Scan** | 16 ports YCC365/Hipcam scannés |
| 2 | **Bruteforce** | 23 credentials × ports HTTP |
| 3 | **RTSP Detection** | 21 paths RTSP énumérés |
| 4 | **Telnet Backdoor** | Port 9527 + brute `root/xmhdipc` |
| 5 | **ONVIF Probe** | SOAP sans auth (info disclosure) |
| 6 | **Username Arsenal** | 58 usernames × 19 passwords = 1102 tests |
| 7 | **Cloud Domain Mapper** | 42 domaines XMEYE/YCC365 cartographiés |

**Code de structure** :

```python
class GhostScanner:
    YCC365_PORTS = [...]              # 16 ports
    
    def run_full_scan(self) -> ScanResult:
        self.phase1_port_scan()
        self.phase2_bruteforce()
        self.phase3_rtsp()
        self.phase4_telnet_backdoor()
        self.phase5_onvif()
        self.phase6_username_arsenal()      # NEW v1.1
        self.phase7_cloud_mapper()          # NEW v1.1
        return self.result
```

### 2️⃣ Username Arsenal (`scanner/usernames.py`)

**Adapté de OSIN CHAIN UsernameSherlock (Module #4)** — cross-platform username enumeration sans rate-limit aggressif.

- **58 usernames** (admin, root, xmeye, hikvision, dahua, etc.)
- **19 passwords** (admin, 12345, xmhdipc, etc.)
- **1102 combinaisons** par port HTTP
- Test HTTP Basic Auth sur ports 80/443/8000/8080/34567/34599

### 3️⃣ Cloud Domain Mapper (`scanner/cloudmapper.py`)

**Adapté de OSIN CHAIN DomainMapper (Module #5)** — cartographie réseau d'infrastructure.

- **42 domaines** XMEYE/YCC365/LookCam connus
- Résolution DNS (A + AAAA records)
- Probe HTTP + HTTPS
- Banner grabbing (Server header)
- Inspection certificat SSL/TLS
- Détection cloud provider (Aliyun/Tencent/AWS/Akamai)

### 4️⃣ Android APK (`src/com/ghost1o1/ycc365/MainActivity.java`)

**200 lignes Java** — UI de scan sur téléphone Android.

- minSdk 21 (Android 5.0)
- targetSdk 33 (Android 13)
- Sans dépendances externes (pure Java)
- Signed RSA 2048 SHA384

### 5️⃣ Termux Scanner (`assets/ycc365-ghost.sh`)

**13 KB** de Bash portable — fonctionne dans Termux sans root.

```bash
bash ycc365-ghost.sh 192.168.1.100
```

---

## 📦 Structure Arborescente

```
ycc365-ghost/
├── 📄 README.md                    # Doc principale
├── 📄 LICENSE                      # MIT + disclaimer
├── 📄 SECURITY.md                  # Politique de divulgation
├── 📄 CHANGELOG.md                 # Historique versions
├── 📄 build.sh                     # Build APK one-shot
├── 📄 AndroidManifest.xml          # Manifest Android
│
├── 📁 src/com/ghost1o1/ycc365/
│   └── MainActivity.java           # 200 lignes UI Android
│
├── 📁 res/values/
│   ├── colors.xml                  # Palette Ghost1o1
│   ├── strings.xml                 # Textes UI
│   └── styles.xml                  # Styles Android
│
├── 📁 assets/
│   └── ycc365-ghost.sh             # Scanner Termux 13KB
│
├── 📁 scanner/
│   ├── __init__.py                 # Module entry point
│   ├── core.py                     # Moteur 7 phases (NEW v1.1)
│   ├── usernames.py                # Module 4 UsernameSherlock (NEW)
│   ├── cloudmapper.py              # Module 5 DomainMapper (NEW)
│   ├── theme.py                    # Palette ANSI 256
│   └── wordlists/
│       ├── credentials.txt         # 23 creds
│       ├── rtsp_paths.txt          # 21 paths
│       ├── usernames.txt           # 58 usernames (NEW)
│       └── cloud_domains.txt       # 42 domaines (NEW)
│
├── 📁 docs/
│   ├── ATTACK_SURFACE.md           # Analyse surface attaque
│   ├── ARCHITECTURE.md             # Ce fichier
│   ├── METHODOLOGY.md              # Méthodologie pentest
│   └── SCREENSHOTS.md              # Documentation visuelle
│
├── 📁 examples/
│   └── sample_report.txt           # Exemple rapport généré
│
├── 📁 .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── workflows/
│       └── build.yml               # CI/CD APK auto (optionnel)
│
├── 📁 fdroid/                      # NEW v1.1 — metadata F-Droid
│   ├── metadata.yml
│   ├── build.gradle
│   └── SUBMIT.md
│
├── 📁 bin/
│   └── ycc365-ghost-1.0.0.apk      # 16.9 KB signé
│
└── 📁 build/
    ├── ghost1o1.keystore           # Certificat de signature
    └── ...                         # Outputs de build
```

---

## 🔄 Flux de Données

### Workflow Scanner Python

```
[User input: IP target]
        │
        ▼
┌──────────────────┐
│ GhostScanner     │
│ .run_full_scan() │
└────────┬─────────┘
         │
         ├─► phase1_port_scan ─────► PortInfo[]
         │     (16 ports TCP connect)
         │
         ├─► phase2_bruteforce ────► CredentialTest[]
         │     (HTTP Basic Auth × 23 creds)
         │
         ├─► phase3_rtsp ──────────► RTSPPath[]
         │     (DESCRIBE × 21 paths)
         │
         ├─► phase4_telnet_backdoor ► bool + VulnList
         │     (ncat 9527 + brute)
         │
         ├─► phase5_onvif ─────────► onvif_info Dict
         │     (SOAP GetDeviceInformation)
         │
         ├─► phase6_username_arsenal ► UsernameHit[]
         │     (UsernameArsenal × ports HTTP)
         │
         └─► phase7_cloud_mapper ──► DomainInfo[]
               (CloudDomainMapper.run)
                      │
                      ▼
              ┌────────────────┐
              │   ScanResult   │
              │   .to_json()   │
              └────────┬───────┘
                       │
                       ▼
              /tmp/ycc365_<IP>_<timestamp>.json
```

### Workflow Android APK

```
[User lance l'APK]
        │
        ▼
┌─────────────────────────┐
│ MainActivity.onCreate() │
└────────┬────────────────┘
         │
         ▼
[Load layout activity_main.xml]
         │
         ▼
[Setup listeners sur boutons]
         │
         ├── Button "SCAN CAMERA" ─► build Command
         ├── Button "WORDLISTS" ───► show WordListActivity
         └── Button "ABOUT" ────────► show AboutDialog
                  │
                  ▼
        [Execute bash -c via Runtime]
                  │
                  ▼
        [assets/ycc365-ghost.sh <IP>]
                  │
                  ▼
        [Affiche résultats dans TextView]
```

---

## 🎨 Design Patterns Utilisés

### Builder Pattern (ScanResult)

```python
@dataclass
class ScanResult:
    target: str
    open_ports: List[PortInfo] = field(default_factory=list)
    valid_credentials: List[CredentialTest] = field(default_factory=list)
    # ... autres phases
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)
```

### Strategy Pattern (Modules)

Chaque module (UsernameArsenal, CloudDomainMapper) implémente `.run()` :
- Interface implicite : charge wordlist → exécute → retourne hits
- Composition : GhostScanner aggregate les modules

### Factory Pattern (Wordlists)

```python
WORDLIST_PATH = Path(__file__).parent / "wordlists" / "..."

def _load_usernames(self) -> List[str]:
    if not self.WORDLIST_PATH.exists():
        return ["admin", "root", "user", "support"]  # Fallback
```

### Lazy Loading

Les wordlists ne sont chargées qu'à l'init du scanner, pas au moment de l'import module.

---

## 🔌 Points d'Extension

Pour ajouter un nouveau module (par exemple Module 8: BLE Scanner) :

1. Créer `scanner/ble.py` avec une classe `BLEScanner`
2. Implémenter `run(self) -> List[BLEDevice]`
3. Ajouter une phase dans `GhostScanner.run_full_scan()`
4. Documenter dans `CHANGELOG.md`

### API Stable

```python
from scanner import GhostScanner
from scanner.usernames import UsernameArsenal
from scanner.cloudmapper import CloudDomainMapper

# Usage direct
scanner = GhostScanner("192.168.1.100")
result = scanner.run_full_scan()

# Usage modulaire
ua = UsernameArsenal("192.168.1.100")
hits = ua.run(http_ports=[80, 443])

cm = CloudDomainMapper("192.168.1.100")
domains = cm.run()
```

---

## 🔒 Considérations Sécurité

### Isolation
- Pas de NDK ou libs externes = surface réduite
- Self-signed APK (pas de Play Services)
- Aucune télémétrie ou tracking

### Privacy
- Aucun data exfiltration
- 100% offline-friendly (sauf cloud mapper)
- Pas d'appel API tiers non documenté

### Reproduction
- Sources 100% open (MIT)
- Build déterministe via `build.sh`
- Keystore self-signed = reproducible local

---

## 📊 Métriques

| Métrique | Valeur |
|----------|--------|
| Lignes Python (core) | 356 |
| Lignes Java (Android) | 200 |
| Lignes Bash (Termux) | ~600 |
| Lignes Markdown (docs) | ~1500 |
| Taille APK | 16.9 KB |
| Ports scannés | 16 |
| Credentials testés | 23 × N ports |
| Paths RTSP | 21 |
| Usernames (v1.1) | 58 |
| Domaines cloud (v1.1) | 42 |
| Tests combinaison v1.1 | 1102+ |

---

## 🚀 Évolution Architecture

### v1.0.0 (Actuelle)
- 5 phases de scan
- APK Android signé
- Script Termux standalone

### v1.1.0 (Réelle)
- + Modules 4 (Username Arsenal)
- + Modules 5 (Cloud Domain Mapper)
- + 7 phases totales
- + Wiki GitHub

### v1.2.0 (Roadmap)
- + Frida integration (dynamic analysis)
- + Module GPS/location leakage
- + Multi-targets depuis CSV
- + PDF report generation

### v2.0.0 (Vision)
- + Kivy Python mobile (sans APK)
- + FastAPI backend + WebSocket
- + Docker self-hosted
- + CI/CD automatisé

---

**Signé Ghost1o1** 🏴‍☠️ — *Le squelette tient la maison*
