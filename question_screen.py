"""Part 1 Question screen for IELTS Speaking Coach.

Shows a question from the bank, runs a countdown timer, and
records the user's answer to a .wav file in recordings/.
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
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, RoundedRectangle

from questions import get_random_question
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


class Part1Screen(Screen):
    """Part 1 — short Q&A, timed answer."""

    def __init__(self, used_indices=None, **kwargs):
        super().__init__(**kwargs)
        self.used_indices = used_indices if used_indices is not None else set()
        self.current_idx = None
        self.current_question = None

        self.is_recording = False
        self.audio_frames = []
        self.stream = None
        self.timer_event = None
        self.seconds_left = PART_1_DURATION

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

        btn_row = BoxLayout(size_hint_y=None, height=dp(120))
        self.record_btn = Button(
            text="REC",
            size_hint=(None, None),
            size=(dp(100), dp(100)),
            pos_hint={"center_x": 0.5},
            background_normal="",
            background_color=CORAL,
            color=TEXT,
            font_size=dp(20),
            bold=True,
        )
        self.record_btn.bind(on_release=self._toggle_recording)
        btn_row.add_widget(self.record_btn)
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

        def callback(indata, frames, time_info, status):
            if status:
                print("Audio status:", status)
            self.audio_frames.append(indata.copy())

        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            callback=callback,
        )
        self.stream.start()

        self.timer_event = Clock.schedule_interval(self._tick, 1.0)

    def _tick(self, _dt):
        self.seconds_left -= 1
        self.timer_label.text = format_time(max(self.seconds_left, 0))
        if self.seconds_left <= 0:
            self._stop_recording()
            return False

    def _stop_recording(self):
        if not self.is_recording:
            return
        self.is_recording = False

        if self.timer_event is not None:
            self.timer_event.cancel()
            self.timer_event = None

        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        self.record_btn.text = "REC"

        if self.audio_frames:
            audio = np.concatenate(self.audio_frames, axis=0)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = RECORDINGS_DIR / ("part1_" + timestamp + ".wav")
            sf.write(str(filename), audio, SAMPLE_RATE)
            self.status_label.text = "Saved - " + filename.name
            self.next_btn.disabled = False
            self.next_btn.opacity = 1.0

            if self.current_idx is not None:
                self.used_indices.add(self.current_idx)
        else:
            self.status_label.text = "No audio captured"

    def _next_question(self, *_):
        self._load_question()

    def _go_home(self, *_):
        if self.is_recording:
            self._stop_recording()
        self.manager.current = "home"
