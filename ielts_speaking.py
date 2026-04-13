import customtkinter as ctk
import anthropic
import json
import threading
import time
import re
import random

# ── Theme ──────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Palette ────────────────────────────────────────────────────────────────
BG      = "#0F1117"
SURFACE = "#1A1D27"
SURFACE2= "#22263A"
BORDER  = "#2E334D"
ACCENT  = "#4A7CF7"
ACCENT2 = "#6C9FFF"
GREEN   = "#3DBE7A"
AMBER   = "#F5A623"
TEXT    = "#E8EAF6"
MUTED   = "#7B82A8"
DANGER  = "#E05C5C"

# ── Question Bank ──────────────────────────────────────────────────────────
QUESTION_BANK = {
    1: [
        {"topic": "Home", "question": "Can you describe the area where you currently live?",
         "tips": ["Use descriptive adjectives to paint a vivid picture.", "Mention both positive and negative aspects for balance.", "Add personal feelings to make your answer more engaging."]},
        {"topic": "Home", "question": "Do you prefer living in a house or an apartment? Why?",
         "tips": ["Give clear reasons for your preference.", "Use comparative language like 'more', 'less', 'rather than'.", "Include a personal anecdote if possible."]},
        {"topic": "Work & Study", "question": "Do you work or are you a student? What do you enjoy most about it?",
         "tips": ["Be specific — avoid vague answers like 'it's interesting'.", "Mention a particular task, subject, or moment you enjoy.", "Show enthusiasm through your tone and word choice."]},
        {"topic": "Work & Study", "question": "Would you like to change your job or field of study in the future?",
         "tips": ["Explain the reason behind your answer clearly.", "Use future tenses confidently: 'I would like to', 'I'm planning to'.", "Mention what skills or opportunities attract you."]},
        {"topic": "Hobbies", "question": "What do you like to do in your free time?",
         "tips": ["Don't just list hobbies — describe one in detail.", "Explain why this hobby matters to you.", "Use time expressions: 'whenever I can', 'at least twice a week'."]},
        {"topic": "Hobbies", "question": "Have your hobbies changed since you were a child?",
         "tips": ["Use past and present tenses to contrast then and now.", "Give a specific example of a childhood hobby.", "Explain what caused the change."]},
        {"topic": "Food", "question": "What is your favourite food and why do you enjoy it?",
         "tips": ["Use sensory language: taste, smell, texture.", "Mention where or when you typically eat it.", "Talk about any cultural or emotional connection to the dish."]},
        {"topic": "Food", "question": "Do you prefer eating at home or at a restaurant?",
         "tips": ["Give at least two reasons for your preference.", "Use contrast: 'whereas', 'on the other hand'.", "Keep your answer conversational, not like a list."]},
        {"topic": "Travel", "question": "Do you enjoy travelling? Where have you been recently?",
         "tips": ["Describe a specific trip rather than talking in general.", "Use past tenses accurately when talking about past trips.", "Express emotions: excitement, surprise, disappointment."]},
        {"topic": "Travel", "question": "Do you prefer travelling alone or with others?",
         "tips": ["Compare both options before giving your preference.", "Use personal experience to support your point.", "Vary your vocabulary: 'solo travel', 'group trip', 'companions'."]},
        {"topic": "Music", "question": "What kind of music do you enjoy listening to?",
         "tips": ["Describe a specific genre or artist you love.", "Talk about when and where you typically listen to music.", "Mention how music makes you feel."]},
        {"topic": "Music", "question": "Did you learn to play any musical instruments when you were young?",
         "tips": ["Answer directly, then elaborate with details.", "Use past tenses accurately.", "If you didn't play, explain what you did instead."]},
        {"topic": "Technology", "question": "How often do you use your smartphone during the day?",
         "tips": ["Give specific numbers or time frames.", "Mention both work-related and personal uses.", "Reflect on whether you think it's too much or just right."]},
        {"topic": "Technology", "question": "Do you think people today are too dependent on technology?",
         "tips": ["Present a balanced view before giving your opinion.", "Use hedging language: 'it seems', 'to some extent'.", "Support with a concrete real-life example."]},
        {"topic": "Weather", "question": "What kind of weather do you prefer and why?",
         "tips": ["Use vivid descriptive language for weather conditions.", "Link your preference to activities you enjoy.", "Mention how weather affects your mood."]},
        {"topic": "Sports", "question": "Do you enjoy watching or playing sports?",
         "tips": ["Be specific about which sport and why.", "If you play, describe your level or frequency.", "Talk about how it benefits you physically or mentally."]},
        {"topic": "Reading", "question": "Do you enjoy reading books? What kind of books do you read?",
         "tips": ["Name a specific book or author you like.", "Explain why you prefer that genre.", "Mention how often you read and in what setting."]},
        {"topic": "Friends", "question": "How important are friends to you?",
         "tips": ["Go beyond saying 'very important' — explain why.", "Give an example of how a friend has supported you.", "Use emotive language to show genuine feeling."]},
        {"topic": "Daily Routine", "question": "Can you describe a typical day in your life?",
         "tips": ["Structure your answer chronologically.", "Use time markers: 'first', 'then', 'after that', 'finally'.", "Highlight one part of your day you particularly enjoy."]},
        {"topic": "Transport", "question": "How do you usually get around your city?",
         "tips": ["Mention the mode of transport and why you chose it.", "Compare different options available to you.", "Comment on convenience, cost, or environmental impact."]},
    ],
    2: [
        {"topic": "A Person", "main_prompt": "Describe a person who has had a great influence on your life.",
         "cue_points": ["You should say:", "who this person is", "how long you have known them", "what qualities they have", "and explain why they have been so influential to you."],
         "tips": ["Spend your 1-minute prep time jotting down key points.", "Speak for the full 2 minutes — keep adding details.", "End with a strong concluding sentence."]},
        {"topic": "A Place", "main_prompt": "Describe a place you have visited that you particularly enjoyed.",
         "cue_points": ["You should say:", "where the place is", "when you went there", "what you did or saw there", "and explain why you enjoyed it so much."],
         "tips": ["Use sensory details — sights, sounds, smells.", "Give a personal reaction, not just a description.", "Use past tenses consistently throughout."]},
        {"topic": "An Object", "main_prompt": "Describe an object that is very important to you.",
         "cue_points": ["You should say:", "what the object is", "how long you have had it", "what you use it for", "and explain why it is so important to you."],
         "tips": ["Focus on personal significance, not just function.", "Include where you got the object or who gave it to you.", "Use a variety of adjectives to describe it vividly."]},
        {"topic": "An Event", "main_prompt": "Describe a memorable event from your childhood.",
         "cue_points": ["You should say:", "what the event was", "when and where it happened", "who was involved", "and explain why it is so memorable to you."],
         "tips": ["Tell it like a story — set the scene first.", "Include how you felt at the time and how you feel now.", "Use narrative past tenses: simple past and past continuous."]},
        {"topic": "A Book or Film", "main_prompt": "Describe a book or film that you found very interesting.",
         "cue_points": ["You should say:", "what the book or film is called", "what it is about", "when you read or watched it", "and explain why you found it so interesting."],
         "tips": ["Give a brief plot summary before your personal reaction.", "Mention a specific scene or moment that stood out.", "Avoid spoilers — keep the suspense if relevant."]},
        {"topic": "A Skill", "main_prompt": "Describe a skill you would like to learn in the future.",
         "cue_points": ["You should say:", "what the skill is", "why you want to learn it", "how you plan to learn it", "and explain how it would benefit your life."],
         "tips": ["Use conditional and future tenses confidently.", "Be specific: instead of 'a language', say 'Japanese'.", "Link the skill to your personal goals or interests."]},
        {"topic": "An Achievement", "main_prompt": "Describe a personal achievement that you are proud of.",
         "cue_points": ["You should say:", "what you achieved", "when it happened", "what challenges you faced", "and explain why you are so proud of it."],
         "tips": ["Show emotion — pride, relief, satisfaction.", "Describe the journey, not just the result.", "Use the past perfect to show sequence: 'after I had studied...'"]},
        {"topic": "A Tradition", "main_prompt": "Describe a tradition or custom in your country that you find interesting.",
         "cue_points": ["You should say:", "what the tradition is", "when and how it is celebrated", "who takes part in it", "and explain why you find it interesting."],
         "tips": ["Give cultural context so the examiner understands it fully.", "Use present simple for things that happen regularly.", "Add your personal feelings about the tradition."]},
        {"topic": "A Journey", "main_prompt": "Describe an interesting journey you have made.",
         "cue_points": ["You should say:", "where you went", "how you travelled", "who you were with", "and explain what made the journey interesting."],
         "tips": ["Include unexpected moments or surprises.", "Use transition words to guide the examiner through the story.", "End with what you learned or how you felt afterwards."]},
        {"topic": "A Goal", "main_prompt": "Describe a goal you hope to achieve in the next five years.",
         "cue_points": ["You should say:", "what the goal is", "why you want to achieve it", "what steps you are taking towards it", "and explain how achieving it would change your life."],
         "tips": ["Be ambitious but realistic — examiners appreciate authenticity.", "Use a mix of present and future tenses.", "Show self-awareness about challenges you may face."]},
    ],
    3: [
        {"topic": "Education", "main_question": "Do you think the education system in your country prepares young people well for adult life?",
         "follow_ups": ["Should schools focus more on practical life skills rather than academic knowledge?", "How has technology changed the way people learn in recent years?"],
         "tips": ["Structure your answer: opinion → reason → example → conclusion.", "Use discourse markers: 'In my view', 'On the other hand', 'For instance'.", "Don't be afraid to present a nuanced or complex opinion."]},
        {"topic": "Environment", "main_question": "How responsible do you think individuals are for protecting the environment?",
         "follow_ups": ["Should governments impose stricter penalties on companies that pollute?", "Do you think people today are more or less environmentally aware than previous generations?"],
         "tips": ["Balance individual and collective responsibility in your answer.", "Use modal verbs for suggestions: 'could', 'should', 'might'.", "Give real-world examples to support your argument."]},
        {"topic": "Technology & Society", "main_question": "In what ways has technology changed the way people communicate with each other?",
         "follow_ups": ["Do you think social media has had a positive or negative impact on society overall?", "How might communication change further in the next 20 years?"],
         "tips": ["Consider both positive and negative impacts for a balanced answer.", "Use speculative language for the future: 'It's possible that', 'I imagine'.", "Link your ideas clearly between sentences."]},
        {"topic": "Work & Economy", "main_question": "Do you think the nature of work will change significantly in the next decade?",
         "follow_ups": ["Should employees have the right to work from home permanently?", "How can governments support workers whose jobs are replaced by automation?"],
         "tips": ["Refer to current trends to make your answer feel relevant.", "Use passive voice where appropriate: 'Jobs are being replaced by...'", "Show that you can think critically about economic and social issues."]},
        {"topic": "Health", "main_question": "Who do you think is most responsible for maintaining people's health — individuals or governments?",
         "follow_ups": ["Should unhealthy food and drinks be taxed more heavily?", "How has people's understanding of health and wellbeing changed over time?"],
         "tips": ["Explore multiple perspectives before giving your opinion.", "Use hedging language: 'To a large extent', 'It could be argued that'.", "Mention statistics or facts you know to add credibility."]},
        {"topic": "Culture & Globalisation", "main_question": "Do you think globalisation is causing local cultures to disappear?",
         "follow_ups": ["Is it important for countries to preserve their traditional cultures? Why?", "How can people maintain their cultural identity while embracing globalisation?"],
         "tips": ["Define key terms briefly: What do you mean by 'culture'?", "Give specific examples from countries you know.", "Show awareness of different viewpoints across generations."]},
        {"topic": "Media", "main_question": "To what extent do you think the media influences people's opinions and behaviour?",
         "follow_ups": ["Should governments regulate what is published on social media platforms?", "How can people critically evaluate the information they consume online?"],
         "tips": ["Distinguish between traditional media and social media in your answer.", "Use examples of real media influence you have observed.", "Consider the role of education in developing media literacy."]},
        {"topic": "Cities & Urban Life", "main_question": "What are the main challenges facing cities today?",
         "follow_ups": ["Do you think people will continue to move from rural areas to cities in the future?", "How can urban planners make cities more liveable for their residents?"],
         "tips": ["Cover a range of challenges: transport, housing, pollution, inequality.", "Prioritise — which challenge do you think is most serious and why?", "Use cause and effect language: 'This leads to', 'As a result'."]},
        {"topic": "Family & Society", "main_question": "How has the role of the family changed in modern society?",
         "follow_ups": ["Do you think strong family bonds are less important to younger generations today?", "What responsibilities do adult children have towards their ageing parents?"],
         "tips": ["Compare family structures across different generations or cultures.", "Use present perfect to show change over time: 'Families have become...'", "Acknowledge that experiences vary widely across different societies."]},
        {"topic": "Crime & Justice", "main_question": "What do you think are the most effective ways to reduce crime in society?",
         "follow_ups": ["Should the focus of the justice system be on punishment or rehabilitation?", "How does poverty contribute to crime, and what can be done about it?"],
         "tips": ["Don't just list solutions — evaluate how effective each one is.", "Use concessive language: 'Although punishment may deter crime...'", "Show awareness of the root causes, not just symptoms."]},
    ]
}

