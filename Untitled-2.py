"""Interface gráfica do Jogo da Forca."""

from pathlib import Path
import random
import tkinter as tk
from tkinter import messagebox

from forca_core import HangmanGame, WordEntry, load_word_bank, normalize_letter


BACKGROUND = "#101820"
PANEL = "#1c2935"
TEXT = "#f4f7fa"
MUTED = "#a9b7c4"
BUTTON = "#2b3b49"
ACCENT = "#168c74"
DANGER = "#a84949"
CORRECT = "#31735f"


class HangmanApp:
    def __init__(self, root: tk.Tk, word_bank: list[WordEntry]) -> None:
        self.root = root
        self.word_bank = word_bank
        self.wins = 0
        self.losses = 0
        self.hint_used = False

        root.title("Jogo da Forca")
        root.configure(bg=BACKGROUND)
        root.geometry("780x820")
        root.minsize(700, 740)

        self._build_interface()
        self.new_game()
        root.bind("<KeyPress>", self._on_key_press)

    def _build_interface(self) -> None:
        content = tk.Frame(self.root, bg=BACKGROUND, padx=24, pady=20)
        content.pack(fill=tk.BOTH, expand=True)
        content.columnconfigure(0, weight=1)

        tk.Label(
            content,
            text="JOGO DA FORCA",
            bg=BACKGROUND,
            fg=TEXT,
            font=("Segoe UI", 24, "bold"),
        ).grid(row=0, column=0, sticky="w")

        self.stats_text = tk.StringVar()
        tk.Label(
            content,
            textvariable=self.stats_text,
            bg=BACKGROUND,
            fg=MUTED,
            font=("Segoe UI", 11),
        ).grid(row=1, column=0, sticky="w", pady=(2, 14))

        game_area = tk.Frame(content, bg=BACKGROUND)
        game_area.grid(row=2, column=0, sticky="nsew")
        game_area.columnconfigure(0, weight=1)
        game_area.columnconfigure(1, weight=1)

        self.canvas = tk.Canvas(
            game_area,
            width=330,
            height=270,
            bg=PANEL,
            highlightthickness=0,
        )
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        info = tk.Frame(game_area, bg=PANEL, padx=18, pady=18)
        info.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        info.columnconfigure(0, weight=1)

        tk.Label(
            info,
            text="TENTATIVAS RESTANTES",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 10, "bold"),
        ).grid(row=0, column=0, sticky="w")

        self.attempts_text = tk.StringVar()
        tk.Label(
            info,
            textvariable=self.attempts_text,
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 28, "bold"),
        ).grid(row=1, column=0, sticky="w", pady=(0, 14))

        self.word_text = tk.StringVar()
        tk.Label(
            info,
            textvariable=self.word_text,
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 23, "bold"),
            wraplength=320,
        ).grid(row=2, column=0, sticky="w", pady=(0, 16))

        self.message_text = tk.StringVar()
        tk.Label(
            info,
            textvariable=self.message_text,
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 12, "bold"),
            wraplength=320,
            justify=tk.LEFT,
        ).grid(row=3, column=0, sticky="w")

        self.hint_text = tk.StringVar()
        tk.Label(
            info,
            textvariable=self.hint_text,
            bg=PANEL,
            fg="#f0c674",
            font=("Segoe UI", 11),
            wraplength=320,
            justify=tk.LEFT,
        ).grid(row=4, column=0, sticky="w", pady=(12, 0))

        controls = tk.Frame(content, bg=BACKGROUND)
        controls.grid(row=3, column=0, sticky="ew", pady=(16, 8))
        for column in range(3):
            controls.columnconfigure(column, weight=1)

        self._make_button(
            controls, "Novo Jogo", self.new_game, ACCENT
        ).grid(row=0, column=0, sticky="ew", padx=(0, 5))

        self._make_button(
            controls, "Desistir", self.give_up, DANGER
        ).grid(row=0, column=1, sticky="ew", padx=5)

        self.hint_button = self._make_button(
            controls, "Dicas", self.show_hint, BUTTON
        )
        self.hint_button.grid(row=0, column=2, sticky="ew", padx=(5, 0))

        keyboard = tk.Frame(content, bg=BACKGROUND)
        keyboard.grid(row=4, column=0, sticky="ew", pady=(8, 0))
        for column in range(7):
            keyboard.columnconfigure(column, weight=1, uniform="letter")

        self.letter_buttons: dict[str, tk.Button] = {}
        for index, letter in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
            button = self._make_button(
                keyboard,
                letter,
                lambda chosen=letter: self.make_guess(chosen),
                BUTTON,
            )
            button.grid(
                row=index // 7,
                column=index % 7,
                sticky="nsew",
                padx=3,
                pady=3,
                ipady=5,
            )
            self.letter_buttons[letter] = button

    @staticmethod
    def _make_button(
        parent: tk.Widget,
        text: str,
        command: object,
        color: str,
    ) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg=TEXT,
            activebackground=color,
            activeforeground=TEXT,
            disabledforeground=MUTED,
            relief=tk.FLAT,
            borderwidth=0,
            font=("Segoe UI", 11, "bold"),
            cursor="hand2",
            takefocus=True,
        )

    def new_game(self) -> None:
        entry = random.choice(self.word_bank)
        self.entry = entry
        self.game = HangmanGame(entry.word)
        self.hint_used = False
        self.message_text.set("Escolha uma letra para começar.")
        self.hint_text.set("Você tem uma dica disponível nesta partida.")
        self.hint_button.configure(state=tk.NORMAL, text="Dicas")
        self._refresh()

    def make_guess(self, letter: str) -> None:
        if self.game.is_finished:
            return

        letter = letter.upper()
        if letter in self.game.guessed_letters:
            return

        was_correct = self.game.guess(letter)

        if self.game.is_won:
            self.wins += 1
            self.message_text.set(
                f"Você venceu! A palavra era {self.game.word}."
            )
        elif self.game.is_lost:
            self.losses += 1
            self.message_text.set(
                f"Fim de jogo! A palavra era {self.game.word}."
            )
        elif was_correct:
            self.message_text.set("Letra encontrada!")
        else:
            self.message_text.set("Letra não encontrada.")

        self._refresh()

    def show_hint(self) -> None:
        if self.hint_used or self.game.is_finished:
            return

        self.hint_used = True
        self.hint_text.set(f"Dica: {self.entry.hint}")
        self.hint_button.configure(state=tk.DISABLED, text="Dica usada")

    def give_up(self) -> None:
        if self.game.is_finished:
            return

        self.game.give_up()
        self.losses += 1
        self.message_text.set(
            f"Você desistiu. A palavra era {self.game.word}."
        )
        self._refresh()

    def _refresh(self) -> None:
        self.stats_text.set(
            f"Vitórias: {self.wins}    Derrotas: {self.losses}"
        )
        self.attempts_text.set(f"{self.game.remaining_attempts} / 6")

        self.word_text.set(
            " ".join(
                character
                if character in " -'"
                or normalize_letter(character)
                in self.game.guessed_letters
                else "_"
                for character in self.game.word
            )
        )

        self._draw_hangman()

        for letter, button in self.letter_buttons.items():
            if letter in self.game.guessed_letters:
                color = (
                    CORRECT
                    if letter in self.game.word_letters
                    else DANGER
                )
                button.configure(state=tk.DISABLED, bg=color)
            elif self.game.is_finished:
                button.configure(state=tk.DISABLED)
            else:
                button.configure(state=tk.NORMAL, bg=BUTTON)

    def _draw_hangman(self) -> None:
        self.canvas.delete("all")
        self.canvas.create_line(35, 245, 180, 245, fill=TEXT, width=5)
        self.canvas.create_line(85, 245, 85, 35, fill=TEXT, width=5)
        self.canvas.create_line(85, 35, 205, 35, fill=TEXT, width=5)
        self.canvas.create_line(205, 35, 205, 62, fill=TEXT, width=4)

        parts = [
            lambda: self.canvas.create_oval(
                185, 62, 225, 102, outline=TEXT, width=4
            ),
            lambda: self.canvas.create_line(
                205, 102, 205, 166, fill=TEXT, width=4
            ),
            lambda: self.canvas.create_line(
                205, 116, 175, 145, fill=TEXT, width=4
            ),
            lambda: self.canvas.create_line(
                205, 116, 235, 145, fill=TEXT, width=4
            ),
            lambda: self.canvas.create_line(
                205, 166, 178, 205, fill=TEXT, width=4
            ),
            lambda: self.canvas.create_line(
                205, 166, 232, 205, fill=TEXT, width=4
            ),
        ]

        for draw_part in parts[: self.game.wrong_guesses]:
            draw_part()

    def _on_key_press(self, event: tk.Event) -> None:
        letter = event.char.upper()
        if len(letter) == 1 and "A" <= letter <= "Z":
            self.make_guess(letter)


def main() -> None:
    root = tk.Tk()

    try:
        word_bank = load_word_bank(
            Path(__file__).with_name("palavras.txt")
        )
    except (OSError, ValueError) as error:
        messagebox.showerror(
            "Erro ao carregar palavras",
            str(error),
            parent=root,
        )
        root.destroy()
        return

    HangmanApp(root, word_bank)
    root.mainloop()


if __name__ == "__main__":
    main()


