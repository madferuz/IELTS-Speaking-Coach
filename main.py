"""IELTS Speaking Coach — app entry point."""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window

from theme import BG
from screens.home import HomeScreen
from screens.question_screen import Part1Screen
from screens.part2_screen import Part2Screen
from screens.part3_screen import Part3Screen
from screens.full_test import TestStartScreen, TestEndScreen


# Set window background to dark theme
Window.clearcolor = BG
# Mobile-like window size for development on Mac
Window.size = (400, 740)


class IELTSCoachApp(App):
    def build(self):
        self.title = "IELTS Speaking Coach"
        self.sm = ScreenManager(transition=SlideTransition(duration=0.3))

        # Tracks whether we're in a full mock test (vs single-part practice)
        self.test_mode = False
        self.test_step = 0  # 0 = part1, 1 = part2, 2 = part3

        # Home screen
        home = HomeScreen(
            name="home",
            on_part_selected=self.go_to_part,
            on_full_test=self.start_full_test,
        )
        self.sm.add_widget(home)

        # Part screens — each gets an on_complete hook used only in test mode.
        # In practice mode on_complete stays unused and they return home as before.
        self.part1 = Part1Screen(name="part1")
        self.part2 = Part2Screen(name="part2")
        self.part3 = Part3Screen(name="part3")
        for p in (self.part1, self.part2, self.part3):
            # Stage 3 will have the screens call self.on_test_complete when in test mode.
            p.on_test_complete = self.advance_test
            p.test_mode = False
        self.sm.add_widget(self.part1)
        self.sm.add_widget(self.part2)
        self.sm.add_widget(self.part3)

        # Full-test bookend screens
        self.sm.add_widget(TestStartScreen(
            name="test_start",
            on_begin=self.begin_test,
            on_cancel=self.go_home,
        ))
        self.sm.add_widget(TestEndScreen(
            name="test_end",
            on_home=self.go_home,
        ))

        return self.sm

    # ------------------------------------------------------------
    # Practice mode (single part)
    # ------------------------------------------------------------
    def go_to_part(self, part_id: int):
        """Practice a single part. Screens return to home when finished."""
        self.test_mode = False
        for p in (self.part1, self.part2, self.part3):
            p.test_mode = False
        self.sm.transition.direction = "left"
        if part_id == 1:
            self.sm.current = "part1"
        elif part_id == 2:
            self.sm.current = "part2"
        elif part_id == 3:
            self.sm.current = "part3"
        else:
            print(f"Unknown part_id: {part_id}")

    # ------------------------------------------------------------
    # Full test mode (all three parts in sequence)
    # ------------------------------------------------------------
    def start_full_test(self):
        """Show the test intro screen."""
        self.sm.transition.direction = "left"
        self.sm.current = "test_start"

    def begin_test(self):
        """User confirmed — enter test mode and launch Part 1."""
        self.test_mode = True
        self.test_step = 0
        for p in (self.part1, self.part2, self.part3):
            p.test_mode = True
        self.sm.transition.direction = "left"
        self.sm.current = "part1"

    def advance_test(self):
        """Called by a part screen (in test mode) when its recording is done."""
        if not self.test_mode:
            return
        self.test_step += 1
        self.sm.transition.direction = "left"
        if self.test_step == 1:
            self.sm.current = "part2"
        elif self.test_step == 2:
            self.sm.current = "part3"
        else:
            # Finished Part 3 — show the completion screen
            self.test_mode = False
            for p in (self.part1, self.part2, self.part3):
                p.test_mode = False
            self.sm.current = "test_end"

    def go_home(self):
        self.test_mode = False
        for p in (self.part1, self.part2, self.part3):
            p.test_mode = False
        self.sm.transition.direction = "right"
        self.sm.current = "home"


if __name__ == "__main__":
    IELTSCoachApp().run()
