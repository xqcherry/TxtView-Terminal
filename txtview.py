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


def fg(color: int) -> str:
    return f"\x1b[38;5;{color}m"


def bg(color: int) -> str:
    return f"\x1b[48;5;{color}m"


THEMES = [
    {"name": "ansi", "fg": 252, "muted": 244, "border": 75, "accent": 81, "title": 117, "status_bg": 236, "status_fg": 250, "code_bg": 235, "pygments": "monokai"},
    {"name": "base16", "fg": 252, "muted": 245, "border": 109, "accent": 180, "title": 116, "status_bg": 237, "status_fg": 251, "code_bg": 236, "pygments": "native"},
    {"name": "base16-eighties.dark", "fg": 252, "muted": 245, "border": 139, "accent": 215, "title": 174, "status_bg": 235, "status_fg": 251, "code_bg": 234, "pygments": "native"},
    {"name": "base16-mocha.dark", "fg": 252, "muted": 244, "border": 137, "accent": 180, "title": 109, "status_bg": 235, "status_fg": 251, "code_bg": 234, "pygments": "native"},
    {"name": "base16-ocean.dark", "fg": 252, "muted": 245, "border": 67, "accent": 110, "title": 152, "status_bg": 236, "status_fg": 251, "code_bg": 235, "pygments": "native"},
    {"name": "base16-ocean.light", "fg": 239, "muted": 246, "border": 67, "accent": 31, "title": 25, "status_bg": 250, "status_fg": 238, "code_bg": 254, "pygments": "default"},
    {"name": "base16-256", "fg": 252, "muted": 244, "border": 73, "accent": 214, "title": 150, "status_bg": 236, "status_fg": 251, "code_bg": 235, "pygments": "native"},
    {"name": "Catppuccin Frappe", "fg": 252, "muted": 146, "border": 111, "accent": 182, "title": 153, "status_bg": 60, "status_fg": 253, "code_bg": 236, "pygments": "dracula"},
    {"name": "Catppuccin Latte", "fg": 238, "muted": 103, "border": 104, "accent": 176, "title": 67, "status_bg": 254, "status_fg": 238, "code_bg": 255, "pygments": "default"},
    {"name": "Catppuccin Macchiato", "fg": 252, "muted": 146, "border": 110, "accent": 183, "title": 153, "status_bg": 60, "status_fg": 253, "code_bg": 235, "pygments": "dracula"},
    {"name": "Catppuccin Mocha", "fg": 252, "muted": 146, "border": 111, "accent": 183, "title": 153, "status_bg": 59, "status_fg": 253, "code_bg": 234, "pygments": "dracula"},
    {"name": "Coldark-Cold", "fg": 238, "muted": 244, "border": 31, "accent": 37, "title": 25, "status_bg": 254, "status_fg": 238, "code_bg": 255, "pygments": "default"},
    {"name": "Coldark-Dark", "fg": 252, "muted": 244, "border": 38, "accent": 80, "title": 110, "status_bg": 236, "status_fg": 251, "code_bg": 235, "pygments": "native"},
    {"name": "DarkNeon", "fg": 252, "muted": 246, "border": 48, "accent": 201, "title": 51, "status_bg": 235, "status_fg": 51, "code_bg": 234, "pygments": "monokai"},
    {"name": "Dracula", "fg": 253, "muted": 247, "border": 141, "accent": 212, "title": 117, "status_bg": 236, "status_fg": 253, "code_bg": 235, "pygments": "dracula"},
    {"name": "GitHub", "fg": 238, "muted": 244, "border": 32, "accent": 35, "title": 25, "status_bg": 254, "status_fg": 238, "code_bg": 255, "pygments": "default"},
    {"name": "gruvbox-dark", "fg": 223, "muted": 248, "border": 108, "accent": 214, "title": 179, "status_bg": 237, "status_fg": 223, "code_bg": 235, "pygments": "native"},
    {"name": "gruvbox-light", "fg": 238, "muted": 244, "border": 100, "accent": 166, "title": 94, "status_bg": 229, "status_fg": 238, "code_bg": 230, "pygments": "default"},
    {"name": "InspiredGitHub", "fg": 238, "muted": 244, "border": 68, "accent": 31, "title": 25, "status_bg": 254, "status_fg": 238, "code_bg": 255, "pygments": "default"},
    {"name": "1337", "fg": 46, "muted": 34, "border": 40, "accent": 82, "title": 118, "status_bg": 22, "status_fg": 46, "code_bg": 16, "pygments": "native"},
    {"name": "Monokai Extended", "fg": 252, "muted": 245, "border": 141, "accent": 148, "title": 81, "status_bg": 236, "status_fg": 251, "code_bg": 235, "pygments": "monokai"},
    {"name": "Monokai Extended Bright", "fg": 255, "muted": 248, "border": 141, "accent": 184, "title": 117, "status_bg": 237, "status_fg": 255, "code_bg": 236, "pygments": "monokai"},
    {"name": "Monokai Extended Light", "fg": 238, "muted": 245, "border": 97, "accent": 166, "title": 25, "status_bg": 254, "status_fg": 238, "code_bg": 255, "pygments": "default"},
    {"name": "Monokai Extended Origin", "fg": 252, "muted": 245, "border": 141, "accent": 197, "title": 81, "status_bg": 236, "status_fg": 251, "code_bg": 235, "pygments": "monokai"},
    {"name": "Nord", "fg": 253, "muted": 109, "border": 67, "accent": 110, "title": 153, "status_bg": 60, "status_fg": 253, "code_bg": 236, "pygments": "nord"},
    {"name": "OneHalfDark", "fg": 252, "muted": 247, "border": 75, "accent": 73, "title": 111, "status_bg": 236, "status_fg": 251, "code_bg": 235, "pygments": "native"},
    {"name": "OneHalfLight", "fg": 238, "muted": 244, "border": 67, "accent": 31, "title": 25, "status_bg": 254, "status_fg": 238, "code_bg": 255, "pygments": "default"},
    {"name": "Solarized (dark)", "fg": 244, "muted": 240, "border": 37, "accent": 136, "title": 67, "status_bg": 235, "status_fg": 244, "code_bg": 234, "pygments": "solarized-dark"},
    {"name": "Solarized (light)", "fg": 240, "muted": 244, "border": 37, "accent": 136, "title": 25, "status_bg": 230, "status_fg": 240, "code_bg": 254, "pygments": "default"},
]
THEME_INDEX = {theme["name"].lower(): i for i, theme in enumerate(THEMES)}

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


