"""
YCC365 Ghost Scanner — Python Package
Signé Ghost1o1 — IoT Pentest Toolkit v1.1.0

Point d'entrée principal du scanner:
    from scanner import GhostScanner, ScanResult
    scanner = GhostScanner(target="192.168.1.100")
    results = scanner.run_full_scan()

Modules additionnels (v1.1.0):
    from scanner.usernames import UsernameArsenal
    from scanner.cloudmapper import CloudDomainMapper
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

__version__ = "1.1.0"
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