_used_indices = {1: set(), 2: set(), 3: set()}

def get_random_question(part):
    bank = QUESTION_BANK[part]
    available = [i for i in range(len(bank)) if i not in _used_indices[part]]
    if not available:
        return None
    idx = random.choice(available)
    _used_indices[part].add(idx)
    return bank[idx]

def reset_used(part):
    _used_indices[part].clear()

# ── AI prompts ─────────────────────────────────────────────────────────────
PARTS = {
    1: {"label": "Part 1", "name": "Introduction & Interview", "desc": "Familiar topics · ~4 min", "color": ACCENT, "duration": 60,
        "prompt": 'Generate an IELTS Speaking Part 1 question about a familiar topic.\nReturn ONLY valid JSON, no markdown fences:\n{"topic":"short topic","question":"the question","tips":["tip1","tip2","tip3"]}'},
    2: {"label": "Part 2", "name": "Individual Long Turn", "desc": "Cue card · speak 1–2 min", "color": GREEN, "duration": 120,
        "prompt": 'Generate an IELTS Speaking Part 2 cue card task.\nReturn ONLY valid JSON, no markdown fences:\n{"topic":"short topic","main_prompt":"Describe [something]...","cue_points":["You should say:","point1","point2","point3","and explain..."],"tips":["tip1","tip2"]}'},
    3: {"label": "Part 3", "name": "Two-way Discussion", "desc": "Abstract topics · ~5 min", "color": AMBER, "duration": 60,
        "prompt": 'Generate an IELTS Speaking Part 3 question set.\nReturn ONLY valid JSON, no markdown fences:\n{"topic":"short topic","main_question":"abstract question","follow_ups":["follow-up 1","follow-up 2"],"tips":["tip1","tip2"]}'},
}

