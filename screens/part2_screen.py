"""Part 2 Question screen for IELTS Speaking Coach.

Shows a cue card, runs a 60s prep phase with a notes area,
then records up to 2 minutes of the user's long turn.
Includes the shared circular REC button + voice-reactive ripple
(active only during the recording phase, never during prep).
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
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle

from questions import get_random_question
from sound import play_tap, play_click
from screens.recorder_widgets import CircleButton, RippleController
from theme import (
    BG,
    SURFACE,
    SURFACE2,
    BORDER,
    TEXT,
    MUTED,
    CORAL,
    EMERALD,
    VIOLET,
    LIME,
    PARTS,
    format_time,
)


SAMPLE_RATE = 44100
CHANNELS = 1
PREP_DURATION = 60  # seconds
TALK_DURATION = PARTS[2]["duration"]  # 120 seconds, from theme

# Phases
PHASE_IDLE = "idle"
PHASE_PREP = "prep"
PHASE_RECORDING = "recording"
PHASE_DONE = "done"

RECORDINGS_DIR = Path(__file__).resolve().parent.parent / "recordings"
RECORDINGS_DIR.mkdir(exist_ok=True)


class Part2Screen(Screen):
    """Part 2 — Long Turn cue card, 60s prep + 2min talk."""

    def __init__(self, used_indices=None, **kwargs):
        super().__init__(**kwargs)
        self.used_indices = used_indices if used_indices is not None else set()
        self.current_idx = None
        self.current_question = None

        self.phase = PHASE_IDLE
        self.audio_frames = []
        self.stream = None
        self.timer_event = None
        self.seconds_left = 0

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
            padding=[dp(20), dp(36), dp(20), dp(20)],
            spacing=dp(14),
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
            text="Part 2 - Long Turn",
            color=VIOLET,
            font_size=dp(13),
            bold=True,
            halign="right",
            valign="middle",
        )
        part_label.bind(size=lambda i, s: setattr(i, "text_size", s))
        top_bar.add_widget(back_btn)
        top_bar.add_widget(part_label)
        root.add_widget(top_bar)

        # Scrollable content area (cue card + cue points + notes)
        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            size_hint_y=None,
            padding=[0, 0, 0, dp(8)],
        )
        content.bind(minimum_height=content.setter("height"))

        # Cue card surface
        self.cue_card = BoxLayout(
            orientation="vertical",
            padding=[dp(18), dp(16)],
            spacing=dp(8),
            size_hint_y=None,
        )
        self.cue_card.bind(minimum_height=self.cue_card.setter("height"))
        with self.cue_card.canvas.before:
            Color(*SURFACE2)
            self._cue_rect = RoundedRectangle(
                pos=self.cue_card.pos,
                size=self.cue_card.size,
                radius=[dp(12)],
            )
        self.cue_card.bind(pos=self._sync_cue, size=self._sync_cue)

        self.topic_label = Label(
            text="",
            color=VIOLET,
            font_size=dp(12),
            bold=True,
            size_hint_y=None,
            height=dp(18),
            halign="left",
            valign="middle",
        )
        self.topic_label.bind(size=lambda i, s: setattr(i, "text_size", s))
        self.cue_card.add_widget(self.topic_label)

        self.main_prompt_label = Label(
            text="",
            color=TEXT,
            font_size=dp(20),
            bold=True,
            size_hint_y=None,
            halign="left",
            valign="top",
        )
        self.main_prompt_label.bind(
            width=lambda i, w: setattr(i, "text_size", (w, None)),
            texture_size=lambda i, ts: setattr(i, "height", ts[1] + dp(4)),
        )
        self.cue_card.add_widget(self.main_prompt_label)

        self.cue_points_label = Label(
            text="",
            color=MUTED,
            font_size=dp(14),
            size_hint_y=None,
            halign="left",
            valign="top",
        )
        self.cue_points_label.bind(
            width=lambda i, w: setattr(i, "text_size", (w, None)),
            texture_size=lambda i, ts: setattr(i, "height", ts[1] + dp(4)),
        )
        self.cue_card.add_widget(self.cue_points_label)

        content.add_widget(self.cue_card)

        # Tips block (small, dimmed)
        self.tips_label = Label(
            text="",
            color=MUTED,
            font_size=dp(12),
            size_hint_y=None,
            halign="left",
            valign="top",
        )
        self.tips_label.bind(
            width=lambda i, w: setattr(i, "text_size", (w, None)),
            texture_size=lambda i, ts: setattr(i, "height", ts[1] + dp(4)),
        )
        content.add_widget(self.tips_label)

        # Notes area (hidden until PREP starts)
        self.notes_container = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=0,  # collapsed by default
            spacing=dp(6),
            opacity=0,
        )

        self.notes_header = Label(
            text="YOUR NOTES",
            color=LIME,
            font_size=dp(11),
            bold=True,
            size_hint_y=None,
            height=dp(16),
            halign="left",
            valign="middle",
        )
        self.notes_header.bind(size=lambda i, s: setattr(i, "text_size", s))
        self.notes_container.add_widget(self.notes_header)

        self.notes_input = TextInput(
            text="",
            hint_text="Jot down ideas... where, who, what, why...",
            background_color=SURFACE,
            foreground_color=TEXT,
            cursor_color=LIME,
            hint_text_color=MUTED,
            font_size=dp(15),
            padding=[dp(12), dp(10), dp(12), dp(10)],
            size_hint_y=None,
            height=dp(160),
            multiline=True,
        )
        self.notes_container.add_widget(self.notes_input)

        content.add_widget(self.notes_container)

        scroll.add_widget(content)
        root.add_widget(scroll)

        # Timer
        self.timer_label = Label(
            text=format_time(PREP_DURATION),
            color=TEXT,
            font_size=dp(42),
            size_hint_y=None,
            height=dp(56),
            bold=True,
        )
        root.add_widget(self.timer_label)

        # Status text
        self.status_label = Label(
            text="Read the cue card carefully",
            color=MUTED,
            font_size=dp(13),
            size_hint_y=None,
            height=dp(20),
        )
        root.add_widget(self.status_label)

        # Action button (changes label based on phase) — circular REC
        btn_row = BoxLayout(size_hint_y=None, height=dp(120))
        btn_row.add_widget(Widget())
        self.record_btn = CircleButton(
            text="GO",
            bg_color=VIOLET,
            size_hint=(None, None),
            size=(dp(100), dp(100)),
            color=TEXT,
            font_size=dp(18),
            bold=True,
        )
        self.record_btn.bind(on_release=self._on_action)
        center_holder = BoxLayout(size_hint=(None, 1), width=dp(100))
        center_holder.add_widget(self.record_btn)
        btn_row.add_widget(center_holder)
        btn_row.add_widget(Widget())
        root.add_widget(btn_row)

        # Next button (hidden until DONE)
        self.next_btn = Button(
            text="Next cue card",
            size_hint_y=None,
            height=dp(48),
            background_normal="",
            background_color=EMERALD,
            color=TEXT,
            font_size=dp(15),
            disabled=True,
            opacity=0,
        )
        self.next_btn.bind(on_release=self._next_question)
        root.add_widget(self.next_btn)

        self.add_widget(root)

    def _update_bg(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _sync_cue(self, *_):
        self._cue_rect.pos = self.cue_card.pos
        self._cue_rect.size = self.cue_card.size

    # ------------------------------------------------------------
    # Question loading
    # ------------------------------------------------------------
    def _load_question(self):
        result = get_random_question(2, self.used_indices)
        if result is None:
            self.main_prompt_label.text = "You've answered all Part 2 cue cards!"
            self.topic_label.text = ""
            self.cue_points_label.text = ""
            self.tips_label.text = ""
            self.record_btn.disabled = True
            self.record_btn.opacity = 0.5
            return

        q, idx = result
        self.current_question = q
        self.current_idx = idx

        self.topic_label.text = "TOPIC - " + q["topic"].upper()
        self.main_prompt_label.text = q["main_prompt"]
        self.cue_points_label.text = "\n".join(q["cue_points"])
        self.tips_label.text = "Tips:\n" + "\n".join("- " + t for t in q["tips"])

        self._set_phase(PHASE_IDLE)

    # ------------------------------------------------------------
    # Phase management
    # ------------------------------------------------------------
    def _set_phase(self, phase):
        self.phase = phase

        if phase == PHASE_IDLE:
            self.timer_label.text = format_time(PREP_DURATION)
            self.status_label.text = "Read the cue card carefully"
            self.record_btn.text = "PREP"
            self.record_btn.set_bg(VIOLET)
            self.record_btn.disabled = False
            self.record_btn.opacity = 1
            self._collapse_notes()
            self.notes_input.text = ""
            self.next_btn.disabled = True
            self.next_btn.opacity = 0

        elif phase == PHASE_PREP:
            self.seconds_left = PREP_DURATION
            self.timer_label.text = format_time(PREP_DURATION)
            self.status_label.text = "Preparing - make some notes"
            self.record_btn.text = "REC"
            self.record_btn.set_bg(CORAL)
            self._expand_notes()
            self.timer_event = Clock.schedule_interval(self._tick_prep, 1.0)

        elif phase == PHASE_RECORDING:
            self.seconds_left = TALK_DURATION
            self.timer_label.text = format_time(TALK_DURATION)
            self.status_label.text = "Recording - speak now"
            self.record_btn.text = "STOP"
            self.record_btn.set_bg(CORAL)
            # Notes stay visible during recording (read-only)
            self.notes_input.readonly = True
            self._start_audio_stream()
            self.timer_event = Clock.schedule_interval(self._tick_record, 1.0)

        elif phase == PHASE_DONE:
            self.status_label.text = "Answer recorded"
            self.record_btn.disabled = True
            self.record_btn.opacity = 0.4
            self.record_btn.text = "DONE"
            self.next_btn.disabled = False
            self.next_btn.opacity = 1
            self.notes_input.readonly = True

    # ------------------------------------------------------------
    # Notes expand / collapse
    # ------------------------------------------------------------
    def _expand_notes(self):
        self.notes_container.height = dp(190)
        self.notes_container.opacity = 1
        self.notes_input.readonly = False

    def _collapse_notes(self):
        self.notes_container.height = 0
        self.notes_container.opacity = 0

    # ------------------------------------------------------------
    # Action button dispatcher
    # ------------------------------------------------------------
    def _on_action(self, *_):
        if self.phase == PHASE_IDLE:
            play_tap()
            self._set_phase(PHASE_PREP)
        elif self.phase == PHASE_PREP:
            play_tap()
            self._end_prep_early()
        elif self.phase == PHASE_RECORDING:
            self._stop_recording()

    def _end_prep_early(self):
        if self.timer_event is not None:
            self.timer_event.cancel()
            self.timer_event = None
        self._set_phase(PHASE_RECORDING)

    # ------------------------------------------------------------
    # Timer ticks
    # ------------------------------------------------------------
    def _tick_prep(self, _dt):
        self.seconds_left -= 1
        self.timer_label.text = format_time(max(self.seconds_left, 0))
        if self.seconds_left <= 0:
            self.timer_event = None
            self._set_phase(PHASE_RECORDING)
            return False

    def _tick_record(self, _dt):
        self.seconds_left -= 1
        self.timer_label.text = format_time(max(self.seconds_left, 0))
        self.timer_label.color = CORAL if self.seconds_left <= 10 else TEXT
        if self.seconds_left <= 0:
            self._stop_recording()
            return False

    # ------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------
    def _start_audio_stream(self):
        self.audio_frames = []

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
        # Ripple fires only during the recording phase
        self.ripple.start()

    def _stop_recording(self):
        if self.phase != PHASE_RECORDING:
            return

        if self.timer_event is not None:
            self.timer_event.cancel()
            self.timer_event = None

        self.ripple.stop()

        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        # Mic closed — safe to play the click
        play_click()

        if self.audio_frames:
            audio = np.concatenate(self.audio_frames, axis=0)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            wav_path = RECORDINGS_DIR / ("part2_" + timestamp + ".wav")
            sf.write(str(wav_path), audio, SAMPLE_RATE)

            # Save notes alongside the recording
            notes = self.notes_input.text.strip()
            if notes:
                txt_path = RECORDINGS_DIR / ("part2_" + timestamp + "_notes.txt")
                txt_path.write_text(notes, encoding="utf-8")

            if self.current_idx is not None:
                self.used_indices.add(self.current_idx)

        self._set_phase(PHASE_DONE)

    # ------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------
    def _next_question(self, *_):
        play_tap()
        self._load_question()

    def _go_home(self, *_):
        play_tap()
        # Clean up before leaving
        if self.timer_event is not None:
            self.timer_event.cancel()
            self.timer_event = None
        self.ripple.stop()
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self.manager.current = "home"
