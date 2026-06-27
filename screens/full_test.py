"""Full Test mode — start and completion screens for the mock exam flow.

The completion screen shows a looping confetti celebration plus a
bouncy "Congratulations" headline.
"""

import random

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.graphics import Color, RoundedRectangle, Ellipse, PushMatrix, PopMatrix, Rotate

from sound import play_tap
from theme import (
    BG, SURFACE2, LIME, TEXT, MUTED, EMERALD, CYAN, VIOLET, AMBER, CORAL,
    FONT_LABEL, FONT_BODY,
)


CONFETTI_COLORS = [LIME, CYAN, VIOLET, AMBER, CORAL, EMERALD]


def _bg(screen):
    with screen.canvas.before:
        Color(*BG)
        screen._bg = RoundedRectangle(pos=screen.pos, size=screen.size, radius=[0])
    screen.bind(
        pos=lambda *_: setattr(screen._bg, "pos", screen.pos),
        size=lambda *_: setattr(screen._bg, "size", screen.size),
    )


class TestStartScreen(Screen):
    """Shown when the user taps FULL MOCK TEST. Explains the flow, then begins."""

    def __init__(self, on_begin, on_cancel, **kwargs):
        super().__init__(**kwargs)
        self.on_begin = on_begin
        self.on_cancel = on_cancel
        _bg(self)
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical",
                         padding=[dp(28), dp(48), dp(28), dp(40)], spacing=dp(20))

        title = Label(text="Full Mock Test", color=TEXT, font_size=dp(30), bold=True,
                      size_hint_y=None, height=dp(44))
        root.add_widget(title)

        subtitle = Label(
            text="A complete IELTS speaking test, just like the real thing.",
            color=MUTED, font_size=dp(15), size_hint_y=None, height=dp(48),
            halign="center", valign="top",
        )
        subtitle.bind(width=lambda i, w: setattr(i, "text_size", (w, None)))
        root.add_widget(subtitle)

        card = BoxLayout(orientation="vertical", padding=[dp(20), dp(20)],
                         spacing=dp(14), size_hint_y=None, height=dp(220))
        with card.canvas.before:
            Color(*SURFACE2)
            card._rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(16)])
        card.bind(
            pos=lambda *_: setattr(card._rect, "pos", card.pos),
            size=lambda *_: setattr(card._rect, "size", card.size),
        )

        rows = [
            ("PART 1", "Introduction - a few short questions"),
            ("PART 2", "Long turn - cue card with prep time"),
            ("PART 3", "Discussion - deeper follow-up questions"),
        ]
        for label, desc in rows:
            row = BoxLayout(orientation="vertical", spacing=dp(2),
                            size_hint_y=None, height=dp(50))
            lbl = Label(text=label, color=LIME, font_size=FONT_LABEL, bold=True,
                        halign="left", valign="middle", size_hint_y=None, height=dp(18))
            lbl.bind(size=lambda i, s: setattr(i, "text_size", s))
            d = Label(text=desc, color=TEXT, font_size=FONT_BODY,
                      halign="left", valign="middle", size_hint_y=None, height=dp(26))
            d.bind(size=lambda i, s: setattr(i, "text_size", s))
            row.add_widget(lbl)
            row.add_widget(d)
            card.add_widget(row)
        root.add_widget(card)

        note = Label(
            text="The test runs continuously - it won't pause between parts. Set aside ~14 minutes.",
            color=MUTED, font_size=dp(13), size_hint_y=None, height=dp(56),
            halign="center", valign="top",
        )
        note.bind(width=lambda i, w: setattr(i, "text_size", (w, None)))
        root.add_widget(note)

        root.add_widget(BoxLayout())

        begin_btn = Button(text="Begin test", size_hint_y=None, height=dp(54),
                           background_normal="", background_color=LIME, color=BG,
                           font_size=dp(17), bold=True)
        begin_btn.bind(on_release=self._begin)
        root.add_widget(begin_btn)

        cancel_btn = Button(text="Not now", size_hint_y=None, height=dp(44),
                            background_color=(0, 0, 0, 0), color=MUTED, font_size=dp(15))
        cancel_btn.bind(on_release=self._cancel)
        root.add_widget(cancel_btn)

        self.add_widget(root)

    def _begin(self, *_):
        play_tap()
        self.on_begin()

    def _cancel(self, *_):
        play_tap()
        self.on_cancel()


class _Confetto:
    """A single falling confetti piece (a small rotating rectangle)."""

    def __init__(self):
        self.color_instr = None
        self.rect = None
        self.rot = None
        self.push = None
        self.pop = None
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.size = dp(8)
        self.spin = 0.0
        self.angle = 0.0


