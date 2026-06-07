#!/usr/bin/env python3
"""
utils/text_editor/editor.py  —  Multi-tab text editor

Features
  · ≤10 tabs  ·  close without saving (changes discarded)
  · Session restore — reopens previous files on next launch
  · Zoom: Ctrl+wheel | Ctrl+= | Ctrl+- | Ctrl+0  (all tabs)
  · XML syntax highlighting  (auto, by .xml extension)
  · XML node fold / unfold   (click ▼/▶ in the line-number gutter)

Usage
  python utils/text_editor/editor.py [file ...]
  (or double-click if .py files are associated with Python)
"""
from __future__ import annotations

import json
import os
import re
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Optional

# ── Configuration ─────────────────────────────────────────────────────────────
MAX_TABS            = 10
FONT_FAMILY         = "Courier New"
FONT_SIZE_DEFAULT   = 11
FONT_SIZE_MIN       = 6
FONT_SIZE_MAX       = 48
FONT_SIZE_STEP      = 2

# Session file lives in the user's home directory
SESSION_FILE = Path.home() / ".gfl2_text_editor_session.json"

# ── Dark (VS-Code-like) colour palette ───────────────────────────────────────
BG          = "#1E1E1E"   # editor background
FG          = "#D4D4D4"   # editor foreground
BG_GUTTER   = "#252526"   # gutter background
FG_GUTTER   = "#858585"   # line-number colour
C_FOLD      = "#569CD6"   # fold-marker colour
C_SEL_BG    = "#264F78"   # selection background
C_CURSOR    = "#AEAFAD"   # text cursor
C_STATUS_BG = "#007ACC"   # status-bar background

# XML highlight colours
_XML_COLORS: dict[str, str] = {
    "comment": "#6A9955",
    "cdata":   "#D7BA7D",
    "pi":      "#C586C0",   # processing instructions + DOCTYPE
    "bracket": "#808080",   # < > /
    "tag":     "#569CD6",   # element names
    "attr":    "#9CDCFE",   # attribute names
    "value":   "#CE9178",   # attribute values (quoted strings)
    "entity":  "#4EC9B0",   # &amp; &lt; …
}


# ── XML helpers ───────────────────────────────────────────────────────────────

def _is_xml(path: Optional[str]) -> bool:
    return bool(path and path.lower().endswith(".xml"))


def _apply_xml_highlight(widget: tk.Text, font_size: int) -> None:
    """Repaint all XML syntax tags on the widget content."""
    for tag in _XML_COLORS:
        widget.tag_remove(tag, "1.0", "end")

    content = widget.get("1.0", "end-1c")
    if not content.strip():
        return

    def _mark(pattern: str, tag: str, group: int = 0,
              flags: int = re.DOTALL) -> None:
        for m in re.finditer(pattern, content, flags):
            s, e = m.span(group)
            widget.tag_add(tag, f"1.0+{s}c", f"1.0+{e}c")

    # Apply in priority order (later calls overwrite earlier for overlaps)
    _mark(r"<!--.*?-->",                              "comment")
    _mark(r"<!\[CDATA\[.*?\]\]>",                    "cdata")
    _mark(r"<\?.*?\?>",                              "pi")
    _mark(r"<!DOCTYPE\b[^>]*>",                      "pi", flags=re.IGNORECASE | re.DOTALL)
    _mark(r"[<>/]",                                  "bracket")
    _mark(r"</?([A-Za-z_:][A-Za-z0-9_:.-]*)",       "tag",   group=1)
    _mark(r"\s([A-Za-z_:][A-Za-z0-9_:.-]*)=",       "attr",  group=1)
    _mark(r'"[^"]*"',                                "value")
    _mark(r"'[^']*'",                                "value")
    _mark(r"&[A-Za-z0-9#]+;",                        "entity")

    # Italic comment (font must be re-applied after font-size changes)
    widget.tag_configure("comment",
                         font=(FONT_FAMILY, font_size, "italic"))


def _find_xml_folds(content: str) -> list[tuple[int, int]]:
    """
    Return 1-based (open_line, close_line) pairs for multi-line XML elements.
    Only elements whose inner content spans ≥1 line are returned.
    """
    stack:  list[tuple[str, int]] = []
    result: list[tuple[int, int]] = []

    for lineno, line in enumerate(content.split("\n"), start=1):
        # Opening tags whose matching close is NOT on the same line
        for m in re.finditer(
                r"<([A-Za-z_:][A-Za-z0-9_:.-]*)(?:\s[^>]*)?>", line):
            tag = m.group(1)
            if not re.search(rf"</{re.escape(tag)}>", line):
                stack.append((tag, lineno))

        # Closing tags
        for m in re.finditer(r"</([A-Za-z_:][A-Za-z0-9_:.-]*)>", line):
            tag = m.group(1)
            for j in range(len(stack) - 1, -1, -1):
                if stack[j][0] == tag:
                    open_ln = stack[j][1]
                    stack.pop(j)
                    if open_ln < lineno - 1:
                        result.append((open_ln, lineno))
                    break

    return result


