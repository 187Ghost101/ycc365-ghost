# 🏴‍☠️ YCC365 GHOST SCANNER — Wiki Technique

> Scanner d'audit IoT pour caméras YCC365 / Hipcam / XMEYE  
> Signé **Ghost1o1** — Pentest & Audit IoT

---

## 📚 Pages

### 🎯 Fondamentaux

- [🏛️ Architecture](Architecture) — Architecture technique du scanner
- [🎯 Attack-Surface](Attack-Surface) — Surface d'attaque complète YCC365/Hipcam
- [📋 Methodology](Methodology) — Méthodologie pentest reproductible
- [⚠️ Threat-Model](Threat-Model) — Modélisation STRIDE des menaces
- [🛡️ Defense-Recommendations](Defense-Recommendations) — Guide de remédiation complet

### 🧩 Modules & Vulns

- [🧩 Modules-Reference](Modules-Reference) — Référence des 7 modules du scanner
- [💀 CVE-Mapping](CVE-Mapping) — Référentiel CVEs YCC365/Hipcam/XMEYE
- [🌐 IoT-Camera-Threats](IoT-Camera-Threats) — Paysage mondial IoT

### 🛠️ Pratique

- [🧪 Testing-Guide](Testing-Guide) — Guide d'utilisation pas-à-pas
- [📊 Sample-Reports](Sample-Reports) — Exemples de rapports générés

---

## 🚀 Quickstart

```bash
# Clone
git clone https://github.com/187Ghost101/ycc365-ghost.git
cd ycc365-ghost

# Scan Python complet
python3 -m scanner.core 192.168.1.100

# APK Android (depuis Releases)
# https://github.com/187Ghost101/ycc365-ghost/releases

# Script Termux
bash assets/ycc365-ghost.sh 192.168.1.100
```

---

## 🎨 Charte Ghost1o1

| Couleur | Hex | Usage |
|---------|-----|-------|
| 🟡 Or | `#ffd60a` | Titres & succès critiques |
| 🔵 Bleu | `#4da6ff` | Sous-titres & informations |
| 🔴 Rouge | `#ff3860` | Alertes & vulnérabilités |
| ⚫ Fond | `#0a0f1e` | Background dark theme |
| ⚪ Gris | `#94a3b8` | Texte secondaire |
| 🟢 Vert | `#10b981` | Confirmations & succès |

---

## ⚖️ Disclaimer Légal

**Cet outil est fourni UNIQUEMENT pour :**
- Tests sur vos propres équipements
- Audits autorisés avec permission écrite
- Recherche en sécurité dans un cadre légal
- Éducation en cybersécurité

**Toute utilisation sur des systèmes tiers sans autorisation est ILLÉGALE** (CFAA, Computer Misuse Act UK, Art. 323-1 CP France, équivalents internationaux).

---

**Signé Ghost1o1** 🏴‍☠️ — *Les pièces du puzzle s'assemblent*
