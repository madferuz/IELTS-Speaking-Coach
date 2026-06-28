"""Home screen — landing page with hero, stats, full-test card, and practice pills.

Depth pass: cards now sit on the dark background with a soft COLORED GLOW behind
them plus a 1px border, the dark-theme equivalent of elevation. All navigation,
callbacks, and animations are unchanged from the original.
"""

import os

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.scrollview import ScrollView
from kivy.graphics import (
    Color, RoundedRectangle, Line, PushMatrix, PopMatrix, Rotate,
)
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.clock import Clock

from theme import (
    SURFACE, SURFACE2, BORDER, LIME, TEXT, MUTED, DIM, BG,
    FONT_H2, FONT_BODY, FONT_LABEL,
    PARTS,
)
from questions import total_questions
from sound import play_tap
from depth import draw_glow


# Path to the graduation cap image (assets/ next to the project root)
CAP_IMAGE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "graduationhat.png",
)


def make_label(text, font_size, color, bold=False, height=24):
    lbl = Label(
        text=text, font_size=font_size, color=color, bold=bold,
        halign="left", valign="middle",
        size_hint_y=None, height=dp(height),
    )
    lbl.bind(width=lambda i, w: setattr(i, "text_size", (w, None)))
    return lbl


class RockingImage(Image):
    """An image that rocks/tilts back and forth continuously."""

    def __init__(self, source, max_angle=14, **kwargs):
        super().__init__(source=source, allow_stretch=True, keep_ratio=True, **kwargs)
        self._max_angle = max_angle
        with self.canvas.before:
            PushMatrix()
            self._rot = Rotate(angle=0, origin=self.center)
        with self.canvas.after:
            PopMatrix()
        self.bind(pos=self._update_origin, size=self._update_origin)

    def _update_origin(self, *_):
        self._rot.origin = self.center

    def start_rocking(self):
        self._rot.angle = -self._max_angle
        self._rock_to(self._max_angle)

    def _rock_to(self, target):
        anim = Animation(angle=target, duration=1.1, transition="in_out_sine")
        anim.bind(on_complete=lambda *a: self._rock_to(-target))
        anim.start(self._rot)


class RoundedCard(BoxLayout):
    """A surface card with an optional soft glow halo and a subtle border."""

    def __init__(self, bg_color=SURFACE, radius=12,
                 glow_color=None, glow_alpha=0.25, border_color=BORDER, **kwargs):
        super().__init__(**kwargs)
        _radius = dp(radius)
        with self.canvas.before:
            # glow first (back layer) so the solid fill sits on top of it
            if glow_color is not None:
                draw_glow(self, glow_color, spread=dp(14), alpha=glow_alpha)
            Color(*bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[_radius])
            # subtle border for crisp edges on the dark bg
            self._border_color = Color(*border_color)
            self._border = Line(
                rounded_rectangle=(self.x, self.y, self.width, self.height, _radius),
                width=1.0,
            )
        self._radius = _radius
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._border.rounded_rectangle = (
            self.x, self.y, self.width, self.height, self._radius,
        )


class FullTestCard(ButtonBehavior, BoxLayout):
    """Big primary card that starts a full mock exam (all 3 parts)."""

    def __init__(self, on_start, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = [dp(20), dp(18)]
        self.spacing = dp(4)
        self.size_hint_y = None
        self.height = dp(110)
        self.on_start = on_start
        self._press_inset = dp(6)

        with self.canvas.before:
            # lime glow makes the primary action visibly "lift" off the page
            draw_glow(self, LIME, spread=dp(28), alpha=0.62)
            Color(*LIME)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(16)])
        self.bind(pos=self._sync, size=self._sync)

        self.add_widget(make_label("FULL MOCK TEST", FONT_LABEL, BG, bold=True, height=20))
        self.add_widget(make_label("Take the complete exam", "19sp", BG, bold=True, height=30))
        self.add_widget(make_label("All 3 parts - one continuous test - ~14 min",
                                   FONT_BODY, BG, height=24))

    def _sync(self, *_):
        if not getattr(self, "_animating", False):
            self._rect.pos = self.pos
            self._rect.size = self.size

    def on_press(self):
        play_tap()
        self._animating = True
        inset = self._press_inset
        target_pos = (self.x + inset, self.y + inset)
        target_size = (self.width - 2 * inset, self.height - 2 * inset)
        Animation.cancel_all(self._rect)
        Animation(pos=target_pos, size=target_size,
                  duration=0.09, transition="out_quad").start(self._rect)

    def on_release(self):
        Animation.cancel_all(self._rect)
        anim = Animation(pos=self.pos, size=self.size,
                         duration=0.32, transition="out_back")

        def _done(*_):
            self._animating = False
            self.on_start()

        anim.bind(on_complete=_done)
        anim.start(self._rect)


