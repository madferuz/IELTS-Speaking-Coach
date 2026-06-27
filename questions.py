"""IELTS Speaking question bank.

40 hand-written questions across the three parts. Used as the
primary source; AI generation kicks in only when a part's bank
is exhausted.
"""

import random


# ============================================================
# PART 1 — Introduction (familiar topics)
# 20 questions, each with topic / question / 3 tips
# ============================================================

PART_1 = [
    {
        "topic": "Home",
        "question": "Can you describe the place where you live?",
        "tips": [
            "Mention the type of home (apartment, house).",
            "Use descriptive adjectives (spacious, cozy, modern).",
            "Add a personal feeling about it.",
        ],
    },
    {
        "topic": "Home",
        "question": "What is your favorite room in your home and why?",
        "tips": [
            "Name the room clearly.",
            "Describe what you do there.",
            "Explain why it feels special.",
        ],
    },
    {
        "topic": "Work & Study",
        "question": "Do you work or are you a student?",
        "tips": [
            "State your situation clearly.",
            "Give one specific detail (field, year).",
            "Add whether you enjoy it.",
        ],
    },
    {
        "topic": "Work & Study",
        "question": "What subject did you enjoy most at school?",
        "tips": [
            "Name the subject.",
            "Explain what you liked about it.",
            "Mention a teacher or memory.",
        ],
    },
    {
        "topic": "Hobbies",
        "question": "What do you like to do in your free time?",
        "tips": [
            "Give one or two specific activities.",
            "Use frequency adverbs (often, sometimes).",
            "Say why you enjoy it.",
        ],
    },
    {
        "topic": "Hobbies",
        "question": "Have you taken up any new hobbies recently?",
        "tips": [
            "Mention when you started.",
            "Describe what you do.",
            "Reflect on whether you'll continue.",
        ],
    },
    {
        "topic": "Food",
        "question": "What kind of food do you usually eat?",
        "tips": [
            "Mention a cuisine or specific dish.",
            "Talk about a typical meal.",
            "Add a preference or dislike.",
        ],
    },
    {
        "topic": "Food",
        "question": "Do you prefer cooking at home or eating out?",
        "tips": [
            "State your preference clearly.",
            "Give one reason.",
            "Mention how often you do each.",
        ],
    },
    {
        "topic": "Travel",
        "question": "Do you enjoy travelling? Why or why not?",
        "tips": [
            "Give a clear yes/no.",
            "Use a complex sentence with 'because'.",
            "Mention a destination.",
        ],
    },
    {
        "topic": "Travel",
        "question": "What is the most interesting place you have visited?",
        "tips": [
            "Name the place.",
            "Describe one memorable detail.",
            "Say why it stood out.",
        ],
    },
    {
        "topic": "Music",
        "question": "What kind of music do you like to listen to?",
        "tips": [
            "Mention one or two genres.",
            "Name an artist or song.",
            "Say when you listen to it.",
        ],
    },
    {
        "topic": "Music",
        "question": "Did you learn a musical instrument as a child?",
        "tips": [
            "Give a clear yes/no.",
            "Add a short detail.",
            "Reflect on whether you'd start now.",
        ],
    },
    {
        "topic": "Technology",
        "question": "How often do you use your smartphone?",
        "tips": [
            "Use a frequency expression (constantly, a few hours).",
            "Mention what you use it for.",
            "Add a feeling about the habit.",
        ],
    },
    {
        "topic": "Technology",
        "question": "Has technology changed the way you communicate?",
        "tips": [
            "Give a clear opinion.",
            "Compare past and present briefly.",
            "Add one example.",
        ],
    },
    {
        "topic": "Weather",
        "question": "What is the weather like in your hometown?",
        "tips": [
            "Mention the seasons.",
            "Use weather adjectives (humid, mild).",
            "Add a personal preference.",
        ],
    },
    {
        "topic": "Sports",
        "question": "Do you play any sports?",
        "tips": [
            "State the sport clearly.",
            "Mention how often you play.",
            "Add who you play with.",
        ],
    },
    {
        "topic": "Reading",
        "question": "Do you enjoy reading books?",
        "tips": [
            "Give a clear yes/no.",
            "Mention a genre or title.",
            "Say when you usually read.",
        ],
    },
    {
        "topic": "Friends",
        "question": "How often do you see your friends?",
        "tips": [
            "Use a frequency expression.",
            "Mention what you usually do together.",
            "Add a feeling about it.",
        ],
    },
    {
        "topic": "Daily Routine",
        "question": "What does a typical weekday look like for you?",
        "tips": [
            "Use sequencing words (first, then, after that).",
            "Mention 2–3 key activities.",
            "Add whether you enjoy the routine.",
        ],
    },
    {
        "topic": "Transport",
        "question": "How do you usually get around your city?",
        "tips": [
            "Name your usual mode of transport.",
            "Mention reasons (cost, speed).",
            "Add a comparison to another option.",
        ],
    },
]


