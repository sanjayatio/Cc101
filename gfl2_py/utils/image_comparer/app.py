"""
utils/image_comparer/app.py
----------------------------
Side-by-side image comparison viewer.

Usage:
    python -m utils.image_comparer            # blank
    python -m utils.image_comparer left.png   # auto-loads left_debug.png on right

Controls:
    Scroll wheel   - zoom in/out (per pane)
    Ctrl +/-       - zoom in/out (per pane)
    Ctrl 0         - reset to fit-in-window
    Middle-drag    - pan

Auto-load: when a *.png is chosen on the left, the right pane attempts to
load a file named *_debug.png in the same directory.
"""
import sys
import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path

from PIL import Image, ImageTk

ZOOM_STEP   = 1.25
ZOOM_MIN    = 0.05
ZOOM_MAX    = 16.0
BG_COLOR    = "#2b2b2b"
PANEL_COLOR = "#1e1e1e"
TEXT_COLOR  = "#cccccc"
ACCENT      = "#5294e2"


# ── Image panel ───────────────────────────────────────────────────────────────

class ImagePanel(tk.Frame):
    """A scrollable, zoomable image pane with a file-chooser toolbar."""

    def __init__(self, master, label: str, on_file_chosen=None, **kw):
        super().__init__(master, bg=PANEL_COLOR, **kw)
        self._image_path: Path | None = None
        self._pil_image:  Image.Image | None = None
        self._tk_image:   ImageTk.PhotoImage | None = None
        self._zoom:       float = 1.0
        self._pan_start:  tuple[int, int] | None = None
        self._on_file_chosen = on_file_chosen

        self._build_toolbar(label)
        self._build_canvas()

    # ── build ──────────────────────────────────────────────────────────────

    def _build_toolbar(self, label: str) -> None:
        bar = tk.Frame(self, bg=PANEL_COLOR, pady=4)
        bar.pack(fill=tk.X, side=tk.TOP)

        tk.Label(bar, text=label, fg=ACCENT, bg=PANEL_COLOR,
                 font=("Helvetica", 9, "bold")).pack(side=tk.LEFT, padx=(8, 4))

        self._path_var = tk.StringVar(value="(no file)")
        tk.Label(bar, textvariable=self._path_var, fg=TEXT_COLOR, bg=PANEL_COLOR,
                 font=("Helvetica", 8), anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

        tk.Button(bar, text="Browse…", command=self._browse,
                  bg="#3c3c3c", fg=TEXT_COLOR, relief=tk.FLAT,
                  activebackground=ACCENT, cursor="hand2",
                  font=("Helvetica", 8)).pack(side=tk.RIGHT, padx=(0, 4))

        # zoom controls
        zbar = tk.Frame(self, bg=PANEL_COLOR)
        zbar.pack(fill=tk.X, side=tk.TOP)
        tk.Button(zbar, text="−", command=self._zoom_out, width=2,
                  bg="#3c3c3c", fg=TEXT_COLOR, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT, padx=(8, 0))
        self._zoom_label = tk.Label(zbar, text="100%", width=6,
                                    fg=TEXT_COLOR, bg=PANEL_COLOR, font=("Helvetica", 8))
        self._zoom_label.pack(side=tk.LEFT)
        tk.Button(zbar, text="+", command=self._zoom_in, width=2,
                  bg="#3c3c3c", fg=TEXT_COLOR, relief=tk.FLAT, cursor="hand2").pack(side=tk.LEFT)
        tk.Button(zbar, text="Fit", command=self._zoom_fit,
                  bg="#3c3c3c", fg=TEXT_COLOR, relief=tk.FLAT, cursor="hand2",
                  font=("Helvetica", 8)).pack(side=tk.LEFT, padx=4)

    def _build_canvas(self) -> None:
        frame = tk.Frame(self, bg=PANEL_COLOR)
        frame.pack(fill=tk.BOTH, expand=True)

        self._canvas = tk.Canvas(frame, bg=BG_COLOR, highlightthickness=0,
                                 cursor="crosshair")
        h_scroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL,
                                  command=self._canvas.xview)
        v_scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL,
                                  command=self._canvas.yview)

        self._canvas.configure(xscrollcommand=h_scroll.set,
                               yscrollcommand=v_scroll.set)

        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        v_scroll.pack(side=tk.RIGHT,  fill=tk.Y)
        self._canvas.pack(fill=tk.BOTH, expand=True)

        # bindings
        self._canvas.bind("<MouseWheel>",        self._on_mousewheel)       # Windows/macOS
        self._canvas.bind("<Button-4>",           self._on_scroll_up)        # Linux
        self._canvas.bind("<Button-5>",           self._on_scroll_down)      # Linux
        self._canvas.bind("<Control-equal>",      lambda e: self._zoom_in())
        self._canvas.bind("<Control-minus>",      lambda e: self._zoom_out())
        self._canvas.bind("<Control-0>",          lambda e: self._zoom_fit())
        self._canvas.bind("<ButtonPress-2>",      self._pan_start)
        self._canvas.bind("<B2-Motion>",          self._pan_move)
        self._canvas.bind("<Configure>",          lambda e: self._redraw())

    # ── file loading ───────────────────────────────────────────────────────

    def _browse(self) -> None:
        path = filedialog.askopenfilename(
            title="Open image",
            filetypes=[("PNG images", "*.png"), ("All files", "*.*")],
        )
        if path:
            self.load(Path(path))
            if self._on_file_chosen:
                self._on_file_chosen(Path(path))

    def load(self, path: Path) -> None:
        if not path.exists():
            self._path_var.set(f"(not found) {path.name}")
            self._pil_image = None
            self._canvas.delete("all")
            self._canvas.create_text(
                10, 10, anchor="nw", fill="#888",
                text=f"File not found:\n{path}",
                font=("Helvetica", 10),
            )
            return
        self._image_path = path
        self._pil_image  = Image.open(path)
        self._path_var.set(path.name)
        self._zoom_fit()

    # ── zoom / pan ─────────────────────────────────────────────────────────

    def _set_zoom(self, zoom: float) -> None:
        self._zoom = max(ZOOM_MIN, min(ZOOM_MAX, zoom))
        self._zoom_label.config(text=f"{self._zoom*100:.0f}%")
        self._redraw()

    def _zoom_in(self)  -> None: self._set_zoom(self._zoom * ZOOM_STEP)
    def _zoom_out(self) -> None: self._set_zoom(self._zoom / ZOOM_STEP)

    def _zoom_fit(self) -> None:
        if self._pil_image is None:
            return
        cw = self._canvas.winfo_width()
        ch = self._canvas.winfo_height()
        if cw < 2 or ch < 2:          # not yet laid out
            self.after(50, self._zoom_fit)
            return
        iw, ih = self._pil_image.size
        self._set_zoom(min(cw / iw, ch / ih))

    def _on_mousewheel(self, event) -> None:
        factor = ZOOM_STEP if event.delta > 0 else 1 / ZOOM_STEP
        self._set_zoom(self._zoom * factor)

    def _on_scroll_up(self, _event) -> None: self._set_zoom(self._zoom * ZOOM_STEP)
    def _on_scroll_down(self, _event) -> None: self._set_zoom(self._zoom / ZOOM_STEP)

    def _pan_start(self, event) -> None:
        self._canvas.scan_mark(event.x, event.y)

    def _pan_move(self, event) -> None:
        self._canvas.scan_dragto(event.x, event.y, gain=1)

    # ── render ─────────────────────────────────────────────────────────────

    def _redraw(self) -> None:
        if self._pil_image is None:
            return
        iw, ih = self._pil_image.size
        nw = max(1, int(iw * self._zoom))
        nh = max(1, int(ih * self._zoom))
        resized = self._pil_image.resize((nw, nh), Image.LANCZOS)
        self._tk_image = ImageTk.PhotoImage(resized)
        self._canvas.delete("all")
        self._canvas.create_image(0, 0, anchor="nw", image=self._tk_image)
        self._canvas.configure(scrollregion=(0, 0, nw, nh))