class PartPill(ButtonBehavior, BoxLayout):
    """A compact, color-accented pill for selecting a single part to practice."""

    def __init__(self, part_id, on_select, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = [dp(8), dp(14)]
        self.spacing = dp(2)
        self.part_id = part_id
        self.on_select_callback = on_select
        self._press_inset = dp(4)

        part = PARTS[part_id]
        radius = dp(20)

        with self.canvas.before:
            # each pill glows in its own part color (cyan / violet / amber)
            draw_glow(self, part["color"], spread=dp(18), alpha=0.38)
            Color(*SURFACE)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[radius])
            self._accent_color = Color(*part["color"])
            self._accent = RoundedRectangle(
                pos=self.pos, size=(self.width, dp(4)), radius=[dp(2)],
            )
        self.bind(pos=self._sync, size=self._sync)

        self.add_widget(Label(
            text=part["label"], font_size=FONT_LABEL, color=part["color"], bold=True,
            halign="center", valign="middle", size_hint_y=None, height=dp(18),
        ))
        name_lbl = Label(
            text=part["name"], font_size="13sp", color=TEXT, bold=True,
            halign="center", valign="middle", size_hint_y=None, height=dp(20),
        )
        name_lbl.bind(width=lambda i, w: setattr(i, "text_size", (w, None)))
        self.add_widget(name_lbl)
        self.add_widget(Label(
            text="{} Qs".format(total_questions(part_id)),
            font_size=FONT_LABEL, color=MUTED,
            halign="center", valign="middle", size_hint_y=None, height=dp(16),
        ))

    def _sync(self, *_):
        if not getattr(self, "_animating", False):
            self._rect.pos = self.pos
            self._rect.size = self.size
        self._accent.pos = (self.x, self.top - dp(4))
        self._accent.size = (self.width, dp(4))

    def on_press(self):
        play_tap()
        self._animating = True
        inset = self._press_inset
        target_pos = (self.x + inset, self.y + inset)
        target_size = (self.width - 2 * inset, self.height - 2 * inset)
        Animation.cancel_all(self._rect)
        Animation(pos=target_pos, size=target_size,
                  duration=0.09, transition="out_quad").start(self._rect)

    def on_release(self):
        Animation.cancel_all(self._rect)
        anim = Animation(pos=self.pos, size=self.size,
                         duration=0.32, transition="out_back")

        def _done(*_):
            self._animating = False
            self.on_select_callback(self.part_id)

        anim.bind(on_complete=_done)
        anim.start(self._rect)


class HomeScreen(Screen):
    def __init__(self, on_part_selected, on_full_test=None, **kwargs):
        super().__init__(**kwargs)
        self.on_part_selected = on_part_selected
        self.on_full_test = on_full_test or self._full_test_placeholder
        self._pills = []
        self._full_card = None
        self._cap = None
        self._build_ui()

    def _full_test_placeholder(self):
        print("Full Test tapped — flow controller not wired yet (Stage 2).")

    def _build_ui(self):
        scroll = ScrollView(do_scroll_x=False)
        root = BoxLayout(orientation="vertical", padding=[dp(20), dp(20)],
                         spacing=dp(16), size_hint_y=None)
        root.bind(minimum_height=root.setter("height"))

        # Hero: text on the left, rocking graduation cap image on the right
        hero = RoundedCard(bg_color=SURFACE2, orientation="horizontal",
                           padding=[dp(20), dp(20)], spacing=dp(8),
                           glow_color=LIME, glow_alpha=0.18,
                           size_hint_y=None, height=dp(170))

        hero_text = BoxLayout(orientation="vertical", spacing=dp(6))
        hero_text.add_widget(make_label("AI COACH", FONT_LABEL, LIME, bold=True, height=20))
        hero_text.add_widget(make_label("Master Your Speaking Test", "22sp", TEXT, bold=True, height=60))
        hero_text.add_widget(make_label("Record answers - Get AI band scores", FONT_BODY, MUTED, height=24))
        hero.add_widget(hero_text)

        self._cap = RockingImage(CAP_IMAGE, max_angle=14,
                                 size_hint_x=None, width=dp(78))
        hero.add_widget(self._cap)

        root.add_widget(hero)

        stats = BoxLayout(orientation="horizontal", spacing=dp(10),
                         size_hint_y=None, height=dp(80))
        for value, label_text in [("40", "Questions"), ("4", "Criteria"), ("9.0", "Max Band")]:
            box = RoundedCard(bg_color=SURFACE, orientation="vertical", padding=dp(10))
            box.add_widget(Label(text=value, font_size="22sp", bold=True, color=LIME))
            box.add_widget(Label(text=label_text, font_size=FONT_LABEL, color=MUTED))
            stats.add_widget(box)
        root.add_widget(stats)

        # --- FULL TEST (primary action) ---
        self._full_card = FullTestCard(on_start=lambda: self.on_full_test())
        root.add_widget(self._full_card)

        # --- PRACTICE (individual parts) ---
        root.add_widget(make_label("OR PRACTICE ONE PART", FONT_LABEL, MUTED, bold=True, height=20))

        pill_row = BoxLayout(orientation="horizontal", spacing=dp(10),
                             size_hint_y=None, height=dp(78))
        for part_id in (1, 2, 3):
            pill = PartPill(part_id=part_id, on_select=self.on_part_selected)
            self._pills.append(pill)
            pill_row.add_widget(pill)
        root.add_widget(pill_row)

        root.add_widget(make_label("HOW IT WORKS", FONT_LABEL, MUTED, bold=True, height=20))

        for num, text in [("1", "Pick a part and read the question"),
                          ("2", "Record your spoken answer"),
                          ("3", "Get an AI band score with feedback")]:
            row = BoxLayout(orientation="horizontal", spacing=dp(12),
                           size_hint_y=None, height=dp(36))
            row.add_widget(Label(text=num, font_size="20sp", bold=True, color=DIM,
                                 size_hint_x=None, width=dp(30)))
            row.add_widget(make_label(text, FONT_BODY, TEXT, height=36))
            root.add_widget(row)

        scroll.add_widget(root)
        self.add_widget(scroll)

    def on_pre_enter(self, *args):
        for pill in self._pills:
            pill.opacity = 0
        if self._full_card is not None:
            self._full_card.opacity = 0

    def on_enter(self, *args):
        items = ([self._full_card] if self._full_card else []) + self._pills
        for i, item in enumerate(items):
            anim = Animation(opacity=1, duration=0.4, transition="out_quad")
            Clock.schedule_once(lambda dt, w=item, a=anim: a.start(w), i * 0.1)
        if self._cap is not None:
            self._cap.start_rocking()
