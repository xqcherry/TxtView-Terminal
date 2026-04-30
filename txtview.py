import os
import sys
import shutil
import textwrap
import re
import tkinter as tk
from tkinter import filedialog

IS_WIN = os.name == "nt"

if IS_WIN:
    import msvcrt
    import ctypes

    kernel32 = ctypes.windll.kernel32
    STD_OUTPUT_HANDLE = -11
    ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004

    def enable_ansi():
        handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)

else:
    import termios
    import tty


RESET = "\x1b[0m"
CYAN = "\x1b[38;5;81m"
BLUE = "\x1b[38;5;75m"
MUTED = "\x1b[38;5;244m"
FG = "\x1b[38;5;252m"
DIM = "\x1b[38;5;240m"
STATUS = "\x1b[48;5;236m\x1b[38;5;250m"
TITLE = "\x1b[1m\x1b[38;5;117m"
CODE_BG = "\x1b[48;5;235m"

try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, guess_lexer, TextLexer
    from pygments.formatters import Terminal256Formatter
    HAS_PYGMENTS = True
except Exception:
    HAS_PYGMENTS = False
    highlight = None
    TextLexer = None



def esc(s: str):
    sys.stdout.write(s)


def flush():
    sys.stdout.flush()


def read_text(path: str) -> str:
    for enc in ("utf-8-sig", "utf-8", "gb18030", "gbk", "big5"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            pass
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def pick_file() -> str | None:
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    path = filedialog.askopenfilename(
        title="选择 TXT 文件",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
    )
    root.destroy()
    return path or None


def visual_width(s: str) -> int:
    w = 0
    for ch in s:
        code = ord(ch)
        if code < 32:
            continue
        if (
            0x1100 <= code <= 0x115F
            or code in (0x2329, 0x232A)
            or 0x2E80 <= code <= 0xA4CF
            or 0xAC00 <= code <= 0xD7A3
            or 0xF900 <= code <= 0xFAFF
            or 0xFE10 <= code <= 0xFE19
            or 0xFE30 <= code <= 0xFE6F
            or 0xFF00 <= code <= 0xFF60
            or 0xFFE0 <= code <= 0xFFE6
        ):
            w += 2
        else:
            w += 1
    return w


def fit(s: str, width: int) -> str:
    out = []
    w = 0
    for ch in s:
        cw = visual_width(ch)
        if w + cw > width:
            break
        out.append(ch)
        w += cw
    return "".join(out) + " " * max(0, width - w)


def wrap_line(line: str, width: int) -> list[str]:
    line = line.replace("\t", "    ").rstrip("\r")
    if not line:
        return [""]
    rows = []
    cur = []
    w = 0
    for ch in line:
        cw = visual_width(ch)
        if w and w + cw > width:
            rows.append("".join(cur))
            cur = []
            w = 0
        cur.append(ch)
        w += cw
    rows.append("".join(cur))
    return rows


def lexer_for(lang: str, code: str):
    if not HAS_PYGMENTS:
        return None
    lang = (lang or "").strip().lower()
    aliases = {
        "py": "python", "python3": "python", "js": "javascript", "ts": "typescript",
        "tsx": "tsx", "jsx": "jsx", "c++": "cpp", "cc": "cpp", "h": "cpp",
        "rs": "rust", "sh": "bash", "shell": "bash", "ps1": "powershell",
        "md": "markdown", "yml": "yaml",
    }
    lang = aliases.get(lang, lang)
    try:
        if lang:
            return get_lexer_by_name(lang)
    except Exception:
        pass
    try:
        return guess_lexer(code)
    except Exception:
        return TextLexer()


def colorize_code(code: str, lang: str) -> list[str]:
    if not HAS_PYGMENTS:
        return code.splitlines() or [""]
    lexer = lexer_for(lang, code)
    formatter = Terminal256Formatter(style="monokai")
    colored = highlight(code, lexer, formatter).rstrip("\n")
    return colored.splitlines() or [""]


def wrap_colored_line(line: str, width: int) -> list[str]:
    """Wrap ANSI-colored text while preserving escape sequences."""
    rows = []
    cur = []
    w = 0
    i = 0
    active = ""
    while i < len(line):
        if line[i] == "\x1b":
            j = i + 1
            while j < len(line) and line[j] != "m":
                j += 1
            seq = line[i:j + 1]
            cur.append(seq)
            active = "" if seq == RESET else active + seq
            i = j + 1
            continue
        ch = line[i]
        cw = visual_width(ch)
        if w and w + cw > width:
            rows.append("".join(cur) + RESET)
            cur = [active] if active else []
            w = 0
        cur.append(ch)
        w += cw
        i += 1
    rows.append("".join(cur) if cur else "")
    return rows


def build_rows(text: str, width: int) -> list[str]:
    rows = []
    lines = text.splitlines() or [""]
    in_code = False
    code_lang = ""
    code_buf = []

    def flush_code():
        nonlocal code_buf, code_lang
        code = "\n".join(code_buf)
        for colored_line in colorize_code(code, code_lang):
            for part in wrap_colored_line(colored_line, width):
                rows.append(CODE_BG + part + RESET)
        code_buf = []
        code_lang = ""

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            if in_code:
                flush_code()
                in_code = False
                rows.append(BLUE + fit(stripped, width) + RESET)
            else:
                in_code = True
                code_lang = stripped[3:].strip()
                rows.append(BLUE + fit(stripped, width) + RESET)
            continue

        if in_code:
            code_buf.append(line)
            continue

        # Markdown / Codex 风格基础着色
        lstrip = line.lstrip()
        prefix = ""
        suffix = RESET + FG
        if lstrip.startswith("#"):
            prefix = TITLE
        elif lstrip.startswith((">", "│")):
            prefix = MUTED
        elif lstrip.startswith(("- ", "* ", "+ ")):
            prefix = CYAN
        elif re.match(r"^\s*\d+[.)]\s+", line):
            prefix = CYAN
        for part in wrap_line(line, width):
            rows.append(prefix + part + suffix if prefix else part)

    if in_code:
        flush_code()
    return rows


class Terminal:
    def __enter__(self):
        if IS_WIN:
            enable_ansi()
        else:
            self.old = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())
        esc("\x1b[?1049h\x1b[?25l\x1b[2J")
        flush()
        return self

    def __exit__(self, exc_type, exc, tb):
        esc(RESET + "\x1b[?25h\x1b[?1049l")
        flush()
        if not IS_WIN:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old)


