"""Emoji -> Lucide line icon (ISC license). Used by build.py to replace every emoji.

Icons are vendored in ./icons/*.svg (copied from lucide-static) so builds are offline.
Unmapped emoji in running text are removed; in icon slots they fall back to DEFAULT.
"""
import re
from pathlib import Path

ICON_DIR = Path(__file__).parent / "icons"
DEFAULT = "sparkles"

MAP = {
    "🎯": "target", "👉": "arrow-right", "✅": "circle-check", "🚫": "ban", "📅": "calendar", "💬": "message-circle",
    "📝": "notebook-pen", "⚖️": "scale", "✍️": "pen-line", "🧰": "briefcase", "⚠️": "triangle-alert", "⏱️": "timer",
    "🚩": "flag", "💸": "banknote", "📋": "clipboard-list", "📄": "file-text", "📧": "mail", "💡": "lightbulb",
    "🙋": "hand", "🔁": "repeat", "📊": "chart-column", "⏰": "alarm-clock", "🗣️": "megaphone", "🌱": "sprout",
    "🎨": "palette", "🌐": "globe", "✉️": "mail", "🔍": "search", "🔎": "search", "📁": "folder", "🗂️": "folders",
    "❓": "circle-help", "📥": "inbox", "🏢": "building-2", "📚": "library", "❌": "circle-x", "🔐": "lock-keyhole",
    "🧾": "receipt", "💻": "laptop", "🤝": "handshake", "🕐": "clock", "🔗": "link", "🌙": "moon", "⚡": "zap",
    "🛠️": "wrench", "🔄": "refresh-cw", "🧱": "blocks", "🧠": "brain", "🌏": "earth", "📈": "trending-up",
    "🎓": "graduation-cap", "👤": "user", "📱": "smartphone", "🎥": "video", "🗓️": "calendar-days", "📌": "pin",
    "📨": "send", "🧩": "puzzle", "💵": "banknote", "⏳": "hourglass", "📐": "ruler", "🏷️": "tag", "☕": "coffee",
    "✈️": "plane", "👀": "eye", "⭐": "star", "🧪": "flask-conical", "🧭": "compass", "🪟": "app-window",
    "📆": "calendar-range", "💼": "briefcase-business", "🪜": "trending-up", "🧑‍💻": "laptop", "➕": "plus",
    "☀️": "sun", "🔴": "circle-alert", "🖥️": "monitor", "🧑‍💼": "user-round", "🤖": "bot", "😴": "bed",
    "🗒️": "sticky-note", "🧮": "calculator", "🏛️": "landmark", "✂️": "scissors", "🛡️": "shield-check",
    "🏆": "trophy", "🚀": "rocket", "🗺️": "map", "🔒": "lock", "🎭": "drama", "🔢": "hash", "🪪": "id-card",
    "🏠": "house", "🔋": "battery-charging", "🆘": "life-buoy", "📉": "trending-down", "🚨": "siren", "🔑": "key-round",
    "🏦": "landmark", "📒": "notebook", "👋": "hand", "📶": "wifi", "💪": "dumbbell", "🎬": "clapperboard",
    "🙅": "ban", "😎": "smile", "🔵": "circle", "🟢": "circle-check", "🟡": "circle-dot", "🆓": "gift", "🏅": "medal",
    "⬇️": "arrow-down", "💾": "save", "📤": "upload", "⌨️": "keyboard", "🗑️": "trash-2", "➡️": "arrow-right",
    "✋": "hand", "📦": "package", "🗞️": "newspaper", "⚙️": "settings", "🤫": "volume-x", "🚧": "construction",
    "💱": "arrow-left-right", "🎉": "party-popper", "🔭": "telescope", "🏃": "footprints", "👨‍👩‍👧": "users",
    "👍": "thumbs-up", "👎": "thumbs-down", "✨": "sparkles", "🛑": "octagon-x", "🗃️": "archive", "🙏": "heart-handshake",
    "🤐": "volume-x", "🍽️": "utensils", "📵": "phone-off", "💙": "heart", "👥": "users", "🛒": "shopping-cart",
    "🎧": "headphones", "💳": "credit-card", "📜": "scroll-text", "💯": "badge-check", "🏨": "hotel",
    "😊": "smile", "🙂": "smile", "🤗": "smile", "😌": "smile", "📖": "book-open", "☁️": "cloud", "💎": "gem",
    "🚦": "traffic-cone", "🐷": "piggy-bank", "🏥": "hospital", "🏋️": "dumbbell", "🎂": "cake", "🧹": "brush-cleaning",
    "🛟": "life-buoy", "🗄️": "archive", "🏪": "store", "🎁": "gift", "🐢": "turtle", "🚪": "door-open", "🔥": "flame",
    "🛏️": "bed", "🛌": "bed", "🪑": "armchair", "🚶": "footprints", "🏖️": "palmtree", "🥤": "cup-soda", "⏲️": "timer",
    "📢": "megaphone", "👮": "shield", "📸": "camera", "📷": "camera", "👔": "shirt", "🌟": "star", "🌳": "trees",
    "📍": "map-pin", "🔧": "wrench", "❗": "circle-alert", "🕰️": "clock", "🌍": "earth", "🏧": "credit-card",
    "🔔": "bell", "🔕": "bell-off", "🌤️": "cloud-sun", "😷": "thermometer", "❤️": "heart", "🩺": "stethoscope",
    "🧳": "luggage", "💺": "armchair", "🚕": "car-taxi-front", "🛂": "id-card", "📲": "smartphone", "📞": "phone",
    "🔀": "shuffle", "🧗": "mountain", "🔌": "plug", "🎤": "mic", "💌": "mail-open", "🆚": "scale", "⬅️": "arrow-left",
    "🖱️": "mouse-pointer", "📏": "ruler", "✏️": "pencil", "🖐️": "hand", "☁": "cloud", "🔮": "eye", "🎚️": "sliders-horizontal",
    "🍜": "soup", "🍳": "cooking-pot", "🎰": "dices", "🫀": "heart-pulse", "🧺": "shopping-basket", "🎣": "fish",
    "📇": "contact", "🧑": "user", "👩‍💻": "laptop", "🇵🇭": "map-pin", "🇨🇦": "map-pin",
}

