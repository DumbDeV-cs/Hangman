#!/usr/bin/env python3
"""Terminal Hangman — categories, difficulty levels, hints, colors and
an almost unlimited supply of random words."""

import os
import random
import sys

# ---------------------------------------------------------------- colors ----
os.system("")  # enables ANSI escape codes on Windows terminals
USE_COLOR = sys.stdout.isatty()


def c(text, code):
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, BOLD, DIM = (
    "31", "32", "33", "34", "35", "36", "1", "2",
)

# ----------------------------------------------------------------- words ----
CATEGORIES = {
    "Technology": """
        python keyboard compiler algorithm database network terminal software
        hardware browser firewall protocol bandwidth encryption processor
        variable function recursion debugger framework interface developer
        server router malware backup cloud pixel laptop monitor wireless
        satellite password username internet bluetooth android javascript
        repository kernel binary cache thread""".split(),
    "Science": """
        voltage resistor capacitor inductor transistor circuit current
        electron proton neutron molecule gravity quantum photon galaxy planet
        orbit asteroid nebula velocity momentum friction magnetic physics
        chemistry biology genetics ecosystem evolution enzyme bacteria
        microscope telescope laboratory element oxygen hydrogen carbon
        spectrum frequency amplifier""".split(),
    "Animals": """
        elephant giraffe leopard penguin dolphin kangaroo crocodile gorilla
        cheetah buffalo squirrel hedgehog flamingo peacock octopus jellyfish
        scorpion butterfly dragonfly chameleon porcupine platypus mongoose
        panda yak tiger rhinoceros eagle falcon parrot tortoise seahorse
        antelope hippopotamus""".split(),
    "Nature & Places": """
        himalaya kathmandu mountain glacier volcano waterfall rainforest
        desert island canyon valley river ocean meadow forest monsoon
        thunder lightning rainbow horizon peninsula plateau savanna tundra
        archipelago lagoon everest pokhara lumbini himalayan temple monastery
        stupa village""".split(),
    "Food": """
        momo noodle chocolate sandwich pancake spaghetti dumpling pudding
        biscuit mushroom cucumber pineapple strawberry blueberry coconut
        avocado cabbage cauliflower broccoli pumpkin potato tomato ginger
        cinnamon cardamom turmeric yogurt cheese butter lentil porridge
        chutney samosa""".split(),
    "Everyday Life": """
        umbrella backpack notebook bicycle sunglasses pillow blanket window
        curtain mirror kitchen bedroom library hospital airport station
        market festival holiday journey adventure treasure mystery shadow
        whisper challenge freedom friendship courage memory dream puzzle
        orchestra telescope compass lantern""".split(),
}

DICT_PATHS = ["/usr/share/dict/words", "/usr/dict/words"]


def load_system_dictionary():
    """Use the OS word list (huge variety) if the machine has one."""
    for path in DICT_PATHS:
        try:
            with open(path, encoding="utf-8") as f:
                words = {
                    w.strip().lower()
                    for w in f
                    if w.strip().isalpha() and w.strip().isascii()
                    and w.strip() == w.strip().lower()  # skip proper nouns
                    and 4 <= len(w.strip()) <= 14
                }
            if len(words) > 1000:
                return sorted(words)
        except OSError:
            continue
    return []


SYSTEM_WORDS = load_system_dictionary()
ALL_BUILTIN = sorted({w for ws in CATEGORIES.values() for w in ws})

DIFFICULTY = {
    "Easy": (3, 6),
    "Medium": (7, 9),
    "Hard": (10, 20),
    "Any": (3, 20),
}

MAX_WRONG = 6

STAGES = [
    r"""
     +---+
     |   |
         |
         |
         |
         |
    =========""",
    r"""
     +---+
     |   |
     O   |
         |
         |
         |
    =========""",
    r"""
     +---+
     |   |
     O   |
     |   |
         |
         |
    =========""",
    r"""
     +---+
     |   |
     O   |
    /|   |
         |
         |
    =========""",
    r"""
     +---+
     |   |
     O   |
    /|\  |
         |
         |
    =========""",
    r"""
     +---+
     |   |
     O   |
    /|\  |
    /    |
         |
    =========""",
    r"""
     +---+
     |   |
     O   |
    /|\  |
    / \  |
         |
    =========""",
]

BANNER = r"""
  _   _    _    _   _  ____ __  __    _    _   _
 | | | |  / \  | \ | |/ ___|  \/  |  / \  | \ | |
 | |_| | / _ \ |  \| | |  _| |\/| | / _ \ |  \| |
 |  _  |/ ___ \| |\  | |_| | |  | |/ ___ \| |\  |
 |_| |_/_/   \_\_| \_|\____|_|  |_/_/   \_\_| \_|
"""


