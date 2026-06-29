# 🛡️ Politique de Sécurité

## Signé Ghost1o1 — Divulgation Responsable

---

## 🎯 Versions Supportées

| Version | Supportée | Statut |
|---------|-----------|--------|
| 1.0.0   | ✅        | Stable |
| < 1.0.0 | ❌        | Non supportée |

---

## 🚨 Signaler une Vulnérabilité

**⚠️ Ce projet est lui-même un outil de test d'intrusion.**

Les vulnérabilités **dans le code de l'outil** doivent être signalées à :

📧 **Email** : `security@ghost1o1.dev` (placeholder)

### 🔐 Processus de Divulgation

1. **Ne PAS** ouvrir d'issue publique pour les bugs critiques
2. **Email chiffré** (PGP key à publier bientôt)
3. **Attendre** un accusé de réception sous 48h
4. **Coordination** sur le fix + CVE assignation
5. **Disclosure publique** 90 jours après le fix

### 📋 Informations à Fournir

- [ ] Description technique détaillée
- [ ] Étapes de reproduction (PoC)
- [ ] Version(s) affectée(s)
- [ ] Impact potentiel (CVSS v3.1)
- [ ] Environnement (OS, device, etc.)
- [ ] Logs / crash dumps / screenshots

---

## 🎯 Vulnérabilités Connexes (Hors Scope)

Ce projet référence des vulnérabilités dans des produits tiers :

| Produit | CVE | Statut |
|---------|-----|--------|
| YCC365 Plus | Multiples | Voir `docs/ATTACK_SURFACE.md` |
| Hipcam SDK | CVE-2017-16919 | Patché par vendor (2023) |
| HiSilicon firmware | CVE-2020-9525 | Patché (2021) |
| Hikvision | CVE-2021-36260 | Patché (2021) |

**Pour signaler une faille dans ces produits**, contactez directement les vendors.

---

## 🔒 Bonnes Pratiques Utilisateur

Si tu utilises ce scanner :

1. ✅ **Documente** chaque scan (qui, quand, pourquoi)
2. ✅ **Obtiens** une autorisation écrite si tiers
3. ✅ **Limite** le scope à tes propres IPs
4. ✅ **Supprime** les credentials trouvés après usage
5. ✅ **Divulgue** responsablement au vendor

---

## 🏴‍☠️ Engagement Ghost1o1

- ✅ Pas de backdoor dans cet outil
- ✅ Code auditable (MIT License)
- ✅ Aucun beacon / télémétrie / tracking
- ✅ Signé numériquement (keystore Ghost1o1)
- ✅ Disclosure transparente

---

*Signé Ghost1o1 🏴‍☠️ — Juin 2026*
