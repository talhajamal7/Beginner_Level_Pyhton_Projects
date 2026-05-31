"""
Scientific Calculator using Tkinter
====================================
A fully functional scientific calculator with a clean, modern GUI.
Supports basic arithmetic and scientific functions like sin, cos, tan,
log, ln, sqrt, power, and factorial.

Run with: python scientific_calculator.py
"""

import tkinter as tk
from tkinter import font as tkfont
import math


# ──────────────────────────────────────────────
#  CALCULATOR LOGIC
# ──────────────────────────────────────────────

def evaluate_expression(expression: str) -> str:
    """
    Safely evaluate a mathematical expression string.
    Replaces user-friendly symbols with Python/math equivalents,
    then uses eval() in a restricted namespace for safety.
    Returns the result as a string, or an error message.
    """
    try:
        # Replace display symbols with Python equivalents
        expr = expression
        expr = expr.replace("^", "**")          # power
        expr = expr.replace("π", str(math.pi))  # pi constant
        expr = expr.replace("e", str(math.e))   # Euler's number

        # Allowed names for eval – only math functions + builtins we need
        safe_names = {
            "__builtins__": {},          # block all built-ins
            "sin":   lambda x: math.sin(math.radians(x)),   # degrees mode
            "cos":   lambda x: math.cos(math.radians(x)),
            "tan":   lambda x: math.tan(math.radians(x)),
            "log":   math.log10,         # log base-10
            "ln":    math.log,           # natural log
            "sqrt":  math.sqrt,
            "factorial": math.factorial,
            "abs":   abs,
            "pi":    math.pi,
            "e":     math.e,
        }

        result = eval(expr, safe_names)   # evaluate the expression

        # Format: remove trailing .0 for whole numbers
        if isinstance(result, float) and result.is_integer():
            return str(int(result))
        return str(round(result, 10))     # round to avoid floating-point noise

    except ZeroDivisionError:
        return "Error: ÷ by 0"
    except ValueError as err:
        return f"Error: {err}"
    except Exception:
        return "Error: Invalid input"


# ──────────────────────────────────────────────
#  GUI – CALCULATOR WINDOW
# ──────────────────────────────────────────────

