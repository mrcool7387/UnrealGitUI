# ui/tabs/terminal.py
"""
Terminal tab with non-blocking reader and basic ANSI SGR color handling.
Works with pywinpty output that contains escape sequences (Clink, prompts, etc.)
"""

import os
import re
import threading
import queue
import customtkinter as ctk
import winpty

# ANSI SGR regex (matches sequences like \x1b[31m or \x1b[1;32m)
SGR_RE = re.compile(r'\x1b\[((?:\d{1,3};?)+)m')
# OSC (Operating System Command) sequences like ESC ] 0;title BEL or ESC ] 0;title ESC \
OSC_RE = re.compile(r'\x1b\].*?(?:\x07|\x1b\\)')
# Other CSI / control sequences (cursor moves, erase, etc.) - remove conservative set
CSI_RE = re.compile(r'\x1b\[[:<>?=\d;]*[A-Za-z]')

# Map common SGR color codes to tkinter tag names / colors (basic)
SGR_COLOR_MAP = {
    30: ("fg_black",   "#000000"),
    31: ("fg_red",     "#ff5555"),
    32: ("fg_green",   "#50fa7b"),
    33: ("fg_yellow",  "#f1fa8c"),
    34: ("fg_blue",    "#6272a4"),
    35: ("fg_magenta", "#ff79c6"),
    36: ("fg_cyan",    "#8be9fd"),
    37: ("fg_white",   "#f8f8f2"),
    90: ("fg_bright_black",   "#44475a"),
    91: ("fg_bright_red",     "#ff6e6e"),
    92: ("fg_bright_green",   "#69ff94"),
    93: ("fg_bright_yellow",  "#ffffa5"),
    94: ("fg_bright_blue",    "#caa9ff"),
    95: ("fg_bright_magenta", "#ff92df"),
    96: ("fg_bright_cyan",    "#9aedfe"),
    97: ("fg_bright_white",   "#ffffff"),
}

# Basic attributes
ATTR_BOLD = 1
ATTR_ITALIC = 3  # rarely supported in terminals
ATTR_UNDERLINE = 4
ATTR_RESET = 0

def parse_sgr_parts(sgr_code_str):
    """Return list of int codes from SGR parameter string like '1;31' -> [1,31]"""
    parts = []
    for p in sgr_code_str.split(';'):
        try:
            parts.append(int(p))
        except ValueError:
            pass
    return parts

class AnsiTextParser:
    """
    Simple ANSI SGR parser that yields (text, taglist)
    It strips OSC and many CSI sequences, and processes SGR color/bold/reset.
    Not a full terminal emulator — enough for colored prompts and outputs.
    """
    def __init__(self):
        self.reset_state()

    def reset_state(self):
        self.current_fg = None
        self.bold = False
        self.underline = False

    def _make_tags(self):
        tags = []
        if self.current_fg:
            tags.append(self.current_fg)
        if self.bold:
            tags.append("attr_bold")
        if self.underline:
            tags.append("attr_underline")
        return tags

    def feed(self, text):
        # First remove OSC and many cursor-control CSI sequences
        text = OSC_RE.sub('', text)
        text = CSI_RE.sub('', text)

        # Now iterate over SGR sequences
        pos = 0
        for match in SGR_RE.finditer(text):
            start, end = match.span()
            if start > pos:
                yield text[pos:start], self._make_tags()

            codes = parse_sgr_parts(match.group(1))
            # Apply codes
            if not codes:
                codes = [0]

            for code in codes:
                if code == ATTR_RESET:
                    self.reset_state()
                elif code == ATTR_BOLD:
                    self.bold = True
                elif code == ATTR_UNDERLINE:
                    self.underline = True
                elif 30 <= code <= 37 or 90 <= code <= 97:
                    # Set foreground
                    mapping = SGR_COLOR_MAP.get(code)
                    if mapping:
                        self.current_fg = mapping[0]
                elif code == 39:
                    # default fg
                    self.current_fg = None
                # NOTE: bg colors, 256-color, truecolor not implemented here
            pos = end

        # Remainder
        if pos < len(text):
            yield text[pos:], self._make_tags()

