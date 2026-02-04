import base64
import re
from enum import Enum


class Channel(Enum):
    Unknown = "Unknown"
    Preview = "Preview"
    Hotfix = "Hotfix"
    EPTU = "EPTU"
    PTU = "PTU"
    Live = "Live"


class Wave(Enum):
    Unknown = "Unknown"
    One = "Wave 1"
    Two = "Wave 2"
    Three = "Wave 3"
    Four = "Wave 4"
    AllBackers = "All Backers"


# ==============================
# 🔹 CHANNEL-PATTERNS
# ==============================

CHANNEL_PATTERNS = {
    Channel.Preview: [r"PREVIEW"],
    Channel.Hotfix: [r"HOTFIX"],
    Channel.EPTU: [r"\bEPTU\b", r"\bEVO\b", r"EVOCATI", r"EVOCATI\s*PTU", r"EVO\s*PTU"],
    Channel.PTU: [r"\bPTU\b"],
    Channel.Live: [r"\bLIVE\b"],
}

# ==============================
# 🔹 WAVE-PATTERNS
# ==============================

WAVE_PATTERNS = {
    Wave.One: [r"WAVE\s*1"],
    Wave.Two: [r"WAVE\s*2"],
    Wave.Three: [r"WAVE\s*3"],
    Wave.Four: [r"WAVE\s*4"],
    Wave.AllBackers: [r"ALL\s*BACKER", r"ALL\s*BACKERS", r"ALL\s*WAVE", r"ALL\s*WAVES"],
}


def get_channel(subject: str) -> Channel:
    s = subject.upper()
    for channel, patterns in CHANNEL_PATTERNS.items():
        for p in patterns:
            if re.search(p, s):
                return channel
    return Channel.Unknown


def get_wave(subject: str) -> Wave:
    s = subject.upper()
    for wave, patterns in WAVE_PATTERNS.items():
        for p in patterns:
            if re.search(p, s):
                return wave
    return Wave.Unknown


import re

def get_version(subject: str) -> dict:
    """Extracts a version and ignores dates."""    
    # Pattern erklärt: 
    # \b(?<!\.) -> Wortgrenze, kein Punkt davor
    # (\d+)\.(\d+)(?:\.(\d+))? -> x.y oder x.y.z
    # (?!\.\d{4}) -> Negativer Lookahead: Verhindert Treffer, wenn direkt danach .2026 (Jahr) folgt
    pattern = r"\b(?<!\.)(\d+)\.(\d+)(?:\.(\d+))?(?!\.\d{4})\b"
    
    matches = re.finditer(pattern, subject)
    
    for m in matches:
        major = int(m.group(1))
        minor = int(m.group(2))
        patch = int(m.group(3)) if m.group(3) else 0
        
        # Plausibilitätscheck: In Star Citizen sind Major-Versionen aktuell einstellig (z.B. 3 oder 4).
        # Jahre wie 2026 haben 4 Stellen. 
        if major < 1000: 
            return {"major": major, "minor": minor, "patch": patch}

    return {"major": 0, "minor": 0, "patch": 0}


def get_build(subject: str) -> str:
    """Extract buildnumber (min len 7)."""
    m = re.search(r"\d{7,}", subject)
    return m.group(0) if m else ""


def parse_patch_entry(entry: dict) -> dict:
    """
    Transforms a Raw-Thread-Object ({subject,url,pinned}) into a Patch-Object pased on the server.
    """
    subject = entry.get("subject", "")
    channel = get_channel(subject)
    wave = get_wave(subject)
    version = get_version(subject)
    build = get_build(subject)

    # provide base64-encoded URL for single thread fetching via API
    sourceUrl = entry.get("url")
    url_b64 = base64.b64encode(sourceUrl.encode("utf-8")).decode("utf-8")

    return {
        "sourceUrl": sourceUrl,
        "urlBase64": url_b64,
        "pinned": entry.get("pinned", False),
        "subject": subject,  # keep original subject
        "channel": channel.value,
        "wave": wave.value,
        "version": version,
        "build": build,
    }