class TestEndScreen(Screen):
    """Shown after Part 3 in test mode: looping confetti + congratulations."""

    def __init__(self, on_home, **kwargs):
        super().__init__(**kwargs)
        self.on_home = on_home
        self._confetti = []
        self._spawn_event = None
        self._update_event = None
        _bg(self)
        self._build_ui()

    def _build_ui(self):
        root = BoxLayout(orientation="vertical",
                         padding=[dp(28), dp(60), dp(28), dp(40)], spacing=dp(18))

        root.add_widget(BoxLayout())  # top spacer

        self.headline = Label(text="Congratulations!", color=LIME, font_size=dp(32),
                              bold=True, size_hint_y=None, height=dp(48))
        root.add_widget(self.headline)

        self.subhead = Label(text="Test complete", color=EMERALD, font_size=dp(22),
                             bold=True, size_hint_y=None, height=dp(34))
        root.add_widget(self.subhead)

        msg = Label(
            text="You finished all three parts. Your answers have been recorded.",
            color=TEXT, font_size=dp(16), size_hint_y=None, height=dp(60),
            halign="center", valign="top",
        )
        msg.bind(width=lambda i, w: setattr(i, "text_size", (w, None)))
        root.add_widget(msg)

        pending = Label(
            text="AI band scores and feedback will appear here once scoring is connected.",
            color=MUTED, font_size=dp(13), size_hint_y=None, height=dp(56),
            halign="center", valign="top",
        )
        pending.bind(width=lambda i, w: setattr(i, "text_size", (w, None)))
        root.add_widget(pending)

        root.add_widget(BoxLayout())  # bottom spacer

        home_btn = Button(text="Back to home", size_hint_y=None, height=dp(54),
                          background_normal="", background_color=EMERALD, color=TEXT,
                          font_size=dp(17), bold=True)
        home_btn.bind(on_release=self._home)
        root.add_widget(home_btn)

        self.add_widget(root)

    # ------------------------------------------------------------
    # Confetti lifecycle
    # ------------------------------------------------------------
    def on_enter(self, *args):
        # Bouncy headline pop
        self.headline.font_size = dp(10)
        Animation(font_size=dp(32), duration=0.5, transition="out_back").start(self.headline)

        # Start looping confetti
        self._spawn_event = Clock.schedule_interval(self._spawn_batch, 0.18)
        self._update_event = Clock.schedule_interval(self._update_confetti, 1 / 30.)

    def on_leave(self, *args):
        if self._spawn_event:
            self._spawn_event.cancel()
            self._spawn_event = None
        if self._update_event:
            self._update_event.cancel()
            self._update_event = None
        self._clear_confetti()

    def _spawn_batch(self, _dt):
        for _ in range(3):
            self._spawn_one()

    def _spawn_one(self):
        c = _Confetto()
        c.x = random.uniform(0, self.width)
        c.y = self.height + dp(10)
        c.vx = random.uniform(-30, 30)
        c.vy = random.uniform(-120, -60)
        c.size = random.uniform(dp(6), dp(11))
        c.spin = random.uniform(-180, 180)
        col = random.choice(CONFETTI_COLORS)
        with self.canvas.after:
            c.push = PushMatrix()
            c.rot = Rotate(angle=0, origin=(c.x, c.y))
            c.color_instr = Color(col[0], col[1], col[2], 1)
            c.rect = Ellipse(pos=(c.x, c.y), size=(c.size, c.size * 0.6))
            c.pop = PopMatrix()
        self._confetti.append(c)

    def _update_confetti(self, dt):
        for c in self._confetti[:]:
            c.vy -= 200 * dt          # gravity pulls down
            c.x += c.vx * dt
            c.y += c.vy * dt
            c.angle = (c.angle + c.spin * dt) % 360
            if c.rect is not None:
                c.rect.pos = (c.x, c.y)
            if c.rot is not None:
                c.rot.origin = (c.x + c.size / 2, c.y + c.size / 2)
                c.rot.angle = c.angle
            if c.y < -dp(20):
                self._remove(c)

    def _remove(self, c):
        for instr in (c.push, c.rot, c.color_instr, c.rect, c.pop):
            try:
                if instr is not None:
                    self.canvas.after.remove(instr)
            except Exception:
                pass
        if c in self._confetti:
            self._confetti.remove(c)

    def _clear_confetti(self):
        for c in self._confetti[:]:
            self._remove(c)
        self._confetti = []

    def _home(self, *_):
        play_tap()
        self.on_home()
