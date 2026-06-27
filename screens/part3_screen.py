"""Part 3 Question screen for IELTS Speaking Coach.

Discussion phase - one main question plus two follow-ups,
each with its own 45-second recording.
Includes the shared circular REC button + voice-reactive ripple,
reset cleanly between each of the three recordings.
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
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, RoundedRectangle

from questions import get_random_question
from sound import play_tap, play_click
from screens.recorder_widgets import CircleButton, RippleController
from theme import (
    BG,
    SURFACE2,
    TEXT,
    MUTED,
    CORAL,
    EMERALD,
    AMBER,
    PARTS,
    format_time,
)


SAMPLE_RATE = 44100
CHANNELS = 1
QUESTION_DURATION = 45  # seconds per question

RECORDINGS_DIR = Path(__file__).resolve().parent.parent / "recordings"
RECORDINGS_DIR.mkdir(exist_ok=True)


class Part3Screen(Screen):
    """Part 3 - Discussion: main question + 2 follow-ups, 45s each."""

    def __init__(self, used_indices=None, **kwargs):
        super().__init__(**kwargs)
        self.used_indices = used_indices if used_indices is not None else set()
        self.current_idx = None
        self.current_question = None

        # 0 = main, 1 = follow-up 1, 2 = follow-up 2, 3 = done
        self.question_step = 0
        self.session_timestamp = None  # shared across the 3 recordings

        # Recording state
        self.is_recording = False
        self.audio_frames = []
        self.stream = None
        self.timer_event = None
        self.seconds_left = QUESTION_DURATION

        self._build_ui()
        self.ripple = RippleController(self, self.record_btn)
        self._load_question()

    # ------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------
    def _build_ui(self):
        with self.canvas.before:
            Color(*BG)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[0])
        self.bind(pos=self._update_bg, size=self._update_bg)

        root = BoxLayout(
            orientation="vertical",
            padding=[dp(24), dp(36), dp(24), dp(28)],
            spacing=dp(16),
        )

        # Top bar
        top_bar = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(12))
        back_btn = Button(
            text="< Back",
            size_hint_x=None,
            width=dp(80),
            background_color=(0, 0, 0, 0),
            color=MUTED,
            font_size=dp(15),
        )
        back_btn.bind(on_release=self._go_home)
        part_label = Label(
            text="Part 3 - Discussion",
            color=AMBER,
            font_size=dp(13),
            bold=True,
            halign="right",
            valign="middle",
        )
        part_label.bind(size=lambda i, s: setattr(i, "text_size", s))
        top_bar.add_widget(back_btn)
        top_bar.add_widget(part_label)
        root.add_widget(top_bar)

        # Progress indicator (1 of 3, 2 of 3, 3 of 3)
        self.progress_label = Label(
            text="",
            color=AMBER,
            font_size=dp(12),
            bold=True,
            size_hint_y=None,
            height=dp(18),
            halign="center",
        )
        self.progress_label.bind(size=lambda i, s: setattr(i, "text_size", s))
        root.add_widget(self.progress_label)

        # Topic
        self.topic_label = Label(
            text="",
            color=MUTED,
            font_size=dp(13),
            size_hint_y=None,
            height=dp(22),
            halign="center",
        )
        self.topic_label.bind(size=lambda i, s: setattr(i, "text_size", s))
        root.add_widget(self.topic_label)

        # Question card surface
        self.q_card = BoxLayout(
            orientation="vertical",
            padding=[dp(18), dp(18)],
            spacing=dp(6),
            size_hint_y=None,
        )
        self.q_card.bind(minimum_height=self.q_card.setter("height"))
        with self.q_card.canvas.before:
            Color(*SURFACE2)
            self._q_rect = RoundedRectangle(
                pos=self.q_card.pos,
                size=self.q_card.size,
                radius=[dp(12)],
            )
        self.q_card.bind(pos=self._sync_q, size=self._sync_q)

        self.question_label = Label(
            text="",
            color=TEXT,
            font_size=dp(20),
            bold=True,
            size_hint_y=None,
            halign="center",
            valign="middle",
        )
        self.question_label.bind(
            width=lambda i, w: setattr(i, "text_size", (w, None)),
            texture_size=lambda i, ts: setattr(i, "height", ts[1] + dp(8)),
        )
        self.q_card.add_widget(self.question_label)

        root.add_widget(self.q_card)

        # Tips (shown only on main question)
        self.tips_label = Label(
            text="",
            color=MUTED,
            font_size=dp(12),
            size_hint_y=None,
            halign="center",
            valign="top",
        )
        self.tips_label.bind(
            width=lambda i, w: setattr(i, "text_size", (w, None)),
            texture_size=lambda i, ts: setattr(i, "height", ts[1] + dp(4)),
        )
        root.add_widget(self.tips_label)

        # Timer
        self.timer_label = Label(
            text=format_time(QUESTION_DURATION),
            color=TEXT,
            font_size=dp(46),
            size_hint_y=None,
            height=dp(64),
            bold=True,
        )
        root.add_widget(self.timer_label)

        # Record button — circular
        btn_row = BoxLayout(size_hint_y=None, height=dp(110))
        btn_row.add_widget(Widget())
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
        center_holder = BoxLayout(size_hint=(None, 1), width=dp(100))
        center_holder.add_widget(self.record_btn)
        btn_row.add_widget(center_holder)
        btn_row.add_widget(Widget())
        root.add_widget(btn_row)

        # Status text
        self.status_label = Label(
            text="Tap to start recording",
            color=MUTED,
            font_size=dp(13),
            size_hint_y=None,
            height=dp(22),
        )
        root.add_widget(self.status_label)

        # Continue button (changes label based on step)
        self.continue_btn = Button(
            text="Continue",
            size_hint_y=None,
            height=dp(48),
            background_normal="",
            background_color=EMERALD,
            color=TEXT,
            font_size=dp(15),
            bold=True,
            disabled=True,
            opacity=0.4,
        )
        self.continue_btn.bind(on_release=self._on_continue)
        root.add_widget(self.continue_btn)

        self.add_widget(root)

    def _update_bg(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _sync_q(self, *_):
        self._q_rect.pos = self.q_card.pos
        self._q_rect.size = self.q_card.size

    # ------------------------------------------------------------
    # Question loading
    # ------------------------------------------------------------
    def _load_question(self):
        """Pick a new discussion topic and reset to step 0 (main question)."""
        result = get_random_question(3, self.used_indices)
        if result is None:
            self.question_label.text = "You've answered all Part 3 discussions!"
            self.topic_label.text = ""
            self.progress_label.text = ""
            self.tips_label.text = ""
            self.record_btn.disabled = True
            self.record_btn.opacity = 0.4
            return

        q, idx = result
        self.current_question = q
        self.current_idx = idx
        self.question_step = 0
        self.session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.topic_label.text = "Topic - " + q["topic"]

        self._show_current_step()

    def _show_current_step(self):
        """Update the question display based on self.question_step."""
        q = self.current_question
        step = self.question_step

        if step == 0:
            self.progress_label.text = "QUESTION 1 OF 3 - MAIN"
            self.question_label.text = q["main_question"]
            self.tips_label.text = "\n".join("- " + t for t in q["tips"])
            self.continue_btn.text = "Continue to follow-up 1"
        elif step == 1:
            self.progress_label.text = "QUESTION 2 OF 3 - FOLLOW-UP"
            self.question_label.text = q["follow_ups"][0]
            self.tips_label.text = ""
            self.continue_btn.text = "Continue to follow-up 2"
        elif step == 2:
            self.progress_label.text = "QUESTION 3 OF 3 - FOLLOW-UP"
            self.question_label.text = q["follow_ups"][1]
            self.tips_label.text = ""
            self.continue_btn.text = "Next discussion"
        else:
            return

        # Reset per-question state
        self.timer_label.text = format_time(QUESTION_DURATION)
        self.seconds_left = QUESTION_DURATION
        self.status_label.text = "Tap to start recording"
        self.record_btn.disabled = False
        self.record_btn.opacity = 1
        self.record_btn.text = "REC"
        self.continue_btn.disabled = True
        self.continue_btn.opacity = 0.4

    # ------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------
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
        self.seconds_left = QUESTION_DURATION
        self.continue_btn.disabled = True
        self.continue_btn.opacity = 0.4

        def callback(indata, frames, time_info, status):
            if status:
                print("Audio status:", status)
            self.audio_frames.append(indata.copy())
            try:
                self.ripple.level = float(np.sqrt(np.mean(indata.astype(np.float64) ** 2)))
            except Exception:
                self.ripple.level = 0.0

        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            callback=callback,
        )
        self.stream.start()
        self.timer_event = Clock.schedule_interval(self._tick, 1.0)
        self.ripple.start()

    def _tick(self, _dt):
        self.seconds_left -= 1
        self.timer_label.text = format_time(max(self.seconds_left, 0))
        self.timer_label.color = CORAL if self.seconds_left <= 10 else TEXT
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

        self.ripple.stop()

        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        play_click()

        self.record_btn.text = "REC"

        if self.audio_frames:
            audio = np.concatenate(self.audio_frames, axis=0)
            step_labels = ["main", "followup1", "followup2"]
            label = step_labels[self.question_step]
            filename = RECORDINGS_DIR / (
                "part3_" + self.session_timestamp + "_" + label + ".wav"
            )
            sf.write(str(filename), audio, SAMPLE_RATE)
            self.status_label.text = "Answer recorded"
            self.continue_btn.disabled = False
            self.continue_btn.opacity = 1.0
        else:
            self.status_label.text = "No audio captured - tap REC again"

    # ------------------------------------------------------------
    # Continue / navigation between questions
    # ------------------------------------------------------------
    def _on_continue(self, *_):
        play_tap()
        if self.question_step < 2:
            # Move to next question in this discussion
            self.question_step += 1
            self._show_current_step()
        else:
            # Finished all 3 - mark used and load a new discussion
            if self.current_idx is not None:
                self.used_indices.add(self.current_idx)
            self._load_question()

    def _go_home(self, *_):
        play_tap()
        if self.is_recording:
            self._stop_recording()
        if self.timer_event is not None:
            self.timer_event.cancel()
            self.timer_event = None
        self.ripple.stop()
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self.manager.current = "home"