EMOJI_RE = re.compile(
    r"(?:[\U0001F1E6-\U0001F1FF]{2})|"
    r"(?:[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\u2300-\u23FF\u2190-\u21FF\u2934\u2935\u3030\u303D\u3297\u3299\u00A9\u00AE\u203C\u2049\u2122\u2139]"
    r"[\uFE0F\U0001F3FB-\U0001F3FF]*(?:\u200D[\U0001F000-\U0001FAFF\u2600-\u27BF\u2640\u2642][\uFE0F]*)*)"
)
_cache = {}


def svg(name, cls="ico"):
    if name not in _cache:
        raw = (ICON_DIR / f"{name}.svg").read_text(encoding="utf-8")
        raw = re.sub(r"<!--.*?-->", "", raw, flags=re.S).strip()
        head, rest = raw.split(">", 1)
        head = re.sub(r'\s(class|width|height)="[^"]*"', "", head)
        raw = re.sub(r"\s+", " ", head + ">" + rest).replace("<svg ", '<svg aria-hidden="true" ', 1)
        _cache[name] = raw
    return _cache[name].replace("<svg ", f'<svg class="{cls}" ', 1)


def name_for(e):
    return MAP.get(e) or MAP.get(e.replace("\uFE0F", "")) or MAP.get(e + "\uFE0F")


def icon(e, cls="ico", fallback=DEFAULT):
    """Icon slot: always returns an SVG."""
    n = name_for(e.strip()) or fallback
    return svg(n, cls)


def replace_in_html(html):
    """Running text: mapped emoji -> inline icon, unmapped -> removed."""
    def sub(m):
        n = name_for(m.group(0))
        return svg(n, "ico-inline") if n else ""
    out = EMOJI_RE.sub(sub, html)
    return re.sub(r"(<(?:h[1-6]|p|li|b|span)[^>]*>)\s+", r"\1", out)


def needed():
    return sorted(set(MAP.values()) | {DEFAULT})