# ============================================================
# PART 2 — Long Turn (cue cards)
# 10 cue cards, each with topic / main_prompt / 5 cue_points / 3 tips
# ============================================================

PART_2 = [
    {
        "topic": "A memorable trip",
        "main_prompt": "Describe a memorable trip you have taken.",
        "cue_points": [
            "You should say:",
            "where you went",
            "who you went with",
            "what you did there",
            "and explain why it was memorable.",
        ],
        "tips": [
            "Use past tenses consistently.",
            "Include sensory details (sights, sounds).",
            "End with a clear reflection.",
        ],
    },
    {
        "topic": "A person who influenced you",
        "main_prompt": "Describe a person who has had a big influence on your life.",
        "cue_points": [
            "You should say:",
            "who this person is",
            "how you know them",
            "what they are like",
            "and explain how they influenced you.",
        ],
        "tips": [
            "Use character adjectives (supportive, ambitious).",
            "Give a specific example of their influence.",
            "Show genuine emotion.",
        ],
    },
    {
        "topic": "A useful skill",
        "main_prompt": "Describe a useful skill you have learned.",
        "cue_points": [
            "You should say:",
            "what the skill is",
            "when you learned it",
            "how you learned it",
            "and explain why it is useful.",
        ],
        "tips": [
            "Use sequencing language.",
            "Mention challenges you overcame.",
            "Connect to current usefulness.",
        ],
    },
    {
        "topic": "A favourite book",
        "main_prompt": "Describe a book you have enjoyed reading.",
        "cue_points": [
            "You should say:",
            "what the book is about",
            "when you read it",
            "what you liked about it",
            "and explain why you would recommend it.",
        ],
        "tips": [
            "Don't retell the plot — focus on themes.",
            "Use opinion phrases (I found it…).",
            "Recommend it to a specific kind of reader.",
        ],
    },
    {
        "topic": "An important decision",
        "main_prompt": "Describe an important decision you have made.",
        "cue_points": [
            "You should say:",
            "what the decision was",
            "when you made it",
            "what factors you considered",
            "and explain how it changed your life.",
        ],
        "tips": [
            "Frame it as a turning point.",
            "Mention the alternatives briefly.",
            "Reflect on the outcome.",
        ],
    },
    {
        "topic": "A special meal",
        "main_prompt": "Describe a special meal you have had.",
        "cue_points": [
            "You should say:",
            "what the meal was",
            "where you had it",
            "who you were with",
            "and explain why it was special.",
        ],
        "tips": [
            "Use vivid food vocabulary.",
            "Include the atmosphere.",
            "End with a feeling, not just facts.",
        ],
    },
    {
        "topic": "A piece of technology",
        "main_prompt": "Describe a piece of technology you find useful.",
        "cue_points": [
            "You should say:",
            "what it is",
            "how often you use it",
            "what you use it for",
            "and explain why it is useful to you.",
        ],
        "tips": [
            "Be specific about features.",
            "Contrast with life before it.",
            "Mention one drawback for balance.",
        ],
    },
    {
        "topic": "A goal you want to achieve",
        "main_prompt": "Describe a goal you would like to achieve in the future.",
        "cue_points": [
            "You should say:",
            "what the goal is",
            "when you want to achieve it",
            "what steps you will take",
            "and explain why it matters to you.",
        ],
        "tips": [
            "Use future tenses and modals (I plan to, I will).",
            "Show realistic planning.",
            "Connect it to your values.",
        ],
    },
    {
        "topic": "A childhood memory",
        "main_prompt": "Describe a happy memory from your childhood.",
        "cue_points": [
            "You should say:",
            "what happened",
            "where it took place",
            "who was with you",
            "and explain why it is a happy memory.",
        ],
        "tips": [
            "Use past simple and past continuous.",
            "Include small concrete details.",
            "End with how it makes you feel now.",
        ],
    },
    {
        "topic": "A place you'd like to visit",
        "main_prompt": "Describe a place you would like to visit in the future.",
        "cue_points": [
            "You should say:",
            "where it is",
            "how you found out about it",
            "what you would do there",
            "and explain why you want to go.",
        ],
        "tips": [
            "Use 'would' and conditional structures.",
            "Mention specific landmarks or activities.",
            "Show genuine curiosity.",
        ],
    },
]


