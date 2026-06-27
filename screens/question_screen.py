"""Part 1 Question screen for IELTS Speaking Coach.

Shows a question from the bank, runs a countdown timer, and
records the user's answer to a .wav file in recordings/.
Includes a live voice-reactive ripple visualizer around the REC button.
"""

from datetime import datetime
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, RoundedRectangle, Line, Ellipse

from questions import get_random_question
from sound import play_tap, play_click
from theme import (
    BG,
    TEXT,
    MUTED,
    CORAL,
    EMERALD,
    PARTS,
    format_time,
)


SAMPLE_RATE = 44100
CHANNELS = 1
PART_1_DURATION = PARTS[1]["duration"]

RECORDINGS_DIR = Path(__file__).resolve().parent.parent / "recordings"
RECORDINGS_DIR.mkdir(exist_ok=True)

# --- Ripple tuning ---
RIPPLE_FPS = 30                 # how often we update the rings
RIPPLE_THRESHOLD = 0.02         # min loudness (RMS) before a ring spawns
RIPPLE_SPAWN_GAP = 0.07         # min seconds between new rings (snappy)
RIPPLE_LIFETIME = 0.5           # seconds for a ring to expand & fade
RIPPLE_BASE_RADIUS = dp(55)     # starting radius (just outside the REC button)
RIPPLE_MAX_GROWTH = dp(90)      # extra radius a loud ring travels


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


class Ripple:
    """A single expanding, fading ring."""

    def __init__(self, strength):
        self.age = 0.0
        self.growth = RIPPLE_BASE_RADIUS + RIPPLE_MAX_GROWTH * min(strength * 6, 1.0)
        self.color_instr = None
        self.line_instr = None