def read_text_with_encoding(path: str) -> tuple[str, str]:
    for enc in ("utf-8-sig", "utf-8", "gb18030", "gbk", "big5"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read(), enc
        except UnicodeDecodeError:
            pass
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read(), "utf-8"


def read_text(path: str) -> str:
    text, _ = read_text_with_encoding(path)
    return text


def write_text(path: str, text: str, encoding: str):
    with open(path, "w", encoding=encoding, newline="") as f:
        f.write(text)


def split_edit_lines(text: str) -> list[str]:
    return text.split("\n") if text else [""]


def join_edit_lines(lines_buf: list[str]) -> str:
    return "\n".join(lines_buf)


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


def colorize_code(code: str, lang: str, theme: dict) -> list[str]:
    if not HAS_PYGMENTS:
        return code.splitlines() or [""]
    lexer = lexer_for(lang, code)
    style = theme.get("pygments", "monokai")
    try:
        formatter = Terminal256Formatter(style=style)
    except Exception:
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


def build_rows(text: str, width: int, theme: dict) -> list[str]:
    rows = []
    lines = text.splitlines() or [""]
    in_code = False
    code_lang = ""
    code_buf = []
    fg_color = fg(theme["fg"])
    border = fg(theme["border"])
    muted = fg(theme["muted"])
    accent = fg(theme["accent"])
    title_color = "\x1b[1m" + fg(theme["title"])
    code_bg = bg(theme["code_bg"])

    def flush_code():
        nonlocal code_buf, code_lang
        code = "\n".join(code_buf)
        for colored_line in colorize_code(code, code_lang, theme):
            for part in wrap_colored_line(colored_line, width):
                rows.append(code_bg + part + RESET)
        code_buf = []
        code_lang = ""

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            if in_code:
                flush_code()
                in_code = False
                rows.append(border + fit(stripped, width) + RESET)
            else:
                in_code = True
                code_lang = stripped[3:].strip()
                rows.append(border + fit(stripped, width) + RESET)
            continue

        if in_code:
            code_buf.append(line)
            continue

        # Markdown / Codex 风格基础着色
        lstrip = line.lstrip()
        prefix = ""
        suffix = RESET + fg_color
        if lstrip.startswith("#"):
            prefix = title_color
        elif lstrip.startswith((">", "│")):
            prefix = muted
        elif lstrip.startswith(("- ", "* ", "+ ")):
            prefix = accent
        elif re.match(r"^\s*\d+[.)]\s+", line):
            prefix = accent
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
                "K": "left",
                "M": "right",
                "I": "pgup",
                "Q": "pgdn",
                "G": "home",
                "O": "end",
                "S": "delete",
            }.get(ch2, "")
        if ch == "\x1b":
            return "esc"
        if ch in ("\r", "\n"):
            return "enter"
        if ch == "\x08":
            return "backspace"
        if ch == "\x13":
            return "ctrl+s"
        return ch
    ch = sys.stdin.read(1)
    if ch == "\x1b":
        seq = sys.stdin.read(2)
        if seq == "[A": return "up"
        if seq == "[B": return "down"
        if seq == "[C": return "right"
        if seq == "[D": return "left"
        if seq == "[H": return "home"
        if seq == "[F": return "end"
        if seq == "[3":
            sys.stdin.read(1); return "delete"
        if seq == "[5":
            sys.stdin.read(1); return "pgup"
        if seq == "[6":
            sys.stdin.read(1); return "pgdn"
        return "esc"
    if ch in ("\r", "\n"):
        return "enter"
    if ch in ("\x7f", "\b"):
        return "backspace"
    if ch == "\x13":
        return "ctrl+s"
    return ch


