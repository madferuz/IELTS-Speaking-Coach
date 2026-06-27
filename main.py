"""IELTS Speaking Coach — app entry point."""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.core.window import Window

from theme import BG
from screens.home import HomeScreen
from screens.question_screen import Part1Screen
from screens.part2_screen import Part2Screen
from screens.part3_screen import Part3Screen


# Set window background to dark theme
Window.clearcolor = BG
# Mobile-like window size for development on Mac
Window.size = (400, 740)


class IELTSCoachApp(App):
    def build(self):
        self.title = "IELTS Speaking Coach"
        self.sm = ScreenManager(transition=NoTransition())

        # Home screen
        home = HomeScreen(name="home", on_part_selected=self.go_to_part)
        self.sm.add_widget(home)

        # Part 1 - short Q&A
        self.sm.add_widget(Part1Screen(name="part1"))

        # Part 2 - cue card with prep + long turn
        self.sm.add_widget(Part2Screen(name="part2"))

        # Part 3 - discussion: main + 2 follow-ups
        self.sm.add_widget(Part3Screen(name="part3"))

        return self.sm

    def go_to_part(self, part_id: int):
        """Switch to the appropriate Question screen for the selected part."""
        if part_id == 1:
            self.sm.current = "part1"
        elif part_id == 2:
            self.sm.current = "part2"
        elif part_id == 3:
            self.sm.current = "part3"
        else:
            print(f"Unknown part_id: {part_id}")


if __name__ == "__main__":
    IELTSCoachApp().run()
