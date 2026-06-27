"""Design tokens for IELTS Speaking Coach.

All colors are RGBA tuples normalized to 0.0-1.0 (Kivy's format),
converted from the hex codes in the spec.
"""

from kivy.utils import get_color_from_hex as hx


# ============================================================
# COLORS — from spec section 2
# ============================================================

BG       = hx("#080B14")  # App background
SURFACE  = hx("#0E1220")  # Card surface
SURFACE2 = hx("#161B2E")  # Elevated surface
BORDER   = hx("#1E2640")  # Subtle borders
BORDER2  = hx("#2A3355")  # Hover/secondary

LIME     = hx("#C8F135")  # Primary accent
LIME2    = hx("#E2FF6A")  # Lime highlight
BLUE     = hx("#2B5BFF")  # Secondary accent
CYAN     = hx("#00D4FF")  # Part 1 color
VIOLET   = hx("#9747FF")  # Part 2 color
AMBER    = hx("#FFB020")  # Part 3 color
CORAL    = hx("#FF5C5C")  # Record button, danger
EMERALD  = hx("#00C896")  # Success

WHITE    = hx("#FFFFFF")
TEXT     = hx("#EDF0FF")  # Body text
MUTED    = hx("#5A6380")  # Secondary text
DIM      = hx("#2E3555")  # Disabled / decorative


# ============================================================
# TYPOGRAPHY — sp values (scale-independent pixels)
# ============================================================

FONT_HERO   = "72sp"
FONT_H1     = "24sp"
FONT_H2     = "18sp"
FONT_BODY   = "14sp"
FONT_LABEL  = "11sp"


# ============================================================
# PART CONFIGURATION — from spec section 6
# ============================================================

PARTS = {
    1: {
        "label": "PART 1",
        "name": "Introduction",
        "desc": "Familiar topics · 4 min",
        "color": CYAN,
        "duration": 60,
    },
    2: {
        "label": "PART 2",
        "name": "Long Turn",
        "desc": "Cue card · 2 min",
        "color": VIOLET,
        "duration": 120,
    },
    3: {
        "label": "PART 3",
        "name": "Discussion",
        "desc": "Abstract topics · 5 min",
        "color": AMBER,
        "duration": 60,
    },
}


# ============================================================
# HELPER FUNCTIONS — from spec section 8
# ============================================================

def band_color(score: float):
    """Return color for a band score."""
    if score >= 7.5:
        return EMERALD
    if score >= 6.0:
        return CYAN
    if score >= 5.0:
        return AMBER
    return CORAL


def band_descriptor(score: float) -> str:
    """Return text descriptor for a band score."""
    if score >= 8.5:
        return "Expert User"
    if score >= 7.5:
        return "Very Good User"
    if score >= 6.5:
        return "Good User"
    if score >= 5.5:
        return "Competent User"
    if score >= 4.5:
        return "Modest User"
    return "Limited User"


def format_time(seconds: int) -> str:
    """Format seconds as M:SS."""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"