def draw(path: str, rows: list[str], scroll: int, theme: dict, edit_mode: bool = False, dirty: bool = False, message: str = ""):
    cols, lines = shutil.get_terminal_size((100, 30))
    cols = max(cols, 50)
    lines = max(lines, 12)
    inner = cols - 2
    body_h = lines - 3
    total = len(rows)
    max_scroll = max(0, total - body_h)
    pct = 100 if max_scroll == 0 else int(scroll * 100 / max_scroll)
    name = os.path.basename(path)
    fg_color = fg(theme["fg"])
    page_bg = bg(theme["code_bg"])
    border = fg(theme["border"])
    status = bg(theme["status_bg"]) + fg(theme["status_fg"])

    esc("\x1b[H")
    flags = []
    if edit_mode:
        flags.append("EDIT")
    if dirty:
        flags.append("*")
    flag_text = f" {' '.join(flags)}" if flags else ""
    title = f" txtview: {name} [{theme['name']}]{flag_text} "
    top = "┌" + title
    esc(border + top + "─" * max(0, cols - visual_width(top) - 1) + "┐" + RESET + "\r\n")

    for i in range(body_h):
        idx = scroll + i
        raw = rows[idx] if idx < total else ""
        clean_width = visual_width(strip_ansi(raw))
        esc(border + "│" + RESET + page_bg + fg_color)
        esc(raw)
        esc(page_bg + fg_color + " " * max(0, inner - clean_width))
        esc(border + "│" + RESET + "\r\n")

    if edit_mode:
        status_text = f" 编辑: 输入文字 | Enter 换行 | Backspace/Delete 删除 | Ctrl+S 保存 | Esc 退出编辑 | {message} "
    else:
        status_text = f" ↑↓/PgUp/PgDn 滚动 | Home/End | e 编辑 | t/] 下个主题 | T/[ 上个主题 | q/Esc 退出 | {scroll + 1}/{max(total,1)} | {pct}% {message} "
    esc(border + "└" + RESET + status + fit(status_text, inner) + RESET + border + "┘" + RESET)
    flush()