# ----------------------------------------------------------------- menus ----
def ask_choice(title, options):
    """Show a numbered menu and return the chosen option."""
    print(c(f"\n  {title}", BOLD))
    for i, opt in enumerate(options, 1):
        print(f"   {c(str(i), CYAN)}. {opt}")
    while True:
        raw = input(c("  > ", YELLOW)).strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print(c("  Pick a number from the list.", RED))


def pick_word():
    cats = list(CATEGORIES) + ["Surprise me (random)"]
    if SYSTEM_WORDS:
        cats.append("Whole dictionary (huge)")
    category = ask_choice("Choose a category:", cats)
    level = ask_choice("Choose difficulty:", list(DIFFICULTY))
    lo, hi = DIFFICULTY[level]

    if category in CATEGORIES:
        pool, label = CATEGORIES[category], category
    elif category.startswith("Whole"):
        pool, label = SYSTEM_WORDS, "Dictionary word"
    else:
        # random mix, with dictionary words thrown in when available
        pool = ALL_BUILTIN + (random.sample(SYSTEM_WORDS, 3000) if SYSTEM_WORDS else [])
        label = "Mystery"

    matching = [w for w in pool if lo <= len(w) <= hi] or pool
    return random.choice(matching), label


# ------------------------------------------------------------------ game ----
def render(word, guessed, wrong, label, hints_left):
    print(c(STAGES[len(wrong)], RED if len(wrong) >= 4 else YELLOW))
    shown = " ".join(c(ch.upper(), GREEN) if ch in guessed else "_" for ch in word)
    print(f"\n   Category: {c(label, MAGENTA)}   ({len(word)} letters)")
    print(f"   Word:     {shown}")
    lives = c("♥ " * (MAX_WRONG - len(wrong)), RED) + c("♡ " * len(wrong), DIM)
    print(f"   Lives:    {lives}")
    wrong_txt = " ".join(sorted(x.upper() for x in wrong)) or "-"
    print(f"   Missed:   {c(wrong_txt, RED)}")
    if hints_left:
        print(c("   (type ? for a hint — costs 1 life)", DIM))
    print()


def play(stats):
    word, label = pick_word()
    guessed, wrong = set(), set()
    hints_left = 1
    message = ""

    print(c("\n  ─────────────  New game  ─────────────", CYAN))
    while True:
        render(word, guessed, wrong, label, hints_left)
        if message:
            print("  " + message + "\n")
            message = ""

        if all(ch in guessed for ch in word):
            print(c(f"  🎉 You won! The word was '{word.upper()}'.", GREEN))
            stats["wins"] += 1
            stats["streak"] += 1
            return
        if len(wrong) >= MAX_WRONG:
            print(c(f"  💀 You lost! The word was '{word.upper()}'.", RED))
            stats["losses"] += 1
            stats["streak"] = 0
            return

        guess = input(c("  Guess a letter: ", YELLOW)).strip().lower()

        if guess == "?":
            hidden = [ch for ch in set(word) if ch not in guessed]
            if hints_left and len(wrong) < MAX_WRONG - 1 and hidden:
                letter = random.choice(hidden)
                guessed.add(letter)
                hints_left -= 1
                wrong.add("*")  # costs a life; shown as a star
                message = c(f"Hint: the word contains '{letter.upper()}'.", CYAN)
            else:
                message = c("No hints available right now.", RED)
        elif len(guess) != 1 or not guess.isalpha():
            message = c("Please enter a single letter.", RED)
        elif guess in guessed or guess in wrong:
            message = c("You already guessed that one.", YELLOW)
        elif guess in word:
            guessed.add(guess)
            message = c("Nice! 👍", GREEN)
        else:
            wrong.add(guess)
            message = c("Nope! 😬", RED)


def main():
    print(c(BANNER, CYAN))
    print(c("  Guess the word before the drawing is complete!", DIM))
    stats = {"wins": 0, "losses": 0, "streak": 0}

    while True:
        play(stats)
        print(
            f"\n  Score — {c('Wins: ' + str(stats['wins']), GREEN)}  "
            f"{c('Losses: ' + str(stats['losses']), RED)}  "
            f"{c('Streak: ' + str(stats['streak']), YELLOW)}"
        )
        if input("\n  Play again? (y/n): ").strip().lower() not in ("y", "yes"):
            print(c("\n  Thanks for playing! 👋\n", CYAN))
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print(c("\n\n  Bye! 👋\n", CYAN))
        """thanks!!"""
        #test




        #dgwrhtrgettjrtrethjgrgfhfdfgfdsfgbghfdsgh