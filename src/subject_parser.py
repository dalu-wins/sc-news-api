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


def get_version(subject: str) -> dict:
    """Extrahiert eine Version aus einem String."""
    # Full Version x.y.z
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", subject)
    if m:
        return {"major": int(m.group(1)), "minor": int(m.group(2)), "patch": int(m.group(3))}

    # Shortened x.y
    m = re.search(r"(\d+)\.(\d+)", subject)
    if m:
        return {"major": int(m.group(1)), "minor": int(m.group(2)), "patch": 0}

    # No version found
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

    url_b64 = base64.b64encode(url.encode("utf-8")).decode("utf-8")

    return {
        "sourceUrl": entry.get("url"),
        "url_b64": url_b64,
        "pinned": entry.get("pinned", False),
        "subject": subject,  # keep original subject
        "channel": channel.value,
        "wave": wave.value,
        "version": version,
        "build": build,
    }