def draw_editor(path: str, lines_buf: list[str], cursor_line: int, cursor_col: int, scroll: int, theme: dict, dirty: bool, message: str):
    cols, lines = shutil.get_terminal_size((100, 30))
    cols = max(cols, 50)
    lines = max(lines, 12)
    inner = cols - 2
    body_h = lines - 3
    name = os.path.basename(path)
    fg_color = fg(theme["fg"])
    page_bg = bg(theme["code_bg"])
    border = fg(theme["border"])
    status = bg(theme["status_bg"]) + fg(theme["status_fg"])

    esc("\x1b[?25l\x1b[H")
    flag_text = " EDIT * " if dirty else " EDIT "
    title = f" txtview: {name} [{theme['name']}]{flag_text}"
    top = "┌" + title
    esc(border + top + "─" * max(0, cols - visual_width(top) - 1) + "┐" + RESET + "\r\n")

    for i in range(body_h):
        idx = scroll + i
        raw = lines_buf[idx].replace("\t", "    ") if idx < len(lines_buf) else ""
        shown = fit(raw, inner)
        esc(border + "│" + RESET + page_bg + fg_color + shown + RESET + border + "│" + RESET + "\r\n")

    status_text = f" 编辑: 输入文字 | Enter 换行 | Backspace/Delete 删除 | Ctrl+S 保存 | Esc 退出编辑 | {cursor_line + 1}:{cursor_col + 1} {message} "
    esc(border + "└" + RESET + status + fit(status_text, inner) + RESET + border + "┘" + RESET)

    cursor_y = cursor_line - scroll + 2
    cursor_x = visual_width(lines_buf[cursor_line][:cursor_col].replace("\t", "    ")) + 2
    if 2 <= cursor_y < lines:
        cursor_x = max(2, min(cursor_x, cols - 1))
        esc(f"\x1b[{cursor_y};{cursor_x}H\x1b[?25h")
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


def theme_names() -> str:
    return "\n".join(theme["name"] for theme in THEMES)


def find_theme(name: str | None) -> tuple[int, dict]:
    if not name:
        return 0, THEMES[0]
    key = name.strip().lower()
    if key in THEME_INDEX:
        idx = THEME_INDEX[key]
        return idx, THEMES[idx]
    matches = [i for i, theme in enumerate(THEMES) if theme["name"].lower().startswith(key)]
    if len(matches) == 1:
        idx = matches[0]
        return idx, THEMES[idx]
    return 0, THEMES[0]


def parse_args(argv: list[str]) -> tuple[str | None, int, bool]:
    path = None
    theme_name = os.environ.get("TXTVIEW_THEME")
    list_themes = False
    i = 1
    while i < len(argv):
        arg = argv[i]
        if arg in ("--list-themes", "--themes"):
            list_themes = True
        elif arg in ("--theme", "-t"):
            i += 1
            if i < len(argv):
                theme_name = argv[i]
        elif arg.startswith("--theme="):
            theme_name = arg.split("=", 1)[1]
        elif arg in ("-h", "--help"):
            print("Usage: python txtview.py [--theme NAME] [--list-themes] [file]")
            print()
            print("Themes:")
            print(theme_names())
            raise SystemExit(0)
        elif path is None:
            path = arg
        i += 1
    theme_idx, _ = find_theme(theme_name)
    return path, theme_idx, list_themes


