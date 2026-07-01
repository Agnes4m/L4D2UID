STEAM_BASE = 76561197960265728


def to_steam64(steam32: str) -> str:
    """STEAM_0:1:220052419 -> 76561198400370567"""
    parts = steam32.split(":")
    return str(STEAM_BASE + (int(parts[2]) * 2) + int(parts[1]))


def to_steam32(steam64: str) -> str:
    """76561198400370567 -> STEAM_0:1:220052419"""
    z = int(steam64) - STEAM_BASE
    return f"STEAM_0:{z % 2}:{z // 2}"