# ── FoldManager ───────────────────────────────────────────────────────────────

class FoldManager:
    """
    Uses the Text widget's built-in `elide` tag feature to hide / show
    the inner lines of an XML element.  Each foldable region gets a
    dedicated tag; setting elide=True on that tag hides its characters
    without removing them from the buffer.
    """

    def __init__(self, widget: tk.Text) -> None:
        self._w    = widget
        self._map: dict[int, dict] = {}   # open_line → {close, tag, folded}
        self._seq  = 0

    # ── public ──────────────────────────────────────────────────────────────

    def clear(self) -> None:
        """Remove all fold tags from the widget."""
        for info in self._map.values():
            try:
                self._w.tag_delete(info["tag"])
            except Exception:
                pass
        self._map.clear()

    def scan(self, content: str) -> None:
        """Detect foldable regions from content and register elide tags."""
        self.clear()
        for (ol, cl) in _find_xml_folds(content):
            self._seq += 1
            tag = f"_fold_{self._seq}"
            self._w.tag_configure(tag, elide=False)
            # Cover lines ol+1 … cl-1  (inner content, not the tag lines)
            self._w.tag_add(tag, f"{ol + 1}.0", f"{cl}.0")
            self._map[ol] = {"close": cl, "tag": tag, "folded": False}

    def toggle(self, open_line: int) -> None:
        if open_line not in self._map:
            return
        info = self._map[open_line]
        info["folded"] = not info["folded"]
        self._w.tag_configure(info["tag"], elide=info["folded"])

    def is_foldable(self, line: int) -> bool:
        return line in self._map

    def is_folded(self, line: int) -> bool:
        return self._map.get(line, {}).get("folded", False)


# ── Gutter ────────────────────────────────────────────────────────────────────

class Gutter(tk.Canvas):
    """
    Left-side canvas showing line numbers and (for XML) fold markers.
    Syncs with the Text widget's vertical scroll position.
    Clicking a ▼/▶ marker toggles the fold for that line.
    """

    WIDTH = 56   # canvas width in pixels

    def __init__(self, parent: tk.Widget,
                 text: tk.Text, folds: FoldManager) -> None:
        super().__init__(parent, width=self.WIDTH,
                         background=BG_GUTTER, highlightthickness=0)
        self._text   = text
        self._folds  = folds
        self._xml    = False
        self._job    = None   # pending after_idle redraw handle

        self.bind("<Button-1>", self._on_click)
        # Forward scroll events to the text widget
        self.bind("<MouseWheel>",
                  lambda e: text.yview_scroll(int(-e.delta / 120), "units"))
        self.bind("<Button-4>", lambda e: text.yview_scroll(-3, "units"))
        self.bind("<Button-5>", lambda e: text.yview_scroll(+3, "units"))

    # ── public ──────────────────────────────────────────────────────────────

    def set_xml(self, enabled: bool) -> None:
        self._xml = enabled

    def schedule_redraw(self, *_) -> None:
        """Debounced redraw: coalesces rapid events into one after_idle call."""
        if self._job is not None:
            self.after_cancel(self._job)
        self._job = self.after_idle(self.redraw)

    def redraw(self) -> None:
        self._job = None
        self.delete("all")
        tw = self._text
        h  = max(self.winfo_height(), 100)

        try:
            first_line = int(tw.index("@0,0").split(".")[0])
            last_line  = int(tw.index("end-1c").split(".")[0])
        except tk.TclError:
            return

        # Font size for gutter labels (2pt smaller than editor font)
        try:
            font_desc = str(tw.cget("font"))
            parts = font_desc.replace("{", "").replace("}", "").split()
            editor_size = int(next(p for p in reversed(parts) if p.isdigit()))
        except Exception:
            editor_size = FONT_SIZE_DEFAULT
        gfont = (FONT_FAMILY, max(editor_size - 2, 7))

        for ln in range(first_line, last_line + 1):
            try:
                dl = tw.dlineinfo(f"{ln}.0")
            except tk.TclError:
                break
            if dl is None:
                continue          # line is elided (folded) or off-screen
            _, y, _, lh, _ = dl
            if y > h:
                break
            cy = y + lh // 2

            # Line number (right-aligned, leaving room for fold marker)
            self.create_text(self.WIDTH - 18, cy, text=str(ln),
                             anchor="e", fill=FG_GUTTER, font=gfont)

            # Fold marker (XML only)
            if self._xml and self._folds.is_foldable(ln):
                sym = "▶" if self._folds.is_folded(ln) else "▼"
                self.create_text(self.WIDTH - 4, cy, text=sym,
                                 anchor="e", fill=C_FOLD, font=gfont)

    # ── internal ────────────────────────────────────────────────────────────

    def _on_click(self, event: tk.Event) -> None:
        if not self._xml:
            return
        try:
            ln = int(self._text.index(f"@0,{event.y}").split(".")[0])
        except tk.TclError:
            return
        if self._folds.is_foldable(ln):
            self._folds.toggle(ln)
            self.redraw()


