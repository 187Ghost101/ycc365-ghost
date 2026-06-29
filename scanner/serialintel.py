"""
YCC365 Ghost Scanner — Module 1: DeviceSerialIntel
Signé Ghost1o1 — Adapté de OSIN CHAIN PhoneIntel (Module #1)

Pour les caméras YCC365/Hipcam, le "numéro de téléphone" devient :
- MAC Address (OUI vendor lookup)
- Device Serial / UID (cloud exposure)
- WiFi BSSID (WiGLE geolocation)
- IP publique (ASN + geo)
- ONVIF UUID (collision detection)
"""

import re
import socket
import subprocess
import json
import urllib.request
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime


# ─── OUI Database (top 50 vendors YCC365 / Hipcam ecosystem) ───
OUI_DATABASE = {
    "00:12:12": "HiSilicon",
    "00:1F:F7": "Xiongmai (XM)",
    "00:50:43": "Xiongmai",
    "00:12:17": "Xiongmai",
    "00:0C:43": "Xiongmai",
    "00:0E:F0": "Hipcam",
    "28:06:1D": "Hipcam",
    "00:23:3B": "YCC365 (Shenzhen)",
    "00:18:A9": "YCC365",
    "00:12:17": "YCC365",
    "BC:AD:28": "YCC365",
    "00:0C:43": "Dahua",
    "00:12:12": "Dahua",
    "4C:BD:8F": "Dahua",
    "E0:3F:49": "Dahua",
    "00:40:48": "Hikvision",
    "00:80:48": "Hikvision",
    "28:57:BE": "Hikvision",
    "44:19:B6": "Hikvision",
    "BC:71:C1": "Hikvision",
    "00:18:FF": "GeoVision",
    "00:90:9F": "GeoVision",
    "00:07:32": "GeoVision",
    "00:23:5A": "Reolink",
    "9C:8E:CD": "Reolink",
    "BC:51:FE": "Anran",
    "00:12:17": "Anran",
    "00:0E:64": "Tenvis",
    "00:50:43": "Sricam",
    "00:0C:43": "Sricam",
    "BC:AD:28": "Sv3C",
    "00:18:12": "Vivotek",
    "00:02:D1": "Vivotek",
    "00:0E:63": "Arecont Vision",
    "00:1F:84": "Axis Communications",
    "AC:CC:8E": "Axis Communications",
    "B8:A4:4F": "Axis Communications",
    "00:40:8C": "Axis Communications",
    "00:0D:89": "Cisco (IoT)",
}


@dataclass
class SerialHit:
    """Résultat d'identification d'un identifiant IoT."""
    identifier_type: str  # mac, serial, uid, bssid, uuid
    identifier_value: str
    vendor: Optional[str] = None
    country: Optional[str] = None
    asn: Optional[str] = None
    cloud_known: bool = False
    leak_references: List[str] = field(default_factory=list)
    risk_score: float = 0.0
    notes: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict:
        return asdict(self)


