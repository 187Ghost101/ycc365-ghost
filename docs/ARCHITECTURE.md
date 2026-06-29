# 🏗️ Architecture Technique

## Signé Ghost1o1 — Diagramme & Stack

---

## 🎯 Vue d'Ensemble

```
┌────────────────────────────────────────────────────────────────┐
│                       UTILISATEUR                              │
│                (propriétaire caméra IoT)                       │
└─────────────┬─────────────────────────┬────────────────────────┘
              │                         │
              ▼                         ▼
    ┌──────────────────┐      ┌────────────────────┐
    │   APK Android    │      │   Termux + Bash    │
    │   Launcher       │      │   CLI Scanner      │
    │                  │      │                    │
    │  ┌────────────┐  │      │  ┌──────────────┐  │
    │  │ MainActivity│ │      │  │ ycc365-ghost │  │
    │  │  Java 8     │ │      │  │   .sh        │  │
    │  └─────┬───────┘  │      │  └──────┬───────┘  │
    │        │          │      │         │          │
    │  ┌─────▼───────┐  │      │  ┌──────▼───────┐  │
    │  │ assets/     │  │      │  │ Scanner Core │  │
    │  │ ycc365.sh   │  │      │  │  Python 3    │  │
    │  └─────────────┘  │      │  └──────────────┘  │
    └─────────┬────────┘      └──────────┬─────────┘
              │                          │
              └────────────┬─────────────┘
                           ▼
            ┌──────────────────────────────┐
            │      SCANNER CORE            │
            │      (logique métier)        │
            │                              │
            │  ┌────────────────────────┐  │
            │  │  Phase 1: PORT SCAN    │  │
            │  │  • 16 ports TCP        │  │
            │  │  • bash /dev/tcp       │  │
            │  └────────────────────────┘  │
            │                              │
            │  ┌────────────────────────┐  │
            │  │  Phase 2: BRUTEFORCE   │  │
            │  │  • 23 credentials      │  │
            │  │  • curl HTTP Basic     │  │
            │  └────────────────────────┘  │
            │                              │
            │  ┌────────────────────────┐  │
            │  │  Phase 3: RTSP TEST    │  │
            │  │  • 21 paths            │  │
            │  │  • curl DESCRIBE       │  │
            │  └────────────────────────┘  │
            │                              │
            │  ┌────────────────────────┐  │
            │  │  Phase 4: TELNET BD    │  │
            │  │  • root/xmhdipc        │  │
            │  │  • ncat interactif     │  │
            │  └────────────────────────┘  │
            │                              │
            │  ┌────────────────────────┐  │
            │  │  Phase 5: ONVIF        │  │
            │  │  • SOAP GetDeviceInfo  │  │
            │  └────────────────────────┘  │
            │                              │
            │  ┌────────────────────────┐  │
            │  │  REPORT GENERATOR      │  │
            │  │  • /tmp/ycc365_*.txt   │  │
            │  │  • Horodaté            │  │
            │  └────────────────────────┘  │
            └──────────────┬───────────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │  CAMÉRA YCC365   │
                  │  192.168.1.X     │
                  │  Ports 554/9527/ │
                  │  8899/34567      │
                  └──────────────────┘
```

---

## 📱 Stack Android (APK)

### Composants

| Élément | Détail |
|---------|--------|
| **Package** | `com.ghost1o1.ycc365` |
| **Activity** | `MainActivity` (200 lignes Java) |
| **Layout** | `ScrollView + LinearLayout` (programmatic, no XML) |
| **Theme** | `android:Theme.Material.NoActionBar.Fullscreen` |
| **min SDK** | 21 (Android 5.0 Lollipop) |
| **target SDK** | 33 (Android 13 Tiramisu) |
| **Permissions** | INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE |

### Pipeline Build APK

```
┌──────────────────────────────────────────────────────────┐
│  1. KEYTOOL                                              │
│     ↓                                                    │
│     Génère keystore RSA 2048 SHA384 (validité 10000j)    │
│     Alias: ghost1o1                                      │
│     Password: ghost101                                   │
└────────────────────────┬─────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│  2. JAVAC                                                │
│     ↓                                                    │
│     Compile MainActivity.java → .class                   │
│     Source: 1.8, Target: 1.8                             │
│     Bootclasspath: android.jar (API 33)                  │
└────────────────────────┬─────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│  3. D8 (Dexer)                                           │
│     ↓                                                    │
│     Convertit .class → classes.dex (Dalvik bytecode)     │
│     min-api: 21                                          │
│     lib: android.jar                                     │
└────────────────────────┬─────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│  4. AAPT (Android Asset Packaging Tool)                  │
│     ↓                                                    │
│     Compile: AndroidManifest.xml + res/ + assets/        │
│     Output: APK unsigned (sans classes.dex)              │
└────────────────────────┬─────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│  5. ZIP add classes.dex                                  │
│     ↓                                                    │
│     Injection du DEX dans l'APK                          │
└────────────────────────┬─────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│  6. ZIPALIGN                                             │
│     ↓                                                    │
│     Alignement 4-byte boundary pour optimisation OS      │
└────────────────────────┬─────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│  7. APKSIGNER                                            │
│     ↓                                                    │
│     Signature v1+v2+v3 avec keystore Ghost1o1           │
│     Output: APK final signé                              │
└──────────────────────────────────────────────────────────┘
```

