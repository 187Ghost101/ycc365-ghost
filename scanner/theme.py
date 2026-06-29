"""
YCC365 Ghost Scanner — Theme / Palette
Signé Ghost1o1 — Charte graphique centrale
"""

# ─── Couleurs ANSI 256 pour terminal ───
class GhostColors:
    GOLD = "\033[38;5;220m"     # #ffd60a — Titres & succès
    CYAN = "\033[38;5;39m"      # #4da6ff — Sous-titres
    RED  = "\033[38;5;196m"     # #ff3860 — Alertes critiques
    GREEN = "\033[38;5;46m"     # #2ecc71 — Validations OK
    GRAY = "\033[38;5;245m"     # #94a3b8 — Texte secondaire
    WHITE = "\033[38;5;255m"    # #ffffff

    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    REVERSE = "\033[7m"
    RESET = "\033[0m"

    # Background
    BG_DARK = "\033[48;5;236m"  # #0a0f1e
    BG_RED = "\033[48;5;196m"


PALETTE = {
    "gold":   "#ffd60a",
    "cyan":   "#4da6ff",
    "red":    "#ff3860",
    "gray":   "#94a3b8",
    "dark":   "#0a0f1e",
    "white":  "#e8edf5",
    "green":  "#2ecc71",
}


def banner() -> str:
    """ASCII art banner Ghost1o1."""
    return f"""{GhostColors.GOLD}{GhostColors.BOLD}
    ▓██▓▒░       ░▒▓██▓
     ▓█▓▒░ ░▒▓██▓▒░ ░▒▓█    ╔══════════════════════════════════╗
      █▒░ ░▓██▓▒░ ░▒▓█      ║  🏴‍☠️  YCC365 GHOST SCANNER  🏴‍☠️    ║
      ▓█▒░ ░▒░░░░░ ░▒▓█      ║                                  ║
       ▓█▒░░░░░░░░░░░▒▓█      ║  Signé Ghost1o1 — Pentest IoT   ║
        █▒░░░░░░░░░░░▒█       ║  Version 1.0.0                   ║
        ▓█▒░░░░░░░░░▒▓█       ╚══════════════════════════════════╝
         ▓██▒░░░░░▒██▓
          ░▒▓███▓▒░                                          {GhostColors.RESET}
"""


def print_banner() -> None:
    """Affiche le banner dans stdout."""
    print(banner())


def colored_section(title: str, char: str = "═") -> str:
    """Section heading colored Ghost1o1 style."""
    line = char * (len(title) + 4)
    return (
        f"\n{GhostColors.GOLD}{GhostColors.BOLD}{line}\n"
        f"  {title}  \n"
        f"{line}{GhostColors.RESET}\n"
    )


def ok(msg: str) -> str:
    return f"{GhostColors.GREEN}[OK]{GhostColors.RESET} {msg}"


def info(msg: str) -> str:
    return f"{GhostColors.CYAN}[*]{GhostColors.RESET} {msg}"


def warn(msg: str) -> str:
    return f"{GhostColors.GOLD}[!]{GhostColors.RESET} {msg}"


def error(msg: str) -> str:
    return f"{GhostColors.RED}{GhostColors.BOLD}[X]{GhostColors.RESET} {GhostColors.RED}{msg}{GhostColors.RESET}"


def critical(msg: str) -> str:
    return f"{GhostColors.RED}{GhostColors.BOLD}[CRITICAL]{GhostColors.RESET} {GhostColors.RED}{msg}{GhostColors.RESET}"
