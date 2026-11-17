"codigo completo"


"""Interface grafica da calculadora."""

import tkinter as tk
from decimal import Decimal

from calculadora.core import calculate


BACKGROUND = "#101820"
PANEL = "#1c2935"
DISPLAY = "#f4f7fa"
TEXT = "#f4f7fa"
MUTED = "#a9b7c4"
BUTTON = "#2b3b49"
OPERATOR = "#38566c"
ACCENT = "#168c74"
DANGER = "#a84949"


def format_result(value: Decimal) -> str:
    """Formata decimais sem zeros finais ou notacao exponencial."""
    if value == 0:
        return "0"
    result = format(value, "f")
    if "." in result:
        result = result.rstrip("0").rstrip(".")
    return result


class Calculator:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Calculadora")
        self.root.configure(bg=BACKGROUND)
        self.root.minsize(340, 620)
        self.root.geometry("390x700")

        self.current = "0"
        self.first_operand: str | None = None
        self.operator: str | None = None
        self.waiting_for_operand = True
        self.error_active = False
        self.display_text = tk.StringVar(value=self.current)

        self._build_interface()
        self.root.bind("<Key>", self._handle_key)

    def _build_interface(self) -> None:
        content = tk.Frame(self.root, bg=BACKGROUND, padx=20, pady=18)
        content.pack(fill=tk.BOTH, expand=True)
        content.columnconfigure(0, weight=1)

        tk.Label(
            content,
            text="CALCULADORA",
            bg=BACKGROUND,
            fg=MUTED,
            font=("Segoe UI", 11, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        display_frame = tk.Frame(content, bg=PANEL, padx=16, pady=12)
        display_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 14))
        display_frame.columnconfigure(0, weight=1)
        self.expression_label = tk.Label(
            display_frame,
            text="",
            bg=PANEL,
            fg=MUTED,
            anchor="e",
            font=("Segoe UI", 12),
        )
        self.expression_label.grid(row=0, column=0, sticky="ew")
        self.display_label = tk.Label(
            display_frame,
            textvariable=self.display_text,
            bg=PANEL,
            fg=DISPLAY,
            anchor="e",
            font=("Segoe UI", 32, "bold"),
        )
        self.display_label.grid(row=1, column=0, sticky="ew", pady=(8, 0))

        history_frame = tk.Frame(content, bg=BACKGROUND)
        history_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 14))
        history_frame.columnconfigure(0, weight=1)
        tk.Label(
            history_frame,
            text="HISTÓRICO RECENTE",
            bg=BACKGROUND,
            fg=MUTED,
            anchor="w",
            font=("Segoe UI", 9, "bold"),
        ).grid(row=0, column=0, sticky="ew", pady=(0, 5))
        self.history = tk.Listbox(
            history_frame,
            height=5,
            bg=PANEL,
            fg=TEXT,
            selectbackground=OPERATOR,
            borderwidth=0,
            highlightthickness=0,
            font=("Segoe UI", 10),
            activestyle="none",
        )
        self.history.grid(row=1, column=0, sticky="nsew")
        scrollbar = tk.Scrollbar(history_frame, command=self.history.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.history.configure(yscrollcommand=scrollbar.set)

        keypad = tk.Frame(content, bg=BACKGROUND)
        keypad.grid(row=3, column=0, sticky="nsew")
        for column in range(4):
            keypad.columnconfigure(column, weight=1, uniform="key")
        for row in range(5):
            keypad.rowconfigure(row, weight=1, uniform="key")

        keys = [
            ("C", 0, 0, self.clear_all, DANGER),
            ("←", 0, 1, self.backspace, BUTTON),
            ("/", 0, 2, lambda: self.choose_operator("/"), OPERATOR),
            ("*", 0, 3, lambda: self.choose_operator("*"), OPERATOR),
            ("7", 1, 0, lambda: self.add_digit("7"), BUTTON),
            ("8", 1, 1, lambda: self.add_digit("8"), BUTTON),
            ("9", 1, 2, lambda: self.add_digit("9"), BUTTON),
            ("-", 1, 3, lambda: self.choose_operator("-"), OPERATOR),
            ("4", 2, 0, lambda: self.add_digit("4"), BUTTON),
            ("5", 2, 1, lambda: self.add_digit("5"), BUTTON),
            ("6", 2, 2, lambda: self.add_digit("6"), BUTTON),
            ("+", 2, 3, lambda: self.choose_operator("+"), OPERATOR),
            ("1", 3, 0, lambda: self.add_digit("1"), BUTTON),
            ("2", 3, 1, lambda: self.add_digit("2"), BUTTON),
            ("3", 3, 2, lambda: self.add_digit("3"), BUTTON),
            ("=", 3, 3, self.equals, ACCENT),
            ("0", 4, 0, lambda: self.add_digit("0"), BUTTON),
            (".", 4, 2, self.add_decimal, BUTTON),
        ]
        for label, row, column, command, color in keys:
            button = tk.Button(
                keypad,
                text=label,
                command=command,
                bg=color,
                fg=TEXT,
                activebackground=color,
                activeforeground=TEXT,
                relief=tk.FLAT,
                borderwidth=0,
                font=("Segoe UI", 17, "bold"),
                cursor="hand2",
                takefocus=True,
            )
            button.grid(
                row=row,
                column=column,
                columnspan=2 if label == "0" else 1,
                sticky="nsew",
                padx=4,
                pady=4,
                ipady=7,
            )

    def _sync_display(self) -> None:
        self.display_text.set(self.current)
        self.display_label.configure(
            font=("Segoe UI", 18 if len(self.current) > 13 else 32, "bold")
        )

    def _reset_error(self) -> None:
        if self.error_active:
            self.current = "0"
            self.error_active = False
            self.expression_label.configure(text="")

    def add_digit(self, digit: str) -> None:
        if digit not in "0123456789":
            self._show_error("Entrada inválida")
            return
        self._reset_error()
        if self.waiting_for_operand:
            self.current = digit
            self.waiting_for_operand = False
        elif self.current == "0":
            self.current = digit
        elif len(self.current.replace(".", "").lstrip("-")) < 16:
            self.current += digit
        self._sync_display()

    def add_decimal(self) -> None:
        self._reset_error()
        if self.waiting_for_operand:
            self.current = "0."
            self.waiting_for_operand = False
        elif "." not in self.current:
            self.current += "."
        self._sync_display()

    def choose_operator(self, operator: str) -> None:
        if operator not in {"+", "-", "*", "/"}:
            self._show_error("Operador inválido")
            return
        if self.error_active:
            return

        if self.operator and not self.waiting_for_operand:
            if not self._evaluate():
                return
        elif self.first_operand is None:
            self.first_operand = self.current

        self.operator = operator
        self.waiting_for_operand = True
        self.expression_label.configure(
            text=f"{self.first_operand} {self.operator}"
        )

    def equals(self) -> None:
        if self.error_active or self.operator is None:
            return
        if self.waiting_for_operand:
            self._show_error("Entrada inválida")
            return

        first = self.first_operand
        operator = self.operator
        second = self.current
        if first is None:
            self._show_error("Entrada inválida")
            return
        try:
            result = calculate(first, operator, second)
        except ZeroDivisionError:
            self._show_error("Divisão por zero")
            return
        except ValueError:
            self._show_error("Entrada inválida")
            return

        formatted_result = format_result(result)
        self.history.insert(
            0, f"{first} {operator} {second} = {formatted_result}"
        )
        if self.history.size() > 10:
            self.history.delete(10, tk.END)
        self.current = formatted_result
        self.first_operand = None
        self.operator = None
        self.waiting_for_operand = True
        self.expression_label.configure(text="")
        self._sync_display()

    def _evaluate(self) -> bool:
        if self.first_operand is None or self.operator is None:
            self._show_error("Entrada inválida")
            return False
        try:
            result = calculate(self.first_operand, self.operator, self.current)
        except ZeroDivisionError:
            self._show_error("Divisão por zero")
            return False
        except ValueError:
            self._show_error("Entrada inválida")
            return False
        self.current = format_result(result)
        self.first_operand = self.current
        self.waiting_for_operand = True
        return True

    def backspace(self) -> None:
        if self.error_active:
            self.clear_display()
        elif not self.waiting_for_operand:
            self.current = self.current[:-1]
            if self.current in {"", "-"}:
                self.current = "0"
            self._sync_display()

    def clear_display(self) -> None:
        self.current = "0"
        self.first_operand = None
        self.operator = None
        self.waiting_for_operand = True
        self.error_active = False
        self.expression_label.configure(text="")
        self._sync_display()

    def clear_all(self) -> None:
        self.clear_display()
        self.history.delete(0, tk.END)

    def _show_error(self, message: str) -> None:
        self.current = message
        self.first_operand = None
        self.operator = None
        self.waiting_for_operand = True
        self.error_active = True
        self.expression_label.configure(text="")
        self._sync_display()

    def _handle_key(self, event: tk.Event) -> None:
        if event.char and event.char in "0123456789":
            self.add_digit(event.char)
        elif event.char == "." or event.char == ",":
            self.add_decimal()
        elif event.char in {"+", "-", "*", "/"}:
            self.choose_operator(event.char)
        elif event.keysym in {"Return", "KP_Enter"}:
            self.equals()
        elif event.keysym == "BackSpace":
            self.backspace()
        elif event.keysym == "Escape":
            self.clear_all()


def main() -> None:
    root = tk.Tk()
    Calculator(root)
    root.mainloop()


if __name__ == "__main__":
    main()