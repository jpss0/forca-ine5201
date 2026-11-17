"""Regras e carregamento de palavras para o Jogo da Forca."""

from dataclasses import dataclass
from pathlib import Path
import unicodedata


MAX_ERRORS = 6
MIN_WORDS = 50


def normalize_letter(letter: str) -> str:
    """Converte uma letra acentuada para A-Z e valida a entrada."""
    normalized = "".join(
        character
        for character in unicodedata.normalize("NFD", letter.upper())
        if unicodedata.category(character) != "Mn"
    )
    if len(normalized) != 1 or not "A" <= normalized <= "Z":
        raise ValueError("Informe uma única letra de A a Z.")
    return normalized


@dataclass(frozen=True)
class WordEntry:
    word: str
    hint: str


def load_word_bank(path: Path) -> list[WordEntry]:
    """Carrega linhas no formato palavra|dica e valida o banco de palavras."""
    entries: list[WordEntry] = []
    with path.open(encoding="utf-8") as words_file:
        for line_number, raw_line in enumerate(words_file, start=1):
            line = raw_line.strip()
            if not line:
                continue
            word, separator, hint = line.partition("|")
            word = word.strip()
            hint = hint.strip()
            if not separator or not word or not hint:
                raise ValueError(
                    f"Linha {line_number} inválida em {path}: "
                    "use o formato palavra|dica."
                )
            try:
                _word_letters(word)
            except ValueError as error:
                raise ValueError(
                    f"Palavra inválida na linha {line_number} de {path}."
                ) from error
            entries.append(WordEntry(word=word.upper(), hint=hint))

    if len(entries) < MIN_WORDS:
        raise ValueError(
            f"O arquivo {path} deve conter pelo menos {MIN_WORDS} palavras."
        )
    return entries


class HangmanGame:
    """Estado de uma partida, independente da interface gráfica."""

    def __init__(self, word: str) -> None:
        word = word.strip()
        if not word:
            raise ValueError("A palavra não pode ser vazia.")
        self.word = word.upper()
        self.word_letters = frozenset(_word_letters(self.word))
        if not self.word_letters:
            raise ValueError("A palavra deve conter pelo menos uma letra.")
        self.guessed_letters: set[str] = set()
        self.wrong_guesses = 0

    @property
    def remaining_attempts(self) -> int:
        return MAX_ERRORS - self.wrong_guesses

    @property
    def is_won(self) -> bool:
        return self.word_letters.issubset(self.guessed_letters)

    @property
    def is_lost(self) -> bool:
        return self.wrong_guesses >= MAX_ERRORS

    @property
    def is_finished(self) -> bool:
        return self.is_won or self.is_lost

    def guess(self, letter: str) -> bool:
        """Registra uma tentativa; retorna False para uma letra repetida."""
        if self.is_finished:
            raise RuntimeError("A partida já terminou.")
        normalized = normalize_letter(letter)
        if normalized in self.guessed_letters:
            return False
        self.guessed_letters.add(normalized)
        if normalized not in self.word_letters:
            self.wrong_guesses += 1
            return False
        return True

    def give_up(self) -> None:
        if not self.is_finished:
            self.wrong_guesses = MAX_ERRORS


def _word_letters(word: str) -> set[str]:
    letters: set[str] = set()
    for character in word:
        if character.isalpha():
            letters.add(normalize_letter(character))
        elif character not in " -'":
            raise ValueError("A palavra contém um caractere inválido.")
    if not letters:
        raise ValueError("A palavra deve conter pelo menos uma letra.")
    return letters