class TerminalUI(ctk.CTkFrame):
    def __init__(self, master, shell_cmd="cmd.exe /Q", **kwargs):
        super().__init__(master, **kwargs)

        # Text widget (CTkTextbox wraps tkinter.Text and supports tags)
        self.textbox = ctk.CTkTextbox(self, wrap="none")
        self.textbox.pack(fill="both", expand=True, padx=8, pady=8)

        # Configure tags for colors / attributes
        self._configure_tags()

        # Entry for user input
        self.entry = ctk.CTkEntry(self, placeholder_text="Befehl eingeben...")
        self.entry.pack(fill="x", padx=8, pady=(0,8))
        self.entry.bind("<Return>", self._on_enter)

        # Thread safe queue for output chunks
        self._q = queue.Queue()

        # Start pty
        self._pty = winpty.PtyProcess
        self._proc = self._pty.spawn(shell_cmd)

        # Parser instance
        self._parser = AnsiTextParser()

        # Reader thread
        self._running = True
        self._reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._reader_thread.start()

        # Start periodic GUI update
        self.after(50, self._poll_output)

        # Ensure focus on entry
        self.entry.focus_set()

    def _configure_tags(self):
        # Attribute tags
        self.textbox.tag_config("attr_bold")
        self.textbox.tag_config("attr_underline", underline=True)
        # Color tags
        for code, (tagname, hexcol) in SGR_COLOR_MAP.items():
            # CTkTextbox.tag_config accepts foreground as "fg" or "foreground"
            # Under the hood CTk uses tkinter.Text tag_config, so use foreground
            try:
                self.textbox.tag_config(tagname, foreground=hexcol)
            except Exception:
                # If CTkTextbox blocks direct tag_config, fallback to no colors
                pass

    def _reader_loop(self):
        """Background thread that reads from the PTY and pushes to queue."""
        while self._running:
            try:
                data = self._proc.read()
                if data:
                    # Ensure it's a python string
                    if isinstance(data, bytes):
                        try:
                            data = data.decode('utf-8', errors='replace')
                        except Exception:
                            data = data.decode('latin1', errors='replace')
                    self._q.put(data)
                else:
                    # small sleep to avoid busy loop if read() returns empty
                    threading.Event().wait(0.01)
            except Exception:
                threading.Event().wait(0.05)

    def _poll_output(self):
        """Called in main thread periodically to flush output queue into textbox."""
        try:
            while True:
                chunk = self._q.get_nowait()
                # Parse ANSI and insert with tags
                for txt, tags in self._parser.feed(chunk):
                    if txt:
                        # Replace carriage returns that attempt to move cursor; keep newlines
                        txt = txt.replace('\r', '')
                        # Insert preserving tags
                        if tags:
                            # Insert with multiple tags
                            self.textbox.insert("end", txt, tuple(tags))
                        else:
                            self.textbox.insert("end", txt)
                        self.textbox.see("end")
        except queue.Empty:
            pass
        # schedule next poll
        if self._running:
            self.after(50, self._poll_output)

    def _on_enter(self, event=None):
        cmd = self.entry.get()
        if not cmd:
            return
        # Send the command to the PTY (append newline)
        try:
            to_send = (cmd + "\n")
            # write expects bytes or str depending on API
            try:
                self._proc.write(to_send)
            except TypeError:
                # maybe expects bytes
                self._proc.write(to_send.encode('utf-8'))
        except Exception:
            pass
        # echo command optionally to the textbox (some shells already echo)
        # self.textbox.insert("end", f"> {cmd}\n")
        self.entry.delete(0, "end")

    def destroy(self):
        # stop reader
        self._running = False
        try:
            # try to close spawned process cleanly
            try:
                self._proc.close()
            except Exception:
                pass
        finally:
            super().destroy()
