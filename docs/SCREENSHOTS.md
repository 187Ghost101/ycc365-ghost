# 📸 Screenshots — YCC365 Ghost

## Signé Ghost1o1 — Visuels UI

---

## 📱 APK Android — Capture 1 (Banner + Modules)

```
╔════════════════════════════════════╗
║ 🏴‍☠️  YCC365 GHOST SCANNER  🏴‍☠️     ║
║ Signé Ghost1o1 — IoT Pentest Kit ║
╠════════════════════════════════════╣
║                                    ║
║ 📦 MODULES INCLUS                  ║
║                                    ║
║ ✅ 16 ports YCC365 scannés         ║
║   (34567, 34599, 9527, 554…)       ║
║                                    ║
║ ✅ 23 couples credentials testés   ║
║   admin/admin, root/xmhdipc…       ║
║                                    ║
║ ✅ 21 URLs RTSP énumérées          ║
║   /onvif/streaming/channels/101   ║
║   /11, /12, /live/ch00_0…         ║
║                                    ║
║ ✅ Détection backdoor Telnet       ║
║ ✅ Scan ONVIF + dump device info   ║
║                                    ║
║ ⚠️ Usage légal uniquement ⚠️      ║
╚════════════════════════════════════╝
```

---

## 📱 APK Android — Capture 2 (Instructions)

```
╔════════════════════════════════════╗
║ 🚀 UTILISATION                     ║
╠════════════════════════════════════╣
║                                    ║
║ 1. Installer Termux (F-Droid)      ║
║ 2. Lancer Termux                   ║
║ 3. Exécuter :                      ║
║                                    ║
║    bash /sdcard/ycc365-ghost.sh    ║
║                                    ║
║ OU copier depuis l'APK vers :      ║
║ /data/data/com.termux/files/home/  ║
║                                    ║
╚════════════════════════════════════╝
```

---

## 🐚 Termux CLI — Capture (Banner + Menu)

```
$ bash ycc365-ghost.sh

    ▓██▓▒░       ░▒▓██▓
     ▓█▓▒░ ░▒▓██▓▒░ ░▒▓█      🏴‍☠️  YCC365 GHOST  🏴‍☠️
      █▒░ ░▓██▓▒░ ░▒▓█
      ▓█▒░ ░▒░░░░░ ░▒▓█         Signé Ghost1o1
       ▓█▒░░░░░░░░░░░▒▓█
        █▒░░░░░░░░░░░▒█         v1.0.0
        ▓█▒░░░░░░░░░▒▓█
         ▓██▒░░░░░▒██▓

═══════════════════════════════════════
📋 MENU PRINCIPAL
═══════════════════════════════════════
  [1] Scanner une IP spécifique
  [2] Découverte réseau local
  [3] Afficher wordlist credentials
  [4] Afficher paths RTSP
  [5] Aide détaillée
  [q] Quitter

Choix: _
```

---

## 🔍 Scan en Cours (Phase 1: Ports)

```
═══ Phase 1: Port Scan ═══

  [OPEN] 80     (HTTP admin)
  [OPEN] 443    (HTTPS)
  [OPEN] 554    (RTSP streaming)
  [OPEN] 9527   (TELNET BACKDOOR)  ← ⚠️
  [OPEN] 8899   (ONVIF)
  [OPEN] 34567  (YCC365 admin)
  [OPEN] 34599  (YCC365 login)

Total: 7 ports ouverts
```

---

## 🔍 Bruteforce Credentials (Phase 2)

```
═══ Phase 2: Bruteforce ═══

  [*] Test port 34567...
  [VALID] admin:12345 (HTTP 200)
  [VALID] admin:888888 (HTTP 200)
  [*] Test port 80...
  [VALID] user:user (HTTP 302 → /index.html)

⚠️  3 credentials valides trouvées
```

---

## 🚪 Backdoor Detection (Phase 4)

```
═══ Phase 4: Telnet Backdoor ═══

  [*] Test backdoor Telnet port 9527
  [*] Tentative root/xmhdipc...
  [CRITICAL] BACKDOOR TELNET ACTIF!
    Sortie: root@camera:/# ▮

🚨 TAKE OVER COMPLET — DEVICE COMPROMIS
```

---

## 📊 Résumé Final

```
════════════════════════════════════════════
📊 RÉSUMÉ
════════════════════════════════════════════
Cible           : 192.168.1.100
Ports ouverts   : 7 (80, 443, 554, 9527, 8899, 34567, 34599)
Credentials OK  : 3 (admin:12345, admin:888888, user:user)
Backdoor Telnet : ✓ ACTIF
ONVIF probe     : ✓ Manufacturer: HiSilicon
Risk score      : 🔴 9.8/10 CRITICAL

Rapport: /tmp/ycc365_192.168.1.100_20260629_143217.txt

════════════════════════════════════════════
  🏴‍☠️  Signé Ghost1o1  🏴‍☠️
════════════════════════════════════════════
```

---

## 🎨 Charte Ghost1o1

| Élément | Couleur | Hex |
|---------|---------|-----|
| Banner Skull | Gold | `#ffd60a` |
| Sous-titres | Cyan | `#4da6ff` |
| Alertes | Rouge | `#ff3860` |
| Succès | Vert | `#2ecc71` |
| Fond | Dark | `#0a0f1e` |

---

*Signé Ghost1o1 🏴‍☠️ — Screenshots v1.0*