# ── EditorTab ─────────────────────────────────────────────────────────────────

class EditorTab:
    """One notebook tab: gutter + text area + scrollbars."""

    def __init__(self, notebook: ttk.Notebook,
                 path: Optional[str],
                 font_size: int) -> None:
        self.path      = path
        self.font_size = font_size
        self.is_xml    = _is_xml(path)

        # Outer frame
        self.frame = tk.Frame(notebook, background=BG)
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)

        # Text widget
        self.tw = tk.Text(
            self.frame, wrap=tk.NONE, undo=True,
            font=(FONT_FAMILY, font_size),
            background=BG, foreground=FG,
            insertbackground=C_CURSOR,
            selectbackground=C_SEL_BG, selectforeground=FG,
            relief="flat", borderwidth=0,
            padx=4, pady=2,
        )

        # Fold manager and gutter
        self.folds  = FoldManager(self.tw)
        self.gutter = Gutter(self.frame, self.tw, self.folds)

        # Scrollbars
        self._vsb = ttk.Scrollbar(self.frame, orient="vertical",
                                  command=self.tw.yview)
        hsb = ttk.Scrollbar(self.frame, orient="horizontal",
                            command=self.tw.xview)
        self.tw.configure(
            yscrollcommand=self._on_yscroll,
            xscrollcommand=hsb.set,
        )

        # Grid layout: gutter | text | vsb / hsb
        self.gutter.grid(row=0, column=0, sticky="nsw")
        self.tw.grid(    row=0, column=1, sticky="nsew")
        self._vsb.grid(  row=0, column=2, sticky="ns")
        hsb.grid(        row=1, column=1, sticky="ew")

        # Configure XML colour tags
        for tag, colour in _XML_COLORS.items():
            self.tw.tag_configure(tag, foreground=colour)

        # Sync gutter on edits and resizes
        self.gutter.set_xml(self.is_xml)
        self.tw.bind("<KeyRelease>", self.gutter.schedule_redraw, add=True)
        self.tw.bind("<Configure>",  self.gutter.schedule_redraw, add=True)
        self.tw.bind("<FocusIn>",    self.gutter.schedule_redraw, add=True)

        self._load_file()

    # ── properties ──────────────────────────────────────────────────────────

    @property
    def title(self) -> str:
        return os.path.basename(self.path) if self.path else "Untitled"

    # ── zoom ────────────────────────────────────────────────────────────────

    def apply_font_size(self, size: int) -> None:
        self.font_size = size
        self.tw.configure(font=(FONT_FAMILY, size))
        if self.is_xml:
            self.tw.tag_configure("comment",
                                  font=(FONT_FAMILY, size, "italic"))
        self.gutter.schedule_redraw()

    # ── internal ────────────────────────────────────────────────────────────

    def _on_yscroll(self, *args) -> None:
        self._vsb.set(*args)
        self.gutter.schedule_redraw()

    def _load_file(self) -> None:
        if not self.path or not os.path.isfile(self.path):
            return
        try:
            content = Path(self.path).read_text(encoding="utf-8",
                                                errors="replace")
        except OSError:
            return
        self.tw.delete("1.0", "end")
        self.tw.insert("1.0", content)
        self.tw.edit_reset()          # clear undo history after load
        self.tw.mark_set("insert", "1.0")
        self.tw.see("1.0")
        if self.is_xml:
            _apply_xml_highlight(self.tw, self.font_size)
            self.folds.scan(content)
        self.gutter.schedule_redraw()


# ── App ───────────────────────────────────────────────────────────────────────

