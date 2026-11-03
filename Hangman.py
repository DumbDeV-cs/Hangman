#!/usr/bin/env python3
"""Terminal Hangman game."""

import random

WORDS = [
    "python", "circuit", "voltage", "resistor", "capacitor", "inductor",
    "algorithm", "variable", "function", "compiler", "keyboard", "network",
    "database", "terminal", "programming", "recursion", "processor",
    "transistor", "himalaya", "kathmandu", "mountain", "software",
]

MAX_WRONG = 6

STAGES = [
    """
     +---+
     |   |
         |
         |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
         |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
     |   |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
    /|   |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
    /|\\  |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
    /|\\  |
    /    |
         |
    =========""",
    """
     +---+
     |   |
     O   |
    /|\\  |
    / \\  |
         |
    =========""",
]


def display(word, guessed, wrong):
    print(STAGES[len(wrong)])
    print("\n  Word: " + " ".join(c if c in guessed else "_" for c in word))
    print(f"  Wrong guesses ({len(wrong)}/{MAX_WRONG}): {' '.join(sorted(wrong)) or '-'}\n")


def play():
    word = random.choice(WORDS)
    guessed = set()
    wrong = set()

    print("\n=== HANGMAN ===")
    while True:
        display(word, guessed, wrong)

        if all(c in guessed for c in word):
            print(f"  You won! The word was '{word}'.")
            return
        if len(wrong) >= MAX_WRONG:
            print(f"  You lost! The word was '{word}'.")
            return

        guess = input("  Guess a letter: ").strip().lower()

        if len(guess) != 1 or not guess.isalpha():
            print("  Please enter a single letter.")
        elif guess in guessed or guess in wrong:
            print("  You already guessed that.")
        elif guess in word:
            guessed.add(guess)
            print("  Good guess!")
        else:
            wrong.add(guess)
            print("  Nope!")


def main():
    while True:
        play()
        again = input("\n  Play again? (y/n): ").strip().lower()
        if again != "y":
            print("  Thanks for playing!")
            break


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n  Bye!")