"""
YCC365 Ghost Scanner — Module 2: FirmwareMetadataExtractor
Signé Ghost1o1 — Adapté de OSIN CHAIN ImageDeepScan (Module #2)

Pour les caméras YCC365/Hipcam, l'analyse d'image devient :
- EXIF extraction de snapshots JPG
- Firmware header analysis (binwalk-style)
- Strings extraction depuis firmware.bin
- HTTP/RTSP banner fingerprinting
- Cloud response header forensic
- M3U8/manifest path disclosure
"""

import re
import subprocess
import socket
import urllib.request
import ssl
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class MetaFinding:
    """Résultat d'extraction de métadonnée."""
    source: str  # exif, firmware, banner, header
    field_name: str  # e.g. "GPS", "Firmware Version", "Server Header"
    value: str
    fingerprint: Optional[str] = None  # hash ou signature
    risk_potential: str = "info"  # info | low | medium | high
    cve_references: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict:
        return asdict(self)


class FirmwareMetadataExtractor:
    """
    Module 2 — FirmwareMetadataExtractor adapté aux firmwares caméra YCC365/Hipcam.

    Extrait les métadonnées techniques de :
    - Snapshots JPG (EXIF, GPS si activé, timestamps)
    - Firmware .bin (version, taille, compression type, URLs hardcodées)
    - Banner HTTP/RTSP (server fingerprinting)
    - Headers HTTPS cloud (subdomain enumeration via CST)
    - M3U8 manifests (chemins cloud)
    """

    USER_AGENTS = [
        "YCC365/3.0",
        "LookCam/2.0",
        "Hipcam/1.0",
        "Dalvik/2.1.0 (Linux; U; Android 9; SM-G960F)",
        "Mozilla/5.0 (Linux; Android 9; SM-G960F)",
    ]

    FIRMWARE_SIGNATURES = {
        b"UImage": "uImage (uboot)",
        b"CRAMFS": "CRAMFS filesystem",
        b"hsqs": "SquashFS (HiSilicon)",
        b"JFFS": "JFFS2 filesystem",
        b"Squashfs": "Squashfs filesystem",
        b"sdcc_": "HiSilicon SoC firmware",
        b"HiSilicon": "HiSilicon chip",
        b"XMEYE": "XMEYE firmware",
        b"YCC365": "YCC365 firmware",
        b"Hipcam": "Hipcam firmware",
        b"rootfs": "Linux rootfs",
        b"BusyBox": "BusyBox userspace",
    }

    FINGERPRINT_KEYS = {
        "Server": "Web Server",
        "X-Powered-By": "Framework",
        "WWW-Authenticate": "Auth Method",
        "Content-Type": "Response Type",
        "Set-Cookie": "Session Cookie",
        "Server: Hipcam": "Hipcam RTSP",
        "realm": "Auth Realm",
    }

    def __init__(self, target: str = "127.0.0.1", timeout: float = 5.0):
        self.target = target
        self.timeout = timeout
        self.findings: List[MetaFinding] = []

    # ─── HTTP Banner ───

    def _http_banner_grab(self, port: int = 80, scheme: str = "http") -> List[MetaFinding]:
        """Récupère headers HTTP/HTTPS complets."""
        results = []
        try:
            req = urllib.request.Request(
                f"{scheme}://{self.target}:{port}/",
                headers={"User-Agent": self.USER_AGENTS[0]},
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                headers = dict(r.headers)

                for key, value in headers.items():
                    risk = "info"
                    if key.lower() in ("x-powered-by", "server"):
                        if "hipcam" in value.lower() or "ycc365" in value.lower():
                            risk = "high"
                        elif "nginx" in value.lower() or "apache" in value.lower():
                            risk = "low"

                    results.append(MetaFinding(
                        source="http_banner",
                        field_name=f"{key}",
                        value=str(value)[:200],
                        risk_potential=risk,
                    ))
        except (urllib.error.URLError, urllib.error.HTTPError, OSError, ssl.SSLError):
            pass
        return results

    # ─── RTSP Banner ───

    def _rtsp_banner_grab(self, port: int = 554) -> List[MetaFinding]:
        """Banner grab RTSP pour fingerprinting."""
        results = []
        try:
            sock = socket.create_connection((self.target, port), timeout=self.timeout)
            sock.settimeout(self.timeout)
            sock.send(b"OPTIONS * RTSP/1.0\r\nCSeq: 1\r\nUser-Agent: YCC365-Ghost\r\n\r\n")
            response = b""
            while True:
                try:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    response += chunk
                    if b"\r\n\r\n" in response:
                        break
                except socket.timeout:
                    break
            sock.close()

            output = response.decode("utf-8", errors="ignore")

            for line in output.splitlines():
                if line.strip() and ":" in line:
                    key, _, value = line.partition(":")
                    results.append(MetaFinding(
                        source="rtsp_banner",
                        field_name=key.strip(),
                        value=value.strip()[:200],
                        risk_potential="high" if "hipcam" in value.lower() else "low",
                    ))

            # Server RTSP
            server_match = re.search(r"Server:\s*(.+)", output, re.IGNORECASE)
            if server_match:
                server = server_match.group(1).strip()
                risk = "high" if any(s in server.lower() for s in ["hipcam", "ycc365", "xmeye"]) else "low"
                results.append(MetaFinding(
                    source="rtsp_banner",
                    field_name="RTSP Server",
                    value=server,
                    risk_potential=risk,
                    notes="Server fingerprint → ciblage CVE précis",
                ))

        except (socket.timeout, ConnectionRefusedError, OSError):
            pass
        return results

    # ─── Firmware .bin Analysis (binwalk-style) ───

    def _firmware_analysis(self, firmware_url: str = None) -> List[MetaFinding]:
        """Analyse basique d'un firmware via binwalk."""
        results = []

        # Télécharger le firmware si URL fournie
        fw_path = Path("/tmp/ycc365_firmware_dump.bin")
        if firmware_url:
            try:
                urllib.request.urlretrieve(firmware_url, fw_path)
            except Exception:
                return results

        if not fw_path.exists():
            return results

        try:
            # Lire le binaire
            data = fw_path.read_bytes()

            # Recherche de signatures
            for signature, description in self.FIRMWARE_SIGNATURES.items():
                if signature in data:
                    offset = data.find(signature)
                    results.append(MetaFinding(
                        source="firmware",
                        field_name=f"Signature: {signature.decode('latin-1', errors='ignore')}",
                        value=f"{description} at offset 0x{offset:x}",
                        risk_potential="medium" if description == "HiSilicon chip" else "info",
                    ))

            # Extraction de strings (URLs, paths, IPs)
            strings_pattern = re.compile(rb"[\x20-\x7e]{6,}")
            interesting = []
            for match in strings_pattern.finditer(data[:1024 * 1024]):  # 1 MB max
                s = match.group().decode("latin-1", errors="ignore")
                if any(p in s for p in ["http://", "https://", ".cn", ".com", ".net", "/etc/", "/usr/"]):
                    if not any(skip in s.lower() for skip in ["google.com", "schema.org"]):
                        interesting.append(s)

            for s in interesting[:20]:
                risk = "high" if ".cn" in s.lower() else "medium"
                results.append(MetaFinding(
                    source="firmware",
                    field_name="Hardcoded URL/String",
                    value=s[:200],
                    risk_potential=risk,
                    notes="Trouvé dans firmware dump - peut révéler C2 backend ou paths internes",
                ))

        except (OSError, ValueError):
            pass
        finally:
            try:
                fw_path.unlink()
            except OSError:
                pass

        return results

    # ─── EXIF Snapshot ───

    def _snapshot_exif(self, snapshot_url: str = None) -> List[MetaFinding]:
        """Tente d'extraire EXIF d'un snapshot JPG."""
        results = []

        if not snapshot_url:
            # Tester quelques paths snapshot typiques
            for path in ["/snapshot.jpg", "/web/snap.jpg", "/img/snapshot.jpg", "/jpg/image.jpg"]:
                snapshot_url = f"http://{self.target}{path}"
                try:
                    req = urllib.request.Request(snapshot_url)
                    response = urllib.request.urlopen(req, timeout=self.timeout)
                    if response.status == 200 and "image" in response.headers.get("Content-Type", "").lower():
                        break
                except (urllib.error.URLError, OSError):
                    continue
            else:
                return results

        # Télécharger
        try:
            snap_path = Path(f"/tmp/ycc365_snap_{int(datetime.utcnow().timestamp())}.jpg")
            urllib.request.urlretrieve(snapshot_url, snap_path)

            # EXIF extraction (via exiftool si dispo, sinon regex basique)
            try:
                result = subprocess.run(
                    ["exiftool", str(snap_path)],
                    capture_output=True, timeout=self.timeout + 5,
                )
                output = result.stdout.decode("utf-8", errors="ignore")

                exif_lines = output.splitlines()
                for line in exif_lines[:30]:  # Top 30 entrées
                    if ":" in line:
                        key, _, value = line.partition(":")
                        key = key.strip()
                        value = value.strip()

                        risk = "info"
                        if key.lower() in ("gps latitude", "gps longitude", "gps position"):
                            risk = "high"
                            notes = "⚠️ GPS exposé dans snapshot - géolocalisation possible"
                        elif key.lower() in ("camera model name", "software"):
                            risk = "medium"
                            notes = "Infos caméra dans EXIF"
                        else:
                            notes = None

                        results.append(MetaFinding(
                            source="exif",
                            field_name=key,
                            value=value[:200],
                            risk_potential=risk,
                            notes=notes,
                        ))
            except (subprocess.TimeoutExpired, FileNotFoundError):
                # Pas d'exiftool - regex basique sur le JPG
                data = snap_path.read_bytes()

                exif_match = re.search(rb"\xff\xd8\xff\xe1(.*?)\xff\xd9", data, re.DOTALL)
                if exif_match:
                    exif_data = exif_match.group(1)
                    results.append(MetaFinding(
                        source="exif",
                        field_name="EXIF Block Found",
                        value=f"{len(exif_data)} bytes of EXIF data",
                        risk_potential="medium",
                        notes="EXIF détecté mais extraction complète nécessite exiftool",
                    ))

            snap_path.unlink(missing_ok=True)

        except Exception as e:
            results.append(MetaFinding(
                source="exif",
                field_name="Snapshot Error",
                value=str(e),
                risk_potential="info",
            ))

        return results

    # ─── Cloud Response Headers ───

    def _cloud_meta(self, cloud_domains: List[str]) -> List[MetaFinding]:
        """Analyse headers des domaines cloud mappés."""
        results = []
        for domain in cloud_domains[:5]:  # Top 5 pour éviter trop de bruit
            try:
                req = urllib.request.Request(
                    f"https://{domain}/",
                    headers={"User-Agent": "YCC365-Ghost/1.2"},
                )
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    headers = dict(r.headers)

                    for key, value in headers.items():
                        risk = "info"
                        if "x-powered-by" in key.lower():
                            risk = "medium"

                        results.append(MetaFinding(
                            source="cloud_headers",
                            field_name=f"[{domain}] {key}",
                            value=str(value)[:150],
                            risk_potential=risk,
                        ))

            except (urllib.error.URLError, OSError, ssl.SSLError):
                continue
        return results

    # ─── Run ───

    def run(self, cloud_domains: Optional[List[str]] = None) -> List[MetaFinding]:
        """Exécute Module 2."""
        print(f"\n═══ Module 2: FirmwareMetadataExtractor ═══")
        print(f"  [*] Cible: {self.target}")
        print(f"  [*] Extraction de métadonnées bannières + firmware + EXIF")

        self.findings = []

        # HTTP banner
        print(f"  [*] HTTP banner grab...")
        for port in (80, 8080, 34567):
            new = self._http_banner_grab(port, "http")
            self.findings.extend(new)

        # RTSP banner
        print(f"  [*] RTSP banner grab...")
        new = self._rtsp_banner_grab(554)
        self.findings.extend(new)

        # Firmware depuis URL standard
        print(f"  [*] Firmware dump check...")
        for url in [f"http://{self.target}/firmware.bin",
                    f"http://{self.target}/upgrade/firmware.bin",
                    f"http://{self.target}/update.bin"]:
            new = self._firmware_analysis(url)
            self.findings.extend(new)
            if any(f.field_name.startswith("Signature") for f in new):
                break  # OK on a un firmware

        # Snapshot EXIF
        print(f"  [*] Snapshot EXIF extraction...")
        new = self._snapshot_exif()
        self.findings.extend(new)

        # Cloud headers
        if cloud_domains:
            print(f"  [*] Cloud headers sur {len(cloud_domains)} domaines...")
            new = self._cloud_meta(cloud_domains)
            self.findings.extend(new)

        # Dedupe
        seen = set()
        unique = []
        for f in self.findings:
            key = (f.source, f.field_name, f.value)
            if key not in seen:
                seen.add(key)
                unique.append(f)
        self.findings = unique

        # Résumé
        high = [f for f in self.findings if f.risk_potential == "high"]
        medium = [f for f in self.findings if f.risk_potential == "medium"]
        print(f"\n  📊 {len(self.findings)} métadonnées extraites")
        print(f"     🔴 {len(high)} critiques")
        print(f"     🟡 {len(medium)} moyennes")
        print(f"     🟢 {len(self.findings) - len(high) - len(medium)} info")

        if high:
            print(f"\n  🚨 Trouvailles critiques:")
            for f in high[:5]:
                print(f"     • [{f.source}] {f.field_name}: {f.value[:80]}")

        return self.findings

    def stats(self) -> Dict:
        return {
            "module": "FirmwareMetadataExtractor (2)",
            "target": self.target,
            "total_findings": len(self.findings),
            "critical": sum(1 for f in self.findings if f.risk_potential == "high"),
            "medium": sum(1 for f in self.findings if f.risk_potential == "medium"),
            "info": sum(1 for f in self.findings if f.risk_potential == "info"),
            "sources": list(set(f.source for f in self.findings)),
        }