class Part1Screen(Screen):
    """Part 1 — short Q&A, timed answer."""

    def __init__(self, used_indices=None, **kwargs):
        super().__init__(**kwargs)
        self.used_indices = used_indices if used_indices is not None else set()
        self.current_idx = None
        self.current_question = None
        # Full-test mode hooks (set by main.py)
        self.test_mode = False
        self.on_test_complete = None
        self._test_q_count = 0
        self._test_q_target = 4

        self.is_recording = False
        self.audio_frames = []
        self.stream = None
        self.timer_event = None
        self.seconds_left = PART_1_DURATION

        # Ripple state
        self._current_level = 0.0
        self._ripples = []
        self._ripple_event = None
        self._time_since_spawn = 0.0

        self._build_ui()
        self._load_question()

    def _build_ui(self):
        with self.canvas.before:
            Color(*BG)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[0])
        self.bind(pos=self._update_bg, size=self._update_bg)

        root = BoxLayout(
            orientation="vertical",
            padding=[dp(24), dp(40), dp(24), dp(40)],
            spacing=dp(20),
        )

        top_bar = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(12))
        back_btn = Button(
            text="< Back",
            size_hint_x=None,
            width=dp(80),
            background_color=(0, 0, 0, 0),
            color=MUTED,
            font_size=dp(16),
        )
        back_btn.bind(on_release=self._go_home)
        part_label = Label(
            text="Part 1 - Introduction",
            color=MUTED,
            font_size=dp(14),
            halign="right",
            valign="middle",
        )
        part_label.bind(size=lambda i, s: setattr(i, "text_size", s))
        top_bar.add_widget(back_btn)
        top_bar.add_widget(part_label)
        root.add_widget(top_bar)

        self.topic_label = Label(
            text="",
            color=MUTED,
            font_size=dp(14),
            size_hint_y=None,
            height=dp(24),
            halign="center",
        )
        root.add_widget(self.topic_label)

        self.question_label = Label(
            text="",
            color=TEXT,
            font_size=dp(26),
            halign="center",
            valign="middle",
            bold=True,
        )
        self.question_label.bind(
            size=lambda i, s: setattr(i, "text_size", (s[0], None))
        )
        root.add_widget(self.question_label)

        self.tips_label = Label(
            text="",
            color=MUTED,
            font_size=dp(14),
            halign="center",
            valign="top",
            size_hint_y=None,
            height=dp(90),
        )
        self.tips_label.bind(
            size=lambda i, s: setattr(i, "text_size", (s[0], None))
        )
        root.add_widget(self.tips_label)

        self.timer_label = Label(
            text=format_time(PART_1_DURATION),
            color=TEXT,
            font_size=dp(48),
            size_hint_y=None,
            height=dp(70),
            bold=True,
        )
        root.add_widget(self.timer_label)

        # Centered circular REC button via spacers on each side
        btn_row = BoxLayout(size_hint_y=None, height=dp(120))
        btn_row.add_widget(Widget())  # left spacer
        self.record_btn = CircleButton(
            text="REC",
            bg_color=CORAL,
            size_hint=(None, None),
            size=(dp(100), dp(100)),
            color=TEXT,
            font_size=dp(20),
            bold=True,
        )
        self.record_btn.bind(on_release=self._toggle_recording)
        # Wrap in an anchor so the fixed-size circle stays vertically centered
        center_holder = BoxLayout(size_hint=(None, 1), width=dp(100))
        center_holder.add_widget(self.record_btn)
        btn_row.add_widget(center_holder)
        btn_row.add_widget(Widget())  # right spacer
        root.add_widget(btn_row)

        self.status_label = Label(
            text="Tap to start recording",
            color=MUTED,
            font_size=dp(14),
            size_hint_y=None,
            height=dp(24),
        )
        root.add_widget(self.status_label)

        self.next_btn = Button(
            text="Next question",
            size_hint_y=None,
            height=dp(48),
            background_normal="",
            background_color=EMERALD,
            color=TEXT,
            font_size=dp(16),
            disabled=True,
            opacity=0.5,
        )
        self.next_btn.bind(on_release=self._next_question)
        root.add_widget(self.next_btn)

        self.add_widget(root)

    def _update_bg(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _load_question(self):
        result = get_random_question(1, self.used_indices)
        if result is None:
            self.question_label.text = "You've answered all Part 1 questions!"
            self.topic_label.text = ""
            self.tips_label.text = ""
            self.record_btn.disabled = True
            return

        q, idx = result
        self.current_question = q
        self.current_idx = idx
        self.topic_label.text = "Topic - " + q["topic"]
        self.question_label.text = q["question"]
        self.tips_label.text = "\n".join("- " + t for t in q["tips"])
        self.timer_label.text = format_time(PART_1_DURATION)
        self.seconds_left = PART_1_DURATION
        self.status_label.text = "Tap to start recording"
        self.next_btn.disabled = True
        self.next_btn.opacity = 0.5

    def _toggle_recording(self, *_):
        if self.is_recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        self.audio_frames = []
        self.is_recording = True
        self.record_btn.text = "STOP"
        self.status_label.text = "Recording..."
        self.seconds_left = PART_1_DURATION
        self._current_level = 0.0

        def callback(indata, frames, time_info, status):
            if status:
                print("Audio status:", status)
            self.audio_frames.append(indata.copy())
            try:
                self._current_level = float(np.sqrt(np.mean(indata.astype(np.float64) ** 2)))
            except Exception:
                self._current_level = 0.0

        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            callback=callback,
        )
        self.stream.start()

        self.timer_event = Clock.schedule_interval(self._tick, 1.0)
        self._ripple_event = Clock.schedule_interval(self._update_ripples, 1.0 / RIPPLE_FPS)

    def _tick(self, _dt):
        self.seconds_left -= 1
        self.timer_label.text = format_time(max(self.seconds_left, 0))
        self.timer_label.color = CORAL if self.seconds_left <= 10 else TEXT
        if self.seconds_left <= 0:
            self._stop_recording()
            return False

    def _update_ripples(self, dt):
        self._time_since_spawn += dt
        level = self._current_level
        if (self.is_recording and level > RIPPLE_THRESHOLD
                and self._time_since_spawn >= RIPPLE_SPAWN_GAP):
            self._spawn_ripple(level)
            self._time_since_spawn = 0.0

        cx = self.record_btn.center_x
        cy = self.record_btn.center_y

        for ripple in self._ripples[:]:
            ripple.age += dt
            progress = ripple.age / RIPPLE_LIFETIME
            if progress >= 1.0:
                self._remove_ripple(ripple)
                continue
            radius = RIPPLE_BASE_RADIUS + ripple.growth * progress
            alpha = (1.0 - progress) * 0.7
            if ripple.color_instr is not None:
                ripple.color_instr.rgba = (CORAL[0], CORAL[1], CORAL[2], alpha)
            if ripple.line_instr is not None:
                ripple.line_instr.circle = (cx, cy, radius)

    def _spawn_ripple(self, strength):
        ripple = Ripple(strength)
        cx = self.record_btn.center_x
        cy = self.record_btn.center_y
        with self.canvas.after:
            ripple.color_instr = Color(CORAL[0], CORAL[1], CORAL[2], 0.7)
            ripple.line_instr = Line(circle=(cx, cy, RIPPLE_BASE_RADIUS), width=dp(2))
        self._ripples.append(ripple)

    def _remove_ripple(self, ripple):
        try:
            if ripple.color_instr is not None:
                self.canvas.after.remove(ripple.color_instr)
            if ripple.line_instr is not None:
                self.canvas.after.remove(ripple.line_instr)
        except Exception:
            pass
        if ripple in self._ripples:
            self._ripples.remove(ripple)

    def _clear_ripples(self):
        for ripple in self._ripples[:]:
            self._remove_ripple(ripple)
        self._ripples = []

    def _stop_recording(self):
        if not self.is_recording:
            return
        self.is_recording = False

        if self.timer_event is not None:
            self.timer_event.cancel()
            self.timer_event = None

        if self._ripple_event is not None:
            self._ripple_event.cancel()
            self._ripple_event = None
        self._clear_ripples()
        self._current_level = 0.0

        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        play_click()

        self.record_btn.text = "REC"

        if self.audio_frames:
            audio = np.concatenate(self.audio_frames, axis=0)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = RECORDINGS_DIR / ("part1_" + timestamp + ".wav")
            sf.write(str(filename), audio, SAMPLE_RATE)
            self.status_label.text = "Answer recorded"
            if self.current_idx is not None:
                self.used_indices.add(self.current_idx)

            if getattr(self, "test_mode", False):
                # Full test: auto-advance through several Part 1 questions
                self._test_q_count += 1
                self.next_btn.disabled = True
                self.next_btn.opacity = 0.5
                if self._test_q_count >= self._test_q_target:
                    Clock.schedule_once(lambda dt: self._finish_part1_test(), 1.5)
                else:
                    Clock.schedule_once(lambda dt: self._load_question(), 1.5)
            else:
                self.next_btn.disabled = False
                self.next_btn.opacity = 1.0
        else:
            self.status_label.text = "No audio captured"

    def _next_question(self, *_):
        play_tap()
        self._load_question()

    def _finish_part1_test(self):
        self._test_q_count = 0
        if self.on_test_complete:
            self.on_test_complete()

    def _go_home(self, *_):
        play_tap()
        if self.is_recording:
            self._stop_recording()
        self.manager.current = "home"
