# 🏴‍☠️ YCC365 Ghost Scanner — F-Droid Submission Guide

> **Signé Ghost1o1** — How to publish the scanner as an alternative on F-Droid

---

## 📖 À propos de F-Droid

F-Droid est un repository open-source d'applications Android. Contrairement à Google Play Store, **100% des apps sont :**
- Open source (vérifié)
- Sans pub ni tracking
- Sans dépendance propriétaire
- Signées avec les clés F-Droid (pas par le vendor)
- Buildés sur l'infra F-Droid (reproductible)

---

## 🎯 Pourquoi Publier sur F-Droid ?

| Avantage | Bénéfice |
|----------|----------|
| Visibilité | 2M+ downloads mensuels sur le store F-Droid |
| Trust | Apps vérifiées par F-Droid maintainers |
| Privacy | Pas de tracking, pas de compte requis |
| Plateforme | Aligné avec les valeurs du projet (privacy + sécurité) |
| Alternative | Canal de distribution hors Google Play |

---

## 📂 Fichiers Préparés (dans ce dossier)

```
fdroid/
├── metadata/com.ghost1o1.ycc365.yml  ← Metadata F-Droid standard
├── build.gradle                     ← Configuration Gradle pour build F-Droid
├── src/                             ← Code source Android (à copier depuis src/)
└── SUBMIT.md                        ← Ce fichier
```

---

## 🔧 Processus de Soumission

### Étape 1 : Vérifier la Conformité Source

F-Droid impose des règles strictes :

```
✅ License MIT ou compatible — OK (LICENSE présent)
✅ Code source entièrement disponible
✅ Pas de dépendances propriétaires (Google Play, Firebase, etc.)
✅ Build reproductible via Gradle
✅ Pas de crashlytics / analytics
✅ App fonctionne sans Google Play Services
```

### Étape 2 : Fork fdroiddata (GitLab)

```bash
# F-Droid est sur GitLab, pas GitHub
# 1. Créer compte GitLab: https://gitlab.com/users/sign_up
# 2. Fork le repo fdroiddata:
#    https://gitlab.com/fdroid/fdroiddata/-/forks
# 3. Clone votre fork
git clone https://gitlab.com/<votre-username>/fdroiddata.git
cd fdroiddata
```

### Étape 3 : Ajouter le Metadata

```bash
# Copier le metadata.yml dans la structure standard
mkdir -p metadata
cp /path/to/ycc365-ghost/fdroid/metadata/com.ghost1o1.ycc365.yml \
   metadata/

# Vérifier que la syntaxe est correcte
fdroid readmeta --pretty
```

### Étape 4 : Tester le Build Localement

```bash
# F-Droid utilise `fdroidserver` pour builder
# Installer fdroidserver
pip install fdroidserver

# Build l'APK
fdroid build com.ghost1o1.ycc365:11
# → Output: build/com.ghost1o1.ycc365_11.apk
```

### Étape 5 : Vérifications Qualité

```bash
# Lint checks
fdroid lint com.ghost1o1.ycc365
fdroid check com.ghost1o1.ycc365

# Doit retourner 0
```

### Étape 6 : Soumettre le Merge Request

```bash
# Pousser la branche
git add metadata/com.ghost1o1.ycc365.yml
git commit -m "New app: YCC365 Ghost Scanner 1.1.0

*IoT security audit scanner for YCC365/Hipcam/XMEYE cameras.
Self-signed APK, no Google Play Services dependencies.
MIT licensed, 100% open source.*

Signed-off-by: Ghost1o1 <ghost1o1@ghost-sec.ca>"
git push origin main

# Créer le MR sur GitLab vers fdroiddata
# → https://gitlab.com/fdroid/fdroiddata/-/merge_requests/new
```

---

## ⏰ Délai de Review

| Scénario | Délai |
|----------|-------|
| App clean, no concerns | 1-2 semaines |
| Premier merge (besoin 2 maintainer approval) | 2-4 semaines |
| Demande de clarifications | Variable (1-2 iter) |
| Refus (rare) | N/A |