def get_key() -> str:
    if IS_WIN:
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):
            ch2 = msvcrt.getwch()
            return {
                "H": "up",
                "P": "down",
                "I": "pgup",
                "Q": "pgdn",
                "G": "home",
                "O": "end",
            }.get(ch2, "")
        if ch == "\x1b":
            return "esc"
        return ch.lower()
    ch = sys.stdin.read(1)
    if ch == "\x1b":
        seq = sys.stdin.read(2)
        if seq == "[A": return "up"
        if seq == "[B": return "down"
        if seq == "[H": return "home"
        if seq == "[F": return "end"
        if seq == "[5":
            sys.stdin.read(1); return "pgup"
        if seq == "[6":
            sys.stdin.read(1); return "pgdn"
        return "esc"
    return ch.lower()


def draw(path: str, rows: list[str], scroll: int):
    cols, lines = shutil.get_terminal_size((100, 30))
    cols = max(cols, 50)
    lines = max(lines, 12)
    inner = cols - 2
    body_h = lines - 3
    total = len(rows)
    max_scroll = max(0, total - body_h)
    pct = 100 if max_scroll == 0 else int(scroll * 100 / max_scroll)
    name = os.path.basename(path)

    esc("\x1b[H")
    title = f" txtview: {name} "
    top = "┌" + title
    esc(BLUE + top + "─" * max(0, cols - visual_width(top) - 1) + "┐" + RESET + "\r\n")

    for i in range(body_h):
        idx = scroll + i
        raw = rows[idx] if idx < total else ""
        clean_width = visual_width(strip_ansi(raw))
        esc(BLUE + "│" + RESET + FG)
        esc(raw)
        esc(" " * max(0, inner - clean_width))
        esc(BLUE + "│" + RESET + "\r\n")

    status = f" ↑↓/PgUp/PgDn 滚动 | Home/End | q/Esc 退出 | {scroll + 1}/{max(total,1)} | {pct}% "
    esc(BLUE + "└" + RESET + STATUS + fit(status, inner) + RESET + BLUE + "┘" + RESET)
    flush()


def strip_ansi(s: str) -> str:
    out = []
    i = 0
    while i < len(s):
        if s[i] == "\x1b":
            i += 1
            while i < len(s) and s[i] != "m":
                i += 1
            i += 1
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else None
    if not path:
        path = pick_file()
    if not path:
        return

    text = read_text(path)

    with Terminal():
        last_width = -1
        rows = []
        scroll = 0
        while True:
            cols, lines = shutil.get_terminal_size((100, 30))
            inner = max(20, cols - 2)
            body_h = max(5, lines - 3)
            if inner != last_width:
                rows = build_rows(text, inner)
                last_width = inner
            max_scroll = max(0, len(rows) - body_h)
            scroll = max(0, min(scroll, max_scroll))
            draw(path, rows, scroll)

            key = get_key()
            if key in ("q", "esc"):
                break
            elif key == "up":
                scroll -= 1
            elif key == "down":
                scroll += 1
            elif key == "pgup":
                scroll -= body_h
            elif key == "pgdn":
                scroll += body_h
            elif key == "home":
                scroll = 0
            elif key == "end":
                scroll = max_scroll


if __name__ == "__main__":
    main()
