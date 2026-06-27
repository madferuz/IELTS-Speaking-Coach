"""Shared recording widgets: circular REC button + voice-reactive ripple.

Used by all three Part screens so the ripple/button behavior lives in one place.
"""

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Line, Ellipse

from theme import CORAL

# --- Ripple tuning (shared across all parts) ---
RIPPLE_FPS = 30
RIPPLE_THRESHOLD = 0.02
RIPPLE_SPAWN_GAP = 0.07
RIPPLE_LIFETIME = 0.5
RIPPLE_BASE_RADIUS = dp(55)
RIPPLE_MAX_GROWTH = dp(90)


class CircleButton(ButtonBehavior, Label):
    """A circular button: an Ellipse drawn behind centered text."""

    def __init__(self, bg_color=CORAL, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        with self.canvas.before:
            self._color = Color(*self.bg_color)
            self._circle = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self._sync_circle, size=self._sync_circle)

    def _sync_circle(self, *_):
        self._circle.pos = self.pos
        self._circle.size = self.size

    def set_bg(self, rgba):
        self._color.rgba = rgba


class _Ripple:
    def __init__(self, strength):
        self.age = 0.0
        self.growth = RIPPLE_BASE_RADIUS + RIPPLE_MAX_GROWTH * min(strength * 6, 1.0)
        self.color_instr = None
        self.line_instr = None


class RippleController:
    """Drives ripple rings on a screen's canvas, centered on a button.

    Usage:
        self.ripple = RippleController(self, self.record_btn)
        # in audio callback: self.ripple.level = rms_value
        # on record start:   self.ripple.start()
        # on record stop:    self.ripple.stop()
    """

    def __init__(self, screen, button):
        self.screen = screen
        self.button = button
        self.level = 0.0          # set this from the audio callback (RMS)
        self._ripples = []
        self._event = None
        self._time_since_spawn = 0.0
        self._active = False

    def start(self):
        self.level = 0.0
        self._active = True
        self._time_since_spawn = 0.0
        if self._event is None:
            self._event = Clock.schedule_interval(self._update, 1.0 / RIPPLE_FPS)

    def stop(self):
        self._active = False
        self.level = 0.0
        if self._event is not None:
            self._event.cancel()
            self._event = None
        self._clear()

    def _update(self, dt):
        self._time_since_spawn += dt
        if (self._active and self.level > RIPPLE_THRESHOLD
                and self._time_since_spawn >= RIPPLE_SPAWN_GAP):
            self._spawn(self.level)
            self._time_since_spawn = 0.0

        cx = self.button.center_x
        cy = self.button.center_y
        for r in self._ripples[:]:
            r.age += dt
            progress = r.age / RIPPLE_LIFETIME
            if progress >= 1.0:
                self._remove(r)
                continue
            radius = RIPPLE_BASE_RADIUS + r.growth * progress
            alpha = (1.0 - progress) * 0.7
            if r.color_instr is not None:
                r.color_instr.rgba = (CORAL[0], CORAL[1], CORAL[2], alpha)
            if r.line_instr is not None:
                r.line_instr.circle = (cx, cy, radius)

    def _spawn(self, strength):
        r = _Ripple(strength)
        cx = self.button.center_x
        cy = self.button.center_y
        with self.screen.canvas.after:
            r.color_instr = Color(CORAL[0], CORAL[1], CORAL[2], 0.7)
            r.line_instr = Line(circle=(cx, cy, RIPPLE_BASE_RADIUS), width=dp(2))
        self._ripples.append(r)

    def _remove(self, r):
        try:
            if r.color_instr is not None:
                self.screen.canvas.after.remove(r.color_instr)
            if r.line_instr is not None:
                self.screen.canvas.after.remove(r.line_instr)
        except Exception:
            pass
        if r in self._ripples:
            self._ripples.remove(r)

    def _clear(self):
        for r in self._ripples[:]:
            self._remove(r)
        self._ripples = []