# ── Main window ───────────────────────────────────────────────────────────────

class ComparerApp(tk.Tk):
    def __init__(self, left_path: Path | None = None):
        super().__init__()
        self.title("Image Comparer")
        self.geometry("1400x800")
        self.configure(bg=BG_COLOR)
        self._build_ui()

        if left_path:
            self.after(100, lambda: self._load_left(left_path))

    def _build_ui(self) -> None:
        # Horizontal paned window — user can drag the divider
        pane = tk.PanedWindow(self, orient=tk.HORIZONTAL,
                              bg=BG_COLOR, sashwidth=6,
                              sashrelief=tk.FLAT)
        pane.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self._left  = ImagePanel(pane, "LEFT",  on_file_chosen=self._on_left_chosen)
        self._right = ImagePanel(pane, "RIGHT", on_file_chosen=None)

        pane.add(self._left,  stretch="always")
        pane.add(self._right, stretch="always")

    def _on_left_chosen(self, path: Path) -> None:
        """When left pane picks a file, auto-load *_debug.png on the right."""
        debug_path = path.with_name(path.stem + "_debug.png")
        self._right.load(debug_path)   # shows "not found" gracefully if absent

    def _load_left(self, path: Path) -> None:
        self._left.load(path)
        debug_path = path.with_name(path.stem + "_debug.png")
        self._right.load(debug_path)


# ── entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    left = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    app  = ComparerApp(left_path=left)
    app.mainloop()


if __name__ == "__main__":
    main()