class ScientificCalculator(tk.Tk):
    """Main application window for the scientific calculator."""

    # ── Colour palette ──────────────────────────────────────────────────────
    BG          = "#1a1a2e"   # deep navy background
    DISPLAY_BG  = "#16213e"   # slightly lighter for the display area
    BTN_DARK    = "#0f3460"   # dark buttons (digits row bg)
    BTN_MID     = "#1a1a2e"   # mid-tone (scientific functions)
    BTN_ACCENT  = "#e94560"   # red accent (operators + equals)
    BTN_CLEAR   = "#533483"   # purple for clear / backspace
    TEXT_LIGHT  = "#eaeaea"   # primary text
    TEXT_ACCENT = "#e94560"   # accent text (operator labels)
    TEXT_DIM    = "#a8a8b3"   # secondary / dim text
    TEXT_RESULT = "#ff4d4d"   # bright red for the main display output

    def __init__(self):
        super().__init__()

        self.title("Scientific Calculator")
        self.resizable(False, False)
        self.configure(bg=self.BG)

        # Stores the current expression being built
        self._expression = ""

        self._build_fonts()
        self._build_display()
        self._build_buttons()

        # Allow keyboard input as well
        self.bind("<Key>", self._on_key_press)

    # ── Fonts ────────────────────────────────────────────────────────────────

    def _build_fonts(self):
        self.font_display    = tkfont.Font(family="Courier New", size=28, weight="bold")
        self.font_small_disp = tkfont.Font(family="Courier New", size=13)
        self.font_btn        = tkfont.Font(family="Segoe UI",    size=13, weight="bold")
        self.font_btn_sm     = tkfont.Font(family="Segoe UI",    size=11)

    # ── Display ──────────────────────────────────────────────────────────────

    def _build_display(self):
        """Create the top display panel with two rows: expression + result preview."""
        frame = tk.Frame(self, bg=self.DISPLAY_BG, pady=10)
        frame.grid(row=0, column=0, columnspan=5, sticky="nsew", padx=2, pady=(2, 0))

        # Small label that shows the running expression
        self._expr_var = tk.StringVar(value="")
        tk.Label(
            frame,
            textvariable=self._expr_var,
            font=self.font_small_disp,
            bg=self.DISPLAY_BG,
            fg=self.TEXT_DIM,
            anchor="e",
            padx=12,
        ).pack(fill="x")

        # Large entry for current input / result
        self._display_var = tk.StringVar(value="0")
        entry = tk.Entry(
            frame,
            textvariable=self._display_var,
            font=self.font_display,
            bg=self.DISPLAY_BG,
            fg=self.TEXT_RESULT,       # red text so result is clearly visible
            insertbackground=self.TEXT_RESULT,
            bd=0,
            highlightthickness=0,
            justify="right",
            state="readonly",   # user types via buttons; keyboard handled separately
        )
        entry.pack(fill="x", padx=10, pady=(0, 8))

    # ── Button grid ──────────────────────────────────────────────────────────

    def _build_buttons(self):
        """
        Define every button in row-order and place them in a grid.
        Each entry: (label, column-span, action, bg-colour, fg-colour)
        """
        # Each row is a list of (label, colspan, action, bg, fg)
        rows = [
            # Row 1 – scientific top row
            [
                ("sin",  1, lambda: self._fn("sin("),  self.BTN_MID,    self.TEXT_LIGHT),
                ("cos",  1, lambda: self._fn("cos("),  self.BTN_MID,    self.TEXT_LIGHT),
                ("tan",  1, lambda: self._fn("tan("),  self.BTN_MID,    self.TEXT_LIGHT),
                ("log",  1, lambda: self._fn("log("),  self.BTN_MID,    self.TEXT_LIGHT),
                ("ln",   1, lambda: self._fn("ln("),   self.BTN_MID,    self.TEXT_LIGHT),
            ],
            # Row 2 – more scientific
            [
                ("√",    1, lambda: self._fn("sqrt("), self.BTN_MID,    self.TEXT_LIGHT),
                ("x²",   1, lambda: self._append("^2"),self.BTN_MID,    self.TEXT_LIGHT),
                ("xʸ",   1, lambda: self._append("^"), self.BTN_MID,    self.TEXT_LIGHT),
                ("n!",   1, lambda: self._fn("factorial("), self.BTN_MID, self.TEXT_LIGHT),
                ("π",    1, lambda: self._append("π"), self.BTN_MID,    self.TEXT_ACCENT),
            ],
            # Row 3 – parentheses, sign, mod, backspace, clear
            [
                ("(",    1, lambda: self._append("("), self.BTN_DARK,   self.TEXT_DIM),
                (")",    1, lambda: self._append(")"), self.BTN_DARK,   self.TEXT_DIM),
                ("+/-",  1, self._toggle_sign,         self.BTN_DARK,   self.TEXT_DIM),
                ("⌫",    1, self._backspace,            self.BTN_CLEAR,  self.TEXT_LIGHT),
                ("C",    1, self._clear,                self.BTN_CLEAR,  self.TEXT_LIGHT),
            ],
            # Row 4 – digits + operator
            [
                ("7",    1, lambda: self._append("7"), self.BTN_DARK,   self.TEXT_LIGHT),
                ("8",    1, lambda: self._append("8"), self.BTN_DARK,   self.TEXT_LIGHT),
                ("9",    1, lambda: self._append("9"), self.BTN_DARK,   self.TEXT_LIGHT),
                ("÷",    1, lambda: self._append("/"), self.BTN_ACCENT,  self.TEXT_LIGHT),
                ("%",    1, lambda: self._append("%"), self.BTN_ACCENT,  self.TEXT_LIGHT),
            ],
            # Row 5
            [
                ("4",    1, lambda: self._append("4"), self.BTN_DARK,   self.TEXT_LIGHT),
                ("5",    1, lambda: self._append("5"), self.BTN_DARK,   self.TEXT_LIGHT),
                ("6",    1, lambda: self._append("6"), self.BTN_DARK,   self.TEXT_LIGHT),
                ("×",    1, lambda: self._append("*"), self.BTN_ACCENT,  self.TEXT_LIGHT),
                ("1/x",  1, self._reciprocal,          self.BTN_MID,    self.TEXT_DIM),
            ],
            # Row 6
            [
                ("1",    1, lambda: self._append("1"), self.BTN_DARK,   self.TEXT_LIGHT),
                ("2",    1, lambda: self._append("2"), self.BTN_DARK,   self.TEXT_LIGHT),
                ("3",    1, lambda: self._append("3"), self.BTN_DARK,   self.TEXT_LIGHT),
                ("−",    1, lambda: self._append("-"), self.BTN_ACCENT,  self.TEXT_LIGHT),
                ("abs",  1, lambda: self._fn("abs("),  self.BTN_MID,    self.TEXT_DIM),
            ],
            # Row 7 – zero (wide) + decimal + equals + plus
            [
                ("0",    2, lambda: self._append("0"), self.BTN_DARK,   self.TEXT_LIGHT),
                (".",    1, lambda: self._append("."), self.BTN_DARK,   self.TEXT_DIM),
                ("+",    1, lambda: self._append("+"), self.BTN_ACCENT,  self.TEXT_LIGHT),
                ("=",    1, self._calculate,           "#e94560",       "#ffffff"),
            ],
        ]

        # Render every button
        for r_idx, row in enumerate(rows):
            col = 0
            for (label, span, action, bg, fg) in row:
                btn = tk.Button(
                    self,
                    text=label,
                    command=action,
                    bg=bg,
                    fg=fg,
                    activebackground=self._lighten(bg),
                    activeforeground=fg,
                    font=self.font_btn if len(label) <= 2 else self.font_btn_sm,
                    bd=0,
                    highlightthickness=0,
                    cursor="hand2",
                    relief="flat",
                    width=5 * span,   # approx character width
                    height=2,
                )
                btn.grid(
                    row=r_idx + 1,    # row 0 is the display
                    column=col,
                    columnspan=span,
                    sticky="nsew",
                    padx=2,
                    pady=2,
                )
                col += span

        # Make all button rows stretch evenly
        for r in range(1, len(rows) + 1):
            self.grid_rowconfigure(r, weight=1)
        for c in range(5):
            self.grid_columnconfigure(c, weight=1)

    # ── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _lighten(hex_color: str) -> str:
        """Return a slightly lighter hex colour for hover feedback."""
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = min(r + 30, 255), min(g + 30, 255), min(b + 30, 255)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _set_display(self, text: str):
        """Update the main display label."""
        self._display_var.set(text)

    def _update_expr_label(self):
        """Show the running expression in the small label above."""
        self._expr_var.set(self._expression)

    # ── Actions ──────────────────────────────────────────────────────────────

    def _append(self, char: str):
        """Append a character / operator to the expression."""
        # If the display shows a result and user presses a digit, start fresh
        if self._expression == "" and self._display_var.get() not in ("0", ""):
            # Continue from previous result
            self._expression = self._display_var.get()

        self._expression += char
        self._set_display(self._expression)
        self._update_expr_label()

    def _fn(self, func_str: str):
        """Insert a function call prefix like 'sin(' into the expression."""
        self._expression += func_str
        self._set_display(self._expression)
        self._update_expr_label()

    def _clear(self):
        """Reset everything to the initial state."""
        self._expression = ""
        self._set_display("0")
        self._expr_var.set("")

    def _backspace(self):
        """Remove the last character from the expression."""
        self._expression = self._expression[:-1]
        self._set_display(self._expression if self._expression else "0")
        self._update_expr_label()

    def _calculate(self):
        """Evaluate the current expression and show the result."""
        if not self._expression:
            return

        result = evaluate_expression(self._expression)

        # Show full expression in small label, result in main display
        self._expr_var.set(self._expression + " =")
        self._expression = ""          # ready for new input
        self._set_display(result)

    def _toggle_sign(self):
        """Negate the current value or prepend a minus sign."""
        if self._expression:
            if self._expression.startswith("-"):
                self._expression = self._expression[1:]
            else:
                self._expression = "-" + self._expression
        else:
            current = self._display_var.get()
            if current not in ("0", "", "Error"):
                self._expression = "-" + current
        self._set_display(self._expression or "0")
        self._update_expr_label()

    def _reciprocal(self):
        """Calculate 1 / (current expression)."""
        expr = self._expression or self._display_var.get()
        if expr:
            self._expression = f"1/({expr})"
            self._calculate()

    # ── Keyboard support ─────────────────────────────────────────────────────

    def _on_key_press(self, event: tk.Event):
        """Map physical keyboard keys to calculator actions."""
        key = event.char
        keysym = event.keysym

        if key in "0123456789.":
            self._append(key)
        elif key in "+-*/":
            self._append(key)
        elif key == "^":
            self._append("^")
        elif key in ("\r", "\n") or keysym == "Return":
            self._calculate()
        elif keysym == "BackSpace":
            self._backspace()
        elif keysym == "Escape":
            self._clear()
        elif key == "(":
            self._append("(")
        elif key == ")":
            self._append(")")


# ──────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────

if __name__ == "__main__":
    app = ScientificCalculator()
    app.mainloop()
