"""Depth helpers for the dark theme.

On a dark UI, "elevation" reads as a soft COLORED GLOW behind an element plus a
subtle border -- not the grey drop-shadow you'd use on a light theme.

Usage inside a widget's __init__, BEFORE drawing its own background:

    from depth import draw_glow
    with self.canvas.before:
        draw_glow(self, part["color"])      # halo goes down first (back layer)
        Color(*SURFACE)
        self._rect = RoundedRectangle(...)  # solid card on top of the glow

draw_glow returns nothing; it binds itself to the widget's pos/size so the halo
follows the widget. Keep your own _rect handling exactly as before.
"""

from kivy.graphics import Color, RoundedRectangle
from kivy.graphics.texture import Texture
from kivy.metrics import dp


_GLOW_TEX = None


def _build_glow_texture(size=64, falloff=1.8):
    """A soft radial blob (white, alpha fades to edges) to fake a blurred glow."""
    s = size
    buf = bytearray(s * s * 4)
    cx = cy = (s - 1) / 2.0
    maxd = (cx ** 2 + cy ** 2) ** 0.5
    for y in range(s):
        for x in range(s):
            d = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5 / maxd
            a = max(0.0, 1.0 - d) ** falloff
            i = (y * s + x) * 4
            buf[i] = buf[i + 1] = buf[i + 2] = 255
            buf[i + 3] = int(a * 255)
    tex = Texture.create(size=(s, s), colorfmt="rgba")
    tex.blit_buffer(bytes(buf), colorfmt="rgba", bufferfmt="ubyte")
    tex.wrap = "clamp_to_edge"
    return tex


def glow_texture():
    global _GLOW_TEX
    if _GLOW_TEX is None:
        _GLOW_TEX = _build_glow_texture()
    return _GLOW_TEX


def draw_glow(widget, color, spread=dp(16), alpha=0.45):
    """Add a soft colored halo to the CURRENT canvas context, behind whatever is
    drawn next. Call this inside a `with widget.canvas.before:` block, before the
    widget's own background rectangle, so the glow sits underneath.

    The glow keeps itself aligned to the widget via pos/size bindings.
    """
    r, g, b = color[0], color[1], color[2]
    glow_color = Color(r, g, b, alpha)
    glow_rect = RoundedRectangle(
        texture=glow_texture(),
        pos=(widget.x - spread, widget.y - spread),
        size=(widget.width + 2 * spread, widget.height + 2 * spread),
    )

    def _sync(*_):
        glow_rect.pos = (widget.x - spread, widget.y - spread)
        glow_rect.size = (widget.width + 2 * spread, widget.height + 2 * spread)

    widget.bind(pos=_sync, size=_sync)
    return glow_rect