def clean_json(text):
    text = re.sub(r"```json|```", "", text).strip()
    return json.loads(text)

# ── App ────────────────────────────────────────────────────────────────────
class IELTSApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("IELTS Speaking Coach")
        self.geometry("520x720")
        self.resizable(False, False)
        self.configure(fg_color=BG)
        self.client = anthropic.Anthropic()
        self._current_part = None
        self._question_data = None
        self._source = "bank"
        self._timer_val = 0
        self._timer_max = 60
        self._timer_running = False
        self._timer_thread = None
        self._build_ui()
        self._show_home()

    def _build_ui(self):
        self.header = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0, height=64)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)
        self.btn_back = ctk.CTkButton(self.header, text="‹  Back", width=80, height=32,
            fg_color="transparent", hover_color=SURFACE2, text_color=MUTED,
            font=ctk.CTkFont(size=14), command=self._show_home)
        self.btn_back.place(x=12, y=16)
        self.lbl_title = ctk.CTkLabel(self.header, text="IELTS Speaking Coach",
            font=ctk.CTkFont(size=17, weight="bold"), text_color=TEXT)
        self.lbl_title.place(relx=0.5, rely=0.5, anchor="center")
        self.lbl_sub = ctk.CTkLabel(self.header, text="AI-powered practice",
            font=ctk.CTkFont(size=11), text_color=MUTED)
        self.lbl_sub.place(relx=0.5, rely=0.78, anchor="center")
        self.content = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0)
        self.content.pack(fill="both", expand=True)
        self.footer = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0, height=72)
        self.footer.pack(fill="x", side="bottom")
        self.footer.pack_propagate(False)
        self.btn_new = ctk.CTkButton(self.footer, text="↺  New Question", width=160, height=40,
            fg_color=SURFACE2, hover_color=BORDER, text_color=TEXT,
            font=ctk.CTkFont(size=13), corner_radius=8, command=self._generate_question)
        self.btn_new.place(x=16, rely=0.5, anchor="w")
        self.btn_timer = ctk.CTkButton(self.footer, text="▶  Start Timer", width=160, height=40,
            fg_color=ACCENT, hover_color=ACCENT2, text_color="white",
            font=ctk.CTkFont(size=13, weight="bold"), corner_radius=8, command=self._toggle_timer)
        self.btn_timer.place(relx=1, x=-16, rely=0.5, anchor="e")
        ctk.CTkLabel(self.footer, text="developed by Madrakhimov",
            font=ctk.CTkFont(size=10), text_color=MUTED).place(relx=0.5, rely=0.88, anchor="center")

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _show_home(self):
        self._stop_timer()
        self._current_part = None
        self._question_data = None
        self._clear_content()
        self.btn_back.place_forget()
        self.lbl_title.configure(text="IELTS Speaking Coach")
        self.lbl_sub.configure(text="AI-powered practice")
        self.footer.pack_forget()

        hero = ctk.CTkFrame(self.content, fg_color="transparent")
        hero.pack(fill="x", padx=24, pady=(28, 8))
        ctk.CTkLabel(hero, text="Practice your", font=ctk.CTkFont(size=22), text_color=MUTED).pack(anchor="w")
        ctk.CTkLabel(hero, text="Speaking Test", font=ctk.CTkFont(size=30, weight="bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(hero, text="Select a part below. Questions are drawn from a\nbuilt-in bank, with AI backup when it runs out.",
            font=ctk.CTkFont(size=13), text_color=MUTED, justify="left").pack(anchor="w", pady=(6, 0))
        ctk.CTkLabel(hero, text="developed by Madrakhimov",
            font=ctk.CTkFont(size=10), text_color=BORDER).pack(anchor="w", pady=(10, 0))

        ctk.CTkFrame(self.content, fg_color=BORDER, height=1).pack(fill="x", padx=24, pady=16)
        ctk.CTkLabel(self.content, text="CHOOSE A PART",
            font=ctk.CTkFont(size=10, weight="bold"), text_color=MUTED).pack(anchor="w", padx=24)

        for part_id, pt in PARTS.items():
            self._part_card(self.content, part_id, pt)

        ctk.CTkFrame(self.content, fg_color=BORDER, height=1).pack(fill="x", padx=24, pady=16)
        ctk.CTkLabel(self.content, text="GENERAL TIPS",
            font=ctk.CTkFont(size=10, weight="bold"), text_color=MUTED).pack(anchor="w", padx=24)
        for tip in ["Speak at a natural pace — avoid rushing or long pauses.",
                    "Use varied vocabulary and a range of grammatical structures.",
                    "Extend answers with reasons, examples, and personal experience."]:
            row = ctk.CTkFrame(self.content, fg_color="transparent")
            row.pack(fill="x", padx=24, pady=3)
            ctk.CTkLabel(row, text="→", text_color=ACCENT, font=ctk.CTkFont(size=13), width=18).pack(side="left", anchor="n", pady=1)
            ctk.CTkLabel(row, text=tip, text_color=MUTED, font=ctk.CTkFont(size=13), justify="left", wraplength=380).pack(side="left", padx=6)
        ctk.CTkFrame(self.content, fg_color="transparent", height=24).pack()

    def _part_card(self, parent, part_id, pt):
        bank_count = len(QUESTION_BANK[part_id])
        used_count = len(_used_indices[part_id])
        remaining = bank_count - used_count
        card = ctk.CTkFrame(parent, fg_color=SURFACE, corner_radius=12, border_width=1, border_color=BORDER)
        card.pack(fill="x", padx=24, pady=6)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=14)
        dot = ctk.CTkFrame(inner, fg_color=pt["color"], width=10, height=10, corner_radius=5)
        dot.pack(side="left", padx=(0, 12), pady=4)
        dot.pack_propagate(False)
        info = ctk.CTkFrame(inner, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(info, text=f"{pt['label']}  ·  {pt['name']}",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT, anchor="w").pack(fill="x")
        ctk.CTkLabel(info, text=f"{pt['desc']}  ·  {remaining}/{bank_count} questions left",
            font=ctk.CTkFont(size=12), text_color=MUTED, anchor="w").pack(fill="x")
        ctk.CTkLabel(inner, text="›", font=ctk.CTkFont(size=20), text_color=MUTED).pack(side="right")
        for w in [card, inner, info, dot]:
            w.bind("<Button-1>", lambda e, pid=part_id: self._select_part(pid))
            w.bind("<Enter>", lambda e, c=card: c.configure(border_color=ACCENT))
            w.bind("<Leave>", lambda e, c=card: c.configure(border_color=BORDER))

    def _select_part(self, part_id):
        self._current_part = part_id
        pt = PARTS[part_id]
        self._timer_val = pt["duration"]
        self._timer_max = pt["duration"]
        self.btn_back.place(x=12, y=16)
        self.lbl_title.configure(text=pt["name"])
        self.lbl_sub.configure(text=pt["label"])
        self.footer.pack(fill="x", side="bottom")
        self.btn_timer.configure(text="▶  Start Timer", fg_color=ACCENT)
        self._load_next_question()

    def _generate_question(self):
        if self._current_part is None:
            return
        self._stop_timer()
        self._load_next_question()

    def _load_next_question(self):
        self._stop_timer()
        q = get_random_question(self._current_part)
        if q is not None:
            self._source = "bank"
            self._question_data = q
            pt = PARTS[self._current_part]
            self._timer_val = pt["duration"]
            self._timer_max = pt["duration"]
            self.btn_timer.configure(text="▶  Start Timer", fg_color=ACCENT)
            self._render_question()
        else:
            self._source = "ai"
            self._show_loading()
            threading.Thread(target=self._fetch_ai_question, daemon=True).start()

    def _show_loading(self):
        self._clear_content()
        box = ctk.CTkFrame(self.content, fg_color="transparent")
        box.pack(expand=True, pady=100)
        ctk.CTkLabel(box, text="⏳", font=ctk.CTkFont(size=36)).pack()
        ctk.CTkLabel(box, text="Bank exhausted — generating with AI…",
            font=ctk.CTkFont(size=14), text_color=MUTED).pack(pady=8)
        ctk.CTkLabel(box, text="All built-in questions used.\nTap 'Reset bank' to reuse them.",
            font=ctk.CTkFont(size=11), text_color=BORDER, wraplength=340, justify="center").pack()

    def _fetch_ai_question(self):
        pt = PARTS[self._current_part]
        try:
            msg = self.client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=800,
                messages=[{"role": "user", "content": pt["prompt"]}],
            )
            raw = msg.content[0].text
            data = clean_json(raw)
            self._question_data = data
            self._timer_val = pt["duration"]
            self._timer_max = pt["duration"]
            self.after(0, self._render_question)
        except Exception as e:
            err_msg = str(e)
            self.after(0, lambda: self._show_error(err_msg))

    def _show_error(self, msg):
        self._clear_content()
        box = ctk.CTkFrame(self.content, fg_color=SURFACE, corner_radius=12, border_width=1, border_color=DANGER)
        box.pack(fill="x", padx=24, pady=32)
        ctk.CTkLabel(box, text="⚠  Error", font=ctk.CTkFont(size=14, weight="bold"), text_color=DANGER).pack(padx=16, pady=(14, 4), anchor="w")
        ctk.CTkLabel(box, text=msg, text_color=MUTED, font=ctk.CTkFont(size=12), wraplength=400, justify="left").pack(padx=16, pady=(0, 10), anchor="w")
        ctk.CTkButton(box, text="↺  Reset question bank", width=200, height=36,
            fg_color=SURFACE2, hover_color=BORDER, text_color=TEXT,
            font=ctk.CTkFont(size=13), corner_radius=8, command=self._reset_bank).pack(padx=16, pady=(0, 14))

    def _reset_bank(self):
        if self._current_part:
            reset_used(self._current_part)
            self._load_next_question()

    def _render_question(self):
        self._clear_content()
        q = self._question_data
        pt = PARTS[self._current_part]
        color = pt["color"]

        self.timer_bar_bg = ctk.CTkFrame(self.content, fg_color=SURFACE2, height=4, corner_radius=2)
        self.timer_bar_bg.pack(fill="x")
        self.timer_bar = ctk.CTkFrame(self.timer_bar_bg, fg_color=color, height=4, corner_radius=2)
        self.timer_bar.place(relx=0, rely=0, relwidth=1.0, relheight=1.0)

        meta_row = ctk.CTkFrame(self.content, fg_color="transparent")
        meta_row.pack(fill="x", padx=20, pady=(6, 0))
        src_color = MUTED if self._source == "bank" else AMBER
        src_text  = "📚 From question bank" if self._source == "bank" else "✨ AI generated"
        ctk.CTkLabel(meta_row, text=src_text, font=ctk.CTkFont(size=11), text_color=src_color).pack(side="left")
        self.timer_lbl = ctk.CTkLabel(meta_row, text=self._fmt_time(self._timer_val),
            font=ctk.CTkFont(size=12), text_color=MUTED)
        self.timer_lbl.pack(side="right")

        if q.get("topic"):
            tag_row = ctk.CTkFrame(self.content, fg_color="transparent")
            tag_row.pack(anchor="w", padx=24, pady=(10, 0))
            tag = ctk.CTkFrame(tag_row, fg_color=SURFACE2, corner_radius=20, border_width=1, border_color=BORDER)
            tag.pack(side="left")
            ctk.CTkLabel(tag, text=f"  {q['topic']}  ", font=ctk.CTkFont(size=11), text_color=MUTED).pack()

        if self._current_part == 1:
            self._render_part1(q, color)
        elif self._current_part == 2:
            self._render_part2(q, color)
        elif self._current_part == 3:
            self._render_part3(q, color)

        if q.get("tips"):
            self._render_tips(q["tips"], color)

        # Status row
        bank = QUESTION_BANK[self._current_part]
        remaining = len(bank) - len(_used_indices[self._current_part])
        status = f"{remaining} question{'s' if remaining != 1 else ''} remaining in bank"
        if remaining == 0:
            status = "Bank exhausted — next tap will use AI"
        ctk.CTkLabel(self.content, text=status, font=ctk.CTkFont(size=11), text_color=BORDER).pack(pady=(10, 0))
        ctk.CTkButton(self.content, text="Reset bank", width=100, height=26,
            fg_color="transparent", hover_color=SURFACE2, text_color=MUTED,
            font=ctk.CTkFont(size=11), command=self._reset_bank).pack(pady=(2, 0))
        ctk.CTkFrame(self.content, fg_color="transparent", height=20).pack()

    def _section_label(self, text, color=None):
        ctk.CTkLabel(self.content, text=text, font=ctk.CTkFont(size=10, weight="bold"),
            text_color=color or MUTED).pack(anchor="w", padx=24, pady=(16, 4))

    def _card(self):
        f = ctk.CTkFrame(self.content, fg_color=SURFACE, corner_radius=12, border_width=1, border_color=BORDER)
        f.pack(fill="x", padx=24, pady=4)
        return f

    def _render_part1(self, q, color):
        self._section_label("QUESTION", color)
        card = self._card()
        ctk.CTkLabel(card, text=q.get("question", ""),
            font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT,
            wraplength=420, justify="left").pack(padx=18, pady=18, anchor="w")

    def _render_part2(self, q, color):
        self._section_label("CUE CARD", color)
        card = self._card()
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=18, pady=14)
        ctk.CTkLabel(inner, text=q.get("main_prompt", ""),
            font=ctk.CTkFont(size=15, weight="bold"), text_color=TEXT,
            wraplength=400, justify="left").pack(anchor="w", pady=(0, 10))
        for pt in q.get("cue_points", []):
            row = ctk.CTkFrame(inner, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text="–", text_color=color, font=ctk.CTkFont(size=13), width=14).pack(side="left", anchor="n", pady=1)
            ctk.CTkLabel(row, text=pt, text_color=MUTED, font=ctk.CTkFont(size=13), wraplength=380, justify="left").pack(side="left", padx=6)

    def _render_part3(self, q, color):
        self._section_label("MAIN QUESTION", color)
        card = self._card()
        ctk.CTkLabel(card, text=q.get("main_question", ""),
            font=ctk.CTkFont(size=15, weight="bold"), text_color=TEXT,
            wraplength=420, justify="left").pack(padx=18, pady=16, anchor="w")
        follow_ups = q.get("follow_ups", [])
        if follow_ups:
            self._section_label("FOLLOW-UP QUESTIONS", color)
            for i, fu in enumerate(follow_ups, 1):
                card = self._card()
                inner = ctk.CTkFrame(card, fg_color="transparent")
                inner.pack(fill="x", padx=16, pady=12)
                ctk.CTkLabel(inner, text=f"#{i}", font=ctk.CTkFont(size=10, weight="bold"), text_color=color).pack(anchor="w")
                ctk.CTkLabel(inner, text=fu, text_color=TEXT, font=ctk.CTkFont(size=13), wraplength=400, justify="left").pack(anchor="w", pady=(3, 0))

    def _render_tips(self, tips, color):
        self._section_label("SPEAKING TIPS", color)
        card = self._card()
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)
        for tip in tips:
            row = ctk.CTkFrame(inner, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text="→", text_color=color, font=ctk.CTkFont(size=12), width=16).pack(side="left", anchor="n", pady=1)
            ctk.CTkLabel(row, text=tip, text_color=MUTED, font=ctk.CTkFont(size=12), wraplength=390, justify="left").pack(side="left", padx=6)

    def _fmt_time(self, secs):
        m, s = divmod(int(secs), 60)
        return f"{m}:{s:02d}"

    def _toggle_timer(self):
        if self._timer_running:
            self._stop_timer()
            self.btn_timer.configure(text="▶  Resume Timer", fg_color=ACCENT)
        else:
            if self._timer_val <= 0:
                self._timer_val = self._timer_max
            self._timer_running = True
            self.btn_timer.configure(text="⏸  Pause Timer", fg_color=MUTED)
            self._timer_thread = threading.Thread(target=self._run_timer, daemon=True)
            self._timer_thread.start()

    def _run_timer(self):
        while self._timer_running and self._timer_val > 0:
            time.sleep(1)
            self._timer_val -= 1
            self.after(0, self._update_timer_ui)
        if self._timer_val <= 0:
            self._timer_running = False
            self.after(0, lambda: self.btn_timer.configure(text="▶  Start Timer", fg_color=ACCENT))

    def _stop_timer(self):
        self._timer_running = False

    def _update_timer_ui(self):
        if hasattr(self, "timer_lbl") and self.timer_lbl.winfo_exists():
            self.timer_lbl.configure(text=self._fmt_time(self._timer_val))
        if hasattr(self, "timer_bar") and self.timer_bar.winfo_exists():
            pct = self._timer_val / self._timer_max if self._timer_max else 0
            self.timer_bar.place(relx=0, rely=0, relwidth=pct, relheight=1.0)

if __name__ == "__main__":
    app = IELTSApp()
    app.mainloop()
    