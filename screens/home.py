"""Home screen — landing page with hero, stats, and part cards."""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.clock import Clock

from theme import (
    SURFACE, SURFACE2, LIME, TEXT, MUTED, DIM,
    FONT_H2, FONT_BODY, FONT_LABEL,
    PARTS,
)
from questions import total_questions
from sound import play_tap


def make_label(text, font_size, color, bold=False, height=24):
    lbl = Label(
        text=text, font_size=font_size, color=color, bold=bold,
        halign="left", valign="middle",
        size_hint_y=None, height=dp(height),
    )
    lbl.bind(width=lambda i, w: setattr(i, "text_size", (w, None)))
    return lbl


class RoundedCard(BoxLayout):
    def __init__(self, bg_color=SURFACE, radius=12, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*bg_color)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(radius)])
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *_):
        self._rect.pos = self.pos
        self._rect.size = self.size


class PartCard(ButtonBehavior, BoxLayout):
    def __init__(self, part_id, on_select, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = [dp(16), dp(14)]
        self.spacing = dp(4)
        self.size_hint_y = None
        self.height = dp(130)
        self.part_id = part_id
        self.on_select_callback = on_select
        # How far the card shrinks inward on press (in dp)
        self._press_inset = dp(6)

        with self.canvas.before:
            Color(*SURFACE)
            self._rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(12)])
        self.bind(pos=self._sync, size=self._sync)

        part = PARTS[part_id]
        self.add_widget(make_label(part["label"], FONT_LABEL, part["color"], bold=True, height=20))
        self.add_widget(make_label(part["name"], FONT_H2, TEXT, bold=True, height=30))
        self.add_widget(make_label(part["desc"], FONT_BODY, MUTED, height=26))
        self.add_widget(make_label(
            "{} questions".format(total_questions(part_id)),
            FONT_LABEL, part["color"], bold=True, height=20,
        ))

    def _sync(self, *_):
        # Only re-sync from layout when not mid-press-animation
        if not getattr(self, "_animating", False):
            self._rect.pos = self.pos
            self._rect.size = self.size

    def on_press(self):
        # Play tap sound + springy shrink-inward on touch down
        play_tap()
        self._animating = True
        inset = self._press_inset
        target_pos = (self.x + inset, self.y + inset)
        target_size = (self.width - 2 * inset, self.height - 2 * inset)
        Animation.cancel_all(self._rect)
        anim = Animation(pos=target_pos, size=target_size,
                         duration=0.09, transition="out_quad")
        anim.start(self._rect)

    def on_release(self):
        # Spring back out with overshoot, then fire the callback
        Animation.cancel_all(self._rect)
        anim = Animation(pos=self.pos, size=self.size,
                         duration=0.32, transition="out_back")

        def _done(*_):
            self._animating = False
            self.on_select_callback(self.part_id)

        anim.bind(on_complete=_done)
        anim.start(self._rect)


class HomeScreen(Screen):
    def __init__(self, on_part_selected, **kwargs):
        super().__init__(**kwargs)
        self.on_part_selected = on_part_selected
        self._cards = []
        self._build_ui()

    def _build_ui(self):
        scroll = ScrollView(do_scroll_x=False)
        root = BoxLayout(orientation="vertical", padding=[dp(20), dp(20)],
                         spacing=dp(16), size_hint_y=None)
        root.bind(minimum_height=root.setter("height"))

        hero = RoundedCard(bg_color=SURFACE2, orientation="vertical",
                           padding=[dp(20), dp(20)], spacing=dp(6),
                           size_hint_y=None, height=dp(170))
        hero.add_widget(make_label("AI COACH", FONT_LABEL, LIME, bold=True, height=20))
        hero.add_widget(make_label("Master Your Speaking Test", "22sp", TEXT, bold=True, height=60))
        hero.add_widget(make_label("Record answers - Get AI band scores", FONT_BODY, MUTED, height=24))
        root.add_widget(hero)

        stats = BoxLayout(orientation="horizontal", spacing=dp(10),
                         size_hint_y=None, height=dp(80))
        for value, label_text in [("40", "Questions"), ("4", "Criteria"), ("9.0", "Max Band")]:
            box = RoundedCard(bg_color=SURFACE, orientation="vertical", padding=dp(10))
            box.add_widget(Label(text=value, font_size="22sp", bold=True, color=LIME))
            box.add_widget(Label(text=label_text, font_size=FONT_LABEL, color=MUTED))
            stats.add_widget(box)
        root.add_widget(stats)

        root.add_widget(make_label("SELECT A PART", FONT_LABEL, MUTED, bold=True, height=20))

        for part_id in (1, 2, 3):
            card = PartCard(part_id=part_id, on_select=self.on_part_selected)
            self._cards.append(card)
            root.add_widget(card)

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
        # Reset cards to hidden before the entrance animation
        for card in self._cards:
            card.opacity = 0

    def on_enter(self, *args):
        # Stagger each card fading in, one after another
        for i, card in enumerate(self._cards):
            anim = Animation(opacity=1, duration=0.4, transition="out_quad")
            Clock.schedule_once(lambda dt, c=card, a=anim: a.start(c), i * 0.1)
