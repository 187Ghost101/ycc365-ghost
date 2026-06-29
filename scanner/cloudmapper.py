"""
YCC365 Ghost Scanner — Module 5: Cloud Domain Mapper
Signé Ghost1o1 — Adapté de OSIN CHAIN DomainMapper

Cartographie les domaines cloud que contacte une caméra YCC365/Hipcam.
- Énumère les domaines XMEYE, YCC365, LookCam connus
- Résout DNS (A, AAAA)
- Test connectivité HTTP/HTTPS
- Banner grab (Server header)
- Récupère certificat SSL/TLS
"""

import socket
import subprocess
import ssl
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class DomainInfo:
    """Résultat de mapping pour un domaine."""
    domain: str
    resolved_ips: List[str] = field(default_factory=list)
    has_http: bool = False
    has_https: bool = False
    http_banner: Optional[str] = None
    http_code: Optional[int] = None
    https_cert_cn: Optional[str] = None
    https_cert_issuer: Optional[str] = None
    https_cert_expiry: Optional[str] = None
    https_tls_version: Optional[str] = None
    cloud_provider: Optional[str] = None
    reachable: bool = False
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict:
        return asdict(self)


class CloudDomainMapper:
    """
    Module 5 — DomainMapper adapté aux caméras IoT YCC365/Hipcam.

    Énumère les domaines cloud connus (XMEYE, YCC365, LookCam, etc.),
    résout leurs IPs, songe leur connectivité HTTP/HTTPS,
    extrait les bannières, et inspecte les certificats SSL.
    """

    WORDLIST_PATH = Path(__file__).parent / "wordlists" / "cloud_domains.txt"

    CLOUD_PROVIDERS = {
        "aliyun": ["aliyun.com", "aliyuncs.com"],
        "tencent": ["qcloud.com", "myqcloud.com"],
        "aws": ["amazonaws.com", "cloudfront.net"],
        "akamai": ["akamaized.net", "akamai.net"],
        "azure": ["azurewebsites.net", "cloudapp.net"],
    }

    def __init__(self, target: str = "127.0.0.1", timeout: float = 5.0):
        self.target = target
        self.timeout = timeout
        self.domains: List[str] = self._load_domains()
        self.results: List[DomainInfo] = []

    def _load_domains(self) -> List[str]:
        if not self.WORDLIST_PATH.exists():
            return [
                "xmeye.net", "ycc365.com", "lookcam.live",
                "api.xmeye.net", "cloud.xmeye.net",
            ]

        lines = []
        for line in self.WORDLIST_PATH.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            lines.append(line)
        return lines

    def _detect_cloud_provider(self, domain: str) -> Optional[str]:
        for provider, patterns in self.CLOUD_PROVIDERS.items():
            for pattern in patterns:
                if domain.endswith(pattern):
                    return provider
        return None

    def _resolve_dns(self, domain: str) -> List[str]:
        ips = []
        try:
            addrs = socket.getaddrinfo(domain, None, socket.AF_INET)
            ips.extend([a[4][0] for a in addrs if a[4][0] not in ips])
        except (socket.gaierror, OSError):
            pass

        try:
            addrs = socket.getaddrinfo(domain, None, socket.AF_INET6)
            ips.extend([a[4][0] for a in addrs if a[4][0] not in ips])
        except (socket.gaierror, OSError):
            pass

        return ips

    def _http_check(self, domain: str, scheme: str = "http") -> tuple:
        try:
            result = subprocess.run(
                ["curl", "-s", "-m", str(int(self.timeout)),
                 "-o", "/dev/null", "-D", "-",
                 f"{scheme}://{domain}"],
                capture_output=True,
                timeout=self.timeout + 2,
            )
            output = result.stdout.decode("utf-8", errors="ignore")

            server = None
            code = 0
            for line in output.splitlines():
                if line.lower().startswith("server:"):
                    server = line.split(":", 1)[1].strip()
                if line.startswith("HTTP/"):
                    try:
                        parts = line.split()
                        if len(parts) >= 2:
                            code = int(parts[1])
                    except (ValueError, IndexError):
                        pass

            reachable = result.returncode == 0 and bool(output)
            return reachable, server, code
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return False, None, 0

    def _https_cert_info(self, domain: str) -> Dict:
        info = {
            "cn": None,
            "issuer": None,
            "expiry": None,
            "tls_version": None,
        }

        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    info["tls_version"] = ssock.version()

                    subject = dict(x[0] for x in cert.get("subject", []))
                    info["cn"] = subject.get("commonName")

                    issuer = dict(x[0] for x in cert.get("issuer", []))
                    info["issuer"] = issuer.get("commonName")

                    info["expiry"] = cert.get("notAfter")
        except (socket.gaierror, socket.timeout, OSError, ssl.SSLError) as e:
            info["error"] = str(e)

        return info

    def _probe_domain(self, domain: str) -> DomainInfo:
        info = DomainInfo(domain=domain)
        info.cloud_provider = self._detect_cloud_provider(domain)

        info.resolved_ips = self._resolve_dns(domain)
        if not info.resolved_ips:
            info.error = "DNS resolution failed"
            return info

        http_ok, http_banner, http_code = self._http_check(domain, "http")
        info.has_http = http_ok
        info.http_banner = http_banner
        info.http_code = http_code

        try:
            https_ok, _, https_code = self._http_check(domain, "https")
            info.has_https = https_ok
            if https_ok:
                cert = self._https_cert_info(domain)
                info.https_cert_cn = cert["cn"]
                info.https_cert_issuer = cert["issuer"]
                info.https_cert_expiry = cert["expiry"]
                info.https_tls_version = cert["tls_version"]
        except Exception as e:
            info.error = f"HTTPS probe failed: {e}"

        info.reachable = info.has_http or info.has_https
        return info

    def run(self) -> List[DomainInfo]:
        print(f"\n═══ Module 5: Cloud Domain Mapper ═══")
        print(f"  [*] {len(self.domains)} domaines à cartographier")
        print(f"  [*] Cible contexte caméra: {self.target}\n")

        self.results = []

        for idx, domain in enumerate(self.domains, 1):
            print(f"  [{idx:2}/{len(self.domains)}] {domain}...", end=" ", flush=True)
            try:
                info = self._probe_domain(domain)
                self.results.append(info)

                if info.resolved_ips:
                    status = f"✅ {len(info.resolved_ips)} IPs"
                    if info.has_https:
                        status += " +TLS"
                    elif info.has_http:
                        status += " +HTTP"
                    if info.cloud_provider:
                        status += f" ({info.cloud_provider})"
                    print(status)
                else:
                    print(f"❌ {info.error or 'unresolved'}")

            except Exception as e:
                print(f"❌ {e}")
                self.results.append(DomainInfo(domain=domain, error=str(e)))

        # Résumé
        reachable = [r for r in self.results if r.reachable]
        https_ok = [r for r in self.results if r.has_https]
        with_certs = [r for r in self.results if r.https_cert_cn]

        print(f"\n  ✅ {len(reachable)}/{len(self.domains)} domaines accessibles")
        print(f"  🔒 {len(https_ok)} avec HTTPS actif")
        print(f"  📜 {len(with_certs)} certificats SSL valides")

        return self.results

    def stats(self) -> Dict:
        return {
            "module": "Cloud Domain Mapper (5)",
            "domains_loaded": len(self.domains),
            "domains_probed": len(self.results),
            "reachable": sum(1 for r in self.results if r.reachable),
            "https_enabled": sum(1 for r in self.results if r.has_https),
            "with_cert": sum(1 for r in self.results if r.https_cert_cn),
            "cloud_providers_found": list(set(
                r.cloud_provider for r in self.results
                if r.cloud_provider
            )),
        }