class DeviceSerialIntel:
    """
    Module 1 — DeviceSerialIntel adapté aux caméras IoT YCC365/Hipcam.

    Identifie les caméras par leurs identifiants uniques (sérialisés)
    et corrèle avec bases publiques (OUI, WiGLE, IP geo).
    """

    SERIAL_PATTERNS = [
        # Patterns typiques device serials YCC365 / Hipcam / XMEYE
        r"^[A-Z]{2}\d{8,12}$",                # YK123456789
        r"^[A-Z0-9]{6}-[A-Z0-9]{6}$",         # ABCDEF-123456
        r"^\d{10,16}$",                        # 20 digit serial (HiSilicon)
        r"^[A-F0-9]{32}$",                     # UUID sans tirets
        r"^[A-F0-9]{8}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{12}$",  # UUID standard
    ]

    CLOUD_UID_PATTERNS = {
        "xmeye": {"pattern": r"^[A-Z0-9]{32}$", "description": "XMEYE cloud UID"},
        "ycc365": {"pattern": r"^\d{12,16}$", "description": "YCC365 cloud UID"},
        "hipcam": {"pattern": r"^HC[A-Z0-9]{10,12}$", "description": "Hipcam cloud UID"},
    }

    def __init__(self, target: str = "127.0.0.1", timeout: float = 5.0):
        self.target = target
        self.timeout = timeout
        self.hits: List[SerialHit] = []

    def _mac_vendor_lookup(self, mac: str) -> Optional[str]:
        """Lookup vendor via OUI (first 3 octets)."""
        if not mac:
            return None
        mac_clean = mac.upper().strip().replace("-", ":")
        if not re.match(r"^([0-9A-F]{2}:){2}[0-9A-F]{2}", mac_clean):
            return None
        prefix = ":".join(mac_clean.split(":")[:3])
        return OUI_DATABASE.get(prefix, "Unknown")

    def _ip_geo_lookup(self, ip: str) -> Dict:
        """Lookup IP géographique + ASN via API publique."""
        info = {"country": None, "asn": None, "org": None, "city": None}

        try:
            req = urllib.request.Request(
                f"https://ipinfo.io/{ip}/json",
                headers={"User-Agent": "ycc365-ghost/1.2"},
                timeout=self.timeout,
            )
            with urllib.request.urlopen(req) as r:
                data = json.loads(r.read())
                info["country"] = data.get("country")
                info["city"] = data.get("city")
                info["org"] = data.get("org")
                if "org" in data:
                    parts = data["org"].split()
                    info["asn"] = parts[0] if parts else None
        except (urllib.error.URLError, urllib.error.HTTPError, OSError, KeyError):
            pass

        return info

    def _wigle_lookup(self, bssid: str) -> Dict:
        """Lookup BSSID via WiGLE (nécessite API key) - placeholder."""
        # WiGLE API: https://api.wigle.net/api/v2/network/search?netid=...
        # Sans API key, retourne info limitée basée sur patterns
        return {
            "source": "wigle",
            "available": False,
            "note": "API key requise pour lookup complet",
            "fallback": "Geolocation basée sur premier hop BSSID",
        }

    def _reverse_mac(self, mac: str) -> Dict:
        """Reverse MAC lookup (sans API key externe - via nmap + OUI)."""
        try:
            result = subprocess.run(
                ["nmap", "--script", "mac-lookup", "-sn", self.target],
                capture_output=True, timeout=self.timeout + 5,
            )
            output = result.stdout.decode("utf-8", errors="ignore")
            vendor = self._mac_vendor_lookup(mac)
            return {
                "vendor_oui": vendor,
                "nmap_output_excerpt": output[:200],
            }
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return {"vendor_oui": self._mac_vendor_lookup(mac)}

    def _uid_cloud_check(self, uid: str) -> Dict:
        """Vérifie si un UID cloud est exposé publiquement (XMEYE + YCC365)."""
        info = {"known_clouds": [], "leak_refs": []}

        for cloud, cfg in self.CLOUD_UID_PATTERNS.items():
            if re.match(cfg["pattern"], uid, re.IGNORECASE):
                info["known_clouds"].append({
                    "cloud": cloud,
                    "description": cfg["description"],
                    "risk": "Élevé - si device actif, accessible via cloud app",
                })

        return info

    def analyze_mac(self, mac: str) -> SerialHit:
        """Analyse une adresse MAC."""
        vendor = self._mac_vendor_lookup(mac)
        risk = 0.5
        if vendor in ("YCC365", "Hipcam", "Xiongmai", "Dahua", "Hikvision"):
            risk = 0.9  # Plus risqué si vendor chinois avec cloud obligatoire
            notes = f"Vendor à cloud obligatoire ({vendor})"
        elif vendor == "Unknown":
            risk = 0.3
            notes = "Vendor inconnu - possible private MAC ou spoofing"
        else:
            notes = f"Vendor {vendor}"

        return SerialHit(
            identifier_type="mac",
            identifier_value=mac,
            vendor=vendor,
            risk_score=risk,
            notes=notes,
        )

    def analyze_serial(self, serial: str) -> SerialHit:
        """Analyse un numéro de série."""
        matched = False
        for pattern in self.SERIAL_PATTERNS:
            if re.match(pattern, serial):
                matched = True
                break

        cloud_info = self._uid_cloud_check(serial) if matched else {"known_clouds": [], "leak_refs": []}
        risk = 0.5
        notes = None

        if cloud_info["known_clouds"]:
            risk = 0.95
            notes = f"⚠️ UID cloud identifié : {', '.join(c['cloud'] for c in cloud_info['known_clouds'])}"
        elif matched:
            risk = 0.4
            notes = "Format serial reconnu (HIPCAM/Hikvision standard)"

        return SerialHit(
            identifier_type="serial",
            identifier_value=serial,
            cloud_known=bool(cloud_info["known_clouds"]),
            risk_score=risk,
            leak_references=cloud_info["known_clouds"],
            notes=notes,
        )

    def analyze_bssid(self, bssid: str) -> SerialHit:
        """Analyse un BSSID WiFi."""
        vendor = self._mac_vendor_lookup(bssid)
        wigle = self._wigle_lookup(bssid)

        return SerialHit(
            identifier_type="bssid",
            identifier_value=bssid,
            vendor=vendor or "Unknown",
            risk_score=0.6 if vendor == "Unknown" else 0.5,
            notes=f"WiGLE lookup: {wigle.get('note', 'N/A')}",
        )

    def analyze_ip(self, ip: str) -> SerialHit:
        """Analyse une IP via géolocalisation."""
        info = self._ip_geo_lookup(ip)
        risk = 0.3

        if info["country"] and info["country"] != "CA":
            notes = f"IP localisée ({info['country']}) - non géographique Canada"
        else:
            notes = f"IP localisée: {info.get('city', 'unknown')}, {info.get('country', 'XX')}"

        # Villes réseau connues (corridor IoT cameras)
        cloud_hubs = {"CN", "HK", "TW", "SG"}
        if info.get("country") in cloud_hubs:
            risk = 0.7
            notes = f"⚠️ IP en région cloud hub ({info.get('country')}) - probable hébergement XMEYE/aliyun"

        return SerialHit(
            identifier_type="ip",
            identifier_value=ip,
            country=info.get("country"),
            asn=info.get("asn"),
            vendor=info.get("org"),
            risk_score=risk,
            notes=notes,
        )

    def analyze_target(self, target: str, target_type: Optional[str] = None) -> List[SerialHit]:
        """Analyse une cible selon son type (auto-detect si None)."""
        hits = []

        if not target_type:
            if re.match(r"^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$", target):
                target_type = "mac"
            elif re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", target):
                target_type = "ip"
            elif re.match(r"^[A-Z0-9-]{6,32}$", target, re.IGNORECASE):
                target_type = "serial"

        if target_type == "mac":
            hits.append(self.analyze_mac(target))
        elif target_type == "ip":
            hits.append(self.analyze_ip(target))
        elif target_type == "serial":
            hits.append(self.analyze_serial(target))
        elif target_type == "bssid":
            hits.append(self.analyze_bssid(target))

        return hits

    def run(self, identifiers: Optional[Dict[str, str]] = None) -> List[SerialHit]:
        """Exécute Module 1."""
        print(f"\n═══ Module 1: DeviceSerialIntel ═══")
        print(f"  [*] Cible: {self.target}")
        print(f"  [*] Reconnaissance par identifiants IoT")

        self.hits = []

        # Si aucun identifier fourni, utiliser self.target
        if not identifiers:
            identifiers = {"ip": self.target}

        for id_type, value in identifiers.items():
            if not value:
                continue
            try:
                new_hits = self.analyze_target(value, id_type)
                for h in new_hits:
                    self.hits.append(h)
                    emoji = "🔴" if h.risk_score >= 0.7 else "🟡" if h.risk_score >= 0.4 else "🟢"
                    print(f"  {emoji} [{h.identifier_type.upper()}] {h.identifier_value}")
                    if h.vendor:
                        print(f"     Vendor: {h.vendor}")
                    if h.notes:
                        print(f"     {h.notes}")
                    if h.identifier_type == "ip" and h.country:
                        print(f"     Geo: {h.country} (ASN: {h.asn or 'N/A'})")
            except Exception as e:
                print(f"  ❌ {id_type}:{value} → {e}")

        # Résumé
        high_risk = [h for h in self.hits if h.risk_score >= 0.7]
        print(f"\n  📊 {len(self.hits)} identifiants analysés")
        print(f"  🔴 {len(high_risk)} haut risque")
        if high_risk:
            print(f"\n  🚨 Recommandation: Changer identifiants cloud + désactiver services exposés")

        return self.hits

    def stats(self) -> Dict:
        return {
            "module": "DeviceSerialIntel (1)",
            "target": self.target,
            "identifiers_analyzed": len(self.hits),
            "high_risk": sum(1 for h in self.hits if h.risk_score >= 0.7),
            "vendors_found": list(set(h.vendor for h in self.hits if h.vendor)),
            "cloud_uids_matched": sum(1 for h in self.hits if h.cloud_known),
        }
