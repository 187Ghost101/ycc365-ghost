"""
YCC365 Ghost Scanner — Python Package
Signé Ghost1o1 — IoT Pentest Toolkit v1.2.0

Point d'entrée principal du scanner:
    from scanner import GhostScanner, ScanResult
    scanner = GhostScanner(target="192.168.1.100")
    results = scanner.run_full_scan()

Modules OSIN CHAIN adaptés (v1.2.0):
    Module 1: scanner.serialintel.DeviceSerialIntel
    Module 2: scanner.firmware_meta.FirmwareMetadataExtractor
    Module 4: scanner.usernames.UsernameArsenal
    Module 5: scanner.cloudmapper.CloudDomainMapper
"""

from .core import (
    GhostScanner,
    PortInfo,
    CredentialTest,
    RTSPPath,
    ScanResult,
    ScanPhase,
    Severity,
)
from .theme import (
    PALETTE,
    banner,
    print_banner,
    GhostColors,
)

__version__ = "1.2.0"
__author__ = "Ghost1o1"
__license__ = "MIT"

__all__ = [
    "GhostScanner",
    "PortInfo",
    "CredentialTest",
    "RTSPPath",
    "ScanResult",
    "ScanPhase",
    "Severity",
    "PALETTE",
    "banner",
    "print_banner",
    "GhostColors",
]