**Notre cas** (security scanner avec disclaimer légal) :
- Probablement OK
- Review rapide si `noSourceSince` ou `AntiFeatures` correctement configurés
- F-Droid aime les apps sécurité mais veut :
  - Avertissement légal clair
  - Pas d'output sans confirmation utilisateur
  - Pas de payload offensif

Notre APK a déjà tout ça → acceptance probable.

---

## ⚠️ Considérations Spéciales (Security Scanner)

F-Droid a des directives spécifiques pour les apps de sécurité :

### AntiFeatures possibles

```yaml
# Si l'app contient des "anti-features", il faut le déclarer

AntiFeatures:
  - NonFreeNet    # Si l'app fait des requêtes non-libres
  - Tracking      # Si tracking (pas notre cas)
```

Notre cas :
- Pas de tracking
- Requêtes HTTP standards (curl, RTSP, ONVIF)
- Pas de dépendance propriétaire
- → Pas d'`AntiFeatures` normalement

### Vérification de Sécurité Renforcée

```yaml
# Si F-Droid maintient considère notre app comme "security tool"
# Ils peuvent demander:
# 1. Code review approfondi
# 2. Justification fonctionnelle
# 3. Preuve que pas d'exploit payload
# 4. Disclaimers visibles

# Notre APK contient déjà tout:
# - Avertissement dans le launcher Activity
# - Pas d'exploit autonome
# - Code source 100% Java simple
```

---

## 🔧 Problèmes Courants

### "sdkmanager not found" / Android SDK manquant

F-Droid runners ont l'SDK installé automatiquement. Pas nécessaire de setup local.

### "License non-standard"

Notre LICENSE = MIT (standard). Devrait fonctionner.

### "No versionCode"

✓ versionCode 11 dans metadata.yml

### "Missing build.yml keys"

Vérifier la syntaxe avec `fdroid readmeta --pretty`.

### "Build failed reproducibly"

```bash
# F-Droid vérifie que les builds sont reproductibles
# Si votre build local diffère de leur infra :
# 1. Vérifier $SOURCE_DATE_EPOCH
# 2. Pas de timestamps dans le build
# 3. Gradle version pinned
```

---

## 📚 Liens Utiles

### F-Droid Official Resources

- **Documentation** : https://f-droid.org/docs/
- **Inclusion Howto** : https://f-droid.org/docs/Inclusion_Howto/
- **metadata.yml schema** : https://f-droid.org/docs/Build_Metadata_Reference/
- **GitLab** : https://gitlab.com/fdroid/fdroiddata

### Submission Forum

- **Forum** : https://forum.f-droid.org/
- **Matrix channel** : #fdroid-dev:matrix.org
- **Discourse** : https://discourse.f-droid.org/

### Test F-Droid Localement

- **Docker image** : https://hub.docker.com/r/fdroid/fdroidserver
```bash
docker run -it -v $(pwd):/repo fdroid/fdroidserver build com.ghost1o1.ycc365
```

---

## ✅ Checklist Finale

```
[ ] Fork fdroiddata sur GitLab
[ ] Copier metadata.yml
[ ] Configurer build.gradle dans le repo principal
[ ] Build local avec fdroidserver
[ ] Lint check passing
[ ] MR créé vers fdroiddata
[ ] Attendre review (1-4 semaines)
[ ] App publiée sur F-Droid 🏆
```

---

## 💰 Alternative : IzzyOnDroid

Si F-Droid est trop strict ou lent, **IzzyOnDroid** est une alternative :

- https://gitlab.com/IzzyOnDroid
- Plus rapide à accepter (1-3 jours)
- Même qualité minimale
- Moins de downloads mais plus agile

---

**Signé Ghost1o1** 🏴‍☠️ — *F-Droid, c'est la Bible de l'open source Android*