class App:
    """Main application window."""

    def __init__(self, root: tk.Tk, initial_files: list[str]) -> None:
        self._root      = root
        self._tabs:     list[EditorTab] = []
        self._font_size = FONT_SIZE_DEFAULT

        self._configure_root()
        self._build_style()
        self._build_menu()
        self._build_notebook()
        self._build_statusbar()
        self._bind_keys()

        # Session restore or command-line files
        files_to_open = initial_files or self._restore_session()
        for path in files_to_open:
            if os.path.isfile(path):
                self._open_path(path, silent=True)

        if not self._tabs:
            self._new_tab()   # always start with at least one tab

        root.protocol("WM_DELETE_WINDOW", self._quit)
        root.after(50, self._nb.focus_set)

    # ── Setup ────────────────────────────────────────────────────────────────

    def _configure_root(self) -> None:
        self._root.title("Text Editor")
        self._root.geometry("1280x800")
        self._root.minsize(600, 400)
        self._root.configure(background=BG)
        self._root.option_add("*tearOff", False)

    def _build_style(self) -> None:
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("TNotebook",
                    background=BG, borderwidth=0, tabmargins=[0, 0, 0, 0])
        s.configure("TNotebook.Tab",
                    background="#2D2D2D", foreground="#CCCCCC",
                    padding=[12, 5], borderwidth=0, focuscolor=BG)
        s.map("TNotebook.Tab",
              background=[("selected", BG), ("active", "#3E3E3E")],
              foreground=[("selected", "#FFFFFF")])
        s.configure("TScrollbar",
                    background="#3C3C3C", troughcolor=BG,
                    arrowcolor=FG, borderwidth=0, relief="flat")
        s.configure("TScrollbar.thumb", background="#5A5A5A")

    def _build_menu(self) -> None:
        opts = dict(bg="#2D2D2D", fg=FG,
                    activebackground="#3E3E3E", activeforeground=FG,
                    relief="flat", borderwidth=1)
        mb = tk.Menu(self._root, **opts)
        self._root.config(menu=mb)

        # File menu
        fm = tk.Menu(mb, **opts)
        mb.add_cascade(label="File", menu=fm)
        fm.add_command(label="Open…",    accelerator="Ctrl+O",
                       command=self._open_dialog)
        fm.add_command(label="Close Tab", accelerator="Ctrl+W",
                       command=self._close_current_tab)
        fm.add_separator()
        fm.add_command(label="Exit",     accelerator="Ctrl+Q",
                       command=self._quit)

        # View menu
        vm = tk.Menu(mb, **opts)
        mb.add_cascade(label="View", menu=vm)
        vm.add_command(label="Zoom In",    accelerator="Ctrl+=",
                       command=lambda: self._zoom(+FONT_SIZE_STEP))
        vm.add_command(label="Zoom Out",   accelerator="Ctrl+-",
                       command=lambda: self._zoom(-FONT_SIZE_STEP))
        vm.add_command(label="Reset Zoom", accelerator="Ctrl+0",
                       command=self._zoom_reset)

    def _build_notebook(self) -> None:
        self._nb = ttk.Notebook(self._root)
        self._nb.pack(fill="both", expand=True)
        self._nb.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self._nb.bind("<Button-3>",             self._tab_context_menu)

    def _build_statusbar(self) -> None:
        self._status_var = tk.StringVar(value="")
        tk.Label(
            self._root, textvariable=self._status_var,
            background=C_STATUS_BG, foreground="white",
            anchor="w", padx=8, pady=2,
            font=(FONT_FAMILY, 9),
        ).pack(fill="x", side="bottom")

    def _bind_keys(self) -> None:
        r = self._root
        r.bind("<Control-o>",      lambda e: self._open_dialog())
        r.bind("<Control-w>",      lambda e: self._close_current_tab())
        r.bind("<Control-q>",      lambda e: self._quit())
        r.bind("<Control-equal>",  lambda e: self._zoom(+FONT_SIZE_STEP))
        r.bind("<Control-plus>",   lambda e: self._zoom(+FONT_SIZE_STEP))
        r.bind("<Control-minus>",  lambda e: self._zoom(-FONT_SIZE_STEP))
        r.bind("<Control-0>",      lambda e: self._zoom_reset())
        # Ctrl+scroll: Windows uses delta, Linux uses Button-4/5
        r.bind("<Control-MouseWheel>",
               lambda e: self._zoom(
                   +FONT_SIZE_STEP if e.delta > 0 else -FONT_SIZE_STEP))
        r.bind("<Control-Button-4>", lambda e: self._zoom(+FONT_SIZE_STEP))
        r.bind("<Control-Button-5>", lambda e: self._zoom(-FONT_SIZE_STEP))
        # Status bar updates
        r.bind("<KeyRelease>",    self._update_status, add=True)
        r.bind("<ButtonRelease>", self._update_status, add=True)

    # ── Tab management ───────────────────────────────────────────────────────

    def _new_tab(self, path: Optional[str] = None) -> Optional[EditorTab]:
        if len(self._tabs) >= MAX_TABS:
            messagebox.showwarning(
                "Tab limit reached",
                f"Cannot open more than {MAX_TABS} tabs at once.\n"
                "Close a tab first.")
            return None
        tab = EditorTab(self._nb, path, self._font_size)
        self._tabs.append(tab)
        self._nb.add(tab.frame, text=f"  {tab.title}  ")
        self._nb.select(tab.frame)
        self._update_status()
        return tab

    def _open_path(self, path: str, silent: bool = False) -> None:
        # If already open, just focus that tab
        norm = os.path.normpath(path)
        for tab in self._tabs:
            if tab.path and os.path.normpath(tab.path) == norm:
                self._nb.select(tab.frame)
                return
        self._new_tab(path)

    def _open_dialog(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Open file(s)",
            filetypes=[
                ("All files",    "*.*"),
                ("XML files",    "*.xml"),
                ("Text files",   "*.txt"),
                ("Python files", "*.py"),
                ("JSON files",   "*.json"),
            ])
        for p in paths:
            self._open_path(p)

    def _close_tab(self, idx: int) -> None:
        if not (0 <= idx < len(self._tabs)):
            return
        self._nb.forget(idx)
        self._tabs.pop(idx)
        if not self._tabs:
            self._new_tab()   # always keep at least one tab

    def _close_current_tab(self) -> None:
        idx = self._current_index()
        if idx is not None:
            self._close_tab(idx)

    def _tab_context_menu(self, event: tk.Event) -> None:
        try:
            idx = self._nb.index(f"@{event.x},{event.y}")
        except tk.TclError:
            return
        m = tk.Menu(self._root, tearoff=False,
                    bg="#2D2D2D", fg=FG,
                    activebackground="#3E3E3E", activeforeground=FG,
                    relief="flat")
        m.add_command(label="Close Tab",
                      command=lambda i=idx: self._close_tab(i))
        m.tk_popup(event.x_root, event.y_root)

    def _on_tab_changed(self, *_) -> None:
        self._update_status()

    # ── Zoom ─────────────────────────────────────────────────────────────────

    def _zoom(self, delta: int) -> None:
        self._font_size = max(FONT_SIZE_MIN,
                              min(FONT_SIZE_MAX, self._font_size + delta))
        for tab in self._tabs:
            tab.apply_font_size(self._font_size)
        self._update_status()

    def _zoom_reset(self) -> None:
        self._font_size = FONT_SIZE_DEFAULT
        for tab in self._tabs:
            tab.apply_font_size(self._font_size)
        self._update_status()

    # ── Status bar ───────────────────────────────────────────────────────────

    def _update_status(self, *_) -> None:
        tab = self._current_tab()
        if tab is None:
            self._status_var.set("")
            return
        try:
            ln, col = tab.tw.index("insert").split(".")
            path_label = tab.path or "Untitled"
            self._status_var.set(
                f"  {path_label}    "
                f"Ln {ln}, Col {int(col) + 1}    "
                f"Zoom {self._font_size}pt")
        except Exception:
            pass

    # ── Session ──────────────────────────────────────────────────────────────

    def _restore_session(self) -> list[str]:
        """Load the list of previously open files (and restore font size)."""
        try:
            data = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
            self._font_size = int(data.get("font_size", FONT_SIZE_DEFAULT))
            return [p for p in data.get("files", []) if os.path.isfile(p)]
        except Exception:
            return []

    def _save_session(self) -> None:
        """Persist open file paths and current font size."""
        paths = [t.path for t in self._tabs if t.path]
        try:
            active = self._current_index() or 0
        except Exception:
            active = 0
        try:
            SESSION_FILE.write_text(
                json.dumps({
                    "files":     paths,
                    "active":    active,
                    "font_size": self._font_size,
                }, indent=2),
                encoding="utf-8")
        except OSError:
            pass

    # ── Quit ─────────────────────────────────────────────────────────────────

    def _quit(self) -> None:
        self._save_session()
        self._root.destroy()

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _current_tab(self) -> Optional[EditorTab]:
        idx = self._current_index()
        return self._tabs[idx] if idx is not None else None

    def _current_index(self) -> Optional[int]:
        sel = self._nb.select()
        if not sel:
            return None
        try:
            return self._nb.index(sel)
        except tk.TclError:
            return None


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    root = tk.Tk()
    App(root, sys.argv[1:])
    root.mainloop()


if __name__ == "__main__":
    main()