# ============================================================
# PART 3 — Discussion (abstract topics)
# 10 question sets, each with topic / main_question / 2 follow_ups / 3 tips
# ============================================================

PART_3 = [
    {
        "topic": "Education",
        "main_question": "How has education changed in your country over the past few decades?",
        "follow_ups": [
            "Do you think online learning is as effective as classroom learning?",
            "What role should the government play in improving education?",
        ],
        "tips": [
            "Use comparison language (whereas, in contrast).",
            "Support claims with one example.",
            "Acknowledge both sides before concluding.",
        ],
    },
    {
        "topic": "Technology",
        "main_question": "How has technology changed the way people work?",
        "follow_ups": [
            "Do you think remote work will become the norm?",
            "What are the downsides of being constantly connected?",
        ],
        "tips": [
            "Use abstract nouns (productivity, connectivity).",
            "Give a balanced view.",
            "Avoid generalising — qualify with 'many', 'some'.",
        ],
    },
    {
        "topic": "Environment",
        "main_question": "What are the biggest environmental challenges your country faces?",
        "follow_ups": [
            "Whose responsibility is it to tackle climate change — individuals or governments?",
            "Are people in your country becoming more eco-conscious?",
        ],
        "tips": [
            "Use cause-effect linkers (as a result, due to).",
            "Cite one concrete example.",
            "Distinguish short- and long-term impacts.",
        ],
    },
    {
        "topic": "Family",
        "main_question": "How have family structures changed in modern society?",
        "follow_ups": [
            "Do you think extended families are better than nuclear families?",
            "How has the role of grandparents changed?",
        ],
        "tips": [
            "Compare generations.",
            "Use hedging language (tends to, generally).",
            "Avoid stating it's universally good or bad.",
        ],
    },
    {
        "topic": "Work",
        "main_question": "What makes a job satisfying for most people?",
        "follow_ups": [
            "Is salary more important than passion?",
            "Should young people choose stable careers or follow their interests?",
        ],
        "tips": [
            "Use abstract vocabulary (fulfilment, autonomy).",
            "Distinguish intrinsic vs extrinsic motivation.",
            "Take a clear position at the end.",
        ],
    },
    {
        "topic": "Cities",
        "main_question": "What are the advantages and disadvantages of living in big cities?",
        "follow_ups": [
            "Why do so many people move from rural to urban areas?",
            "How can cities be made more liveable?",
        ],
        "tips": [
            "Structure as pros / cons / your view.",
            "Use comparative structures.",
            "Mention specific city features (transport, housing).",
        ],
    },
    {
        "topic": "Health",
        "main_question": "How can people be encouraged to lead healthier lifestyles?",
        "follow_ups": [
            "Should governments tax unhealthy food?",
            "Why do many people struggle to maintain healthy habits?",
        ],
        "tips": [
            "Use modal verbs (could, should, ought to).",
            "Combine personal responsibility and policy.",
            "Mention behavioural barriers.",
        ],
    },
    {
        "topic": "Media",
        "main_question": "How reliable is the news in your country?",
        "follow_ups": [
            "Do social media platforms spread more misinformation than traditional media?",
            "How can people learn to evaluate news critically?",
        ],
        "tips": [
            "Use cautious language (it seems, arguably).",
            "Distinguish types of media.",
            "Suggest one practical solution.",
        ],
    },
    {
        "topic": "Travel",
        "main_question": "Why do people travel to other countries?",
        "follow_ups": [
            "Has international travel become too easy?",
            "Does tourism benefit or harm local communities?",
        ],
        "tips": [
            "Categorise motivations (cultural, leisure, business).",
            "Balance benefits with harms.",
            "Use 'on the one hand / on the other'.",
        ],
    },
    {
        "topic": "Money",
        "main_question": "Do you think money is the most important factor in happiness?",
        "follow_ups": [
            "Why do some wealthy people remain unhappy?",
            "What other factors contribute to a good life?",
        ],
        "tips": [
            "Use abstract nouns (contentment, security).",
            "Reference research or common sense briefly.",
            "Avoid clichés — give a specific angle.",
        ],
    },
]


# ============================================================
# Lookup by part number
# ============================================================

BANK = {1: PART_1, 2: PART_2, 3: PART_3}


def get_random_question(part: int, used_indices: set) -> tuple[dict, int] | None:
    """Pick a random unused question for the given part.

    Returns (question_dict, index) or None if all questions are used.
    """
    bank = BANK[part]
    available = [i for i in range(len(bank)) if i not in used_indices]
    if not available:
        return None
    idx = random.choice(available)
    return bank[idx], idx


def total_questions(part: int) -> int:
    """How many questions are in the bank for this part."""
    return len(BANK[part])