### APK Final Structure

```
ycc365-ghost-1.0.0.apk
├── META-INF/
│   ├── GHOST1O1.SF       ← Signature file
│   ├── GHOST1O1.RSA      ← Certificat RSA
│   └── MANIFEST.MF       ← Manifest JAR
├── AndroidManifest.xml   ← Permissions + Activity
├── classes.dex           ← Dalvik bytecode (MainActivity)
├── resources.arsc        ← Ressources compilées
└── assets/
    └── ycc365-ghost.sh   ← Scanner CLI complet
```

---

## 🐚 Stack Termux (CLI)

### Composants

| Élément | Technologie | Version |
|---------|-------------|---------|
| Shell | Bash | 4.0+ |
| Réseau | ncat (nmap project) | latest |
| HTTP | curl | 7.74+ |
| Script | Python 3 | 3.10+ |

### Modules Bash

```bash
ycc365-ghost.sh (13 KB)
├── check_tools()           # Vérification dépendances
├── banner()                # ASCII art Ghost1o1
├── port_scan(target,port)  # TCP /dev/tcp
├── rtsp_check(target,port) # curl DESCRIBE
├── http_auth_test(...)     # curl Basic Auth
├── telnet_backdoor_check() # ncat root/xmhdipc
├── onvif_probe(target)     # curl SOAP
├── scan_target(target)     # Orchestrateur 5 phases
└── main()                  # Menu interactif
```

---

## 🎨 Charte Technique

### Palette ANSI (Terminal)

| Code | Hex | Usage |
|------|-----|-------|
| `\033[38;5;220m` | `#ffd60a` | Titres & succès |
| `\033[38;5;39m`  | `#4da6ff` | Sous-titres |
| `\033[38;5;196m` | `#ff3860` | Alertes critiques |
| `\033[38;5;245m` | `#94a3b8` | Texte secondaire |
| `\033[1m`        | **BOLD** | Emphase |
| `\033[2m`        | DIM | Texte faible |

### Palette AOSP (Android Java)

```java
// Dans MainActivity.java
Color.parseColor("#ffd60a")   // Gold
Color.parseColor("#4da6ff")   // Cyan
Color.parseColor("#ff3860")   // Red
Color.parseColor("#94a3b8")   // Gray
Color.parseColor("#0a0f1e")   // Dark BG
Color.parseColor("#e8edf5")   // Light FG
```

---

## 🔄 Flow d'Exécution

### Scénario: Scan d'une caméra cible

```
[START] main()
    │
    ├─→ banner()                    ← Affiche ASCII art
    │
    ├─→ check_tools()                ← Vérifie ncat/curl/python
    │
    ├─→ Menu interactif
    │   │
    │   └─→ Choix [1] → scan_target($IP)
    │       │
    │       ├─→ Phase 1: TCP scan 16 ports
    │       │   └─→ Liste ports ouverts
    │       │
    │       ├─→ Phase 2: HTTP bruteforce
    │       │   └─→ Pour chaque port HTTP ouvert:
    │       │       └─→ Test 23 credentials via curl
    │       │
    │       ├─→ Phase 3: RTSP detection
    │       │   └─→ DESCRIBE rtsp://IP:554/
    │       │       └─→ Test 21 paths
    │       │
    │       ├─→ Phase 4: Telnet backdoor
    │       │   └─→ ncat → root/xmhdipc attempt
    │       │       └─→ Si OK: shell root
    │       │
    │       └─→ Phase 5: ONVIF probe
    │           └─→ POST SOAP GetDeviceInformation
    │
    ├─→ Résumé + Rapport /tmp/ycc365_*_DATE.txt
    │
    └─→ [END]
```

---

## 🛡️ Considérations Sécurité

### Couches de Protection

1. **Chiffrement en transit** : SHA-256 sur signatures APK
2. **Permissions minimales** : INTERNET/WiFi only, pas de camera/micro/storage
3. **Pas de persistence** : Aucun fichier hors `/tmp/`
4. **Pas de beaconing** : Aucun trafic réseau sortant non-initié
5. **Code auditable** : Open source MIT, signature Ghost1o1

### Menaces Couvertes

- ✅ Device compromise via Telnet BD
- ✅ Stream video intercept (RTSP)
- ✅ Auth bypass (default creds)
- ✅ Info disclosure (ONVIF)
- ✅ QR code leakage (WiFi + device sharing)

### Menaces NON Couvertes

- ❌ Zero-day firmware exploit
- ❌ Side-channel attack (power/TEMPEST)
- ❌ Physical tampering (JTAG/UART)
- ❌ Crypto implementation flaws

---

## 📊 Métriques de Build

| Composant | Taille | Lignes |
|-----------|--------|--------|
| `MainActivity.java` | 8.5 KB | 200 |
| `AndroidManifest.xml` | 700 B | 30 |
| `res/values/*.xml` | 1.5 KB | 50 |
| `assets/ycc365-ghost.sh` | 13 KB | 600+ |
| `scanner/core.py` | 14 KB | 450 |
| `scanner/theme.py` | 4 KB | 150 |
| `README.md` | 16 KB | 600+ |
| **TOTAL** | **~57 KB** | **~2080** |

---

*Signé Ghost1o1 🏴‍☠️ — Architecture v1.0*