def main():
    path, theme_idx, list_themes = parse_args(sys.argv)
    if list_themes:
        print(theme_names())
        return
    if not path:
        path = pick_file()
    if not path:
        return

    text, encoding = read_text_with_encoding(path)
    edit_lines = split_edit_lines(text)

    with Terminal():
        last_width = -1
        last_theme_idx = -1
        rows = []
        scroll = 0
        edit_mode = False
        dirty = False
        cursor_line = 0
        cursor_col = 0
        message = ""
        confirm_quit = False
        while True:
            theme = THEMES[theme_idx]
            cols, lines = shutil.get_terminal_size((100, 30))
            inner = max(20, cols - 2)
            body_h = max(5, lines - 3)
            if edit_mode:
                cursor_line = max(0, min(cursor_line, len(edit_lines) - 1))
                cursor_col = max(0, min(cursor_col, len(edit_lines[cursor_line])))
                if cursor_line < scroll:
                    scroll = cursor_line
                elif cursor_line >= scroll + body_h:
                    scroll = cursor_line - body_h + 1
                max_scroll = max(0, len(edit_lines) - body_h)
                scroll = max(0, min(scroll, max_scroll))
                draw_editor(path, edit_lines, cursor_line, cursor_col, scroll, theme, dirty, message)
            else:
                if inner != last_width or theme_idx != last_theme_idx:
                    rows = build_rows(text, inner, theme)
                    last_width = inner
                    last_theme_idx = theme_idx
                max_scroll = max(0, len(rows) - body_h)
                scroll = max(0, min(scroll, max_scroll))
                draw(path, rows, scroll, theme, edit_mode, dirty, message)

            key = get_key()
            message = ""

            if edit_mode:
                confirm_quit = False
                if key == "ctrl+s":
                    text = join_edit_lines(edit_lines)
                    write_text(path, text, encoding)
                    dirty = False
                    rows = []
                    last_width = -1
                    message = "已保存"
                elif key == "esc":
                    edit_mode = False
                    text = join_edit_lines(edit_lines)
                    rows = []
                    last_width = -1
                    message = "已退出编辑" if dirty else ""
                elif key == "up":
                    cursor_line -= 1
                    if cursor_line >= 0:
                        cursor_col = min(cursor_col, len(edit_lines[cursor_line]))
                elif key == "down":
                    cursor_line += 1
                    if cursor_line < len(edit_lines):
                        cursor_col = min(cursor_col, len(edit_lines[cursor_line]))
                elif key == "left":
                    if cursor_col > 0:
                        cursor_col -= 1
                    elif cursor_line > 0:
                        cursor_line -= 1
                        cursor_col = len(edit_lines[cursor_line])
                elif key == "right":
                    if cursor_col < len(edit_lines[cursor_line]):
                        cursor_col += 1
                    elif cursor_line < len(edit_lines) - 1:
                        cursor_line += 1
                        cursor_col = 0
                elif key == "home":
                    cursor_col = 0
                elif key == "end":
                    cursor_col = len(edit_lines[cursor_line])
                elif key == "pgup":
                    cursor_line = max(0, cursor_line - body_h)
                    cursor_col = min(cursor_col, len(edit_lines[cursor_line]))
                elif key == "pgdn":
                    cursor_line = min(len(edit_lines) - 1, cursor_line + body_h)
                    cursor_col = min(cursor_col, len(edit_lines[cursor_line]))
                elif key == "enter":
                    line = edit_lines[cursor_line]
                    edit_lines[cursor_line] = line[:cursor_col]
                    edit_lines.insert(cursor_line + 1, line[cursor_col:])
                    cursor_line += 1
                    cursor_col = 0
                    dirty = True
                elif key == "backspace":
                    if cursor_col > 0:
                        line = edit_lines[cursor_line]
                        edit_lines[cursor_line] = line[:cursor_col - 1] + line[cursor_col:]
                        cursor_col -= 1
                        dirty = True
                    elif cursor_line > 0:
                        prev_len = len(edit_lines[cursor_line - 1])
                        edit_lines[cursor_line - 1] += edit_lines.pop(cursor_line)
                        cursor_line -= 1
                        cursor_col = prev_len
                        dirty = True
                elif key == "delete":
                    line = edit_lines[cursor_line]
                    if cursor_col < len(line):
                        edit_lines[cursor_line] = line[:cursor_col] + line[cursor_col + 1:]
                        dirty = True
                    elif cursor_line < len(edit_lines) - 1:
                        edit_lines[cursor_line] += edit_lines.pop(cursor_line + 1)
                        dirty = True
                elif len(key) == 1 and ord(key) >= 32:
                    line = edit_lines[cursor_line]
                    edit_lines[cursor_line] = line[:cursor_col] + key + line[cursor_col:]
                    cursor_col += 1
                    dirty = True
                continue

            if key == "ctrl+s" and dirty:
                text = join_edit_lines(edit_lines)
                write_text(path, text, encoding)
                dirty = False
                rows = []
                last_width = -1
                message = "已保存"
                confirm_quit = False
            elif key in ("q", "Q", "esc"):
                if dirty and not confirm_quit:
                    message = "有未保存修改，再按 q/Esc 放弃退出，或按 e 后 Ctrl+S 保存"
                    confirm_quit = True
                    continue
                break
            elif key in ("e", "E"):
                edit_mode = True
                edit_lines = split_edit_lines(text)
                cursor_line = min(scroll, len(edit_lines) - 1)
                cursor_col = 0
                confirm_quit = False
            elif key in ("t", "]"):
                theme_idx = (theme_idx + 1) % len(THEMES)
                confirm_quit = False
            elif key in ("T", "["):
                theme_idx = (theme_idx - 1) % len(THEMES)
                confirm_quit = False
            elif key == "up":
                scroll -= 1
                confirm_quit = False
            elif key == "down":
                scroll += 1
                confirm_quit = False
            elif key == "pgup":
                scroll -= body_h
                confirm_quit = False
            elif key == "pgdn":
                scroll += body_h
                confirm_quit = False
            elif key == "home":
                scroll = 0
                confirm_quit = False
            elif key == "end":
                scroll = max_scroll
                confirm_quit = False


if __name__ == "__main__":
    main()
