# utils/image_comparer — Side-by-side Image Viewer

A dark-themed, two-pane image comparison tool built on `tkinter` + `Pillow`.
Useful for visually diffing a raw screenshot against its annotated debug output.

## Requirements

- Python 3.10+
- [Pillow](https://pillow.readthedocs.io/) (`pip install pillow`)

## Launch

```bash
# Open blank (choose files from within the app)
python -m utils.image_comparer

# Pre-load the left pane; right pane auto-loads *_debug.png if it exists
python -m utils.image_comparer path/to/image.png
```

## Features

### Two-pane layout

The window is split into **LEFT** and **RIGHT** panes by a draggable divider.
Each pane is independent: its own file, its own zoom level.

### Auto-load of debug images

When a `*.png` is loaded in the **left** pane (either via Browse or command
line), the right pane automatically attempts to load a file named
`<stem>_debug.png` in the same directory.  If the file does not exist, the
right pane shows a "not found" message rather than an error.

This mirrors the GFL2 pipeline convention where `render_debug.py` produces
`<image>_debug.png` alongside the original.

### Zoom

Each pane zooms independently.

| Action | Effect |
|--------|--------|
| Scroll wheel | Zoom in / out (×1.25 per step) |
| **Ctrl + =** | Zoom in |
| **Ctrl + −** | Zoom out |
| **Ctrl + 0** or **Fit** button | Reset to fit-in-window |
| **+** / **−** buttons | Zoom in / out |

Zoom range: 5% – 1600%.  Current level shown in the zoom label above the canvas.

### Pan

Hold **middle mouse button** and drag to pan within a pane.  Horizontal and
vertical scrollbars are also available.

### File chooser

Each pane has a **Browse…** button.  The file path is shown in the toolbar;
clicking the file path label has no effect (use Browse to change).

## File layout

```
utils/image_comparer/
├── __init__.py   Package marker
├── __main__.py   `python -m utils.image_comparer` entry point
├── app.py        All application logic
└── README.md     This file
```
